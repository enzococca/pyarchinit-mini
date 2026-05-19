"""Translate a ProjectedGraph into cytoscape.js JSON with palette-derived styles.

Compound parents (one per (row_id, sub_group) pair) are emitted when
graph.group_by != "none", giving cytoscape a way to visually cluster nodes
within each period row.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from pyarchinit_mini.em_palette import get_palette
from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph


def to_cytoscape(graph: ProjectedGraph) -> Dict[str, Any]:
    palette = get_palette()
    out_nodes: List[Dict[str, Any]] = []
    out_edges: List[Dict[str, Any]] = []

    # Compound parents indexed by (row_id, sub_group_value)
    parent_ids: Dict[Tuple[str, str], str] = {}
    if graph.group_by != "none":
        for n in graph.nodes:
            if n.sub_group is None:
                continue
            key = (n.row_id, n.sub_group)
            if key not in parent_ids:
                parent_id = f"cluster_{n.row_id}_{n.sub_group}"
                parent_ids[key] = parent_id
                out_nodes.append({
                    "data": {
                        "id": parent_id,
                        "label": n.sub_group,
                        "row": n.row_id,
                        "compound": True,
                    },
                    "style": {
                        "backgroundColor": "#F5F5F5",
                        "borderColor": "#9E9E9E",
                    },
                })

    for n in graph.nodes:
        ns = palette.get_node_style(n.unit_type)
        node_obj: Dict[str, Any] = {
            "data": {
                "id": n.node_id,
                "label": n.us,
                "us": n.us,
                "area": n.area,
                "unit_type": n.unit_type,
                "description": n.description,
                "row": n.row_id,
            },
            "style": {
                "shape": ns.shape,
                "backgroundColor": ns.fill_color,
                "borderColor": ns.border_color,
                "borderWidth": ns.border_width,
                "lineStyle": ns.border_style,
                "fontColor": ns.font_color,
                "fontSize": ns.font_size,
            },
        }
        if graph.group_by != "none" and n.sub_group is not None:
            node_obj["data"]["parent"] = f"cluster_{n.row_id}_{n.sub_group}"
        out_nodes.append(node_obj)

    for e in graph.edges:
        es = palette.get_edge_style(e.canonical)
        out_edges.append({
            "data": {
                "id": f"{e.source_id}__{e.canonical}__{e.target_id}",
                "source": e.source_id,
                "target": e.target_id,
                "label": e.canonical,
            },
            "style": {
                "lineColor": es.line_color,
                "lineWidth": es.line_width,
                "lineStyle": es.line_style,
                "targetArrowShape": es.arrow_target,
                "sourceArrowShape": es.arrow_source,
            },
        })

    return {
        "site": graph.site,
        "group_by": graph.group_by,
        "rows": [
            {
                "row_id": r.row_id,
                "label": r.label,
                "periodo": r.periodo,
                "fase": r.fase,
                "datazione": r.datazione,
                "is_fallback": r.is_fallback,
            }
            for r in graph.rows
        ],
        "nodes": out_nodes,
        "edges": out_edges,
    }
