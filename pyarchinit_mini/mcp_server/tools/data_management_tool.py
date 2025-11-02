"""
Data Management Tool - Unified CRUD + Validation Tool for MCP

Provides comprehensive database operations for archaeological data:
- CREATE: Insert new records
- READ: Get database schema
- UPDATE: Modify existing records
- DELETE: Remove records (with safety checks)
- UPSERT: Insert or update (conflict resolution)
- VALIDATE: Stratigraphic relationship validation and auto-fix
"""

from typing import Dict, Any
from .base_tool import BaseTool, ToolDescription

# Import the underlying functions
from .get_schema_tool import get_schema
from .insert_data_tool import insert_data
from .batch_insert_tool import batch_insert
from .update_data_tool import update_data
from .delete_data_tool import delete_data
from .resolve_conflicts_tool import resolve_conflicts
from .validate_stratigraphy_tool import validate_stratigraphy


class DataManagementTool(BaseTool):
    """
    Unified Data Management Tool

    Provides all CRUD operations plus stratigraphic validation in one tool.
    Use the 'command' parameter to specify which operation to perform.
    """

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="manage_data",
            description=(
                "**PyArchInit Database Operations** - Manage archaeological data in the PyArchInit database. "
                "Features: CRUD operations (insert/update/delete/batch_insert), schema inspection, stratigraphic validation. "
                "Supports ALL PyArchInit tables: sites, stratigraphic units (US), materials inventory, "
                "datazioni, relationships, periodization. "
                "IMPORTANT: For inserting MULTIPLE records (10+), use 'batch_insert' command - it's much faster! "
                "Always use THIS tool for PyArchInit archaeological data operations. "
                "If you encounter an error, try again with this same tool - it handles datetime conversion, "
                "validation, and conflict resolution automatically."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Operation to perform",
                        "enum": [
                            "get_schema",
                            "insert",
                            "batch_insert",
                            "update",
                            "delete",
                            "upsert",
                            "validate_stratigraphy"
                        ]
                    },
                    # Common parameters
                    "table": {
                        "type": "string",
                        "description": "Table name (site_table, us_table, inventario_materiali_table, datazioni_table, us_relationships_table)"
                    },
                    "data": {
                        "type": "object",
                        "description": "Data dictionary for insert/update/upsert operations"
                    },
                    "records": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Array of data dictionaries for batch_insert operation (max 1000 records)"
                    },
                    # Batch insert specific
                    "stop_on_error": {
                        "type": "boolean",
                        "description": "For batch_insert: stop at first error (default: false)"
                    },
                    # Insert/Update/Delete specific
                    "record_id": {
                        "type": "integer",
                        "description": "Primary key ID for update/delete operations"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Filter conditions for update/delete operations"
                    },
                    "validate_only": {
                        "type": "boolean",
                        "description": "Dry-run mode (validate without executing)"
                    },
                    # Delete specific
                    "confirm_delete": {
                        "type": "boolean",
                        "description": "Required to confirm deletion (safety feature)"
                    },
                    "cascade_aware": {
                        "type": "boolean",
                        "description": "Check for foreign key dependencies before delete"
                    },
                    # Upsert specific
                    "conflict_keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields that define uniqueness for conflict detection"
                    },
                    "resolution": {
                        "type": "string",
                        "description": "Conflict resolution strategy",
                        "enum": ["detect", "skip", "update", "upsert"]
                    },
                    "merge_strategy": {
                        "type": "string",
                        "description": "How to merge conflicting data",
                        "enum": ["prefer_new", "prefer_existing", "replace_all"]
                    },
                    # Get schema specific
                    "include_constraints": {
                        "type": "boolean",
                        "description": "Include foreign keys and constraints in schema"
                    },
                    "include_sample_values": {
                        "type": "boolean",
                        "description": "Include sample enum values in schema"
                    },
                    # Validate stratigraphy specific
                    "site": {
                        "type": "string",
                        "description": "Site name for validation scope"
                    },
                    "area": {
                        "type": "string",
                        "description": "Area identifier for validation scope"
                    },
                    "check_chronology": {
                        "type": "boolean",
                        "description": "Validate chronological consistency with periodization data"
                    },
                    "auto_fix": {
                        "type": "boolean",
                        "description": "Automatically fix missing reciprocal relationships"
                    }
                },
                "required": ["command"]
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the requested data management operation

        Routes to the appropriate underlying function based on command.
        """
        command = arguments.get("command")

        if not command:
            return self._format_error("Missing required parameter: command")

        try:
            # Route to appropriate function
            if command == "get_schema":
                result = get_schema(
                    table=arguments.get("table"),
                    include_constraints=arguments.get("include_constraints", True),
                    include_sample_values=arguments.get("include_sample_values", False)
                )

            elif command == "insert":
                if "table" not in arguments or "data" not in arguments:
                    return self._format_error("insert requires 'table' and 'data' parameters")

                result = insert_data(
                    table=arguments["table"],
                    data=arguments["data"],
                    validate_only=arguments.get("validate_only", False)
                )

            elif command == "batch_insert":
                if "table" not in arguments or "records" not in arguments:
                    return self._format_error("batch_insert requires 'table' and 'records' parameters")

                result = batch_insert(
                    table=arguments["table"],
                    records=arguments["records"],
                    validate_only=arguments.get("validate_only", False),
                    stop_on_error=arguments.get("stop_on_error", False)
                )

            elif command == "update":
                if "table" not in arguments or "data" not in arguments:
                    return self._format_error("update requires 'table' and 'data' parameters")

                if "record_id" not in arguments and "filters" not in arguments:
                    return self._format_error("update requires either 'record_id' or 'filters'")

                result = update_data(
                    table=arguments["table"],
                    data=arguments["data"],
                    record_id=arguments.get("record_id"),
                    filters=arguments.get("filters"),
                    validate_only=arguments.get("validate_only", False)
                )

            elif command == "delete":
                if "table" not in arguments:
                    return self._format_error("delete requires 'table' parameter")

                if "record_id" not in arguments and "filters" not in arguments:
                    return self._format_error("delete requires either 'record_id' or 'filters'")

                result = delete_data(
                    table=arguments["table"],
                    record_id=arguments.get("record_id"),
                    filters=arguments.get("filters"),
                    confirm_delete=arguments.get("confirm_delete", False),
                    cascade_aware=arguments.get("cascade_aware", True)
                )

            elif command == "upsert":
                if "table" not in arguments or "data" not in arguments or "conflict_keys" not in arguments:
                    return self._format_error("upsert requires 'table', 'data', and 'conflict_keys' parameters")

                result = resolve_conflicts(
                    table=arguments["table"],
                    data=arguments["data"],
                    conflict_keys=arguments["conflict_keys"],
                    resolution=arguments.get("resolution", "upsert"),
                    merge_strategy=arguments.get("merge_strategy", "prefer_new")
                )

            elif command == "validate_stratigraphy":
                result = validate_stratigraphy(
                    site=arguments.get("site"),
                    area=arguments.get("area"),
                    check_chronology=arguments.get("check_chronology", False),
                    auto_fix=arguments.get("auto_fix", False)
                )

            else:
                return self._format_error(f"Unknown command: {command}")

            # Return result (already formatted by underlying functions)
            if result.get("success"):
                return self._format_success(result, result.get("message", "Operation completed successfully"))
            else:
                return self._format_error(result.get("message", "Operation failed"), details=result)

        except Exception as e:
            return self._format_error(f"Error executing {command}: {str(e)}")

    def _format_error(self, message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format error response"""
        result = {
            "success": False,
            "error": message
        }
        if details:
            result["details"] = details
        return result
