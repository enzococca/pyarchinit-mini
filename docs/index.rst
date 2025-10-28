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

What's New in Version 1.6.1
---------------------------

.. versionadded:: 1.6.1
   **Excel Import Integration & Database Schema Fix**

   This patch release completes Excel import integration and fixes critical database schema issues:

   **Excel Import Features**:

   - ✅ **Web GUI Integration**: Complete Excel import interface with dual format support
   - ✅ **Harris Matrix Template**: Sheet-based format (NODES + RELATIONSHIPS)
   - ✅ **Extended Matrix Parser**: Inline format with relationship columns
   - ✅ **Database Consistency**: Unified database path across all interfaces
   - ✅ **Metro C Testing**: Successfully tested with 65 US and 658 relationships
   - ✅ **Italian Relationships**: Full support for Italian relationship names

   **Critical Fixes**:

   - 🐛 **Database Schema**: Fixed ``id_us`` field from ``VARCHAR(100)`` to ``INTEGER AUTOINCREMENT``
   - 🐛 **Date Type Handling**: Fixed SQLite date field type errors
   - 🐛 **Desktop GUI**: Updated to use consistent database connection

   **Documentation**:

   - 📖 Complete Excel Import Guide (500+ lines)
   - 📖 Troubleshooting section with schema migration steps
   - 📖 Testing procedures and test results

   **Migration Note**: Users upgrading from v1.6.0 should recreate their database or migrate schema manually. See ``docs/EXCEL_IMPORT_BUG_FIXES.md`` for details.

   **Files**: ``docs/EXCEL_IMPORT_GUIDE.md``, ``docs/EXCEL_IMPORT_BUG_FIXES.md``, ``docs/EXCEL_IMPORT_INTEGRATION_SUMMARY.md``

What's New in Version 1.6.0
---------------------------

.. versionadded:: 1.6.0
   **Extensible EM Node Type System & Pure NetworkX GraphML Export**

   This major release introduces a flexible configuration system for Extended Matrix node types and pure-Python GraphML export:

   **Extensible EM Node Type Configuration**

   - **YAML-Based Configuration**: Node types defined in ``pyarchinit_mini/config/em_node_types.yaml`` with visual properties, relationships, and descriptions
   - **Web Management Interface**: Complete CRUD interface at ``/em-node-config`` for creating, editing, and deleting custom node types
   - **14 Built-in Node Types**: US, USM, USVA, USVB, USVC, TU, USD, SF, VSF, CON, DOC, Extractor, Combinar, property with full specifications
   - **Hot Reload Capability**: Configuration changes reflected immediately without application restart
   - **Harris Creator Integration**: Custom node types automatically available in Harris Matrix Creator dropdown
   - **Python API**: ``EMNodeConfigManager`` class for programmatic access via ``get_config_manager()``
   - **Automatic Validation**: Type checking for colors, shapes, and required fields
   - **Menu Integration**: Accessible via Configuration menu in web GUI

   **Pure NetworkX GraphML Export**

   - **No Graphviz Dependency**: GraphML export now uses pure Python with NetworkX library
   - **Consistent Node IDs**: Maintains compatibility with yEd and other graph editors
   - **Full Relationship Support**: Exports all stratigraphic relationships (Taglia, Copre, Si appoggia a, Riempie, etc.)
   - **Periodization Preservation**: Archaeological periods and phases preserved in node attributes
   - **Layout Information**: Node positioning data embedded for visual consistency
   - **Backward Compatible**: Existing DOT/Graphviz export still available
   - **Improved Performance**: Faster export for large graphs (1000+ nodes)
   - **Better Error Handling**: Clear error messages and validation

   **User Experience Improvements**

   - Color picker interface for visual node type customization
   - Bootstrap 5 styled web interface with responsive design
   - Comprehensive documentation in ``EM_NODE_TYPE_MANAGEMENT.md`` and ``PURE_NETWORKX_GRAPHML_EXPORT.md``
   - Session summary documentation in ``VERSION_1.6.0_IMPLEMENTATION_SUMMARY.md``

   **Technical Implementation**

   - ``pyarchinit_mini/config/em_node_config_manager.py``: Configuration manager with singleton pattern
   - ``web_interface/em_node_config_routes.py``: Flask blueprint for web interface
   - ``pyarchinit_mini/graphml_converter/graphml_exporter.py``: NetworkX-based exporter
   - ``web_interface/harris_creator_routes.py``: Dynamic node type loading from configuration

   **Impact**: Users can now define custom node types for project-specific Extended Matrix needs, and export Harris Matrix to GraphML without requiring Graphviz installation. Foundation for extensible archaeological data modeling.

   See :doc:`EM_NODE_TYPE_MANAGEMENT` and :doc:`PURE_NETWORKX_GRAPHML_EXPORT` for complete documentation.

What's New in Version 1.5.7
---------------------------

.. versionadded:: 1.5.7
   **Web GUI Combobox Integration**

   This release implements web interface integration with the chronological datazioni system:

   - **Web GUI Combobox**: ``datazione`` field now uses SelectField with database-driven choices from ``datazioni_table``
   - **Dynamic Choices Population**: Dropdown populated in both ``/us/create`` and ``/us/<us_id>/edit`` routes
   - **Text Input Fields**: ``periodo_iniziale``, ``periodo_finale``, ``fase_iniziale``, ``fase_finale`` changed to StringField for flexible data entry
   - **Removed Hardcoded Choices**: Eliminated 40+ hardcoded period options, replaced with open text fields
   - **Italian Translation**: Complete Italian language support for chronology field labels
   - **Service Integration**: ``DatazioneService`` initialized at app startup, ``get_datazioni_choices()`` provides formatted dropdown data
   - **Bootstrap 5 Styling**: Proper ``form-select`` for dropdown, ``form-control`` for text inputs
   - **Session Management**: Context managers ensure no detached instance errors

   **User Experience**:
   - Standardized dating selection via dropdown with 36 Italian archaeological periods
   - Free-text entry for periodo/fase fields allows flexible chronological data
   - Form displays "-- Seleziona Datazione --" as default option
   - Field labels: "Periodo Iniziale", "Fase Iniziale", "Periodo Finale", "Fase Finale", "Datazione"

   **Technical Implementation**:
   - ``web_interface/app.py``: USForm field definitions updated, DatazioneService import added
   - ``web_interface/templates/us/form.html``: Form rendering updated with correct CSS classes
   - ``pyarchinit_mini/services/datazione_service.py``: Fixed dict access in ``get_datazioni_choices()``
   - ``pyarchinit_mini/translations/it/LC_MESSAGES/messages.po``: Italian translations added

   **Impact**: Users can now select standardized datazioni from dropdown in web interface, while maintaining flexibility for periodo/fase fields. Foundation completed for Desktop GUI integration in v1.6.0.

What's New in Version 1.5.6
---------------------------

.. versionadded:: 1.5.6
   **Chronological Datazioni System**

   This release introduces a comprehensive chronological dating system for standardized archaeological periodization:

   - **New Datazioni Table**: ``datazioni_table`` model with fields for ``nome_datazione``, ``fascia_cronologica``, and ``descrizione``
   - **36 Pre-configured Italian Periods**: Default Italian archaeological periods from Paleolitico to Età Contemporanea
   - **DatazioneService**: Complete CRUD operations with validation, search, and choices generation
   - **Multi-Database Support**: Compatible with both SQLite and PostgreSQL via SQLAlchemy ORM
   - **API Ready**: ``get_datazioni_choices()`` method returns formatted data for dropdown/combobox integration
   - **Session Management**: Context managers prevent detached instance errors

   **Default Periods Included**: Paleolitico Inferiore, Paleolitico Medio, Paleolitico Superiore, Mesolitico, Neolitico (Antico/Medio/Recente/Finale), Eneolitico, Età del Bronzo (Antico/Medio/Recente/Finale), Età del Ferro (Prima/Seconda), Età Arcaica, Età Classica, Età Ellenistica, Età Repubblicana, Età Augustea, Età Giulio-Claudia, Età Flavia, Età Antonina, Età dei Severi, Crisi del III secolo, Tarda Età Imperiale, Alto Medioevo, Basso Medioevo, Età Longobarda, Età Carolingia, Età Comunale, Rinascimento, Età Moderna, Età Contemporanea, and generic periods.

   **Testing**: Comprehensive test suite (``test_datazioni_table.py``) with 90%+ coverage validates table creation, CRUD operations, and choices generation.

   **Impact**: Standardized chronological dating replaces free-text datazione field with controlled vocabulary, enabling consistent periodization for Harris Matrix exports and future GUI integration.

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
   PURE_NETWORKX_GRAPHML_EXPORT
   EM_NODE_TYPE_MANAGEMENT
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
   VERSION_1.6.0_IMPLEMENTATION_SUMMARY
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
