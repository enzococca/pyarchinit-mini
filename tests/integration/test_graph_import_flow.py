import sqlite3
from pathlib import Path
import pytest

import s3dgraphy
from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphml_io.writer import write_graphml

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def client_and_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)

    # DB setup
    db = tmp_path / "app.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us INTEGER,
        unita_tipo TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        rapporti TEXT, node_uuid TEXT
    )""")
    conn.commit()
    conn.close()

    from flask import Flask, g
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker
    from pyarchinit_mini.web_interface.graph_routes import graph_bp

    eng = create_engine(f"sqlite:///{db}")
    Session = scoped_session(sessionmaker(bind=eng))

    app = Flask(
        __name__,
        template_folder=str(
            Path(__file__).parent.parent.parent
            / "pyarchinit_mini" / "web_interface" / "templates"
        ),
    )
    app.config["TESTING"] = True
    app.secret_key = "test"

    @app.before_request
    def _attach_session():
        g.db_session = Session()

    @app.teardown_request
    def _remove_session(exc):
        Session.remove()

    app.register_blueprint(graph_bp)

    yield app.test_client(), tmp_path
    VocabProvider.reset()


def _make_upload_file(tmp_path, nodes):
    g = s3dgraphy.Graph(graph_id="up", name="up", description="")
    for us_num, ut, emid in nodes:
        n = s3dgraphy.Node(f"Volterra_{us_num}", f"{ut}{us_num}", "")
        if not hasattr(n, "attributes") or n.attributes is None:
            n.attributes = {}
        n.attributes["unit_type"] = ut
        n.attributes["EMid"] = emid
        g.add_node(n)
    path = tmp_path / "upload.graphml"
    write_graphml(g, path)
    return path


def test_preview_returns_200_with_inserts(client_and_path):
    cli, tmp_path = client_and_path
    upload = _make_upload_file(tmp_path, [(3001, "US", "u-3001")])
    with upload.open("rb") as f:
        r = cli.post(
            "/sites/Volterra/graph/import-preview",
            data={"file": (f, "upload.graphml")},
            content_type="multipart/form-data",
        )
    assert r.status_code == 200, r.data[:500]
    # Page mentions insert / new
    body = r.data.decode("utf-8", errors="ignore").lower()
    assert "insert" in body or "new" in body


def test_apply_without_plan_returns_404(client_and_path):
    cli, _ = client_and_path
    r = cli.post(
        "/sites/Volterra/graph/import-apply",
        data={"upload_id": "nonexistent"},
    )
    assert r.status_code == 404
