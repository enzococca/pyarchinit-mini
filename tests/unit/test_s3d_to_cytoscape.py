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


# ── Fix B: flat palette fields instead of nested style dict ─────────────────

def test_to_cytoscape_node_has_flat_palette_fields():
    """US nodes expose shape/bgcolor/bordercolor as flat data keys (Fix B)."""
    out = to_cytoscape(_graph_with_two_us())
    us_nodes = [n for n in out["nodes"] if n["data"].get("us")]
    assert len(us_nodes) == 2
    usm = next(n for n in us_nodes if n["data"]["id"] == "us_1")
    data = usm["data"]
    assert "shape" in data, "shape must be flat data key"
    assert "bgcolor" in data, "bgcolor must be flat data key"
    assert "bordercolor" in data, "bordercolor must be flat data key"
    assert data["bgcolor"].startswith("#"), f"bgcolor should be a hex colour, got {data['bgcolor']!r}"
    assert data["label"] == "1"
    # No nested style dict
    assert "style" not in usm, "flat-field contract: no nested 'style' key on node"


def test_to_cytoscape_edge_has_flat_palette_fields():
    """Edges expose linecolor/linewidth/arrowtarget as flat data keys (Fix B)."""
    out = to_cytoscape(_graph_with_two_us())
    assert len(out["edges"]) == 1
    e = out["edges"][0]
    data = e["data"]
    assert "linecolor" in data, "linecolor must be flat data key"
    assert "arrowtarget" in data, "arrowtarget must be flat data key"
    assert data["label"] == "Copre"
    assert data["canonical"] == "overlies"
    assert data["source"] == "us_1"
    assert data["target"] == "us_2"
    # No nested style dict
    assert "style" not in e, "flat-field contract: no nested 'style' key on edge"


# ── Fix C: period rows always emitted as compound parents ────────────────────

def test_to_cytoscape_period_row_always_emitted():
    """Period row compound parent always present even with group_by=none (Fix C)."""
    out = to_cytoscape(_graph_with_two_us())
    period_rows = [n for n in out["nodes"] if n["data"].get("is_period_row")]
    assert len(period_rows) == 1
    assert period_rows[0]["data"]["id"] == "row_0"
    assert period_rows[0]["data"]["compound"] is True


def test_to_cytoscape_us_nodes_have_parent_row():
    """Every US node has data.parent = row_id (Fix C)."""
    out = to_cytoscape(_graph_with_two_us())
    us_nodes = [n for n in out["nodes"] if n["data"].get("us")]
    assert all(n["data"].get("parent") == "row_0" for n in us_nodes), (
        "All US nodes must reference their period row as parent"
    )


# ── Fix D: sub-group clusters nested inside period rows ─────────────────────

def test_to_cytoscape_with_sub_group_creates_compound_parents():
    g = _graph_with_two_us(group_by="area")
    for n in g.nodes:
        n.sub_group = "A"
    out = to_cytoscape(g)
    # Sub-cluster compounds (compound=True, is_period_row falsy)
    sub_clusters = [n for n in out["nodes"] if n["data"].get("compound") and not n["data"].get("is_period_row")]
    assert len(sub_clusters) == 1
    cluster = sub_clusters[0]
    assert cluster["data"]["id"] == "cluster_row_0_A"
    # Cluster must be nested inside the period row
    assert cluster["data"].get("parent") == "row_0"
    # US nodes parent is the cluster
    us_nodes = [n for n in out["nodes"] if n["data"].get("us")]
    assert all(n["data"]["parent"] == "cluster_row_0_A" for n in us_nodes)


def test_to_cytoscape_distinct_sub_groups_create_distinct_parents():
    g = _graph_with_two_us(group_by="area")
    g.nodes[0].sub_group = "A1"
    g.nodes[1].sub_group = "A2"
    out = to_cytoscape(g)
    sub_clusters = [n for n in out["nodes"] if n["data"].get("compound") and not n["data"].get("is_period_row")]
    parent_ids = sorted([p["data"]["id"] for p in sub_clusters])
    assert parent_ids == ["cluster_row_0_A1", "cluster_row_0_A2"]


# ── Arrow target: directional vs symmetric ───────────────────────────────────

def test_to_cytoscape_arrowtarget_for_directional():
    """Directional edge (overlies) gets a real arrow target; symmetric gets 'none' (Fix B)."""
    out = to_cytoscape(_graph_with_two_us())
    e = out["edges"][0]
    assert e["data"]["arrowtarget"] != "none", (
        f"overlies edge should have an arrow target, got {e['data']['arrowtarget']!r}"
    )


def test_to_cytoscape_arrowtarget_none_for_symmetric():
    """has_same_time edges get arrowtarget='none' (Fix B)."""
    g = _graph_with_two_us()
    g.edges = [Edge(source_id="us_1", target_id="us_2", canonical="has_same_time")]
    out = to_cytoscape(g)
    e = out["edges"][0]
    assert e["data"]["arrowtarget"] == "none"


# ── Rows preserved ───────────────────────────────────────────────────────────

def test_to_cytoscape_rows_preserved():
    out = to_cytoscape(_graph_with_two_us())
    assert len(out["rows"]) == 1
    r = out["rows"][0]
    assert r["row_id"] == "row_0"
    assert r["label"] == "I/a"
    assert r["periodo"] == "I"
    assert r["fase"] == "a"
    assert r["is_fallback"] is False
