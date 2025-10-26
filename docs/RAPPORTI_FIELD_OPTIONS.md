# Campo Rapporti: Opzioni di Design

## Situazione Attuale

Durante l'import da PyArchInit a PyArchInit-Mini:

1. ✅ **Campo rapporti viene LETTO** dal database sorgente
2. ✅ **Relazioni vengono CREATE** nella tabella `us_relationships_table`
3. ❌ **Campo rapporti NON viene COPIATO** nel database destinazione

### Risultato

```sql
-- PyArchInit (sorgente)
us_table.rapporti = "[['Copre', '2'], ['Taglia', '3']]"

-- PyArchInit-Mini (destinazione) dopo import
us_table.rapporti = NULL o ''
us_relationships_table:
  - US 1 -> US 2 (Copre)
  - US 1 -> US 3 (Taglia)
```

## Perché È Così?

**Design di PyArchInit-Mini:**
- Approccio relazionale normalizzato
- Relazioni in tabella separata
- Migliori performance per query complesse
- Integrità referenziale garantita

**Design di PyArchInit (originale):**
- Campo TEXT con lista Python
- Formato: `"[['Copre', '2'], ['Taglia', '3']]"`
- Più semplice ma meno efficiente per query

## Opzioni Disponibili

### Opzione 1: Design Attuale (Raccomandato) ✅

**Cosa fa:**
- Relazioni SOLO in `us_relationships_table`
- Campo `rapporti` rimane vuoto

**Pro:**
- ✅ Design pulito e relazionale
- ✅ Nessuna duplicazione dati
- ✅ Query più veloci
- ✅ Integrità referenziale
- ✅ Più facile da mantenere

**Contro:**
- ❌ Non compatibile con codice che legge `rapporti`
- ❌ Campo visibilmente vuoto nell'interfaccia

**Compatibilità:**
- Harris Matrix: ✅ Funziona (legge da us_relationships_table)
- Export verso PyArchInit: ✅ Funziona (genera rapporti al volo)
- PDF Export: ✅ Funziona (usa us_relationships_table)

### Opzione 2: Copia Campo Rapporti Durante Import

**Cosa fa:**
- COPIA il campo `rapporti` AS-IS dalla sorgente
- CREA ANCHE record in `us_relationships_table`

**Pro:**
- ✅ Mantiene campo originale visibile
- ✅ Compatibilità totale con codice legacy
- ✅ Nessuna perdita di informazioni

**Contro:**
- ❌ Duplicazione dati (stesse info in 2 posti)
- ❌ Possibile inconsistenza se modificati separatamente
- ❌ Occupa più spazio

**Implementazione:**
```python
# Aggiungere in _map_us_fields_import():
'rapporti': source_data.get('rapporti'),  # ← Aggiungere questa riga
```

### Opzione 3: Sincronizzazione Automatica Bidirezionale

**Cosa fa:**
- Genera campo `rapporti` da `us_relationships_table`
- Aggiorna automaticamente quando cambiano relazioni

**Pro:**
- ✅ Single source of truth (tabella)
- ✅ Campo rapporti sempre aggiornato
- ✅ Nessuna inconsistenza possibile

**Contro:**
- ❌ Più complesso da implementare
- ❌ Overhead per mantenere sincronizzazione
- ❌ Trigger o hook necessari

**Implementazione richiesta:**
- Funzione `sync_rapporti_field()`
- Trigger su insert/update/delete in us_relationships_table
- Hook in US service

## Impatto Attuale

### Codice Che Legge dal Campo Rapporti

Ho verificato i file che accedono al campo `rapporti`:

1. **`harris_matrix/matrix_generator.py`** ✅
   - Ha FALLBACK: legge da rapporti se us_relationships_table è vuota
   - FUNZIONA con design attuale

2. **`services/import_export_service.py`** ✅
   - Usa rapporti solo per LEGGERE da sorgente
   - FUNZIONA con design attuale

3. **`pdf_export/pdf_generator.py`** ⚠️
   - Potrebbe leggere da rapporti
   - DA VERIFICARE

4. **Web/Desktop GUI** ℹ️
   - Form permettono vedere/modificare rapporti
   - Campo appare vuoto ma funzionale

### Test di Funzionalità

```bash
# Verifica stato attuale
python check_rapporti_field.py

# Risultato atteso:
# - 47 US con rapporti (dati demo)
# - 54 US senza rapporti (importati)
# - 488 relazioni in us_relationships_table
```

## Raccomandazione

### Per Utente Finale: Opzione 2 (Copia Campo)

**Perché:**
- ✅ Facilmente visibile nell'interfaccia
- ✅ Compatibilità garantita
- ✅ Implementazione semplice (1 riga di codice)

**Implementazione:**

```python
# File: pyarchinit_mini/services/import_export_service.py
# Linea: ~530 (in _map_us_fields_import)

# Text fields
'inclusi': source_data.get('inclusi'),
'campioni': source_data.get('campioni'),
'rapporti': source_data.get('rapporti'),  # ← AGGIUNGERE QUESTA RIGA
'documentazione': source_data.get('documentazione'),
'cont_per': source_data.get('cont_per'),
```

### Per Sviluppo Futuro: Opzione 3 (Sync Automatico)

Quando avremo tempo, implementare sincronizzazione bidirezionale:
- `us_relationships_table` → campo `rapporti`
- Trigger/hook automatici
- Sempre consistente

## Come Implementare Opzione 2 (Fix Immediato)

### 1. Modifica Import Service

```bash
# Edit file
nano pyarchinit_mini/services/import_export_service.py

# Vai alla linea ~527 (sezione "Text fields")
# Aggiungi:
'rapporti': source_data.get('rapporti'),
```

### 2. Test

```bash
# 1. Backup database
cp pyarchinit_mini.db pyarchinit_mini.db.backup

# 2. Re-import dati
# Via web interface: Tools → Import/Export PyArchInit

# 3. Verifica
python check_rapporti_field.py

# Risultato atteso: Tutti gli US hanno rapporti popolato
```

### 3. Verifica Consistenza

```bash
# Script per verificare che rapporti e us_relationships_table sono allineati
python verify_rapporti_consistency.py
```

## FAQ

**Q: Perché rapporti era vuoto dopo l'import?**
A: Per design - PyArchInit-Mini usa approccio relazionale, non copia il campo TEXT.

**Q: È un bug?**
A: No, è una scelta di design. Ma possiamo cambiarlo se preferisci.

**Q: Cosa succede all'export?**
A: Durante export verso PyArchInit, il campo rapporti viene GENERATO automaticamente da us_relationships_table.

**Q: Le relazioni sono perse?**
A: No! Sono in `us_relationships_table` (488 relazioni trovate).

**Q: La Harris Matrix funziona?**
A: Sì, legge da us_relationships_table (ora funziona correttamente dopo i fix).

**Q: Devo popolare il campo rapporti?**
A: Dipende:
  - **No** se usi solo PyArchInit-Mini → tabella relazioni è sufficiente
  - **Sì** se vuoi compatibilità visiva o esporti spesso verso PyArchInit

**Q: Posso avere entrambi?**
A: Sì! Opzione 2 mantiene entrambi. Opzione 3 li sincronizza automaticamente.

## Decisione

Vuoi che implementi l'Opzione 2 (copia campo rapporti durante import)?

**Vantaggi:**
- ✅ 5 minuti per implementare
- ✅ Totalmente backward compatible
- ✅ Campo visibile nell'interfaccia
- ✅ Prossimo import popolerà il campo

**Svantaggi:**
- ⚠️ Dati duplicati (tabella + campo TEXT)
- ⚠️ Se modifichi relazioni via interfaccia, devi aggiornare entrambi

Dimmi se vuoi che proceda con questa modifica!
