#!/usr/bin/env python3
"""Test loading GraphML file with GraphMLParser"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pyarchinit_mini.mcp_server.graphml_parser import GraphMLParser


def test_load(filepath: str):
    """Test loading a GraphML file"""

    print(f"\nTesting GraphML file: {filepath}")
    print("=" * 80)

    # Create parser (without db_session since we're just testing loading)
    parser = GraphMLParser(db_session=None)

    # Try to load
    success = parser.load_graphml(filepath)

    if not success:
        print("❌ FAILED to load GraphML")
        return False

    # Check what was loaded
    if parser.graph is None:
        print("❌ Graph is None after loading")
        return False

    nodes = list(parser.graph.nodes())
    edges = list(parser.graph.edges())

    print(f"\n✅ SUCCESS: Loaded graph with {len(nodes)} nodes and {len(edges)} edges\n")

    if nodes:
        print("Nodes:")
        for node_id in nodes:
            attrs = parser.graph.nodes[node_id]
            label = attrs.get('label', 'N/A')
            period = attrs.get('period', 'N/A')
            desc = attrs.get('description', 'N/A')
            print(f"  - {node_id}: {label} (period: {period})")
            print(f"    Description: {desc[:80]}...")

    if edges:
        print("\nEdges:")
        for source, target in edges:
            attrs = parser.graph.edges[source, target]
            relationship = attrs.get('relationship', 'N/A')
            print(f"  - {source} -> {target}: {relationship}")

    return True


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tmpqzjbg7bc.graphml"

    success = test_load(filepath)
    sys.exit(0 if success else 1)
