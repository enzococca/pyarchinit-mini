from pathlib import Path
from pyarchinit_mini.vocab.i18n import VocabI18n


def test_lookup_returns_translated_label_in_italian():
    i18n = VocabI18n(translations_dir=Path("pyarchinit_mini/vocab/translations"))
    label = i18n.unit_type_label("US", lang="it")
    assert label  # non-empty
    assert isinstance(label, str)


def test_lookup_falls_back_to_english_when_lang_missing():
    i18n = VocabI18n(translations_dir=Path("pyarchinit_mini/vocab/translations"))
    label = i18n.unit_type_label("US", lang="xx")  # nonexistent
    assert label  # English fallback


def test_lookup_returns_abbreviation_when_no_translation_anywhere():
    i18n = VocabI18n(translations_dir=Path("pyarchinit_mini/vocab/translations"))
    label = i18n.unit_type_label("ZZZ_NEW_NEVER_SEEN", lang="it")
    assert label == "ZZZ_NEW_NEVER_SEEN"
    assert "it:ZZZ_NEW_NEVER_SEEN" in i18n.missing_translations


def test_edge_type_label_translation():
    i18n = VocabI18n(translations_dir=Path("pyarchinit_mini/vocab/translations"))
    label = i18n.edge_type_label("overlies", lang="it")
    assert label == "copre"


def test_edge_aliases_returns_italian_variants_for_parsing():
    i18n = VocabI18n(translations_dir=Path("pyarchinit_mini/vocab/translations"))
    # is_after only covers "coperto da" / "coperta da" — "tagliato da" was
    # wrongly grouped here; it belongs to is_cut_by (fixed in vocab_it.json).
    aliases_after = i18n.edge_aliases("is_after", lang="it")
    assert "coperto da" in aliases_after
    assert "tagliato da" not in aliases_after
    # Verify tagliato da now lives under is_cut_by
    aliases_cut = i18n.edge_aliases("is_cut_by", lang="it")
    assert "tagliato da" in aliases_cut


def test_edge_aliases_missing_returns_empty_tuple():
    i18n = VocabI18n(translations_dir=Path("pyarchinit_mini/vocab/translations"))
    aliases = i18n.edge_aliases("nonexistent_edge", lang="it")
    assert aliases == ()
