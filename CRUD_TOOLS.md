# CRUD + Validation Tools - v1.9.11

PyArchInit-Mini now provides comprehensive data management tools for Claude AI and ChatGPT to manage archaeological database records through MCP (Model Context Protocol).

## Overview

The `manage_data` MCP tool provides 6 operations:
1. **get_schema** - Inspect database structure
2. **insert** - Create new records
3. **update** - Modify existing records
4. **delete** - Remove records
5. **upsert** - Insert or update (conflict resolution)
6. **validate_stratigraphy** - Validate and fix stratigraphic relationships

## Quick Start

```python
# In Claude Desktop or ChatGPT with MCP support
from pyarchinit_mini.mcp_server.tools.data_management_tool import DataManagementTool

# Example: Get database schema
result = await tool.execute({
    "command": "get_schema",
    "table": "us_table",
    "include_constraints": True,
    "include_sample_values": True
})

# Example: Insert new US
result = await tool.execute({
    "command": "insert",
    "table": "us_table",
    "data": {
        "sito": "Scavo archeologico",
        "area": "1",
        "us": "150",
        "unita_tipo": "US",
        "d_stratigrafica": "Strato di crollo",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
})
```

## Tool Reference

### 1. get_schema

Get database schema information for PyArchInit tables.

**Parameters:**
- `table` (optional): Specific table name (us_table, site_table, etc.)
- `include_constraints` (bool): Include foreign keys and unique constraints
- `include_sample_values` (bool): Include example values for enum fields

**Example:**
```json
{
    "command": "get_schema",
    "table": "us_table",
    "include_constraints": true,
    "include_sample_values": true
}
```

**Returns:**
- Database type (sqlite/postgresql)
- Field types and properties (required, nullable, auto-increment)
- Primary keys
- Foreign key relationships
- Unique constraints
- Sample values for choice fields

### 2. insert

Insert new archaeological records into the database.

**Parameters:**
- `table` (required): Table name
- `data` (required): Dictionary of field_name -> value pairs
- `validate_only` (bool): Dry-run mode (validate without inserting)

**Example:**
```json
{
    "command": "insert",
    "table": "us_table",
    "data": {
        "sito": "Scavo archeologico",
        "area": "1",
        "us": "200",
        "unita_tipo": "US",
        "d_stratigrafica": "Strato",
        "created_at": "2025-11-02T12:00:00",
        "updated_at": "2025-11-02T12:00:00"
    },
    "validate_only": false
}
```

**Features:**
- Automatic field validation (required fields, data types)
- Foreign key validation
- Auto-increment field detection
- Transaction safety with rollback on error

**Returns:**
- Success status
- Inserted record ID
- Validation errors (if any)

### 3. update

Update existing archaeological records.

**Parameters:**
- `table` (required): Table name
- `data` (required): Dictionary of fields to update
- `record_id` (optional): Primary key ID
- `filters` (optional): Dictionary of filter conditions
- `validate_only` (bool): Dry-run mode

**Note:** Either `record_id` OR `filters` must be provided (not both).

**Example by ID:**
```json
{
    "command": "update",
    "table": "us_table",
    "record_id": 42,
    "data": {
        "d_stratigrafica": "Updated description",
        "updated_at": "2025-11-02T12:30:00"
    }
}
```

**Example by filters:**
```json
{
    "command": "update",
    "table": "us_table",
    "filters": {"sito": "Scavo archeologico", "area": "1"},
    "data": {"stato_di_conservazione": "Buono"}
}
```

**Features:**
- Partial updates (only specified fields are modified)
- Primary key protection (cannot update ID fields)
- Foreign key validation
- Dry-run preview

**Returns:**
- Success status
- Number of rows updated
- Validation errors (if any)

### 4. delete

Delete archaeological records from the database.

**Parameters:**
- `table` (required): Table name
- `record_id` (optional): Primary key ID
- `filters` (optional): Dictionary of filter conditions
- `confirm_delete` (bool): Must be `true` to actually delete (safety feature)
- `cascade_aware` (bool): Check for dependent records via foreign keys

**Note:** Either `record_id` OR `filters` must be provided.

**Example dry-run:**
```json
{
    "command": "delete",
    "table": "us_table",
    "record_id": 59,
    "confirm_delete": false,
    "cascade_aware": true
}
```

**Example actual delete:**
```json
{
    "command": "delete",
    "table": "us_table",
    "record_id": 59,
    "confirm_delete": true,
    "cascade_aware": true
}
```

**Safety Features:**
- `confirm_delete=true` required for actual deletion
- Dry-run mode shows what would be deleted
- Cascade warnings for dependent records
- Transaction rollback if foreign key violations occur

**Returns:**
- Success status
- Number of rows deleted
- Cascade warnings (if any)
- Dry-run info (if not confirmed)

### 5. upsert (resolve_conflicts)

Insert or update records with intelligent conflict resolution.

**Parameters:**
- `table` (required): Table name
- `data` (required): Dictionary of data to insert/update
- `conflict_keys` (required): List of fields that define uniqueness
- `resolution` (optional): Strategy ("detect", "skip", "update", "upsert")
- `merge_strategy` (optional): How to merge data ("prefer_new", "prefer_existing", "replace_all")

**Resolution Strategies:**
- `detect`: Only detect conflicts, don't modify data
- `skip`: Insert only if record doesn't exist
- `update`: Update only if record exists (error if not found)
- `upsert`: Insert if not exists, update if exists (default)

**Merge Strategies:**
- `prefer_new`: Use new values, keep old only if new is NULL
- `prefer_existing`: Keep existing values, use new only if old is NULL
- `replace_all`: Replace all fields with new values

**Example - detect conflict:**
```json
{
    "command": "upsert",
    "table": "us_table",
    "data": {
        "sito": "Scavo archeologico",
        "area": "1",
        "us": "200"
    },
    "conflict_keys": ["sito", "area", "us"],
    "resolution": "detect"
}
```

**Example - upsert:**
```json
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

**Features:**
- Atomic operations (no race conditions)
- Intelligent data merging
- Conflict detection before modification
- Transaction safety

**Returns:**
- Success status
- Conflict detected (true/false)
- Action taken ("inserted", "updated", "skipped", "detected")
- Affected rows count
- Existing record data (if conflict detected)
- Merged data (if update performed)

### 6. validate_stratigraphy

Validate and fix stratigraphic relationships for archaeological units.

**Parameters:**
- `site` (optional): Specific site to validate (None = all sites)
- `area` (optional): Specific area (requires site)
- `check_chronology` (bool): Validate chronological consistency with periodization data
- `auto_fix` (bool): Automatically fix missing reciprocal relationships

**Example - validate all:**
```json
{
    "command": "validate_stratigraphy",
    "site": null,
    "check_chronology": false,
    "auto_fix": false
}
```

**Example - validate and fix:**
```json
{
    "command": "validate_stratigraphy",
    "site": "Scavo archeologico",
    "area": "1",
    "check_chronology": true,
    "auto_fix": true
}
```

**What it Detects:**
1. **Paradoxes**: Contradictory relationships (e.g., US 1 covers 2 AND US 1 covered by 2)
2. **Cycles**: Circular dependencies in Harris Matrix (temporal paradoxes)
3. **Missing Reciprocals**: If US 1 covers 2, then US 2 should be covered by 1
4. **Chronological Inconsistencies**: Period conflicts with periodization data
5. **Non-existent US**: References to US that don't exist in the database

**Auto-Fix Capabilities:**
- ✓ Automatically fixes missing reciprocal relationships
- ✗ Cannot auto-fix paradoxes (requires manual intervention)
- ✗ Cannot auto-fix cycles (logical errors)
- ⚠ Warns about non-existent US (manual creation recommended)

**Features:**
- Works with Italian and English relationship types
- Categorizes errors by type
- Re-validates after applying fixes
- Provides improvement metrics

**Returns:**
- Success status
- Valid (true if no errors found)
- Units checked
- Relationships found
- Error count
- Error categories (paradoxes, cycles, chronology errors, other)
- Fixes applied (if auto_fix=true)
- Fixes count
- Warnings
- After-fixes validation report

## Database Schema

### Supported Tables

- `site_table` - Archaeological sites
- `us_table` - Stratigraphic units (US)
- `inventario_materiali_table` - Material inventory
- `datazioni_table` - Periodization/dating
- `us_relationships_table` - Explicit US relationships

### Required Fields (us_table)

- `sito` (VARCHAR) - Site name (foreign key to site_table)
- `us` (VARCHAR) - US number
- `created_at` (DATETIME) - Creation timestamp
- `updated_at` (DATETIME) - Update timestamp

### Optional Fields (us_table)

- `area` (TEXT) - Area identifier
- `unita_tipo` (VARCHAR) - Unit type (US, USM, USD, etc.)
- `d_stratigrafica` (TEXT) - Stratigraphic description
- `d_interpretativa` (TEXT) - Interpretative description
- `periodo_iniziale` (VARCHAR) - Initial period
- `periodo_finale` (VARCHAR) - Final period
- ... and 60+ more fields

## Best Practices

### 1. Always Validate Before Insert/Update

```python
# Step 1: Validate (dry-run)
result = await tool.execute({
    "command": "insert",
    "table": "us_table",
    "data": {...},
    "validate_only": True
})

# Step 2: Check validation result
if result["success"]:
    # Step 3: Actually insert
    result = await tool.execute({
        "command": "insert",
        "table": "us_table",
        "data": {...},
        "validate_only": False
    })
```

### 2. Use Dry-Run for Deletes

```python
# Always preview before deleting
result = await tool.execute({
    "command": "delete",
    "table": "us_table",
    "record_id": 42,
    "confirm_delete": False,  # Dry-run
    "cascade_aware": True
})

# Check cascade warnings
if result["cascade_warnings"]:
    print(f"Warning: {len(result['cascade_warnings'])} dependent records found")

# Then confirm delete if safe
if confirm_safe:
    result = await tool.execute({
        "command": "delete",
        "table": "us_table",
        "record_id": 42,
        "confirm_delete": True
    })
```

### 3. Use UPSERT for Data Import

```python
# When importing data where records may already exist
for record in import_data:
    result = await tool.execute({
        "command": "upsert",
        "table": "us_table",
        "data": record,
        "conflict_keys": ["sito", "area", "us"],
        "resolution": "upsert",
        "merge_strategy": "prefer_new"
    })
```

### 4. Regular Stratigraphy Validation

```python
# Run periodic validation
result = await tool.execute({
    "command": "validate_stratigraphy",
    "check_chronology": True,
    "auto_fix": False  # Don't auto-fix on first run
})

# Review errors
if not result["valid"]:
    print(f"Found {result['error_count']} errors:")
    print(f"  Paradoxes: {len(result['error_categories']['paradoxes'])}")
    print(f"  Cycles: {len(result['error_categories']['cycles'])}")

    # If only missing reciprocals, auto-fix is safe
    if result['error_categories']['paradoxes'] == [] and result['error_categories']['cycles'] == []:
        result = await tool.execute({
            "command": "validate_stratigraphy",
            "auto_fix": True
        })
```

### 5. Foreign Key Awareness

Always ensure referenced records exist:

```python
# Step 1: Check if site exists
result = await tool.execute({
    "command": "get_schema",
    "table": "site_table"
})

# Step 2: Insert site if needed
# Step 3: Insert US with valid site reference
result = await tool.execute({
    "command": "insert",
    "table": "us_table",
    "data": {
        "sito": "Existing Site Name",  # Must exist in site_table
        "us": "100",
        ...
    }
})
```

## Error Handling

All tools return a consistent error format:

```json
{
    "success": false,
    "error": "error_code",
    "message": "Human-readable error message",
    "validation_errors": [  // For validation failures
        {
            "field": "field_name",
            "error": "error_type",
            "message": "Error description"
        }
    ]
}
```

Common error codes:
- `validation_failed` - Data validation failed
- `integrity_error` - Database constraint violation (foreign key, unique, NOT NULL)
- `data_type_error` - Data type mismatch
- `no_records_found` - No records match the filter
- `missing_identifier` - Missing record_id or filters
- `unknown_field` - Field doesn't exist in table

## Testing

Run the comprehensive test suite:

```bash
export DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db"
python3 test_crud_tools.py
```

Test coverage:
- ✓ Get Schema (all tables)
- ✓ Insert validation + actual
- ✓ Update by ID and by filters
- ✓ Delete dry-run + actual with cascade checks
- ✓ Conflict detection
- ✓ UPSERT (insert or update)
- ✓ Stratigraphy validation (59 units, 51 relationships)

## Architecture

```
pyarchinit_mini/
├── mcp_server/
│   ├── tools/
│   │   ├── data_management_tool.py       # Unified MCP tool
│   │   ├── get_schema_tool.py            # Schema inspector
│   │   ├── insert_data_tool.py           # Insert records
│   │   ├── update_data_tool.py           # Update records
│   │   ├── delete_data_tool.py           # Delete records
│   │   ├── resolve_conflicts_tool.py     # Conflict resolution (UPSERT)
│   │   └── validate_stratigraphy_tool.py # Stratigraphic validator
│   └── server.py                         # MCP server (registers manage_data tool)
└── utils/
    └── stratigraphic_validator.py        # Validation logic
```

## Version History

**v1.9.11** (2025-11-02)
- ✨ New: CRUD + Validation tools for data management
- ✨ New: `manage_data` unified MCP tool with 6 operations
- ✨ New: Stratigraphic relationship validator with auto-fix
- 🐛 Fix: DatabaseManager initialization in all tools
- ✅ Test: Comprehensive test suite (11 test operations, all passing)

## License

GPL-3.0 - Same as PyArchInit-Mini

## Support

For issues or questions:
- GitHub: https://github.com/pyarchinit/pyarchinit-mini
- Documentation: See MCP_INTEGRATION.md
