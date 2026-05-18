import sqlite3
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.harris_swimlane.row_provider import Row, RowProvider


@pytest.fixture
def session_with_period_table(tmp_path):
    db = tmp_path / "rp.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE period_table (
        id_period INTEGER PRIMARY KEY,
        period_name TEXT NOT NULL,
        phase_name TEXT,
        start_date INTEGER,
        end_date INTEGER,
        description TEXT,
        chronology TEXT
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
    rows = [
        ("Roman Imperial", "early", -27, 100),
        ("Roman Imperial", "late", 100, 476),
        ("Medieval", "early", 476, 1000),
    ]
    for r in rows:
        conn.execute(
            "INSERT INTO period_table (period_name, phase_name, start_date, end_date) VALUES (?,?,?,?)",
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
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE period_table (
        id_period INTEGER PRIMARY KEY, period_name TEXT, phase_name TEXT,
        start_date INTEGER, end_date INTEGER, description TEXT, chronology TEXT
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


def test_list_rows_from_period_table_sorted_recent_first(session_with_period_table):
    rows = RowProvider(session_with_period_table, "Volterra").list_rows()
    assert len(rows) == 3
    assert rows[0].period_name == "Medieval"
    assert rows[1].period_name == "Roman Imperial"
    assert rows[1].phase_name == "late"
    assert rows[2].phase_name == "early"


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
