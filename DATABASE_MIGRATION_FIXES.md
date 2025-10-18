# Database Migration Fixes

## Problem Solved

The application was experiencing `sqlite3.OperationalError` when trying to access columns that didn't exist in existing databases:

```
sqlite3.OperationalError: no such column: inventario_materiali_table.schedatore
```

This occurred because the existing database schema was missing new columns that were added to the model definitions.

## Solution Implemented

### 1. Enhanced Database Migrations

Updated `pyarchinit_mini/database/migrations.py` to automatically detect and add missing columns:

```python
def migrate_inventario_materiali_table(self):
    """Migrate inventario_materiali_table to include all new fields"""
    new_columns = [
        ('schedatore', 'TEXT'),
        ('date_scheda', 'TEXT'),
        ('punto_rinv', 'TEXT'),
        ('negativo_photo', 'TEXT'),
        ('diapositiva', 'TEXT')
    ]
    
    for column_name, column_type in new_columns:
        self.add_column_if_not_exists('inventario_materiali_table', column_name, column_type)
```

### 2. Updated Database Initialization

Modified `pyarchinit_mini/database/connection.py` to run migrations automatically:

```python
def initialize_database(self):
    """Initialize database and create tables with migrations"""
    try:
        # Create all tables
        self.create_tables()
        
        # Run migrations to add any missing columns
        from ..database.migrations import DatabaseMigrations
        from ..database.manager import DatabaseManager
        
        db_manager = DatabaseManager(self)
        migrations = DatabaseMigrations(db_manager)
        migrations_applied = migrations.migrate_all_tables()
        
        if migrations_applied > 0:
            logger.info(f"Applied {migrations_applied} database migrations")
```

### 3. Updated API Dependencies

Modified `pyarchinit_mini/api/dependencies.py` to use the new initialization method:

```python
def init_database(database_url: str):
    """Initialize global database connection"""
    global _db_connection
    _db_connection = DatabaseConnection.from_url(database_url)
    
    # Initialize database with migrations
    _db_connection.initialize_database()
```

## New Columns Added

The following columns were added to `inventario_materiali_table`:

- `schedatore` (TEXT) - Who catalogued the item
- `date_scheda` (TEXT) - Date of cataloguing  
- `punto_rinv` (TEXT) - Find point/location
- `negativo_photo` (TEXT) - Photo negative reference
- `diapositiva` (TEXT) - Slide reference

## Benefits

1. **Backward Compatibility**: Existing databases are automatically updated without data loss
2. **Forward Compatibility**: New features can add columns safely
3. **Error Prevention**: No more `OperationalError` when accessing new fields
4. **Data Integrity**: All existing data is preserved during migrations

## Testing

The fix has been verified by:

1. Running the desktop GUI successfully without errors
2. Confirming database initialization with migrations
3. Testing all interfaces (API, Web, Desktop, CLI)

## Usage

No manual intervention required. When starting any PyArchInit-Mini interface, migrations are applied automatically if needed.