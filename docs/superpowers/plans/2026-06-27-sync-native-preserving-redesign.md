# Sync redesign — preserve v2-native rows (provenance row-map) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the `pyarchinit_mini/sync/` engine so identity is bridged by a provenance map (`sync_row_map`, v1_pk↔v2_pk) instead of raw PK equality, so v1 changes/adds/deletes propagate only to v1-origin rows while v2-native rows are never deleted or overwritten, with id-collision handling and CHAR-padding idempotency.

**Architecture:** Keep `config`, `policy`, `transform`, `diff`, `introspect`, `state` and extend them; add `rowmap.py` for the map table; rewrite `engine.sync_table` into two modes — `mapped` (tables with a single-column PK: map-based insert/update/delete) and `additive` (no single-column PK: insert-only by content hash). Two direct psycopg2 connections (source=classic read-only, target=v2 transactional).

**Tech Stack:** Python 3.12, psycopg2 + stdlib, pytest. Postgres 17 / PostGIS 3.4.

## Global Constraints

- Python 3.12; runtime deps = `psycopg2` + stdlib only; NO new dependencies.
- One-way only: SELECT on source; writes only on target; never cross-DB SELECT in one statement.
- Identity is the **map** `sync_row_map(table_name, v1_pk, v2_pk)` — NOT raw PK equality. A row is in the map **iff** it is v1-origin; v2-native rows are never mapped and never touched.
- DELETE only a v2 row whose map entry's `v1_pk` is absent from v1. UPDATE only v1-origin (mapped) rows; v1 wins (compare source-coerced hash vs target-actual hash).
- Collision: a new v1 row whose pk is already occupied in v2 by a non-mapped row gets a v2_pk from a high dedicated range, `collision_id_base` default **1_000_000_000**.
- Coerced values via `cast_expr`; `character` (bpchar) source columns are `rtrim`-med (CHAR padding is insignificant).
- `mapped` for tables with a single-column PK; `additive` for tables without one (e.g. `shape_finali_polygon`).
- Large tables (rowcount > `size_threshold_keyset`, default 200000) use the `sync_state` signature-gate (skip when v1 `count+max(pk)` unchanged).
- Exclude tables (system): `spatial_ref_sys, raster_columns, raster_overviews`. Never exclude `public.layer`.
- Generated SQL identifiers are double-quoted. Full type annotations. No AI-attribution / no `Co-Authored-By` in commits.
- Integration tests run against two throwaway Postgres test DBs via env `TEST_SYNC_SRC_DSN` / `TEST_SYNC_TGT_DSN`; they skip if unset.

---

## File Structure

- `pyarchinit_mini/sync/transform.py` — MODIFY: `cast_expr` rtrim for `character` source.
- `pyarchinit_mini/sync/config.py` — MODIFY: add `collision_id_base`.
- `pyarchinit_mini/sync/policy.py` — MODIFY: `select_mode` → `mapped`/`additive`; add `is_gated`.
- `pyarchinit_mini/sync/rowmap.py` — CREATE: `sync_row_map` management.
- `pyarchinit_mini/sync/engine.py` — REWRITE: `sync_table` mapped + additive; helpers.
- `pyarchinit_mini/sync/runner.py` — (unchanged; verify in Task 7).
- `pyarchinit_mini/sync/introspect.py`, `diff.py`, `state.py` — reused unchanged.
- `tests/sync/test_transform.py`, `test_policy.py`, `test_config.py` — MODIFY (add cases).
- `tests/sync/test_rowmap.py` — CREATE.
- `tests/sync/test_engine.py` — REWRITE for the new model.
- `docs/superpowers/runbooks/sync-classic-to-v2.md` — MODIFY (Task 7): document the map/native model.

Reused interfaces (already implemented):
- `introspect.primary_key(conn, table) -> list[str]`, `column_types(conn, table) -> dict[str,(type,maxlen)]`, `geometry_columns(conn, table) -> set[str]`, `row_count`, `signature(conn, table, pk_list) -> str`.
- `diff.diff_by_hash(source: dict, target: dict) -> Diff(inserts, updates, deletes)`.
- `transform.cast_expr(src_type, tgt_type, maxlen, ph="%s")`, `build_pk_hash_select_coerced(table, pk_list, cols, src_types, tgt_types, geom)`, `row_hash_sql(cols)`.
- `state.ensure_state_table`, `get_signature`, `record_result`.
- `policy.preserve_set_for_table`, `common_data_columns`.

---

### Task 1: `cast_expr` rtrim for CHAR(bpchar) source

**Files:**
- Modify: `pyarchinit_mini/sync/transform.py`
- Test: `tests/sync/test_transform.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `cast_expr(src_type, tgt_type, tgt_maxlen, ph="%s")` now strips trailing spaces when `src_type == "character"` (bpchar), so `'A  '` → `'A'`.

- [ ] **Step 1: Write the failing test** (append to `tests/sync/test_transform.py`)

```python
def test_cast_bpchar_source_rtrims_padding():
    # source CHAR(n) blank-padded -> target text/varchar must drop trailing spaces
    e = cast_expr("character", "character varying", 255)
    assert "rtrim(" in e
    e2 = cast_expr("character", "text", None)
    assert "rtrim(" in e2

def test_cast_non_char_source_not_rtrimmed():
    e = cast_expr("character varying", "text", None)
    assert "rtrim(" not in e
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/sync/test_transform.py -k bpchar -v`
Expected: FAIL (no `rtrim(` in output).

- [ ] **Step 3: Implement** — at the TOP of `cast_expr`, before the existing type branches, normalize the placeholder for bpchar sources:

```python
def cast_expr(src_type: str, tgt_type: str, tgt_maxlen: int | None, ph: str = "%s") -> str:
    # CHAR(n) (bpchar) source is blank-padded; trailing spaces are insignificant.
    # Strip them so the coerced value matches the trimmed value stored in v2.
    if src_type == "character":
        ph = f"rtrim({ph})"
    t = tgt_type
    if t in ("geometry", "geography"):
        return f"({ph})::{t}"
    # ... (rest of the existing function unchanged) ...
```

Leave every existing branch exactly as-is; only the two lines above are added.

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/sync/test_transform.py -v`
Expected: PASS (existing 9 + 2 new = 11).

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/transform.py tests/sync/test_transform.py
git commit -m "fix(sync): rtrim CHAR(bpchar) source in cast_expr (idempotency)"
```

---

### Task 2: `collision_id_base` config

**Files:**
- Modify: `pyarchinit_mini/sync/config.py`
- Test: `tests/sync/test_config.py`

**Interfaces:**
- Produces: `Config.collision_id_base: int = 1_000_000_000`; `load_config` reads `collision_id_base` from JSON (default 1_000_000_000).

- [ ] **Step 1: Write the failing test** (append to `tests/sync/test_config.py`)

```python
def test_collision_id_base_default_and_override(tmp_path):
    import json
    from pyarchinit_mini.sync.config import load_config
    env = {"SRC": "postgresql://x@h/c", "TGT": "postgresql://x@h/v2"}
    cfg = load_config(None, env={**env, "PYARCHINIT_CLASSIC_DSN": env["SRC"], "DATABASE_URL": env["TGT"]})
    assert cfg.collision_id_base == 1_000_000_000
    f = tmp_path / "c.json"
    f.write_text(json.dumps({"source_dsn_env": "SRC", "target_dsn_env": "TGT", "collision_id_base": 5000}))
    cfg2 = load_config(str(f), env=env)
    assert cfg2.collision_id_base == 5000
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/sync/test_config.py -k collision -v`
Expected: FAIL (`Config` has no `collision_id_base`).

- [ ] **Step 3: Implement** — in `config.py`, add the field to the dataclass (after `delete_on_empty_source`):

```python
    collision_id_base: int = 1_000_000_000
```

and in `load_config`, add to the `Config(...)` construction:

```python
        collision_id_base=int(raw.get("collision_id_base", 1_000_000_000)),
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/sync/test_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/config.py tests/sync/test_config.py
git commit -m "feat(sync): collision_id_base config (high range for id collisions)"
```

---

### Task 3: `policy.select_mode` → mapped/additive + `is_gated`

**Files:**
- Modify: `pyarchinit_mini/sync/policy.py`
- Test: `tests/sync/test_policy.py`

**Interfaces:**
- Produces:
  - `select_mode(has_single_pk: bool) -> str` → `"mapped"` if `has_single_pk` else `"additive"`.
  - `is_gated(rowcount: int, threshold: int) -> bool` → `rowcount > threshold`.
- Keep `preserve_set_for_table` and `common_data_columns` exactly as they are.

> NOTE: this REPLACES the old `select_mode(rowcount, has_pk, threshold, override)` signature. The engine (Task 5/6) is the only caller and is rewritten to match. Update `test_policy.py`'s old `select_mode` tests accordingly.

- [ ] **Step 1: Rewrite the select_mode tests** in `tests/sync/test_policy.py` — replace the four `test_select_mode_*` tests with:

```python
def test_select_mode_mapped_when_single_pk():
    assert select_mode(True) == "mapped"

def test_select_mode_additive_when_no_single_pk():
    assert select_mode(False) == "additive"

def test_is_gated_threshold():
    from pyarchinit_mini.sync.policy import is_gated
    assert is_gated(500_000, 200_000) is True
    assert is_gated(1915, 200_000) is False
```

(Keep `test_preserve_set_includes_target_only_and_en_cols` and `test_common_data_columns_excludes_preserved` unchanged.)

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/sync/test_policy.py -v`
Expected: FAIL (old `select_mode` signature / `is_gated` missing).

- [ ] **Step 3: Implement** — replace `select_mode` in `policy.py` and add `is_gated`:

```python
def select_mode(has_single_pk: bool) -> str:
    return "mapped" if has_single_pk else "additive"

def is_gated(rowcount: int, threshold: int) -> bool:
    return rowcount > threshold
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/sync/test_policy.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/policy.py tests/sync/test_policy.py
git commit -m "feat(sync): select_mode mapped/additive + is_gated"
```

---

### Task 4: `rowmap.py` — provenance map management

**Files:**
- Create: `pyarchinit_mini/sync/rowmap.py`
- Test: `tests/sync/test_rowmap.py`

**Interfaces:**
- Consumes: a live target `connection`.
- Produces (all on the `public.sync_row_map` table; pk values stored as `text`):
  - `ensure_map_table(conn) -> None`
  - `map_count(conn, table: str) -> int`
  - `load_map(conn, table: str) -> dict[str, str]` — `{v1_pk: v2_pk}`
  - `v2_pk_set(conn, table: str, pk: str) -> set[str]` — current v2 PK values (text) of the real table
  - `bootstrap_table(tgt_conn, src_conn, table: str, pk: str) -> int` — if map empty for table, seed `(v1_pk, v2_pk=same)` for every v1 pk that also exists in v2; returns rows seeded
  - `upsert_map(conn, table: str, v1_pk: str, v2_pk: str) -> None`
  - `delete_map(conn, table: str, v1_pk: str) -> None`

`sync_row_map` schema: `table_name text, v1_pk text, v2_pk text, last_run_at timestamptz default now(), PRIMARY KEY(table_name, v1_pk), UNIQUE(table_name, v2_pk)`.

- [ ] **Step 1: Write the failing test** (`tests/sync/test_rowmap.py`)

```python
import os, pytest
pytestmark = pytest.mark.skipif(
    not (os.getenv("TEST_SYNC_SRC_DSN") and os.getenv("TEST_SYNC_TGT_DSN")),
    reason="needs test DBs")
from pyarchinit_mini.sync import rowmap as M

def test_map_crud_and_bootstrap(src_conn, tgt_conn, make_table):
    M.ensure_map_table(tgt_conn); tgt_conn.commit()
    # source has ids 1,2,3 ; target has 2,3 (v1-origin) and 99 (native)
    ddl = 'CREATE TABLE public."w_map" (id int primary key, sito varchar(20))'
    make_table(src_conn, "w_map", ddl, rows=[(1,"A"),(2,"B"),(3,"C")])
    make_table(tgt_conn, "w_map", ddl, rows=[(2,"B"),(3,"C"),(99,"native")])
    assert M.map_count(tgt_conn, "w_map") == 0
    seeded = M.bootstrap_table(tgt_conn, src_conn, "w_map", "id"); tgt_conn.commit()
    assert seeded == 2                                   # ids 2,3 overlap; 99 native not mapped; 1 not in v2
    assert M.load_map(tgt_conn, "w_map") == {"2": "2", "3": "3"}
    assert M.v2_pk_set(tgt_conn, "w_map", "id") == {"2", "3", "99"}
    M.upsert_map(tgt_conn, "w_map", "1", "1"); tgt_conn.commit()
    assert M.load_map(tgt_conn, "w_map")["1"] == "1"
    M.delete_map(tgt_conn, "w_map", "2"); tgt_conn.commit()
    assert "2" not in M.load_map(tgt_conn, "w_map")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/sync/test_rowmap.py -v`
Expected: FAIL (`ModuleNotFoundError: pyarchinit_mini.sync.rowmap`).

- [ ] **Step 3: Implement** (`pyarchinit_mini/sync/rowmap.py`)

```python
from psycopg2.extensions import connection
from psycopg2.extras import execute_values

def ensure_map_table(conn: connection) -> None:
    conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS public.sync_row_map (
            table_name text NOT NULL,
            v1_pk text NOT NULL,
            v2_pk text NOT NULL,
            last_run_at timestamptz DEFAULT now(),
            PRIMARY KEY (table_name, v1_pk),
            UNIQUE (table_name, v2_pk)
        )""")

def map_count(conn: connection, table: str) -> int:
    cur = conn.cursor()
    cur.execute("select count(*) from public.sync_row_map where table_name=%s", (table,))
    return cur.fetchone()[0]

def load_map(conn: connection, table: str) -> dict:
    cur = conn.cursor()
    cur.execute("select v1_pk, v2_pk from public.sync_row_map where table_name=%s", (table,))
    return {r[0]: r[1] for r in cur.fetchall()}

def v2_pk_set(conn: connection, table: str, pk: str) -> set:
    cur = conn.cursor()
    cur.execute(f'select "{pk}"::text from public."{table}"')
    return {r[0] for r in cur.fetchall()}

def bootstrap_table(tgt_conn: connection, src_conn: connection, table: str, pk: str) -> int:
    scur = src_conn.cursor()
    scur.execute(f'select "{pk}"::text from public."{table}"')
    v1 = {r[0] for r in scur.fetchall()}
    v2 = v2_pk_set(tgt_conn, table, pk)
    overlap = sorted(v1 & v2)
    if not overlap:
        return 0
    tcur = tgt_conn.cursor()
    execute_values(tcur,
        "INSERT INTO public.sync_row_map (table_name, v1_pk, v2_pk) VALUES %s "
        "ON CONFLICT (table_name, v1_pk) DO NOTHING",
        [(table, k, k) for k in overlap])
    return len(overlap)

def upsert_map(conn: connection, table: str, v1_pk: str, v2_pk: str) -> None:
    conn.cursor().execute(
        "INSERT INTO public.sync_row_map (table_name, v1_pk, v2_pk) VALUES (%s,%s,%s) "
        "ON CONFLICT (table_name, v1_pk) DO UPDATE SET v2_pk=EXCLUDED.v2_pk, last_run_at=now()",
        (table, v1_pk, v2_pk))

def delete_map(conn: connection, table: str, v1_pk: str) -> None:
    conn.cursor().execute(
        "delete from public.sync_row_map where table_name=%s and v1_pk=%s", (table, v1_pk))
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/sync/test_rowmap.py -v`
Expected: PASS (with test DBs).

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/rowmap.py tests/sync/test_rowmap.py
git commit -m "feat(sync): sync_row_map provenance table (load/bootstrap/upsert/delete)"
```

---

### Task 5: `engine.py` — `mapped` mode rewrite

**Files:**
- Modify (rewrite core): `pyarchinit_mini/sync/engine.py`
- Test (rewrite): `tests/sync/test_engine.py`

**Interfaces:**
- Consumes: `introspect`, `transform`, `diff.diff_by_hash`, `state`, `rowmap`, `policy.{select_mode,is_gated,preserve_set_for_table,common_data_columns}`, `config.Config`.
- Produces: `TableResult(table, mode, inserted, updated, deleted, skipped, error)`; `sync_table(src_conn, tgt_conn, table, cfg, dry_run=True) -> TableResult`. (This task implements the `mapped` branch + helpers; the `additive` branch + gate come in Task 6 — for now non-`mapped` tables raise NotImplementedError, exercised in Task 6.)

**Identity & hashing:** map = `{v1_pk: v2_pk}`. Source hash `{v1_pk: coerced_hash}` via `build_pk_hash_select_coerced`. Target hash `{v2_pk: plain_hash}` via `row_hash_sql` over `common`. A mapped row needs update when `source_hash[v1_pk] != target_hash[map[v1_pk]]` (v1 wins, reverting v2 edits). Insert/delete from `diff_by_hash(source, {v1_pk: target_hash_via_map})`.

- [ ] **Step 1: Write the failing tests** — REPLACE the contents of `tests/sync/test_engine.py` with:

```python
import os, pytest
pytestmark = pytest.mark.skipif(
    not (os.getenv("TEST_SYNC_SRC_DSN") and os.getenv("TEST_SYNC_TGT_DSN")),
    reason="needs test DBs")
from pyarchinit_mini.sync.engine import sync_table
from pyarchinit_mini.sync.config import Config
from pyarchinit_mini.sync import rowmap as M

def _cfg():
    return Config(source_dsn="x", target_dsn="x", size_threshold_keyset=10_000)

def test_native_row_is_never_deleted_or_touched(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w1" (id int primary key, sito varchar(20))'
    make_table(src_conn, "w1", ddl, rows=[(1,"A"),(2,"B")])
    make_table(tgt_conn, "w1", ddl, rows=[(1,"A"),(2,"B"),(99,"NATIVE")])  # 99 is v2-native
    r = sync_table(src_conn, tgt_conn, "w1", _cfg(), dry_run=False)
    assert r.mode == "mapped"
    cur = tgt_conn.cursor(); cur.execute('select id, sito from public."w1" order by id')
    assert cur.fetchall() == [(1,"A"),(2,"B"),(99,"NATIVE")]   # native preserved

def test_v1_insert_update_delete_only_affect_v1_origin(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w2" (id int primary key, sito varchar(20))'
    make_table(src_conn, "w2", ddl, rows=[(1,"A"),(2,"B")])
    make_table(tgt_conn, "w2", ddl, rows=[(1,"A"),(2,"B"),(99,"NATIVE")])
    sync_table(src_conn, tgt_conn, "w2", _cfg(), dry_run=False)   # 1st run: bootstrap maps 1,2 (99 native)
    sc = src_conn.cursor()                                        # now v1 changes:
    sc.execute('update public."w2" set sito=%s where id=1', ("A2",))   # update 1
    sc.execute('delete from public."w2" where id=2')                    # delete 2 (was mapped)
    sc.execute('insert into public."w2" values (3, %s)', ("C",))        # new 3
    src_conn.commit()
    r = sync_table(src_conn, tgt_conn, "w2", _cfg(), dry_run=False)
    assert (r.inserted, r.updated, r.deleted) == (1, 1, 1)
    cur = tgt_conn.cursor(); cur.execute('select id, sito from public."w2" order by id')
    assert cur.fetchall() == [(1,"A2"),(3,"C"),(99,"NATIVE")]    # 2 deleted (v1-origin gone), 99 kept

def test_collision_assigns_high_id(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w3" (id int primary key, sito varchar(20))'
    make_table(src_conn, "w3", ddl, rows=[(1,"X")])              # v1 initially: id 1
    make_table(tgt_conn, "w3", ddl, rows=[(1,"X"),(99,"NATIVE")])   # native id=99 (not in v1)
    cfg = _cfg(); cfg.collision_id_base = 1000
    sync_table(src_conn, tgt_conn, "w3", cfg, dry_run=False)     # bootstrap maps 1; 99 stays native
    src_conn.cursor().execute('insert into public."w3" values (99, %s)', ("FROM_V1",))  # v1 now mints id 99
    src_conn.commit()
    r = sync_table(src_conn, tgt_conn, "w3", cfg, dry_run=False)
    assert r.inserted == 1
    cur = tgt_conn.cursor(); cur.execute('select id, sito from public."w3" order by id')
    rows = cur.fetchall()
    assert (99, "NATIVE") in rows                                # native id=99 untouched
    assert any(i >= 1000 and s == "FROM_V1" for i, s in rows)    # v1 row got a high id
    assert M.load_map(tgt_conn, "w3")["99"] != "99"             # mapped to a different v2 id

def test_idempotent_second_run(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w4" (id int primary key, anno varchar(10))'
    make_table(src_conn, "w4", ddl, rows=[(1,"2020"),(2,"n/a")])
    make_table(tgt_conn, "w4", 'CREATE TABLE public."w4" (id int primary key, anno integer)')
    r1 = sync_table(src_conn, tgt_conn, "w4", _cfg(), dry_run=False)
    assert r1.inserted == 2
    r2 = sync_table(src_conn, tgt_conn, "w4", _cfg(), dry_run=False)
    assert (r2.inserted, r2.updated, r2.deleted) == (0, 0, 0)   # idempotent (coerced compare)

def test_dry_run_writes_nothing(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w5" (id int primary key, sito varchar(20))'
    make_table(src_conn, "w5", ddl, rows=[(1,"A")])
    make_table(tgt_conn, "w5", ddl, rows=[])
    r = sync_table(src_conn, tgt_conn, "w5", _cfg(), dry_run=True)
    assert r.inserted == 1
    cur = tgt_conn.cursor(); cur.execute('select count(*) from public."w5"')
    assert cur.fetchone()[0] == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/sync/test_engine.py -v`
Expected: FAIL (engine not yet rewritten / behavior differs).

- [ ] **Step 3: Implement** — REPLACE `pyarchinit_mini/sync/engine.py` with:

```python
from dataclasses import dataclass
from psycopg2.extensions import connection
from . import introspect as I, transform as T, state as S, rowmap as M
from .diff import diff_by_hash
from .policy import select_mode, is_gated, preserve_set_for_table, common_data_columns

@dataclass
class TableResult:
    table: str; mode: str; inserted: int; updated: int; deleted: int
    skipped: bool; error: str | None

_FILL_DEFAULTS = {
    "created_at": "now()", "updated_at": "now()", "version_number": "1",
    "entity_uuid": "gen_random_uuid()::text", "node_uuid": "gen_random_uuid()::text",
}

def _source_hash(src_conn, table, pk, common, src_types, tgt_types, geom):
    cur = src_conn.cursor()
    cur.execute(T.build_pk_hash_select_coerced(table, [pk], common, src_types, tgt_types, geom))
    return {str(r[0]): r[1] for r in cur.fetchall()}

def _target_hash(tgt_conn, table, pk, common):
    cur = tgt_conn.cursor()
    cur.execute(f'select "{pk}"::text, {T.row_hash_sql(common)} from public."{table}"')
    return {r[0]: r[1] for r in cur.fetchall()}

def _fetch_source_row(src_conn, table, common, pk, v1_pk):
    cur = src_conn.cursor()
    cols = ", ".join(f'"{c}"' for c in common)
    cur.execute(f'select {cols} from public."{table}" where "{pk}"::text=%s', (v1_pk,))
    return cur.fetchone()

def _value_exprs(common, src_types, tgt_types, geom):
    out = []
    for c in common:
        tgt_t = "geometry" if c in geom else tgt_types[c][0]
        out.append(T.cast_expr(src_types[c][0], tgt_t, tgt_types[c][1], ph=f"%({c})s"))
    return out

def _insert_one(tgt_conn, table, common, pk, row, v2_pk, src_types, tgt_types, geom):
    # row is aligned to `common`; force the pk column to the chosen v2_pk
    exprs = _value_exprs(common, src_types, tgt_types, geom)
    fill = {c: v for c, v in _FILL_DEFAULTS.items() if c in tgt_types and c not in common}
    cols = common + list(fill.keys())
    col_sql = ", ".join(f'"{c}"' for c in cols)
    val_sql = ", ".join(exprs + list(fill.values()))
    params = {c: row[i] for i, c in enumerate(common)}
    params[pk] = v2_pk                       # override pk value with the chosen v2_pk
    tgt_conn.cursor().execute(
        f'INSERT INTO public."{table}" ({col_sql}) VALUES ({val_sql})', params)

def _update_one(tgt_conn, table, common, pk, row, v2_pk, src_types, tgt_types, geom):
    set_cols = [c for c in common if c != pk]            # never update the pk
    exprs = _value_exprs(set_cols, src_types, tgt_types, geom)
    assigns = ", ".join(f'"{c}" = {e}' for c, e in zip(set_cols, exprs))
    params = {c: row[common.index(c)] for c in set_cols}
    params["__v2pk"] = v2_pk
    tgt_conn.cursor().execute(
        f'UPDATE public."{table}" SET {assigns} WHERE "{pk}"::text = %(__v2pk)s', params)

def _delete_one(tgt_conn, table, pk, v2_pk):
    tgt_conn.cursor().execute(f'delete from public."{table}" where "{pk}"::text=%s', (v2_pk,))

def _alloc_v2_pk(v1_pk, v2pks, state):
    if v1_pk not in v2pks:
        return v1_pk
    nxt = state["next_high"]
    while str(nxt) in v2pks:
        nxt += 1
    state["next_high"] = nxt + 1
    return str(nxt)

def sync_table(src_conn, tgt_conn, table, cfg, dry_run=True) -> TableResult:
    mode = "unknown"; ins = upd = dele = 0
    try:
        M.ensure_map_table(tgt_conn); S.ensure_state_table(tgt_conn)
        pk_cols = I.primary_key(src_conn, table)
        single_pk = pk_cols[0] if len(pk_cols) == 1 else None
        mode = select_mode(single_pk is not None)
        rc = I.row_count(src_conn, table)
        src_types = I.column_types(src_conn, table)
        tgt_types = I.column_types(tgt_conn, table)
        geom = I.geometry_columns(tgt_conn, table)
        preserve = preserve_set_for_table(cfg.preserve_columns_global,
                                          set(src_types), set(tgt_types), [])
        common = common_data_columns(set(src_types), set(tgt_types), preserve)
        if mode != "mapped":
            raise NotImplementedError("additive mode implemented in Task 6")
        if is_gated(rc, cfg.size_threshold_keyset):
            if I.signature(src_conn, table, pk_cols) == S.get_signature(tgt_conn, table):
                tgt_conn.rollback()
                return TableResult(table, mode, 0, 0, 0, True, None)
        if M.map_count(tgt_conn, table) == 0:
            M.bootstrap_table(tgt_conn, src_conn, table, single_pk)
        mp = M.load_map(tgt_conn, table)                       # {v1_pk: v2_pk}
        src = _source_hash(src_conn, table, single_pk, common, src_types, tgt_types, geom)
        tgt_h = _target_hash(tgt_conn, table, single_pk, common)   # {v2_pk: hash}
        target = {v1: tgt_h.get(v2) for v1, v2 in mp.items()}      # {v1_pk: hash-of-its-v2-row}
        d = diff_by_hash(src, target)
        v2pks = M.v2_pk_set(tgt_conn, table, single_pk)
        import re
        nums = [int(x) for x in v2pks if re.fullmatch(r"-?\d+", x)]
        state = {"next_high": max([cfg.collision_id_base] + [n + 1 for n in nums])}
        for v1k in d.deletes:
            _delete_one(tgt_conn, table, single_pk, mp[v1k]); M.delete_map(tgt_conn, table, v1k); dele += 1
        for v1k in d.inserts:
            row = _fetch_source_row(src_conn, table, common, single_pk, v1k)
            if row is None:
                continue
            v2k = _alloc_v2_pk(v1k, v2pks, state)
            _insert_one(tgt_conn, table, common, single_pk, row, v2k, src_types, tgt_types, geom)
            M.upsert_map(tgt_conn, table, v1k, v2k); v2pks.add(v2k); ins += 1
        for v1k in d.updates:
            v2k = mp[v1k]
            row = _fetch_source_row(src_conn, table, common, single_pk, v1k)
            if row is None:
                continue
            if v2k in v2pks:
                _update_one(tgt_conn, table, common, single_pk, row, v2k, src_types, tgt_types, geom)
            else:                                   # mapped row deleted in v2 -> re-insert
                v2k = _alloc_v2_pk(v1k, v2pks, state)
                _insert_one(tgt_conn, table, common, single_pk, row, v2k, src_types, tgt_types, geom)
                M.upsert_map(tgt_conn, table, v1k, v2k); v2pks.add(v2k)
            upd += 1
        if dry_run:
            tgt_conn.rollback()
        else:
            S.record_result(tgt_conn, table, I.signature(src_conn, table, pk_cols),
                            mode, ins, upd, dele, None)
            tgt_conn.commit()
        return TableResult(table, mode, ins, upd, dele, False, None)
    except Exception as e:
        tgt_conn.rollback()
        msg = str(e).splitlines()[0]
        try:
            S.ensure_state_table(tgt_conn)
            S.record_result(tgt_conn, table, "", mode, 0, 0, 0, msg); tgt_conn.commit()
        except Exception:
            tgt_conn.rollback()
        return TableResult(table, mode, 0, 0, 0, False, msg)
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/sync/test_engine.py -v`
Expected: PASS (native preserved, insert/update/delete only v1-origin, collision high id, idempotent, dry-run).

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/engine.py tests/sync/test_engine.py
git commit -m "feat(sync): map-based mapped-mode engine (preserve v2-native, collision ids)"
```

---

### Task 6: `engine.py` — `additive` mode + verify gate

**Files:**
- Modify: `pyarchinit_mini/sync/engine.py`
- Test: `tests/sync/test_engine.py`

**Interfaces:**
- Consumes: same as Task 5.
- Produces: `sync_table` handles `additive` (no single-col PK): insert v1 rows whose full-row content hash is absent from v2; never update/delete. Native rows preserved.

- [ ] **Step 1: Write the failing tests** (append to `tests/sync/test_engine.py`)

```python
def test_additive_mode_no_pk_inserts_missing_keeps_native(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."wA" (sito varchar(20), n int)'   # no PK -> additive
    make_table(src_conn, "wA", ddl, rows=[("A",1),("B",2)])
    make_table(tgt_conn, "wA", ddl, rows=[("A",1),("NATIVE",9)])  # has one v1 row + one native
    r = sync_table(src_conn, tgt_conn, "wA", _cfg(), dry_run=False)
    assert r.mode == "additive"
    assert r.deleted == 0
    cur = tgt_conn.cursor(); cur.execute('select sito, n from public."wA" order by sito')
    assert cur.fetchall() == [("A",1),("B",2),("NATIVE",9)]   # B added, native + A kept, nothing deleted

def test_large_table_gate_skips_when_unchanged(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."wG" (id int primary key, sito varchar(20))'
    make_table(src_conn, "wG", ddl, rows=[(1,"A"),(2,"B")])
    make_table(tgt_conn, "wG", ddl, rows=[(1,"A"),(2,"B")])
    cfg = _cfg(); cfg.size_threshold_keyset = 1      # rc=2 > 1 -> gated
    r1 = sync_table(src_conn, tgt_conn, "wG", cfg, dry_run=False)
    assert r1.skipped is False                       # first run: bootstraps + processes
    r2 = sync_table(src_conn, tgt_conn, "wG", cfg, dry_run=False)
    assert r2.skipped is True                         # unchanged v1 signature -> skipped
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/sync/test_engine.py -k "additive or gate" -v`
Expected: FAIL (additive raises NotImplementedError).

- [ ] **Step 3: Implement** — in `engine.py`, replace the `if mode != "mapped": raise NotImplementedError(...)` line with an additive branch. Insert this block right after `common = common_data_columns(...)` and before the gate:

```python
        if mode == "additive":
            hexpr = T.row_hash_sql(common)
            scur = src_conn.cursor()
            scur.execute(f'select {hexpr}, {", ".join(chr(34)+c+chr(34) for c in common)} '
                         f'from public."{table}"')
            srows = scur.fetchall()
            tcur = tgt_conn.cursor()
            tcur.execute(f'select {hexpr} from public."{table}"')
            thashes = {r[0] for r in tcur.fetchall()}
            seen = set(thashes)
            for r in srows:
                h = r[0]
                if h in seen:
                    continue
                seen.add(h)
                row = r[1:]
                exprs = _value_exprs(common, src_types, tgt_types, geom)
                col_sql = ", ".join(f'"{c}"' for c in common)
                params = {c: row[i] for i, c in enumerate(common)}
                tgt_conn.cursor().execute(
                    f'INSERT INTO public."{table}" ({col_sql}) VALUES ({", ".join(exprs)})', params)
                ins += 1
            if dry_run:
                tgt_conn.rollback()
            else:
                S.record_result(tgt_conn, table, I.signature(src_conn, table, pk_cols),
                                mode, ins, 0, 0, None)
                tgt_conn.commit()
            return TableResult(table, mode, ins, 0, 0, False, None)
```

(Remove the old `raise NotImplementedError` line.)

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/sync/test_engine.py -v`
Expected: PASS (all Task 5 tests + additive + gate).

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/sync/engine.py tests/sync/test_engine.py
git commit -m "feat(sync): additive mode for no-PK tables + verify large-table gate"
```

---

### Task 7: Runner check, runbook, full suite

**Files:**
- Verify: `pyarchinit_mini/sync/runner.py` (should need no change; the mode string is just logged).
- Modify: `docs/superpowers/runbooks/sync-classic-to-v2.md`
- Test: full suite.

**Interfaces:** none (wiring + docs).

- [ ] **Step 1: Confirm runner is compatible**

Run: `python3 -c "import pyarchinit_mini.sync.runner, pyarchinit_mini.sync.engine; print('import ok')"`
Expected: `import ok`. (The runner calls `sync_table(...)` and logs `r.mode`; `discover_tables` is unchanged. No edit expected. If an import error appears, fix only the broken reference.)

- [ ] **Step 2: Update the runbook** — append this section to `docs/superpowers/runbooks/sync-classic-to-v2.md`:

```markdown
## Native-preserving model (since 2026-06-27)
- Identity is the map `public.sync_row_map (table_name, v1_pk, v2_pk)`; a row is synced from v1 iff it is mapped.
- v2-native rows (inserted directly in v2, not mapped) are NEVER updated or deleted.
- DELETE happens only for mapped rows whose v1_pk disappeared from v1.
- Id collisions (a new v1 row whose id is taken by a native row) get a v2 id from `collision_id_base` (default 1e9); the map records v1_pk->v2_pk. Relationships are by name (sito/us), so the reassigned surrogate id is harmless.
- No-PK tables (e.g. shape_finali_polygon) are additive-only (insert new v1 content; no update/delete).
- First run bootstraps the map from the current overlap (v1 ids also present in v2); it will not re-delete natives.
- To force a deep refresh of a large gated table, delete its row from public.sync_state.
```

- [ ] **Step 3: Run the full suite**

Run (with test DBs exported):
```
export TEST_SYNC_SRC_DSN='postgresql://...@.../sync_test_src'
export TEST_SYNC_TGT_DSN='postgresql://...@.../sync_test_tgt'
python3 -m pytest tests/sync -v
```
Expected: all pass; integration tests run (not skipped).

- [ ] **Step 4: CLI smoke**

Run: `python3 -m pyarchinit_mini.sync --help`
Expected: argparse help, exit 0.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/runbooks/sync-classic-to-v2.md
git commit -m "docs(sync): document native-preserving map model in runbook"
```

---

## Self-Review

- **Spec coverage:** §2 map → Task 4 + engine; §3.1 bootstrap → Task 4 `bootstrap_table` (auto-called in engine); §3.2 mapped insert/update/delete → Task 5; §3.3 additive → Task 6; §3.4 gate → Task 6; §4 collision high id → Task 5 `_alloc_v2_pk` + Task 2 config; §5 bpchar rtrim + coerced hash → Task 1 (+ reused `build_pk_hash_select_coerced`); §6 v1-wins (source vs target-actual hash) → Task 5; §7 module changes → Tasks 1-6; §8 dry-run/error/backup → Task 5 (dry-run rollback, error record); §9 edge cases (re-insert deleted mapped row, no-PK additive) → Task 5/6. ✅
- **Placeholder scan:** no TBD/TODO; every step has concrete code/commands.
- **Type consistency:** `select_mode(bool)`, `is_gated`, `rowmap.*`, `TableResult`, `sync_table`, `_alloc_v2_pk`, `cast_expr(...,ph=)` used consistently across tasks. The old `select_mode(rowcount,has_pk,threshold,override)` is fully replaced and its callers (engine) rewritten in the same plan.
- **Note for implementer:** Task 5 leaves `additive` raising NotImplementedError so Task 5's tests (all `mapped`) pass in isolation; Task 6 removes it. Do not run additive tests before Task 6.
