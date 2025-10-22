# Test 3D Models - s3Dgraphy Integration

## Overview

This document describes the test 3D models generated for testing the s3Dgraphy integration in PyArchInit-Mini.

## Generated Models

### Location
```
web_interface/static/uploads/models/Sito Archeologico di Esempio/site/
```

### Files
1. **stratigraphy_test.obj** - Wavefront OBJ format with MTL material file
2. **stratigraphy_test.mtl** - Material library for OBJ model
3. **stratigraphy_test.gltf** - GLTF 2.0 format with embedded vertex colors
4. **stratigraphy_test.bin** - Binary buffer for GLTF model

## Model Structure

Both models represent **10 stratigraphic units (US)** as colored 3D boxes, positioned in 3D space based on:
- **Stratigraphic level** (Y-axis) - Deeper units are lower
- **Area** (X-axis) - Areas A, B, C are separated horizontally
- **Random variation** (Z-axis) - Slight randomization for visual clarity

## Stratigraphic Units (US) in Test Models

| US   | Type              | Area | Period        | EM Color                | RGB           |
|------|-------------------|------|---------------|-------------------------|---------------|
| 1001 | Humus             | A    | Moderno       | Sandy Brown             | (244,163,95)  |
| 1002 | Deposito          | A    | Medievale     | Chocolate               | (210,105,30)  |
| 1003 | Taglio            | A    | Medievale     | Dark Brown              | (138,69,19)   |
| 1004 | Riempimento       | A    | Medievale     | Peru                    | (205,133,62)  |
| 1005 | Pavimento         | B    | Romano        | Steel Blue              | (70,130,180)  |
| 1006 | Muro              | B    | Romano        | Gray                    | (128,128,128) |
| 1007 | Deposito          | B    | Romano        | Chocolate               | (210,105,30)  |
| 1008 | Crollo            | C    | Tardo Antico  | Gold                    | (255,214,0)   |
| 1009 | Costruzione       | C    | Romano        | Light Green             | (144,237,144) |
| 1010 | Terreno arativo   | C    | Moderno       | Sandy Brown             | (244,163,95)  |

## Extended Matrix Color Palette

The models follow the Extended Matrix (EM) standard color palette:

- **Taglio (Cut)**: `#8B4513` - Dark brown
- **Deposito (Deposit)**: `#D2691E` - Chocolate
- **Riempimento (Fill)**: `#CD853F` - Peru
- **Humus/Terreno arativo (Layer)**: `#F4A460` - Sandy brown
- **Muro (Wall)**: `#808080` - Gray
- **Pavimento (Floor)**: `#4682B4` - Steel blue
- **Crollo/Distruzione (Destruction)**: `#FFD700` - Gold
- **Costruzione (Construction)**: `#90EE90` - Light green

## Format Comparison

### OBJ Format
- **Pros**:
  - Simple text format
  - Wide support
  - Separate MTL file for materials
  - Easy to edit manually
- **Cons**:
  - No embedded materials
  - No vertex colors (uses materials instead)
  - Less efficient for web

### GLTF Format
- **Pros**:
  - Modern web-optimized format
  - Embedded vertex colors
  - Binary buffer for efficiency
  - Standard for 3D on web
  - Progressive loading support
- **Cons**:
  - More complex structure
  - Harder to edit manually

## Usage in PyArchInit-Mini

### Loading Models

Both models can be loaded in the 3D Harris Matrix Viewer:

1. Navigate to **Export Harris Matrix** page
2. Select a site and export as s3Dgraphy
3. Click **"Visualizzatore Interattivo"**
4. From the **3D Model** dropdown, select either:
   - `stratigraphy_test.obj`
   - `stratigraphy_test.gltf`

### Model Features

- **Automatic centering and scaling**: Models are centered and scaled to fit the view
- **EM color preservation**:
  - OBJ: Colors loaded from MTL file
  - GLTF: Colors embedded as vertex attributes
- **Interactive viewing**: Orbit, pan, zoom with OrbitControls
- **US markers**: Colored spheres representing each US with Extended Matrix colors
- **Matrix ↔ 3D interaction**: Click nodes in Harris Matrix to focus on corresponding US in 3D

## Generating New Test Models

To regenerate or create new test models:

```bash
python scripts/generate_test_3d_model.py
```

### Customization

Edit the `SAMPLE_US` list in `generate_test_3d_model.py` to:
- Add more stratigraphic units
- Change US types, areas, periods
- Modify positioning logic
- Add different geometries

## Integration with Real Data

When integrating with real archaeological data:

1. **Export from EM Tools**: Export your stratigraphic 3D models as OBJ or GLTF
2. **Upload via Web Interface**: Use the "Upload OBJ/GLTF" button in the viewer
3. **Database coordinates**: Modify `createUSMarkers()` to use real X/Y/Z coordinates from database
4. **Metadata linking**: Ensure US numbers in 3D models match database US records

## File Structure

### OBJ File Structure
```
# Comments
mtllib stratigraphy_test.mtl

g US_1001
v x y z  # Vertices
usemtl Humus
f v1 v2 v3  # Faces
...
```

### GLTF File Structure
```json
{
  "asset": { "version": "2.0" },
  "scene": 0,
  "scenes": [{ "nodes": [0] }],
  "nodes": [{ "mesh": 0 }],
  "meshes": [{
    "primitives": [{
      "attributes": {
        "POSITION": 0,
        "COLOR_0": 1
      },
      "indices": 2
    }]
  }],
  "accessors": [...],
  "bufferViews": [...],
  "buffers": [{ "uri": "stratigraphy_test.bin" }]
}
```

## Viewer Capabilities

The integrated viewer supports:

- ✅ **OBJ loading** with MTL materials
- ✅ **GLTF/GLB loading** with vertex colors
- ✅ **Automatic format detection** based on file extension
- ✅ **Progress indicators** for loading
- ✅ **Error handling** with user feedback
- ✅ **Extended Matrix color palette** for both formats
- ✅ **Interactive Harris Matrix** synchronized with 3D view
- ✅ **US marker system** with color coding

## Next Steps

1. **Real coordinate integration**: Connect US markers to actual excavation coordinates
2. **Texture support**: Add texture loading for OBJ models
3. **GLB support**: Test with binary GLTF (.glb) files
4. **Multi-model support**: Load multiple models simultaneously
5. **Measurement tools**: Add distance/volume measurement in 3D view

## References

- **s3Dgraphy**: Extended Matrix Framework for 3D stratigraphic documentation
- **GLTF Specification**: https://www.khronos.org/gltf/
- **Three.js Loaders**: OBJLoader, GLTFLoader documentation
- **Extended Matrix**: Archaeological 3D documentation standard