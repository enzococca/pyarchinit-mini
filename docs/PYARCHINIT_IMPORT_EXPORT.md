# PyArchInit Import/Export Documentation

## Overview

The PyArchInit Import/Export feature provides bidirectional data synchronization between PyArchInit (full version) and PyArchInit-Mini databases. This allows users to:

- Import archaeological data from existing PyArchInit databases
- Export data from PyArchInit-Mini to PyArchInit format
- Migrate between SQLite and PostgreSQL databases
- Maintain data compatibility with the full PyArchInit system

## Supported Data Types

### Import
- **Sites** (`site_table`) - Archaeological site information
- **US** (`us_table`) - Stratigraphic units with automatic relationship mapping
- **Inventario Materiali** (`inventario_materiali_table`) - Artifact inventory
- **Periodizzazione** (`periodizzazione_table`) - Chronological periods
- **Thesaurus** (`pyarchinit_thesaurus_sigle`) - Terminology and abbreviations

### Export
- **Sites** - Site data export to PyArchInit format
- **US with Relationships** - Stratigraphic units with automatic rapporti field generation

## Key Features

### Intelligent Relationship Mapping

PyArchInit stores US relationships in a `rapporti` TEXT field using Python list format:
```python
[['Copre', '2'], ['Copre', '8'], ['Taglia', '5']]
```

PyArchInit-Mini uses a relational table `us_relationships_table` with proper foreign keys. The import/export service automatically converts between these formats:

**Import**: Parses the rapporti string and creates individual relationship records
**Export**: Aggregates relationship records and generates the rapporti list format

### Database Support

- **Source/Target**: SQLite and PostgreSQL
- **Connection Strings**:
  - SQLite: `sqlite:////absolute/path/to/database.db`
  - PostgreSQL: `postgresql://user:password@host:port/database`

### Site Filtering

All operations support filtering by site name, allowing selective import/export of specific archaeological sites.

## Usage

### 1. Command Line Interface (CLI)

#### Installation

```bash
pip install pyarchinit-mini
```

#### Import from PyArchInit

```bash
# Import all data types from a site
pyarchinit-mini-import import-from-pyarchinit \
  --source-db "sqlite:////path/to/pyarchinit_db.sqlite" \
  --tables all \
  --sites "Scavo archeologico"

# Import specific tables
pyarchinit-mini-import import-from-pyarchinit \
  --source-db "postgresql://user:pass@localhost:5432/pyarchinit" \
  --tables sites \
  --tables us \
  --sites "Pompei" \
  --sites "Ercolano" \
  --import-relationships

# Import without relationships
pyarchinit-mini-import import-from-pyarchinit \
  --source-db "sqlite:////path/to/db.sqlite" \
  --tables us \
  --no-import-relationships
```

#### Export to PyArchInit

```bash
# Export sites and US to PyArchInit
pyarchinit-mini-import export-to-pyarchinit \
  --target-db "sqlite:////path/to/target_db.sqlite" \
  --tables sites \
  --tables us \
  --sites "Sito Test" \
  --export-relationships
```

#### List Available Sites

```bash
# List sites in a PyArchInit database
pyarchinit-mini-import list-sites \
  --source-db "sqlite:////path/to/pyarchinit_db.sqlite"
```

#### CLI Options

- `--source-db`, `-s`: Source database connection string (required for import/list)
- `--target-db`, `-t`: Target database connection string (required for export)
- `--tables`, `-T`: Tables to import/export (sites, us, inventario, periodizzazione, thesaurus, all)
- `--sites`: Site names to filter (can specify multiple)
- `--import-relationships/--no-import-relationships`: Import US relationships (default: yes)
- `--export-relationships/--no-export-relationships`: Export US relationships (default: yes)

### 2. Desktop GUI

#### Access

1. Launch PyArchInit-Mini Desktop GUI
2. Navigate to **Tools** → **PyArchInit Import/Export**

#### Import Process

1. **Select Operation**: Click "Import" tab
2. **Database Type**: Choose SQLite or PostgreSQL
3. **Connection Details**:
   - **SQLite**: Click "Browse" to select database file
   - **PostgreSQL**: Enter host, port, database name, username, password
4. **Test Connection**: Click "Test Connection" to verify and load available sites
5. **Select Data**:
   - Check tables to import (Sites, US, Inventario, Periodizzazione, Thesaurus)
   - Select "Import Relationships" for US data
   - Use site filter to select specific sites
6. **Start Import**: Click "Import" button
7. **Monitor Progress**: View real-time logs in the console area

#### Export Process

1. **Select Operation**: Click "Export" tab
2. **Database Type**: Choose SQLite or PostgreSQL
3. **Connection Details**: Enter target database information
4. **Test Connection**: Verify target database is accessible
5. **Select Data**:
   - Check tables to export (Sites, US)
   - Select "Export Relationships" to generate rapporti field
   - Filter sites if needed
6. **Start Export**: Click "Export" button
7. **Monitor Progress**: View results in console

### 3. Web Interface

#### Access

1. Open PyArchInit-Mini web interface (default: `http://localhost:5000`)
2. Navigate to **Tools** → **PyArchInit Import/Export** from the main menu

#### Import via Web

1. **Select "Import" tab**
2. **Database Configuration**:
   - Toggle between SQLite and PostgreSQL
   - Enter connection details
3. **Test Connection**:
   - Click "Test Connection"
   - View available sites count
   - Review sites list
4. **Import Options**:
   - Select tables to import using checkboxes
   - Enable "Import Relationships" for US data
   - Filter by specific sites using the site filter
5. **Execute Import**:
   - Click "Start Import"
   - Monitor progress via status messages
   - Review import statistics

#### Export via Web

1. **Select "Export" tab**
2. **Configure Target Database**
3. **Select Export Options**:
   - Choose tables (Sites, US)
   - Enable relationship export
   - Apply site filters
4. **Execute Export**:
   - Click "Start Export"
   - Review export results

## Technical Details

### Field Mapping

The service automatically maps fields between PyArchInit and PyArchInit-Mini schemas:

**US Table Mapping** (50+ fields):
- Core stratigraphic data (descrizione, interpretazione, etc.)
- Chronological periods (periodo_iniziale, fase_iniziale, etc.)
- Physical characteristics (colore, consistenza, struttura, etc.)
- Excavation metadata (schedatore, data_schedatura, etc.)
- Measurements (quota, lunghezza, profondita, etc.)

### Relationship Parsing

**PyArchInit Format**:
```python
rapporti = "[['Copre', '2', '1', 'Pompei'], ['Taglia', '5', '1', 'Pompei']]"
```

**Extracted Data**:
- Relationship type: "Copre", "Taglia"
- Target US number: "2", "5"
- Area and site ignored (redundant in PyArchInit-Mini's relational model)

**PyArchInit-Mini Storage**:
```sql
INSERT INTO us_relationships_table
  (sito, us_from, us_to, relationship_type)
VALUES
  ('Pompei', 1, 2, 'Copre'),
  ('Pompei', 1, 5, 'Taglia');
```

### Date Handling

Date fields (`data_schedatura`) are automatically converted:
- String dates (YYYY-MM-DD, DD/MM/YYYY, etc.) → Python date objects
- Handles various common date formats
- Invalid dates are set to NULL

### Auto-increment ID Generation

PyArchInit-Mini uses VARCHAR primary keys (`id_us`) with sequential numbers:
- Automatically generates next available ID during import
- Queries MAX(id_us) and increments
- Ensures no conflicts with existing records

### Error Handling

- **Per-record error handling**: Failed records don't stop the entire import
- **Error reporting**: Detailed error messages with site/US identification
- **Transaction safety**: Each record is committed individually to prevent data loss
- **Statistics tracking**: Import/update/error counts for all operations

## Examples

### Example 1: Migrate Complete Site

Import all data from a PyArchInit SQLite database for a specific site:

```bash
pyarchinit-mini-import import-from-pyarchinit \
  --source-db "sqlite:////Users/archaeologist/pyarchinit/db.sqlite" \
  --tables all \
  --sites "Scavo 2024 - Area A" \
  --import-relationships
```

Result:
```
✓ Sites imported: 1
✓ US imported: 150
✓ Relationships created: 487
✓ Inventario imported: 320
✓ Periodizzazione imported: 12
```

### Example 2: Export to PyArchInit for Collaboration

Export PyArchInit-Mini data to a PostgreSQL database for team collaboration:

```bash
pyarchinit-mini-import export-to-pyarchinit \
  --target-db "postgresql://team:password@server.example.com:5432/pyarchinit" \
  --tables sites \
  --tables us \
  --sites "Project Alpha" \
  --export-relationships
```

### Example 3: Desktop GUI Import Workflow

1. Open PyArchInit Import/Export dialog
2. Select SQLite database: `/path/to/pyarchinit_db.sqlite`
3. Click "Test Connection" → Shows 3 sites available
4. Select all tables for import
5. Filter sites: Select "Scavo 2023"
6. Click "Import"
7. Console shows:
   ```
   [INFO] Importing sites...
   [INFO] Sites: 1 imported, 0 updated
   [INFO] Importing US...
   [INFO] US: 85 imported, 0 updated
   [INFO] Relationships: 234 created
   [SUCCESS] Import completed!
   ```

## Troubleshooting

### Connection Issues

**Error**: "Database file not found"
- **Solution**: Verify absolute path to SQLite database file
- Use forward slashes even on Windows: `C:/Users/user/db.sqlite`

**Error**: "Failed to connect to PostgreSQL"
- **Solution**: Check credentials, host, and port
- Verify PostgreSQL is running and accessible
- Check firewall settings

### Import Errors

**Error**: "NOT NULL constraint failed"
- **Solution**: Source data may have missing required fields
- Check PyArchInit data quality
- Review error logs for specific fields

**Error**: "Date parsing failed"
- **Solution**: Invalid date format in source data
- Dates will be set to NULL
- Import continues with other fields

### Relationship Issues

**Error**: "Referenced US not found"
- **Solution**: Import US records before relationships
- Use `--import-relationships` flag
- Ensure target US records exist

## Performance

### Typical Import Times

- **100 US records**: ~5-10 seconds
- **1000 US records**: ~30-60 seconds
- **Large datasets (10,000+ records)**: 5-10 minutes

### Optimization Tips

1. **Use site filtering**: Import only needed sites
2. **Batch operations**: Import multiple tables in one operation
3. **PostgreSQL**: Faster than SQLite for large datasets
4. **Network**: Use local databases when possible

## API Reference

### ImportExportService Class

```python
from pyarchinit_mini.services.import_export_service import ImportExportService

# Initialize
service = ImportExportService(
    mini_db_connection="sqlite:///./pyarchinit_mini.db",
    source_db_connection="sqlite:////path/to/pyarchinit_db.sqlite"
)

# Import sites
stats = service.import_sites(sito_filter=['Pompei'])
# Returns: {'imported': 1, 'updated': 0, 'skipped': 0, 'errors': []}

# Import US with relationships
stats = service.import_us(
    sito_filter=['Pompei'],
    import_relationships=True
)
# Returns: {
#     'imported': 50,
#     'updated': 0,
#     'relationships_created': 187,
#     'errors': []
# }

# Export to PyArchInit
stats = service.export_us(
    target_db_connection="sqlite:////path/to/target.sqlite",
    sito_filter=['Pompei'],
    export_relationships=True
)
```

### Available Methods

- `import_sites(sito_filter)` - Import site data
- `import_us(sito_filter, import_relationships)` - Import stratigraphic units
- `import_inventario(sito_filter)` - Import artifacts
- `import_periodizzazione(sito_filter)` - Import periods
- `import_thesaurus()` - Import terminology
- `export_sites(target_db, sito_filter)` - Export sites
- `export_us(target_db, sito_filter, export_relationships)` - Export US
- `get_available_sites_in_source()` - List source database sites
- `validate_database_connection(connection_string)` - Test connection

## Version History

### v1.2.17 (Current)
- ✅ Full bidirectional import/export for Sites and US
- ✅ Intelligent relationship mapping (rapporti ↔ us_relationships_table)
- ✅ Support for Inventario, Periodizzazione, and Thesaurus
- ✅ CLI, Desktop GUI, and Web interface implementations
- ✅ SQLite and PostgreSQL support
- ✅ Site filtering and selective import/export
- ✅ Automatic date conversion and ID generation
- ✅ Comprehensive error handling and reporting

## Support

For issues, questions, or feature requests:
- GitHub: https://github.com/[your-repo]/pyarchinit-mini
- Email: support@pyarchinit-mini.org
- Documentation: https://docs.pyarchinit-mini.org

## License

PyArchInit-Mini is released under the MIT License. See LICENSE file for details.
