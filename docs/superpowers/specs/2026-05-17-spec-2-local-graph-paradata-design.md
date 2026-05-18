# PyArchInit-Mini Web ↔ s3dgraphy — Spec 2: Local Graph & Paradata

**Spec date:** 2026-05-17
**Author:** Enzo Cocca (with brainstorming session)
**Status:** Design proposal — pending user review
**Target version:** `pyarchinit-mini` 2.2.0-alpha → 2.3.0-alpha
**Target s3dgraphy version:** 0.1.42 (installed in Spec 1)
**Group:** A — s3dgraphy bidirectional sync, Spec 2 of 4

## 1. Overview

This is **Spec 2 of 4** for porting the s3dgraphy bidirectional-sync
architecture to pyarchinit-mini-web. It builds on Spec 1's `VocabProvider`
foundation (merged at `7aba054`) and delivers the **Local Graph & Paradata
layer** — the bidirectional translation between SQL rows and s3dgraphy
graphs, plus the storage for paradata-only node types.

Concretely, Spec 2 introduces:

- `GraphProjector` — `populate_graph()`: DB rows → s3dgraphy.Graph (idempotent)
- `ParadataStore` — owns `data/paradata/<site>/paradata.graphml` per-site, CRUD
  for `AuthorNode`, `LicenseNode`, `EmbargoNode`, `DocumentNode`, `EpochNode`
- `GraphIngestor` — `populate_list()`: s3dgraphy.Graph → DB rows with 2-phase
  preview/apply
- GraphML writer/reader delegate to `s3dgraphy.exporter.graphml` /
  `s3dgraphy.importer.import_graphml` — retiring the 4 in-house writers
- Auto-regen hook on US/USM save → produces merged `stratigraphy.graphml`
- 5 paradata CRUD HTML pages + REST API
- Import GraphML flow with mandatory 2-phase preview

It does **not** cover datacenter sync (`SyncEngine`, `DatacenterClient`,
`ConflictResolver` real-time) or GraphDB backends — those are Specs 3 and 4.

## 2. Context and decisions

### 2.1 Project context (post-Spec 1)

- `pyarchinit_mini.vocab.VocabProvider` is the canonical source of unit types,
  edge types, and visual styles. All 4 modules built in Spec 2 consume it.
- `pyarchinit_mini.s3d_integration.s3d_converter.S3DConverter` is the current
  legacy DB-to-Graph converter (refactored in Spec 1 to use VocabProvider).
  It mixes projection, JSON export, and Heriverse formatting. Spec 2's
  `GraphProjector` replaces its `create_graph_from_us()` method as the
  canonical projection path; the JSON/Heriverse export methods stay (they
  use the projection output downstream).
- `pyarchinit_mini.graphml_converter.{graphml_builder, graphml_exporter,
  pure_networkx_exporter, converter}` are 4 in-house GraphML writers. Per
  the foundational spec §7.6, they are superseded by `s3dgraphy.exporter.graphml`
  and retired with deprecation shims at Spec 2 PR8.
- `pyarchinit_mini.graphml_converter.em_palette` (VocabProvider-backed in
  Spec 1) STAYS — it's a styling helper, not a writer.
- `harris_creator_routes.py` consumes `graphml_builder.GraphMLBuilder` today;
  must be refactored to use the new `graphml_io.writer` at Spec 2 PR8 (no
  shim path for internal consumers).
- pyarchinit-mini-web is multi-user (`flask_login` + `UserRole`); sites are
  shared across users that have access to the same DB.
- `data/paradata/` directory does NOT yet exist; it is created lazily by Spec 2.

### 2.2 Decisions captured during brainstorming

| # | Decision | Value |
|---|---|---|
| D1 | Paradata storage model | **Filesystem per-site** — `data/paradata/<site_slug>/paradata.graphml`. Git-trackable, simple backup, atomic write via tmp + `os.replace` |
| D2 | Paradata UI scope | **Full CRUD pages** — 5 HTML pages (one per node type) + REST API. Not API-only |
| D3 | Graph generation trigger | **Auto-regen on US/USM save** — post-commit hook produces merged `stratigraphy.graphml`. Best-effort, error-isolated (regen fail does NOT block save) |
| D4 | Bulk import handling | `disable_regen()` context manager skips per-row regen; single explicit regen at batch end |
| D5 | GraphIngestor import flow | **Mandatory 2-phase preview** — upload → `preview()` returns `IngestPlan` → diff page → user confirms → `apply()` |
| D6 | GraphIngestor staleness check | `IngestPlan.snapshot_revision` (SHA-256 of relevant DB state) verified at `apply()`; mismatch → 409 + re-render preview |
| D7 | Approach | **Parallel + cutover.** 8 PRs sequential, deprecation shims for old writers, retire at PR8. Mirrors Spec 1 pattern |
| D8 | GraphML writer retirement | All 4 in-house writers deprecated with shim for one release cycle, then removed in Spec 3. `harris_creator_routes` refactored to new writer at PR8 (no shim) |
| D9 | Concurrent edits on paradata | **Last-writer-wins** within Spec 2 (real-time conflict resolution is Spec 3) |
| D10 | Auto-regen failure handling | Logged + cached `regen_status:<site>` = error; banner shown on next page render; save itself returns 201 |

### 2.3 Out of scope (deferred to later specs)

- `SyncEngine`, `DatacenterClient`, `EMBackend` — Spec 3
- `ConflictResolver` real-time UI for concurrent paradata edits — Spec 3
- `GraphDBBackend` (SPARQL) — Spec 4
- `paradata.graphml` versioning / history view — Spec 3
- Background-job worker for large dataset regen (Celery / RQ) — out of band
- `_index.json` driven site rename/delete UI — out of band

## 3. Architecture

Two new packages plus 3 new route modules:

```
pyarchinit_mini/
├── graphproj/                       # NEW — graph projection layer
│   ├── __init__.py
│   ├── projector.py                 # GraphProjector.populate_graph()
│   ├── paradata_store.py            # ParadataStore (per-site filesystem-backed)
│   ├── ingestor.py                  # GraphIngestor.preview() / apply()
│   ├── ingest_plan.py               # IngestPlan / IngestResult / NodePlanEntry
│   ├── edge_registry.py             # Stratigraphic edge type registry
│   ├── filesystem.py                # atomic_write + per-site flock helpers
│   ├── auto_regen.py                # Post-commit hook + disable_regen() context
│   └── exceptions.py
├── graphml_io/                      # NEW — thin wrapper around s3dgraphy
│   ├── __init__.py
│   ├── writer.py                    # Delegates to s3dgraphy.exporter.graphml
│   └── reader.py                    # Delegates to s3dgraphy.importer.import_graphml
└── web_interface/
    ├── graph_routes.py              # NEW — /sites/<site>/graph/{view,download,import-preview,import-apply}
    ├── paradata_routes.py           # NEW — /api/v1/paradata/<site>/... (REST)
    └── paradata_ui_routes.py        # NEW — /paradata/<site>/... (HTML)
```

Flow at-a-glance:

```
Browser
  │
  ├─ Save US/USM ────────► us_service.save_us()
  │                              │ (after commit)
  │                              ▼
  │                          auto_regen._trigger_graph_regen(site)
  │                              ├─► GraphProjector.populate_graph(site)
  │                              ├─► ParadataStore(site).load()
  │                              ├─► s3dgraphy.merge.GraphMerger.merge(...)
  │                              ├─► graphml_io.writer.write(merged, tmp_path)
  │                              └─► os.replace(tmp, stratigraphy.graphml)
  │
  ├─ Paradata CRUD ──────► paradata_ui_routes ──► paradata_routes ──► ParadataStore
  │
  └─ Import GraphML ─────► graph_routes /import-preview
                              ├─► graphml_io.reader.read()
                              ├─► GraphIngestor.preview() → IngestPlan
                              └─► render diff page
                                       └─► (user confirms) /import-apply
                                                ├─► verify snapshot_revision
                                                └─► GraphIngestor.apply(plan)
```

**Constraint:** `pyarchinit_mini.vocab.VocabProvider` is the single canonical
source consulted by every new module for unit-type, edge-type, and family
information. No new hardcoded mappings.

**Constraint:** Old `graphml_converter.*` writers receive deprecation shims
(import works, logs `DeprecationWarning`). Direct internal consumer
`harris_creator_routes.py` is refactored to use `graphml_io.writer` directly.

## 4. Components

### 4.1 `GraphProjector` (pure, no state)

```python
class GraphProjector:
    @staticmethod
    def populate_graph(
        session: Session,
        site: str,
        *,
        area: str | None = None,
    ) -> "s3dgraphy.Graph":
        """DB rows → s3dgraphy.Graph (stratigraphic layer only)."""
```

Idempotent (modulo timestamps). Uses `s3dgraphy.importer.pyarchinit_importer`
as base. Output covers stratigraphic-family nodes + stratigraphic edges
(`is_after`, `covers`, `cuts`, `leans_against`, `has_same_time`, `fills`,
`connected_to`). Does NOT include paradata-only nodes.

Edge typing routes through `pyarchinit_mini.graphproj.edge_registry`, which
wraps `VocabProvider.get_edge_types()` for canonical lookup + Italian alias
parsing.

### 4.2 `ParadataStore` (per-site filesystem-backed)

```python
class ParadataStore:
    def __init__(self, site: str, *, root: Path | None = None) -> None: ...

    def load(self) -> "s3dgraphy.Graph": ...
    def atomic_write(self, graph: "s3dgraphy.Graph") -> None: ...

    # Per node type — same shape × 5
    def list_authors(self) -> list[AuthorNode]: ...
    def add_author(self, name: str, orcid: str | None = None) -> AuthorNode: ...
    def update_author(self, node_id: str, **fields) -> AuthorNode: ...
    def delete_author(self, node_id: str) -> None: ...
    # ... licenses, embargoes, documents, epochs
```

Atomic write protocol: write to `.tmp`, then `os.replace`. Per-site `fcntl.flock`
(`msvcrt` fallback on Windows). Lock held for the load → mutate → write
sequence.

### 4.3 `GraphIngestor` (2-phase: preview, apply)

```python
class GraphIngestor:
    def __init__(self, session: Session, site: str) -> None: ...

    def preview(self, graph: "s3dgraphy.Graph", *, dry_run: bool = True) -> "IngestPlan":
        """Compute what would change. No DB writes.

        Classifies each node:
        - INSERT (no DB match by node_uuid)
        - UPDATE (match, graph node newer or equal)
        - SKIP_LOCAL_NEWER (match, DB row updated_at > graph)
        - SKIP_LOCKED (row protected by another user)
        """

    def apply(self, plan: "IngestPlan") -> "IngestResult":
        """Execute. Transaction-wrapped. Raises IngestStaleError if
        plan.snapshot_revision != current_db_revision(site)."""
```

### 4.4 `IngestPlan` / `IngestResult` (immutable dataclasses)

```python
@dataclass(frozen=True)
class IngestPlan:
    site: str
    snapshot_revision: str             # SHA-256 of relevant DB rows
    inserts: tuple[NodePlanEntry, ...]
    updates: tuple[NodePlanEntry, ...]
    skips_local_newer: tuple[NodePlanEntry, ...]
    skips_locked: tuple[NodePlanEntry, ...]

@dataclass(frozen=True)
class NodePlanEntry:
    node_uuid: str
    unit_type: str
    semantic_id: str                   # "pyarchinit:site=X/us=N"
    before: dict | None                # current DB row (None for INSERT)
    after: dict                        # what would be written
    reason: str                        # "new", "graph_newer", "tie", ...

@dataclass(frozen=True)
class IngestResult:
    plan: IngestPlan
    inserted: int
    updated: int
    skipped: int
    errors: tuple[str, ...]
```

### 4.5 `graphml_io.writer` / `graphml_io.reader`

```python
def write_graphml(graph: "s3dgraphy.Graph", path: Path) -> None:
    """Delegates to s3dgraphy.exporter.graphml."""

def read_graphml(path: Path) -> "s3dgraphy.Graph":
    """Delegates to s3dgraphy.importer.import_graphml."""
```

Exact 0.1.42 API resolved at implementation time. Wrapper exists for stable
internal call site (allows future s3dgraphy version bumps without touching
consumers).

### 4.6 `auto_regen` hook

```python
def _trigger_graph_regen(site: str, *, session) -> None:
    """Best-effort post-commit regen. Errors logged, never raised."""

@contextmanager
def disable_regen() -> Iterator[None]:
    """Thread-local flag suppresses per-row regen during bulk operations."""

def force_regen_all_touched_sites() -> None:
    """Manually triggers regen for all sites touched within the most recent
    disable_regen context. Called at end of bulk import."""
```

Modification to `pyarchinit_mini/services/us_service.py`: after
`session.commit()`, call `_trigger_graph_regen(us.sito, session=session)`.

Escape hatch: env var `PYARCHINIT_DISABLE_AUTO_REGEN=1` → no-op.

### 4.7 Deprecation map (PR8)

| Old API | Shim | Removed |
|---|---|---|
| `graphml_converter.graphml_builder.GraphMLBuilder` | Property wrapper around `graphml_io.writer` + `DeprecationWarning` | Spec 3 |
| `graphml_converter.graphml_exporter.*` | Same | Spec 3 |
| `graphml_converter.pure_networkx_exporter.*` | Same | Spec 3 |
| `graphml_converter.converter.*` | Same | Spec 3 |

`harris_creator_routes.py` refactored at PR8 to call `graphml_io.writer`
directly (no shim).

### 4.8 Paradata REST API (PR5)

```
GET    /api/v1/paradata/<site>/{authors,licenses,embargoes,documents,epochs}
POST   /api/v1/paradata/<site>/{type}                body: {name, ...}
GET    /api/v1/paradata/<site>/{type}/<id>
PUT    /api/v1/paradata/<site>/{type}/<id>           body: {fields...}
DELETE /api/v1/paradata/<site>/{type}/<id>
```

All endpoints `flask_login`-protected. Audit entry per write to
`data/paradata/<site_slug>/audit.log` (JSON-line).

### 4.9 Paradata UI pages (PR6)

5 pages under `/paradata/<site>/{authors,licenses,embargoes,documents,epochs}`:

- List page: table + "New" modal-trigger button
- Edit page: form with current values
- Delete: confirmation dialog
- Bootstrap-styled, consistent with existing pyarchinit-mini-web pages

### 4.10 Graph routes (PR3 + PR7)

```
GET    /sites/<site>/graph/view              ─ HTML viewer (renders graphml inline)
GET    /sites/<site>/graph/download          ─ Content-Disposition: attachment
GET    /sites/<site>/graph/import            ─ upload form
POST   /sites/<site>/graph/import-preview    ─ multipart upload → diff page
POST   /sites/<site>/graph/import-apply      ─ confirm plan_id → apply + result
```

## 5. Data flow

### 5.1 Save US with auto-regen

```
POST /us {sito: "Volterra", us: 24, ...}
  → us_service.save_us()
    → session.add(US(**payload))
    → session.commit()                     ◄─── 201 OK valid here
  → auto_regen._trigger_graph_regen("Volterra", session)
    → flock per-site
    → GraphProjector.populate_graph()
    → ParadataStore.load()
    → s3dgraphy.merge.GraphMerger.merge()
    → graphml_io.writer.write(merged, .tmp)
    → os.replace(.tmp, stratigraphy.graphml)
    → unlock
  → cache.set("regen_status:Volterra", {"status": "ok"})
  → return 201
```

On any error: caught, logged, cache `{"status": "error", "msg": "..."}`,
save still returns 201.

### 5.2 Bulk excel import

```
POST /excel-import (file=hundreds_of_rows.xlsx)
  → with auto_regen.disable_regen():
      for row in parsed_excel:
          us_service.save_us(row, session)   ◄─── auto_regen no-ops
  → (context exit)
  → auto_regen.force_regen_all_touched_sites()
                                             ◄─── exactly 1 regen per touched site
```

### 5.3 Paradata CRUD (create AuthorNode)

```
POST /api/v1/paradata/Volterra/authors {name: "M. Rossi", orcid: "0000-..."}
  → enforce auth
  → ParadataStore("Volterra").add_author(...)   ◄─── flock + load + mutate + atomic_write
  → audit_log("paradata.author.create", user, target=node_id)
  → trigger regen
  → 201 + JSON
```

### 5.4 Import GraphML (preview + apply)

```
POST /sites/Volterra/graph/import-preview (file=upload.graphml)
  → save to data/paradata/volterra/imports/<uuid>.graphml
  → graph = graphml_io.reader.read(upload_path)
  → plan = GraphIngestor(session, "Volterra").preview(graph)
  → store plan in Flask session under key "import_plan:Volterra:<uuid>"
  → render templates/graph_import_preview.html (tables: inserts/updates/skips)

POST /sites/Volterra/graph/import-apply {plan_id}
  → retrieve plan from session
  → verify plan.snapshot_revision == current_db_revision("Volterra")
    → if stale → 409 + re-render preview
  → result = ingestor.apply(plan)
  → trigger regen
  → delete imports/<uuid>.graphml
  → render templates/graph_import_result.html
```

### 5.5 Regen status banner

```
Any page render (base template)
  → status = cache.get(f"regen_status:{current_site}")
  → if status.status == "error":
      render <div class="alert alert-warning">Graph regen failed: {msg} [Retry]</div>
```

## 6. Storage layout

```
data/paradata/
├── _index.json                          # site_slug → site_name canonical mapping
├── _regen.log                           # global JSON-line regen log (rotating 5×2MB)
├── _metrics.sqlite                      # local telemetry (admin diagnostics only)
├── <site_slug>/
│   ├── paradata.graphml                 # paradata-only nodes (committed to git)
│   ├── stratigraphy.graphml             # merged output (NOT in git, derived)
│   ├── stratigraphy.graphml.tmp         # transient
│   ├── .paradata.lock                   # flock file
│   ├── audit.log                        # JSON-line per CRUD op (committed)
│   └── imports/
│       └── <uuid>.graphml               # transient upload, GC'd after 1h
└── volterra/                            # example
    ├── paradata.graphml
    └── stratigraphy.graphml
```

**Git tracking:**
- `paradata.graphml`, `audit.log`, `_index.json` → committed (human input)
- `stratigraphy.graphml`, `*.tmp`, `imports/*`, `.paradata.lock`, `_regen.log`,
  `_metrics.sqlite` → `.gitignore`d (derived/transient)

**Atomic write:**
```python
tmp = target.with_suffix(target.suffix + ".tmp")
tmp.write_text(content, encoding="utf-8")
tmp.replace(target)  # POSIX rename: atomic on same filesystem
```

**Per-site flock** with cross-platform fallback (`fcntl` POSIX, `msvcrt`
Windows). Held for full load → mutate → write sequence. 30s timeout
followed by force-acquire (last-resort, logged).

**Lazy migration:** `data/paradata/` and per-site dirs created on first need.
No explicit migration script.

**Disk footprint estimate:** Volterra-scale (~1500 US, 20 authors, 50 docs,
30 epochs) → ~2.1 MB per site. 50-site instance → ~25 MB total. No quotas
enforced in Spec 2.

## 7. Error handling

Guiding principle: **graph-layer errors never block US save or page render**.
Spec 2 is additive to existing flow.

### 7.1 Auto-regen failures

All errors caught in `_trigger_graph_regen`, logged, status cached, **save
still returns 201**. UI shows banner on next render. Escape hatch:
`PYARCHINIT_DISABLE_AUTO_REGEN=1`.

### 7.2 GraphProjector errors

| Case | Strategy |
|---|---|
| Legacy `unita_tipo` (USVA/USVB/USVC) post-migration missing | Processed with `family="unknown"`, warning logged |
| `node_uuid` NULL | UUID v7 generated for projection only (does NOT write to DB; Spec 1 migration handles persisted upgrade) |
| Malformed `rapporti` | Single relation skipped, node kept, warning logged |
| Site missing | `ProjectionError` |

### 7.3 ParadataStore errors

| Case | HTTP |
|---|---|
| Duplicate node_id | 409 + `{"error": "duplicate", "existing": {...}}` |
| Not found on PUT/DELETE | 404 |
| Validation (missing required field) | 400 |
| Filesystem unavailable | 500 + log |
| Corrupted GraphML on load | 500 + log; **no auto-recovery** |

### 7.4 GraphIngestor errors

| Case | Strategy |
|---|---|
| Malformed GraphML upload | Preview page shows error + "Upload another" |
| Plan stale (DB changed between preview and apply) | 409 + re-render preview with new state |
| Partial apply failure | Full transaction rollback; `IngestResult.errors` populated |
| Unsupported node type in graph | Skip silently with log; counted in skipped |

### 7.5 Concurrent paradata edits (Spec 2 policy)

**Last-writer-wins.** Real-time conflict resolution is Spec 3. Double-delete
is idempotent (second DELETE returns 404 → treated as success in UI).

### 7.6 Logging channels

| Channel | Content | Level |
|---|---|---|
| Python `logging` (`pyarchinit_mini.graphproj`) | Bootstrap, regen events, errors | INFO/WARNING/ERROR |
| `data/paradata/<site>/audit.log` (JSON-line) | Each paradata CRUD: ts, user, op, target, ip | always |
| `data/paradata/_regen.log` (JSON-line, rotated 5×2MB) | Each regen: ts, site, status, duration_ms, nodes, edges | always |
| Flask header `X-Graph-Status` | `ok` / `degraded` on site pages | — |
| Flask cache `regen_status:<site>` | Last regen result (TTL 24h) | — |

### 7.7 Validation gates

| Gate | Where |
|---|---|
| `unita_tipo` valid | DTO via VocabProvider (Spec 1) |
| Paradata CRUD payload | `paradata_routes` validators |
| Site slug | `_slugify(site)` ascii-only, non-empty (prevents path traversal) |
| Upload size | `MAX_CONTENT_LENGTH = 50 MB` |
| GraphML mime/extension | `.graphml` or `.xml` |

### 7.8 Local telemetry (no external)

`data/paradata/_metrics.sqlite`: regen_count, regen_p50/p95/p99,
ingest_count by outcome, paradata_op_count by type. Surfaced in
`/api/v1/graphproj/diagnostics` (admin-only). **Nothing sent externally.**

## 8. Testing strategy

### 8.1 Pyramid

| Level | Target | Coverage |
|---|---|---|
| Unit | ~75 | All 4 graphproj modules + IngestPlan/Result + filesystem helpers + edge_registry + writer/reader + exceptions |
| Integration | ~30 | Flask routes, auto-regen end-to-end, bulk-import debounce, lock contention, paradata CRUD chains |
| E2E | ~6 | Save US → graph file appears; import flow round-trip; paradata UI CRUD; harris_creator regression; bulk excel import + single regen; concurrent save smoke |

Framework: pytest (existing). New deps: none (`freezegun` from Spec 1).

### 8.2 Fixtures

```
tests/fixtures/
├── databases/
│   ├── sqlite_volterra_30us.db
│   ├── sqlite_with_legacy_vocab.db
│   └── sqlite_empty_site.db
├── paradata_graphmls/
│   ├── empty_paradata.graphml
│   ├── volterra_paradata_seeded.graphml      # 3 authors, 1 license, 2 documents
│   └── corrupt_paradata.graphml              # malformed XML
├── ingest_uploads/
│   ├── new_us_only.graphml
│   ├── update_existing.graphml
│   ├── skip_local_newer.graphml
│   └── mixed.graphml
└── graphml_outputs/                            # parity baselines
    ├── volterra_baseline_old_writer.graphml
    └── volterra_target_new_writer.graphml
```

DB fixtures synthetic, regenerable via `tests/fixtures/_generate_volterra_synthetic.py`.

### 8.3 Critical tests

**1. Auto-regen integration** — `test_auto_regen_on_save.py`
- Save US → graph file appears within 100ms
- Save US on site without paradata.graphml → empty paradata created
- Save US fails (DB error) → auto_regen NOT fired
- Auto_regen fails → save still returns 201; cache marked error

**2. Bulk import debounce** — `test_bulk_import_single_regen.py`
- 100 US import within `disable_regen()` → no per-row regen
- After context exit, 1 regen per touched site

**3. Concurrent saves serialize** — `test_concurrent_saves_serialize.py`
- 4 threads save US same site → final graphml reflects all 4
- No `.tmp` files left
- Flock prevents interleaved writes

**4. Ingest preview/apply staleness** — `test_ingest_preview_stale.py`
- A: preview → IngestPlan in session
- B: save US (changes snapshot)
- A: apply → 409 + new preview re-rendered

**5. GraphML writer parity** — `test_graphml_writer_parity.py` (PR2 gate)
- Old `GraphMLBuilder` vs new `graphml_io.writer` on same DB
- XML diff: differences allowed only on new attrs / ordering; never on id/label/style/edges

**6. Paradata CRUD HTML round-trip** — `test_paradata_ui_crud.py`
- GET list → empty
- POST form → 302 → list contains new entry
- Edit, delete, verify

**7. Harris matrix regression** — `test_harris_matrix_post_cutover.py` (PR8 gate)
- Pre-PR8 baseline → post-PR8 diff: standard node styles preserved

### 8.4 CI matrix

| OS | Python | Storage |
|---|---|---|
| macOS Sequoia | 3.13 | SQLite + filesystem |
| Ubuntu 24.04 | 3.13 + 3.12 | SQLite + PG (Docker) + filesystem |
| Windows 11 | 3.13 | SQLite + filesystem (`msvcrt` lock fallback) |

Windows-specific test `test_filesystem_windows_lock.py` (skipif other OS).

## 9. Definition of Done

- All unit + integration tests green on CI matrix
- GraphML writer parity test green (zero diff on standard attributes)
- Auto-regen integration green on SQLite + PG
- Harris matrix regression green (PR8 gate)
- Bulk import debounce green (1 regen per site, not N)
- CHANGELOG bilingual IT+EN
- Version bumped `2.2.0-alpha → 2.3.0-alpha`
- `README.md` gets new "Graph projection & paradata" section
- `docs/PARADATA_GUIDE.md` (user) — what the 5 paradata node types are, how to create them
- `docs/GRAPH_AUTO_REGEN.md` (dev) — how the hook works, how to disable
- 8 PRs merged in order: PR1 graphproj module → PR2 writer delegate +
  shims → PR3 auto-regen hook → PR4 GraphIngestor + preview API → PR5
  paradata REST API → PR6 paradata UI pages → PR7 graph routes UI →
  PR8 retire old writers + harris_creator refactor + docs + release

## 10. Implementation phasing

This is Spec 2 of 4 for Group A:

| Spec | Scope | Depends on |
|---|---|---|
| **1 (merged at `7aba054`)** — Web Foundation | VocabProvider + vocab endpoints + em_palette / s3d_converter cutover + DB migrations + DTO validator + retire of hardcoded mappings | — |
| **2 (this doc)** — Local Graph & Paradata | GraphProjector, ParadataStore, GraphIngestor, GraphML writer delegate, auto-regen hook, 5 paradata CRUD pages, import preview/apply flow | Spec 1 |
| **3** — Sync Engine + EM Backend | SyncEngine as Flask background worker, DatacenterClient with EMBackend (REST), offline queue (sqlite), ConflictResolver web UI, multi-user sync ownership, real-time concurrent edit resolution | Spec 1 + 2 + EM Datacenter API |
| **4** — GraphDB Backend | GraphDBBackend implementing same interface as Spec 3, SPARQL transport | Spec 1 + 2; parallel to Spec 3 |

## 11. Open questions (deferred, non-blocking for Spec 2)

1. Real-time conflict resolution UI when User A and User B edit same
   AuthorNode simultaneously → Spec 3 (ConflictResolver)
2. `paradata.graphml` versioning / history view → Spec 3 (or out of band)
3. `SyncEngine` push/pull to EM Datacenter → Spec 3
4. `GraphDBBackend` SPARQL → Spec 4
5. `GraphMerger` user-customizable merge policy → Spec 3
6. Site rename/delete UI → out of band
7. Background-job worker (Celery / RQ) for large dataset regen → out of band

## 12. References

- **Foundational design (QGIS plugin):**
  `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md`
- **QGIS plugin sync directory (reference impl):**
  `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/s3dgraphy/sync/`
  - `graph_projector.py`, `paradata_store.py`, `graph_ingestor.py`,
    `graphml_writer.py`, `ingest_result.py`, `edge_registry.py`
- **Spec 1 (merged):**
  `docs/superpowers/specs/2026-05-16-s3dgraphy-web-foundation-design.md`
- **Spec 1 plan:**
  `docs/superpowers/plans/2026-05-16-s3dgraphy-web-foundation.md`
- **s3dgraphy 0.1.42** modules: `exporter.graphml`, `importer.import_graphml`,
  `merge.GraphMerger`, `importer.pyarchinit_importer`
- **QGIS plugin dev log:**
  `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`
