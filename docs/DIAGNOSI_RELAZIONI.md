# Diagnosi Relazioni Stratigrafiche Mancanti

## Problema

Dopo aver importato i dati da PyArchInit, le relazioni stratigrafiche (rapporti) non sono visibili nella Harris Matrix.

## Possibili Cause

1. **Database sorgente senza rapporti**: Il database PyArchInit originale potrebbe non avere relazioni definite nel campo `rapporti`
2. **Checkbox non selezionata**: Durante l'import, la checkbox "Import US Relationships" potrebbe non essere stata selezionata
3. **Errori nel parsing**: Le relazioni potrebbero essere in un formato non standard
4. **Relazioni non visualizzate**: Le relazioni potrebbero essere nel database ma non visualizzate nella Harris Matrix

## Script di Diagnostica

### 1. Verifica Database PyArchInit-Mini (destinazione)

Controlla se le relazioni sono state importate:

```bash
python check_relationships.py
```

**Output atteso se le relazioni ci sono:**
```
Total US records: 150
Total relationships: 89

✓ Found 89 relationships

Sample relationships:
  Pompei - US 1 --[Copre]--> US 2
  Pompei - US 2 --[Copre]--> US 3
  ...
```

**Output se NON ci sono relazioni:**
```
Total US records: 150
Total relationships: 0

⚠️  NO RELATIONSHIPS FOUND!
```

### 2. Verifica Database PyArchInit (sorgente)

Controlla se il database originale ha relazioni nel campo `rapporti`:

```bash
python check_source_rapporti.py /percorso/al/database/pyarchinit_db.sqlite
```

Sostituisci `/percorso/al/database/pyarchinit_db.sqlite` con il percorso effettivo del tuo database PyArchInit.

**Output atteso se ci sono rapporti:**
```
Total US records: 150
US with rapporti: 89

✓ Found 89 US records with rapporti

Sample rapporti fields:
  Site: Pompei
  US: 1
  Rapporti: [['Copre', '2'], ['Copre', '8']]
  Parsed relationships:
    - Copre → US 2
    - Copre → US 8
```

**Output se NON ci sono rapporti:**
```
Total US records: 150
US with rapporti: 0

⚠️  NO RAPPORTI FOUND IN SOURCE DATABASE!

This is why no relationships were imported.
```

## Soluzioni per Ogni Scenario

### Scenario 1: Database Sorgente Senza Rapporti

**Problema**: Il database PyArchInit originale non ha relazioni definite.

**Soluzione**:
1. Apri PyArchInit (versione completa)
2. Definisci le relazioni stratigrafiche per ogni US usando l'interfaccia di PyArchInit
3. Salva il database
4. Ripeti l'import in PyArchInit-Mini

**Alternativa**: Crea le relazioni direttamente in PyArchInit-Mini:
1. Vai alla pagina US
2. Per ogni US, clicca "Modifica"
3. Nella sezione "Relazioni Stratigrafiche", aggiungi le relazioni
4. Salva

### Scenario 2: Import Senza Checkbox Selezionata

**Problema**: L'import è stato fatto senza selezionare "Import US Relationships".

**Soluzione**: Ripeti l'import selezionando la checkbox:

1. Vai a **Tools → Import/Export PyArchInit**
2. Tab **Import**
3. Configura il database sorgente
4. Seleziona **✓ Import US**
5. **IMPORTANTE**: Seleziona **✓ Import US Relationships (from rapporti field)**
6. Clicca **Start Import**

### Scenario 3: Relazioni Importate ma Non Visualizzate

**Problema**: Le relazioni sono nel database ma non visibili nella Harris Matrix.

**Verifica**:
```bash
python check_relationships.py
```

Se mostra relazioni ma la Harris Matrix è vuota, il problema è nella visualizzazione.

**Soluzione**:

1. **Controlla i log del server** durante la generazione della Harris Matrix:
   ```bash
   # Nel terminale dove gira Flask, cerca:
   INFO:pyarchinit_mini.harris_matrix.matrix_generator:Found X relationships for site Y
   ```

2. **Rigenera la Harris Matrix**:
   - Vai a **Harris Matrix** nel menu
   - Seleziona il sito
   - Clicca **Generate Matrix**
   - Controlla la console del browser (F12) per errori JavaScript

3. **Verifica il tipo di unità (unita_tipo)**:
   - Solo unità di tipo `US` e `USM` mostrano le relazioni testuali (Copre, Taglia, etc.)
   - Altre unità usano simboli (`>`, `>>`)

### Scenario 4: Errori nel Parsing

**Problema**: Il formato del campo `rapporti` non è standard.

**Verifica nei log del server**:
```bash
# Durante l'import, cerca:
WARNING:pyarchinit_mini.services.import_export_service:Failed to parse rapporti: ...
```

**Soluzione**:
1. Controlla il formato dei rapporti con `check_source_rapporti.py`
2. Se il formato è non standard, contatta lo sviluppatore con un esempio

## Flusso Completo di Import con Relazioni

### Passo 1: Verifica Database Sorgente

```bash
python check_source_rapporti.py /percorso/al/pyarchinit_db.sqlite
```

Assicurati che ci siano rapporti da importare.

### Passo 2: Configura Import

1. Apri http://localhost:5000
2. Vai a **Tools → Import/Export PyArchInit**
3. Tab **Import**

### Passo 3: Connessione Database

**Per SQLite:**
- Database Type: **SQLite**
- Database File Path: usa **Browse** per selezionare il file
- Clicca **Test Connection**

**Per PostgreSQL:**
- Database Type: **PostgreSQL**
- Host, Port, Database, User, Password
- Clicca **Test Connection**

### Passo 4: Seleziona Cosa Importare

✓ **Sites** (site_table)
✓ **US - Stratigraphic Units** (us_table)
  ✓ **Import US Relationships (from rapporti field)** ← **IMPORTANTE!**
✓ **Inventario Materiali**
□ Periodizzazione
□ Thesaurus

### Passo 5: Filtra per Sito (Opzionale)

Se vuoi importare solo specifici siti, selezionali dalla lista.

### Passo 6: Avvia Import

Clicca **Start Import** e attendi il completamento.

### Passo 7: Verifica Risultati

1. **Controlla i risultati mostrati nell'interfaccia web**:
   ```
   Table          | Imported | Updated | Errors
   sites          | 5        | 0       | 0
   us             | 89       | 0       | 0
   relationships  | 156      | -       | -
   ```

   Se "relationships" è 0 o non compare, c'è un problema.

2. **Verifica con script**:
   ```bash
   python check_relationships.py
   ```

3. **Testa la Harris Matrix**:
   - Vai a **Harris Matrix**
   - Seleziona il sito importato
   - Clicca **Generate Matrix**
   - Dovresti vedere le frecce con etichette (Copre, Taglia, etc.)

## Log Dettagliati

Se l'import continua a fallire, abilita logging dettagliato:

### Nel Server Flask

Guarda il terminale dove gira il server Flask durante l'import. Cerca messaggi come:

```
INFO:...Processing relationships for US Pompei/1: [['Copre', '2'], ['Copre', '8']]
INFO:...Parsed 2 relationships: [('Copre', '2'), ('Copre', '8')]
INFO:...Created relationship: Pompei US 1 -Copre-> 2
INFO:...Created relationship: Pompei US 1 -Copre-> 8
```

Se vedi:
```
DEBUG:...No rapporti field for US Pompei/1
```

Significa che quel US non ha relazioni definite nel database sorgente.

### Errori Comuni nei Log

**Errore di conversione tipo**:
```
WARNING:...Failed to create relationship Pompei US 1 -Copre-> 2: invalid literal for int()
```
Problema: Il campo `us` o `us_to` non è convertibile in intero.

**Chiave esterna mancante**:
```
WARNING:...Failed to create relationship Pompei US 1 -Copre-> 999: FOREIGN KEY constraint failed
```
Problema: La relazione punta a un US che non esiste (US 999 non importato).

## Workflow Ottimale

1. ✅ **Prima**: Verifica database sorgente con `check_source_rapporti.py`
2. ✅ **Durante**: Seleziona la checkbox "Import US Relationships"
3. ✅ **Dopo**: Verifica relazioni importate con `check_relationships.py`
4. ✅ **Test**: Genera Harris Matrix e verifica visualizzazione

## FAQ

**Q: Le relazioni sono importate ma non le vedo nella Harris Matrix?**
A: Verifica che le US abbiano `unita_tipo` = 'US' o 'USM'. Altre unità usano simboli diversi.

**Q: Vedo solo alcune relazioni, non tutte?**
A: Controlla i log del server per errori di chiave esterna (relazioni che puntano a US non importate).

**Q: Posso aggiungere relazioni manualmente dopo l'import?**
A: Sì, vai alla pagina US → Modifica → sezione "Relazioni Stratigrafiche".

**Q: Come faccio a re-importare solo le relazioni senza ri-importare le US?**
A: Attualmente non supportato. Devi fare un import completo o aggiungere manualmente le relazioni.

**Q: Le relazioni inverse vengono create automaticamente?**
A: No. Se il database PyArchInit ha "US 1 Copre US 2", viene importata solo quella direzione. "US 2 Coperto da US 1" deve essere definita separatamente nel database sorgente.

## Supporto

Se dopo aver seguito questa guida le relazioni ancora non vengono importate:

1. Esegui entrambi gli script di diagnostica
2. Copia l'output completo
3. Copia i log del server Flask durante l'import
4. Riporta il problema con questi dettagli

## Riferimenti

- `pyarchinit_mini/services/import_export_service.py` - Codice import/export
- `docs/features/pyarchinit_import_export.rst` - Documentazione completa
- `docs/features/stratigraphic_relationships.rst` - Tipi di relazioni supportate
