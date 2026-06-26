def select_mode(rowcount: int, has_pk: bool, threshold: int, override: str | None) -> str:
    if override in ("full", "keyset", "replace"):
        return override
    if not has_pk:
        return "replace"
    if rowcount > threshold:
        return "keyset"
    return "full"

def preserve_set_for_table(global_preserve: frozenset[str], src_cols: set[str], tgt_cols: set[str], extra: list[str]) -> set[str]:
    target_only = set(tgt_cols) - set(src_cols)
    en_cols = {c for c in tgt_cols if c.endswith("_en")}
    return set(global_preserve) | target_only | en_cols | set(extra or [])

def common_data_columns(src_cols: set[str], tgt_cols: set[str], preserve: set[str]) -> list[str]:
    return sorted((set(src_cols) & set(tgt_cols)) - set(preserve))
