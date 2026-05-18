import sqlite3
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.harris_swimlane.row_provider import Row, RowProvider


def _make_db_with_real_schema(db_path):
    """Create the 3 tables matching the real pyarchinit schema used in prod."""
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE period_table (
        id_period INTEGER PRIMARY KEY,
        sito TEXT,
        periodo TEXT,
        fase TEXT,
        datazione TEXT,
        descrizione TEXT
    )""")
    conn.execute("""CREATE TABLE periodizzazione_table (
        id_periodizzazione INTEGER PRIMARY KEY,
        sito TEXT, area TEXT, us INTEGER,
        periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT
    )""")
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY,
        sito TEXT, us INTEGER,
        periodo_iniziale TEXT, fase_iniziale TEXT
    )""")
    return conn


@pytest.fixture
def session_with_period_table(tmp_path):
    db = tmp_path / "rp.db"
    conn = _make_db_with_real_schema(db)
    rows = [
        ("Volterra", "Roman Imperial", "early", "-27..100"),
        ("Volterra", "Roman Imperial", "late", "100..476"),
        ("Volterra", "Medieval", "early", "476..1000"),
    ]
    for r in rows:
        conn.execute(
            "INSERT INTO period_table (sito, periodo, fase, datazione) VALUES (?,?,?,?)",
            r,
        )
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


@pytest.fixture
def session_fallback_only(tmp_path):
    db = tmp_path / "rp_fb.db"
    conn = _make_db_with_real_schema(db)
    pz = [
        ("Volterra", "A", 1, "Roman", "a", None, None),
        ("Volterra", "A", 2, "Medieval", "b", None, None),
        ("Volterra", "A", 3, "Roman", "a", None, None),
    ]
    for r in pz:
        conn.execute(
            "INSERT INTO periodizzazione_table (sito, area, us, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale) VALUES (?,?,?,?,?,?,?)",
            r,
        )
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def test_list_rows_from_period_table_sorted_alphabetically(session_with_period_table):
    # Real period_table has no numeric start_date/end_date — we sort by
    # (periodo, fase) alphabetically and leave numeric dates as None.
    rows = RowProvider(session_with_period_table, "Volterra").list_rows()
    assert len(rows) == 3
    assert rows[0].period_name == "Medieval"
    assert rows[0].phase_name == "early"
    assert rows[1].period_name == "Roman Imperial"
    assert rows[1].phase_name == "early"
    assert rows[2].period_name == "Roman Imperial"
    assert rows[2].phase_name == "late"
    for r in rows:
        assert r.start_date is None
        assert r.end_date is None


def test_list_rows_source_period_table(session_with_period_table):
    rows = RowProvider(session_with_period_table, "Volterra").list_rows()
    for r in rows:
        assert r.source == "period_table"


def test_list_rows_assigns_color(session_with_period_table):
    rows = RowProvider(session_with_period_table, "Volterra").list_rows()
    for r in rows:
        assert r.color.startswith("#")
        assert len(r.color) == 7


def test_list_rows_fallback_path(session_fallback_only):
    rows = RowProvider(session_fallback_only, "Volterra").list_rows()
    assert len(rows) == 2
    for r in rows:
        assert r.source == "fallback_distinct"
        assert r.start_date is None


def test_find_row_returns_match(session_with_period_table):
    rp = RowProvider(session_with_period_table, "Volterra")
    rp.list_rows()
    row = rp.find_row("Roman Imperial", "early")
    assert row is not None
    assert row.period_name == "Roman Imperial"


def test_find_row_unknown_returns_none(session_with_period_table):
    rp = RowProvider(session_with_period_table, "Volterra")
    rp.list_rows()
    assert rp.find_row("Bogus", "x") is None
