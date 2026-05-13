"""Integration tests for pottery web routes."""
import os

from flask import Flask
from flask_login import LoginManager, AnonymousUserMixin
from jinja2 import ChoiceLoader, FileSystemLoader
import pytest

from pyarchinit_mini.web_interface.pottery_routes import _register_pottery_routes

# Directory of this test file
_HERE = os.path.dirname(__file__)
# Real app templates
_APP_TEMPLATES = os.path.join(_HERE, "..", "..", "pyarchinit_mini", "web_interface", "templates")
# Test template overrides (minimal base.html to avoid url_for BuildErrors)
_TEST_TEMPLATES = os.path.join(_HERE, "..", "templates")


@pytest.fixture
def flask_app(db_manager):
    """Minimal Flask app for pottery route tests.

    Uses the existing `db_manager` fixture (from tests/conftest.py) which provides
    an isolated SQLite DB with all tables already created.

    The Jinja2 loader checks test overrides first (for a minimal base.html),
    then falls back to the real app templates for pottery/list.html etc.
    """
    app = Flask(
        __name__,
        template_folder=_APP_TEMPLATES,
        static_folder=os.path.join(
            _HERE, "..", "..", "pyarchinit_mini", "web_interface", "static"
        ),
    )
    app.config["TESTING"] = True
    app.config["LOGIN_DISABLED"] = True
    app.config["SECRET_KEY"] = "test-secret"
    app.db_manager = db_manager

    # Override loader: test templates first (minimal base.html), then real templates
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(os.path.abspath(_TEST_TEMPLATES)),
        FileSystemLoader(os.path.abspath(_APP_TEMPLATES)),
    ])

    # Inject dummy i18n helpers the base.html may reference
    app.jinja_env.globals.setdefault("get_locale", lambda: "it")
    app.jinja_env.globals.setdefault("_", lambda s: s)

    # Minimal LoginManager for current_user references in templates
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.anonymous_user = AnonymousUserMixin

    @login_manager.user_loader
    def load_user(user_id):  # noqa: unused-variable
        return None

    # Stub the one route base.html always calls unconditionally (index)
    @app.route("/")
    def index():
        return ""

    _register_pottery_routes(app)
    return app


@pytest.fixture
def client(flask_app):
    return flask_app.test_client()


@pytest.fixture
def pottery_service(db_manager):
    """Re-import here so test runs cleanly even if conftest already provides one."""
    from pyarchinit_mini.services.pottery_service import PotteryService
    return PotteryService(db_manager)


def test_list_page_renders(client, pottery_service):
    pottery_service.create_pottery({"sito": "X", "form": "Olla", "qty": 1})
    r = client.get("/pottery")
    assert r.status_code == 200
    assert b"Pottery" in r.data
    assert b"Olla" in r.data


def test_list_page_filter_by_sito(client, pottery_service):
    pottery_service.create_pottery({"sito": "X", "form": "Olla"})
    pottery_service.create_pottery({"sito": "Y", "form": "Ciotola"})
    r = client.get("/pottery?sito=X")
    assert r.status_code == 200
    assert b"Olla" in r.data
    assert b"Ciotola" not in r.data


def test_create_form_renders(client):
    r = client.get("/pottery/create")
    assert r.status_code == 200
    assert b"Description data" in r.data
    assert b"Technical Data" in r.data
    assert b"Supplements" in r.data


def test_create_post_inserts_record(client, pottery_service):
    r = client.post("/pottery/create", data={
        "sito": "X", "area": "A", "us": "1", "form": "Olla",
        "fabric": "Coarse", "qty": "2",
    }, follow_redirects=False)
    assert r.status_code in (302, 303)
    items, total = pottery_service.get_all_pottery()
    assert total == 1
    assert items[0].sito == "X"
    assert items[0].form == "Olla"


def test_create_post_missing_sito_flashes_error(client):
    r = client.post("/pottery/create", data={"form": "Olla"}, follow_redirects=True)
    assert r.status_code == 200
    assert b"sito" in r.data.lower()  # flashed error


def test_detail_renders_record(client, pottery_service):
    p = pottery_service.create_pottery({"sito": "X", "form": "Olla", "fabric": "Coarse"})
    r = client.get(f"/pottery/{p.id_rep}")
    assert r.status_code == 200
    assert b"Olla" in r.data
    assert b"Coarse" in r.data


def test_detail_404_for_missing(client):
    r = client.get("/pottery/99999")
    assert r.status_code == 404


def test_edit_get_prefills_form(client, pottery_service):
    p = pottery_service.create_pottery({"sito": "X", "form": "Olla"})
    r = client.get(f"/pottery/{p.id_rep}/edit")
    assert r.status_code == 200
    assert b"Olla" in r.data


def test_edit_post_updates(client, pottery_service):
    p = pottery_service.create_pottery({"sito": "X", "form": "Olla"})
    r = client.post(f"/pottery/{p.id_rep}/edit", data={
        "sito": "X", "form": "Ciotola", "qty": "3"
    })
    assert r.status_code in (302, 303)
    refreshed = pottery_service.get_pottery_by_id(p.id_rep)
    assert refreshed.form == "Ciotola"
    assert refreshed.qty == 3


def test_delete_removes_record(client, pottery_service):
    p = pottery_service.create_pottery({"sito": "X", "form": "Olla"})
    r = client.post(f"/pottery/{p.id_rep}/delete")
    assert r.status_code in (302, 303)
    assert pottery_service.get_pottery_by_id(p.id_rep) is None


def test_api_forms_returns_distinct(client, pottery_service):
    pottery_service.create_pottery({"sito": "X", "form": "Olla"})
    pottery_service.create_pottery({"sito": "X", "form": "Ciotola"})
    pottery_service.create_pottery({"sito": "Y", "form": "Olla"})
    r = client.get("/api/pottery/forms")
    assert r.status_code == 200
    vs = r.get_json()["values"]
    assert set(vs) == {"Olla", "Ciotola"}


def test_api_stats(client, pottery_service):
    pottery_service.create_pottery({"sito": "X", "form": "Olla", "fabric": "Coarse", "qty": 5, "anno": 2024})
    pottery_service.create_pottery({"sito": "X", "form": "Ciotola", "fabric": "Fine", "qty": 1, "anno": 2024})
    r = client.get("/api/pottery/stats?sito=X")
    assert r.status_code == 200
    o = r.get_json()
    assert o["total"] == 2
    assert any(d["form"] == "Olla" for d in o["by_form"])
    assert o["mni"] == 6
