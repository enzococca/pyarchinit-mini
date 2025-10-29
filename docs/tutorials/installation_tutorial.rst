Installation Tutorial
=====================

This tutorial provides step-by-step instructions for installing PyArchInit-Mini on your system.

System Requirements
-------------------

Before installing PyArchInit-Mini, ensure your system meets these requirements:

* **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+, Debian 10+, Fedora 32+)
* **Python**: Version 3.9, 3.10, 3.11, 3.12, or 3.13
* **RAM**: Minimum 4GB (8GB recommended)
* **Disk Space**: 500MB for installation plus space for your databases
* **Internet Connection**: Required for initial installation

Installation Methods
--------------------

PyArchInit-Mini can be installed in several ways depending on your needs.

Method 1: Install via pip (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the simplest and recommended method for most users.

**Step 1: Open Terminal/Command Prompt**

* **Windows**: Press ``Win + R``, type ``cmd``, and press Enter
* **macOS**: Press ``Cmd + Space``, type ``Terminal``, and press Enter
* **Linux**: Press ``Ctrl + Alt + T``

**Step 2: Verify Python Installation**

Check that Python is installed and the version is 3.9 or higher:

.. code-block:: bash

   python --version

Or on some systems:

.. code-block:: bash

   python3 --version

You should see output like:

.. code-block:: text

   Python 3.11.5

If Python is not installed, download it from https://www.python.org/downloads/

**Step 3: Install PyArchInit-Mini**

Install using pip:

.. code-block:: bash

   pip install pyarchinit-mini

Or:

.. code-block:: bash

   pip3 install pyarchinit-mini

The installation will download and install all required dependencies automatically. This may take a few minutes.

**Step 4: Verify Installation**

Check that PyArchInit-Mini was installed correctly:

.. code-block:: bash

   pyarchinit-mini --version

You should see the version number:

.. code-block:: text

   PyArchInit-Mini version 1.7.3

.. tip::
   If you get a "command not found" error, try closing and reopening your terminal, or use ``python -m pyarchinit_mini --version``

Method 2: Install in Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using a virtual environment is recommended for development or if you want to isolate the installation.

**Step 1: Create Virtual Environment**

.. code-block:: bash

   # Create a directory for your project
   mkdir pyarchinit-project
   cd pyarchinit-project

   # Create virtual environment
   python -m venv venv

**Step 2: Activate Virtual Environment**

On Windows:

.. code-block:: bash

   venv\\Scripts\\activate

On macOS/Linux:

.. code-block:: bash

   source venv/bin/activate

Your prompt should change to show ``(venv)`` at the beginning.

**Step 3: Install PyArchInit-Mini**

.. code-block:: bash

   pip install pyarchinit-mini

**Step 4: Deactivate (when finished)**

To deactivate the virtual environment:

.. code-block:: bash

   deactivate

Method 3: Install from Source (Developers)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For developers who want the latest features or wish to contribute:

**Step 1: Clone Repository**

.. code-block:: bash

   git clone https://github.com/pyarchinit/pyarchinit-mini.git
   cd pyarchinit-mini

**Step 2: Install in Editable Mode**

.. code-block:: bash

   pip install -e .

This installs the package in "editable" mode, meaning changes to the source code are immediately available.

**Step 3: Install Development Dependencies**

.. code-block:: bash

   pip install -e ".[dev]"

Database Setup
--------------

PyArchInit-Mini supports both SQLite and PostgreSQL databases.

SQLite Setup (Default)
~~~~~~~~~~~~~~~~~~~~~~

SQLite requires no additional setup. PyArchInit-Mini will create a database file automatically:

.. code-block:: bash

   # Create a new SQLite database
   pyarchinit-mini-cli create-db --db-type sqlite --db-path ./myproject.db

PostgreSQL Setup
~~~~~~~~~~~~~~~~

For PostgreSQL, you need a running PostgreSQL server.

**Step 1: Install PostgreSQL**

* **Windows**: Download installer from https://www.postgresql.org/download/windows/
* **macOS**: Use Homebrew: ``brew install postgresql``
* **Linux**: Use package manager: ``sudo apt install postgresql`` (Ubuntu/Debian)

**Step 2: Create Database**

.. code-block:: bash

   # Connect to PostgreSQL
   psql -U postgres

   # Create database
   CREATE DATABASE pyarchinit;
   \\q

**Step 3: Initialize PyArchInit-Mini Database**

.. code-block:: bash

   pyarchinit-mini-cli create-db \\
     --db-type postgresql \\
     --host localhost \\
     --port 5432 \\
     --database pyarchinit \\
     --username your_username \\
     --password your_password

Creating Your First Database
-----------------------------

Let's create a sample database to get started.

**Step 1: Create Database File**

.. code-block:: bash

   pyarchinit-mini-cli create-db \\
     --db-type sqlite \\
     --db-path ./tutorial.db

**Step 2: Set Database Path**

Set the environment variable to use this database:

On Windows:

.. code-block:: bash

   set DATABASE_URL=sqlite:///tutorial.db

On macOS/Linux:

.. code-block:: bash

   export DATABASE_URL=sqlite:///tutorial.db

**Step 3: Create Admin User**

.. code-block:: bash

   pyarchinit-mini-cli create-user \\
     --username admin \\
     --password your_secure_password \\
     --email admin@example.com \\
     --role admin

Starting the Application
-------------------------

Web Interface
~~~~~~~~~~~~~

Start the web interface:

.. code-block:: bash

   pyarchinit-mini-web

The server will start on http://localhost:5001

Open your browser and navigate to that address to access the interface.

Desktop GUI
~~~~~~~~~~~

Start the desktop application:

.. code-block:: bash

   pyarchinit-mini-gui

The graphical interface will open in a new window.

Common Installation Issues
---------------------------

Issue: "pip: command not found"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution**: Ensure Python is installed and added to your system PATH. Try:

* Windows: Reinstall Python and check "Add Python to PATH" during installation
* macOS: Use ``python3 -m pip`` instead of ``pip``
* Linux: Install pip separately: ``sudo apt install python3-pip``

Issue: Permission Denied Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution**:

On Windows (run as administrator):

.. code-block:: bash

   pip install --user pyarchinit-mini

On macOS/Linux:

.. code-block:: bash

   pip3 install --user pyarchinit-mini

Do NOT use ``sudo pip install`` as this can cause permission issues.

Issue: Module Not Found Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution**: Ensure you're using the same Python version that you used for installation:

.. code-block:: bash

   python3 -m pyarchinit_mini --version

Issue: Database Connection Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution**:

* Verify the DATABASE_URL environment variable is set correctly
* Check that the database file exists and is readable
* For PostgreSQL, ensure the server is running: ``pg_ctl status``

Updating PyArchInit-Mini
-------------------------

To update to the latest version:

.. code-block:: bash

   pip install --upgrade pyarchinit-mini

Check the changelog for breaking changes:

.. code-block:: bash

   pyarchinit-mini-cli changelog

Uninstalling
------------

To remove PyArchInit-Mini:

.. code-block:: bash

   pip uninstall pyarchinit-mini

Your databases and data files are NOT removed automatically. To remove them:

* Find your database files (usually in the current directory or ``~/.pyarchinit/``)
* Delete the database files manually
* On Linux/macOS: ``rm -rf ~/.pyarchinit/``
* On Windows: Delete the ``.pyarchinit`` folder in your user directory

Next Steps
----------

Now that PyArchInit-Mini is installed:

1. **Start the Web Interface** and explore the features
2. **Follow the Web Interface Tutorial** to learn the basics
3. **Create your first site** and add stratigraphic data
4. **Read the User Guide** for detailed documentation

.. seealso::

   * :doc:`web_interface_tutorial`
   * :doc:`desktop_gui_tutorial`
   * :doc:`../user/quickstart`
   * :doc:`../user/database_setup`

Getting Help
------------

If you encounter issues:

* **Documentation**: https://docs.pyarchinit.org
* **GitHub Issues**: https://github.com/pyarchinit/pyarchinit-mini/issues
* **Community Forum**: https://forum.pyarchinit.org
* **Email Support**: support@pyarchinit.org
