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
