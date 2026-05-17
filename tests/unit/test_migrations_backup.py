import sqlite3
from pathlib import Path
import pytest

from pyarchinit_mini.database.migrations.backup import backup_database, BackupRecord


@pytest.fixture
def tmp_sqlite(tmp_path):
    db = tmp_path / "src.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE t (id INTEGER)")
    conn.execute("INSERT INTO t VALUES (1)")
    conn.commit()
    conn.close()
    return db


def test_backup_sqlite_copies_file_and_records(tmp_sqlite, tmp_path):
    url = f"sqlite:///{tmp_sqlite}"
    rec = backup_database(url, backups_dir=tmp_path / "backups")
    assert isinstance(rec, BackupRecord)
    assert rec.backup_path.exists()
    assert rec.backup_path.suffix == ".db"
    assert rec.size_bytes > 0
    assert len(rec.checksum) == 64  # SHA-256 hex digest


def test_backup_index_file_updated(tmp_sqlite, tmp_path):
    url = f"sqlite:///{tmp_sqlite}"
    backup_database(url, backups_dir=tmp_path / "backups")
    backup_database(url, backups_dir=tmp_path / "backups")
    index = (tmp_path / "backups" / "_index.json").read_text()
    assert "src.db" in index
    # Should contain 2 entries after 2 backups
    import json
    data = json.loads(index)
    assert isinstance(data, list)
    assert len(data) == 2


def test_backup_unsupported_backend_raises(tmp_path):
    with pytest.raises(ValueError):
        backup_database("mongodb://localhost/foo", backups_dir=tmp_path / "b")
