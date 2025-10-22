Desktop GUI Documentation
=========================

PyArchInit-Mini provides a native desktop application built with Tkinter, offering a traditional desktop experience for managing archaeological data with offline capabilities.

.. toctree::
   :maxdepth: 2
   :caption: Desktop GUI Contents:

   quickstart
   interface_overview
   sites_management
   us_management
   inventory_management
   harris_matrix
   analytics
   export_import
   media_manager
   tools_menu
   database_configuration
   internationalization

Quick Start
-----------

Starting the Desktop Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To launch the desktop GUI:

.. code-block:: bash

   pyarchinit-mini-gui

Or from Python:

.. code-block:: python

   from pyarchinit_mini.desktop_gui.gui_app import main
   main()

System Requirements
~~~~~~~~~~~~~~~~~~~

- Python 3.8 or higher
- Tkinter (included with Python)
- 1024x768 minimum resolution
- 4GB RAM recommended
- Windows, macOS, or Linux

First Launch
~~~~~~~~~~~~

On first launch:

1. Database selection dialog appears
2. Choose SQLite (default) or PostgreSQL
3. For SQLite: automatic setup in ~/.pyarchinit_mini/
4. For PostgreSQL: enter connection details
5. Main window opens with dashboard

Interface Overview
------------------

Main Window Layout
~~~~~~~~~~~~~~~~~~

The desktop GUI features a traditional menu-driven interface:

**Menu Bar:**

- File (New, Open, Save, Export, Exit)
- Edit (Cut, Copy, Paste, Find)
- View (Sites, US, Inventory, Tools)
- Tools (Harris Matrix, Analytics, Export/Import)
- Database (Connect, Info, Backup)
- Window (Cascade, Tile)
- Help (Documentation, About)

**Toolbar:**

Quick access buttons for:

- New Site
- New US  
- New Inventory
- Search
- Refresh
- Settings

**Status Bar:**

- Current database
- Record count
- User info
- Connection status

Navigation
~~~~~~~~~~

Multiple ways to navigate:

1. **Menu Navigation**: Traditional File → View → Sites
2. **Toolbar Buttons**: Quick access to common actions
3. **Keyboard Shortcuts**: Ctrl+N for new, Ctrl+S for save
4. **Tree View**: Hierarchical site/US browser

Sites Management
----------------

Sites List Window
~~~~~~~~~~~~~~~~~

Access via View → Sites:

**Features:**

- Sortable columns
- Right-click context menu
- Double-click to edit
- Search box with filters
- Print preview

**Columns:**

- ID
- Site Name
- Nation  
- Region
- Comune
- Province
- Definition (IT)
- Definition (EN)

Site Dialog
~~~~~~~~~~~

Create/Edit site dialog:

**Layout:**

- Form fields in logical groups
- Required fields marked with *
- Tab order optimization
- Validation indicators

**Fields:**

- Site Name* (Entry widget)
- Location/Nation (Combobox)
- Region (Combobox)
- Comune (Entry)
- Province (Entry)  
- Definition IT (Text widget)
- Definition EN (Text widget)

**Buttons:**

- Save (Ctrl+S)
- Save & New
- Cancel (Esc)
- Reset

Stratigraphic Units (US) Management
------------------------------------

US List Window
~~~~~~~~~~~~~~

Accessed via View → Stratigraphic Units:

**Tree View Display:**

Shows hierarchical structure:

.. code-block::

   📁 Pompei
   ├── 📁 Area A
   │   ├── US 1001
   │   ├── US 1002
   │   └── US 1003
   └── 📁 Area B
       ├── US 2001
       └── US 2002

**List View Columns:**

- Site
- Area
- US Number
- Type
- Definition
- Period
- Relationships

US Extended Dialog
~~~~~~~~~~~~~~~~~~

The US form with 49 fields across 6 tabs:

**Tab 1: Dati Generali**

.. code-block::

   ┌─────────────────────────────────────┐
   │ Sito*: [Dropdown_______________▼]    │
   │ Area:  [_______] US*: [_______]     │
   │ Anno:  [_______]                    │
   │                                     │
   │ D. Stratigrafica: [Text area_____]  │
   │                   [______________]  │
   │ D. Interpretativa:[Text area_____]  │
   │                   [______________]  │
   └─────────────────────────────────────┘

**Tab 2: Dati Stratigrafici**

Period selectors, phase fields, unit type dropdown

**Tab 3: Rapporti**

Relationship entry with validation:

- Smart US picker dialog
- Reciprocal relationship checking
- Visual relationship browser

**Tab 4: Caratteristiche**

Physical characteristics with ICCD thesaurus:

- Color picker
- Consistency dropdown
- Inclusions checklist

**Tab 5: Documentazione**

- Multi-line text fields
- File attachments
- Photo references

**Tab 6: Misure**

Numeric entries with units

Tab Navigation
~~~~~~~~~~~~~~

- Click tab headers
- Ctrl+Tab for next tab
- Ctrl+Shift+Tab for previous
- Red dot indicates validation errors

Inventory Management
--------------------

Inventory List
~~~~~~~~~~~~~~

View → Material Inventory:

**Advanced Features:**

- Thumbnail view option
- Grouping by type/material
- Quick filters toolbar
- Bulk operations

Inventory Extended Dialog
~~~~~~~~~~~~~~~~~~~~~~~~~

37 fields across 8 tabs:

**Special Widgets:**

1. **Photo Display**
   
   - Thumbnail preview
   - Click to enlarge
   - Drag & drop upload

2. **ICCD Lookups**
   
   - Type ahead search
   - Hierarchical browser
   - Recent selections

3. **Numeric Spinboxes**
   
   - Up/down arrows
   - Range validation
   - Unit labels

**Tab Layout Example:**

.. code-block::

   ┌─ Dati Principali ─┬─ Misure ─┬─ Datazione ─┐
   │                   │          │             │
   │ N. Inventario*: [____]                     │
   │ Tipo Reperto:   [Dropdown▼]                │
   │ Definizione:    [_____________________]    │
   │                                            │
   │ [Photo     ]    Classe: [Ceramica    ▼]    │
   │ [Preview   ]    Stato:  [Integro     ▼]    │
   │ [Area      ]                               │
   │                                            │
   │ Sito: [Pompei      ▼] Area: [A] US: [1001] │
   └────────────────────────────────────────────┘

Harris Matrix Viewer
--------------------

Matrix Window
~~~~~~~~~~~~~

Tools → Harris Matrix:

**Controls Panel:**

- Site selector
- Grouping options
- Zoom controls  
- Export buttons
- Print setup

**Visualization Area:**

- Canvas with pan/zoom
- Node interaction
- Relationship lines
- Period coloring

**Features:**

1. **Interactive Nodes**
   
   - Click for details
   - Double-click to edit US
   - Hover for tooltip

2. **Layout Options**
   
   - Hierarchical (default)
   - Force-directed
   - Circular
   - Custom positioning

3. **Export Formats**
   
   - PNG (300 DPI)
   - PDF (vector)
   - SVG (editable)
   - GraphML (yEd)

Matrix Editor
~~~~~~~~~~~~~

Right-click node → Edit Relationships:

.. code-block::

   ┌─ Edit Relationships: US 1001 ──────┐
   │                                    │
   │ Covers:     [1002, 1003      ][+] │
   │ Covered by: [________________][+] │
   │ Fills:      [________________][+] │
   │ Filled by:  [________________][+] │
   │ Cuts:       [________________][+] │
   │ Cut by:     [________________][+] │
   │                                    │
   │ [Validate] [Apply] [Cancel]        │
   └────────────────────────────────────┘

Analytics Dashboard
-------------------

Analytics Window
~~~~~~~~~~~~~~~~

Tools → Analytics Dashboard:

**Layout:**

Matplotlib canvas with 8 subplots:

.. code-block::

   ┌───────────┬───────────┐
   │ Sites by  │ Sites by  │
   │  Region   │ Province  │
   ├───────────┼───────────┤
   │  US by    │  US by    │
   │  Period   │   Type    │
   ├───────────┼───────────┤
   │ Finds by  │ Finds by  │
   │   Type    │  State    │
   ├───────────┼───────────┤
   │ Top Sites │ Top Sites │
   │  by US    │ by Finds  │
   └───────────┴───────────┘

**Toolbar:**

- Save figure
- Zoom/Pan
- Reset view
- Configure subplots

Export/Import Dialog
--------------------

Export Tab
~~~~~~~~~~

Tools → Export/Import Data:

.. code-block::

   ┌─ Export ─┬─ Import ─┐
   │                    │
   │ Data Type:         │
   │ ○ Sites            │
   │ ● US               │
   │ ○ Inventory        │
   │                    │
   │ Format: [Excel ▼]  │
   │                    │
   │ Filters:           │
   │ Site: [All    ▼]   │
   │                    │
   │ Output: [Browse..] │
   │         [Export]   │
   └────────────────────┘

Import Tab
~~~~~~~~~~

Drag & drop area with:

- File preview grid
- Column mapping
- Validation results
- Import progress

Media Manager
-------------

Advanced Media Dialog
~~~~~~~~~~~~~~~~~~~~~

Tools → Media Manager:

**Three-Panel Layout:**

1. **Folder Tree** (Left)
   
   - Sites hierarchy
   - Media types
   - Tags

2. **Thumbnail Grid** (Center)
   
   - Image previews
   - File info overlay
   - Multi-select

3. **Details Panel** (Right)
   
   - Large preview
   - Metadata editor
   - Related entities

**Toolbar Actions:**

- Upload files
- Create folder
- Delete selected
- Batch rename
- Generate thumbnails

Database Configuration
----------------------

Connection Dialog
~~~~~~~~~~~~~~~~~

Database → Connect:

.. code-block::

   ┌─ Database Configuration ────────┐
   │                                 │
   │ Type: ○ SQLite  ● PostgreSQL    │
   │                                 │
   │ ┌─ PostgreSQL Settings ───────┐ │
   │ │ Host: [localhost_______]    │ │
   │ │ Port: [5432___________]     │ │
   │ │ Database: [pyarchinit__]    │ │
   │ │ Username: [____________]     │ │
   │ │ Password: [************]     │ │
   │ └─────────────────────────────┘ │
   │                                 │
   │ [Test Connection] [Save] [Cancel]│
   └─────────────────────────────────┘

Backup Dialog
~~~~~~~~~~~~~

Database → Backup:

- Automatic filename
- Compression option
- Schedule setup
- Restore function

Internationalization
--------------------

Language Selection
~~~~~~~~~~~~~~~~~~

View → Language:

.. code-block::

   ┌─ Select Language ───┐
   │                     │
   │ ○ English           │
   │ ● Italiano          │
   │                     │
   │ [OK] [Cancel]       │
   └─────────────────────┘

Changes apply immediately to:

- All menus
- Dialog titles
- Form labels
- Button text
- Messages

Keyboard Shortcuts
------------------

Global Shortcuts
~~~~~~~~~~~~~~~~

- ``Ctrl+N``: New (context-aware)
- ``Ctrl+O``: Open
- ``Ctrl+S``: Save
- ``Ctrl+Q``: Quit
- ``F1``: Help
- ``F5``: Refresh

Navigation
~~~~~~~~~~

- ``Ctrl+Tab``: Next tab
- ``Ctrl+Shift+Tab``: Previous tab
- ``Alt+<letter>``: Access menu
- ``Tab/Shift+Tab``: Navigate fields

Window Management
~~~~~~~~~~~~~~~~~

- ``Ctrl+W``: Close window
- ``Ctrl+M``: Minimize
- ``Alt+F4``: Exit application

Customization
-------------

Preferences Dialog
~~~~~~~~~~~~~~~~~~

Edit → Preferences:

**General Tab:**

- Theme (Light/Dark)
- Font size
- Date format
- Number format
- Startup behavior

**Display Tab:**

- Grid lines
- Alternating rows
- Tooltips
- Animations

**Advanced Tab:**

- Auto-save interval
- Backup frequency
- Cache size
- Debug mode

Theme Support
~~~~~~~~~~~~~

Built-in themes:

1. **Classic**: Windows 95 style
2. **Modern**: Flat design
3. **Dark**: Dark mode
4. **High Contrast**: Accessibility

Performance Tips
----------------

Optimization
~~~~~~~~~~~~

1. **Large Datasets**
   
   - Use pagination (100 records)
   - Enable lazy loading
   - Filter before loading

2. **Memory Usage**
   
   - Close unused windows
   - Clear image cache
   - Limit preview size

3. **Responsiveness**
   
   - Disable animations
   - Reduce autosave frequency
   - Use local database

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Window Not Responding:**

1. Check database connection
2. Wait for operation to complete
3. Force quit: Ctrl+Alt+Del (Windows)

**Display Issues:**

1. Update graphics drivers
2. Change theme
3. Reset window positions

**Database Locks:**

1. Close other connections
2. Restart application
3. Check file permissions

Error Dialogs
~~~~~~~~~~~~~

Standard error dialog:

.. code-block::

   ┌─ Error ─────────────────────┐
   │ ⚠                           │
   │ Database connection failed  │
   │                            │
   │ Details:                   │
   │ Connection refused on      │
   │ localhost:5432            │
   │                           │
   │ [Copy] [Report] [OK]      │
   └────────────────────────────┘

Integration
-----------

Command Line Arguments
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Open specific database
   pyarchinit-mini-gui --database /path/to/db.sqlite

   # Start maximized
   pyarchinit-mini-gui --maximized

   # Debug mode
   pyarchinit-mini-gui --debug

Python Integration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.desktop_gui import MainWindow
   from tkinter import Tk

   # Custom startup
   root = Tk()
   app = MainWindow(root, database_path="custom.db")
   
   # Add custom menu
   app.add_menu("Plugins", custom_commands)
   
   # Start
   app.mainloop()

Platform-Specific Features
--------------------------

Windows
~~~~~~~

- Native file dialogs
- System tray integration
- Windows installer available

macOS
~~~~~

- Native menu bar
- Dock integration  
- Retina display support

Linux
~~~~~

- GTK theme support
- System notifications
- AppImage available