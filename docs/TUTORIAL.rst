==========================================
📚 Complete Manual - PyArchInit-Mini
==========================================

🚀 Welcome
----------

Hello and welcome to **PyArchInit-Mini**! 🏛️

**PyArchInit-Mini** is your all-in-one, lightweight solution for managing archaeological data without the heavy baggage of GIS dependencies. Whether you're an archaeologist, site manager, researcher, or student, this system empowers you to keep your sites, stratigraphic records, and artifact inventories organized and accessible—right from your command line, desktop, web browser, or through a powerful API.

Let’s dig in and see how **PyArchInit-Mini** can become the digital backbone of your archaeological projects! 🏺

📖 Project Overview
-------------------

**Project Name:** PyArchInit-Mini  
**Type:** Multi-interface (CLI, Desktop, Web, REST API)  
**Primary Audience:** Archaeologists, researchers, students, site managers, and digital heritage professionals who need a modern, efficient way to manage archaeological data.

**Purpose and Goals:**

PyArchInit-Mini is designed to simplify and streamline archaeological data management. It provides robust tools for:

* Managing archaeological sites and excavation contexts (stratigraphic units / US)
* Cataloging finds and materials
* Visualizing stratigraphic relationships (Harris Matrix)
* Exporting data and reports as PDFs
* Handling images and media files
* Searching, filtering, and analyzing data with advanced tools
* Using your data seamlessly across different platforms (web, desktop, CLI, and API)
* Supporting both SQLite and PostgreSQL databases

No GIS? No problem! PyArchInit-Mini is built for flexibility and speed, focusing on the core needs of archaeological documentation.

🎯 Main Interface
-----------------

PyArchInit-Mini offers **four main interfaces**. Each is tailored for different workflows, but they all share a unified approach to data and make archaeological data management a breeze.

You can use:

1. **Web Interface (Flask + Bootstrap)**
2. **Desktop GUI (Tkinter)**
3. **CLI Interface (Rich)**
4. **REST API (FastAPI)**

Let’s explore each interface and its main elements!

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Dialog/Window: Command-Line Interface (CLI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What is it?**

The CLI interface is your terminal-based command center, powered by the Rich library for colorful, interactive management of your archaeological data.

**Typical Use Cases:**

* Quick data entry and retrieval
* Batch operations
* Advanced search and filtering
* Scriptable workflows

**Main Elements:**

--------------------------------------------
Field: Command Prompt
--------------------------------------------

- **Description**:  
  The main input area where you type commands (e.g., to add a site, list finds, or search for stratigraphic units).

- **How to use it**:  
  Launch the CLI with:

  .. code-block:: bash

     cd pyarchinit-mini
     python cli_interface/cli_app.py

  Then enter commands such as:

  .. code-block:: bash

     add site
     list sites
     search us --site "Pompei"

- **Practical Example**:

  .. code-block:: bash

     > add site
     Sito: Pompei
     Nazione: Italia
     Regione: Campania
     Comune: Pompei
     Provincia: NA
     Descrizione: Ancient Roman city

     Output: Site "Pompei" added successfully!

--------------------------------------------
Button: "Help"
--------------------------------------------

- **Description**:  
  Typing `help` or `--help` shows a list of available commands and usage instructions.

- **How to use it**:  
  At any prompt, type:

  .. code-block:: bash

     help

- **Practical Example**:

  .. code-block:: bash

     > help
     Available commands:
      - add site
      - list sites
      - add us
      - list us
      - search us [options]
      - export pdf

     Output: Lists all commands and their descriptions.

- **Icon**:  
  Often displayed as `?` or `ℹ️` in Rich-powered UIs.

--------------------------------------------
Toolbar: Search & Filtering
--------------------------------------------

- **Description**:  
  Use optional flags in commands to filter and search data (e.g., by site name, date, or context).

- **How to use it**:  
  Append search criteria to your command:

  .. code-block:: bash

     search us --site "Pompei" --period "Roman"

- **Practical Example**:

  .. code-block:: bash

     > search us --site "Pompei" --period "Roman"
     Output:
     [1] US 101 | Site: Pompei | Period: Roman | Description: Floor deposit

     [2] US 203 | Site: Pompei | Period: Roman | Description: Wall collapse

- **Icon**:  
  Often paired with a magnifying glass (🔍) in documentation.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Dialog/Window: Web Interface (Flask)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What is it?**

A modern, Bootstrap-powered web application for intuitive, visual management of your archaeological database. Accessible via your browser.

**How to launch:**

.. code-block:: bash

   cd pyarchinit-mini
   python web_interface/app.py

Then visit `http://localhost:5000` in your browser.

**Main Elements:**

--------------------------------------------
Field: "Site List"
--------------------------------------------

- **Description**:  
  Displays all archaeological sites in your database in a tabular format.

- **How to use it**:  
  Click on a site to view, edit, or delete its details.

- **Practical Example**:

  1. You see a table listing "Pompei", "Ostia", etc.
  2. Click "Pompei" to view full site record.

  *Screenshot Description*:  
  A Bootstrap-styled table with rows for each site, action buttons on the right.

--------------------------------------------
Button: "Add Site"
--------------------------------------------

- **Description**:  
  Opens a form for entering a new site's details.

- **How to use it**:  
  Click the "+ Add Site" button at the top of the Site List.

- **Practical Example**:

  1. Click "+ Add Site"
  2. Fill in fields: Sito, Nazione, Regione, etc.
  3. Click "Save"
  4. The new site appears in the Site List.

- **Icon**:  
  Typically a plus sign (➕) or "Add" label.

--------------------------------------------
Button: "Edit" / "Delete"
--------------------------------------------

- **Description**:  
  Edit or remove existing site entries.

- **How to use it**:  
  Click "Edit" (✏️) to modify a site, or "Delete" (🗑️) to remove it.

- **Practical Example**:

  1. Find "Pompei" in the list.
  2. Click the "Edit" button, change the description, save.
  3. Or click "Delete" to remove the site (confirmation dialog appears).

- **Icon**:  
  "Edit" is usually a pencil (✏️), "Delete" is a trash can (🗑️).

--------------------------------------------
Toolbar: Navigation Bar
--------------------------------------------

- **Description**:  
  The top menu for switching between Sites, Stratigraphic Units, Materials, Reports, Media, etc.

- **How to use it**:  
  Click on a section (e.g., "US" for stratigraphic units) to switch views.

- **Practical Example**:

  1. Click "Materials" to view artifact inventory.
  2. Click "Reports" to generate PDF reports.

- **Icon**:  
  Section icons may include a box (📦), stack (🗄️), or chart (📊).

--------------------------------------------
Button: "Export PDF"
--------------------------------------------

- **Description**:  
  Generate a PDF report of current data (e.g., all sites or stratigraphic units).

- **How to use it**:  
  Click "Export PDF" in the Reports section.

- **Practical Example**:

  1. In the "Reports" view, click "Export PDF"
  2. Download the generated archaeological report for sharing or archiving.

- **Icon**:  
  A document or PDF icon (📄).

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Dialog/Window: Desktop GUI (Tkinter)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What is it?**

A full-featured desktop application for local, offline management of your data.

**How to launch:**

.. code-block:: bash

   cd pyarchinit-mini
   python desktop_gui/gui_app.py
   # OR
   python run_gui.py

**Main Elements:**

--------------------------------------------
Field: "Database Connection"
--------------------------------------------

- **Description**:  
  Selects and displays the current database connection (SQLite/PostgreSQL).

- **How to use it**:  
  Use the dropdown to switch databases or configure connection details.

- **Practical Example**:

  1. Choose "SQLite: archaeological_data.db"
  2. Or enter PostgreSQL credentials and connect.

--------------------------------------------
Tab: "Sites", "US", "Materials", "Reports"
--------------------------------------------

- **Description**:  
  Main tabs for each primary data area (Sites, Stratigraphic Units, Material Inventory, Reports).

- **How to use it**:  
  Click tabs to navigate between data types.

- **Practical Example**:

  1. Click "US" to enter new stratigraphic units.
  2. Click "Materials" to document finds.

- **Icon**:  
  Tabs may use icons like 🏛️ for Sites, 📋 for US, 📦 for Materials.

--------------------------------------------
Button: "Save", "Delete", "New"
--------------------------------------------

- **Description**:  
  Standard action buttons for creating, saving, and deleting records.

- **How to use it**:  
  After filling in a form, click "Save" (💾) to commit, "Delete" (🗑️) to remove, "New" (➕) to add a fresh record.

- **Practical Example**:

  1. Enter a new stratigraphic unit, click "Save"
  2. Select a record, click "Delete" for removal

--------------------------------------------
Toolbar: Harris Matrix Visualization
--------------------------------------------

- **Description**:  
  View and interact with Harris Matrix diagrams representing stratigraphic relationships.

- **How to use it**:  
  Click "Harris Matrix" in the toolbar; use zoom, pan, or export tools.

- **Practical Example**:

  1. Open "Harris Matrix" tab
  2. Visualize the sequence of archaeological layers for a site

- **Icon**:  
  Typically a connected nodes icon (🔗) or diagram.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Dialog/Window: REST API Documentation (FastAPI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What is it?**

An interactive, auto-generated web documentation for your API, powered by Swagger/OpenAPI. Ideal for developers and integrators.

**How to launch:**

.. code-block:: bash

   cd pyarchinit-mini
   python main.py

Visit `http://localhost:8000/docs`

**Main Elements:**

--------------------------------------------
Field: API Endpoints List
--------------------------------------------

- **Description**:  
  Lists all available API endpoints with documentation.

- **How to use it**:  
  Expand each endpoint to see parameters, try requests, and view results.

- **Practical Example**:

  1. Go to `/api/v1/sites/` > "GET" to list all sites
  2. Fill parameters, click "Execute", see JSON output

- **Icon**:  
  Endpoint methods (GET, POST, etc.) color-coded (🟢 for GET, 🟠 for POST, etc.)

--------------------------------------------
Button: "Try it out"
--------------------------------------------

- **Description**:  
  Enables live testing of each API endpoint directly from the docs.

- **How to use it**:  
  Click "Try it out", enter request parameters, click "Execute".

- **Practical Example**:

  1. Click "Try it out" on `POST /api/v1/sites/`
  2. Enter site data in the form, click "Execute"
  3. See immediate response with created site details

- **Icon**:  
  Labeled as "Try it out" (no emoji by default).

🔧 Toolbars and Buttons
-----------------------

Across all interfaces, PyArchInit-Mini maintains a consistent set of toolbars and action buttons to make your workflow smooth and efficient:

* **Search (🔍)**: Instantly filter sites, US, or materials.
* **Add / New (➕)**: Start a new entry (site, US, etc.).
* **Edit (✏️)**: Modify existing records.
* **Delete (🗑️)**: Remove records (with confirmation).
* **Save (💾)**: Commit changes to the database.
* **Export PDF (📄)**: Generate printable reports.
* **Navigation Bar**: Jump between major data sections.
* **Database Connection**: Switch or configure your database.
* **Harris Matrix (🔗)**: Visualize stratigraphic relationships.

💡 Complete Practical Examples
------------------------------

Scenario 1: Creating and Managing an Archaeological Site (Web Interface)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Goal:** Add a new site for "Pompei", edit its description, and export a report.

**Steps:**

1. **Launch Web Interface**
   - Start with:

     .. code-block:: bash

        cd pyarchinit-mini
        python web_interface/app.py

   - Open `http://localhost:5000` in your web browser.

2. **Add a New Site**
   - Click the **"+ Add Site" (➕)** button.
   - Fill in:
      - Sito: Pompei
      - Nazione: Italia
      - Regione: Campania
      - Comune: Pompei
      - Provincia: NA
      - Descrizione: Ancient Roman city
   - Click **"Save" (💾)**
   - *Result*: "Pompei" appears in your site list.

   *Screenshot Description*: Site form with labeled fields, "Save" button at the bottom.

3. **Edit Site Description**
   - In the Site List, find "Pompei", click **"Edit" (✏️)**
   - Update description to: "Ancient Roman city destroyed in 79 AD"
   - Click **"Save" (💾)**
   - *Result*: Site description updated.

4. **Export Site Report as PDF**
   - Go to the **Reports** section via the navigation bar.
   - Click **"Export PDF" (📄)**
   - Download the generated site report for your records.

Scenario 2: Adding Stratigraphic Units via CLI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Goal:** Enter two stratigraphic units for the "Pompei" site using the command-line interface.

**Steps:**

1. **Launch CLI**
   - Start with:

     .. code-block:: bash

        cd pyarchinit-mini
        python cli_interface/cli_app.py

2. **Add First US**
   - At the prompt, type:

     .. code-block:: bash

        add us
        Site: Pompei
        US Number: 101
        Description: Floor deposit

   - *Output*: "US 101 added to Pompei"

3. **Add Second US**
   - At the prompt, type:

     .. code-block:: bash

        add us
        Site: Pompei
        US Number: 203
        Description: Wall collapse

   - *Output*: "US 203 added to Pompei"

4. **List Stratigraphic Units**
   - At the prompt, type:

     .. code-block:: bash

        list us --site "Pompei"

   - *Output*:

     .. code-block::

        [1] US 101 | Description: Floor deposit
        [2] US 203 | Description: Wall collapse

❓ Frequently Asked Questions
----------------------------

* **Can I use PyArchInit-Mini with both SQLite and PostgreSQL?**
  - Yes! Set the `DATABASE_URL` environment variable to choose your backend.

* **Is my data validated?**
  - Absolutely. All input is validated with robust Pydantic schemas.

* **How do I access the REST API docs?**
  - Launch with `python main.py` and visit `http://localhost:8000/docs`.

* **Can I use PyArchInit-Mini as a Python library?**
  - Yes, import and use its services directly in your scripts.

* **Are GIS or mapping tools included?**
  - No, PyArchInit-Mini is focused on core data management without GIS.

🔧 Troubleshooting
------------------

* **I can’t connect to my PostgreSQL database!**
  - Double-check your `DATABASE_URL` format:

    .. code-block:: bash

       export DATABASE_URL="postgresql://user:password@localhost:5432/pyarchinit"

* **Web/desktop interface won’t start.**
  - Ensure you’re running the correct command in the `pyarchinit-mini` directory.

* **Commands not recognized in CLI.**
  - Use `help` to see available commands and ensure you’re in the right directory.

* **PDF export fails.**
  - Check for missing dependencies or file permissions in your output directory.

* **API returns error 422 (validation error).**
  - Ensure your data input matches the expected schema—see API docs for examples.

-------------------------------

Now you’re ready to manage your archaeological data efficiently with **PyArchInit-Mini**!  
Happy excavating—digitally! 🏺📊