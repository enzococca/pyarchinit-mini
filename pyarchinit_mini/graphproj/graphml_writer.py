"""yEd-flavoured GraphML writer (EM Harris Matrix Creator format) from the
projected s3dgraphy.Graph: ONE <y:TableNode> group with one <y:Row> per
swimlane row, US nodes positioned inside their row, Italian edge labels.
Thin bridge to graphml_io.yed_writer.write_extended_matrix_graphml."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

from .rapporti_codec import CANONICAL_TO_ITALIAN, display_label
from .strat_graph import get_swimlane, pyarchinit_attrs, stratigraphic_edges, stratigraphic_nodes


def write_graphml(graph, *, palette_path: Optional[Path] = None) -> bytes:
    """Render the graph as yEd-compatible GraphML bytes (palette_path is ignored)."""
    from pyarchinit_mini.harris_swimlane.swimlane_state import CytoscapeElement
    from pyarchinit_mini.harris_swimlane.row_provider import Row as LegacyRow, PERIOD_COLORS
    from pyarchinit_mini.graphml_io.yed_writer import write_extended_matrix_graphml

    sw = get_swimlane(graph)
    swim_rows = list(sw["rows"]) or [{"row_id": "row_0", "label": "Periodo 1", "periodo": None,
                                      "fase": None, "datazione": None, "is_fallback": True}]
    rows = [
        LegacyRow(row_id=r["row_id"], period_name=r.get("periodo") or r["label"], phase_name=r.get("fase"),
                  start_date=None, end_date=None, color=PERIOD_COLORS[i % len(PERIOD_COLORS)],
                  source="fallback" if r["is_fallback"] else "period_table")
        for i, r in enumerate(swim_rows)
    ]
    row_index = {r["row_id"]: i for i, r in enumerate(swim_rows)}
    row_height, node_h, node_w = 200, 30.0, 80.0
    col_counter: dict = {}

    nodes = []
    for node in stratigraphic_nodes(graph):
        a = pyarchinit_attrs(node)
        us = str(a.get("us") or node.name)
        row_id = a.get("row_id") or swim_rows[0]["row_id"]
        ri = row_index.get(row_id, 0)
        col = col_counter.get(row_id, 0)
        col_counter[row_id] = col + 1
        nodes.append(CytoscapeElement(
            data={
                "id": node.node_id, "us": us, "us_number": us, "label": us,
                "area": a.get("area") or "", "unit_type": a.get("unit_type") or "US",
                "description": a.get("description") or (node.description or ""),
                "row": row_id, "node_uuid": a.get("node_uuid") or node.node_id,
                "period": a.get("periodo") or "", "phase": a.get("fase") or "",
            },
            position={"x": col * (node_w + 20) + 30, "y": ri * row_height + (row_height / 2 - node_h / 2)},
        ))

    edges = []
    for e in stratigraphic_edges(graph):
        canonical = e.edge_type
        edges.append(CytoscapeElement(data={
            "id": f"{e.edge_source}__{canonical}__{e.edge_target}",
            "source": e.edge_source, "target": e.edge_target,
            "label": display_label(canonical, locale="it"), "canonical": canonical,
            "relationship": CANONICAL_TO_ITALIAN.get(canonical, canonical),
        }))

    class _State:
        site = sw["site"]
        group_by = sw["group_by"]
        pending_changes: dict = {}

    state = _State()
    state.rows, state.nodes, state.edges = rows, nodes, edges
    epochs = [{"row_id": r["row_id"], "periodo": r.get("periodo"), "fase": r.get("fase"),
               "datazione": r["datazione"]} for r in swim_rows if r.get("datazione")]

    with tempfile.NamedTemporaryFile(suffix=".graphml", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        write_extended_matrix_graphml(state, site_meta={"sito": sw["site"]}, epochs=epochs, out=Path(tmp_path))
        with open(tmp_path, "rb") as fh:
            return fh.read()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
