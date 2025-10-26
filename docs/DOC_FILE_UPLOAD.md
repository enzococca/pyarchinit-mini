# DOC Units - File Upload Guide

## Overview

PyArchInit-Mini v1.2.16+ includes complete file upload functionality for DOC (Document) units. When creating or editing a DOC unit, you can upload any type of file, and it will be automatically saved in the **DoSC** (Documents Storage Collection) folder.

---

## Features

✅ **File Upload for DOC Units** - Upload files directly when creating/editing DOC units
✅ **DoSC Folder** - All files automatically saved in centralized DoSC directory
✅ **Automatic Naming** - Files renamed with Site_US_timestamp_originalname pattern
✅ **Database Tracking** - File paths stored in database for retrieval
✅ **Multiple Formats** - Support for Images, PDF, DOCX, CSV, Excel, TXT, and more
✅ **Both Interfaces** - Available in Web Interface and Desktop GUI
✅ **Bilingual** - Full Italian and English translations

---

## Web Interface Usage

### Creating a New DOC Unit with File

1. **Navigate to US List**
   - Go to: Menu → US → List

2. **Create New US**
   - Click "New US" button

3. **Select Unit Type**
   - In "Unit Type" dropdown, select **"DOC"**
   - Two new fields will appear:
     - **Document Type**: Select file type (Image, PDF, DOCX, CSV, Excel, TXT)
     - **Upload Document File**: File upload field

4. **Select Document Type**
   - Choose appropriate type from dropdown
   - Example: Select "Image" for photos, "PDF" for reports

5. **Upload File**
   - Click "Choose File" button
   - Browse and select your file
   - File name will appear next to button

6. **Fill Other Fields**
   - Site: **Required**
   - US Number: **Required**
   - Other fields optional

7. **Save**
   - Click "Save US"
   - File is uploaded to `DoSC/` folder
   - Path saved in database
   - Success message displayed

### Example

```
Site: Pompei
Area: Regio VI
US: DOC-8001
Unit Type: DOC
Document Type: Image
File: excavation_photo_001.jpg → uploaded

Result:
File saved as: DoSC/Pompei_DOC-8001_20251023_142530_excavation_photo_001.jpg
Database field file_path: "DoSC/Pompei_DOC-8001_20251023_142530_excavation_photo_001.jpg"
```

### Editing Existing DOC Unit

1. Go to US List
2. Click "Edit" on DOC unit
3. Document Type and Upload fields appear (if DOC type)
4. Upload new file (optional - replaces old file)
5. Save changes

---

## Desktop GUI Usage

### Creating a New DOC Unit with File

1. **Open US Dialog**
   - Menu → US → New US
   - Or click "New US" button

2. **Select Site and US Number**
   - Select site from dropdown
   - Enter US number

3. **Select Unit Type**
   - In "Unit Type" combobox, select **"DOC"**
   - Two new fields will appear below:
     - **Document Type**: Combobox with file types
     - **Document File**: Entry with "Browse..." button

4. **Select Document Type**
   - Choose from: Image, PDF, DOCX, CSV, Excel, TXT

5. **Browse for File**
   - Click **"Browse..."** button
   - File dialog opens with filters by type
   - Select your file
   - Filename appears in readonly entry field

6. **Complete Other Fields**
   - Fill in remaining US information
   - All standard US fields available

7. **Save**
   - Click "Save" button
   - File copied to `DoSC/` folder
   - Path saved in database
   - "US created successfully" message

### Example

```
Site: Pompei
US Number: DOC-8002
Unit Type: DOC
Document Type: PDF
File: [Browse...] → selected "excavation_report_2024.pdf"

Result:
File copied to: DoSC/Pompei_DOC-8002_20251023_143015_excavation_report_2024.pdf
Database stores: "DoSC/Pompei_DOC-8002_20251023_143015_excavation_report_2024.pdf"
```

### File Selection Dialog

The Browse dialog includes file type filters:

- **All Files** (*.\*)
- **Images** (*.jpg, *.jpeg, *.png, *.tiff, *.gif)
- **PDF** (*.pdf)
- **Word Documents** (*.docx, *.doc)
- **Excel Files** (*.xlsx, *.xls)
- **CSV Files** (*.csv)
- **Text Files** (*.txt)

---

## DoSC Folder Structure

### Location

```
<project_root>/
  ├── DoSC/                           # Documents Storage Collection
  │   ├── Pompei_DOC-8001_20251023_142530_photo001.jpg
  │   ├── Pompei_DOC-8002_20251023_143015_report.pdf
  │   ├── Herculaneum_DOC-9001_20251023_150000_data.xlsx
  │   └── ...
  ├── pyarchinit_mini.db
  ├── web_interface/
  └── desktop_gui/
```

### Filename Pattern

```
{SITE}_{US}_{TIMESTAMP}_{ORIGINAL_FILENAME}
```

**Components:**
- `SITE`: Site name (e.g., "Pompei")
- `US`: US number (e.g., "DOC-8001")
- `TIMESTAMP`: Upload time in format `YYYYMMDD_HHMMSS`
- `ORIGINAL_FILENAME`: Original filename (spaces replaced with underscores)

**Examples:**
```
Pompei_DOC-8001_20251023_142530_excavation_photo_001.jpg
Pompei_DOC-8002_20251023_143015_excavation_report_2024.pdf
Ostia_DOC-7050_20251023_160000_ceramic_analysis.xlsx
```

### Benefits of This Pattern

✅ **Unique Names**: Timestamp ensures no collisions
✅ **Traceability**: Site and US clearly identified
✅ **Sortable**: Chronological ordering by timestamp
✅ **Original Preserved**: Original filename kept for reference
✅ **Cross-Platform**: No special characters or spaces

---

## Database Schema

### New Field: `file_path`

**Table**: `us_table`
**Column**: `file_path`
**Type**: VARCHAR(500)
**Purpose**: Store relative path to uploaded file

**Example Values:**
```sql
-- DOC unit with image
file_path = "DoSC/Pompei_DOC-8001_20251023_142530_photo.jpg"

-- DOC unit with PDF
file_path = "DoSC/Pompei_DOC-8002_20251023_143015_report.pdf"

-- Non-DOC unit
file_path = NULL
```

### Migration

New installations include the `file_path` field automatically.

Existing installations need migration:

```bash
# Backup database first
cp pyarchinit_mini.db pyarchinit_mini.db.backup

# Run migration
python run_file_path_migration.py upgrade

# Verify
sqlite3 pyarchinit_mini.db "PRAGMA table_info(us_table)" | grep file_path
# Expected: 69|file_path|VARCHAR(500)|0||0

# Rollback if needed
python run_file_path_migration.py downgrade
```

---

## File Type Mapping

### tipo_documento Values

| Database Value | Display Name (IT) | Display Name (EN) | Typical Extensions |
|----------------|-------------------|-------------------|-------------------|
| `image` | Immagine | Image | .jpg, .png, .tiff, .gif |
| `PDF` | PDF | PDF | .pdf |
| `DOCX` | DOCX | DOCX | .docx, .doc |
| `CSV` | CSV | CSV | .csv |
| `Excel` | Excel | Excel | .xlsx, .xls |
| `TXT` | TXT | TXT | .txt |

### Usage Guidelines

**Image**:
- Excavation photos
- Site documentation
- Artifact images
- Drawings scanned as images

**PDF**:
- Reports
- Publications
- Technical documents
- Scanned documents

**DOCX**:
- Editable reports
- Field notes
- Descriptions
- Templates

**CSV**:
- Data exports
- Tabular data
- Measurements
- Coordinates

**Excel**:
- Spreadsheets
- Databases
- Calculations
- Complex data

**TXT**:
- Plain text notes
- Logs
- Simple data files
- Configuration files

---

## Best Practices

### 1. Consistent Naming

**Before Upload:**
Use descriptive original filenames:

✅ Good:
- `excavation_area_A_general_view_2024.jpg`
- `ceramic_analysis_phase_II.xlsx`
- `conservation_report_USM_2001.pdf`

❌ Bad:
- `IMG_1234.jpg`
- `Document1.docx`
- `untitled.pdf`

### 2. Document Type Selection

**Match tipo_documento to actual file:**

✅ Correct:
- `photo.jpg` → tipo_documento: `image`
- `report.pdf` → tipo_documento: `PDF`
- `data.xlsx` → tipo_documento: `Excel`

❌ Incorrect:
- `photo.jpg` → tipo_documento: `PDF`
- `spreadsheet.xlsx` → tipo_documento: `TXT`

### 3. Organization

**Use US numbering scheme for DOC units:**

```
DOC-8000 to DOC-8999: Photos
DOC-9000 to DOC-9999: Reports
DOC-10000 to DOC-10999: Data files
```

**Example:**
```
DOC-8001: General excavation photo
DOC-8002: Detail of structure A
DOC-9001: Preliminary excavation report 2024
DOC-9002: Ceramic analysis report
DOC-10001: Artifact coordinates (CSV)
DOC-10002: Measurements database (Excel)
```

### 4. File Size Considerations

**Recommended limits:**
- Images: < 10 MB (compress large photos)
- PDFs: < 20 MB (compress scanned documents)
- Excel/CSV: < 5 MB (split large datasets)
- Word: < 10 MB

**For larger files:**
- Use external storage (cloud, NAS)
- Store reference/link in `documentazione` field
- Use DOC unit without file upload
- Add path/URL in description

### 5. Backup Strategy

**The DoSC folder contains all uploaded files - backup regularly!**

```bash
# Daily backup
cp -r DoSC DoSC_backup_$(date +%Y%m%d)

# Weekly compressed backup
tar -czf DoSC_backup_$(date +%Y%m%d).tar.gz DoSC/

# Sync to remote storage
rsync -av DoSC/ remote_server:/backups/pyarchinit/DoSC/
```

---

## Accessing Uploaded Files

### From Database

```python
from pyarchinit_mini.services.us_service import USService

# Get DOC unit
us_service = USService(db_manager)
doc_unit = us_service.get_us_by_id(123)

# Check if file exists
if doc_unit.file_path:
    print(f"File: {doc_unit.file_path}")
    # Output: DoSC/Pompei_DOC-8001_20251023_142530_photo.jpg

    # Full path
    import os
    full_path = os.path.join(os.getcwd(), doc_unit.file_path)

    # Verify existence
    if os.path.exists(full_path):
        print(f"File exists: {full_path}")
    else:
        print(f"File not found: {full_path}")
```

### From Filesystem

```bash
# List all uploaded files
ls -lh DoSC/

# Find files for specific site
ls DoSC/ | grep "Pompei"

# Find files by type
ls DoSC/*.jpg     # All images
ls DoSC/*.pdf     # All PDFs
ls DoSC/*.xlsx    # All Excel files

# Search by date
ls DoSC/*20251023*   # All files from October 23, 2025
```

### Opening Files

**Direct access:**
```bash
# View image
open DoSC/Pompei_DOC-8001_20251023_142530_photo.jpg

# Open PDF
xdg-open DoSC/Pompei_DOC-8002_20251023_143015_report.pdf

# Open in Excel
libreoffice DoSC/Ostia_DOC-10001_20251023_150000_data.xlsx
```

---

## Troubleshooting

### File Not Uploading (Web Interface)

**Problem**: File not appearing in DoSC folder after save

**Solutions**:
1. Check file size (may exceed server limits)
2. Verify DoSC folder exists and is writable
3. Check browser console for errors
4. Ensure Unit Type is "DOC"
5. Check Flask logs for permission errors

**Debug:**
```bash
# Check DoSC folder
ls -la | grep DoSC
# Should show: drwxr-xr-x ... DoSC

# Check permissions
ls -ld DoSC/
# Should be writable

# Check Flask logs
tail -f logs/pyarchinit_web.log
```

### File Not Uploading (Desktop GUI)

**Problem**: "File not saved" or error message

**Solutions**:
1. Verify file exists at selected path
2. Check DoSC folder permissions
3. Ensure sufficient disk space
4. Check if file is open in another application
5. Try file with simple name (no special chars)

**Debug:**
```python
import os
import shutil

# Test file copy
source = "/path/to/test.jpg"
dest = "DoSC/test_copy.jpg"

try:
    shutil.copy2(source, dest)
    print("Copy successful")
except Exception as e:
    print(f"Error: {e}")
```

### File Path Not in Database

**Problem**: File uploaded but `file_path` field is NULL

**Solutions**:
1. Ensure migration was run: `python run_file_path_migration.py upgrade`
2. Verify `file_path` column exists in database
3. Check application logs for database errors
4. Restart application after migration

**Verify:**
```bash
sqlite3 pyarchinit_mini.db "PRAGMA table_info(us_table)" | grep file_path
# Expected output: 69|file_path|VARCHAR(500)|0||0
```

### DoSC Folder Not Created

**Problem**: Upload fails - "DoSC folder not found"

**Solutions**:
1. Manually create: `mkdir DoSC`
2. Check working directory: `pwd`
3. Verify write permissions
4. Restart application

**Manual creation:**
```bash
# In project root
mkdir -p DoSC
chmod 755 DoSC
```

---

## API Examples

### Python API - Creating DOC Unit with File

```python
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.database.connection import DatabaseConnection
import shutil
import os
from datetime import datetime

# Initialize
db = DatabaseConnection("sqlite:///./pyarchinit_mini.db")
us_service = USService(db)

# Prepare DOC unit data
doc_data = {
    'sito': 'Pompei',
    'us': 'DOC-8001',
    'unita_tipo': 'DOC',
    'tipo_documento': 'Image',
    'd_interpretativa': 'General excavation photo - Area A, Phase II'
}

# Handle file upload
source_file = "/path/to/original/photo.jpg"
if os.path.exists(source_file):
    # Create DoSC folder
    os.makedirs('DoSC', exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    original_name = os.path.basename(source_file).replace(' ', '_')
    filename = f"{doc_data['sito']}_{doc_data['us']}_{timestamp}_{original_name}"

    # Copy file
    dest_path = os.path.join('DoSC', filename)
    shutil.copy2(source_file, dest_path)

    # Store path in data
    doc_data['file_path'] = f"DoSC/{filename}"

# Create DOC unit
doc_unit = us_service.create_us(doc_data)
print(f"Created DOC unit: {doc_unit.us}")
print(f"File saved: {doc_unit.file_path}")
```

### Querying DOC Units with Files

```python
# Get all DOC units
from sqlalchemy import and_

all_docs = us_service.get_all_us(
    filters={'unita_tipo': 'DOC'}
)

for doc in all_docs:
    print(f"DOC {doc.us}:")
    print(f"  Type: {doc.tipo_documento}")
    print(f"  File: {doc.file_path}")
    if doc.file_path and os.path.exists(doc.file_path):
        file_size = os.path.getsize(doc.file_path)
        print(f"  Size: {file_size / 1024:.2f} KB")
```

---

## Migration Reference

### Files Created

1. `/pyarchinit_mini/database/migration_scripts/add_file_path.py` - Migration script
2. `/run_file_path_migration.py` - Migration runner
3. `/DoSC/` - Documents storage directory

### Database Changes

**Before Migration:**
```sql
-- us_table schema
CREATE TABLE us_table (
    ...
    unita_tipo VARCHAR(200),
    tipo_documento VARCHAR(100),
    ...
);
```

**After Migration:**
```sql
-- us_table schema
CREATE TABLE us_table (
    ...
    unita_tipo VARCHAR(200),
    tipo_documento VARCHAR(100),
    file_path VARCHAR(500),  -- NEW COLUMN
    ...
);
```

### Rollback

If you need to remove the file upload functionality:

```bash
# 1. Backup DoSC folder
cp -r DoSC DoSC_backup_permanent

# 2. Run migration downgrade
python run_file_path_migration.py downgrade

# 3. Verify column removed
sqlite3 pyarchinit_mini.db "PRAGMA table_info(us_table)" | grep file_path
# Should return nothing

# 4. Optionally remove DoSC folder
# rm -rf DoSC  # CAREFUL! This deletes all uploaded files
```

---

## Conclusion

The DOC file upload system provides:

✅ **Seamless Integration** - Works with existing DOC units
✅ **User-Friendly** - Simple upload process in both interfaces
✅ **Organized Storage** - Centralized DoSC folder with clear naming
✅ **Database Tracking** - Full traceability of all files
✅ **Flexible** - Supports all common file types
✅ **Documented** - Complete guide and examples

For more information:
- [Extended Matrix Framework Guide](EXTENDED_MATRIX_FRAMEWORK.md)
- [Main README](../README.md)
- [GitHub Repository](https://github.com/enzococca/pyarchinit-mini)

---

**Version**: 1.0
**Date**: 2025-10-23
**Author**: PyArchInit Development Team
