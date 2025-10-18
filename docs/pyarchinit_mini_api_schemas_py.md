# pyarchinit_mini/api/schemas.py

## Overview

This file contains 57 documented elements.

## Classes

### BaseSchema

Base schema with common fields

**Inherits from**: BaseModel

### SiteBase

Base site schema

**Inherits from**: BaseModel

### SiteCreate

Schema for creating a site

**Inherits from**: SiteBase

### SiteUpdate

Schema for updating a site

**Inherits from**: BaseModel

### SiteResponse

Schema for site response

**Inherits from**: SiteBase, BaseSchema

### USBase

Base US schema

**Inherits from**: BaseModel

### USCreate

Schema for creating a US

**Inherits from**: USBase

### USUpdate

Schema for updating a US

**Inherits from**: BaseModel

### USResponse

Schema for US response

**Inherits from**: USBase, BaseSchema

### InventarioBase

Base inventory schema

**Inherits from**: BaseModel

#### Methods

##### validate_yes_no_fields(cls, v)

The **validate_yes_no_fields** method is a data validator that ensures the values provided for the fields 'lavato', 'repertato', and 'diagnostico' are either 'SI', 'NO', 'S', or 'N' (case-insensitive). If a value is provided and does not match one of these accepted responses, a ValueError is raised. This helps enforce data integrity for fields intended to capture binary yes/no information.

### InventarioCreate

Schema for creating inventory item

**Inherits from**: InventarioBase

### InventarioUpdate

Schema for updating inventory item

**Inherits from**: BaseModel

### InventarioResponse

Schema for inventory response

**Inherits from**: InventarioBase, BaseSchema

### PaginationParams

Pagination parameters

**Inherits from**: BaseModel

### PaginatedResponse

Paginated response wrapper

**Inherits from**: BaseModel

### Config

The **Config** class defines configuration options for a Pydantic model, enabling features such as attribute-based data population by setting `from_attributes = True`. This allows instances of the model to be created directly from objects with matching attribute names, improving flexibility in data parsing and serialization workflows.

### Config

The **Config** class defines the pagination parameters for a dataset, including the current page number (`page`), the number of items per page (`size`), and the total number of pages (`pages`). It leverages attribute-based serialization to facilitate data exchange and validation. This class is typically used to standardize and manage paginated API responses.

### BaseSchema

Base schema with common fields

**Inherits from**: BaseModel

### SiteBase

Base site schema

**Inherits from**: BaseModel

### SiteCreate

Schema for creating a site

**Inherits from**: SiteBase

### SiteUpdate

Schema for updating a site

**Inherits from**: BaseModel

### SiteResponse

Schema for site response

**Inherits from**: SiteBase, BaseSchema

### USBase

Base US schema

**Inherits from**: BaseModel

### USCreate

Schema for creating a US

**Inherits from**: USBase

### USUpdate

Schema for updating a US

**Inherits from**: BaseModel

### USResponse

Schema for US response

**Inherits from**: USBase, BaseSchema

### InventarioBase

Base inventory schema

**Inherits from**: BaseModel

#### Methods

##### validate_yes_no_fields(cls, v)

The **validate_yes_no_fields** method is a Pydantic validator that ensures the values assigned to the 'lavato', 'repertato', and 'diagnostico' fields are either 'SI', 'NO', 'S', or 'N' (case-insensitive). If a value outside of these accepted responses is provided, a ValueError is raised. This validation enforces standardized yes/no input for these fields.

### InventarioCreate

Schema for creating inventory item

**Inherits from**: InventarioBase

### InventarioUpdate

Schema for updating inventory item

**Inherits from**: BaseModel

### InventarioResponse

Schema for inventory response

**Inherits from**: InventarioBase, BaseSchema

### PaginationParams

Pagination parameters

**Inherits from**: BaseModel

### PaginatedResponse

Paginated response wrapper

**Inherits from**: BaseModel

### Config

The **Config** class is an internal configuration class used to customize the behavior of the parent Pydantic model. By setting `from_attributes = True`, it allows model instances to be created from objects with matching attribute names, not just from dictionaries. This enhances flexibility when initializing models from various data sources.

### Config

The Config class defines the structure for pagination configuration, specifying the current page, page size, and total number of pages. Each field includes descriptive metadata to support clear API documentation and validation. The inner Config class enables initialization of instances from attribute-based data sources.

### BaseSchema

Base schema with common fields

**Inherits from**: BaseModel

### SiteBase

Base site schema

**Inherits from**: BaseModel

### SiteCreate

Schema for creating a site

**Inherits from**: SiteBase

### SiteUpdate

Schema for updating a site

**Inherits from**: BaseModel

### SiteResponse

Schema for site response

**Inherits from**: SiteBase, BaseSchema

### USBase

Base US schema

**Inherits from**: BaseModel

### USCreate

Schema for creating a US

**Inherits from**: USBase

### USUpdate

Schema for updating a US

**Inherits from**: BaseModel

### USResponse

Schema for US response

**Inherits from**: USBase, BaseSchema

### InventarioBase

Base inventory schema

**Inherits from**: BaseModel

#### Methods

##### validate_yes_no_fields(cls, v)

The `validate_yes_no_fields` method is a Pydantic validator that ensures the values of the fields `lavato`, `repertato`, and `diagnostico` are either 'SI', 'NO', 'S', or 'N' (case-insensitive). If a value outside these accepted options is provided, it raises a `ValueError`. This validation enforces standardized yes/no responses for these fields.

### InventarioCreate

Schema for creating inventory item

**Inherits from**: InventarioBase

### InventarioUpdate

Schema for updating inventory item

**Inherits from**: BaseModel

### InventarioResponse

Schema for inventory response

**Inherits from**: InventarioBase, BaseSchema

### PaginationParams

Pagination parameters

**Inherits from**: BaseModel

### PaginatedResponse

Paginated response wrapper

**Inherits from**: BaseModel

### Config

The **Config** class is a configuration class used within a Pydantic schema to specify model behaviors and options. In this context, it enables the `from_attributes` setting, allowing the schema to be populated from object attributes rather than just dictionaries. This facilitates seamless integration with ORM models and other objects when creating or updating schema instances.

### Config

The **Config** class defines the pagination configuration for data queries, specifying the current page, the number of items per page, and the total number of pages available. It is designed to facilitate structured and consistent handling of paginated responses. The class is configured to support initialization from attribute-based data sources.

