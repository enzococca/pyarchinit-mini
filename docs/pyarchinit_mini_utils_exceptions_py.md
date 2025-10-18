# pyarchinit_mini/utils/exceptions.py

## Overview

This file contains 30 documented elements.

## Classes

### PyArchInitMiniError

Base exception class for PyArchInit-Mini

**Inherits from**: Exception

### DatabaseError

Raised when database operations fail

**Inherits from**: PyArchInitMiniError

### ValidationError

Raised when data validation fails

**Inherits from**: PyArchInitMiniError

#### Methods

##### __init__(self, message, field, value)

Initializes a new instance of the ValidationError class. This method sets the error message, and optionally associates the error with a specific field and value that caused the validation to fail. It also calls the initializer of the base exception class with the provided message.

### RecordNotFoundError

Raised when a requested record is not found

**Inherits from**: PyArchInitMiniError

### DuplicateRecordError

Raised when trying to create a duplicate record

**Inherits from**: PyArchInitMiniError

### ConnectionError

Raised when database connection fails

**Inherits from**: PyArchInitMiniError

### ConfigurationError

Raised when configuration is invalid

**Inherits from**: PyArchInitMiniError

### PermissionError

Raised when user lacks required permissions

**Inherits from**: PyArchInitMiniError

### PyArchInitMiniError

Base exception class for PyArchInit-Mini

**Inherits from**: Exception

### DatabaseError

Raised when database operations fail

**Inherits from**: PyArchInitMiniError

### ValidationError

Raised when data validation fails

**Inherits from**: PyArchInitMiniError

#### Methods

##### __init__(self, message, field, value)

Initializes a new instance of the ValidationError class with a specified error message, and optionally the field and value that caused the validation to fail. This constructor also calls the base class initializer with the provided message, and stores the field and value information for further context about the validation error.

### RecordNotFoundError

Raised when a requested record is not found

**Inherits from**: PyArchInitMiniError

### DuplicateRecordError

Raised when trying to create a duplicate record

**Inherits from**: PyArchInitMiniError

### ConnectionError

Raised when database connection fails

**Inherits from**: PyArchInitMiniError

### ConfigurationError

Raised when configuration is invalid

**Inherits from**: PyArchInitMiniError

### PermissionError

Raised when user lacks required permissions

**Inherits from**: PyArchInitMiniError

### PyArchInitMiniError

Base exception class for PyArchInit-Mini

**Inherits from**: Exception

### DatabaseError

Raised when database operations fail

**Inherits from**: PyArchInitMiniError

### ValidationError

Raised when data validation fails

**Inherits from**: PyArchInitMiniError

#### Methods

##### __init__(self, message, field, value)

Initializes a new instance of the **ValidationError** class with a specified error message, and optionally the name of the field and its associated value that caused the validation to fail.  
This constructor passes the error message to the base exception class and stores the field and value information for further context about the validation error.

### RecordNotFoundError

Raised when a requested record is not found

**Inherits from**: PyArchInitMiniError

### DuplicateRecordError

Raised when trying to create a duplicate record

**Inherits from**: PyArchInitMiniError

### ConnectionError

Raised when database connection fails

**Inherits from**: PyArchInitMiniError

### ConfigurationError

Raised when configuration is invalid

**Inherits from**: PyArchInitMiniError

### PermissionError

Raised when user lacks required permissions

**Inherits from**: PyArchInitMiniError

