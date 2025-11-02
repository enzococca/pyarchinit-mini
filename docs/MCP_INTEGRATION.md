# PyArchInit MCP Integration Guide

**Simple step-by-step guide to connect PyArchInit with AI assistants**

This guide explains how to integrate PyArchInit-Mini with AI assistants (Claude Desktop and ChatGPT) using the Model Context Protocol (MCP). With MCP, AI assistants can directly access your archaeological data, create 3D models, and generate stratigraphic analyses.

## Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [Quick Overview](#quick-overview)
3. [Setup for Claude Desktop](#setup-for-claude-desktop)
4. [Setup for ChatGPT](#setup-for-chatgpt)
5. [Available Tools](#available-tools)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)

---

## What is MCP?

**Model Context Protocol (MCP)** is a standard way for AI assistants to connect to external tools and data sources. Think of it as a bridge that lets Claude or ChatGPT:

- Read your archaeological database
- Generate Harris matrices
- Create 3D models
- Export data in various formats
- Analyze stratigraphic relationships

**Benefits:**
- Natural language interface to your data
- Automatic GraphML generation
- 3D model creation from US data
- Real-time data analysis

---

## Quick Overview

### Architecture

```
┌─────────────────┐
│  Claude Desktop │  or  │   ChatGPT    │
│  (Your computer)│      │  (Web browser)│
└────────┬────────┘      └──────┬───────┘
         │                       │
         │ MCP Protocol          │ HTTPS + SSE
         │                       │
    ┌────▼───────────────────────▼────┐
    │   PyArchInit MCP Server         │
    │   (Runs on your computer)       │
    └────────────┬────────────────────┘
                 │
                 │ SQL Queries
                 │
    ┌────────────▼────────────────────┐
    │   SQLite/PostgreSQL Database    │
    │   (Your archaeological data)    │
    └─────────────────────────────────┘
```

### Two Integration Methods

| Feature | Claude Desktop | ChatGPT |
|---------|---------------|---------|
| **Connection** | Direct (stdio) | Via HTTP/SSE |
| **Setup Difficulty** | Easy | Medium |
| **Internet Required** | No | Yes (for public access) |
| **Best For** | Local work | Remote collaboration |

---

## Setup for Claude Desktop

**Difficulty:** Easy
**Time:** 5 minutes
**Requirements:** Python 3.8+, PyArchInit-Mini installed

### Step 1: Install PyArchInit-Mini

```bash
# Install with pip
pip install pyarchinit-mini

# Or install from source
git clone https://github.com/enzococca/pyarchinit-mini.git
cd pyarchinit-mini
pip install -e .
```

### Step 2: Find Your Python Path

```bash
# Find the Python path
which python3

# Example output:
# /usr/local/bin/python3
# or
# /Users/yourusername/.pyenv/versions/3.11.6/bin/python3
```

**Copy this path** - you'll need it in the next step.

### Step 3: Find Your Database Path

```bash
# Find where your database is located
ls data/*.db

# Example output:
# data/pyarchinit_tutorial.db
```

Note the **full path** to your database file:
```bash
pwd  # Shows current directory, e.g., /Users/enzo/Documents/pyarchinit-mini-desk
# Full path: /Users/enzo/Documents/pyarchinit-mini-desk/data/pyarchinit_tutorial.db
```

### Step 4: Configure Claude Desktop

1. **Locate the config file:**
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

2. **Edit the config file** (create it if it doesn't exist):

```json
{
  "mcpServers": {
    "pyarchinit": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "pyarchinit_mini.mcp_server"],
      "env": {
        "DATABASE_URL": "sqlite:////Users/enzo/Documents/pyarchinit-mini-desk/data/pyarchinit_tutorial.db"
      }
    }
  }
}
```

**Important:** Replace these values:
- `"/usr/local/bin/python3"` → Your Python path from Step 2
- `"/Users/enzo/Documents/..."` → Your database path from Step 3

**Database URL Format:**
- SQLite: `sqlite:////absolute/path/to/database.db` (4 slashes!)
- PostgreSQL: `postgresql://user:password@localhost/dbname`

### Step 5: Restart Claude Desktop

1. **Quit Claude Desktop** completely
2. **Restart** the application
3. **Verify connection** - look for the hammer icon (🔨) in the input box

### Step 6: Test the Connection

Open a new chat in Claude Desktop and type:

```
List all archaeological sites in the database
```

Claude should respond with site data from your database!

---

## Setup for ChatGPT

**Difficulty:** Medium
**Time:** 15-30 minutes
**Requirements:** ChatGPT Plus/Pro account, PyArchInit-Mini installed, Public URL

### Overview

ChatGPT requires a **public URL** to connect to your MCP server. You have two options:

1. **Quick Testing** - Ngrok (temporary URL, changes each time)
2. **Permanent Access** - Cloudflare Tunnel (stable URL)

### Step 1: Install PyArchInit-Mini

Same as [Claude Desktop Step 1](#step-1-install-pyarchinit-mini)

### Step 2: Start the MCP HTTP Server

```bash
# Navigate to your project directory
cd /path/to/pyarchinit-mini

# Start the server
MCP_TRANSPORT=sse DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" \
python3 -m pyarchinit_mini.mcp_server.http_server
```

You should see:
```
[INFO] Starting PyArchInit MCP Server (HTTP/SSE mode)
[INFO] Server running on http://localhost:8765
[INFO] 5 tools, 5 resources, 3 prompts registered
```

Leave this terminal window open!

### Step 3A: Expose with Ngrok (Quick Testing)

**Best for:** Testing, temporary demos

1. **Install Ngrok:**
   ```bash
   # macOS
   brew install ngrok

   # Linux
   snap install ngrok

   # Windows
   choco install ngrok
   ```

2. **Create tunnel** (in a new terminal):
   ```bash
   ngrok http 8765
   ```

3. **Copy the HTTPS URL:**
   ```
   Forwarding  https://abc123.ngrok.io -> http://localhost:8765
   ```

   Copy: `https://abc123.ngrok.io`

**Note:** This URL changes every time you restart ngrok.

### Step 3B: Expose with Cloudflare Tunnel (Permanent)

**Best for:** Long-term use, stable URL

1. **Install Cloudflare Tunnel:**
   ```bash
   # macOS
   brew install cloudflared

   # Linux
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared-linux-amd64.deb
   ```

2. **Create quick tunnel** (no signup needed):
   ```bash
   cloudflared tunnel --url http://localhost:8765
   ```

3. **Copy the URL:**
   ```
   Your quick Tunnel has been created! Visit it at:
   https://random-words-here.trycloudflare.com
   ```

**For a permanent URL** (requires Cloudflare account):
See detailed instructions in [CHATGPT_MCP_SETUP.md](../CHATGPT_MCP_SETUP.md)

### Step 4: Configure ChatGPT

1. **Enable Developer Mode:**
   - Open ChatGPT in your browser
   - Go to **Settings** (⚙️) → **Apps & Connectors**
   - Scroll to **Advanced settings**
   - Enable **Developer Mode**

2. **Create MCP Connector:**
   - Go to **Settings** → **Connectors**
   - Click **Create** (or **Add custom connector**)

3. **Fill in the details:**

   ```
   Name:           PyArchInit MCP

   Description:    Archaeological data management server with stratigraphic
                   analysis, 3D model generation, and Harris matrix export.

   MCP Server URL: https://your-url-here.ngrok.io/mcp
                   (or https://your-tunnel.trycloudflare.com/mcp)

   Authentication: None
   ```

4. **Save** the connector

5. **Verify** - you should see: `✓ PyArchInit MCP - Connected`

### Step 5: Test the Connection

Open a new chat in ChatGPT and type:

```
Use PyArchInit MCP to show me all archaeological sites
```

ChatGPT should connect to your server and display the sites!

---

## Available Tools

PyArchInit MCP provides **5 main tools** for working with archaeological data:

### 1. build_3d
**Purpose:** Create 3D models from stratigraphic data

**Usage:**
```
Create a 3D model for US 1, 2, 3
Build 3D visualization for site "Pompei"
Generate 3D model with GraphML positioning
```

**Parameters:**
- `us_ids`: List of US IDs to include
- `mode`: "selected" | "all" | "site"
- `positioning`: "graphml" | "simple" | "grid"
- `site_id`: Site ID (when mode="site")

### 2. filter
**Purpose:** Filter stratigraphic units by criteria

**Usage:**
```
Show only US from Roman period
Filter US by area "Sector A"
Show structures (USM) only
```

**Parameters:**
- `periodo`: Filter by archaeological period
- `area`: Filter by excavation area
- `unita_tipo`: Filter by unit type (US, USM, USD, etc.)

### 3. export
**Purpose:** Export data in various formats

**Usage:**
```
Export site data to GraphML
Export US as CSV
Generate Harris Matrix PDF for site "Tempio"
```

**Parameters:**
- `format`: "graphml" | "csv" | "json" | "pdf"
- `data_type`: "sites" | "us" | "relationships"
- `site_id`: Site ID to export

### 4. position
**Purpose:** Calculate 3D positions for US

**Usage:**
```
Calculate positions using GraphML layout
Position US with 0.8m layer spacing
```

**Parameters:**
- `method`: "graphml" | "simple"
- `layer_spacing`: Vertical spacing between layers
- `us_ids`: US to position

### 5. material
**Purpose:** Apply materials to 3D models

**Usage:**
```
Color US 3 red
Apply stone material to USM 5
```

**Parameters:**
- `us_id`: US to modify
- `color`: Color name or hex code
- `material_type`: "earth" | "stone" | "brick"

---

## Usage Examples

### Example 1: Basic Site Query

**You ask:**
```
Show me all archaeological sites in the database
```

**AI responds with:**
- Site names
- Locations
- Descriptions
- Associated US counts

### Example 2: Stratigraphic Analysis

**You ask:**
```
For site "Tempio della Fortuna", show me:
1. All stratigraphic units (US)
2. Their relationships
3. Generate a Harris Matrix in GraphML format
```

**AI will:**
1. Query all US for that site
2. Find stratigraphic relationships (above/below/cuts/fills)
3. Generate GraphML file
4. Provide download link or content

### Example 3: 3D Model Creation

**You ask:**
```
Create a 3D model for US 1, 2, 3, 4, 5 with:
- GraphML positioning
- Layer spacing: 0.8 meters
- Colors based on period
```

**AI will:**
1. Fetch complete US data
2. Generate GraphML for relationships
3. Calculate 3D positions
4. Create proxy metadata
5. (If Blender connected) Generate actual 3D geometry

### Example 4: Period Analysis

**You ask:**
```
For site "Pompei":
1. How many US are from Roman period?
2. How many from Medieval period?
3. Create a period distribution chart
```

**AI will:**
1. Query and count US by period
2. Provide statistics
3. Suggest visualization options

### Example 5: Export for yEd

**You ask:**
```
Export the Harris Matrix for site "Scavo 2024" in GraphML format
optimized for yEd Graph Editor with:
- Period grouping
- Color-coded by US type
- All metadata included
```

**AI will:**
1. Generate GraphML with proper structure
2. Include EM_palette styling
3. Add all archaeological metadata
4. Provide formatted file ready for yEd

---

## Troubleshooting

### Claude Desktop Issues

#### Problem: No hammer icon visible

**Solution:**
1. Check config file syntax (JSON must be valid)
2. Verify Python path is correct
3. Verify database path is absolute and exists
4. Restart Claude Desktop completely (quit and reopen)

**Test config:**
```bash
# Verify Python works
/your/python/path -m pyarchinit_mini.mcp_server --help

# Should show MCP server help
```

#### Problem: "Database not found" error

**Solution:**
- Use absolute paths, not relative
- Check database file exists: `ls -l /path/to/database.db`
- For SQLite: Use 4 slashes: `sqlite:////absolute/path/to/file.db`

#### Problem: Tools not working

**Solution:**
1. Check logs: Look in Claude Desktop logs
2. Verify database has data: `sqlite3 your.db "SELECT COUNT(*) FROM site_table;"`
3. Reinstall: `pip uninstall pyarchinit-mini && pip install pyarchinit-mini`

---

### ChatGPT Issues

#### Problem: Connection failed

**Solution:**
1. Verify MCP server is running: `curl http://localhost:8765/health`
2. Check tunnel is active: Test the ngrok/cloudflare URL
3. Verify URL in ChatGPT includes `/mcp` at the end
4. Check firewall isn't blocking port 8765

**Test server:**
```bash
# Should return JSON with status
curl http://localhost:8765/health

# Should return capabilities
curl http://localhost:8765/capabilities
```

#### Problem: Tools not visible

**Solution:**
1. Delete and recreate the connector in ChatGPT
2. Restart MCP server
3. Check server logs for errors
4. Verify 5 tools registered in startup logs

#### Problem: Ngrok URL stops working

**Cause:** Free ngrok URLs change on restart

**Solution:**
- Use Cloudflare Tunnel for stable URL
- Or upgrade to ngrok paid plan for static domain

---

### General Issues

#### Database locked error

**Solution:**
- Close any other programs accessing the database
- Check no other PyArchInit instances running
- For SQLite: Ensure file isn't on network drive

#### Import errors

**Solution:**
```bash
# Reinstall with all dependencies
pip uninstall pyarchinit-mini
pip install pyarchinit-mini

# Or install from source
pip install -e .
```

#### Slow responses

**Solution:**
- Optimize database (run VACUUM for SQLite)
- Add indexes to tables
- Use PostgreSQL instead of SQLite for large datasets
- Reduce number of US in queries

---

## Advanced Configuration

### Using PostgreSQL

Instead of SQLite, use PostgreSQL for better performance:

```json
{
  "mcpServers": {
    "pyarchinit": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "pyarchinit_mini.mcp_server"],
      "env": {
        "DATABASE_URL": "postgresql://user:password@localhost/pyarchinit_db"
      }
    }
  }
}
```

### Custom Port for HTTP Server

```bash
# Run on different port
MCP_TRANSPORT=sse \
MCP_PORT=9000 \
DATABASE_URL="sqlite:///data/pyarchinit.db" \
python3 -m pyarchinit_mini.mcp_server.http_server
```

### Enable Debug Logging

```bash
# See detailed logs
MCP_TRANSPORT=sse \
LOG_LEVEL=DEBUG \
DATABASE_URL="sqlite:///data/pyarchinit.db" \
python3 -m pyarchinit_mini.mcp_server.http_server
```

---

## Next Steps

1. **Try the 3D Viewer** - See [3D_VIEWER_GUIDE.md](./3D_VIEWER_GUIDE.md)
2. **Connect Blender** - See [BLENDER_INTEGRATION.md](./BLENDER_INTEGRATION.md)
3. **Read detailed setup guides:**
   - [CLAUDE_DESKTOP_MCP_SETUP.md](../CLAUDE_DESKTOP_MCP_SETUP.md)
   - [CHATGPT_MCP_SETUP.md](../CHATGPT_MCP_SETUP.md)

---

## Resources

- **MCP Protocol:** https://modelcontextprotocol.io/
- **Claude Desktop:** https://claude.ai/download
- **ChatGPT Developer Mode:** https://help.openai.com/
- **PyArchInit-Mini:** https://github.com/enzococca/pyarchinit-mini

---

## Support

- **Issues:** https://github.com/enzococca/pyarchinit-mini/issues
- **Email:** enzo.ccc@gmail.com
- **Documentation:** https://github.com/enzococca/pyarchinit-mini/blob/main/README.md

---

**Last Updated:** November 2025
**PyArchInit-Mini Version:** 1.9.10+
