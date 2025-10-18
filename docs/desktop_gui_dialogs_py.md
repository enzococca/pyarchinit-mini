# desktop_gui/dialogs.py

## Overview

This file contains 207 documented elements.

## Classes

### BaseDialog

Base class for dialog windows

#### Methods

##### __init__(self, parent, title, width, height)

Initializes a new instance of the `BaseDialog` class by creating and configuring a modal dialog window with the specified parent, title, width, and height. This method sets up the dialog's main, content, and button frames, ensures the window is centered on the parent, and enables resizing and modality for user interaction.

##### center_window(self)

Center dialog window on parent

##### create_buttons(self, ok_text, cancel_text)

Create standard OK/Cancel buttons

##### ok(self)

OK button handler - to be overridden

##### cancel(self)

Cancel button handler

### SiteDialog

Dialog for creating/editing sites with media support

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, site_service, media_service, site, callback)

Initializes a new instance of the **SiteDialog** class for creating or editing a site, with optional media support. It sets up the dialog window, initializes services and site data, creates the media directory, and constructs the form and action buttons. If an existing site is provided, the form is pre-populated and associated media are loaded.

##### create_media_directory(self)

Create media directory for the site

##### create_form(self)

Create site form with tabs

##### create_basic_tab(self)

Create basic information tab

##### create_description_tab(self)

Create description tab

##### create_media_tab(self)

Create media management tab with thumbnails and drag & drop

##### add_media_file(self, event)

Add media file with file dialog

##### process_media_file(self, file_path)

Process and add media file to the list

##### refresh_media_list(self)

Refresh the media list display

##### format_file_size(self, size_bytes)

Format file size in human readable format

##### on_media_select(self, event)

Handle media selection

##### remove_media_file(self)

Remove selected media file

##### preview_media(self)

Preview selected media file

##### load_media(self)

Load existing media files for the site

##### populate_form(self)

Populate form with existing site data

##### ok(self)

Save site data

### USDialog

Dialog for creating/editing US

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, us_service, site_names, us, callback)

Initializes the form for creating or editing a site, setting up the necessary UI fields and internal variables. If an existing site is provided, it prepares the form with the site's current data for editing; otherwise, it initializes the form for creating a new site. This method also configures the connections to the site service for handling data retrieval and submission.

##### create_form(self)

Create US form

##### populate_form(self)

Populate form with existing US data

##### ok(self)

Save US data

### InventarioDialog

Dialog for creating/editing inventory items

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, inventario_service, site_names, inventario, callback)

Initializes the form by setting up the data fields and populating them with existing values if an "US" (Unità Stratigrafica) instance is provided. It prepares the form for either creating a new US record or updating an existing one, ensuring proper handling and validation of input fields.

##### create_form(self)

Create inventory form

##### populate_form(self)

Populate form with existing inventory data

##### ok(self)

Save inventory data

### HarrisMatrixDialog

Dialog for generating and viewing Harris Matrix

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, matrix_generator, matrix_visualizer, sites)

Initializes a new instance of the class, setting up the necessary fields and user interface components for inventory data entry. This method also prepares the form for creating a new inventory item or updating an existing one, depending on whether inventory data is provided. It ensures that all input fields are properly configured and linked to the underlying inventory management service.

##### create_interface(self)

Create Harris Matrix interface

##### generate_matrix(self)

Generate Harris Matrix for selected site

##### display_statistics(self, stats)

Display matrix statistics

##### display_levels(self)

Display matrix levels

##### export_matrix(self)

Export Harris Matrix to files

##### open_advanced_editor(self)

Open advanced Harris Matrix editor

### PDFExportDialog

Dialog for PDF export

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, pdf_generator, site_service, us_service, inventario_service, sites)

Initializes the object by setting the current site, displaying matrix statistics and levels, and visualizing the matrix. Upon successful completion, it shows a confirmation message; if an error occurs during the process, it displays an error message. This method ensures that the UI is updated with the latest matrix information for the selected site.

##### create_interface(self)

Create PDF export interface

##### select_output_file(self)

Select output file

##### ok(self)

Generate PDF report

### DatabaseConfigDialog

Dialog for database configuration

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, callback)

**\_\_init\_\_ Method Documentation:**

Initializes the object by setting up the plotting axes and canvas for displaying images or data. It configures the axis limits to adjust automatically and triggers an initial rendering of the canvas to reflect the current state. This setup ensures that the display is ready for further interactions, such as zooming or data updates.

##### create_interface(self)

Create database configuration interface

##### on_db_type_change(self)

Handle database type change

##### browse_sqlite_file(self)

Browse for SQLite file

##### test_connection(self)

Test PostgreSQL connection

##### build_postgres_connection_string(self)

Build PostgreSQL connection string

##### ok(self)

Connect to selected database

### MediaManagerDialog

Dialog for media management

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, media_handler)

Initializes the class by setting up the required service dependencies and a list of available sites. It also constructs the user interface for PDF export by invoking methods to create the interface elements and action buttons.

##### create_interface(self)

Create media management interface

##### select_file(self)

Select file to upload

##### upload_file(self)

Upload selected file

### StatisticsDialog

Dialog for viewing statistics

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, site_service, us_service, inventario_service)

Initializes the object by processing a list of inventory items related to a specific site. If no items are found for the given site, it displays a warning message to the user. Otherwise, it converts each inventory item into a dictionary format, ensuring all relevant attributes are included for further use.

##### create_interface(self)

Create statistics interface

##### load_statistics(self)

Load and display statistics

### BaseDialog

Base class for dialog windows

#### Methods

##### __init__(self, parent, title, width, height)

Initializes a new instance of the `BaseDialog` class.  
This method creates and configures a modal dialog window as a child of the specified parent, sets its title and dimensions, centers it on the screen, and sets up the main layout frames for content and buttons.  
Optional parameters allow customization of the dialog's width and height.

##### center_window(self)

Center dialog window on parent

##### create_buttons(self, ok_text, cancel_text)

Create standard OK/Cancel buttons

##### ok(self)

OK button handler - to be overridden

##### cancel(self)

Cancel button handler

### SiteDialog

Dialog for creating/editing sites with media support

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, site_service, media_service, site, callback)

Initializes a new instance of the **SiteDialog** class, setting up the dialog window for creating or editing a site, with optional media support. This method configures the dialog's title, associates the required services, initializes form elements and buttons, and, if editing an existing site, pre-populates the form and loads associated media.

##### create_media_directory(self)

Create media directory for the site

##### create_form(self)

Create site form with tabs

##### create_basic_tab(self)

Create basic information tab

##### create_description_tab(self)

Create description tab

##### create_media_tab(self)

Create media management tab with thumbnails and drag & drop

##### add_media_file(self, event)

Add media file with file dialog

##### process_media_file(self, file_path)

Process and add media file to the list

##### refresh_media_list(self)

Refresh the media list display

##### format_file_size(self, size_bytes)

Format file size in human readable format

##### on_media_select(self, event)

Handle media selection

##### remove_media_file(self)

Remove selected media file

##### preview_media(self)

Preview selected media file

##### load_media(self)

Load existing media files for the site

##### populate_form(self)

Populate form with existing site data

##### ok(self)

Save site data

### USDialog

Dialog for creating/editing US

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, us_service, site_names, us, callback)

Initializes a new instance of the **USDialog** class for creating or editing a US (Unità Stratigrafica). Sets up the dialog window with form fields, action buttons, and optionally populates the form with existing US data if provided. Also stores references to the US service, site names, and an optional callback for further processing.

##### create_form(self)

Create US form

##### populate_form(self)

Populate form with existing US data

##### ok(self)

Save US data

### InventarioDialog

Dialog for creating/editing inventory items

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, inventario_service, site_names, inventario, callback)

Initializes a new instance of the **InventarioDialog** class for creating or editing inventory items.  
This method sets up the dialog window, initializes its attributes with the provided inventory service, site names, existing inventory item (if any), and callback function, and creates the input form and action buttons. If an existing inventory item is provided, the form is pre-populated with its data.

##### create_form(self)

Create inventory form

##### populate_form(self)

Populate form with existing inventory data

##### ok(self)

Save inventory data

### HarrisMatrixDialog

Dialog for generating and viewing Harris Matrix

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, matrix_generator, matrix_visualizer, sites, site_service, us_service, db_manager)

Initializes a new instance of the **HarrisMatrixDialog** class, setting up the dialog window for generating and viewing a Harris Matrix. This method assigns the provided matrix generator, matrix visualizer, list of sites, and optional services to instance variables, then constructs the user interface and customizes the dialog buttons to display only a "Close" option.

##### create_interface(self)

Create Harris Matrix interface

##### generate_matrix(self)

Generate Harris Matrix for selected site

##### display_statistics(self, stats)

Display matrix statistics

##### display_levels(self)

Display matrix levels

##### export_matrix(self)

Export Harris Matrix to files

##### open_advanced_editor(self)

Open advanced Harris Matrix editor

### PDFExportDialog

Dialog for PDF export

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, pdf_generator, site_service, us_service, inventario_service, sites)

Initializes the visualizer for the Harris Matrix using PyArchInit-style rendering. This method retrieves the current layout setting, configures visualization parameters for optimal readability, and generates a high-resolution matrix image, saving the output to a temporary file. The path to the generated image is stored for further use.

##### create_interface(self)

Create PDF export interface

##### select_output_file(self)

Select output file

##### ok(self)

Generate PDF report

### DatabaseConfigDialog

Dialog for database configuration

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, callback)

Initializes a new instance of the class, setting up all necessary attributes and dependencies required for operation. This method typically prepares services and resources that the class will use, ensuring the object is in a valid, ready-to-use state after creation.

##### create_interface(self)

Create database configuration interface

##### on_db_type_change(self)

Handle database type change

##### browse_sqlite_file(self)

Browse for SQLite file

##### test_connection(self)

Test PostgreSQL connection

##### build_postgres_connection_string(self)

Build PostgreSQL connection string

##### ok(self)

Connect to selected database

### MediaManagerDialog

Dialog for media management

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, media_handler)

Initializes the class instance and prepares the necessary data structures for handling inventory records. This method extracts relevant attributes from inventory objects, assembles them into dictionaries, and manages the generation and saving of inventory PDF reports. It also provides user feedback upon successful completion of the PDF generation process.

##### create_interface(self)

Create media management interface

##### select_file(self)

Select file to upload

##### upload_file(self)

Upload selected file

### StatisticsDialog

Dialog for viewing statistics

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, site_service, us_service, inventario_service)

Initializes the user interface components for configuring PostgreSQL database connections within the application. This method creates and arranges input fields for host, port, and database name, assigning default values and organizing them within a labeled frame for easy user access. It also sets up an "Import Database" button to facilitate database import operations.

##### create_interface(self)

Create statistics interface

##### load_statistics(self)

Load and display statistics

### BaseDialog

Base class for dialog windows

#### Methods

##### __init__(self, parent, title, width, height)

Initializes a new instance of the BaseDialog class by creating and configuring a dialog window as a child of the specified parent widget. Sets the dialog's title, size, and modality, centers it on the parent, and constructs the main, content, and button frames for further customization. This method also initializes attributes for storing the dialog result and an optional callback.

##### center_window(self)

Center dialog window on parent

##### create_buttons(self, ok_text, cancel_text)

Create standard OK/Cancel buttons

##### ok(self)

OK button handler - to be overridden

##### cancel(self)

Cancel button handler

### SiteDialog

Dialog for creating/editing sites with media support

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, site_service, media_service, site, callback)

Initializes a new instance of the **SiteDialog** class for creating or editing a site, optionally with media support. This method sets up the dialog window, initializes service references, prepares the media directory, and populates the form and media list if an existing site is provided. It also configures the dialog's form fields and action buttons.

##### create_media_directory(self)

Create media directory for the site

##### create_form(self)

Create site form with tabs

##### create_basic_tab(self)

Create basic information tab

##### create_description_tab(self)

Create description tab

##### create_media_tab(self)

Create media management tab with thumbnails and drag & drop

##### add_media_file(self, event)

Add media file with file dialog

##### process_media_file(self, file_path)

Process and add media file to the list

##### refresh_media_list(self)

Refresh the media list display

##### format_file_size(self, size_bytes)

Format file size in human readable format

##### on_media_select(self, event)

Handle media selection

##### remove_media_file(self)

Remove selected media file

##### preview_media(self)

Preview selected media file

##### load_media(self)

Load existing media files for the site

##### populate_form(self)

Populate form with existing site data

##### ok(self)

Save site data

### USDialog

Dialog for creating/editing US

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, us_service, site_names, us, callback)

Initializes a new instance of the USDialog class for creating or editing a "US" entity. Sets up the dialog window with the appropriate title and size, stores provided services and data, and creates the form and action buttons. If an existing "US" is provided, the form is pre-populated with its data.

##### create_form(self)

Create US form

##### populate_form(self)

Populate form with existing US data

##### ok(self)

Save US data

### InventarioDialog

Dialog for creating/editing inventory items

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, inventario_service, site_names, inventario, callback)

Initializes a new instance of the **InventarioDialog** class, setting up the dialog window for creating or editing inventory items. It configures the dialog title, dimensions, and fields based on whether an existing inventory item is provided, initializes necessary services and callbacks, and prepares the form and action buttons. If an inventory item is supplied, the form is pre-populated with its data.

##### create_form(self)

Create inventory form

##### populate_form(self)

Populate form with existing inventory data

##### ok(self)

Save inventory data

### HarrisMatrixDialog

Dialog for generating and viewing Harris Matrix

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, matrix_generator, matrix_visualizer, sites, site_service, us_service, db_manager)

Initializes a new instance of the **HarrisMatrixDialog** class. This constructor sets up the dialog window with the provided matrix generator, matrix visualizer, list of sites, and optional service and database manager dependencies. It also configures the user interface and customizes the dialog buttons to display only a "Close" option.

##### create_interface(self)

Create Harris Matrix interface

##### generate_matrix(self)

Generate Harris Matrix for selected site

##### display_statistics(self, stats)

Display matrix statistics

##### display_levels(self)

Display matrix levels

##### visualize_matrix(self)

Visualize Harris Matrix using PyArchInit-style Graphviz

##### on_layout_changed(self, event)

Handle layout option change

##### zoom_in(self)

Zoom in on the matrix

##### zoom_out(self)

Zoom out on the matrix

##### zoom_fit(self)

Fit matrix to window

##### on_scroll(self, event)

Handle mouse wheel zoom

##### on_button_press(self, event)

Handle mouse button press for pan

##### on_button_release(self, event)

Handle mouse button release

##### on_mouse_move(self, event)

Handle mouse movement for pan

##### export_matrix(self)

Export Harris Matrix to files

##### open_advanced_editor(self)

Open advanced Harris Matrix editor

### PDFExportDialog

Dialog for PDF export

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, pdf_generator, site_service, us_service, inventario_service, sites)

Initializes a new instance of the **PDFExportDialog** class. This constructor sets up the dialog window for exporting PDFs by initializing required services and data, and creates the user interface and dialog buttons. It requires references to the parent window, a PDF generator, various service objects, and a list of available sites.

##### create_interface(self)

Create PDF export interface

##### select_output_file(self)

Select output file

##### ok(self)

Generate PDF report

### DatabaseConfigDialog

Dialog for database configuration

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, callback)

Initializes a new instance of the DatabaseConfigDialog class.  
Sets up the dialog window with a specified parent, optional callback function, and predefined dimensions and title.  
Also initializes the user interface and dialog buttons for database configuration.

##### create_interface(self)

Create database configuration interface

##### on_db_type_change(self)

Handle database type change

##### browse_sqlite_file(self)

Browse for SQLite file

##### use_sample_database(self)

Use the sample database

##### create_new_database(self)

Create a new empty database

##### import_database(self)

Import database from file

##### create_sample_database(self)

Create sample database

##### test_connection(self)

Test PostgreSQL connection

##### build_postgres_connection_string(self)

Build PostgreSQL connection string

##### ok(self)

Connect to selected database

### MediaManagerDialog

Dialog for media management

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, media_handler)

**__init__(self, parent, media_handler):**  
Initializes a new instance of the `MediaManagerDialog` class, setting up the dialog window for media management. It configures the dialog's title, size, and associates it with the provided media handler, then creates the user interface and customizes the dialog buttons to display only the "Close" option.

##### create_interface(self)

Create media management interface

##### select_file(self)

Select file to upload

##### upload_file(self)

Upload selected file

### StatisticsDialog

Dialog for viewing statistics

**Inherits from**: BaseDialog

#### Methods

##### __init__(self, parent, site_service, us_service, inventario_service)

Initializes a new instance of the StatisticsDialog class.  
This method sets up the dialog window with the provided parent and service objects, creates the user interface components, configures the dialog buttons to only display "Chiudi" (Close), and loads the initial statistics into the interface.

##### create_interface(self)

Create statistics interface

##### load_statistics(self)

Load and display statistics

## Functions

### get_attr(obj, attr_name, default)

The **`get_attr`** function is a helper designed to retrieve an attribute value from an object, which can be either a dictionary or a data transfer object (DTO). It attempts to access the specified attribute using `getattr` if present, or falls back to the `get` method if the object is a dictionary, returning a default value if the attribute is not found or is falsy. This ensures flexible and safe attribute access across different object types.

**Parameters:**
- `obj`
- `attr_name`
- `default`

### get_attr(obj, attr_name, default)

The `get_attr` function is a utility that retrieves the value of a specified attribute from an object, supporting both standard Python objects (using attribute access) and dictionary-like objects (using key access). If the attribute or key does not exist, or if the retrieved value is falsy, it returns a provided default value (empty string by default). This ensures flexible and safe extraction of data from heterogeneous objects.

**Parameters:**
- `obj`
- `attr_name`
- `default`

