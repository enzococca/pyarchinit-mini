# pyarchinit_mini/pdf_export/pdf_generator.py

## Overview

This file contains 22 documented elements.

## Classes

### PDFGenerator

Generate PDF reports for archaeological data

#### Methods

##### __init__(self)

Initializes a new instance of the PDFGenerator class. This method sets up the default stylesheet for PDF generation and applies any custom paragraph styles required for formatting archaeological reports.

##### generate_site_report(self, site_data, us_list, inventory_list, media_list, output_path)

Generate comprehensive site report

Args:
    site_data: Site information
    us_list: List of stratigraphic units
    inventory_list: List of inventory items
    media_list: List of media files
    output_path: Optional output file path
    
Returns:
    PDF bytes

##### generate_harris_matrix_report(self, site_name, matrix_image_path, relationships, statistics, output_path)

Generate Harris Matrix documentation report

### PDFGenerator

Generate PDF reports for archaeological data

#### Methods

##### __init__(self)

Initializes the PDF report generator by setting up the default paragraph styles used throughout the document. This method retrieves a sample stylesheet and applies any custom styles needed for formatting the report content.

##### generate_site_report(self, site_data, us_list, inventory_list, media_list, output_path)

Generate comprehensive site report

Args:
    site_data: Site information
    us_list: List of stratigraphic units
    inventory_list: List of inventory items
    media_list: List of media files
    output_path: Optional output file path
    
Returns:
    PDF bytes

##### generate_harris_matrix_report(self, site_name, matrix_image_path, relationships, statistics, output_path)

Generate Harris Matrix documentation report

##### generate_us_pdf(self, site_name, us_list, output_path)

Generate US (Stratigraphic Units) PDF report in PyArchInit original format

##### generate_inventario_pdf(self, site_name, inventario_list, output_path)

Generate Inventario (Finds) PDF report in PyArchInit original format (A5)

### PDFGenerator

Generate PDF reports for archaeological data

#### Methods

##### __init__(self)

Initializes the PDF report generator by loading the default stylesheet and configuring custom paragraph styles for the document. This method ensures that all subsequent PDF content adheres to the specified formatting standards required for archaeological data reports.

##### generate_site_report(self, site_data, us_list, inventory_list, media_list, output_path)

Generate comprehensive site report

Args:
    site_data: Site information
    us_list: List of stratigraphic units
    inventory_list: List of inventory items
    media_list: List of media files
    output_path: Optional output file path
    
Returns:
    PDF bytes

##### generate_harris_matrix_report(self, site_name, matrix_image_path, relationships, statistics, output_path)

Generate Harris Matrix documentation report

##### generate_us_pdf(self, site_name, us_list, output_path)

Generate US (Stratigraphic Units) PDF report in PyArchInit original format

##### generate_inventario_pdf(self, site_name, inventario_list, output_path)

Generate Inventario (Finds) PDF report using authentic PyArchInit template

## Functions

### safe_str(value)

Safely convert value to string

**Parameters:**
- `value`

### safe_str(value)

Safely convert value to string

**Parameters:**
- `value`

### safe_str(value)

Safely convert value to string

**Parameters:**
- `value`

