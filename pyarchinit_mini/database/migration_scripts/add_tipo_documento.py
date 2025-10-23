"""
Database migration: Add tipo_documento field to US table

This migration adds:
- us_table.tipo_documento: VARCHAR(100) - Document type for DOC units

Date: 2025-10-23
Version: 1.0
"""

from sqlalchemy import text


def upgrade_sqlite(connection):
    """
    Add tipo_documento column for SQLite database
    """

    print("[Migration] Adding tipo_documento column to us_table for SQLite...")

    try:
        # Add new column
        connection.execute(text("""
            ALTER TABLE us_table ADD COLUMN tipo_documento VARCHAR(100)
        """))

        print("[Migration] tipo_documento column added successfully")

    except Exception as e:
        print(f"[Migration] Error: {e}")
        raise


def upgrade_postgresql(connection):
    """
    Add tipo_documento column for PostgreSQL database
    """

    print("[Migration] Adding tipo_documento column to us_table for PostgreSQL...")

    try:
        # Add new column
        connection.execute(text("""
            ALTER TABLE us_table ADD COLUMN tipo_documento VARCHAR(100)
        """))

        print("[Migration] tipo_documento column added successfully")

    except Exception as e:
        print(f"[Migration] Error: {e}")
        raise


def downgrade_sqlite(connection):
    """
    Remove tipo_documento column for SQLite

    Note: SQLite requires table recreation to drop columns
    """

    print("[Migration] Removing tipo_documento column from us_table for SQLite...")
    print("[Migration] WARNING: This requires table recreation in SQLite!")

    try:
        # Get existing columns
        result = connection.execute(text("PRAGMA table_info(us_table)"))
        columns = [row[1] for row in result if row[1] != 'tipo_documento']
        column_list = ', '.join(columns)

        # Get CREATE TABLE statement
        result = connection.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='us_table'"))
        create_sql = result.fetchone()[0]

        # Remove tipo_documento from CREATE TABLE
        # This is a simple approach that works if tipo_documento is defined simply
        create_sql_new = create_sql.replace('CREATE TABLE us_table', 'CREATE TABLE us_table_temp')
        # Remove the tipo_documento line (adjust this if your schema has different formatting)
        lines = create_sql_new.split('\n')
        filtered_lines = [line for line in lines if 'tipo_documento' not in line.lower()]
        create_sql_new = '\n'.join(filtered_lines)

        # Create temp table without tipo_documento
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

        print("[Migration] tipo_documento column removed successfully")

    except Exception as e:
        print(f"[Migration] Error: {e}")
        raise


def downgrade_postgresql(connection):
    """
    Remove tipo_documento column for PostgreSQL
    """

    print("[Migration] Removing tipo_documento column from us_table for PostgreSQL...")

    try:
        connection.execute(text("""
            ALTER TABLE us_table DROP COLUMN tipo_documento
        """))

        print("[Migration] tipo_documento column removed successfully")

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
