#!/usr/bin/env python3
"""
Test script for Relationship Synchronization Service
=====================================================

Tests bidirectional synchronization between:
- us_table.rapporti field (text format)
- us_relationships_table (structured records)

This ensures the new synchronization service works correctly.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.services.site_service import SiteService
from pyarchinit_mini.services.relationship_sync_service import RelationshipSyncService
from pyarchinit_mini.models.harris_matrix import USRelationships
from pyarchinit_mini.models.us import US


def print_section(title):
    """Print section header"""
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print(f"{'=' * 70}\n")


def test_sync_service():
    """Test the relationship synchronization service"""

    # Use project database
    db_path = "/Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db"
    connection_string = f"sqlite:///{db_path}"

    print_section("Relationship Synchronization Service Test")
    print(f"Database: {db_path}\n")

    # Create services
    db_connection = DatabaseConnection(connection_string)
    db_manager = DatabaseManager(db_connection)
    us_service = USService(db_manager)
    site_service = SiteService(db_manager)
    sync_service = RelationshipSyncService(db_manager)

    # Test site
    test_site = "Test Sync Site"

    # Clean up any existing test data
    print("Cleaning up existing test data...")
    with db_manager.connection.get_session() as session:
        # Delete test US relationships
        session.query(USRelationships).filter_by(sito=test_site).delete()
        # Delete test US
        session.query(US).filter_by(sito=test_site).delete()

    # Create test site if it doesn't exist
    try:
        site_service.create_site({'sito': test_site})
        print(f"✓ Created test site: {test_site}\n")
    except Exception as e:
        print(f"Test site already exists (OK)\n")

    # ======================================================================
    # TEST 1: rapporti field → us_relationships_table
    # ======================================================================
    print_section("TEST 1: Sync rapporti field → us_relationships_table")

    # Create US with rapporti field
    us1_data = {
        'id_us': f'{test_site}___{1}',  # Required format: site__area__us_number
        'sito': test_site,
        'area': '',
        'us': 1,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Test US 1',
        'rapporti': 'Copre 2, Taglia 3, Coperto da 4'
    }

    us1 = us_service.create_us(us1_data)
    us1_id_us = us1_data['id_us']  # Save the id_us directly from data
    print(f"✓ Created US 1 with rapporti: '{us1_data['rapporti']}'")

    # Sync rapporti to relationships table
    with db_manager.connection.get_session() as session:
        result = sync_service.sync_rapporti_to_relationships_table(
            sito=test_site,
            us_number=1,
            rapporti_text=us1_data['rapporti'],
            session=session
        )

    print(f"✓ Sync result: deleted={result['deleted']}, created={result['created']}")

    # Verify relationships were created
    with db_manager.connection.get_session() as session:
        relationships = session.query(USRelationships).filter_by(
            sito=test_site,
            us_from=1
        ).all()

        print(f"\n✓ Found {len(relationships)} relationships in us_relationships_table:")
        for rel in relationships:
            print(f"  - US {rel.us_from} {rel.relationship_type} US {rel.us_to}")

        assert len(relationships) == 3, f"Expected 3 relationships, found {len(relationships)}"
        print(f"\n✓ TEST 1 PASSED: rapporti → us_relationships_table works correctly")

    # ======================================================================
    # TEST 2: us_relationships_table → rapporti field
    # ======================================================================
    print_section("TEST 2: Sync us_relationships_table → rapporti field")

    # Create US 2 without rapporti
    us2_data = {
        'id_us': f'{test_site}___{2}',
        'sito': test_site,
        'area': '',
        'us': 2,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Test US 2',
        'rapporti': ''
    }

    us2 = us_service.create_us(us2_data)
    us2_id_us = us2_data['id_us']  # Save the id_us directly from data
    print(f"✓ Created US 2 with empty rapporti")

    # Add relationships directly to us_relationships_table
    with db_manager.connection.get_session() as session:
        rel1 = USRelationships(
            sito=test_site,
            us_from=2,
            us_to=5,
            relationship_type='Copre'
        )
        rel2 = USRelationships(
            sito=test_site,
            us_from=2,
            us_to=6,
            relationship_type='Taglia'
        )
        session.add_all([rel1, rel2])

    print(f"✓ Added 2 relationships to us_relationships_table")

    # Sync relationships table to rapporti field
    with db_manager.connection.get_session() as session:
        rapporti_text = sync_service.sync_relationships_table_to_rapporti(
            sito=test_site,
            us_number=2,
            session=session
        )

    print(f"✓ Generated rapporti text: '{rapporti_text}'")

    # Update US with generated rapporti
    us_service.update_us(us2_id_us, {'rapporti': rapporti_text})

    # Verify rapporti field was updated
    with db_manager.connection.get_session() as session:
        updated_us = session.query(US).filter_by(sito=test_site, us=2).first()
        print(f"\n✓ US 2 rapporti field: '{updated_us.rapporti}'")

        assert updated_us.rapporti == rapporti_text
        assert 'Copre 5' in updated_us.rapporti
        assert 'Taglia 6' in updated_us.rapporti
        print(f"\n✓ TEST 2 PASSED: us_relationships_table → rapporti works correctly")

    # ======================================================================
    # TEST 3: Update rapporti field and verify sync
    # ======================================================================
    print_section("TEST 3: Update rapporti field and verify sync")

    # Update US 1 rapporti field
    new_rapporti = 'Copre 2, Copre 7, Uguale a 8'
    us_service.update_us(us1_id_us, {'rapporti': new_rapporti})
    print(f"✓ Updated US 1 rapporti to: '{new_rapporti}'")

    # Sync to relationships table
    with db_manager.connection.get_session() as session:
        result = sync_service.sync_rapporti_to_relationships_table(
            sito=test_site,
            us_number=1,
            rapporti_text=new_rapporti,
            session=session
        )

    print(f"✓ Sync result: deleted={result['deleted']}, created={result['created']}")

    # Verify relationships were updated
    with db_manager.connection.get_session() as session:
        relationships = session.query(USRelationships).filter_by(
            sito=test_site,
            us_from=1
        ).all()

        print(f"\n✓ Found {len(relationships)} relationships after update:")
        for rel in relationships:
            print(f"  - US {rel.us_from} {rel.relationship_type} US {rel.us_to}")

        assert len(relationships) == 3, f"Expected 3 relationships, found {len(relationships)}"

        # Check specific relationships
        rel_types = [(r.relationship_type, r.us_to) for r in relationships]
        assert ('Copre', 2) in rel_types
        assert ('Copre', 7) in rel_types
        assert ('Uguale a', 8) in rel_types

        print(f"\n✓ TEST 3 PASSED: Update and sync works correctly")

    # ======================================================================
    # TEST 4: Parse various rapporti formats
    # ======================================================================
    print_section("TEST 4: Parse various rapporti formats")

    test_cases = [
        ('Copre 1, Copre 2, Taglia 3', 3),
        ('Coperto da 5, Tagliato da 6', 2),
        ('Copre 10', 1),
        ('Si appoggia a 20, Uguale a 21, Riempie 22', 3),
        ('', 0),
    ]

    for rapporti, expected_count in test_cases:
        parsed = sync_service.parse_rapporti_field(rapporti)
        print(f"  '{rapporti}' → {len(parsed)} relationships")
        assert len(parsed) == expected_count, f"Expected {expected_count}, got {len(parsed)}"

    print(f"\n✓ TEST 4 PASSED: All rapporti formats parsed correctly")

    # ======================================================================
    # TEST 5: Full synchronization of a site
    # ======================================================================
    print_section("TEST 5: Full site synchronization")

    # Create multiple US with rapporti
    for i in range(10, 15):
        us_data = {
            'id_us': f'{test_site}___{i}',
            'sito': test_site,
            'area': '',
            'us': i,
            'unita_tipo': 'US',
            'd_stratigrafica': f'Test US {i}',
            'rapporti': f'Copre {i+1}, Coperto da {i-1}'
        }
        us_service.create_us(us_data)

    print(f"✓ Created 5 test US (10-14)")

    # Sync entire site
    result = sync_service.sync_all_site_us(test_site)

    print(f"\n✓ Full site sync result:")
    print(f"  - US processed: {result['us_processed']}")
    print(f"  - Relationships deleted: {result['total_relationships_deleted']}")
    print(f"  - Relationships created: {result['total_relationships_created']}")

    assert result['us_processed'] >= 7  # US 1, 2, and 10-14

    print(f"\n✓ TEST 5 PASSED: Full site synchronization works correctly")

    # ======================================================================
    # Summary
    # ======================================================================
    print_section("TEST SUMMARY")

    print("✓ All tests passed successfully!")
    print("\nVerified functionality:")
    print("  1. rapporti field → us_relationships_table synchronization")
    print("  2. us_relationships_table → rapporti field synchronization")
    print("  3. Update and re-sync behavior")
    print("  4. Various rapporti format parsing")
    print("  5. Full site synchronization")

    print("\n" + "=" * 70)
    print("Bidirectional synchronization is working correctly!")
    print("=" * 70)


if __name__ == '__main__':
    try:
        test_sync_service()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
