"""
MCP Server Configuration

Configuration dataclass for PyArchInit MCP Server.
"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)


def _get_default_database_url() -> str:
    """
    Get default database URL from ConnectionManager or create default database

    Priority:
    1. DATABASE_URL environment variable (for backward compatibility)
    2. Active connection from ConnectionManager
    3. Default database in ~/.pyarchinit-mini/databases/default.db

    Returns:
        Database URL string
    """
    # 1. Check environment variable first (backward compatibility)
    env_db = os.getenv("DATABASE_URL")
    if env_db:
        logger.info(f"Using DATABASE_URL from environment: {env_db}")
        return env_db

    try:
        # 2. Try to get from ConnectionManager
        from pyarchinit_mini.config.connection_manager import get_connection_manager
        from datetime import datetime

        conn_manager = get_connection_manager()
        connections = conn_manager.list_connections()

        # Find most recently used connection based on last_used timestamp
        if connections:
            # Sort by last_used timestamp (most recent first)
            sorted_connections = sorted(
                connections,
                key=lambda x: datetime.fromisoformat(x.get('last_used', '1970-01-01T00:00:00')),
                reverse=True
            )

            most_recent_conn = sorted_connections[0]
            db_url = conn_manager.get_connection_string(most_recent_conn['name'])
            if db_url:
                logger.info(f"Using most recently used database from ConnectionManager: {most_recent_conn['name']} (last used: {most_recent_conn.get('last_used', 'unknown')})")
                return db_url

    except Exception as e:
        logger.warning(f"Could not load from ConnectionManager: {e}")

    # 3. Create default database in ~/.pyarchinit_mini/
    home_dir = Path.home() / '.pyarchinit_mini'
    db_dir = home_dir / 'data'
    db_dir.mkdir(parents=True, exist_ok=True)

    default_db_path = db_dir / 'pyarchinit_mini.db'
    db_url = f"sqlite:///{default_db_path}"

    logger.info(f"Using default database: {db_url}")

    # Save to ConnectionManager for future use
    try:
        from pyarchinit_mini.config.connection_manager import get_connection_manager
        conn_manager = get_connection_manager()
        conn_manager.add_connection(
            name="Default Database",
            db_type="sqlite",
            connection_string=db_url,
            description="Default PyArchInit database in user home directory"
        )
        logger.info("Saved default database to ConnectionManager")
    except Exception as e:
        logger.warning(f"Could not save to ConnectionManager: {e}")

    return db_url


@dataclass
class MCPConfig:
    """Configuration for PyArchInit MCP Server"""

    # Database
    database_url: str = field(default_factory=_get_default_database_url)

    # Blender Connection
    blender_host: str = field(
        default_factory=lambda: os.getenv("BLENDER_HOST", "localhost")
    )
    blender_port: int = field(
        default_factory=lambda: int(os.getenv("BLENDER_PORT", "9876"))
    )
    blender_timeout: int = 30  # seconds

    # WebSocket Streaming
    websocket_enabled: bool = True
    websocket_port: int = field(
        default_factory=lambda: int(os.getenv("WEBSOCKET_PORT", "5002"))
    )

    # MCP Server
    mcp_server_name: str = "pyarchinit-mini"
    mcp_server_version: str = "1.0.0"
    mcp_transport: str = "stdio"  # "stdio" | "tcp" | "sse" | "http"
    mcp_host: str = field(
        default_factory=lambda: os.getenv("MCP_HOST", "0.0.0.0")
    )
    mcp_port: int = field(
        default_factory=lambda: int(os.getenv("MCP_PORT", "8765"))
    )

    # 3D Builder Settings
    default_positioning: str = "graphml"  # "graphml" | "grid" | "force_directed"
    default_layer_spacing: float = 0.5  # Blender units
    default_grid_spacing: float = 3.0  # Blender units
    enable_auto_color: bool = True
    enable_auto_material: bool = True

    # Export Settings
    export_format: str = "gltf"  # "gltf" | "glb"
    export_dir: str = field(
        default_factory=lambda: os.getenv(
            "EXPORT_DIR", "/tmp/pyarchinit_3d_exports"
        )
    )

    # Caching
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds (1 hour)

    # Logging
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_file: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization"""
        # Ensure export directory exists
        os.makedirs(self.export_dir, exist_ok=True)

        # Validate positioning mode
        valid_positioning = ["graphml", "grid", "force_directed"]
        if self.default_positioning not in valid_positioning:
            raise ValueError(
                f"Invalid positioning mode: {self.default_positioning}. "
                f"Must be one of {valid_positioning}"
            )

        # Validate export format
        valid_formats = ["gltf", "glb"]
        if self.export_format not in valid_formats:
            raise ValueError(
                f"Invalid export format: {self.export_format}. "
                f"Must be one of {valid_formats}"
            )

        # Validate MCP transport
        valid_transports = ["stdio", "tcp", "sse", "http"]
        if self.mcp_transport not in valid_transports:
            raise ValueError(
                f"Invalid MCP transport: {self.mcp_transport}. "
                f"Must be one of {valid_transports}"
            )

        # If network transport (tcp/sse/http), ensure host and port are set
        if self.mcp_transport in ["tcp", "sse", "http"]:
            if not self.mcp_host or not self.mcp_port:
                raise ValueError(
                    f"MCP host and port must be set when using {self.mcp_transport} transport"
                )


# Default instance
default_config = MCPConfig()
