"""Test bundle creation and validation."""
import os
import tempfile
import json
from pyarchinit_mini.stratigraph.bundle_creator import BundleCreator
from pyarchinit_mini.stratigraph.bundle_validator import validate_bundle


def test_bundle_creator_builds_zip():
    with tempfile.TemporaryDirectory() as tmpdir:
        data_file = os.path.join(tmpdir, "test_data.jsonld")
        with open(data_file, "w") as f:
            json.dump({"@context": "test"}, f)

        output_dir = os.path.join(tmpdir, "output")
        creator = BundleCreator(output_dir=output_dir, site_name="TestSite")
        creator.add_data_file(data_file)
        result = creator.build()

        assert result["success"] is True
        assert result["bundle_path"] is not None
        assert os.path.isfile(result["bundle_path"])
        assert result["file_count"] >= 2  # data file + manifest


def test_bundle_validator_validates_good_bundle():
    with tempfile.TemporaryDirectory() as tmpdir:
        data_file = os.path.join(tmpdir, "test_data.jsonld")
        with open(data_file, "w") as f:
            json.dump({"@context": "test"}, f)

        output_dir = os.path.join(tmpdir, "output")
        creator = BundleCreator(output_dir=output_dir, site_name="TestSite")
        creator.add_data_file(data_file)
        result = creator.build()

        validation = validate_bundle(result["bundle_path"])
        assert validation["valid"] is True


def test_bundle_creator_no_files_error():
    with tempfile.TemporaryDirectory() as tmpdir:
        creator = BundleCreator(output_dir=tmpdir, site_name="Empty")
        result = creator.build()
        assert result["success"] is False
        assert "No files" in result["errors"][0]
