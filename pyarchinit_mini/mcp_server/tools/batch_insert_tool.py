"""
Batch Insert Tool - High-Performance Bulk Data Insertion for MCP

This tool enables AI assistants to insert multiple archaeological records in a single operation.
Features:
- Batch insertion of up to 1000 records per call
- Support for all PyArchInit tables
- Automatic validation for all records
- Transaction safety (all-or-nothing insertion)
- Detailed error reporting with record-level feedback
- Progress tracking for large datasets
"""

import logging
import os
from datetime import datetime, date
from sqlalchemy import Table, MetaData, inspect, DateTime, Date
from sqlalchemy.exc import IntegrityError, DataError
from typing import Dict, Any, List
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager

logger = logging.getLogger(__name__)


def batch_insert(
    table: str,
    records: List[Dict[str, Any]],
    validate_only: bool = False,
    stop_on_error: bool = False
) -> dict:
    """
    Insert multiple records into a PyArchInit table in a single transaction.

    Args:
        table: Table name to insert into.
               Supports ALL database tables including: site_table, us_table,
               inventario_materiali_table, datazioni_table, us_relationships_table, etc.
        records: List of dictionaries, each containing field_name -> value pairs.
                 Do NOT include auto-increment primary key fields (like "id").
                 Example: [
                     {"sito": "Pompei", "area": 1, "us": 100, "unita_tipo": "US"},
                     {"sito": "Pompei", "area": 1, "us": 101, "unita_tipo": "US"}
                 ]
        validate_only: If True, only validate data without inserting (dry-run mode)
        stop_on_error: If True, stop at first validation error. If False, validate all records
                       and report all errors.

    Returns:
        dict: Result with structure:
        {
            "success": True | False,
            "message": "Success/error message",
            "inserted_count": <number of records inserted> (only if success=True),
            "inserted_ids": [list of new record IDs] (only if success=True),
            "failed_count": <number of records that failed>,
            "errors": [list of validation/insertion errors with record indexes],
            "data": {...} (echoed data if validate_only=True)
        }

    Examples:
        # Insert 50 US in one call
        result = batch_insert(
            table="us_table",
            records=[
                {
                    "sito": "Pompei",
                    "area": 1,
                    "us": 1,
                    "unita_tipo": "US",
                    "definizione_stratigrafica": "Strato",
                    "descrizione": "Strato di lapilli",
                    "periodo": "Romano"
                },
                {
                    "sito": "Pompei",
                    "area": 1,
                    "us": 2,
                    "unita_tipo": "US",
                    "definizione_stratigrafica": "Strato",
                    "descrizione": "Cenere vulcanica",
                    "periodo": "Romano"
                },
                # ... 48 more records ...
            ]
        )

        # Insert 10 materials in one call
        result = batch_insert(
            table="inventario_materiali_table",
            records=[
                {
                    "sito": "Pompei",
                    "area": 1,
                    "us": 1,
                    "numero_inventario": "PM-001",
                    "tipo_reperto": "Ceramica",
                    "classe_materiale": "Sigillata"
                },
                # ... 9 more records ...
            ]
        )

        # Validate without inserting
        result = batch_insert(
            table="us_table",
            records=[...],
            validate_only=True
        )

    Notes:
        - Auto-increment fields (like "id") are generated automatically - do NOT include them
        - All records must be for the same table
        - Maximum 1000 records per call (for performance)
        - All records inserted in a single transaction (rollback on any error if stop_on_error=True)
        - DateTime fields accept ISO 8601 strings and are automatically converted
    """
    try:
        # Validate inputs
        if not records:
            return {
                "success": False,
                "error": "empty_records",
                "message": "Parameter 'records' must contain at least one record"
            }

        if len(records) > 1000:
            return {
                "success": False,
                "error": "too_many_records",
                "message": f"Maximum 1000 records per batch. Got {len(records)}. Split into smaller batches."
            }

        # Get database connection
        from pyarchinit_mini.mcp_server.config import _get_default_database_url
        database_url = os.getenv("DATABASE_URL") or _get_default_database_url()
        db_connection = DatabaseConnection(database_url)
        db_manager = DatabaseManager(db_connection)
        engine = db_connection.engine
        metadata = MetaData()
        inspector = inspect(engine)

        # Detect database type
        db_type = "sqlite" if "sqlite" in str(engine.url) else "postgresql"

        # Validate table exists
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

        # Get table metadata
        pk_constraint = inspector.get_pk_constraint(table)
        pk_columns = pk_constraint.get('constrained_columns', []) if pk_constraint else []
        columns = inspector.get_columns(table)
        column_info = {col['name']: col for col in columns}
        foreign_keys = inspector.get_foreign_keys(table)

        # Validate all records
        all_errors = []
        converted_records = []

        for idx, record_data in enumerate(records):
            record_errors = []

            # Check for auto-increment primary keys in data (should NOT be provided)
            for col_name in pk_columns:
                if col_name in record_data:
                    col = column_info.get(col_name)
                    if col:
                        is_autoincrement = False
                        if db_type == "sqlite":
                            is_autoincrement = "INTEGER" in str(col['type']).upper()
                        else:  # postgresql
                            is_autoincrement = (
                                col.get('autoincrement', False) or
                                'SERIAL' in str(col['type']).upper() or
                                (col.get('default', '') or '').startswith('nextval')
                            )

                        if is_autoincrement:
                            record_errors.append({
                                "record_index": idx,
                                "field": col_name,
                                "error": "auto_increment_field_provided",
                                "message": f"Field '{col_name}' is auto-increment - do NOT provide it"
                            })

            # Check required fields
            for col_name, col_info_item in column_info.items():
                is_required = not col_info_item.get('nullable', True)
                is_pk = col_name in pk_columns
                has_default = col_info_item.get('default') is not None

                # Skip auto-increment primary keys
                if is_pk:
                    col_type = str(col_info_item['type'])
                    is_autoincrement = False
                    if db_type == "sqlite":
                        is_autoincrement = "INTEGER" in col_type.upper()
                    else:
                        is_autoincrement = (
                            col_info_item.get('autoincrement', False) or
                            'SERIAL' in col_type.upper() or
                            (col_info_item.get('default', '') or '').startswith('nextval')
                        )

                    if is_autoincrement:
                        continue

                # Field is required if: NOT NULL, no default, and not auto-increment
                if is_required and not has_default and col_name not in record_data:
                    record_errors.append({
                        "record_index": idx,
                        "field": col_name,
                        "error": "required_field_missing",
                        "message": f"Required field '{col_name}' is missing"
                    })

            # Check for unknown fields
            for field_name in record_data.keys():
                if field_name not in column_info:
                    record_errors.append({
                        "record_index": idx,
                        "field": field_name,
                        "error": "unknown_field",
                        "message": f"Field '{field_name}' does not exist in table '{table}'"
                    })

            # Check foreign key constraints
            for fk in foreign_keys:
                constrained_cols = fk.get('constrained_columns', [])
                referred_table = fk.get('referred_table')
                referred_cols = fk.get('referred_columns', [])

                for i, col_name in enumerate(constrained_cols):
                    if col_name in record_data:
                        value = record_data[col_name]
                        if value is not None:
                            referred_col = referred_cols[i] if i < len(referred_cols) else 'id'
                            ref_table = Table(referred_table, MetaData(), autoload_with=engine)

                            with engine.connect() as conn:
                                result = conn.execute(
                                    ref_table.select().where(
                                        getattr(ref_table.c, referred_col) == value
                                    )
                                ).fetchone()

                                if not result:
                                    record_errors.append({
                                        "record_index": idx,
                                        "field": col_name,
                                        "error": "foreign_key_violation",
                                        "message": f"Value '{value}' for field '{col_name}' does not exist in {referred_table}.{referred_col}"
                                    })

            # If this record has errors and stop_on_error is True, stop validation
            if record_errors:
                all_errors.extend(record_errors)
                if stop_on_error:
                    break
            else:
                # Convert datetime/date strings to datetime/date objects
                converted_data = {}
                for field_name, value in record_data.items():
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
                                    # Try parsing as date-only string
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

                converted_records.append(converted_data)

        # If there are validation errors, return them
        if all_errors:
            return {
                "success": False,
                "error": "validation_failed",
                "message": f"Batch validation failed with {len(all_errors)} error(s) across {len(set(e['record_index'] for e in all_errors))} record(s)",
                "failed_count": len(set(e['record_index'] for e in all_errors)),
                "total_records": len(records),
                "validation_errors": all_errors
            }

        # If validate_only mode, return success without inserting
        if validate_only:
            return {
                "success": True,
                "message": f"Batch validation passed for {len(records)} record(s) - ready to insert",
                "total_records": len(records),
                "validated_records": len(converted_records)
            }

        # Insert all records in a single transaction
        inserted_ids = []
        with engine.begin() as conn:
            for record_data in converted_records:
                result = conn.execute(table_obj.insert().values(**record_data))
                inserted_id = result.inserted_primary_key[0] if result.inserted_primary_key else None
                inserted_ids.append(inserted_id)

        return {
            "success": True,
            "message": f"Successfully inserted {len(converted_records)} record(s) into {table}",
            "inserted_count": len(converted_records),
            "inserted_ids": inserted_ids,
            "total_records": len(records)
        }

    except IntegrityError as e:
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        logger.error(f"Integrity error in batch insert to {table}: {error_msg}", exc_info=True)

        return {
            "success": False,
            "error": "integrity_error",
            "message": f"Database constraint violation during batch insert: {error_msg}",
            "details": "This usually means:\n"
                      "- Duplicate value in unique field\n"
                      "- Foreign key reference doesn't exist\n"
                      "- NOT NULL constraint violated"
        }

    except DataError as e:
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        logger.error(f"Data type error in batch insert to {table}: {error_msg}", exc_info=True)

        return {
            "success": False,
            "error": "data_type_error",
            "message": f"Data type mismatch in batch insert: {error_msg}",
            "details": "This usually means:\n"
                      "- String provided for integer field\n"
                      "- Invalid date format\n"
                      "- Value too long for field"
        }

    except Exception as e:
        logger.error(f"Error in batch insert to {table}: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to batch insert into {table}: {str(e)}"
        }
