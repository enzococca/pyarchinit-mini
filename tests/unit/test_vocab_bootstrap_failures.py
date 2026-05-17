from pathlib import Path
import pytest

from pyarchinit_mini.vocab.loader import load_node_datamodel
from pyarchinit_mini.vocab.exceptions import VocabBootstrapError, VocabSchemaError


def test_missing_json_config_dir_raises_bootstrap_error(tmp_path):
    with pytest.raises(VocabBootstrapError):
        load_node_datamodel(json_config_dir=tmp_path / "nonexistent")


def test_malformed_json_raises_schema_error_with_location():
    fix = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "malformed"
    with pytest.raises(VocabSchemaError) as exc_info:
        load_node_datamodel(json_config_dir=fix)
    assert exc_info.value.line > 0
    assert exc_info.value.column >= 0


def test_empty_dir_with_no_pillars_raises_bootstrap_error(tmp_path):
    """A directory that exists but has no expected JSON file → BootstrapError."""
    empty = tmp_path / "empty_config"
    empty.mkdir()
    with pytest.raises(VocabBootstrapError):
        load_node_datamodel(json_config_dir=empty)
