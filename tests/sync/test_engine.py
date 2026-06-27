import os, pytest
pytestmark = pytest.mark.skipif(
    not (os.getenv("TEST_SYNC_SRC_DSN") and os.getenv("TEST_SYNC_TGT_DSN")),
    reason="needs test DBs")
from pyarchinit_mini.sync.engine import sync_table
from pyarchinit_mini.sync.config import Config
from pyarchinit_mini.sync import rowmap as M

@pytest.fixture(autouse=True)
def isolate(tgt_conn):
    """Drop sync tracking tables before each test to guarantee clean isolation."""
    cur = tgt_conn.cursor()
    for tbl in ("sync_row_map", "sync_state"):
        cur.execute(f"DROP TABLE IF EXISTS public.{tbl}")
    tgt_conn.commit()
    yield

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
    r2 = sync_table(src_conn, tgt_conn, "w3", cfg, dry_run=False)
    assert (r2.inserted, r2.updated, r2.deleted) == (0, 0, 0)   # collision row idempotent

def test_idempotent_second_run(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w4" (id int primary key, anno varchar(10))'
    make_table(src_conn, "w4", ddl, rows=[(1,"2020"),(2,"n/a")])
    make_table(tgt_conn, "w4", 'CREATE TABLE public."w4" (id int primary key, anno integer)')
    r1 = sync_table(src_conn, tgt_conn, "w4", _cfg(), dry_run=False)
    assert r1.inserted == 2
    r2 = sync_table(src_conn, tgt_conn, "w4", _cfg(), dry_run=False)
    assert (r2.inserted, r2.updated, r2.deleted) == (0, 0, 0)   # idempotent (coerced compare)

def test_error_recorded_and_isolated(src_conn, tgt_conn, make_table):
    # table exists only on target -> source introspection fails; error caught + recorded
    make_table(tgt_conn, "wE", 'CREATE TABLE public."wE" (id int primary key)')
    r = sync_table(src_conn, tgt_conn, "wE", _cfg(), dry_run=False)
    assert r.error is not None and r.inserted == 0
    cur = tgt_conn.cursor()
    cur.execute("select error from public.sync_state where table_name='wE'")
    row = cur.fetchone()
    assert row is not None and row[0]            # error persisted to sync_state
    cur.execute("select 1")
    assert cur.fetchone()[0] == 1                 # connection still usable

def test_dry_run_writes_nothing(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."w5" (id int primary key, sito varchar(20))'
    make_table(src_conn, "w5", ddl, rows=[(1,"A")])
    make_table(tgt_conn, "w5", ddl, rows=[])
    r = sync_table(src_conn, tgt_conn, "w5", _cfg(), dry_run=True)
    assert r.inserted == 1
    cur = tgt_conn.cursor(); cur.execute('select count(*) from public."w5"')
    assert cur.fetchone()[0] == 0

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

def test_empty_source_does_not_wipe_v1_origin(src_conn, tgt_conn, make_table):
    ddl = 'CREATE TABLE public."wEmpty" (id int primary key, sito varchar(20))'
    make_table(src_conn, "wEmpty", ddl, rows=[(1,"A"),(2,"B")])
    make_table(tgt_conn, "wEmpty", ddl, rows=[(1,"A"),(2,"B")])
    sync_table(src_conn, tgt_conn, "wEmpty", _cfg(), dry_run=False)   # bootstrap maps 1,2
    src_conn.cursor().execute('delete from public."wEmpty"'); src_conn.commit()  # source now empty
    r = sync_table(src_conn, tgt_conn, "wEmpty", _cfg(), dry_run=False)
    assert r.deleted == 0                                   # empty source must not wipe v1-origin
    cur = tgt_conn.cursor(); cur.execute('select count(*) from public."wEmpty"')
    assert cur.fetchone()[0] == 2

def test_additive_idempotent_on_divergent_types(src_conn, tgt_conn, make_table):
    # no-PK (additive); source `n` varchar vs target `n` integer -> coerced insert must be idempotent
    make_table(src_conn, "wAi", 'CREATE TABLE public."wAi" (sito varchar(20), n varchar(10))',
               rows=[("A","1"),("B","2")])
    make_table(tgt_conn, "wAi", 'CREATE TABLE public."wAi" (sito varchar(20), n integer)')
    r1 = sync_table(src_conn, tgt_conn, "wAi", _cfg(), dry_run=False)
    assert r1.inserted == 2
    r2 = sync_table(src_conn, tgt_conn, "wAi", _cfg(), dry_run=False)
    assert r2.inserted == 0                                 # no perpetual re-insert
    cur = tgt_conn.cursor(); cur.execute('select count(*) from public."wAi"')
    assert cur.fetchone()[0] == 2

def test_idempotent_on_v2_char_column(src_conn, tgt_conn, make_table):
    # v2 column is char(3): stored blank-padded; sync must still converge (target hash rtrims char)
    make_table(src_conn, "wC", 'CREATE TABLE public."wC" (id int primary key, code char(3))',
               rows=[(1, "A"), (2, "BB")])
    make_table(tgt_conn, "wC", 'CREATE TABLE public."wC" (id int primary key, code char(3))')
    r1 = sync_table(src_conn, tgt_conn, "wC", _cfg(), dry_run=False)
    assert r1.inserted == 2
    r2 = sync_table(src_conn, tgt_conn, "wC", _cfg(), dry_run=False)
    assert (r2.inserted, r2.updated, r2.deleted) == (0, 0, 0)   # char padding no longer perpetual-updates
