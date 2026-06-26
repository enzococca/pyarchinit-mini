from dataclasses import dataclass

@dataclass
class Diff:
    inserts: list
    updates: list
    deletes: list

def diff_by_hash(source: dict[tuple, str], target: dict[tuple, str]) -> Diff:
    src_keys, tgt_keys = set(source), set(target)
    inserts = sorted(src_keys - tgt_keys)
    deletes = sorted(tgt_keys - src_keys)
    updates = sorted(k for k in (src_keys & tgt_keys) if source[k] != target[k])
    return Diff(inserts=inserts, updates=updates, deletes=deletes)

def diff_by_keyset(source_keys: set[tuple], target_keys: set[tuple]) -> Diff:
    return Diff(inserts=sorted(source_keys - target_keys),
                updates=[],
                deletes=sorted(target_keys - source_keys))
