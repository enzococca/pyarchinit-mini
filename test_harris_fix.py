#!/usr/bin/env python3
"""
Test script to verify Harris Matrix relationship fix
"""

import sys
sys.path.append('.')

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.services.us_service import USService
from sqlalchemy import text

def test_harris_matrix_fix():
    """Test that Harris Matrix can read relationships from us_relationships_table"""

    print("=" * 70)
    print("TESTING HARRIS MATRIX RELATIONSHIP FIX")
    print("=" * 70)

    # Initialize database
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///./pyarchinit_mini.db')

    # Create simple db_manager object
    class SimpleDBManager:
        def __init__(self, engine):
            self.engine = engine

    db_manager = SimpleDBManager(engine)

    # Initialize Harris generator without US service (will use db query directly)
    harris_generator = HarrisMatrixGenerator(db_manager, us_service=None)

    # Get list of sites with relationships
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Find sites with relationships
        result = session.execute(text("""
            SELECT sito, COUNT(*) as rel_count
            FROM us_relationships_table
            GROUP BY sito
            ORDER BY rel_count DESC
            LIMIT 3
        """))
        sites_with_rels = result.fetchall()

        if not sites_with_rels:
            print("\n⚠️  No relationships found in database!")
            print("Please import data first using the web interface.")
            return

        print(f"\nFound {len(sites_with_rels)} sites with relationships:")
        for site in sites_with_rels:
            print(f"  - {site.sito}: {site.rel_count} relationships")

        # Test matrix generation for first site
        test_site = sites_with_rels[0].sito
        expected_rels = sites_with_rels[0].rel_count

        print(f"\n" + "=" * 70)
        print(f"Testing Harris Matrix generation for: {test_site}")
        print(f"Expected relationships: {expected_rels}")
        print("=" * 70)

        # Generate matrix
        graph = harris_generator.generate_matrix(test_site)

        # Check results
        nodes_count = len(graph.nodes())
        edges_count = len(graph.edges())

        print(f"\nGeneration Results:")
        print(f"  Nodes (US): {nodes_count}")
        print(f"  Edges (Relationships): {edges_count}")

        if edges_count > 0:
            print(f"\n✅ SUCCESS! Harris Matrix is reading relationships from us_relationships_table!")
            print(f"\nSample relationships in graph:")
            for i, (us_from, us_to, data) in enumerate(list(graph.edges(data=True))[:5]):
                rel_type = data.get('relationship', 'unknown')
                print(f"  {i+1}. US {us_from} --[{rel_type}]--> US {us_to}")

            if edges_count < expected_rels:
                print(f"\n⚠️  Note: Graph has {edges_count} edges but database has {expected_rels} relationships")
                print("   This is normal - transitive reduction removes redundant edges.")
        else:
            print(f"\n❌ FAILED! No relationships in graph despite {expected_rels} in database!")
            print("\nPossible causes:")
            print("1. Relationship types not recognized (check valid_relationships list)")
            print("2. Query failed (check logs above)")

        print("\n" + "=" * 70)
        print("TEST COMPLETED")
        print("=" * 70)

        # Show what to do next
        if edges_count > 0:
            print("\n✅ Next steps:")
            print("1. Restart Flask web server")
            print("2. Go to Harris Matrix page")
            print(f"3. Select site: {test_site}")
            print("4. Click Generate Matrix")
            print("5. You should see the relationships visualized!")
        else:
            print("\n⚠️  Next steps:")
            print("1. Check the server logs when generating the matrix")
            print("2. Look for messages about relationship types")
            print("3. Report any errors you see")

    finally:
        session.close()

if __name__ == "__main__":
    test_harris_matrix_fix()
