# desktop_gui/inventario_dialog_extended.py

## Overview

This file contains 84 documented elements.

## Classes

### ExtendedInventarioDialog

Extended Inventory Dialog with all fields from PyArchInit plugin
Includes media management and thesaurus integration

#### Methods

##### __init__(self, parent, inventario_service, site_service, thesaurus_service, media_service, inventario, callback)

Initializes the Extended Inventory Dialog, setting up the user interface with all relevant inventory fields from the PyArchInit plugin, including media management and thesaurus integration. Configures dialog properties, creates and arranges all UI tabs, and loads existing inventory data and associated media if provided. This method establishes all necessary services and prepares the dialog for user interaction.

##### center_window(self)

Center dialog window on parent

##### create_media_directory(self)

Create media directory for the inventory item

##### get_thesaurus_values(self, field_name)

Get thesaurus values for a field

##### create_identification_tab(self)

Create identification and basic info tab

##### create_classification_tab(self)

Create classification tab

##### create_context_tab(self)

Create context tab

##### create_physical_tab(self)

Create physical characteristics tab

##### create_conservation_tab(self)

Create conservation tab

##### create_ceramic_tab(self)

Create ceramic-specific fields tab

##### create_measurements_tab(self)

Create measurements and dating tab

##### create_documentation_tab(self)

Create documentation tab

##### create_media_tab(self)

Create media management tab

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

Load existing media files for the inventory item

##### get_text_field_value(self, field_name)

Get value from Text widget

##### get_entry_field_value(self, field_name)

Get value from Entry or Combobox widget

##### populate_form(self)

Populate form with existing inventory data

##### save(self)

Save inventory data

##### cancel(self)

Cancel and close dialog

### ExtendedInventarioDialog

Extended Inventory Dialog with all fields from PyArchInit plugin
Includes media management and thesaurus integration

#### Methods

##### __init__(self, parent, inventario_service, site_service, thesaurus_service, media_service, inventario, callback)

Initializes the Extended Inventory Dialog, setting up all user interface components and services required for managing inventory records, including media and thesaurus integration. Configures dialog properties, creates form tabs for all relevant data fields, and loads existing inventory data and associated media if provided. This method prepares the dialog for both creating new and editing existing inventory entries.

##### center_window(self)

Center dialog window on parent

##### create_media_directory(self)

Create media directory for the inventory item

##### get_thesaurus_values(self, field_name)

Get thesaurus values for a field

##### create_identification_tab(self)

Create identification and basic info tab

##### create_classification_tab(self)

Create classification tab

##### create_context_tab(self)

Create context tab

##### create_physical_tab(self)

Create physical characteristics tab

##### create_conservation_tab(self)

Create conservation tab

##### create_ceramic_tab(self)

Create ceramic-specific fields tab

##### create_measurements_tab(self)

Create measurements and dating tab

##### create_documentation_tab(self)

Create documentation tab

##### create_media_tab(self)

Create media management tab

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

Load existing media files for the inventory item

##### get_text_field_value(self, field_name)

Get value from Text widget

##### get_entry_field_value(self, field_name)

Get value from Entry or Combobox widget

##### populate_form(self)

Populate form with existing inventory data

##### save(self)

Save inventory data

##### cancel(self)

Cancel and close dialog

### ExtendedInventarioDialog

Extended Inventory Dialog with all fields from PyArchInit plugin
Includes media management and thesaurus integration

#### Methods

##### __init__(self, parent, inventario_service, site_service, thesaurus_service, media_service, inventario, callback)

Initializes an extended inventory dialog window with all relevant fields from the PyArchInit plugin, including media management and thesaurus integration. Sets up the dialog’s layout, tabs, and controls, and optionally populates the form and associated media if an existing inventory record is provided. This method also configures service dependencies and prepares the dialog for user interaction.

##### center_window(self)

Center dialog window on parent

##### create_media_directory(self)

Create media directory for the inventory item

##### get_thesaurus_values(self, field_name)

Get thesaurus values for a field

##### create_identification_tab(self)

Create identification and basic info tab

##### create_classification_tab(self)

Create classification tab

##### create_context_tab(self)

Create context tab

##### create_physical_tab(self)

Create physical characteristics tab

##### create_conservation_tab(self)

Create conservation tab

##### create_ceramic_tab(self)

Create ceramic-specific fields tab

##### create_measurements_tab(self)

Create measurements and dating tab

##### create_documentation_tab(self)

Create documentation tab

##### create_media_tab(self)

Create media management tab

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

Load existing media files for the inventory item

##### get_text_field_value(self, field_name)

Get value from Text widget

##### get_entry_field_value(self, field_name)

Get value from Entry or Combobox widget

##### populate_form(self)

Populate form with existing inventory data

##### save(self)

Save inventory data

##### cancel(self)

Cancel and close dialog

