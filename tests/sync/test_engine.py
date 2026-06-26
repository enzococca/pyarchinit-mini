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
