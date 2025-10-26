#!/usr/bin/env python3
"""
Script to check US relationships in PyArchInit-Mini database
"""

import sys
sys.path.append('.')

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from sqlalchemy import text

def check_relationships():
    """Check if relationships exist in database"""

    print("=" * 70)
    print("CHECKING US RELATIONSHIPS IN DATABASE")
    print("=" * 70)

    # Initialize database
    db_conn = DatabaseConnection('sqlite:///./pyarchinit_mini.db')
    db_manager = DatabaseManager(db_conn.engine)

    # Create session
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=db_conn.engine)
    session = Session()

    try:
        # Count total US records
        result = session.execute(text("SELECT COUNT(*) FROM us_table"))
        us_count = result.scalar()
        print(f"\nTotal US records: {us_count}")

        # Count relationships
        result = session.execute(text("SELECT COUNT(*) FROM us_relationships_table"))
        rel_count = result.scalar()
        print(f"Total relationships: {rel_count}")

        if rel_count == 0:
            print("\n⚠️  NO RELATIONSHIPS FOUND!")
            print("\nPossible causes:")
            print("1. Import was done without 'Import US Relationships' checkbox")
            print("2. PyArchInit database has empty 'rapporti' fields")
            print("3. Relationship parsing failed")

            # Check if there are any rapporti fields in source
            print("\nChecking US table for any data...")
            result = session.execute(text("""
                SELECT sito, us, unita_tipo, d_stratigrafica
                FROM us_table
                LIMIT 5
            """))
            us_records = result.fetchall()

            if us_records:
                print("\nSample US records:")
                for us in us_records:
                    print(f"  - {us.sito} / US {us.us} ({us.unita_tipo}): {us.d_stratigrafica}")

        else:
            print(f"\n✓ Found {rel_count} relationships")

            # Show sample relationships
            result = session.execute(text("""
                SELECT sito, us_from, relationship_type, us_to
                FROM us_relationships_table
                LIMIT 10
            """))
            relationships = result.fetchall()

            print("\nSample relationships:")
            for rel in relationships:
                print(f"  {rel.sito} - US {rel.us_from} --[{rel.relationship_type}]--> US {rel.us_to}")

            # Group by site
            result = session.execute(text("""
                SELECT sito, COUNT(*) as count
                FROM us_relationships_table
                GROUP BY sito
                ORDER BY count DESC
            """))
            site_counts = result.fetchall()

            print("\nRelationships by site:")
            for site in site_counts:
                print(f"  {site.sito}: {site.count} relationships")

        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    check_relationships()
