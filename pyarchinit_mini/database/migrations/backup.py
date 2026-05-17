"""Database backup utilities for pre-migration safety.

- SQLite: file copy via shutil.copy2 (preserves mtime)
- PostgreSQL: pg_dump -Fc (custom format, restorable via pg_restore)
- All backups catalogued in `<backups_dir>/_index.json` as a JSON array.
"""
import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class BackupRecord:
    original_url: str
    backup_path: Path
    timestamp: datetime
    size_bytes: int
    checksum: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["backup_path"] = str(self.backup_path)
        d["timestamp"] = self.timestamp.isoformat()
        return d


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _update_index(backups_dir: Path, rec: BackupRecord) -> None:
    idx = backups_dir / "_index.json"
    data = []
    if idx.exists():
        data = json.loads(idx.read_text(encoding="utf-8"))
    data.append(rec.to_dict())
    idx.write_text(json.dumps(data, indent=2), encoding="utf-8")


def backup_database(url: str, *, backups_dir: Path) -> BackupRecord:
    """Backup a database. Supports sqlite:/// and postgresql:// URLs."""
    backups_dir = Path(backups_dir)
    backups_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now()
    suffix = ts.strftime("%Y%m%d_%H%M%S")

    if url.startswith("sqlite"):
        src = Path(url.replace("sqlite:///", "", 1))
        dst = backups_dir / f"{src.name}.pre_vocab_alignment_{suffix}.db"
        shutil.copy2(src, dst)
    elif url.startswith("postgresql") or url.startswith("postgres"):
        parsed = urlparse(url)
        dbname = parsed.path.lstrip("/") or "db"
        dst = backups_dir / f"{dbname}.pre_vocab_alignment_{suffix}.dump"
        subprocess.run(
            ["pg_dump", "-Fc", "-d", url, "-f", str(dst)],
            check=True,
            capture_output=True,
        )
    else:
        raise ValueError(f"unsupported DB backend: {url}")

    rec = BackupRecord(
        original_url=url,
        backup_path=dst,
        timestamp=ts,
        size_bytes=dst.stat().st_size,
        checksum=_sha256(dst),
    )
    _update_index(backups_dir, rec)
    return rec
