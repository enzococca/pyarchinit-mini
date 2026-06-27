from pyarchinit_mini.sync.policy import select_mode, preserve_set_for_table, common_data_columns

def test_select_mode_mapped_when_single_pk():
    assert select_mode(True) == "mapped"

def test_select_mode_additive_when_no_single_pk():
    assert select_mode(False) == "additive"

def test_is_gated_threshold():
    from pyarchinit_mini.sync.policy import is_gated
    assert is_gated(500_000, 200_000) is True
    assert is_gated(1915, 200_000) is False

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
