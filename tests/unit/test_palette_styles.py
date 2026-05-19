from pyarchinit_mini.em_palette.styles import NodeStyle, EdgeStyle


def test_node_style_defaults():
    s = NodeStyle(unit_type="US")
    assert s.unit_type == "US"
    assert s.shape == "rectangle"
    assert s.fill_color == "#FFFFFF"
    assert s.border_color == "#000000"
    assert s.border_width == 1.0
    assert s.border_style == "line"


def test_edge_style_defaults():
    e = EdgeStyle(canonical_name="overlies")
    assert e.canonical_name == "overlies"
    assert e.line_color == "#000000"
    assert e.line_width == 1.0
    assert e.line_style == "line"
    assert e.arrow_target == "standard"
