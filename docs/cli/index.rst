CLI (Command Line Interface) Documentation
===========================================

PyArchInit-Mini provides a rich command-line interface built with Click and Rich libraries, offering an interactive terminal experience for managing archaeological data.

.. toctree::
   :maxdepth: 2
   :caption: CLI Contents:

   quickstart
   commands
   export_import
   graphml
   examples

Quick Start
-----------

Starting the CLI
~~~~~~~~~~~~~~~~

To start the interactive CLI:

.. code-block:: bash

   pyarchinit-mini
   
   # Welcome to PyArchInit-Mini CLI!
   # Type 'help' to see available commands or 'exit' to quit.
   # pyarchinit>

Available Commands
~~~~~~~~~~~~~~~~~~

Type ``help`` in the CLI to see all available commands:

.. code-block::

   pyarchinit> help

   Available commands:
   - list-sites      : List all archaeological sites
   - create-site     : Create a new site
   - list-us         : List stratigraphic units
   - create-us       : Create a new US
   - list-inventory  : List inventory items
   - create-inventory: Create a new inventory item
   - search          : Search across all data
   - export          : Export data to various formats
   - import          : Import data from CSV/Excel
   - harris-matrix   : Generate Harris Matrix
   - stats           : Show database statistics
   - help            : Show this help message
   - exit            : Exit the CLI

Command Structure
-----------------

Basic Command Syntax
~~~~~~~~~~~~~~~~~~~~

Commands follow a consistent pattern:

.. code-block::

   pyarchinit> command-name [options] [arguments]

Examples:

.. code-block::

   pyarchinit> list-sites
   pyarchinit> list-sites --limit 10
   pyarchinit> search --type site --query "Pompei"
   pyarchinit> export --format excel --output sites.xlsx

Interactive Mode Features
~~~~~~~~~~~~~~~~~~~~~~~~~

The CLI provides several interactive features:

1. **Auto-completion**: Press TAB to auto-complete commands
2. **Command history**: Use UP/DOWN arrows to navigate history
3. **Color output**: Important information highlighted in colors
4. **Progress bars**: Visual feedback for long operations
5. **Tables**: Data displayed in formatted tables
6. **Prompts**: Interactive prompts for required information

Site Management Commands
------------------------

list-sites
~~~~~~~~~~

List all archaeological sites with optional filtering:

.. code-block::

   pyarchinit> list-sites [OPTIONS]

   Options:
     --limit INTEGER     Maximum number of sites to display [default: 20]
     --offset INTEGER    Number of sites to skip [default: 0]
     --sort-by TEXT      Field to sort by [default: site_name]
     --search TEXT       Search sites by name or location

Example output:

.. code-block::

   ┏━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
   ┃ ID ┃ Site Name     ┃ Location   ┃ Comune    ┃ Definition         ┃
   ┡━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
   │ 1  │ Pompei        │ Campania   │ Pompei    │ Ancient Roman city │
   │ 2  │ Herculaneum   │ Campania   │ Ercolano  │ Roman settlement   │
   └────┴───────────────┴────────────┴───────────┴────────────────────┘

create-site
~~~~~~~~~~~

Create a new archaeological site interactively:

.. code-block::

   pyarchinit> create-site

The command will prompt for:

- Site name (required)
- Location/Nation
- Region
- Comune (municipality)
- Province
- Site definition (Italian)
- Site definition (English)

Example:

.. code-block::

   pyarchinit> create-site
   
   Creating new archaeological site...
   
   Site name: Villa Adriana
   Location (Nation) [Italia]: 
   Region: Lazio
   Comune: Tivoli
   Province: Roma
   Site definition (IT): Villa imperiale romana
   Site definition (EN): Roman imperial villa
   
   ✓ Site 'Villa Adriana' created successfully!

update-site
~~~~~~~~~~~

Update an existing site:

.. code-block::

   pyarchinit> update-site SITE_NAME

   Options:
     --name TEXT         New site name
     --location TEXT     New location
     --region TEXT       New region
     --comune TEXT       New comune
     --definition TEXT   New definition

delete-site
~~~~~~~~~~~

Delete a site (with confirmation):

.. code-block::

   pyarchinit> delete-site SITE_NAME

   ⚠️  Are you sure you want to delete site 'SITE_NAME'? [y/N]:

Stratigraphic Units (US) Commands
---------------------------------

list-us
~~~~~~~

List stratigraphic units with filters:

.. code-block::

   pyarchinit> list-us [OPTIONS]

   Options:
     --site TEXT         Filter by site name
     --area TEXT         Filter by area
     --limit INTEGER     Maximum number of US to display
     --sort-by TEXT      Sort by field (us, area, d_stratigrafica)

create-us
~~~~~~~~~

Create a new stratigraphic unit:

.. code-block::

   pyarchinit> create-us

Interactive prompts will guide through all 49 US fields organized in tabs:

1. Basic Information (site, area, US number)
2. Stratigraphic Data
3. Characteristics
4. Dating Information
5. Documentation
6. Relationships

search-us
~~~~~~~~~

Search US by various criteria:

.. code-block::

   pyarchinit> search-us [OPTIONS]

   Options:
     --site TEXT         Site name
     --area TEXT         Area
     --us INTEGER        US number
     --type TEXT         Unit type (US, USM, USD, USV)
     --period TEXT       Chronological period
     --definition TEXT   Search in definitions

Inventory Commands
------------------

list-inventory
~~~~~~~~~~~~~~

List inventory items:

.. code-block::

   pyarchinit> list-inventory [OPTIONS]

   Options:
     --site TEXT         Filter by site
     --type TEXT         Filter by artifact type
     --limit INTEGER     Maximum items to display
     --material TEXT     Filter by material

create-inventory
~~~~~~~~~~~~~~~~

Create new inventory item (37 fields):

.. code-block::

   pyarchinit> create-inventory

Prompts for all inventory fields including:
- Basic data (number, type, material)
- Measurements
- Conservation state
- Dating
- Bibliography
- ICCD thesaurus terms

Export/Import Commands
----------------------

The CLI includes dedicated export/import functionality:

Export Commands
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Export sites to Excel
   pyarchinit-export-import export-sites -f excel -o sites.xlsx

   # Export US to CSV for specific site
   pyarchinit-export-import export-us -f csv -s "Pompei" -o pompei_us.csv

   # Export inventory to Excel
   pyarchinit-export-import export-inventario -f excel -o inventory.xlsx

Import Commands
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Import sites from CSV
   pyarchinit-export-import import-sites sites.csv

   # Import US with duplicate handling
   pyarchinit-export-import import-us --skip-duplicates us_data.csv

   # Import inventory without skipping duplicates
   pyarchinit-export-import import-inventario --no-skip-duplicates inventory.csv

Harris Matrix Commands
----------------------

generate-matrix
~~~~~~~~~~~~~~~

Generate Harris Matrix for a site:

.. code-block::

   pyarchinit> harris-matrix SITE_NAME [OPTIONS]

   Options:
     --format TEXT       Output format (png, pdf, svg) [default: png]
     --output TEXT       Output filename
     --dpi INTEGER       DPI for raster formats [default: 300]
     --grouping TEXT     Grouping mode (period_area, period, area, none)

Example:

.. code-block::

   pyarchinit> harris-matrix "Pompei" --format pdf --output pompei_matrix.pdf

   Generating Harris Matrix for site 'Pompei'...
   ✓ Found 127 stratigraphic units
   ✓ Processing 245 relationships
   ✓ Matrix generated successfully: pompei_matrix.pdf

validate-stratigraphy
~~~~~~~~~~~~~~~~~~~~~

Check for stratigraphic inconsistencies:

.. code-block::

   pyarchinit> validate-stratigraphy SITE_NAME

   Validating stratigraphy for site 'Pompei'...
   
   ⚠️  Found 3 issues:
   
   1. Missing reciprocal relationship:
      US 1001 covers US 1002, but US 1002 doesn't list "covered by 1001"
   
   2. Stratigraphic paradox detected:
      US 2001 → US 2002 → US 2003 → US 2001 (circular reference)
   
   3. Temporal inconsistency:
      US 3001 (Medieval) covers US 3002 (Modern)

GraphML Export Commands
-----------------------

The CLI includes a dedicated GraphML converter:

.. code-block:: bash

   # Convert DOT file to GraphML
   pyarchinit-graphml convert input.dot output.graphml -t "Site Title"

   # Convert with custom template
   pyarchinit-graphml convert input.dot output.graphml \
     -t "Pompei Excavation" \
     --template my_template.graphml

   # Batch conversion
   pyarchinit-graphml batch input_dir/ output_dir/ -t "Project Name"

   # Get default template
   pyarchinit-graphml template -o EM_palette.graphml

Search Functionality
--------------------

Global Search
~~~~~~~~~~~~~

Search across all data types:

.. code-block::

   pyarchinit> search QUERY [OPTIONS]

   Options:
     --type TEXT         Limit to type (site, us, inventory)
     --limit INTEGER     Maximum results per type
     --exact             Exact match only

Example:

.. code-block::

   pyarchinit> search "romano" --limit 5

   Search results for "romano":
   
   📍 Sites (2 results):
   - Pompei: Ancient Roman city
   - Ostia Antica: Roman port city
   
   📋 Stratigraphic Units (5 results):
   - US 1001: Strato romano imperiale
   - US 1045: Pavimento romano
   - US 2003: Muro romano
   - US 3021: Deposito romano
   - US 4001: Crollo strutture romane
   
   📦 Inventory (3 results):
   - INV001: Ceramica romana
   - INV045: Moneta romana
   - INV123: Tegola romana

Advanced Search
~~~~~~~~~~~~~~~

Use filters for precise searching:

.. code-block::

   pyarchinit> advanced-search

   Select search type:
   1. Sites
   2. Stratigraphic Units
   3. Inventory
   
   Choice: 2
   
   US Search Criteria:
   - Site name (optional): Pompei
   - Area (optional): A
   - US type (optional): US
   - Period (optional): Romano
   - Date range (optional): 
   - Text search in definitions: villa

Statistics Command
------------------

View database statistics:

.. code-block::

   pyarchinit> stats

   📊 PyArchInit-Mini Database Statistics
   
   Overview:
   ├── Total Sites: 12
   ├── Total US: 1,247
   ├── Total Inventory Items: 3,456
   └── Total Relationships: 2,891
   
   By Site:
   ├── Pompei: 523 US, 1,234 items
   ├── Herculaneum: 312 US, 876 items
   └── Ostia: 412 US, 1,346 items
   
   By Period:
   ├── Romano: 45%
   ├── Medievale: 23%
   ├── Moderno: 18%
   └── Contemporaneo: 14%

Database Commands
-----------------

db-info
~~~~~~~

Show database connection information:

.. code-block::

   pyarchinit> db-info

   Database Information:
   ├── Type: PostgreSQL
   ├── Host: localhost:5432
   ├── Database: pyarchinit
   ├── User: pyarchinit_user
   └── Tables: 15

db-backup
~~~~~~~~~

Create database backup:

.. code-block::

   pyarchinit> db-backup [OPTIONS]

   Options:
     --output TEXT       Backup filename
     --compress          Compress backup

Configuration
-------------

The CLI uses the same configuration as other interfaces:

.. code-block::

   ~/.pyarchinit_mini/config/config.yaml

CLI-specific settings:

.. code-block:: yaml

   cli:
     colors: true          # Enable colored output
     page_size: 20         # Default pagination size
     date_format: "%Y-%m-%d"
     export_format: excel  # Default export format
     confirm_delete: true  # Require confirmation for deletions

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Disable colors
   export PYARCHINIT_CLI_NO_COLOR=1

   # Set default export directory
   export PYARCHINIT_EXPORT_DIR=/path/to/exports

   # Skip confirmation prompts
   export PYARCHINIT_CLI_YES=1

Keyboard Shortcuts
------------------

While in the CLI:

- ``Ctrl+C``: Cancel current operation
- ``Ctrl+D``: Exit CLI (same as 'exit')
- ``TAB``: Auto-complete commands
- ``↑/↓``: Navigate command history
- ``Ctrl+R``: Search command history
- ``Ctrl+L``: Clear screen

Tips and Tricks
---------------

1. **Command Aliases**

   Create shorter aliases for common commands:

   .. code-block::

      pyarchinit> alias ls list-sites
      pyarchinit> alias lus list-us

2. **Output Redirection**

   Save command output to file:

   .. code-block::

      pyarchinit> list-sites > sites.txt
      pyarchinit> list-us --site "Pompei" > pompei_us.txt

3. **Batch Operations**

   Use the CLI in scripts:

   .. code-block:: bash

      echo "list-sites
      stats
      exit" | pyarchinit-mini > report.txt

4. **JSON Output**

   Get machine-readable output:

   .. code-block::

      pyarchinit> list-sites --format json

5. **Quiet Mode**

   Suppress interactive prompts:

   .. code-block::

      pyarchinit> create-site --quiet \
        --name "Test Site" \
        --region "Lazio" \
        --comune "Roma"

Error Handling
--------------

The CLI provides clear error messages:

.. code-block::

   pyarchinit> create-site
   
   Site name: Pompei
   
   ❌ Error: Site 'Pompei' already exists!
   
   Try:
   - Use a different site name
   - Run 'update-site Pompei' to modify existing site
   - Run 'list-sites' to see all sites

Integration Examples
--------------------

Shell Script Integration
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # backup_archaeological_data.sh

   DATE=$(date +%Y%m%d)
   EXPORT_DIR="./backups/$DATE"

   mkdir -p $EXPORT_DIR

   # Export all data
   pyarchinit-export-import export-sites -f excel -o "$EXPORT_DIR/sites.xlsx"
   pyarchinit-export-import export-us -f excel -o "$EXPORT_DIR/us.xlsx"
   pyarchinit-export-import export-inventario -f excel -o "$EXPORT_DIR/inventory.xlsx"

   # Generate Harris matrices for all sites
   echo "list-sites --format json" | pyarchinit-mini | \
   jq -r '.[] | .site_name' | \
   while read site; do
     echo "Generating matrix for $site..."
     pyarchinit-mini harris-matrix "$site" \
       --format pdf \
       --output "$EXPORT_DIR/${site// /_}_matrix.pdf"
   done

Python Integration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import subprocess
   import json

   def get_sites():
       """Get all sites from CLI"""
       result = subprocess.run(
           ['pyarchinit-mini', 'list-sites', '--format', 'json'],
           capture_output=True,
           text=True
       )
       return json.loads(result.stdout)

   def create_site_batch(sites_data):
       """Create multiple sites"""
       for site in sites_data:
           cmd = [
               'pyarchinit-mini', 'create-site', '--quiet',
               '--name', site['name'],
               '--region', site['region'],
               '--comune', site['comune']
           ]
           subprocess.run(cmd)

   # Example usage
   sites = get_sites()
   print(f"Found {len(sites)} sites")