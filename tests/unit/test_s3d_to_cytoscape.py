import pytest

from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph, Row, Node, Edge
from pyarchinit_mini.graphproj.s3d_to_cytoscape import to_cytoscape


def _graph_with_two_us(group_by="none"):
    g = ProjectedGraph(site="S", group_by=group_by)
    g.rows = [Row(row_id="row_0", label="I/a", periodo="I", fase="a")]
    g.nodes = [
        Node(node_id="us_1", us="1", area="A", sito="S", unit_type="USM",
             description="x", row_id="row_0", sub_group=None),
        Node(node_id="us_2", us="2", area="A", sito="S", unit_type="USV",
             description="y", row_id="row_0", sub_group=None),
    ]
    g.edges = [Edge(source_id="us_1", target_id="us_2", canonical="overlies")]
    return g


def test_to_cytoscape_top_level_keys():
    out = to_cytoscape(_graph_with_two_us())
    assert set(out.keys()) >= {"site", "group_by", "rows", "nodes", "edges"}


def test_to_cytoscape_node_has_style_from_palette():
    out = to_cytoscape(_graph_with_two_us())
    usm = next(n for n in out["nodes"] if n["data"]["id"] == "us_1")
    assert "style" in usm
    assert "shape" in usm["style"]
    assert usm["style"]["backgroundColor"].startswith("#")
    assert usm["data"]["label"] == "1"


def test_to_cytoscape_edge_has_style_from_palette():
    out = to_cytoscape(_graph_with_two_us())
    assert len(out["edges"]) == 1
    e = out["edges"][0]
    assert "style" in e
    assert "lineColor" in e["style"]
    assert e["data"]["label"] == "Copre"
    assert e["data"]["canonical"] == "overlies"
    assert e["data"]["source"] == "us_1"
    assert e["data"]["target"] == "us_2"


def test_to_cytoscape_with_sub_group_creates_compound_parents():
    g = _graph_with_two_us(group_by="area")
    for n in g.nodes:
        n.sub_group = "A"
    out = to_cytoscape(g)
    parents = [n for n in out["nodes"] if n["data"].get("compound")]
    assert len(parents) == 1
    assert parents[0]["data"]["id"] == "cluster_row_0_A"
    us_nodes = [n for n in out["nodes"] if n["data"]["id"].startswith("us_")]
    assert all(n["data"]["parent"] == "cluster_row_0_A" for n in us_nodes)


def test_to_cytoscape_distinct_sub_groups_create_distinct_parents():
    g = _graph_with_two_us(group_by="area")
    g.nodes[0].sub_group = "A1"
    g.nodes[1].sub_group = "A2"
    out = to_cytoscape(g)
    parents = [n for n in out["nodes"] if n["data"].get("compound")]
    parent_ids = sorted([p["data"]["id"] for p in parents])
    assert parent_ids == ["cluster_row_0_A1", "cluster_row_0_A2"]


def test_to_cytoscape_rows_preserved():
    out = to_cytoscape(_graph_with_two_us())
    assert len(out["rows"]) == 1
    r = out["rows"][0]
    assert r["row_id"] == "row_0"
    assert r["label"] == "I/a"
    assert r["periodo"] == "I"
    assert r["fase"] == "a"
    assert r["is_fallback"] is False
