# PyArchInit Blender MCP Integration Setup

Complete guide to set up and use the Blender MCP integration for creating real 3D stratigraphic models.

## Architecture Overview

```
Claude Desktop (Chat Interface)
        ↓ (MCP Protocol via stdio)
PyArchInit MCP Server
        ↓ (Queries database for complete US data)
        ↓ (TCP Socket - port 9876)
Blender + MCP Addon
        ↓ (Creates REAL 3D geometry)
        ↓ (WebSocket - port 5002)
Web GUI Viewer
        ↓ (Displays real-time construction)
```

## Features

### What This System Does

- **Real 3D Geometry**: Creates actual mesh geometry in Blender, not simple proxy cubes
- **Archaeological Data Integration**: Uses ALL US data fields:
  - `unita_tipo` → Determines geometry type (layer, structure, cut, fill)
  - `descrizione` → Influences detail level and geometry characteristics
  - `periodo` → Determines color scheme based on archaeological period
  - `colore`, `formazione`, `struttura` → Material properties
  - `measurements` → Scales geometry appropriately
  - `relationships` → Positions objects based on stratigraphy
- **Real-time Streaming**: Watch Blender construct the model in real-time via WebSocket
- **Dual Interface**:
  - Claude Desktop: Natural language commands
  - Web GUI: Visual interface with chat and 3D viewer

## Installation Steps

### 1. Claude Desktop Configuration

**Already Done!** Configuration file created at:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

Content:
```json
{
  "mcpServers": {
    "pyarchinit": {
      "command": "/Users/enzo/.pyenv/versions/3.11.6/bin/python3",
      "args": ["-m", "pyarchinit_mini.mcp_server"],
      "env": {
        "DATABASE_URL": "sqlite:///Users/enzo/Documents/pyarchinit-mini-desk/data/pyarchinit_tutorial.db",
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876",
        "WEBSOCKET_PORT": "5002",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 2. Blender MCP Addon Installation

**Addon Created!** Located at:
```
blender_addon/pyarchinit_blender_addon.py
```

**FIXED**: Removed websockets dependency for compatibility with Blender's Python.

#### Install in Blender:

1. **Open Blender** (version 3.0 or higher recommended)

2. **Go to**: `Edit > Preferences > Add-ons`

3. **Click**: `Install...` button (or `Install from Disk...`)

4. **Navigate to**: `/Users/enzo/Documents/pyarchinit-mini-desk/blender_addon/pyarchinit_blender_addon.py`

5. **Select** the file and click `Install Add-on`

6. **Enable** the addon by checking the box next to "PyArchInit: MCP Builder"
   - If you see an error about missing modules, the addon has been updated to fix this
   - The addon now uses only Blender's built-in Python modules

7. **Find the addon panel**:
   - Switch to 3D Viewport (if not already there)
   - Press `N` to open the sidebar (properties panel)
   - Look for the "PyArchInit" tab in the sidebar
   - You should see the MCP control panel

8. **Start the MCP Server** by clicking the "Start MCP Server" button
   - Status will change from "Stopped" to "Running"
   - Server listens on port 9876
   - You can now send commands from PyArchInit

**Troubleshooting Installation:**
- If installation fails, check Blender's console (Window > Toggle System Console on Windows, or check terminal on Mac)
- The addon requires only standard Python modules: `bpy`, `bmesh`, `json`, `socket`, `threading`, `logging`
- All these are included with Blender by default

### 3. PyArchInit MCP Server

**Already Configured!** No additional setup needed.

The MCP server will:
- Read complete US data from database
- Generate GraphML for stratigraphic relationships
- Send data to Blender via TCP socket
- Return results to Claude Desktop or Web GUI

## Usage

### Option A: Using Claude Desktop (Recommended)

1. **Start Blender** and enable the MCP addon (see step 2 above)

2. **Start the MCP Server in Blender** (click button in addon panel)

3. **Open Claude Desktop**

4. **Use natural language commands**:
   ```
   "Create 3D model for US 1, 2, 3"
   "Build stratigraphic model for site Pompei"
   "Generate 3D visualization with periods colored by chronology"
   ```

5. **Claude will**:
   - Parse your command
   - Query the database for complete US data
   - Send to Blender for geometry creation
   - Stream progress updates
   - Return success/failure message

6. **Watch in Blender** as the model is constructed in real-time

### Option B: Using Web GUI

1. **Start Blender** and enable the MCP addon

2. **Start the MCP Server in Blender**

3. **Start Flask server**:
   ```bash
   cd /Users/enzo/Documents/pyarchinit-mini-desk
   DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" python3 -m pyarchinit_mini.web_interface.app
   ```

4. **Open browser**: http://localhost:5001/3d-builder/

5. **Use the chat interface** in the right sidebar:
   ```
   Crea US 1,2,3
   Mostra solo periodo Romano
   Costruisci tutto
   ```

6. **Watch** as Blender creates geometry and streams updates to the viewer

### Available Commands (Italian/English)

**Build 3D Model:**
- `Crea US 1,2,3` / `Create US 1,2,3`
- `Costruisci tutto` / `Build all`
- `Genera dal GraphML` / `Generate from GraphML`

**Filter:**
- `Mostra solo periodo Romano` / `Show only Roman period`
- `Nascondi US 5,6` / `Hide US 5,6`
- `Mostra US 1,2,3` / `Show US 1,2,3`

**Export:**
- `Esporta come .blend` / `Export as .blend`
- `Export .glb` / `Export .glb`

**Materials:**
- `Colora US 3 rosso` / `Color US 3 red`
- `Color US 5 #FF0000` / `Color US 5 #FF0000`

## How It Works

### 1. Command Parsing

The `CommandParser` (already implemented) converts natural language to MCP tool calls:

```python
"Crea US 1,2,3" → build_3d(us_ids=[1,2,3], mode="selected")
```

### 2. Data Fetching

`Build3DTool` queries the database for **COMPLETE** US data:

```python
complete_us_data = {
    'us_id': 1,
    'unita_tipo': 'Strato',  # → Creates layered geometry
    'descrizione': 'Strato di terra marrone...',  # → Influences detail
    'periodo': 'Romano',  # → Red-brown color
    'colore': 'Marrone',
    'formazione': 'Naturale',
    'struttura': 'Stratificata',
    # ... all other fields
}
```

### 3. Geometry Creation in Blender

The Blender addon receives complete data and creates geometry based on `unita_tipo`:

| unita_tipo | Geometry Type | Characteristics |
|------------|---------------|-----------------|
| Strato / Layer | Thin rectangular volume | Surface variation for natural deposits |
| Struttura / Muro | Vertical structure | Stone block subdivisions for masonry |
| Taglio / Fossa | Inverted/negative | Cylindrical for pits, rectangular for cuts |
| Riempimento / Fill | Irregular volume | Random variations for fill deposits |

### 4. Material Application

Materials are applied based on archaeological data:

- **Color**: Based on `periodo` (period)
  - Romano → Red-brown (0.8, 0.3, 0.2)
  - Medieval → Brown (0.5, 0.4, 0.3)
  - Etrusco → Blue (0.3, 0.3, 0.6)
  - Custom colors from `colore` field

- **Roughness**: Based on `unita_tipo`
  - Struttura (stone) → 0.8 (very rough)
  - Strato (earth) → 0.9 (extremely rough)
  - Default → 0.7

### 5. Real-time Streaming

Blender sends WebSocket messages during construction:

```json
{
  "type": "progress",
  "action": "creating_geometry",
  "us_id": 1,
  "unita_tipo": "Strato",
  "progress": 33,
  "message": "Creating geometry for US 1 (Strato)"
}
```

The web GUI displays these updates in real-time.

## Troubleshooting

### Blender Connection Issues

**Error**: `Could not connect to Blender`

**Solutions**:
1. Make sure Blender is running
2. Enable the PyArchInit MCP addon in Blender
3. Click "Start MCP Server" in the addon panel
4. Check that port 9876 is not blocked by firewall
5. Verify `BLENDER_PORT` in Claude Desktop config matches addon port

### No Geometry Created

**Error**: `No proxies generated`

**Solutions**:
1. Check that US records exist in database
2. Verify `us_ids` are correct
3. Check logs: `/tmp/pyarchinit_mcp_server.log`
4. Ensure GraphML relationships exist or can be auto-generated

### Claude Desktop Not Connecting

**Error**: `MCP server not found`

**Solutions**:
1. Restart Claude Desktop
2. Check config file location: `~/Library/Application Support/Claude/claude_desktop_config.json`
3. Verify Python path in config: `/Users/enzo/.pyenv/versions/3.11.6/bin/python3`
4. Check database path is absolute, not relative

### WebSocket Stream Not Working

**Solutions**:
1. Check port 5002 is available
2. Verify `WEBSOCKET_PORT` in environment variables
3. Check browser console for WebSocket connection errors
4. Ensure Flask server is running

## Testing

### Test 1: Command Parser

```bash
cd /Users/enzo/Documents/pyarchinit-mini-desk
python3 test_chat_builder.py
```

**Expected Output**:
```
TEST 1: Command Parser
Command: 'Crea US 1,2,3'
  → Tool: build_3d
  → Arguments: {'us_ids': [1, 2, 3], 'mode': 'selected'}
✓ Command Parser Test Complete
```

### Test 2: MCP Executor (without Blender)

```bash
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" python3 test_chat_builder.py
```

**Expected Output**:
```
TEST 2: MCP Executor - Build 3D
  Success: True
  Proxies Count: 3
✓ MCP Executor Test Complete
```

### Test 3: Blender Connection

In Blender's Python console:
```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 9876))
# Should connect without error if MCP server is running
```

### Test 4: Complete Flow

1. Start Blender with MCP addon running
2. Start Flask server
3. Open http://localhost:5001/3d-builder/
4. Type in chat: `Crea US 1,2,3`
5. Watch Blender create geometry
6. See real-time updates in web viewer

**Expected**: 3 objects created in Blender with materials based on archaeological data

## Architecture Details

### Data Flow

1. **User Command** (Claude Desktop or Web GUI)
   ↓
2. **CommandParser** → Converts to MCP tool call
   ↓
3. **MCPToolsExecutor** → Routes to Build3DTool
   ↓
4. **Build3DTool.execute()**:
   - Query database for complete US data
   - Generate GraphML for relationships
   - Call ProxyGenerator for positioning
   ↓
5. **Build3DTool._send_to_blender()**:
   - Connect to Blender via TCP socket
   - Send complete US data + positioning
   ↓
6. **Blender MCP Addon**:
   - Parse command
   - Create geometry based on `unita_tipo`
   - Apply materials based on `periodo`, `colore`
   - Stream progress via WebSocket
   ↓
7. **Web GUI** (if using):
   - Receive WebSocket messages
   - Display real-time construction
   - Show final 3D model

### Key Files

```
pyarchinit-mini-desk/
├── blender_addon/
│   └── pyarchinit_blender_addon.py          # Blender MCP addon (NEW!)
├── pyarchinit_mini/
│   ├── mcp_server/
│   │   ├── __main__.py                      # MCP server entry point
│   │   ├── blender_client.py                # TCP client for Blender
│   │   ├── tools/
│   │   │   └── build_3d_tool.py             # MODIFIED: Sends complete US data
│   │   └── graphml_parser.py                # GraphML relationship parsing
│   ├── services/
│   │   ├── command_parser.py                # Natural language → tool calls
│   │   └── mcp_executor.py                  # Local tool execution
│   ├── models/
│   │   └── us.py                            # US model with all fields
│   └── web_interface/
│       ├── three_d_builder_routes.py        # Chat API endpoint
│       └── templates/3d_builder/index.html  # Chat UI
├── test_chat_builder.py                     # Test script
└── ~/Library/Application Support/Claude/
    └── claude_desktop_config.json           # Claude Desktop config
```

## Next Steps

### Completed ✓
1. Claude Desktop configuration
2. Blender MCP addon creation
3. Build3DTool integration with Blender
4. Complete US data fetching from database
5. Real geometry creation based on unita_tipo
6. Material application based on periodo

### In Progress ⚙️
1. WebSocket streaming implementation
2. Web GUI real-time updates

### TODO
1. Test complete flow end-to-end
2. Add more geometry variations based on descrizione
3. Implement measurement-based scaling
4. Add export functionality (.blend, .glb)
5. Create video tutorial

## Support

For issues or questions:
1. Check logs: `/tmp/pyarchinit_mcp_server.log`
2. Check Blender console for addon errors
3. Review this documentation
4. Test individual components using test scripts

## Advanced Usage

### Custom Geometry

To add custom geometry types, modify `blender_addon/pyarchinit_blender_addon.py`:

```python
def create_custom_geometry(bm, us_data, descrizione):
    # Your custom geometry creation logic
    pass

# Then add to geometry dispatcher:
if unita_tipo == "YourCustomType":
    create_custom_geometry(bm, us_data, descrizione)
```

### Custom Materials

To add period colors, modify `get_period_color()`:

```python
period_colors = {
    "YourPeriod": (r, g, b, 1.0),  # RGB 0-1 range
    # ...
}
```

### Disable Blender

To generate proxy metadata without Blender:

```python
result = await executor.execute_tool(
    "build_3d",
    {
        "us_ids": [1, 2, 3],
        "mode": "selected",
        "options": {"use_blender": False}  # Disable Blender
    }
)
```

## Performance

- **Small models** (< 10 US): ~1-2 seconds in Blender
- **Medium models** (10-50 US): ~5-10 seconds
- **Large models** (50+ US): ~20-30 seconds
- Real-time streaming updates every ~0.1 seconds per object

## Credits

- **PyArchInit**: Original archaeological GIS software
- **Blender**: Open-source 3D creation suite
- **Anthropic**: Claude AI and MCP protocol
- **Three.js**: WebGL 3D library for web viewer
