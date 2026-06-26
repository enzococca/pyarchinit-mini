import os, pytest
pytestmark = pytest.mark.skipif(
    not (os.getenv("TEST_SYNC_SRC_DSN") and os.getenv("TEST_SYNC_TGT_DSN")),
    reason="needs test DBs")
from pyarchinit_mini.sync import state as S
from pyarchinit_mini.sync.engine import sync_table
from pyarchinit_mini.sync.config import Config


def test_state_roundtrip(tgt_conn):
    S.ensure_state_table(tgt_conn)
    assert S.get_signature(tgt_conn, "nope") is None
    S.record_result(tgt_conn, "w_state", "5:5", "full", 1, 2, 0, None)
    assert S.get_signature(tgt_conn, "w_state") == "5:5"
    # upsert overwrites
    S.record_result(tgt_conn, "w_state", "6:6", "full", 0, 0, 0, None)
    assert S.get_signature(tgt_conn, "w_state") == "6:6"


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

def test_full_sync_casts_divergent_types(src_conn, tgt_conn, make_table):
    # source `anno` is varchar, target `anno` is integer -> cast_expr emits the
    # placeholder twice; named params must bind both occurrences to one value.
    make_table(src_conn, "w_cast",
        'CREATE TABLE public."w_cast" (id int primary key, anno varchar(10))',
        rows=[(1, "2020"), (2, "n/a")])
    make_table(tgt_conn, "w_cast",
        'CREATE TABLE public."w_cast" (id int primary key, anno integer)')
    res = sync_table(src_conn, tgt_conn, "w_cast", _cfg("x", "x"), dry_run=False)
    assert res.inserted == 2
    cur = tgt_conn.cursor()
    cur.execute('select id, anno from public."w_cast" order by id')
    assert cur.fetchall() == [(1, 2020), (2, None)]   # "2020"->2020, "n/a"->NULL (guarded)

def test_keyset_mode_insert_and_delete_first_run(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w_keyset" (id int primary key, sito varchar(20))'
    make_table(src_conn, "w_keyset", ddl, rows=[(1, "A"), (2, "B")])
    make_table(tgt_conn, "w_keyset", ddl, rows=[(2, "B"), (3, "old")])
    cfg = _cfg("x", "x"); cfg.size_threshold_keyset = 1
    tgt_conn.cursor().execute("DROP TABLE IF EXISTS public.sync_state"); tgt_conn.commit()
    res = sync_table(src_conn, tgt_conn, "w_keyset", cfg, dry_run=False)
    assert res.mode == "keyset"
    assert (res.inserted, res.deleted) == (1, 1)
    cur = tgt_conn.cursor(); cur.execute('select id from public."w_keyset" order by id')
    assert [r[0] for r in cur.fetchall()] == [1, 2]

def test_replace_mode_truncates_and_reloads_first_run(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w_replace" (sito varchar(20), n int)'
    make_table(src_conn, "w_replace", ddl, rows=[("A", 1), ("B", 2)])
    make_table(tgt_conn, "w_replace", ddl, rows=[("OLD", 9)])
    tgt_conn.cursor().execute("DROP TABLE IF EXISTS public.sync_state"); tgt_conn.commit()
    res = sync_table(src_conn, tgt_conn, "w_replace", _cfg("x", "x"), dry_run=False)
    assert res.mode == "replace"
    cur = tgt_conn.cursor(); cur.execute('select sito, n from public."w_replace" order by sito')
    assert cur.fetchall() == [("A", 1), ("B", 2)]

def test_missing_source_table_is_isolated(src_conn, tgt_conn, make_table):
    make_table(tgt_conn, "w_only_tgt", 'CREATE TABLE public."w_only_tgt" (id int primary key)')
    res = sync_table(src_conn, tgt_conn, "w_only_tgt", _cfg("x", "x"), dry_run=False)
    assert res.error is not None and res.inserted == 0
    cur = tgt_conn.cursor(); cur.execute("select 1")
    assert cur.fetchone()[0] == 1

def test_full_sync_idempotent_on_divergent_types(src_conn, tgt_conn, make_table):
    make_table(src_conn, "w_idem",
        'CREATE TABLE public."w_idem" (id int primary key, anno varchar(10))', rows=[(1, "2020"), (2, "n/a")])
    make_table(tgt_conn, "w_idem",
        'CREATE TABLE public."w_idem" (id int primary key, anno integer)')
    r1 = sync_table(src_conn, tgt_conn, "w_idem", _cfg("x", "x"), dry_run=False)
    assert r1.inserted == 2
    r2 = sync_table(src_conn, tgt_conn, "w_idem", _cfg("x", "x"), dry_run=False)
    assert (r2.inserted, r2.updated, r2.deleted) == (0, 0, 0)   # no perpetual update

def test_error_is_recorded_in_sync_state(src_conn, tgt_conn, make_table):
    make_table(tgt_conn, "w_err", 'CREATE TABLE public."w_err" (id int primary key)')  # absent on source
    res = sync_table(src_conn, tgt_conn, "w_err", _cfg("x", "x"), dry_run=False)
    assert res.error is not None
    cur = tgt_conn.cursor()
    cur.execute("select error from public.sync_state where table_name='w_err'")
    row = cur.fetchone()
    assert row is not None and row[0]      # error persisted

def test_empty_source_does_not_wipe_target_by_default(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w_empty" (id int primary key, sito varchar(10))'
    make_table(src_conn, "w_empty", ddl, rows=[])
    make_table(tgt_conn, "w_empty", ddl, rows=[(1, "A"), (2, "B")])
    res = sync_table(src_conn, tgt_conn, "w_empty", _cfg("x", "x"), dry_run=False)
    assert res.deleted == 0
    cur = tgt_conn.cursor(); cur.execute('select count(*) from public."w_empty"')
    assert cur.fetchone()[0] == 2
