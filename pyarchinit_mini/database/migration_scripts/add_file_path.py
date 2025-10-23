"""
Database migration: Add file_path field to US table

This migration adds:
- us_table.file_path: VARCHAR(500) - File path for DOC units

Date: 2025-10-23
Version: 1.0
"""

from sqlalchemy import text


def upgrade_sqlite(connection):
    """
    Add file_path column for SQLite database
    """

    print("[Migration] Adding file_path column to us_table for SQLite...")

    try:
        # Add new column
        connection.execute(text("""
            ALTER TABLE us_table ADD COLUMN file_path VARCHAR(500)
        """))

        print("[Migration] file_path column added successfully")

    except Exception as e:
        print(f"[Migration] Error: {e}")
        raise


def upgrade_postgresql(connection):
    """
    Add file_path column for PostgreSQL database
    """

    print("[Migration] Adding file_path column to us_table for PostgreSQL...")

    try:
        # Add new column
        connection.execute(text("""
            ALTER TABLE us_table ADD COLUMN file_path VARCHAR(500)
        """))

        print("[Migration] file_path column added successfully")

    except Exception as e:
        print(f"[Migration] Error: {e}")
        raise


def downgrade_sqlite(connection):
    """
    Remove file_path column for SQLite

    Note: SQLite requires table recreation to drop columns
    """

    print("[Migration] Removing file_path column from us_table for SQLite...")
    print("[Migration] WARNING: This requires table recreation in SQLite!")

    try:
        # Get existing columns
        result = connection.execute(text("PRAGMA table_info(us_table)"))
        columns = [row[1] for row in result if row[1] != 'file_path']
        column_list = ', '.join(columns)

        # Get CREATE TABLE statement
        result = connection.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='us_table'"))
        create_sql = result.fetchone()[0]

        # Remove file_path from CREATE TABLE
        create_sql_new = create_sql.replace('CREATE TABLE us_table', 'CREATE TABLE us_table_temp')
        lines = create_sql_new.split('\n')
        filtered_lines = [line for line in lines if 'file_path' not in line.lower()]
        create_sql_new = '\n'.join(filtered_lines)

        # Create temp table without file_path
        connection.execute(text(create_sql_new))

        # Copy data
        copy_sql = f"""
            INSERT INTO us_table_temp ({column_list})
            SELECT {column_list}
            FROM us_table
        """
        connection.execute(text(copy_sql))

        # Drop old table
        connection.execute(text("DROP TABLE us_table"))

        # Rename temp table
        connection.execute(text("ALTER TABLE us_table_temp RENAME TO us_table"))

        print("[Migration] file_path column removed successfully")

    except Exception as e:
        print(f"[Migration] Error: {e}")
        raise


def downgrade_postgresql(connection):
    """
    Remove file_path column for PostgreSQL
    """

    print("[Migration] Removing file_path column from us_table for PostgreSQL...")

    try:
        connection.execute(text("""
            ALTER TABLE us_table DROP COLUMN file_path
        """))

        print("[Migration] file_path column removed successfully")

    except Exception as e:
        print(f"[Migration] Error: {e}")
        raise


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
