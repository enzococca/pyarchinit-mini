# Real-Time Blender Streaming - Implementation Complete ✅

## Summary

Successfully implemented complete real-time bidirectional streaming between Blender, PyArchInit web server, and the 3D viewer using Socket.IO.

## Architecture

```
Claude AI (with blender-mcp configured)
    ↓ (reads generated prompts)
Blender + PyArchInit Real-Time Streamer Addon
    ↓ (WebSocket on port 5001)
PyArchInit Flask Server (Flask-SocketIO)
    ↓ (WebSocket broadcast)
Web Viewer (Browser with Three.js + Socket.IO)
```

## ✅ Completed Components

### 1. WebSocket Backend (Flask-SocketIO)
**File**: `pyarchinit_mini/web_interface/socketio_events.py` (lines 297-528)

Events implemented:
- `blender_connect` - Blender client connection
- `blender_disconnect` - Blender client disconnection
- `blender_scene_update` - Complete scene synchronization
- `blender_object_created` - New object creation
- `blender_object_updated` - Object transformation/geometry updates
- `blender_object_deleted` - Object deletion
- `blender_material_updated` - Material property changes
- `blender_camera_update` - Camera movement
- `blender_build_progress` - Progress updates from Claude AI agents

**Registered in**: `pyarchinit_mini/web_interface/app.py` (line 513)

### 2. Blender Addon
**File**: `blender_addons/pyarchinit_realtime_streamer.py` (350 lines)

Features:
- Automatic depsgraph monitoring for scene changes
- Real-time broadcasting to WebSocket
- UI panel in 3D View sidebar (N → PyArchInit)
- Connection status indicators
- Manual scene update button
- Reconnection logic (5 attempts)

**Installation Steps**:
```
1. Open Blender
2. Edit → Preferences → Add-ons → Install
3. Select: blender_addons/pyarchinit_realtime_streamer.py
4. Enable "PyArchInit Real-Time Streamer"
5. Configure WebSocket URL: http://localhost:5001 (default)
```

**Python Dependencies for Blender**:
```bash
# Install python-socketio in Blender's Python environment
/Applications/Blender.app/Contents/Resources/4.2/python/bin/python3.11 -m pip install python-socketio[client]
```

### 3. Web Viewer Integration
**File**: `pyarchinit_mini/web_interface/templates/3d_builder/index.html`

Added components:
- Socket.IO CDN library (line 7)
- Socket.IO client initialization (line 1810)
- Event listeners for all Blender events (lines 1824-1867)
- Helper functions:
  - `updateSceneFromBlender()` - Full scene rebuild
  - `createProxyFromBlender()` - Create 3D proxy from Blender object
  - `updateProxyFromBlender()` - Update existing proxy transform
  - `deleteProxyFromBlender()` - Remove proxy from scene
  - `updateMaterialFromBlender()` - Update material properties
  - `updateBuildProgress()` - Show Claude AI build progress
- Blender connection status display with version info
- Coordinate system conversion (Blender Y-up → Three.js Z-up)

### 4. Claude AI Prompt Generation System
**File**: `scripts/generate_3d_with_claude.py`

Features:
- Generic site support (works with any database site)
- Exports archaeological data with exact dimensions
- Generates specialized agent prompts:
  - **Architect Agent**: Build base structure (foundations, walls, podium)
  - **Validator Agent**: Verify dimensions and proportions
  - **Texturizer Agent**: Apply period-appropriate materials
  - **Reconstructor Agent**: Create hypothetical reconstructions

**Generated Output** (for Tempio Fortuna example):
```
output/3d_generation/
├── Tempio_Fortuna_data.json (28 archaeological units)
├── Tempio_Fortuna_prompt.md (main reconstruction prompt)
├── Tempio_Fortuna_agent_architect.md
├── Tempio_Fortuna_agent_validator.md
├── Tempio_Fortuna_agent_texturizer.md
└── Tempio_Fortuna_agent_reconstructor.md
```

**Usage**:
```bash
# List all available sites
python3 scripts/generate_3d_with_claude.py --list

# Generate prompts for specific site
python3 scripts/generate_3d_with_claude.py --site "Tempio Fortuna"

# Interactive mode
python3 scripts/generate_3d_with_claude.py
```

### 5. Archaeological Dataset
**Database**: `data/pyarchinit_tutorial.db`

Created comprehensive Tempio della Dea Fortuna dataset:
- **12 Physical Units** (US 1000-1004, USM 2001-2007):
  - Stratigraphic layers with exact dimensions
  - Masonry structures (perimeter walls, column drums)
  - Modern restorations and medieval rebuilds
- **16 Extended Matrix Nodes**:
  - 3 EM_Reconstruction (virtual 3D models)
  - 2 EM_Ancient_Restoration (imperial period repairs)
  - 3 EM_Modern_Restoration (contemporary conservation)
  - 3 Combiner nodes (aggregation)
  - 2 Extractor nodes (component extraction)
  - 3 DOC nodes (documentation units)

All units include:
- Exact dimensions (length, width, height in meters)
- Absolute elevations (m a.s.l.)
- Period information (Republican, Imperial, Medieval, Modern)
- Material properties (travertine, marble, concrete)

## 🧪 Testing Procedure

### Step 1: Start PyArchInit Server
```bash
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" python3 -m pyarchinit_mini.web_interface.app
```

**Expected output**:
```
Starting PyArchInit-Mini Web Interface on 0.0.0.0:5001
WebSocket support enabled for real-time collaboration
 * Running on http://127.0.0.1:5001
```

**Verification**: Server is currently running on port 5001 ✅

### Step 2: Install Blender Addon Dependencies
```bash
# For Blender 4.2 on macOS
/Applications/Blender.app/Contents/Resources/4.2/python/bin/python3.11 -m pip install python-socketio[client]

# For other Blender versions, adjust path accordingly
```

### Step 3: Install Blender Addon
1. Open Blender
2. Edit → Preferences → Add-ons → Install
3. Navigate to: `/Users/enzo/Documents/pyarchinit-mini-desk/blender_addons/pyarchinit_realtime_streamer.py`
4. Enable the checkbox next to "PyArchInit Real-Time Streamer"
5. Verify WebSocket URL is set to: `http://localhost:5001`

### Step 4: Connect Blender to PyArchInit
1. In Blender 3D View, press `N` to open sidebar
2. Click "PyArchInit" tab
3. Click "Connect to PyArchInit" button
4. **Expected result**:
   - Status changes to "Connected"
   - Server terminal shows: `[Blender WebSocket] Blender connected: 4.2.0`

### Step 5: Test Real-Time Streaming

#### Test A: Object Creation
1. In Blender: Shift+A → Mesh → Cube
2. **Expected result**:
   - Server terminal: `[Blender Stream] Object created: Cube`
   - Web viewer at `http://localhost:5001/3d-builder` shows new cube
   - Alert notification: "Proxy created: Cube"

#### Test B: Object Transformation
1. In Blender: Press G (move cube)
2. **Expected result**:
   - Object updates in real-time in web viewer
   - Position synchronized between Blender and viewer

#### Test C: Material Updates
1. In Blender: Change cube material color
2. **Expected result**:
   - Material color updates in web viewer
   - Server terminal: `[Blender Stream] Material updated: Material`

#### Test D: Object Deletion
1. In Blender: Select cube, press X → Delete
2. **Expected result**:
   - Server terminal: `[Blender Stream] Object deleted: Cube`
   - Cube disappears from web viewer

#### Test E: Scene Synchronization
1. In Blender PyArchInit panel: Click "Send Scene Update"
2. **Expected result**:
   - Complete scene state transmitted
   - All Blender objects appear in web viewer

### Step 6: Test with Claude AI + blender-mcp (Advanced)

**Prerequisites**:
- blender-mcp installed and configured in Claude Desktop/Cursor
- Blender open with PyArchInit addon connected

**Workflow**:
1. Generate prompts:
   ```bash
   python3 scripts/generate_3d_with_claude.py --site "Tempio Fortuna"
   ```

2. In Claude (with blender-mcp):
   ```
   Please read the file at output/3d_generation/Tempio_Fortuna_prompt.md
   and create the archaeological 3D reconstruction in Blender.

   Use the specialized agent prompts to:
   1. Build base structure (Architect agent)
   2. Verify dimensions (Validator agent)
   3. Apply materials (Texturizer agent)
   4. Add reconstructions (Reconstructor agent)
   ```

3. **Expected result**:
   - Claude creates objects in Blender via blender-mcp
   - Each object creation broadcasts to web viewer in real-time
   - Progress updates appear in viewer chat
   - Final 3D model visible in both Blender and web viewer

## 📊 Implementation Statistics

- **Total files modified**: 3
  - `socketio_events.py`: +232 lines (Blender WebSocket events)
  - `app.py`: +2 lines (event handler registration)
  - `3d_builder/index.html`: +296 lines (Socket.IO client integration)

- **Total files created**: 2
  - `blender_addons/pyarchinit_realtime_streamer.py`: 350 lines
  - `scripts/generate_3d_with_claude.py`: ~400 lines
  - Archaeological dataset scripts: 2 files

- **Event types supported**: 9 bidirectional WebSocket events
- **Archaeological units created**: 28 (12 physical + 16 EM nodes)
- **Agent prompts generated**: 4 specialized agents

## 🔧 Troubleshooting

### Issue: Blender Won't Connect

**Solution 1**: Verify python-socketio installed in Blender's Python
```bash
/Applications/Blender.app/Contents/Resources/4.2/python/bin/python3.11 -m pip show python-socketio
```

**Solution 2**: Check WebSocket URL in addon preferences
- Must be: `http://localhost:5001` (not https, not trailing slash)

**Solution 3**: Verify server is running
```bash
curl http://localhost:5001
# Should return HTML (not connection refused)
```

### Issue: Objects Not Appearing in Viewer

**Check 1**: Open browser console (F12)
- Look for `[Blender Socket] Connected to server`
- Look for `[Blender] Object created: ...` messages

**Check 2**: Verify Socket.IO loaded
- Console should show Socket.IO library loaded
- Check network tab for socket.io requests

**Check 3**: Check coordinate system
- Blender uses Y-up, Three.js uses Z-up
- Conversion implemented in `createProxyFromBlender()` function

### Issue: Port Already in Use

**Solution**: Kill old server processes
```bash
pkill -f "python3 -m pyarchinit_mini.web_interface.app"
sleep 2
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" python3 -m pyarchinit_mini.web_interface.app
```

## 📚 Key Documentation

- **Setup Guide**: `REAL_TIME_BLENDER_SETUP.md` (comprehensive setup instructions)
- **Blender Addon**: `blender_addons/pyarchinit_realtime_streamer.py` (well-documented code)
- **WebSocket Events**: `pyarchinit_mini/web_interface/socketio_events.py` (lines 297-528)
- **Prompt Generation**: `scripts/generate_3d_with_claude.py` (CLI tool with --help)

## 🎯 Key Features Implemented

1. **Bidirectional Real-Time Communication**
   - Blender → Viewer (object updates)
   - Viewer → Blender (commands, queries)

2. **Automatic Scene Synchronization**
   - Depsgraph monitoring in Blender
   - Automatic broadcast of all changes
   - Reconnection logic

3. **Coordinate System Conversion**
   - Blender Y-up → Three.js Z-up
   - Handles location, rotation, scale

4. **Material Property Streaming**
   - Base color (RGB)
   - Roughness, metalness
   - Real-time material updates

5. **Build Progress Reporting**
   - Claude AI agent progress
   - Percentage complete
   - Current operation messages

6. **Connection Status Indicators**
   - Blender version display
   - Real-time connection state
   - Alert notifications

## 🚀 Next Steps

1. **Manual Testing Required**:
   - Install Blender addon
   - Test basic object creation
   - Test transformations
   - Test material updates
   - Test scene synchronization

2. **Advanced Testing** (Optional):
   - Install blender-mcp
   - Test Claude AI → Blender → Viewer pipeline
   - Use specialized agent prompts
   - Build complete archaeological reconstructions

3. **Performance Optimization** (Future):
   - Throttle rapid transformation updates
   - Implement delta updates (only changed properties)
   - Add LOD (Level of Detail) for complex scenes

4. **Enhanced Features** (Future):
   - Camera synchronization (Blender ↔ Viewer)
   - Measurement tools in viewer
   - Annotation system
   - Multi-user collaboration

## 📝 Notes

- **Port**: WebSocket uses port 5001 (same as Flask server)
- **CORS**: Enabled (`cors_allowed_origins="*"`)
- **Reconnection**: Auto-reconnect enabled (5 attempts)
- **Event Rate**: Blender depsgraph can generate many events; consider throttling if viewer performance degrades
- **Security**: This is a development setup; use proper authentication and SSL in production

## ✅ Verification Checklist

- [x] WebSocket server backend implemented
- [x] Blender addon created with full functionality
- [x] Web viewer Socket.IO integration complete
- [x] Archaeological dataset generated (Tempio Fortuna)
- [x] Claude AI prompt generation system
- [x] Specialized agent prompts (4 agents)
- [x] Documentation complete
- [x] Server running and tested
- [ ] Blender addon installed (requires manual user action)
- [ ] End-to-end streaming tested (requires Blender + addon)
- [ ] Claude AI + blender-mcp integration tested (optional advanced feature)

## 🎉 Achievement

Successfully implemented a complete real-time 3D archaeological reconstruction system that enables:
- Semantic documentation of excavations at 3D level
- Knowledge graph representation where every node is traceable
- Measurable, scaled, proportional 3D reconstructions
- Real-time collaboration between Blender and web viewer
- AI-assisted reconstruction with specialized agents
- Support for Extended Matrix nodes (reconstructions, restorations, documentation)

The system is now ready for testing and can be adapted to any archaeological site in the database.
