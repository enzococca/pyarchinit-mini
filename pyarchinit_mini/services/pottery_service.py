"""Pottery records service (CRUD + listing + stats)."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, or_

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

    # ---------- Listing & Filtering ----------
    _FILTERABLE = ("sito", "area", "us", "form", "fabric", "ware", "material")

    def _apply_filters(self, q, filters: Optional[Dict[str, Any]]):
        if not filters:
            return q
        for k in self._FILTERABLE:
            v = filters.get(k)
            if v in (None, ""):
                continue
            col = getattr(Pottery, k)
            q = q.filter(col == v)
        q_text = filters.get("q")
        if q_text:
            like = f"%{q_text}%"
            q = q.filter(
                or_(
                    Pottery.form.ilike(like),
                    Pottery.specific_form.ilike(like),
                    Pottery.fabric.ilike(like),
                    Pottery.ware.ilike(like),
                    Pottery.note.ilike(like),
                    Pottery.descrip_ex_deco.ilike(like),
                    Pottery.descrip_in_deco.ilike(like),
                )
            )
        return q

    def get_all_pottery(
        self, page: int = 1, size: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Pottery], int]:
        with self.db_manager.connection.get_session() as session:
            q = session.query(Pottery)
            q = self._apply_filters(q, filters)
            total = q.count()
            items = (
                q.order_by(Pottery.id_rep.desc())
                .offset((page - 1) * size)
                .limit(size)
                .all()
            )
            for it in items:
                session.expunge(it)
            return items, total

    def count_pottery(self, filters: Optional[Dict[str, Any]] = None) -> int:
        with self.db_manager.connection.get_session() as session:
            q = session.query(Pottery)
            q = self._apply_filters(q, filters)
            return q.count()

    def search_pottery(self, q_text: str, page: int = 1, size: int = 10) -> List[Pottery]:
        items, _ = self.get_all_pottery(page=page, size=size, filters={"q": q_text})
        return items

    def get_pottery_by_site(self, sito: str, page: int = 1, size: int = 10) -> List[Pottery]:
        items, _ = self.get_all_pottery(page=page, size=size, filters={"sito": sito})
        return items

    def get_pottery_by_us(
        self, sito: str, area: Optional[str], us: int,
        page: int = 1, size: int = 10,
    ) -> List[Pottery]:
        items, _ = self.get_all_pottery(
            page=page, size=size,
            filters={"sito": sito, "area": area, "us": us},
        )
        return items

    def get_pottery_by_form(self, form: str, page: int = 1, size: int = 10) -> List[Pottery]:
        items, _ = self.get_all_pottery(page=page, size=size, filters={"form": form})
        return items

    # ---------- Stats ----------
    def _distribution(self, column_name: str, sito: Optional[str] = None) -> Dict[str, int]:
        with self.db_manager.connection.get_session() as session:
            col = getattr(Pottery, column_name)
            q = session.query(col, func.count(Pottery.id_rep)).group_by(col)
            if sito:
                q = q.filter(Pottery.sito == sito)
            return {k: c for k, c in q.all() if k is not None}

    def get_form_distribution(self, sito: Optional[str] = None) -> Dict[str, int]:
        return self._distribution("form", sito)

    def get_fabric_distribution(self, sito: Optional[str] = None) -> Dict[str, int]:
        return self._distribution("fabric", sito)

    def get_ware_distribution(self, sito: Optional[str] = None) -> Dict[str, int]:
        return self._distribution("ware", sito)

    def count_by_site(self) -> List[Dict[str, Any]]:
        with self.db_manager.connection.get_session() as session:
            rows = (
                session.query(Pottery.sito, func.count(Pottery.id_rep))
                .group_by(Pottery.sito)
                .all()
            )
            return [{"sito": s, "count": c} for s, c in rows]

    def calculate_mni(
        self, sito: str, area: Optional[str] = None, us: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Minimum Number of Individuals — sum of qty grouped by form+fabric+ware."""
        with self.db_manager.connection.get_session() as session:
            q = session.query(
                Pottery.form, Pottery.fabric, Pottery.ware,
                func.coalesce(func.sum(Pottery.qty), 0),
            ).filter(Pottery.sito == sito)
            if area:
                q = q.filter(Pottery.area == area)
            if us is not None:
                q = q.filter(Pottery.us == us)
            q = q.group_by(Pottery.form, Pottery.fabric, Pottery.ware)
            groups = [
                {"form": f, "fabric": fa, "ware": w, "mni": int(s or 0)}
                for f, fa, w, s in q.all()
            ]
            total = sum(g["mni"] for g in groups)
            return {"total": total, "groups": groups}
