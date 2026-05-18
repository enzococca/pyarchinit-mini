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
    conn.execute("""CREATE TABLE period_table (
        id_period INTEGER PRIMARY KEY AUTOINCREMENT,
        period_name TEXT NOT NULL,
        phase_name TEXT,
        start_date INTEGER, end_date INTEGER,
        description TEXT, chronology TEXT
    )""")
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def test_upsert_row_creates_new_entry(session):
    svc = PeriodSyncService(session)
    row = svc.upsert_row(period_name="P1", phase_name="a",
                         start_date=100, end_date=200)
    assert row.period_name == "P1"
    assert row.phase_name == "a"
    assert row.start_date == 100
    assert row.row_id == "row_p1_a"


def test_upsert_row_idempotent(session):
    svc = PeriodSyncService(session)
    svc.upsert_row(period_name="P1", phase_name="a", start_date=100, end_date=200)
    svc.upsert_row(period_name="P1", phase_name="a", start_date=100, end_date=200)
    count = session.execute(text(
        "SELECT COUNT(*) FROM period_table WHERE period_name='P1' AND phase_name='a'"
    )).scalar()
    assert count == 1


def test_upsert_row_different_phase_creates_new(session):
    svc = PeriodSyncService(session)
    svc.upsert_row(period_name="P1", phase_name="a")
    svc.upsert_row(period_name="P1", phase_name="b")
    count = session.execute(text(
        "SELECT COUNT(*) FROM period_table WHERE period_name='P1'"
    )).scalar()
    assert count == 2


def test_upsert_row_empty_period_raises(session):
    svc = PeriodSyncService(session)
    with pytest.raises(PeriodSyncError):
        svc.upsert_row(period_name="")


def test_upsert_row_invalid_date_range_raises(session):
    svc = PeriodSyncService(session)
    with pytest.raises(PeriodSyncError):
        svc.upsert_row(period_name="P1", phase_name="a",
                       start_date=200, end_date=100)


def test_upsert_row_no_phase(session):
    svc = PeriodSyncService(session)
    row = svc.upsert_row(period_name="Iron Age")
    assert row.phase_name is None
    assert row.row_id == "row_iron-age"
