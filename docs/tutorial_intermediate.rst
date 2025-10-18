Tutorial Intermediate: Advanced Features
========================================

🎯 Goals
--------

By the end of this tutorial, you'll be able to:

* Use advanced data management features of PyArchInit-Mini from the command line.
* Work with stratigraphic relationships using the Harris Matrix.
* Export archaeological data into PDF reports.
* Automate common archaeological data workflows.
* Avoid common mistakes and improve your productivity.

📋 Prerequisites
----------------

Before starting, make sure you:

* Know basic Python (functions, classes, modules).
* Have used the command line before.
* Are familiar with basic archaeological terminology (site, stratigraphic unit, inventory).
* Have PyArchInit-Mini installed:

  .. code-block:: bash

     pip install pyarchinit-mini

* Have initialized a sample project (see PyArchInit-Mini docs for details).

📖 Key Concepts
---------------

Let's quickly break down the advanced features we'll explore:

* **Harris Matrix**: A diagram that shows the sequence and relationship of stratigraphic units (contexts) in archaeology.
* **PDF Export**: Automated creation of structured archaeological reports.
* **Media Management**: Linking photos and documents to your data records.
* **CLI Automation**: Using PyArchInit-Mini's command-line tools for repetitive or complex tasks.

💻 Practical Example
--------------------

Let's dive into hands-on usage! We'll walk through creating sites, adding stratigraphic units, generating a Harris Matrix, and exporting a PDF report—all from the CLI.

### Step 1: Create a New Archaeological Site

.. code-block:: bash

   pyarchinit-mini site add --name "Civita Campana" --location "Italy" --period "Roman"

**Output:**

.. code-block:: text

   Site added: Civita Campana (ID: 1)

**Explanation:**  
You've just created a new site record. The `site add` command takes in specific arguments to define the site.

### Step 2: Add Stratigraphic Units (US)

.. code-block:: bash

   pyarchinit-mini us add --site 1 --number 1001 --description "Clay floor layer" --type "floor"
   pyarchinit-mini us add --site 1 --number 1002 --description "Fill layer above floor" --type "fill"
   pyarchinit-mini us add --site 1 --number 1003 --description "Wall foundation" --type "structure"

**Output:**

.. code-block:: text

   US added: 1001 (floor)
   US added: 1002 (fill)
   US added: 1003 (structure)

**Explanation:**  
You just associated new stratigraphic units (contexts) with your site. Each US gets a unique number and type.

### Step 3: Define Stratigraphic Relationships

.. code-block:: bash

   pyarchinit-mini relationship add --site 1 --us1 1002 --us2 1001 --relationship "overlies"
   pyarchinit-mini relationship add --site 1 --us1 1001 --us2 1003 --relationship "overlies"

**Output:**

.. code-block:: text

   Relationship added: US 1002 overlies US 1001
   Relationship added: US 1001 overlies US 1003

**Explanation:**  
You've described the stratigraphic sequence: fill (1002) is above the floor (1001), which is above the wall foundation (1003).

### Step 4: Generate the Harris Matrix

.. code-block:: bash

   pyarchinit-mini harris-matrix generate --site 1 --output matrix.png

**Output:**

.. code-block:: text

   Harris Matrix generated: matrix.png

**Explanation:**  
This command visualizes the relationships between your stratigraphic units as a Harris Matrix diagram.

### Step 5: Export a PDF Report

.. code-block:: bash

   pyarchinit-mini report export --site 1 --output site_report.pdf

**Output:**

.. code-block:: text

   PDF report created: site_report.pdf

**Explanation:**  
You now have a comprehensive PDF summarizing your site's data, including stratigraphy and relationships.

🎓 Exercises
------------

1. **Exercise:**  
   Add a new site called "Monte Stella", with two stratigraphic units: a "surface layer" and a "buried floor". The surface layer should overlie the buried floor. Generate a Harris Matrix for this site.

   **Solution:**

   .. code-block:: bash

      pyarchinit-mini site add --name "Monte Stella" --location "Italy"
      pyarchinit-mini us add --site 2 --number 2001 --description "Surface layer" --type "surface"
      pyarchinit-mini us add --site 2 --number 2002 --description "Buried floor" --type "floor"
      pyarchinit-mini relationship add --site 2 --us1 2001 --us2 2002 --relationship "overlies"
      pyarchinit-mini harris-matrix generate --site 2 --output monte_stella_matrix.png

2. **Exercise:**  
   Attach a photo called `floor.jpg` to US 1001 in the "Civita Campana" site, then export a new PDF report that includes media.

   **Solution:**

   .. code-block:: bash

      pyarchinit-mini media add --site 1 --us 1001 --file floor.jpg
      pyarchinit-mini report export --site 1 --output site_report_with_media.pdf

💡 Tips
-------

* Use tab-completion (if your shell supports it) to explore available commands.
* The `--help` flag can be used with any command for more information (e.g., `pyarchinit-mini us add --help`).
* Use consistent US numbering to avoid confusion in large sites.
* Store media files in a dedicated folder and use relative paths for portability.

⚠️ Common Errors
----------------

* **Mistyped US or Site IDs:**  
  If you get "Site/US not found", double-check the IDs. Use `pyarchinit-mini site list` or `us list` to verify.

* **Missing Required Arguments:**  
  The CLI will prompt you if you forget required arguments. Always check the help output for required fields.

* **Incompatible Relationships:**  
  Don't link a US to itself or create circular relationships—Harris Matrix won't generate properly!

* **File Not Found for Media:**  
  If attaching media, make sure the file path is correct and accessible.

🔗 Additional Resources
----------------------

* `PyArchInit-Mini Documentation <https://pypi.org/project/pyarchinit-mini/>`_
* `Harris Matrix Explained (Wikipedia) <https://en.wikipedia.org/wiki/Harris_matrix>`_
* `Command-Line Basics (Real Python) <https://realpython.com/python-command-line-arguments/>`_
* `Python PDF Generation (ReportLab) <https://www.reportlab.com/docs/reportlab-userguide.pdf>`_

---

Keep experimenting with PyArchInit-Mini's CLI! These advanced features will help organize and visualize your archaeological data like a pro.