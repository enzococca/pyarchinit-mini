"""
Create Harris Matrix Tool

Creates or updates a Harris Matrix for a site from provided stratigraphic relationships.
"""

import logging
from typing import Dict, Any, List, Optional
from .base_tool import BaseTool, ToolDescription

logger = logging.getLogger(__name__)


class CreateHarrisMatrixTool(BaseTool):
    """Create or update Harris Matrix relationships for a site"""

    def __init__(self, db_session, config):
        super().__init__(db_session, config)
        from pyarchinit_mini.database.manager import DatabaseManager
        from pyarchinit_mini.database.connection import DatabaseConnection
        from pyarchinit_mini.services.us_service import USService
        import os
        db_url = getattr(config, 'database_url', None) or os.getenv('DATABASE_URL', 'sqlite:///pyarchinit_mini.db')
        connection = DatabaseConnection.from_url(db_url)
        self.db_manager = DatabaseManager(connection)
        self.us_service = USService(self.db_manager)

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="create_harris_matrix",
            description=(
                "Create or update Harris Matrix stratigraphic relationships for a site. "
                "Accepts a list of relationships between stratigraphic units (US) and stores them "
                "in the database. Supports all standard Harris Matrix relationship types: "
                "copre/è coperto da, taglia/è tagliato da, si appoggia a/è appoggiato da, "
                "uguale a, si lega a, viene prima di/viene dopo."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "site_name": {
                        "type": "string",
                        "description": "Name of the archaeological site"
                    },
                    "relationships": {
                        "type": "array",
                        "description": "List of stratigraphic relationships to create",
                        "items": {
                            "type": "object",
                            "properties": {
                                "us_from": {
                                    "type": ["string", "integer"],
                                    "description": "Source US number"
                                },
                                "us_to": {
                                    "type": ["string", "integer"],
                                    "description": "Target US number"
                                },
                                "relationship_type": {
                                    "type": "string",
                                    "description": "Type of relationship (e.g. 'copre', 'taglia', 'uguale a', 'si lega a')"
                                }
                            },
                            "required": ["us_from", "us_to", "relationship_type"]
                        }
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "If true, delete existing relationships for the site before inserting (default: false)",
                        "default": False
                    }
                },
                "required": ["site_name", "relationships"]
            }
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            site_name = arguments.get("site_name")
            relationships = arguments.get("relationships", [])
            overwrite = arguments.get("overwrite", False)

            if not site_name:
                return self._format_error("site_name is required")
            if not relationships:
                return self._format_error("relationships list is required and cannot be empty")

            session = self.db_manager.get_session()
            created = 0
            skipped = 0
            errors = []

            try:
                from sqlalchemy import text

                if overwrite:
                    session.execute(
                        text("DELETE FROM us_relationships_table WHERE sito = :sito"),
                        {"sito": site_name}
                    )
                    session.commit()
                    logger.info(f"Deleted existing relationships for site {site_name}")

                for rel in relationships:
                    try:
                        us_from = str(rel["us_from"])
                        us_to = str(rel["us_to"])
                        rel_type = rel["relationship_type"]

                        # Check if relationship already exists
                        existing = session.execute(
                            text("""SELECT id_relationship FROM us_relationships_table
                                    WHERE sito = :sito AND us_from = :us_from
                                    AND us_to = :us_to AND relationship_type = :rel_type"""),
                            {"sito": site_name, "us_from": us_from,
                             "us_to": us_to, "rel_type": rel_type}
                        ).fetchone()

                        if existing:
                            skipped += 1
                            continue

                        from datetime import datetime
                        import uuid
                        session.execute(
                            text("""INSERT INTO us_relationships_table
                                    (sito, us_from, us_to, relationship_type,
                                     created_at, updated_at, version_number, sync_status, entity_uuid)
                                    VALUES (:sito, :us_from, :us_to, :rel_type,
                                            :created_at, :updated_at, 1, 'new', :uuid)"""),
                            {
                                "sito": site_name,
                                "us_from": us_from,
                                "us_to": us_to,
                                "rel_type": rel_type,
                                "created_at": datetime.now(),
                                "updated_at": datetime.now(),
                                "uuid": str(uuid.uuid4())
                            }
                        )
                        created += 1

                    except Exception as e:
                        errors.append(f"Rel {rel.get('us_from')}→{rel.get('us_to')}: {str(e)}")

                session.commit()

            finally:
                session.close()

            result = {
                "site_name": site_name,
                "created": created,
                "skipped": skipped,
                "errors": errors
            }

            if errors:
                return self._format_success(
                    result=result,
                    message=f"Created {created} relationships ({skipped} skipped, {len(errors)} errors)"
                )
            return self._format_success(
                result=result,
                message=f"Successfully created {created} relationships for site '{site_name}' ({skipped} already existed)"
            )

        except Exception as e:
            logger.error(f"CreateHarrisMatrixTool error: {str(e)}", exc_info=True)
            return self._format_error(f"Failed to create Harris Matrix: {str(e)}")
