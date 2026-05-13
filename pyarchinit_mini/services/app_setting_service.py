"""AppSetting service — Fernet-encrypted key/value runtime config."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import List, Optional

from ..database.manager import DatabaseManager
from ..models.app_setting import AppSetting

logger = logging.getLogger(__name__)


def _get_secret_key_path() -> Path:
    """Return path to ~/.pyarchinit_mini/secret.key (honoring $PYARCHINIT_HOME)."""
    base = os.environ.get("PYARCHINIT_HOME", str(Path.home() / ".pyarchinit_mini"))
    return Path(base) / "secret.key"


def _load_or_create_fernet():
    """Load Fernet master key from disk, generating if missing.

    Returns (Fernet, available). When cryptography is missing, returns (None, False)
    — callers must fall back to plain-text storage with a warning.
    """
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        logger.warning("cryptography not installed; AppSetting secrets stored in plaintext")
        return None, False

    key_path = _get_secret_key_path()
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if not key_path.exists():
        key = Fernet.generate_key()
        key_path.write_bytes(key)
        os.chmod(key_path, 0o600)
    else:
        key = key_path.read_bytes()
    return Fernet(key), True


class AppSettingService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._fernet, self._crypto_available = _load_or_create_fernet()

    def _encrypt(self, plaintext: str) -> str:
        if not self._crypto_available:
            return plaintext
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("ascii")

    def _decrypt(self, ciphertext: str) -> str:
        if not self._crypto_available:
            return ciphertext
        try:
            return self._fernet.decrypt(ciphertext.encode("ascii")).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to decrypt setting value: {e}")
            return ""

    def get(self, key: str) -> Optional[str]:
        with self.db_manager.connection.get_session() as session:
            row = session.query(AppSetting).filter(AppSetting.key == key).first()
            if row is None:
                return None
            if row.is_secret and row.value:
                return self._decrypt(row.value)
            return row.value

    def set(
        self,
        key: str,
        value: str,
        is_secret: bool = False,
        description: Optional[str] = None,
    ) -> AppSetting:
        stored = self._encrypt(value) if is_secret and value else value
        with self.db_manager.connection.get_session() as session:
            row = session.query(AppSetting).filter(AppSetting.key == key).first()
            if row is None:
                row = AppSetting(
                    key=key, value=stored, is_secret=is_secret,
                    description=description,
                )
                session.add(row)
            else:
                row.value = stored
                row.is_secret = is_secret
                if description is not None:
                    row.description = description
            session.flush()
            session.refresh(row)
            session.expunge(row)
            return row

    def list_settings(self) -> List[AppSetting]:
        with self.db_manager.connection.get_session() as session:
            rows = session.query(AppSetting).order_by(AppSetting.key).all()
            for r in rows:
                session.expunge(r)
            return rows

    def delete(self, key: str) -> bool:
        with self.db_manager.connection.get_session() as session:
            row = session.query(AppSetting).filter(AppSetting.key == key).first()
            if row is None:
                return False
            session.delete(row)
            return True
