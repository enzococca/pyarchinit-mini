#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug GraphML Export - See what periods are being exported
"""

import sys
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from sqlalchemy import text

def debug_export():
    """Debug the GraphML export process"""

    print("=" * 80)
    print("DEBUG GRAPHML EXPORT")
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

    site_name = "Dom zu Lund"

    print(f"Site: {site_name}")
    print()

    # Step 1: Generate graph
    print("Step 1: Generating graph...")
    graph = matrix_generator.generate_matrix(site_name)
    print(f"Graph has {len(graph.nodes())} nodes")
    print()

    # Step 2: Simulate the periodization grouping logic
    print("Step 2: Simulating periodization grouping...")
    print()

    try:
        with db_manager.connection.get_session() as session:
            # Build lookup map
            query = text("""
                SELECT periodo_iniziale, fase_iniziale, datazione_estesa
                FROM periodizzazione_table
                WHERE sito = :site
            """)
            result = session.execute(query, {'site': site_name})

            periodo_fase_to_datazione = {}
            for row in result.fetchall():
                periodo = str(row.periodo_iniziale) if row.periodo_iniziale else ''
                fase = str(row.fase_iniziale) if row.fase_iniziale else ''
                datazione = row.datazione_estesa or 'Non datato'
                key = (periodo, fase)
                periodo_fase_to_datazione[key] = datazione

            print(f"Loaded {len(periodo_fase_to_datazione)} periodo/fase mappings")
            print()

            # Group nodes by datazione
            datazione_groups = {}
            datazione_min_periodo_fase = {}

            for node_id, node_data in graph.nodes(data=True):
                periodo_raw = node_data.get('period_initial')
                fase_raw = node_data.get('phase_initial')

                periodo = str(periodo_raw) if periodo_raw is not None and periodo_raw != '' else ''
                fase = str(fase_raw) if fase_raw is not None and fase_raw != '' else ''

                lookup_key = (periodo, fase)
                if lookup_key in periodo_fase_to_datazione:
                    datazione = periodo_fase_to_datazione[lookup_key]
                else:
                    datazione = 'Non datato'

                # Track minimum (periodo, fase) for this datazione
                if datazione not in datazione_min_periodo_fase:
                    datazione_min_periodo_fase[datazione] = (periodo, fase)
                else:
                    current_min = datazione_min_periodo_fase[datazione]
                    if (periodo or 'ZZZ', fase or 'ZZZ') < (current_min[0] or 'ZZZ', current_min[1] or 'ZZZ'):
                        datazione_min_periodo_fase[datazione] = (periodo, fase)

                # Group nodes
                if datazione not in datazione_groups:
                    datazione_groups[datazione] = []

                datazione_groups[datazione].append((node_id, node_data))

            print(f"Found {len(datazione_groups)} unique datazioni:")
            print()

            for datazione, nodes in datazione_groups.items():
                min_p, min_f = datazione_min_periodo_fase[datazione]
                print(f"  - {datazione:45} : {len(nodes):4} nodes (min p={min_p or 'NULL'}, f={min_f or 'NULL'})")

            print()

            # Sort groups
            sorted_groups = sorted(
                datazione_groups.items(),
                key=lambda x: (
                    datazione_min_periodo_fase[x[0]][0] or 'ZZZ',
                    datazione_min_periodo_fase[x[0]][1] or 'ZZZ',
                    x[0]
                )
            )

            print("Sorted order:")
            print()
            for i, (datazione, nodes) in enumerate(sorted_groups, 1):
                min_p, min_f = datazione_min_periodo_fase[datazione]
                print(f"  {i}. {datazione:45} : {len(nodes):4} nodes (sort key: p={min_p or 'ZZZ'}, f={min_f or 'ZZZ'})")

            print()
            print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_export()