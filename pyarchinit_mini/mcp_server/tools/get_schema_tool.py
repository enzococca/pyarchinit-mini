
"""
Get Schema Tool - Database Schema Inspector for MCP

This tool provides detailed database schema information including:
- Table structure with field names and types
- Required vs optional fields
- Primary keys and auto-increment fields
- Foreign key relationships
- Unique constraints
- Sample values for enum/choice fields
"""

import logging
import os
from sqlalchemy import inspect, Table, MetaData
from sqlalchemy.dialects import sqlite, postgresql
from typing import Optional
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager

logger = logging.getLogger(__name__)


def get_schema(
    table: Optional[str] = None,
    include_constraints: bool = True,
    include_sample_values: bool = False
) -> dict:
    """
    Get database schema information for PyArchInit tables.

    Args:
        table: Specific table name (None = all tables).
               Supports ALL database tables including: site_table, us_table,
               inventario_materiali_table, datazioni_table, us_relationships_table,
               periodizzazione tables, media tables, thesaurus tables, users table, etc.
        include_constraints: Include foreign keys, unique constraints, etc.
        include_sample_values: Include example values for specific fields

    Returns:
        dict: Schema information with structure:
        {
            "database_type": "sqlite" | "postgresql",
            "tables": {
                "table_name": {
                    "fields": {
                        "field_name": {
                            "type": "VARCHAR(100)" | "INTEGER" | etc.,
                            "required": True | False,
                            "primary_key": True | False,
                            "auto_increment": True | False,
                            "unique": True | False,
                            "default": value | None,
                            "sample_values": [...]  # if include_sample_values=True
                        }
                    },
                    "foreign_keys": [...],  # if include_constraints=True
                    "unique_constraints": [...]  # if include_constraints=True
                }
            }
        }

    Example:
        # Get schema for all tables
        schema = get_schema()

        # Get schema for US table only
        schema = get_schema(table="us_table")

        # Get schema with sample values
        schema = get_schema(table="us_table", include_sample_values=True)
    """
    try:
        # Get database connection - use config default if DATABASE_URL not set
        from pyarchinit_mini.mcp_server.config import _get_default_database_url
        database_url = os.getenv("DATABASE_URL") or _get_default_database_url()
        db_connection = DatabaseConnection(database_url)
        db_manager = DatabaseManager(db_connection)
        engine = db_connection.engine
        inspector = inspect(engine)

        # Detect database type
        db_type = "sqlite" if "sqlite" in str(engine.url) else "postgresql"

        # Get all available tables in the database
        all_tables = inspector.get_table_names()

        # If specific table requested, validate it exists
        if table:
            if table not in all_tables:
                return {
                    "success": False,
                    "error": "table_not_found",
                    "message": f"Table '{table}' does not exist in database",
                    "available_tables": all_tables
                }
            tables_to_inspect = [table]
        else:
            # Return all tables
            tables_to_inspect = all_tables

        result = {
            "database_type": db_type,
            "tables": {}
        }

        for table_name in tables_to_inspect:
            table_info = {
                "fields": {},
                "foreign_keys": [] if include_constraints else None,
                "unique_constraints": [] if include_constraints else None
            }

            # Get columns
            columns = inspector.get_columns(table_name)
            pk_constraint = inspector.get_pk_constraint(table_name)
            pk_columns = pk_constraint.get('constrained_columns', []) if pk_constraint else []

            for col in columns:
                field_name = col['name']
                field_type = str(col['type'])

                # Determine if field is required (NOT NULL)
                is_required = not col.get('nullable', True)

                # Determine if primary key
                is_pk = field_name in pk_columns

                # Determine if auto-increment (for SQLite and PostgreSQL)
                is_autoincrement = False
                if is_pk:
                    if db_type == "sqlite":
                        # In SQLite, INTEGER PRIMARY KEY is auto-increment
                        is_autoincrement = "INTEGER" in field_type.upper()
                    else:  # postgresql
                        # Check for SERIAL or SEQUENCE
                        is_autoincrement = col.get('autoincrement', False) or \
                                         'SERIAL' in field_type.upper() or \
                                         col.get('default', '').startswith('nextval')

                # Get default value
                default = col.get('default')
                if default:
                    default = str(default)

                field_info = {
                    "type": field_type,
                    "required": is_required,
                    "primary_key": is_pk,
                    "auto_increment": is_autoincrement,
                    "default": default
                }

                # Add sample values for specific fields
                if include_sample_values:
                    field_info["sample_values"] = _get_sample_values(
                        table_name, field_name, field_type
                    )

                table_info["fields"][field_name] = field_info

            # Get foreign keys
            if include_constraints:
                fks = inspector.get_foreign_keys(table_name)
                for fk in fks:
                    table_info["foreign_keys"].append({
                        "constrained_columns": fk.get('constrained_columns', []),
                        "referred_table": fk.get('referred_table'),
                        "referred_columns": fk.get('referred_columns', [])
                    })

                # Get unique constraints
                unique_constraints = inspector.get_unique_constraints(table_name)
                for uc in unique_constraints:
                    table_info["unique_constraints"].append({
                        "name": uc.get('name'),
                        "columns": uc.get('column_names', [])
                    })

            result["tables"][table_name] = table_info

        return {
            "success": True,
            "schema": result
        }

    except Exception as e:
        logger.error(f"Error getting schema: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get database schema: {str(e)}"
        }


def _get_sample_values(table_name: str, field_name: str, field_type: str) -> list:
    """
    Get sample values for specific fields (mainly for enum/choice fields).

    Returns predefined sample values based on field name and table.
    """
    # Sample values for common choice fields
    samples = {
        "us_table": {
            "unita_tipo": ["US", "USM", "USD", "USV", "USVA", "USVB", "USVC", "SF", "VSF", "TU", "DOC"],
            "definizione_stratigrafica": ["Strato", "Struttura", "Riempimento", "Taglio", "Interfaccia"],
            "formazione": ["Naturale", "Antropico"],
            "stato_di_conservazione": ["Ottimo", "Buono", "Mediocre", "Cattivo"],
            "periodo": ["Preistorico", "Etrusco", "Romano", "Medievale", "Moderno", "Contemporaneo"]
        },
        "site_table": {
            "tipologia": ["Insediamento", "Necropoli", "Santuario", "Altro"]
        },
        "inventario_materiali_table": {
            "tipo_reperto": ["Ceramica", "Metallo", "Vetro", "Osso", "Pietra", "Altro"],
            "stato_conservazione": ["Integro", "Frammentario", "Lacunoso"]
        }
    }

    if table_name in samples and field_name in samples[table_name]:
        return samples[table_name][field_name]

    return []
