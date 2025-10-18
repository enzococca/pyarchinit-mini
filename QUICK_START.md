# PyArchInit-Mini Web Interface - Quick Start

**Versione: 1.0.0** - Parità 100% Desktop GUI ✅

---

## 🚀 Avvio Rapido

### 1. Avvia la Web App
```bash
cd /Users/enzo/Documents/pyarchinit-mini-desk
PYTHONPATH=. python web_interface/app.py
```

### 2. Accedi all'interfaccia
```
http://localhost:5001
```

---

## 📋 Funzionalità Complete

### ✅ Gestione Dati
- **Siti**: Crea, modifica, visualizza, esporta PDF
- **US**: Form completo 49 campi, 6 tab, esporta PDF
- **Inventario**: Form completo 37 campi, 8 tab, thesaurus ICCD, esporta PDF

### ✅ Harris Matrix
- **Matplotlib**: Visualizzazione semplice
- **Graphviz**: 4 modalità (period_area, period, area, none)
- **PDF Export**: Harris Matrix embedded ad alta risoluzione

### ✅ Validazione Stratigrafici
- Rilevamento paradossi
- Rilevamento cicli
- Rapporti reciproci mancanti
- Auto-fix automatico

### ✅ Database Management
- Upload file SQLite (.db)
- Connessione PostgreSQL remoti
- Connessione SQLite locali
- Info e statistiche database

### ✅ Export PDF
- **Siti**: Relazione completa + Harris Matrix
- **US**: Lista filtrata + schede singole
- **Inventario**: Lista filtrata + schede singole
- Formato identico Desktop GUI

---

## 🎯 Test Funzionalità Principali

### Test 1: Crea Sito e US
1. Dashboard → **Siti** → **Nuovo Sito**
2. Compila form → **Salva**
3. **US** → **Nuova US**
4. Seleziona sito, compila 6 tab → **Salva**

### Test 2: Harris Matrix
1. **Siti** → Sito → **Matrix** dropdown → **Graphviz (Desktop GUI)**
2. Prova 4 modalità: Periodo+Area, Solo Periodo, Solo Area, Nessuno
3. **Download PNG** per salvare immagine

### Test 3: Validazione
1. **Siti** → Sito → **Valida** (button warning)
2. Verifica report: paradossi, cicli, reciproci mancanti
3. Se ci sono reciproci mancanti → **Applica Auto-Fix**

### Test 4: Export PDF
1. **Siti** → **PDF** dropdown → **Harris Matrix PDF**
2. Verifica PDF con matrice embedded
3. **US** → **Esporta PDF** (lista completa)
4. **Inventario** → **Esporta PDF** (lista completa)

### Test 5: Database Upload
1. **Database** (navbar top-right)
2. **Carica Database SQLite** → Seleziona file .db
3. Verifica upload e connessione salvata

---

## 📊 Navigazione Rapida

### Menu Principale (Navbar)
- **Dashboard**: Statistiche e overview
- **Siti**: Gestione siti archeologici
- **US**: Unità stratigrafiche
- **Inventario**: Reperti materiali
- **Media**: Upload foto/documenti
- **Harris Matrix**: Visualizzatori
- **Database**: Amministrazione database
- **API Docs**: Documentazione API REST

### Sidebar
- **Navigazione**: Siti, US, Inventario
- **Strumenti**: Carica Media
- **Amministrazione**: Gestione Database

---

## 📁 Struttura Progetto

```
pyarchinit-mini-desk/
├── pyarchinit_mini/          # Core library
│   ├── models/               # SQLAlchemy models
│   ├── services/             # Business logic
│   ├── harris_matrix/        # Matrix generators
│   ├── pdf_export/           # PDF generators
│   └── utils/                # Validators, utilities
├── web_interface/            # Flask web app
│   ├── app.py                # Main Flask app (1200+ righe)
│   ├── templates/            # HTML templates (20+)
│   └── static/               # CSS, JS, images
├── data/                     # Sample databases
├── databases/                # Uploaded databases
└── uploads/                  # Uploaded media
```

---

## 🔧 Database di Test

### Database di Esempio Incluso
```
data/pyarchinit_mini_sample.db
```

**Contenuto**:
- 1 sito archeologico
- 50 US con rapporti stratigrafici
- Inventario materiali
- Dati completi per test

### Usa Database di Esempio
```bash
export DATABASE_URL="sqlite:///./data/pyarchinit_mini_sample.db"
PYTHONPATH=. python web_interface/app.py
```

---

## 📖 Report Dettagliati

Leggi i report per dettagli implementazione:

1. **COMPLETE_REPORT.md** - Overview 100% parità Desktop GUI
2. **GRAPHVIZ_INTEGRATION_REPORT.md** - Dettagli Graphviz
3. **DATABASE_UPLOAD_REPORT.md** - Dettagli database management
4. **STATUS_REPORT.md** - Status implementazione fasi

---

## 🎯 Prossimi Passi (Opzionali)

### Enhancement Futuri (Non Bloccanti):
- [ ] Autenticazione utenti (login/logout)
- [ ] Permessi ruoli (admin, editor, viewer)
- [ ] Export Excel per liste
- [ ] Import batch CSV
- [ ] API REST authentication
- [ ] WebSocket real-time updates
- [ ] Chart analytics dashboard

### Deployment:
- [ ] Containerizzazione Docker
- [ ] Deploy su Heroku/AWS/DigitalOcean
- [ ] Setup database PostgreSQL produzione
- [ ] CI/CD pipeline
- [ ] Backup automatici

---

## 💡 Tips & Tricks

### Performance
- Usa filtri per limitare query grandi
- Limite export PDF: 500 record
- Cache browser per assets statici

### Sicurezza
- Cambia `SECRET_KEY` in produzione
- Usa PostgreSQL per produzione
- Abilita HTTPS in produzione
- Valida upload files

### Database
- Backup regolari con dump
- Usa migrazioni per schema changes
- Monitor query slow con logging

---

## 🆘 Troubleshooting

### Port 5001 Already in Use
```bash
# Cambia porta
export PYARCHINIT_WEB_PORT=5002
python web_interface/app.py
```

### Database Connection Error
```bash
# Verifica DATABASE_URL
echo $DATABASE_URL

# Reset a default
unset DATABASE_URL
```

### Import Errors
```bash
# Verifica PYTHONPATH
export PYTHONPATH=/Users/enzo/Documents/pyarchinit-mini-desk
```

### PDF Generation Error
```bash
# Installa Graphviz se mancante
brew install graphviz  # macOS
```

---

## ✅ Checklist Pre-Produzione

- [x] Tutte le funzionalità testate
- [x] PDF export funzionante
- [x] Harris Matrix Graphviz funzionante
- [x] Database upload funzionante
- [x] Validazione stratigrafici funzionante
- [ ] SECRET_KEY cambiato
- [ ] DATABASE_URL produzione configurato
- [ ] HTTPS abilitato
- [ ] Backup database configurato
- [ ] Monitoring/logging configurato

---

**PyArchInit-Mini Web Interface v1.0.0**
*100% Desktop GUI Parity Achieved* ✅

**Pronto per Produzione!** 🚀
