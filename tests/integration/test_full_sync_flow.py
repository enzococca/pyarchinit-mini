# -*- coding: utf-8 -*-
"""Integration test for the full sync lifecycle."""
import os
import json
import tempfile
from pyarchinit_mini.stratigraph import (
    SyncStateMachine, SyncState, SyncQueue, generate_uuid, validate_uuid,
    BundleCreator, validate_bundle,
)
from pyarchinit_mini.stratigraph.sync_state_machine import SettingsManager


def test_full_bundle_lifecycle():
    """Test: create bundle -> validate -> enqueue."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a data file
        data_file = os.path.join(tmpdir, "export.jsonld")
        with open(data_file, "w") as f:
            json.dump({"@context": "cidoc-crm"}, f)

        # Create bundle
        out = os.path.join(tmpdir, "bundles")
        creator = BundleCreator(output_dir=out, site_name="IntegTest")
        creator.add_data_file(data_file)
        result = creator.build()
        assert result["success"]

        # Validate bundle
        val = validate_bundle(result["bundle_path"])
        assert val["valid"]

        # State machine transitions
        config_path = os.path.join(tmpdir, "sync_settings.json")
        sm = SyncStateMachine(settings_manager=SettingsManager(config_path=config_path))
        assert sm.transition(SyncState.LOCAL_EXPORT)
        assert sm.transition(SyncState.LOCAL_VALIDATION)
        assert sm.transition(SyncState.QUEUED_FOR_SYNC)

        # Enqueue
        db_path = os.path.join(tmpdir, "sync_queue.sqlite")
        q = SyncQueue(db_path=db_path)
        eid = q.enqueue(result["bundle_path"], result["manifest_hash"])
        assert eid is not None

        stats = q.get_stats()
        assert stats["pending"] == 1


def test_uuid_generation_and_validation():
    """Test UUID generation and validation round-trip."""
    uid = generate_uuid()
    assert validate_uuid(uid)
    assert len(uid) == 36
