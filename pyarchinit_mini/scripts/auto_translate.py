#!/usr/bin/env python3
"""
Auto-translate .po files:
- For English: Copy msgid to msgstr (since strings are already in English)
- For Italian: Add Italian translations for common UI strings
"""

import re
from pathlib import Path

# Italian translations dictionary
IT_TRANSLATIONS = {
    # Navigation
    "Dashboard": "Dashboard",
    "Analytics": "Analitiche",
    "Sites": "Siti",
    "Sites List": "Lista Siti",
    "New Site": "Nuovo Sito",
    "Stratigraphic Units": "Unità Stratigrafiche",
    "US List": "Lista US",
    "New US": "Nuova US",
    "Inventory": "Inventario",
    "Artifacts List": "Lista Reperti",
    "New Artifact": "Nuovo Reperto",
    "Media": "Media",
    "Harris Matrix": "Harris Matrix",
    "View": "Visualizza",
    "Export GraphML (yEd)": "Esporta GraphML (yEd)",
    "Export/Import": "Esporta/Importa",
    "online": "online",
    "Database": "Database",
    "Users": "Utenti",
    "API Docs": "Documentazione API",
    "Logout": "Esci",
    "Login": "Accedi",
    "Navigation": "Navigazione",
    "Archaeological Sites": "Siti Archeologici",
    "Material Inventory": "Inventario Materiali",
    "Tools": "Strumenti",
    "Upload Media": "Carica Media",
    "Administration": "Amministrazione",
    "Database Management": "Gestione Database",

    # Notifications
    "has connected": "si è collegato",
    "has disconnected": "si è disconnesso",
    "created site": "ha creato il sito",
    "modified site": "ha modificato il sito",
    "deleted site": "ha eliminato il sito",
    "created US": "ha creato US",
    "modified US": "ha modificato US",
    "deleted US": "ha eliminato US",
    "created artifact": "ha creato reperto",
    "modified artifact": "ha modificato reperto",
    "deleted artifact": "ha eliminato reperto",
    "Notification": "Notifica",
    "Now": "Ora",

    # Dashboard
    "Archaeological Dashboard": "Dashboard Archeologica",
    "Export": "Esporta",
    "Catalogued Artifacts": "Reperti Catalogati",
    "Media Files": "File Multimediali",
    "Recent Sites": "Siti Recenti",
    "Site Name": "Nome Sito",
    "Municipality": "Comune",
    "Province": "Provincia",
    "Actions": "Azioni",
    "Details": "Dettagli",
    "Edit": "Modifica",
    "Validate": "Valida",
    "Validate Relationships": "Valida Rapporti",
    "Site Report": "Relazione Sito",
    "Harris Matrix PDF": "Harris Matrix PDF",
    "View All Sites": "Visualizza Tutti i Siti",
    "No sites found": "Nessun sito presente",
    "Start by creating your first archaeological site": "Inizia creando il tuo primo sito archeologico",
    "Create First Site": "Crea Primo Sito",
    "Quick Actions": "Azioni Rapide",
    "System": "Sistema",
    "Version": "Versione",
    "Documentation": "Documentazione",
    "Interface": "Interfaccia",
    "Statistics by Type": "Statistiche per Tipologia",
    "Statistics charts available in full version": "Grafici statistiche disponibili nella versione completa",

    # Sites List
    "Search site...": "Cerca sito...",
    "Search": "Cerca",
    "Reset": "Reset",
    "Name": "Nome",
    "Country": "Nazione",
    "Region": "Regione",
    "View Details": "Visualizza Dettagli",
    "Edit Site": "Modifica Sito",
    "Export PDF": "Esporta PDF",
    "Total sites": "Totale siti",
    "No sites found.": "Nessun sito trovato.",
    "Create the first site": "Crea il primo sito",

    # Form buttons
    "Save": "Salva",
    "Cancel": "Annulla",
    "Save US": "Salva US",

    # US List
    "Filter": "Filtra",
    "All sites": "Tutti i siti",
    "Site": "Sito",
    "Year": "Anno",
    "Total": "Totale",
    "No US found.": "Nessuna US trovata.",
    "Edit US": "Modifica US",
    "Stratigraphic Description": "Descrizione Stratigrafica",
    "Excavation Year": "Anno Scavo",
    "Description": "Descrizione",

    # US Form tabs
    "Form errors:": "Errori nel form:",
    "Basic Information": "Informazioni Base",
    "Descriptions": "Descrizioni",
    "Physical Characteristics": "Caratteristiche Fisiche",
    "Chronology": "Cronologia",
    "Stratigraphic Relationships": "Relazioni Stratigrafiche",

    # Inventario
    "Inventory No.": "N. Inventario",
    "Type": "Tipo",
    "Definition": "Definizione",
    "Weight (g)": "Peso (g)",
    "Artifact type": "Tipo reperto",
    "Artifact Type": "Tipo Reperto",
    "Weight": "Peso",
    "Edit Artifact": "Modifica Reperto",
    "artifacts": "reperti",
    "No artifacts found.": "Nessun reperto trovato.",
    "Inv.": "Inv.",
    "Save Artifact": "Salva Reperto",

    # Harris Matrix
    "Back": "Indietro",
    "Matplotlib Visualizer (Simple)": "Visualizzatore Matplotlib (Semplice)",
    "For advanced visualization with groupings and desktop GUI style,": "Per una visualizzazione avanzata con raggruppamenti e stile desktop GUI,",
    "switch to Graphviz": "passa a Graphviz",
    "Relationships": "Relazioni",
    "Maximum Depth": "Profondità Massima",
    "Levels": "Livelli",
    "Matrix Visualization": "Visualizzazione Matrice",
    "No matrix available for this site.": "Nessuna matrice disponibile per questo sito.",
    "Stratigraphic Sequence": "Sequenza Stratigrafica",
    "Level": "Livello",

    # Desktop GUI - Window & Menu
    "PyArchInit-Mini - Archaeological Data Management": "PyArchInit-Mini - Gestione Dati Archeologici",
    "Ready": "Pronto",
    "File": "File",
    "New SQLite Database": "Nuovo Database SQLite",
    "New Site": "Nuovo Sito",
    "New US": "Nuova US",
    "New Artifact": "Nuovo Reperto",
    "Configure Database": "Configura Database",
    "Install PostgreSQL": "Installa PostgreSQL",
    "Load Sample Database": "Carica Database di Esempio",
    "Import Database": "Importa Database",
    "Export Database": "Esporta Database",
    "Exit": "Esci",
    "View": "Visualizza",
    "Tools": "Strumenti",
    "Thesaurus Management": "Gestione Thesaurus",
    "Export/Import Data": "Esporta/Importa Dati",
    "Help": "Aiuto",
    "About": "Informazioni",
    "User Guide": "Guida Utente",

    # Desktop GUI - Toolbar & Common
    "Current Site:": "Sito Corrente:",
    "Refresh": "Aggiorna",
    "Edit": "Modifica",
    "Delete": "Elimina",
    "Search:": "Cerca:",
    "General Statistics": "Statistiche Generali",
    "Recent Activity": "Attività Recente",

    # Desktop GUI - Sites Tab
    "Site Name": "Nome Sito",

    # Desktop GUI - US Tab
    "Validate Paradoxes": "Valida Paradossi",
    "Fix Relationships": "Fix Rapporti",
    "Area": "Area",

    # Desktop GUI - Inventory Tab
    "Inv. No.": "N. Inv.",
    "Ceramic": "Ceramica",
    "Metal": "Metallo",
    "Stone": "Pietra",
    "Bone": "Osso",
    "Glass": "Vetro",

    # Desktop GUI - Messageboxes
    "Database Error": "Errore Database",
    "Failed to initialize database: {}": "Impossibile inizializzare il database: {}",
    "Selection": "Selezione",
    "Select a site to edit": "Seleziona un sito da modificare",
    "Select a site to delete": "Seleziona un sito da eliminare",
    "Select a US to edit": "Seleziona una US da modificare",
    "Select a US to delete": "Seleziona una US da eliminare",
    "Select an artifact to edit": "Seleziona un reperto da modificare",
    "Select an artifact to delete": "Seleziona un reperto da eliminare",
    "Confirm": "Conferma",
    "Are you sure you want to delete the selected site?": "Sei sicuro di voler eliminare il sito selezionato?",
    "Are you sure you want to delete the selected US?": "Sei sicuro di voler eliminare la US selezionata?",
    "Are you sure you want to delete the selected artifact?": "Sei sicuro di voler eliminare il reperto selezionato?",
    "Success": "Successo",
    "Site deleted successfully": "Sito eliminato con successo",
    "US deleted successfully": "US eliminata con successo",
    "Artifact deleted successfully": "Reperto eliminato con successo",
    "Error": "Errore",
    "Error during deletion: {}": "Errore durante l'eliminazione: {}",
    "Warning": "Avviso",
    "No sites available to generate Harris Matrix": "Nessun sito disponibile per generare la Harris Matrix",

    # Desktop GUI - Dialogs (common buttons & labels)
    "OK": "OK",
    "Save": "Salva",
    "New Site": "Nuovo Sito",
    "Edit Site": "Modifica Sito",
    "Site Name *:": "Nome Sito *:",
    "Country:": "Nazione:",
    "Region:": "Regione:",
    "Site Definition:": "Definizione Sito:",
    "Site description:": "Descrizione del sito:",
    "Add Media": "Aggiungi Media",
    "Remove Selected": "Rimuovi Selezionato",
    "Preview": "Anteprima",
    "Drag media files here": "Trascina qui i file multimediali",
    "Drag media files here\\n(Images, PDF, Video, Audio)": "Trascina qui i file multimediali\n(Immagini, PDF, Video, Audio)",
    "Site name is required": "Il nome del sito è obbligatorio",
    "Site updated successfully": "Sito aggiornato con successo",
    "Site created successfully": "Sito creato con successo",
    "Error saving: {}": "Errore durante il salvataggio: {}",

    # Desktop GUI - USDialog
    "Edit US": "Modifica US",
    "Site *:": "Sito *:",
    "US Number *:": "Numero US *:",
    "Stratigraphic Description:": "Descrizione Stratigrafica:",
    "Interpretative Description:": "Descrizione Interpretativa:",
    "Cataloguer:": "Schedatore:",
    "Formation:": "Formazione:",
    "Natural": "Naturale",
    "Artificial": "Artificiale",
    "Site is required": "Il sito è obbligatorio",
    "US number is required": "Il numero US è obbligatorio",
    "US number must be an integer": "Il numero US deve essere un numero intero",
    "Excavation year must be a number": "L'anno scavo deve essere un numero",
    "US updated successfully": "US aggiornata con successo",
    "US created successfully": "US creata con successo",

    # Desktop GUI - InventarioDialog
    "Edit Artifact": "Modifica Reperto",
    "Inventory Number *:": "Numero Inventario *:",
    "Inventory number is required": "Il numero inventario è obbligatorio",
    "Inventory number must be an integer": "Il numero inventario deve essere un numero intero",
    "US must be a number": "US deve essere un numero",
    "Weight must be a number": "Il peso deve essere un numero",
    "Artifact updated successfully": "Reperto aggiornato con successo",
    "Artifact created successfully": "Reperto creato con successo",

    # Desktop GUI - HarrisMatrixDialog
    "Harris Matrix Generator": "Generatore Harris Matrix",
    "Close": "Chiudi",
    "Select Site:": "Seleziona Sito:",
    "Generate Matrix": "Genera Matrix",
    "Advanced Editor": "Editor Avanzato",
    "Export": "Esporta",
    "Matrix Visualization:": "Visualizzazione Matrix:",
    "Layout:": "Layout:",
    "Select a site and generate the Harris Matrix\n\nControls:\n• Drag with mouse to pan\n• Mouse wheel to zoom\n• Zoom buttons for precise control": "Seleziona un sito e genera la Harris Matrix\n\nControlli:\n• Trascina con il mouse per spostare\n• Rotella mouse per zoom\n• Pulsanti zoom per controllo preciso",
    "Select a site": "Seleziona un sito",
    "Generating Harris Matrix for {}...\n": "Generando Harris Matrix per {}...\n",
    "Completed": "Completato",
    "Harris Matrix generated successfully!": "Harris Matrix generata con successo!",
    "Error generating matrix: {}": "Errore nella generazione della matrix: {}",
    "HARRIS MATRIX STATISTICS - {}\n\nTotal US: {}\nStratigraphic Relationships: {}\nStratigraphic Levels: {}\nValid Matrix: {}\nIsolated US: {}\n\n": "STATISTICHE HARRIS MATRIX - {}\n\nTotale US: {}\nRelazioni Stratigrafiche: {}\nLivelli Stratigrafici: {}\nMatrix Valida: {}\nUS Isolate: {}\n\n",
    "Yes": "Sì",
    "No": "No",
    "⚠️ WARNING: The matrix contains cycles or logical errors\n": "⚠️ ATTENZIONE: La matrix contiene cicli o errori logici\n",
    "\nSTRATIGRAPHIC LEVELS:\n\n": "\nLIVELLI STRATIGRAFICI:\n\n",
    "Level {}: US {}\n": "Livello {}: US {}\n",
    "No data to visualize\nGenerate a Harris Matrix first": "Nessun dato da visualizzare\nGenera prima una Harris Matrix",
    "Harris Matrix - {} (Layout: {})": "Harris Matrix - {} (Layout: {})",
    "Error generating image\nTry the Advanced Editor": "Errore nella generazione dell'immagine\nProva l'Editor Avanzato",
    "Visualization error:\n{}\n\nUse the Advanced Editor for more options": "Errore nella visualizzazione:\n{}\n\nUsa l'Editor Avanzato per maggiori opzioni",
    "Generate a matrix first": "Genera prima una matrix",
    "Select folder for export": "Seleziona cartella per l'export",
    "Export Completed": "Export Completato",
    "Matrix exported to:\n\n{}": "Matrix esportata in:\n\n{}",
    "Error during export: {}": "Errore durante l'export: {}",
    "Services not available for advanced editor": "Servizi non disponibili per l'editor avanzato",
    "Database manager not available": "Database manager non disponibile",
    "Error opening editor: {}": "Errore apertura editor: {}",

    # Desktop GUI - PDFExportDialog
    "Export PDF": "Export PDF",
    "Export": "Esporta",
    "Cancel": "Annulla",
    "Select Site:": "Seleziona Sito:",
    "Export Type:": "Tipo Export:",
    "US Sheets": "Schede US",
    "Inventory Sheets": "Schede Inventario",
    "Complete Site Report": "Report Completo Sito",
    "Custom Logo:": "Logo Personalizzato:",
    "Browse...": "Sfoglia...",
    "Output File:": "File Output:",
    "Select logo": "Seleziona logo",
    "Images": "Immagini",
    "All files": "Tutti i file",
    "Save PDF report": "Salva report PDF",
    "Specify the output file": "Specifica il file di output",
    "Site not found": "Sito non trovato",
    "Data": "Dati",
    "No US found for site {}": "Nessuna US trovata per il sito {}",
    "US sheets saved to:\n{}": "Schede US salvate in:\n{}",
    "No artifacts found for site {}": "Nessun reperto trovato per il sito {}",
    "Inventory sheets saved to:\n{}": "Schede Inventario salvate in:\n{}",
    "Error generating PDF": "Errore nella generazione del PDF",
    "Complete report saved to:\n{}": "Report completo salvato in:\n{}",
    "Error generating PDF: {}": "Errore durante la generazione del PDF: {}",

    # Desktop GUI - DatabaseConfigDialog
    "Database Configuration": "Configurazione Database",
    "Connect": "Connetti",
    "Database Type": "Tipo Database",
    "SQLite (Local file)": "SQLite (File locale)",
    "PostgreSQL (Server)": "PostgreSQL (Server)",
    "SQLite Configuration": "Configurazione SQLite",
    "Database File:": "File Database:",
    "Browse": "Sfoglia",
    "Sample Database": "Database di Esempio",
    "New Database": "Nuovo Database",
    "Import Database": "Importa Database",
    "PostgreSQL Configuration": "Configurazione PostgreSQL",
    "Host:": "Host:",
    "Port:": "Porta:",
    "Database:": "Database:",
    "Username:": "Username:",
    "Password:": "Password:",
    "Test Connection": "Test Connessione",
    "Information": "Informazioni",
    """DATABASE CONFIGURATION

SQLite:
• Local database stored in a file
• Ideal for single user
• Easy to transport and share

PostgreSQL:
• Professional database server
• Supports multi-user access
• Better performance for large datasets
• Requires PostgreSQL server installation

NOTE: Changing database will reload the interface
and data migrations may be required.""": """CONFIGURAZIONE DATABASE

SQLite:
• Database locale memorizzato in un file
• Ideale per uso singolo utente
• Facile da trasportare e condividere

PostgreSQL:
• Database server professionale
• Supporta accesso multi-utente
• Migliori prestazioni per grandi dataset
• Richiede installazione server PostgreSQL

NOTA: Cambiare database ricaricherà l'interfaccia
e potrebbero essere necessarie migrazioni dati.""",
    "Select SQLite database file": "Seleziona file database SQLite",
    "Sample database loaded!\n\nContents:\n• 1 Archaeological site\n• 100 Stratigraphic units\n• 50 Artifacts\n• 70+ Stratigraphic relationships": "Database di esempio caricato!\n\nContenuto:\n• 1 Sito archeologico\n• 100 Unità Stratigrafiche\n• 50 Materiali\n• 70+ Relazioni stratigrafiche",
    "Missing Database": "Database Mancante",
    "The sample database does not exist.\nDo you want to create it now?": "Il database di esempio non esiste.\nVuoi crearlo ora?",
    "Create new SQLite database": "Crea nuovo database SQLite",
    "New database created: {}": "Nuovo database creato: {}",
    "Import SQLite database": "Importa database SQLite",
    "Database imported: {}": "Database importato: {}",
    "Sample database created successfully!\n\nContents:\n• 1 Archaeological site\n• 100 US with relationships\n• 50 Artifacts": "Database di esempio creato con successo!\n\nContenuto:\n• 1 Sito archeologico\n• 100 US con relazioni\n• 50 Materiali",
    "Database creation error: {}": "Errore creazione database: {}",
    "Database creation script not found": "Script di creazione database non trovato",
    "Error during creation: {}": "Errore durante la creazione: {}",
    "PostgreSQL connection successful!": "Connessione PostgreSQL riuscita!",
    "PostgreSQL connection failed": "Connessione PostgreSQL fallita",
    "Connection test error: {}": "Errore test connessione: {}",
    "All PostgreSQL fields are required": "Tutti i campi PostgreSQL sono obbligatori",
    "Specify the SQLite file path": "Specifica il percorso del file SQLite",
    "Unable to connect to database": "Impossibile connettersi al database",
    "Database configuration error: {}": "Errore configurazione database: {}",

    # Desktop GUI - MediaManagerDialog
    "Media Management": "Gestione Media",
    "Upload New File": "Carica Nuovo File",
    "File:": "File:",
    "Entity Type:": "Tipo Entità:",
    "Entity ID:": "ID Entità:",
    "Description:": "Descrizione:",
    "Upload File": "Carica File",
    "Media Files": "File Multimediali",
    "Media file list (in development)": "Lista file multimediali (in sviluppo)",
    "Select file to upload": "Seleziona file da caricare",
    "Documents": "Documenti",
    "Videos": "Video",
    "Select a file to upload": "Seleziona un file da caricare",
    "Entity": "Entità",
    "Select the entity type": "Seleziona il tipo di entità",
    "ID": "ID",
    "Enter the entity ID": "Inserisci l'ID dell'entità",
    "ID must be a number": "L'ID deve essere un numero",
    "File uploaded successfully!": "File caricato con successo!",
    "Error during upload: {}": "Errore durante il caricamento: {}",

    # Desktop GUI - StatisticsDialog
    "Statistics": "Statistiche",
    "Refresh": "Aggiorna",
    "PYARCHINIT-MINI STATISTICS\nDate: {}\n\nOVERALL TOTALS:\n• Archaeological Sites: {}\n• Stratigraphic Units: {}\n• Catalogued Artifacts: {}\n\nDETAILS BY SITE:\n": "STATISTICHE PYARCHINIT-MINI\nData: {}\n\nTOTALI GENERALI:\n• Siti Archeologici: {}\n• Unità Stratigrafiche: {}\n• Reperti Catalogati: {}\n\nDETTAGLIO PER SITO:\n",
    "  - US: {}\n": "  - US: {}\n",
    "  - Artifacts: {}\n": "  - Reperti: {}\n",
    "  - Municipality: {}\n": "  - Comune: {}\n",
    "Error loading statistics: {}": "Errore caricamento statistiche: {}",

    # Desktop GUI - Extended US Dialog
    "New US": "Nuova US",
    "Edit US {}": "Modifica US {}",
    "Delete": "Elimina",
    "Identification": "Identificazione",
    "Unit Type:": "Tipo Unità:",
    "Excavation Data": "Dati di Scavo",
    "Excavation Year:": "Anno Scavo:",
    "Excavated:": "Scavato:",
    "Partially": "Parzialmente",
    "Excavation Method:": "Metodo Scavo:",
    "Manual": "Manuale",
    "Mechanical": "Meccanico",
    "Mixed": "Misto",
    "Record Date:": "Data Schedatura:",
    "Activity:": "Attività:",
    "Descriptions": "Descrizioni",
    "Stratigraphic Description:": "Descrizione Stratigrafica:",
    "Interpretative Description:": "Descrizione Interpretativa:",
    "Interpretation:": "Interpretazione:",
    "Observations:": "Osservazioni:",
    "Physical Characteristics": "Caratteristiche Fisiche",
    "Chronology": "Cronologia",
    "Stratigraphic Relationships": "Relazioni Stratigrafiche",
    "Media": "Media",
    "Documentation": "Documentazione",

    # Desktop GUI - Settings & Language Preference
    "Settings": "Impostazioni",
    "Language": "Lingua",
    "Language Selection": "Selezione Lingua",
    "Select Language:": "Seleziona Lingua:",
    "Language Changed": "Lingua Modificata",
    "Language preference saved.\nPlease restart the application for changes to take effect.": "Preferenza lingua salvata.\nRiavvia l'applicazione per applicare le modifiche.",

    # Web GUI - Navbar Compact
    "Menu": "Menu",
    "Main Sections": "Sezioni Principali",
    "Tools": "Strumenti",

    # PDF Export - General
    "Archaeological Report": "Relazione Archeologica",
    "Archaeological Site": "Sito Archeologico",
    "Site:": "Sito:",
    "Date:": "Data",
    "Generated by PyArchInit-Mini": "Generato da PyArchInit-Mini",

    # PDF Export - Site Information Section
    "1. SITE INFORMATION": "1. INFORMAZIONI SITO",
    "1.1 Location": "1.1 Localizzazione",
    "1.2 Description": "1.2 Descrizione",
    "1.3 Site Definition": "1.3 Definizione Sito",

    # PDF Export - US Section
    "2. STRATIGRAPHIC UNITS": "2. UNITÀ STRATIGRAFICHE",
    "2.1 US List": "2.1 Elenco US",
    "2.2 Detailed Descriptions": "2.2 Descrizioni Dettagliate",

    # PDF Export - Inventory Section
    "3. MATERIAL INVENTORY": "3. INVENTARIO MATERIALI",
    "3.1 Statistics": "3.1 Statistiche",
    "3.2 Artifacts List": "3.2 Elenco Reperti",
    "Total catalogued artifacts": "Totale reperti catalogati",
    "Ceramic materials": "Materiali ceramici",
    "Metal materials": "Materiali metallici",
    "State": "Stato",

    # PDF Export - Media Section
    "4. PHOTOGRAPHIC DOCUMENTATION": "4. DOCUMENTAZIONE FOTOGRAFICA",
    "4.1 Media List": "4.1 Elenco Media",
    "Total media files": "Totale file media",
    "File Name": "Nome File",
    "Entity": "Entità",
    "Author": "Autore",

    # PDF Export - Harris Matrix Report
    "Matrix Statistics": "Statistiche Matrix",
    "Total US:": "Totale US:",
    "Relationships:": "Relazioni:",
    "Levels:": "Livelli:",
    "Valid Matrix:": "Matrix Valida:",
    "Yes": "Sì",
    "Isolated US:": "US Isolate:",
    "Harris Matrix Diagram": "Diagramma Harris Matrix",

    # PDF Export - ICCD US Form Fields
    "LOCALITY": "LOCALITÀ",
    "AREA/BUILDING/STRUCTURE": "AREA/EDIFICIO/STRUTTURA",
    "IDENTIFICATION NUMBER/CODE OF STRATIGRAPHIC UNIT": "NUMERO/CODICE IDENTIFICATIVO DELL'UNITÀ STRATIGRAFICA",
    "NAT.": "NAT.",
    "Natural": "Naturale",
    "ART.": "ART.",
    "Artificial": "Artificiale",
    "DEFINITION AND POSITION": "DEFINIZIONE E POSIZIONE",
    "Stratigraphic definition": "Definizione stratigrafica",
    "Interpretative definition": "Definizione interpretativa",
    "DESCRIPTION": "DESCRIZIONE",
    "INTERPRETATION": "INTERPRETAZIONE",

    # PDF Export - Stratigraphic Relationships
    "BONDS TO": "SI LEGA A",
    "EQUAL TO": "UGUALE A",
    "COVERS": "COPRE",
    "COVERED BY": "COPERTO DA",
    "CUTS": "TAGLIA",
    "CUT BY": "TAGLIATO DA",
    "FILLS": "RIEMPIE",
    "FILLED BY": "RIEMPITO DA",
    "LEANS AGAINST": "SI APPOGGIA",
    "LEANED AGAINST BY": "GLI SI APPOGGIA",
    "LATER THAN": "POSTERIORE A",
    "EARLIER THAN": "ANTERIORE A",

    # PDF Export - Physical Characteristics
    "STATE OF CONSERVATION": "STATO DI CONSERVAZIONE",
    "CONSISTENCY": "CONSISTENZA",
    "COLOR": "COLORE",
    "INCLUSIONS": "INCLUSI",
    "SAMPLES": "CAMPIONI",
    "Flotation": "Flottazione",
    "Sieving": "Setacciatura",
    "ENVIRONMENT": "AMBIENTE",
    "POSITION IN ENVIRONMENT": "POS. NELL'AMBIENTE",
    "SECTOR(S)": "SETTORE/I",
    "SQUARE(S)": "QUADRATO/I",
    "TRENCH": "SAGGIO",
    "ELEVATIONS": "QUOTE",
    "min": "min",
    "max": "max",

    # PDF Export - Documentation
    "PLANS": "PIANTE",
    "SECTIONS": "SEZIONI",
    "PHOTOGRAPHS": "FOTOGRAFIE",
    "DISTINCTION CRITERIA": "CRITERI DI DISTINZIONE",
    "FORMATION MODE": "MODO FORMAZIONE",
    "MEASUREMENTS": "MISURE",

    # PDF Export - Components
    "ORGANIC": "ORGANICI",
    "INORGANIC": "INORGANICI",
    "C<br/>O<br/>M<br/>P<br/>O<br/>N<br/>E<br/>N<br/>T<br/>S": "C<br/>O<br/>M<br/>P<br/>O<br/>N<br/>E<br/>N<br/>T<br/>I",
    "S<br/>T<br/>R<br/>A<br/>T<br/>I<br/>G<br/>R<br/>A<br/>P<br/>H<br/>I<br/>C<br/><br/>S<br/>E<br/>Q<br/>U<br/>E<br/>N<br/>C<br/>E": "S<br/>E<br/>Q<br/>U<br/>E<br/>N<br/>Z<br/>A<br/><br/>S<br/>T<br/>R<br/>A<br/>T<br/>I<br/>G<br/>R<br/>A<br/>F<br/>I<br/>C<br/>A",

    # PDF Export - Chronology
    "DATING": "DATAZIONE",
    "PERIOD OR PHASE": "PERIODO O FASE",
    "Initial period": "Periodo iniziale",
    "Initial phase": "Fase iniziale",
    "Final period": "Periodo finale",
    "Final phase": "Fase finale",
    "ACTIVITY": "ATTIVITÀ",
    "DATING ELEMENTS": "ELEMENTI DATANTI",
    "QUANTITATIVE DATA OF FINDS": "DATI QUANTITATIVI DEI REPERTI",

    # PDF Export - Sampling
    "SAMPLING": "CAMPIONATURE",
    "FLOTATION": "FLOTTAZIONE",
    "SIEVING": "SETACCIATURA",
    "STRATIGRAPHIC RELIABILITY": "AFFIDABILITÀ STRATIGRAFICA",

    # PDF Export - Responsibility
    "SCIENTIFIC SUPERVISOR OF INVESTIGATIONS": "RESPONSABILE SCIENTIFICO DELLE INDAGINI",
    "DATE OF FIELD SURVEY": "DATA RILEVAMENTO SUL CAMPO",
    "DATE OF ELABORATION": "DATA RIELABORAZIONE",
    "RESPONSIBLE ENTITY": "ENTE RESPONSABILE",
    "IDENTIFICATION NUMBER/CODE OF STRATIGRAPHIC TRENCH/BUILDING/STRUCTURE/BURIAL REFERENCE": "NUMERO/CODICE IDENTIFICATIVO DEL SAGGIO STRATIGRAFICO/DELL'EDIFICIO/DELLA STRUTTURA/DELLA DEPOSIZIONE FUNERARIA DI RIFERIMENTO",
    "COMPETENT SUPERINTENDENCE FOR PROTECTION": "SOPRINTENDENZA MIBACT COMPETENTE PER TUTELA",
    "FIELD COMPILATION SUPERVISOR": "RESPONSABILE COMPILAZIONE SUL CAMPO",
    "ELABORATION SUPERVISOR": "RESPONSABILE RIELABORAZIONE",
    "OBSERVATIONS": "OSSERVAZIONI",
    "MATERIAL TABLE REFERENCES": "RIFERIMENTI TABELLE MATERIALI",

    # PDF Export - USM
    "USM sheet generation to be implemented": "Generazione schede USM da implementare",
}


def auto_translate_po_file(po_file_path: Path, lang: str):
    """Auto-translate a .po file based on language"""
    print(f"[Auto-translate] Processing {lang.upper()} file: {po_file_path}")

    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count translations needed
    empty_msgstr_count = content.count('msgstr ""')
    print(f"[Auto-translate] Found {empty_msgstr_count} empty translations")

    # Split into entries
    lines = content.split('\n')
    output_lines = []
    current_msgid = None
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a msgid line
        if line.startswith('msgid "') and not line.startswith('msgid ""'):
            # Extract msgid value
            match = re.match(r'msgid "(.*)"', line)
            if match:
                current_msgid = match.group(1)
            output_lines.append(line)
            i += 1

            # Check next line for msgstr
            if i < len(lines) and lines[i].startswith('msgstr "'):
                msgstr_line = lines[i]

                # If msgstr is empty, fill it
                if msgstr_line == 'msgstr ""' and current_msgid:
                    if lang == 'en':
                        # For English, use the same as msgid
                        output_lines.append(f'msgstr "{current_msgid}"')
                    elif lang == 'it':
                        # For Italian, use translation dictionary
                        translation = IT_TRANSLATIONS.get(current_msgid, current_msgid)
                        output_lines.append(f'msgstr "{translation}"')
                else:
                    output_lines.append(msgstr_line)
                i += 1
            current_msgid = None
        else:
            output_lines.append(line)
            i += 1

    # Write back
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"[Auto-translate] {lang.upper()} file updated successfully!")


if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    translations_dir = base_dir / 'pyarchinit_mini' / 'translations'

    # Auto-translate English
    en_po = translations_dir / 'en' / 'LC_MESSAGES' / 'messages.po'
    auto_translate_po_file(en_po, 'en')

    # Auto-translate Italian
    it_po = translations_dir / 'it' / 'LC_MESSAGES' / 'messages.po'
    auto_translate_po_file(it_po, 'it')

    print("\n[Auto-translate] SUCCESS! Both .po files have been auto-translated.")
    print("[Auto-translate] Next step: Compile with 'pybabel compile'")
