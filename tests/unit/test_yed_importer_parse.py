"""Tests for yed_importer.parse_extended_matrix."""
from pathlib import Path
import pytest

from pyarchinit_mini.graphml_io.yed_importer import parse_extended_matrix
from pyarchinit_mini.harris_swimlane.exceptions import YEDImporterError

FIX = Path(__file__).parent.parent / "fixtures" / "yed_graphml"


def test_parse_minimal_returns_expected_nodes():
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    assert len(parsed.nodes) == 3
    assert parsed.nodes[0]["us"] == "1"
    assert parsed.nodes[0]["sito"] == "TestSite"
    assert parsed.nodes[0]["unita_tipo"] == "US"
    assert parsed.nodes[2]["unita_tipo"] == "USVs"


def test_parse_minimal_returns_edges():
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    assert len(parsed.edges) == 2
    e = parsed.edges[0]
    assert e["us_from"] == "1" and e["us_to"] == "2"


def test_parse_minimal_returns_epochs():
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    assert len(parsed.epochs) == 1
    assert parsed.epochs[0]["name"] == "P1"


def test_parse_vanilla_yed_raises():
    with pytest.raises(YEDImporterError, match="not a pyarchinit"):
        parse_extended_matrix(FIX / "vanilla_yed.graphml")


def test_parse_malformed_raises():
    with pytest.raises(YEDImporterError):
        parse_extended_matrix(FIX / "malformed.graphml")


def test_parse_reference_file_runs():
    """Reference fixture parses without error and returns ≥10 nodes."""
    parsed = parse_extended_matrix(FIX / "extended_matrix_pyarchinit.graphml")
    assert len(parsed.nodes) >= 10
