# Guida Completa Web App - PyArchInit-Mini

## 🚀 Quick Start

### 1. Installazione

```bash
# Clona il repository
git clone https://github.com/enzococa/pyarchinit-mini-desk.git
cd pyarchinit-mini-desk

# Crea virtual environment
python -m venv .venv
source .venv/bin/activate  # Su Linux/Mac
# oppure
.venv\Scripts\activate  # Su Windows

# Installa dipendenze web
pip install -e ".[web,harris,pdf]"
```

### 2. Crea Database con Dati di Esempio

```bash
# Crea database con 3 siti, 15 US, 10 reperti
python scripts/create_sample_for_webapp.py

# Oppure specifica path custom
python scripts/create_sample_for_webapp.py --database /path/to/mydb.db
```

### 3. Avvia Web Server

```bash
# Metodo 1: Script diretto
python web_interface/app.py

# Metodo 2: Console script (dopo pip install)
pyarchinit-mini-web

# Metodo 3: Con Flask CLI
export FLASK_APP=web_interface/app.py
flask run --port 5001
```

### 4. Apri Browser

```
http://localhost:5001
```

**Nota**: Porta 5001 invece di 5000 per evitare conflitti con AirPlay su macOS.

---

## 📊 Dati di Esempio Creati

Lo script `create_sample_for_webapp.py` crea:

### Siti (3)
1. **Villa Romana di Positano**
   - Campania, Salerno
   - Villa marittima con impianto termale
   - 5 US con rapporti stratigrafici

2. **Necropoli Etrusca di Tarquinia**
   - Lazio, Viterbo
   - Area funeraria con tombe affrescate
   - 5 US con corredo funerario

3. **Insediamento Medievale di Monteriggioni**
   - Toscana, Siena
   - Borgo fortificato
   - 4 US torre difensiva

### US - Unità Stratigrafiche (14 totali)

#### Villa Romana di Positano
- US 1001: Humus superficiale (top)
- US 1002: Crollo tegole → copre 1003, 1004
- US 1003: Pavimento mosaico → si appoggia a 1005
- US 1004: Strato incendio → copre 1005
- US 1005: Muro opera reticolata → taglia 1006

#### Necropoli Etrusca
- US 2001: Riempimento camera → copre 2002, 2003
- US 2002: Intonaco affrescato → si appoggia a 2004
- US 2003: Deposizione funeraria → si appoggia a 2005
- US 2004: Parete camera → taglia 2006
- US 2005: Banchina pietra → si appoggia a 2006

#### Monteriggioni
- US 3001: Crollo merlatura → copre 3002
- US 3002: Pavimento cotto → si appoggia a 3003
- US 3003: Muratura pietra → taglia 3004
- US 3004: Terreno vegetale (base)

### Reperti - Inventario (10 totali)

#### Villa Romana
- 1001: Anfora Dressel 20 (3.5 kg)
- 1002: Tessera mosaico vetro (15.5 g)
- 1003: Chiodo ferro (45.2 g)

#### Necropoli Etrusca
- 2001: Kylix bucchero nero (280 g)
- 2002: Fibula bronzo (18.5 g)
- 2003: Oinochoe bucchero (450 g)

#### Monteriggioni
- 3001: Maiolica arcaica (65 g)
- 3002: Punta freccia ferro (25 g)
- 3003: Bicchiere vetro (8.5 g)
- 3004: Macina pietra (2.5 kg)

---

## 🎯 Funzionalità Principali

### 1. Dashboard (`/`)

**Cosa visualizza**:
- Statistiche totali (siti, US, reperti)
- Lista 5 siti recenti
- Azioni rapide (nuovo sito, US, reperto)
- Link veloci a Harris Matrix e PDF

**Azioni disponibili**:
- Visualizza dettaglio sito
- Vai a Harris Matrix
- Esporta PDF

### 2. Gestione Siti

#### Lista Siti (`/sites`)
- Visualizzazione tabellare con filtri
- Ricerca per nome
- **Azioni per ogni sito**:
  - 👁️ Dettagli
  - 🔀 Harris Matrix
  - 📄 Export PDF

#### Nuovo Sito (`/sites/create`)
**Form completo**:
- Nome Sito * (obbligatorio)
- Nazione
- Regione, Provincia, Comune
- Definizione Sito
- Descrizione (textarea)

**Esempio compilazione**:
```
Nome Sito: Villa dei Papiri
Nazione: Italia
Regione: Campania
Provincia: Napoli
Comune: Ercolano
Definizione: Villa suburbana romana
Descrizione: Villa di età romana con biblioteca di papiri...
```

#### Dettaglio Sito (`/sites/<id>`)
Mostra:
- Dati sito completi
- Lista US (prime 10)
- Lista reperti (primi 10)
- Link Harris Matrix (pulsante verde grande)
- Pulsanti "Nuova US" e "Nuovo Reperto"

### 3. Gestione US

#### Lista US (`/us`)
- Tabella con tutte le US
- Filtro per sito
- Paginazione (20 per pagina)

#### Nuova US (`/us/create`)

**Form completo con tutti i campi**:

**Campi obbligatori**:
- ⭐ **Sito**: Select da lista siti
- ⭐ **Numero US**: Numero univoco per sito

**Campi descrittivi**:
- Descrizione Stratigrafica
- Descrizione Interpretativa
- Descrizione Dettagliata (textarea)
- Interpretazione (textarea)

**Campi tecnici**:
- Area: Settore di scavo
- Anno Scavo
- Schedatore: Nome archeologo
- Formazione: Natural/Artificial

**⭐ Campo fondamentale - Rapporti Stratigrafici**:
```
Formato: copre 1002, taglia 1005, si appoggia a 1010

Relazioni supportate:
- copre / coperto da
- taglia / tagliato da
- riempie / riempito da
- si appoggia / gli si appoggia
- si lega a
- uguale a
```

**Esempio compilazione US**:
```
Sito: Villa Romana di Positano
Numero US: 1010
Area: Settore B
Descrizione Stratigrafica: Strato di malta e frammenti laterizi
Descrizione Interpretativa: Livello di preparazione pavimento
Descrizione: Strato compatto di malta di calce con inclusi di laterizio frantumato. Spessore 8-12 cm.
Interpretazione: Strato di preparazione (statumen) per il pavimento in opus signinum dell'ambiente termale
Anno Scavo: 2024
Schedatore: Dr. Mario Rossi
Formazione: Artificial
Rapporti: copre 1011, si appoggia a 1012, taglia 1013
```

**Validazione form**:
- ✅ Errori mostrati in alert rosso
- ✅ Errori sotto ogni campo
- ✅ Flash message successo/errore
- ✅ Redirect a lista US dopo salvataggio

### 4. Harris Matrix (`/harris_matrix/<site_name>`)

**Come accedere** (4 modi):
1. Dashboard → Pulsante "Matrix"
2. Lista Siti → Pulsante "Matrix" verde
3. Dettaglio Sito → "Visualizza Matrice di Harris"
4. Navbar → "Harris Matrix" → Scegli sito

**Cosa visualizza**:
- **Statistiche matrice**:
  - Totale US (nodi)
  - Totale relazioni (edges)
  - Profondità massima
  - Numero livelli
  - US isolate
  - US top/bottom level

- **Immagine Harris Matrix**:
  - Grafo generato con matplotlib
  - Layout topologico automatico
  - PNG inline base64

- **Sequenza stratigrafica**:
  - Lista ordinata per livelli
  - Dal più recente al più antico

**Esempio output con dati di esempio**:
```
Villa Romana di Positano
------------------------
📊 Statistiche:
- Totale US: 5
- Relazioni: 6
- Livelli: 4
- Valid DAG: ✓

🔀 Sequenza Stratigrafica:
Livello 1: US 1001 (humus)
Livello 2: US 1002 (crollo)
Livello 3: US 1003, 1004 (pavimento, incendio)
Livello 4: US 1005 (muro)
```

### 5. Export PDF (`/export/site_pdf/<site_id>`)

**Come esportare** (2 modi):
1. Lista Siti → Pulsante "PDF" grigio
2. Dettaglio Sito → "Esporta PDF"

**Contenuto PDF**:
- **Sezione Sito**:
  - Nome, località completa
  - Definizione e descrizione

- **Sezione US** (fino a 100):
  - Numero US, area
  - Descrizioni stratigrafiche
  - Anno scavo, schedatore

- **Sezione Inventario** (fino a 100):
  - Numero inventario
  - Tipo reperto, definizione
  - Peso, US di provenienza

**File generato**:
```
relazione_Villa_Romana_di_Positano.pdf
```

**Dimensione tipica**: 5-50 KB a seconda della quantità di dati

### 6. Inventario Materiali

#### Lista Reperti (`/inventario`)
- Tabella con tutti i reperti
- Filtri per sito e tipo reperto
- Paginazione

#### Nuovo Reperto (`/inventario/create`)

**Form completo**:
- Sito * (obbligatorio)
- Numero Inventario * (obbligatorio)
- Tipo Reperto: Ceramica, Metallo, Pietra, Osso, Vetro
- Definizione
- Descrizione (textarea)
- Area, US
- Peso (grammi)

**Esempio compilazione**:
```
Sito: Villa Romana di Positano
Numero Inventario: 1005
Tipo Reperto: Ceramica
Definizione: Lucerna ad olio
Descrizione: Lucerna in ceramica comune con tracce di combustione sul becco. Ansa rotta. Decorazione geometrica sul disco.
Area: Settore A
US: 1004
Peso: 125.5
```

### 7. Gestione Media

#### Upload Media (`/media/upload`)

**Form upload**:
- Tipo Entità: Sito / US / Inventario
- ID Entità
- File (immagini, PDF, documenti)
- Descrizione
- Autore/Fotografo

---

## 🔍 Workflow Completo di Esempio

### Scenario: Documentare un nuovo scavo

#### Passo 1: Crea il Sito
```
1. Dashboard → "Nuovo Sito"
2. Compila:
   - Nome: Domus Romana Via Appia
   - Località: Roma, Lazio
   - Definizione: Abitazione romana
3. Salva
```

#### Passo 2: Crea le US
```
Per ogni unità stratigrafica:

US 4001 (prima US, top level):
- Sito: Domus Romana Via Appia
- Numero: 4001
- Descrizione: Strato di demolizione moderna
- Rapporti: (lascia vuoto, è il livello superiore)

US 4002:
- Numero: 4002
- Descrizione: Crollo muratura
- Rapporti: copre 4003, copre 4004

US 4003:
- Numero: 4003
- Descrizione: Pavimento in cocciopesto
- Rapporti: si appoggia a 4005

US 4004:
- Numero: 4004
- Descrizione: Strato di abbandono
- Rapporti: copre 4005

US 4005:
- Numero: 4005
- Descrizione: Muro in laterizi
- Rapporti: (muro di base, nessuna relazione sotto)
```

#### Passo 3: Registra i Reperti
```
Per ogni reperto trovato:

Reperto 4001:
- Sito: Domus Romana Via Appia
- Numero: 4001
- Tipo: Ceramica
- Definizione: Sigillata italica
- US: 4003
- Peso: 45.2
```

#### Passo 4: Visualizza Harris Matrix
```
1. Vai a Dettaglio Sito
2. Clicca "Visualizza Matrice di Harris"
3. Verifica:
   - 5 nodi (US)
   - 4 relazioni
   - 3 livelli
   - Sequenza corretta
```

#### Passo 5: Esporta Documentazione
```
1. Clicca "Esporta PDF"
2. Download: relazione_Domus_Romana_Via_Appia.pdf
3. Contenuto:
   - Dati sito
   - 5 US complete
   - Reperti catalogati
```

---

## 🐛 Risoluzione Problemi

### 1. Form US non salva

**Sintomi**:
- Clicco Salva ma non succede nulla
- Nessun messaggio di errore

**Soluzione**:
- ✅ Ora implementata: visualizzazione errori completa
- Controlla alert rosso in cima al form
- Verifica campi obbligatori (Sito, Numero US)
- Console server: `python web_interface/app.py` mostra errori

**Debug**:
```bash
# Terminal server mostra:
Form validation errors: {'sito': ['This field is required']}
```

### 2. Harris Matrix non si vede

**Sintomi**:
- Non trovo dove cliccare per Harris Matrix

**Soluzione**:
- ✅ Ora 4 percorsi disponibili:
  1. Dashboard → Pulsante "Matrix"
  2. Lista Siti → Pulsante verde "Matrix"
  3. Dettaglio Sito → Card verde in fondo
  4. Navbar → Voce "Harris Matrix"

### 3. Errore DetachedInstanceError

**Sintomi**:
```
sqlalchemy.orm.exc.DetachedInstanceError: Instance <Site> is not bound to a Session
```

**Soluzione**:
- ✅ Fix applicato in tutte le route
- Codice ora usa dict invece di oggetti SQLAlchemy fuori sessione

### 4. Errore ModuleNotFoundError: inventario

**Sintomi**:
```
ModuleNotFoundError: No module named 'pyarchinit_mini.models.inventario'
```

**Soluzione**:
- ✅ Fix applicato: import corretto
- File è `inventario_materiali.py` non `inventario.py`

### 5. Harris Matrix mostra 0 nodi

**Sintomi**:
- Harris Matrix carica ma dice "0 nodi, 0 relazioni"

**Cause possibili**:
- Nessuna US creata per il sito
- Rapporti stratigrafici non compilati
- Formato rapporti non corretto

**Soluzione**:
```
1. Verifica US esistano: Lista US → Filtro per sito
2. Verifica rapporti: Controlla campo "Rapporti Stratigrafici"
3. Formato corretto: "copre 1002, taglia 1003"
4. Testa con dati esempio: python scripts/create_sample_for_webapp.py
```

---

## 📋 Checklist Test Completo

### ✅ Test Siti
- [ ] Crea nuovo sito
- [ ] Visualizza lista siti
- [ ] Visualizza dettaglio sito
- [ ] Ricerca sito per nome

### ✅ Test US
- [ ] Crea US senza rapporti (top level)
- [ ] Crea US con rapporti semplici (copre 1002)
- [ ] Crea US con rapporti multipli (copre 1002, taglia 1003)
- [ ] Visualizza lista US filtrata per sito
- [ ] Form mostra errori se campi vuoti

### ✅ Test Harris Matrix
- [ ] Accedi da dashboard
- [ ] Accedi da lista siti
- [ ] Accedi da dettaglio sito
- [ ] Accedi da navbar
- [ ] Matrice mostra nodi e relazioni corrette
- [ ] Statistiche corrette
- [ ] Sequenza ordinata corretta

### ✅ Test Export PDF
- [ ] Esporta da lista siti
- [ ] Esporta da dettaglio sito
- [ ] PDF contiene dati sito
- [ ] PDF contiene US
- [ ] PDF contiene reperti
- [ ] Nessun errore DetachedInstance

### ✅ Test Inventario
- [ ] Crea reperto
- [ ] Lista reperti
- [ ] Filtro per sito
- [ ] Filtro per tipo

### ✅ Test Navigazione
- [ ] Navbar funziona
- [ ] Sidebar funziona
- [ ] Breadcrumb corretti
- [ ] Flash messages visibili
- [ ] Redirect dopo salvataggio

---

## 🎓 Best Practices

### Compilazione Rapporti Stratigrafici

**✅ CORRETTO**:
```
copre 1002, taglia 1005, si appoggia a 1010
Copre 1002, Taglia 1005
copre 1002
```

**❌ SBAGLIATO**:
```
copre US 1002  (no "US" nella sintassi)
Copre: 1002    (no due punti)
1002, 1003     (manca tipo relazione)
```

### Numerazione US

**Convenzioni comuni**:
```
- Sito 1: US 1001-1999
- Sito 2: US 2001-2999
- Area A: US x001-x499
- Area B: US x500-x999
```

**Esempio**:
```
Villa Romana, Settore A:
- US 1001, 1002, 1003... (fino a 1499)

Villa Romana, Settore B:
- US 1500, 1501, 1502... (fino a 1999)
```

### Workflow Stratigrafia

1. **Scava dall'alto verso il basso**
2. **Documenta ogni livello** (US top level prima)
3. **Registra rapporti** mentre scavi
4. **Verifica Harris Matrix** dopo ogni sessione
5. **Correggi relazioni** se necessario

---

## 🔧 Configurazione Avanzata

### Variabili Ambiente

```bash
# Database
export DATABASE_URL="sqlite:///./data/mydb.db"

# Web Server
export PYARCHINIT_WEB_HOST="0.0.0.0"
export PYARCHINIT_WEB_PORT="5001"
export PYARCHINIT_WEB_DEBUG="true"

# Flask
export FLASK_SECRET_KEY="your-secure-secret-key"
```

### Porta Custom

```bash
# Cambia porta in web_interface/app.py (linea 397)
port = int(os.getenv("PYARCHINIT_WEB_PORT", "8080"))
```

### Database PostgreSQL

```bash
# Invece di SQLite
export DATABASE_URL="postgresql://user:pass@localhost:5432/pyarchinit"
```

---

## 📞 Supporto

**Problemi?**
- Leggi `BUGFIX_WEB_INTERFACE.md`
- Leggi `FIXES_SUMMARY.md`
- Controlla console server per errori

**Documentazione**:
- `WEB_INTERFACE_FEATURES.md` - Funzionalità complete
- `CLAUDE.md` - Architettura sistema
- `README.md` - Overview progetto

**GitHub**: https://github.com/enzococa/pyarchinit-mini-desk

---

## ✅ Pronto!

Ora puoi:
1. ✅ Creare database con dati di esempio
2. ✅ Avviare web interface
3. ✅ Testare tutte le funzionalità
4. ✅ Creare siti, US, reperti
5. ✅ Visualizzare Harris Matrix
6. ✅ Esportare PDF

**Buon scavo virtuale! 🏺**
