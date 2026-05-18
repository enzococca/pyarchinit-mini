import sqlite3
import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def client_and_db(tmp_path):
    db = tmp_path / "rc.db"
    conn = sqlite3.connect(db)
    # Real pyarchinit schema: periodo / fase / datazione / sito.
    conn.executescript("""
    CREATE TABLE period_table (
        id_period INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT,
        periodo TEXT,
        fase TEXT,
        datazione TEXT,
        descrizione TEXT
    );
    """)
    conn.commit()
    conn.close()

    from flask import Flask, g
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp

    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.before_request
    def _attach():
        g.db_session = Session()

    @app.teardown_request
    def _detach(exc):
        try:
            g.db_session.close()
        except Exception:
            pass

    app.register_blueprint(harris_creator_bp)
    yield app.test_client(), db


def test_post_create_row(client_and_db):
    cli, db = client_and_db
    r = cli.post("/harris-creator/api/swimlanes/Volterra", json={
        "period_name": "Period 1",
        "phase_name": "a",
        "start_date": 100,
        "end_date": 200,
    })
    assert r.status_code == 201
    data = r.get_json()
    assert data["period_name"] == "Period 1"
    assert data["row_id"] == "row_period-1_a"

    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM period_table").fetchone()[0]
    conn.close()
    assert count == 1


def test_post_create_row_idempotent(client_and_db):
    cli, db = client_and_db
    cli.post("/harris-creator/api/swimlanes/Volterra", json={
        "period_name": "P1", "phase_name": "a",
    })
    r = cli.post("/harris-creator/api/swimlanes/Volterra", json={
        "period_name": "P1", "phase_name": "a",
    })
    # Either 201 or 200 acceptable for idempotent
    assert r.status_code in (200, 201)

    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM period_table").fetchone()[0]
    conn.close()
    assert count == 1


def test_post_create_row_empty_name_returns_400(client_and_db):
    cli, _ = client_and_db
    r = cli.post("/harris-creator/api/swimlanes/Volterra", json={"period_name": ""})
    assert r.status_code == 400


def test_post_create_row_invalid_dates_returns_400(client_and_db):
    cli, _ = client_and_db
    r = cli.post("/harris-creator/api/swimlanes/Volterra", json={
        "period_name": "P1", "start_date": 200, "end_date": 100,
    })
    assert r.status_code == 400
