import xml.etree.ElementTree as ET
from pathlib import Path
import pytest
from flask import Flask
from sqlalchemy import create_engine, text


_APP_TEMPLATES = (
    Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/exp.db"
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
        conn.execute(text("INSERT INTO us_table (sito,area,us,unita_tipo,rapporti) VALUES ('S','A','1','USM',:r)"), {"r": "[['Copre','2','A','S']]"})
        conn.execute(text("INSERT INTO us_table (sito,area,us,unita_tipo) VALUES ('S','A','2','USM')"))
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "t"
    app.register_blueprint(harris_creator_bp)
    return app.test_client()


def test_export_graphml_returns_xml(client):
    r = client.get("/harris-creator/api/export/S/yed-graphml")
    assert r.status_code == 200, r.data[:300]
    # parse as XML
    root = ET.fromstring(r.data)
    assert root.tag.endswith("graphml") or root.tag == "{http://graphml.graphdrawing.org/xmlns}graphml"


def test_export_graphml_includes_site_nodes(client):
    r = client.get("/harris-creator/api/export/S/yed-graphml")
    body = r.data.decode("utf-8")
    # The site's US numbers should appear in the exported graphml
    assert ">1<" in body or "us_" in body
    assert ">2<" in body or "us_" in body


def test_export_graphml_includes_palette_template(client):
    r = client.get("/harris-creator/api/export/S/yed-graphml")
    body = r.data.decode("utf-8")
    # Now produces TableNode swimlane format; yfiles namespace must be present
    assert "yfiles" in body


def test_export_graphml_has_tablenode_with_rows(client):
    r = client.get("/harris-creator/api/export/S/yed-graphml")
    body = r.data.decode("utf-8")
    assert "TableNode" in body, "Expected <y:TableNode> wrapper"
    assert 'yfiles.foldertype="group"' in body, "Expected group node with foldertype=group"
    # at least one row inside the table
    assert "<y:Row " in body or "<y:Rows" in body


def test_export_graphml_edge_labels_italianized(client):
    body = client.get("/harris-creator/api/export/S/yed-graphml").data.decode("utf-8")
    # When we have an edge, its label should be "Copre" (italian), not "overlies"
    if "EdgeLabel" in body:
        import re
        labels = re.findall(r'<y:EdgeLabel[^>]*>([^<]+)</y:EdgeLabel>', body)
        for lbl in labels:
            assert lbl.strip() not in {
                "overlies", "is_after", "cuts", "is_cut_by",
                "fills", "is_filled_by", "abuts",
                "is_abutted_by", "is_bonded_to",
                "has_same_time", "is_before",
            }, f"Edge label still in canonical form: {lbl!r}"
