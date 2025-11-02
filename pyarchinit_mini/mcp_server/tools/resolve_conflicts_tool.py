"""
Resolve Conflicts Tool - Database Conflict Resolution for MCP

This tool enables AI assistants to detect and resolve data conflicts.
Features:
- Detect duplicate records (by unique constraints or composite keys)
- Provide conflict resolution strategies (skip, update, upsert)
- UPSERT operations (INSERT or UPDATE if exists)
- Merge strategies for conflicting data
- Works with both SQLite and PostgreSQL
- Transaction safety
"""

import logging
import os
from sqlalchemy import Table, MetaData, inspect, and_
from sqlalchemy.dialects import sqlite, postgresql
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any, Optional, List
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager

logger = logging.getLogger(__name__)


def resolve_conflicts(
    table: str,
    data: Dict[str, Any],
    conflict_keys: List[str],
    resolution: str = "detect",
    merge_strategy: str = "prefer_new"
) -> dict:
    """
    Detect and resolve data conflicts in a PyArchInit table.

    This tool handles situations where inserting data would violate unique constraints
    or create duplicate records based on composite keys.

    Args:
        table: Table name to work with.
               Supports ALL database tables including: site_table, us_table,
               inventario_materiali_table, datazioni_table, us_relationships_table,
               periodizzazione tables, media tables, thesaurus tables, users table, etc.
        data: Dictionary of field_name -> value pairs to insert/update.
              Example: {"sito": "Pompei", "area": 1, "us": 100, "descrizione": "New"}
        conflict_keys: List of field names that define uniqueness.
                      Records with matching values in these fields are considered conflicts.
                      Example: ["sito", "area", "us"] for us_table
                      Example: ["sito"] for site_table
        resolution: Conflict resolution strategy:
                   - "detect": Only detect conflicts, don't modify data (default)
                   - "skip": Skip if record exists (no changes)
                   - "update": Update existing record with new data
                   - "upsert": Insert if not exists, update if exists (INSERT ON CONFLICT UPDATE)
        merge_strategy: When resolution="update" or "upsert", how to merge data:
                       - "prefer_new": Use new values, keep old only if new is NULL (default)
                       - "prefer_existing": Keep existing values, use new only if old is NULL
                       - "replace_all": Replace all fields with new values

    Returns:
        dict: Result with structure:
        {
            "success": True | False,
            "message": "Success/error message",
            "conflict_detected": True | False,
            "existing_record": {...} (if conflict detected),
            "action_taken": "inserted" | "updated" | "skipped" | "detected",
            "affected_rows": <number of rows affected>
        }

    Examples:
        # Detect if US already exists
        result = resolve_conflicts(
            table="us_table",
            data={"sito": "Pompei", "area": 1, "us": 100, "descrizione": "Test"},
            conflict_keys=["sito", "area", "us"],
            resolution="detect"
        )

        # Skip if exists, insert if not
        result = resolve_conflicts(
            table="us_table",
            data={"sito": "Pompei", "area": 1, "us": 150, "descrizione": "New US"},
            conflict_keys=["sito", "area", "us"],
            resolution="skip"
        )

        # Update if exists, insert if not (UPSERT)
        result = resolve_conflicts(
            table="site_table",
            data={"sito": "Tempio", "location": "Palestrina", "nazione": "Italia"},
            conflict_keys=["sito"],
            resolution="upsert",
            merge_strategy="prefer_new"
        )

    Notes:
        - conflict_keys should match unique constraints in the table
        - For us_table, typical conflict_keys: ["sito", "area", "us"]
        - For site_table, typical conflict_keys: ["sito"]
        - UPSERT is atomic (no race conditions)
        - Transaction is rolled back if any error occurs
    """
    try:
        # Validate resolution strategy
        valid_resolutions = ["detect", "skip", "update", "upsert"]
        if resolution not in valid_resolutions:
            return {
                "success": False,
                "error": "invalid_resolution",
                "message": f"Resolution must be one of: {', '.join(valid_resolutions)}"
            }

        # Validate merge strategy
        valid_merge = ["prefer_new", "prefer_existing", "replace_all"]
        if merge_strategy not in valid_merge:
            return {
                "success": False,
                "error": "invalid_merge_strategy",
                "message": f"Merge strategy must be one of: {', '.join(valid_merge)}"
            }

        # Validate conflict_keys
        if not conflict_keys:
            return {
                "success": False,
                "error": "missing_conflict_keys",
                "message": "conflict_keys must be provided (at least one field)"
            }

        # Get database connection - use config default if DATABASE_URL not set
        from pyarchinit_mini.mcp_server.config import _get_default_database_url
        database_url = os.getenv("DATABASE_URL") or _get_default_database_url()
        db_connection = DatabaseConnection(database_url)
        db_manager = DatabaseManager(db_connection)
        engine = db_connection.engine
        metadata = MetaData()
        inspector = inspect(engine)

        # Detect database type
        db_type = "sqlite" if "sqlite" in str(engine.url) else "postgresql"

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

        # Get column information
        columns = inspector.get_columns(table)
        column_names = [col['name'] for col in columns]

        # Validate conflict_keys exist in table
        for key in conflict_keys:
            if key not in column_names:
                return {
                    "success": False,
                    "error": "invalid_conflict_key",
                    "message": f"Conflict key '{key}' does not exist in table '{table}'"
                }

        # Validate conflict_keys are provided in data
        for key in conflict_keys:
            if key not in data:
                return {
                    "success": False,
                    "error": "missing_conflict_key_value",
                    "message": f"Conflict key '{key}' must be provided in data"
                }

        # Build WHERE clause for conflict detection
        where_conditions = [getattr(table_obj.c, key) == data[key] for key in conflict_keys]
        where_clause = and_(*where_conditions) if len(where_conditions) > 1 else where_conditions[0]

        # Check for existing record
        with engine.connect() as conn:
            existing = conn.execute(
                table_obj.select().where(where_clause)
            ).fetchone()

            conflict_detected = existing is not None

            # DETECT mode: Just report conflict
            if resolution == "detect":
                if conflict_detected:
                    return {
                        "success": True,
                        "conflict_detected": True,
                        "message": f"Conflict detected: record with {conflict_keys} = {[data[k] for k in conflict_keys]} already exists",
                        "existing_record": dict(existing._mapping) if existing else None,
                        "action_taken": "detected"
                    }
                else:
                    return {
                        "success": True,
                        "conflict_detected": False,
                        "message": f"No conflict: record with {conflict_keys} = {[data[k] for k in conflict_keys]} does not exist",
                        "action_taken": "detected"
                    }

            # SKIP mode: Insert only if not exists
            if resolution == "skip":
                if conflict_detected:
                    return {
                        "success": True,
                        "conflict_detected": True,
                        "message": f"Record exists - skipped (no changes made)",
                        "existing_record": dict(existing._mapping) if existing else None,
                        "action_taken": "skipped",
                        "affected_rows": 0
                    }
                else:
                    # Insert new record
                    with engine.begin() as conn_trans:
                        result = conn_trans.execute(table_obj.insert().values(**data))
                        inserted_id = result.inserted_primary_key[0] if result.inserted_primary_key else None

                        return {
                            "success": True,
                            "conflict_detected": False,
                            "message": f"No conflict - record inserted",
                            "action_taken": "inserted",
                            "inserted_id": inserted_id,
                            "affected_rows": 1
                        }

            # UPDATE mode: Update existing record, fail if not exists
            if resolution == "update":
                if not conflict_detected:
                    return {
                        "success": False,
                        "conflict_detected": False,
                        "error": "no_record_to_update",
                        "message": f"Cannot update: no record with {conflict_keys} = {[data[k] for k in conflict_keys]} exists"
                    }

                # Merge data based on strategy
                merged_data = _merge_data(
                    existing_data=dict(existing._mapping),
                    new_data=data,
                    strategy=merge_strategy,
                    conflict_keys=conflict_keys
                )

                with engine.begin() as conn_trans:
                    result = conn_trans.execute(
                        table_obj.update().where(where_clause).values(**merged_data)
                    )

                    return {
                        "success": True,
                        "conflict_detected": True,
                        "message": f"Record updated successfully",
                        "existing_record": dict(existing._mapping),
                        "action_taken": "updated",
                        "affected_rows": result.rowcount,
                        "merged_data": merged_data
                    }

            # UPSERT mode: Insert if not exists, update if exists
            if resolution == "upsert":
                with engine.begin() as conn_trans:
                    if conflict_detected:
                        # Update existing record
                        merged_data = _merge_data(
                            existing_data=dict(existing._mapping),
                            new_data=data,
                            strategy=merge_strategy,
                            conflict_keys=conflict_keys
                        )

                        result = conn_trans.execute(
                            table_obj.update().where(where_clause).values(**merged_data)
                        )

                        return {
                            "success": True,
                            "conflict_detected": True,
                            "message": f"Record existed - updated",
                            "existing_record": dict(existing._mapping),
                            "action_taken": "updated",
                            "affected_rows": result.rowcount,
                            "merged_data": merged_data
                        }
                    else:
                        # Insert new record
                        result = conn_trans.execute(table_obj.insert().values(**data))
                        inserted_id = result.inserted_primary_key[0] if result.inserted_primary_key else None

                        return {
                            "success": True,
                            "conflict_detected": False,
                            "message": f"Record did not exist - inserted",
                            "action_taken": "inserted",
                            "inserted_id": inserted_id,
                            "affected_rows": 1
                        }

    except IntegrityError as e:
        # Database constraint violation
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        logger.error(f"Integrity error resolving conflicts in {table}: {error_msg}", exc_info=True)

        return {
            "success": False,
            "error": "integrity_error",
            "message": f"Database constraint violation: {error_msg}",
            "details": "This may mean:\n"
                      "- Different unique constraint violated\n"
                      "- Foreign key reference doesn't exist\n"
                      "- NOT NULL constraint violated"
        }

    except Exception as e:
        logger.error(f"Error resolving conflicts in {table}: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to resolve conflicts in {table}: {str(e)}"
        }


def _merge_data(
    existing_data: Dict[str, Any],
    new_data: Dict[str, Any],
    strategy: str,
    conflict_keys: List[str]
) -> Dict[str, Any]:
    """
    Merge existing and new data according to strategy.

    Args:
        existing_data: Current record data from database
        new_data: New data to apply
        strategy: Merge strategy ("prefer_new", "prefer_existing", "replace_all")
        conflict_keys: Keys that identify the record (don't update these)

    Returns:
        Merged data dictionary
    """
    merged = {}

    # Get all unique keys
    all_keys = set(new_data.keys())

    for key in all_keys:
        # Never update conflict keys (they identify the record)
        if key in conflict_keys:
            continue

        # Never update primary key
        if key == 'id':
            continue

        new_value = new_data.get(key)
        existing_value = existing_data.get(key)

        if strategy == "replace_all":
            # Always use new value
            merged[key] = new_value

        elif strategy == "prefer_new":
            # Use new value unless it's None/NULL
            merged[key] = new_value if new_value is not None else existing_value

        elif strategy == "prefer_existing":
            # Keep existing value unless it's None/NULL
            merged[key] = existing_value if existing_value is not None else new_value

    return merged
