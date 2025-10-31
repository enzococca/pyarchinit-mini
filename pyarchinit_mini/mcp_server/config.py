"""
MCP Server Configuration

Configuration dataclass for PyArchInit MCP Server.
"""

from dataclasses import dataclass, field
from typing import Optional
import os


@dataclass
class MCPConfig:
    """Configuration for PyArchInit MCP Server"""

    # Database
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", "sqlite:///data/pyarchinit_mini.db"
        )
    )

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
    mcp_transport: str = "stdio"  # or "tcp"
    mcp_host: Optional[str] = None
    mcp_port: Optional[int] = None

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
        valid_transports = ["stdio", "tcp"]
        if self.mcp_transport not in valid_transports:
            raise ValueError(
                f"Invalid MCP transport: {self.mcp_transport}. "
                f"Must be one of {valid_transports}"
            )

        # If TCP transport, ensure host and port are set
        if self.mcp_transport == "tcp":
            if not self.mcp_host or not self.mcp_port:
                raise ValueError(
                    "MCP host and port must be set when using TCP transport"
                )


# Default instance
default_config = MCPConfig()
