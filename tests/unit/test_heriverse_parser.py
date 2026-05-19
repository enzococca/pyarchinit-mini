import json
import pytest

from pyarchinit_mini.graphproj.heriverse_parser import parse_heriverse


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


def test_parse_heriverse_returns_projected_graph():
    g = parse_heriverse(json.dumps(SAMPLE))
    assert g.site == "Site_A"
    assert g.group_by == "none"
    assert len(g.nodes) == 2


def test_parse_heriverse_unit_types_preserved():
    g = parse_heriverse(json.dumps(SAMPLE))
    by_us = {n.us: n.unit_type for n in g.nodes}
    assert by_us["US1"] == "USM"
    assert by_us["US2"] == "USV"


def test_parse_heriverse_area_from_data_dict():
    g = parse_heriverse(json.dumps(SAMPLE))
    by_us = {n.us: n.area for n in g.nodes}
    assert by_us["US1"] == "A1"
    assert by_us["US2"] == "A1"


def test_parse_heriverse_creates_edges_with_canonical_mapping():
    g = parse_heriverse(json.dumps(SAMPLE))
    assert len(g.edges) == 1
    e = g.edges[0]
    # Heriverse "line" edge type maps to canonical "overlies"
    assert e.canonical == "overlies"
    assert e.source_id == "us_1"
    assert e.target_id == "us_2"


def test_parse_heriverse_skips_edges_with_missing_endpoints():
    sample = dict(SAMPLE)
    sample = json.loads(json.dumps(SAMPLE))  # deep copy
    sample["multigraph"]["graphs"][0]["edges"]["line"].append({
        "id": "e_bad", "from": "us_nonexistent", "to": "us_2", "type": "line",
    })
    g = parse_heriverse(json.dumps(sample))
    # only the 1 valid edge remains
    assert len(g.edges) == 1


def test_parse_heriverse_empty_returns_minimal_graph():
    minimal = {"wapp": "heriverse", "multigraph": {"graphs": []}, "couchdb_metadata": {}}
    g = parse_heriverse(json.dumps(minimal))
    assert g.site == "UnknownSite"
    assert g.nodes == []
    assert g.edges == []


def test_parse_heriverse_has_fallback_row():
    """A "Periodo 1" fallback row is always present so consumers don't have to handle the empty case."""
    g = parse_heriverse(json.dumps(SAMPLE))
    assert len(g.rows) == 1
    assert g.rows[0].label == "Periodo 1"
    assert g.rows[0].is_fallback is True


def test_parse_heriverse_edge_type_cuts_mapping():
    sample = json.loads(json.dumps(SAMPLE))
    sample["multigraph"]["graphs"][0]["edges"]["cuts"] = [
        {"id": "ec", "from": "us_1", "to": "us_2", "type": "cuts"},
    ]
    g = parse_heriverse(json.dumps(sample))
    cans = {e.canonical for e in g.edges}
    assert "cuts" in cans
