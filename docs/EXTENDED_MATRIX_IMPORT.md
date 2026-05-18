# Extended Matrix Import — User Guide

This page describes how to import a pyarchinit Extended Matrix `.graphml`
file into pyarchinit-mini's database.

## When to use

You exported a Harris matrix from pyarchinit QGIS plugin (or from another
pyarchinit-mini instance) and want to populate `us_table`, `site_table`,
and `periodizzazione_table` from it.

## Steps

1. Navigate to **Tools → Import GraphML** in the sidebar.
2. Upload a `.graphml` file.
3. Review the preview — you'll see counts of records that will be created /
   updated / skipped per table.
4. Click **Apply** to commit the changes.

## What happens

- `site_table`: a row is created if `pyarchinit.sito` is new.
- `periodizzazione_table`: rows from `pyarchinit.epochs_meta` (graph-level).
  Upsert on `(sito, periodo_iniziale, fase_iniziale)`.
- `us_table`: upsert on `node_uuid` first, then `(sito, us)`. All
  `pyarchinit.*` keys are mapped to their corresponding columns.
- `us_relationships_table`: edges are imported with deduplication on
  the triple `(sito, us_from, us_to, relationship_type)`.

## Conflicts

If `node_uuid` matches an existing US in a **different** site, the preview
shows a conflict. Resolve manually by deleting the existing US or editing
the source file before re-importing.

## Files supported

- pyarchinit QGIS plugin Extended Matrix exports
- pyarchinit-mini Extended Matrix exports (round-trip)

Plain yEd files without `pyarchinit.us` keys are rejected with HTTP 400.
