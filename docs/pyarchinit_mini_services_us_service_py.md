# pyarchinit_mini/services/us_service.py

## Overview

This file contains 47 documented elements.

## Classes

### USService

Service class for US operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the USService class with the specified database manager.  
This constructor assigns the provided DatabaseManager instance to the service, enabling database operations related to US (stratigraphic unit) management.

##### create_us(self, us_data)

Create a new stratigraphic unit

##### get_us_by_id(self, us_id)

Get US by ID

##### get_us_dto_by_id(self, us_id)

Get US by ID as DTO

##### get_all_us(self, page, size, filters)

Get all US with pagination and filtering - returns DTOs

##### update_us(self, us_id, update_data)

Update existing US

##### update_us_dto(self, us_id, update_data)

Update existing US and return DTO

##### delete_us(self, us_id)

Delete US

##### count_us(self, filters)

Count US with optional filters

##### search_us(self, search_term, page, size)

Search US by term - returns DTOs

##### get_us_by_site(self, site_name, page, size)

Get all US for a specific site - returns DTOs

##### get_us_by_site_and_area(self, site_name, area, page, size)

Get all US for a specific site and area - returns DTOs

##### get_us_statistics(self, us_id)

Get statistics for a US

### USService

Service class for US operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the USService class.  
This constructor method accepts a DatabaseManager object, which is stored as an instance attribute for managing database operations related to US services.

##### create_us(self, us_data)

Create a new stratigraphic unit

##### create_us_dto(self, us_data)

Create a new US and return as DTO

##### get_us_by_id(self, us_id)

Get US by ID

##### get_us_dto_by_id(self, us_id)

Get US by ID as DTO

##### get_all_us(self, page, size, filters)

Get all US with pagination and filtering - returns DTOs

##### update_us(self, us_id, update_data)

Update existing US

##### update_us_dto(self, us_id, update_data)

Update existing US and return DTO

##### delete_us(self, us_id)

Delete US

##### count_us(self, filters)

Count US with optional filters

##### search_us(self, search_term, page, size)

Search US by term - returns DTOs

##### get_us_by_site(self, site_name, page, size)

Get all US for a specific site - returns DTOs

##### get_us_by_site_and_area(self, site_name, area, page, size)

Get all US for a specific site and area - returns DTOs

##### get_us_statistics(self, us_id)

Get statistics for a US

### USService

Service class for US operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the USService class.  
This constructor accepts a DatabaseManager object, which is assigned to the instance for managing database operations related to US services.

##### create_us(self, us_data)

Create a new stratigraphic unit

##### create_us_dto(self, us_data)

Create a new US and return as DTO

##### get_us_by_id(self, us_id)

Get US by ID

##### get_us_dto_by_id(self, us_id)

Get US by ID as DTO

##### get_all_us(self, page, size, filters)

Get all US with pagination and filtering - returns DTOs

##### update_us(self, us_id, update_data)

Update existing US

##### update_us_dto(self, us_id, update_data)

Update existing US and return DTO

##### delete_us(self, us_id)

Delete US

##### count_us(self, filters)

Count US with optional filters

##### search_us(self, search_term, page, size)

Search US by term - returns DTOs

##### get_us_by_site(self, site_name, page, size)

Get all US for a specific site - returns DTOs

##### get_us_by_site_and_area(self, site_name, area, page, size)

Get all US for a specific site and area - returns DTOs

##### get_us_statistics(self, us_id)

Get statistics for a US

