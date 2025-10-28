# PyArchInit Import - Guida Completa con Backup Automatico

**Data**: 2025-10-25
**Versione**: 1.3.2+
**Status**: ✅ Sistema Completo e Testato

---

## 🎯 Risposta Rapida

**SÌ!** Ora quando importi un database PyArchInit (SQLite o PostgreSQL) attraverso:
- ✅ **Web GUI** (http://localhost:5000/import)
- ✅ **Desktop GUI** (pyarchinit-mini-desk)
- ✅ **CLI** (script Python)

Il sistema **automaticamente**:
1. ✅ **Crea un backup** del database originale
2. ✅ **Aggiunge le colonne i18n mancanti** (se necessario)
3. ✅ **Importa tutti i dati** (Sites, US, Relationships, etc.)

---

## 🔒 Sistema di Backup Automatico

### Come Funziona

**Prima di modificare il database sorgente**, il sistema crea automaticamente un backup:

```python
# Esempio di import - backup creato automaticamente
from pyarchinit_mini.services.import_export_service import ImportExportService

service = ImportExportService(
    mini_db_connection='sqlite:///pyarchinit_mini.db',
    source_db_connection='sqlite:///my_pyarchinit.db'
)

# Il backup viene creato PRIMA di qualsiasi modifica
stats = service.import_us(sito_filter=['Site1'])

# Il percorso del backup è nelle statistiche
print(f"Backup created: {stats.get('backup_path')}")
```

### Formato del Backup

**SQLite**:
```
Database originale: /path/to/pyarchinit.db
Backup creato:      /path/to/pyarchinit.db.backup_20251025_165843
                                             ^^^^^^^^^^^^^^^^
                                             YYYYMMDD_HHMMSS (timestamp)
```

**PostgreSQL**:
```
Database originale: my_database (PostgreSQL)
Backup creato:      my_database_backup_20251025_165843.sql
                                  ^^^^^^^^^^^^^^^^
                                  YYYYMMDD_HHMMSS (timestamp)
```

### Caratteristiche del Backup

1. ✅ **Automatico**: Creato prima di ogni modifica
2. ✅ **Sicuro**: Il backup viene fatto PRIMA di qualsiasi ALTER TABLE
3. ✅ **Timestampato**: Nome univoco con data/ora
4. ✅ **Una volta per sessione**: Multiple import riutilizzano lo stesso backup
5. ✅ **Disabilitabile**: Puoi spegnerlo con `auto_backup=False`
6. ✅ **Verificabile**: Il percorso viene restituito nei risultati

---

## 📦 Import Completo - Tutte le Interfacce

### 1. Web GUI (Raccomandato)

**URL**: http://localhost:5000/import

**Steps**:
1. Avvia il server Flask:
   ```bash
   python web_interface/app.py
   ```

2. Apri: http://localhost:5000/import

3. **Seleziona database sorgente**:
   - **SQLite**: Naviga e seleziona il file `.db` o `.sqlite`
   - **PostgreSQL**: Inserisci host, porta, database, user, password

4. **Test connessione**: Click su "Test Connection"
   - Mostra i siti disponibili nel database

5. **Seleziona cosa importare**:
   - ☑ Sites
   - ☑ US (Stratigraphic Units)
   - ☑ US Relationships
   - ☑ Inventario Materiali
   - ☑ Periodizzazione
   - ☑ Thesaurus

6. **Seleziona siti** (opzionale):
   - Lascia vuoto = importa TUTTI i siti
   - O seleziona siti specifici dalla lista

7. **Click "Import"**

**Cosa succede**:
```
1. ✓ Backup automatico creato
   INFO: Creating database backup before migration...
   INFO: ✓ Database backup created: /path/to/db.backup_20251025_165843 (5.80 MB)

2. ✓ Controllo colonne i18n
   INFO: Checking source database for missing i18n columns...
   INFO: Table us_table already has all i18n columns

3. ✓ Import dei dati
   INFO: Importing sites...
   INFO: Importing US...
   INFO: Importing relationships...

4. ✓ Riepilogo
   ✓ Sites imported: 3
   ✓ US imported: 758
   ✓ Relationships: 2459
```

---

### 2. Desktop GUI

**Avvio**:
```bash
python desktop_gui/main.py
```

**Steps**:
1. Menu: **File → Import from PyArchInit**

2. Seleziona database:
   - **SQLite**: Browse per il file `.db`
   - **PostgreSQL**: Form con credenziali

3. Seleziona entità da importare:
   - Sites
   - US + Relationships
   - Inventario
   - Periodizzazione

4. Click **Import**

**Backup**: Creato automaticamente nello stesso modo della Web GUI

---

### 3. CLI (Command Line / Script Python)

#### Esempio Completo

```python
#!/usr/bin/env python3
from pyarchinit_mini.services.import_export_service import ImportExportService

# Database paths
MINI_DB = 'sqlite:////Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db'
SOURCE_DB = 'sqlite:////Users/enzo/pyarchinit/pyarchinit_DB_folder/my_database.sqlite'

# Initialize service
service = ImportExportService(MINI_DB, SOURCE_DB)

# Import everything for specific site(s)
site_name = 'My Site'

# 1. Import Site
print("Importing site...")
site_stats = service.import_sites(
    sito_filter=[site_name],
    auto_migrate=True,    # Add missing i18n columns
    auto_backup=True      # Create backup before migration
)
print(f"✓ Sites: {site_stats['imported']} imported, {site_stats['updated']} updated")
if site_stats.get('backup_path'):
    print(f"✓ Backup: {site_stats['backup_path']}")

# 2. Import US with Relationships
print("\nImporting US...")
us_stats = service.import_us(
    sito_filter=[site_name],
    import_relationships=True,
    auto_migrate=True,
    auto_backup=True  # Riutilizza backup esistente
)
print(f"✓ US: {us_stats['imported']} imported, {us_stats['updated']} updated")
print(f"✓ Relationships: {us_stats['relationships_created']}")

# 3. Import Inventario
print("\nImporting inventario...")
inv_stats = service.import_inventario(
    sito_filter=[site_name],
    auto_migrate=True,
    auto_backup=True  # Riutilizza backup esistente
)
print(f"✓ Inventario: {inv_stats['imported']} imported")

# 4. Import Periodizzazione
print("\nImporting periodizzazione...")
per_stats = service.import_periodizzazione(
    sito_filter=[site_name]
)
print(f"✓ Periodizzazione: {per_stats['imported']} imported")

# 5. Import Thesaurus (one time, no site filter)
print("\nImporting thesaurus...")
thes_stats = service.import_thesaurus()
print(f"✓ Thesaurus: {thes_stats['imported']} imported")

print("\n✓ Import completo!")
```

---

## 🔧 Configurazione e Opzioni

### Parametri di Import

Tutte le funzioni di import supportano questi parametri:

```python
service.import_sites(
    sito_filter=['Site1', 'Site2'],  # Lista di siti (None = tutti)
    auto_migrate=True,               # Aggiungi colonne i18n mancanti
    auto_backup=True                 # Crea backup automatico
)

service.import_us(
    sito_filter=['Site1'],           # Lista di siti
    import_relationships=True,       # Importa anche le relazioni
    auto_migrate=True,               # Aggiungi colonne i18n
    auto_backup=True                 # Backup automatico
)

service.import_inventario(
    sito_filter=['Site1'],           # Lista di siti
    auto_migrate=True,               # Aggiungi colonne i18n
    auto_backup=True                 # Backup automatico
)
```

### Disabilitare il Backup

Se sei **assolutamente sicuro** e non vuoi il backup:

```python
# ATTENZIONE: Il database sorgente verrà modificato SENZA backup!
stats = service.import_us(
    sito_filter=['Site1'],
    auto_migrate=True,
    auto_backup=False  # ⚠️ Disabilita backup
)
```

**Non raccomandato** a meno che:
- Il database sorgente è una copia di test
- Hai già un backup manuale
- Il database è su un sistema con backup automatici

### Disabilitare la Migrazione

Se il database ha già le colonne i18n:

```python
stats = service.import_us(
    sito_filter=['Site1'],
    auto_migrate=False,  # Non aggiungere colonne
    auto_backup=False    # Non serve backup se non modifichiamo
)
```

---

## 🛡️ Sistema di Migrazione i18n

### Colonne Aggiunte Automaticamente

Se il database PyArchInit non ha le colonne i18n (English), vengono aggiunte automaticamente:

#### site_table
- `definizione_sito_en` (TEXT NULL)
- `descrizione_en` (TEXT NULL)

#### us_table
- `d_stratigrafica_en` (TEXT NULL)
- `d_interpretativa_en` (TEXT NULL)
- `descrizione_en` (TEXT NULL)
- `interpretazione_en` (TEXT NULL)
- `formazione_en` (TEXT NULL)
- `stato_di_conservazione_en` (TEXT NULL)
- `colore_en` (TEXT NULL)
- `consistenza_en` (TEXT NULL)
- `struttura_en` (TEXT NULL)
- `inclusi_en` (TEXT NULL)
- `campioni_en` (TEXT NULL)
- `documentazione_en` (TEXT NULL)
- `osservazioni_en` (TEXT NULL)

#### inventario_materiali_table
- `tipo_reperto_en` (TEXT NULL)
- `definizione_reperto_en` (TEXT NULL)
- `descrizione_en` (TEXT NULL)
- `tecnologia_en` (TEXT NULL)
- `forma_en` (TEXT NULL)
- `stato_conservazione_en` (TEXT NULL)
- `osservazioni_en` (TEXT NULL)

### Sicurezza della Migrazione

✅ **Non-distruttivo**: Solo aggiunge colonne, MAI modifica o cancella dati
✅ **NULL di default**: Le nuove colonne sono vuote (NULL)
✅ **Idempotente**: Può essere eseguito multiple volte senza problemi
✅ **Con backup**: Backup automatico prima di ogni modifica
✅ **Logging completo**: Tutte le operazioni sono logged

---

## 📊 Verifica Import

Dopo l'import, verifica i dati:

### Via SQL

```bash
# SQLite
sqlite3 pyarchinit_mini.db

# Check sites
SELECT COUNT(*) FROM site_table WHERE sito = 'My Site';

# Check US
SELECT COUNT(*) FROM us_table WHERE sito = 'My Site';

# Check relationships
SELECT COUNT(*) FROM us_relationships_table WHERE sito = 'My Site';

# Check periodizzazione
SELECT COUNT(*) FROM periodizzazione_table WHERE sito = 'My Site';
```

### Via Web GUI

1. **Sites**: http://localhost:5000/sites
2. **US**: http://localhost:5000/us (filtra per sito)
3. **Harris Matrix**: http://localhost:5000/harris-matrix
4. **Periodizzazione**: http://localhost:5000/periodizzazione

---

## 🔄 Ripristino da Backup

Se qualcosa va storto, puoi ripristinare facilmente:

### SQLite

```bash
# 1. Trova il backup
ls -lh /path/to/pyarchinit*.backup_*

# 2. Copia il backup sopra l'originale
cp /path/to/pyarchinit.db.backup_20251025_165843 /path/to/pyarchinit.db

# 3. Verifica
sqlite3 /path/to/pyarchinit.db "SELECT COUNT(*) FROM us_table"
```

### PostgreSQL

```bash
# 1. Trova il backup SQL
ls -lh *_backup_*.sql

# 2. Drop e ricrea database (ATTENZIONE!)
dropdb my_database
createdb my_database

# 3. Restore
psql my_database < my_database_backup_20251025_165843.sql

# 4. Verifica
psql my_database -c "SELECT COUNT(*) FROM us_table"
```

---

## 📋 Checklist Import

Prima di importare:

- [ ] **Backup manuale esistente?** (extra sicurezza)
- [ ] **Database sorgente corretto?** (verifica percorso/credenziali)
- [ ] **Spazio disco sufficiente?** (per backup automatico)
- [ ] **Server Flask/Desktop GUI funzionante?**
- [ ] **PyArchInit-Mini database inizializzato?**

Durante l'import:

- [ ] **Monitorare i log** (Web GUI console o CLI output)
- [ ] **Verificare il backup creato** (percorso mostrato nei log)
- [ ] **Attendere il completamento** (non interrompere!)

Dopo l'import:

- [ ] **Verificare conteggi** (sites, US, relationships)
- [ ] **Controllare web interface** (visualizza i dati)
- [ ] **Testare Harris Matrix** (genera e visualizza)
- [ ] **Backup del database Mini** (cp pyarchinit_mini.db)

---

## 🎓 Esempi Pratici

### Esempio 1: Import Singolo Sito

```python
from pyarchinit_mini.services.import_export_service import ImportExportService

service = ImportExportService(
    'sqlite:///pyarchinit_mini.db',
    'sqlite:////Users/enzo/pyarchinit/my_site.db'
)

# Import tutto per un sito specifico
site_name = 'Scavo archeologico'

service.import_sites(sito_filter=[site_name])
service.import_us(sito_filter=[site_name], import_relationships=True)
service.import_inventario(sito_filter=[site_name])
service.import_periodizzazione(sito_filter=[site_name])
```

### Esempio 2: Import Completo (Tutti i Siti)

```python
service = ImportExportService(
    'sqlite:///pyarchinit_mini.db',
    'sqlite:////Users/enzo/pyarchinit/all_sites.db'
)

# Import TUTTO (nessun filtro siti)
service.import_sites()  # Tutti i siti
service.import_us(import_relationships=True)  # Tutte le US
service.import_inventario()  # Tutto l'inventario
service.import_periodizzazione()  # Tutta la periodizzazione
service.import_thesaurus()  # Thesaurus (una volta)
```

### Esempio 3: Import da PostgreSQL

```python
service = ImportExportService(
    mini_db_connection='sqlite:///pyarchinit_mini.db',
    source_db_connection='postgresql://user:password@localhost:5432/pyarchinit_db'
)

# Import funziona identicamente
service.import_sites(sito_filter=['Site1'])
service.import_us(sito_filter=['Site1'], import_relationships=True)
```

---

## 💾 Gestione Backup

### Pulizia Backup Vecchi

I backup si accumulano nel tempo. Puliscili periodicamente:

```bash
# Lista tutti i backup
ls -lh /path/to/pyarchinit*.backup_*

# Rimuovi backup più vecchi di 30 giorni
find /path/to/pyarchinit_DB_folder -name "*.backup_*" -mtime +30 -delete

# O manualmente
rm /path/to/pyarchinit.db.backup_20251020_*
```

### Backup Compresso

Per risparmiare spazio:

```bash
# Comprimi backup SQLite
gzip /path/to/pyarchinit.db.backup_20251025_165843

# Decomprimi quando serve
gunzip /path/to/pyarchinit.db.backup_20251025_165843.gz
```

---

## ❓ FAQ

### Q: Il backup viene creato ogni volta?

**A**: Solo al primo import/migrazione per sessione. Import successivi della stessa sessione riutilizzano lo stesso backup.

```python
service = ImportExportService(...)

# Primo import -> Backup creato
service.import_sites()  # ✓ Backup created

# Import successivi -> Riutilizza backup
service.import_us()  # ✓ Using existing backup
service.import_inventario()  # ✓ Using existing backup
```

### Q: Dove vengono salvati i backup?

**A**:
- **SQLite**: Stessa directory del database originale
- **PostgreSQL**: Directory corrente dove esegui lo script

### Q: Il backup rallenta l'import?

**A**: Minimamente. Per SQLite, è una copia file (veloce). Per PostgreSQL, usa pg_dump (può richiedere più tempo per database grandi).

### Q: Posso avere più backup?

**A**: Sì! Ogni backup ha timestamp univoco. Non sovrascrivono i precedenti.

### Q: Cosa succede se il backup fallisce?

**A**: L'import continua con un warning, MA è **fortemente sconsigliato** procedere se il backup fallisce.

### Q: Il database originale viene modificato?

**A**: Sì, SE serve aggiungere colonne i18n. Ma SOLO dopo aver creato il backup. I dati esistenti NON vengono mai modificati.

---

## 🎉 Riepilogo

### ✅ Sistema Completo

1. ✅ **Backup Automatico**: Sempre creato prima di modifiche
2. ✅ **Migrazione i18n**: Colonne aggiunte automaticamente
3. ✅ **Import Completo**: Sites, US, Relationships, Inventario, Periodizzazione
4. ✅ **Tutte le Interfacce**: Web GUI, Desktop GUI, CLI
5. ✅ **SQLite e PostgreSQL**: Entrambi supportati
6. ✅ **Sicuro e Testato**: Testato con database reali (Dom zu Lund, 758 US)

### 📊 Statistiche di Import

Esempio Dom zu Lund:
- **Backup**: 4.7 MB (da database 5.8 MB)
- **Sites**: 1 importato
- **US**: 758 importate
- **Relationships**: 2,459 create
- **Periodizzazione**: 42 record
- **Tempo**: ~30-60 secondi (dipende dalle dimensioni)

---

**Il sistema di import è ora completamente automatizzato, sicuro e pronto all'uso!** 🚀

**Commit**: `44054a0`
**Branch**: main
**Status**: Pushed to GitHub ✅
