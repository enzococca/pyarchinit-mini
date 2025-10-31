# GraphML Node → Blender Proxy Mapping Schema

**Data creazione:** 31 Ottobre 2025
**Versione:** 1.0
**Scopo:** Definire lo schema di associazione tra nodi GraphML (US stratigrafiche) e proxy 3D Blender

---

## 1. Overview

Questo documento definisce la struttura dati e le regole di mapping per associare:
- **Source**: Nodi GraphML contenenti dati stratigrafici
- **Target**: Proxy objects 3D in Blender
- **Link**: Metadata strutturati per interrogazione, filtering, visualizzazione

### Obiettivi

1. **Tracciabilità**: Ogni proxy Blender deve essere univocamente associato a un nodo GraphML
2. **Bi-direzionalità**: Possibilità di query da GraphML → Proxy e da Proxy → GraphML
3. **Ricchezza informativa**: Preservare tutti i metadata archeologici
4. **Estensibilità**: Schema flessibile per futuri attributi

---

## 2. Core Mapping Structure

### 2.1 Proxy Metadata Object

```json
{
  "proxy_id": "proxy_us_<us_id>",
  "us_id": <integer>,
  "graphml_node_id": "<node_id>",
  "site_id": <integer>,
  "build_session_id": "<uuid>",
  "created_at": "<ISO8601 timestamp>",

  "stratigraphic_data": {
    // Sezione 2.2
  },

  "chronology": {
    // Sezione 2.3
  },

  "relationships": {
    // Sezione 2.4
  },

  "blender_properties": {
    // Sezione 2.5
  },

  "visualization": {
    // Sezione 2.6
  },

  "media": {
    // Sezione 2.7
  }
}
```

### 2.2 Stratigraphic Data

Dati archeologici estratti da `us_table` e GraphML node attributes.

```json
"stratigraphic_data": {
  "sito": "Sito Archeologico di Esempio",
  "area": "1000",
  "us": 5,
  "definizione_stratigrafica": "Strato",
  "descrizione": "Strato di riempimento con ceramica frammentaria e materiale edilizio",
  "interpretazione": "Deposit layer",
  "formazione": "Naturale",
  "modo_formazione": "Accumulo graduale",
  "consistenza": "Compatta",
  "colore": "Marrone scuro",
  "inclusi": "Ceramica, laterizi, carboni",
  "unita_tipo": "US",
  "settore": "A",
  "quad_par": "Q1",
  "ambient": "Ambiente 1",
  "quota_min": 12.50,
  "quota_max": 12.85,
  "lunghezza_max": 2.5,
  "altezza_max": 0.35,
  "altezza_min": 0.20,
  "profondita_max": 1.8,
  "profondita_min": 1.5,
  "larghezza_media": 2.0
}
```

**Source Mapping:**
- Database: `us_table` tramite `us_id`
- GraphML attributes: `label`, `description`, `formation`, `interpretation`, `unita_tipo`

### 2.3 Chronology

Dati di periodizzazione estratti da `periodizzazione_table` e `datazioni_table`.

```json
"chronology": {
  "period_id": 2,
  "period_name": "Bronze Age",
  "period_code": "BA",
  "fase": "Middle Bronze Age",
  "datazione_estesa": "1200-1000 BCE",
  "dating_start": -1200,
  "dating_end": -1000,
  "cron_iniziale": 0,
  "cron_finale": 1,
  "affidabilita": "Alta",
  "motivazione": "Ceramica tipologica",
  "cronologia_relativa": "Post-deposizionale"
}
```

**Source Mapping:**
- `periodizzazione_table`: JOIN su `sito`, `area`, `us`
- `datazioni_table`: Periodo associato tramite `periodo` field
- GraphML attributes: `period` (se presente)

**Conversion Rules:**
- BCE dates: negative integers (`-1200` = 1200 BCE)
- CE dates: positive integers (`500` = 500 CE)
- `cron_iniziale`/`cron_finale`: Ordinamento relativo (0, 1, 2, ...)

### 2.4 Relationships

Relazioni stratigrafiche estratte da GraphML edges.

```json
"relationships": {
  "covers": [6, 7, 10],
  "covered_by": [3, 4],
  "fills": [],
  "filled_by": [],
  "cuts": [8],
  "cut_by": [],
  "equals": [],
  "contemporaneous_with": []
}
```

**Source Mapping:**
- GraphML edges con attributo `relationship`
- Valori possibili:
  - `covers` / `covered_by`
  - `fills` / `filled_by`
  - `cuts` / `cut_by`
  - `equals`
  - `contemporaneous_with`

**Bidirectional Inference:**
Se edge `US5 --covers--> US6`, allora:
- US5: `"covers": [6]`
- US6: `"covered_by": [5]`

### 2.5 Blender Properties

Proprietà 3D del proxy object in Blender.

```json
"blender_properties": {
  "object_name": "Proxy_US_5",
  "object_type": "MESH",
  "geometry": "CUBE",
  "location": {
    "x": 0.0,
    "y": 0.0,
    "z": -5.0
  },
  "rotation": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0
  },
  "scale": {
    "x": 2.0,
    "y": 2.0,
    "z": 0.35
  },
  "material": {
    "name": "Bronze_Age_Soil",
    "base_color": [0.8, 0.6, 0.4, 1.0],
    "roughness": 0.7,
    "metallic": 0.0,
    "alpha": 1.0
  },
  "layer": "bronze_age",
  "collection": "Site_1_Stratigraphy",
  "parent": null
}
```

**Generation Rules:**

#### Location (Z-axis positioning)
- **Algoritmo stratigrafico**:
  - Z = 0 per la US più antica (bottom)
  - Z incrementa per ogni layer superiore
  - Spacing: 0.5 Blender units per layer
  - Formula: `z = (max_depth - us_depth) * layer_spacing`

#### Scale
- **X/Y**: Basato su `larghezza_media`, `lunghezza_max` (se disponibili)
- **Z**: Basato su `altezza_max` - `altezza_min`
- **Normalizzazione**: Scale relative tra proxies

#### Material & Color
- **Color mapping da periodo**:
  ```python
  PERIOD_COLORS = {
      "Paleolithic": [0.6, 0.5, 0.4, 1.0],      # Grigio-bruno
      "Neolithic": [0.7, 0.6, 0.3, 1.0],        # Giallo-bruno
      "Bronze Age": [0.8, 0.6, 0.4, 1.0],       # Arancio-bruno
      "Iron Age": [0.5, 0.4, 0.3, 1.0],         # Bruno scuro
      "Roman": [0.8, 0.2, 0.2, 1.0],            # Rosso mattone
      "Medieval": [0.4, 0.4, 0.5, 1.0],         # Grigio
      "Modern": [0.3, 0.3, 0.3, 1.0],           # Grigio scuro
      "Unknown": [0.5, 0.5, 0.5, 0.5]           # Grigio trasparente
  }
  ```

- **Material naming**: `{period_name}_{formation_type}`
  - Example: `Bronze_Age_Soil`, `Roman_Fill`, `Medieval_Cut`

#### Layer Assignment
- **Layer name** = `period_code.lower()` (e.g., "ba", "ia", "rom")
- **Purpose**: Permette show/hide per periodo in Blender

#### Collection
- **Naming**: `Site_{site_id}_Stratigraphy`
- **Hierarchy**:
  ```
  Scene
  └─ Site_1_Stratigraphy
      ├─ Paleolithic (Collection)
      ├─ Bronze_Age (Collection)
      │   ├─ Proxy_US_5
      │   ├─ Proxy_US_6
      │   └─ Proxy_US_7
      └─ Iron_Age (Collection)
  ```

### 2.6 Visualization State

Stato di visualizzazione del proxy nella web GUI.

```json
"visualization": {
  "visible": true,
  "opacity": 1.0,
  "highlight": false,
  "selected": false,
  "color_override": null,
  "wireframe": false,
  "bounding_box": false,
  "label_visible": true,
  "label_text": "US 5 - Bronze Age"
}
```

**Purpose:**
- Gestire filtri interattivi (period filter, transparency slider)
- Highlighting su selezione
- Override temporanei di colore (e.g., search results)

**State Management:**
- Initial state: Tutti visibili, opacity 1.0, no highlight
- Updated via WebSocket messages da Frontend
- Synced back to Blender per rendering updates

### 2.7 Media References

Collegamenti a media associati (foto, documenti, 3D scans).

```json
"media": [
  {
    "media_id": 42,
    "media_name": "US5_Photo_001.jpg",
    "media_type": "image",
    "media_path": "/uploads/sites/1/us/5/US5_Photo_001.jpg",
    "thumbnail_path": "/uploads/sites/1/us/5/thumbs/US5_Photo_001_thumb.jpg",
    "description": "Vista generale dello strato US 5",
    "tags": ["stratigrafia", "ceramica"],
    "created_at": "2025-10-15T14:30:00Z"
  },
  {
    "media_id": 43,
    "media_name": "US5_3D_Scan.ply",
    "media_type": "3d_model",
    "media_path": "/uploads/sites/1/us/5/US5_3D_Scan.ply",
    "description": "Scansione 3D dello strato",
    "tags": ["3d", "scan"],
    "created_at": "2025-10-16T09:15:00Z"
  }
]
```

**Source Mapping:**
- `media_table`: JOIN su `entity_type = 'us'` AND `id_entity = us_id`

**Purpose:**
- Display in info panel when proxy is selected
- Link to media viewer
- Integrate 3D scans into Blender scene (future feature)

---

## 3. Spatial Positioning Algorithms

### 3.1 Z-Axis (Vertical) Positioning

**Algoritmo di ordinamento stratigrafico:**

```python
def calculate_z_position(us_id: int, graph: nx.DiGraph, layer_spacing: float = 0.5) -> float:
    """
    Calcola la posizione Z di un proxy basata sulla sequenza stratigrafica.

    Args:
        us_id: ID della US
        graph: GraphML graph con edges stratigrafici
        layer_spacing: Distanza verticale tra layer (Blender units)

    Returns:
        Coordinata Z in Blender space
    """
    # 1. Topological sort per ottenere ordinamento bottom-up
    topo_order = nx.topological_sort(graph)
    us_nodes = [node for node in topo_order]

    # 2. Assegna depth level (0 = più antico/bottom)
    depth_levels = {}
    for idx, node in enumerate(us_nodes):
        depth_levels[node] = idx

    # 3. Calcola Z position
    us_depth = depth_levels.get(f"US{us_id}", 0)
    max_depth = len(us_nodes) - 1

    # Z = 0 per bottom, cresce verso l'alto
    z_position = (max_depth - us_depth) * layer_spacing

    return z_position
```

**Example:**
```
US10 (top)      → depth_level = 9 → Z = 0.0
US9             → depth_level = 8 → Z = 0.5
US8             → depth_level = 7 → Z = 1.0
...
US1 (bottom)    → depth_level = 0 → Z = 4.5
```

### 3.2 X-Y (Horizontal) Positioning

**Opzione A: Grid-based (default)**

```python
def calculate_xy_position_grid(us_id: int, site_proxies: List[int], grid_spacing: float = 3.0) -> Tuple[float, float]:
    """
    Dispone proxies su griglia regolare per leggibilità.
    """
    index = site_proxies.index(us_id)
    cols = math.ceil(math.sqrt(len(site_proxies)))

    x = (index % cols) * grid_spacing
    y = (index // cols) * grid_spacing

    return (x, y)
```

**Opzione B: GraphML-based (preserve visual layout)**

```python
def calculate_xy_position_graphml(us_id: int, graphml_data: Dict) -> Tuple[float, float]:
    """
    Usa coordinate dal GraphML se disponibili (yEd geometry).
    """
    node = graphml_data['nodes'].get(f"US{us_id}")
    if node and 'position' in node:
        # Scala coordinate GraphML (pixel) a Blender units
        x = node['position']['x'] * 0.01  # 100 px = 1 Blender unit
        y = node['position']['y'] * 0.01
        return (x, y)
    else:
        return calculate_xy_position_grid(us_id, ...)
```

**Opzione C: Relationship-based (organic layout)**

```python
def calculate_xy_position_force_directed(graph: nx.DiGraph, us_id: int) -> Tuple[float, float]:
    """
    Usa force-directed layout (NetworkX spring_layout).
    """
    pos = nx.spring_layout(graph, k=2.0, iterations=50)
    x, y = pos.get(f"US{us_id}", (0, 0))
    return (x * 10.0, y * 10.0)  # Scala a Blender units
```

**Default strategy:**
1. Prova GraphML positions (se disponibili e valide)
2. Fallback a Grid-based se GraphML mancante
3. Opzione Force-directed abilitabile via config

### 3.3 Scale Calculation

```python
def calculate_proxy_scale(us_data: Dict) -> Dict[str, float]:
    """
    Calcola scale X, Y, Z da dimensioni US.
    """
    # Default scale (se dimensioni non disponibili)
    default_scale = {"x": 1.0, "y": 1.0, "z": 0.3}

    # Estrai dimensioni
    lunghezza = us_data.get('lunghezza_max')
    larghezza = us_data.get('larghezza_media')
    altezza = us_data.get('altezza_max', 0) - us_data.get('altezza_min', 0)

    if not all([lunghezza, larghezza, altezza]):
        return default_scale

    # Normalizza a Blender units (1 metro = 1 Blender unit)
    scale_x = larghezza
    scale_y = lunghezza
    scale_z = max(altezza, 0.1)  # Min 0.1 per evitare proxies piatti

    return {"x": scale_x, "y": scale_y, "z": scale_z}
```

---

## 4. Period-Based Material Mapping

### 4.1 Material Library Structure

```json
{
  "materials": [
    {
      "name": "Bronze_Age_Soil",
      "period": "Bronze Age",
      "formation_type": "Naturale",
      "base_color": [0.8, 0.6, 0.4, 1.0],
      "roughness": 0.7,
      "metallic": 0.0,
      "normal_map": null,
      "description": "Terreno compatto epoca bronzo"
    },
    {
      "name": "Roman_Fill",
      "period": "Roman",
      "formation_type": "Riempimento",
      "base_color": [0.8, 0.2, 0.2, 1.0],
      "roughness": 0.6,
      "metallic": 0.0,
      "normal_map": "textures/brick_normal.png",
      "description": "Riempimento con laterizi romani"
    }
  ]
}
```

### 4.2 Material Assignment Logic

```python
def assign_material(period_name: str, formation_type: str, material_library: Dict) -> str:
    """
    Assegna material name a proxy basato su periodo e formazione.

    Returns:
        Material name da applicare in Blender
    """
    # 1. Cerca exact match
    material_name = f"{period_name}_{formation_type}".replace(" ", "_")
    if material_exists(material_library, material_name):
        return material_name

    # 2. Fallback a periodo solo
    period_material = f"{period_name}_Generic".replace(" ", "_")
    if material_exists(material_library, period_material):
        return period_material

    # 3. Fallback finale
    return "Default_Stratigraphic"
```

---

## 5. Data Storage & Persistence

### 5.1 Database Schema Extension

**Nuova tabella: `proxy_mapping`**

```sql
CREATE TABLE proxy_mapping (
    id SERIAL PRIMARY KEY,
    proxy_id VARCHAR(50) UNIQUE NOT NULL,
    us_id INTEGER NOT NULL REFERENCES us_table(id_us),
    graphml_node_id VARCHAR(100),
    build_session_id UUID NOT NULL,
    blender_object_name VARCHAR(200),

    -- 3D Properties (JSON)
    location JSONB,          -- {"x": 0, "y": 0, "z": 0}
    rotation JSONB,
    scale JSONB,
    material_name VARCHAR(100),
    layer_name VARCHAR(100),

    -- Visualization State (JSON)
    visualization_state JSONB,  -- {"visible": true, "opacity": 1.0, ...}

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_us FOREIGN KEY (us_id) REFERENCES us_table(id_us) ON DELETE CASCADE
);

CREATE INDEX idx_proxy_mapping_us_id ON proxy_mapping(us_id);
CREATE INDEX idx_proxy_mapping_session ON proxy_mapping(build_session_id);
CREATE INDEX idx_proxy_mapping_graphml ON proxy_mapping(graphml_node_id);
```

**Nuova tabella: `build_sessions`**

```sql
CREATE TABLE build_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id INTEGER NOT NULL REFERENCES site_table(id_sito),
    graphml_id INTEGER REFERENCES extended_matrix_table(id),

    prompt TEXT,
    generated_by VARCHAR(50) DEFAULT 'Claude',

    total_proxies INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'building',  -- building, completed, failed

    -- glTF Export
    model_url VARCHAR(500),
    thumbnail_url VARCHAR(500),

    -- Filters applied
    period_filters JSONB,
    us_filters JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,

    CONSTRAINT fk_site FOREIGN KEY (site_id) REFERENCES site_table(id_sito) ON DELETE CASCADE
);

CREATE INDEX idx_build_sessions_site ON build_sessions(site_id);
CREATE INDEX idx_build_sessions_status ON build_sessions(status);
```

### 5.2 JSON Export Format

Per caching e transfer a Blender:

**File: `{build_session_id}_proxies.json`**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "site_id": 1,
  "graphml_id": 15,
  "created_at": "2025-10-31T10:30:00Z",
  "proxies": [
    {
      "proxy_id": "proxy_us_5",
      "us_id": 5,
      "graphml_node_id": "n5",
      "stratigraphic_data": { ... },
      "chronology": { ... },
      "relationships": { ... },
      "blender_properties": { ... },
      "visualization": { ... },
      "media": [ ... ]
    },
    ...
  ],
  "statistics": {
    "total_proxies": 10,
    "periods": {
      "Bronze Age": 5,
      "Iron Age": 3,
      "Roman": 2
    },
    "relationships": {
      "covers": 15,
      "cuts": 2
    }
  }
}
```

---

## 6. API Contracts

### 6.1 Generate Proxies Metadata

**Endpoint:** `POST /api/3d-builder/generate-proxy-metadata`

**Request:**
```json
{
  "site_id": 1,
  "graphml_id": 15,
  "us_ids": [5, 6, 7],
  "options": {
    "positioning": "graphml",  // "graphml" | "grid" | "force_directed"
    "material_source": "period",  // "period" | "formation" | "custom"
    "layer_grouping": "period",  // "period" | "area" | "none"
    "scale_mode": "actual"  // "actual" | "normalized"
  }
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "proxies": [ ... ],  // Array di proxy metadata
  "export_path": "/tmp/session_550e8400_proxies.json",
  "statistics": { ... }
}
```

### 6.2 Query Proxy by US ID

**Endpoint:** `GET /api/3d-builder/proxy/{us_id}`

**Response:**
```json
{
  "proxy_id": "proxy_us_5",
  "us_id": 5,
  "stratigraphic_data": { ... },
  "chronology": { ... },
  "relationships": { ... },
  "blender_properties": { ... },
  "visualization": { ... },
  "media": [ ... ]
}
```

### 6.3 Update Visualization State

**Endpoint:** `PATCH /api/3d-builder/proxy/{proxy_id}/visualization`

**Request:**
```json
{
  "visible": true,
  "opacity": 0.5,
  "highlight": false
}
```

**Response:**
```json
{
  "success": true,
  "proxy_id": "proxy_us_5",
  "visualization": {
    "visible": true,
    "opacity": 0.5,
    "highlight": false,
    "selected": false,
    "color_override": null,
    "wireframe": false,
    "bounding_box": false,
    "label_visible": true,
    "label_text": "US 5 - Bronze Age"
  }
}
```

---

## 7. Example: Complete Proxy Metadata

```json
{
  "proxy_id": "proxy_us_1005",
  "us_id": 1005,
  "graphml_node_id": "n1005",
  "site_id": 1,
  "build_session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-10-31T10:35:22Z",

  "stratigraphic_data": {
    "sito": "Sito Archeologico di Esempio",
    "area": "1000",
    "us": 1005,
    "definizione_stratigrafica": "Strato",
    "descrizione": "Strato di accumulo con ceramica attica a figure rosse e monete repubblicane",
    "interpretazione": "Deposit layer - Living surface",
    "formazione": "Antropica",
    "modo_formazione": "Accumulo graduale",
    "consistenza": "Compatta",
    "colore": "Rosso-bruno",
    "inclusi": "Ceramica fine, monete, ossa animali",
    "unita_tipo": "US",
    "settore": "A",
    "quad_par": "Q5",
    "ambient": "Ambiente 3",
    "quota_min": 15.20,
    "quota_max": 15.45,
    "lunghezza_max": 3.2,
    "altezza_max": 0.25,
    "altezza_min": 0.20,
    "profondita_max": 2.5,
    "profondita_min": 2.25,
    "larghezza_media": 2.8
  },

  "chronology": {
    "period_id": 5,
    "period_name": "Roman",
    "period_code": "ROM",
    "fase": "Late Republic",
    "datazione_estesa": "150-50 BCE",
    "dating_start": -150,
    "dating_end": -50,
    "cron_iniziale": 3,
    "cron_finale": 4,
    "affidabilita": "Alta",
    "motivazione": "Ceramica tipologica + numismatica",
    "cronologia_relativa": "Coevo a US 1004"
  },

  "relationships": {
    "covers": [1006, 1007, 1010],
    "covered_by": [1003, 1004],
    "fills": [],
    "filled_by": [],
    "cuts": [],
    "cut_by": [1002],
    "equals": [],
    "contemporaneous_with": [1004]
  },

  "blender_properties": {
    "object_name": "Proxy_US_1005",
    "object_type": "MESH",
    "geometry": "CUBE",
    "location": {
      "x": 6.0,
      "y": 9.0,
      "z": 1.5
    },
    "rotation": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.0
    },
    "scale": {
      "x": 2.8,
      "y": 3.2,
      "z": 0.23
    },
    "material": {
      "name": "Roman_Living_Surface",
      "base_color": [0.8, 0.2, 0.2, 1.0],
      "roughness": 0.6,
      "metallic": 0.0,
      "alpha": 1.0
    },
    "layer": "roman",
    "collection": "Site_1_Stratigraphy",
    "parent": null
  },

  "visualization": {
    "visible": true,
    "opacity": 1.0,
    "highlight": false,
    "selected": false,
    "color_override": null,
    "wireframe": false,
    "bounding_box": false,
    "label_visible": true,
    "label_text": "US 1005 - Roman (150-50 BCE)"
  },

  "media": [
    {
      "media_id": 127,
      "media_name": "US1005_General_View.jpg",
      "media_type": "image",
      "media_path": "/uploads/sites/1/us/1005/US1005_General_View.jpg",
      "thumbnail_path": "/uploads/sites/1/us/1005/thumbs/US1005_General_View_thumb.jpg",
      "description": "Vista generale dello strato con ceramica in situ",
      "tags": ["stratigrafia", "ceramica", "attica"],
      "created_at": "2025-10-20T14:30:00Z"
    },
    {
      "media_id": 128,
      "media_name": "US1005_Pottery_Detail.jpg",
      "media_type": "image",
      "media_path": "/uploads/sites/1/us/1005/US1005_Pottery_Detail.jpg",
      "thumbnail_path": "/uploads/sites/1/us/1005/thumbs/US1005_Pottery_Detail_thumb.jpg",
      "description": "Dettaglio ceramica attica a figure rosse",
      "tags": ["ceramica", "attica", "figure_rosse"],
      "created_at": "2025-10-20T15:45:00Z"
    },
    {
      "media_id": 129,
      "media_name": "US1005_Coins.pdf",
      "media_type": "document",
      "media_path": "/uploads/sites/1/us/1005/US1005_Coins.pdf",
      "thumbnail_path": "/uploads/sites/1/us/1005/thumbs/US1005_Coins_thumb.png",
      "description": "Catalogo monete repubblicane rinvenute",
      "tags": ["numismatica", "monete", "repubblica"],
      "created_at": "2025-10-21T09:15:00Z"
    }
  ]
}
```

---

## 8. Validation Rules

### 8.1 Required Fields

**Mandatory per ogni proxy:**
- `proxy_id` (unique)
- `us_id` (existing in `us_table`)
- `build_session_id` (existing in `build_sessions`)
- `blender_properties.object_name` (unique in Blender scene)
- `blender_properties.location` (complete x, y, z)
- `blender_properties.scale` (complete x, y, z)

### 8.2 Consistency Checks

1. **Relationship bidirectionality:**
   - If US_A covers US_B, then US_B must have covered_by US_A

2. **Period coherence:**
   - `chronology.dating_start` < `chronology.dating_end`
   - `cron_iniziale` <= `cron_finale`

3. **Spatial coherence:**
   - Z-position: US coperte devono avere Z maggiore di US che coprono
   - Scale: No negative values

4. **Reference integrity:**
   - `us_id` exists in `us_table`
   - `period_id` (if present) exists in `datazioni_table`
   - `media.media_id` exists in `media_table`

### 8.3 Validation Function

```python
def validate_proxy_metadata(proxy: Dict) -> Tuple[bool, List[str]]:
    """
    Valida metadata di un proxy.

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    # Required fields
    required = ['proxy_id', 'us_id', 'build_session_id', 'blender_properties']
    for field in required:
        if field not in proxy:
            errors.append(f"Missing required field: {field}")

    # Blender properties
    if 'blender_properties' in proxy:
        bp = proxy['blender_properties']
        if 'location' not in bp or not all(k in bp['location'] for k in ['x', 'y', 'z']):
            errors.append("Invalid location: must have x, y, z")
        if 'scale' in bp:
            if any(bp['scale'][k] <= 0 for k in ['x', 'y', 'z']):
                errors.append("Scale values must be positive")

    # Chronology coherence
    if 'chronology' in proxy:
        chron = proxy['chronology']
        if 'dating_start' in chron and 'dating_end' in chron:
            if chron['dating_start'] > chron['dating_end']:
                errors.append("dating_start must be <= dating_end")

    # Relationships (basic check)
    if 'relationships' in proxy:
        rel = proxy['relationships']
        for key in rel:
            if not isinstance(rel[key], list):
                errors.append(f"Relationship '{key}' must be a list")

    return (len(errors) == 0, errors)
```

---

## 9. Migration Strategy

### 9.1 Existing Data

Per dataset esistenti senza mapping:
1. **Generazione batch**: Script per generare proxy metadata da tutti i siti
2. **Defaults intelligenti**: Usa positioning grid se GraphML positions non disponibili
3. **Period inference**: Se periodizzazione mancante, usa "Unknown" period
4. **Material fallback**: Material generico se periodo non mappato

### 9.2 Retrocompatibilità

- GraphML files esistenti continuano a funzionare per Harris Matrix 2D
- Mapping è opt-in: 3D Builder genera mapping solo quando richiesto
- Database backward compatible: Tabelle `proxy_mapping` e `build_sessions` sono additive

---

## 10. Future Extensions

### 10.1 Advanced Features (Phase 2+)

1. **3D Scan Integration:**
   - Import di scansioni 3D reali
   - Sostituzione di proxy con mesh realistiche
   - Alignment automatico basato su coordinate

2. **Temporal Animation:**
   - Animazione sequenza stratigrafica (bottom-up/top-down)
   - Keyframing per mostrare scavo progressivo
   - Export video MP4

3. **AR/VR Export:**
   - glTF export con metadata per AR
   - WebXR integration
   - Oculus/HoloLens compatible scenes

4. **AI-Generated Geometry:**
   - Claude genera forme custom basate su descrizione
   - Textures procedurali
   - Realistic terrain deformation

### 10.2 Community Contributions

Schema è estensibile tramite:
- `custom_attributes` field in metadata
- Plugin system per positioning algorithms
- Material library community-contributed

---

## 11. References

- **GraphML Spec**: http://graphml.graphdrawing.org/
- **Blender Python API**: https://docs.blender.org/api/current/
- **glTF 2.0**: https://www.khronos.org/gltf/
- **NetworkX**: https://networkx.org/documentation/stable/
- **MCP Protocol**: https://modelcontextprotocol.io/

---

**Fine Documento**

**Status:** ✅ Completato
**Prossimo step:** Implementazione parser GraphML e generatore proxy metadata
