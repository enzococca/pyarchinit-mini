# pyarchinit-mini - API Reference

Complete API documentation with classes, methods, and functions.

Generated: 2025-10-16 16:43:57

---


## Module: `cli_interface/cli_app.py`

**File Path:** `cli_interface/cli_app.py`

### Classes

#### `PyArchInitCLI`

Interactive CLI for PyArchInit-Mini

**Methods:**

##### `__init__(self, database_url: str)`

Initializes a new instance of the PyArchInitCLI class. This method sets up the database connection, initializes the database schema and management components, and creates service objects required for site, unit, inventory management, matrix generation and visualization, and PDF generation. If no database URL is provided, it defaults to an environment variable or a local SQLite database.

**Parameters:**

- `self`
- `database_url` (str)

---

##### `create_site(self)`

Create new site

**Parameters:**

- `self`

---

##### `generate_harris_matrix(self)`

Generate Harris Matrix for a site

**Parameters:**

- `self`

---

##### `harris_matrix_menu(self)`

Harris Matrix menu

**Parameters:**

- `self`

---

##### `list_sites(self)`

List all sites

**Parameters:**

- `self`

---

##### `list_us(self)`

List all US

**Parameters:**

- `self`

---

##### `run(self)`

Run the CLI application

**Parameters:**

- `self`

---

##### `show_help(self)`

Show help information

**Parameters:**

- `self`

---

##### `show_main_menu(self)`

Show main menu and handle selection

**Parameters:**

- `self`

---

##### `show_welcome(self)`

Show welcome screen

**Parameters:**

- `self`

---

##### `sites_menu(self)`

Sites management menu

**Parameters:**

- `self`

---

##### `statistics_menu(self)`

Statistics and reports menu

**Parameters:**

- `self`

---

##### `us_menu(self)`

US management menu

**Parameters:**

- `self`

---

##### `view_site(self)`

View site details

**Parameters:**

- `self`

---


#### `PyArchInitCLI`

Interactive CLI for PyArchInit-Mini

**Methods:**

##### `__init__(self, database_url: str)`

Initializes a new instance of the **PyArchInitCLI** class. This method sets up the application console, configures the database connection (using the provided `database_url` or a default value), creates required database tables, and initializes all core service components needed for the CLI to function.

**Parameters:**

- `self`
- `database_url` (str)

---

##### `create_site(self)`

Create new site

**Parameters:**

- `self`

---

##### `generate_harris_matrix(self)`

Generate Harris Matrix for a site

**Parameters:**

- `self`

---

##### `harris_matrix_menu(self)`

Harris Matrix menu

**Parameters:**

- `self`

---

##### `list_sites(self)`

List all sites

**Parameters:**

- `self`

---

##### `list_us(self)`

List all US

**Parameters:**

- `self`

---

##### `run(self)`

Run the CLI application

**Parameters:**

- `self`

---

##### `show_help(self)`

Show help information

**Parameters:**

- `self`

---

##### `show_main_menu(self)`

Show main menu and handle selection

**Parameters:**

- `self`

---

##### `show_welcome(self)`

Show welcome screen

**Parameters:**

- `self`

---

##### `sites_menu(self)`

Sites management menu

**Parameters:**

- `self`

---

##### `statistics_menu(self)`

Statistics and reports menu

**Parameters:**

- `self`

---

##### `us_menu(self)`

US management menu

**Parameters:**

- `self`

---

##### `view_site(self)`

View site details

**Parameters:**

- `self`

---


#### `PyArchInitCLI`

Interactive CLI for PyArchInit-Mini

**Methods:**

##### `__init__(self, database_url: str)`

Initializes a new instance of the `PyArchInitCLI` class.  
This method sets up the command-line interface environment by configuring the database connection, initializing the database schema, and instantiating all core services required for site, stratigraphic unit, inventory management, Harris matrix generation, visualization, and PDF export. An optional `database_url` parameter can be provided; otherwise, a default or environment-specified database is used.

**Parameters:**

- `self`
- `database_url` (str)

---

##### `create_site(self)`

Create new site

**Parameters:**

- `self`

---

##### `generate_harris_matrix(self)`

Generate Harris Matrix for a site

**Parameters:**

- `self`

---

##### `harris_matrix_menu(self)`

Harris Matrix menu

**Parameters:**

- `self`

---

##### `list_sites(self)`

List all sites

**Parameters:**

- `self`

---

##### `list_us(self)`

List all US

**Parameters:**

- `self`

---

##### `run(self)`

Run the CLI application

**Parameters:**

- `self`

---

##### `show_help(self)`

Show help information

**Parameters:**

- `self`

---

##### `show_main_menu(self)`

Show main menu and handle selection

**Parameters:**

- `self`

---

##### `show_welcome(self)`

Show welcome screen

**Parameters:**

- `self`

---

##### `sites_menu(self)`

Sites management menu

**Parameters:**

- `self`

---

##### `statistics_menu(self)`

Statistics and reports menu

**Parameters:**

- `self`

---

##### `us_menu(self)`

US management menu

**Parameters:**

- `self`

---

##### `view_site(self)`

View site details

**Parameters:**

- `self`

---


### Functions

#### `main(database_url, version)`

PyArchInit-Mini Interactive CLI

**Parameters:**

- `database_url`
- `version`

**Decorators:** `click.command, click.option, click.option`

---

#### `main(database_url, version)`

PyArchInit-Mini Interactive CLI

**Parameters:**

- `database_url`
- `version`

**Decorators:** `click.command, click.option, click.option`

---

#### `main(database_url, version)`

PyArchInit-Mini Interactive CLI

**Parameters:**

- `database_url`
- `version`

**Decorators:** `click.command, click.option, click.option`

---


\newpage


## Module: `desktop_gui/__init__.py`

**File Path:** `desktop_gui/__init__.py`


\newpage


## Module: `desktop_gui/dialogs.py`

**File Path:** `desktop_gui/dialogs.py`

### Classes

#### `BaseDialog`

Base class for dialog windows

**Methods:**

##### `__init__(self, parent, title, width, height)`

Initializes a new instance of the `BaseDialog` class by creating and configuring a modal dialog window with the specified parent, title, width, and height. This method sets up the dialog's main, content, and button frames, ensures the window is centered on the parent, and enables resizing and modality for user interaction.

**Parameters:**

- `self`
- `parent`
- `title`
- `width`
- `height`

---

##### `cancel(self)`

Cancel button handler

**Parameters:**

- `self`

---

##### `center_window(self)`

Center dialog window on parent

**Parameters:**

- `self`

---

##### `create_buttons(self, ok_text, cancel_text)`

Create standard OK/Cancel buttons

**Parameters:**

- `self`
- `ok_text`
- `cancel_text`

---

##### `ok(self)`

OK button handler - to be overridden

**Parameters:**

- `self`

---


#### `BaseDialog`

Base class for dialog windows

**Methods:**

##### `__init__(self, parent, title, width, height)`

Initializes a new instance of the `BaseDialog` class.  
This method creates and configures a modal dialog window as a child of the specified parent, sets its title and dimensions, centers it on the screen, and sets up the main layout frames for content and buttons.  
Optional parameters allow customization of the dialog's width and height.

**Parameters:**

- `self`
- `parent`
- `title`
- `width`
- `height`

---

##### `cancel(self)`

Cancel button handler

**Parameters:**

- `self`

---

##### `center_window(self)`

Center dialog window on parent

**Parameters:**

- `self`

---

##### `create_buttons(self, ok_text, cancel_text)`

Create standard OK/Cancel buttons

**Parameters:**

- `self`
- `ok_text`
- `cancel_text`

---

##### `ok(self)`

OK button handler - to be overridden

**Parameters:**

- `self`

---


#### `BaseDialog`

Base class for dialog windows

**Methods:**

##### `__init__(self, parent, title, width, height)`

Initializes a new instance of the BaseDialog class by creating and configuring a dialog window as a child of the specified parent widget. Sets the dialog's title, size, and modality, centers it on the parent, and constructs the main, content, and button frames for further customization. This method also initializes attributes for storing the dialog result and an optional callback.

**Parameters:**

- `self`
- `parent`
- `title`
- `width`
- `height`

---

##### `cancel(self)`

Cancel button handler

**Parameters:**

- `self`

---

##### `center_window(self)`

Center dialog window on parent

**Parameters:**

- `self`

---

##### `create_buttons(self, ok_text, cancel_text)`

Create standard OK/Cancel buttons

**Parameters:**

- `self`
- `ok_text`
- `cancel_text`

---

##### `ok(self)`

OK button handler - to be overridden

**Parameters:**

- `self`

---


#### `DatabaseConfigDialog`

Dialog for database configuration

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, callback)`

**\_\_init\_\_ Method Documentation:**

Initializes the object by setting up the plotting axes and canvas for displaying images or data. It configures the axis limits to adjust automatically and triggers an initial rendering of the canvas to reflect the current state. This setup ensures that the display is ready for further interactions, such as zooming or data updates.

**Parameters:**

- `self`
- `parent`
- `callback`

---

##### `browse_sqlite_file(self)`

Browse for SQLite file

**Parameters:**

- `self`

---

##### `build_postgres_connection_string(self)`

Build PostgreSQL connection string

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create database configuration interface

**Parameters:**

- `self`

---

##### `ok(self)`

Connect to selected database

**Parameters:**

- `self`

---

##### `on_db_type_change(self)`

Handle database type change

**Parameters:**

- `self`

---

##### `test_connection(self)`

Test PostgreSQL connection

**Parameters:**

- `self`

---


#### `DatabaseConfigDialog`

Dialog for database configuration

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, callback)`

Initializes a new instance of the class, setting up all necessary attributes and dependencies required for operation. This method typically prepares services and resources that the class will use, ensuring the object is in a valid, ready-to-use state after creation.

**Parameters:**

- `self`
- `parent`
- `callback`

---

##### `browse_sqlite_file(self)`

Browse for SQLite file

**Parameters:**

- `self`

---

##### `build_postgres_connection_string(self)`

Build PostgreSQL connection string

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create database configuration interface

**Parameters:**

- `self`

---

##### `ok(self)`

Connect to selected database

**Parameters:**

- `self`

---

##### `on_db_type_change(self)`

Handle database type change

**Parameters:**

- `self`

---

##### `test_connection(self)`

Test PostgreSQL connection

**Parameters:**

- `self`

---


#### `DatabaseConfigDialog`

Dialog for database configuration

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, callback)`

Initializes a new instance of the DatabaseConfigDialog class.  
Sets up the dialog window with a specified parent, optional callback function, and predefined dimensions and title.  
Also initializes the user interface and dialog buttons for database configuration.

**Parameters:**

- `self`
- `parent`
- `callback`

---

##### `browse_sqlite_file(self)`

Browse for SQLite file

**Parameters:**

- `self`

---

##### `build_postgres_connection_string(self)`

Build PostgreSQL connection string

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create database configuration interface

**Parameters:**

- `self`

---

##### `create_new_database(self)`

Create a new empty database

**Parameters:**

- `self`

---

##### `create_sample_database(self)`

Create sample database

**Parameters:**

- `self`

---

##### `import_database(self)`

Import database from file

**Parameters:**

- `self`

---

##### `ok(self)`

Connect to selected database

**Parameters:**

- `self`

---

##### `on_db_type_change(self)`

Handle database type change

**Parameters:**

- `self`

---

##### `test_connection(self)`

Test PostgreSQL connection

**Parameters:**

- `self`

---

##### `use_sample_database(self)`

Use the sample database

**Parameters:**

- `self`

---


#### `HarrisMatrixDialog`

Dialog for generating and viewing Harris Matrix

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, matrix_generator, matrix_visualizer, sites)`

Initializes a new instance of the class, setting up the necessary fields and user interface components for inventory data entry. This method also prepares the form for creating a new inventory item or updating an existing one, depending on whether inventory data is provided. It ensures that all input fields are properly configured and linked to the underlying inventory management service.

**Parameters:**

- `self`
- `parent`
- `matrix_generator`
- `matrix_visualizer`
- `sites`

---

##### `create_interface(self)`

Create Harris Matrix interface

**Parameters:**

- `self`

---

##### `display_levels(self)`

Display matrix levels

**Parameters:**

- `self`

---

##### `display_statistics(self, stats)`

Display matrix statistics

**Parameters:**

- `self`
- `stats`

---

##### `export_matrix(self)`

Export Harris Matrix to files

**Parameters:**

- `self`

---

##### `generate_matrix(self)`

Generate Harris Matrix for selected site

**Parameters:**

- `self`

---

##### `open_advanced_editor(self)`

Open advanced Harris Matrix editor

**Parameters:**

- `self`

---


#### `HarrisMatrixDialog`

Dialog for generating and viewing Harris Matrix

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, matrix_generator, matrix_visualizer, sites, site_service, us_service, db_manager)`

Initializes a new instance of the **HarrisMatrixDialog** class, setting up the dialog window for generating and viewing a Harris Matrix. This method assigns the provided matrix generator, matrix visualizer, list of sites, and optional services to instance variables, then constructs the user interface and customizes the dialog buttons to display only a "Close" option.

**Parameters:**

- `self`
- `parent`
- `matrix_generator`
- `matrix_visualizer`
- `sites`
- `site_service`
- `us_service`
- `db_manager`

---

##### `create_interface(self)`

Create Harris Matrix interface

**Parameters:**

- `self`

---

##### `display_levels(self)`

Display matrix levels

**Parameters:**

- `self`

---

##### `display_statistics(self, stats)`

Display matrix statistics

**Parameters:**

- `self`
- `stats`

---

##### `export_matrix(self)`

Export Harris Matrix to files

**Parameters:**

- `self`

---

##### `generate_matrix(self)`

Generate Harris Matrix for selected site

**Parameters:**

- `self`

---

##### `open_advanced_editor(self)`

Open advanced Harris Matrix editor

**Parameters:**

- `self`

---


#### `HarrisMatrixDialog`

Dialog for generating and viewing Harris Matrix

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, matrix_generator, matrix_visualizer, sites, site_service, us_service, db_manager)`

Initializes a new instance of the **HarrisMatrixDialog** class. This constructor sets up the dialog window with the provided matrix generator, matrix visualizer, list of sites, and optional service and database manager dependencies. It also configures the user interface and customizes the dialog buttons to display only a "Close" option.

**Parameters:**

- `self`
- `parent`
- `matrix_generator`
- `matrix_visualizer`
- `sites`
- `site_service`
- `us_service`
- `db_manager`

---

##### `create_interface(self)`

Create Harris Matrix interface

**Parameters:**

- `self`

---

##### `display_levels(self)`

Display matrix levels

**Parameters:**

- `self`

---

##### `display_statistics(self, stats)`

Display matrix statistics

**Parameters:**

- `self`
- `stats`

---

##### `export_matrix(self)`

Export Harris Matrix to files

**Parameters:**

- `self`

---

##### `generate_matrix(self)`

Generate Harris Matrix for selected site

**Parameters:**

- `self`

---

##### `on_button_press(self, event)`

Handle mouse button press for pan

**Parameters:**

- `self`
- `event`

---

##### `on_button_release(self, event)`

Handle mouse button release

**Parameters:**

- `self`
- `event`

---

##### `on_layout_changed(self, event)`

Handle layout option change

**Parameters:**

- `self`
- `event`

---

##### `on_mouse_move(self, event)`

Handle mouse movement for pan

**Parameters:**

- `self`
- `event`

---

##### `on_scroll(self, event)`

Handle mouse wheel zoom

**Parameters:**

- `self`
- `event`

---

##### `open_advanced_editor(self)`

Open advanced Harris Matrix editor

**Parameters:**

- `self`

---

##### `visualize_matrix(self)`

Visualize Harris Matrix using PyArchInit-style Graphviz

**Parameters:**

- `self`

---

##### `zoom_fit(self)`

Fit matrix to window

**Parameters:**

- `self`

---

##### `zoom_in(self)`

Zoom in on the matrix

**Parameters:**

- `self`

---

##### `zoom_out(self)`

Zoom out on the matrix

**Parameters:**

- `self`

---


#### `InventarioDialog`

Dialog for creating/editing inventory items

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, inventario_service, site_names, inventario, callback)`

Initializes the form by setting up the data fields and populating them with existing values if an "US" (Unità Stratigrafica) instance is provided. It prepares the form for either creating a new US record or updating an existing one, ensuring proper handling and validation of input fields.

**Parameters:**

- `self`
- `parent`
- `inventario_service`
- `site_names`
- `inventario`
- `callback`

---

##### `create_form(self)`

Create inventory form

**Parameters:**

- `self`

---

##### `ok(self)`

Save inventory data

**Parameters:**

- `self`

---

##### `populate_form(self)`

Populate form with existing inventory data

**Parameters:**

- `self`

---


#### `InventarioDialog`

Dialog for creating/editing inventory items

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, inventario_service, site_names, inventario, callback)`

Initializes a new instance of the **InventarioDialog** class for creating or editing inventory items.  
This method sets up the dialog window, initializes its attributes with the provided inventory service, site names, existing inventory item (if any), and callback function, and creates the input form and action buttons. If an existing inventory item is provided, the form is pre-populated with its data.

**Parameters:**

- `self`
- `parent`
- `inventario_service`
- `site_names`
- `inventario`
- `callback`

---

##### `create_form(self)`

Create inventory form

**Parameters:**

- `self`

---

##### `ok(self)`

Save inventory data

**Parameters:**

- `self`

---

##### `populate_form(self)`

Populate form with existing inventory data

**Parameters:**

- `self`

---


#### `InventarioDialog`

Dialog for creating/editing inventory items

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, inventario_service, site_names, inventario, callback)`

Initializes a new instance of the **InventarioDialog** class, setting up the dialog window for creating or editing inventory items. It configures the dialog title, dimensions, and fields based on whether an existing inventory item is provided, initializes necessary services and callbacks, and prepares the form and action buttons. If an inventory item is supplied, the form is pre-populated with its data.

**Parameters:**

- `self`
- `parent`
- `inventario_service`
- `site_names`
- `inventario`
- `callback`

---

##### `create_form(self)`

Create inventory form

**Parameters:**

- `self`

---

##### `ok(self)`

Save inventory data

**Parameters:**

- `self`

---

##### `populate_form(self)`

Populate form with existing inventory data

**Parameters:**

- `self`

---


#### `MediaManagerDialog`

Dialog for media management

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, media_handler)`

Initializes the class by setting up the required service dependencies and a list of available sites. It also constructs the user interface for PDF export by invoking methods to create the interface elements and action buttons.

**Parameters:**

- `self`
- `parent`
- `media_handler`

---

##### `create_interface(self)`

Create media management interface

**Parameters:**

- `self`

---

##### `select_file(self)`

Select file to upload

**Parameters:**

- `self`

---

##### `upload_file(self)`

Upload selected file

**Parameters:**

- `self`

---


#### `MediaManagerDialog`

Dialog for media management

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, media_handler)`

Initializes the class instance and prepares the necessary data structures for handling inventory records. This method extracts relevant attributes from inventory objects, assembles them into dictionaries, and manages the generation and saving of inventory PDF reports. It also provides user feedback upon successful completion of the PDF generation process.

**Parameters:**

- `self`
- `parent`
- `media_handler`

---

##### `create_interface(self)`

Create media management interface

**Parameters:**

- `self`

---

##### `select_file(self)`

Select file to upload

**Parameters:**

- `self`

---

##### `upload_file(self)`

Upload selected file

**Parameters:**

- `self`

---


#### `MediaManagerDialog`

Dialog for media management

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, media_handler)`

**__init__(self, parent, media_handler):**  
Initializes a new instance of the `MediaManagerDialog` class, setting up the dialog window for media management. It configures the dialog's title, size, and associates it with the provided media handler, then creates the user interface and customizes the dialog buttons to display only the "Close" option.

**Parameters:**

- `self`
- `parent`
- `media_handler`

---

##### `create_interface(self)`

Create media management interface

**Parameters:**

- `self`

---

##### `select_file(self)`

Select file to upload

**Parameters:**

- `self`

---

##### `upload_file(self)`

Upload selected file

**Parameters:**

- `self`

---


#### `PDFExportDialog`

Dialog for PDF export

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, pdf_generator, site_service, us_service, inventario_service, sites)`

Initializes the object by setting the current site, displaying matrix statistics and levels, and visualizing the matrix. Upon successful completion, it shows a confirmation message; if an error occurs during the process, it displays an error message. This method ensures that the UI is updated with the latest matrix information for the selected site.

**Parameters:**

- `self`
- `parent`
- `pdf_generator`
- `site_service`
- `us_service`
- `inventario_service`
- `sites`

---

##### `create_interface(self)`

Create PDF export interface

**Parameters:**

- `self`

---

##### `ok(self)`

Generate PDF report

**Parameters:**

- `self`

---

##### `select_output_file(self)`

Select output file

**Parameters:**

- `self`

---


#### `PDFExportDialog`

Dialog for PDF export

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, pdf_generator, site_service, us_service, inventario_service, sites)`

Initializes the visualizer for the Harris Matrix using PyArchInit-style rendering. This method retrieves the current layout setting, configures visualization parameters for optimal readability, and generates a high-resolution matrix image, saving the output to a temporary file. The path to the generated image is stored for further use.

**Parameters:**

- `self`
- `parent`
- `pdf_generator`
- `site_service`
- `us_service`
- `inventario_service`
- `sites`

---

##### `create_interface(self)`

Create PDF export interface

**Parameters:**

- `self`

---

##### `ok(self)`

Generate PDF report

**Parameters:**

- `self`

---

##### `select_output_file(self)`

Select output file

**Parameters:**

- `self`

---


#### `PDFExportDialog`

Dialog for PDF export

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, pdf_generator, site_service, us_service, inventario_service, sites)`

Initializes a new instance of the **PDFExportDialog** class. This constructor sets up the dialog window for exporting PDFs by initializing required services and data, and creates the user interface and dialog buttons. It requires references to the parent window, a PDF generator, various service objects, and a list of available sites.

**Parameters:**

- `self`
- `parent`
- `pdf_generator`
- `site_service`
- `us_service`
- `inventario_service`
- `sites`

---

##### `create_interface(self)`

Create PDF export interface

**Parameters:**

- `self`

---

##### `ok(self)`

Generate PDF report

**Parameters:**

- `self`

---

##### `select_output_file(self)`

Select output file

**Parameters:**

- `self`

---


#### `SiteDialog`

Dialog for creating/editing sites with media support

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, site_service, media_service, site, callback)`

Initializes a new instance of the **SiteDialog** class for creating or editing a site, with optional media support. It sets up the dialog window, initializes services and site data, creates the media directory, and constructs the form and action buttons. If an existing site is provided, the form is pre-populated and associated media are loaded.

**Parameters:**

- `self`
- `parent`
- `site_service`
- `media_service`
- `site`
- `callback`

---

##### `add_media_file(self, event)`

Add media file with file dialog

**Parameters:**

- `self`
- `event`

---

##### `create_basic_tab(self)`

Create basic information tab

**Parameters:**

- `self`

---

##### `create_description_tab(self)`

Create description tab

**Parameters:**

- `self`

---

##### `create_form(self)`

Create site form with tabs

**Parameters:**

- `self`

---

##### `create_media_directory(self)`

Create media directory for the site

**Parameters:**

- `self`

---

##### `create_media_tab(self)`

Create media management tab with thumbnails and drag & drop

**Parameters:**

- `self`

---

##### `format_file_size(self, size_bytes)`

Format file size in human readable format

**Parameters:**

- `self`
- `size_bytes`

---

##### `load_media(self)`

Load existing media files for the site

**Parameters:**

- `self`

---

##### `ok(self)`

Save site data

**Parameters:**

- `self`

---

##### `on_media_select(self, event)`

Handle media selection

**Parameters:**

- `self`
- `event`

---

##### `populate_form(self)`

Populate form with existing site data

**Parameters:**

- `self`

---

##### `preview_media(self)`

Preview selected media file

**Parameters:**

- `self`

---

##### `process_media_file(self, file_path)`

Process and add media file to the list

**Parameters:**

- `self`
- `file_path`

---

##### `refresh_media_list(self)`

Refresh the media list display

**Parameters:**

- `self`

---

##### `remove_media_file(self)`

Remove selected media file

**Parameters:**

- `self`

---


#### `SiteDialog`

Dialog for creating/editing sites with media support

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, site_service, media_service, site, callback)`

Initializes a new instance of the **SiteDialog** class, setting up the dialog window for creating or editing a site, with optional media support. This method configures the dialog's title, associates the required services, initializes form elements and buttons, and, if editing an existing site, pre-populates the form and loads associated media.

**Parameters:**

- `self`
- `parent`
- `site_service`
- `media_service`
- `site`
- `callback`

---

##### `add_media_file(self, event)`

Add media file with file dialog

**Parameters:**

- `self`
- `event`

---

##### `create_basic_tab(self)`

Create basic information tab

**Parameters:**

- `self`

---

##### `create_description_tab(self)`

Create description tab

**Parameters:**

- `self`

---

##### `create_form(self)`

Create site form with tabs

**Parameters:**

- `self`

---

##### `create_media_directory(self)`

Create media directory for the site

**Parameters:**

- `self`

---

##### `create_media_tab(self)`

Create media management tab with thumbnails and drag & drop

**Parameters:**

- `self`

---

##### `format_file_size(self, size_bytes)`

Format file size in human readable format

**Parameters:**

- `self`
- `size_bytes`

---

##### `load_media(self)`

Load existing media files for the site

**Parameters:**

- `self`

---

##### `ok(self)`

Save site data

**Parameters:**

- `self`

---

##### `on_media_select(self, event)`

Handle media selection

**Parameters:**

- `self`
- `event`

---

##### `populate_form(self)`

Populate form with existing site data

**Parameters:**

- `self`

---

##### `preview_media(self)`

Preview selected media file

**Parameters:**

- `self`

---

##### `process_media_file(self, file_path)`

Process and add media file to the list

**Parameters:**

- `self`
- `file_path`

---

##### `refresh_media_list(self)`

Refresh the media list display

**Parameters:**

- `self`

---

##### `remove_media_file(self)`

Remove selected media file

**Parameters:**

- `self`

---


#### `SiteDialog`

Dialog for creating/editing sites with media support

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, site_service, media_service, site, callback)`

Initializes a new instance of the **SiteDialog** class for creating or editing a site, optionally with media support. This method sets up the dialog window, initializes service references, prepares the media directory, and populates the form and media list if an existing site is provided. It also configures the dialog's form fields and action buttons.

**Parameters:**

- `self`
- `parent`
- `site_service`
- `media_service`
- `site`
- `callback`

---

##### `add_media_file(self, event)`

Add media file with file dialog

**Parameters:**

- `self`
- `event`

---

##### `create_basic_tab(self)`

Create basic information tab

**Parameters:**

- `self`

---

##### `create_description_tab(self)`

Create description tab

**Parameters:**

- `self`

---

##### `create_form(self)`

Create site form with tabs

**Parameters:**

- `self`

---

##### `create_media_directory(self)`

Create media directory for the site

**Parameters:**

- `self`

---

##### `create_media_tab(self)`

Create media management tab with thumbnails and drag & drop

**Parameters:**

- `self`

---

##### `format_file_size(self, size_bytes)`

Format file size in human readable format

**Parameters:**

- `self`
- `size_bytes`

---

##### `load_media(self)`

Load existing media files for the site

**Parameters:**

- `self`

---

##### `ok(self)`

Save site data

**Parameters:**

- `self`

---

##### `on_media_select(self, event)`

Handle media selection

**Parameters:**

- `self`
- `event`

---

##### `populate_form(self)`

Populate form with existing site data

**Parameters:**

- `self`

---

##### `preview_media(self)`

Preview selected media file

**Parameters:**

- `self`

---

##### `process_media_file(self, file_path)`

Process and add media file to the list

**Parameters:**

- `self`
- `file_path`

---

##### `refresh_media_list(self)`

Refresh the media list display

**Parameters:**

- `self`

---

##### `remove_media_file(self)`

Remove selected media file

**Parameters:**

- `self`

---


#### `StatisticsDialog`

Dialog for viewing statistics

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, site_service, us_service, inventario_service)`

Initializes the object by processing a list of inventory items related to a specific site. If no items are found for the given site, it displays a warning message to the user. Otherwise, it converts each inventory item into a dictionary format, ensuring all relevant attributes are included for further use.

**Parameters:**

- `self`
- `parent`
- `site_service`
- `us_service`
- `inventario_service`

---

##### `create_interface(self)`

Create statistics interface

**Parameters:**

- `self`

---

##### `load_statistics(self)`

Load and display statistics

**Parameters:**

- `self`

---


#### `StatisticsDialog`

Dialog for viewing statistics

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, site_service, us_service, inventario_service)`

Initializes the user interface components for configuring PostgreSQL database connections within the application. This method creates and arranges input fields for host, port, and database name, assigning default values and organizing them within a labeled frame for easy user access. It also sets up an "Import Database" button to facilitate database import operations.

**Parameters:**

- `self`
- `parent`
- `site_service`
- `us_service`
- `inventario_service`

---

##### `create_interface(self)`

Create statistics interface

**Parameters:**

- `self`

---

##### `load_statistics(self)`

Load and display statistics

**Parameters:**

- `self`

---


#### `StatisticsDialog`

Dialog for viewing statistics

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, site_service, us_service, inventario_service)`

Initializes a new instance of the StatisticsDialog class.  
This method sets up the dialog window with the provided parent and service objects, creates the user interface components, configures the dialog buttons to only display "Chiudi" (Close), and loads the initial statistics into the interface.

**Parameters:**

- `self`
- `parent`
- `site_service`
- `us_service`
- `inventario_service`

---

##### `create_interface(self)`

Create statistics interface

**Parameters:**

- `self`

---

##### `load_statistics(self)`

Load and display statistics

**Parameters:**

- `self`

---


#### `USDialog`

Dialog for creating/editing US

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, us_service, site_names, us, callback)`

Initializes the form for creating or editing a site, setting up the necessary UI fields and internal variables. If an existing site is provided, it prepares the form with the site's current data for editing; otherwise, it initializes the form for creating a new site. This method also configures the connections to the site service for handling data retrieval and submission.

**Parameters:**

- `self`
- `parent`
- `us_service`
- `site_names`
- `us`
- `callback`

---

##### `create_form(self)`

Create US form

**Parameters:**

- `self`

---

##### `ok(self)`

Save US data

**Parameters:**

- `self`

---

##### `populate_form(self)`

Populate form with existing US data

**Parameters:**

- `self`

---


#### `USDialog`

Dialog for creating/editing US

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, us_service, site_names, us, callback)`

Initializes a new instance of the **USDialog** class for creating or editing a US (Unità Stratigrafica). Sets up the dialog window with form fields, action buttons, and optionally populates the form with existing US data if provided. Also stores references to the US service, site names, and an optional callback for further processing.

**Parameters:**

- `self`
- `parent`
- `us_service`
- `site_names`
- `us`
- `callback`

---

##### `create_form(self)`

Create US form

**Parameters:**

- `self`

---

##### `ok(self)`

Save US data

**Parameters:**

- `self`

---

##### `populate_form(self)`

Populate form with existing US data

**Parameters:**

- `self`

---


#### `USDialog`

Dialog for creating/editing US

**Inherits from:** `BaseDialog`

**Methods:**

##### `__init__(self, parent, us_service, site_names, us, callback)`

Initializes a new instance of the USDialog class for creating or editing a "US" entity. Sets up the dialog window with the appropriate title and size, stores provided services and data, and creates the form and action buttons. If an existing "US" is provided, the form is pre-populated with its data.

**Parameters:**

- `self`
- `parent`
- `us_service`
- `site_names`
- `us`
- `callback`

---

##### `create_form(self)`

Create US form

**Parameters:**

- `self`

---

##### `ok(self)`

Save US data

**Parameters:**

- `self`

---

##### `populate_form(self)`

Populate form with existing US data

**Parameters:**

- `self`

---


### Functions

#### `get_attr(obj, attr_name, default)`

The **`get_attr`** function is a helper designed to retrieve an attribute value from an object, which can be either a dictionary or a data transfer object (DTO). It attempts to access the specified attribute using `getattr` if present, or falls back to the `get` method if the object is a dictionary, returning a default value if the attribute is not found or is falsy. This ensures flexible and safe attribute access across different object types.

**Parameters:**

- `obj`
- `attr_name`
- `default`

---

#### `get_attr(obj, attr_name, default)`

The `get_attr` function is a utility that retrieves the value of a specified attribute from an object, supporting both standard Python objects (using attribute access) and dictionary-like objects (using key access). If the attribute or key does not exist, or if the retrieved value is falsy, it returns a provided default value (empty string by default). This ensures flexible and safe extraction of data from heterogeneous objects.

**Parameters:**

- `obj`
- `attr_name`
- `default`

---


\newpage


## Module: `desktop_gui/gui_app.py`

**File Path:** `desktop_gui/gui_app.py`

### Functions

#### `check_dependencies()`

Check if all required dependencies are available

---

#### `check_dependencies()`

Check if all required dependencies are available

---

#### `check_dependencies()`

Check if all required dependencies are available

---

#### `main()`

Main application entry point

---

#### `main()`

Main application entry point

---

#### `main()`

Main application entry point

---


\newpage


## Module: `desktop_gui/harris_matrix_editor.py`

**File Path:** `desktop_gui/harris_matrix_editor.py`

### Classes

#### `HarrisMatrixEditor`

Advanced Harris Matrix editor with relationship management and validation

**Methods:**

##### `__init__(self, parent, matrix_generator, matrix_visualizer, site_service, us_service)`

Initializes a new instance of the Advanced Harris Matrix editor, setting up the main window, interface components, and required services for matrix generation, visualization, and site/unit management. This constructor also initializes data structures for managing current site, area, relationships, and the underlying graph, and makes the editor window modal relative to the parent.

**Parameters:**

- `self`
- `parent`
- `matrix_generator`
- `matrix_visualizer`
- `site_service`
- `us_service`

---

##### `add_relationship(self)`

Add new stratigraphic relationship

**Parameters:**

- `self`

---

##### `auto_fix_matrix(self)`

Attempt automatic fixes for matrix issues

**Parameters:**

- `self`

---

##### `create_control_panel(self, parent)`

Create site selection and main controls

**Parameters:**

- `self`
- `parent`

---

##### `create_interface(self)`

Create the main interface

**Parameters:**

- `self`

---

##### `create_left_panel(self, parent)`

Create left panel with relationships and tools

**Parameters:**

- `self`
- `parent`

---

##### `create_relationships_tab(self, parent)`

Create relationships management tab

**Parameters:**

- `self`
- `parent`

---

##### `create_right_panel(self, parent)`

Create right panel with matrix visualization

**Parameters:**

- `self`
- `parent`

---

##### `create_us_list_tab(self, parent)`

Create US list tab

**Parameters:**

- `self`
- `parent`

---

##### `create_validation_tab(self, parent)`

Create validation tab

**Parameters:**

- `self`
- `parent`

---

##### `delete_relationship(self)`

Delete selected relationship

**Parameters:**

- `self`

---

##### `edit_relationship(self)`

Edit selected relationship

**Parameters:**

- `self`

---

##### `export_matrix_image(self)`

Export matrix as image

**Parameters:**

- `self`

---

##### `export_validation_report(self)`

Export validation report

**Parameters:**

- `self`

---

##### `generate_matrix(self)`

Generate new matrix from relationships

**Parameters:**

- `self`

---

##### `highlight_us_in_matrix(self)`

Highlight selected US in matrix

**Parameters:**

- `self`

---

##### `load_areas(self)`

Load areas for selected site

**Parameters:**

- `self`

---

##### `load_matrix(self)`

Load existing matrix for the site

**Parameters:**

- `self`

---

##### `load_sites(self)`

Load available sites

**Parameters:**

- `self`

---

##### `load_us_list(self)`

Load US list for selected site/area

**Parameters:**

- `self`

---

##### `on_area_changed(self, event)`

Handle area selection change

**Parameters:**

- `self`
- `event`

---

##### `on_layout_changed(self, event)`

Handle layout change

**Parameters:**

- `self`
- `event`

---

##### `on_site_changed(self, event)`

Handle site selection change

**Parameters:**

- `self`
- `event`

---

##### `refresh_relationships(self)`

Refresh relationships list

**Parameters:**

- `self`

---

##### `reset_view(self)`

Reset matrix view

**Parameters:**

- `self`

---

##### `save_matrix(self)`

Save current matrix

**Parameters:**

- `self`

---

##### `select_us_for_relation(self)`

Select US from list for relationship creation

**Parameters:**

- `self`

---

##### `validate_matrix(self)`

Validate current matrix

**Parameters:**

- `self`

---

##### `visualize_matrix(self)`

Visualize the Harris Matrix

**Parameters:**

- `self`

---

##### `zoom_in(self)`

Zoom in the matrix view

**Parameters:**

- `self`

---

##### `zoom_out(self)`

Zoom out the matrix view

**Parameters:**

- `self`

---


#### `HarrisMatrixEditor`

Advanced Harris Matrix editor with relationship management and validation

**Methods:**

##### `__init__(self, parent, matrix_generator, matrix_visualizer, site_service, us_service)`

Initializes a new instance of the Advanced Harris Matrix editor, setting up the main window, user interface, and essential services for matrix generation, visualization, and site/unit management. This constructor configures the application's state, loads initial site data, and ensures the editor window operates as a modal dialog relative to its parent.

**Parameters:**

- `self`
- `parent`
- `matrix_generator`
- `matrix_visualizer`
- `site_service`
- `us_service`

---

##### `add_relationship(self)`

Add new stratigraphic relationship

**Parameters:**

- `self`

---

##### `auto_fix_matrix(self)`

Attempt automatic fixes for matrix issues

**Parameters:**

- `self`

---

##### `create_control_panel(self, parent)`

Create site selection and main controls

**Parameters:**

- `self`
- `parent`

---

##### `create_interface(self)`

Create the main interface

**Parameters:**

- `self`

---

##### `create_left_panel(self, parent)`

Create left panel with relationships and tools

**Parameters:**

- `self`
- `parent`

---

##### `create_relationships_tab(self, parent)`

Create relationships management tab

**Parameters:**

- `self`
- `parent`

---

##### `create_right_panel(self, parent)`

Create right panel with matrix visualization

**Parameters:**

- `self`
- `parent`

---

##### `create_us_list_tab(self, parent)`

Create US list tab

**Parameters:**

- `self`
- `parent`

---

##### `create_validation_tab(self, parent)`

Create validation tab

**Parameters:**

- `self`
- `parent`

---

##### `delete_relationship(self)`

Delete selected relationship

**Parameters:**

- `self`

---

##### `edit_relationship(self)`

Edit selected relationship

**Parameters:**

- `self`

---

##### `export_matrix_image(self)`

Export matrix as image

**Parameters:**

- `self`

---

##### `export_validation_report(self)`

Export validation report

**Parameters:**

- `self`

---

##### `generate_matrix(self)`

Generate new matrix from relationships

**Parameters:**

- `self`

---

##### `highlight_us_in_matrix(self)`

Highlight selected US in matrix

**Parameters:**

- `self`

---

##### `load_areas(self)`

Load areas for selected site

**Parameters:**

- `self`

---

##### `load_matrix(self)`

Load existing matrix for the site

**Parameters:**

- `self`

---

##### `load_sites(self)`

Load available sites

**Parameters:**

- `self`

---

##### `load_us_list(self)`

Load US list for selected site/area

**Parameters:**

- `self`

---

##### `on_area_changed(self, event)`

Handle area selection change

**Parameters:**

- `self`
- `event`

---

##### `on_layout_changed(self, event)`

Handle layout change

**Parameters:**

- `self`
- `event`

---

##### `on_site_changed(self, event)`

Handle site selection change

**Parameters:**

- `self`
- `event`

---

##### `refresh_relationships(self)`

Refresh relationships list

**Parameters:**

- `self`

---

##### `reset_view(self)`

Reset matrix view

**Parameters:**

- `self`

---

##### `save_matrix(self)`

Save current matrix

**Parameters:**

- `self`

---

##### `select_us_for_relation(self)`

Select US from list for relationship creation

**Parameters:**

- `self`

---

##### `validate_matrix(self)`

Validate current matrix

**Parameters:**

- `self`

---

##### `visualize_matrix(self)`

Visualize the Harris Matrix

**Parameters:**

- `self`

---

##### `zoom_in(self)`

Zoom in the matrix view

**Parameters:**

- `self`

---

##### `zoom_out(self)`

Zoom out the matrix view

**Parameters:**

- `self`

---


#### `HarrisMatrixEditor`

Advanced Harris Matrix editor with relationship management and validation

**Methods:**

##### `__init__(self, parent, matrix_generator, matrix_visualizer, site_service, us_service)`

Initializes a new instance of the Advanced Harris Matrix editor, setting up required services, data structures, and the main application window. This method configures the editor’s interface, loads initial site data, and ensures the window operates modally relative to its parent. It prepares the editor for managing and visualizing Harris Matrix relationships.

**Parameters:**

- `self`
- `parent`
- `matrix_generator`
- `matrix_visualizer`
- `site_service`
- `us_service`

---

##### `add_relationship(self)`

Add new stratigraphic relationship

**Parameters:**

- `self`

---

##### `auto_fix_matrix(self)`

Attempt automatic fixes for matrix issues

**Parameters:**

- `self`

---

##### `create_control_panel(self, parent)`

Create site selection and main controls

**Parameters:**

- `self`
- `parent`

---

##### `create_interface(self)`

Create the main interface

**Parameters:**

- `self`

---

##### `create_left_panel(self, parent)`

Create left panel with relationships and tools

**Parameters:**

- `self`
- `parent`

---

##### `create_relationships_tab(self, parent)`

Create relationships management tab

**Parameters:**

- `self`
- `parent`

---

##### `create_right_panel(self, parent)`

Create right panel with matrix visualization

**Parameters:**

- `self`
- `parent`

---

##### `create_us_list_tab(self, parent)`

Create US list tab

**Parameters:**

- `self`
- `parent`

---

##### `create_validation_tab(self, parent)`

Create validation tab

**Parameters:**

- `self`
- `parent`

---

##### `delete_relationship(self)`

Delete selected relationship

**Parameters:**

- `self`

---

##### `edit_relationship(self)`

Edit selected relationship

**Parameters:**

- `self`

---

##### `export_matrix_image(self)`

Export matrix as image

**Parameters:**

- `self`

---

##### `export_validation_report(self)`

Export validation report

**Parameters:**

- `self`

---

##### `generate_matrix(self)`

Generate new matrix from relationships

**Parameters:**

- `self`

---

##### `highlight_us_in_matrix(self)`

Highlight selected US in matrix

**Parameters:**

- `self`

---

##### `load_areas(self)`

Load areas for selected site

**Parameters:**

- `self`

---

##### `load_matrix(self)`

Load existing matrix for the site

**Parameters:**

- `self`

---

##### `load_sites(self)`

Load available sites

**Parameters:**

- `self`

---

##### `load_us_list(self)`

Load US list for selected site/area

**Parameters:**

- `self`

---

##### `on_area_changed(self, event)`

Handle area selection change

**Parameters:**

- `self`
- `event`

---

##### `on_layout_changed(self, event)`

Handle layout change

**Parameters:**

- `self`
- `event`

---

##### `on_site_changed(self, event)`

Handle site selection change

**Parameters:**

- `self`
- `event`

---

##### `refresh_relationships(self)`

Refresh relationships list

**Parameters:**

- `self`

---

##### `reset_view(self)`

Reset matrix view

**Parameters:**

- `self`

---

##### `save_matrix(self)`

Save current matrix

**Parameters:**

- `self`

---

##### `select_us_for_relation(self)`

Select US from list for relationship creation

**Parameters:**

- `self`

---

##### `validate_matrix(self)`

Validate current matrix

**Parameters:**

- `self`

---

##### `visualize_matrix(self)`

Visualize the Harris Matrix using PyArchInit-style Graphviz

**Parameters:**

- `self`

---

##### `zoom_in(self)`

Zoom in the matrix view

**Parameters:**

- `self`

---

##### `zoom_out(self)`

Zoom out the matrix view

**Parameters:**

- `self`

---


### Functions

#### `save_changes()`

The `save_changes` function updates a relationship between two nodes in a graph based on user input from a GUI form. It removes the old edge, adds a new edge with the specified type, refreshes the interface to reflect the changes, and displays a success or error message as appropriate.

---


\newpage


## Module: `desktop_gui/inventario_dialog_extended.py`

**File Path:** `desktop_gui/inventario_dialog_extended.py`

### Classes

#### `ExtendedInventarioDialog`

Extended Inventory Dialog with all fields from PyArchInit plugin
Includes media management and thesaurus integration

**Methods:**

##### `__init__(self, parent, inventario_service, site_service, thesaurus_service, media_service, inventario, callback)`

Initializes the Extended Inventory Dialog, setting up the user interface with all relevant inventory fields from the PyArchInit plugin, including media management and thesaurus integration. Configures dialog properties, creates and arranges all UI tabs, and loads existing inventory data and associated media if provided. This method establishes all necessary services and prepares the dialog for user interaction.

**Parameters:**

- `self`
- `parent`
- `inventario_service`
- `site_service`
- `thesaurus_service`
- `media_service`
- `inventario`
- `callback`

---

##### `add_media_file(self, event)`

Add media file with file dialog

**Parameters:**

- `self`
- `event`

---

##### `cancel(self)`

Cancel and close dialog

**Parameters:**

- `self`

---

##### `center_window(self)`

Center dialog window on parent

**Parameters:**

- `self`

---

##### `create_ceramic_tab(self)`

Create ceramic-specific fields tab

**Parameters:**

- `self`

---

##### `create_classification_tab(self)`

Create classification tab

**Parameters:**

- `self`

---

##### `create_conservation_tab(self)`

Create conservation tab

**Parameters:**

- `self`

---

##### `create_context_tab(self)`

Create context tab

**Parameters:**

- `self`

---

##### `create_documentation_tab(self)`

Create documentation tab

**Parameters:**

- `self`

---

##### `create_identification_tab(self)`

Create identification and basic info tab

**Parameters:**

- `self`

---

##### `create_measurements_tab(self)`

Create measurements and dating tab

**Parameters:**

- `self`

---

##### `create_media_directory(self)`

Create media directory for the inventory item

**Parameters:**

- `self`

---

##### `create_media_tab(self)`

Create media management tab

**Parameters:**

- `self`

---

##### `create_physical_tab(self)`

Create physical characteristics tab

**Parameters:**

- `self`

---

##### `format_file_size(self, size_bytes)`

Format file size in human readable format

**Parameters:**

- `self`
- `size_bytes`

---

##### `get_entry_field_value(self, field_name)`

Get value from Entry or Combobox widget

**Parameters:**

- `self`
- `field_name`

---

##### `get_text_field_value(self, field_name)`

Get value from Text widget

**Parameters:**

- `self`
- `field_name`

---

##### `get_thesaurus_values(self, field_name: str) → List[str]`

Get thesaurus values for a field

**Parameters:**

- `self`
- `field_name` (str)

**Returns:** `List[str]`

---

##### `load_media(self)`

Load existing media files for the inventory item

**Parameters:**

- `self`

---

##### `on_media_select(self, event)`

Handle media selection

**Parameters:**

- `self`
- `event`

---

##### `populate_form(self)`

Populate form with existing inventory data

**Parameters:**

- `self`

---

##### `preview_media(self)`

Preview selected media file

**Parameters:**

- `self`

---

##### `process_media_file(self, file_path)`

Process and add media file to the list

**Parameters:**

- `self`
- `file_path`

---

##### `refresh_media_list(self)`

Refresh the media list display

**Parameters:**

- `self`

---

##### `remove_media_file(self)`

Remove selected media file

**Parameters:**

- `self`

---

##### `save(self)`

Save inventory data

**Parameters:**

- `self`

---


#### `ExtendedInventarioDialog`

Extended Inventory Dialog with all fields from PyArchInit plugin
Includes media management and thesaurus integration

**Methods:**

##### `__init__(self, parent, inventario_service, site_service, thesaurus_service, media_service, inventario, callback)`

Initializes the Extended Inventory Dialog, setting up all user interface components and services required for managing inventory records, including media and thesaurus integration. Configures dialog properties, creates form tabs for all relevant data fields, and loads existing inventory data and associated media if provided. This method prepares the dialog for both creating new and editing existing inventory entries.

**Parameters:**

- `self`
- `parent`
- `inventario_service`
- `site_service`
- `thesaurus_service`
- `media_service`
- `inventario`
- `callback`

---

##### `add_media_file(self, event)`

Add media file with file dialog

**Parameters:**

- `self`
- `event`

---

##### `cancel(self)`

Cancel and close dialog

**Parameters:**

- `self`

---

##### `center_window(self)`

Center dialog window on parent

**Parameters:**

- `self`

---

##### `create_ceramic_tab(self)`

Create ceramic-specific fields tab

**Parameters:**

- `self`

---

##### `create_classification_tab(self)`

Create classification tab

**Parameters:**

- `self`

---

##### `create_conservation_tab(self)`

Create conservation tab

**Parameters:**

- `self`

---

##### `create_context_tab(self)`

Create context tab

**Parameters:**

- `self`

---

##### `create_documentation_tab(self)`

Create documentation tab

**Parameters:**

- `self`

---

##### `create_identification_tab(self)`

Create identification and basic info tab

**Parameters:**

- `self`

---

##### `create_measurements_tab(self)`

Create measurements and dating tab

**Parameters:**

- `self`

---

##### `create_media_directory(self)`

Create media directory for the inventory item

**Parameters:**

- `self`

---

##### `create_media_tab(self)`

Create media management tab

**Parameters:**

- `self`

---

##### `create_physical_tab(self)`

Create physical characteristics tab

**Parameters:**

- `self`

---

##### `format_file_size(self, size_bytes)`

Format file size in human readable format

**Parameters:**

- `self`
- `size_bytes`

---

##### `get_entry_field_value(self, field_name)`

Get value from Entry or Combobox widget

**Parameters:**

- `self`
- `field_name`

---

##### `get_text_field_value(self, field_name)`

Get value from Text widget

**Parameters:**

- `self`
- `field_name`

---

##### `get_thesaurus_values(self, field_name: str) → List[str]`

Get thesaurus values for a field

**Parameters:**

- `self`
- `field_name` (str)

**Returns:** `List[str]`

---

##### `load_media(self)`

Load existing media files for the inventory item

**Parameters:**

- `self`

---

##### `on_media_select(self, event)`

Handle media selection

**Parameters:**

- `self`
- `event`

---

##### `populate_form(self)`

Populate form with existing inventory data

**Parameters:**

- `self`

---

##### `preview_media(self)`

Preview selected media file

**Parameters:**

- `self`

---

##### `process_media_file(self, file_path)`

Process and add media file to the list

**Parameters:**

- `self`
- `file_path`

---

##### `refresh_media_list(self)`

Refresh the media list display

**Parameters:**

- `self`

---

##### `remove_media_file(self)`

Remove selected media file

**Parameters:**

- `self`

---

##### `save(self)`

Save inventory data

**Parameters:**

- `self`

---


#### `ExtendedInventarioDialog`

Extended Inventory Dialog with all fields from PyArchInit plugin
Includes media management and thesaurus integration

**Methods:**

##### `__init__(self, parent, inventario_service, site_service, thesaurus_service, media_service, inventario, callback)`

Initializes an extended inventory dialog window with all relevant fields from the PyArchInit plugin, including media management and thesaurus integration. Sets up the dialog’s layout, tabs, and controls, and optionally populates the form and associated media if an existing inventory record is provided. This method also configures service dependencies and prepares the dialog for user interaction.

**Parameters:**

- `self`
- `parent`
- `inventario_service`
- `site_service`
- `thesaurus_service`
- `media_service`
- `inventario`
- `callback`

---

##### `add_media_file(self, event)`

Add media file with file dialog

**Parameters:**

- `self`
- `event`

---

##### `cancel(self)`

Cancel and close dialog

**Parameters:**

- `self`

---

##### `center_window(self)`

Center dialog window on parent

**Parameters:**

- `self`

---

##### `create_ceramic_tab(self)`

Create ceramic-specific fields tab

**Parameters:**

- `self`

---

##### `create_classification_tab(self)`

Create classification tab

**Parameters:**

- `self`

---

##### `create_conservation_tab(self)`

Create conservation tab

**Parameters:**

- `self`

---

##### `create_context_tab(self)`

Create context tab

**Parameters:**

- `self`

---

##### `create_documentation_tab(self)`

Create documentation tab

**Parameters:**

- `self`

---

##### `create_identification_tab(self)`

Create identification and basic info tab

**Parameters:**

- `self`

---

##### `create_measurements_tab(self)`

Create measurements and dating tab

**Parameters:**

- `self`

---

##### `create_media_directory(self)`

Create media directory for the inventory item

**Parameters:**

- `self`

---

##### `create_media_tab(self)`

Create media management tab

**Parameters:**

- `self`

---

##### `create_physical_tab(self)`

Create physical characteristics tab

**Parameters:**

- `self`

---

##### `format_file_size(self, size_bytes)`

Format file size in human readable format

**Parameters:**

- `self`
- `size_bytes`

---

##### `get_entry_field_value(self, field_name)`

Get value from Entry or Combobox widget

**Parameters:**

- `self`
- `field_name`

---

##### `get_text_field_value(self, field_name)`

Get value from Text widget

**Parameters:**

- `self`
- `field_name`

---

##### `get_thesaurus_values(self, field_name: str) → List[str]`

Get thesaurus values for a field

**Parameters:**

- `self`
- `field_name` (str)

**Returns:** `List[str]`

---

##### `load_media(self)`

Load existing media files for the inventory item

**Parameters:**

- `self`

---

##### `on_media_select(self, event)`

Handle media selection

**Parameters:**

- `self`
- `event`

---

##### `populate_form(self)`

Populate form with existing inventory data

**Parameters:**

- `self`

---

##### `preview_media(self)`

Preview selected media file

**Parameters:**

- `self`

---

##### `process_media_file(self, file_path)`

Process and add media file to the list

**Parameters:**

- `self`
- `file_path`

---

##### `refresh_media_list(self)`

Refresh the media list display

**Parameters:**

- `self`

---

##### `remove_media_file(self)`

Remove selected media file

**Parameters:**

- `self`

---

##### `save(self)`

Save inventory data

**Parameters:**

- `self`

---



\newpage


## Module: `desktop_gui/main_window.py`

**File Path:** `desktop_gui/main_window.py`

### Classes

#### `PyArchInitGUI`

Main GUI application for PyArchInit-Mini

**Methods:**

##### `__del__(self)`

Cleanup when application closes

**Parameters:**

- `self`

---

##### `__init__(self)`

**__init__**  
Initializes the main window and user interface for the PyArchInit-Mini application. This method sets up the main application window, initializes the database connection and key status variables, applies styles, creates the menu and interface components, and loads the initial data required for the application to function.

**Parameters:**

- `self`

---

##### `create_dashboard_content(self, parent)`

Create dashboard content widgets

**Parameters:**

- `self`
- `parent`

---

##### `create_dashboard_tab(self)`

Create dashboard tab

**Parameters:**

- `self`

---

##### `create_inventario_tab(self)`

Create inventory management tab

**Parameters:**

- `self`

---

##### `create_main_interface(self)`

Create main application interface

**Parameters:**

- `self`

---

##### `create_menu(self)`

Create application menu bar

**Parameters:**

- `self`

---

##### `create_sites_tab(self)`

Create sites management tab

**Parameters:**

- `self`

---

##### `create_status_bar(self, parent)`

Create status bar

**Parameters:**

- `self`
- `parent`

---

##### `create_toolbar(self, parent)`

Create application toolbar

**Parameters:**

- `self`
- `parent`

---

##### `create_us_tab(self)`

Create US management tab

**Parameters:**

- `self`

---

##### `delete_selected_inventario(self)`

Delete selected inventory item

**Parameters:**

- `self`

---

##### `delete_selected_site(self)`

Delete selected site

**Parameters:**

- `self`

---

##### `delete_selected_us(self)`

Delete selected US

**Parameters:**

- `self`

---

##### `edit_selected_inventario(self)`

Edit selected inventory item

**Parameters:**

- `self`

---

##### `edit_selected_site(self)`

Edit selected site

**Parameters:**

- `self`

---

##### `edit_selected_us(self)`

Edit selected US

**Parameters:**

- `self`

---

##### `export_database(self)`

Export database to file

**Parameters:**

- `self`

---

##### `export_pdf_dialog(self)`

Show PDF export dialog

**Parameters:**

- `self`

---

##### `import_database(self)`

Import database from file

**Parameters:**

- `self`

---

##### `new_inventario_dialog(self)`

Show new inventory dialog

**Parameters:**

- `self`

---

##### `new_site_dialog(self)`

Show new site dialog

**Parameters:**

- `self`

---

##### `new_us_dialog(self)`

Show new US dialog

**Parameters:**

- `self`

---

##### `on_inventario_filter_changed(self, event)`

Handle inventory filter change

**Parameters:**

- `self`
- `event`

---

##### `on_site_changed(self, event)`

Handle site selection change

**Parameters:**

- `self`
- `event`

---

##### `on_sites_search(self)`

Handle sites search

**Parameters:**

- `self`

---

##### `on_us_filter_changed(self, event)`

Handle US filter change

**Parameters:**

- `self`
- `event`

---

##### `reconnect_database(self, connection_string)`

Reconnect to database with new connection string

**Parameters:**

- `self`
- `connection_string`

---

##### `refresh_activity_log(self)`

Refresh activity log in dashboard

**Parameters:**

- `self`

---

##### `refresh_dashboard(self)`

Refresh dashboard statistics

**Parameters:**

- `self`

---

##### `refresh_data(self)`

Refresh all data in the interface

**Parameters:**

- `self`

---

##### `refresh_inventario(self)`

Refresh inventory list

**Parameters:**

- `self`

---

##### `refresh_sites(self)`

Refresh sites list

**Parameters:**

- `self`

---

##### `refresh_us(self)`

Refresh US list

**Parameters:**

- `self`

---

##### `run(self)`

Start the application

**Parameters:**

- `self`

---

##### `setup_database(self)`

Initialize database connection and services

**Parameters:**

- `self`

---

##### `setup_styles(self)`

Configure ttk styles

**Parameters:**

- `self`

---

##### `show_about_dialog(self)`

Show about dialog

**Parameters:**

- `self`

---

##### `show_database_config(self)`

Show database configuration dialog

**Parameters:**

- `self`

---

##### `show_harris_matrix_dialog(self)`

Show Harris Matrix dialog

**Parameters:**

- `self`

---

##### `show_help_dialog(self)`

Show help dialog

**Parameters:**

- `self`

---

##### `show_media_manager(self)`

Show media manager dialog

**Parameters:**

- `self`

---

##### `show_media_manager(self)`

Show media manager dialog

**Parameters:**

- `self`

---

##### `show_pdf_export_dialog(self)`

Show PDF export dialog

**Parameters:**

- `self`

---

##### `show_postgres_installer(self)`

Show PostgreSQL installer dialog

**Parameters:**

- `self`

---

##### `show_statistics_dialog(self)`

Show statistics dialog

**Parameters:**

- `self`

---

##### `show_statistics_dialog(self)`

Show statistics dialog

**Parameters:**

- `self`

---

##### `show_tab(self, tab_name)`

Show specific tab

**Parameters:**

- `self`
- `tab_name`

---

##### `show_thesaurus_dialog(self)`

Show thesaurus management dialog

**Parameters:**

- `self`

---


#### `PyArchInitGUI`

Main GUI application for PyArchInit-Mini

**Methods:**

##### `__del__(self)`

Cleanup when application closes

**Parameters:**

- `self`

---

##### `__init__(self)`

Initializes the main window and core components of the PyArchInit-Mini graphical user interface. This method sets up the application window, initializes the database connection and status variables, applies GUI styles, constructs the menu and main interface, and loads the initial data for user interaction.

**Parameters:**

- `self`

---

##### `create_dashboard_content(self, parent)`

Create dashboard content widgets

**Parameters:**

- `self`
- `parent`

---

##### `create_dashboard_tab(self)`

Create dashboard tab

**Parameters:**

- `self`

---

##### `create_inventario_tab(self)`

Create inventory management tab

**Parameters:**

- `self`

---

##### `create_main_interface(self)`

Create main application interface

**Parameters:**

- `self`

---

##### `create_menu(self)`

Create application menu bar

**Parameters:**

- `self`

---

##### `create_sites_tab(self)`

Create sites management tab

**Parameters:**

- `self`

---

##### `create_status_bar(self, parent)`

Create status bar

**Parameters:**

- `self`
- `parent`

---

##### `create_toolbar(self, parent)`

Create application toolbar

**Parameters:**

- `self`
- `parent`

---

##### `create_us_tab(self)`

Create US management tab

**Parameters:**

- `self`

---

##### `delete_selected_inventario(self)`

Delete selected inventory item

**Parameters:**

- `self`

---

##### `delete_selected_site(self)`

Delete selected site

**Parameters:**

- `self`

---

##### `delete_selected_us(self)`

Delete selected US

**Parameters:**

- `self`

---

##### `edit_selected_inventario(self)`

Edit selected inventory item

**Parameters:**

- `self`

---

##### `edit_selected_site(self)`

Edit selected site

**Parameters:**

- `self`

---

##### `edit_selected_us(self)`

Edit selected US

**Parameters:**

- `self`

---

##### `export_database(self)`

Export database to file

**Parameters:**

- `self`

---

##### `export_pdf_dialog(self)`

Show PDF export dialog

**Parameters:**

- `self`

---

##### `import_database(self)`

Import database from file

**Parameters:**

- `self`

---

##### `new_inventario_dialog(self)`

Show new inventory dialog

**Parameters:**

- `self`

---

##### `new_site_dialog(self)`

Show new site dialog

**Parameters:**

- `self`

---

##### `new_us_dialog(self)`

Show new US dialog

**Parameters:**

- `self`

---

##### `on_inventario_filter_changed(self, event)`

Handle inventory filter change

**Parameters:**

- `self`
- `event`

---

##### `on_site_changed(self, event)`

Handle site selection change

**Parameters:**

- `self`
- `event`

---

##### `on_sites_search(self)`

Handle sites search

**Parameters:**

- `self`

---

##### `on_us_filter_changed(self, event)`

Handle US filter change

**Parameters:**

- `self`
- `event`

---

##### `reconnect_database(self, connection_string)`

Reconnect to database with new connection string

**Parameters:**

- `self`
- `connection_string`

---

##### `refresh_activity_log(self)`

Refresh activity log in dashboard

**Parameters:**

- `self`

---

##### `refresh_dashboard(self)`

Refresh dashboard statistics

**Parameters:**

- `self`

---

##### `refresh_data(self)`

Refresh all data in the interface

**Parameters:**

- `self`

---

##### `refresh_inventario(self)`

Refresh inventory list

**Parameters:**

- `self`

---

##### `refresh_sites(self)`

Refresh sites list

**Parameters:**

- `self`

---

##### `refresh_us(self)`

Refresh US list

**Parameters:**

- `self`

---

##### `run(self)`

Start the application

**Parameters:**

- `self`

---

##### `setup_database(self)`

Initialize database connection and services

**Parameters:**

- `self`

---

##### `setup_styles(self)`

Configure ttk styles

**Parameters:**

- `self`

---

##### `show_about_dialog(self)`

Show about dialog

**Parameters:**

- `self`

---

##### `show_database_config(self)`

Show database configuration dialog

**Parameters:**

- `self`

---

##### `show_harris_matrix_dialog(self)`

Show Harris Matrix dialog

**Parameters:**

- `self`

---

##### `show_help_dialog(self)`

Show help dialog

**Parameters:**

- `self`

---

##### `show_media_manager(self)`

Show media manager dialog

**Parameters:**

- `self`

---

##### `show_media_manager(self)`

Show media manager dialog

**Parameters:**

- `self`

---

##### `show_pdf_export_dialog(self)`

Show PDF export dialog

**Parameters:**

- `self`

---

##### `show_postgres_installer(self)`

Show PostgreSQL installer dialog

**Parameters:**

- `self`

---

##### `show_statistics_dialog(self)`

Show statistics dialog

**Parameters:**

- `self`

---

##### `show_statistics_dialog(self)`

Show statistics dialog

**Parameters:**

- `self`

---

##### `show_tab(self, tab_name)`

Show specific tab

**Parameters:**

- `self`
- `tab_name`

---

##### `show_thesaurus_dialog(self)`

Show thesaurus management dialog

**Parameters:**

- `self`

---


#### `PyArchInitGUI`

Main GUI application for PyArchInit-Mini

**Methods:**

##### `__del__(self)`

Cleanup when application closes

**Parameters:**

- `self`

---

##### `__init__(self)`

Initializes the main window and core components of the PyArchInit-Mini GUI application. This method sets up the application window, initializes the database connection and necessary services, prepares status variables, applies GUI styles, creates the menu and main interface, and loads the initial data for display.

**Parameters:**

- `self`

---

##### `copy_as_new_database(self, source_file)`

Copy imported database as new file

**Parameters:**

- `self`
- `source_file`

---

##### `create_dashboard_content(self, parent)`

Create dashboard content widgets

**Parameters:**

- `self`
- `parent`

---

##### `create_dashboard_tab(self)`

Create dashboard tab

**Parameters:**

- `self`

---

##### `create_inventario_tab(self)`

Create inventory management tab

**Parameters:**

- `self`

---

##### `create_main_interface(self)`

Create main application interface

**Parameters:**

- `self`

---

##### `create_menu(self)`

Create application menu bar

**Parameters:**

- `self`

---

##### `create_sample_database(self)`

Create sample database

**Parameters:**

- `self`

---

##### `create_sites_tab(self)`

Create sites management tab

**Parameters:**

- `self`

---

##### `create_status_bar(self, parent)`

Create status bar

**Parameters:**

- `self`
- `parent`

---

##### `create_toolbar(self, parent)`

Create application toolbar

**Parameters:**

- `self`
- `parent`

---

##### `create_us_tab(self)`

Create US management tab

**Parameters:**

- `self`

---

##### `delete_selected_inventario(self)`

Delete selected inventory item

**Parameters:**

- `self`

---

##### `delete_selected_site(self)`

Delete selected site

**Parameters:**

- `self`

---

##### `delete_selected_us(self)`

Delete selected US

**Parameters:**

- `self`

---

##### `edit_selected_inventario(self)`

Edit selected inventory item

**Parameters:**

- `self`

---

##### `edit_selected_site(self)`

Edit selected site

**Parameters:**

- `self`

---

##### `edit_selected_us(self)`

Edit selected US

**Parameters:**

- `self`

---

##### `export_database(self)`

Export database to file

**Parameters:**

- `self`

---

##### `export_pdf_dialog(self)`

Show PDF export dialog

**Parameters:**

- `self`

---

##### `import_database(self)`

Import database from file

**Parameters:**

- `self`

---

##### `load_sample_database(self)`

Load the sample database

**Parameters:**

- `self`

---

##### `new_inventario_dialog(self)`

Show new inventory dialog

**Parameters:**

- `self`

---

##### `new_site_dialog(self)`

Show new site dialog

**Parameters:**

- `self`

---

##### `new_us_dialog(self)`

Show new US dialog

**Parameters:**

- `self`

---

##### `on_inventario_filter_changed(self, event)`

Handle inventory filter change

**Parameters:**

- `self`
- `event`

---

##### `on_site_changed(self, event)`

Handle site selection change

**Parameters:**

- `self`
- `event`

---

##### `on_sites_search(self)`

Handle sites search

**Parameters:**

- `self`

---

##### `on_us_filter_changed(self, event)`

Handle US filter change

**Parameters:**

- `self`
- `event`

---

##### `reconnect_database(self, connection_string)`

Reconnect to database with new connection string

**Parameters:**

- `self`
- `connection_string`

---

##### `refresh_activity_log(self)`

Refresh activity log in dashboard

**Parameters:**

- `self`

---

##### `refresh_dashboard(self)`

Refresh dashboard statistics

**Parameters:**

- `self`

---

##### `refresh_data(self)`

Refresh all data in the interface

**Parameters:**

- `self`

---

##### `refresh_inventario(self)`

Refresh inventory list

**Parameters:**

- `self`

---

##### `refresh_sites(self)`

Refresh sites list

**Parameters:**

- `self`

---

##### `refresh_us(self)`

Refresh US list

**Parameters:**

- `self`

---

##### `replace_current_database(self, source_file)`

Replace current database with imported one

**Parameters:**

- `self`
- `source_file`

---

##### `run(self)`

Start the application

**Parameters:**

- `self`

---

##### `setup_database(self)`

Initialize database connection and services

**Parameters:**

- `self`

---

##### `setup_styles(self)`

Configure ttk styles

**Parameters:**

- `self`

---

##### `show_about_dialog(self)`

Show about dialog

**Parameters:**

- `self`

---

##### `show_database_config(self)`

Show database configuration dialog

**Parameters:**

- `self`

---

##### `show_harris_matrix_dialog(self)`

Show Harris Matrix dialog

**Parameters:**

- `self`

---

##### `show_help_dialog(self)`

Show help dialog

**Parameters:**

- `self`

---

##### `show_media_manager(self)`

Show media manager dialog

**Parameters:**

- `self`

---

##### `show_media_manager(self)`

Show media manager dialog

**Parameters:**

- `self`

---

##### `show_pdf_export_dialog(self)`

Show PDF export dialog

**Parameters:**

- `self`

---

##### `show_postgres_installer(self)`

Show PostgreSQL installer dialog

**Parameters:**

- `self`

---

##### `show_statistics_dialog(self)`

Show statistics dialog

**Parameters:**

- `self`

---

##### `show_statistics_dialog(self)`

Show statistics dialog

**Parameters:**

- `self`

---

##### `show_tab(self, tab_name)`

Show specific tab

**Parameters:**

- `self`
- `tab_name`

---

##### `show_thesaurus_dialog(self)`

Show thesaurus management dialog

**Parameters:**

- `self`

---


### Functions

#### `on_postgres_installed(connection_string)`

Callback when PostgreSQL is installed and database created

**Parameters:**

- `connection_string`

---

#### `on_postgres_installed(connection_string)`

Callback when PostgreSQL is installed and database created

**Parameters:**

- `connection_string`

---

#### `on_postgres_installed(connection_string)`

Callback when PostgreSQL is installed and database created

**Parameters:**

- `connection_string`

---


\newpage


## Module: `desktop_gui/postgres_installer_dialog.py`

**File Path:** `desktop_gui/postgres_installer_dialog.py`

### Classes

#### `PostgreSQLInstallerDialog`

Dialog for PostgreSQL installation and setup

**Methods:**

##### `__init__(self, parent, postgres_installer, callback)`

Initializes the dialog window for PostgreSQL installation and setup. This method creates and configures the dialog interface, sets up the main frame and user interface elements, and initiates a check of the current PostgreSQL installation status. It requires the parent window, a PostgreSQL installer instance, and optionally a callback function to handle completion events.

**Parameters:**

- `self`
- `parent`
- `postgres_installer`
- `callback`

---

##### `center_window(self)`

Center dialog window on parent

**Parameters:**

- `self`

---

##### `check_postgres_status(self)`

Check current PostgreSQL status

**Parameters:**

- `self`

---

##### `close(self)`

Close dialog

**Parameters:**

- `self`

---

##### `create_database(self)`

Create PyArchInit database

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create the main interface

**Parameters:**

- `self`

---

##### `install_postgres_thread(self)`

PostgreSQL installation thread

**Parameters:**

- `self`

---

##### `log_message(self, message)`

Add message to log

**Parameters:**

- `self`
- `message`

---

##### `start_installation(self)`

Start PostgreSQL installation in background thread

**Parameters:**

- `self`

---

##### `test_connection(self)`

Test database connection

**Parameters:**

- `self`

---

##### `update_progress(self, value, message)`

Update progress bar and message

**Parameters:**

- `self`
- `value`
- `message`

---


#### `PostgreSQLInstallerDialog`

Dialog for PostgreSQL installation and setup

**Methods:**

##### `__init__(self, parent, postgres_installer, callback)`

Initializes the dialog window for PostgreSQL installation and setup. This method configures the dialog's properties, sets up the main interface components, and checks the current PostgreSQL installation status. It also stores references to the parent window, the installer object, and an optional callback for later use.

**Parameters:**

- `self`
- `parent`
- `postgres_installer`
- `callback`

---

##### `center_window(self)`

Center dialog window on parent

**Parameters:**

- `self`

---

##### `check_postgres_status(self)`

Check current PostgreSQL status

**Parameters:**

- `self`

---

##### `close(self)`

Close dialog

**Parameters:**

- `self`

---

##### `create_database(self)`

Create PyArchInit database

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create the main interface

**Parameters:**

- `self`

---

##### `install_postgres_thread(self)`

PostgreSQL installation thread

**Parameters:**

- `self`

---

##### `log_message(self, message)`

Add message to log

**Parameters:**

- `self`
- `message`

---

##### `start_installation(self)`

Start PostgreSQL installation in background thread

**Parameters:**

- `self`

---

##### `test_connection(self)`

Test database connection

**Parameters:**

- `self`

---

##### `update_progress(self, value, message)`

Update progress bar and message

**Parameters:**

- `self`
- `value`
- `message`

---


#### `PostgreSQLInstallerDialog`

Dialog for PostgreSQL installation and setup

**Methods:**

##### `__init__(self, parent, postgres_installer, callback)`

Initializes the PostgreSQL installation dialog by setting up the dialog window, its size, position, and modality with respect to the parent. It also creates the main user interface elements and checks the current status of the PostgreSQL installation. Optional callback functionality can be provided to handle post-installation actions.

**Parameters:**

- `self`
- `parent`
- `postgres_installer`
- `callback`

---

##### `center_window(self)`

Center dialog window on parent

**Parameters:**

- `self`

---

##### `check_postgres_status(self)`

Check current PostgreSQL status

**Parameters:**

- `self`

---

##### `close(self)`

Close dialog

**Parameters:**

- `self`

---

##### `create_database(self)`

Create PyArchInit database

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create the main interface

**Parameters:**

- `self`

---

##### `install_postgres_thread(self)`

PostgreSQL installation thread

**Parameters:**

- `self`

---

##### `log_message(self, message)`

Add message to log

**Parameters:**

- `self`
- `message`

---

##### `start_installation(self)`

Start PostgreSQL installation in background thread

**Parameters:**

- `self`

---

##### `test_connection(self)`

Test database connection

**Parameters:**

- `self`

---

##### `update_progress(self, value, message)`

Update progress bar and message

**Parameters:**

- `self`
- `value`
- `message`

---



\newpage


## Module: `desktop_gui/thesaurus_dialog.py`

**File Path:** `desktop_gui/thesaurus_dialog.py`

### Classes

#### `ThesaurusDialog`

Dialog for managing thesaurus and controlled vocabularies

**Methods:**

##### `__init__(self, parent, thesaurus_service, callback)`

Initializes the dialog for managing thesaurus and controlled vocabularies. This method sets up the dialog window, configures its properties, creates the main user interface, and loads the initial data required for interaction. It also accepts a parent widget, a thesaurus service instance, and an optional callback function.

**Parameters:**

- `self`
- `parent`
- `thesaurus_service`
- `callback`

---

##### `add_value(self)`

Add new value

**Parameters:**

- `self`

---

##### `center_window(self)`

Center dialog window on parent

**Parameters:**

- `self`

---

##### `clear_details_form(self)`

Clear the details form

**Parameters:**

- `self`

---

##### `clear_values(self)`

Clear the values tree

**Parameters:**

- `self`

---

##### `close(self)`

Close dialog

**Parameters:**

- `self`

---

##### `create_details_form(self, parent)`

Create the details form for value editing

**Parameters:**

- `self`
- `parent`

---

##### `create_interface(self)`

Create the main interface

**Parameters:**

- `self`

---

##### `delete_value(self)`

Delete selected value

**Parameters:**

- `self`

---

##### `edit_value(self)`

Edit selected value

**Parameters:**

- `self`

---

##### `initialize_defaults(self)`

Initialize default vocabularies

**Parameters:**

- `self`

---

##### `load_tables(self)`

Load available tables

**Parameters:**

- `self`

---

##### `load_values(self)`

Load values for the selected table and field

**Parameters:**

- `self`

---

##### `on_field_change(self, event)`

Handle field selection change

**Parameters:**

- `self`
- `event`

---

##### `on_table_change(self, event)`

Handle table selection change

**Parameters:**

- `self`
- `event`

---

##### `on_value_select(self, event)`

Handle value selection

**Parameters:**

- `self`
- `event`

---

##### `save_value_changes(self)`

Save changes to the selected value

**Parameters:**

- `self`

---


#### `ThesaurusDialog`

Dialog for managing thesaurus and controlled vocabularies

**Methods:**

##### `__init__(self, parent, thesaurus_service, callback)`

Initializes the dialog for managing thesaurus and controlled vocabularies. This method sets up the dialog window, configures its properties, creates the main interface components, and loads the initial data required for user interaction. It also accepts a parent widget, a thesaurus service instance, and an optional callback function for additional actions.

**Parameters:**

- `self`
- `parent`
- `thesaurus_service`
- `callback`

---

##### `add_value(self)`

Add new value

**Parameters:**

- `self`

---

##### `center_window(self)`

Center dialog window on parent

**Parameters:**

- `self`

---

##### `clear_details_form(self)`

Clear the details form

**Parameters:**

- `self`

---

##### `clear_values(self)`

Clear the values tree

**Parameters:**

- `self`

---

##### `close(self)`

Close dialog

**Parameters:**

- `self`

---

##### `create_details_form(self, parent)`

Create the details form for value editing

**Parameters:**

- `self`
- `parent`

---

##### `create_interface(self)`

Create the main interface

**Parameters:**

- `self`

---

##### `delete_value(self)`

Delete selected value

**Parameters:**

- `self`

---

##### `edit_value(self)`

Edit selected value

**Parameters:**

- `self`

---

##### `initialize_defaults(self)`

Initialize default vocabularies

**Parameters:**

- `self`

---

##### `load_tables(self)`

Load available tables

**Parameters:**

- `self`

---

##### `load_values(self)`

Load values for the selected table and field

**Parameters:**

- `self`

---

##### `on_field_change(self, event)`

Handle field selection change

**Parameters:**

- `self`
- `event`

---

##### `on_table_change(self, event)`

Handle table selection change

**Parameters:**

- `self`
- `event`

---

##### `on_value_select(self, event)`

Handle value selection

**Parameters:**

- `self`
- `event`

---

##### `save_value_changes(self)`

Save changes to the selected value

**Parameters:**

- `self`

---


#### `ThesaurusDialog`

Dialog for managing thesaurus and controlled vocabularies

**Methods:**

##### `__init__(self, parent, thesaurus_service, callback)`

Initializes the dialog for managing thesaurus and controlled vocabularies.  
This constructor sets up the dialog window, configures its properties, creates the main interface components, and loads the initial data required for user interaction.

**Parameters:**

- `self`
- `parent`
- `thesaurus_service`
- `callback`

---

##### `add_value(self)`

Add new value

**Parameters:**

- `self`

---

##### `center_window(self)`

Center dialog window on parent

**Parameters:**

- `self`

---

##### `clear_details_form(self)`

Clear the details form

**Parameters:**

- `self`

---

##### `clear_values(self)`

Clear the values tree

**Parameters:**

- `self`

---

##### `close(self)`

Close dialog

**Parameters:**

- `self`

---

##### `create_details_form(self, parent)`

Create the details form for value editing

**Parameters:**

- `self`
- `parent`

---

##### `create_interface(self)`

Create the main interface

**Parameters:**

- `self`

---

##### `delete_value(self)`

Delete selected value

**Parameters:**

- `self`

---

##### `edit_value(self)`

Edit selected value

**Parameters:**

- `self`

---

##### `initialize_defaults(self)`

Initialize default vocabularies

**Parameters:**

- `self`

---

##### `load_tables(self)`

Load available tables

**Parameters:**

- `self`

---

##### `load_values(self)`

Load values for the selected table and field

**Parameters:**

- `self`

---

##### `on_field_change(self, event)`

Handle field selection change

**Parameters:**

- `self`
- `event`

---

##### `on_table_change(self, event)`

Handle table selection change

**Parameters:**

- `self`
- `event`

---

##### `on_value_select(self, event)`

Handle value selection

**Parameters:**

- `self`
- `event`

---

##### `save_value_changes(self)`

Save changes to the selected value

**Parameters:**

- `self`

---



\newpage


## Module: `desktop_gui/us_dialog_extended.py`

**File Path:** `desktop_gui/us_dialog_extended.py`

### Classes

#### `ChronologicalSequenceDialog`

Dialog for displaying chronological sequence

**Methods:**

##### `__init__(self, parent, site_name, us_service, periodizzazione_service)`

**Description:**  
Initializes a new instance of the `ChronologicalSequenceDialog` class. This constructor sets up the dialog window by storing references to the parent widget, the site name, the US service, and the periodization service, preparing the dialog for further configuration and display.

**Parameters:**

- `self`
- `parent`
- `site_name`
- `us_service`
- `periodizzazione_service`

---

##### `close(self)`

Close dialog

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create chronological sequence interface

**Parameters:**

- `self`

---

##### `create_matrix_tab(self)`

Create stratigraphic matrix tab

**Parameters:**

- `self`

---

##### `create_periods_tab(self)`

Create periods summary tab

**Parameters:**

- `self`

---

##### `create_timeline_tab(self)`

Create timeline view tab

**Parameters:**

- `self`

---

##### `export_sequence(self)`

Export chronological sequence

**Parameters:**

- `self`

---

##### `generate_harris_matrix(self)`

Generate Harris Matrix

**Parameters:**

- `self`

---

##### `load_chronological_data(self)`

Load chronological data for the site

**Parameters:**

- `self`

---

##### `show_matrix_graph(self)`

Show matrix as graph

**Parameters:**

- `self`

---

##### `update_matrix_info(self, us_list)`

Update matrix information

**Parameters:**

- `self`
- `us_list`

---

##### `update_periods_summary(self, periods_summary)`

Update periods summary text

**Parameters:**

- `self`
- `periods_summary`

---


#### `ChronologicalSequenceDialog`

Dialog for displaying chronological sequence

**Methods:**

##### `__init__(self, parent, site_name, us_service, periodizzazione_service)`

Initializes a new instance of the **ChronologicalSequenceDialog** class. This method sets up the dialog window with the specified parent, site name, and service dependencies, configures the window properties, and initializes the user interface by creating the necessary components and loading chronological data.

**Parameters:**

- `self`
- `parent`
- `site_name`
- `us_service`
- `periodizzazione_service`

---

##### `close(self)`

Close dialog

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create chronological sequence interface

**Parameters:**

- `self`

---

##### `create_matrix_tab(self)`

Create stratigraphic matrix tab

**Parameters:**

- `self`

---

##### `create_periods_tab(self)`

Create periods summary tab

**Parameters:**

- `self`

---

##### `create_timeline_tab(self)`

Create timeline view tab

**Parameters:**

- `self`

---

##### `export_sequence(self)`

Export chronological sequence

**Parameters:**

- `self`

---

##### `generate_harris_matrix(self)`

Generate Harris Matrix

**Parameters:**

- `self`

---

##### `load_chronological_data(self)`

Load chronological data for the site

**Parameters:**

- `self`

---

##### `show_matrix_graph(self)`

Show matrix as graph

**Parameters:**

- `self`

---

##### `update_matrix_info(self, us_list)`

Update matrix information

**Parameters:**

- `self`
- `us_list`

---

##### `update_periods_summary(self, periods_summary)`

Update periods summary text

**Parameters:**

- `self`
- `periods_summary`

---


#### `ChronologicalSequenceDialog`

Dialog for displaying chronological sequence

**Methods:**

##### `__init__(self, parent, site_name, us_service, periodizzazione_service)`

Initializes a new instance of the **ChronologicalSequenceDialog** class. This constructor sets up the dialog window with the specified parent, site name, and service dependencies, configures the window properties (such as title, size, and modality), and initializes the user interface and chronological data display.

**Parameters:**

- `self`
- `parent`
- `site_name`
- `us_service`
- `periodizzazione_service`

---

##### `close(self)`

Close dialog

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create chronological sequence interface

**Parameters:**

- `self`

---

##### `create_matrix_tab(self)`

Create stratigraphic matrix tab

**Parameters:**

- `self`

---

##### `create_periods_tab(self)`

Create periods summary tab

**Parameters:**

- `self`

---

##### `create_timeline_tab(self)`

Create timeline view tab

**Parameters:**

- `self`

---

##### `export_sequence(self)`

Export chronological sequence

**Parameters:**

- `self`

---

##### `generate_harris_matrix(self)`

Generate Harris Matrix

**Parameters:**

- `self`

---

##### `load_chronological_data(self)`

Load chronological data for the site

**Parameters:**

- `self`

---

##### `show_matrix_graph(self)`

Show matrix as graph

**Parameters:**

- `self`

---

##### `update_matrix_info(self, us_list)`

Update matrix information

**Parameters:**

- `self`
- `us_list`

---

##### `update_periods_summary(self, periods_summary)`

Update periods summary text

**Parameters:**

- `self`
- `periods_summary`

---


#### `ExtendedUSDialog`

Extended US dialog with multiple tabs for complete archaeological recording

**Methods:**

##### `__init__(self, parent, us_service, site_service, matrix_generator, periodizzazione_service, site_names, us, callback)`

Initializes the extended US dialog window for comprehensive archaeological recording, setting up the necessary services, data structures, and user interface elements. This constructor configures the dialog as either a new entry or an edit form (depending on the provided US object), establishes the window properties, and prepares the interface for user interaction. If editing an existing US, it also pre-populates the form with relevant data.

**Parameters:**

- `self`
- `parent`
- `us_service`
- `site_service`
- `matrix_generator`
- `periodizzazione_service`
- `site_names`
- `us`
- `callback`

---

##### `add_media_file(self, event)`

Add new media file

**Parameters:**

- `self`
- `event`

---

##### `add_relationship(self)`

Add new stratigraphic relationship

**Parameters:**

- `self`

---

##### `cancel(self)`

Cancel and close dialog

**Parameters:**

- `self`

---

##### `create_basic_tab(self)`

Create basic information tab

**Parameters:**

- `self`

---

##### `create_chronology_tab(self)`

Create chronology/periodization tab

**Parameters:**

- `self`

---

##### `create_description_tab(self)`

Create descriptions tab

**Parameters:**

- `self`

---

##### `create_documentation_tab(self)`

Create documentation tab

**Parameters:**

- `self`

---

##### `create_file_icon(self, filename)`

Create a generic file icon

**Parameters:**

- `self`
- `filename`

---

##### `create_interface(self)`

Create the main interface with tabs

**Parameters:**

- `self`

---

##### `create_media_directory(self)`

Create media directory structure

**Parameters:**

- `self`

---

##### `create_media_item(self, filename, row, col)`

Create a media item widget

**Parameters:**

- `self`
- `filename`
- `row`
- `col`

---

##### `create_media_tab(self)`

Create media management tab with thumbnails and drag & drop

**Parameters:**

- `self`

---

##### `create_physical_tab(self)`

Create physical characteristics tab

**Parameters:**

- `self`

---

##### `create_relationships_tab(self)`

Create stratigraphic relationships tab

**Parameters:**

- `self`

---

##### `create_thumbnail(self, file_path)`

Create thumbnail for image files

**Parameters:**

- `self`
- `file_path`

---

##### `delete_relationship(self)`

Delete selected relationship

**Parameters:**

- `self`

---

##### `delete_selected_media(self)`

Delete selected media files

**Parameters:**

- `self`

---

##### `delete_us(self)`

Delete current US

**Parameters:**

- `self`

---

##### `edit_relationship(self)`

Edit selected relationship

**Parameters:**

- `self`

---

##### `export_all_media(self)`

Export all media files

**Parameters:**

- `self`

---

##### `format_file_size(self, size_bytes)`

Format file size in human readable format

**Parameters:**

- `self`
- `size_bytes`

---

##### `load_media_grid(self)`

Load media files in grid with thumbnails

**Parameters:**

- `self`

---

##### `load_relationships(self)`

Load stratigraphic relationships for current US

**Parameters:**

- `self`

---

##### `on_drop_click(self, event)`

Handle click on drop area

**Parameters:**

- `self`
- `event`

---

##### `on_file_drop(self, event)`

Handle file drop

**Parameters:**

- `self`
- `event`

---

##### `on_media_select(self, filename)`

Handle media item selection

**Parameters:**

- `self`
- `filename`

---

##### `open_harris_editor(self)`

Open Harris Matrix editor

**Parameters:**

- `self`

---

##### `open_periodization_dialog(self)`

Open detailed periodization dialog

**Parameters:**

- `self`

---

##### `populate_form(self)`

Populate form with existing US data

**Parameters:**

- `self`

---

##### `process_dropped_file(self, file_path)`

Process a dropped file

**Parameters:**

- `self`
- `file_path`

---

##### `refresh_periodization_data(self)`

Refresh periodization data in form

**Parameters:**

- `self`

---

##### `save_us(self)`

Save US data

**Parameters:**

- `self`

---

##### `setup_drag_drop(self)`

Setup drag and drop functionality

**Parameters:**

- `self`

---

##### `show_chronological_sequence(self)`

Show chronological sequence for site

**Parameters:**

- `self`

---

##### `view_media_file(self, filename)`

View selected media file

**Parameters:**

- `self`
- `filename`

---


#### `ExtendedUSDialog`

Extended US dialog with multiple tabs for complete archaeological recording

**Methods:**

##### `__init__(self, parent, us_service, site_service, matrix_generator, periodizzazione_service, site_names, us, callback)`

Initializes the Extended US dialog window for comprehensive archaeological recording, setting up all required services, data fields, and user interface components. This constructor configures the dialog as either a new record or for editing an existing US (Unità Stratigrafica), and prepares the multi-tabbed interface for user interaction. If an existing US is provided, the form is populated with its data for editing.

**Parameters:**

- `self`
- `parent`
- `us_service`
- `site_service`
- `matrix_generator`
- `periodizzazione_service`
- `site_names`
- `us`
- `callback`

---

##### `add_media_file(self, event)`

Add new media file

**Parameters:**

- `self`
- `event`

---

##### `add_relationship(self)`

Add new stratigraphic relationship

**Parameters:**

- `self`

---

##### `cancel(self)`

Cancel and close dialog

**Parameters:**

- `self`

---

##### `create_basic_tab(self)`

Create basic information tab

**Parameters:**

- `self`

---

##### `create_chronology_tab(self)`

Create chronology/periodization tab

**Parameters:**

- `self`

---

##### `create_description_tab(self)`

Create descriptions tab

**Parameters:**

- `self`

---

##### `create_documentation_tab(self)`

Create documentation tab

**Parameters:**

- `self`

---

##### `create_file_icon(self, filename)`

Create a generic file icon

**Parameters:**

- `self`
- `filename`

---

##### `create_interface(self)`

Create the main interface with tabs

**Parameters:**

- `self`

---

##### `create_media_directory(self)`

Create media directory structure

**Parameters:**

- `self`

---

##### `create_media_item(self, filename, row, col)`

Create a media item widget

**Parameters:**

- `self`
- `filename`
- `row`
- `col`

---

##### `create_media_tab(self)`

Create media management tab with thumbnails and drag & drop

**Parameters:**

- `self`

---

##### `create_physical_tab(self)`

Create physical characteristics tab

**Parameters:**

- `self`

---

##### `create_relationships_tab(self)`

Create stratigraphic relationships tab

**Parameters:**

- `self`

---

##### `create_thumbnail(self, file_path)`

Create thumbnail for image files

**Parameters:**

- `self`
- `file_path`

---

##### `delete_relationship(self)`

Delete selected relationship

**Parameters:**

- `self`

---

##### `delete_selected_media(self)`

Delete selected media files

**Parameters:**

- `self`

---

##### `delete_us(self)`

Delete current US

**Parameters:**

- `self`

---

##### `edit_relationship(self)`

Edit selected relationship

**Parameters:**

- `self`

---

##### `export_all_media(self)`

Export all media files

**Parameters:**

- `self`

---

##### `format_file_size(self, size_bytes)`

Format file size in human readable format

**Parameters:**

- `self`
- `size_bytes`

---

##### `load_media_grid(self)`

Load media files in grid with thumbnails

**Parameters:**

- `self`

---

##### `load_relationships(self)`

Load stratigraphic relationships for current US

**Parameters:**

- `self`

---

##### `on_drop_click(self, event)`

Handle click on drop area

**Parameters:**

- `self`
- `event`

---

##### `on_file_drop(self, event)`

Handle file drop

**Parameters:**

- `self`
- `event`

---

##### `on_media_select(self, filename)`

Handle media item selection

**Parameters:**

- `self`
- `filename`

---

##### `open_harris_editor(self)`

Open Harris Matrix editor

**Parameters:**

- `self`

---

##### `open_periodization_dialog(self)`

Open detailed periodization dialog

**Parameters:**

- `self`

---

##### `populate_form(self)`

Populate form with existing US data

**Parameters:**

- `self`

---

##### `process_dropped_file(self, file_path)`

Process a dropped file

**Parameters:**

- `self`
- `file_path`

---

##### `refresh_periodization_data(self)`

Refresh periodization data in form

**Parameters:**

- `self`

---

##### `save_us(self)`

Save US data

**Parameters:**

- `self`

---

##### `setup_drag_drop(self)`

Setup drag and drop functionality

**Parameters:**

- `self`

---

##### `show_chronological_sequence(self)`

Show chronological sequence for site

**Parameters:**

- `self`

---

##### `view_media_file(self, filename)`

View selected media file

**Parameters:**

- `self`
- `filename`

---


#### `ExtendedUSDialog`

Extended US dialog with multiple tabs for complete archaeological recording

**Methods:**

##### `__init__(self, parent, us_service, site_service, matrix_generator, periodizzazione_service, site_names, us, callback)`

Initializes the Extended US dialog for comprehensive archaeological recording, setting up the required services, site information, and optional US data. This constructor creates and configures a modal window with multiple tabs for data entry, and populates the form if an existing US record is being edited. It also prepares internal data structures for fields, relationships, and periodization.

**Parameters:**

- `self`
- `parent`
- `us_service`
- `site_service`
- `matrix_generator`
- `periodizzazione_service`
- `site_names`
- `us`
- `callback`

---

##### `add_media_file(self, event)`

Add new media file

**Parameters:**

- `self`
- `event`

---

##### `add_relationship(self)`

Add new stratigraphic relationship

**Parameters:**

- `self`

---

##### `cancel(self)`

Cancel and close dialog

**Parameters:**

- `self`

---

##### `create_basic_tab(self)`

Create basic information tab

**Parameters:**

- `self`

---

##### `create_chronology_tab(self)`

Create chronology/periodization tab

**Parameters:**

- `self`

---

##### `create_description_tab(self)`

Create descriptions tab

**Parameters:**

- `self`

---

##### `create_documentation_tab(self)`

Create documentation tab

**Parameters:**

- `self`

---

##### `create_file_icon(self, filename)`

Create a generic file icon

**Parameters:**

- `self`
- `filename`

---

##### `create_interface(self)`

Create the main interface with tabs

**Parameters:**

- `self`

---

##### `create_media_directory(self)`

Create media directory structure

**Parameters:**

- `self`

---

##### `create_media_item(self, filename, row, col)`

Create a media item widget

**Parameters:**

- `self`
- `filename`
- `row`
- `col`

---

##### `create_media_tab(self)`

Create media management tab with thumbnails and drag & drop

**Parameters:**

- `self`

---

##### `create_physical_tab(self)`

Create physical characteristics tab

**Parameters:**

- `self`

---

##### `create_relationships_tab(self)`

Create stratigraphic relationships tab

**Parameters:**

- `self`

---

##### `create_thumbnail(self, file_path)`

Create thumbnail for image files

**Parameters:**

- `self`
- `file_path`

---

##### `delete_relationship(self)`

Delete selected relationship

**Parameters:**

- `self`

---

##### `delete_selected_media(self)`

Delete selected media files

**Parameters:**

- `self`

---

##### `delete_us(self)`

Delete current US

**Parameters:**

- `self`

---

##### `edit_relationship(self)`

Edit selected relationship

**Parameters:**

- `self`

---

##### `export_all_media(self)`

Export all media files

**Parameters:**

- `self`

---

##### `format_file_size(self, size_bytes)`

Format file size in human readable format

**Parameters:**

- `self`
- `size_bytes`

---

##### `load_media_grid(self)`

Load media files in grid with thumbnails

**Parameters:**

- `self`

---

##### `load_relationships(self)`

Load stratigraphic relationships for current US

**Parameters:**

- `self`

---

##### `on_drop_click(self, event)`

Handle click on drop area

**Parameters:**

- `self`
- `event`

---

##### `on_file_drop(self, event)`

Handle file drop

**Parameters:**

- `self`
- `event`

---

##### `on_media_select(self, filename)`

Handle media item selection

**Parameters:**

- `self`
- `filename`

---

##### `open_harris_editor(self)`

Open Harris Matrix editor

**Parameters:**

- `self`

---

##### `open_periodization_dialog(self)`

Open detailed periodization dialog

**Parameters:**

- `self`

---

##### `populate_form(self)`

Populate form with existing US data

**Parameters:**

- `self`

---

##### `process_dropped_file(self, file_path)`

Process a dropped file

**Parameters:**

- `self`
- `file_path`

---

##### `refresh_periodization_data(self)`

Refresh periodization data in form

**Parameters:**

- `self`

---

##### `save_us(self)`

Save US data

**Parameters:**

- `self`

---

##### `setup_drag_drop(self)`

Setup drag and drop functionality

**Parameters:**

- `self`

---

##### `show_chronological_sequence(self)`

Show chronological sequence for site

**Parameters:**

- `self`

---

##### `view_media_file(self, filename)`

View selected media file

**Parameters:**

- `self`
- `filename`

---


#### `PeriodizationDialog`

Dialog for detailed periodization management

**Methods:**

##### `__init__(self, parent, us, periodizzazione_service, callback)`

Initializes a new instance of the PeriodizationDialog class. Sets up the dialog with the provided parent window, stratigraphic unit (us), periodization service, and an optional callback function to be executed after operations. This method prepares the dialog for managing detailed periodization tasks.

**Parameters:**

- `self`
- `parent`
- `us`
- `periodizzazione_service`
- `callback`

---

##### `cancel(self)`

Cancel and close dialog

**Parameters:**

- `self`

---

##### `create_chronology_tab(self)`

Create chronology tab

**Parameters:**

- `self`

---

##### `create_dating_tab(self)`

Create dating tab

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create periodization interface

**Parameters:**

- `self`

---

##### `create_phases_tab(self)`

Create phases tab

**Parameters:**

- `self`

---

##### `load_periodization_data(self)`

Load existing periodization data

**Parameters:**

- `self`

---

##### `save_periodization(self)`

Save periodization data

**Parameters:**

- `self`

---


#### `PeriodizationDialog`

Dialog for detailed periodization management

**Methods:**

##### `__init__(self, parent, us, periodizzazione_service, callback)`

Initializes a new instance of the **PeriodizationDialog** class. This constructor sets up the dialog window for detailed periodization management by storing provided parameters, creating the modal interface, and loading relevant periodization data.

**Parameters:**

- `self`
- `parent`
- `us`
- `periodizzazione_service`
- `callback`

---

##### `cancel(self)`

Cancel and close dialog

**Parameters:**

- `self`

---

##### `create_chronology_tab(self)`

Create chronology tab

**Parameters:**

- `self`

---

##### `create_dating_tab(self)`

Create dating tab

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create periodization interface

**Parameters:**

- `self`

---

##### `create_phases_tab(self)`

Create phases tab

**Parameters:**

- `self`

---

##### `load_periodization_data(self)`

Load existing periodization data

**Parameters:**

- `self`

---

##### `save_periodization(self)`

Save periodization data

**Parameters:**

- `self`

---


#### `PeriodizationDialog`

Dialog for detailed periodization management

**Methods:**

##### `__init__(self, parent, us, periodizzazione_service, callback)`

Initializes a new instance of the `PeriodizationDialog` class. This method creates and configures a modal dialog window for managing detailed periodization, sets up the user interface, and loads the relevant periodization data. It accepts the parent window, a user story object (`us`), a periodization service, and an optional callback function.

**Parameters:**

- `self`
- `parent`
- `us`
- `periodizzazione_service`
- `callback`

---

##### `cancel(self)`

Cancel and close dialog

**Parameters:**

- `self`

---

##### `create_chronology_tab(self)`

Create chronology tab

**Parameters:**

- `self`

---

##### `create_dating_tab(self)`

Create dating tab

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create periodization interface

**Parameters:**

- `self`

---

##### `create_phases_tab(self)`

Create phases tab

**Parameters:**

- `self`

---

##### `load_periodization_data(self)`

Load existing periodization data

**Parameters:**

- `self`

---

##### `save_periodization(self)`

Save periodization data

**Parameters:**

- `self`

---


#### `RelationshipDialog`

Simple dialog for adding stratigraphic relationships

**Methods:**

##### `__init__(self, parent, us, matrix_generator, callback)`

**__init__**  
Initializes a new instance of the `RelationshipDialog` class. This constructor sets up the dialog window and prepares all necessary components for adding stratigraphic relationships.

**Parameters:**

- `self`
- `parent`
- `us`
- `matrix_generator`
- `callback`

---

##### `cancel(self)`

Cancel dialog

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create relationship dialog interface

**Parameters:**

- `self`

---

##### `save_relationship(self)`

Save the relationship

**Parameters:**

- `self`

---


#### `RelationshipDialog`

Simple dialog for adding stratigraphic relationships

**Methods:**

##### `__init__(self, parent, us, matrix_generator, callback)`

Initializes a new instance of the **RelationshipDialog** class. Sets up the dialog window for adding stratigraphic relationships, initializes its attributes with the provided parameters, and invokes the method to create the user interface.

**Parameters:**

- `self`
- `parent`
- `us`
- `matrix_generator`
- `callback`

---

##### `cancel(self)`

Cancel dialog

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create relationship dialog interface

**Parameters:**

- `self`

---

##### `save_relationship(self)`

Save the relationship

**Parameters:**

- `self`

---


#### `RelationshipDialog`

Simple dialog for adding stratigraphic relationships

**Methods:**

##### `__init__(self, parent, us, matrix_generator, callback)`

Initializes a new instance of the `RelationshipDialog` class. Sets up the dialog window for adding stratigraphic relationships, configuring its properties and linking it to the parent window, the stratigraphic unit (`us`), the matrix generator, and an optional callback function. Calls the method to create the dialog interface.

**Parameters:**

- `self`
- `parent`
- `us`
- `matrix_generator`
- `callback`

---

##### `cancel(self)`

Cancel dialog

**Parameters:**

- `self`

---

##### `create_interface(self)`

Create relationship dialog interface

**Parameters:**

- `self`

---

##### `save_relationship(self)`

Save the relationship

**Parameters:**

- `self`

---



\newpage


## Module: `example_usage.py`

**File Path:** `example_usage.py`

### Functions

#### `main()`

Demonstrate PyArchInit-Mini usage

---

#### `main()`

Demonstrate PyArchInit-Mini usage

---

#### `main()`

Demonstrate PyArchInit-Mini usage

---


\newpage


## Module: `examples/__init__.py`

**File Path:** `examples/__init__.py`


\newpage


## Module: `examples/interface_demo.py`

**File Path:** `examples/interface_demo.py`

### Functions

#### `create_sample_data()`

Create sample archaeological data for demonstration

---

#### `create_sample_data()`

Create sample archaeological data for demonstration

---

#### `create_sample_data()`

Create sample archaeological data for demonstration

---

#### `demo_api_server()`

Demonstrate the FastAPI server

---

#### `demo_api_server()`

Demonstrate the FastAPI server

---

#### `demo_api_server()`

Demonstrate the FastAPI server

---

#### `demo_cli_interface()`

Demonstrate the Rich CLI interface

---

#### `demo_cli_interface()`

Demonstrate the Rich CLI interface

---

#### `demo_cli_interface()`

Demonstrate the Rich CLI interface

---

#### `demo_desktop_gui()`

Demonstrate the Tkinter desktop GUI

---

#### `demo_desktop_gui()`

Demonstrate the Tkinter desktop GUI

---

#### `demo_desktop_gui()`

Demonstrate the Tkinter desktop GUI

---

#### `demo_python_library()`

Demonstrate using PyArchInit-Mini as a Python library

---

#### `demo_python_library()`

Demonstrate using PyArchInit-Mini as a Python library

---

#### `demo_python_library()`

Demonstrate using PyArchInit-Mini as a Python library

---

#### `demo_web_interface()`

Demonstrate the Flask web interface

---

#### `demo_web_interface()`

Demonstrate the Flask web interface

---

#### `demo_web_interface()`

Demonstrate the Flask web interface

---

#### `main()`

Main demo function

---

#### `main()`

Main demo function

---

#### `main()`

Main demo function

---

#### `print_banner(title)`

Print a formatted banner

**Parameters:**

- `title`

---

#### `print_banner(title)`

Print a formatted banner

**Parameters:**

- `title`

---

#### `print_banner(title)`

Print a formatted banner

**Parameters:**

- `title`

---


\newpage


## Module: `launch_with_sample_data.py`

**File Path:** `launch_with_sample_data.py`

### Functions

#### `main()`

Launch PyArchInit-Mini with sample database

---

#### `main()`

Launch PyArchInit-Mini with sample database

---

#### `run_api()`

The `run_api` function serves as a wrapper to start the main API server by importing and invoking the `main` function from the `main` module. It includes exception handling to catch and print any errors that occur during the server startup, ensuring that issues are logged rather than causing the application to crash. Typically, this function is intended to be executed in a separate background thread.

---

#### `run_api()`

The **`run_api`** function serves as a wrapper to start the main API server by importing and invoking the `main` function from the `main` module. It handles any exceptions that occur during the server startup, printing an error message if the server fails to launch. This function is typically used to run the API server in a background thread.

---


\newpage


## Module: `main.py`

**File Path:** `main.py`

### Functions

#### `main()`

Main function to start the API server

---

#### `main()`

Main function to start the API server

---

#### `main()`

Main function to start the API server

---


\newpage


## Module: `migrate_database.py`

**File Path:** `migrate_database.py`

### Functions

#### `main()`

Main migration function

---

#### `main()`

Main migration function

---


\newpage


## Module: `pyarchinit_mini/__init__.py`

**File Path:** `pyarchinit_mini/__init__.py`


\newpage


## Module: `pyarchinit_mini/api/__init__.py`

**File Path:** `pyarchinit_mini/api/__init__.py`

### Functions

#### `create_app(database_url: str) → FastAPI`

Create and configure FastAPI application

Args:
    database_url: Database connection URL
    
Returns:
    Configured FastAPI app

**Parameters:**

- `database_url` (str)

**Returns:** `FastAPI`

---

#### `create_app(database_url: str) → FastAPI`

Create and configure FastAPI application

Args:
    database_url: Database connection URL
    
Returns:
    Configured FastAPI app

**Parameters:**

- `database_url` (str)

**Returns:** `FastAPI`

---

#### `create_app(database_url: str) → FastAPI`

Create and configure FastAPI application

Args:
    database_url: Database connection URL
    
Returns:
    Configured FastAPI app

**Parameters:**

- `database_url` (str)

**Returns:** `FastAPI`

---

#### `health_check()`

The `health_check` function is an asynchronous endpoint that responds to HTTP GET requests at the `/health` route. It returns a JSON object indicating the application's health status, typically used for monitoring and verifying that the service is running correctly.

**Modifiers:** `async`

**Decorators:** `app.get`

---

#### `health_check()`

The health_check function defines an HTTP GET endpoint at /health that returns a simple JSON response indicating the application's operational status. When accessed, it responds with {"status": "healthy"}, which can be used by monitoring tools or load balancers to verify that the service is running and responsive.

**Modifiers:** `async`

**Decorators:** `app.get`

---

#### `health_check()`

The **health_check** function is an HTTP GET endpoint that returns the current health status of the application. When accessed at the `/health` route, it responds with a JSON object indicating that the service is operational by returning `{"status": "healthy"}`. This endpoint is typically used for monitoring and verifying that the application is running correctly.

**Modifiers:** `async`

**Decorators:** `app.get`

---

#### `root()`

The **root** function is an asynchronous endpoint that handles GET requests to the root URL ("/") of the API. It returns a JSON response containing a welcome message, the current API version, and a link to the API documentation. This endpoint serves as an entry point to provide basic information about the PyArchInit-Mini API.

**Modifiers:** `async`

**Decorators:** `app.get`

---

#### `root()`

The **root** function is an asynchronous endpoint that handles GET requests to the root URL ("/") of the API. It returns a JSON response containing a welcome message, the current API version, and a link to the API documentation. This endpoint serves as the main entry point and overview for users of the PyArchInit-Mini API.

**Modifiers:** `async`

**Decorators:** `app.get`

---

#### `root()`

The **root** function defines the API's root endpoint ("/") and returns a JSON response containing a welcome message, the current API version, and a link to the documentation. It serves as an entry point for users to verify the API is running and to locate further documentation.

**Modifiers:** `async`

**Decorators:** `app.get`

---


\newpage


## Module: `pyarchinit_mini/api/dependencies.py`

**File Path:** `pyarchinit_mini/api/dependencies.py`

### Functions

#### `close_database()`

Close global database connection

---

#### `close_database()`

Close global database connection

---

#### `close_database()`

Close global database connection

---

#### `get_database_connection() → DatabaseConnection`

Get database connection dependency

**Returns:** `DatabaseConnection`

---

#### `get_database_connection() → DatabaseConnection`

Get database connection dependency

**Returns:** `DatabaseConnection`

---

#### `get_database_connection() → DatabaseConnection`

Get database connection dependency

**Returns:** `DatabaseConnection`

---

#### `get_database_manager(db_conn: DatabaseConnection) → DatabaseManager`

Get database manager dependency

**Parameters:**

- `db_conn` (DatabaseConnection)

**Returns:** `DatabaseManager`

---

#### `get_database_manager(db_conn: DatabaseConnection) → DatabaseManager`

Get database manager dependency

**Parameters:**

- `db_conn` (DatabaseConnection)

**Returns:** `DatabaseManager`

---

#### `get_database_manager(db_conn: DatabaseConnection) → DatabaseManager`

Get database manager dependency

**Parameters:**

- `db_conn` (DatabaseConnection)

**Returns:** `DatabaseManager`

---

#### `get_inventario_service(db_manager: DatabaseManager) → InventarioService`

Get inventario service dependency

**Parameters:**

- `db_manager` (DatabaseManager)

**Returns:** `InventarioService`

---

#### `get_inventario_service(db_manager: DatabaseManager) → InventarioService`

Get inventario service dependency

**Parameters:**

- `db_manager` (DatabaseManager)

**Returns:** `InventarioService`

---

#### `get_inventario_service(db_manager: DatabaseManager) → InventarioService`

Get inventario service dependency

**Parameters:**

- `db_manager` (DatabaseManager)

**Returns:** `InventarioService`

---

#### `get_site_service(db_manager: DatabaseManager) → SiteService`

Get site service dependency

**Parameters:**

- `db_manager` (DatabaseManager)

**Returns:** `SiteService`

---

#### `get_site_service(db_manager: DatabaseManager) → SiteService`

Get site service dependency

**Parameters:**

- `db_manager` (DatabaseManager)

**Returns:** `SiteService`

---

#### `get_site_service(db_manager: DatabaseManager) → SiteService`

Get site service dependency

**Parameters:**

- `db_manager` (DatabaseManager)

**Returns:** `SiteService`

---

#### `get_us_service(db_manager: DatabaseManager) → USService`

Get US service dependency

**Parameters:**

- `db_manager` (DatabaseManager)

**Returns:** `USService`

---

#### `get_us_service(db_manager: DatabaseManager) → USService`

Get US service dependency

**Parameters:**

- `db_manager` (DatabaseManager)

**Returns:** `USService`

---

#### `get_us_service(db_manager: DatabaseManager) → USService`

Get US service dependency

**Parameters:**

- `db_manager` (DatabaseManager)

**Returns:** `USService`

---

#### `init_database(database_url: str)`

Initialize global database connection

**Parameters:**

- `database_url` (str)

---

#### `init_database(database_url: str)`

Initialize global database connection

**Parameters:**

- `database_url` (str)

---

#### `init_database(database_url: str)`

Initialize global database connection

**Parameters:**

- `database_url` (str)

---


\newpage


## Module: `pyarchinit_mini/api/inventario.py`

**File Path:** `pyarchinit_mini/api/inventario.py`

### Functions

#### `create_inventario_item(item_data: InventarioCreate, inventario_service: InventarioService)`

Create a new inventory item

**Parameters:**

- `item_data` (InventarioCreate)
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.post`

---

#### `create_inventario_item(item_data: InventarioCreate, inventario_service: InventarioService)`

Create a new inventory item

**Parameters:**

- `item_data` (InventarioCreate)
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.post`

---

#### `create_inventario_item(item_data: InventarioCreate, inventario_service: InventarioService)`

Create a new inventory item

**Parameters:**

- `item_data` (InventarioCreate)
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.post`

---

#### `delete_inventario_item(item_id: int, inventario_service: InventarioService)`

Delete an inventory item

**Parameters:**

- `item_id` (int)
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.delete`

---

#### `delete_inventario_item(item_id: int, inventario_service: InventarioService)`

Delete an inventory item

**Parameters:**

- `item_id` (int)
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.delete`

---

#### `delete_inventario_item(item_id: int, inventario_service: InventarioService)`

Delete an inventory item

**Parameters:**

- `item_id` (int)
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.delete`

---

#### `get_inventario_item(item_id: int, inventario_service: InventarioService)`

Get inventory item by ID

**Parameters:**

- `item_id` (int)
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_inventario_item(item_id: int, inventario_service: InventarioService)`

Get inventory item by ID

**Parameters:**

- `item_id` (int)
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_inventario_item(item_id: int, inventario_service: InventarioService)`

Get inventory item by ID

**Parameters:**

- `item_id` (int)
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_inventario_list(page: int, size: int, sito: Optional[str], tipo_reperto: Optional[str], inventario_service: InventarioService)`

Get paginated list of inventory items

**Parameters:**

- `page` (int)
- `size` (int)
- `sito` (Optional[str])
- `tipo_reperto` (Optional[str])
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_inventario_list(page: int, size: int, sito: Optional[str], tipo_reperto: Optional[str], inventario_service: InventarioService)`

Get paginated list of inventory items

**Parameters:**

- `page` (int)
- `size` (int)
- `sito` (Optional[str])
- `tipo_reperto` (Optional[str])
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_inventario_list(page: int, size: int, sito: Optional[str], tipo_reperto: Optional[str], inventario_service: InventarioService)`

Get paginated list of inventory items

**Parameters:**

- `page` (int)
- `size` (int)
- `sito` (Optional[str])
- `tipo_reperto` (Optional[str])
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `update_inventario_item(item_id: int, item_data: InventarioUpdate, inventario_service: InventarioService)`

Update an existing inventory item

**Parameters:**

- `item_id` (int)
- `item_data` (InventarioUpdate)
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.put`

---

#### `update_inventario_item(item_id: int, item_data: InventarioUpdate, inventario_service: InventarioService)`

Update an existing inventory item

**Parameters:**

- `item_id` (int)
- `item_data` (InventarioUpdate)
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.put`

---

#### `update_inventario_item(item_id: int, item_data: InventarioUpdate, inventario_service: InventarioService)`

Update an existing inventory item

**Parameters:**

- `item_id` (int)
- `item_data` (InventarioUpdate)
- `inventario_service` (InventarioService)

**Modifiers:** `async`

**Decorators:** `router.put`

---


\newpage


## Module: `pyarchinit_mini/api/schemas.py`

**File Path:** `pyarchinit_mini/api/schemas.py`

### Classes

#### `BaseSchema`

Base schema with common fields

**Inherits from:** `BaseModel`


#### `BaseSchema`

Base schema with common fields

**Inherits from:** `BaseModel`


#### `BaseSchema`

Base schema with common fields

**Inherits from:** `BaseModel`


#### `Config`

The **Config** class defines configuration options for a Pydantic model, enabling features such as attribute-based data population by setting `from_attributes = True`. This allows instances of the model to be created directly from objects with matching attribute names, improving flexibility in data parsing and serialization workflows.


#### `Config`

The **Config** class defines the pagination parameters for a dataset, including the current page number (`page`), the number of items per page (`size`), and the total number of pages (`pages`). It leverages attribute-based serialization to facilitate data exchange and validation. This class is typically used to standardize and manage paginated API responses.


#### `Config`

The **Config** class is an internal configuration class used to customize the behavior of the parent Pydantic model. By setting `from_attributes = True`, it allows model instances to be created from objects with matching attribute names, not just from dictionaries. This enhances flexibility when initializing models from various data sources.


#### `Config`

The Config class defines the structure for pagination configuration, specifying the current page, page size, and total number of pages. Each field includes descriptive metadata to support clear API documentation and validation. The inner Config class enables initialization of instances from attribute-based data sources.


#### `Config`

The **Config** class is a configuration class used within a Pydantic schema to specify model behaviors and options. In this context, it enables the `from_attributes` setting, allowing the schema to be populated from object attributes rather than just dictionaries. This facilitates seamless integration with ORM models and other objects when creating or updating schema instances.


#### `Config`

The **Config** class defines the pagination configuration for data queries, specifying the current page, the number of items per page, and the total number of pages available. It is designed to facilitate structured and consistent handling of paginated responses. The class is configured to support initialization from attribute-based data sources.


#### `InventarioBase`

Base inventory schema

**Inherits from:** `BaseModel`

**Methods:**

##### `validate_yes_no_fields(cls, v)`

The **validate_yes_no_fields** method is a data validator that ensures the values provided for the fields 'lavato', 'repertato', and 'diagnostico' are either 'SI', 'NO', 'S', or 'N' (case-insensitive). If a value is provided and does not match one of these accepted responses, a ValueError is raised. This helps enforce data integrity for fields intended to capture binary yes/no information.

**Parameters:**

- `cls`
- `v`

**Decorators:** `validator`

---


#### `InventarioBase`

Base inventory schema

**Inherits from:** `BaseModel`

**Methods:**

##### `validate_yes_no_fields(cls, v)`

The **validate_yes_no_fields** method is a Pydantic validator that ensures the values assigned to the 'lavato', 'repertato', and 'diagnostico' fields are either 'SI', 'NO', 'S', or 'N' (case-insensitive). If a value outside of these accepted responses is provided, a ValueError is raised. This validation enforces standardized yes/no input for these fields.

**Parameters:**

- `cls`
- `v`

**Decorators:** `validator`

---


#### `InventarioBase`

Base inventory schema

**Inherits from:** `BaseModel`

**Methods:**

##### `validate_yes_no_fields(cls, v)`

The `validate_yes_no_fields` method is a Pydantic validator that ensures the values of the fields `lavato`, `repertato`, and `diagnostico` are either 'SI', 'NO', 'S', or 'N' (case-insensitive). If a value outside these accepted options is provided, it raises a `ValueError`. This validation enforces standardized yes/no responses for these fields.

**Parameters:**

- `cls`
- `v`

**Decorators:** `validator`

---


#### `InventarioCreate`

Schema for creating inventory item

**Inherits from:** `InventarioBase`


#### `InventarioCreate`

Schema for creating inventory item

**Inherits from:** `InventarioBase`


#### `InventarioCreate`

Schema for creating inventory item

**Inherits from:** `InventarioBase`


#### `InventarioResponse`

Schema for inventory response

**Inherits from:** `InventarioBase, BaseSchema`


#### `InventarioResponse`

Schema for inventory response

**Inherits from:** `InventarioBase, BaseSchema`


#### `InventarioResponse`

Schema for inventory response

**Inherits from:** `InventarioBase, BaseSchema`


#### `InventarioUpdate`

Schema for updating inventory item

**Inherits from:** `BaseModel`


#### `InventarioUpdate`

Schema for updating inventory item

**Inherits from:** `BaseModel`


#### `InventarioUpdate`

Schema for updating inventory item

**Inherits from:** `BaseModel`


#### `PaginatedResponse`

Paginated response wrapper

**Inherits from:** `BaseModel`


#### `PaginatedResponse`

Paginated response wrapper

**Inherits from:** `BaseModel`


#### `PaginatedResponse`

Paginated response wrapper

**Inherits from:** `BaseModel`


#### `PaginationParams`

Pagination parameters

**Inherits from:** `BaseModel`


#### `PaginationParams`

Pagination parameters

**Inherits from:** `BaseModel`


#### `PaginationParams`

Pagination parameters

**Inherits from:** `BaseModel`


#### `SiteBase`

Base site schema

**Inherits from:** `BaseModel`


#### `SiteBase`

Base site schema

**Inherits from:** `BaseModel`


#### `SiteBase`

Base site schema

**Inherits from:** `BaseModel`


#### `SiteCreate`

Schema for creating a site

**Inherits from:** `SiteBase`


#### `SiteCreate`

Schema for creating a site

**Inherits from:** `SiteBase`


#### `SiteCreate`

Schema for creating a site

**Inherits from:** `SiteBase`


#### `SiteResponse`

Schema for site response

**Inherits from:** `SiteBase, BaseSchema`


#### `SiteResponse`

Schema for site response

**Inherits from:** `SiteBase, BaseSchema`


#### `SiteResponse`

Schema for site response

**Inherits from:** `SiteBase, BaseSchema`


#### `SiteUpdate`

Schema for updating a site

**Inherits from:** `BaseModel`


#### `SiteUpdate`

Schema for updating a site

**Inherits from:** `BaseModel`


#### `SiteUpdate`

Schema for updating a site

**Inherits from:** `BaseModel`


#### `USBase`

Base US schema

**Inherits from:** `BaseModel`


#### `USBase`

Base US schema

**Inherits from:** `BaseModel`


#### `USBase`

Base US schema

**Inherits from:** `BaseModel`


#### `USCreate`

Schema for creating a US

**Inherits from:** `USBase`


#### `USCreate`

Schema for creating a US

**Inherits from:** `USBase`


#### `USCreate`

Schema for creating a US

**Inherits from:** `USBase`


#### `USResponse`

Schema for US response

**Inherits from:** `USBase, BaseSchema`


#### `USResponse`

Schema for US response

**Inherits from:** `USBase, BaseSchema`


#### `USResponse`

Schema for US response

**Inherits from:** `USBase, BaseSchema`


#### `USUpdate`

Schema for updating a US

**Inherits from:** `BaseModel`


#### `USUpdate`

Schema for updating a US

**Inherits from:** `BaseModel`


#### `USUpdate`

Schema for updating a US

**Inherits from:** `BaseModel`



\newpage


## Module: `pyarchinit_mini/api/site.py`

**File Path:** `pyarchinit_mini/api/site.py`

### Functions

#### `create_site(site_data: SiteCreate, site_service: SiteService)`

Create a new site

**Parameters:**

- `site_data` (SiteCreate)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.post`

---

#### `create_site(site_data: SiteCreate, site_service: SiteService)`

Create a new site

**Parameters:**

- `site_data` (SiteCreate)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.post`

---

#### `create_site(site_data: SiteCreate, site_service: SiteService)`

Create a new site

**Parameters:**

- `site_data` (SiteCreate)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.post`

---

#### `delete_site(site_id: int, site_service: SiteService)`

Delete a site

**Parameters:**

- `site_id` (int)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.delete`

---

#### `delete_site(site_id: int, site_service: SiteService)`

Delete a site

**Parameters:**

- `site_id` (int)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.delete`

---

#### `delete_site(site_id: int, site_service: SiteService)`

Delete a site

**Parameters:**

- `site_id` (int)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.delete`

---

#### `get_countries(site_service: SiteService)`

Get list of unique countries from sites

**Parameters:**

- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_countries(site_service: SiteService)`

Get list of unique countries from sites

**Parameters:**

- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_countries(site_service: SiteService)`

Get list of unique countries from sites

**Parameters:**

- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_municipalities(nazione: Optional[str], regione: Optional[str], site_service: SiteService)`

Get list of unique municipalities, optionally filtered by country and region

**Parameters:**

- `nazione` (Optional[str])
- `regione` (Optional[str])
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_municipalities(nazione: Optional[str], regione: Optional[str], site_service: SiteService)`

Get list of unique municipalities, optionally filtered by country and region

**Parameters:**

- `nazione` (Optional[str])
- `regione` (Optional[str])
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_municipalities(nazione: Optional[str], regione: Optional[str], site_service: SiteService)`

Get list of unique municipalities, optionally filtered by country and region

**Parameters:**

- `nazione` (Optional[str])
- `regione` (Optional[str])
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_regions(nazione: Optional[str], site_service: SiteService)`

Get list of unique regions, optionally filtered by country

**Parameters:**

- `nazione` (Optional[str])
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_regions(nazione: Optional[str], site_service: SiteService)`

Get list of unique regions, optionally filtered by country

**Parameters:**

- `nazione` (Optional[str])
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_regions(nazione: Optional[str], site_service: SiteService)`

Get list of unique regions, optionally filtered by country

**Parameters:**

- `nazione` (Optional[str])
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_site(site_id: int, site_service: SiteService)`

Get site by ID

**Parameters:**

- `site_id` (int)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_site(site_id: int, site_service: SiteService)`

Get site by ID

**Parameters:**

- `site_id` (int)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_site(site_id: int, site_service: SiteService)`

Get site by ID

**Parameters:**

- `site_id` (int)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_site_by_name(site_name: str, site_service: SiteService)`

Get site by name

**Parameters:**

- `site_name` (str)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_site_by_name(site_name: str, site_service: SiteService)`

Get site by name

**Parameters:**

- `site_name` (str)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_site_by_name(site_name: str, site_service: SiteService)`

Get site by name

**Parameters:**

- `site_name` (str)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_site_stats(site_id: int, site_service: SiteService)`

Get statistics for a site (US count, inventory count, etc.)

**Parameters:**

- `site_id` (int)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_site_stats(site_id: int, site_service: SiteService)`

Get statistics for a site (US count, inventory count, etc.)

**Parameters:**

- `site_id` (int)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_site_stats(site_id: int, site_service: SiteService)`

Get statistics for a site (US count, inventory count, etc.)

**Parameters:**

- `site_id` (int)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_sites(page: int, size: int, search: Optional[str], nazione: Optional[str], regione: Optional[str], comune: Optional[str], site_service: SiteService)`

Get paginated list of sites with optional filtering and search

**Parameters:**

- `page` (int)
- `size` (int)
- `search` (Optional[str])
- `nazione` (Optional[str])
- `regione` (Optional[str])
- `comune` (Optional[str])
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_sites(page: int, size: int, search: Optional[str], nazione: Optional[str], regione: Optional[str], comune: Optional[str], site_service: SiteService)`

Get paginated list of sites with optional filtering and search

**Parameters:**

- `page` (int)
- `size` (int)
- `search` (Optional[str])
- `nazione` (Optional[str])
- `regione` (Optional[str])
- `comune` (Optional[str])
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_sites(page: int, size: int, search: Optional[str], nazione: Optional[str], regione: Optional[str], comune: Optional[str], site_service: SiteService)`

Get paginated list of sites with optional filtering and search

**Parameters:**

- `page` (int)
- `size` (int)
- `search` (Optional[str])
- `nazione` (Optional[str])
- `regione` (Optional[str])
- `comune` (Optional[str])
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `update_site(site_id: int, site_data: SiteUpdate, site_service: SiteService)`

Update an existing site

**Parameters:**

- `site_id` (int)
- `site_data` (SiteUpdate)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.put`

---

#### `update_site(site_id: int, site_data: SiteUpdate, site_service: SiteService)`

Update an existing site

**Parameters:**

- `site_id` (int)
- `site_data` (SiteUpdate)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.put`

---

#### `update_site(site_id: int, site_data: SiteUpdate, site_service: SiteService)`

Update an existing site

**Parameters:**

- `site_id` (int)
- `site_data` (SiteUpdate)
- `site_service` (SiteService)

**Modifiers:** `async`

**Decorators:** `router.put`

---


\newpage


## Module: `pyarchinit_mini/api/us.py`

**File Path:** `pyarchinit_mini/api/us.py`

### Functions

#### `create_us(us_data: USCreate, us_service: USService)`

Create a new stratigraphic unit

**Parameters:**

- `us_data` (USCreate)
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.post`

---

#### `create_us(us_data: USCreate, us_service: USService)`

Create a new stratigraphic unit

**Parameters:**

- `us_data` (USCreate)
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.post`

---

#### `create_us(us_data: USCreate, us_service: USService)`

Create a new stratigraphic unit

**Parameters:**

- `us_data` (USCreate)
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.post`

---

#### `delete_us(us_id: int, us_service: USService)`

Delete a stratigraphic unit

**Parameters:**

- `us_id` (int)
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.delete`

---

#### `delete_us(us_id: int, us_service: USService)`

Delete a stratigraphic unit

**Parameters:**

- `us_id` (int)
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.delete`

---

#### `delete_us(us_id: int, us_service: USService)`

Delete a stratigraphic unit

**Parameters:**

- `us_id` (int)
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.delete`

---

#### `get_us(us_id: int, us_service: USService)`

Get US by ID

**Parameters:**

- `us_id` (int)
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_us(us_id: int, us_service: USService)`

Get US by ID

**Parameters:**

- `us_id` (int)
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_us(us_id: int, us_service: USService)`

Get US by ID

**Parameters:**

- `us_id` (int)
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_us_list(page: int, size: int, sito: Optional[str], area: Optional[str], us_service: USService)`

Get paginated list of stratigraphic units

**Parameters:**

- `page` (int)
- `size` (int)
- `sito` (Optional[str])
- `area` (Optional[str])
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_us_list(page: int, size: int, sito: Optional[str], area: Optional[str], us_service: USService)`

Get paginated list of stratigraphic units

**Parameters:**

- `page` (int)
- `size` (int)
- `sito` (Optional[str])
- `area` (Optional[str])
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `get_us_list(page: int, size: int, sito: Optional[str], area: Optional[str], us_service: USService)`

Get paginated list of stratigraphic units

**Parameters:**

- `page` (int)
- `size` (int)
- `sito` (Optional[str])
- `area` (Optional[str])
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.get`

---

#### `update_us(us_id: int, us_data: USUpdate, us_service: USService)`

Update an existing stratigraphic unit

**Parameters:**

- `us_id` (int)
- `us_data` (USUpdate)
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.put`

---

#### `update_us(us_id: int, us_data: USUpdate, us_service: USService)`

Update an existing stratigraphic unit

**Parameters:**

- `us_id` (int)
- `us_data` (USUpdate)
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.put`

---

#### `update_us(us_id: int, us_data: USUpdate, us_service: USService)`

Update an existing stratigraphic unit

**Parameters:**

- `us_id` (int)
- `us_data` (USUpdate)
- `us_service` (USService)

**Modifiers:** `async`

**Decorators:** `router.put`

---


\newpage


## Module: `pyarchinit_mini/database/__init__.py`

**File Path:** `pyarchinit_mini/database/__init__.py`


\newpage


## Module: `pyarchinit_mini/database/connection.py`

**File Path:** `pyarchinit_mini/database/connection.py`

### Classes

#### `DatabaseConnection`

Manages database connections for both PostgreSQL and SQLite

**Methods:**

##### `__init__(self, connection_string: str)`

Initializes a new instance of the database connection manager with the provided connection string. This method stores the connection string and prepares the necessary attributes for establishing database connections. Upon initialization, it also triggers the setup of the database engine and session factory.

**Parameters:**

- `self`
- `connection_string` (str)

---

##### `close(self)`

Close database connection

**Parameters:**

- `self`

---

##### `create_tables(self)`

Create all tables from models

**Parameters:**

- `self`

---

##### `from_url(cls, database_url: str) → DatabaseConnection`

Create connection from database URL

**Parameters:**

- `cls`
- `database_url` (str)

**Returns:** `DatabaseConnection`

**Decorators:** `classmethod`

---

##### `get_session(self) → Session`

Context manager for database sessions
Ensures proper session cleanup

**Parameters:**

- `self`

**Returns:** `Session`

**Decorators:** `contextmanager`

---

##### `postgresql(cls, host: str, port: int, database: str, username: str, password: str) → DatabaseConnection`

Create PostgreSQL connection

**Parameters:**

- `cls`
- `host` (str)
- `port` (int)
- `database` (str)
- `username` (str)
- `password` (str)

**Returns:** `DatabaseConnection`

**Decorators:** `classmethod`

---

##### `sqlite(cls, db_path: str) → DatabaseConnection`

Create SQLite connection

**Parameters:**

- `cls`
- `db_path` (str)

**Returns:** `DatabaseConnection`

**Decorators:** `classmethod`

---

##### `test_connection(self) → bool`

Test database connection

**Parameters:**

- `self`

**Returns:** `bool`

---


#### `DatabaseConnection`

Manages database connections for both PostgreSQL and SQLite

**Methods:**

##### `__init__(self, connection_string: str)`

Initializes a new instance of the database connection manager with the provided connection string. This method sets up the necessary attributes and triggers the configuration of the database engine and session factory to enable interactions with either PostgreSQL or SQLite databases.

**Parameters:**

- `self`
- `connection_string` (str)

---

##### `close(self)`

Close database connection

**Parameters:**

- `self`

---

##### `create_tables(self)`

Create all tables from models

**Parameters:**

- `self`

---

##### `from_url(cls, database_url: str) → DatabaseConnection`

Create connection from database URL

**Parameters:**

- `cls`
- `database_url` (str)

**Returns:** `DatabaseConnection`

**Decorators:** `classmethod`

---

##### `get_session(self) → Session`

Context manager for database sessions
Ensures proper session cleanup

**Parameters:**

- `self`

**Returns:** `Session`

**Decorators:** `contextmanager`

---

##### `initialize_database(self)`

Initialize database and create tables with migrations

**Parameters:**

- `self`

---

##### `postgresql(cls, host: str, port: int, database: str, username: str, password: str) → DatabaseConnection`

Create PostgreSQL connection

**Parameters:**

- `cls`
- `host` (str)
- `port` (int)
- `database` (str)
- `username` (str)
- `password` (str)

**Returns:** `DatabaseConnection`

**Decorators:** `classmethod`

---

##### `sqlite(cls, db_path: str) → DatabaseConnection`

Create SQLite connection

**Parameters:**

- `cls`
- `db_path` (str)

**Returns:** `DatabaseConnection`

**Decorators:** `classmethod`

---

##### `test_connection(self) → bool`

Test database connection

**Parameters:**

- `self`

**Returns:** `bool`

---


#### `DatabaseConnection`

Manages database connections for both PostgreSQL and SQLite

**Methods:**

##### `__init__(self, connection_string: str)`

Initializes a new instance of the database connection manager with the specified connection string. This method sets up the required attributes and triggers the initialization of the database engine and session factory. It supports connections to both PostgreSQL and SQLite databases.

**Parameters:**

- `self`
- `connection_string` (str)

---

##### `close(self)`

Close database connection

**Parameters:**

- `self`

---

##### `create_tables(self)`

Create all tables from models

**Parameters:**

- `self`

---

##### `from_url(cls, database_url: str) → DatabaseConnection`

Create connection from database URL

**Parameters:**

- `cls`
- `database_url` (str)

**Returns:** `DatabaseConnection`

**Decorators:** `classmethod`

---

##### `get_session(self) → Session`

Context manager for database sessions
Ensures proper session cleanup

**Parameters:**

- `self`

**Returns:** `Session`

**Decorators:** `contextmanager`

---

##### `initialize_database(self)`

Initialize database and create tables with migrations

**Parameters:**

- `self`

---

##### `postgresql(cls, host: str, port: int, database: str, username: str, password: str) → DatabaseConnection`

Create PostgreSQL connection

**Parameters:**

- `cls`
- `host` (str)
- `port` (int)
- `database` (str)
- `username` (str)
- `password` (str)

**Returns:** `DatabaseConnection`

**Decorators:** `classmethod`

---

##### `sqlite(cls, db_path: str) → DatabaseConnection`

Create SQLite connection

**Parameters:**

- `cls`
- `db_path` (str)

**Returns:** `DatabaseConnection`

**Decorators:** `classmethod`

---

##### `test_connection(self) → bool`

Test database connection

**Parameters:**

- `self`

**Returns:** `bool`

---


### Functions

#### `set_sqlite_pragma(dbapi_connection, connection_record)`

The **set_sqlite_pragma** function is an event listener for SQLAlchemy that executes the SQLite `PRAGMA foreign_keys=ON` statement whenever a new database connection is established. This ensures that foreign key constraints are enforced in all SQLite connections managed by the SQLAlchemy engine. It is particularly important because, by default, SQLite does not enforce foreign key constraints unless explicitly enabled.

**Parameters:**

- `dbapi_connection`
- `connection_record`

**Decorators:** `event.listens_for`

---

#### `set_sqlite_pragma(dbapi_connection, connection_record)`

The `set_sqlite_pragma` function is an event listener that executes whenever a new SQLite database connection is established through SQLAlchemy. It enables foreign key constraint enforcement by executing the SQL statement `PRAGMA foreign_keys=ON` on the newly connected database. This ensures that SQLite complies with foreign key relationships defined in the schema.

**Parameters:**

- `dbapi_connection`
- `connection_record`

**Decorators:** `event.listens_for`

---


\newpage


## Module: `pyarchinit_mini/database/manager.py`

**File Path:** `pyarchinit_mini/database/manager.py`

### Classes

#### `DatabaseManager`

High-level database manager providing CRUD operations
and query functionality for PyArchInit-Mini models

**Methods:**

##### `__init__(self, connection: DatabaseConnection)`

Initializes a new instance of the DatabaseManager class.  
This method sets up the database manager by assigning the provided DatabaseConnection object to the instance, enabling subsequent database operations.

**Parameters:**

- `self`
- `connection` (DatabaseConnection)

---

##### `begin_transaction(self) → Session`

Begin a manual transaction

**Parameters:**

- `self`

**Returns:** `Session`

---

##### `bulk_create(self, model_class: Type[T], data_list: List[Dict[str, Any]]) → List[T]`

Create multiple records in a single transaction

**Parameters:**

- `self`
- `model_class` (Type[T])
- `data_list` (List[Dict[str, Any]])

**Returns:** `List[T]`

---

##### `commit_transaction(self, session: Session)`

Commit transaction

**Parameters:**

- `self`
- `session` (Session)

---

##### `count(self, model_class: Type[T], filters: Optional[Dict[str, Any]]) → int`

Count records with optional filters

**Parameters:**

- `self`
- `model_class` (Type[T])
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create(self, model_class: Type[T], data: Dict[str, Any]) → T`

Create a new record

**Parameters:**

- `self`
- `model_class` (Type[T])
- `data` (Dict[str, Any])

**Returns:** `T`

---

##### `delete(self, model_class: Type[T], record_id: int) → bool`

Delete record by ID

**Parameters:**

- `self`
- `model_class` (Type[T])
- `record_id` (int)

**Returns:** `bool`

---

##### `execute_raw_query(self, query: str, params: Optional[Dict])`

Execute raw SQL query

**Parameters:**

- `self`
- `query` (str)
- `params` (Optional[Dict])

---

##### `get_all(self, model_class: Type[T], offset: int, limit: int, order_by: Optional[str], filters: Optional[Dict[str, Any]]) → List[T]`

Get all records with optional filtering and pagination

**Parameters:**

- `self`
- `model_class` (Type[T])
- `offset` (int)
- `limit` (int)
- `order_by` (Optional[str])
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[T]`

---

##### `get_by_field(self, model_class: Type[T], field_name: str, value: Any) → Optional[T]`

Get record by specific field

**Parameters:**

- `self`
- `model_class` (Type[T])
- `field_name` (str)
- `value` (Any)

**Returns:** `Optional[T]`

---

##### `get_by_id(self, model_class: Type[T], record_id: int) → Optional[T]`

Get record by primary key

**Parameters:**

- `self`
- `model_class` (Type[T])
- `record_id` (int)

**Returns:** `Optional[T]`

---

##### `get_table_info(self, model_class: Type[T]) → Dict[str, Any]`

Get table metadata information

**Parameters:**

- `self`
- `model_class` (Type[T])

**Returns:** `Dict[str, Any]`

---

##### `rollback_transaction(self, session: Session)`

Rollback transaction

**Parameters:**

- `self`
- `session` (Session)

---

##### `search(self, model_class: Type[T], search_term: str, search_fields: List[str]) → List[T]`

Search records across multiple fields

**Parameters:**

- `self`
- `model_class` (Type[T])
- `search_term` (str)
- `search_fields` (List[str])

**Returns:** `List[T]`

---

##### `update(self, model_class: Type[T], record_id: int, data: Dict[str, Any]) → T`

Update existing record

**Parameters:**

- `self`
- `model_class` (Type[T])
- `record_id` (int)
- `data` (Dict[str, Any])

**Returns:** `T`

---


#### `DatabaseManager`

High-level database manager providing CRUD operations
and query functionality for PyArchInit-Mini models

**Methods:**

##### `__init__(self, connection: DatabaseConnection)`

Initializes the database manager by establishing a connection to the database and setting up the migration handler. This method ensures that the manager is ready to perform CRUD operations and manage schema migrations for PyArchInit-Mini models.

**Parameters:**

- `self`
- `connection` (DatabaseConnection)

---

##### `begin_transaction(self) → Session`

Begin a manual transaction

**Parameters:**

- `self`

**Returns:** `Session`

---

##### `bulk_create(self, model_class: Type[T], data_list: List[Dict[str, Any]]) → List[T]`

Create multiple records in a single transaction

**Parameters:**

- `self`
- `model_class` (Type[T])
- `data_list` (List[Dict[str, Any]])

**Returns:** `List[T]`

---

##### `commit_transaction(self, session: Session)`

Commit transaction

**Parameters:**

- `self`
- `session` (Session)

---

##### `count(self, model_class: Type[T], filters: Optional[Dict[str, Any]]) → int`

Count records with optional filters

**Parameters:**

- `self`
- `model_class` (Type[T])
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create(self, model_class: Type[T], data: Dict[str, Any]) → T`

Create a new record

**Parameters:**

- `self`
- `model_class` (Type[T])
- `data` (Dict[str, Any])

**Returns:** `T`

---

##### `delete(self, model_class: Type[T], record_id: int) → bool`

Delete record by ID

**Parameters:**

- `self`
- `model_class` (Type[T])
- `record_id` (int)

**Returns:** `bool`

---

##### `execute_raw_query(self, query: str, params: Optional[Dict])`

Execute raw SQL query

**Parameters:**

- `self`
- `query` (str)
- `params` (Optional[Dict])

---

##### `get_all(self, model_class: Type[T], offset: int, limit: int, order_by: Optional[str], filters: Optional[Dict[str, Any]]) → List[T]`

Get all records with optional filtering and pagination

**Parameters:**

- `self`
- `model_class` (Type[T])
- `offset` (int)
- `limit` (int)
- `order_by` (Optional[str])
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[T]`

---

##### `get_by_field(self, model_class: Type[T], field_name: str, value: Any) → Optional[T]`

Get record by specific field

**Parameters:**

- `self`
- `model_class` (Type[T])
- `field_name` (str)
- `value` (Any)

**Returns:** `Optional[T]`

---

##### `get_by_id(self, model_class: Type[T], record_id: int) → Optional[T]`

Get record by primary key

**Parameters:**

- `self`
- `model_class` (Type[T])
- `record_id` (int)

**Returns:** `Optional[T]`

---

##### `get_table_info(self, model_class: Type[T]) → Dict[str, Any]`

Get table metadata information

**Parameters:**

- `self`
- `model_class` (Type[T])

**Returns:** `Dict[str, Any]`

---

##### `rollback_transaction(self, session: Session)`

Rollback transaction

**Parameters:**

- `self`
- `session` (Session)

---

##### `run_migrations(self)`

Run all necessary database migrations

**Parameters:**

- `self`

---

##### `search(self, model_class: Type[T], search_term: str, search_fields: List[str]) → List[T]`

Search records across multiple fields

**Parameters:**

- `self`
- `model_class` (Type[T])
- `search_term` (str)
- `search_fields` (List[str])

**Returns:** `List[T]`

---

##### `update(self, model_class: Type[T], record_id: int, data: Dict[str, Any]) → T`

Update existing record

**Parameters:**

- `self`
- `model_class` (Type[T])
- `record_id` (int)
- `data` (Dict[str, Any])

**Returns:** `T`

---


#### `DatabaseManager`

High-level database manager providing CRUD operations
and query functionality for PyArchInit-Mini models

**Methods:**

##### `__init__(self, connection: DatabaseConnection)`

Initializes the database manager by establishing a connection to the database using the provided DatabaseConnection object. It also sets up the migration handler to manage database schema updates. This ensures the manager is ready to perform CRUD operations and handle migrations for PyArchInit-Mini models.

**Parameters:**

- `self`
- `connection` (DatabaseConnection)

---

##### `begin_transaction(self) → Session`

Begin a manual transaction

**Parameters:**

- `self`

**Returns:** `Session`

---

##### `bulk_create(self, model_class: Type[T], data_list: List[Dict[str, Any]]) → List[T]`

Create multiple records in a single transaction

**Parameters:**

- `self`
- `model_class` (Type[T])
- `data_list` (List[Dict[str, Any]])

**Returns:** `List[T]`

---

##### `commit_transaction(self, session: Session)`

Commit transaction

**Parameters:**

- `self`
- `session` (Session)

---

##### `count(self, model_class: Type[T], filters: Optional[Dict[str, Any]]) → int`

Count records with optional filters

**Parameters:**

- `self`
- `model_class` (Type[T])
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create(self, model_class: Type[T], data: Dict[str, Any]) → T`

Create a new record

**Parameters:**

- `self`
- `model_class` (Type[T])
- `data` (Dict[str, Any])

**Returns:** `T`

---

##### `delete(self, model_class: Type[T], record_id: int) → bool`

Delete record by ID

**Parameters:**

- `self`
- `model_class` (Type[T])
- `record_id` (int)

**Returns:** `bool`

---

##### `execute_raw_query(self, query: str, params: Optional[Dict])`

Execute raw SQL query

**Parameters:**

- `self`
- `query` (str)
- `params` (Optional[Dict])

---

##### `get_all(self, model_class: Type[T], offset: int, limit: int, order_by: Optional[str], filters: Optional[Dict[str, Any]]) → List[T]`

Get all records with optional filtering and pagination

**Parameters:**

- `self`
- `model_class` (Type[T])
- `offset` (int)
- `limit` (int)
- `order_by` (Optional[str])
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[T]`

---

##### `get_by_field(self, model_class: Type[T], field_name: str, value: Any) → Optional[T]`

Get record by specific field

**Parameters:**

- `self`
- `model_class` (Type[T])
- `field_name` (str)
- `value` (Any)

**Returns:** `Optional[T]`

---

##### `get_by_id(self, model_class: Type[T], record_id: int) → Optional[T]`

Get record by primary key

**Parameters:**

- `self`
- `model_class` (Type[T])
- `record_id` (int)

**Returns:** `Optional[T]`

---

##### `get_table_info(self, model_class: Type[T]) → Dict[str, Any]`

Get table metadata information

**Parameters:**

- `self`
- `model_class` (Type[T])

**Returns:** `Dict[str, Any]`

---

##### `rollback_transaction(self, session: Session)`

Rollback transaction

**Parameters:**

- `self`
- `session` (Session)

---

##### `run_migrations(self)`

Run all necessary database migrations

**Parameters:**

- `self`

---

##### `search(self, model_class: Type[T], search_term: str, search_fields: List[str]) → List[T]`

Search records across multiple fields

**Parameters:**

- `self`
- `model_class` (Type[T])
- `search_term` (str)
- `search_fields` (List[str])

**Returns:** `List[T]`

---

##### `update(self, model_class: Type[T], record_id: int, data: Dict[str, Any]) → T`

Update existing record

**Parameters:**

- `self`
- `model_class` (Type[T])
- `record_id` (int)
- `data` (Dict[str, Any])

**Returns:** `T`

---


#### `RecordNotFoundError`

Record not found error

**Inherits from:** `DatabaseError`


#### `RecordNotFoundError`

Record not found error

**Inherits from:** `DatabaseError`



\newpage


## Module: `pyarchinit_mini/database/migrations.py`

**File Path:** `pyarchinit_mini/database/migrations.py`

### Classes

#### `DatabaseMigrations`

Handle database schema migrations

**Methods:**

##### `__init__(self, db_manager)`

Initializes a new instance of the migration handler by associating it with a given database manager. This method stores references to both the database manager and its active connection for use in migration operations.

**Parameters:**

- `self`
- `db_manager`

---

##### `add_column_if_not_exists(self, table_name: str, column_name: str, column_type: str, default_value: str)`

Add a column to a table if it doesn't exist

**Parameters:**

- `self`
- `table_name` (str)
- `column_name` (str)
- `column_type` (str)
- `default_value` (str)

---

##### `check_column_exists(self, table_name: str, column_name: str) → bool`

Check if a column exists in a table

**Parameters:**

- `self`
- `table_name` (str)
- `column_name` (str)

**Returns:** `bool`

---

##### `check_migration_needed(self, table_name: str, required_columns: List[str]) → List[str]`

Check which columns are missing from a table

**Parameters:**

- `self`
- `table_name` (str)
- `required_columns` (List[str])

**Returns:** `List[str]`

---

##### `get_table_info(self, table_name: str) → Dict[str, Any]`

Get information about a table structure

**Parameters:**

- `self`
- `table_name` (str)

**Returns:** `Dict[str, Any]`

---

##### `migrate_all_tables(self)`

Run all necessary migrations

**Parameters:**

- `self`

---

##### `migrate_inventario_materiali_table(self)`

Migrate inventario_materiali_table to include all new fields

**Parameters:**

- `self`

---


#### `DatabaseMigrations`

Handle database schema migrations

**Methods:**

##### `__init__(self, db_manager)`

Initializes a new instance of the migration handler by accepting a database manager object. This method sets up internal references to both the database manager and its associated database connection, enabling subsequent schema migration operations.

**Parameters:**

- `self`
- `db_manager`

---

##### `add_column_if_not_exists(self, table_name: str, column_name: str, column_type: str, default_value: str)`

Add a column to a table if it doesn't exist

**Parameters:**

- `self`
- `table_name` (str)
- `column_name` (str)
- `column_type` (str)
- `default_value` (str)

---

##### `check_column_exists(self, table_name: str, column_name: str) → bool`

Check if a column exists in a table

**Parameters:**

- `self`
- `table_name` (str)
- `column_name` (str)

**Returns:** `bool`

---

##### `check_migration_needed(self, table_name: str, required_columns: List[str]) → List[str]`

Check which columns are missing from a table

**Parameters:**

- `self`
- `table_name` (str)
- `required_columns` (List[str])

**Returns:** `List[str]`

---

##### `get_table_info(self, table_name: str) → Dict[str, Any]`

Get information about a table structure

**Parameters:**

- `self`
- `table_name` (str)

**Returns:** `Dict[str, Any]`

---

##### `migrate_all_tables(self)`

Run all necessary migrations

**Parameters:**

- `self`

---

##### `migrate_inventario_materiali_table(self)`

Migrate inventario_materiali_table to include all new fields

**Parameters:**

- `self`

---



\newpage


## Module: `pyarchinit_mini/database/postgres_installer.py`

**File Path:** `pyarchinit_mini/database/postgres_installer.py`

### Classes

#### `PostgreSQLInstaller`

Manages PostgreSQL installation on different platforms

**Methods:**

##### `__init__(self)`

Initializes a new instance of the PostgreSQL management class by detecting the current operating system and system architecture. It also sets default values for the PostgreSQL data directory, port, username, and password, which are used for managing PostgreSQL installations.

**Parameters:**

- `self`

---

##### `check_postgres_installed(self) → bool`

Check if PostgreSQL is already installed and accessible

**Parameters:**

- `self`

**Returns:** `bool`

---

##### `create_pyarchinit_database(self, connection_params: Dict[str, str]) → Dict[str, Any]`

Create PyArchInit database and user

**Parameters:**

- `self`
- `connection_params` (Dict[str, str])

**Returns:** `Dict[str, Any]`

---

##### `get_connection_info(self) → Dict[str, Any]`

Get default connection information

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `get_postgres_version(self) → Optional[str]`

Get installed PostgreSQL version

**Parameters:**

- `self`

**Returns:** `Optional[str]`

---

##### `install_postgres(self) → Dict[str, Any]`

Install PostgreSQL based on the current platform

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `install_postgres_linux(self) → Dict[str, Any]`

Install PostgreSQL on Linux

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `install_postgres_macos(self) → Dict[str, Any]`

Install PostgreSQL on macOS using Homebrew

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `install_postgres_windows(self) → Dict[str, Any]`

Install PostgreSQL on Windows

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---


#### `PostgreSQLInstaller`

Manages PostgreSQL installation on different platforms

**Methods:**

##### `__init__(self)`

Initializes the PostgreSQL manager by detecting the current operating system and architecture, and setting default configuration parameters such as the data directory, port, user, and password. This method prepares the instance for subsequent PostgreSQL management operations across different platforms. It is called automatically when a new instance of the class is created.

**Parameters:**

- `self`

---

##### `check_postgres_installed(self) → bool`

Check if PostgreSQL is already installed and accessible

**Parameters:**

- `self`

**Returns:** `bool`

---

##### `create_pyarchinit_database(self, connection_params: Dict[str, str]) → Dict[str, Any]`

Create PyArchInit database and user

**Parameters:**

- `self`
- `connection_params` (Dict[str, str])

**Returns:** `Dict[str, Any]`

---

##### `get_connection_info(self) → Dict[str, Any]`

Get default connection information

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `get_postgres_version(self) → Optional[str]`

Get installed PostgreSQL version

**Parameters:**

- `self`

**Returns:** `Optional[str]`

---

##### `install_postgres(self) → Dict[str, Any]`

Install PostgreSQL based on the current platform

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `install_postgres_linux(self) → Dict[str, Any]`

Install PostgreSQL on Linux

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `install_postgres_macos(self) → Dict[str, Any]`

Install PostgreSQL on macOS using Homebrew

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `install_postgres_windows(self) → Dict[str, Any]`

Install PostgreSQL on Windows

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---


#### `PostgreSQLInstaller`

Manages PostgreSQL installation on different platforms

**Methods:**

##### `__init__(self)`

Initializes the PostgreSQL manager by detecting the current operating system and machine architecture. It also sets default values for PostgreSQL data directory, port, user, and password. This method prepares the instance for further management of PostgreSQL installation and configuration.

**Parameters:**

- `self`

---

##### `check_postgres_installed(self) → bool`

Check if PostgreSQL is already installed and accessible

**Parameters:**

- `self`

**Returns:** `bool`

---

##### `create_pyarchinit_database(self, connection_params: Dict[str, str]) → Dict[str, Any]`

Create PyArchInit database and user

**Parameters:**

- `self`
- `connection_params` (Dict[str, str])

**Returns:** `Dict[str, Any]`

---

##### `get_connection_info(self) → Dict[str, Any]`

Get default connection information

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `get_postgres_version(self) → Optional[str]`

Get installed PostgreSQL version

**Parameters:**

- `self`

**Returns:** `Optional[str]`

---

##### `install_postgres(self) → Dict[str, Any]`

Install PostgreSQL based on the current platform

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `install_postgres_linux(self) → Dict[str, Any]`

Install PostgreSQL on Linux

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `install_postgres_macos(self) → Dict[str, Any]`

Install PostgreSQL on macOS using Homebrew

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `install_postgres_windows(self) → Dict[str, Any]`

Install PostgreSQL on Windows

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---



\newpage


## Module: `pyarchinit_mini/database/schemas.py`

**File Path:** `pyarchinit_mini/database/schemas.py`

### Classes

#### `DatabaseSchema`

Utilities for database schema management and migrations

**Methods:**

##### `__init__(self, connection: DatabaseConnection)`

Initializes a new instance of the schema management utility by establishing a connection to the specified database. This method stores the provided DatabaseConnection object for use in subsequent schema operations.

**Parameters:**

- `self`
- `connection` (DatabaseConnection)

---

##### `backup_schema(self) → str`

Generate SQL script to backup current schema structure

**Parameters:**

- `self`

**Returns:** `str`

---

##### `check_schema_compatibility(self) → Dict[str, Any]`

Check if current database schema is compatible with models

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `check_table_exists(self, table_name: str) → bool`

Check if a table exists in the database

**Parameters:**

- `self`
- `table_name` (str)

**Returns:** `bool`

---

##### `create_all_tables(self)`

Create all tables defined in models

**Parameters:**

- `self`

---

##### `create_indexes(self)`

Create recommended indexes for performance

**Parameters:**

- `self`

---

##### `get_database_stats(self) → Dict[str, Any]`

Get database statistics

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `get_table_columns(self, table_name: str) → List[Dict[str, Any]]`

Get column information for a table

**Parameters:**

- `self`
- `table_name` (str)

**Returns:** `List[Dict[str, Any]]`

---

##### `get_table_list(self) → List[str]`

Get list of all tables in the database

**Parameters:**

- `self`

**Returns:** `List[str]`

---


#### `DatabaseSchema`

Utilities for database schema management and migrations

**Methods:**

##### `__init__(self, connection: DatabaseConnection)`

Initializes a new instance of the class with the given database connection.  
Stores the provided DatabaseConnection object for use in subsequent schema management and migration operations.

**Parameters:**

- `self`
- `connection` (DatabaseConnection)

---

##### `backup_schema(self) → str`

Generate SQL script to backup current schema structure

**Parameters:**

- `self`

**Returns:** `str`

---

##### `check_schema_compatibility(self) → Dict[str, Any]`

Check if current database schema is compatible with models

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `check_table_exists(self, table_name: str) → bool`

Check if a table exists in the database

**Parameters:**

- `self`
- `table_name` (str)

**Returns:** `bool`

---

##### `create_all_tables(self)`

Create all tables defined in models

**Parameters:**

- `self`

---

##### `create_indexes(self)`

Create recommended indexes for performance

**Parameters:**

- `self`

---

##### `get_database_stats(self) → Dict[str, Any]`

Get database statistics

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `get_table_columns(self, table_name: str) → List[Dict[str, Any]]`

Get column information for a table

**Parameters:**

- `self`
- `table_name` (str)

**Returns:** `List[Dict[str, Any]]`

---

##### `get_table_list(self) → List[str]`

Get list of all tables in the database

**Parameters:**

- `self`

**Returns:** `List[str]`

---


#### `DatabaseSchema`

Utilities for database schema management and migrations

**Methods:**

##### `__init__(self, connection: DatabaseConnection)`

Initializes a new instance of the class with the provided database connection.  
This method assigns the given DatabaseConnection object to the instance for use in schema management and migration operations.

**Parameters:**

- `self`
- `connection` (DatabaseConnection)

---

##### `backup_schema(self) → str`

Generate SQL script to backup current schema structure

**Parameters:**

- `self`

**Returns:** `str`

---

##### `check_schema_compatibility(self) → Dict[str, Any]`

Check if current database schema is compatible with models

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `check_table_exists(self, table_name: str) → bool`

Check if a table exists in the database

**Parameters:**

- `self`
- `table_name` (str)

**Returns:** `bool`

---

##### `create_all_tables(self)`

Create all tables defined in models

**Parameters:**

- `self`

---

##### `create_indexes(self)`

Create recommended indexes for performance

**Parameters:**

- `self`

---

##### `get_database_stats(self) → Dict[str, Any]`

Get database statistics

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `get_table_columns(self, table_name: str) → List[Dict[str, Any]]`

Get column information for a table

**Parameters:**

- `self`
- `table_name` (str)

**Returns:** `List[Dict[str, Any]]`

---

##### `get_table_list(self) → List[str]`

Get list of all tables in the database

**Parameters:**

- `self`

**Returns:** `List[str]`

---



\newpage


## Module: `pyarchinit_mini/dto/__init__.py`

**File Path:** `pyarchinit_mini/dto/__init__.py`


\newpage


## Module: `pyarchinit_mini/dto/inventario_dto.py`

**File Path:** `pyarchinit_mini/dto/inventario_dto.py`

### Classes

#### `InventarioDTO`

Data Transfer Object for Inventario (Material Inventory) data
This class holds inventory data without SQLAlchemy session dependencies

**Decorators:** `dataclass`

**Methods:**

##### `display_name(self) → str`

Get display name for the inventory item

**Parameters:**

- `self`

**Returns:** `str`

**Decorators:** `property`

---

##### `from_model(cls, inventario_model) → InventarioDTO`

Create DTO from SQLAlchemy model instance

**Parameters:**

- `cls`
- `inventario_model`

**Returns:** `InventarioDTO`

**Decorators:** `classmethod`

---

##### `to_dict(self) → dict`

Convert DTO to dictionary

**Parameters:**

- `self`

**Returns:** `dict`

---


#### `InventarioDTO`

Data Transfer Object for Inventario (Material Inventory) data
This class holds inventory data without SQLAlchemy session dependencies

**Decorators:** `dataclass`

**Methods:**

##### `display_name(self) → str`

Get display name for the inventory item

**Parameters:**

- `self`

**Returns:** `str`

**Decorators:** `property`

---

##### `from_model(cls, inventario_model) → InventarioDTO`

Create DTO from SQLAlchemy model instance

**Parameters:**

- `cls`
- `inventario_model`

**Returns:** `InventarioDTO`

**Decorators:** `classmethod`

---

##### `to_dict(self) → dict`

Convert DTO to dictionary

**Parameters:**

- `self`

**Returns:** `dict`

---


#### `InventarioDTO`

Data Transfer Object for Inventario (Material Inventory) data
This class holds inventory data without SQLAlchemy session dependencies

**Decorators:** `dataclass`

**Methods:**

##### `display_name(self) → str`

Get display name for the inventory item

**Parameters:**

- `self`

**Returns:** `str`

**Decorators:** `property`

---

##### `from_model(cls, inventario_model) → InventarioDTO`

Create DTO from SQLAlchemy model instance

**Parameters:**

- `cls`
- `inventario_model`

**Returns:** `InventarioDTO`

**Decorators:** `classmethod`

---

##### `to_dict(self) → dict`

Convert DTO to dictionary

**Parameters:**

- `self`

**Returns:** `dict`

---



\newpage


## Module: `pyarchinit_mini/dto/site_dto.py`

**File Path:** `pyarchinit_mini/dto/site_dto.py`

### Classes

#### `SiteDTO`

Data Transfer Object for Site data
This class holds site data without SQLAlchemy session dependencies

**Decorators:** `dataclass`

**Methods:**

##### `display_name(self) → str`

Get display name for the site

**Parameters:**

- `self`

**Returns:** `str`

**Decorators:** `property`

---

##### `from_model(cls, site_model) → SiteDTO`

Create DTO from SQLAlchemy model instance

**Parameters:**

- `cls`
- `site_model`

**Returns:** `SiteDTO`

**Decorators:** `classmethod`

---

##### `to_dict(self) → dict`

Convert DTO to dictionary

**Parameters:**

- `self`

**Returns:** `dict`

---


#### `SiteDTO`

Data Transfer Object for Site data
This class holds site data without SQLAlchemy session dependencies

**Decorators:** `dataclass`

**Methods:**

##### `display_name(self) → str`

Get display name for the site

**Parameters:**

- `self`

**Returns:** `str`

**Decorators:** `property`

---

##### `from_model(cls, site_model) → SiteDTO`

Create DTO from SQLAlchemy model instance

**Parameters:**

- `cls`
- `site_model`

**Returns:** `SiteDTO`

**Decorators:** `classmethod`

---

##### `to_dict(self) → dict`

Convert DTO to dictionary

**Parameters:**

- `self`

**Returns:** `dict`

---


#### `SiteDTO`

Data Transfer Object for Site data
This class holds site data without SQLAlchemy session dependencies

**Decorators:** `dataclass`

**Methods:**

##### `display_name(self) → str`

Get display name for the site

**Parameters:**

- `self`

**Returns:** `str`

**Decorators:** `property`

---

##### `from_model(cls, site_model) → SiteDTO`

Create DTO from SQLAlchemy model instance

**Parameters:**

- `cls`
- `site_model`

**Returns:** `SiteDTO`

**Decorators:** `classmethod`

---

##### `to_dict(self) → dict`

Convert DTO to dictionary

**Parameters:**

- `self`

**Returns:** `dict`

---



\newpage


## Module: `pyarchinit_mini/dto/us_dto.py`

**File Path:** `pyarchinit_mini/dto/us_dto.py`

### Classes

#### `USDTO`

Data Transfer Object for US (Stratigraphic Unit) data
This class holds US data without SQLAlchemy session dependencies

**Decorators:** `dataclass`

**Methods:**

##### `display_name(self) → str`

Get display name for the US

**Parameters:**

- `self`

**Returns:** `str`

**Decorators:** `property`

---

##### `from_model(cls, us_model) → USDTO`

Create DTO from SQLAlchemy model instance

**Parameters:**

- `cls`
- `us_model`

**Returns:** `USDTO`

**Decorators:** `classmethod`

---

##### `to_dict(self) → dict`

Convert DTO to dictionary

**Parameters:**

- `self`

**Returns:** `dict`

---


#### `USDTO`

Data Transfer Object for US (Stratigraphic Unit) data
This class holds US data without SQLAlchemy session dependencies

**Decorators:** `dataclass`

**Methods:**

##### `display_name(self) → str`

Get display name for the US

**Parameters:**

- `self`

**Returns:** `str`

**Decorators:** `property`

---

##### `from_model(cls, us_model) → USDTO`

Create DTO from SQLAlchemy model instance

**Parameters:**

- `cls`
- `us_model`

**Returns:** `USDTO`

**Decorators:** `classmethod`

---

##### `to_dict(self) → dict`

Convert DTO to dictionary

**Parameters:**

- `self`

**Returns:** `dict`

---


#### `USDTO`

Data Transfer Object for US (Stratigraphic Unit) data
This class holds US data without SQLAlchemy session dependencies

**Decorators:** `dataclass`

**Methods:**

##### `display_name(self) → str`

Get display name for the US

**Parameters:**

- `self`

**Returns:** `str`

**Decorators:** `property`

---

##### `from_model(cls, us_model) → USDTO`

Create DTO from SQLAlchemy model instance

**Parameters:**

- `cls`
- `us_model`

**Returns:** `USDTO`

**Decorators:** `classmethod`

---

##### `to_dict(self) → dict`

Convert DTO to dictionary

**Parameters:**

- `self`

**Returns:** `dict`

---



\newpage


## Module: `pyarchinit_mini/exceptions.py`

**File Path:** `pyarchinit_mini/exceptions.py`

### Classes

#### `ConfigurationError`

Configuration errors

**Inherits from:** `PyArchInitError`


#### `ConfigurationError`

Configuration errors

**Inherits from:** `PyArchInitError`


#### `ConfigurationError`

Configuration errors

**Inherits from:** `PyArchInitError`


#### `DatabaseError`

Database related errors

**Inherits from:** `PyArchInitError`


#### `DatabaseError`

Database related errors

**Inherits from:** `PyArchInitError`


#### `DatabaseError`

Database related errors

**Inherits from:** `PyArchInitError`


#### `PyArchInitError`

Base exception for PyArchInit-Mini

**Inherits from:** `Exception`


#### `PyArchInitError`

Base exception for PyArchInit-Mini

**Inherits from:** `Exception`


#### `PyArchInitError`

Base exception for PyArchInit-Mini

**Inherits from:** `Exception`


#### `ServiceError`

Service layer errors

**Inherits from:** `PyArchInitError`


#### `ServiceError`

Service layer errors

**Inherits from:** `PyArchInitError`


#### `ServiceError`

Service layer errors

**Inherits from:** `PyArchInitError`


#### `ValidationError`

Data validation errors

**Inherits from:** `PyArchInitError`


#### `ValidationError`

Data validation errors

**Inherits from:** `PyArchInitError`


#### `ValidationError`

Data validation errors

**Inherits from:** `PyArchInitError`



\newpage


## Module: `pyarchinit_mini/harris_matrix/__init__.py`

**File Path:** `pyarchinit_mini/harris_matrix/__init__.py`


\newpage


## Module: `pyarchinit_mini/harris_matrix/enhanced_visualizer.py`

**File Path:** `pyarchinit_mini/harris_matrix/enhanced_visualizer.py`

### Classes

#### `EnhancedHarrisMatrixVisualizer`

Enhanced Harris Matrix visualizer using Graphviz for hierarchical orthogonal layout
Supports area/period/phase grouping and all stratigraphic relationships

**Methods:**

##### `__init__(self)`

**__init__**

Initializes the visualizer by configuring default styles and properties for stratigraphic relationships, area color assignments, and period shapes used in Harris Matrix diagrams. Sets up dictionaries that define the visual representation (such as color, line style, and arrowhead type) for different relationship types, as well as color codes for excavation areas and shapes for archaeological periods. These configurations are used throughout the visualizer to ensure consistent and meaningful graphical output.

**Parameters:**

- `self`

---

##### `analyze_matrix_statistics(self, graph: nx.DiGraph) → Dict[str, Any]`

Analyze Harris Matrix and provide statistics

**Parameters:**

- `self`
- `graph` (nx.DiGraph)

**Returns:** `Dict[str, Any]`

---

##### `create_graphviz_matrix(self, graph: nx.DiGraph, grouping: str, output_format: str, output_path: Optional[str]) → str`

Create Harris Matrix using Graphviz with hierarchical orthogonal layout

Args:
    graph: NetworkX directed graph
    grouping: 'none', 'area', 'period', 'phase', or 'area_period'
    output_format: 'png', 'svg', 'pdf', 'dot'
    output_path: Optional output file path
    
Returns:
    Path to generated file or DOT source

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `grouping` (str)
- `output_format` (str)
- `output_path` (Optional[str])

**Returns:** `str`

---

##### `create_relationship_legend(self, output_path: Optional[str]) → str`

Create a legend showing all relationship types and their visual styles

**Parameters:**

- `self`
- `output_path` (Optional[str])

**Returns:** `str`

---

##### `create_temporal_matrix(self, graph: nx.DiGraph, output_path: Optional[str]) → str`

Create Harris Matrix with temporal/chronological ordering
Groups by periods and phases with hierarchical display

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `output_path` (Optional[str])

**Returns:** `str`

---

##### `export_multiple_formats(self, graph: nx.DiGraph, base_filename: str, grouping: str) → Dict[str, str]`

Export Harris Matrix in multiple formats

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `base_filename` (str)
- `grouping` (str)

**Returns:** `Dict[str, str]`

---



\newpage


## Module: `pyarchinit_mini/harris_matrix/matrix_generator.py`

**File Path:** `pyarchinit_mini/harris_matrix/matrix_generator.py`

### Classes

#### `HarrisMatrixGenerator`

Generates Harris Matrix from stratigraphic relationships

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the HarrisMatrixGenerator class. This constructor sets up the generator with the provided database manager for accessing stratigraphic data and an optional US service for additional context or functionality.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `add_relationship(self, site_name: str, us_from: int, us_to: int, relationship_type: str, certainty: str, description: str) → bool`

Add a new stratigraphic relationship

Args:
    site_name: Site name
    us_from: US number (from)
    us_to: US number (to)
    relationship_type: Type of relationship
    certainty: Certainty level
    description: Optional description
    
Returns:
    True if successful

**Parameters:**

- `self`
- `site_name` (str)
- `us_from` (int)
- `us_to` (int)
- `relationship_type` (str)
- `certainty` (str)
- `description` (str)

**Returns:** `bool`

---

##### `generate_matrix(self, site_name: str, area: Optional[str]) → nx.DiGraph`

Generate Harris Matrix graph from site relationships

Args:
    site_name: Site name
    area: Optional area filter
    
Returns:
    NetworkX directed graph representing the Harris Matrix

**Parameters:**

- `self`
- `site_name` (str)
- `area` (Optional[str])

**Returns:** `nx.DiGraph`

---

##### `get_matrix_levels(self, graph: nx.DiGraph) → Dict[int, List[int]]`

Get topological levels for matrix layout

Returns:
    Dictionary mapping level number to list of US numbers

**Parameters:**

- `self`
- `graph` (nx.DiGraph)

**Returns:** `Dict[int, List[int]]`

---

##### `get_matrix_statistics(self, graph: nx.DiGraph) → Dict[str, Any]`

Get statistics about the Harris Matrix

**Parameters:**

- `self`
- `graph` (nx.DiGraph)

**Returns:** `Dict[str, Any]`

---


#### `HarrisMatrixGenerator`

Generates Harris Matrix from stratigraphic relationships

**Methods:**

##### `__init__(self, db_manager: DatabaseManager, us_service)`

Initializes a new instance of the class responsible for generating Harris Matrices from stratigraphic relationships. This constructor sets up the required database manager for data access and optionally accepts a unit stratigraphy service for additional functionality. It prepares the class for subsequent matrix generation operations.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)
- `us_service`

---

##### `add_relationship(self, site_name: str, us_from: int, us_to: int, relationship_type: str, certainty: str, description: str) → bool`

Add a new stratigraphic relationship

Args:
    site_name: Site name
    us_from: US number (from)
    us_to: US number (to)
    relationship_type: Type of relationship
    certainty: Certainty level
    description: Optional description
    
Returns:
    True if successful

**Parameters:**

- `self`
- `site_name` (str)
- `us_from` (int)
- `us_to` (int)
- `relationship_type` (str)
- `certainty` (str)
- `description` (str)

**Returns:** `bool`

---

##### `generate_matrix(self, site_name: str, area: Optional[str]) → nx.DiGraph`

Generate Harris Matrix graph from site relationships

Args:
    site_name: Site name
    area: Optional area filter
    
Returns:
    NetworkX directed graph representing the Harris Matrix

**Parameters:**

- `self`
- `site_name` (str)
- `area` (Optional[str])

**Returns:** `nx.DiGraph`

---

##### `get_matrix_levels(self, graph: nx.DiGraph) → Dict[int, List[int]]`

Get topological levels for matrix layout

Returns:
    Dictionary mapping level number to list of US numbers

**Parameters:**

- `self`
- `graph` (nx.DiGraph)

**Returns:** `Dict[int, List[int]]`

---

##### `get_matrix_statistics(self, graph: nx.DiGraph) → Dict[str, Any]`

Get statistics about the Harris Matrix

**Parameters:**

- `self`
- `graph` (nx.DiGraph)

**Returns:** `Dict[str, Any]`

---


#### `HarrisMatrixGenerator`

Generates Harris Matrix from stratigraphic relationships

**Methods:**

##### `__init__(self, db_manager: DatabaseManager, us_service)`

Initializes the HarrisMatrixGenerator class by setting up the required database manager and an optional stratigraphic unit service. This method prepares the instance for generating Harris Matrices by establishing the necessary connections to data sources.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)
- `us_service`

---

##### `add_relationship(self, site_name: str, us_from: int, us_to: int, relationship_type: str, certainty: str, description: str) → bool`

Add a new stratigraphic relationship

Args:
    site_name: Site name
    us_from: US number (from)
    us_to: US number (to)
    relationship_type: Type of relationship
    certainty: Certainty level
    description: Optional description
    
Returns:
    True if successful

**Parameters:**

- `self`
- `site_name` (str)
- `us_from` (int)
- `us_to` (int)
- `relationship_type` (str)
- `certainty` (str)
- `description` (str)

**Returns:** `bool`

---

##### `generate_matrix(self, site_name: str, area: Optional[str]) → nx.DiGraph`

Generate Harris Matrix graph from site relationships

Args:
    site_name: Site name
    area: Optional area filter
    
Returns:
    NetworkX directed graph representing the Harris Matrix

**Parameters:**

- `self`
- `site_name` (str)
- `area` (Optional[str])

**Returns:** `nx.DiGraph`

---

##### `get_matrix_levels(self, graph: nx.DiGraph) → Dict[int, List[int]]`

Get topological levels for matrix layout

Returns:
    Dictionary mapping level number to list of US numbers

**Parameters:**

- `self`
- `graph` (nx.DiGraph)

**Returns:** `Dict[int, List[int]]`

---

##### `get_matrix_statistics(self, graph: nx.DiGraph) → Dict[str, Any]`

Get statistics about the Harris Matrix

**Parameters:**

- `self`
- `graph` (nx.DiGraph)

**Returns:** `Dict[str, Any]`

---



\newpage


## Module: `pyarchinit_mini/harris_matrix/matrix_visualizer.py`

**File Path:** `pyarchinit_mini/harris_matrix/matrix_visualizer.py`

### Classes

#### `MatrixVisualizer`

Visualizes Harris Matrix using different rendering methods

**Methods:**

##### `__init__(self)`

Initializes the visualizer with a set of default styling parameters for rendering Harris Matrices. This includes node dimensions, spacing, font size, and color schemes for various matrix elements, ensuring consistent visualization across different rendering methods.

**Parameters:**

- `self`

---

##### `create_interactive_html(self, graph: nx.DiGraph, levels: Dict[int, List[int]]) → str`

Create interactive HTML visualization using D3.js or similar

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `levels` (Dict[int, List[int]])

**Returns:** `str`

---

##### `export_to_formats(self, graph: nx.DiGraph, levels: Dict[int, List[int]], base_filename: str) → Dict[str, str]`

Export Harris Matrix to multiple formats

Returns:
    Dictionary mapping format to file path

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `levels` (Dict[int, List[int]])
- `base_filename` (str)

**Returns:** `Dict[str, str]`

---

##### `render_graphviz(self, graph: nx.DiGraph, output_path: Optional[str]) → str`

Render Harris Matrix using Graphviz for better layouts

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `output_path` (Optional[str])

**Returns:** `str`

---

##### `render_matplotlib(self, graph: nx.DiGraph, levels: Dict[int, List[int]], output_path: Optional[str], style: Optional[Dict]) → str`

Render Harris Matrix using matplotlib

Args:
    graph: NetworkX graph
    levels: Matrix levels from generator
    output_path: Optional file path to save
    style: Optional style overrides
    
Returns:
    Base64 encoded image string

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `levels` (Dict[int, List[int]])
- `output_path` (Optional[str])
- `style` (Optional[Dict])

**Returns:** `str`

---


#### `MatrixVisualizer`

Visualizes Harris Matrix using different rendering methods

**Methods:**

##### `__init__(self)`

Initializes a new instance of the visualizer with default style settings for rendering Harris Matrix diagrams. This method defines standard dimensions, spacing, font size, and color schemes to ensure consistent visualization appearance across different rendering methods. These default styles can later be customized or overridden as needed during rendering.

**Parameters:**

- `self`

---

##### `create_interactive_html(self, graph: nx.DiGraph, levels: Dict[int, List[int]]) → str`

Create interactive HTML visualization using D3.js or similar

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `levels` (Dict[int, List[int]])

**Returns:** `str`

---

##### `export_to_formats(self, graph: nx.DiGraph, levels: Dict[int, List[int]], base_filename: str) → Dict[str, str]`

Export Harris Matrix to multiple formats

Returns:
    Dictionary mapping format to file path

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `levels` (Dict[int, List[int]])
- `base_filename` (str)

**Returns:** `Dict[str, str]`

---

##### `render_graphviz(self, graph: nx.DiGraph, output_path: Optional[str]) → str`

Render Harris Matrix using Graphviz for better layouts

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `output_path` (Optional[str])

**Returns:** `str`

---

##### `render_matplotlib(self, graph: nx.DiGraph, levels: Dict[int, List[int]], output_path: Optional[str], style: Optional[Dict]) → str`

Render Harris Matrix using matplotlib

Args:
    graph: NetworkX graph
    levels: Matrix levels from generator
    output_path: Optional file path to save
    style: Optional style overrides
    
Returns:
    Base64 encoded image string

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `levels` (Dict[int, List[int]])
- `output_path` (Optional[str])
- `style` (Optional[Dict])

**Returns:** `str`

---


#### `MatrixVisualizer`

Visualizes Harris Matrix using different rendering methods

**Methods:**

##### `__init__(self)`

Initializes a new instance of the Harris Matrix visualizer with a set of default visualization styles and parameters. This includes default node dimensions, spacing, font size, and color schemes for various elements of the Harris Matrix diagram. These defaults are used unless overridden by custom style definitions during rendering.

**Parameters:**

- `self`

---

##### `create_interactive_html(self, graph: nx.DiGraph, levels: Dict[int, List[int]]) → str`

Create interactive HTML visualization using D3.js or similar

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `levels` (Dict[int, List[int]])

**Returns:** `str`

---

##### `export_to_formats(self, graph: nx.DiGraph, levels: Dict[int, List[int]], base_filename: str) → Dict[str, str]`

Export Harris Matrix to multiple formats

Returns:
    Dictionary mapping format to file path

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `levels` (Dict[int, List[int]])
- `base_filename` (str)

**Returns:** `Dict[str, str]`

---

##### `render_graphviz(self, graph: nx.DiGraph, output_path: Optional[str]) → str`

Render Harris Matrix using Graphviz for better layouts

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `output_path` (Optional[str])

**Returns:** `str`

---

##### `render_matplotlib(self, graph: nx.DiGraph, levels: Dict[int, List[int]], output_path: Optional[str], style: Optional[Dict]) → str`

Render Harris Matrix using matplotlib

Args:
    graph: NetworkX graph
    levels: Matrix levels from generator
    output_path: Optional file path to save
    style: Optional style overrides
    
Returns:
    Base64 encoded image string

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `levels` (Dict[int, List[int]])
- `output_path` (Optional[str])
- `style` (Optional[Dict])

**Returns:** `str`

---



\newpage


## Module: `pyarchinit_mini/harris_matrix/pyarchinit_visualizer.py`

**File Path:** `pyarchinit_mini/harris_matrix/pyarchinit_visualizer.py`

### Classes

#### `PyArchInitMatrixVisualizer`

Harris Matrix visualizer that replicates PyArchInit plugin behavior
Uses Graphviz with hierarchical orthogonal layout and period/area grouping

**Methods:**

##### `__init__(self)`

Initializes a new instance of the Harris Matrix visualizer with a predefined set of default visualization settings. These settings control the appearance and layout of the matrix, including resolution, node and edge styles, grouping options, and legend visibility, to replicate the behavior of the PyArchInit plugin using Graphviz.

**Parameters:**

- `self`

---

##### `create_matrix(self, graph: nx.DiGraph, grouping: str, settings: Optional[Dict], output_path: Optional[str]) → str`

Create Harris Matrix using PyArchInit approach

Args:
    graph: NetworkX directed graph with US nodes and relationships
    grouping: 'period_area', 'period', 'area', 'none'
    settings: Optional style settings override
    output_path: Optional output file path
    
Returns:
    Path to generated file

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `grouping` (str)
- `settings` (Optional[Dict])
- `output_path` (Optional[str])

**Returns:** `str`

---

##### `export_multiple_formats(self, graph: nx.DiGraph, base_filename: str, grouping: str) → Dict[str, str]`

Export matrix in multiple formats

**Parameters:**

- `self`
- `graph` (nx.DiGraph)
- `base_filename` (str)
- `grouping` (str)

**Returns:** `Dict[str, str]`

---



\newpage


## Module: `pyarchinit_mini/media_manager/__init__.py`

**File Path:** `pyarchinit_mini/media_manager/__init__.py`


\newpage


## Module: `pyarchinit_mini/media_manager/media_handler.py`

**File Path:** `pyarchinit_mini/media_manager/media_handler.py`

### Classes

#### `MediaHandler`

Handles media file operations, storage, and organization

**Methods:**

##### `__init__(self, base_media_path: str)`

Initializes the media handler by setting up the base directory for media storage. Creates the main media directory and standard subdirectories for images, documents, videos, and thumbnails if they do not already exist. This ensures an organized file structure for subsequent media operations.

**Parameters:**

- `self`
- `base_media_path` (str)

---

##### `create_media_archive(self, entity_type: str, entity_id: int, archive_path: str) → bool`

Create ZIP archive of all media for an entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)
- `archive_path` (str)

**Returns:** `bool`

---

##### `delete_file(self, media_filename: str, entity_type: str, entity_id: int) → bool`

Delete media file and its thumbnails

**Parameters:**

- `self`
- `media_filename` (str)
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `bool`

---

##### `get_file_path(self, media_filename: str, entity_type: str, entity_id: int) → Optional[Path]`

Get full path to stored media file

**Parameters:**

- `self`
- `media_filename` (str)
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `Optional[Path]`

---

##### `get_media_info(self, file_path: Path) → Dict[str, Any]`

Get detailed media information

**Parameters:**

- `self`
- `file_path` (Path)

**Returns:** `Dict[str, Any]`

---

##### `organize_media_by_entity(self, entity_type: str, entity_id: int) → List[Dict[str, Any]]`

Get all media files for a specific entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `List[Dict[str, Any]]`

---

##### `store_file(self, file_path: str, entity_type: str, entity_id: int, description: str, tags: str, author: str) → Dict[str, Any]`

Store a media file and return metadata

Args:
    file_path: Source file path
    entity_type: Type of entity (site, us, inventario)
    entity_id: Entity ID
    description: File description
    tags: Tags for the file
    author: Author/photographer
    
Returns:
    Dictionary with file metadata

**Parameters:**

- `self`
- `file_path` (str)
- `entity_type` (str)
- `entity_id` (int)
- `description` (str)
- `tags` (str)
- `author` (str)

**Returns:** `Dict[str, Any]`

---


#### `MediaHandler`

Handles media file operations, storage, and organization

**Methods:**

##### `__init__(self, base_media_path: str)`

Initializes the media file handler by setting up the base media directory and creating the necessary subdirectories for images, documents, videos, and thumbnails. If the specified base directory or any subdirectory does not exist, it is created automatically. This ensures that the required folder structure is in place for subsequent media file operations.

**Parameters:**

- `self`
- `base_media_path` (str)

---

##### `create_media_archive(self, entity_type: str, entity_id: int, archive_path: str) → bool`

Create ZIP archive of all media for an entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)
- `archive_path` (str)

**Returns:** `bool`

---

##### `delete_file(self, media_filename: str, entity_type: str, entity_id: int) → bool`

Delete media file and its thumbnails

**Parameters:**

- `self`
- `media_filename` (str)
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `bool`

---

##### `get_file_path(self, media_filename: str, entity_type: str, entity_id: int) → Optional[Path]`

Get full path to stored media file

**Parameters:**

- `self`
- `media_filename` (str)
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `Optional[Path]`

---

##### `get_media_info(self, file_path: Path) → Dict[str, Any]`

Get detailed media information

**Parameters:**

- `self`
- `file_path` (Path)

**Returns:** `Dict[str, Any]`

---

##### `organize_media_by_entity(self, entity_type: str, entity_id: int) → List[Dict[str, Any]]`

Get all media files for a specific entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `List[Dict[str, Any]]`

---

##### `store_file(self, file_path: str, entity_type: str, entity_id: int, description: str, tags: str, author: str) → Dict[str, Any]`

Store a media file and return metadata

Args:
    file_path: Source file path
    entity_type: Type of entity (site, us, inventario)
    entity_id: Entity ID
    description: File description
    tags: Tags for the file
    author: Author/photographer
    
Returns:
    Dictionary with file metadata

**Parameters:**

- `self`
- `file_path` (str)
- `entity_type` (str)
- `entity_id` (int)
- `description` (str)
- `tags` (str)
- `author` (str)

**Returns:** `Dict[str, Any]`

---


#### `MediaHandler`

Handles media file operations, storage, and organization

**Methods:**

##### `__init__(self, base_media_path: str)`

Initializes the media file handler by setting up the base media directory and creating standardized subdirectories for images, documents, videos, and thumbnails. Ensures that all required folders exist for organized storage and future media file operations. The base path can be customized via the `base_media_path` parameter.

**Parameters:**

- `self`
- `base_media_path` (str)

---

##### `create_media_archive(self, entity_type: str, entity_id: int, archive_path: str) → bool`

Create ZIP archive of all media for an entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)
- `archive_path` (str)

**Returns:** `bool`

---

##### `delete_file(self, media_filename: str, entity_type: str, entity_id: int) → bool`

Delete media file and its thumbnails

**Parameters:**

- `self`
- `media_filename` (str)
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `bool`

---

##### `get_file_path(self, media_filename: str, entity_type: str, entity_id: int) → Optional[Path]`

Get full path to stored media file

**Parameters:**

- `self`
- `media_filename` (str)
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `Optional[Path]`

---

##### `get_media_info(self, file_path: Path) → Dict[str, Any]`

Get detailed media information

**Parameters:**

- `self`
- `file_path` (Path)

**Returns:** `Dict[str, Any]`

---

##### `organize_media_by_entity(self, entity_type: str, entity_id: int) → List[Dict[str, Any]]`

Get all media files for a specific entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `List[Dict[str, Any]]`

---

##### `store_file(self, file_path: str, entity_type: str, entity_id: int, description: str, tags: str, author: str) → Dict[str, Any]`

Store a media file and return metadata

Args:
    file_path: Source file path
    entity_type: Type of entity (site, us, inventario)
    entity_id: Entity ID
    description: File description
    tags: Tags for the file
    author: Author/photographer
    
Returns:
    Dictionary with file metadata

**Parameters:**

- `self`
- `file_path` (str)
- `entity_type` (str)
- `entity_id` (int)
- `description` (str)
- `tags` (str)
- `author` (str)

**Returns:** `Dict[str, Any]`

---



\newpage


## Module: `pyarchinit_mini/models/__init__.py`

**File Path:** `pyarchinit_mini/models/__init__.py`


\newpage


## Module: `pyarchinit_mini/models/base.py`

**File Path:** `pyarchinit_mini/models/base.py`

### Classes

#### `BaseModel`

Base model class with common fields and methods

**Inherits from:** `Base`

**Methods:**

##### `to_dict(self)`

Convert model instance to dictionary

**Parameters:**

- `self`

---

##### `update_from_dict(self, data)`

Update model instance from dictionary

**Parameters:**

- `self`
- `data`

---


#### `BaseModel`

Base model class with common fields and methods

**Inherits from:** `Base`

**Methods:**

##### `to_dict(self)`

Convert model instance to dictionary

**Parameters:**

- `self`

---

##### `update_from_dict(self, data)`

Update model instance from dictionary

**Parameters:**

- `self`
- `data`

---


#### `BaseModel`

Base model class with common fields and methods

**Inherits from:** `Base`

**Methods:**

##### `to_dict(self)`

Convert model instance to dictionary

**Parameters:**

- `self`

---

##### `update_from_dict(self, data)`

Update model instance from dictionary

**Parameters:**

- `self`
- `data`

---



\newpage


## Module: `pyarchinit_mini/models/harris_matrix.py`

**File Path:** `pyarchinit_mini/models/harris_matrix.py`

### Classes

#### `HarrisMatrix`

Harris Matrix relationships between stratigraphic units

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `HarrisMatrix` object, displaying key attributes such as the site identifier (`sito`) and the relationship between the upper (`us_sopra`) and lower (`us_sotto`) stratigraphic units. This representation is useful for debugging and logging, as it provides a clear and concise summary of the object's state.

**Parameters:**

- `self`

---


#### `HarrisMatrix`

Harris Matrix relationships between stratigraphic units

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `HarrisMatrix` object, displaying its associated `sito` value as well as the stratigraphic relationship from `us_sopra` (upper unit) to `us_sotto` (lower unit). This representation is useful for debugging and logging, as it provides a concise summary of the object's key attributes and relationships.

**Parameters:**

- `self`

---


#### `HarrisMatrix`

Harris Matrix relationships between stratigraphic units

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The **`__repr__`** method returns a string representation of the `HarrisMatrix` object, displaying key attributes such as the site identifier (`sito`) and the relationship between `us_sopra` and `us_sotto`. This representation is useful for debugging and logging, as it provides a concise summary of the object's essential information.

**Parameters:**

- `self`

---


#### `Period`

Archaeological periods and phases

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `Periodizzazione` instance, displaying its period name along with the start and end dates. This is primarily used for debugging and logging, providing a human-readable summary that helps identify the periodization assignment at a glance.

**Parameters:**

- `self`

---


#### `Period`

Archaeological periods and phases

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the Periodizzazione instance, displaying its period name and date range in the format `<Period('period_name', start_date-end_date)>`. This representation is primarily intended for debugging and logging purposes, providing a concise summary of the object's key attributes.

**Parameters:**

- `self`

---


#### `Period`

Archaeological periods and phases

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `Period` object, displaying its `period_name` along with the `start_date` and `end_date`. This representation is intended to provide a concise and informative summary of the object's key attributes for debugging and logging purposes.

**Parameters:**

- `self`

---


#### `Periodizzazione`

Periodization assignments for archaeological contexts
Links US and other entities to chronological periods

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `Periodizzazione` object, displaying its associated site (`sito`), stratigraphic unit (`us`), and the initial and final periods (`periodo_iniziale` and `periodo_finale`). This representation is intended to provide a clear and concise summary of the object's key identifying information, primarily for debugging and logging purposes.

**Parameters:**

- `self`

---

##### `dating_range(self) → str`

Get formatted dating range

**Parameters:**

- `self`

**Returns:** `str`

**Decorators:** `property`

---


#### `Periodizzazione`

Periodization assignments for archaeological contexts
Links US and other entities to chronological periods

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `Periodizzazione` object, displaying its associated site, US number, and the range between its initial and final periods. This representation is useful for debugging and logging purposes, providing a concise summary of the object's key identifying information.

**Parameters:**

- `self`

---

##### `dating_range(self) → str`

Get formatted dating range

**Parameters:**

- `self`

**Returns:** `str`

**Decorators:** `property`

---


#### `Periodizzazione`

Periodization assignments for archaeological contexts
Links US and other entities to chronological periods

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `Periodizzazione` object, including its associated site (`sito`), stratigraphic unit (`us`), and the range from the initial to the final period (`periodo_iniziale`-`periodo_finale`). This representation is primarily used for debugging and logging, making it easier to identify specific instances of the class.

**Parameters:**

- `self`

---

##### `dating_range(self) → str`

Get formatted dating range

**Parameters:**

- `self`

**Returns:** `str`

**Decorators:** `property`

---


#### `USRelationships`

Detailed stratigraphic relationships between US

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `USRelationship` object, displaying its core attributes in a readable format. Specifically, it outputs the source unit (`us_from`), the type of relationship (`relationship_type`), and the target unit (`us_to`). This representation is useful for debugging and logging, as it succinctly summarizes the object's key information.

**Parameters:**

- `self`

---


#### `USRelationships`

Detailed stratigraphic relationships between US

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `USRelationship` object, displaying its `us_from`, `relationship_type`, and `us_to` attributes in a concise format. This is primarily used for debugging and logging, allowing for an informative and human-readable display of the object's key relational data.

**Parameters:**

- `self`

---


#### `USRelationships`

Detailed stratigraphic relationships between US

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `USRelationship` object, displaying its key attributes (`us_from`, `relationship_type`, and `us_to`) in a concise format. This representation is useful for debugging and logging, as it allows developers to quickly identify the relationship between stratigraphic units.

**Parameters:**

- `self`

---



\newpage


## Module: `pyarchinit_mini/models/inventario_materiali.py`

**File Path:** `pyarchinit_mini/models/inventario_materiali.py`

### Classes

#### `InventarioMateriali`

Material inventory model
Complete implementation from PyArchInit INVENTARIO_MATERIALI entity

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string that provides a clear and concise representation of the `InventarioMateriali` object, including its primary attributes: `id_invmat`, `sito`, `numero_inventario`, and `tipo_reperto`. This representation is primarily intended for debugging and logging purposes, making it easier to identify individual instances of the class.

**Parameters:**

- `self`

---

##### `context_info(self)`

Context information as string

**Parameters:**

- `self`

**Decorators:** `property`

---

##### `display_name(self)`

Human readable identifier

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `InventarioMateriali`

Material inventory model
Complete implementation from PyArchInit INVENTARIO_MATERIALI entity

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `InventarioMateriali` object, including its unique identifier (`id_invmat`), site (`sito`), inventory number (`numero_inventario`), and artifact type (`tipo_reperto`). This representation is useful for debugging and logging, as it provides a clear and concise summary of the object's key attributes.

**Parameters:**

- `self`

---

##### `context_info(self)`

Context information as string

**Parameters:**

- `self`

**Decorators:** `property`

---

##### `display_name(self)`

Human readable identifier

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `InventarioMateriali`

Material inventory model
Complete implementation from PyArchInit INVENTARIO_MATERIALI entity

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `InventarioMateriali` object, displaying key attributes such as `id_invmat`, `sito`, `numero_inventario`, and `tipo_reperto`. This representation is intended to provide a clear and informative summary of the object's state, which is useful for debugging and logging purposes.

**Parameters:**

- `self`

---

##### `context_info(self)`

Context information as string

**Parameters:**

- `self`

**Decorators:** `property`

---

##### `display_name(self)`

Human readable identifier

**Parameters:**

- `self`

**Decorators:** `property`

---



\newpage


## Module: `pyarchinit_mini/models/media.py`

**File Path:** `pyarchinit_mini/models/media.py`

### Classes

#### `Documentation`

Documentation files and reports

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The __repr__ method returns a string representation of the Documentation object, including its title, entity type, and entity ID. This representation is useful for debugging and logging, as it provides a concise summary of the object's key identifying information.

**Parameters:**

- `self`

---


#### `Documentation`

Documentation files and reports

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The __repr__ method returns a string representation of the Documentation object, including its title, entity type, and entity ID. This representation is intended to provide a concise summary of the instance, making it useful for debugging and logging purposes.

**Parameters:**

- `self`

---


#### `Documentation`

Documentation files and reports

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The __repr__ method returns a string representation of the Documentation object, displaying its title, entity type, and entity ID in a concise format. This representation is primarily intended for debugging and logging purposes, providing a clear and informative summary of the object's key identifying attributes.

**Parameters:**

- `self`

---


#### `Media`

Media files (images, documents, videos) linked to archaeological records

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the Media object, displaying its media name along with the associated entity type and entity ID. This representation is primarily intended for debugging and logging, making it easier to identify specific Media instances in output or logs.

**Parameters:**

- `self`

---

##### `is_document(self)`

**is_document**  
Indicates whether the media file is of type 'document'. Returns True if the media_type attribute equals 'document', otherwise returns False. This property helps differentiate document files from other media types.

**Parameters:**

- `self`

**Decorators:** `property`

---

##### `is_image(self)`

The **is_image** property returns a boolean indicating whether the media instance is classified as an image. It evaluates to **True** if the instance's `media_type` attribute is set to `'image'`; otherwise, it returns **False**. This property enables quick checks for image-type media objects within the class.

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `Media`

Media files (images, documents, videos) linked to archaeological records

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the Media object, displaying its media name, entity type, and entity ID. This representation is primarily intended for debugging and logging purposes, allowing developers to easily identify individual Media instances in output.

**Parameters:**

- `self`

---

##### `is_document(self)`

**is_document**  
Returns a boolean indicating whether the media file is classified as a document. This property evaluates to True if the media_type attribute equals 'document', enabling type checks within media handling workflows.

**Parameters:**

- `self`

**Decorators:** `property`

---

##### `is_image(self)`

The **is_image** property determines whether the media object's type is classified as an image. It returns `True` if the `media_type` attribute equals `'image'`; otherwise, it returns `False`. This is useful for quickly checking the nature of the media without directly accessing its type attribute.

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `Media`

Media files (images, documents, videos) linked to archaeological records

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the Media object, displaying its `media_name`, `entity_type`, and `entity_id`. This provides a clear and informative summary of the object, which is useful for debugging and logging purposes.

**Parameters:**

- `self`

---

##### `is_document(self)`

**is_document**  
Returns True if the media file is classified as a document. This property checks whether the media_type attribute of the instance is set to 'document', allowing for easy identification of document-type media files.

**Parameters:**

- `self`

**Decorators:** `property`

---

##### `is_image(self)`

The **is_image** property returns a boolean value indicating whether the media instance is of type 'image'. It evaluates to True if the `media_type` attribute equals 'image', and False otherwise. This property is useful for distinguishing images from other media types within the class.

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `MediaThumb`

Thumbnails for media files

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The __repr__ method provides a string representation of the MediaThumb object, displaying its associated media ID and thumbnail size. This representation is useful for debugging and logging, as it clearly identifies instances of MediaThumb in an informative and readable format.

**Parameters:**

- `self`

---


#### `MediaThumb`

Thumbnails for media files

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The __repr__ method returns a string representation of the MediaThumb object, displaying its associated media ID and thumbnail size. This representation is useful for debugging and logging, as it provides a concise summary of the object's key identifying attributes.

**Parameters:**

- `self`

---


#### `MediaThumb`

Thumbnails for media files

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The __repr__ method returns a string representation of the MediaThumb instance, displaying its associated media ID and thumbnail size. This is useful for debugging and logging, as it provides a concise summary of the object's key attributes.

**Parameters:**

- `self`

---



\newpage


## Module: `pyarchinit_mini/models/site.py`

**File Path:** `pyarchinit_mini/models/site.py`

### Classes

#### `Site`

Archaeological site model
Adapted from PyArchInit SITE entity

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the Site object, displaying key attributes such as `id_sito`, `sito`, and `comune`. This representation is intended to be unambiguous and useful for debugging, logging, or interactive sessions, allowing developers to easily identify instances of the Site class.

**Parameters:**

- `self`

---

##### `display_name(self)`

Human readable name for the site

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `Site`

Archaeological site model
Adapted from PyArchInit SITE entity

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the Site object, displaying its unique identifier (`id_sito`), name (`sito`), and associated municipality (`comune`). This representation is primarily intended for debugging and logging purposes, providing a clear and concise summary of the object's key attributes.

**Parameters:**

- `self`

---

##### `display_name(self)`

Human readable name for the site

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `Site`

Archaeological site model
Adapted from PyArchInit SITE entity

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method provides a string representation of the Site object, including its unique ID, name (`sito`), and associated municipality (`comune`). This representation is primarily intended for debugging and logging purposes, allowing developers to easily identify and inspect instances of the Site class.

**Parameters:**

- `self`

---

##### `display_name(self)`

Human readable name for the site

**Parameters:**

- `self`

**Decorators:** `property`

---



\newpage


## Module: `pyarchinit_mini/models/thesaurus.py`

**File Path:** `pyarchinit_mini/models/thesaurus.py`

### Classes

#### `ThesaurusCategory`

Categories for organizing thesaurus entries

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `ThesaurusCategory` object, displaying its unique ID and category name. This representation is useful for debugging and logging, as it provides a clear and concise summary of the object's key attributes.

**Parameters:**

- `self`

---


#### `ThesaurusCategory`

Categories for organizing thesaurus entries

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `ThesaurusCategory` instance, displaying its `id_category` and `category_name` attributes. This representation is useful for debugging and logging, as it provides a clear and concise summary of the object's key information.

**Parameters:**

- `self`

---


#### `ThesaurusCategory`

Categories for organizing thesaurus entries

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `ThesaurusCategory` object, displaying its `id_category` and `category_name` attributes. This representation is intended to provide a concise and informative summary of the object, useful for debugging and logging purposes.

**Parameters:**

- `self`

---


#### `ThesaurusField`

Field-specific thesaurus entries
For detailed field vocabularies

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `ThesaurusField` instance, including the table name, field name, and value attributes. This representation is primarily used for debugging and logging, providing a clear and concise summary of the object's key identifying fields.

**Parameters:**

- `self`

---

##### `display_name(self)`

Display name for UI

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `ThesaurusField`

Field-specific thesaurus entries
For detailed field vocabularies

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `ThesaurusField` object, including the table name, field name, and value attributes. This representation is useful for debugging and logging, as it provides a clear and concise summary of the object's key identifying information.

**Parameters:**

- `self`

---

##### `display_name(self)`

Display name for UI

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `ThesaurusField`

Field-specific thesaurus entries
For detailed field vocabularies

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `ThesaurusField` object, displaying the values of its `table_name`, `field_name`, and `value` attributes. This representation is useful for debugging and logging, as it provides a clear and concise summary of the object's key properties.

**Parameters:**

- `self`

---

##### `display_name(self)`

Display name for UI

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `ThesaurusSigle`

Thesaurus for controlled vocabularies and abbreviations
Based on pyarchinit_thesaurus_sigle table

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `ThesaurusSigle` object, including its `id_thesaurus_sigle`, `nome_tabella`, and `sigla` attributes. This representation is primarily intended for debugging and logging purposes, providing a clear and concise summary of the object's key identifying fields.

**Parameters:**

- `self`

---

##### `display_value(self)`

Display value for UI

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `ThesaurusSigle`

Thesaurus for controlled vocabularies and abbreviations
Based on pyarchinit_thesaurus_sigle table

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `ThesaurusSigle` object, displaying key attributes such as `id_thesaurus_sigle`, `nome_tabella`, and `sigla`. This representation is primarily intended for debugging and logging, making it easier to identify and inspect instances of the class.

**Parameters:**

- `self`

---

##### `display_value(self)`

Display value for UI

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `ThesaurusSigle`

Thesaurus for controlled vocabularies and abbreviations
Based on pyarchinit_thesaurus_sigle table

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `ThesaurusSigle` object, displaying its unique identifier (`id_thesaurus_sigle`), table name (`nome_tabella`), and code (`sigla`). This representation is primarily intended for debugging and logging purposes, providing a concise and informative summary of the object's key attributes.

**Parameters:**

- `self`

---

##### `display_value(self)`

Display value for UI

**Parameters:**

- `self`

**Decorators:** `property`

---



\newpage


## Module: `pyarchinit_mini/models/us.py`

**File Path:** `pyarchinit_mini/models/us.py`

### Classes

#### `US`

Stratigraphic Unit model
Adapted from PyArchInit US entity with key fields

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `US` object, displaying its key attributes: `id_us`, `sito`, `area`, and `us`. This representation is useful for debugging and logging, as it provides a concise summary of the object's state.

**Parameters:**

- `self`

---

##### `display_name(self)`

Human readable identifier for the US

**Parameters:**

- `self`

**Decorators:** `property`

---

##### `full_identifier(self)`

Complete identifier: Site.Area.US

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `US`

Stratigraphic Unit model
Adapted from PyArchInit US entity with key fields

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the `US` object, including its `id_us`, `sito`, `area`, and `us` attributes. This representation is useful for debugging and logging, as it provides a concise summary of the object's key identifying information.

**Parameters:**

- `self`

---

##### `display_name(self)`

Human readable identifier for the US

**Parameters:**

- `self`

**Decorators:** `property`

---

##### `full_identifier(self)`

Complete identifier: Site.Area.US

**Parameters:**

- `self`

**Decorators:** `property`

---


#### `US`

Stratigraphic Unit model
Adapted from PyArchInit US entity with key fields

**Inherits from:** `BaseModel`

**Methods:**

##### `__repr__(self)`

The `__repr__` method returns a string representation of the US object, including its unique identifier (`id_us`), site (`sito`), area, and unit (`us`). This representation is primarily intended for debugging and logging, allowing developers to easily identify and inspect instances of the US class.

**Parameters:**

- `self`

---

##### `display_name(self)`

Human readable identifier for the US

**Parameters:**

- `self`

**Decorators:** `property`

---

##### `full_identifier(self)`

Complete identifier: Site.Area.US

**Parameters:**

- `self`

**Decorators:** `property`

---



\newpage


## Module: `pyarchinit_mini/pdf_export/__init__.py`

**File Path:** `pyarchinit_mini/pdf_export/__init__.py`


\newpage


## Module: `pyarchinit_mini/pdf_export/pdf_generator.py`

**File Path:** `pyarchinit_mini/pdf_export/pdf_generator.py`

### Classes

#### `PDFGenerator`

Generate PDF reports for archaeological data

**Methods:**

##### `__init__(self)`

Initializes a new instance of the PDFGenerator class. This method sets up the default stylesheet for PDF generation and applies any custom paragraph styles required for formatting archaeological reports.

**Parameters:**

- `self`

---

##### `generate_harris_matrix_report(self, site_name: str, matrix_image_path: str, relationships: List[Dict[str, Any]], statistics: Dict[str, Any], output_path: Optional[str]) → bytes`

Generate Harris Matrix documentation report

**Parameters:**

- `self`
- `site_name` (str)
- `matrix_image_path` (str)
- `relationships` (List[Dict[str, Any]])
- `statistics` (Dict[str, Any])
- `output_path` (Optional[str])

**Returns:** `bytes`

---

##### `generate_site_report(self, site_data: Dict[str, Any], us_list: List[Dict[str, Any]], inventory_list: List[Dict[str, Any]], media_list: List[Dict[str, Any]], output_path: Optional[str]) → bytes`

Generate comprehensive site report

Args:
    site_data: Site information
    us_list: List of stratigraphic units
    inventory_list: List of inventory items
    media_list: List of media files
    output_path: Optional output file path
    
Returns:
    PDF bytes

**Parameters:**

- `self`
- `site_data` (Dict[str, Any])
- `us_list` (List[Dict[str, Any]])
- `inventory_list` (List[Dict[str, Any]])
- `media_list` (List[Dict[str, Any]])
- `output_path` (Optional[str])

**Returns:** `bytes`

---


#### `PDFGenerator`

Generate PDF reports for archaeological data

**Methods:**

##### `__init__(self)`

Initializes the PDF report generator by setting up the default paragraph styles used throughout the document. This method retrieves a sample stylesheet and applies any custom styles needed for formatting the report content.

**Parameters:**

- `self`

---

##### `generate_harris_matrix_report(self, site_name: str, matrix_image_path: str, relationships: List[Dict[str, Any]], statistics: Dict[str, Any], output_path: Optional[str]) → bytes`

Generate Harris Matrix documentation report

**Parameters:**

- `self`
- `site_name` (str)
- `matrix_image_path` (str)
- `relationships` (List[Dict[str, Any]])
- `statistics` (Dict[str, Any])
- `output_path` (Optional[str])

**Returns:** `bytes`

---

##### `generate_inventario_pdf(self, site_name: str, inventario_list: List[Dict[str, Any]], output_path: str) → str`

Generate Inventario (Finds) PDF report in PyArchInit original format (A5)

**Parameters:**

- `self`
- `site_name` (str)
- `inventario_list` (List[Dict[str, Any]])
- `output_path` (str)

**Returns:** `str`

---

##### `generate_site_report(self, site_data: Dict[str, Any], us_list: List[Dict[str, Any]], inventory_list: List[Dict[str, Any]], media_list: List[Dict[str, Any]], output_path: Optional[str]) → bytes`

Generate comprehensive site report

Args:
    site_data: Site information
    us_list: List of stratigraphic units
    inventory_list: List of inventory items
    media_list: List of media files
    output_path: Optional output file path
    
Returns:
    PDF bytes

**Parameters:**

- `self`
- `site_data` (Dict[str, Any])
- `us_list` (List[Dict[str, Any]])
- `inventory_list` (List[Dict[str, Any]])
- `media_list` (List[Dict[str, Any]])
- `output_path` (Optional[str])

**Returns:** `bytes`

---

##### `generate_us_pdf(self, site_name: str, us_list: List[Dict[str, Any]], output_path: str) → str`

Generate US (Stratigraphic Units) PDF report in PyArchInit original format

**Parameters:**

- `self`
- `site_name` (str)
- `us_list` (List[Dict[str, Any]])
- `output_path` (str)

**Returns:** `str`

---


#### `PDFGenerator`

Generate PDF reports for archaeological data

**Methods:**

##### `__init__(self)`

Initializes the PDF report generator by loading the default stylesheet and configuring custom paragraph styles for the document. This method ensures that all subsequent PDF content adheres to the specified formatting standards required for archaeological data reports.

**Parameters:**

- `self`

---

##### `generate_harris_matrix_report(self, site_name: str, matrix_image_path: str, relationships: List[Dict[str, Any]], statistics: Dict[str, Any], output_path: Optional[str]) → bytes`

Generate Harris Matrix documentation report

**Parameters:**

- `self`
- `site_name` (str)
- `matrix_image_path` (str)
- `relationships` (List[Dict[str, Any]])
- `statistics` (Dict[str, Any])
- `output_path` (Optional[str])

**Returns:** `bytes`

---

##### `generate_inventario_pdf(self, site_name: str, inventario_list: List[Dict[str, Any]], output_path: str) → str`

Generate Inventario (Finds) PDF report using authentic PyArchInit template

**Parameters:**

- `self`
- `site_name` (str)
- `inventario_list` (List[Dict[str, Any]])
- `output_path` (str)

**Returns:** `str`

---

##### `generate_site_report(self, site_data: Dict[str, Any], us_list: List[Dict[str, Any]], inventory_list: List[Dict[str, Any]], media_list: List[Dict[str, Any]], output_path: Optional[str]) → bytes`

Generate comprehensive site report

Args:
    site_data: Site information
    us_list: List of stratigraphic units
    inventory_list: List of inventory items
    media_list: List of media files
    output_path: Optional output file path
    
Returns:
    PDF bytes

**Parameters:**

- `self`
- `site_data` (Dict[str, Any])
- `us_list` (List[Dict[str, Any]])
- `inventory_list` (List[Dict[str, Any]])
- `media_list` (List[Dict[str, Any]])
- `output_path` (Optional[str])

**Returns:** `bytes`

---

##### `generate_us_pdf(self, site_name: str, us_list: List[Dict[str, Any]], output_path: str) → str`

Generate US (Stratigraphic Units) PDF report in PyArchInit original format

**Parameters:**

- `self`
- `site_name` (str)
- `us_list` (List[Dict[str, Any]])
- `output_path` (str)

**Returns:** `str`

---


### Functions

#### `safe_str(value)`

Safely convert value to string

**Parameters:**

- `value`

---

#### `safe_str(value)`

Safely convert value to string

**Parameters:**

- `value`

---

#### `safe_str(value)`

Safely convert value to string

**Parameters:**

- `value`

---


\newpage


## Module: `pyarchinit_mini/pdf_export/pyarchinit_inventory_template.py`

**File Path:** `pyarchinit_mini/pdf_export/pyarchinit_inventory_template.py`

### Classes

#### `PyArchInitInventoryTemplate`

Authentic PyArchInit inventory template following the original design

**Methods:**

##### `__init__(self)`

Initializes a new instance of the class by configuring the document’s visual styles according to the authentic PyArchInit inventory template. This method calls setup_styles() to apply PyArchInit-specific style settings, ensuring consistent formatting throughout the document.

**Parameters:**

- `self`

---

##### `generate_inventory_catalog(self, inventario_list: List[Dict[str, Any]], output_path: str, site_name: str) → str`

Generate inventory catalog (summary table) in A4 format

Args:
    inventario_list: List of inventory items
    output_path: Output file path 
    site_name: Site name for header
    
Returns:
    Generated file path

**Parameters:**

- `self`
- `inventario_list` (List[Dict[str, Any]])
- `output_path` (str)
- `site_name` (str)

**Returns:** `str`

---

##### `generate_inventory_sheets(self, inventario_list: List[Dict[str, Any]], output_path: str, site_name: str) → str`

Generate inventory sheets in authentic PyArchInit A5 format

Args:
    inventario_list: List of inventory items
    output_path: Output file path
    site_name: Site name for header
    
Returns:
    Generated file path

**Parameters:**

- `self`
- `inventario_list` (List[Dict[str, Any]])
- `output_path` (str)
- `site_name` (str)

**Returns:** `str`

---

##### `setup_styles(self)`

Setup PyArchInit specific styles

**Parameters:**

- `self`

---


### Functions

#### `safe_str(value)`

Safely convert value to string

**Parameters:**

- `value`

---


\newpage


## Module: `pyarchinit_mini/services/__init__.py`

**File Path:** `pyarchinit_mini/services/__init__.py`


\newpage


## Module: `pyarchinit_mini/services/inventario_service.py`

**File Path:** `pyarchinit_mini/services/inventario_service.py`

### Classes

#### `InventarioService`

Service class for inventory operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the InventarioService class.  
This constructor method accepts a DatabaseManager object and assigns it to the service, enabling database operations related to inventory management.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_inventario(self, filters: Optional[Dict[str, Any]]) → int`

Count inventory items with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_inventario(self, inv_data: Dict[str, Any]) → InventarioMateriali`

Create a new inventory item

**Parameters:**

- `self`
- `inv_data` (Dict[str, Any])

**Returns:** `InventarioMateriali`

---

##### `delete_inventario(self, inv_id: int) → bool`

Delete inventory item

**Parameters:**

- `self`
- `inv_id` (int)

**Returns:** `bool`

---

##### `get_all_inventario(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[InventarioDTO]`

Get all inventory items with pagination and filtering - returns DTOs

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[InventarioDTO]`

---

##### `get_inventario_by_id(self, inv_id: int) → Optional[InventarioMateriali]`

Get inventory item by ID

**Parameters:**

- `self`
- `inv_id` (int)

**Returns:** `Optional[InventarioMateriali]`

---

##### `get_inventario_by_site(self, site_name: str, page: int, size: int) → List[InventarioDTO]`

Get all inventory items for a specific site - returns DTOs

**Parameters:**

- `self`
- `site_name` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[InventarioDTO]`

---

##### `get_inventario_by_type(self, tipo_reperto: str, page: int, size: int) → List[InventarioDTO]`

Get all inventory items of a specific type - returns DTOs

**Parameters:**

- `self`
- `tipo_reperto` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[InventarioDTO]`

---

##### `get_inventario_by_us(self, site_name: str, area: str, us_number: int, page: int, size: int) → List[InventarioDTO]`

Get all inventory items for a specific US - returns DTOs

**Parameters:**

- `self`
- `site_name` (str)
- `area` (str)
- `us_number` (int)
- `page` (int)
- `size` (int)

**Returns:** `List[InventarioDTO]`

---

##### `get_inventario_dto_by_id(self, inv_id: int) → Optional[InventarioDTO]`

Get inventory item by ID as DTO

**Parameters:**

- `self`
- `inv_id` (int)

**Returns:** `Optional[InventarioDTO]`

---

##### `get_inventory_statistics(self, inv_id: int) → Dict[str, Any]`

Get statistics for an inventory item

**Parameters:**

- `self`
- `inv_id` (int)

**Returns:** `Dict[str, Any]`

---

##### `get_type_statistics(self, site_name: Optional[str]) → Dict[str, int]`

Get statistics by find type

**Parameters:**

- `self`
- `site_name` (Optional[str])

**Returns:** `Dict[str, int]`

---

##### `search_inventario(self, search_term: str, page: int, size: int) → List[InventarioDTO]`

Search inventory items by term - returns DTOs

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[InventarioDTO]`

---

##### `update_inventario(self, inv_id: int, update_data: Dict[str, Any]) → InventarioMateriali`

Update existing inventory item

**Parameters:**

- `self`
- `inv_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `InventarioMateriali`

---


#### `InventarioService`

Service class for inventory operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the InventarioService class.  
This constructor accepts a DatabaseManager object, which is used to manage database operations related to inventory activities.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_inventario(self, filters: Optional[Dict[str, Any]]) → int`

Count inventory items with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_inventario(self, inv_data: Dict[str, Any]) → InventarioMateriali`

Create a new inventory item

**Parameters:**

- `self`
- `inv_data` (Dict[str, Any])

**Returns:** `InventarioMateriali`

---

##### `create_inventario_dto(self, inv_data: Dict[str, Any]) → InventarioDTO`

Create a new inventory item and return as DTO

**Parameters:**

- `self`
- `inv_data` (Dict[str, Any])

**Returns:** `InventarioDTO`

---

##### `delete_inventario(self, inv_id: int) → bool`

Delete inventory item

**Parameters:**

- `self`
- `inv_id` (int)

**Returns:** `bool`

---

##### `get_all_inventario(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[InventarioDTO]`

Get all inventory items with pagination and filtering - returns DTOs

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[InventarioDTO]`

---

##### `get_all_inventario_dto(self, page: int, size: int) → List`

Get all inventario items as DTOs (session-safe)

**Parameters:**

- `self`
- `page` (int)
- `size` (int)

**Returns:** `List`

---

##### `get_inventario_by_id(self, inv_id: int) → Optional[InventarioMateriali]`

Get inventory item by ID

**Parameters:**

- `self`
- `inv_id` (int)

**Returns:** `Optional[InventarioMateriali]`

---

##### `get_inventario_by_site(self, site_name: str, page: int, size: int) → List[InventarioDTO]`

Get all inventory items for a specific site - returns DTOs

**Parameters:**

- `self`
- `site_name` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[InventarioDTO]`

---

##### `get_inventario_by_type(self, tipo_reperto: str, page: int, size: int) → List[InventarioDTO]`

Get all inventory items of a specific type - returns DTOs

**Parameters:**

- `self`
- `tipo_reperto` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[InventarioDTO]`

---

##### `get_inventario_by_us(self, site_name: str, area: str, us_number: int, page: int, size: int) → List[InventarioDTO]`

Get all inventory items for a specific US - returns DTOs

**Parameters:**

- `self`
- `site_name` (str)
- `area` (str)
- `us_number` (int)
- `page` (int)
- `size` (int)

**Returns:** `List[InventarioDTO]`

---

##### `get_inventario_dto_by_id(self, inv_id: int) → Optional[InventarioDTO]`

Get inventory item by ID as DTO

**Parameters:**

- `self`
- `inv_id` (int)

**Returns:** `Optional[InventarioDTO]`

---

##### `get_inventory_statistics(self, inv_id: int) → Dict[str, Any]`

Get statistics for an inventory item

**Parameters:**

- `self`
- `inv_id` (int)

**Returns:** `Dict[str, Any]`

---

##### `get_type_statistics(self, site_name: Optional[str]) → Dict[str, int]`

Get statistics by find type

**Parameters:**

- `self`
- `site_name` (Optional[str])

**Returns:** `Dict[str, int]`

---

##### `search_inventario(self, search_term: str, page: int, size: int) → List[InventarioDTO]`

Search inventory items by term - returns DTOs

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[InventarioDTO]`

---

##### `update_inventario(self, inv_id: int, update_data: Dict[str, Any]) → InventarioMateriali`

Update existing inventory item

**Parameters:**

- `self`
- `inv_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `InventarioMateriali`

---


#### `InventarioService`

Service class for inventory operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes an instance of the InventarioService class.  
This constructor accepts a DatabaseManager object and assigns it to the instance for managing database operations related to inventory.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_inventario(self, filters: Optional[Dict[str, Any]]) → int`

Count inventory items with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_inventario(self, inv_data: Dict[str, Any]) → InventarioMateriali`

Create a new inventory item

**Parameters:**

- `self`
- `inv_data` (Dict[str, Any])

**Returns:** `InventarioMateriali`

---

##### `create_inventario_dto(self, inv_data: Dict[str, Any]) → InventarioDTO`

Create a new inventory item and return as DTO

**Parameters:**

- `self`
- `inv_data` (Dict[str, Any])

**Returns:** `InventarioDTO`

---

##### `delete_inventario(self, inv_id: int) → bool`

Delete inventory item

**Parameters:**

- `self`
- `inv_id` (int)

**Returns:** `bool`

---

##### `get_all_inventario(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[InventarioDTO]`

Get all inventory items with pagination and filtering - returns DTOs

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[InventarioDTO]`

---

##### `get_all_inventario_dto(self, page: int, size: int) → List`

Get all inventario items as DTOs (session-safe)

**Parameters:**

- `self`
- `page` (int)
- `size` (int)

**Returns:** `List`

---

##### `get_inventario_by_id(self, inv_id: int) → Optional[InventarioMateriali]`

Get inventory item by ID

**Parameters:**

- `self`
- `inv_id` (int)

**Returns:** `Optional[InventarioMateriali]`

---

##### `get_inventario_by_site(self, site_name: str, page: int, size: int) → List[InventarioDTO]`

Get all inventory items for a specific site - returns DTOs

**Parameters:**

- `self`
- `site_name` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[InventarioDTO]`

---

##### `get_inventario_by_type(self, tipo_reperto: str, page: int, size: int) → List[InventarioDTO]`

Get all inventory items of a specific type - returns DTOs

**Parameters:**

- `self`
- `tipo_reperto` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[InventarioDTO]`

---

##### `get_inventario_by_us(self, site_name: str, area: str, us_number: int, page: int, size: int) → List[InventarioDTO]`

Get all inventory items for a specific US - returns DTOs

**Parameters:**

- `self`
- `site_name` (str)
- `area` (str)
- `us_number` (int)
- `page` (int)
- `size` (int)

**Returns:** `List[InventarioDTO]`

---

##### `get_inventario_dto_by_id(self, inv_id: int) → Optional[InventarioDTO]`

Get inventory item by ID as DTO

**Parameters:**

- `self`
- `inv_id` (int)

**Returns:** `Optional[InventarioDTO]`

---

##### `get_inventory_statistics(self, inv_id: int) → Dict[str, Any]`

Get statistics for an inventory item

**Parameters:**

- `self`
- `inv_id` (int)

**Returns:** `Dict[str, Any]`

---

##### `get_type_statistics(self, site_name: Optional[str]) → Dict[str, int]`

Get statistics by find type

**Parameters:**

- `self`
- `site_name` (Optional[str])

**Returns:** `Dict[str, int]`

---

##### `search_inventario(self, search_term: str, page: int, size: int) → List[InventarioDTO]`

Search inventory items by term - returns DTOs

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[InventarioDTO]`

---

##### `update_inventario(self, inv_id: int, update_data: Dict[str, Any]) → InventarioMateriali`

Update existing inventory item

**Parameters:**

- `self`
- `inv_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `InventarioMateriali`

---



\newpage


## Module: `pyarchinit_mini/services/media_service.py`

**File Path:** `pyarchinit_mini/services/media_service.py`

### Classes

#### `DocumentationService`

Service class for documentation operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the DocumentationService class.  
This constructor method takes a DatabaseManager object as a parameter and assigns it to an instance variable for use in documentation operations.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_documentation(self, filters: Optional[Dict[str, Any]]) → int`

Count documentation with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_documentation(self, doc_data: Dict[str, Any]) → Documentation`

Create a new documentation record

**Parameters:**

- `self`
- `doc_data` (Dict[str, Any])

**Returns:** `Documentation`

---

##### `delete_documentation(self, doc_id: int, delete_file: bool) → bool`

Delete documentation record and optionally the file

**Parameters:**

- `self`
- `doc_id` (int)
- `delete_file` (bool)

**Returns:** `bool`

---

##### `get_all_documentation(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[Documentation]`

Get all documentation with pagination and filtering

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[Documentation]`

---

##### `get_documentation_by_entity(self, entity_type: str, entity_id: int, page: int, size: int) → List[Documentation]`

Get all documentation for a specific entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)
- `page` (int)
- `size` (int)

**Returns:** `List[Documentation]`

---

##### `get_documentation_by_id(self, doc_id: int) → Optional[Documentation]`

Get documentation by ID

**Parameters:**

- `self`
- `doc_id` (int)

**Returns:** `Optional[Documentation]`

---

##### `update_documentation(self, doc_id: int, update_data: Dict[str, Any]) → Documentation`

Update existing documentation

**Parameters:**

- `self`
- `doc_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Documentation`

---


#### `DocumentationService`

Service class for documentation operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the DocumentationService class. This constructor takes a DatabaseManager object as a parameter and assigns it to an instance variable for managing database interactions related to documentation operations.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_documentation(self, filters: Optional[Dict[str, Any]]) → int`

Count documentation with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_documentation(self, doc_data: Dict[str, Any]) → Documentation`

Create a new documentation record

**Parameters:**

- `self`
- `doc_data` (Dict[str, Any])

**Returns:** `Documentation`

---

##### `delete_documentation(self, doc_id: int, delete_file: bool) → bool`

Delete documentation record and optionally the file

**Parameters:**

- `self`
- `doc_id` (int)
- `delete_file` (bool)

**Returns:** `bool`

---

##### `get_all_documentation(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[Documentation]`

Get all documentation with pagination and filtering

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[Documentation]`

---

##### `get_documentation_by_entity(self, entity_type: str, entity_id: int, page: int, size: int) → List[Documentation]`

Get all documentation for a specific entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)
- `page` (int)
- `size` (int)

**Returns:** `List[Documentation]`

---

##### `get_documentation_by_id(self, doc_id: int) → Optional[Documentation]`

Get documentation by ID

**Parameters:**

- `self`
- `doc_id` (int)

**Returns:** `Optional[Documentation]`

---

##### `update_documentation(self, doc_id: int, update_data: Dict[str, Any]) → Documentation`

Update existing documentation

**Parameters:**

- `self`
- `doc_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Documentation`

---


#### `DocumentationService`

Service class for documentation operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the DocumentationService class by assigning the provided DatabaseManager instance to the db_manager attribute. This setup enables the service to perform documentation operations using the specified database manager.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_documentation(self, filters: Optional[Dict[str, Any]]) → int`

Count documentation with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_documentation(self, doc_data: Dict[str, Any]) → Documentation`

Create a new documentation record

**Parameters:**

- `self`
- `doc_data` (Dict[str, Any])

**Returns:** `Documentation`

---

##### `delete_documentation(self, doc_id: int, delete_file: bool) → bool`

Delete documentation record and optionally the file

**Parameters:**

- `self`
- `doc_id` (int)
- `delete_file` (bool)

**Returns:** `bool`

---

##### `get_all_documentation(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[Documentation]`

Get all documentation with pagination and filtering

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[Documentation]`

---

##### `get_documentation_by_entity(self, entity_type: str, entity_id: int, page: int, size: int) → List[Documentation]`

Get all documentation for a specific entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)
- `page` (int)
- `size` (int)

**Returns:** `List[Documentation]`

---

##### `get_documentation_by_id(self, doc_id: int) → Optional[Documentation]`

Get documentation by ID

**Parameters:**

- `self`
- `doc_id` (int)

**Returns:** `Optional[Documentation]`

---

##### `update_documentation(self, doc_id: int, update_data: Dict[str, Any]) → Documentation`

Update existing documentation

**Parameters:**

- `self`
- `doc_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Documentation`

---


#### `MediaService`

Service class for media operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager, media_handler: Optional[MediaHandler])`

Initializes a new instance of the MediaService class. This constructor accepts a DatabaseManager object for database operations and an optional MediaHandler; if none is provided, a default MediaHandler instance is created.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)
- `media_handler` (Optional[MediaHandler])

---

##### `count_media(self, filters: Optional[Dict[str, Any]]) → int`

Count media with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_media_collection(self, collection_name: str, entity_type: str, entity_id: int, media_ids: List[int]) → Dict[str, Any]`

Create a media collection (virtual grouping)

**Parameters:**

- `self`
- `collection_name` (str)
- `entity_type` (str)
- `entity_id` (int)
- `media_ids` (List[int])

**Returns:** `Dict[str, Any]`

---

##### `create_media_record(self, media_data: Dict[str, Any]) → Media`

Create a new media record in database

**Parameters:**

- `self`
- `media_data` (Dict[str, Any])

**Returns:** `Media`

---

##### `delete_media(self, media_id: int, delete_file: bool) → bool`

Delete media record and optionally the file

**Parameters:**

- `self`
- `media_id` (int)
- `delete_file` (bool)

**Returns:** `bool`

---

##### `export_media_archive(self, entity_type: str, entity_id: int, archive_path: str, include_metadata: bool) → bool`

Export media archive for an entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)
- `archive_path` (str)
- `include_metadata` (bool)

**Returns:** `bool`

---

##### `get_all_media(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[Media]`

Get all media with pagination and filtering

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[Media]`

---

##### `get_media_by_entity(self, entity_type: str, entity_id: int, page: int, size: int) → List[Media]`

Get all media for a specific entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)
- `page` (int)
- `size` (int)

**Returns:** `List[Media]`

---

##### `get_media_by_id(self, media_id: int) → Optional[Media]`

Get media by ID

**Parameters:**

- `self`
- `media_id` (int)

**Returns:** `Optional[Media]`

---

##### `get_media_by_site_summary(self, site_name: str) → Dict[str, Any]`

Get media summary for a site

**Parameters:**

- `self`
- `site_name` (str)

**Returns:** `Dict[str, Any]`

---

##### `get_media_by_type(self, media_type: str, page: int, size: int) → List[Media]`

Get all media of a specific type

**Parameters:**

- `self`
- `media_type` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Media]`

---

##### `get_media_statistics(self) → Dict[str, Any]`

Get media statistics

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `get_primary_media(self, entity_type: str, entity_id: int) → Optional[Media]`

Get primary media for an entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `Optional[Media]`

---

##### `search_media(self, search_term: str, page: int, size: int) → List[Media]`

Search media by term

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Media]`

---

##### `set_primary_media(self, media_id: int, entity_type: str, entity_id: int) → bool`

Set media as primary for an entity

**Parameters:**

- `self`
- `media_id` (int)
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `bool`

---

##### `store_and_register_media(self, file_path: str, entity_type: str, entity_id: int, description: str, tags: str, author: str, is_primary: bool) → Media`

Store media file and register in database

**Parameters:**

- `self`
- `file_path` (str)
- `entity_type` (str)
- `entity_id` (int)
- `description` (str)
- `tags` (str)
- `author` (str)
- `is_primary` (bool)

**Returns:** `Media`

---

##### `update_media(self, media_id: int, update_data: Dict[str, Any]) → Media`

Update existing media

**Parameters:**

- `self`
- `media_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Media`

---


#### `MediaService`

Service class for media operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager, media_handler: Optional[MediaHandler])`

Initializes a new instance of the MediaService class.  
This constructor accepts a DatabaseManager instance for database operations and an optional MediaHandler; if no MediaHandler is provided, a default instance is created and used.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)
- `media_handler` (Optional[MediaHandler])

---

##### `count_media(self, filters: Optional[Dict[str, Any]]) → int`

Count media with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_media_collection(self, collection_name: str, entity_type: str, entity_id: int, media_ids: List[int]) → Dict[str, Any]`

Create a media collection (virtual grouping)

**Parameters:**

- `self`
- `collection_name` (str)
- `entity_type` (str)
- `entity_id` (int)
- `media_ids` (List[int])

**Returns:** `Dict[str, Any]`

---

##### `create_media_record(self, media_data: Dict[str, Any]) → Media`

Create a new media record in database

**Parameters:**

- `self`
- `media_data` (Dict[str, Any])

**Returns:** `Media`

---

##### `delete_media(self, media_id: int, delete_file: bool) → bool`

Delete media record and optionally the file

**Parameters:**

- `self`
- `media_id` (int)
- `delete_file` (bool)

**Returns:** `bool`

---

##### `export_media_archive(self, entity_type: str, entity_id: int, archive_path: str, include_metadata: bool) → bool`

Export media archive for an entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)
- `archive_path` (str)
- `include_metadata` (bool)

**Returns:** `bool`

---

##### `get_all_media(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[Media]`

Get all media with pagination and filtering

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[Media]`

---

##### `get_media_by_entity(self, entity_type: str, entity_id: int, page: int, size: int) → List[Media]`

Get all media for a specific entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)
- `page` (int)
- `size` (int)

**Returns:** `List[Media]`

---

##### `get_media_by_id(self, media_id: int) → Optional[Media]`

Get media by ID

**Parameters:**

- `self`
- `media_id` (int)

**Returns:** `Optional[Media]`

---

##### `get_media_by_site_summary(self, site_name: str) → Dict[str, Any]`

Get media summary for a site

**Parameters:**

- `self`
- `site_name` (str)

**Returns:** `Dict[str, Any]`

---

##### `get_media_by_type(self, media_type: str, page: int, size: int) → List[Media]`

Get all media of a specific type

**Parameters:**

- `self`
- `media_type` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Media]`

---

##### `get_media_statistics(self) → Dict[str, Any]`

Get media statistics

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `get_primary_media(self, entity_type: str, entity_id: int) → Optional[Media]`

Get primary media for an entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `Optional[Media]`

---

##### `search_media(self, search_term: str, page: int, size: int) → List[Media]`

Search media by term

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Media]`

---

##### `set_primary_media(self, media_id: int, entity_type: str, entity_id: int) → bool`

Set media as primary for an entity

**Parameters:**

- `self`
- `media_id` (int)
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `bool`

---

##### `store_and_register_media(self, file_path: str, entity_type: str, entity_id: int, description: str, tags: str, author: str, is_primary: bool) → Media`

Store media file and register in database

**Parameters:**

- `self`
- `file_path` (str)
- `entity_type` (str)
- `entity_id` (int)
- `description` (str)
- `tags` (str)
- `author` (str)
- `is_primary` (bool)

**Returns:** `Media`

---

##### `update_media(self, media_id: int, update_data: Dict[str, Any]) → Media`

Update existing media

**Parameters:**

- `self`
- `media_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Media`

---


#### `MediaService`

Service class for media operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager, media_handler: Optional[MediaHandler])`

Initializes a new instance of the MediaService class with the specified database manager and an optional media handler. If no media handler is provided, a default MediaHandler instance is created and used. This setup prepares the service for performing media-related operations with the given dependencies.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)
- `media_handler` (Optional[MediaHandler])

---

##### `count_media(self, filters: Optional[Dict[str, Any]]) → int`

Count media with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_media_collection(self, collection_name: str, entity_type: str, entity_id: int, media_ids: List[int]) → Dict[str, Any]`

Create a media collection (virtual grouping)

**Parameters:**

- `self`
- `collection_name` (str)
- `entity_type` (str)
- `entity_id` (int)
- `media_ids` (List[int])

**Returns:** `Dict[str, Any]`

---

##### `create_media_record(self, media_data: Dict[str, Any]) → Media`

Create a new media record in database

**Parameters:**

- `self`
- `media_data` (Dict[str, Any])

**Returns:** `Media`

---

##### `delete_media(self, media_id: int, delete_file: bool) → bool`

Delete media record and optionally the file

**Parameters:**

- `self`
- `media_id` (int)
- `delete_file` (bool)

**Returns:** `bool`

---

##### `export_media_archive(self, entity_type: str, entity_id: int, archive_path: str, include_metadata: bool) → bool`

Export media archive for an entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)
- `archive_path` (str)
- `include_metadata` (bool)

**Returns:** `bool`

---

##### `get_all_media(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[Media]`

Get all media with pagination and filtering

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[Media]`

---

##### `get_media_by_entity(self, entity_type: str, entity_id: int, page: int, size: int) → List[Media]`

Get all media for a specific entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)
- `page` (int)
- `size` (int)

**Returns:** `List[Media]`

---

##### `get_media_by_id(self, media_id: int) → Optional[Media]`

Get media by ID

**Parameters:**

- `self`
- `media_id` (int)

**Returns:** `Optional[Media]`

---

##### `get_media_by_site_summary(self, site_name: str) → Dict[str, Any]`

Get media summary for a site

**Parameters:**

- `self`
- `site_name` (str)

**Returns:** `Dict[str, Any]`

---

##### `get_media_by_type(self, media_type: str, page: int, size: int) → List[Media]`

Get all media of a specific type

**Parameters:**

- `self`
- `media_type` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Media]`

---

##### `get_media_statistics(self) → Dict[str, Any]`

Get media statistics

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `get_primary_media(self, entity_type: str, entity_id: int) → Optional[Media]`

Get primary media for an entity

**Parameters:**

- `self`
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `Optional[Media]`

---

##### `search_media(self, search_term: str, page: int, size: int) → List[Media]`

Search media by term

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Media]`

---

##### `set_primary_media(self, media_id: int, entity_type: str, entity_id: int) → bool`

Set media as primary for an entity

**Parameters:**

- `self`
- `media_id` (int)
- `entity_type` (str)
- `entity_id` (int)

**Returns:** `bool`

---

##### `store_and_register_media(self, file_path: str, entity_type: str, entity_id: int, description: str, tags: str, author: str, is_primary: bool) → Media`

Store media file and register in database

**Parameters:**

- `self`
- `file_path` (str)
- `entity_type` (str)
- `entity_id` (int)
- `description` (str)
- `tags` (str)
- `author` (str)
- `is_primary` (bool)

**Returns:** `Media`

---

##### `update_media(self, media_id: int, update_data: Dict[str, Any]) → Media`

Update existing media

**Parameters:**

- `self`
- `media_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Media`

---



\newpage


## Module: `pyarchinit_mini/services/periodizzazione_service.py`

**File Path:** `pyarchinit_mini/services/periodizzazione_service.py`

### Classes

#### `PeriodizzazioneService`

Service class for periodization operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the PeriodizzazioneService class.  
This constructor method accepts a DatabaseManager object and assigns it to the service instance, enabling database operations for periodization-related methods.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_periodizzazioni(self, filters: Optional[Dict[str, Any]]) → int`

Count periodizations with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `count_periods(self, filters: Optional[Dict[str, Any]]) → int`

Count periods with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_period(self, period_data: Dict[str, Any]) → Period`

Create a new archaeological period

**Parameters:**

- `self`
- `period_data` (Dict[str, Any])

**Returns:** `Period`

---

##### `create_periodizzazione(self, periodizzazione_data: Dict[str, Any]) → Periodizzazione`

Create a new periodization assignment

**Parameters:**

- `self`
- `periodizzazione_data` (Dict[str, Any])

**Returns:** `Periodizzazione`

---

##### `delete_period(self, period_id: int) → bool`

Delete period

**Parameters:**

- `self`
- `period_id` (int)

**Returns:** `bool`

---

##### `delete_periodizzazione(self, periodizzazione_id: int) → bool`

Delete periodizzazione

**Parameters:**

- `self`
- `periodizzazione_id` (int)

**Returns:** `bool`

---

##### `get_all_periodizzazioni(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[Periodizzazione]`

Get all periodizations with pagination and filtering

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[Periodizzazione]`

---

##### `get_all_periods(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[Period]`

Get all periods with pagination and filtering

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[Period]`

---

##### `get_chronological_sequence(self, site_name: str) → List[Dict[str, Any]]`

Get chronological sequence for a site based on US relationships and dating

**Parameters:**

- `self`
- `site_name` (str)

**Returns:** `List[Dict[str, Any]]`

---

##### `get_dating_summary_by_site(self, site_name: str) → Dict[str, Any]`

Get dating summary for a site

**Parameters:**

- `self`
- `site_name` (str)

**Returns:** `Dict[str, Any]`

---

##### `get_period_by_id(self, period_id: int) → Optional[Period]`

Get period by ID

**Parameters:**

- `self`
- `period_id` (int)

**Returns:** `Optional[Period]`

---

##### `get_period_statistics(self) → Dict[str, Any]`

Get general statistics about periods and dating

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `get_periodizzazione_by_id(self, periodizzazione_id: int) → Optional[Periodizzazione]`

Get periodizzazione by ID

**Parameters:**

- `self`
- `periodizzazione_id` (int)

**Returns:** `Optional[Periodizzazione]`

---

##### `get_periodizzazioni_by_period(self, period_name: str, page: int, size: int) → List[Periodizzazione]`

Get all periodizations for a specific period

**Parameters:**

- `self`
- `period_name` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Periodizzazione]`

---

##### `get_periodizzazioni_by_site(self, site_name: str, page: int, size: int) → List[Periodizzazione]`

Get all periodizations for a specific site

**Parameters:**

- `self`
- `site_name` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Periodizzazione]`

---

##### `search_periodizzazioni(self, search_term: str, page: int, size: int) → List[Periodizzazione]`

Search periodizations by term

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Periodizzazione]`

---

##### `search_periods(self, search_term: str, page: int, size: int) → List[Period]`

Search periods by term

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Period]`

---

##### `update_period(self, period_id: int, update_data: Dict[str, Any]) → Period`

Update existing period

**Parameters:**

- `self`
- `period_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Period`

---

##### `update_periodizzazione(self, periodizzazione_id: int, update_data: Dict[str, Any]) → Periodizzazione`

Update existing periodizzazione

**Parameters:**

- `self`
- `periodizzazione_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Periodizzazione`

---


#### `PeriodizzazioneService`

Service class for periodization operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the PeriodizzazioneService class.  
This constructor method accepts a DatabaseManager object, which is used to manage database operations related to periodization, and assigns it to an instance variable for use in the service methods.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_periodizzazioni(self, filters: Optional[Dict[str, Any]]) → int`

Count periodizations with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `count_periods(self, filters: Optional[Dict[str, Any]]) → int`

Count periods with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_period(self, period_data: Dict[str, Any]) → Period`

Create a new archaeological period

**Parameters:**

- `self`
- `period_data` (Dict[str, Any])

**Returns:** `Period`

---

##### `create_periodizzazione(self, periodizzazione_data: Dict[str, Any]) → Periodizzazione`

Create a new periodization assignment

**Parameters:**

- `self`
- `periodizzazione_data` (Dict[str, Any])

**Returns:** `Periodizzazione`

---

##### `delete_period(self, period_id: int) → bool`

Delete period

**Parameters:**

- `self`
- `period_id` (int)

**Returns:** `bool`

---

##### `delete_periodizzazione(self, periodizzazione_id: int) → bool`

Delete periodizzazione

**Parameters:**

- `self`
- `periodizzazione_id` (int)

**Returns:** `bool`

---

##### `get_all_periodizzazioni(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[Periodizzazione]`

Get all periodizations with pagination and filtering

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[Periodizzazione]`

---

##### `get_all_periods(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[Period]`

Get all periods with pagination and filtering

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[Period]`

---

##### `get_chronological_sequence(self, site_name: str) → List[Dict[str, Any]]`

Get chronological sequence for a site based on US relationships and dating

**Parameters:**

- `self`
- `site_name` (str)

**Returns:** `List[Dict[str, Any]]`

---

##### `get_dating_summary_by_site(self, site_name: str) → Dict[str, Any]`

Get dating summary for a site

**Parameters:**

- `self`
- `site_name` (str)

**Returns:** `Dict[str, Any]`

---

##### `get_period_by_id(self, period_id: int) → Optional[Period]`

Get period by ID

**Parameters:**

- `self`
- `period_id` (int)

**Returns:** `Optional[Period]`

---

##### `get_period_statistics(self) → Dict[str, Any]`

Get general statistics about periods and dating

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `get_periodizzazione_by_id(self, periodizzazione_id: int) → Optional[Periodizzazione]`

Get periodizzazione by ID

**Parameters:**

- `self`
- `periodizzazione_id` (int)

**Returns:** `Optional[Periodizzazione]`

---

##### `get_periodizzazioni_by_period(self, period_name: str, page: int, size: int) → List[Periodizzazione]`

Get all periodizations for a specific period

**Parameters:**

- `self`
- `period_name` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Periodizzazione]`

---

##### `get_periodizzazioni_by_site(self, site_name: str, page: int, size: int) → List[Periodizzazione]`

Get all periodizations for a specific site

**Parameters:**

- `self`
- `site_name` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Periodizzazione]`

---

##### `search_periodizzazioni(self, search_term: str, page: int, size: int) → List[Periodizzazione]`

Search periodizations by term

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Periodizzazione]`

---

##### `search_periods(self, search_term: str, page: int, size: int) → List[Period]`

Search periods by term

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Period]`

---

##### `update_period(self, period_id: int, update_data: Dict[str, Any]) → Period`

Update existing period

**Parameters:**

- `self`
- `period_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Period`

---

##### `update_periodizzazione(self, periodizzazione_id: int, update_data: Dict[str, Any]) → Periodizzazione`

Update existing periodizzazione

**Parameters:**

- `self`
- `periodizzazione_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Periodizzazione`

---


#### `PeriodizzazioneService`

Service class for periodization operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the PeriodizzazioneService class.  
This constructor method accepts a DatabaseManager object and assigns it to the instance, enabling database operations for periodization tasks.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_periodizzazioni(self, filters: Optional[Dict[str, Any]]) → int`

Count periodizations with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `count_periods(self, filters: Optional[Dict[str, Any]]) → int`

Count periods with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_period(self, period_data: Dict[str, Any]) → Period`

Create a new archaeological period

**Parameters:**

- `self`
- `period_data` (Dict[str, Any])

**Returns:** `Period`

---

##### `create_periodizzazione(self, periodizzazione_data: Dict[str, Any]) → Periodizzazione`

Create a new periodization assignment

**Parameters:**

- `self`
- `periodizzazione_data` (Dict[str, Any])

**Returns:** `Periodizzazione`

---

##### `delete_period(self, period_id: int) → bool`

Delete period

**Parameters:**

- `self`
- `period_id` (int)

**Returns:** `bool`

---

##### `delete_periodizzazione(self, periodizzazione_id: int) → bool`

Delete periodizzazione

**Parameters:**

- `self`
- `periodizzazione_id` (int)

**Returns:** `bool`

---

##### `get_all_periodizzazioni(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[Periodizzazione]`

Get all periodizations with pagination and filtering

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[Periodizzazione]`

---

##### `get_all_periods(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[Period]`

Get all periods with pagination and filtering

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[Period]`

---

##### `get_chronological_sequence(self, site_name: str) → List[Dict[str, Any]]`

Get chronological sequence for a site based on US relationships and dating

**Parameters:**

- `self`
- `site_name` (str)

**Returns:** `List[Dict[str, Any]]`

---

##### `get_dating_summary_by_site(self, site_name: str) → Dict[str, Any]`

Get dating summary for a site

**Parameters:**

- `self`
- `site_name` (str)

**Returns:** `Dict[str, Any]`

---

##### `get_period_by_id(self, period_id: int) → Optional[Period]`

Get period by ID

**Parameters:**

- `self`
- `period_id` (int)

**Returns:** `Optional[Period]`

---

##### `get_period_statistics(self) → Dict[str, Any]`

Get general statistics about periods and dating

**Parameters:**

- `self`

**Returns:** `Dict[str, Any]`

---

##### `get_periodizzazione_by_id(self, periodizzazione_id: int) → Optional[Periodizzazione]`

Get periodizzazione by ID

**Parameters:**

- `self`
- `periodizzazione_id` (int)

**Returns:** `Optional[Periodizzazione]`

---

##### `get_periodizzazioni_by_period(self, period_name: str, page: int, size: int) → List[Periodizzazione]`

Get all periodizations for a specific period

**Parameters:**

- `self`
- `period_name` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Periodizzazione]`

---

##### `get_periodizzazioni_by_site(self, site_name: str, page: int, size: int) → List[Periodizzazione]`

Get all periodizations for a specific site

**Parameters:**

- `self`
- `site_name` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Periodizzazione]`

---

##### `search_periodizzazioni(self, search_term: str, page: int, size: int) → List[Periodizzazione]`

Search periodizations by term

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Periodizzazione]`

---

##### `search_periods(self, search_term: str, page: int, size: int) → List[Period]`

Search periods by term

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[Period]`

---

##### `update_period(self, period_id: int, update_data: Dict[str, Any]) → Period`

Update existing period

**Parameters:**

- `self`
- `period_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Period`

---

##### `update_periodizzazione(self, periodizzazione_id: int, update_data: Dict[str, Any]) → Periodizzazione`

Update existing periodizzazione

**Parameters:**

- `self`
- `periodizzazione_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Periodizzazione`

---



\newpage


## Module: `pyarchinit_mini/services/site_service.py`

**File Path:** `pyarchinit_mini/services/site_service.py`

### Classes

#### `SiteService`

Service class for site operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the SiteService class.  
This constructor method accepts a DatabaseManager object and assigns it to an instance variable, enabling the service to interact with the database.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_sites(self, filters: Optional[Dict[str, Any]]) → int`

Count sites with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_site(self, site_data: Dict[str, Any]) → Site`

Create a new site

**Parameters:**

- `self`
- `site_data` (Dict[str, Any])

**Returns:** `Site`

---

##### `delete_site(self, site_id: int) → bool`

Delete site

**Parameters:**

- `self`
- `site_id` (int)

**Returns:** `bool`

---

##### `get_all_sites(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[SiteDTO]`

Get all sites with pagination and filtering - returns DTOs

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[SiteDTO]`

---

##### `get_site_by_id(self, site_id: int) → Optional[Site]`

Get site by ID

**Parameters:**

- `self`
- `site_id` (int)

**Returns:** `Optional[Site]`

---

##### `get_site_by_name(self, site_name: str) → Optional[Site]`

Get site by name

**Parameters:**

- `self`
- `site_name` (str)

**Returns:** `Optional[Site]`

---

##### `get_site_dto_by_id(self, site_id: int) → Optional[SiteDTO]`

Get site by ID as DTO

**Parameters:**

- `self`
- `site_id` (int)

**Returns:** `Optional[SiteDTO]`

---

##### `get_site_statistics(self, site_id: int) → Dict[str, Any]`

Get statistics for a site

**Parameters:**

- `self`
- `site_id` (int)

**Returns:** `Dict[str, Any]`

---

##### `get_unique_countries(self) → List[str]`

Get list of unique countries

**Parameters:**

- `self`

**Returns:** `List[str]`

---

##### `get_unique_municipalities(self, nazione: Optional[str], regione: Optional[str]) → List[str]`

Get list of unique municipalities with optional filters

**Parameters:**

- `self`
- `nazione` (Optional[str])
- `regione` (Optional[str])

**Returns:** `List[str]`

---

##### `get_unique_regions(self, nazione: Optional[str]) → List[str]`

Get list of unique regions, optionally filtered by country

**Parameters:**

- `self`
- `nazione` (Optional[str])

**Returns:** `List[str]`

---

##### `search_sites(self, search_term: str, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[SiteDTO]`

Search sites by term - returns DTOs

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[SiteDTO]`

---

##### `update_site(self, site_id: int, update_data: Dict[str, Any]) → Site`

Update existing site

**Parameters:**

- `self`
- `site_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Site`

---


#### `SiteService`

Service class for site operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the SiteService class.  
This constructor accepts a DatabaseManager object, which is used to manage database operations related to site functionalities.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_sites(self, filters: Optional[Dict[str, Any]]) → int`

Count sites with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `count_sites(self) → int`

Count total number of sites

**Parameters:**

- `self`

**Returns:** `int`

---

##### `create_site(self, site_data: Dict[str, Any]) → Site`

Create a new site

**Parameters:**

- `self`
- `site_data` (Dict[str, Any])

**Returns:** `Site`

---

##### `create_site_dto(self, site_data: Dict[str, Any]) → SiteDTO`

Create a new site and return as DTO

**Parameters:**

- `self`
- `site_data` (Dict[str, Any])

**Returns:** `SiteDTO`

---

##### `delete_site(self, site_id: int) → bool`

Delete site

**Parameters:**

- `self`
- `site_id` (int)

**Returns:** `bool`

---

##### `get_all_sites(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[SiteDTO]`

Get all sites with pagination and filtering - returns DTOs

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[SiteDTO]`

---

##### `get_all_sites_dto(self, page: int, size: int) → List[SiteDTO]`

Get all sites as DTOs with pagination

**Parameters:**

- `self`
- `page` (int)
- `size` (int)

**Returns:** `List[SiteDTO]`

---

##### `get_site_by_id(self, site_id: int) → Optional[Site]`

Get site by ID

**Parameters:**

- `self`
- `site_id` (int)

**Returns:** `Optional[Site]`

---

##### `get_site_by_name(self, site_name: str) → Optional[Site]`

Get site by name

**Parameters:**

- `self`
- `site_name` (str)

**Returns:** `Optional[Site]`

---

##### `get_site_dto_by_id(self, site_id: int) → Optional[SiteDTO]`

Get site by ID as DTO

**Parameters:**

- `self`
- `site_id` (int)

**Returns:** `Optional[SiteDTO]`

---

##### `get_site_statistics(self, site_id: int) → Dict[str, Any]`

Get statistics for a site

**Parameters:**

- `self`
- `site_id` (int)

**Returns:** `Dict[str, Any]`

---

##### `get_unique_countries(self) → List[str]`

Get list of unique countries

**Parameters:**

- `self`

**Returns:** `List[str]`

---

##### `get_unique_municipalities(self, nazione: Optional[str], regione: Optional[str]) → List[str]`

Get list of unique municipalities with optional filters

**Parameters:**

- `self`
- `nazione` (Optional[str])
- `regione` (Optional[str])

**Returns:** `List[str]`

---

##### `get_unique_regions(self, nazione: Optional[str]) → List[str]`

Get list of unique regions, optionally filtered by country

**Parameters:**

- `self`
- `nazione` (Optional[str])

**Returns:** `List[str]`

---

##### `search_sites(self, search_term: str, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[SiteDTO]`

Search sites by term - returns DTOs

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[SiteDTO]`

---

##### `update_site(self, site_id: int, update_data: Dict[str, Any]) → Site`

Update existing site

**Parameters:**

- `self`
- `site_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Site`

---

##### `update_site_dto(self, site_id: int, update_data: Dict[str, Any]) → Optional[SiteDTO]`

Update existing site and return DTO

**Parameters:**

- `self`
- `site_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Optional[SiteDTO]`

---


#### `SiteService`

Service class for site operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the SiteService class.  
This constructor method accepts a DatabaseManager object and assigns it to the instance for managing database operations related to site functionality.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_sites(self, filters: Optional[Dict[str, Any]]) → int`

Count sites with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `count_sites(self) → int`

Count total number of sites

**Parameters:**

- `self`

**Returns:** `int`

---

##### `create_site(self, site_data: Dict[str, Any]) → Site`

Create a new site

**Parameters:**

- `self`
- `site_data` (Dict[str, Any])

**Returns:** `Site`

---

##### `create_site_dto(self, site_data: Dict[str, Any]) → SiteDTO`

Create a new site and return as DTO

**Parameters:**

- `self`
- `site_data` (Dict[str, Any])

**Returns:** `SiteDTO`

---

##### `delete_site(self, site_id: int) → bool`

Delete site

**Parameters:**

- `self`
- `site_id` (int)

**Returns:** `bool`

---

##### `get_all_sites(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[SiteDTO]`

Get all sites with pagination and filtering - returns DTOs

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[SiteDTO]`

---

##### `get_all_sites_dto(self, page: int, size: int) → List[SiteDTO]`

Get all sites as DTOs with pagination

**Parameters:**

- `self`
- `page` (int)
- `size` (int)

**Returns:** `List[SiteDTO]`

---

##### `get_site_by_id(self, site_id: int) → Optional[Site]`

Get site by ID

**Parameters:**

- `self`
- `site_id` (int)

**Returns:** `Optional[Site]`

---

##### `get_site_by_name(self, site_name: str) → Optional[Site]`

Get site by name

**Parameters:**

- `self`
- `site_name` (str)

**Returns:** `Optional[Site]`

---

##### `get_site_dto_by_id(self, site_id: int) → Optional[SiteDTO]`

Get site by ID as DTO

**Parameters:**

- `self`
- `site_id` (int)

**Returns:** `Optional[SiteDTO]`

---

##### `get_site_statistics(self, site_id: int) → Dict[str, Any]`

Get statistics for a site

**Parameters:**

- `self`
- `site_id` (int)

**Returns:** `Dict[str, Any]`

---

##### `get_unique_countries(self) → List[str]`

Get list of unique countries

**Parameters:**

- `self`

**Returns:** `List[str]`

---

##### `get_unique_municipalities(self, nazione: Optional[str], regione: Optional[str]) → List[str]`

Get list of unique municipalities with optional filters

**Parameters:**

- `self`
- `nazione` (Optional[str])
- `regione` (Optional[str])

**Returns:** `List[str]`

---

##### `get_unique_regions(self, nazione: Optional[str]) → List[str]`

Get list of unique regions, optionally filtered by country

**Parameters:**

- `self`
- `nazione` (Optional[str])

**Returns:** `List[str]`

---

##### `search_sites(self, search_term: str, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[SiteDTO]`

Search sites by term - returns DTOs

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[SiteDTO]`

---

##### `update_site(self, site_id: int, update_data: Dict[str, Any]) → Site`

Update existing site

**Parameters:**

- `self`
- `site_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Site`

---

##### `update_site_dto(self, site_id: int, update_data: Dict[str, Any]) → Optional[SiteDTO]`

Update existing site and return DTO

**Parameters:**

- `self`
- `site_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Optional[SiteDTO]`

---



\newpage


## Module: `pyarchinit_mini/services/thesaurus_service.py`

**File Path:** `pyarchinit_mini/services/thesaurus_service.py`

### Classes

#### `ThesaurusService`

Service for managing thesaurus and controlled vocabularies

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes the service with the provided database manager instance.  
This constructor sets up the necessary database connection required for managing thesaurus and controlled vocabularies.  
It ensures that all subsequent operations within the service have access to the database through the specified DatabaseManager.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `add_field_value(self, table_name: str, field_name: str, value: str, label: Optional[str], description: Optional[str], language: str) → Dict[str, Any]`

Add a new vocabulary value for a field

Args:
    table_name: Database table name
    field_name: Field name
    value: The vocabulary value
    label: Human-readable label
    description: Description
    language: Language code
    
Returns:
    Created entry data

**Parameters:**

- `self`
- `table_name` (str)
- `field_name` (str)
- `value` (str)
- `label` (Optional[str])
- `description` (Optional[str])
- `language` (str)

**Returns:** `Dict[str, Any]`

---

##### `delete_field_value(self, field_id: int) → bool`

Delete a vocabulary value

Args:
    field_id: Field entry ID
    
Returns:
    True if deleted successfully

**Parameters:**

- `self`
- `field_id` (int)

**Returns:** `bool`

---

##### `get_field_values(self, table_name: str, field_name: str, language: str) → List[Dict[str, Any]]`

Get vocabulary values for a specific field

Args:
    table_name: Database table name
    field_name: Field name
    language: Language code
    
Returns:
    List of vocabulary entries

**Parameters:**

- `self`
- `table_name` (str)
- `field_name` (str)
- `language` (str)

**Returns:** `List[Dict[str, Any]]`

---

##### `get_table_fields(self, table_name: str) → List[str]`

Get list of fields that have thesaurus entries for a table

Args:
    table_name: Database table name
    
Returns:
    List of field names

**Parameters:**

- `self`
- `table_name` (str)

**Returns:** `List[str]`

---

##### `initialize_default_vocabularies(self) → bool`

Initialize default vocabularies from predefined mappings

Returns:
    True if initialized successfully

**Parameters:**

- `self`

**Returns:** `bool`

---

##### `search_values(self, query: str, table_name: Optional[str], field_name: Optional[str], language: str) → List[Dict[str, Any]]`

Search vocabulary values by query string

Args:
    query: Search query
    table_name: Optional table filter
    field_name: Optional field filter
    language: Language code
    
Returns:
    List of matching entries

**Parameters:**

- `self`
- `query` (str)
- `table_name` (Optional[str])
- `field_name` (Optional[str])
- `language` (str)

**Returns:** `List[Dict[str, Any]]`

---

##### `update_field_value(self, field_id: int, value: Optional[str], label: Optional[str], description: Optional[str]) → Dict[str, Any]`

Update an existing vocabulary value

Args:
    field_id: Field entry ID
    value: New value
    label: New label
    description: New description
    
Returns:
    Updated entry data

**Parameters:**

- `self`
- `field_id` (int)
- `value` (Optional[str])
- `label` (Optional[str])
- `description` (Optional[str])

**Returns:** `Dict[str, Any]`

---


#### `ThesaurusService`

Service for managing thesaurus and controlled vocabularies

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the service for managing thesaurus and controlled vocabularies.  
This constructor takes a DatabaseManager object as a parameter and assigns it to an instance variable for use in database operations throughout the service.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `add_field_value(self, table_name: str, field_name: str, value: str, label: Optional[str], description: Optional[str], language: str) → Dict[str, Any]`

Add a new vocabulary value for a field

Args:
    table_name: Database table name
    field_name: Field name
    value: The vocabulary value
    label: Human-readable label
    description: Description
    language: Language code
    
Returns:
    Created entry data

**Parameters:**

- `self`
- `table_name` (str)
- `field_name` (str)
- `value` (str)
- `label` (Optional[str])
- `description` (Optional[str])
- `language` (str)

**Returns:** `Dict[str, Any]`

---

##### `delete_field_value(self, field_id: int) → bool`

Delete a vocabulary value

Args:
    field_id: Field entry ID
    
Returns:
    True if deleted successfully

**Parameters:**

- `self`
- `field_id` (int)

**Returns:** `bool`

---

##### `get_field_values(self, table_name: str, field_name: str, language: str) → List[Dict[str, Any]]`

Get vocabulary values for a specific field

Args:
    table_name: Database table name
    field_name: Field name
    language: Language code
    
Returns:
    List of vocabulary entries

**Parameters:**

- `self`
- `table_name` (str)
- `field_name` (str)
- `language` (str)

**Returns:** `List[Dict[str, Any]]`

---

##### `get_table_fields(self, table_name: str) → List[str]`

Get list of fields that have thesaurus entries for a table

Args:
    table_name: Database table name
    
Returns:
    List of field names

**Parameters:**

- `self`
- `table_name` (str)

**Returns:** `List[str]`

---

##### `initialize_default_vocabularies(self) → bool`

Initialize default vocabularies from predefined mappings

Returns:
    True if initialized successfully

**Parameters:**

- `self`

**Returns:** `bool`

---

##### `search_values(self, query: str, table_name: Optional[str], field_name: Optional[str], language: str) → List[Dict[str, Any]]`

Search vocabulary values by query string

Args:
    query: Search query
    table_name: Optional table filter
    field_name: Optional field filter
    language: Language code
    
Returns:
    List of matching entries

**Parameters:**

- `self`
- `query` (str)
- `table_name` (Optional[str])
- `field_name` (Optional[str])
- `language` (str)

**Returns:** `List[Dict[str, Any]]`

---

##### `update_field_value(self, field_id: int, value: Optional[str], label: Optional[str], description: Optional[str]) → Dict[str, Any]`

Update an existing vocabulary value

Args:
    field_id: Field entry ID
    value: New value
    label: New label
    description: New description
    
Returns:
    Updated entry data

**Parameters:**

- `self`
- `field_id` (int)
- `value` (Optional[str])
- `label` (Optional[str])
- `description` (Optional[str])

**Returns:** `Dict[str, Any]`

---


#### `ThesaurusService`

Service for managing thesaurus and controlled vocabularies

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the service for managing thesaurus and controlled vocabularies.  
This method sets up the service with the provided DatabaseManager, enabling database operations required for vocabulary management.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `add_field_value(self, table_name: str, field_name: str, value: str, label: Optional[str], description: Optional[str], language: str) → Dict[str, Any]`

Add a new vocabulary value for a field

Args:
    table_name: Database table name
    field_name: Field name
    value: The vocabulary value
    label: Human-readable label
    description: Description
    language: Language code
    
Returns:
    Created entry data

**Parameters:**

- `self`
- `table_name` (str)
- `field_name` (str)
- `value` (str)
- `label` (Optional[str])
- `description` (Optional[str])
- `language` (str)

**Returns:** `Dict[str, Any]`

---

##### `delete_field_value(self, field_id: int) → bool`

Delete a vocabulary value

Args:
    field_id: Field entry ID
    
Returns:
    True if deleted successfully

**Parameters:**

- `self`
- `field_id` (int)

**Returns:** `bool`

---

##### `get_field_values(self, table_name: str, field_name: str, language: str) → List[Dict[str, Any]]`

Get vocabulary values for a specific field

Args:
    table_name: Database table name
    field_name: Field name
    language: Language code
    
Returns:
    List of vocabulary entries

**Parameters:**

- `self`
- `table_name` (str)
- `field_name` (str)
- `language` (str)

**Returns:** `List[Dict[str, Any]]`

---

##### `get_table_fields(self, table_name: str) → List[str]`

Get list of fields that have thesaurus entries for a table

Args:
    table_name: Database table name
    
Returns:
    List of field names

**Parameters:**

- `self`
- `table_name` (str)

**Returns:** `List[str]`

---

##### `initialize_default_vocabularies(self) → bool`

Initialize default vocabularies from predefined mappings

Returns:
    True if initialized successfully

**Parameters:**

- `self`

**Returns:** `bool`

---

##### `search_values(self, query: str, table_name: Optional[str], field_name: Optional[str], language: str) → List[Dict[str, Any]]`

Search vocabulary values by query string

Args:
    query: Search query
    table_name: Optional table filter
    field_name: Optional field filter
    language: Language code
    
Returns:
    List of matching entries

**Parameters:**

- `self`
- `query` (str)
- `table_name` (Optional[str])
- `field_name` (Optional[str])
- `language` (str)

**Returns:** `List[Dict[str, Any]]`

---

##### `update_field_value(self, field_id: int, value: Optional[str], label: Optional[str], description: Optional[str]) → Dict[str, Any]`

Update an existing vocabulary value

Args:
    field_id: Field entry ID
    value: New value
    label: New label
    description: New description
    
Returns:
    Updated entry data

**Parameters:**

- `self`
- `field_id` (int)
- `value` (Optional[str])
- `label` (Optional[str])
- `description` (Optional[str])

**Returns:** `Dict[str, Any]`

---



\newpage


## Module: `pyarchinit_mini/services/us_service.py`

**File Path:** `pyarchinit_mini/services/us_service.py`

### Classes

#### `USService`

Service class for US operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the USService class with the specified database manager.  
This constructor assigns the provided DatabaseManager instance to the service, enabling database operations related to US (stratigraphic unit) management.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_us(self, filters: Optional[Dict[str, Any]]) → int`

Count US with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_us(self, us_data: Dict[str, Any]) → US`

Create a new stratigraphic unit

**Parameters:**

- `self`
- `us_data` (Dict[str, Any])

**Returns:** `US`

---

##### `delete_us(self, us_id: int) → bool`

Delete US

**Parameters:**

- `self`
- `us_id` (int)

**Returns:** `bool`

---

##### `get_all_us(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[USDTO]`

Get all US with pagination and filtering - returns DTOs

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[USDTO]`

---

##### `get_us_by_id(self, us_id: int) → Optional[US]`

Get US by ID

**Parameters:**

- `self`
- `us_id` (int)

**Returns:** `Optional[US]`

---

##### `get_us_by_site(self, site_name: str, page: int, size: int) → List[USDTO]`

Get all US for a specific site - returns DTOs

**Parameters:**

- `self`
- `site_name` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[USDTO]`

---

##### `get_us_by_site_and_area(self, site_name: str, area: str, page: int, size: int) → List[USDTO]`

Get all US for a specific site and area - returns DTOs

**Parameters:**

- `self`
- `site_name` (str)
- `area` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[USDTO]`

---

##### `get_us_dto_by_id(self, us_id: int) → Optional[USDTO]`

Get US by ID as DTO

**Parameters:**

- `self`
- `us_id` (int)

**Returns:** `Optional[USDTO]`

---

##### `get_us_statistics(self, us_id: int) → Dict[str, Any]`

Get statistics for a US

**Parameters:**

- `self`
- `us_id` (int)

**Returns:** `Dict[str, Any]`

---

##### `search_us(self, search_term: str, page: int, size: int) → List[USDTO]`

Search US by term - returns DTOs

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[USDTO]`

---

##### `update_us(self, us_id: int, update_data: Dict[str, Any]) → US`

Update existing US

**Parameters:**

- `self`
- `us_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `US`

---

##### `update_us_dto(self, us_id: int, update_data: Dict[str, Any]) → Optional[USDTO]`

Update existing US and return DTO

**Parameters:**

- `self`
- `us_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Optional[USDTO]`

---


#### `USService`

Service class for US operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the USService class.  
This constructor method accepts a DatabaseManager object, which is stored as an instance attribute for managing database operations related to US services.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_us(self, filters: Optional[Dict[str, Any]]) → int`

Count US with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_us(self, us_data: Dict[str, Any]) → US`

Create a new stratigraphic unit

**Parameters:**

- `self`
- `us_data` (Dict[str, Any])

**Returns:** `US`

---

##### `create_us_dto(self, us_data: Dict[str, Any]) → USDTO`

Create a new US and return as DTO

**Parameters:**

- `self`
- `us_data` (Dict[str, Any])

**Returns:** `USDTO`

---

##### `delete_us(self, us_id: int) → bool`

Delete US

**Parameters:**

- `self`
- `us_id` (int)

**Returns:** `bool`

---

##### `get_all_us(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[USDTO]`

Get all US with pagination and filtering - returns DTOs

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[USDTO]`

---

##### `get_us_by_id(self, us_id: int) → Optional[US]`

Get US by ID

**Parameters:**

- `self`
- `us_id` (int)

**Returns:** `Optional[US]`

---

##### `get_us_by_site(self, site_name: str, page: int, size: int) → List[USDTO]`

Get all US for a specific site - returns DTOs

**Parameters:**

- `self`
- `site_name` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[USDTO]`

---

##### `get_us_by_site_and_area(self, site_name: str, area: str, page: int, size: int) → List[USDTO]`

Get all US for a specific site and area - returns DTOs

**Parameters:**

- `self`
- `site_name` (str)
- `area` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[USDTO]`

---

##### `get_us_dto_by_id(self, us_id: int) → Optional[USDTO]`

Get US by ID as DTO

**Parameters:**

- `self`
- `us_id` (int)

**Returns:** `Optional[USDTO]`

---

##### `get_us_statistics(self, us_id: int) → Dict[str, Any]`

Get statistics for a US

**Parameters:**

- `self`
- `us_id` (int)

**Returns:** `Dict[str, Any]`

---

##### `search_us(self, search_term: str, page: int, size: int) → List[USDTO]`

Search US by term - returns DTOs

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[USDTO]`

---

##### `update_us(self, us_id: int, update_data: Dict[str, Any]) → US`

Update existing US

**Parameters:**

- `self`
- `us_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `US`

---

##### `update_us_dto(self, us_id: int, update_data: Dict[str, Any]) → Optional[USDTO]`

Update existing US and return DTO

**Parameters:**

- `self`
- `us_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Optional[USDTO]`

---


#### `USService`

Service class for US operations

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the USService class.  
This constructor accepts a DatabaseManager object, which is assigned to the instance for managing database operations related to US services.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `count_us(self, filters: Optional[Dict[str, Any]]) → int`

Count US with optional filters

**Parameters:**

- `self`
- `filters` (Optional[Dict[str, Any]])

**Returns:** `int`

---

##### `create_us(self, us_data: Dict[str, Any]) → US`

Create a new stratigraphic unit

**Parameters:**

- `self`
- `us_data` (Dict[str, Any])

**Returns:** `US`

---

##### `create_us_dto(self, us_data: Dict[str, Any]) → USDTO`

Create a new US and return as DTO

**Parameters:**

- `self`
- `us_data` (Dict[str, Any])

**Returns:** `USDTO`

---

##### `delete_us(self, us_id: int) → bool`

Delete US

**Parameters:**

- `self`
- `us_id` (int)

**Returns:** `bool`

---

##### `get_all_us(self, page: int, size: int, filters: Optional[Dict[str, Any]]) → List[USDTO]`

Get all US with pagination and filtering - returns DTOs

**Parameters:**

- `self`
- `page` (int)
- `size` (int)
- `filters` (Optional[Dict[str, Any]])

**Returns:** `List[USDTO]`

---

##### `get_us_by_id(self, us_id: int) → Optional[US]`

Get US by ID

**Parameters:**

- `self`
- `us_id` (int)

**Returns:** `Optional[US]`

---

##### `get_us_by_site(self, site_name: str, page: int, size: int) → List[USDTO]`

Get all US for a specific site - returns DTOs

**Parameters:**

- `self`
- `site_name` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[USDTO]`

---

##### `get_us_by_site_and_area(self, site_name: str, area: str, page: int, size: int) → List[USDTO]`

Get all US for a specific site and area - returns DTOs

**Parameters:**

- `self`
- `site_name` (str)
- `area` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[USDTO]`

---

##### `get_us_dto_by_id(self, us_id: int) → Optional[USDTO]`

Get US by ID as DTO

**Parameters:**

- `self`
- `us_id` (int)

**Returns:** `Optional[USDTO]`

---

##### `get_us_statistics(self, us_id: int) → Dict[str, Any]`

Get statistics for a US

**Parameters:**

- `self`
- `us_id` (int)

**Returns:** `Dict[str, Any]`

---

##### `search_us(self, search_term: str, page: int, size: int) → List[USDTO]`

Search US by term - returns DTOs

**Parameters:**

- `self`
- `search_term` (str)
- `page` (int)
- `size` (int)

**Returns:** `List[USDTO]`

---

##### `update_us(self, us_id: int, update_data: Dict[str, Any]) → US`

Update existing US

**Parameters:**

- `self`
- `us_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `US`

---

##### `update_us_dto(self, us_id: int, update_data: Dict[str, Any]) → Optional[USDTO]`

Update existing US and return DTO

**Parameters:**

- `self`
- `us_id` (int)
- `update_data` (Dict[str, Any])

**Returns:** `Optional[USDTO]`

---



\newpage


## Module: `pyarchinit_mini/utils/__init__.py`

**File Path:** `pyarchinit_mini/utils/__init__.py`


\newpage


## Module: `pyarchinit_mini/utils/exceptions.py`

**File Path:** `pyarchinit_mini/utils/exceptions.py`

### Classes

#### `ConfigurationError`

Raised when configuration is invalid

**Inherits from:** `PyArchInitMiniError`


#### `ConfigurationError`

Raised when configuration is invalid

**Inherits from:** `PyArchInitMiniError`


#### `ConfigurationError`

Raised when configuration is invalid

**Inherits from:** `PyArchInitMiniError`


#### `ConnectionError`

Raised when database connection fails

**Inherits from:** `PyArchInitMiniError`


#### `ConnectionError`

Raised when database connection fails

**Inherits from:** `PyArchInitMiniError`


#### `ConnectionError`

Raised when database connection fails

**Inherits from:** `PyArchInitMiniError`


#### `DatabaseError`

Raised when database operations fail

**Inherits from:** `PyArchInitMiniError`


#### `DatabaseError`

Raised when database operations fail

**Inherits from:** `PyArchInitMiniError`


#### `DatabaseError`

Raised when database operations fail

**Inherits from:** `PyArchInitMiniError`


#### `DuplicateRecordError`

Raised when trying to create a duplicate record

**Inherits from:** `PyArchInitMiniError`


#### `DuplicateRecordError`

Raised when trying to create a duplicate record

**Inherits from:** `PyArchInitMiniError`


#### `DuplicateRecordError`

Raised when trying to create a duplicate record

**Inherits from:** `PyArchInitMiniError`


#### `PermissionError`

Raised when user lacks required permissions

**Inherits from:** `PyArchInitMiniError`


#### `PermissionError`

Raised when user lacks required permissions

**Inherits from:** `PyArchInitMiniError`


#### `PermissionError`

Raised when user lacks required permissions

**Inherits from:** `PyArchInitMiniError`


#### `PyArchInitMiniError`

Base exception class for PyArchInit-Mini

**Inherits from:** `Exception`


#### `PyArchInitMiniError`

Base exception class for PyArchInit-Mini

**Inherits from:** `Exception`


#### `PyArchInitMiniError`

Base exception class for PyArchInit-Mini

**Inherits from:** `Exception`


#### `RecordNotFoundError`

Raised when a requested record is not found

**Inherits from:** `PyArchInitMiniError`


#### `RecordNotFoundError`

Raised when a requested record is not found

**Inherits from:** `PyArchInitMiniError`


#### `RecordNotFoundError`

Raised when a requested record is not found

**Inherits from:** `PyArchInitMiniError`


#### `ValidationError`

Raised when data validation fails

**Inherits from:** `PyArchInitMiniError`

**Methods:**

##### `__init__(self, message: str, field: str, value)`

Initializes a new instance of the ValidationError class. This method sets the error message, and optionally associates the error with a specific field and value that caused the validation to fail. It also calls the initializer of the base exception class with the provided message.

**Parameters:**

- `self`
- `message` (str)
- `field` (str)
- `value`

---


#### `ValidationError`

Raised when data validation fails

**Inherits from:** `PyArchInitMiniError`

**Methods:**

##### `__init__(self, message: str, field: str, value)`

Initializes a new instance of the ValidationError class with a specified error message, and optionally the field and value that caused the validation to fail. This constructor also calls the base class initializer with the provided message, and stores the field and value information for further context about the validation error.

**Parameters:**

- `self`
- `message` (str)
- `field` (str)
- `value`

---


#### `ValidationError`

Raised when data validation fails

**Inherits from:** `PyArchInitMiniError`

**Methods:**

##### `__init__(self, message: str, field: str, value)`

Initializes a new instance of the **ValidationError** class with a specified error message, and optionally the name of the field and its associated value that caused the validation to fail.  
This constructor passes the error message to the base exception class and stores the field and value information for further context about the validation error.

**Parameters:**

- `self`
- `message` (str)
- `field` (str)
- `value`

---



\newpage


## Module: `pyarchinit_mini/utils/validators.py`

**File Path:** `pyarchinit_mini/utils/validators.py`

### Classes

#### `BaseValidator`

Base validator class

**Methods:**

##### `validate_numeric_range(value, field_name: str, min_value, max_value)`

Validate numeric value is within range

**Parameters:**

- `value`
- `field_name` (str)
- `min_value`
- `max_value`

**Decorators:** `staticmethod`

---

##### `validate_required_fields(data: Dict[str, Any], required_fields: List[str])`

Validate that all required fields are present and not empty

**Parameters:**

- `data` (Dict[str, Any])
- `required_fields` (List[str])

**Decorators:** `staticmethod`

---

##### `validate_string_length(value: str, field_name: str, max_length: int, min_length: int)`

Validate string length

**Parameters:**

- `value` (str)
- `field_name` (str)
- `max_length` (int)
- `min_length` (int)

**Decorators:** `staticmethod`

---


#### `BaseValidator`

Base validator class

**Methods:**

##### `validate_numeric_range(value, field_name: str, min_value, max_value)`

Validate numeric value is within range

**Parameters:**

- `value`
- `field_name` (str)
- `min_value`
- `max_value`

**Decorators:** `staticmethod`

---

##### `validate_required_fields(data: Dict[str, Any], required_fields: List[str])`

Validate that all required fields are present and not empty

**Parameters:**

- `data` (Dict[str, Any])
- `required_fields` (List[str])

**Decorators:** `staticmethod`

---

##### `validate_string_length(value: str, field_name: str, max_length: int, min_length: int)`

Validate string length

**Parameters:**

- `value` (str)
- `field_name` (str)
- `max_length` (int)
- `min_length` (int)

**Decorators:** `staticmethod`

---


#### `BaseValidator`

Base validator class

**Methods:**

##### `validate_numeric_range(value, field_name: str, min_value, max_value)`

Validate numeric value is within range

**Parameters:**

- `value`
- `field_name` (str)
- `min_value`
- `max_value`

**Decorators:** `staticmethod`

---

##### `validate_required_fields(data: Dict[str, Any], required_fields: List[str])`

Validate that all required fields are present and not empty

**Parameters:**

- `data` (Dict[str, Any])
- `required_fields` (List[str])

**Decorators:** `staticmethod`

---

##### `validate_string_length(value: str, field_name: str, max_length: int, min_length: int)`

Validate string length

**Parameters:**

- `value` (str)
- `field_name` (str)
- `max_length` (int)
- `min_length` (int)

**Decorators:** `staticmethod`

---


#### `InventarioValidator`

Validator for Inventario Materiali model data

**Inherits from:** `BaseValidator`

**Methods:**

##### `validate(cls, data: Dict[str, Any])`

Validate inventory material data

**Parameters:**

- `cls`
- `data` (Dict[str, Any])

**Decorators:** `classmethod`

---


#### `InventarioValidator`

Validator for Inventario Materiali model data

**Inherits from:** `BaseValidator`

**Methods:**

##### `validate(cls, data: Dict[str, Any])`

Validate inventory material data

**Parameters:**

- `cls`
- `data` (Dict[str, Any])

**Decorators:** `classmethod`

---


#### `InventarioValidator`

Validator for Inventario Materiali model data

**Inherits from:** `BaseValidator`

**Methods:**

##### `validate(cls, data: Dict[str, Any])`

Validate inventory material data

**Parameters:**

- `cls`
- `data` (Dict[str, Any])

**Decorators:** `classmethod`

---


#### `SiteValidator`

Validator for Site model data

**Inherits from:** `BaseValidator`

**Methods:**

##### `validate(cls, data: Dict[str, Any])`

Validate site data

**Parameters:**

- `cls`
- `data` (Dict[str, Any])

**Decorators:** `classmethod`

---


#### `SiteValidator`

Validator for Site model data

**Inherits from:** `BaseValidator`

**Methods:**

##### `validate(cls, data: Dict[str, Any])`

Validate site data

**Parameters:**

- `cls`
- `data` (Dict[str, Any])

**Decorators:** `classmethod`

---


#### `SiteValidator`

Validator for Site model data

**Inherits from:** `BaseValidator`

**Methods:**

##### `validate(cls, data: Dict[str, Any])`

Validate site data

**Parameters:**

- `cls`
- `data` (Dict[str, Any])

**Decorators:** `classmethod`

---


#### `USValidator`

Validator for US (Stratigraphic Unit) model data

**Inherits from:** `BaseValidator`

**Methods:**

##### `validate(cls, data: Dict[str, Any])`

Validate US data

**Parameters:**

- `cls`
- `data` (Dict[str, Any])

**Decorators:** `classmethod`

---


#### `USValidator`

Validator for US (Stratigraphic Unit) model data

**Inherits from:** `BaseValidator`

**Methods:**

##### `validate(cls, data: Dict[str, Any])`

Validate US data

**Parameters:**

- `cls`
- `data` (Dict[str, Any])

**Decorators:** `classmethod`

---


#### `USValidator`

Validator for US (Stratigraphic Unit) model data

**Inherits from:** `BaseValidator`

**Methods:**

##### `validate(cls, data: Dict[str, Any])`

Validate US data

**Parameters:**

- `cls`
- `data` (Dict[str, Any])

**Decorators:** `classmethod`

---


### Functions

#### `validate_data(model_type: str, data: Dict[str, Any])`

Validate data based on model type

Args:
    model_type: Type of model ('site', 'us', 'inventario')
    data: Data to validate

Raises:
    ValidationError: If validation fails

**Parameters:**

- `model_type` (str)
- `data` (Dict[str, Any])

---

#### `validate_data(model_type: str, data: Dict[str, Any])`

Validate data based on model type

Args:
    model_type: Type of model ('site', 'us', 'inventario')
    data: Data to validate

Raises:
    ValidationError: If validation fails

**Parameters:**

- `model_type` (str)
- `data` (Dict[str, Any])

---

#### `validate_data(model_type: str, data: Dict[str, Any])`

Validate data based on model type

Args:
    model_type: Type of model ('site', 'us', 'inventario')
    data: Data to validate

Raises:
    ValidationError: If validation fails

**Parameters:**

- `model_type` (str)
- `data` (Dict[str, Any])

---


\newpage


## Module: `run_gui.py`

**File Path:** `run_gui.py`

### Functions

#### `main()`

Launch the desktop GUI

---

#### `main()`

Launch the desktop GUI

---

#### `main()`

Launch the desktop GUI

---


\newpage


## Module: `scripts/load_sample_as_main.py`

**File Path:** `scripts/load_sample_as_main.py`

### Functions

#### `load_sample_database()`

Copy sample database as main database

---

#### `load_sample_database()`

Copy sample database as main database

---


\newpage


## Module: `scripts/populate_sample_data.py`

**File Path:** `scripts/populate_sample_data.py`

### Classes

#### `SampleDataGenerator`

Generator for archaeological sample data

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the `SampleDataGenerator` class by setting up predefined data attributes used for generating archaeological sample data. This includes references to the database manager, site information, lists of areas, archaeological periods, formation types, material types, and relevant descriptive categories.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `create_materials(self, us_records)`

Create 50 material records distributed across US

**Parameters:**

- `self`
- `us_records`

---

##### `create_periodization(self, us_records, periods)`

Create periodization assignments for US

**Parameters:**

- `self`
- `us_records`
- `periods`

---

##### `create_periods(self)`

Create archaeological periods

**Parameters:**

- `self`

---

##### `create_site(self)`

Create the sample archaeological site

**Parameters:**

- `self`

---

##### `create_stratigraphic_relationships(self, us_records)`

Create realistic stratigraphic relationships

**Parameters:**

- `self`
- `us_records`

---

##### `create_thesaurus(self)`

Create thesaurus entries

**Parameters:**

- `self`

---

##### `create_us_records(self, site)`

Create 100 US records with realistic stratigraphic data

**Parameters:**

- `self`
- `site`

---

##### `generate_all_data(self)`

Generate complete sample dataset

**Parameters:**

- `self`

---


#### `SampleDataGenerator`

Generator for archaeological sample data

**Methods:**

##### `__init__(self, db_manager: DatabaseManager)`

Initializes a new instance of the SampleDataGenerator class with predefined attributes for generating archaeological sample data. This constructor sets up references to the database manager, site name, and various lists representing archaeological periods, formation types, material types, and related properties used in sample data generation.

**Parameters:**

- `self`
- `db_manager` (DatabaseManager)

---

##### `create_materials(self, us_records)`

Create 50 material records distributed across US

**Parameters:**

- `self`
- `us_records`

---

##### `create_periodization(self, us_records, periods)`

Create periodization assignments for US

**Parameters:**

- `self`
- `us_records`
- `periods`

---

##### `create_periods(self)`

Create archaeological periods

**Parameters:**

- `self`

---

##### `create_site(self)`

Create the sample archaeological site

**Parameters:**

- `self`

---

##### `create_stratigraphic_relationships(self, us_records)`

Create realistic stratigraphic relationships

**Parameters:**

- `self`
- `us_records`

---

##### `create_thesaurus(self)`

Create thesaurus entries

**Parameters:**

- `self`

---

##### `create_us_records(self, site)`

Create 100 US records with realistic stratigraphic data

**Parameters:**

- `self`
- `site`

---

##### `generate_all_data(self)`

Generate complete sample dataset

**Parameters:**

- `self`

---


### Functions

#### `main()`

Main function to run sample data generation

---

#### `main()`

Main function to run sample data generation

---


\newpage


## Module: `scripts/populate_simple_data.py`

**File Path:** `scripts/populate_simple_data.py`

### Functions

#### `create_sample_data(clean_first)`

Create all sample data

**Parameters:**

- `clean_first`

---

#### `create_sample_data(clean_first)`

Create all sample data

**Parameters:**

- `clean_first`

---


\newpage


## Module: `setup.py`

**File Path:** `setup.py`


\newpage


## Module: `web_interface/app.py`

**File Path:** `web_interface/app.py`

### Classes

#### `InventarioForm`

The `InventarioForm` class defines a structured web form for recording and managing inventory data of archaeological artifacts within a Flask application. It captures essential details such as site, inventory number, artifact type, definition, description, area, stratigraphic unit (US), and weight. The form ensures data integrity through field validations and standardized input choices for consistent cataloging.

**Inherits from:** `FlaskForm`


#### `InventarioForm`

The `InventarioForm` class defines a web form for managing archaeological inventory records using Flask-WTF. It allows users to input and validate key artifact information such as site, inventory number, artifact type, definition, description, area, stratigraphic unit (US), and weight. This form ensures structured data entry for cataloging artifacts in an archaeological database.

**Inherits from:** `FlaskForm`


#### `InventarioForm`

The `InventarioForm` class defines a Flask-WTF form for recording and managing archaeological inventory data. It includes fields for selecting a site, entering inventory numbers, specifying artifact type, providing definitions and descriptions, and recording contextual details such as area, stratigraphic unit (US), and weight. This form ensures structured data input for cataloging archaeological finds within a web application.

**Inherits from:** `FlaskForm`


#### `MediaUploadForm`

The `MediaUploadForm` class is a Flask-WTF form designed for uploading media files and associating them with specific entities within an application, such as a site, US, or inventory item. It collects essential metadata including the entity type and ID, the media file itself, an optional description, and author or photographer information. This form ensures all required fields are validated before processing uploads.

**Inherits from:** `FlaskForm`


#### `MediaUploadForm`

The `MediaUploadForm` class is a Flask-WTF form designed to facilitate the upload of media files associated with specific entities, such as sites, US (stratigraphic units), or inventory items. It allows users to specify the entity type and ID, upload a file, and optionally provide a description and author information. This form ensures that all required fields are validated before accepting the upload.

**Inherits from:** `FlaskForm`


#### `MediaUploadForm`

The `MediaUploadForm` class defines a Flask-WTF form used for uploading media files associated with different entities (such as sites, US, or inventory items) within a web application. It collects essential metadata about the upload, including the entity type and ID, the file itself, an optional description, and the author's name. This form ensures that all required information is provided and properly validated before processing the upload.

**Inherits from:** `FlaskForm`


#### `SiteForm`

The `SiteForm` class is a Flask-WTF form used to collect and validate information about archaeological sites within a web application. It includes fields for site name, country, region, municipality, province, site definition, and a description, ensuring required data such as the site name is provided. This form facilitates standardized data entry for site records in the application.

**Inherits from:** `FlaskForm`


#### `SiteForm`

The **SiteForm** class is a Flask-WTF form used to collect and validate information about archaeological sites. It includes fields for site name, country, region, municipality, province, site definition, and a description. This form ensures that required data, such as the site name, is provided by the user before submission.

**Inherits from:** `FlaskForm`


#### `SiteForm`

The `SiteForm` class is a Flask-WTF form designed for collecting and validating archaeological site information. It includes fields for site name, country, region, municipality, province, site definition, and a descriptive text, ensuring essential data is captured for each site entry. The form utilizes standard field types and validators to facilitate structured and accurate input.

**Inherits from:** `FlaskForm`


#### `USForm`

The **USForm** class defines a structured web form for recording and managing archaeological stratigraphic units ("Unità Stratigrafiche") using Flask-WTF. It collects detailed information such as site, area, stratigraphic and interpretive descriptions, inventory numbers, excavation year, and formation type. This form ensures standardized data entry for stratigraphic records in archaeological projects.

**Inherits from:** `FlaskForm`


#### `USForm`

The `USForm` class is a Flask-WTF form designed for recording and managing archaeological stratigraphic unit (US) data within a web application. It collects detailed information such as site, area, stratigraphic and interpretative descriptions, excavation year, and other relevant metadata, ensuring comprehensive documentation of each stratigraphic unit. The form employs validation to ensure required fields are properly completed for accurate data entry.

**Inherits from:** `FlaskForm`


#### `USForm`

The **USForm** class is a Flask-WTF form designed for the input and management of archaeological stratigraphic unit (US) data within a web application. It facilitates the collection of detailed information such as site, area, US number, stratigraphic and interpretative descriptions, excavation year, and formation type. This form ensures data integrity by enforcing required fields and standardized choices for key attributes.

**Inherits from:** `FlaskForm`


### Functions

#### `api_sites()`

The `api_sites` function is a Flask route handler that serves as an API endpoint at `/api/sites`. It retrieves up to 100 site records using the `site_service.get_all_sites` method and returns a JSON-formatted list of sites, where each site is represented by its `id` and `name` attributes. This endpoint is typically used for AJAX requests to dynamically fetch site information.

**Decorators:** `app.route`

---

#### `api_sites()`

The `api_sites` function is a Flask route handler that provides an API endpoint at `/api/sites`. When accessed, it retrieves up to 100 site records using the `site_service.get_all_sites` method and returns a JSON array containing the ID and name of each site. This endpoint is typically used for AJAX requests to populate site data dynamically in client-side applications.

**Decorators:** `app.route`

---

#### `api_sites()`

The `api_sites` function is a Flask route that provides an API endpoint at `/api/sites`. When accessed, it retrieves up to 100 site records using the `site_service`, and returns a JSON array containing the `id` and `name` of each site. This endpoint is typically used for AJAX requests to fetch site information dynamically.

**Decorators:** `app.route`

---

#### `create_app()`

The `create_app` function initializes and configures a Flask web application for managing archaeological site data, stratigraphic units (US), inventories, Harris matrices, and media uploads. It sets up the application configuration, database connections, service layers, and all primary routes for site management, data visualization, PDF export, and media handling. This function returns the fully configured Flask app instance, ready to be run as a web server.

---

#### `create_app()`

**Description:**

The `create_app` function initializes and configures a Flask web application for managing archaeological site data. It sets up application configuration, database connections, and service objects, and defines routes for CRUD operations on sites, stratigraphic units (US), inventory, Harris matrix generation, PDF export, media uploads, and API endpoints. This function serves as the main entry point for building and running the application.

---

#### `create_app()`

The **`create_app`** function initializes and configures a Flask web application for managing archaeological site data, including sites, stratigraphic units (US), inventories, Harris matrices, and media uploads. It sets up essential configuration, database connections, service layers, and registers all routes for CRUD operations, data visualization, PDF export, and API endpoints. This function returns a fully configured Flask app instance ready to be run.

---

#### `create_inventario()`

The `create_inventario` function handles the creation of a new inventory record ("reperto") via a web form in a Flask application. It displays the form to the user, populates site choices, validates submitted data, and, upon successful validation, creates the inventory record using the provided service. If the creation is successful, it flashes a success message and redirects to the inventory list; otherwise, it displays an error message.

**Decorators:** `app.route`

---

#### `create_inventario()`

The `create_inventario` function handles the creation of a new inventory record ("reperto") via a web form in a Flask application. It displays a form for entering inventory details, populates site choices dynamically, validates submitted data, and, upon successful submission, saves the new record using the inventory service. If creation is successful, it flashes a success message and redirects to the inventory list; otherwise, it handles errors and redisplays the form.

**Decorators:** `app.route`

---

#### `create_inventario()`

The `create_inventario` function handles the creation of new inventory records (reperti) through a web form in a Flask application. It displays the form, populates site choices dynamically, validates user input, and upon successful submission, saves the new item to the database and provides user feedback. If any error occurs during the process, it flashes an error message and re-displays the form.

**Decorators:** `app.route`

---

#### `create_site()`

The `create_site` function handles the creation of a new site record via a web form in a Flask application. It processes both GET and POST requests: displaying the empty form on GET, and validating and saving the form data on POST. Upon successful creation, it flashes a success message and redirects to the sites list; otherwise, it renders the form with error messages as needed.

**Decorators:** `app.route`

---

#### `create_site()`

The `create_site` function handles the creation of a new site record within the web application. It displays a form for user input, validates and processes the form submission, creates the site using the provided data, and provides user feedback on success or failure. Upon successful creation, it redirects to the site listing page; otherwise, it re-renders the form with error messages if needed.

**Decorators:** `app.route`

---

#### `create_site()`

The `create_site` function handles the creation of a new site record via a web form within a Flask application. It displays the site creation form to the user, validates the submitted data, and, upon successful validation, saves the new site using the `site_service`. On success or failure, it provides user feedback and redirects appropriately.

**Decorators:** `app.route`

---

#### `create_us()`

The `create_us` function handles the creation of a new "US" (Unità Stratigrafica) record via a web form in a Flask application. It displays the form for input, populates site choices, validates submitted data, and, upon successful validation, creates the new record using the provided service. If creation is successful, it redirects to the US list page with a success message; otherwise, it displays appropriate error messages.

**Decorators:** `app.route`

---

#### `create_us()`

The `create_us` function handles the creation of a new "US" (Unità Stratigrafica) record via a web form. It displays the form to the user, populates site choices dynamically, validates the submitted data, and, upon successful validation, saves the new record using the `us_service`. If creation is successful, it flashes a success message and redirects to the US list; otherwise, it displays any errors encountered.

**Decorators:** `app.route`

---

#### `create_us()`

The `create_us` function handles the creation of a new "US" (Unità Stratigrafica) record via a web form in a Flask application. It displays the form to the user, populates the site selection options, processes form submissions, and saves the new record to the database if validation succeeds, providing user feedback through flash messages. Upon successful creation, it redirects the user to the list of US records.

**Decorators:** `app.route`

---

#### `export_site_pdf(site_id)`

The `export_site_pdf` function generates and downloads a PDF report containing detailed information about a specific site, including its associated US (stratigraphic units) and inventory records. When accessed via the `/export/site_pdf/<site_id>` route, it retrieves the site's data, compiles it into a PDF using a PDF generator, and returns the PDF file as a download to the user. If the site is not found or an error occurs during the process, the user is redirected with an appropriate error message.

**Parameters:**

- `site_id`

**Decorators:** `app.route`

---

#### `export_site_pdf(site_id)`

The `export_site_pdf` function handles the export of a PDF report for a specific site, identified by its `site_id`. It retrieves the site's details and related data, generates a comprehensive PDF report, and sends the PDF as a downloadable file to the user. If the site is not found or an error occurs during export, the user is redirected with an appropriate error message.

**Parameters:**

- `site_id`

**Decorators:** `app.route`

---

#### `export_site_pdf(site_id)`

The `export_site_pdf` function generates and exports a PDF report for a specific site, identified by its `site_id`. It retrieves the site's data along with related records, generates a comprehensive PDF report, and sends the file to the user as a downloadable attachment. If an error occurs or the site is not found, the function displays an appropriate error message and redirects the user accordingly.

**Parameters:**

- `site_id`

**Decorators:** `app.route`

---

#### `harris_matrix(site_name)`

The `harris_matrix` function is a Flask route handler that generates and displays the Harris Matrix for a given archaeological site, identified by `site_name`. It creates the matrix graph, calculates its levels and statistics, and renders a visualization, all of which are presented in the 'harris_matrix/view.html' template. If an error occurs during this process, the function flashes an error message and redirects the user to the site list page.

**Parameters:**

- `site_name`

**Decorators:** `app.route`

---

#### `harris_matrix(site_name)`

The `harris_matrix` function is a Flask route that generates and displays the Harris Matrix for a given archaeological site, identified by `site_name`. It constructs the matrix graph, calculates its levels and statistical data, creates a visual representation, and renders these results in a dedicated template. If an error occurs during processing, it displays an error message and redirects the user to the sites list.

**Parameters:**

- `site_name`

**Decorators:** `app.route`

---

#### `harris_matrix(site_name)`

The **harris_matrix** function is a Flask route that generates and displays the Harris Matrix for a given archaeological site, identified by its site name. It constructs the matrix graph, computes relevant levels and statistics, creates a visualization, and then renders these details in the 'harris_matrix/view.html' template. If an error occurs during processing, it flashes an error message and redirects the user to the site list page.

**Parameters:**

- `site_name`

**Decorators:** `app.route`

---

#### `index()`

Dashboard with statistics

**Decorators:** `app.route`

---

#### `index()`

Dashboard with statistics

**Decorators:** `app.route`

---

#### `index()`

Dashboard with statistics

**Decorators:** `app.route`

---

#### `inventario_list()`

The `inventario_list` function handles the `/inventario` route and displays a paginated list of inventory items, allowing optional filtering by site (`sito`) and item type (`tipo`). It retrieves the relevant inventory data and available site options, then renders the `inventario/list.html` template with the filtered results and pagination details.

**Decorators:** `app.route`

---

#### `inventario_list()`

The `inventario_list` function handles the `/inventario` route and displays a paginated list of inventory items, with optional filtering by site (`sito`) and item type (`tipo`). It retrieves the relevant inventory data and available site options, then renders the `inventario/list.html` template with the resulting list, filters, and pagination information.

**Decorators:** `app.route`

---

#### `inventario_list()`

The `inventario_list` function handles the `/inventario` route and displays a paginated list of inventory items, with optional filters for site (`sito`) and item type (`tipo`). It retrieves the relevant inventory data and site options, then renders the `inventario/list.html` template with the filtered results and pagination details. This view facilitates browsing and filtering of inventory records within the application.

**Decorators:** `app.route`

---

#### `sites_list()`

The `sites_list` function handles HTTP GET requests to the `/sites` route, displaying a paginated list of sites. It supports optional search functionality via a query parameter and renders the `sites/list.html` template with the retrieved sites, total count, current page, and search term.

**Decorators:** `app.route`

---

#### `sites_list()`

The `sites_list` function handles requests to the `/sites` route, displaying a paginated list of sites. It supports optional search functionality, retrieves the relevant sites from the database, and renders the `sites/list.html` template with the sites, pagination details, and search query.

**Decorators:** `app.route`

---

#### `sites_list()`

The `sites_list` function handles the `/sites` route and displays a paginated list of sites, optionally filtered by a search query provided via the request parameters. It retrieves the relevant site data and the total count of sites from the `site_service`, then renders the 'sites/list.html' template with this information along with the current page and search term.

**Decorators:** `app.route`

---

#### `upload_media()`

The `upload_media` function handles both the display and processing of a media upload form. It allows users to upload a media file associated with a specific entity, temporarily saves and processes the file, stores its metadata using a media handler, and provides user feedback on the upload status. On successful upload, it also manages cleanup of the temporary file and redirects the user back to the upload page.

**Decorators:** `app.route`

---

#### `upload_media()`

The `upload_media` function handles the uploading of media files through a web form. It processes both GET and POST requests, validates the submitted form, saves the uploaded file temporarily, and delegates storage to a media handler with associated metadata. Upon successful upload, it provides user feedback and redirects, while handling errors gracefully and rendering the upload form as needed.

**Decorators:** `app.route`

---

#### `upload_media()`

The `upload_media` function handles the uploading of media files via a web form. It processes both GET and POST requests: displaying the upload form, validating submitted data, securely saving the uploaded file temporarily, and delegating the file storage to a media handler along with associated metadata. Upon successful upload or error, it provides user feedback and redirects appropriately.

**Decorators:** `app.route`

---

#### `us_list()`

The `us_list` function is a Flask route handler that displays a paginated list of US records, optionally filtered by a site parameter provided via query string. It retrieves the filtered data and total count from the `us_service`, fetches available sites for filtering from `site_service`, and renders them in the `us/list.html` template along with pagination and filter information.

**Decorators:** `app.route`

---

#### `us_list()`

The `us_list` function handles the `/us` route and displays a paginated list of "us" records, optionally filtered by site (`sito`). It retrieves the current page number and filter parameters from the request, fetches the filtered list and total count from the service layer, and renders the results along with available sites in the `us/list.html` template.

**Decorators:** `app.route`

---

#### `us_list()`

The `us_list` function handles the `/us` route and displays a paginated list of "US" entries, with optional filtering by site ("sito"). It retrieves the relevant data from the service layer, gathers site options for filtering, and renders the `us/list.html` template with the results and filter parameters.

**Decorators:** `app.route`

---

#### `view_site(site_id)`

The **`view_site`** function handles requests to display detailed information about a specific site identified by its `site_id`. It retrieves the site's data along with related US records and inventory items, and renders them in the `sites/detail.html` template. If the site is not found, it flashes an error message and redirects the user to the site list page.

**Parameters:**

- `site_id`

**Decorators:** `app.route`

---

#### `view_site(site_id)`

The `view_site` function handles the display of detailed information for a specific site identified by its `site_id`. It retrieves the site's data along with related US and inventory records; if the site is not found, the user is redirected with an error message. Upon successful retrieval, it renders the detail page with all relevant information displayed.

**Parameters:**

- `site_id`

**Decorators:** `app.route`

---

#### `view_site(site_id)`

The `view_site` function handles requests to display the details of a specific site identified by `site_id`. It retrieves the site's information, along with related US and inventory records, and renders them in the `sites/detail.html` template. If the site does not exist, the user is notified and redirected to the list of sites.

**Parameters:**

- `site_id`

**Decorators:** `app.route`

---


\newpage

