"""yEd-flavoured GraphML writer using EM_palette.graphml as the document base.

Strategy: load the palette XML, append site nodes/edges into the <graph> element,
serialize. The palette's existing node/edge definitions remain in place so yEd
opens the file with all unit types visible in the palette panel.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from typing import Optional

from pyarchinit_mini.em_palette import get_palette
from pyarchinit_mini.em_palette.loader import DEFAULT_PALETTE_PATH
from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph


NS_G = "http://graphml.graphdrawing.org/xmlns"
NS_Y = "http://www.yworks.com/xml/graphml"


def write_graphml(graph: ProjectedGraph, *, palette_path: Optional[Path] = None) -> bytes:
    """Render the projected graph as yEd-compatible GraphML bytes."""
    palette_path = palette_path or DEFAULT_PALETTE_PATH
    ET.register_namespace("", NS_G)
    ET.register_namespace("y", NS_Y)
    tree = ET.parse(palette_path)
    root = tree.getroot()
    graph_el = root.find(f"{{{NS_G}}}graph")
    if graph_el is None:
        raise RuntimeError("Palette template missing <graph> element")

    palette = get_palette()

    for n in graph.nodes:
        ns = palette.get_node_style(n.unit_type)
        node_el = ET.SubElement(graph_el, f"{{{NS_G}}}node", attrib={"id": n.node_id})
        data_el = ET.SubElement(node_el, f"{{{NS_G}}}data", attrib={"key": "d7"})
        shape_node = ET.SubElement(data_el, f"{{{NS_Y}}}ShapeNode")
        ET.SubElement(
            shape_node, f"{{{NS_Y}}}Geometry",
            attrib={"height": "30.0", "width": "60.0", "x": "0.0", "y": "0.0"},
        )
        ET.SubElement(
            shape_node, f"{{{NS_Y}}}Fill",
            attrib={"color": ns.fill_color, "transparent": "false"},
        )
        ET.SubElement(
            shape_node, f"{{{NS_Y}}}BorderStyle",
            attrib={
                "color": ns.border_color,
                "type": ns.border_style,
                "width": str(ns.border_width),
            },
        )
        label = ET.SubElement(
            shape_node, f"{{{NS_Y}}}NodeLabel",
            attrib={"textColor": ns.font_color, "fontSize": str(ns.font_size)},
        )
        label.text = n.us
        ET.SubElement(shape_node, f"{{{NS_Y}}}Shape", attrib={"type": ns.shape})

    for e in graph.edges:
        es = palette.get_edge_style(e.canonical)
        edge_el = ET.SubElement(
            graph_el, f"{{{NS_G}}}edge",
            attrib={
                "id": f"{e.source_id}__{e.target_id}",
                "source": e.source_id,
                "target": e.target_id,
            },
        )
        data_el = ET.SubElement(edge_el, f"{{{NS_G}}}data", attrib={"key": "d13"})
        poly = ET.SubElement(data_el, f"{{{NS_Y}}}PolyLineEdge")
        ET.SubElement(
            poly, f"{{{NS_Y}}}LineStyle",
            attrib={"color": es.line_color, "type": es.line_style, "width": str(es.line_width)},
        )
        ET.SubElement(
            poly, f"{{{NS_Y}}}Arrows",
            attrib={"source": es.arrow_source, "target": es.arrow_target},
        )
        elabel = ET.SubElement(poly, f"{{{NS_Y}}}EdgeLabel")
        elabel.text = e.canonical

    buf = BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    return buf.getvalue()
