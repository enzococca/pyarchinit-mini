# Guida alla Pubblicazione su PyPI

Questa guida spiega come pubblicare PyArchInit-Mini su PyPI (Python Package Index).

## Prerequisiti

1. **Account PyPI**: Registrati su [PyPI](https://pypi.org/account/register/) e [TestPyPI](https://test.pypi.org/account/register/)
2. **Token API**: Crea un token API su PyPI (Settings → API tokens)
3. **Strumenti necessari**:
   ```bash
   pip install --upgrade pip
   pip install build twine
   ```

## Struttura del Package

Il progetto include:
- **Core API** (sempre installato): FastAPI, SQLAlchemy, database management
- **CLI** (opzionale): Interfaccia a riga di comando
- **Web** (opzionale): Interfaccia web Flask
- **GUI** (opzionale): Interfaccia desktop Tkinter
- **Harris Matrix** (opzionale): Visualizzazione avanzata
- **Media** (opzionale): Gestione avanzata media

## Comandi di Installazione per gli Utenti

Dopo la pubblicazione su PyPI, gli utenti potranno installare il package in diversi modi:

### Solo API (installazione minima)
```bash
pip install pyarchinit-mini
```

### Con interfaccia CLI
```bash
pip install pyarchinit-mini[cli]
```

### Con interfaccia Web
```bash
pip install pyarchinit-mini[web]
```

### Con interfaccia GUI Desktop
```bash
pip install pyarchinit-mini[gui]
```

### Con Harris Matrix completo
```bash
pip install pyarchinit-mini[harris]
```

### Installazione completa (tutte le interfacce)
```bash
pip install pyarchinit-mini[all]
```

### Per sviluppatori
```bash
pip install pyarchinit-mini[dev]
```

## Setup Iniziale dopo l'Installazione

Dopo l'installazione, l'utente deve eseguire:

```bash
# 1. Setup dell'ambiente utente
pyarchinit-mini-setup

# Questo creerà:
# - ~/.pyarchinit_mini/data/          (database)
# - ~/.pyarchinit_mini/media/         (file multimediali)
# - ~/.pyarchinit_mini/export/        (export PDF)
# - ~/.pyarchinit_mini/backup/        (backup automatici)
# - ~/.pyarchinit_mini/config/        (configurazione)
# - ~/.pyarchinit_mini/logs/          (log applicazione)
```

## Comandi Disponibili dopo l'Installazione

```bash
# Avvia il server REST API (porta 8000)
pyarchinit-mini-api

# Avvia l'interfaccia web (porta 5000)
pyarchinit-mini-web

# Avvia l'interfaccia GUI desktop
pyarchinit-mini-gui

# Avvia l'interfaccia CLI interattiva
pyarchinit-mini

# Riesegui il setup
pyarchinit-mini-setup
```

## Processo di Pubblicazione

### 1. Preparazione

Prima di pubblicare, verifica:

```bash
# Verifica la versione in pyproject.toml
cat pyproject.toml | grep version

# Esegui i test
pytest

# Verifica il codice
black pyarchinit_mini/
flake8 pyarchinit_mini/

# Verifica che tutti i file necessari siano inclusi
cat MANIFEST.in
```

### 2. Build del Package

```bash
# Pulisci le build precedenti
rm -rf build/ dist/ *.egg-info

# Crea il package
python -m build

# Questo creerà:
# - dist/pyarchinit_mini-0.1.0.tar.gz (source distribution)
# - dist/pyarchinit_mini-0.1.0-py3-none-any.whl (wheel)
```

### 3. Verifica il Package

```bash
# Verifica che il package sia corretto
twine check dist/*

# Dovrebbe mostrare:
# Checking dist/pyarchinit_mini-0.1.0.tar.gz: PASSED
# Checking dist/pyarchinit_mini-0.1.0-py3-none-any.whl: PASSED
```

### 4. Test su TestPyPI (Consigliato)

TestPyPI è un ambiente di test che ti permette di provare il caricamento senza pubblicare sul PyPI principale.

```bash
# Carica su TestPyPI
twine upload --repository testpypi dist/*

# Ti verrà chiesto:
# Username: __token__
# Password: <il tuo TestPyPI API token>
```

Test dell'installazione da TestPyPI:

```bash
# Crea un ambiente virtuale di test
python -m venv test_env
source test_env/bin/activate  # su Linux/Mac
# test_env\Scripts\activate.bat  # su Windows

# Installa dal TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    pyarchinit-mini[all]

# Prova i comandi
pyarchinit-mini-setup
pyarchinit-mini-api --help

# Disattiva e elimina l'ambiente di test
deactivate
rm -rf test_env
```

### 5. Pubblicazione su PyPI

Una volta verificato che tutto funziona su TestPyPI:

```bash
# Carica su PyPI
twine upload dist/*

# Ti verrà chiesto:
# Username: __token__
# Password: <il tuo PyPI API token>
```

**ATTENZIONE**: Una volta pubblicato su PyPI, non puoi:
- Eliminare una versione e ricaricarla
- Modificare i file di una versione esistente
- Riutilizzare un numero di versione

### 6. Configurazione Token API

Per evitare di inserire il token ogni volta, crea `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-<il-tuo-token-api>

[testpypi]
username = __token__
password = pypi-<il-tuo-testpypi-token>
```

Poi puoi usare:

```bash
# Senza dover inserire le credenziali
twine upload --repository testpypi dist/*
twine upload dist/*
```

## Versioning

PyArchInit-Mini usa [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (es. 1.2.3)
  - **MAJOR**: Cambiamenti incompatibili con versioni precedenti
  - **MINOR**: Nuove funzionalità mantenendo compatibilità
  - **PATCH**: Bug fix

Prima della versione 1.0.0, il progetto è considerato in fase di sviluppo:
- **0.1.0**: Prima release alpha
- **0.2.0**: Aggiunte nuove funzionalità
- **0.2.1**: Bug fix

Per aggiornare la versione:

```bash
# Modifica il numero di versione in:
# - pyproject.toml (campo version)
# - pyarchinit_mini/__init__.py (__version__)
# - setup.py (version)

# Poi segui il processo di build e pubblicazione
```

## Gestione delle Release su GitHub

Dopo la pubblicazione su PyPI, crea una release su GitHub:

```bash
# 1. Crea un tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# 2. Vai su GitHub → Releases → Draft a new release
# 3. Seleziona il tag v0.1.0
# 4. Scrivi le release notes
# 5. Allega i file dist/pyarchinit_mini-0.1.0.tar.gz e .whl
# 6. Pubblica la release
```

## Checklist Pre-Pubblicazione

- [ ] Test passano tutti (`pytest`)
- [ ] Codice formattato (`black`, `isort`)
- [ ] No errori di linting (`flake8`)
- [ ] Versione aggiornata in `pyproject.toml` e `setup.py`
- [ ] `CHANGELOG.md` aggiornato con le novità
- [ ] `README.md` aggiornato
- [ ] Database di esempio funzionante
- [ ] Script di setup testato
- [ ] Tutte le interfacce (API, Web, GUI, CLI) testate
- [ ] Build completata senza errori
- [ ] Package verificato con `twine check`
- [ ] Testato su TestPyPI
- [ ] Commit fatto e pushato su GitHub
- [ ] Tag creato su GitHub

## Post-Pubblicazione

Dopo la pubblicazione:

1. **Annuncia la release**:
   - README.md su GitHub
   - Social media (se applicabile)
   - Mailing list/forum archeologici

2. **Monitora feedback**:
   - Issue su GitHub
   - Download statistics su PyPI
   - Feedback degli utenti

3. **Pianifica prossima release**:
   - Milestone su GitHub
   - TODO list per nuove funzionalità

## Troubleshooting

### Errore: "File already exists"
```
HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
The name 'pyarchinit-mini' is too similar to an existing project
```
**Soluzione**: Il nome potrebbe essere già preso o troppo simile. Verifica su PyPI.

### Errore: "Invalid distribution"
```
ERROR: Invalid distribution file
```
**Soluzione**: Esegui `twine check dist/*` per identificare il problema.

### Package troppo grande
Se il package supera i 60MB:

1. Rimuovi file non necessari
2. Usa `.gitignore` e `MANIFEST.in` per escludere file
3. Considera di distribuire il database di esempio separatamente

### Dipendenze non installate correttamente
Verifica che:
- `dependencies` in `pyproject.toml` sia corretto
- `optional-dependencies` siano ben definite
- Gli utenti usino i comandi corretti (`pip install pyarchinit-mini[cli]`)

## Supporto

Per problemi con la pubblicazione:
- PyPI Documentation: https://packaging.python.org/
- PyPI Help: https://pypi.org/help/
- Issue tracker: https://github.com/pyarchinit/pyarchinit-mini/issues

## Riferimenti

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Setuptools Documentation](https://setuptools.pypa.io/)