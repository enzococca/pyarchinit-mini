# Pottery Sheet — Design Spec

- **Date:** 2026-05-13
- **Target version:** pyarchinit-mini v2.1.60
- **Author:** Enzo Cocca (brainstormed via Claude)
- **Status:** Approved for planning

## 1. Summary

Add full *Pottery* (ceramica) records management to pyarchinit-mini with 1:1
schema parity to PyArchInit-QGIS's `pottery_table`. The feature delivers a new
top-level entity alongside Site / US / Inventario Materiali, with CRUD across
all three interfaces (Web, Desktop GUI, CLI), media attachments, PDF/Excel/CSV
export and import, legacy QGIS database compatibility, and analytics.

## 2. Goals

- Pottery specialists can record sherds and vessels in pyarchinit-mini with the
  same schema they already use in PyArchInit-QGIS — round-trip import/export
  works without column loss.
- Legacy `pyarchinitcs_*.sqlite` files containing `pottery_table` are migrated
  automatically by the existing `upgrade_legacy_schema` (v2.1.56/57) without
  additional user action.
- The feature is consistent with the rest of pyarchinit-mini: sync columns,
  audit columns, media polymorphism, real-time concurrency, role-based auth,
  PDF/Excel/CSV export, Desktop GUI tab, analytics dashboard.

## 3. Non-Goals

- New AI features, new admin modules, new backup system — those are tracked
  as separate features in the same multi-bump cycle.
- i18n `_en` columns for free-text descriptions (`note`, `descrip_*`) — can be
  added later via ALTER TABLE without breaking import compatibility.
- Foreign keys from `pottery_table.sito` / `area` / `us` to the parent tables —
  QGIS uses free strings; we preserve that to avoid import failures on legacy
  data with orphan sherds.
- Bibliography table integration — the QGIS "Supplements > Bibliography" tab
  reads from a separate `bibliography_table` that does **not** exist in
  pyarchinit-mini yet. For v2.1.60 the Bibliography sub-tab renders a
  placeholder *"Bibliography integration coming in a future release"* with
  no schema work. Bibliography is a separate feature in its own release.

## 4. Schema

`pyarchinit_mini/models/pottery.py` defines `Pottery(BaseModel)` with
`__tablename__ = 'pottery_table'`. Inherits `created_at`, `updated_at`,
`entity_uuid`, `version_number`, `last_modified_by`, `last_modified_timestamp`,
`sync_status`, `editing_by`, `editing_since` from `BaseModel`.

### 4.1 Columns (32 + 9 inherited)

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id_rep` | Integer PK autoinc | no | matches QGIS PK |
| `id_number` | Integer | yes | catalog number; unique per `sito` |
| `sito` | Text | **no** | required for unique constraint to be effective |
| `area` | Text | yes | |
| `us` | Integer | yes | |
| `box` | Integer | yes | storage box |
| `photo` | Text | yes | legacy QGIS photo path |
| `drawing` | Text | yes | legacy QGIS drawing path |
| `anno` | Integer | yes | excavation year |
| `fabric` | Text | yes | |
| `percent` | Text | yes | preserved percentage, free text |
| `material` | Text | yes | broad class (ceramica, vetro, ...) |
| `form` | Text | yes | functional form (Olla, Ciotola, ...) |
| `specific_form` | Text | yes | sub-typology |
| `ware` | Text | yes | ware class |
| `munsell` | Text | yes | e.g. `7.5YR 5/6` |
| `surf_trat` | Text | yes | surface treatment |
| `exdeco` | Text | yes | exterior decoration code |
| `intdeco` | Text | yes | interior decoration code |
| `wheel_made` | Text | yes | `Yes`/`No`/`Indeterminate` |
| `descrip_ex_deco` | Text | yes | free description |
| `descrip_in_deco` | Text | yes | free description |
| `note` | Text | yes | free notes |
| `diametro_max` | Numeric(7,3) | yes | cm |
| `qty` | Integer | yes | quantity, ≥ 1 when set |
| `diametro_rim` | Numeric(7,3) | yes | cm |
| `diametro_bottom` | Numeric(7,3) | yes | cm |
| `diametro_height` | Numeric(7,3) | yes | cm |
| `diametro_preserved` | Numeric(7,3) | yes | cm |
| `specific_shape` | Text | yes | morphological detail |
| `bag` | Integer | yes | field bag number |
| `sector` | Text | yes | excavation sector |

### 4.2 Constraints and indexes

- `UniqueConstraint('sito', 'id_number', name='ID_rep_unico')` — matches QGIS.
- `Index('ix_pottery_sito_area_us', 'sito', 'area', 'us')`
- `Index('ix_pottery_form', 'form')`
- `Index('ix_pottery_fabric', 'fabric')`

### 4.3 Migration & legacy compatibility

- `migrations.py` ensures `CREATE TABLE pottery_table` runs on first boot for
  existing DBs (uses `Base.metadata.create_all(engine, tables=[Pottery.__table__], checkfirst=True)`).
- `upgrade_legacy_schema` in `ImportExportService` (v2.1.56) automatically
  picks up `pottery_table` because it walks `Base.metadata.tables`: missing
  table is created, existing legacy table gets the 9 sync columns added via
  ALTER TABLE, `entity_uuid` / `created_at` / `updated_at` / `sync_status`
  back-filled, Italian dates in any Date/DateTime column normalised.
- The "Migrate Database" wizard (`/admin/database/migrate-database`) gains
  `'pottery_table'` in its migratable-table list with order
  `site_table → us_table → pottery_table`.

## 5. Service Layer

`pyarchinit_mini/services/pottery_service.py` exposes `PotteryService` with:

- CRUD: `create_pottery`, `get_pottery_by_id`, `get_pottery_dto_by_id`,
  `update_pottery`, `delete_pottery`.
- Listing: `get_all_pottery(page, size, filters)`, `count_pottery(filters)`,
  `search_pottery(q, page, size)`, `get_pottery_by_site/us/form`.
- Validation helpers: `_validate_unique_sito_idnumber` (hard),
  `_validate_us_exists` (**warning-only**, never blocks insert).
- Stats: `get_form_distribution`, `get_fabric_distribution`,
  `get_ware_distribution`, `count_by_site`.
- MNI: `calculate_mni(sito, area=None, us=None)` returns
  `{group_key: mni}` grouped by `form+fabric+ware`.

`pyarchinit_mini/services/pottery_dto.py` defines `PotteryDTO` dataclass with
all 32 + sync fields, `from_model` and `to_dict` classmethods.

### 5.1 Validation rules

- `sito` required (NOT NULL).
- `id_number` required when set → enforce
  `UniqueConstraint(sito, id_number)` with pre-insert check for friendlier
  error messages.
- `us` value triggers existence check on `us_table(sito, area, us)` —
  **warning logged, insert proceeds** (legacy data tolerance).
- `qty` ≥ 1 when set; reject negatives or zero.
- `percent`: free text, but if it contains a numeric portion, must be 0–100.
- `munsell`: free text, no regex.
- `wheel_made`: form provides a dropdown `Yes / No / Indeterminate`, but the
  column accepts any string for legacy compatibility.

### 5.2 Concurrency / sync

Delegated entirely to `BaseModel` columns and the existing
`concurrency_manager.py` — no pottery-specific work required.

## 6. Web Routes & Templates

Routes registered inline in `app.py` via `_register_pottery_routes(app)`
helper called from `create_app()`. Endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/pottery` | list (filters: `sito`, `area`, `us`, `form`, `fabric`, `q`) |
| GET | `/pottery/create` | form (tab 1 active) |
| POST | `/pottery/create` | insert + redirect to detail |
| GET | `/pottery/<id_rep>` | detail view |
| GET | `/pottery/<id_rep>/edit` | edit form |
| POST | `/pottery/<id_rep>/edit` | update |
| POST | `/pottery/<id_rep>/delete` | delete (confirm modal) |
| GET | `/pottery/<id_rep>/media` | open media manager modal |
| GET | `/export/pottery/excel` | batch Excel (filters from query) |
| GET | `/export/pottery/csv` | batch CSV |
| POST | `/import/pottery/excel` | batch Excel/CSV import (multipart) |
| GET | `/export/pottery_pdf` | batch PDF |
| GET | `/export/pottery_single_pdf/<id_rep>` | single-record PDF |
| GET | `/api/pottery/forms` | autocomplete distinct values + thesaurus |
| GET | `/api/pottery/fabrics` | autocomplete |
| GET | `/api/pottery/wares` | autocomplete |
| GET | `/api/pottery/stats` | JSON for analytics dashboard |
| GET | `/api/media/pottery` | media list for selector (parallel to inventario) |

### 6.1 Templates

`templates/pottery/`:

- `list.html` — paginated list with filter bar, action buttons
  (*+ Nuovo*, *Excel*, *CSV*, *PDF*, *Import*).
- `form.html` — 3-tab layout matching QGIS:
  - **Description data** — site / area / us / sector / year / box / bag /
    id_number / material / form / specific_form / specific_shape /
    photo / drawing / note + *Manage media* button (opens shared modal).
  - **Technical Data** — fabric / ware / munsell / percent / surf_trat /
    wheel_made / exdeco / intdeco / descrip_ex_deco / descrip_in_deco /
    qty / 5 × diametro_*.
  - **Supplements** — sub-tabs:
    - *Bibliography* — placeholder panel
      *"Bibliography integration coming in a future release"*; no data
      source until a dedicated `bibliography_table` feature ships.
    - *Statistic* — MNI card, form/fabric/ware distribution charts via
      Chart.js, total qty for the same `sito+area+us` context.
- `detail.html` — read-only same 3-tab layout, *Media attachments*
  thumbnail grid, action bar.
- `_row_card.html` — partial for global search re-use.

### 6.2 Navigation

`templates/base.html` `Records ▾` menu gains *Pottery* between *Inventario
Materiali* and *Datazioni*.

## 7. Media Attachments

`media_table` is already polymorphic via `entity_type` + `entity_id`. Pottery
uses `entity_type='pottery'` and `entity_id=pottery.id_rep`.

Changes:

- `app.py:288` — `entity_type` SelectField adds `('pottery', 'Pottery')`.
- `app.py:2682-2706` upload route — `elif entity_type == 'pottery':` branch
  validates the pottery row exists.
- New endpoint `GET /api/media/pottery` returns
  `[{id_rep, sito, id_number, form, fabric}]` for the upload form selector.
- `templates/pottery/form.html` Manage media button opens the shared
  `_media_manager_modal.html` with `entity_type=pottery&entity_id={{ id_rep }}`.

### 7.1 Legacy QGIS path migration

The QGIS `photo` and `drawing` columns hold filesystem paths from the QGIS
machine. On detail view, if these are set and no `media_table` row exists
yet for the pottery, render them as *Legacy file paths* read-only, with a
*Convert to media_table entries* button. The button scans each path,
copies the file into `static/uploads/`, creates `media_table` +
`media_thumb_table` rows, and clears the legacy path on the pottery row.
Missing files are reported in a non-blocking flash.

## 8. PDF Export

`pyarchinit_mini/services/pottery_pdf_service.py` renders 1 sheet per A4
page using WeasyPrint, replicating the layout of
`pyarchinit_exp_POTTERYsheet_pdf.py` from PyArchInit-QGIS.

- Template: `templates/pdf/pottery_sheet.html` with print-CSS.
- Header: site + id_rep + id_number.
- Sections: Identification (area/us/sector/year/box/bag), Description
  (material/form/specific_form/specific_shape), Technical
  (fabric/ware/munsell/surf_trat/wheel_made/percent + ext/int deco rows),
  Measurements (qty + 5 diametri), Media (up to 6 thumbnails), Notes.
- Footer: `pyarchinit-mini v<version> · printed <date>`.
- Logo: reuses `logo/pyarchinit_logo.png`.

Routes:
- `/export/pottery_pdf` — multi-record PDF with filters from query string.
- `/export/pottery_single_pdf/<id_rep>` — single-record.

## 9. Excel + CSV + Legacy QGIS Import/Export

### 9.1 Excel/CSV export

- Pandas + openpyxl pipeline (mirroring `app.py:4778-4922`).
- Headers = QGIS column names (32 cols, sync excluded) — re-importable in QGIS.
- Sheet `pottery` + sheet `metadata` (export date, version, applied filters).
- Filters from query string (`?sito=&form=&fabric=&us=`).

### 9.2 Excel/CSV import

- Parse pandas → per-row validation (sito required, type coercion for
  Integer / Numeric, Italian-date normalisation via existing
  `_normalise_date`).
- Duplicate handling — radio in upload form:
  - `skip`: skip rows whose `(sito, id_number)` exists.
  - `update`: overwrite existing rows.
  - `renumber`: assign a fresh `id_number` to incoming rows.
- Final report: `rows_inserted`, `rows_updated`, `rows_skipped`, per-row
  errors.

### 9.3 Legacy QGIS database import

Two paths, both already partially in place:

1. **Automatic, via `upgrade_legacy_schema`:** including `Pottery` in
   `Base.metadata` makes the v2.1.56/57 upgrade path handle CREATE +
   ALTER + backfill of sync columns when a user uploads a legacy
   `pyarchinitcs_*.sqlite`. No new code.
2. **Wizard, via `/admin/database/migrate-database`:** add
   `'pottery_table'` to the migratable list with dependency order
   `site_table → us_table → pottery_table`. The migration loop already
   has type-driven Boolean coercion (v2.1.59), Italian date
   normalisation (v2.1.56), per-row error tolerance — works as-is.

## 10. Desktop GUI

`pyarchinit_mini/desktop_gui/pottery_panel.py`:

- Registered in `main_window.py:206` notebook with key `pottery`.
- Toolbar: `[+ New] [Edit] [Delete] [Refresh] [Excel→] [←Excel] [PDF] [🔍 Search]`.
- Left: `ttk.Treeview` with columns
  `id_rep / sito / area / us / form / fabric / qty`, sortable headers,
  double-click → edit.
- Right: detail pane with `ttk.Notebook` (3 tabs identical to web form).
- Bottom status bar with row count + active filters.

`pyarchinit_mini/desktop_gui/pottery_dialog_extended.py` — modal
*New / Edit Pottery* with media attach/preview (PIL.ImageTk thumbnails).

Menu changes in `main_window.py`:

- `View → Pottery`
- `File → Export → Pottery (Excel/CSV/PDF)`
- `File → Import → Pottery (Excel/CSV)`

## 11. Analytics

### 11.1 Web dashboard

Three new Chart.js panels in
`templates/analytics/dashboard.html`:

1. *Pottery — Form distribution* — donut, top 10 + Other.
2. *Pottery — Fabric distribution* — horizontal bar.
3. *Pottery — Ware over time* — stacked bar, X = `anno`, stack = `ware`.

Plus an MNI card: *Min Number of Individuals: N (group by sito+form+fabric+ware)*.

API endpoint `/api/pottery/stats?sito=&area=&us=` returns:

```json
{
  "total": 4521,
  "by_form": [{"form": "Olla", "count": 312}],
  "by_fabric": [{"fabric": "Coarse ware", "count": 1024}],
  "by_ware": [{"ware": "African Red Slip", "count": 89}],
  "by_anno": [{"anno": 2023, "count": 1502}],
  "mni": 478
}
```

### 11.2 Desktop analytics

`analytics_dialog.py` gains 3 matplotlib charts matching the web set,
reusing existing donut/bar helpers.

## 12. CLI (optional)

The existing `pyarchinit-mini-migrate` command picks up `pottery_table`
automatically once it is in `Base.metadata`. No new CLI work required
for v2.1.60; a dedicated `pyarchinit-pottery` CLI can be added later.

## 13. Testing Strategy

- **Unit tests** (`tests/unit/test_pottery_service.py`):
  - Model creation, UniqueConstraint enforcement, sync columns autoset.
  - Service CRUD round-trip.
  - Validation: `sito` required, `qty` ≥ 1, `us_exists` warning-only.
  - MNI calculation against fixture dataset.
- **Integration tests** (`tests/integration/test_pottery_routes.py`):
  - All 17 web routes with auth fixture.
  - Excel/CSV export + re-import round-trip.
  - PDF generation (just non-empty bytes + valid PDF magic).
  - Media attach via shared media flow.
- **Migration tests** (`tests/migration/test_legacy_pottery_upgrade.py`):
  - Load fixture `pyarchinitcs_legacy_with_pottery.sqlite`, run
    `upgrade_legacy_schema`, assert pottery rows preserved, sync columns
    backfilled, dates normalised.
  - Migrate-database wizard end-to-end SQLite → Postgres for pottery.

## 14. Rollout

- Single PyPI release **v2.1.60**: model + service + routes + templates
  + desktop panel + analytics + tests.
- Deploy to Adarte (`ganesh@10.0.1.13`) via the established expect-SSH
  flow used in v2.1.55–2.1.59.
- Marco's Railway instance picks up v2.1.60 from PyPI on next redeploy.
- No data migration is destructive; existing DBs gain `pottery_table`
  the first time `migrations.py` runs after upgrade.

## 15. Open questions

None — all design decisions resolved during brainstorming. Implementation
plan to follow.
