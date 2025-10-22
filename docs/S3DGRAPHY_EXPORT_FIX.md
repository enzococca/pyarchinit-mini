# s3Dgraphy Export Fix - Risoluzione Errori

**Data**: Ottobre 21, 2025
**Problema**: Errori durante export GraphML e JSON con s3Dgraphy

---

## 🔴 PROBLEMA ORIGINALE

L'utente ha segnalato:
```
Error exporting GraphML: Graph.__init__() missing 1 required positional argument: 'graph_id'
vale anche per il Json
```

---

## 🔍 ANALISI DEL PROBLEMA

### Errore 1: Inizializzazione Graph
**Codice errato**:
```python
graph = s3dgraphy.Graph()
```

**Problema**: Il costruttore di `s3dgraphy.Graph` richiede `graph_id` come parametro obbligatorio.

**Firma corretta**:
```python
s3dgraphy.Graph(graph_id, name=None, description=None, audio=None, video=None, data=None)
```

### Errore 2: API add_node
**Codice errato**:
```python
node = graph.add_node(node_id, node_type="US", properties=properties)
```

**Problema**: `add_node` accetta un oggetto `Node`, non stringhe e parametri keyword.

**Firma corretta**:
```python
graph.add_node(node: s3dgraphy.nodes.base_node.Node, overwrite=False)
```

### Errore 3: API add_edge
**Codice errato**:
```python
graph.add_edge(node_source, node_target, edge_type=edge_type, properties={...})
```

**Problema**: `add_edge` richiede ID stringa, non oggetti Node.

**Firma corretta**:
```python
graph.add_edge(edge_id: str, edge_source: str, edge_target: str, edge_type: str)
```

### Errore 4: Metodi di Export
**Problema**: `s3dgraphy.Graph` non ha metodi `export_graphml()` o `export_json()`.

**Soluzione**: Conversione a NetworkX per l'export.

---

## ✅ SOLUZIONI IMPLEMENTATE

### 1. Inizializzazione Corretta del Graph

```python
# Create graph with required graph_id parameter
graph_id = f"{site_name}_stratigraphy"
graph_name = f"{site_name} Stratigraphy"
graph_description = f"Stratigraphic graph exported from PyArchInit-Mini on {datetime.now().strftime('%Y-%m-%d %H:%M')}"

graph = s3dgraphy.Graph(
    graph_id=graph_id,
    name=graph_name,
    description=graph_description
)
```

### 2. Creazione Corretta dei Nodi

```python
# Create s3dgraphy Node object
node = s3dgraphy.Node(node_id, node_name, node_description)

# Add attributes to node
node.add_attribute("us_number", us_number)
node.add_attribute("site", sito)
node.add_attribute("description_strat", str(us.get('d_stratigrafica')))
# ... altri attributi ...

# Add node to graph
graph.add_node(node)
```

### 3. Creazione Corretta degli Archi

```python
# Create unique edge ID
edge_counter += 1
edge_id = f"edge_{edge_counter}_{source_id}_to_{target_id}"

# Add edge to graph (edge_id, source_id, target_id, edge_type)
graph.add_edge(edge_id, source_id, target_id, edge_type)
```

### 4. Export via NetworkX

Aggiunto metodo helper per conversione:

```python
def _convert_to_networkx(self, graph: 's3dgraphy.Graph') -> 'nx.DiGraph':
    """Convert s3dgraphy Graph to NetworkX DiGraph for export"""
    nx_graph = nx.DiGraph()

    # Add graph-level metadata
    nx_graph.graph['name'] = graph.name
    nx_graph.graph['description'] = graph.description
    nx_graph.graph['graph_id'] = graph.graph_id

    # Add nodes with all their attributes
    for node in graph.nodes:
        node_attrs = {
            'name': node.name,
            'description': node.description,
            'node_type': node.node_type if hasattr(node, 'node_type') else 'Node',
        }
        if hasattr(node, 'attributes') and node.attributes:
            node_attrs.update(node.attributes)

        nx_graph.add_node(node.node_id, **node_attrs)

    # Add edges with their attributes
    for edge in graph.edges:
        edge_attrs = {
            'edge_id': edge.edge_id,
            'edge_type': edge.edge_type,
        }
        nx_graph.add_edge(edge.edge_source, edge.edge_target, **edge_attrs)

    return nx_graph
```

Export GraphML:

```python
def export_to_graphml(self, graph: 's3dgraphy.Graph', output_path: str) -> str:
    """Export s3dgraphy graph to GraphML format using NetworkX"""
    nx_graph = self._convert_to_networkx(graph)
    nx.write_graphml(nx_graph, output_path, encoding='utf-8', prettyprint=True)
    return output_path
```

Export JSON:

```python
def export_to_json(self, graph: 's3dgraphy.Graph', output_path: str) -> str:
    """Export s3dgraphy graph to JSON format using NetworkX node-link format"""
    nx_graph = self._convert_to_networkx(graph)
    json_data = nx.node_link_data(nx_graph, edges='edges')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    return output_path
```

### 5. Fix get_graph_statistics

```python
# Count nodes by type
for node in graph.nodes:
    node_type = getattr(node, 'node_type', 'unknown')  # Era: node.get('type')
    stats["node_types"][node_type] = stats["node_types"].get(node_type, 0) + 1

# Count edges by type
for edge in graph.edges:
    edge_type = getattr(edge, 'edge_type', 'unknown')  # Era: edge.get('type')
    stats["edge_types"][edge_type] = stats["edge_types"].get(edge_type, 0) + 1
```

---

## 📁 FILE MODIFICATO

**File**: `pyarchinit_mini/s3d_integration/s3d_converter.py`

**Modifiche**:
1. Aggiunto `import json` e `import networkx as nx`
2. Riscritto `create_graph_from_us()` per usare API corretta di s3dgraphy
3. Aggiunto metodo helper `_convert_to_networkx()`
4. Riscritto `export_to_graphml()` usando NetworkX
5. Riscritto `export_to_json()` usando NetworkX
6. Fixato `get_graph_statistics()` per usare `getattr()` invece di `get()`

---

## ✅ RISULTATI TEST

```
✅ Graph Created
   ID: Pompei_stratigraphy
   Name: Pompei Stratigraphy
   Nodes: 4
   Edges: 4

✅ GraphML Export
   File: pompei.graphml
   Size: 2893 bytes

✅ JSON Export
   File: pompei.json
   Size: 1730 bytes

✅ Graph Statistics
   Total nodes: 4
   Total edges: 4
   Node types: {'geo_position': 1, 'Node': 3}
   Edge types: {'generic_connection': 4}
```

---

## 🎯 FUNZIONALITÀ RIPRISTINATE

### Web GUI
- ✅ Export GraphML s3Dgraphy da `/3d/export/graphml/<site>`
- ✅ Export JSON s3Dgraphy da `/3d/export/json/<site>`

### Desktop GUI
- ✅ Pulsante "Export GraphML s3Dgraphy" funzionante
- ✅ Pulsante "Export JSON s3Dgraphy" funzionante
- ✅ Statistiche grafo visualizzate correttamente

---

## 📊 FORMATO EXPORT

### GraphML (XML)
File XML compatibile con:
- yEd Graph Editor
- Gephi
- NetworkX
- Cytoscape

Include:
- Metadata del grafo (name, description, graph_id)
- Tutti gli attributi dei nodi (US number, site, area, descriptions, etc.)
- Tutti gli archi con tipo di relazione

### JSON (Node-Link)
File JSON compatibile con:
- D3.js
- NetworkX
- Analisi programmate con Python/JavaScript

Formato:
```json
{
  "directed": true,
  "multigraph": false,
  "graph": {
    "name": "Pompei Stratigraphy",
    "description": "Stratigraphic graph exported...",
    "graph_id": "Pompei_stratigraphy"
  },
  "nodes": [
    {
      "id": "Pompei_001",
      "name": "US 001",
      "description": "Strato superficiale",
      "us_number": "001",
      "site": "Pompei",
      ...
    }
  ],
  "edges": [
    {
      "source": "Pompei_001",
      "target": "Pompei_002",
      "edge_id": "edge_1_Pompei_001_to_Pompei_002",
      "edge_type": "COVERS"
    }
  ]
}
```

---

## 🚀 COME USARE

### Da Web GUI

1. Vai a: Menu → Harris Matrix
2. Scorri fino a "Export s3Dgraphy (Extended Matrix)"
3. Seleziona il sito dal dropdown
4. Clicca "Export GraphML s3Dgraphy" o "Export JSON s3Dgraphy"
5. Il file verrà scaricato automaticamente

### Da Desktop GUI

1. Menu → Harris Matrix → Export GraphML
2. Nella sezione "Export s3Dgraphy (Extended Matrix)"
3. Clicca "Export GraphML s3Dgraphy" o "Export JSON s3Dgraphy"
4. Scegli dove salvare il file
5. Messaggio di successo con statistiche

---

## ✅ CONCLUSIONE

Tutti gli errori di s3Dgraphy export sono stati risolti:

- ✅ Graph initialization corretta con `graph_id`
- ✅ Nodes creati con oggetti `s3dgraphy.Node`
- ✅ Edges creati con API corretta
- ✅ Export GraphML tramite NetworkX
- ✅ Export JSON tramite NetworkX
- ✅ Statistiche funzionanti

**Entrambi gli export (GraphML e JSON) ora funzionano correttamente in Web GUI e Desktop GUI.**