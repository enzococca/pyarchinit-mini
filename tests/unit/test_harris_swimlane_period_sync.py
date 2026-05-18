"""Tests for PeriodSyncService against the real pyarchinit period_table schema."""
import sqlite3
import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.harris_swimlane.period_sync_service import PeriodSyncService
from pyarchinit_mini.harris_swimlane.exceptions import PeriodSyncError


@pytest.fixture
def session(tmp_path):
    db = tmp_path / "ps.db"
    conn = sqlite3.connect(db)
    # Real pyarchinit schema: periodo / fase / datazione / sito.
    conn.execute("""CREATE TABLE period_table (
        id_period INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT,
        periodo TEXT,
        fase TEXT,
        datazione TEXT,
        descrizione TEXT
    )""")
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def test_upsert_row_creates_new_entry(session):
    svc = PeriodSyncService(session, site="Volterra")
    row = svc.upsert_row(period_name="P1", phase_name="a",
                         start_date=100, end_date=200)
    assert row.period_name == "P1"
    assert row.phase_name == "a"
    assert row.start_date == 100
    assert row.row_id == "row_p1_a"
    datazione = session.execute(text(
        "SELECT datazione FROM period_table WHERE periodo='P1' AND fase='a'"
    )).scalar()
    assert datazione == "100..200"


def test_upsert_row_idempotent(session):
    svc = PeriodSyncService(session, site="Volterra")
    svc.upsert_row(period_name="P1", phase_name="a", start_date=100, end_date=200)
    svc.upsert_row(period_name="P1", phase_name="a", start_date=100, end_date=200)
    count = session.execute(text(
        "SELECT COUNT(*) FROM period_table WHERE periodo='P1' AND fase='a'"
    )).scalar()
    assert count == 1


def test_upsert_row_different_phase_creates_new(session):
    svc = PeriodSyncService(session, site="Volterra")
    svc.upsert_row(period_name="P1", phase_name="a")
    svc.upsert_row(period_name="P1", phase_name="b")
    count = session.execute(text(
        "SELECT COUNT(*) FROM period_table WHERE periodo='P1'"
    )).scalar()
    assert count == 2


def test_upsert_row_empty_period_raises(session):
    svc = PeriodSyncService(session, site="Volterra")
    with pytest.raises(PeriodSyncError):
        svc.upsert_row(period_name="")


def test_upsert_row_invalid_date_range_raises(session):
    svc = PeriodSyncService(session, site="Volterra")
    with pytest.raises(PeriodSyncError):
        svc.upsert_row(period_name="P1", phase_name="a",
                       start_date=200, end_date=100)


def test_upsert_row_no_phase(session):
    svc = PeriodSyncService(session, site="Volterra")
    row = svc.upsert_row(period_name="Iron Age")
    assert row.phase_name is None
    assert row.row_id == "row_iron-age"


def test_upsert_row_persists_sito(session):
    svc = PeriodSyncService(session, site="Volterra")
    svc.upsert_row(period_name="P1", phase_name="a")
    sito = session.execute(text(
        "SELECT sito FROM period_table WHERE periodo='P1'"
    )).scalar()
    assert sito == "Volterra"
