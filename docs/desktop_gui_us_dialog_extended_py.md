# desktop_gui/us_dialog_extended.py

## Overview

This file contains 195 documented elements.

## Classes

### ExtendedUSDialog

Extended US dialog with multiple tabs for complete archaeological recording

#### Methods

##### __init__(self, parent, us_service, site_service, matrix_generator, periodizzazione_service, site_names, us, callback)

Initializes the extended US dialog window for comprehensive archaeological recording, setting up the necessary services, data structures, and user interface elements. This constructor configures the dialog as either a new entry or an edit form (depending on the provided US object), establishes the window properties, and prepares the interface for user interaction. If editing an existing US, it also pre-populates the form with relevant data.

##### create_interface(self)

Create the main interface with tabs

##### create_basic_tab(self)

Create basic information tab

##### create_description_tab(self)

Create descriptions tab

##### create_physical_tab(self)

Create physical characteristics tab

##### create_chronology_tab(self)

Create chronology/periodization tab

##### create_relationships_tab(self)

Create stratigraphic relationships tab

##### create_media_tab(self)

Create media management tab with thumbnails and drag & drop

##### create_documentation_tab(self)

Create documentation tab

##### populate_form(self)

Populate form with existing US data

##### load_relationships(self)

Load stratigraphic relationships for current US

##### add_relationship(self)

Add new stratigraphic relationship

##### edit_relationship(self)

Edit selected relationship

##### delete_relationship(self)

Delete selected relationship

##### open_harris_editor(self)

Open Harris Matrix editor

##### open_periodization_dialog(self)

Open detailed periodization dialog

##### refresh_periodization_data(self)

Refresh periodization data in form

##### show_chronological_sequence(self)

Show chronological sequence for site

##### create_media_directory(self)

Create media directory structure

##### setup_drag_drop(self)

Setup drag and drop functionality

##### on_drop_click(self, event)

Handle click on drop area

##### on_file_drop(self, event)

Handle file drop

##### process_dropped_file(self, file_path)

Process a dropped file

##### create_thumbnail(self, file_path)

Create thumbnail for image files

##### load_media_grid(self)

Load media files in grid with thumbnails

##### create_media_item(self, filename, row, col)

Create a media item widget

##### create_file_icon(self, filename)

Create a generic file icon

##### format_file_size(self, size_bytes)

Format file size in human readable format

##### on_media_select(self, filename)

Handle media item selection

##### add_media_file(self, event)

Add new media file

##### view_media_file(self, filename)

View selected media file

##### delete_selected_media(self)

Delete selected media files

##### export_all_media(self)

Export all media files

##### save_us(self)

Save US data

##### delete_us(self)

Delete current US

##### cancel(self)

Cancel and close dialog

### RelationshipDialog

Simple dialog for adding stratigraphic relationships

#### Methods

##### __init__(self, parent, us, matrix_generator, callback)

**__init__**  
Initializes a new instance of the `RelationshipDialog` class. This constructor sets up the dialog window and prepares all necessary components for adding stratigraphic relationships.

##### create_interface(self)

Create relationship dialog interface

##### save_relationship(self)

Save the relationship

##### cancel(self)

Cancel dialog

### PeriodizationDialog

Dialog for detailed periodization management

#### Methods

##### __init__(self, parent, us, periodizzazione_service, callback)

Initializes a new instance of the PeriodizationDialog class. Sets up the dialog with the provided parent window, stratigraphic unit (us), periodization service, and an optional callback function to be executed after operations. This method prepares the dialog for managing detailed periodization tasks.

##### create_interface(self)

Create periodization interface

##### create_chronology_tab(self)

Create chronology tab

##### create_phases_tab(self)

Create phases tab

##### create_dating_tab(self)

Create dating tab

##### load_periodization_data(self)

Load existing periodization data

##### save_periodization(self)

Save periodization data

##### cancel(self)

Cancel and close dialog

### ChronologicalSequenceDialog

Dialog for displaying chronological sequence

#### Methods

##### __init__(self, parent, site_name, us_service, periodizzazione_service)

**Description:**  
Initializes a new instance of the `ChronologicalSequenceDialog` class. This constructor sets up the dialog window by storing references to the parent widget, the site name, the US service, and the periodization service, preparing the dialog for further configuration and display.

##### create_interface(self)

Create chronological sequence interface

##### create_timeline_tab(self)

Create timeline view tab

##### create_periods_tab(self)

Create periods summary tab

##### create_matrix_tab(self)

Create stratigraphic matrix tab

##### load_chronological_data(self)

Load chronological data for the site

##### update_periods_summary(self, periods_summary)

Update periods summary text

##### update_matrix_info(self, us_list)

Update matrix information

##### generate_harris_matrix(self)

Generate Harris Matrix

##### show_matrix_graph(self)

Show matrix as graph

##### export_sequence(self)

Export chronological sequence

##### close(self)

Close dialog

### ExtendedUSDialog

Extended US dialog with multiple tabs for complete archaeological recording

#### Methods

##### __init__(self, parent, us_service, site_service, matrix_generator, periodizzazione_service, site_names, us, callback)

Initializes the Extended US dialog window for comprehensive archaeological recording, setting up all required services, data fields, and user interface components. This constructor configures the dialog as either a new record or for editing an existing US (Unità Stratigrafica), and prepares the multi-tabbed interface for user interaction. If an existing US is provided, the form is populated with its data for editing.

##### create_interface(self)

Create the main interface with tabs

##### create_basic_tab(self)

Create basic information tab

##### create_description_tab(self)

Create descriptions tab

##### create_physical_tab(self)

Create physical characteristics tab

##### create_chronology_tab(self)

Create chronology/periodization tab

##### create_relationships_tab(self)

Create stratigraphic relationships tab

##### create_media_tab(self)

Create media management tab with thumbnails and drag & drop

##### create_documentation_tab(self)

Create documentation tab

##### populate_form(self)

Populate form with existing US data

##### load_relationships(self)

Load stratigraphic relationships for current US

##### add_relationship(self)

Add new stratigraphic relationship

##### edit_relationship(self)

Edit selected relationship

##### delete_relationship(self)

Delete selected relationship

##### open_harris_editor(self)

Open Harris Matrix editor

##### open_periodization_dialog(self)

Open detailed periodization dialog

##### refresh_periodization_data(self)

Refresh periodization data in form

##### show_chronological_sequence(self)

Show chronological sequence for site

##### create_media_directory(self)

Create media directory structure

##### setup_drag_drop(self)

Setup drag and drop functionality

##### on_drop_click(self, event)

Handle click on drop area

##### on_file_drop(self, event)

Handle file drop

##### process_dropped_file(self, file_path)

Process a dropped file

##### create_thumbnail(self, file_path)

Create thumbnail for image files

##### load_media_grid(self)

Load media files in grid with thumbnails

##### create_media_item(self, filename, row, col)

Create a media item widget

##### create_file_icon(self, filename)

Create a generic file icon

##### format_file_size(self, size_bytes)

Format file size in human readable format

##### on_media_select(self, filename)

Handle media item selection

##### add_media_file(self, event)

Add new media file

##### view_media_file(self, filename)

View selected media file

##### delete_selected_media(self)

Delete selected media files

##### export_all_media(self)

Export all media files

##### save_us(self)

Save US data

##### delete_us(self)

Delete current US

##### cancel(self)

Cancel and close dialog

### RelationshipDialog

Simple dialog for adding stratigraphic relationships

#### Methods

##### __init__(self, parent, us, matrix_generator, callback)

Initializes a new instance of the **RelationshipDialog** class. Sets up the dialog window for adding stratigraphic relationships, initializes its attributes with the provided parameters, and invokes the method to create the user interface.

##### create_interface(self)

Create relationship dialog interface

##### save_relationship(self)

Save the relationship

##### cancel(self)

Cancel dialog

### PeriodizationDialog

Dialog for detailed periodization management

#### Methods

##### __init__(self, parent, us, periodizzazione_service, callback)

Initializes a new instance of the **PeriodizationDialog** class. This constructor sets up the dialog window for detailed periodization management by storing provided parameters, creating the modal interface, and loading relevant periodization data.

##### create_interface(self)

Create periodization interface

##### create_chronology_tab(self)

Create chronology tab

##### create_phases_tab(self)

Create phases tab

##### create_dating_tab(self)

Create dating tab

##### load_periodization_data(self)

Load existing periodization data

##### save_periodization(self)

Save periodization data

##### cancel(self)

Cancel and close dialog

### ChronologicalSequenceDialog

Dialog for displaying chronological sequence

#### Methods

##### __init__(self, parent, site_name, us_service, periodizzazione_service)

Initializes a new instance of the **ChronologicalSequenceDialog** class. This method sets up the dialog window with the specified parent, site name, and service dependencies, configures the window properties, and initializes the user interface by creating the necessary components and loading chronological data.

##### create_interface(self)

Create chronological sequence interface

##### create_timeline_tab(self)

Create timeline view tab

##### create_periods_tab(self)

Create periods summary tab

##### create_matrix_tab(self)

Create stratigraphic matrix tab

##### load_chronological_data(self)

Load chronological data for the site

##### update_periods_summary(self, periods_summary)

Update periods summary text

##### update_matrix_info(self, us_list)

Update matrix information

##### generate_harris_matrix(self)

Generate Harris Matrix

##### show_matrix_graph(self)

Show matrix as graph

##### export_sequence(self)

Export chronological sequence

##### close(self)

Close dialog

### ExtendedUSDialog

Extended US dialog with multiple tabs for complete archaeological recording

#### Methods

##### __init__(self, parent, us_service, site_service, matrix_generator, periodizzazione_service, site_names, us, callback)

Initializes the Extended US dialog for comprehensive archaeological recording, setting up the required services, site information, and optional US data. This constructor creates and configures a modal window with multiple tabs for data entry, and populates the form if an existing US record is being edited. It also prepares internal data structures for fields, relationships, and periodization.

##### create_interface(self)

Create the main interface with tabs

##### create_basic_tab(self)

Create basic information tab

##### create_description_tab(self)

Create descriptions tab

##### create_physical_tab(self)

Create physical characteristics tab

##### create_chronology_tab(self)

Create chronology/periodization tab

##### create_relationships_tab(self)

Create stratigraphic relationships tab

##### create_media_tab(self)

Create media management tab with thumbnails and drag & drop

##### create_documentation_tab(self)

Create documentation tab

##### populate_form(self)

Populate form with existing US data

##### load_relationships(self)

Load stratigraphic relationships for current US

##### add_relationship(self)

Add new stratigraphic relationship

##### edit_relationship(self)

Edit selected relationship

##### delete_relationship(self)

Delete selected relationship

##### open_harris_editor(self)

Open Harris Matrix editor

##### open_periodization_dialog(self)

Open detailed periodization dialog

##### refresh_periodization_data(self)

Refresh periodization data in form

##### show_chronological_sequence(self)

Show chronological sequence for site

##### create_media_directory(self)

Create media directory structure

##### setup_drag_drop(self)

Setup drag and drop functionality

##### on_drop_click(self, event)

Handle click on drop area

##### on_file_drop(self, event)

Handle file drop

##### process_dropped_file(self, file_path)

Process a dropped file

##### create_thumbnail(self, file_path)

Create thumbnail for image files

##### load_media_grid(self)

Load media files in grid with thumbnails

##### create_media_item(self, filename, row, col)

Create a media item widget

##### create_file_icon(self, filename)

Create a generic file icon

##### format_file_size(self, size_bytes)

Format file size in human readable format

##### on_media_select(self, filename)

Handle media item selection

##### add_media_file(self, event)

Add new media file

##### view_media_file(self, filename)

View selected media file

##### delete_selected_media(self)

Delete selected media files

##### export_all_media(self)

Export all media files

##### save_us(self)

Save US data

##### delete_us(self)

Delete current US

##### cancel(self)

Cancel and close dialog

### RelationshipDialog

Simple dialog for adding stratigraphic relationships

#### Methods

##### __init__(self, parent, us, matrix_generator, callback)

Initializes a new instance of the `RelationshipDialog` class. Sets up the dialog window for adding stratigraphic relationships, configuring its properties and linking it to the parent window, the stratigraphic unit (`us`), the matrix generator, and an optional callback function. Calls the method to create the dialog interface.

##### create_interface(self)

Create relationship dialog interface

##### save_relationship(self)

Save the relationship

##### cancel(self)

Cancel dialog

### PeriodizationDialog

Dialog for detailed periodization management

#### Methods

##### __init__(self, parent, us, periodizzazione_service, callback)

Initializes a new instance of the `PeriodizationDialog` class. This method creates and configures a modal dialog window for managing detailed periodization, sets up the user interface, and loads the relevant periodization data. It accepts the parent window, a user story object (`us`), a periodization service, and an optional callback function.

##### create_interface(self)

Create periodization interface

##### create_chronology_tab(self)

Create chronology tab

##### create_phases_tab(self)

Create phases tab

##### create_dating_tab(self)

Create dating tab

##### load_periodization_data(self)

Load existing periodization data

##### save_periodization(self)

Save periodization data

##### cancel(self)

Cancel and close dialog

### ChronologicalSequenceDialog

Dialog for displaying chronological sequence

#### Methods

##### __init__(self, parent, site_name, us_service, periodizzazione_service)

Initializes a new instance of the **ChronologicalSequenceDialog** class. This constructor sets up the dialog window with the specified parent, site name, and service dependencies, configures the window properties (such as title, size, and modality), and initializes the user interface and chronological data display.

##### create_interface(self)

Create chronological sequence interface

##### create_timeline_tab(self)

Create timeline view tab

##### create_periods_tab(self)

Create periods summary tab

##### create_matrix_tab(self)

Create stratigraphic matrix tab

##### load_chronological_data(self)

Load chronological data for the site

##### update_periods_summary(self, periods_summary)

Update periods summary text

##### update_matrix_info(self, us_list)

Update matrix information

##### generate_harris_matrix(self)

Generate Harris Matrix

##### show_matrix_graph(self)

Show matrix as graph

##### export_sequence(self)

Export chronological sequence

##### close(self)

Close dialog

