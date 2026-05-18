"""Integration tests for SwimlaneState.load(group_by=...) — 9 valid values."""
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState

DB_FIX = Path(__file__).parent.parent / "fixtures" / "databases" / "sqlite_volterra_30us_with_periods.db"


@pytest.fixture
def session():
    eng = create_engine(f"sqlite:///{DB_FIX}")
    s = sessionmaker(bind=eng)()
    yield s
    s.close()


def test_default_group_by_is_period_phase(session):
    state = SwimlaneState.load(session, "Volterra")
    assert state.group_by == "period_phase"
    assert len(state.rows) == 5


def test_group_by_period_phase_explicit(session):
    state = SwimlaneState.load(session, "Volterra", group_by="period_phase")
    assert state.group_by == "period_phase"
    assert len(state.rows) == 5


def test_group_by_none_returns_single_lane(session):
    state = SwimlaneState.load(session, "Volterra", group_by="none")
    assert state.group_by == "none"
    assert len(state.rows) == 1
    assert state.rows[0].row_id == "row_default"


def test_group_by_invalid_raises(session):
    with pytest.raises(ValueError, match="invalid group_by"):
        SwimlaneState.load(session, "Volterra", group_by="not_a_valid_value")


@pytest.mark.parametrize("gb", ["struttura", "attivita", "settore", "area", "ambient", "saggio", "quad_par"])
def test_group_by_distinct_field_runs(session, gb):
    state = SwimlaneState.load(session, "Volterra", group_by=gb)
    assert state.group_by == gb
    # Fixture has no values in these columns → 1 lane "(missing)"
    assert len(state.rows) >= 1


def test_harris_positions_within_lanes(session):
    state = SwimlaneState.load(session, "Volterra")
    # Nodes within the same lane must have ascending y when there is an
    # edge between them (older below newer).
    by_id = {n.data["id"]: n for n in state.nodes if not n.data.get("is_swimlane")}
    for e in state.edges:
        if e.data.get("label") != "overlies":
            continue
        src = by_id.get(e.data["source"])
        tgt = by_id.get(e.data["target"])
        if not src or not tgt:
            continue
        if src.data.get("parent") != tgt.data.get("parent"):
            continue
        # source overlies target → source must be above target (smaller y).
        assert src.position["y"] <= tgt.position["y"], (
            f"{src.data['id']} should be above {tgt.data['id']}"
        )


def test_api_load_accepts_group_by(tmp_path, monkeypatch):
    from flask import Flask
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp

    db_path = str(DB_FIX)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(harris_creator_bp)
    cli = app.test_client()

    r = cli.get("/harris-creator/api/load/Volterra?group_by=none")
    assert r.status_code == 200, r.get_data(as_text=True)
    body = r.get_json()
    assert body["group_by"] == "none"
    assert len(body["rows"]) == 1


def test_api_export_yed_with_group_by(tmp_path, monkeypatch):
    from flask import Flask
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{DB_FIX}")
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(harris_creator_bp)
    cli = app.test_client()

    r = cli.get("/harris-creator/api/export/Volterra/yed-graphml?group_by=none")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "YED_TABLE_NODE" in body
    assert '<y:Row id="row_default"' in body
