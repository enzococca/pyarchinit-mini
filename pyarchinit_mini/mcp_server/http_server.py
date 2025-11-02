"""
PyArchInit MCP Server - HTTP/SSE Transport

FastAPI wrapper for PyArchInit MCP Server to enable ChatGPT integration
via Server-Sent Events (SSE) or HTTP transport.

Usage:
    # Run server
    python -m pyarchinit_mini.mcp_server.http_server

    # Or with custom config
    MCP_TRANSPORT=sse MCP_PORT=8765 python -m pyarchinit_mini.mcp_server.http_server
"""

import logging
import asyncio
import json
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

try:
    from mcp.server.sse import SseServerTransport
    from mcp.types import (
        JSONRPCRequest,
        JSONRPCResponse,
        JSONRPCError,
        ErrorData,
    )
    MCP_AVAILABLE = True
except ImportError:
    logging.warning("MCP SDK not installed. Install with: pip install mcp")
    MCP_AVAILABLE = False
    SseServerTransport = None

from .server import PyArchInitMCPServer
from .config import MCPConfig


logger = logging.getLogger(__name__)


class MCPHTTPServer:
    """
    HTTP/SSE wrapper for PyArchInit MCP Server

    Exposes MCP server via HTTP endpoints for ChatGPT integration:
    - GET /mcp - SSE endpoint for bidirectional communication
    - POST /mcp/messages - HTTP endpoint for messages
    - GET /health - Health check endpoint
    """

    def __init__(self, config: Optional[MCPConfig] = None):
        """
        Initialize HTTP MCP Server

        Args:
            config: MCP configuration
        """
        if not MCP_AVAILABLE:
            raise RuntimeError("MCP SDK not installed. Install with: pip install mcp")

        self.config = config or MCPConfig()
        self.mcp_server: Optional[PyArchInitMCPServer] = None
        self.transport: Optional[SseServerTransport] = None

        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    async def start_mcp_server(self):
        """Initialize and start the MCP server"""
        logger.info("Initializing PyArchInit MCP Server...")
        self.mcp_server = PyArchInitMCPServer(self.config)

        # Setup handlers
        await self._setup_handlers()

        logger.info("MCP Server initialized successfully")

    async def _setup_handlers(self):
        """Setup MCP server request handlers"""
        if not self.mcp_server:
            raise RuntimeError("MCP server not initialized")

        # List resources handler
        @self.mcp_server.server.list_resources()
        async def handle_list_resources():
            """List available resources"""
            return [
                resource.to_resource_description()
                for resource in self.mcp_server.resources.values()
            ]

        # Read resource handler
        @self.mcp_server.server.read_resource()
        async def handle_read_resource(uri: str):
            """Read resource by URI"""
            parts = uri.replace("resource://", "").split("/")
            resource_type = parts[0]
            resource_id = parts[1] if len(parts) > 1 else None

            if resource_type not in self.mcp_server.resources:
                raise ValueError(f"Unknown resource type: {resource_type}")

            return await self.mcp_server.resources[resource_type].read(resource_id)

        # List tools handler
        @self.mcp_server.server.list_tools()
        async def handle_list_tools():
            """List available tools"""
            return [
                tool.to_tool_description()
                for tool in self.mcp_server.tools.values()
            ]

        # Call tool handler
        @self.mcp_server.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]):
            """Call a tool"""
            if name not in self.mcp_server.tools:
                raise ValueError(f"Unknown tool: {name}")

            return await self.mcp_server.tools[name].execute(arguments)

        # List prompts handler
        @self.mcp_server.server.list_prompts()
        async def handle_list_prompts():
            """List available prompts"""
            return [
                prompt.to_prompt_description()
                for prompt in self.mcp_server.prompts.values()
            ]

        # Get prompt handler
        @self.mcp_server.server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: Optional[Dict[str, str]] = None
        ):
            """Get a prompt"""
            if name not in self.mcp_server.prompts:
                raise ValueError(f"Unknown prompt: {name}")

            return await self.mcp_server.prompts[name].get(arguments or {})

    async def stop_mcp_server(self):
        """Stop the MCP server and cleanup resources"""
        logger.info("Stopping MCP Server...")
        if self.mcp_server:
            self.mcp_server.stop()
        logger.info("MCP Server stopped")


# Global server instance
mcp_http_server: Optional[MCPHTTPServer] = None


async def mcp_sse_handler(scope, receive, send):
    """
    ASGI handler for MCP SSE endpoint

    Provides Server-Sent Events stream for bidirectional MCP communication.
    ChatGPT connects to this endpoint to communicate with the MCP server.
    """
    if not mcp_http_server or not mcp_http_server.mcp_server:
        # Return 503 error
        await send({
            'type': 'http.response.start',
            'status': 503,
            'headers': [[b'content-type', b'text/plain']],
        })
        await send({
            'type': 'http.response.body',
            'body': b'MCP server not initialized',
        })
        return

    try:
        # Create SSE transport
        transport = SseServerTransport("/mcp/messages")

        # Connect transport to MCP server
        async with transport.connect_sse(scope, receive, send) as streams:
            # Run MCP server with SSE transport
            await mcp_http_server.mcp_server.server.run(
                streams[0],  # read stream
                streams[1],  # write stream
                mcp_http_server.mcp_server._create_init_options()
            )
    except Exception as e:
        logger.error(f"Error in SSE stream: {e}", exc_info=True)
        # Try to send error if connection still open
        try:
            await send({
                'type': 'http.response.start',
                'status': 500,
                'headers': [[b'content-type', b'text/plain']],
            })
            await send({
                'type': 'http.response.body',
                'body': f"Error: {str(e)}".encode(),
            })
        except:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager

    Handles startup and shutdown of MCP server
    """
    global mcp_http_server

    # Startup
    config = MCPConfig()
    mcp_http_server = MCPHTTPServer(config)
    await mcp_http_server.start_mcp_server()
    logger.info(f"MCP HTTP Server started on {config.mcp_host}:{config.mcp_port}")

    yield

    # Shutdown
    if mcp_http_server:
        await mcp_http_server.stop_mcp_server()


# Create FastAPI app
app = FastAPI(
    title="PyArchInit MCP Server",
    description="MCP Server for archaeological data management and 3D visualization",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for ChatGPT access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to ChatGPT domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add ASGI route for MCP SSE endpoint
# We need to add this as a raw route that passes through to ASGI handler
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response

async def mcp_sse_endpoint(request: Request):
    """Wrapper to convert FastAPI request to ASGI handler"""
    # Call the raw ASGI handler with scope, receive, send from request
    await mcp_sse_handler(request.scope, request.receive, request._send)
    # Return empty response (handler has already sent response)
    return Response()

app.add_route("/mcp", mcp_sse_endpoint, methods=["GET", "POST"])

# Add /sse/ endpoint for ChatGPT MCP integration
app.add_route("/sse/", mcp_sse_endpoint, methods=["GET", "POST"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "pyarchinit-mcp-server",
        "version": "1.0.0",
        "transport": "sse/http"
    }


# OpenAI/ChatGPT REST API endpoints
@app.get("/mcp/health")
async def mcp_health_check():
    """MCP health check endpoint for OpenAI/ChatGPT"""
    if not mcp_http_server or not mcp_http_server.mcp_server:
        raise HTTPException(status_code=503, detail="MCP server not initialized")

    return {
        "status": "ok",
        "tools_cached": len(mcp_http_server.mcp_server.tools)
    }


@app.get("/mcp/tools/list")
async def mcp_list_tools():
    """List available tools in OpenAI/ChatGPT format"""
    if not mcp_http_server or not mcp_http_server.mcp_server:
        raise HTTPException(status_code=503, detail="MCP server not initialized")

    try:
        tools = []
        for tool_name, tool in mcp_http_server.mcp_server.tools.items():
            tool_desc = tool.to_tool_description()
            tools.append({
                "name": tool_desc.name,
                "description": tool_desc.description,
                "input_schema": tool_desc.input_schema
            })

        return {"tools": tools}

    except Exception as e:
        logger.error(f"Error listing tools: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/call")
async def mcp_call_tool(request: Request):
    """Execute a tool in OpenAI/ChatGPT format"""
    if not mcp_http_server or not mcp_http_server.mcp_server:
        raise HTTPException(status_code=503, detail="MCP server not initialized")

    try:
        data = await request.json()
        tool_name = data.get("name")
        arguments = data.get("arguments", {})

        if not tool_name:
            raise HTTPException(status_code=400, detail="Missing 'name' parameter")

        if tool_name not in mcp_http_server.mcp_server.tools:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

        logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")

        # Execute the tool
        result = await mcp_http_server.mcp_server.tools[tool_name].execute(arguments)

        return result

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error calling tool: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/capabilities")
async def get_capabilities():
    """
    Capabilities discovery endpoint

    Returns all available MCP resources, tools, and prompts.
    Useful for debugging, documentation, and auto-discovery.
    """
    if not mcp_http_server or not mcp_http_server.mcp_server:
        raise HTTPException(status_code=503, detail="MCP server not initialized")

    try:
        return {
            "server": {
                "name": mcp_http_server.config.mcp_server_name,
                "version": mcp_http_server.config.mcp_server_version,
                "transport": "sse/http",
                "protocol": "MCP 2024-11-05",
            },
            "capabilities": {
                "resources": {
                    "count": len(mcp_http_server.mcp_server.resources),
                    "available": list(mcp_http_server.mcp_server.resources.keys()),
                },
                "tools": {
                    "count": len(mcp_http_server.mcp_server.tools),
                    "available": list(mcp_http_server.mcp_server.tools.keys()),
                },
                "prompts": {
                    "count": len(mcp_http_server.mcp_server.prompts),
                    "available": list(mcp_http_server.mcp_server.prompts.keys()),
                },
            },
            "endpoints": {
                "mcp_sse": {
                    "path": "/mcp",
                    "method": "GET",
                    "description": "SSE endpoint for MCP protocol communication",
                },
                "mcp_messages": {
                    "path": "/mcp/messages",
                    "method": "POST",
                    "description": "POST endpoint for MCP messages",
                },
                "health": {
                    "path": "/health",
                    "method": "GET",
                    "description": "Health check endpoint",
                },
                "capabilities": {
                    "path": "/capabilities",
                    "method": "GET",
                    "description": "This endpoint - auto-discovery",
                },
                "docs": {
                    "path": "/docs",
                    "method": "GET",
                    "description": "Interactive API documentation",
                },
            },
            "usage": {
                "chatgpt_url": "https://YOUR_SERVER/mcp",
                "test_commands": [
                    "GET /health - Check server status",
                    "GET /capabilities - List available capabilities",
                    "GET /mcp - Connect via SSE (ChatGPT)",
                ],
            },
        }

    except Exception as e:
        logger.error(f"Error getting capabilities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/messages")
async def mcp_messages_endpoint(request: Request):
    """
    MCP messages endpoint for HTTP POST requests

    Receives MCP messages from ChatGPT via POST requests.
    Used in conjunction with SSE endpoint for bidirectional communication.
    """
    if not mcp_http_server or not mcp_http_server.mcp_server:
        raise HTTPException(status_code=503, detail="MCP server not initialized")

    try:
        # Parse JSON-RPC request
        data = await request.json()
        logger.debug(f"Received message: {data}")

        # Process request through MCP server
        # This is handled by the SSE transport automatically
        # This endpoint is primarily for the SSE transport to receive messages

        return JSONResponse({"status": "received"})

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "service": "PyArchInit MCP Server",
        "version": "1.0.0",
        "transport": "HTTP/SSE",
        "endpoints": {
            "health": "/health",
            "capabilities": "/capabilities",
            "mcp_sse": "/mcp",
            "mcp_messages": "/mcp/messages",
            "documentation": "/docs",
        },
        "description": "MCP Server for archaeological data management, "
                      "stratigraphic analysis, and 3D visualization. "
                      "Compatible with ChatGPT Developer Mode.",
        "quick_start": {
            "1_check_health": "GET /health",
            "2_view_capabilities": "GET /capabilities",
            "3_connect_chatgpt": "Use URL: https://YOUR_SERVER/mcp",
        }
    }


def main():
    """Run the HTTP MCP server"""
    config = MCPConfig()

    logger.info(f"Starting PyArchInit MCP HTTP Server...")
    logger.info(f"Transport: {config.mcp_transport}")
    logger.info(f"Host: {config.mcp_host}")
    logger.info(f"Port: {config.mcp_port}")
    logger.info(f"Database: {config.database_url}")

    # Run with uvicorn
    uvicorn.run(
        app,
        host=config.mcp_host,
        port=config.mcp_port,
        log_level=config.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()
