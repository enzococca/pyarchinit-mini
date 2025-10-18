# pyarchinit_mini/database/connection.py

## Overview

This file contains 34 documented elements.

## Classes

### DatabaseConnection

Manages database connections for both PostgreSQL and SQLite

#### Methods

##### __init__(self, connection_string)

Initializes a new instance of the database connection manager with the provided connection string. This method stores the connection string and prepares the necessary attributes for establishing database connections. Upon initialization, it also triggers the setup of the database engine and session factory.

##### get_session(self)

Context manager for database sessions
Ensures proper session cleanup

##### create_tables(self)

Create all tables from models

##### test_connection(self)

Test database connection

##### close(self)

Close database connection

##### from_url(cls, database_url)

Create connection from database URL

##### sqlite(cls, db_path)

Create SQLite connection

##### postgresql(cls, host, port, database, username, password)

Create PostgreSQL connection

### DatabaseConnection

Manages database connections for both PostgreSQL and SQLite

#### Methods

##### __init__(self, connection_string)

Initializes a new instance of the database connection manager with the provided connection string. This method sets up the necessary attributes and triggers the configuration of the database engine and session factory to enable interactions with either PostgreSQL or SQLite databases.

##### get_session(self)

Context manager for database sessions
Ensures proper session cleanup

##### create_tables(self)

Create all tables from models

##### initialize_database(self)

Initialize database and create tables with migrations

##### test_connection(self)

Test database connection

##### close(self)

Close database connection

##### from_url(cls, database_url)

Create connection from database URL

##### sqlite(cls, db_path)

Create SQLite connection

##### postgresql(cls, host, port, database, username, password)

Create PostgreSQL connection

### DatabaseConnection

Manages database connections for both PostgreSQL and SQLite

#### Methods

##### __init__(self, connection_string)

Initializes a new instance of the database connection manager with the specified connection string. This method sets up the required attributes and triggers the initialization of the database engine and session factory. It supports connections to both PostgreSQL and SQLite databases.

##### get_session(self)

Context manager for database sessions
Ensures proper session cleanup

##### create_tables(self)

Create all tables from models

##### initialize_database(self)

Initialize database and create tables with migrations

##### test_connection(self)

Test database connection

##### close(self)

Close database connection

##### from_url(cls, database_url)

Create connection from database URL

##### sqlite(cls, db_path)

Create SQLite connection

##### postgresql(cls, host, port, database, username, password)

Create PostgreSQL connection

## Functions

### set_sqlite_pragma(dbapi_connection, connection_record)

The **set_sqlite_pragma** function is an event listener for SQLAlchemy that executes the SQLite `PRAGMA foreign_keys=ON` statement whenever a new database connection is established. This ensures that foreign key constraints are enforced in all SQLite connections managed by the SQLAlchemy engine. It is particularly important because, by default, SQLite does not enforce foreign key constraints unless explicitly enabled.

**Parameters:**
- `dbapi_connection`
- `connection_record`

### set_sqlite_pragma(dbapi_connection, connection_record)

The `set_sqlite_pragma` function is an event listener that executes whenever a new SQLite database connection is established through SQLAlchemy. It enables foreign key constraint enforcement by executing the SQL statement `PRAGMA foreign_keys=ON` on the newly connected database. This ensures that SQLite complies with foreign key relationships defined in the schema.

**Parameters:**
- `dbapi_connection`
- `connection_record`

