import os, pytest
pytestmark = pytest.mark.skipif(
    not (os.getenv("TEST_SYNC_SRC_DSN") and os.getenv("TEST_SYNC_TGT_DSN")),
    reason="needs test DBs")
from pyarchinit_mini.sync import rowmap as M

def test_map_crud_and_bootstrap(src_conn, tgt_conn, make_table):
    M.ensure_map_table(tgt_conn); tgt_conn.commit()
    # clean up any leftover map entries for w_map from prior runs (sync_row_map persists)
    tgt_conn.cursor().execute("DELETE FROM public.sync_row_map WHERE table_name = 'w_map'"); tgt_conn.commit()
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
