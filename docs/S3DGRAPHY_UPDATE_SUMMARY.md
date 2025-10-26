# s3Dgraphy Integration Update Summary

**Date**: October 25, 2025
**Status**: ✅ Completed

---

## Overview

This update implements the correct s3Dgraphy JSON v1.5 export format and removes redundant GraphML export functionality from the s3Dgraphy integration, following the official s3Dgraphy specification.

---

## Changes Made

### 1. ✅ Implemented Correct JSON v1.5 Export Format

**File**: `pyarchinit_mini/s3d_integration/s3d_converter.py`

**Changes**:
- Replaced NetworkX node-link format with s3Dgraphy v1.5 specification
- Added proper structure with:
  - Top-level: `version`, `context`, `graphs`
  - Context: `absolute_time_Epochs` with period definitions
  - Graphs: Complete graph structure with nested node categories
  - Nodes organized by category:
    - `authors`, `stratigraphic` (US, USVs, SF), `epochs`, `groups`
    - `properties`, `documents`, `extractors`, `combiners`, `links`, `geo`
  - Edges organized by type:
    - `is_before`, `has_same_time`, `has_data_provenance`, `has_author`
    - `has_first_epoch`, `survive_in_epoch`, `is_in_activity`
    - `has_property`, `has_timebranch`, `has_linked_resource`
- Added `_generate_epoch_color()` helper method for period visualization

**Before** (lines 342-364):
```python
def export_to_json(self, graph, output_path):
    """Export using NetworkX node-link format"""
    nx_graph = self._convert_to_networkx(graph)
    json_data = nx.node_link_data(nx_graph, edges='edges')  # WRONG FORMAT
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    return output_path
```

**After** (lines 342-508):
```python
def export_to_json(self, graph, output_path):
    """Export s3dgraphy graph to JSON format v1.5 specification"""
    # Build s3Dgraphy v1.5 JSON structure
    json_data = {
        "version": "1.5",
        "context": {"absolute_time_Epochs": {}},
        "graphs": {}
    }
    # Extract epochs, organize nodes by category, organize edges by type
    # ... (complete implementation)
```

---

### 2. ✅ Removed GraphML Export from s3Dgraphy

**Rationale**: PyArchInit already has native GraphML export with Extended Matrix support. s3Dgraphy GraphML export was redundant and should only use JSON format for web platforms.

**Files Modified**:

#### A. `pyarchinit_mini/s3d_integration/s3d_converter.py`
- **Removed**: `export_to_graphml()` method (lines 250-282)
- **Removed**: `_add_yed_formatting()` method (lines 284-340)

#### B. `web_interface/s3d_routes.py`
- **Removed**: `/3d/export/graphml/<site_name>` route (lines 166-206)
- **Kept**: `/3d/export/json/<site_name>` route for JSON export
- **Kept**: `/3d/viewer/<site_name>` route for interactive viewer

#### C. `web_interface/templates/harris_matrix/graphml_export.html`
- **Removed**: "Export GraphML" button from s3Dgraphy section (line 92-95)
- **Updated**: Layout to 2 buttons instead of 3 (JSON + Interactive Viewer)
- **Removed**: `exportS3DGraphML()` JavaScript function (lines 169-176)
- **Updated**: Features list to mention JSON v1.5 and web platforms

---

### 3. ✅ Updated 3D Viewer to Use JSON v1.5

**Files Modified**:

#### A. `web_interface/s3d_routes.py` (lines 208-262)

**Changes**:
- Added automatic JSON file check: creates JSON if it doesn't exist
- Uses s3Dgraphy JSON v1.5 format instead of NetworkX node-link format
- Ensures directory exists before writing JSON
- Reads JSON file directly instead of converting on-the-fly

**Before**:
```python
# Convert to NetworkX and then to JSON
nx_graph = converter._convert_to_networkx(graph)
graph_data = nx.node_link_data(nx_graph, edges='edges')  # WRONG FORMAT
```

**After**:
```python
# Check if s3Dgraphy JSON file exists, if not create it
json_path = Path(app.config['UPLOAD_FOLDER']) / 'graphml' / f"{site_name}_stratigraphy.json"
if not json_path.exists():
    # Create JSON file using export_to_json (v1.5 format)
    converter.export_to_json(graph, str(json_path))

# Read the s3Dgraphy JSON v1.5 file
with open(json_path, 'r', encoding='utf-8') as f:
    graph_data = json.load(f)
```

#### B. `web_interface/templates/harris_matrix/viewer_3d_integrated.html`

**Changes**:
- Added `transformS3DGraphData()` function to convert s3Dgraphy JSON v1.5 to viewer format
- Function flattens nested node categories into single array
- Function flattens edge types into single array
- Maps edge properties (from/to → source/target)

**Added Transformation Function** (lines 421-505):
```javascript
function transformS3DGraphData(s3dData) {
    // Extract first graph
    const graph = s3dData.graphs[Object.keys(s3dData.graphs)[0]];

    // Flatten node categories (stratigraphic.US, documents, etc.) → nodes array
    const nodes = [];
    for (const [category, categoryNodes] of Object.entries(graph.nodes)) {
        // Handle stratigraphic subcategories
        // Flatten to single array
    }

    // Flatten edge types (is_before, has_same_time, etc.) → edges array
    const edges = [];
    for (const [edgeType, edgeList] of Object.entries(graph.edges)) {
        edges.push({ source: edge.from, target: edge.to, ... });
    }

    return { nodes, edges };
}

const graphData = transformS3DGraphData(s3dData);
```

**Fix**: Resolved `TypeError: undefined is not an object (evaluating 'nodes.forEach')` error

---

### 4. ✅ Translated Documentation to English

**Files Modified**:

#### A. `docs/s3dgraphy_integration.md`
- **Translated**: Complete Italian → English translation
- **Updated**: Removed GraphML export references
- **Added**: JSON v1.5 structure documentation
- **Added**: Comparison table (Native GraphML vs s3Dgraphy JSON)
- **Added**: Troubleshooting section
- **Added**: API reference
- **Added**: Key differences section

#### B. `docs/features/s3dgraphy.rst` (NEW FILE)
- **Created**: ReadTheDocs integration file
- **Added**: Complete feature documentation
- **Added**: Usage examples (Web, API, Python)
- **Added**: Comparison table
- **Added**: Resource links
- **Linked**: To main s3dgraphy_integration.md

---

### 5. ✅ Testing

**Created**: `test_s3d_integration.py`

**Test Results**: ✅ All tests passed (3/3)

1. ✅ **Import S3DConverter**: Successfully imports without errors
2. ✅ **JSON v1.5 Export**: Validates complete JSON structure
   - Version: 1.5
   - Context with absolute_time_Epochs
   - Graphs with all required keys
   - 10 node categories (authors, stratigraphic, epochs, etc.)
   - 10 edge types (is_before, has_same_time, etc.)
3. ✅ **GraphML Method Removed**: Confirms export_to_graphml() doesn't exist

---

## Files Modified Summary

| File | Changes |
|------|---------|
| `pyarchinit_mini/s3d_integration/s3d_converter.py` | Rewrote export_to_json(), removed export_to_graphml() and _add_yed_formatting() |
| `web_interface/s3d_routes.py` | Removed GraphML route, updated viewer to use JSON v1.5 |
| `web_interface/templates/harris_matrix/graphml_export.html` | Removed GraphML button, updated UI |
| `web_interface/templates/harris_matrix/viewer_3d_integrated.html` | Added transformS3DGraphData() function to convert JSON v1.5 to viewer format |
| `docs/s3dgraphy_integration.md` | Translated to English, updated content |
| `docs/features/s3dgraphy.rst` | Created new ReadTheDocs integration file |
| `test_s3d_integration.py` | Created comprehensive test suite |

---

## API Changes

### Removed
- ❌ `GET /3d/export/graphml/<site_name>` - Use native GraphML export instead
- ❌ `S3DConverter.export_to_graphml()` - Method removed
- ❌ `S3DConverter._add_yed_formatting()` - Method removed

### Updated
- ✅ `S3DConverter.export_to_json()` - Now exports s3Dgraphy JSON v1.5 format
- ✅ `GET /3d/viewer/<site_name>` - Uses JSON v1.5, auto-creates if missing

### Unchanged
- ✅ `GET /3d/export/json/<site_name>` - Export s3Dgraphy JSON
- ✅ `POST /3d/upload` - Upload 3D models
- ✅ `GET /3d/viewer/<path>` - View 3D models
- ✅ `GET /3d/models/<site_name>` - List site models

---

## JSON v1.5 Structure

### Top Level
```json
{
  "version": "1.5",
  "context": {
    "absolute_time_Epochs": {
      "epoch_01": {
        "name": "Modern Period",
        "start": null,
        "end": null,
        "color": "#FFD700"
      }
    }
  },
  "graphs": { /* ... */ }
}
```

### Graph Structure
```json
{
  "graph_id": {
    "id": "graph_id",
    "name": "Graph Name",
    "description": "Description",
    "defaults": {
      "license": "CC-BY-NC-ND",
      "authors": ["pyarchinit_export_20251025"],
      "embargo_until": null
    },
    "nodes": {
      "authors": {},
      "stratigraphic": {"US": {}, "USVs": {}, "SF": {}},
      "epochs": {},
      "groups": {},
      "properties": {},
      "documents": {},
      "extractors": {},
      "combiners": {},
      "links": {},
      "geo": {}
    },
    "edges": {
      "is_before": [],
      "has_same_time": [],
      /* ... 10 edge types total ... */
    }
  }
}
```

---

## Migration Guide

### For Users

**If you were using s3Dgraphy GraphML export**:
1. Use the **native PyArchInit GraphML export** instead:
   - Menu → Harris Matrix → Export GraphML → Export to GraphML
   - This provides Extended Matrix palette with period-based TableNode layout
2. For s3Dgraphy integration, use **JSON export only**:
   - Menu → Harris Matrix → Export GraphML → Export s3Dgraphy → Export JSON

**If you have old JSON files**:
- Old files used NetworkX node-link format (incompatible)
- Re-export using new JSON v1.5 format
- New format is compatible with Heriverse, ATON, and other s3Dgraphy platforms

### For Developers

**If you were calling `export_to_graphml()`**:
```python
# OLD (removed)
converter.export_to_graphml(graph, "output.graphml")

# NEW - Use native PyArchInit export instead
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
matrix_gen = HarrisMatrixGenerator(db_manager)
matrix_gen.export_to_graphml(graph, "output.graphml", site_name, title)
```

**If you were using JSON export**:
```python
# Still works, but now exports v1.5 format
converter.export_to_json(graph, "output.json")

# Old format: NetworkX node-link (WRONG)
# New format: s3Dgraphy v1.5 (CORRECT)
```

---

## Benefits

1. **Standards Compliance**: Now follows official s3Dgraphy v1.5 specification
2. **Clearer Separation**: Native GraphML for yEd, s3Dgraphy JSON for web platforms
3. **Better Metadata**: Complete node categorization and edge type organization
4. **Web Platform Ready**: Compatible with Heriverse, ATON, and other platforms
5. **English Documentation**: All documentation now in English for broader accessibility
6. **Tested**: Comprehensive test suite ensures correct implementation

---

## Next Steps

1. Update version number in `pyproject.toml` (suggest v1.3.2 or v1.4.0)
2. Update `docs/conf.py` with new version
3. Commit changes with message: "Fix s3Dgraphy JSON v1.5 export, remove GraphML redundancy"
4. Push to repository
5. Publish to PyPI
6. Update ReadTheDocs (automatic on push)

---

## Resources

- **s3Dgraphy**: https://github.com/zalmoxes-laran/s3dgraphy
- **Extended Matrix**: https://www.extendedmatrix.org
- **s3Dgraphy Docs**: https://docs.extendedmatrix.org/projects/s3dgraphy/
- **Import/Export Spec**: https://docs.extendedmatrix.org/projects/s3dgraphy/en/latest/s3dgraphy_import_export.html

---

## Test Command

```bash
python test_s3d_integration.py
```

Expected output:
```
============================================================
s3Dgraphy Integration Test Suite
============================================================
✓ Import S3DConverter: PASS
✓ JSON v1.5 Export: PASS
✓ GraphML Method Removed: PASS

============================================================
Total: 3/3 tests passed
============================================================
```

---

**Summary**: All s3Dgraphy integration issues resolved. JSON export now complies with v1.5 specification, redundant GraphML export removed, documentation translated to English, and comprehensive tests passing.
