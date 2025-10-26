#!/usr/bin/env python3
"""
Script to check rapporti field in source PyArchInit database
"""

import sys
import ast
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def check_source_rapporti(db_path):
    """Check rapporti field in source PyArchInit database"""

    print("=" * 70)
    print("CHECKING RAPPORTI FIELD IN PYARCHINIT DATABASE")
    print("=" * 70)
    print(f"\nDatabase: {db_path}")

    try:
        # Connect to source database
        conn_string = f"sqlite:///{db_path}"
        engine = create_engine(conn_string)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Count total US
        result = session.execute(text("SELECT COUNT(*) FROM us_table"))
        us_count = result.scalar()
        print(f"\nTotal US records: {us_count}")

        # Count US with non-empty rapporti
        result = session.execute(text("""
            SELECT COUNT(*)
            FROM us_table
            WHERE rapporti IS NOT NULL AND rapporti != '' AND rapporti != '[]'
        """))
        rapporti_count = result.scalar()
        print(f"US with rapporti: {rapporti_count}")

        if rapporti_count == 0:
            print("\n⚠️  NO RAPPORTI FOUND IN SOURCE DATABASE!")
            print("\nThis is why no relationships were imported.")
            print("The source PyArchInit database has no stratigraphic relationships defined.")
        else:
            print(f"\n✓ Found {rapporti_count} US records with rapporti")

            # Show sample rapporti
            result = session.execute(text("""
                SELECT sito, us, rapporti, d_stratigrafica
                FROM us_table
                WHERE rapporti IS NOT NULL AND rapporti != '' AND rapporti != '[]'
                LIMIT 10
            """))
            samples = result.fetchall()

            print("\nSample rapporti fields:")
            for sample in samples:
                print(f"\n  Site: {sample.sito}")
                print(f"  US: {sample.us}")
                print(f"  Description: {sample.d_stratigrafica}")
                print(f"  Rapporti: {sample.rapporti}")

                # Try to parse rapporti
                try:
                    rapporti_list = ast.literal_eval(sample.rapporti)
                    print(f"  Parsed relationships:")
                    for rel in rapporti_list:
                        if isinstance(rel, list) and len(rel) >= 2:
                            print(f"    - {rel[0]} → US {rel[1]}")
                except Exception as e:
                    print(f"  ⚠️  Failed to parse: {str(e)}")

            # Count relationships by type
            print("\n" + "=" * 70)
            print("Analyzing relationship types...")

            all_rapporti = session.execute(text("""
                SELECT rapporti FROM us_table
                WHERE rapporti IS NOT NULL AND rapporti != '' AND rapporti != '[]'
            """)).fetchall()

            rel_types = {}
            total_rels = 0

            for row in all_rapporti:
                try:
                    rapporti_list = ast.literal_eval(row.rapporti)
                    for rel in rapporti_list:
                        if isinstance(rel, list) and len(rel) >= 2:
                            rel_type = rel[0]
                            rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
                            total_rels += 1
                except:
                    pass

            print(f"\nTotal relationships found: {total_rels}")
            if rel_types:
                print("\nRelationship types:")
                for rel_type, count in sorted(rel_types.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {rel_type}: {count}")

        print("\n" + "=" * 70)

        session.close()

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python check_source_rapporti.py <path_to_pyarchinit_db>")
        print("\nExample:")
        print("  python check_source_rapporti.py /Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite")
        sys.exit(1)

    db_path = sys.argv[1]
    check_source_rapporti(db_path)
