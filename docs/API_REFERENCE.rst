======================
API Reference Overview
======================

Welcome! This reference documents the key classes and functions in the PyArchInit-Mini plugin API, including dialogs for inventory, site, US (stratigraphic unit) recording, media, thesaurus, and database setup. Each entry includes a clear description, parameter types and examples, expected return values, practical code examples, and common use cases.

Classes
=======

ExtendedInventarioDialog
------------------------

**Description**:  
A comprehensive inventory dialog encompassing all fields from the PyArchInit plugin. Enhances inventory management with media support and integrated thesaurus vocabulary tools.

**Constructor**:
.. code-block:: python

    ExtendedInventarioDialog()

Methods
~~~~~~~

center_window()
^^^^^^^^^^^^^^^

**Description**:  
Centers the inventory dialog window on the user's screen for optimal usability.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dialog = ExtendedInventarioDialog()
    dialog.center_window()

**When to Use It**:  
Call after initializing the dialog, before showing it, to ensure it appears centrally and is user-friendly.

create_media_directory()
^^^^^^^^^^^^^^^^^^^^^^^^

**Description**:  
Creates a dedicated directory for storing media (photos, scans, etc.) associated with inventory entries.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dialog = ExtendedInventarioDialog()
    dialog.create_media_directory()

**When to Use It**:  
Use when you need to organize and attach media to inventory items, ensuring files are saved in the correct location.

PyArchInitGUI
-------------

**Description**:  
Main graphical user interface for the PyArchInit-Mini application. Handles application launch, styling, and database connectivity.

**Constructor**:
.. code-block:: python

    PyArchInitGUI()

Methods
~~~~~~~

setup_database()
^^^^^^^^^^^^^^^^

**Description**:  
Initializes and configures the connection to the PyArchInit database.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    gui = PyArchInitGUI()
    gui.setup_database()

**When to Use It**:  
Invoke at startup or when changing database settings to ensure data can be saved and loaded.

setup_styles()
^^^^^^^^^^^^^^

**Description**:  
Applies application-wide style sheets and visual themes.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    gui = PyArchInitGUI()
    gui.setup_styles()

**When to Use It**:  
Use to ensure consistent appearance, either at startup or after changing themes.

PostgreSQLInstallerDialog
-------------------------

**Description**:  
Dialog for guiding users through PostgreSQL installation and setup within PyArchInit-Mini.

**Constructor**:
.. code-block:: python

    PostgreSQLInstallerDialog()

Methods
~~~~~~~

center_window()
^^^^^^^^^^^^^^^

**Description**:  
Centers the installer dialog window.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = PostgreSQLInstallerDialog()
    dlg.center_window()

**When to Use It**:  
Ensures the installer is easily visible and accessible.

create_interface()
^^^^^^^^^^^^^^^^^^

**Description**:  
Constructs the graphical interface, including forms for entering PostgreSQL configuration.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = PostgreSQLInstallerDialog()
    dlg.create_interface()

**When to Use It**:  
Automatically called during dialog initialization; can be extended for custom interface elements.

ExtendedUSDialog
----------------

**Description**:  
Advanced dialog for recording stratigraphic units (US) with multiple tabs for detailed archaeological documentation.

**Constructor**:
.. code-block:: python

    ExtendedUSDialog()

Methods
~~~~~~~

create_interface()
^^^^^^^^^^^^^^^^^^

**Description**:  
Builds the tabbed interface for complete US recording.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = ExtendedUSDialog()
    dlg.create_interface()

**When to Use It**:  
On dialog initialization or when refreshing tabs after configuration changes.

create_basic_tab()
^^^^^^^^^^^^^^^^^^

**Description**:  
Creates and adds the "Basic" information tab for US entry.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = ExtendedUSDialog()
    dlg.create_basic_tab()

**When to Use It**:  
Useful if you need to dynamically add or refresh the basic tab, e.g., after modifying field definitions.

RelationshipDialog
------------------

**Description**:  
Dialog for adding or editing simple stratigraphic relationships between units.

**Constructor**:
.. code-block:: python

    RelationshipDialog()

Methods
~~~~~~~

create_interface()
^^^^^^^^^^^^^^^^^^

**Description**:  
Constructs the minimal interface for defining relationships.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = RelationshipDialog()
    dlg.create_interface()

**When to Use It**:  
When initializing the dialog or after modifying the set of available relationships.

save_relationship()
^^^^^^^^^^^^^^^^^^^

**Description**:  
Saves the user-defined stratigraphic relationship to the database or session.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = RelationshipDialog()
    dlg.save_relationship()

**When to Use It**:  
After the user has filled in the relationship form and clicks "Save".

PeriodizationDialog
-------------------

**Description**:  
Dialog for managing detailed periodization, including chronological phases and attributes.

**Constructor**:
.. code-block:: python

    PeriodizationDialog()

Methods
~~~~~~~

create_interface()
^^^^^^^^^^^^^^^^^^

**Description**:  
Sets up the main periodization management interface.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = PeriodizationDialog()
    dlg.create_interface()

**When to Use It**:  
When initializing or reloading the dialog.

create_chronology_tab()
^^^^^^^^^^^^^^^^^^^^^^^

**Description**:  
Adds a dedicated tab for chronological information.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = PeriodizationDialog()
    dlg.create_chronology_tab()

**When to Use It**:  
When you need to show or refresh the chronology section.

ChronologicalSequenceDialog
--------------------------

**Description**:  
Dialog for visualizing and navigating the site's chronological sequence, often as a timeline.

**Constructor**:
.. code-block:: python

    ChronologicalSequenceDialog()

Methods
~~~~~~~

create_interface()
^^^^^^^^^^^^^^^^^^

**Description**:  
Sets up the main sequence view interface.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = ChronologicalSequenceDialog()
    dlg.create_interface()

**When to Use It**:  
When opening or refreshing the sequence dialog.

create_timeline_tab()
^^^^^^^^^^^^^^^^^^^^^

**Description**:  
Adds a timeline visualization tab.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = ChronologicalSequenceDialog()
    dlg.create_timeline_tab()

**When to Use It**:  
For displaying a visual timeline of periods, phases, or events.

ThesaurusDialog
---------------

**Description**:  
Dialog for managing thesaurus entries and controlled vocabularies, supporting standardization across the project.

**Constructor**:
.. code-block:: python

    ThesaurusDialog()

Methods
~~~~~~~

center_window()
^^^^^^^^^^^^^^^

**Description**:  
Centers the thesaurus dialog window.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = ThesaurusDialog()
    dlg.center_window()

**When to Use It**:  
To keep the dialog easily accessible and visually focused.

create_interface()
^^^^^^^^^^^^^^^^^^

**Description**:  
Builds the main interface for vocabulary editing and management.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = ThesaurusDialog()
    dlg.create_interface()

**When to Use It**:  
On dialog initialization or when updating vocabulary lists.

BaseDialog
----------

**Description**:  
Abstract base class for dialog windows. Provides common methods such as centering and button creation.

**Constructor**:
.. code-block:: python

    BaseDialog()

Methods
~~~~~~~

center_window()
^^^^^^^^^^^^^^^

**Description**:  
Centers the dialog window on the screen.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = BaseDialog()
    dlg.center_window()

**When to Use It**:  
Used in all UI dialogs to ensure consistent, user-friendly window placement.

create_buttons()
^^^^^^^^^^^^^^^^

**Description**:  
Adds standard buttons (OK, Cancel, etc.) to the dialog.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = BaseDialog()
    dlg.create_buttons()

**When to Use It**:  
When setting up dialog actions, to provide standard controls.

SiteDialog
----------

**Description**:  
Dialog for creating or editing archaeological site records, with integrated media directory management.

**Constructor**:
.. code-block:: python

    SiteDialog()

Methods
~~~~~~~

create_media_directory()
^^^^^^^^^^^^^^^^^^^^^^^^

**Description**:  
Creates a dedicated folder for site-related media files.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = SiteDialog()
    dlg.create_media_directory()

**When to Use It**:  
When uploading or linking site documentation images, plans, or maps.

create_form()
^^^^^^^^^^^^^

**Description**:  
Builds the site data entry form, including fields for name, location, description, etc.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    dlg = SiteDialog()
    dlg.create_form()

**When to Use It**:  
At dialog initialization or when the form structure is updated.

Functions
=========

main()
------

**Description**:  
Entry point function. Launches the main application or a specific dialog, depending on context.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    if __name__ == "__main__":
        main()

**When to Use It**:  
To start the application or as a script entry point.

test_all_improvements()
----------------------

**Description**:  
Runs a suite of tests to verify all recent improvements and bug fixes in the application.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    test_all_improvements()

**When to Use It**:  
Before release or after major updates to confirm stability.

run_api()
---------

**Description**:  
Starts the API server for programmatic access to PyArchInit-Mini functionalities.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    run_api()

**When to Use It**:  
When integrating PyArchInit-Mini with other software or services.

test_harris_gui()
-----------------

**Description**:  
Launches and tests the Harris Matrix (stratigraphic sequence) GUI dialog.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    test_harris_gui()

**When to Use It**:  
For UI testing or development of the Harris Matrix interface.

test_media_manager_import()
--------------------------

**Description**:  
Tests the import functionality for the media manager module.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    test_media_manager_import()

**When to Use It**:  
During development or after refactoring media management code.

test_improved_harris_dialog()
----------------------------

**Description**:  
Tests the latest version of the Harris dialog for improved features and bug fixes.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    test_improved_harris_dialog()

**When to Use It**:  
To validate enhancements to the Harris Matrix dialog.

test_session_fixes()
-------------------

**Description**:  
Runs tests focusing on recent session-handling improvements.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    test_session_fixes()

**When to Use It**:  
After session handling code has been updated.

test_all_interfaces()
--------------------

**Description**:  
Launches and checks all graphical interfaces to ensure they load and behave as expected.

**Parameters**:  
None

**Return Value**:  
None

**Practical Example**:
.. code-block:: python

    test_all_interfaces()

**When to Use It**:  
During QA or before deployment, as a comprehensive interface check.

-----------------
Common Use Cases
-----------------

* Recording archaeological inventories and related media
* Managing archaeological sites and stratigraphic units
* Standardizing terms with thesaurus integration
* Visualizing stratigraphic and chronological sequences
* Running tests and ensuring application integrity
* Integrating with other systems via API

For more details and usage scenarios, consult the full PyArchInit-Mini documentation or community forums.