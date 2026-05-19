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
    """US nodes carry flat palette fields in data (Fix B); no nested style dict."""
    r = client.get("/harris-creator/api/load/S")
    assert r.status_code == 200, r.data[:300]
    body = r.get_json()
    assert "nodes" in body and "edges" in body
    # Period row compound + 2 US nodes = at least 3 total
    us_nodes = [n for n in body["nodes"] if n["data"].get("us")]
    assert len(us_nodes) >= 2
    node = us_nodes[0]
    # Flat palette keys in data (Fix B)
    assert "shape" in node["data"], f"Expected flat 'shape' in data, got keys: {list(node['data'].keys())}"
    assert "bgcolor" in node["data"]
    assert node["data"]["bgcolor"].startswith("#")
    # No nested style dict
    assert "style" not in node, "flat-field contract: no nested 'style' key on node"


def test_api_load_emits_edges_with_flat_fields(client):
    """Edges carry flat palette fields in data (Fix B); direction normalized to forward."""
    r = client.get("/harris-creator/api/load/S")
    assert r.status_code == 200
    body = r.get_json()
    assert len(body["edges"]) >= 1
    e = body["edges"][0]
    # After Fix A, only forward canonicals: 'Copre' / 'overlies'
    assert e["data"]["label"] == "Copre", f"Expected 'Copre', got {e['data']['label']!r}"
    assert e["data"]["canonical"] == "overlies", f"Expected 'overlies', got {e['data']['canonical']!r}"
    # Flat palette keys in data (Fix B)
    assert "linecolor" in e["data"], f"Expected flat 'linecolor' in data, got keys: {list(e['data'].keys())}"
    assert "arrowtarget" in e["data"]
    # No nested style dict
    assert "style" not in e, "flat-field contract: no nested 'style' key on edge"


def test_api_load_with_group_by_area_yields_compound_parents(client):
    """Period row + sub-cluster compounds present when group_by=area (Fix C/D)."""
    r = client.get("/harris-creator/api/load/S?group_by=area")
    assert r.status_code == 200
    body = r.get_json()
    # At minimum: 1 period-row compound always present (Fix C)
    period_rows = [n for n in body["nodes"] if n["data"].get("is_period_row")]
    assert len(period_rows) >= 1
    # With group_by=area and US in area 'A', also a sub-cluster compound
    all_compounds = [n for n in body["nodes"] if n["data"].get("compound")]
    assert len(all_compounds) >= 1


def test_api_load_unknown_site_returns_empty(client):
    r = client.get("/harris-creator/api/load/NoSuchSite")
    assert r.status_code == 200
    body = r.get_json()
    assert body["nodes"] == []
    assert body["edges"] == []
