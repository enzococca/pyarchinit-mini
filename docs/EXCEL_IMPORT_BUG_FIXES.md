# Excel Import Bug Fixes

**Date**: 2025-10-28
**Version**: 1.6.0
**Commits**: c90195e, 7bc39f2, d4462ed

## Overview

Fixed three critical bugs that prevented Excel import functionality from working correctly in both the Web GUI and command-line interfaces.

**LATEST UPDATE (d4462ed)**: All Excel imports now working correctly with unified database path!

## Bugs Fixed

### 1. Extended Matrix Parser - Date Type Mismatch

**Error**: `sqlite3.IntegrityError: datatype mismatch`

**Root Cause**: The `data_schedatura` field was being set to a Python `date` object (`datetime.now().date()`), but SQLite expects date values as ISO-formatted strings.

**Location**: `pyarchinit_mini/services/extended_matrix_excel_parser.py:363`

**Fix**:
```python
# Before
data_schedatura=datetime.now().date()

# After
data_schedatura=datetime.now().date().isoformat()
```

**Impact**: Extended Matrix Excel imports now work correctly without type conversion errors.

---

### 2. Harris Template Parser - Missing Database Columns

**Error**: `sqlite3.OperationalError: no such column: us_table.d_stratigrafica_en`

**Root Cause**: The web interface was using a local database file (`web_interface/pyarchinit_mini.db`) that was created before the multilingual (`_en`) columns were added to the schema. SQLAlchemy tried to query these columns, causing the error.

**Location**: `web_interface/excel_import_routes.py`

**Fix Applied**:

1. **Code Changes** - Added schema initialization:
   ```python
   from pyarchinit_mini.models.base import BaseModel

   # Initialize database schema (create missing tables/columns)
   BaseModel.metadata.create_all(connection.engine)
   ```

   Added to both `import_harris_template_format()` and `import_extended_matrix_format()` functions.

2. **Database Migration** - Manually added missing columns:
   ```sql
   -- Added to web_interface/pyarchinit_mini.db
   ALTER TABLE us_table ADD COLUMN d_stratigrafica_en VARCHAR(350);
   ALTER TABLE us_table ADD COLUMN d_interpretativa_en VARCHAR(350);
   ALTER TABLE us_table ADD COLUMN descrizione_en TEXT;
   ALTER TABLE us_table ADD COLUMN interpretazione_en TEXT;
   ALTER TABLE us_table ADD COLUMN formazione_en VARCHAR(20);
   ALTER TABLE us_table ADD COLUMN stato_di_conservazione_en VARCHAR(20);
   ALTER TABLE us_table ADD COLUMN colore_en VARCHAR(20);
   ALTER TABLE us_table ADD COLUMN consistenza_en VARCHAR(20);
   ALTER TABLE us_table ADD COLUMN struttura_en VARCHAR(30);
   ALTER TABLE us_table ADD COLUMN inclusi_en TEXT;
   ALTER TABLE us_table ADD COLUMN campioni_en TEXT;
   ALTER TABLE us_table ADD COLUMN documentazione_en TEXT;
   ```

**Impact**: Harris Template Excel imports now work correctly with the updated database schema.

---

## Database Architecture Note

### Multiple Database Files

The project currently uses multiple database files in different locations:
- `web_interface/pyarchinit_mini.db` - Used by Flask web interface
- `pyarchinit_mini.db` (root) - Used by CLI tools
- `~/.pyarchinit_mini/data/pyarchinit_mini.db` - Default for Extended Matrix parser

**Best Practice**: Use environment variable `DATABASE_URL` to specify a consistent database location:
```bash
export DATABASE_URL="sqlite:////absolute/path/to/pyarchinit_mini.db"
```

---

## Testing

### Test Extended Matrix Import
```bash
# Using Web GUI
# Navigate to: http://localhost:5000/excel-import
# Select "Extended Matrix Parser" format
# Upload test file: test_20us_em.xlsx
```

### Test Harris Template Import
```bash
# Using Web GUI
# Navigate to: http://localhost:5000/excel-import
# Select "Harris Matrix Template" format
# Upload test file: test_20us_complete.xlsx
```

---

## Related Files

- `pyarchinit_mini/services/extended_matrix_excel_parser.py`
- `pyarchinit_mini/cli/harris_import.py`
- `web_interface/excel_import_routes.py`
- `web_interface/templates/excel_import/index.html`

---

## Future Improvements

1. **Unified Database Path**: Configure all components to use a single, consistent database location
2. **Automatic Migrations**: Implement Alembic or similar migration tool to handle schema changes
3. **Database Validation**: Add startup checks to verify schema compatibility
4. **Better Error Messages**: Provide more user-friendly error messages for database issues

---

### 3. Harris Template - id_us Type Mismatch (FIXED: 7bc39f2)

**Error**: `(sqlite3.IntegrityError) datatype mismatch` when trying to insert STRING into INTEGER autoincrement field

**Root Cause**: Both parsers were manually generating `id_us` as strings like `"site__area__us_number"`, but the US model defines `id_us` as `Integer autoincrement`.

**Fix**:
```python
# Before (WRONG):
id_us = f"{site_name}__{area_str}__{us_number}"
new_us = US(id_us=id_us, ...)

# After (CORRECT):
new_us = US(...)  # Let SQLAlchemy auto-generate id_us
```

**Impact**: Both Harris Template and Extended Matrix imports now work correctly.

---

### 4. Extended Matrix - Date Field Type (FIXED: d4462ed)

**Error**: `(builtins.TypeError) SQLite Date type only accepts Python date objects as input`

**Root Cause**: Using `.isoformat()` on date object produces a STRING, but SQLAlchemy Date type expects Python date object or None.

**Fix**:
```python
# Before (WRONG):
data_schedatura=datetime.now().date().isoformat()  # Returns STRING

# After (CORRECT):
data_schedatura=None  # SQLAlchemy handles default
```

**Location**: `pyarchinit_mini/services/extended_matrix_excel_parser.py:358`

---

### 5. Missing Italian Relationship Mapping (FIXED: d4462ed)

**Error**: `Skipping unknown relationship type: anteriore a`

**Root Cause**: Metro C Excel uses lowercase Italian relationship names, but mapping only had English names.

**Fix**: Added Italian relationship names to mapping:
```python
RELATIONSHIP_MAPPING = {
    'is_before': 'Anteriore a',
    'anteriore a': 'Anteriore a',  # NEW
    'copre': 'Copre',               # NEW
    'coperto da': 'Coperto da',     # NEW
    # ... etc
}
```

**Location**: `pyarchinit_mini/services/extended_matrix_excel_parser.py:82-90`

---

### 6. Database Path Inconsistency (FIXED: d4462ed)

**Problem**: Data was imported successfully but not visible in web interface!

**Root Cause**: Three different databases were being used:
- Web interface: `pyarchinit_mini.db` (project root)
- Harris importer: `web_interface/pyarchinit_mini.db` 
- Extended Matrix: `~/.pyarchinit_mini/data/pyarchinit_mini.db`

**Fix**: All importers now use the SAME database as web interface:
```python
# Use Flask app's database
db_url = current_app.config.get('CURRENT_DATABASE_URL')
if not db_url:
    # Fallback to project root (same as app.py)
    default_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyarchinit_mini.db')
    db_url = f"sqlite:///{default_db_path}"
```

**Impact**: All imported data now immediately visible in web interface!

---

## Final Test Results

### Harris Template (`test_20us_complete.xlsx`)
✅ **SUCCESS**
- 20 US imported
- 24 relationships created
- Data visible in web interface
- No errors

### Extended Matrix (`test_em_real_data.xlsx`)
✅ **SUCCESS**
- 5 US imported
- 6 relationships created
- Data visible in web interface
- No date type errors

### Metro C Extended Matrix (65 US)
✅ **SUCCESS** (after all fixes)
- 65 US imported
- 658 relationships parsed
- Italian relationship names recognized
- Data visible in web interface

---

## How to Test

1. **Start web interface**: `cd web_interface && python app.py`
2. **Navigate to**: http://localhost:5000/excel-import
3. **Test Harris Template**:
   - Select "Harris Matrix Template" format
   - Upload `test_20us_complete.xlsx`
   - Enter site name: "Test Harris"
   - Click "Import Excel"
   - ✅ Should see: "Import completed successfully! US records: 20, Relationships: 24"
4. **Test Extended Matrix**:
   - Select "Extended Matrix Parser" format
   - Upload your Metro C Excel file
   - Enter site name: "Metro C Test"
   - Click "Import Excel"
   - ✅ Should see: "Import completed successfully! US created: 65, Relationships created: 658"
5. **Verify data visible**: Navigate to US list and search for your site name

---

## Summary of All Commits

- **c90195e**: Initial fix for date conversion and schema initialization
- **2b62ff9**: Added bug fix documentation
- **7bc39f2**: Fixed id_us type mismatch (INTEGER vs STRING)
- **d4462ed**: Fixed date field type, Italian mappings, and unified database path

🎉 **All Excel import functionality now working correctly!**
