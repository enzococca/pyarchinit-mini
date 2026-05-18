"""Tests for build_import_plan — DB diff + conflict detection."""
import sqlite3
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.graphml_io.yed_importer import (
    parse_extended_matrix, build_import_plan,
)


@pytest.fixture
def session(tmp_path):
    db = tmp_path / "plan.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
    CREATE TABLE site_table (
      id_sito INTEGER PRIMARY KEY, sito TEXT,
      created_at DATETIME, updated_at DATETIME
    );
    CREATE TABLE us_table (
      id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
      d_stratigrafica TEXT, datazione TEXT, file_path TEXT,
      rapporti TEXT, node_uuid TEXT,
      periodo_iniziale TEXT, fase_iniziale TEXT,
      struttura TEXT, attivita TEXT, settore TEXT,
      ambient TEXT, saggio TEXT, quad_par TEXT,
      created_at DATETIME, updated_at DATETIME
    );
    CREATE TABLE periodizzazione_table (
      id_periodizzazione INTEGER PRIMARY KEY,
      sito TEXT, periodo_iniziale TEXT, fase_iniziale TEXT,
      datazione_estesa TEXT,
      created_at DATETIME, updated_at DATETIME
    );
    CREATE TABLE us_relationships_table (
      id_relationship INTEGER PRIMARY KEY,
      sito TEXT, us_from INTEGER, us_to INTEGER, relationship_type TEXT,
      created_at DATETIME, updated_at DATETIME
    );
    """)
    conn.commit(); conn.close()
    eng = create_engine(f"sqlite:///{db}")
    s = sessionmaker(bind=eng)()
    yield s
    s.close()


FIX = Path(__file__).parent.parent / "fixtures" / "yed_graphml"


def test_plan_marks_site_da_creare(session):
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan = build_import_plan(parsed, session)
    assert plan.sites == [{"sito": "TestSite", "da_creare": True}]


def test_plan_all_us_action_create_on_empty_db(session):
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan = build_import_plan(parsed, session)
    assert len(plan.us_records) == 3
    assert all(r["action"] == "create" for r in plan.us_records)


def test_plan_marks_update_when_uuid_exists(session):
    from sqlalchemy import text
    session.execute(text(
        "INSERT INTO us_table (sito, us, unita_tipo, node_uuid) "
        "VALUES ('TestSite', '1', 'US', 'uuid-001')"
    ))
    session.commit()
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan = build_import_plan(parsed, session)
    us1 = next(r for r in plan.us_records if r["us"] == "1")
    assert us1["action"] == "update"


def test_plan_includes_periodizations(session):
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan = build_import_plan(parsed, session)
    assert len(plan.periodizations) >= 1


def test_plan_includes_relationships(session):
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan = build_import_plan(parsed, session)
    assert len(plan.relationships) == 2


def test_apply_inserts_new_records(session):
    from sqlalchemy import text
    from pyarchinit_mini.graphml_io.yed_importer import apply_import_plan
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan = build_import_plan(parsed, session)
    result = apply_import_plan(plan, session)
    assert result.us_created == 3
    assert result.sites_created == 1
    count = session.execute(text("SELECT COUNT(*) FROM us_table")).scalar()
    assert count == 3


def test_apply_is_idempotent(session):
    from pyarchinit_mini.graphml_io.yed_importer import apply_import_plan
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan1 = build_import_plan(parsed, session)
    apply_import_plan(plan1, session)

    plan2 = build_import_plan(parsed, session)
    result2 = apply_import_plan(plan2, session)
    assert result2.us_created == 0
    assert result2.us_updated == 3
