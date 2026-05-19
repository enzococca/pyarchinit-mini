"""Translate a ProjectedGraph into cytoscape.js JSON with palette-derived styles.

Changes from 2.9.0:
- Palette fields are FLAT top-level data keys (shape, bgcolor, bordercolor …)
  instead of a nested ``style`` object.  Cytoscape's ``data()`` accessor does
  not reliably traverse nested objects, so ``data(style.shape)`` silently
  returns nothing.
- Period rows are ALWAYS emitted as compound parents (regardless of group_by)
  so the UI always shows horizontal swimlanes.
- When group_by != "none", sub-cluster compounds are nested INSIDE their period
  row compound (cytoscape supports nested compounds).
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from pyarchinit_mini.em_palette import get_palette
from pyarchinit_mini.graphproj.rapporti_codec import display_label, SYMMETRIC
from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph


def to_cytoscape(graph: ProjectedGraph) -> Dict[str, Any]:
    palette = get_palette()
    out_nodes: List[Dict[str, Any]] = []
    out_edges: List[Dict[str, Any]] = []

    # ── Fix C: ALWAYS emit period row compound parents first ─────────────────
    for r in graph.rows:
        label = r.label
        if r.datazione:
            label = f"{r.label} — {r.datazione}"
        out_nodes.append({
            "data": {
                "id": r.row_id,
                "label": label,
                "compound": True,
                "is_period_row": True,
                "is_fallback": r.is_fallback,
            },
        })

    # ── Fix D: sub-cluster compounds nested inside period rows ───────────────
    # Indexed by (row_id, sub_group) → cluster node id
    parent_ids: Dict[Tuple[str, str], str] = {}
    if graph.group_by != "none":
        for n in graph.nodes:
            if n.sub_group is None:
                continue
            key = (n.row_id, n.sub_group)
            if key not in parent_ids:
                cluster_id = f"cluster_{n.row_id}_{n.sub_group}"
                parent_ids[key] = cluster_id
                out_nodes.append({
                    "data": {
                        "id": cluster_id,
                        "label": n.sub_group,
                        "row": n.row_id,
                        "compound": True,
                        "is_period_row": False,
                        # Nested inside the period row
                        "parent": n.row_id,
                    },
                })

    # ── Fix B: flat palette fields on US nodes ────────────────────────────────
    for n in graph.nodes:
        ns = palette.get_node_style(n.unit_type)

        # Determine the immediate parent for this node
        if graph.group_by != "none" and n.sub_group is not None:
            immediate_parent = parent_ids.get((n.row_id, n.sub_group), n.row_id)
        else:
            immediate_parent = n.row_id

        node_obj: Dict[str, Any] = {
            "data": {
                "id": n.node_id,
                "label": n.us,
                "us": n.us,
                "area": n.area,
                "unit_type": n.unit_type,
                "description": n.description,
                "row": n.row_id,
                "parent": immediate_parent,
                # ── Flat palette fields (Fix B) ──
                "shape": ns.shape,
                "bgcolor": ns.fill_color,
                "bordercolor": ns.border_color,
                "borderwidth": ns.border_width,
                "borderstyle": ns.border_style,
                "fontcolor": ns.font_color,
                "fontsize": ns.font_size,
            },
        }
        out_nodes.append(node_obj)

    # ── Fix B: flat palette fields on edges ──────────────────────────────────
    for e in graph.edges:
        es = palette.get_edge_style(e.canonical)
        is_symmetric = e.canonical in SYMMETRIC
        out_edges.append({
            "data": {
                "id": f"{e.source_id}__{e.canonical}__{e.target_id}",
                "source": e.source_id,
                "target": e.target_id,
                "label": display_label(e.canonical, locale="it"),
                "canonical": e.canonical,
                # ── Flat palette fields (Fix B) ──
                "linecolor": es.line_color,
                "linewidth": es.line_width,
                "linestyle": es.line_style,
                "arrowtarget": "none" if is_symmetric else es.arrow_target,
                "arrowsource": es.arrow_source,
                "is_dashed": "true" if e.canonical == "cuts" else "false",
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
