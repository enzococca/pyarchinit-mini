# PyArchInit Blender Integration Guide

**Create real 3D archaeological models with Blender integration**

This guide explains how to connect PyArchInit with Blender to create professional 3D models of stratigraphic excavations with real geometry, materials, and real-time streaming to the web viewer.

## Table of Contents

1. [What is Blender Integration?](#what-is-blender-integration)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Features](#features)
6. [Real-Time Streaming](#real-time-streaming)
7. [AI-Powered Reconstruction](#ai-powered-reconstruction)
8. [Troubleshooting](#troubleshooting)

---

## What is Blender Integration?

**Blender** is a professional, open-source 3D creation suite. PyArchInit integrates with Blender to:

- **Create real 3D geometry** from archaeological data (not just simple boxes)
- **Apply realistic materials** based on US type, period, and description
- **Stream in real-time** to the web viewer
- **Export professional formats** (.blend, .glb, .fbx, .obj)
- **Use AI** (via Claude/ChatGPT) to automate model creation

### What You Get

**Without Blender:**
- Simple colored boxes
- Basic positioning
- Limited visualization

**With Blender:**
- Real mesh geometry (layers, structures, cuts, fills)
- Realistic materials (stone, earth, brick textures)
- Professional lighting and rendering
- Export to any format
- AI-powered reconstruction

---

## Quick Start

### Prerequisites

- PyArchInit-Mini installed
- Blender 3.0+ installed
- Python 3.8+

### 5-Minute Setup

1. **Start PyArchInit Web Interface:**
   ```bash
   cd /path/to/pyarchinit-mini
   DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" \
   python3 -m pyarchinit_mini.web_interface.app
   ```

2. **Open Blender**

3. **Install Addon:**
   - Edit → Preferences → Add-ons
   - Click "Install..."
   - Navigate to: `blender_addons/pyarchinit_realtime_streamer.py`
   - Select and install
   - Enable the addon (check the box)

4. **Connect:**
   - Press `N` in 3D Viewport
   - Click "PyArchInit" tab
   - Click "Connect to PyArchInit"
   - Status should show "Connected"

5. **Test:**
   - Open browser: `http://localhost:5001/3d-builder/`
   - Select a site
   - Type in chat: `Build all`
   - Watch Blender create geometry in real-time!

---

## Installation

### Step 1: Install Blender

**Download:** https://www.blender.org/download/

**Supported Versions:** 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.0, 4.1, 4.2

**Recommended:** Blender 4.2+ for best compatibility

### Step 2: Install Python Dependencies

Blender uses its own Python. Install required packages:

```bash
# Find Blender's Python (example paths)
# macOS: /Applications/Blender.app/Contents/Resources/4.2/python/bin/python3.11
# Windows: C:\Program Files\Blender Foundation\Blender 4.2\4.2\python\bin\python.exe
# Linux: /usr/share/blender/4.2/python/bin/python3.11

# Install Socket.IO
/path/to/blender/python -m pip install python-socketio[client]
```

### Step 3: Install PyArchInit Blender Addon

#### Option A: Via Blender UI (Easiest)

1. **Open Blender**
2. **Go to:** Edit → Preferences
3. **Click:** Add-ons tab
4. **Click:** Install... button (top right)
5. **Navigate to your PyArchInit directory:**
   ```
   /path/to/pyarchinit-mini/blender_addons/pyarchinit_realtime_streamer.py
   ```
6. **Select the file** and click "Install Add-on"
7. **Enable it:** Check the box next to "PyArchInit Real-Time Streamer"
8. **Save preferences** (bottom left)

#### Option B: Manual Installation

1. **Copy addon file:**
   ```bash
   # macOS/Linux
   cp blender_addons/pyarchinit_realtime_streamer.py \
      ~/Library/Application\ Support/Blender/4.2/scripts/addons/

   # Windows
   copy blender_addons\pyarchinit_realtime_streamer.py \
        %APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\
   ```

2. **Restart Blender**

3. **Enable addon:**
   - Edit → Preferences → Add-ons
   - Search for "PyArchInit"
   - Enable it

### Step 4: Verify Installation

1. **Open Blender**
2. **Press `N`** in 3D Viewport (opens sidebar)
3. **Look for "PyArchInit" tab**
4. **You should see:**
   - "PyArchInit Real-Time Streamer" panel
   - Connection settings
   - "Connect to PyArchInit" button
   - Status indicator

---

## Usage

### Method 1: With Web Viewer (Recommended)

**This is the easiest and most visual way.**

1. **Start PyArchInit Web:**
   ```bash
   DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" \
   python3 -m pyarchinit_mini.web_interface.app
   ```

2. **Start Blender** and connect addon (see Quick Start)

3. **Open Web Viewer:** `http://localhost:5001/3d-builder/`

4. **Type commands:**
   ```
   Build all
   Create US 1, 2, 3
   Show only Roman period
   ```

5. **Watch:**
   - Blender creates geometry
   - Web viewer updates in real-time
   - You can interact with both

### Method 2: With Claude Desktop

**Use natural language with Claude AI.**

1. **Setup Claude Desktop MCP:**
   See [MCP_INTEGRATION.md](./MCP_INTEGRATION.md#setup-for-claude-desktop)

2. **Start Blender** with addon connected

3. **Open Claude Desktop**

4. **Type:**
   ```
   Create a 3D model for US 1, 2, 3 from the Tempio Fortuna site
   with GraphML positioning and colors based on period
   ```

5. **Claude will:**
   - Query the database
   - Generate positioning data
   - Send commands to Blender
   - Report results

### Method 3: With ChatGPT

**Same as Claude Desktop, but requires public URL.**

See [MCP_INTEGRATION.md](./MCP_INTEGRATION.md#setup-for-chatgpt)

### Method 4: Direct API (Advanced)

**For programmatic control.**

```python
from pyarchinit_mini.mcp_server.blender_client import BlenderClient

client = BlenderClient(host='localhost', port=9876)
client.connect()

# Send build command
result = client.build_3d(
    us_ids=[1, 2, 3],
    positioning='graphml',
    layer_spacing=0.8
)

print(result)
```

---

## Features

### Automatic Geometry Creation

Blender creates different geometry based on `unita_tipo`:

| US Type | Geometry | Characteristics |
|---------|----------|----------------|
| **Strato** (Layer) | Flat rectangular volume | Surface variations for natural deposits |
| **Struttura/Muro** (Wall) | Vertical structure | Stone block subdivisions, masonry texture |
| **Taglio** (Cut) | Inverted volume | Cylindrical for pits, rectangular for trenches |
| **Riempimento** (Fill) | Irregular volume | Random variations, fill material texture |

### Material Application

Materials are applied based on archaeological data:

#### Color by Period
- **Romano:** Red-brown (terracotta)
- **Medieval:** Brown (aged stone)
- **Etrusco:** Blue-gray (tufo stone)
- **Modern:** Gray (cement)

#### Texture by Type
- **Earth layers:** Rough, matte finish
- **Stone structures:** Bumpy, high roughness
- **Brick:** Regular pattern
- **Cut fill:** Mixed texture

#### Custom Materials
Override in chat:
```
Apply stone material to US 3
Color US 5 red
Use brick texture on USM 7
```

### Positioning

Blender positions objects based on:

1. **GraphML Layout:**
   - Reads Harris Matrix relationships
   - Hierarchical positioning
   - Respects stratigraphy

2. **Archaeological Data:**
   - Uses actual measurements when available
   - Scales geometry appropriately
   - Maintains proportions

3. **Layer Spacing:**
   - Vertical offset between layers (default: 0.8m)
   - Prevents overlap
   - Adjustable via commands

---

## Real-Time Streaming

### How It Works

```
User Command → PyArchInit → Blender → WebSocket → Web Viewer
                                ↓
                        Creates 3D Geometry
```

1. **User types command** in web viewer or Claude Desktop
2. **PyArchInit queries database** for complete US data
3. **Sends to Blender** via TCP socket (port 9876)
4. **Blender creates geometry** based on data
5. **Addon streams updates** via WebSocket (port 5001)
6. **Web viewer displays** in real-time

### What Gets Streamed

- **Object creation** - New meshes appear
- **Material updates** - Colors and textures change
- **Transformations** - Position, rotation, scale
- **Progress updates** - Status messages and percentages
- **Errors** - Warnings and error messages

### Setup Real-Time Streaming

Already works if you followed [Quick Start](#quick-start)!

**Verify it's working:**
1. Open Blender (addon connected)
2. Open web viewer: `http://localhost:5001/3d-builder/`
3. Type: `Build US 1`
4. Watch Blender and web viewer simultaneously
5. You should see object appear in both

---

## AI-Powered Reconstruction

Use Claude AI with Blender MCP to automatically reconstruct sites.

### Prerequisites

- **blender-mcp** installed: https://github.com/VertexStudio/blender-mcp
- **Claude Desktop** configured (see [MCP_INTEGRATION.md](./MCP_INTEGRATION.md))
- **PyArchInit Blender addon** connected

### Generate Reconstruction Prompts

PyArchInit includes a script to generate AI prompts for site reconstruction:

```bash
# List available sites
python3 scripts/generate_3d_with_claude.py --list

# Generate prompt for specific site
python3 scripts/generate_3d_with_claude.py --site "Tempio Fortuna"

# Interactive mode
python3 scripts/generate_3d_with_claude.py
```

**Output files** (in `output/3d_generation/`):
- `Site_Name_data.json` - Complete archaeological data
- `Site_Name_prompt.md` - Main reconstruction prompt
- `Site_Name_agent_architect.md` - Architectural agent prompt
- `Site_Name_agent_validator.md` - Validation agent prompt
- `Site_Name_agent_texturizer.md` - Texturing agent prompt
- `Site_Name_agent_reconstructor.md` - Reconstruction agent prompt

### Use with Claude AI

1. **Generate prompts:**
   ```bash
   python3 scripts/generate_3d_with_claude.py --site "Tempio Fortuna"
   ```

2. **Open Claude Desktop**

3. **Load the main prompt:**
   ```
   Read the file output/3d_generation/Tempio_Fortuna_prompt.md
   and create the 3D reconstruction in Blender
   ```

4. **Claude will:**
   - Read all archaeological data (28+ US with complete metadata)
   - Use specialized agents (Architect, Validator, Texturizer, Reconstructor)
   - Create realistic geometry in Blender
   - Apply appropriate materials
   - Validate dimensions and relationships
   - Add missing/reconstructed elements

5. **Watch in real-time:**
   - Blender constructs the model
   - Web viewer shows progress
   - You can intervene anytime

### Specialized Agents

The reconstruction uses 4 AI agents:

1. **Architect Agent:**
   - Creates base structures
   - Places walls, floors, foundations
   - Ensures structural integrity

2. **Validator Agent:**
   - Checks dimensions match data
   - Verifies stratigraphic relationships
   - Reports discrepancies

3. **Texturizer Agent:**
   - Applies realistic materials
   - Uses period-appropriate textures
   - Adds weathering and aging effects

4. **Reconstructor Agent:**
   - Adds missing elements (virtual reconstruction)
   - Completes partial structures
   - Makes educated guesses based on typology

---

## Troubleshooting

### Problem: Addon won't install

**Error:** "Module not found: python-socketio"

**Solution:**
```bash
# Install to Blender's Python
/path/to/blender/python -m pip install python-socketio[client]

# macOS example:
/Applications/Blender.app/Contents/Resources/4.2/python/bin/python3.11 \
  -m pip install python-socketio[client]
```

### Problem: Can't connect to PyArchInit

**Error:** "Connection failed to localhost:5001"

**Solutions:**
1. **Verify Flask server is running:**
   ```bash
   # Should show process
   lsof -i :5001
   ```

2. **Check firewall** allows local connections

3. **Try different URL in addon settings:**
   - Default: `http://localhost:5001`
   - Alternative: `http://127.0.0.1:5001`

4. **Restart both** Flask server and Blender

### Problem: No geometry created

**Error:** "Build command sent but nothing appears"

**Solutions:**
1. **Check Blender console** (Window → Toggle System Console)
2. **Look for errors** in Python traceback
3. **Verify data:**
   ```bash
   sqlite3 data/pyarchinit_tutorial.db \
     "SELECT us, unita_tipo FROM us_table LIMIT 5;"
   ```
4. **Try simple test:**
   - In Blender: Add → Mesh → Cube (verify Blender works)
   - Delete cube
   - Try PyArchInit command again

### Problem: Real-time streaming not working

**Cause:** WebSocket not connected

**Solutions:**
1. **Check Socket.IO installed:**
   ```bash
   /path/to/blender/python -m pip show python-socketio
   ```

2. **Verify Flask-SocketIO running:**
   - Check Flask startup logs
   - Should see: "SocketIO server running"

3. **Test WebSocket:**
   - Open browser console (F12)
   - Look for WebSocket connection messages
   - Should see: "Socket.IO connected"

4. **Restart everything:**
   - Stop Flask server
   - Close Blender
   - Start Flask server
   - Open Blender and reconnect addon
   - Refresh browser

### Problem: Blender freezes

**Cause:** Large model or complex geometry

**Solutions:**
1. **Build in batches:**
   ```
   Create US 1-10
   Create US 11-20
   ```

2. **Use simpler positioning:**
   ```
   Build with simple positioning
   ```

3. **Reduce layer spacing:**
   ```
   Build with layer spacing 0.5
   ```

4. **Increase Blender memory:**
   - Edit → Preferences → System
   - Increase "Memory Cache Limit"

---

## Advanced Configuration

### Custom Port

If port 5001 is occupied:

**In PyArchInit:**
```bash
FLASK_PORT=9000 \
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" \
python3 -m pyarchinit_mini.web_interface.app
```

**In Blender Addon:**
1. Press N → PyArchInit tab
2. Change "Server URL" to: `http://localhost:9000`
3. Click "Connect to PyArchInit"

### Custom Geometry

**Modify addon to add custom geometry:**

Edit `blender_addons/pyarchinit_realtime_streamer.py`:

```python
def create_custom_geometry(bm, us_data):
    # Your custom geometry code
    # Example: Create cylinder for a well
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        diameter1=2.0,
        diameter2=2.0,
        depth=5.0,
        segments=32
    )

# Add to dispatcher in handle_build_command():
if us_data.get('unita_tipo') == 'Pozzo':  # Well
    create_custom_geometry(bm, us_data)
```

### Export Settings

**Export Blender file:**
```
Export as .blend
```

**Export for web:**
```
Export as .glb
```

**Customize export:**
```python
# In chat or via API
export({
    "format": "glb",
    "options": {
        "use_selection": False,
        "use_visible": True,
        "export_materials": True,
        "export_animations": False
    }
})
```

---

## Performance Tips

### For Large Sites (100+ US)

1. **Disable real-time streaming temporarily**
2. **Build in background**
3. **Use lower subdivision levels**
4. **Reduce material complexity**
5. **Use instances for repeated elements**

### Blender Settings

**Optimize for performance:**
- Edit → Preferences → System
- Set "Viewport Ray Tracing" to "CPU"
- Reduce "Simplify" render settings
- Use "Workbench" engine for preview (faster than Eevee/Cycles)

---

## Next Steps

1. **Try AI Reconstruction** - Generate prompts and use Claude Desktop
2. **Export Your Models** - Save as .blend, .glb for other software
3. **Learn Blender** - https://www.blender.org/support/tutorials/

---

## Resources

- **Blender:** https://www.blender.org/
- **Blender MCP:** https://github.com/VertexStudio/blender-mcp
- **Socket.IO Python:** https://python-socketio.readthedocs.io/
- **PyArchInit-Mini:** https://github.com/enzococca/pyarchinit-mini

---

## Support

- **Issues:** https://github.com/enzococca/pyarchinit-mini/issues
- **Email:** enzo.ccc@gmail.com
- **Blender Help:** https://blender.org/support/
- **Documentation:** https://github.com/enzococca/pyarchinit-mini/blob/main/README.md

---

**Last Updated:** November 2025
**PyArchInit-Mini Version:** 1.9.10+
**Blender Versions Supported:** 3.0+
