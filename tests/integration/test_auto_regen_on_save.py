from pathlib import Path
import sqlite3
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_trigger_graph_regen_produces_stratigraphy_file(tmp_path, monkeypatch):
    """Direct integration test: calling _trigger_graph_regen against a real
    DB session produces stratigraphy.graphml on disk."""
    monkeypatch.chdir(tmp_path)
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    db = tmp_path / "test.db"
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
    session = Session()
    session.execute(text(
        "INSERT INTO us_table (sito, us, unita_tipo, rapporti, node_uuid) "
        "VALUES ('Volterra', 1001, 'US', '', 'uuid-1')"
    ))
    session.commit()

    from pyarchinit_mini.graphproj.auto_regen import _trigger_graph_regen
    _trigger_graph_regen("Volterra", session=session)

    out = tmp_path / "data" / "paradata" / "volterra" / "stratigraphy.graphml"
    assert out.exists(), "stratigraphy.graphml should be created"
    session.close()


def test_regen_failure_does_not_propagate(tmp_path, monkeypatch):
    """Auto-regen failures must never raise to the caller."""
    monkeypatch.chdir(tmp_path)
    from unittest.mock import patch
    from pyarchinit_mini.graphproj.auto_regen import _trigger_graph_regen
    with patch(
        "pyarchinit_mini.graphproj.auto_regen.GraphProjector.populate_graph",
        side_effect=RuntimeError("boom"),
    ):
        _trigger_graph_regen("X", session=None)  # must NOT raise
