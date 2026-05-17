import sqlite3
from pathlib import Path
import pytest

from pyarchinit_mini.database.migrations import _2026_05_node_uuid_schema as schema_m


@pytest.fixture
def fresh_db(tmp_path):
    db = tmp_path / "x.db"
    conn = sqlite3.connect(db)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        conn.execute(f"CREATE TABLE {t} (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()
    return db


def _has_column(db, table, col):
    conn = sqlite3.connect(db)
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    conn.close()
    return any(r[1] == col for r in rows)


def test_schema_migration_adds_node_uuid_to_three_tables(fresh_db):
    schema_m.run(f"sqlite:///{fresh_db}", dry_run=False)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        assert _has_column(fresh_db, t, "node_uuid"), f"{t} missing node_uuid column"


def test_schema_migration_idempotent(fresh_db):
    schema_m.run(f"sqlite:///{fresh_db}", dry_run=False)
    # Re-run must not error and must not duplicate columns
    schema_m.run(f"sqlite:///{fresh_db}", dry_run=False)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        assert _has_column(fresh_db, t, "node_uuid")


def test_schema_migration_dry_run_does_not_mutate(fresh_db):
    schema_m.run(f"sqlite:///{fresh_db}", dry_run=True)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        assert not _has_column(fresh_db, t, "node_uuid")


def test_schema_migration_skips_missing_tables(tmp_path):
    """If a table doesn't exist (e.g. inventario_materiali_table missing in a stripped DB),
    the script should skip it cleanly and report the skip."""
    db = tmp_path / "partial.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id INTEGER PRIMARY KEY)")
    # No inventario or periodizzazione tables
    conn.commit()
    conn.close()
    report = schema_m.run(f"sqlite:///{db}", dry_run=False)
    assert "us_table" in report.tables_changed
    assert any("inventario_materiali_table" in s for s in report.tables_skipped)
    assert any("periodizzazione_table" in s for s in report.tables_skipped)


from pyarchinit_mini.database.migrations import (
    _2026_05_node_uuid_backfill as backfill_m,
)


@pytest.fixture
def db_with_schema(tmp_path):
    db = tmp_path / "y.db"
    conn = sqlite3.connect(db)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        conn.execute(f"CREATE TABLE {t} (id INTEGER PRIMARY KEY, node_uuid TEXT)")
        for i in range(10):
            conn.execute(f"INSERT INTO {t}(id) VALUES (?)", (i,))
    conn.commit()
    conn.close()
    return db


def test_backfill_populates_node_uuid_on_all_rows(db_with_schema):
    backfill_m.run(f"sqlite:///{db_with_schema}", dry_run=False)
    conn = sqlite3.connect(db_with_schema)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        nulls = conn.execute(f"SELECT COUNT(*) FROM {t} WHERE node_uuid IS NULL").fetchone()[0]
        assert nulls == 0, f"{t} still has {nulls} rows with NULL node_uuid"
    conn.close()


def test_backfill_idempotent(db_with_schema):
    backfill_m.run(f"sqlite:///{db_with_schema}", dry_run=False)
    conn = sqlite3.connect(db_with_schema)
    before = conn.execute("SELECT node_uuid FROM us_table ORDER BY id").fetchall()
    conn.close()
    backfill_m.run(f"sqlite:///{db_with_schema}", dry_run=False)
    conn = sqlite3.connect(db_with_schema)
    after = conn.execute("SELECT node_uuid FROM us_table ORDER BY id").fetchall()
    conn.close()
    assert before == after, "UUIDs must be preserved across re-runs"


def test_backfill_dry_run_does_not_mutate(db_with_schema):
    backfill_m.run(f"sqlite:///{db_with_schema}", dry_run=True)
    conn = sqlite3.connect(db_with_schema)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        nulls = conn.execute(f"SELECT COUNT(*) FROM {t} WHERE node_uuid IS NULL").fetchone()[0]
        assert nulls == 10
    conn.close()
