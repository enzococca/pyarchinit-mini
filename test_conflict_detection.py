#!/usr/bin/env python3
"""
Test script for conflict detection system

Tests:
1. Detect no conflicts (fresh databases)
2. Detect ID conflicts (duplicate IDs)
3. Detect mixed scenario (some conflicts, some new records)
"""

import os
import sys
import shutil
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyarchinit_mini.services.import_export_service import ImportExportService
from pyarchinit_mini.database.database_creator import create_empty_database

def setup_test_databases():
    """Create test databases with known conflicts"""
    # Paths for test databases
    source_path = "/tmp/test_conflict_source.db"
    target_path = "/tmp/test_conflict_target.db"

    # Remove if they exist
    for path in [source_path, target_path]:
        if os.path.exists(path):
            os.remove(path)

    # Create empty databases with schema
    create_empty_database('sqlite', source_path, overwrite=True)
    create_empty_database('sqlite', target_path, overwrite=True)

    return source_path, target_path

def insert_test_data(db_path, sites_data, us_data, inventario_data):
    """Insert test data into database"""
    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Insert sites
        for site in sites_data:
            session.execute(text("""
                INSERT INTO site_table (id, sito, nazione, regione, comune, descrizione)
                VALUES (:id, :sito, :nazione, :regione, :comune, :descrizione)
            """), site)

        # Insert US
        for us in us_data:
            session.execute(text("""
                INSERT INTO us_table (id, sito, area, us, d_stratigrafica, interpretazione)
                VALUES (:id, :sito, :area, :us, :d_stratigrafica, :interpretazione)
            """), us)

        # Insert inventario
        for inv in inventario_data:
            session.execute(text("""
                INSERT INTO inventario_materiali_table (id, sito, numero_inventario, tipo_reperto, materiale)
                VALUES (:id, :sito, :numero_inventario, :tipo_reperto, :materiale)
            """), inv)

        session.commit()
        print(f"✓ Inserted {len(sites_data)} sites, {len(us_data)} US, {len(inventario_data)} inventario")

    except Exception as e:
        session.rollback()
        print(f"❌ Error inserting data: {e}")
        raise
    finally:
        session.close()

def test_no_conflicts():
    """Test conflict detection with no conflicts (all new records)"""
    print("=" * 70)
    print("TEST 1: No Conflicts (Fresh Target Database)")
    print("=" * 70)

    source_path, target_path = setup_test_databases()

    # Insert data only in source (target is empty)
    insert_test_data(
        source_path,
        sites_data=[
            {'id': 1, 'sito': 'Site A', 'nazione': 'Italy', 'regione': 'Lazio', 'comune': 'Rome', 'descrizione': 'Test site A'},
            {'id': 2, 'sito': 'Site B', 'nazione': 'Italy', 'regione': 'Lazio', 'comune': 'Rome', 'descrizione': 'Test site B'},
        ],
        us_data=[
            {'id': 1, 'sito': 'Site A', 'area': '1', 'us': 1, 'd_stratigrafica': 'Strato', 'interpretazione': 'Test US 1'},
            {'id': 2, 'sito': 'Site A', 'area': '1', 'us': 2, 'd_stratigrafica': 'Strato', 'interpretazione': 'Test US 2'},
        ],
        inventario_data=[
            {'id': 1, 'sito': 'Site A', 'numero_inventario': 'INV001', 'tipo_reperto': 'Ceramica', 'materiale': 'Terracotta'},
        ]
    )

    # Detect conflicts
    source_url = f"sqlite:///{source_path}"
    target_url = f"sqlite:///{target_path}"

    print(f"\n🔍 Analyzing conflicts...")
    conflicts = ImportExportService._detect_conflicts(source_url, target_url)

    print(f"\n📊 Results:")
    print(f"   Has conflicts: {conflicts['has_conflicts']}")
    print(f"   Total conflicts: {conflicts['total_conflicts']}")
    print(f"   Total new records: {conflicts['total_new_records']}")

    print(f"\n📋 Per Table:")
    for table_name, table_data in conflicts['tables'].items():
        if table_data['total_source_records'] > 0:
            print(f"   {table_name}:")
            print(f"      Conflicts: {table_data['conflicts']}")
            print(f"      New records: {table_data['new_records']}")

    # Cleanup
    os.remove(source_path)
    os.remove(target_path)

    # Verify
    success = (
        not conflicts['has_conflicts'] and
        conflicts['total_conflicts'] == 0 and
        conflicts['total_new_records'] == 5  # 2 sites + 2 us + 1 inventario
    )

    if success:
        print(f"\n✅ TEST PASSED: No conflicts detected correctly")
    else:
        print(f"\n❌ TEST FAILED: Expected no conflicts")

    return success

def test_with_conflicts():
    """Test conflict detection with duplicate IDs"""
    print("\n" + "=" * 70)
    print("TEST 2: With Conflicts (Duplicate IDs)")
    print("=" * 70)

    source_path, target_path = setup_test_databases()

    # Insert overlapping data
    source_sites = [
        {'id': 1, 'sito': 'Site A (source)', 'nazione': 'Italy', 'regione': 'Lazio', 'comune': 'Rome', 'descrizione': 'Source version'},
        {'id': 2, 'sito': 'Site B', 'nazione': 'Italy', 'regione': 'Lazio', 'comune': 'Rome', 'descrizione': 'Only in source'},
        {'id': 3, 'sito': 'Site C', 'nazione': 'Italy', 'regione': 'Lazio', 'comune': 'Rome', 'descrizione': 'Also in source'},
    ]

    target_sites = [
        {'id': 1, 'sito': 'Site A (target)', 'nazione': 'Italy', 'regione': 'Lazio', 'comune': 'Rome', 'descrizione': 'Target version'},  # CONFLICT!
        {'id': 4, 'sito': 'Site D', 'nazione': 'Italy', 'regione': 'Lazio', 'comune': 'Rome', 'descrizione': 'Only in target'},
    ]

    insert_test_data(source_path, source_sites, [], [])
    insert_test_data(target_path, target_sites, [], [])

    # Detect conflicts
    source_url = f"sqlite:///{source_path}"
    target_url = f"sqlite:///{target_path}"

    print(f"\n🔍 Analyzing conflicts...")
    conflicts = ImportExportService._detect_conflicts(source_url, target_url)

    print(f"\n📊 Results:")
    print(f"   Has conflicts: {conflicts['has_conflicts']}")
    print(f"   Total conflicts: {conflicts['total_conflicts']}")
    print(f"   Total new records: {conflicts['total_new_records']}")

    if 'site_table' in conflicts['tables']:
        site_conflicts = conflicts['tables']['site_table']
        print(f"\n📋 Site Table Details:")
        print(f"   Conflicts: {site_conflicts['conflicts']}")
        print(f"   New records: {site_conflicts['new_records']}")
        print(f"   Conflicting IDs: {site_conflicts['conflicting_ids']}")

    # Cleanup
    os.remove(source_path)
    os.remove(target_path)

    # Verify
    success = (
        conflicts['has_conflicts'] and
        conflicts['total_conflicts'] == 1 and  # ID 1 conflicts
        conflicts['total_new_records'] == 2  # IDs 2 and 3 are new
    )

    if success:
        print(f"\n✅ TEST PASSED: Conflicts detected correctly (1 conflict, 2 new)")
    else:
        print(f"\n❌ TEST FAILED: Expected 1 conflict and 2 new records")

    return success

def test_mixed_scenario():
    """Test with multiple tables having different conflict scenarios"""
    print("\n" + "=" * 70)
    print("TEST 3: Mixed Scenario (Multiple Tables)")
    print("=" * 70)

    source_path, target_path = setup_test_databases()

    # Source data
    insert_test_data(
        source_path,
        sites_data=[
            {'id': 1, 'sito': 'Site A', 'nazione': 'Italy', 'regione': 'Lazio', 'comune': 'Rome', 'descrizione': 'Test'},
            {'id': 2, 'sito': 'Site B', 'nazione': 'Italy', 'regione': 'Lazio', 'comune': 'Rome', 'descrizione': 'Test'},
        ],
        us_data=[
            {'id': 10, 'sito': 'Site A', 'area': '1', 'us': 1, 'd_stratigrafica': 'Strato', 'interpretazione': 'US 10'},
            {'id': 11, 'sito': 'Site A', 'area': '1', 'us': 2, 'd_stratigrafica': 'Strato', 'interpretazione': 'US 11'},
            {'id': 12, 'sito': 'Site A', 'area': '1', 'us': 3, 'd_stratigrafica': 'Strato', 'interpretazione': 'US 12'},
        ],
        inventario_data=[
            {'id': 100, 'sito': 'Site A', 'numero_inventario': 'INV100', 'tipo_reperto': 'Ceramica', 'materiale': 'Terracotta'},
        ]
    )

    # Target data (overlapping IDs in different tables)
    insert_test_data(
        target_path,
        sites_data=[
            {'id': 1, 'sito': 'Site A (old)', 'nazione': 'Italy', 'regione': 'Lazio', 'comune': 'Rome', 'descrizione': 'Old version'},  # CONFLICT
        ],
        us_data=[
            {'id': 10, 'sito': 'Site A', 'area': '1', 'us': 1, 'd_stratigrafica': 'Strato', 'interpretazione': 'Old US 10'},  # CONFLICT
            {'id': 13, 'sito': 'Site A', 'area': '1', 'us': 4, 'd_stratigrafica': 'Strato', 'interpretazione': 'Only in target'},
        ],
        inventario_data=[]  # Empty - all source inventario are new
    )

    # Detect conflicts
    source_url = f"sqlite:///{source_path}"
    target_url = f"sqlite:///{target_path}"

    print(f"\n🔍 Analyzing conflicts...")
    conflicts = ImportExportService._detect_conflicts(source_url, target_url)

    print(f"\n📊 Overall Results:")
    print(f"   Has conflicts: {conflicts['has_conflicts']}")
    print(f"   Total conflicts: {conflicts['total_conflicts']}")
    print(f"   Total new records: {conflicts['total_new_records']}")

    print(f"\n📋 Detailed Table Analysis:")
    for table_name in ['site_table', 'us_table', 'inventario_materiali_table']:
        if table_name in conflicts['tables']:
            data = conflicts['tables'][table_name]
            print(f"\n   {table_name}:")
            print(f"      Total source records: {data['total_source_records']}")
            print(f"      Conflicts: {data['conflicts']}")
            print(f"      New records: {data['new_records']}")
            if data['conflicting_ids']:
                print(f"      Conflicting IDs: {data['conflicting_ids']}")

    # Cleanup
    os.remove(source_path)
    os.remove(target_path)

    # Verify
    success = (
        conflicts['has_conflicts'] and
        conflicts['total_conflicts'] == 2 and  # 1 site + 1 US
        conflicts['total_new_records'] == 4  # 1 site + 2 US + 1 inventario
    )

    if success:
        print(f"\n✅ TEST PASSED: Mixed scenario handled correctly")
    else:
        print(f"\n❌ TEST FAILED: Expected 2 conflicts and 4 new records")
        print(f"   Got: {conflicts['total_conflicts']} conflicts, {conflicts['total_new_records']} new")

    return success

def main():
    """Run all conflict detection tests"""
    print("\n" + "🧪" * 35)
    print("CONFLICT DETECTION SYSTEM TESTS")
    print("🧪" * 35 + "\n")

    tests = [
        ("No Conflicts", test_no_conflicts),
        ("With Conflicts", test_with_conflicts),
        ("Mixed Scenario", test_mixed_scenario)
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
