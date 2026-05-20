# S3dgraphy Bridge — Vendored Shared Package

**Date**: 2026-05-20
**Status**: Design (pending implementation plan)
**Author**: Enzo + Claude
**Branch**: TBD (will be created during writing-plans)
**Spec ID**: S3DGRAPHY-BRIDGE-2026-05-20
**Supersedes**: nothing — first design for this concern

## Goal

Extract the s3dgraphy sync logic currently living inline inside the QGIS plugin (`pyarchinit/modules/s3dgraphy/sync/`, ~22 modules + 75 test files) into a standalone Python package `pyarchinit-s3dgraphy-bridge`, distributed via public PyPI, and consume it from both the QGIS plugin and `pyarchinit-mini-desk` so that yEd ↔ DB ↔ GraphML round-trip is implemented **once** and used **twice**.

The driving user statement: *"in pyarchinit-mini-desk deve funzionare come hai implementato in pyarchinit"*. Vendoring is the only port strategy that literally honors that: same code, same fixes, same AC-2 guarantee.

## Non-goals

- Building a new graph model (s3dgraphy itself is unchanged; the bridge is just the *sync layer* around it).
- Migrating yE-F multi-folder paradata, LocationNodeGroup, or PG-Compat to mini-desk in the v1.0 cut. Those land in successive bridge minor releases (see Roadmap).
- Designing Heriverse ↔ mini-web bidirectional integration. That is a separate brainstorming session (Task #7) that runs AFTER this design is implemented.
- Replacing mini-desk's `stratigraph/*` (bundle transport, sync queue, connectivity monitor) — orthogonal to the bridge.
- Replacing mini-desk's `graphml_converter/*` (em_palette, dot_parser, svg_resources) — not overlapping the bridge.
- Backporting the bridge to plugin v5.x stable pre-5.9 (bridge assumes schema with optional `other_locations` and UUID7 `node_uuid`).
- Supporting Python ≤ 3.10 (bridge requires `typing.Protocol` runtime semantics).

## Decisions captured during brainstorm

Six picks, in the order they were made:

| # | Topic | Decision | Rationale |
|---|---|---|---|
| Q1 | Port strategy | **Vendoring**: shared package `pyarchinit-s3dgraphy-bridge` consumed by both plugin and mini-desk | Only strategy that literally keeps "same behavior" without doubling maintenance. |
| Q2 | First cut size | **MVP-roundtrip** (16 modules): yEd→DB→GraphML round-trip + AC-2 byte-identical, **no** yE-F, **no** LocationNodeGroup, **no** PG-Compat | Smallest scope that actually validates the adapter abstraction (needs both directions). |
| Q3 | Mini-desk reconciliation | **Delete-and-replace** legacy `graphproj/*`, `graphml_io/*`, `s3d_integration/*` (14 files) | Aggressive cleanup. Flask audit mandatory before merge. |
| Q4 | Distribution | **New repo + public PyPI**: `github.com/pyarchinit/pyarchinit-s3dgraphy-bridge` + GitHub Actions Trusted Publishing on tag | Standard Python pattern, version-explicit, no submodule friction, no monorepo restructure. |
| Q5 | Adapter surface | **5 typing.Protocol**: `DbSession`, `Workspace`, `Settings`, `FileProvider`, `Logger` | Pythonic, mypy-verifiable, trivial mocks for tests. Avoids god-object. |
| Q6 | Plugin migration | **Shim re-export**: 22 plugin files become 1-line `from pyarchinit_s3dgraphy_bridge.X import *  # noqa` | Minimum risk, 0 call sites touched in ~80 plugin files. Shims removed in plugin v6.0.0 cleanup. |

The asymmetry between Q3 (mini-desk = radical delete) and Q6 (plugin = conservative shim) is deliberate: mini-desk has few consumers of the modules being replaced, the plugin has ~80 files that import from `modules/s3dgraphy/sync/*`.

## Architecture

Three layers. The bridge knows nothing about Qt or Flask. Consumers implement 5 Protocols and pass them in.

```
┌────────────────────────────────────────────────────────────────┐
│  Layer 3 — HOST (UI + concrete storage)                        │
│  ┌──────────────────────────┐    ┌──────────────────────────┐  │
│  │  pyarchinit (QGIS)       │    │  mini-desk (Flask)       │  │
│  │  - PyQt forms            │    │  - Jinja templates       │  │
│  │  - QSettings             │    │  - AppSetting model      │  │
│  │  - QFileDialog           │    │  - upload endpoints      │  │
│  │  - sqlite3 / psycopg2    │    │  - SQLAlchemy Session    │  │
│  └────────────┬─────────────┘    └────────────┬─────────────┘  │
└───────────────┼───────────────────────────────┼────────────────┘
                │ implements 5 Protocols        │
                ▼                               ▼
┌────────────────────────────────────────────────────────────────┐
│  Layer 2 — ADAPTER (Protocol set, defined in the bridge)       │
│  DbSession · Workspace · Settings · FileProvider · Logger      │
│  No knowledge of Qt or Flask. Pure typing.Protocol.            │
└───────────────┬────────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────────┐
│  Layer 1 — BRIDGE (pure logic, PyPI package)                   │
│  pyarchinit-s3dgraphy-bridge==1.0                              │
│  ├─ yed_import_pipeline + parser/classifier/detector/walker    │
│  ├─ graph_projector + group_projector                          │
│  ├─ graph_ingestor + graphml_writer                            │
│  ├─ paradata_store + edge_registry                             │
│  ├─ vocab_provider + uuid7                                     │
│  └─ tests/ (~50 file, AC-2 fixtures included)                  │
└────────────────────────────────────────────────────────────────┘
```

### Three load-bearing invariants

1. **AC-2 byte-identical**: bridge GraphML output is byte-per-byte identical to plugin v5.9.0.1-alpha output for the same inputs, modulo normalized line endings. Enforced by golden fixture suite in the bridge CI. Any new bug found in the wild adds a fixture (test-driven release).
2. **Zero Qt/Flask deps in the bridge**: bridge imports only stdlib + SQLAlchemy + lxml. CI gate: `grep -r "import PyQt\|from PyQt\|import flask\|from flask\|import qgis\|from qgis" src/` must return 0 results.
3. **Symmetric Protocol implementations**: plugin and mini-desk implement *the same 5 Protocols* with different backends. A bridge function that passes tests against mock Protocols must work in both consumers without modification.

### Protocol contracts (signatures)

```python
# Bridge: src/pyarchinit_s3dgraphy_bridge/protocols.py
from typing import Protocol, Any
from pathlib import Path

class DbSession(Protocol):
    def execute(self, sql: str, params: dict | None = None) -> "Cursor": ...
    def commit(self) -> None: ...
    is_postgres: bool

class Workspace(Protocol):
    root: Path
    def tmp(self) -> Path: ...

class Settings(Protocol):
    def get(self, key: str, default: Any = None) -> Any: ...

class FileProvider(Protocol):
    def read_bytes(self, ref: str) -> bytes: ...
    # ref is consumer-defined: local path (plugin) or upload-id (mini-desk)

class Logger(Protocol):
    def info(self, msg: str) -> None: ...
    def warn(self, msg: str) -> None: ...
    def error(self, msg: str, exc: Exception | None = None) -> None: ...
```

## MVP Scope (bridge v1.0.0)

### 16 modules ported

| Role | Modules |
|---|---|
| **Import yEd → DB** | `yed_import_pipeline`, `yed_table_parser`, `yed_classifier`, `yed_detector`, `yed_group_walker`, `yed_rapporti_policy` |
| **Projection DB → in-memory graph** | `graph_projector`, `group_projector` (base, no LocationNodeGroup) |
| **Ingest graph → DB writes** | `graph_ingestor` |
| **Export graph → GraphML** | `graphml_writer` |
| **Shared state** | `paradata_store`, `edge_registry`, `vocab_provider`, `vocab_types`, `uuid7`, `_db_handle` |

### Test inclusion (~50 of 75 plugin test files)

- **L0 unit** (~25 file): one per module (parsing, UUID7 generation, edge_registry equality, vocab lookup).
- **L1 integration** (~15 file): end-to-end import/export pipelines on in-memory SQLite.
- **L2 AC-2 golden** (~10 file): GraphML fixtures from plugin v5.9.0.1-alpha + byte-identical assertion.

### AC-2 byte-identical contract

The package ships `tests/fixtures/ac2_golden/` with the GraphML fixtures already present in the plugin (`tests/fixtures/*.graphml`, ~10 files at v5.9.0.1-alpha — exact count locked when the bridge repo bootstraps). The test `test_ac2_byte_identical.py` iterates each fixture:

1. Load original GraphML → `GraphIngestor` → in-memory SQLite.
2. Re-read SQLite → `GraphProjector` → `GraphmlWriter` → bytes.
3. Assert `output_bytes == original_bytes` (byte-per-byte, normalized line endings).

If a single fixture fails, bridge CI is red. No `v1.x.x` tag ships with AC-2 broken.

### Explicit non-inclusions in MVP (see Roadmap for landing version)

- yE-F multi-folder paradata + `other_locations` JSON column
- LocationNodeGroup pattern (AI07) + 6 spatial dimensions
- PG-Compat complete (`_workspace`, `_columns_of`, `conftest_pg`, `pyarchinit_pg_importer`) — MVP is SQLite-only
- `conflict_resolver`, `group_store`, `_legacy_paradata_svgs`
- `yed_classifier` hardening from plugin 5.8.5-alpha *Bug A–T fastfix* is **included** (it patches modules already in scope).

## Roadmap

One concept per minor release. Plugin and mini-desk pin to whatever version they need.

| Release | Brings | Effort | Plugin reference |
|---|---|---|---|
| v1.0.0 | MVP-roundtrip + AC-2 | ~3-4 weeks | Pre-yE-F baseline (plugin 5.7.4-alpha) |
| v1.1.0 | yE-F multi-folder paradata + `other_locations` JSON | ~2 weeks | Plugin 5.9.0-alpha (16 tasks `yed-f-multifolder`) |
| v1.1.1 | yE-F hotfix: primary `attivita` duplicate | ~1 day | Plugin 5.9.0.1-alpha (1653363c) |
| v1.2.0 | LocationNodeGroup (AI07) + 6 spatial dimensions | ~3 weeks | Plugin 5.6.0-alpha (b893838d) |
| v1.2.1 | Per-dimension visual style F2 (pastel-soft palette) | ~3 days | Plugin 5.5.1-alpha |
| v1.3.0 | PG-Compat full: `_workspace`, `_columns_of`, `conftest_pg`, `pyarchinit_pg_importer` | ~4 weeks | Plugin Phase 3 (5.6.2 → 5.7.4-alpha) |
| v1.3.1 | PG hotfix bundle: query coercion, sqlite_path resolution, media-fk migration | ~1 week | Plugin 5.7.9.1+2+3-alpha |
| v1.4.0 | `conflict_resolver`, `group_store`, `_legacy_paradata_svgs`, hardened vocab provider | ~2 weeks | Plugin 5.8.x cumulative |
| v2.0.0 | Breaking: Protocol API v2 (post-dogfood refactor), drop `_db_handle` legacy fields | ~2 weeks | TBD post-v1.4 |

### Release coordination

- **Bridge v1.0** is the blocker for the mini-desk delete-and-replace merge (Q3=A).
- Plugin migrates to shim re-export (Q6=C) **at** bridge v1.0, tag `5.9.1-bridge-migration-alpha`.
- Plugin shim **cleanup** (deletion of the 22 shim files) **not before** bridge v1.2 — needs confidence that the bridge handles yE-F + LocationNodeGroup as well as the inline did.
- Mini-desk jumps directly to bridge v1.0 (it never had yE-F natively, gains it for free at v1.1).
- Branch policy: GitFlow-light. `main` is always releasable. Development on `feat/*`. Annotated tags `vX.Y.Z`. GitHub Actions Trusted Publishing on tag — no API tokens in repo.

## Mini-desk migration plan (Q3=A)

Pre-requisite blocker: `pyarchinit-s3dgraphy-bridge==1.0.0` on PyPI with green AC-2.

| PR | Title | Effort | Notes |
|---|---|---|---|
| PR-1 | **Flask audit** | 1-2 days, no code | `scripts/audit_legacy_imports.py` grep-s `pyarchinit_mini/` for imports of `graphproj.*`, `graphml_io.*`, `s3d_integration.*`, `stratigraph/uuid_manager`. Output: `docs/audit/2026-XX-XX-bridge-migration-impact.md`. Manual review gate. Also greps for dynamic imports (`importlib.import_module` with literal strings) and Flask route definitions. |
| PR-2 | **Adapter Flask-side** | ~3 days | New `pyarchinit_mini/bridge_adapter/` with 5 classes implementing the bridge Protocols: `SqlalchemyDbSession`, `FlaskWorkspace`, `AppSettingProxy`, `UploadFileProvider`, `PythonLogger`. Unit test per adapter (no bridge import yet). |
| PR-3 | **requirements + dev install** | ~1 day | `pyarchinit-s3dgraphy-bridge==1.0.0` in `pyproject.toml`. Makefile target `dev-install-bridge`. CI green with bridge installed but unused. |
| PR-4 | **Re-route APIs the bridge replaces** | ~1 week | Per-endpoint rewrite of the service backing each identified route (e.g. `POST /api/v1/sync/import`, `POST /api/v1/sync/export`). REST contracts (JSON shape, status codes) preserved — snapshot tests assert this. Web integration tests per migrated endpoint. |
| PR-5 | **Delete legacy modules** | ~1 day | Physical deletion of the 14 files identified in Q3. Survivors (mini-desk-specific, outside bridge scope): `graphproj/heriverse_parser.py`, `graphproj/auto_regen.py`, `graphproj/ingest_plan.py`, `graphproj/filesystem.py`, all of `stratigraph/`, all of `graphml_converter/`. Verify `grep` returns 0 hits for deleted modules. |
| PR-6 | **Tag** `3.0.0-bridge-migration` | ~1 hour | Major bump (today is 2.9.1). CHANGELOG bilingual. CI green. Auto-deploy to Flask preview env if available. |

Rollback per PR: each is revertable in isolation. Worst case revert PR-5 reinstates the 14 files; revert PR-4 restores the old route. The bridge stays installed but inert.

## Plugin migration plan (Q6=C)

Pre-requisite blocker: same as mini-desk.

| PR | Title | Effort | Notes |
|---|---|---|---|
| PR-A | **requirements + auto-install** | ~1 day | `pyarchinit-s3dgraphy-bridge==1.0.0` in `requirements.txt`. `scripts/modules_installer.py` extended to `pip install` the bridge into `ext_libs/`. Smoke test: after QGIS restart, `import pyarchinit_s3dgraphy_bridge` works. **Zero lines of plugin code touched** — bridge installed but inert. |
| PR-B | **Adapter QGIS-side** | ~3 days | New `modules/s3dgraphy/bridge_adapter/` with `QgisDbSession` (wraps existing `_db_handle`), `QgisWorkspace`, `QSettingsProxy`, `QtFileProvider`, `QgsLogger`. Unit tests via pytest-qt mocks. |
| PR-C | **Shim re-export atomico** | ~1 day | The 22 files in `modules/s3dgraphy/sync/` reduced to 1-line `from pyarchinit_s3dgraphy_bridge.<modulename> import *  # noqa: F401, F403`. `modules/s3dgraphy/sync/__init__.py` master re-export. ~80 plugin call sites unchanged. Gate: the 351 plugin sync tests must pass against the installed bridge. |
| PR-D | **CHANGELOG + tag** | ~1 hour | `5.9.1-bridge-migration-alpha`. Bilingual CHANGELOG entry. `metadata.txt` bumped. |

Plugin v6.0.0 "Great Cleanup" (deferred, target Q4 2026):
- Delete the 22 shim files when bridge ≥ v1.4 and zero bug reports for at least 6 weeks.
- Rewrite all plugin call sites to import directly from `pyarchinit_s3dgraphy_bridge.*` (drop the `modules/s3dgraphy/sync.*` path).
- Major bump 5.9 → 6.0 to signal internal API breaking change for third-party scripts.

External plugin users (people with scripts like `from pyarchinit.modules.s3dgraphy.sync.graph_projector import GraphProjector`) keep working until plugin v6.0.0. Minimum 6-month shim window.

## Risks + mitigations

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| AC-2 byte-identical fails in real-world inputs (golden passes, wild GraphML diverges) | High | Medium | PR-1 audit collects real `.graphml` files in `pyarchinit_test{002..010}.sqlite` and adds them to the fixture set. Weekly CI cron runs golden over every fixture collected so far. |
| Drift bridge ↔ plugin in dogfood (bug fixed in plugin only, bridge missed) | High | High | Plugin v5.9.1+ forbids new edits inside `modules/s3dgraphy/sync/*` (CI fails if PR touches them). All fixes go to the bridge. Documented in plugin `CONTRIBUTING.md`. Hotfix escape valve: documented cherry-pick procedure with explicit follow-up PR to bridge. |
| Flask audit misses a dynamic import like `importlib.import_module("pyarchinit_mini.graphproj.projector")` | Medium | Low | Audit script also greps for string literals matching the deleted module paths. Manual gate review. |
| Bridge v1.0 slips (3-4 weeks → 6-8) | Medium | High | Cut B is the minimum viable; if needed, descope to MVP-import (Q2-A) as pre-release `0.9.0-import-only` to unblock mini-desk. Plugin stays inline until full roundtrip is ready. |
| QGIS dependency drift across platforms (`ext_libs/` behavior diverges on Linux/Mac/Windows) | Medium | Medium | CI matrix `ubuntu-latest / macos-latest / windows-latest` × Python 3.11/3.12/3.13. Wheel-only on PyPI (no sdist). |
| PyPI publish account compromise | High | Very low | Trusted Publishing via GitHub Actions (no API token, no secret in repo). 2FA on PyPI mandatory. |
| Mini-desk delete-and-replace breaks Flask routes not covered by tests | High | Medium | PR-1 audit extracts route definitions (`@app.route`, `@router.get`). Manual smoke test of **every** listed endpoint before PR-5 merge. |
| Bridge version not coordinated (mini-desk pins `>=1.0,<2.0`, bridge 1.3 accidentally breaks an API) | Medium | Low | Strict SemVer: everything in `__all__` or exported from package root is public API. Breaking change → major bump. Documented in `PUBLIC_API.md`. |
| Bridge test suite runs slowly (75 files × matrix CI = many minutes) | Low | Medium | Pytest `slow` marker for AC-2 (tag-only run) + parallelization (`pytest -n auto`). Fast smoke suite for PRs. |
| yE-F roadmap (v1.1) slips, leaving mini-desk without multi-folder paradata | Low | Medium | Mini-desk never had yE-F natively — gaining it at v1.1 is gravy, losing it would be a regression that doesn't apply here. Heriverse session D can proceed without yE-F in the first round. |

### Highlighted mitigations

- **"Plugin forbids edits to `modules/s3dgraphy/sync/`"** — pre-commit hook + CI gate. Hard guard-rail against involuntary drift.
- **Progressive AC-2 fixtures** — initial golden set is not enough; every bridge bug report adds a fixture that pins the regression. Test-driven release engineering.
- **Manual Flask smoke** — 30-40 endpoint checklist to click through after PR-4 and before PR-5. Boring but necessary.

## Acceptance criteria

### Functional (bridge v1.0)

1. **AC-FUNC-1** — yEd → SQLite import: given `Extended_Matrix_test_1.graphml` (known plugin fixture), the bridge produces the **same number of `us_table` rows** as plugin v5.9.0.1-alpha (one row per unique paradata label after yE-F fold, same as plugin behavior), with identical `node_uuid`, `attivita`, `unita_tipo`, and `rapporti` JSON. (Note: yE-F fold itself ships in v1.1; for v1.0 the row count matches the simpler pre-yE-F semantics of plugin 5.7.4-alpha.)
2. **AC-FUNC-2** — SQLite → GraphML export: given the SQLite state from AC-FUNC-1, the bridge GraphML output is byte-identical to the original (line endings normalized). This is the AC-2 contract.
3. **AC-FUNC-3** — Round-trip stability: `input.graphml → bridge import → bridge export → output.graphml`; `output == input` byte-per-byte, verified over all fixtures in `tests/fixtures/ac2_golden/`.
4. **AC-FUNC-4** — Vocab provider: the 7 base vocabulary types (Site, Period, US, Rapporto, Materiale, Pottery, Photo) are importable from `pyarchinit_s3dgraphy_bridge.vocab_provider` with the same API as the plugin (`get_vocab("us_table.unita_tipo")` returns an identical list).
5. **AC-FUNC-5** — Adapter contracts: the 5 Protocols (`DbSession`, `Workspace`, `Settings`, `FileProvider`, `Logger`) are documented in `PUBLIC_API.md` with a complete plugin-side and mini-desk-side example.

### Non-functional

6. **AC-NF-1 (test coverage)** ≥ 90% line coverage on the 16 modules of v1.0 (measured via `pytest --cov`).
7. **AC-NF-2 (CI matrix)** Ubuntu/macOS/Windows × Python 3.11/3.12/3.13 = 9 combinations green on every PR. Wheel-only on PyPI.
8. **AC-NF-3 (zero Qt/Flask deps)** Lint check: `grep -r "import PyQt\|from PyQt\|import flask\|from flask\|import qgis\|from qgis" src/` returns 0 results. CI gate.
9. **AC-NF-4 (semver)** Major bump if `__all__` or root-exported API changes. Manual verification via PR template checklist.
10. **AC-NF-5 (publication)** Auto-publish to PyPI on annotated tag `vX.Y.Z` via GitHub Actions Trusted Publishing, with manual approval gate in the Actions workflow for release tags.

### Integration (mini-desk migration)

11. **AC-INT-1** The 14 legacy mini-desk files (Q3 list) are physically deleted. `grep -r "from pyarchinit_mini.graphproj.projector\|...ingestor\|...graphml_io.yed_importer..." pyarchinit_mini/` returns 0 hits.
12. **AC-INT-2** Every Flask endpoint listed in the PR-1 audit responds with identical JSON shape and status code to pre-migration. Snapshot tests in `tests/integration/test_route_contracts.py`.
13. **AC-INT-3** Tag mini-desk `3.0.0-bridge-migration` on `main` with complete bilingual CHANGELOG.

### Integration (plugin migration)

14. **AC-INT-4** The 22 files in `modules/s3dgraphy/sync/` of the plugin are reduced to 1-line `from pyarchinit_s3dgraphy_bridge.X import *` each.
15. **AC-INT-5** The 351 plugin sync tests pass against the installed bridge (with `PYTHONPATH` excluding the inline `sync`).
16. **AC-INT-6** Plugin tag `5.9.1-bridge-migration-alpha` with `metadata.txt` aligned and bilingual CHANGELOG.

## Out-of-scope (explicit, to prevent scope creep)

### Deferred to later bridge releases

- yE-F multi-folder paradata + `other_locations` column + visual fan-out — bridge v1.1.0
- LocationNodeGroup pattern (AI07) + 6 spatial dimensions + `is_in_location` + toponym chain m:n — bridge v1.2.0
- PG-Compat complete (`_workspace`, `_columns_of`, `conftest_pg`, `pyarchinit_pg_importer`, mini_volterra PG fixture, `_normalize_query_params` coercion) — bridge v1.3.0
- `conflict_resolver`, `group_store`, `_legacy_paradata_svgs`, hardened vocab — bridge v1.4.0
- Per-dimension visual style F2 (pastel-soft palette, alpha-blending) — bridge v1.2.1
- Standalone migrations (`node_uuid` backfill, `other_locations` add-column, media-fk cleanup) — remain consumer-side until bridge v1.3+

### Never (or only if explicitly requested later)

- Heriverse ↔ mini-web bidirectional sync (separate brainstorming session, Task #7, starts after this design is implemented).
- Replacing mini-desk's frontend (Flask → FastAPI/React/etc.).
- Refactor of `pyarchinit_mini/graphml_converter/*` (em_palette, dot_parser, svg_resources, pure_networkx_exporter).
- Rewrite of `pyarchinit_mini/stratigraph/*` (bundle creator, sync queue, connectivity monitor, state machine) — orthogonal.
- Backport of the bridge to plugin v5.x stable pre-5.9.
- Support for Python ≤ 3.10.
- MCP server / LLM integration inside the bridge — bridge is pure logic, no LLM.

### Bounded by user statement

- Heriverse interaction during this brainstorming (Task #7 is pending and starts after).
- Wholesale rewrite of mini-desk to plugin style — Q5 (Protocol set) gives the abstraction without imposing plugin architecture on mini-desk.

---

## Appendix 1 — Task B: Ollama + LM Studio in mini-desk

Independent, non-blocking. Pattern of reference: the plugin's `modules/utility/llm_providers.py` already extends OpenAI + Anthropic with `OLLAMA` and `LMSTUDIO` (enum `LLMProvider`, `PROVIDER_DEFAULTS` dict, `_validate_local_model()` discovery).

### Scope

- File modified: `pyarchinit_mini/services/ai_assistant_service.py` (extend providers from 2 to 4).
- File added: `pyarchinit_mini/services/local_llm_discovery.py` (async HTTP probe of `http://localhost:11434/v1/models` for Ollama and `http://localhost:1234/v1/models` for LM Studio).
- Admin UI: dropdown extended to 4 entries, `base_url` field editable when local provider selected, **"Refresh models"** button performing async discovery via `asyncio.create_task` (mirroring plugin's `_ModelDiscoveryThread`).
- Tests: extend `tests/integration/test_admin_ai_settings_routes.py` with 4 cases (local provider switch, empty discovery, model not loaded, model loaded).

### Estimate

1-2 days. Mergeable before, after, or in parallel with the bridge work. Tag options: dedicated `2.10.0-llm-locals` or folded into `3.0.0-bridge-migration`.

---

## Appendix 2 — Task C: Heriverse deployment docx → spec preparation

Pure documentation task, no code.

### Source

`/Users/enzo/Downloads/Deployment and Infrastructure Proposal for Heriverse.docx` (19 KB, 8 sections):

1. Repository structure and environment management (GitLab repo `git.3dresearch.it/stratigraph/docker-heriverse.git`, branches `production` (PSNC) / `staging` (PSNC) / `development` (CNR))
2. Docker Compose architecture and services (Heriverse Node.js frontend on ATON.js, Heriverse-server Node.js middleware, CouchDB, Keycloak, Caddy)
3. Container registry strategy — TBD per docx (3DR GitLab / GitHub / PSNC, three options listed without commitment)
4. Identity management via Keycloak (request to host on PSNC infra)
5. Infrastructure sizing (test: 256 GB / 8 GB / 4 cores; prod: 2 TB / 32 GB / 12 cores)
6. Server access and management — TBD per docx (SSH scope, admin perms for 3DR + CNR DevOps)
7. CI/CD pipeline — production deployment strategy TBD per docx (GitLab Runner on CNR dev for staging is confirmed)
8. DNS (`heriverse.stratigraph-eccch.eu` target, `heriverse-staging.stratigraph-eccch.eu` for staging)

### Output

`docs/superpowers/specs/2026-05-20-heriverse-deployment.md` containing:

- Structured Italian summary of the 8 sections.
- Open questions extracted from the docx (Keycloak hosting, SSH scope, admin perms, production deployment strategy, DNS readiness).
- "Constraints for mini-desk integration" section (anticipates what session D will need to respect: CouchDB as Heriverse-side storage, Keycloak as SSO, Caddy as reverse proxy, `heriverse-server` middleware as the only allowed API entry from external clients into the Heriverse stack).
- Link to the original docx (left in Downloads or copied under `docs/superpowers/specs/heriverse-source/` per Q-during-brainstorm decision).

### Estimate

30 minutes. Non-blocking. Pure preparation for the subsequent session D (Task #7).

---

## Next steps after this spec is approved

1. User reviews this document and confirms.
2. Skill transition to `writing-plans` to produce the implementation plan(s).
3. Likely plan decomposition:
   - **Plan 1**: bridge v1.0 (new repo, 16 modules, AC-2, CI matrix, PyPI publication).
   - **Plan 2**: mini-desk PR-1 to PR-6 sequence.
   - **Plan 3**: plugin PR-A to PR-D sequence.
   - **Plan 4** (light): Appendix 1 — Ollama/LM Studio in mini-desk.
   - **Plan 5** (light): Appendix 2 — Heriverse docx → preparatory spec.
   - **Session D** (separate brainstorm later): Heriverse ↔ mini-web bidirectional.