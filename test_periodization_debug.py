#!/usr/bin/env python3
"""
Debug script to check periodization in graph
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.harris_matrix import HarrisMatrixGenerator
import os

def main():
    # Get database connection
    db_path = os.path.expanduser('~/.pyarchinit_mini/data/pyarchinit_mini.db')
    connection_string = f"sqlite:///{db_path}"
    db_connection = DatabaseConnection(connection_string)

    # Create database manager
    db_manager = DatabaseManager(db_connection)

    # Create US service
    us_service = USService(db_manager)

    # Create Harris Matrix generator
    generator = HarrisMatrixGenerator(db_manager, us_service)

    # Generate matrix graph
    site_name = "Metro C - Amba Aradam"
    graph = generator.generate_matrix(site_name)

    print(f"\n{'='*70}")
    print(f"Graph Nodes Debug - Site: {site_name}")
    print(f"{'='*70}\n")

    print(f"Total nodes: {graph.number_of_nodes()}")
    print(f"Total edges: {graph.number_of_edges()}")
    print()

    # Check periodo_code in nodes
    periods_found = {}

    for node_id, node_data in list(graph.nodes(data=True))[:10]:  # First 10 nodes
        periodo_code = node_data.get('periodo_code', '')
        period_initial = node_data.get('period_initial', '')
        phase_initial = node_data.get('phase_initial', '')
        extended_label = node_data.get('extended_label', '')

        print(f"Node: {node_id}")
        print(f"  Extended label: {extended_label}")
        print(f"  Period initial: {period_initial}")
        print(f"  Phase initial: {phase_initial}")
        print(f"  Periodo code: {periodo_code}")
        print()

        if periodo_code:
            periods_found[periodo_code] = periods_found.get(periodo_code, 0) + 1

    print(f"\n{'='*70}")
    print(f"Periods Found in Graph:")
    print(f"{'='*70}\n")

    if periods_found:
        for periodo, count in sorted(periods_found.items()):
            print(f"  {periodo}: {count} nodes")
    else:
        print("  NO PERIODS FOUND!")

    print()

if __name__ == '__main__':
    main()
