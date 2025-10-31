# PyArchInit MCP Server - Architecture Design

**Versione:** 1.0
**Data:** 31 Ottobre 2025
**Status:** Design Phase

---

## 1. Overview

Il PyArchInit MCP Server è il componente centrale che collega:
- Claude AI (via Model Context Protocol)
- Blender (via Blender MCP addon)
- PyArchInit Web GUI (via WebSocket)
- PyArchInit database (US, Sites, Periods, GraphML)

### Obiettivi

1. **Esporre contesto archeologico a Claude** tramite MCP Resources
2. **Fornire strumenti 3D** tramite MCP Tools
3. **Coordinare generazione 3D** tra Claude e Blender
4. **Streaming real-time** dei modelli 3D alla web GUI
5. **Gestire associazioni** GraphML nodes ↔ Blender proxies

---

## 2. Directory Structure

```
pyarchinit_mini/
├── mcp_server/
│   ├── __init__.py
│   ├── server.py                    # MCP server principale
│   ├── config.py                    # Configurazione
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── graphml_resource.py      # Resource: GraphML data
│   │   ├── us_resource.py           # Resource: US stratigrafici
│   │   ├── periods_resource.py      # Resource: Periodi
│   │   ├── relationships_resource.py # Resource: Relazioni
│   │   └── site_resource.py         # Resource: Siti
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── build_3d_tool.py         # Tool: Genera 3D da US
│   │   ├── filter_tool.py           # Tool: Filtra per periodo
│   │   ├── export_tool.py           # Tool: Export glTF
│   │   ├── position_tool.py         # Tool: Posiziona proxies
│   │   └── material_tool.py         # Tool: Applica materiali
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── stratigraphic_model.py   # Prompt: Template modello strat.
│   │   ├── period_visualization.py  # Prompt: Template viz periodo
│   │   └── us_description.py        # Prompt: Template descrizione US
│   ├── blender/
│   │   ├── __init__.py
│   │   ├── client.py                # Client Blender MCP
│   │   ├── commands.py              # Comandi Blender
│   │   └── proxy_mapper.py          # Mapper US → Proxy
│   ├── streaming/
│   │   ├── __init__.py
│   │   ├── websocket_handler.py     # WebSocket server
│   │   ├── gltf_streamer.py         # Streamer glTF
│   │   └── progress_tracker.py      # Progress tracking
│   ├── services/
│   │   ├── __init__.py
│   │   ├── graphml_parser.py        # Parser GraphML
│   │   ├── us_data_provider.py      # Provider dati US
│   │   ├── period_filter.py         # Filtro periodi
│   │   └── spatial_analyzer.py      # Analisi spaziale
│   └── models/
│       ├── __init__.py
│       ├── proxy.py                 # Model: Proxy 3D
│       ├── build_session.py         # Model: Sessione build
│       └── us_mapping.py            # Model: Mapping US
```

---

## 3. Core Components

### 3.1 MCP Server (`server.py`)

**Responsabilità:**
- Implementare MCP protocol specification
- Registrare Resources, Tools, Prompts
- Gestire connessioni Claude ↔ PyArchInit
- Coordinare chiamate a Blender
- Inviare updates a Web GUI

**Classe principale:**

```python
class PyArchInitMCPServer:
    """
    MCP Server per PyArchInit-Mini

    Espone:
    - 5 Resources (GraphML, US, Periods, Relationships, Sites)
    - 5 Tools (build_3d, filter, export, position, material)
    - 3 Prompts (stratigraphic_model, period_visualization, us_description)
    """

    def __init__(self, config: MCPConfig):
        self.config = config
        self.db_session = create_db_session(config.database_url)
        self.blender_client = BlenderClient(config.blender_host, config.blender_port)
        self.websocket_handler = WebSocketHandler(config.websocket_port)
        self.resources = self._register_resources()
        self.tools = self._register_tools()
        self.prompts = self._register_prompts()

    def _register_resources(self) -> Dict[str, Resource]:
        """Registra MCP Resources"""
        return {
            'graphml://current': GraphMLResource(self.db_session),
            'us://list': USResource(self.db_session),
            'periods://all': PeriodsResource(self.db_session),
            'relationships://matrix': RelationshipsResource(self.db_session),
            'sites://active': SiteResource(self.db_session)
        }

    def _register_tools(self) -> Dict[str, Tool]:
        """Registra MCP Tools"""
        return {
            'build_3d_from_us': Build3DTool(self.blender_client),
            'filter_by_period': FilterTool(self.db_session),
            'export_scene': ExportTool(self.blender_client),
            'position_proxies': PositionTool(self.blender_client),
            'apply_materials': MaterialTool(self.blender_client)
        }

    def _register_prompts(self) -> Dict[str, Prompt]:
        """Registra MCP Prompts"""
        return {
            'stratigraphic_model': StratigraphicModelPrompt(),
            'period_visualization': PeriodVisualizationPrompt(),
            'us_description': USDescriptionPrompt()
        }

    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle MCP request from Claude"""
        if request.type == 'resource':
            return await self._handle_resource_request(request)
        elif request.type == 'tool':
            return await self._handle_tool_request(request)
        elif request.type == 'prompt':
            return await self._handle_prompt_request(request)
        else:
            raise MCPError(f"Unknown request type: {request.type}")
```

**Configuration (`config.py`):**

```python
@dataclass
class MCPConfig:
    """Configurazione MCP Server"""

    # Database
    database_url: str = "sqlite:///data/pyarchinit_mini.db"

    # Blender
    blender_host: str = "localhost"
    blender_port: int = 9876
    blender_timeout: int = 30

    # WebSocket
    websocket_host: str = "0.0.0.0"
    websocket_port: int = 5002

    # MCP
    mcp_server_name: str = "pyarchinit-mcp"
    mcp_version: str = "1.0.0"

    # Streaming
    chunk_size: int = 1024 * 1024  # 1MB
    max_concurrent_builds: int = 3

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/mcp_server.log"
```

---

## 4. MCP Resources

### 4.1 GraphML Resource

**URI:** `graphml://current`

**Descrizione:** Fornisce GraphML corrente del sito attivo

**Schema:**

```python
class GraphMLResource(Resource):
    """
    Resource che espone GraphML strutturato
    """

    async def read(self, params: Dict) -> ResourceData:
        """
        Params:
            site_id: int (optional)
            include_periods: bool (default: True)
            include_relationships: bool (default: True)

        Returns:
            {
                "site_name": str,
                "nodes": [
                    {
                        "id": str,           # "US1001"
                        "us_id": int,        # 1001
                        "label": str,        # "US1001"
                        "description": str,  # "Modern topsoil..."
                        "period": str,       # "Bronze Age"
                        "area": str,         # "1000"
                        "interpretation": str,
                        "formation": str,
                        "position": {
                            "x": float,
                            "y": float
                        }
                    },
                    ...
                ],
                "edges": [
                    {
                        "source": str,       # "US1001"
                        "target": str,       # "US1002"
                        "relationship": str, # "covers"
                        "certainty": str     # "certain"
                    },
                    ...
                ],
                "periods": [
                    {
                        "name": str,
                        "color": str,
                        "us_ids": [int]
                    }
                ]
            }
        """
```

### 4.2 US Resource

**URI:** `us://list`

**Descrizione:** Lista completa US con tutti i dati

```python
class USResource(Resource):
    """
    Resource che espone dati US completi
    """

    async def read(self, params: Dict) -> ResourceData:
        """
        Params:
            site_id: int
            us_ids: List[int] (optional)
            include_media: bool (default: False)

        Returns:
            {
                "us_list": [
                    {
                        "id_us": int,
                        "sito": str,
                        "area": str,
                        "us": int,
                        "d_stratigrafica": str,
                        "d_interpretativa": str,
                        "descrizione": str,
                        "interpretazione": str,
                        "periodo_iniziale": int,
                        "fase_iniziale": int,
                        "periodo_finale": int,
                        "fase_finale": int,
                        "relationships": {
                            "covers": [int],
                            "covered_by": [int],
                            "cuts": [int],
                            "cut_by": [int],
                            "fills": [int],
                            "filled_by": [int],
                            "same_as": [int]
                        },
                        "media": [...]  # if include_media=True
                    }
                ]
            }
        """
```

### 4.3 Periods Resource

**URI:** `periods://all`

**Descrizione:** Tutti i periodi archeologici configurati

```python
class PeriodsResource(Resource):
    """
    Resource che espone periodi e datazioni
    """

    async def read(self, params: Dict) -> ResourceData:
        """
        Returns:
            {
                "periods": [
                    {
                        "id": int,
                        "period": str,           # "Bronze Age"
                        "cron_iniziale": int,    # -1200
                        "cron_finale": int,      # -1000
                        "fase": str,             # "Middle"
                        "datazione_estesa": str, # "1200-1000 BCE"
                        "color": str,            # "#D8BD30"
                        "us_count": int          # Numero US in questo periodo
                    }
                ]
            }
        """
```

### 4.4 Relationships Resource

**URI:** `relationships://matrix`

**Descrizione:** Matrice relazioni stratigrafiche

```python
class RelationshipsResource(Resource):
    """
    Resource che espone matrice relazioni
    """

    async def read(self, params: Dict) -> ResourceData:
        """
        Params:
            site_id: int
            us_ids: List[int] (optional)

        Returns:
            {
                "matrix": {
                    "1": {  # US ID
                        "covers": [2, 3],
                        "covered_by": [],
                        "contemporaneo_a": [4]
                    },
                    "2": {
                        "covers": [5],
                        "covered_by": [1],
                        "contemporaneo_a": [3]
                    }
                },
                "stratigraphic_order": [1, 4, 2, 3, 5],  # Top to bottom
                "validation": {
                    "cycles": [],
                    "paradoxes": [],
                    "warnings": []
                }
            }
        """
```

---

## 5. MCP Tools

### 5.1 Build 3D Tool

**Name:** `build_3d_from_us`

**Descrizione:** Genera modello 3D da lista US

```python
class Build3DTool(Tool):
    """
    Tool per generare modello 3D
    """

    schema = {
        "name": "build_3d_from_us",
        "description": "Build 3D stratigraphic model from US list",
        "input_schema": {
            "type": "object",
            "properties": {
                "site_id": {
                    "type": "integer",
                    "description": "Site ID"
                },
                "us_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of US IDs to include"
                },
                "auto_position": {
                    "type": "boolean",
                    "default": True,
                    "description": "Auto-position based on relationships"
                },
                "apply_colors": {
                    "type": "boolean",
                    "default": True,
                    "description": "Apply colors based on periods"
                },
                "scale_by_depth": {
                    "type": "boolean",
                    "default": False,
                    "description": "Scale proxies by stratigraphic depth"
                }
            },
            "required": ["site_id", "us_ids"]
        }
    }

    async def execute(self, params: Dict) -> ToolResult:
        """
        1. Fetch US data from database
        2. Build proxy list with metadata
        3. Send commands to Blender via MCP
        4. Track progress
        5. Return session ID for streaming

        Returns:
            {
                "success": True,
                "session_id": "build_12345",
                "websocket_url": "ws://localhost:5002/3d-stream/12345",
                "proxies_count": 10,
                "estimated_duration": 30
            }
        """
```

### 5.2 Filter Tool

**Name:** `filter_by_period`

**Descrizione:** Filtra proxies per periodo

```python
class FilterTool(Tool):
    """
    Tool per filtrare proxies
    """

    schema = {
        "name": "filter_by_period",
        "description": "Filter 3D proxies by archaeological period",
        "input_schema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Build session ID"
                },
                "periods": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Period names to show"
                },
                "cron_range": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "integer"},
                        "end": {"type": "integer"}
                    },
                    "description": "Chronological range (BCE/CE)"
                },
                "action": {
                    "type": "string",
                    "enum": ["show", "hide", "highlight", "transparent"],
                    "default": "show"
                }
            },
            "required": ["session_id"]
        }
    }

    async def execute(self, params: Dict) -> ToolResult:
        """
        Returns:
            {
                "success": True,
                "visible_count": 5,
                "hidden_count": 5,
                "filtered_us_ids": [1, 2, 5, 7, 9]
            }
        """
```

### 5.3 Export Tool

**Name:** `export_scene`

**Descrizione:** Export scena 3D in formato glTF

```python
class ExportTool(Tool):
    """
    Tool per export glTF
    """

    schema = {
        "name": "export_scene",
        "description": "Export 3D scene to glTF format",
        "input_schema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Build session ID"
                },
                "format": {
                    "type": "string",
                    "enum": ["gltf", "glb"],
                    "default": "gltf"
                },
                "include_metadata": {
                    "type": "boolean",
                    "default": True
                },
                "optimize": {
                    "type": "boolean",
                    "default": True
                }
            },
            "required": ["session_id"]
        }
    }
```

### 5.4 Position Tool

**Name:** `position_proxies`

**Descrizione:** Posiziona proxies basato su relazioni stratigrafiche

```python
class PositionTool(Tool):
    """
    Tool per posizionamento spaziale
    """

    schema = {
        "name": "position_proxies",
        "description": "Position proxies based on stratigraphic relationships",
        "input_schema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string"
                },
                "algorithm": {
                    "type": "string",
                    "enum": ["hierarchical", "force_directed", "manual"],
                    "default": "hierarchical"
                },
                "spacing": {
                    "type": "number",
                    "default": 1.0,
                    "description": "Vertical spacing between layers"
                }
            },
            "required": ["session_id"]
        }
    }
```

### 5.5 Material Tool

**Name:** `apply_materials`

**Descrizione:** Applica materiali e colori a proxies

```python
class MaterialTool(Tool):
    """
    Tool per materiali
    """

    schema = {
        "name": "apply_materials",
        "description": "Apply materials and colors to proxies",
        "input_schema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string"
                },
                "strategy": {
                    "type": "string",
                    "enum": ["by_period", "by_type", "by_formation", "custom"],
                    "default": "by_period"
                },
                "custom_colors": {
                    "type": "object",
                    "description": "Custom color mapping {us_id: '#RRGGBB'}"
                }
            },
            "required": ["session_id"]
        }
    }
```

---

## 6. MCP Prompts

### 6.1 Stratigraphic Model Prompt

**Name:** `stratigraphic_model`

**Template:**

```
You are helping create a 3D stratigraphic model. Here's the context:

Site: {{site_name}}
Total US: {{us_count}}
Periods present: {{periods}}

GraphML Data:
{{graphml_json}}

US Details:
{{us_details}}

Please analyze the stratigraphy and suggest:
1. Which US should be included in the 3D model
2. How to position them spatially (based on relationships)
3. What colors to apply (based on periods)
4. Any special considerations (cuts, fills, interfaces)

Use the following tools:
- build_3d_from_us: to create the model
- position_proxies: to arrange layers
- apply_materials: to apply period-based colors
```

### 6.2 Period Visualization Prompt

**Name:** `period_visualization`

**Template:**

```
Create a chronological 3D visualization for:

Period: {{period_name}}
Date range: {{cron_iniziale}} to {{cron_finale}}
US in this period: {{us_ids}}

Relationships:
{{relationships_matrix}}

Please:
1. Build 3D model for these US
2. Apply period-specific color: {{period_color}}
3. Position based on stratigraphic order
4. Highlight temporal relationships

Tools available: build_3d_from_us, apply_materials, filter_by_period
```

---

## 7. Blender Client

### 7.1 Client Implementation

```python
class BlenderClient:
    """
    Client per comunicare con Blender MCP addon
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None

    async def connect(self):
        """Connect to Blender socket server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    async def send_command(self, command: BlenderCommand) -> BlenderResponse:
        """
        Send command to Blender

        Command format:
        {
            "type": "create_object" | "apply_material" | "export_gltf" | ...,
            "params": {...}
        }

        Response format:
        {
            "status": "success" | "error",
            "result": {...},
            "message": "..."
        }
        """
        message = json.dumps(command.to_dict())
        self.socket.sendall(message.encode('utf-8'))

        response_data = self.socket.recv(4096).decode('utf-8')
        return BlenderResponse.from_json(response_data)
```

### 7.2 Commands

```python
@dataclass
class CreateProxyCommand:
    """Comando per creare proxy"""
    us_id: int
    name: str
    position: Tuple[float, float, float]
    scale: Tuple[float, float, float]
    color: str

    def to_blender_command(self) -> Dict:
        return {
            "type": "create_object",
            "params": {
                "object_type": "cube",  # or "mesh"
                "name": f"US{self.us_id}",
                "location": list(self.position),
                "scale": list(self.scale),
                "custom_properties": {
                    "us_id": self.us_id,
                    "pyarchinit_type": "stratigraphic_unit"
                }
            }
        }

@dataclass
class ApplyMaterialCommand:
    """Comando per applicare materiale"""
    proxy_id: str
    color: str
    transparency: float = 0.0

    def to_blender_command(self) -> Dict:
        return {
            "type": "apply_material",
            "params": {
                "object_name": self.proxy_id,
                "material_type": "principled",
                "base_color": self.color,
                "alpha": 1.0 - self.transparency
            }
        }
```

---

## 8. WebSocket Streaming

### 8.1 Handler

```python
class WebSocketHandler:
    """
    WebSocket server per streaming 3D
    """

    def __init__(self, port: int):
        self.port = port
        self.sessions: Dict[str, BuildSession] = {}

    async def handle_connection(self, websocket, path):
        """Handle WebSocket connection"""
        session_id = path.split('/')[-1]

        if session_id not in self.sessions:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Session not found"
            }))
            return

        session = self.sessions[session_id]

        # Stream progress updates
        async for update in session.progress_updates():
            await websocket.send(json.dumps(update))

        # Stream 3D model chunks
        async for chunk in session.model_chunks():
            await websocket.send(json.dumps({
                "type": "model_chunk",
                "data": base64.b64encode(chunk).decode('utf-8')
            }))

        # Send completion
        await websocket.send(json.dumps({
            "type": "complete",
            "model_url": session.final_model_url,
            "metadata": session.metadata
        }))
```

---

## 9. Data Models

### 9.1 Proxy Model

```python
@dataclass
class Proxy:
    """Model per proxy 3D"""
    proxy_id: str
    us_id: int
    name: str
    position: Tuple[float, float, float]
    scale: Tuple[float, float, float]
    rotation: Tuple[float, float, float]
    color: str
    transparency: float
    visible: bool
    period: Optional[str]
    metadata: Dict[str, Any]
```

### 9.2 Build Session Model

```python
@dataclass
class BuildSession:
    """Model per sessione build 3D"""
    session_id: str
    site_id: int
    us_ids: List[int]
    proxies: List[Proxy]
    status: str  # "building", "complete", "error"
    progress: float  # 0.0 to 1.0
    created_at: datetime
    completed_at: Optional[datetime]
    final_model_url: Optional[str]
    metadata: Dict[str, Any]
```

---

## 10. Error Handling

```python
class MCPError(Exception):
    """Base MCP error"""
    pass

class BlenderConnectionError(MCPError):
    """Blender connection failed"""
    pass

class ResourceNotFoundError(MCPError):
    """Resource not found"""
    pass

class ToolExecutionError(MCPError):
    """Tool execution failed"""
    pass
```

---

## 11. Deployment

### 11.1 Installation

```bash
# Install Python MCP SDK
pip install mcp-python

# Install dependencies
pip install websockets aiohttp networkx

# Configure MCP server
export PYARCHINIT_DATABASE_URL="sqlite:///data/pyarchinit_mini.db"
export BLENDER_MCP_HOST="localhost"
export BLENDER_MCP_PORT="9876"
```

### 11.2 Running

```bash
# Start MCP server
python -m pyarchinit_mini.mcp_server.server

# Or via uvx
uvx pyarchinit-mcp
```

### 11.3 Claude Desktop Configuration

```json
{
  "mcpServers": {
    "pyarchinit": {
      "command": "uvx",
      "args": ["pyarchinit-mcp"],
      "env": {
        "PYARCHINIT_DATABASE_URL": "sqlite:///data/pyarchinit_mini.db"
      }
    }
  }
}
```

---

## 12. Testing Strategy

### Unit Tests

- Test ogni Resource individualmente
- Test ogni Tool con mock Blender client
- Test Prompts templates
- Test data models

### Integration Tests

- Test MCP server con mock Claude client
- Test Blender client con mock socket
- Test WebSocket streaming
- Test end-to-end flow

### Performance Tests

- Benchmark GraphML parsing (target: < 100ms per 100 US)
- Benchmark 3D generation (target: < 5s per 10 US)
- Benchmark streaming (target: < 2s lag)

---

## 13. Next Steps

1. ✅ Design completato
2. ⏳ Implement base MCP server (Task #5)
3. ⏳ Implement Resources (GraphML, US)
4. ⏳ Implement Tools (build_3d)
5. ⏳ Implement Blender client
6. ⏳ Implement WebSocket streaming
7. ⏳ Integration testing
8. ⏳ Performance optimization

---

**Fine Design Document**
