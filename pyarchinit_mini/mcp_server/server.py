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
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.server.models import InitializationOptions
    from mcp.types import (
        TextContent,
        ImageContent,
        EmbeddedResource,
        ServerCapabilities,
        Tool,
        Resource,
    )
    MCP_AVAILABLE = True
except ImportError:
    # MCP SDK not installed - provide stub for development
    logging.warning("MCP SDK not installed. Server functionality will be limited.")
    MCP_AVAILABLE = False

    class Server:  # type: ignore
        pass

    stdio_server = None  # type: ignore
    InitializationOptions = None  # type: ignore
    TextContent = None  # type: ignore
    ImageContent = None  # type: ignore
    EmbeddedResource = None  # type: ignore
    ServerCapabilities = None  # type: ignore
    Tool = None  # type: ignore
    Resource = None  # type: ignore


from .config import MCPConfig
from ..database.connection import DatabaseConnection
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
from .tools.import_excel_tool import ImportExcelTool
from .tools.upload_file_tool import UploadFileTool
from .tools.create_harris_matrix_tool import CreateHarrisMatrixTool
from .tools.configure_em_nodes_tool import ConfigureEMNodesTool
from .tools.create_database_tool import CreateDatabaseTool
from .tools.pyarchinit_sync_tool import PyArchInitSyncTool
from .tools.chatgpt_search_tool import ChatGPTSearchTool
from .tools.chatgpt_fetch_tool import ChatGPTFetchTool
from .tools.database_manager_tool import DatabaseManagerTool
from .tools.data_management_tool import DataManagementTool
from .tools.service_management_tool import ServiceManagementTool
from .tools.export_harris_matrix_graphml_tool import ExportHarrisMatrixGraphMLTool
from .tools.validate_stratigraphic_relationships_tool import ValidateStratigraphicRelationshipsTool
from .tools.validate_relationship_format_tool import ValidateRelationshipFormatTool
from .tools.generate_report_tool import GenerateReportTool
from .tools.validate_relationship_integrity_tool import ValidateRelationshipIntegrityTool
from .tools.media_management_tool import MediaManagementTool
from .tools.thesaurus_management_tool import ThesaurusManagementTool
from .tools.data_import_parser_tool import DataImportParserTool

from .prompts.stratigraphic_model_prompt import StratigraphicModelPrompt
from .prompts.period_visualization_prompt import PeriodVisualizationPrompt
from .prompts.us_description_prompt import USDescriptionPrompt


logger = logging.getLogger(__name__)


class PyArchInitMCPServer:
    """
    MCP Server for PyArchInit-Mini

    Exposes:
    - 5 Resources (GraphML, US, Periods, Relationships, Sites)
    - 23 Tools (build_3d, filter, export, position, material, import_excel, create_harris_matrix,
                configure_em_nodes, create_database, pyarchinit_sync, search, fetch,
                manage_database_connections, manage_data, manage_services, export_harris_matrix_graphml,
                validate_stratigraphic_relationships, validate_relationship_format, generate_report,
                validate_relationship_integrity, manage_media, manage_thesaurus, import_data)
    - 3 Prompts (stratigraphic_model, period_visualization, us_description)

    Architecture:
        Claude AI / ChatGPT ↔ PyArchInit MCP Server ↔ Blender MCP Addon
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
        db_connection = DatabaseConnection(self.config.database_url)
        self.db_manager = DatabaseManager(db_connection)
        self.db_session = db_connection.SessionLocal()  # Create session for resources/tools
        self.site_service = SiteService(self.db_manager)
        self.us_service = USService(self.db_manager)
        self.periodizzazione_service = PeriodizzazioneService(self.db_manager)

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
            db_session=self.db_session,
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
            db_session=self.db_session,
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
            db_session=self.db_session,
            config=self.config,
        )

        # Filter Tool
        self.tools["filter"] = FilterTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Export Tool
        self.tools["export"] = ExportTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Position Tool
        self.tools["position"] = PositionTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Material Tool
        self.tools["material"] = MaterialTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Import Excel Tool
        self.tools["import_excel"] = ImportExcelTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Upload File Tool
        self.tools["upload_file"] = UploadFileTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Create Harris Matrix Tool
        self.tools["create_harris_matrix"] = CreateHarrisMatrixTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Configure EM Nodes Tool
        self.tools["configure_em_nodes"] = ConfigureEMNodesTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Create Database Tool
        self.tools["create_database"] = CreateDatabaseTool(
            db_session=self.db_session,
            config=self.config,
        )

        # PyArchInit Sync Tool (Import/Export)
        self.tools["pyarchinit_sync"] = PyArchInitSyncTool(
            db_session=self.db_session,
            config=self.config,
        )

        # ChatGPT Search Tool
        self.tools["search"] = ChatGPTSearchTool(
            db_session=self.db_session,
            config=self.config,
        )

        # ChatGPT Fetch Tool
        self.tools["fetch"] = ChatGPTFetchTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Database Manager Tool
        self.tools["manage_database_connections"] = DatabaseManagerTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Data Management Tool (CRUD + Validation)
        self.tools["manage_data"] = DataManagementTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Service Management Tool (Start/Stop services)
        self.tools["manage_services"] = ServiceManagementTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Export Harris Matrix GraphML Tool (Auto-export from database)
        self.tools["export_harris_matrix_graphml"] = ExportHarrisMatrixGraphMLTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Validate Stratigraphic Relationships Tool (Data integrity)
        self.tools["validate_stratigraphic_relationships"] = ValidateStratigraphicRelationshipsTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Validate Relationship Format Tool (Symbols vs Textual)
        self.tools["validate_relationship_format"] = ValidateRelationshipFormatTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Generate Report Tool (Comprehensive reports and summaries)
        self.tools["generate_report"] = GenerateReportTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Validate Relationship Integrity Tool (Bidirectional integrity checks)
        self.tools["validate_relationship_integrity"] = ValidateRelationshipIntegrityTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Media Management Tool (Upload and manage media files)
        self.tools["manage_media"] = MediaManagementTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Thesaurus Management Tool (Controlled vocabularies)
        self.tools["manage_thesaurus"] = ThesaurusManagementTool(
            db_session=self.db_session,
            config=self.config,
        )

        # Data Import Parser Tool (Automatic data import from CSV, Excel, JSON, XML)
        self.tools["import_data"] = DataImportParserTool(
            db_session=self.db_session,
            config=self.config,
        )

        logger.info(f"Registered {len(self.tools)} tools")

    def _register_prompts(self):
        """Register MCP Prompts"""
        logger.info("Registering MCP Prompts...")

        # Stratigraphic Model Prompt
        self.prompts["stratigraphic_model"] = StratigraphicModelPrompt(
            db_session=self.db_session,
            config=self.config,
        )

        # Period Visualization Prompt
        self.prompts["period_visualization"] = PeriodVisualizationPrompt(
            db_session=self.db_session,
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
                resources = []
                for resource in self.resources.values():
                    desc = resource.to_resource_description()
                    resources.append(
                        Resource(
                            uri=desc.uri,
                            name=desc.name,
                            description=desc.description,
                            mimeType=desc.mime_type,
                        )
                    )
                return resources

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
                tools = []
                for tool in self.tools.values():
                    desc = tool.to_tool_description()
                    tools.append(
                        Tool(
                            name=desc.name,
                            description=desc.description,
                            inputSchema=desc.input_schema,
                        )
                    )
                return tools

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
                    self._create_init_options(),
                )

        elif self.config.mcp_transport == "tcp":
            # TCP transport not yet implemented
            raise NotImplementedError("TCP transport not yet implemented")

        else:
            raise ValueError(f"Invalid transport: {self.config.mcp_transport}")

    def _create_init_options(self):
        """
        Create initialization options for MCP server

        Returns:
            InitializationOptions with server name, version, and capabilities
        """
        if InitializationOptions is None:
            raise RuntimeError("MCP SDK not installed")

        return InitializationOptions(
            server_name=self.config.mcp_server_name,
            server_version=self.config.mcp_server_version,
            capabilities=ServerCapabilities(
                resources={},
                tools={},
                prompts={},
            ),
        )

    def stop(self):
        """Stop the MCP server"""
        logger.info("Stopping MCP Server...")
        # Cleanup resources
        if hasattr(self, "db_session"):
            self.db_session.close()


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
