"""
Verify upgrade_legacy_schema picks up pottery_table:
- Existing legacy rows preserved
- Sync columns added with backfill
- Missing legacy table created from scratch on a DB without pottery
"""
import shutil
import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

from pyarchinit_mini.services.import_export_service import ImportExportService

FIXTURE = Path(__file__).parent.parent / "fixtures" / "legacy_with_pottery.sqlite"


@pytest.fixture
def legacy_db(tmp_path):
    dst = tmp_path / "legacy.sqlite"
    shutil.copy(FIXTURE, dst)
    return dst


def test_upgrade_preserves_pottery_rows(legacy_db):
    db_url = f"sqlite:///{legacy_db}"
    stats = ImportExportService.upgrade_legacy_schema(db_url)
    assert "pottery_table" in stats.get("added_per_table", {}) or \
           "pottery_table" in stats.get("created_tables", [])
    # Re-open and verify rows survived + sync cols present
    conn = sqlite3.connect(str(legacy_db))
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id_rep, sito, id_number FROM pottery_table ORDER BY id_rep"
    ).fetchall()
    assert rows == [(1, "Castelseprio", 101), (2, "Castelseprio", 102)]
    cols = [r[1] for r in cur.execute("PRAGMA table_info(pottery_table)").fetchall()]
    for sync in ("entity_uuid", "version_number", "sync_status",
                 "created_at", "updated_at"):
        assert sync in cols, f"Missing sync column {sync}"
    # entity_uuid backfilled non-null
    null_uuids = cur.execute(
        "SELECT COUNT(*) FROM pottery_table WHERE entity_uuid IS NULL"
    ).fetchone()[0]
    assert null_uuids == 0
    conn.close()


def test_upgrade_creates_pottery_when_missing(tmp_path):
    """A legacy DB that lacks pottery_table entirely should get it created."""
    db_path = tmp_path / "no_pottery.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY, sito TEXT)")
    conn.execute("INSERT INTO site_table VALUES (1, 'TestSite')")
    conn.commit()
    conn.close()

    db_url = f"sqlite:///{db_path}"
    stats = ImportExportService.upgrade_legacy_schema(db_url)
    assert "pottery_table" in stats.get("created_tables", []) or \
           stats.get("tables_created", 0) > 0

    engine = create_engine(db_url)
    insp = inspect(engine)
    assert "pottery_table" in insp.get_table_names()
