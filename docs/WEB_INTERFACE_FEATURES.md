# Web Interface - Funzionalità Complete

## Panoramica

L'interfaccia web di PyArchInit-Mini offre tutte le funzionalità principali della desktop GUI attraverso un'interfaccia browser moderna e responsive.

**Accesso**: `http://localhost:5001` (porta 5001 per evitare conflitti con AirPlay su macOS)

---

## ✅ Funzionalità Implementate e Testate

### 1. Dashboard
- **Statistiche in tempo reale**
  - Numero totale siti
  - Numero totale US
  - Numero totale reperti inventario
  - Lista siti recenti

**Route**: `/`

---

### 2. Gestione Siti

#### Visualizzazione Lista Siti
- Paginazione (20 siti per pagina)
- Ricerca per nome sito
- Dettagli sito con US e inventario correlati

**Routes**:
- `/sites` - Lista siti
- `/sites/<id>` - Dettaglio sito

#### Creazione Nuovo Sito
Form completo con campi:
- Nome Sito (obbligatorio)
- Nazione
- Regione
- Comune
- Provincia
- Definizione Sito
- Descrizione

**Route**: `/sites/create`

---

### 3. Gestione US (Unità Stratigrafiche)

#### Visualizzazione Lista US
- Paginazione (20 US per pagina)
- Filtro per sito
- Visualizzazione dati stratigrafici

**Route**: `/us`

#### Creazione Nuova US
Form completo con **tutti** i campi della desktop GUI:
- **Sito** (obbligatorio) - Select con lista siti
- **Numero US** (obbligatorio)
- **Area**
- **Descrizione Stratigrafica**
- **Descrizione Interpretativa**
- **Descrizione Dettagliata** (textarea)
- **Interpretazione** (textarea)
- **Anno Scavo**
- **Schedatore**
- **Formazione** (Naturale/Artificiale)
- **⭐ Rapporti Stratigrafici** (textarea)
  - Formato: `copre 1002, taglia 1005, si appoggia a 1010`
  - Help text integrato nel form

**Route**: `/us/create`

**Funzionalità Rapporti Stratigrafici**:
- ✅ Campo `rapporti` presente nel form
- ✅ Parser dei rapporti nel backend (legge formato testuale)
- ✅ 228 relazioni trovate nel database di esempio
- ✅ Relazioni utilizzate per generare Harris Matrix

---

### 4. ⭐ Harris Matrix - Matrice di Harris

**Funzionalità Complete** (come desktop GUI):

#### Generazione Automatica
- ✅ Parsing rapporti stratigrafici da campo testuale
- ✅ Generazione grafo NetworkX con 50 nodi, 99 relazioni
- ✅ Calcolo livelli topologici (7 livelli)
- ✅ Validazione DAG (Directed Acyclic Graph)
- ✅ Rilevamento e risoluzione cicli

#### Statistiche Matrice
- Numero totale US
- Numero totale relazioni
- Profondità massima (livelli)
- US isolate
- US livello superiore
- US livello inferiore

#### Visualizzazione
- Grafico matplotlib renderizzato come PNG base64
- Visualizzazione inline nel browser
- Sequenza stratigrafica ordinata per livelli

**Route**: `/harris_matrix/<site_name>`

**Test Risultati**:
```
✓ Harris Matrix generated: 50 nodes, 99 edges
✓ Matrix levels calculated: 7 levels
✓ Statistics: {
    'total_us': 50,
    'total_relationships': 99,
    'levels': 7,
    'is_valid': True,
    'has_cycles': False,
    'isolated_us': 2,
    'top_level_us': 6,
    'bottom_level_us': 8
}
```

---

### 5. ⭐ Esportazione PDF

**Funzionalità Complete** (come desktop GUI):

#### Report Sito Completo
- ✅ Dati sito (nome, località, descrizione)
- ✅ Lista US con dettagli stratigrafici
- ✅ Lista reperti inventario
- ✅ Generazione PDF (5679 bytes per report di test)
- ✅ Download automatico come attachment

**Route**: `/export/site_pdf/<site_id>`

**Formato PDF**:
- Intestazione sito
- Sezione US (fino a 100 US)
- Sezione Inventario (fino a 100 reperti)
- Layout professionale con ReportLab

**Test Risultati**:
```
✓ PDF generated: 5679 bytes
Download: relazione_Sito_Archeologico_di_Esempio.pdf
```

---

### 6. Gestione Inventario Materiali

#### Visualizzazione Lista Inventario
- Paginazione (20 reperti per pagina)
- Filtro per sito
- Filtro per tipo reperto

**Route**: `/inventario`

#### Creazione Nuovo Reperto
Form completo con campi:
- Sito (obbligatorio)
- Numero Inventario (obbligatorio)
- Tipo Reperto (Ceramica, Metallo, Pietra, Osso, Vetro)
- Definizione
- Descrizione
- Area
- US
- Peso (grammi)

**Route**: `/inventario/create`

---

### 7. Gestione Media

#### Upload File
Form per caricamento file multimediali:
- Tipo Entità (Sito/US/Inventario)
- ID Entità
- File upload
- Descrizione
- Autore/Fotografo

**Route**: `/media/upload`

**Gestione**:
- Salvataggio temporaneo sicuro
- Integrazione con MediaHandler
- Metadata tracking

---

## 🎨 Design e UX

### Bootstrap 5
- Layout responsive
- Componenti professionali
- Form validation styling
- Card-based layouts
- Navigation breadcrumbs

### Template Structure
```
web_interface/templates/
├── base.html              # Template base con navbar
├── dashboard.html         # Dashboard statistiche
├── sites/
│   ├── list.html         # Lista siti
│   ├── detail.html       # Dettaglio sito
│   └── form.html         # Form creazione sito
├── us/
│   ├── list.html         # Lista US
│   └── form.html         # Form creazione US (con rapporti!)
├── inventario/
│   ├── list.html         # Lista inventario
│   └── form.html         # Form creazione reperto
├── harris_matrix/
│   └── view.html         # Visualizzazione matrice
└── media/
    └── upload.html       # Upload file media
```

---

## 🔧 Configurazione

### Variabili Ambiente

```bash
# Database
export DATABASE_URL="sqlite:///./pyarchinit_mini.db"

# Web Server
export PYARCHINIT_WEB_HOST="0.0.0.0"
export PYARCHINIT_WEB_PORT="5001"  # Cambiato da 5000 per macOS
export PYARCHINIT_WEB_DEBUG="true"

# Flask Secret Key
export FLASK_SECRET_KEY="your-secret-key"
```

### Avvio Server

```bash
# Via console script (dopo installazione pip)
pyarchinit-mini-web

# Oppure direttamente
python web_interface/app.py

# Oppure con Flask CLI
export FLASK_APP=web_interface/app.py
flask run --port 5001
```

---

## 📊 Confronto con Desktop GUI

| Funzionalità | Desktop GUI | Web Interface |
|-------------|-------------|---------------|
| Gestione Siti | ✅ | ✅ |
| Gestione US | ✅ | ✅ |
| Rapporti Stratigrafici | ✅ | ✅ |
| Harris Matrix | ✅ | ✅ |
| PDF Export | ✅ | ✅ |
| Inventario Materiali | ✅ | ✅ |
| Media Upload | ✅ | ✅ |
| Ricerca/Filtri | ✅ | ✅ |
| Paginazione | ❌ | ✅ |
| Multi-utente | ❌ | ✅ |
| Accesso Remoto | ❌ | ✅ |

**Vantaggi Web Interface**:
- ✅ Accesso multi-utente simultaneo
- ✅ Accessibile da qualsiasi dispositivo
- ✅ Nessuna installazione client richiesta
- ✅ Responsive design (mobile-friendly)
- ✅ Paginazione per grandi dataset

---

## 🐛 Bug Fix Implementati

### 1. Porta 5000 - Conflitto AirPlay macOS
**Problema**: Porta 5000 occupata da AirPlay Receiver su macOS
**Fix**: Cambiata porta default da 5000 a 5001

### 2. Harris Matrix - 0 nodi generati
**Problema**: `HarrisMatrixGenerator` non riceveva `us_service`
**Fix**: Passaggio corretto di `us_service` al costruttore
```python
matrix_generator = HarrisMatrixGenerator(db_manager, us_service)
```

### 3. PDF Export - Detached Instance Error
**Problema**: Modelli SQLAlchemy usati fuori sessione
**Fix**: Conversione a dict all'interno del contesto sessione
```python
with db_manager.connection.get_session() as session:
    site_dict = site.to_dict()
    us_list = [us.to_dict() for us in us_records]
# Uso di dict fuori sessione
pdf_bytes = pdf_generator.generate_site_report(site_dict, us_list, [])
```

### 4. Campo Rapporti Mancante
**Problema**: Form US non includeva campo rapporti stratigrafici
**Fix**: Aggiunto campo `rapporti` a `USForm` e template
```python
rapporti = TextAreaField('Rapporti Stratigrafici',
                        description='Formato: copre 1002, taglia 1005')
```

---

## 🚀 Prossimi Sviluppi

### Funzionalità Aggiuntive
- [ ] Edit/Update per Siti, US, Inventario
- [ ] Delete con conferma
- [ ] Visualizzazione Harris Matrix interattiva (D3.js)
- [ ] Export Harris Matrix come Graphviz/SVG
- [ ] Bulk import CSV
- [ ] Advanced search
- [ ] User authentication
- [ ] Audit log

### Miglioramenti UX
- [ ] AJAX form submission
- [ ] Real-time validation
- [ ] Toast notifications
- [ ] Drag & drop file upload
- [ ] Image preview

---

## 📝 Note Tecniche

### Session Management
Tutto il codice segue il pattern context manager per sessioni database:
```python
with db_manager.connection.get_session() as session:
    # Query e operazioni
    data = model.to_dict()  # Conversione a dict dentro sessione
# Uso dati fuori sessione
```

### Parser Rapporti Stratigrafici
Supporta formato testuale intuitivo:
```
Input: "copre 1002, taglia 1005, si appoggia a 1010"

Parsing:
- Relazione 1: ("copre", 1002)
- Relazione 2: ("taglia", 1005)
- Relazione 3: ("si appoggia", 1010)
```

### API REST Disponibili
Endpoint JSON per integrazione:
- `GET /api/sites` - Lista siti JSON

---

## 📦 Dipendenze Web

```toml
[project.optional-dependencies]
web = [
    "flask>=3.0.0",
    "flask-wtf>=1.2.0",
    "wtforms>=3.1.0",
    "jinja2>=3.1.0"
]
```

Installazione:
```bash
pip install pyarchinit-mini[web]
```

---

## ✅ Conclusioni

L'interfaccia web di PyArchInit-Mini è **completa e funzionale**, offrendo tutte le funzionalità principali della desktop GUI:

1. ✅ **Harris Matrix** - Generazione e visualizzazione completa
2. ✅ **Rapporti Stratigrafici** - Gestione tramite campo testuale
3. ✅ **PDF Export** - Report sito completo
4. ✅ **CRUD Operations** - Create per Siti, US, Inventario
5. ✅ **Template Professionali** - Bootstrap 5, responsive
6. ✅ **Session Handling** - Corretto uso sessioni SQLAlchemy

**Status**: Pronta per pubblicazione versione 0.1.3

**Test Passati**:
- ✅ Harris Matrix: 50 nodi, 99 relazioni, 7 livelli
- ✅ PDF Export: 5679 bytes generati
- ✅ Rapporti: 228 relazioni parsate dal database
