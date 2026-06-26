from pyarchinit_mini.sync.policy import select_mode, preserve_set_for_table, common_data_columns

def test_select_mode_override_wins():
    assert select_mode(10, True, 200_000, "replace") == "replace"

def test_select_mode_no_pk_is_replace():
    assert select_mode(10, False, 200_000, None) == "replace"

def test_select_mode_large_is_keyset():
    assert select_mode(500_000, True, 200_000, None) == "keyset"

def test_select_mode_small_is_full():
    assert select_mode(1915, True, 200_000, None) == "full"

def test_preserve_set_includes_target_only_and_en_cols():
    p = preserve_set_for_table(
        frozenset({"order_layer"}),
        src_cols={"sito", "descrizione"},
        tgt_cols={"sito", "descrizione", "descrizione_en", "node_uuid", "order_layer"},
        extra=["custom_col"],
    )
    assert {"order_layer", "descrizione_en", "node_uuid", "custom_col"} <= p
    assert "sito" not in p

def test_common_data_columns_excludes_preserved():
    cols = common_data_columns(
        src_cols={"id_us", "sito", "us", "order_layer"},
        tgt_cols={"id_us", "sito", "us", "order_layer", "node_uuid"},
        preserve={"order_layer", "node_uuid"},
    )
    assert cols == ["id_us", "sito", "us"]
