# Extended Matrix Framework - Guida Completa

## Indice
1. [Introduzione](#introduzione)
2. [Tipi di Unità](#tipi-di-unità)
3. [Simboli di Relazione](#simboli-di-relazione)
4. [Unità DOC e Documenti](#unità-doc-e-documenti)
5. [Export GraphML per yEd](#export-graphml-per-yed)
6. [Best Practices](#best-practices)
7. [Esempi Pratici](#esempi-pratici)

---

## Introduzione

L'**Extended Matrix Framework** (EMF) è un sistema avanzato per la documentazione archeologica che estende la tradizionale matrice di Harris con nuovi tipi di unità e relazioni specializzate.

PyArchInit-Mini implementa completamente l'Extended Matrix Framework, permettendo di:
- Documentare diverse tipologie di unità stratigrafiche e non-stratigrafiche
- Gestire relazioni complesse tra unità
- Collegare documenti multimediali alle unità
- Esportare matrici complesse in formato GraphML per yEd

---

## Tipi di Unità

### Unità Stratigrafiche Standard

#### **US** - Unità Stratigrafica
- **Descrizione**: Unità stratigrafica tradizionale
- **Simbolo relazione**: `>` (sopra) / `<` (sotto)
- **Uso**: Depositi, livelli, strati naturali
- **Esempio**: US 1001 - Strato di riempimento

#### **USM** - Unità Stratigrafica Muraria
- **Descrizione**: Unità stratigrafica di tipo murario
- **Simbolo relazione**: `>` / `<`
- **Uso**: Muri, strutture edilizie, elevati
- **Esempio**: USM 2001 - Muro in laterizi

### Unità Stratigrafiche Specializzate

#### **VSF** - Virtual Stratigraphic Face
- **Descrizione**: Interfaccia stratigrafica virtuale
- **Simbolo relazione**: `>` / `<`
- **Uso**: Superfici di interfaccia, piani di calpestio
- **Esempio**: VSF 3001 - Piano di calpestio fase II

#### **SF** - Stratigraphic Face
- **Descrizione**: Interfaccia stratigrafica fisica
- **Simbolo relazione**: `>` / `<`
- **Uso**: Superfici di taglio, discontinuità
- **Esempio**: SF 3002 - Superficie di taglio trincea

### Unità Stratigrafiche Distruttive

#### **USD** - Unità Stratigrafica Distruttiva
- **Descrizione**: Azione negativa/distruttiva
- **Simbolo relazione**: `>` / `<`
- **Uso**: Tagli, asportazioni, distruzioni
- **Esempio**: USD 4001 - Taglio di fondazione

#### **CON** - Connector
- **Descrizione**: Connettore tra unità
- **Simbolo relazione**: `>` / `<`
- **Uso**: Collegamenti fisici tra strutture
- **Esempio**: CON 5001 - Connessione tra USM 2001 e USM 2002

### Unità Stratigrafiche Virtuali (Gruppi)

#### **USVA** - Unità Stratigrafica Virtuale A
- **Descrizione**: Gruppo virtuale tipo A (blu)
- **Simbolo relazione**: `>` / `<`
- **Uso**: Raggruppamento funzionale/cronologico
- **Esempio**: USVA 6001 - Gruppo fase arcaica

#### **USVB** - Unità Stratigrafica Virtuale B
- **Descrizione**: Gruppo virtuale tipo B (verde)
- **Simbolo relazione**: `>` / `<`
- **Uso**: Raggruppamento tematico
- **Esempio**: USVB 6002 - Gruppo strutture produttive

#### **USVC** - Unità Stratigrafica Virtuale C
- **Descrizione**: Gruppo virtuale tipo C
- **Simbolo relazione**: `>` / `<`
- **Uso**: Altri raggruppamenti logici
- **Esempio**: USVC 6003 - Gruppo livelli di abbandono

### Unità Non-Stratigrafiche

#### **TU** - Typological Unit
- **Descrizione**: Unità tipologica
- **Simbolo relazione**: `>` / `<`
- **Uso**: Classificazioni tipologiche
- **Esempio**: TU 7001 - Ceramica a vernice nera

#### **property** - Proprietà
- **Descrizione**: Attributo o proprietà
- **Simbolo relazione**: `>>` / `<<`
- **Uso**: Caratteristiche, attributi, metadati
- **Esempio**: property "colore_rosso"

#### **DOC** - Document
- **Descrizione**: Unità documentale
- **Simbolo relazione**: `>>` / `<<`
- **Uso**: Collegamenti a documenti, foto, file
- **Campo speciale**: `tipo_documento` (Image, PDF, DOCX, CSV, Excel, TXT)
- **Esempio**: DOC 8001 - Foto generale scavo (tipo: Image)

### Unità di Processo

#### **Extractor** - Estrattore
- **Descrizione**: Nodo che estrae informazioni
- **Simbolo relazione**: `>>` / `<<`
- **Uso**: Analisi, elaborazioni, derivazioni
- **Esempio**: Extractor "analisi_ceramica"

#### **Combiner** - Combinatore
- **Descrizione**: Nodo che combina informazioni
- **Simbolo relazione**: `>>` / `<<`
- **Uso**: Sintesi, aggregazioni, fusioni
- **Esempio**: Combiner "sintesi_fase_II"

---

## Simboli di Relazione

### Relazioni Standard: `>` e `<`

Le **unità stratigrafiche** utilizzano simboli singoli:
- `>` : indica "sopra a" o "più recente di"
- `<` : indica "sotto a" o "più antico di"

**Unità che usano `>` / `<`:**
- US, USM
- VSF, SF
- CON, USD
- USVA, USVB, USVC
- TU

**Esempio:**
```
US 1001 > US 1002
(US 1001 copre US 1002)
```

### Relazioni Speciali: `>>` e `<<`

Le **unità non-stratigrafiche e di processo** utilizzano simboli doppi:
- `>>` : indica "è collegato a" o "deriva da"
- `<<` : indica "riceve da" o "è fonte per"

**Unità che usano `>>` / `<<`:**
- DOC (Document)
- property (Proprietà)
- Extractor (Estrattore)
- Combiner (Combinatore)

**Esempio:**
```
DOC 8001 >> US 1001
(Il documento DOC 8001 documenta l'US 1001)

Extractor "ceramica" >> US 1002
(L'estrattore analizza la ceramica dall'US 1002)
```

### Regole di Visualizzazione in yEd

Quando si esporta la matrice in formato GraphML per yEd:

1. **Unità stratigrafiche** (`>`, `<`)
   - Relazioni visualizzate con frecce standard
   - Layout verticale: più recente → più antico
   - Colori differenziati per tipo

2. **Unità non-stratigrafiche** (`>>`, `<<`)
   - Relazioni visualizzate con frecce doppie
   - Collegamenti trasversali alla stratigrafia
   - Evidenziazione speciale per DOC

---

## Unità DOC e Documenti

### Funzionalità Speciale

Le unità di tipo **DOC** hanno funzionalità uniche:
1. Il campo **tipo_documento** che specifica il formato del file
2. L'**upload del file** con salvataggio automatico nella cartella DoSC
3. Il campo **file_path** che memorizza il percorso del file nel database

### Campo tipo_documento

Quando selezioni "DOC" come tipo di unità, appare automaticamente un campo aggiuntivo per specificare il tipo di documento:

**Tipi disponibili:**
- **Image** - File immagine (JPG, PNG, TIFF, ecc.)
- **PDF** - Documento PDF
- **DOCX** - Documento Word
- **CSV** - File dati CSV
- **Excel** - Foglio di calcolo Excel
- **TXT** - File di testo

### Upload del File

**Cartella DoSC (Documents Storage Collection)**:
- Tutti i file vengono salvati automaticamente in `DoSC/`
- Naming automatico: `{SITO}_{US}_{TIMESTAMP}_{NOMEFILE_ORIGINALE}`
- Percorso memorizzato nel database nel campo `file_path`

**Esempio di naming**:
```
File originale: excavation_photo_2024.jpg
File salvato: DoSC/Pompei_DOC-8001_20251023_142530_excavation_photo_2024.jpg
Database field_path: "DoSC/Pompei_DOC-8001_20251023_142530_excavation_photo_2024.jpg"
```

### Esempi d'uso Completi

```
DOC 8001
  tipo_documento: Image
  file_path: DoSC/Pompei_DOC-8001_20251023_142530_photo.jpg
  descrizione: Foto generale area di scavo A, fase II
  collegato a: US 1001, US 1002, US 1003

DOC 8002
  tipo_documento: PDF
  file_path: DoSC/Pompei_DOC-8002_20251023_143015_report.pdf
  descrizione: Relazione preliminare scavo 2024
  collegato a: USVA 6001 (tutto il gruppo fase arcaica)

DOC 8003
  tipo_documento: Excel
  file_path: DoSC/Pompei_DOC-8003_20251023_150000_database.xlsx
  descrizione: Database reperti ceramici
  collegato a: TU 7001, TU 7002, TU 7003
```

### Interfacce

#### Web Interface
1. Campo "Tipo Unità" → seleziona **"DOC"**
2. Appaiono automaticamente due campi:
   - **"Tipo Documento"** - Menu dropdown per selezionare il tipo
   - **"Upload Document File"** - Campo per caricare il file
3. Click su "Choose File" → Seleziona file dal computer
4. Salva → File caricato automaticamente in DoSC

**Processo**:
```
1. Select Unit Type: DOC
2. Document Type appears → Choose "Image"
3. Upload Document File appears → Click "Choose File"
4. Browse and select: photo.jpg
5. Save → File uploaded to DoSC/Pompei_DOC-8001_20251023_142530_photo.jpg
```

#### Desktop GUI
1. Combobox "Unit Type" → seleziona **"DOC"**
2. Appaiono automaticamente due campi:
   - **"Document Type"** - Combobox per selezionare il tipo
   - **"Document File"** - Entry con pulsante "Sfoglia..."
3. Click su "Sfoglia..." → Dialogo per selezionare file
4. Salva → File copiato automaticamente in DoSC

**Processo**:
```
1. Select Unit Type: DOC
2. Document Type combobox appears → Choose "PDF"
3. Document File with "Browse..." button appears
4. Click "Browse..." → File dialog opens
5. Select file: report.pdf
6. Save → File copied to DoSC/Pompei_DOC-8002_20251023_143015_report.pdf
```

### Gestione File

**Accesso ai file**:
```bash
# Tutti i file DOC sono in DoSC/
ls -lh DoSC/

# File di un sito specifico
ls DoSC/ | grep "Pompei"

# File per tipo
ls DoSC/*.jpg    # Immagini
ls DoSC/*.pdf    # PDF
ls DoSC/*.xlsx   # Excel
```

**Backup**:
```bash
# Backup cartella DoSC
cp -r DoSC DoSC_backup_$(date +%Y%m%d)

# Backup compresso
tar -czf DoSC_backup_$(date +%Y%m%d).tar.gz DoSC/
```

> 📖 **Guida Completa**: Per maggiori dettagli sull'upload file, consulta [DOC File Upload Documentation](DOC_FILE_UPLOAD.md)

---

## Export GraphML per yEd

### Funzionalità

PyArchInit-Mini supporta l'export completo della matrice di Harris in formato GraphML ottimizzato per **yEd**.

### Come Esportare

#### Da Web Interface:
1. Vai alla lista US
2. Clicca su "Export Harris Matrix to GraphML (yEd)"
3. Seleziona sito e area
4. Download del file .graphml

#### Da Desktop GUI:
1. Apri il menu "Export"
2. Seleziona "Export Harris Matrix (GraphML)"
3. Scegli sito e area
4. Salva il file .graphml

### Visualizzazione in yEd

1. **Apri yEd** (scarica da: https://www.yworks.com/products/yed)

2. **Importa il file GraphML:**
   - File → Open → seleziona il .graphml esportato

3. **Applica layout automatico:**
   - Layout → Hierarchical
   - Orientation: Top to Bottom
   - Layer Assignment Policy: Hierarchical - Optimal

4. **Personalizza visualizzazione:**
   - Usa la palette Extended Matrix inclusa
   - Colori pre-configurati per ogni tipo di unità
   - Simboli di relazione (`>`, `>>`) già impostati

### Palette Extended Matrix

Il file `EM_palette.graphml` include:
- **Stili pre-configurati** per tutti i tipi di unità
- **Colori codificati:**
  - US/USM: bianco/grigio con bordo rosso
  - VSF/SF: bianco/giallo con bordi specifici
  - USVA: nero con bordo blu
  - USVB: nero con bordo verde
  - USD: bianco con bordo arancione
  - DOC: forma speciale per documenti
  - CON: connettore nero piccolo
  - Extractor/Combiner: icone SVG specializzate

---

## Best Practices

### 1. Scelta del Tipo di Unità

**Usa US/USM per:**
- Depositi archeologici tradizionali
- Strutture murarie
- Livelli naturali e antropici

**Usa VSF/SF per:**
- Interfacce tra depositi
- Superfici di calpestio
- Piani d'uso

**Usa USD per:**
- Tagli di fondazione
- Fosse
- Distruzioni intenzionali

**Usa USVA/USVB/USVC per:**
- Raggruppare US per fase cronologica
- Creare gruppi funzionali
- Organizzare per area di scavo

**Usa DOC per:**
- Collegare foto alle US
- Allegare relazioni
- Referenziare database esterni

**Usa property per:**
- Aggiungere metadati
- Specificare caratteristiche
- Annotazioni tecniche

**Usa Extractor/Combiner per:**
- Workflow di analisi
- Processi di elaborazione dati
- Derivazioni e sintesi

### 2. Nomenclatura

**Convenzioni suggerite:**

```
US:     numeri progressivi (1001, 1002, 1003...)
USM:    numeri progressivi separati (2001, 2002, 2003...)
VSF:    numeri con prefisso area (A3001, B3001...)
DOC:    numeri progressivi per anno (2024-001, 2024-002...)
USVA:   numeri per fase (FASE1-6001, FASE2-6002...)
```

### 3. Documentazione delle Relazioni

**Registra sempre:**
- Il tipo di relazione fisica (copre, taglia, riempie, ecc.)
- La certezza della relazione
- Note sulla stratigrafia

**Esempio:**
```
US 1001 copre US 1002
  - Certezza: certa
  - Note: Contatto netto, orizzontale
  - DOC 8001 documenta il contatto
```

### 4. Uso dei Documenti

**Organizza i DOC per categoria:**

```
DOC 8001-8099: Foto generali
DOC 8100-8199: Foto di dettaglio
DOC 8200-8299: Disegni
DOC 8300-8399: Relazioni
DOC 8400-8499: Database
```

**Collega sempre i DOC alle unità appropriate:**
- Foto generale → collegala al gruppo USVA
- Foto di dettaglio → collegala alla singola US
- Relazione → collegala a tutte le US pertinenti

### 5. Workflow Consigliato

1. **Fase di scavo:**
   - Crea US, USM, USD durante lo scavo
   - Registra le relazioni stratigrafiche
   - Crea DOC per ogni foto scattata

2. **Fase di post-processing:**
   - Crea VSF/SF per le interfacce
   - Crea gruppi USVA/USVB per le fasi
   - Aggiungi TU per le classificazioni

3. **Fase di analisi:**
   - Usa Extractor per le analisi specialistiche
   - Usa Combiner per le sintesi
   - Aggiungi property per i metadati

4. **Fase di pubblicazione:**
   - Esporta la matrice completa in GraphML
   - Genera visualizzazioni in yEd
   - Crea relazioni con collegamenti ai DOC

---

## Esempi Pratici

### Esempio 1: Scavo Stratigrafico Urbano

```
USVA 6001 - Fase Medievale
  ├─ US 1001 - Riempimento fossa
  ├─ USD 4001 - Taglio fossa
  └─ DOC 8001 (Image) - Foto generale fase medievale

USVA 6002 - Fase Romana
  ├─ US 1002 - Livello di crollo
  ├─ USM 2001 - Muro in opus reticulatum
  ├─ SF 3001 - Piano di calpestio
  └─ DOC 8002 (PDF) - Relazione fase romana

Relazioni:
  US 1001 > USD 4001 > US 1002
  USM 2001 = SF 3001 (contemporanei)
  DOC 8001 >> USVA 6001
  DOC 8002 >> USVA 6002
```

### Esempio 2: Struttura con Documentazione Complessa

```
USM 2001 - Muro perimetrale
  ├─ property "tecnica_costruttiva" = "opus incertum"
  ├─ property "cronologia" = "II sec. a.C."
  ├─ DOC 8010 (Image) - Foto prospetto nord
  ├─ DOC 8011 (Image) - Foto prospetto sud
  ├─ DOC 8012 (DOCX) - Scheda USM dettagliata
  └─ DOC 8013 (Excel) - Rilievo fotogrammetrico

Connessioni:
  CON 5001 - Connessione tra USM 2001 e USM 2002

Relazioni:
  property >> USM 2001
  DOC 8010 >> USM 2001
  DOC 8011 >> USM 2001
  DOC 8012 >> USM 2001
  DOC 8013 >> USM 2001
  CON 5001 > USM 2001
  CON 5001 > USM 2002
```

### Esempio 3: Analisi e Derivazioni

```
US 1003 - Strato di riempimento con ceramica

  ↓ analisi materiali

Extractor "analisi_ceramica" >> US 1003

  ↓ estrazione dati

TU 7001 - Ceramica a vernice nera
TU 7002 - Ceramica comune
TU 7003 - Anfore

  ↓ sintesi

Combiner "sintesi_reperti_US1003"

  ↓ output

DOC 8020 (Excel) - Database ceramica US 1003
DOC 8021 (PDF) - Relazione ceramologica

Relazioni complete:
  Extractor >> US 1003
  Extractor >> TU 7001
  Extractor >> TU 7002
  Extractor >> TU 7003
  Combiner << TU 7001
  Combiner << TU 7002
  Combiner << TU 7003
  DOC 8020 >> Combiner
  DOC 8021 >> Combiner
```

---

## Conclusioni

L'Extended Matrix Framework implementato in PyArchInit-Mini offre:

✅ **Flessibilità** - Tipi di unità per ogni esigenza documentale
✅ **Potenza** - Relazioni complesse tra unità stratigrafiche e non
✅ **Integrazione** - Collegamenti diretti ai documenti multimediali
✅ **Compatibilità** - Export completo per yEd e altri software
✅ **Scalabilità** - Dal singolo scavo al grande progetto multi-sito

Per ulteriori informazioni, consulta:
- [README principale](../README.md)
- [Documentazione completa](https://docs.pyarchinit.org)
- [Repository GitHub](https://github.com/pyarchinit/pyarchinit-mini)

---

**Versione documento**: 1.0
**Data**: 2025-10-23
**Autore**: PyArchInit Team
