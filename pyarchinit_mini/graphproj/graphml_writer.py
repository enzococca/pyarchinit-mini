"""yEd-flavoured GraphML writer producing the EM Harris Matrix Creator format.

Strategy (Approach A): thin bridge from ProjectedGraph to the canonical
graphml_io.yed_writer.write_extended_matrix_graphml which already produces the
proper TableNode / swimlane format consumed by yEd Desktop.

Output:
  - Standalone GraphML (no palette template merging)
  - ONE group node with <y:TableNode YED_TABLE_NODE> containing one <y:Row>
    per period row from the ProjectedGraph
  - US nodes positioned inside their row's y-range
  - Edges with italianized labels (Copre, Taglia, …) via rapporti_codec
"""
from __future__ import annotations

import tempfile
import os
from pathlib import Path
from typing import Optional

from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph
from pyarchinit_mini.graphproj.rapporti_codec import display_label, CANONICAL_TO_ITALIAN


def write_graphml(graph: ProjectedGraph, *, palette_path: Optional[Path] = None) -> bytes:
    """Render the projected graph as yEd-compatible GraphML bytes.

    palette_path is accepted for backward-compatible call-sites but is ignored —
    the new output is a standalone TableNode document, not a palette extension.
    """
    from pyarchinit_mini.harris_swimlane.swimlane_state import CytoscapeElement
    from pyarchinit_mini.harris_swimlane.row_provider import Row as LegacyRow, PERIOD_COLORS

    # ------------------------------------------------------------------
    # 1. Convert ProjectedGraph.rows → legacy Row objects
    # ------------------------------------------------------------------
    rows: list[LegacyRow] = []
    for i, r in enumerate(graph.rows):
        rows.append(LegacyRow(
            row_id=r.row_id,
            period_name=r.periodo or r.label,
            phase_name=r.fase,
            start_date=None,
            end_date=None,
            color=PERIOD_COLORS[i % len(PERIOD_COLORS)],
            source="period_table" if not r.is_fallback else "fallback",
        ))

    # ------------------------------------------------------------------
    # 2. Convert ProjectedGraph.nodes → CytoscapeElement list
    # ------------------------------------------------------------------
    # Build a lookup: row_id → index so we can calculate y positions
    row_index = {r.row_id: i for i, r in enumerate(graph.rows)}
    row_height = 200
    node_h, node_w = 30.0, 80.0
    # Track column (x) per row so nodes in the same row are spread horizontally
    col_counter: dict[str, int] = {}

    nodes: list[CytoscapeElement] = []
    for n in graph.nodes:
        ri = row_index.get(n.row_id, 0)
        col = col_counter.get(n.row_id, 0)
        col_counter[n.row_id] = col + 1
        x = col * (node_w + 20) + 30
        y = ri * row_height + (row_height / 2 - node_h / 2)

        nodes.append(CytoscapeElement(
            data={
                "id": n.node_id,
                "us": n.us,
                "us_number": n.us,
                "area": n.area or "",
                "unit_type": n.unit_type or "US",
                "description": n.description or "",
                "row": n.row_id,
                "label": str(n.us),
            },
            position={"x": x, "y": y},
        ))

    # ------------------------------------------------------------------
    # 3. Convert ProjectedGraph.edges → CytoscapeElement list with italian labels
    # ------------------------------------------------------------------
    edges: list[CytoscapeElement] = []
    for e in graph.edges:
        italian = display_label(e.canonical, locale="it")
        edges.append(CytoscapeElement(
            data={
                "id": f"{e.source_id}__{e.canonical}__{e.target_id}",
                "source": e.source_id,
                "target": e.target_id,
                "label": italian,
                "canonical": e.canonical,
                "relationship": CANONICAL_TO_ITALIAN.get(e.canonical, e.canonical),
            },
        ))

    # ------------------------------------------------------------------
    # 4. Build a minimal state-like object the legacy writer accepts
    # ------------------------------------------------------------------
    class _State:
        def __init__(self):
            self.site = graph.site
            self.group_by = graph.group_by
            self.rows = rows
            self.nodes = nodes
            self.edges = edges
            self.pending_changes = {}

    state = _State()

    # ------------------------------------------------------------------
    # 5. Call the canonical writer and return bytes
    # ------------------------------------------------------------------
    from pyarchinit_mini.graphml_io.yed_writer import write_extended_matrix_graphml

    epochs: list[dict] = []
    # Populate epochs from rows that have dating information
    for r in graph.rows:
        if r.datazione:
            epochs.append({
                "row_id": r.row_id,
                "periodo": r.periodo,
                "fase": r.fase,
                "datazione": r.datazione,
            })

    with tempfile.NamedTemporaryFile(suffix=".graphml", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        write_extended_matrix_graphml(
            state,
            site_meta={"sito": graph.site},
            epochs=epochs,
            out=Path(tmp_path),
        )
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
