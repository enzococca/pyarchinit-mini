"""Integration tests for /api/export/<site>/yed-graphml.

The route now streams a palette-based GraphML response directly (no file on
disk, no _index.json). These tests verify the new streaming behaviour using
the Volterra fixture database.
"""
import xml.etree.ElementTree as ET
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
    assert r.status_code == 200, r.data[:400]
    assert "xml" in r.headers.get("Content-Type", "").lower()
    body = r.data.decode("utf-8", errors="ignore")
    assert "<graphml" in body


def test_get_export_graphml_is_valid_xml(client):
    cli, _ = client
    r = cli.get("/harris-creator/api/export/Volterra/yed-graphml")
    assert r.status_code == 200, r.data[:400]
    # Must be parseable XML
    root = ET.fromstring(r.data)
    assert root.tag.endswith("graphml")


def test_get_export_graphml_contains_site_nodes(client):
    cli, _ = client
    r = cli.get("/harris-creator/api/export/Volterra/yed-graphml")
    assert r.status_code == 200, r.data[:400]
    body = r.data.decode("utf-8", errors="ignore")
    # Volterra fixture has US nodes — their IDs appear as us_<id>
    assert "us_" in body


def test_get_export_graphml_contains_palette_usm(client):
    cli, _ = client
    r = cli.get("/harris-creator/api/export/Volterra/yed-graphml")
    assert r.status_code == 200, r.data[:400]
    body = r.data.decode("utf-8", errors="ignore")
    # Palette template carries USM node definitions
    assert "USM" in body or "yfiles" in body


def test_get_export_no_file_on_disk(client):
    """New implementation streams directly — no file written to disk."""
    cli, tmp_path = client
    cli.get("/harris-creator/api/export/Volterra/yed-graphml")
    out_path = tmp_path / "data" / "exports" / "harris_yed" / "volterra-extmatrix.graphml"
    assert not out_path.exists(), "New implementation must not write files to disk"
