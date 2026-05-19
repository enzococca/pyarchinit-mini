from pyarchinit_mini.graphproj.rapporti_codec import (
    CANONICAL_TO_ITALIAN,
    CANONICAL_TO_ENGLISH,
    display_label,
)


def test_canonical_to_italian_has_known_entries():
    assert CANONICAL_TO_ITALIAN["overlies"] == "Copre"
    assert CANONICAL_TO_ITALIAN["is_after"] == "Coperto da"
    assert CANONICAL_TO_ITALIAN["cuts"] == "Taglia"
    assert CANONICAL_TO_ITALIAN["is_cut_by"] == "Tagliato da"
    assert CANONICAL_TO_ITALIAN["has_same_time"] == "Uguale a"


def test_canonical_to_english_has_known_entries():
    assert CANONICAL_TO_ENGLISH["overlies"] == "Covers"
    assert CANONICAL_TO_ENGLISH["is_after"] == "Covered by"
    assert CANONICAL_TO_ENGLISH["cuts"] == "Cuts"
    assert CANONICAL_TO_ENGLISH["is_cut_by"] == "Cut by"
    assert CANONICAL_TO_ENGLISH["has_same_time"] == "Same as"


def test_display_label_default_locale_italian():
    assert display_label("overlies") == "Copre"


def test_display_label_english():
    assert display_label("overlies", locale="en") == "Covers"


def test_display_label_unknown_canonical_falls_back():
    assert display_label("totally_unknown") == "totally_unknown"
