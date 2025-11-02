"""
Database Manager Tool

MCP tool for managing database connections.
Allows Claude to list, switch, and manage database connections.
"""

import logging
from typing import Dict, Any
from .base_tool import BaseTool, ToolDescription

logger = logging.getLogger(__name__)


class DatabaseManagerTool(BaseTool):
    """Tool for managing database connections"""

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="manage_database_connections",
            description="Manage database connections: list available connections, get current database info, or switch to a different database",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "current", "switch"],
                        "description": "Action to perform: 'list' available connections, get 'current' database info, or 'switch' to a different database"
                    },
                    "connection_name": {
                        "type": "string",
                        "description": "Connection name (required for 'switch' action)"
                    }
                },
                "required": ["action"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database management action"""
        try:
            action = arguments.get("action")

            if action == "list":
                return await self._list_connections()
            elif action == "current":
                return await self._get_current_database()
            elif action == "switch":
                connection_name = arguments.get("connection_name")
                if not connection_name:
                    return self._format_error(
                        "ValidationError",
                        "connection_name is required for 'switch' action"
                    )
                return await self._switch_database(connection_name)
            else:
                return self._format_error(
                    "ValidationError",
                    f"Invalid action: {action}. Must be 'list', 'current', or 'switch'"
                )

        except Exception as e:
            logger.error(f"Database manager error: {str(e)}", exc_info=True)
            return self._format_error("ExecutionError", str(e))

    async def _list_connections(self) -> Dict[str, Any]:
        """List all available database connections"""
        try:
            from pyarchinit_mini.config.connection_manager import get_connection_manager

            conn_manager = get_connection_manager()
            connections = conn_manager.list_connections()

            # Get current database for comparison
            current_db = self.config.database_url

            # Format connection list
            conn_list = []
            for conn in connections:
                # Get full connection details
                conn_full = conn_manager.get_connection(conn['name'])
                if conn_full:
                    conn_info = {
                        "name": conn['name'],
                        "type": conn['db_type'],
                        "description": conn.get('description', ''),
                        "display_info": conn.get('display_info', ''),
                        "is_active": conn_full['connection_string'] == current_db,
                        "created_at": conn.get('created_at', ''),
                        "last_used": conn.get('last_used', '')
                    }
                    conn_list.append(conn_info)

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Found {len(conn_list)} database connections:\n\n" +
                               "\n".join([
                                   f"{'✓' if c['is_active'] else ' '} {c['name']}\n"
                                   f"  Type: {c['type']}\n"
                                   f"  Info: {c['display_info']}\n"
                                   f"  Description: {c['description']}"
                                   for c in conn_list
                               ])
                    }
                ]
            }

        except Exception as e:
            logger.error(f"List connections error: {e}")
            return self._format_error("ExecutionError", str(e))

    async def _get_current_database(self) -> Dict[str, Any]:
        """Get current database information"""
        try:
            current_url = self.config.database_url

            # Parse database type and path
            if current_url.startswith('sqlite:///'):
                db_type = "SQLite"
                db_path = current_url.replace('sqlite:///', '')
            elif current_url.startswith('postgresql://'):
                db_type = "PostgreSQL"
                db_path = current_url
            else:
                db_type = "Unknown"
                db_path = current_url

            # Check if it's in ConnectionManager
            from pyarchinit_mini.config.connection_manager import get_connection_manager
            conn_manager = get_connection_manager()
            connections = conn_manager.list_connections()

            connection_name = None
            for conn in connections:
                conn_full = conn_manager.get_connection(conn['name'])
                if conn_full and conn_full['connection_string'] == current_url:
                    connection_name = conn['name']
                    break

            info_text = f"Current Database:\n\n"
            info_text += f"Type: {db_type}\n"
            info_text += f"Path: {db_path}\n"
            if connection_name:
                info_text += f"Connection Name: {connection_name}\n"
            else:
                info_text += "Connection Name: (not saved)\n"

            return {
                "content": [
                    {
                        "type": "text",
                        "text": info_text
                    }
                ]
            }

        except Exception as e:
            logger.error(f"Get current database error: {e}")
            return self._format_error("ExecutionError", str(e))

    async def _switch_database(self, connection_name: str) -> Dict[str, Any]:
        """Switch to a different database connection"""
        try:
            from pyarchinit_mini.config.connection_manager import get_connection_manager

            conn_manager = get_connection_manager()

            # Get connection details
            connection = conn_manager.get_connection(connection_name)
            if not connection:
                return self._format_error(
                    "NotFoundError",
                    f"Connection '{connection_name}' not found"
                )

            new_db_url = connection['connection_string']

            # Update config (note: this only updates the config object, not persistent state)
            # The server would need to be restarted to actually switch databases
            old_db = self.config.database_url
            self.config.database_url = new_db_url

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Switched database connection:\n\n"
                               f"From: {old_db}\n"
                               f"To: {new_db_url}\n\n"
                               f"Note: This change affects the current MCP session only. "
                               f"To make it permanent, restart the MCP server or use the web interface."
                    }
                ]
            }

        except Exception as e:
            logger.error(f"Switch database error: {e}")
            return self._format_error("ExecutionError", str(e))
