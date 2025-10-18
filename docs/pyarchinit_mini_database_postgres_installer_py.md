# pyarchinit_mini/database/postgres_installer.py

## Overview

This file contains 33 documented elements.

## Classes

### PostgreSQLInstaller

Manages PostgreSQL installation on different platforms

#### Methods

##### __init__(self)

Initializes a new instance of the PostgreSQL management class by detecting the current operating system and system architecture. It also sets default values for the PostgreSQL data directory, port, username, and password, which are used for managing PostgreSQL installations.

##### check_postgres_installed(self)

Check if PostgreSQL is already installed and accessible

##### get_postgres_version(self)

Get installed PostgreSQL version

##### install_postgres_macos(self)

Install PostgreSQL on macOS using Homebrew

##### install_postgres_windows(self)

Install PostgreSQL on Windows

##### install_postgres_linux(self)

Install PostgreSQL on Linux

##### create_pyarchinit_database(self, connection_params)

Create PyArchInit database and user

##### install_postgres(self)

Install PostgreSQL based on the current platform

##### get_connection_info(self)

Get default connection information

### PostgreSQLInstaller

Manages PostgreSQL installation on different platforms

#### Methods

##### __init__(self)

Initializes the PostgreSQL manager by detecting the current operating system and architecture, and setting default configuration parameters such as the data directory, port, user, and password. This method prepares the instance for subsequent PostgreSQL management operations across different platforms. It is called automatically when a new instance of the class is created.

##### check_postgres_installed(self)

Check if PostgreSQL is already installed and accessible

##### get_postgres_version(self)

Get installed PostgreSQL version

##### install_postgres_macos(self)

Install PostgreSQL on macOS using Homebrew

##### install_postgres_windows(self)

Install PostgreSQL on Windows

##### install_postgres_linux(self)

Install PostgreSQL on Linux

##### create_pyarchinit_database(self, connection_params)

Create PyArchInit database and user

##### install_postgres(self)

Install PostgreSQL based on the current platform

##### get_connection_info(self)

Get default connection information

### PostgreSQLInstaller

Manages PostgreSQL installation on different platforms

#### Methods

##### __init__(self)

Initializes the PostgreSQL manager by detecting the current operating system and machine architecture. It also sets default values for PostgreSQL data directory, port, user, and password. This method prepares the instance for further management of PostgreSQL installation and configuration.

##### check_postgres_installed(self)

Check if PostgreSQL is already installed and accessible

##### get_postgres_version(self)

Get installed PostgreSQL version

##### install_postgres_macos(self)

Install PostgreSQL on macOS using Homebrew

##### install_postgres_windows(self)

Install PostgreSQL on Windows

##### install_postgres_linux(self)

Install PostgreSQL on Linux

##### create_pyarchinit_database(self, connection_params)

Create PyArchInit database and user

##### install_postgres(self)

Install PostgreSQL based on the current platform

##### get_connection_info(self)

Get default connection information

