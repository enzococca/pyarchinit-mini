# pyarchinit_mini/database/manager.py

## Overview

This file contains 55 documented elements.

## Classes

### DatabaseManager

High-level database manager providing CRUD operations
and query functionality for PyArchInit-Mini models

#### Methods

##### __init__(self, connection)

Initializes a new instance of the DatabaseManager class.  
This method sets up the database manager by assigning the provided DatabaseConnection object to the instance, enabling subsequent database operations.

##### create(self, model_class, data)

Create a new record

##### get_by_id(self, model_class, record_id)

Get record by primary key

##### get_by_field(self, model_class, field_name, value)

Get record by specific field

##### get_all(self, model_class, offset, limit, order_by, filters)

Get all records with optional filtering and pagination

##### update(self, model_class, record_id, data)

Update existing record

##### delete(self, model_class, record_id)

Delete record by ID

##### count(self, model_class, filters)

Count records with optional filters

##### search(self, model_class, search_term, search_fields)

Search records across multiple fields

##### bulk_create(self, model_class, data_list)

Create multiple records in a single transaction

##### execute_raw_query(self, query, params)

Execute raw SQL query

##### begin_transaction(self)

Begin a manual transaction

##### commit_transaction(self, session)

Commit transaction

##### rollback_transaction(self, session)

Rollback transaction

##### get_table_info(self, model_class)

Get table metadata information

### RecordNotFoundError

Record not found error

**Inherits from**: DatabaseError

### DatabaseManager

High-level database manager providing CRUD operations
and query functionality for PyArchInit-Mini models

#### Methods

##### __init__(self, connection)

Initializes the database manager by establishing a connection to the database and setting up the migration handler. This method ensures that the manager is ready to perform CRUD operations and manage schema migrations for PyArchInit-Mini models.

##### run_migrations(self)

Run all necessary database migrations

##### create(self, model_class, data)

Create a new record

##### get_by_id(self, model_class, record_id)

Get record by primary key

##### get_by_field(self, model_class, field_name, value)

Get record by specific field

##### get_all(self, model_class, offset, limit, order_by, filters)

Get all records with optional filtering and pagination

##### update(self, model_class, record_id, data)

Update existing record

##### delete(self, model_class, record_id)

Delete record by ID

##### count(self, model_class, filters)

Count records with optional filters

##### search(self, model_class, search_term, search_fields)

Search records across multiple fields

##### bulk_create(self, model_class, data_list)

Create multiple records in a single transaction

##### execute_raw_query(self, query, params)

Execute raw SQL query

##### begin_transaction(self)

Begin a manual transaction

##### commit_transaction(self, session)

Commit transaction

##### rollback_transaction(self, session)

Rollback transaction

##### get_table_info(self, model_class)

Get table metadata information

### RecordNotFoundError

Record not found error

**Inherits from**: DatabaseError

### DatabaseManager

High-level database manager providing CRUD operations
and query functionality for PyArchInit-Mini models

#### Methods

##### __init__(self, connection)

Initializes the database manager by establishing a connection to the database using the provided DatabaseConnection object. It also sets up the migration handler to manage database schema updates. This ensures the manager is ready to perform CRUD operations and handle migrations for PyArchInit-Mini models.

##### run_migrations(self)

Run all necessary database migrations

##### create(self, model_class, data)

Create a new record

##### get_by_id(self, model_class, record_id)

Get record by primary key

##### get_by_field(self, model_class, field_name, value)

Get record by specific field

##### get_all(self, model_class, offset, limit, order_by, filters)

Get all records with optional filtering and pagination

##### update(self, model_class, record_id, data)

Update existing record

##### delete(self, model_class, record_id)

Delete record by ID

##### count(self, model_class, filters)

Count records with optional filters

##### search(self, model_class, search_term, search_fields)

Search records across multiple fields

##### bulk_create(self, model_class, data_list)

Create multiple records in a single transaction

##### execute_raw_query(self, query, params)

Execute raw SQL query

##### begin_transaction(self)

Begin a manual transaction

##### commit_transaction(self, session)

Commit transaction

##### rollback_transaction(self, session)

Rollback transaction

##### get_table_info(self, model_class)

Get table metadata information

