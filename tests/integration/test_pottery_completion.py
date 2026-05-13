"""v2.1.61 pottery completion tests (T1-T4)."""
import os

from flask import Flask
from flask_login import LoginManager, AnonymousUserMixin
from jinja2 import ChoiceLoader, FileSystemLoader
import pytest

from pyarchinit_mini.web_interface.pottery_routes import _register_pottery_routes

_HERE = os.path.dirname(__file__)
_APP_TEMPLATES = os.path.join(_HERE, "..", "..", "pyarchinit_mini", "web_interface", "templates")
_TEST_TEMPLATES = os.path.join(_HERE, "..", "templates")


@pytest.fixture
def flask_app(db_manager):
    app = Flask(
        __name__,
        template_folder=_APP_TEMPLATES,
        static_folder=os.path.join(
            _HERE, "..", "..", "pyarchinit_mini", "web_interface", "static"
        ),
    )
    app.config["TESTING"] = True
    app.config["LOGIN_DISABLED"] = True
    app.config["SECRET_KEY"] = "test"
    app.db_manager = db_manager

    # Override loader: test templates first (minimal base.html), then real templates
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(os.path.abspath(_TEST_TEMPLATES)),
        FileSystemLoader(os.path.abspath(_APP_TEMPLATES)),
    ])

    app.jinja_env.globals.setdefault("get_locale", lambda: "it")
    app.jinja_env.globals.setdefault("_", lambda s: s)
    app.jinja_env.globals.setdefault("csrf_token", lambda: "test-csrf-token")

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.anonymous_user = AnonymousUserMixin

    @login_manager.user_loader
    def _load_user(_uid):
        return None

    @app.route("/")
    def index():
        return ""

    @app.route("/media/upload")
    def upload_media():
        return ""

    _register_pottery_routes(app)
    return app


@pytest.fixture
def client(flask_app):
    return flask_app.test_client()


@pytest.fixture
def pottery_service(db_manager):
    from pyarchinit_mini.services.pottery_service import PotteryService
    return PotteryService(db_manager)


def test_list_shows_view_and_edit_buttons(client, pottery_service):
    p = pottery_service.create_pottery({"sito": "X", "form": "Olla"})
    r = client.get("/pottery")
    assert r.status_code == 200
    body = r.data.decode("utf-8")
    # Both endpoints must be linked in the row
    assert f"/pottery/{p.id_rep}" in body, "Detail link missing"
    assert f"/pottery/{p.id_rep}/edit" in body, "Edit link missing"


def test_form_edit_shows_manage_media_button(client, pottery_service):
    p = pottery_service.create_pottery({"sito": "X", "form": "Olla"})
    r = client.get(f"/pottery/{p.id_rep}/edit")
    assert r.status_code == 200
    body = r.data.decode("utf-8")
    assert "entity_type=pottery" in body and f"entity_id={p.id_rep}" in body, "Manage media link missing"


def test_form_create_no_manage_media_button(client):
    """Manage media should only render when editing an existing pottery."""
    r = client.get("/pottery/create")
    assert r.status_code == 200
    body = r.data.decode("utf-8")
    assert "entity_type=pottery" not in body


def test_api_forms_includes_thesaurus_defaults(client, pottery_service):
    # /api/pottery/forms must include archaeological defaults even with zero DB rows
    r = client.get("/api/pottery/forms")
    assert r.status_code == 200
    values = r.get_json()["values"]
    # Defaults from THESAURUS_MAPPINGS['pottery_table']['form']
    for expected in ("Olla", "Ciotola", "Anfora"):
        assert expected in values, f"{expected!r} missing from API output"


def test_api_forms_merges_db_with_defaults(client, pottery_service):
    pottery_service.create_pottery({"sito": "X", "form": "CustomShape"})
    r = client.get("/api/pottery/forms")
    values = r.get_json()["values"]
    assert "CustomShape" in values  # DB value
    assert "Olla" in values         # default value
