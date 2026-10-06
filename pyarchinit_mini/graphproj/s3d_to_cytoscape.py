"""Translate the projected s3dgraphy.Graph into cytoscape.js JSON with
palette-derived styles. Output shape unchanged (flat palette keys, period rows
always emitted as compound parents, sub-clusters nested inside rows)."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from pyarchinit_mini.em_palette import get_palette
from .rapporti_codec import SYMMETRIC, display_label
from .strat_graph import get_swimlane, pyarchinit_attrs, stratigraphic_edges, stratigraphic_nodes


def _node_view(node, default_row_id: str) -> Dict[str, Any]:
    a = pyarchinit_attrs(node)
    if a:
        return {"id": node.node_id, "us": a["us"], "area": a.get("area"), "unit_type": a.get("unit_type") or "US",
                "description": a.get("description"), "row_id": a.get("row_id") or default_row_id,
                "sub_group": a.get("sub_group")}
    return {"id": node.node_id, "us": node.name, "area": None, "unit_type": "US",
            "description": node.description or None, "row_id": default_row_id, "sub_group": None}


def to_cytoscape(graph) -> Dict[str, Any]:
    palette = get_palette()
    sw = get_swimlane(graph)
    rows: List[Dict[str, Any]] = list(sw["rows"]) or [{"row_id": "row_0", "label": "Periodo 1", "periodo": None,
                                                        "fase": None, "datazione": None, "is_fallback": True}]
    group_by = sw["group_by"]
    out_nodes: List[Dict[str, Any]] = []
    out_edges: List[Dict[str, Any]] = []

    for r in rows:
        label = f"{r['label']} — {r['datazione']}" if r.get("datazione") else r["label"]
        out_nodes.append({"data": {"id": r["row_id"], "label": label, "compound": True,
                                   "is_period_row": True, "is_fallback": r["is_fallback"]}})

    views = [_node_view(n, rows[0]["row_id"]) for n in stratigraphic_nodes(graph)]
    parent_ids: Dict[Tuple[str, str], str] = {}
    if group_by != "none":
        for v in views:
            if v["sub_group"] is None:
                continue
            key = (v["row_id"], v["sub_group"])
            if key not in parent_ids:
                cluster_id = f"cluster_{v['row_id']}_{v['sub_group']}"
                parent_ids[key] = cluster_id
                out_nodes.append({"data": {"id": cluster_id, "label": v["sub_group"], "row": v["row_id"],
                                           "compound": True, "is_period_row": False, "parent": v["row_id"]}})

    for v in views:
        ns = palette.get_node_style(v["unit_type"])
        parent = parent_ids.get((v["row_id"], v["sub_group"]), v["row_id"]) if (group_by != "none" and v["sub_group"] is not None) else v["row_id"]
        out_nodes.append({"data": {
            "id": v["id"], "label": v["us"], "us": v["us"], "area": v["area"], "unit_type": v["unit_type"],
            "description": v["description"], "row": v["row_id"], "parent": parent,
            "shape": ns.shape, "bgcolor": ns.fill_color, "bordercolor": ns.border_color,
            "borderwidth": ns.border_width, "borderstyle": ns.border_style,
            "fontcolor": ns.font_color, "fontsize": ns.font_size,
        }})

    for e in stratigraphic_edges(graph):
        canonical = e.edge_type
        es = palette.get_edge_style(canonical)
        out_edges.append({"data": {
            "id": f"{e.edge_source}__{canonical}__{e.edge_target}", "source": e.edge_source, "target": e.edge_target,
            "label": display_label(canonical, locale="it"), "canonical": canonical,
            "linecolor": es.line_color, "linewidth": es.line_width, "linestyle": es.line_style,
            "arrowtarget": "none" if canonical in SYMMETRIC else es.arrow_target, "arrowsource": es.arrow_source,
            "is_dashed": "true" if canonical == "cuts" else "false",
        }})

    return {"site": sw["site"], "group_by": group_by,
            "rows": [{"row_id": r["row_id"], "label": r["label"], "periodo": r.get("periodo"), "fase": r.get("fase"),
                      "datazione": r.get("datazione"), "is_fallback": r["is_fallback"]} for r in rows],
            "nodes": out_nodes, "edges": out_edges}
