# pyarchinit_mini/models/harris_matrix.py

## Overview

This file contains 30 documented elements.

## Classes

### HarrisMatrix

Harris Matrix relationships between stratigraphic units

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `HarrisMatrix` object, displaying key attributes such as the site identifier (`sito`) and the relationship between the upper (`us_sopra`) and lower (`us_sotto`) stratigraphic units. This representation is useful for debugging and logging, as it provides a clear and concise summary of the object's state.

### USRelationships

Detailed stratigraphic relationships between US

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `USRelationship` object, displaying its core attributes in a readable format. Specifically, it outputs the source unit (`us_from`), the type of relationship (`relationship_type`), and the target unit (`us_to`). This representation is useful for debugging and logging, as it succinctly summarizes the object's key information.

### Period

Archaeological periods and phases

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `Periodizzazione` instance, displaying its period name along with the start and end dates. This is primarily used for debugging and logging, providing a human-readable summary that helps identify the periodization assignment at a glance.

### Periodizzazione

Periodization assignments for archaeological contexts
Links US and other entities to chronological periods

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `Periodizzazione` object, displaying its associated site (`sito`), stratigraphic unit (`us`), and the initial and final periods (`periodo_iniziale` and `periodo_finale`). This representation is intended to provide a clear and concise summary of the object's key identifying information, primarily for debugging and logging purposes.

##### dating_range(self)

Get formatted dating range

### HarrisMatrix

Harris Matrix relationships between stratigraphic units

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `HarrisMatrix` object, displaying its associated `sito` value as well as the stratigraphic relationship from `us_sopra` (upper unit) to `us_sotto` (lower unit). This representation is useful for debugging and logging, as it provides a concise summary of the object's key attributes and relationships.

### USRelationships

Detailed stratigraphic relationships between US

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `USRelationship` object, displaying its `us_from`, `relationship_type`, and `us_to` attributes in a concise format. This is primarily used for debugging and logging, allowing for an informative and human-readable display of the object's key relational data.

### Period

Archaeological periods and phases

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the Periodizzazione instance, displaying its period name and date range in the format `<Period('period_name', start_date-end_date)>`. This representation is primarily intended for debugging and logging purposes, providing a concise summary of the object's key attributes.

### Periodizzazione

Periodization assignments for archaeological contexts
Links US and other entities to chronological periods

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `Periodizzazione` object, displaying its associated site, US number, and the range between its initial and final periods. This representation is useful for debugging and logging purposes, providing a concise summary of the object's key identifying information.

##### dating_range(self)

Get formatted dating range

### HarrisMatrix

Harris Matrix relationships between stratigraphic units

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The **`__repr__`** method returns a string representation of the `HarrisMatrix` object, displaying key attributes such as the site identifier (`sito`) and the relationship between `us_sopra` and `us_sotto`. This representation is useful for debugging and logging, as it provides a concise summary of the object's essential information.

### USRelationships

Detailed stratigraphic relationships between US

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `USRelationship` object, displaying its key attributes (`us_from`, `relationship_type`, and `us_to`) in a concise format. This representation is useful for debugging and logging, as it allows developers to quickly identify the relationship between stratigraphic units.

### Period

Archaeological periods and phases

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `Period` object, displaying its `period_name` along with the `start_date` and `end_date`. This representation is intended to provide a concise and informative summary of the object's key attributes for debugging and logging purposes.

### Periodizzazione

Periodization assignments for archaeological contexts
Links US and other entities to chronological periods

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `Periodizzazione` object, including its associated site (`sito`), stratigraphic unit (`us`), and the range from the initial to the final period (`periodo_iniziale`-`periodo_finale`). This representation is primarily used for debugging and logging, making it easier to identify specific instances of the class.

##### dating_range(self)

Get formatted dating range

