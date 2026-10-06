from pyarchinit_mini.graphproj.graphml_reader import parse_graphml
from pyarchinit_mini.graphproj.strat_graph import (
    FALLBACK_ROW, get_swimlane, pyarchinit_attrs, stratigraphic_edges, stratigraphic_nodes,
)

YED = b"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:y="http://www.yworks.com/xml/graphml">
  <graph id="G" edgedefault="directed">
    <node id="n1"><data><y:ShapeNode><y:NodeLabel>1</y:NodeLabel></y:ShapeNode></data></node>
    <node id="n2"><data><y:ShapeNode><y:NodeLabel>2</y:NodeLabel></y:ShapeNode></data></node>
    <edge id="e1" source="n1" target="n2"><data><y:PolyLineEdge><y:EdgeLabel>cuts</y:EdgeLabel></y:PolyLineEdge></data></edge>
    <edge id="e2" source="n1" target="ghost"/>
  </graph>
</graphml>"""


def test_parse_graphml_builds_contract_graph():
    g = parse_graphml(YED, target_site="S")
    nodes = stratigraphic_nodes(g)
    assert {pyarchinit_attrs(n)["us"] for n in nodes} == {"1", "2"}
    assert all(pyarchinit_attrs(n)["sito"] == "S" for n in nodes)
    assert get_swimlane(g)["rows"] == [FALLBACK_ROW]
    edges = stratigraphic_edges(g)
    assert len(edges) == 1
    assert (edges[0].edge_source, edges[0].edge_target) == ("n1", "n2")
    assert edges[0].edge_type == "cuts"


def test_parse_graphml_duplicate_edges_collapse_to_one():
    dup = YED.replace(b'<edge id="e2" source="n1" target="ghost"/>',
                      b'<edge id="e2" source="n1" target="n2"><data><y:PolyLineEdge><y:EdgeLabel>cuts</y:EdgeLabel></y:PolyLineEdge></data></edge>')
    g = parse_graphml(dup, target_site="S")
    assert len(stratigraphic_edges(g)) == 1
