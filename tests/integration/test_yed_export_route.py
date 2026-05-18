import sqlite3
import json
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"
DB_FIX = Path(__file__).parent.parent / "fixtures" / "databases" / "sqlite_volterra_30us_with_periods.db"


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
    yield app.test_client(), tmp_path
    VocabProvider.reset()


def test_get_export_returns_graphml_download(client):
    cli, tmp_path = client
    r = cli.get("/harris-creator/api/export/Volterra/yed-graphml")
    assert r.status_code == 200
    assert "xml" in r.headers.get("Content-Type", "").lower()
    body = r.data.decode("utf-8", errors="ignore")
    assert "<graphml" in body
    assert "y:TableNode" in body or "y:Table" in body

    out_path = tmp_path / "data" / "exports" / "harris_yed" / "volterra-harris-yed.graphml"
    assert out_path.exists()


def test_get_export_updates_index_json(client):
    cli, tmp_path = client
    cli.get("/harris-creator/api/export/Volterra/yed-graphml")
    idx = tmp_path / "data" / "exports" / "harris_yed" / "_index.json"
    assert idx.exists()
    data = json.loads(idx.read_text())
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["site"] == "Volterra"
