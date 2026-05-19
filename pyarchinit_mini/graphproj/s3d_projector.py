"""Project DB stratigraphy (us_table + period_table) into a ProjectedGraph.

The ProjectedGraph is the canonical intermediate representation consumed by:
  - s3d_to_cytoscape (web UI)
  - graphml_writer (yEd export)
  - s3d_integration.export_to_heriverse_json (ATON/Heriverse)

Rows = periods (always). When period_table is empty for the site OR a US has
no fase_iniziale matching any period row, the US is assigned to a synthetic
fallback row named "Periodo 1".
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from pyarchinit_mini.graphproj.rapporti_codec import parse_rapporti, SYMMETRIC


logger = logging.getLogger(__name__)


@dataclass
class Row:
    row_id: str
    label: str
    periodo: Optional[str] = None
    fase: Optional[str] = None
    datazione: Optional[str] = None
    is_fallback: bool = False


@dataclass
class Node:
    node_id: str
    us: str
    area: Optional[str]
    sito: str
    unit_type: str
    description: Optional[str]
    row_id: str
    sub_group: Optional[str] = None


@dataclass
class Edge:
    source_id: str
    target_id: str
    canonical: str


@dataclass
class ProjectedGraph:
    site: str
    group_by: str
    rows: List[Row] = field(default_factory=list)
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)


VALID_GROUP_BY = frozenset({"none", "area", "settore", "quadrato", "attivita", "strutture"})


class S3DProjector:
    _SUB_GROUP_COLUMN: Dict[str, str] = {
        "none": "",
        "area": "area",
        "settore": "settore",
        "quadrato": "quadrato",
        "attivita": "attivita",
        "strutture": "struttura",
    }

    @classmethod
    def from_site(cls, session: Session, site: str, group_by: str = "none") -> ProjectedGraph:
        if group_by not in VALID_GROUP_BY:
            raise ValueError(f"Invalid group_by={group_by!r}; valid: {sorted(VALID_GROUP_BY)}")
        graph = ProjectedGraph(site=site, group_by=group_by)
        cls._load_rows(session, site, graph)
        cls._load_us_nodes(session, site, graph)
        cls._load_edges(session, site, graph)
        return graph

    @classmethod
    def _load_rows(cls, session: Session, site: str, graph: ProjectedGraph) -> None:
        result = session.execute(
            text("SELECT periodo, fase, datazione FROM period_table "
                 "WHERE sito = :s OR sito IS NULL OR sito = ''"),
            {"s": site},
        ).fetchall()
        sorted_rows = sorted(
            [(r[0] or "", r[1] or "", r[2]) for r in result if r[0]],
            key=lambda t: (t[0], t[1]),
        )
        for i, (periodo, fase, dataz) in enumerate(sorted_rows):
            label = f"{periodo}/{fase}" if fase else periodo
            graph.rows.append(Row(
                row_id=f"row_{i}",
                label=label,
                periodo=periodo,
                fase=fase or None,
                datazione=dataz,
                is_fallback=False,
            ))

    @classmethod
    def _ensure_fallback_row(cls, graph: ProjectedGraph) -> Row:
        for r in graph.rows:
            if r.is_fallback:
                return r
        idx = len(graph.rows)
        fb = Row(row_id=f"row_{idx}", label="Periodo 1", is_fallback=True)
        graph.rows.append(fb)
        return fb

    @classmethod
    def _resolve_row_id(cls, fase: Optional[str], graph: ProjectedGraph) -> str:
        if fase:
            for r in graph.rows:
                if r.is_fallback:
                    continue
                if r.fase == fase or r.periodo == fase:
                    return r.row_id
        return cls._ensure_fallback_row(graph).row_id

    @classmethod
    def _load_us_nodes(cls, session: Session, site: str, graph: ProjectedGraph) -> None:
        col = cls._SUB_GROUP_COLUMN.get(graph.group_by, "")
        # "area" is already in the base SELECT at index 2; other columns need an extra select.
        extra_select = ""
        if col and col != "area":
            extra_select = f", {col}"
        sql = (f"SELECT id_us, sito, area, us, unita_tipo, descrizione, fase_iniziale"
               f"{extra_select} FROM us_table WHERE sito = :s")
        try:
            rows = session.execute(text(sql), {"s": site}).fetchall()
        except Exception as exc:
            # Column doesn't exist in this schema — retry without it
            logger.warning("us_table column %r missing; sub_group falls back to None: %s",
                           col, exc)
            session.rollback()
            sql_fb = ("SELECT id_us, sito, area, us, unita_tipo, descrizione, fase_iniziale "
                      "FROM us_table WHERE sito = :s")
            rows = session.execute(text(sql_fb), {"s": site}).fetchall()
            extra_select = ""
        for r in rows:
            unit_type = r[4] or "US"
            row_id = cls._resolve_row_id(r[6], graph)
            if graph.group_by == "none":
                sub = None
            elif graph.group_by == "area":
                sub = r[2]
            elif extra_select and len(r) > 7:
                sub = r[7]
            else:
                sub = None
            graph.nodes.append(Node(
                node_id=f"us_{r[0]}",
                us=str(r[3]),
                area=r[2],
                sito=r[1],
                unit_type=unit_type,
                description=r[5],
                row_id=row_id,
                sub_group=str(sub) if sub is not None else None,
            ))

    @classmethod
    def _load_edges(cls, session: Session, site: str, graph: ProjectedGraph) -> None:
        us_index: Dict[str, str] = {n.us: n.node_id for n in graph.nodes}
        rows = session.execute(
            text("SELECT us, rapporti FROM us_table "
                 "WHERE sito = :s AND rapporti IS NOT NULL AND rapporti != ''"),
            {"s": site},
        ).fetchall()
        seen = set()
        for us_num, rapp_raw in rows:
            src_id = us_index.get(str(us_num))
            if src_id is None:
                continue
            for rap in parse_rapporti(rapp_raw, current_site=site):
                tgt_id = us_index.get(rap.target_us)
                if tgt_id is None:
                    continue
                if rap.canonical in SYMMETRIC:
                    key = (rap.canonical, tuple(sorted((src_id, tgt_id))))
                else:
                    key = (rap.canonical, src_id, tgt_id)
                if key in seen:
                    continue
                seen.add(key)
                graph.edges.append(Edge(source_id=src_id, target_id=tgt_id, canonical=rap.canonical))
