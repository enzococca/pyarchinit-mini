import warnings
from pathlib import Path
import pytest

from pyarchinit_mini.graphml_converter.em_palette import EMPalette
from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def reset_provider():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_get_node_style_for_us_sources_from_vocab_provider():
    """US must source visual style from em_visual_rules.json (0.1.42).
    US fill_color in 0.1.42 is #F0F0F0 (NOT the legacy #FFFFFF).
    Shape stays rectangle (parity gate)."""
    style = EMPalette.get_node_style("US100")
    assert style["shape"] == "rectangle"
    assert style["fill_color"] == "#F0F0F0"
    assert style["border_color"] == "#540909"


def test_get_node_style_for_usvs_now_supported():
    """USVs is a new type that didn't exist in legacy PALETTE — VocabProvider now provides it."""
    style = EMPalette.get_node_style("USVs42")
    assert style["shape"] == "parallelogram"


def test_get_node_style_for_unknown_type_returns_fallback():
    """Unknown unit types must return a sensible fallback (neutral grey rectangle)."""
    style = EMPalette.get_node_style("ZZZ_UNKNOWN_999")
    assert style["shape"] == "rectangle"
    assert style["fill_color"] == "#CCCCCC"


def test_palette_dict_access_emits_deprecation_warning():
    """Legacy `EMPalette.PALETTE["US"]` access must still work (backward compat) but emit DeprecationWarning."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _ = EMPalette.PALETTE["US"]
        assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_palette_iteration_emits_deprecation_warning_keys():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        list(EMPalette.PALETTE.keys())
        assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_palette_iteration_emits_deprecation_warning_items():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        list(EMPalette.PALETTE.items())
        assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_palette_iteration_emits_deprecation_warning_values():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        list(EMPalette.PALETTE.values())
        assert any(issubclass(w.category, DeprecationWarning) for w in caught)
