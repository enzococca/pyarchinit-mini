"""PR8 gate: harris matrix output must not regress visually for standard
unit types after harris_creator_routes is refactored to graphml_io.writer.

This test verifies the structural contract: standard unit types still
produce shapes/styles that the EM-tools / Heriverse ecosystem expects.
The actual route-level integration is exercised separately; here we
isolate EMPalette.get_node_style() which is the visual contract.
"""
from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphml_converter.em_palette import EMPalette

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_us_shape_remains_rectangle_after_cutover():
    style = EMPalette.get_node_style("US100")
    assert style["shape"] == "rectangle"


def test_usm_shape_remains_rectangle_after_cutover():
    style = EMPalette.get_node_style("USM100")
    assert style["shape"] == "rectangle"


def test_usvs_supported_after_cutover():
    style = EMPalette.get_node_style("USVs100")
    assert style["shape"] == "parallelogram"


def test_unknown_type_fallback_after_cutover():
    style = EMPalette.get_node_style("ZZZ100")
    assert style["shape"] == "rectangle"  # fallback grey rect
    assert style["fill_color"] in ("#CCCCCC", "#FFFFFF")
