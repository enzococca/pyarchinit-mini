# pyarchinit_mini/api/site.py

## Overview

This file contains 33 documented elements.

## Functions

### get_sites(page, size, search, nazione, regione, comune, site_service)

Get paginated list of sites with optional filtering and search

**Parameters:**
- `page: int`
- `size: int`
- `search: Optional[str]`
- `nazione: Optional[str]`
- `regione: Optional[str]`
- `comune: Optional[str]`
- `site_service: SiteService`

### get_site(site_id, site_service)

Get site by ID

**Parameters:**
- `site_id: int`
- `site_service: SiteService`

### get_site_by_name(site_name, site_service)

Get site by name

**Parameters:**
- `site_name: str`
- `site_service: SiteService`

### create_site(site_data, site_service)

Create a new site

**Parameters:**
- `site_data: SiteCreate`
- `site_service: SiteService`

### update_site(site_id, site_data, site_service)

Update an existing site

**Parameters:**
- `site_id: int`
- `site_data: SiteUpdate`
- `site_service: SiteService`

### delete_site(site_id, site_service)

Delete a site

**Parameters:**
- `site_id: int`
- `site_service: SiteService`

### get_site_stats(site_id, site_service)

Get statistics for a site (US count, inventory count, etc.)

**Parameters:**
- `site_id: int`
- `site_service: SiteService`

### get_countries(site_service)

Get list of unique countries from sites

**Parameters:**
- `site_service: SiteService`

### get_regions(nazione, site_service)

Get list of unique regions, optionally filtered by country

**Parameters:**
- `nazione: Optional[str]`
- `site_service: SiteService`

### get_municipalities(nazione, regione, site_service)

Get list of unique municipalities, optionally filtered by country and region

**Parameters:**
- `nazione: Optional[str]`
- `regione: Optional[str]`
- `site_service: SiteService`

### get_sites(page, size, search, nazione, regione, comune, site_service)

Get paginated list of sites with optional filtering and search

**Parameters:**
- `page: int`
- `size: int`
- `search: Optional[str]`
- `nazione: Optional[str]`
- `regione: Optional[str]`
- `comune: Optional[str]`
- `site_service: SiteService`

### get_site(site_id, site_service)

Get site by ID

**Parameters:**
- `site_id: int`
- `site_service: SiteService`

### get_site_by_name(site_name, site_service)

Get site by name

**Parameters:**
- `site_name: str`
- `site_service: SiteService`

### create_site(site_data, site_service)

Create a new site

**Parameters:**
- `site_data: SiteCreate`
- `site_service: SiteService`

### update_site(site_id, site_data, site_service)

Update an existing site

**Parameters:**
- `site_id: int`
- `site_data: SiteUpdate`
- `site_service: SiteService`

### delete_site(site_id, site_service)

Delete a site

**Parameters:**
- `site_id: int`
- `site_service: SiteService`

### get_site_stats(site_id, site_service)

Get statistics for a site (US count, inventory count, etc.)

**Parameters:**
- `site_id: int`
- `site_service: SiteService`

### get_countries(site_service)

Get list of unique countries from sites

**Parameters:**
- `site_service: SiteService`

### get_regions(nazione, site_service)

Get list of unique regions, optionally filtered by country

**Parameters:**
- `nazione: Optional[str]`
- `site_service: SiteService`

### get_municipalities(nazione, regione, site_service)

Get list of unique municipalities, optionally filtered by country and region

**Parameters:**
- `nazione: Optional[str]`
- `regione: Optional[str]`
- `site_service: SiteService`

### get_sites(page, size, search, nazione, regione, comune, site_service)

Get paginated list of sites with optional filtering and search

**Parameters:**
- `page: int`
- `size: int`
- `search: Optional[str]`
- `nazione: Optional[str]`
- `regione: Optional[str]`
- `comune: Optional[str]`
- `site_service: SiteService`

### get_site(site_id, site_service)

Get site by ID

**Parameters:**
- `site_id: int`
- `site_service: SiteService`

### get_site_by_name(site_name, site_service)

Get site by name

**Parameters:**
- `site_name: str`
- `site_service: SiteService`

### create_site(site_data, site_service)

Create a new site

**Parameters:**
- `site_data: SiteCreate`
- `site_service: SiteService`

### update_site(site_id, site_data, site_service)

Update an existing site

**Parameters:**
- `site_id: int`
- `site_data: SiteUpdate`
- `site_service: SiteService`

### delete_site(site_id, site_service)

Delete a site

**Parameters:**
- `site_id: int`
- `site_service: SiteService`

### get_site_stats(site_id, site_service)

Get statistics for a site (US count, inventory count, etc.)

**Parameters:**
- `site_id: int`
- `site_service: SiteService`

### get_countries(site_service)

Get list of unique countries from sites

**Parameters:**
- `site_service: SiteService`

### get_regions(nazione, site_service)

Get list of unique regions, optionally filtered by country

**Parameters:**
- `nazione: Optional[str]`
- `site_service: SiteService`

### get_municipalities(nazione, regione, site_service)

Get list of unique municipalities, optionally filtered by country and region

**Parameters:**
- `nazione: Optional[str]`
- `regione: Optional[str]`
- `site_service: SiteService`

