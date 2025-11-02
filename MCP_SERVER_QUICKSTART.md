# PyArchInit MCP Server - Quick Start

## Server HTTP/SSE per ChatGPT Integration

### Stato del Server

Il server MCP HTTP è **operativo e funzionante**:

✅ Server running su `http://localhost:8765`
✅ 5 Resources disponibili (graphml, us, periods, relationships, sites)
✅ 5 Tools disponibili (build_3d, filter, export, position, material)
✅ 3 Prompts disponibili
✅ Endpoint SSE per ChatGPT: `http://localhost:8765/mcp`

### Come Avviare il Server

#### Opzione 1: Script Wrapper (Raccomandato)

```bash
cd /Users/enzo/Documents/pyarchinit-mini-desk
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" ./run-mcp-http.sh
```

#### Opzione 2: Modulo Python diretto

```bash
cd /Users/enzo/Documents/pyarchinit-mini-desk
MCP_TRANSPORT=sse DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" \
.venv/bin/python3 -m pyarchinit_mini.mcp_server.http_server
```

### Verifica Server

```bash
# Health check
curl http://localhost:8765/health

# Capabilities auto-discovery
curl http://localhost:8765/capabilities

# Root endpoint
curl http://localhost:8765/
```

### Prossimi Passi per ChatGPT Integration

1. **Esposizione Pubblica** (scegli un metodo):
   - Ngrok: `ngrok http 8765`
   - Cloudflare Tunnel (vedi CHATGPT_MCP_SETUP.md)
   - Deploy Cloud (Vercel, Docker, etc.)

2. **Configurazione ChatGPT**:
   - Apri ChatGPT Settings → Connectors
   - Aggiungi nuovo connector MCP
   - URL: `https://YOUR_PUBLIC_URL/mcp`
   - Nome: "PyArchInit MCP"
   - Descrizione: "Server MCP per gestione dati archeologici e 3D"

3. **Test** in ChatGPT:
   ```
   Mostrami tutti i siti archeologici nel database PyArchInit
   ```

### Risoluzione Problemi

#### Console Script `pyarchinit-mcp-http` Non Funziona

Il comando `pyarchinit-mcp-http` installato tramite pip ha un problema di import.
**Soluzione**: Usa lo script wrapper `./run-mcp-http.sh` o il comando modulo diretto.

Questo è un problema noto con editable install in venv con symlink a conda.
Il server funziona perfettamente tramite modulo Python.

### File Importanti

- `CHATGPT_MCP_SETUP.md` - Guida completa integrazione ChatGPT
- `run-mcp-http.sh` - Script wrapper per avviare il server
- `pyarchinit_mini/mcp_server/http_server.py` - Implementazione server HTTP/SSE

### Supporto

Per dettagli completi e troubleshooting, consulta `CHATGPT_MCP_SETUP.md`.
