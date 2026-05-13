"""/admin/settings/ai integration tests."""
import pytest
from flask import Flask
from flask_login import LoginManager, AnonymousUserMixin


def _make_app(db_manager, tmp_path, monkeypatch):
    """Build a minimal Flask app that exposes the /admin/settings/ai routes.

    Mirrors the production wiring from app.py but isolated for unit-level
    integration testing.
    """
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))

    from jinja2 import ChoiceLoader, FileSystemLoader
    import os

    test_templates = os.path.join(os.path.dirname(__file__), "..", "templates")
    real_templates = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..",
                     "pyarchinit_mini", "web_interface", "templates")
    )

    app = Flask(__name__)
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(test_templates),
        FileSystemLoader(real_templates),
    ])
    app.config["TESTING"] = True
    app.config["LOGIN_DISABLED"] = True
    app.config["SECRET_KEY"] = "test"
    app.db_manager = db_manager

    lm = LoginManager(); lm.init_app(app); lm.anonymous_user = AnonymousUserMixin
    @lm.user_loader
    def _u(_id): return None

    @app.route("/")
    def index(): return ""

    @app.template_global()
    def csrf_token(): return "test-csrf-token"
    app.jinja_env.globals["_"] = lambda s: s

    # Register the AI settings routes inline (mirroring app.py production wiring)
    from pyarchinit_mini.services.app_setting_service import AppSettingService
    from flask import render_template, request, redirect, url_for, flash

    def _mask(key):
        if not key: return ""
        return "*" * 8 + key[-4:] if len(key) > 4 else "****"

    @app.route("/admin/settings/ai", methods=["GET", "POST"])
    def admin_settings_ai():
        svc = AppSettingService(app.db_manager)
        if request.method == "POST":
            svc.set("openai_api_key", request.form.get("openai_api_key", "").strip(), is_secret=True)
            svc.set("anthropic_api_key", request.form.get("anthropic_api_key", "").strip(), is_secret=True)
            svc.set("ai_provider", request.form.get("ai_provider", "openai").strip())
            svc.set("ai_model", request.form.get("ai_model", "").strip())
            flash("AI settings saved", "success")
            return redirect(url_for("admin_settings_ai"))
        return render_template(
            "admin/settings_ai.html",
            openai_key_masked=_mask(svc.get("openai_api_key")),
            anthropic_key_masked=_mask(svc.get("anthropic_api_key")),
            ai_provider=svc.get("ai_provider") or "openai",
            ai_model=svc.get("ai_model") or "",
        )

    return app


@pytest.fixture
def app(db_manager, tmp_path, monkeypatch):
    return _make_app(db_manager, tmp_path, monkeypatch)


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_settings_form(client):
    r = client.get("/admin/settings/ai")
    assert r.status_code == 200
    assert b"openai_api_key" in r.data
    assert b"anthropic_api_key" in r.data


def test_post_settings_saves(client, app):
    r = client.post("/admin/settings/ai", data={
        "openai_api_key": "sk-abc123",
        "anthropic_api_key": "sk-ant-xyz",
        "ai_provider": "anthropic",
        "ai_model": "claude-sonnet-4-7",
    }, follow_redirects=False)
    assert r.status_code in (302, 303)

    from pyarchinit_mini.services.app_setting_service import AppSettingService
    svc = AppSettingService(app.db_manager)
    assert svc.get("openai_api_key") == "sk-abc123"
    assert svc.get("anthropic_api_key") == "sk-ant-xyz"
    assert svc.get("ai_provider") == "anthropic"
    assert svc.get("ai_model") == "claude-sonnet-4-7"


def test_get_masks_existing_keys(client, app):
    from pyarchinit_mini.services.app_setting_service import AppSettingService
    svc = AppSettingService(app.db_manager)
    svc.set("openai_api_key", "sk-very-secret-12345", is_secret=True)
    r = client.get("/admin/settings/ai")
    assert r.status_code == 200
    body = r.data.decode("utf-8")
    # Masked form: must show only the last 4 chars, never the full secret
    assert "sk-very-secret-12345" not in body
    assert "2345" in body  # last 4 chars visible
