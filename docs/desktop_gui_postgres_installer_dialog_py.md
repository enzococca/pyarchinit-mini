# desktop_gui/postgres_installer_dialog.py

## Overview

This file contains 39 documented elements.

## Classes

### PostgreSQLInstallerDialog

Dialog for PostgreSQL installation and setup

#### Methods

##### __init__(self, parent, postgres_installer, callback)

Initializes the dialog window for PostgreSQL installation and setup. This method creates and configures the dialog interface, sets up the main frame and user interface elements, and initiates a check of the current PostgreSQL installation status. It requires the parent window, a PostgreSQL installer instance, and optionally a callback function to handle completion events.

##### center_window(self)

Center dialog window on parent

##### create_interface(self)

Create the main interface

##### log_message(self, message)

Add message to log

##### update_progress(self, value, message)

Update progress bar and message

##### check_postgres_status(self)

Check current PostgreSQL status

##### start_installation(self)

Start PostgreSQL installation in background thread

##### install_postgres_thread(self)

PostgreSQL installation thread

##### create_database(self)

Create PyArchInit database

##### test_connection(self)

Test database connection

##### close(self)

Close dialog

### PostgreSQLInstallerDialog

Dialog for PostgreSQL installation and setup

#### Methods

##### __init__(self, parent, postgres_installer, callback)

Initializes the dialog window for PostgreSQL installation and setup. This method configures the dialog's properties, sets up the main interface components, and checks the current PostgreSQL installation status. It also stores references to the parent window, the installer object, and an optional callback for later use.

##### center_window(self)

Center dialog window on parent

##### create_interface(self)

Create the main interface

##### log_message(self, message)

Add message to log

##### update_progress(self, value, message)

Update progress bar and message

##### check_postgres_status(self)

Check current PostgreSQL status

##### start_installation(self)

Start PostgreSQL installation in background thread

##### install_postgres_thread(self)

PostgreSQL installation thread

##### create_database(self)

Create PyArchInit database

##### test_connection(self)

Test database connection

##### close(self)

Close dialog

### PostgreSQLInstallerDialog

Dialog for PostgreSQL installation and setup

#### Methods

##### __init__(self, parent, postgres_installer, callback)

Initializes the PostgreSQL installation dialog by setting up the dialog window, its size, position, and modality with respect to the parent. It also creates the main user interface elements and checks the current status of the PostgreSQL installation. Optional callback functionality can be provided to handle post-installation actions.

##### center_window(self)

Center dialog window on parent

##### create_interface(self)

Create the main interface

##### log_message(self, message)

Add message to log

##### update_progress(self, value, message)

Update progress bar and message

##### check_postgres_status(self)

Check current PostgreSQL status

##### start_installation(self)

Start PostgreSQL installation in background thread

##### install_postgres_thread(self)

PostgreSQL installation thread

##### create_database(self)

Create PyArchInit database

##### test_connection(self)

Test database connection

##### close(self)

Close dialog

