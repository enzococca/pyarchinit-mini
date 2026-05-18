# Harris Matrix Swimlane Editor — yEd-flavored Template + Auto-layout + Interactive Creation

**Spec date:** 2026-05-18
**Author:** Enzo Cocca (with brainstorming session)
**Status:** Design proposal — pending user review
**Target version:** `pyarchinit-mini` 2.3.0-alpha → 2.4.0-alpha
**Out of scope deps:** s3dgraphy GraphMLExporter (per Spec 2), VocabProvider (per Spec 1)
**Group:** Auxiliary spec between Spec 2 and Spec 3 (Datacenter sync), addressing a real user request that the Datacenter readiness does not block.

## 1. Overview

The Harris Matrix Creator at `/harris-creator/editor` currently uses
Cytoscape.js + dagre to render stratigraphic graphs as hierarchical
top-to-bottom layouts. Dagre does not natively support yEd-style
**swimlanes** (rows representing temporal periods). The legacy
`pure_networkx_exporter` did emit `y:TableNode`-based swimlanes by
period, but was deprecated in Spec 2 PR8 as part of the GraphML writer
cutover to `s3dgraphy.exporter.graphml.GraphMLExporter`.

s3dgraphy's exporter emits a single `simple_swimlane` `y:GroupNode`, not
a multi-row `y:TableNode`. So the swimlane-by-period feature is currently
absent from the post-Spec-2 web flow.

This spec brings yEd-like swimlanes back **and** adds the missing
interactive piece: the user can create new swimlane rows on the fly
while building a new Harris matrix from scratch, with each new row
upserting a corresponding `period_table` entry. Existing US records are
auto-placed in their respective swimlane based on `periodo_iniziale +
fase_iniziale`. The output is a separate yEd-flavored GraphML file
(`<site>-harris-yed.graphml`) that lives alongside Spec 2's clean
`stratigraphy.graphml` (s3dgraphy-emitted).

## 2. Context and decisions

### 2.1 Project context

- The web editor exists at `/harris-creator/editor` (Cytoscape.js +
  cytoscape-dagre). `harris_creator_routes.py` already exposes
  `/api/periods`, `/api/node-types`, `/api/relationship-types`,
  `/api/save`, `/api/export/<format>`.
- Two relevant DB tables (already in `pyarchinit_mini/models/harris_matrix.py`):
  - `period_table` (model `Period`): formal definitions —
    `id_period, period_name, phase_name, start_date, end_date,
    description, chronology`. **No `sito` column → cross-site / global.**
  - `periodizzazione_table` (model `Periodizzazione`): per-context
    assignments — `sito, area, us, periodo_iniziale, fase_iniziale,
    periodo_finale, fase_finale, datazione_estesa, motivazione`.
- `us_table` already has `periodo_iniziale, fase_iniziale,
  periodo_finale, fase_finale` columns (denormalised assignments).
- Spec 1's `VocabProvider.get_visual_style(unit_type)` is the canonical
  source for node colours/shapes. Re-used by the new yEd writer.
- Spec 2's `EdgeRegistry` parses `rapporti` strings to canonical edge
  names. Re-used by `SwimlaneState.load()` for edge construction.
- Spec 2's `auto_regen._trigger_graph_regen()` post-commit hook is
  invoked also from the new save endpoint to keep `stratigraphy.graphml`
  current after editor saves.

### 2.2 Decisions captured during brainstorming

| # | Decision | Value |
|---|---|---|
| D1 | Scope | **Single spec** covering template loading + auto-layout existing + interactive new (3 concerns share editor + data model) |
| D2 | Row source | **Mixed**: `period_table` priority → fallback distinct `(periodo_iniziale, fase_iniziale)` from `periodizzazione_table` (and `us_table`) |
| D3 | Row granularity | **One row per `(period_name, phase_name)` pair** (phase is first-class in `period_table`) |
| D4 | Orientation / ordering | **Horizontal rows, recent at top** (Harris convention). Label `period+phase` on the left |
| D5 | Cytoscape implementation | **Compound nodes (1 level)**: swimlane = parent compound node; US = child node. No library switch |
| D6 | GraphML output (yEd-flavored) | **New `graphml_io/yed_writer.py`** writing `y:TableNode + y:Table + y:Rows`. Legacy `pure_networkx_exporter` **stays deprecated** (not resurrected) |
| D7 | Approach | **Parallel + cutover.** 8 PRs. Mirrors Spec 1/2 pattern. ~22 tasks total |
| D8 | DB writes on drag-drop | **Save-only.** Drag-drop in editor only modifies pending-state on the client; explicit "Save" triggers DB UPDATE/INSERT/DELETE |
| D9 | Concurrent edits | **Last-writer-wins** (Spec 2 policy). Real-time conflict UI is Spec 4 |
| D10 | yEd export | **On-demand only.** No auto-regen of `<site>-harris-yed.graphml`; user clicks "Export yEd GraphML" |
| D11 | Multi-period US handling | **Place in start row** (`periodo_iniziale + fase_iniziale`). Span / dual-position is deferred (Spec 4) |
| D12 | Auto_regen integration | Save endpoint also calls `_trigger_graph_regen(site, session)` (Spec 2). Two derived outputs (clean `stratigraphy.graphml` + on-demand `<site>-harris-yed.graphml`) coexist for different audiences |

### 2.3 Out of scope (deferred)

- Round-trip from yEd Desktop → editor (import yEd-edited GraphML) — Spec 3-ter
- Real-time concurrent edit visibility (WebSocket / SSE) — Spec 4
- Stratigraphic edge auto-routing inside yEd TableNode constraints (user
  may need to re-route in yEd) — out of band
- Cytoscape touch / mobile support — out of band
- Per-site `period_table` (current schema is cross-site) — Spec 4 if
  isolation becomes load-bearing
- USVn / USVs visual variants in TableNode rows — Spec 2's VocabProvider
  styles apply; nothing new needed
- Promote-fallback bulk migration UI — deferred to Spec 4 (the helper
  exists in `period_sync_service.maybe_promote_fallback` but not exposed)

## 3. Architecture

Two new packages plus modifications to one existing route file:

```
pyarchinit_mini/
├── harris_swimlane/                  # NEW — backend swimlane logic
│   ├── __init__.py
│   ├── exceptions.py                 # SwimlaneError + 4 specific subclasses
│   ├── row_provider.py               # RowProvider — period_table → list[Row]; fallback
│   ├── compound_layout.py            # Cytoscape compound positioning helpers
│   ├── swimlane_state.py             # Cytoscape JSON ↔ DB serialization
│   └── period_sync_service.py        # Interactive row creation → period_table upsert
├── graphml_io/
│   └── yed_writer.py                 # NEW — y:TableNode emitter (separate from s3dgraphy)
└── web_interface/
    └── harris_creator_routes.py      # MODIFY — 5 new endpoints + editor.html updates
```

Flow at-a-glance:

```
Browser /harris-creator/editor?site=Volterra
  │
  ├─ GET /api/swimlanes/<site> ────► RowProvider.list_rows()
  │                                    period_table → fallback distinct
  │
  ├─ GET /api/load/<site> ───────────► SwimlaneState.load()
  │                                    rows + US (with parent=row_id) + edges
  │                                    via EdgeRegistry (Spec 1/2)
  │
  ├─ POST /api/swimlanes/<site> ────► PeriodSyncService.upsert_row()
  │                                    INSERT INTO period_table
  │
  ├─ POST /api/save/<site> ─────────► SwimlaneState.save()
  │                                    UPDATE/INSERT/DELETE us_table
  │                                    ↳ AFTER COMMIT:
  │                                       auto_regen._trigger_graph_regen()
  │                                       (Spec 2 — regenerates stratigraphy.graphml)
  │
  └─ GET /api/export/<site>/yed-graphml ► yed_writer.write_yed_graphml()
                                          y:TableNode + Rows + US ShapeNodes
                                          → data/exports/harris_yed/<slug>-harris-yed.graphml
```

**Two GraphML outputs coexist** for two audiences:
- `stratigraphy.graphml` (Spec 2 auto-regen) — s3dgraphy clean,
  EM-canonical, for the EM Datacenter & external interoperability
- `<site>-harris-yed.graphml` (this spec, on-demand) — yEd-flavored
  with TableNode, for users who want to open/edit in yEd Desktop

**Backward compat:** existing routes (`/api/save`, `/api/export/<format>`,
`/api/periods`, etc.) remain functional. The 5 new endpoints have
paths under `/api/swimlanes/`, `/api/load/`, `/api/save/<site>`,
`/api/export/<site>/yed-graphml` to avoid collision.

## 4. Components

### 4.1 `harris_swimlane/row_provider.py`

```python
@dataclass(frozen=True)
class Row:
    row_id: str                  # canonical: slugified "period__phase"
    period_name: str
    phase_name: str | None
    start_date: int | None
    end_date: int | None
    color: str                   # auto-assigned from PERIOD_COLORS palette
    source: str                  # "period_table" | "fallback_distinct"


class RowProvider:
    def __init__(self, session: Session, site: str) -> None: ...

    def list_rows(self) -> list[Row]:
        """Returns rows sorted: most-recent-first (descending start_date).
        Source priority: period_table → fallback to distinct values from
        periodizzazione_table + us_table when period_table empty."""

    def find_row(self, period: str, phase: str | None) -> Row | None:
        """Lookup helper. Returns None for unknown (period, phase)."""
```

**Color cycling:** PERIOD_COLORS palette (30 distinct colors, reused
from `graphml_converter/yed_template.py:YEdTemplate.PERIOD_COLORS`).
Sites with >30 rows cycle the palette; logged as INFO.

**Sort fallback:** when `start_date` is NULL, ordering falls back to
alphabetical on `(period_name, phase_name)`. Logged WARNING.

### 4.2 `harris_swimlane/swimlane_state.py`

```python
@dataclass
class CytoscapeElement:
    data: dict                   # id, label, parent, period, phase, unit_type
    classes: str = ""
    position: dict | None = None  # {x, y}


@dataclass
class EditorState:
    site: str
    rows: list[Row]              # swimlanes as parent compound nodes
    nodes: list[CytoscapeElement]  # US nodes with parent=row_id
    edges: list[CytoscapeElement]  # stratigraphic edges from rapporti
    pending_changes: dict        # {us_updates: [], us_inserts: [], us_deletes: []}


class SwimlaneState:
    @staticmethod
    def load(session: Session, site: str) -> EditorState:
        """Load: row_provider + us_table rows + edges from rapporti
        → returns Cytoscape-shaped state ready to JSON-serialize.

        Each US becomes a child node with parent=<row_id derived from
        periodo_iniziale + fase_iniziale>. US without period → parent
        '_unassigned' pseudo-row."""

    @staticmethod
    def save(session: Session, site: str, state: dict) -> "SaveResult":
        """Save: apply pending_changes to DB.
        - us_updates: UPDATE us_table SET periodo_iniziale=..., fase_iniziale=...
        - us_inserts: INSERT INTO us_table + node_uuid via uuid7
        - us_deletes: DELETE FROM us_table

        All in single transaction. Rollback on partial failure.
        After successful commit: invokes auto_regen._trigger_graph_regen()
        (Spec 2 compat). Returns SaveResult with counts + errors."""
```

`SaveResult` dataclass: `{updated: int, inserted: int, deleted: int, errors: tuple[str, ...]}`.

### 4.3 `harris_swimlane/period_sync_service.py`

```python
class PeriodSyncService:
    def __init__(self, session: Session) -> None: ...

    def upsert_row(self, period_name: str, phase_name: str | None = None,
                   start_date: int | None = None,
                   end_date: int | None = None) -> Row:
        """Interactive: when user creates a new swimlane row in the editor,
        ensure a corresponding period_table entry exists. Idempotent: if
        (period_name, phase_name) already exists, returns it without
        creating a duplicate."""

    def maybe_promote_fallback(self, site: str) -> int:
        """For sites currently using fallback source, offer to bulk-promote
        their distinct (periodo_iniziale, fase_iniziale) values into formal
        period_table entries. Returns count promoted. Helper exists but
        not wired to UI in this spec (Spec 4 territory)."""
```

`period_table` has no `sito` column → rows are cross-site. Implication:
creating a row in site A's editor makes it available in site B's editor
too. Documented as a known limitation; could be addressed in Spec 4 if
isolation becomes load-bearing.

### 4.4 `harris_swimlane/compound_layout.py`

```python
def initial_node_position(row: Row, index_in_row: int) -> dict:
    """Compute initial (x, y) for a node within its row parent.
    Returns {x, y}. Used at editor load to give Cytoscape an initial
    layout. After load, Cytoscape's dagre layout (constrained by
    parent boundaries) refines."""

def compute_row_positions(rows: list[Row]) -> dict[str, tuple[float, float]]:
    """Stack the swimlane parents top-to-bottom with most-recent at top
    (per D4). Returns {row_id: (x, y)}.

    Row height: max(min_height, 40 * us_count_in_row).
    Row width: configurable canvas width (default 2000)."""
```

### 4.5 `harris_swimlane/exceptions.py`

```python
class SwimlaneError(Exception): pass
class RowProviderError(SwimlaneError): pass
class PeriodSyncError(SwimlaneError): pass
class SwimlaneStateError(SwimlaneError): pass
class YEDWriterError(SwimlaneError): pass
```

### 4.6 `graphml_io/yed_writer.py`

```python
def write_yed_graphml(state: "EditorState", path: Path) -> None:
    """Emit yEd-flavored GraphML with TableNode + Rows.

    Structure:
      <graphml>
        <graph>
          <node id="swimlane_root" yfiles.foldertype="group">
            <data><y:TableNode>
              <y:Table>
                <y:Rows>
                  <y:Row id="row_period3_phaseb" height="120.0"/>
                  <y:Row id="row_period3_phasea" height="200.0"/>
                  ...
                </y:Rows>
                <y:Columns><y:Column id="col_main" width="1900.0"/></y:Columns>
              </y:Table>
            </y:TableNode></data>
            <graph>  <!-- nested -->
              <node id="us_5">
                <data><y:ShapeNode>
                  <y:Geometry x="50" y="20" width="80" height="50"/>
                  <y:Fill color="#F0F0F0"/>  <!-- from VocabProvider -->
                  <y:BorderStyle color="#540909" width="3.0"/>
                  <y:Shape type="rectangle"/>  <!-- from VocabProvider -->
                </y:ShapeNode></data>
              </node>
              ...
            </graph>
          </node>
        </graph>
        <edge id="e1" source="us_5" target="us_3">
          <data><y:GenericEdge>
            <y:EdgeLabel>overlies</y:EdgeLabel>
          </y:GenericEdge></data>
        </edge>
      </graphml>

    Visual style per US: VocabProvider.get_visual_style(unit_type)
    (Spec 1). Fallback to VisualStyle.fallback() for unknown types.
    Row height: 40 * max(1, us_count_in_row); minimum 40.

    Writes atomically via tmp + os.replace (per Spec 2 pattern).
    Raises YEDWriterError on filesystem / serialization failures."""
```

**No hardcoded palette** in yed_writer. All visual style routed through
`VocabProvider.get_visual_style()`. PERIOD_COLORS palette for row
backgrounds comes from `row.color` (assigned by RowProvider).

### 4.7 New REST endpoints

```
GET    /harris-creator/api/swimlanes/<site>          → rows JSON
POST   /harris-creator/api/swimlanes/<site>          → create row, 201
GET    /harris-creator/api/load/<site>               → EditorState as Cytoscape JSON
POST   /harris-creator/api/save/<site>               → save pending_changes + trigger regen
GET    /harris-creator/api/export/<site>/yed-graphml → download yEd-flavored file
```

All endpoints require `flask_login` auth. Audit log entry per write
op (Spec 2 audit pattern extended).

### 4.8 Frontend `editor.html` updates

- Cytoscape compound config: each US node gets `data('parent')` =
  `row_id`; swimlane parents have `classes: 'swimlane'` with style
  override for background colour from `row.color`.
- Drag-drop handler: when US is dropped on a different row parent,
  updates `data('parent')` + pushes `{us_id, parent_old, parent_new}`
  to `pending_changes.us_updates`. Visual indicator: "● Unsaved".
- Modal "+ New Row": form fields `period_name` (required),
  `phase_name?`, `start_date?`, `end_date?` → POST `/api/swimlanes/<site>`
  → on success, add Cytoscape compound parent at top (most-recent
  placement).
- "Save" button: POST `/api/save/<site>` with `pending_changes`. On
  success: clear pending indicator, show "✓ Saved", trigger Cytoscape
  refresh from server (re-fetch `/api/load/<site>` to capture any
  side-effects like auto-regen).
- "Export yEd GraphML" button: GET `/api/export/<site>/yed-graphml` →
  browser triggers download.
- Performance guardrail: count US > 500 → show warning banner
  "Consider filtering by area for better performance."

## 5. Data flow

### 5.1 Open editor (load existing data)

```
Browser GET /harris-creator/editor?site=Volterra
  → render template editor.html (Cytoscape init)
  → JS GET /api/load/Volterra
    → RowProvider(session, "Volterra").list_rows()
        ├─ try period_table (5 rows sorted desc by start_date)
        └─ if empty → distinct from periodizzazione + us_table
    → SwimlaneState.load(session, "Volterra")
        ├─ for each US: derive parent row_id
        ├─ for each rapporti relation → edge via EdgeRegistry
        └─ EditorState(rows, nodes, edges)
  → JS Cytoscape: compound parents + child US + dagre within parent
```

### 5.2 Drag US to different row

```
User drags US 5 from "P2/a" → "P3/b"
  → Cytoscape compound drag handler
  → JS: us_node.move({parent: "row_period3_phaseb"})
  → JS: pending_changes.us_updates.push({us_id: 5, ...})
  → UI shows "● Unsaved"
  → no DB write yet
```

### 5.3 Create new row interactively

```
User clicks "+ New Row" → modal
  → fields: period_name="Period 4", phase_name="a", start=1500, end=1700
  → JS POST /api/swimlanes/Volterra {...}
    → PeriodSyncService.upsert_row(...)
      → INSERT INTO period_table (idempotent)
      → returns Row(row_id, color auto-assigned)
    → 201 + JSON
  → JS: add Cytoscape parent at top
```

### 5.4 Save

```
User clicks "Save"
  → JS POST /api/save/Volterra {pending_us_updates, pending_us_inserts, pending_us_deletes}
    → SwimlaneState.save()
      → UPDATE/INSERT/DELETE us_table (in transaction)
      → session.commit()
      → AFTER COMMIT: _trigger_graph_regen(site, session=session)  # Spec 2
  → 200 + {updated: 3, inserted: 2, deleted: 1}
  → JS: clear pending; re-fetch /api/load to capture side-effects
```

### 5.5 Export yEd-flavored GraphML

```
User clicks "Export yEd GraphML"
  → JS GET /api/export/Volterra/yed-graphml
    → state = SwimlaneState.load(session, "Volterra")
    → out_path = "data/exports/harris_yed/volterra-harris-yed.graphml"
    → yed_writer.write_yed_graphml(state, out_path)
    → send_file(out_path, as_attachment=True,
                download_name="volterra-harris-yed.graphml",
                mimetype="application/xml")
  → browser triggers download
```

### 5.6 Empty site flow

```
GET /api/load/NewSite → 200 + empty EditorState
  → Editor banner: "No periods defined. Click '+ New Row' to start."
  → User creates first row (Flow 5.3) → can drag-create US (palette)
```

### 5.7 Fallback path (no period_table, distinct in periodizzazione)

```
RowProvider.list_rows():
  → period_table empty → fallback
  → SELECT DISTINCT periodo_iniziale, fase_iniziale FROM periodizzazione_table WHERE sito=?
    + UNION with distinct from us_table.periodo_iniziale+fase_iniziale
  → for each unique tuple → synth Row(row_id, period, phase,
      start_date=None, end_date=None, color=auto, source="fallback_distinct")
  → sort alphabetical
  → editor banner: "Periods derived from existing US records.
    [Promote to period_table]" (link to maybe_promote_fallback — UI deferred to Spec 4)
```

## 6. Storage layout

```
data/
├── pyarchinit_mini.db                                    # principal SQLite
├── paradata/                                              # Spec 2 territory (unchanged)
│   └── <site_slug>/
│       ├── paradata.graphml + .json
│       └── stratigraphy.graphml                          # auto-regen (s3dgraphy clean)
└── exports/                                               # NEW — Spec 3-bis
    └── harris_yed/
        ├── <site_slug>-harris-yed.graphml                # on-demand export
        ├── _index.json                                    # last-export timestamps
        └── *.tmp                                          # transient, cleaned on success
```

**Git tracking:**
- `data/exports/harris_yed/*.graphml` → **NOT** committed (`.gitignore` entry)
- `data/exports/harris_yed/_index.json` → **NOT** committed (audit, regenerable)

**Atomic write:** yed_writer follows Spec 2 pattern — write to `.tmp`
then `os.replace`. Path traversal blocked by `_slugify(site)` (Spec 2 helper).

**Disk footprint estimate:** typical site (~100 US, 10 swimlane rows) →
~50 KB yEd file. Volterra-scale (~1500 US, 30 rows) → ~600 KB. 50-site
instance → ~30 MB. No quota enforcement.

## 7. Error handling

Guiding principle: **swimlane editor errors do not block the classic
US form flow or Spec 1/2 functionality**.

### 7.1 Editor bootstrap errors

| Case | HTTP | UX |
|---|---|---|
| `period_table` query fails | 500 + `{"error":"row_provider","message":...}` | Editor: "Cannot load periods. Retry." Classic form still works |
| period_table + periodizzazione empty | 200 + `rows=[]` | Banner: "No periods defined. Click '+ New Row' to start." |
| Site not found | 404 + `{"error":"site_not_found"}` | Editor: "Site X not found. Did you mean: [suggestions]?" |
| Cytoscape lib not loaded (CDN down) | n/a | Fallback: "Editor unavailable, check network." Classic form unaffected |
| US with legacy `unita_tipo` (USVA/USVB/USVC) | n/a | Banner: "Some US use deprecated vocab. Run migrate-vocab." Style fallback grey rectangle (per Spec 1) |

### 7.2 RowProvider errors

| Case | Strategy |
|---|---|
| period_table.start_date NULL | Sort fallback: alphabetical (logged WARNING) |
| Duplicate (period_name, phase_name) in period_table | First wins; others skipped + WARNING |
| Color palette exhausted (>30 rows) | Cycle the palette (modulo 30); same color may reappear |
| period_table is cross-site (current schema) | Documented limitation; not enforced per-site (Spec 4 if needed) |

### 7.3 SwimlaneState errors

| Case | HTTP |
|---|---|
| Save body malformed | 400 + `{"error":"validation","fields":...}` |
| UPDATE constraint violation (e.g. unique us-area-sito) | Transaction rollback. 200 OK + errors[] in body. Pending preserved client-side |
| INSERT us_table duplicate | Same — rolled back |
| DELETE FK violation (inventario references) | Same |
| Auto_regen after save fails | Save still 200 OK; regen failure logged (Spec 2 banner mechanism) |
| State JSON >50MB | 413 (Flask MAX_CONTENT_LENGTH default) |

### 7.4 PeriodSyncService errors

| Case | HTTP |
|---|---|
| Empty `period_name` | 400 + validation error |
| (period_name, phase_name) already exists | 200 + existing Row (idempotent) |
| start_date > end_date | 400 + validation error |
| period_table write fails | 500 + log |

### 7.5 yEd writer errors

| Case | Strategy |
|---|---|
| EditorState inconsistent (orphan node) | `YEDWriterError`. 500 + actionable body |
| File write fail (disk, permission) | Tmp file cleaned. `YEDWriterError` + 500 + log |
| VocabProvider lookup error | Per-node fallback to `VisualStyle.fallback()`. WARNING per miss |
| Path traversal in site name | `_slugify(site)` blocks. 400 if slug empty |

### 7.6 Cytoscape compound issues (frontend)

| Issue | Mitigation |
|---|---|
| Drag US outside any row | Add to `_unassigned` pseudo-row + visual warning |
| Accidental drag of row parent | Cytoscape config: `selectable: true, grabbable: false` on parents |
| Dagre layout glitch with compound | Modal "Layout reset" option |
| Performance >500 US | Warning banner: "Consider filtering by area" |

### 7.7 Logging channels

| Channel | Content | Level |
|---|---|---|
| Python `logging` (`pyarchinit_mini.harris_swimlane`) | Row provider, save outcomes, yed_writer | INFO/WARNING/ERROR |
| `data/exports/harris_yed/_index.json` | Per export: ts, site, user, file_path, file_size | always |
| Flask header `X-Swimlane-Status` | `ok` / `fallback_source` / `error` | when relevant |
| Audit log (extending Spec 2) | `harris.row.create`, `harris.save`, `harris.export` | always |

### 7.8 Validation gates

| Gate | Where |
|---|---|
| `site` slug valid | `_slugify(site)` (Spec 2 helper, blocks path traversal) |
| `period_name` non-empty | PeriodSyncService.upsert_row |
| `unita_tipo` valid | DTO via VocabProvider (Spec 1 — re-used) |
| pending_changes shape | Backend validates arrays |
| Upload size | Flask `MAX_CONTENT_LENGTH = 50 MB` |

## 8. Testing strategy

### 8.1 Pyramid

| Level | Target | Coverage |
|---|---|---|
| Unit | ~55 | RowProvider (priority + fallback), SwimlaneState (load/save), PeriodSyncService (upsert idempotency), compound_layout (math), yed_writer (XML emission per fixture), exceptions |
| Integration | ~25 | Flask routes (4 new), DB round-trip (load → drag → save → re-load preserved), period creation triggers period_table insert, auto_regen fires after save |
| E2E | ~5 | Editor load on real DB site (Volterra-30us fixture), yEd round-trip (manual: open in yEd Desktop), empty-site flow, fallback-source flow, save+regen interplay |

Framework: pytest (existing). Optional `playwright` for headless browser
tests (deferrable).

### 8.2 Fixtures

```
tests/fixtures/
├── databases/
│   ├── sqlite_volterra_30us_with_periods.db   # 30 US across 5 (period, phase) pairs
│   ├── sqlite_periodizzazione_only.db         # No period_table, only periodizzazione
│   ├── sqlite_empty_site.db                    # Empty site, 0 US, 0 periods
│   └── sqlite_legacy_vocab.db                  # US with USVA/USVB/USVC (graceful)
├── cytoscape_states/
│   ├── volterra_loaded.json                    # Expected /api/load response
│   ├── volterra_with_pending_changes.json      # Typical /api/save body
│   └── volterra_save_result.json               # Expected /api/save response
└── yed_graphml_outputs/
    ├── volterra_baseline.graphml               # Golden fixture for yed_writer parity
    └── empty_swimlane.graphml                  # Empty-state output
```

DB fixtures regenerable via `tests/fixtures/_generate_harris_swimlane_synthetic.py`.

### 8.3 Critical tests

1. **`test_swimlane_load_roundtrip.py`** — load editor, assert correct
   row/node/edge counts, parent assignment, EdgeRegistry usage
2. **`test_swimlane_save_persists.py`** — load → modify pending → save
   → re-load → state preserved; auto_regen invoked (mock-verified)
3. **`test_swimlane_save_concurrent_edit.py`** — A loads, B updates DB
   directly, A saves → last-writer-wins (documents Spec 2 policy)
4. **`test_period_sync_idempotent.py`** — upsert_row twice with same args
   returns existing row; different args creates new
5. **`test_yed_writer_xml_parity.py`** — render fixture to file, diff vs
   golden (`volterra_baseline.graphml`). Allowed diffs: yfiles version
   metadata, minor coordinate jitter. Updatable via
   `pytest --update-fixtures`
6. **`test_row_provider_fallback.py`** — empty period_table + 3 distinct
   periodizzazione entries → 3 fallback rows
7. **`test_editor_empty_site.py`** — empty state load + first row creation
   + first US insert + save round-trip
8. **`test_yed_export_writes_file.py`** — file appears at correct path +
   `_index.json` updated with timestamp

### 8.4 CI matrix

| OS | Python | Storage |
|---|---|---|
| macOS Sequoia | 3.13 | SQLite + filesystem |
| Ubuntu 24.04 | 3.13 + 3.12 | SQLite + PG (Docker) + filesystem |
| Windows 11 | 3.13 | SQLite + filesystem |

Pattern identical to Spec 1/2. PG tests skipped via `pg_isready`.

### 8.5 Manual smoke gates

| Test | Pass criteria |
|---|---|
| Open Volterra fixture in browser | Swimlanes visible with labels; US in correct rows; row colours distinct |
| Drag US 5 from P2/a → P3/b | "● Unsaved"; save → re-load → US 5 in P3/b |
| Create new row "P4/a" via modal | Row appears at top; period_table updated |
| Export yEd GraphML + open in yEd Desktop | TableNode with separate rows; US inside rows; styles correct |
| 500+ US stress | Load <5s; drag responsive; warning banner visible |
| Empty site → rows → US → save → re-load | Full persistence |

## 9. Definition of Done

- All unit + integration tests green on CI matrix
- yEd writer XML parity test green (golden fixture)
- Auto_regen integration green on SQLite + PG (Spec 2 invariant preserved)
- yEd export opens cleanly in yEd Desktop (manual smoke)
- CHANGELOG bilingual IT + EN
- Version bumped `2.3.0-alpha → 2.4.0-alpha`
- `README.md` gets new "Harris Swimlane Editor" section
- `docs/HARRIS_SWIMLANE.md` (user) — editor usage + drag-drop + row creation
- `docs/YED_INTEGRATION.md` (advanced) — round-trip, limits, future specs
- 8 PRs in order: PR1 swimlane module → PR2 yed_writer → PR3 route +
  load endpoint → PR4 save endpoint + auto_regen integration → PR5
  row creation endpoint + period_sync → PR6 editor.html frontend +
  modal → PR7 export endpoint + UI button → PR8 docs + release

## 10. Implementation phasing

| Spec | Scope | Depends on |
|---|---|---|
| **1 (merged)** — Web Foundation | VocabProvider + endpoints + DB migrations | — |
| **2 (merged)** — Local Graph & Paradata | GraphProjector + ParadataStore + GraphIngestor + auto_regen | Spec 1 |
| **3-bis (this doc)** — Harris Swimlane Editor | RowProvider + SwimlaneState + PeriodSync + yed_writer + editor UI | Spec 1 + 2 |
| **3** — Sync Engine + EM Backend | SyncEngine + DatacenterClient + ConflictResolver web UI | Spec 1 + 2 + EM Datacenter API |
| **4** — GraphDB Backend | GraphDBBackend (SPARQL), same interface as Spec 3 | Spec 1 + 2; parallel to Spec 3 |

3-bis is auxiliary — addresses a real user-request that does not depend
on Datacenter readiness. Spec 3 (SyncEngine) remains on hold until the
EM Datacenter API is available.

## 11. Open questions (deferred, non-blocking)

1. Round-trip from yEd Desktop → editor — Spec 3-ter
2. Real-time concurrent edit visibility (WebSocket/SSE) — Spec 4
3. Stratigraphic edge auto-routing inside yEd TableNode constraints —
   out of band (user re-routes in yEd if needed)
4. Cytoscape touch / mobile support — out of band
5. Per-site `period_table` schema (currently cross-site) — Spec 4 if
   isolation becomes load-bearing
6. Promote-fallback bulk migration UI — Spec 4 (helper exists,
   `period_sync_service.maybe_promote_fallback`; not exposed in UI)

## 12. References

- **Spec 1 (merged):** `docs/superpowers/specs/2026-05-16-s3dgraphy-web-foundation-design.md`
- **Spec 2 (merged):** `docs/superpowers/specs/2026-05-17-spec-2-local-graph-paradata-design.md`
- **Spec 2 plan:** `docs/superpowers/plans/2026-05-17-spec-2-local-graph-paradata.md`
- **Legacy reference (deprecated, not resurrected):**
  `pyarchinit_mini/graphml_converter/pure_networkx_exporter.py` — original
  TableNode-emission logic, kept for reference; will be removed in Spec 3
- **yEd palette source:** `pyarchinit_mini/graphml_converter/yed_template.py:PERIOD_COLORS`
- **yEd GraphML spec:** <https://yed.yworks.com/support/qa/3413/yed-graphml-format>
- **Cytoscape.js compound nodes:** <https://js.cytoscape.org/#notation/compound-nodes>
- **DB models:** `pyarchinit_mini/models/harris_matrix.py` (Period, Periodizzazione)
