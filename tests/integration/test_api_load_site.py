import json
from pathlib import Path
import pytest
from flask import Flask
from sqlalchemy import create_engine, text


_APP_TEMPLATES = (
    Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/api.db"
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("SWIMLANE_PIPELINE", "s3dgraphy")
    engine = create_engine(db_url)
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE)"""))
        conn.execute(text("""CREATE TABLE period_table (id_period INTEGER PRIMARY KEY, sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE periodizzazione_table (id_periodizzazione INTEGER PRIMARY KEY, sito TEXT, periodo_iniziale INTEGER, fase_iniziale INTEGER, periodo_finale INTEGER, fase_finale INTEGER, cronologia_iniziale TEXT, cronologia_finale TEXT, descrizione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
            unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT, rapporti TEXT,
            UNIQUE(sito, area, us))"""))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
            "VALUES ('S','A','1','USM','[[\"Copre\",\"2\",\"A\",\"S\"]]')"
        ))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S','A','2','USM')"
        ))
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "t"
    app.register_blueprint(harris_creator_bp)
    return app.test_client()


def test_api_load_returns_palette_styled_nodes(client):
    r = client.get("/harris-creator/api/load/S")
    assert r.status_code == 200, r.data[:300]
    body = r.get_json()
    assert "nodes" in body and "edges" in body
    assert len(body["nodes"]) >= 2
    node = body["nodes"][0]
    assert "style" in node
    assert isinstance(node["style"], dict)
    assert "shape" in node["style"]
    assert "backgroundColor" in node["style"]


def test_api_load_emits_edges_with_style(client):
    r = client.get("/harris-creator/api/load/S")
    assert r.status_code == 200
    body = r.get_json()
    assert len(body["edges"]) >= 1
    e = body["edges"][0]
    # Edge labels are italianized for the swimlane UI (locale=it); canonical kept in data.canonical
    assert e["data"]["label"] in {"Copre", "Coperto da"}
    assert e["data"]["canonical"] in {"overlies", "is_after"}
    assert "style" in e
    assert isinstance(e["style"], dict)
    assert "lineColor" in e["style"]


def test_api_load_with_group_by_area_yields_compound_parents(client):
    r = client.get("/harris-creator/api/load/S?group_by=area")
    assert r.status_code == 200
    body = r.get_json()
    parents = [n for n in body["nodes"] if n["data"].get("compound")]
    assert len(parents) >= 1


def test_api_load_unknown_site_returns_empty(client):
    r = client.get("/harris-creator/api/load/NoSuchSite")
    assert r.status_code == 200
    body = r.get_json()
    assert body["nodes"] == []
    assert body["edges"] == []
