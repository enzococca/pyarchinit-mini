from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphproj.edge_registry import EdgeRegistry

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def reset_provider():
    VocabProvider.reset()
    # Use fixture for json_config_dir (s3dgraphy JSON models)
    # Use default translations_dir (vocab_it.json, vocab_en.json)
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_resolve_alias_returns_canonical_edge_name():
    reg = EdgeRegistry()
    name = reg.resolve_italian_alias("copre")
    assert name == "overlies"


def test_resolve_compound_alias_coperto_da():
    """«coperto da» is no longer an alias of the temporal is_after. Like
    «tagliato da» it is the reverse reading of a datamodel edge
    (is_overlain_by), which the registry does not list; the codec resolves it."""
    reg = EdgeRegistry()
    assert reg.resolve_italian_alias("coperto da") is None
    from pyarchinit_mini.graphproj.rapporti_codec import _resolve_canonical
    assert _resolve_canonical("Coperto da") == "is_overlain_by"


def test_uguale_a_is_equals_not_has_same_time():
    reg = EdgeRegistry()
    assert reg.resolve_italian_alias("uguale a") == "equals"


def test_resolve_alias_unknown_returns_none():
    reg = EdgeRegistry()
    assert reg.resolve_italian_alias("xyzzy") is None


def test_longest_alias_wins():
    """coperto da (longer) must match before copre when both candidates.

    Here 'coperto' alone is NOT an alias of anything (only the full
    'coperto da' is), so it must return None — not silently match 'copre'.
    """
    reg = EdgeRegistry()
    assert reg.resolve_italian_alias("coperto") is None
