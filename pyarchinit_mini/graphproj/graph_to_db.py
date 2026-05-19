"""Write a ProjectedGraph back to us_table (4-tuple rapporti, inverses on both sides)."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from pyarchinit_mini.graphproj.rapporti_codec import (
    parse_rapporti,
    serialize_rapporti,
    INVERSE_PAIRS,
    SYMMETRIC,
    Rapporto,
)
from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph, Node


logger = logging.getLogger(__name__)


# Canonical → italian display label (used when serializing).
CANONICAL_TO_ITALIAN: Dict[str, str] = {
    "overlies": "Copre",
    "is_after": "Coperto da",
    "cuts": "Taglia",
    "is_cut_by": "Tagliato da",
    "fills": "Riempie",
    "is_filled_by": "Riempito da",
    "abuts": "Si appoggia a",
    "is_abutted_by": "Gli si appoggia",
    "has_same_time": "Uguale a",
    "is_bonded_to": "Si lega a",
    "is_before": "Anteriore a",
}


@dataclass
class WriteResult:
    imported_us: int = 0
    imported_edges: int = 0
    inverses_written: int = 0
    stubs_created: int = 0
    inverses_skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def write_graph(
    graph: ProjectedGraph,
    *,
    target_site: str,
    session: Session,
    source_label: str = "import",
) -> WriteResult:
    result = WriteResult()
    now = datetime.now(timezone.utc).isoformat()
    origin_tag = f"{source_label}_{now}"

    # Ensure site row exists (sqlite-compatible: SELECT then INSERT)
    existing_site = session.execute(
        text("SELECT id_sito FROM site_table WHERE sito = :s"),
        {"s": target_site},
    ).scalar()
    if existing_site is None:
        session.execute(
            text("INSERT INTO site_table (sito) VALUES (:s)"),
            {"s": target_site},
        )

    # Upsert US rows
    for n in graph.nodes:
        is_new = _upsert_us_row(n, target_site, origin_tag, session)
        result.imported_us += 1
        if is_new and n.description == "Imported placeholder":
            result.stubs_created += 1

    # Index us_table by node_id for rapporti generation
    by_node_id: Dict[str, Node] = {n.node_id: n for n in graph.nodes}

    # Accumulate rapporti per US (forward + inverse)
    per_us_items: Dict[str, List[Rapporto]] = {}
    for e in graph.edges:
        src = by_node_id.get(e.source_id)
        tgt = by_node_id.get(e.target_id)
        if src is None or tgt is None:
            continue
        # Forward
        fwd = Rapporto(
            canonical=e.canonical,
            target_us=tgt.us,
            target_area=tgt.area,
            target_sito=target_site,
        )
        per_us_items.setdefault(src.us, []).append(fwd)
        result.imported_edges += 1
        # Inverse (skip if symmetric)
        if e.canonical in SYMMETRIC:
            continue
        inv = INVERSE_PAIRS.get(e.canonical)
        if inv is None:
            result.inverses_skipped.append(e.canonical)
            continue
        rev = Rapporto(
            canonical=inv,
            target_us=src.us,
            target_area=src.area,
            target_sito=target_site,
        )
        per_us_items.setdefault(tgt.us, []).append(rev)
        result.inverses_written += 1

    # Write merged rapporti (append + dedup)
    for us_num, items in per_us_items.items():
        existing_raw = session.execute(
            text("SELECT rapporti FROM us_table WHERE sito = :s AND us = :u"),
            {"s": target_site, "u": us_num},
        ).scalar() or ""
        existing = parse_rapporti(existing_raw, current_site=target_site)
        merged = existing + items
        serialized = serialize_rapporti(merged, italian_labels=CANONICAL_TO_ITALIAN)
        session.execute(
            text("UPDATE us_table SET rapporti = :r WHERE sito = :s AND us = :u"),
            {"r": serialized, "s": target_site, "u": us_num},
        )

    session.commit()
    return result


def _upsert_us_row(n: Node, target_site: str, origin_tag: str, session: Session) -> bool:
    """INSERT OR UPDATE us_table for this node. Returns True if newly inserted."""
    existing = session.execute(
        text("SELECT id_us FROM us_table WHERE sito = :s AND area = :a AND us = :u"),
        {"s": target_site, "a": n.area or "", "u": n.us},
    ).scalar()
    if existing is None:
        session.execute(
            text("INSERT INTO us_table (sito, area, us, unita_tipo, descrizione, data_origine) "
                 "VALUES (:s, :a, :u, :t, :d, :o)"),
            {"s": target_site, "a": n.area or "", "u": n.us, "t": n.unit_type,
             "d": n.description, "o": origin_tag},
        )
        return True
    session.execute(
        text("UPDATE us_table SET unita_tipo = :t, descrizione = COALESCE(:d, descrizione) "
             "WHERE sito = :s AND area = :a AND us = :u"),
        {"t": n.unit_type, "d": n.description, "s": target_site, "a": n.area or "", "u": n.us},
    )
    return False
