import os
import time
from pathlib import Path

import pytest


@pytest.fixture
def backup_svc(db_manager, tmp_path, monkeypatch):
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    from pyarchinit_mini.services.backup_service import BackupService
    return BackupService(db_manager)


def test_create_backup_now(backup_svc):
    info = backup_svc.create_backup_now()
    assert Path(info["path"]).exists()
    assert info["size_bytes"] > 0
    assert info["format"] in ("sqlite", "json", "pg_dump")


def test_list_backups_returns_sorted_desc(backup_svc):
    backup_svc.create_backup_now()
    time.sleep(1)  # ensure distinct mtimes
    backup_svc.create_backup_now()
    items = backup_svc.list_backups()
    assert len(items) == 2
    assert items[0]["created_at"] >= items[1]["created_at"]


def test_delete_backup(backup_svc):
    info = backup_svc.create_backup_now()
    filename = Path(info["path"]).name
    assert backup_svc.delete_backup(filename) is True
    assert not Path(info["path"]).exists()
    assert backup_svc.delete_backup(filename) is False  # second delete returns False


def test_delete_rejects_path_traversal(backup_svc):
    """Deleting must reject filenames with .. or absolute paths."""
    assert backup_svc.delete_backup("../etc/passwd") is False
    assert backup_svc.delete_backup("/etc/passwd") is False


def test_enforce_retention(backup_svc):
    # Create 5 fake backup files, set keep_last=3 — only 3 should survive.
    for i in range(5):
        backup_svc.create_backup_now()
        time.sleep(0.1)
    backup_svc._enforce_retention(keep_last=3)
    assert len(backup_svc.list_backups()) == 3


def test_default_schedule(backup_svc):
    sched = backup_svc.get_schedule()
    assert sched == {"enabled": False, "frequency": "weekly", "keep_last": 7}


def test_set_schedule_roundtrip(backup_svc):
    backup_svc.set_schedule(enabled=True, frequency="daily", keep_last=14)
    sched = backup_svc.get_schedule()
    assert sched == {"enabled": True, "frequency": "daily", "keep_last": 14}


def test_due_for_backup_no_previous_backup(backup_svc):
    # With backup_enabled and no prior backups, due_for_backup returns True
    backup_svc.set_schedule(enabled=True, frequency="daily", keep_last=7)
    assert backup_svc.is_due_for_backup() is True


def test_due_for_backup_recent_backup_not_due(backup_svc):
    backup_svc.set_schedule(enabled=True, frequency="daily", keep_last=7)
    backup_svc.create_backup_now()
    assert backup_svc.is_due_for_backup() is False


def test_set_schedule_rejects_invalid_frequency(backup_svc):
    with pytest.raises(ValueError, match="frequency"):
        backup_svc.set_schedule(enabled=True, frequency="hourly", keep_last=7)


def test_set_schedule_rejects_negative_keep_last(backup_svc):
    with pytest.raises(ValueError, match="keep_last"):
        backup_svc.set_schedule(enabled=True, frequency="daily", keep_last=0)


def test_create_backup_now_postgres_pg_dump_missing_falls_back_to_json(backup_svc, monkeypatch):
    """When pg_dump is unavailable AND _create_backup returns None path,
    BackupService must fall back to an inline JSON snapshot instead of
    crashing with 'argument should be a str ... not NoneType'.
    """
    from unittest.mock import patch

    fake_url = "postgresql://user:pwd@host:5432/dbname"

    # Simulate _create_backup returning success=False, path=None (the failure
    # mode that caused the bug in v2.1.62)
    def _fake_create_backup(db_url, backup_dir=None):
        return {"success": False, "path": None, "message": "pg_dump not found"}

    # Simulate _python_json_snapshot writing a tiny file at the requested path
    def _fake_json_snapshot(db_url, snapshot_path):
        from pathlib import Path as _P
        _P(snapshot_path).write_text('{"tables": {}}')
        return {"success": True, "path": snapshot_path, "size_mb": 0.01, "message": "ok"}

    with patch(
        "pyarchinit_mini.services.import_export_service.ImportExportService._create_backup",
        side_effect=_fake_create_backup,
    ), patch(
        "pyarchinit_mini.services.import_export_service.ImportExportService._python_json_snapshot",
        side_effect=_fake_json_snapshot,
    ):
        info = backup_svc.create_backup_now(db_url=fake_url)

    assert info["format"] == "json"
    from pathlib import Path as _P
    assert _P(info["path"]).exists()


def test_create_backup_now_raises_when_both_pg_dump_and_json_fail(backup_svc):
    """If both pg_dump and JSON snapshot fail, BackupService raises a
    clear RuntimeError rather than silently returning a broken result.
    """
    from unittest.mock import patch
    fake_url = "postgresql://user:pwd@host:5432/dbname"

    def _fail_create_backup(db_url, backup_dir=None):
        return {"success": False, "path": None, "message": "pg_dump not found"}

    def _fail_json_snapshot(db_url, snapshot_path):
        return {"success": False, "path": None, "message": "DB unreachable"}

    with patch(
        "pyarchinit_mini.services.import_export_service.ImportExportService._create_backup",
        side_effect=_fail_create_backup,
    ), patch(
        "pyarchinit_mini.services.import_export_service.ImportExportService._python_json_snapshot",
        side_effect=_fail_json_snapshot,
    ):
        with pytest.raises(RuntimeError, match="JSON snapshot"):
            backup_svc.create_backup_now(db_url=fake_url)
