import json
import pytest

from pyarchinit_mini.graphproj.heriverse_parser import parse_heriverse
from pyarchinit_mini.graphproj.strat_graph import (
    FALLBACK_ROW, get_swimlane, pyarchinit_attrs, stratigraphic_edges, stratigraphic_nodes,
)


SAMPLE = {
    "wapp": "heriverse",
    "multigraph": {
        "graphs": [{
            "id": "g0",
            "name": "Site_A",
            "nodes": {
                "USM": [{"id": "us_1", "name": "US1", "type": "USM", "data": {"area": "A1"}}],
                "USV": [{"id": "us_2", "name": "US2", "type": "USV", "data": {"area": "A1"}}],
                "USVn": [], "USD": [], "SF": [], "VSF": [], "TSU": [],
            },
            "edges": {
                "line": [{"id": "e1", "from": "us_1", "to": "us_2", "type": "line"}],
            },
            "semantic_shapes": {}, "representation_models": {}, "panorama_models": {},
        }]
    },
    "couchdb_metadata": {}, "epochs": [],
}


def _by_us(g):
    return {pyarchinit_attrs(n)["us"]: pyarchinit_attrs(n) for n in stratigraphic_nodes(g)}


def test_parse_heriverse_returns_contract_graph():
    g = parse_heriverse(json.dumps(SAMPLE))
    sw = get_swimlane(g)
    assert sw["site"] == "Site_A"
    assert sw["group_by"] == "none"
    assert len(stratigraphic_nodes(g)) == 2


def test_parse_heriverse_unit_types_preserved():
    g = parse_heriverse(json.dumps(SAMPLE))
    by_us = {us: a["unit_type"] for us, a in _by_us(g).items()}
    assert by_us["US1"] == "USM"
    assert by_us["US2"] == "USV"


def test_parse_heriverse_area_from_data_dict():
    g = parse_heriverse(json.dumps(SAMPLE))
    by_us = {us: a["area"] for us, a in _by_us(g).items()}
    assert by_us["US1"] == "A1"
    assert by_us["US2"] == "A1"


def test_parse_heriverse_creates_edges_with_canonical_mapping():
    g = parse_heriverse(json.dumps(SAMPLE))
    edges = stratigraphic_edges(g)
    assert len(edges) == 1
    e = edges[0]
    # Heriverse "line" edge type maps to canonical "overlies"
    assert e.edge_type == "overlies"
    assert e.edge_source == "us_1"
    assert e.edge_target == "us_2"


def test_parse_heriverse_skips_edges_with_missing_endpoints():
    sample = json.loads(json.dumps(SAMPLE))  # deep copy
    sample["multigraph"]["graphs"][0]["edges"]["line"].append({
        "id": "e_bad", "from": "us_nonexistent", "to": "us_2", "type": "line",
    })
    g = parse_heriverse(json.dumps(sample))
    # only the 1 valid edge remains
    assert len(stratigraphic_edges(g)) == 1


def test_parse_heriverse_empty_returns_minimal_graph():
    minimal = {"wapp": "heriverse", "multigraph": {"graphs": []}, "couchdb_metadata": {}}
    g = parse_heriverse(json.dumps(minimal))
    assert get_swimlane(g)["site"] == "UnknownSite"
    assert stratigraphic_nodes(g) == []
    assert stratigraphic_edges(g) == []


def test_parse_heriverse_has_fallback_row():
    """A fallback row is always present so consumers don't have to handle the empty case."""
    g = parse_heriverse(json.dumps(SAMPLE))
    assert get_swimlane(g)["rows"] == [FALLBACK_ROW]


def test_parse_heriverse_edge_type_cuts_mapping():
    sample = json.loads(json.dumps(SAMPLE))
    sample["multigraph"]["graphs"][0]["edges"]["cuts"] = [
        {"id": "ec", "from": "us_1", "to": "us_2", "type": "cuts"},
    ]
    g = parse_heriverse(json.dumps(sample))
    cans = {e.edge_type for e in stratigraphic_edges(g)}
    assert "cuts" in cans
