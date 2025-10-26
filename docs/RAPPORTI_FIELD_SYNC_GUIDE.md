# Guida: Sincronizzazione Campo Rapporti

## Cosa È Stato Fatto

### 1. Modificato Import Service ✅

**File:** `pyarchinit_mini/services/import_export_service.py` (linea 529)

**Modifica:**
```python
'rapporti': source_data.get('rapporti'),  # Copy rapporti field for compatibility
```

**Effetto:**
- I PROSSIMI import copieranno il campo rapporti da PyArchInit
- Le relazioni saranno in ENTRAMBI:
  - Campo `rapporti` (formato testo)
  - Tabella `us_relationships_table` (formato relazionale)

### 2. Creato Script di Sincronizzazione ✅

**File:** `sync_rapporti_from_relationships.py`

**Funzione:**
- Legge da `us_relationships_table`
- Genera campo `rapporti` in formato PyArchInit
- Aggiorna tutti gli US già importati

## Come Usare

### Opzione A: Sincronizza Dati Esistenti (Raccomandato)

Per i dati già importati, usa lo script di sync:

```bash
# 1. Backup database (importante!)
cp pyarchinit_mini.db pyarchinit_mini.db.backup

# 2. Esegui sync
python sync_rapporti_from_relationships.py

# 3. Verifica risultati
python check_rapporti_field.py
```

**Cosa fa:**
- Legge le 488 relazioni da `us_relationships_table`
- Genera campo `rapporti` per ogni US
- Formato: `[['Copre', '2'], ['Taglia', '3']]`

**Risultato atteso:**
```
Total US updated with rapporti: 54
US with populated rapporti: 101/101  ← Tutti!
```

### Opzione B: Re-Import Dati

Se preferisci re-importare da PyArchInit:

```bash
# 1. Backup database
cp pyarchinit_mini.db pyarchinit_mini.db.backup

# 2. Via web interface:
#    - Riavvia server Flask
#    - Tools → Import/Export PyArchInit
#    - Seleziona: Import US
#    - Seleziona: ✓ Import US Relationships
#    - Start Import

# 3. Verifica
python check_rapporti_field.py
```

**Vantaggio:** Campo rapporti avrà esattamente lo stesso formato del database sorgente

## Formato Campo Rapporti

### Formato PyArchInit (Standard)

```python
# Lista di liste: [tipo_relazione, us_numero]
"[['Copre', '2'], ['Copre', '8'], ['Taglia', '5']]"
```

### Esempi

**US con più relazioni:**
```
US 1: [['Copre', '2'], ['Copre', '8'], ['Taglia', '5']]
```

**US con una relazione:**
```
US 2: [['Coperto da', '1']]
```

**US senza relazioni:**
```
US 3: []
```

## Verifica Sincronizzazione

### Script di Verifica

```bash
python check_rapporti_field.py
```

**Output atteso dopo sync:**
```
Total US records: 101
US with rapporti field populated: 101

✓ Found 101 US with rapporti field

Sample US with rapporti:
  Scavo archeologico / US 1: [['Copre', '2'], ['Taglia', '5']]...
```

### Verifica Manuale

```bash
# Conta US con rapporti
sqlite3 pyarchinit_mini.db "SELECT COUNT(*) FROM us_table WHERE rapporti IS NOT NULL AND rapporti != ''"

# Mostra esempi
sqlite3 pyarchinit_mini.db "SELECT sito, us, rapporti FROM us_table WHERE rapporti != '' LIMIT 3"
```

## Comportamento Futuro

### Durante Import

Con la modifica applicata:

1. **Campo rapporti copiato** da database sorgente
2. **Relazioni create** in `us_relationships_table`
3. **Risultato:** Entrambi popolati

### Durante Export

Quando esporti verso PyArchInit:

1. Legge da `us_relationships_table`
2. Genera campo `rapporti` al volo
3. O usa campo esistente se già popolato

### Durante Modifica Relazioni

Quando modifichi relazioni nell'interfaccia:

⚠️ **IMPORTANTE:** Devi decidere:

**Opzione 1: Aggiorna solo us_relationships_table**
- Più semplice
- Campo rapporti diventa obsoleto
- Richiede sync periodico

**Opzione 2: Aggiorna entrambi (sync automatico)**
- Richiede implementazione trigger
- Sempre consistente
- Più complesso

**Raccomandazione attuale:**
- Usa `us_relationships_table` come fonte principale
- Rigenera campo `rapporti` quando necessario con lo script sync

## Vantaggi della Sincronizzazione

### ✅ Vantaggi

1. **Compatibilità Visuale**
   - Campo rapporti visibile in interfaccia
   - Più familiare per utenti PyArchInit

2. **Backup Informazioni**
   - Relazioni in 2 formati
   - Ridondanza utile

3. **Compatibilità Legacy**
   - Codice che legge rapporti continua a funzionare
   - Migrazione graduale possibile

4. **Export Facilitato**
   - Campo già pronto per export verso PyArchInit
   - Nessuna conversione necessaria

### ⚠️ Considerazioni

1. **Duplicazione Dati**
   - Stesse info in 2 posti
   - Circa 10-20% spazio in più

2. **Sincronizzazione Manuale**
   - Dopo modifiche, esegui script sync
   - O implementa sync automatico in futuro

3. **Possibili Inconsistenze**
   - Se modifichi uno ma non l'altro
   - Script sync risolve inconsistenze

## Manutenzione

### Quando Eseguire Sync

Esegui lo script sync quando:

1. ✅ Hai importato nuovi dati
2. ✅ Hai modificato molte relazioni
3. ✅ Campo rapporti appare vuoto/obsoleto
4. ✅ Prima di un export importante

### Script Periodico (Opzionale)

Puoi schedulare il sync automaticamente:

```bash
# Crontab: Sync ogni notte alle 2 AM
0 2 * * * cd /path/to/pyarchinit-mini-desk && python sync_rapporti_from_relationships.py
```

### Rollback

Se qualcosa va storto:

```bash
# Ripristina backup
cp pyarchinit_mini.db.backup pyarchinit_mini.db
```

## FAQ

**Q: Devo re-importare tutti i dati?**
A: No! Usa lo script `sync_rapporti_from_relationships.py` per i dati esistenti.

**Q: Il campo rapporti sarà sempre aggiornato?**
A: Solo dopo import o esecuzione script sync. Per sync automatico serve implementazione trigger.

**Q: Posso modificare il campo rapporti manualmente?**
A: Sì, ma verrà sovrascritto al prossimo sync. Meglio modificare in `us_relationships_table`.

**Q: Quale è la fonte di verità?**
A: `us_relationships_table` - il campo rapporti è derivato da questa.

**Q: Cosa succede se sono inconsistenti?**
A: Lo script sync sovrascrive rapporti con dati da `us_relationships_table`.

**Q: Quanto spazio occupa?**
A: Il campo rapporti aggiunge circa 10-20% allo spazio del database.

**Q: Posso tornare indietro?**
A: Sì, il backup permette rollback. Oppure svuota il campo: `UPDATE us_table SET rapporti = ''`

## Troubleshooting

### Problema: Script Sync Fallisce

**Errore:** `Error: ...`

**Soluzione:**
1. Verifica database non corrotto: `sqlite3 pyarchinit_mini.db "PRAGMA integrity_check;"`
2. Verifica permessi scrittura
3. Controlla che us_relationships_table esista
4. Ripristina backup e riprova

### Problema: Rapporti Ancora Vuoto

**Verifica:**
```bash
python check_relationships.py
```

Se `us_relationships_table` è vuota, non c'è nulla da sincronizzare.

**Soluzione:** Import dati da PyArchInit prima.

### Problema: Formato Rapporti Diverso

Il formato generato è standard PyArchInit. Se vedi differenze:

```python
# Generato dallo script:
[['Copre', '2'], ['Taglia', '3']]

# Formato alternativo (se usato):
'copre 2, taglia 3'
```

Il formato lista è quello corretto e standard.

## Prossimi Passi

1. ✅ **Ora:** Esegui `sync_rapporti_from_relationships.py`
2. ✅ **Test:** Verifica con `check_rapporti_field.py`
3. ✅ **Usa:** Campo rapporti ora visibile in interfaccia
4. 🔄 **Futuro:** Considera implementazione sync automatico con trigger

## Versione

Implementazione: 2025-10-23
Versione PyArchInit-Mini: 1.2.17+
Script: sync_rapporti_from_relationships.py
