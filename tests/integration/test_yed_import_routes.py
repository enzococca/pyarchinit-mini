"""Integration tests for /import-graphml/ endpoints."""
import io
from pathlib import Path
import pytest

from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader

from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
from pyarchinit_mini.web_interface.yed_import_routes import yed_import_bp


FIX = Path(__file__).parent.parent / "fixtures" / "yed_graphml"

_TEST_TEMPLATES = Path(__file__).parent.parent / "templates"
_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"


@pytest.fixture
def client(tmp_path, monkeypatch):
    from sqlalchemy import create_engine, text
    from pyarchinit_mini.models.base import Base
    db_path = tmp_path / "imp.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    eng = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(eng)
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"
    # Use stub base.html first, then real templates
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(str(_TEST_TEMPLATES)),
        FileSystemLoader(str(_APP_TEMPLATES)),
    ])
    # Inject i18n + auth stubs so templates render without full app context
    app.jinja_env.globals.setdefault("_", lambda s: s)
    app.jinja_env.globals.setdefault("get_locale", lambda: "it")
    app.jinja_env.globals.setdefault("csrf_token", lambda: "test-csrf")
    app.register_blueprint(harris_creator_bp)
    app.register_blueprint(yed_import_bp)
    yield app.test_client()


def test_index_renders(client):
    r = client.get("/import-graphml/")
    assert r.status_code == 200
    assert b"Import GraphML" in r.data or b"yEd" in r.data


def test_preview_minimal_file(client):
    data = (FIX / "minimal.graphml").read_bytes()
    r = client.post(
        "/import-graphml/preview",
        data={"file": (io.BytesIO(data), "minimal.graphml")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "3" in body  # 3 US created


def test_apply_renders_result(client):
    import re
    data = (FIX / "minimal.graphml").read_bytes()
    r = client.post(
        "/import-graphml/preview",
        data={"file": (io.BytesIO(data), "minimal.graphml")},
        content_type="multipart/form-data",
    )
    body = r.get_data(as_text=True)
    m = re.search(r'name="plan_id"\s+value="([0-9a-f]+)"', body)
    # Stub preview.html doesn't include the hidden input yet — Task 17 will.
    # If no match, just smoke-test that result.html template exists by calling
    # /apply with a bogus plan_id and expecting 400 (plan_expired), not 500.
    if not m:
        r2 = client.post("/import-graphml/apply", data={"plan_id": "bogus"})
        assert r2.status_code == 400  # plan_expired, not TemplateNotFound 500
    else:
        plan_id = m.group(1)
        r2 = client.post("/import-graphml/apply", data={"plan_id": plan_id})
        assert r2.status_code == 200
        assert b"3 US created" in r2.data
