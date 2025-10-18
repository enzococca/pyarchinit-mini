#!/usr/bin/env python3
"""
Test script per verificare la cancellazione a cascata
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.models.us import US
from pyarchinit_mini.models.inventario_materiali import InventarioMateriali
from pyarchinit_mini.models.harris_matrix import HarrisMatrix, USRelationships

def test_cascade_deletion():
    """Test cascade deletion functionality"""
    
    # Connect to sample database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          'data', 'pyarchinit_mini_sample.db')
    
    if not os.path.exists(db_path):
        print("Error: Sample database not found. Run populate_simple_data.py first.")
        return
    
    db_connection = DatabaseConnection.sqlite(db_path)
    
    print("TESTING CASCADE DELETION")
    print("=" * 50)
    
    # Count records before deletion
    with db_connection.get_session() as session:
        sites_count = session.query(Site).count()
        us_count = session.query(US).count()
        materials_count = session.query(InventarioMateriali).count()
        harris_count = session.query(HarrisMatrix).count()
        relations_count = session.query(USRelationships).count()
        
        print(f"Records BEFORE deletion:")
        print(f"  Sites: {sites_count}")
        print(f"  US: {us_count}")
        print(f"  Materials: {materials_count}")
        print(f"  Harris Matrix: {harris_count}")
        print(f"  US Relationships: {relations_count}")
        
        # Find the sample site
        site = session.query(Site).filter(Site.sito == "Sito Archeologico di Esempio").first()
        if not site:
            print("Error: Sample site not found")
            return
        
        print(f"\nDeleting site: {site.sito}")
        session.delete(site)
        session.commit()
        
        # Count records after deletion
        sites_count_after = session.query(Site).count()
        us_count_after = session.query(US).count()
        materials_count_after = session.query(InventarioMateriali).count()
        harris_count_after = session.query(HarrisMatrix).count()
        relations_count_after = session.query(USRelationships).count()
        
        print(f"\nRecords AFTER deletion:")
        print(f"  Sites: {sites_count_after}")
        print(f"  US: {us_count_after}")
        print(f"  Materials: {materials_count_after}")
        print(f"  Harris Matrix: {harris_count_after}")
        print(f"  US Relationships: {relations_count_after}")
        
        print(f"\nDeleted records:")
        print(f"  Sites: {sites_count - sites_count_after}")
        print(f"  US: {us_count - us_count_after}")
        print(f"  Materials: {materials_count - materials_count_after}")
        print(f"  Harris Matrix: {harris_count - harris_count_after}")
        print(f"  US Relationships: {relations_count - relations_count_after}")
        
        # Test results
        if (sites_count_after == 0 and us_count_after == 0 and 
            materials_count_after == 0 and harris_count_after == 0 and 
            relations_count_after == 0):
            print("\n✓ CASCADE DELETION SUCCESSFUL!")
            print("All related records were automatically deleted when the site was removed.")
        else:
            print("\n✗ CASCADE DELETION FAILED!")
            print("Some records were not deleted automatically.")

if __name__ == "__main__":
    test_cascade_deletion()