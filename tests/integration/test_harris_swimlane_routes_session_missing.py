"""Verify _get_session() lazily acquires a session when g.db_session is not bound.

Prior to 2.4.2, _get_session() raised RuntimeError when no before_request hook
had set g.db_session — but no such hook exists in the production app, so every
swimlane request 500'd. 2.4.2 lazy-acquires a session through the same path as
get_db_session() and binds it to g for the duration of the request.
"""
import sqlite3

import pytest
from flask import Flask

from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp


@pytest.fixture
def client_no_session(tmp_path, monkeypatch):
    db_path = tmp_path / "swimlane_lazy.db"
    # Pre-create the tables Spec 3-bis queries, matching the real pyarchinit
    # production schema (periodo / fase / datazione, not period_name / phase_name).
    conn = sqlite3.connect(db_path)
    conn.executescript("""
    CREATE TABLE period_table (
        id_period INTEGER PRIMARY KEY,
        sito TEXT, periodo TEXT, fase TEXT, datazione TEXT, descrizione TEXT
    );
    CREATE TABLE periodizzazione_table (
        id_periodizzazione INTEGER PRIMARY KEY,
        sito TEXT, area TEXT, us INTEGER,
        periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT
    );
    CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY,
        sito TEXT, area TEXT, us INTEGER, unita_tipo TEXT,
        d_stratigrafica TEXT, datazione TEXT, file_path TEXT,
        rapporti TEXT, node_uuid TEXT,
        periodo_iniziale TEXT, fase_iniziale TEXT
    );
    """)
    conn.commit()
    conn.close()
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
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
