# StratiGraph Sync & Concurrency Integration Design

**Date**: 2026-02-18
**Status**: Approved

## Goal

Align pyarchinit-mini-desk with the pyarchinit QGIS plugin by:
1. Adding concurrency columns to all models (optimistic locking + soft locks)
2. Porting all 9 stratigraph module files (UUID, bundle, sync)
3. Porting concurrency manager and database sync (headless, no Qt)
4. Adding CLI sync commands
5. Adding API sync/conflict endpoints
6. Ensuring strict 1:1 field match for US, Site, InventarioMateriali, Pottery tables

## Architecture: Port & Adapt

Replace Qt/QGIS dependencies with standalone Python equivalents:

| Qt/QGIS | Standalone Replacement |
|---------|----------------------|
| QObject + pyqtSignal | Plain class + callback lists |
| QgsSettings | JSON config file (`~/.pyarchinit/stratigraph_config.json`) |
| QgsNetworkAccessManager | httpx |
| QThread | threading.Thread |
| QgsMessageLog | Python logging |
| QTimer | threading.Timer |
| QEventLoop | threading.Event |

Implementation order: DB Schema -> Stratigraph module -> Concurrency manager -> Database sync -> CLI -> API -> Web UI

## Section 1: Architecture Overview

Port pyarchinit modules, replace Qt/QGIS deps with standalone Python, implement CLI first.

- All 9 stratigraph files ported to `pyarchinit_mini/stratigraph/`
- Concurrency manager ported to `pyarchinit_mini/database/concurrency_manager.py`
- Database sync ported to `pyarchinit_mini/database/database_sync.py`
- Both deployment scenarios: multi-user server (PostgreSQL) + offline sync (SQLite -> server)

## Section 2: DB Schema Changes

### BaseModel additions (7 new columns for all tables)

| Column | Type | Purpose |
|--------|------|---------|
| `entity_uuid` | String(36), unique, indexed | StratiGraph entity identifier |
| `version_number` | Integer, default=1 | Optimistic locking counter |
| `last_modified_by` | String(100) | Username of last editor |
| `last_modified_timestamp` | DateTime(timezone=True) | UTC timestamp of last change |
| `sync_status` | String(20), default='new' | Track sync state per record |
| `editing_by` | String(100), nullable | Soft lock - who is editing |
| `editing_since` | DateTime(timezone=True), nullable | Soft lock - since when |

Migration adds these 7 columns to all existing tables. Existing records get auto-generated UUIDs and version_number=1.

### Table field alignment

Compare pyarchinit column lists for us_table, site_table, inventario_materiali_table against mini-desk models. Add any missing columns to achieve strict 1:1 match.

## Section 3: Stratigraph Module Port

All 9 files ported to `pyarchinit_mini/stratigraph/`:

| Original (pyarchinit) | Ported (mini-desk) | Changes |
|----------------------|---------------------|---------|
| uuid_manager.py | Direct copy | No Qt deps |
| bundle_manifest.py | Direct copy | No Qt deps |
| bundle_creator.py | Fix imports | `modules.stratigraph.` -> `pyarchinit_mini.stratigraph.` |
| bundle_validator.py | Fix imports | Same |
| sync_state_machine.py | Rewrite signals | QObject->class, pyqtSignal->callbacks, QgsSettings->JSON |
| sync_queue.py | Minor logging | QgsMessageLog->logging |
| connectivity_monitor.py | Full rewrite | QTimer->threading.Timer, network->httpx |
| sync_orchestrator.py | Full rewrite | All Qt networking->httpx, QTimer->threading.Timer |
| __init__.py | Update imports | New package path |

### Signal replacement pattern

```python
class SyncStateMachine:
    def __init__(self):
        self._on_state_changed = []

    def on_state_changed(self, callback):
        self._on_state_changed.append(callback)

    def _notify_state_changed(self, old, new):
        for cb in self._on_state_changed:
            cb(old, new)
```

### Settings replacement

QgsSettings -> JSON config at `~/.pyarchinit/stratigraph_config.json` with `SettingsManager` wrapper.

## Section 4: Concurrency Manager

Port `concurrency_manager.py` without Qt GUI:

- **Keep**: check_version_conflict, handle_conflict, lock_record, unlock_record, get_active_editors, id_field_mappings
- **Remove**: ConflictResolutionDialog (Qt), RecordLockIndicator (Qt)
- **Add**: CLI conflict resolution (Click prompts), API conflict endpoints (JSON)
- **SQLAlchemy integration**: Use mini-desk engine/session instead of raw SQL

## Section 5: Database Sync

Port `database_sync.py`:

- DatabaseAdapter ABC: Keep as-is
- PostgreSQLAdapter: SQLAlchemy engine (not psql subprocess)
- SQLiteAdapter: Keep SpatiaLite support via SQLAlchemy
- SyncAnalyzer: QThread -> threading.Thread + callbacks
- SyncWorker: QThread -> threading.Thread + progress callbacks
- DatabaseSyncManager: QObject -> plain class + callback pattern
- SyncConfig: dataclass, loaded from JSON config

### Differential sync logic

1. Compare last_modified_timestamp between local and remote
2. Records with sync_status='modified' get pushed
3. Version conflict check before applying remote changes
4. sync_status values: 'new', 'synced', 'modified', 'conflict'

## Section 6: CLI Commands

New Click command group `sync`:

```
pyarchinit-mini sync status          # Show sync state, queue stats, connectivity
pyarchinit-mini sync export [--site] # Export bundle for a site
pyarchinit-mini sync push            # Force upload of pending bundles
pyarchinit-mini sync pull            # Download changes from remote
pyarchinit-mini sync resolve         # Interactive conflict resolution
pyarchinit-mini sync config          # View/set sync settings
pyarchinit-mini sync queue list      # List queued bundles
pyarchinit-mini sync queue retry     # Retry failed entries
pyarchinit-mini sync queue clean     # Remove completed entries
pyarchinit-mini connectivity check   # One-shot connectivity test
```

Extended existing commands:
- `pyarchinit-mini user create/list/delete/update` (JWT auth with roles)
- `pyarchinit-mini db migrate` extended with concurrency columns migration

## Section 7: API Endpoints

### New `/api/v1/sync/` router

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /sync/status | Sync state + queue stats |
| POST | /sync/export | Trigger bundle export |
| POST | /sync/push | Upload pending bundles |
| POST | /sync/pull | Download remote changes |
| GET | /sync/queue | List queue entries |
| POST | /sync/queue/{id}/retry | Retry failed entry |
| GET | /sync/conflicts | List unresolved conflicts |
| POST | /sync/conflicts/{id}/resolve | Resolve a conflict |
| GET | /sync/connectivity | Check remote connectivity |

### New `/api/v1/users/` router

CRUD + role assignment for user management.

### Existing entity endpoints changes

- Optimistic locking via `If-Match` header (version_number)
- 409 Conflict response on version mismatch
- Soft locking via `X-Lock-Record` / `X-Unlock-Record` headers
