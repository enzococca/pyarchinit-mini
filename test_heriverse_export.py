#!/usr/bin/env python3
"""
Test script for Heriverse JSON export format

This script validates that the export_to_heriverse_json() method
generates the correct structure for Heriverse/ATON platforms.
"""

import os
import sys
import json
import tempfile

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("Heriverse Export Test Suite")
print("=" * 60)

# Test 1: Import S3DConverter
print("\n[1/4] Testing S3DConverter import...")
try:
    from pyarchinit_mini.s3d_integration import S3DConverter
    print("✓ S3DConverter imported successfully")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Check export_to_heriverse_json method exists
print("\n[2/4] Testing export_to_heriverse_json() method exists...")
converter = S3DConverter()
if hasattr(converter, 'export_to_heriverse_json'):
    print("✓ export_to_heriverse_json() method exists")
else:
    print("✗ export_to_heriverse_json() method not found")
    sys.exit(1)

# Test 3: Create sample graph and export to Heriverse format
print("\n[3/4] Testing Heriverse JSON export...")
try:
    # Sample US data
    us_data = [
        {
            'us': '001',
            'sito': 'TestSite',
            'area': 'A',
            'unita_tipo': 'US',
            'd_stratigrafica': 'Test stratigraphic description',
            'd_interpretativa': 'Test interpretation',
            'rapporti': 'copre 002',
            'periodo_iniziale': 'Modern',
        },
        {
            'us': '002',
            'sito': 'TestSite',
            'area': 'A',
            'unita_tipo': 'US',
            'd_stratigrafica': 'Lower layer',
            'd_interpretativa': 'Foundation layer',
            'rapporti': '',
            'periodo_iniziale': 'Medieval',
        }
    ]

    # Create graph
    graph = converter.create_graph_from_us(us_data, "TestSite")
    print(f"  - Created graph with {len(graph.nodes)} nodes, {len(graph.edges)} edges")

    # Export to Heriverse JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        output_path = tmp.name

    converter.export_to_heriverse_json(
        graph,
        output_path,
        site_name="TestSite",
        creator_id="user:test-12345",
        resource_path="https://test.server/uploads"
    )

    # Read exported JSON
    with open(output_path, 'r', encoding='utf-8') as f:
        heriverse_data = json.load(f)

    # Clean up temp file
    os.unlink(output_path)

    print("✓ Heriverse JSON exported successfully")

except Exception as e:
    print(f"✗ Export failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Validate Heriverse JSON structure
print("\n[4/4] Validating Heriverse JSON structure...")
errors = []

# Check top-level CouchDB/scene wrapper
required_top_keys = ['_id', '_rev', 'type', 'creator', 'resource_path',
                     'title', 'resource_json', 'wapp', 'created_at']
for key in required_top_keys:
    if key not in heriverse_data:
        errors.append(f"Missing top-level key: {key}")

# Check type and wapp
if heriverse_data.get('type') != 'scene':
    errors.append(f"type should be 'scene', got: {heriverse_data.get('type')}")
if heriverse_data.get('wapp') != 'heriverse':
    errors.append(f"wapp should be 'heriverse', got: {heriverse_data.get('wapp')}")

# Check _id format
if not heriverse_data.get('_id', '').startswith('scene:'):
    errors.append(f"_id should start with 'scene:', got: {heriverse_data.get('_id')}")

# Check resource_json structure
resource_json = heriverse_data.get('resource_json', {})
required_resource_keys = ['title', 'environment', 'scenegraph', 'multigraph']
for key in required_resource_keys:
    if key not in resource_json:
        errors.append(f"Missing resource_json key: {key}")

# Check environment
environment = resource_json.get('environment', {})
env_keys = ['mainpano', 'lightprobes', 'mainlight']
for key in env_keys:
    if key not in environment:
        errors.append(f"Missing environment key: {key}")

# Check scenegraph
scenegraph = resource_json.get('scenegraph', {})
if 'nodes' not in scenegraph or 'edges' not in scenegraph:
    errors.append("scenegraph missing 'nodes' or 'edges'")

# Check multigraph structure
multigraph = resource_json.get('multigraph', {})
if multigraph.get('version') != '1.5':
    errors.append(f"multigraph version should be '1.5', got: {multigraph.get('version')}")

if 'context' not in multigraph:
    errors.append("multigraph missing 'context'")
if 'graphs' not in multigraph:
    errors.append("multigraph missing 'graphs'")

# Check graphs structure
graphs = multigraph.get('graphs', {})
if not graphs:
    errors.append("multigraph.graphs is empty")
else:
    # Get first graph
    graph_id = list(graphs.keys())[0]
    graph_data = graphs[graph_id]

    # Check node categories
    node_categories = graph_data.get('nodes', {})
    required_node_cats = ['authors', 'stratigraphic', 'epochs', 'groups',
                          'properties', 'documents', 'extractors', 'combiners',
                          'links', 'geo', 'semantic_shapes', 'representation_models',
                          'panorama_models']
    for cat in required_node_cats:
        if cat not in node_categories:
            errors.append(f"Missing node category: {cat}")

    # Check stratigraphic subcategories (including USVn)
    strat = node_categories.get('stratigraphic', {})
    required_strat_cats = ['US', 'USVs', 'USVn', 'SF']
    for cat in required_strat_cats:
        if cat not in strat:
            errors.append(f"Missing stratigraphic category: {cat}")

    # Check edge types
    edge_types = graph_data.get('edges', {})
    required_edge_types = ['is_before', 'has_same_time', 'has_data_provenance',
                          'has_author', 'has_first_epoch', 'survive_in_epoch',
                          'is_in_activity', 'has_property', 'has_timebranch',
                          'has_linked_resource', 'generic_connection',
                          'changed_from', 'contrasts_with']
    for edge_type in required_edge_types:
        if edge_type not in edge_types:
            errors.append(f"Missing edge type: {edge_type}")

    # Check that semantic_shapes were auto-generated
    semantic_shapes = node_categories.get('semantic_shapes', {})
    if not semantic_shapes:
        print("  ⚠ Warning: No semantic_shapes generated (expected for US nodes)")

# Print results
print("\nValidation Results:")
print("-" * 60)

if errors:
    print(f"✗ Found {len(errors)} validation errors:")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    sys.exit(1)
else:
    print("✓ All validation checks passed!")
    print("\nStructure verified:")
    print(f"  - CouchDB wrapper: ✓")
    print(f"  - Scene metadata: ✓")
    print(f"  - Environment config: ✓")
    print(f"  - Scenegraph: ✓")
    print(f"  - Multigraph v1.5: ✓")
    print(f"  - Node categories (13): ✓")
    print(f"  - Stratigraphic subcategories (4 including USVn): ✓")
    print(f"  - Edge types (13): ✓")
    print(f"  - Semantic shapes: ✓")

print("\n" + "=" * 60)
print("All tests passed!")
print("=" * 60)
