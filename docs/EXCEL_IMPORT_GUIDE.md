# Excel Import Guide

**Version**: 1.6.0
**Date**: 2025-10-28
**Status**: Complete and Working

## Overview

PyArchInit-Mini supports importing stratigraphic data from Excel files in **two different formats**:

1. **Harris Matrix Template** - Sheet-based format with separate NODES and RELATIONSHIPS sheets
2. **Extended Matrix Parser** - Inline format with relationships in columns

Both formats are supported in **all three interfaces**: Web GUI, Desktop GUI, and CLI.

---

## Excel Formats

### 1. Harris Matrix Template Format

**Structure**: Multiple sheets in one Excel file

**Required Sheets**:
- `INSTRUCTIONS` - Usage instructions (optional)
- `NODES` - Stratigraphic units
- `RELATIONSHIPS` - Relationships between units

**NODES Sheet Columns**:
```
us_number       | US identifier (e.g., 1001, 1002)
unit_type       | Type: US, USM, USVA, USD, etc.
description     | Short description
area            | Archaeological area
period          | Archaeological period
phase           | Archaeological phase
file_path       | Path to 3D model file (optional)
```

**RELATIONSHIPS Sheet Columns**:
```
from_us         | Source US number
to_us           | Target US number
relationship    | Type: Anteriore a, Copre, Coperto da, etc.
notes           | Additional notes (optional)
```

**Example Template**: `test_20us_complete.xlsx`

---

### 2. Extended Matrix Parser Format

**Structure**: Single sheet with inline relationships

**Required Columns**:
```
ID                  | US identifier (e.g., 1001)
DEFINITION          | Short description
LONG_DESCRIPTION    | Detailed description
PHASE               | Archaeological phase
```

**Relationship Columns** (comma-separated US numbers):
```
is_before           | List of US this unit is before
covers              | List of US this unit covers
is_covered_by       | List of US covering this unit
cuts                | List of US this unit cuts
is_cut_by           | List of US cutting this unit
leans_on            | List of US this unit leans on
equals              | List of equivalent US
fills               | List of US this unit fills
```

**Optional Columns**:
```
NOTES               | Additional notes
```

**Example Files**: `test_em_real_data.xlsx`, Metro C excavation files

---

## Using Web GUI

### Access
1. Start web interface: `cd web_interface && python app.py`
2. Navigate to: http://localhost:5000
3. Go to: **Import/Export** → **Excel Import - Harris Matrix**

### Import Steps

1. **Select Excel Format**
   - Choose "Harris Matrix Template" or "Extended Matrix Parser"
   - Format info panel shows structure requirements

2. **Upload Excel File**
   - Click "Browse..." and select your Excel file
   - Supported: .xlsx, .xls, .csv

3. **Enter Site Name**
   - Required field
   - Example: "Scavi Metro C - Amba Aradam"

4. **Options**
   - ☑ Generate GraphML for visualization (optional)

5. **Import**
   - Click "Import Excel"
   - Wait for processing
   - View results with statistics

### Success Message Example
```
Import completed successfully!

US records: 20
Relationships: 24
```

### Generate Template
- Click "Download Template" to get Harris Matrix Template Excel file
- Includes example data and instructions

---

## Using Desktop GUI

### Access
1. Launch Desktop GUI: `python -m pyarchinit_mini`
2. Go to menu: **Tools** → **Import Excel - Harris Matrix**

### Import Dialog

**Format Selection**:
- Radio buttons for Harris Template or Extended Matrix
- Real-time format information

**File Selection**:
- Browse button to select Excel file
- Path displayed in read-only field

**Site Name**:
- Required text field
- Enter archaeological site name

**Options**:
- Generate GraphML checkbox

**Actions**:
- **Import Excel** - Start import process
- **Download Template** - Save Harris Matrix Template
- **Close** - Close dialog

### Progress Tracking
- Progress bar shows import status
- Status label updates: "Importing..." → "Import completed successfully!"
- Success/error message boxes

---

## Using CLI

### Harris Matrix Template Import

```bash
python -m pyarchinit_mini.cli.harris_import \
    --file path/to/template.xlsx \
    --site "Site Name" \
    --graphml \
    --output output_dir/
```

**Parameters**:
- `--file` - Path to Excel file
- `--site` - Archaeological site name
- `--graphml` - Generate GraphML export
- `--output` - Output directory for GraphML

**Example**:
```bash
python -m pyarchinit_mini.cli.harris_import \
    --file test_20us_complete.xlsx \
    --site "Test Harris" \
    --graphml \
    --output exports/
```

---

### Extended Matrix Parser Import

```python
from pyarchinit_mini.services.extended_matrix_excel_parser import import_extended_matrix_excel

stats = import_extended_matrix_excel(
    excel_path='data/metro_c.xlsx',
    site_name='Metro C - Amba Aradam',
    generate_graphml=True
)

print(f"US created: {stats['us_created']}")
print(f"Relationships: {stats['relationships_created']}")
```

**Python API**:
```python
def import_extended_matrix_excel(
    excel_path: str,
    site_name: str,
    generate_graphml: bool = True,
    db_connection: Optional[DatabaseConnection] = None
) -> Dict
```

**Returns**:
```python
{
    'us_created': 65,
    'us_updated': 0,
    'relationships_created': 658,
    'graphml_path': 'site_name.graphml',
    'errors': []
}
```

---

## Relationship Types

### Supported Relationships

**Italian** (preferred):
- `Anteriore a` - Is before
- `Copre` - Covers
- `Coperto da` - Is covered by
- `Taglia` - Cuts
- `Tagliato da` - Is cut by
- `Si appoggia a` - Leans on
- `Uguale a` - Equals
- `Riempie` - Fills

**English** (also accepted):
- `is_before`, `covers`, `is_covered_by`, `cuts`, `is_cut_by`
- `leans_on`, `equals`, `fills`

### Case Insensitive
Both uppercase and lowercase are accepted:
- "anteriore a" ✅
- "Anteriore a" ✅
- "ANTERIORE A" ✅

---

## Node Types (Harris Template)

Supported unit types in Harris Matrix Template format:

| Type | Description |
|------|-------------|
| `US` | Stratigraphic Unit |
| `USM` | Masonry Unit |
| `USVA` | Archaeological Value Unit A |
| `USVB` | Archaeological Value Unit B |
| `USVC` | Archaeological Value Unit C |
| `TU` | Typological Unit |
| `USD` | Destruction Unit |
| `SF` | Stratigraphic Feature |
| `VSF` | Virtual Stratigraphic Feature |
| `CON` | Context |
| `DOC` | Document |
| `Extractor` | Data Extractor |
| `Combiner` | Data Combiner |
| `property` | Property Node |

---

## GraphML Export

### What is GraphML?

GraphML is an XML-based format for graphs that can be visualized in:
- **yEd Graph Editor** (recommended)
- **Gephi**
- **Cytoscape**
- Any GraphML-compatible tool

### When GraphML is Generated

If "Generate GraphML" option is enabled:
1. **Web GUI**: File available for download after import
2. **Desktop GUI**: Saved to default location
3. **CLI**: Saved to specified output directory

### GraphML Features

- **Nodes**: All stratigraphic units with labels
- **Edges**: All relationships with types
- **Metadata**: Site name, periods, phases
- **Labels**: US numbers and descriptions
- **Colors**: By node type (if configured)

### Opening in yEd

1. Download/locate GraphML file
2. Open yEd Graph Editor
3. File → Open → Select .graphml file
4. Apply layout: Layout → Hierarchical → Top to Bottom
5. Adjust and export to PNG/PDF

---

## Database Consistency

### Unified Database Path

All three interfaces (Web GUI, Desktop GUI, CLI) now use **consistent database paths**:

- **Web GUI**: Uses Flask app's `CURRENT_DATABASE_URL` config
- **Desktop GUI**: Uses passed `db_manager.connection`
- **CLI**: Uses default or `DATABASE_URL` environment variable

### Why This Matters

✅ **Before Fix**: Data imported in one interface was not visible in others
✅ **After Fix**: All imported data immediately visible in all interfaces

### Setting Custom Database

```bash
# Use environment variable for CLI
export DATABASE_URL="sqlite:////path/to/your/database.db"

# Or in Python
from pyarchinit_mini.database.connection import DatabaseConnection

connection = DatabaseConnection.from_url("sqlite:////path/to/db.db")
```

---

## Troubleshooting

### Error: "No file selected"
**Solution**: Click "Browse" and select an Excel file

---

### Error: "Site name is required"
**Solution**: Enter a site name in the text field

---

### Error: "Invalid file format"
**Solution**: Use .xlsx, .xls, or .csv file format

---

### Error: "no such column: us_table.d_stratigrafica_en"
**Solution**: Database schema is outdated
```bash
# Recreate database with correct schema
cd web_interface
rm pyarchinit_mini.db
python app.py  # Will create new database
```

---

### Error: "datatype mismatch"
**Solution**: This was fixed in v1.6.0. Update to latest version:
```bash
git pull origin main
```

---

### Error: "Skipping unknown relationship type"
**Solution**:
- Check spelling of relationship names
- Use supported relationship types (see above)
- Both Italian and English are accepted

---

### Import succeeds but data not visible
**Solution**: This was fixed in v1.6.0 (database path unification)
```bash
# Verify all interfaces use same database
# Check CURRENT_DATABASE_URL in web interface
# Update Desktop GUI to latest version
```

---

## Testing

### Test Files Included

1. **test_20us_complete.xlsx** - Harris Matrix Template format
   - 20 US records
   - 24 relationships
   - Example site: "Test Harris"

2. **test_em_real_data.xlsx** - Extended Matrix Parser format
   - 5 US records
   - 6 relationships
   - Example site: "Test EM"

### Test Procedure

```bash
# 1. Start web interface
cd web_interface && python app.py

# 2. Open browser to http://localhost:5000/excel-import

# 3. Test Harris Template
- Select "Harris Matrix Template" format
- Upload test_20us_complete.xlsx
- Site name: "Test Harris"
- Click "Import Excel"
- Expected: "Import completed successfully! US records: 20, Relationships: 24"

# 4. Test Extended Matrix
- Select "Extended Matrix Parser" format
- Upload test_em_real_data.xlsx
- Site name: "Test EM"
- Click "Import Excel"
- Expected: "Import completed successfully! US created: 5, Relationships created: 6"

# 5. Verify data visible
- Navigate to US list
- Search for "Test Harris" or "Test EM"
- Confirm records appear
```

---

## Version History

### v1.6.0 (2025-10-28)
✅ All Excel import functionality working correctly!

**Fixed**:
- Date type mismatch errors
- Missing Italian relationship mappings
- Database path inconsistency
- id_us type mismatch (INTEGER autoincrement)
- Missing multilingual columns
- KeyError on Extended Matrix columns

**Added**:
- Web GUI integration with dual format support
- Desktop GUI database consistency fix
- Complete documentation
- Test files and procedures

---

## Next Steps

1. ✅ Web GUI - Complete and tested
2. ✅ Desktop GUI - Complete with database fix
3. ✅ CLI - Working (both formats)
4. ✅ Documentation - Complete

**All interfaces ready for production use!**

---

## Support

For issues or questions:
1. Check this documentation
2. Review error messages carefully
3. Verify Excel file format matches selected type
4. Check database path configuration
5. Ensure v1.6.0 or later

**Documentation Last Updated**: 2025-10-28
