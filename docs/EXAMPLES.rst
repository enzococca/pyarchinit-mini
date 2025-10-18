💡 Practical Examples
=====================

This guide demonstrates how to use and manage the PyArchInit-Mini desktop application and its command-line tools. Each section provides a real-world scenario, a complete working code snippet, input data, execution command, expected output, explanation, and variations for each major use case.

Example 1: Install Command-Line Tool
------------------------------------

**Scenario**:  
You want to install the PyArchInit-Mini command-line tool and ensure it is available in your environment, so you can perform batch operations or administrative tasks from the terminal.

**Complete Code**:

.. code-block:: python

    # File: install_pyarchinit_cli.py
    import subprocess
    import sys

    def install_pyarchinit_cli():
        try:
            # Try to install via pip
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyarchinit-mini'])
            print("PyArchInit-Mini CLI installed successfully!")
        except subprocess.CalledProcessError:
            print("Installation failed. Please check your network connection or pip configuration.")

    if __name__ == "__main__":
        install_pyarchinit_cli()

**Input Data**:

.. code-block:: python

    input_data = {
        "command": "pip install pyarchinit-mini"
    }

**Execution**:

.. code-block:: bash

    $ python install_pyarchinit_cli.py

**Expected Output**:

.. code-block:: text

    Collecting pyarchinit-mini
      Downloading pyarchinit-mini-*.tar.gz (X.X MB)
    ...
    Successfully installed pyarchinit-mini-*
    PyArchInit-Mini CLI installed successfully!

**Explanation**:
- Imports `subprocess` and `sys` to call pip from within Python.
- Calls pip to install `pyarchinit-mini`.
- If successful, prints a confirmation; otherwise, prints an error.

**Variants**:
- Use `pip install pyarchinit-mini` directly in your shell.
- Install in a virtual environment for project isolation:

  .. code-block:: bash

      $ python -m venv venv
      $ source venv/bin/activate
      $ pip install pyarchinit-mini

---

Example 2: Basic Command Usage
------------------------------

**Scenario**:  
You need to check the version of the installed PyArchInit-Mini CLI and view its help options for basic usage.

**Complete Code**:

.. code-block:: python

    # File: check_pyarchinit_cli.py
    import subprocess

    def run_cli_command(args):
        result = subprocess.run(['pyarchinit-mini'] + args, capture_output=True, text=True)
        print(result.stdout)

    if __name__ == "__main__":
        run_cli_command(['--version'])
        run_cli_command(['--help'])

**Input Data**:

.. code-block:: python

    input_data = {
        "commands": [
            ["--version"],
            ["--help"]
        ]
    }

**Execution**:

.. code-block:: bash

    $ python check_pyarchinit_cli.py

**Expected Output**:

.. code-block:: text

    pyarchinit-mini, version 1.2.3
    usage: pyarchinit-mini [OPTIONS] COMMAND [ARGS]...
      PyArchInit-Mini CLI - Manage PyArchInit databases and tools

    Options:
      --help     Show this message and exit.
      --version  Show the version and exit.
    ...

**Explanation**:
- Runs `pyarchinit-mini --version` and `pyarchinit-mini --help` using `subprocess`.
- Prints the output of each command.

**Variants**:
- Run commands directly:

  .. code-block:: bash

      $ pyarchinit-mini --version
      $ pyarchinit-mini --help

- Use `python -m pyarchinit_mini --help` if installed as a module.

---

Example 3: Common Command Combinations
--------------------------------------

**Scenario**:  
You want to create a new PyArchInit SQLite database, import some sample data, and export the database for backup.

**Complete Code**:

.. code-block:: python

    # File: pyarchinit_database_workflow.py
    import subprocess

    def run_cmd(args):
        result = subprocess.run(['pyarchinit-mini'] + args, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

    if __name__ == "__main__":
        # 1. Create new database
        run_cmd(['db', 'init', '--file', 'myarch.db'])
        # 2. Import sample data
        run_cmd(['db', 'import', '--file', 'myarch.db', '--sample'])
        # 3. Export for backup
        run_cmd(['db', 'export', '--file', 'myarch.db', '--output', 'myarch_backup.db'])

**Input Data**:

.. code-block:: python

    input_data = {
        "db_file": "myarch.db",
        "import_type": "sample",
        "backup_file": "myarch_backup.db"
    }

**Execution**:

.. code-block:: bash

    $ python pyarchinit_database_workflow.py

**Expected Output**:

.. code-block:: text

    Database created: myarch.db
    Imported sample data into myarch.db
    Database exported to myarch_backup.db

**Explanation**:
- Initializes a new SQLite database called `myarch.db`.
- Imports built-in sample data for easy testing.
- Exports the database to a backup file.

**Variants**:
- Import from your own data:

  .. code-block:: bash

      $ pyarchinit-mini db import --file myarch.db --input mydata.csv

- Use PostgreSQL instead of SQLite:

  .. code-block:: bash

      $ pyarchinit-mini db init --postgres --host localhost --user admin --password secret

---

Example 4: Configuration and Customization
------------------------------------------

**Scenario**:  
You want to configure PyArchInit-Mini to use a specific database file and customize the language setting.

**Complete Code**:

.. code-block:: python

    # File: configure_pyarchinit.py
    import configparser

    def set_config(db_file, language):
        config = configparser.ConfigParser()
        config['pyarchinit'] = {
            'database_file': db_file,
            'language': language
        }
        with open('pyarchinit.ini', 'w') as configfile:
            config.write(configfile)
        print(f"Configuration updated:\n  Database: {db_file}\n  Language: {language}")

    if __name__ == "__main__":
        set_config('myarch.db', 'en')

**Input Data**:

.. code-block:: python

    input_data = {
        "database_file": "myarch.db",
        "language": "en"
    }

**Execution**:

.. code-block:: bash

    $ python configure_pyarchinit.py

**Expected Output**:

.. code-block:: text

    Configuration updated:
      Database: myarch.db
      Language: en

**Explanation**:
- Uses `configparser` to write a settings file (pyarchinit.ini).
- Sets the database file and language code.
- This file can be loaded by PyArchInit-Mini at startup.

**Variants**:
- Set additional options, such as theme or log level.
- Use the PyArchInit-Mini GUI to set these options interactively via the menu.

---

Example 5: Troubleshooting Common Issues
----------------------------------------

**Scenario**:  
You encounter a database connection error when launching PyArchInit-Mini and need to diagnose and resolve the issue.

**Complete Code**:

.. code-block:: python

    # File: troubleshoot_db_connection.py
    import sqlite3

    def test_sqlite_connection(db_file):
        try:
            conn = sqlite3.connect(db_file)
            print(f"Connected successfully to {db_file}")
            conn.close()
        except sqlite3.Error as e:
            print(f"Database connection failed: {e}")

    if __name__ == "__main__":
        test_sqlite_connection('myarch.db')

**Input Data**:

.. code-block:: python

    input_data = {
        "database_file": "myarch.db"
    }

**Execution**:

.. code-block:: bash

    $ python troubleshoot_db_connection.py

**Expected Output** (if file exists):

.. code-block:: text

    Connected successfully to myarch.db

**Expected Output** (if file missing or corrupted):

.. code-block:: text

    Database connection failed: unable to open database file

**Explanation**:
- Attempts to connect to the SQLite database file.
- Prints a success or error message for rapid troubleshooting.

**Variants**:
- Add checks for required tables:

  .. code-block:: python

      conn.execute("SELECT * FROM inventario LIMIT 1")

- For PostgreSQL, use `psycopg2` to check connection.

---

🎯 Combined Use Cases
---------------------

You can combine these workflows to streamline your setup and maintenance with PyArchInit-Mini:

1. **Install the CLI** and dependencies (Example 1).
2. **Configure** your preferred database and language (Example 4).
3. **Initialize and populate** your database (Example 3).
4. **Check version and help** to learn new commands (Example 2).
5. **Troubleshoot** quickly if you hit database or configuration errors (Example 5).

For example, after setting your configuration, you might initialize a database, load data, and check your setup:

.. code-block:: bash