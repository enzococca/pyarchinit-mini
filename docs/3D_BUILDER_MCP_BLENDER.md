# 3D Builder - MCP Blender Integration

## Overview

Sistema integrato per la generazione e visualizzazione interattiva di modelli 3D stratigrafici utilizzando Claude (tramite MCP), Blender e PyArchInit-Mini web GUI.

## Architettura

```
┌─────────────────┐
│  PyArchInit Web │
│   (Frontend)    │
│                 │
│  - Prompt UI    │
│  - 3D Viewer    │
│  - Controls     │
└────────┬────────┘
         │
    WebSocket
         │
┌────────┴────────┐
│  PyArchInit API │
│   (Backend)     │
│                 │
│  - MCP Server   │
│  - GraphML Svc  │
│  - Period Svc   │
└────────┬────────┘
         │
      MCP Protocol
         │
┌────────┴────────┐
│     Claude      │
│   (via MCP)     │
└────────┬────────┘
         │
      MCP Protocol
         │
┌────────┴────────┐
│     Blender     │
│   (MCP Addon)   │
│                 │
│  - 3D Engine    │
│  - Proxy Gen    │
│  - Export       │
└─────────────────┘
```

## Componenti Principali

### 1. MCP Server (PyArchInit-Mini)

**Posizione:** `pyarchinit_mini/mcp_server/`

**Responsabilità:**
- Esporre API MCP per Claude
- Gestire comunicazione con Blender
- Fornire contesto archeologico (GraphML, periodizzazione)
- Coordinare generazione e streaming 3D

**File chiave:**
- `mcp_server.py` - Server principale MCP
- `blender_client.py` - Client per comunicare con Blender
- `stratigraphic_context.py` - Provider dati stratigrafici
- `proxy_mapper.py` - Mapping GraphML → Blender proxies

### 2. Blender Integration

**Addon Blender esistente:** [MCP addon per Blender]

**Estensioni necessarie:**
- Script custom per ricevere dati stratigrafici
- Sistema di tagging proxies con IDs da GraphML
- Export incrementale per streaming
- Gestione layer temporali (periodi)

**File chiave:**
- `blender_addon/pyarchinit_connector.py`
- `blender_addon/stratigraphic_builder.py`
- `blender_addon/streaming_exporter.py`

### 3. Frontend Web Interface

**Posizione:** `pyarchinit_mini/web_interface/templates/3d_builder/`

**UI Components:**

#### 3.1 Prompt Section
```html
┌─────────────────────────────────────────┐
│ 3D Stratigraphic Builder with Claude   │
├─────────────────────────────────────────┤
│                                         │
│  📝 Prompt:                             │
│  ┌─────────────────────────────────┐   │
│  │ "Create a 3D model of the      │   │
│  │  stratigraphic sequence from   │   │
│  │  Site 1, showing US 1-10 with  │   │
│  │  Bronze Age layers..."         │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Generate 3D] [Stop] [Reset]          │
└─────────────────────────────────────────┘
```

#### 3.2 3D Viewer Section
```html
┌─────────────────────────────────────────┐
│ 3D Model Viewer (Streaming)             │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  │   [Three.js 3D Canvas]         │   │
│  │                                 │   │
│  │   - Real-time updates          │   │
│  │   - Interactive rotation       │   │
│  │   - Zoom/Pan                   │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Status: Building layer US 5/10...     │
└─────────────────────────────────────────┘
```

#### 3.3 Controls Panel
```html
┌─────────────────────────────────────────┐
│ 3D Model Controls                       │
├─────────────────────────────────────────┤
│                                         │
│ Visibility:                             │
│  [x] Show all proxies                  │
│  [ ] Show only selected period         │
│                                         │
│ Transparency:                           │
│  ├────────●──────┤ 75%                 │
│                                         │
│ Chronological Filter:                  │
│  Period: [Bronze Age ▼]                │
│  Timeline: ├──●─────────┤              │
│            1200 BCE → 800 BCE          │
│                                         │
│ Layer Selection:                       │
│  [x] US 1  [x] US 2  [ ] US 3          │
│  [x] US 4  [ ] US 5  [x] US 6          │
│                                         │
│ [Export glTF] [Save Scene] [Share]     │
└─────────────────────────────────────────┘
```

#### 3.4 Info Panel (Proxy Details)
```html
┌─────────────────────────────────────────┐
│ Selected Proxy: US 5                    │
├─────────────────────────────────────────┤
│                                         │
│ Stratigraphic Unit: 5                  │
│ Site: Sito Archeologico di Esempio     │
│ Area: 1000                              │
│                                         │
│ Description:                            │
│ Strato di riempimento con ceramica     │
│ frammentaria e materiale edilizio      │
│                                         │
│ Dating:                                 │
│ Period: Bronze Age                      │
│ Dating: 1200-1000 BCE                   │
│                                         │
│ Relationships:                          │
│ ↑ Covers: US 6, US 7                   │
│ ↓ Covered by: US 3, US 4               │
│                                         │
│ [View in GraphML] [Edit US]            │
└─────────────────────────────────────────┘
```

### 4. Data Flow

#### 4.1 Generazione Modello 3D

```
1. User → Prompt
   "Create 3D model showing Bronze Age layers from Site 1"

2. Frontend → Backend API
   POST /api/3d-builder/generate
   {
     "prompt": "...",
     "site_id": 1,
     "include_periods": ["Bronze Age"],
     "graphml_source": "current"
   }

3. Backend → MCP Server → Claude
   - Fornisce contesto (GraphML, US data, periods)
   - Claude interpreta richiesta
   - Genera comandi Blender

4. Claude → Blender (via MCP)
   - Comandi di costruzione 3D
   - Posizionamento proxies
   - Applicazione materiali/colori

5. Blender → Backend (streaming)
   - Export incrementale glTF
   - Metadata associati
   - Progress updates

6. Backend → Frontend (WebSocket)
   - 3D model chunks
   - Progress updates
   - Real-time visualization
```

#### 4.2 Query e Filtri

```
1. User → Controls (filter by period)
   Timeline slider → 1000-800 BCE

2. Frontend → Backend API
   POST /api/3d-builder/filter
   {
     "period_range": ["1000 BCE", "800 BCE"],
     "transparency": 0.75,
     "visible_us": [1, 2, 5, 7]
   }

3. Backend → 3D Scene
   - Applica filtri
   - Aggiorna visibilità
   - Modifica trasparenza

4. Backend → Frontend
   - Updated 3D scene
   - Filtered proxies list
```

## Schema Dati

### GraphML Node → Blender Proxy Mapping

```json
{
  "proxy_id": "proxy_us_5",
  "us_id": 5,
  "graphml_node_id": "n5",
  "stratigraphic_data": {
    "site": "Sito Archeologico di Esempio",
    "area": "1000",
    "us": 5,
    "description": "Strato di riempimento...",
    "interpretation": "Deposit layer"
  },
  "chronology": {
    "period_id": 2,
    "period_name": "Bronze Age",
    "dating_start": -1200,
    "dating_end": -1000,
    "phase": "Middle Bronze Age"
  },
  "relationships": {
    "covers": [6, 7],
    "covered_by": [3, 4],
    "equals": [],
    "cuts": [],
    "cut_by": []
  },
  "blender_properties": {
    "location": [0.0, 0.0, -5.0],
    "scale": [2.0, 2.0, 0.5],
    "color": [0.8, 0.6, 0.4, 1.0],
    "material": "soil_material"
  },
  "visualization": {
    "visible": true,
    "transparency": 0.0,
    "highlight": false,
    "layer": "bronze_age"
  }
}
```

### API Endpoints

#### POST /api/3d-builder/generate
```json
Request:
{
  "prompt": "Create 3D stratigraphic model...",
  "site_id": 1,
  "graphml_id": 15,
  "include_periods": ["Bronze Age", "Iron Age"],
  "options": {
    "auto_position": true,
    "apply_colors": true,
    "scale_by_depth": true
  }
}

Response:
{
  "success": true,
  "session_id": "3d_build_12345",
  "websocket_url": "ws://localhost:5001/3d-stream/12345",
  "estimated_duration": 30
}
```

#### WebSocket /3d-stream/{session_id}

**Messages from server:**
```json
{
  "type": "progress",
  "message": "Building US 5...",
  "progress": 50,
  "current_us": 5,
  "total_us": 10
}

{
  "type": "model_chunk",
  "data": "base64_encoded_gltf_chunk",
  "proxies": [
    {
      "proxy_id": "proxy_us_5",
      "us_id": 5,
      "position": [0, 0, -5]
    }
  ]
}

{
  "type": "complete",
  "model_url": "/static/3d_models/session_12345.gltf",
  "total_proxies": 10,
  "metadata": {...}
}
```

#### POST /api/3d-builder/filter
```json
Request:
{
  "session_id": "3d_build_12345",
  "filters": {
    "period_range": {
      "start": -1200,
      "end": -800
    },
    "visible_us": [1, 2, 5, 7, 9],
    "transparency": 0.75,
    "highlight_us": [5]
  }
}

Response:
{
  "success": true,
  "updated_proxies": 10,
  "visible_count": 5,
  "hidden_count": 5
}
```

#### GET /api/3d-builder/proxy/{proxy_id}
```json
Response:
{
  "proxy_id": "proxy_us_5",
  "us_data": {
    "id_us": 5,
    "sito": "...",
    "area": "...",
    "us": 5,
    "d_stratigrafica": "...",
    "interpretazione": "..."
  },
  "chronology": {
    "period": "Bronze Age",
    "dating": "1200-1000 BCE"
  },
  "relationships": [...],
  "media": [
    {
      "id": 1,
      "type": "image",
      "filename": "us5_photo.jpg"
    }
  ]
}
```

## Tecnologie

### Backend
- **MCP Server**: Python con `mcp` library
- **Blender Communication**: JSON-RPC o REST API
- **WebSocket**: Flask-SocketIO per streaming
- **GraphML Parser**: `networkx` per parsing

### Frontend
- **3D Viewer**: Three.js con GLTFLoader
- **UI Framework**: Bootstrap 5
- **Real-time Updates**: Socket.IO client
- **Controls**: HTML5 range sliders, checkboxes

### Blender
- **MCP Addon**: Addon esistente per Blender
- **Python API**: bpy per scripting
- **Export**: glTF 2.0 format
- **Streaming**: Export incrementale chunks

## Timeline di Sviluppo

### Phase 1: Research & Design (1-2 settimane)
- Studiare MCP protocol
- Analizzare Blender MCP addon
- Progettare architettura
- Definire schema dati

### Phase 2: Backend Foundation (2-3 settimane)
- Implementare MCP server
- Creare Blender client
- Parser GraphML
- Sistema di mapping

### Phase 3: Frontend Development (2-3 settimane)
- UI components
- 3D viewer con Three.js
- WebSocket integration
- Controls panel

### Phase 4: Integration (2 settimane)
- End-to-end testing
- Blender addon configuration
- Streaming optimization
- Bug fixing

### Phase 5: Polish & Documentation (1 settimana)
- Performance tuning
- Documentazione tecnica
- Tutorial utente
- Demo video

**Totale stimato: 8-11 settimane**

## Rischi e Mitigazioni

### Rischi Tecnici

1. **Latenza streaming 3D**
   - Mitigazione: Chunked export, WebGL optimization

2. **Sincronizzazione Blender-Web**
   - Mitigazione: WebSocket con acknowledgments

3. **Complessità MCP protocol**
   - Mitigazione: Studio approfondito, testing incrementale

4. **Performance con molti proxies**
   - Mitigazione: LOD (Level of Detail), culling, batching

### Rischi di Progetto

1. **Complessità integrazione**
   - Mitigazione: Development iterativo, MVP first

2. **Curva apprendimento MCP**
   - Mitigazione: Documentazione, esempi, community

## Success Criteria

✅ **MVP (Minimum Viable Product):**
- Generare modello 3D semplice da prompt
- Visualizzare in web GUI
- Associare almeno 5 US a proxies
- Filtro base per periodo

✅ **Full Release:**
- Tutti i 23 tasks completati
- Streaming real-time funzionante
- Tutti i controlli interattivi operativi
- Documentazione completa
- Performance < 2s per update

## Next Steps

1. ✅ TODO list creata (23 tasks)
2. ⏳ Research MCP protocol
3. ⏳ Analisi Blender MCP addon
4. ⏳ Setup development environment
5. ⏳ Implementazione MCP server (primo componente)

## References

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Blender Python API](https://docs.blender.org/api/current/)
- [Three.js Documentation](https://threejs.org/docs/)
- [glTF 2.0 Specification](https://www.khronos.org/gltf/)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
