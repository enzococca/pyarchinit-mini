# pyarchinit_mini/utils/validators.py

## Overview

This file contains 36 documented elements.

## Classes

### BaseValidator

Base validator class

#### Methods

##### validate_required_fields(data, required_fields)

Validate that all required fields are present and not empty

##### validate_string_length(value, field_name, max_length, min_length)

Validate string length

##### validate_numeric_range(value, field_name, min_value, max_value)

Validate numeric value is within range

### SiteValidator

Validator for Site model data

**Inherits from**: BaseValidator

#### Methods

##### validate(cls, data)

Validate site data

### USValidator

Validator for US (Stratigraphic Unit) model data

**Inherits from**: BaseValidator

#### Methods

##### validate(cls, data)

Validate US data

### InventarioValidator

Validator for Inventario Materiali model data

**Inherits from**: BaseValidator

#### Methods

##### validate(cls, data)

Validate inventory material data

### BaseValidator

Base validator class

#### Methods

##### validate_required_fields(data, required_fields)

Validate that all required fields are present and not empty

##### validate_string_length(value, field_name, max_length, min_length)

Validate string length

##### validate_numeric_range(value, field_name, min_value, max_value)

Validate numeric value is within range

### SiteValidator

Validator for Site model data

**Inherits from**: BaseValidator

#### Methods

##### validate(cls, data)

Validate site data

### USValidator

Validator for US (Stratigraphic Unit) model data

**Inherits from**: BaseValidator

#### Methods

##### validate(cls, data)

Validate US data

### InventarioValidator

Validator for Inventario Materiali model data

**Inherits from**: BaseValidator

#### Methods

##### validate(cls, data)

Validate inventory material data

### BaseValidator

Base validator class

#### Methods

##### validate_required_fields(data, required_fields)

Validate that all required fields are present and not empty

##### validate_string_length(value, field_name, max_length, min_length)

Validate string length

##### validate_numeric_range(value, field_name, min_value, max_value)

Validate numeric value is within range

### SiteValidator

Validator for Site model data

**Inherits from**: BaseValidator

#### Methods

##### validate(cls, data)

Validate site data

### USValidator

Validator for US (Stratigraphic Unit) model data

**Inherits from**: BaseValidator

#### Methods

##### validate(cls, data)

Validate US data

### InventarioValidator

Validator for Inventario Materiali model data

**Inherits from**: BaseValidator

#### Methods

##### validate(cls, data)

Validate inventory material data

## Functions

### validate_data(model_type, data)

Validate data based on model type

Args:
    model_type: Type of model ('site', 'us', 'inventario')
    data: Data to validate

Raises:
    ValidationError: If validation fails

**Parameters:**
- `model_type: str`
- `data: Dict[str, Any]`

### validate_data(model_type, data)

Validate data based on model type

Args:
    model_type: Type of model ('site', 'us', 'inventario')
    data: Data to validate

Raises:
    ValidationError: If validation fails

**Parameters:**
- `model_type: str`
- `data: Dict[str, Any]`

### validate_data(model_type, data)

Validate data based on model type

Args:
    model_type: Type of model ('site', 'us', 'inventario')
    data: Data to validate

Raises:
    ValidationError: If validation fails

**Parameters:**
- `model_type: str`
- `data: Dict[str, Any]`

