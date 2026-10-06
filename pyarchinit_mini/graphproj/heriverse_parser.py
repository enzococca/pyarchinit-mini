"""Heriverse/ATON JSON → contract s3dgraphy.Graph reverse parser.

Mirror of pyarchinit_mini/s3d_integration/s3d_converter.py::export_to_heriverse_json.
Heriverse stores nodes grouped by unit type and edges grouped by edge type within
a multigraph[graphs[0]] structure. The first graph in the multigraph is the
canonical site graph.
"""
from __future__ import annotations

import json
from typing import Dict

from s3dgraphy import Graph

from pyarchinit_mini.graphproj.strat_graph import (
    FALLBACK_ROW, new_graph, new_strat_node, set_pyarchinit_attrs, set_swimlane,
    stratigraphic_nodes,
)


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


def parse_heriverse(raw_json: str) -> Graph:
    data = json.loads(raw_json)
    multi = data.get("multigraph", {})
    graphs = multi.get("graphs", [])
    if not graphs:
        graph = new_graph("UnknownSite")
        set_swimlane(graph, site="UnknownSite", group_by="none", rows=[dict(FALLBACK_ROW)])
        return graph

    g0 = graphs[0]
    site = g0.get("name") or "UnknownSite"
    graph = new_graph(site)
    set_swimlane(graph, site=site, group_by="none", rows=[dict(FALLBACK_ROW)])

    counter = 0
    for unit_type, items in (g0.get("nodes") or {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            counter += 1
            node_id = item.get("id") or f"us_{counter}"
            us = str(item.get("name") or item.get("id") or "?")
            area = (item.get("data") or {}).get("area") if isinstance(item.get("data"), dict) else None
            node = new_strat_node(node_id=node_id, name=f"{unit_type}{us}", unit_type=unit_type,
                                  description=item.get("description") or "")
            set_pyarchinit_attrs(node, us=us, unit_type=unit_type, sito=site, area=area,
                                 description=item.get("description"), row_id="row_0",
                                 node_uuid=node_id)
            graph.add_node(node)

    known = {n.node_id for n in stratigraphic_nodes(graph)}
    for edge_type, items in (g0.get("edges") or {}).items():
        if not isinstance(items, list):
            continue
        canonical = EDGE_TYPE_MAP.get(edge_type, edge_type)
        for item in items:
            if not isinstance(item, dict):
                continue
            src, tgt = item.get("from"), item.get("to")
            if src in known and tgt in known:
                edge_id = f"{src}__{canonical}__{tgt}"
                if graph.find_edge_by_id(edge_id) is not None:
                    continue
                graph.add_edge(edge_id, src, tgt, canonical)

    return graph
