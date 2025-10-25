#!/usr/bin/env python3
"""
Diagnostic script to test Dom zu Lund import
"""

import sys
import logging
from pyarchinit_mini.services.import_export_service import ImportExportService

# Configure logging to see everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s'
)

# Database paths
MINI_DB = 'sqlite:////Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db'
SOURCE_DB = 'sqlite:////Users/enzo/pyarchinit/pyarchinit_DB_folder/Promotion_Krypta_Lund.sqlite'

print("="*80)
print("Dom zu Lund Import Diagnostic")
print("="*80)
print(f"\nMini DB: {MINI_DB}")
print(f"Source DB: {SOURCE_DB}\n")

# Initialize service
try:
    service = ImportExportService(MINI_DB, SOURCE_DB)
    print("✓ Service initialized\n")
except Exception as e:
    print(f"✗ Failed to initialize service: {e}")
    sys.exit(1)

# Test import with detailed error reporting
print("="*80)
print("Starting US Import (first 5 only for testing)")
print("="*80)

try:
    # Import first few US to see what happens
    stats = service.import_us(
        sito_filter=['Dom zu Lund'],
        import_relationships=True,
        auto_migrate=True
    )

    print("\n" + "="*80)
    print("Import Results")
    print("="*80)
    print(f"Imported: {stats['imported']}")
    print(f"Updated: {stats['updated']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Relationships: {stats['relationships_created']}")
    print(f"Errors: {len(stats['errors'])}")

    if stats['errors']:
        print("\nErrors encountered:")
        for i, error in enumerate(stats['errors'][:10], 1):  # Show first 10 errors
            print(f"  {i}. {error}")

        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more errors")

    print("\n" + "="*80)

    # Verify data in database
    from sqlalchemy import text
    with service.mini_session_maker() as session:
        count = session.execute(
            text("SELECT COUNT(*) FROM us_table WHERE sito = 'Dom zu Lund'")
        ).scalar()
        print(f"US in database after import: {count}")

        if count > 0:
            print("\nFirst 5 US in database:")
            result = session.execute(
                text("SELECT id_us, sito, us, d_stratigrafica FROM us_table WHERE sito = 'Dom zu Lund' LIMIT 5")
            )
            for row in result:
                print(f"  - ID {row[0]}: {row[1]}/{row[2]} - {row[3]}")

    print("="*80)

except Exception as e:
    print(f"\n✗ Import failed with exception: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
