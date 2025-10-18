# pyarchinit_mini/database/schemas.py

## Overview

This file contains 33 documented elements.

## Classes

### DatabaseSchema

Utilities for database schema management and migrations

#### Methods

##### __init__(self, connection)

Initializes a new instance of the schema management utility by establishing a connection to the specified database. This method stores the provided DatabaseConnection object for use in subsequent schema operations.

##### create_all_tables(self)

Create all tables defined in models

##### check_table_exists(self, table_name)

Check if a table exists in the database

##### get_table_list(self)

Get list of all tables in the database

##### get_table_columns(self, table_name)

Get column information for a table

##### create_indexes(self)

Create recommended indexes for performance

##### check_schema_compatibility(self)

Check if current database schema is compatible with models

##### backup_schema(self)

Generate SQL script to backup current schema structure

##### get_database_stats(self)

Get database statistics

### DatabaseSchema

Utilities for database schema management and migrations

#### Methods

##### __init__(self, connection)

Initializes a new instance of the class with the given database connection.  
Stores the provided DatabaseConnection object for use in subsequent schema management and migration operations.

##### create_all_tables(self)

Create all tables defined in models

##### check_table_exists(self, table_name)

Check if a table exists in the database

##### get_table_list(self)

Get list of all tables in the database

##### get_table_columns(self, table_name)

Get column information for a table

##### create_indexes(self)

Create recommended indexes for performance

##### check_schema_compatibility(self)

Check if current database schema is compatible with models

##### backup_schema(self)

Generate SQL script to backup current schema structure

##### get_database_stats(self)

Get database statistics

### DatabaseSchema

Utilities for database schema management and migrations

#### Methods

##### __init__(self, connection)

Initializes a new instance of the class with the provided database connection.  
This method assigns the given DatabaseConnection object to the instance for use in schema management and migration operations.

##### create_all_tables(self)

Create all tables defined in models

##### check_table_exists(self, table_name)

Check if a table exists in the database

##### get_table_list(self)

Get list of all tables in the database

##### get_table_columns(self, table_name)

Get column information for a table

##### create_indexes(self)

Create recommended indexes for performance

##### check_schema_compatibility(self)

Check if current database schema is compatible with models

##### backup_schema(self)

Generate SQL script to backup current schema structure

##### get_database_stats(self)

Get database statistics

