"""Integration tests for /api/export/<site>/heriverse-json."""
import json
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"
DB_FIX = (
    Path(__file__).parent.parent
    / "fixtures"
    / "databases"
    / "sqlite_volterra_30us_with_periods.db"
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX_VOCAB)

    import shutil
    db = tmp_path / "app.db"
    shutil.copy(DB_FIX, db)

    from flask import Flask, g
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp

    eng = create_engine(f"sqlite:///{db}")
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


def test_export_heriverse_returns_valid_json(client):
    r = client.get("/harris-creator/api/export/Volterra/heriverse-json")
    assert r.status_code == 200, r.data[:500]
    data = json.loads(r.data)
    # Top-level Heriverse/CouchDB scene document structure
    assert data.get("wapp") == "heriverse"
    assert "resource_json" in data
    assert "multigraph" in data["resource_json"]


def test_export_heriverse_includes_site_in_graph(client):
    r = client.get("/harris-creator/api/export/Volterra/heriverse-json")
    data = json.loads(r.data)
    mg = data["resource_json"]["multigraph"]
    graphs = mg["graphs"]
    # graphs is a dict keyed by graph ID
    assert isinstance(graphs, dict) and len(graphs) > 0
    first_graph = next(iter(graphs.values()))
    assert isinstance(first_graph.get("name"), str) and len(first_graph["name"]) > 0


def test_export_heriverse_content_disposition(client):
    r = client.get("/harris-creator/api/export/Volterra/heriverse-json")
    assert r.status_code == 200, r.data[:500]
    cd = r.headers.get("Content-Disposition", "")
    assert "attachment" in cd
    assert "heriverse.json" in cd


def test_export_heriverse_content_type(client):
    r = client.get("/harris-creator/api/export/Volterra/heriverse-json")
    assert r.status_code == 200, r.data[:500]
    assert "application/json" in r.headers.get("Content-Type", "")
