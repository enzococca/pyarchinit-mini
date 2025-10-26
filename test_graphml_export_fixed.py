#!/usr/bin/env python3
"""
Test GraphML export with:
1. Fixed edge styling (Extended Matrix palette)
2. Graphviz tred for transitive reduction
"""

import sys
sys.path.insert(0, '/Users/enzo/Documents/pyarchinit-mini-desk')

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.services.us_service import USService

def test_graphml_export():
    """Test GraphML export with new features"""

    database_url = "sqlite:///./pyarchinit_mini.db"
    db_conn = DatabaseConnection.from_url(database_url)
    db_manager = DatabaseManager(db_conn)
    us_service = USService(db_manager)

    matrix_generator = HarrisMatrixGenerator(db_manager, us_service)

    site_name = "Scavo archeologico"
    output_path = "/Users/enzo/Desktop/test_harris_matrix_fixed.graphml"

    print("=" * 80)
    print("Testing GraphML Export with Fixed Edge Styling and tred")
    print("=" * 80)

    # Generate Harris Matrix graph
    print("\n1. Generating Harris Matrix graph...")
    graph = matrix_generator.generate_matrix(site_name)

    print(f"\n📊 Graph Statistics:")
    print(f"   - Nodes: {len(graph.nodes())}")
    print(f"   - Edges: {len(graph.edges())}")

    # Count edges by type
    from collections import Counter
    edge_types = Counter()
    for _, _, data in graph.edges(data=True):
        rel_type = data.get('relationship', 'unknown')
        edge_types[rel_type] += 1

    print(f"\n📊 Edge Types:")
    for edge_type, count in sorted(edge_types.items()):
        print(f"   - {edge_type}: {count}")

    # Check specific edges
    print(f"\n🔍 Checking specific edges:")
    for source, target, data in graph.edges(data=True):
        if 'US7' in str(source) and 'US2' in str(target):
            print(f"   - US7 -> US2: {data.get('relationship', 'unknown')}")
        if 'US13' in str(source) and 'US4' in str(target):
            print(f"   - US13 -> US4: {data.get('relationship', 'unknown')}")

    # Export to GraphML with extended labels and periodization
    print(f"\n2. Exporting to GraphML: {output_path}")
    result_path = matrix_generator.export_to_graphml(
        graph=graph,
        output_path=output_path,
        site_name=site_name,
        title=site_name,
        use_extended_labels=True,
        include_periods=True,
        reverse_epochs=False
    )

    if result_path:
        print(f"\n✅ Export completed: {result_path}")

        # Check if DOT files were created
        import os
        dot_path = output_path.replace('.graphml', '.dot')
        dot_tred_path = output_path.replace('.graphml', '_tred.dot')

        print(f"\n📁 Files created:")
        if os.path.exists(dot_path):
            size = os.path.getsize(dot_path) / 1024
            print(f"   - DOT file: {dot_path} ({size:.1f} KB)")
        if os.path.exists(dot_tred_path):
            size = os.path.getsize(dot_tred_path) / 1024
            print(f"   - DOT reduced (tred): {dot_tred_path} ({size:.1f} KB)")
        if os.path.exists(output_path):
            size = os.path.getsize(output_path) / 1024
            print(f"   - GraphML file: {output_path} ({size:.1f} KB)")

        print("\n✅ Test completed successfully!")
        print(f"\nOpen the file with yEd Graph Editor to verify:")
        print(f"   - Edge colors (black, red, blue, green, purple)")
        print(f"   - Edge styles (solid, dashed, dotted, bold)")
        print(f"   - Transitive reduction applied")

    else:
        print(f"\n❌ Export failed")
        return False

    return True

if __name__ == '__main__':
    test_graphml_export()
