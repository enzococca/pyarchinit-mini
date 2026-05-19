import io
import json
from pathlib import Path
import pytest
from flask import Flask
from sqlalchemy import create_engine, text


_APP_TEMPLATES = (
    Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"
)


SAMPLE_HERIVERSE = json.dumps({
    "wapp": "heriverse",
    "multigraph": {
        "graphs": [{
            "id": "g0",
            "name": "Site_T",
            "nodes": {
                "USM": [{"id": "us_a", "name": "10", "type": "USM"}],
                "USV": [{"id": "us_b", "name": "20", "type": "USV"}],
            },
            "edges": {"line": [{"id": "e1", "from": "us_a", "to": "us_b"}]},
            "semantic_shapes": {}, "representation_models": {}, "panorama_models": {},
        }]
    },
    "couchdb_metadata": {},
}).encode()


@pytest.fixture
def app_and_engine(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/j.db"
    monkeypatch.setenv("DATABASE_URL", db_url)
    engine = create_engine(db_url)
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
            unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT, rapporti TEXT,
            data_origine TEXT, UNIQUE(sito, area, us))"""))
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "t"
    app.config["WTF_CSRF_ENABLED"] = False
    app.register_blueprint(harris_creator_bp)
    return app.test_client(), engine


def test_import_heriverse_json_writes_us(app_and_engine):
    client, engine = app_and_engine
    r = client.post(
        "/harris-creator/api/import/S/json",
        data={"file": (io.BytesIO(SAMPLE_HERIVERSE), "h.json")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200, r.data[:300]
    body = r.get_json()
    assert body["imported_us"] == 2
    assert body["imported_edges"] == 1
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT us, unita_tipo FROM us_table ORDER BY us")).fetchall()
        assert rows == [("10", "USM"), ("20", "USV")]


def test_import_heriverse_overrides_site_to_url_param(app_and_engine):
    """The site in the URL takes precedence over the site name embedded in the JSON."""
    client, engine = app_and_engine
    client.post(
        "/harris-creator/api/import/MySite/json",
        data={"file": (io.BytesIO(SAMPLE_HERIVERSE), "h.json")},
        content_type="multipart/form-data",
    )
    with engine.begin() as conn:
        sitos = conn.execute(text("SELECT DISTINCT sito FROM us_table")).fetchall()
        assert sitos == [("MySite",)]


def test_import_heriverse_no_file_returns_400(app_and_engine):
    client, _ = app_and_engine
    r = client.post("/harris-creator/api/import/S/json", content_type="multipart/form-data")
    assert r.status_code == 400
