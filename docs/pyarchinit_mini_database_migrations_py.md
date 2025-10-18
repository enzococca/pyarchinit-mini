# pyarchinit_mini/database/migrations.py

## Overview

This file contains 18 documented elements.

## Classes

### DatabaseMigrations

Handle database schema migrations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the migration handler by associating it with a given database manager. This method stores references to both the database manager and its active connection for use in migration operations.

##### check_column_exists(self, table_name, column_name)

Check if a column exists in a table

##### add_column_if_not_exists(self, table_name, column_name, column_type, default_value)

Add a column to a table if it doesn't exist

##### migrate_inventario_materiali_table(self)

Migrate inventario_materiali_table to include all new fields

##### migrate_all_tables(self)

Run all necessary migrations

##### get_table_info(self, table_name)

Get information about a table structure

##### check_migration_needed(self, table_name, required_columns)

Check which columns are missing from a table

### DatabaseMigrations

Handle database schema migrations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the migration handler by accepting a database manager object. This method sets up internal references to both the database manager and its associated database connection, enabling subsequent schema migration operations.

##### check_column_exists(self, table_name, column_name)

Check if a column exists in a table

##### add_column_if_not_exists(self, table_name, column_name, column_type, default_value)

Add a column to a table if it doesn't exist

##### migrate_inventario_materiali_table(self)

Migrate inventario_materiali_table to include all new fields

##### migrate_all_tables(self)

Run all necessary migrations

##### get_table_info(self, table_name)

Get information about a table structure

##### check_migration_needed(self, table_name, required_columns)

Check which columns are missing from a table

