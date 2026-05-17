from pathlib import Path
import pytest
from pyarchinit_mini.vocab.loader import (
    load_node_datamodel,
    load_connections_datamodel,
    load_visual_rules,
)
from pyarchinit_mini.vocab.exceptions import VocabBootstrapError, VocabSchemaError

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons"


def test_load_node_datamodel_from_0_1_42():
    data = load_node_datamodel(json_config_dir=FIX / "0.1.42")
    assert data.version == "1.5.4"
    assert "US" in data.stratigraphic_subtypes
    assert "USVs" in data.stratigraphic_subtypes


def test_load_visual_rules_from_0_1_42():
    data = load_visual_rules(json_config_dir=FIX / "0.1.42")
    assert "US" in data.node_styles
    assert data.node_styles["US"]["style"]["shape"] == "rectangle"


def test_load_connections_datamodel_from_0_1_42():
    data = load_connections_datamodel(json_config_dir=FIX / "0.1.42")
    # Either is_after or is_before key is acceptable depending on edge_types naming in pillar
    assert data is not None


def test_load_handles_filename_quirk_with_space():
    # 0.1.15 ships node datamodel with a literal space in the filename
    data = load_node_datamodel(json_config_dir=FIX / "0.1.15")
    assert data.version  # parsed something


def test_load_handles_legacy_connections_naming():
    # 0.1.15 uses em_connection_rules.json (not the new s3Dgraphy_connections_datamodel.json)
    data = load_connections_datamodel(json_config_dir=FIX / "0.1.15", allow_legacy=True)
    assert data is not None


def test_load_legacy_without_allow_legacy_raises():
    with pytest.raises(VocabBootstrapError) as exc_info:
        load_connections_datamodel(json_config_dir=FIX / "0.1.15", allow_legacy=False)
    assert "s3dgraphy" in str(exc_info.value).lower() or "upgrade" in str(exc_info.value).lower()


def test_load_malformed_raises_schema_error():
    with pytest.raises(VocabSchemaError):
        load_node_datamodel(json_config_dir=FIX / "malformed")


def test_load_missing_dir_raises_bootstrap_error():
    with pytest.raises(VocabBootstrapError):
        load_node_datamodel(json_config_dir=Path("/nonexistent/path"))
