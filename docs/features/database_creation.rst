Database Creation and Management
==================================

.. versionadded:: 1.7.0

Overview
--------

PyArchInit-Mini 1.7.0 introduces comprehensive database creation and management features, allowing users to create empty PyArchInit databases with full schema from both the CLI and Web interface. This release also enhances the chronological dating system with automatic synchronization and adds a dedicated UI for viewing periodization records.

Key Features
------------

* **Empty Database Creation**: Create new SQLite or PostgreSQL databases with complete PyArchInit-Mini schema
* **Multi-Interface Support**: Available via CLI, Python API, and Web GUI
* **Automatic Dating Synchronization**: Sync dating values from US records to maintain data consistency
* **Periodization Records Viewer**: Dedicated interface for viewing and searching chronological periodization
* **Dual Menu System**: Separate menus for Dating Periods (datazioni) and Periodization Records

Empty Database Creation
-----------------------

The database creation feature provides a simple way to initialize new PyArchInit-Mini databases with all required tables and structure.

Supported Databases
^^^^^^^^^^^^^^^^^^^

* **SQLite**: File-based databases for single-user or development scenarios
* **PostgreSQL**: Server-based databases for multi-user production environments

Tables Created
^^^^^^^^^^^^^^

When creating a new database, the following 15 tables are automatically created:

Core Tables:
  * ``site_table`` - Archaeological site information
  * ``us_table`` - Stratigraphic units (Unità Stratigrafiche)
  * ``inventario_materiali_table`` - Artifact inventory
  * ``media_table`` - Media file metadata

Harris Matrix Tables:
  * ``us_relationships_table`` - Stratigraphic relationships
  * ``periodizzazione_table`` - Chronological periodization
  * ``period_table`` - Archaeological periods

User Management:
  * ``user`` - User accounts and authentication

Dating System:
  * ``datazioni_table`` - Chronological dating periods (introduced in v1.5.6)

Thesaurus Tables:
  * ``pyarchinit_thesaurus_sigle`` - Standard abbreviations
  * ``pyarchinit_thesaurus_field`` - Field definitions
  * ``pyarchinit_thesaurus_category`` - Category classifications

Extended Matrix Tables:
  * ``em_nodes_table`` - Extended Matrix nodes
  * ``em_edges_table`` - Extended Matrix edges
  * ``extended_matrix_index_table`` - Matrix indexing

Command Line Interface
----------------------

Create SQLite Database
^^^^^^^^^^^^^^^^^^^^^^^

Create a new SQLite database with full schema:

.. code-block:: bash

   pyarchinit-mini create-database \
     --type sqlite \
     --path /path/to/new_database.db

With overwrite protection disabled, attempting to create an existing database will fail:

.. code-block:: bash

   $ pyarchinit-mini create-database --type sqlite --path existing.db
   Error: Database already exists at /path/to/existing.db
   Use --overwrite to replace it

Enable overwrite to replace an existing database:

.. code-block:: bash

   pyarchinit-mini create-database \
     --type sqlite \
     --path /path/to/database.db \
     --overwrite

Create PostgreSQL Database
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a new PostgreSQL database:

.. code-block:: bash

   pyarchinit-mini create-database \
     --type postgresql \
     --host localhost \
     --port 5432 \
     --database pyarchinit_new \
     --username archaeologist \
     --password secret123

.. note::
   PostgreSQL database creation requires appropriate server permissions. The user must have ``CREATEDB`` privilege.

CLI Options
^^^^^^^^^^^

.. option:: --type, -t <sqlite|postgresql>

   Database type (required)

.. option:: --path, -p <file_path>

   Path for SQLite database file (required for SQLite)

.. option:: --host <hostname>

   PostgreSQL server hostname (required for PostgreSQL, default: localhost)

.. option:: --port <port>

   PostgreSQL server port (required for PostgreSQL, default: 5432)

.. option:: --database, -d <database_name>

   PostgreSQL database name (required for PostgreSQL)

.. option:: --username, -u <username>

   PostgreSQL username (required for PostgreSQL)

.. option:: --password <password>

   PostgreSQL password (optional, prompts if not provided)

.. option:: --overwrite

   Overwrite existing database (default: false)

Python API
----------

Module Import
^^^^^^^^^^^^^

.. code-block:: python

   from pyarchinit_mini.database.database_creator import (
       create_empty_database,
       create_sqlite_database,
       create_postgresql_database
   )

Create SQLite Database
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyarchinit_mini.database.database_creator import create_sqlite_database

   # Create new SQLite database
   result = create_sqlite_database(
       db_path='/path/to/new_database.db',
       overwrite=False
   )

   print(f"Database created: {result['message']}")
   print(f"Tables created: {result['tables_created']}")
   print(f"Size: {result['db_size']} bytes")

Result format:

.. code-block:: python

   {
       'success': True,
       'message': 'Database created successfully',
       'db_type': 'sqlite',
       'db_path': '/path/to/new_database.db',
       'tables_created': 15,
       'db_size': 102400,
       'table_names': ['site_table', 'us_table', ...]
   }

Create PostgreSQL Database
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyarchinit_mini.database.database_creator import create_postgresql_database

   # Create new PostgreSQL database
   result = create_postgresql_database(
       host='localhost',
       port=5432,
       database='pyarchinit_new',
       username='archaeologist',
       password='secret123',
       overwrite=False
   )

   print(f"Status: {result['message']}")
   print(f"Tables: {result['tables_created']}")

Unified Interface
^^^^^^^^^^^^^^^^^

The ``create_empty_database()`` function provides a unified interface for both database types:

.. code-block:: python

   from pyarchinit_mini.database.database_creator import create_empty_database

   # SQLite
   result = create_empty_database(
       db_type='sqlite',
       db_path_or_config='/path/to/database.db',
       overwrite=False
   )

   # PostgreSQL
   pg_config = {
       'host': 'localhost',
       'port': 5432,
       'database': 'pyarchinit_new',
       'username': 'archaeologist',
       'password': 'secret123'
   }
   result = create_empty_database(
       db_type='postgresql',
       db_path_or_config=pg_config,
       overwrite=False
   )

Error Handling
^^^^^^^^^^^^^^

.. code-block:: python

   from pyarchinit_mini.database.database_creator import create_sqlite_database

   try:
       result = create_sqlite_database('/path/to/database.db')
   except FileExistsError as e:
       print(f"Database already exists: {e}")
       print("Use overwrite=True to replace it")
   except ValueError as e:
       print(f"Invalid parameter: {e}")
   except Exception as e:
       print(f"Database creation failed: {e}")

Web Interface
-------------

Access
^^^^^^

Navigate to **Tools → PyArchInit Import/Export** from the main menu, then select the **Create Empty Database** tab.

.. image:: ../images/database_creator_web_ui.png
   :alt: Database Creation Web Interface
   :align: center
   :width: 100%

Create SQLite Database
^^^^^^^^^^^^^^^^^^^^^^^

1. Select **SQLite** radio button
2. Enter the absolute path for the new database file:

   .. code-block:: text

      /Users/archaeologist/Documents/my_new_project.db

3. (Optional) Check **Overwrite existing database** if you want to replace an existing file
4. Click **Create Database**
5. Monitor progress and review statistics:

   * Tables created: 15
   * Database size: ~102 KB
   * Location: Full path to created database

Create PostgreSQL Database
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Select **PostgreSQL** radio button
2. Enter connection details:

   * **Host**: Database server hostname (e.g., localhost)
   * **Port**: Server port (default: 5432)
   * **Database Name**: Name for the new database
   * **Username**: PostgreSQL username
   * **Password**: PostgreSQL password

3. (Optional) Check **Overwrite existing database**
4. Click **Create Database**
5. Review creation results

Form Validation
^^^^^^^^^^^^^^^

The web interface validates all inputs before submitting:

* **SQLite**: Verifies path is not empty
* **PostgreSQL**: Validates all required fields are filled
* **Overwrite Warning**: Displays warning when overwrite is enabled

Real-Time Feedback
^^^^^^^^^^^^^^^^^^

During database creation, the interface provides:

* Loading spinner indicating operation in progress
* Success message with detailed statistics
* Error messages with specific failure reasons
* Color-coded status indicators (green for success, red for errors)

Dating Synchronization
----------------------

Overview
^^^^^^^^

Version 1.7.0 introduces automatic synchronization between US dating values and the ``datazioni_table``. This ensures that the dating dropdown (SelectField) in the US form always contains all values currently used in the database.

The Problem
^^^^^^^^^^^

In previous versions, users experienced an issue where:

1. US records contained dating values like "XV secolo", "Età contemporanea"
2. The ``datazioni_table`` only had 7 default periods
3. The US form's dating dropdown appeared empty because values didn't match

The Solution
^^^^^^^^^^^^

The ``sync_datazioni_from_us_values()`` method automatically:

1. Queries all unique dating values from ``us_table.datazione``
2. Checks which values don't exist in ``datazioni_table``
3. Creates new ``datazioni_table`` records for missing values
4. Returns statistics about created records

Automatic Synchronization
^^^^^^^^^^^^^^^^^^^^^^^^^^

The sync runs automatically during:

* **PyArchInit Database Import**: After importing US records from PyArchInit databases
* **Database Migration**: When upgrading database schema

Manual Synchronization
^^^^^^^^^^^^^^^^^^^^^^

Users can manually trigger sync via the web interface:

1. Navigate to **Tools → PyArchInit Import/Export**
2. Click **Sync Dating Values** button (if available)
3. Review statistics: "Created X new dating records"

Python API
^^^^^^^^^^

.. code-block:: python

   from pyarchinit_mini.services.import_export_service import ImportExportService

   service = ImportExportService()
   result = service.sync_datazioni_from_us_values()

   print(f"Existing datazioni: {result['existing_count']}")
   print(f"US values found: {result['us_values_count']}")
   print(f"New records created: {result['created_count']}")
   print(f"Total after sync: {result['total_count']}")
   print(f"Created values: {result['created_values']}")

Example output:

.. code-block:: text

   Existing datazioni: 7
   US values found: 20
   New records created: 13
   Total after sync: 20
   Created values: ['XV secolo', 'XVI secolo', 'Età contemporanea', ...]

Implementation Location
^^^^^^^^^^^^^^^^^^^^^^^

The sync method is implemented in:

* Module: ``pyarchinit_mini/services/import_export_service.py``
* Method: ``sync_datazioni_from_us_values()`` (line ~1530)
* Called by: ``import_us()`` method after US import completes

Periodization Management
------------------------

Version 1.7.0 introduces a clear distinction between two chronological data types: Dating Periods and Periodization Records.

Dating Periods (Datazioni)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Controlled vocabulary of archaeological periods used in the dating dropdown

**Table**: ``datazioni_table``

**Fields**:
  * ``id_datazione`` - Unique identifier
  * ``nome_datazione`` - Period name (e.g., "Età Romana Imperiale")
  * ``fascia_cronologica`` - Chronological range (e.g., "27 a.C. - 476 d.C.")
  * ``descrizione`` - Period description

**Access**: Navigate to **Data → Dating Periods**

**Features**:
  * View all available dating periods
  * Add new periods (if permissions allow)
  * Edit existing period definitions
  * Used as choices in US form dating dropdown

.. image:: ../images/datazioni_list.png
   :alt: Dating Periods List
   :align: center
   :width: 100%

Periodization Records (Periodizzazione)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Stratigraphic unit periodization assignments linking US to archaeological periods

**Table**: ``periodizzazione_table``

**Fields**:
  * ``sito`` - Site name
  * ``area`` - Excavation area
  * ``us`` - Stratigraphic unit number
  * ``periodo_iniziale`` - Initial period
  * ``fase_iniziale`` - Initial phase
  * ``periodo_finale`` - Final period
  * ``fase_finale`` - Final phase
  * ``datazione_estesa`` - Extended dating description
  * ``affidabilita`` - Dating reliability level

**Access**: Navigate to **Data → Periodization Records**

**Features**:
  * View all US periodization assignments
  * Search by site, US number, or period
  * Pagination for large datasets (50 records per page)
  * Read-only view (records typically imported from PyArchInit)

.. image:: ../images/periodization_records.png
   :alt: Periodization Records Viewer
   :align: center
   :width: 100%

Search and Filtering
^^^^^^^^^^^^^^^^^^^^

The Periodization Records viewer provides three search fields:

.. code-block:: html

   Search by Site:    [_________________]
   Search by US:      [_________________]
   Search by Period:  [_________________]
                      [Search] [Reset]

Example searches:

* **Site**: "Dom zu Lund" - Shows all records for that site
* **US**: "1001" - Shows periodization for US 1001
* **Period**: "Romano" - Shows all records with periods containing "Romano"

Search is case-insensitive and uses partial matching (LIKE operator).

Pagination
^^^^^^^^^^

Large result sets are paginated automatically:

* **Page Size**: 50 records per page
* **Navigation**: Previous/Next buttons
* **Current Page**: Highlighted indicator
* **Total Count**: Displayed above table ("Total records: 758")

Example pagination:

.. code-block:: text

   Total records: 758

   [← Previous] [3] [Next →]

Data Source
^^^^^^^^^^^

Periodization records are typically created by:

1. **PyArchInit Import**: Automatically imported when importing from PyArchInit databases that contain ``periodizzazione_table``
2. **Manual Entry**: Can be created via Python API or database direct access
3. **Harris Matrix Analysis**: Generated by periodization analysis tools

The web interface currently provides read-only viewing. For editing, use:

* PyArchInit Desktop application
* Direct database access
* Python API

Technical Details
-----------------

Database Schema
^^^^^^^^^^^^^^^

All tables use SQLAlchemy ORM models defined in ``pyarchinit_mini/models/``:

* Base model with ``Base.metadata``
* Declarative base pattern
* Support for both SQLite and PostgreSQL
* Proper foreign key constraints
* Index optimization for common queries

Table Creation Process
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pyarchinit_mini.models.base import Base
   from sqlalchemy import create_engine

   # Import all models to register with metadata
   from pyarchinit_mini.models import (
       Site, US, User, InventarioMateriali,
       USRelationships, Periodizzazione, Period,
       Datazione, ThesaurusSigle, ThesaurusField,
       ThesaurusCategory, Media
   )

   # Create engine
   engine = create_engine(connection_string)

   # Create all tables
   Base.metadata.create_all(engine)

   # Verify creation
   inspector = inspect(engine)
   tables = inspector.get_table_names()
   print(f"Created {len(tables)} tables")

Model Import Requirements
^^^^^^^^^^^^^^^^^^^^^^^^^

The ``database_creator.py`` module must import all models to ensure they are registered with ``Base.metadata`` before calling ``create_all()``. Missing imports will result in missing tables.

Correct import pattern:

.. code-block:: python

   def _import_all_models():
       """Import all models to ensure registration with Base.metadata"""
       from ..models.base import Base
       from ..models.site import Site
       from ..models.us import US
       # ... all other models
       from ..models.thesaurus import ThesaurusSigle, ThesaurusField, ThesaurusCategory
       return Base

Use Cases
---------

Scenario 1: Start New Project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a fresh database for a new archaeological project:

.. code-block:: bash

   # CLI approach
   pyarchinit-mini create-database \
     --type sqlite \
     --path /Users/archaeologist/Projects/NewSite2024/data.db

   # Then populate with data
   pyarchinit-mini add-site --name "NewSite2024" --location "Italy"

Result:

* Empty database with full schema (15 tables, ~102 KB)
* Ready to accept site, US, and inventory data
* All relationships and constraints properly configured

Scenario 2: Create Team Database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Set up a PostgreSQL database for team collaboration:

.. code-block:: bash

   pyarchinit-mini create-database \
     --type postgresql \
     --host db.archaeology-team.org \
     --port 5432 \
     --database pompeii_excavation_2024 \
     --username lead_archaeologist

   # Prompted for password securely

Result:

* Multi-user PostgreSQL database
* Full schema with proper permissions
* Team can connect and collaborate
* Supports concurrent access

Scenario 3: Testing and Development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create temporary test databases:

.. code-block:: python

   import tempfile
   import os
   from pyarchinit_mini.database.database_creator import create_sqlite_database

   # Create temp database
   temp_dir = tempfile.mkdtemp()
   test_db = os.path.join(temp_dir, 'test.db')

   result = create_sqlite_database(test_db)
   assert result['tables_created'] == 15

   # Run tests...

   # Cleanup
   os.remove(test_db)

Scenario 4: Data Migration
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create new database and migrate data:

.. code-block:: bash

   # Step 1: Create new database
   pyarchinit-mini create-database \
     --type sqlite \
     --path /path/to/new_database.db

   # Step 2: Import data from old PyArchInit database
   pyarchinit-mini-import import-from-pyarchinit \
     --source-db "sqlite:////path/to/old_pyarchinit.db" \
     --tables all \
     --sites "Pompeii"

   # Step 3: Sync dating values
   # (Automatically triggered during import)

Result:

* New database with current schema
* All data migrated from legacy database
* Dating values synchronized
* Ready for use with PyArchInit-Mini v1.7.0

Scenario 5: Review Periodization Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

View and search periodization assignments:

1. Open web interface
2. Navigate to **Data → Periodization Records**
3. Search for site "Dom zu Lund"
4. Review 758 records showing US periodization
5. Filter by period "Medieval" to see medieval layers
6. Export results for reporting (future feature)

Troubleshooting
---------------

Database Creation Issues
^^^^^^^^^^^^^^^^^^^^^^^^

**Problem**: "Permission denied" when creating SQLite database

**Solution**:

* Verify write permissions on target directory
* Use absolute paths: ``/Users/name/Documents/db.db``
* Avoid network drives or cloud-synced folders

**Problem**: "Database already exists" error

**Solution**:

* Use ``--overwrite`` flag to replace existing database
* Choose different path/name
* Manually delete existing file first

**Problem**: PostgreSQL "permission denied for database creation"

**Solution**:

* Ensure user has CREATEDB privilege
* Connect as superuser or admin: ``GRANT CREATEDB TO username;``
* Check pg_hba.conf for connection permissions

Dating Sync Issues
^^^^^^^^^^^^^^^^^^

**Problem**: Dating dropdown still empty after sync

**Solution**:

* Verify sync completed successfully (check logs)
* Manually query: ``SELECT * FROM datazioni_table;``
* Ensure US records have non-null datazione values
* Restart web interface to reload cached data

**Problem**: Duplicate dating values created

**Solution**:

* Sync is idempotent - safe to run multiple times
* Check for case sensitivity issues ("Romano" vs "romano")
* Manually clean duplicates: ``DELETE FROM datazioni_table WHERE id_datazione IN (...);``

Periodization Viewer Issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem**: "Instance is not bound to a Session" error

**Solution**: This was fixed in v1.7.0. Ensure you're running the latest version.

**Problem**: Periodization Records shows 0 records

**Solution**:

* Check correct menu item: **Data → Periodization Records** (not Dating Periods)
* Verify data exists: ``SELECT COUNT(*) FROM periodizzazione_table;``
* Import periodization data from PyArchInit database
* Check site filter isn't hiding results

API Reference
-------------

database_creator Module
^^^^^^^^^^^^^^^^^^^^^^^

.. py:module:: pyarchinit_mini.database.database_creator

.. py:function:: create_sqlite_database(db_path: str, overwrite: bool = False) -> Dict[str, Any]

   Create an empty SQLite database with full PyArchInit-Mini schema.

   :param db_path: Absolute path to SQLite database file
   :param overwrite: Whether to overwrite existing database (default: False)
   :return: Dictionary with creation statistics
   :raises FileExistsError: If database exists and overwrite is False
   :raises ValueError: If db_path is invalid
   :raises Exception: If database creation fails

   **Returns**:

   .. code-block:: python

      {
          'success': True,
          'message': 'SQLite database created successfully',
          'db_type': 'sqlite',
          'db_path': '/path/to/database.db',
          'tables_created': 15,
          'db_size': 102400,
          'table_names': ['site_table', 'us_table', ...]
      }

.. py:function:: create_postgresql_database(host: str, port: int, database: str, username: str, password: str, overwrite: bool = False) -> Dict[str, Any]

   Create an empty PostgreSQL database with full PyArchInit-Mini schema.

   :param host: PostgreSQL server hostname
   :param port: PostgreSQL server port
   :param database: Name for the new database
   :param username: PostgreSQL username
   :param password: PostgreSQL password
   :param overwrite: Whether to overwrite existing database (default: False)
   :return: Dictionary with creation statistics
   :raises ValueError: If connection parameters are invalid
   :raises Exception: If database creation fails

   **Returns**:

   .. code-block:: python

      {
          'success': True,
          'message': 'PostgreSQL database created successfully',
          'db_type': 'postgresql',
          'host': 'localhost',
          'database': 'pyarchinit_new',
          'tables_created': 15,
          'table_names': ['site_table', 'us_table', ...]
      }

.. py:function:: create_empty_database(db_type: str, db_path_or_config: Union[str, Dict], overwrite: bool = False) -> Dict[str, Any]

   Unified interface to create empty database (SQLite or PostgreSQL).

   :param db_type: Database type ('sqlite' or 'postgresql')
   :param db_path_or_config: File path (SQLite) or config dict (PostgreSQL)
   :param overwrite: Whether to overwrite existing database (default: False)
   :return: Dictionary with creation statistics
   :raises ValueError: If db_type is invalid

   **PostgreSQL Config Dict**:

   .. code-block:: python

      {
          'host': 'localhost',
          'port': 5432,
          'database': 'pyarchinit_new',
          'username': 'archaeologist',
          'password': 'secret123'
      }

import_export_service Module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:module:: pyarchinit_mini.services.import_export_service

.. py:class:: ImportExportService

   .. py:method:: sync_datazioni_from_us_values() -> Dict[str, Any]

      Synchronize dating values from US records to datazioni table.

      Extracts all unique dating values from ``us_table.datazione`` and creates
      corresponding records in ``datazioni_table`` if they don't already exist.

      :return: Dictionary with synchronization statistics

      **Returns**:

      .. code-block:: python

         {
             'existing_count': 7,           # Datazioni before sync
             'us_values_count': 20,         # Unique US dating values
             'created_count': 13,           # New datazioni created
             'total_count': 20,             # Total datazioni after sync
             'created_values': ['XV secolo', 'XVI secolo', ...]
         }

      **Example**:

      .. code-block:: python

         from pyarchinit_mini.services.import_export_service import ImportExportService

         service = ImportExportService()
         result = service.sync_datazioni_from_us_values()

         if result['created_count'] > 0:
             print(f"Synced {result['created_count']} new dating values")
             print(f"Created: {', '.join(result['created_values'])}")
         else:
             print("All dating values already synchronized")

Web API Endpoints
^^^^^^^^^^^^^^^^^

.. http:post:: /pyarchinit-import-export/api/pyarchinit/create-database

   Create a new empty PyArchInit database via REST API.

   **Request JSON**:

   .. code-block:: json

      {
          "db_type": "sqlite",
          "db_path": "/path/to/database.db",
          "overwrite": false
      }

   Or for PostgreSQL:

   .. code-block:: json

      {
          "db_type": "postgresql",
          "pg_host": "localhost",
          "pg_port": "5432",
          "pg_database": "pyarchinit_new",
          "pg_user": "archaeologist",
          "pg_password": "secret123",
          "overwrite": false
      }

   **Response JSON** (Success):

   .. code-block:: json

      {
          "success": true,
          "message": "Database created successfully with 15 tables",
          "tables_created": 15,
          "db_type": "sqlite"
      }

   **Response JSON** (Error):

   .. code-block:: json

      {
          "success": false,
          "message": "Database already exists. Enable overwrite to replace it."
      }

   **Status Codes**:

   * ``200 OK`` - Database created successfully
   * ``400 Bad Request`` - Invalid parameters or database already exists
   * ``500 Internal Server Error`` - Database creation failed

Performance Considerations
--------------------------

Database Size
^^^^^^^^^^^^^

Empty database sizes:

* **SQLite**: ~102 KB (15 tables with schema only)
* **PostgreSQL**: ~200 KB (includes system catalog overhead)

After populating with typical site data:

* **Small Site** (100 US, 500 artifacts): ~5 MB
* **Medium Site** (1000 US, 5000 artifacts): ~50 MB
* **Large Site** (10000 US, 50000 artifacts): ~500 MB

Creation Time
^^^^^^^^^^^^^

Typical creation times:

* **SQLite**: < 1 second (local filesystem)
* **PostgreSQL** (localhost): 1-2 seconds
* **PostgreSQL** (remote): 2-5 seconds (depends on network)

Dating Sync Performance
^^^^^^^^^^^^^^^^^^^^^^^

Sync operation performance:

* **100 US records**: < 1 second
* **1000 US records**: 1-2 seconds
* **10000 US records**: 5-10 seconds

Optimization: Sync runs only once after import, results are persisted.

Best Practices
--------------

Database Creation
^^^^^^^^^^^^^^^^^

1. **Use Absolute Paths**: Always use absolute paths for SQLite databases
2. **Backup First**: Enable overwrite only after backing up existing databases
3. **Test Connections**: For PostgreSQL, test connection before creating
4. **Appropriate Type**: Use SQLite for single-user, PostgreSQL for teams
5. **Secure Passwords**: Use strong passwords for PostgreSQL databases

Dating Management
^^^^^^^^^^^^^^^^^

1. **Run Sync After Import**: Always sync after importing from PyArchInit
2. **Standardize Values**: Use consistent naming for dating periods
3. **Regular Cleanup**: Periodically review and consolidate similar values
4. **Avoid Duplicates**: Check for existing values before manual additions

Periodization Workflow
^^^^^^^^^^^^^^^^^^^^^^

1. **Import First**: Import periodization data from authoritative sources
2. **Search Efficiently**: Use site filters to narrow large result sets
3. **Export for Analysis**: Export periodization data for external analysis
4. **Maintain Consistency**: Ensure periodo_iniziale precedes periodo_finale

See Also
--------

* :doc:`pyarchinit_import_export` - Import/Export from PyArchInit databases
* :doc:`../data/database_management` - General database management
* :doc:`../data/migrations` - Database migration procedures
* :doc:`harris_matrix` - Harris Matrix visualization with periodization
* :doc:`../web/index` - Web interface documentation
* :doc:`../cli/index` - Command line interface documentation

Changelog
---------

Version 1.7.0 (2025-01-XX)
^^^^^^^^^^^^^^^^^^^^^^^^^^

**New Features**:

* ✨ Empty database creation for SQLite and PostgreSQL
* ✨ Automatic dating synchronization from US values
* ✨ Dedicated Periodization Records viewer with search and pagination
* ✨ Dual menu system for Dating Periods vs Periodization Records
* ✨ Web UI for database creation with form validation
* ✨ Python API and CLI for database creation
* ✨ REST API endpoint for database creation

**Improvements**:

* 🔧 Fixed SQLAlchemy session issues in periodization viewer
* 🔧 Separated Dating Periods and Periodization Records templates
* 🔧 Enhanced menu structure with clearer navigation
* 📖 Comprehensive documentation for all new features

**Technical**:

* New module: ``pyarchinit_mini/database/database_creator.py``
* New route: ``/api/pyarchinit/create-database`` (POST)
* New method: ``ImportExportService.sync_datazioni_from_us_values()``
* New template: ``templates/periodizzazione/periods.html``
* Updated template: ``templates/datazioni/list.html``
* Updated: Menu links in ``base.html``

**Files Modified**:

* ``pyarchinit_mini/database/database_creator.py`` (new)
* ``web_interface/pyarchinit_import_export_routes.py`` (+65 lines)
* ``web_interface/templates/pyarchinit_import_export/index.html`` (+243 lines)
* ``web_interface/templates/periodizzazione/periods.html`` (new)
* ``web_interface/templates/datazioni/list.html`` (new)
* ``web_interface/templates/base.html`` (menu updates)
* ``web_interface/app.py`` (route fixes)
* ``pyarchinit_mini/services/import_export_service.py`` (+40 lines)
