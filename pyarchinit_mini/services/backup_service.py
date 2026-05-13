"""BackupService — DB dumps with retention, plus schedule via AppSetting."""
from __future__ import annotations

import json
import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..database.manager import DatabaseManager

logger = logging.getLogger(__name__)


def _backups_dir() -> Path:
    base = os.environ.get("PYARCHINIT_HOME", str(Path.home() / ".pyarchinit_mini"))
    d = Path(base) / "backups"
    d.mkdir(parents=True, exist_ok=True)
    return d


class BackupService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    # ---------- Create ----------
    def create_backup_now(self, db_url: Optional[str] = None) -> Dict[str, Any]:
        from .import_export_service import ImportExportService

        if db_url is None:
            db_url = str(self.db_manager.connection.engine.url)

        backups = _backups_dir()
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")

        if db_url.startswith("sqlite:///"):
            src = db_url.replace("sqlite:///", "", 1)
            path = backups / f"pyarchinit_backup_{ts}.sqlite"
            shutil.copy(src, path)
            fmt = "sqlite"
        elif db_url.startswith("postgresql"):
            # Try pg_dump first via ImportExportService._create_backup
            result = ImportExportService._create_backup(db_url, backup_dir=str(backups))
            path = Path(result["path"])
            fmt = result.get("format", "pg_dump")
        else:
            # JSON snapshot fallback for any other dialect
            path = backups / f"pyarchinit_backup_{ts}.json"
            snapshot = ImportExportService._python_json_snapshot(db_url, str(path))
            fmt = "json"
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(snapshot, fh, default=str, indent=2)

        return {
            "path": str(path),
            "size_bytes": path.stat().st_size,
            "format": fmt,
            "created_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
        }

    # ---------- List ----------
    def list_backups(self) -> List[Dict[str, Any]]:
        backups = _backups_dir()
        items = []
        for f in backups.iterdir():
            if not f.is_file():
                continue
            if not f.name.startswith("pyarchinit_backup_"):
                continue
            st = f.stat()
            items.append({
                "filename": f.name,
                "path": str(f),
                "size_bytes": st.st_size,
                "created_at": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
            })
        items.sort(key=lambda x: x["created_at"], reverse=True)
        return items

    # ---------- Delete ----------
    def delete_backup(self, filename: str) -> bool:
        if ".." in filename or "/" in filename or filename.startswith("."):
            return False
        path = _backups_dir() / filename
        if not path.exists() or not path.is_file():
            return False
        if not path.name.startswith("pyarchinit_backup_"):
            return False
        path.unlink()
        return True

    # ---------- Retention ----------
    def _enforce_retention(self, keep_last: Optional[int] = None) -> int:
        if keep_last is None:
            from .app_setting_service import AppSettingService
            svc = AppSettingService(self.db_manager)
            try:
                keep_last = int(svc.get("backup_keep_last") or 7)
            except (TypeError, ValueError):
                keep_last = 7
        items = self.list_backups()
        deleted = 0
        for old in items[keep_last:]:
            if self.delete_backup(old["filename"]):
                deleted += 1
        return deleted
