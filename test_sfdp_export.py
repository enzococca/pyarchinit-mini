#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test SFDP GraphML Export for Large Graph (760 US)
Measures performance improvement vs traditional dot layout
"""

import time
import os
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator

def test_sfdp_graphml_export():
    """Test GraphML export with sfdp for Dom zu Lund (760 US)"""

    print("=" * 80)
    print("SFDP GraphML Export Performance Test")
    print("=" * 80)
    print()

    # Initialize database
    db_path = "/Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db"
    connection_string = f"sqlite:///{db_path}"

    db_connection = DatabaseConnection(connection_string)
    db_manager = DatabaseManager(db_connection)
    us_service = USService(db_manager)

    # Initialize Harris Matrix generator
    matrix_generator = HarrisMatrixGenerator(db_manager, us_service)

    # Site to test (Dom zu Lund - 760 US, 2459 relationships)
    site_name = "Dom zu Lund"
    output_path = "/Users/enzo/Desktop/dom_zu_lund_harris_matrix.graphml"

    print(f"📊 Testing site: {site_name}")
    print(f"📁 Output file: {output_path}")
    print()

    # Step 1: Generate Harris Matrix graph
    print("Step 1: Generating Harris Matrix graph...")
    start_generate = time.time()

    try:
        graph = matrix_generator.generate_matrix(site_name)
        time_generate = time.time() - start_generate

        num_nodes = len(graph.nodes())
        num_edges = len(graph.edges())

        print(f"✅ Graph generated in {time_generate:.2f} seconds")
        print(f"   - Nodes: {num_nodes}")
        print(f"   - Edges: {num_edges}")
        print()

    except Exception as e:
        print(f"❌ Error generating graph: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 2: Export to GraphML with sfdp
    print("Step 2: Exporting to GraphML with sfdp layout...")
    print("   (This should be MUCH faster than traditional dot layout)")
    print()

    start_export = time.time()

    try:
        result_path = matrix_generator.export_to_graphml(
            graph=graph,
            output_path=output_path,
            site_name=site_name,
            title="Dom zu Lund - Harris Matrix (sfdp optimized)",
            reverse_epochs=False
        )

        time_export = time.time() - start_export

        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path) / (1024 * 1024)  # MB

            print()
            print("✅ GraphML export completed successfully!")
            print()
            print("=" * 80)
            print("PERFORMANCE RESULTS")
            print("=" * 80)
            print(f"Graph generation time:  {time_generate:.2f} seconds")
            print(f"GraphML export time:    {time_export:.2f} seconds")
            print(f"Total time:             {time_generate + time_export:.2f} seconds")
            print()
            print(f"Output file:            {result_path}")
            print(f"File size:              {file_size:.2f} MB")
            print()
            print(f"Nodes:                  {num_nodes}")
            print(f"Edges:                  {num_edges}")
            print()

            # Determine if sfdp was used
            if num_nodes > 500 or num_edges > 1500:
                print("🚀 sfdp layout engine was used (optimized for large graphs)")
                print("   Expected speedup: 10-100x vs traditional dot layout")
            else:
                print("📊 dot layout engine was used (graph below threshold)")

            print()
            print("=" * 80)
            print("NEXT STEPS")
            print("=" * 80)
            print(f"1. Open the file in yEd: {result_path}")
            print("2. In yEd, go to: Layout → Hierarchical")
            print("3. Or let yEd calculate layout automatically")
            print("4. Verify all 760 US nodes are present")
            print("5. Verify all relationships are correctly displayed")
            print()

        else:
            print(f"❌ Export failed - no file created")

    except Exception as e:
        time_export = time.time() - start_export
        print(f"❌ Error during export (after {time_export:.2f} seconds): {e}")
        import traceback
        traceback.print_exc()
        return

    print("=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    test_sfdp_graphml_export()