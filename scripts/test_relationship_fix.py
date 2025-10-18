#!/usr/bin/env python3
"""
Test script for relationship fix functionality
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.site_service import SiteService
from pyarchinit_mini.services.us_service import USService

def test_relationship_fix():
    """Test the relationship fix functionality"""
    
    # Create test database
    db_path = os.path.join(project_root, 'test_fix.db')
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create new database
    db_conn = DatabaseConnection(f'sqlite:///{db_path}')
    db_conn.create_tables()
    
    db_manager = DatabaseManager(db_conn)
    site_service = SiteService(db_manager)
    us_service = USService(db_manager)
    
    print("Testing relationship fix functionality...")
    
    # Create test site
    site = site_service.create_site({
        'sito': 'Test Fix Site',
        'comune': 'Roma',
        'provincia': 'RM',
        'regione': 'Lazio',
        'nazione': 'Italia'
    })
    print("Created test site")
    
    # Create US with missing reciprocal relationships
    us1 = us_service.create_us({
        'sito': 'Test Fix Site',
        'area': 'A',
        'us': 1,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Strato superficiale',
        'rapporti': 'copre 2, 3; taglia 4',  # US 3 and 4 don't exist
        'scavato': 'yes',
        'anno_scavo': 2024
    })
    
    us2 = us_service.create_us({
        'sito': 'Test Fix Site',
        'area': 'A',
        'us': 2,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Strato di accumulo',
        'rapporti': '',  # Missing reciprocal "coperto da 1"
        'scavato': 'yes',
        'anno_scavo': 2024
    })
    
    print("Created test US with missing relationships")
    
    # Generate fixes
    fixes = us_service.generate_relationship_fixes('Test Fix Site')
    
    print(f"\nGenerated fixes:")
    print(f"- Updates needed: {len(fixes['updates'])}")
    print(f"- US to create: {len(fixes['creates'])}")
    
    # Print fix details
    print("\nUpdate details:")
    for update in fixes['updates']:
        print(f"  US {update['us']}: Add '{update['new_value']}' (reason: {update['reason']})")
    
    print("\nCreate details:")
    for create in fixes['creates']:
        print(f"  New US {create['us']}: {create['d_stratigrafica']} (reason: {create['reason']})")
    
    # Apply fixes
    results = us_service.apply_relationship_fixes(fixes, apply_creates=True)
    
    print(f"\nFix results:")
    print(f"- Updated: {results['updated']}")
    print(f"- Created: {results['created']}")
    if results['errors']:
        print(f"- Errors: {results['errors']}")
    
    # Verify fixes
    print("\nVerifying fixes...")
    
    # Check US 2 now has reciprocal relationship
    # Need to find US 2's ID by searching
    us2_list = us_service.get_all_us(filters={'sito': 'Test Fix Site', 'us': 2})
    if us2_list:
        us2_after = us2_list[0]
        print(f"US 2 rapporti after fix: '{us2_after.rapporti}'")
    
    # Check that US 3 and 4 were created
    us_list = us_service.get_us_by_site('Test Fix Site', page=1, size=100)
    us_numbers = [us.us for us in us_list]
    print(f"US in database: {sorted(us_numbers)}")
    
    # Test validation after fix
    print("\nValidating after fix...")
    report = us_service.validate_stratigraphic_paradoxes('Test Fix Site')
    print(f"Validation result: {'Valid' if report['valid'] else 'Has errors'}")
    if not report['valid']:
        for error in report['errors']:
            print(f"  - {error}")
    
    # Clean up
    db_conn.close()
    os.remove(db_path)
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_relationship_fix()