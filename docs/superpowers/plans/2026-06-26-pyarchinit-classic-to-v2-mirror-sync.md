# Sync mirror `pyarchinit` → `pyarchinit_v2` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a scheduled one-way sync engine that mirrors data from the classic `pyarchinit` Postgres DB into `pyarchinit_v2` (the mini schema), table-by-table, keyed on the (preserved) primary key.

**Architecture:** A small Python package `pyarchinit_mini/sync/` with pure-logic units (config, column policy, type-cast expression builder, diff) that are unit-tested without a DB, plus a thin DB layer (introspection + engine + runner) tested against two local Postgres test databases. Invoked as `python -m pyarchinit_mini.sync`. Two direct `psycopg2` connections (source = classic, target = v2); only SELECT on the source, writes only to the target.

**Tech Stack:** Python 3.12, `psycopg2` (already a dependency), stdlib `json`/`argparse`/`logging`/`dataclasses`, `pytest`. No new runtime dependencies. Postgres 17 / PostGIS 3.4 on both DBs.

## Global Constraints

- Python **3.12** (Adarte venv `/home/ganesh/pyarchinit_env`). Runtime: only `psycopg2` + stdlib. No new deps.
- **One-way only:** source = `pyarchinit` (classic), target = `pyarchinit_v2`. NEVER write to the source; only `SELECT` there.
- **Dry-run is the default.** Writes happen only with `--apply`.
- **Keyed on primary key** (preserved 1:1 between DBs). Per-table mode: `full` | `keyset` | `replace`.
- **DELETE enabled by default** (rows gone from classic are removed from v2).
- **Preserve columns** (never written from classic; excluded from row-hash and from UPDATE), copy verbatim:
  `order_layer, cont_per, entity_uuid, node_uuid, version_number, created_at, updated_at, last_modified_timestamp, last_modified_by, editing_since, editing_by, audit_trail, sync_status` — plus every column present in v2 but absent in the classic, plus any `*_en` column.
- **Exclude tables** (Postgres/PostGIS system base tables in `public`): `spatial_ref_sys, raster_columns, raster_overviews`. **Never exclude `public.layer`** (real data table).
- **DSNs come from environment variables** — never hardcode credentials in the repo or in committed config.
- Commits: **no AI-attribution** trailer or footer (per repo policy).
- Identifiers in generated SQL are always **double-quoted** (`"col"`, `"table"`).

---

## File Structure

- `pyarchinit_mini/sync/__init__.py` — package marker + public exports.
- `pyarchinit_mini/sync/config.py` — `Config` dataclass + `load_config()`; resolves DSNs from env, applies defaults, reads optional JSON override file.
- `pyarchinit_mini/sync/policy.py` — **pure** helpers: `select_mode()`, `common_data_columns()`, `preserve_set_for_table()`.
- `pyarchinit_mini/sync/transform.py` — **pure** SQL builders: `cast_expr()`, `row_hash_sql()`, `build_pk_hash_select()`, `build_insert_select()`, `build_update_set()`.
- `pyarchinit_mini/sync/diff.py` — **pure** diff: `diff_by_hash()`, `diff_by_keyset()`, `Diff` dataclass.
- `pyarchinit_mini/sync/introspect.py` — DB introspection: `base_tables()`, `column_types()`, `primary_key()`, `geometry_columns()`, `row_count()`, `signature()`.
- `pyarchinit_mini/sync/state.py` — `sync_state` table: `ensure_state_table()`, `get_signature()`, `record_result()`.
- `pyarchinit_mini/sync/engine.py` — `sync_table()`: orchestrates one table (mode dispatch, transaction, counts).
- `pyarchinit_mini/sync/runner.py` — `discover_tables()`, `run()`: iterate tables, logging, summary.
- `pyarchinit_mini/sync/__main__.py` — argparse CLI → `load_config()` → `run()`.
- `pyarchinit_mini/sync/sync_config.example.json` — documented example config (committed; real config with env names lives on the server).
- `tests/sync/__init__.py`
- `tests/sync/test_config.py`, `test_policy.py`, `test_transform.py`, `test_diff.py` — pure unit tests (no DB).
- `tests/sync/conftest.py` — Postgres fixtures (skip if `TEST_SYNC_SRC_DSN`/`TEST_SYNC_TGT_DSN` unset).
- `tests/sync/test_introspect.py`, `test_engine.py`, `test_runner.py` — integration tests.
- `docs/superpowers/runbooks/sync-classic-to-v2.md` — operational runbook (first run, cron, rollback).

**Result of these data facts (from the spec):** PKs are preserved (`id_sito` max 1977, `id_us` 30893, `id_invmat` 5075 identical on both sides); PostGIS 3.4 on both; ~107 mirrored tables with data, large GIS layers already populated and aligned.

---

### Task 1: Package scaffold + configuration

**Files:**
- Create: `pyarchinit_mini/sync/__init__.py`
- Create: `pyarchinit_mini/sync/config.py`
- Create: `pyarchinit_mini/sync/sync_config.example.json`
- Create: `tests/sync/__init__.py`
- Test: `tests/sync/test_config.py`

**Interfaces:**
- Produces:
  - `DEFAULT_PRESERVE: frozenset[str]`, `DEFAULT_EXCLUDE: frozenset[str]`
  - `@dataclass class Config(source_dsn: str, target_dsn: str, size_threshold_keyset: int = 200_000, exclude_tables: frozenset[str] = DEFAULT_EXCLUDE, preserve_columns_global: frozenset[str] = DEFAULT_PRESERVE, overrides: dict[str, dict] = {}, weekly_full_refresh: bool = True, delete_enabled: bool = True)`
  - `load_config(path: str | None = None, env: Mapping[str, str] = os.environ) -> Config`

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_config.py
import json, pytest
from pyarchinit_mini.sync.config import load_config, Config, DEFAULT_PRESERVE

def test_load_config_resolves_dsn_from_env(tmp_path):
    cfg_file = tmp_path / "c.json"
    cfg_file.write_text(json.dumps({
        "source_dsn_env": "SRC", "target_dsn_env": "TGT",
        "size_threshold_keyset": 50,
        "overrides": {"shape_finali_polygon": {"mode": "replace"}},
    }))
    env = {"SRC": "postgresql://x@h/classic", "TGT": "postgresql://x@h/v2"}
    cfg = load_config(str(cfg_file), env=env)
    assert cfg.source_dsn == "postgresql://x@h/classic"
    assert cfg.target_dsn == "postgresql://x@h/v2"
    assert cfg.size_threshold_keyset == 50
    assert cfg.overrides["shape_finali_polygon"]["mode"] == "replace"
    assert "order_layer" in cfg.preserve_columns_global
    assert cfg.delete_enabled is True

def test_load_config_missing_env_raises():
    with pytest.raises(KeyError):
        load_config(None, env={})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: pyarchinit_mini.sync.config`

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/sync/__init__.py
"""One-way sync engine: classic pyarchinit -> pyarchinit_v2 (mini)."""
```

```python
# pyarchinit_mini/sync/config.py
import json, os
from dataclasses import dataclass, field
from typing import Mapping

DEFAULT_PRESERVE = frozenset({
    "order_layer", "cont_per", "entity_uuid", "node_uuid", "version_number",
    "created_at", "updated_at", "last_modified_timestamp", "last_modified_by",
    "editing_since", "editing_by", "audit_trail", "sync_status",
})
DEFAULT_EXCLUDE = frozenset({"spatial_ref_sys", "raster_columns", "raster_overviews"})

@dataclass
class Config:
    source_dsn: str
    target_dsn: str
    size_threshold_keyset: int = 200_000
    exclude_tables: frozenset = DEFAULT_EXCLUDE
    preserve_columns_global: frozenset = DEFAULT_PRESERVE
    overrides: dict = field(default_factory=dict)
    weekly_full_refresh: bool = True
    delete_enabled: bool = True

def load_config(path: str | None = None, env: Mapping[str, str] = os.environ) -> Config:
    raw = {}
    if path:
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
    src_env = raw.get("source_dsn_env", "PYARCHINIT_CLASSIC_DSN")
    tgt_env = raw.get("target_dsn_env", "DATABASE_URL")
    source_dsn = env[src_env]          # KeyError if missing — intentional
    target_dsn = env[tgt_env]
    preserve = DEFAULT_PRESERVE | frozenset(raw.get("preserve_columns_global", []))
    exclude = DEFAULT_EXCLUDE | frozenset(raw.get("exclude_tables", []))
    return Config(
        source_dsn=source_dsn, target_dsn=target_dsn,
        size_threshold_keyset=int(raw.get("size_threshold_keyset", 200_000)),
        exclude_tables=exclude, preserve_columns_global=preserve,
        overrides=raw.get("overrides", {}),
        weekly_full_refresh=bool(raw.get("weekly_full_refresh", True)),
        delete_enabled=bool(raw.get("delete_enabled", True)),
    )
```

```json
// pyarchinit_mini/sync/sync_config.example.json
{
  "source_dsn_env": "PYARCHINIT_CLASSIC_DSN",
  "target_dsn_env": "DATABASE_URL",
  "size_threshold_keyset": 200000,
  "exclude_tables": [],
  "preserve_columns_global": [],
  "overrides": { "shape_finali_polygon": { "mode": "replace" } },
  "weekly_full_refresh": true,
  "delete_enabled": true
}
```

(`tests/sync/__init__.py` is empty.)

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_config.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/__init__.py pyarchinit_mini/sync/config.py \
        pyarchinit_mini/sync/sync_config.example.json tests/sync/__init__.py tests/sync/test_config.py
git commit -m "feat(sync): config loader for classic->v2 mirror"
```

---

### Task 2: Column policy + mode selection (pure)

**Files:**
- Create: `pyarchinit_mini/sync/policy.py`
- Test: `tests/sync/test_policy.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `select_mode(rowcount: int, has_pk: bool, threshold: int, override: str | None) -> str` → `"full" | "keyset" | "replace"`
  - `preserve_set_for_table(global_preserve: frozenset[str], src_cols: set[str], tgt_cols: set[str], extra: list[str]) -> set[str]` (global + columns only-in-target + `*_en` + extra)
  - `common_data_columns(src_cols: set[str], tgt_cols: set[str], preserve: set[str]) -> list[str]` (sorted intersection minus preserve)

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_policy.py
from pyarchinit_mini.sync.policy import select_mode, preserve_set_for_table, common_data_columns

def test_select_mode_override_wins():
    assert select_mode(10, True, 200_000, "replace") == "replace"

def test_select_mode_no_pk_is_replace():
    assert select_mode(10, False, 200_000, None) == "replace"

def test_select_mode_large_is_keyset():
    assert select_mode(500_000, True, 200_000, None) == "keyset"

def test_select_mode_small_is_full():
    assert select_mode(1915, True, 200_000, None) == "full"

def test_preserve_set_includes_target_only_and_en_cols():
    p = preserve_set_for_table(
        frozenset({"order_layer"}),
        src_cols={"sito", "descrizione"},
        tgt_cols={"sito", "descrizione", "descrizione_en", "node_uuid", "order_layer"},
        extra=["custom_col"],
    )
    assert {"order_layer", "descrizione_en", "node_uuid", "custom_col"} <= p
    assert "sito" not in p

def test_common_data_columns_excludes_preserved():
    cols = common_data_columns(
        src_cols={"id_us", "sito", "us", "order_layer"},
        tgt_cols={"id_us", "sito", "us", "order_layer", "node_uuid"},
        preserve={"order_layer", "node_uuid"},
    )
    assert cols == ["id_us", "sito", "us"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_policy.py -v`
Expected: FAIL with `ModuleNotFoundError: pyarchinit_mini.sync.policy`

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/sync/policy.py
def select_mode(rowcount: int, has_pk: bool, threshold: int, override: str | None) -> str:
    if override in ("full", "keyset", "replace"):
        return override
    if not has_pk:
        return "replace"
    if rowcount > threshold:
        return "keyset"
    return "full"

def preserve_set_for_table(global_preserve, src_cols, tgt_cols, extra):
    target_only = set(tgt_cols) - set(src_cols)
    en_cols = {c for c in tgt_cols if c.endswith("_en")}
    return set(global_preserve) | target_only | en_cols | set(extra or [])

def common_data_columns(src_cols, tgt_cols, preserve):
    return sorted((set(src_cols) & set(tgt_cols)) - set(preserve))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_policy.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/policy.py tests/sync/test_policy.py
git commit -m "feat(sync): column policy and per-table mode selection"
```

---

### Task 3: Type-cast & SQL builders (pure)

**Files:**
- Create: `pyarchinit_mini/sync/transform.py`
- Test: `tests/sync/test_transform.py`

**ARCHITECTURE NOTE (read first):** source and target are **separate connections** — no cross-DB `SELECT`. So source rows are read into Python and re-inserted/updated into the target with **value placeholders** (`%s`). `cast_expr` therefore wraps a *placeholder*, not a column reference, so the safe coercions (varchar→int guard, EU dates, etc.) run in the target's INSERT/UPDATE SQL around each parameter. `row_hash_sql` stays **column-based** because it runs separately on each DB's own table (for change detection).

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `cast_expr(src_type: str, tgt_type: str, tgt_maxlen: int | None, ph: str = "%s") -> str` — SQL expression that coerces a single value `ph` to the target column type (festos `expr()` logic; geometry → `(%s)::geometry`).
  - `row_hash_sql(columns: list[str]) -> str` — `md5("a"::text||'|'||...)` over the given columns (uses `||`, not `concat_ws`, to avoid the 100-arg limit).
  - `build_pk_hash_select(table: str, pk: list[str], hash_cols: list[str]) -> str` — `SELECT <pk...>, md5(...) FROM public."table"`.
  - `build_insert(table: str, cols: list[str], value_exprs: list[str], fill: dict[str,str]) -> str` — `INSERT INTO public."table" (cols + fill-keys) VALUES (value_exprs..., fill-vals...)`. `value_exprs` are `cast_expr` fragments (each containing one `%s`); `fill` maps extra columns → SQL literals (e.g. `now()`).
  - `build_update(table: str, set_cols: list[str], set_exprs: list[str], pk: list[str]) -> str` — `UPDATE public."table" SET col = <expr> ... WHERE pk = %s ...` (set_exprs are `cast_expr` fragments; pk matched by trailing `%s`).

> NOTE: `cast_expr` mirrors `scratchpad/merge2.py::expr` but over a placeholder instead of a column.

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_transform.py
from pyarchinit_mini.sync.transform import (
    cast_expr, row_hash_sql, build_pk_hash_select, build_insert, build_update)

def test_cast_varchar_to_integer_guards_non_numeric():
    e = cast_expr("character varying", "integer", None)
    assert "~ '^-?[0-9]+$'" in e and "::integer" in e and "%s" in e

def test_cast_bigint_to_boolean():
    e = cast_expr("bigint", "boolean", None)
    assert "false" in e and "true" in e and "%s" in e

def test_cast_varchar_to_date_handles_eu_formats():
    e = cast_expr("character varying", "date", None)
    assert "DD/MM/YYYY" in e and "DD-MM-YYYY" in e

def test_cast_text_to_varchar_truncates():
    e = cast_expr("text", "character varying", 100)
    assert "left(" in e and "100" in e

def test_cast_geometry_uses_geometry_cast():
    assert cast_expr("geometry", "geometry", None) == "(%s)::geometry"

def test_row_hash_uses_pipe_operator_not_concat_ws():
    h = row_hash_sql(["a", "b"])
    assert h.startswith("md5(") and "||'|'||" in h and "concat_ws" not in h

def test_build_pk_hash_select():
    s = build_pk_hash_select("us_table", ["id_us"], ["sito", "us"])
    assert s.lower().startswith("select")
    assert '"id_us"' in s and 'from public."us_table"' in s.lower()

def test_build_insert_includes_fill_and_value_exprs():
    sql = build_insert("us_table", ["sito"], ["(%s)::text"], {"created_at": "now()", "version_number": "1"})
    assert 'insert into public."us_table"' in sql.lower()
    assert '"sito"' in sql and '"created_at"' in sql and "now()" in sql and "(%s)::text" in sql

def test_build_update_sets_and_pk_where():
    sql = build_update("site_table", ["descrizione"], ["(%s)::text"], ["id_sito"])
    assert 'update public."site_table" set "descrizione" = (%s)::text' in sql.lower()
    assert 'where "id_sito" = %s' in sql.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_transform.py -v`
Expected: FAIL with `ModuleNotFoundError: pyarchinit_mini.sync.transform`

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/sync/transform.py
def cast_expr(src_type: str, tgt_type: str, tgt_maxlen: int | None, ph: str = "%s") -> str:
    t = tgt_type
    if t in ("geometry", "geography"):
        return f"({ph})::{t}"
    if t == "character varying" and tgt_maxlen:
        return f"left(({ph})::text, {tgt_maxlen})"
    if t == "text":
        return f"({ph})::text"
    if t in ("integer", "bigint", "smallint"):
        if src_type in ("character varying", "text"):
            return (f"(CASE WHEN btrim(({ph})::text) ~ '^-?[0-9]+$' "
                    f"THEN btrim(({ph})::text)::{t} ELSE NULL END)")
        return f"({ph})::{t}"
    if t == "boolean":
        if src_type == "boolean":
            return f"({ph})"
        if src_type in ("bigint", "integer", "smallint", "numeric", "double precision"):
            return (f"(CASE WHEN {ph} IS NULL THEN NULL "
                    f"WHEN ({ph})::numeric=0 THEN false ELSE true END)")
        return (f"(CASE WHEN btrim(({ph})::text) IN ('1','true','t','yes','si','y') THEN true "
                f"WHEN btrim(({ph})::text) IN ('0','false','f','no','n','') THEN false ELSE NULL END)")
    if t == "date":
        if src_type == "date":
            return f"({ph})"
        return ("(CASE "
                f"WHEN btrim(({ph})::text) ~ '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}' THEN substr(btrim(({ph})::text),1,10)::date "
                f"WHEN btrim(({ph})::text) ~ '^[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{4}}$' THEN to_date(btrim(({ph})::text),'DD/MM/YYYY') "
                f"WHEN btrim(({ph})::text) ~ '^[0-9]{{1,2}}-[0-9]{{1,2}}-[0-9]{{4}}$' THEN to_date(btrim(({ph})::text),'DD-MM-YYYY') "
                "ELSE NULL END)")
    if t == "timestamp with time zone":
        return f"({ph})::timestamptz"
    if t == "timestamp without time zone":
        return f"({ph})::timestamp"
    if t == "double precision":
        return f"({ph})::double precision"
    if t == "numeric":
        return f"({ph})::numeric"
    return f"({ph})"   # matching/other types: pass the value through

def row_hash_sql(columns: list[str]) -> str:
    parts = "||'|'||".join(f"coalesce(\"{c}\"::text,'')" for c in columns)
    return f"md5({parts})" if columns else "md5('')"

def build_pk_hash_select(table: str, pk: list[str], hash_cols: list[str]) -> str:
    pk_sql = ", ".join(f'"{c}"' for c in pk)
    return f'SELECT {pk_sql}, {row_hash_sql(hash_cols)} FROM public."{table}"'

def build_insert(table: str, cols: list[str], value_exprs: list[str], fill: dict) -> str:
    all_cols = cols + list(fill.keys())
    col_sql = ", ".join(f'"{c}"' for c in all_cols)
    val_sql = ", ".join(value_exprs + list(fill.values()))
    return f'INSERT INTO public."{table}" ({col_sql}) VALUES ({val_sql})'

def build_update(table: str, set_cols: list[str], set_exprs: list[str], pk: list[str]) -> str:
    assigns = ", ".join(f'"{c}" = {e}' for c, e in zip(set_cols, set_exprs))
    where = " AND ".join(f'"{c}" = %s' for c in pk)
    return f'UPDATE public."{table}" SET {assigns} WHERE {where}'
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_transform.py -v`
Expected: PASS (9 passed)

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/transform.py tests/sync/test_transform.py
git commit -m "feat(sync): type-cast and SQL builders (festos expr reuse)"
```

---

### Task 4: Diff logic (pure)

**Files:**
- Create: `pyarchinit_mini/sync/diff.py`
- Test: `tests/sync/test_diff.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `@dataclass class Diff(inserts: list, updates: list, deletes: list)` (each a list of pk-tuples)
  - `diff_by_hash(source: dict[tuple, str], target: dict[tuple, str]) -> Diff`
  - `diff_by_keyset(source_keys: set[tuple], target_keys: set[tuple]) -> Diff` (updates always empty)

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_diff.py
from pyarchinit_mini.sync.diff import diff_by_hash, diff_by_keyset

def test_diff_by_hash_detects_all_three():
    src = {(1,): "a", (2,): "b", (3,): "c"}      # 3 new vs target
    tgt = {(1,): "a", (2,): "X", (4,): "z"}      # 2 changed, 4 only in target
    d = diff_by_hash(src, tgt)
    assert set(d.inserts) == {(3,)}
    assert set(d.updates) == {(2,)}
    assert set(d.deletes) == {(4,)}

def test_diff_by_hash_identical_is_empty():
    src = {(1,): "a"}; tgt = {(1,): "a"}
    d = diff_by_hash(src, tgt)
    assert d.inserts == [] and d.updates == [] and d.deletes == []

def test_diff_by_keyset_has_no_updates():
    d = diff_by_keyset({(1,), (2,)}, {(2,), (3,)})
    assert set(d.inserts) == {(1,)} and set(d.deletes) == {(3,)} and d.updates == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_diff.py -v`
Expected: FAIL with `ModuleNotFoundError: pyarchinit_mini.sync.diff`

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/sync/diff.py
from dataclasses import dataclass

@dataclass
class Diff:
    inserts: list
    updates: list
    deletes: list

def diff_by_hash(source: dict, target: dict) -> Diff:
    src_keys, tgt_keys = set(source), set(target)
    inserts = sorted(src_keys - tgt_keys)
    deletes = sorted(tgt_keys - src_keys)
    updates = sorted(k for k in (src_keys & tgt_keys) if source[k] != target[k])
    return Diff(inserts=inserts, updates=updates, deletes=deletes)

def diff_by_keyset(source_keys: set, target_keys: set) -> Diff:
    return Diff(inserts=sorted(source_keys - target_keys),
                updates=[],
                deletes=sorted(target_keys - source_keys))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_diff.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/diff.py tests/sync/test_diff.py
git commit -m "feat(sync): pure diff (insert/update/delete) logic"
```

---

### Task 5: DB introspection + Postgres test fixtures

**Files:**
- Create: `pyarchinit_mini/sync/introspect.py`
- Create: `tests/sync/conftest.py`
- Test: `tests/sync/test_introspect.py`

**Interfaces:**
- Consumes: a live `psycopg2` connection.
- Produces (all take a `conn` and use the `public` schema):
  - `base_tables(conn) -> set[str]`
  - `column_types(conn, table) -> dict[str, tuple[str, int | None]]` (name → (data_type, character_maximum_length))
  - `primary_key(conn, table) -> list[str]`
  - `geometry_columns(conn, table) -> set[str]`
  - `row_count(conn, table) -> int`
  - `signature(conn, table, pk: list[str]) -> str` (`"count:maxpk"`; `maxpk` empty if no pk)

**Fixture contract (`conftest.py`):** `src_conn` and `tgt_conn` fixtures connect to `TEST_SYNC_SRC_DSN` / `TEST_SYNC_TGT_DSN`; `pytest.skip` if unset. A `make_table(conn, ddl, rows)` helper creates a table and inserts rows; teardown drops created tables.

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/conftest.py
import os, pytest, psycopg2
SRC = os.getenv("TEST_SYNC_SRC_DSN"); TGT = os.getenv("TEST_SYNC_TGT_DSN")
pytestmark = pytest.mark.skipif(not (SRC and TGT), reason="set TEST_SYNC_SRC_DSN/TEST_SYNC_TGT_DSN")

@pytest.fixture
def src_conn():
    c = psycopg2.connect(SRC); c.autocommit = True     # source is read-only
    yield c; c.close()

@pytest.fixture
def tgt_conn():
    c = psycopg2.connect(TGT); c.autocommit = False    # engine controls the transaction
    yield c; c.close()

@pytest.fixture
def make_table():
    created = []  # (conn, name)
    def _make(conn, name, ddl, rows=()):
        cur = conn.cursor()
        cur.execute(f'DROP TABLE IF EXISTS public."{name}" CASCADE')
        cur.execute(ddl)
        created.append((conn, name))
        for r in rows:
            ph = ",".join(["%s"] * len(r))
            cur.execute(f'INSERT INTO public."{name}" VALUES ({ph})', r)
        conn.commit()      # no-op under autocommit; required for the transactional target
        return name
    yield _make
    for conn, name in created:
        conn.cursor().execute(f'DROP TABLE IF EXISTS public."{name}" CASCADE')
        conn.commit()
```

```python
# tests/sync/test_introspect.py
import os, pytest
pytestmark = pytest.mark.skipif(
    not (os.getenv("TEST_SYNC_SRC_DSN") and os.getenv("TEST_SYNC_TGT_DSN")),
    reason="needs test DBs")
from pyarchinit_mini.sync import introspect as I

def test_introspect_table_and_pk(src_conn, make_table):
    make_table(src_conn, "w_intro",
        'CREATE TABLE public."w_intro" (id int primary key, name varchar(10), n int)',
        rows=[(1, "a", 5), (2, "bb", 7)])
    assert "w_intro" in I.base_tables(src_conn)
    assert I.primary_key(src_conn, "w_intro") == ["id"]
    ct = I.column_types(src_conn, "w_intro")
    assert ct["name"] == ("character varying", 10)
    assert I.row_count(src_conn, "w_intro") == 2
    assert I.signature(src_conn, "w_intro", ["id"]) == "2:2"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_introspect.py -v`
Expected: FAIL with `ModuleNotFoundError: pyarchinit_mini.sync.introspect` (or SKIP if test DBs not configured — then configure them per the runbook in Task 9 before continuing).

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/sync/introspect.py
def base_tables(conn) -> set:
    cur = conn.cursor()
    cur.execute("select table_name from information_schema.tables "
                "where table_schema='public' and table_type='BASE TABLE'")
    return {r[0] for r in cur.fetchall()}

def column_types(conn, table) -> dict:
    cur = conn.cursor()
    cur.execute("select column_name, data_type, character_maximum_length "
                "from information_schema.columns where table_schema='public' and table_name=%s",
                (table,))
    return {r[0]: (r[1], r[2]) for r in cur.fetchall()}

def primary_key(conn, table) -> list:
    cur = conn.cursor()
    cur.execute("""select a.attname from pg_index i
                   join pg_class c on c.oid=i.indrelid
                   join pg_namespace n on n.oid=c.relnamespace
                   join pg_attribute a on a.attrelid=c.oid and a.attnum=any(i.indkey)
                   where n.nspname='public' and c.relname=%s and i.indisprimary
                   order by a.attnum""", (table,))
    return [r[0] for r in cur.fetchall()]

def geometry_columns(conn, table) -> set:
    cur = conn.cursor()
    cur.execute("select column_name from information_schema.columns "
                "where table_schema='public' and table_name=%s "
                "and udt_name in ('geometry','geography')", (table,))
    return {r[0] for r in cur.fetchall()}

def row_count(conn, table) -> int:
    cur = conn.cursor()
    cur.execute(f'select count(*) from public."{table}"')
    return cur.fetchone()[0]

def signature(conn, table, pk) -> str:
    cur = conn.cursor()
    cur.execute(f'select count(*) from public."{table}"')
    cnt = cur.fetchone()[0]
    maxpk = ""
    if pk:
        cur.execute(f'select max("{pk[0]}") from public."{table}"')
        maxpk = str(cur.fetchone()[0])
    return f"{cnt}:{maxpk}"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_introspect.py -v`
Expected: PASS (1 passed) — after test DBs are configured.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/introspect.py tests/sync/conftest.py tests/sync/test_introspect.py
git commit -m "feat(sync): DB introspection + postgres test fixtures"
```

---

### Task 6: sync_state tracking

**Files:**
- Create: `pyarchinit_mini/sync/state.py`
- Test: `tests/sync/test_engine.py` (state portion)

**Interfaces:**
- Produces:
  - `ensure_state_table(conn) -> None` (creates `public.sync_state` if missing)
  - `get_signature(conn, table) -> str | None`
  - `record_result(conn, table, signature: str, mode: str, inserted: int, updated: int, deleted: int, error: str | None) -> None`

`sync_state` columns: `table_name text primary key, last_signature text, last_run_at timestamptz default now(), last_mode text, rows_inserted int, rows_updated int, rows_deleted int, error text`.

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_engine.py  (part 1 — state)
import os, pytest
pytestmark = pytest.mark.skipif(
    not (os.getenv("TEST_SYNC_SRC_DSN") and os.getenv("TEST_SYNC_TGT_DSN")),
    reason="needs test DBs")
from pyarchinit_mini.sync import state as S

def test_state_roundtrip(tgt_conn):
    S.ensure_state_table(tgt_conn)
    assert S.get_signature(tgt_conn, "nope") is None
    S.record_result(tgt_conn, "w_state", "5:5", "full", 1, 2, 0, None)
    assert S.get_signature(tgt_conn, "w_state") == "5:5"
    # upsert overwrites
    S.record_result(tgt_conn, "w_state", "6:6", "full", 0, 0, 0, None)
    assert S.get_signature(tgt_conn, "w_state") == "6:6"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_engine.py::test_state_roundtrip -v`
Expected: FAIL with `ModuleNotFoundError: pyarchinit_mini.sync.state`

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/sync/state.py
def ensure_state_table(conn) -> None:
    conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS public.sync_state (
            table_name text PRIMARY KEY,
            last_signature text,
            last_run_at timestamptz DEFAULT now(),
            last_mode text,
            rows_inserted int DEFAULT 0,
            rows_updated int DEFAULT 0,
            rows_deleted int DEFAULT 0,
            error text
        )""")

def get_signature(conn, table) -> str | None:
    cur = conn.cursor()
    cur.execute("select last_signature from public.sync_state where table_name=%s", (table,))
    row = cur.fetchone()
    return row[0] if row else None

def record_result(conn, table, signature, mode, inserted, updated, deleted, error) -> None:
    conn.cursor().execute("""
        INSERT INTO public.sync_state
          (table_name, last_signature, last_run_at, last_mode, rows_inserted, rows_updated, rows_deleted, error)
        VALUES (%s,%s,now(),%s,%s,%s,%s,%s)
        ON CONFLICT (table_name) DO UPDATE SET
          last_signature=EXCLUDED.last_signature, last_run_at=now(), last_mode=EXCLUDED.last_mode,
          rows_inserted=EXCLUDED.rows_inserted, rows_updated=EXCLUDED.rows_updated,
          rows_deleted=EXCLUDED.rows_deleted, error=EXCLUDED.error
        """, (table, signature, mode, inserted, updated, deleted, error))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_engine.py::test_state_roundtrip -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/state.py tests/sync/test_engine.py
git commit -m "feat(sync): sync_state tracking table"
```

---

### Task 7: Engine — sync one table (full / keyset / replace)

**Files:**
- Create: `pyarchinit_mini/sync/engine.py`
- Modify: `tests/sync/test_engine.py` (add engine tests)

**Interfaces:**
- Consumes: `Config`, `introspect.*`, `transform.*`, `diff.*`, `policy.*`, `state.*`.
- Produces:
  - `@dataclass class TableResult(table: str, mode: str, inserted: int, updated: int, deleted: int, skipped: bool, error: str | None)`
  - `sync_table(src_conn, tgt_conn, table: str, cfg: Config, dry_run: bool = True) -> TableResult`

**Behavior (two connections — source rows are read into Python, then written to target with cast-wrapped params):**
- Determine `pk`, `src_types`, `tgt_types`, geometry cols, `row_count(src)`. `mode = select_mode(rc, bool(pk), threshold, override)`.
- `preserve = preserve_set_for_table(...)`; `common = common_data_columns(...)`.
- **Change detection** (`full`): build `{pk_tuple: hash}` for src and tgt via `build_pk_hash_select` run **on each connection's own table** (`_fetch_keyed_hash`); `diff_by_hash`.
- **Apply** (all on `tgt_conn`):
  - INSERT: fetch source rows for `d.inserts` (`_fetch_source_rows`), run `build_insert` per row with `cast_expr` value placeholders + fill (`created_at/updated_at=now()`, `version_number=1`, `entity_uuid/node_uuid=gen_random_uuid()::text` only when present in target and not in `common`).
  - UPDATE: fetch source rows for `d.updates`, run `build_update` per row (sets `common` via `cast_expr`, WHERE on pk). Preserve columns are never in `common`, so never touched.
  - DELETE: `_delete_rows` for `d.deletes` (respects `cfg.delete_enabled`).
- `keyset`: signature gate via `state.get_signature`; if unchanged → `skipped=True`. Else PK-set diff (`diff_by_keyset`) → INSERT new + DELETE gone (no per-row UPDATE).
- `replace`: signature gate; if changed → `TRUNCATE` + INSERT all source rows.
- Geometry columns are cast `(%s)::geometry` (EWKB hex from psycopg2 round-trips through PostGIS).
- All writes happen on `tgt_conn` in one transaction per call; on exception → rollback + return `error`. `dry_run=True` computes counts then `rollback()` (no writes, no `sync_state` update).

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_engine.py  (part 2 — engine)
from pyarchinit_mini.sync.engine import sync_table
from pyarchinit_mini.sync.config import Config

def _cfg(src, tgt):
    return Config(source_dsn=src, target_dsn=tgt, size_threshold_keyset=1000)

def test_full_sync_insert_update_delete(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w_full" (id int primary key, sito varchar(50), order_layer int)'
    make_table(src_conn, "w_full", ddl, rows=[(1, "A", None), (2, "Bclassic", None)])
    make_table(tgt_conn, "w_full", ddl, rows=[(2, "Bold", 99), (3, "ghost", 7)])
    cfg = _cfg("x", "x"); cfg.preserve_columns_global = frozenset({"order_layer"})
    res = sync_table(src_conn, tgt_conn, "w_full", cfg, dry_run=False)
    assert (res.inserted, res.updated, res.deleted) == (1, 1, 1)
    cur = tgt_conn.cursor()
    cur.execute('select id, sito, order_layer from public."w_full" order by id')
    rows = cur.fetchall()
    assert rows == [(1, "A", None), (2, "Bclassic", 99)]   # id3 deleted, id2 updated, order_layer preserved

def test_dry_run_writes_nothing(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w_dry" (id int primary key, sito varchar(50))'
    make_table(src_conn, "w_dry", ddl, rows=[(1, "A")])
    make_table(tgt_conn, "w_dry", ddl, rows=[])
    res = sync_table(src_conn, tgt_conn, "w_dry", _cfg("x", "x"), dry_run=True)
    assert res.inserted == 1
    cur = tgt_conn.cursor()
    cur.execute('select count(*) from public."w_dry"')
    assert cur.fetchone()[0] == 0   # dry-run rolled back, nothing written
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_engine.py -k "full_sync or dry_run" -v`
Expected: FAIL with `ImportError: cannot import name 'sync_table'`

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/sync/engine.py
from dataclasses import dataclass
from . import introspect as I, transform as T, state as S
from .diff import diff_by_hash, diff_by_keyset
from .policy import select_mode, preserve_set_for_table, common_data_columns

@dataclass
class TableResult:
    table: str; mode: str; inserted: int; updated: int; deleted: int
    skipped: bool; error: str | None

_FILL_DEFAULTS = {
    "created_at": "now()", "updated_at": "now()", "version_number": "1",
    "entity_uuid": "gen_random_uuid()::text", "node_uuid": "gen_random_uuid()::text",
}

def _fetch_keyed_hash(conn, table, pk, hash_cols):
    cur = conn.cursor()
    cur.execute(T.build_pk_hash_select(table, pk, hash_cols))
    return {tuple(r[:len(pk)]): r[len(pk)] for r in cur.fetchall()}

def _pk_set(conn, table, pk):
    cur = conn.cursor()
    cur.execute(f'select {", ".join(chr(34)+c+chr(34) for c in pk)} from public."{table}"')
    return {tuple(r) for r in cur.fetchall()}

def _fetch_source_rows(src_conn, table, common, pk, keys=None, all_rows=False):
    """Return rows as tuples ordered (common..., pk...)."""
    cur = src_conn.cursor()
    sel = ", ".join(f'"{c}"' for c in common + pk)
    if all_rows:
        cur.execute(f'select {sel} from public."{table}"')
        return cur.fetchall()
    rows = []
    where = " AND ".join(f'"{c}"=%s' for c in pk)
    for key in (keys or []):
        cur.execute(f'select {sel} from public."{table}" where {where}', list(key))
        r = cur.fetchone()
        if r is not None:
            rows.append(r)
    return rows

def _value_exprs(common, src_types, tgt_types, geom):
    out = []
    for c in common:
        tgt_t = "geometry" if c in geom else tgt_types[c][0]
        out.append(T.cast_expr(src_types[c][0], tgt_t, tgt_types[c][1]))
    return out

def _insert_rows(tgt_conn, table, common, rows, src_types, tgt_types, geom):
    if not rows:
        return 0
    exprs = _value_exprs(common, src_types, tgt_types, geom)
    fill = {c: v for c, v in _FILL_DEFAULTS.items() if c in tgt_types and c not in common}
    sql = T.build_insert(table, common, exprs, fill)
    cur = tgt_conn.cursor(); total = 0
    for r in rows:
        cur.execute(sql, list(r[:len(common)]))   # common-column values only
        total += cur.rowcount
    return total

def _update_rows(tgt_conn, table, common, pk, rows, src_types, tgt_types, geom):
    if not rows:
        return 0
    exprs = _value_exprs(common, src_types, tgt_types, geom)
    sql = T.build_update(table, common, exprs, pk)
    cur = tgt_conn.cursor(); total = 0
    for r in rows:
        cur.execute(sql, list(r[:len(common)]) + list(r[len(common):]))  # common values + pk values
        total += cur.rowcount
    return total

def _delete_rows(tgt_conn, table, pk, keys, cfg):
    if not keys or not cfg.delete_enabled:
        return 0
    cur = tgt_conn.cursor(); total = 0
    where = " AND ".join(f'"{c}"=%s' for c in pk)
    for key in keys:
        cur.execute(f'delete from public."{table}" where {where}', list(key))
        total += cur.rowcount
    return total

def sync_table(src_conn, tgt_conn, table, cfg, dry_run=True) -> TableResult:
    pk = I.primary_key(src_conn, table)
    override = cfg.overrides.get(table) or {}
    rc = I.row_count(src_conn, table)
    mode = select_mode(rc, bool(pk), cfg.size_threshold_keyset, override.get("mode"))
    src_types = I.column_types(src_conn, table)
    tgt_types = I.column_types(tgt_conn, table)
    geom = I.geometry_columns(tgt_conn, table)
    preserve = preserve_set_for_table(cfg.preserve_columns_global, set(src_types), set(tgt_types),
                                      override.get("extra_preserve", []))
    common = common_data_columns(set(src_types), set(tgt_types), preserve)
    ins = upd = dele = 0
    try:
        if mode in ("keyset", "replace"):
            if I.signature(src_conn, table, pk) == S.get_signature(tgt_conn, table):
                return TableResult(table, mode, 0, 0, 0, True, None)
        if mode == "replace":
            tgt_conn.cursor().execute(f'TRUNCATE public."{table}"')
            rows = _fetch_source_rows(src_conn, table, common, pk, all_rows=True)
            ins = _insert_rows(tgt_conn, table, common, rows, src_types, tgt_types, geom)
        elif mode == "keyset":
            d = diff_by_keyset(_pk_set(src_conn, table, pk), _pk_set(tgt_conn, table, pk))
            rows = _fetch_source_rows(src_conn, table, common, pk, keys=d.inserts)
            ins = _insert_rows(tgt_conn, table, common, rows, src_types, tgt_types, geom)
            dele = _delete_rows(tgt_conn, table, pk, d.deletes, cfg)
        else:  # full
            d = diff_by_hash(_fetch_keyed_hash(src_conn, table, pk, common),
                             _fetch_keyed_hash(tgt_conn, table, pk, common))
            ins = _insert_rows(tgt_conn, table, common,
                               _fetch_source_rows(src_conn, table, common, pk, keys=d.inserts),
                               src_types, tgt_types, geom)
            upd = _update_rows(tgt_conn, table, common, pk,
                               _fetch_source_rows(src_conn, table, common, pk, keys=d.updates),
                               src_types, tgt_types, geom)
            dele = _delete_rows(tgt_conn, table, pk, d.deletes, cfg)
        if dry_run:
            tgt_conn.rollback()
        else:
            S.ensure_state_table(tgt_conn)
            S.record_result(tgt_conn, table, I.signature(src_conn, table, pk), mode, ins, upd, dele, None)
            tgt_conn.commit()
        return TableResult(table, mode, ins, upd, dele, False, None)
    except Exception as e:
        tgt_conn.rollback()
        return TableResult(table, mode, 0, 0, 0, False, str(e).splitlines()[0])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_engine.py -v`
Expected: PASS (state + full_sync + dry_run)

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/engine.py tests/sync/test_engine.py
git commit -m "feat(sync): per-table engine (full/keyset/replace) with dry-run"
```

---

### Task 8: Runner + CLI

**Files:**
- Create: `pyarchinit_mini/sync/runner.py`
- Create: `pyarchinit_mini/sync/__main__.py`
- Test: `tests/sync/test_runner.py`

**Interfaces:**
- Consumes: `Config`, `engine.sync_table`, `introspect.base_tables`.
- Produces:
  - `discover_tables(src_conn, tgt_conn, cfg) -> list[str]` (sorted mirrored tables minus `cfg.exclude_tables`)
  - `run(cfg: Config, tables: list[str] | None = None, dry_run: bool = True, logger=None) -> list[TableResult]`
- CLI (`__main__.py`): `--config PATH`, `--apply` (else dry-run), `--tables a,b,c`, `--config`-less default; logs a per-table summary line and a final totals line.

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_runner.py
import os, pytest
pytestmark = pytest.mark.skipif(
    not (os.getenv("TEST_SYNC_SRC_DSN") and os.getenv("TEST_SYNC_TGT_DSN")),
    reason="needs test DBs")
from pyarchinit_mini.sync.runner import discover_tables, run
from pyarchinit_mini.sync.config import Config

def test_discover_excludes_system_and_target_only(src_conn, tgt_conn, make_table):
    make_table(src_conn, "w_shared", 'CREATE TABLE public."w_shared"(id int primary key)')
    make_table(tgt_conn, "w_shared", 'CREATE TABLE public."w_shared"(id int primary key)')
    make_table(tgt_conn, "w_only_v2", 'CREATE TABLE public."w_only_v2"(id int primary key)')
    cfg = Config(source_dsn="x", target_dsn="x", exclude_tables=frozenset({"spatial_ref_sys"}))
    tables = discover_tables(src_conn, tgt_conn, cfg)
    assert "w_shared" in tables and "w_only_v2" not in tables

def test_run_filtered_apply(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w_run"(id int primary key, sito varchar(20))'
    make_table(src_conn, "w_run", ddl, rows=[(1, "A")])
    make_table(tgt_conn, "w_run", ddl, rows=[])
    cfg = Config(source_dsn="x", target_dsn="x")
    results = run(cfg, tables=["w_run"], dry_run=False,
                  _conns=(src_conn, tgt_conn))  # test hook
    assert results[0].inserted == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_runner.py -v`
Expected: FAIL with `ModuleNotFoundError: pyarchinit_mini.sync.runner`

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/sync/runner.py
import logging, psycopg2
from . import introspect as I
from .engine import sync_table

def discover_tables(src_conn, tgt_conn, cfg) -> list:
    mirrored = I.base_tables(src_conn) & I.base_tables(tgt_conn)
    return sorted(mirrored - set(cfg.exclude_tables))

def run(cfg, tables=None, dry_run=True, logger=None, _conns=None) -> list:
    logger = logger or logging.getLogger("sync")
    src, tgt = _conns or (psycopg2.connect(cfg.source_dsn), psycopg2.connect(cfg.target_dsn))
    src.autocommit = True              # source: read-only
    owns = _conns is None
    try:
        names = tables if tables else discover_tables(src, tgt, cfg)
        results = []
        ti = tu = td = 0
        for name in names:
            r = sync_table(src, tgt, name, cfg, dry_run=dry_run)
            results.append(r)
            ti += r.inserted; tu += r.updated; td += r.deleted
            tag = "DRY" if dry_run else "APPLY"
            state = "SKIP" if r.skipped else ("ERR:" + r.error if r.error else "ok")
            logger.info("[%s] %-40s mode=%-7s +%d ~%d -%d %s",
                        tag, name, r.mode, r.inserted, r.updated, r.deleted, state)
        logger.info("[%s] TOTAL tables=%d +%d ~%d -%d",
                    "DRY" if dry_run else "APPLY", len(results), ti, tu, td)
        return results
    finally:
        if owns:
            src.close(); tgt.close()
```

```python
# pyarchinit_mini/sync/__main__.py
import argparse, logging, sys
from .config import load_config
from .runner import run

def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m pyarchinit_mini.sync",
                                description="Sync classic pyarchinit -> pyarchinit_v2")
    p.add_argument("--config", default=None)
    p.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    p.add_argument("--tables", default=None, help="comma-separated subset")
    p.add_argument("--log", default=None, help="log file (default: stderr)")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, filename=args.log,
                        format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config(args.config)
    tables = [t.strip() for t in args.tables.split(",")] if args.tables else None
    results = run(cfg, tables=tables, dry_run=not args.apply)
    errors = [r for r in results if r.error]
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_runner.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/runner.py pyarchinit_mini/sync/__main__.py tests/sync/test_runner.py
git commit -m "feat(sync): runner orchestration + CLI (dry-run default)"
```

---

### Task 9: Runbook, packaging, full test pass

**Files:**
- Create: `docs/superpowers/runbooks/sync-classic-to-v2.md`
- Modify: `pyproject.toml` (ensure `pyarchinit_mini.sync` ships + package-data includes `sync_config.example.json`)
- Test: full suite

**Interfaces:** none (operational + packaging).

- [ ] **Step 1: Write the runbook**

Create `docs/superpowers/runbooks/sync-classic-to-v2.md` with the verbatim content:

```markdown
# Runbook — sync classic pyarchinit -> pyarchinit_v2

## DSNs (env)
- PYARCHINIT_CLASSIC_DSN = postgresql://admin_pyarchinit:<pw>@10.0.1.6:5432/pyarchinit
- DATABASE_URL           = postgresql://admin_pyarchinit:<pw>@10.0.1.6:5432/pyarchinit_v2

## Local test DBs (for the integration tests)
createdb sync_test_src ; createdb sync_test_tgt
export TEST_SYNC_SRC_DSN=postgresql://localhost/sync_test_src
export TEST_SYNC_TGT_DSN=postgresql://localhost/sync_test_tgt
python -m pytest tests/sync -v

## First run (the re-sync)
1. Dry-run (no writes):
   PYARCHINIT_CLASSIC_DSN=... DATABASE_URL=... python -m pyarchinit_mini.sync
2. Backup target:
   pg_dump "$DATABASE_URL" -Fc -f ~/pyarchinit_v2_pre_sync_$(date +%Y%m%d).dump
3. Apply (start narrow, then full):
   ... python -m pyarchinit_mini.sync --apply --tables site_table,us_table,inventario_materiali_table
   ... python -m pyarchinit_mini.sync --apply
4. Verify: re-run dry-run -> expect all tables +0 ~0 -0 (or SKIP).

## Cron (Adarte)
0 1 * * *  PYARCHINIT_CLASSIC_DSN=... DATABASE_URL=... /home/ganesh/pyarchinit_env/bin/python -m pyarchinit_mini.sync --apply --log /home/ganesh/sync_classic_to_v2.log
# weekly full refresh of keyset tables is handled by the engine's signature gate;
# force a deep pass if needed by clearing sync_state for those tables.

## Rollback
pg_restore --clean --no-owner -d "$DATABASE_URL" ~/pyarchinit_v2_pre_sync_<date>.dump
```

- [ ] **Step 2: Verify packaging includes the sync module**

Run: `python -c "import pyarchinit_mini.sync.runner, pyarchinit_mini.sync.__main__; print('import ok')"`
Expected: `import ok`
Check `pyproject.toml` `[tool.setuptools.packages.find]`/`include` already matches `pyarchinit_mini*` (it does: `include = ["pyarchinit_mini*", "tests*"]`). Add `sync_config.example.json` to `[tool.setuptools.package-data]` if package-data is restrictive.

- [ ] **Step 3: Run the full suite**

Run: `python -m pytest tests/sync -v`
Expected: pure tests PASS; integration tests PASS if `TEST_SYNC_*` set, else SKIP.

- [ ] **Step 4: Run the CLI dry-run smoke (pure import path)**

Run: `python -m pyarchinit_mini.sync --help`
Expected: argparse help text, exit 0.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/runbooks/sync-classic-to-v2.md pyproject.toml
git commit -m "docs(sync): runbook + ensure sync module is packaged"
```

---

## Self-Review

- **Spec coverage:** §5.1 discovery → Task 8 `discover_tables` (+ exclude). §5.2 modes full/keyset/replace → Task 7. §5.3 column policy/preserve → Task 2 + engine. §5.4 transform/geometry → Task 3. §5.5 weekly refresh → runbook + signature gate (Task 7/9). §5.6 config → Task 1. §5.7 sync_state → Task 6. §6 safety (dry-run/transaction/error isolation/logging) → Task 7 + 8. §7 cron → Task 9. §8 first run → Task 9 runbook. ✅
- **Placeholder scan:** no TBD/TODO; all steps carry concrete code/commands.
- **Type consistency:** `Config`, `TableResult`, `Diff`, `sync_table`, `cast_expr`, `row_hash_sql`, `build_*`, `select_mode`, `common_data_columns`, `preserve_set_for_table`, `signature`, `get_signature`/`record_result` names are used consistently across tasks.
- **Known refinements for the implementer:** the `keyset` weekly deep pass is currently realized by clearing `sync_state` rows (documented in runbook) rather than a dedicated flag; if a `--full-refresh` flag is desired later it maps to "ignore signature gate" in `sync_table`.
