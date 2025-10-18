# Piano Implementazione Web App - Parità con Desktop GUI

## 📋 Obiettivi

1. **Form US identici alla desktop GUI** (7 tab completi)
2. **Form Inventario identici alla desktop GUI** (9 tab completi)
3. **Harris Matrix con Graphviz** come desktop GUI
4. **Validatore rapporti** con fix automatici
5. **Upload database SQLite/PostgreSQL**
6. **Stampa PDF identica** alla desktop GUI
7. **Esecuzione script dati esempio**

---

## ✅ Stato Attuale - Cosa Funziona

### Implementato
- ✅ Form US base (campo rapporti incluso)
- ✅ Form Inventario base
- ✅ Harris Matrix con matplotlib
- ✅ Export PDF base
- ✅ Validazione form con errori visibili
- ✅ Session management corretto
- ✅ 4 percorsi per Harris Matrix

### Parziale
- ⚠️ Form US - mancano molti campi (solo ~10/50 campi)
- ⚠️ Form Inventario - mancano molti campi (solo ~10/80 campi)
- ⚠️ Harris Matrix - matplotlib invece di Graphviz
- ⚠️ PDF - formato base, non identico desktop GUI
- ❌ Nessun validatore rapporti
- ❌ Nessun fix automatico
- ❌ Nessun upload database

---

## 🎯 Task 1: Eseguire Script Dati Esempio

**Priorità**: IMMEDIATA

**Problema**: Dataset di esempio non caricato

**Soluzione**:
```bash
python scripts/create_sample_for_webapp.py
```

**Verifica**:
```bash
# Check database
sqlite3 data/pyarchinit_mini.db "SELECT COUNT(*) FROM site_table;"
sqlite3 data/pyarchinit_mini.db "SELECT COUNT(*) FROM us_table;"
sqlite3 data/pyarchinit_mini.db "SELECT COUNT(*) FROM inventario_materiali_table;"
```

**Output atteso**:
- 3 siti
- 14 US
- 10 reperti

---

## 🎯 Task 2: Form US Completo (Desktop GUI Parity)

**File da modificare**:
- `web_interface/app.py` - USForm class
- `web_interface/templates/us/form.html` - Template

### Desktop GUI ha 7 TAB:

#### Tab 1: Informazioni Base
**Campi** (✅ = implementato, ❌ = mancante):
- ✅ Sito *
- ✅ Area
- ✅ US *
- ❌ Unità Tipo (US, USM, USV, USR)
- ✅ Anno Scavo
- ❌ Scavato (Sì/No)
- ❌ Attività (Scavo/Pulizia/Documentazione)
- ✅ Schedatore
- ❌ Data Schedatura
- ❌ Quota Min
- ❌ Quota Max
- ❌ Quota Assoluta
- ❌ Livello Appartenenza

#### Tab 2: Descrizione
- ✅ Descrizione Stratigrafica
- ✅ Descrizione Interpretativa
- ✅ Descrizione Dettagliata
- ✅ Interpretazione
- ❌ Osservazioni
- ❌ Elementi Datanti
- ❌ Datazione Estesa

#### Tab 3: Caratteristiche Fisiche
- ✅ Formazione (Natural/Artificial)
- ❌ Modo Formazione
- ❌ Componenti Organici
- ❌ Componenti Inorganici
- ❌ Colore
- ❌ Consistenza
- ❌ Aggregazione
- ❌ Tessitura
- ❌ Inclusioni
- ❌ Lunghezza
- ❌ Larghezza
- ❌ Spessore
- ❌ Forma

#### Tab 4: Cronologia/Periodizzazione
- ❌ Periodo Iniziale
- ❌ Fase Iniziale
- ❌ Periodo Finale
- ❌ Fase Finale
- ❌ Datazione Archeo-Stratigrafica

#### Tab 5: Rapporti Stratigrafici
- ✅ Rapporti (campo testuale)
- ❌ Editor grafico rapporti
- ❌ Validazione automatica
- ❌ Fix rapporti reciproci

#### Tab 6: Media
- ❌ Lista media associati
- ❌ Upload foto
- ❌ Thumbnails

#### Tab 7: Documentazione
- ❌ Piante
- ❌ Sezioni
- ❌ Foto

**Priorità campi**: Almeno Tab 1-5 completi

---

## 🎯 Task 3: Form Inventario Completo (Desktop GUI Parity)

**File da modificare**:
- `web_interface/app.py` - InventarioForm class
- `web_interface/templates/inventario/form.html`

### Desktop GUI ha 9 TAB:

#### Tab 1: Identificazione
**Campi** (✅ = implementato, ❌ = mancante):
- ✅ Sito *
- ✅ Numero Inventario *
- ❌ ID Oggetto
- ❌ Tipo Contenitore
- ❌ Tipo Reperto (più dettagliato)
- ✅ Definizione
- ❌ Descrizione Oggetto
- ✅ Area
- ✅ US
- ❌ Quadrato/Settore
- ❌ Livello
- ❌ Schedatore
- ❌ Data Schedatura

#### Tab 2: Classificazione
- ❌ Classe Materiale
- ❌ Tipo
- ❌ Forma
- ❌ Decorazione
- ❌ Produzione
- ❌ Datazione
- ❌ Confronti

#### Tab 3: Contesto
- ❌ Contesto di rinvenimento
- ❌ Posizione nell'US
- ❌ Associazioni

#### Tab 4: Caratteristiche Fisiche
- ✅ Peso
- ❌ Lunghezza
- ❌ Larghezza
- ❌ Altezza
- ❌ Diametro
- ❌ Spessore
- ❌ Colore Ext
- ❌ Colore Int
- ❌ Consistenza

#### Tab 5: Conservazione
- ❌ Stato Conservazione
- ❌ Completezza
- ❌ Rotture
- ❌ Restauri
- ❌ Interventi

#### Tab 6: Ceramica (specifico)
- ❌ Corpo Ceramico
- ❌ Rivestimento
- ❌ Cottura
- ❌ Tecnica Manifattura
- ❌ Inclusi

#### Tab 7: Misure
- ❌ Diametro orlo
- ❌ Diametro base
- ❌ Diametro massimo
- ❌ Anse
- ❌ Piedi

#### Tab 8: Documentazione
- ❌ Bibliografia
- ❌ Note
- ❌ Disegni
- ❌ Tavola

#### Tab 9: Media
- ❌ Foto associate
- ❌ Upload immagini

**Priorità campi**: Almeno Tab 1-6 completi

---

## 🎯 Task 4: Harris Matrix con Graphviz

**File**: Già esistente! `pyarchinit_mini/harris_matrix/pyarchinit_visualizer.py`

**Implementazione Web**:

### A. Route per Graphviz
Aggiungere a `web_interface/app.py`:

```python
@app.route('/harris_matrix/<site_name>/graphviz')
def harris_matrix_graphviz(site_name):
    """Harris Matrix con Graphviz come desktop GUI"""
    try:
        from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer

        # Generate matrix
        graph = matrix_generator.generate_matrix(site_name)
        visualizer = PyArchInitMatrixVisualizer()

        # Create SVG output
        svg_path = visualizer.create_matrix(graph, output_format='svg')

        # Read SVG
        with open(svg_path, 'r') as f:
            svg_content = f.read()

        return render_template('harris_matrix/graphviz.html',
                             site_name=site_name,
                             svg_content=svg_content,
                             stats=matrix_generator.get_matrix_statistics(graph))
    except Exception as e:
        flash(f'Errore: {e}', 'error')
        return redirect(url_for('sites_list'))
```

### B. Template con scelta visualizzatore
```html
<div class="btn-group">
    <a href="/harris_matrix/{{ site_name }}" class="btn btn-primary">
        Matplotlib (corrente)
    </a>
    <a href="/harris_matrix/{{ site_name }}/graphviz" class="btn btn-success">
        Graphviz (Desktop GUI)
    </a>
</div>
```

---

## 🎯 Task 5: Validatore Rapporti Stratigrafici

**File**: Già esistente! `pyarchinit_mini/utils/stratigraphic_validator.py`

### Funzionalità da implementare:

#### A. Validazione Automatica al Salvataggio

In `web_interface/app.py`, route `create_us`:

```python
from pyarchinit_mini.utils.stratigraphic_validator import StratigraphicValidator

@app.route('/us/create', methods=['GET', 'POST'])
def create_us():
    # ... existing code ...

    if form.validate_on_submit():
        # Validate stratigraphic relationships
        validator = StratigraphicValidator()

        # Get all US for site
        site_name = form.sito.data
        all_us = us_service.get_us_by_site(site_name)
        us_list = [us.to_dict() for us in all_us]

        # Add new US to list
        new_us_data = {
            'us': form.us.data,
            'sito': site_name,
            'area': form.area.data,
            'rapporti': form.rapporti.data
        }
        us_list.append(new_us_data)

        # Validate
        errors = validator.validate_all(us_list)

        if errors:
            for error in errors:
                flash(f'Attenzione: {error}', 'warning')

        # Save anyway but show warnings
        us = us_service.create_us(us_data)
        flash(f'US {us_data["us"]} creata con successo!', 'success')
```

#### B. Pagina Validazione Completa

Route nuova: `/us/validate/<site_name>`

```python
@app.route('/us/validate/<site_name>')
def validate_us(site_name):
    """Valida tutti i rapporti stratigrafici di un sito"""
    validator = StratigraphicValidator()

    # Get all US
    all_us = us_service.get_us_by_site(site_name)
    us_list = [us.to_dict() for us in all_us]

    # Get validation report
    report = validator.get_validation_report(us_list)

    # Get fix suggestions
    fixes = validator.generate_relationship_fixes(us_list)

    return render_template('us/validation_report.html',
                         site_name=site_name,
                         report=report,
                         fixes=fixes)
```

#### C. Fix Automatici

Route: `/us/fix/<site_name>`

```python
@app.route('/us/fix/<site_name>', methods=['POST'])
def fix_us_relationships(site_name):
    """Applica fix automatici ai rapporti"""
    validator = StratigraphicValidator()

    all_us = us_service.get_us_by_site(site_name)
    us_list = [us.to_dict() for us in all_us]

    fixes = validator.generate_relationship_fixes(us_list)

    # Apply updates
    for update in fixes['updates']:
        us_service.update_us(update['us_id'], {
            'rapporti': update['new_value']
        })

    # Create missing US
    for create in fixes['creates']:
        us_service.create_us(create)

    flash(f"Applicati {len(fixes['updates'])} aggiornamenti e create {len(fixes['creates'])} US", 'success')
    return redirect(url_for('validate_us', site_name=site_name))
```

---

## 🎯 Task 6: Upload Database

**Route nuova**: `/admin/upload_database`

### Implementazione:

```python
from werkzeug.utils import secure_filename
import shutil

@app.route('/admin/upload_database', methods=['GET', 'POST'])
def upload_database():
    """Upload SQLite database file"""
    if request.method == 'POST':
        if 'database' not in request.files:
            flash('Nessun file selezionato', 'error')
            return redirect(request.url)

        file = request.files['database']
        if file.filename == '':
            flash('Nessun file selezionato', 'error')
            return redirect(request.url)

        if file and file.filename.endswith('.db'):
            # Save uploaded file
            filename = secure_filename(file.filename)
            upload_path = os.path.join('data', 'uploaded_' + filename)
            file.save(upload_path)

            # Backup current database
            if os.path.exists('data/pyarchinit_mini.db'):
                backup_path = f'data/backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
                shutil.copy('data/pyarchinit_mini.db', backup_path)

            # Replace database
            shutil.copy(upload_path, 'data/pyarchinit_mini.db')

            flash('Database caricato con successo!', 'success')

            # Reload services
            global db_manager, site_service, us_service
            db_conn = DatabaseConnection.from_url('sqlite:///./data/pyarchinit_mini.db')
            db_manager = DatabaseManager(db_conn)
            site_service = SiteService(db_manager)
            us_service = USService(db_manager)

            return redirect(url_for('index'))

    return render_template('admin/upload_database.html')

@app.route('/admin/connect_postgresql', methods=['GET', 'POST'])
def connect_postgresql():
    """Connect to PostgreSQL database"""
    if request.method == 'POST':
        host = request.form.get('host', 'localhost')
        port = request.form.get('port', '5432')
        database = request.form.get('database')
        username = request.form.get('username')
        password = request.form.get('password')

        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"

        try:
            # Test connection
            db_conn = DatabaseConnection.from_url(connection_string)

            # Save connection
            os.environ['DATABASE_URL'] = connection_string

            # Reload services
            global db_manager, site_service, us_service
            db_manager = DatabaseManager(db_conn)
            site_service = SiteService(db_manager)
            us_service = USService(db_manager)

            flash('Connesso a PostgreSQL con successo!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Errore connessione: {e}', 'error')

    return render_template('admin/connect_postgresql.html')
```

### Template Upload Database

`web_interface/templates/admin/upload_database.html`:

```html
<form method="POST" enctype="multipart/form-data">
    <div class="mb-3">
        <label>Carica Database SQLite</label>
        <input type="file" name="database" accept=".db" class="form-control">
    </div>
    <button type="submit" class="btn btn-primary">Carica Database</button>
</form>

<hr>

<h4>Oppure Connetti a PostgreSQL</h4>
<a href="{{ url_for('connect_postgresql') }}" class="btn btn-secondary">
    Connetti PostgreSQL
</a>
```

---

## 🎯 Task 7: PDF Identico Desktop GUI

**File**: `pyarchinit_mini/pdf_export/pdf_generator.py`

### Confronto Desktop vs Web:

**Desktop GUI PDF include**:
- Intestazione sito con logo
- Tabelle US formattate con tutti i campi
- Sezioni separate per:
  - Dati sito
  - Lista US con descrizioni complete
  - Rapporti stratigrafici
  - Periodizzazione
  - Inventario
- Grafici statistici
- Harris Matrix embedded
- Bibliografia

**Web App PDF (attuale)**:
- Solo testo base
- Campi limitati

### Implementazione:

Leggere `pdf_generator.py` desktop e replicare stesso formato.

---

## 📅 Timeline Implementazione

### Fase 1: Immediate (1-2 ore)
1. ✅ Eseguire script dati esempio
2. ✅ Verificare caricamento database

### Fase 2: Form Completi (3-4 ore)
3. Completare USForm con almeno Tab 1-5
4. Completare InventarioForm con almeno Tab 1-6
5. Aggiornare template con nuovi campi

### Fase 3: Validazione (2-3 ore)
6. Aggiungere validazione automatica al salvataggio
7. Creare pagina validazione report
8. Implementare fix automatici

### Fase 4: Harris Matrix (1-2 ore)
9. Aggiungere route Graphviz
10. Template con scelta visualizzatore
11. Test rendering SVG

### Fase 5: Upload Database (1-2 ore)
12. Route upload SQLite
13. Route connect PostgreSQL
14. Template admin

### Fase 6: PDF Desktop-Style (3-4 ore)
15. Replicare formato PDF desktop
16. Embedded Harris Matrix
17. Test stampa

### Totale stimato: 11-17 ore

---

## 🧪 Testing Checklist

### Dopo Fase 1
- [ ] Database contiene 3 siti
- [ ] Database contiene 14 US
- [ ] Database contiene 10 reperti
- [ ] Web app carica dati

### Dopo Fase 2
- [ ] Form US ha tutti i campi Tab 1-5
- [ ] Form Inventario ha tutti i campi Tab 1-6
- [ ] Salvataggio funziona con nuovi campi
- [ ] Template visualizza tutti i campi

### Dopo Fase 3
- [ ] Validazione rileva paradossi
- [ ] Fix rapporti reciproci funziona
- [ ] Creazione US mancanti funziona
- [ ] Report validazione chiaro

### Dopo Fase 4
- [ ] Graphviz genera SVG corretto
- [ ] Visualizzazione web funziona
- [ ] Scelta tra matplotlib/graphviz

### Dopo Fase 5
- [ ] Upload SQLite funziona
- [ ] Connessione PostgreSQL funziona
- [ ] Reload servizi automatico

### Dopo Fase 6
- [ ] PDF identico desktop
- [ ] Harris Matrix embedded
- [ ] Tutti i campi presenti

---

## 📝 Note Implementazione

### Priorità Assolute
1. **Eseguire script dati** - TEST immediato
2. **Form completi** - Parità desktop
3. **Validatore** - Qualità dati

### Nice to Have
- Grafici statistici in PDF
- Editor grafico rapporti
- Media management completo

### Dipendenze
- Graphviz: `pip install graphviz` + install system binary
- PostgreSQL: `pip install psycopg2-binary`

---

## 🚀 Prossimi Passi

**ADESSO**:
1. Eseguire script dati esempio
2. Verificare caricamento
3. Iniziare Fase 2 (form completi)
