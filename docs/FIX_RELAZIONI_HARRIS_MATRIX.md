# Fix: Relazioni Non Visualizzate nella Harris Matrix

## Problema Identificato

Le relazioni stratigrafiche erano **correttamente importate** nel database (488 relazioni trovate!), ma **non visualizzate** nella Harris Matrix.

### Causa Root

Il generatore della Harris Matrix (`matrix_generator.py`) stava cercando di leggere le relazioni dal vecchio campo `rapporti` (formato PyArchInit legacy), invece che dalla tabella `us_relationships_table` dove vengono importate le relazioni in PyArchInit-Mini.

## Fix Applicato

### File Modificato: `pyarchinit_mini/harris_matrix/matrix_generator.py`

#### Cambiamento 1: Metodo `_get_relationships()` (linea 111-188)

**PRIMA:**
- Leggeva solo dal campo `rapporti` delle US (metodo legacy PyArchInit)
- Non accedeva alla tabella `us_relationships_table`

**DOPO:**
- **Metodo 1 (Prioritario)**: Legge dalla tabella `us_relationships_table` con una query SQL diretta
- **Metodo 2 (Fallback)**: Se la tabella è vuota, fallback al metodo legacy `rapporti`
- Normalizza i tipi di relazione a lowercase per il confronto

```python
# Query relationships from dedicated table
query = text("""
    SELECT DISTINCT r.us_from, r.us_to, r.relationship_type
    FROM us_relationships_table r
    INNER JOIN us_table u_from ON r.sito = u_from.sito AND r.us_from = CAST(u_from.us AS INTEGER)
    INNER JOIN us_table u_to ON r.sito = u_to.sito AND r.us_to = CAST(u_to.us AS INTEGER)
    WHERE r.sito = :site
""")
```

#### Cambiamento 2: Filtro Relazioni (linea 67-90)

**PRIMA:**
- Filtrava solo relazioni in minuscolo strict match
- Mancavano varianti inglesi

**DOPO:**
- Confronto case-insensitive
- Incluse tutte le varianti italiane e inglesi:
  - `copre / covered by / covers`
  - `taglia / cut by / cuts`
  - `riempie / filled by / fills`
  - `si appoggia a / leans against`
  - ecc.
- Log delle relazioni sconosciute per debug

### File Modificato: `pyarchinit_mini/services/import_export_service.py`

#### Cambiamento: Import Relazioni con Logging (linea 407-455)

**Aggiunti:**
- Log dettagliato durante il parsing delle relazioni
- Controllo duplicati prima dell'inserimento
- Warning per relazioni fallite (invece di silent fail)
- Contatore relazioni create

```python
logger.info(f"Processing relationships for US {sito}/{us}: {rapporti_field}")
logger.info(f"Parsed {len(relationships)} relationships")
logger.info(f"Created relationship: {sito} US {us_from} -{rel_type}-> {us_to}")
```

## Come Testare

### 1. Riavvia il Server Web

**IMPORTANTE:** Devi riavviare Flask per applicare i cambiamenti:

```bash
# Stop server (Ctrl+C)
# Restart:
cd /Users/enzo/Documents/pyarchinit-mini-desk
python web_interface/app.py
```

### 2. Verifica Relazioni nel Database

```bash
python check_relationships.py
```

**Output atteso:**
```
Total US records: 101
Total relationships: 488

✓ Found 488 relationships

Sample relationships:
  Scavo archeologico - US 1001 --[Copre]--> US 1002
  Scavo archeologico - US 1002 --[Taglia]--> US 1005
  ...
```

### 3. Genera Harris Matrix

1. Apri http://localhost:5000
2. Vai a **Harris Matrix** nel menu
3. Seleziona un sito (es. "Scavo archeologico" che ha 374 relazioni)
4. Clicca **Generate Matrix**

### 4. Verifica Visualizzazione

Dovresti vedere:

- **Nodi US**: Rettangoli con numero US
- **Frecce**: Collegamenti tra le US
- **Etichette**: Tipi di relazione sulle frecce:
  - "Copre"
  - "Taglia"
  - "Riempie"
  - "Si appoggia a"
  - ecc.

### 5. Controlla Log del Server

Nel terminale dove gira Flask, durante la generazione dovresti vedere:

```
Found 374 relationships in us_relationships_table for Scavo archeologico
```

Se vedi invece:
```
Falling back to rapporti field method...
```

Significa che la query sulla tabella relazioni è fallita (verifica il database).

## Verifica Completa

### Test Scenario 1: Sito con Molte Relazioni

```bash
# Terminal 1: Check database
python check_relationships.py

# Terminal 2: Start Flask
python web_interface/app.py

# Browser: Generate matrix for "Scavo archeologico"
```

**Risultato Atteso:**
- Matrix visualizzata con 374 relazioni
- Frecce etichettate correttamente
- Nessun errore nel log

### Test Scenario 2: Re-Import Relazioni

Se vuoi testare un nuovo import:

```bash
# 1. Verifica sorgente
python check_source_rapporti.py /path/to/pyarchinit_db.sqlite

# 2. Import via web interface
#    - Seleziona ✓ Import US Relationships

# 3. Verifica destinazione
python check_relationships.py

# 4. Test Harris Matrix
```

## Logging Migliorato

### Durante Import

Il server ora mostra dettagli per ogni relazione:

```
INFO:...Processing relationships for US Pompei/1: [['Copre', '2'], ['Copre', '8']]
INFO:...Parsed 2 relationships: [('Copre', '2'), ('Copre', '8')]
INFO:...Created relationship: Pompei US 1 -Copre-> 2
INFO:...Created relationship: Pompei US 1 -Copre-> 8
```

### Durante Generazione Harris Matrix

```
Found 374 relationships in us_relationships_table for Scavo archeologico
```

O se trova relazioni sconosciute:
```
Skipping unknown relationship type: RelazioneSconosciuta
```

## Risoluzione Problemi

### Problema: "Found 0 relationships in us_relationships_table"

**Causa**: La tabella è vuota
**Soluzione**:
1. Verifica import con `python check_relationships.py`
2. Se 0 relazioni, ri-fai l'import selezionando la checkbox "Import US Relationships"

### Problema: "Skipping unknown relationship type: XYZ"

**Causa**: Tipo di relazione non riconosciuto
**Soluzione**:
1. Verifica il tipo con `python check_relationships.py`
2. Se è un tipo valido, aggiungilo alla lista `valid_relationships` in matrix_generator.py linea 69-77
3. Riavvia server

### Problema: Matrix vuota anche dopo il fix

**Debug:**
1. Controlla console browser (F12) per errori JavaScript
2. Controlla log server per errori durante generazione
3. Verifica che il sito selezionato abbia relazioni: `python check_relationships.py`

### Problema: Alcune relazioni mancano

**Possibili cause:**
1. **Chiave esterna mancante**: La relazione punta a US non importata
   - Cerca nei log: "WARNING:...Failed to create relationship...FOREIGN KEY"
   - Soluzione: Importa tutte le US del sito

2. **Tipo relazione non supportato**: La relazione ha un tipo non standard
   - Cerca nei log: "Skipping unknown relationship type"
   - Soluzione: Aggiungi il tipo alla lista valida

3. **Duplicati**: La relazione esisteva già
   - Cerca nei log: "Relationship already exists"
   - Normale, non è un errore

## Riepilogo Cambiamenti

### ✅ Cosa Funziona Ora

1. ✅ Import relazioni da PyArchInit → us_relationships_table
2. ✅ Lettura relazioni da us_relationships_table per Harris Matrix
3. ✅ Supporto completo italiano/inglese
4. ✅ Logging dettagliato import/export
5. ✅ Fallback al metodo legacy se necessario
6. ✅ Filtraggio case-insensitive

### 📝 File Modificati

1. `pyarchinit_mini/harris_matrix/matrix_generator.py`
   - Metodo `_get_relationships()`: Query us_relationships_table
   - Filtro relazioni: Case-insensitive, multi-lingua

2. `pyarchinit_mini/services/import_export_service.py`
   - Metodo `import_us()`: Logging dettagliato
   - Check duplicati prima insert

### 🔧 Utility Create

1. `check_relationships.py` - Verifica relazioni in PyArchInit-Mini
2. `check_source_rapporti.py` - Verifica rapporti in PyArchInit sorgente
3. `docs/DIAGNOSI_RELAZIONI.md` - Guida completa diagnosi
4. `docs/FIX_RELAZIONI_HARRIS_MATRIX.md` - Questo documento

## Prossimi Passi

1. ✅ **Riavvia server** - Applica modifiche
2. ✅ **Genera Harris Matrix** - Test visualizzazione
3. ✅ **Verifica log** - Conferma lettura da us_relationships_table
4. ✅ **Report problemi** - Se ancora non funziona, fornisci log

## Versione

Fix applicato: 2025-10-23
Versione PyArchInit-Mini: 1.2.17+
