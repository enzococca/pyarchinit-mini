# tests/conftest.py

## Overview

This file contains 9 documented elements.

## Functions

### temp_db()

Create temporary SQLite database for testing

### db_manager(temp_db)

Create database manager with test database

**Parameters:**
- `temp_db`

### site_service(db_manager)

Create site service with test database

**Parameters:**
- `db_manager`

### us_service(db_manager)

Create US service with test database

**Parameters:**
- `db_manager`

### inventario_service(db_manager)

Create inventario service with test database

**Parameters:**
- `db_manager`

### sample_site_data()

Sample site data for testing

### sample_us_data()

Sample US data for testing

### sample_inventario_data()

Sample inventory data for testing

