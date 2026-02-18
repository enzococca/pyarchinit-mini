# -*- coding: utf-8 -*-
"""
Connectivity monitor for StratiGraph sync.

Periodically checks a configurable health-check endpoint and notifies
callbacks when connectivity changes. Uses debouncing to avoid
flapping on unstable networks.
"""
import logging
import threading
from typing import Optional

import httpx

from pyarchinit_mini.stratigraph.sync_state_machine import SettingsManager

logger = logging.getLogger(__name__)

DEFAULT_HEALTH_URL = "http://localhost:8080/health"
DEFAULT_INTERVAL_S = 30
DEFAULT_DEBOUNCE = 2
REQUEST_TIMEOUT_S = 5


class ConnectivityMonitor:
    """Monitors network connectivity to the StratiGraph server.

    Notifies callbacks when connectivity status changes. Uses a debounce
    counter so that N consecutive identical results are required
    before the reported state actually flips.
    """

    def __init__(self, check_interval_s: int = None,
                 debounce_count: int = None,
                 health_url: str = None,
                 settings_manager: Optional[SettingsManager] = None):
        settings = settings_manager or SettingsManager()

        self._check_interval = (
            check_interval_s
            if check_interval_s is not None
            else settings.get("check_interval_s", DEFAULT_INTERVAL_S))
        self._debounce_count = (
            debounce_count
            if debounce_count is not None
            else settings.get("debounce_count", DEFAULT_DEBOUNCE))
        self._health_url = (
            health_url
            if health_url is not None
            else settings.get("health_check_url", DEFAULT_HEALTH_URL))

        self._is_online = False
        self._consecutive_same = 0
        self._last_probe_result = None
        self._timer = None
        self._running = False

        # Callbacks
        self._on_connection_available = []
        self._on_connection_lost = []
        self._on_connectivity_changed = []

    # -- callback registration -----------------------------------------------

    def on_connection_available(self, callback):
        """Register callback() called when connectivity is restored."""
        self._on_connection_available.append(callback)

    def on_connection_lost(self, callback):
        """Register callback() called when connectivity is lost."""
        self._on_connection_lost.append(callback)

    def on_connectivity_changed(self, callback):
        """Register callback(is_online: bool) called on any change."""
        self._on_connectivity_changed.append(callback)

    # -- public API ----------------------------------------------------------

    @property
    def is_online(self) -> bool:
        return self._is_online

    def start(self):
        """Start periodic connectivity checks."""
        self._running = True
        self._schedule_check()
        # Run an immediate check
        threading.Thread(target=self._do_check, daemon=True).start()

    def stop(self):
        """Stop periodic checks."""
        self._running = False
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def check_now(self):
        """Force an immediate connectivity check."""
        self._do_check()

    def set_check_interval(self, seconds: int):
        """Update the check interval (seconds)."""
        self._check_interval = seconds

    # -- internal ------------------------------------------------------------

    def _schedule_check(self):
        """Schedule the next periodic check."""
        if not self._running:
            return
        self._timer = threading.Timer(self._check_interval, self._timer_fired)
        self._timer.daemon = True
        self._timer.start()

    def _timer_fired(self):
        """Called when the timer fires."""
        self._do_check()
        self._schedule_check()

    def _do_check(self):
        """Perform a single health-check probe."""
        reachable = self._probe()
        self._update_state(reachable)

    def _probe(self) -> bool:
        """HTTP GET to health endpoint. Returns True on 2xx."""
        try:
            response = httpx.get(self._health_url, timeout=REQUEST_TIMEOUT_S)
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.debug(f"Connectivity probe failed: {e}")
            return False

    def _update_state(self, probe_result: bool):
        """Apply debounce logic and notify callbacks if state changes."""
        if probe_result == self._last_probe_result:
            self._consecutive_same += 1
        else:
            self._consecutive_same = 1
            self._last_probe_result = probe_result

        if self._consecutive_same < self._debounce_count:
            return

        if probe_result == self._is_online:
            return  # no change

        self._is_online = probe_result
        for cb in self._on_connectivity_changed:
            cb(self._is_online)

        if self._is_online:
            logger.info("Connectivity restored")
            for cb in self._on_connection_available:
                cb()
        else:
            logger.warning("Connectivity lost")
            for cb in self._on_connection_lost:
                cb()
