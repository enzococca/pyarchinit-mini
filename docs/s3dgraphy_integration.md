# s3Dgraphy Integration - Complete Guide

**Date**: October 25, 2025

---

## 📘 WHAT IS s3Dgraphy?

**s3Dgraphy** is a Python library for 3D stratigraphic graphs.

- Multi-temporal Knowledge Graph
- Extended Matrix Framework
- JSON v1.5 export format
- 3D model integration

---

## 🔧 HOW IT WORKS

PyArchInit integrates s3Dgraphy with 3 modules:

### 1. S3DConverter
Converts PyArchInit US → s3dgraphy graph

```python
from pyarchinit_mini.s3d_integration import S3DConverter

converter = S3DConverter()
graph = converter.create_graph_from_us(us_list, "Pompeii")

# Export to s3Dgraphy JSON v1.5
converter.export_to_json(graph, "pompeii_s3d.json")

# Export to Heriverse JSON (with CouchDB wrapper)
converter.export_to_heriverse_json(
    graph,
    "pompeii_heriverse.json",
    site_name="Pompeii",
    creator_id="user:12345",
    resource_path="https://server/uploads"
)
```

### 2. Model3DManager
Manages 3D models (GLB, GLTF, OBJ, PLY, STL, FBX)

```python
from pyarchinit_mini.s3d_integration import Model3DManager

manager = Model3DManager("uploads")
metadata = manager.save_model("scan.glb", us_id="001", site_name="Pompeii")
```

### 3. Web Routes
- GET /3d/viewer/<path> - Display 3D model
- POST /3d/upload - Upload 3D model
- GET /3d/export/json/<site> - Export s3Dgraphy JSON v1.5
- GET /3d/export/heriverse/<site> - Export Heriverse JSON
- GET /3d/viewer/<site> - Interactive stratigraph viewer

---

## 📤 EXPORT FORMAT

### s3Dgraphy JSON v1.5
Standard format for web platforms (Heriverse, ATON)

**Structure**:
```json
{
  "version": "1.5",
  "context": {
    "absolute_time_Epochs": {}
  },
  "graphs": {
    "graph_id": {
      "nodes": {
        "authors": {},
        "stratigraphic": {
          "US": {},
          "USVs": {},
          "SF": {}
        },
        "documents": {},
        "extractors": {},
        "combiners": {}
      },
      "edges": {
        "is_before": [],
        "has_same_time": []
      }
    }
  }
}
```

**Features**:
- Complete metadata for each SU
- Extended Matrix Framework compliant
- 3D model references (GLB/GLTF)
- Archaeological period context
- Stratigraphic relationships (is_before, has_same_time)

### Heriverse/ATON JSON Format
Full-featured format for Heriverse and ATON platforms

**Structure**:
```json
{
  "_id": "scene:uuid",
  "_rev": "1-revision",
  "type": "scene",
  "creator": "user:uuid",
  "resource_path": "https://server/uploads/...",
  "title": "Site Name",
  "resource_json": {
    "environment": {...},
    "scenegraph": {...},
    "multigraph": {
      "version": "1.5",
      "context": {...},
      "graphs": {
        "graph_id": {
          "nodes": {
            "stratigraphic": {
              "US": {},
              "USVs": {},
              "USVn": {},  // Virtual negative units
              "SF": {}
            },
            "semantic_shapes": {},        // 3D proxy models (GLB)
            "representation_models": {},  // Full 3D models (GLTF)
            "panorama_models": {}         // Panoramic images
          },
          "edges": {
            "is_before": [],
            "has_same_time": [],
            "generic_connection": [],  // Paradata connections
            "changed_from": [],        // Evolution
            "contrasts_with": []       // Interpretations
          }
        }
      }
    }
  },
  "wapp": "heriverse"
}
```

**Additional Features**:
- CouchDB/scene wrapper with metadata
- Environment configuration (panoramas, lighting)
- Scenegraph for 3D scene structure
- USVn category (virtual negative units)
- Semantic shapes (proxy 3D models)
- Representation models (full 3D models)
- Panorama models (360° images)
- Generic paradata connections
- Auto-generated UUIDs for scene and creator

**When to use**:
- Uploading to Heriverse platform
- Integration with ATON viewer
- Advanced 3D visualization with semantic shapes
- CouchDB-based storage systems

---

## 🎯 HOW TO USE IT

### Via Web GUI

1. Menu → Harris Matrix → Export GraphML
2. Scroll to "Export s3Dgraphy (Extended Matrix)" section
3. Select site
4. Choose export format:
   - **Export JSON** - Standard s3Dgraphy v1.5 format
   - **Export Heriverse** - Heriverse/ATON format with CouchDB wrapper
   - **Interactive Viewer** - View in browser
5. Download file (site_name_stratigraphy.json or site_name_heriverse.json)

### Via API

#### Export JSON (s3Dgraphy v1.5)
```bash
curl http://localhost:5000/3d/export/json/Pompeii \
  -o pompeii_stratigraphy.json
```

#### Export Heriverse JSON
```bash
curl http://localhost:5000/3d/export/heriverse/Pompeii \
  -o pompeii_heriverse.json
```

#### Upload 3D Model
```bash
curl -X POST http://localhost:5000/3d/upload \
  -F "model_file=@scan.glb" \
  -F "site_name=Pompeii" \
  -F "us_id=001"
```

#### View 3D Model
URL: http://localhost:5000/3d/viewer/3d_models/Pompeii/US_001/scan.glb

#### Interactive Stratigraph Viewer
URL: http://localhost:5000/3d/viewer/Pompeii

---

## 🔄 EXPORT COMPARISON

| | Native GraphML | s3Dgraphy JSON v1.5 | Heriverse JSON |
|---|---|---|---|
| Route | /harris_matrix/graphml_export | /3d/export/json/<site> | /3d/export/heriverse/<site> |
| Format | GraphML (yEd) | JSON v1.5 | Heriverse/CouchDB |
| Metadata | Minimal | Complete | Complete + Scene |
| 3D Models | No | References | Semantic shapes + Models |
| Wrapper | No | No | CouchDB/scene |
| USVn Category | No | No | Yes |
| Use Case | yEd visualization | Web platforms | Heriverse/ATON platforms |

**Use Native GraphML for**:
- Quick visualization in yEd
- Period-based table layout
- Traditional Harris Matrix diagrams

**Use s3Dgraphy JSON v1.5 for**:
- Advanced analysis
- Complete metadata
- 3D model integration
- Extended Matrix Framework compliance
- General web platform integration

**Use Heriverse JSON for**:
- Uploading to Heriverse platform
- Integration with ATON viewer
- CouchDB-based systems
- Advanced 3D visualization with semantic shapes
- Full scene environment configuration

---

## ✅ WORKFLOW

1. Create US in database
2. 3D scan (photogrammetry)
3. Upload models via API
4. Export s3Dgraphy JSON
5. Use in web platforms or programmatic analysis
6. Share 3D model links

---

## 🆘 TROUBLESHOOTING

```bash
# Install s3dgraphy
pip install s3dgraphy

# Empty JSON: check US in database
# Model doesn't load: use GLB format, max 50MB
# Viewer error: check WebGL supported in browser
```

### Common Issues

**JSON file not found in viewer**:
The viewer automatically creates the JSON file on first load. If you see an error, manually export via:
- Web GUI: Harris Matrix → Export s3Dgraphy → Export JSON
- API: GET /3d/export/json/<site_name>

**3D model upload fails**:
- Check file format (GLB recommended)
- Check file size (max 50MB)
- Verify site_name exists in database
- Check upload directory permissions

---

## 📋 API REFERENCE

```python
# Export s3Dgraphy JSON
GET /3d/export/json/Pompeii → Pompeii_stratigraphy.json

# Upload 3D Model
POST /3d/upload
  - model_file (file): 3D model file
  - site_name (string): Archaeological site name
  - us_id (string): Stratigraphic unit ID

# View 3D Model
GET /3d/viewer/3d_models/Pompeii/US_001/scan.glb

# Interactive Stratigraph Viewer
GET /3d/viewer/Pompeii

# List 3D Models for Site
GET /3d/models/Pompeii

# List 3D Models for US
GET /3d/models/Pompeii/us/001
```

---

## 📚 ADDITIONAL RESOURCES

**s3Dgraphy**: https://github.com/zalmoxes-laran/s3dgraphy

**Extended Matrix**: https://www.extendedmatrix.org

**s3Dgraphy Documentation**: https://docs.extendedmatrix.org/projects/s3dgraphy/

**Import/Export Specification**: https://docs.extendedmatrix.org/projects/s3dgraphy/en/latest/s3dgraphy_import_export.html

---

## 🔑 KEY DIFFERENCES FROM PREVIOUS VERSION

- **Removed**: GraphML export via s3Dgraphy (use native PyArchInit GraphML export instead)
- **Updated**: JSON format to s3Dgraphy v1.5 specification
- **Added**: Automatic JSON creation in interactive viewer
- **Improved**: Node categorization (stratigraphic, documents, extractors, combiners)
- **Enhanced**: Edge type organization (is_before, has_same_time, etc.)
