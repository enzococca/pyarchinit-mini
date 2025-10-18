# scripts/populate_sample_data.py

## Overview

This file contains 24 documented elements.

## Classes

### SampleDataGenerator

Generator for archaeological sample data

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the `SampleDataGenerator` class by setting up predefined data attributes used for generating archaeological sample data. This includes references to the database manager, site information, lists of areas, archaeological periods, formation types, material types, and relevant descriptive categories.

##### create_site(self)

Create the sample archaeological site

##### create_periods(self)

Create archaeological periods

##### create_thesaurus(self)

Create thesaurus entries

##### create_us_records(self, site)

Create 100 US records with realistic stratigraphic data

##### create_stratigraphic_relationships(self, us_records)

Create realistic stratigraphic relationships

##### create_materials(self, us_records)

Create 50 material records distributed across US

##### create_periodization(self, us_records, periods)

Create periodization assignments for US

##### generate_all_data(self)

Generate complete sample dataset

### SampleDataGenerator

Generator for archaeological sample data

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the SampleDataGenerator class with predefined attributes for generating archaeological sample data. This constructor sets up references to the database manager, site name, and various lists representing archaeological periods, formation types, material types, and related properties used in sample data generation.

##### create_site(self)

Create the sample archaeological site

##### create_periods(self)

Create archaeological periods

##### create_thesaurus(self)

Create thesaurus entries

##### create_us_records(self, site)

Create 100 US records with realistic stratigraphic data

##### create_stratigraphic_relationships(self, us_records)

Create realistic stratigraphic relationships

##### create_materials(self, us_records)

Create 50 material records distributed across US

##### create_periodization(self, us_records, periods)

Create periodization assignments for US

##### generate_all_data(self)

Generate complete sample dataset

## Functions

### main()

Main function to run sample data generation

### main()

Main function to run sample data generation

