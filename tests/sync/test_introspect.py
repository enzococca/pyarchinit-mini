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
