# -*- coding: utf-8 -*-
"""
Sync State Machine for StratiGraph offline-first architecture.

Manages the 6-state lifecycle of bundle synchronization:
OFFLINE_EDITING -> LOCAL_EXPORT -> LOCAL_VALIDATION ->
QUEUED_FOR_SYNC -> SYNC_SUCCESS/SYNC_FAILED -> OFFLINE_EDITING
"""
import json
import logging
import os
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)

CONFIG_DIR = os.path.expanduser("~/.pyarchinit")
CONFIG_FILE = os.path.join(CONFIG_DIR, "stratigraph_config.json")


class SyncState(Enum):
    """Possible states in the sync lifecycle."""
    OFFLINE_EDITING = "OFFLINE_EDITING"
    LOCAL_EXPORT = "LOCAL_EXPORT"
    LOCAL_VALIDATION = "LOCAL_VALIDATION"
    QUEUED_FOR_SYNC = "QUEUED_FOR_SYNC"
    SYNC_SUCCESS = "SYNC_SUCCESS"
    SYNC_FAILED = "SYNC_FAILED"


# Valid state transitions
VALID_TRANSITIONS = {
    SyncState.OFFLINE_EDITING: [SyncState.LOCAL_EXPORT],
    SyncState.LOCAL_EXPORT: [SyncState.LOCAL_VALIDATION],
    SyncState.LOCAL_VALIDATION: [SyncState.QUEUED_FOR_SYNC, SyncState.OFFLINE_EDITING],
    SyncState.QUEUED_FOR_SYNC: [SyncState.SYNC_SUCCESS, SyncState.SYNC_FAILED],
    SyncState.SYNC_FAILED: [SyncState.QUEUED_FOR_SYNC],
    SyncState.SYNC_SUCCESS: [SyncState.OFFLINE_EDITING],
}

MAX_HISTORY = 50


class SettingsManager:
    """JSON-based settings replacement for QgsSettings."""

    def __init__(self, config_path=None):
        self._config_path = config_path or CONFIG_FILE
        self._data = self._load()

    def _load(self):
        try:
            if os.path.isfile(self._config_path):
                with open(self._config_path, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
        return {}

    def _save(self):
        os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
        with open(self._config_path, 'w') as f:
            json.dump(self._data, f, indent=2)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self._save()

    def remove(self, key):
        self._data.pop(key, None)
        self._save()


class SyncStateMachine:
    """State machine governing the sync lifecycle.

    Persists current state and transition history via JSON config.
    Notifies callbacks on every transition.
    """

    def __init__(self, settings_manager=None):
        self._settings = settings_manager or SettingsManager()
        self._state = self._load_state()
        self._on_state_changed = []
        self._on_transition_failed = []

    # -- callback registration -----------------------------------------------

    def on_state_changed(self, callback):
        """Register callback(old_state_value, new_state_value)."""
        self._on_state_changed.append(callback)

    def on_transition_failed(self, callback):
        """Register callback(current_value, attempted_value, reason)."""
        self._on_transition_failed.append(callback)

    # -- public API ----------------------------------------------------------

    @property
    def current_state(self) -> SyncState:
        return self._state

    def transition(self, new_state: SyncState, context: dict = None) -> bool:
        """Attempt a state transition.

        Args:
            new_state: Target state.
            context: Optional metadata stored in transition history.

        Returns:
            True if the transition succeeded, False otherwise.
        """
        old = self._state
        allowed = VALID_TRANSITIONS.get(old, [])

        if new_state not in allowed:
            reason = (f"Transition {old.value} -> {new_state.value} not allowed. "
                      f"Valid targets: {[s.value for s in allowed]}")
            logger.warning(reason)
            for cb in self._on_transition_failed:
                cb(old.value, new_state.value, reason)
            return False

        self._state = new_state
        self._save_state()
        self._append_history(old, new_state, context)

        logger.info(f"State transition: {old.value} -> {new_state.value}")
        for cb in self._on_state_changed:
            cb(old.value, new_state.value)
        return True

    def get_transition_history(self, limit: int = 10) -> list:
        """Return the most recent *limit* transition entries (newest first)."""
        history = self._load_history()
        return history[-limit:][::-1]

    def reset(self):
        """Reset to OFFLINE_EDITING and clear history."""
        old = self._state
        self._state = SyncState.OFFLINE_EDITING
        self._save_state()
        self._settings.remove("sync_history")
        if old != self._state:
            for cb in self._on_state_changed:
                cb(old.value, self._state.value)

    # -- persistence helpers -------------------------------------------------

    def _load_state(self) -> SyncState:
        raw = self._settings.get("sync_state", SyncState.OFFLINE_EDITING.value)
        try:
            return SyncState(raw)
        except (ValueError, KeyError):
            return SyncState.OFFLINE_EDITING

    def _save_state(self):
        self._settings.set("sync_state", self._state.value)

    def _load_history(self) -> list:
        raw = self._settings.get("sync_history", [])
        if isinstance(raw, list):
            return raw
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []

    def _append_history(self, old: SyncState, new: SyncState,
                        context: dict = None):
        history = self._load_history()
        entry = {
            "from": old.value,
            "to": new.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if context:
            entry["context"] = context
        history.append(entry)
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
        self._settings.set("sync_history", history)
