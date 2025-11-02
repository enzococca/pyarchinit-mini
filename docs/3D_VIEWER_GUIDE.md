# PyArchInit 3D Viewer Guide

**Interactive 3D visualization of stratigraphic models in your browser**

This guide explains how to use the PyArchInit 3D Viewer - a web-based tool that lets you visualize archaeological stratigraphic units in three dimensions, with real-time updates and natural language commands.

## Table of Contents

1. [What is the 3D Viewer?](#what-is-the-3d-viewer)
2. [Quick Start](#quick-start)
3. [Interface Overview](#interface-overview)
4. [Building 3D Models](#building-3d-models)
5. [Chat Commands](#chat-commands)
6. [Viewer Controls](#viewer-controls)
7. [Features](#features)
8. [Blender Integration](#blender-integration)
9. [Troubleshooting](#troubleshooting)

---

## What is the 3D Viewer?

The **PyArchInit 3D Viewer** is a web-based 3D visualization tool that:

- **Displays stratigraphic units (US)** as 3D objects in your browser
- **Uses archaeological data** from your database (dimensions, relationships, periods)
- **Supports natural language commands** via chat interface
- **Updates in real-time** when connected to Blender
- **Positions automatically** based on stratigraphic relationships (Harris Matrix)
- **Color-codes by period** or other criteria
- **Runs entirely in your browser** using Three.js (WebGL)

### What You Can Do

- Create 3D models from US data
- Filter by period, area, or type
- Position objects based on Harris Matrix
- Export to various formats
- Watch real-time construction when connected to Blender
- Interact with objects (click for info)
- Orbit, zoom, pan the view

---

## Quick Start

### Step 1: Start the Web Interface

```bash
# Navigate to your project directory
cd /path/to/pyarchinit-mini

# Start the Flask server
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" python3 -m pyarchinit_mini.web_interface.app
```

You should see:
```
[INFO] PyArchInit-Mini Web Interface starting...
[INFO] Running on http://127.0.0.1:5001
[INFO] Press CTRL+C to quit
```

### Step 2: Open the 3D Builder

1. **Open your browser** (Chrome, Firefox, Safari, Edge)
2. **Navigate to:** `http://localhost:5001/3d-builder/`
3. **You should see:**
   - Left side: Site selector and form
   - Center: 3D viewer canvas (black background)
   - Right side: Chat interface

### Step 3: Select a Site

1. **Click the "Site" dropdown** in the left panel
2. **Select a site** from your database (e.g., "Tempio Fortuna")
3. **Click "Auto-Populate US"** to load all US for that site
4. The US list will appear below

### Step 4: Build Your First Model

**Type in the chat:**
```
Build all
```

The viewer will:
- Query all US for the selected site
- Generate a GraphML file with relationships
- Calculate 3D positions
- Create proxy objects (colored boxes)
- Display them in the viewer

---

## Interface Overview

### Layout

```
┌─────────────────┬──────────────────────────┬─────────────────┐
│                 │                          │                 │
│  Left Panel     │    Center Viewer         │  Right Panel    │
│                 │                          │                 │
│  - Site Select  │    - 3D Canvas           │  - Chat         │
│  - US List      │    - Camera Controls     │  - Messages     │
│  - Options      │    - Object Info         │  - Input        │
│                 │                          │                 │
└─────────────────┴──────────────────────────┴─────────────────┘
```

### Left Panel: Site & US Selection

- **Site Dropdown:** Select which archaeological site to work with
- **Auto-Populate US Button:** Load all US for selected site
- **US List:** Shows all US with checkboxes
- **Build Options:**
  - Positioning mode (GraphML, Simple, Grid)
  - Layer spacing (vertical distance between layers)
  - Color mode (by period, by type, custom)

### Center Panel: 3D Viewer

- **Canvas:** WebGL 3D rendering area
- **Camera:** Orbits around the center, can zoom and pan
- **Grid:** Optional grid floor for reference
- **Axes Helper:** X (red), Y (green), Z (blue) axes
- **Overlay:** Shows current view info (camera position, object count)
- **Controls:** Bottom-left buttons for view presets

### Right Panel: Chat Interface

- **Messages Area:** Shows conversation history
- **Input Box:** Type natural language commands
- **Send Button:** Submit your command
- **Status:** Shows connection status and progress

---

## Building 3D Models

### Method 1: Chat Commands (Recommended)

Simply type what you want in the chat:

```
Build all
Create US 1, 2, 3
Generate 3D model for selected site
```

### Method 2: Manual Selection

1. Check US in the left panel
2. Click "Build Selected"
3. Wait for processing
4. View results in the canvas

### Method 3: API Call (Advanced)

Use the MCP tools directly:
```javascript
// Via MCP
build_3d({
  us_ids: [1, 2, 3],
  mode: "selected",
  positioning: "graphml",
  layer_spacing: 0.8
})
```

### Understanding Positioning Modes

#### GraphML (Recommended)
- Uses Harris Matrix relationships
- Automatically calculates vertical positions
- Respects stratigraphic sequence
- Best for accurate visualization

**Example:**
```
Build with GraphML positioning
```

#### Simple
- Stacks US vertically in database order
- No relationship analysis
- Fast but less accurate

**Example:**
```
Build with simple positioning
```

#### Grid
- Arranges US in a regular grid
- Ignores relationships
- Good for viewing many US side-by-side

**Example:**
```
Build with grid layout
```

---

## Chat Commands

The chat interface accepts natural language commands in Italian or English.

### Build Commands

| Command | What It Does | Example |
|---------|-------------|---------|
| `Build all` / `Costruisci tutto` | Build all US for selected site | Creates complete 3D model |
| `Create US 1,2,3` / `Crea US 1,2,3` | Build specific US | Creates only listed US |
| `Generate from GraphML` | Use existing GraphML file | Loads relationships from file |

### Filter Commands

| Command | What It Does | Example |
|---------|-------------|---------|
| `Show only Roman period` / `Mostra solo periodo Romano` | Filter by period | Shows only US from Roman period |
| `Hide US 5,6` / `Nascondi US 5,6` | Hide specific US | Removes US from view |
| `Show structures` / `Mostra strutture` | Filter by type | Shows only USM (structures) |
| `Show area "Sector A"` | Filter by area | Shows US from specific area |

### Material Commands

| Command | What It Does | Example |
|---------|-------------|---------|
| `Color US 3 red` / `Colora US 3 rosso` | Change object color | Applies red color to US 3 |
| `Color US 5 #FF0000` | Use hex color | Applies exact color code |
| `Apply stone material to USM 7` | Change material type | Makes object look like stone |

### View Commands

| Command | What It Does | Example |
|---------|-------------|---------|
| `Reset camera` / `Reset camera` | Return to default view | Centers and resets zoom |
| `Top view` / `Vista dall'alto` | Camera looks down | Bird's eye view |
| `Front view` / `Vista frontale` | Camera looks from front | Elevation view |
| `Zoom in` / `Zoom avanti` | Closer view | Magnifies scene |

### Export Commands

| Command | What It Does | Example |
|---------|-------------|---------|
| `Export GraphML` / `Esporta GraphML` | Save Harris Matrix | Downloads .graphml file |
| `Export .blend` / `Esporta .blend` | Save Blender file | (Requires Blender connected) |
| `Export .glb` / `Esporta .glb` | Save 3D model | Downloads GLB file |

---

## Viewer Controls

### Mouse Controls

- **Left Click + Drag:** Rotate camera (orbit)
- **Right Click + Drag:** Pan camera (move sideways)
- **Scroll Wheel:** Zoom in/out
- **Left Click on Object:** Select and show info

### Keyboard Shortcuts

- **Arrow Keys:** Rotate view
- **+/-:** Zoom in/out
- **H:** Toggle help overlay
- **G:** Toggle grid
- **R:** Reset camera

### View Presets

Bottom-left buttons provide quick view angles:

- **Top:** View from above (Y-axis)
- **Front:** View from front (Z-axis)
- **Side:** View from side (X-axis)
- **Iso:** Isometric 45° view
- **Reset:** Default view

---

## Features

### Automatic Positioning

The viewer automatically positions US based on:

1. **Stratigraphic Relationships:**
   - "Above" relationships place US higher
   - "Below" relationships place US lower
   - "Cuts" and "Fills" affect positioning

2. **GraphML Layout:**
   - Hierarchical layout from Harris Matrix
   - Respects all relationship types
   - Handles cycles and paradoxes

3. **Layer Spacing:**
   - Adjustable vertical distance (default: 0.8m)
   - Prevents overlap
   - Maintains stratigraphic order

### Color Coding

Objects are colored based on:

#### By Period (Default)
- **Romano:** Red-brown
- **Medieval:** Brown
- **Etrusco:** Blue
- **Modern:** Gray
- **Unknown:** Light gray

#### By Unit Type
- **US (Strato):** Earth tones
- **USM (Muro):** Stone gray
- **USD (Distruzione):** Dark gray
- **USV (Negativo):** Inverted colors

#### Custom Colors
Set specific colors via chat:
```
Color US 3 #FF5733
```

### Object Information

**Click any object** to see:
- US ID and description
- Unit type (US, USM, USD, USV)
- Archaeological period
- Excavation area
- Dimensions
- Stratigraphic relationships

### Real-time Updates

When connected to Blender:
- Objects appear as they're created
- Materials update live
- Transformations sync instantly
- Progress bar shows construction

---

## Blender Integration

The 3D Viewer can display models created in Blender in real-time.

### Setup

1. **Install Blender MCP Addon:**
   See [BLENDER_INTEGRATION.md](./BLENDER_INTEGRATION.md)

2. **Start Blender** with addon enabled

3. **Start Web Interface:**
   ```bash
   DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" \
   python3 -m pyarchinit_mini.web_interface.app
   ```

4. **Open 3D Viewer:** `http://localhost:5001/3d-builder/`

5. **Type in chat:**
   ```
   Build US 1,2,3
   ```

6. **Watch:**
   - Blender creates actual 3D geometry
   - Viewer receives real-time updates via WebSocket
   - Objects appear with realistic materials

### What Gets Streamed

From Blender to Viewer:
- **Geometry creation** - New objects appear
- **Material changes** - Colors and textures update
- **Transformations** - Position, rotation, scale changes
- **Progress updates** - Status messages and percentages

### Benefits of Blender Integration

- **Real geometry** instead of simple boxes
- **Realistic materials** based on archaeological data
- **Professional rendering** quality
- **Export options** (.blend, .glb, .fbx, .obj)
- **Advanced editing** capabilities

---

## Troubleshooting

### Problem: Viewer shows empty canvas

**Possible Causes:**
1. No site selected
2. No US in database
3. JavaScript errors

**Solutions:**
```bash
# Check database has data
sqlite3 data/pyarchinit_tutorial.db "SELECT COUNT(*) FROM us_table;"

# Check browser console for errors (F12 → Console)

# Verify site selected in dropdown

# Try: "Build all" in chat
```

### Problem: "Build all" does nothing

**Possible Causes:**
1. No US for selected site
2. GraphML generation failed
3. Server error

**Solutions:**
```bash
# Check server logs
# Look for errors in terminal where Flask is running

# Try manual US selection:
# 1. Check some US in left panel
# 2. Click "Build Selected"

# Check if site has US:
sqlite3 data/pyarchinit_tutorial.db \
  "SELECT COUNT(*) FROM us_table WHERE sito='Site Name';"
```

### Problem: Objects overlapping

**Cause:** Insufficient layer spacing or missing relationships

**Solutions:**
```
# Increase spacing:
Build with layer spacing 1.5

# Use GraphML positioning:
Build with GraphML layout

# Check relationships exist:
# Go to US management and verify "Above/Below" relationships
```

### Problem: Chat not responding

**Possible Causes:**
1. Server not running
2. MCP executor not initialized
3. Database locked

**Solutions:**
```bash
# Restart Flask server
# Press CTRL+C, then restart:
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" \
python3 -m pyarchinit_mini.web_interface.app

# Check logs for errors

# Try refreshing browser (CTRL+R)
```

### Problem: Colors all gray

**Cause:** Period data missing from US

**Solutions:**
```sql
# Check period data:
sqlite3 data/pyarchinit_tutorial.db \
  "SELECT us, periodo FROM us_table LIMIT 10;"

# Add period to US:
# Go to US edit form → Fill "Periodo iniziale" field

# Or manually color in chat:
Color US 3 blue
```

### Problem: Blender connection failed

**Cause:** Blender addon not running or wrong port

**Solutions:**
1. Open Blender
2. Press N → PyArchInit tab
3. Click "Connect to PyArchInit"
4. Verify port 5001 matches Flask server
5. Check firewall allows local connections

---

## Performance Tips

### For Large Sites (50+ US)

1. **Filter first:**
   ```
   Show only Roman period
   ```

2. **Build in batches:**
   ```
   Create US 1-10
   Create US 11-20
   ...
   ```

3. **Use simple positioning:**
   ```
   Build with simple positioning
   ```

4. **Reduce layer spacing:**
   ```
   Build with layer spacing 0.5
   ```

### Browser Performance

- **Use Chrome or Firefox** for best WebGL performance
- **Close other tabs** to free memory
- **Update graphics drivers**
- **Reduce window size** if laggy

### Network Performance

If using remote server:
- Use wired connection over WiFi
- Close bandwidth-heavy apps
- Consider local installation instead

---

## Advanced Usage

### Custom Positioning

Create custom positions via API:
```javascript
position({
  method: "graphml",
  layer_spacing: 1.2,
  horizontal_spacing: 2.0,
  us_ids: [1, 2, 3, 4, 5]
})
```

### Export for Other Software

The viewer can export to:
- **yEd Graph Editor:** GraphML format
- **Blender:** .blend files (via Blender integration)
- **Game engines:** .glb/.gltf formats
- **CAD software:** .obj/.fbx formats (planned)

### Embed in Your Site

Embed the 3D viewer in your own webpage:
```html
<iframe src="http://localhost:5001/3d-builder/"
        width="100%" height="600px"
        frameborder="0">
</iframe>
```

---

## Next Steps

1. **Try Blender Integration** - See [BLENDER_INTEGRATION.md](./BLENDER_INTEGRATION.md)
2. **Setup MCP for AI Commands** - See [MCP_INTEGRATION.md](./MCP_INTEGRATION.md)
3. **Explore the API** - See REST API documentation in README.md

---

## Technical Details

### Stack

- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **3D Engine:** Three.js r150
- **Real-time:** Socket.IO 4.5.4
- **Backend:** Flask + Flask-SocketIO
- **Database:** SQLite or PostgreSQL

### Browser Requirements

- **WebGL 2.0** support
- **ES6 JavaScript** support
- **WebSocket** support

**Supported Browsers:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### File Locations

```
pyarchinit-mini/
├── pyarchinit_mini/web_interface/
│   ├── templates/3d_builder/index.html    # Main template
│   ├── static/js/three-d-viewer.js        # Viewer logic
│   ├── static/js/three.min.js             # Three.js library
│   ├── static/js/OrbitControls.js         # Camera controls
│   └── three_d_builder_routes.py          # Flask routes
├── pyarchinit_mini/services/
│   ├── command_parser.py                   # Chat command parsing
│   └── mcp_executor.py                     # MCP tool execution
└── pyarchinit_mini/mcp_server/tools/
    └── build_3d_tool.py                    # 3D model generation
```

---

## Resources

- **Three.js Docs:** https://threejs.org/docs/
- **Socket.IO Docs:** https://socket.io/docs/
- **WebGL Tutorial:** https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API
- **PyArchInit-Mini:** https://github.com/enzococca/pyarchinit-mini

---

## Support

- **Issues:** https://github.com/enzococca/pyarchinit-mini/issues
- **Email:** enzo.ccc@gmail.com
- **Documentation:** https://github.com/enzococca/pyarchinit-mini/blob/main/README.md

---

**Last Updated:** November 2025
**PyArchInit-Mini Version:** 1.9.10+
