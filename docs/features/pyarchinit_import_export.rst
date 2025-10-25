PyArchInit Import/Export
=========================

.. versionadded:: 1.2.17

Overview
--------

The PyArchInit Import/Export feature provides bidirectional data synchronization between PyArchInit (full version) and PyArchInit-Mini databases. This enables seamless data migration, collaboration workflows, and compatibility with the full PyArchInit ecosystem.

Key Capabilities
----------------

* **Bidirectional Sync**: Import from and export to PyArchInit databases
* **Multi-Database Support**: SQLite and PostgreSQL compatibility
* **Intelligent Relationship Mapping**: Automatic conversion between PyArchInit's ``rapporti`` field and PyArchInit-Mini's relational structure
* **Selective Import/Export**: Filter by site name and choose specific data tables
* **Multi-Interface**: Available in CLI, Desktop GUI, and Web interface

Supported Data Types
--------------------

Import
^^^^^^

The following data types can be imported from PyArchInit:

* **Sites** (``site_table``) - Archaeological site information
* **Stratigraphic Units** (``us_table``) - US data with automatic relationship mapping
* **Inventario Materiali** (``inventario_materiali_table``) - Artifact inventory
* **Periodizzazione** (``periodizzazione_table``) - Chronological periods
* **Thesaurus** (``pyarchinit_thesaurus_sigle``) - Terminology and abbreviations

Export
^^^^^^

The following data types can be exported to PyArchInit:

* **Sites** - Site data in PyArchInit format
* **US with Relationships** - Stratigraphic units with automatic ``rapporti`` field generation

Relationship Mapping
--------------------

One of the most important features is the intelligent mapping between PyArchInit's ``rapporti`` field and PyArchInit-Mini's relational database structure.

PyArchInit Format
^^^^^^^^^^^^^^^^^

PyArchInit stores US relationships in a TEXT field using Python list format:

.. code-block:: python

   rapporti = "[['Copre', '2'], ['Copre', '8'], ['Taglia', '5']]"

PyArchInit-Mini Format
^^^^^^^^^^^^^^^^^^^^^^^

PyArchInit-Mini uses a proper relational table ``us_relationships_table``:

.. code-block:: sql

   CREATE TABLE us_relationships_table (
       id INTEGER PRIMARY KEY,
       sito VARCHAR(350) NOT NULL,
       us_from VARCHAR(100) NOT NULL,
       us_to VARCHAR(100) NOT NULL,
       relationship_type VARCHAR(50) NOT NULL
   );

Automatic Conversion
^^^^^^^^^^^^^^^^^^^^

The import/export service automatically converts between these formats:

**Import Process:**

1. Parse ``rapporti`` string using ``ast.literal_eval()``
2. Extract relationship type and target US number
3. Create individual records in ``us_relationships_table``

**Export Process:**

1. Query all relationships for a US
2. Format as Python list of lists
3. Generate ``rapporti`` string for PyArchInit

Example:

.. code-block:: python

   # PyArchInit format
   rapporti = "[['Copre', '2', '1', 'Pompei'], ['Taglia', '5', '1', 'Pompei']]"

   # Imported to PyArchInit-Mini as:
   # Record 1: sito='Pompei', us_from=1, us_to=2, relationship_type='Copre'
   # Record 2: sito='Pompei', us_from=1, us_to=5, relationship_type='Taglia'

Command Line Interface
----------------------

Installation
^^^^^^^^^^^^

.. code-block:: bash

   pip install pyarchinit-mini>=1.2.17

Import from PyArchInit
^^^^^^^^^^^^^^^^^^^^^^^

Import all data from a specific site:

.. code-block:: bash

   pyarchinit-mini-import import-from-pyarchinit \
     --source-db "sqlite:////path/to/pyarchinit_db.sqlite" \
     --tables all \
     --sites "Scavo archeologico"

Import specific tables:

.. code-block:: bash

   pyarchinit-mini-import import-from-pyarchinit \
     --source-db "postgresql://user:pass@localhost:5432/pyarchinit" \
     --tables sites \
     --tables us \
     --sites "Pompei" \
     --sites "Ercolano" \
     --import-relationships

Export to PyArchInit
^^^^^^^^^^^^^^^^^^^^

Export sites and US to a PyArchInit database:

.. code-block:: bash

   pyarchinit-mini-import export-to-pyarchinit \
     --target-db "sqlite:////path/to/target_db.sqlite" \
     --tables sites \
     --tables us \
     --sites "Project Alpha" \
     --export-relationships

List Available Sites
^^^^^^^^^^^^^^^^^^^^

View sites in a PyArchInit database:

.. code-block:: bash

   pyarchinit-mini-import list-sites \
     --source-db "sqlite:////path/to/pyarchinit_db.sqlite"

CLI Options
^^^^^^^^^^^

.. option:: --source-db, -s <connection_string>

   Source database connection string (required for import/list operations)

.. option:: --target-db, -t <connection_string>

   Target database connection string (required for export operations)

.. option:: --tables, -T <table_name>

   Tables to import/export. Can be specified multiple times.
   Valid values: ``sites``, ``us``, ``inventario``, ``periodizzazione``, ``thesaurus``, ``all``

.. option:: --sites <site_name>

   Filter by site name. Can be specified multiple times for multiple sites.

.. option:: --import-relationships / --no-import-relationships

   Import US relationships (default: yes)

.. option:: --export-relationships / --no-export-relationships

   Export US relationships (default: yes)

Desktop GUI Interface
---------------------

Access
^^^^^^

1. Launch PyArchInit-Mini Desktop GUI
2. Navigate to **Tools → PyArchInit Import/Export**

Import Workflow
^^^^^^^^^^^^^^^

1. **Select Database Type**: Choose SQLite or PostgreSQL
2. **Enter Connection Details**:

   * **SQLite**: Browse to select database file
   * **PostgreSQL**: Enter host, port, database, username, password

3. **Test Connection**: Verify connection and load available sites
4. **Select Data**: Check tables to import and optionally filter by sites
5. **Import**: Click "Import" and monitor progress in console

Export Workflow
^^^^^^^^^^^^^^^

1. **Select Database Type**: Choose target database type
2. **Configure Connection**: Enter target database details
3. **Select Data**: Choose tables and sites to export
4. **Export**: Start export and review results

.. image:: ../images/pyarchinit_import_export_gui.png
   :alt: PyArchInit Import/Export GUI
   :align: center

Web Interface
-------------

Access
^^^^^^

Navigate to **Tools → PyArchInit Import/Export** from the main menu.

Import Process
^^^^^^^^^^^^^^

1. Select **Import** tab
2. Toggle database type (SQLite/PostgreSQL)
3. Enter connection details
4. Click **Test Connection** to verify
5. Select tables and filter options
6. Click **Start Import**
7. Monitor real-time progress and statistics

Export Process
^^^^^^^^^^^^^^

1. Select **Export** tab
2. Configure target database
3. Choose export options
4. Click **Start Export**
5. Review export results

Connection String Formats
--------------------------

SQLite
^^^^^^

.. code-block:: text

   sqlite:////absolute/path/to/database.db
   sqlite:///~/Documents/database.db
   sqlite:///relative/path/database.db

PostgreSQL
^^^^^^^^^^

.. code-block:: text

   postgresql://username:password@hostname:port/database_name

Example:

.. code-block:: text

   postgresql://archaeologist:secret123@db.example.com:5432/pyarchinit

Technical Details
-----------------

Field Mapping
^^^^^^^^^^^^^

The service maps over 50 US fields between PyArchInit and PyArchInit-Mini schemas:

* Core stratigraphic data (descrizione, interpretazione, etc.)
* Chronological periods (periodo_iniziale, fase_iniziale, etc.)
* Physical characteristics (colore, consistenza, struttura, etc.)
* Excavation metadata (schedatore, data_schedatura, etc.)
* Measurements (quota, lunghezza, profondita, etc.)

Date Handling
^^^^^^^^^^^^^

Date fields are automatically converted:

* String dates (YYYY-MM-DD, DD/MM/YYYY, etc.) → Python date objects
* Handles multiple common date formats
* Invalid dates are set to NULL

ID Generation
^^^^^^^^^^^^^

PyArchInit-Mini uses VARCHAR primary keys (``id_us``) with sequential numbering:

* Automatically generates next available ID during import
* Queries ``MAX(id_us)`` and increments
* Ensures no conflicts with existing records

Error Handling
^^^^^^^^^^^^^^

* Per-record error handling without stopping entire import
* Detailed error messages with site/US identification
* Transaction safety with individual commits
* Statistics tracking for all operations

API Reference
-------------

Python API
^^^^^^^^^^

.. code-block:: python

   from pyarchinit_mini.services.import_export_service import ImportExportService

   # Initialize service
   service = ImportExportService(
       mini_db_connection="sqlite:///./pyarchinit_mini.db",
       source_db_connection="sqlite:////path/to/pyarchinit_db.sqlite"
   )

   # Import sites
   stats = service.import_sites(sito_filter=['Pompei'])
   print(f"Imported: {stats['imported']}, Updated: {stats['updated']}")

   # Import US with relationships
   stats = service.import_us(
       sito_filter=['Pompei'],
       import_relationships=True
   )
   print(f"Imported: {stats['imported']}, Relationships: {stats['relationships_created']}")

   # Export to PyArchInit
   stats = service.export_us(
       target_db_connection="sqlite:////path/to/target.sqlite",
       sito_filter=['Pompei'],
       export_relationships=True
   )

Available Methods
^^^^^^^^^^^^^^^^^

.. py:class:: ImportExportService

   .. py:method:: import_sites(sito_filter: Optional[List[str]] = None) -> Dict[str, Any]

      Import site data from PyArchInit database.

      :param sito_filter: Optional list of site names to import
      :return: Dictionary with import statistics

   .. py:method:: import_us(sito_filter: Optional[List[str]] = None, import_relationships: bool = True) -> Dict[str, Any]

      Import stratigraphic units from PyArchInit database.

      :param sito_filter: Optional list of site names to import
      :param import_relationships: Whether to import US relationships
      :return: Dictionary with import statistics

   .. py:method:: import_inventario(sito_filter: Optional[List[str]] = None) -> Dict[str, Any]

      Import artifact inventory from PyArchInit database.

   .. py:method:: import_periodizzazione(sito_filter: Optional[List[str]] = None) -> Dict[str, Any]

      Import chronological periods from PyArchInit database.

   .. py:method:: import_thesaurus() -> Dict[str, Any]

      Import thesaurus/terminology from PyArchInit database.

   .. py:method:: export_sites(target_db_connection: str, sito_filter: Optional[List[str]] = None) -> Dict[str, Any]

      Export sites to PyArchInit format.

   .. py:method:: export_us(target_db_connection: str, sito_filter: Optional[List[str]] = None, export_relationships: bool = True) -> Dict[str, Any]

      Export US to PyArchInit format with automatic rapporti generation.

   .. py:method:: get_available_sites_in_source() -> List[str]

      List available sites in source database.

   .. py:method:: validate_database_connection(connection_string: str) -> bool

      Test database connection validity.

Use Cases
---------

Scenario 1: Migrate Complete Site
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Import all data from a PyArchInit database for a specific excavation:

.. code-block:: bash

   pyarchinit-mini-import import-from-pyarchinit \
     --source-db "sqlite:////path/to/pyarchinit_db.sqlite" \
     --tables all \
     --sites "Scavo 2024 - Area A"

Result:

* 1 site imported
* 150 US imported
* 487 relationships created
* 320 inventory items imported
* 12 chronological periods imported

Scenario 2: Collaborate with Team
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Export data to a shared PostgreSQL database:

.. code-block:: bash

   pyarchinit-mini-import export-to-pyarchinit \
     --target-db "postgresql://team:pass@server:5432/pyarchinit" \
     --tables sites \
     --tables us \
     --sites "Project Alpha" \
     --export-relationships

Scenario 3: Desktop Workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Open PyArchInit Import/Export dialog
2. Select PyArchInit database
3. Test connection → 3 sites found
4. Select all tables
5. Filter: "Scavo 2023"
6. Import complete: 85 US, 234 relationships

Troubleshooting
---------------

Connection Issues
^^^^^^^^^^^^^^^^^

**Problem**: "Database file not found"

**Solution**:

* Verify absolute path to database file
* Use forward slashes: ``/Users/name/db.sqlite``
* Expand user home: ``~/Documents/db.sqlite``

**Problem**: "Failed to connect to PostgreSQL"

**Solution**:

* Check credentials, host, and port
* Verify PostgreSQL is running
* Check firewall settings

Import Errors
^^^^^^^^^^^^^

**Problem**: "Date parsing failed"

**Solution**: Invalid date formats are automatically converted to NULL

**Problem**: "Referenced US not found"

**Solution**:

* Import US before relationships
* Use ``--import-relationships`` flag
* Ensure target US exists

Performance
-----------

Typical Import Times
^^^^^^^^^^^^^^^^^^^^

* 100 US records: ~5-10 seconds
* 1000 US records: ~30-60 seconds
* Large datasets (10,000+): 5-10 minutes

Optimization Tips
^^^^^^^^^^^^^^^^^

1. Use site filtering for selective imports
2. Import multiple tables in one operation
3. PostgreSQL is faster than SQLite for large datasets
4. Use local databases when possible

See Also
--------

* :doc:`../data/stratigraphic_units` - US data model documentation
* :doc:`harris_matrix` - Harris Matrix visualization
* :doc:`export_import` - Standard export/import features
* :doc:`../cli/index` - CLI documentation
