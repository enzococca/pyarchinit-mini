import sqlite3
from pathlib import Path
from unittest.mock import patch
import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX_VOCAB)
    yield
    VocabProvider.reset()


@pytest.fixture
def session(tmp_path):
    db = tmp_path / "save.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
    CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, area TEXT, us INTEGER, unita_tipo TEXT,
        d_stratigrafica TEXT, d_interpretativa TEXT, rapporti TEXT,
        node_uuid TEXT, periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT
    );
    INSERT INTO us_table (sito, area, us, unita_tipo, node_uuid, periodo_iniziale, fase_iniziale)
    VALUES ('Volterra', 'A', 1001, 'US', 'u-1', 'Roman', 'a');
    INSERT INTO us_table (sito, area, us, unita_tipo, node_uuid, periodo_iniziale, fase_iniziale)
    VALUES ('Volterra', 'A', 1002, 'US', 'u-2', 'Medieval', 'a');
    """)
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def test_save_updates_us_periodo(session):
    state = {
        "pending_us_updates": [
            {"us": 1001, "periodo_iniziale": "Medieval", "fase_iniziale": "b"},
        ],
        "pending_us_inserts": [],
        "pending_us_deletes": [],
    }
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen"):
        result = SwimlaneState.save(session, "Volterra", state)
    assert result.updated == 1
    row = session.execute(text(
        "SELECT periodo_iniziale, fase_iniziale FROM us_table WHERE us=1001"
    )).fetchone()
    assert row[0] == "Medieval"
    assert row[1] == "b"


def test_save_inserts_new_us(session):
    state = {
        "pending_us_updates": [],
        "pending_us_inserts": [
            {"sito": "Volterra", "area": "A", "us": 1003, "unita_tipo": "US",
             "periodo_iniziale": "Roman", "fase_iniziale": "b"},
        ],
        "pending_us_deletes": [],
    }
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen"):
        result = SwimlaneState.save(session, "Volterra", state)
    assert result.inserted == 1
    count = session.execute(text(
        "SELECT COUNT(*) FROM us_table WHERE us=1003"
    )).scalar()
    assert count == 1


def test_save_deletes_us(session):
    state = {
        "pending_us_updates": [],
        "pending_us_inserts": [],
        "pending_us_deletes": [{"us": 1001}],
    }
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen"):
        result = SwimlaneState.save(session, "Volterra", state)
    assert result.deleted == 1
    count = session.execute(text(
        "SELECT COUNT(*) FROM us_table WHERE us=1001"
    )).scalar()
    assert count == 0


def test_save_triggers_auto_regen(session):
    state = {
        "pending_us_updates": [
            {"us": 1001, "periodo_iniziale": "Medieval", "fase_iniziale": "b"},
        ],
        "pending_us_inserts": [],
        "pending_us_deletes": [],
    }
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen") as mock_regen:
        SwimlaneState.save(session, "Volterra", state)
        mock_regen.assert_called_once_with("Volterra", session=session)


def test_save_empty_pending_returns_zero_counts(session):
    state = {
        "pending_us_updates": [],
        "pending_us_inserts": [],
        "pending_us_deletes": [],
    }
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen"):
        result = SwimlaneState.save(session, "Volterra", state)
    assert result.updated == 0
    assert result.inserted == 0
    assert result.deleted == 0
