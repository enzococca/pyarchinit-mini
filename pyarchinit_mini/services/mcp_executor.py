"""
MCP Tools Executor

Executes MCP tools locally for web interface chat functionality.
Provides a bridge between web UI and MCP tools.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..mcp_server.config import MCPConfig
from ..mcp_server.tools.build_3d_tool import Build3DTool
from ..mcp_server.tools.filter_tool import FilterTool
from ..mcp_server.tools.export_tool import ExportTool
from ..mcp_server.tools.position_tool import PositionTool
from ..mcp_server.tools.material_tool import MaterialTool
from ..mcp_server.resources.graphml_resource import GraphMLResource
from ..mcp_server.resources.us_resource import USResource
from ..database.connection import DatabaseConnection
from ..database.manager import DatabaseManager
from ..services.us_service import USService

logger = logging.getLogger(__name__)


class MCPToolsExecutor:
    """
    Executes MCP tools locally without needing Claude Desktop.

    Used by web interface to provide chat-based 3D building.
    """

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize MCP tools executor

        Args:
            database_url: Database URL (uses default if None)
        """
        self.config = MCPConfig()
        if database_url:
            self.config.database_url = database_url

        # Initialize database
        db_connection = DatabaseConnection(self.config.database_url)
        self.db_manager = DatabaseManager(db_connection)
        self.db_session = db_connection.SessionLocal()

        # Initialize services
        self.us_service = USService(self.db_manager)

        # Initialize tools
        self.tools = self._initialize_tools()

        # Initialize resources
        self.resources = self._initialize_resources()

        logger.info("MCP Tools Executor initialized")

    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize all MCP tools"""
        return {
            "build_3d": Build3DTool(
                db_session=self.db_session,
                config=self.config,
            ),
            "filter": FilterTool(
                db_session=self.db_session,
                config=self.config,
            ),
            "export": ExportTool(
                db_session=self.db_session,
                config=self.config,
            ),
            "position": PositionTool(
                db_session=self.db_session,
                config=self.config,
            ),
            "material": MaterialTool(
                db_session=self.db_session,
                config=self.config,
            ),
        }

    def _initialize_resources(self) -> Dict[str, Any]:
        """Initialize all MCP resources"""
        return {
            "graphml": GraphMLResource(
                db_session=self.db_session,
                config=self.config,
            ),
            "us": USResource(
                us_service=self.us_service,
                config=self.config,
            ),
        }

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool by name

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool = self.tools[tool_name]

        try:
            result = await tool.execute(arguments)
            logger.info(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}", exc_info=True)
            raise

    async def read_resource(
        self,
        resource_type: str,
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Read a resource

        Args:
            resource_type: Type of resource (graphml, us, etc.)
            resource_id: Resource ID (optional)

        Returns:
            Resource data
        """
        if resource_type not in self.resources:
            raise ValueError(f"Unknown resource type: {resource_type}")

        resource = self.resources[resource_type]

        try:
            result = await resource.read(resource_id)
            logger.info(f"Resource {resource_type} read successfully")
            return result
        except Exception as e:
            logger.error(f"Resource {resource_type} read failed: {e}", exc_info=True)
            raise

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools with their descriptions

        Returns:
            List of tool descriptions
        """
        return [
            tool.to_tool_description()
            for tool in self.tools.values()
        ]

    def get_available_resources(self) -> List[Dict[str, Any]]:
        """
        Get list of available resources with their descriptions

        Returns:
            List of resource descriptions
        """
        return [
            resource.to_resource_description()
            for resource in self.resources.values()
        ]

    def close(self):
        """Cleanup resources"""
        if hasattr(self, 'db_session'):
            self.db_session.close()
        logger.info("MCP Tools Executor closed")


# Singleton instance for web app
_executor_instance: Optional[MCPToolsExecutor] = None


def get_executor(database_url: Optional[str] = None) -> MCPToolsExecutor:
    """
    Get singleton MCP tools executor instance

    Args:
        database_url: Database URL (uses default if None)

    Returns:
        MCPToolsExecutor instance
    """
    global _executor_instance

    if _executor_instance is None:
        _executor_instance = MCPToolsExecutor(database_url)

    return _executor_instance
