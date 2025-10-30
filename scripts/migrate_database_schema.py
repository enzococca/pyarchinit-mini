#!/usr/bin/env python3
"""
Database Schema Migration Script
Adds missing columns for Extended Matrix Framework support (v1.6.0+)

This script migrates old PyArchInit-Mini databases to the current schema
by adding missing columns to the us_table.

Usage:
    python scripts/migrate_database_schema.py [database_path]

If no database path is provided, migrates the default database.
"""

import sqlite3
import sys
import os
from pathlib import Path


def get_default_db_path():
    """Get the default database path from config"""
    home = Path.home()
    config_dir = home / '.pyarchinit_mini'
    db_path = config_dir / 'data' / 'pyarchinit_mini.db'
    return str(db_path)


def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def add_column_if_missing(cursor, table_name, column_name, column_type, default_value='NULL'):
    """Add a column to a table if it doesn't exist"""
    if not check_column_exists(cursor, table_name, column_name):
        print(f"  ➕ Adding column: {column_name} ({column_type})")
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default_value}")
        return True
    else:
        print(f"  ✓ Column already exists: {column_name}")
        return False


def migrate_us_table(db_path):
    """Migrate US table to add Extended Matrix fields"""
    print(f"\n📂 Database: {db_path}")

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n🔍 Checking us_table schema...")

        # Extended Matrix fields (added in v1.6.0)
        migrations = [
            ('unita_tipo', 'VARCHAR(200)', 'NULL'),
            ('tipo_documento', 'VARCHAR(100)', 'NULL'),
            ('file_path', 'VARCHAR(500)', 'NULL'),
        ]

        changes_made = 0
        for column_name, column_type, default_value in migrations:
            if add_column_if_missing(cursor, 'us_table', column_name, column_type, default_value):
                changes_made += 1

        # Also check for internationalization columns (added in v1.7.0)
        i18n_migrations = [
            ('d_stratigrafica_en', 'VARCHAR(350)', 'NULL'),
            ('d_interpretativa_en', 'VARCHAR(350)', 'NULL'),
            ('descrizione_en', 'TEXT', 'NULL'),
            ('interpretazione_en', 'TEXT', 'NULL'),
            ('formazione_en', 'VARCHAR(20)', 'NULL'),
            ('stato_di_conservazione_en', 'VARCHAR(20)', 'NULL'),
            ('colore_en', 'VARCHAR(20)', 'NULL'),
            ('consistenza_en', 'VARCHAR(20)', 'NULL'),
            ('struttura_en', 'VARCHAR(30)', 'NULL'),
            ('inclusi_en', 'TEXT', 'NULL'),
            ('campioni_en', 'TEXT', 'NULL'),
            ('documentazione_en', 'TEXT', 'NULL'),
            ('osservazioni_en', 'TEXT', 'NULL'),
        ]

        print("\n🔍 Checking internationalization columns...")
        for column_name, column_type, default_value in i18n_migrations:
            if add_column_if_missing(cursor, 'us_table', column_name, column_type, default_value):
                changes_made += 1

        conn.commit()
        conn.close()

        if changes_made > 0:
            print(f"\n✅ Migration completed: {changes_made} column(s) added")
        else:
            print(f"\n✓ Database schema is up to date")

        return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def migrate_site_table(db_path):
    """Migrate site_table to add internationalization fields"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n🔍 Checking site_table schema...")

        # Internationalization fields (added in v1.7.0)
        site_migrations = [
            ('definizione_sito_en', 'VARCHAR(250)', 'NULL'),
            ('descrizione_en', 'TEXT', 'NULL'),
        ]

        changes_made = 0
        for column_name, column_type, default_value in site_migrations:
            if add_column_if_missing(cursor, 'site_table', column_name, column_type, default_value):
                changes_made += 1

        conn.commit()
        conn.close()

        if changes_made > 0:
            print(f"✅ Site table migration: {changes_made} column(s) added")

        return True

    except sqlite3.Error as e:
        print(f"❌ Database error in site_table: {e}")
        return False


def main():
    print("=" * 70)
    print("PyArchInit-Mini Database Schema Migration")
    print("=" * 70)

    # Get database path from command line or use default
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = get_default_db_path()
        print(f"\nNo database path provided, using default: {db_path}")

    # Migrate US table
    success = migrate_us_table(db_path)

    # Migrate Site table
    if success:
        migrate_site_table(db_path)

    if success:
        print("\n" + "=" * 70)
        print("✅ Database migration completed successfully!")
        print("=" * 70)
        print("\nYou can now run pyarchinit-mini-web without errors.")
        return 0
    else:
        print("\n" + "=" * 70)
        print("❌ Database migration failed!")
        print("=" * 70)
        return 1


if __name__ == '__main__':
    sys.exit(main())
