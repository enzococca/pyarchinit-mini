# PyArchInit MCP Server

MCP (Model Context Protocol) server for PyArchInit-Mini, enabling Claude AI to interact with stratigraphic data and control Blender for 3D visualization.

## Overview

The PyArchInit MCP Server implements the Model Context Protocol to provide Claude AI with:

- **5 Resources**: Access to stratigraphic data (GraphML, US, Periods, Relationships, Sites)
- **5 Tools**: Actions for 3D model generation (build_3d, filter, export, position, material)
- **3 Prompts**: Pre-defined templates for common archaeological tasks

## Architecture

```
Claude AI (Claude Desktop)
       ↓ MCP Protocol (JSON-RPC over stdio)
PyArchInit MCP Server
  ├─ Resources (Context Data)
  ├─ Tools (Actions)
  └─ Prompts (Templates)
       ↓ TCP Socket (port 9876)
Blender MCP Addon
       ↓ glTF Export
3D Viewer (Three.js in Web GUI)
```

## Installation

### 1. Install MCP SDK

```bash
pip install mcp
# or with pyarchinit-mini
pip install pyarchinit-mini[mcp]
```

### 2. Configure Claude Desktop

Edit your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

Add the PyArchInit MCP server:

```json
{
  "mcpServers": {
    "pyarchinit": {
      "command": "pyarchinit-mcp-server",
      "env": {
        "DATABASE_URL": "sqlite:///path/to/your/pyarchinit_mini.db",
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

### 3. Install and Configure Blender MCP Addon

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Blender MCP addon
uvx blender-mcp

# Configure Claude Desktop for Blender
# Add to the same claude_desktop_config.json:
{
  "mcpServers": {
    "pyarchinit": { ... },
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

### 4. Start Blender

Open Blender and enable the MCP addon. The addon will automatically start a socket server on port 9876.

## Usage

### Via Claude Desktop

Once configured, you can interact with Claude Desktop using natural language:

```
User: "Show me the GraphML for site 1"
Claude: [Uses GraphML Resource to fetch data]

User: "Create a 3D model of Bronze Age layers from site 1"
Claude: [Uses build_3d_from_us Tool with period filter]

User: "Filter the 3D model to show only US 5-10"
Claude: [Uses filter_proxies Tool]
```

### Programmatic Usage

You can also run the MCP server programmatically:

```python
import asyncio
from pyarchinit_mini.mcp_server import run_mcp_server, MCPConfig

config = MCPConfig(
    database_url="sqlite:///data/pyarchinit_mini.db",
    blender_host="localhost",
    blender_port=9876,
)

asyncio.run(run_mcp_server(config))
```

### CLI

```bash
# Start MCP server with default config
pyarchinit-mcp-server

# With custom log level
pyarchinit-mcp-server --log-level DEBUG

# Show help
pyarchinit-mcp-server --help

# Show version
pyarchinit-mcp-server --version
```

## Resources

### 1. GraphML Resource

**URI**: `resource://graphml/{graphml_id}`

Provides access to GraphML stratigraphic graphs.

**Examples**:
- `resource://graphml/current` - Latest GraphML
- `resource://graphml/15` - Specific GraphML by ID
- `resource://graphml/site/1` - All GraphML for site 1

**Data Structure**:
```json
{
  "type": "graphml_data",
  "id": 15,
  "metadata": {
    "node_count": 25,
    "edge_count": 40,
    "site_name": "Sito Archeologico di Esempio"
  },
  "nodes": [
    {
      "id": "n5",
      "label": "US 5",
      "us_id": 5,
      "period": "Bronze Age",
      "description": "Strato di riempimento...",
      "position": {"x": 100.0, "y": 200.0}
    }
  ],
  "edges": [
    {
      "source": "n5",
      "target": "n6",
      "relationship": "covers"
    }
  ]
}
```

### 2. US Resource

**URI**: `resource://us/{us_id}`

Provides stratigraphic unit data (all 49 fields).

### 3. Periods Resource

**URI**: `resource://periods/{period_id}`

Provides chronological periods and datazioni data.

### 4. Relationships Resource

**URI**: `resource://relationships/{us_id}`

Provides stratigraphic relationships (covers, cuts, fills, etc.).

### 5. Sites Resource

**URI**: `resource://sites/{site_id}`

Provides archaeological sites data.

## Tools

### 1. build_3d_from_us

Generate 3D stratigraphic model in Blender.

**Parameters**:
```json
{
  "site_id": 1,
  "us_ids": [5, 6, 7, 10],
  "graphml_id": 15,
  "options": {
    "positioning": "graphml",
    "auto_color": true,
    "auto_material": true
  }
}
```

**Returns**:
```json
{
  "success": true,
  "session_id": "uuid",
  "proxy_count": 4
}
```

### 2. filter_proxies

Filter 3D proxies by period, US, or other criteria.

**Parameters**:
```json
{
  "session_id": "uuid",
  "filters": {
    "period_range": {"start": -1200, "end": -800},
    "visible_us": [5, 6, 7],
    "transparency": 0.75
  }
}
```

### 3. export_3d_model

Export 3D model in glTF or glB format.

**Parameters**:
```json
{
  "session_id": "uuid",
  "format": "gltf"
}
```

### 4. calculate_positions

Calculate proxy positions based on stratigraphic relationships.

**Parameters**:
```json
{
  "us_ids": [5, 6, 7],
  "algorithm": "graphml"
}
```

### 5. assign_materials

Assign materials to proxies based on periods or formation types.

**Parameters**:
```json
{
  "session_id": "uuid",
  "material_mode": "period"
}
```

## Prompts

### 1. stratigraphic_model

Template for generating stratigraphic 3D models with best practices.

### 2. period_visualization

Template for period-based chronological visualization.

### 3. us_description

Template for describing stratigraphic units in archaeological context.

## Configuration

### Environment Variables

- `DATABASE_URL`: Database connection URL (default: `sqlite:///data/pyarchinit_mini.db`)
- `BLENDER_HOST`: Blender host (default: `localhost`)
- `BLENDER_PORT`: Blender port (default: `9876`)
- `WEBSOCKET_PORT`: WebSocket port for streaming (default: `5002`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `EXPORT_DIR`: Export directory (default: `/tmp/pyarchinit_3d_exports`)

### MCPConfig Class

```python
from pyarchinit_mini.mcp_server import MCPConfig

config = MCPConfig(
    database_url="sqlite:///data/pyarchinit_mini.db",
    blender_host="localhost",
    blender_port=9876,
    websocket_port=5002,
    default_positioning="graphml",  # or "grid" or "force_directed"
    default_layer_spacing=0.5,
    enable_auto_color=True,
    enable_auto_material=True,
    export_format="gltf",  # or "glb"
    cache_enabled=True,
    log_level="INFO",
)
```

## Development Status

**Current Version**: 1.0.0 (Initial Implementation)

**Implemented**:
- ✅ MCP server architecture
- ✅ Configuration system
- ✅ GraphML Resource (complete implementation)
- ✅ 5 Resources (stubs)
- ✅ 5 Tools (stubs)
- ✅ 3 Prompts (stubs)
- ✅ CLI entry point

**Pending** (see [TODO list](#todo)):
- ⏳ Complete Resource implementations (US, Periods, Relationships, Sites)
- ⏳ Complete Tool implementations (build_3d, filter, export, position, material)
- ⏳ Complete Prompt implementations
- ⏳ Blender client for communication
- ⏳ WebSocket streaming handler
- ⏳ Proxy metadata generator
- ⏳ Testing suite

## Testing

```bash
# Run MCP server in test mode
pyarchinit-mcp-server --log-level DEBUG

# Test GraphML Resource
# (Use Claude Desktop to query: "Show me the current GraphML")

# Test with sample database
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" pyarchinit-mcp-server
```

## Troubleshooting

### MCP SDK not found

```bash
pip install mcp
# or
pip install 'pyarchinit-mini[mcp]'
```

### Blender connection failed

Check that:
1. Blender is running
2. Blender MCP addon is enabled
3. Socket server is listening on port 9876
4. No firewall blocking localhost:9876

```bash
# Test socket connection
nc -zv localhost 9876
# or
telnet localhost 9876
```

### Claude Desktop not recognizing server

1. Check `claude_desktop_config.json` syntax (valid JSON)
2. Restart Claude Desktop
3. Check MCP server logs in Claude Desktop (View > Developer > Show Logs)

## References

- **MCP Protocol**: https://modelcontextprotocol.io
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **Blender MCP Addon**: https://github.com/ahujasid/blender-mcp
- **Claude Desktop**: https://claude.ai/download

## License

GPL-2.0 (same as PyArchInit-Mini)

## Contributing

Contributions welcome! See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

For questions or issues, please open an issue on GitHub:
https://github.com/enzococca/pyarchinit-mini/issues
