from pyarchinit_mini.graphproj.rapporti_codec import (
    parse_rapporti,
    serialize_rapporti,
    INVERSE_PAIRS,
    SYMMETRIC,
    Rapporto,
)


def test_parse_empty_returns_empty_list():
    assert parse_rapporti("", current_site="S") == []
    assert parse_rapporti(None, current_site="S") == []


def test_parse_2_tuple_expands_to_4_tuple():
    items = parse_rapporti("[['Coperto da', '120']]", current_site="SiteX")
    assert len(items) == 1
    r = items[0]
    assert r.canonical == "is_after"
    assert r.target_us == "120"
    assert r.target_area is None  # unknown at parse time
    assert r.target_sito == "SiteX"


def test_parse_4_tuple_preserves_area_sito():
    items = parse_rapporti("[['Copre', '120', 'A1', 'SiteX']]", current_site="SiteX")
    assert len(items) == 1
    r = items[0]
    assert r.canonical == "overlies"
    assert r.target_us == "120"
    assert r.target_area == "A1"
    assert r.target_sito == "SiteX"


def test_parse_english_label_resolves_canonical():
    items = parse_rapporti("[['Covers', '120']]", current_site="S")
    assert items[0].canonical == "overlies"


def test_parse_italian_extras_resolve():
    items = parse_rapporti(
        "[['Riempito da', '1'], ['Si lega a', '2'], ['Gli si appoggia', '3']]",
        current_site="S",
    )
    cans = [r.canonical for r in items]
    # "Riempito da" is the inverse of "fills" → is_filled_by (not is_after)
    assert "is_filled_by" in cans      # riempito da — corrected from old wrong mapping
    assert "is_bonded_to" in cans      # si lega a
    # "Gli si appoggia" is the inverse of "abuts" → is_abutted_by (not is_before)
    assert "is_abutted_by" in cans     # gli si appoggia — corrected from old wrong mapping


def test_parse_unknown_label_yields_none():
    items = parse_rapporti("[['totalmente sconosciuto', '5']]", current_site="S")
    assert items == []


def test_parse_malformed_string_returns_empty():
    items = parse_rapporti("not a literal {{{", current_site="S")
    assert items == []


def test_serialize_writes_4_tuple_list():
    items = [
        Rapporto(canonical="overlies", target_us="120", target_area="A1", target_sito="S"),
        Rapporto(canonical="is_after", target_us="121", target_area="A1", target_sito="S"),
    ]
    out = serialize_rapporti(
        items,
        italian_labels={"overlies": "Copre", "is_after": "Coperto da"},
    )
    parsed = eval(out)
    assert parsed == [
        ["Copre", "120", "A1", "S"],
        ["Coperto da", "121", "A1", "S"],
    ]


def test_serialize_emits_none_area_as_empty_string():
    items = [Rapporto(canonical="overlies", target_us="120", target_area=None, target_sito="S")]
    out = serialize_rapporti(items, italian_labels={"overlies": "Copre"})
    parsed = eval(out)
    assert parsed == [["Copre", "120", "", "S"]]


def test_inverse_pairs_covers_directional():
    for can in ("overlies", "is_after", "cuts", "is_cut_by", "fills", "abuts", "is_before"):
        assert can in INVERSE_PAIRS or can in SYMMETRIC, (
            f"{can} missing from INVERSE_PAIRS/SYMMETRIC"
        )


def test_symmetric_has_same_time_and_is_bonded():
    assert "has_same_time" in SYMMETRIC
    assert "is_bonded_to" in SYMMETRIC


def test_serialize_dedups_by_canonical_us_area_sito():
    items = [
        Rapporto(canonical="overlies", target_us="120", target_area="A", target_sito="S"),
        Rapporto(canonical="overlies", target_us="120", target_area="A", target_sito="S"),
        Rapporto(canonical="overlies", target_us="121", target_area="A", target_sito="S"),
    ]
    out = serialize_rapporti(items, italian_labels={"overlies": "Copre"})
    parsed = eval(out)
    assert len(parsed) == 2
