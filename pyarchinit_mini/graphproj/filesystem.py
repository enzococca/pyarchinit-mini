"""Filesystem helpers: atomic write + per-site flock + slugify."""
from __future__ import annotations

import re
import sys
import unicodedata
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

DEFAULT_PARADATA_ROOT = Path("data/paradata")


def slugify(name: str) -> str:
    if not name or not name.strip():
        raise ValueError("name cannot be empty")
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    s = folded.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if not s:
        raise ValueError(f"name slugifies to empty: {name!r}")
    return s


def paradata_dir(site: str, *, root: Optional[Path] = None) -> Path:
    base = Path(root) if root else DEFAULT_PARADATA_ROOT
    return base / slugify(site)


def atomic_write(content: str, target: Path, *, encoding: str = "utf-8") -> None:
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(content, encoding=encoding)
    tmp.replace(target)


@contextmanager
def paradata_flock(site: str, *, root: Optional[Path] = None) -> Iterator[None]:
    d = paradata_dir(site, root=root)
    d.mkdir(parents=True, exist_ok=True)
    lock_path = d / ".paradata.lock"
    fp = lock_path.open("a+")
    try:
        if sys.platform == "win32":
            import msvcrt
            msvcrt.locking(fp.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                fp.seek(0)
                msvcrt.locking(fp.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
    finally:
        fp.close()
