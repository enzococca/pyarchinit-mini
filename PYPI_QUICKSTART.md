# PyArchInit-Mini - Quick Start per PyPI

## Riepilogo Modifiche Completate

### 1. ✅ Database Normalizzato
- Migrato le relazioni stratigrafiche dalla colonna testuale `rapporti` alla tabella strutturata `us_relationships_table`
- `relationship_type` ora contiene solo il tipo ("Copre", "Taglia", "Si appoggia a")
- I numeri delle US sono memorizzati in `us_from` e `us_to`
- 114 relazioni migrate con successo

Script disponibile: `scripts/migrate_relationships.py`

### 2. ✅ Configurazione PyPI
- `pyproject.toml` aggiornato con dipendenze opzionali per ogni interfaccia
- `MANIFEST.in` creato per includere tutti i file necessari
- Entry points configurati per tutti i comandi

### 3. ✅ Script di Setup Utente
- Script `pyarchinit_mini/scripts/setup_user_env.py` per configurare `~/.pyarchinit_mini`
- Gestisce database, media, export, backup, config, logs
- Entry point: `pyarchinit-mini-setup`

### 4. ✅ Entry Points per Interfacce
Comandi disponibili dopo l'installazione:
- `pyarchinit-mini-api` → Server REST API (porta 8000)
- `pyarchinit-mini-web` → Interfaccia Web Flask (porta 5000)
- `pyarchinit-mini-gui` → Interfaccia Desktop GUI
- `pyarchinit-mini` → Interfaccia CLI
- `pyarchinit-mini-setup` → Setup ambiente utente

## Come Pubblicare su PyPI

### Passo 1: Preparazione

```bash
# 1. Verifica che tutti i test passino
pytest

# 2. Formatta il codice
black pyarchinit_mini/
isort pyarchinit_mini/

# 3. Verifica versione in pyproject.toml
grep version pyproject.toml
```

### Passo 2: Build

```bash
# 1. Installa gli strumenti
pip install --upgrade pip build twine

# 2. Pulisci build precedenti
rm -rf build/ dist/ *.egg-info

# 3. Crea il package
python -m build

# 4. Verifica il package
twine check dist/*
```

### Passo 3: Test su TestPyPI (Consigliato)

```bash
# Carica su TestPyPI
twine upload --repository testpypi dist/*

# Test installazione
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    pyarchinit-mini[all]
```

### Passo 4: Pubblicazione su PyPI

```bash
# Carica su PyPI
twine upload dist/*

# Username: __token__
# Password: <your-pypi-token>
```

## Come gli Utenti Installeranno il Package

### Installazione Base (Solo API)

```bash
pip install pyarchinit-mini
```

### Con Desktop GUI

```bash
pip install pyarchinit-mini[gui]
```

### Installazione Completa

```bash
pip install pyarchinit-mini[all]
```

### Setup Iniziale

```bash
# Dopo l'installazione, eseguire:
pyarchinit-mini-setup

# Questo crea:
# ~/.pyarchinit_mini/
#   ├── data/              (database SQLite)
#   ├── media/             (immagini, video, documenti)
#   ├── export/            (PDF e altri export)
#   ├── backup/            (backup automatici)
#   ├── config/            (config.yaml)
#   └── logs/              (log applicazione)
```

### Utilizzo

```bash
# Avvia il server API
pyarchinit-mini-api
# Apri http://localhost:8000/docs

# Oppure avvia la GUI
pyarchinit-mini-gui

# Oppure avvia il web
pyarchinit-mini-web
# Apri http://localhost:5001
```

## Struttura delle Dipendenze

### Core (sempre installato)
- FastAPI + Uvicorn
- SQLAlchemy + psycopg2-binary
- Pydantic
- NetworkX (Harris Matrix)
- ReportLab (PDF base)
- Pillow (immagini)

### Opzionali

| Extra | Componenti | Comando |
|-------|-----------|---------|
| `cli` | Click, Rich, Inquirer | `pip install pyarchinit-mini[cli]` |
| `web` | Flask, WTForms, Jinja2 | `pip install pyarchinit-mini[web]` |
| `gui` | (Tkinter è nella stdlib) | `pip install pyarchinit-mini[gui]` |
| `harris` | Matplotlib, Graphviz | `pip install pyarchinit-mini[harris]` |
| `pdf` | WeasyPrint | `pip install pyarchinit-mini[pdf]` |
| `media` | python-magic, moviepy | `pip install pyarchinit-mini[media]` |
| `all` | Tutto quanto sopra | `pip install pyarchinit-mini[all]` |
| `dev` | pytest, black, flake8, mypy | `pip install pyarchinit-mini[dev]` |

## Pubblicazione Desktop GUI

**SÌ, la desktop GUI è inclusa nel package PyPI!**

Quando un utente installa con:
```bash
pip install pyarchinit-mini[gui]
```

Riceve:
1. Il modulo `desktop_gui` con l'interfaccia Tkinter
2. Il comando `pyarchinit-mini-gui` per avviare l'applicazione
3. Setup automatico di database e configurazioni in `~/.pyarchinit_mini`

### Vantaggi di questo approccio

1. **Installazione semplice**: Un solo comando pip
2. **Gestione dipendenze**: pip gestisce tutto automaticamente
3. **Aggiornamenti facili**: `pip install --upgrade pyarchinit-mini[gui]`
4. **Multi-piattaforma**: Funziona su Windows, Linux, macOS
5. **Dati separati**: Database e media in `~/.pyarchinit_mini`, non nel virtualenv

## Configurazione

Gli utenti possono configurare l'applicazione modificando:

```bash
~/.pyarchinit_mini/config/config.yaml
```

Esempio:

```yaml
database:
  url: "sqlite:///~/.pyarchinit_mini/data/pyarchinit_mini.db"
  # O per PostgreSQL:
  # url: "postgresql://user:password@localhost:5432/pyarchinit"

api:
  host: "0.0.0.0"
  port: 8000

web:
  host: "0.0.0.0"
  port: 5000
  debug: true

media:
  base_dir: "~/.pyarchinit_mini/media"
  max_upload_size: 104857600  # 100MB

export:
  base_dir: "~/.pyarchinit_mini/export"
  pdf_dpi: 300
```

## Gestione Database nella Home

### Perché `~/.pyarchinit_mini`?

1. **Persistenza**: I dati sopravvivono alla rimozione del virtualenv
2. **Backup facilitato**: Una sola directory da backuppare
3. **Multi-progetto**: Stesso DB accessibile da diversi virtualenv
4. **Convenzione standard**: Seguita da molte applicazioni (`.docker`, `.config`, ecc.)

### Struttura Directory

```
~/.pyarchinit_mini/
├── data/
│   └── pyarchinit_mini.db          # Database SQLite
├── media/
│   ├── images/                      # Foto di scavo
│   ├── videos/                      # Video documentazione
│   ├── documents/                   # PDF, relazioni
│   └── thumbnails/                  # Miniature generate
├── export/
│   └── relazione_*.pdf             # Export PDF generati
├── backup/
│   └── backup_2025-10-18.db       # Backup automatici
├── config/
│   └── config.yaml                 # Configurazione utente
└── logs/
    └── pyarchinit_mini.log         # Log applicazione
```

## Workflow Completo

### Per lo Sviluppatore (Te)

```bash
# 1. Finalizza il codice
pytest
black pyarchinit_mini/

# 2. Aggiorna versione in pyproject.toml
# version = "0.1.0"

# 3. Build e pubblicazione
python -m build
twine upload dist/*

# 4. Tag su GitHub
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

### Per l'Utente Finale

```bash
# 1. Installazione
pip install pyarchinit-mini[gui]

# 2. Setup ambiente
pyarchinit-mini-setup

# 3. Avvia l'applicazione
pyarchinit-mini-gui

# 4. (Opzionale) Avvia API server
pyarchinit-mini-api
```

## Prossimi Passi

1. **Test finale**: Testa tutti i componenti localmente
2. **Aggiorna README.md**: Aggiungi badge PyPI, istruzioni installazione
3. **CHANGELOG.md**: Documenta le modifiche della versione
4. **Screenshot/GIF**: Aggiungi screenshot della GUI al README
5. **Pubblica su TestPyPI**: Test completo prima di PyPI
6. **Pubblica su PyPI**: Release ufficiale
7. **Annuncia**: README, social media, forum archeologici

## Troubleshooting

### Il comando non viene trovato dopo l'installazione

```bash
# Verifica che il path di pip sia nel PATH
pip show pyarchinit-mini

# Su Linux/Mac, aggiungi al PATH:
export PATH="$HOME/.local/bin:$PATH"

# Su Windows, i comandi sono in:
# C:\Users\<username>\AppData\Local\Programs\Python\PythonXX\Scripts\
```

### Database non trovato

```bash
# Riesegui il setup
pyarchinit-mini-setup

# Oppure specifica il DATABASE_URL
export DATABASE_URL="sqlite:///path/to/your/database.db"
```

### Tkinter non disponibile

Su alcuni sistemi Linux, Tkinter deve essere installato separatamente:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (dovrebbe essere già incluso)
# Windows (dovrebbe essere già incluso)
```

## Supporto

- **Documentazione**: `docs/PYPI_PUBLICATION.md`
- **Issues**: https://github.com/enzococca/pyarchinit-mini/issues
- **Email**: enzo.ccc@gmail.com

## Licenza

GPL-2.0 - Vedi file LICENSE per i dettagli