#!/usr/bin/env python3
"""
Complete import of Dom zu Lund site with all related data
"""

import sys
import logging
from pyarchinit_mini.services.import_export_service import ImportExportService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

# Database paths
MINI_DB = 'sqlite:////Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db'
SOURCE_DB = 'sqlite:////Users/enzo/pyarchinit/pyarchinit_DB_folder/Promotion_Krypta_Lund.sqlite'

print("="*80)
print("Complete Dom zu Lund Import")
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

site_name = 'Dom zu Lund'
results = {}

# 1. Import Site
print("="*80)
print("1. Importing Site")
print("="*80)
try:
    stats = service.import_sites(sito_filter=[site_name], auto_migrate=True)
    results['sites'] = stats
    print(f"✓ Sites imported: {stats['imported']}")
    print(f"  Sites updated: {stats['updated']}")
    print(f"  Sites skipped: {stats['skipped']}")
    if stats['errors']:
        print(f"  Errors: {len(stats['errors'])}")
        for error in stats['errors'][:5]:
            print(f"    - {error}")
except Exception as e:
    print(f"✗ Site import failed: {e}")
    results['sites'] = {'error': str(e)}

print()

# 2. Import US (if not already done)
print("="*80)
print("2. Importing US")
print("="*80)
try:
    stats = service.import_us(
        sito_filter=[site_name],
        import_relationships=True,
        auto_migrate=True
    )
    results['us'] = stats
    print(f"✓ US imported: {stats['imported']}")
    print(f"  US updated: {stats['updated']}")
    print(f"  US skipped: {stats['skipped']}")
    print(f"  Relationships: {stats['relationships_created']}")
    if stats['errors']:
        print(f"  Errors: {len(stats['errors'])}")
        for error in stats['errors'][:5]:
            print(f"    - {error}")
except Exception as e:
    print(f"✗ US import failed: {e}")
    results['us'] = {'error': str(e)}

print()

# 3. Import Inventario
print("="*80)
print("3. Importing Inventario Materiali")
print("="*80)
try:
    stats = service.import_inventario(sito_filter=[site_name], auto_migrate=True)
    results['inventario'] = stats
    print(f"✓ Inventario imported: {stats['imported']}")
    print(f"  Inventario updated: {stats['updated']}")
    print(f"  Inventario skipped: {stats['skipped']}")
    if stats['errors']:
        print(f"  Errors: {len(stats['errors'])}")
        for error in stats['errors'][:5]:
            print(f"    - {error}")
except Exception as e:
    print(f"✗ Inventario import failed: {e}")
    results['inventario'] = {'error': str(e)}

print()

# 4. Import Periodizzazione
print("="*80)
print("4. Importing Periodizzazione")
print("="*80)
try:
    stats = service.import_periodizzazione(sito_filter=[site_name])
    results['periodizzazione'] = stats
    print(f"✓ Periodizzazione imported: {stats['imported']}")
    print(f"  Periodizzazione updated: {stats['updated']}")
    print(f"  Periodizzazione skipped: {stats['skipped']}")
    if stats['errors']:
        print(f"  Errors: {len(stats['errors'])}")
        for error in stats['errors'][:5]:
            print(f"    - {error}")
except Exception as e:
    print(f"✗ Periodizzazione import failed: {e}")
    results['periodizzazione'] = {'error': str(e)}

print()

# 5. Import Thesaurus
print("="*80)
print("5. Importing Thesaurus")
print("="*80)
try:
    stats = service.import_thesaurus()
    results['thesaurus'] = stats
    print(f"✓ Thesaurus imported: {stats['imported']}")
    print(f"  Thesaurus updated: {stats['updated']}")
    print(f"  Thesaurus skipped: {stats['skipped']}")
    if stats['errors']:
        print(f"  Errors: {len(stats['errors'])}")
        for error in stats['errors'][:5]:
            print(f"    - {error}")
except Exception as e:
    print(f"✗ Thesaurus import failed: {e}")
    results['thesaurus'] = {'error': str(e)}

print()

# Final verification
print("="*80)
print("Final Verification")
print("="*80)

from sqlalchemy import text

with service.mini_session_maker() as session:
    # Check Site
    site_count = session.execute(
        text("SELECT COUNT(*) FROM site_table WHERE sito = :site"),
        {'site': site_name}
    ).scalar()
    print(f"✓ Sites in DB: {site_count}")

    # Check US
    us_count = session.execute(
        text("SELECT COUNT(*) FROM us_table WHERE sito = :site"),
        {'site': site_name}
    ).scalar()
    print(f"✓ US in DB: {us_count}")

    # Check Relationships
    rel_count = session.execute(
        text("SELECT COUNT(*) FROM us_relationships_table WHERE sito = :site"),
        {'site': site_name}
    ).scalar()
    print(f"✓ Relationships in DB: {rel_count}")

    # Check Inventario
    inv_count = session.execute(
        text("SELECT COUNT(*) FROM inventario_materiali_table WHERE sito = :site"),
        {'site': site_name}
    ).scalar()
    print(f"✓ Inventario in DB: {inv_count}")

    # Check Periodizzazione
    try:
        per_count = session.execute(
            text("SELECT COUNT(*) FROM periodizzazione_table WHERE sito = :site"),
            {'site': site_name}
        ).scalar()
        print(f"✓ Periodizzazione in DB: {per_count}")
    except:
        print("  (Periodizzazione table may not exist)")

print()
print("="*80)
print("Import Complete!")
print("="*80)
print("\nSummary:")
for table, stats in results.items():
    if isinstance(stats, dict) and 'error' not in stats:
        print(f"  {table.capitalize():20} Imported: {stats.get('imported', 0):4}  "
              f"Updated: {stats.get('updated', 0):4}  "
              f"Errors: {len(stats.get('errors', []))}")
    else:
        print(f"  {table.capitalize():20} [ERROR]")

print("\n✓ Restart Flask server to see changes:")
print("  python web_interface/app.py")
print()
