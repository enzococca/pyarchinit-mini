#!/usr/bin/env python3
"""
Test GraphML auto-generation from US rapporti field
"""

import os
import sys

# Set database URL
os.environ['DATABASE_URL'] = 'sqlite:///data/pyarchinit_tutorial.db'

# Add project root to path
sys.path.insert(0, '/Users/enzo/Documents/pyarchinit-mini-desk')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.services.us_service import USService

def test_graphml_generation():
    print("="*80)
    print("Testing GraphML Auto-Generation")
    print("="*80)

    # Create database session directly
    db_url = os.environ.get('DATABASE_URL')
    # Convert sqlite:/// to absolute path
    db_url = db_url.replace('sqlite:///', 'sqlite:////Users/enzo/Documents/pyarchinit-mini-desk/')
    print(f"\nDatabase: {db_url}")

    # Create engine and session
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create database connection and manager
        db_connection = DatabaseConnection(db_url)
        db_manager = DatabaseManager(db_connection)

        # Create US service
        us_service = USService(db_manager)

        # Create matrix generator WITH us_service
        print("\nCreating HarrisMatrixGenerator...")
        matrix_generator = HarrisMatrixGenerator(db_manager, us_service=us_service)

        # Generate matrix for site
        site_name = "Roman Forum Excavation"
        print(f"\nGenerating Harris Matrix for site: {site_name}")

        graph = matrix_generator.generate_matrix(site_name)

        print(f"\nGenerated graph:")
        print(f"  - Nodes: {len(graph.nodes())}")
        print(f"  - Edges: {len(graph.edges())}")

        # Show nodes
        print(f"\nNodes:")
        for node_id, node_data in graph.nodes(data=True):
            print(f"  - {node_id}: {node_data.get('label', '')}")

        # Show edges (relationships)
        print(f"\nEdges (relationships):")
        for source, target, edge_data in graph.edges(data=True):
            rel_type = edge_data.get('relationship', 'unknown')
            print(f"  - US {source} → {rel_type} → US {target}")

        # Export to GraphML
        output_path = '/tmp/test_harris_matrix.graphml'
        print(f"\nExporting to GraphML: {output_path}")

        result_path = matrix_generator.export_to_graphml(
            graph=graph,
            output_path=output_path,
            site_name=site_name,
            title="Roman Forum - Auto-generated Test",
            use_graphviz=False  # Use pure NetworkX (no Graphviz required)
        )

        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"\n✅ SUCCESS! GraphML generated:")
            print(f"   Path: {result_path}")
            print(f"   Size: {file_size} bytes")

            # Show first few lines
            print(f"\nFirst 20 lines of GraphML:")
            with open(result_path, 'r') as f:
                for i, line in enumerate(f):
                    if i >= 20:
                        break
                    print(f"   {line.rstrip()}")
        else:
            print(f"\n❌ FAILED: GraphML not generated")

        print("\n" + "="*80)
        print("Test Complete")
        print("="*80)

    finally:
        session.close()

if __name__ == '__main__':
    test_graphml_generation()
