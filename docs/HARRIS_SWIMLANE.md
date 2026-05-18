# Harris Swimlane Editor — User Guide

The Harris Matrix Creator's swimlane editor lets you view and edit
stratigraphic graphs with horizontal rows representing temporal
periods+phases.

## Opening the editor

Navigate to `/harris-creator/editor?site=<SITE_NAME>`. The editor
auto-loads:
- **Rows** (swimlanes) from `period_table` for your site; if empty,
  derived from distinct `periodo_iniziale + fase_iniziale` values in
  `periodizzazione_table` + `us_table`.
- **US records** placed in their respective row (auto-layout).
- **Edges** from `rapporti` strings (parsed via canonical edge names
  like `overlies`, `is_after`, `cuts`).

## Drag-drop a US to a different row

Drag the US node from one row to another. The change is tracked
client-side — the "● Unsaved changes" indicator appears top-right.
**No DB write happens until you click Save.**

## Create a new row

Click "**+ New Row**". Prompts:
- **Period name** (required, e.g. "Period 4")
- **Phase name** (optional, e.g. "a")
- **Start date** (optional, year — negative for BCE)
- **End date** (optional)

The row is added to `period_table` immediately (idempotent — existing
combinations reused). Appears at the top (most-recent placement).

## Save changes

Click "**💾 Save**" to commit all pending changes to the DB:
- US updates (row reassignments)
- US inserts (new records)
- US deletes

After a successful save, Spec 2's auto-regen fires too, refreshing
`data/paradata/<site>/stratigraphy.graphml` for downstream consumers.

## Export yEd GraphML

Click "**⬇ Export yEd GraphML**" to download a yEd-flavored GraphML
file: `<site>-harris-yed.graphml`. Open in yEd Desktop to edit layout
with full yEd swimlane support. On-demand — no auto-regen of this file.

## Limitations

- **Last-writer-wins on concurrent edits** (Spec 4 will add real-time
  conflict resolution)
- **No round-trip from yEd Desktop back to editor** (Spec 3-ter)
- **`period_table` is cross-site**: a row created in site A's editor is
  visible in site B too. Per-site isolation is Spec 4 if needed.
- **Multi-period US**: an US with both `periodo_iniziale` and
  `periodo_finale` is placed only in the starting row.
