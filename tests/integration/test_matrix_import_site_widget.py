"""When AI doesn't detect a site and form doesn't set one, preview shows widget."""
import io
import json
from pathlib import Path
import pytest

from flask import Flask
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.web_interface.matrix_import_routes import matrix_import_bp


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path}/w.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (
            id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT UNIQUE, descrizione TEXT,
            created_at DATETIME, updated_at DATETIME)"""))
    Session = sessionmaker(bind=engine)
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "t"
    app.jinja_env.globals.setdefault("_", lambda s: s)
    app.jinja_env.globals.setdefault("get_locale", lambda: "it")
    app.jinja_env.globals.setdefault("csrf_token", lambda: "t")
    @app.before_request
    def _s():
        from flask import g
        g.db_session = Session()
    app.register_blueprint(matrix_import_bp)
    yield app.test_client()


def test_preview_shows_site_widget_when_missing(client, monkeypatch):
    """AI returns plan with detected_site=None and form sito='' → widget visible."""
    fake_payload = json.dumps({
        "is_harris_matrix": True, "confidence": 0.9, "reason": "OK",
        "detected_site": None, "detected_area": None,
        "us": [{"us_num": "1", "area": "A", "unit_type": "US",
                "descrizione": "x", "fase_recente": 1, "fase_iniziale": 1}],
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

    r = client.post("/matrix-import/upload", data={
        "image": (io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"x" * 100), "m.png"),
        "sito": "", "sito_new": "", "area": "", "provider": "anthropic",
    }, content_type="multipart/form-data")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "non rilevato" in body.lower() or "widget" in body.lower() or "manualmente" in body.lower()
