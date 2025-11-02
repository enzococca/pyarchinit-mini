# PyArchInit Real-Time Blender Streaming - Setup Completo

## Architettura Implementata

```
Claude AI (con blender-mcp)
    ↓
Blender + PyArchInit Real-Time Streamer Addon
    ↓ (WebSocket - Port 5001)
PyArchInit Flask Server (SocketIO)
    ↓ (WebSocket broadcast)
Web Viewer (Browser - ThreeJS)
```

## Componenti Implementati

### 1. ✅ WebSocket Server (Backend)
**File**: `pyarchinit_mini/web_interface/socketio_events.py`

Eventi implementati:
- `blender_connect` - Connessione iniziale da Blender
- `blender_disconnect` - Disconnessione Blender
- `blender_scene_update` - Aggiornamento completo scena
- `blender_object_created` - Creazione nuovo oggetto
- `blender_object_updated` - Modifica oggetto esistente
- `blender_object_deleted` - Cancellazione oggetto
- `blender_material_updated` - Aggiornamento materiali
- `blender_camera_update` - Movimento camera
- `blender_build_progress` - Progress da agenti Claude AI

**File**: `pyarchinit_mini/web_interface/app.py`
- Registrato `init_blender_socketio_events(socketio)` nella linea 513

### 2. ✅ Blender Addon
**File**: `blender_addons/pyarchinit_realtime_streamer.py`

Funzionalità:
- Connessione automatica a WebSocket PyArchInit
- Monitoring automatico di tutte le modifiche (depsgraph)
- Broadcast in tempo reale di:
  - Trasformazioni (location, rotation, scale)
  - Modifiche geometria
  - Creazione/cancellazione oggetti
  - Modifiche materiali
- UI panel in 3D View sidebar (N → PyArchInit)

**Installazione Addon**:
1. Apri Blender
2. Edit → Preferences → Add-ons → Install
3. Seleziona `blender_addons/pyarchinit_realtime_streamer.py`
4. Abilita "PyArchInit Real-Time Streamer"
5. Configura URL WebSocket (default: http://localhost:5001)

**Dipendenze Python per Blender**:
```bash
# Installa python-socketio nel Python di Blender
/Applications/Blender.app/Contents/Resources/4.2/python/bin/python3.11 -m pip install python-socketio[client]
```

### 3. ✅ Claude AI Prompts
**Directory**: `output/3d_generation/`

File generati per Tempio Fortuna:
- `Tempio_Fortuna_data.json` - Dati archeologici completi (28 unità)
- `Tempio_Fortuna_prompt.md` - Prompt principale per ricostruzione
- `Tempio_Fortuna_agent_architect.md` - Agente Architetto
- `Tempio_Fortuna_agent_validator.md` - Agente Validatore
- `Tempio_Fortuna_agent_texturizer.md` - Agente Texturizzatore
- `Tempio_Fortuna_agent_reconstructor.md` - Agente Ricostruttore

**Generare prompt per altri siti**:
```bash
# Lista siti disponibili
python3 scripts/generate_3d_with_claude.py --list

# Genera prompt per sito specifico
python3 scripts/generate_3d_with_claude.py --site "Nome Sito"

# Modalità interattiva
python3 scripts/generate_3d_with_claude.py
```

### 4. 🔧 Web Viewer (TODO - In Progress)
**File da aggiornare**: `pyarchinit_mini/web_interface/templates/3d_builder/index.html`

**Modifiche necessarie**:
1. Aggiungere SocketIO client nel template
2. Listener per eventi Blender
3. Aggiornamento scena ThreeJS in real-time

**Codice da aggiungere** (prima di `</body>`):

```html
<!-- Socket.IO Client -->
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script>
// Real-time Blender connection
const socket = io();
let blenderConnected = false;

// Connection events
socket.on('blender_connected', (data) => {
    blenderConnected = true;
    console.log('[Blender] Connected:', data.blender_version);
    showNotification('Blender connected!', 'success');
});

socket.on('blender_disconnected', () => {
    blenderConnected = false;
    console.log('[Blender] Disconnected');
    showNotification('Blender disconnected', 'warning');
});

// Scene updates
socket.on('blender_scene_update', (data) => {
    console.log('[Blender] Scene update:', data);
    // TODO: Update ThreeJS scene with all objects
    updateSceneFromBlender(data);
});

socket.on('blender_object_created', (data) => {
    console.log('[Blender] Object created:', data.object_name);
    // TODO: Create new mesh in ThreeJS
    createProxyFromBlender(data);
});

socket.on('blender_object_updated', (data) => {
    console.log('[Blender] Object updated:', data.object_name);
    // TODO: Update existing mesh in ThreeJS
    updateProxyFromBlender(data);
});

socket.on('blender_object_deleted', (data) => {
    console.log('[Blender] Object deleted:', data.object_name);
    // TODO: Remove mesh from ThreeJS
    deleteProxyFromBlender(data);
});

socket.on('blender_build_progress', (data) => {
    console.log(`[Blender Build] ${data.message} (${data.percentage}%)`);
    updateBuildProgress(data);
});

// Helper functions
function updateSceneFromBlender(sceneData) {
    // Clear current scene
    clearProxies();

    // Rebuild from Blender data
    sceneData.objects.forEach(obj => {
        createProxyFromBlender(obj);
    });
}

function createProxyFromBlender(objData) {
    const geometry = new THREE.BoxGeometry(
        objData.scale[0],
        objData.scale[1],
        objData.scale[2]
    );

    const material = new THREE.MeshPhongMaterial({
        color: objData.material ?
            new THREE.Color(
                objData.material.base_color[0],
                objData.material.base_color[1],
                objData.material.base_color[2]
            ) : 0x808080,
        roughness: objData.material?.roughness || 0.7,
        metalness: objData.material?.metallic || 0
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(...objData.location);
    mesh.rotation.set(...objData.rotation);
    mesh.name = objData.object_name;
    mesh.userData.proxy_id = objData.proxy_id;

    scene.add(mesh);
}

function updateProxyFromBlender(updateData) {
    const mesh = scene.getObjectByName(updateData.object_name);
    if (!mesh) return;

    if (updateData.new_values.location) {
        mesh.position.set(...updateData.new_values.location);
    }
    if (updateData.new_values.rotation) {
        mesh.rotation.set(...updateData.new_values.rotation);
    }
    if (updateData.new_values.scale) {
        mesh.scale.set(...updateData.new_values.scale);
    }
}

function deleteProxyFromBlender(data) {
    const mesh = scene.getObjectByName(data.object_name);
    if (mesh) {
        scene.remove(mesh);
        mesh.geometry.dispose();
        mesh.material.dispose();
    }
}

function showNotification(message, type) {
    // TODO: Implement notification UI
    console.log(`[${type.toUpperCase()}] ${message}`);
}

function updateBuildProgress(data) {
    // TODO: Show progress bar
    const progressBar = document.getElementById('build-progress');
    if (progressBar) {
        progressBar.style.width = `${data.percentage}%`;
        progressBar.textContent = data.message;
    }
}
</script>
```

## Workflow Completo

### Scenario 1: Ricostruzione Manuale in Blender

1. **Avvia PyArchInit Server**:
   ```bash
   DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" python3 -m pyarchinit_mini.web_interface.app
   ```

2. **Apri Blender** e installa l'addon

3. **Connetti Blender a PyArchInit**:
   - Premi N → PyArchInit tab
   - Click "Connect to PyArchInit"
   - Verifica connessione (status: Connected)

4. **Apri Web Viewer**:
   - Browser: http://localhost:5001/3d-builder
   - Seleziona sito "Tempio Fortuna"

5. **Modifica in Blender**:
   - Qualsiasi modifica viene streamata automaticamente
   - Il viewer si aggiorna in tempo reale

### Scenario 2: Ricostruzione con Claude AI + blender-mcp

1. **Setup blender-mcp**:
   - Installa blender-mcp: https://github.com/VertexStudio/blender-mcp
   - Configura in Claude Desktop/Cursor

2. **Avvia tutti i servizi**:
   ```bash
   # PyArchInit Server
   DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" python3 -m pyarchinit_mini.web_interface.app

   # Blender con addon installato e connesso
   ```

3. **Usa Claude AI per generare 3D**:
   ```
   Prompt: "Usa il prompt in output/3d_generation/Tempio_Fortuna_prompt.md
   per creare la ricostruzione 3D del Tempio della Fortuna in Blender."
   ```

4. **Claude AI workflow**:
   - Legge i dati archeologici (28 unità, dimensioni esatte)
   - Usa agente Architetto per creare base
   - Usa agente Validatore per verificare dimensioni
   - Usa agente Texturizzatore per materiali realistici
   - Usa agente Ricostruttore per parti virtuali
   - Ogni modifica viene streamata al viewer in tempo reale

5. **Osserva nel viewer**:
   - Vedi la ricostruzione prendere forma in tempo reale
   - Progress bar mostra avanzamento agenti
   - Ogni oggetto appare con dimensioni e materiali corretti

## Testing

### Test 1: WebSocket Server
```bash
# Terminal 1: Avvia server
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" python3 -m pyarchinit_mini.web_interface.app

# Verifica log:
# [PyArchInit] WebSocket server running on port 5001
```

### Test 2: Blender Addon
1. Apri Blender
2. Verifica addon installato e abilitato
3. Premi N → PyArchInit
4. Click "Connect to PyArchInit"
5. Verifica nel terminale PyArchInit:
   ```
   [Blender WebSocket] Blender connected: 4.2.0 (SID: xyz123)
   ```

### Test 3: Modifica Oggetto
1. In Blender, aggiungi un cubo (Shift+A → Mesh → Cube)
2. Muovi il cubo (G)
3. Verifica nel terminale PyArchInit:
   ```
   [Blender Stream] Object created: Cube
   [Blender Stream] Object updated: Cube
   ```

### Test 4: Prompt Claude AI
```bash
# Genera prompt
python3 scripts/generate_3d_with_claude.py --site "Tempio Fortuna"

# Verifica file creati:
ls -l output/3d_generation/
```

## Risoluzione Problemi

### Blender non si connette
```bash
# Verifica dipendenze Python Blender
/Applications/Blender.app/Contents/Resources/4.2/python/bin/python3.11 -m pip install python-socketio[client]

# Verifica URL nelle preferenze addon (deve essere http://localhost:5001)
```

### WebSocket errors
```bash
# Verifica Flask-SocketIO installato
pip install flask-socketio python-socketio

# Riavvia server con log verbose
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" FLASK_DEBUG=1 python3 -m pyarchinit_mini.web_interface.app
```

### Oggetti sovrapposti in Blender
**RISOLTO**: Usa i prompt Claude AI con agenti specializzati invece di generazione semplice di cubi.

## Prossimi Passi

1. ✅ WebSocket server - COMPLETATO
2. ✅ Blender addon - COMPLETATO
3. ✅ Claude AI prompts - COMPLETATO
4. 🔧 Web viewer integration - IN PROGRESS (codice fornito sopra)
5. 🔧 Testing end-to-end
6. 🔧 Ottimizzazione performance viewer
7. 🔧 Fix proxy info panel on click
8. 🔧 Documentazione video tutorial

## Note Tecniche

- **Port**: WebSocket usa porta 5001 (stesso del Flask server)
- **CORS**: Abilitato (`cors_allowed_origins="*"`)
- **Reconnection**: Auto-reconnect abilitato (5 tentativi)
- **Event rate**: Blender depsgraph può generare molti eventi, considerare throttling se necessario
- **Performance**: Eventi `blender_object_updated` sono commentati come verbose per evitare flood di log

## Crediti

- Blender MCP: https://github.com/VertexStudio/blender-mcp
- Flask-SocketIO: https://flask-socketio.readthedocs.io/
- ThreeJS: https://threejs.org/
