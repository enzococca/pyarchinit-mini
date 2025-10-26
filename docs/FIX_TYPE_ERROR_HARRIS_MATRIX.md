# Fix: Errore di Tipo nella Generazione Harris Matrix

## Problema

Errore durante la generazione della Harris Matrix:
```
'<' not supported between instances of 'int' and 'str'
```

## Causa

NetworkX (la libreria che genera il grafo) prova a confrontare i nodi per ordinamento interno e altre operazioni. Quando alcuni numeri US sono interi e altri sono stringhe, il confronto fallisce.

**Dove si verificava il problema:**

1. **Nodi dal servizio US**: US number poteva essere int o str
2. **Edges dalla tabella relazioni**: `us_from` e `us_to` erano interi (dalla query SQL)
3. **Edges dal campo rapporti**: `us_to` era convertito a int esplicitamente

## Soluzione Applicata

### File Modificato: `pyarchinit_mini/harris_matrix/matrix_generator.py`

#### Fix 1: Conversione Nodi (linea 55-56)

**PRIMA:**
```python
us_num = getattr(us, 'us', None)
if us_num is None:
    continue

graph.add_node(us_num, ...)
```

**DOPO:**
```python
us_num = getattr(us, 'us', None)
if us_num is None:
    continue

# Ensure us_num is always a string for consistent node keys
us_num = str(us_num)

graph.add_node(us_num, ...)
```

#### Fix 2: Conversione Edges da Relazioni (linea 90-92)

**PRIMA:**
```python
if rel_type_lower in valid_relationships:
    graph.add_edge(
        rel['us_from'],
        rel['us_to'],
        ...
    )
```

**DOPO:**
```python
if rel_type_lower in valid_relationships:
    # Ensure US numbers are strings for consistent node keys
    us_from = str(rel['us_from'])
    us_to = str(rel['us_to'])

    graph.add_edge(
        us_from,
        us_to,
        ...
    )
```

#### Fix 3: Conversione nel Parsing Rapporti Legacy (linea 272-273)

**PRIMA:**
```python
relationships.append({
    'us_from': us_num,
    'us_to': int(rel_us),  # ← Problema qui!
    ...
})
```

**DOPO:**
```python
relationships.append({
    'us_from': str(us_num),  # Always string
    'us_to': str(rel_us),    # Always string
    ...
})
```

## Verifica Fix

### Test Automatico

```bash
python test_harris_fix.py
```

**Output Atteso:**
```
✅ SUCCESS! Harris Matrix is reading relationships from us_relationships_table!

Sample relationships in graph:
  1. US 2 --[coperto da]--> US 1
  2. US 8 --[coperto da]--> US 1
  ...
```

### Test Manuale nel Browser

1. **Avvia server:**
   ```bash
   python web_interface/app.py
   ```

2. **Genera Harris Matrix:**
   - Vai a http://localhost:5000
   - Menu → Harris Matrix
   - Seleziona un sito
   - Clicca "Generate Matrix"

3. **Risultato atteso:**
   - ✅ Matrix visualizzata senza errori
   - ✅ Nodi US collegati
   - ✅ Etichette sulle frecce

### Cosa Controllare nei Log

**Prima del fix:**
```
ERROR: '<' not supported between instances of 'int' and 'str'
```

**Dopo il fix:**
```
Found 374 relationships in us_relationships_table for Scavo archeologico
```

Nessun errore di tipo!

## Dettagli Tecnici

### Perché NetworkX Confronta i Nodi?

NetworkX internamente:
1. **Ordina i nodi** per alcune operazioni (es. transitive reduction)
2. **Usa dizionari** dove le chiavi devono essere comparabili
3. **Applica algoritmi** che possono richiedere confronti

Quando i tipi sono misti (int e str), Python non può confrontarli:
```python
1 < "2"  # TypeError: '<' not supported between instances of 'int' and 'str'
```

### Perché Usare Stringhe Invece di Interi?

1. **Schema Database**: Il campo `us` è definito come `VARCHAR` nella tabella US
2. **Extended Matrix**: Supporta US con suffissi (es. "US_A", "US_1a")
3. **Compatibilità**: PyArchInit originale usa stringhe
4. **Flessibilità**: Permette numeri US non numerici

### Dove Possono Verificarsi Problemi Simili

Se aggiungi altre funzionalità che lavorano con i nodi del grafo, assicurati che:

1. **ID nodi sono sempre stringhe**: Converti sempre a `str()` prima di usare come chiave nodo
2. **Confronti espliciti**: Non fare `us1 < us2` con tipi misti
3. **Ordinamento**: Usa `sorted(nodes, key=str)` per ordinare in modo sicuro

## Riepilogo Modifiche

### ✅ Cosa È Stato Fatto

1. ✅ Convertiti tutti gli US number a stringhe nei nodi
2. ✅ Convertiti tutti gli US number a stringhe negli edges (da tabella relazioni)
3. ✅ Convertiti tutti gli US number a stringhe negli edges (da campo rapporti legacy)
4. ✅ Test passato senza errori di tipo

### 📁 File Modificati

- `pyarchinit_mini/harris_matrix/matrix_generator.py` (3 fix applicati)

### 🧪 Test Creati

- `test_harris_fix.py` - Test automatico generazione Harris Matrix

## Compatibilità

### Retrocompatibilità

✅ **Mantenuta**: Il fix non rompe dati esistenti perché:
- Il database memorizza già US come VARCHAR
- La conversione `str()` funziona sia su int che su str
- Gli algoritmi NetworkX funzionano correttamente con chiavi stringa

### Database Esistenti

✅ **Nessuna migrazione necessaria**: I dati esistenti continuano a funzionare

### Import da PyArchInit

✅ **Funziona**: L'import converte correttamente i tipi durante il processo

## Troubleshooting

### Problema: "AttributeError: 'str' object has no attribute..."

**Causa**: Codice che assume US number sia intero

**Soluzione**: Converti a int quando necessario:
```python
us_num_str = str(us.us)  # Per grafo
us_num_int = int(us.us)  # Per calcoli matematici
```

### Problema: "KeyError" su un nodo

**Causa**: Stai cercando un nodo con tipo diverso da quello usato per crearlo

**Soluzione**: Assicurati di usare sempre stringhe:
```python
node_id = str(us_number)
if node_id in graph:
    ...
```

### Problema: Relazioni mancanti dopo il fix

**Causa**: Improbabile, ma verifica con:
```bash
python check_relationships.py
```

Se le relazioni ci sono nel database ma non nel grafo, controlla i log per messaggi "Skipping unknown relationship type".

## Test Completo

### Scenario 1: Sito con Molte Relazioni

```bash
# 1. Test automatico
python test_harris_fix.py

# 2. Avvia server
python web_interface/app.py

# 3. Browser: Generate matrix per "Scavo archeologico"
```

**Risultato atteso**: Matrix visualizzata senza errori

### Scenario 2: Import Nuovo Database

```bash
# 1. Import da PyArchInit via web interface
# 2. Verifica relazioni
python check_relationships.py

# 3. Test Harris Matrix
python test_harris_fix.py

# 4. Visualizza nel browser
```

**Risultato atteso**: Tutto funziona senza errori di tipo

## Versione

Fix applicato: 2025-10-23
Versione PyArchInit-Mini: 1.2.17+
Moduli interessati: Harris Matrix Generator
