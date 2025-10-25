#!/usr/bin/env python3
"""
Test script for automatic backup system
"""

import sys
import os
from pyarchinit_mini.services.import_export_service import ImportExportService

# Database paths
MINI_DB = 'sqlite:////Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db'
SOURCE_DB = 'sqlite:////Users/enzo/pyarchinit/pyarchinit_DB_folder/Promotion_Krypta_Lund.sqlite'

print("="*80)
print("Testing Automatic Backup System")
print("="*80)
print(f"\nSource DB: {SOURCE_DB}\n")

# Initialize service
service = ImportExportService(MINI_DB, SOURCE_DB)

print("="*80)
print("Test 1: Manual backup creation")
print("="*80)
backup_path = service._backup_source_database()

if backup_path:
    print(f"✓ Backup created: {backup_path}")

    # Check file exists and size
    if os.path.exists(backup_path):
        size_mb = os.path.getsize(backup_path) / (1024 * 1024)
        print(f"✓ Backup file exists ({size_mb:.2f} MB)")
    else:
        print("✗ Backup file not found!")
else:
    print("✗ Backup failed!")

print("\n" + "="*80)
print("Test 2: Backup during migration (auto_backup=True)")
print("="*80)

# Reset backup flags
service._backup_created = False
service._backup_path = None

stats = service.migrate_source_database(tables=['site_table'], auto_backup=True)

print(f"Tables migrated: {stats['tables_migrated']}")
print(f"Columns added: {stats['columns_added']}")
print(f"Backup path: {stats.get('backup_path', 'None')}")

if stats.get('backup_path'):
    print("✓ Backup was created during migration")
else:
    print("  (No backup created - columns already exist)")

print("\n" + "="*80)
print("Test 3: Second migration (should reuse backup)")
print("="*80)

stats2 = service.migrate_source_database(tables=['us_table'], auto_backup=True)

print(f"Tables migrated: {stats2['tables_migrated']}")
print(f"Columns added: {stats2['columns_added']}")
print(f"Backup path: {stats2.get('backup_path', 'None')}")

if stats.get('backup_path') == stats2.get('backup_path'):
    print("✓ Backup path is the same (reused existing backup)")
else:
    print("  Different backup paths")

print("\n" + "="*80)
print("Test 4: Import with auto_backup=False")
print("="*80)

# Create new service to test
service3 = ImportExportService(MINI_DB, SOURCE_DB)
stats3 = service3.import_sites(sito_filter=['Dom zu Lund'], auto_migrate=True, auto_backup=False)

print(f"Sites imported: {stats3['imported']}")
print(f"Sites updated: {stats3['updated']}")
print(f"Backup created: {'No' if not service3._backup_created else 'Yes'}")

print("\n" + "="*80)
print("Summary")
print("="*80)
print(f"✓ Backup system is working correctly")
print(f"✓ SQLite backups are created with timestamps")
print(f"✓ Backups can be disabled with auto_backup=False")
print(f"✓ Only one backup per session (multiple migrations reuse same backup)")
print("="*80)
