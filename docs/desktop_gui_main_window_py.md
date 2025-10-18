# desktop_gui/main_window.py

## Overview

This file contains 160 documented elements.

## Classes

### PyArchInitGUI

Main GUI application for PyArchInit-Mini

#### Methods

##### __init__(self)

**__init__**  
Initializes the main window and user interface for the PyArchInit-Mini application. This method sets up the main application window, initializes the database connection and key status variables, applies styles, creates the menu and interface components, and loads the initial data required for the application to function.

##### setup_database(self)

Initialize database connection and services

##### setup_styles(self)

Configure ttk styles

##### create_menu(self)

Create application menu bar

##### create_main_interface(self)

Create main application interface

##### create_toolbar(self, parent)

Create application toolbar

##### create_status_bar(self, parent)

Create status bar

##### create_dashboard_tab(self)

Create dashboard tab

##### create_dashboard_content(self, parent)

Create dashboard content widgets

##### create_sites_tab(self)

Create sites management tab

##### create_us_tab(self)

Create US management tab

##### create_inventario_tab(self)

Create inventory management tab

##### refresh_data(self)

Refresh all data in the interface

##### refresh_dashboard(self)

Refresh dashboard statistics

##### refresh_activity_log(self)

Refresh activity log in dashboard

##### refresh_sites(self)

Refresh sites list

##### refresh_us(self)

Refresh US list

##### refresh_inventario(self)

Refresh inventory list

##### on_site_changed(self, event)

Handle site selection change

##### on_sites_search(self)

Handle sites search

##### on_us_filter_changed(self, event)

Handle US filter change

##### on_inventario_filter_changed(self, event)

Handle inventory filter change

##### show_tab(self, tab_name)

Show specific tab

##### new_site_dialog(self)

Show new site dialog

##### new_us_dialog(self)

Show new US dialog

##### new_inventario_dialog(self)

Show new inventory dialog

##### edit_selected_site(self)

Edit selected site

##### delete_selected_site(self)

Delete selected site

##### edit_selected_us(self)

Edit selected US

##### delete_selected_us(self)

Delete selected US

##### edit_selected_inventario(self)

Edit selected inventory item

##### delete_selected_inventario(self)

Delete selected inventory item

##### show_harris_matrix_dialog(self)

Show Harris Matrix dialog

##### export_pdf_dialog(self)

Show PDF export dialog

##### show_media_manager(self)

Show media manager dialog

##### show_statistics_dialog(self)

Show statistics dialog

##### show_database_config(self)

Show database configuration dialog

##### reconnect_database(self, connection_string)

Reconnect to database with new connection string

##### show_about_dialog(self)

Show about dialog

##### show_help_dialog(self)

Show help dialog

##### import_database(self)

Import database from file

##### export_database(self)

Export database to file

##### show_thesaurus_dialog(self)

Show thesaurus management dialog

##### show_postgres_installer(self)

Show PostgreSQL installer dialog

##### show_media_manager(self)

Show media manager dialog

##### show_pdf_export_dialog(self)

Show PDF export dialog

##### show_statistics_dialog(self)

Show statistics dialog

##### run(self)

Start the application

##### __del__(self)

Cleanup when application closes

### PyArchInitGUI

Main GUI application for PyArchInit-Mini

#### Methods

##### __init__(self)

Initializes the main window and core components of the PyArchInit-Mini graphical user interface. This method sets up the application window, initializes the database connection and status variables, applies GUI styles, constructs the menu and main interface, and loads the initial data for user interaction.

##### setup_database(self)

Initialize database connection and services

##### setup_styles(self)

Configure ttk styles

##### create_menu(self)

Create application menu bar

##### create_main_interface(self)

Create main application interface

##### create_toolbar(self, parent)

Create application toolbar

##### create_status_bar(self, parent)

Create status bar

##### create_dashboard_tab(self)

Create dashboard tab

##### create_dashboard_content(self, parent)

Create dashboard content widgets

##### create_sites_tab(self)

Create sites management tab

##### create_us_tab(self)

Create US management tab

##### create_inventario_tab(self)

Create inventory management tab

##### refresh_data(self)

Refresh all data in the interface

##### refresh_dashboard(self)

Refresh dashboard statistics

##### refresh_activity_log(self)

Refresh activity log in dashboard

##### refresh_sites(self)

Refresh sites list

##### refresh_us(self)

Refresh US list

##### refresh_inventario(self)

Refresh inventory list

##### on_site_changed(self, event)

Handle site selection change

##### on_sites_search(self)

Handle sites search

##### on_us_filter_changed(self, event)

Handle US filter change

##### on_inventario_filter_changed(self, event)

Handle inventory filter change

##### show_tab(self, tab_name)

Show specific tab

##### new_site_dialog(self)

Show new site dialog

##### new_us_dialog(self)

Show new US dialog

##### new_inventario_dialog(self)

Show new inventory dialog

##### edit_selected_site(self)

Edit selected site

##### delete_selected_site(self)

Delete selected site

##### edit_selected_us(self)

Edit selected US

##### delete_selected_us(self)

Delete selected US

##### edit_selected_inventario(self)

Edit selected inventory item

##### delete_selected_inventario(self)

Delete selected inventory item

##### show_harris_matrix_dialog(self)

Show Harris Matrix dialog

##### export_pdf_dialog(self)

Show PDF export dialog

##### show_media_manager(self)

Show media manager dialog

##### show_statistics_dialog(self)

Show statistics dialog

##### show_database_config(self)

Show database configuration dialog

##### reconnect_database(self, connection_string)

Reconnect to database with new connection string

##### show_about_dialog(self)

Show about dialog

##### show_help_dialog(self)

Show help dialog

##### import_database(self)

Import database from file

##### export_database(self)

Export database to file

##### show_thesaurus_dialog(self)

Show thesaurus management dialog

##### show_postgres_installer(self)

Show PostgreSQL installer dialog

##### show_media_manager(self)

Show media manager dialog

##### show_pdf_export_dialog(self)

Show PDF export dialog

##### show_statistics_dialog(self)

Show statistics dialog

##### run(self)

Start the application

##### __del__(self)

Cleanup when application closes

### PyArchInitGUI

Main GUI application for PyArchInit-Mini

#### Methods

##### __init__(self)

Initializes the main window and core components of the PyArchInit-Mini GUI application. This method sets up the application window, initializes the database connection and necessary services, prepares status variables, applies GUI styles, creates the menu and main interface, and loads the initial data for display.

##### setup_database(self)

Initialize database connection and services

##### setup_styles(self)

Configure ttk styles

##### create_menu(self)

Create application menu bar

##### create_main_interface(self)

Create main application interface

##### create_toolbar(self, parent)

Create application toolbar

##### create_status_bar(self, parent)

Create status bar

##### create_dashboard_tab(self)

Create dashboard tab

##### create_dashboard_content(self, parent)

Create dashboard content widgets

##### create_sites_tab(self)

Create sites management tab

##### create_us_tab(self)

Create US management tab

##### create_inventario_tab(self)

Create inventory management tab

##### refresh_data(self)

Refresh all data in the interface

##### refresh_dashboard(self)

Refresh dashboard statistics

##### refresh_activity_log(self)

Refresh activity log in dashboard

##### refresh_sites(self)

Refresh sites list

##### refresh_us(self)

Refresh US list

##### refresh_inventario(self)

Refresh inventory list

##### on_site_changed(self, event)

Handle site selection change

##### on_sites_search(self)

Handle sites search

##### on_us_filter_changed(self, event)

Handle US filter change

##### on_inventario_filter_changed(self, event)

Handle inventory filter change

##### show_tab(self, tab_name)

Show specific tab

##### new_site_dialog(self)

Show new site dialog

##### new_us_dialog(self)

Show new US dialog

##### new_inventario_dialog(self)

Show new inventory dialog

##### edit_selected_site(self)

Edit selected site

##### delete_selected_site(self)

Delete selected site

##### edit_selected_us(self)

Edit selected US

##### delete_selected_us(self)

Delete selected US

##### edit_selected_inventario(self)

Edit selected inventory item

##### delete_selected_inventario(self)

Delete selected inventory item

##### show_harris_matrix_dialog(self)

Show Harris Matrix dialog

##### export_pdf_dialog(self)

Show PDF export dialog

##### show_media_manager(self)

Show media manager dialog

##### show_statistics_dialog(self)

Show statistics dialog

##### show_database_config(self)

Show database configuration dialog

##### reconnect_database(self, connection_string)

Reconnect to database with new connection string

##### show_about_dialog(self)

Show about dialog

##### show_help_dialog(self)

Show help dialog

##### import_database(self)

Import database from file

##### replace_current_database(self, source_file)

Replace current database with imported one

##### copy_as_new_database(self, source_file)

Copy imported database as new file

##### load_sample_database(self)

Load the sample database

##### create_sample_database(self)

Create sample database

##### export_database(self)

Export database to file

##### show_thesaurus_dialog(self)

Show thesaurus management dialog

##### show_postgres_installer(self)

Show PostgreSQL installer dialog

##### show_media_manager(self)

Show media manager dialog

##### show_pdf_export_dialog(self)

Show PDF export dialog

##### show_statistics_dialog(self)

Show statistics dialog

##### run(self)

Start the application

##### __del__(self)

Cleanup when application closes

## Functions

### on_postgres_installed(connection_string)

Callback when PostgreSQL is installed and database created

**Parameters:**
- `connection_string`

### on_postgres_installed(connection_string)

Callback when PostgreSQL is installed and database created

**Parameters:**
- `connection_string`

### on_postgres_installed(connection_string)

Callback when PostgreSQL is installed and database created

**Parameters:**
- `connection_string`

