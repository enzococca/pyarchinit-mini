# Extended Matrix GraphML Export

## Panoramica

Il sistema di export GraphML implementa la **Extended Matrix Palette** di PyArchInit, un sistema avanzato di visualizzazione delle matrici di Harris che include:

- **Nodi speciali EM**: DOC, Extractor, Combiner, USV (A/B/C), USD, TU, SF, VSF, property
- **Relazioni simboliche**: `>`, `>>`, `<`, `<<` (con direzione esplicita)
- **Stili archi differenziati**: dotted, solid, bold, con arrowhead specifici (dot, box, none)
- **Periodizzazione archeologica**: Organizzazione automatica per periodi con datazione estesa
- **Compatibilità yEd**: Export ottimizzato per yEd Graph Editor

## Requisiti Software

### Python Dependencies (Installati Automaticamente)
```bash
pip install 'pyarchinit-mini[harris]'
```

Questo installa:
- `networkx>=3.0.0` - Struttura dati grafo in memoria
- `graphviz>=0.20.0` - Modulo Python per generare file DOT

### Graphviz Software (Richiede Installazione Manuale)

**IMPORTANTE**: Il modulo Python `graphviz` è solo un wrapper. Richiede il software nativo **Graphviz** installato nel sistema.

#### Installazione per Sistema Operativo:

**Linux (Debian/Ubuntu)**:
```bash
sudo apt-get update
sudo apt-get install graphviz
```

**Linux (Fedora/RHEL)**:
```bash
sudo dnf install graphviz
```

**macOS (Homebrew)**:
```bash
brew install graphviz
```

**macOS (MacPorts)**:
```bash
sudo port install graphviz
```

**Windows (Chocolatey)** - Aggiunge automaticamente al PATH:
```powershell
choco install graphviz
```

**Windows (Download Diretto)** - Richiede configurazione PATH:
1. **Installazione**:
   - Download da: https://graphviz.org/download/
   - Esegui `.msi` installer
   - Durante installazione: **seleziona "Add Graphviz to the system PATH for all users"**

2. **Aggiungere manualmente al PATH** (se necessario):
   - Trova percorso installazione: `C:\Program Files\Graphviz\bin`
   - Settings → System → About → Advanced system settings
   - Environment Variables → System variables → Path → Edit
   - New → Incolla: `C:\Program Files\Graphviz\bin`
   - OK → **Riapri terminali aperti**

3. **Verifica** (nuovo terminale):
   ```powershell
   dot -V
   tred -V
   ```

#### Verifica Installazione:
```bash
# Comando dot (per generare DOT)
dot -V
# Output: dot - graphviz version X.X.X

# Comando tred (per riduzione transitiva)
tred -V
# Output: tred - graphviz version X.X.X
```

> **Note**: Se Graphviz software non è installato, il sistema mostrerà un errore chiaro con istruzioni di installazione.

## Architettura del Sistema

### 1. Flusso di Trasformazione

```
Database → NetworkX DiGraph → Graphviz Digraph → DOT → DOT Ridotto → GraphML (yEd)
    ↓           ↓                    ↓              ↓         ↓            ↓
  SQLite    Struttura dati      Python graphviz   Text    tred cmd      XML
            intermedia             module          file    (Graphviz)
```

**Componenti Software**:
- **NetworkX**: Struttura dati in memoria per costruire e manipolare il grafo (normalizzazione relazioni, rimozione cicli)
- **Python `graphviz` module**: Genera il file DOT con attributi Graphviz
- **Graphviz `tred`**: Comando per riduzione transitiva del grafo
- **Custom parser**: Converte DOT in GraphML con struttura yEd TableNode

### 2. Pipeline Completa

#### Fase 1: Database → NetworkX Graph (Struttura Dati Intermedia)

**File**: `pyarchinit_mini/harris_matrix/matrix_generator.py`
**Metodo**: `generate_matrix(site_name)`

**Ruolo**: NetworkX è usato SOLO come struttura dati in memoria per:
- Organizzare nodi e archi da database
- Normalizzare relazioni inverse (coperto da → copre)
- Invertire direzioni per nodi EM speciali
- Validare e rimuovere cicli

```python
# Query database
us_nodes = db_manager.query(US).filter(sito=site_name).all()
relationships = db_manager.query(USRelationship).filter(sito=site_name).all()

# Crea grafo NetworkX
graph = nx.DiGraph()

# Aggiungi nodi con attributi
for us in us_nodes:
    graph.add_node(
        us.id_us,
        label=f"US {us.id_us}",
        extended_label=f"{us.unita_tipo}{us.id_us}",
        description=us.d_interpretativa,
        url=us.file_path if us.unita_tipo == 'DOC' else '',
        period_initial=us.periodo_iniziale,
        phase_initial=us.fase_iniziale,
        periodo_code=f"{us.periodo_iniziale}-{us.fase_iniziale}",
        unita_tipo=us.unita_tipo
    )

# Aggiungi archi con normalizzazione
for rel in relationships:
    # Normalizza relazioni inverse (coperto da → copre)
    us_from, us_to = normalize_relationship(rel)

    # Inverti direzione per nodi EM speciali (esclusi simboli)
    if is_special_node(us_from) and not is_symbolic(rel.type):
        us_from, us_to = us_to, us_from

    graph.add_edge(us_from, us_to, relationship=rel.type)
```

**Caratteristiche**:
- Rimozione cicli con validazione
- Deduplicazione relazioni inverse
- Inversione automatica per nodi EM (esclusi `>`, `>>`, `<`, `<<`)

#### Fase 2: NetworkX → Graphviz Digraph → DOT File

**File**: `pyarchinit_mini/harris_matrix/matrix_generator.py`
**Metodo**: `export_to_graphml(...)`

**Ruolo**: Il modulo Python `graphviz` genera il file DOT (NON NetworkX):
- Trasferisce nodi e archi da NetworkX a Graphviz Digraph
- Applica attributi Graphviz (shape, style, arrowhead, color)
- Organizza nodi in subgraph per periodo
- Genera file DOT usando `G.render()`

```python
from graphviz import Digraph

# Crea Graphviz Digraph (NON NetworkX!)
G = Digraph(engine='dot', strict=False)
G.attr(rankdir='TB')  # Top to Bottom

# Organizza per periodo (se richiesto)
if include_periods:
    periodo_fase_to_datazione = query_periodizzazione_table()

    for (datazione, periodo, fase), nodes in grouped_by_period:
        with G.subgraph(name=f'cluster_datazione_{id}') as c:
            c.attr(label=datazione, style='filled', color='lightblue')

            for node_id, node_data in nodes:
                c.node(
                    node_data['extended_label'],
                    label=node_data['extended_label'],
                    shape='box',
                    style='filled',
                    fillcolor='white',
                    tooltip=node_data['description'],
                    URL=node_data.get('url', ''),
                    period=datazione  # Nome periodo per Y positioning
                )

# Aggiungi archi con stili Extended Matrix
edges_by_type = classify_edges(graph)

# Dotted: taglia, property, EM symbols
for src, tgt in edges_dotted:
    G.edge(src, tgt, color='black', style='dotted', arrowhead='normal')

# Bold double: uguale a, si lega a
for src, tgt in edges_double:
    G.edge(src, tgt, color='black', style='bold', dir='both',
           arrowhead='normal', arrowtail='normal')

# Dot arrow: si appoggia
for src, tgt in edges_dot:
    G.edge(src, tgt, color='black', style='solid', arrowhead='dot')

# Box arrow: riempie
for src, tgt in edges_box:
    G.edge(src, tgt, color='black', style='solid', arrowhead='box')

# No arrow: continuity
for src, tgt in edges_no_arrow:
    G.edge(src, tgt, color='black', style='solid', arrowhead='none')

# Normal: copre (default stratigraphic)
for src, tgt in edges_normal:
    G.edge(src, tgt, color='black', style='solid', arrowhead='normal')

# Render to DOT file
G.render(filename='output.dot', format='dot')
```

**Attributi DOT Chiave**:
- `label`: Etichetta visualizzata (tipo + numero, es. "US12", "DOC4001")
- `tooltip`: Descrizione (d_interpretativa o continuità)
- `URL`: Path a file allegato (solo per DOC)
- `period`: Nome periodo (es. "Età moderna") per calcolo Y
- `shape`: Forma nodo (box, parallelogram per USV, etc.)
- `style`: filled, dotted, bold, solid
- `arrowhead`: normal, dot, box, none
- `dir`: both (per doppi archi)

#### Fase 3: DOT → DOT Ridotto (Transitive Reduction)

**File**: `pyarchinit_mini/harris_matrix/matrix_generator.py`
**Metodo**: `export_to_graphml(...)`

**Ruolo**: Graphviz `tred` command esegue la riduzione transitiva:
- Comando shell `tred` (parte della suite Graphviz software)
- NON un algoritmo NetworkX
- Processa il file DOT come testo e genera DOT ridotto

```python
import subprocess

# Applica riduzione transitiva con comando Graphviz tred
# tred è un COMANDO di Graphviz software (non Python)
with open('output_tred.dot', 'w') as f:
    subprocess.run(['tred', 'output.dot'], stdout=f, timeout=30)

# Converti DOT ridotto in GraphML
from pyarchinit_mini.graphml_converter.converter import convert_dot_to_graphml

success = convert_dot_to_graphml(
    dot_file='output_tred.dot',
    graphml_file='output.graphml',
    title='Harris Matrix',
    reverse_epochs=False
)
```

**Transitive Reduction** (comando `tred` di Graphviz):
- Rimuove archi ridondanti mantenendo le relazioni
- Esempio: se US1→US2→US3 e US1→US3, rimuove US1→US3
- Richiede Graphviz installato nel sistema (`sudo apt install graphviz` o `brew install graphviz`)
- Fallback: se tred non disponibile, usa DOT non ridotto

#### Fase 4: DOT → GraphML (Parsing e Rendering)

**File**: `pyarchinit_mini/graphml_converter/dot_parser.py`
**Classe**: `Node`

```python
class Node:
    def get_y(self, epoch, nome_us, node_to_cluster=None):
        """Calcola coordinata Y per posizionamento"""
        # 1. Prova node_to_cluster (se fornito)
        if node_to_cluster and nome_us in node_to_cluster:
            return (int(node_to_cluster[nome_us]) - 1) * 1000

        # 2. Prova attributo 'period'
        if 'period' in self.attribs:
            period_value = self.attribs['period']
            for i, epoch_name in enumerate(epoch):
                if epoch_name in period_value:
                    return i * 1000  # 1000 pixel per riga

        # 3. Fallback: cerca periodo nel label
        for i, epoch_name in enumerate(epoch):
            if epoch_name in nome_us:
                return i * 1000

        return 0  # Default prima riga

    def exportGraphml(self, doc, parent, conf, epoch_sigla, node_to_cluster=None):
        """Esporta nodo in formato GraphML (yEd TableNode)"""
        # Crea elemento <node>
        node_elem = doc.createElement('node')
        node_elem.setAttribute('id', f'n0::n{self.id}')

        # Data key d5: description (da tooltip)
        if 'tooltip' in self.attribs:
            data_desc = doc.createElement('data')
            data_desc.setAttribute('key', 'd5')
            data_desc.appendChild(doc.createTextNode(self.attribs['tooltip']))
            node_elem.appendChild(data_desc)

        # Data key d4: URL (solo per DOC)
        if 'URL' in self.attribs:
            data_url = doc.createElement('data')
            data_url.setAttribute('key', 'd4')
            data_url.appendChild(doc.createTextNode(self.attribs['URL']))
            node_elem.appendChild(data_url)

        # Data key d6: node graphics
        data_graphics = doc.createElement('data')
        data_graphics.setAttribute('key', 'd6')

        # y:ShapeNode (o SVGNode per CON, GenericNode per DOC)
        shape_node = doc.createElement('y:ShapeNode')

        # Geometry con Y calcolata
        geom = doc.createElement('y:Geometry')
        geom.setAttribute('height', '30.0')
        geom.setAttribute('width', '90.0')
        geom.setAttribute('x', '520.0')
        geom.setAttribute('y', str(self.get_y(epoch_sigla, self.label)))

        # NodeLabel con testo del label
        label_elem = doc.createElement('y:NodeLabel')
        label_elem.appendChild(doc.createTextNode(self.label))

        # Assembla struttura
        shape_node.appendChild(geom)
        shape_node.appendChild(label_elem)
        # ... altri elementi (Fill, BorderStyle, Shape)

        data_graphics.appendChild(shape_node)
        node_elem.appendChild(data_graphics)

        return node_elem
```

**Struttura GraphML (yEd TableNode)**:

```xml
<graphml>
  <!-- Key definitions -->
  <key attr.name="url" for="node" id="d4" />
  <key attr.name="description" for="node" id="d5" />
  <key yfiles.type="nodegraphics" for="node" id="d6" />

  <graph edgedefault="directed">
    <!-- TableNode container (periodo rows) -->
    <node id="n0" yfiles.foldertype="group">
      <data key="d6">
        <y:TableNode>
          <y:Geometry height="10000" width="1044" x="-29" y="-596"/>

          <!-- Row labels (periodi) -->
          <y:NodeLabel modelName="RowNodeLabelModel"
                       id="row_Età_contemporanea">
            Età contemporanea
          </y:NodeLabel>
          <y:NodeLabel modelName="RowNodeLabelModel"
                       id="row_Età_moderna">
            Età moderna
          </y:NodeLabel>
          <!-- ... altre rows ... -->

          <y:Table>
            <y:Rows>
              <y:Row height="940" id="row_Età_contemporanea"/>
              <y:Row height="940" id="row_Età_moderna"/>
              <!-- ... -->
            </y:Rows>
          </y:Table>
        </y:TableNode>
      </data>

      <!-- Nodi US (posizionati nelle rows) -->
      <graph edgedefault="directed" id="n0:">
        <node id="n0::n1">
          <data key="d5">Fondazione in muratura</data>
          <data key="d6">
            <y:ShapeNode>
              <y:Geometry height="30" width="90" x="520" y="0"/>
              <y:NodeLabel>US1</y:NodeLabel>
              <y:Shape type="rectangle"/>
            </y:ShapeNode>
          </data>
        </node>

        <node id="n0::n19">
          <data key="d4">DosCo\test1.graphml</data>
          <data key="d6">
            <y:GenericNode configuration="com.yworks.bpmn.Artifact">
              <y:Geometry height="55" width="35" x="520" y="0"/>
              <y:NodeLabel>DOC4001</y:NodeLabel>
            </y:GenericNode>
          </data>
        </node>

        <!-- Archi -->
        <edge source="n0::n1" target="n0::n2">
          <data key="d10">
            <y:PolyLineEdge>
              <y:LineStyle color="#000000" type="line" width="1.0"/>
              <y:Arrows source="none" target="standard"/>
            </y:PolyLineEdge>
          </data>
        </edge>
      </graph>
    </node>
  </graph>
</graphml>
```

## Struttura Dati Richiesta

### Database Schema

#### Tabella `us_table`

```sql
CREATE TABLE us_table (
    id_us INTEGER PRIMARY KEY,
    sito VARCHAR(350) NOT NULL,
    unita_tipo VARCHAR(50),  -- 'US', 'USM', 'DOC', 'Extractor', etc.
    area VARCHAR(100),
    d_stratigrafica TEXT,
    d_interpretativa TEXT,
    formazione VARCHAR(100),
    periodo_iniziale INTEGER,
    fase_iniziale INTEGER,
    periodo_finale INTEGER,
    fase_finale INTEGER,
    file_path VARCHAR(500)  -- Path relativo per DOC
);
```

#### Tabella `us_relationships_table`

```sql
CREATE TABLE us_relationships_table (
    id_relationship INTEGER PRIMARY KEY,
    sito VARCHAR(350) NOT NULL,
    us_from INTEGER NOT NULL,
    us_to INTEGER NOT NULL,
    relationship_type VARCHAR(100),  -- 'copre', 'taglia', '>>', etc.
    certainty VARCHAR(20),
    FOREIGN KEY (us_from) REFERENCES us_table(id_us),
    FOREIGN KEY (us_to) REFERENCES us_table(id_us)
);
```

#### Tabella `periodizzazione_table`

```sql
CREATE TABLE periodizzazione_table (
    id_periodo INTEGER PRIMARY KEY,
    sito VARCHAR(350) NOT NULL,
    periodo_iniziale INTEGER NOT NULL,
    fase_iniziale INTEGER NOT NULL,
    datazione_estesa VARCHAR(200),  -- "Età moderna", "XV secolo", etc.
    cron_iniziale INTEGER,
    cron_finale INTEGER
);
```

### Tipi di Relazioni Supportate

#### Relazioni Stratigrafiche Standard
- `copre` / `coperto da` (normalized to `copre`)
- `taglia` / `tagliato da` (normalized to `taglia`)
- `riempie` / `riempito da` (normalized to `riempie`)
- `si appoggia` / `si appoggia a` / `gli si appoggia` (normalized to `si appoggia`)
- `uguale a` / `same as`
- `si lega a` / `bonds with`
- `sopra` / `above`

#### Relazioni Extended Matrix Simboliche
- `>` / `<` (coppia inversa, normalized to `>`)
- `>>` / `<<` (coppia inversa, normalized to `>>`)

**IMPORTANTE**: Le relazioni simboliche (`>`, `>>`, `<`, `<<`) **NON** vengono invertite automaticamente per nodi EM, perché codificano già la direzione esplicita.

## Uso Programmatico

### Export Base

```python
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.services.us_service import USService

# Connessione database
db_url = "sqlite:///./pyarchinit_mini.db"
db_conn = DatabaseConnection.from_url(db_url)
db_manager = DatabaseManager(db_conn)
us_service = USService(db_manager)

# Generatore Matrix
matrix_generator = HarrisMatrixGenerator(db_manager, us_service)

# Genera grafo
site_name = "Scavo Archeologico"
graph = matrix_generator.generate_matrix(site_name)

# Export GraphML con Extended Matrix
output_path = "/path/to/output.graphml"
result = matrix_generator.export_to_graphml(
    graph=graph,
    output_path=output_path,
    site_name=site_name,
    title="Titolo Diagramma",
    use_extended_labels=True,  # Usa tipo+numero (es. USM12)
    include_periods=True,       # Organizza per periodi
    reverse_epochs=False        # False = Periodo 1 = epoca più antica
)

print(f"Export completato: {result}")
```

### Parametri di Export

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `graph` | `nx.DiGraph` | **required** | Grafo NetworkX generato |
| `output_path` | `str` | **required** | Path file .graphml output |
| `site_name` | `str` | **required** | Nome sito archeologico |
| `title` | `str` | `None` | Titolo diagramma |
| `use_extended_labels` | `bool` | `True` | Usa label EM (tipo+numero) |
| `include_periods` | `bool` | `True` | Organizza per periodi |
| `reverse_epochs` | `bool` | `False` | Inverti ordine periodi |

### Accesso Diretto ai File DOT

```python
# Export genera 3 file:
# 1. output.dot - DOT originale
# 2. output_tred.dot - DOT con riduzione transitiva
# 3. output.graphml - GraphML finale

# Puoi lavorare direttamente con i file DOT
import subprocess

# Genera DOT senza GraphML
dot_path = "/path/to/output.dot"
# ... (usa graphviz.Digraph come sopra)

# Applica tred manualmente
with open('output_tred.dot', 'w') as f:
    subprocess.run(['tred', dot_path], stdout=f)

# Visualizza con dot
subprocess.run(['dot', '-Tpng', 'output_tred.dot', '-o', 'output.png'])
```

## Estendere con Nuovi Tipi di Nodi EM

### Step 1: Aggiungere Tipo al Database

```python
# Inserisci nuovo tipo US
us = US(
    sito="Sito Test",
    id_us=999,
    unita_tipo="NUOVO_TIPO",  # <-- Nuovo tipo EM
    d_interpretativa="Descrizione nodo",
    periodo_iniziale=1,
    fase_iniziale=1
)
db_manager.session.add(us)
db_manager.session.commit()
```

### Step 2: Configurare Inversione Relazioni

**File**: `pyarchinit_mini/harris_matrix/matrix_generator.py`
**Metodo**: `generate_matrix()`
**Linea**: ~194

```python
# Special node types that should be TARGET of relationships (not source)
special_target_types = [
    'DOC', 'Extractor', 'Combiner',
    'USVA', 'USVB', 'USVC', 'USD', 'TU', 'SF', 'VSF',
    'NUOVO_TIPO'  # <-- Aggiungi qui
]
```

**Spiegazione**:
- I nodi in `special_target_types` sono **sempre TARGET** delle relazioni
- Esempio: se DB ha `NUOVO_TIPO → US5`, il sistema inverte in `US5 → NUOVO_TIPO`
- **Eccezione**: Relazioni simboliche (`>`, `>>`, `<`, `<<`) non vengono invertite

### Step 3: Configurare Stile Archi (Opzionale)

Se il nuovo nodo richiede uno stile arco specifico:

**File**: `pyarchinit_mini/harris_matrix/matrix_generator.py`
**Metodo**: `export_to_graphml()`
**Linea**: ~750-810

```python
# Classifica archi per tipo
for source, target, edge_data in graph.edges(data=True):
    rel_type = edge_data.get('relationship', 'sopra')
    rel_lower = rel_type.lower()

    # ... esistente ...

    # Aggiungi nuova classificazione
    elif rel_lower in ['relazione_nuovo_tipo']:
        edges_nuovo_tipo.append((source_label, target_label))

# Render archi con stile specifico
for source_label, target_label in edges_nuovo_tipo:
    G.edge(source_label, target_label,
           color='black',
           style='dashed',  # Scegli stile
           arrowhead='diamond')  # Scegli arrowhead
```

**Arrowhead disponibili**: `normal`, `dot`, `box`, `diamond`, `odiamond`, `none`
**Style disponibili**: `solid`, `dotted`, `dashed`, `bold`

### Step 4: Configurare Simbologia Nodo (yEd)

Per simboli grafici speciali (come DOC = data object):

**File**: `pyarchinit_mini/graphml_converter/dot_parser.py`
**Metodo**: `exportGraphml()`
**Linea**: ~1010-1050

```python
# Detect node type
if 'NUOVO_TIPO' in a_type:
    # Usa GenericNode (esempio: BPMN artifact)
    generic_node = doc.createElement('y:GenericNode')
    generic_node.setAttribute('configuration', 'com.yworks.bpmn.Artifact')

    geom = doc.createElement('y:Geometry')
    geom.setAttribute('height', '55.0')
    geom.setAttribute('width', '35.0')
    geom.setAttribute('x', '520.0')
    geom.setAttribute('y', str(self.get_y(epoch_sigla, LabelText)))

    generic_node.appendChild(geom)
    # ... label, StyleProperties, etc.

    data0.appendChild(generic_node)
```

**Configurazioni yEd disponibili**:
- `y:ShapeNode` - Forme standard (rectangle, ellipse, parallelogram, etc.)
- `y:GenericNode` con `com.yworks.bpmn.Artifact` - Simboli BPMN (document, data)
- `y:SVGNode` - Forme custom SVG (es. cerchio per continuità)

### Step 5: Testare

```python
# Test con nuovo tipo
graph = matrix_generator.generate_matrix("Test Site")

# Verifica nodo presente
assert 999 in graph.nodes()
assert graph.nodes[999]['unita_tipo'] == 'NUOVO_TIPO'

# Verifica direzione archi (se ha relazioni)
edges = list(graph.out_edges(999))  # Archi in uscita
print(f"NUOVO_TIPO → {edges}")

# Export e verifica GraphML
result = matrix_generator.export_to_graphml(
    graph=graph,
    output_path="test_nuovo_tipo.graphml",
    site_name="Test Site"
)

# Apri con yEd e verifica simbolo e posizionamento
```

## Debugging e Troubleshooting

### Problema: Nodi mancanti nel GraphML

**Causa**: Parser DOT non trova i nodi
**Soluzione**: Verifica attributi DOT

```bash
# Controlla DOT generato
grep "MISSING_NODE" output.dot

# Verifica che abbia attributi base
# label, shape, style, fillcolor
```

### Problema: Nodi tutti sulla prima riga

**Causa**: Attributo `period` mancante o non trovato in epoch list
**Soluzione**:

```python
# Verifica epoch list
from pyarchinit_mini.graphml_converter.converter import DotToGraphMLConverter
converter = DotToGraphMLConverter()
print(converter.epoch_list)  # Deve contenere nomi periodi

# Verifica attributo period nel DOT
grep "period=" output.dot
# Deve mostrare: period="Età moderna" (NOME, non "1-2")
```

### Problema: Relazioni invertite

**Causa**: Nodo EM non in `special_target_types` o è una relazione simbolica
**Soluzione**:

```python
# Verifica tipo nodo
node_data = graph.nodes[node_id]
print(node_data['unita_tipo'])

# Verifica se è relazione simbolica
rel_type = edge_data['relationship']
if rel_type in ['>', '>>', '<', '<<']:
    print("Relazione simbolica - NON invertita")
else:
    print("Relazione standard - invertita se nodo EM")
```

### Problema: Archi con stile sbagliato

**Causa**: Classificazione edge non corretta
**Soluzione**: Debug edge classification

```python
# Prima di export, stampa classificazione
edges_dotted = []
edges_double_no_arrow = []
# ... (classifica tutti gli archi)

print(f"Dotted: {len(edges_dotted)}")
print(f"Double: {len(edges_double_no_arrow)}")
# ... verifica conteggi
```

## File di Riferimento

| File | Descrizione |
|------|-------------|
| `pyarchinit_mini/harris_matrix/matrix_generator.py` | Core: genera grafo, export DOT, export GraphML |
| `pyarchinit_mini/graphml_converter/converter.py` | Converti DOT → GraphML (dispatcher) |
| `pyarchinit_mini/graphml_converter/dot_parser.py` | Parse DOT, calcola posizioni, render nodi |
| `pyarchinit_mini/graphml_converter/graphml_exporter.py` | Render GraphML XML finale |
| `pyarchinit_mini/graphml_converter/templates/EM_palette.graphml` | Template base con key definitions |

## Riferimenti

- **PyArchInit Extended Matrix**: [GitHub pyarchinit/pyarchinit3](https://github.com/pyarchinit/pyarchinit3)
- **Graphviz DOT Language**: [graphviz.org/doc/info/lang.html](https://graphviz.org/doc/info/lang.html)
- **yEd GraphML Format**: [yWorks GraphML Primer](https://yed.yworks.com/support/manual/graphml_primer.html)
- **Harris Matrix**: [Harris, E. C. (1979). Principles of Archaeological Stratigraphy](https://doi.org/10.1016/B978-0-12-326580-9.50009-3)
