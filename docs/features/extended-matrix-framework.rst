Extended Matrix Framework - Complete Guide
===========================================

:Date: 2025-10-28
:Version: 1.7.0+
:Status: ✅ Production-Ready System

.. contents:: Table of Contents
   :local:
   :depth: 3

Introduction
------------

The **Extended Matrix Framework** (EMF) is an advanced archaeological documentation system that extends the traditional Harris Matrix with new unit types and specialized relationships.

PyArchInit-Mini fully implements the Extended Matrix Framework, allowing you to:

- Document different types of stratigraphic and non-stratigraphic units
- Manage complex relationships between units
- Link multimedia documents to units
- Export complex matrices in GraphML format for yEd
- Create custom archaeological data workflows

Overview
~~~~~~~~

The EMF provides **14 specialized unit types** organized in categories:

**Stratigraphic Units**:
  US, USM, VSF, SF

**Destructive Units**:
  USD, CON

**Virtual Groups**:
  USVA, USVB, USVC

**Non-Stratigraphic**:
  TU, property

**Documentary**:
  DOC (with file upload)

**Process**:
  Extractor, Combiner

Unit Types
----------

Standard Stratigraphic Units
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

US - Stratigraphic Unit
^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Traditional stratigraphic unit

**Relationship symbol**: ``>`` (above) / ``<`` (below)

**Use cases**:
  - Deposits
  - Layers
  - Natural strata

**Example**: US 1001 - Fill layer

**Python API Example**:

.. code-block:: python

   from pyarchinit_mini.services.us_service import USService
   from pyarchinit_mini.database.manager import DatabaseManager

   db = DatabaseManager('sqlite:///pyarchinit_mini.db')
   us_service = USService(db)

   # Create a standard US unit
   us_data = {
       'sito': 'Pompeii',
       'area': 'Area A',
       'us': 1001,
       'unita_tipo': 'US',  # Standard stratigraphic unit
       'd_stratigrafica': 'Fill layer with ceramic fragments',
       'd_interpretativa': 'Burial fill from medieval period',
       'tipo_us': 'deposit',
       'formazione': 'natural',
       'stato_di_conservazione': 'good'
   }

   result = us_service.create(us_data)
   print(f"Created US: {result['us']}")

USM - Masonry Stratigraphic Unit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Masonry stratigraphic unit

**Relationship symbol**: ``>`` / ``<``

**Use cases**:
  - Walls
  - Building structures
  - Architectural features

**Example**: USM 2001 - Brick wall

**Python API Example**:

.. code-block:: python

   # Create a masonry unit
   usm_data = {
       'sito': 'Pompeii',
       'area': 'Area A',
       'us': 2001,
       'unita_tipo': 'USM',  # Masonry unit
       'd_stratigrafica': 'Wall in opus reticulatum',
       'd_interpretativa': 'Perimeter wall of residential building',
       'tipo_us': 'structure',
       'formazione': 'anthropic'
   }

   result = us_service.create(usm_data)

Specialized Stratigraphic Units
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

VSF - Virtual Stratigraphic Face
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Virtual stratigraphic interface

**Relationship symbol**: ``>`` / ``<``

**Use cases**:
  - Interface surfaces
  - Walking surfaces
  - Floor levels

**Example**: VSF 3001 - Floor surface phase II

SF - Stratigraphic Face
^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Physical stratigraphic interface

**Relationship symbol**: ``>`` / ``<``

**Use cases**:
  - Cut surfaces
  - Discontinuities
  - Physical interfaces

**Example**: SF 3002 - Trench cut surface

Destructive Stratigraphic Units
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

USD - Destructive Stratigraphic Unit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Negative/destructive action

**Relationship symbol**: ``>`` / ``<``

**Use cases**:
  - Cuts
  - Removals
  - Destructions

**Example**: USD 4001 - Foundation trench cut

**Python API Example**:

.. code-block:: python

   # Create a destructive unit (cut)
   usd_data = {
       'sito': 'Pompeii',
       'area': 'Area A',
       'us': 4001,
       'unita_tipo': 'USD',  # Destructive unit
       'd_stratigrafica': 'Foundation trench cut',
       'd_interpretativa': 'Cut for wall USM 2001 foundation',
       'tipo_us': 'cut'
   }

   result = us_service.create(usd_data)

   # Create relationship: USD cuts earlier deposit
   relationship_data = {
       'sito': 'Pompeii',
       'area': 'Area A',
       'us': 4001,
       'rapporti': 'Taglia',  # Cuts
       'nazione': '',
       'us_rapporti': 1002
   }

   us_service.add_relationship(relationship_data)

CON - Connector
^^^^^^^^^^^^^^^

**Description**: Connector between units

**Relationship symbol**: ``>`` / ``<``

**Use cases**:
  - Physical connections between structures
  - Joint units
  - Binding elements

**Example**: CON 5001 - Connection between USM 2001 and USM 2002

Virtual Stratigraphic Units (Groups)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

USVA - Virtual Stratigraphic Unit A
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Virtual group type A (blue)

**Relationship symbol**: ``>`` / ``<``

**Use cases**:
  - Functional/chronological grouping
  - Phase grouping
  - Thematic collections

**Example**: USVA 6001 - Archaic phase group

**Python API Example**:

.. code-block:: python

   # Create a virtual group for a chronological phase
   usva_data = {
       'sito': 'Pompeii',
       'area': 'Area A',
       'us': 6001,
       'unita_tipo': 'USVA',  # Virtual group A
       'd_stratigrafica': 'Archaic phase group',
       'd_interpretativa': 'All units from archaic settlement phase',
       'periodo_iniziale': 'Archaic',
       'fase_iniziale': 'Early Archaic',
       'periodo_finale': 'Classical',
       'fase_finale': 'Late Archaic'
   }

   result = us_service.create(usva_data)

   # Add multiple US to this virtual group via relationships
   for us_num in [1001, 1002, 1003, 1004]:
       rel = {
           'sito': 'Pompeii',
           'area': 'Area A',
           'us': 6001,
           'rapporti': 'Ingloba',  # Encompasses
           'nazione': '',
           'us_rapporti': us_num
       }
       us_service.add_relationship(rel)

USVB - Virtual Stratigraphic Unit B
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Virtual group type B (green)

**Relationship symbol**: ``>`` / ``<``

**Use cases**:
  - Thematic grouping
  - Functional areas
  - Activity zones

**Example**: USVB 6002 - Production structures group

USVC - Virtual Stratigraphic Unit C
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Virtual group type C

**Relationship symbol**: ``>`` / ``<``

**Use cases**:
  - Other logical groupings
  - Custom classifications
  - Special categories

**Example**: USVC 6003 - Abandonment layers group

Non-Stratigraphic Units
~~~~~~~~~~~~~~~~~~~~~~~

TU - Typological Unit
^^^^^^^^^^^^^^^^^^^^^

**Description**: Typological unit

**Relationship symbol**: ``>`` / ``<``

**Use cases**:
  - Typological classifications
  - Material categories
  - Artifact groups

**Example**: TU 7001 - Black-glazed pottery

property - Property
^^^^^^^^^^^^^^^^^^^

**Description**: Attribute or property

**Relationship symbol**: ``>>`` / ``<<``

**Use cases**:
  - Characteristics
  - Attributes
  - Metadata

**Example**: property "red_color"

DOC - Document
^^^^^^^^^^^^^^

**Description**: Documentary unit

**Relationship symbol**: ``>>`` / ``<<``

**Use cases**:
  - Links to documents
  - Photos
  - Files

**Special field**: ``tipo_documento`` (Image, PDF, DOCX, CSV, Excel, TXT)

**Example**: DOC 8001 - General excavation photo (type: Image)

Process Units
~~~~~~~~~~~~~

Extractor - Extractor
^^^^^^^^^^^^^^^^^^^^^

**Description**: Node that extracts information

**Relationship symbol**: ``>>`` / ``<<``

**Use cases**:
  - Analyses
  - Elaborations
  - Derivations

**Example**: Extractor "ceramic_analysis"

Combiner - Combiner
^^^^^^^^^^^^^^^^^^^

**Description**: Node that combines information

**Relationship symbol**: ``>>`` / ``<<``

**Use cases**:
  - Synthesis
  - Aggregations
  - Mergers

**Example**: Combiner "phase_II_synthesis"

Relationship Symbols
--------------------

Standard Relationships: ``>`` and ``<``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Stratigraphic units** use single symbols:

- ``>`` : indicates "above" or "more recent than"
- ``<`` : indicates "below" or "older than"

**Units using** ``>`` / ``<``:
  - US, USM
  - VSF, SF
  - CON, USD
  - USVA, USVB, USVC
  - TU

**Example**:

.. code-block:: text

   US 1001 > US 1002
   (US 1001 covers US 1002)

**Python API Example**:

.. code-block:: python

   from pyarchinit_mini.services.us_service import USService

   # Create stratigraphic relationship
   relationship = {
       'sito': 'Pompeii',
       'area': 'Area A',
       'us': 1001,
       'rapporti': 'Copre',  # Covers (> symbol)
       'nazione': '',
       'us_rapporti': 1002
   }

   us_service.add_relationship(relationship)

   # This creates: US 1001 > US 1002
   # (US 1001 is stratigraphically above US 1002)

Special Relationships: ``>>`` and ``<<``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Non-stratigraphic and process units** use double symbols:

- ``>>`` : indicates "is connected to" or "derives from"
- ``<<`` : indicates "receives from" or "is source for"

**Units using** ``>>`` / ``<<``:
  - DOC (Document)
  - property (Property)
  - Extractor (Extractor)
  - Combiner (Combiner)

**Example**:

.. code-block:: text

   DOC 8001 >> US 1001
   (Document DOC 8001 documents US 1001)

   Extractor "ceramic" >> US 1002
   (Extractor analyzes ceramics from US 1002)

Visualization Rules in yEd
~~~~~~~~~~~~~~~~~~~~~~~~~~

When exporting the matrix to GraphML format for yEd:

1. **Stratigraphic units** (``>``, ``<``)
   - Relationships visualized with standard arrows
   - Vertical layout: more recent → older
   - Colors differentiated by type

2. **Non-stratigraphic units** (``>>``, ``<<``)
   - Relationships visualized with double arrows
   - Transversal links to stratigraphy
   - Special highlighting for DOC

DOC Units and Documents
-----------------------

Special Functionality
~~~~~~~~~~~~~~~~~~~~~

**DOC** type units have unique features:

1. The **tipo_documento** field specifying file format
2. **File upload** with automatic saving to DoSC folder
3. The **file_path** field storing file location in database

tipo_documento Field
~~~~~~~~~~~~~~~~~~~~

When you select "DOC" as unit type, an additional field appears to specify document type:

**Available types**:

- **Image** - Image file (JPG, PNG, TIFF, etc.)
- **PDF** - PDF document
- **DOCX** - Word document
- **CSV** - CSV data file
- **Excel** - Excel spreadsheet
- **TXT** - Text file

File Upload
~~~~~~~~~~~

**DoSC Folder (Documents Storage Collection)**:

- All files automatically saved in ``DoSC/``
- Automatic naming: ``{SITE}_{US}_{TIMESTAMP}_{ORIGINAL_FILENAME}``
- Path stored in database in ``file_path`` field

**Naming example**:

.. code-block:: text

   Original file: excavation_photo_2024.jpg
   Saved file: DoSC/Pompeii_DOC-8001_20251028_142530_excavation_photo_2024.jpg
   Database file_path: "DoSC/Pompeii_DOC-8001_20251028_142530_excavation_photo_2024.jpg"

Python API for DOC Units
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.services.us_service import USService
   import shutil
   from pathlib import Path
   from datetime import datetime

   db = DatabaseManager('sqlite:///pyarchinit_mini.db')
   us_service = USService(db)

   def create_doc_unit(site: str, area: str, us: int, doc_type: str,
                       source_file: str, description: str) -> dict:
       """
       Create a DOC unit with file upload

       Args:
           site: Site name
           area: Area name
           us: DOC unit number
           doc_type: Type of document (Image, PDF, DOCX, CSV, Excel, TXT)
           source_file: Path to source file
           description: Description of the document

       Returns:
           dict: Created DOC unit data with file_path
       """
       # Create DoSC directory if it doesn't exist
       dosc_dir = Path('DoSC')
       dosc_dir.mkdir(exist_ok=True)

       # Generate unique filename
       timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
       source_path = Path(source_file)
       filename = f"{site}_DOC-{us}_{timestamp}_{source_path.name}"
       dest_path = dosc_dir / filename

       # Copy file to DoSC
       shutil.copy2(source_file, dest_path)

       # Create DOC unit in database
       doc_data = {
           'sito': site,
           'area': area,
           'us': us,
           'unita_tipo': 'DOC',
           'tipo_documento': doc_type,
           'd_stratigrafica': description,
           'file_path': str(dest_path)
       }

       result = us_service.create(doc_data)
       return result

   # Usage example
   doc = create_doc_unit(
       site='Pompeii',
       area='Area A',
       us=8001,
       doc_type='Image',
       source_file='/path/to/excavation_photo.jpg',
       description='General photo of excavation area A, medieval phase'
   )

   print(f"DOC unit created: DOC {doc['us']}")
   print(f"File saved: {doc['file_path']}")

   # Link DOC to stratigraphic units
   for us_num in [1001, 1002, 1003]:
       relationship = {
           'sito': 'Pompeii',
           'area': 'Area A',
           'us': 8001,  # DOC unit
           'rapporti': 'Documenta',  # Documents
           'nazione': '',
           'us_rapporti': us_num
       }
       us_service.add_relationship(relationship)

**Expected Output**:

.. code-block:: text

   DOC unit created: DOC 8001
   File saved: DoSC/Pompeii_DOC-8001_20251028_142530_excavation_photo.jpg

Complete Usage Examples
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Example 1: Photo documentation
   DOC 8001
     tipo_documento: Image
     file_path: DoSC/Pompeii_DOC-8001_20251028_142530_photo.jpg
     descrizione: General photo excavation area A, phase II
     linked to: US 1001, US 1002, US 1003

   # Example 2: PDF report
   DOC 8002
     tipo_documento: PDF
     file_path: DoSC/Pompeii_DOC-8002_20251028_143015_report.pdf
     descrizione: Preliminary excavation report 2024
     linked to: USVA 6001 (entire archaic phase group)

   # Example 3: Excel database
   DOC 8003
     tipo_documento: Excel
     file_path: DoSC/Pompeii_DOC-8003_20251028_150000_database.xlsx
     descrizione: Ceramic finds database
     linked to: TU 7001, TU 7002, TU 7003

Web Interface
~~~~~~~~~~~~~

1. Field "Unit Type" → select **"DOC"**
2. Two fields appear automatically:

   - **"Document Type"** - Dropdown menu to select type
   - **"Upload Document File"** - Field to upload file

3. Click "Choose File" → Select file from computer
4. Save → File automatically uploaded to DoSC

**Process**:

.. code-block:: text

   1. Select Unit Type: DOC
   2. Document Type appears → Choose "Image"
   3. Upload Document File appears → Click "Choose File"
   4. Browse and select: photo.jpg
   5. Save → File uploaded to DoSC/Pompeii_DOC-8001_20251028_142530_photo.jpg

Desktop GUI
~~~~~~~~~~~

1. Combobox "Unit Type" → select **"DOC"**
2. Two fields appear automatically:

   - **"Document Type"** - Combobox to select type
   - **"Document File"** - Entry with "Browse..." button

3. Click "Browse..." → File dialog to select file
4. Save → File automatically copied to DoSC

File Management
~~~~~~~~~~~~~~~

**Access files**:

.. code-block:: bash

   # All DOC files are in DoSC/
   ls -lh DoSC/

   # Files for specific site
   ls DoSC/ | grep "Pompeii"

   # Files by type
   ls DoSC/*.jpg    # Images
   ls DoSC/*.pdf    # PDFs
   ls DoSC/*.xlsx   # Excel

**Backup**:

.. code-block:: bash

   # Backup DoSC folder
   cp -r DoSC DoSC_backup_$(date +%Y%m%d)

   # Compressed backup
   tar -czf DoSC_backup_$(date +%Y%m%d).tar.gz DoSC/

.. seealso::

   :doc:`DOC_FILE_UPLOAD` - Complete documentation on DOC file upload

GraphML Export for yEd
----------------------

Functionality
~~~~~~~~~~~~~

PyArchInit-Mini supports complete Harris Matrix export in GraphML format optimized for **yEd**.

How to Export
~~~~~~~~~~~~~

Web Interface
^^^^^^^^^^^^^

1. Go to US list
2. Click "Export Harris Matrix to GraphML (yEd)"
3. Select site and area
4. Download .graphml file

Desktop GUI
^^^^^^^^^^^

1. Open "Export" menu
2. Select "Export Harris Matrix (GraphML)"
3. Choose site and area
4. Save .graphml file

Python API
^^^^^^^^^^

.. code-block:: python

   from pyarchinit_mini.graphml_converter.graphml_exporter import GraphMLExporter
   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator

   # Initialize services
   matrix_gen = MatrixGenerator('sqlite:///pyarchinit_mini.db')
   graphml_exporter = GraphMLExporter('sqlite:///pyarchinit_mini.db')

   # Generate Harris Matrix
   matrix_data = matrix_gen.generate_matrix(
       sito='Pompeii',
       area='Area A'
   )

   # Export to GraphML
   graphml_file = graphml_exporter.export_to_graphml(
       sito='Pompeii',
       area='Area A',
       output_path='harris_matrix_pompeii.graphml',
       include_periodization=True,
       reverse_epochs=False
   )

   print(f"GraphML exported to: {graphml_file}")

**Expected Output**:

.. code-block:: text

   Generating Harris Matrix for Pompeii - Area A...
   Found 45 stratigraphic units
   Created 123 relationships
   Applying periodization data...
   Exporting to GraphML format...
   GraphML exported to: harris_matrix_pompeii.graphml

Visualization in yEd
~~~~~~~~~~~~~~~~~~~~

1. **Open yEd** (download from: https://www.yworks.com/products/yed)

2. **Import GraphML file:**

   - File → Open → select the exported .graphml

3. **Apply automatic layout:**

   - Layout → Hierarchical
   - Orientation: Top to Bottom
   - Layer Assignment Policy: Hierarchical - Optimal

4. **Customize visualization:**

   - Use the included Extended Matrix palette
   - Pre-configured colors for each unit type
   - Relationship symbols (``>``, ``>>``) already set

Extended Matrix Palette
~~~~~~~~~~~~~~~~~~~~~~~~

The ``EM_palette.graphml`` file includes:

- **Pre-configured styles** for all unit types
- **Color codes:**

  - US/USM: white/gray with red border
  - VSF/SF: white/yellow with specific borders
  - USVA: black with blue border
  - USVB: black with green border
  - USD: white with orange border
  - DOC: special shape for documents
  - CON: small black connector
  - Extractor/Combiner: specialized SVG icons

Best Practices
--------------

1. Choosing Unit Type
~~~~~~~~~~~~~~~~~~~~~

**Use US/USM for:**

- Traditional archaeological deposits
- Masonry structures
- Natural and anthropogenic layers

**Use VSF/SF for:**

- Interfaces between deposits
- Walking surfaces
- Use levels

**Use USD for:**

- Foundation cuts
- Pits
- Intentional destructions

**Use USVA/USVB/USVC for:**

- Grouping US by chronological phase
- Creating functional groups
- Organizing by excavation area

**Use DOC for:**

- Linking photos to US
- Attaching reports
- Referencing external databases

**Use property for:**

- Adding metadata
- Specifying characteristics
- Technical annotations

**Use Extractor/Combiner for:**

- Analysis workflows
- Data processing pipelines
- Derivations and syntheses

2. Naming Conventions
~~~~~~~~~~~~~~~~~~~~~

**Suggested conventions**:

.. code-block:: text

   US:     sequential numbers (1001, 1002, 1003...)
   USM:    separate sequential numbers (2001, 2002, 2003...)
   VSF:    numbers with area prefix (A3001, B3001...)
   DOC:    sequential numbers per year (2024-001, 2024-002...)
   USVA:   numbers per phase (PHASE1-6001, PHASE2-6002...)

**Python API Example**:

.. code-block:: python

   def generate_us_number(site: str, us_type: str) -> int:
       """
       Generate sequential US number based on type

       Args:
           site: Site name
           us_type: Type of unit (US, USM, VSF, DOC, etc.)

       Returns:
           int: Next sequential number for this type
       """
       type_ranges = {
           'US': (1000, 1999),
           'USM': (2000, 2999),
           'VSF': (3000, 3999),
           'USD': (4000, 4999),
           'CON': (5000, 5999),
           'USVA': (6000, 6099),
           'USVB': (6100, 6199),
           'USVC': (6200, 6299),
           'TU': (7000, 7999),
           'DOC': (8000, 8999)
       }

       min_num, max_num = type_ranges.get(us_type, (1000, 9999))

       # Query database for highest existing number
       existing_numbers = us_service.search(
           sito=site,
           unita_tipo=us_type
       )

       if not existing_numbers:
           return min_num

       max_existing = max(us['us'] for us in existing_numbers)
       next_num = max_existing + 1

       if next_num > max_num:
           raise ValueError(f"No more numbers available for {us_type}")

       return next_num

   # Usage
   next_us = generate_us_number('Pompeii', 'US')
   next_usm = generate_us_number('Pompeii', 'USM')
   next_doc = generate_us_number('Pompeii', 'DOC')

3. Documenting Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Always record:**

- Type of physical relationship (covers, cuts, fills, etc.)
- Relationship certainty
- Stratigraphic notes

**Example**:

.. code-block:: python

   relationship = {
       'sito': 'Pompeii',
       'area': 'Area A',
       'us': 1001,
       'rapporti': 'Copre',  # Covers
       'nazione': '',
       'us_rapporti': 1002,
       'note_rapporti': 'Sharp horizontal contact, certain relationship. Documented by DOC 8001'
   }

   us_service.add_relationship(relationship)

4. Using Documents
~~~~~~~~~~~~~~~~~~

**Organize DOC by category**:

.. code-block:: text

   DOC 8001-8099: General photos
   DOC 8100-8199: Detail photos
   DOC 8200-8299: Drawings
   DOC 8300-8399: Reports
   DOC 8400-8499: Databases

**Always link DOC to appropriate units**:

- General photo → link to USVA group
- Detail photo → link to individual US
- Report → link to all relevant US

**Python API Example**:

.. code-block:: python

   def link_doc_to_units(doc_us: int, target_units: list,
                         site: str, area: str) -> None:
       """
       Link a DOC unit to multiple target units

       Args:
           doc_us: DOC unit number
           target_units: List of target US numbers
           site: Site name
           area: Area name
       """
       for target_us in target_units:
           relationship = {
               'sito': site,
               'area': area,
               'us': doc_us,
               'rapporti': 'Documenta',
               'nazione': '',
               'us_rapporti': target_us
           }
           us_service.add_relationship(relationship)

       print(f"DOC {doc_us} linked to {len(target_units)} units")

   # Usage: Link general photo to entire phase group
   link_doc_to_units(
       doc_us=8001,
       target_units=[1001, 1002, 1003, 1004, 1005],
       site='Pompeii',
       area='Area A'
   )

5. Recommended Workflow
~~~~~~~~~~~~~~~~~~~~~~~

**1. Excavation phase:**

- Create US, USM, USD during excavation
- Record stratigraphic relationships
- Create DOC for every photo taken

**Python Example**:

.. code-block:: python

   # During excavation: Quick US entry
   def record_excavation_unit(site: str, area: str, us_type: str,
                             description: str, photo_path: str = None) -> dict:
       """Quick entry of excavation data"""

       # Generate US number
       us_num = generate_us_number(site, us_type)

       # Create US
       us_data = {
           'sito': site,
           'area': area,
           'us': us_num,
           'unita_tipo': us_type,
           'd_stratigrafica': description
       }
       us = us_service.create(us_data)

       # Create DOC if photo provided
       if photo_path:
           doc_num = generate_us_number(site, 'DOC')
           doc = create_doc_unit(
               site=site,
               area=area,
               us=doc_num,
               doc_type='Image',
               source_file=photo_path,
               description=f"Photo of {us_type} {us_num}"
           )
           link_doc_to_units(doc_num, [us_num], site, area)

       return us

**2. Post-processing phase:**

- Create VSF/SF for interfaces
- Create USVA/USVB groups for phases
- Add TU for classifications

**3. Analysis phase:**

- Use Extractor for specialized analyses
- Use Combiner for syntheses
- Add property for metadata

**4. Publication phase:**

- Export complete matrix to GraphML
- Generate visualizations in yEd
- Create reports with DOC links

Practical Examples
------------------

Example 1: Urban Stratigraphic Excavation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   USVA 6001 - Medieval Phase
     ├─ US 1001 - Pit fill
     ├─ USD 4001 - Pit cut
     └─ DOC 8001 (Image) - General photo medieval phase

   USVA 6002 - Roman Phase
     ├─ US 1002 - Collapse layer
     ├─ USM 2001 - Wall in opus reticulatum
     ├─ SF 3001 - Floor surface
     └─ DOC 8002 (PDF) - Roman phase report

   Relationships:
     US 1001 > USD 4001 > US 1002
     USM 2001 = SF 3001 (contemporary)
     DOC 8001 >> USVA 6001
     DOC 8002 >> USVA 6002

**Python Implementation**:

.. code-block:: python

   def create_urban_excavation_example():
       """Complete example of urban excavation documentation"""

       site = 'Urban Site'
       area = 'Trench 1'

       # Create Medieval phase group
       medieval_group = us_service.create({
           'sito': site, 'area': area, 'us': 6001,
           'unita_tipo': 'USVA',
           'd_stratigrafica': 'Medieval Phase',
           'periodo_iniziale': 'Medieval',
           'periodo_finale': 'Medieval'
       })

       # Create medieval units
       pit_fill = us_service.create({
           'sito': site, 'area': area, 'us': 1001,
           'unita_tipo': 'US',
           'd_stratigrafica': 'Pit fill with pottery'
       })

       pit_cut = us_service.create({
           'sito': site, 'area': area, 'us': 4001,
           'unita_tipo': 'USD',
           'd_stratigrafica': 'Pit cut'
       })

       # Create Roman phase group
       roman_group = us_service.create({
           'sito': site, 'area': area, 'us': 6002,
           'unita_tipo': 'USVA',
           'd_stratigrafica': 'Roman Phase'
       })

       # Create Roman units
       collapse = us_service.create({
           'sito': site, 'area': area, 'us': 1002,
           'unita_tipo': 'US',
           'd_stratigrafica': 'Building collapse layer'
       })

       wall = us_service.create({
           'sito': site, 'area': area, 'us': 2001,
           'unita_tipo': 'USM',
           'd_stratigrafica': 'Wall in opus reticulatum'
       })

       floor = us_service.create({
           'sito': site, 'area': area, 'us': 3001,
           'unita_tipo': 'SF',
           'd_stratigrafica': 'Floor surface'
       })

       # Create relationships
       relationships = [
           (1001, 'Riempie', 4001),  # Fill fills cut
           (4001, 'Taglia', 1002),   # Cut cuts collapse
           (2001, 'Si lega a', 3001),  # Wall bonds with floor
       ]

       for us, rap, us_rap in relationships:
           us_service.add_relationship({
               'sito': site, 'area': area,
               'us': us, 'rapporti': rap,
               'nazione': '', 'us_rapporti': us_rap
           })

       # Create documentation
       medieval_photo = create_doc_unit(
           site, area, 8001, 'Image',
           '/photos/medieval_phase.jpg',
           'General photo medieval phase'
       )
       link_doc_to_units(8001, [6001], site, area)

       return {
           'medieval_group': medieval_group,
           'roman_group': roman_group,
           'units_created': 6,
           'relationships': len(relationships)
       }

Example 2: Structure with Complex Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   USM 2001 - Perimeter wall
     ├─ property "construction_technique" = "opus incertum"
     ├─ property "chronology" = "2nd century BC"
     ├─ DOC 8010 (Image) - North elevation photo
     ├─ DOC 8011 (Image) - South elevation photo
     ├─ DOC 8012 (DOCX) - Detailed USM sheet
     └─ DOC 8013 (Excel) - Photogrammetric survey

   Connections:
     CON 5001 - Connection between USM 2001 and USM 2002

   Relationships:
     property >> USM 2001
     DOC 8010 >> USM 2001
     DOC 8011 >> USM 2001
     DOC 8012 >> USM 2001
     DOC 8013 >> USM 2001
     CON 5001 > USM 2001
     CON 5001 > USM 2002

Example 3: Analysis and Derivations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   US 1003 - Fill layer with ceramics

     ↓ material analysis

   Extractor "ceramic_analysis" >> US 1003

     ↓ data extraction

   TU 7001 - Black-glazed pottery
   TU 7002 - Common pottery
   TU 7003 - Amphorae

     ↓ synthesis

   Combiner "synthesis_finds_US1003"

     ↓ output

   DOC 8020 (Excel) - US 1003 ceramic database
   DOC 8021 (PDF) - Ceramological report

   Complete relationships:
     Extractor >> US 1003
     Extractor >> TU 7001
     Extractor >> TU 7002
     Extractor >> TU 7003
     Combiner << TU 7001
     Combiner << TU 7002
     Combiner << TU 7003
     DOC 8020 >> Combiner
     DOC 8021 >> Combiner

**Python Implementation**:

.. code-block:: python

   def create_analysis_workflow(site: str, area: str, us_num: int):
       """
       Create complete analysis workflow for ceramic finds

       This example shows how to use Extractor and Combiner units
       to document the analysis process
       """

       # Create extractor node
       extractor = us_service.create({
           'sito': site, 'area': area, 'us': 9001,
           'unita_tipo': 'Extractor',
           'd_stratigrafica': 'Ceramic analysis process',
           'd_interpretativa': 'Extraction and classification of ceramic materials'
       })

       # Link extractor to source US
       us_service.add_relationship({
           'sito': site, 'area': area,
           'us': 9001, 'rapporti': 'Deriva da',
           'nazione': '', 'us_rapporti': us_num
       })

       # Create typological units for different ceramic types
       ceramic_types = [
           (7001, 'Black-glazed pottery'),
           (7002, 'Common pottery'),
           (7003, 'Amphorae')
       ]

       for tu_num, description in ceramic_types:
           tu = us_service.create({
               'sito': site, 'area': area, 'us': tu_num,
               'unita_tipo': 'TU',
               'd_stratigrafica': description
           })

           # Link extractor to each TU
           us_service.add_relationship({
               'sito': site, 'area': area,
               'us': 9001, 'rapporti': 'Produce',
               'nazione': '', 'us_rapporti': tu_num
           })

       # Create combiner for synthesis
       combiner = us_service.create({
           'sito': site, 'area': area, 'us': 9002,
           'unita_tipo': 'Combiner',
           'd_stratigrafica': f'Synthesis of finds from US {us_num}'
       })

       # Link all TUs to combiner
       for tu_num, _ in ceramic_types:
           us_service.add_relationship({
               'sito': site, 'area': area,
               'us': tu_num, 'rapporti': 'Confluisce in',
               'nazione': '', 'us_rapporti': 9002
           })

       # Create output documents
       database_doc = create_doc_unit(
           site, area, 8020, 'Excel',
           f'/data/ceramic_database_US{us_num}.xlsx',
           f'Ceramic database for US {us_num}'
       )

       report_doc = create_doc_unit(
           site, area, 8021, 'PDF',
           f'/reports/ceramic_report_US{us_num}.pdf',
           f'Ceramological report for US {us_num}'
       )

       # Link documents to combiner
       link_doc_to_units(8020, [9002], site, area)
       link_doc_to_units(8021, [9002], site, area)

       return {
           'extractor': extractor,
           'combiner': combiner,
           'typological_units': len(ceramic_types),
           'documents': 2
       }

   # Usage
   workflow = create_analysis_workflow('Pompeii', 'Area A', 1003)
   print(f"Created analysis workflow with {workflow['typological_units']} TU units")

Integration in External Projects
---------------------------------

Using EMF in Custom Applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Extended Matrix Framework can be integrated into custom archaeological data management systems:

.. code-block:: python

   """
   Custom archaeological data pipeline using EMF

   This example shows how to integrate PyArchInit-Mini's EMF
   into a larger data processing system
   """

   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.services.us_service import USService
   from pyarchinit_mini.graphml_converter.graphml_exporter import GraphMLExporter
   import json

   class ArchaeologicalDataPipeline:
       """
       Custom pipeline for archaeological data processing
       using Extended Matrix Framework
       """

       def __init__(self, db_path: str):
           self.db = DatabaseManager(f'sqlite:///{db_path}')
           self.us_service = USService(self.db)
           self.graphml_exporter = GraphMLExporter(f'sqlite:///{db_path}')

       def import_field_data(self, field_data_json: str) -> dict:
           """
           Import field data from JSON format

           Args:
               field_data_json: Path to JSON file with field data

           Returns:
               dict: Import statistics
           """
           with open(field_data_json, 'r') as f:
               data = json.load(f)

           stats = {
               'units_created': 0,
               'relationships_created': 0,
               'documents_linked': 0
           }

           # Process stratigraphic units
           for unit in data.get('stratigraphic_units', []):
               us_data = {
                   'sito': unit['site'],
                   'area': unit['area'],
                   'us': unit['number'],
                   'unita_tipo': unit['type'],
                   'd_stratigrafica': unit['description']
               }
               self.us_service.create(us_data)
               stats['units_created'] += 1

           # Process relationships
           for rel in data.get('relationships', []):
               rel_data = {
                   'sito': rel['site'],
                   'area': rel['area'],
                   'us': rel['from_us'],
                   'rapporti': rel['relationship_type'],
                   'nazione': '',
                   'us_rapporti': rel['to_us']
               }
               self.us_service.add_relationship(rel_data)
               stats['relationships_created'] += 1

           return stats

       def export_to_multiple_formats(self, site: str, area: str,
                                     output_dir: str) -> dict:
           """
           Export Harris Matrix to multiple formats

           Args:
               site: Site name
               area: Area name
               output_dir: Output directory path

           Returns:
               dict: Paths to generated files
           """
           from pathlib import Path

           output_path = Path(output_dir)
           output_path.mkdir(parents=True, exist_ok=True)

           files = {}

           # Export GraphML
           graphml_path = output_path / f'{site}_{area}_matrix.graphml'
           self.graphml_exporter.export_to_graphml(
               sito=site,
               area=area,
               output_path=str(graphml_path)
           )
           files['graphml'] = str(graphml_path)

           # Export DOT
           dot_path = output_path / f'{site}_{area}_matrix.dot'
           self.graphml_exporter.export_to_dot(
               sito=site,
               area=area,
               output_path=str(dot_path)
           )
           files['dot'] = str(dot_path)

           return files

   # Usage example
   pipeline = ArchaeologicalDataPipeline('my_project.db')

   # Import field data
   stats = pipeline.import_field_data('field_data.json')
   print(f"Imported {stats['units_created']} units")

   # Export to multiple formats
   files = pipeline.export_to_multiple_formats(
       'Pompeii', 'Area A', 'exports/'
   )
   print(f"Exported to: {files}")

Conclusions
-----------

The Extended Matrix Framework implemented in PyArchInit-Mini offers:

✅ **Flexibility** - Unit types for every documentation need
✅ **Power** - Complex relationships between stratigraphic and non-stratigraphic units
✅ **Integration** - Direct links to multimedia documents
✅ **Compatibility** - Complete export for yEd and other software
✅ **Scalability** - From single excavation to large multi-site project
✅ **Programmability** - Full Python API for custom workflows

API Reference
-------------

Core Methods
~~~~~~~~~~~~

.. code-block:: python

   # Create stratigraphic unit
   us_service.create(us_data: dict) -> dict

   # Add relationship between units
   us_service.add_relationship(relationship_data: dict) -> dict

   # Search units by criteria
   us_service.search(sito: str, unita_tipo: str = None, **kwargs) -> list

   # Export to GraphML
   graphml_exporter.export_to_graphml(
       sito: str,
       area: str,
       output_path: str,
       include_periodization: bool = True
   ) -> str

See Also
--------

- :doc:`EXTENDED_MATRIX_EXPORT` - GraphML export technical details
- :doc:`DOC_FILE_UPLOAD` - Complete DOC file upload documentation
- :doc:`harris_matrix` - Harris Matrix generation and visualization
- :doc:`../python-api/overview` - Python API overview
- :doc:`../examples/python_api` - More Python examples

**The Extended Matrix Framework is production-ready and fully documented!** 🚀

**Document version**: 2.0
**Date**: 2025-10-28
**Author**: PyArchInit Team
