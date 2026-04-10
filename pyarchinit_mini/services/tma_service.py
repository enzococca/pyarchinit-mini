"""
TMA Service — manages tma_materiali_archeologici (master) and
tma_materiali_ripetibili (detail) records.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import or_

from pyarchinit_mini.models.tma import TmaMaterialiArcheologici, TmaMaterialiRipetibili

logger = logging.getLogger(__name__)


class TMAService:
    """Service for TMA records (master + detail)."""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    # ---------------- Master records ----------------

    def list_tma(self, page: int = 1, size: int = 50, search: str = '',
                 sito: str = '') -> List[Dict[str, Any]]:
        """List TMA master records with optional filters."""
        try:
            with self.db_manager.connection.get_session() as session:
                q = session.query(TmaMaterialiArcheologici)
                if sito:
                    q = q.filter(TmaMaterialiArcheologici.sito == sito)
                if search:
                    pat = f"%{search}%"
                    q = q.filter(or_(
                        TmaMaterialiArcheologici.sito.ilike(pat),
                        TmaMaterialiArcheologici.cassetta.ilike(pat),
                        TmaMaterialiArcheologici.inventario.ilike(pat),
                        TmaMaterialiArcheologici.ogtm.ilike(pat),
                        TmaMaterialiArcheologici.localita.ilike(pat),
                    ))
                q = q.order_by(TmaMaterialiArcheologici.id.desc())
                offset = (page - 1) * size
                rows = q.offset(offset).limit(size).all()
                return [r.to_dict() for r in rows]
        except Exception as e:
            logger.error(f"list_tma failed: {e}")
            return []

    def count_tma(self, search: str = '', sito: str = '') -> int:
        try:
            with self.db_manager.connection.get_session() as session:
                q = session.query(TmaMaterialiArcheologici)
                if sito:
                    q = q.filter(TmaMaterialiArcheologici.sito == sito)
                if search:
                    pat = f"%{search}%"
                    q = q.filter(or_(
                        TmaMaterialiArcheologici.sito.ilike(pat),
                        TmaMaterialiArcheologici.cassetta.ilike(pat),
                        TmaMaterialiArcheologici.inventario.ilike(pat),
                        TmaMaterialiArcheologici.ogtm.ilike(pat),
                    ))
                return q.count()
        except Exception:
            return 0

    def get_tma(self, tma_id: int) -> Optional[Dict[str, Any]]:
        try:
            with self.db_manager.connection.get_session() as session:
                row = session.query(TmaMaterialiArcheologici).filter(
                    TmaMaterialiArcheologici.id == tma_id).first()
                return row.to_dict() if row else None
        except Exception as e:
            logger.error(f"get_tma failed: {e}")
            return None

    def create_tma(self, data: Dict[str, Any]) -> Optional[int]:
        try:
            with self.db_manager.connection.get_session() as session:
                # Filter only valid model fields
                valid_keys = {c.name for c in TmaMaterialiArcheologici.__table__.columns}
                clean = {k: v for k, v in data.items() if k in valid_keys and v is not None and v != ''}
                row = TmaMaterialiArcheologici(**clean)
                session.add(row)
                session.flush()
                tma_id = row.id
                session.commit()
                return tma_id
        except Exception as e:
            logger.error(f"create_tma failed: {e}")
            return None

    def update_tma(self, tma_id: int, data: Dict[str, Any]) -> bool:
        try:
            with self.db_manager.connection.get_session() as session:
                row = session.query(TmaMaterialiArcheologici).filter(
                    TmaMaterialiArcheologici.id == tma_id).first()
                if not row:
                    return False
                valid_keys = {c.name for c in TmaMaterialiArcheologici.__table__.columns}
                for k, v in data.items():
                    if k in valid_keys and k != 'id':
                        setattr(row, k, v if v != '' else None)
                session.commit()
                return True
        except Exception as e:
            logger.error(f"update_tma failed: {e}")
            return False

    def delete_tma(self, tma_id: int) -> bool:
        try:
            with self.db_manager.connection.get_session() as session:
                # Delete detail rows first
                session.query(TmaMaterialiRipetibili).filter(
                    TmaMaterialiRipetibili.id_tma == tma_id).delete()
                row = session.query(TmaMaterialiArcheologici).filter(
                    TmaMaterialiArcheologici.id == tma_id).first()
                if row:
                    session.delete(row)
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"delete_tma failed: {e}")
            return False

    # ---------------- Detail (repetitive) records ----------------

    def list_materials(self, tma_id: int) -> List[Dict[str, Any]]:
        try:
            with self.db_manager.connection.get_session() as session:
                rows = session.query(TmaMaterialiRipetibili).filter(
                    TmaMaterialiRipetibili.id_tma == tma_id).order_by(
                    TmaMaterialiRipetibili.id).all()
                return [r.to_dict() for r in rows]
        except Exception as e:
            logger.error(f"list_materials failed: {e}")
            return []

    def add_material(self, tma_id: int, data: Dict[str, Any]) -> Optional[int]:
        try:
            with self.db_manager.connection.get_session() as session:
                valid_keys = {c.name for c in TmaMaterialiRipetibili.__table__.columns}
                clean = {k: v for k, v in data.items() if k in valid_keys and v is not None and v != ''}
                clean['id_tma'] = tma_id
                # Convert peso to float if present
                if 'peso' in clean:
                    try:
                        clean['peso'] = float(clean['peso'])
                    except (ValueError, TypeError):
                        clean.pop('peso', None)
                row = TmaMaterialiRipetibili(**clean)
                session.add(row)
                session.flush()
                rid = row.id
                session.commit()
                return rid
        except Exception as e:
            logger.error(f"add_material failed: {e}")
            return None

    def update_material(self, mat_id: int, data: Dict[str, Any]) -> bool:
        try:
            with self.db_manager.connection.get_session() as session:
                row = session.query(TmaMaterialiRipetibili).filter(
                    TmaMaterialiRipetibili.id == mat_id).first()
                if not row:
                    return False
                valid_keys = {c.name for c in TmaMaterialiRipetibili.__table__.columns}
                for k, v in data.items():
                    if k in valid_keys and k not in ('id', 'id_tma'):
                        if k == 'peso' and v not in (None, ''):
                            try:
                                v = float(v)
                            except (ValueError, TypeError):
                                continue
                        setattr(row, k, v if v != '' else None)
                session.commit()
                return True
        except Exception as e:
            logger.error(f"update_material failed: {e}")
            return False

    def delete_material(self, mat_id: int) -> bool:
        try:
            with self.db_manager.connection.get_session() as session:
                row = session.query(TmaMaterialiRipetibili).filter(
                    TmaMaterialiRipetibili.id == mat_id).first()
                if row:
                    session.delete(row)
                    session.commit()
                    return True
                return False
        except Exception:
            return False

    # ---------------- Helpers ----------------

    def get_distinct_sites(self) -> List[str]:
        try:
            with self.db_manager.connection.get_session() as session:
                rows = session.query(TmaMaterialiArcheologici.sito).filter(
                    TmaMaterialiArcheologici.sito.isnot(None)).distinct().all()
                return sorted([r[0] for r in rows if r[0]])
        except Exception:
            return []
