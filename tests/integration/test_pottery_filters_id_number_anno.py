"""PotteryService respects id_number / anno filters with integer-cast guard."""
import sqlite3
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.models.base import Base
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.models.pottery import Pottery
from pyarchinit_mini.services.pottery_service import PotteryService


@pytest.fixture
def db_manager(tmp_path):
    db = tmp_path / "pot_filters.db"
    conn = DatabaseConnection.from_url(f"sqlite:///{db}")
    Base.metadata.create_all(conn.engine)
    mgr = DatabaseManager(conn)
    # Seed 4 rows: 2 different anno, 2 different id_number
    with conn.get_session() as s:
        s.add(Site(sito="TestSite"))
        s.commit()
    with conn.get_session() as s:
        s.add(Pottery(sito="TestSite", us=1, id_number=10, anno=2024, form="amphora"))
        s.add(Pottery(sito="TestSite", us=2, id_number=11, anno=2024, form="olla"))
        s.add(Pottery(sito="TestSite", us=3, id_number=12, anno=2025, form="amphora"))
        s.add(Pottery(sito="TestSite", us=4, id_number=13, anno=2025, form="olla"))
        s.commit()
    return mgr


def test_filter_by_id_number(db_manager):
    svc = PotteryService(db_manager)
    items, total = svc.get_all_pottery(filters={"id_number": 11})
    assert total == 1
    assert items[0].id_number == 11


def test_filter_by_anno(db_manager):
    svc = PotteryService(db_manager)
    items, total = svc.get_all_pottery(filters={"anno": 2024})
    assert total == 2
    assert {i.anno for i in items} == {2024}


def test_filter_combined_id_number_and_anno(db_manager):
    svc = PotteryService(db_manager)
    items, total = svc.get_all_pottery(filters={"anno": 2025, "id_number": 12})
    assert total == 1
    assert items[0].id_number == 12 and items[0].anno == 2025


def test_filter_id_number_non_numeric_ignored(db_manager):
    """A non-numeric id_number must be silently ignored (no SQL error)."""
    svc = PotteryService(db_manager)
    items, total = svc.get_all_pottery(filters={"id_number": "abc"})
    assert total == 4  # all 4 rows returned (filter dropped)


def test_filter_anno_non_numeric_ignored(db_manager):
    svc = PotteryService(db_manager)
    items, total = svc.get_all_pottery(filters={"anno": "xyz"})
    assert total == 4
