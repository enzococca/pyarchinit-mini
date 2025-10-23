#!/usr/bin/env python3
"""
Run migration to add tipo_documento field to us_table

Usage:
    python run_tipo_documento_migration.py upgrade
    python run_tipo_documento_migration.py downgrade
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.migration_scripts.add_tipo_documento import upgrade, downgrade


def main():
    """Run migration"""

    if len(sys.argv) < 2:
        print("Usage: python run_tipo_documento_migration.py [upgrade|downgrade]")
        sys.exit(1)

    action = sys.argv[1].lower()

    if action not in ('upgrade', 'downgrade'):
        print("Error: Action must be 'upgrade' or 'downgrade'")
        sys.exit(1)

    # Connect to database
    print("Connecting to database...")

    # Try to get database URL from environment or use default SQLite
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///./pyarchinit_mini.db')
    print(f"Database URL: {db_url}")

    db_conn = DatabaseConnection(db_url)
    if 'postgresql' in db_url or 'postgres' in db_url:
        db_type = 'postgresql'
    else:
        db_type = 'sqlite'

    print(f"Database type detected: {db_type}")

    # Create backup warning
    print("\n" + "="*60)
    print("WARNING: This migration will modify the database schema")
    print("Please ensure you have a backup of your database!")
    print("="*60)

    if db_type == 'sqlite':
        db_file = db_url.replace('sqlite:///', '')
        print(f"\nSQLite database file: {db_file}")
        print(f"Backup command: cp {db_file} {db_file}.backup")

    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled")
        sys.exit(0)

    # Run migration
    print(f"\nRunning {action}...")

    with db_conn.engine.begin() as connection:
        if action == 'upgrade':
            upgrade(connection, db_type)
        else:
            downgrade(connection, db_type)

    print(f"\n{action.capitalize()} completed successfully!")
    print("\nIMPORTANT: Restart your application to use the updated schema")


if __name__ == '__main__':
    main()
