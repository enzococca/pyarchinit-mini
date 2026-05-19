"""Dataclasses for palette-derived rendering styles."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NodeStyle:
    unit_type: str
    shape: str = "rectangle"  # rectangle, ellipse, roundrectangle, parallelogram, hexagon, octagon
    fill_color: str = "#FFFFFF"
    border_color: str = "#000000"
    border_width: float = 1.0
    border_style: str = "line"  # line, dashed, dotted
    font_color: str = "#000000"
    font_size: int = 12
    label_placement: str = "center"


@dataclass(frozen=True)
class EdgeStyle:
    canonical_name: str
    line_color: str = "#000000"
    line_width: float = 1.0
    line_style: str = "line"  # line, dashed, dotted
    arrow_source: str = "none"
    arrow_target: str = "standard"
