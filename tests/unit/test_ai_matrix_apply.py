"""Tests for ai_matrix.apply.apply_ai_plan."""
from datetime import datetime
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.ai_matrix.plan import AIPlan, USRow, EdgeRow
from pyarchinit_mini.ai_matrix.apply import apply_ai_plan


@pytest.fixture
def db_session(tmp_path):
    """Sqlite session with the minimal schema apply_ai_plan needs."""
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE site_table (
                id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT UNIQUE NOT NULL,
                descrizione TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
        """))
        conn.execute(text("""
            CREATE TABLE us_table (
                id_us INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT NOT NULL,
                area TEXT NOT NULL,
                us TEXT NOT NULL,
                unita_tipo TEXT,
                d_stratigrafica TEXT,
                fase_recente INTEGER,
                fase_iniziale INTEGER,
                created_at DATETIME,
                updated_at DATETIME
            )
        """))
        conn.execute(text("""
            CREATE TABLE us_relationships_table (
                id_rel INTEGER PRIMARY KEY AUTOINCREMENT,
                sito_from TEXT,
                sito_to TEXT,
                us_from INTEGER,
                us_to INTEGER,
                tipo_relazione TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
        """))
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def _make_plan(us_rows=None, edges=None):
    return AIPlan(
        detected_site=None, detected_area=None,
        us=us_rows or [], edges=edges or [],
    )


def test_apply_creates_site_when_new(db_session):
    plan = _make_plan(us_rows=[USRow("1", "A", "USM", "x", 1, 1)])
    result = apply_ai_plan(plan, "NewSite", db_session)
    assert result.site_created is True
    row = db_session.execute(text("SELECT sito FROM site_table")).fetchone()
    assert row[0] == "NewSite"


def test_apply_does_not_recreate_existing_site(db_session):
    db_session.execute(text(
        "INSERT INTO site_table (sito, created_at, updated_at) VALUES ('S', :n, :n)"
    ), {"n": datetime.utcnow()})
    db_session.commit()
    plan = _make_plan(us_rows=[USRow("1", "A", "USM", "x", 1, 1)])
    result = apply_ai_plan(plan, "S", db_session)
    assert result.site_created is False


def test_apply_imports_us_with_audit_cols(db_session):
    plan = _make_plan(us_rows=[USRow("11a", "Area1", "USM", "Muro", 1, 1)])
    result = apply_ai_plan(plan, "S", db_session)
    assert result.us_imported == 1
    row = db_session.execute(text(
        "SELECT us, area, unita_tipo, created_at FROM us_table WHERE sito = 'S'"
    )).fetchone()
    assert row[0] == "11a"
    assert row[1] == "Area1"
    assert row[2] == "USM"
    assert row[3] is not None  # audit col populated


def test_apply_skips_duplicate_us(db_session):
    plan1 = _make_plan(us_rows=[USRow("1", "A", "USM", "x", 1, 1)])
    apply_ai_plan(plan1, "S", db_session)
    plan2 = _make_plan(us_rows=[USRow("1", "A", "US", "y", 2, 2)])
    result = apply_ai_plan(plan2, "S", db_session)
    assert result.us_imported == 0
    assert result.us_skipped == 1


def test_apply_skips_us_missing_mandatory_fields(db_session):
    plan = _make_plan(us_rows=[
        USRow("", "A", "USM", "x", 1, 1),       # missing us_num
        USRow("1", None, "USM", "x", 1, 1),     # missing area
        USRow("2", "A", "", "x", 1, 1),         # missing unit_type
        USRow("3", "A", "USM", "x", 1, 1),      # valid
    ])
    result = apply_ai_plan(plan, "S", db_session)
    assert result.us_imported == 1
    assert result.us_skipped == 3


def test_apply_coerces_unknown_unit_type_to_us(db_session):
    plan = _make_plan(us_rows=[USRow("1", "A", "XYZ", "x", 1, 1)])
    apply_ai_plan(plan, "S", db_session)
    row = db_session.execute(text("SELECT unita_tipo FROM us_table")).fetchone()
    assert row[0] == "US"


def test_apply_imports_int_edges(db_session):
    plan = _make_plan(edges=[EdgeRow("1", "2", "copre")])
    result = apply_ai_plan(plan, "S", db_session)
    assert result.edges_imported == 1
    row = db_session.execute(text(
        "SELECT us_from, us_to, tipo_relazione FROM us_relationships_table"
    )).fetchone()
    assert row[0] == 1 and row[1] == 2 and row[2] == "copre"


def test_apply_skips_non_numeric_edges(db_session):
    plan = _make_plan(edges=[
        EdgeRow("11a", "12", "copre"),   # us_from non-int
        EdgeRow("1", "abc", "copre"),    # us_to non-int
        EdgeRow("1", "2", "copre"),      # valid
    ])
    result = apply_ai_plan(plan, "S", db_session)
    assert result.edges_imported == 1
    assert result.edges_skipped == 2


def test_apply_skips_unknown_tipo(db_session):
    plan = _make_plan(edges=[
        EdgeRow("1", "2", "invented_relation"),
        EdgeRow("1", "2", "copre"),
    ])
    result = apply_ai_plan(plan, "S", db_session)
    assert result.edges_imported == 1
    assert result.edges_skipped == 1


def test_apply_skips_duplicate_edges(db_session):
    plan1 = _make_plan(edges=[EdgeRow("1", "2", "copre")])
    apply_ai_plan(plan1, "S", db_session)
    plan2 = _make_plan(edges=[EdgeRow("1", "2", "copre")])
    result = apply_ai_plan(plan2, "S", db_session)
    assert result.edges_imported == 0
    assert result.edges_skipped == 1
    # Assert no duplicate row was inserted
    count = db_session.execute(text(
        "SELECT COUNT(*) FROM us_relationships_table"
    )).fetchone()[0]
    assert count == 1
