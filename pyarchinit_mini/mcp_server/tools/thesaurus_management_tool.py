"""
Thesaurus Management Tool

Provides comprehensive controlled vocabulary management for archaeological data:
- List available thesaurus fields for tables
- Get vocabulary values for specific fields
- Add, update, and delete vocabulary entries
- Search vocabulary entries
- Initialize default vocabularies
- Export thesaurus data
- Get thesaurus statistics
"""

import logging
from typing import Dict, Any, List, Optional
from .base_tool import BaseTool, ToolDescription
from ...services.thesaurus_service import ThesaurusService

logger = logging.getLogger(__name__)


class ThesaurusManagementTool(BaseTool):
    """Comprehensive thesaurus and controlled vocabulary management"""

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="manage_thesaurus",
            description=(
                "Comprehensive thesaurus and controlled vocabulary management tool. "
                "List available fields, get vocabulary values, add/update/delete entries, "
                "search vocabularies, initialize default values, and get statistics. "
                "Supports Italian and English vocabularies for archaeological data."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "list_fields",
                            "list_values",
                            "search",
                            "add_value",
                            "update_value",
                            "delete_value",
                            "initialize",
                            "statistics"
                        ],
                        "description": (
                            "'list_fields' = List fields with thesaurus for a table, "
                            "'list_values' = Get vocabulary values for a field, "
                            "'search' = Search vocabulary entries, "
                            "'add_value' = Add new vocabulary value, "
                            "'update_value' = Update vocabulary value, "
                            "'delete_value' = Delete vocabulary value, "
                            "'initialize' = Initialize default vocabularies, "
                            "'statistics' = Get thesaurus statistics"
                        )
                    },
                    "table_name": {
                        "type": "string",
                        "description": (
                            "Database table name (e.g., 'site_table', 'us_table', 'inventario_materiali_table'). "
                            "Required for list_fields, list_values, add_value operations."
                        )
                    },
                    "field_name": {
                        "type": "string",
                        "description": (
                            "Field name within the table (e.g., 'tipologia_sito', 'tipo_us', 'tipo_reperto'). "
                            "Required for list_values, add_value operations."
                        )
                    },
                    "value": {
                        "type": "string",
                        "description": "Vocabulary value (required for add_value, update_value operations)"
                    },
                    "label": {
                        "type": "string",
                        "description": "Human-readable label for the value (optional, for add_value, update_value)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the vocabulary value (optional, for add_value, update_value)"
                    },
                    "field_id": {
                        "type": "integer",
                        "description": "Field entry ID (required for update_value, delete_value operations)"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["it", "en"],
                        "description": "Language code (default: 'it' for Italian, 'en' for English)",
                        "default": "it"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query string (required for search operation)"
                    },
                    "include_predefined": {
                        "type": "boolean",
                        "description": "Include predefined vocabularies in results (default: true)",
                        "default": True
                    }
                },
                "required": ["operation"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute thesaurus management operation"""
        try:
            operation = arguments.get("operation")

            # Initialize thesaurus service
            thesaurus_service = ThesaurusService(self.db_manager)

            logger.info(f"Executing thesaurus operation: {operation}")

            if operation == "list_fields":
                return await self._handle_list_fields(thesaurus_service, arguments)
            elif operation == "list_values":
                return await self._handle_list_values(thesaurus_service, arguments)
            elif operation == "search":
                return await self._handle_search(thesaurus_service, arguments)
            elif operation == "add_value":
                return await self._handle_add_value(thesaurus_service, arguments)
            elif operation == "update_value":
                return await self._handle_update_value(thesaurus_service, arguments)
            elif operation == "delete_value":
                return await self._handle_delete_value(thesaurus_service, arguments)
            elif operation == "initialize":
                return await self._handle_initialize(thesaurus_service, arguments)
            elif operation == "statistics":
                return await self._handle_statistics(thesaurus_service, arguments)
            else:
                return self._format_error(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(f"Thesaurus management error: {str(e)}", exc_info=True)
            return self._format_error(f"Thesaurus management failed: {str(e)}")

    async def _handle_list_fields(
        self,
        thesaurus_service: ThesaurusService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle list fields with thesaurus operation"""
        table_name = arguments.get("table_name")

        if not table_name:
            return self._format_error("table_name is required for list_fields operation")

        fields = thesaurus_service.get_table_fields(table_name)

        return self._format_success(
            result={
                "table_name": table_name,
                "fields": fields,
                "count": len(fields)
            },
            message=f"Found {len(fields)} fields with thesaurus for table '{table_name}'"
        )

    async def _handle_list_values(
        self,
        thesaurus_service: ThesaurusService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle list vocabulary values operation"""
        table_name = arguments.get("table_name")
        field_name = arguments.get("field_name")
        language = arguments.get("language", "it")

        if not table_name or not field_name:
            return self._format_error(
                "table_name and field_name are required for list_values operation"
            )

        values = thesaurus_service.get_field_values(
            table_name=table_name,
            field_name=field_name,
            language=language
        )

        return self._format_success(
            result={
                "table_name": table_name,
                "field_name": field_name,
                "language": language,
                "values": values,
                "count": len(values)
            },
            message=f"Found {len(values)} vocabulary values for {table_name}.{field_name}"
        )

    async def _handle_search(
        self,
        thesaurus_service: ThesaurusService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle search vocabulary operation"""
        query = arguments.get("query")
        table_name = arguments.get("table_name")
        field_name = arguments.get("field_name")
        language = arguments.get("language", "it")

        if not query:
            return self._format_error("query is required for search operation")

        results = thesaurus_service.search_values(
            query=query,
            table_name=table_name,
            field_name=field_name,
            language=language
        )

        return self._format_success(
            result={
                "query": query,
                "table_name": table_name,
                "field_name": field_name,
                "language": language,
                "results": results,
                "count": len(results)
            },
            message=f"Found {len(results)} matching vocabulary entries for query '{query}'"
        )

    async def _handle_add_value(
        self,
        thesaurus_service: ThesaurusService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle add vocabulary value operation"""
        table_name = arguments.get("table_name")
        field_name = arguments.get("field_name")
        value = arguments.get("value")
        label = arguments.get("label")
        description = arguments.get("description")
        language = arguments.get("language", "it")

        if not table_name or not field_name or not value:
            return self._format_error(
                "table_name, field_name, and value are required for add_value operation"
            )

        new_entry = thesaurus_service.add_field_value(
            table_name=table_name,
            field_name=field_name,
            value=value,
            label=label,
            description=description,
            language=language
        )

        return self._format_success(
            result={
                "id": new_entry["id"],
                "table_name": table_name,
                "field_name": field_name,
                "value": new_entry["value"],
                "label": new_entry["label"],
                "description": new_entry["description"]
            },
            message=f"Added vocabulary value '{value}' to {table_name}.{field_name}"
        )

    async def _handle_update_value(
        self,
        thesaurus_service: ThesaurusService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle update vocabulary value operation"""
        field_id = arguments.get("field_id")
        value = arguments.get("value")
        label = arguments.get("label")
        description = arguments.get("description")

        if not field_id:
            return self._format_error("field_id is required for update_value operation")

        if not value and not label and not description:
            return self._format_error(
                "At least one of value, label, or description must be provided for update"
            )

        updated_entry = thesaurus_service.update_field_value(
            field_id=field_id,
            value=value,
            label=label,
            description=description
        )

        return self._format_success(
            result={
                "id": updated_entry["id"],
                "value": updated_entry["value"],
                "label": updated_entry["label"],
                "description": updated_entry["description"]
            },
            message=f"Updated vocabulary entry ID {field_id}"
        )

    async def _handle_delete_value(
        self,
        thesaurus_service: ThesaurusService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle delete vocabulary value operation"""
        field_id = arguments.get("field_id")

        if not field_id:
            return self._format_error("field_id is required for delete_value operation")

        success = thesaurus_service.delete_field_value(field_id)

        if success:
            return self._format_success(
                result={"field_id": field_id, "deleted": True},
                message=f"Deleted vocabulary entry ID {field_id}"
            )
        else:
            return self._format_error(f"Failed to delete vocabulary entry ID {field_id}")

    async def _handle_initialize(
        self,
        thesaurus_service: ThesaurusService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle initialize default vocabularies operation"""
        try:
            success = thesaurus_service.initialize_default_vocabularies()

            if success:
                # Get statistics after initialization
                stats = self._get_thesaurus_statistics(thesaurus_service)

                return self._format_success(
                    result={
                        "initialized": True,
                        "statistics": stats
                    },
                    message="Default vocabularies initialized successfully"
                )
            else:
                return self._format_error("Failed to initialize default vocabularies")

        except Exception as e:
            return self._format_error(f"Initialization failed: {str(e)}")

    async def _handle_statistics(
        self,
        thesaurus_service: ThesaurusService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get thesaurus statistics operation"""
        table_name = arguments.get("table_name")

        stats = self._get_thesaurus_statistics(thesaurus_service, table_name)

        return self._format_success(
            result=stats,
            message="Thesaurus statistics retrieved"
        )

    def _get_thesaurus_statistics(
        self,
        thesaurus_service: ThesaurusService,
        table_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get thesaurus statistics"""
        from ...models.thesaurus import THESAURUS_MAPPINGS

        if table_name:
            # Statistics for specific table
            fields = thesaurus_service.get_table_fields(table_name)
            total_values = 0
            field_counts = {}

            for field in fields:
                values = thesaurus_service.get_field_values(table_name, field)
                field_counts[field] = len(values)
                total_values += len(values)

            return {
                "table_name": table_name,
                "total_fields": len(fields),
                "total_values": total_values,
                "field_counts": field_counts
            }
        else:
            # Global statistics
            all_tables = list(THESAURUS_MAPPINGS.keys())
            table_stats = {}
            total_fields = 0
            total_values = 0

            for tbl_name in all_tables:
                fields = thesaurus_service.get_table_fields(tbl_name)
                tbl_total_values = 0

                for field in fields:
                    values = thesaurus_service.get_field_values(tbl_name, field)
                    tbl_total_values += len(values)

                table_stats[tbl_name] = {
                    "fields": len(fields),
                    "values": tbl_total_values
                }

                total_fields += len(fields)
                total_values += tbl_total_values

            return {
                "total_tables": len(all_tables),
                "total_fields": total_fields,
                "total_values": total_values,
                "table_statistics": table_stats
            }
