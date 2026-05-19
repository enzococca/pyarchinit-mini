from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"
DB_FIX = Path(__file__).parent.parent / "fixtures" / "databases" / "sqlite_volterra_30us_with_periods.db"


@pytest.fixture(autouse=True)
def legacy_pipeline(monkeypatch):
    """Force legacy pipeline: Volterra fixture has old-format rapporti strings
    that the s3dgraphy pipeline cannot parse, so tests expecting 35 nodes/edges
    must run through the legacy code path."""
    monkeypatch.setenv("SWIMLANE_PIPELINE", "legacy")


@pytest.fixture
def client():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX_VOCAB)

    from flask import Flask, g
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp

    eng = create_engine(f"sqlite:///{DB_FIX}")
    Session = sessionmaker(bind=eng)

    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.before_request
    def _attach():
        g.db_session = Session()

    @app.teardown_request
    def _detach(exc):
        try:
            g.db_session.close()
        except Exception:
            pass

    app.register_blueprint(harris_creator_bp)

    yield app.test_client()
    VocabProvider.reset()


def test_get_swimlanes_returns_rows_json(client):
    r = client.get("/harris-creator/api/swimlanes/Volterra")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert len(data) == 5
    for row in data:
        assert "row_id" in row
        assert "period_name" in row
        assert "color" in row


def test_get_load_returns_editor_state(client):
    r = client.get("/harris-creator/api/load/Volterra")
    assert r.status_code == 200
    data = r.get_json()
    assert "rows" in data
    assert "nodes" in data
    assert "edges" in data
    assert len(data["rows"]) == 5
    # 30 US + 5 swimlane parents = 35 nodes
    assert len(data["nodes"]) == 35


def test_get_load_empty_site(client):
    r = client.get("/harris-creator/api/load/UnknownSite")
    assert r.status_code == 200
    data = r.get_json()
    # Fix 2 (review): empty site still returns period_table rows + swimlane
    # parent nodes so the user can drag-create US into them.
    assert data["edges"] == []
    us_nodes = [n for n in data["nodes"] if not n["data"].get("is_swimlane")]
    assert us_nodes == []  # no US for unknown site
    # swimlane parents may be present (cross-site period_table); that's intentional
