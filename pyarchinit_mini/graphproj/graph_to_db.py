"""Write a contract s3dgraphy graph back to us_table (4-tuple rapporti, inverses on both sides)."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, NamedTuple, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from pyarchinit_mini.graphproj.rapporti_codec import (
    parse_rapporti,
    serialize_rapporti,
    INVERSE_PAIRS,
    SYMMETRIC,
    Rapporto,
    CANONICAL_TO_ITALIAN,
)
from pyarchinit_mini.graphproj.strat_graph import (
    pyarchinit_attrs, stratigraphic_edges, stratigraphic_nodes,
)


logger = logging.getLogger(__name__)


@dataclass
class WriteResult:
    imported_us: int = 0
    imported_edges: int = 0
    inverses_written: int = 0
    stubs_created: int = 0
    inverses_skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class _NodeView(NamedTuple):
    node_id: str
    us: str
    area: Optional[str]
    unit_type: str
    description: Optional[str]


def _us_from_name(name: str) -> str:
    m = re.search(r"(\d+)\s*$", name or "")
    return m.group(1) if m else (name or "")


def _views(graph) -> List[_NodeView]:
    out = []
    for n in stratigraphic_nodes(graph):
        a = pyarchinit_attrs(n)
        out.append(_NodeView(n.node_id, str(a.get("us") or _us_from_name(n.name)), a.get("area"),
                             a.get("unit_type") or "US", a.get("description") if a else (n.description or None)))
    return out


def _canonical(e) -> str:
    """Canonical relation of an edge.

    s3dgraphy coerces edge types it does not know (e.g. ``partially_covers``) to
    ``generic_connection``; the contract edge id ``<src>__<canonical>__<tgt>`` keeps
    the original label, so recover it from there.
    """
    if e.edge_type == "generic_connection":
        prefix, suffix = f"{e.edge_source}__", f"__{e.edge_target}"
        eid = str(e.edge_id or "")
        if eid.startswith(prefix) and eid.endswith(suffix) and len(eid) > len(prefix) + len(suffix):
            return eid[len(prefix):-len(suffix)]
    return e.edge_type


def write_graph(
    graph,
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
    for n in _views(graph):
        is_new = _upsert_us_row(n, target_site, origin_tag, session)
        result.imported_us += 1
        if is_new and n.description == "Imported placeholder":
            result.stubs_created += 1

    # Index us_table by node_id for rapporti generation
    by_node_id: Dict[str, _NodeView] = {v.node_id: v for v in _views(graph)}

    # Accumulate rapporti per US (forward + inverse)
    per_us_items: Dict[str, List[Rapporto]] = {}
    for e in stratigraphic_edges(graph):
        src = by_node_id.get(e.edge_source)
        tgt = by_node_id.get(e.edge_target)
        canonical = _canonical(e)
        if src is None or tgt is None:
            continue
        # Forward
        fwd = Rapporto(
            canonical=canonical,
            target_us=tgt.us,
            target_area=tgt.area,
            target_sito=target_site,
        )
        per_us_items.setdefault(src.us, []).append(fwd)
        result.imported_edges += 1
        # Inverse (skip if symmetric)
        if canonical in SYMMETRIC:
            continue
        inv = INVERSE_PAIRS.get(canonical)
        if inv is None:
            result.inverses_skipped.append(canonical)
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


def _upsert_us_row(n: _NodeView, target_site: str, origin_tag: str, session: Session) -> bool:
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
