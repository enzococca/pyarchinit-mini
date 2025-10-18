# pyarchinit_mini/harris_matrix/matrix_generator.py

## Overview

This file contains 21 documented elements.

## Classes

### HarrisMatrixGenerator

Generates Harris Matrix from stratigraphic relationships

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the HarrisMatrixGenerator class. This constructor sets up the generator with the provided database manager for accessing stratigraphic data and an optional US service for additional context or functionality.

##### generate_matrix(self, site_name, area)

Generate Harris Matrix graph from site relationships

Args:
    site_name: Site name
    area: Optional area filter
    
Returns:
    NetworkX directed graph representing the Harris Matrix

##### get_matrix_levels(self, graph)

Get topological levels for matrix layout

Returns:
    Dictionary mapping level number to list of US numbers

##### get_matrix_statistics(self, graph)

Get statistics about the Harris Matrix

##### add_relationship(self, site_name, us_from, us_to, relationship_type, certainty, description)

Add a new stratigraphic relationship

Args:
    site_name: Site name
    us_from: US number (from)
    us_to: US number (to)
    relationship_type: Type of relationship
    certainty: Certainty level
    description: Optional description
    
Returns:
    True if successful

### HarrisMatrixGenerator

Generates Harris Matrix from stratigraphic relationships

#### Methods

##### __init__(self, db_manager, us_service)

Initializes a new instance of the class responsible for generating Harris Matrices from stratigraphic relationships. This constructor sets up the required database manager for data access and optionally accepts a unit stratigraphy service for additional functionality. It prepares the class for subsequent matrix generation operations.

##### generate_matrix(self, site_name, area)

Generate Harris Matrix graph from site relationships

Args:
    site_name: Site name
    area: Optional area filter
    
Returns:
    NetworkX directed graph representing the Harris Matrix

##### get_matrix_levels(self, graph)

Get topological levels for matrix layout

Returns:
    Dictionary mapping level number to list of US numbers

##### get_matrix_statistics(self, graph)

Get statistics about the Harris Matrix

##### add_relationship(self, site_name, us_from, us_to, relationship_type, certainty, description)

Add a new stratigraphic relationship

Args:
    site_name: Site name
    us_from: US number (from)
    us_to: US number (to)
    relationship_type: Type of relationship
    certainty: Certainty level
    description: Optional description
    
Returns:
    True if successful

### HarrisMatrixGenerator

Generates Harris Matrix from stratigraphic relationships

#### Methods

##### __init__(self, db_manager, us_service)

Initializes the HarrisMatrixGenerator class by setting up the required database manager and an optional stratigraphic unit service. This method prepares the instance for generating Harris Matrices by establishing the necessary connections to data sources.

##### generate_matrix(self, site_name, area)

Generate Harris Matrix graph from site relationships

Args:
    site_name: Site name
    area: Optional area filter
    
Returns:
    NetworkX directed graph representing the Harris Matrix

##### get_matrix_levels(self, graph)

Get topological levels for matrix layout

Returns:
    Dictionary mapping level number to list of US numbers

##### get_matrix_statistics(self, graph)

Get statistics about the Harris Matrix

##### add_relationship(self, site_name, us_from, us_to, relationship_type, certainty, description)

Add a new stratigraphic relationship

Args:
    site_name: Site name
    us_from: US number (from)
    us_to: US number (to)
    relationship_type: Type of relationship
    certainty: Certainty level
    description: Optional description
    
Returns:
    True if successful

