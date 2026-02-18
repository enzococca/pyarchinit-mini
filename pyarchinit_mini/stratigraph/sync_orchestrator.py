# -*- coding: utf-8 -*-
"""
Sync Orchestrator for StratiGraph offline-first architecture.

Coordinates the state machine, sync queue and connectivity monitor
to drive the export -> validate -> enqueue -> upload lifecycle.
"""
import logging
import os
import threading

import httpx

from pyarchinit_mini.stratigraph.sync_state_machine import SyncStateMachine, SyncState, SettingsManager
from pyarchinit_mini.stratigraph.sync_queue import SyncQueue
from pyarchinit_mini.stratigraph.connectivity_monitor import ConnectivityMonitor
from pyarchinit_mini.stratigraph.bundle_creator import BundleCreator
from pyarchinit_mini.stratigraph.bundle_validator import validate_bundle

logger = logging.getLogger(__name__)

BACKOFF_SCHEDULE = [30, 60, 120, 300, 900]


class SyncOrchestrator:
    """Ties together state machine, queue and connectivity.

    Automatically processes the queue when connectivity is available
    and retries failed uploads with exponential backoff.
    """

    def __init__(self, config_dir=None, settings_manager=None):
        self._settings = settings_manager or SettingsManager(
            config_path=os.path.join(config_dir, "stratigraph_config.json") if config_dir else None
        )
        self.state_machine = SyncStateMachine(settings_manager=self._settings)

        queue_dir = config_dir or os.path.expanduser("~/.pyarchinit")
        self.queue = SyncQueue(db_path=os.path.join(queue_dir, "stratigraph_sync_queue.sqlite"))
        self.connectivity = ConnectivityMonitor(settings_manager=self._settings)

        self._running = False
        self._processing = False

        self._upload_endpoint = self._settings.get(
            "upload_endpoint", "http://localhost:8080/api/v1/bundles")

        # Callback lists
        self._on_sync_started = []
        self._on_sync_progress = []
        self._on_sync_completed = []
        self._on_bundle_exported = []

        # Auto-process queue when connectivity returns
        self.connectivity.on_connection_available(self._process_queue)

    # -- callback registration -----------------------------------------------

    def on_sync_started(self, callback):
        """Register callback(entry_id)."""
        self._on_sync_started.append(callback)

    def on_sync_progress(self, callback):
        """Register callback(entry_id, percent, message)."""
        self._on_sync_progress.append(callback)

    def on_sync_completed(self, callback):
        """Register callback(entry_id, success, message)."""
        self._on_sync_completed.append(callback)

    def on_bundle_exported(self, callback):
        """Register callback(bundle_path)."""
        self._on_bundle_exported.append(callback)

    # -- lifecycle -----------------------------------------------------------

    def start(self):
        """Start the orchestrator and connectivity monitor."""
        self._running = True
        self.connectivity.start()
        self.queue.cleanup_completed(older_than_days=7)
        logger.info("SyncOrchestrator started")

    def stop(self):
        """Stop the orchestrator and connectivity monitor."""
        self._running = False
        self.connectivity.stop()
        logger.info("SyncOrchestrator stopped")

    # -- public API ----------------------------------------------------------

    def export_bundle(self, site_name: str = None) -> dict:
        """Run the full export -> validate -> enqueue pipeline."""
        result = {"success": False, "bundle_path": None, "errors": []}

        if not self.state_machine.transition(SyncState.LOCAL_EXPORT, {"site": site_name}):
            result["errors"].append(
                f"Cannot start export from current state: {self.state_machine.current_state.value}")
            return result

        home = os.environ.get("PYARCHINIT_HOME", "")
        output_dir = os.path.join(home, "stratigraph_bundles")

        try:
            creator = BundleCreator(output_dir=output_dir, site_name=site_name)
            db_folder = os.path.join(home, "pyarchinit_DB_folder")
            if os.path.isdir(db_folder):
                creator.add_directory(db_folder, "data", extensions=[".sqlite", ".gpkg"])
            build_result = creator.build()
        except Exception as e:
            self.state_machine.transition(SyncState.LOCAL_VALIDATION)
            self.state_machine.transition(SyncState.OFFLINE_EDITING, {"error": str(e)})
            result["errors"].append(f"Bundle creation failed: {e}")
            return result

        if not build_result.get("success"):
            self.state_machine.transition(SyncState.LOCAL_VALIDATION)
            self.state_machine.transition(SyncState.OFFLINE_EDITING,
                                          {"errors": build_result.get("errors")})
            result["errors"] = build_result.get("errors", [])
            return result

        bundle_path = build_result["bundle_path"]

        if not self.state_machine.transition(SyncState.LOCAL_VALIDATION):
            result["errors"].append("Transition to LOCAL_VALIDATION failed")
            return result

        validation = validate_bundle(bundle_path)
        if not validation.get("valid"):
            self.state_machine.transition(SyncState.OFFLINE_EDITING,
                                          {"validation_errors": validation.get("errors")})
            result["errors"] = [e.get("message", str(e)) for e in validation.get("errors", [])]
            return result

        if not self.state_machine.transition(SyncState.QUEUED_FOR_SYNC):
            result["errors"].append("Transition to QUEUED_FOR_SYNC failed")
            return result

        entry_id = self.queue.enqueue(
            bundle_path,
            build_result.get("manifest_hash", ""),
            metadata={"site": site_name, "timestamp": build_result.get("timestamp")})

        result["success"] = True
        result["bundle_path"] = bundle_path
        result["entry_id"] = entry_id

        for cb in self._on_bundle_exported:
            cb(bundle_path)

        if self.connectivity.is_online:
            threading.Timer(0, self._process_queue).start()

        return result

    def sync_now(self):
        """Force an immediate sync attempt if online."""
        if self.connectivity.is_online:
            self._process_queue()
        else:
            logger.warning("sync_now called but offline")

    def get_status(self) -> dict:
        """Return a snapshot of the orchestrator's status."""
        return {
            "state": self.state_machine.current_state.value,
            "online": self.connectivity.is_online,
            "queue_stats": self.queue.get_stats(),
            "running": self._running,
        }

    # -- internal queue processing -------------------------------------------

    def _process_queue(self):
        """Process pending entries one at a time."""
        if self._processing or not self._running:
            return
        self._processing = True

        try:
            while True:
                entry = self.queue.dequeue()
                if entry is None:
                    break

                for cb in self._on_sync_started:
                    cb(entry.id)
                for cb in self._on_sync_progress:
                    cb(entry.id, 0, "Uploading bundle...")

                success = self._upload_bundle(entry.bundle_path, self._upload_endpoint)
                if success:
                    self.queue.mark_completed(entry.id)
                    for cb in self._on_sync_progress:
                        cb(entry.id, 100, "Upload complete")
                    for cb in self._on_sync_completed:
                        cb(entry.id, True, "Sync successful")
                    if self.state_machine.current_state == SyncState.QUEUED_FOR_SYNC:
                        self.state_machine.transition(SyncState.SYNC_SUCCESS)
                        self.state_machine.transition(SyncState.OFFLINE_EDITING)
                else:
                    error_msg = "Upload failed"
                    self.queue.mark_failed(entry.id, error_msg)
                    for cb in self._on_sync_completed:
                        cb(entry.id, False, error_msg)
                    if self.state_machine.current_state == SyncState.QUEUED_FOR_SYNC:
                        self.state_machine.transition(SyncState.SYNC_FAILED)

                    delay_idx = min(entry.attempts, len(BACKOFF_SCHEDULE) - 1)
                    delay_s = BACKOFF_SCHEDULE[delay_idx]
                    threading.Timer(delay_s, self._process_queue).start()
                    break
        finally:
            self._processing = False

    def _upload_bundle(self, bundle_path: str, endpoint: str) -> bool:
        """Upload a bundle ZIP via HTTP POST."""
        if not os.path.isfile(bundle_path):
            logger.warning(f"Bundle file not found: {bundle_path}")
            return False

        try:
            with open(bundle_path, "rb") as f:
                data = f.read()

            response = httpx.post(
                endpoint,
                content=data,
                headers={"Content-Type": "application/zip"},
                timeout=60.0,
            )
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.warning(f"Upload exception: {e}")
            return False
