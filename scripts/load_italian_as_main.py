#!/usr/bin/env python3
"""
Load Italian sample database as main database
"""

import os
import shutil
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def load_italian_as_main():
    """Copy Italian sample database as main database"""
    
    data_dir = os.path.join(project_root, 'data')
    italian_db = os.path.join(data_dir, 'pyarchinit_mini_italian.db')
    main_db = os.path.join(data_dir, 'pyarchinit_mini.db')
    
    if not os.path.exists(italian_db):
        print("❌ Italian database not found. Run create_italian_sample_database.py first.")
        return False
    
    # Backup existing main database if it exists
    if os.path.exists(main_db):
        backup_db = os.path.join(data_dir, 'pyarchinit_mini_backup.db')
        shutil.copy2(main_db, backup_db)
        print(f"📋 Backed up existing database to: {backup_db}")
    
    # Copy Italian database as main
    shutil.copy2(italian_db, main_db)
    print(f"✅ Loaded Italian sample database as main database")
    print(f"📍 Location: {main_db}")
    
    return True

if __name__ == "__main__":
    load_italian_as_main()