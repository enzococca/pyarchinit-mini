#!/bin/bash
# PyArchInit MCP HTTP Server Launcher
# Simple wrapper to start the MCP HTTP server

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate venv and run server
cd "$SCRIPT_DIR"
exec .venv/bin/python3 -m pyarchinit_mini.mcp_server.http_server "$@"
