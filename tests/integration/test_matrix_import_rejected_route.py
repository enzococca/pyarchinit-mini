"""Test the rejected.html path: AI says is_harris_matrix=false."""
import io
import json
from pathlib import Path
import pytest

from flask import Flask
from pyarchinit_mini.web_interface.matrix_import_routes import matrix_import_bp


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"


@pytest.fixture
def client(tmp_path, monkeypatch):
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(f"sqlite:///{tmp_path}/r.db")
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE site_table (
                id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT UNIQUE, descrizione TEXT,
                created_at DATETIME, updated_at DATETIME)
        """))
    Session = sessionmaker(bind=engine)
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"
    app.jinja_env.globals.setdefault("_", lambda s: s)
    app.jinja_env.globals.setdefault("get_locale", lambda: "it")
    app.jinja_env.globals.setdefault("csrf_token", lambda: "test")
    @app.before_request
    def _s():
        from flask import g
        g.db_session = Session()
    app.register_blueprint(matrix_import_bp)
    yield app.test_client()


def test_rejected_renders_when_ai_says_not_a_matrix(client, monkeypatch):
    fake_payload = json.dumps({
        "is_harris_matrix": False, "confidence": 0.2,
        "reason": "Foto di un muro romano, non un diagramma stratigrafico",
        "detected_site": None, "detected_area": None, "us": [], "edges": [],
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
            "image": (io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"x" * 100), "wall.png"),
            "provider": "anthropic",
        },
        content_type="multipart/form-data",
    )
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "muro romano" in body
    assert "non riconosciuta" in body.lower() or "rejected" in body.lower() or "matrix" in body.lower()
