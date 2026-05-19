"""Integration tests for the SWIMLANE_PIPELINE feature flag dispatcher."""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState


@pytest.fixture
def session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/p.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY, sito TEXT)"""))
        conn.execute(text("""CREATE TABLE period_table (
            id_period INTEGER PRIMARY KEY, sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE periodizzazione_table (
            id_periodizzazione INTEGER PRIMARY KEY, sito TEXT,
            periodo_iniziale TEXT, fase_iniziale TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
            unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT, rapporti TEXT,
            node_uuid TEXT, periodo_iniziale TEXT, d_stratigrafica TEXT,
            datazione TEXT, file_path TEXT, ambient TEXT, saggio TEXT, quad_par TEXT)"""))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
            "VALUES ('S','A','1','USM','[[\"Copre\",\"2\",\"A\",\"S\"]]')"
        ))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S','A','2','USM')"
        ))
    return sessionmaker(bind=engine)()


def test_s3dgraphy_pipeline_returns_edges(session, monkeypatch):
    monkeypatch.setenv("SWIMLANE_PIPELINE", "s3dgraphy")
    state = SwimlaneState.load(session, "S", group_by="none")
    assert len(state.edges) == 1


def test_s3dgraphy_pipeline_returns_nodes(session, monkeypatch):
    monkeypatch.setenv("SWIMLANE_PIPELINE", "s3dgraphy")
    state = SwimlaneState.load(session, "S", group_by="none")
    # We should have 2 US nodes
    us_nodes = [n for n in state.nodes if "us_" in str(getattr(n, "data", {}).get("id", ""))]
    assert len(us_nodes) >= 2


def test_legacy_pipeline_does_not_error(session, monkeypatch):
    monkeypatch.setenv("SWIMLANE_PIPELINE", "legacy")
    # Legacy needs group_by="period_phase" or similar from its registry; just check it doesn't crash
    state = SwimlaneState.load(session, "S", group_by="period_phase")
    assert state is not None


def test_s3dgraphy_falls_back_to_legacy_on_exception(session, monkeypatch):
    """If S3DProjector raises, the loader should fall back without crashing."""
    monkeypatch.setenv("SWIMLANE_PIPELINE", "s3dgraphy")
    # Patch S3DProjector to raise
    import pyarchinit_mini.graphproj.s3d_projector as sp
    original = sp.S3DProjector.from_site
    def boom(*a, **kw):
        raise RuntimeError("forced failure")
    monkeypatch.setattr(sp.S3DProjector, "from_site", staticmethod(boom))
    # Should not raise — falls back to legacy
    state = SwimlaneState.load(session, "S", group_by="period_phase")
    assert state is not None
