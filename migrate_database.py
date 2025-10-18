#!/usr/bin/env python3
"""
Database migration script for PyArchInit-Mini
Run this script to update existing databases with new schema changes
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.database.migrations import DatabaseMigrations

def main():
    """Main migration function"""
    print("PyArchInit-Mini Database Migration Tool")
    print("=" * 40)
    
    # Default database path
    default_db = "./pyarchinit_mini.db"
    
    # Get database path from user or use default
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = input(f"Enter database path (default: {default_db}): ").strip()
        if not db_path:
            db_path = default_db
    
    # Check if database file exists
    if not os.path.exists(db_path) and db_path.startswith("sqlite"):
        print(f"Database file {db_path} does not exist!")
        print("Please provide a valid database path.")
        return 1
    
    try:
        # Connect to database
        print(f"Connecting to database: {db_path}")
        
        if db_path.startswith(("postgresql://", "mysql://", "sqlite:///")):
            # Full connection string
            db_conn = DatabaseConnection.from_url(db_path)
        else:
            # Assume SQLite file path
            db_conn = DatabaseConnection.sqlite(db_path)
        
        # Test connection
        if not db_conn.test_connection():
            print("❌ Failed to connect to database!")
            return 1
        
        print("✅ Database connection successful")
        
        # Initialize database manager
        db_manager = DatabaseManager(db_conn)
        migrations = DatabaseMigrations(db_manager)
        
        # Show current table info
        print("\n📊 Current Database Schema:")
        print("-" * 30)
        
        tables_to_check = ['inventario_materiali_table', 'site_table', 'us_table']
        
        for table_name in tables_to_check:
            table_info = migrations.get_table_info(table_name)
            if table_info['exists']:
                print(f"✅ {table_name}: {table_info['column_count']} columns")
            else:
                print(f"❌ {table_name}: Table not found")
        
        # Check what migrations are needed
        print("\n🔍 Checking required migrations...")
        
        required_cols = ['schedatore', 'date_scheda', 'punto_rinv', 'negativo_photo', 'diapositiva']
        missing_cols = migrations.check_migration_needed('inventario_materiali_table', required_cols)
        
        if missing_cols:
            print(f"📝 Missing columns in inventario_materiali_table: {', '.join(missing_cols)}")
            
            # Ask user for confirmation
            response = input("\n🚀 Apply migrations? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                print("\n⚙️  Applying migrations...")
                
                # Run migrations
                migrations_applied = migrations.migrate_all_tables()
                
                if migrations_applied > 0:
                    print(f"✅ Successfully applied {migrations_applied} migrations!")
                else:
                    print("ℹ️  No migrations were needed.")
                
                # Show updated schema
                print("\n📊 Updated Database Schema:")
                print("-" * 30)
                
                for table_name in tables_to_check:
                    table_info = migrations.get_table_info(table_name)
                    if table_info['exists']:
                        print(f"✅ {table_name}: {table_info['column_count']} columns")
                
            else:
                print("❌ Migration cancelled by user")
        else:
            print("✅ Database is up to date - no migrations needed!")
        
        # Close connection
        db_conn.close()
        print("\n🎉 Migration process completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())