🚀 Quick Start - PyArchInit-Mini
=================================

📖 What is PyArchInit-Mini?
--------------------------

**PyArchInit-Mini** is a lightweight, modular CLI tool designed for archaeological data management. Whether you’re cataloguing sites, handling stratigraphic units, or managing material inventories, PyArchInit-Mini provides a powerful yet simple interface—without the overhead of GIS dependencies. Built with robust data validation, advanced search and filtering, and seamless session management, it’s perfect for both field archaeologists and researchers who want to keep their data organized and accessible.

💿 Installation
---------------

Getting started is a breeze! Just run the following command in your terminal:

.. code-block:: bash

   pip install pyarchinit-mini

That’s it—you’re ready to start managing archaeological data!

⚡ First Example
---------------

Let’s dive right in! Suppose you want to add a new archaeological site to your database using the CLI.

### Input:

.. code-block:: bash

   pyarchinit-mini site add --name "Monte Testaccio" --location "Rome, Italy" --period "Imperial Roman"

### Output:

.. code-block:: text

   ✅ Site added successfully!
   ---------------------------
   ID:          1
   Name:        Monte Testaccio
   Location:    Rome, Italy
   Period:      Imperial Roman
   Created At:  2024-06-20 14:32:11

Now, let’s say you want to quickly search for all sites from the “Imperial Roman” period:

### Input:

.. code-block:: bash

   pyarchinit-mini site search --period "Imperial Roman"

### Output:

.. code-block:: text

   🔍 Search Results (1):
   -------------------------------------
   [1] Monte Testaccio | Rome, Italy | Imperial Roman

🎯 What's Next?
---------------

Ready to dig deeper? Check out these resources:

* `Full CLI User Guide <https://github.com/enzococca/pyarchinit-mini/wiki/CLI-Guide>`_
* `Managing Stratigraphic Units <https://github.com/enzococca/pyarchinit-mini/wiki/Stratigraphic-Units>`_
* `Material Inventory Tutorial <https://github.com/enzococca/pyarchinit-mini/wiki/Material-Inventory>`_
* `REST API Documentation (Swagger/OpenAPI) <http://localhost:8000/docs>`_

Happy excavating! 🏺