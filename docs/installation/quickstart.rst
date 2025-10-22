Quick Start Guide
=================

This guide will help you get PyArchInit-Mini up and running in minutes.

Installation
------------

Basic Installation (API Only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install pyarchinit-mini

Complete Installation (All Features)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install 'pyarchinit-mini[all]'

Initial Setup
-------------

1. Initialize the System
~~~~~~~~~~~~~~~~~~~~~~~~

After installation, run the initialization command:

.. code-block:: bash

   pyarchinit-mini-init

This command will:

- Create the configuration directory at ``~/.pyarchinit_mini/``
- Set up the SQLite database
- Prompt you to create an admin user
- Create necessary directories for media, exports, and backups

Example:

.. code-block:: console

   $ pyarchinit-mini-init
   
   Welcome to PyArchInit-Mini Setup!
   
   Creating directories...
   ✓ Created ~/.pyarchinit_mini/data/
   ✓ Created ~/.pyarchinit_mini/media/
   ✓ Created ~/.pyarchinit_mini/export/
   ✓ Created ~/.pyarchinit_mini/backup/
   ✓ Created ~/.pyarchinit_mini/config/
   
   Setting up database...
   ✓ Database created at ~/.pyarchinit_mini/data/pyarchinit_mini.db
   
   Create admin user:
   Username: admin
   Email: admin@example.com
   Password: ********
   Confirm password: ********
   
   ✓ Admin user created successfully!
   ✓ Setup complete!
   
   You can now start using PyArchInit-Mini:
   - Web interface: pyarchinit-mini-web
   - Desktop GUI: pyarchinit-mini-gui
   - CLI: pyarchinit-mini
   - API: pyarchinit-mini-api

Non-Interactive Setup
~~~~~~~~~~~~~~~~~~~~~

For automated deployments:

.. code-block:: bash

   pyarchinit-mini-init --non-interactive

This creates a default admin user with:
- Username: ``admin``
- Password: ``admin``

.. warning::
   Change the default password immediately after first login!

2. Choose Your Interface
~~~~~~~~~~~~~~~~~~~~~~~~

Web Interface
^^^^^^^^^^^^^

Start the web server:

.. code-block:: bash

   pyarchinit-mini-web
   
   * Running on http://localhost:5001

Open your browser to http://localhost:5001

Desktop GUI
^^^^^^^^^^^

Launch the desktop application:

.. code-block:: bash

   pyarchinit-mini-gui

Command Line Interface
^^^^^^^^^^^^^^^^^^^^^^

Start the interactive CLI:

.. code-block:: bash

   pyarchinit-mini

REST API
^^^^^^^^

Start the API server:

.. code-block:: bash

   pyarchinit-mini-api
   
   * Running on http://localhost:8000
   * API docs at http://localhost:8000/docs

3. First Steps
~~~~~~~~~~~~~~

Create Your First Site
^^^^^^^^^^^^^^^^^^^^^^

**Web Interface:**

1. Login with your admin credentials
2. Click "Sites" in the navigation
3. Click "New Site"
4. Fill in the required fields
5. Click "Save"

**CLI:**

.. code-block:: console

   pyarchinit> create-site
   
   Site name: Pompei
   Location (Nation) [Italia]: 
   Region: Campania
   Comune: Pompei
   Province: Napoli
   Site definition (IT): Antica città romana
   Site definition (EN): Ancient Roman city
   
   ✓ Site 'Pompei' created successfully!

**API:**

.. code-block:: bash

   curl -X POST http://localhost:8000/api/sites \
     -H "Authorization: Bearer <your-token>" \
     -H "Content-Type: application/json" \
     -d '{
       "site_name": "Pompei",
       "nation": "Italia",
       "region": "Campania",
       "comune": "Pompei",
       "province": "Napoli",
       "definizione_sito": "Antica città romana"
     }'

Quick Tour
----------

Essential Features
~~~~~~~~~~~~~~~~~~

1. **Sites Management**
   - Create archaeological sites
   - Edit site information
   - View site details

2. **Stratigraphic Units (US)**
   - Record stratigraphic units
   - Define relationships
   - 49 fields of data

3. **Inventory**
   - Catalog finds
   - Track conservation state
   - 37 fields with ICCD thesaurus

4. **Harris Matrix**
   - Generate stratigraphic diagrams
   - Export to PDF/GraphML
   - Interactive visualization

5. **Analytics Dashboard**
   - View statistics
   - Interactive charts
   - Export reports

Common Workflows
~~~~~~~~~~~~~~~~

Recording an Excavation
^^^^^^^^^^^^^^^^^^^^^^^

1. Create a site
2. Add stratigraphic units as you excavate
3. Define relationships between units
4. Catalog finds with inventory numbers
5. Generate Harris Matrix for publication

Data Export
^^^^^^^^^^^

1. Go to Export/Import
2. Select data type (Sites/US/Inventory)
3. Choose format (Excel/CSV)
4. Apply filters if needed
5. Download file

Collaboration
^^^^^^^^^^^^^

1. Create user accounts for team members
2. Assign appropriate roles
3. Share database connection
4. Work simultaneously with real-time updates

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Command not found after installation:**

Add Python scripts directory to PATH:

.. code-block:: bash

   # Linux/Mac
   export PATH="$HOME/.local/bin:$PATH"
   
   # Windows
   # Add to System Environment Variables

**Database connection failed:**

1. Check if database exists:

   .. code-block:: bash

      ls ~/.pyarchinit_mini/data/

2. Re-run initialization:

   .. code-block:: bash

      pyarchinit-mini-init

**Port already in use:**

Change the port:

.. code-block:: bash

   # Web interface on different port
   export PYARCHINIT_WEB_PORT=5002
   pyarchinit-mini-web
   
   # API on different port
   export PYARCHINIT_API_PORT=8001
   pyarchinit-mini-api

Next Steps
----------

- Read the full documentation for your chosen interface
- Explore the example data
- Set up your team's workflow
- Configure backups
- Integrate with your existing tools

Getting Help
------------

- **Documentation**: https://pyarchinit-mini.readthedocs.io
- **GitHub Issues**: https://github.com/enzococca/pyarchinit-mini/issues
- **Email**: enzo.ccc@gmail.com