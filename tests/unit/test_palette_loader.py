from pathlib import Path
import pytest

from pyarchinit_mini.em_palette.loader import PaletteLoader
from pyarchinit_mini.em_palette.styles import NodeStyle, EdgeStyle


FIXTURE = Path(__file__).parent.parent / "fixtures" / "em_palette_minimal.graphml"


@pytest.fixture
def loader():
    return PaletteLoader(palette_path=FIXTURE)


def test_loader_returns_node_style_for_known_unit_type(loader):
    s = loader.get_node_style("USM")
    assert isinstance(s, NodeStyle)
    assert s.unit_type == "USM"
    assert s.shape  # non-empty
    assert s.fill_color.startswith("#")
    assert s.border_color.startswith("#")


def test_loader_returns_default_for_unknown_unit_type(loader):
    s = loader.get_node_style("UNKNOWN_TYPE_XYZ")
    assert s.unit_type == "UNKNOWN_TYPE_XYZ"
    assert s.shape == "rectangle"  # default from NodeStyle


def test_loader_returns_edge_style_for_canonical(loader):
    s = loader.get_edge_style("overlies")
    assert isinstance(s, EdgeStyle)
    assert s.canonical_name == "overlies"


def test_loader_caches_first_load(loader):
    # First call loads; second hits cache (same object identity for same key)
    first = loader.get_node_style("USM")
    second = loader.get_node_style("USM")
    assert first is second


def test_loader_reload_refreshes_cache(loader):
    first = loader.get_node_style("USM")
    loader.reload()
    second = loader.get_node_style("USM")
    # After reload, cache is rebuilt — different object identity but same content
    assert first is not second
    assert first == second


def test_loader_fallback_when_palette_missing():
    bogus = Path("/nonexistent/em_palette.graphml")
    loader = PaletteLoader(palette_path=bogus, allow_fallback=True)
    s = loader.get_node_style("USM")
    # Falls back to NodeStyle defaults
    assert s.shape == "rectangle"
    assert s.fill_color == "#FFFFFF"
