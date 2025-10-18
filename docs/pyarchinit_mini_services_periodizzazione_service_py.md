# pyarchinit_mini/services/periodizzazione_service.py

## Overview

This file contains 66 documented elements.

## Classes

### PeriodizzazioneService

Service class for periodization operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the PeriodizzazioneService class.  
This constructor method accepts a DatabaseManager object and assigns it to the service instance, enabling database operations for periodization-related methods.

##### create_period(self, period_data)

Create a new archaeological period

##### get_period_by_id(self, period_id)

Get period by ID

##### get_all_periods(self, page, size, filters)

Get all periods with pagination and filtering

##### search_periods(self, search_term, page, size)

Search periods by term

##### update_period(self, period_id, update_data)

Update existing period

##### delete_period(self, period_id)

Delete period

##### count_periods(self, filters)

Count periods with optional filters

##### create_periodizzazione(self, periodizzazione_data)

Create a new periodization assignment

##### get_periodizzazione_by_id(self, periodizzazione_id)

Get periodizzazione by ID

##### get_all_periodizzazioni(self, page, size, filters)

Get all periodizations with pagination and filtering

##### get_periodizzazioni_by_site(self, site_name, page, size)

Get all periodizations for a specific site

##### get_periodizzazioni_by_period(self, period_name, page, size)

Get all periodizations for a specific period

##### search_periodizzazioni(self, search_term, page, size)

Search periodizations by term

##### update_periodizzazione(self, periodizzazione_id, update_data)

Update existing periodizzazione

##### delete_periodizzazione(self, periodizzazione_id)

Delete periodizzazione

##### count_periodizzazioni(self, filters)

Count periodizations with optional filters

##### get_dating_summary_by_site(self, site_name)

Get dating summary for a site

##### get_chronological_sequence(self, site_name)

Get chronological sequence for a site based on US relationships and dating

##### get_period_statistics(self)

Get general statistics about periods and dating

### PeriodizzazioneService

Service class for periodization operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the PeriodizzazioneService class.  
This constructor method accepts a DatabaseManager object, which is used to manage database operations related to periodization, and assigns it to an instance variable for use in the service methods.

##### create_period(self, period_data)

Create a new archaeological period

##### get_period_by_id(self, period_id)

Get period by ID

##### get_all_periods(self, page, size, filters)

Get all periods with pagination and filtering

##### search_periods(self, search_term, page, size)

Search periods by term

##### update_period(self, period_id, update_data)

Update existing period

##### delete_period(self, period_id)

Delete period

##### count_periods(self, filters)

Count periods with optional filters

##### create_periodizzazione(self, periodizzazione_data)

Create a new periodization assignment

##### get_periodizzazione_by_id(self, periodizzazione_id)

Get periodizzazione by ID

##### get_all_periodizzazioni(self, page, size, filters)

Get all periodizations with pagination and filtering

##### get_periodizzazioni_by_site(self, site_name, page, size)

Get all periodizations for a specific site

##### get_periodizzazioni_by_period(self, period_name, page, size)

Get all periodizations for a specific period

##### search_periodizzazioni(self, search_term, page, size)

Search periodizations by term

##### update_periodizzazione(self, periodizzazione_id, update_data)

Update existing periodizzazione

##### delete_periodizzazione(self, periodizzazione_id)

Delete periodizzazione

##### count_periodizzazioni(self, filters)

Count periodizations with optional filters

##### get_dating_summary_by_site(self, site_name)

Get dating summary for a site

##### get_chronological_sequence(self, site_name)

Get chronological sequence for a site based on US relationships and dating

##### get_period_statistics(self)

Get general statistics about periods and dating

### PeriodizzazioneService

Service class for periodization operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the PeriodizzazioneService class.  
This constructor method accepts a DatabaseManager object and assigns it to the instance, enabling database operations for periodization tasks.

##### create_period(self, period_data)

Create a new archaeological period

##### get_period_by_id(self, period_id)

Get period by ID

##### get_all_periods(self, page, size, filters)

Get all periods with pagination and filtering

##### search_periods(self, search_term, page, size)

Search periods by term

##### update_period(self, period_id, update_data)

Update existing period

##### delete_period(self, period_id)

Delete period

##### count_periods(self, filters)

Count periods with optional filters

##### create_periodizzazione(self, periodizzazione_data)

Create a new periodization assignment

##### get_periodizzazione_by_id(self, periodizzazione_id)

Get periodizzazione by ID

##### get_all_periodizzazioni(self, page, size, filters)

Get all periodizations with pagination and filtering

##### get_periodizzazioni_by_site(self, site_name, page, size)

Get all periodizations for a specific site

##### get_periodizzazioni_by_period(self, period_name, page, size)

Get all periodizations for a specific period

##### search_periodizzazioni(self, search_term, page, size)

Search periodizations by term

##### update_periodizzazione(self, periodizzazione_id, update_data)

Update existing periodizzazione

##### delete_periodizzazione(self, periodizzazione_id)

Delete periodizzazione

##### count_periodizzazioni(self, filters)

Count periodizations with optional filters

##### get_dating_summary_by_site(self, site_name)

Get dating summary for a site

##### get_chronological_sequence(self, site_name)

Get chronological sequence for a site based on US relationships and dating

##### get_period_statistics(self)

Get general statistics about periods and dating

