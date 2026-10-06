from pyarchinit_mini.graphproj.strat_edges import (
    NodeIndex, StratEdge, add_stratigraphic_edges, build_stratigraphic_edges,
)
from pyarchinit_mini.graphproj.strat_graph import stratigraphic_edges
from tests.unit.strat_graph_factory import make_graph


def _g():
    return make_graph(nodes=[{"id": "n1", "us": "1", "area": "A"}, {"id": "n2", "us": "2", "area": "A"},
                             {"id": "n3", "us": "3", "area": "A"}, {"id": "n2b", "us": "2", "area": "B"}])


def test_copre_becomes_overlies_forward():
    g = _g(); idx = NodeIndex.from_graph(g)
    edges = build_stratigraphic_edges([("n1", "[['Copre', '2', 'A', 'S']]")], site="S", index=idx)
    assert edges == [StratEdge("n1", "n2", "overlies")]


def test_inverse_rapporti_are_swapped_to_forward():
    g = _g(); idx = NodeIndex.from_graph(g)
    for raw, canonical in [("[['Coperto da', '2', 'A', 'S']]", "overlies"),
                           ("[['Tagliato da', '2', 'A', 'S']]", "cuts"),
                           ("[['Riempito da', '2', 'A', 'S']]", "fills")]:
        assert build_stratigraphic_edges([("n1", raw)], site="S", index=idx) == [StratEdge("n2", "n1", canonical)]


def test_reciprocal_symmetric_is_emitted_once():
    g = _g(); idx = NodeIndex.from_graph(g)
    edges = build_stratigraphic_edges([("n1", "[['Uguale a', '2', 'A', 'S']]"),
                                       ("n2", "[['Uguale a', '1', 'A', 'S']]")], site="S", index=idx)
    assert len(edges) == 1 and edges[0].canonical == "has_same_time"


def test_forward_and_its_inverse_on_both_rows_dedup_to_one_edge():
    g = _g(); idx = NodeIndex.from_graph(g)
    edges = build_stratigraphic_edges([("n1", "[['Copre', '2', 'A', 'S']]"),
                                       ("n2", "[['Coperto da', '1', 'A', 'S']]")], site="S", index=idx)
    assert edges == [StratEdge("n1", "n2", "overlies")]


def test_transitive_reduction_drops_implied_edge():
    g = _g(); idx = NodeIndex.from_graph(g)
    edges = build_stratigraphic_edges([("n1", "[['Copre', '2', 'A', 'S'], ['Copre', '3', 'A', 'S']]"),
                                       ("n2", "[['Copre', '3', 'A', 'S']]")], site="S", index=idx)
    assert set(edges) == {StratEdge("n1", "n2", "overlies"), StratEdge("n2", "n3", "overlies")}


def test_target_resolves_by_area_then_us():
    g = _g(); idx = NodeIndex.from_graph(g)
    assert build_stratigraphic_edges([("n1", "[['Copre', '2', 'B', 'S']]")], site="S", index=idx) == [StratEdge("n1", "n2b", "overlies")]
    assert build_stratigraphic_edges([("n1", "[['Copre', '2']]")], site="S", index=idx)[0].target_id == "n2"


def test_unknown_target_and_second_rapporto_keep_original_source():
    g = _g(); idx = NodeIndex.from_graph(g)
    edges = build_stratigraphic_edges([("n1", "[['Coperto da', '99', 'A', 'S'], ['Copre', '3', 'A', 'S']]")], site="S", index=idx)
    assert edges == [StratEdge("n1", "n3", "overlies")]


def test_free_text_rapporti_are_tokenised():
    g = _g(); idx = NodeIndex.from_graph(g)
    edges = build_stratigraphic_edges([("n1", "Copre 2, Taglia 3")], site="S", index=idx)
    assert set(edges) == {StratEdge("n1", "n2", "overlies"), StratEdge("n1", "n3", "cuts")}


def test_free_text_inverse_is_swapped():
    g = _g(); idx = NodeIndex.from_graph(g)
    assert build_stratigraphic_edges([("n1", "coperto da 2")], site="S", index=idx) == [StratEdge("n2", "n1", "overlies")]


def test_add_edges_is_idempotent_and_uses_contract_ids():
    g = _g()
    e = [StratEdge("n1", "n2", "overlies")]
    assert add_stratigraphic_edges(g, e) == 1
    assert add_stratigraphic_edges(g, e) == 0
    assert [x.edge_id for x in stratigraphic_edges(g)] == ["n1__overlies__n2"]
    assert stratigraphic_edges(g)[0].edge_type == "overlies"


def test_edge_types_constant_is_the_forward_only_contract():
    from pyarchinit_mini.graphproj.strat_edges import STRATIGRAPHIC_EDGE_TYPES
    assert STRATIGRAPHIC_EDGE_TYPES == {"overlies", "cuts", "fills", "abuts", "has_same_time", "is_bonded_to", "is_before"}


def test_area_qualified_rapporto_to_unknown_area_yields_no_edge():
    g = _g(); idx = NodeIndex.from_graph(g)
    assert build_stratigraphic_edges([("n1", "[['Copre', '2', 'C', 'S']]")], site="S", index=idx) == []


def test_self_referencing_rapporto_is_dropped():
    g = _g(); idx = NodeIndex.from_graph(g)
    assert build_stratigraphic_edges([("n1", "[['Copre', '1', 'A', 'S']]")], site="S", index=idx) == []
