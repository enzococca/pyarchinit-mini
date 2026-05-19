# EM Palette + Multi-Format Round-Trip for Harris Swimlane

**Date**: 2026-05-19
**Status**: Design (pending implementation plan)
**Author**: Enzo + Claude
**Branch**: TBD (will be created during writing-plans)
**Spec ID**: EM-PALETTE-SWIMLANE-2026-05-19

## Goal

Make the Harris swimlane rendering, export, and import driven by the canonical Extended Matrix (EM) palette and s3dgraphy graph model. Replace the current cytoscape-only renderer with an s3dgraphy-centric pipeline that produces consistent visual output across the web UI, yEd GraphML export, and Heriverse/ATON JSON export. Add GraphML and Heriverse JSON import that writes inverse rapporti on both involved US.

## Non-goals

- Migrating historical 2-tuple rapporti data on disk (we read both formats forever, write only 4-tuple).
- Adding a new physical relationship store (`us_relationships_table`) as a replacement for `us_table.rapporti` — `rapporti` remains the system of record.
- Replacing the s3dgraphy library with a hand-rolled graph model.
- Building a separate ATON-specific export format. ATON consumes the existing Heriverse JSON format; one exporter serves both.

## Decisions captured during brainstorm

| Topic | Decision |
|---|---|
| Palette source | `~/Downloads/em_palette_template.graphml` (3246 lines) becomes the canonical `pyarchinit_mini/graphml_converter/templates/EM_palette.graphml` (replaces existing 658-line stub). |
| Rapporti format | Bilingual reader (accepts 2-tuple and 4-tuple); writer always emits 4-tuple `[tipo, us, area, sito]`. |
| Inverse rapporti on import | Write on both US rows: source gets forward, target gets inverse (lookup via `INVERSE_PAIRS`). Symmetric edges only emitted once. |
| Swimlane layout | 1D rows = periods (always). Within-row visual clusters by selected grouping (none = default; or area / settore / quadrato / attività / strutture). |
| Period fallback | When `period_table` is empty for the site OR a US has no `periodo_iniziale`, that US is assigned to a synthetic row named "Periodo 1". |
| Export/Import UI touchpoints | Swimlane page (primary), sites list (quick action buttons), dedicated `/matrix-tools` page (file pickers). |
| ATON vs Heriverse | Same format. Single exporter (`s3dgraphy.exporter.json_exporter`), labelled "Heriverse / ATON" in UI. |
| Pipeline rollback | Feature flag `SWIMLANE_PIPELINE=s3dgraphy|legacy` (default `s3dgraphy`). Legacy code path retained until regression parity confirmed on Adarte. |
| Stub US on import | Auto-create stub `us_table` row when an edge references a US not present in DB. Returned in result as `stubs_created`. |
| Dedup key | Rapporti deduplicated by `(relation_canonical, target_us, target_area, target_sito)`. |
| Hot-reload | Palette reloaded via SIGHUP for dev convenience. Cache cleared. |

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  DB (postgres/sqlite)                                            │
│  us_table  period_table  site_table  us_relationships_table      │
└────────────────────┬─────────────────────────────────────────────┘
                     │ S3DProjector.from_site(site, group_by)
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│  s3dgraphy.Graph (canonical representation)                      │
│  • nodes: US typed (USM/USD/USV/SF/VSF/TSU/USVn/…)               │
│  • edges: normalized canonical (overlies/cuts/fills/abuts/…)     │
│  • styling: from palette_loader (EM_palette.graphml)             │
│  • period rows + sub-group metadata                              │
└──┬──────────────────┬──────────────────┬──────────────────┬──────┘
   │                  │                  │                  │
   ▼                  ▼                  ▼                  ▼
Cytoscape         GraphML            Heriverse JSON     Reverse:
JSON for web      Exporter           Exporter           Graph → DB
/api/swimlane     (yEd palette       (= ATON)           (4-tuple +
 /load            template)                              inverses)
```

The `s3dgraphy.Graph` is the canonical representation. Web rendering, multi-format export, and import all pass through it. Palette/styling are attached to nodes and edges as metadata.

## Components

### Palette layer

`pyarchinit_mini/em_palette/loader.py`
- Parses `EM_palette.graphml` once at startup; caches a singleton.
- Exposes `get_node_style(unit_type: str) -> NodeStyle` and `get_edge_style(canonical_relation: str) -> EdgeStyle`.
- `NodeStyle = {shape, fill_color, border_color, border_width, border_style, font_color, font_size}`.
- `EdgeStyle = {line_color, line_width, line_style, arrow_source, arrow_target}`.
- SIGHUP handler clears cache; dev can edit the palette without restarting the server.
- Fallback: if `EM_palette.graphml` missing/corrupt, logs warning at startup and uses a hardcoded minimal palette (USM/USD/USV/SF/VSF/TSU + overlies/cuts/fills/abuts/has_same_time/is_after).

### Projector layer

`pyarchinit_mini/graphproj/s3d_projector.py`
- `class S3DProjector`:
  - `from_site(session, site: str, group_by: str = "none") -> s3dgraphy.Graph`
  - Steps:
    1. Load periods: `SELECT periodo, fase, datazione FROM period_table WHERE sito = :sito OR sito IS NULL OR sito = ''`. If empty → single fallback `Period("Periodo 1", phase=None)`.
    2. Load US rows: `SELECT * FROM us_table WHERE sito = :sito`. For each US: assign to period via `periodo_iniziale`; if no period or unmatched, assign to "Periodo 1".
    3. Parse `rapporti` (bilingual + 4-tuple aware) → canonical edges. Reuses bilingual matching: `registry.resolve_italian_alias(rel) or _EN_TO_CANONICAL.get(rel) or _IT_EXTRAS.get(rel)` where `_IT_EXTRAS` includes `riempito da`, `si lega a`, `gli si appoggia`, and other Italian aliases missing from `vocab_it.json`.
    4. Build `s3dgraphy.Graph`: instantiate typed nodes via `palette_loader.get_node_style(unit_type)`, edges with `palette_loader.get_edge_style(canonical_rel)`. Attach period_row_id and sub-group key (area/settore/…) as metadata.

`pyarchinit_mini/graphproj/s3d_to_cytoscape.py`
- `to_cytoscape(graph: s3dgraphy.Graph, group_by: str) -> dict`
- Translates Graph → cytoscape JSON with `style:{shape, fillColor, borderColor, line-color, target-arrow-shape, ...}` derived from palette.
- If `group_by != "none"`: wraps nodes in cytoscape compound parents, one per (period_row, sub_group_value).

### Reverse layer

`pyarchinit_mini/graphproj/graph_to_db.py`
- `write_graph(graph: s3dgraphy.Graph, target_site: str, session, *, source_label: str) -> WriteResult`
- For each US node N in graph:
  - UPSERT `us_table (sito=target_site, area=N.area, us=N.us_num, unita_tipo=N.type, descrizione=N.description, periodo_iniziale=N.period)` with `ON CONFLICT (sito, area, us) DO UPDATE SET ...`. Does NOT overwrite `rapporti` here.
  - If US already exists, mark for rapporti append (next step).
- For each edge E (A→B, type=`canonical_rel`):
  - Resolve display labels: forward via `INVERSE_PAIRS` lookup → italian display (e.g., overlies → "Copre"); inverse → "Coperto da".
  - Append to A.rapporti: `[forward_italian, B.us, B.area, target_site]`.
  - Append to B.rapporti: `[inverse_italian, A.us, A.area, target_site]` (skipped if `canonical_rel` in SYMMETRIC).
  - Dedup A.rapporti and B.rapporti by `(rel, us, area, sito)`.
- For each US referenced by an edge but not present in graph nodes:
  - Auto-create stub: `INSERT us_table (sito, us, area, unita_tipo="US", descrizione="Imported placeholder", data_origine=f"import_{source_label}_{ts}")`. Tracked in `WriteResult.stubs_created`.
- `COMMIT`. Returns counts: `imported_us`, `imported_edges`, `inverses_written`, `stubs_created`, `inverses_skipped` (unknown inverse), `errors`.

### Routes layer

Modifications to `pyarchinit_mini/web_interface/harris_creator_routes.py`:

| Route | Method | Behavior |
|---|---|---|
| `/api/load/<site>` | GET | Uses `S3DProjector` + `s3d_to_cytoscape` when flag = `s3dgraphy`; falls back to legacy `SwimlaneState.load` on exception (with `X-Pipeline-Fallback: legacy` header). |
| `/api/export/<site>/yed-graphml` | GET | `S3DProjector` → `s3dgraphy.exporter.graphml.GraphMLExporter` writing to a copy of `EM_palette.graphml` (palette nodes preserved at the bottom; site nodes injected into the `<graph>` element). |
| `/api/export/<site>/heriverse-json` (NEW) | GET | `S3DProjector` → `s3dgraphy.exporter.json_exporter.JsonExporter.export_heriverse()`. |
| `/api/import/<site>/graphml` (NEW) | POST | `multipart/form-data` file → `s3dgraphy.importer.import_graphml.GraphMLImporter` → `graph_to_db.write_graph(graph, site, source_label="graphml")`. |
| `/api/import/<site>/json` (NEW) | POST | Parse Heriverse JSON → reconstruct `s3dgraphy.Graph` → `write_graph(...)`. |

### UI layer

`pyarchinit_mini/web_interface/templates/harris_creator/swimlane.html`
- **Raggruppamento** dropdown: `nessuno (default)` / `area` / `settore` / `quadrato` / `attività` / `strutture`. Triggers reload of `/api/load/<site>?group_by=<value>`.
- **Export** menu: `yEd GraphML (.graphml)` / `Heriverse / ATON (.json)`.
- **Import** menu: file picker for `.graphml` and `.json`; POST to corresponding endpoint; on success, reload swimlane.

`pyarchinit_mini/web_interface/templates/matrix_tools.html` (NEW)
- Dedicated page at `/matrix-tools`. Site selector + file uploader + format radio (GraphML / Heriverse JSON). One page for users who want to manage matrix files without opening the swimlane.

`pyarchinit_mini/web_interface/templates/sites/list.html`
- Add two quick-action buttons per site row: `Export GraphML`, `Export Heriverse JSON`.

### Removed / refactored

- `pyarchinit_mini/graphml_converter/yed_template.py::YEdTemplate` is repurposed: instead of building GraphML from scratch, it merges `palette_loader` styles into a copy of `EM_palette.graphml` for the exporter. May be replaced entirely by `s3dgraphy.exporter.graphml.GraphMLExporter` if that exporter accepts a template base.
- Legacy `SwimlaneState.build_edges_literal` retained behind feature flag until parity confirmed.

## Data flow detail

### A) Render swimlane (`GET /api/load/<site>?group_by=...`)

```
DB.us_table + period_table
        │
        ▼ S3DProjector.from_site(session, site, group_by)
        │   1. Load periods (or fallback "Periodo 1")
        │   2. Load US rows, assign to period
        │   3. Parse rapporti (bilingual + 4-tuple aware)
        │   4. Build s3dgraphy.Graph with palette styling
        │
        ▼ s3d_to_cytoscape.to_cytoscape(graph, group_by)
        ▼
{"site":..., "rows":[...], "nodes":[{data, style}], "edges":[{data, style}]}
```

### B) Export GraphML

```
S3DProjector → s3dgraphy.Graph
        ▼ s3dgraphy.exporter.graphml.GraphMLExporter(graph).write(palette_template=EM_palette.graphml)
        ▼ HTTP 200, file download (.graphml)
```

### C) Export Heriverse/ATON JSON

```
S3DProjector → s3dgraphy.Graph
        ▼ s3dgraphy.exporter.json_exporter.JsonExporter(graph).export_heriverse()
        ▼ HTTP 200, .json download
```

### D) Import GraphML

```
uploaded.graphml
        ▼ s3dgraphy.importer.import_graphml.GraphMLImporter(file).load() → s3dgraphy.Graph
        ▼ graph_to_db.write_graph(graph, target_site, session, source_label="graphml")
        │   For each US node: UPSERT us_table
        │   For each edge (A→B, type=overlies):
        │     A.rapporti += ['Copre', B.us, B.area, target_site]
        │     B.rapporti += ['Coperto da', A.us, A.area, target_site]
        │     Dedup
        │   For missing target US: INSERT stub
        │   COMMIT
        ▼ HTTP 200 {imported_us, imported_edges, inverses_written, stubs_created, errors}
```

### E) Import Heriverse JSON

```
uploaded.json
        ▼ heriverse_parser.parse(file) → s3dgraphy.Graph (new small helper)
        ▼ graph_to_db.write_graph(...)  (same as D)
```

### F) Rapporti round-trip semantics

```
READ:
  parse via ast.literal_eval
  for each item:
    if 2-tuple [rel, us]: expand → [rel, us, area=lookup(us, site), sito=current_site]
    if 4-tuple: keep as-is
    resolve rel via registry.resolve_italian_alias() + _EN_TO_CANONICAL + _IT_EXTRAS

WRITE:
  always 4-tuple list
  inverses written on the OTHER US (via INVERSE_PAIRS)
  symmetric edges (has_same_time, is_bonded_to) emitted once
```

## Error handling

| Scenario | Behavior |
|---|---|
| `EM_palette.graphml` missing/corrupt | Log warning at startup; fallback to minimal hardcoded palette; UI banner "palette ridotta in uso". |
| `s3dgraphy` pipeline raises on `/api/load/<site>` | Auto-fallback to `legacy` path; response includes `X-Pipeline-Fallback: legacy` header. |
| Import file invalid (parse error) | `400 {error: "parse_error", detail: "<line> <message>"}`. No DB writes. |
| Rapporti malformed (read time) | `try/except` `ast.literal_eval`; log warning; skip that US's edges; UI shows other edges normally. |
| Imported edge references missing US | Auto-create stub: `INSERT us_table (sito, us, area, unita_tipo="US", descrizione="Imported placeholder", data_origine="import_<source>_<ts>")`. Counted in `stubs_created`. |
| Unknown inverse (no `INVERSE_PAIRS` entry) | Write forward, skip inverse, log; accumulated in `inverses_skipped`. |
| UPSERT conflict on `(sito, us, area)` | SQLAlchemy `insert().on_conflict_do_update()` (postgres) or equivalent SQLite ≥3.24 `INSERT OR REPLACE` for unita_tipo/descrizione/periodo; `rapporti` field is append+dedup, never overwritten. |
| Invalid `group_by` param | `400 {error: "bad_param", valid: ["none","area","settore","quadrato","attivita","strutture"]}`. |
| Site doesn't exist on export | `404 {error: "site_not_found"}`. |

**Audit log**: every import emits a JSON line to `~/.pyarchinit_mini/logs/matrix_import.jsonl`:
```json
{"ts": "2026-05-19T08:30:00Z", "user": "admin", "site": "Rimini_RN_2020_21", "source": "graphml", "imported_us": 100, "imported_edges": 230, "stubs_created": 3, "inverses_skipped": []}
```

## Testing

### Unit tests (`tests/unit/`)

- `test_palette_loader.py`: parse `EM_palette.graphml`, assert `unit_type → NodeStyle` map for USM/USD/USV/SF/VSF/TSU/USVn; `canonical_rel → EdgeStyle` for overlies/cuts/fills/abuts/has_same_time/is_after/is_before/is_bonded_to. SIGHUP test.
- `test_s3d_projector.py`: build Graph from fixture DB (3 periods, 10 US, mixed rapporti formats) → assert N nodes, M edges, fallback "Periodo 1" when period_table empty, sub-grouping by area produces compound clusters.
- `test_rapporti_reader.py`: parametrize input (2-tuple, 4-tuple, mixed, malformed, italian labels, english labels, with extras `riempito da`/`si lega a`/`gli si appoggia`) → assert canonical resolution + 4-tuple expansion.
- `test_rapporti_writer.py`: write 4-tuple, read back; dedup duplicates by `(rel, us, area, sito)`.
- `test_graph_to_db.py`: input Graph with 2 edges → assert `us_table.rapporti` on both sides (4-tuple, with inverses).
- `test_inverse_pairs_registry.py`: every canonical edge name either has an `INVERSE_PAIRS` entry or is in `SYMMETRIC`.

### Integration tests (`tests/integration/`)

- `test_api_load_site.py`: `GET /api/load/<site>` with and without `group_by`, assert cytoscape JSON structure + palette-derived style fields.
- `test_api_export_graphml.py`: `GET /api/export/<site>/yed-graphml` → assert valid XML, yEd namespaces, palette unit nodes present in `<graph>`.
- `test_api_export_heriverse.py`: `GET /api/export/<site>/heriverse-json` → assert Heriverse structure (multigraph + USVn + semantic_shapes wrapper).
- `test_api_import_graphml.py`: POST file → assert us_table populated, rapporti 4-tuple on both sides, stubs created for missing US.
- `test_api_import_json.py`: POST Heriverse JSON → same checks.
- `test_feature_flag_pipelines.py`: same fixture under `SWIMLANE_PIPELINE=s3dgraphy` vs `legacy` produces equal edge count.

### Round-trip tests (`tests/integration/test_roundtrip.py`)

- `test_db_to_graphml_to_db`: DB → export → import in fresh DB → assert parity (modulo timestamps).
- `test_db_to_json_to_db`: same for Heriverse JSON.

### Regression test (`tests/integration/test_adarte_regression.py`)

- Fixture: anonymized postgres dump of Rimini_RN_2020_21_Museo_Fellini, 50–100 US covering all Italian rapporti patterns (Coperto da, Copre, Riempie, Riempito da, Taglia, Tagliato da, Si lega a, Gli si appoggia, Uguale a, Si appoggia a).
- Site renamed to `RegressionFixture_v1`; US numbers preserved.
- Assert: edge distribution under `SWIMLANE_PIPELINE=s3dgraphy` matches legacy ±5 edges (small drift OK from improved dedup).

### Test infrastructure

- All tests use `ChoiceLoader` stub + `monkeypatch.setenv("DATABASE_URL", "sqlite:///...")`.
- Fixture schema **must match real postgres** (column types, names) — same lesson as Spec 10 hotfix run.
- `tests/fixtures/em_palette_minimal.graphml`: 5 unit types + 5 edge types, smaller than real palette for fast tests.

## Migration / Rollout

1. Land new modules behind `SWIMLANE_PIPELINE=legacy` (default OFF). All tests pass with default.
2. Test on Adarte staging with `SWIMLANE_PIPELINE=s3dgraphy`; verify Rimini Museo Fellini still shows ~4066 edges.
3. Flip default to `SWIMLANE_PIPELINE=s3dgraphy` in production deploy.
4. After 2 weeks stable, delete legacy `build_edges_literal` and feature flag in a separate PR.

## Open questions for plan phase

- Do we want s3dgraphy version pin > 0.1.42 if the project's GraphMLImporter API has changed? Verify during writing-plans.
- Does s3dgraphy's `GraphMLExporter` accept a template base, or do we wrap with `YEdTemplate` post-process? Verify during writing-plans by reading exporter source.
- Audit log location: `~/.pyarchinit_mini/logs/matrix_import.jsonl` — does logging infrastructure exist or do we need to add it? Verify during writing-plans.
- Which `us_table` columns link a US to a period? On Adarte postgres `us_table` has `fase_iniziale` and `fase_finale` (text fields). Verify whether `periodo_iniziale` exists alongside (per legacy pyarchinit schemas) or whether the projector must join on `fase_iniziale → period_table.fase` to derive periodo. The fallback "Periodo 1" logic depends on this resolution.
- Backward compatibility note: the Adarte post-upgrade patch (`patch_pyarchinit_post_upgrade.py`) has a Section 27 that breaks on postgres and Section 28 that needs bilingual matching. The new s3dgraphy pipeline must natively include the bilingual + extras matching so those patches become NO-OPs (no `MARKER MISSING` failures). Plan a step to either gate Section 27/28 by Python version detection or remove from the patch script entirely.
- Adarte regression test baseline: legacy currently emits 4066 edges on Rimini_RN_2020_21_Museo_Fellini. The new pipeline must produce ≥ 4060 edges (±5 tolerance, same label distribution within ±10% per label).
