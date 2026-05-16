from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class VisualStyle:
    shape: str
    fill_color: str
    border_color: str
    border_style: str
    border_width: float = 3.0
    text_color: str = "#000000"
    font_family: str = "DialogInput"
    font_size: int = 24
    font_style: str = "bold"
    label_position: str = "over"
    file_2d_raster: Optional[str] = None
    file_2d_vector: Optional[str] = None
    file_3d: Optional[str] = None
    material_rgba: Optional[tuple[float, float, float, float]] = None

    @classmethod
    def fallback(cls) -> "VisualStyle":
        return cls(
            shape="rectangle",
            fill_color="#CCCCCC",
            border_color="#000000",
            border_style="solid",
        )


@dataclass(frozen=True)
class UnitType:
    abbreviation: str
    class_name: str
    parent: Optional[str]
    label: str
    description: str
    symbol: str
    family: Optional[str]
    is_series: bool
    cidoc_mapping: Optional[str]
    properties: dict[str, str]
    visual_style: VisualStyle


@dataclass(frozen=True)
class EdgeType:
    name: str
    label: str
    italian_aliases: tuple[str, ...]
    symmetric: bool
    legal_pairs: tuple[tuple[str, str], ...]
