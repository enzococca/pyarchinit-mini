# Spec 9 — Harris Matrix orthogonal edges + spacing tuning

> **Status:** Brainstormed, ready for implementation plan
> **Target version:** `pyarchinit-mini` 2.5.1 → 2.6.0
> **Author:** Enzo + Claude Opus 4.7
> **Date:** 2026-05-18

## 1. Goal

Far renderizzare gli edge stratigrafici del Harris Matrix Creator con percorsi
**ortogonali a 90°** (right-angle routing), come nel formato yEd PolyLineEdge
usato da pyarchinit QGIS plugin (riferimento: file
`Extended_Matrix_test_1.graphml`). Lo stato attuale è curve bezier diagonali
— non assomiglia al Harris matrix tradizionale.

In aggiunta: aumentare leggermente lo spacing (v_gap, h_gap) del layout
server-side `harris_layout.py` per evitare che gli edge orthogonal si
sovrappongano fra rank adiacenti.

## 2. Non-goals (YAGNI)

- Custom segments con bend-points calcolati lato client.
- Toggle "bezier vs taxi" nel toolbar.
- Riscrivere `harris_layout` per ottimizzazioni di crossing-minimization.
- Spec 10 (AI matrix import da immagine/disegno → US) — separato.

## 3. Architecture

```
┌─────────────────────────────────────────────────────┐
│  Browser editor.html (no change to template)        │
│  ┌───────────────────────────────────────────────┐  │
│  │ harris_creator_editor.js (Cytoscape style):  │  │
│  │   curve-style: 'taxi'                         │  │
│  │   taxi-direction: 'vertical'                  │  │
│  │   taxi-turn: 'auto'                           │  │
│  │   target-arrow-shape: 'triangle'              │  │
│  └───────────────────────────────────────────────┘  │
└──────────┬──────────────────────────────────────────┘
           │  positions from /api/load (server)
           ▼
   ┌─────────────────────────────────┐
   │ pyarchinit_mini/harris_swimlane/│
   │ harris_layout.py (defaults)     │
   │   v_gap: 20 → 40                │
   │   h_gap: 30 → 50                │
   │   node_h, node_w: unchanged     │
   └─────────────────────────────────┘
```

### Confini

- **Frontend**: 1 file (`harris_creator_editor.js`) — 3 nuove proprietà nel
  selettore `edge` del block stile Cytoscape esistente.
- **Backend**: 1 file (`harris_layout.py`) — solo cambio dei 2 default
  numerici (`v_gap`, `h_gap`).
- **Niente nuove routes / nuove tabelle DB / nuove migration**.
- **Niente cambio al pattern dei nodi** — il taxi style funziona con i nodi
  già posizionati da `compute_harris_positions`.

## 4. Components

### 4.1 `pyarchinit_mini/web_interface/static/js/harris_creator_editor.js`

Locate the existing edge stylesheet block (search for
`selector: 'edge'` near line 261-280). The current style:

```javascript
{
    selector: 'edge',
    style: {
        'width': 2,
        'line-color': '#666',
        'target-arrow-color': '#666',
        'target-arrow-shape': 'triangle',
    }
},
```

Replace with:

```javascript
{
    selector: 'edge',
    style: {
        'width': 2,
        'line-color': '#666',
        'target-arrow-color': '#666',
        'target-arrow-shape': 'triangle',
        // Spec 9: orthogonal routing (matches yEd PolyLineEdge)
        'curve-style': 'taxi',
        'taxi-direction': 'vertical',
        'taxi-turn': 'auto',
    }
},
```

Le altre selector override (`edge:selected`, `edge[style="dashed"]`,
`edge[edgeCategory="negative"]`, ecc) restano invariati — eridtano il
`curve-style: 'taxi'` perché Cytoscape applica gli stili cascade.

### 4.2 `pyarchinit_mini/harris_swimlane/harris_layout.py`

Modify the `compute_harris_positions` function signature defaults:

```python
def compute_harris_positions(
    nodes: list[dict],
    edges: list[dict],
    *,
    lane_id_for: Callable[[dict], str],
    lane_widths: dict[str, int],
    node_w: int = 80,
    node_h: int = 30,
    h_gap: int = 50,    # was 30
    v_gap: int = 40,    # was 20
) -> dict[str, tuple[float, float]]:
```

No logic changes — only the two integer defaults.

## 5. Data flow

```
GET /harris-creator/api/load/<site>
   ↓
SwimlaneState.load(...) → compute_harris_positions(...)
   ↓ (uses new larger defaults)
{node_id: (x, y)} positions
   ↓ JSON response
Browser: renderSwimlaneState(state)
   ↓
Cytoscape places nodes at (x, y) + applies taxi style on edges
   ↓
User sees right-angle Harris matrix
```

## 6. Error handling

Nessun nuovo error path. `curve-style: 'taxi'` è una proprietà nativa di
Cytoscape — sempre supportata dalla versione caricata (3.26.0). I default
numerici non cambiano la firma né lanciano errori.

## 7. Testing

| Layer | Test | Strategia |
|---|---|---|
| Unit | `compute_harris_positions` default v_gap=40 | `inspect.signature(...).parameters['v_gap'].default == 40` |
| Unit | `compute_harris_positions` default h_gap=50 | idem per h_gap |
| Regression | 8 test esistenti di `test_harris_layout.py` | Devono restare verdi (test passano args espliciti, non dipendono dai default) |
| Manual smoke | Aprire `/harris-creator/editor?site=<existing>` in browser | Edge devono apparire ortogonali (90°) |

## 8. Definition of Done

### Backend
- [ ] `harris_layout.py` defaults `v_gap=40, h_gap=50`
- [ ] 2 nuovi test sui default (firma)
- [ ] 8 test esistenti restano verdi

### Frontend
- [ ] `harris_creator_editor.js` selettore `edge` ha 3 nuove proprietà:
  `curve-style: 'taxi'`, `taxi-direction: 'vertical'`, `taxi-turn: 'auto'`
- [ ] Smoke browser: edge ortogonali visibili

### Release
- [ ] Bump 2.5.1 → 2.6.0 (minor — visible UI behavior change)
- [ ] CHANGELOG entry IT+EN

## 9. Backwards compat

- API Python: i chiamanti che passano `v_gap` / `h_gap` espliciti sono
  intatti. Solo i default cambiano.
- Cytoscape: i selector override esistenti (`edge:selected`, etc) ereditano
  il nuovo `curve-style`. Nessuno smette di funzionare.
- yEd export: invariato. Il file Extended Matrix esportato resta uguale
  byte-per-byte (gli x/y dei nodi cambiano con i nuovi defaults, ma quello
  è già un effetto desiderato — più spazio = miglior leggibilità anche in
  yEd Desktop).

## 10. Riferimenti

- Spec 7 — `harris_swimlane/harris_layout.py` (compute_harris_positions)
- Spec 7 — `swimlane_state.py` chiama `compute_harris_positions` con args
  espliciti `lane_id_for=lambda n: n["lane"], lane_widths={...}` ma NON
  override di `v_gap`/`h_gap` → riceve i nuovi defaults automaticamente.
- Cytoscape 3.26 — `curve-style: 'taxi'` docs:
  https://js.cytoscape.org/#style/taxi-edges
- pyarchinit reference: `Extended_Matrix_test_1.graphml` usa
  `y:PolyLineEdge` con bends orthogonal.
- Roadmap successiva: **Spec 10 — AI matrix import** (separato, non in
  questo spec): caricare immagine/disegno di un Harris matrix e popolare
  `us_table` + `us_relationships_table` via Claude/OpenAI Vision API.
