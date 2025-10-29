Desktop GUI Tutorial
====================

.. note::
   The Desktop GUI module is under development. This tutorial will be updated with screenshots and detailed instructions in a future release.

This tutorial guides you through using PyArchInit-Mini's desktop application for offline archaeological data management.

Overview
--------

The desktop GUI provides a native application interface for PyArchInit-Mini, offering:

* **Offline Operation**: Work without an internet connection
* **Native Performance**: Faster response times compared to web interface
* **Desktop Integration**: File system access, native dialogs, and OS integration
* **Cross-Platform**: Available on Windows, macOS, and Linux

Prerequisites
-------------

* PyArchInit-Mini installed with GUI dependencies
* Python 3.9 or higher
* Qt5 or Qt6 libraries (installed automatically)

Installation
------------

Install PyArchInit-Mini with GUI support:

.. code-block:: bash

   pip install pyarchinit-mini[gui]

Or if you already have PyArchInit-Mini installed:

.. code-block:: bash

   pip install pyarchinit-mini[gui] --upgrade

Starting the Desktop Application
---------------------------------

Launch the desktop GUI:

.. code-block:: bash

   pyarchinit-mini-gui

Or from Python:

.. code-block:: python

   from pyarchinit_mini.gui import main
   main()

The application window will open with the main interface.

Main Interface
--------------

The desktop application is organized into several main areas:

Top Menu Bar
~~~~~~~~~~~~

* **File**: New database, open database, save, export, quit
* **Edit**: Undo, redo, preferences
* **View**: Switch between modules, toggle sidebars
* **Data**: Sites, US, inventory, documentation
* **Tools**: Harris Matrix, reports, import/export
* **Help**: Documentation, about, check for updates

Sidebar Navigation
~~~~~~~~~~~~~~~~~~

The left sidebar provides quick access to:

* **Sites Module**: Manage archaeological sites
* **US Module**: Stratigraphic units
* **Inventory Module**: Finds and artifacts
* **Documentation Module**: Files and media
* **Matrix Module**: Harris Matrix visualization
* **Reports Module**: Generate PDF reports

Main Content Area
~~~~~~~~~~~~~~~~~

The central area displays the selected module's content:

* Data entry forms
* Lists and tables
* Visualization panels
* Report previews

Status Bar
~~~~~~~~~~

The bottom status bar shows:

* Current database path
* Record count
* Active user
* Connection status

Working with Sites
------------------

Creating a New Site
~~~~~~~~~~~~~~~~~~~

1. Click **Data → Sites** or select **Sites** from the sidebar
2. Click the **New Site** button in the toolbar
3. Fill in the site information form:

   * Site name (required)
   * Location details
   * Site definition
   * Description
   * Coordinates (optional)

4. Click **Save** to create the site

Editing Existing Sites
~~~~~~~~~~~~~~~~~~~~~~

1. Select a site from the sites list
2. Click the **Edit** button or double-click the site
3. Modify the site information
4. Click **Save** to apply changes

Deleting Sites
~~~~~~~~~~~~~~

1. Select a site from the sites list
2. Click the **Delete** button
3. Confirm the deletion in the dialog

.. warning::
   Deleting a site will also delete all associated stratigraphic units and finds. This action cannot be undone.

Managing Stratigraphic Units
-----------------------------

Creating US Records
~~~~~~~~~~~~~~~~~~~

1. Navigate to **Data → US** or select **US** from the sidebar
2. Click **New US** in the toolbar
3. Fill in the US form:

   * Select site (required)
   * Area and US number
   * Stratigraphic description
   * Interpretative description
   * Physical characteristics
   * Dating information

4. Click **Save** to create the US record

Defining Relationships
~~~~~~~~~~~~~~~~~~~~~~

1. Open a US record
2. Click the **Relationships** tab
3. Add relationships:

   * Click **Add Relationship**
   * Select relationship type (covers, cuts, fills, etc.)
   * Select related US
   * Click **Add**

4. The relationships will automatically update the Harris Matrix

Inventory Management
--------------------

Recording Finds
~~~~~~~~~~~~~~~

1. Go to **Data → Inventory**
2. Click **New Inventory Item**
3. Enter find details:

   * Inventory number
   * Find type and classification
   * Description
   * Provenance (site, area, US)
   * Conservation status
   * Measurements
   * Dating

4. Click **Save**

Attaching Photos
~~~~~~~~~~~~~~~~

1. Open an inventory item
2. Click the **Media** tab
3. Click **Add Photo**
4. Select image files from your computer
5. Add captions and metadata
6. Click **Save**

Harris Matrix Visualization
----------------------------

Generating the Matrix
~~~~~~~~~~~~~~~~~~~~~

1. Navigate to **Tools → Harris Matrix**
2. Select the site
3. Click **Generate Matrix**

The application will:

* Analyze all stratigraphic relationships
* Calculate the correct layering sequence
* Generate an interactive visualization

Interacting with the Matrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Zoom**: Use mouse wheel or pinch gesture
* **Pan**: Click and drag
* **Select US**: Click on a node to see details
* **Highlight Path**: Right-click a node to trace relationships

Exporting the Matrix
~~~~~~~~~~~~~~~~~~~~

1. Click **Export** in the Matrix toolbar
2. Choose format:

   * SVG (vector graphics)
   * PNG (raster image)
   * PDF (document)
   * GraphML (for analysis software)

3. Select destination and click **Save**

Reports and Export
------------------

Generating Reports
~~~~~~~~~~~~~~~~~~

1. Go to **Tools → Reports**
2. Select report type:

   * Site Report
   * US Summary
   * Inventory Catalog
   * Harris Matrix Document

3. Configure report options
4. Click **Generate**
5. Preview the report
6. Click **Export** to save as PDF

Exporting Data
~~~~~~~~~~~~~~

Export your data for backup or analysis:

1. Go to **File → Export**
2. Select export format:

   * Excel (.xlsx)
   * CSV (comma-separated)
   * JSON (structured data)
   * SQL dump (full backup)

3. Choose what to export:

   * All data
   * Selected site only
   * Custom selection

4. Click **Export** and choose destination

Importing Data
~~~~~~~~~~~~~~

Import data from external sources:

1. Go to **File → Import**
2. Select import format
3. Choose file to import
4. Map fields (if required)
5. Review preview
6. Click **Import**

Preferences and Settings
------------------------

Access preferences: **Edit → Preferences**

General Settings
~~~~~~~~~~~~~~~~

* Default database location
* Auto-save interval
* Language selection
* Date and number formats

Display Settings
~~~~~~~~~~~~~~~~

* Theme (light/dark)
* Font size
* Grid lines in tables
* Icon size

Database Settings
~~~~~~~~~~~~~~~~~

* Default database type (SQLite/PostgreSQL)
* Connection timeout
* Backup location
* Auto-backup schedule

Keyboard Shortcuts
------------------

Common shortcuts:

* ``Ctrl+N`` (``Cmd+N`` on macOS): New record
* ``Ctrl+S`` (``Cmd+S``): Save
* ``Ctrl+F`` (``Cmd+F``): Find/Search
* ``Ctrl+Z`` (``Cmd+Z``): Undo
* ``Ctrl+Shift+Z`` (``Cmd+Shift+Z``): Redo
* ``F5``: Refresh data
* ``Ctrl+Q`` (``Cmd+Q``): Quit application

Troubleshooting
---------------

Application Won't Start
~~~~~~~~~~~~~~~~~~~~~~~

* Verify GUI dependencies are installed: ``pip install pyarchinit-mini[gui]``
* Check Python version: ``python --version`` (must be 3.9+)
* Try running with verbose output: ``pyarchinit-mini-gui --verbose``

Database Connection Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

* Verify database path in **Edit → Preferences → Database**
* Check file permissions for SQLite database files
* For PostgreSQL, ensure server is running

Performance Issues
~~~~~~~~~~~~~~~~~~

* Close unused modules
* Reduce auto-save frequency
* Limit displayed records using filters
* Check available disk space

Tips and Best Practices
------------------------

Data Entry
~~~~~~~~~~

* Use keyboard shortcuts to speed up data entry
* Configure auto-save to prevent data loss
* Use templates for repetitive entries
* Regularly backup your database

Organization
~~~~~~~~~~~~

* Use consistent naming conventions
* Create a site-specific thesaurus
* Document your workflow in site notes
* Review and validate data regularly

Collaboration
~~~~~~~~~~~~~

* Use version control for database files
* Export regularly for team sharing
* Document changes in commit messages
* Use PostgreSQL for multi-user access

Next Steps
----------

* Explore the **Web Interface Tutorial** for remote access
* Learn about **Harris Matrix** advanced features
* Read the **API Documentation** for automation
* Join the community forum for tips and support

.. seealso::

   * :doc:`installation_tutorial`
   * :doc:`web_interface_tutorial`
   * :doc:`../user/desktop_gui`
   * :doc:`../developer/api`

Getting Help
------------

* **Documentation**: https://docs.pyarchinit.org
* **GitHub Issues**: https://github.com/pyarchinit/pyarchinit-mini/issues
* **Community Forum**: https://forum.pyarchinit.org
* **Video Tutorials**: https://www.youtube.com/c/PyArchInit
