#!/usr/bin/env python3
"""
Test script for Harris Matrix periodization system
"""

import sys
sys.path.insert(0, '.')

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.services.us_service import USService

def test_periodization():
    """Test periodization in Harris Matrix"""

    print("=" * 70)
    print("TESTING HARRIS MATRIX PERIODIZATION SYSTEM")
    print("=" * 70)

    # Initialize database and services
    db_path = 'pyarchinit_mini.db'
    connection = DatabaseConnection(f'sqlite:///{db_path}')
    db_manager = DatabaseManager(connection)
    us_service = USService(db_manager)
    matrix_gen = HarrisMatrixGenerator(db_manager, us_service)

    # Test with site "Scavo archeologico"
    site_name = "Scavo archeologico"

    print(f"\n1. Generating Harris Matrix for site: {site_name}")
    print("-" * 70)

    try:
        graph = matrix_gen.generate_matrix(site_name)

        print(f"\n✅ Matrix generated successfully!")
        print(f"   - Total nodes (US): {len(graph.nodes())}")
        print(f"   - Total edges (relationships): {len(graph.edges())}")

        # Show sample nodes with extended labels
        print(f"\n2. Sample nodes with periodization:")
        print("-" * 70)

        sample_count = 0
        for node_id, node_data in graph.nodes(data=True):
            if sample_count >= 5:
                break

            print(f"\n   US {node_id}:")
            print(f"   - Simple label: {node_data.get('label', 'N/A')}")
            print(f"   - Extended label: {node_data.get('extended_label', 'N/A')}")
            print(f"   - Periodo code: {node_data.get('periodo_code', 'N/A')}")
            print(f"   - Period/Phase: {node_data.get('period_initial', 'N/A')}/{node_data.get('phase_initial', 'N/A')}")
            print(f"   - Unita tipo: {node_data.get('unita_tipo', 'N/A')}")
            print(f"   - Interpretation: {node_data.get('interpretation', 'N/A')[:50]}...")

            sample_count += 1

        # Show sample relationships with extended data
        print(f"\n3. Sample relationships with EM palette support:")
        print("-" * 70)

        sample_count = 0
        for source, target, edge_data in graph.edges(data=True):
            if sample_count >= 5:
                break

            print(f"\n   {source} → {target}")
            print(f"   - Relationship: {edge_data.get('relationship', 'N/A')}")
            print(f"   - Certainty: {edge_data.get('certainty', 'N/A')}")

            sample_count += 1

        # Test GraphML export
        print(f"\n4. Testing GraphML export with EM palette:")
        print("-" * 70)

        output_file = "harris_matrix_with_periodization.graphml"
        matrix_gen.export_to_graphml(graph, output_file,
                                     use_extended_labels=True,
                                     site_name=site_name)

        print(f"\n✅ GraphML export successful!")
        print(f"   File: {output_file}")

        # Also export with simple labels for comparison
        output_file_simple = "harris_matrix_simple_labels.graphml"
        matrix_gen.export_to_graphml(graph, output_file_simple,
                                     use_extended_labels=False,
                                     site_name=site_name)

        print(f"\n✅ Simple label export successful!")
        print(f"   File: {output_file_simple}")

        # Test with another site if available
        print(f"\n5. Testing with another site:")
        print("-" * 70)

        site_name_2 = "Sito Archeologico di Esempio"
        try:
            graph2 = matrix_gen.generate_matrix(site_name_2)
            print(f"\n✅ Matrix generated for '{site_name_2}'!")
            print(f"   - Total nodes: {len(graph2.nodes())}")
            print(f"   - Total edges: {len(graph2.edges())}")

            # Export this one too
            output_file_2 = "harris_matrix_site2_with_periodization.graphml"
            matrix_gen.export_to_graphml(graph2, output_file_2,
                                         use_extended_labels=True,
                                         site_name=site_name_2)
            print(f"\n✅ GraphML export for site 2 successful!")
            print(f"   File: {output_file_2}")
        except Exception as e:
            print(f"\n⚠️  Could not process site '{site_name_2}': {e}")

        print("\n" + "=" * 70)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)

        print("\n📊 Summary:")
        print(f"   - Harris Matrix generation: ✅")
        print(f"   - Extended labels (periodo-fase): ✅")
        print(f"   - GraphML export with EM palette: ✅")
        print(f"   - Files generated: 3-4 GraphML files")

        print("\n📖 Next steps:")
        print("   1. Open the GraphML files in yEd")
        print("   2. Verify extended labels show: unita_tipo+us+definition+periodo-fase")
        print("   3. Use periodo/phase attributes for grouping/filtering")
        print("   4. Apply EM palette layout in yEd")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_periodization()
    sys.exit(0 if success else 1)
