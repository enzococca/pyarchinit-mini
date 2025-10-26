=============================
Harris Matrix Import Guide
=============================

.. contents:: Table of Contents
   :depth: 3
   :local:

Overview
========

PyArchInit-Mini provides a powerful command-line tool for importing complete Harris Matrix data from **CSV** or **Excel** files. This feature allows you to:

- Create and populate an entire stratigraphic sequence from structured data
- Import nodes with Extended Matrix types (US, USM, USVA, USVB, SF, DOC, etc.)
- Define complex relationships between stratigraphic units
- Organize units by period (periodizzazione) and area
- Export imported data to GraphML and DOT formats for visualization

This is particularly useful for:

- **Migrating** existing data from other systems
- **Bulk creation** of stratigraphic sequences
- **Sharing** standardized datasets
- **Testing** and demonstration purposes

Installation
============

The Harris Matrix import tool is included with PyArchInit-Mini. Ensure you have the package installed:

.. code-block:: bash

   pip install pyarchinit-mini

The command-line tool will be available as:

.. code-block:: bash

   pyarchinit-harris-import

File Format
===========

The import file must contain **two sections**:

1. **NODES** - Defines all stratigraphic units
2. **RELATIONSHIPS** - Defines connections between units

Excel Format (.xlsx, .xls)
---------------------------

For Excel files, create **two sheets**:

**Sheet 1: NODES**

+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| us_number  | unit_type  | description            | area   | period          | phase            | file_path |
+============+============+========================+========+=================+==================+===========+
| 1001       | US         | Topsoil layer          | Area A | Medievale       | Basso Medioevo   |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1002       | USM        | North wall foundation  | Area A | Romano Imperiale| Alto Impero      |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1003       | USVA       | Foundation trench cut  | Area A | Romano Imperiale| Alto Impero      |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1004       | SF         | Bronze coin hoard      | Area A | Medievale       | Alto Medioevo    |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1005       | DOC        | Site plan drawing      | Area A |                 |                  | plan.pdf  |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+

**Sheet 2: RELATIONSHIPS**

+----------+-------+--------------+
| from_us  | to_us | relationship |
+==========+=======+==============+
| 1001     | 1002  | Covers       |
+----------+-------+--------------+
| 1002     | 1003  | Fills        |
+----------+-------+--------------+
| 1003     | 1002  | Cut_by       |
+----------+-------+--------------+
| 1004     | 1001  | >            |
+----------+-------+--------------+
| 1005     | 1002  | >>           |
+----------+-------+--------------+

CSV Format (.csv)
-----------------

For CSV files, use **two sections separated by an empty line**:

.. code-block:: text

   NODES
   us_number,unit_type,description,area,period,phase,file_path
   1001,US,Topsoil layer,Area A,Medievale,Basso Medioevo,
   1002,USM,North wall foundation,Area A,Romano Imperiale,Alto Impero,
   1003,USVA,Foundation trench cut,Area A,Romano Imperiale,Alto Impero,

   RELATIONSHIPS
   from_us,to_us,relationship
   1001,1002,Covers
   1002,1003,Fills
   1003,1002,Cut_by

Column Definitions
==================

NODES Columns
-------------

Required Columns
~~~~~~~~~~~~~~~~

:us_number:
   **Required**. The stratigraphic unit number/identifier.

   - Must be unique within the site/area combination
   - Can be numeric (``1001``) or alphanumeric (``US1001``, ``SF1009``)
   - Examples: ``1001``, ``2003``, ``SF1009``, ``USM1004``

:unit_type:
   **Required**. The Extended Matrix type of the unit.

   - Default: ``US`` (standard stratigraphic unit)
   - See `Extended Matrix Node Types`_ for all available types

Optional Columns
~~~~~~~~~~~~~~~~

:description:
   Textual description of the stratigraphic unit.

   - Free text field
   - Examples: ``"Topsoil layer"``, ``"Brown silty deposit"``

:area:
   Archaeological area or sector identifier.

   - Used for organizing units spatially
   - Examples: ``Area A``, ``Sector 1``, ``Trench 3``

:period:
   Chronological period (periodo).

   - Used for periodization (datazione) grouping
   - Examples: ``Medievale``, ``Romano Imperiale``, ``Preistorico``

:phase:
   Chronological phase (fase) within the period.

   - Provides finer chronological subdivision
   - Examples: ``Alto Medioevo``, ``Basso Medioevo``, ``Alto Impero``

:file_path:
   Path to associated file (required for ``DOC`` type units).

   - Relative or absolute path to the document
   - Examples: ``docs/site_plan.pdf``, ``/data/drawings/US1001.jpg``

RELATIONSHIPS Columns
---------------------

All columns are **required**:

:from_us:
   Source US number (the unit that has the relationship).

   - Must exist in the NODES section
   - Examples: ``1001``, ``2003``

:to_us:
   Target US number (the unit that is related to).

   - Must exist in the NODES section
   - Examples: ``1002``, ``3001``

:relationship:
   Type of stratigraphic relationship.

   - See `Relationship Types`_ for all available types
   - Can use English or Italian names

Extended Matrix Node Types
===========================

PyArchInit-Mini supports the **Extended Matrix** methodology with the following unit types:

Standard Stratigraphic Units
-----------------------------

:US:
   **Standard Stratigraphic Unit**

   - Default unit type
   - Represents physical layers, fills, cuts, etc.
   - Example: ``US1001`` - "Topsoil layer"

:USM:
   **Mural Stratigraphic Unit** (Unità Stratigrafica Muraria)

   - Represents wall units, masonry structures
   - Example: ``USM1004`` - "North wall foundation"

Virtual Units (Single-Symbol)
------------------------------

:USVA:
   **Virtual Unit Type A**

   - Represents negative features (cuts, intrusions)
   - Example: ``USVA1006`` - "Foundation trench cut"

:USVB:
   **Virtual Unit Type B**

   - Represents interface units
   - Example: ``USVB2002`` - "Ground surface interface"

:USVC:
   **Virtual Unit Type C**

   - Additional virtual unit category
   - Example: ``USVC3001`` - "Collapse event"

Finds and Special Features
---------------------------

:SF:
   **Special Find** (Singolo Frammento)

   - Individual significant artifacts
   - Example: ``SF1009`` - "Bronze coin hoard"

:VSF:
   **Virtual Special Find**

   - Aggregated or conceptual find groups
   - Example: ``VSF3003`` - "Ceramic assemblage"

:TU:
   **Topographic Unit**

   - Modern or reference surfaces
   - Example: ``TU2004`` - "Ground surface level"

:USD:
   **Stratigraphic Unit - Special**

   - Special stratigraphic context
   - Example: ``USD1008`` - "Ritual deposit"

Aggregation Nodes (Double-Symbol)
----------------------------------

:Extractor:
   **Extractor Node**

   - Groups related units for analysis
   - Example: ``Extractor3001`` - "Medieval phase aggregate"

:Combiner:
   **Combiner Node**

   - Combines multiple units into a single concept
   - Example: ``Combiner3004`` - "Medieval features combination"

:DOC:
   **Document Node**

   - Links external documentation
   - **Requires** ``file_path`` column
   - Example: ``DOC3005`` - "Site plan drawing"

:property:
   **Property Node**

   - Represents conceptual properties
   - Example: ``property_001`` - "Burning evidence"

:CON:
   **Context Node**

   - Represents archaeological contexts
   - Example: ``CON1001`` - "Domestic context"

Relationship Types
==================

Stratigraphic Relationships (for US/USM)
-----------------------------------------

English Name / Italian Name / Description:

:Covers / Copre:
   Unit A physically covers unit B

   - Indicates superposition
   - Most common relationship type

:Covered_by / Coperto da:
   Unit A is physically covered by unit B

   - Reverse of "Covers"

:Fills / Riempie:
   Unit A fills a cut or space (unit B)

   - Used with negative features

:Filled_by / Riempito da:
   Unit A (cut) is filled by unit B

   - Reverse of "Fills"

:Cuts / Taglia:
   Unit A (cut) intrudes into unit B

   - Indicates truncation or intrusion

:Cut_by / Tagliato da:
   Unit A is cut by unit B

   - Reverse of "Cuts"

:Bonds_to / Si lega a:
   Unit A bonds with unit B

   - Physical connection, often for walls

:Equal_to / Uguale a:
   Unit A equals unit B

   - Same stratigraphic unit, different contexts

:Leans_on / Si appoggia a:
   Unit A leans on unit B

   - Physical support relationship

:Continuity:
   **Contemporary Units** (no directional arrow)

   - Units exist at the same time
   - No stratigraphic priority

Extended Matrix Relationships
------------------------------

For Virtual and Special Units:

:>:
   **Connection to single-symbol units**

   - Links to USVA, USVB, USVC, SF, VSF, TU
   - Example: ``SF1009 > US1001``

:<:
   **Reverse connection from single-symbol units**

   - Reverse direction of ``>``
   - Example: ``US1001 < SF1009``

:>>:
   **Connection to double-symbol units**

   - Links to Extractor, Combiner, DOC nodes
   - Example: ``US2005 >> Extractor3001``

:<<:
   **Reverse connection from double-symbol units**

   - Reverse direction of ``>>``
   - Example: ``Extractor3001 << US2005``

Command-Line Usage
==================

Basic Import
------------

Import a Harris Matrix from a file:

.. code-block:: bash

   pyarchinit-harris-import matrix.xlsx --site "My Site"

Or from CSV:

.. code-block:: bash

   pyarchinit-harris-import data.csv --site "Archaeological Site"

With Export Options
-------------------

Import and export to GraphML:

.. code-block:: bash

   pyarchinit-harris-import matrix.xlsx --site "Site 1" --export-graphml

Import and export to both GraphML and DOT:

.. code-block:: bash

   pyarchinit-harris-import data.csv -s "Site 2" -g -d

Specify output directory:

.. code-block:: bash

   pyarchinit-harris-import matrix.xlsx --site "Site" --export-graphml --output-dir ./exports

Custom Database
---------------

Use a different database:

.. code-block:: bash

   pyarchinit-harris-import matrix.xlsx --site "Site" --db sqlite:///custom.db

PostgreSQL database:

.. code-block:: bash

   pyarchinit-harris-import data.xlsx --site "Site" \
       --db postgresql://user:pass@localhost/pyarchinit

Command-Line Options
--------------------

.. code-block:: text

   Usage: pyarchinit-harris-import [OPTIONS] FILE_PATH

   Arguments:
     FILE_PATH       Path to CSV or Excel file

   Options:
     -s, --site TEXT         Archaeological site name [required]
     -g, --export-graphml    Export to GraphML format
     -d, --export-dot        Export to DOT format
     -o, --output-dir PATH   Output directory for exports
     --db TEXT               Database URL (default: from environment)
     --help                  Show this message and exit

Complete Example
================

Step 1: Create the Excel File
------------------------------

Create a file named ``test_site.xlsx`` with two sheets:

**NODES Sheet:**

+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| us_number  | unit_type  | description            | area   | period          | phase            | file_path |
+============+============+========================+========+=================+==================+===========+
| 1001       | US         | Topsoil layer          | Area A | Medievale       | Basso Medioevo   |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1002       | US         | Brown silty deposit    | Area A | Medievale       | Alto Medioevo    |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1003       | US         | Stone collapse layer   | Area A | Medievale       | Basso Medioevo   |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1004       | USM        | North wall foundation  | Area A | Romano Imperiale| Alto Impero      |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1005       | USM        | East wall facing       | Area A | Romano Imperiale| Medio Impero     |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1006       | USVA       | Foundation trench cut  | Area A | Romano Imperiale| Alto Impero      |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1007       | US         | Fill of trench         | Area A | Romano Imperiale| Alto Impero      |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1008       | US         | Clay floor surface     | Area A | Romano Rep.     | Tardo Rep.       |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1009       | SF         | Bronze coin hoard      | Area A | Medievale       | Alto Medioevo    |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+
| 1010       | US         | Charcoal deposit       | Area A | Romano Rep.     | Medio Rep.       |           |
+------------+------------+------------------------+--------+-----------------+------------------+-----------+

**RELATIONSHIPS Sheet:**

+----------+-------+--------------+
| from_us  | to_us | relationship |
+==========+=======+==============+
| 1001     | 1002  | Covers       |
+----------+-------+--------------+
| 1002     | 1003  | Covers       |
+----------+-------+--------------+
| 1003     | 1004  | Covers       |
+----------+-------+--------------+
| 1004     | 1005  | Bonds_to     |
+----------+-------+--------------+
| 1004     | 1006  | Fills        |
+----------+-------+--------------+
| 1006     | 1007  | Cut_by       |
+----------+-------+--------------+
| 1007     | 1008  | Covers       |
+----------+-------+--------------+
| 1008     | 1010  | Covers       |
+----------+-------+--------------+
| 1009     | 1002  | >            |
+----------+-------+--------------+

Step 2: Import the Data
------------------------

.. code-block:: bash

   pyarchinit-harris-import test_site.xlsx \
       --site "Test Site EM 20 US" \
       --export-graphml \
       --export-dot \
       --output-dir ./output

**Output:**

.. code-block:: text

   ============================================================
   PyArchInit-Mini - Harris Matrix Import Tool
   ============================================================
   📖 Reading file: test_site.xlsx
      Found 10 nodes and 9 relationships

   🏛️  Site: Test Site EM 20 US
      Using existing site (ID: 1)

   📥 Importing nodes...
      ✓ US 1001: Created
      ✓ US 1002: Created
      ✓ US 1003: Created
      ✓ US 1004: Created
      ✓ US 1005: Created
      ✓ US 1006: Created
      ✓ US 1007: Created
      ✓ US 1008: Created
      ✓ US 1009: Created
      ✓ US 1010: Created

   🔗 Importing relationships...
      ✓ 1001 -> 1002 (Copre)
      ✓ 1002 -> 1003 (Copre)
      ✓ 1003 -> 1004 (Copre)
      ✓ 1004 -> 1005 (Si lega a)
      ✓ 1004 -> 1006 (Riempie)
      ✓ 1006 -> 1007 (Tagliato da)
      ✓ 1007 -> 1008 (Copre)
      ✓ 1008 -> 1010 (Copre)
      ✓ 1009 -> 1002 (>)

   ✅ Successfully imported Harris Matrix to database

   📤 Exporting...
      ✓ GraphML: ./output/Test_Site_EM_20_US.graphml
      ✓ DOT: ./output/Test_Site_EM_20_US.dot

   ============================================================
   ✅ Import completed successfully!
   ============================================================

Step 3: View in Web Interface
------------------------------

Start the web interface:

.. code-block:: bash

   pyarchinit-mini-web

Navigate to **Harris Matrix → View** and select ``Test Site EM 20 US`` to see your imported matrix.

Web Interface Integration
=========================

Creating Matrix via Web GUI
----------------------------

The web interface provides an **interactive dialog** for creating Harris Matrix data:

1. Navigate to **Harris Matrix → Create**
2. Fill in the form:

   - **Site Name**: Select or enter site name
   - **US Number**: Enter stratigraphic unit number
   - **Unit Type**: Select from dropdown (US, USM, USVA, etc.)
   - **Description**: Free text description
   - **Area**: Organizational area
   - **Period**: Select chronological period
   - **Phase**: Select chronological phase
   - **File Path**: (for DOC units) Upload or specify file

3. Add relationships using the relationship editor:

   - Click **Add Relationship**
   - Select **From US** and **To US**
   - Choose **Relationship Type**
   - Click **Save Relationship**

4. Click **Save** to create the unit

5. Repeat for all units in your matrix

6. Use **Export** to download as GraphML or DOT

Viewing and Editing
-------------------

**View Matrix:**

- Navigate to **Harris Matrix → View**
- Select site from dropdown
- View interactive graph visualization
- Pan, zoom, and explore relationships

**Edit Matrix:**

- Click on any US node in the visualization
- Edit form appears with current data
- Modify fields and save changes
- Relationships can be added or removed

**Export:**

- Click **Export to GraphML** for yEd import
- Click **Export to DOT** for Graphviz processing
- Files are downloaded to your browser

3D Integration
--------------

If 3D models are available:

- Enable **3D View** in the Harris Matrix viewer
- US nodes are highlighted on the 3D model
- Click nodes to see stratigraphic information
- Toggle between 2D matrix and 3D model views

Validation and Error Handling
==============================

The import tool performs extensive validation:

File Validation
---------------

- Checks file existence
- Validates file format (.csv, .xlsx, .xls)
- Verifies sheet names (Excel) or section markers (CSV)

Data Validation
---------------

**NODES Validation:**

- ✓ Required columns present (us_number, unit_type)
- ✓ US numbers are not empty
- ✓ Unit types are recognized
- ⚠ Warning for unknown unit types (defaults to 'US')
- ⚠ Warning for DOC units without file_path

**RELATIONSHIPS Validation:**

- ✓ Required columns present (from_us, to_us, relationship)
- ✓ US numbers are not empty
- ✓ Both from_us and to_us exist in NODES section
- ⚠ Warning for unknown relationship types

Error Messages
--------------

**File Errors:**

.. code-block:: text

   ❌ File not found: matrix.xlsx
   ❌ Unsupported file format: .txt
   ❌ Excel file must have 'NODES' sheet
   ❌ CSV must have two sections separated by empty line

**Data Errors:**

.. code-block:: text

   ❌ NODES section missing required column: us_number
   ❌ Row 5: us_number is required
   ❌ Row 12: from_us '3001' not defined in NODES section

**Warnings:**

.. code-block:: text

   ⚠️  Row 8: Unknown unit_type 'USX', defaulting to 'US'
   ⚠️  Row 15: DOC unit type should have file_path
   ⚠️  Row 20: Unknown relationship type 'IsNextTo'

Database Integration
====================

Duplicate Handling
------------------

If a US already exists with the same ``(site, area, us_number)`` combination:

- The import tool **updates** the existing record
- All fields are overwritten with new values
- Message: ``⟳ US 1001: Already exists, updating...``

For relationships:

- Duplicate relationships are **skipped**
- Message: ``⟳ 1001 -> 1002 (Copre): Already exists``

Transaction Safety
------------------

- All imports are wrapped in a database transaction
- If any error occurs, the entire import is **rolled back**
- Database remains in a consistent state

Generated IDs
-------------

For new US records, the system generates a composite ID:

.. code-block:: text

   id_us = "{site}__{area}__{us_number}"

   Examples:
   - Test Site EM 20 US__Area A__1001
   - My Site__Trench 3__2005

Periodization Records
---------------------

If ``period`` or ``phase`` is specified, a ``Periodizzazione`` record is automatically created with:

- ``periodo_iniziale`` = period
- ``fase_iniziale`` = phase
- ``datazione_estesa`` = "period - phase" (or single value if only one provided)

Best Practices
==============

1. **Plan Your Sequence**

   - Design your stratigraphic sequence before creating the file
   - Use consistent numbering schemes
   - Group related units in the same area

2. **Use Extended Matrix Types Appropriately**

   - ``US`` for physical deposits and features
   - ``USM`` for walls and structures
   - ``USVA`` for negative features (cuts)
   - ``SF`` for significant individual finds
   - ``DOC`` for linking external documentation

3. **Define Relationships Carefully**

   - Use standard stratigraphic relationships (Covers, Fills, Cuts)
   - Use ``>`` for links to single-symbol virtual units
   - Use ``>>`` for links to aggregation nodes
   - Ensure logical consistency (no circular references)

4. **Organize by Area and Period**

   - Use ``area`` to separate spatial contexts
   - Use ``period`` and ``phase`` for chronological grouping
   - This enables better visualization and analysis

5. **Test with Small Datasets**

   - Start with a few US to verify the import process
   - Check the results in the web interface
   - Expand to full dataset once validated

6. **Export for Backup**

   - Always export to GraphML after import
   - Keep exported files as backups
   - Use exported files for external visualization (yEd, Graphviz)

Troubleshooting
===============

Import Fails with Database Error
---------------------------------

**Problem:** Database connection error or lock

**Solutions:**

- Verify database is not in use by another application
- Check database URL is correct
- Ensure you have write permissions
- Try using a new database:

  .. code-block:: bash

     pyarchinit-harris-import matrix.xlsx --site "Site" --db sqlite:///new.db

Relationships Not Created
--------------------------

**Problem:** Relationships section is empty or not found

**Solutions:**

- **Excel:** Verify you have a sheet named ``RELATIONSHIPS``
- **CSV:** Ensure there's an empty line between NODES and RELATIONSHIPS sections
- Check column names are exactly: ``from_us``, ``to_us``, ``relationship``

US Numbers Not Matching
------------------------

**Problem:** Error: "from_us '1001' not defined in NODES section"

**Solutions:**

- Verify US numbers in RELATIONSHIPS match exactly those in NODES
- Check for extra spaces or formatting
- Ensure US numbers are consistent (e.g., all use "1001" not "US1001")

Period/Phase Not Showing
-------------------------

**Problem:** Periodization not visible in interface

**Solutions:**

- Check ``period`` and ``phase`` columns are filled in NODES
- Export to GraphML with ``--export-graphml`` to see periods as clusters
- View in yEd for full periodization visualization

Related Documentation
=====================

- :doc:`harris_matrix` - General Harris Matrix documentation
- :doc:`stratigraphic_relationships` - Relationship types reference
- :doc:`pyarchinit_import_export` - Other import/export features
- :doc:`../cli/index` - CLI tools overview
- :doc:`../web/index` - Web interface guide

Examples and Templates
======================

Generate Template
-----------------

To create an empty template file:

.. code-block:: bash

   pyarchinit-harris-template

This creates ``harris_matrix_template.xlsx`` with proper structure.

Sample Dataset
--------------

A complete 20-US sample is available:

.. code-block:: bash

   # Download from repository
   wget https://raw.githubusercontent.com/.../test_20us_complete.xlsx

   # Import
   pyarchinit-harris-import test_20us_complete.xlsx \
       --site "Test Site EM 20 US" \
       --export-graphml \
       --output-dir ./output

This sample includes:

- 20 stratigraphic units
- Multiple Extended Matrix types
- Complex relationships
- Period and phase grouping
- Cross-area relationships

Python API
==========

You can also use the import functionality programmatically:

.. code-block:: python

   from pyarchinit_mini.database.connection import DatabaseConnection
   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.cli.harris_import import HarrisMatrixImporter

   # Setup database
   db_url = "sqlite:///pyarchinit_mini.db"
   connection = DatabaseConnection.from_url(db_url)
   db_manager = DatabaseManager(connection)

   # Import matrix
   with db_manager.connection.get_session() as session:
       importer = HarrisMatrixImporter(session, db_manager)

       success = importer.import_matrix(
           file_path="matrix.xlsx",
           site_name="My Site",
           export_graphml=True,
           export_dot=True,
           output_dir="./exports"
       )

       if not success:
           for error in importer.errors:
               print(f"Error: {error}")

       for warning in importer.warnings:
           print(f"Warning: {warning}")

Appendix: Complete Reference
=============================

Extended Matrix Node Types Reference
-------------------------------------

===========  ===============================  ===================
Type         Description                      Symbol
===========  ===============================  ===================
US           Standard stratigraphic unit      None
USM          Mural stratigraphic unit         None
USVA         Virtual unit type A              Single-symbol
USVB         Virtual unit type B              Single-symbol
USVC         Virtual unit type C              Single-symbol
SF           Special find                     Single-symbol
VSF          Virtual special find             Single-symbol
TU           Topographic unit                 Single-symbol
USD          Stratigraphic unit - special     Single-symbol
Extractor    Extractor aggregation node       Double-symbol
Combiner     Combiner aggregation node        Double-symbol
DOC          Document node                    Double-symbol
property     Property node                    Double-symbol
CON          Context node                     None
===========  ===============================  ===================

Relationship Types Reference
-----------------------------

=================  =================  =============================
English            Italian            Usage
=================  =================  =============================
Covers             Copre              Physical superposition
Covered_by         Coperto da         Reverse of Covers
Fills              Riempie            Fills a cut/space
Filled_by          Riempito da        Reverse of Fills
Cuts               Taglia             Intrusion/truncation
Cut_by             Tagliato da        Reverse of Cuts
Bonds_to           Si lega a          Physical connection
Equal_to           Uguale a           Same unit, different context
Leans_on           Si appoggia a      Physical support
Continuity         Continuity         Contemporary units
>                  >                  Link to single-symbol unit
<                  <                  Reverse of >
>>                 >>                 Link to double-symbol unit
<<                 <<                 Reverse of >>
=================  =================  =============================

Copyright and License
=====================

PyArchInit-Mini is licensed under GPL v2.

For support, visit: https://github.com/enzococca/pyarchinit-mini

---

*Last updated: 2025-10-26*