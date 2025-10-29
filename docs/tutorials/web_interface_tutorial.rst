Web Interface Complete Tutorial
=================================

.. versionadded:: 1.7.13
   Complete visual tutorial with 63 screenshots covering all Web GUI features

This tutorial provides a complete visual walkthrough of the PyArchInit-Mini Web interface, covering all features, forms, and functions with real screenshots.

.. contents:: Table of Contents
   :local:
   :depth: 2

Prerequisites
-------------

* PyArchInit-Mini v1.7.13+ installed (``pip install pyarchinit-mini``)
* Python 3.8 or higher
* Modern web browser (Chrome, Firefox, Safari, Edge)
* SQLite or PostgreSQL database

Starting the Web Server
------------------------

Launch the web interface from command line:

.. code-block:: bash

   # Start with default database
   pyarchinit-mini-web

   # Start with specific database
   DATABASE_URL="sqlite:///data/pyarchinit_mini.db" python3 -m pyarchinit_mini.web_interface.app

   # Start on custom port
   PYARCHINIT_WEB_PORT=8080 pyarchinit-mini-web

The web interface will be available at: **http://localhost:5001**

.. note::
   Port 5001 is used by default to avoid conflicts with AirPlay on macOS (which uses port 5000).

Getting Started
===============

Authentication
--------------

.. figure:: ../_static/images/webapp/001_login_page.png
   :alt: Login Page
   :align: center
   :width: 80%

   **Login Page** - Entry point to PyArchInit-Mini Web GUI

The login page is the entry point to the system.

**Default Credentials:**

* Username: ``admin``
* Password: ``admin``

.. warning::
   In production environments, always change the default credentials immediately after first login.

**Login Process:**

1. **Enter Username**

.. figure:: ../_static/images/webapp/002_highlight_Campo Username.png
   :alt: Username Field
   :align: center
   :width: 70%

   Username field highlighted

2. **Enter Password**

.. figure:: ../_static/images/webapp/003_highlight_Campo Password.png
   :alt: Password Field
   :align: center
   :width: 70%

   Password field highlighted

3. **Click Login Button**

.. figure:: ../_static/images/webapp/004_click_Bottone Login.png
   :alt: Login Button
   :align: center
   :width: 70%

   Login button highlighted

Security Features
~~~~~~~~~~~~~~~~~

* Session-based authentication
* Role-based access control (Admin, Operator, Viewer)
* Secure password hashing with bcrypt
* Auto-logout on browser close

Dashboard
=========

.. figure:: ../_static/images/webapp/005_dashboard_main.png
   :alt: Main Dashboard
   :align: center
   :width: 100%

   **Main Dashboard** - Overview of system statistics and quick navigation

After logging in, the dashboard provides:

**Statistics Cards:**

* Total Sites count
* Total Stratigraphic Units (US)
* Total Inventory Items
* Database information
* System version (v1.7.13)

**Recent Activity:**

* Latest created sites
* Recent stratigraphic units
* Recent inventory additions

**Quick Navigation:**

* Access all major modules from top navigation menu
* Responsive design adapts to screen size
* Real-time statistics updates

Site Management
===============

Sites are the top-level organizational units representing archaeological sites or excavation areas.

Site List
---------

.. figure:: ../_static/images/webapp/007_sites_list.png
   :alt: Sites List
   :align: center
   :width: 100%

   **Sites List** - Paginated list of all archaeological sites

Features:

* Paginated list (20 sites per page)
* Search by site name
* Quick view of location (Nation, Region, Province, Municipality)
* Direct links to site details
* Create new site button

Site Detail View
----------------

.. figure:: ../_static/images/webapp/009_sites_detail.png
   :alt: Site Detail
   :align: center
   :width: 100%

   **Site Detail** - Complete site information with related data

The site detail page shows:

* Complete site information
* Associated stratigraphic units
* Related inventory items
* Geographic location details
* Edit and delete options

Creating a New Site
-------------------

.. figure:: ../_static/images/webapp/011_sites_form.png
   :alt: New Site Form
   :align: center
   :width: 100%

   **Site Form** - Create or edit site information

**Required Fields:**

* Site Name (Nome Sito)

**Optional Fields:**

* Nation (Nazione)
* Region (Regione)
* Province (Provincia)
* Municipality (Comune)
* Site Definition (Definizione Sito)
* Description (Descrizione)
* English translations for definition and description

**Form Features:**

* Client-side validation
* i18n support (Italian/English)
* Auto-save draft functionality
* Cancel to return to list

Stratigraphic Units (US)
=========================

The US (Unità Stratigrafiche) module manages stratigraphic units with comprehensive archaeological data organized across **6 tabs**.

US List
-------

.. figure:: ../_static/images/webapp/013_us_list.png
   :alt: US List
   :align: center
   :width: 100%

   **US List** - Stratigraphic units with advanced filtering

Features:

* Paginated list with advanced filtering
* Filter by site, area, unit type, year
* Quick view of US number, site, and area
* Color-coded by unit type
* Bulk operations support

Creating a New US
-----------------

The US form is organized into **6 comprehensive tabs** for better data organization.

Tab 1: Basic Information
~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/015_us_form_tab1.png
   :alt: US Form Tab 1
   :align: center
   :width: 100%

   **Tab 1: Basic Information** - Site selection and primary fields

**Fields:**

* Site (required) - Select from dropdown
* US Number (required) - Unique identifier
* Area
* Stratigraphic Description
* Interpretative Description
* Formation Type (Natural/Artificial)
* Year of Excavation
* Archaeologist

Tab 2: Physical Characteristics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/017_us_form_tab2.png
   :alt: US Form Tab 2
   :align: center
   :width: 100%

   **Tab 2: Physical Characteristics** - Material properties

**Fields:**

* Unit Type (e.g., Layer, Cut, Fill)
* Color
* Consistency
* Texture
* Compaction
* Inclusions
* Soil composition details

Tab 3: Stratigraphic Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/019_us_form_tab3.png
   :alt: US Form Tab 3
   :align: center
   :width: 100%

   **Tab 3: Relationships** - Define stratigraphic connections

**Relationship Types:**

* Covers (Copre)
* Covered by (Coperto da)
* Cuts (Taglia)
* Cut by (Tagliato da)
* Fills (Riempie)
* Filled by (Riempito da)
* Equals (Uguale a)
* Adjacent to (Si appoggia a)

**Text Format:**

.. code-block:: text

   copre 1002, taglia 1005, si appoggia a 1010

These relationships are used to automatically generate the Harris Matrix.

.. tip::
   Use consistent relationship definitions to ensure accurate Harris Matrix generation.

Tab 4: Documentation
~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/021_us_form_tab4.png
   :alt: US Form Tab 4
   :align: center
   :width: 100%

   **Tab 4: Documentation** - Detailed descriptions and notes

**Fields:**

* Detailed description (long text)
* Interpretation notes
* Bibliography references
* Archaeological finds summary
* Special observations

Tab 5: Dimensions & Measurements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/023_us_form_tab5.png
   :alt: US Form Tab 5
   :align: center
   :width: 100%

   **Tab 5: Dimensions** - Measurements and spatial data

**Fields:**

* Length (cm)
* Width (cm)
* Depth/Thickness (cm)
* Volume (cubic meters)
* Surface area (square meters)
* Elevation values (top/bottom)

Tab 6: Dating & Chronology
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/025_us_form_tab6.png
   :alt: US Form Tab 6
   :align: center
   :width: 100%

   **Tab 6: Dating** - Chronological information

**Fields:**

* Chronological Period (from Datazioni table)
* Dating Method
* Terminus Post Quem (TPQ)
* Terminus Ante Quem (TAQ)
* Absolute dating
* Relative chronology notes

Advanced US Features
--------------------

**Navigation:**

* Previous/Next buttons to navigate between records
* Position counter (e.g., "Record 5 of 20")
* Respects active filters

**Data Validation:**

* Required field checking
* US number uniqueness validation
* Relationship syntax validation
* Date format validation

Material Inventory
==================

The Inventario module manages archaeological finds and materials with **8 specialized tabs**.

Inventory List
--------------

.. figure:: ../_static/images/webapp/027_inventario_list.png
   :alt: Inventory List
   :align: center
   :width: 100%

   **Inventory List** - Material finds with filtering

Features:

* Paginated list with filters
* Filter by site, area, US, find type
* Material type icons
* Conservation state indicators
* Quick search by inventory number

Creating a New Inventory Item
------------------------------

The inventory form spans **8 comprehensive tabs**.

Tab 1: Identification
~~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/029_inventario_form_tab1.png
   :alt: Inventory Form Tab 1
   :align: center
   :width: 100%

   **Tab 1: Identification** - Basic find information

**Fields:**

* Site (required)
* Inventory Number (required)
* Find Type (Ceramica, Metallo, Pietra, Osso, Vetro, etc.)
* Definition
* Object Type
* Area
* Associated US

Tab 2: Physical Description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/031_inventario_form_tab2.png
   :alt: Inventory Form Tab 2
   :align: center
   :width: 100%

   **Tab 2: Physical Description** - Material characteristics

**Fields:**

* Material
* Technique
* Color description
* Dimensions (length, width, height, diameter)
* Weight (grams)
* Thickness (mm)

Tab 3: Conservation
~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/033_inventario_form_tab3.png
   :alt: Inventory Form Tab 3
   :align: center
   :width: 100%

   **Tab 3: Conservation** - Preservation state

**Fields:**

* Conservation State (Ottimo, Buono, Discreto, Mediocre, Pessimo)
* Completeness percentage
* Degradation type
* Restoration needed
* Conservation notes

Tab 4: Decoration & Style
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/035_inventario_form_tab4.png
   :alt: Inventory Form Tab 4
   :align: center
   :width: 100%

   **Tab 4: Decoration** - Artistic attributes

**Fields:**

* Decoration technique
* Decoration description
* Decorative motifs
* Style attribution
* Artistic period

Tab 5: Context & Dating
~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/037_inventario_form_tab5.png
   :alt: Inventory Form Tab 5
   :align: center
   :width: 100%

   **Tab 5: Context** - Archaeological context and dating

**Fields:**

* Archaeological context
* Chronological period
* Cultural attribution
* Functional category
* Use interpretation

Tab 6: Documentation
~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/039_inventario_form_tab6.png
   :alt: Inventory Form Tab 6
   :align: center
   :width: 100%

   **Tab 6: Documentation** - Notes and references

**Fields:**

* Detailed description
* Bibliography
* Comparanda
* Notes
* Special observations

Tab 7: Media & Files
~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/041_inventario_form_tab7.png
   :alt: Inventory Form Tab 7
   :align: center
   :width: 100%

   **Tab 7: Media** - Attachments and multimedia

**Features:**

* Photo uploads
* Drawing attachments
* 3D model links
* Document attachments
* Media gallery viewer

Tab 8: Administrative
~~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../_static/images/webapp/043_inventario_form_tab8.png
   :alt: Inventory Form Tab 8
   :align: center
   :width: 100%

   **Tab 8: Administrative** - Storage and cataloging

**Fields:**

* Storage location
* Current location
* Cataloguer name
* Catalog date
* Last modification
* Ownership notes

Harris Matrix
=============

The Harris Matrix visualization tool generates and displays stratigraphic relationships automatically.

Harris Matrix View
------------------

.. figure:: ../_static/images/webapp/045_harris_matrix_view.png
   :alt: Harris Matrix View
   :align: center
   :width: 100%

   **Harris Matrix** - Automatic generation from US relationships

Features:

* Automatic generation from US relationships
* Topological sorting (chronological sequence)
* Directed Acyclic Graph (DAG) visualization
* Level-based layout
* Node grouping by depth

**Statistics:**

* Total nodes (US count)
* Total relationships/edges
* Matrix depth (levels)
* Isolated nodes
* Top-level nodes
* Bottom-level nodes

**Visualization Options:**

* Matplotlib rendering
* PNG export
* Zoom and pan controls
* Print-friendly format

GraphML Export
--------------

.. figure:: ../_static/images/webapp/047_harris_matrix_graphml.png
   :alt: GraphML Export
   :align: center
   :width: 100%

   **GraphML Export** - yEd Graph Editor compatible format

**Export Features:**

* GraphML format for yEd Graph Editor
* Preserves all relationships
* Node attributes included
* Edge styling compatible with yEd
* Downloadable file

**Use Cases:**

* Import into yEd for advanced editing
* Publish in research papers
* Archive with project data
* Share with collaborators

Harris Matrix Creator
=====================

Interactive graphical editor for creating and editing Harris matrices.

.. figure:: ../_static/images/webapp/049_harris_creator.png
   :alt: Harris Matrix Creator
   :align: center
   :width: 100%

   **Harris Matrix Creator** - Interactive graphical editor

Features:

* Drag-and-drop node creation
* Visual relationship drawing
* Node editing inline
* Auto-layout options
* Real-time validation

**Tools:**

* Add Node button
* Connect Nodes tool
* Delete Node/Edge
* Auto-arrange layout
* Zoom controls

**Validation:**

* Cycle detection
* DAG enforcement
* Duplicate prevention
* Orphan node warning

**Export Options:**

* Save to database
* Export to GraphML
* Generate PDF
* Create PNG image

Data Import/Export
==================

Excel Import
------------

.. figure:: ../_static/images/webapp/051_excel_import.png
   :alt: Excel Import Interface
   :align: center
   :width: 100%

   **Excel Import** - Import stratigraphic data from Excel

**Supported Formats:**

1. **Harris Matrix Template**

   * Two sheets: NODES and RELATIONSHIPS
   * Node properties in NODES sheet
   * Edges defined in RELATIONSHIPS sheet

2. **Extended Matrix Format**

   * Single sheet with inline relationships
   * Columns for relationship types
   * Compatible with Extended Matrix framework

**Features:**

* File upload with drag-and-drop
* Format auto-detection
* Validation before import
* Duplicate handling options
* Import statistics report
* Error logging

PyArchInit Import/Export
-------------------------

.. figure:: ../_static/images/webapp/053_pyarchinit_import_export.png
   :alt: PyArchInit Import/Export
   :align: center
   :width: 100%

   **PyArchInit Import/Export** - Data exchange with PyArchInit

**Import Features:**

* Import from PyArchInit SQLite databases
* Table selection (Sites, US, Inventario, Media)
* Field mapping
* Data transformation
* Conflict resolution

**Export Features:**

* Export to PyArchInit format
* Full database export
* Selective table export
* Maintains relationships
* Compatible with PyArchInit QGIS plugin

Extended Matrix Configuration
==============================

EM Node Configuration
---------------------

.. figure:: ../_static/images/webapp/055_em_node_config.png
   :alt: EM Node Config
   :align: center
   :width: 100%

   **Extended Matrix Node Configuration** - Customize node types

The Extended Matrix (EM) Node Configuration allows customization of node types and display properties.

**Node Type Management:**

* Add custom node types
* Edit node colors and shapes
* Configure node grouping
* Set default properties

**Visual Properties:**

* Fill color
* Border color
* Border width
* Node shape (rectangle, ellipse, hexagon)
* Label position
* Font settings

**Grouping Configuration:**

* Define semantic groups (e.g., "Layers", "Cuts", "Fills")
* Set group colors
* Configure group hierarchy
* Group-based filtering

Analytics
=========

The Analytics dashboard provides comprehensive data visualization and statistics.

.. figure:: ../_static/images/webapp/057_analytics_dashboard.png
   :alt: Analytics Dashboard
   :align: center
   :width: 100%

   **Analytics Dashboard** - Interactive charts and visualizations

Overview Statistics
-------------------

**Top Metrics:**

* Total Sites
* Total US
* Total Inventory Items
* Unique Regions
* Unique Provinces

Geographic Analysis
-------------------

**Charts:**

* Sites by Region (Pie Chart)
* Sites by Province (Bar Chart)
* Geographic Distribution Map

Chronological Analysis
----------------------

**Visualizations:**

* US Distribution by Period (Timeline)
* Dating Certainty Analysis
* Temporal Coverage Histogram

Typological Analysis
--------------------

**US Type Distribution:**

* Unit types breakdown (Pie Chart)
* Formation types (Natural vs Artificial)
* Stratigraphic complexity metrics

**Inventory Type Distribution:**

* Material types (Ceramica, Metallo, etc.)
* Conservation states
* Completeness distribution

Site-Level Aggregations
-----------------------

**Top 10 Lists:**

* Sites with most US
* Sites with most inventory items
* Most complex stratigraphic sequences

Conservation Analysis
---------------------

**Inventory Conservation:**

* Conservation state breakdown
* Restoration needs priority
* Degradation types

Validation
==========

Stratigraphic validation ensures data quality and identifies potential issues.

.. figure:: ../_static/images/webapp/059_validation_report.png
   :alt: Validation Report
   :align: center
   :width: 100%

   **Validation Report** - Data quality checks and issue detection

Validation Checks
-----------------

**Stratigraphic Paradoxes:**

* Circular relationships (A covers B, B covers A)
* Impossible sequences
* Inconsistent relationship types

**Cycle Detection:**

* Identify loops in the Harris Matrix
* Highlight problematic US relationships
* Suggest fixes

**Relationship Consistency:**

* Check reciprocal relationships
* Verify bidirectional consistency
* Detect missing counterparts

**Data Completeness:**

* Required fields missing
* Orphan records (US without site)
* Media without entities

Validation Report
-----------------

**Report Sections:**

1. **Summary Statistics**

   * Total issues found
   * Issues by severity (Error, Warning, Info)
   * Validation score (%)

2. **Issue Details**

   * Issue type
   * Affected records
   * Suggested fixes
   * Priority level

3. **Auto-Fix Options**

   * One-click fixes for common issues
   * Bulk resolution tools
   * Review before apply

Administration
==============

Administrative functions for database and user management.

Database Management
-------------------

.. figure:: ../_static/images/webapp/061_admin_database.png
   :alt: Database Management
   :align: center
   :width: 100%

   **Database Management** - Database operations and maintenance

**Database Operations:**

* View database information
* Database backup
* Database restore
* Optimize database
* Vacuum (SQLite)

**Upload Database:**

* Upload new SQLite database
* Replace current database
* Import from file
* Validation before replacement

**Connect to Database:**

* Configure PostgreSQL connection
* Test connection
* Switch databases
* Connection string builder

User Management
---------------

.. figure:: ../_static/images/webapp/063_admin_users.png
   :alt: User Management
   :align: center
   :width: 100%

   **User Management** - User administration

**User Administration:**

* View all users
* Create new users
* Edit user details
* Delete users (with confirmation)
* Reset passwords

**User Fields:**

* Username
* Full Name
* Email
* Role (Admin, Operator, Viewer)
* Active status
* Last login date

**Permissions:**

* Create (Sites, US, Inventario)
* Read (View data)
* Update (Edit records)
* Delete (Remove records)
* Manage Users (Admin only)

Best Practices
==============

Data Entry Guidelines
---------------------

1. **Start with Sites**

   Create site records before US or inventory

2. **Use Consistent Naming**

   Follow naming conventions for areas and US numbers

3. **Document Relationships**

   Always define stratigraphic relationships in Tab 3

4. **Add Chronology**

   Include dating information for better analysis

5. **Attach Media**

   Link photos and documents as you work

Workflow Recommendations
------------------------

1. **Plan Your Structure**

   Define sites and areas first

2. **Enter Stratigraphic Data**

   Record US with relationships as you excavate

3. **Validate Regularly**

   Run validation checks to catch issues early

4. **Generate Matrix**

   Create Harris Matrix to visualize sequences

5. **Inventory Finds**

   Record materials linked to their US

6. **Export Data**

   Regular backups and exports for safety

Performance Tips
----------------

1. **Filter Lists**

   Use filters to reduce load times on large datasets

2. **Paginate Results**

   Keep page size at 20-50 records

3. **Optimize Database**

   Run database optimization periodically

4. **Clear Browser Cache**

   If experiencing slowness

5. **Use Chrome/Firefox**

   For best performance and compatibility

Keyboard Shortcuts
==================

* ``Ctrl/Cmd + S``: Save current form
* ``Ctrl/Cmd + K``: Quick search
* ``Alt + N``: Create new record
* ``Alt + B``: Back to list
* ``Alt + P``: Previous record
* ``Alt + N``: Next record
* ``Esc``: Cancel current action

Troubleshooting
===============

Common Issues
-------------

**Cannot Login**

* Check credentials (default: admin/admin)
* Clear browser cookies and cache
* Check server is running on port 5001
* Verify database connection

**Slow Performance**

* Reduce page size in lists
* Filter data before viewing
* Check database size (optimize if large)
* Close unused browser tabs

**Import Errors**

* Verify Excel format matches template
* Check for duplicate records
* Validate data types (numbers, dates)
* Review error log in import results

**Harris Matrix Not Generating**

* Ensure US have stratigraphic relationships defined
* Check for cycles using validation tool
* Verify at least 2 US exist for the site
* Check US numbers are consistent

**Missing Data After Refresh**

* Forms may not auto-save (save manually)
* Check if you're logged in (session timeout)
* Verify database connection
* Check browser console for errors

Getting Help
------------

* **Documentation**: https://pyarchinit-mini.readthedocs.io/
* **GitHub Issues**: https://github.com/enzococca/pyarchinit-mini/issues
* **Email Support**: enzo.ccc@gmail.com

Next Steps
==========

* Explore the :doc:`desktop_gui_tutorial` for offline data entry
* Learn about :doc:`../features/harris_matrix` visualization
* Read the :doc:`../python-api/overview` for custom integrations

.. seealso::

   * :doc:`installation_tutorial`
   * :doc:`desktop_gui_tutorial`
   * :doc:`../features/extended-matrix-framework`
   * :doc:`../features/analytics`

Conclusion
==========

PyArchInit-Mini Web GUI provides a complete, modern interface for archaeological data management. This tutorial covers all major features with 63 real screenshots showing every aspect of the system.

**Key Takeaways:**

* Web interface offers 100% desktop GUI functionality
* Multi-tab forms organize complex archaeological data
* Harris Matrix auto-generation from relationships
* Comprehensive analytics and validation tools
* Multi-user support with role-based access
* Multiple import/export formats for flexibility

---

**Version**: 1.7.13
**Tutorial Last Updated**: 2025-10-29
**Screenshots**: 63 images captured from live system
