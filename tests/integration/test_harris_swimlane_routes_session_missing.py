"""Verify _get_session() fails loud when g.db_session is not bound."""
import pytest
from flask import Flask

from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp


@pytest.fixture
def client_no_session():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(harris_creator_bp)
    # Deliberately NO before_request hook setting g.db_session
    yield app.test_client()


def test_swimlanes_endpoint_fails_loud_without_session(client_no_session):
    r = client_no_session.get("/harris-creator/api/swimlanes/Volterra")
    # Should return 500 with explicit error, NOT silent AttributeError
    assert r.status_code == 500
    body = r.get_json() or {}
    # Either "internal" generic error catch or our explicit message
    assert "error" in body
