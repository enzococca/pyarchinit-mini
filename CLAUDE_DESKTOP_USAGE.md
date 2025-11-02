# Using PyArchInit with Claude Desktop - Complete Guide

## Overview

This guide explains how to use PyArchInit's real-time 3D viewer with Claude Desktop for archaeological data visualization and Blender integration.

## System Architecture

```
Claude Desktop (AI Assistant)
    ↓ (queries data via HTTP)
PyArchInit Server (REST API + Socket.IO)
    ↓ (real-time stream)
Blender (with PyArchInit addon)
    ↓ (real-time updates)
3D Viewer (Browser)
```

## Prerequisites

1. **PyArchInit Server** running on `http://localhost:5001`
2. **Blender** with PyArchInit Real-Time Streamer addon installed
3. **Claude Desktop** (or any AI assistant with HTTP access)
4. **Web Browser** for the 3D viewer

## Step 1: Start PyArchInit Server

```bash
cd /Users/enzo/Documents/pyarchinit-mini-desk

# Start with your database
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" python3 -m pyarchinit_mini.web_interface.app

# Or with PostgreSQL
DATABASE_URL="postgresql://user:pass@localhost/pyarchinit" python3 -m pyarchinit_mini.web_interface.app
```

Server starts on: `http://localhost:5001`

## Step 2: Open the 3D Viewer

You have two options:

**Option 1 - From the menu** (recommended):
1. Login to PyArchInit web interface: `http://localhost:5001`
2. Click: Menu → Tools → **Blender 3D Viewer**

**Option 2 - Direct URL**:
```
http://localhost:5001/api/3d-builder/viewer
```

The viewer provides:
- **Real-time Blender streaming** via Socket.IO
- **Archaeological data browser** (sites, US units)
- **Interactive 3D scene** with Three.js
- **Unit details panel** with full metadata

## Step 3: Connect Blender (Optional)

If you want real-time 3D model streaming from Blender:

1. **Install Blender addon dependencies**:
   ```bash
   # For Blender 4.5
   /Applications/Blender.app/Contents/Resources/4.5/python/bin/python3.11 -m pip install "python-socketio[client]"
   ```

2. **Install addon in Blender**:
   - Edit → Preferences → Add-ons → Install
   - Select: `blender_addons/pyarchinit_realtime_streamer.py`
   - Enable the addon

3. **Connect to PyArchInit**:
   - Press `N` in 3D View to open sidebar
   - Go to "PyArchInit" tab
   - Click "Connect to PyArchInit"
   - Status should show "Connected"

4. **Test the connection**:
   - Create any object in Blender (Shift+A)
   - Object should appear in the web viewer in real-time

## Step 4: Using Claude Desktop to Query Data

Claude Desktop can query the archaeological database without any configuration changes.

### Example Prompts for Claude Desktop

#### 1. List All Available Sites

```
Please fetch the list of all archaeological sites from the PyArchInit database.

Use this endpoint:
GET http://localhost:5001/api/3d-builder/archaeological-data
```

**What Claude will see**:
```json
{
  "success": true,
  "database": {"type": "sqlite", "connected": true},
  "sites": [
    {
      "id": 1,
      "nome": "Roman Forum Excavation",
      "comune": "Rome",
      "regione": "Lazio",
      "nazione": "Italy"
    },
    ...
  ],
  "summary": {
    "total_sites": 3,
    "total_us": 7
  }
}
```

#### 2. Get Data for a Specific Site

```
Please get all archaeological data for the "Roman Forum Excavation" site, including stratigraphic units and their dimensions.

GET http://localhost:5001/api/3d-builder/archaeological-data?site=Roman%20Forum%20Excavation
```

**What Claude will see**:
- Complete site information
- All US (Stratigraphic Units) with full details:
  - US number, area, type
  - Stratigraphic and interpretative descriptions
  - Physical dimensions (length, width, height, depth)
  - Elevations (relative and absolute)
  - Physical properties (color, consistency)
  - Material inclusions

#### 3. Analyze Archaeological Data

```
Please analyze the stratigraphic sequence for "Roman Forum Excavation":

1. Fetch the site data
2. List all US units ordered by stratigraphic position
3. Identify any structural elements (walls, floors, foundations)
4. Summarize the chronological phases

GET http://localhost:5001/api/3d-builder/archaeological-data?site=Roman%20Forum%20Excavation
```

#### 4. Generate 3D Reconstruction Instructions

```
Based on the archaeological data from "Roman Forum Excavation", create instructions for building a 3D model in Blender:

1. Fetch the site data with dimensions
2. For each US with physical dimensions, generate:
   - Object type (cube for foundations, plane for floors, etc.)
   - Exact dimensions in meters
   - Position (from elevation data)
   - Material suggestions (based on description)

GET http://localhost:5001/api/3d-builder/archaeological-data?site=Roman%20Forum%20Excavation&include_dimensions=true
```

## API Endpoints Reference

### GET /api/3d-builder/archaeological-data

Query archaeological data from the currently connected database.

**Parameters**:
- `site` (optional) - Filter by site name
- `include_em` (optional, default: true) - Include Extended Matrix nodes
- `include_dimensions` (optional, default: true) - Include dimensional data

**Response**:
```json
{
  "success": true,
  "database": {
    "type": "sqlite",
    "connected": true
  },
  "query_params": {
    "site_filter": "Roman Forum Excavation",
    "include_em": true,
    "include_dimensions": true
  },
  "sites": [...],
  "us_data": [
    {
      "id_us": 1,
      "sito": "Roman Forum Excavation",
      "area": "1",
      "us": "1001",
      "d_stratigrafica": "Wall foundation",
      "d_interpretativa": "Foundation for temple wall...",
      "lunghezza_max": 12.5,
      "larghezza_max": 2.5,
      "altezza_max": 1.8,
      "quota_abs": 15.2,
      "colore": "Gray",
      "consistenza": "Compact",
      ...
    }
  ],
  "em_nodes": [...],
  "summary": {
    "total_sites": 1,
    "total_us": 3,
    "total_em_nodes": 0,
    "us_by_type": {"Unknown": 3}
  }
}
```

### GET /api/3d-builder/viewer

Opens the interactive 3D viewer (browser interface).

**No parameters required**. No authentication needed.

## Workflow Examples

### Workflow 1: Simple Data Query

1. **Start PyArchInit server**
2. **Ask Claude Desktop**:
   ```
   What archaeological sites are available in the database?
   GET http://localhost:5001/api/3d-builder/archaeological-data
   ```
3. **Claude responds** with the list of sites
4. **Ask for details**:
   ```
   Get detailed information for "Roman Forum Excavation" including all US units
   ```

### Workflow 2: Data Analysis

1. **Start PyArchInit server**
2. **Ask Claude Desktop**:
   ```
   Analyze the stratigraphy of "Roman Forum Excavation":
   - Fetch all US data
   - Identify structural phases
   - Create a chronological sequence
   - Highlight any anomalies
   ```
3. **Claude fetches data** and provides analysis

### Workflow 3: Full 3D Workflow with Blender

1. **Start PyArchInit server**
2. **Open 3D viewer** in browser
3. **Start Blender** with addon connected
4. **Ask Claude Desktop**:
   ```
   Create a 3D reconstruction of "Roman Forum Excavation" in Blender:
   1. Fetch the archaeological data
   2. For each structural US (walls, foundations, floors):
      - Create appropriate geometry
      - Use exact dimensions from database
      - Position at correct elevations
      - Apply realistic materials
   ```
5. **Claude creates objects** in Blender
6. **Objects appear** in viewer in real-time
7. **Query data** in viewer sidebar to compare

## Advantages of This Approach

1. **No Config Changes**: Claude Desktop reads from currently connected database via HTTP
2. **Database Agnostic**: Works with SQLite or PostgreSQL
3. **Real-Time Visualization**: See Blender changes instantly in viewer
4. **Full Data Access**: Complete archaeological dataset with dimensions
5. **No Authentication**: Simplified workflow for local development
6. **Bi-directional**: Query data + visualize 3D models simultaneously

## Troubleshooting

### Server Not Responding

```bash
# Check if server is running
curl http://localhost:5001/api/3d-builder/archaeological-data

# If not running, start it
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" python3 -m pyarchinit_mini.web_interface.app
```

### Blender Not Connecting

1. **Check python-socketio installed**:
   ```bash
   /Applications/Blender.app/Contents/Resources/4.5/python/bin/python3.11 -m pip show python-socketio
   ```

2. **Check addon is enabled** in Blender Preferences

3. **Check WebSocket URL** in addon preferences (should be `http://localhost:5001`)

4. **Check server logs** for connection attempts

### Viewer Shows No Data

1. **Click "Load Sites"** button in viewer sidebar
2. **Check browser console** (F12) for errors
3. **Verify API endpoint**:
   ```bash
   curl http://localhost:5001/api/3d-builder/archaeological-data
   ```

## Advanced Usage

### Using with Different Databases

Simply change the DATABASE_URL when starting the server:

```bash
# SQLite database 1
DATABASE_URL="sqlite:///path/to/site1.db" python3 -m pyarchinit_mini.web_interface.app

# PostgreSQL database 2
DATABASE_URL="postgresql://user:pass@localhost/site2" python3 -m pyarchinit_mini.web_interface.app
```

Claude Desktop queries will automatically use the currently connected database.

### Programmatic Access from Claude

Claude can make multiple requests to build complex analyses:

```python
# Pseudo-code of what Claude might do:

# 1. Get all sites
sites = fetch("http://localhost:5001/api/3d-builder/archaeological-data")

# 2. For each site, get detailed data
for site in sites["sites"]:
    details = fetch(f"http://localhost:5001/api/3d-builder/archaeological-data?site={site['nome']}")

    # 3. Analyze stratigraphic sequence
    analyze_stratigraphy(details["us_data"])

    # 4. Generate 3D reconstruction plan
    create_3d_plan(details)
```

## Files Reference

- **Viewer**: `/api/3d-builder/viewer`
- **API Endpoint**: `/api/3d-builder/archaeological-data`
- **Blender Addon**: `blender_addons/pyarchinit_realtime_streamer.py`
- **Socket.IO Events**: `pyarchinit_mini/web_interface/socketio_events.py`
- **Routes**: `pyarchinit_mini/web_interface/three_d_builder_routes.py`

## Next Steps

1. **Test the API** with Claude Desktop
2. **Try the viewer** with your archaeological data
3. **Connect Blender** for real-time streaming
4. **Build 3D reconstructions** with AI assistance

## Support

- Check `REAL_TIME_STREAMING_COMPLETE.md` for technical details
- Check `REAL_TIME_BLENDER_SETUP.md` for Blender setup
- Server logs provide debugging information
- Browser console (F12) shows client-side errors
