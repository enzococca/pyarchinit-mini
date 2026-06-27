def select_mode(has_single_pk: bool) -> str:
    return "mapped" if has_single_pk else "additive"

def is_gated(rowcount: int, threshold: int) -> bool:
    return rowcount > threshold

def preserve_set_for_table(global_preserve: frozenset[str], src_cols: set[str], tgt_cols: set[str], extra: list[str]) -> set[str]:
    target_only = set(tgt_cols) - set(src_cols)
    en_cols = {c for c in tgt_cols if c.endswith("_en")}
    return set(global_preserve) | target_only | en_cols | set(extra or [])

def common_data_columns(src_cols: set[str], tgt_cols: set[str], preserve: set[str]) -> list[str]:
    return sorted((set(src_cols) & set(tgt_cols)) - set(preserve))
