# PyArchInit Blender Addon - Guida Rapida Installazione

**IMPORTANTE:** Se hai installato un addon chiamato "mcp blender" o simile, devi rimuoverlo e installare l'addon corretto "PyArchInit MCP Connector".

---

## Passo 1: Rimuovi addon sbagliato (se presente)

### In Blender:

1. Vai a **Edit → Preferences** (o **Blender → Settings → Preferences** su macOS)
2. Clicca sulla tab **Add-ons**
3. Cerca "mcp" nella barra di ricerca
4. Se vedi un addon che NON si chiama "PyArchInit MCP Connector":
   - Clicca sulla freccia a sinistra per espandere i dettagli
   - Clicca su **Remove** in basso
   - Conferma la rimozione
5. **Riavvia Blender** (importante!)

---

## Passo 2: Installa addon corretto

### File addon:
Il file ZIP si trova in:
```
/Users/enzo/Documents/pyarchinit-mini-desk/docs/pyarchinit_mcp.zip
```

### In Blender:

1. Vai a **Edit → Preferences → Add-ons**
2. Clicca sul pulsante **Install...** in alto a destra
3. Naviga a:
   ```
   /Users/enzo/Documents/pyarchinit-mini-desk/docs/
   ```
4. Seleziona il file **pyarchinit_mcp.zip**
5. Clicca **Install Add-on**

---

## Passo 3: Abilita addon

1. Nella lista addons, cerca "PyArchInit"
2. Dovresti vedere: **"3D View: PyArchInit MCP Connector"**
3. Spunta la checkbox per abilitarlo
4. Verifica che compaia il messaggio: "MCP Server started on 0.0.0.0:9876" nella console di Blender

---

## Passo 4: Avvia server MCP

### Metodo 1: Pannello 3D View (Raccomandato)

1. Apri una **3D Viewport** in Blender
2. Premi il tasto **N** per aprire la sidebar
3. Clicca sulla tab **"PyArchInit"**
4. Clicca il pulsante **"Start Server"**
5. Verifica che lo status dica: **"Server Status: Running"**

### Metodo 2: Blender Console (Debug)

Apri la Python Console in Blender e esegui:
```python
import bpy
bpy.ops.pyarchinit_mcp.start_server()

# Verifica status
props = bpy.context.scene.pyarchinit_mcp_props
print(f"Server running: {props.server_running}")
print(f"Port: {props.server_port}")
```

---

## Passo 5: Testa connessione

### Opzione A: Da terminale

Apri un terminale e esegui:
```bash
cd /Users/enzo/Documents/pyarchinit-mini-desk
python3 /tmp/test_blender_connection.py
```

**Output atteso:**
```
Connecting to localhost:9876...
✓ Connected successfully
Sending: {"type": "get_scene_info", "params": {}}
✓ Command sent
Waiting for response...
✓ Received response: {"status":"success","result":{...}}
✓ Status: success
✓ Result: {'name': 'Scene', 'frame_current': 1, ...}
✓ Test successful!
```

### Opzione B: Dalla web interface

1. Apri browser: http://localhost:5001/3d-builder
2. Clicca sul pulsante **"Test Blender Connection"**
3. Dovresti vedere messaggio verde: **"Connected successfully"**

---

## Troubleshooting

### ❌ "Server won't start"

**Soluzione:**
- Verifica che la porta 9876 non sia già in uso:
  ```bash
  lsof -i :9876
  ```
- Se vedi un processo Blender già attivo, fermalo con:
  ```bash
  # Trova il PID dalla colonna di lsof
  kill <PID>
  ```
- Riavvia Blender

### ❌ "Connection refused"

**Verifiche:**
1. Il server è avviato? Controlla pannello PyArchInit (N → PyArchInit)
2. La porta è corretta? Dovrebbe essere **9876**
3. Firewall attivo? Su macOS:
   - System Preferences → Security & Privacy → Firewall
   - Se attivo, aggiungi Blender alle eccezioni

### ❌ "Timeout waiting for response"

**Questo era il bug fixato!**

Se ancora ottieni timeout:
1. **Disinstalla completamente l'addon:**
   - Edit → Preferences → Add-ons
   - Cerca "PyArchInit"
   - Clicca Remove
   - Riavvia Blender

2. **Reinstalla da zero:**
   - Segui di nuovo i passi 2-4

3. **Verifica versione corretta:**
   - Espandi i dettagli dell'addon
   - Deve dire: **Version: (1, 0, 0)**
   - Author: **PyArchInit Team**

### ❌ "Addon won't enable"

**Soluzioni:**
1. Verifica versione Blender:
   - Deve essere **3.0 o superiore**
   - Help → About Blender

2. Controlla console errori:
   - Window → Toggle System Console (Windows)
   - Controlla messaggi di errore

3. Verifica permessi file:
   ```bash
   # L'addon deve essere leggibile
   ls -l ~/Library/Application\ Support/Blender/3.*/scripts/addons/pyarchinit_mcp/
   ```

---

## Verifica installazione corretta

### Checklist:

- [ ] Addon si chiama **"3D View: PyArchInit MCP Connector"**
- [ ] Addon è **abilitato** (checkbox spuntata)
- [ ] Tab **"PyArchInit"** visibile nella sidebar (tasto N)
- [ ] Pulsante **"Start Server"** presente
- [ ] Server status mostra **"Running"** dopo click
- [ ] Porta impostata a **9876**
- [ ] Test connessione **SUCCESSO** (nessun timeout)

---

## Prossimi passi

Dopo l'installazione corretta:

1. **Testa comandi base:**
   ```bash
   cd /Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini/mcp_server
   python3 blender_client.py --test
   ```

2. **Genera primo modello 3D:**
   - Apri http://localhost:5001/3d-builder
   - Scrivi nel prompt: "Create a simple 3D cube"
   - Clicca "Generate 3D Model"
   - Controlla che il cubo appaia in Blender

3. **Esplora funzionalità:**
   - Leggi: `docs/3D_BUILDER_USER_GUIDE.md`
   - Tutorial completo per l'uso del 3D Builder

---

## Link utili

- **Documentazione completa:** `/Users/enzo/Documents/pyarchinit-mini-desk/docs/3D_BUILDER_USER_GUIDE.md`
- **Documentazione tecnica:** `/Users/enzo/Documents/pyarchinit-mini-desk/docs/3D_BUILDER_TECHNICAL_DOCUMENTATION.md`
- **Addon README:** `/Users/enzo/Documents/pyarchinit-mini-desk/blender_addon/pyarchinit_mcp/README.md`

---

## Supporto

Se continui ad avere problemi:

1. Controlla log Blender:
   - Window → Toggle System Console
   - Cerca errori con "pyarchinit" o "mcp"

2. Verifica file addon:
   ```bash
   unzip -l /Users/enzo/Documents/pyarchinit-mini-desk/docs/pyarchinit_mcp.zip
   ```
   Deve contenere:
   - pyarchinit_mcp/__init__.py
   - pyarchinit_mcp/README.md

3. Testa connessione manuale:
   ```bash
   python3 /tmp/test_blender_connection.py
   ```
   E verifica output dettagliato

---

**Ultima modifica:** 2025-11-01
**Versione addon:** 1.0.0
**Versione Blender richiesta:** 3.0+
