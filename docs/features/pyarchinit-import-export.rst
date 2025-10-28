PyArchInit Import/Export - Complete Guide with Automatic Backup
=================================================================

:Date: 2025-10-28
:Version: 1.7.0+
:Status: ✅ Complete and Tested System

.. contents:: Table of Contents
   :local:
   :depth: 3

Quick Answer
------------

**YES!** When you import a PyArchInit database (SQLite or PostgreSQL) through:

- ✅ **Web GUI** (http://localhost:5000/pyarchinit-import-export)
- ✅ **Desktop GUI** (pyarchinit-mini-desk)
- ✅ **CLI** (Python scripts)
- ✅ **Python API** (programmatic integration)

The system **automatically**:

1. ✅ **Creates a backup** of the original database
2. ✅ **Adds missing i18n columns** (if needed)
3. ✅ **Imports all data** (Sites, US, Relationships, etc.)

Overview
--------

The PyArchInit Import/Export system provides bidirectional synchronization between PyArchInit and PyArchInit-Mini databases. This powerful feature allows you to:

- Migrate existing PyArchInit projects to PyArchInit-Mini
- Keep databases synchronized across multiple installations
- Create backups before any database modifications
- Add internationalization (i18n) support automatically
- Filter imports by specific archaeological sites

The system supports both **SQLite** and **PostgreSQL** databases and includes automatic safety features to protect your data.

Automatic Backup System
-----------------------

How It Works
~~~~~~~~~~~~

**Before modifying the source database**, the system automatically creates a timestamped backup:

.. code-block:: python

   from pyarchinit_mini.services.import_export_service import ImportExportService

   # Initialize the service with database connections
   service = ImportExportService(
       mini_db_connection='sqlite:///pyarchinit_mini.db',
       source_db_connection='sqlite:///my_pyarchinit.db'
   )

   # Backup is created BEFORE any modifications
   stats = service.import_us(sito_filter=['Site1'])

   # Backup path is included in the statistics
   print(f"Backup created: {stats.get('backup_path')}")
   # Output: Backup created: /path/to/my_pyarchinit.db.backup_20251028_143025

Backup Format
~~~~~~~~~~~~~

**SQLite Backup**:

.. code-block:: text

   Original database: /path/to/pyarchinit.db
   Backup created:    /path/to/pyarchinit.db.backup_20251028_143025
                                           ^^^^^^^^^^^^^^^^
                                           YYYYMMDD_HHMMSS (timestamp)

**PostgreSQL Backup**:

.. code-block:: text

   Original database: my_database (PostgreSQL)
   Backup created:    my_database_backup_20251028_143025.sql
                                  ^^^^^^^^^^^^^^^^
                                  YYYYMMDD_HHMMSS (timestamp)

Backup Features
~~~~~~~~~~~~~~~

1. ✅ **Automatic**: Created before every modification
2. ✅ **Safe**: Backup happens BEFORE any ALTER TABLE operations
3. ✅ **Timestamped**: Unique name with date/time
4. ✅ **Once per session**: Multiple imports reuse the same backup
5. ✅ **Optional**: Can be disabled with ``auto_backup=False``
6. ✅ **Verifiable**: Path returned in import statistics

Complete Import Workflows
--------------------------

1. Web GUI (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~

**URL**: http://localhost:5000/pyarchinit-import-export

**Steps**:

1. Start the Flask server:

   .. code-block:: bash

      python web_interface/app.py
      # Or: pyarchinit-mini-web

2. Open: http://localhost:5000/pyarchinit-import-export

3. **Select source database**:

   - **SQLite**: Browse and select the ``.db`` or ``.sqlite`` file
   - **PostgreSQL**: Enter host, port, database, username, password

4. **Test connection**: Click "Test Connection"

   - Shows available sites in the database

5. **Select what to import**:

   - ☑ Sites
   - ☑ US (Stratigraphic Units)
   - ☑ US Relationships
   - ☑ Inventario Materiali
   - ☑ Periodizzazione
   - ☑ Thesaurus

6. **Select sites** (optional):

   - Leave empty = import ALL sites
   - Or select specific sites from the list

7. **Click "Import"**

**What happens**:

.. code-block:: text

   1. ✓ Automatic backup created
      INFO: Creating database backup before migration...
      INFO: ✓ Database backup created: /path/to/db.backup_20251028_143025 (5.80 MB)

   2. ✓ Check i18n columns
      INFO: Checking source database for missing i18n columns...
      INFO: Table us_table already has all i18n columns

   3. ✓ Import data
      INFO: Importing sites...
      INFO: Importing US...
      INFO: Importing relationships...

   4. ✓ Summary
      ✓ Sites imported: 3
      ✓ US imported: 758
      ✓ Relationships: 2459

2. Desktop GUI
~~~~~~~~~~~~~~

**Launch**:

.. code-block:: bash

   python desktop_gui/main.py
   # Or: pyarchinit-mini-gui

**Steps**:

1. Menu: **File → Import from PyArchInit**

2. Select database:

   - **SQLite**: Browse for the ``.db`` file
   - **PostgreSQL**: Form with credentials

3. Select entities to import:

   - Sites
   - US + Relationships
   - Inventario
   - Periodizzazione

4. Click **Import**

**Backup**: Created automatically the same way as Web GUI

3. CLI (Command Line / Python Script)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complete Example
^^^^^^^^^^^^^^^^

.. code-block:: python

   #!/usr/bin/env python3
   from pyarchinit_mini.services.import_export_service import ImportExportService

   # Database paths
   MINI_DB = 'sqlite:////Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db'
   SOURCE_DB = 'sqlite:////Users/enzo/pyarchinit/pyarchinit_DB_folder/my_database.sqlite'

   # Initialize service
   service = ImportExportService(MINI_DB, SOURCE_DB)

   # Import everything for specific site(s)
   site_name = 'My Site'

   # 1. Import Site
   print("Importing site...")
   site_stats = service.import_sites(
       sito_filter=[site_name],
       auto_migrate=True,    # Add missing i18n columns
       auto_backup=True      # Create backup before migration
   )
   print(f"✓ Sites: {site_stats['imported']} imported, {site_stats['updated']} updated")
   if site_stats.get('backup_path'):
       print(f"✓ Backup: {site_stats['backup_path']}")

   # 2. Import US with Relationships
   print("\nImporting US...")
   us_stats = service.import_us(
       sito_filter=[site_name],
       import_relationships=True,
       auto_migrate=True,
       auto_backup=True  # Reuses existing backup
   )
   print(f"✓ US: {us_stats['imported']} imported, {us_stats['updated']} updated")
   print(f"✓ Relationships: {us_stats['relationships_created']}")

   # 3. Import Inventario
   print("\nImporting inventario...")
   inv_stats = service.import_inventario(
       sito_filter=[site_name],
       auto_migrate=True,
       auto_backup=True  # Reuses existing backup
   )
   print(f"✓ Inventario: {inv_stats['imported']} imported")

   # 4. Import Periodizzazione
   print("\nImporting periodizzazione...")
   per_stats = service.import_periodizzazione(
       sito_filter=[site_name]
   )
   print(f"✓ Periodizzazione: {per_stats['imported']} imported")

   # 5. Import Thesaurus (one time, no site filter)
   print("\nImporting thesaurus...")
   thes_stats = service.import_thesaurus()
   print(f"✓ Thesaurus: {thes_stats['imported']} imported")

   print("\n✓ Import complete!")

**Expected Output**:

.. code-block:: text

   Importing site...
   ✓ Sites: 1 imported, 0 updated
   ✓ Backup: /Users/enzo/pyarchinit/pyarchinit_DB_folder/my_database.sqlite.backup_20251028_143025

   Importing US...
   ✓ US: 758 imported, 0 updated
   ✓ Relationships: 2459

   Importing inventario...
   ✓ Inventario: 1234 imported

   Importing periodizzazione...
   ✓ Periodizzazione: 42 imported

   Importing thesaurus...
   ✓ Thesaurus: 156 imported

   ✓ Import complete!

Python API Integration
----------------------

Using in External Projects
~~~~~~~~~~~~~~~~~~~~~~~~~~

You can integrate PyArchInit-Mini's import/export functionality into your own Python applications. This is particularly useful for:

- Custom data migration tools
- Automated synchronization scripts
- Data pipeline integration
- Multi-database management systems

Basic Integration Example
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   """
   Custom Archaeological Data Migrator

   This example shows how to use PyArchInit-Mini's import service
   in your own Python application.
   """

   from pyarchinit_mini.services.import_export_service import ImportExportService
   import logging
   from pathlib import Path

   # Configure logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s'
   )
   logger = logging.getLogger(__name__)

   class ArchaeologicalDataMigrator:
       """Custom migrator using PyArchInit-Mini services"""

       def __init__(self, mini_db_path: str, source_db_path: str):
           """
           Initialize the migrator

           Args:
               mini_db_path: Path to PyArchInit-Mini database
               source_db_path: Path to source PyArchInit database
           """
           # Create SQLAlchemy connection strings
           self.mini_conn = f'sqlite:///{mini_db_path}'
           self.source_conn = f'sqlite:///{source_db_path}'

           # Initialize the import service
           self.service = ImportExportService(
               mini_db_connection=self.mini_conn,
               source_db_connection=self.source_conn
           )

           logger.info(f"Migrator initialized")
           logger.info(f"  Source: {source_db_path}")
           logger.info(f"  Target: {mini_db_path}")

       def migrate_site(self, site_name: str, include_media: bool = True) -> dict:
           """
           Migrate a complete archaeological site

           Args:
               site_name: Name of the site to migrate
               include_media: Whether to include inventario materiali

           Returns:
               Dictionary with migration statistics
           """
           logger.info(f"Starting migration for site: {site_name}")

           results = {
               'site': site_name,
               'statistics': {},
               'errors': []
           }

           try:
               # Step 1: Import site metadata
               logger.info("Step 1/5: Importing site metadata...")
               site_stats = self.service.import_sites(
                   sito_filter=[site_name],
                   auto_migrate=True,
                   auto_backup=True
               )
               results['statistics']['sites'] = site_stats
               logger.info(f"  ✓ Sites: {site_stats['imported']} imported")

               # Step 2: Import stratigraphic units
               logger.info("Step 2/5: Importing stratigraphic units...")
               us_stats = self.service.import_us(
                   sito_filter=[site_name],
                   import_relationships=True,
                   auto_migrate=True,
                   auto_backup=True
               )
               results['statistics']['us'] = us_stats
               logger.info(f"  ✓ US: {us_stats['imported']} imported")
               logger.info(f"  ✓ Relationships: {us_stats.get('relationships_created', 0)}")

               # Step 3: Import periodization
               logger.info("Step 3/5: Importing periodization...")
               per_stats = self.service.import_periodizzazione(
                   sito_filter=[site_name]
               )
               results['statistics']['periodizzazione'] = per_stats
               logger.info(f"  ✓ Periodizzazione: {per_stats['imported']} imported")

               # Step 4: Import material inventory (optional)
               if include_media:
                   logger.info("Step 4/5: Importing material inventory...")
                   inv_stats = self.service.import_inventario(
                       sito_filter=[site_name],
                       auto_migrate=True,
                       auto_backup=True
                   )
                   results['statistics']['inventario'] = inv_stats
                   logger.info(f"  ✓ Inventario: {inv_stats['imported']} imported")
               else:
                   logger.info("Step 4/5: Skipping material inventory")

               # Step 5: Import thesaurus (once per database)
               logger.info("Step 5/5: Importing thesaurus...")
               thes_stats = self.service.import_thesaurus()
               results['statistics']['thesaurus'] = thes_stats
               logger.info(f"  ✓ Thesaurus: {thes_stats['imported']} imported")

               logger.info(f"Migration complete for site: {site_name}")

           except Exception as e:
               logger.error(f"Migration failed: {str(e)}")
               results['errors'].append(str(e))

           return results

       def migrate_multiple_sites(self, site_names: list) -> dict:
           """
           Migrate multiple archaeological sites

           Args:
               site_names: List of site names to migrate

           Returns:
               Dictionary with overall migration statistics
           """
           overall_results = {
               'total_sites': len(site_names),
               'successful': 0,
               'failed': 0,
               'site_results': []
           }

           for site_name in site_names:
               logger.info(f"\n{'='*60}")
               result = self.migrate_site(site_name)
               overall_results['site_results'].append(result)

               if not result['errors']:
                   overall_results['successful'] += 1
               else:
                   overall_results['failed'] += 1

           logger.info(f"\n{'='*60}")
           logger.info("Overall migration summary:")
           logger.info(f"  Total sites: {overall_results['total_sites']}")
           logger.info(f"  Successful: {overall_results['successful']}")
           logger.info(f"  Failed: {overall_results['failed']}")

           return overall_results

   # Usage example
   if __name__ == '__main__':
       # Initialize migrator
       migrator = ArchaeologicalDataMigrator(
           mini_db_path='/path/to/pyarchinit_mini.db',
           source_db_path='/path/to/pyarchinit_source.db'
       )

       # Migrate single site
       result = migrator.migrate_site('Scavo Archeologico')

       # Or migrate multiple sites
       results = migrator.migrate_multiple_sites([
           'Site A',
           'Site B',
           'Site C'
       ])

**Expected Output**:

.. code-block:: text

   2025-10-28 14:30:25 - INFO - Migrator initialized
   2025-10-28 14:30:25 - INFO -   Source: /path/to/pyarchinit_source.db
   2025-10-28 14:30:25 - INFO -   Target: /path/to/pyarchinit_mini.db
   2025-10-28 14:30:25 - INFO - Starting migration for site: Scavo Archeologico
   2025-10-28 14:30:25 - INFO - Step 1/5: Importing site metadata...
   2025-10-28 14:30:26 - INFO -   ✓ Sites: 1 imported
   2025-10-28 14:30:26 - INFO - Step 2/5: Importing stratigraphic units...
   2025-10-28 14:30:32 - INFO -   ✓ US: 758 imported
   2025-10-28 14:30:32 - INFO -   ✓ Relationships: 2459
   2025-10-28 14:30:32 - INFO - Step 3/5: Importing periodization...
   2025-10-28 14:30:33 - INFO -   ✓ Periodizzazione: 42 imported
   2025-10-28 14:30:33 - INFO - Step 4/5: Importing material inventory...
   2025-10-28 14:30:38 - INFO -   ✓ Inventario: 1234 imported
   2025-10-28 14:30:38 - INFO - Step 5/5: Importing thesaurus...
   2025-10-28 14:30:39 - INFO -   ✓ Thesaurus: 156 imported
   2025-10-28 14:30:39 - INFO - Migration complete for site: Scavo Archeologico

Advanced: PostgreSQL Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   """
   PostgreSQL to PostgreSQL migration with custom configuration
   """

   from pyarchinit_mini.services.import_export_service import ImportExportService
   import os

   class PostgreSQLMigrator:
       """Specialized migrator for PostgreSQL databases"""

       def __init__(self):
           # Read credentials from environment variables (best practice)
           source_host = os.getenv('SOURCE_PG_HOST', 'localhost')
           source_port = os.getenv('SOURCE_PG_PORT', '5432')
           source_db = os.getenv('SOURCE_PG_DB', 'pyarchinit_source')
           source_user = os.getenv('SOURCE_PG_USER', 'postgres')
           source_pass = os.getenv('SOURCE_PG_PASS', '')

           target_host = os.getenv('TARGET_PG_HOST', 'localhost')
           target_port = os.getenv('TARGET_PG_PORT', '5432')
           target_db = os.getenv('TARGET_PG_DB', 'pyarchinit_mini')
           target_user = os.getenv('TARGET_PG_USER', 'postgres')
           target_pass = os.getenv('TARGET_PG_PASS', '')

           # Build connection strings
           source_conn = (
               f'postgresql://{source_user}:{source_pass}@'
               f'{source_host}:{source_port}/{source_db}'
           )

           target_conn = (
               f'postgresql://{target_user}:{target_pass}@'
               f'{target_host}:{target_port}/{target_db}'
           )

           self.service = ImportExportService(target_conn, source_conn)

       def sync_databases(self, sites: list = None) -> dict:
           """
           Synchronize databases for specified sites

           Args:
               sites: List of site names, or None for all sites

           Returns:
               Synchronization statistics
           """
           # Import all entity types
           site_stats = self.service.import_sites(
               sito_filter=sites,
               auto_migrate=True,
               auto_backup=True
           )

           us_stats = self.service.import_us(
               sito_filter=sites,
               import_relationships=True,
               auto_migrate=True,
               auto_backup=True
           )

           inv_stats = self.service.import_inventario(
               sito_filter=sites,
               auto_migrate=True,
               auto_backup=True
           )

           per_stats = self.service.import_periodizzazione(
               sito_filter=sites
           )

           return {
               'sites': site_stats,
               'us': us_stats,
               'inventario': inv_stats,
               'periodizzazione': per_stats
           }

   # Usage with environment variables
   # export SOURCE_PG_HOST=sourceserver.com
   # export SOURCE_PG_DB=pyarchinit_prod
   # export TARGET_PG_DB=pyarchinit_mini_dev
   # python migrate_postgres.py

   migrator = PostgreSQLMigrator()
   results = migrator.sync_databases(sites=['Site A', 'Site B'])

Configuration and Options
-------------------------

Import Parameters
~~~~~~~~~~~~~~~~~

All import functions support these parameters:

.. code-block:: python

   service.import_sites(
       sito_filter=['Site1', 'Site2'],  # List of sites (None = all)
       auto_migrate=True,               # Add missing i18n columns
       auto_backup=True                 # Create automatic backup
   )

   service.import_us(
       sito_filter=['Site1'],           # List of sites
       import_relationships=True,       # Also import relationships
       auto_migrate=True,               # Add i18n columns
       auto_backup=True                 # Automatic backup
   )

   service.import_inventario(
       sito_filter=['Site1'],           # List of sites
       auto_migrate=True,               # Add i18n columns
       auto_backup=True                 # Automatic backup
   )

Disabling Backup
~~~~~~~~~~~~~~~~

If you are **absolutely certain** and don't want backup:

.. code-block:: python

   # WARNING: Source database will be modified WITHOUT backup!
   stats = service.import_us(
       sito_filter=['Site1'],
       auto_migrate=True,
       auto_backup=False  # ⚠️ Disables backup
   )

**Not recommended** unless:

- Source database is a test copy
- You already have a manual backup
- Database is on a system with automatic backups

Disabling Migration
~~~~~~~~~~~~~~~~~~~

If the database already has i18n columns:

.. code-block:: python

   stats = service.import_us(
       sito_filter=['Site1'],
       auto_migrate=False,  # Don't add columns
       auto_backup=False    # No backup needed if not modifying
   )

i18n Migration System
---------------------

Automatically Added Columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the PyArchInit database doesn't have i18n (English) columns, they are added automatically:

site_table
^^^^^^^^^^

- ``definizione_sito_en`` (TEXT NULL)
- ``descrizione_en`` (TEXT NULL)

us_table
^^^^^^^^

- ``d_stratigrafica_en`` (TEXT NULL)
- ``d_interpretativa_en`` (TEXT NULL)
- ``descrizione_en`` (TEXT NULL)
- ``interpretazione_en`` (TEXT NULL)
- ``formazione_en`` (TEXT NULL)
- ``stato_di_conservazione_en`` (TEXT NULL)
- ``colore_en`` (TEXT NULL)
- ``consistenza_en`` (TEXT NULL)
- ``struttura_en`` (TEXT NULL)
- ``inclusi_en`` (TEXT NULL)
- ``campioni_en`` (TEXT NULL)
- ``documentazione_en`` (TEXT NULL)
- ``osservazioni_en`` (TEXT NULL)

inventario_materiali_table
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``tipo_reperto_en`` (TEXT NULL)
- ``definizione_reperto_en`` (TEXT NULL)
- ``descrizione_en`` (TEXT NULL)
- ``tecnologia_en`` (TEXT NULL)
- ``forma_en`` (TEXT NULL)
- ``stato_conservazione_en`` (TEXT NULL)
- ``osservazioni_en`` (TEXT NULL)

Migration Safety
~~~~~~~~~~~~~~~~

✅ **Non-destructive**: Only adds columns, NEVER modifies or deletes data
✅ **NULL default**: New columns are empty (NULL)
✅ **Idempotent**: Can be run multiple times safely
✅ **With backup**: Automatic backup before any modification
✅ **Complete logging**: All operations are logged

Verification
------------

After Import - SQL Queries
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # SQLite
   sqlite3 pyarchinit_mini.db

   # Check sites
   SELECT COUNT(*) FROM site_table WHERE sito = 'My Site';

   # Check US
   SELECT COUNT(*) FROM us_table WHERE sito = 'My Site';

   # Check relationships
   SELECT COUNT(*) FROM us_relationships_table WHERE sito = 'My Site';

   # Check periodizzazione
   SELECT COUNT(*) FROM periodizzazione_table WHERE sito = 'My Site';

After Import - Web GUI
~~~~~~~~~~~~~~~~~~~~~~~

1. **Sites**: http://localhost:5000/sites
2. **US**: http://localhost:5000/us (filter by site)
3. **Harris Matrix**: http://localhost:5000/harris-matrix
4. **Periodizzazione**: http://localhost:5000/periodizzazione

After Import - Python API
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.services.site_service import SiteService
   from pyarchinit_mini.services.us_service import USService

   # Initialize services
   db_manager = DatabaseManager('sqlite:///pyarchinit_mini.db')
   site_service = SiteService(db_manager)
   us_service = USService(db_manager)

   # Verify sites
   sites = site_service.get_all()
   print(f"Total sites: {len(sites)}")
   for site in sites:
       print(f"  - {site['sito']}")

   # Verify US for a specific site
   us_list = us_service.search(sito='My Site')
   print(f"US for 'My Site': {len(us_list)}")

   # Verify relationships
   relationships = us_service.get_relationships(sito='My Site')
   print(f"Relationships: {len(relationships)}")

Backup Restoration
------------------

SQLite Restoration
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Find the backup
   ls -lh /path/to/pyarchinit*.backup_*

   # 2. Copy backup over original
   cp /path/to/pyarchinit.db.backup_20251028_143025 /path/to/pyarchinit.db

   # 3. Verify
   sqlite3 /path/to/pyarchinit.db "SELECT COUNT(*) FROM us_table"

PostgreSQL Restoration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Find the backup SQL file
   ls -lh *_backup_*.sql

   # 2. Drop and recreate database (CAREFUL!)
   dropdb my_database
   createdb my_database

   # 3. Restore
   psql my_database < my_database_backup_20251028_143025.sql

   # 4. Verify
   psql my_database -c "SELECT COUNT(*) FROM us_table"

Import Checklist
----------------

Before Importing
~~~~~~~~~~~~~~~~

- ☑ **Manual backup exists?** (extra safety)
- ☑ **Source database correct?** (verify path/credentials)
- ☑ **Sufficient disk space?** (for automatic backup)
- ☑ **Flask server/Desktop GUI running?**
- ☑ **PyArchInit-Mini database initialized?**

During Import
~~~~~~~~~~~~~

- ☑ **Monitor logs** (Web GUI console or CLI output)
- ☑ **Verify backup created** (path shown in logs)
- ☑ **Wait for completion** (don't interrupt!)

After Import
~~~~~~~~~~~~

- ☑ **Verify counts** (sites, US, relationships)
- ☑ **Check web interface** (visualize data)
- ☑ **Test Harris Matrix** (generate and view)
- ☑ **Backup Mini database** (cp pyarchinit_mini.db)

Practical Examples
------------------

Example 1: Single Site Import
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.services.import_export_service import ImportExportService

   service = ImportExportService(
       'sqlite:///pyarchinit_mini.db',
       'sqlite:////Users/enzo/pyarchinit/my_site.db'
   )

   # Import everything for a specific site
   site_name = 'Scavo archeologico'

   service.import_sites(sito_filter=[site_name])
   service.import_us(sito_filter=[site_name], import_relationships=True)
   service.import_inventario(sito_filter=[site_name])
   service.import_periodizzazione(sito_filter=[site_name])

**Output**:

.. code-block:: text

   INFO: Creating backup: /Users/enzo/pyarchinit/my_site.db.backup_20251028_143025
   INFO: Sites imported: 1
   INFO: US imported: 125, Relationships: 456
   INFO: Inventario imported: 234
   INFO: Periodizzazione imported: 18

Example 2: Complete Import (All Sites)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   service = ImportExportService(
       'sqlite:///pyarchinit_mini.db',
       'sqlite:////Users/enzo/pyarchinit/all_sites.db'
   )

   # Import EVERYTHING (no site filter)
   service.import_sites()  # All sites
   service.import_us(import_relationships=True)  # All US
   service.import_inventario()  # All inventario
   service.import_periodizzazione()  # All periodizzazione
   service.import_thesaurus()  # Thesaurus (once)

Example 3: PostgreSQL Import
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   service = ImportExportService(
       mini_db_connection='sqlite:///pyarchinit_mini.db',
       source_db_connection='postgresql://user:password@localhost:5432/pyarchinit_db'
   )

   # Import works identically
   service.import_sites(sito_filter=['Site1'])
   service.import_us(sito_filter=['Site1'], import_relationships=True)

Example 4: Selective Import with Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.services.import_export_service import ImportExportService
   import logging

   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   def safe_import(mini_db: str, source_db: str, sites: list):
       """
       Import with comprehensive error handling

       Args:
           mini_db: Target database connection string
           source_db: Source database connection string
           sites: List of site names to import

       Returns:
           dict: Import statistics or error information
       """
       try:
           service = ImportExportService(mini_db, source_db)

           results = {
               'success': True,
               'sites': [],
               'errors': []
           }

           for site in sites:
               try:
                   logger.info(f"Importing {site}...")

                   # Import with full error tracking
                   site_stats = service.import_sites(
                       sito_filter=[site],
                       auto_migrate=True,
                       auto_backup=True
                   )

                   us_stats = service.import_us(
                       sito_filter=[site],
                       import_relationships=True,
                       auto_migrate=True,
                       auto_backup=True
                   )

                   results['sites'].append({
                       'name': site,
                       'imported': True,
                       'us_count': us_stats['imported'],
                       'rel_count': us_stats.get('relationships_created', 0)
                   })

                   logger.info(f"✓ {site}: {us_stats['imported']} US imported")

               except Exception as e:
                   logger.error(f"✗ {site}: {str(e)}")
                   results['errors'].append({
                       'site': site,
                       'error': str(e)
                   })

           if results['errors']:
               results['success'] = False

           return results

       except Exception as e:
           logger.error(f"Fatal error: {str(e)}")
           return {
               'success': False,
               'error': str(e)
           }

   # Usage
   results = safe_import(
       mini_db='sqlite:///pyarchinit_mini.db',
       source_db='sqlite:///source.db',
       sites=['Site A', 'Site B', 'Site C']
   )

   if results['success']:
       print(f"✓ Successfully imported {len(results['sites'])} sites")
   else:
       print(f"✗ Import failed with {len(results['errors'])} errors")

Backup Management
-----------------

Cleanup Old Backups
~~~~~~~~~~~~~~~~~~~

Backups accumulate over time. Clean them periodically:

.. code-block:: bash

   # List all backups
   ls -lh /path/to/pyarchinit*.backup_*

   # Remove backups older than 30 days
   find /path/to/pyarchinit_DB_folder -name "*.backup_*" -mtime +30 -delete

   # Or manually
   rm /path/to/pyarchinit.db.backup_20251001_*

Compressed Backups
~~~~~~~~~~~~~~~~~~

To save disk space:

.. code-block:: bash

   # Compress SQLite backup
   gzip /path/to/pyarchinit.db.backup_20251028_143025

   # Decompress when needed
   gunzip /path/to/pyarchinit.db.backup_20251028_143025.gz

FAQ
---

Q: Is backup created every time?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A**: Only on the first import/migration per session. Subsequent imports in the same session reuse the same backup.

.. code-block:: python

   service = ImportExportService(...)

   # First import -> Backup created
   service.import_sites()  # ✓ Backup created

   # Subsequent imports -> Reuse backup
   service.import_us()  # ✓ Using existing backup
   service.import_inventario()  # ✓ Using existing backup

Q: Where are backups saved?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A**:

- **SQLite**: Same directory as the original database
- **PostgreSQL**: Current directory where you run the script

Q: Does backup slow down import?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A**: Minimally. For SQLite, it's a file copy (fast). For PostgreSQL, it uses pg_dump (can take longer for large databases).

Q: Can I have multiple backups?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A**: Yes! Each backup has a unique timestamp. They don't overwrite previous backups.

Q: What if backup fails?
~~~~~~~~~~~~~~~~~~~~~~~~~

**A**: Import continues with a warning, but it's **strongly discouraged** to proceed if backup fails.

Q: Is the original database modified?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A**: Yes, IF i18n columns need to be added. But ONLY after backup is created. Existing data is NEVER modified.

API Reference
-------------

ImportExportService Class
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class ImportExportService:
       """
       Service for importing/exporting data between PyArchInit and PyArchInit-Mini
       """

       def __init__(
           self,
           mini_db_connection: str,
           source_db_connection: str
       ):
           """
           Initialize the import/export service

           Args:
               mini_db_connection: SQLAlchemy connection string for PyArchInit-Mini
               source_db_connection: SQLAlchemy connection string for source database
           """
           pass

       def import_sites(
           self,
           sito_filter: list = None,
           auto_migrate: bool = True,
           auto_backup: bool = True
       ) -> dict:
           """
           Import sites from source database

           Args:
               sito_filter: List of site names to import (None = all)
               auto_migrate: Add missing i18n columns automatically
               auto_backup: Create backup before modifications

           Returns:
               dict: Statistics with 'imported', 'updated', 'backup_path' keys
           """
           pass

       def import_us(
           self,
           sito_filter: list = None,
           import_relationships: bool = True,
           auto_migrate: bool = True,
           auto_backup: bool = True
       ) -> dict:
           """
           Import stratigraphic units from source database

           Args:
               sito_filter: List of site names to import (None = all)
               import_relationships: Also import US relationships
               auto_migrate: Add missing i18n columns automatically
               auto_backup: Create backup before modifications

           Returns:
               dict: Statistics with 'imported', 'updated', 'relationships_created' keys
           """
           pass

       def import_inventario(
           self,
           sito_filter: list = None,
           auto_migrate: bool = True,
           auto_backup: bool = True
       ) -> dict:
           """
           Import material inventory from source database

           Args:
               sito_filter: List of site names to import (None = all)
               auto_migrate: Add missing i18n columns automatically
               auto_backup: Create backup before modifications

           Returns:
               dict: Statistics with 'imported', 'updated' keys
           """
           pass

       def import_periodizzazione(
           self,
           sito_filter: list = None
       ) -> dict:
           """
           Import periodization data from source database

           Args:
               sito_filter: List of site names to import (None = all)

           Returns:
               dict: Statistics with 'imported', 'updated' keys
           """
           pass

       def import_thesaurus(self) -> dict:
           """
           Import thesaurus data from source database

           Note: Thesaurus is global, not site-specific

           Returns:
               dict: Statistics with 'imported', 'updated' keys
           """
           pass

Summary
-------

✅ Complete System
~~~~~~~~~~~~~~~~~~

1. ✅ **Automatic Backup**: Always created before modifications
2. ✅ **i18n Migration**: Columns added automatically
3. ✅ **Complete Import**: Sites, US, Relationships, Inventario, Periodizzazione
4. ✅ **All Interfaces**: Web GUI, Desktop GUI, CLI, Python API
5. ✅ **SQLite and PostgreSQL**: Both supported
6. ✅ **Safe and Tested**: Tested with real databases (Dom zu Lund, 758 US)

Import Statistics Example
~~~~~~~~~~~~~~~~~~~~~~~~~~

Dom zu Lund archaeological site:

- **Backup**: 4.7 MB (from 5.8 MB database)
- **Sites**: 1 imported
- **US**: 758 imported
- **Relationships**: 2,459 created
- **Periodizzazione**: 42 records
- **Time**: ~30-60 seconds (depends on size)

See Also
--------

- :doc:`harris_matrix` - Harris Matrix generation and visualization
- :doc:`database_creation` - Creating new databases
- :doc:`../python-api/overview` - Python API overview
- :doc:`../examples/python_api` - More Python examples

**The import system is now fully automated, safe, and production-ready!** 🚀
