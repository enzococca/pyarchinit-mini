"""Resolve the Flask session signing key for this installation.

The key signs every session cookie and, through Flask-WTF, every CSRF token,
so it must be unique per installation and never live in the repository.

Precedence (there is deliberately no silent third case):

1. ``FLASK_SECRET_KEY`` or ``SECRET_KEY`` environment variable, trimmed,
   non-empty and not a known placeholder value.
2. A per-installation key file ``<PYARCHINIT_HOME or ~/.pyarchinit_mini>/flask_secret.key``:
   read if present, otherwise generated once with ``secrets.token_urlsafe``
   and written with mode 0600, so it is private to the OS user and stable
   across restarts even for users who never set an environment variable.
3. If that file can neither be read nor created, ``RuntimeError`` is raised
   naming the path and the environment variable to set instead, and the
   application does not start.
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Optional

ENV_VARS = ("FLASK_SECRET_KEY", "SECRET_KEY")
KEY_FILENAME = "flask_secret.key"
# Values that are documentation samples, not secrets.
PLACEHOLDERS = frozenset({
    "your-secret-key-here",
    "your-secret-key",
    "change-this-in-production",
    "changeme",
    "change-me",
    "secret",
})


def pyarchinit_home() -> Path:
    """Data folder: ``$PYARCHINIT_HOME`` if set, else ``~/.pyarchinit_mini``."""
    return Path(os.environ.get("PYARCHINIT_HOME") or (Path.home() / ".pyarchinit_mini"))


def secret_key_path() -> Path:
    return pyarchinit_home() / KEY_FILENAME


def _from_env() -> Optional[str]:
    for var in ENV_VARS:
        value = (os.environ.get(var) or "").strip()
        if value and value.lower() not in PLACEHOLDERS:
            return value
    return None


def _write_private(path: Path, key: str) -> None:
    """Create ``path`` with mode 0600 and write ``key``; never clobber a non-empty file."""
    try:
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        # Created concurrently (e.g. a second worker booting) or an empty leftover.
        existing = path.read_text(encoding="utf-8").strip()
        if existing:
            return
        fd = os.open(str(path), os.O_WRONLY | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(key + "\n")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass  # non-POSIX filesystems: the owner-only create above already applied


def resolve_secret_key() -> str:
    env_key = _from_env()
    if env_key:
        return env_key

    path = secret_key_path()
    try:
        if path.exists():
            existing = path.read_text(encoding="utf-8").strip()
            if existing:
                return existing
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_private(path, secrets.token_urlsafe(48))
        return path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise RuntimeError(
            f"pyarchinit-mini cannot read or create the session secret-key file {path} "
            f"({exc.strerror or exc}). Make that folder writable for this user, "
            f"or set the FLASK_SECRET_KEY environment variable."
        ) from exc
