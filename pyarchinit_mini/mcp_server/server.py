"""
PyArchInit MCP Server

Main MCP server implementation providing Resources, Tools, and Prompts
for Claude AI to interact with stratigraphic data and Blender 3D visualization.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    from mcp import Server, Resource, Tool
    from mcp.server import stdio_server
    from mcp.server.models import InitializationOptions
    from mcp.types import TextContent, ImageContent, EmbeddedResource
except ImportError:
    # MCP SDK not installed - provide stub for development
    logging.warning("MCP SDK not installed. Server functionality will be limited.")

    class Server:  # type: ignore
        pass

    class Resource:  # type: ignore
        pass

    class Tool:  # type: ignore
        pass

    stdio_server = None  # type: ignore
    InitializationOptions = None  # type: ignore
    TextContent = None  # type: ignore
    ImageContent = None  # type: ignore
    EmbeddedResource = None  # type: ignore


from .config import MCPConfig
from ..database.manager import DatabaseManager
from ..services.site_service import SiteService
from ..services.us_service import USService
from ..services.periodizzazione_service import PeriodizzazioneService

# Import resources, tools, prompts
from .resources.graphml_resource import GraphMLResource
from .resources.us_resource import USResource
from .resources.periods_resource import PeriodsResource
from .resources.relationships_resource import RelationshipsResource
from .resources.sites_resource import SitesResource

from .tools.build_3d_tool import Build3DTool
from .tools.filter_tool import FilterTool
from .tools.export_tool import ExportTool
from .tools.position_tool import PositionTool
from .tools.material_tool import MaterialTool

from .prompts.stratigraphic_model_prompt import StratigraphicModelPrompt
from .prompts.period_visualization_prompt import PeriodVisualizationPrompt
from .prompts.us_description_prompt import USDescriptionPrompt


logger = logging.getLogger(__name__)


class PyArchInitMCPServer:
    """
    MCP Server for PyArchInit-Mini

    Exposes:
    - 5 Resources (GraphML, US, Periods, Relationships, Sites)
    - 5 Tools (build_3d, filter, export, position, material)
    - 3 Prompts (stratigraphic_model, period_visualization, us_description)

    Architecture:
        Claude AI ↔ PyArchInit MCP Server ↔ Blender MCP Addon
    """

    def __init__(self, config: Optional[MCPConfig] = None):
        """
        Initialize PyArchInit MCP Server

        Args:
            config: MCP configuration (uses default if None)
        """
        self.config = config or MCPConfig()
        self._setup_logging()

        # Database and services
        self.db_manager = DatabaseManager(self.config.database_url)
        self.site_service = SiteService(self.db_manager.get_session())
        self.us_service = USService(self.db_manager.get_session())
        self.periodizzazione_service = PeriodizzazioneService(
            self.db_manager.get_session()
        )

        # MCP Server instance
        self.server = Server(self.config.mcp_server_name)

        # Resources
        self.resources: Dict[str, Any] = {}
        self.tools: Dict[str, Any] = {}
        self.prompts: Dict[str, Any] = {}

        # Initialize components
        self._register_resources()
        self._register_tools()
        self._register_prompts()

        logger.info(
            f"PyArchInit MCP Server initialized "
            f"(v{self.config.mcp_server_version})"
        )

    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            filename=self.config.log_file,
        )

    def _register_resources(self):
        """Register MCP Resources"""
        logger.info("Registering MCP Resources...")

        # GraphML Resource
        self.resources["graphml"] = GraphMLResource(
            db_session=self.db_manager.get_session(),
            config=self.config,
        )

        # US Resource
        self.resources["us"] = USResource(
            us_service=self.us_service,
            config=self.config,
        )

        # Periods Resource
        self.resources["periods"] = PeriodsResource(
            periodizzazione_service=self.periodizzazione_service,
            config=self.config,
        )

        # Relationships Resource
        self.resources["relationships"] = RelationshipsResource(
            db_session=self.db_manager.get_session(),
            config=self.config,
        )

        # Sites Resource
        self.resources["sites"] = SitesResource(
            site_service=self.site_service,
            config=self.config,
        )

        logger.info(f"Registered {len(self.resources)} resources")

    def _register_tools(self):
        """Register MCP Tools"""
        logger.info("Registering MCP Tools...")

        # Build 3D Tool
        self.tools["build_3d"] = Build3DTool(
            db_session=self.db_manager.get_session(),
            config=self.config,
        )

        # Filter Tool
        self.tools["filter"] = FilterTool(
            db_session=self.db_manager.get_session(),
            config=self.config,
        )

        # Export Tool
        self.tools["export"] = ExportTool(
            db_session=self.db_manager.get_session(),
            config=self.config,
        )

        # Position Tool
        self.tools["position"] = PositionTool(
            db_session=self.db_manager.get_session(),
            config=self.config,
        )

        # Material Tool
        self.tools["material"] = MaterialTool(
            db_session=self.db_manager.get_session(),
            config=self.config,
        )

        logger.info(f"Registered {len(self.tools)} tools")

    def _register_prompts(self):
        """Register MCP Prompts"""
        logger.info("Registering MCP Prompts...")

        # Stratigraphic Model Prompt
        self.prompts["stratigraphic_model"] = StratigraphicModelPrompt(
            db_session=self.db_manager.get_session(),
            config=self.config,
        )

        # Period Visualization Prompt
        self.prompts["period_visualization"] = PeriodVisualizationPrompt(
            db_session=self.db_manager.get_session(),
            config=self.config,
        )

        # US Description Prompt
        self.prompts["us_description"] = USDescriptionPrompt(
            us_service=self.us_service,
            config=self.config,
        )

        logger.info(f"Registered {len(self.prompts)} prompts")

    async def run(self):
        """
        Run the MCP server

        Uses stdio transport by default for Claude Desktop integration
        """
        logger.info(f"Starting MCP Server (transport: {self.config.mcp_transport})")

        if self.config.mcp_transport == "stdio":
            if stdio_server is None:
                raise RuntimeError(
                    "MCP SDK not installed. Install with: pip install mcp"
                )

            # Setup MCP server handlers
            @self.server.list_resources()
            async def handle_list_resources():
                """List available resources"""
                return [
                    resource.to_resource_description()
                    for resource in self.resources.values()
                ]

            @self.server.read_resource()
            async def handle_read_resource(uri: str):
                """Read resource by URI"""
                # Parse URI: resource://type/id
                parts = uri.replace("resource://", "").split("/")
                resource_type = parts[0]
                resource_id = parts[1] if len(parts) > 1 else None

                if resource_type not in self.resources:
                    raise ValueError(f"Unknown resource type: {resource_type}")

                return await self.resources[resource_type].read(resource_id)

            @self.server.list_tools()
            async def handle_list_tools():
                """List available tools"""
                return [tool.to_tool_description() for tool in self.tools.values()]

            @self.server.call_tool()
            async def handle_call_tool(name: str, arguments: Dict[str, Any]):
                """Call a tool"""
                if name not in self.tools:
                    raise ValueError(f"Unknown tool: {name}")

                return await self.tools[name].execute(arguments)

            @self.server.list_prompts()
            async def handle_list_prompts():
                """List available prompts"""
                return [
                    prompt.to_prompt_description() for prompt in self.prompts.values()
                ]

            @self.server.get_prompt()
            async def handle_get_prompt(
                name: str, arguments: Optional[Dict[str, str]] = None
            ):
                """Get a prompt"""
                if name not in self.prompts:
                    raise ValueError(f"Unknown prompt: {name}")

                return await self.prompts[name].get(arguments or {})

            # Run stdio server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.config.mcp_server_name,
                        server_version=self.config.mcp_server_version,
                    ),
                )

        elif self.config.mcp_transport == "tcp":
            # TCP transport not yet implemented
            raise NotImplementedError("TCP transport not yet implemented")

        else:
            raise ValueError(f"Invalid transport: {self.config.mcp_transport}")

    def stop(self):
        """Stop the MCP server"""
        logger.info("Stopping MCP Server...")
        # Cleanup resources
        if hasattr(self, "db_manager"):
            self.db_manager.close()


# Convenience function to run server
async def run_mcp_server(config: Optional[MCPConfig] = None):
    """
    Run PyArchInit MCP Server

    Args:
        config: Server configuration (uses default if None)

    Example:
        ```python
        import asyncio
        from pyarchinit_mini.mcp_server import run_mcp_server

        asyncio.run(run_mcp_server())
        ```
    """
    server = PyArchInitMCPServer(config)
    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        server.stop()


def main():
    """CLI entry point for MCP server"""
    import sys

    config = MCPConfig()

    # Parse command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == "--version":
            print(f"PyArchInit MCP Server v{config.mcp_server_version}")
            sys.exit(0)
        elif sys.argv[1] == "--help":
            print(
                """
PyArchInit MCP Server

Usage:
    pyarchinit-mcp-server [OPTIONS]

Options:
    --version       Show version
    --help          Show this help message
    --transport     Transport type (stdio | tcp) [default: stdio]
    --host          Host for TCP transport
    --port          Port for TCP transport
    --log-level     Logging level (DEBUG | INFO | WARNING | ERROR)

Environment Variables:
    DATABASE_URL        Database connection URL
    BLENDER_HOST        Blender host [default: localhost]
    BLENDER_PORT        Blender port [default: 9876]
    WEBSOCKET_PORT      WebSocket port [default: 5002]
    LOG_LEVEL           Logging level [default: INFO]
    EXPORT_DIR          Export directory [default: /tmp/pyarchinit_3d_exports]

Example:
    pyarchinit-mcp-server --log-level DEBUG
"""
            )
            sys.exit(0)
        elif sys.argv[1] == "--transport":
            config.mcp_transport = sys.argv[2]
        elif sys.argv[1] == "--log-level":
            config.log_level = sys.argv[2]

    # Run server
    asyncio.run(run_mcp_server(config))


if __name__ == "__main__":
    main()
