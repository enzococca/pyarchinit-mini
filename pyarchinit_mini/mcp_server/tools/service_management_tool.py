"""
Service Management Tool - PyArchInit Services Controller for MCP

Provides service management operations for PyArchInit:
- START: Launch services (web, api, gui, mcp-http)
- STOP: Stop running services
- STATUS: Check service status
- LIST: List all running services
- LOGS: View service logs
"""

from typing import Dict, Any
from .base_tool import BaseTool, ToolDescription

# Import the underlying function
from .manage_services_tool import manage_service


class ServiceManagementTool(BaseTool):
    """
    Unified Service Management Tool

    Provides all service management operations in one tool.
    Use the 'action' parameter to specify which operation to perform.
    """

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="manage_services",
            description=(
                "Manage PyArchInit services (web interface, API server, GUI, MCP HTTP server). "
                "Supports: start, stop, status, list, logs"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform on the service",
                        "enum": ["start", "stop", "status", "list", "logs"]
                    },
                    "service": {
                        "type": "string",
                        "description": "Service to manage",
                        "enum": ["web", "api", "gui", "mcp-http", "all"]
                    },
                    "port": {
                        "type": "integer",
                        "description": "Optional port number (defaults: web=5001, api=8000, mcp-http=8765)"
                    },
                    "host": {
                        "type": "string",
                        "description": "Host to bind to (default: localhost)"
                    },
                    "database_url": {
                        "type": "string",
                        "description": "Optional database URL override"
                    },
                    "background": {
                        "type": "boolean",
                        "description": "Run service in background (default: true)"
                    }
                },
                "required": ["action", "service"]
            }
        )

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute service management operation"""
        action = arguments.get("action")
        service = arguments.get("service")
        port = arguments.get("port")
        host = arguments.get("host", "localhost")
        database_url = arguments.get("database_url")
        background = arguments.get("background", True)

        # Validate required parameters
        if not action:
            return {
                "success": False,
                "error": "missing_action",
                "message": "Parameter 'action' is required"
            }

        if not service:
            return {
                "success": False,
                "error": "missing_service",
                "message": "Parameter 'service' is required"
            }

        # Call the underlying function
        return manage_service(
            action=action,
            service=service,
            port=port,
            host=host,
            database_url=database_url,
            background=background
        )
