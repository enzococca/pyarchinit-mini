# Excel Import Bug Fixes

**Date**: 2025-10-28
**Version**: 1.6.0
**Commit**: c90195e

## Overview

Fixed two critical bugs that prevented Excel import functionality from working correctly in both the Web GUI and command-line interfaces.

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
