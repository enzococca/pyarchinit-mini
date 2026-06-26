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
