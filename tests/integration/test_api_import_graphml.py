import io
from pathlib import Path
import pytest
from flask import Flask
from sqlalchemy import create_engine, text


_APP_TEMPLATES = (
    Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"
)


SAMPLE_GRAPHML = b"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d7" yfiles.type="nodegraphics"/>
  <key for="edge" id="d13" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="us_1">
      <data key="d7">
        <y:ShapeNode>
          <y:Fill color="#FFFFFF"/>
          <y:BorderStyle color="#9B3333" type="line" width="4.0"/>
          <y:NodeLabel>10</y:NodeLabel>
          <y:Shape type="rectangle"/>
        </y:ShapeNode>
      </data>
    </node>
    <node id="us_2">
      <data key="d7">
        <y:ShapeNode>
          <y:Fill color="#FFFFFF"/>
          <y:BorderStyle color="#9B3333" type="line" width="4.0"/>
          <y:NodeLabel>20</y:NodeLabel>
          <y:Shape type="rectangle"/>
        </y:ShapeNode>
      </data>
    </node>
    <edge id="e1" source="us_1" target="us_2">
      <data key="d13">
        <y:PolyLineEdge>
          <y:EdgeLabel>overlies</y:EdgeLabel>
        </y:PolyLineEdge>
      </data>
    </edge>
  </graph>
</graphml>"""


@pytest.fixture
def app_and_engine(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/imp.db"
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
    app.config["WTF_CSRF_ENABLED"] = False  # bypass CSRF for tests
    app.register_blueprint(harris_creator_bp)
    return app.test_client(), engine


def test_import_graphml_creates_us(app_and_engine):
    client, engine = app_and_engine
    r = client.post(
        "/harris-creator/api/import/S/graphml",
        data={"file": (io.BytesIO(SAMPLE_GRAPHML), "test.graphml")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200, r.data[:500]
    body = r.get_json()
    assert body["imported_us"] == 2
    assert body["imported_edges"] == 1
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT us FROM us_table ORDER BY us")).fetchall()
        assert rows == [("10",), ("20",)]


def test_import_graphml_writes_4tuple_rapporti_with_inverses(app_and_engine):
    client, engine = app_and_engine
    client.post(
        "/harris-creator/api/import/S/graphml",
        data={"file": (io.BytesIO(SAMPLE_GRAPHML), "test.graphml")},
        content_type="multipart/form-data",
    )
    with engine.begin() as conn:
        r10 = conn.execute(text("SELECT rapporti FROM us_table WHERE us='10'")).scalar()
        r20 = conn.execute(text("SELECT rapporti FROM us_table WHERE us='20'")).scalar()
        assert "Copre" in (r10 or "")
        assert "Coperto da" in (r20 or "")


def test_import_no_file_returns_400(app_and_engine):
    client, _ = app_and_engine
    r = client.post("/harris-creator/api/import/S/graphml", content_type="multipart/form-data")
    assert r.status_code == 400
