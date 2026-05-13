"""Pottery records service (CRUD + listing + stats)."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..database.manager import DatabaseManager
from ..models.pottery import Pottery
from .pottery_dto import PotteryDTO

logger = logging.getLogger(__name__)

_POTTERY_COLUMNS = {c.name for c in Pottery.__table__.columns}


class PotteryService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    # ---------- CRUD ----------
    def create_pottery(self, data: Dict[str, Any]) -> Pottery:
        clean = self._validate_and_clean(data)
        if clean.get("id_number") is not None:
            self._validate_unique_sito_idnumber(clean["sito"], clean["id_number"])
        with self.db_manager.connection.get_session() as session:
            p = Pottery(**{k: v for k, v in clean.items() if k in _POTTERY_COLUMNS})
            session.add(p)
            session.flush()
            session.refresh(p)
            session.expunge(p)
        return p

    # ---------- Validation ----------
    def _validate_and_clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get("sito"):
            raise ValueError("sito is required")
        qty = data.get("qty")
        if qty is not None and qty != "":
            try:
                qi = int(qty)
            except (TypeError, ValueError):
                raise ValueError("qty must be an integer")
            if qi < 1:
                raise ValueError("qty must be >= 1")
            data["qty"] = qi
        return data

    def _validate_unique_sito_idnumber(
        self, sito: str, id_number: int, exclude_id: Optional[int] = None
    ) -> None:
        with self.db_manager.connection.get_session() as session:
            q = session.query(Pottery).filter(
                Pottery.sito == sito, Pottery.id_number == id_number
            )
            if exclude_id is not None:
                q = q.filter(Pottery.id_rep != exclude_id)
            existing = q.first()
            if existing is not None:
                raise ValueError(
                    f"Pottery with sito={sito!r} id_number={id_number} already exists"
                )

    # ---------- Read ----------
    def get_pottery_by_id(self, id_rep: int) -> Optional[Pottery]:
        with self.db_manager.connection.get_session() as session:
            p = session.query(Pottery).filter(Pottery.id_rep == id_rep).first()
            if p is not None:
                session.expunge(p)
            return p

    def get_pottery_dto_by_id(self, id_rep: int) -> Optional[PotteryDTO]:
        p = self.get_pottery_by_id(id_rep)
        return PotteryDTO.from_model(p) if p else None

    # ---------- Update / Delete ----------
    def update_pottery(self, id_rep: int, data: Dict[str, Any]) -> Pottery:
        # Pre-fetch current row (in its own session) to figure out new sito/id_number
        current = self.get_pottery_by_id(id_rep)
        if current is None:
            raise ValueError(f"Pottery id_rep={id_rep} not found")
        new_sito = data.get("sito", current.sito)
        new_idn = data.get("id_number", current.id_number)
        if new_idn is not None and (new_sito != current.sito or new_idn != current.id_number):
            self._validate_unique_sito_idnumber(new_sito, new_idn, exclude_id=id_rep)
        if "qty" in data and data["qty"] not in (None, ""):
            try:
                q = int(data["qty"])
            except (TypeError, ValueError):
                raise ValueError("qty must be an integer")
            if q < 1:
                raise ValueError("qty must be >= 1")
            data["qty"] = q
        with self.db_manager.connection.get_session() as session:
            p = session.query(Pottery).filter(Pottery.id_rep == id_rep).first()
            if p is None:
                raise ValueError(f"Pottery id_rep={id_rep} not found")
            for k, v in data.items():
                if k in _POTTERY_COLUMNS:
                    setattr(p, k, v)
            session.flush()
            session.refresh(p)
            session.expunge(p)
            return p

    def delete_pottery(self, id_rep: int) -> bool:
        with self.db_manager.connection.get_session() as session:
            p = session.query(Pottery).filter(Pottery.id_rep == id_rep).first()
            if p is None:
                return False
            session.delete(p)
            return True
