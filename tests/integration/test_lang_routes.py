"""Integration tests for /set-language/<lang> endpoint."""
import pytest
from flask import Flask

from pyarchinit_mini.i18n.lang_routes import lang_bp


@pytest.fixture
def client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"
    app.register_blueprint(lang_bp)

    # Stub `index` route so url_for fallback resolves.
    @app.route("/")
    def index():
        return "home"

    return app.test_client()


def test_set_language_it_saves_session(client):
    r = client.post("/set-language/it", headers={"Referer": "/pottery/?q=test"})
    assert r.status_code == 302
    assert r.location == "/pottery/?q=test"
    with client.session_transaction() as s:
        assert s["lang"] == "it"


def test_set_language_en_saves_session(client):
    r = client.post("/set-language/en", headers={"Referer": "/pottery/"})
    assert r.status_code == 302
    with client.session_transaction() as s:
        assert s["lang"] == "en"


def test_set_language_invalid_redirects_no_change(client):
    r = client.post("/set-language/zh", headers={"Referer": "/pottery/"})
    assert r.status_code == 302
    with client.session_transaction() as s:
        assert "lang" not in s


def test_set_language_no_referrer_falls_back_to_index(client):
    r = client.post("/set-language/it")
    assert r.status_code == 302
    assert r.location.endswith("/")


def test_set_language_preserves_query_string(client):
    r = client.post(
        "/set-language/en",
        headers={"Referer": "/pottery/?sito=Volterra&id_number=42&anno=2024"},
    )
    assert r.status_code == 302
    assert r.location == "/pottery/?sito=Volterra&id_number=42&anno=2024"
