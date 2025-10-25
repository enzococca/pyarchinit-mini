#!/usr/bin/env python3
"""
Script to add missing i18n (_en) columns to PyArchInit database

Usage:
    python add_i18n_columns_to_pyarchinit_db.py <database_path>

Example:
    python add_i18n_columns_to_pyarchinit_db.py /path/to/pyarchinit.db
"""

import sys
import sqlite3
from pathlib import Path

# Define i18n columns for each table
I18N_COLUMNS = {
    'site_table': [
        'definizione_sito_en',
        'descrizione_en'
    ],
    'us_table': [
        'd_stratigrafica_en',
        'd_interpretativa_en',
        'descrizione_en',
        'interpretazione_en',
        'formazione_en',
        'stato_di_conservazione_en',
        'colore_en',
        'consistenza_en',
        'struttura_en',
        'inclusi_en',
        'campioni_en',
        'documentazione_en',
        'osservazioni_en'
    ],
    'inventario_materiali_table': [
        'tipo_reperto_en',
        'definizione_reperto_en',
        'descrizione_en',
        'tecnologia_en',
        'forma_en',
        'stato_conservazione_en',
        'osservazioni_en'
    ]
}


def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def add_i18n_columns(db_path):
    """Add missing i18n columns to PyArchInit database"""

    db_path = Path(db_path).expanduser().resolve()

    if not db_path.exists():
        print(f"❌ Error: Database not found: {db_path}")
        return False

    print(f"📂 Database: {db_path}")
    print(f"🔧 Adding missing i18n columns...\n")

    # Backup recommendation
    backup_path = db_path.with_suffix('.backup' + db_path.suffix)
    print(f"💡 Recommendation: Create a backup first:")
    print(f"   cp '{db_path}' '{backup_path}'\n")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    total_added = 0

    try:
        for table_name, columns in I18N_COLUMNS.items():
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                print(f"⚠️  Table {table_name} not found, skipping")
                continue

            print(f"📋 Processing table: {table_name}")

            added_count = 0
            for column_name in columns:
                if check_column_exists(cursor, table_name, column_name):
                    print(f"   ✓ Column {column_name} already exists")
                else:
                    try:
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT")
                        print(f"   ✅ Added column: {column_name}")
                        added_count += 1
                        total_added += 1
                    except sqlite3.Error as e:
                        print(f"   ❌ Failed to add {column_name}: {e}")

            if added_count == 0:
                print(f"   All i18n columns already present")

            print()

        conn.commit()

        print("="*60)
        if total_added > 0:
            print(f"✅ Success! Added {total_added} i18n columns")
            print(f"📊 Database is now compatible with PyArchInit-Mini")
        else:
            print(f"✅ All i18n columns already present")
        print("="*60)

        return True

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        return False
    finally:
        conn.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: python add_i18n_columns_to_pyarchinit_db.py <database_path>")
        print("\nExample:")
        print("  python add_i18n_columns_to_pyarchinit_db.py /Users/enzo/Desktop/pyarchinit_db.sqlite")
        sys.exit(1)

    db_path = sys.argv[1]
    success = add_i18n_columns(db_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
