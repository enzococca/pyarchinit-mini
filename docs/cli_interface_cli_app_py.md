# cli_interface/cli_app.py

## Overview

This file contains 51 documented elements.

## Classes

### PyArchInitCLI

Interactive CLI for PyArchInit-Mini

#### Methods

##### __init__(self, database_url)

Initializes a new instance of the PyArchInitCLI class. This method sets up the database connection, initializes the database schema and management components, and creates service objects required for site, unit, inventory management, matrix generation and visualization, and PDF generation. If no database URL is provided, it defaults to an environment variable or a local SQLite database.

##### show_welcome(self)

Show welcome screen

##### show_main_menu(self)

Show main menu and handle selection

##### sites_menu(self)

Sites management menu

##### list_sites(self)

List all sites

##### create_site(self)

Create new site

##### view_site(self)

View site details

##### us_menu(self)

US management menu

##### list_us(self)

List all US

##### harris_matrix_menu(self)

Harris Matrix menu

##### generate_harris_matrix(self)

Generate Harris Matrix for a site

##### statistics_menu(self)

Statistics and reports menu

##### show_help(self)

Show help information

##### run(self)

Run the CLI application

### PyArchInitCLI

Interactive CLI for PyArchInit-Mini

#### Methods

##### __init__(self, database_url)

Initializes a new instance of the **PyArchInitCLI** class. This method sets up the application console, configures the database connection (using the provided `database_url` or a default value), creates required database tables, and initializes all core service components needed for the CLI to function.

##### show_welcome(self)

Show welcome screen

##### show_main_menu(self)

Show main menu and handle selection

##### sites_menu(self)

Sites management menu

##### list_sites(self)

List all sites

##### create_site(self)

Create new site

##### view_site(self)

View site details

##### us_menu(self)

US management menu

##### list_us(self)

List all US

##### harris_matrix_menu(self)

Harris Matrix menu

##### generate_harris_matrix(self)

Generate Harris Matrix for a site

##### statistics_menu(self)

Statistics and reports menu

##### show_help(self)

Show help information

##### run(self)

Run the CLI application

### PyArchInitCLI

Interactive CLI for PyArchInit-Mini

#### Methods

##### __init__(self, database_url)

Initializes a new instance of the `PyArchInitCLI` class.  
This method sets up the command-line interface environment by configuring the database connection, initializing the database schema, and instantiating all core services required for site, stratigraphic unit, inventory management, Harris matrix generation, visualization, and PDF export. An optional `database_url` parameter can be provided; otherwise, a default or environment-specified database is used.

##### show_welcome(self)

Show welcome screen

##### show_main_menu(self)

Show main menu and handle selection

##### sites_menu(self)

Sites management menu

##### list_sites(self)

List all sites

##### create_site(self)

Create new site

##### view_site(self)

View site details

##### us_menu(self)

US management menu

##### list_us(self)

List all US

##### harris_matrix_menu(self)

Harris Matrix menu

##### generate_harris_matrix(self)

Generate Harris Matrix for a site

##### statistics_menu(self)

Statistics and reports menu

##### show_help(self)

Show help information

##### run(self)

Run the CLI application

## Functions

### main(database_url, version)

PyArchInit-Mini Interactive CLI

**Parameters:**
- `database_url`
- `version`

### main(database_url, version)

PyArchInit-Mini Interactive CLI

**Parameters:**
- `database_url`
- `version`

### main(database_url, version)

PyArchInit-Mini Interactive CLI

**Parameters:**
- `database_url`
- `version`

