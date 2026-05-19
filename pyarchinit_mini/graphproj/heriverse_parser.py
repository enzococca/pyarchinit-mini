"""Heriverse/ATON JSON → ProjectedGraph reverse parser.

Mirror of pyarchinit_mini/s3d_integration/s3d_converter.py::export_to_heriverse_json.
Heriverse stores nodes grouped by unit type and edges grouped by edge type within
a multigraph[graphs[0]] structure. The first graph in the multigraph is the
canonical site graph.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph, Row, Node, Edge


# Heriverse edge type → canonical stratigraphic relation.
EDGE_TYPE_MAP: Dict[str, str] = {
    "line": "overlies",
    "contrasts_with": "is_after",
    "changed_from": "is_after",
    "is_before": "is_before",
    "covers": "overlies",
    "cuts": "cuts",
    "fills": "fills",
    "abuts": "abuts",
    "has_same_time": "has_same_time",
    "is_bonded_to": "is_bonded_to",
    "is_after": "is_after",
    "is_cut_by": "is_cut_by",
    "is_filled_by": "is_filled_by",
    "is_abutted_by": "is_abutted_by",
}


def parse_heriverse(raw_json: str) -> ProjectedGraph:
    data = json.loads(raw_json)
    multi = data.get("multigraph", {})
    graphs = multi.get("graphs", [])
    if not graphs:
        out = ProjectedGraph(site="UnknownSite", group_by="none")
        out.rows.append(Row(row_id="row_0", label="Periodo 1", is_fallback=True))
        return out

    g0 = graphs[0]
    site = g0.get("name") or "UnknownSite"
    out = ProjectedGraph(site=site, group_by="none")
    out.rows.append(Row(row_id="row_0", label="Periodo 1", is_fallback=True))

    nodes_by_id: Dict[str, Node] = {}
    for unit_type, items in (g0.get("nodes") or {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            node_id = item.get("id") or f"us_{len(nodes_by_id)}"
            us_num = str(item.get("name") or item.get("id") or "?")
            area = (item.get("data") or {}).get("area") if isinstance(item.get("data"), dict) else None
            description = item.get("description")
            n = Node(
                node_id=node_id,
                us=us_num,
                area=area,
                sito=site,
                unit_type=unit_type,
                description=description,
                row_id="row_0",
            )
            nodes_by_id[node_id] = n
            out.nodes.append(n)

    for edge_type, items in (g0.get("edges") or {}).items():
        if not isinstance(items, list):
            continue
        canonical = EDGE_TYPE_MAP.get(edge_type, edge_type)
        for item in items:
            if not isinstance(item, dict):
                continue
            src = item.get("from")
            tgt = item.get("to")
            if not src or not tgt:
                continue
            if src not in nodes_by_id or tgt not in nodes_by_id:
                continue
            out.edges.append(Edge(source_id=src, target_id=tgt, canonical=canonical))

    return out
