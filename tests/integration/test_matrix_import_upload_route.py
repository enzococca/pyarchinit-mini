"""Integration tests for /matrix-import/ endpoints."""
import io
import json
from pathlib import Path
import pytest

from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader

from pyarchinit_mini.web_interface.matrix_import_routes import matrix_import_bp


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"


@pytest.fixture
def client(tmp_path, monkeypatch):
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    db_path = tmp_path / "mi.db"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE site_table (
                id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT UNIQUE NOT NULL,
                descrizione TEXT,
                created_at DATETIME, updated_at DATETIME)
        """))
        conn.execute(text("""
            CREATE TABLE us_table (
                id_us INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
                d_stratigrafica TEXT, fase_recente INT, fase_iniziale INT,
                created_at DATETIME, updated_at DATETIME)
        """))
        conn.execute(text("""
            CREATE TABLE us_relationships_table (
                id_rel INTEGER PRIMARY KEY AUTOINCREMENT,
                sito_from TEXT, sito_to TEXT, us_from INT, us_to INT,
                tipo_relazione TEXT, created_at DATETIME, updated_at DATETIME)
        """))
        conn.execute(text(
            "INSERT INTO site_table (sito, created_at, updated_at) VALUES ('ExistingSite', :n, :n)"
        ), {"n": "2026-01-01"})
    Session = sessionmaker(bind=engine)

    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"
    app.jinja_env.globals.setdefault("_", lambda s: s)
    app.jinja_env.globals.setdefault("get_locale", lambda: "it")
    app.jinja_env.globals.setdefault("csrf_token", lambda: "test-csrf")

    @app.before_request
    def _attach_session():
        from flask import g
        g.db_session = Session()

    app.register_blueprint(matrix_import_bp)
    yield app.test_client()


def test_get_index_renders_with_sites(client):
    r = client.get("/matrix-import/")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "ExistingSite" in body
    assert "matrix" in body.lower() or "AI" in body


def test_upload_renders_preview_on_success(client, monkeypatch):
    """Mocked AI returns valid plan → preview rendered."""
    fake_payload = json.dumps({
        "is_harris_matrix": True, "confidence": 0.9, "reason": "OK",
        "detected_site": "FromImage", "detected_area": None,
        "us": [{"us_num": "1", "area": "A", "unit_type": "USM",
                "descrizione": "muro", "fase_recente": 1, "fase_iniziale": 1}],
        "edges": [],
    })
    class FakeContent:
        def __init__(self, t): self.text = t
    class FakeResp:
        content = [FakeContent(fake_payload)]
    class FakeMessages:
        def create(self, **kw): return FakeResp()
    class FakeClient:
        def __init__(self, **kw): self.messages = FakeMessages()
    import anthropic
    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")

    r = client.post(
        "/matrix-import/upload",
        data={
            "image": (io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"x" * 100), "matrix.png"),
            "descrizione": "",
            "sito": "",
            "area": "",
            "provider": "anthropic",
        },
        content_type="multipart/form-data",
    )
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "FromImage" in body or "muro" in body
    assert "plan_json" in body


def test_upload_missing_file_redirects(client):
    r = client.post(
        "/matrix-import/upload",
        data={"sito": "", "area": "", "provider": "anthropic"},
        content_type="multipart/form-data",
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)


def test_upload_empty_file_filename_redirects(client):
    """Browser submits form without choosing a file — FileStorage with empty filename."""
    import io as _io
    r = client.post(
        "/matrix-import/upload",
        data={
            "image": (_io.BytesIO(b""), ""),  # empty filename — Flask treats as "no file"
            "provider": "anthropic",
        },
        content_type="multipart/form-data",
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)
