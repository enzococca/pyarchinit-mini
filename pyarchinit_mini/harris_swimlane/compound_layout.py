"""Cytoscape compound layout helpers + row_id slugifier.

Coordinate system: x grows right, y grows DOWN. Recent rows at TOP (smaller y).
"""
from __future__ import annotations

import re
import unicodedata
from typing import Optional


CANVAS_WIDTH = 2000
ROW_HEIGHT_BASE = 80
ROW_HEIGHT_PER_NODE = 40
NODE_WIDTH = 100
NODE_HORIZONTAL_GAP = 20
NODE_INITIAL_X = 50
NODE_INITIAL_Y = 20


def derive_row_id(period_name: Optional[str], phase_name: Optional[str]) -> str:
    if not period_name or not period_name.strip():
        return "_unassigned"
    p_slug = _slug_part(period_name)
    if not phase_name or not phase_name.strip():
        return f"row_{p_slug}"
    ph_slug = _slug_part(phase_name)
    return f"row_{p_slug}_{ph_slug}"


def _slug_part(s: str) -> str:
    folded = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    out = folded.lower()
    out = re.sub(r"[^a-z0-9]+", "-", out)
    return out.strip("-")


def initial_node_position(row, index_in_row: int) -> dict:
    return {
        "x": NODE_INITIAL_X + index_in_row * (NODE_WIDTH + NODE_HORIZONTAL_GAP),
        "y": NODE_INITIAL_Y,
    }


def compute_row_positions(rows) -> dict:
    dated = [r for r in rows if r.start_date is not None]
    undated = [r for r in rows if r.start_date is None]
    dated_sorted = sorted(dated, key=lambda r: -r.start_date)
    ordered = dated_sorted + undated
    positions = {}
    cursor_y = 0
    for row in ordered:
        positions[row.row_id] = (0, cursor_y)
        cursor_y += ROW_HEIGHT_BASE
    return positions
