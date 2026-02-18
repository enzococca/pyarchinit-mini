"""Test sync orchestrator."""
import os
import tempfile
from pyarchinit_mini.stratigraph.sync_orchestrator import SyncOrchestrator


def test_orchestrator_get_status():
    with tempfile.TemporaryDirectory() as tmpdir:
        orch = SyncOrchestrator(config_dir=tmpdir)
        status = orch.get_status()
        assert status["state"] == "OFFLINE_EDITING"
        assert status["online"] is False
        assert "queue_stats" in status


def test_orchestrator_start_stop():
    with tempfile.TemporaryDirectory() as tmpdir:
        orch = SyncOrchestrator(config_dir=tmpdir)
        orch.start()
        assert orch._running is True
        orch.stop()
        assert orch._running is False
