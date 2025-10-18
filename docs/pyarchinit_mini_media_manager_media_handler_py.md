# pyarchinit_mini/media_manager/media_handler.py

## Overview

This file contains 27 documented elements.

## Classes

### MediaHandler

Handles media file operations, storage, and organization

#### Methods

##### __init__(self, base_media_path)

Initializes the media handler by setting up the base directory for media storage. Creates the main media directory and standard subdirectories for images, documents, videos, and thumbnails if they do not already exist. This ensures an organized file structure for subsequent media operations.

##### store_file(self, file_path, entity_type, entity_id, description, tags, author)

Store a media file and return metadata

Args:
    file_path: Source file path
    entity_type: Type of entity (site, us, inventario)
    entity_id: Entity ID
    description: File description
    tags: Tags for the file
    author: Author/photographer
    
Returns:
    Dictionary with file metadata

##### get_file_path(self, media_filename, entity_type, entity_id)

Get full path to stored media file

##### delete_file(self, media_filename, entity_type, entity_id)

Delete media file and its thumbnails

##### get_media_info(self, file_path)

Get detailed media information

##### organize_media_by_entity(self, entity_type, entity_id)

Get all media files for a specific entity

##### create_media_archive(self, entity_type, entity_id, archive_path)

Create ZIP archive of all media for an entity

### MediaHandler

Handles media file operations, storage, and organization

#### Methods

##### __init__(self, base_media_path)

Initializes the media file handler by setting up the base media directory and creating the necessary subdirectories for images, documents, videos, and thumbnails. If the specified base directory or any subdirectory does not exist, it is created automatically. This ensures that the required folder structure is in place for subsequent media file operations.

##### store_file(self, file_path, entity_type, entity_id, description, tags, author)

Store a media file and return metadata

Args:
    file_path: Source file path
    entity_type: Type of entity (site, us, inventario)
    entity_id: Entity ID
    description: File description
    tags: Tags for the file
    author: Author/photographer
    
Returns:
    Dictionary with file metadata

##### get_file_path(self, media_filename, entity_type, entity_id)

Get full path to stored media file

##### delete_file(self, media_filename, entity_type, entity_id)

Delete media file and its thumbnails

##### get_media_info(self, file_path)

Get detailed media information

##### organize_media_by_entity(self, entity_type, entity_id)

Get all media files for a specific entity

##### create_media_archive(self, entity_type, entity_id, archive_path)

Create ZIP archive of all media for an entity

### MediaHandler

Handles media file operations, storage, and organization

#### Methods

##### __init__(self, base_media_path)

Initializes the media file handler by setting up the base media directory and creating standardized subdirectories for images, documents, videos, and thumbnails. Ensures that all required folders exist for organized storage and future media file operations. The base path can be customized via the `base_media_path` parameter.

##### store_file(self, file_path, entity_type, entity_id, description, tags, author)

Store a media file and return metadata

Args:
    file_path: Source file path
    entity_type: Type of entity (site, us, inventario)
    entity_id: Entity ID
    description: File description
    tags: Tags for the file
    author: Author/photographer
    
Returns:
    Dictionary with file metadata

##### get_file_path(self, media_filename, entity_type, entity_id)

Get full path to stored media file

##### delete_file(self, media_filename, entity_type, entity_id)

Delete media file and its thumbnails

##### get_media_info(self, file_path)

Get detailed media information

##### organize_media_by_entity(self, entity_type, entity_id)

Get all media files for a specific entity

##### create_media_archive(self, entity_type, entity_id, archive_path)

Create ZIP archive of all media for an entity

