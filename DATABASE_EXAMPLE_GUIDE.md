# Guida al Database di Esempio - PyArchInit-Mini

Questa guida spiega come utilizzare il database di esempio creato per PyArchInit-Mini.

## 📊 Contenuto del Database di Esempio

Il database di esempio include:
- **1 Sito archeologico**: "Sito Archeologico di Esempio" (Roma, RM)
- **100 Unità Stratigrafiche (US)**: Distribuite su 4 aree (A, B, C, D)
- **50 Materiali**: Ceramiche, metalli, vetri, ossa lavorate, ecc.
- **70+ Relazioni stratigrafiche**: Harris Matrix completo
- **Cancellazione a cascata**: Eliminando un sito si cancellano automaticamente tutte le US e materiali collegati

## 🚀 Come Caricare il Database di Esempio

### Metodo 1: Launcher Interattivo (Consigliato)

```bash
python launch_with_sample_data.py
```

Questo script ti permette di scegliere:
1. GUI Desktop (Tkinter)
2. API Server (FastAPI) 
3. Entrambi

### Metodo 2: Variabile d'Ambiente

#### Per l'API Server:
```bash
DATABASE_URL="sqlite:///./data/pyarchinit_mini_sample.db" python main.py
```

#### Per la GUI Desktop:
```bash
DATABASE_URL="sqlite:///./data/pyarchinit_mini_sample.db" python desktop_gui/main.py
```

### Metodo 3: Copia come Database Principale

```bash
python scripts/load_sample_as_main.py
```

Questo script:
- Fa il backup del database esistente
- Copia il database di esempio come database principale
- Permette di usare PyArchInit-Mini normalmente

## 🔧 Generazione del Database di Esempio

Se il database di esempio non esiste, generalo con:

```bash
python scripts/populate_simple_data.py
```

## 🧪 Test della Cancellazione a Cascata

Per testare che la cancellazione a cascata funzioni:

```bash
python scripts/test_cascade_delete.py
```

## 📁 Struttura File

```
pyarchinit-mini/
├── data/
│   └── pyarchinit_mini_sample.db     # Database di esempio
├── scripts/
│   ├── populate_simple_data.py       # Genera dati esempio
│   ├── test_cascade_delete.py        # Test cancellazione cascata
│   └── load_sample_as_main.py        # Carica come DB principale
├── launch_with_sample_data.py        # Launcher interattivo
└── main.py                           # API Server
```

## 🌐 Accesso alle Interfacce

### API Server
- **URL**: http://localhost:8000
- **Documentazione**: http://localhost:8000/docs
- **Swagger UI**: http://localhost:8000/redoc

### GUI Desktop
Interfaccia Tkinter nativa con finestre per:
- Gestione siti
- Schede US estese
- Inventario materiali
- Harris Matrix editor
- Export PDF
- Gestione media

## 🗃️ Dati di Esempio Inclusi

### Sito Archeologico
- **Nome**: Sito Archeologico di Esempio
- **Località**: Roma, Lazio (RM)
- **Tipo**: Scavo stratigrafico
- **Descrizione**: Sito con stratificazione completa

### Unità Stratigrafiche (US 1-100)
- **Aree**: A, B, C, D
- **Periodi**: Età del Bronzo, Età del Ferro, Età Romana, Medioevo
- **Formazioni**: Naturale, Antropica, Mista
- **Dati completi**: Quote, dimensioni, schedatori, date

### Materiali (Inv. 1-50)
- **Tipologie**: Ceramica comune/fine, vetro, bronzo, ferro, osso lavorato, pietra, monete, laterizi
- **Contesti**: Distribuiti tra le 100 US
- **Attributi**: Peso, dimensioni, stato conservazione, datazione

### Relazioni Stratigrafiche
- **Sequenziali**: US precedenti sopra US successive
- **Di taglio**: Alcune US tagliano altre (rapporti complessi)
- **Harris Matrix**: Grafo diretto aciclico completo
- **Tipologie**: "sopra", "taglia", "riempie", "copre"

## 🔄 Reset del Database

Per ricreare il database di esempio da zero:

```bash
# Elimina il database esistente
rm data/pyarchinit_mini_sample.db

# Rigenera i dati
python scripts/populate_simple_data.py
```

## ⚠️ Note Importanti

1. **Foreign Keys**: SQLite ha le foreign key constraints abilitate per supportare la cancellazione a cascata

2. **Backup**: Lo script `load_sample_as_main.py` crea automaticamente un backup del database esistente

3. **Compatibilità**: Il database è compatibile sia con SQLite che PostgreSQL (schema identico)

4. **Dati Realistici**: Tutti i dati seguono gli standard ICCD per l'archeologia italiana

## 🛠️ Risoluzione Problemi

### Database non trovato
```bash
# Verifica che il file esista
ls -la data/pyarchinit_mini_sample.db

# Se non esiste, generalo
python scripts/populate_simple_data.py
```

### Errore di connessione
```bash
# Verifica le permissions
chmod 644 data/pyarchinit_mini_sample.db

# Testa la connessione
python -c "import sqlite3; sqlite3.connect('data/pyarchinit_mini_sample.db').execute('SELECT COUNT(*) FROM site_table')"
```

### Porta occupata (API Server)
```bash
# Usa una porta diversa
PORT=8001 DATABASE_URL="sqlite:///./data/pyarchinit_mini_sample.db" python main.py
```