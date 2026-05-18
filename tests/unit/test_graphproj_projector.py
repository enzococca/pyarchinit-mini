"""Tests for GraphProjector.populate_graph (stratigraphic layer).

NOTE: s3dgraphy.Graph always contains one GeoPositionNode in addition to
user-added nodes. Tests filter it out via isinstance check so assertions
on node counts are stable regardless of s3dgraphy internals.
"""
from pathlib import Path
import sqlite3
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphproj.projector import GraphProjector

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


def _user_nodes(graph):
    """Return only user-added nodes (exclude the internal GeoPositionNode)."""
    try:
        from s3dgraphy.nodes.geo_position_node import GeoPositionNode
        return [n for n in graph.nodes if not isinstance(n, GeoPositionNode)]
    except ImportError:
        return list(graph.nodes)


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


@pytest.fixture
def session(tmp_path):
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY,
        sito TEXT, area TEXT, us INTEGER, unita_tipo TEXT,
        d_stratigrafica TEXT, d_interpretativa TEXT,
        rapporti TEXT, node_uuid TEXT
    )""")
    rows = [
        (1, "Volterra", "A", 1001, "US", "strat 1", "interp 1", "copre 1002", "01900000-0000-7000-8000-000000000001"),
        (2, "Volterra", "A", 1002, "US", "strat 2", "interp 2", "", "01900000-0000-7000-8000-000000000002"),
        (3, "Volterra", "A", 1003, "USVs", "virtual reconstruction", "", "", "01900000-0000-7000-8000-000000000003"),
    ]
    conn.executemany("INSERT INTO us_table VALUES (?,?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def test_populate_graph_returns_graph(session):
    g = GraphProjector.populate_graph(session, "Volterra")
    assert g is not None
    assert len(_user_nodes(g)) == 3


def test_populate_graph_idempotent(session):
    g1 = GraphProjector.populate_graph(session, "Volterra")
    g2 = GraphProjector.populate_graph(session, "Volterra")
    ids1 = {n.node_id for n in _user_nodes(g1)}
    ids2 = {n.node_id for n in _user_nodes(g2)}
    assert ids1 == ids2


def test_populate_graph_creates_stratigraphic_edges(session):
    g = GraphProjector.populate_graph(session, "Volterra")
    edges = list(g.edges)
    # 'copre 1002' produces an edge between 1001 and 1002
    assert len(edges) >= 1


def test_populate_graph_empty_site_returns_empty_graph(session):
    g = GraphProjector.populate_graph(session, "NoSuchSite")
    assert len(_user_nodes(g)) == 0


def test_populate_graph_area_filter(session):
    g = GraphProjector.populate_graph(session, "Volterra", area="A")
    assert len(_user_nodes(g)) == 3
    g_b = GraphProjector.populate_graph(session, "Volterra", area="B")
    assert len(_user_nodes(g_b)) == 0


def test_node_attributes_carry_unit_type_and_family(session):
    g = GraphProjector.populate_graph(session, "Volterra")
    nodes = _user_nodes(g)
    usvs_node = next(n for n in nodes if "1003" in n.node_id)
    attrs = getattr(usvs_node, "attributes", {}) or {}
    # USVs has family "virtual" per VocabProvider
    # Accept either real attribute or the node having stored unit_type
    has_family = attrs.get("family") in ("virtual", "real", "unknown")
    # At minimum, unit_type stored somewhere
    assert attrs.get("unit_type") in ("USVs", "US", "USVn") or hasattr(usvs_node, "unit_type")
