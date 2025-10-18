# pyarchinit_mini/models/thesaurus.py

## Overview

This file contains 27 documented elements.

## Classes

### ThesaurusSigle

Thesaurus for controlled vocabularies and abbreviations
Based on pyarchinit_thesaurus_sigle table

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `ThesaurusSigle` object, including its `id_thesaurus_sigle`, `nome_tabella`, and `sigla` attributes. This representation is primarily intended for debugging and logging purposes, providing a clear and concise summary of the object's key identifying fields.

##### display_value(self)

Display value for UI

### ThesaurusField

Field-specific thesaurus entries
For detailed field vocabularies

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `ThesaurusField` instance, including the table name, field name, and value attributes. This representation is primarily used for debugging and logging, providing a clear and concise summary of the object's key identifying fields.

##### display_name(self)

Display name for UI

### ThesaurusCategory

Categories for organizing thesaurus entries

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `ThesaurusCategory` object, displaying its unique ID and category name. This representation is useful for debugging and logging, as it provides a clear and concise summary of the object's key attributes.

### ThesaurusSigle

Thesaurus for controlled vocabularies and abbreviations
Based on pyarchinit_thesaurus_sigle table

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `ThesaurusSigle` object, displaying key attributes such as `id_thesaurus_sigle`, `nome_tabella`, and `sigla`. This representation is primarily intended for debugging and logging, making it easier to identify and inspect instances of the class.

##### display_value(self)

Display value for UI

### ThesaurusField

Field-specific thesaurus entries
For detailed field vocabularies

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `ThesaurusField` object, including the table name, field name, and value attributes. This representation is useful for debugging and logging, as it provides a clear and concise summary of the object's key identifying information.

##### display_name(self)

Display name for UI

### ThesaurusCategory

Categories for organizing thesaurus entries

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `ThesaurusCategory` instance, displaying its `id_category` and `category_name` attributes. This representation is useful for debugging and logging, as it provides a clear and concise summary of the object's key information.

### ThesaurusSigle

Thesaurus for controlled vocabularies and abbreviations
Based on pyarchinit_thesaurus_sigle table

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `ThesaurusSigle` object, displaying its unique identifier (`id_thesaurus_sigle`), table name (`nome_tabella`), and code (`sigla`). This representation is primarily intended for debugging and logging purposes, providing a concise and informative summary of the object's key attributes.

##### display_value(self)

Display value for UI

### ThesaurusField

Field-specific thesaurus entries
For detailed field vocabularies

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `ThesaurusField` object, displaying the values of its `table_name`, `field_name`, and `value` attributes. This representation is useful for debugging and logging, as it provides a clear and concise summary of the object's key properties.

##### display_name(self)

Display name for UI

### ThesaurusCategory

Categories for organizing thesaurus entries

**Inherits from**: BaseModel

#### Methods

##### __repr__(self)

The `__repr__` method returns a string representation of the `ThesaurusCategory` object, displaying its `id_category` and `category_name` attributes. This representation is intended to provide a concise and informative summary of the object, useful for debugging and logging purposes.

