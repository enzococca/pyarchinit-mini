"""
Database migration: Change us and area columns to TEXT type (Simple version)

This migration changes:
- us_table.us: INTEGER → VARCHAR(100)
- us_table.area: VARCHAR(20) → TEXT

Uses actual existing schema, not the full model.

Date: 2025-10-23
Version: 1.1 (Simple)
"""

from sqlalchemy import text


def upgrade_sqlite(connection):
    """
    Change column types for SQLite database

    Uses dynamic column detection to work with any schema version
    """

    print("[Migration] Changing us and area column types for SQLite...")

    # Step 1: Get existing columns
    print("[Migration] Detecting existing columns...")
    result = connection.execute(text("PRAGMA table_info(us_table)"))
    columns = [row[1] for row in result]
    column_list = ', '.join(columns)

    print(f"[Migration] Found {len(columns)} columns")

    # Step 2: Create new table (minimal schema with our changes)
    print("[Migration] Creating new us_table with updated schema...")

    # Build CREATE TABLE dynamically
    result = connection.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='us_table'"))
    create_sql = result.fetchone()[0]

    # Modify the CREATE TABLE statement
    create_sql_new = create_sql.replace('CREATE TABLE us_table', 'CREATE TABLE us_table_new')
    create_sql_new = create_sql_new.replace('area VARCHAR(20)', 'area TEXT')
    create_sql_new = create_sql_new.replace('us INTEGER', 'us VARCHAR(100)')

    connection.execute(text(create_sql_new))

    # Step 3: Copy data (cast us to VARCHAR)
    print("[Migration] Copying data from old table...")

    # Build column list for SELECT, casting us to VARCHAR
    select_columns = []
    for col in columns:
        if col == 'us':
            select_columns.append('CAST(us AS VARCHAR(100)) AS us')
        else:
            select_columns.append(col)

    select_list = ', '.join(select_columns)

    copy_sql = f"""
        INSERT INTO us_table_new ({column_list})
        SELECT {select_list}
        FROM us_table
    """

    connection.execute(text(copy_sql))

    # Step 4: Drop old table
    print("[Migration] Dropping old table...")
    connection.execute(text("DROP TABLE us_table"))

    # Step 5: Rename new table
    print("[Migration] Renaming new table...")
    connection.execute(text("ALTER TABLE us_table_new RENAME TO us_table"))

    # Step 6: Recreate indexes (if they exist)
    print("[Migration] Recreating indexes...")
    try:
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_us_sito ON us_table(sito)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_us_us ON us_table(us)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_us_area ON us_table(area)"))
    except Exception as e:
        print(f"[Migration] Warning: Could not recreate some indexes: {e}")

    print("[Migration] us_table migration complete")


def upgrade_postgresql(connection):
    """
    Change column types for PostgreSQL database
    """

    print("[Migration] Changing us and area column types for PostgreSQL...")

    # Change us from INTEGER to VARCHAR(100)
    print("[Migration] Converting us column to VARCHAR(100)...")
    connection.execute(text("""
        ALTER TABLE us_table
        ALTER COLUMN us TYPE VARCHAR(100) USING us::VARCHAR(100)
    """))

    # Change area from VARCHAR(20) to TEXT
    print("[Migration] Converting area column to TEXT...")
    connection.execute(text("""
        ALTER TABLE us_table
        ALTER COLUMN area TYPE TEXT
    """))

    print("[Migration] us_table migration complete")


def downgrade_sqlite(connection):
    """
    Revert changes for SQLite

    WARNING: This may cause data loss if us contains non-numeric values!
    """

    print("[Migration] Reverting us and area column types for SQLite...")
    print("[Migration] WARNING: This will fail if us contains non-numeric values!")

    # Get existing columns
    result = connection.execute(text("PRAGMA table_info(us_table)"))
    columns = [row[1] for row in result]
    column_list = ', '.join(columns)

    # Create old table structure
    result = connection.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='us_table'"))
    create_sql = result.fetchone()[0]

    create_sql_old = create_sql.replace('CREATE TABLE us_table', 'CREATE TABLE us_table_old')
    create_sql_old = create_sql_old.replace('area TEXT', 'area VARCHAR(20)')
    create_sql_old = create_sql_old.replace('us VARCHAR(100)', 'us INTEGER')

    connection.execute(text(create_sql_old))

    # Copy data (try to cast us to INTEGER)
    select_columns = []
    for col in columns:
        if col == 'us':
            select_columns.append('CAST(us AS INTEGER) AS us')
        else:
            select_columns.append(col)

    select_list = ', '.join(select_columns)

    copy_sql = f"""
        INSERT INTO us_table_old ({column_list})
        SELECT {select_list}
        FROM us_table
    """

    connection.execute(text(copy_sql))

    # Drop new table and rename old
    connection.execute(text("DROP TABLE us_table"))
    connection.execute(text("ALTER TABLE us_table_old RENAME TO us_table"))

    # Recreate indexes
    try:
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_us_sito ON us_table(sito)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_us_us ON us_table(us)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_us_area ON us_table(area)"))
    except Exception:
        pass

    print("[Migration] us_table downgrade complete")


def downgrade_postgresql(connection):
    """
    Revert changes for PostgreSQL

    WARNING: This may cause data loss if us contains non-numeric values!
    """

    print("[Migration] Reverting us and area column types for PostgreSQL...")

    # Revert us to INTEGER (may fail if data is not numeric)
    print("[Migration] Converting us column back to INTEGER...")
    try:
        connection.execute(text("""
            ALTER TABLE us_table
            ALTER COLUMN us TYPE INTEGER USING us::INTEGER
        """))
    except Exception as e:
        print(f"[Migration] ERROR: Cannot convert us to INTEGER: {e}")
        raise

    # Revert area to VARCHAR(20)
    print("[Migration] Converting area column back to VARCHAR(20)...")
    connection.execute(text("""
        ALTER TABLE us_table
        ALTER COLUMN area TYPE VARCHAR(20)
    """))

    print("[Migration] us_table downgrade complete")


def upgrade(connection, db_type='sqlite'):
    """
    Main upgrade function

    Args:
        connection: SQLAlchemy connection
        db_type: 'sqlite' or 'postgresql'
    """
    if db_type.lower() == 'sqlite':
        upgrade_sqlite(connection)
    elif db_type.lower() in ('postgresql', 'postgres'):
        upgrade_postgresql(connection)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def downgrade(connection, db_type='sqlite'):
    """
    Main downgrade function

    Args:
        connection: SQLAlchemy connection
        db_type: 'sqlite' or 'postgresql'
    """
    if db_type.lower() == 'sqlite':
        downgrade_sqlite(connection)
    elif db_type.lower() in ('postgresql', 'postgres'):
        downgrade_postgresql(connection)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
