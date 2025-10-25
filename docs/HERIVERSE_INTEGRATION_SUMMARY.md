# Heriverse/ATON Export Integration Summary

**Date**: October 25, 2025
**Status**: ✅ Completed

---

## Overview

This update adds a separate Heriverse/ATON JSON export format to PyArchInit-Mini s3Dgraphy integration, following the complete specification provided by the user.

---

## What is Heriverse Format?

Heriverse/ATON JSON format is an extended version of s3Dgraphy v1.5 that includes:

1. **CouchDB/Scene Wrapper**: Top-level metadata for scene management
2. **Environment Configuration**: Panoramas, lighting, and scene settings
3. **Scenegraph**: 3D scene hierarchy for rendering
4. **Extended Node Categories**:
   - `USVn`: Virtual negative units (separate from USVs)
   - `semantic_shapes`: 3D proxy models (GLB) for performance
   - `representation_models`: Full-detail 3D models (GLTF)
   - `panorama_models`: 360° panoramic images
5. **Additional Edge Types**:
   - `generic_connection`: Paradata relationships
   - `changed_from`: Stratigraphic evolution
   - `contrasts_with`: Conflicting interpretations

---

## Implementation Details

### 1. New Export Method

**File**: `pyarchinit_mini/s3d_integration/s3d_converter.py:418-647`

```python
def export_to_heriverse_json(self, graph, output_path,
                              site_name, creator_id, resource_path):
    """
    Export s3dgraphy graph to Heriverse/ATON JSON format

    Features:
    - CouchDB/scene wrapper with auto-generated UUIDs
    - Environment, scenegraph, multigraph sections
    - USVn category for virtual negative units
    - Semantic shapes auto-generated for each US
    - Additional edge types for paradata
    """
```

**Key Features**:
- Auto-generates scene UUID (`scene:uuid`)
- Auto-generates creator UUID if not provided
- Auto-generates semantic_shape placeholders for each US
- Includes environment configuration (panoramas, lighting)
- Includes scenegraph structure
- Wraps s3Dgraphy v1.5 graph in `resource_json.multigraph`

---

### 2. New Flask Route

**File**: `web_interface/s3d_routes.py:208-259`

```python
@s3d_bp.route('/export/heriverse/<site_name>')
@login_required
def export_heriverse(site_name):
    """Export site stratigraphy as Heriverse/ATON JSON"""
    # Get US data from database
    # Create s3dgraphy graph
    # Export to Heriverse format
    # Send file download
```

**Endpoint**: `GET /3d/export/heriverse/<site_name>`
**Output**: `{site_name}_heriverse.json`
**Authentication**: Login required

---

### 3. Web UI Update

**File**: `web_interface/templates/harris_matrix/graphml_export.html`

**Changes**:
- Added third export button: "Export Heriverse" (warning color)
- Updated button layout from 2 to 3 columns (col-md-4)
- Added `exportHeriverse()` JavaScript function
- Updated features list to mention Heriverse format

**UI Layout**:
```
┌──────────────┬──────────────┬──────────────┐
│ Export JSON  │Export Heriverse│Interactive  │
│  (success)   │  (warning)   │  Viewer     │
│              │              │ (primary)    │
└──────────────┴──────────────┴──────────────┘
```

---

### 4. Documentation

**File**: `docs/s3dgraphy_integration.md`

**Updates**:
1. Added **Heriverse/ATON JSON Format** section with:
   - Complete structure example
   - Feature list
   - When to use guidelines
2. Updated **Web GUI usage** with 3 export options
3. Added **API example** for `/3d/export/heriverse/<site>`
4. Updated **comparison table** with Heriverse column
5. Added **Python code example** for `export_to_heriverse_json()`
6. Updated **Web Routes** list with Heriverse endpoint

---

### 5. Testing

**File**: `test_heriverse_export.py`

**Test Coverage**:
1. ✅ S3DConverter import
2. ✅ `export_to_heriverse_json()` method exists
3. ✅ Heriverse JSON export functionality
4. ✅ Complete structure validation:
   - Top-level CouchDB wrapper (8 required keys)
   - Scene metadata (_id, _rev, type, creator, etc.)
   - Environment configuration (mainpano, lightprobes, mainlight)
   - Scenegraph structure (nodes, edges)
   - Multigraph v1.5 format
   - 13 node categories (including semantic_shapes, USVn)
   - 4 stratigraphic subcategories (US, USVs, USVn, SF)
   - 13 edge types (including generic_connection)
   - Semantic shapes auto-generation

**Test Results**: ✅ All tests passed (4/4)

---

## JSON Structure Comparison

### Basic s3Dgraphy v1.5
```json
{
  "version": "1.5",
  "context": {...},
  "graphs": {
    "graph_id": {
      "nodes": {
        "stratigraphic": {"US": {}, "USVs": {}, "SF": {}}
      },
      "edges": {"is_before": [], "has_same_time": []}
    }
  }
}
```

### Heriverse Format
```json
{
  "_id": "scene:uuid",
  "_rev": "1-revision",
  "type": "scene",
  "creator": "user:uuid",
  "resource_path": "https://...",
  "resource_json": {
    "environment": {
      "mainpano": {"url": "s"},
      "lightprobes": {"auto": "true"},
      "mainlight": {"direction": ["0.0", "0.0", "0.0"]}
    },
    "scenegraph": {
      "nodes": {},
      "edges": {".": []}
    },
    "multigraph": {
      "version": "1.5",
      "graphs": {
        "graph_id": {
          "nodes": {
            "stratigraphic": {
              "US": {},
              "USVs": {},
              "USVn": {},  // NEW
              "SF": {}
            },
            "semantic_shapes": {},        // NEW
            "representation_models": {},  // NEW
            "panorama_models": {}         // NEW
          },
          "edges": {
            "is_before": [],
            "generic_connection": [],  // NEW
            "changed_from": [],        // NEW
            "contrasts_with": []       // NEW
          }
        }
      }
    }
  },
  "wapp": "heriverse"
}
```

---

## Key Differences: s3Dgraphy v1.5 vs Heriverse

| Feature | s3Dgraphy v1.5 | Heriverse |
|---------|----------------|-----------|
| **Wrapper** | None | CouchDB scene wrapper |
| **UUIDs** | No | Auto-generated (_id, creator) |
| **Environment** | No | Yes (panoramas, lighting) |
| **Scenegraph** | No | Yes (3D scene hierarchy) |
| **USVn Category** | No | Yes (virtual negative units) |
| **Semantic Shapes** | No | Yes (auto-generated GLB placeholders) |
| **Representation Models** | No | Yes (GLTF models) |
| **Panorama Models** | No | Yes (360° images) |
| **Generic Connection** | No | Yes (paradata edges) |
| **Use Case** | General web platforms | Heriverse/ATON platforms |

---

## Usage Examples

### Web GUI

1. Navigate to **Harris Matrix → Export GraphML**
2. Scroll to **"Export s3Dgraphy (Extended Matrix)"** section
3. Select site from dropdown
4. Choose **"From Database"** source
5. Click **"Export Heriverse"** button
6. Download `{site_name}_heriverse.json`

### API

```bash
# Export Heriverse JSON
curl http://localhost:5000/3d/export/heriverse/Pompeii \
  -H "Authorization: Bearer <token>" \
  -o pompeii_heriverse.json
```

### Python

```python
from pyarchinit_mini.s3d_integration import S3DConverter

converter = S3DConverter()
graph = converter.create_graph_from_us(us_list, "Pompeii")

# Export to Heriverse format
converter.export_to_heriverse_json(
    graph,
    "pompeii_heriverse.json",
    site_name="Pompeii",
    creator_id="user:12345",  # Optional
    resource_path="https://server/uploads"  # Optional
)
```

---

## Files Modified

| File | Changes | Lines |
|------|---------|-------|
| `pyarchinit_mini/s3d_integration/s3d_converter.py` | Added `export_to_heriverse_json()` method | +230 |
| `web_interface/s3d_routes.py` | Added `/3d/export/heriverse/<site>` route | +52 |
| `web_interface/templates/harris_matrix/graphml_export.html` | Added Heriverse export button and function | +21 |
| `docs/s3dgraphy_integration.md` | Added Heriverse documentation | +95 |
| `test_heriverse_export.py` | Created comprehensive test suite | +249 (new file) |

**Total**: ~647 lines added

---

## Semantic Shapes Auto-Generation

The Heriverse export automatically generates semantic shape placeholders for each US:

```python
# For each US node
shape_id = f"shape_{node.node_id}"
semantic_shapes[shape_id] = {
    "name": f"3D Model for {node.name}",
    "description": "Proxy 3D model",
    "url": f"{resource_path}/models/{node.node_id}.glb",
    "format": "glb",
    "us_reference": node.node_id
}
```

**Benefits**:
- Ready for 3D model integration
- Performance-optimized proxy models (GLB)
- Automatic US → semantic_shape mapping
- Compatible with Heriverse/ATON viewers

---

## Integration with Existing Features

### Compatible With
- ✅ Database export (from US table)
- ✅ Interactive stratigraph viewer
- ✅ 3D model upload system
- ✅ Extended Matrix Framework
- ✅ Period/epoch context

### Not Yet Supported
- ⚠️ GraphML import → Heriverse export (can be added later)
- ⚠️ Actual 3D model URLs (currently placeholders)
- ⚠️ Actual panorama model URLs (currently placeholders)

---

## Benefits

1. **Standards Compliance**: Follows Heriverse/ATON specification exactly
2. **Separate Option**: Doesn't interfere with existing s3Dgraphy v1.5 export
3. **Auto-Generation**: UUIDs and semantic shapes generated automatically
4. **Complete Metadata**: Full CouchDB wrapper with scene information
5. **Future-Ready**: Placeholder structure for 3D models and panoramas
6. **Tested**: Comprehensive test suite validates structure
7. **Documented**: Complete documentation in English

---

## Next Steps (Optional Enhancements)

1. **GraphML → Heriverse**: Support importing GraphML and exporting to Heriverse
2. **Actual 3D Model Integration**: Link semantic_shapes to uploaded 3D models
3. **Panorama Upload**: Add panorama upload functionality
4. **Representation Models**: Support full GLTF model references
5. **Scene Editor**: Web UI for editing environment/scenegraph
6. **CouchDB Integration**: Direct sync with CouchDB database

---

## Resources

- **s3Dgraphy**: https://github.com/zalmoxes-laran/s3dgraphy
- **Extended Matrix**: https://www.extendedmatrix.org
- **s3Dgraphy Docs**: https://docs.extendedmatrix.org/projects/s3dgraphy/
- **Heriverse**: https://heriverse.org
- **ATON Framework**: https://github.com/phoenixbf/aton

---

## Summary

✅ **All tasks completed successfully**:
1. ✅ Created `export_to_heriverse_json()` method with full specification
2. ✅ Added Flask route `/3d/export/heriverse/<site_name>`
3. ✅ Updated web UI with "Export Heriverse" button
4. ✅ Documented Heriverse format in s3dgraphy_integration.md
5. ✅ Created comprehensive test suite (4/4 tests passing)

**The Heriverse export is now fully functional and ready for use!** 🎉
