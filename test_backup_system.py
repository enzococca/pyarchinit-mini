#!/usr/bin/env python3
"""
Test script for database backup system

Tests:
1. SQLite database backup creation
2. Backup file creation with timestamp
3. Backup file size verification
"""

import os
import sys
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyarchinit_mini.services.import_export_service import ImportExportService

def test_sqlite_backup():
    """Test SQLite database backup creation"""
    print("=" * 70)
    print("TEST 1: SQLite Database Backup")
    print("=" * 70)

    # Use the tutorial database as source
    source_db_path = "/Users/enzo/Documents/pyarchinit-mini-desk/data/pyarchinit_tutorial.db"

    if not os.path.exists(source_db_path):
        print(f"❌ Source database not found: {source_db_path}")
        return False

    source_db_url = f"sqlite:///{source_db_path}"

    print(f"\n📁 Source database: {source_db_path}")
    source_size = os.path.getsize(source_db_path) / (1024 * 1024)
    print(f"📊 Source size: {source_size:.2f} MB")

    # Create backup
    print("\n🔄 Creating backup...")
    backup_result = ImportExportService._create_backup(source_db_url)

    # Verify results
    print("\n📋 Backup Results:")
    print(f"   Success: {backup_result['success']}")
    print(f"   Path: {backup_result['path']}")
    print(f"   Size: {backup_result['size_mb']} MB")
    print(f"   Message: {backup_result['message']}")

    if backup_result['success']:
        # Verify backup file exists
        if os.path.exists(backup_result['path']):
            print(f"\n✅ Backup file created successfully!")
            print(f"   Location: {backup_result['path']}")

            # Verify file size matches
            backup_size = os.path.getsize(backup_result['path']) / (1024 * 1024)
            if abs(backup_size - source_size) < 0.1:  # Allow 0.1 MB difference
                print(f"✅ Backup size matches source ({backup_size:.2f} MB)")
            else:
                print(f"⚠️  Backup size differs from source: {backup_size:.2f} MB vs {source_size:.2f} MB")

            return True
        else:
            print(f"❌ Backup file not found: {backup_result['path']}")
            return False
    else:
        print(f"❌ Backup creation failed: {backup_result['message']}")
        return False

def test_backup_with_custom_dir():
    """Test backup with custom directory"""
    print("\n" + "=" * 70)
    print("TEST 2: Backup with Custom Directory")
    print("=" * 70)

    source_db_path = "/Users/enzo/Documents/pyarchinit-mini-desk/data/pyarchinit_tutorial.db"
    source_db_url = f"sqlite:///{source_db_path}"
    backup_dir = "/tmp/pyarchinit_backups"

    # Create backup in custom directory
    print(f"\n📁 Backup directory: {backup_dir}")
    backup_result = ImportExportService._create_backup(source_db_url, backup_dir)

    print("\n📋 Backup Results:")
    print(f"   Success: {backup_result['success']}")
    print(f"   Path: {backup_result['path']}")
    print(f"   Size: {backup_result['size_mb']} MB")

    if backup_result['success']:
        # Verify it's in the correct directory
        if backup_result['path'].startswith(backup_dir):
            print(f"✅ Backup created in correct directory")
            print(f"   Full path: {backup_result['path']}")

            # Cleanup
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
                print(f"🧹 Cleaned up test directory: {backup_dir}")

            return True
        else:
            print(f"❌ Backup not in expected directory")
            return False
    else:
        print(f"❌ Backup failed: {backup_result['message']}")
        return False

def test_migration_with_backup():
    """Test full migration with automatic backup"""
    print("\n" + "=" * 70)
    print("TEST 3: Migration with Automatic Backup")
    print("=" * 70)

    source_db_path = "/Users/enzo/Documents/pyarchinit-mini-desk/data/pyarchinit_tutorial.db"
    source_db_url = f"sqlite:///{source_db_path}"

    # Create a temporary target database
    target_db_path = "/tmp/test_migration_target.db"
    target_db_url = f"sqlite:///{target_db_path}"

    # Remove target if exists
    if os.path.exists(target_db_path):
        os.remove(target_db_path)

    print(f"\n🔄 Testing migration with auto_backup=True...")
    print(f"   Source: {source_db_path}")
    print(f"   Target: {target_db_path}")

    # Run migration with auto backup
    result = ImportExportService.migrate_database(
        source_db_url=source_db_url,
        target_db_url=target_db_url,
        create_target=True,
        overwrite_target=True,
        auto_backup=True  # This should create a backup
    )

    print("\n📋 Migration Results:")
    print(f"   Success: {result['success']}")
    print(f"   Tables migrated: {result['tables_migrated']}")
    print(f"   Rows copied: {result['total_rows_copied']}")
    print(f"   Backup created: {result['backup_created']}")
    print(f"   Backup path: {result['backup_path']}")
    print(f"   Backup size: {result['backup_size_mb']} MB")
    print(f"   Duration: {result['duration_seconds']:.2f}s")

    if result['errors']:
        print(f"\n⚠️  Errors/Warnings:")
        for error in result['errors']:
            print(f"   - {error}")

    # Verify backup was created
    if result['backup_created']:
        if result['backup_path'] and os.path.exists(result['backup_path']):
            print(f"\n✅ Migration backup created successfully!")
            print(f"   Path: {result['backup_path']}")

            # Cleanup test files
            if os.path.exists(target_db_path):
                os.remove(target_db_path)
                print(f"🧹 Cleaned up target database")

            return True
        else:
            print(f"❌ Backup path reported but file not found")
            return False
    else:
        print(f"❌ No backup was created during migration")
        return False

def main():
    """Run all backup system tests"""
    print("\n" + "🧪" * 35)
    print("DATABASE BACKUP SYSTEM TESTS")
    print("🧪" * 35 + "\n")

    tests = [
        ("SQLite Backup", test_sqlite_backup),
        ("Custom Directory Backup", test_backup_with_custom_dir),
        ("Migration with Backup", test_migration_with_backup)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test {test_name} failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} tests passed")
    print(f"{'='*70}\n")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
