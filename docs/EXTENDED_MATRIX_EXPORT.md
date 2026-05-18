# Extended Matrix Export — User Guide

The Harris Matrix Editor can export its current state as a yEd-flavored
GraphML file compatible with pyarchinit QGIS plugin and yEd Desktop.

## Steps

1. Open the editor on a site (e.g. `/harris-creator/editor?site=Volterra`).
2. (Optional) Choose **Group by** in the toolbar to organise lanes by
   `period_phase` (default), `struttura`, `attivita`, `settore`, `area`,
   `ambient`, `saggio`, `quad_par`, or `none`.
3. Click **Export yEd GraphML** in the toolbar.

The file is saved at
`data/exports/harris_yed/<site_slug>-extmatrix.graphml` and offered for
download.

## What's inside

- `y:TableNode configuration="YED_TABLE_NODE"` root with one `y:Row` per lane
- All 38 keys d0..d37 (epochs_meta, EMID, pyarchinit.us / area / sito /
  unita_tipo / periodo_iniziale / fase_iniziale / rapporti /
  d_stratigrafica / d_interpretativa / documentazione / node_uuid /
  struttura / attivita / settore / ambient / saggio / quad_par /
  datazione_estesa, plus URI / description / nodegraphics / edgegraphics)
- Per-US `<node>` children with full `pyarchinit.*` payload
- Per-edge `<edge>` with `y:PolyLineEdge` and edge label

## Compatibility

- yEd Desktop 3.x — opens directly, preserves table layout
- pyarchinit QGIS plugin — round-trip via `pyarchinit.*` keys

## Round-trip

Export then re-import via `/import-graphml/` is idempotent: same node_uuid
matches, no duplicates created.
