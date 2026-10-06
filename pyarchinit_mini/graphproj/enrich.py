"""Read the us_table columns the importer does not keep and attach them to the
importer's nodes (spec §4/§5)."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy import text

from .periods import PeriodRow, resolve_row_id
from .strat_graph import is_stratigraphic, set_pyarchinit_attrs, stratigraphic_nodes

logger = logging.getLogger(__name__)

VALID_GROUP_BY = frozenset({"none", "area", "settore", "quadrato", "attivita", "strutture"})
_SUB_GROUP_COLUMN = {"area": "area", "settore": "settore", "quadrato": "quadrato",
                     "attivita": "attivita", "strutture": "struttura"}


@dataclass
class UsRow:
    id_us: int
    sito: str
    area: Optional[str]
    us: str
    unita_tipo_raw: Optional[str]
    unit_type: str
    description: Optional[str]
    periodo: Optional[str]
    phase: Optional[str]
    sub_group: Optional[str]
    node_uuid: Optional[str]
    rapporti: Optional[str]
    settore: Optional[str]


def _available_columns(session) -> set:
    """Column names of us_table on this connection (SQLite and PostgreSQL)."""
    try:
        return set(session.execute(text("SELECT * FROM us_table LIMIT 0")).keys())
    except Exception as exc:
        logger.error("Cannot inspect us_table: %s", exc)
        try:
            session.rollback()
        except Exception:
            pass
        return set()


def load_us_rows(session, site: str, *, group_by: str = "none", area: Optional[str] = None) -> List[UsRow]:
    if group_by not in VALID_GROUP_BY:
        raise ValueError(f"group_by must be one of {sorted(VALID_GROUP_BY)}, got {group_by!r}")
    cols = _available_columns(session)
    if not cols:
        return []

    def pick(*candidates: str) -> str:
        for c in candidates:
            if c in cols:
                return c
        return "NULL"  # selected as a literal NULL column

    group_col = _SUB_GROUP_COLUMN.get(group_by, "")
    sql = (
        f"SELECT id_us, sito, area, us, unita_tipo, "
        f"{pick('descrizione', 'd_stratigrafica')}, {pick('fase_iniziale', 'periodo_iniziale')}, "
        f"{pick('periodo_iniziale')}, {pick('node_uuid')}, {pick('rapporti')}, {pick('settore')}, "
        f"{pick(group_col) if group_col else 'NULL'} "
        f"FROM us_table WHERE sito = :s" + (" AND area = :a" if area else "") + " ORDER BY id_us"
    )
    params = {"s": site, **({"a": area} if area else {})}
    rows = session.execute(text(sql), params).fetchall()
    out: List[UsRow] = []
    for r in rows:
        if group_by == "none":
            sub = None
        elif group_by == "area":
            sub = r[2]
        else:
            sub = r[11]
        out.append(UsRow(
            id_us=r[0], sito=r[1], area=r[2], us=str(r[3]), unita_tipo_raw=r[4],
            unit_type=r[4] or "US", description=r[5], phase=r[6], periodo=r[7],
            sub_group=(str(sub) if sub is not None else None), node_uuid=r[8],
            rapporti=r[9], settore=r[10],
        ))
    return out


def attach_pyarchinit_attributes(graph, importer, rows: List[UsRow], *, period_rows: List[PeriodRow]) -> Dict[int, str]:
    from pyarchinit_mini.vocab.provider import VocabProvider
    provider = VocabProvider.instance()
    by_id = {n.node_id: n for n in stratigraphic_nodes(graph)}
    mapping: Dict[int, str] = {}
    for r in rows:
        node = by_id.get(r.node_uuid) if r.node_uuid else None
        if node is None:
            name = importer._resolve_node_name(
                {"area": r.area, "settore": r.settore, "unita_tipo": r.unita_tipo_raw, "us": r.us}, "us")
            node = graph.find_node_by_name(name)
            if node is None or not is_stratigraphic(node):
                logger.warning("us_table row id_us=%s (%s) has no node in the projected graph; skipped", r.id_us, name)
                continue
        ut = provider.get_unit_type(r.unit_type)
        family = ut.family if (ut and getattr(ut, "family", None)) else "unknown"
        set_pyarchinit_attrs(
            node, us=r.us, unit_type=r.unit_type, sito=r.sito, area=r.area,
            description=r.description, periodo=r.periodo, fase=r.phase,
            row_id=resolve_row_id(period_rows, r.phase), sub_group=r.sub_group,
            node_uuid=r.node_uuid or node.node_id, id_us=r.id_us, family=family,
        )
        mapping[r.id_us] = node.node_id
    return mapping
