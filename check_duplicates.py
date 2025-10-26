#!/usr/bin/env python3
"""
Check for duplicate relationships in rapporti field
"""

import sqlite3

def check_duplicates():
    conn = sqlite3.connect('pyarchinit_mini.db')
    cursor = conn.cursor()

    print("=" * 70)
    print("CHECKING FOR DUPLICATE RELATIONSHIPS")
    print("=" * 70)

    cursor.execute("""
        SELECT sito, us, rapporti
        FROM us_table
        WHERE rapporti IS NOT NULL
        AND rapporti != ''
        AND rapporti != '[]'
    """)

    total_us = 0
    us_with_duplicates = 0
    examples = []

    for row in cursor.fetchall():
        sito, us, rapporti = row
        total_us += 1

        # Parse relationships
        parts = [p.strip() for p in rapporti.split(',')]

        # Check for duplicates
        seen = set()
        has_duplicates = False

        for part in parts:
            if part in seen:
                has_duplicates = True
                if len(examples) < 5:
                    examples.append((sito, us, rapporti))
                break
            seen.add(part)

        if has_duplicates:
            us_with_duplicates += 1

    print(f"\nTotal US checked: {total_us}")
    print(f"US with duplicate relationships: {us_with_duplicates}")

    if us_with_duplicates > 0:
        print("\n⚠️  Found duplicates in rapporti field!")
        print("\nExamples:")
        for sito, us, rapporti in examples:
            print(f"\n  {sito} / US {us}:")
            print(f"    {rapporti}")
    else:
        print("\n✅ No duplicates found!")
        print("\nFormat verification:")

        # Show some examples
        cursor.execute("""
            SELECT sito, us, rapporti
            FROM us_table
            WHERE rapporti IS NOT NULL
            AND rapporti != ''
            AND rapporti != '[]'
            ORDER BY RANDOM()
            LIMIT 5
        """)

        for row in cursor.fetchall():
            sito, us, rapporti = row
            print(f"\n  {sito} / US {us}:")
            print(f"    {rapporti}")

    print("\n" + "=" * 70)

    conn.close()

if __name__ == "__main__":
    check_duplicates()
