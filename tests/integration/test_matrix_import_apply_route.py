"""POST /matrix-import/apply commits selected US + edges to DB."""
import json
from pathlib import Path
import pytest

from flask import Flask
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.web_interface.matrix_import_routes import matrix_import_bp


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"
_TEST_TEMPLATES = Path(__file__).parent.parent / "templates"


def _make_app(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/a.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (
            id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT UNIQUE, descrizione TEXT,
            created_at DATETIME, updated_at DATETIME)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
            descrizione TEXT, fase_finale TEXT, fase_iniziale TEXT,
            created_at DATETIME, updated_at DATETIME)"""))
        conn.execute(text("""CREATE TABLE us_relationships_table (
            id_relationship INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, us_from INT, us_to INT,
            relationship_type TEXT, created_at DATETIME, updated_at DATETIME)"""))
    Session = sessionmaker(bind=engine)
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"
    from jinja2 import ChoiceLoader, FileSystemLoader
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(str(_TEST_TEMPLATES)),
        FileSystemLoader(str(_APP_TEMPLATES)),
    ])
    app.jinja_env.globals.setdefault("_", lambda s: s)
    app.jinja_env.globals.setdefault("get_locale", lambda: "it")
    app.jinja_env.globals.setdefault("csrf_token", lambda: "t")

    # Stub the us.list_us endpoint that apply redirects to
    from flask import Blueprint
    us_bp = Blueprint("us", __name__)
    @us_bp.route("/us/list")
    def list_us():
        return "us list page"
    app.register_blueprint(us_bp)

    app.register_blueprint(matrix_import_bp)
    return app, Session


@pytest.fixture
def client_and_session(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/a.db")
    app, Session = _make_app(tmp_path)
    return app.test_client(), Session


def _plan_json(us_rows, edges):
    return json.dumps({
        "detected_site": None, "detected_area": None,
        "us": us_rows, "edges": edges,
    })


def test_apply_commits_us_and_edges(client_and_session):
    client, Session = client_and_session
    plan = _plan_json(
        us_rows=[{"us_num": "1", "area": "A", "unit_type": "USM",
                  "descrizione": "x", "fase_recente": 1, "fase_iniziale": 1}],
        edges=[{"us_from": "1", "us_to": "2", "tipo": "copre"}],
    )
    r = client.post("/matrix-import/apply", data={
        "plan_json": plan,
        "image_b64": "",
        "sito": "TestSite",
        "selected_us": "0",
        "selected_edges": "0",
        "us_num_0": "1", "area_0": "A", "unit_type_0": "USM",
        "desc_0": "x", "fr_0": "1", "fi_0": "1",
        "ef_0": "1", "et_0": "2", "etipo_0": "copre",
    }, follow_redirects=False)
    assert r.status_code in (302, 303)
    s = Session()
    row = s.execute(text("SELECT sito FROM site_table")).fetchone()
    assert row[0] == "TestSite"
    us = s.execute(text("SELECT us, area FROM us_table")).fetchone()
    assert us[0] == "1" and us[1] == "A"
    e = s.execute(text("SELECT us_from, us_to, relationship_type FROM us_relationships_table")).fetchone()
    assert e[0] == 1 and e[1] == 2 and e[2] == "copre"


def test_apply_respects_unchecked_rows(client_and_session):
    client, Session = client_and_session
    plan = _plan_json(
        us_rows=[
            {"us_num": "1", "area": "A", "unit_type": "USM",
             "descrizione": "keep", "fase_recente": 1, "fase_iniziale": 1},
            {"us_num": "2", "area": "A", "unit_type": "USM",
             "descrizione": "skip", "fase_recente": 1, "fase_iniziale": 1},
        ],
        edges=[],
    )
    r = client.post("/matrix-import/apply", data={
        "plan_json": plan,
        "sito": "S",
        "selected_us": "0",  # only row 0
        "us_num_0": "1", "area_0": "A", "unit_type_0": "USM",
        "desc_0": "keep", "fr_0": "1", "fi_0": "1",
        "us_num_1": "2", "area_1": "A", "unit_type_1": "USM",
        "desc_1": "skip", "fr_1": "1", "fi_1": "1",
    }, follow_redirects=False)
    assert r.status_code in (302, 303)
    s = Session()
    rows = s.execute(text("SELECT us FROM us_table")).fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "1"


def test_apply_rejects_missing_sito(client_and_session):
    client, _ = client_and_session
    r = client.post("/matrix-import/apply", data={
        "plan_json": _plan_json([], []),
        "sito": "",
    }, follow_redirects=False)
    assert r.status_code in (302, 303)
    # Should redirect back to upload form, not /us/list
    assert "/us/list" not in r.headers.get("Location", "")


def test_apply_rejects_malformed_plan_json(client_and_session):
    client, _ = client_and_session
    r = client.post("/matrix-import/apply", data={
        "plan_json": "not valid json {{{",
        "sito": "S",
    }, follow_redirects=False)
    assert r.status_code in (302, 303)
    assert "/us/list" not in r.headers.get("Location", "")


def test_apply_rejects_empty_selection(client_and_session):
    client, Session = client_and_session
    plan = _plan_json(
        us_rows=[{"us_num": "1", "area": "A", "unit_type": "USM",
                  "descrizione": "x", "fase_recente": 1, "fase_iniziale": 1}],
        edges=[],
    )
    # No selected_us / selected_edges in form data → empty filtered plan
    r = client.post("/matrix-import/apply", data={
        "plan_json": plan,
        "sito": "S",
        # no selected_us, no selected_edges
    }, follow_redirects=False)
    assert r.status_code in (302, 303)
    assert "/us/list" not in r.headers.get("Location", "")
    # Verify no us_table row was created
    s = Session()
    rows = s.execute(text("SELECT us FROM us_table")).fetchall()
    assert len(rows) == 0
    # site might still be created — that's OK (apply_ai_plan never ran)


def test_apply_rejects_non_numeric_fase(client_and_session):
    client, _ = client_and_session
    plan = _plan_json(
        us_rows=[{"us_num": "1", "area": "A", "unit_type": "USM",
                  "descrizione": "x", "fase_recente": 1, "fase_iniziale": 1}],
        edges=[],
    )
    r = client.post("/matrix-import/apply", data={
        "plan_json": plan,
        "sito": "S",
        "selected_us": "0",
        "us_num_0": "1", "area_0": "A", "unit_type_0": "USM",
        "desc_0": "x", "fr_0": "abc", "fi_0": "1",  # malformed fase_recente
    }, follow_redirects=False)
    assert r.status_code in (302, 303)
    assert "/us/list" not in r.headers.get("Location", "")
