from s3dgraphy.nodes.geo_position_node import GeoPositionNode
from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode

from pyarchinit_mini.graphproj.strat_graph import (
    FALLBACK_ROW, get_swimlane, new_graph, new_strat_node, pyarchinit_attrs,
    set_pyarchinit_attrs, set_swimlane, stratigraphic_edges, stratigraphic_nodes,
)


def test_new_graph_has_site_id_and_only_the_geo_node():
    g = new_graph("Volterra")
    assert g.graph_id == "strat:Volterra"
    assert stratigraphic_nodes(g) == []
    assert any(isinstance(n, GeoPositionNode) for n in g.nodes)


def test_new_strat_node_picks_subclass_from_unit_type():
    usvs = new_strat_node(node_id="u", name="USVs3", unit_type="USVs")
    assert isinstance(usvs, StratigraphicNode)
    assert type(usvs).__name__ == "StructuralVirtualStratigraphicUnit"
    assert type(new_strat_node(node_id="m", name="USM2", unit_type="USM")).__name__ == "StratigraphicUnit"


def test_set_and_read_pyarchinit_attrs_keeps_legacy_keys():
    n = new_strat_node(node_id="u", name="US1", unit_type="US")
    set_pyarchinit_attrs(n, us="1", unit_type="US", sito="S", area="A", row_id="row_0",
                         node_uuid="u", family="stratigraphic")
    assert pyarchinit_attrs(n)["us"] == "1"
    assert pyarchinit_attrs(n)["area"] == "A"
    assert n.attributes["unit_type"] == "US"
    assert n.attributes["EMid"] == "u"
    assert n.attributes["family"] == "stratigraphic"


def test_pyarchinit_attrs_is_empty_dict_for_foreign_nodes():
    n = new_strat_node(node_id="u", name="US1", unit_type="US")
    assert pyarchinit_attrs(n) == {}


def test_stratigraphic_edges_excludes_edges_to_non_stratigraphic_nodes():
    g = new_graph("S")
    a = g.add_node(new_strat_node(node_id="a", name="US1", unit_type="US"))
    b = g.add_node(new_strat_node(node_id="b", name="US2", unit_type="US"))
    geo = [n for n in g.nodes if isinstance(n, GeoPositionNode)][0]
    g.add_edge("a__overlies__b", "a", "b", "overlies")
    g.add_edge("a_geo", "a", geo.node_id, "generic_connection")
    assert [e.edge_id for e in stratigraphic_edges(g)] == ["a__overlies__b"]


def test_swimlane_roundtrip_and_default():
    g = new_graph("S")
    assert get_swimlane(g) == {"site": "S", "group_by": "none", "rows": []}
    set_swimlane(g, site="S", group_by="area", rows=[FALLBACK_ROW])
    assert get_swimlane(g)["rows"][0]["label"] == "Periodo 1"
    assert get_swimlane(g)["group_by"] == "area"
