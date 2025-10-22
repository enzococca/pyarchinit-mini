"""
Database migration: Add i18n columns (_en) for translatable fields

This migration adds English translation columns to tables with descriptive fields.
It follows the pattern: original_field → original_field_it, adds original_field_en

Date: 2025-10-21
Version: 1.0
"""

from sqlalchemy import text


def upgrade_sqlite(connection):
    """
    Add _en columns for SQLite database

    SQLite limitations:
    - Cannot RENAME COLUMN directly (need to recreate table)
    - Cannot ADD multiple columns in one statement
    - We'll add _en columns only, keep original columns as-is for compatibility
    """

    print("[Migration] Adding i18n columns for SQLite...")

    # ========== SITE TABLE ==========
    print("[Migration] Migrating site_table...")

    # Add new columns for English translations
    connection.execute(text("""
        ALTER TABLE site_table ADD COLUMN definizione_sito_en VARCHAR(250)
    """))

    connection.execute(text("""
        ALTER TABLE site_table ADD COLUMN descrizione_en TEXT
    """))

    print("[Migration] site_table migration complete")

    # ========== US TABLE ==========
    print("[Migration] Migrating us_table...")

    # Add English columns for descriptive fields
    us_text_fields = [
        'descrizione_en',
        'interpretazione_en',
        'inclusi_en',
        'campioni_en',
        'documentazione_en',
        'osservazioni_en'
    ]

    for field in us_text_fields:
        connection.execute(text(f"""
            ALTER TABLE us_table ADD COLUMN {field} TEXT
        """))

    us_string_fields = [
        ('d_stratigrafica_en', 'VARCHAR(350)'),
        ('d_interpretativa_en', 'VARCHAR(350)'),
        ('formazione_en', 'VARCHAR(20)'),
        ('stato_di_conservazione_en', 'VARCHAR(20)'),
        ('colore_en', 'VARCHAR(20)'),
        ('consistenza_en', 'VARCHAR(20)'),
        ('struttura_en', 'VARCHAR(30)')
    ]

    for field, field_type in us_string_fields:
        connection.execute(text(f"""
            ALTER TABLE us_table ADD COLUMN {field} {field_type}
        """))

    print("[Migration] us_table migration complete")

    # ========== INVENTARIO_MATERIALI TABLE ==========
    print("[Migration] Migrating inventario_materiali_table...")

    # Add English columns for descriptive fields
    inv_text_fields = [
        'tipo_reperto_en',
        'criterio_schedatura_en',
        'definizione_en',
        'descrizione_en',
        'elementi_reperto_en'
    ]

    for field in inv_text_fields:
        connection.execute(text(f"""
            ALTER TABLE inventario_materiali_table ADD COLUMN {field} TEXT
        """))

    inv_string_fields = [
        ('stato_conservazione_en', 'VARCHAR(200)'),
        ('corpo_ceramico_en', 'VARCHAR(200)'),
        ('rivestimento_en', 'VARCHAR(200)'),
        ('tipo_contenitore_en', 'VARCHAR(200)')
    ]

    for field, field_type in inv_string_fields:
        connection.execute(text(f"""
            ALTER TABLE inventario_materiali_table ADD COLUMN {field} {field_type}
        """))

    print("[Migration] inventario_materiali_table migration complete")

    print("[Migration] SQLite upgrade complete!")


def upgrade_postgresql(connection):
    """
    Add _en columns for PostgreSQL database

    PostgreSQL allows multiple columns in one ALTER TABLE statement
    """

    print("[Migration] Adding i18n columns for PostgreSQL...")

    # ========== SITE TABLE ==========
    print("[Migration] Migrating site_table...")

    connection.execute(text("""
        ALTER TABLE site_table
        ADD COLUMN IF NOT EXISTS definizione_sito_en VARCHAR(250),
        ADD COLUMN IF NOT EXISTS descrizione_en TEXT
    """))

    print("[Migration] site_table migration complete")

    # ========== US TABLE ==========
    print("[Migration] Migrating us_table...")

    connection.execute(text("""
        ALTER TABLE us_table
        ADD COLUMN IF NOT EXISTS d_stratigrafica_en VARCHAR(350),
        ADD COLUMN IF NOT EXISTS d_interpretativa_en VARCHAR(350),
        ADD COLUMN IF NOT EXISTS descrizione_en TEXT,
        ADD COLUMN IF NOT EXISTS interpretazione_en TEXT,
        ADD COLUMN IF NOT EXISTS formazione_en VARCHAR(20),
        ADD COLUMN IF NOT EXISTS stato_di_conservazione_en VARCHAR(20),
        ADD COLUMN IF NOT EXISTS colore_en VARCHAR(20),
        ADD COLUMN IF NOT EXISTS consistenza_en VARCHAR(20),
        ADD COLUMN IF NOT EXISTS struttura_en VARCHAR(30),
        ADD COLUMN IF NOT EXISTS inclusi_en TEXT,
        ADD COLUMN IF NOT EXISTS campioni_en TEXT,
        ADD COLUMN IF NOT EXISTS documentazione_en TEXT,
        ADD COLUMN IF NOT EXISTS osservazioni_en TEXT
    """))

    print("[Migration] us_table migration complete")

    # ========== INVENTARIO_MATERIALI TABLE ==========
    print("[Migration] Migrating inventario_materiali_table...")

    connection.execute(text("""
        ALTER TABLE inventario_materiali_table
        ADD COLUMN IF NOT EXISTS tipo_reperto_en TEXT,
        ADD COLUMN IF NOT EXISTS criterio_schedatura_en TEXT,
        ADD COLUMN IF NOT EXISTS definizione_en TEXT,
        ADD COLUMN IF NOT EXISTS descrizione_en TEXT,
        ADD COLUMN IF NOT EXISTS stato_conservazione_en VARCHAR(200),
        ADD COLUMN IF NOT EXISTS elementi_reperto_en TEXT,
        ADD COLUMN IF NOT EXISTS corpo_ceramico_en VARCHAR(200),
        ADD COLUMN IF NOT EXISTS rivestimento_en VARCHAR(200),
        ADD COLUMN IF NOT EXISTS tipo_contenitore_en VARCHAR(200)
    """))

    print("[Migration] inventario_materiali_table migration complete")

    print("[Migration] PostgreSQL upgrade complete!")


def downgrade_sqlite(connection):
    """
    Remove _en columns for SQLite

    Note: SQLite doesn't support DROP COLUMN easily.
    For production, you'd need to recreate tables without these columns.
    For now, we'll just log a warning.
    """
    print("[Migration] WARNING: SQLite does not support DROP COLUMN.")
    print("[Migration] To remove _en columns, you would need to:")
    print("[Migration] 1. Create new tables without _en columns")
    print("[Migration] 2. Copy data from old tables")
    print("[Migration] 3. Drop old tables")
    print("[Migration] 4. Rename new tables")
    print("[Migration] This is not implemented in this migration.")
    print("[Migration] Please perform manual rollback if needed.")


def downgrade_postgresql(connection):
    """
    Remove _en columns for PostgreSQL
    """
    print("[Migration] Removing i18n columns for PostgreSQL...")

    # SITE TABLE
    connection.execute(text("""
        ALTER TABLE site_table
        DROP COLUMN IF EXISTS definizione_sito_en,
        DROP COLUMN IF EXISTS descrizione_en
    """))

    # US TABLE
    connection.execute(text("""
        ALTER TABLE us_table
        DROP COLUMN IF EXISTS d_stratigrafica_en,
        DROP COLUMN IF EXISTS d_interpretativa_en,
        DROP COLUMN IF EXISTS descrizione_en,
        DROP COLUMN IF EXISTS interpretazione_en,
        DROP COLUMN IF EXISTS formazione_en,
        DROP COLUMN IF EXISTS stato_di_conservazione_en,
        DROP COLUMN IF EXISTS colore_en,
        DROP COLUMN IF EXISTS consistenza_en,
        DROP COLUMN IF EXISTS struttura_en,
        DROP COLUMN IF EXISTS inclusi_en,
        DROP COLUMN IF EXISTS campioni_en,
        DROP COLUMN IF EXISTS documentazione_en,
        DROP COLUMN IF EXISTS osservazioni_en
    """))

    # INVENTARIO_MATERIALI TABLE
    connection.execute(text("""
        ALTER TABLE inventario_materiali_table
        DROP COLUMN IF EXISTS tipo_reperto_en,
        DROP COLUMN IF EXISTS criterio_schedatura_en,
        DROP COLUMN IF EXISTS definizione_en,
        DROP COLUMN IF EXISTS descrizione_en,
        DROP COLUMN IF EXISTS stato_conservazione_en,
        DROP COLUMN IF EXISTS elementi_reperto_en,
        DROP COLUMN IF EXISTS corpo_ceramico_en,
        DROP COLUMN IF EXISTS rivestimento_en,
        DROP COLUMN IF EXISTS tipo_contenitore_en
    """))

    print("[Migration] PostgreSQL downgrade complete!")


def run_migration(db_manager, direction='upgrade'):
    """
    Run migration using DatabaseManager

    Args:
        db_manager: DatabaseManager instance
        direction: 'upgrade' or 'downgrade'
    """
    # Get connection from db_manager.connection.engine
    engine = db_manager.connection.engine
    db_type = db_manager.connection._get_db_type()

    print(f"[Migration] Running {direction} for database type: {db_type}")

    # Use engine.begin() to get a connection with transaction
    with engine.begin() as connection:
        if direction == 'upgrade':
            if db_type.lower() == 'sqlite':
                upgrade_sqlite(connection)
            elif db_type.lower() == 'postgresql':
                upgrade_postgresql(connection)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
        elif direction == 'downgrade':
            if db_type.lower() == 'sqlite':
                downgrade_sqlite(connection)
            elif db_type.lower() == 'postgresql':
                downgrade_postgresql(connection)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
        else:
            raise ValueError(f"Invalid direction: {direction}. Use 'upgrade' or 'downgrade'.")

    # Transaction automatically committed when exiting context
    print(f"[Migration] {direction.capitalize()} complete and committed!")


if __name__ == '__main__':
    """
    Standalone migration runner
    """
    import sys
    import os

    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.database.manager import DatabaseManager

    # Get database URL from environment or use default SQLite
    database_url = os.getenv("DATABASE_URL", "sqlite:///./pyarchinit_mini.db")

    print(f"[Migration] Connecting to: {database_url}")

    # Create database manager
    db_conn = DatabaseConnection.from_url(database_url)
    db_manager = DatabaseManager(db_conn)

    # Get direction from command line args
    direction = sys.argv[1] if len(sys.argv) > 1 else 'upgrade'

    if direction not in ['upgrade', 'downgrade']:
        print(f"Usage: python {sys.argv[0]} [upgrade|downgrade]")
        sys.exit(1)

    # Run migration
    try:
        run_migration(db_manager, direction)
        print(f"\n[Migration] SUCCESS! Database {direction} completed.")
    except Exception as e:
        print(f"\n[Migration] ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
