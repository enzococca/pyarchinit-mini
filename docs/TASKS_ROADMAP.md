# PyArchInit-Mini v1.7.4 - Tasks Roadmap

## ✅ Task Completati

### 1. ✅ Database Migration Tool
- **Status**: Completato
- **Files Creati**:
  - `pyarchinit_mini/cli/migrate.py` - CLI tool
  - `scripts/migrate_database_schema.py` - Standalone script
  - `docs/DATABASE_MIGRATION.md` - Documentazione
- **CLI Command**: `pyarchinit-mini-migrate`
- **Versione**: 1.7.4

---

## 📋 PRIORITÀ 1 - DATABASE (Tasks 2-7)

### 2. 🔄 Move 'Create Empty Database' to Database Management
**Status**: In Progress
**Complessità**: Media
**Tempo stimato**: 30 min

**Files da Modificare**:
1. `pyarchinit_mini/web_interface/templates/admin/database.html`
   - Aggiungere sezione "Create Empty Database"
2. `pyarchinit_mini/web_interface/templates/pyarchinit_import_export/index.html`
   - Rimuovere il tab "Create Empty Database" (righe 33-38, 401-480)
3. `pyarchinit_mini/web_interface/pyarchinit_import_export_routes.py`
   - Spostare la route `/api/pyarchinit/create-database` nel file admin
4. `pyarchinit_mini/web_interface/admin_routes.py`
   - Aggiungere la route per create database

**Modifiche Necessarie**:
- La nuova UI dovrebbe essere più semplice: nome database + tipo (SQLite/PostgreSQL)
- Default path: `~/.pyarchinit_mini/data/[nome].db`

### 3. 🔄 Ensure Empty Database Uses Default Folder
**Status**: Pending
**Complessità**: Bassa
**Tempo stimato**: 15 min

**Files da Modificare**:
1. `pyarchinit_mini/database/database_creator.py`
   - Modificare `create_empty_database()` per usare path di default se non specificato
   - Default path: `~/.pyarchinit_mini/data/`

**Codice da Aggiungere**:
```python
def create_empty_database(db_type='sqlite', db_config=None, overwrite=False, use_default_path=True):
    if use_default_path and db_type == 'sqlite':
        from pathlib import Path
        default_dir = Path.home() / '.pyarchinit_mini' / 'data'
        default_dir.mkdir(parents=True, exist_ok=True)
        db_config = str(default_dir / 'pyarchinit_empty.db')
```

### 4. 🔄 Web App Sample Database
**Status**: Pending
**Complessità**: Media
**Tempo stimato**: 20 min

**Files da Verificare/Modificare**:
1. `pyarchinit_mini/cli/__init__.py` - comando `pyarchinit-mini-init`
2. `data/pyarchinit_mini_sample.db` - verificare che esista
3. Setup.py - assicurarsi che il sample DB sia incluso nel package

**Check Necessari**:
- ✅ Verificare se `pyarchinit-mini-init` copia già un DB di esempio
- ⚠️  Creare sample DB con dati in INGLESE se non esiste

### 5. 🔄 Desktop GUI Sample Database
**Status**: Pending
**Complessità**: Media
**Tempo stimato**: 20 min

**Files da Verificare**:
1. `pyarchinit_mini/desktop_gui/main.py` - verificare inizializzazione
2. Verificare se la GUI usa lo stesso meccanismo della web app

### 6. 🔄 Verify Empty Database Schema
**Status**: Pending
**Complessità**: Bassa
**Tempo stimato**: 15 min

**Test da Eseguire**:
```bash
# Creare DB vuoto
pyarchinit-mini-migrate --create-empty test.db

# Verificare schema
sqlite3 test.db ".schema" | wc -l  # Dovrebbe avere ~30 tabelle

# Testare con web app
DATABASE_URL="sqlite:///test.db" pyarchinit-mini-web
```

### 7. 🔄 Verify PostgreSQL Support
**Status**: Pending
**Complessità**: Media
**Tempo stimato**: 30 min

**Test da Eseguire**:
```python
# Test PostgreSQL connection
from pyarchinit_mini.database.database_creator import create_empty_database

config = {
    'host': 'localhost',
    'port': '5432',
    'database': 'test_pyarchinit',
    'user': 'postgres',
    'password': 'password'
}

result = create_empty_database('postgresql', config)
print(result)
```

---

## 📋 PRIORITÀ 2 - MEDIA SYSTEM (Tasks 8-15)

### 8. 🔄 Media List Viewer
**Status**: Pending
**Complessità**: Alta
**Tempo stimato**: 2 ore

**Files da Creare/Modificare**:
1. **Nuovo**: `pyarchinit_mini/web_interface/templates/media/list.html`
2. **Nuovo**: `pyarchinit_mini/web_interface/media_routes.py` - route `/media/list`
3. **Modificare**: `pyarchinit_mini/models/media.py` - verificare model

**Features Richieste**:
- Lista di tutti i media caricati
- Thumbnail preview per immagini
- Icone per PDF, DOCX, etc
- Link per aprire/download file
- Filtro per tipo file
- Cerca per nome file
- Visualizza record associato (Site/US/Inventory)

**UI Mockup**:
```
╔════════════════════════════════════════════════╗
║  Media Files                              [🔍] ║
║  ┌──────────────────────────────────────────┐ ║
║  │ 📷 IMG_001.jpg  Site: Roma, Area 1      │ ║
║  │ 📄 Report.pdf   US: 1001                │ ║
║  │ 🎥 Video.mp4    Inventory: Pottery 5     │ ║
║  └──────────────────────────────────────────┘ ║
╚════════════════════════════════════════════════╝
```

### 9. 🔄 3D File Support
**Status**: Pending
**Complessità**: Alta
**Tempo stimato**: 3 ore

**Files da Creare/Modificare**:
1. **Modificare**: `pyarchinit_mini/web_interface/templates/media/upload.html`
   - Accettare formati 3D: .obj, .ply, .stl, .glb, .gltf
2. **Nuovo**: `pyarchinit_mini/web_interface/templates/media/viewer_3d.html`
   - Usare Three.js per visualizzazione 3D
3. **Modificare**: `pyarchinit_mini/web_interface/media_routes.py`
   - Gestire upload 3D

**Libraries Necessarie**:
- Three.js (già disponibile?)
- OrbitControls for Three.js

### 10-12. 🔄 Media Tabs in Forms (Site/US/Inventory)
**Status**: Pending
**Complessità**: Alta (x3)
**Tempo stimato**: 2 ore ciascuna = 6 ore totali

**Files da Modificare**:
1. `pyarchinit_mini/web_interface/templates/sites/form.html`
2. `pyarchinit_mini/web_interface/templates/us/form.html`
3. `pyarchinit_mini/web_interface/templates/inventario/form.html`

**Struttura Tab Media** (per ogni form):
```html
<ul class="nav nav-tabs">
    <li><a href="#general">General</a></li>
    <li><a href="#media">Media Files</a></li>  <!-- NUOVO -->
</ul>

<div class="tab-pane" id="media">
    <!-- Lista media associati -->
    <div id="associated-media">
        <!-- Thumbnail + nome file + azioni -->
    </div>

    <!-- Drag & drop upload area -->
    <div id="dropzone">
        Drop files here or click to upload
    </div>
</div>
```

### 13-15. 🔄 Drag-and-Drop Media Upload
**Status**: Pending
**Complessità**: Media (x3)
**Tempo stimato**: 1 ora ciascuna = 3 ore totali

**JavaScript da Aggiungere** (nei form):
```javascript
// In sites/form.html, us/form.html, inventario/form.html
const dropzone = document.getElementById('dropzone');

dropzone.addEventListener('drop', async (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;

    for (let file of files) {
        await uploadMediaFile(file, recordId, recordType);
    }

    refreshMediaList();
});
```

---

## 📋 PRIORITÀ 3 - TRANSLATIONS (Tasks 16-19)

### 16. 🔄 Convert Sample Databases to English
**Status**: Pending
**Complessità**: Media
**Tempo stimato**: 1 ora

**Database da Modificare**:
1. `data/pyarchinit_mini_sample.db`
2. `data/pyarchinit_tutorial.db`

**Dati da Tradurre**:
```sql
-- Esempio site_table
UPDATE site_table SET
    definizione_sito = 'Archaeological excavation',
    descrizione = 'Roman forum excavation site',
    definizione_sito_en = 'Archaeological excavation',
    descrizione_en = 'Roman forum excavation site'
WHERE sito = 'Roma';

-- Esempio us_table
UPDATE us_table SET
    d_stratigrafica = 'Stone wall foundation',
    d_interpretativa = 'Roman period wall',
    d_stratigrafica_en = 'Stone wall foundation',
    d_interpretativa_en = 'Roman period wall';
```

### 17. 🔄 Translate Thesaurus Form
**Status**: Pending
**Complessità**: Bassa
**Tempo stimato**: 30 min

**Files da Modificare**:
1. `pyarchinit_mini/web_interface/templates/thesaurus/list.html`

**Stringhe da Tradurre**:
- Cercare tutte le stringhe hardcoded in italiano
- Usare `{{ _('...') }}` per gettext
- Verificare traduzioni in `translations/en/LC_MESSAGES/messages.po`

### 18. 🔄 Translate Upload Form
**Status**: Pending
**Complessità**: Bassa
**Tempo stimato**: 30 min

**Files da Modificare**:
1. `pyarchinit_mini/web_interface/templates/media/upload.html`

**Check**:
```bash
grep -r "Carica\|Seleziona\|File" pyarchinit_mini/web_interface/templates/media/upload.html
```

### 19. 🔄 Translate Site Form
**Status**: Pending
**Complessità**: Bassa
**Tempo stimato**: 30 min

**Files da Modificare**:
1. `pyarchinit_mini/web_interface/templates/sites/form.html`

**Check**:
```bash
grep -r "Nuovo\|Crea\|Sito" pyarchinit_mini/web_interface/templates/sites/form.html
```

---

## 📊 Stima Totale Tempo

| Priorità | Tasks | Tempo Stimato | Note |
|----------|-------|---------------|------|
| ✅ Completato | 1 | - | Migration tool |
| 🔴 Database | 2-7 | 2.5 ore | Fondamentale |
| 🟡 Media | 8-15 | 17 ore | Feature complessa |
| 🟢 Traduzioni | 16-19 | 3 ore | Miglioramento UX |
| **TOTALE** | **19** | **22.5 ore** | **Lavoro sostanziale** |

## 🎯 Raccomandazioni

### Per Questa Sessione (Token rimasti: ~90k)
Completa solo:
- ✅ Task 2-3: Spostare Create Empty Database (45 min)
- ✅ Task 4-6: Verificare sample DB e schema (55 min)
- **Totale**: ~1.5 ore di lavoro

### Sessione Futura 1 - Media System
- Task 8-15: Sistema media completo
- Stima: 17 ore

### Sessione Futura 2 - Traduzioni & Polish
- Task 16-19: Traduzioni
- Task 7: Test PostgreSQL
- Stima: 3.5 ore

---

*Documento creato: Ottobre 2025*
*Versione: 1.7.4*
