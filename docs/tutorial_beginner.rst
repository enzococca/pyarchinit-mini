Tutorial Beginner: Getting Started and Configuration
====================================================

🎯 Goals
--------

By the end of this tutorial, you will:

* Understand what PyArchInit-Mini is and what it can do
* Install PyArchInit-Mini on your computer
* Run your first command-line operation
* Learn how to configure the system to use your preferred database (SQLite or PostgreSQL)
* Avoid common setup mistakes

📋 Prerequisites
----------------

Before you begin, make sure you have:

* Basic knowledge of using the command line (terminal)
* Python 3.7 or newer installed (`python --version`)
* Pip (Python package installer) available (`pip --version`)

No archaeological background required!

📖 Key Concepts
---------------

Let's break down the essentials:

* **PyArchInit-Mini**: A lightweight command-line tool for managing archaeological data (sites, artifacts, and more) with or without a graphical interface.
* **CLI (Command Line Interface)**: You interact with PyArchInit-Mini by typing commands in your terminal.
* **Configuration**: Telling PyArchInit-Mini where and how to store your archaeological data (choose between SQLite or PostgreSQL databases).
* **Database**: The place where all your archaeological records live.

💻 Practical Example
--------------------

Let's get you up and running!

Step 1: Install PyArchInit-Mini
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open your terminal and type:

.. code-block:: bash

   pip install pyarchinit-mini

**Output**:

.. code-block:: text

   Collecting pyarchinit-mini
     Downloading pyarchinit_mini-x.x.x-py3-none-any.whl (XX kB)
   Installing collected packages: pyarchinit-mini
   Successfully installed pyarchinit-mini-x.x.x

**Explanation**:  
This uses pip to fetch and install PyArchInit-Mini along with all the code you need.

Step 2: Verify Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check that PyArchInit-Mini is installed and accessible:

.. code-block:: bash

   pyarchinit-mini --help

**Output**:

.. code-block:: text

   Usage: pyarchinit-mini [OPTIONS] COMMAND [ARGS]...

   Lightweight Archaeological Data Management System

   Options:
     --help  Show this message and exit.

   Commands:
     init      Initialize a new project
     config    Configure database settings
     site      Manage archaeological sites
     (other commands...)

**Explanation**:  
You should see a help message with available commands. If you get "command not found", see Common Errors below.

Step 3: Initialize a New Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a new directory for your project, then initialize:

.. code-block:: bash

   mkdir my_excavation
   cd my_excavation
   pyarchinit-mini init

**Output**:

.. code-block:: text

   Welcome to PyArchInit-Mini!
   Project initialized in /path/to/my_excavation
   Please run `pyarchinit-mini config` to set up your database.

**Explanation**:  
This sets up the folder for your archaeological data. Next, you'll connect a database.

Step 4: Configure Database (SQLite Example)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's start with SQLite (the easiest—no setup required):

.. code-block:: bash

   pyarchinit-mini config

You'll be prompted:

.. code-block:: text

   Which database backend would you like to use?
   [1] SQLite (default)
   [2] PostgreSQL
   Enter choice [1/2]:

Type ``1`` and press Enter.

Then:

.. code-block:: text

   Enter path for your SQLite database [pyarchinit.db]:

(Press Enter to accept the default, or type a custom filename.)

**Output**:

.. code-block:: text

   Database configuration saved.
   Ready to go!

**Explanation**:  
SQLite databases are just files—quick and easy for beginners!

Step 5: Add Your First Site
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's create your first archaeological site:

.. code-block:: bash

   pyarchinit-mini site add --name "Pompeii" --location "Italy"

**Output**:

.. code-block:: text

   Site 'Pompeii' added successfully!

**Explanation**:  
You just created your first archaeological record! You can now manage sites, stratigraphic units, and more.

🎓 Exercises
------------

1. **Exercise:**  
   Try configuring PyArchInit-Mini to use a PostgreSQL database instead of SQLite.

   **Solution:**

   .. code-block:: bash

      pyarchinit-mini config

   When prompted, choose ``2`` for PostgreSQL and enter your database details (host, port, user, password, database name).

2. **Exercise:**  
   List all registered sites.

   **Solution:**

   .. code-block:: bash

      pyarchinit-mini site list

   **Expected Output**:

   .. code-block:: text

      ID   Name      Location
      --   ----      --------
      1    Pompeii   Italy

💡 Tips
-------

* Use the ``--help`` flag on any command (e.g. ``pyarchinit-mini site --help``) to see usage and options.
* You can safely experiment with a test SQLite database before connecting to a real PostgreSQL server.
* Keep your database files in a safe, backed-up location for data security.

⚠️ Common Errors
----------------

* **Command not found:**  
  If ``pyarchinit-mini`` is not found, try restarting your terminal, or check that Python's `Scripts` directory is in your PATH.

* **Permission denied (database):**  
  Ensure you have write permissions to the folder where your database file lives.

* **PostgreSQL connection fails:**  
  Double-check your host, port, username, password, and that the PostgreSQL server is running.

* **Duplicate Site Name:**  
  Site names should be unique. Use descriptive names and locations.

🔗 Additional Resources
----------------------

* `Official PyArchInit-Mini Documentation <https://github.com/your-org/pyarchinit-mini>`_
* `Python Virtual Environments <https://docs.python.org/3/tutorial/venv.html>`_
* `PostgreSQL Quickstart <https://www.postgresql.org/docs/current/tutorial-install.html>`_
* `SQLite Documentation <https://sqlite.org/docs.html>`_

Ready to dig in? Try creating stratigraphic units and material inventories next!