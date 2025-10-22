# s3Dgraphy Integration - Guida Completa

**Data**: Ottobre 21, 2025

---

## 📘 COS'È s3Dgraphy?

**s3Dgraphy** è una libreria Python per grafi stratigrafici 3D.

- Knowledge Graph Multitemporale
- Extended Matrix Framework
- Export GraphML, JSON
- Integrazione modelli 3D

---

## 🔧 COME FUNZIONA

PyArchInit integra s3Dgraphy con 3 moduli:

### 1. S3DConverter
Converte US PyArchInit → grafo s3dgraphy

```python
from pyarchinit_mini.s3d_integration import S3DConverter

converter = S3DConverter()
graph = converter.create_graph_from_us(us_list, "Pompei")
converter.export_to_graphml(graph, "pompei.graphml")
```

### 2. Model3DManager
Gestisce modelli 3D (GLB, GLTF, OBJ, PLY, STL, FBX)

```python
from pyarchinit_mini.s3d_integration import Model3DManager

manager = Model3DManager("uploads")
metadata = manager.save_model("scan.glb", us_id="001", site_name="Pompei")
```

### 3. Web Routes
- GET /3d/viewer/<path> - Visualizza 3D
- POST /3d/upload - Upload modello
- GET /3d/export/graphml/<site> - Export GraphML
- GET /3d/export/json/<site> - Export JSON

---

## 📤 COSA RESTITUISCE

### GraphML (XML)
Formato standard per yEd, Gephi, NetworkX

### JSON
Formato leggibile per analisi

---

## 🎯 COME USARLO

### Via Web GUI

1. Menu → Harris Matrix
2. Seleziona sito
3. Click "Export GraphML (s3Dgraphy)"
4. Download file

### Upload 3D

```bash
curl -X POST http://localhost:5000/3d/upload \
  -F "model_file=@scan.glb" \
  -F "site_name=Pompei" \
  -F "us_id=001"
```

### Visualizza 3D

URL: http://localhost:5000/3d/viewer/3d_models/Pompei/US_001/scan.glb

---

## 🔄 DUE TIPI DI GRAPHML

| | Tradizionale | s3Dgraphy |
|---|---|---|
| Route | /harris_matrix/graphml_export | /3d/export/graphml/<site> |
| Metadata | Minimale | Completo |
| 3D | No | Sì |

**Usa s3Dgraphy per**:
- Analisi avanzate
- Metadata completi
- Integrazione 3D
- Extended Matrix standard

---

## ✅ WORKFLOW

1. Crea US nel database
2. Scansiona 3D (fotogrammetria)
3. Upload modelli via API
4. Export GraphML
5. Apri in yEd: Layout → Hierarchical
6. Condividi link 3D

---

## 🆘 TROUBLESHOOTING

```bash
# Installa s3dgraphy
pip install s3dgraphy

# GraphML vuoto: verifica US nel database
# Modello non si carica: usa formato GLB, max 50MB
# Viewer errore: verifica WebGL supportato
```

---

## 📋 API RAPIDO

```python
# Export GraphML
GET /3d/export/graphml/Pompei → Pompei_stratigraphy.graphml

# Upload 3D
POST /3d/upload (model_file, site_name, us_id)

# View 3D
GET /3d/viewer/3d_models/Pompei/US_001/scan.glb

# List models
GET /3d/models/Pompei
```

---

**s3Dgraphy**: https://github.com/zalmoxes-laran/s3dgraphy
**Extended Matrix**: https://www.extendedmatrix.org
