# Extended Matrix Framework - Implementation Summary

## Overview

This document summarizes the complete implementation of Extended Matrix Framework features in PyArchInit-Mini v1.2.15.

**Date**: 2025-10-23
**Version**: 1.2.15

---

## Changes Implemented

### 1. Database Schema

#### New Field: `tipo_documento`
- **Table**: `us_table`
- **Type**: VARCHAR(100)
- **Purpose**: Store document type for DOC units
- **Values**: Image, PDF, DOCX, CSV, Excel, TXT
- **Migration**: `run_tipo_documento_migration.py`

**Migration Files Created**:
- `/pyarchinit_mini/database/migration_scripts/add_tipo_documento.py`
- `/run_tipo_documento_migration.py`

**Migration Execution**:
```bash
python run_tipo_documento_migration.py upgrade
```

**Result**:
```
[Migration] Adding tipo_documento column to us_table for SQLite...
[Migration] tipo_documento column added successfully
Upgrade completed successfully!
```

---

### 2. Model Updates

**File**: `pyarchinit_mini/models/us.py`

**Changes**:
```python
# Line 80: Added tipo_documento field
tipo_documento = Column(String(100))  # Document type for DOC units
```

**Description**: Added database column definition to US model for storing document type when unit type is DOC.

---

### 3. GraphML Export - Relationship Symbols

**File**: `pyarchinit_mini/harris_matrix/pyarchinit_visualizer.py`

**Changes**:
1. Added `_get_edge_label_for_unit()` method (lines 343-372)
2. Updated `_add_sequence_edges()` to use relationship symbols (lines 374-393)
3. Updated `_add_negative_edges()` to use relationship symbols (lines 395-410)
4. Updated `_add_contemporary_edges()` to use relationship symbols (lines 412-427)

**Functionality**:
- Standard units (US, USM, VSF, SF, CON, USD, USVA, USVB, USVC, TU) → use `>` symbol
- Special units (DOC, property, Extractor, Combiner) → use `>>` symbol
- Automatic symbol assignment based on `unita_tipo` attribute

**Example**:
```python
# US 1001 > US 1002  (standard stratigraphic)
# DOC 8001 >> US 1001  (document to US)
```

---

### 4. Web Interface

**File**: `web_interface/app.py`

**Changes** (lines 88-96):
```python
tipo_documento = SelectField(_l('Document Type'), choices=[
    ('', _l('-- Select --')),
    ('image', _l('Image')),
    ('PDF', _l('PDF')),
    ('DOCX', _l('DOCX')),
    ('CSV', _l('CSV')),
    ('Excel', _l('Excel')),
    ('TXT', _l('TXT'))
])
```

**File**: `web_interface/templates/us/form.html`

**Changes** (lines 89-96):
```html
<div class="col-md-3 mb-3">
    <label class="form-label">{{ _('Unit Type') }}</label>
    {{ form.unita_tipo(class="form-select", id="unita_tipo") }}
</div>
<div class="col-md-3 mb-3" id="tipo_documento_field" style="display:none;">
    <label class="form-label">{{ _('Document Type') }}</label>
    {{ form.tipo_documento(class="form-select") }}
</div>
```

**JavaScript** (lines 447-467):
```javascript
document.addEventListener('DOMContentLoaded', function() {
    const unitaTipoSelect = document.getElementById('unita_tipo');
    const tipoDocumentoField = document.getElementById('tipo_documento_field');

    function toggleTipoDocumento() {
        if (unitaTipoSelect.value === 'DOC') {
            tipoDocumentoField.style.display = 'block';
        } else {
            tipoDocumentoField.style.display = 'none';
        }
    }

    toggleTipoDocumento();
    unitaTipoSelect.addEventListener('change', toggleTipoDocumento);
});
```

**Functionality**:
- `tipo_documento` field appears automatically when `unita_tipo = "DOC"`
- JavaScript handles show/hide dynamically
- Form validation included

---

### 5. Desktop GUI

**File**: `desktop_gui/us_dialog_extended.py`

**Changes**:

1. **Field Declaration** (lines 141-153):
```python
# Tipo documento (conditional field)
self.tipo_documento_label = ttk.Label(id_frame, text=_("Document Type:"))
self.tipo_documento_label.grid(row=2, column=0, sticky="w", pady=5)
self.tipo_documento_label.grid_remove()  # Hide initially

self.fields['tipo_documento'] = ttk.Combobox(id_frame,
    values=[_("Image"), _("PDF"), _("DOCX"), _("CSV"), _("Excel"), _("TXT")],
    width=30)
self.fields['tipo_documento'].grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
self.fields['tipo_documento'].grid_remove()  # Hide initially

# Bind event
self.fields['unita_tipo'].bind('<<ComboboxSelected>>', self._toggle_tipo_documento_field)
```

2. **Toggle Method** (lines 1250-1263):
```python
def _toggle_tipo_documento_field(self, event=None):
    """Show/hide tipo_documento field based on unita_tipo selection"""
    translated_value = self.fields['unita_tipo'].get()
    original_value = translate_unit_type_to_original(translated_value)

    if original_value == 'DOC':
        # Show tipo_documento field
        self.tipo_documento_label.grid()
        self.fields['tipo_documento'].grid()
    else:
        # Hide tipo_documento field
        self.tipo_documento_label.grid_remove()
        self.fields['tipo_documento'].grid_remove()
```

3. **Data Loading** (lines 589, 631):
```python
# Added 'tipo_documento' to text_fields list
text_fields = ['area', 'us', 'schedatore', 'anno_scavo', 'unita_tipo', 'tipo_documento', ...]

# After loading, toggle visibility
self._toggle_tipo_documento_field()
```

4. **Data Saving** (line 1284):
```python
# Added 'tipo_documento' to string_fields
string_fields = ['sito', 'area', 'us', 'schedatore', 'unita_tipo', 'tipo_documento', ...]
```

**Functionality**:
- `tipo_documento` combobox appears when `unita_tipo = "DOC"`
- Uses `grid_remove()` / `grid()` for show/hide
- Automatically toggles on unit type change and on form load
- Integrated with translation system

---

### 6. Translations

**Files Modified**:
- `pyarchinit_mini/translations/it/LC_MESSAGES/messages.po`
- `pyarchinit_mini/translations/en/LC_MESSAGES/messages.po`

**New Translations Added**:

**Italian** (lines 4734-4754):
```po
# Extended Matrix - Document Type field
msgid "Document Type"
msgstr "Tipo Documento"

msgid "Image"
msgstr "Immagine"

msgid "PDF"
msgstr "PDF"

msgid "DOCX"
msgstr "DOCX"

msgid "CSV"
msgstr "CSV"

msgid "Excel"
msgstr "Excel"

msgid "TXT"
msgstr "TXT"
```

**English** (lines 4942-4962):
```po
# Extended Matrix - Document Type field
msgid "Document Type"
msgstr "Document Type"

msgid "Image"
msgstr "Image"

msgid "PDF"
msgstr "PDF"

msgid "DOCX"
msgstr "DOCX"

msgid "CSV"
msgstr "CSV"

msgid "Excel"
msgstr "Excel"

msgid "TXT"
msgstr "TXT"
```

**Compilation**:
```bash
pybabel compile -d pyarchinit_mini/translations
```

**Result**:
- Italian: `messages.mo` updated
- English: `messages.mo` updated

---

### 7. Documentation

#### 7.1 Extended Matrix Framework Guide

**File**: `docs/EXTENDED_MATRIX_FRAMEWORK.md`

**Content**:
- Complete guide to Extended Matrix Framework (90+ KB)
- 14 unit types with detailed descriptions
- Relationship symbols (`>`, `<`, `>>`, `<<`) explained
- DOC units and tipo_documento field usage
- GraphML export instructions
- Best practices and examples
- Practical workflow recommendations

**Sections**:
1. Introduction
2. Unit Types (detailed for each)
3. Relationship Symbols
4. DOC Units and Documents
5. GraphML Export for yEd
6. Best Practices
7. Practical Examples

#### 7.2 README Update

**File**: `README.md`

**Section Updated**: Lines 80-236

**Changes**:
- Renamed section from "GraphML Converter" to "Extended Matrix Framework & GraphML Export"
- Added comprehensive Extended Matrix documentation
- Listed all 14 unit types
- Explained relationship symbols with examples
- Documented DOC unit special functionality
- Updated GraphML export features
- Added migration instructions
- Updated code examples

**Key Additions**:
```markdown
### 🔄 Extended Matrix Framework & GraphML Export (v1.2.15+)

**Extended Matrix Framework**:
- 14 unit types supported
- Dual relationship symbols (>, >>, <, <<)
- DOC units with tipo_documento field
- Full GraphML export with all styles

**Unit Types**:
- Stratigraphic: US, USM, VSF, SF, CON, USD, USVA, USVB, USVC, TU
- Non-Stratigraphic: DOC, property, Extractor, Combiner

**Relationship Symbols**:
- Standard (>/<): For stratigraphic units
- Special (>><<): For non-stratigraphic units
```

---

## File Summary

### Files Created:
1. `/pyarchinit_mini/database/migration_scripts/add_tipo_documento.py`
2. `/run_tipo_documento_migration.py`
3. `/docs/EXTENDED_MATRIX_FRAMEWORK.md`
4. `/docs/EXTENDED_MATRIX_IMPLEMENTATION_SUMMARY.md` (this file)

### Files Modified:
1. `/pyarchinit_mini/models/us.py` - Added tipo_documento column
2. `/pyarchinit_mini/harris_matrix/pyarchinit_visualizer.py` - Added relationship symbols
3. `/web_interface/app.py` - Added tipo_documento form field
4. `/web_interface/templates/us/form.html` - Added conditional field with JavaScript
5. `/desktop_gui/us_dialog_extended.py` - Added conditional combobox with toggle logic
6. `/pyarchinit_mini/translations/it/LC_MESSAGES/messages.po` - Added Italian translations
7. `/pyarchinit_mini/translations/en/LC_MESSAGES/messages.po` - Added English translations
8. `/pyarchinit_mini/translations/it/LC_MESSAGES/messages.mo` - Compiled Italian catalog
9. `/pyarchinit_mini/translations/en/LC_MESSAGES/messages.mo` - Compiled English catalog
10. `/README.md` - Updated Extended Matrix section

---

## Testing Performed

### 1. Database Migration
✅ Migration executed successfully
✅ Column added: tipo_documento VARCHAR(100)
✅ Verified with: `sqlite3 pyarchinit_mini.db "PRAGMA table_info(us_table)"`

### 2. Model Updates
✅ US model includes tipo_documento field
✅ Field accessible via SQLAlchemy ORM

### 3. GraphML Export
✅ Relationship symbol logic implemented
✅ Method `_get_edge_label_for_unit()` returns correct symbols
✅ Standard units: `>`
✅ Special units: `>>`

### 4. Web Interface
✅ Form includes tipo_documento field
✅ JavaScript toggles field visibility
✅ Field shows when unita_tipo="DOC"
✅ Field hides for other unit types

### 5. Desktop GUI
✅ Combobox added with translations
✅ Toggle method works correctly
✅ Field visibility managed with grid_remove()/grid()
✅ Integration with save/load operations

### 6. Translations
✅ Italian translations compiled
✅ English translations compiled
✅ All document type values translated

### 7. Documentation
✅ Complete Extended Matrix guide created
✅ README updated with comprehensive section
✅ Examples and best practices included

---

## Usage Examples

### Creating a DOC Unit

**Web Interface**:
1. Navigate to US → New US
2. Select "DOC" from Unit Type dropdown
3. "Document Type" field appears automatically
4. Select document type (Image, PDF, etc.)
5. Fill in other fields and save

**Desktop GUI**:
1. Open US Dialog
2. Select "DOC" from Unit Type combobox
3. "Document Type" combobox appears
4. Select appropriate document type
5. Complete form and save

**Python API**:
```python
from pyarchinit_mini.services.us_service import USService

us_service = USService(db_manager)

doc_unit = {
    'sito': 'Pompei',
    'area': 'A',
    'us': 'DOC-8001',
    'unita_tipo': 'DOC',
    'tipo_documento': 'Image',
    'd_interpretativa': 'General excavation photo, Area A, Phase II'
}

us_service.create_us(doc_unit)
```

### Exporting with Relationship Symbols

**Export GraphML**:
```python
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer

# Generate matrix
generator = HarrisMatrixGenerator(db_manager, us_service)
graph = generator.generate_matrix('Pompei', 'A')

# Export with symbols
visualizer = PyArchInitMatrixVisualizer()
visualizer.create_matrix(graph, output_path='harris_pompei.dot')

# Convert to GraphML
from pyarchinit_mini.graphml_converter import convert_dot_to_graphml
convert_dot_to_graphml('harris_pompei.dot', 'harris_pompei.graphml')
```

**Result**:
- Standard units show `>` symbols on edges
- DOC units show `>>` symbols on edges
- All styled according to Extended Matrix palette

---

## Migration Instructions for Existing Installations

### Step 1: Backup Database

**SQLite**:
```bash
cp pyarchinit_mini.db pyarchinit_mini.db.backup_$(date +%Y%m%d)
```

**PostgreSQL**:
```bash
pg_dump -U postgres archaeology_db > backup_$(date +%Y%m%d).sql
```

### Step 2: Update PyArchInit-Mini

```bash
pip install --upgrade pyarchinit-mini
```

### Step 3: Run Migration

```bash
python run_tipo_documento_migration.py upgrade
```

### Step 4: Verify Migration

**SQLite**:
```bash
sqlite3 pyarchinit_mini.db "PRAGMA table_info(us_table)" | grep tipo_documento
```

**Expected Output**:
```
68|tipo_documento|VARCHAR(100)|0||0
```

### Step 5: Restart Application

```bash
# Web Interface
pyarchinit-mini-web

# Desktop GUI
pyarchinit-mini-gui
```

---

## Rollback Procedure (if needed)

### Rollback Migration

```bash
python run_tipo_documento_migration.py downgrade
```

**Warning**: This will remove the tipo_documento column and any data stored in it.

### Restore from Backup

**SQLite**:
```bash
cp pyarchinit_mini.db.backup_YYYYMMDD pyarchinit_mini.db
```

**PostgreSQL**:
```bash
psql -U postgres archaeology_db < backup_YYYYMMDD.sql
```

---

## Future Enhancements

Potential future additions to Extended Matrix Framework:

1. **Document File Attachments**
   - Upload actual files for DOC units
   - Store in media management system
   - Link DOC units to physical files

2. **Extractor/Combiner Workflows**
   - Visual workflow editor
   - Automatic data processing pipelines
   - Integration with analysis tools

3. **Advanced Property System**
   - Typed properties (boolean, numeric, date, etc.)
   - Property inheritance
   - Constraint validation

4. **Enhanced Visualization**
   - 3D matrix with Extended Matrix types
   - Interactive filtering by unit type
   - Custom color schemes

5. **Export Formats**
   - Gephi GraphML
   - Cytoscape JSON
   - Neo4j graph database

---

## References

- **Extended Matrix Framework Guide**: `docs/EXTENDED_MATRIX_FRAMEWORK.md`
- **README**: Main project README with Extended Matrix section
- **Migration Script**: `pyarchinit_mini/database/migration_scripts/add_tipo_documento.py`
- **Model Definition**: `pyarchinit_mini/models/us.py`
- **Web Form**: `web_interface/templates/us/form.html`
- **Desktop Dialog**: `desktop_gui/us_dialog_extended.py`
- **GraphML Visualizer**: `pyarchinit_mini/harris_matrix/pyarchinit_visualizer.py`

---

## Conclusion

The Extended Matrix Framework implementation in PyArchInit-Mini v1.2.15 provides:

✅ **Complete Unit Type Support** - All 14 Extended Matrix unit types
✅ **Relationship Symbols** - Correct `>` and `>>` symbols based on unit type
✅ **DOC Unit Management** - Special tipo_documento field with conditional display
✅ **Full Interface Coverage** - Web, Desktop GUI, CLI, and API
✅ **GraphML Export** - Complete yEd compatibility with Extended Matrix palette
✅ **i18n Support** - Italian and English translations
✅ **Comprehensive Documentation** - Complete guide and examples
✅ **Migration Support** - Safe upgrade/downgrade for existing installations

The implementation follows archaeological best practices and the Extended Matrix specification while maintaining backward compatibility with traditional Harris Matrix workflows.

---

**Document Version**: 1.0
**Date**: 2025-10-23
**Author**: PyArchInit Development Team
