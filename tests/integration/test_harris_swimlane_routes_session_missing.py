"""Verify _get_session() lazily acquires a session when g.db_session is not bound.

Prior to 2.4.2, _get_session() raised RuntimeError when no before_request hook
had set g.db_session — but no such hook exists in the production app, so every
swimlane request 500'd. 2.4.2 lazy-acquires a session through the same path as
get_db_session() and binds it to g for the duration of the request.
"""
import pytest
from flask import Flask
from sqlalchemy import create_engine

from pyarchinit_mini.models.base import Base
from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp


@pytest.fixture
def client_no_session(tmp_path, monkeypatch):
    db_path = tmp_path / "swimlane_lazy.db"
    db_url = f"sqlite:///{db_path}"
    # Pre-create the schema so lazy session has tables to query.
    Base.metadata.create_all(create_engine(db_url))
    monkeypatch.setenv("DATABASE_URL", db_url)
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(harris_creator_bp)
    # Deliberately NO before_request hook setting g.db_session — we rely on
    # _get_session() lazy acquisition.
    yield app.test_client()


def test_swimlanes_endpoint_lazy_acquires_session(client_no_session):
    """Without a pre-bound g.db_session, the endpoint should still answer 200
    by lazily opening a fresh session via get_db_session()."""
    r = client_no_session.get("/harris-creator/api/swimlanes/EmptySite")
    assert r.status_code == 200, r.get_data(as_text=True)
    body = r.get_json()
    assert isinstance(body, list)
