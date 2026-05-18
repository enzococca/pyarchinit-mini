from pathlib import Path
import sqlite3
import pytest

import s3dgraphy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphproj.ingestor import GraphIngestor
from pyarchinit_mini.graphproj.exceptions import IngestStaleError

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


@pytest.fixture
def session(tmp_path):
    db = tmp_path / "app.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us INTEGER,
        unita_tipo TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        rapporti TEXT, node_uuid TEXT
    )""")
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def _input_graph(nodes):
    g = s3dgraphy.Graph(graph_id="ing", name="ing", description="")
    for us_num, unita_tipo, emid in nodes:
        n = s3dgraphy.Node(f"Volterra_{us_num}", f"{unita_tipo}{us_num}", "")
        if not hasattr(n, "attributes") or n.attributes is None:
            n.attributes = {}
        n.attributes["unit_type"] = unita_tipo
        n.attributes["EMid"] = emid
        g.add_node(n)
    return g


def test_apply_inserts_new_us_rows(session):
    g = _input_graph([(2001, "US", "u-1"), (2002, "US", "u-2")])
    ing = GraphIngestor(session, "Volterra")
    plan = ing.preview(g)
    result = ing.apply(plan)
    assert result.inserted == 2
    assert result.errors == ()
    count = session.execute(text(
        "SELECT COUNT(*) FROM us_table WHERE sito='Volterra'"
    )).scalar()
    assert count == 2


def test_apply_stale_plan_raises(session):
    g = _input_graph([(2001, "US", "u-1")])
    ing = GraphIngestor(session, "Volterra")
    plan = ing.preview(g)
    # Mutate DB so snapshot changes
    session.execute(text(
        "INSERT INTO us_table (sito, us, unita_tipo, node_uuid) "
        "VALUES ('Volterra', 9999, 'US', 'mutator')"
    ))
    session.commit()
    with pytest.raises(IngestStaleError):
        ing.apply(plan)


def test_apply_updates_existing_row(session):
    # Seed DB with an existing row
    session.execute(text(
        "INSERT INTO us_table (sito, us, unita_tipo, node_uuid) "
        "VALUES ('Volterra', 1001, 'US', 'u-1001')"
    ))
    session.commit()

    # Input graph: same UUID, different unita_tipo
    g = _input_graph([(1001, "USVs", "u-1001")])
    ing = GraphIngestor(session, "Volterra")
    plan = ing.preview(g)
    assert len(plan.updates) == 1
    result = ing.apply(plan)
    assert result.updated == 1

    # Verify DB updated
    row = session.execute(text(
        "SELECT unita_tipo FROM us_table WHERE node_uuid='u-1001'"
    )).fetchone()
    assert row[0] == "USVs"


def test_apply_empty_plan_succeeds(session):
    g = s3dgraphy.Graph(graph_id="empty", name="empty", description="")
    ing = GraphIngestor(session, "Volterra")
    plan = ing.preview(g)
    result = ing.apply(plan)
    assert result.inserted == 0
    assert result.updated == 0
    assert result.skipped == 0
