"""
PyArchInit-Mini MCP Server

MCP (Model Context Protocol) server implementation for PyArchInit-Mini,
providing Claude AI with access to stratigraphic data, GraphML exports,
and integration with Blender for 3D visualization.

Architecture:
- Resources: Provide context data (GraphML, US, Periods, Relationships, Sites)
- Tools: Execute actions (build_3d, filter, export, position, material)
- Prompts: Pre-defined templates for common tasks

Integration:
- Claude AI ↔ PyArchInit MCP Server ↔ Blender MCP Addon
"""

__version__ = "1.0.0"

from .server import PyArchInitMCPServer, MCPConfig, main
from .blender_client import BlenderClient, test_blender_connection

__all__ = ["PyArchInitMCPServer", "MCPConfig", "BlenderClient", "test_blender_connection", "main"]
