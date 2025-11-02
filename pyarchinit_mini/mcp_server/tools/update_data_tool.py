"""
Update Data Tool - Database Record Update for MCP

This tool enables AI assistants to update existing archaeological records in the database.
Features:
- Update records by ID or by filter conditions
- Partial updates (only modify specified fields)
- Automatic field validation
- Foreign key validation
- Transaction safety (rollback on error)
- Works with both SQLite and PostgreSQL
- Returns number of affected rows
"""

import logging
import os
from datetime import datetime, date
from sqlalchemy import Table, MetaData, inspect, and_, DateTime, Date
from sqlalchemy.exc import IntegrityError, DataError
from typing import Dict, Any, Optional
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager

logger = logging.getLogger(__name__)


def update_data(
    table: str,
    data: Dict[str, Any],
    record_id: Optional[int] = None,
    filters: Optional[Dict[str, Any]] = None,
    validate_only: bool = False
) -> dict:
    """
    Update existing record(s) in a PyArchInit table.

    Args:
        table: Table name to update.
               Supports ALL database tables including: site_table, us_table,
               inventario_materiali_table, datazioni_table, us_relationships_table,
               periodizzazione tables, media tables, thesaurus tables, users table, etc.
        data: Dictionary of field_name -> new_value pairs.
              Only fields provided will be updated (partial update).
              Example: {"descrizione": "Updated description", "periodo": "Romano"}
        record_id: Primary key ID of specific record to update.
                   If provided, updates only this record.
                   Cannot be used together with filters.
        filters: Dictionary of field_name -> value conditions for filtering records.
                 Updates ALL records matching these conditions.
                 Example: {"sito": "Pompei", "area": 1}
                 Cannot be used together with record_id.
        validate_only: If True, only validate data without updating (dry-run mode)

    Returns:
        dict: Result with structure:
        {
            "success": True | False,
            "message": "Success/error message",
            "rows_updated": <number of records updated>,
            "validation_errors": [...] (only if validation failed)
        }

    Examples:
        # Update a specific record by ID
        result = update_data(
            table="us_table",
            record_id=42,
            data={
                "descrizione": "Strato di crollo aggiornato",
                "periodo": "Romano Imperiale"
            }
        )

        # Update all US in a specific site and area
        result = update_data(
            table="us_table",
            filters={"sito": "Pompei", "area": 1},
            data={"stato_di_conservazione": "Buono"}
        )

        # Validate update without applying it
        result = update_data(
            table="site_table",
            record_id=5,
            data={"nazione": "Francia"},
            validate_only=True
        )

    Notes:
        - Either record_id OR filters must be provided (not both, not neither)
        - Only fields in 'data' will be updated (partial updates supported)
        - Primary key fields cannot be updated
        - Foreign keys are validated before update
        - Transaction is rolled back if any error occurs
    """
    try:
        # Validate that either record_id or filters is provided
        if record_id is None and filters is None:
            return {
                "success": False,
                "error": "missing_identifier",
                "message": "Either 'record_id' or 'filters' must be provided to identify records to update"
            }

        if record_id is not None and filters is not None:
            return {
                "success": False,
                "error": "conflicting_identifiers",
                "message": "Cannot use both 'record_id' and 'filters' - choose one"
            }

        # Validate data is not empty
        if not data:
            return {
                "success": False,
                "error": "empty_data",
                "message": "No data provided for update"
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

        # Validate data
        validation_errors = []

        # Get primary key columns
        pk_constraint = inspector.get_pk_constraint(table)
        pk_columns = pk_constraint.get('constrained_columns', []) if pk_constraint else []

        # Get column information
        columns = inspector.get_columns(table)
        column_info = {col['name']: col for col in columns}

        # Check for attempts to update primary key
        for pk_col in pk_columns:
            if pk_col in data:
                validation_errors.append({
                    "field": pk_col,
                    "error": "cannot_update_primary_key",
                    "message": f"Primary key field '{pk_col}' cannot be updated"
                })

        # Check for unknown fields
        for field_name in data.keys():
            if field_name not in column_info:
                validation_errors.append({
                    "field": field_name,
                    "error": "unknown_field",
                    "message": f"Field '{field_name}' does not exist in table '{table}'"
                })

        # Check foreign key constraints
        foreign_keys = inspector.get_foreign_keys(table)
        for fk in foreign_keys:
            constrained_cols = fk.get('constrained_columns', [])
            referred_table = fk.get('referred_table')
            referred_cols = fk.get('referred_columns', [])

            for i, col_name in enumerate(constrained_cols):
                if col_name in data:
                    value = data[col_name]
                    if value is not None:  # NULL is allowed for optional foreign keys
                        # Check if referenced value exists
                        referred_col = referred_cols[i] if i < len(referred_cols) else 'id'
                        ref_table = Table(referred_table, MetaData(), autoload_with=engine)

                        with engine.connect() as conn:
                            result = conn.execute(
                                ref_table.select().where(
                                    getattr(ref_table.c, referred_col) == value
                                )
                            ).fetchone()

                            if not result:
                                validation_errors.append({
                                    "field": col_name,
                                    "error": "foreign_key_violation",
                                    "message": f"Value '{value}' for field '{col_name}' does not exist in {referred_table}.{referred_col}"
                                })

        # If validation errors, return them
        if validation_errors:
            return {
                "success": False,
                "error": "validation_failed",
                "message": f"Data validation failed with {len(validation_errors)} error(s)",
                "validation_errors": validation_errors
            }

        # Build WHERE clause
        where_conditions = []
        if record_id is not None:
            # Update by primary key
            if not pk_columns:
                return {
                    "success": False,
                    "error": "no_primary_key",
                    "message": f"Table '{table}' has no primary key defined"
                }
            pk_col = pk_columns[0]  # Use first primary key column
            where_conditions.append(getattr(table_obj.c, pk_col) == record_id)
        else:
            # Update by filters
            for field_name, value in filters.items():
                if field_name not in column_info:
                    return {
                        "success": False,
                        "error": "unknown_filter_field",
                        "message": f"Filter field '{field_name}' does not exist in table '{table}'"
                    }
                where_conditions.append(getattr(table_obj.c, field_name) == value)

        where_clause = and_(*where_conditions) if len(where_conditions) > 1 else where_conditions[0]

        # Check if records exist before update
        with engine.connect() as conn:
            check_result = conn.execute(
                table_obj.select().where(where_clause)
            ).fetchall()

            if not check_result:
                identifier = f"ID {record_id}" if record_id else f"filters {filters}"
                return {
                    "success": False,
                    "error": "no_records_found",
                    "message": f"No records found in {table} matching {identifier}"
                }

            # If validate_only mode, return success without updating
            if validate_only:
                return {
                    "success": True,
                    "message": f"Data validation passed - {len(check_result)} record(s) ready to update",
                    "records_to_update": len(check_result),
                    "data": data
                }

        # Convert datetime/date strings to Python objects
        # SQLAlchemy requires Python datetime/date objects for DateTime/Date columns
        converted_data = {}
        for field_name, value in data.items():
            if field_name in column_info:
                col_type = column_info[field_name]['type']

                # Handle DateTime fields (timestamp with time)
                if isinstance(col_type, DateTime):
                    if isinstance(value, str) and value:
                        try:
                            value_clean = value.replace('Z', '').replace('T', ' ').strip()
                            for fmt in [
                                '%Y-%m-%d %H:%M:%S.%f',
                                '%Y-%m-%d %H:%M:%S',
                                '%Y-%m-%d',
                            ]:
                                try:
                                    converted_data[field_name] = datetime.strptime(value_clean, fmt)
                                    break
                                except ValueError:
                                    continue
                            else:
                                converted_data[field_name] = value
                        except Exception:
                            converted_data[field_name] = value
                    else:
                        converted_data[field_name] = value

                # Handle Date fields (date only, no time)
                elif isinstance(col_type, Date):
                    if isinstance(value, str) and value:
                        try:
                            value_clean = value.strip()
                            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                                try:
                                    converted_data[field_name] = datetime.strptime(value_clean, fmt).date()
                                    break
                                except ValueError:
                                    continue
                            else:
                                converted_data[field_name] = value
                        except Exception:
                            converted_data[field_name] = value
                    else:
                        converted_data[field_name] = value
                else:
                    converted_data[field_name] = value
            else:
                converted_data[field_name] = value

        # Update data with converted datetime/date values
        with engine.begin() as conn:  # Transaction automatically commits or rolls back
            result = conn.execute(
                table_obj.update().where(where_clause).values(**converted_data)
            )

            rows_updated = result.rowcount

            identifier = f"ID {record_id}" if record_id else f"filters {filters}"
            return {
                "success": True,
                "message": f"Successfully updated {rows_updated} record(s) in {table} matching {identifier}",
                "rows_updated": rows_updated,
                "data": data
            }

    except IntegrityError as e:
        # Database constraint violation (unique, foreign key, etc.)
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        logger.error(f"Integrity error updating {table}: {error_msg}", exc_info=True)

        return {
            "success": False,
            "error": "integrity_error",
            "message": f"Database constraint violation: {error_msg}",
            "details": "This usually means:\n"
                      "- Duplicate value in unique field\n"
                      "- Foreign key reference doesn't exist\n"
                      "- NOT NULL constraint violated"
        }

    except DataError as e:
        # Data type mismatch
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        logger.error(f"Data type error updating {table}: {error_msg}", exc_info=True)

        return {
            "success": False,
            "error": "data_type_error",
            "message": f"Data type mismatch: {error_msg}",
            "details": "This usually means:\n"
                      "- String provided for integer field\n"
                      "- Invalid date format\n"
                      "- Value too long for field"
        }

    except Exception as e:
        logger.error(f"Error updating data in {table}: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update data in {table}: {str(e)}"
        }
