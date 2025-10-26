#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug Periodization Lookup - Find why only 4 clusters appear instead of 8
"""

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from sqlalchemy import text

def debug_periodization_lookup():
    """Debug the periodization lookup to find missing datazioni"""

    print("=" * 80)
    print("PERIODIZATION LOOKUP DEBUG")
    print("=" * 80)
    print()

    # Initialize database
    db_path = "/Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db"
    connection_string = f"sqlite:///{db_path}"

    db_connection = DatabaseConnection(connection_string)
    db_manager = DatabaseManager(db_connection)

    site_name = "Dom zu Lund"

    try:
        with db_manager.connection.get_session() as session:

            # 1. Build lookup map (same logic as export_to_graphml)
            print("1. BUILDING LOOKUP MAP (periodo, fase) -> datazione_estesa")
            print("-" * 80)

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

                print(f"   Map: ({periodo}, {fase}) -> {datazione}")

            print()
            print(f"Total entries in lookup map: {len(periodo_fase_to_datazione)}")
            print()

            # 2. Check US periodo/fase values
            print("2. US PERIODO/FASE VALUES AND LOOKUP RESULTS")
            print("-" * 80)

            query = text("""
                SELECT
                    periodo_iniziale,
                    fase_iniziale,
                    COUNT(*) as us_count
                FROM us_table
                WHERE sito = :site
                GROUP BY periodo_iniziale, fase_iniziale
                ORDER BY us_count DESC
            """)

            result = session.execute(query, {'site': site_name})
            rows = result.fetchall()

            datazione_groups = {}

            for row in rows:
                # Same logic as export_to_graphml
                periodo_raw = row.periodo_iniziale
                fase_raw = row.fase_iniziale

                periodo = str(periodo_raw) if periodo_raw is not None and periodo_raw != '' else ''
                fase = str(fase_raw) if fase_raw is not None and fase_raw != '' else ''

                lookup_key = (periodo, fase)

                if lookup_key in periodo_fase_to_datazione:
                    datazione = periodo_fase_to_datazione[lookup_key]
                    match_status = "✅ MATCH"
                else:
                    datazione = 'Non datato'
                    match_status = "❌ NO MATCH"

                # Group by datazione
                if datazione not in datazione_groups:
                    datazione_groups[datazione] = 0
                datazione_groups[datazione] += row.us_count

                print(f"   Periodo: {periodo_raw or 'NULL':4} | Fase: {fase_raw or 'NULL':4} | US: {row.us_count:4} | {match_status}")
                print(f"      Lookup key: {lookup_key}")
                print(f"      Datazione:  {datazione}")
                print()

            # 3. Show grouped results
            print("3. GROUPED BY DATAZIONE (What GraphML will show)")
            print("-" * 80)

            sorted_datazioni = sorted(datazione_groups.items(), key=lambda x: x[1], reverse=True)

            for datazione, us_count in sorted_datazioni:
                print(f"   {datazione:45} : {us_count:4} US")

            print()
            print(f"Total unique datazioni: {len(datazione_groups)}")
            print()

            # 4. Check for type mismatches
            print("4. CHECKING FOR TYPE MISMATCHES (INTEGER vs STRING)")
            print("-" * 80)

            # Check if periodo/fase in periodizzazione_table are stored as TEXT or INTEGER
            query_types = text("""
                SELECT
                    typeof(periodo_iniziale) as periodo_type,
                    typeof(fase_iniziale) as fase_type,
                    periodo_iniziale,
                    fase_iniziale,
                    datazione_estesa
                FROM periodizzazione_table
                WHERE sito = :site
                LIMIT 5
            """)

            result = session.execute(query_types, {'site': site_name})
            rows = result.fetchall()

            print("   Periodizzazione table types:")
            for row in rows:
                print(f"      Periodo: {row.periodo_iniziale} ({row.periodo_type})")
                print(f"      Fase:    {row.fase_iniziale} ({row.fase_type})")
                print(f"      Datazione: {row.datazione_estesa}")
                print()

            # Check US table types
            query_types_us = text("""
                SELECT
                    typeof(periodo_iniziale) as periodo_type,
                    typeof(fase_iniziale) as fase_type,
                    periodo_iniziale,
                    fase_iniziale
                FROM us_table
                WHERE sito = :site
                  AND periodo_iniziale IS NOT NULL
                LIMIT 5
            """)

            result = session.execute(query_types_us, {'site': site_name})
            rows = result.fetchall()

            print("   US table types:")
            for row in rows:
                print(f"      Periodo: {row.periodo_iniziale} ({row.periodo_type})")
                print(f"      Fase:    {row.fase_iniziale} ({row.fase_type})")
                print()

            print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_periodization_lookup()