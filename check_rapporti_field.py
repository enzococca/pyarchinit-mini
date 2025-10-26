#!/usr/bin/env python3
"""
Check if rapporti field is populated in us_table
"""

import sqlite3

def check_rapporti():
    conn = sqlite3.connect('pyarchinit_mini.db')
    cursor = conn.cursor()

    print("=" * 70)
    print("CHECKING RAPPORTI FIELD IN US_TABLE")
    print("=" * 70)

    # Count total US
    cursor.execute("SELECT COUNT(*) FROM us_table")
    total = cursor.fetchone()[0]
    print(f"\nTotal US records: {total}")

    # Count US with non-empty rapporti
    cursor.execute("""
        SELECT COUNT(*) FROM us_table
        WHERE rapporti IS NOT NULL
        AND rapporti != ''
        AND rapporti != '[]'
    """)
    with_rapporti = cursor.fetchone()[0]
    print(f"US with rapporti field populated: {with_rapporti}")

    if with_rapporti == 0:
        print("\n⚠️  RAPPORTI FIELD IS EMPTY IN ALL US!")
        print("\nThis is expected behavior for PyArchInit-Mini:")
        print("- Import reads FROM rapporti field (PyArchInit source)")
        print("- Creates relationships in us_relationships_table")
        print("- Does NOT copy rapporti field to destination")
        print("\nRelationships are stored in separate table:")

        cursor.execute("SELECT COUNT(*) FROM us_relationships_table")
        rels = cursor.fetchone()[0]
        print(f"  us_relationships_table: {rels} relationships")

        if rels > 0:
            print("\n✅ This is CORRECT! PyArchInit-Mini uses relational approach.")
            print("\nRapporti field vs us_relationships_table:")
            print("  PyArchInit (old):  rapporti field (TEXT, Python list)")
            print("  PyArchInit-Mini:   us_relationships_table (relational)")
        else:
            print("\n❌ Problem: No relationships found anywhere!")

    else:
        print(f"\n✓ Found {with_rapporti} US with rapporti field")

        # Show samples
        cursor.execute("""
            SELECT sito, us, rapporti
            FROM us_table
            WHERE rapporti IS NOT NULL
            AND rapporti != ''
            AND rapporti != '[]'
            LIMIT 5
        """)

        print("\nSample US with rapporti:")
        for row in cursor.fetchall():
            print(f"  {row[0]} / US {row[1]}: {row[2][:80]}...")

    print("\n" + "=" * 70)

    # Check if rapporti field should be synced
    print("\nDo you want rapporti field to be populated?")
    print("\nOptions:")
    print("1. Keep current design (recommended)")
    print("   - Relationships in us_relationships_table")
    print("   - rapporti field empty")
    print("   - Faster queries, better data integrity")
    print("\n2. Sync rapporti field with relationships")
    print("   - Populate rapporti from us_relationships_table")
    print("   - Maintains backward compatibility")
    print("   - Requires keeping both in sync")

    conn.close()

if __name__ == "__main__":
    check_rapporti()
