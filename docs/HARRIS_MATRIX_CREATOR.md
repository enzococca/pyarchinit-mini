# Harris Matrix Creator - Complete Guide

**Version:** 1.6.0
**Date:** 2025-10-26
**Status:** ✅ Production Ready

## Overview

The Harris Matrix Creator provides two powerful ways to create and manage Harris Matrix diagrams:

1. **CSV/Excel Import Tool** - Import complete stratigraphic matrices from spreadsheets
2. **Interactive Web Editor** - Visual drag-and-drop matrix creation

Both tools support:
- 14 Extended Matrix node types (US, USM, USVA, DOC, Extractor, etc.)
- 14 relationship types (Covers, Cuts, Continuity, etc.)
- Period and area grouping
- Automatic database population
- GraphML and DOT export

---

## Part 1: CSV/Excel Import Tool

### Features

- ✅ Import complete Harris Matrix from Excel or CSV
- ✅ Extended Matrix support (all 14 node types)
- ✅ Validation and error reporting
- ✅ Automatic database population
- ✅ GraphML/DOT export
- ✅ Template generation with examples

### Quick Start

#### 1. Generate Template

```bash
pyarchinit-harris-template
```

This creates `harris_matrix_template.xlsx` with three sheets:
- **INSTRUCTIONS** - Read this first!
- **NODES** - Define your stratigraphic units
- **RELATIONSHIPS** - Define connections

#### 2. Fill the Template

Open the Excel file and edit the **NODES** sheet:

| us_number | unit_type | description | area | period | phase | file_path |
|-----------|-----------|-------------|------|--------|-------|-----------|
| 1001 | US | Topsoil layer | Area A | Modern | | |
| 1002 | USM | Stone wall foundation | Area A | Medieval | Late | |
| 1003 | US | Fill deposit | Area A | Medieval | Late | |
| 1004 | USVA | Pit cut (virtual) | Area B | Medieval | | |
| 1005 | DOC | Site plan drawing | Area A | | | docs/plan.pdf |

Edit the **RELATIONSHIPS** sheet:

| from_us | to_us | relationship | notes |
|---------|-------|--------------|-------|
| 1001 | 1002 | Covers | Topsoil above wall |
| 1002 | 1003 | Covers | Wall above fill |
| 1003 | 1004 | Fills | Fill inside pit |
| 1002 | 1005 | >> | Wall linked to document |

#### 3. Import

```bash
pyarchinit-harris-import harris_matrix_template.xlsx --site "Archaeological Site"
```

Add export options:

```bash
pyarchinit-harris-import matrix.xlsx --site "Site 1" --export-graphml --export-dot -o ./output
```

### Field Descriptions

#### NODES Sheet

**Required Fields:**
- `us_number` - Unique US identifier (e.g., "1001")
- `unit_type` - Node type (see list below)

**Optional Fields:**
- `description` - Human-readable description
- `area` - Spatial grouping (e.g., "Area A", "Trench 1")
- `period` - Chronological period (e.g., "Medieval", "Roman")
- `phase` - Period subdivision (e.g., "Early", "Late")
- `file_path` - Document path (required for DOC type)

**Node Types:**

| Type | Symbol | Description | Usage |
|------|--------|-------------|-------|
| US | ☐ | Standard stratigraphic unit | Default for most contexts |
| USM | ☐ | Mural stratigraphic unit | Walls, structures |
| USVA | ☐ | Virtual US type A | Negative features (pits, cuts) |
| USVB | ☐ | Virtual US type B | Virtual boundaries |
| USVC | ☐ | Virtual US type C | Virtual contexts |
| TU | ☐ | Topographic unit | Survey/topographic features |
| USD | ☐ | Stratigraphic unit (special) | Special stratigraphic contexts |
| SF | ○ | Special finds | Important artifacts |
| VSF | ○ | Virtual special finds | Virtual find contexts |
| CON | ☐ | Context | General context |
| DOC | ◇ | Document | Plans, photos, reports |
| Extractor | ⬢ | Extractor node | Aggregation/extraction |
| Combiner | ⬢ | Combiner node | Combination/grouping |
| property | ○ | Property node | Metadata/properties |

#### RELATIONSHIPS Sheet

**Required Fields:**
- `from_us` - Source US number
- `to_us` - Target US number
- `relationship` - Relationship type (see below)

**Optional Fields:**
- `notes` - Additional information

**Relationship Types:**

| English Name | Italian | Symbol | Arrow | Usage |
|--------------|---------|--------|-------|-------|
| Covers | Copre | → | ▶ | A covers/above B |
| Covered_by | Coperto da | ← | ◀ | A covered by/below B |
| Fills | Riempie | → | ▶ | A fills B (deposit in feature) |
| Filled_by | Riempito da | ← | ◀ | A filled by B |
| Cuts | Taglia | → | ▶ | A cuts B (negative action) |
| Cut_by | Tagliato da | ← | ◀ | A cut by B |
| Bonds_to | Si lega a | → | ▶ | A bonds to B (physical connection) |
| Equal_to | Uguale a | ↔ | ⬌ | A equals B (same context) |
| Leans_on | Si appoggia a | → | ▶ | A leans on B (rests against) |
| > | > | ⋯→ | ▷ | Connection to single-symbol unit |
| < | < | ←⋯ | ◁ | From single-symbol unit |
| >> | >> | ⋯→ | ▷ | Connection to double-symbol unit |
| << | << | ←⋯ | ◁ | From double-symbol unit |
| Continuity | Continuity | — | — | Contemporary (no direction) |

### CSV Format

For CSV files, combine NODES and RELATIONSHIPS sections with an empty line between:

```csv
us_number,unit_type,description,area,period,phase,file_path
1001,US,Topsoil layer,Area A,Modern,,
1002,USM,Stone wall,Area A,Medieval,Late,

from_us,to_us,relationship,notes
1001,1002,Covers,Topsoil above wall
```

### Validation

The import tool automatically validates:

- ✅ Required fields present
- ✅ US numbers unique
- ✅ Referenced US exist
- ✅ Relationship types valid
- ✅ DOC units have file_path
- ⚠️ Warnings for unknown types (uses defaults)

### Error Handling

**Common Errors:**

1. **Missing US number:**
   ```
   Error: Row 5: us_number is required
   ```
   **Fix:** Fill the `us_number` column

2. **Referenced US not found:**
   ```
   Error: Row 3: from_us '1005' not defined in NODES section
   ```
   **Fix:** Add US 1005 to NODES sheet or fix the reference

3. **Invalid file format:**
   ```
   Error: Unsupported file format: .txt. Use .csv, .xlsx, or .xls
   ```
   **Fix:** Use Excel or CSV format

### Command-Line Options

```bash
pyarchinit-harris-import [OPTIONS] FILE_PATH

Arguments:
  FILE_PATH  Path to CSV or Excel file

Options:
  -s, --site TEXT        Site name (required)
  -g, --export-graphml   Export to GraphML format
  -d, --export-dot       Export to DOT format
  -o, --output-dir PATH  Output directory for exports
  --help                 Show this message and exit
```

**Examples:**

```bash
# Basic import
pyarchinit-harris-import matrix.xlsx --site "Pompeii Insula V"

# Import with GraphML export
pyarchinit-harris-import data.csv -s "Roman Villa" -g

# Import with both exports to specific directory
pyarchinit-harris-import site1.xlsx -s "Site 1" -g -d -o ./exports

# Generate empty template (no examples)
pyarchinit-harris-template --output my_template --no-examples
```

---

## Part 2: Interactive Web Editor

### Features

- ✅ Visual drag-and-drop node creation
- ✅ Interactive edge drawing
- ✅ Real-time property editing
- ✅ Extended Matrix node types
- ✅ Automatic layout
- ✅ Save to database
- ✅ Export to GraphML/DOT

### Access

1. Start the web server:
   ```bash
   pyarchinit-mini-web
   ```

2. Navigate to: `http://localhost:5001/harris-creator`

### User Interface

#### Main Page

The creator index shows:
- **Create New Matrix** - Start fresh with new site
- **Edit Existing Matrix** - Continue working on existing site
- **Features List** - Overview of capabilities
- **CSV/Excel Alternative** - Link to CLI tool

#### Editor Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ [Save] [Export GraphML] [Export DOT] [Back]                    │
├──────────┬────────────────────────────────────────┬──────────────┤
│  Tools   │          Canvas                        │ Properties   │
│          │                                        │              │
│ ☑ Node   │    ┌─────────┐                        │ US Number: * │
│ ☐ Edge   │    │ US 1001 │                        │ Type: US ▼  │
│          │    └────┬────┘                        │ Description: │
│ Node     │         │                             │              │
│ Types:   │    ┌────▼────┐                        │ Area:        │
│ [US]     │    │ US 1002 │                        │ Period:      │
│ [USM]    │    └────┬────┘                        │ Phase:       │
│ ...      │         │                             │              │
│          │    ┌────▼────┐                        │ [Apply]      │
│ Legend   │    │ US 1003 │                        │              │
│          │    └─────────┘                        │              │
└──────────┴────────────────────────────────────────┴──────────────┘
```

### Workflow

#### Creating a New Matrix

**Step 1: Create Site**
1. Go to `/harris-creator`
2. Enter site name
3. Click "Create New Matrix"

**Step 2: Add Nodes**
1. Select node type from toolbar (default: US)
2. Click on canvas to add node
3. Node appears with auto-generated number
4. Edit properties in right panel

**Step 3: Connect Nodes**
1. Switch to "Edge Mode"
2. Select relationship type
3. Click source node
4. Click target node
5. Edge is created

**Step 4: Edit Properties**
1. Click node or edge
2. Properties panel shows fields
3. Edit values
4. Click "Apply Changes"

**Step 5: Save and Export**
1. Click "Save" - Data saved to database
2. Click "Export GraphML" - Download GraphML file
3. Click "Export DOT" - Download DOT file

#### Editing Existing Matrix

**Step 1: Load Matrix**
1. Go to `/harris-creator`
2. Select site from dropdown
3. Click "Edit Matrix"

**Step 2: Modify**
- Add new nodes
- Add new edges
- Edit properties
- Delete elements (select + Delete button)

**Step 3: Save Changes**
- Click "Save" to update database
- Export if needed

### Editor Modes

#### Node Mode (Default)

**Purpose:** Add and edit nodes

**Actions:**
- Click canvas → Add node
- Click node → Select node
- Properties panel → Edit node

**Node Properties:**
- US Number (required)
- Unit Type (US, USM, USVA, etc.)
- Description
- Area (spatial grouping)
- Period (chronology)
- Phase (period subdivision)
- File Path (for DOC type)

#### Edge Mode

**Purpose:** Connect nodes with relationships

**Actions:**
1. Select relationship type
2. Click source node (highlighted green)
3. Click target node
4. Edge created automatically

**Edge Properties:**
- From US (read-only)
- To US (read-only)
- Relationship Type (editable)

### Canvas Controls

| Button | Action |
|--------|--------|
| Zoom In | Enlarge view |
| Zoom Out | Reduce view |
| Fit to Screen | Show all nodes |
| Auto Layout | Arrange hierarchically |
| Delete Selected | Remove selected element |
| Clear All | Remove everything |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Del | Delete selected |
| Esc | Deselect all |
| Ctrl+S | Save (browser default) |
| Ctrl+Z | Undo (not yet implemented) |

### Visual Styling

**Node Colors by Type:**

- US (Standard): Light Blue
- USM (Mural): Orange
- USVA (Virtual A): Purple
- SF (Special Finds): Yellow
- DOC (Document): Gray
- Extractor: Red
- Combiner: Indigo

**Edge Styles by Type:**

- Standard (Covers, Fills): Solid line
- Cuts: Dashed line
- Extended Matrix (>, >>): Dotted line
- Continuity: Solid line, no arrow

### API Endpoints

The web editor uses these REST endpoints:

```
GET  /harris-creator/                      - Index page
GET  /harris-creator/editor                - Editor page
POST /harris-creator/api/save              - Save matrix
GET  /harris-creator/api/export/<format>   - Export matrix
GET  /harris-creator/api/node-types        - Get node types
GET  /harris-creator/api/relationship-types - Get relationships
```

### Technical Details

**Technologies:**
- Backend: Flask (Python)
- Frontend: Cytoscape.js
- Storage: SQLite/PostgreSQL
- Export: NetworkX → GraphML/DOT

**Data Flow:**
```
User Input → Cytoscape.js → AJAX → Flask → SQLAlchemy → Database
                                                      ↓
                              GraphML/DOT ← NetworkX ← Flask
```

---

## Comparison

| Feature | CSV/Excel Import | Interactive Editor |
|---------|------------------|-------------------|
| Batch creation | ✅ Excellent | ❌ One-by-one |
| Visual feedback | ❌ None | ✅ Real-time |
| Learning curve | Low | Medium |
| Speed (100+ nodes) | Fast | Slow |
| Precision | High | High |
| Reusability | ✅ Templates | ❌ Manual |
| Collaboration | ✅ Share files | ⚠️ Database access |
| Best for | Large sites, bulk import | Small sites, visual design |

**Recommendation:**
- **Large sites (>50 nodes):** Use CSV/Excel import
- **Small sites (<50 nodes):** Use interactive editor
- **Hybrid:** Import bulk data, fine-tune in editor

---

## Integration with Existing Features

Both tools integrate seamlessly with:

### Harris Matrix Visualization
```python
# After import/creation, visualize
from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator

generator = MatrixGenerator(db_session)
graph = generator.generate_matrix("Site Name")
```

### GraphML Export for yEd
```bash
# Via CLI
pyarchinit-harris-import data.xlsx --site "Site" --export-graphml

# Via Web
Click "Export GraphML" in editor
```

### Documentation
```bash
# Generate site report with matrix
pyarchinit-mini-pdf --site "Site Name" --include-matrix
```

---

## Troubleshooting

### CSV/Excel Import

**Problem:** Import fails with "encoding error"

**Solution:** Save CSV as UTF-8:
```
Excel → Save As → CSV UTF-8 (Comma delimited)
```

**Problem:** "US number required" for all rows

**Solution:** Check column name is exactly `us_number` (lowercase, underscore)

### Interactive Editor

**Problem:** Editor won't load

**Solution:** Check Cytoscape.js is loaded:
```javascript
// In browser console
typeof cytoscape  // Should be "function"
```

**Problem:** Nodes don't appear on click

**Solution:**
1. Check mode indicator shows "Node Mode"
2. Clear browser cache
3. Check browser console for errors

**Problem:** Save fails

**Solution:**
1. Check database connection
2. Verify site exists
3. Check US numbers are unique

---

## Best Practices

### Data Preparation (CSV/Excel)

1. **Plan your structure** - Sketch matrix on paper first
2. **Use consistent naming** - "Area A", "Area B" (not "area a", "AREA-A")
3. **Test with small dataset** - Import 5-10 nodes first
4. **Validate periods** - Use standard period names
5. **Document relationships** - Use notes column

### Visual Editor

1. **Start with chronology** - Add oldest units first
2. **Group by area** - Create area sections
3. **Save frequently** - Click save every 10 nodes
4. **Use auto-layout** - Apply layout before saving
5. **Preview before export** - Check matrix looks correct

### Performance

**For large sites (>200 nodes):**
- Use CSV import (much faster)
- Export GraphML → Open in yEd
- Don't use web editor for bulk creation

**For small sites (<50 nodes):**
- Interactive editor provides best UX
- Visual feedback helps prevent errors

---

## Example Use Cases

### Use Case 1: Urban Excavation

**Site:** Medieval town, 150 US, 5 areas

**Method:** CSV/Excel Import

**Workflow:**
1. Archaeologist fills Excel template during excavation
2. Each area has separate section
3. Import at end of day
4. Export GraphML for publication

### Use Case 2: Small Trench

**Site:** Test trench, 30 US, single area

**Method:** Interactive Editor

**Workflow:**
1. Create site in web interface
2. Add nodes as excavation progresses
3. Connect relationships visually
4. Export for documentation

### Use Case 3: Legacy Data Migration

**Site:** Old database, 500 US

**Method:** CSV/Excel Import

**Workflow:**
1. Export old database to CSV
2. Map columns to template format
3. Batch import all data
4. Validate in web interface

---

## Future Enhancements

Planned features:

- [ ] Undo/Redo in visual editor
- [ ] Import from CSV directly in web UI
- [ ] Collaborative editing (multiple users)
- [ ] Export to PDF from editor
- [ ] Mobile-responsive editor
- [ ] Node templates (save frequent types)
- [ ] Bulk edge creation
- [ ] Visual diff between versions

---

## Support and Resources

### Documentation
- Main docs: https://pyarchinit-mini.readthedocs.io/en/latest/
- Harris Matrix theory: docs/HARRIS_MATRIX_THEORY.md
- GraphML format: docs/GRAPHML_DOT_EXPORT_GUIDE.md

### Examples
- Example CSV: `examples/harris_matrix_example.csv`
- Example Excel: `examples/harris_matrix_example.xlsx`
- Video tutorial: [Coming soon]

### Getting Help
- GitHub Issues: https://github.com/enzococca/pyarchinit-mini/issues
- Email: enzo.ccc@gmail.com

---

## License

GPL-2.0 License

Copyright (c) 2025 PyArchInit Team

---

**Last Updated:** 2025-10-26
**Version:** 1.6.0
**Tested With:** PyArchInit-Mini 1.5.2