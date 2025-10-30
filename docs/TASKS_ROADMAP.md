# PyArchInit-Mini v1.7.4 - Tasks Roadmap

## ✅ Tasks Completati (1-7, 16)

### 1. ✅ Database Migration Tool
- **Status**: ✅ Completato
- **Commit**: `8889b97`
- **Files Creati**:
  - `pyarchinit_mini/cli/migrate.py` - CLI tool
  - `scripts/migrate_database_schema.py` - Standalone script
  - `docs/DATABASE_MIGRATION.md` - Documentazione
- **CLI Command**: `pyarchinit-mini-migrate`

### 2-3. ✅ Database Creation Reorganization
- **Status**: ✅ Completato
- **Commit**: `c8f3264`
- **Changes**:
  - Moved "Create Empty Database" to Database Management section
  - Simplified UI (only database name required)
  - Default path: `~/.pyarchinit_mini/data/`
  - Added `use_default_path` parameter to database_creator.py

### 4-7. ✅ Sample Database Distribution & Verification
- **Status**: ✅ Completato
- **Commit**: `779cbfd`
- **Changes**:
  - Added `data/*.db` to package_data in setup.py and pyproject.toml
  - Added `pyarchinit-mini-migrate` to pyproject.toml scripts
  - Verified empty database schema (15 tables, all Extended Matrix + i18n fields)
  - Verified PostgreSQL support code

### 16. ✅ English Sample Database
- **Status**: ✅ Completato
- **Commit**: `528c0df`
- **Changes**:
  - Replaced Italian sample DB with English tutorial DB
  - 3 archaeological sites with complete English data
  - Ready for international users

---

## 📋 PRIORITÀ 2 - MEDIA SYSTEM (Tasks 8-15)
**Status**: 🔄 In Progress

### 8. 🔄 Media List Viewer
**Status**: In Progress
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

## 📋 PRIORITÀ 3 - TRANSLATIONS (Tasks 17-19)

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

## 📊 Progress Summary

| Priorità | Tasks | Status | Completato |
|----------|-------|--------|------------|
| ✅ Database & Migration | 1-7 | Completato | 100% (7/7) |
| 🔄 Media System | 8-15 | In Progress | 0% (0/8) |
| 🔄 Traduzioni | 16-19 | In Progress | 25% (1/4) |
| **TOTALE** | **1-19** | **42% Complete** | **8/19 tasks** |

## 🎯 Next Steps

### Current Priority - Media System (Tasks 8-15)
Starting with Task 8: Media List Viewer
- Create `/media/list` route and template
- Display all uploaded media files
- Add thumbnail previews and file type icons
- Implement search and filtering
- Show associated records (Site/US/Inventory)

---

*Documento creato: Ottobre 2025*
*Versione: 1.7.4*
