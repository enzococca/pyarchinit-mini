import pytest
from pyarchinit_mini.vocab.types import UnitType, EdgeType, VisualStyle


def test_visual_style_fallback_is_neutral_rectangle():
    fb = VisualStyle.fallback()
    assert fb.shape == "rectangle"
    assert fb.fill_color == "#CCCCCC"
    assert fb.border_color == "#000000"


def test_dataclasses_are_frozen():
    style = VisualStyle(shape="rectangle", fill_color="#fff", border_color="#000", border_style="solid")
    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        style.shape = "hexagon"


def test_unit_type_carries_visual_style():
    style = VisualStyle(shape="parallelogram", fill_color="#FFF", border_color="#000", border_style="solid")
    ut = UnitType(
        abbreviation="USVs",
        class_name="StructuralVirtualStratigraphicUnit",
        parent="StratigraphicNode",
        label="USV/s",
        description="...",
        symbol="black parallelogram",
        family="virtual",
        is_series=False,
        cidoc_mapping="A2 Stratigraphic Volume Unit",
        properties={"name": "P1_is_identified_by"},
        visual_style=style,
    )
    assert ut.visual_style.shape == "parallelogram"
    assert ut.family == "virtual"


def test_edge_type_legal_pairs_is_immutable():
    e = EdgeType(
        name="covers",
        label="copre",
        italian_aliases=("copre", "coperto da"),
        symmetric=False,
        legal_pairs=(("US", "US"), ("US", "USM")),
    )
    assert ("US", "USM") in e.legal_pairs
