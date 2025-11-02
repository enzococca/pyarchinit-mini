# Claude Desktop MCP Setup

Simple setup guide for PyArchInit MCP Server with Claude Desktop using `uvx`.

## Quick Setup

### 1. Install PyArchInit-Mini

```bash
# Install from PyPI
pip install pyarchinit-mini[mcp]

# Or with uvx (recommended for Claude Desktop)
uvx pyarchinit-mini-mcp --version
```

### 2. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "pyarchinit": {
      "command": "uvx",
      "args": ["pyarchinit-mini-mcp"]
    }
  }
}
```

**That's it!** No paths, no environment variables needed.

### 3. Restart Claude Desktop

1. Quit Claude Desktop completely (Cmd+Q on macOS)
2. Start Claude Desktop
3. Look for the 🔧 tools icon - you should see 13 PyArchInit tools

## Features

### Automatic Configuration

The MCP server automatically:
- Creates default database at `~/.pyarchinit-mini/databases/default.db`
- Saves connection info to `~/.pyarchinit-mini/connections.json`
- Sets up export directory at `~/.pyarchinit-mini/exports/`

### Available Tools

Once connected, Claude can use:

1. **Database Management**
   - `manage_database_connections` - List/switch databases

2. **Data Management**
   - `build_3d` - Create 3D archaeological models
   - `filter` - Filter stratigraphic units
   - `export` - Export data to various formats

3. **Analysis**
   - `create_harris_matrix` - Generate Harris Matrix diagrams
   - `configure_em_nodes` - Configure Extended Matrix nodes

4. **Import/Export**
   - `import_excel` - Import Excel/CSV data
   - `pyarchinit_sync` - Sync with PyArchInit databases
   - `create_database` - Create new databases

5. **Search (ChatGPT compatibility)**
   - `search` - Search archaeological data
   - `fetch` - Fetch complete document details

6. **3D Positioning**
   - `position` - Position stratigraphic units in 3D
   - `material` - Assign materials to 3D models

### Database Management

Claude can manage your databases directly:

```
You: List my databases
Claude: [Uses manage_database_connections with action: "list"]

You: Switch to the Pompeii excavation database
Claude: [Uses manage_database_connections with action: "switch"]

You: What database am I using?
Claude: [Uses manage_database_connections with action: "current"]
```

## Directory Structure

After first run, you'll have:

```
~/.pyarchinit-mini/
├── databases/
│   └── default.db          # Default SQLite database
├── connections.json        # Saved database connections
├── exports/                # Exported files
└── logs/                   # Server logs
```

## Managing Multiple Databases

### Via Web Interface

1. Start the web interface:
   ```bash
   pyarchinit-mini-web
   ```

2. Go to Admin → Database → Add Connection

3. The connection will be automatically available in Claude Desktop

### Via Claude Desktop

Ask Claude to list connections:
```
You: What databases are available?
```

Claude will show all saved connections and mark the active one with ✓.

## Advanced Configuration (Optional)

If you need custom database or settings, you can still use environment variables:

```json
{
  "mcpServers": {
    "pyarchinit": {
      "command": "uvx",
      "args": ["pyarchinit-mini-mcp"],
      "env": {
        "DATABASE_URL": "sqlite:////path/to/custom.db",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

But for most users, the zero-config setup is recommended.

## Troubleshooting

### Tools not appearing in Claude Desktop

1. Check Claude Desktop logs:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp-server-pyarchinit.log
   ```

2. Verify the server can start:
   ```bash
   uvx pyarchinit-mini-mcp --version
   ```

3. Ensure Claude Desktop was fully restarted (Cmd+Q, not just window close)

### Database location

Default database is at: `~/.pyarchinit-mini/databases/default.db`

To use a different database:
1. Create it via web interface or CLI
2. Add connection via Admin → Database
3. Switch to it using Claude: "Switch to [database name]"

### Permission errors

If you see permission errors for `~/.pyarchinit-mini/`:

```bash
chmod -R u+w ~/.pyarchinit-mini
```

## Comparison with Manual Setup

| Aspect | uvx Setup | Manual Setup |
|--------|-----------|--------------|
| Configuration | 3 lines JSON | 15+ lines JSON |
| Path management | Automatic | Manual absolute paths |
| Database location | `~/.pyarchinit-mini/` | User-specified |
| Environment vars | None needed | DATABASE_URL, PYTHONPATH, etc. |
| Updates | `uvx` auto-updates | Manual reinstall |
| Multi-user | Works everywhere | Breaks on path changes |

## ChatGPT Integration

For ChatGPT integration via HTTP/SSE, see [CHATGPT_MCP_SETUP.md](CHATGPT_MCP_SETUP.md).

The HTTP server uses the same database management system, so databases added in Claude Desktop are automatically available in ChatGPT and vice versa.

## Next Steps

- Try asking Claude: "Create a 3D model of the site called Tempio"
- Ask: "What databases do I have?"
- Import Excel data: "Import this archaeological data from Excel"
- Create Harris Matrix: "Generate a Harris Matrix for site Tempio"

## Support

- GitHub: https://github.com/enzococca/pyarchinit-mini
- Issues: https://github.com/enzococca/pyarchinit-mini/issues
