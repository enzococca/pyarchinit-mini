#!/usr/bin/env python3
"""
Migration runner for i18n columns

Usage:
    python run_migration.py upgrade    # Add _en columns
    python run_migration.py downgrade  # Remove _en columns (PostgreSQL only)
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.database.migration_scripts.add_i18n_columns import run_migration

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
