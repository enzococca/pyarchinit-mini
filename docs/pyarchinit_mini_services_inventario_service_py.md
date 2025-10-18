# pyarchinit_mini/services/inventario_service.py

## Overview

This file contains 52 documented elements.

## Classes

### InventarioService

Service class for inventory operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the InventarioService class.  
This constructor method accepts a DatabaseManager object and assigns it to the service, enabling database operations related to inventory management.

##### create_inventario(self, inv_data)

Create a new inventory item

##### get_inventario_by_id(self, inv_id)

Get inventory item by ID

##### get_inventario_dto_by_id(self, inv_id)

Get inventory item by ID as DTO

##### get_all_inventario(self, page, size, filters)

Get all inventory items with pagination and filtering - returns DTOs

##### update_inventario(self, inv_id, update_data)

Update existing inventory item

##### delete_inventario(self, inv_id)

Delete inventory item

##### count_inventario(self, filters)

Count inventory items with optional filters

##### search_inventario(self, search_term, page, size)

Search inventory items by term - returns DTOs

##### get_inventario_by_site(self, site_name, page, size)

Get all inventory items for a specific site - returns DTOs

##### get_inventario_by_us(self, site_name, area, us_number, page, size)

Get all inventory items for a specific US - returns DTOs

##### get_inventario_by_type(self, tipo_reperto, page, size)

Get all inventory items of a specific type - returns DTOs

##### get_inventory_statistics(self, inv_id)

Get statistics for an inventory item

##### get_type_statistics(self, site_name)

Get statistics by find type

### InventarioService

Service class for inventory operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the InventarioService class.  
This constructor accepts a DatabaseManager object, which is used to manage database operations related to inventory activities.

##### create_inventario(self, inv_data)

Create a new inventory item

##### create_inventario_dto(self, inv_data)

Create a new inventory item and return as DTO

##### get_inventario_by_id(self, inv_id)

Get inventory item by ID

##### get_inventario_dto_by_id(self, inv_id)

Get inventory item by ID as DTO

##### get_all_inventario(self, page, size, filters)

Get all inventory items with pagination and filtering - returns DTOs

##### update_inventario(self, inv_id, update_data)

Update existing inventory item

##### delete_inventario(self, inv_id)

Delete inventory item

##### count_inventario(self, filters)

Count inventory items with optional filters

##### search_inventario(self, search_term, page, size)

Search inventory items by term - returns DTOs

##### get_inventario_by_site(self, site_name, page, size)

Get all inventory items for a specific site - returns DTOs

##### get_inventario_by_us(self, site_name, area, us_number, page, size)

Get all inventory items for a specific US - returns DTOs

##### get_inventario_by_type(self, tipo_reperto, page, size)

Get all inventory items of a specific type - returns DTOs

##### get_inventory_statistics(self, inv_id)

Get statistics for an inventory item

##### get_type_statistics(self, site_name)

Get statistics by find type

##### get_all_inventario_dto(self, page, size)

Get all inventario items as DTOs (session-safe)

### InventarioService

Service class for inventory operations

#### Methods

##### __init__(self, db_manager)

Initializes an instance of the InventarioService class.  
This constructor accepts a DatabaseManager object and assigns it to the instance for managing database operations related to inventory.

##### create_inventario(self, inv_data)

Create a new inventory item

##### create_inventario_dto(self, inv_data)

Create a new inventory item and return as DTO

##### get_inventario_by_id(self, inv_id)

Get inventory item by ID

##### get_inventario_dto_by_id(self, inv_id)

Get inventory item by ID as DTO

##### get_all_inventario(self, page, size, filters)

Get all inventory items with pagination and filtering - returns DTOs

##### update_inventario(self, inv_id, update_data)

Update existing inventory item

##### delete_inventario(self, inv_id)

Delete inventory item

##### count_inventario(self, filters)

Count inventory items with optional filters

##### search_inventario(self, search_term, page, size)

Search inventory items by term - returns DTOs

##### get_inventario_by_site(self, site_name, page, size)

Get all inventory items for a specific site - returns DTOs

##### get_inventario_by_us(self, site_name, area, us_number, page, size)

Get all inventory items for a specific US - returns DTOs

##### get_inventario_by_type(self, tipo_reperto, page, size)

Get all inventory items of a specific type - returns DTOs

##### get_inventory_statistics(self, inv_id)

Get statistics for an inventory item

##### get_type_statistics(self, site_name)

Get statistics by find type

##### get_all_inventario_dto(self, page, size)

Get all inventario items as DTOs (session-safe)

