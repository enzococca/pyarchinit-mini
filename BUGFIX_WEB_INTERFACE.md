# Bug Fix - Web Interface

## Problemi Risolti

### 1. ❌ Le schede US non vengono salvate

**Problema**: L'utente segnala che le schede US non vengono salvate

**Cause possibili**:
- Validazione del form che fallisce silenziosamente
- Errori non visualizzati all'utente
- Problemi con i campi obbligatori

**Soluzioni implementate**:

#### A. Visualizzazione errori di validazione
Aggiunto blocco di visualizzazione errori in `/web_interface/templates/us/form.html`:

```html
{% if form.errors %}
<div class="alert alert-danger">
    <strong>Errori nel form:</strong>
    <ul>
    {% for field_name, errors in form.errors.items() %}
        {% for error in errors %}
        <li>{{ field_name }}: {{ error }}</li>
        {% endfor %}
    {% endfor %}
    </ul>
</div>
{% endif %}
```

#### B. Errori per campi specifici
Aggiunto visualizzazione errori sotto i campi obbligatori:

```html
<!-- Campo Sito -->
<div class="mb-3">
    <label class="form-label">Sito *</label>
    {{ form.sito(class="form-select", required=True) }}
    {% if form.sito.errors %}
        <div class="text-danger">{{ form.sito.errors[0] }}</div>
    {% endif %}
</div>

<!-- Campo Numero US -->
<div class="col-md-6 mb-3">
    <label class="form-label">Numero US *</label>
    {{ form.us(class="form-control", required=True) }}
    {% if form.us.errors %}
        <div class="text-danger">{{ form.us.errors[0] }}</div>
    {% endif %}
</div>
```

#### C. Debug logging in backend
Aggiunto logging in `/web_interface/app.py` (linee 233-236):

```python
elif request.method == 'POST':
    # Form validation failed - show errors
    flash('Errore nella validazione del form. Controlla i campi obbligatori.', 'error')
    print(f"Form validation errors: {form.errors}")
```

**Ora quando il form non passa la validazione**:
- ✅ L'utente vede un alert rosso con tutti gli errori
- ✅ Ogni campo con errori mostra il messaggio specifico
- ✅ Console del server mostra gli errori per debugging

---

### 2. ❌ Non vedo le funzioni per l'Harris Matrix

**Problema**: L'utente non trova i link per accedere alla visualizzazione della Harris Matrix

**Soluzioni implementate**:

#### A. Link nella Lista Siti
Modificato `/web_interface/templates/sites/list.html` (linee 44-54):

Aggiunto gruppo di pulsanti per ogni sito:
```html
<div class="btn-group btn-group-sm">
    <a href="{{ url_for('view_site', site_id=site.id_sito) }}" class="btn btn-info">
        <i class="fas fa-eye"></i> Dettagli
    </a>
    <a href="{{ url_for('harris_matrix', site_name=site.sito) }}" class="btn btn-success">
        <i class="fas fa-project-diagram"></i> Matrix
    </a>
    <a href="{{ url_for('export_site_pdf', site_id=site.id_sito) }}" class="btn btn-secondary">
        <i class="fas fa-file-pdf"></i> PDF
    </a>
</div>
```

**Risultato**: Ogni sito nella lista ha ora 3 pulsanti:
- **Dettagli** (blu) - Vai al dettaglio sito
- **Matrix** (verde) - Visualizza Harris Matrix
- **PDF** (grigio) - Esporta PDF

#### B. Link nella Navbar
Modificato `/web_interface/templates/base.html` (linee 101-105):

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('sites_list') }}">
        <i class="fas fa-project-diagram"></i> Harris Matrix
    </a>
</li>
```

**Risultato**: Nella barra di navigazione principale c'è ora una voce "Harris Matrix" sempre visibile

#### C. Link nella Dashboard
Il template `dashboard.html` aveva già i link alla Harris Matrix (linee 98-101):

```html
<a href="{{ url_for('harris_matrix', site_name=site.sito) }}"
   class="btn btn-outline-info">
    <i class="fas fa-project-diagram"></i> Matrix
</a>
```

#### D. Link nella Pagina Dettaglio Sito
Il template `sites/detail.html` aveva già una sezione dedicata (linee 119-126):

```html
<!-- Harris Matrix Link -->
<div class="card">
    <div class="card-body text-center">
        <a href="{{ url_for('harris_matrix', site_name=site.sito) }}"
           class="btn btn-lg btn-success">
            Visualizza Matrice di Harris
        </a>
    </div>
</div>
```

---

## Dove Trovare la Harris Matrix Ora

### 1. **Dashboard** (`/`)
- Tabella "Siti Recenti" → Pulsante **Matrix** per ogni sito

### 2. **Lista Siti** (`/sites`)
- Colonna "Azioni" → Pulsante **Matrix** per ogni sito
- Link diretto dalla navbar principale

### 3. **Dettaglio Sito** (`/sites/<id>`)
- Card dedicata in fondo con pulsante grande verde "Visualizza Matrice di Harris"

### 4. **Navbar** (sempre visibile)
- Menu principale → **Harris Matrix** (porta alla lista siti)

---

## Test di Verifica

### Per testare il salvataggio US:

1. Avvia il server web:
   ```bash
   python web_interface/app.py
   ```

2. Vai a: `http://localhost:5001/us/create`

3. Compila il form:
   - **Sito**: Seleziona un sito dalla lista (obbligatorio)
   - **Numero US**: Inserisci un numero (obbligatorio)
   - Altri campi: opzionali

4. Clicca "Salva"

5. **Verifica errori**:
   - Se mancano campi obbligatori → Alert rosso con lista errori
   - Se validazione OK → Messaggio verde "US XXX creata con successo!"
   - Se errore database → Alert rosso con dettaglio errore

6. **Console server**: Controlla output per eventuali errori di validazione

### Per testare Harris Matrix:

1. Dalla dashboard → Clicca "Matrix" su un sito
2. Dalla lista siti → Clicca "Matrix" su un sito
3. Dal dettaglio sito → Clicca "Visualizza Matrice di Harris"
4. Dalla navbar → Clicca "Harris Matrix" → Seleziona sito → Clicca "Matrix"

**Tutti i percorsi portano a**: `/harris_matrix/<site_name>`

---

## File Modificati

### Template
1. `/web_interface/templates/us/form.html`
   - Aggiunta visualizzazione errori form completa
   - Aggiunta visualizzazione errori per campi specifici

2. `/web_interface/templates/sites/list.html`
   - Aggiunto gruppo pulsanti con Matrix e PDF

3. `/web_interface/templates/base.html`
   - Aggiunta voce Harris Matrix nella navbar

### Backend
4. `/web_interface/app.py`
   - Aggiunto debug logging per errori validazione (linee 233-236)

---

## Funzionalità Harris Matrix

### Route: `/harris_matrix/<site_name>`

**Cosa fa**:
1. Recupera tutte le US del sito
2. Parsa i rapporti stratigrafici dal campo `rapporti`
3. Genera grafo NetworkX
4. Calcola livelli topologici
5. Renderizza visualizzazione matplotlib
6. Converte in PNG base64
7. Mostra immagine + statistiche

**Statistiche mostrate**:
- Numero totale US (nodi)
- Numero totale relazioni (edges)
- Profondità massima (livelli)
- Numero livelli
- US isolate
- US livello superiore/inferiore

**Visualizzazione**:
- Immagine matrice (matplotlib PNG inline)
- Sequenza stratigrafica ordinata per livelli

**Test con database di esempio**:
```
✓ Site: Sito Archeologico di Esempio
✓ Nodes: 50 US
✓ Edges: 99 relazioni stratigrafiche
✓ Levels: 7 livelli
✓ Valid DAG: True (no cycles)
```

---

## Prossimi Passi

### Se il salvataggio US ancora non funziona:

1. **Controlla console browser** (F12 → Console)
   - Eventuali errori JavaScript
   - Richieste HTTP fallite

2. **Controlla console server**
   - Errori di validazione stampati
   - Stack trace completi

3. **Verifica database**
   ```bash
   sqlite3 data/pyarchinit_mini_sample.db
   SELECT COUNT(*) FROM us_table;
   SELECT * FROM us_table ORDER BY id_us DESC LIMIT 5;
   ```

4. **Test manuale con curl**:
   ```bash
   curl -X POST http://localhost:5001/us/create \
     -d "sito=Sito Test&us=9999&area=A" \
     -H "Content-Type: application/x-www-form-urlencoded"
   ```

5. **Segnala errori specifici**:
   - Screenshot alert errori
   - Output console server
   - Messaggi flash visualizzati

---

## Riepilogo Miglioramenti

✅ **Form US**: Ora mostra tutti gli errori di validazione
✅ **Harris Matrix**: Accessibile da 4 percorsi diversi
✅ **Link PDF**: Visibili in lista siti e dashboard
✅ **Navbar**: Voce dedicata Harris Matrix
✅ **UX**: Pulsanti con icone Font Awesome chiare
✅ **Debug**: Logging errori in console server

**Tutti i link necessari sono ora presenti e visibili!**
