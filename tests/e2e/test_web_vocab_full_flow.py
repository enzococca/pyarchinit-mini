"""End-to-end smoke for /api/v1/vocab/* endpoints against the real Flask app.

Uses a minimal Flask app with only the vocab blueprint registered — the same
proven pattern as tests/integration/test_vocab_routes.py — rather than
invoking the full create_app() factory, which requires DB, backup scheduler,
and connection-manager setup unrelated to vocab correctness.
"""
from pathlib import Path
import pytest
from flask import Flask
from flask_login import LoginManager, AnonymousUserMixin

from pyarchinit_mini.vocab.provider import VocabProvider


FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def app_client():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)

    from pyarchinit_mini.web_interface.vocab_routes import vocab_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"

    # flask-login needed by the /diagnostics route (current_user.is_authenticated)
    lm = LoginManager()
    lm.init_app(app)
    lm.anonymous_user = AnonymousUserMixin

    @lm.user_loader
    def _load_user(_id):
        return None

    app.register_blueprint(vocab_bp)

    with app.test_client() as c:
        yield c

    VocabProvider.reset()


def test_vocab_unit_types_endpoint_serves(app_client):
    r = app_client.get("/api/v1/vocab/unit-types?lang=it")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert any(t["abbreviation"] == "US" for t in data)


def test_vocab_visual_style_endpoint_serves(app_client):
    r = app_client.get("/api/v1/vocab/visual-style/US")
    assert r.status_code == 200
    data = r.get_json()
    assert data["shape"] == "rectangle"


def test_vocab_unit_type_single_endpoint_serves(app_client):
    r = app_client.get("/api/v1/vocab/unit-types/USVs?lang=en")
    assert r.status_code == 200
    assert r.get_json()["abbreviation"] == "USVs"


def test_vocab_unit_type_unknown_returns_404(app_client):
    r = app_client.get("/api/v1/vocab/unit-types/ZZZ_NEVER_SEEN")
    assert r.status_code == 404
    data = r.get_json()
    assert data["error"] == "unknown_unit_type"


def test_vocab_diagnostics_requires_admin(app_client):
    # Unauthenticated AnonymousUser → is_authenticated is False → 403
    r = app_client.get("/api/v1/vocab/diagnostics")
    assert r.status_code == 403
