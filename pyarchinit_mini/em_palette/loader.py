"""EM palette GraphML parser with caching and hot-reload.

The palette is a yEd-flavoured GraphML document where each <node> represents
one canonical US type (USM, USD, USV, SF, VSF, TSU, USVn) and each <edge>
represents one canonical stratigraphic relation (overlies, cuts, fills, abuts,
has_same_time, is_after, is_before, is_bonded_to).

Unit type and canonical relation are identified by the text content of
<y:NodeLabel> and <y:EdgeLabel> respectively.
"""
from __future__ import annotations

import logging
import signal
import threading
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional

from .styles import NodeStyle, EdgeStyle


logger = logging.getLogger(__name__)

NS = {
    "g": "http://graphml.graphdrawing.org/xmlns",
    "y": "http://www.yworks.com/xml/graphml",
}

DEFAULT_PALETTE_PATH = (
    Path(__file__).parent.parent
    / "graphml_converter" / "templates" / "EM_palette.graphml"
)


class PaletteLoader:
    def __init__(
        self,
        palette_path: Optional[Path] = None,
        *,
        allow_fallback: bool = True,
    ) -> None:
        self.palette_path = palette_path or DEFAULT_PALETTE_PATH
        self.allow_fallback = allow_fallback
        self._node_cache: Dict[str, NodeStyle] = {}
        self._edge_cache: Dict[str, EdgeStyle] = {}
        self._loaded = False
        self._lock = threading.Lock()

    def _load(self) -> None:
        with self._lock:
            if self._loaded:
                return
            try:
                tree = ET.parse(self.palette_path)
            except (FileNotFoundError, ET.ParseError) as exc:
                if self.allow_fallback:
                    logger.warning(
                        "Palette load failed (%s); using hardcoded fallbacks.", exc,
                    )
                    self._loaded = True
                    return
                raise
            root = tree.getroot()
            for node_el in root.iter(f"{{{NS['g']}}}node"):
                style = self._parse_node(node_el)
                if style is not None:
                    self._node_cache[style.unit_type] = style
            for edge_el in root.iter(f"{{{NS['g']}}}edge"):
                style = self._parse_edge(edge_el)
                if style is not None:
                    self._edge_cache[style.canonical_name] = style
            self._loaded = True

    def _parse_node(self, node_el: ET.Element) -> Optional[NodeStyle]:
        shape_node = node_el.find(f".//{{{NS['y']}}}ShapeNode")
        if shape_node is None:
            return None
        label = shape_node.find(f".//{{{NS['y']}}}NodeLabel")
        if label is None or not (label.text and label.text.strip()):
            return None
        unit_type = label.text.strip()
        shape_el = shape_node.find(f"{{{NS['y']}}}Shape")
        shape = shape_el.attrib.get("type", "rectangle") if shape_el is not None else "rectangle"
        fill_el = shape_node.find(f"{{{NS['y']}}}Fill")
        fill_color = fill_el.attrib.get("color", "#FFFFFF") if fill_el is not None else "#FFFFFF"
        border_el = shape_node.find(f"{{{NS['y']}}}BorderStyle")
        if border_el is not None:
            border_color = border_el.attrib.get("color", "#000000")
            border_width = float(border_el.attrib.get("width", "1.0"))
            border_style = border_el.attrib.get("type", "line")
        else:
            border_color = "#000000"
            border_width = 1.0
            border_style = "line"
        font_color = label.attrib.get("textColor", "#000000")
        font_size = int(label.attrib.get("fontSize", "12"))
        return NodeStyle(
            unit_type=unit_type,
            shape=shape,
            fill_color=fill_color,
            border_color=border_color,
            border_width=border_width,
            border_style=border_style,
            font_color=font_color,
            font_size=font_size,
        )

    def _parse_edge(self, edge_el: ET.Element) -> Optional[EdgeStyle]:
        line_el = edge_el.find(f".//{{{NS['y']}}}LineStyle")
        label_el = edge_el.find(f".//{{{NS['y']}}}EdgeLabel")
        arrow_el = edge_el.find(f".//{{{NS['y']}}}Arrows")
        if label_el is None or not (label_el.text and label_el.text.strip()):
            return None
        canonical = label_el.text.strip().lower().replace(" ", "_")
        if not canonical:
            return None
        if line_el is not None:
            line_color = line_el.attrib.get("color", "#000000")
            line_width = float(line_el.attrib.get("width", "1.0"))
            line_style = line_el.attrib.get("type", "line")
        else:
            line_color = "#000000"
            line_width = 1.0
            line_style = "line"
        if arrow_el is not None:
            arrow_target = arrow_el.attrib.get("target", "standard")
            arrow_source = arrow_el.attrib.get("source", "none")
        else:
            arrow_target = "standard"
            arrow_source = "none"
        return EdgeStyle(
            canonical_name=canonical,
            line_color=line_color,
            line_width=line_width,
            line_style=line_style,
            arrow_target=arrow_target,
            arrow_source=arrow_source,
        )

    def get_node_style(self, unit_type: str) -> NodeStyle:
        self._load()
        return self._node_cache.get(unit_type, NodeStyle(unit_type=unit_type))

    def get_edge_style(self, canonical_name: str) -> EdgeStyle:
        self._load()
        return self._edge_cache.get(canonical_name, EdgeStyle(canonical_name=canonical_name))

    def reload(self) -> None:
        with self._lock:
            self._node_cache.clear()
            self._edge_cache.clear()
            self._loaded = False
        self._load()


_singleton: Optional[PaletteLoader] = None


def get_palette() -> PaletteLoader:
    global _singleton
    if _singleton is None:
        _singleton = PaletteLoader()
    return _singleton


def install_sighup_reload() -> None:
    def _handler(_signum, _frame):
        logger.info("SIGHUP received: reloading EM palette")
        get_palette().reload()
    signal.signal(signal.SIGHUP, _handler)
