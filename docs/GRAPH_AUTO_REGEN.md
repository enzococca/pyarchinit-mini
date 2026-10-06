# Graph auto-regen

Every time a US/USM record is saved, pyarchinit-mini-web rebuilds the
stratigraphic graph for that site:

```
data/paradata/<site_slug>/stratigraphy.graphml
```

This file is the projector's output (DB rows → s3dgraphy.Graph). Paradata
are NOT embedded in it (they live in `paradata.json` — see PARADATA_GUIDE).

Since 3.6.0 the projection is the s3dgraphy library's `PyArchInitImporter`
(typed stratigraphic nodes keyed by `node_uuid`) plus two thin mini layers:
the stratigraphic edges parsed from `rapporti` and the swimlane rows from
`period_table`. The regenerated GraphML therefore also carries the
library's qualia (`has_property`), location (`is_in_location`) and author
nodes, not only US nodes and stratigraphic edges.

## When it fires

- After `session.commit()` in the US save paths:
  - `app.py:create_us` and `app.py:edit_us` (form routes)
  - `three_d_builder_routes.py:/create-us` and `/update-us` (API routes)
- Best-effort: regen failure does NOT block the originating save (caller
  still receives 201). Failure is logged to `pyarchinit_mini.graphproj`
  logger.

## When it does NOT fire

- During bulk operations wrapped in `auto_regen.disable_regen()`:
  ```python
  from pyarchinit_mini.graphproj import auto_regen
  with auto_regen.disable_regen():
      for row in big_excel:
          us_service.create_us(row, session)
  # Manually trigger one regen per touched site at the end:
  for site in auto_regen._drain_touched_sites():
      auto_regen._trigger_graph_regen(site, session=session)
  ```
  (Excel/CSV bulk-import wiring is a known TODO — see Spec 2 plan §Known gaps.)

- When `PYARCHINIT_DISABLE_AUTO_REGEN=1` is set in the environment.

## Disabling for development

```bash
export PYARCHINIT_DISABLE_AUTO_REGEN=1
.venv/bin/python -m pyarchinit_mini.web_interface.app
```

US/USM saves work normally; `stratigraphy.graphml` simply isn't written.

## Concurrency

- Per-site flock (`data/paradata/<site>/.paradata.lock`) serializes
  concurrent regens for the same site. Cross-site regens run in parallel.
- The flock is held only for the write step (load → write → replace),
  not for the DB query.

## Performance

100-US site: ~50ms. 1500-US site (Volterra-scale): ~500ms (timings
measured before 3.6.0). Synchronous in the request handler today; large
deployments may want a background queue (out of scope for Spec 2).

Since 3.6.0, very large sites are slower: Rimini (990 US) takes ~10 s
versus ~1.3 s before, the time being spent in the library's node/edge
lookups. Because regen runs synchronously, a US save on such a site takes
correspondingly longer until this is addressed.

## Logs

- Python `logging` (`pyarchinit_mini.graphproj`) — INFO on success,
  EXCEPTION on failure with traceback.
- File-based `_regen.log` JSON-line writer is a Spec 3 TODO.
