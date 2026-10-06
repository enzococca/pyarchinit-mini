# s3dgraphy adoption for DB⇄graph projection (issue #2) — design

**Date:** 2026-10-06
**Issue:** https://github.com/enzococca/pyarchinit-mini/issues/2 (direction: zalmoxes-laran/s3Dgraphy#25)
**Status:** approved decisions below; implementation plan in `docs/superpowers/plans/2026-10-06-s3dgraphy-adoption.md`

## 1. Goal

pyarchinit-mini projects its database into an `s3dgraphy.Graph` through the shared
library (`s3dgraphy.importer.pyarchinit_importer.PyArchInitImporter`), not through its
own row→node code, so that full PyArchInit and mini maintain **one bridge, not three**.
Everything mini still needs on top of the library (stratigraphic edges from `rapporti`,
swimlane rows, DB write-back, yEd swimlane output) becomes a thin layer that reads and
writes the same `s3dgraphy.Graph`; the local `ProjectedGraph` model disappears.

## 2. Decisions (Enzo, 2026-10-06)

| # | Decision | Consequence |
|---|----------|-------------|
| D1 | Target **`s3dgraphy>=1.6.0.dev39,<1.7`** (pre-release, aligned with the full plugin) | Pin in `pyproject.toml` and `requirements.txt` (today they disagree: `>=0.1.42` vs `>=1.5.0`). `requires-python` becomes `>=3.9` (s3dgraphy 1.6 floor). |
| D2 | **`pyarchinit_mini/stratigraph/` stays, out of scope** | It is the StratiGraph ZIP bundle + sync queue, not GraphML I/O. s3dgraphy 1.5.4/1.6.0.dev39 ship no bundle module and the WP4 spec is not final. Record this in issue #2 and s3Dgraphy#25. |
| D3 | DB→graph goes through **`PyArchInitImporter(connection_url=…, filters={"sito": …})`** | 1.6.0.dev39 accepts `sqlite:///<abs>` and `postgresql://…` (psycopg2); mini passes the URL of its own SQLAlchemy engine. No rows→`process_row` shim needed. |
| D4 | **Thin local shims** for what s3dgraphy does not provide | Stratigraphic edges from `rapporti`, swimlane rows, cytoscape view, yEd TableNode writer, yEd/Heriverse readers, DB write-back (`write_graph`, `GraphIngestor`). All operate on `s3dgraphy.Graph`. |

## 3. What the library does and does not do (verified on 1.6.0.dev39)

Verified by running the importer on a mini-schema SQLite sample (see plan Task 0 spike):

- Reads `SELECT * FROM us_table WHERE sito = ?` (filters are whitelisted against the
  mapping's `column_mappings`; `area` is allowed). Per row it creates a
  `StratigraphicNode` subclass chosen from `unita_tipo` (`US/USM` → `StratigraphicUnit`,
  `USVs` → `StructuralVirtualStratigraphicUnit`, `USVn` → `NonStructuralVirtual…`),
  **`node_id = us_table.node_uuid`** (passthrough; rows with NULL uuid get a fresh
  `uuid4`), **name = `{area}.{settore}.{unita_tipo}{us}`** with empty parts collapsed
  (`A.Nord.US1`, `USVs3`), description = `d_stratigrafica`.
- Adds `PropertyNode`s (`has_property`) for the mapped qualia columns,
  `LocationNodeGroup`s (`is_in_location`) for area/settore/saggio/ambient,
  `AuthorNode`s (`has_author`), `DocumentNode`s (`has_documentation`), and
  `EpochNode`s (`has_first_epoch`/`survive_in_epoch`) resolved against the **classic**
  `periodizzazione_table` (`sito, periodo, fase, cron_iniziale, cron_finale,
  descrizione`). On mini-schema databases that table has different columns: the
  importer degrades to an empty index and per-row warnings. Epochs therefore exist only
  on shared plugin databases; mini's swimlane rows keep coming from `period_table`.
- **Does not create stratigraphic edges from `rapporti`** (`relations: []` in the
  mapping; s3Dgraphy#26 is still open). Mini keeps `rapporti_codec` and adds the edges.
- **Does not keep** `periodo_iniziale`, `fase_iniziale`, `descrizione`, the sub-group
  columns or `unita_tipo` as node attributes. Mini reads those columns itself.
- `Graph()` always contains one `GeoPositionNode`; every mini consumer must select
  stratigraphic nodes explicitly.
- `Graph.add_edge` accepts mini's canonical edge names (`overlies`, `cuts`, `fills`,
  `abuts`, `has_same_time`, `is_bonded_to`, `is_before`, `is_after`) without warnings;
  unknown names are downgraded to `generic_connection` with a graph warning.
- Passing `existing_graph=` switches the importer to "enriching" mode that **skips every
  row** not already in the graph (an empty `Graph` is not empty: it holds the
  GeoPositionNode). Never pass `existing_graph`; set `graph_id`/`name` after `parse()`.
- The importer opens its own DB-API connection; it sees committed data only.
  `parse()` wraps any failure in `ImportError`.

## 4. The graph contract mini adds

Two attribute blocks, defined once in `pyarchinit_mini/graphproj/strat_graph.py`:

```python
node.attributes["pyarchinit"] = {
    "id_us": int | None, "sito": str, "area": str | None, "us": str,
    "unit_type": str, "description": str | None,
    "periodo": str | None, "fase": str | None,
    "row_id": str, "sub_group": str | None, "node_uuid": str | None,
}
# legacy keys kept for the ingestor and older callers
node.attributes["unit_type"], node.attributes["family"], node.attributes["EMid"]

graph.attributes["swimlane"] = {
    "site": str, "group_by": str,
    "rows": [{"row_id", "label", "periodo", "fase", "datazione", "is_fallback"}, ...],
}
```

Stratigraphic edges are ordinary `s3dgraphy` edges between two stratigraphic nodes,
`edge_type` = mini canonical (forward form only: `overlies`, `cuts`, `fills`, `abuts`,
`has_same_time`, `is_bonded_to`, `is_before`), `edge_id = f"{src}__{canonical}__{tgt}"`.
Edge normalisation is unchanged from today: inverse → forward with endpoint swap,
symmetric dedup, inverse dedup, per-canonical transitive reduction.

Helpers: `stratigraphic_nodes(graph)`, `stratigraphic_edges(graph)` (both endpoints
stratigraphic), `pyarchinit_attrs(node)`, `set_pyarchinit_attrs(node, …)`,
`new_strat_node(…)`, `set_swimlane(graph, …)`, `get_swimlane(graph)`.

## 5. Pipeline after the change

```
us_table / period_table ──PyArchInitImporter(connection_url, filters)──▶ s3dgraphy.Graph
        │                                                                     │
        ├─ load_us_rows()  ──▶ attach_pyarchinit_attributes()  (uuid ⇒ node, else name)
        ├─ load_period_rows() ─▶ set_swimlane()
        └─ rapporti ──rapporti_codec──▶ build_stratigraphic_edges() ──▶ add_stratigraphic_edges()
                                                                              │
   to_cytoscape(graph) ◀──────────────────────────────────────────────────────┤  /api/load (editor)
   graphml_writer.write_graphml(graph) ◀──────────────────────────────────────┤  yEd TableNode export
   graphml_io.writer.write_graphml(graph, path) ◀─────────────────────────────┤  auto-regen + /api/export/graphml (GraphMLExporter)
   GraphIngestor.preview/apply(graph) ◀── graphml_io.reader (GraphMLImporter) ─┘  yEd/EM import
   graph_to_db.write_graph(graph) ◀── graphml_reader.parse_graphml / heriverse_parser
```

`GraphProjector.populate_graph(session, site, *, area=None, group_by="none") -> Graph`
is the single projection entry point (callers: auto-regen, `/api/export/graphml`,
`/api/load/<site>`, `/api/export/<site>/yed-graphml`, `swimlane_state`).

Row correlation: a DB row is matched to the importer's node by `node_uuid`; rows with a
NULL uuid (legacy data) are matched by recomputing the importer's own node name
(`importer._resolve_node_name(row, "us")` + `graph.find_node_by_name`). Unmatched rows
are logged and skipped.

Target resolution for `rapporti`: `(area, us)` when the rapporto carries an area,
falling back to `us` alone (legacy 2-tuples).

## 6. Retired / kept

| Path | Fate |
|------|------|
| `graphproj/s3d_projector.py` (`ProjectedGraph`, `S3DProjector`) | **deleted** |
| `graphproj/projector.py` | rewritten on the importer |
| `graphproj/s3d_to_cytoscape.py`, `graphml_writer.py`, `graphml_reader.py`, `heriverse_parser.py`, `graph_to_db.py` | rewritten on `s3dgraphy.Graph` (same outputs) |
| `graphproj/ingestor.py` | US number from `pyarchinit` attrs, else trailing digits of the name |
| `graphproj/{rapporti_codec,edge_registry,exceptions,filesystem,ingest_plan,paradata_store,auto_regen}.py` | unchanged |
| `graphml_io/` (GraphMLExporter/Importer wrappers, yEd TableNode writer) | unchanged |
| `stratigraph/` | unchanged (D2) |
| `s3d_integration/s3d_converter.py` | unchanged (Heriverse JSON export; separate track) |

## 7. Constraints and known risks

- **Pre-release dependency**: `1.6.0.dev39` can change; the plan pins `<1.7` and the
  spike test (Task 0) is the canary for API drift.
- **In-memory SQLite is not supported** by the importer (needs a file URL). Tests use
  temp files; `connection_url_from_session` raises `ProjectionError` otherwise.
- **Performance**: the importer emits property/location/author nodes per US, so the
  graph is larger than today's; auto-regen runs synchronously after each US save.
  Measure on Adarte's largest site (Rimini Museo Fellini, ≈4066 legacy edges) before
  release; acceptance: edges within ±5 % of today's `S3DProjector` count and
  `populate_graph` < 3 s for that site.
- **Names with digits** (`A1.US12`): never derive the US number from all digits of the
  name; use the `pyarchinit` attributes, else trailing digits.
- **Rows without `node_uuid`** get a random uuid per projection, so their node ids are
  not stable across projections; the backfill migration already runs at startup, this
  only affects DBs never opened by mini.
- **rapporti in legacy free-text form** (`"copre 1002"`) are not parsed by
  `rapporti_codec` (list-of-lists only); they yield no edges, no error.

## 8. Out of scope (follow-ups to note in issue #2)

- WP4 bundle I/O through s3dgraphy (waits for the library; `stratigraph/` stays).
- `relations` mapping in s3dgraphy (#26) — when it lands, `strat_edges.py` can be
  reduced to a verifier.
- Round-tripping `node_uuid` from arbitrary yEd files in `graphml_reader` (the yEd
  writer now emits it; the minimal reader still keys on labels).
- `s3d_integration.s3d_converter.create_graph_from_us` (legacy JSON path).
