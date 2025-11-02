"""
Delete Data Tool - Database Record Deletion for MCP

This tool enables AI assistants to delete archaeological records from the database.
Features:
- Delete records by ID or by filter conditions
- Safety checks to prevent accidental mass deletion
- Foreign key cascade warnings
- Dry-run mode for validation
- Transaction safety (rollback on error)
- Works with both SQLite and PostgreSQL
- Returns number of deleted rows
"""

import logging
import os
from sqlalchemy import Table, MetaData, inspect, and_
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any, Optional
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager

logger = logging.getLogger(__name__)


def delete_data(
    table: str,
    record_id: Optional[int] = None,
    filters: Optional[Dict[str, Any]] = None,
    confirm_delete: bool = False,
    cascade_aware: bool = True
) -> dict:
    """
    Delete record(s) from a PyArchInit table.

    IMPORTANT: This operation is IRREVERSIBLE. Deleted data cannot be recovered.

    Args:
        table: Table name to delete from.
               Supports ALL database tables including: site_table, us_table,
               inventario_materiali_table, datazioni_table, us_relationships_table,
               periodizzazione tables, media tables, thesaurus tables, users table, etc.
        record_id: Primary key ID of specific record to delete.
                   If provided, deletes only this record.
                   Cannot be used together with filters.
        filters: Dictionary of field_name -> value conditions for filtering records.
                 Deletes ALL records matching these conditions.
                 Example: {"sito": "Test Site", "area": 99}
                 Cannot be used together with record_id.
        confirm_delete: REQUIRED for deletion. Set to True to confirm you want to delete.
                        If False, performs dry-run showing what would be deleted.
        cascade_aware: If True, checks for foreign key dependencies and warns
                       if deletion may affect related records (default: True).

    Returns:
        dict: Result with structure:
        {
            "success": True | False,
            "message": "Success/error message",
            "rows_deleted": <number of records deleted>,
            "cascade_warnings": [...] (if cascade_aware=True),
            "dry_run_info": {...} (if confirm_delete=False)
        }

    Examples:
        # Preview deletion (dry-run)
        result = delete_data(
            table="us_table",
            record_id=42,
            confirm_delete=False  # Just preview
        )

        # Delete a specific record by ID
        result = delete_data(
            table="us_table",
            record_id=42,
            confirm_delete=True  # Actually delete
        )

        # Delete all test records from a site
        result = delete_data(
            table="us_table",
            filters={"sito": "Test Site", "area": 99},
            confirm_delete=True
        )

    Safety Features:
        - confirm_delete=True is REQUIRED for actual deletion
        - Without confirmation, performs dry-run showing affected records
        - Checks for dependent records via foreign keys
        - Warns about potential cascade effects
        - Prevents deletion if it would violate foreign key constraints

    Notes:
        - Either record_id OR filters must be provided (not both, not neither)
        - Deletion is permanent and cannot be undone
        - Foreign key cascade behavior depends on database schema
        - Transaction is rolled back if any error occurs
    """
    try:
        # Validate that either record_id or filters is provided
        if record_id is None and filters is None:
            return {
                "success": False,
                "error": "missing_identifier",
                "message": "Either 'record_id' or 'filters' must be provided to identify records to delete"
            }

        if record_id is not None and filters is not None:
            return {
                "success": False,
                "error": "conflicting_identifiers",
                "message": "Cannot use both 'record_id' and 'filters' - choose one"
            }

        # Get database connection - use config default if DATABASE_URL not set
        from pyarchinit_mini.mcp_server.config import _get_default_database_url
        database_url = os.getenv("DATABASE_URL") or _get_default_database_url()
        db_connection = DatabaseConnection(database_url)
        db_manager = DatabaseManager(db_connection)
        engine = db_connection.engine
        metadata = MetaData()
        inspector = inspect(engine)

        # Validate table exists in database
        all_tables = inspector.get_table_names()
        if table not in all_tables:
            return {
                "success": False,
                "error": "table_not_found",
                "message": f"Table '{table}' does not exist in database",
                "available_tables": all_tables
            }

        # Reflect table structure
        table_obj = Table(table, metadata, autoload_with=engine)

        # Get primary key columns
        pk_constraint = inspector.get_pk_constraint(table)
        pk_columns = pk_constraint.get('constrained_columns', []) if pk_constraint else []

        # Build WHERE clause
        where_conditions = []
        if record_id is not None:
            # Delete by primary key
            if not pk_columns:
                return {
                    "success": False,
                    "error": "no_primary_key",
                    "message": f"Table '{table}' has no primary key defined"
                }
            pk_col = pk_columns[0]  # Use first primary key column
            where_conditions.append(getattr(table_obj.c, pk_col) == record_id)
        else:
            # Delete by filters
            columns = inspector.get_columns(table)
            column_names = [col['name'] for col in columns]

            for field_name, value in filters.items():
                if field_name not in column_names:
                    return {
                        "success": False,
                        "error": "unknown_filter_field",
                        "message": f"Filter field '{field_name}' does not exist in table '{table}'"
                    }
                where_conditions.append(getattr(table_obj.c, field_name) == value)

        where_clause = and_(*where_conditions) if len(where_conditions) > 1 else where_conditions[0]

        # Check if records exist and get them
        with engine.connect() as conn:
            records_to_delete = conn.execute(
                table_obj.select().where(where_clause)
            ).fetchall()

            if not records_to_delete:
                identifier = f"ID {record_id}" if record_id else f"filters {filters}"
                return {
                    "success": False,
                    "error": "no_records_found",
                    "message": f"No records found in {table} matching {identifier}"
                }

        # Check for foreign key dependencies if cascade_aware
        cascade_warnings = []
        if cascade_aware:
            # Get all tables that reference this table
            all_tables = inspector.get_table_names()
            for other_table in all_tables:
                if other_table == table:
                    continue

                try:
                    fks = inspector.get_foreign_keys(other_table)
                    for fk in fks:
                        if fk.get('referred_table') == table:
                            # This table references our table
                            constrained_cols = fk.get('constrained_columns', [])
                            referred_cols = fk.get('referred_columns', [])

                            # Check if there are dependent records
                            for record in records_to_delete:
                                for i, referred_col in enumerate(referred_cols):
                                    if referred_col in record._mapping:
                                        ref_value = record._mapping[referred_col]
                                        constrained_col = constrained_cols[i] if i < len(constrained_cols) else None

                                        if constrained_col:
                                            # Check for dependent records
                                            dep_table = Table(other_table, MetaData(), autoload_with=engine)
                                            with engine.connect() as conn:
                                                dep_count = conn.execute(
                                                    dep_table.select().where(
                                                        getattr(dep_table.c, constrained_col) == ref_value
                                                    )
                                                ).rowcount

                                                if dep_count > 0:
                                                    cascade_warnings.append({
                                                        "table": other_table,
                                                        "field": constrained_col,
                                                        "dependent_records": dep_count,
                                                        "warning": f"{dep_count} record(s) in {other_table} reference this record via {constrained_col}"
                                                    })
                except Exception as e:
                    logger.warning(f"Could not check foreign keys for {other_table}: {e}")

        # Prepare dry-run info
        identifier = f"ID {record_id}" if record_id else f"filters {filters}"
        dry_run_info = {
            "records_to_delete": len(records_to_delete),
            "identifier": identifier,
            "cascade_warnings": cascade_warnings if cascade_aware else None,
            "message": f"Would delete {len(records_to_delete)} record(s) from {table}"
        }

        # If not confirmed, return dry-run info
        if not confirm_delete:
            return {
                "success": True,
                "dry_run": True,
                "message": f"DRY RUN: Would delete {len(records_to_delete)} record(s) from {table}. "
                          f"Set confirm_delete=True to actually delete.",
                "dry_run_info": dry_run_info,
                "cascade_warnings": cascade_warnings if cascade_warnings else None
            }

        # Perform actual deletion
        with engine.begin() as conn:  # Transaction automatically commits or rolls back
            result = conn.execute(
                table_obj.delete().where(where_clause)
            )

            rows_deleted = result.rowcount

            response = {
                "success": True,
                "message": f"Successfully deleted {rows_deleted} record(s) from {table} matching {identifier}",
                "rows_deleted": rows_deleted
            }

            if cascade_warnings:
                response["cascade_warnings"] = cascade_warnings
                response["message"] += f" (Note: {len(cascade_warnings)} cascade warning(s))"

            return response

    except IntegrityError as e:
        # Foreign key constraint violation
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        logger.error(f"Integrity error deleting from {table}: {error_msg}", exc_info=True)

        return {
            "success": False,
            "error": "integrity_error",
            "message": f"Cannot delete: foreign key constraint violation",
            "details": error_msg,
            "hint": "Other records reference this record. Delete dependent records first, "
                   "or check cascade_warnings for more information."
        }

    except Exception as e:
        logger.error(f"Error deleting data from {table}: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to delete data from {table}: {str(e)}"
        }
