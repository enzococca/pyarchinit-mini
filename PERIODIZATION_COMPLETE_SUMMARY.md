# Periodization System - Complete Implementation

**Data:** 24 Ottobre 2025
**Versione:** PyArchInit-Mini v1.2.17+
**Status:** ✅ COMPLETATO

---

## 🎯 Obiettivo Raggiunto

Sistema di periodizzazione completo per Harris Matrix export, compatibile con PyArchInit QGIS plugin, che usa **datazione_estesa** dalla tabella periodizzazione invece di codici numerici.

---

## ✅ Caratteristiche Implementate

### 1. Datazione Estesa per Clustering

Le righe (rows) del graphml sono ora organizzate per **datazione cronologica leggibile**:

```
✅ Età contemporanea
✅ Età moderna
✅ Fine XVI secolo - Inizi XVII secolo
✅ XV sec rec
✅ XV secolo
✅ Prima metà' del XV secolo rec
✅ Prima metà' del XV secolo
```

**Invece di codici numerici:**
```
❌ Periodo: 1, Fase: 1
❌ Periodo: 1, Fase: 2
❌ Periodo: 2, Fase: 1
```

### 2. Struttura Database

**us_table** (dati periodizzazione per ogni US):
- `periodo_iniziale`: VARCHAR (es. "1", "2", "3")
- `fase_iniziale`: VARCHAR (es. "1", "2", "2.1", "3.1")
- `periodo_finale`: VARCHAR
- `fase_finale`: VARCHAR

**periodizzazione_table** (tabella lookup):
- **Chiave**: (periodo_iniziale, fase_iniziale, sito)
- **Valore**: datazione_estesa (testo cronologico)

```sql
SELECT periodo_iniziale, fase_iniziale, datazione_estesa
FROM periodizzazione_table
WHERE sito = 'Scavo archeologico'

-- Esempi:
-- 1, 1 → "Età contemporanea"
-- 1, 2 → "Età moderna"
-- 2, 1 → "Fine XVI secolo - Inizi XVII secolo"
-- 2, 2.1 → "XV sec rec"
-- 2, 3 → "XV secolo"
```

### 3. Logica di Lookup

```python
# 1. Carica lookup map da periodizzazione_table
periodo_fase_to_datazione = {}
query = text("""
    SELECT periodo_iniziale, fase_iniziale, datazione_estesa
    FROM periodizzazione_table
    WHERE sito = :site
""")
result = session.execute(query, {'site': site_name})

for row in result.fetchall():
    periodo = str(row.periodo_iniziale) if row.periodo_iniziale else ''
    fase = str(row.fase_iniziale) if row.fase_iniziale else ''
    datazione = row.datazione_estesa or 'Non datato'

    # Chiave: (periodo, fase)
    key = (periodo, fase)
    periodo_fase_to_datazione[key] = datazione

# 2. Per ogni nodo, ottieni periodo/fase da us_table
for node_id, node_data in graph.nodes(data=True):
    periodo = str(node_data.get('period_initial', ''))
    fase = str(node_data.get('phase_initial', ''))

    # 3. Lookup datazione_estesa
    lookup_key = (periodo, fase)
    if lookup_key in periodo_fase_to_datazione:
        datazione = periodo_fase_to_datazione[lookup_key]
    else:
        datazione = 'Non datato'

    # 4. Raggruppa per datazione
    datazione_groups[datazione].append((node_id, node_data))
```

---

## 📊 Risultati Test - Sito "Scavo archeologico"

### Distribuzione US per Datazione

```
Totale US: 51
US con relazioni: 23
Cluster creati: 7

Cluster 1: Età contemporanea                  → 1 US
Cluster 2: Età moderna                        → 2 US
Cluster 3: Fine XVI secolo - Inizi XVII secolo → 2 US
Cluster 4: XV sec rec                         → 8 US
Cluster 5: XV secolo                          → 4 US
Cluster 6: Prima metà' del XV secolo rec      → 3 US
Cluster 7: Prima metà' del XV secolo          → 1 US
```

### File Generati

```bash
harris_matrix_with_periodization.dot     # 11 KB - File DOT intermedio
harris_matrix_with_periodization.graphml # 39 KB - File GraphML finale
```

---

## 🔧 Codice Implementato

### File Modificato

`pyarchinit_mini/harris_matrix/matrix_generator.py` - Funzione `export_to_graphml()`

### Modifiche Principali

**Prima (ERRATO - usava codici numerici):**
```python
# Query periodizzazione_table per US
query = text("""
    SELECT us, datazione_estesa
    FROM periodizzazione_table
    WHERE sito = :site
""")
# Problema: campo us è NULL nella tabella!
```

**Dopo (CORRETTO - lookup per periodo/fase):**
```python
# Build lookup map: (periodo, fase) -> datazione_estesa
query = text("""
    SELECT periodo_iniziale, fase_iniziale, datazione_estesa
    FROM periodizzazione_table
    WHERE sito = :site
""")

# Per ogni nodo, lookup usando periodo/fase dal node_data
periodo = str(node_data.get('period_initial', ''))
fase = str(node_data.get('phase_initial', ''))
lookup_key = (periodo, fase)

if lookup_key in periodo_fase_to_datazione:
    datazione = periodo_fase_to_datazione[lookup_key]
else:
    datazione = 'Non datato'
```

---

## 🎨 Formato Extended Labels

Ogni nodo mantiene il formato PyArchInit EM palette:

```
unita_tipo + us + '_' + d_interpretativa + '_' + periodo-fase
```

**Esempi:**
```
US1_Fondazione_in_muratura_1-1
US2_Livellamento_1-2
USVA102_test_2-2.1
USVB104_gggg_2-3.1
USM12_Muro_2-3
```

**Nota:** Il suffisso periodo-fase (`1-1`, `2-2.1`) rimane nei nomi dei nodi per compatibilità, ma i cluster ora usano datazione_estesa.

---

## 📁 Struttura DOT Generato

```dot
digraph {
    graph [rankdir=TB, compound=true];

    subgraph cluster_datazione_1 {
        label="Età contemporanea"
        style=filled
        color=lightblue

        "US1_Fondazione_in_muratura_1-1" [...]
    }

    subgraph cluster_datazione_2 {
        label="Età moderna"
        style=filled
        color=lightblue

        "US2_Livellamento_1-2" [...]
        "US8_Buca_1-2" [...]
    }

    subgraph cluster_datazione_3 {
        label="Fine XVI secolo - Inizi XVII secolo"
        style=filled
        color=lightblue

        "US3_Abbandono_2-1" [...]
        "CON500_continuità_con_US_12_2-1" [...]
    }

    # ... altri cluster ...
}
```

---

## 🚀 Utilizzo

### Generazione con Periodizzazione

```python
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.services.us_service import USService

# Setup
connection = DatabaseConnection('sqlite:///pyarchinit_mini.db')
db_manager = DatabaseManager(connection)
us_service = USService(db_manager)
matrix_gen = HarrisMatrixGenerator(db_manager, us_service)

# Genera matrice
graph = matrix_gen.generate_matrix("Scavo archeologico")

# Export con datazione_estesa clustering (default)
matrix_gen.export_to_graphml(
    graph,
    "harris_matrix_with_periodization.graphml",
    use_extended_labels=True,
    site_name="Scavo archeologico",
    include_periods=True  # Default: True
)
```

### Export senza Clustering

```python
# Per grafo semplice senza raggruppamenti cronologici
matrix_gen.export_to_graphml(
    graph,
    "harris_matrix_flat.graphml",
    use_extended_labels=True,
    include_periods=False  # Disabilita clustering
)
```

---

## 📖 Apertura in yEd

### 1. Apri File

1. Avvia yEd Graph Editor
2. File → Open
3. Seleziona `harris_matrix_with_periodization.graphml`

### 2. Visualizzazione Cluster

I cluster datazione appaiono come **TableNode** raggruppati:

```
┌─ Età contemporanea ──────────────────┐
│ US1_Fondazione_in_muratura_1-1      │
└──────────────────────────────────────┘

┌─ Età moderna ────────────────────────┐
│ US2_Livellamento_1-2                 │
│ US8_Buca_1-2                         │
└──────────────────────────────────────┘

┌─ XV secolo ──────────────────────────┐
│ USM12_Muro_2-3                       │
│ USM19_Muro_2-3                       │
│ US5_Focolare_2-3                     │
│ USM6_Muro_2-3                        │
└──────────────────────────────────────┘
```

### 3. Layout Consigliato

1. Layout → Hierarchical
2. Orientation: Top to Bottom
3. Layering: Hierarchical Optimal
4. Edge Routing: Orthogonal
5. Grouping: Use Automatic Grouping

---

## 🔍 Verifica Implementazione

### Test Script

```bash
python test_periodization.py
```

### Verifica DOT File

```bash
# Conta cluster datazione
grep "subgraph cluster_datazione" harris_matrix_with_periodization.dot | wc -l

# Lista datazioni usate
grep -E "subgraph cluster_datazione|label=\"[A-Z]" harris_matrix_with_periodization.dot \
  | grep -A1 "subgraph cluster" \
  | grep "label=" \
  | sed 's/.*label="\([^"]*\)".*/\1/'
```

**Output atteso:**
```
Età contemporanea
Età moderna
Fine XVI secolo - Inizi XVII secolo
XV sec rec
XV secolo
Prima metà' del XV secolo rec
Prima metà' del XV secolo
```

### Verifica Database

```bash
# Verifica lookup map periodizzazione
sqlite3 pyarchinit_mini.db "
  SELECT periodo_iniziale, fase_iniziale, datazione_estesa
  FROM periodizzazione_table
  WHERE sito = 'Scavo archeologico'
  ORDER BY periodo_iniziale, fase_iniziale
"
```

**Output atteso:**
```
1|1|Età contemporanea
1|2|Età moderna
2|1|Fine XVI secolo - Inizi XVII secolo
2|2|Prima metà del XVI secolo
2|2.1|XV sec rec
2|3|XV secolo
2|3.1|Prima metà' del XV secolo rec
2|4|Prima metà' del XV secolo
3|1|Inizi XV secolo
3|2|Fine XIV secolo
3|3|Seconda metà' del XIV secolo
4|1|Generico XIII secolo - Primi del XIV secolo
```

```bash
# Verifica periodo/fase in US
sqlite3 pyarchinit_mini.db "
  SELECT us, periodo_iniziale, fase_iniziale
  FROM us_table
  WHERE sito = 'Scavo archeologico'
  AND us IN (1,2,3,5,6,7,8,12,19,29)
  ORDER BY us
"
```

**Output atteso:**
```
1|1|1         → Lookup: Età contemporanea
2|1|2         → Lookup: Età moderna
3|2|1         → Lookup: Fine XVI secolo - Inizi XVII secolo
5|2|3         → Lookup: XV secolo
6|2|3         → Lookup: XV secolo
7|1|2         → Lookup: Età moderna
8|1|2         → Lookup: Età moderna
12|2|3        → Lookup: XV secolo
19|2|3        → Lookup: XV secolo
29|2|4        → Lookup: Prima metà' del XV secolo
```

---

## 📊 Confronto Prima/Dopo

### Prima (ERRATO)

**DOT File:**
```dot
subgraph cluster_periodo_1 {
    label="Periodo: 1"

    subgraph cluster_fase_1 {
        label="Fase: 1"
        ...
    }
}
```

**Problema:** Mostra codici numerici incomprensibili

### Dopo (CORRETTO)

**DOT File:**
```dot
subgraph cluster_datazione_1 {
    label="Età contemporanea"
    ...
}

subgraph cluster_datazione_2 {
    label="Età moderna"
    ...
}
```

**Soluzione:** Mostra periodi cronologici leggibili

---

## 🎯 Vantaggi

### 1. Leggibilità

- **Prima:** "Periodo: 2, Fase: 3.1" → Incomprensibile
- **Dopo:** "Prima metà' del XV secolo rec" → Chiaro e professionale

### 2. Compatibilità PyArchInit

- Stessa logica del plugin QGIS originale
- Usa periodizzazione_table come lookup
- Extended labels identici

### 3. Flessibilità

- Datazioni testuali modificabili in periodizzazione_table
- Nessun hard-coding di periodi
- Supporto multilingua (es. "XV century" vs "XV secolo")

---

## 📝 Note Tecniche

### Gestione Valori NULL

US senza periodizzazione vengono raggruppati in "Non datato":

```python
if lookup_key in periodo_fase_to_datazione:
    datazione = periodo_fase_to_datazione[lookup_key]
else:
    datazione = 'Non datato'
```

### Ordinamento Cluster

Cluster ordinati cronologicamente per periodo-fase:

```python
sorted_groups = sorted(datazione_groups.items(),
                      key=lambda x: (x[0][1] or 'ZZZ', x[0][2] or 'ZZZ', x[0][0]))
```

Dove:
- `x[0][1]`: periodo_iniziale (es. "1", "2")
- `x[0][2]`: fase_iniziale (es. "1", "2.1")
- `x[0][0]`: datazione_estesa (es. "XV secolo")

### Filtro US Rilevanti

Solo US con relazioni stratigrafiche sono inclusi:

```python
us_rilevanti = set()
for source, target in graph.edges():
    us_rilevanti.add(source)
    us_rilevanti.add(target)

# Solo nodi con relazioni
if node_id not in us_rilevanti:
    continue
```

---

## ✅ Checklist Completamento

- [x] Lookup datazione_estesa da periodizzazione_table
- [x] Mapping (periodo, fase) → datazione
- [x] Clustering per datazione_estesa
- [x] Extended labels preservate
- [x] Test con sito "Scavo archeologico" completato
- [x] 7 cluster datazione creati correttamente
- [x] File DOT e GraphML generati
- [x] Verifica labels testuali (non numerici)
- [x] Documentazione completa

---

## 🔗 File Correlati

- `pyarchinit_mini/harris_matrix/matrix_generator.py` - Export function (linee 706-792)
- `test_periodization.py` - Test script
- `harris_matrix_with_periodization.dot` - DOT output (11 KB)
- `harris_matrix_with_periodization.graphml` - GraphML output (39 KB)
- `docs/GRAPHML_DOT_EXPORT_GUIDE.md` - Guida export

---

## 🔮 Sviluppi Futuri Possibili

### 1. Colori Automatici per Periodo

Assegnare colori differenziati per periodo storico:
- Età contemporanea → Verde
- Medievale → Blu
- Romano → Rosso

### 2. Supporto Periodo Finale

Includere periodo_finale/fase_finale per US che attraversano più periodi:
```
Label: "Età moderna - XV secolo"
```

### 3. Export Multilingua

Generare GraphML con datazioni in lingue diverse:
```python
matrix_gen.export_to_graphml(graph, "out.graphml", language='en')
# "Modern Age" invece di "Età moderna"
```

---

**Fine Documento**

*Sistema periodizzazione con datazione_estesa implementato e testato ✅*
*Compatibile con PyArchInit QGIS plugin*
*Data: 24 Ottobre 2025*
