#!/usr/bin/env python3
"""
Test script for Harris Matrix generation and visualization
"""

import sys
import os
sys.path.insert(0, '.')

from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.us_service import USService

def test_harris_matrix():
    """Test Harris Matrix generation and PyArchInit-style visualization"""
    
    # Initialize components
    db_path = 'pyarchinit_mini.db'
    connection = DatabaseConnection(f'sqlite:///{db_path}')
    db_manager = DatabaseManager(connection)
    us_service = USService(db_manager)
    generator = HarrisMatrixGenerator(db_manager, us_service)
    visualizer = PyArchInitMatrixVisualizer()

    print("🏺 Testing Harris Matrix Generation")
    print("=" * 50)
    
    # Test generation
    print("📊 Generating Harris Matrix for Sito Archeologico di Esempio...")
    graph = generator.generate_matrix('Sito Archeologico di Esempio')
    print(f"Generated graph with {len(graph.nodes())} nodes and {len(graph.edges())} edges")

    # Show some node details
    if graph.nodes():
        print("\n📝 Sample nodes:")
        for node in sorted(list(graph.nodes()))[:5]:
            data = graph.nodes[node]
            area = data.get('area', '?')
            period = data.get('period_initial', '?')
            formation = data.get('formation', '?')
            desc = data.get('interpretation', '')[:40] if data.get('interpretation') else ''
            print(f"   US {node}: Area {area}, Periodo {period}, {formation}, {desc}")

    # Show relationships
    if graph.edges():
        print(f"\n🔗 Sample relationships:")
        for edge in list(graph.edges(data=True))[:5]:
            rel_type = edge[2].get('relationship', '?')
            print(f"   US {edge[0]} -> US {edge[1]}: {rel_type}")

    # Matrix statistics
    print(f"\n📈 Matrix statistics:")
    stats = generator.get_matrix_statistics(graph)
    for key, value in stats.items():
        if key != 'cycles':
            print(f"   {key}: {value}")
    
    # Test Graphviz visualization
    print(f"\n🎨 Testing PyArchInit-style Graphviz visualization...")
    try:
        import tempfile
        output_path = tempfile.mktemp(suffix='_harris_matrix')
        
        # Test period/area grouping
        result = visualizer.create_matrix(graph, grouping='period_area', output_path=output_path)
        print(f"   Matrix with period/area grouping created: {result}")
        
        # Test period only grouping
        result2 = visualizer.create_matrix(graph, grouping='period', output_path=output_path + '_period')
        print(f"   Matrix with period grouping created: {result2}")
        
        # Test export in multiple formats
        exports = visualizer.export_multiple_formats(graph, output_path + '_multi')
        print(f"   Multi-format exports: {list(exports.keys())}")
        
    except Exception as e:
        print(f"   ⚠️  Visualization error: {e}")
        print("   Note: Graphviz may not be installed. Install with: brew install graphviz")

    print("\n✅ Harris Matrix test completed!")

if __name__ == "__main__":
    test_harris_matrix()