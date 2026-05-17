from pathlib import Path
import threading
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.vocab.types import UnitType, VisualStyle

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def reset_provider():
    VocabProvider.reset()
    yield
    VocabProvider.reset()


def _instance():
    return VocabProvider.instance(json_config_dir=FIX)


def test_singleton_returns_same_object_on_concurrent_first_access():
    instances = []

    def grab():
        instances.append(_instance())

    threads = [threading.Thread(target=grab) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    first = instances[0]
    for inst in instances:
        assert inst is first


def test_get_unit_types_returns_known_subtypes():
    p = _instance()
    types = p.get_unit_types(lang="en")
    abbrs = {t.abbreviation for t in types}
    assert "US" in abbrs
    assert "USVs" in abbrs


def test_get_unit_type_returns_localized_label():
    p = _instance()
    us_it = p.get_unit_type("US", lang="it")
    assert us_it is not None
    assert "Unità" in us_it.description or "Stratigrafica" in us_it.description


def test_get_unit_type_unknown_returns_none():
    p = _instance()
    assert p.get_unit_type("ZZZ_UNKNOWN") is None


def test_get_visual_style_returns_fallback_for_unknown_type():
    p = _instance()
    style = p.get_visual_style("ZZZ_UNKNOWN")
    assert style == VisualStyle.fallback()


def test_get_visual_style_returns_real_style_for_us():
    p = _instance()
    style = p.get_visual_style("US")
    assert style.shape == "rectangle"
    assert style.fill_color == "#F0F0F0"


def test_diagnostics_includes_versions_and_counts():
    p = _instance()
    d = p.diagnostics()
    assert "data_model_versions" in d
    assert "counts" in d
    assert d["counts"]["unit_types"] > 0
