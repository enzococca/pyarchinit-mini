# Integrazione PyArchInit MCP Server con ChatGPT

Guida completa per collegare il server MCP di PyArchInit a ChatGPT Developer Mode per l'accesso diretto ai dati archeologici, stratigrafie e modelli 3D tramite ChatGPT.

## Indice

1. [Prerequisiti](#prerequisiti)
2. [Architettura](#architettura)
3. [Setup Locale (Sviluppo e Testing)](#setup-locale)
4. [Deploy su Cloud (Produzione)](#deploy-su-cloud)
5. [Configurazione ChatGPT](#configurazione-chatgpt)
6. [Testing e Utilizzo](#testing-e-utilizzo)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisiti

### Account ChatGPT
- **Account richiesto**: ChatGPT Plus, Pro, Business, Enterprise o Education
- **Feature richiesta**: Developer Mode (Beta)

### Sistema PyArchInit
- Python 3.8+
- PyArchInit-Mini installato con dipendenze MCP
- Database SQLite configurato

### Networking (per produzione)
- Server pubblicamente accessibile con HTTPS
- Porta 443 aperta (standard HTTPS)
- Dominio o indirizzo IP pubblico

---

## Architettura

```
┌──────────────┐         ┌─────────────────┐         ┌──────────────┐
│   ChatGPT    │  HTTPS  │  PyArchInit MCP │   SQL   │  Database    │
│  (Client)    │ ◄────── │  HTTP Server    │ ◄────── │  SQLite/PG   │
│              │   SSE   │  (FastAPI)      │         │              │
└──────────────┘         └─────────────────┘         └──────────────┘
                                 │
                                 │ MCP Protocol
                                 ▼
                         ┌─────────────────┐
                         │  5 Resources    │
                         │  5 Tools        │
                         │  3 Prompts      │
                         └─────────────────┘
```

### Componenti

**MCP Server HTTP** (`pyarchinit_mini/mcp_server/http_server.py`)
- FastAPI application con endpoint SSE
- Gestione connessioni ChatGPT
- Transport: Server-Sent Events (SSE)

**Endpoint Principali**
- `GET /mcp` - Endpoint SSE per comunicazione MCP
- `POST /mcp/messages` - Endpoint messaggi POST
- `GET /health` - Health check
- `GET /` - Informazioni server

**Risorse MCP** (5 totali)
- GraphML (matrici stratigrafiche)
- US (unità stratigrafiche)
- Periods (periodizzazioni)
- Relationships (relazioni stratigrafiche)
- Sites (siti archeologici)

**Tools MCP** (5 totali)
- `build_3d` - Costruzione modelli 3D
- `filter` - Filtraggio dati
- `export` - Esportazione dati
- `position` - Posizionamento 3D
- `material` - Gestione materiali

**Prompts MCP** (3 totali)
- Stratigraphic Model
- Period Visualization
- US Description

---

## Setup Locale

### Opzione 1: Testing con Ngrok (Semplice)

#### 1. Installa Ngrok

```bash
# macOS
brew install ngrok

# Linux
snap install ngrok

# Windows
choco install ngrok
```

#### 2. Avvia il server MCP

```bash
# Nella directory del progetto
cd /path/to/pyarchinit-mini

# Attiva virtual environment
source .venv/bin/activate  # Linux/macOS
# oppure
.venv\Scripts\activate  # Windows

# Avvia server HTTP/SSE
MCP_TRANSPORT=sse DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" \
python3 -m pyarchinit_mini.mcp_server.http_server

# Oppure usa lo script wrapper
./run-mcp-http.sh
```

#### 3. Crea tunnel Ngrok

```bash
# In un altro terminale
ngrok http 8765
```

Output esempio:
```
Session Status      online
Account            Your Name (Plan: Free)
Version            3.x.x
Region             Europe (eu)
Latency            -
Web Interface      http://127.0.0.1:4040
Forwarding         https://abc123.ngrok.io -> http://localhost:8765
```

#### 4. Usa l'URL HTTPS di Ngrok

Copia l'URL `https://abc123.ngrok.io` per configurarlo in ChatGPT.

**⚠️ IMPORTANTE**: L'URL di Ngrok cambia ad ogni riavvio con il piano Free.

---

### Opzione 2: Cloudflare Tunnel (Persistente)

#### 1. Installa Cloudflare Tunnel

```bash
# macOS
brew install cloudflared

# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

#### 2. Login Cloudflare

```bash
cloudflared tunnel login
```

#### 3. Crea e configura tunnel

```bash
# Crea tunnel
cloudflared tunnel create pyarchinit-mcp

# Crea file di config
cat > ~/.cloudflared/config.yml <<EOF
tunnel: pyarchinit-mcp
credentials-file: /Users/YOUR_USER/.cloudflared/TUNNEL_ID.json

ingress:
  - hostname: pyarchinit-mcp.yourdomain.com
    service: http://localhost:8765
  - service: http_status:404
EOF

# Crea DNS record
cloudflared tunnel route dns pyarchinit-mcp pyarchinit-mcp.yourdomain.com
```

#### 4. Avvia tunnel

```bash
# In background
cloudflared tunnel run pyarchinit-mcp &
```

---

## Deploy su Cloud

### Vercel (Raccomandato per semplicità)

#### 1. Prepara il progetto

```bash
# Crea vercel.json nella root
cat > vercel.json <<EOF
{
  "version": 2,
  "builds": [
    {
      "src": "pyarchinit_mini/mcp_server/http_server.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "pyarchinit_mini/mcp_server/http_server.py"
    }
  ],
  "env": {
    "MCP_TRANSPORT": "sse",
    "DATABASE_URL": "@database_url"
  }
}
EOF
```

#### 2. Deploy

```bash
# Installa Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Deploy produzione
vercel --prod
```

#### 3. Configura variabili

```bash
vercel env add DATABASE_URL production
# Inserisci URL database (es: postgresql://...)
```

---

### Docker (Flessibile)

#### 1. Crea Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copia files
COPY . .

# Installa dipendenze
RUN pip install --no-cache-dir -e .

# Esponi porta
EXPOSE 8765

# Environment variables
ENV MCP_TRANSPORT=sse
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8765

# Avvia server
CMD ["python", "-m", "pyarchinit_mini.mcp_server.http_server"]
```

#### 2. Build e Run

```bash
# Build
docker build -t pyarchinit-mcp .

# Run
docker run -d -p 8765:8765 \
  -e DATABASE_URL="sqlite:///data/pyarchinit.db" \
  pyarchinit-mcp
```

#### 3. Deploy su Cloud

```bash
# Google Cloud Run
gcloud run deploy pyarchinit-mcp \
  --source . \
  --platform managed \
  --region europe-west1

# AWS ECS, Azure Container Instances, etc.
# Segui documentazione specifica del provider
```

---

## Configurazione ChatGPT

### 1. Abilita Developer Mode

#### Per account Plus/Pro:
1. Apri ChatGPT Web
2. Vai su `Settings` (⚙️) → `Apps & Connectors`
3. Scorri fino a `Advanced settings` (in fondo)
4. Attiva `Developer Mode` ✓

#### Per Business/Enterprise/Edu:
1. **Admin** deve prima abilitarlo:
   - `Workspace Settings` → `Permissions & Roles`
   - `Connected Data` → `Developer mode` ✓
2. Poi ogni utente può attivarlo come sopra

### 2. Crea il Connector

1. In ChatGPT, vai su `Settings` → `Connectors`
2. Click `Create` (o `Add custom connector`)
3. Compila i campi:

```yaml
Nome:           PyArchInit MCP
Descrizione:    Server MCP per gestione dati archeologici,
                analisi stratigrafiche e visualizzazione 3D.

                Capabilities:
                - Query e filtro dati stratigrafici
                - Esportazione GraphML e matrici Harris
                - Costruzione modelli 3D da stratigrafie
                - Analisi periodizzazioni e relazioni US
                - Accesso siti e unità stratigrafiche

MCP Server URL: https://YOUR_SERVER.com/mcp
                # Esempio Ngrok: https://abc123.ngrok.io/mcp
                # Esempio Vercel: https://pyarchinit.vercel.app/mcp
                # Esempio Cloudflare: https://pyarchinit-mcp.yourdomain.com/mcp

Authentication: None
                # Oppure: OAuth (se configurato)
```

4. Click `Save` o `Create`

### 3. Testa il Connector

Nella stessa pagina Settings → Connectors, dovresti vedere:
```
✓ PyArchInit MCP
  Connected • Last tested: just now
```

---

## Testing e Utilizzo

### Test Base

Apri una nuova chat in ChatGPT e prova:

```
Usa PyArchInit MCP per mostrarmi tutti i siti archeologici nel database
```

ChatGPT dovrebbe:
1. Rilevare automaticamente il connector
2. Chiamare il tool appropriato
3. Mostrare i risultati formattati

### Esempi Pratici

#### 1. Query Siti

```
Mostrami i siti archeologici disponibili con le loro informazioni principali
```

#### 2. Analisi Stratigrafie

```
Dammi tutte le unità stratigrafiche (US) del sito "Tempio di Fortuna"
e creami una matrice Harris
```

#### 3. Costruzione Modelli 3D

```
Costruisci un modello 3D delle stratigrafie del sito X
usando posizionamento GraphML con spaziatura layer di 0.8 unità
```

#### 4. Esportazione Dati

```
Esporta le US del sito Y in formato GraphML
```

#### 5. Analisi Periodizzazioni

```
Quali sono le periodizzazioni definite per il sito Z?
Creami una visualizzazione cronologica
```

### Modalità Write (Attenzione!)

ChatGPT mostrerà una richiesta di conferma per operazioni write:

```
⚠️ PyArchInit MCP wants to:
   Create US: US_123 in site "Scavo Roma"

   [Cancel] [Approve Once] [Always Approve]
```

**Raccomandazioni**:
- ✅ Usa "Approve Once" per testing
- ❌ Evita "Always Approve" in produzione
- 🔒 Verifica sempre i parametri prima di approvare

---

## Troubleshooting

### Server non si connette

**Problema**: ChatGPT mostra "Connection failed"

**Soluzioni**:
1. Verifica che il server sia in esecuzione:
   ```bash
   curl http://localhost:8765/health
   ```

2. Controlla i log:
   ```bash
   tail -f /tmp/mcp_http.log
   ```

3. Verifica il tunnel (Ngrok/Cloudflare):
   ```bash
   # Ngrok
   curl https://YOUR_NGROK_URL.ngrok.io/health

   # Dovrebbe rispondere:
   # {"status":"healthy","service":"pyarchinit-mcp-server",...}
   ```

4. Controlla firewall/security groups se su cloud

---

### Tools non disponibili

**Problema**: ChatGPT non vede i tools

**Soluzioni**:
1. Verifica inizializzazione MCP:
   ```bash
   grep "Registered.*tools" /tmp/mcp_http.log
   # Dovrebbe mostrare: Registered 5 tools
   ```

2. Testa endpoint direttamente:
   ```bash
   curl -X GET http://localhost:8765/mcp \
     -H "Accept: text/event-stream"
   ```

3. Ricrea il connector in ChatGPT (rimuovi e aggiungi di nuovo)

---

### Errori di autenticazione

**Problema**: "403 Forbidden" o "401 Unauthorized"

**Soluzioni**:
1. Se usi OAuth, verifica token validity
2. Controlla CORS headers nel server
3. Per testing locale, disabilita auth

---

### Performance lenta

**Problema**: Risposte molto lente

**Ottimizzazioni**:
1. Usa database cache (Redis)
2. Ottimizza query SQL
3. Abilita CDN per risorse statiche
4. Scala verticalmente/orizzontalmente su cloud

---

## Risorse Aggiuntive

### Documentazione
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [OpenAI MCP Integration](https://developers.openai.com/apps-sdk/concepts/mcp-server/)
- [FastMCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### Tools di Debug
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) - Debug locale
- Ngrok Dashboard: `http://localhost:4040` - Ispeziona richieste HTTP
- FastAPI Docs: `http://localhost:8765/docs` - API documentation interattiva

### Community
- [MCP Discord](https://discord.gg/modelcontextprotocol)
- [OpenAI Developer Forum](https://community.openai.com/)
- [PyArchInit GitHub](https://github.com/enzococca/pyarchinit-mini)

---

## Note di Sicurezza

### ⚠️ IMPORTANTE per Produzione

1. **Abilita HTTPS**: Mai usare HTTP in produzione
2. **Autentica Richieste**: Implementa OAuth 2.1
3. **Rate Limiting**: Limita richieste per IP/token
4. **Input Validation**: Valida tutti gli input utente
5. **Logging**: Monitora accessi e operazioni write
6. **Backup Database**: Backup automatici regolari
7. **Secrets Management**: Usa secret manager (AWS Secrets, Azure Key Vault, etc.)
8. **Network Security**: Firewall, VPC, security groups

### Esempio OAuth Setup

```python
# pyarchinit_mini/mcp_server/http_server.py

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/mcp", dependencies=[Depends(verify_token)])
async def mcp_endpoint(...):
    ...
```

---

## Supporto

Per assistenza:
- 📧 Email: enzo.ccc@gmail.com
- 🐛 Issues: https://github.com/enzococca/pyarchinit-mini/issues
- 📖 Docs: https://github.com/enzococca/pyarchinit-mini/blob/main/README.md

---

**Ultima modifica**: Novembre 2025
**Versione Server MCP**: 1.9.0.dev0
**Compatibilità ChatGPT**: Developer Mode (Beta) - Nov 2025
