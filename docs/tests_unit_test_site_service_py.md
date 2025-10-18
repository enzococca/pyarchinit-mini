# tests/unit/test_site_service.py

## Overview

This file contains 10 documented elements.

## Functions

### test_create_site_success(site_service, sample_site_data)

Test successful site creation

**Parameters:**
- `site_service`
- `sample_site_data`

### test_create_site_duplicate_name(site_service, sample_site_data)

Test that duplicate site names are rejected

**Parameters:**
- `site_service`
- `sample_site_data`

### test_create_site_invalid_data(site_service)

Test validation of site data

**Parameters:**
- `site_service`

### test_get_site_by_id(site_service, sample_site_data)

Test retrieving site by ID

**Parameters:**
- `site_service`
- `sample_site_data`

### test_get_site_by_name(site_service, sample_site_data)

Test retrieving site by name

**Parameters:**
- `site_service`
- `sample_site_data`

### test_update_site(site_service, sample_site_data)

Test updating site data

**Parameters:**
- `site_service`
- `sample_site_data`

### test_delete_site(site_service, sample_site_data)

Test deleting a site

**Parameters:**
- `site_service`
- `sample_site_data`

### test_get_all_sites(site_service)

Test getting all sites with pagination

**Parameters:**
- `site_service`

### test_count_sites(site_service, sample_site_data)

Test counting sites

**Parameters:**
- `site_service`
- `sample_site_data`

