"""
MCP Server entry point for PyArchInit-Mini

Allows running the MCP server as a Python module:
    python -m pyarchinit_mini.mcp_server

Supports multiple transport modes:
    - stdio: For Claude Desktop (default)
    - sse/http: For ChatGPT and web integrations

Usage:
    # Run with stdio transport (Claude Desktop)
    python -m pyarchinit_mini.mcp_server

    # Run with HTTP/SSE transport (ChatGPT)
    MCP_TRANSPORT=sse python -m pyarchinit_mini.mcp_server

    # Or set port
    MCP_TRANSPORT=sse MCP_PORT=8765 python -m pyarchinit_mini.mcp_server
"""

import sys
from .config import MCPConfig


def main():
    """Main entry point - routes to appropriate transport"""
    config = MCPConfig()

    if config.mcp_transport in ["sse", "http"]:
        # Use HTTP/SSE server for ChatGPT
        from .http_server import main as http_main
        http_main()
    elif config.mcp_transport == "stdio":
        # Use stdio server for Claude Desktop
        from .server import main as stdio_main
        stdio_main()
    else:
        print(f"Error: Unknown transport '{config.mcp_transport}'", file=sys.stderr)
        print("Valid transports: stdio, sse, http", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
