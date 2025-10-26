#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix periodization: Change "Preistoria - Neolitico" to "Geologisch"
"""

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from sqlalchemy import text

def fix_periodization():
    """Change Preistoria - Neolitico to Geologisch"""

    print("=" * 80)
    print("FIX PERIODIZATION: Preistoria → Geologisch")
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

            # Check current value
            print("1. Checking current values...")
            query = text("""
                SELECT periodo_iniziale, fase_iniziale, datazione_estesa, COUNT(*) as count
                FROM periodizzazione_table
                WHERE sito = :site
                  AND datazione_estesa LIKE '%Preistoria%'
                GROUP BY periodo_iniziale, fase_iniziale, datazione_estesa
            """)

            result = session.execute(query, {'site': site_name})
            rows = result.fetchall()

            if rows:
                print(f"   Found {len(rows)} record(s) to update:\n")
                for row in rows:
                    print(f"   - Periodo: {row.periodo_iniziale}, Fase: {row.fase_iniziale}")
                    print(f"     Current: {row.datazione_estesa}")
                    print(f"     Records: {row.count}")
                    print()
            else:
                print("   ⚠️  No records found with 'Preistoria' in datazione_estesa")
                return

            # Update to Geologisch
            print("2. Updating to 'Geologisch'...")

            update_query = text("""
                UPDATE periodizzazione_table
                SET datazione_estesa = 'Geologisch'
                WHERE sito = :site
                  AND datazione_estesa LIKE '%Preistoria%'
            """)

            result = session.execute(update_query, {'site': site_name})
            session.commit()

            rows_updated = result.rowcount
            print(f"   ✅ Updated {rows_updated} record(s)")
            print()

            # Verify the change
            print("3. Verifying changes...")
            verify_query = text("""
                SELECT periodo_iniziale, fase_iniziale, datazione_estesa, COUNT(*) as count
                FROM periodizzazione_table
                WHERE sito = :site
                  AND periodo_iniziale = 1
                  AND fase_iniziale = 1
                GROUP BY periodo_iniziale, fase_iniziale, datazione_estesa
            """)

            result = session.execute(verify_query, {'site': site_name})
            rows = result.fetchall()

            if rows:
                print(f"   Verification for Periodo=1, Fase=1:\n")
                for row in rows:
                    print(f"   - Datazione: {row.datazione_estesa}")
                    print(f"     Records:   {row.count}")
                    print()

            # Show all unique datazione values
            print("4. All unique datazione_estesa values:")
            print("-" * 80)

            all_query = text("""
                SELECT DISTINCT datazione_estesa, COUNT(*) as count
                FROM periodizzazione_table
                WHERE sito = :site
                GROUP BY datazione_estesa
                ORDER BY datazione_estesa
            """)

            result = session.execute(all_query, {'site': site_name})
            rows = result.fetchall()

            if rows:
                for i, row in enumerate(rows, 1):
                    print(f"   {i}. {row.datazione_estesa} ({row.count} records)")
                print()
                print(f"Total unique datazione values: {len(rows)}")
                print()

            print("=" * 80)
            print("✅ FIX COMPLETED")
            print("=" * 80)
            print()
            print("Now re-run the GraphML export tests:")
            print("  .venv/bin/python test_sfdp_export.py")
            print("  .venv/bin/python test_sfdp_export_reverse.py")
            print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    fix_periodization()