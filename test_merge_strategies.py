#!/usr/bin/env python3
"""
Test script for merge strategies in database migration

Tests all three strategies:
1. 'skip' - Skip records with conflicting IDs
2. 'overwrite' - Update existing records with new data
3. 'renumber' - Generate new IDs for conflicting records
"""

import os
import sys
import shutil
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyarchinit_mini.services.import_export_service import ImportExportService
from pyarchinit_mini.database.database_creator import create_empty_database

def setup_test_databases():
    """Create test databases with known data for testing strategies"""
    source_path = "/tmp/test_merge_source.db"
    target_path = "/tmp/test_merge_target.db"

    # Remove if they exist
    for path in [source_path, target_path]:
        if os.path.exists(path):
            os.remove(path)

    # Create empty databases with schema
    create_empty_database('sqlite', source_path, overwrite=True)
    create_empty_database('sqlite', target_path, overwrite=True)

    return source_path, target_path

def insert_test_sites(db_path, sites_data):
    """Insert test sites into database"""
    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        now = datetime.now()
        for site in sites_data:
            site_with_timestamps = site.copy()
            site_with_timestamps['created'] = now
            site_with_timestamps['updated'] = now

            session.execute(text("""
                INSERT INTO site_table (id_sito, sito, nazione, regione, comune, descrizione, created_at, updated_at)
                VALUES (:id, :sito, :nazione, :regione, :comune, :descrizione, :created, :updated)
            """), site_with_timestamps)
        session.commit()
        print(f"✓ Inserted {len(sites_data)} sites into {os.path.basename(db_path)}")
    except Exception as e:
        session.rollback()
        print(f"❌ Error inserting sites: {e}")
        raise
    finally:
        session.close()

def get_sites_from_db(db_path):
    """Get all sites from database"""
    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        result = session.execute(text("""
            SELECT id_sito, sito, descrizione
            FROM site_table
            ORDER BY id_sito
        """))
        return result.fetchall()
    finally:
        session.close()

def test_skip_strategy():
    """Test 'skip' strategy - conflicts should be skipped"""
    print("=" * 70)
    print("TEST 1: Skip Strategy")
    print("=" * 70)

    source_path, target_path = setup_test_databases()

    # Source data (IDs 1, 2, 3)
    source_sites = [
        {'id': 1, 'sito': 'Site A (SOURCE)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'This is from SOURCE'},
        {'id': 2, 'sito': 'Site B (SOURCE)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'Also from SOURCE'},
        {'id': 3, 'sito': 'Site C (NEW)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'New record from source'},
    ]

    # Target data (IDs 1, 2) - these will conflict
    target_sites = [
        {'id': 1, 'sito': 'Site A (TARGET)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'This is from TARGET'},
        {'id': 2, 'sito': 'Site B (TARGET)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'Also from TARGET'},
    ]

    insert_test_sites(source_path, source_sites)
    insert_test_sites(target_path, target_sites)

    print("\n🔍 Before migration:")
    print("   Source: 3 sites (IDs 1, 2, 3)")
    print("   Target: 2 sites (IDs 1, 2)")
    print("   Expected: ID 1,2 skipped, ID 3 added")

    # Migrate with skip strategy
    result = ImportExportService.migrate_database(
        source_db_url=f"sqlite:///{source_path}",
        target_db_url=f"sqlite:///{target_path}",
        create_target=False,
        auto_backup=False,
        merge_strategy='skip'
    )

    print("\n📊 Migration Results:")
    print(f"   Success: {result['success']}")
    print(f"   Rows copied: {result['total_rows_copied']}")

    # Verify results
    print("\n🔎 Verifying results...")
    target_sites_after = get_sites_from_db(target_path)

    print(f"\n   Target now has {len(target_sites_after)} sites:")
    for site in target_sites_after:
        print(f"      ID {site[0]}: {site[1]} - {site[2]}")

    # Cleanup
    os.remove(source_path)
    os.remove(target_path)

    # Verify expectations
    # Should have 3 sites: ID 1,2 from TARGET (not overwritten), ID 3 from SOURCE (new)
    success = (
        len(target_sites_after) == 3 and
        'TARGET' in str(target_sites_after[0]) and  # ID 1 should still be from TARGET
        'TARGET' in str(target_sites_after[1]) and  # ID 2 should still be from TARGET
        'NEW' in str(target_sites_after[2])  # ID 3 should be the new one
    )

    if success:
        print("\n✅ TEST PASSED: Skip strategy working correctly")
    else:
        print("\n❌ TEST FAILED: Skip strategy not working as expected")

    return success

def test_overwrite_strategy():
    """Test 'overwrite' strategy - conflicts should be updated"""
    print("\n" + "=" * 70)
    print("TEST 2: Overwrite Strategy")
    print("=" * 70)

    source_path, target_path = setup_test_databases()

    # Source data (IDs 1, 2, 3)
    source_sites = [
        {'id': 1, 'sito': 'Site A (SOURCE)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'This is from SOURCE'},
        {'id': 2, 'sito': 'Site B (SOURCE)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'Also from SOURCE'},
        {'id': 3, 'sito': 'Site C (NEW)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'New record from source'},
    ]

    # Target data (IDs 1, 2) - these will be overwritten
    target_sites = [
        {'id': 1, 'sito': 'Site A (TARGET)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'This is from TARGET'},
        {'id': 2, 'sito': 'Site B (TARGET)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'Also from TARGET'},
    ]

    insert_test_sites(source_path, source_sites)
    insert_test_sites(target_path, target_sites)

    print("\n🔍 Before migration:")
    print("   Source: 3 sites (IDs 1, 2, 3)")
    print("   Target: 2 sites (IDs 1, 2)")
    print("   Expected: ID 1,2 updated with SOURCE data, ID 3 added")

    # Migrate with overwrite strategy
    result = ImportExportService.migrate_database(
        source_db_url=f"sqlite:///{source_path}",
        target_db_url=f"sqlite:///{target_path}",
        create_target=False,
        auto_backup=False,
        merge_strategy='overwrite'
    )

    print("\n📊 Migration Results:")
    print(f"   Success: {result['success']}")
    print(f"   Rows copied: {result['total_rows_copied']}")

    # Verify results
    print("\n🔎 Verifying results...")
    target_sites_after = get_sites_from_db(target_path)

    print(f"\n   Target now has {len(target_sites_after)} sites:")
    for site in target_sites_after:
        print(f"      ID {site[0]}: {site[1]} - {site[2]}")

    # Cleanup
    os.remove(source_path)
    os.remove(target_path)

    # Verify expectations
    # Should have 3 sites: ID 1,2 from SOURCE (overwritten), ID 3 from SOURCE (new)
    success = (
        len(target_sites_after) == 3 and
        'SOURCE' in str(target_sites_after[0]) and  # ID 1 should now be from SOURCE
        'SOURCE' in str(target_sites_after[1]) and  # ID 2 should now be from SOURCE
        'NEW' in str(target_sites_after[2])  # ID 3 should be the new one
    )

    if success:
        print("\n✅ TEST PASSED: Overwrite strategy working correctly")
    else:
        print("\n❌ TEST FAILED: Overwrite strategy not working as expected")

    return success

def test_renumber_strategy():
    """Test 'renumber' strategy - conflicts should get new IDs"""
    print("\n" + "=" * 70)
    print("TEST 3: Renumber Strategy")
    print("=" * 70)

    source_path, target_path = setup_test_databases()

    # Source data (IDs 1, 2, 3)
    source_sites = [
        {'id': 1, 'sito': 'Site A (SOURCE)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'This is from SOURCE'},
        {'id': 2, 'sito': 'Site B (SOURCE)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'Also from SOURCE'},
        {'id': 3, 'sito': 'Site C (NEW)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'New record from source'},
    ]

    # Target data (IDs 1, 2) - source conflicts will be renumbered
    target_sites = [
        {'id': 1, 'sito': 'Site A (TARGET)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'This is from TARGET'},
        {'id': 2, 'sito': 'Site B (TARGET)', 'nazione': 'Italy', 'regione': 'Lazio',
         'comune': 'Rome', 'descrizione': 'Also from TARGET'},
    ]

    insert_test_sites(source_path, source_sites)
    insert_test_sites(target_path, target_sites)

    print("\n🔍 Before migration:")
    print("   Source: 3 sites (IDs 1, 2, 3)")
    print("   Target: 2 sites (IDs 1, 2)")
    print("   Expected: ID 1,2 from TARGET kept, SOURCE IDs 1,2 renumbered to 3,4, SOURCE ID 3 kept")

    # Migrate with renumber strategy
    result = ImportExportService.migrate_database(
        source_db_url=f"sqlite:///{source_path}",
        target_db_url=f"sqlite:///{target_path}",
        create_target=False,
        auto_backup=False,
        merge_strategy='renumber'
    )

    print("\n📊 Migration Results:")
    print(f"   Success: {result['success']}")
    print(f"   Rows copied: {result['total_rows_copied']}")

    # Verify results
    print("\n🔎 Verifying results...")
    target_sites_after = get_sites_from_db(target_path)

    print(f"\n   Target now has {len(target_sites_after)} sites:")
    for site in target_sites_after:
        print(f"      ID {site[0]}: {site[1]} - {site[2]}")

    # Cleanup
    os.remove(source_path)
    os.remove(target_path)

    # Verify expectations
    # Should have 5 sites total:
    # - ID 1,2 from TARGET (original)
    # - ID 3 from SOURCE (original, no conflict)
    # - ID 4,5 from SOURCE (renumbered from IDs 1,2)
    success = (
        len(target_sites_after) == 5 and
        'TARGET' in str(target_sites_after[0]) and  # ID 1 should be from TARGET
        'TARGET' in str(target_sites_after[1])   # ID 2 should be from TARGET
        # IDs 3, 4, 5 should all be from SOURCE
    )

    if success:
        print("\n✅ TEST PASSED: Renumber strategy working correctly")
    else:
        print("\n❌ TEST FAILED: Renumber strategy not working as expected")

    return success

def main():
    """Run all merge strategy tests"""
    print("\n" + "🧪" * 35)
    print("MERGE STRATEGY TESTS")
    print("🧪" * 35 + "\n")

    tests = [
        ("Skip Strategy", test_skip_strategy),
        ("Overwrite Strategy", test_overwrite_strategy),
        ("Renumber Strategy", test_renumber_strategy)
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
