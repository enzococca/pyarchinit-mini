# pyarchinit_mini/services/site_service.py

## Overview

This file contains 56 documented elements.

## Classes

### SiteService

Service class for site operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the SiteService class.  
This constructor method accepts a DatabaseManager object and assigns it to an instance variable, enabling the service to interact with the database.

##### create_site(self, site_data)

Create a new site

##### get_site_by_id(self, site_id)

Get site by ID

##### get_site_dto_by_id(self, site_id)

Get site by ID as DTO

##### get_site_by_name(self, site_name)

Get site by name

##### get_all_sites(self, page, size, filters)

Get all sites with pagination and filtering - returns DTOs

##### update_site(self, site_id, update_data)

Update existing site

##### delete_site(self, site_id)

Delete site

##### count_sites(self, filters)

Count sites with optional filters

##### search_sites(self, search_term, page, size, filters)

Search sites by term - returns DTOs

##### get_unique_countries(self)

Get list of unique countries

##### get_unique_regions(self, nazione)

Get list of unique regions, optionally filtered by country

##### get_unique_municipalities(self, nazione, regione)

Get list of unique municipalities with optional filters

##### get_site_statistics(self, site_id)

Get statistics for a site

### SiteService

Service class for site operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the SiteService class.  
This constructor accepts a DatabaseManager object, which is used to manage database operations related to site functionalities.

##### create_site(self, site_data)

Create a new site

##### create_site_dto(self, site_data)

Create a new site and return as DTO

##### get_site_by_id(self, site_id)

Get site by ID

##### get_site_dto_by_id(self, site_id)

Get site by ID as DTO

##### get_site_by_name(self, site_name)

Get site by name

##### get_all_sites(self, page, size, filters)

Get all sites with pagination and filtering - returns DTOs

##### update_site(self, site_id, update_data)

Update existing site

##### update_site_dto(self, site_id, update_data)

Update existing site and return DTO

##### delete_site(self, site_id)

Delete site

##### count_sites(self, filters)

Count sites with optional filters

##### search_sites(self, search_term, page, size, filters)

Search sites by term - returns DTOs

##### get_unique_countries(self)

Get list of unique countries

##### get_unique_regions(self, nazione)

Get list of unique regions, optionally filtered by country

##### get_unique_municipalities(self, nazione, regione)

Get list of unique municipalities with optional filters

##### get_site_statistics(self, site_id)

Get statistics for a site

##### get_all_sites_dto(self, page, size)

Get all sites as DTOs with pagination

##### count_sites(self)

Count total number of sites

### SiteService

Service class for site operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the SiteService class.  
This constructor method accepts a DatabaseManager object and assigns it to the instance for managing database operations related to site functionality.

##### create_site(self, site_data)

Create a new site

##### create_site_dto(self, site_data)

Create a new site and return as DTO

##### get_site_by_id(self, site_id)

Get site by ID

##### get_site_dto_by_id(self, site_id)

Get site by ID as DTO

##### get_site_by_name(self, site_name)

Get site by name

##### get_all_sites(self, page, size, filters)

Get all sites with pagination and filtering - returns DTOs

##### update_site(self, site_id, update_data)

Update existing site

##### update_site_dto(self, site_id, update_data)

Update existing site and return DTO

##### delete_site(self, site_id)

Delete site

##### count_sites(self, filters)

Count sites with optional filters

##### search_sites(self, search_term, page, size, filters)

Search sites by term - returns DTOs

##### get_unique_countries(self)

Get list of unique countries

##### get_unique_regions(self, nazione)

Get list of unique regions, optionally filtered by country

##### get_unique_municipalities(self, nazione, regione)

Get list of unique municipalities with optional filters

##### get_site_statistics(self, site_id)

Get statistics for a site

##### get_all_sites_dto(self, page, size)

Get all sites as DTOs with pagination

##### count_sites(self)

Count total number of sites

