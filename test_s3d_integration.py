#!/usr/bin/env python3
"""
Test s3Dgraphy integration with JSON v1.5 export
"""

import json
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

def test_s3d_converter_import():
    """Test that S3DConverter can be imported"""
    print("Testing S3DConverter import...")
    try:
        from pyarchinit_mini.s3d_integration import S3DConverter
        print("✓ S3DConverter imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import S3DConverter: {e}")
        return False

def test_json_export_format():
    """Test JSON export creates correct v1.5 structure"""
    print("\nTesting JSON export format...")
    try:
        from pyarchinit_mini.s3d_integration import S3DConverter

        # Create sample US data
        us_data = [
            {
                'us': 1,
                'sito': 'Test Site',
                'area': 'A',
                'unita_tipo': 'US',
                'd_stratigrafica': 'Test stratigraphic description',
                'd_interpretativa': 'Test interpretive description',
                'interpretazione': 'Layer',
                'anno_scavo': 2025,
                'scavato': 'Yes',
                'periodo_iniziale': 'Modern Period',
                'fase_iniziale': 1,
                'rapporti': 'copre 2'
            },
            {
                'us': 2,
                'sito': 'Test Site',
                'area': 'A',
                'unita_tipo': 'US',
                'd_stratigrafica': 'Test description 2',
                'd_interpretativa': 'Test interpretation 2',
                'interpretazione': 'Layer',
                'anno_scavo': 2025,
                'scavato': 'Yes',
                'periodo_iniziale': 'Modern Period',
                'fase_iniziale': 1,
                'rapporti': ''
            }
        ]

        # Create converter and graph
        converter = S3DConverter()
        graph = converter.create_graph_from_us(us_data, "Test Site")

        # Export to JSON
        output_path = "/tmp/test_s3d_export.json"
        converter.export_to_json(graph, output_path)

        # Read and validate JSON
        with open(output_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # Validate v1.5 structure
        errors = []

        if json_data.get('version') != '1.5':
            errors.append(f"Expected version '1.5', got '{json_data.get('version')}'")

        if 'context' not in json_data:
            errors.append("Missing 'context' key")

        if 'absolute_time_Epochs' not in json_data.get('context', {}):
            errors.append("Missing 'context.absolute_time_Epochs' key")

        if 'graphs' not in json_data:
            errors.append("Missing 'graphs' key")

        # Check graph structure
        graphs = json_data.get('graphs', {})
        if graphs:
            first_graph = list(graphs.values())[0]

            required_keys = ['id', 'name', 'description', 'defaults', 'nodes', 'edges']
            for key in required_keys:
                if key not in first_graph:
                    errors.append(f"Missing '{key}' in graph structure")

            # Check nodes structure
            nodes = first_graph.get('nodes', {})
            required_node_categories = ['authors', 'stratigraphic', 'epochs', 'groups',
                                       'properties', 'documents', 'extractors', 'combiners',
                                       'links', 'geo']
            for category in required_node_categories:
                if category not in nodes:
                    errors.append(f"Missing node category: '{category}'")

            # Check stratigraphic subcategories
            stratigraphic = nodes.get('stratigraphic', {})
            for subcat in ['US', 'USVs', 'SF']:
                if subcat not in stratigraphic:
                    errors.append(f"Missing stratigraphic subcategory: '{subcat}'")

            # Check edges structure
            edges = first_graph.get('edges', {})
            required_edge_types = ['is_before', 'has_same_time', 'has_data_provenance',
                                  'has_author', 'has_first_epoch', 'survive_in_epoch',
                                  'is_in_activity', 'has_property', 'has_timebranch',
                                  'has_linked_resource']
            for edge_type in required_edge_types:
                if edge_type not in edges:
                    errors.append(f"Missing edge type: '{edge_type}'")

        # Clean up
        os.remove(output_path)

        if errors:
            print("✗ JSON validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print("✓ JSON export format is correct (v1.5)")
            print(f"  - Version: {json_data['version']}")
            print(f"  - Graphs: {len(json_data['graphs'])}")
            print(f"  - Node categories: {len(first_graph.get('nodes', {}))}")
            print(f"  - Edge types: {len(first_graph.get('edges', {}))}")
            return True

    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_no_graphml_method():
    """Test that export_to_graphml method has been removed"""
    print("\nTesting GraphML method removal...")
    try:
        from pyarchinit_mini.s3d_integration import S3DConverter
        converter = S3DConverter()

        if hasattr(converter, 'export_to_graphml'):
            print("✗ export_to_graphml method still exists (should be removed)")
            return False
        else:
            print("✓ export_to_graphml method successfully removed")
            return True

    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("s3Dgraphy Integration Test Suite")
    print("=" * 60)

    results = []

    results.append(("Import S3DConverter", test_s3d_converter_import()))
    results.append(("JSON v1.5 Export", test_json_export_format()))
    results.append(("GraphML Method Removed", test_no_graphml_method()))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")

    total = len(results)
    passed = sum(1 for _, result in results if result)

    print("\n" + "=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)

    return all(result for _, result in results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
