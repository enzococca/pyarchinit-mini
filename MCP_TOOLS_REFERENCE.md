# PyArchInit MCP Tools Reference

Complete reference for all 14 MCP tools available in PyArchInit-Mini v1.9.11+

**Last Updated:** 2025-11-02
**Version:** 1.9.11

## Table of Contents

- [Overview](#overview)
- [Tool Categories](#tool-categories)
- [Quick Reference](#quick-reference)
- [3D Visualization Tools](#3d-visualization-tools)
  - [build_3d_from_us](#build_3d_from_us)
  - [calculate_positions](#calculate_positions)
  - [assign_materials](#assign_materials)
  - [filter_proxies](#filter_proxies)
  - [export_3d_model](#export_3d_model)
- [Data Management Tools](#data-management-tools)
  - [manage_data](#manage_data)
- [Data Import/Export Tools](#data-importexport-tools)
  - [import_excel](#import_excel)
  - [create_harris_matrix](#create_harris_matrix)
- [Search & Query Tools](#search--query-tools)
  - [search](#search)
  - [fetch](#fetch)
- [Database Operations Tools](#database-operations-tools)
  - [create_database](#create_database)
  - [manage_database_connections](#manage_database_connections)
- [Configuration Tools](#configuration-tools)
  - [configure_em_nodes](#configure_em_nodes)
  - [pyarchinit_sync](#pyarchinit_sync)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

PyArchInit-Mini provides 14 MCP (Model Context Protocol) tools that enable AI assistants like Claude and ChatGPT to interact with archaeological databases and create 3D stratigraphic visualizations.

**What is MCP?**
MCP (Model Context Protocol) is an open protocol that allows AI assistants to access external data sources and tools. PyArchInit-Mini implements MCP to provide AI-powered archaeological data management and visualization.

**Installation:**
See [MCP_INTEGRATION.md](MCP_INTEGRATION.md) for complete setup instructions.

---

## Tool Categories

### 3D Visualization (5 tools)
Build and customize 3D stratigraphic models in Blender
- `build_3d_from_us` - Generate 3D models from US data
- `calculate_positions` - Calculate spatial positions
- `assign_materials` - Apply materials and colors
- `filter_proxies` - Filter visible units
- `export_3d_model` - Export to glTF/glB formats

### Data Management (1 unified tool with 6 operations)
Comprehensive CRUD operations for archaeological data
- `manage_data` - Insert, update, delete, upsert, get schema, validate stratigraphy

### Data Import/Export (2 tools)
Import and create stratigraphic data
- `import_excel` - Import from Excel (Harris Matrix or Extended Matrix format)
- `create_harris_matrix` - Interactive Harris Matrix creation

### Search & Query (2 tools)
Search archaeological data (ChatGPT integration)
- `search` - Search sites and US units
- `fetch` - Fetch complete record details

### Database Operations (2 tools)
Manage database connections and creation
- `create_database` - Create new PyArchInit databases
- `manage_database_connections` - Switch between databases

### Configuration (2 tools)
Manage Extended Matrix node types and synchronization
- `configure_em_nodes` - Configure node visual properties
- `pyarchinit_sync` - Sync with PyArchInit full version

---

## Quick Reference

| Tool | Primary Use | Key Parameters |
|------|-------------|----------------|
| `build_3d_from_us` | Build 3D models | `site_id`, `us_ids` |
| `manage_data` | CRUD operations | `command`, `table`, `data` |
| `import_excel` | Import Excel data | `format`, `site_name`, `excel_base64` |
| `create_harris_matrix` | Create matrices | `site_name`, `nodes`, `relationships` |
| `search` | Search records | `query` |
| `fetch` | Get record details | `id` |
| `create_database` | Create databases | `db_type`, `db_path` |
| `manage_database_connections` | Manage connections | `action` |
| `configure_em_nodes` | Configure nodes | `action`, `tipo_id` |
| `pyarchinit_sync` | Sync with PyArchInit | `operation`, `source_db_url` |

---

## 3D Visualization Tools

### build_3d_from_us

**Purpose:** Generates 3D stratigraphic models in Blender from a list of stratigraphic units (US). Creates proxy objects with correct positioning based on stratigraphic relationships, applies materials based on periods, and tags proxies with US metadata.

**Parameters:**

- `site_id` (integer, required): Site ID to build model for
- `us_ids` (array of integers, required): List of US IDs to include in 3D model
- `graphml_id` (integer, optional): Optional GraphML ID to use for relationships
- `options` (object, optional): Build options
  - `positioning` (string, enum): Positioning algorithm to use
    - Valid values: `"graphml"`, `"grid"`, `"force_directed"`
    - Default: `"graphml"`
  - `auto_color` (boolean): Auto-apply colors based on periods
    - Default: `true`
  - `auto_material` (boolean): Auto-apply materials based on formation type
    - Default: `true`

**Returns:**

```json
{
  "success": true,
  "session_id": "uuid-string",
  "proxies": [...],
  "proxies_count": 15,
  "site_name": "Scavo archeologico",
  "graphml_filepath": "/path/to/graphml",
  "blender_enabled": true,
  "blender_status": "success",
  "blender_result": {...}
}
```

**Usage Examples:**

**Example 1: Build basic 3D model for specific US units**
```
AI Prompt: "Build a 3D model for site ID 1 with US units 1001, 1002, 1003, 1004, and 1005"
```

**Example 2: Build model with custom positioning and no auto-coloring**
```
AI Prompt: "Create a 3D visualization for site 'Scavo archeologico' using US 1001-1020 with grid positioning and manual materials"
```

**Example 3: Build model using all US from a specific GraphML**
```
AI Prompt: "Generate a complete 3D model for GraphML ID 5 with all stratigraphic units"
```

**Notes:**
- Automatically generates GraphML if not found and site is specified
- Communicates with Blender via MCP addon (requires Blender running with addon installed)
- Returns proxy metadata even if Blender connection fails
- Fetches complete archaeological data including descriptions, periods, and physical properties
- Environment variables: `BLENDER_HOST` (default: localhost), `BLENDER_PORT` (default: 9876)

---

### calculate_positions

**Purpose:** Calculates proxy positions based on stratigraphic relationships using different positioning algorithms.

**Parameters:**

- `us_ids` (array of integers, required): List of US IDs to position
- `algorithm` (string, optional): Positioning algorithm
  - Valid values: `"graphml"`, `"grid"`, `"force_directed"`
  - Default: `"graphml"`

**Returns:**

```json
{
  "success": true,
  "message": "Positions calculated (stub)"
}
```

**Usage Examples:**

**Example 1: Calculate positions using GraphML layout**
```
AI Prompt: "Calculate positions for US 1001-1010 using the GraphML algorithm"
```

**Example 2: Calculate grid layout**
```
AI Prompt: "Position these stratigraphic units in a grid pattern: 1001, 1002, 1003"
```

**Notes:**
- Currently returns stub implementation
- Future implementation will calculate spatial coordinates for 3D visualization
- Grid algorithm creates regular spacing, force_directed uses physics simulation, graphml uses existing layout

---

### assign_materials

**Purpose:** Assigns materials to 3D proxies based on archaeological periods, formation types, or custom rules.

**Parameters:**

- `session_id` (string, required): Session identifier for the 3D model
- `material_mode` (string, optional): Material assignment mode
  - Valid values: `"period"`, `"formation"`, `"custom"`
  - Default: `"period"`

**Returns:**

```json
{
  "success": true,
  "message": "Materials assigned (stub)"
}
```

**Usage Examples:**

**Example 1: Assign materials by archaeological period**
```
AI Prompt: "Apply period-based materials to the 3D model from session abc-123"
```

**Example 2: Assign materials by formation type**
```
AI Prompt: "Use formation types to assign materials to the model"
```

**Notes:**
- Currently returns stub implementation
- Period mode assigns colors based on chronological periods (Medieval, Roman, etc.)
- Formation mode assigns textures based on soil types (clay, sand, etc.)
- Custom mode allows manual material assignments

---

### filter_proxies

**Purpose:** Filters 3D proxies by period, US, or other criteria to show/hide specific units in the visualization.

**Parameters:**

- `session_id` (string, required): Session identifier for the 3D model
- `filters` (object, optional): Filter criteria (e.g., period, area, unit type)

**Returns:**

```json
{
  "success": true,
  "message": "Filter applied (stub)"
}
```

**Usage Examples:**

**Example 1: Filter by archaeological period**
```
AI Prompt: "Show only Medieval period units in the 3D model"
```

**Example 2: Filter by area**
```
AI Prompt: "Hide all US from Area B, keep only Area A visible"
```

**Notes:**
- Currently returns stub implementation
- Future implementation will toggle visibility in Blender
- Useful for focusing on specific chronological phases or excavation areas

---

### export_3d_model

**Purpose:** Exports 3D stratigraphic model in various formats for use in other applications.

**Parameters:**

- `session_id` (string, required): Session identifier for the 3D model to export
- `format` (string, optional): Export format
  - Valid values: `"gltf"`, `"glb"`
  - Default: `"gltf"`

**Returns:**

```json
{
  "success": true,
  "message": "Export initiated (stub)"
}
```

**Usage Examples:**

**Example 1: Export as glTF for web viewing**
```
AI Prompt: "Export the 3D model from session xyz-789 as glTF format"
```

**Example 2: Export as glB for sharing**
```
AI Prompt: "Export the stratigraphic model as a binary glB file"
```

**Notes:**
- Currently returns stub implementation
- glTF: JSON-based format, good for web applications
- glB: Binary format, smaller file size, good for sharing
- Future implementation will export from Blender scene

---

## Data Management Tools

### manage_data

**Purpose:** Unified tool providing comprehensive CRUD operations and stratigraphic validation for archaeological data. This single tool replaces multiple separate tools with 6 operations: get_schema, insert, update, delete, upsert, and validate_stratigraphy.

**Parameters:**

- `command` (string, required): Operation to perform
  - Valid values: `"get_schema"`, `"insert"`, `"update"`, `"delete"`, `"upsert"`, `"validate_stratigraphy"`

**Common Parameters:**
- `table` (string): Table name
  - Valid values: `"site_table"`, `"us_table"`, `"inventario_materiali_table"`, `"datazioni_table"`, `"us_relationships_table"`
- `data` (object): Data dictionary for insert/update/upsert operations
- `record_id` (integer): Primary key ID for update/delete operations
- `filters` (object): Filter conditions for update/delete operations
- `validate_only` (boolean): Dry-run mode (validate without executing)

**Operation-Specific Parameters:**

**get_schema:**
- `include_constraints` (boolean): Include foreign keys and constraints
  - Default: `true`
- `include_sample_values` (boolean): Include sample enum values
  - Default: `false`

**insert:**
- `table` (required)
- `data` (required)
- `validate_only` (optional)

**update:**
- `table` (required)
- `data` (required)
- `record_id` OR `filters` (required - one or the other)
- `validate_only` (optional)

**delete:**
- `table` (required)
- `record_id` OR `filters` (required - one or the other)
- `confirm_delete` (boolean): Must be `true` to actually delete (safety feature)
  - Default: `false`
- `cascade_aware` (boolean): Check for foreign key dependencies
  - Default: `true`

**upsert:**
- `table` (required)
- `data` (required)
- `conflict_keys` (array of strings, required): Fields that define uniqueness
- `resolution` (string): Strategy
  - Valid values: `"detect"`, `"skip"`, `"update"`, `"upsert"`
  - Default: `"upsert"`
- `merge_strategy` (string): How to merge conflicting data
  - Valid values: `"prefer_new"`, `"prefer_existing"`, `"replace_all"`
  - Default: `"prefer_new"`

**validate_stratigraphy:**
- `site` (string, optional): Site name for validation scope
- `area` (string, optional): Area identifier for validation scope
- `check_chronology` (boolean): Validate chronological consistency
  - Default: `false`
- `auto_fix` (boolean): Automatically fix missing reciprocal relationships
  - Default: `false`

**Returns:**

Returns vary by operation. See [CRUD_TOOLS.md](CRUD_TOOLS.md) for detailed return formats for each operation.

**Usage Examples:**

**Example 1: Get database schema for US table**
```
AI Prompt: "Show me the schema for the us_table including all constraints and sample values"

Tool call:
{
  "command": "get_schema",
  "table": "us_table",
  "include_constraints": true,
  "include_sample_values": true
}
```

**Example 2: Insert new stratigraphic unit**
```
AI Prompt: "Create a new US 1050 for site 'Scavo archeologico' in area 1, with stratigraphic description 'Layer of collapse'"

Tool call:
{
  "command": "insert",
  "table": "us_table",
  "data": {
    "sito": "Scavo archeologico",
    "area": "1",
    "us": "1050",
    "unita_tipo": "US",
    "d_stratigrafica": "Layer of collapse",
    "created_at": "2025-11-02T12:00:00",
    "updated_at": "2025-11-02T12:00:00"
  }
}
```

**Example 3: Update US description**
```
AI Prompt: "Update the stratigraphic description for US ID 42 to 'Roman floor level'"

Tool call:
{
  "command": "update",
  "table": "us_table",
  "record_id": 42,
  "data": {
    "d_stratigrafica": "Roman floor level",
    "updated_at": "2025-11-02T12:30:00"
  }
}
```

**Example 4: Delete with safety check**
```
AI Prompt: "Delete US with ID 59, but first check what would be affected"

Tool call (dry-run):
{
  "command": "delete",
  "table": "us_table",
  "record_id": 59,
  "confirm_delete": false,
  "cascade_aware": true
}

Then after review:
{
  "command": "delete",
  "table": "us_table",
  "record_id": 59,
  "confirm_delete": true,
  "cascade_aware": true
}
```

**Example 5: Upsert with conflict resolution**
```
AI Prompt: "Import US 200 from site 'Scavo archeologico', update if exists, insert if new"

Tool call:
{
  "command": "upsert",
  "table": "us_table",
  "data": {
    "sito": "Scavo archeologico",
    "area": "1",
    "us": "200",
    "d_stratigrafica": "Updated description",
    "created_at": "2025-11-02T12:00:00",
    "updated_at": "2025-11-02T12:00:00"
  },
  "conflict_keys": ["sito", "area", "us"],
  "resolution": "upsert",
  "merge_strategy": "prefer_new"
}
```

**Example 6: Validate stratigraphic relationships with auto-fix**
```
AI Prompt: "Check the stratigraphic relationships for 'Scavo archeologico' and fix any missing reciprocals"

Tool call:
{
  "command": "validate_stratigraphy",
  "site": "Scavo archeologico",
  "check_chronology": true,
  "auto_fix": true
}
```

**Notes:**
- This unified tool consolidates all database operations
- Always use `validate_only: true` for dry-run testing before actual modifications
- Delete operations require `confirm_delete: true` to execute (safety feature)
- Upsert is ideal for data imports where records may already exist
- Stratigraphic validation detects paradoxes, cycles, missing reciprocals, and chronological inconsistencies
- Auto-fix can resolve missing reciprocals but requires manual intervention for paradoxes and cycles
- See [CRUD_TOOLS.md](CRUD_TOOLS.md) for comprehensive documentation and examples

---

## Data Import/Export Tools

### import_excel

**Purpose:** Imports archaeological stratigraphic data from Excel files in two formats: Harris Matrix Template (separate NODES and RELATIONSHIPS sheets) or Extended Matrix (inline relationship columns). Automatically populates database and optionally generates GraphML file.

**Parameters:**

- `format` (string, required): Import format
  - Valid values: `"harris_template"`, `"extended_matrix"`
- `site_name` (string, required): Archaeological site name
- `excel_base64` (string, required): Base64-encoded Excel file content
- `filename` (string, required): Original filename (e.g., 'matrix.xlsx')
- `generate_graphml` (boolean, optional): Generate GraphML file after import
  - Default: `true`

**Returns:**

```json
{
  "success": true,
  "statistics": {
    "us_count": 25,
    "relationships_count": 48,
    "site_name": "Scavo archeologico"
  },
  "graphml_file": "/path/to/graphml",
  "graphml_available": true
}
```

**Usage Examples:**

**Example 1: Import Harris Matrix Template format**
```
AI Prompt: "Import the Excel file 'harris_matrix.xlsx' for site 'Tempio' using Harris Template format"

Note: The Excel file must have two sheets:
- NODES: Contains US data (US, Type, Description, Period, etc.)
- RELATIONSHIPS: Contains relationships (From_US, To_US, Relationship_Type)
```

**Example 2: Import Extended Matrix format with GraphML generation**
```
AI Prompt: "Import Extended Matrix Excel for 'Scavo archeologico' and generate a GraphML visualization"

Note: Extended Matrix format has relationship columns directly in the main sheet:
- Columns: US, Type, Description, Covers, Covered_by, Fills, etc.
```

**Example 3: Import without GraphML generation**
```
AI Prompt: "Import the Excel data for site 'Roman Villa' but don't generate the GraphML file"

Tool call:
{
  "format": "harris_template",
  "site_name": "Roman Villa",
  "excel_base64": "base64_encoded_content...",
  "filename": "villa_matrix.xlsx",
  "generate_graphml": false
}
```

**Notes:**
- Excel file must be base64-encoded before sending
- Harris Template format requires two sheets: NODES and RELATIONSHIPS
- Extended Matrix format uses inline relationship columns
- Automatically creates Site record if it doesn't exist
- Validates US types against Extended Matrix node configurations
- Creates US, USRelationships, and Periodizzazione records
- Synchronizes relationships to the `rapporti` field in US table
- GraphML export uses Gephi-compatible format

---

### create_harris_matrix

**Purpose:** Interactively create or edit Harris Matrix diagrams for stratigraphic analysis. Add nodes (US units) with properties and relationships between them. Supports Extended Matrix node types and standard stratigraphic relationships. Automatically saves to database and can optionally export to GraphML/DOT formats.

**Parameters:**

- `site_name` (string, required): Archaeological site name
- `mode` (string, optional): Mode
  - Valid values: `"create"`, `"edit"`
  - Default: `"create"`
- `nodes` (array, required): Array of US nodes to create/update
  - Each node object has:
    - `us_number` (string, required): US number/identifier (e.g., '1001', 'USM_5')
    - `unit_type` (string, optional): Node type
      - Valid values: US, USM, USVA, USVB, USVC, TU, USD, SF, VSF, CON, DOC, etc.
      - Default: `"US"`
    - `description` (string, optional): Stratigraphic description
    - `area` (string, optional): Excavation area (e.g., 'Area A', 'Sector 3')
    - `period` (string, optional): Archaeological period (e.g., 'Medieval', 'Roman')
    - `phase` (string, optional): Phase within period (e.g., 'Early', 'Late')
    - `file_path` (string, optional): Optional file path for documentation/photos
- `relationships` (array, optional): Array of stratigraphic relationships
  - Each relationship object has:
    - `from_us` (string, required): Source US number
    - `to_us` (string, required): Target US number
    - `relationship` (string, required): Relationship type
      - Valid values: `"Covers"`, `"Covered_by"`, `"Fills"`, `"Filled_by"`, `"Cuts"`, `"Cut_by"`, `"Bonds_to"`, `"Equal_to"`, `"Leans_on"`, `"Continuity"`, `">"`, `"<"`, `">>"`, `"<<"`
- `export_format` (string, optional): Export format after saving
  - Valid values: `"none"`, `"graphml"`, `"dot"`
  - Default: `"none"`

**Returns:**

```json
{
  "success": true,
  "site_name": "Scavo archeologico",
  "nodes_created": 10,
  "nodes_updated": 2,
  "relationships_created": 15,
  "relationships_updated": 3,
  "exported_file": "/path/to/export.graphml",
  "export_format": "graphml"
}
```

**Usage Examples:**

**Example 1: Create new Harris Matrix with nodes and relationships**
```
AI Prompt: "Create a Harris Matrix for 'Tempio' with US 1001 (Medieval floor) covering US 1002 (Roman wall)"

Tool call:
{
  "site_name": "Tempio",
  "mode": "create",
  "nodes": [
    {
      "us_number": "1001",
      "unit_type": "US",
      "description": "Medieval floor level",
      "period": "Medieval",
      "area": "A"
    },
    {
      "us_number": "1002",
      "unit_type": "USM",
      "description": "Roman wall foundation",
      "period": "Roman",
      "area": "A"
    }
  ],
  "relationships": [
    {
      "from_us": "1001",
      "to_us": "1002",
      "relationship": "Covers"
    }
  ],
  "export_format": "graphml"
}
```

**Example 2: Add more nodes to existing matrix**
```
AI Prompt: "Add US 1003, 1004, and 1005 to the 'Scavo archeologico' matrix with relationships"

Tool call:
{
  "site_name": "Scavo archeologico",
  "mode": "edit",
  "nodes": [
    {"us_number": "1003", "description": "Fill layer"},
    {"us_number": "1004", "description": "Cut for pit"},
    {"us_number": "1005", "description": "Pit fill"}
  ],
  "relationships": [
    {"from_us": "1003", "to_us": "1004", "relationship": "Fills"},
    {"from_us": "1004", "to_us": "1005", "relationship": "Cut_by"}
  ]
}
```

**Example 3: Create matrix with Extended Matrix node types**
```
AI Prompt: "Create a matrix with different node types: US, USM (masonry), and SF (stratigraphic feature)"

Tool call:
{
  "site_name": "Roman Fort",
  "nodes": [
    {"us_number": "1", "unit_type": "US", "description": "Topsoil"},
    {"us_number": "2", "unit_type": "USM", "description": "Stone wall"},
    {"us_number": "3", "unit_type": "SF", "description": "Post hole"}
  ],
  "relationships": [
    {"from_us": "1", "to_us": "2", "relationship": "Covers"},
    {"from_us": "1", "to_us": "3", "relationship": "Fills"}
  ]
}
```

**Notes:**
- Automatically creates Site record if it doesn't exist
- Creates or updates US, Periodizzazione, and USRelationships records
- Synchronizes relationships to the `rapporti` field in US table
- Supports both Italian and English relationship types
- Edit mode updates existing nodes without deleting others
- GraphML export is compatible with Gephi and yEd
- DOT export can be used with Graphviz for visualization
- Reciprocal relationships are automatically created (e.g., Covers → Covered_by)

---

## Search & Query Tools

### search

**Purpose:** Search archaeological stratigraphic data including sites and US (stratigraphic units). Implements the ChatGPT MCP integration 'search' tool. Returns results in ChatGPT-compatible format.

**Parameters:**

- `query` (string, required): Search query for archaeological data

**Returns:**

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"results\":[{\"id\":\"site-1\",\"title\":\"Site: Scavo archeologico\",\"url\":\"pyarchinit://site/1\"},{\"id\":\"us-42\",\"title\":\"US 1001 (Scavo archeologico) - US\",\"url\":\"pyarchinit://us/42\"}]}"
    }
  ]
}
```

**Usage Examples:**

**Example 1: Search for a site**
```
AI Prompt: "Search for 'Tempio' in the database"
```

**Example 2: Search for stratigraphic units**
```
AI Prompt: "Find all US containing 'medieval' or 'floor'"
```

**Example 3: Search by US number**
```
AI Prompt: "Search for US 1001"
```

**Notes:**
- Searches across multiple fields: site name, site description, US number, US description, unit type
- Case-insensitive search
- Returns top 10 results (5 sites + 5 US units max)
- Results include clickable URLs in format `pyarchinit://type/id`
- Designed for ChatGPT integration but works with any MCP client
- Returns empty results array if no matches found

---

### fetch

**Purpose:** Fetch complete details for a specific archaeological site or stratigraphic unit. Implements the ChatGPT MCP integration 'fetch' tool. Returns full document content in ChatGPT-compatible format.

**Parameters:**

- `id` (string, required): Document ID
  - Format: `"site-{id}"` or `"us-{id}"`
  - Examples: `"site-123"`, `"us-456"`

**Returns:**

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"id\":\"us-42\",\"title\":\"US 1001 (Scavo archeologico)\",\"text\":\"Stratigraphic Unit: 1001\\n\\nSite: Scavo archeologico\\n\\nUnit Type: US\\n\\nStratigraphic Description: Medieval floor level\\n\\nArea: A\\n\\nPeriod: Medieval\\n\\nPhase: Early\\n\\nRelationships: Covers US 1002\",\"url\":\"pyarchinit://us/42\",\"metadata\":{\"type\":\"stratigraphic_unit\",\"site\":\"Scavo archeologico\",\"unit_type\":\"US\",\"area\":\"A\",\"period\":\"Medieval\"}}"
    }
  ]
}
```

**Usage Examples:**

**Example 1: Fetch site details**
```
AI Prompt: "Get complete information for site-1"
```

**Example 2: Fetch US details**
```
AI Prompt: "Show me all data for us-42"
```

**Example 3: Fetch from search results**
```
AI Prompt: "Search for 'Tempio', then fetch the first result"

(Typically used after a search operation to get full details)
```

**Notes:**
- Returns complete record with all available fields
- Site documents include: name, definition, description, nation, municipality, province
- US documents include: US number, site, unit type, description, area, period, phase, relationships
- Metadata provides structured information about the record type
- Returns error document if ID not found or invalid format
- Designed for ChatGPT integration but works with any MCP client

---

## Database Operations Tools

### create_database

**Purpose:** Create an empty PyArchInit-Mini database with full schema. Supports SQLite and PostgreSQL. Creates all necessary tables for sites, stratigraphic units, inventories, relationships, etc.

**Parameters:**

- `db_type` (string, required): Database type
  - Valid values: `"sqlite"`, `"postgresql"`
- `db_path` (string, required): Database path/name
  - For SQLite: file path (e.g., `'data/new_project.db'`)
  - For PostgreSQL: database name (e.g., `'pyarchinit_production'`)
- `overwrite` (boolean, optional): If true, overwrite existing database
  - Default: `false`
- `postgres_config` (object, optional): PostgreSQL connection configuration (required for postgresql)
  - `host` (string): PostgreSQL host
    - Default: `"localhost"`
  - `port` (integer): PostgreSQL port
    - Default: `5432`
  - `user` (string, required): PostgreSQL user
  - `password` (string, optional): PostgreSQL password

**Returns:**

```json
{
  "success": true,
  "tables_created": 15,
  "db_type": "sqlite",
  "db_path": "data/new_project.db"
}
```

**Usage Examples:**

**Example 1: Create SQLite database**
```
AI Prompt: "Create a new SQLite database at 'data/medieval_site.db'"

Tool call:
{
  "db_type": "sqlite",
  "db_path": "data/medieval_site.db",
  "overwrite": false
}
```

**Example 2: Create PostgreSQL database**
```
AI Prompt: "Create a PostgreSQL database called 'pyarchinit_prod' on localhost"

Tool call:
{
  "db_type": "postgresql",
  "db_path": "pyarchinit_prod",
  "postgres_config": {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "secret123"
  }
}
```

**Example 3: Overwrite existing database**
```
AI Prompt: "Reset the database at 'data/test.db', overwrite if exists"

Tool call:
{
  "db_type": "sqlite",
  "db_path": "data/test.db",
  "overwrite": true
}
```

**Notes:**
- Creates complete PyArchInit-Mini schema with all tables and relationships
- SQLite databases are created as files on disk
- PostgreSQL databases are created on the server (requires admin privileges)
- Tables created include: site_table, us_table, inventario_materiali_table, datazioni_table, us_relationships_table, and more
- Schema includes proper foreign keys, indexes, and constraints
- Overwrite safety: requires explicit `overwrite: true` to replace existing database
- Returns error if database exists and `overwrite: false`

---

### manage_database_connections

**Purpose:** Manage database connections: list available connections, get current database info, or switch to a different database.

**Parameters:**

- `action` (string, required): Action to perform
  - Valid values: `"list"`, `"current"`, `"switch"`
- `connection_name` (string, optional): Connection name (required for 'switch' action)

**Returns:**

**For "list" action:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "Found 3 database connections:\n\n✓ production\n  Type: postgresql\n  Info: localhost:5432/pyarchinit_prod\n  Description: Production database\n\n  development\n  Type: sqlite\n  Info: data/dev.db\n  Description: Development database"
    }
  ]
}
```

**For "current" action:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "Current Database:\n\nType: SQLite\nPath: data/pyarchinit_tutorial.db\nConnection Name: tutorial"
    }
  ]
}
```

**For "switch" action:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "Switched database connection:\n\nFrom: sqlite:///data/tutorial.db\nTo: postgresql://localhost/pyarchinit_prod\n\nNote: This change affects the current MCP session only. To make it permanent, restart the MCP server or use the web interface."
    }
  ]
}
```

**Usage Examples:**

**Example 1: List all available database connections**
```
AI Prompt: "Show me all available database connections"

Tool call:
{
  "action": "list"
}
```

**Example 2: Get current database information**
```
AI Prompt: "What database am I currently connected to?"

Tool call:
{
  "action": "current"
}
```

**Example 3: Switch to a different database**
```
AI Prompt: "Switch to the production database"

Tool call:
{
  "action": "switch",
  "connection_name": "production"
}
```

**Notes:**
- Connections are managed via ConnectionManager configuration
- List action shows active connection with checkmark (✓)
- Switch action only affects current MCP session (not persistent)
- To make switch permanent, restart MCP server or use web interface
- Connection names are defined in configuration files
- Displays database type, connection string, description, and usage timestamps
- Returns error if connection name not found for switch action

---

## Configuration Tools

### configure_em_nodes

**Purpose:** Configure Extended Matrix node types for stratigraphic visualizations. Manage built-in and custom node types with visual properties (shapes, colors, fonts). Operations: list all node types, get specific type, create/update/delete custom types, list available shapes and symbol types.

**Parameters:**

- `action` (string, required): Action to perform
  - Valid values: `"list"`, `"get"`, `"create"`, `"update"`, `"delete"`, `"list_shapes"`, `"list_symbols"`
- `tipo_id` (string, optional): Node type ID (required for get, update, delete actions)
  - Examples: `"US"`, `"USM"`, `"USVA"`, `"TU"`, `"SF"`, etc.
- `node_config` (object, optional): Node configuration (required for create/update)
  - `name` (string): Display name for the node type
  - `description` (string): Description of the node type
  - `category` (string): Category
    - Valid values: `"stratigraphic"`, `"non-stratigraphic"`
  - `symbol_type` (string): Symbol type for relationships
    - Valid values: `"single_arrow"`, `"double_arrow"`, `"no_arrows"`
  - `label_format` (string): Label format template (e.g., `'US{number}'`, `'USM{number}'`)
  - `visual` (object): Visual configuration
    - `shape` (string): GraphML shape (rectangle, ellipse, roundrectangle, triangle, diamond, trapezium, etc.)
    - `fill_color` (string): Fill color (hex format, e.g., `'#FFFFFF'`)
    - `border_color` (string): Border color (hex format)
    - `border_width` (number): Border width
      - Default: `1.0`
    - `text_color` (string): Text color (hex format)
    - `font_family` (string): Font family
      - Default: `"DialogInput"`
    - `font_size` (integer): Font size
      - Default: `12`
    - `font_style` (string): Font style
      - Valid values: `"plain"`, `"bold"`, `"italic"`, `"bold_italic"`
    - `width` (number, optional): Node width
    - `height` (number, optional): Node height

**Returns:**

**For "list" action:**
```json
{
  "success": true,
  "total_count": 15,
  "stratigraphic_count": 10,
  "non_stratigraphic_count": 5,
  "stratigraphic_types": [...],
  "non_stratigraphic_types": [...]
}
```

**For "get" action:**
```json
{
  "success": true,
  "tipo_id": "USM",
  "name": "Unità Stratigrafica Muraria",
  "description": "Masonry stratigraphic unit",
  "category": "stratigraphic",
  "symbol_type": "single_arrow",
  "label_format": "USM{number}",
  "custom": false,
  "visual": {
    "shape": "rectangle",
    "fill_color": "#D4E6F1",
    "border_color": "#000000",
    ...
  }
}
```

**For "create/update/delete" actions:**
```json
{
  "success": true,
  "tipo_id": "CUSTOM_TYPE",
  "created": true
}
```

**For "list_shapes" action:**
```json
{
  "success": true,
  "shapes": ["rectangle", "ellipse", "roundrectangle", "triangle", "diamond", "trapezium", ...],
  "count": 12
}
```

**Usage Examples:**

**Example 1: List all node type configurations**
```
AI Prompt: "Show me all Extended Matrix node types"

Tool call:
{
  "action": "list"
}
```

**Example 2: Get configuration for specific node type**
```
AI Prompt: "What are the visual properties for USM nodes?"

Tool call:
{
  "action": "get",
  "tipo_id": "USM"
}
```

**Example 3: Create custom node type**
```
AI Prompt: "Create a custom node type 'FOUNDATION' with blue color and rectangular shape"

Tool call:
{
  "action": "create",
  "tipo_id": "FOUNDATION",
  "node_config": {
    "name": "Foundation Unit",
    "description": "Foundation or base structure",
    "category": "stratigraphic",
    "symbol_type": "single_arrow",
    "label_format": "FND{number}",
    "visual": {
      "shape": "rectangle",
      "fill_color": "#3498DB",
      "border_color": "#000000",
      "border_width": 2.0,
      "text_color": "#FFFFFF",
      "font_family": "DialogInput",
      "font_size": 14,
      "font_style": "bold"
    }
  }
}
```

**Example 4: Update existing custom node type**
```
AI Prompt: "Change the FOUNDATION node color to green"

Tool call:
{
  "action": "update",
  "tipo_id": "FOUNDATION",
  "node_config": {
    "visual": {
      "fill_color": "#27AE60"
    }
  }
}
```

**Example 5: Delete custom node type**
```
AI Prompt: "Remove the FOUNDATION custom node type"

Tool call:
{
  "action": "delete",
  "tipo_id": "FOUNDATION"
}
```

**Example 6: List available shapes**
```
AI Prompt: "What shapes can I use for nodes?"

Tool call:
{
  "action": "list_shapes"
}
```

**Notes:**
- Built-in node types (US, USM, USD, etc.) cannot be deleted or edited
- Only custom node types can be modified or removed
- Configuration is saved to JSON file and persists across sessions
- Changes require global config manager reset to take effect
- Visual properties affect GraphML export and yEd/Gephi visualization
- Symbol types determine relationship arrow styles (>, >>, or no arrows)
- Label format uses {number} placeholder for dynamic numbering
- Shapes must be valid GraphML/yEd shapes
- Colors must be in hex format (#RRGGBB)

---

### pyarchinit_sync

**Purpose:** Synchronize data between PyArchInit (full version) and PyArchInit-Mini. Import sites, US, inventories from PyArchInit or export data to PyArchInit. Automatically creates backups and handles database migrations.

**Parameters:**

- `operation` (string, required): Operation
  - Valid values: `"import"`, `"export"`
- `source_db_url` (string, required): Source database URL
  - Examples: `'sqlite:///path/to/pyarchinit.db'`, `'postgresql://user:pass@host/dbname'`
- `data_types` (array of strings, optional): Types of data to sync
  - Valid values: `"sites"`, `"us"`, `"inventario"`, `"thesaurus"`
  - Default: `["sites", "us"]`
- `site_filter` (array of strings, optional): Filter by site names (empty = all sites)
- `auto_backup` (boolean, optional): Create automatic backup before operation
  - Default: `true`

**Returns:**

```json
{
  "success": true,
  "imported": {
    "sites": 5,
    "us": 150,
    "relationships": 280
  },
  "backup_path": "/path/to/backup.db",
  "errors": []
}
```

**Usage Examples:**

**Example 1: Import all data from PyArchInit**
```
AI Prompt: "Import all sites and US from the PyArchInit database at '/data/pyarchinit_main.db'"

Tool call:
{
  "operation": "import",
  "source_db_url": "sqlite:///data/pyarchinit_main.db",
  "data_types": ["sites", "us"],
  "auto_backup": true
}
```

**Example 2: Import specific sites only**
```
AI Prompt: "Import only 'Tempio' and 'Scavo archeologico' sites from PyArchInit"

Tool call:
{
  "operation": "import",
  "source_db_url": "sqlite:///data/pyarchinit_main.db",
  "data_types": ["sites", "us"],
  "site_filter": ["Tempio", "Scavo archeologico"],
  "auto_backup": true
}
```

**Example 3: Import thesaurus data**
```
AI Prompt: "Import thesaurus controlled vocabulary from PyArchInit"

Tool call:
{
  "operation": "import",
  "source_db_url": "sqlite:///data/pyarchinit_main.db",
  "data_types": ["thesaurus"],
  "auto_backup": false
}
```

**Example 4: Export data to PyArchInit**
```
AI Prompt: "Export all PyArchInit-Mini data to the main PyArchInit database"

Tool call:
{
  "operation": "export",
  "source_db_url": "sqlite:///data/pyarchinit_main.db",
  "data_types": ["sites", "us"]
}
```

**Example 5: Import from PostgreSQL**
```
AI Prompt: "Import from PostgreSQL PyArchInit production database"

Tool call:
{
  "operation": "import",
  "source_db_url": "postgresql://user:password@localhost:5432/pyarchinit_prod",
  "data_types": ["sites", "us", "inventario"],
  "auto_backup": true
}
```

**Notes:**
- Import operation: PyArchInit → PyArchInit-Mini
- Export operation: PyArchInit-Mini → PyArchInit
- Auto-backup creates timestamped backup before import (recommended)
- Site filter applies to both sites and related US/inventory records
- Thesaurus import includes controlled vocabularies for periods, materials, etc.
- Handles schema differences between PyArchInit and PyArchInit-Mini
- Creates missing foreign key records automatically
- Import is non-destructive (adds/updates, doesn't delete)
- Export requires write access to target database
- Returns partial success if some data types fail
- Errors array contains details of any failures

---

## Best Practices

### 1. Always Validate Before Modifying Data

Use `validate_only: true` for dry-run testing:

```json
{
  "command": "insert",
  "table": "us_table",
  "data": {...},
  "validate_only": true
}
```

### 2. Use Dry-Run for Delete Operations

Preview what will be deleted before confirming:

```json
{
  "command": "delete",
  "table": "us_table",
  "record_id": 42,
  "confirm_delete": false,
  "cascade_aware": true
}
```

### 3. Leverage Upsert for Data Imports

When importing data where records may already exist:

```json
{
  "command": "upsert",
  "table": "us_table",
  "data": {...},
  "conflict_keys": ["sito", "area", "us"],
  "resolution": "upsert"
}
```

### 4. Regular Stratigraphic Validation

Run periodic validation to catch errors early:

```json
{
  "command": "validate_stratigraphy",
  "check_chronology": true,
  "auto_fix": false
}
```

### 5. Check GraphML Before 3D Building

Ensure GraphML exists or will be auto-generated:

```json
{
  "site_id": 1,
  "us_ids": [1001, 1002, 1003]
}
```

### 6. Use Site Filters for Large Imports

Import specific sites to avoid overwhelming the database:

```json
{
  "operation": "import",
  "source_db_url": "...",
  "site_filter": ["Tempio", "Roman Fort"]
}
```

### 7. Backup Before Major Operations

Enable auto-backup for imports and syncs:

```json
{
  "operation": "import",
  "source_db_url": "...",
  "auto_backup": true
}
```

---

## Troubleshooting

### Problem: "Blender connection failed"

**Solution:**
1. Ensure Blender is running
2. Install PyArchInit Blender MCP addon
3. Check environment variables: `BLENDER_HOST` and `BLENDER_PORT`
4. Default connection: localhost:9876

### Problem: "Foreign key constraint violation"

**Solution:**
1. Ensure referenced records exist (e.g., site must exist before creating US)
2. Use `get_schema` to check foreign key relationships
3. Create parent records first (sites before US, US before relationships)

### Problem: "GraphML not found"

**Solution:**
1. Specify `site_id` to enable auto-generation
2. Or create GraphML using `create_harris_matrix` tool
3. Or import Excel with `generate_graphml: true`

### Problem: "Validation errors on insert"

**Solution:**
1. Use `validate_only: true` to see detailed errors
2. Check required fields with `get_schema`
3. Verify data types match schema
4. Include `created_at` and `updated_at` timestamps

### Problem: "Stratigraphic paradox detected"

**Solution:**
1. Run validation without auto_fix to review errors
2. Manually resolve contradictory relationships
3. Use Harris Matrix principles: stratigraphic law of superposition
4. Cannot be auto-fixed, requires archaeological judgment

### Problem: "Cannot delete node type"

**Solution:**
- Only custom node types can be deleted
- Built-in types (US, USM, etc.) are protected
- Create a new custom type instead of modifying built-in ones

### Problem: "Database connection switch not permanent"

**Solution:**
- Switch only affects current MCP session
- To make permanent: restart MCP server or use web interface
- Or update configuration files directly

---

## Additional Resources

- **MCP Integration Guide**: [MCP_INTEGRATION.md](MCP_INTEGRATION.md)
- **CRUD Tools Documentation**: [CRUD_TOOLS.md](CRUD_TOOLS.md)
- **Blender Setup Guide**: [BLENDER_MCP_SETUP.md](BLENDER_MCP_SETUP.md)
- **Real-time Streaming**: [REAL_TIME_STREAMING_COMPLETE.md](REAL_TIME_STREAMING_COMPLETE.md)
- **Claude Desktop Usage**: [CLAUDE_DESKTOP_USAGE.md](CLAUDE_DESKTOP_USAGE.md)

---

**License:** GPL-3.0 (same as PyArchInit-Mini)
**Repository:** https://github.com/pyarchinit/pyarchinit-mini
**Support:** Open an issue on GitHub for questions or bug reports
