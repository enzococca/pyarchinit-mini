from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    from flask import Flask
    from pyarchinit_mini.web_interface.graph_routes import graph_bp
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test"
    app.register_blueprint(graph_bp)
    yield app.test_client(), tmp_path
    VocabProvider.reset()


def test_download_returns_404_when_no_graph(client):
    cli, _ = client
    r = cli.get("/sites/Volterra/graph/download")
    assert r.status_code == 404


def test_download_serves_file_when_exists(client):
    cli, tmp_path = client
    out_dir = tmp_path / "data" / "paradata" / "volterra"
    out_dir.mkdir(parents=True)
    (out_dir / "stratigraphy.graphml").write_text("<graphml/>", encoding="utf-8")
    r = cli.get("/sites/Volterra/graph/download")
    assert r.status_code == 200
    assert b"<graphml/>" in r.data
    assert "attachment" in r.headers.get("Content-Disposition", "")


def test_view_returns_404_when_no_graph(client):
    cli, _ = client
    r = cli.get("/sites/Volterra/graph/view")
    assert r.status_code == 404


def test_view_serves_xml_when_exists(client):
    cli, tmp_path = client
    out_dir = tmp_path / "data" / "paradata" / "volterra"
    out_dir.mkdir(parents=True)
    (out_dir / "stratigraphy.graphml").write_text("<?xml version='1.0'?><graphml/>", encoding="utf-8")
    r = cli.get("/sites/Volterra/graph/view")
    assert r.status_code == 200
    assert "xml" in r.headers.get("Content-Type", "")
