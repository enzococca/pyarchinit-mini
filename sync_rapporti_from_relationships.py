#!/usr/bin/env python3
"""
Sync rapporti field from us_relationships_table

This script populates the 'rapporti' field in us_table using data
from us_relationships_table, so you don't need to re-import.
"""

import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def sync_rapporti_field():
    """Sync rapporti field for all US from relationships table"""

    print("=" * 70)
    print("SYNCING RAPPORTI FIELD FROM US_RELATIONSHIPS_TABLE")
    print("=" * 70)

    # Connect to database
    engine = create_engine('sqlite:///./pyarchinit_mini.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get all sites
        result = session.execute(text("SELECT DISTINCT sito FROM us_table ORDER BY sito"))
        sites = [row[0] for row in result.fetchall()]

        print(f"\nFound {len(sites)} sites to process")

        total_updated = 0
        total_empty = 0

        for site in sites:
            print(f"\nProcessing site: {site}")

            # Get all US for this site
            result = session.execute(
                text("SELECT us FROM us_table WHERE sito = :sito ORDER BY CAST(us AS INTEGER)"),
                {'sito': site}
            )
            us_list = [row[0] for row in result.fetchall()]

            updated_in_site = 0

            for us_num in us_list:
                # Get relationships for this US from us_relationships_table
                result = session.execute(
                    text("""
                        SELECT relationship_type, us_to
                        FROM us_relationships_table
                        WHERE sito = :sito AND us_from = :us_from
                        ORDER BY relationship_type, us_to
                    """),
                    {'sito': site, 'us_from': int(us_num)}
                )
                relationships = result.fetchall()

                if relationships:
                    # Build rapporti string in simple text format
                    # Format: "Copre 2, Taglia 3"
                    # Remove duplicates using a set to track seen relationships
                    seen = set()
                    rapporti_parts = []

                    for rel in relationships:
                        # Create unique key to detect duplicates
                        rel_key = (rel.relationship_type, str(rel.us_to))

                        if rel_key not in seen:
                            seen.add(rel_key)
                            rapporti_parts.append(f"{rel.relationship_type} {rel.us_to}")

                    # Join with comma separator
                    rapporti_str = ", ".join(rapporti_parts) if rapporti_parts else ""

                    # Update US record
                    session.execute(
                        text("""
                            UPDATE us_table
                            SET rapporti = :rapporti
                            WHERE sito = :sito AND us = :us
                        """),
                        {
                            'rapporti': rapporti_str,
                            'sito': site,
                            'us': us_num
                        }
                    )
                    updated_in_site += 1
                    total_updated += 1
                    print(f"  US {us_num}: {len(relationships)} relationships → rapporti field")
                else:
                    # Clear rapporti field if no relationships
                    session.execute(
                        text("""
                            UPDATE us_table
                            SET rapporti = ''
                            WHERE sito = :sito AND us = :us
                        """),
                        {'sito': site, 'us': us_num}
                    )
                    total_empty += 1

            session.commit()
            print(f"  → Updated {updated_in_site} US records with rapporti")

        print("\n" + "=" * 70)
        print("SYNC COMPLETED")
        print("=" * 70)
        print(f"\nTotal US updated with rapporti: {total_updated}")
        print(f"Total US with no relationships: {total_empty}")

        # Verify results
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)

        result = session.execute(text("""
            SELECT COUNT(*) FROM us_table
            WHERE rapporti IS NOT NULL AND rapporti != '' AND rapporti != '[]'
        """))
        populated = result.scalar()

        result = session.execute(text("SELECT COUNT(*) FROM us_table"))
        total = result.scalar()

        print(f"\nUS with populated rapporti: {populated}/{total}")

        # Show samples
        result = session.execute(text("""
            SELECT sito, us, rapporti
            FROM us_table
            WHERE rapporti IS NOT NULL AND rapporti != '' AND rapporti != '[]'
            LIMIT 5
        """))

        print("\nSample US with rapporti field:")
        for row in result.fetchall():
            rapporti_preview = row.rapporti[:80] + "..." if len(row.rapporti) > 80 else row.rapporti
            print(f"  {row.sito} / US {row.us}")
            print(f"    {rapporti_preview}")

        print("\n✅ Rapporti field successfully synced from us_relationships_table!")
        print("\nNow you can:")
        print("1. View rapporti field in web interface")
        print("2. Export to PyArchInit with rapporti preserved")
        print("3. Use both rapporti field AND us_relationships_table")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    print("\n⚠️  This script will UPDATE the 'rapporti' field in us_table")
    print("It will generate the field from us_relationships_table data.")
    print("\nBackup recommendation:")
    print("  cp pyarchinit_mini.db pyarchinit_mini.db.backup")
    print("\nPress Enter to continue or Ctrl+C to cancel...")

    try:
        input()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)

    sync_rapporti_field()
