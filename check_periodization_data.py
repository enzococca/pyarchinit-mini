#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check Periodization Data Import for Dom zu Lund
Verifies periodo/fase/datazione_estesa data
"""

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from sqlalchemy import text

def check_periodization_data():
    """Check periodization data for Dom zu Lund"""

    print("=" * 80)
    print("PERIODIZATION DATA VERIFICATION")
    print("=" * 80)
    print()

    # Initialize database
    db_path = "/Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db"
    connection_string = f"sqlite:///{db_path}"

    db_connection = DatabaseConnection(connection_string)
    db_manager = DatabaseManager(db_connection)

    site_name = "Dom zu Lund"

    # 1. Check periodizzazione_table
    print("1. PERIODIZZAZIONE TABLE")
    print("-" * 80)

    try:
        with db_manager.connection.get_session() as session:
            query = text("""
                SELECT
                    periodo_iniziale,
                    fase_iniziale,
                    periodo_finale,
                    fase_finale,
                    datazione_estesa,
                    COUNT(*) as count
                FROM periodizzazione_table
                WHERE sito = :site
                GROUP BY periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, datazione_estesa
                ORDER BY periodo_iniziale, fase_iniziale
            """)

            result = session.execute(query, {'site': site_name})
            rows = result.fetchall()

            if rows:
                print(f"Found {len(rows)} unique periodo/fase combinations:\n")
                for row in rows:
                    print(f"  Periodo: {row.periodo_iniziale or 'NULL'}")
                    print(f"  Fase:    {row.fase_iniziale or 'NULL'}")
                    print(f"  Periodo Finale: {row.periodo_finale or 'NULL'}")
                    print(f"  Fase Finale:    {row.fase_finale or 'NULL'}")
                    print(f"  Datazione:      {row.datazione_estesa or 'NULL'}")
                    print(f"  Records:        {row.count}")
                    print()
            else:
                print("⚠️  NO RECORDS FOUND in periodizzazione_table")
                print()

    except Exception as e:
        print(f"❌ Error reading periodizzazione_table: {e}")
        print()

    # 2. Check US table periodo/fase distribution
    print("2. US TABLE - PERIODO/FASE DISTRIBUTION")
    print("-" * 80)

    try:
        with db_manager.connection.get_session() as session:
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

            if rows:
                print(f"Found {len(rows)} unique periodo/fase in US table:\n")
                total_us = sum(row.us_count for row in rows)

                for row in rows:
                    periodo = row.periodo_iniziale or 'NULL'
                    fase = row.fase_iniziale or 'NULL'
                    count = row.us_count
                    percentage = (count / total_us * 100) if total_us > 0 else 0

                    print(f"  Periodo: {periodo:15} | Fase: {fase:20} | US: {count:4} ({percentage:5.1f}%)")

                print()
                print(f"Total US: {total_us}")
                print()
            else:
                print("⚠️  NO RECORDS FOUND in us_table")
                print()

    except Exception as e:
        print(f"❌ Error reading us_table: {e}")
        print()

    # 3. Check US without periodo/fase (NULL values)
    print("3. US WITHOUT PERIODIZATION DATA")
    print("-" * 80)

    try:
        with db_manager.connection.get_session() as session:
            query = text("""
                SELECT COUNT(*) as null_count
                FROM us_table
                WHERE sito = :site
                  AND (periodo_iniziale IS NULL OR periodo_iniziale = '')
                  AND (fase_iniziale IS NULL OR fase_iniziale = '')
            """)

            result = session.execute(query, {'site': site_name})
            null_count = result.scalar()

            query_total = text("""
                SELECT COUNT(*) as total_count
                FROM us_table
                WHERE sito = :site
            """)

            result_total = session.execute(query_total, {'site': site_name})
            total_count = result_total.scalar()

            if null_count > 0:
                percentage = (null_count / total_count * 100) if total_count > 0 else 0
                print(f"⚠️  {null_count} US without periodo/fase ({percentage:.1f}%)")

                # Show some examples
                query_examples = text("""
                    SELECT us, unita_tipo, d_interpretativa
                    FROM us_table
                    WHERE sito = :site
                      AND (periodo_iniziale IS NULL OR periodo_iniziale = '')
                      AND (fase_iniziale IS NULL OR fase_iniziale = '')
                    LIMIT 10
                """)

                result_examples = session.execute(query_examples, {'site': site_name})
                examples = result_examples.fetchall()

                if examples:
                    print("\nExamples of US without periodization:")
                    for ex in examples:
                        print(f"  - US {ex.us} ({ex.unita_tipo}): {ex.d_interpretativa or 'N/A'}")
                print()
            else:
                print("✅ All US have periodo/fase data")
                print()

    except Exception as e:
        print(f"❌ Error checking NULL values: {e}")
        print()

    # 4. Check if periodo/fase from US match periodizzazione_table
    print("4. PERIODO/FASE MATCHING")
    print("-" * 80)

    try:
        with db_manager.connection.get_session() as session:
            # Get periodo/fase combinations from US that DON'T exist in periodizzazione
            query = text("""
                SELECT DISTINCT
                    u.periodo_iniziale,
                    u.fase_iniziale,
                    COUNT(*) as us_count
                FROM us_table u
                LEFT JOIN periodizzazione_table p
                    ON p.sito = u.sito
                    AND p.periodo_iniziale = u.periodo_iniziale
                    AND p.fase_iniziale = u.fase_iniziale
                WHERE u.sito = :site
                  AND u.periodo_iniziale IS NOT NULL
                  AND u.periodo_iniziale != ''
                  AND p.periodo_iniziale IS NULL
                GROUP BY u.periodo_iniziale, u.fase_iniziale
            """)

            result = session.execute(query, {'site': site_name})
            unmatched = result.fetchall()

            if unmatched:
                print(f"⚠️  Found {len(unmatched)} periodo/fase in US that DON'T match periodizzazione_table:\n")
                for row in unmatched:
                    print(f"  Periodo: {row.periodo_iniziale or 'NULL'}")
                    print(f"  Fase:    {row.fase_iniziale or 'NULL'}")
                    print(f"  US affected: {row.us_count}")
                    print()
                print("These US will be grouped as 'Non datato' in GraphML export!")
                print()
            else:
                print("✅ All US periodo/fase match periodizzazione_table")
                print()

    except Exception as e:
        print(f"❌ Error checking matching: {e}")
        print()

    # 5. Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    try:
        with db_manager.connection.get_session() as session:
            # Total periodizzazione records
            query = text("SELECT COUNT(*) FROM periodizzazione_table WHERE sito = :site")
            result = session.execute(query, {'site': site_name})
            period_count = result.scalar()

            # Total US
            query = text("SELECT COUNT(*) FROM us_table WHERE sito = :site")
            result = session.execute(query, {'site': site_name})
            us_count = result.scalar()

            # Unique datazione_estesa values
            query = text("""
                SELECT COUNT(DISTINCT datazione_estesa)
                FROM periodizzazione_table
                WHERE sito = :site AND datazione_estesa IS NOT NULL AND datazione_estesa != ''
            """)
            result = session.execute(query, {'site': site_name})
            datazione_count = result.scalar()

            print(f"Total periodizzazione records: {period_count}")
            print(f"Total US: {us_count}")
            print(f"Unique datazione_estesa values: {datazione_count}")
            print()

    except Exception as e:
        print(f"❌ Error in summary: {e}")

    print("=" * 80)


if __name__ == "__main__":
    check_periodization_data()