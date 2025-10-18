# pyarchinit_mini/services/thesaurus_service.py

## Overview

This file contains 30 documented elements.

## Classes

### ThesaurusService

Service for managing thesaurus and controlled vocabularies

#### Methods

##### __init__(self, db_manager)

Initializes the service with the provided database manager instance.  
This constructor sets up the necessary database connection required for managing thesaurus and controlled vocabularies.  
It ensures that all subsequent operations within the service have access to the database through the specified DatabaseManager.

##### get_field_values(self, table_name, field_name, language)

Get vocabulary values for a specific field

Args:
    table_name: Database table name
    field_name: Field name
    language: Language code
    
Returns:
    List of vocabulary entries

##### add_field_value(self, table_name, field_name, value, label, description, language)

Add a new vocabulary value for a field

Args:
    table_name: Database table name
    field_name: Field name
    value: The vocabulary value
    label: Human-readable label
    description: Description
    language: Language code
    
Returns:
    Created entry data

##### update_field_value(self, field_id, value, label, description)

Update an existing vocabulary value

Args:
    field_id: Field entry ID
    value: New value
    label: New label
    description: New description
    
Returns:
    Updated entry data

##### delete_field_value(self, field_id)

Delete a vocabulary value

Args:
    field_id: Field entry ID
    
Returns:
    True if deleted successfully

##### get_table_fields(self, table_name)

Get list of fields that have thesaurus entries for a table

Args:
    table_name: Database table name
    
Returns:
    List of field names

##### initialize_default_vocabularies(self)

Initialize default vocabularies from predefined mappings

Returns:
    True if initialized successfully

##### search_values(self, query, table_name, field_name, language)

Search vocabulary values by query string

Args:
    query: Search query
    table_name: Optional table filter
    field_name: Optional field filter
    language: Language code
    
Returns:
    List of matching entries

### ThesaurusService

Service for managing thesaurus and controlled vocabularies

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the service for managing thesaurus and controlled vocabularies.  
This constructor takes a DatabaseManager object as a parameter and assigns it to an instance variable for use in database operations throughout the service.

##### get_field_values(self, table_name, field_name, language)

Get vocabulary values for a specific field

Args:
    table_name: Database table name
    field_name: Field name
    language: Language code
    
Returns:
    List of vocabulary entries

##### add_field_value(self, table_name, field_name, value, label, description, language)

Add a new vocabulary value for a field

Args:
    table_name: Database table name
    field_name: Field name
    value: The vocabulary value
    label: Human-readable label
    description: Description
    language: Language code
    
Returns:
    Created entry data

##### update_field_value(self, field_id, value, label, description)

Update an existing vocabulary value

Args:
    field_id: Field entry ID
    value: New value
    label: New label
    description: New description
    
Returns:
    Updated entry data

##### delete_field_value(self, field_id)

Delete a vocabulary value

Args:
    field_id: Field entry ID
    
Returns:
    True if deleted successfully

##### get_table_fields(self, table_name)

Get list of fields that have thesaurus entries for a table

Args:
    table_name: Database table name
    
Returns:
    List of field names

##### initialize_default_vocabularies(self)

Initialize default vocabularies from predefined mappings

Returns:
    True if initialized successfully

##### search_values(self, query, table_name, field_name, language)

Search vocabulary values by query string

Args:
    query: Search query
    table_name: Optional table filter
    field_name: Optional field filter
    language: Language code
    
Returns:
    List of matching entries

### ThesaurusService

Service for managing thesaurus and controlled vocabularies

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the service for managing thesaurus and controlled vocabularies.  
This method sets up the service with the provided DatabaseManager, enabling database operations required for vocabulary management.

##### get_field_values(self, table_name, field_name, language)

Get vocabulary values for a specific field

Args:
    table_name: Database table name
    field_name: Field name
    language: Language code
    
Returns:
    List of vocabulary entries

##### add_field_value(self, table_name, field_name, value, label, description, language)

Add a new vocabulary value for a field

Args:
    table_name: Database table name
    field_name: Field name
    value: The vocabulary value
    label: Human-readable label
    description: Description
    language: Language code
    
Returns:
    Created entry data

##### update_field_value(self, field_id, value, label, description)

Update an existing vocabulary value

Args:
    field_id: Field entry ID
    value: New value
    label: New label
    description: New description
    
Returns:
    Updated entry data

##### delete_field_value(self, field_id)

Delete a vocabulary value

Args:
    field_id: Field entry ID
    
Returns:
    True if deleted successfully

##### get_table_fields(self, table_name)

Get list of fields that have thesaurus entries for a table

Args:
    table_name: Database table name
    
Returns:
    List of field names

##### initialize_default_vocabularies(self)

Initialize default vocabularies from predefined mappings

Returns:
    True if initialized successfully

##### search_values(self, query, table_name, field_name, language)

Search vocabulary values by query string

Args:
    query: Search query
    table_name: Optional table filter
    field_name: Optional field filter
    language: Language code
    
Returns:
    List of matching entries

