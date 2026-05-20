# Mini-desk Migration to pyarchinit-s3dgraphy-bridge v1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate `pyarchinit-mini-desk` from inline `graphproj/`, `graphml_io/`, `s3d_integration/` modules (14 files) to the published `pyarchinit-s3dgraphy-bridge==1.0.0` package via 6 sequential PRs. End state: legacy modules deleted, Flask routes preserved, tag `3.0.0-bridge-migration`.

**Architecture:** Delete-and-replace strategy (Q3=A in the spec). 5 Flask-side adapter classes implement the bridge Protocols. Every Flask endpoint that backed by a deleted module is rewired through the adapters with REST contract preserved.

**Tech Stack:** Python 3.11+, FastAPI (mini-desk's actual framework), SQLAlchemy, pytest, pytest-snapshot for route contract preservation.

**Hard pre-requisite:** `pyarchinit-s3dgraphy-bridge==1.0.0` published to PyPI with green AC-2 suite (Plan 1 complete).

**Spec reference:** [`docs/superpowers/specs/2026-05-20-s3dgraphy-bridge-design.md`](../specs/2026-05-20-s3dgraphy-bridge-design.md)

---

## Discovery notes (audit input, frozen 2026-05-20)

Mini-desk runs **two web stacks side-by-side**:
- **FastAPI** under `pyarchinit_mini/api/` (`sync.py`, `graphml.py`, `us.py`, etc.) — JSON REST.
- **Flask Blueprints** under `pyarchinit_mini/web_interface/` (`yed_import_routes.py`, `graph_routes.py`, `paradata_routes.py`, `paradata_ui_routes.py`, `three_d_builder_routes.py`, `harris_creator_routes.py`, `s3d_routes.py`) — server-rendered + JSON.

PR-1 (the audit) discovers all transitive callers; PR-4 re-routes both stacks.

Confirmed legacy module inventory (matches spec count = 14):

```
pyarchinit_mini/graphproj/  (10 files, survivors EXCLUDED)
  projector.py            <- delete
  ingestor.py             <- delete
  graph_to_db.py          <- delete
  paradata_store.py       <- delete
  edge_registry.py        <- delete
  graphml_writer.py       <- delete
  graphml_reader.py       <- delete
  rapporti_codec.py       <- delete
  s3d_projector.py        <- delete
  s3d_to_cytoscape.py     <- delete
  heriverse_parser.py     <- SURVIVOR (mini-desk specific)
  auto_regen.py           <- SURVIVOR (mini-desk specific)
  ingest_plan.py          <- SURVIVOR (mini-desk specific)
  filesystem.py           <- SURVIVOR (mini-desk specific)
  exceptions.py           <- SURVIVOR (re-export only)
  __init__.py             <- KEEP, prune re-exports

pyarchinit_mini/graphml_io/  (3 files DELETE, 2 SURVIVE)
  yed_importer.py         <- delete
  yed_writer.py           <- delete
  yed_keys.py             <- delete
  reader.py               <- SURVIVOR
  writer.py               <- SURVIVOR
  __init__.py             <- KEEP, prune re-exports

pyarchinit_mini/s3d_integration/  (1 file DELETE, 1 SURVIVES)
  s3d_converter.py        <- delete
  model_manager.py        <- SURVIVOR
  __init__.py             <- KEEP, prune re-exports
```

Total deletions = 10 + 3 + 1 = **14**. Matches Q3 spec exactly.

---

## PR-1 — Flask & FastAPI audit

**Goal:** Produce a machine-generated impact report listing every import, dynamic import, and route definition that touches a deleted module. No production code touched; only a script + a markdown report.

### Task 1.1 — Bootstrap the audit script skeleton

- [ ] Create directory `scripts/` if missing:
  ```bash
  test -d /Users/enzo/pyarchinit-mini-desk/scripts && echo "exists" || mkdir -p /Users/enzo/pyarchinit-mini-desk/scripts
  ```
  Expected: `exists` (the directory is present per discovery).

- [ ] Create file `/Users/enzo/pyarchinit-mini-desk/scripts/audit_legacy_imports.py` with shebang and the immutable list of 14 deletion targets:
  ```python
  #!/usr/bin/env python3
  """Audit legacy imports against the 14-module bridge-migration deletion list.

  Run from repo root:

      python scripts/audit_legacy_imports.py > docs/audit/2026-05-20-bridge-migration-impact.md

  The script greps `pyarchinit_mini/` for:
    1. static `from pyarchinit_mini.<deleted_module> import ...`
    2. static `import pyarchinit_mini.<deleted_module>`
    3. dynamic `importlib.import_module("pyarchinit_mini.<deleted_module>...")`
    4. Flask Blueprint route decorators (`@*_bp.route`, `@*_bp.get`, `@*_bp.post`)
    5. FastAPI route decorators (`@router.get`, `@router.post`, `@router.put`,
       `@router.delete`) defined in files that transitively reach a deleted module.
  """
  from __future__ import annotations

  import re
  import sys
  from pathlib import Path

  ROOT = Path(__file__).resolve().parent.parent
  PKG = ROOT / "pyarchinit_mini"

  DELETED_MODULES = [
      "pyarchinit_mini.graphproj.projector",
      "pyarchinit_mini.graphproj.ingestor",
      "pyarchinit_mini.graphproj.graph_to_db",
      "pyarchinit_mini.graphproj.paradata_store",
      "pyarchinit_mini.graphproj.edge_registry",
      "pyarchinit_mini.graphproj.graphml_writer",
      "pyarchinit_mini.graphproj.graphml_reader",
      "pyarchinit_mini.graphproj.rapporti_codec",
      "pyarchinit_mini.graphproj.s3d_projector",
      "pyarchinit_mini.graphproj.s3d_to_cytoscape",
      "pyarchinit_mini.graphml_io.yed_importer",
      "pyarchinit_mini.graphml_io.yed_writer",
      "pyarchinit_mini.graphml_io.yed_keys",
      "pyarchinit_mini.s3d_integration.s3d_converter",
  ]
  ```
  Expected: file exists; `python -c "import ast; ast.parse(open('/Users/enzo/pyarchinit-mini-desk/scripts/audit_legacy_imports.py').read())"` exits 0.

- [ ] Commit step (end of PR-1 sequence below).

### Task 1.2 — Static-import scanner

- [ ] Append to `scripts/audit_legacy_imports.py` a `scan_static_imports()` function:
  ```python
  def scan_static_imports() -> dict[str, list[tuple[Path, int, str]]]:
      """Return {deleted_module: [(file, lineno, source_line), ...]}."""
      hits: dict[str, list[tuple[Path, int, str]]] = {m: [] for m in DELETED_MODULES}
      patterns = {
          m: re.compile(
              rf"^\s*(?:from\s+{re.escape(m)}\s+import|import\s+{re.escape(m)}\b)"
          )
          for m in DELETED_MODULES
      }
      for py in PKG.rglob("*.py"):
          if "__pycache__" in py.parts:
              continue
          for lineno, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
              for mod, pat in patterns.items():
                  if pat.search(line):
                      hits[mod].append((py.relative_to(ROOT), lineno, line.strip()))
      return hits
  ```
  Expected: import succeeds — `python -c "from scripts.audit_legacy_imports import scan_static_imports"` runs without error.

- [ ] Add a smoke check at the bottom of the file (under `if __name__ == "__main__":`) that prints `len(scan_static_imports())` matches `len(DELETED_MODULES)`:
  ```python
  if __name__ == "__main__":
      static = scan_static_imports()
      assert len(static) == 14, f"expected 14 buckets, got {len(static)}"
  ```
  Run: `python /Users/enzo/pyarchinit-mini-desk/scripts/audit_legacy_imports.py`. Expected: silent exit 0.

### Task 1.3 — Dynamic-import scanner (string-literal grep)

- [ ] Append `scan_dynamic_imports()` to the script:
  ```python
  def scan_dynamic_imports() -> list[tuple[Path, int, str]]:
      """Find importlib.import_module("pyarchinit_mini.<deleted>") and equivalent."""
      hits: list[tuple[Path, int, str]] = []
      lit_re = re.compile(
          r"""(import_module|__import__)\s*\(\s*["']("""
          + "|".join(re.escape(m) for m in DELETED_MODULES)
          + r""")["']"""
      )
      for py in PKG.rglob("*.py"):
          if "__pycache__" in py.parts:
              continue
          for lineno, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
              if lit_re.search(line):
                  hits.append((py.relative_to(ROOT), lineno, line.strip()))
      return hits
  ```
  Expected: `python -c "from scripts.audit_legacy_imports import scan_dynamic_imports; print(scan_dynamic_imports())"` returns a list (possibly empty).

### Task 1.4 — Route-decorator scanner

- [ ] Append `scan_routes()` to the script. It collects both Flask (`@<name>_bp.<verb>`) and FastAPI (`@router.<verb>`) decorators in files that statically import a deleted module:
  ```python
  ROUTE_RE = re.compile(
      r"""^\s*@\s*(?:[A-Za-z_][A-Za-z0-9_]*\.)?(?:router|[A-Za-z_]+_bp)"""
      r"""\.(get|post|put|delete|patch|route)\s*\(\s*["']([^"']+)["']"""
  )


  def scan_routes(static_hits: dict[str, list]) -> dict[Path, list[tuple[int, str, str]]]:
      """{flask_or_fastapi_file: [(lineno, verb, path), ...]}."""
      tainted_files = {p for entries in static_hits.values() for (p, _, _) in entries}
      out: dict[Path, list[tuple[int, str, str]]] = {}
      for py in sorted(tainted_files):
          full = ROOT / py
          for lineno, line in enumerate(full.read_text(encoding="utf-8").splitlines(), 1):
              m = ROUTE_RE.match(line)
              if m:
                  out.setdefault(py, []).append((lineno, m.group(1).upper(), m.group(2)))
      return out
  ```
  Expected: `python -c "from scripts.audit_legacy_imports import scan_routes, scan_static_imports; print(len(scan_routes(scan_static_imports())))"` returns a non-negative integer.

### Task 1.5 — Markdown emitter

- [ ] Append `emit_markdown()` and wire it into `__main__`:
  ```python
  def emit_markdown(
      static_hits: dict[str, list],
      dynamic_hits: list,
      routes: dict[Path, list],
  ) -> str:
      lines = ["# Bridge migration impact — generated", ""]
      lines.append(f"Generated by `scripts/audit_legacy_imports.py` on demand.")
      lines.append("")
      lines.append("## 1. Static imports of deleted modules")
      for mod, entries in static_hits.items():
          lines.append(f"### `{mod}`  ({len(entries)} hits)")
          for path, ln, src in entries:
              lines.append(f"- `{path}:{ln}` — `{src}`")
          lines.append("")
      lines.append("## 2. Dynamic imports (importlib/__import__ literals)")
      if not dynamic_hits:
          lines.append("_None detected._")
      for path, ln, src in dynamic_hits:
          lines.append(f"- `{path}:{ln}` — `{src}`")
      lines.append("")
      lines.append("## 3. Route decorators in tainted files")
      for path, entries in routes.items():
          lines.append(f"### `{path}`")
          for ln, verb, route in entries:
              lines.append(f"- L{ln}: `{verb} {route}`")
          lines.append("")
      return "\n".join(lines)


  if __name__ == "__main__":
      static = scan_static_imports()
      dynamic = scan_dynamic_imports()
      routes = scan_routes(static)
      print(emit_markdown(static, dynamic, routes))
  ```
  Expected: running the script prints a markdown document to stdout.

### Task 1.6 — Generate and save the impact report

- [ ] Create the audit directory and run the script:
  ```bash
  mkdir -p /Users/enzo/pyarchinit-mini-desk/docs/audit && \
  cd /Users/enzo/pyarchinit-mini-desk && \
  python scripts/audit_legacy_imports.py > docs/audit/2026-05-20-bridge-migration-impact.md
  ```
  Expected: file `/Users/enzo/pyarchinit-mini-desk/docs/audit/2026-05-20-bridge-migration-impact.md` is non-empty.

- [ ] Verify the report contains all 14 sections:
  ```bash
  grep -c "^### \`pyarchinit_mini\." /Users/enzo/pyarchinit-mini-desk/docs/audit/2026-05-20-bridge-migration-impact.md
  ```
  Expected: `14` (one heading per deleted module).

### Task 1.7 — Manual review gate

- [ ] Print a manual-review checklist in the impact report by appending to the file (the executor reads the printed list and confirms each item):
  ```markdown
  ## Manual review checklist (HUMAN gate)

  - [ ] Every route under "tainted files" has a documented JSON contract or template.
  - [ ] No `subprocess.run(["python", "-m", "pyarchinit_mini.graphproj...."])` style invocations.
  - [ ] No template strings in `web_interface/templates/` reference a deleted module by name.
  - [ ] CHANGELOG.md sections about the deleted modules are flagged for rewrite in PR-6.
  ```
  Expected: the four checkboxes appear at the bottom of the file.

### Task 1.8 — PR-1 commit

- [ ] Run:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add scripts/audit_legacy_imports.py docs/audit/2026-05-20-bridge-migration-impact.md && \
  git commit -m "chore(bridge-migration): PR-1 add legacy-import audit script + impact report"
  ```
  Expected: commit succeeds; `git log -1 --oneline` shows the new commit.

---

## PR-2 — Flask-side adapters (5 Protocol implementations)

**Goal:** Implement 5 adapter classes in a new `pyarchinit_mini/bridge_adapter/` package, each satisfying one bridge `Protocol`. Each adapter has unit tests that mock the bridge Protocol to keep PR-2 independent of PR-3 (bridge not yet a hard dependency).

### Task 2.1 — Package scaffold

- [ ] Create the directory and `__init__.py`:
  ```bash
  mkdir -p /Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/bridge_adapter
  ```
  Expected: directory exists.

- [ ] Create `/Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/bridge_adapter/__init__.py`:
  ```python
  """Mini-desk adapters for `pyarchinit_s3dgraphy_bridge` Protocols.

  Each adapter is a thin wrapper around an existing mini-desk dependency
  (SQLAlchemy Session, Flask app.config, AppSetting model, upload directory,
  stdlib logging) that fulfils one of the 5 bridge Protocols.
  """

  from .db_session import SqlalchemyDbSession  # noqa: F401
  from .workspace import FlaskWorkspace  # noqa: F401
  from .settings import AppSettingProxy  # noqa: F401
  from .file_provider import UploadFileProvider  # noqa: F401
  from .logger import PythonLogger  # noqa: F401

  __all__ = [
      "SqlalchemyDbSession",
      "FlaskWorkspace",
      "AppSettingProxy",
      "UploadFileProvider",
      "PythonLogger",
  ]
  ```
  Expected: file exists.

- [ ] Create tests dir: `mkdir -p /Users/enzo/pyarchinit-mini-desk/tests/bridge_adapter` and an empty `tests/bridge_adapter/__init__.py`.

### Task 2.2 — `SqlalchemyDbSession` adapter (DbSession Protocol)

- [ ] Write failing test `/Users/enzo/pyarchinit-mini-desk/tests/bridge_adapter/test_db_session.py`:
  ```python
  """SqlalchemyDbSession satisfies the bridge DbSession Protocol."""
  from sqlalchemy import create_engine, text
  from sqlalchemy.orm import sessionmaker

  from pyarchinit_mini.bridge_adapter import SqlalchemyDbSession


  def _make_session():
      engine = create_engine("sqlite:///:memory:")
      Session = sessionmaker(bind=engine)
      return Session()


  def test_execute_returns_cursor_like_object():
      adapter = SqlalchemyDbSession(_make_session())
      rs = adapter.execute("SELECT 1 AS x")
      rows = list(rs)
      assert rows[0][0] == 1


  def test_commit_does_not_raise():
      adapter = SqlalchemyDbSession(_make_session())
      adapter.commit()


  def test_is_postgres_flag_false_for_sqlite():
      adapter = SqlalchemyDbSession(_make_session())
      assert adapter.is_postgres is False
  ```
  Run: `cd /Users/enzo/pyarchinit-mini-desk && pytest tests/bridge_adapter/test_db_session.py -x`. Expected: 3 failures (ImportError of `SqlalchemyDbSession`).

- [ ] Implement `/Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/bridge_adapter/db_session.py`:
  ```python
  """SqlalchemyDbSession — wraps SQLAlchemy Session to satisfy DbSession Protocol."""
  from __future__ import annotations

  from typing import Any

  from sqlalchemy import text
  from sqlalchemy.orm import Session


  class SqlalchemyDbSession:
      def __init__(self, session: Session):
          self._session = session
          dialect = session.bind.dialect.name if session.bind is not None else "sqlite"
          self.is_postgres = dialect.startswith("postgres")

      def execute(self, sql: str, params: dict | None = None):
          return self._session.execute(text(sql), params or {})

      def commit(self) -> None:
          self._session.commit()
  ```
  Run: `pytest tests/bridge_adapter/test_db_session.py -x`. Expected: 3 passed.

- [ ] Commit:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add pyarchinit_mini/bridge_adapter/__init__.py \
          pyarchinit_mini/bridge_adapter/db_session.py \
          tests/bridge_adapter/__init__.py \
          tests/bridge_adapter/test_db_session.py && \
  git commit -m "feat(bridge-adapter): SqlalchemyDbSession implements DbSession Protocol"
  ```

### Task 2.3 — `FlaskWorkspace` adapter (Workspace Protocol)

- [ ] Failing test `/Users/enzo/pyarchinit-mini-desk/tests/bridge_adapter/test_workspace.py`:
  ```python
  from pathlib import Path

  from pyarchinit_mini.bridge_adapter import FlaskWorkspace


  def test_root_property(tmp_path):
      ws = FlaskWorkspace(tmp_path)
      assert ws.root == tmp_path


  def test_tmp_dir_is_created(tmp_path):
      ws = FlaskWorkspace(tmp_path)
      t = ws.tmp()
      assert t.exists() and t.is_dir()
      assert t.parent == tmp_path
  ```
  Run: `pytest tests/bridge_adapter/test_workspace.py -x`. Expected: 2 failures (ImportError).

- [ ] Implement `/Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/bridge_adapter/workspace.py`:
  ```python
  """FlaskWorkspace — wraps an upload-root path to satisfy Workspace Protocol."""
  from __future__ import annotations

  from pathlib import Path


  class FlaskWorkspace:
      def __init__(self, root: Path | str):
          self.root = Path(root)
          self.root.mkdir(parents=True, exist_ok=True)

      def tmp(self) -> Path:
          t = self.root / "tmp"
          t.mkdir(parents=True, exist_ok=True)
          return t
  ```
  Run: `pytest tests/bridge_adapter/test_workspace.py -x`. Expected: 2 passed.

- [ ] Commit:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add pyarchinit_mini/bridge_adapter/workspace.py tests/bridge_adapter/test_workspace.py && \
  git commit -m "feat(bridge-adapter): FlaskWorkspace implements Workspace Protocol"
  ```

### Task 2.4 — `AppSettingProxy` adapter (Settings Protocol)

- [ ] Failing test `/Users/enzo/pyarchinit-mini-desk/tests/bridge_adapter/test_settings.py`:
  ```python
  from unittest.mock import MagicMock

  from pyarchinit_mini.bridge_adapter import AppSettingProxy


  def test_get_existing_key():
      svc = MagicMock()
      svc.get.return_value = "openai"
      proxy = AppSettingProxy(svc)
      assert proxy.get("ai.provider") == "openai"
      svc.get.assert_called_once_with("ai.provider")


  def test_get_missing_returns_default():
      svc = MagicMock()
      svc.get.return_value = None
      proxy = AppSettingProxy(svc)
      assert proxy.get("absent", default=42) == 42
  ```
  Run: `pytest tests/bridge_adapter/test_settings.py -x`. Expected: 2 failures (ImportError).

- [ ] Implement `/Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/bridge_adapter/settings.py`:
  ```python
  """AppSettingProxy — wraps AppSettingService to satisfy Settings Protocol."""
  from __future__ import annotations

  from typing import Any


  class AppSettingProxy:
      def __init__(self, app_setting_service):
          self._svc = app_setting_service

      def get(self, key: str, default: Any = None) -> Any:
          val = self._svc.get(key)
          return default if val is None else val
  ```
  Run: `pytest tests/bridge_adapter/test_settings.py -x`. Expected: 2 passed.

- [ ] Commit:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add pyarchinit_mini/bridge_adapter/settings.py tests/bridge_adapter/test_settings.py && \
  git commit -m "feat(bridge-adapter): AppSettingProxy implements Settings Protocol"
  ```

### Task 2.5 — `UploadFileProvider` adapter (FileProvider Protocol)

- [ ] Failing test `/Users/enzo/pyarchinit-mini-desk/tests/bridge_adapter/test_file_provider.py`:
  ```python
  import pytest

  from pyarchinit_mini.bridge_adapter import UploadFileProvider


  def test_read_bytes_relative_ref(tmp_path):
      (tmp_path / "hello.txt").write_bytes(b"hello")
      fp = UploadFileProvider(upload_root=tmp_path)
      assert fp.read_bytes("hello.txt") == b"hello"


  def test_traversal_is_rejected(tmp_path):
      fp = UploadFileProvider(upload_root=tmp_path)
      with pytest.raises(ValueError):
          fp.read_bytes("../../etc/passwd")


  def test_missing_raises_filenotfound(tmp_path):
      fp = UploadFileProvider(upload_root=tmp_path)
      with pytest.raises(FileNotFoundError):
          fp.read_bytes("nope.bin")
  ```
  Run: `pytest tests/bridge_adapter/test_file_provider.py -x`. Expected: 3 failures (ImportError).

- [ ] Implement `/Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/bridge_adapter/file_provider.py`:
  ```python
  """UploadFileProvider — wraps Flask UPLOAD_FOLDER to satisfy FileProvider Protocol."""
  from __future__ import annotations

  from pathlib import Path


  class UploadFileProvider:
      def __init__(self, upload_root: Path | str):
          self._root = Path(upload_root).resolve()
          self._root.mkdir(parents=True, exist_ok=True)

      def read_bytes(self, ref: str) -> bytes:
          target = (self._root / ref).resolve()
          # path-traversal guard: target must remain inside upload root
          if self._root not in target.parents and target != self._root:
              raise ValueError(f"path traversal detected: {ref!r}")
          if not target.is_file():
              raise FileNotFoundError(target)
          return target.read_bytes()
  ```
  Run: `pytest tests/bridge_adapter/test_file_provider.py -x`. Expected: 3 passed.

- [ ] Commit:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add pyarchinit_mini/bridge_adapter/file_provider.py tests/bridge_adapter/test_file_provider.py && \
  git commit -m "feat(bridge-adapter): UploadFileProvider implements FileProvider Protocol"
  ```

### Task 2.6 — `PythonLogger` adapter (Logger Protocol)

- [ ] Failing test `/Users/enzo/pyarchinit-mini-desk/tests/bridge_adapter/test_logger.py`:
  ```python
  import logging

  from pyarchinit_mini.bridge_adapter import PythonLogger


  def test_info_routes_to_underlying_logger(caplog):
      adapter = PythonLogger(logging.getLogger("bridge_adapter_test"))
      with caplog.at_level(logging.INFO, logger="bridge_adapter_test"):
          adapter.info("hello")
      assert any("hello" in r.message for r in caplog.records)


  def test_error_records_exception(caplog):
      adapter = PythonLogger(logging.getLogger("bridge_adapter_test"))
      with caplog.at_level(logging.ERROR, logger="bridge_adapter_test"):
          adapter.error("boom", exc=RuntimeError("x"))
      assert any("boom" in r.message for r in caplog.records)


  def test_warn_alias(caplog):
      adapter = PythonLogger(logging.getLogger("bridge_adapter_test"))
      with caplog.at_level(logging.WARNING, logger="bridge_adapter_test"):
          adapter.warn("careful")
      assert any("careful" in r.message for r in caplog.records)
  ```
  Run: `pytest tests/bridge_adapter/test_logger.py -x`. Expected: 3 failures (ImportError).

- [ ] Implement `/Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/bridge_adapter/logger.py`:
  ```python
  """PythonLogger — wraps stdlib logging.Logger to satisfy Logger Protocol."""
  from __future__ import annotations

  import logging


  class PythonLogger:
      def __init__(self, logger: logging.Logger | None = None):
          self._log = logger or logging.getLogger("pyarchinit_s3dgraphy_bridge")

      def info(self, msg: str) -> None:
          self._log.info(msg)

      def warn(self, msg: str) -> None:
          self._log.warning(msg)

      def error(self, msg: str, exc: Exception | None = None) -> None:
          if exc is not None:
              self._log.error("%s — %s: %s", msg, type(exc).__name__, exc)
          else:
              self._log.error(msg)
  ```
  Run: `pytest tests/bridge_adapter/test_logger.py -x`. Expected: 3 passed.

- [ ] Commit:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add pyarchinit_mini/bridge_adapter/logger.py tests/bridge_adapter/test_logger.py && \
  git commit -m "feat(bridge-adapter): PythonLogger implements Logger Protocol"
  ```

### Task 2.7 — PR-2 closure: combined import smoke

- [ ] Add `/Users/enzo/pyarchinit-mini-desk/tests/bridge_adapter/test_package_imports.py`:
  ```python
  """All 5 adapters import cleanly from the public package surface."""

  def test_public_surface_complete():
      from pyarchinit_mini.bridge_adapter import (
          SqlalchemyDbSession,
          FlaskWorkspace,
          AppSettingProxy,
          UploadFileProvider,
          PythonLogger,
      )
      assert all(cls is not None for cls in (
          SqlalchemyDbSession, FlaskWorkspace, AppSettingProxy,
          UploadFileProvider, PythonLogger,
      ))
  ```
  Run: `pytest tests/bridge_adapter -x`. Expected: 14 passed (3+2+2+3+3+1).

- [ ] Commit:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add tests/bridge_adapter/test_package_imports.py && \
  git commit -m "test(bridge-adapter): PR-2 public surface smoke test (5/5 adapters)"
  ```

---

## PR-3 — requirements + dev install + green CI

**Goal:** Add `pyarchinit-s3dgraphy-bridge==1.0.0` to project metadata. Add a Makefile target for editable local install. Run the full test suite to confirm zero regressions while the bridge is installed but not yet used by routes.

### Task 3.1 — Pin the bridge in `pyproject.toml`

- [ ] Open `/Users/enzo/pyarchinit-mini-desk/pyproject.toml` and locate the `[project]` table's `dependencies = [...]` list.

- [ ] Add the line `"pyarchinit-s3dgraphy-bridge==1.0.0",` to the `dependencies` array, alphabetically positioned (between `pyarchinit-...` lexical neighbours if any).

- [ ] Verify the file still parses:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  python -c "import tomllib; tomllib.loads(open('pyproject.toml','rb').read().decode())"
  ```
  Expected: silent exit 0.

- [ ] Commit:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add pyproject.toml && \
  git commit -m "build(deps): pin pyarchinit-s3dgraphy-bridge==1.0.0 (PR-3)"
  ```

### Task 3.2 — Add `dev-install-bridge` Makefile target

- [ ] Open or create `/Users/enzo/pyarchinit-mini-desk/Makefile`. Append:
  ```make
  .PHONY: dev-install-bridge
  dev-install-bridge:  ## Install pyarchinit-s3dgraphy-bridge in editable mode from sibling checkout
  	@if [ -z "$$BRIDGE_PATH" ]; then \
  		echo "Set BRIDGE_PATH=/path/to/pyarchinit-s3dgraphy-bridge (sibling clone)"; \
  		exit 1; \
  	fi
  	pip install -e "$$BRIDGE_PATH"
  	python -c "import pyarchinit_s3dgraphy_bridge; print(pyarchinit_s3dgraphy_bridge.__version__)"
  ```
  Expected: `make dev-install-bridge BRIDGE_PATH=/Users/enzo/dev/pyarchinit-s3dgraphy-bridge` prints `1.0.0`.

- [ ] Commit:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add Makefile && \
  git commit -m "build(make): dev-install-bridge target for editable local install"
  ```

### Task 3.3 — Verify CI passes with bridge installed but unused

- [ ] Run the full test suite locally:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  pip install pyarchinit-s3dgraphy-bridge==1.0.0 && \
  pytest -x --ignore=archive_local
  ```
  Expected: all tests pass; final summary line is `=== <N> passed in <T>s ===`.

- [ ] Capture pass count for the PR description (record in commit message body if useful). No further commit on this task (no files changed).

---

## PR-4 — Re-route APIs through the bridge

**Goal:** For each route identified in PR-1's impact report, swap the implementation to call the bridge via the PR-2 adapters. REST contracts (JSON shape, status codes, HTML response shells) are preserved — snapshot tests assert this.

> **NOTE:** The exact set of routes is the union of (a) every `@*_bp.<verb>` in `pyarchinit_mini/web_interface/yed_import_routes.py`, `graph_routes.py`, `paradata_routes.py`, `paradata_ui_routes.py`, `harris_creator_routes.py`, `three_d_builder_routes.py`, `s3d_routes.py` that the audit flagged, and (b) every `@router.<verb>` in `pyarchinit_mini/api/sync.py`, `graphml.py`. The tasks below cover the **known fixed set**; if the audit surfaces a route not listed here, the executor must add a parallel task following the pattern of Task 4.2.

### Task 4.1 — Test infrastructure: snapshot fixtures

- [ ] Add pytest-snapshot to dev deps:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && pip install pytest-snapshot
  ```
  Expected: install succeeds.

- [ ] Append `"pytest-snapshot>=0.9",` to the `[project.optional-dependencies].dev` array in `pyproject.toml` (create the array if missing).

- [ ] Create `/Users/enzo/pyarchinit-mini-desk/tests/integration/test_route_contracts.py` placeholder:
  ```python
  """REST contract snapshot tests for bridge-migration PR-4.

  Each test records the pre-migration response shape into a snapshot file,
  then asserts the post-migration response matches.
  """
  import json
  from pathlib import Path

  import pytest

  SNAP_DIR = Path(__file__).parent / "snapshots" / "bridge_migration"
  SNAP_DIR.mkdir(parents=True, exist_ok=True)


  @pytest.fixture
  def client():
      from pyarchinit_mini.web_interface.app import create_app
      app = create_app(testing=True)
      with app.test_client() as c:
          yield c
  ```
  Expected: file exists; `pytest --collect-only tests/integration/test_route_contracts.py` collects 0 tests (fixture-only).

- [ ] Commit:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add pyproject.toml tests/integration/test_route_contracts.py && \
  git commit -m "test(bridge-migration): PR-4 snapshot fixture scaffold"
  ```

### Task 4.2 — Re-route `POST /import-graphml/preview` (Flask)

- [ ] Pre-migration snapshot: add to `tests/integration/test_route_contracts.py`:
  ```python
  def test_import_graphml_preview_contract(client, snapshot, tmp_path):
      sample = Path(__file__).parent.parent / "fixtures" / "Extended_Matrix_test_1.graphml"
      with sample.open("rb") as fh:
          resp = client.post("/import-graphml/preview",
                             data={"file": (fh, sample.name)},
                             content_type="multipart/form-data")
      assert resp.status_code == 200
      snapshot.assert_match(json.dumps(resp.get_json(), sort_keys=True, indent=2),
                            "import_graphml_preview.json")
  ```
  Run: `pytest tests/integration/test_route_contracts.py::test_import_graphml_preview_contract --snapshot-update`. Expected: snapshot created.

- [ ] Edit `/Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/web_interface/yed_import_routes.py`:
  Replace
  ```python
  from pyarchinit_mini.graphml_io.yed_importer import (
      parse_extended_matrix, build_import_plan, apply_import_plan,
  )
  ```
  with
  ```python
  from pyarchinit_s3dgraphy_bridge.yed_import_pipeline import (
      parse_extended_matrix, build_import_plan, apply_import_plan,
  )
  ```
  and inject the adapters at the call sites that previously used `_get_session()` directly. Use:
  ```python
  from pyarchinit_mini.bridge_adapter import (
      SqlalchemyDbSession, FlaskWorkspace, AppSettingProxy,
      UploadFileProvider, PythonLogger,
  )
  ```

- [ ] Re-run the snapshot test without `--snapshot-update`:
  ```bash
  pytest tests/integration/test_route_contracts.py::test_import_graphml_preview_contract -x
  ```
  Expected: passes; JSON shape unchanged.

- [ ] Commit:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add pyarchinit_mini/web_interface/yed_import_routes.py \
          tests/integration/test_route_contracts.py \
          tests/integration/snapshots/bridge_migration/import_graphml_preview.json && \
  git commit -m "refactor(yed-import): route POST /import-graphml/preview through bridge"
  ```

### Task 4.3 — Re-route `POST /import-graphml/apply` (Flask)

- [ ] Snapshot test:
  ```python
  def test_import_graphml_apply_contract(client, snapshot):
      resp = client.post("/import-graphml/apply", json={"plan_id": "stub"})
      # status may be 400 if plan_id missing, that's fine — we snapshot the shape
      snapshot.assert_match(
          json.dumps({"status": resp.status_code, "body": resp.get_json()},
                     sort_keys=True, indent=2),
          "import_graphml_apply.json",
      )
  ```
  Capture snapshot with `--snapshot-update`.

- [ ] In `yed_import_routes.py`, swap the `apply_import_plan` call site to use the bridge's `apply_import_plan` and wrap the SQLAlchemy session via `SqlalchemyDbSession(_get_session())`.

- [ ] Re-run without `--snapshot-update`. Expected: pass.

- [ ] Commit:
  ```bash
  git add pyarchinit_mini/web_interface/yed_import_routes.py \
          tests/integration/test_route_contracts.py \
          tests/integration/snapshots/bridge_migration/import_graphml_apply.json && \
  git commit -m "refactor(yed-import): route POST /import-graphml/apply through bridge"
  ```

### Task 4.4 — Re-route `graph_routes.py` (GraphML write/read endpoints)

- [ ] Add snapshot tests for every `@*_bp.<verb>` listed under `graph_routes.py` in the audit report — minimum: the GraphML export endpoint (`GET /graph/export.graphml` or whatever path the audit shows). Pattern is identical to Task 4.2.

- [ ] In `graph_routes.py`, swap:
  - `from pyarchinit_mini.graphproj.graphml_writer import ...` → `from pyarchinit_s3dgraphy_bridge.graphml_writer import ...`
  - `from pyarchinit_mini.graphproj.projector import ...` → `from pyarchinit_s3dgraphy_bridge.graph_projector import ...`
  - `from pyarchinit_mini.graphml_io.yed_writer import ...` → `from pyarchinit_s3dgraphy_bridge.graphml_writer import ...`

- [ ] Re-run snapshot tests. Expected: all pass byte-identical (because AC-2 contract from bridge v1.0).

- [ ] Commit:
  ```bash
  git add pyarchinit_mini/web_interface/graph_routes.py \
          tests/integration/test_route_contracts.py \
          tests/integration/snapshots/bridge_migration/graph_*.json && \
  git commit -m "refactor(graph): route GraphML export endpoints through bridge"
  ```

### Task 4.5 — Re-route `paradata_routes.py` + `paradata_ui_routes.py`

- [ ] Add snapshot tests for every paradata endpoint flagged by the audit.

- [ ] Swap:
  - `from pyarchinit_mini.graphproj.paradata_store import ...` → `from pyarchinit_s3dgraphy_bridge.paradata_store import ...`
  - `from pyarchinit_mini.graphproj.edge_registry import ...` → `from pyarchinit_s3dgraphy_bridge.edge_registry import ...`
  - `from pyarchinit_mini.graphproj.rapporti_codec import ...` → `from pyarchinit_s3dgraphy_bridge.yed_rapporti_policy import ...`

- [ ] Run all snapshot tests. Expected: pass.

- [ ] Commit:
  ```bash
  git add pyarchinit_mini/web_interface/paradata_routes.py \
          pyarchinit_mini/web_interface/paradata_ui_routes.py \
          tests/integration/test_route_contracts.py \
          tests/integration/snapshots/bridge_migration/paradata_*.json && \
  git commit -m "refactor(paradata): route paradata endpoints through bridge"
  ```

### Task 4.6 — Re-route `harris_creator_routes.py`

- [ ] Snapshot Harris-creator endpoints (audit-driven).

- [ ] Swap:
  - `from pyarchinit_mini.graphproj.graphml_writer import ...` → bridge equivalent
  - `from pyarchinit_mini.graphml_io.yed_writer import ...` → `from pyarchinit_s3dgraphy_bridge.graphml_writer import ...`
  - `from pyarchinit_mini.graphproj.auto_regen import ...` → KEEP (mini-desk survivor)

- [ ] Run snapshots. Expected: pass.

- [ ] Commit:
  ```bash
  git add pyarchinit_mini/web_interface/harris_creator_routes.py \
          tests/integration/test_route_contracts.py \
          tests/integration/snapshots/bridge_migration/harris_*.json && \
  git commit -m "refactor(harris-creator): route through bridge (auto_regen survivor untouched)"
  ```

### Task 4.7 — Re-route `three_d_builder_routes.py` + `s3d_routes.py`

- [ ] Snapshot tests for any 3D-related endpoint that uses `s3d_projector.py` or `s3d_to_cytoscape.py` or `s3d_converter.py`.

- [ ] Swap:
  - `from pyarchinit_mini.graphproj.s3d_projector import ...` → equivalent bridge symbol (likely `graph_projector` + a thin S3D wrapper; if not present in bridge v1.0, raise with a TODO marker that this endpoint is **out of MVP scope** and must be parked — DO NOT delete it).
  - `from pyarchinit_mini.graphproj.s3d_to_cytoscape import ...` → same as above.
  - `from pyarchinit_mini.s3d_integration.s3d_converter import S3DConverter` → if the bridge ships an equivalent, swap; otherwise emit a deprecation log and route to a 501 response for the affected endpoints, documented in CHANGELOG (PR-6).

- [ ] Run snapshots. Expected: pass OR documented 501 for parked endpoints.

- [ ] Commit:
  ```bash
  git add pyarchinit_mini/web_interface/three_d_builder_routes.py \
          pyarchinit_mini/web_interface/s3d_routes.py \
          tests/integration/test_route_contracts.py \
          tests/integration/snapshots/bridge_migration/three_d_*.json \
          tests/integration/snapshots/bridge_migration/s3d_*.json && \
  git commit -m "refactor(s3d): route 3D endpoints through bridge (park anything bridge<1.0 lacks)"
  ```

### Task 4.8 — Re-route FastAPI `pyarchinit_mini/api/sync.py`

- [ ] Snapshot test each of the 8 endpoints:
  - `GET /api/v1/sync/status`
  - `POST /api/v1/sync/export`
  - `POST /api/v1/sync/push`
  - `GET /api/v1/sync/connectivity`
  - `GET /api/v1/sync/queue`
  - `POST /api/v1/sync/queue/{entry_id}/retry`
  - `GET /api/v1/sync/conflicts`
  - `POST /api/v1/sync/conflicts/{conflict_id}/resolve`

  Pattern for one:
  ```python
  def test_sync_status_contract(fastapi_client, snapshot):
      resp = fastapi_client.get("/api/v1/sync/status")
      assert resp.status_code == 200
      snapshot.assert_match(
          json.dumps(resp.json(), sort_keys=True, indent=2),
          "sync_status.json",
      )
  ```
  with a `fastapi_client` fixture:
  ```python
  @pytest.fixture
  def fastapi_client():
      from fastapi.testclient import TestClient
      from pyarchinit_mini.api import app  # whichever entry mounts the routers
      return TestClient(app)
  ```

- [ ] In `pyarchinit_mini/api/sync.py`, the `SyncOrchestrator` lives in `pyarchinit_mini/stratigraph/` which is a SURVIVOR. **No bridge swap needed for sync.py — confirmed during discovery.** Mark all 8 sync tests as no-op snapshots: they exist only to guarantee the contract didn't drift while PR-4 was in flight.

- [ ] Run snapshots with `--snapshot-update` once, then assert stability without the flag.

- [ ] Commit:
  ```bash
  git add tests/integration/test_route_contracts.py \
          tests/integration/snapshots/bridge_migration/sync_*.json && \
  git commit -m "test(sync): pin 8 /api/v1/sync/* contracts (stratigraph survivor, no swap)"
  ```

### Task 4.9 — Re-route FastAPI `pyarchinit_mini/api/graphml.py`

- [ ] Snapshot test `POST /api/graphml/convert` (DOT → GraphML). The current implementation calls `pyarchinit_mini.graphml_converter` which is a **survivor** (out of bridge scope). Same as Task 4.8 — pin the contract, do not swap.

- [ ] Commit:
  ```bash
  git add tests/integration/test_route_contracts.py \
          tests/integration/snapshots/bridge_migration/graphml_convert.json && \
  git commit -m "test(graphml): pin /api/graphml/convert contract (graphml_converter survivor)"
  ```

### Task 4.10 — Run the full PR-4 suite + cleanup

- [ ] Full test run:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && pytest -x --ignore=archive_local
  ```
  Expected: all passed; no contracts drifted.

- [ ] If the audit report (PR-1) flagged any route NOT covered in Tasks 4.2–4.9, the executor adds a parallel task with the snapshot-then-swap pattern. No commit unless additional routes were swapped.

---

## PR-5 — Delete legacy modules

**Goal:** Physical deletion of the 14 files identified in Q3. Survivors untouched. Verify zero remaining imports.

### Task 5.1 — Delete the 10 `graphproj/` files

- [ ] Run:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  rm pyarchinit_mini/graphproj/projector.py \
     pyarchinit_mini/graphproj/ingestor.py \
     pyarchinit_mini/graphproj/graph_to_db.py \
     pyarchinit_mini/graphproj/paradata_store.py \
     pyarchinit_mini/graphproj/edge_registry.py \
     pyarchinit_mini/graphproj/graphml_writer.py \
     pyarchinit_mini/graphproj/graphml_reader.py \
     pyarchinit_mini/graphproj/rapporti_codec.py \
     pyarchinit_mini/graphproj/s3d_projector.py \
     pyarchinit_mini/graphproj/s3d_to_cytoscape.py
  ```
  Expected: 10 files removed; survivors `heriverse_parser.py`, `auto_regen.py`, `ingest_plan.py`, `filesystem.py`, `exceptions.py` still present.

- [ ] Confirm:
  ```bash
  ls /Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/graphproj/*.py
  ```
  Expected output (5 lines, no `__pycache__`):
  ```
  pyarchinit_mini/graphproj/__init__.py
  pyarchinit_mini/graphproj/auto_regen.py
  pyarchinit_mini/graphproj/exceptions.py
  pyarchinit_mini/graphproj/filesystem.py
  pyarchinit_mini/graphproj/heriverse_parser.py
  pyarchinit_mini/graphproj/ingest_plan.py
  ```

### Task 5.2 — Delete the 3 `graphml_io/` files

- [ ] Run:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  rm pyarchinit_mini/graphml_io/yed_importer.py \
     pyarchinit_mini/graphml_io/yed_writer.py \
     pyarchinit_mini/graphml_io/yed_keys.py
  ```
  Expected: 3 files removed; survivors `reader.py`, `writer.py` still present.

- [ ] Confirm:
  ```bash
  ls /Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/graphml_io/*.py
  ```
  Expected (3 lines):
  ```
  pyarchinit_mini/graphml_io/__init__.py
  pyarchinit_mini/graphml_io/reader.py
  pyarchinit_mini/graphml_io/writer.py
  ```

### Task 5.3 — Delete the 1 `s3d_integration/` file

- [ ] Run:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  rm pyarchinit_mini/s3d_integration/s3d_converter.py
  ```
  Expected: file removed; survivor `model_manager.py` still present.

- [ ] Confirm:
  ```bash
  ls /Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/s3d_integration/*.py
  ```
  Expected (2 lines):
  ```
  pyarchinit_mini/s3d_integration/__init__.py
  pyarchinit_mini/s3d_integration/model_manager.py
  ```

### Task 5.4 — Prune dead re-exports in surviving `__init__.py` files

- [ ] Open `/Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/graphproj/__init__.py` and remove any line that re-exports a now-deleted module (e.g. `from .projector import ...`, `from .ingestor import ...`).

- [ ] Repeat for `/Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/graphml_io/__init__.py` and `/Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/s3d_integration/__init__.py`.

- [ ] Verify imports still work:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  python -c "import pyarchinit_mini.graphproj, pyarchinit_mini.graphml_io, pyarchinit_mini.s3d_integration"
  ```
  Expected: silent exit 0.

### Task 5.5 — Verify 0 residual imports of deleted modules

- [ ] Run a hard-fail grep:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  set -e; \
  for mod in projector ingestor graph_to_db paradata_store edge_registry \
             graphml_writer graphml_reader rapporti_codec s3d_projector \
             s3d_to_cytoscape; do \
      if grep -rln "from pyarchinit_mini.graphproj.$mod\|import pyarchinit_mini.graphproj.$mod" \
              pyarchinit_mini tests scripts 2>/dev/null; then \
          echo "RESIDUAL: pyarchinit_mini.graphproj.$mod" >&2; exit 1; \
      fi; \
  done; \
  for mod in yed_importer yed_writer yed_keys; do \
      if grep -rln "from pyarchinit_mini.graphml_io.$mod\|import pyarchinit_mini.graphml_io.$mod" \
              pyarchinit_mini tests scripts 2>/dev/null; then \
          echo "RESIDUAL: pyarchinit_mini.graphml_io.$mod" >&2; exit 1; \
      fi; \
  done; \
  if grep -rln "from pyarchinit_mini.s3d_integration.s3d_converter\|import pyarchinit_mini.s3d_integration.s3d_converter" \
          pyarchinit_mini tests scripts 2>/dev/null; then \
      echo "RESIDUAL: pyarchinit_mini.s3d_integration.s3d_converter" >&2; exit 1; \
  fi; \
  echo "OK — 0 residual imports across 14 modules"
  ```
  Expected: final line `OK — 0 residual imports across 14 modules`; exit code 0.

### Task 5.6 — Full test suite green after deletions

- [ ] Run:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && pytest -x --ignore=archive_local
  ```
  Expected: all passed (includes the snapshot tests from PR-4).

### Task 5.7 — PR-5 single commit

- [ ] Commit:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add -A pyarchinit_mini/graphproj/ pyarchinit_mini/graphml_io/ pyarchinit_mini/s3d_integration/ && \
  git commit -m "feat(bridge-migration)!: PR-5 delete 14 legacy modules superseded by pyarchinit-s3dgraphy-bridge==1.0.0"
  ```
  Expected: commit shows 14 deletions plus `__init__.py` prunings; `git log -1 --stat | tail` lists all deleted files.

---

## PR-6 — CHANGELOG + tag `3.0.0-bridge-migration`

**Goal:** Bilingual CHANGELOG entry, version bump in `pyproject.toml`, annotated tag pushed.

### Task 6.1 — Bilingual CHANGELOG entry

- [ ] Open `/Users/enzo/pyarchinit-mini-desk/CHANGELOG.md`. Insert at the top (under the title heading) the bilingual entry:
  ```markdown
  ## [3.0.0-bridge-migration] — 2026-MM-DD

  ### IT — Italiano

  - **BREAKING**: Rimossi i 14 moduli legacy (`graphproj/projector|ingestor|...`, `graphml_io/yed_*`, `s3d_integration/s3d_converter`). La logica di sync s3dgraphy ora vive nel pacchetto PyPI `pyarchinit-s3dgraphy-bridge==1.0.0`.
  - Aggiunti 5 adapter Flask-side in `pyarchinit_mini/bridge_adapter/` che implementano i Protocol del bridge (`DbSession`, `Workspace`, `Settings`, `FileProvider`, `Logger`).
  - Le route Flask e FastAPI sono state ricablate per usare il bridge. I contratti REST sono preservati byte-identico (snapshot test in `tests/integration/test_route_contracts.py`).
  - Aggiunto `scripts/audit_legacy_imports.py` per verificare gli import legacy (output in `docs/audit/2026-05-20-bridge-migration-impact.md`).
  - Aggiunto target Makefile `dev-install-bridge` per installazione editable locale del bridge.
  - I superstiti (mini-desk specifici, fuori scope del bridge) sono **invariati**: `graphproj/heriverse_parser|auto_regen|ingest_plan|filesystem`, tutto `stratigraph/`, tutto `graphml_converter/`.

  ### EN — English

  - **BREAKING**: Removed the 14 legacy modules (`graphproj/projector|ingestor|...`, `graphml_io/yed_*`, `s3d_integration/s3d_converter`). The s3dgraphy sync logic now lives in the PyPI package `pyarchinit-s3dgraphy-bridge==1.0.0`.
  - Added 5 Flask-side adapters in `pyarchinit_mini/bridge_adapter/` implementing the bridge Protocols (`DbSession`, `Workspace`, `Settings`, `FileProvider`, `Logger`).
  - Flask and FastAPI routes rewired through the bridge. REST contracts preserved byte-identical (snapshot tests in `tests/integration/test_route_contracts.py`).
  - Added `scripts/audit_legacy_imports.py` to verify legacy imports (output in `docs/audit/2026-05-20-bridge-migration-impact.md`).
  - Added Makefile target `dev-install-bridge` for local editable install of the bridge.
  - Survivors (mini-desk-specific, out of bridge scope) are **untouched**: `graphproj/heriverse_parser|auto_regen|ingest_plan|filesystem`, all of `stratigraph/`, all of `graphml_converter/`.
  ```

- [ ] Bump `version` in `/Users/enzo/pyarchinit-mini-desk/pyproject.toml` to `3.0.0`. Verify:
  ```bash
  grep '^version' /Users/enzo/pyarchinit-mini-desk/pyproject.toml
  ```
  Expected: `version = "3.0.0"`.

- [ ] Commit:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git add CHANGELOG.md pyproject.toml && \
  git commit -m "release(3.0.0-bridge-migration): bilingual CHANGELOG + version bump"
  ```

### Task 6.2 — Annotated tag, push, CI green

- [ ] Tag and push:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  git tag -a 3.0.0-bridge-migration -m "Bridge migration: 14 legacy modules deleted, routes rewired through pyarchinit-s3dgraphy-bridge==1.0.0" && \
  git push origin HEAD && \
  git push origin 3.0.0-bridge-migration
  ```
  Expected: tag appears on remote; CI run starts on the tagged commit.

- [ ] Verify the CI run is green:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  gh run list --limit 5
  ```
  Expected: the run for the tagged commit shows `completed success`.

- [ ] If a preview deployment exists (Flask preview env per spec), confirm it picked up the tag automatically (no manual step). Otherwise, this task closes the plan.

---

## Self-Review Checklist (AC-INT verification)

Before declaring the migration done, the executor checks each item against the running mini-desk:

- [ ] **AC-INT-1** — The 14 legacy mini-desk files (Q3 list) are physically deleted. Re-run Task 5.5's grep block; expected output `OK — 0 residual imports across 14 modules`.

- [ ] **AC-INT-2** — Every Flask/FastAPI endpoint listed in the PR-1 audit responds with identical JSON shape and status code to pre-migration. Re-run `pytest tests/integration/test_route_contracts.py` without `--snapshot-update`; expected: 100% pass, 0 snapshot drift.

- [ ] **AC-INT-3** — Tag mini-desk `3.0.0-bridge-migration` on `main` with complete bilingual CHANGELOG. Verify: `git tag -l 3.0.0-bridge-migration` returns the tag; `head -40 CHANGELOG.md` shows both `### IT` and `### EN` blocks.

- [ ] **Q3=A invariant 1** — Delete-and-replace (NOT shim re-export). Verify no file in `pyarchinit_mini/graphproj/`, `pyarchinit_mini/graphml_io/`, `pyarchinit_mini/s3d_integration/` is a 1-line `from pyarchinit_s3dgraphy_bridge.X import *` re-export. Run:
  ```bash
  grep -rln "from pyarchinit_s3dgraphy_bridge.* import \*" \
       pyarchinit_mini/graphproj pyarchinit_mini/graphml_io pyarchinit_mini/s3d_integration
  ```
  Expected: 0 results.

- [ ] **Q3=A invariant 2** — Flask audit script committed and reproducible. Run:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  python scripts/audit_legacy_imports.py | diff - docs/audit/2026-05-20-bridge-migration-impact.md
  ```
  Expected: the only diff is the trailing manual-review checklist appended in Task 1.7 (which is intentional and committed).

- [ ] **Q3=A invariant 3** — Bridge installed but no Qt/Flask leakage into the bridge call sites. Run:
  ```bash
  cd /Users/enzo/pyarchinit-mini-desk && \
  python -c "
  import pyarchinit_s3dgraphy_bridge, sys
  before = set(sys.modules)
  from pyarchinit_s3dgraphy_bridge import graph_projector  # arbitrary bridge entry
  after = set(sys.modules) - before
  leaked = [m for m in after if m.startswith(('flask','PyQt','qgis'))]
  assert not leaked, f'bridge leaked GUI deps: {leaked}'
  print('OK — bridge stays pure')
  "
  ```
  Expected: final line `OK — bridge stays pure`.

If all 6 boxes are ticked, the mini-desk migration is **complete** and ready for the plugin-side migration plan (Plan 3) to begin.