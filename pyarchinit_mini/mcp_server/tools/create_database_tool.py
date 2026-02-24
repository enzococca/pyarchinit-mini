"""
Create Database Tool

Creates a new empty PyArchInit-Mini database (SQLite or PostgreSQL) with the full schema.
"""

import logging
import os
from typing import Dict, Any
from .base_tool import BaseTool, ToolDescription

logger = logging.getLogger(__name__)


class CreateDatabaseTool(BaseTool):
    """Create a new PyArchInit-Mini database with full schema"""

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="create_database",
            description=(
                "Create a new empty PyArchInit-Mini database with the complete schema. "
                "Supports SQLite (file-based) and PostgreSQL. "
                "Use this to initialize a fresh database for a new project."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "db_type": {
                        "type": "string",
                        "enum": ["sqlite", "postgresql"],
                        "description": "Database type to create",
                        "default": "sqlite"
                    },
                    "db_path": {
                        "type": "string",
                        "description": "Path for SQLite database file (e.g. /home/user/myproject.db). Required for sqlite."
                    },
                    "pg_host": {
                        "type": "string",
                        "description": "PostgreSQL host (default: localhost)",
                        "default": "localhost"
                    },
                    "pg_port": {
                        "type": "string",
                        "description": "PostgreSQL port (default: 5432)",
                        "default": "5432"
                    },
                    "pg_database": {
                        "type": "string",
                        "description": "PostgreSQL database name"
                    },
                    "pg_user": {
                        "type": "string",
                        "description": "PostgreSQL username"
                    },
                    "pg_password": {
                        "type": "string",
                        "description": "PostgreSQL password"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "If true, overwrite existing database (default: false)",
                        "default": False
                    }
                },
                "required": ["db_type"]
            }
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            db_type = arguments.get("db_type", "sqlite")
            overwrite = arguments.get("overwrite", False)

            from pyarchinit_mini.database.database_creator import create_empty_database

            if db_type == "sqlite":
                db_path = arguments.get("db_path")
                if not db_path:
                    return self._format_error("db_path is required for SQLite databases")

                db_path = os.path.abspath(os.path.expanduser(db_path))

                if os.path.exists(db_path) and not overwrite:
                    return self._format_error(
                        f"Database already exists at {db_path}. Set overwrite=true to replace it."
                    )

                logger.info(f"Creating SQLite database at {db_path}")
                result = create_empty_database("sqlite", db_path, overwrite=overwrite)

            elif db_type == "postgresql":
                host = arguments.get("pg_host", "localhost")
                port = arguments.get("pg_port", "5432")
                database = arguments.get("pg_database")
                user = arguments.get("pg_user")
                password = arguments.get("pg_password", "")

                if not all([database, user]):
                    return self._format_error("pg_database and pg_user are required for PostgreSQL")

                config = {
                    "host": host,
                    "port": int(port),
                    "database": database,
                    "username": user,
                    "password": password
                }

                logger.info(f"Creating PostgreSQL database {database} on {host}:{port}")
                result = create_empty_database("postgresql", config, overwrite=overwrite)

            else:
                return self._format_error(f"Unsupported db_type: {db_type}. Use 'sqlite' or 'postgresql'.")

            return self._format_success(
                result={
                    "db_type": result.get("db_type"),
                    "tables_created": result.get("tables_created"),
                    "message": result.get("message")
                },
                message=result.get("message", "Database created successfully")
            )

        except FileExistsError:
            return self._format_error("Database already exists. Set overwrite=true to replace it.")
        except Exception as e:
            logger.error(f"CreateDatabaseTool error: {str(e)}", exc_info=True)
            return self._format_error(f"Failed to create database: {str(e)}")
