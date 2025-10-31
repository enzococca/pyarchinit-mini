# MCP & Blender Integration Research

**Data ricerca:** 31 Ottobre 2025
**Scopo:** Analisi tecnica per integrazione 3D Builder in PyArchInit-Mini

---

## 1. Model Context Protocol (MCP)

### Overview

**Sviluppatore:** Anthropic
**Release:** Novembre 2024
**Tipo:** Open standard, open source framework
**Scopo:** Standardizzare integrazione AI systems con external tools e data sources

### Status 2025

- ✅ **Marzo 2025**: OpenAI adotta ufficialmente MCP
- ✅ **Aprile 2025**: Google DeepMind conferma supporto MCP in Gemini models
- ✅ **Agosto 2025**: Adozione massiva nel settore AI

### Architettura Tecnica

#### Protocollo Base

**Formato:** JSON-RPC messages
**Transport:** TCP sockets (default), può supportare altri transport layers
**Schema:** Definito in TypeScript, disponibile anche come JSON Schema

#### Primitives

**Server Primitives (3):**
1. **Prompts** - Template di conversazione predefiniti
2. **Resources** - Dati/contesto da fornire al model
3. **Tools** - Funzioni eseguibili dal model

**Client Primitives (2):**
1. **Roots** - Directory o source roots
2. **Sampling** - Richieste di generazione al model

### SDKs Disponibili

- ✅ Python
- ✅ TypeScript
- ✅ C#
- ✅ Java

### Documentazione

- **Sito ufficiale:** https://modelcontextprotocol.io
- **GitHub Org:** https://github.com/modelcontextprotocol
- **Specifica:** https://github.com/modelcontextprotocol/specification
- **Claude Docs:** https://docs.claude.com/en/docs/mcp

---

## 2. Blender MCP Addon

### Overview

**Sviluppatore:** Siddharth Ahuja (ahujasid)
**Repository:** https://github.com/ahujasid/blender-mcp
**Stars:** ~13,000
**Forks:** ~1,200
**License:** MIT
**Ultimo update:** Agosto 2025

### Descrizione

Connessione diretta tra Claude AI e Blender tramite MCP, permettendo controllo AI di Blender mediante linguaggio naturale.

### Architettura

```
┌─────────────┐
│   Claude    │
│   Desktop   │
└──────┬──────┘
       │ MCP Protocol
       │ (JSON-RPC)
┌──────┴──────┐
│ MCP Server  │
│ (Python)    │
│             │
│ uvx blender │
│    -mcp     │
└──────┬──────┘
       │ TCP Socket
       │ (JSON msgs)
┌──────┴──────┐
│  Blender    │
│  Addon      │
│             │
│ Socket Svr  │
│ Port 9876   │
└─────────────┘
```

### Componenti

#### 1. MCP Server (`src/blender_mcp/server.py`)

**Funzione:** Implementa MCP spec, bridge tra Claude e Blender

**Comunicazione:**
- **Input:** Comandi MCP da Claude (JSON-RPC)
- **Output:** JSON messages to Blender socket

**Configurazione:**
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

#### 2. Blender Addon (`addon.py`)

**Funzione:** Socket server interno a Blender

**Comunicazione:**
- **Host:** localhost (default) o `BLENDER_HOST`
- **Port:** 9876 (default) o `BLENDER_PORT`
- **Protocol:** JSON over TCP

**Message Format:**
```json
// Request
{
  "type": "command_type",
  "params": { ... }
}

// Response
{
  "status": "success|error",
  "result": { ... },
  "message": "..."
}
```

### Features Principali

1. **Object Manipulation**
   - Create, modify, delete 3D objects
   - Query scene structure

2. **Material Control**
   - Apply materials
   - Modify colors and textures

3. **Code Execution**
   - Execute arbitrary Python in Blender context
   - ⚠️ Security risk: unrestricted execution

4. **Asset Integration**
   - Poly Haven assets
   - Hyper3D AI-generated models

5. **Scene Analysis**
   - Viewport screenshots
   - Object metadata queries

### Requirements

- **Blender:** 3.0+
- **Python:** 3.10+
- **Package Manager:** UV (mandatory)

### Installation Steps

1. Install UV package manager
2. Configure Claude Desktop config JSON
3. Start Blender with addon enabled
4. Addon auto-starts socket server on port 9876
5. MCP server connects automatically

### Limiti e Considerazioni

**Security:**
- ⚠️ `execute_blender_code` tool = unrestricted Python execution
- ⚠️ Save work before using
- ⚠️ Non usare in production senza safeguards

**Performance:**
- Socket communication può avere latency
- Large scenes potrebbero rallentare responses

**Stability:**
- Blender deve rimanere aperto
- Socket connection può dropparsi

---

## 3. Applicabilità a PyArchInit-Mini

### Integrazione Proposta

#### Architettura Modified

```
┌─────────────┐
│  PyArchInit │
│   Web GUI   │
│             │
│ - Prompt UI │
│ - 3D Viewer │
└──────┬──────┘
       │ WebSocket
┌──────┴──────┐
│ PyArchInit  │
│  MCP Server │ ← NUOVO
│             │
│ + GraphML   │
│ + US Data   │
│ + Periods   │
└──────┬──────┘
       │ MCP
┌──────┴──────┐
│   Claude    │
│  (via MCP)  │
└──────┬──────┘
       │ MCP
┌──────┴──────┐
│  Blender    │
│ MCP Addon   │
│             │
│ + PyArchInit│
│   Extensions│
└─────────────┘
```

### Componenti da Sviluppare

#### 1. PyArchInit MCP Server

**Posizione:** `pyarchinit_mini/mcp_server/`

**Responsabilità:**
- Esporre API MCP per Claude
- Fornire contesto archeologico (GraphML, US, periodi)
- Inviare comandi a Blender MCP
- Ricevere 3D models da Blender
- Streaming a web GUI

**Primitives da Implementare:**

**Resources:**
- `graphml://current` - GraphML corrente
- `us://list` - Lista US per site
- `periods://all` - Tutti i periodi
- `stratigraphic://relationships` - Relazioni stratigrafiche

**Tools:**
- `build_3d_from_us` - Genera 3D da lista US
- `apply_chronology` - Applica colori/layer per periodo
- `export_scene` - Export glTF
- `filter_by_period` - Filtra proxies per periodo

**Prompts:**
- `stratigraphic_model` - Template per modelli stratigrafici
- `period_visualization` - Template per viz cronologica

#### 2. Estensioni Blender Addon

**File:** `blender_addon/pyarchinit_connector.py`

**Features addizionali:**
- **Tagging system:** Associa US ID a ogni proxy
- **Layer system:** Crea layer per periodi (Bronze Age, Iron Age, etc.)
- **Spatial positioning:** Auto-posiziona proxies basato su relazioni (covers/covered by)
- **Material library:** Materiali predefiniti per tipi di strato (riempimento, interfaccia, etc.)
- **Export hooks:** Hook per export incrementale (streaming)

#### 3. Web GUI Integration

**Streaming 3D:**
- WebSocket da PyArchInit server
- Three.js viewer con GLTFLoader
- Update incrementali

**Controls:**
- Period filter (dropdown + timeline)
- Transparency slider
- Layer visibility checkboxes
- Proxy info panel

### Data Flow End-to-End

```
1. User → Prompt
   "Create 3D model of Bronze Age layers from Site 1"

2. Web GUI → PyArchInit MCP Server
   POST /api/3d-builder/generate
   { prompt, site_id, periods }

3. PyArchInit MCP Server → Claude
   - Fornisce GraphML context
   - Fornisce US data context
   - Fornisce periods context
   - Resources + Tools disponibili

4. Claude → Blender (via Blender MCP)
   - Interpreta richiesta
   - Genera comandi Blender
   - create_object(), apply_material(), etc.

5. Blender → Blender MCP Addon
   - Esegue comandi
   - Costruisce 3D scene
   - Tags proxies con US IDs

6. Blender MCP Addon → PyArchInit MCP Server
   - Export glTF chunks
   - Metadata (proxy_id → us_id mapping)
   - Progress updates

7. PyArchInit MCP Server → Web GUI (WebSocket)
   - Stream 3D model chunks
   - Progress updates
   - Final scene URL
```

### Vantaggi Approccio MCP

✅ **Standardizzazione:** Protocol standard, SDK disponibili
✅ **Flessibilità:** Claude può interpretare richieste naturali
✅ **Estensibilità:** Facile aggiungere nuovi Tools/Resources
✅ **Community:** Blender MCP addon già maturo e mantenuto
✅ **Scalabilità:** MCP supporta multiple connections

### Sfide Tecniche

⚠️ **Latency:** Chain MCP → Claude → Blender → PyArchInit
⚠️ **Debugging:** Multi-hop communication, harder to debug
⚠️ **Dependencies:** Dipendenza da Blender MCP addon esterno
⚠️ **Security:** Execute code in Blender = security risk
⚠️ **Sync:** Mantenere sincronizzazione US data ↔ proxies

### Mitigazioni

**Latency:**
- Cache responses comuni
- Async processing con progress updates
- Pre-build 3D templates

**Debugging:**
- Logging dettagliato a ogni step
- Mock servers per testing
- Health checks

**Dependencies:**
- Fork Blender MCP addon se necessario
- Vendor dependencies critical
- Automated testing

**Security:**
- Sandbox Blender execution
- Whitelist comandi permessi
- Code review AI-generated commands

**Sync:**
- Schema versioning
- Validation layers
- Conflict resolution

---

## 4. Alternative Approaches (Considerati)

### Approach A: Direct Blender Python API

**Pro:**
- No dependency su Blender MCP addon
- Controllo completo
- Più veloce (no MCP hop)

**Contro:**
- Reimplementare tutto da zero
- No Claude natural language integration
- Più complesso

### Approach B: Claude Desktop + Manual Export

**Pro:**
- Usa Blender MCP addon as-is
- No backend custom needed

**Contro:**
- No web GUI integration
- No automatic GraphML → proxy mapping
- Manual workflow

### Approach C: MCP Integration (SCELTO)

**Pro:**
- Best of both worlds
- Claude natural language
- Web GUI integration
- Reuse Blender MCP addon
- GraphML auto-mapping

**Contro:**
- Più complesso da implementare
- Latency potenziale
- Multiple dependencies

---

## 5. Next Steps

### Immediate (Task #1 - Completato ✅)

- ✅ Research MCP protocol
- ✅ Research Blender MCP addon
- ✅ Document findings

### Prossimi (Task #2)

- ⏳ Analizzare GraphML structure PyArchInit
- ⏳ Definire mapping schema US → Proxies
- ⏳ Prototypare MCP server PyArchInit (minimal)

### Week 1-2

- Installare Blender MCP addon localmente
- Test basic communication Claude ↔ Blender
- Prototipo "Hello World" 3D generation

### Week 3-4

- Implementare PyArchInit MCP server (minimal)
- Implementare Resources (GraphML, US data)
- Test end-to-end: Prompt → 3D con 1 US

---

## 6. Resources & Links

### MCP

- 📚 Official Docs: https://modelcontextprotocol.io
- 🐙 GitHub: https://github.com/modelcontextprotocol
- 📖 Claude Docs: https://docs.claude.com/en/docs/mcp
- 🐍 Python SDK: https://github.com/modelcontextprotocol/python-sdk

### Blender MCP

- 🐙 GitHub: https://github.com/ahujasid/blender-mcp
- 📺 Tutorial: YouTube channel @ahujasid
- 🌐 Website: https://blender-mcp.com
- 📄 Medium Guides: Search "Blender MCP Mehul Gupta"

### Blender

- 🐍 Python API: https://docs.blender.org/api/current/
- 📦 glTF Export: https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html
- 🔌 Addon Development: https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html

### Related

- 🎨 Three.js: https://threejs.org/docs/
- 📡 WebSocket: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- 🗺️ NetworkX (GraphML): https://networkx.org/

---

## 7. Conclusioni

L'integrazione MCP-Blender per PyArchInit-Mini è **tecnicamente fattibile** e rappresenta un approccio **innovativo e scalabile**.

### Key Insights

1. **MCP è maturo e adottato:** OpenAI, Google, community estesa
2. **Blender MCP addon è production-ready:** 13k stars, attivamente mantenuto
3. **Architecture modulare:** Ogni componente può essere sviluppato/testato indipendentemente
4. **Natural language power:** Claude può interpretare richieste complesse
5. **GraphML perfect fit:** Structured data → AI → 3D è use case ideale

### Recommended Path Forward

1. ✅ **Phase 1: Prototype** (2 settimane)
   - Setup Blender MCP locally
   - Test basic commands
   - Single US → 3D proxy

2. **Phase 2: MVP** (3-4 settimane)
   - PyArchInit MCP server minimal
   - GraphML Resources
   - 5 US → 3D model
   - Basic web viewer

3. **Phase 3: Full Feature** (4-5 settimane)
   - All Tools/Resources
   - Period filtering
   - Interactive controls
   - Production ready

**Timeline totale:** 8-11 settimane ✅

---

**Fine Report Research**
