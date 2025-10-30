# Database Schema Migration Guide

## Problem

When upgrading from older versions of PyArchInit-Mini (pre-1.6.0), you may encounter database schema compatibility errors:

```
sqlite3.OperationalError: no such column: us_table.tipo_documento
```

This error occurs because:
- **Version 1.6.0** added Extended Matrix Framework fields (`unita_tipo`, `tipo_documento`, `file_path`) to the US table
- **Version 1.7.0** added internationalization fields (`*_en` columns) to US and Site tables
- Existing databases created with earlier versions don't have these columns

## Solution: Database Migration Tool

PyArchInit-Mini includes a migration tool that automatically adds missing columns to your existing database without losing any data.

## Usage

### Option 1: CLI Command (Easiest)

After installing/upgrading pyarchinit-mini, run:

```bash
# Migrate the default database
pyarchinit-mini-migrate

# Migrate a specific database
pyarchinit-mini-migrate /path/to/your/database.db

# Migrate an uploaded database
pyarchinit-mini-migrate ~/.pyarchinit_mini/uploaded_databases/mydb.db
```

### Option 2: Python Script

```bash
python3 scripts/migrate_database_schema.py [database_path]
```

### Option 3: Python API

```python
from pyarchinit_mini.cli.migrate import main

# Migrate default database
main()

# Migrate specific database
main("/path/to/database.db")
```

## What Gets Migrated

The migration tool adds these columns if they're missing:

### US Table (Unità Stratigrafiche)

**Extended Matrix Fields (v1.6.0+):**
- `unita_tipo` VARCHAR(200) - Unit type (US, USM, DOC, etc.)
- `tipo_documento` VARCHAR(100) - Document type for DOC units
- `file_path` VARCHAR(500) - File path for DOC units

**Internationalization Fields (v1.7.0+):**
- `d_stratigrafica_en` VARCHAR(350)
- `d_interpretativa_en` VARCHAR(350)
- `descrizione_en` TEXT
- `interpretazione_en` TEXT
- `formazione_en` VARCHAR(20)
- `stato_di_conservazione_en` VARCHAR(20)
- `colore_en` VARCHAR(20)
- `consistenza_en` VARCHAR(20)
- `struttura_en` VARCHAR(30)
- `inclusi_en` TEXT
- `campioni_en` TEXT
- `documentazione_en` TEXT
- `osservazioni_en` TEXT

### Site Table

**Internationalization Fields (v1.7.0+):**
- `definizione_sito_en` VARCHAR(250)
- `descrizione_en` TEXT

## Migration Process

1. **Detection**: The tool checks if each column exists
2. **Addition**: Missing columns are added with NULL default values
3. **Preservation**: All existing data is preserved
4. **Verification**: The tool reports which columns were added

## Example Output

```
======================================================================
PyArchInit-Mini Database Schema Migration
======================================================================

📂 Database: /Users/enzo/.pyarchinit_mini/data/pyarchinit_mini.db

🔍 Checking us_table schema...
  ✓ Column already exists: unita_tipo
  ➕ Adding column: tipo_documento (VARCHAR(100))
  ➕ Adding column: file_path (VARCHAR(500))

🔍 Checking internationalization columns...
  ➕ Adding column: d_stratigrafica_en (VARCHAR(350))
  ➕ Adding column: d_interpretativa_en (VARCHAR(350))
  ...

✅ Migration completed: 15 column(s) added

🔍 Checking site_table schema...
  ➕ Adding column: definizione_sito_en (VARCHAR(250))
  ➕ Adding column: descrizione_en (TEXT)
✅ Site table migration: 2 column(s) added

======================================================================
✅ Database migration completed successfully!
======================================================================

You can now run pyarchinit-mini-web without errors.
```

## When to Use

You should run the migration tool when:

1. **After upgrading** from version < 1.6.0 to 1.6.0+
2. **After upgrading** from version < 1.7.0 to 1.7.0+
3. **When importing** databases from older PyArchInit-Mini installations
4. **When seeing** "no such column" errors in the web interface

## Safety

- ✅ The migration is **non-destructive** - it only adds columns, never removes or modifies existing data
- ✅ All new columns are added with NULL default values
- ✅ The tool can be run multiple times safely - it skips columns that already exist
- ⚠️ Always backup your database before migration (recommended, though not required)

## Backup Your Database (Recommended)

```bash
# Backup default database
cp ~/.pyarchinit_mini/data/pyarchinit_mini.db ~/.pyarchinit_mini/data/pyarchinit_mini.db.backup

# Backup specific database
cp /path/to/your/database.db /path/to/your/database.db.backup
```

## Troubleshooting

### Error: "Database not found"
- Verify the database path is correct
- Check that the file exists: `ls -l /path/to/database.db`

### Error: "Database is locked"
- Close the web interface: `pkill -f pyarchinit_mini`
- Stop any running database connections
- Try the migration again

### Migration doesn't fix the error
- Verify you migrated the correct database
- Check which database the web interface is using (see DATABASE_URL or config)
- Run migration on the active database

## For Developers

The migration script is located at:
- Package: `pyarchinit_mini/cli/migrate.py`
- Standalone: `scripts/migrate_database_schema.py`

To add new migrations in future versions:
1. Edit `pyarchinit_mini/cli/migrate.py`
2. Add new column definitions to `migrations` or `i18n_migrations` lists
3. Update this documentation with the new columns

## Version Compatibility

| PyArchInit-Mini Version | Schema Changes | Migration Required |
|------------------------|----------------|-------------------|
| < 1.6.0 | Original schema | No |
| 1.6.0 | Extended Matrix fields | Yes (if upgrading from < 1.6.0) |
| 1.7.0 | Internationalization fields | Yes (if upgrading from < 1.7.0) |
| 1.7.1+ | Database creation features | Use `pyarchinit-mini-migrate` |

## Support

If you encounter issues with database migration:

1. Check the [GitHub Issues](https://github.com/enzococca/pyarchinit-mini/issues)
2. Create a new issue with:
   - PyArchInit-Mini version (`pip show pyarchinit-mini`)
   - Migration error message
   - Database schema info: `sqlite3 database.db "PRAGMA table_info(us_table)"`
3. Email: enzococca@gmail.com

---

*Last updated: October 2025 (v1.7.0)*
