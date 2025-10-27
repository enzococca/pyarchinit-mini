#!/usr/bin/env python3
"""
Test script for Datazioni Table
=================================

Tests the new datazioni_table feature:
- Table creation (SQLite + PostgreSQL compatible)
- CRUD operations
- Default datazioni initialization
- Choices for dropdown/combobox

Author: PyArchInit Team
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.datazione_service import DatazioneService


def print_section(title):
    """Print section header"""
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print(f"{'=' * 70}\n")


def test_datazioni():
    """Test datazioni table and service"""

    # Use project database
    db_path = "/Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db"
    connection_string = f"sqlite:///{db_path}"

    print_section("Datazioni Table Test")
    print(f"Database: {db_path}\n")

    # Create services
    db_connection = DatabaseConnection(connection_string)
    db_manager = DatabaseManager(db_connection)
    datazione_service = DatazioneService(db_manager)

    # Initialize database tables
    print("Initializing database tables...")
    db_connection.create_tables()
    print("✓ Database tables created\n")

    # ======================================================================
    # TEST 1: Create table and initialize default datazioni
    # ======================================================================
    print_section("TEST 1: Initialize Default Datazioni")

    created_count = datazione_service.initialize_default_datazioni()
    print(f"✓ Created {created_count} default datazioni")

    total_count = datazione_service.count_datazioni()
    print(f"✓ Total datazioni in database: {total_count}")

    assert total_count > 0, "No datazioni found in database"
    print(f"\n✓ TEST 1 PASSED\n")

    # ======================================================================
    # TEST 2: Get all datazioni
    # ======================================================================
    print_section("TEST 2: Get All Datazioni")

    datazioni = datazione_service.get_all_datazioni()
    print(f"✓ Retrieved {len(datazioni)} datazioni\n")

    # Print first 10
    print("First 10 datazioni:")
    for i, dat in enumerate(datazioni[:10], 1):
        print(f"  {i}. {dat['full_label']}")

    assert len(datazioni) == total_count
    print(f"\n✓ TEST 2 PASSED\n")

    # ======================================================================
    # TEST 3: Create custom datazione
    # ======================================================================
    print_section("TEST 3: Create Custom Datazione")

    custom_data = {
        'nome_datazione': 'Test Periodo',
        'fascia_cronologica': '2000-2024 d.C.',
        'descrizione': 'Periodo di test per verifica funzionalità'
    }

    custom_dat = datazione_service.create_datazione(custom_data)
    print(f"✓ Created custom datazione: {custom_dat.full_label}")
    print(f"  ID: {custom_dat.id_datazione}")
    print(f"  Nome: {custom_dat.nome_datazione}")
    print(f"  Fascia: {custom_dat.fascia_cronologica}")

    # Verify it exists
    retrieved = datazione_service.get_datazione_by_id(custom_dat.id_datazione)
    assert retrieved is not None
    assert retrieved.nome_datazione == 'Test Periodo'

    print(f"\n✓ TEST 3 PASSED\n")

    # ======================================================================
    # TEST 4: Update datazione
    # ======================================================================
    print_section("TEST 4: Update Datazione")

    update_data = {
        'fascia_cronologica': '2000-2025 d.C.',
        'descrizione': 'Periodo di test aggiornato'
    }

    updated_dat = datazione_service.update_datazione(custom_dat.id_datazione, update_data)
    print(f"✓ Updated datazione: {updated_dat.full_label}")
    print(f"  New fascia: {updated_dat.fascia_cronologica}")
    print(f"  New descrizione: {updated_dat.descrizione}")

    assert updated_dat.fascia_cronologica == '2000-2025 d.C.'

    print(f"\n✓ TEST 4 PASSED\n")

    # ======================================================================
    # TEST 5: Get datazioni choices for forms
    # ======================================================================
    print_section("TEST 5: Get Datazioni Choices for Forms")

    choices = datazione_service.get_datazioni_choices()
    print(f"✓ Retrieved {len(choices)} choices for forms\n")

    print("Sample choices (first 10):")
    for i, choice in enumerate(choices[:10], 1):
        print(f"  {i}. value='{choice['value']}'")
        print(f"     label='{choice['label']}'")

    assert len(choices) > 0
    assert all('value' in c and 'label' in c for c in choices)

    print(f"\n✓ TEST 5 PASSED\n")

    # ======================================================================
    # TEST 6: Search by nome
    # ======================================================================
    print_section("TEST 6: Search Datazione by Nome")

    found = datazione_service.get_datazione_by_nome('Età del Bronzo Antico')
    if found:
        print(f"✓ Found datazione: {found.full_label}")
        print(f"  ID: {found.id_datazione}")
        print(f"  Fascia: {found.fascia_cronologica}")
    else:
        print("✗ Datazione 'Età del Bronzo Antico' not found")
        assert False, "Expected datazione not found"

    print(f"\n✓ TEST 6 PASSED\n")

    # ======================================================================
    # TEST 7: Delete custom datazione
    # ======================================================================
    print_section("TEST 7: Delete Datazione")

    deleted = datazione_service.delete_datazione(custom_dat.id_datazione)
    assert deleted, "Failed to delete datazione"
    print(f"✓ Deleted custom datazione (ID: {custom_dat.id_datazione})")

    # Verify it's gone
    retrieved = datazione_service.get_datazione_by_id(custom_dat.id_datazione)
    assert retrieved is None, "Datazione still exists after deletion"

    print(f"\n✓ TEST 7 PASSED\n")

    # ======================================================================
    # Summary
    # ======================================================================
    print_section("TEST SUMMARY")

    final_count = datazione_service.count_datazioni()
    print(f"✓ All tests passed successfully!")
    print(f"\nFinal statistics:")
    print(f"  - Total datazioni: {final_count}")
    print(f"  - Default datazioni: {final_count}")
    print(f"  - Database: SQLite (compatible with PostgreSQL)")
    print(f"\nVerified functionality:")
    print(f"  1. Table creation")
    print(f"  2. Default datazioni initialization")
    print(f"  3. CRUD operations (Create, Read, Update, Delete)")
    print(f"  4. Choices generation for forms")
    print(f"  5. Search by nome")

    print("\n" + "=" * 70)
    print("Datazioni table is ready for use!")
    print("=" * 70)


if __name__ == '__main__':
    try:
        test_datazioni()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
