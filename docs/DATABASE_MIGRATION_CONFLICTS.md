# Database Migration Conflict Resolution System

## Overview

PyArchInit-Mini now includes a comprehensive conflict resolution system for database migrations. This system automatically detects ID conflicts between source and target databases and provides three strategies to handle them.

## Features

### 1. Automatic Backup System

Before any migration, the system can automatically create a backup of the source database:

- **SQLite**: Creates a timestamped file copy
- **PostgreSQL**: Uses `pg_dump` to create SQL backup

Backups are named with timestamp: `database_name.backup_YYYYMMDD_HHMMSS`

### 2. Conflict Detection

The system analyzes both databases and identifies:

- **Conflicting IDs**: Records that exist in both databases with the same primary key
- **New Records**: Records that only exist in the source database
- **Total Counts**: Summary statistics per table

**Key Feature**: Automatic primary key detection - works with any table structure without hardcoded column names.

### 3. Merge Strategies

Three strategies are available to handle ID conflicts:

#### Skip Strategy (Default)
- **Behavior**: Skips records with conflicting IDs
- **Use Case**: When target database data should be preserved
- **Result**: Only new records from source are added

#### Overwrite Strategy
- **Behavior**: Updates existing records with source data
- **Use Case**: When source data is more up-to-date
- **Result**: Conflicting records are replaced with source data

#### Renumber Strategy
- **Behavior**: Generates new sequential IDs for conflicting records
- **Use Case**: When you want to keep both versions of conflicting records
- **Result**: All source data is imported, conflicts get new IDs

## API Usage

### Preview Conflicts (Before Migration)

**Endpoint**: `POST /api/pyarchinit/preview-migration-conflicts`

**Request Body**:
```json
{
  "source_type": "current",
  "target_db_type": "sqlite",
  "target_db_path": "/path/to/target.db"
}
```

**Response**:
```json
{
  "success": true,
  "has_conflicts": true,
  "total_conflicts": 15,
  "total_new_records": 8,
  "tables": {
    "site_table": {
      "conflicts": 3,
      "new_records": 2,
      "conflicting_ids": [1, 2, 3],
      "total_source_records": 5
    },
    "us_table": {
      "conflicts": 7,
      "new_records": 3,
      "conflicting_ids": [1, 2, 3, 4, 5, 6, 7],
      "total_source_records": 10
    }
  },
  "errors": []
}
```

### Perform Migration

**Endpoint**: `POST /api/pyarchinit/migrate-database`

**Request Body**:
```json
{
  "source_type": "current",
  "target_db_type": "sqlite",
  "target_db_path": "/path/to/target.db",
  "merge_strategy": "skip",
  "auto_backup": true,
  "overwrite_target": false
}
```

**Parameters**:
- `merge_strategy`: `"skip"`, `"overwrite"`, or `"renumber"` (default: `"skip"`)
- `auto_backup`: `true` or `false` (default: `true`)
- `overwrite_target`: Whether to overwrite existing target database (default: `false`)

**Response**:
```json
{
  "success": true,
  "message": "Database migration completed successfully",
  "tables_migrated": 3,
  "total_rows_copied": 25,
  "rows_per_table": {
    "site_table": 5,
    "us_table": 15,
    "inventario_materiali_table": 5
  },
  "duration_seconds": 2.5,
  "backup_created": true,
  "backup_path": "/path/to/source.db.backup_20251031_182859",
  "backup_size_mb": 0.5,
  "errors": []
}
```

## Python Usage

### Example 1: Migration with Skip Strategy

```python
from pyarchinit_mini.services.import_export_service import ImportExportService

# Migrate with default skip strategy
result = ImportExportService.migrate_database(
    source_db_url="sqlite:///source.db",
    target_db_url="sqlite:///target.db",
    create_target=True,
    auto_backup=True,
    merge_strategy='skip'
)

print(f"Migrated {result['tables_migrated']} tables")
print(f"Copied {result['total_rows_copied']} rows")
if result['backup_created']:
    print(f"Backup created: {result['backup_path']}")
```

### Example 2: Preview Conflicts Before Migration

```python
# First, check for conflicts
conflicts = ImportExportService._detect_conflicts(
    source_db_url="sqlite:///source.db",
    target_db_url="sqlite:///target.db"
)

if conflicts['has_conflicts']:
    print(f"⚠️  Found {conflicts['total_conflicts']} conflicts")
    print(f"✓ Found {conflicts['total_new_records']} new records")

    # Show details per table
    for table_name, data in conflicts['tables'].items():
        if data['conflicts'] > 0:
            print(f"\n{table_name}:")
            print(f"  Conflicts: {data['conflicts']}")
            print(f"  Conflicting IDs: {data['conflicting_ids']}")
            print(f"  New records: {data['new_records']}")

    # Decide strategy based on conflicts
    strategy = 'overwrite' if conflicts['total_conflicts'] > 100 else 'skip'
else:
    print("✓ No conflicts found, safe to migrate")
    strategy = 'skip'

# Perform migration with chosen strategy
result = ImportExportService.migrate_database(
    source_db_url="sqlite:///source.db",
    target_db_url="sqlite:///target.db",
    merge_strategy=strategy
)
```

### Example 3: Migration with Renumber Strategy

```python
# Use renumber to keep all data from both databases
result = ImportExportService.migrate_database(
    source_db_url="sqlite:///source.db",
    target_db_url="sqlite:///target.db",
    merge_strategy='renumber',
    auto_backup=True
)

# Check renumbering results
for table_name, rows in result['rows_per_table'].items():
    print(f"{table_name}: {rows} rows processed")
```

## How It Works

### Conflict Detection Process

1. **Connect** to both source and target databases
2. **Inspect** each table's schema to find primary key column
3. **Query** all primary key values from both databases
4. **Compare** using set operations:
   - Conflicts = `source_ids ∩ target_ids` (intersection)
   - New records = `source_ids - target_ids` (difference)
5. **Return** detailed analysis per table

### Merge Strategy Implementation

#### Skip Strategy
```python
if record_id in existing_ids:
    # Skip this record
    continue
else:
    # Insert normally
    INSERT INTO table VALUES (...)
```

#### Overwrite Strategy
```python
if record_id in existing_ids:
    # Update existing record
    UPDATE table SET col1=val1, col2=val2 WHERE id=record_id
else:
    # Insert normally
    INSERT INTO table VALUES (...)
```

#### Renumber Strategy
```python
if record_id in existing_ids:
    # Generate new ID
    new_id = max_id + 1
    INSERT INTO table VALUES (new_id, other_values...)
else:
    # Insert with original ID
    INSERT INTO table VALUES (record_id, other_values...)
```

## Testing

The system includes comprehensive test coverage:

### Test Files

1. **test_backup_system.py**
   - SQLite backup creation
   - Custom backup directory
   - Migration with automatic backup

2. **test_conflict_detection.py**
   - No conflicts scenario (empty target)
   - Conflicts scenario (duplicate IDs)
   - Mixed scenario (some conflicts, some new)

3. **test_conflict_detection_simple.py**
   - Real database testing
   - Same database (all conflicts)
   - Empty target (all new)
   - Different databases (mixed)

4. **test_merge_strategies.py**
   - Skip strategy verification
   - Overwrite strategy verification
   - Renumber strategy verification

### Running Tests

```bash
# Run all tests
python3 test_backup_system.py
python3 test_conflict_detection.py
python3 test_conflict_detection_simple.py
python3 test_merge_strategies.py

# All tests should pass with 3/3 or similar
```

## Best Practices

### 1. Always Preview Conflicts First
```python
# Check conflicts before deciding strategy
conflicts = ImportExportService._detect_conflicts(source_url, target_url)
if conflicts['has_conflicts']:
    # Show user the conflicts and let them choose strategy
    print(f"Found {conflicts['total_conflicts']} conflicts")
```

### 2. Enable Automatic Backups
```python
# Always create backups for safety
result = ImportExportService.migrate_database(
    ...,
    auto_backup=True  # Default, but explicit is better
)
```

### 3. Choose Strategy Based on Context

- **Skip**: Default, safest option - preserves target data
- **Overwrite**: When source has latest/correct data
- **Renumber**: When you need complete history from both databases

### 4. Handle Errors Gracefully
```python
result = ImportExportService.migrate_database(...)

if not result['success']:
    print("Migration failed!")
    for error in result['errors']:
        print(f"  - {error}")
else:
    if result['errors']:
        print("Migration completed with warnings:")
        for error in result['errors']:
            print(f"  - {error}")
```

## Limitations

1. **Foreign Key Constraints**: Renumber strategy may break foreign key relationships
2. **Auto-increment Sequences**: PostgreSQL sequences are reset after migration
3. **Complex Primary Keys**: Only single-column primary keys are fully supported
4. **Large Databases**: Memory usage scales with number of IDs per table

## Future Enhancements

Possible future improvements:

- [ ] UI integration with conflict preview modal
- [ ] Progress tracking for long migrations
- [ ] Support for composite primary keys
- [ ] Selective table migration with per-table strategies
- [ ] Conflict resolution rules (custom logic per table)
- [ ] Dry-run mode (simulate migration without changes)

## Troubleshooting

### Issue: "No primary key found for table"

**Solution**: Some tables (like junction tables) may not have primary keys. The system skips these with a warning. This is normal behavior.

### Issue: Backup fails on PostgreSQL

**Solution**: Ensure `pg_dump` is installed and accessible:
```bash
which pg_dump
# Should return: /usr/bin/pg_dump or similar
```

### Issue: Renumber creates very large IDs

**Solution**: This is expected - renumbered IDs start from `max(existing_ids) + 1`. If this is a problem, consider using `overwrite` strategy instead.

### Issue: Migration is slow

**Solution**:
- Disable backup with `auto_backup=False` if not needed
- Use `skip` strategy (fastest) if possible
- Consider migrating tables selectively

## Version History

- **v1.8.6** (2025-10-31): Initial implementation
  - Automatic backup system
  - Conflict detection with auto PK detection
  - Three merge strategies (skip, overwrite, renumber)
  - Comprehensive test coverage
  - API endpoints for preview and migration

## See Also

- [Database Creator Documentation](./DATABASE_CREATOR.md)
- [Import/Export Service API](./IMPORT_EXPORT_API.md)
- [Migration Guide](./MIGRATION_GUIDE.md)
