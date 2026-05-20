# Plugin QGIS Migration to pyarchinit-s3dgraphy-bridge v1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the QGIS plugin from inline `modules/s3dgraphy/sync/*.py` (23 implementation files + 1 master `__init__.py`) to consuming `pyarchinit-s3dgraphy-bridge==1.0.0` via shim re-export. Zero plugin call sites touched (~80 files unaffected). End state: tag `5.9.1-bridge-migration-alpha` with the inline files reduced to 1-line `from pyarchinit_s3dgraphy_bridge.X import *` each.

**Architecture:** Shim re-export strategy (Q6=C in spec). 5 QGIS-side adapter classes implement the bridge Protocols. Bridge is installed into the plugin's `ext_libs/` by the existing `modules_installer.py`. Plugin v6.0.0 "Great Cleanup" (deferred) will eventually delete the shim files entirely.

**Tech Stack:** Python 3.11+, PyQt5, QGIS API, pyarchinit-s3dgraphy-bridge>=1.0.

**Hard pre-requisite:** `pyarchinit-s3dgraphy-bridge==1.0.0` published to PyPI with green AC-2 suite (Plan 1 complete).

**Spec reference:** [`docs/superpowers/specs/2026-05-20-s3dgraphy-bridge-design.md`](../specs/2026-05-20-s3dgraphy-bridge-design.md)

**Plugin path:** `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit`

**File count reconciliation:** The spec says "22 files"; on-disk audit (2026-05-20) finds **24 entries** under `modules/s3dgraphy/sync/`: 23 implementation modules + 1 `__init__.py` master re-export. The 23 implementation modules are listed individually in Task C-1 below. The discrepancy between spec text and on-disk reality is documented in the PR-D CHANGELOG.

---

## PR-A — requirements.txt + auto-install (zero plugin code touched)

**Effort:** ~1 day. **Branch:** `plugin/pr-a-bridge-install`. **Rollback:** revert PR — bridge stays inert if requirements line is removed.

### Task A-1 — Append bridge to requirements.txt

- [ ] **Step 1** — Open `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/requirements.txt` and append the new dependency immediately after the `s3dgraphy>=1.5.0` line (block "Graph"):

  ```diff
  @@
   s3dgraphy>=1.5.0
  +
  +# Bridge — extracts the s3dgraphy sync layer (yEd ↔ DB ↔ GraphML round-trip)
  +# into a vendored shared package consumed by both this plugin and
  +# pyarchinit-mini-desk. See docs/superpowers/specs/2026-05-20-s3dgraphy-bridge-design.md.
  +# v1.0.0 ships MVP-roundtrip + AC-2 byte-identical guarantee for the 16
  +# bridge modules (see spec §"MVP Scope"). yE-F multi-folder paradata,
  +# LocationNodeGroup, and PG-Compat land in successive minor bumps
  +# (v1.1, v1.2, v1.3). Pinned `==1.0.0` while plugin v5.9.1 shim-migrates;
  +# floor loosens to `>=1.0,<2.0` after plugin v5.9.2 stabilises.
  +pyarchinit-s3dgraphy-bridge==1.0.0
  ```

- [ ] **Step 2** — Verify the diff with `git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" diff requirements.txt`.

  Expected: 11 added lines, 0 deleted.

### Task A-2 — Extend modules_installer.py to install the bridge into ext_libs/

- [ ] **Step 1** — Open `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/scripts/modules_installer.py`. The existing main loop at line 149 already iterates `packages` (parsed from `requirements.txt` at line 117) and calls `pip install --upgrade <p> --user`. The bridge will be picked up automatically by that loop **but** the plugin convention for s3dgraphy is to install into `ext_libs/` rather than `--user`, so add a dedicated helper before the main loop and special-case the bridge.

  Add the following helper function after `_extract_pkg_name()` (currently ends at line 103, before `packages = sys.argv[1].split(',')`):

  ```python
  # Bridge install target: vendored into plugin's ext_libs/, NOT --user.
  # This matches the s3dgraphy install convention so QGIS picks the bridge
  # up via the plugin's PYTHONPATH bootstrap (see __init__.py) without
  # depending on the user's site-packages.
  _BRIDGE_PKG_NAME = "pyarchinit-s3dgraphy-bridge"


  def _install_into_ext_libs(requirement: str, python_cmd: str) -> int:
      """Install a single requirement line into `ext_libs/` via
      `pip install --target=<ext_libs>`. Returns the pip exit code."""
      if not os.path.isdir(_EXT_LIBS_DIR):
          os.makedirs(_EXT_LIBS_DIR, exist_ok=True)
          print(f"[modules_installer] created {_EXT_LIBS_DIR}")
      print(f"[modules_installer] installing {requirement} -> ext_libs/")
      return subprocess.call(
          [python_cmd, "-m", "pip", "install", "--upgrade",
           "--target", _EXT_LIBS_DIR, requirement],
          shell=False,
      )
  ```

- [ ] **Step 2** — Edit the main loop at line 149 to route the bridge to `_install_into_ext_libs()` instead of the default `--user` install. Replace the existing `for p in packages:` block with:

  ```python
  for p in packages:
      # Pre-step: clean stale dist-info / __pycache__ in ext_libs/ for
      # this package so importlib.metadata can resolve the freshly
      # installed version unambiguously (5.8.1-alpha s3dgraphy-bump fix).
      name = _extract_pkg_name(p)
      if name:
          _cleanup_stale_dists(name)

      # Bridge goes into ext_libs/ (alongside s3dgraphy); everything else
      # goes to --user as before.
      canon = (name or "").lower().replace("_", "-")
      if canon == _BRIDGE_PKG_NAME:
          _install_into_ext_libs(p, cmd)
          continue

      # Use --upgrade to ensure exact versions (==) are installed even if
      # older version exists.
      subprocess.call(['python', '-m', 'pip', 'install',
                       '--upgrade', p, '--user'], shell=True)
  ```

- [ ] **Step 3** — Verify the diff is syntactically valid by running the installer locally with the new requirements line. From the plugin root:

  ```bash
  cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
  python3 scripts/modules_installer.py
  ```

  Expected: among the install log lines, `[modules_installer] installing pyarchinit-s3dgraphy-bridge==1.0.0 -> ext_libs/` appears, followed by pip's standard `Successfully installed pyarchinit-s3dgraphy-bridge-1.0.0`.

- [ ] **Step 4** — Verify the bridge is now on disk under `ext_libs/`:

  ```bash
  ls "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/ext_libs/" | grep -i bridge
  ```

  Expected:
  ```
  pyarchinit_s3dgraphy_bridge
  pyarchinit_s3dgraphy_bridge-1.0.0.dist-info
  ```

### Task A-3 — QGIS smoke test (manual)

- [ ] **Step 1** — Restart QGIS (full quit + relaunch, not just plugin reload). The plugin's `__init__.py` adds `ext_libs/` to `sys.path` during bootstrap; verify the path is present by opening the QGIS Python console and running:

  ```python
  import sys
  any("ext_libs" in p for p in sys.path)
  ```

  Expected: `True`.

- [ ] **Step 2** — In the QGIS Python console, run:

  ```python
  import pyarchinit_s3dgraphy_bridge
  print(pyarchinit_s3dgraphy_bridge.__version__)
  ```

  Expected: `1.0.0` (no `ImportError`, no `ModuleNotFoundError`).

- [ ] **Step 3** — Verify the bridge does NOT yet collide with the inline `modules/s3dgraphy/sync/*` (PR-C has not landed):

  ```python
  from pyarchinit.modules.s3dgraphy.sync.graph_projector import GraphProjector as PluginGP
  from pyarchinit_s3dgraphy_bridge.graph_projector import GraphProjector as BridgeGP
  print(PluginGP is BridgeGP)
  ```

  Expected: `False` (they are two distinct class objects loaded from different files — this is the inert-coexistence state PR-A guarantees).

### Task A-4 — Commit PR-A

- [ ] **Step 1** — Stage the two touched files only:

  ```bash
  cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
  git add requirements.txt scripts/modules_installer.py
  git status
  ```

  Expected: 2 files staged, nothing else.

- [ ] **Step 2** — Commit with message:

  ```bash
  git commit -m "$(cat <<'EOF'
  PR-A: install pyarchinit-s3dgraphy-bridge==1.0.0 into ext_libs/

  Adds the bridge to requirements.txt and extends scripts/modules_installer.py
  to route the bridge to ext_libs/ (via pip install --target) instead of
  --user. Bridge is installed but inert — no plugin call site touched.

  Per spec docs/superpowers/specs/2026-05-20-s3dgraphy-bridge-design.md
  §"Plugin migration plan (Q6=C)" PR-A.
  EOF
  )"
  ```

- [ ] **Step 3** — Push the branch and open a PR titled `PR-A: bridge install (inert)` against the `Stratigraph_00001` branch.

---

## PR-B — QGIS adapters implementing the 5 Protocols

**Effort:** ~3 days. **Branch:** `plugin/pr-b-bridge-adapters`. **Rollback:** revert PR — adapters are isolated under `modules/s3dgraphy/bridge_adapter/`, no other code imports them yet.

New directory: `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/s3dgraphy/bridge_adapter/`

The 5 adapter classes wrap pre-existing plugin facilities:

| Adapter | Wraps | Plugin source |
|---|---|---|
| `QgisDbSession` | `_db_handle.DbHandle` | `modules/s3dgraphy/sync/_db_handle.py` (still inline until PR-C) |
| `QgisWorkspace` | plugin install dir + tmp via `tempfile.gettempdir()` | `os.path.dirname(__file__)` chain |
| `QSettingsProxy` | `qgis.PyQt.QtCore.QSettings("pyArchInit")` | existing convention |
| `QtFileProvider` | `QFileDialog.getOpenFileName` + path-based `read_bytes` | new |
| `QgsLogger` | `qgis.core.QgsMessageLog.logMessage` | existing convention |

### Task B-1 — Create the adapter package skeleton

- [ ] **Step 1** — Create directory:

  ```bash
  mkdir -p "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/s3dgraphy/bridge_adapter"
  ```

  Expected: directory exists, empty.

- [ ] **Step 2** — Write `modules/s3dgraphy/bridge_adapter/__init__.py`:

  ```python
  """QGIS-side adapters implementing the pyarchinit-s3dgraphy-bridge Protocols.

  Five classes mapped 1:1 onto the bridge's typing.Protocol contracts
  (see pyarchinit_s3dgraphy_bridge.protocols). Each wraps an existing
  QGIS/Qt facility (QSettings, QFileDialog, QgsMessageLog) or a plugin
  facility (DbHandle, plugin dir) so the bridge's pure-logic code can be
  invoked from the plugin without leaking Qt/QGIS imports into the bridge.

  Per spec docs/superpowers/specs/2026-05-20-s3dgraphy-bridge-design.md
  §"Architecture" and §"Plugin migration plan (Q6=C)" PR-B.
  """
  from __future__ import annotations

  from .db_session import QgisDbSession
  from .workspace import QgisWorkspace
  from .settings import QSettingsProxy
  from .file_provider import QtFileProvider
  from .logger import QgsLogger

  __all__ = [
      "QgisDbSession",
      "QgisWorkspace",
      "QSettingsProxy",
      "QtFileProvider",
      "QgsLogger",
  ]
  ```

### Task B-2 — `db_session.py` — QgisDbSession (TDD)

- [ ] **Step 1** — Write the failing test first at `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/tests/bridge_adapter/test_db_session.py`:

  ```python
  """Unit tests for QgisDbSession (wraps pyarchinit DbHandle)."""
  from __future__ import annotations

  from unittest.mock import MagicMock

  import pytest

  from pyarchinit.modules.s3dgraphy.bridge_adapter import QgisDbSession


  @pytest.fixture
  def fake_handle():
      """Mock of pyarchinit.modules.s3dgraphy.sync._db_handle.DbHandle."""
      h = MagicMock()
      h.is_postgres = False
      h.sqlite_path = "/tmp/test.sqlite"
      cursor = MagicMock()
      cursor.fetchall.return_value = [(1, "alpha"), (2, "beta")]
      h.cursor.return_value.__enter__.return_value = cursor
      return h


  def test_execute_returns_cursor(fake_handle):
      sess = QgisDbSession(fake_handle)
      cur = sess.execute("SELECT id, name FROM us_table", {})
      assert cur.fetchall() == [(1, "alpha"), (2, "beta")]


  def test_commit_delegates_to_handle(fake_handle):
      sess = QgisDbSession(fake_handle)
      sess.commit()
      fake_handle.commit.assert_called_once_with()


  def test_is_postgres_attribute_mirrors_handle(fake_handle):
      sess_sqlite = QgisDbSession(fake_handle)
      assert sess_sqlite.is_postgres is False

      fake_handle.is_postgres = True
      sess_pg = QgisDbSession(fake_handle)
      assert sess_pg.is_postgres is True


  def test_execute_passes_params_dict(fake_handle):
      sess = QgisDbSession(fake_handle)
      sess.execute("SELECT * FROM us_table WHERE id=:id", {"id": 42})
      # The DbHandle.cursor() context manager's execute is what carries
      # the SQL+params through to the underlying driver.
      cm = fake_handle.cursor.return_value.__enter__.return_value
      cm.execute.assert_called_once_with(
          "SELECT * FROM us_table WHERE id=:id", {"id": 42}
      )
  ```

- [ ] **Step 2** — Run the test, watch it fail (module not found):

  ```bash
  cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
  pytest tests/bridge_adapter/test_db_session.py -v
  ```

  Expected: `ModuleNotFoundError: No module named '...bridge_adapter.db_session'`.

- [ ] **Step 3** — Write `modules/s3dgraphy/bridge_adapter/db_session.py`:

  ```python
  """QgisDbSession — wraps the pyarchinit DbHandle so the bridge's
  pure-Python code (which expects a `DbSession` Protocol) can issue
  SQL against either SQLite or PostgreSQL backends transparently.

  Bridge contract (pyarchinit_s3dgraphy_bridge.protocols.DbSession):
      def execute(self, sql: str, params: dict | None = None) -> Cursor: ...
      def commit(self) -> None: ...
      is_postgres: bool
  """
  from __future__ import annotations

  from typing import Any


  class QgisDbSession:
      """Adapter from pyarchinit.modules.s3dgraphy.sync._db_handle.DbHandle
      to pyarchinit_s3dgraphy_bridge.protocols.DbSession.
      """

      def __init__(self, handle: Any) -> None:
          self._handle = handle
          # Mirror the discriminator so the bridge can branch on it without
          # touching the handle directly.
          self.is_postgres: bool = bool(getattr(handle, "is_postgres", False))

      def execute(self, sql: str, params: dict | None = None):
          """Issue a single SQL statement and return the resulting cursor.

          The bridge uses the cursor's `fetchall()` / `fetchone()` directly;
          it never calls `close()` on it (the underlying DbHandle manages
          cursor lifecycle via its context manager)."""
          with self._handle.cursor() as cur:
              cur.execute(sql, params or {})
              return cur

      def commit(self) -> None:
          """Commit the open transaction on the underlying handle."""
          self._handle.commit()
  ```

- [ ] **Step 4** — Rerun the test:

  ```bash
  pytest tests/bridge_adapter/test_db_session.py -v
  ```

  Expected: 4 passed.

### Task B-3 — `workspace.py` — QgisWorkspace (TDD)

- [ ] **Step 1** — Write the failing test at `tests/bridge_adapter/test_workspace.py`:

  ```python
  """Unit tests for QgisWorkspace."""
  from __future__ import annotations

  import tempfile
  from pathlib import Path

  import pytest

  from pyarchinit.modules.s3dgraphy.bridge_adapter import QgisWorkspace


  def test_root_is_pathlib_path():
      ws = QgisWorkspace(root="/tmp/pyarchinit_workspace")
      assert isinstance(ws.root, Path)
      assert str(ws.root) == "/tmp/pyarchinit_workspace"


  def test_tmp_returns_existing_directory():
      ws = QgisWorkspace(root="/tmp/pyarchinit_workspace")
      t = ws.tmp()
      assert isinstance(t, Path)
      assert t.exists()
      assert t.is_dir()


  def test_tmp_is_writable(tmp_path):
      ws = QgisWorkspace(root=str(tmp_path))
      t = ws.tmp()
      probe = t / "probe.txt"
      probe.write_text("ok")
      assert probe.read_text() == "ok"
  ```

- [ ] **Step 2** — Run the test, expect failure (module missing).

- [ ] **Step 3** — Write `modules/s3dgraphy/bridge_adapter/workspace.py`:

  ```python
  """QgisWorkspace — file-system roots used by the bridge for
  intermediate files (GraphML drafts, paradata SVG cache, etc.).

  Bridge contract (pyarchinit_s3dgraphy_bridge.protocols.Workspace):
      root: Path
      def tmp(self) -> Path: ...
  """
  from __future__ import annotations

  import os
  import tempfile
  from pathlib import Path


  class QgisWorkspace:
      """Adapter exposing two file-system roots to the bridge:
      `root` (persistent, normally the plugin install dir) and `tmp()`
      (volatile, normally the OS tempdir or a QSettings-overridden path).
      """

      def __init__(self, root: str | os.PathLike[str]) -> None:
          self.root: Path = Path(root)

      def tmp(self) -> Path:
          """Return a writable, existing temp directory dedicated to the
          bridge. Created on demand under the OS temp root."""
          t = Path(tempfile.gettempdir()) / "pyarchinit_bridge"
          t.mkdir(parents=True, exist_ok=True)
          return t
  ```

- [ ] **Step 4** — Rerun the test. Expected: 3 passed.

### Task B-4 — `settings.py` — QSettingsProxy (TDD)

- [ ] **Step 1** — Write the failing test at `tests/bridge_adapter/test_settings.py`:

  ```python
  """Unit tests for QSettingsProxy — uses unittest.mock to stub QSettings
  so the test runs outside QGIS."""
  from __future__ import annotations

  from unittest.mock import MagicMock, patch

  import pytest

  from pyarchinit.modules.s3dgraphy.bridge_adapter import QSettingsProxy


  def test_get_returns_value_when_key_exists():
      fake = MagicMock()
      fake.value.return_value = "production"
      with patch(
          "pyarchinit.modules.s3dgraphy.bridge_adapter.settings.QSettings",
          return_value=fake,
      ):
          proxy = QSettingsProxy(organization="pyArchInit")
          assert proxy.get("bridge/profile") == "production"
          fake.value.assert_called_once_with("bridge/profile", None)


  def test_get_returns_default_when_key_missing():
      fake = MagicMock()
      fake.value.return_value = None
      with patch(
          "pyarchinit.modules.s3dgraphy.bridge_adapter.settings.QSettings",
          return_value=fake,
      ):
          proxy = QSettingsProxy(organization="pyArchInit")
          assert proxy.get("bridge/missing", default="fallback") == "fallback"


  def test_organization_is_passed_to_qsettings():
      fake = MagicMock()
      with patch(
          "pyarchinit.modules.s3dgraphy.bridge_adapter.settings.QSettings",
          return_value=fake,
      ) as qs_ctor:
          QSettingsProxy(organization="customOrg")
          qs_ctor.assert_called_once_with("customOrg")
  ```

- [ ] **Step 2** — Run the test, expect module-not-found failure.

- [ ] **Step 3** — Write `modules/s3dgraphy/bridge_adapter/settings.py`:

  ```python
  """QSettingsProxy — read-only adapter exposing QSettings via the
  bridge's `Settings` Protocol.

  Bridge contract (pyarchinit_s3dgraphy_bridge.protocols.Settings):
      def get(self, key: str, default: Any = None) -> Any: ...
  """
  from __future__ import annotations

  from typing import Any

  from qgis.PyQt.QtCore import QSettings  # noqa: F401 (re-exported for tests)


  class QSettingsProxy:
      """Read-only wrapper over QSettings; the bridge uses it only for
      configuration look-ups, never for writes (writes go through the
      plugin's own pyarchinitConfigDialog)."""

      def __init__(self, organization: str = "pyArchInit") -> None:
          self._qs = QSettings(organization)

      def get(self, key: str, default: Any = None) -> Any:
          val = self._qs.value(key, default)
          # QSettings returns the raw default unchanged if the key is
          # absent; some platforms return None for missing keys even when
          # default is passed (older PyQt5). Normalise here.
          if val is None:
              return default
          return val
  ```

- [ ] **Step 4** — Rerun the test. Expected: 3 passed.

### Task B-5 — `file_provider.py` — QtFileProvider (TDD)

- [ ] **Step 1** — Write the failing test at `tests/bridge_adapter/test_file_provider.py`:

  ```python
  """Unit tests for QtFileProvider — path-based read_bytes plus optional
  QFileDialog-driven open."""
  from __future__ import annotations

  from pathlib import Path
  from unittest.mock import patch

  import pytest

  from pyarchinit.modules.s3dgraphy.bridge_adapter import QtFileProvider


  def test_read_bytes_local_path(tmp_path):
      f = tmp_path / "graph.graphml"
      payload = b"<graphml/>"
      f.write_bytes(payload)
      provider = QtFileProvider()
      assert provider.read_bytes(str(f)) == payload


  def test_read_bytes_missing_raises_filenotfound(tmp_path):
      provider = QtFileProvider()
      with pytest.raises(FileNotFoundError):
          provider.read_bytes(str(tmp_path / "does_not_exist.graphml"))


  def test_open_dialog_returns_selected_path():
      """QFileDialog is patched; we only verify the contract that the
      provider returns the first element of the tuple."""
      with patch(
          "pyarchinit.modules.s3dgraphy.bridge_adapter.file_provider"
          ".QFileDialog.getOpenFileName",
          return_value=("/tmp/picked.graphml", "GraphML (*.graphml)"),
      ):
          provider = QtFileProvider()
          assert provider.open_dialog(
              caption="Pick a graph", filters="GraphML (*.graphml)"
          ) == "/tmp/picked.graphml"


  def test_open_dialog_returns_none_when_cancelled():
      with patch(
          "pyarchinit.modules.s3dgraphy.bridge_adapter.file_provider"
          ".QFileDialog.getOpenFileName",
          return_value=("", ""),
      ):
          provider = QtFileProvider()
          assert provider.open_dialog(
              caption="Pick a graph", filters="GraphML (*.graphml)"
          ) is None
  ```

- [ ] **Step 2** — Run the test, expect module-not-found failure.

- [ ] **Step 3** — Write `modules/s3dgraphy/bridge_adapter/file_provider.py`:

  ```python
  """QtFileProvider — file-system access for the bridge.

  Bridge contract (pyarchinit_s3dgraphy_bridge.protocols.FileProvider):
      def read_bytes(self, ref: str) -> bytes: ...

  In the plugin, `ref` is always a local filesystem path. The mini-desk
  adapter (different class, same Protocol) accepts upload-IDs and resolves
  them through its UploadModel; the bridge never sees the difference.

  This class also exposes `open_dialog()` (a non-Protocol convenience) so
  plugin callers can re-use the same instance for QFileDialog-driven
  selection without instantiating a second helper.
  """
  from __future__ import annotations

  from pathlib import Path

  from qgis.PyQt.QtWidgets import QFileDialog  # noqa: F401


  class QtFileProvider:
      """File access for the bridge plus QFileDialog convenience."""

      def read_bytes(self, ref: str) -> bytes:
          """Read the file at `ref` (local filesystem path) and return
          its bytes. Raises FileNotFoundError if `ref` does not exist."""
          p = Path(ref)
          if not p.exists():
              raise FileNotFoundError(ref)
          return p.read_bytes()

      def open_dialog(
          self,
          caption: str = "",
          directory: str = "",
          filters: str = "",
          parent=None,
      ) -> str | None:
          """Show a QFileDialog open dialog. Returns the selected path
          or None if the user cancelled."""
          path, _ = QFileDialog.getOpenFileName(
              parent, caption, directory, filters
          )
          return path or None
  ```

- [ ] **Step 4** — Rerun the test. Expected: 4 passed.

### Task B-6 — `logger.py` — QgsLogger (TDD)

- [ ] **Step 1** — Write the failing test at `tests/bridge_adapter/test_logger.py`:

  ```python
  """Unit tests for QgsLogger — adapter over QgsMessageLog."""
  from __future__ import annotations

  from unittest.mock import patch

  import pytest

  from pyarchinit.modules.s3dgraphy.bridge_adapter import QgsLogger


  def test_info_calls_qgs_message_log_with_info_level():
      with patch(
          "pyarchinit.modules.s3dgraphy.bridge_adapter.logger"
          ".QgsMessageLog.logMessage"
      ) as log:
          QgsLogger(tag="bridge").info("hello")
          log.assert_called_once()
          args, _ = log.call_args
          assert args[0] == "hello"
          assert args[1] == "bridge"
          # Qgis.Info value is 0 in the QGIS public API.
          assert args[2] == 0


  def test_warn_calls_qgs_message_log_with_warning_level():
      with patch(
          "pyarchinit.modules.s3dgraphy.bridge_adapter.logger"
          ".QgsMessageLog.logMessage"
      ) as log:
          QgsLogger(tag="bridge").warn("watch out")
          log.assert_called_once()
          args, _ = log.call_args
          # Qgis.Warning value is 1.
          assert args[2] == 1


  def test_error_includes_exception_repr_when_present():
      with patch(
          "pyarchinit.modules.s3dgraphy.bridge_adapter.logger"
          ".QgsMessageLog.logMessage"
      ) as log:
          QgsLogger(tag="bridge").error("boom", exc=ValueError("nope"))
          msg = log.call_args[0][0]
          assert "boom" in msg
          assert "ValueError" in msg
          assert "nope" in msg
          # Qgis.Critical value is 2.
          assert log.call_args[0][2] == 2


  def test_error_without_exception_logs_plain_message():
      with patch(
          "pyarchinit.modules.s3dgraphy.bridge_adapter.logger"
          ".QgsMessageLog.logMessage"
      ) as log:
          QgsLogger(tag="bridge").error("no exception", exc=None)
          assert log.call_args[0][0] == "no exception"
  ```

- [ ] **Step 2** — Run the test, expect module-not-found failure.

- [ ] **Step 3** — Write `modules/s3dgraphy/bridge_adapter/logger.py`:

  ```python
  """QgsLogger — adapter routing the bridge's structured log calls to
  QgsMessageLog under a dedicated tag.

  Bridge contract (pyarchinit_s3dgraphy_bridge.protocols.Logger):
      def info(self, msg: str) -> None: ...
      def warn(self, msg: str) -> None: ...
      def error(self, msg: str, exc: Exception | None = None) -> None: ...
  """
  from __future__ import annotations

  from qgis.core import Qgis, QgsMessageLog  # noqa: F401


  class QgsLogger:
      """Route bridge log messages to QgsMessageLog under a tag."""

      def __init__(self, tag: str = "s3dgraphy-bridge") -> None:
          self._tag = tag

      def info(self, msg: str) -> None:
          QgsMessageLog.logMessage(msg, self._tag, Qgis.Info)

      def warn(self, msg: str) -> None:
          QgsMessageLog.logMessage(msg, self._tag, Qgis.Warning)

      def error(self, msg: str, exc: Exception | None = None) -> None:
          if exc is not None:
              msg = f"{msg} :: {type(exc).__name__}: {exc}"
          QgsMessageLog.logMessage(msg, self._tag, Qgis.Critical)
  ```

- [ ] **Step 4** — Rerun the test. Expected: 4 passed.

### Task B-7 — Adapter package smoke test + commit

- [ ] **Step 1** — Run the full adapter suite:

  ```bash
  cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
  pytest tests/bridge_adapter/ -v
  ```

  Expected: 4 + 3 + 3 + 4 + 4 = **18 passed** (db_session 4, workspace 3, settings 3, file_provider 4, logger 4).

- [ ] **Step 2** — Stage the new package + tests:

  ```bash
  git add modules/s3dgraphy/bridge_adapter/ tests/bridge_adapter/
  git status
  ```

  Expected: 6 new files staged (5 adapter + 1 `__init__`) + 5 test files = 11 files.

- [ ] **Step 3** — Commit:

  ```bash
  git commit -m "$(cat <<'EOF'
  PR-B: add 5 QGIS-side adapters for pyarchinit-s3dgraphy-bridge

  Adds modules/s3dgraphy/bridge_adapter/ with QgisDbSession,
  QgisWorkspace, QSettingsProxy, QtFileProvider, QgsLogger — 1:1
  implementations of the bridge's typing.Protocol set (DbSession,
  Workspace, Settings, FileProvider, Logger).

  18 unit tests (pytest + unittest.mock for QGIS/Qt facilities so the
  suite runs outside QGIS).

  Adapters are isolated: no other plugin code imports them yet. PR-C
  will wire them through the shim re-export.

  Per spec docs/superpowers/specs/2026-05-20-s3dgraphy-bridge-design.md
  §"Plugin migration plan (Q6=C)" PR-B.
  EOF
  )"
  ```

---

## PR-C — Shim re-export (atomic conversion of inline sync modules)

**Effort:** ~1 day. **Branch:** `plugin/pr-c-shim-reexport`. **Rollback:** revert PR — the inline files come back unchanged (use `git revert` to keep history straight, not `git reset`).

**Critical:** PR-C is atomic — all shim conversions land in a single commit. Partial conversion (some files shim'd, others inline) creates two competing implementations of the same module under different import paths, which is the worst possible state.

### Task C-1 — Convert the 23 implementation modules to 1-line shims

The 23 implementation files under `modules/s3dgraphy/sync/` (`__init__.py` is handled separately in Task C-2):

| # | File | New shim content (3 lines + import) |
|---|---|---|
| 1 | `_db_handle.py` | `from pyarchinit_s3dgraphy_bridge._db_handle import *  # noqa: F401, F403` |
| 2 | `_legacy_paradata_svgs.py` | `from pyarchinit_s3dgraphy_bridge._legacy_paradata_svgs import *  # noqa: F401, F403` |
| 3 | `_workspace.py` | `from pyarchinit_s3dgraphy_bridge._workspace import *  # noqa: F401, F403` |
| 4 | `conflict_resolver.py` | `from pyarchinit_s3dgraphy_bridge.conflict_resolver import *  # noqa: F401, F403` |
| 5 | `edge_registry.py` | `from pyarchinit_s3dgraphy_bridge.edge_registry import *  # noqa: F401, F403` |
| 6 | `graph_ingestor.py` | `from pyarchinit_s3dgraphy_bridge.graph_ingestor import *  # noqa: F401, F403` |
| 7 | `graph_projector.py` | `from pyarchinit_s3dgraphy_bridge.graph_projector import *  # noqa: F401, F403` |
| 8 | `graphml_writer.py` | `from pyarchinit_s3dgraphy_bridge.graphml_writer import *  # noqa: F401, F403` |
| 9 | `group_projector.py` | `from pyarchinit_s3dgraphy_bridge.group_projector import *  # noqa: F401, F403` |
| 10 | `group_store.py` | `from pyarchinit_s3dgraphy_bridge.group_store import *  # noqa: F401, F403` |
| 11 | `ingest_result.py` | `from pyarchinit_s3dgraphy_bridge.ingest_result import *  # noqa: F401, F403` |
| 12 | `paradata_store.py` | `from pyarchinit_s3dgraphy_bridge.paradata_store import *  # noqa: F401, F403` |
| 13 | `pyarchinit_pg_importer.py` | `from pyarchinit_s3dgraphy_bridge.pyarchinit_pg_importer import *  # noqa: F401, F403` |
| 14 | `uuid7.py` | `from pyarchinit_s3dgraphy_bridge.uuid7 import *  # noqa: F401, F403` |
| 15 | `vocab_provider.py` | `from pyarchinit_s3dgraphy_bridge.vocab_provider import *  # noqa: F401, F403` |
| 16 | `vocab_provider_core.py` | `from pyarchinit_s3dgraphy_bridge.vocab_provider_core import *  # noqa: F401, F403` |
| 17 | `vocab_types.py` | `from pyarchinit_s3dgraphy_bridge.vocab_types import *  # noqa: F401, F403` |
| 18 | `yed_classifier.py` | `from pyarchinit_s3dgraphy_bridge.yed_classifier import *  # noqa: F401, F403` |
| 19 | `yed_detector.py` | `from pyarchinit_s3dgraphy_bridge.yed_detector import *  # noqa: F401, F403` |
| 20 | `yed_group_walker.py` | `from pyarchinit_s3dgraphy_bridge.yed_group_walker import *  # noqa: F401, F403` |
| 21 | `yed_import_pipeline.py` | `from pyarchinit_s3dgraphy_bridge.yed_import_pipeline import *  # noqa: F401, F403` |
| 22 | `yed_rapporti_policy.py` | `from pyarchinit_s3dgraphy_bridge.yed_rapporti_policy import *  # noqa: F401, F403` |
| 23 | `yed_table_parser.py` | `from pyarchinit_s3dgraphy_bridge.yed_table_parser import *  # noqa: F401, F403` |

Each file's full content is exactly 4 lines:

```python
# Shim: implementation lives in pyarchinit-s3dgraphy-bridge.
# Deletion planned in plugin v6.0.0 (see spec 2026-05-20).
from pyarchinit_s3dgraphy_bridge.<modulename> import *  # noqa: F401, F403
```

- [ ] **Step 1** — Save the conversion script as `/tmp/convert_to_shims.sh`:

  ```bash
  #!/bin/bash
  set -euo pipefail

  PLUGIN_ROOT="/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
  SYNC_DIR="$PLUGIN_ROOT/modules/s3dgraphy/sync"

  MODULES=(
    "_db_handle"
    "_legacy_paradata_svgs"
    "_workspace"
    "conflict_resolver"
    "edge_registry"
    "graph_ingestor"
    "graph_projector"
    "graphml_writer"
    "group_projector"
    "group_store"
    "ingest_result"
    "paradata_store"
    "pyarchinit_pg_importer"
    "uuid7"
    "vocab_provider"
    "vocab_provider_core"
    "vocab_types"
    "yed_classifier"
    "yed_detector"
    "yed_group_walker"
    "yed_import_pipeline"
    "yed_rapporti_policy"
    "yed_table_parser"
  )

  for m in "${MODULES[@]}"; do
    f="$SYNC_DIR/$m.py"
    if [[ ! -f "$f" ]]; then
      echo "MISSING: $f" >&2
      exit 1
    fi
    cat > "$f" <<EOF
  # Shim: implementation lives in pyarchinit-s3dgraphy-bridge.
  # Deletion planned in plugin v6.0.0 (see spec 2026-05-20).
  from pyarchinit_s3dgraphy_bridge.$m import *  # noqa: F401, F403
  EOF
    echo "shim'd: $m"
  done

  echo
  echo "Done — 23 files converted to shims."
  ```

- [ ] **Step 2** — Make executable and run:

  ```bash
  chmod +x /tmp/convert_to_shims.sh
  /tmp/convert_to_shims.sh
  ```

  Expected: 23 `shim'd: <name>` log lines followed by `Done — 23 files converted to shims.`

- [ ] **Step 3** — Verify every file is now exactly 3 lines:

  ```bash
  cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/s3dgraphy/sync"
  for f in _db_handle.py _legacy_paradata_svgs.py _workspace.py conflict_resolver.py edge_registry.py graph_ingestor.py graph_projector.py graphml_writer.py group_projector.py group_store.py ingest_result.py paradata_store.py pyarchinit_pg_importer.py uuid7.py vocab_provider.py vocab_provider_core.py vocab_types.py yed_classifier.py yed_detector.py yed_group_walker.py yed_import_pipeline.py yed_rapporti_policy.py yed_table_parser.py; do
    lines=$(wc -l < "$f")
    [[ "$lines" -le 3 ]] || echo "TOO LONG: $f has $lines lines"
  done
  echo "all-shims-check done"
  ```

  Expected: no `TOO LONG` lines, followed by `all-shims-check done`.

### Task C-2 — Convert `__init__.py` to master re-export

- [ ] **Step 1** — Overwrite `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/s3dgraphy/sync/__init__.py` with:

  ```python
  """Master shim — re-exports the bridge's public API under the legacy
  pyarchinit.modules.s3dgraphy.sync.* path so ~80 existing call sites
  in the plugin keep working unchanged.

  Real implementation lives in `pyarchinit-s3dgraphy-bridge` (PyPI),
  installed by scripts/modules_installer.py into ext_libs/.

  Plugin v6.0.0 (Q4 2026) will delete this shim plus the 23 sibling
  shims, rewrite call sites to import from pyarchinit_s3dgraphy_bridge.*
  directly, and major-bump to signal the internal API break.

  Per spec docs/superpowers/specs/2026-05-20-s3dgraphy-bridge-design.md
  §"Plugin migration plan (Q6=C)" PR-C.
  """
  from __future__ import annotations

  # Master re-export: mirror the bridge's public API at the legacy path.
  from pyarchinit_s3dgraphy_bridge import (  # noqa: F401
      VocabProviderCore,
      EdgeType,
      Family,
      ParadataType,
      UnitType,
      VisualRule,
      VocabularyVersion,
      DbHandle,
      DbHandleError,
      PgConnectionError,
      UnsupportedBackendError,
  )

  __all__ = [
      "VocabProviderCore",
      "EdgeType",
      "Family",
      "ParadataType",
      "UnitType",
      "VisualRule",
      "VocabularyVersion",
      "DbHandle",
      "DbHandleError",
      "PgConnectionError",
      "UnsupportedBackendError",
  ]


  def get_vocab_provider():
      """Return a process-wide Qt-aware VocabProvider singleton.

      Kept at the legacy import path so callers using
      `from pyarchinit.modules.s3dgraphy.sync import get_vocab_provider`
      continue to work unchanged. Implementation is now in the bridge.
      """
      from pyarchinit_s3dgraphy_bridge.vocab_provider import get_default_provider
      return get_default_provider()
  ```

### Task C-3 — Run the 351 plugin sync tests against the installed bridge

- [ ] **Step 1** — Confirm the bridge is installed (carried over from PR-A):

  ```bash
  ls "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/ext_libs/" | grep -i bridge
  ```

  Expected: `pyarchinit_s3dgraphy_bridge` directory + matching `.dist-info`.

- [ ] **Step 2** — Run the plugin sync test suite (the 351 tests already in `tests/sync/`):

  ```bash
  cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
  pytest tests/sync/ -v --tb=short
  ```

  Expected: 351 passed (or +/- the in-flight skip count from `Stratigraph_00001` HEAD — see spec AC-INT-5).

- [ ] **Step 3** — If any test fails, triage:
  - **Bridge missing module** → file an issue against the bridge repo with the missing symbol; add a regression test to the bridge's AC-2 suite.
  - **Bridge API drift from plugin** → DO NOT patch the shim. File a bridge issue and pin to a prior bridge patch release while it's fixed.
  - **Pre-existing skip** (DB unreachable, etc.) → out of scope for PR-C; record it in the PR description.

  Record the verbatim test count in the commit message and the CHANGELOG entry that PR-D will write.

### Task C-4 — Add the "no edits inside sync/" guard rail

This is the load-bearing mitigation from the spec's Risks table: *"Plugin v5.9.1+ forbids new edits inside `modules/s3dgraphy/sync/*` — CI fails if PR touches them."*

- [ ] **Step 1** — Create `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/.pre-commit-config.yaml` if it does not exist, or append the local hook to the existing file. Full file (if creating fresh):

  ```yaml
  # See https://pre-commit.com for usage.
  repos:
    - repo: local
      hooks:
        - id: forbid-sync-edits
          name: "Forbid edits inside modules/s3dgraphy/sync/ (use pyarchinit-s3dgraphy-bridge)"
          entry: scripts/check_no_sync_edits.sh
          language: script
          pass_filenames: true
          files: ^modules/s3dgraphy/sync/.*\.py$
  ```

- [ ] **Step 2** — Create the gate script at `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/scripts/check_no_sync_edits.sh`:

  ```bash
  #!/bin/bash
  # Refuse any change inside modules/s3dgraphy/sync/*.py
  # (those files are shims to pyarchinit-s3dgraphy-bridge; fixes go to the
  # bridge repo, not here). Exits 1 if any matching path is staged.
  #
  # Escape valve (documented in CONTRIBUTING.md): set
  # ALLOW_SYNC_EDIT=1 in the environment when cherry-picking a hotfix
  # from a bridge PR. The follow-up PR back to the bridge must be opened
  # in the same workday — see spec §"Risks" mitigation row 2.

  set -euo pipefail

  if [[ "${ALLOW_SYNC_EDIT:-0}" == "1" ]]; then
    echo "[forbid-sync-edits] override active (ALLOW_SYNC_EDIT=1)"
    exit 0
  fi

  if [[ $# -eq 0 ]]; then
    exit 0
  fi

  echo "[forbid-sync-edits] BLOCKED — these files are shims to" >&2
  echo "  pyarchinit-s3dgraphy-bridge. Apply the fix in that repo:" >&2
  echo "    https://github.com/pyarchinit/pyarchinit-s3dgraphy-bridge" >&2
  echo "  then bump the version pin in requirements.txt." >&2
  echo "Files refused:" >&2
  for f in "$@"; do
    echo "  $f" >&2
  done
  echo "" >&2
  echo "If this really is a hotfix, set ALLOW_SYNC_EDIT=1 and open a" >&2
  echo "follow-up PR to the bridge the same day." >&2
  exit 1
  ```

  Make it executable:

  ```bash
  chmod +x "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/scripts/check_no_sync_edits.sh"
  ```

- [ ] **Step 3** — Add the matching GitHub Actions check at `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/.github/workflows/forbid-sync-edits.yml`:

  ```yaml
  name: Forbid edits inside modules/s3dgraphy/sync/

  on:
    pull_request:
      paths:
        - 'modules/s3dgraphy/sync/**'

  jobs:
    block:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
          with:
            fetch-depth: 0
        - name: Check diff scope
          run: |
            set -euo pipefail
            base="${{ github.event.pull_request.base.sha }}"
            head="${{ github.event.pull_request.head.sha }}"
            changed=$(git diff --name-only "$base" "$head" \
              | grep '^modules/s3dgraphy/sync/.*\.py$' || true)
            if [[ -z "$changed" ]]; then
              echo "No sync/ file touched — pass."
              exit 0
            fi
            echo "::error::PR modifies modules/s3dgraphy/sync/ files:"
            echo "$changed"
            echo "::error::Apply the fix in pyarchinit-s3dgraphy-bridge instead."
            echo "::error::Then bump the version pin in requirements.txt."
            exit 1
  ```

- [ ] **Step 4** — Add a `CONTRIBUTING.md` section documenting the escape valve. Append to existing `CONTRIBUTING.md` (or create if missing) at the plugin root:

  ```markdown
  ## Editing modules/s3dgraphy/sync/

  Since plugin v5.9.1 (bridge migration), the 23 files under
  `modules/s3dgraphy/sync/` are 3-line shims that re-export
  `pyarchinit-s3dgraphy-bridge`. **Do not edit them.** A pre-commit
  hook and a GitHub Actions job will reject the PR.

  Bug fixes and features for the sync layer land in
  https://github.com/pyarchinit/pyarchinit-s3dgraphy-bridge. After the
  bridge ships a new patch, bump the pin in `requirements.txt` here.

  ### Hotfix escape valve

  In the rare case where a customer-blocking fix can't wait for a bridge
  release, you may temporarily edit the shim by setting
  `ALLOW_SYNC_EDIT=1` in the commit environment. You **must** open a
  follow-up PR against the bridge the same workday, and bump the pin to
  the bridge's hotfix release as soon as it is published.
  ```

### Task C-5 — Commit PR-C atomically

- [ ] **Step 1** — Stage everything PR-C touches:

  ```bash
  cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
  git add modules/s3dgraphy/sync/ \
          .pre-commit-config.yaml \
          scripts/check_no_sync_edits.sh \
          .github/workflows/forbid-sync-edits.yml \
          CONTRIBUTING.md
  git status
  ```

  Expected: 24 sync files modified (23 implementation + 1 master `__init__.py`) + 4 new infra files = 28 entries.

- [ ] **Step 2** — Commit:

  ```bash
  git commit -m "$(cat <<'EOF'
  PR-C: shim re-export 23 sync modules to pyarchinit-s3dgraphy-bridge

  Atomic conversion of modules/s3dgraphy/sync/*.py:
    - 23 implementation modules reduced to 3-line shims that re-export
      from pyarchinit_s3dgraphy_bridge.<module>
    - master __init__.py re-exports the bridge's public API at the
      legacy import path so ~80 plugin call sites keep working
      unchanged

  Guard-rails added:
    - .pre-commit-config.yaml + scripts/check_no_sync_edits.sh
      reject any further edit inside modules/s3dgraphy/sync/*
    - .github/workflows/forbid-sync-edits.yml mirrors the gate on PRs
    - CONTRIBUTING.md documents the ALLOW_SYNC_EDIT=1 hotfix escape

  Per spec docs/superpowers/specs/2026-05-20-s3dgraphy-bridge-design.md
  §"Plugin migration plan (Q6=C)" PR-C and §"Risks" mitigation row 2.

  Tests: 351 sync tests pass against the installed bridge (PR-A).
  EOF
  )"
  ```

---

## PR-D — CHANGELOG + metadata bump + tag

**Effort:** ~1 hour. **Branch:** `plugin/pr-d-changelog-tag`. **Rollback:** revert PR (no functional changes).

### Task D-1 — Write the bilingual CHANGELOG entry

- [ ] **Step 1** — Open `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/dev_logs/CHANGELOG.md` and insert the following block immediately under the file's top-level header (above the prior `5.9.0.1-alpha` entry):

  ```markdown
  ## 5.9.1-bridge-migration-alpha — 2026-05-20

  ### IT

  - **Refactor (Q6=C):** la sync layer s3dgraphy (`modules/s3dgraphy/sync/`)
    è stata estratta nel pacchetto vendored `pyarchinit-s3dgraphy-bridge==1.0.0`,
    pubblicato su PyPI. Le 23 implementazioni inline sono state ridotte a shim
    di 3 righe (`from pyarchinit_s3dgraphy_bridge.<mod> import *`) e il
    `__init__.py` master ri-esporta l'API pubblica del bridge sul percorso
    legacy. **Zero call site del plugin toccato** (~80 file invariati).
  - **Build:** `scripts/modules_installer.py` estende l'auto-installazione
    al nuovo pacchetto, dirottandolo in `ext_libs/` (come per `s3dgraphy`).
    `requirements.txt` aggiunge il pin `pyarchinit-s3dgraphy-bridge==1.0.0`.
  - **Adapter (PR-B):** nuovo package `modules/s3dgraphy/bridge_adapter/`
    con `QgisDbSession`, `QgisWorkspace`, `QSettingsProxy`, `QtFileProvider`,
    `QgsLogger` — implementazioni 1:1 dei 5 Protocol del bridge. 18 unit test
    eseguiti fuori da QGIS via `unittest.mock`.
  - **Guard-rail:** pre-commit hook (`scripts/check_no_sync_edits.sh`) +
    GitHub Actions (`.github/workflows/forbid-sync-edits.yml`) rifiutano
    qualsiasi modifica futura in `modules/s3dgraphy/sync/*`. I fix vanno
    aperti contro il repo del bridge. Escape valve documentata
    (`ALLOW_SYNC_EDIT=1`) per hotfix con follow-up PR same-day.
  - **Test:** 351 test in `tests/sync/` continuano a passare contro il bridge
    installato (AC-INT-5).
  - **Nota di conteggio:** la specifica indicava 22 file; l'audit on-disk
    al 2026-05-20 ha trovato 23 moduli di implementazione + 1 `__init__.py`
    master. Tutti elencati esplicitamente in `Plan 3 §PR-C Task C-1`.
  - **Cleanup futuro:** la rimozione dei 24 file shim è pianificata per
    plugin v6.0.0 (Q4 2026), quando bridge ≥ v1.4 e zero bug report per
    almeno 6 settimane.

  ### EN

  - **Refactor (Q6=C):** the s3dgraphy sync layer
    (`modules/s3dgraphy/sync/`) has been extracted into the vendored package
    `pyarchinit-s3dgraphy-bridge==1.0.0`, published to PyPI. The 23 inline
    implementations are reduced to 3-line shims
    (`from pyarchinit_s3dgraphy_bridge.<mod> import *`) and the master
    `__init__.py` re-exports the bridge's public API at the legacy path.
    **Zero plugin call sites touched** (~80 files unchanged).
  - **Build:** `scripts/modules_installer.py` extends auto-install to the
    new package, routing it into `ext_libs/` (same convention as
    `s3dgraphy`). `requirements.txt` adds the pin
    `pyarchinit-s3dgraphy-bridge==1.0.0`.
  - **Adapters (PR-B):** new package `modules/s3dgraphy/bridge_adapter/`
    with `QgisDbSession`, `QgisWorkspace`, `QSettingsProxy`,
    `QtFileProvider`, `QgsLogger` — 1:1 implementations of the bridge's 5
    Protocols. 18 unit tests run outside QGIS via `unittest.mock`.
  - **Guard-rail:** pre-commit hook (`scripts/check_no_sync_edits.sh`) +
    GitHub Actions (`.github/workflows/forbid-sync-edits.yml`) reject
    further edits inside `modules/s3dgraphy/sync/*`. Fixes go to the bridge
    repo. Escape valve documented (`ALLOW_SYNC_EDIT=1`) for hotfixes with
    same-day follow-up PR.
  - **Tests:** the 351 tests in `tests/sync/` continue to pass against the
    installed bridge (AC-INT-5).
  - **Count reconciliation:** the spec referenced 22 files; the 2026-05-20
    on-disk audit found 23 implementation modules + 1 master `__init__.py`.
    All listed explicitly in `Plan 3 §PR-C Task C-1`.
  - **Future cleanup:** the 24 shim files are scheduled for deletion in
    plugin v6.0.0 (Q4 2026), once bridge ≥ v1.4 and no bug reports surface
    for at least 6 weeks.
  ```

### Task D-2 — Bump metadata.txt

- [ ] **Step 1** — Edit `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/metadata.txt` line 8:

  ```diff
  -version=5.9.0.1-alpha
  +version=5.9.1-bridge-migration-alpha
  ```

- [ ] **Step 2** — Prepend the new entry to the `changelog=` block immediately after the `changelog=` line and before the `5.2.0-alpha` entry currently at the top. Insert:

  ```
  changelog=5.9.1-bridge-migration-alpha (2026-05-20) [Plugin migration to pyarchinit-s3dgraphy-bridge]:
      - Refactor: 23 modules in modules/s3dgraphy/sync/ reduced to 3-line shims
        re-exporting pyarchinit-s3dgraphy-bridge==1.0.0 (vendored PyPI package).
        Master __init__.py re-exports bridge's public API at the legacy import
        path. Zero plugin call sites touched (~80 files unaffected).
      - Build: scripts/modules_installer.py routes pyarchinit-s3dgraphy-bridge to
        ext_libs/ (alongside s3dgraphy). requirements.txt pins ==1.0.0.
      - Adapters: new modules/s3dgraphy/bridge_adapter/ implements the bridge's
        5 typing.Protocol contracts (DbSession, Workspace, Settings, FileProvider,
        Logger) via QgisDbSession, QgisWorkspace, QSettingsProxy, QtFileProvider,
        QgsLogger. 18 unit tests via unittest.mock.
      - Guard-rail: pre-commit hook + GitHub Actions reject edits inside
        modules/s3dgraphy/sync/* (fixes go to the bridge repo).
      - Tests: 351 sync tests pass against installed bridge (AC-INT-5).
    5.9.0.1-alpha (2026-05-16) [yE-F hotfix: primary attivita duplicate]:
  ```

- [ ] **Step 3** — Verify metadata.txt is still parse-able by reading the first 15 lines:

  ```bash
  head -15 "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/metadata.txt"
  ```

  Expected: `version=5.9.1-bridge-migration-alpha` on line 8.

### Task D-3 — Commit, tag, push

- [ ] **Step 1** — Stage:

  ```bash
  cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
  git add dev_logs/CHANGELOG.md metadata.txt
  git status
  ```

  Expected: 2 files staged.

- [ ] **Step 2** — Commit:

  ```bash
  git commit -m "$(cat <<'EOF'
  PR-D: bump to 5.9.1-bridge-migration-alpha + bilingual CHANGELOG

  Closes the plugin migration to pyarchinit-s3dgraphy-bridge v1.0.0.
  Bilingual (IT + EN) CHANGELOG entry covers PR-A through PR-C.
  metadata.txt version + changelog= block aligned.

  Per spec docs/superpowers/specs/2026-05-20-s3dgraphy-bridge-design.md
  §"Plugin migration plan (Q6=C)" PR-D, AC-INT-6.
  EOF
  )"
  ```

- [ ] **Step 3** — Create the annotated tag:

  ```bash
  git tag -a 5.9.1-bridge-migration-alpha -m "Plugin v5.9.1 — migration to pyarchinit-s3dgraphy-bridge==1.0.0 (Q6=C shim re-export)."
  ```

- [ ] **Step 4** — Push branch + tag:

  ```bash
  git push origin Stratigraph_00001
  git push origin 5.9.1-bridge-migration-alpha
  ```

- [ ] **Step 5** — Verify the tag is on the remote:

  ```bash
  git ls-remote --tags origin | grep 5.9.1-bridge-migration-alpha
  ```

  Expected: one line `<sha>\trefs/tags/5.9.1-bridge-migration-alpha`.

---

## Self-Review Checklist

Run this checklist before declaring the plan complete and before promoting the tag to "release":

- [ ] **AC-INT-4** — `find "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/s3dgraphy/sync" -name '*.py' -not -name '__init__.py' | wc -l` reports **23**. For each, `wc -l <file>` reports **≤ 3 lines**. Verify with:

  ```bash
  cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/s3dgraphy/sync"
  for f in $(ls *.py | grep -v __init__.py); do
    lines=$(wc -l < "$f")
    [[ "$lines" -gt 3 ]] && echo "FAIL: $f has $lines lines (>3)"
  done
  echo "AC-INT-4 check done"
  ```
  Expected output: only `AC-INT-4 check done` (no `FAIL:` lines).

- [ ] **AC-INT-5** — `pytest tests/sync/ -v` from the plugin root reports `351 passed` (or matching pre-migration baseline + 0 new failures).

- [ ] **AC-INT-6** — `git tag -l 5.9.1-bridge-migration-alpha` returns the tag locally, and `git ls-remote --tags origin` confirms it on the remote. `metadata.txt` line 8 is `version=5.9.1-bridge-migration-alpha`. `dev_logs/CHANGELOG.md` top entry is bilingual IT + EN dated 2026-05-20.

- [ ] **Zero-code-lines assertion** — every file under `modules/s3dgraphy/sync/` (excluding `__init__.py`) contains exactly 1 line of executable code (the `from … import *` line). Verify:

  ```bash
  cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/s3dgraphy/sync"
  for f in $(ls *.py | grep -v __init__.py); do
    code_lines=$(grep -cE '^(from|import)' "$f")
    [[ "$code_lines" -ne 1 ]] && echo "FAIL: $f has $code_lines code lines (expected 1)"
  done
  echo "zero-code-lines check done"
  ```
  Expected output: only `zero-code-lines check done` (no `FAIL:` lines).

- [ ] **Guard-rail smoke** — open a throwaway local commit that touches one sync shim (e.g. `echo "" >> modules/s3dgraphy/sync/uuid7.py`); run `git add modules/s3dgraphy/sync/uuid7.py && pre-commit run --files modules/s3dgraphy/sync/uuid7.py`. Expected: hook rejects the commit with the `[forbid-sync-edits] BLOCKED` message. Undo the test edit with `git restore modules/s3dgraphy/sync/uuid7.py`.

- [ ] **Coexistence sanity** — in a fresh QGIS Python console:

  ```python
  from pyarchinit.modules.s3dgraphy.sync.graph_projector import GraphProjector as ShimGP
  from pyarchinit_s3dgraphy_bridge.graph_projector import GraphProjector as BridgeGP
  assert ShimGP is BridgeGP, "shim must re-export the SAME class object"
  ```
  Expected: assertion passes silently. This is the post-PR-C state and the opposite of the post-PR-A check in Task A-3 Step 3 (where the two were distinct).

- [ ] **Adapter coverage** — `pytest tests/bridge_adapter/ -v` reports 18 passed.

- [ ] **No leftover `pyc` shadows** — `find "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/s3dgraphy/sync/__pycache__" -name '*.pyc' -delete` then restart QGIS. Verify no `ImportError` on first load.

- [ ] **PR-A inert state was preserved when reverting PR-C only** (rollback drill, optional): in a scratch branch, `git revert <PR-C-sha>` and confirm the plugin still loads (inline files come back; bridge sits unused alongside). This proves PR-C is reversible without touching PR-A or PR-B.