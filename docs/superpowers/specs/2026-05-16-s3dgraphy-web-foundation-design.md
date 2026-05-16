# PyArchInit-Mini Web ↔ s3dgraphy — Spec 1: Web Foundation (VocabProvider + DB migration)

**Spec date:** 2026-05-16
**Author:** Enzo Cocca (with brainstorming session)
**Status:** Design proposal — pending user review
**Target version:** `pyarchinit-mini` 2.1.68 → 2.2.0-alpha
**Target s3dgraphy version:** 0.1.42 (currently installed in `.venv`: 0.1.15)
**Group:** A — s3dgraphy bidirectional sync, Spec 1 of 4

## 1. Overview

This is **Spec 1 of 4** for porting the s3dgraphy bidirectional-sync
architecture from the PyArchInit QGIS plugin (`Stratigraph_00001` branch) to
**pyarchinit-mini-web**. The target architecture is the same full bidirectional
bridge designed for QGIS — see the foundational design at
`~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md`.

This document covers the **Foundation phase**: making pyarchinit-mini-web
consume the s3dgraphy JSON catalogues as the canonical source for unit types,
edge types, and visual styles; aligning existing data with current EM 1.5.4
vocabulary; introducing the `node_uuid` column required by future sync work.

It does **not** cover graph projection, paradata stores, datacenter sync, or
GraphDB backends — those are Specs 2, 3, and 4.

## 2. Context and decisions

### 2.1 Project context

- pyarchinit-mini-web is a Flask web application with multi-user support
  (`User` + `UserRole` + per-DB connections via `data/connections.json`).
- Today, `unita_tipo` is a free-form `Column(String(200))` on `us_table` —
  no enum, no validation, no link to s3dgraphy.
- `pyarchinit_mini/s3d_integration/s3d_converter.py` contains hardcoded
  Italian→English relationship mappings and a hardcoded `unit_type`
  categorization table.
- `pyarchinit_mini/graphml_converter/em_palette.py` contains a hardcoded
  `PALETTE` dict with an existing YAML override system
  (`config/em_node_config_manager.py`), used by the Harris matrix viewer.
- s3dgraphy is installed via pip in `.venv` at version 0.1.15 — predates
  the JSON pillar naming convention (`em_connection_rules.json` instead of
  `s3Dgraphy_connections_datamodel.json`) and ships one file with a
  filename quirk (a space: `s3Dgraphy_node_datamodel .json`).

### 2.2 Decisions captured during brainstorming

| # | Decision | Value |
|---|---|---|
| D1 | Target architecture | Full bidirectional bridge (same scope as QGIS), implemented over 4 specs |
| D2 | Web priority | Spec components designed for the Flask app first; desktop GUI follows. QGIS-specific abstractions (QThread, QFileSystemWatcher, QSettings, Qt dialogs) replaced with Flask-native equivalents |
| D3 | Vocab override scope | **None in Spec 1.** Only bundled s3dgraphy JSONs are read; override mechanisms deferred |
| D4 | Approach | **Parallel + cutover.** Introduce VocabProvider alongside existing code; switch consumers one at a time; retire old code at end of Spec 1 |
| D5 | s3dgraphy target | 0.1.42, bumped in `pyproject.toml`. Old version (0.1.15) supported only via fallback loader with deprecation warning |
| D6 | Harris Matrix Creator | Must consume new system (visual styles from `em_visual_rules.json` via VocabProvider) by end of PR3 |
| D7 | UUID strategy | UUID v7 (time-ordered), generated Python-side for SQLite + PostgreSQL consistency. New dependency: `uuid7>=0.1.0` |
| D8 | Vocab alignment | One-shot migration `USVA, USVB → USVs`, `USVC → USVn`. Legacy values accepted with deprecation warning post-migration to support partial-migration deployments |
| D9 | Migration tooling | Custom scripts under `pyarchinit_mini/database/migrations/` (no Alembic — matches existing pattern in `migration_scripts/`) |
| D10 | DB backup before migration | Mandatory (`--apply` requires successful backup first); SQLite via file copy + SHA-256; PostgreSQL via `pg_dump -Fc` |

### 2.3 Out of scope (deferred to later specs)

- `GraphProjector` (`populate_graph`) — Spec 2
- `ParadataStore` (`paradata.graphml` per project) — Spec 2
- `GraphIngestor` (`populate_list`) — Spec 2
- `SyncEngine`, `DatacenterClient`, `ConflictResolver` — Spec 3
- `GraphDBBackend` (SPARQL) — Spec 4
- Vocab override mechanism (filesystem or DB-backed) — Spec 2 if needed
- `QFileSystemWatcher`-equivalent hot reload — Spec 2 if needed
- Refactor of any module outside the components listed in §4.5

## 3. Architecture

A new package `pyarchinit_mini/vocab/` introduces the central `VocabProvider`
singleton. Three new Flask endpoints expose vocab data to the browser. Existing
modules (`em_palette`, `s3d_converter`, DTO validators) are refactored to read
from `VocabProvider` instead of hardcoded tables. Three DB migrations align
existing data and introduce the `node_uuid` column required for future sync.

```
Browser (forms, harris UI)
        │
        ▼
Flask routes (web_interface/*.py)
        │      ┌─────────────────────────────┐
        ├─────►│ NEW: vocab_routes           │
        │      │ /api/v1/vocab/unit-types    │ ──► VocabProvider
        │      │ /api/v1/vocab/edge-types    │      (singleton, cached)
        │      │ /api/v1/vocab/visual-style  │      │
        │      │ /api/v1/vocab/diagnostics   │      ├──► s3dgraphy JSONs
        │      └─────────────────────────────┘      │     (via importlib.resources)
        ▼                                           │
Existing routes (harris_creator, app, ...)         │
        │                                           │
        ▼                                           │
DTOs + Services  ──────────────────────────────────►│ (validation)
        │                                           │
        ▼                                           │
SQLAlchemy models  ────► DB                         │
                                                    │
graphml_converter/em_palette ──────────────────────►│ (visual styles)
harris_matrix/matrix_visualizer ───────────────────►│
s3d_integration/s3d_converter ─────────────────────►│ (edge & node typing)
```

**Persistence behaviour:** VocabProvider has no DB tables. State is read-only,
cached in-process, invalidated only by Flask restart (after `pip upgrade s3dgraphy`
or admin action).

**Multi-tenancy:** VocabProvider is process-global — all users see the same
vocab (the s3dgraphy version installed in the deployment).

## 4. Components

### 4.1 `vocab/provider.py` — singleton, thread-safe

```python
class VocabProvider:
    _instance: "VocabProvider | None" = None
    _lock = threading.Lock()

    @classmethod
    def instance(cls) -> "VocabProvider": ...
    @classmethod
    def reset(cls) -> None: ...  # test-only

    def get_unit_types(self, lang: str = "en") -> list[UnitType]: ...
    def get_unit_type(self, abbreviation: str, lang: str = "en") -> UnitType | None: ...
    def get_edge_types(self, lang: str = "en") -> list[EdgeType]: ...
    def get_legal_edges(self, source_type: str, target_type: str) -> list[EdgeType]: ...
    def get_visual_style(self, unit_type: str) -> VisualStyle: ...
    def get_cidoc_mapping(self, unit_type: str) -> str | None: ...

    def s3dgraphy_version(self) -> str: ...
    def data_model_versions(self) -> dict[str, str]: ...
    def diagnostics(self) -> dict[str, Any]: ...
```

Thread-safe first access via double-checked locking. `reset()` exists for tests
only and emits a warning if called in non-test process.

### 4.2 `vocab/types.py` — immutable dataclasses

```python
@dataclass(frozen=True)
class UnitType:
    abbreviation: str          # "US", "USVs", "RSF"
    class_name: str            # "StratigraphicUnit"
    parent: str | None         # "StratigraphicNode"
    label: str                 # localized via i18n
    description: str           # localized via i18n
    symbol: str                # textual hint from datamodel JSON ("white rectangle")
    family: str | None         # "real" | "virtual" | None
    is_series: bool
    cidoc_mapping: str | None
    properties: dict[str, str] # CIDOC property mapping per the datamodel
    visual_style: VisualStyle  # joined from em_visual_rules.json

@dataclass(frozen=True)
class VisualStyle:
    shape: str                 # "rectangle" | "parallelogram" | "hexagon" | "octagon"
    fill_color: str            # "#F0F0F0"
    border_color: str          # "#540909"
    border_style: str          # "solid" | "dashed"
    border_width: float = 3.0
    text_color: str = "#000000"
    font_family: str = "DialogInput"
    font_size: int = 24
    font_style: str = "bold"
    label_position: str = "over"
    file_2d_raster: str | None = None  # relative path inside s3dgraphy package
    file_2d_vector: str | None = None
    file_3d: str | None = None
    material_rgba: tuple[float, float, float, float] | None = None

    @classmethod
    def fallback(cls) -> "VisualStyle":
        """Returned for unknown unit types — neutral grey rectangle."""

@dataclass(frozen=True)
class EdgeType:
    name: str                  # "is_after", "covers", "cuts"
    label: str                 # localized
    italian_aliases: tuple[str, ...]  # ("copre", "coperto da", ...) — for legacy text parsing
    symmetric: bool
    legal_pairs: tuple[tuple[str, str], ...]  # ((source_type, target_type), ...)
```

### 4.3 `vocab/loader.py` — resilient JSON loading

```python
def load_node_datamodel() -> NodeDatamodel: ...
def load_connections_datamodel() -> ConnectionsDatamodel: ...
def load_visual_rules() -> VisualRulesDatamodel: ...
```

Loader behaviour:
- Resolves files via `importlib.resources.files("s3dgraphy") / "JSON_config"`.
- Tries the canonical name first
  (`s3Dgraphy_node_datamodel.json`,
  `s3Dgraphy_connections_datamodel.json`,
  `em_visual_rules.json`).
- **Filename quirk:** falls back to `s3Dgraphy_node_datamodel .json` (with
  literal space) if canonical name not found. Logs a single warning.
- **Legacy naming:** for s3dgraphy < 0.1.30, falls back to
  `em_connection_rules.json` for the connections pillar. Behaviour gated by
  flag `--allow-old-s3dgraphy` (env: `PYARCHINIT_ALLOW_OLD_S3D=1`); otherwise
  raises `VocabBootstrapError`.
- Malformed JSON raises `VocabSchemaError(path, line, column, msg)`.
- Missing pillar raises `VocabBootstrapError` with actionable upgrade hint.

### 4.4 `vocab/i18n.py` — translations layer

Custom JSON-catalogue loader, **separate** from `flask_babel` (which keeps
translating regular UI strings). Vocab translations live at
`pyarchinit_mini/vocab/translations/vocab_<lang>.json`:

```json
{
  "unit_types": {
    "US": {"label": "US", "description": "Unità Stratigrafica..."},
    "USVs": {"label": "USV strutturale", "description": "..."}
  },
  "edge_types": {
    "covers": {"label": "copre"},
    "cuts": {"label": "taglia"}
  }
}
```

Missing translation → English fallback + response header
`X-Translation-Missing: it,USVs,USVn`. Logged once per process.

### 4.5 `web_interface/vocab_routes.py` — Flask blueprint

```python
vocab_bp = Blueprint("vocab", __name__, url_prefix="/api/v1/vocab")

@vocab_bp.get("/unit-types")        # ?lang=it&family=real
@vocab_bp.get("/unit-types/<abbr>")
@vocab_bp.get("/edge-types")        # ?lang=it&source_type=US&target_type=US
@vocab_bp.get("/visual-style/<unit_type>")
@vocab_bp.get("/diagnostics")       # admin-only
```

All endpoints emit ETag from VocabProvider state hash. Default cache 1h.
ETag changes only on Flask restart (i.e. on `pip upgrade s3dgraphy` deployment).

### 4.6 Consumer integration map

| File | Refactor | PR# |
|---|---|---|
| `graphml_converter/em_palette.py` | `EMPalette.get_style(unit_type)` reads from `VocabProvider.get_visual_style()`. `PALETTE` dict marked `# DEPRECATED Spec 1 PR8` | PR3 |
| `harris_matrix/matrix_visualizer.py`, `enhanced_visualizer.py`, `pyarchinit_visualizer.py` | No direct changes — consume EMPalette transitively | — |
| `web_interface/harris_creator_routes.py` | Hardcoded `'US'` fallbacks → `VocabProvider.get_unit_type("US")` | PR3 |
| `web_interface/app.py`, `excel_import_routes.py`, `three_d_builder_routes.py` | Form selects populated via vocab endpoint; `unita_tipo` validated on submit | PR4 |
| `s3d_integration/s3d_converter.py` | `relationship_mapping` dict deleted; replaced by `EdgeType.italian_aliases` lookup. Unit categorization (`USVA`/`USVB`/`USVC` if-else) deleted; replaced by `UnitType.family` + `class_name` | PR5 |
| `dto/us_dto.py` | Validator on `unita_tipo`: must exist in `VocabProvider.get_unit_types()` OR be a legacy value `{USVA, USVB, USVC}` with deprecation warning | PR7 |
| `models/us.py` | No column type change — `String(200)` retained, validation lives in DTO/service | — |

### 4.7 Migration scripts

| Script | Purpose | Idempotent | Reversible |
|---|---|---|---|
| `migrations/2026_05_node_uuid_schema.py` | `ALTER TABLE us_table ADD COLUMN node_uuid TEXT` on `us_table`, `inventario_materiali_table`, `periodizzazione_table`. Creates `UNIQUE INDEX` per table | Yes | Yes (SQLite ≥ 3.35; PG always) |
| `migrations/2026_05_node_uuid_backfill.py` | `UPDATE … SET node_uuid = uuid7()` batched at 1000 rows per transaction | Yes | Partial (reverse only with backup) |
| `migrations/2026_05_vocab_alignment.py` | `USVA, USVB → USVs`; `USVC → USVn` on `us_table.unita_tipo` | Yes | Via backup |
| `migrations/2026_05_paradata_bootstrap.py` (optional) | Creates `data/paradata/` directory placeholder for Spec 2 | N/A | N/A |

Backup module: `database/migrations/backup.py` with `BackupRecord` catalogued
in `data/backups/_index.json`.

### 4.8 CLI entry-point

```bash
pyarchinit-mini-migrate-vocab --dry-run
pyarchinit-mini-migrate-vocab --apply
pyarchinit-mini-migrate-vocab --rollback
pyarchinit-mini-migrate-vocab --list-backups
pyarchinit-mini-migrate-vocab --database <url>   # target specific DB
pyarchinit-mini-migrate-vocab --only-default     # skip saved connections
pyarchinit-mini-migrate-vocab --script <name>    # run a single script (advanced)
```

`--apply` (no `--script`) always runs all 4 scripts in the order defined
in §6.5; `--script` is reserved for advanced rerun of a single step (e.g.
re-running `vocab_alignment` after manual fixes).

Discovery order: `DATABASE_URL` (default app) → `data/connections.json` →
`--database` flag.

Lock file `data/.migration_lock` (PID + timestamp) prevents concurrent
`--apply` runs.

### 4.9 Deprecation shims

| Old API | Shim | Removed in |
|---|---|---|
| `EMPalette.PALETTE['US']` | Property recomputes from VocabProvider on access + `DeprecationWarning` | Spec 2 |
| `s3d_converter.relationship_mapping` (if imported externally) | Property logs warning + returns dict generated at runtime | Spec 2 |
| `unita_tipo = "USVA"` on new record post-migration | DTO accepts + warns + suggests `USVs` | Spec 2 |

## 5. Data flow

### 5.1 Flask bootstrap

```
Flask app start
  → from pyarchinit_mini.vocab import VocabProvider
  → VocabProvider.instance()
    → loader.load_node_datamodel()
    → loader.load_connections_datamodel()
    → loader.load_visual_rules()
    → build cache
  → register vocab_bp on /api/v1/vocab
  → log: "VocabProvider ready: 27 unit types, 36 edge types, 22 visual styles. s3dgraphy 0.1.42"
  → if missing pillar / malformed → Flask fails to start with actionable error
```

### 5.2 Form render (US/USM creation/edit)

```
Browser GET /us/new
  → template us_form.html
  → <select data-vocab="unit-types"></select>
  → JS GET /api/v1/vocab/unit-types?lang=it&family=real
    → vocab_routes
    → VocabProvider.get_unit_types(lang="it", family="real")
    → 200 [{"abbreviation":"US","label":"US","description":"…"}, ...]
  → <select> populated; ETag-cached 1h
```

### 5.3 Form submit + validation

```
Browser POST /us {unita_tipo: "USVs", us: 24, …}
  → USDto.from_form(payload)
    → field validator unita_tipo:
      → VocabProvider.get_unit_type("USVs")
      → found → OK
      → not found AND legacy → accept + log warning
      → not found AND not legacy → ValidationError
  → service.save(us_model) → DB INSERT → 201
```

### 5.4 Harris matrix render

```
Browser GET /harris-creator?site=Volterra
  → matrix_generator.build_graph_from_db(site=Volterra)
    → for each US row:
      → style = VocabProvider.get_visual_style(us.unita_tipo or "US")
      → graphml_builder.add_node(id, label, style=style)
  → graphml_builder.serialize() → uploads/graphml/Volterra_stratigraphy.graphml
  → render template
```

**Parity contract:** for standard types (`US`, `SU`, `WSU`) the generated
GraphML is byte-equivalent to the pre-PR3 output modulo colour deltas
documented in `tests/fixtures/graphml_outputs/`. New types
(`USVs`, `USVn`, `RSF`) get correct styles for the first time.

### 5.5 Migration run

```
$ pyarchinit-mini-migrate-vocab --dry-run
  → discover DBs (DATABASE_URL + connections.json + CLI flags)
  → for each DB:
    → count USVA/USVB/USVC rows
    → count rows with NULL node_uuid per migrated table
  → print report
  → no mutations

$ pyarchinit-mini-migrate-vocab --apply
  → confirmation prompt
  → backup each DB (SQLite cp / PG pg_dump)
  → run schema migration in transaction
  → run UUID backfill in batches of 1000
  → run vocab alignment in transaction
  → write data/migration.log
  → print summary

$ pyarchinit-mini-migrate-vocab --rollback
  → list available backups
  → confirmation prompt
  → restore each DB from backup
```

### 5.6 s3dgraphy upgrade

```
$ pip install --upgrade s3dgraphy==0.1.43
$ systemctl restart pyarchinit-mini
  → Flask bootstrap (5.1)
  → VocabProvider re-instantiated, new types/styles picked up
  → no DB migration required between minor s3dgraphy releases
```

## 6. Migration strategy

### 6.1 SQLite vs PostgreSQL

| Aspect | SQLite | PostgreSQL |
|---|---|---|
| `ALTER TABLE ADD COLUMN` | ≥3.2.0 | yes |
| `DROP COLUMN` (rollback) | ≥3.35.0 (2021) — error if older | yes |
| UUID v7 generation | Python-side via `uuid7` lib | Python-side (consistency) |
| Unique index on nullable | yes | yes (multiple NULL allowed during backfill) |
| Backup | `cp data/<db>.db data/<db>.db.pre_vocab_alignment_<ts>` | `pg_dump -Fc <db> > data/backups/<db>.pre_<ts>.dump` |

### 6.2 Backup mechanics

```python
@dataclass
class BackupRecord:
    original_url: str
    backup_path: Path
    timestamp: datetime
    size_bytes: int
    checksum: str  # SHA-256 for restore integrity check
```

Catalogued in `data/backups/_index.json`. `--list-backups` reads this file.

### 6.3 Concurrency

| Scenario | Behaviour |
|---|---|
| `--apply` while Flask running | Warning suggests `--stop-app`. SQLite: `BEGIN IMMEDIATE` + 3 retries on `SQLITE_BUSY`. PG: `ACCESS EXCLUSIVE` lock blocks queries briefly |
| Interrupted `--apply` re-run | Idempotent — resumes via `node_uuid IS NULL` filter + column-existence check |
| Two admins run `--apply` simultaneously | File lock `data/.migration_lock` rejects second |

### 6.4 Migration log

Append-only JSON-line at `data/migration.log`:

```json
{"ts":"2026-05-16T14:23:01Z","script":"node_uuid_backfill","db":"data/pyarchinit_mini.db","table":"us_table","rows_updated":1240,"duration_ms":342,"status":"ok"}
{"ts":"2026-05-16T14:23:02Z","script":"vocab_alignment","db":"data/pyarchinit_mini.db","mappings":{"USVA→USVs":80,"USVB→USVs":50,"USVC→USVn":12},"status":"ok"}
```

### 6.5 Ordering

Single CLI run applies in sequence, each in its own transaction:

1. `node_uuid_schema` (additive — nullable column)
2. `node_uuid_backfill` (populates the column)
3. `vocab_alignment` (USVA/USVB/USVC → USVs/USVn)
4. `paradata_bootstrap` (optional, no DB writes)

Failure at step N leaves steps 1..N-1 committed — additive, no breakage.

## 7. Error handling

| Category | Strategy |
|---|---|
| VocabProvider bootstrap | Flask refuses to start with actionable error (`pip install s3dgraphy>=0.1.42` / "missing pillar X" / "JSON malformed at line:col"). Escape hatch `PYARCHINIT_VOCAB_STRICT=0` for dev only (downgrades to runtime 503 on every vocab call) |
| Vocab endpoint | Never 500. Unknown unit_type → 404 + suggestions. Invalid family → 400. Lang unsupported → 200 + `X-Lang-Fallback: en` |
| DTO validation | Known type → OK. Legacy `{USVA, USVB, USVC}` → accept + deprecation warning + UI banner. Unknown non-legacy → ValidationError. Edit of existing legacy record without changing the field → pass-through |
| Migration backup failure | Abort before mutating. Filesystem-full / permissions / missing `pg_dump` all surfaced with actionable message |
| Migration `ALTER TABLE` failure | Per-DB transaction rollback; report lists OK/failed DBs separately; exit code ≠ 0 |
| Backfill partial failure | Batch transaction rollback; idempotent so resume works on re-run |
| s3dgraphy upgraded but DB not migrated | Graceful degradation: VocabProvider exposes new types; form selects show new types; legacy records still load (with disabled "USVA (deprecated)" preselected option + banner suggesting migration); Harris matrix uses `VisualStyle.fallback()` for unknown legacy types |
| Visual rules entry without datamodel entry (or vice versa) | Single bootstrap warning; runtime returns fallback for missing side |

Guiding principle: **vocab/sync errors never block saving a US or rendering an
existing Harris matrix**. Vocab is a service function, not a blocker for core
functionality.

### 7.1 Logging channels

| Channel | Content | Level |
|---|---|---|
| Python `logging` (`pyarchinit_mini.vocab`) | Bootstrap, runtime warnings, version drift | INFO/WARNING |
| `data/migration.log` (JSON line) | All migration events | always |
| `data/backups/_index.json` | Backup catalogue | — |
| Flask header `X-Vocab-Status` | `ok` / `degraded` / `unavailable` on every vocab endpoint | — |

All logs contain only metadata and identifiers — never stratigraphic user
content.

## 8. Testing strategy

### 8.1 Pyramid

| Level | Target count | Coverage |
|---|---|---|
| Unit | ~60 | VocabProvider API, loader with quirks, DTO validation, EdgeType lookup, fallback paths, deprecation warnings |
| Integration | ~25 | Flask vocab endpoints, harris_creator with VocabProvider, DTO+service end-to-end, migration per table |
| E2E | ~5 | Web smoke (form → save → matrix render); full migration on SQLite + PG fixtures; s3dgraphy upgrade mock; bootstrap fail vs strict mode; Harris parity |

Framework: pytest (already in use). New deps for tests: `freezegun` for
deterministic timestamps.

### 8.2 Fixtures

```
tests/fixtures/
  s3dgraphy_jsons/
    0.1.42/
      s3Dgraphy_node_datamodel.json
      s3Dgraphy_connections_datamodel.json
      em_visual_rules.json
    0.1.15/
      "s3Dgraphy_node_datamodel .json"   # filename quirk
      em_connection_rules.json           # legacy naming
      em_visual_rules.json
    malformed/
      s3Dgraphy_node_datamodel.json      # JSON broken at line 42
  databases/
    sqlite_pre_migration.db          # 30 US, mix of USVA/USVB/USVC + standard types
    sqlite_partially_migrated.db     # vocab migrated, node_uuid not yet backfilled
    sqlite_fully_migrated.db         # all 3 migrations applied
  graphml_outputs/
    synthetic_baseline_em_palette.graphml  # generated from sqlite_fully_migrated.db w/ legacy PALETTE
    synthetic_target_vocab.graphml         # same DB, with VocabProvider styles
```

JSON fixtures are **exact copies** of real s3dgraphy files (no hand-crafting —
avoids drift on upstream JSON evolution). DB fixtures are **small synthetic
datasets** (~30 US, ~5 inventario, ~3 periodizzazione), not real excavation
data — large dataset stress tests live in `tests/e2e/` and are gated on
explicit fixture provisioning.

### 8.3 Critical tests

**Parity test** — `test_harris_matrix_visual_parity.py` (PR3 gate)
- Generate Harris matrix from `sqlite_fully_migrated.db` with legacy
  `EMPalette.PALETTE` → graphml output.
- Generate the same with `VocabProvider.get_visual_style()` → graphml output.
- XML diff: differences allowed ONLY on `style` attributes for new types
  (`USVs`, `RSF`) or documented colour improvements. Never on `US`, `SU`,
  `WSU` standard.
- Fixtures updatable via `pytest --update-fixtures`.

**Migration idempotency** — `test_migrations_idempotent.py`
- For each script: apply → re-apply → no diff vs post-first-apply state.
- For each script: apply → rollback → re-apply → identical to first apply.

**SQLite vs PostgreSQL parity** — `test_migrations_pg_parity.py`
- `skipif` no local PG (pattern matches QGIS `tests/sync/`).
- Setup PG via Docker, `pg_isready` check.
- Apply migrations on both, compare resulting schema + sample data.

**Bootstrap failure modes** — `test_vocab_bootstrap.py`
- Mock `importlib.resources` to simulate missing pillar / malformed /
  version mismatch.
- Verify `VocabBootstrapError` raised with actionable message.

**Web smoke** — extend `test_web_full.py`
- `GET /api/v1/vocab/unit-types` → 200 + valid JSON.
- POST form US with new type → 201.
- POST form US with legacy type → 201 + warning header.
- Render Harris → graphml file with correct styles.

### 8.4 CI matrix

| OS | Python | DB |
|---|---|---|
| macOS Sequoia | 3.13 | SQLite + PG (Docker) |
| Ubuntu 24.04 | 3.13 + 3.12 | SQLite + PG (service) |
| Windows 11 | 3.13 | SQLite |

PG tests skipped if `pg_isready` fails.

## 9. Definition of Done

- All unit + integration tests green on CI matrix
- Harris matrix parity test green (zero diff on standard types)
- Full migration green on SQLite + PG with multiple fixtures
- Dry-run report readable and accurate on realistic DB (≥1000 US)
- CHANGELOG updated bilingually (IT + EN)
- Version bumped `2.1.68 → 2.2.0-alpha`
- Short tutorial updated for "Unit types" section explaining s3dgraphy backing
- `README.md` gets a new "s3dgraphy integration" section
- CLI `pyarchinit-mini-migrate-vocab` documented under `docs/`
- 8 PRs merged in order: PR1 VocabProvider module → PR2 s3dgraphy bump →
  PR3 em_palette cutover → PR4 form integration → PR5 s3d_converter cutover →
  PR6 migrations + CLI → PR7 DTO validation → PR8 retire deprecated code

## 10. Implementation phasing

This is Spec 1 of 4 for Group A:

| Spec | Scope | Depends on |
|---|---|---|
| **1 (this doc)** — Web Foundation | VocabProvider, vocab endpoints, em_palette cutover, s3d_converter cutover, DB migrations, DTO validation, retire hardcoded mappings | — |
| **2** — Local Graph & Paradata | GraphProjector (`populate_graph`), ParadataStore (`paradata.graphml` per site), GraphIngestor (`populate_list`), full delegate of GraphML writer to `s3dgraphy.exporter`, new web routes for graph generation/import | Spec 1 |
| **3** — Sync Engine + EM Backend | SyncEngine as Flask background worker, DatacenterClient with EMBackend (REST), offline queue (sqlite), ConflictResolver web UI, multi-user sync ownership | Spec 1 + 2 + EM Datacenter API |
| **4** — GraphDB Backend | GraphDBBackend implementing same interface as Spec 3, SPARQL transport | Spec 1 + 2; parallel to Spec 3 |

## 11. Open questions (for later specs, non-blocking for Spec 1)

1. Where do `paradata.graphml` files live in the multi-user web (per-project
   filesystem under `data/paradata/<site>/`, or DB blob)? — Spec 2
2. `GraphIngestor` (`populate_list`) — does the UI need a dry-run preview
   before writing to DB? — Spec 2
3. Conflict-resolution UI in the web — modal with diff table, or dedicated
   page? — Spec 3
4. `graph_id` granularity in the multi-user web — per-site, per-user,
   per-organization? — Spec 3
5. Authentication for EM Datacenter — API key vs OAuth device flow? — Spec 3

## 12. References

- **Foundational design (QGIS plugin):**
  `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md`
- **QGIS plugin dev log:**
  `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`
- **s3dgraphy 0.1.42:** <https://github.com/zalmoxes-laran/s3dgraphy>
- **s3dgraphy core concepts:**
  <https://docs.extendedmatrix.org/projects/s3dgraphy/en/latest/s3dgraphy_core_concepts.html>
- **Extended Matrix docs:** <https://docs.extendedmatrix.org/>
- **JSON pillars in QGIS plugin:**
  `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/ext_libs/s3dgraphy/JSON_config/{s3Dgraphy_node_datamodel.json, s3Dgraphy_connections_datamodel.json, em_visual_rules.json}`
