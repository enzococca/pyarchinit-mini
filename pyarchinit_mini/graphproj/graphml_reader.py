"""Parse uploaded yEd GraphML into a ProjectedGraph.

Minimal parser: reads <node> elements, extracts label (= US number) and the
shape type. Reads <edge> elements with source/target/label. The label of
each edge is resolved via rapporti_codec to a canonical relation; unknowns
default to "overlies".
"""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from io import BytesIO

from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph, Row, Node, Edge
from pyarchinit_mini.graphproj.rapporti_codec import _resolve_canonical


logger = logging.getLogger(__name__)


NS_G = "http://graphml.graphdrawing.org/xmlns"
NS_Y = "http://www.yworks.com/xml/graphml"


def parse_graphml(raw: bytes, *, target_site: str) -> ProjectedGraph:
    """Parse yEd-flavoured GraphML bytes into a ProjectedGraph.

    Args:
        raw: Raw bytes of the GraphML file.
        target_site: The site code to assign to all parsed nodes.

    Returns:
        A populated ProjectedGraph ready for write_graph.
    """
    tree = ET.parse(BytesIO(raw))
    root = tree.getroot()
    out = ProjectedGraph(site=target_site, group_by="none")
    out.rows.append(Row(row_id="row_0", label="Periodo 1", is_fallback=True))

    for node_el in root.iter(f"{{{NS_G}}}node"):
        shape_node = node_el.find(f".//{{{NS_Y}}}ShapeNode")
        if shape_node is None:
            continue
        label_el = shape_node.find(f".//{{{NS_Y}}}NodeLabel")
        if label_el is None or not (label_el.text and label_el.text.strip()):
            continue
        us_num = label_el.text.strip()
        unit_type = "US"  # default; richer mapping is the palette's job on export side
        out.nodes.append(Node(
            node_id=node_el.attrib.get("id"),
            us=us_num,
            area=None,
            sito=target_site,
            unit_type=unit_type,
            description=None,
            row_id="row_0",
        ))

    node_ids = {n.node_id for n in out.nodes}
    for edge_el in root.iter(f"{{{NS_G}}}edge"):
        src = edge_el.attrib.get("source")
        tgt = edge_el.attrib.get("target")
        if not src or not tgt:
            continue
        if src not in node_ids or tgt not in node_ids:
            continue
        label_el = edge_el.find(f".//{{{NS_Y}}}EdgeLabel")
        label = (label_el.text or "").strip() if label_el is not None and label_el.text else "overlies"
        canonical = _resolve_canonical(label) or "overlies"
        out.edges.append(Edge(source_id=src, target_id=tgt, canonical=canonical))

    return out
