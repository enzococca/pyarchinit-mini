"""
Universal search service for cross-table full-text search
"""

import logging
from typing import Dict, Any, List

from sqlalchemy import or_, func
from sqlalchemy.exc import SQLAlchemyError

from pyarchinit_mini.models.site import Site
from pyarchinit_mini.models.us import US
from pyarchinit_mini.models.inventario_materiali import InventarioMateriali
from pyarchinit_mini.models.user import User

logger = logging.getLogger(__name__)


class UniversalSearchService:
    """
    Provides cross-table search across sites, stratigraphic units,
    materials inventory, and users using a single database session.
    """

    def __init__(self, db_manager):
        """
        Args:
            db_manager: DatabaseManager instance with access to connection/sessions.
        """
        self.db_manager = db_manager

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search_all(self, query: str, limit_per_table: int = 20) -> Dict[str, Any]:
        """
        Search all major tables for *query* and return consolidated results.

        Args:
            query: Free-text search string (case-insensitive substring match).
            limit_per_table: Maximum number of rows returned per table.

        Returns:
            Dict with keys 'query', 'stats', 'sites', 'us', 'materials', 'users'.
        """
        pattern = f"%{query}%"

        try:
            with self.db_manager.connection.get_session() as session:
                # --- counts ------------------------------------------------
                site_count = self._count(session, Site, self._site_filters(pattern))
                us_count = self._count(session, US, self._us_filters(pattern))
                mat_count = self._count(session, InventarioMateriali, self._material_filters(pattern))
                user_count = self._count(session, User, self._user_filters(pattern))

                # --- limited result sets -----------------------------------
                sites = self._search_table(session, Site, self._site_filters(pattern), limit_per_table)
                us_list = self._search_table(session, US, self._us_filters(pattern), limit_per_table)
                materials = self._search_table(session, InventarioMateriali, self._material_filters(pattern), limit_per_table)
                users = self._search_table(session, User, self._user_filters(pattern), limit_per_table)

                total = site_count + us_count + mat_count + user_count

                return {
                    "query": query,
                    "stats": {
                        "sites": site_count,
                        "us": us_count,
                        "materials": mat_count,
                        "users": user_count,
                        "total": total,
                    },
                    "sites": sites,
                    "us": us_list,
                    "materials": materials,
                    "users": users,
                }
        except SQLAlchemyError as exc:
            logger.error("Universal search failed for query '%s': %s", query, exc)
            return {
                "query": query,
                "stats": {"sites": 0, "us": 0, "materials": 0, "users": 0, "total": 0},
                "sites": [],
                "us": [],
                "materials": [],
                "users": [],
            }
        except Exception as exc:
            logger.error("Unexpected error during universal search: %s", exc)
            return {
                "query": query,
                "stats": {"sites": 0, "us": 0, "materials": 0, "users": 0, "total": 0},
                "sites": [],
                "us": [],
                "materials": [],
                "users": [],
            }

    # ------------------------------------------------------------------
    # Filter builders (return list of column conditions for or_())
    # ------------------------------------------------------------------

    @staticmethod
    def _site_filters(pattern: str):
        return or_(
            Site.sito.ilike(pattern),
            Site.nazione.ilike(pattern),
            Site.regione.ilike(pattern),
            Site.comune.ilike(pattern),
            Site.provincia.ilike(pattern),
            Site.definizione_sito.ilike(pattern),
            Site.descrizione.ilike(pattern),
        )

    @staticmethod
    def _us_filters(pattern: str):
        return or_(
            US.sito.ilike(pattern),
            US.area.ilike(pattern),
            US.us.ilike(pattern),
            US.d_stratigrafica.ilike(pattern),
            US.d_interpretativa.ilike(pattern),
            US.descrizione.ilike(pattern),
            US.interpretazione.ilike(pattern),
            US.schedatore.ilike(pattern),
            US.datazione.ilike(pattern),
            US.osservazioni.ilike(pattern),
        )

    @staticmethod
    def _material_filters(pattern: str):
        return or_(
            InventarioMateriali.sito.ilike(pattern),
            InventarioMateriali.tipo_reperto.ilike(pattern),
            InventarioMateriali.definizione.ilike(pattern),
            InventarioMateriali.descrizione.ilike(pattern),
            InventarioMateriali.criterio_schedatura.ilike(pattern),
            InventarioMateriali.datazione_reperto.ilike(pattern),
        )

    @staticmethod
    def _user_filters(pattern: str):
        return or_(
            User.username.ilike(pattern),
            User.email.ilike(pattern),
            User.full_name.ilike(pattern),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _count(session, model, filters) -> int:
        """Return the number of rows matching *filters* using func.count()."""
        return session.query(func.count()).select_from(model).filter(filters).scalar() or 0

    @staticmethod
    def _search_table(session, model, filters, limit: int) -> List[Dict[str, Any]]:
        """Return up to *limit* rows as dicts."""
        rows = session.query(model).filter(filters).limit(limit).all()
        results: List[Dict[str, Any]] = []
        for row in rows:
            if hasattr(row, "to_dict"):
                results.append(row.to_dict())
            else:
                results.append(dict(row._mapping))
        return results
