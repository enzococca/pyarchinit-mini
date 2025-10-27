.. image:: _static/images/pyarchinit-mini-logo.png
   :align: center
   :width: 300px
   :alt: PyArchInit-Mini Logo

PyArchInit-Mini Documentation
=============================

.. image:: https://badge.fury.io/py/pyarchinit-mini.svg
   :target: https://badge.fury.io/py/pyarchinit-mini
   :alt: PyPI version

.. image:: https://img.shields.io/badge/python-3.8--3.14-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python versions

.. image:: https://img.shields.io/badge/License-GPL%20v2-blue.svg
   :target: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
   :alt: License

.. image:: https://readthedocs.org/projects/pyarchinit-mini/badge/?version=latest
   :target: https://pyarchinit-mini.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

**Lightweight Archaeological Data Management System**

PyArchInit-Mini is a standalone, modular version of PyArchInit focused on core archaeological data management functionality without GIS dependencies. It provides multiple interfaces (Web, Desktop GUI, CLI, REST API) with a clean, scalable architecture for managing archaeological sites, stratigraphic units, and material inventories.

Key Features
------------

- **Multi-Interface Support**: Web, Desktop GUI, CLI, and REST API
- **Multi-Database**: SQLite and PostgreSQL support
- **Internationalization**: Full Italian and English language support
- **Harris Matrix**: Graphviz visualization with GraphML export
- **3D Visualization**: s3Dgraphy integration for stratigraphic units
- **Multi-User Authentication**: Role-based access control
- **Real-Time Collaboration**: WebSocket support for team updates
- **Analytics Dashboard**: Interactive charts and data visualization

What's New in Version 1.5.5
---------------------------

.. versionadded:: 1.5.5
   **Documentation and Internationalization Improvements**

   This release focuses on improving documentation quality and accessibility:

   - **Complete English Translation**: All README content fully translated to English for international audience
   - **ReadTheDocs Compatibility**: Documentation links updated to point to pyarchinit-mini.readthedocs.io
   - **PyPI Package Description**: Clean, English-only package description on PyPI
   - **Improved Installation Instructions**: Clearer Graphviz installation steps for Windows users

   **Impact**: International users can now access complete documentation in English on both PyPI and ReadTheDocs.

What's New in Version 1.5.4
---------------------------

.. versionadded:: 1.5.0
   **GraphML Export - Periodization Display Fixed**

   This release fixes a critical issue in GraphML export where only 3-4 archaeological periods were being displayed instead of all available periods:

   - **Complete Period Display**: All archaeological periods now properly visible in GraphML export to yEd
   - **Chronological Ordering**: Periods arranged in correct chronological sequence (oldest to newest) based on periodo_iniziale and fase_iniziale fields
   - **Reverse Epochs Support**: Proper reverse chronological ordering (newest to oldest) when enabled
   - **Large Site Support**: Tested and verified with Dom zu Lund site (758 US nodes, 8 periods)
   - **Enhanced Parser**: Improved DOT file parsing to handle both quoted and unquoted label formats from Graphviz

   **Impact**: Sites with complex periodization now display complete stratigraphic sequences in yEd Graph Editor, maintaining consistency with database periodization.

   See :doc:`features/harris_matrix` for complete documentation.

Getting Started
---------------

.. toctree::
   :maxdepth: 2
   :caption: Installation & Setup:

   installation/quickstart
   installation/requirements
   installation/configuration
   installation/first_steps

User Interfaces
---------------

.. toctree::
   :maxdepth: 2
   :caption: Interface Documentation:

   web/index
   gui/index
   cli/index
   api/index

Features
--------

.. toctree::
   :maxdepth: 2
   :caption: Feature Documentation:

   features/harris_matrix
   features/harris_matrix_import
   features/stratigraphic_relationships
   features/s3dgraphy
   features/graphml_export
   features/pyarchinit_import_export
   AUTOMATIC_IMPORT_AND_BACKUP_GUIDE
   features/analytics
   features/authentication
   features/export_import
   features/media_management
   EXTENDED_MATRIX_FRAMEWORK
   EXTENDED_MATRIX_EXPORT
   DOC_FILE_UPLOAD

Data Management
---------------

.. toctree::
   :maxdepth: 2
   :caption: Data Documentation:

   data/sites
   data/stratigraphic_units
   data/inventory
   data/database_management
   data/migrations

Development
-----------

.. toctree::
   :maxdepth: 2
   :caption: Developer Documentation:

   development/architecture
   development/api_reference
   development/contributing
   development/testing
   development/changelog
   DOCUMENTATION_VERIFICATION

Examples & Tutorials
--------------------

.. toctree::
   :maxdepth: 2
   :caption: Examples:

   examples/python_api
   examples/rest_api
   examples/cli_usage
   examples/integration

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
