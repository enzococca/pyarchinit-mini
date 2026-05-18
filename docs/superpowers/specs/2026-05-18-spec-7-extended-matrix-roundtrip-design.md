# Spec 7 — Extended Matrix Round-Trip (layout + yEd export + import)

> **Status:** Brainstormed, ready for implementation plan
> **Target version:** `pyarchinit-mini` 2.4.8 → 2.5.0
> **Author:** Enzo + Claude Opus 4.7
> **Date:** 2026-05-18

## 1. Goal

Allineare pyarchinit-mini-web al template pyarchinit Extended Matrix (file di
riferimento: `Extended_Matrix_test_1.graphml`) su tre piani:

1. **Layout editor** — lane verticali (rows del TableNode) con Harris-classico
   interno (US distribuiti per dipendenze stratigrafiche, recent in alto).
2. **Export yEd GraphML** — file byte-compatibile con pyarchinit QGIS plugin:
   `y:TableNode configuration="YED_TABLE_NODE"`, keys `d0..d37`, payload
   `pyarchinit.*` su ogni nodo, `pyarchinit.epochs_meta` graph-level.
3. **Import yEd GraphML** — leggere lo stesso file e popolare/aggiornare
   `us_table`, `site_table`, `periodizzazione_table` con preview 2-fasi e
   upsert by `node_uuid`.

Risultato: un file Extended Matrix esportato da pyarchinit-mini si apre senza
modifiche in yEd Desktop e in pyarchinit QGIS, e re-importato in
pyarchinit-mini è idempotente.

## 2. Non-goals (YAGNI)

- GroupNode EM nested (struttura/attivita come compound interni alle lane) —
  Spec 5 separato.
- AI-driven matrix import da foto/disegno — Spec 8 separato.
- Real-time multi-user editing (SyncEngine) — Spec 3, on hold.
- Round-trip dei paradata standalone (AuthorNode, LicenseNode) — Spec 3-ter.

## 3. Architecture

```
                              Browser
              ┌─────────────────────────────────────┐
              │  /harris-creator/editor?site=X      │
              │  ┌───────────────────────────────┐  │
              │  │ Toolbar: Group by ▼  Save     │  │
              │  │   period_phase | struttura |   │  │
              │  │   attivita | settore | area |  │  │
              │  │   ambient | saggio | quad_par |│  │
              │  │   none                         │  │
              │  ├───────────────────────────────┤  │
              │  │ Cytoscape compound:           │  │
              │  │   lane verticali per group_by │  │
              │  │   Harris-classico INTERNO     │  │
              │  └───────────────────────────────┘  │
              │  /import-graphml/   (nuova pagina)  │
              └────┬─────────────────────────────┬──┘
            ┌─ GET /api/load/<site>?group_by=X   POST /import-graphml/preview+apply
            │     │                            │
            ▼     ▼                            ▼
         ┌──────────────────────────┐    ┌──────────────────────┐
         │ harris_creator_routes    │    │ yed_import_routes    │
         │ (Spec 3-bis + group_by)  │    │  (nuovo blueprint)   │
         └──┬─────────────┬─────────┘    └────────┬─────────────┘
            ▼             ▼                       ▼
   ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
   │ swimlane_state  │  │ yed_writer.py    │  │ yed_importer.py      │
   │ (esteso         │  │ (RISCRITTO byte- │  │ (NUOVO)              │
   │  group_by +     │  │  compat pyarch.  │  │  parse y:TableNode + │
   │  harris_layout) │  │  YED_TABLE_NODE  │  │  pyarchinit.* keys → │
   │                 │  │  d0..d37 keys)   │  │  preview/apply DTOs  │
   └─────────────────┘  └──────────────────┘  └────────┬─────────────┘
                                                       ▼
                                      ┌────────────────────────────┐
                                      │ us_table, site_table,      │
                                      │ periodizzazione_table,     │
                                      │ us_relationships_table     │
                                      │ (upsert by node_uuid)      │
                                      └────────────────────────────┘
```

### Confini

- **Editor (frontend)**: dropdown "Group by" carica
  `/api/load/<site>?group_by=X`. Per ogni lane, Cytoscape riceve posizioni
  pre-calcolate da `harris_layout` server-side — niente re-layout client.
- **`yed_writer.py` (riscritto)**: emette
  `<y:TableNode configuration="YED_TABLE_NODE">` con righe (`y:Row id="row_N"`)
  basate su `group_by`. Tutte le 38 keys `d0..d37` valorizzate (anche vuote).
  Output byte-compat con pyarchinit QGIS.
- **`yed_importer.py` (nuovo)**: legge il file Extended_Matrix, estrae nodi
  US + epochs_meta + relazioni, produce un `ImportPlan` (riusa pattern Spec 2
  `GraphIngestor`). Upsert by `node_uuid`, 2 fasi (preview/apply).
- **Pagina `/import-graphml`**: upload form + preview tabellare + bottone Apply.

## 4. Components

### 4.1 `pyarchinit_mini/harris_swimlane/swimlane_state.py` (extended)

Firma nuova:

```python
@staticmethod
def load(
    session: Session, site: str, *, group_by: str = "period_phase"
) -> EditorState:
    """Load swimlane editor state for the site.

    group_by determines how lanes are built:
      - "period_phase" (default): one lane per (periodo_iniziale, fase_iniziale)
        via RowProvider (period_table + fallback distinct)
      - "struttura" | "attivita" | "settore" | "area" |
        "ambient" | "saggio" | "quad_par":
        one lane per DISTINCT us_table.<col> WHERE sito=:site
      - "none": one lane "default" with all US
    """
```

Per group_by ≠ `period_phase`, RowProvider è bypassato e le lane vengono
costruite dalla query distinct sui campi pyarchinit.

### 4.2 `pyarchinit_mini/harris_swimlane/harris_layout.py` (new)

```python
def compute_harris_positions(
    us_nodes: list[dict],
    edges: list[dict],
    *,
    lane_id_for: Callable[[dict], str],
    lane_widths: dict[str, int],
    node_w: int = 80,
    node_h: int = 30,
    h_gap: int = 30,
    v_gap: int = 20,
) -> dict[str, tuple[float, float]]:
    """Compute (x, y) for each US node WITHIN its lane.

    Algorithm:
      1. Group nodes by lane via lane_id_for(node)
      2. Within each lane, build subgraph from edges (overlies/is_after only)
      3. Topological sort: oldest (no incoming) at bottom, recent at top
      4. Assign y by rank, x by lateral packing within rank
      5. Orphans (no edges) packed at bottom of lane

    Returns: {node_id: (x_local, y_local)}
    """
```

Posizione finale del nodo nel canvas = `(lane_x_offset + x_local, y_local)`.
Lane_widths consente alle lane di adattarsi al contenuto.

### 4.3 `pyarchinit_mini/graphml_io/yed_writer.py` (RIWRITE)

Nuova API:

```python
def write_extended_matrix_graphml(
    state: EditorState,
    *,
    site_meta: SiteMeta,
    epochs: list[Epoch],
    out: Path,
) -> None:
    """Emit yEd Extended Matrix GraphML, byte-compat with pyarchinit QGIS.

    Output structure:
      <graphml xmlns="...">
        <key for="graph" id="d0" attr.name="pyarchinit.epochs_meta" .../>
        ...37 more <key> definitions
        <graph id="G" edgedefault="directed">
          <data key="d0"><![CDATA[<epochs_meta JSON>]]></data>
          <node id="n0" yfiles.foldertype="group">    <!-- TableNode root -->
            <data key="d31">
              <y:TableNode configuration="YED_TABLE_NODE">
                <y:Geometry ... />
                <y:Table>
                  <y:Rows>
                    <y:Row id="row_0" height="..." />  <!-- recent on top -->
                    <y:Row id="row_1" ... />
                    ...
                  </y:Rows>
                </y:Table>
              </y:TableNode>
            </data>
            <graph>  <!-- nested: contains US children -->
              <node id="n1"><!-- US 91 --></node>
              <node id="n2"><!-- US 92 --></node>
              ...
            </graph>
          </node>
          <edge id="e1" source="n1" target="n2"><!-- ... --></edge>
        </graph>
      </graphml>
    """
```

Mantengo il vecchio `write_yed_graphml` come **deprecated thin wrapper** che
chiama il nuovo. Grace period: 1 release (rimosso in 2.6.0).

### 4.4 `pyarchinit_mini/graphml_io/yed_importer.py` (new)

```python
@dataclass
class ImportPlan:
    sites: list[SitePlan]              # {sito, da_creare: bool}
    periodizations: list[PeriodPlan]   # {sito, periodo, fase, datazione_estesa, action}
    us_records: list[USPlan]           # {node_uuid, sito, us, unita_tipo, ..., action}
    relationships: list[RelPlan]       # {sito, us_from, us_to, type, action}
    warnings: list[str]                # non-fatal, shown in preview
    conflicts: list[Conflict]          # require user decision

@dataclass
class ImportResult:
    sites_created: int
    sites_updated: int
    periodizations_created: int
    periodizations_updated: int
    us_created: int
    us_updated: int
    us_skipped: int
    relationships_created: int
    duration_ms: int
    errors: list[str]

def parse_extended_matrix(path: Path) -> ParsedGraphML: ...
def build_import_plan(parsed: ParsedGraphML, session: Session) -> ImportPlan: ...
def apply_import_plan(plan: ImportPlan, session: Session) -> ImportResult: ...
```

`apply_import_plan` esegue tutto in **una sola transazione**. Triggera Spec 2
`_trigger_graph_regen(site, session)` per ogni sito modificato (best-effort).

### 4.5 `pyarchinit_mini/web_interface/yed_import_routes.py` (new blueprint)

```python
yed_import_bp = Blueprint("yed_import", __name__, url_prefix="/import-graphml")

@yed_import_bp.get("/")
def index():
    """Render upload form HTML."""

@yed_import_bp.post("/preview")
def preview():
    """Parse uploaded file + build_import_plan, save plan in flask_session
    under uuid key, render preview.html with stats + Apply button."""

@yed_import_bp.post("/apply")
def apply():
    """Pop plan from session, apply_import_plan, render result.html."""
```

Plan persistito in `flask_session[f"yed_import_plan:{uuid}"]` con timeout 5min.
One-shot: `apply` lo cancella dopo l'esecuzione.

### 4.6 Templates HTML

- `templates/yed_import/index.html` — form upload con drag&drop
- `templates/yed_import/preview.html` — tabella riassuntiva counts + conflict
  list + Apply / Cancel buttons
- `templates/yed_import/result.html` — risultato finale (stats + errori)

### 4.7 Editor toolbar update

`templates/harris_creator/editor.html` — aggiungere dropdown "Group by"
sopra il canvas Cytoscape:

```html
<select id="group-by-selector" class="form-select form-select-sm">
  <option value="period_phase" selected>Period + Phase</option>
  <option value="struttura">Struttura</option>
  <option value="attivita">Attività</option>
  <option value="settore">Settore</option>
  <option value="area">Area</option>
  <option value="ambient">Ambient</option>
  <option value="saggio">Saggio</option>
  <option value="quad_par">Quad/Par</option>
  <option value="none">None (single lane)</option>
</select>
```

JS handler ricarica `loadSwimlaneState(site, group_by)` al change.

### 4.8 Sidebar entry

`templates/base.html` — aggiungere link "Import GraphML" sotto la sezione
Tools (sia navbar dropdown sia sidebar laterale), puntando a
`url_for('yed_import.index')`.

## 5. Data flow

### Flow 1 — Editor load (con group_by)

```
Browser: GET /harris-creator/api/load/<site>?group_by=struttura
    ↓
api_get_load(site, group_by)
    ↓
SwimlaneState.load(session, site, group_by="struttura")
    │
    ├─ Se group_by=='period_phase':
    │       RowProvider.list_rows()
    │
    └─ Altrimenti:
            SELECT DISTINCT <group_by> FROM us_table WHERE sito=:site
    ↓
harris_layout.compute_harris_positions(us_rows, edges, lane_widths)
    ↓
JSON EditorState{site, group_by, rows, nodes, edges}
    ↓
Browser: renderSwimlaneState(state)
    Cytoscape: compound parent (lane) + child (US) con position fissa
```

### Flow 2 — Save Swimlane + auto-regen

Invariato Spec 3-bis. `POST /api/save/<site>` → `SwimlaneState.save` →
`_trigger_graph_regen` rigenera `stratigraphy.graphml` (Spec 2).

### Flow 3 — Editor export yEd Extended Matrix

```
Browser: GET /harris-creator/api/export/<site>/yed-graphml?group_by=X
    ↓
api_export_yed(site, group_by)
    ↓
state = SwimlaneState.load(session, site, group_by=group_by)
site_meta = load_site_meta(session, site)
epochs = load_epochs(session, site)
    ↓
yed_writer.write_extended_matrix_graphml(state, site_meta, epochs, out)
    ↓
data/exports/harris_yed/<slug>-extmatrix.graphml
    ↓
send_file as attachment
```

### Flow 4 — Import yEd preview

```
Browser: POST /import-graphml/preview  (multipart: file=Extended_Matrix.graphml)
    ↓
yed_import_routes.preview()
    ↓
yed_importer.parse_extended_matrix(file_path) → ParsedGraphML
    ↓
yed_importer.build_import_plan(parsed, session) → ImportPlan
    ↓
flask_session[f"yed_import_plan:{plan_id}"] = plan
    ↓
Render preview.html con tabella + Apply button
```

### Flow 5 — Import yEd apply

```
Browser: POST /import-graphml/apply  (form: plan_id=<uuid>)
    ↓
yed_import_routes.apply()
    ↓
plan = flask_session.pop(f"yed_import_plan:{plan_id}")
    ↓
yed_importer.apply_import_plan(plan, session)
    Begin TRANSACTION
      1. INSERT/SKIP sites (da_creare=True)
      2. UPSERT periodizzazione_table by (sito, periodo, fase)
      3. UPSERT us_table by node_uuid (fallback by (sito, us))
      4. INSERT us_relationships_table (dedup by triple)
    COMMIT
    ↓
Spec 2 _trigger_graph_regen(site, session) per ogni sito modificato
    ↓
Render result.html con stats finali
```

## 6. XML structure

### 6.1 Mapping keys ↔ DB

| Key | yEd attr.name | DB column | Direzione |
|---|---|---|---|
| `d0` | `pyarchinit.epochs_meta` (graph) | periodizzazione_table (JSON arr) | both |
| `d4` | `EMID` | `node_uuid` | both |
| `d5` | `URI` | (computed) | export-only |
| `d6` | `pyarchinit.us` | `us` | both |
| `d7` | `pyarchinit.area` | `area` | both |
| `d8` | `pyarchinit.sito` | `sito` | both |
| `d9` | `pyarchinit.unita_tipo` | `unita_tipo` | both |
| `d10` | `pyarchinit.periodo_iniziale` | `periodo_iniziale` | both |
| `d11` | `pyarchinit.fase_iniziale` | `fase_iniziale` | both |
| `d12` | `pyarchinit.rapporti` | `rapporti` | both |
| `d13` | `pyarchinit.d_stratigrafica` | `d_stratigrafica` | both |
| `d14` | `pyarchinit.d_interpretativa` | `d_interpretativa` | both |
| `d15` | `pyarchinit.documentazione` | `file_path` | both |
| `d16` | `pyarchinit.node_uuid` | `node_uuid` (dup di d4) | both |
| `d17-d22` | `pyarchinit.struttura/attivita/settore/ambient/saggio/quad_par` | omonimo | both |
| `d23` | `pyarchinit.datazione_estesa` (US) | `datazione` | both |
| `d24-d28` | `pyarchinit.periodo/fase/cron_iniziale/cron_finale/datazione_estesa` | periodizzazione_table | both |
| `d29` | `url` | — | export-only placeholder |
| `d30` | `description` | metadata | both |
| `d31` | `nodegraphics` (yEd shape) | VocabProvider visual_style | export-only |
| `d33-d36` | edge metadata | us_relationships_table | both |
| `d37` | `edgegraphics` | derived | export-only |

### 6.2 XML emesso (esempio US 91)

```xml
<node id="n42" yfiles.foldertype="">
  <data key="d4"><![CDATA[06a0ac44-5a4e-743d-8000-c7158e658833]]></data>
  <data key="d5"/>
  <data key="d6">91</data>
  <data key="d7">A</data>
  <data key="d8">Ravenna_(RA)_via_Cavour_60</data>
  <data key="d9">US</data>
  <data key="d10">2</data>
  <data key="d11">2</data>
  <data key="d12"><![CDATA[[('copre', '89')]]]></data>
  <data key="d13">strato di terra</data>
  <data key="d14">accumulo post-abbandono</data>
  <data key="d15"/>
  <data key="d16">06a0ac44-5a4e-743d-8000-c7158e658833</data>
  <data key="d17"/><data key="d18"/><data key="d19"/>
  <data key="d20"/><data key="d21"/><data key="d22"/>
  <data key="d23">II sec d.C.</data>
  <data key="d31">
    <y:ShapeNode>
      <y:Geometry x="200" y="540" width="80" height="30"/>
      <y:Fill color="#F0F0F0" transparent="false"/>
      <y:BorderStyle color="#540909" type="line" width="3.0"/>
      <y:NodeLabel>US91</y:NodeLabel>
      <y:Shape type="rectangle"/>
    </y:ShapeNode>
  </data>
</node>
```

### 6.3 TableNode root

Una sola istanza con `<y:Row id="row_0">`, `<y:Row id="row_1">`, ...,
ordinate **recent in alto** (= ordine cronologico inverso quando
`cron_iniziale` disponibile, altrimenti alfabetico discendente).
Geometry calcolata server-side da `harris_layout`.

### 6.4 Parser tolerance

- File con keys mancanti: default a stringa vuota
- File yEd "vanilla" (no `pyarchinit.us`): rifiuta 400
- Nodo senza `pyarchinit.sito`: skip + warning
- US duplicato con diversi node_uuid: l'ultimo vince + warning
- Epoch_meta JSON malformato: skip periodizzazione + warning

## 7. Error handling + validation

### 7.1 Error categories

| # | Categoria | Trattamento |
|---|---|---|
| 1 | Schema legacy DB (period_table) | Auto-migration (`_2026_05_period_table_schema`, già in 2.4.6) |
| 2 | Parsing yEd non valido | `YEDImporterError` con line/col, HTTP 400 |
| 3 | File yEd vanilla (non pyarchinit) | HTTP 400 "Not a pyarchinit Extended Matrix file" |
| 4 | Conflitto node_uuid cross-site | Preview mostra conflict, apply chiede override |
| 5 | Sito mancante | Preview marca `da_creare: True`, apply lo crea |
| 6 | Epoch_meta JSON malformato | Skip periodizzazione + warning |
| 7 | Edge da US inesistenti | Skip edge, log warning |
| 8 | Apply transaction abort | ROLLBACK completo + result.html con errori |
| 9 | Layout overflow (>10k nodes) | Fallback a `compute_simple_grid_positions` |

### 7.2 Validation rules in `build_import_plan`

```python
def build_import_plan(parsed, session):
    errors, conflicts, warnings = [], [], []

    if not parsed.nodes:
        raise YEDImportValidationError("File contains no US nodes")

    if not any(n.get('sito') for n in parsed.nodes):
        raise YEDImportValidationError("No pyarchinit.sito on any node")

    uuids = [n.get('node_uuid') for n in parsed.nodes if n.get('node_uuid')]
    dup = {u for u in uuids if uuids.count(u) > 1}
    if dup:
        warnings.append(f"Duplicate node_uuid in file: {dup}")

    existing_by_uuid = session.execute(
        text("SELECT node_uuid, sito FROM us_table WHERE node_uuid = ANY(:uuids)"),
        {"uuids": uuids}
    ).fetchall()
    for db_uuid, db_sito in existing_by_uuid:
        for parsed_n in parsed.nodes:
            if parsed_n.get('node_uuid') == db_uuid and parsed_n.get('sito') != db_sito:
                conflicts.append({
                    'kind': 'uuid_cross_site',
                    'node_uuid': db_uuid,
                    'db_sito': db_sito,
                    'file_sito': parsed_n['sito'],
                })
    return ImportPlan(errors=errors, conflicts=conflicts, warnings=warnings, ...)
```

### 7.3 Production tolerance

- Preview NON modifica il DB → safe a chiamare anche con file sospetti
- Apply usa una sola transazione → 100% rollback se qualcosa esplode
- Auto-regen Spec 2 post-apply è best-effort: errore qui non fa rollback
- `yed_writer` atomic write via `.tmp + os.replace`
- Logging strutturato: ogni import salva `import_log_<timestamp>.json` in
  `data/imports/`

## 8. Testing

### 8.1 Strategy

| Layer | Test target | Strategia |
|---|---|---|
| Unit | `harris_layout.compute_harris_positions` | Synthetic graph 5-10 US, verify topological order + lane confinement |
| Unit | `yed_writer.write_extended_matrix_graphml` | Golden file test — emit + compare structure against fixture |
| Unit | `yed_importer.parse_extended_matrix` | Parse `Extended_Matrix_test_1.graphml` fixture, assert counts + epochs_meta |
| Unit | `yed_importer.build_import_plan` | Mock DB session, verify upsert/create/skip decisions |
| Integration | Round-trip export-then-import | Assert DB state identical (by node_uuid + relationship triple) |
| Integration | Round-trip import-then-export | Assert file content reproducibility |
| Integration | `/api/load/<site>?group_by=X` | Fixture DB con struttura valorizzata, assert lane = N distinct values |
| Integration | `/import-graphml/preview` + `/apply` | Multipart upload, plan preview, apply, verify DB state |
| Regression | Spec 3-bis swimlane | 47 esistenti devono passare |

### 8.2 Test fixtures necessarie

| File | Contenuto | Path |
|---|---|---|
| `extended_matrix_pyarchinit.graphml` | Copia del file di riferimento (10 lane, ~50 US, epochs_meta) | `tests/fixtures/yed_graphml/extended_matrix_pyarchinit.graphml` |
| `minimal.graphml` | 1 sito, 1 epoch, 3 US, 2 edges (smoke test) | `tests/fixtures/yed_graphml/minimal.graphml` |
| `vanilla_yed.graphml` | yEd puro senza keys pyarchinit (test rejection) | `tests/fixtures/yed_graphml/vanilla_yed.graphml` |
| `malformed.graphml` | XML rotto a metà (test error reporting) | `tests/fixtures/yed_graphml/malformed.graphml` |
| `sqlite_ravenna_191us.db` | DB snapshot sanitizzato (round-trip test) | `tests/fixtures/databases/sqlite_ravenna_191us.db` |
| `golden_volterra_extmatrix.graphml` | Output atteso del writer su Volterra | `tests/fixtures/yed_graphml_outputs/golden_volterra_extmatrix.graphml` |

## 9. Definition of Done

### Backend
- [ ] `swimlane_state.load(session, site, group_by=...)` accetta 9 valori
- [ ] `harris_layout.compute_harris_positions` produce posizioni server-side
- [ ] `yed_writer.write_extended_matrix_graphml` emette tutte le 38 keys
- [ ] Output yEd byte-compat su key set + structure con file pyarchinit
- [ ] `yed_importer.parse_extended_matrix` legge il file di riferimento
- [ ] `yed_importer.build_import_plan` produce piano coerente
- [ ] `yed_importer.apply_import_plan` transazionale + idempotente

### REST API
- [ ] `GET /harris-creator/api/load/<site>?group_by=X` con 9 valori validi
- [ ] `GET /harris-creator/api/export/<site>/yed-graphml?group_by=X`
- [ ] `POST /import-graphml/preview` (multipart) → JSON plan
- [ ] `POST /import-graphml/apply` con plan_id → 200 + stats
- [ ] Tutti gli endpoint usano session lazy (eredità Spec 3-bis 2.4.2)

### UI
- [ ] Editor toolbar: dropdown "Group by" con 9 opzioni
- [ ] Editor renderizza lane con Harris-classico interno
- [ ] Edges visibili (no warning Cytoscape)
- [ ] Pannello Properties popolato al click
- [ ] `/import-graphml/` form upload, preview + apply
- [ ] Sidebar entry "Import GraphML"

### Test
- [ ] 15+ unit test su harris_layout, yed_writer, yed_importer
- [ ] 8+ integration test su routes
- [ ] 2 round-trip test (export-then-import + import-then-export)
- [ ] 1 golden file test su writer
- [ ] 47 Spec 3-bis + 399 totali esistenti passano (no regression)

### Documentation
- [ ] `docs/EXTENDED_MATRIX_IMPORT.md` — guida utente import
- [ ] `docs/EXTENDED_MATRIX_EXPORT.md` — guida utente export + compat pyarchinit
- [ ] `docs/HARRIS_LAYOUT_ALGO.md` — algoritmo layout interno
- [ ] CHANGELOG entry IT+EN per 2.5.0

### Release
- [ ] Bump 2.5.0 (minor — feature grossa)
- [ ] Tag git v2.5.0
- [ ] Upload PyPI
- [ ] Deploy Adarte con verify round-trip live

## 10. Backwards compat

- Vecchio `write_yed_graphml` → thin wrapper deprecato che chiama il nuovo.
  Grace period: 1 release, rimosso in 2.6.0.
- Path output: `data/exports/harris_yed/<slug>-extmatrix.graphml` (era
  `<slug>-harris-yed.graphml`). Redirect 308 sul vecchio nome se l'utente
  ha bookmark.
- API `/api/load/<site>` retro-compat: `group_by` opzionale, default
  `period_phase` = comportamento 2.4.x.
- API `/api/export/<site>/yed-graphml` retro-compat: senza `group_by` →
  `period_phase`.

## 11. Riferimenti

- File di riferimento template pyarchinit: `Extended_Matrix_test_1.graphml`
- Spec 1 (s3dgraphy foundation, VocabProvider, node_uuid)
- Spec 2 (Local Graph & Paradata, GraphIngestor)
- Spec 3-bis (Harris Swimlane Editor, _get_session lazy)
- pyarchinit QGIS plugin `modules/s3dgraphy/sync/`
