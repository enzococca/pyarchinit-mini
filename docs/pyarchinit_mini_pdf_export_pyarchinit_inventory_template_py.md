# pyarchinit_mini/pdf_export/pyarchinit_inventory_template.py

## Overview

This file contains 7 documented elements.

## Classes

### PyArchInitInventoryTemplate

Authentic PyArchInit inventory template following the original design

#### Methods

##### __init__(self)

Initializes a new instance of the class by configuring the document’s visual styles according to the authentic PyArchInit inventory template. This method calls setup_styles() to apply PyArchInit-specific style settings, ensuring consistent formatting throughout the document.

##### setup_styles(self)

Setup PyArchInit specific styles

##### generate_inventory_sheets(self, inventario_list, output_path, site_name)

Generate inventory sheets in authentic PyArchInit A5 format

Args:
    inventario_list: List of inventory items
    output_path: Output file path
    site_name: Site name for header
    
Returns:
    Generated file path

##### generate_inventory_catalog(self, inventario_list, output_path, site_name)

Generate inventory catalog (summary table) in A4 format

Args:
    inventario_list: List of inventory items
    output_path: Output file path 
    site_name: Site name for header
    
Returns:
    Generated file path

## Functions

### safe_str(value)

Safely convert value to string

**Parameters:**
- `value`

