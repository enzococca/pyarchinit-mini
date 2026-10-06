from pathlib import Path
import sqlite3
import pytest

import s3dgraphy
from s3dgraphy.graph import Graph
from s3dgraphy.nodes.base_node import Node
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphproj.ingestor import GraphIngestor
from pyarchinit_mini.graphproj.ingest_plan import IngestPlan
from tests.unit.strat_graph_factory import make_graph

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


@pytest.fixture
def session(tmp_path):
    db = tmp_path / "ing.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us INTEGER,
        unita_tipo TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        rapporti TEXT, node_uuid TEXT
    )""")
    conn.execute(
        "INSERT INTO us_table (sito, us, unita_tipo, node_uuid) "
        "VALUES ('Volterra', 1001, 'US', 'u-1')"
    )
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def _build_input_graph(nodes_data):
    """Helper: build a s3dgraphy graph with given (us, unita_tipo, EMid) tuples."""
    g = s3dgraphy.Graph(graph_id="ing", name="ing", description="")
    for us_num, unita_tipo, emid in nodes_data:
        node_id = f"Volterra_{us_num}"
        n = s3dgraphy.Node(node_id, f"{unita_tipo}{us_num}", "")
        if not hasattr(n, "attributes") or n.attributes is None:
            n.attributes = {}
        n.attributes["unit_type"] = unita_tipo
        n.attributes["EMid"] = emid
        g.add_node(n)
    return g


def test_preview_new_node_classified_as_insert(session):
    g = _build_input_graph([(1002, "US", "u-2")])
    plan = GraphIngestor(session, "Volterra").preview(g)
    assert isinstance(plan, IngestPlan)
    assert len(plan.inserts) == 1
    assert plan.inserts[0].reason == "new"
    assert plan.inserts[0].after["us"] == 1002


def test_preview_existing_node_classified_as_update(session):
    g = _build_input_graph([(1001, "US", "u-1")])
    plan = GraphIngestor(session, "Volterra").preview(g)
    assert len(plan.updates) == 1
    assert plan.updates[0].before is not None
    assert plan.updates[0].before["us"] == 1001


def test_preview_snapshot_revision_set(session):
    g = _build_input_graph([(1002, "US", "u-2")])
    plan = GraphIngestor(session, "Volterra").preview(g)
    assert plan.snapshot_revision != ""
    assert len(plan.snapshot_revision) >= 8  # truncated SHA-256


def test_preview_filters_out_geoposition_or_unknown_nodes(session):
    """Nodes without a derivable us number or unit_type should be skipped silently."""
    g = s3dgraphy.Graph(graph_id="ing", name="ing", description="")
    plan = GraphIngestor(session, "Volterra").preview(g)
    assert len(plan.inserts) == 0
    assert len(plan.updates) == 0


def test_preview_snapshot_changes_when_db_changes(session):
    g = _build_input_graph([(1002, "US", "u-2")])
    plan_a = GraphIngestor(session, "Volterra").preview(g)
    # Mutate DB
    from sqlalchemy import text
    session.execute(text(
        "INSERT INTO us_table (sito, us, unita_tipo, node_uuid) "
        "VALUES ('Volterra', 9999, 'US', 'mutator')"
    ))
    session.commit()
    plan_b = GraphIngestor(session, "Volterra").preview(g)
    assert plan_a.snapshot_revision != plan_b.snapshot_revision


def test_us_number_uses_trailing_digits_when_no_attrs(session):
    g = Graph(graph_id="x")
    n = Node("A1_12", "A1.US12", ""); n.attributes = {"unit_type": "US", "EMid": ""}
    g.add_node(n)
    plan = GraphIngestor(session, "Volterra").preview(g)
    assert [e.after["us"] for e in plan.inserts] == [12]


def test_us_number_prefers_pyarchinit_attrs(session):
    g = make_graph(site="Volterra", nodes=[{"id": "u", "us": "77", "unit_type": "US", "node_uuid": ""}])
    node = next(n for n in g.nodes if n.node_id == "u"); node.name = "A1.US12"
    plan = GraphIngestor(session, "Volterra").preview(g)
    assert [e.after["us"] for e in plan.inserts] == [77]


def test_node_without_digits_or_attrs_is_skipped(session):
    g = Graph(graph_id="x")
    n = Node("nodigits", "US", ""); n.attributes = {"unit_type": "US", "EMid": ""}
    g.add_node(n)
    plan = GraphIngestor(session, "Volterra").preview(g)
    assert not plan.inserts and not plan.updates


def test_non_numeric_attrs_us_falls_back_to_name_digits(session):
    g = make_graph(site="Volterra", nodes=[{"id": "v", "us": "12a", "unit_type": "US", "node_uuid": ""}])
    node = next(n for n in g.nodes if n.node_id == "v"); node.name = "US15"
    plan = GraphIngestor(session, "Volterra").preview(g)
    assert [e.after["us"] for e in plan.inserts] == [15]
