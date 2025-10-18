# pyarchinit_mini/services/media_service.py

## Overview

This file contains 84 documented elements.

## Classes

### MediaService

Service class for media operations

#### Methods

##### __init__(self, db_manager, media_handler)

Initializes a new instance of the MediaService class. This constructor accepts a DatabaseManager object for database operations and an optional MediaHandler; if none is provided, a default MediaHandler instance is created.

##### create_media_record(self, media_data)

Create a new media record in database

##### store_and_register_media(self, file_path, entity_type, entity_id, description, tags, author, is_primary)

Store media file and register in database

##### get_media_by_id(self, media_id)

Get media by ID

##### get_all_media(self, page, size, filters)

Get all media with pagination and filtering

##### get_media_by_entity(self, entity_type, entity_id, page, size)

Get all media for a specific entity

##### get_media_by_type(self, media_type, page, size)

Get all media of a specific type

##### search_media(self, search_term, page, size)

Search media by term

##### update_media(self, media_id, update_data)

Update existing media

##### delete_media(self, media_id, delete_file)

Delete media record and optionally the file

##### count_media(self, filters)

Count media with optional filters

##### set_primary_media(self, media_id, entity_type, entity_id)

Set media as primary for an entity

##### get_primary_media(self, entity_type, entity_id)

Get primary media for an entity

##### get_media_statistics(self)

Get media statistics

##### get_media_by_site_summary(self, site_name)

Get media summary for a site

##### create_media_collection(self, collection_name, entity_type, entity_id, media_ids)

Create a media collection (virtual grouping)

##### export_media_archive(self, entity_type, entity_id, archive_path, include_metadata)

Export media archive for an entity

### DocumentationService

Service class for documentation operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the DocumentationService class.  
This constructor method takes a DatabaseManager object as a parameter and assigns it to an instance variable for use in documentation operations.

##### create_documentation(self, doc_data)

Create a new documentation record

##### get_documentation_by_id(self, doc_id)

Get documentation by ID

##### get_documentation_by_entity(self, entity_type, entity_id, page, size)

Get all documentation for a specific entity

##### get_all_documentation(self, page, size, filters)

Get all documentation with pagination and filtering

##### update_documentation(self, doc_id, update_data)

Update existing documentation

##### delete_documentation(self, doc_id, delete_file)

Delete documentation record and optionally the file

##### count_documentation(self, filters)

Count documentation with optional filters

### MediaService

Service class for media operations

#### Methods

##### __init__(self, db_manager, media_handler)

Initializes a new instance of the MediaService class.  
This constructor accepts a DatabaseManager instance for database operations and an optional MediaHandler; if no MediaHandler is provided, a default instance is created and used.

##### create_media_record(self, media_data)

Create a new media record in database

##### store_and_register_media(self, file_path, entity_type, entity_id, description, tags, author, is_primary)

Store media file and register in database

##### get_media_by_id(self, media_id)

Get media by ID

##### get_all_media(self, page, size, filters)

Get all media with pagination and filtering

##### get_media_by_entity(self, entity_type, entity_id, page, size)

Get all media for a specific entity

##### get_media_by_type(self, media_type, page, size)

Get all media of a specific type

##### search_media(self, search_term, page, size)

Search media by term

##### update_media(self, media_id, update_data)

Update existing media

##### delete_media(self, media_id, delete_file)

Delete media record and optionally the file

##### count_media(self, filters)

Count media with optional filters

##### set_primary_media(self, media_id, entity_type, entity_id)

Set media as primary for an entity

##### get_primary_media(self, entity_type, entity_id)

Get primary media for an entity

##### get_media_statistics(self)

Get media statistics

##### get_media_by_site_summary(self, site_name)

Get media summary for a site

##### create_media_collection(self, collection_name, entity_type, entity_id, media_ids)

Create a media collection (virtual grouping)

##### export_media_archive(self, entity_type, entity_id, archive_path, include_metadata)

Export media archive for an entity

### DocumentationService

Service class for documentation operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the DocumentationService class. This constructor takes a DatabaseManager object as a parameter and assigns it to an instance variable for managing database interactions related to documentation operations.

##### create_documentation(self, doc_data)

Create a new documentation record

##### get_documentation_by_id(self, doc_id)

Get documentation by ID

##### get_documentation_by_entity(self, entity_type, entity_id, page, size)

Get all documentation for a specific entity

##### get_all_documentation(self, page, size, filters)

Get all documentation with pagination and filtering

##### update_documentation(self, doc_id, update_data)

Update existing documentation

##### delete_documentation(self, doc_id, delete_file)

Delete documentation record and optionally the file

##### count_documentation(self, filters)

Count documentation with optional filters

### MediaService

Service class for media operations

#### Methods

##### __init__(self, db_manager, media_handler)

Initializes a new instance of the MediaService class with the specified database manager and an optional media handler. If no media handler is provided, a default MediaHandler instance is created and used. This setup prepares the service for performing media-related operations with the given dependencies.

##### create_media_record(self, media_data)

Create a new media record in database

##### store_and_register_media(self, file_path, entity_type, entity_id, description, tags, author, is_primary)

Store media file and register in database

##### get_media_by_id(self, media_id)

Get media by ID

##### get_all_media(self, page, size, filters)

Get all media with pagination and filtering

##### get_media_by_entity(self, entity_type, entity_id, page, size)

Get all media for a specific entity

##### get_media_by_type(self, media_type, page, size)

Get all media of a specific type

##### search_media(self, search_term, page, size)

Search media by term

##### update_media(self, media_id, update_data)

Update existing media

##### delete_media(self, media_id, delete_file)

Delete media record and optionally the file

##### count_media(self, filters)

Count media with optional filters

##### set_primary_media(self, media_id, entity_type, entity_id)

Set media as primary for an entity

##### get_primary_media(self, entity_type, entity_id)

Get primary media for an entity

##### get_media_statistics(self)

Get media statistics

##### get_media_by_site_summary(self, site_name)

Get media summary for a site

##### create_media_collection(self, collection_name, entity_type, entity_id, media_ids)

Create a media collection (virtual grouping)

##### export_media_archive(self, entity_type, entity_id, archive_path, include_metadata)

Export media archive for an entity

### DocumentationService

Service class for documentation operations

#### Methods

##### __init__(self, db_manager)

Initializes a new instance of the DocumentationService class by assigning the provided DatabaseManager instance to the db_manager attribute. This setup enables the service to perform documentation operations using the specified database manager.

##### create_documentation(self, doc_data)

Create a new documentation record

##### get_documentation_by_id(self, doc_id)

Get documentation by ID

##### get_documentation_by_entity(self, entity_type, entity_id, page, size)

Get all documentation for a specific entity

##### get_all_documentation(self, page, size, filters)

Get all documentation with pagination and filtering

##### update_documentation(self, doc_id, update_data)

Update existing documentation

##### delete_documentation(self, doc_id, delete_file)

Delete documentation record and optionally the file

##### count_documentation(self, filters)

Count documentation with optional filters

