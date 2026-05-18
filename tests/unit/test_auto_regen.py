import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphproj.auto_regen import (
    _trigger_graph_regen,
    disable_regen,
    force_regen_all_touched_sites,
    _is_regen_disabled,
    _record_touched_site,
    _drain_touched_sites,
)

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_disable_regen_context_sets_flag():
    assert _is_regen_disabled() is False
    with disable_regen():
        assert _is_regen_disabled() is True
    assert _is_regen_disabled() is False


def test_disable_regen_records_touched_sites():
    with disable_regen():
        _record_touched_site("Volterra")
        _record_touched_site("Pompei")
        _record_touched_site("Volterra")  # dedupe
    drained = _drain_touched_sites()
    assert set(drained) == {"Volterra", "Pompei"}


def test_drain_touched_sites_is_one_shot():
    with disable_regen():
        _record_touched_site("X")
    first = _drain_touched_sites()
    second = _drain_touched_sites()
    assert "X" in first
    assert second == []


def test_trigger_regen_no_op_when_env_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("PYARCHINIT_DISABLE_AUTO_REGEN", "1")
    monkeypatch.chdir(tmp_path)
    session = MagicMock()
    _trigger_graph_regen("Volterra", session=session)
    assert not (tmp_path / "data" / "paradata" / "volterra" / "stratigraphy.graphml").exists()


def test_trigger_regen_catches_errors(tmp_path, monkeypatch):
    """Regen failures must be caught and logged, never propagate."""
    monkeypatch.chdir(tmp_path)
    session = MagicMock()
    with patch(
        "pyarchinit_mini.graphproj.auto_regen.GraphProjector.populate_graph",
        side_effect=RuntimeError("boom"),
    ):
        # Must NOT raise
        _trigger_graph_regen("Volterra", session=session)


def test_regen_failure_writes_cache_when_available(tmp_path, monkeypatch):
    """On regen failure, cache.set is called with regen_status:<site> if cache is present."""
    monkeypatch.chdir(tmp_path)
    session = MagicMock()
    cache = MagicMock()

    mock_app = MagicMock()
    mock_app.config = {"CACHE": cache}

    # current_app is imported inline inside the except block, so patch flask.current_app.
    with patch(
        "pyarchinit_mini.graphproj.auto_regen.GraphProjector.populate_graph",
        side_effect=RuntimeError("boom"),
    ), patch("flask.current_app", mock_app):
        _trigger_graph_regen("Volterra", session=session)

    cache.set.assert_called_once_with(
        "regen_status:Volterra", {"status": "error"}, timeout=86400
    )


def test_regen_failure_no_crash_when_no_flask_context(tmp_path, monkeypatch):
    """On regen failure, silently skips cache write if no Flask context available."""
    monkeypatch.chdir(tmp_path)
    session = MagicMock()

    # Simulate RuntimeError when accessing current_app (no app context).
    import flask

    class _RaisingProxy:
        @property
        def config(self):
            raise RuntimeError("no app context")

    with patch(
        "pyarchinit_mini.graphproj.auto_regen.GraphProjector.populate_graph",
        side_effect=RuntimeError("boom"),
    ), patch("flask.current_app", _RaisingProxy()):
        # Must NOT raise
        _trigger_graph_regen("Volterra", session=session)


def test_regen_failure_no_crash_when_cache_is_none(tmp_path, monkeypatch):
    """On regen failure, silently skips if CACHE config key is absent/None."""
    monkeypatch.chdir(tmp_path)
    session = MagicMock()

    mock_app = MagicMock()
    mock_app.config = {}  # no CACHE key → .get("CACHE") returns None

    with patch(
        "pyarchinit_mini.graphproj.auto_regen.GraphProjector.populate_graph",
        side_effect=RuntimeError("boom"),
    ), patch("flask.current_app", mock_app):
        # Must NOT raise
        _trigger_graph_regen("Volterra", session=session)


def test_trigger_regen_writes_stratigraphy_file(tmp_path, monkeypatch):
    """Happy path: regen produces stratigraphy.graphml under data/paradata/<slug>/."""
    monkeypatch.chdir(tmp_path)
    import sqlite3
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    db = tmp_path / "app.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us INTEGER,
        unita_tipo TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        rapporti TEXT, node_uuid TEXT
    )""")
    conn.execute(
        "INSERT INTO us_table (sito, us, unita_tipo, rapporti, node_uuid) "
        "VALUES ('Volterra', 1001, 'US', '', 'u-1')"
    )
    conn.commit()
    conn.close()

    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()

    _trigger_graph_regen("Volterra", session=s)

    out = tmp_path / "data" / "paradata" / "volterra" / "stratigraphy.graphml"
    assert out.exists(), "stratigraphy.graphml should be written"
    s.close()
