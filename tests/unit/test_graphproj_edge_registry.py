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
    reg = EdgeRegistry()
    name = reg.resolve_italian_alias("coperto da")
    assert name == "is_after"


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
