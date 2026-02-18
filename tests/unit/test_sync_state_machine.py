"""Test sync state machine."""
import tempfile
import os
from pyarchinit_mini.stratigraph.sync_state_machine import (
    SyncStateMachine, SyncState, SettingsManager, VALID_TRANSITIONS
)


def test_initial_state_is_offline_editing():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SyncStateMachine(SettingsManager(os.path.join(tmpdir, "cfg.json")))
        assert sm.current_state == SyncState.OFFLINE_EDITING


def test_valid_transition():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SyncStateMachine(SettingsManager(os.path.join(tmpdir, "cfg.json")))
        assert sm.transition(SyncState.LOCAL_EXPORT) is True
        assert sm.current_state == SyncState.LOCAL_EXPORT


def test_invalid_transition():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SyncStateMachine(SettingsManager(os.path.join(tmpdir, "cfg.json")))
        # Cannot go directly from OFFLINE_EDITING to SYNC_SUCCESS
        assert sm.transition(SyncState.SYNC_SUCCESS) is False
        assert sm.current_state == SyncState.OFFLINE_EDITING


def test_callback_on_state_change():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SyncStateMachine(SettingsManager(os.path.join(tmpdir, "cfg.json")))
        changes = []
        sm.on_state_changed(lambda old, new: changes.append((old, new)))
        sm.transition(SyncState.LOCAL_EXPORT)
        assert len(changes) == 1
        assert changes[0] == ("OFFLINE_EDITING", "LOCAL_EXPORT")


def test_state_persists():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_path = os.path.join(tmpdir, "cfg.json")
        sm1 = SyncStateMachine(SettingsManager(cfg_path))
        sm1.transition(SyncState.LOCAL_EXPORT)
        sm2 = SyncStateMachine(SettingsManager(cfg_path))
        assert sm2.current_state == SyncState.LOCAL_EXPORT


def test_transition_history():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SyncStateMachine(SettingsManager(os.path.join(tmpdir, "cfg.json")))
        sm.transition(SyncState.LOCAL_EXPORT)
        sm.transition(SyncState.LOCAL_VALIDATION)
        history = sm.get_transition_history(limit=10)
        assert len(history) == 2
        assert history[0]["to"] == "LOCAL_VALIDATION"
        assert history[1]["to"] == "LOCAL_EXPORT"


def test_reset():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SyncStateMachine(SettingsManager(os.path.join(tmpdir, "cfg.json")))
        sm.transition(SyncState.LOCAL_EXPORT)
        sm.reset()
        assert sm.current_state == SyncState.OFFLINE_EDITING
        assert sm.get_transition_history() == []
