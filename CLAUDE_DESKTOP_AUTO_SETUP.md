# Configurazione Automatica di Claude Desktop

PyArchInit-Mini include uno script per configurare automaticamente Claude Desktop con il server MCP (Model Context Protocol).

## Cosa fa lo script

Lo script `pyarchinit-mini-configure-claude` automatizza la configurazione di Claude Desktop:

1. ✅ **Verifica** se Claude Desktop è installato
2. ✅ **Controlla** se `uvx` è installato
3. ✅ **Legge** la configurazione esistente di Claude Desktop
4. ✅ **Aggiunge** la configurazione MCP per PyArchInit-Mini
5. ✅ **Preserva** le configurazioni esistenti (Blender, Memory, Puppeteer, ecc.)
6. ✅ **Crea backup** del file di configurazione prima di modificarlo

## Installazione

### Passo 1: Installa PyArchInit-Mini

```bash
pip install pyarchinit-mini
```

### Passo 2: Configura Claude Desktop

```bash
pyarchinit-mini-configure-claude
```

### Output esempio:

```
======================================================================
Configurazione Claude Desktop per PyArchInit-Mini MCP
======================================================================

1. Controllo installazione Claude Desktop...
  ✓ Claude Desktop installato

2. Controllo installazione uvx...
  ✓ uvx installato

3. Configurazione file di config...
  • File di config: /Users/utente/Library/Application Support/Claude/claude_desktop_config.json
  ✓ Backup creato: /Users/utente/Library/Application Support/Claude/claude_desktop_config.json.backup
  ✓ Configurazione salvata

======================================================================
✓ Configurazione completata con successo!
======================================================================

Configurazione aggiunta:
  {
    "mcpServers": {
      "pyarchinit": {
        "command": "uvx",
        "args": ["--from", "pyarchinit-mini", "pyarchinit-mini-mcp"]
      }
    }
  }

Prossimi passi:
  1. Riavvia Claude Desktop
  2. Apri una nuova conversazione
  3. PyArchInit-Mini MCP sarà disponibile automaticamente
```

## Esempio di configurazione finale

Lo script inserisce la configurazione nel file esistente mantenendo tutte le altre configurazioni:

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    },
    "memory": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-memory"],
      "env": {}
    },
    "puppeteer": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-puppeteer"],
      "env": {}
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://localhost/pyarchinit"
      ]
    },
    "pyarchinit": {
      "command": "uvx",
      "args": ["--from", "pyarchinit-mini", "pyarchinit-mini-mcp"]
    }
  }
}
```

## Comandi disponibili in Claude

Dopo la configurazione, puoi usare Claude per interagire con PyArchInit-Mini:

### Gestione Database

```
- get_schema: Visualizza schema del database
- insert_data: Inserisci nuovi record
- update_data: Aggiorna record esistenti
- delete_data: Elimina record
- resolve_conflicts: Gestisci conflitti (UPSERT)
```

### Gestione Servizi

```
- manage_service: Gestisci servizi PyArchInit
  * Avvia/ferma web interface (porta 5001)
  * Avvia/ferma API server (porta 8000)
  * Avvia/ferma Desktop GUI
  * Controlla stato servizi
```

### Harris Matrix e Stratigrafia

```
- create_harris_matrix: Genera matrice Harris
- validate_stratigraphy: Valida stratigrafia
- filter_by_period: Filtra per periodo
```

### Export e Import

```
- export_data: Esporta dati in vari formati
- import_excel: Importa da Excel
- sync_pyarchinit: Sincronizza con PyArchInit
```

### 3D e Visualizzazione

```
- build_3d: Costruisci modello 3D da stratigrafia
- configure_em_nodes: Configura nodi Extended Matrix
```

## Esempio di utilizzo in Claude

Puoi chiedere a Claude di:

### 1. Avviare l'interfaccia web

```
"Avvia l'interfaccia web di PyArchInit-Mini"
```

Claude userà il tool `manage_service` con parametri:
- action: "start"
- service: "web"

### 2. Inserire dati

```
"Crea un nuovo sito archeologico chiamato 'Tempio di Palestrina'
 in Italia, regione Lazio"
```

Claude userà il tool `insert_data` con i dati appropriati.

### 3. Generare Harris Matrix

```
"Genera la matrice Harris per il sito 'Tempio' raggruppando per periodo"
```

Claude userà il tool `create_harris_matrix`.

## Requisiti

- **Claude Desktop**: [Scarica qui](https://claude.ai/download)
- **uvx**: Installabile via `pip install uv`
- **PyArchInit-Mini**: Installabile via `pip install pyarchinit-mini`

### Installazione uvx

**Opzione 1: Via pip**
```bash
pip install uv
```

**Opzione 2: Via installer (macOS/Linux)**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Opzione 3: Via Homebrew (macOS)**
```bash
brew install uv
```

## Path del file di configurazione

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Linux
```
~/.config/Claude/claude_desktop_config.json
```

## Opzioni avanzate

### Modalità silenziosa
```bash
pyarchinit-mini-configure-claude --silent
```

### Forza sovrascrittura
```bash
pyarchinit-mini-configure-claude --force
```

## Troubleshooting

### Claude Desktop non trovato
Se lo script non trova Claude Desktop:
1. Verifica che Claude Desktop sia installato
2. Controlla che la directory di configurazione esista
3. Scarica Claude Desktop da https://claude.ai/download

### uvx non trovato
Se `uvx` non è installato:
```bash
# Installa uv (include uvx)
pip install uv

# Verifica installazione
uvx --version
```

### Configurazione non caricata
Se Claude non vede i tool PyArchInit:
1. Riavvia completamente Claude Desktop
2. Apri una nuova conversazione
3. Verifica il file di config manualmente
4. Controlla i log di Claude Desktop

### Backup e ripristino

Lo script crea automaticamente un backup prima di modificare il file:
```
claude_desktop_config.json.backup
```

Per ripristinare:
```bash
cd ~/Library/Application\ Support/Claude/
cp claude_desktop_config.json.backup claude_desktop_config.json
```

## Integrazione con MCP

PyArchInit-Mini supporta il Model Context Protocol (MCP) tramite:

1. **MCP Server STDIO** (raccomandato per Claude Desktop):
   - Avviato automaticamente da Claude
   - Configurazione via `uvx`

2. **MCP HTTP Server** (per integrazioni custom):
   ```bash
   pyarchinit-mini-mcp-http
   ```

## Prossimi passi

Dopo la configurazione:

1. ✅ Riavvia Claude Desktop
2. ✅ Apri una nuova conversazione
3. ✅ Chiedi a Claude di aiutarti con PyArchInit-Mini
4. ✅ Esplora i tool disponibili

## Esempio di conversazione

```
User: Puoi aiutarmi a gestire il mio database archeologico?

Claude: Certo! Ho accesso a PyArchInit-Mini tramite MCP.
        Posso aiutarti con:
        - Gestione siti, US e materiali
        - Creazione matrici Harris
        - Validazione stratigrafica
        - Export e import dati
        - Avvio servizi (web, API, GUI)

        Cosa vuoi fare?

User: Avvia l'interfaccia web

Claude: [Usa manage_service tool]
        ✓ Interfaccia web avviata su http://localhost:5001
```

## Supporto

Per problemi o domande:
- GitHub Issues: https://github.com/enzococca/pyarchinit-mini/issues
- Email: enzo.ccc@gmail.com

## License

GPL-2.0
