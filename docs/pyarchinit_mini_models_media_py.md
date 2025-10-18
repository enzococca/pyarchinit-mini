# pyarchinit_mini/models/media.py

## Overview

This file contains 27 documented elements.

## Classes

### Media

Media files (images, documents, videos) linked to archaeological records

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the Media object, displaying its media name along with the associated entity type and entity ID. This representation is primarily intended for debugging and logging, making it easier to identify specific Media instances in output or logs.

##### is_image(self)

The **is_image** property returns a boolean indicating whether the media instance is classified as an image. It evaluates to **True** if the instance's `media_type` attribute is set to `'image'`; otherwise, it returns **False**. This property enables quick checks for image-type media objects within the class.

##### is_document(self)

**is_document**  
Indicates whether the media file is of type 'document'. Returns True if the media_type attribute equals 'document', otherwise returns False. This property helps differentiate document files from other media types.

### MediaThumb

Thumbnails for media files

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The __repr__ method provides a string representation of the MediaThumb object, displaying its associated media ID and thumbnail size. This representation is useful for debugging and logging, as it clearly identifies instances of MediaThumb in an informative and readable format.

### Documentation

Documentation files and reports

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The __repr__ method returns a string representation of the Documentation object, including its title, entity type, and entity ID. This representation is useful for debugging and logging, as it provides a concise summary of the object's key identifying information.

### Media

Media files (images, documents, videos) linked to archaeological records

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the Media object, displaying its media name, entity type, and entity ID. This representation is primarily intended for debugging and logging purposes, allowing developers to easily identify individual Media instances in output.

##### is_image(self)

The **is_image** property determines whether the media object's type is classified as an image. It returns `True` if the `media_type` attribute equals `'image'`; otherwise, it returns `False`. This is useful for quickly checking the nature of the media without directly accessing its type attribute.

##### is_document(self)

**is_document**  
Returns a boolean indicating whether the media file is classified as a document. This property evaluates to True if the media_type attribute equals 'document', enabling type checks within media handling workflows.

### MediaThumb

Thumbnails for media files

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The __repr__ method returns a string representation of the MediaThumb object, displaying its associated media ID and thumbnail size. This representation is useful for debugging and logging, as it provides a concise summary of the object's key identifying attributes.

### Documentation

Documentation files and reports

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The __repr__ method returns a string representation of the Documentation object, including its title, entity type, and entity ID. This representation is intended to provide a concise summary of the instance, making it useful for debugging and logging purposes.

### Media

Media files (images, documents, videos) linked to archaeological records

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the Media object, displaying its `media_name`, `entity_type`, and `entity_id`. This provides a clear and informative summary of the object, which is useful for debugging and logging purposes.

##### is_image(self)

The **is_image** property returns a boolean value indicating whether the media instance is of type 'image'. It evaluates to True if the `media_type` attribute equals 'image', and False otherwise. This property is useful for distinguishing images from other media types within the class.

##### is_document(self)

**is_document**  
Returns True if the media file is classified as a document. This property checks whether the media_type attribute of the instance is set to 'document', allowing for easy identification of document-type media files.

### MediaThumb

Thumbnails for media files

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The __repr__ method returns a string representation of the MediaThumb instance, displaying its associated media ID and thumbnail size. This is useful for debugging and logging, as it provides a concise summary of the object's key attributes.

### Documentation

Documentation files and reports

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The __repr__ method returns a string representation of the Documentation object, displaying its title, entity type, and entity ID in a concise format. This representation is primarily intended for debugging and logging purposes, providing a clear and informative summary of the object's key identifying attributes.

