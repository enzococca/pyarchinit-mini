from pathlib import Path
import sqlite3
import pytest

import s3dgraphy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphproj.ingestor import GraphIngestor
from pyarchinit_mini.graphproj.ingest_plan import IngestPlan

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
