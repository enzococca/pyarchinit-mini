"""Parse uploaded yEd GraphML into a contract s3dgraphy.Graph.

Minimal parser: reads <node> elements, extracts label (= US number) and the
shape type. Reads <edge> elements with source/target/label. The label of
each edge is resolved via rapporti_codec to a canonical relation; unknowns
default to "overlies".
"""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from io import BytesIO

from s3dgraphy import Graph

from pyarchinit_mini.graphproj.strat_graph import (
    FALLBACK_ROW, new_graph, new_strat_node, set_pyarchinit_attrs, set_swimlane,
    stratigraphic_nodes,
)
from pyarchinit_mini.graphproj.rapporti_codec import _resolve_canonical


logger = logging.getLogger(__name__)


NS_G = "http://graphml.graphdrawing.org/xmlns"
NS_Y = "http://www.yworks.com/xml/graphml"


def parse_graphml(raw: bytes, *, target_site: str) -> Graph:
    """Parse yEd-flavoured GraphML bytes into a contract s3dgraphy Graph.

    Args:
        raw: Raw bytes of the GraphML file.
        target_site: The site code to assign to all parsed nodes.

    Returns:
        A populated s3dgraphy Graph ready for write_graph.
    """
    tree = ET.parse(BytesIO(raw))
    root = tree.getroot()
    graph = new_graph(target_site)
    set_swimlane(graph, site=target_site, group_by="none", rows=[dict(FALLBACK_ROW)])

    for node_el in root.iter(f"{{{NS_G}}}node"):
        shape_node = node_el.find(f".//{{{NS_Y}}}ShapeNode")
        if shape_node is None:
            continue
        label_el = shape_node.find(f".//{{{NS_Y}}}NodeLabel")
        if label_el is None or not (label_el.text and label_el.text.strip()):
            continue
        us_num = label_el.text.strip()
        xml_id = node_el.attrib.get("id")
        # default type; richer mapping is the palette's job on export side
        node = new_strat_node(node_id=xml_id, name=us_num, unit_type="US")
        set_pyarchinit_attrs(node, us=us_num, unit_type="US", sito=target_site,
                             row_id="row_0", node_uuid=xml_id)
        graph.add_node(node)

    known = {n.node_id for n in stratigraphic_nodes(graph)}
    for edge_el in root.iter(f"{{{NS_G}}}edge"):
        src = edge_el.attrib.get("source")
        tgt = edge_el.attrib.get("target")
        if not src or not tgt:
            continue
        if src not in known or tgt not in known:
            continue
        label_el = edge_el.find(f".//{{{NS_Y}}}EdgeLabel")
        label = (label_el.text or "").strip() if label_el is not None and label_el.text else "overlies"
        canonical = _resolve_canonical(label) or "overlies"
        edge_id = f"{src}__{canonical}__{tgt}"
        if graph.find_edge_by_id(edge_id) is not None:
            continue
        graph.add_edge(edge_id, src, tgt, canonical)

    return graph
