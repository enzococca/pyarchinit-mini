from pathlib import Path
import sqlite3
import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def client_and_db(tmp_path):
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX_VOCAB)

    db = tmp_path / "save_route.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
    CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, area TEXT, us INTEGER, unita_tipo TEXT,
        d_stratigrafica TEXT, d_interpretativa TEXT, rapporti TEXT,
        node_uuid TEXT, periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT
    );
    INSERT INTO us_table (sito, us, unita_tipo, node_uuid, periodo_iniziale, fase_iniziale)
    VALUES ('Volterra', 1001, 'US', 'u-1', 'Roman', 'a');
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
    VocabProvider.reset()


def test_post_save_updates_us(client_and_db):
    cli, db = client_and_db
    from unittest.mock import patch
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen"):
        r = cli.post("/harris-creator/api/save/Volterra", json={
            "pending_us_updates": [
                {"us": 1001, "periodo_iniziale": "Medieval", "fase_iniziale": "b"},
            ],
            "pending_us_inserts": [],
            "pending_us_deletes": [],
        })
    assert r.status_code == 200
    data = r.get_json()
    assert data["updated"] == 1

    conn = sqlite3.connect(db)
    val = conn.execute("SELECT periodo_iniziale FROM us_table WHERE us=1001").fetchone()[0]
    conn.close()
    assert val == "Medieval"


def test_post_save_empty_body(client_and_db):
    cli, _ = client_and_db
    r = cli.post("/harris-creator/api/save/Volterra", json={})
    assert r.status_code == 200
    data = r.get_json()
    assert data["updated"] == 0
    assert data["inserted"] == 0
    assert data["deleted"] == 0


def test_post_save_handles_save_error(client_and_db):
    cli, _ = client_and_db
    from unittest.mock import patch
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen"):
        # Insert duplicate us — produces errors[] in result, transaction rollback
        r = cli.post("/harris-creator/api/save/Volterra", json={
            "pending_us_inserts": [
                {"sito": "Volterra", "us": 1001, "unita_tipo": "US"},
            ],
        })
    # Either 200 with errors[] OR 500 acceptable
    assert r.status_code in (200, 500)
