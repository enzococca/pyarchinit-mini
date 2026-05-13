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
