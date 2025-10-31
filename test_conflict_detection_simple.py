#!/usr/bin/env python3
"""
Simple test for conflict detection using existing databases
"""

import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyarchinit_mini.services.import_export_service import ImportExportService

def test_with_same_database():
    """Test conflict detection when source == target (all conflicts)"""
    print("=" * 70)
    print("TEST: Same Database (All Conflicts)")
    print("=" * 70)

    # Use same database for source and target
    db_path = "/Users/enzo/Documents/pyarchinit-mini-desk/data/pyarchinit_tutorial.db"

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False

    db_url = f"sqlite:///{db_path}"

    print(f"\n🔍 Analyzing conflicts between same database...")
    print(f"   Database: {db_path}")

    conflicts = ImportExportService._detect_conflicts(db_url, db_url)

    print(f"\n📊 Results:")
    print(f"   Has conflicts: {conflicts['has_conflicts']}")
    print(f"   Total conflicts: {conflicts['total_conflicts']}")
    print(f"   Total new records: {conflicts['total_new_records']}")

    if conflicts['errors']:
        print(f"\n⚠️  Errors:")
        for error in conflicts['errors']:
            print(f"   - {error}")

    print(f"\n📋 Tables with data:")
    for table_name, data in conflicts['tables'].items():
        if data['total_source_records'] > 0:
            print(f"   {table_name}:")
            print(f"      Total records: {data['total_source_records']}")
            print(f"      Conflicts: {data['conflicts']}")
            print(f"      New: {data['new_records']}")

    # All records should be conflicts, none should be new
    success = (
        conflicts['has_conflicts'] and
        conflicts['total_new_records'] == 0 and
        conflicts['total_conflicts'] > 0
    )

    if success:
        print(f"\n✅ TEST PASSED: All records correctly identified as conflicts")
    else:
        print(f"\n❌ TEST FAILED: Expected all conflicts, no new records")

    return success

def test_with_empty_target():
    """Test conflict detection with empty target (all new)"""
    print("\n" + "=" * 70)
    print("TEST: Empty Target (All New Records)")
    print("=" * 70)

    source_path = "/Users/enzo/Documents/pyarchinit-mini-desk/data/pyarchinit_tutorial.db"
    target_path = "/tmp/empty_test_db.db"

    # Create empty target
    from pyarchinit_mini.database.database_creator import create_empty_database
    create_empty_database('sqlite', target_path, overwrite=True)

    source_url = f"sqlite:///{source_path}"
    target_url = f"sqlite:///{target_path}"

    print(f"\n🔍 Analyzing conflicts...")
    print(f"   Source: {source_path} (has data)")
    print(f"   Target: {target_path} (empty)")

    conflicts = ImportExportService._detect_conflicts(source_url, target_url)

    print(f"\n📊 Results:")
    print(f"   Has conflicts: {conflicts['has_conflicts']}")
    print(f"   Total conflicts: {conflicts['total_conflicts']}")
    print(f"   Total new records: {conflicts['total_new_records']}")

    print(f"\n📋 Tables:")
    for table_name, data in conflicts['tables'].items():
        if data['total_source_records'] > 0:
            print(f"   {table_name}: {data['new_records']} new records")

    # Cleanup
    if os.path.exists(target_path):
        os.remove(target_path)

    # All records should be new, none should be conflicts
    success = (
        not conflicts['has_conflicts'] and
        conflicts['total_conflicts'] == 0 and
        conflicts['total_new_records'] > 0
    )

    if success:
        print(f"\n✅ TEST PASSED: All records correctly identified as new")
    else:
        print(f"\n❌ TEST FAILED: Expected no conflicts, all new")

    return success

def test_with_different_databases():
    """Test with two different databases (mixed scenario)"""
    print("\n" + "=" * 70)
    print("TEST: Different Databases (Mixed Scenario)")
    print("=" * 70)

    # Copy tutorial db to create a modified version
    source_path = "/Users/enzo/Documents/pyarchinit-mini-desk/data/pyarchinit_tutorial.db"
    target_path = "/tmp/modified_test_db.db"

    # Copy source to target
    shutil.copy2(source_path, target_path)

    # Now we have two identical databases - they will have all conflicts
    source_url = f"sqlite:///{source_path}"
    target_url = f"sqlite:///{target_path}"

    print(f"\n🔍 Analyzing conflicts...")
    print(f"   Source: {source_path}")
    print(f"   Target: {target_path} (copy of source)")

    conflicts = ImportExportService._detect_conflicts(source_url, target_url)

    print(f"\n📊 Results:")
    print(f"   Has conflicts: {conflicts['has_conflicts']}")
    print(f"   Total conflicts: {conflicts['total_conflicts']}")
    print(f"   Total new records: {conflicts['total_new_records']}")

    print(f"\n📋 Conflicting tables:")
    for table_name, data in conflicts['tables'].items():
        if data['conflicts'] > 0:
            print(f"   {table_name}: {data['conflicts']} conflicts")

    # Cleanup
    if os.path.exists(target_path):
        os.remove(target_path)

    # Should have conflicts, no new records (since it's a copy)
    success = (
        conflicts['has_conflicts'] and
        conflicts['total_conflicts'] > 0 and
        conflicts['total_new_records'] == 0
    )

    if success:
        print(f"\n✅ TEST PASSED: Conflicts detected correctly")
    else:
        print(f"\n❌ TEST FAILED")

    return success

def main():
    """Run all tests"""
    print("\n" + "🧪" * 35)
    print("CONFLICT DETECTION SYSTEM TESTS (SIMPLE)")
    print("🧪" * 35 + "\n")

    tests = [
        ("Same Database", test_with_same_database),
        ("Empty Target", test_with_empty_target),
        ("Different Databases", test_with_different_databases)
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
