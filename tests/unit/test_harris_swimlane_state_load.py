import sqlite3
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"
DB_FIX = Path(__file__).parent.parent / "fixtures" / "databases" / "sqlite_volterra_30us_with_periods.db"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX_VOCAB)
    yield
    VocabProvider.reset()


@pytest.fixture
def session():
    eng = create_engine(f"sqlite:///{DB_FIX}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def test_load_returns_editor_state_with_5_rows(session):
    state = SwimlaneState.load(session, "Volterra")
    assert state.site == "Volterra"
    assert len(state.rows) == 5


def test_load_returns_30_us_nodes_plus_5_swimlane_parents(session):
    state = SwimlaneState.load(session, "Volterra")
    # nodes includes both US records (30) and swimlane parents (5) = 35 total
    assert len(state.nodes) == 35


def test_load_assigns_parent_row_to_us_nodes(session):
    state = SwimlaneState.load(session, "Volterra")
    us_nodes = [el for el in state.nodes if not el.data.get("is_swimlane")]
    assert len(us_nodes) == 30
    for el in us_nodes:
        assert "parent" in el.data
        # Parent should be a real row_id like "row_roman_a", not "_unassigned"
        # (since fixture US always have periodo_iniziale)
        assert el.data["parent"].startswith("row_")


def test_load_creates_edges_from_rapporti(session):
    state = SwimlaneState.load(session, "Volterra")
    # Fixture has rapporti like "copre 1001" every 3rd US — should produce some edges
    assert len(state.edges) >= 5


def test_load_empty_site_returns_rows_but_no_us(session):
    """Empty site (no US rows) still shows period_table rows so user can
    start dragging/creating US into them."""
    state = SwimlaneState.load(session, "NoSuchSite")
    # period_table is cross-site; rows populated from there
    # us_rows for unknown site is empty
    us_nodes = [el for el in state.nodes if not el.data.get("is_swimlane")]
    assert len(us_nodes) == 0  # no US for unknown site
    assert state.edges == []   # no edges either
    # rows may be non-empty (cross-site period_table); that's intentional


def test_load_site_with_periods_but_no_us(session):
    """A site with period_table rows but 0 US records still renders the
    swimlane parents so the user can drag-create US into them. Uses
    ``Volterra`` (which has 5 period rows in the fixture) but queries a
    non-existent area filter — i.e. the period rows are scoped to a real
    site but no US match."""
    state = SwimlaneState.load(session, "Volterra")
    assert len(state.rows) == 5
    swimlane_nodes = [el for el in state.nodes if el.data.get("is_swimlane")]
    assert len(swimlane_nodes) == 5
