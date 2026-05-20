# Bridge v1.0 — Repo Bootstrap + 16-Module Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap the `pyarchinit-s3dgraphy-bridge` repo and ship v1.0 to PyPI with 16 ported modules, AC-2 byte-identical golden suite, and a 9-cell CI matrix.

**Architecture:** New standalone Python package with src/ layout. Public API is 5 typing.Protocol classes (DbSession, Workspace, Settings, FileProvider, Logger) + 16 modules vendored from `pyarchinit/modules/s3dgraphy/sync/`. Zero Qt/Flask dependencies.

**Tech Stack:** Python 3.11+, pyproject.toml (hatchling), SQLAlchemy, lxml, pytest, GitHub Actions, PyPI Trusted Publishing.

**Spec reference:** [`docs/superpowers/specs/2026-05-20-s3dgraphy-bridge-design.md`](../specs/2026-05-20-s3dgraphy-bridge-design.md)

---

## Conventions used in this plan

- **Plugin source root** (read-only during the port): `"/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"` — abbreviated below as `$PLUGIN`.
- **Bridge repo root** (created in Task 1): `~/dev/pyarchinit-s3dgraphy-bridge` — abbreviated below as `$BRIDGE`.
- All `cp` and `cd` commands assume `$PLUGIN` and `$BRIDGE` are exported in the executor shell:

```bash
export PLUGIN="/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
export BRIDGE="$HOME/dev/pyarchinit-s3dgraphy-bridge"
```

- **TDD loop per port task:** copy file → audit Qt/Flask imports → patch any offender to a Protocol call → copy adapted test → run only that test (expect PASS) → commit. The "expect FAIL first" idiom is satisfied by running the test BEFORE the copy — the test errors with `ModuleNotFoundError` until the source file lands.
- **Transitive helpers** (3 modules NOT in the 16-list but pulled in by them): `_workspace.py`, `conflict_resolver.py`, `ingest_result.py`, `vocab_provider_core.py`. These are ported as part of the task that first needs them, with a comment in the commit message marking them as "transitive helper, not in MVP-16".

---

### Task 1: Bootstrap repo skeleton

**Files:**
- Create: `$BRIDGE/.git/` (via `git init`)
- Create: `$BRIDGE/.gitignore`
- Create: `$BRIDGE/README.md`
- Create: `$BRIDGE/LICENSE`

- [ ] **Step 1: Create the repo directory and init git**

```bash
mkdir -p "$BRIDGE"
cd "$BRIDGE"
git init -b main
git config user.email "enzo.ccc@gmail.com"
git config user.name "enzo"
```

Expected: `Initialized empty Git repository in /Users/enzo/dev/pyarchinit-s3dgraphy-bridge/.git/`

- [ ] **Step 2: Write `.gitignore`**

```
# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
build/
dist/
.coverage
.coverage.*
htmlcov/
.tox/
.nox/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Virtualenvs
.venv/
venv/
env/

# IDE / OS
.idea/
.vscode/
.DS_Store

# CI artifacts
*.log
```

Write to `$BRIDGE/.gitignore`.

- [ ] **Step 3: Write `LICENSE` (GPL v2, same as plugin)**

Copy the GPL v2 text from `$PLUGIN/LICENSE` (or fetch from `https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt`):

```bash
cp "$PLUGIN/LICENSE" "$BRIDGE/LICENSE" 2>/dev/null \
  || curl -fsSL https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt -o "$BRIDGE/LICENSE"
test -s "$BRIDGE/LICENSE" && echo "LICENSE present"
```

Expected: `LICENSE present`

- [ ] **Step 4: Write minimal `README.md`**

```markdown
# pyarchinit-s3dgraphy-bridge

Vendored shared package that implements the yEd ↔ DB ↔ GraphML sync logic used by
both the [PyArchInit QGIS plugin](https://github.com/pyarchinit/pyarchinit) and
[pyarchinit-mini-desk](https://github.com/pyarchinit/pyarchinit-mini-desk).

- **License:** GPL v2 (same as the plugin)
- **Python:** 3.11+
- **Public API:** 5 `typing.Protocol` classes (`DbSession`, `Workspace`,
  `Settings`, `FileProvider`, `Logger`) — see [`PUBLIC_API.md`](PUBLIC_API.md).
- **Install:** `pip install pyarchinit-s3dgraphy-bridge`

See `CHANGELOG.md` for release notes.
```

Write to `$BRIDGE/README.md`.

- [ ] **Step 5: First commit**

```bash
cd "$BRIDGE"
git add .gitignore LICENSE README.md
git commit -m "chore(bootstrap): repo skeleton (gitignore + GPL v2 + README)"
```

Expected: `1 file changed` style output, no errors.

---

### Task 2: pyproject.toml + src/ layout

**Files:**
- Create: `$BRIDGE/pyproject.toml`
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/__init__.py`
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/py.typed`
- Create: `$BRIDGE/MANIFEST.in`
- Create: `$BRIDGE/CHANGELOG.md`

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling>=1.21"]
build-backend = "hatchling.build"

[project]
name = "pyarchinit-s3dgraphy-bridge"
version = "1.0.0"
description = "Shared yEd <-> DB <-> GraphML sync logic for pyarchinit (plugin + mini-desk)"
readme = "README.md"
license = { file = "LICENSE" }
requires-python = ">=3.11"
authors = [
  { name = "PyArchInit team", email = "enzo.ccc@gmail.com" },
]
keywords = ["archaeology", "graphml", "yed", "harris-matrix", "pyarchinit"]
classifiers = [
  "Development Status :: 5 - Production/Stable",
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
  "Operating System :: OS Independent",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Topic :: Scientific/Engineering",
]
dependencies = [
  "sqlalchemy>=2.0,<3",
  "lxml>=4.9,<6",
]

[project.optional-dependencies]
dev = [
  "pytest>=7.4",
  "pytest-cov>=4.1",
  "pytest-xdist>=3.5",
  "mypy>=1.8",
  "ruff>=0.4",
  "build>=1.0",
]

[project.urls]
Homepage = "https://github.com/pyarchinit/pyarchinit-s3dgraphy-bridge"
Source = "https://github.com/pyarchinit/pyarchinit-s3dgraphy-bridge"
Issues = "https://github.com/pyarchinit/pyarchinit-s3dgraphy-bridge/issues"
Changelog = "https://github.com/pyarchinit/pyarchinit-s3dgraphy-bridge/blob/main/CHANGELOG.md"

[tool.hatch.build.targets.wheel]
packages = ["src/pyarchinit_s3dgraphy_bridge"]

[tool.hatch.build.targets.sdist]
include = [
  "src/pyarchinit_s3dgraphy_bridge",
  "tests",
  "README.md",
  "LICENSE",
  "CHANGELOG.md",
  "PUBLIC_API.md",
]

[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
addopts = "-ra --strict-markers"
markers = [
  "slow: AC-2 golden suite (heavy, tag-only)",
]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.mypy]
python_version = "3.11"
strict = true
files = ["src/pyarchinit_s3dgraphy_bridge"]
```

Write to `$BRIDGE/pyproject.toml`.

- [ ] **Step 2: Create the src/ package directory**

```bash
mkdir -p "$BRIDGE/src/pyarchinit_s3dgraphy_bridge"
mkdir -p "$BRIDGE/tests"
touch "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/py.typed"
```

- [ ] **Step 3: Write the package `__init__.py`**

```python
"""pyarchinit-s3dgraphy-bridge — vendored yEd <-> DB <-> GraphML sync layer.

Public API: 5 typing.Protocol classes (DbSession, Workspace, Settings,
FileProvider, Logger) + 16 vendored modules. See PUBLIC_API.md.
"""

from __future__ import annotations

__version__ = "1.0.0"

__all__ = ["__version__"]
```

Write to `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/__init__.py`.

- [ ] **Step 4: Write `MANIFEST.in`**

```
include README.md
include LICENSE
include CHANGELOG.md
include PUBLIC_API.md
recursive-include src/pyarchinit_s3dgraphy_bridge py.typed
recursive-include tests *.py *.graphml *.sqlite *.json
```

Write to `$BRIDGE/MANIFEST.in`.

- [ ] **Step 5: Write `CHANGELOG.md` stub**

```markdown
# Changelog

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), SemVer.

## [Unreleased]

### Added

- Initial repo skeleton (pyproject.toml, src/ layout, GPL v2 LICENSE).
```

Write to `$BRIDGE/CHANGELOG.md`.

- [ ] **Step 6: Verify the package is import-clean in a fresh venv**

```bash
cd "$BRIDGE"
python3.11 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
python -c "import pyarchinit_s3dgraphy_bridge; print(pyarchinit_s3dgraphy_bridge.__version__)"
```

Expected: `1.0.0`

- [ ] **Step 7: Commit**

```bash
cd "$BRIDGE"
git add pyproject.toml MANIFEST.in CHANGELOG.md src/
git commit -m "chore(bootstrap): pyproject + src layout + empty package importable"
```

---

### Task 3: pre-commit + dev tooling

**Files:**
- Create: `$BRIDGE/.pre-commit-config.yaml`
- Create: `$BRIDGE/Makefile`

- [ ] **Step 1: Write `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
        args: [--maxkb=500]
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.10
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: local
    hooks:
      - id: no-qt-flask-imports
        name: "Bridge guard: zero Qt/Flask/QGIS imports in src/"
        entry: bash -c 'if grep -RnE "^(import|from) (PyQt|qgis|flask)" src/; then echo "FAIL: Qt/Flask/QGIS import found in src/" >&2; exit 1; fi'
        language: system
        pass_filenames: false
```

Write to `$BRIDGE/.pre-commit-config.yaml`.

- [ ] **Step 2: Write `Makefile`**

```makefile
.PHONY: install test test-fast cov lint type guard build clean

install:
	pip install -e ".[dev]"

test:
	pytest -v

test-fast:
	pytest -v -m "not slow"

cov:
	pytest --cov=pyarchinit_s3dgraphy_bridge --cov-report=term-missing --cov-report=html

lint:
	ruff check src tests
	ruff format --check src tests

type:
	mypy src

guard:
	@if grep -RnE "^(import|from) (PyQt|qgis|flask)" src/; then \
		echo "FAIL: Qt/Flask/QGIS import found in src/"; exit 1; \
	else echo "OK: zero Qt/Flask/QGIS imports"; fi

build:
	python -m build

clean:
	rm -rf build dist *.egg-info src/*.egg-info .pytest_cache .mypy_cache htmlcov .coverage
```

Write to `$BRIDGE/Makefile`.

- [ ] **Step 3: Install pre-commit hooks**

```bash
cd "$BRIDGE"
. .venv/bin/activate
pip install pre-commit
pre-commit install
pre-commit run --all-files || true   # first run may auto-fix, that's OK
```

Expected: hooks install, possibly one or two auto-fix passes on existing files.

- [ ] **Step 4: Verify the guard fires when armed**

```bash
cd "$BRIDGE"
echo "from PyQt5 import QtCore" > src/pyarchinit_s3dgraphy_bridge/_probe.py
make guard ; rc=$?
rm src/pyarchinit_s3dgraphy_bridge/_probe.py
test "$rc" -ne 0 && echo "GUARD ARMED OK"
```

Expected: `GUARD ARMED OK` (the make target exits non-zero, then we delete the probe).

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add .pre-commit-config.yaml Makefile
git commit -m "chore(bootstrap): pre-commit + Makefile + Qt/Flask import guard"
```

---

### Task 4: tests/ directory + conftest skeleton

**Files:**
- Create: `$BRIDGE/tests/__init__.py`
- Create: `$BRIDGE/tests/conftest.py`
- Create: `$BRIDGE/tests/fixtures/.gitkeep`

- [ ] **Step 1: Create tests directory layout**

```bash
mkdir -p "$BRIDGE/tests/fixtures"
touch "$BRIDGE/tests/__init__.py"
touch "$BRIDGE/tests/fixtures/.gitkeep"
```

- [ ] **Step 2: Write `tests/conftest.py` with the 5 mock Protocol fixtures**

```python
"""Shared fixtures for the bridge test suite.

Mocks that implement each of the 5 Protocols so unit tests don't need
the plugin or mini-desk to be installed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


class _MockDbSession:
    """In-memory SQLite DbSession for unit tests."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._conn = engine.connect()
        self.is_postgres = False

    def execute(self, sql: str, params: dict | None = None):
        return self._conn.execute(text(sql), params or {})

    def commit(self) -> None:
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


class _MockWorkspace:
    def __init__(self, root: Path) -> None:
        self.root = root

    def tmp(self) -> Path:
        d = self.root / "tmp"
        d.mkdir(parents=True, exist_ok=True)
        return d


class _MockSettings:
    def __init__(self, data: dict | None = None) -> None:
        self._data = data or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)


class _MockFileProvider:
    def __init__(self, root: Path) -> None:
        self.root = root

    def read_bytes(self, ref: str) -> bytes:
        return (self.root / ref).read_bytes()


class _MockLogger:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def info(self, msg: str) -> None:
        self.messages.append(("info", msg))

    def warn(self, msg: str) -> None:
        self.messages.append(("warn", msg))

    def error(self, msg: str, exc: Exception | None = None) -> None:
        self.messages.append(("error", msg))


@pytest.fixture
def mock_workspace(tmp_path: Path) -> _MockWorkspace:
    return _MockWorkspace(tmp_path)


@pytest.fixture
def mock_settings() -> _MockSettings:
    return _MockSettings()


@pytest.fixture
def mock_logger() -> _MockLogger:
    return _MockLogger()


@pytest.fixture
def mock_file_provider(tmp_path: Path) -> _MockFileProvider:
    return _MockFileProvider(tmp_path)


@pytest.fixture
def mock_db_session() -> _MockDbSession:
    engine = create_engine("sqlite:///:memory:", future=True)
    session = _MockDbSession(engine)
    yield session
    session.close()
```

Write to `$BRIDGE/tests/conftest.py`.

- [ ] **Step 3: Smoke-test the fixtures**

```bash
cd "$BRIDGE"
. .venv/bin/activate
cat > /tmp/_smoke.py <<'PY'
import subprocess, sys
r = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q"], cwd=".", capture_output=True, text=True)
print(r.stdout, r.stderr); sys.exit(r.returncode)
PY
python /tmp/_smoke.py
rm /tmp/_smoke.py
```

Expected: `no tests ran` (collect-only with 0 tests is fine).

- [ ] **Step 4: Commit**

```bash
cd "$BRIDGE"
git add tests/
git commit -m "test(bootstrap): conftest with mock fixtures for the 5 Protocols"
```

---

### Task 5: Empty placeholder for Protocols + first import test

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/protocols.py`
- Create: `$BRIDGE/tests/test_protocols_import.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_protocols_import.py
def test_protocols_module_imports():
    from pyarchinit_s3dgraphy_bridge import protocols
    assert protocols is not None
```

Write to `$BRIDGE/tests/test_protocols_import.py`.

- [ ] **Step 2: Run the failing test**

```bash
cd "$BRIDGE"
. .venv/bin/activate
pytest tests/test_protocols_import.py -v
```

Expected: `ModuleNotFoundError: No module named 'pyarchinit_s3dgraphy_bridge.protocols'`.

- [ ] **Step 3: Write the empty module**

```python
"""Public API: Protocol contracts for the 5 host-side seams.

This file is filled in by Tasks 6-10. Right now it is intentionally empty
so the import test in Task 5 passes.
"""

from __future__ import annotations
```

Write to `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/protocols.py`.

- [ ] **Step 4: Re-run the test**

```bash
cd "$BRIDGE"
pytest tests/test_protocols_import.py -v
```

Expected: `1 passed`.

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/protocols.py tests/test_protocols_import.py
git commit -m "feat(protocols): empty module + import smoke test (TDD scaffold)"
```

---

### Task 6: Protocol — `DbSession`

**Files:**
- Modify: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/protocols.py`
- Create: `$BRIDGE/tests/test_protocol_dbsession.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_protocol_dbsession.py
from pyarchinit_s3dgraphy_bridge.protocols import DbSession


def test_mock_satisfies_dbsession(mock_db_session):
    assert isinstance(mock_db_session, DbSession)


def test_dbsession_execute_and_commit(mock_db_session):
    mock_db_session.execute("CREATE TABLE t(id INTEGER)")
    mock_db_session.execute("INSERT INTO t(id) VALUES (:v)", {"v": 42})
    mock_db_session.commit()
    row = mock_db_session.execute("SELECT id FROM t").fetchone()
    assert row[0] == 42


def test_dbsession_is_postgres_flag(mock_db_session):
    assert mock_db_session.is_postgres is False
```

Write to `$BRIDGE/tests/test_protocol_dbsession.py`.

- [ ] **Step 2: Run — expect FAIL with ImportError**

```bash
cd "$BRIDGE" && pytest tests/test_protocol_dbsession.py -v
```

Expected: `ImportError: cannot import name 'DbSession' from 'pyarchinit_s3dgraphy_bridge.protocols'`.

- [ ] **Step 3: Add the `DbSession` Protocol**

Append to `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/protocols.py`:

```python
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class DbSession(Protocol):
    """Database session contract.

    Implementations:
      - Plugin: `QgisDbSession` wraps `sqlite3.Connection` or `psycopg2.connection`.
      - Mini-desk: `SqlalchemyDbSession` wraps a SQLAlchemy `Session`.
    """

    is_postgres: bool

    def execute(self, sql: str, params: dict | None = None) -> Any:
        ...

    def commit(self) -> None:
        ...
```

- [ ] **Step 4: Run — expect PASS**

```bash
cd "$BRIDGE" && pytest tests/test_protocol_dbsession.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/protocols.py tests/test_protocol_dbsession.py
git commit -m "feat(protocols): add DbSession (execute/commit/is_postgres)"
```

---

### Task 7: Protocol — `Workspace`

**Files:**
- Modify: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/protocols.py`
- Create: `$BRIDGE/tests/test_protocol_workspace.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_protocol_workspace.py
from pathlib import Path
from pyarchinit_s3dgraphy_bridge.protocols import Workspace


def test_mock_satisfies_workspace(mock_workspace):
    assert isinstance(mock_workspace, Workspace)


def test_workspace_tmp_returns_existing_dir(mock_workspace):
    t = mock_workspace.tmp()
    assert isinstance(t, Path)
    assert t.is_dir()


def test_workspace_root_is_path(mock_workspace):
    assert isinstance(mock_workspace.root, Path)
```

- [ ] **Step 2: Run — expect ImportError**

```bash
cd "$BRIDGE" && pytest tests/test_protocol_workspace.py -v
```

- [ ] **Step 3: Add `Workspace` to `protocols.py`**

Append:

```python
from pathlib import Path


@runtime_checkable
class Workspace(Protocol):
    """Per-site workspace directory contract.

    `root` is the on-disk root for paradata SVGs and group folders.
    `tmp()` returns a scratch directory the bridge may write to freely.
    """

    root: Path

    def tmp(self) -> Path:
        ...
```

- [ ] **Step 4: Run — expect PASS**

```bash
cd "$BRIDGE" && pytest tests/test_protocol_workspace.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/protocols.py tests/test_protocol_workspace.py
git commit -m "feat(protocols): add Workspace (root/tmp)"
```

---

### Task 8: Protocol — `Settings`

**Files:**
- Modify: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/protocols.py`
- Create: `$BRIDGE/tests/test_protocol_settings.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_protocol_settings.py
from pyarchinit_s3dgraphy_bridge.protocols import Settings
from tests.conftest import _MockSettings


def test_mock_satisfies_settings(mock_settings):
    assert isinstance(mock_settings, Settings)


def test_settings_get_default():
    s = _MockSettings({"a": 1})
    assert s.get("a") == 1
    assert s.get("missing", "fallback") == "fallback"
```

- [ ] **Step 2: Run — expect ImportError**

```bash
cd "$BRIDGE" && pytest tests/test_protocol_settings.py -v
```

- [ ] **Step 3: Add `Settings` to `protocols.py`**

Append:

```python
@runtime_checkable
class Settings(Protocol):
    """Key-value settings store.

    Plugin: `QSettingsProxy` wraps `QSettings("pyarchinit")`.
    Mini-desk: `AppSettingProxy` wraps the `AppSetting` SQLAlchemy model.
    """

    def get(self, key: str, default: Any = None) -> Any:
        ...
```

- [ ] **Step 4: Run — expect PASS**

```bash
cd "$BRIDGE" && pytest tests/test_protocol_settings.py -v
```

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/protocols.py tests/test_protocol_settings.py
git commit -m "feat(protocols): add Settings (get with default)"
```

---

### Task 9: Protocol — `FileProvider`

**Files:**
- Modify: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/protocols.py`
- Create: `$BRIDGE/tests/test_protocol_fileprovider.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_protocol_fileprovider.py
from pyarchinit_s3dgraphy_bridge.protocols import FileProvider


def test_mock_satisfies_fileprovider(mock_file_provider):
    assert isinstance(mock_file_provider, FileProvider)


def test_fileprovider_read_bytes(tmp_path, mock_file_provider):
    p = tmp_path / "hello.txt"
    p.write_bytes(b"hi")
    assert mock_file_provider.read_bytes("hello.txt") == b"hi"
```

- [ ] **Step 2: Run — expect ImportError**

```bash
cd "$BRIDGE" && pytest tests/test_protocol_fileprovider.py -v
```

- [ ] **Step 3: Add `FileProvider` to `protocols.py`**

Append:

```python
@runtime_checkable
class FileProvider(Protocol):
    """Read raw bytes from a host-defined reference.

    `ref` is opaque to the bridge: the plugin uses local filesystem paths,
    mini-desk uses upload-ids resolved by its `MediaService`.
    """

    def read_bytes(self, ref: str) -> bytes:
        ...
```

- [ ] **Step 4: Run — expect PASS**

```bash
cd "$BRIDGE" && pytest tests/test_protocol_fileprovider.py -v
```

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/protocols.py tests/test_protocol_fileprovider.py
git commit -m "feat(protocols): add FileProvider (opaque ref -> bytes)"
```

---

### Task 10: Protocol — `Logger`

**Files:**
- Modify: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/protocols.py`
- Create: `$BRIDGE/tests/test_protocol_logger.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_protocol_logger.py
from pyarchinit_s3dgraphy_bridge.protocols import Logger


def test_mock_satisfies_logger(mock_logger):
    assert isinstance(mock_logger, Logger)


def test_logger_records_each_level(mock_logger):
    mock_logger.info("ok")
    mock_logger.warn("careful")
    mock_logger.error("boom", RuntimeError("x"))
    levels = [m[0] for m in mock_logger.messages]
    assert levels == ["info", "warn", "error"]
```

- [ ] **Step 2: Run — expect ImportError**

```bash
cd "$BRIDGE" && pytest tests/test_protocol_logger.py -v
```

- [ ] **Step 3: Add `Logger` to `protocols.py`**

Append:

```python
@runtime_checkable
class Logger(Protocol):
    """Three-level logging contract.

    Plugin: `QgsLogger` -> `QgsMessageLog.logMessage`.
    Mini-desk: `PythonLogger` -> stdlib `logging.getLogger("bridge")`.
    """

    def info(self, msg: str) -> None: ...
    def warn(self, msg: str) -> None: ...
    def error(self, msg: str, exc: Exception | None = None) -> None: ...
```

- [ ] **Step 4: Run all Protocol tests together**

```bash
cd "$BRIDGE" && pytest tests/test_protocol_*.py -v
```

Expected: `12 passed` (3+3+2+2+2 across the 5 Protocols).

- [ ] **Step 5: Verify `make guard` still clean**

```bash
cd "$BRIDGE" && make guard
```

Expected: `OK: zero Qt/Flask/QGIS imports`.

- [ ] **Step 6: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/protocols.py tests/test_protocol_logger.py
git commit -m "feat(protocols): add Logger (info/warn/error) — 5/5 Protocols complete"
```

---

### Task 11: Port `uuid7`

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/uuid7.py`
- Create: `$BRIDGE/tests/test_uuid7.py`

- [ ] **Step 1: Copy source from plugin**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/uuid7.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/uuid7.py"
```

- [ ] **Step 2: Audit imports — verify no Qt/QGIS/Flask deps**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/uuid7.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 3: Copy and adapt the plugin test**

```bash
cp "$PLUGIN/tests/sync/test_uuid7.py" "$BRIDGE/tests/test_uuid7.py"
sed -i.bak 's|modules\.s3dgraphy\.sync\.uuid7|pyarchinit_s3dgraphy_bridge.uuid7|g' "$BRIDGE/tests/test_uuid7.py"
rm "$BRIDGE/tests/test_uuid7.py.bak"
```

- [ ] **Step 4: Run the test**

```bash
cd "$BRIDGE" && pytest tests/test_uuid7.py -v
```

Expected: all tests pass (number depends on plugin source; should match plugin output for this file).

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/uuid7.py tests/test_uuid7.py
git commit -m "port(uuid7): vendored from pyarchinit, no Qt deps"
```

---

### Task 12: Port `vocab_types`

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/vocab_types.py`
- Create: `$BRIDGE/tests/test_vocab_types.py`

- [ ] **Step 1: Copy source**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/vocab_types.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/vocab_types.py"
```

- [ ] **Step 2: Audit**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/vocab_types.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 3: Copy + adapt test**

```bash
cp "$PLUGIN/tests/sync/test_vocab_types.py" "$BRIDGE/tests/test_vocab_types.py"
sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/test_vocab_types.py"
rm "$BRIDGE/tests/test_vocab_types.py.bak"
```

- [ ] **Step 4: Run**

```bash
cd "$BRIDGE" && pytest tests/test_vocab_types.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/vocab_types.py tests/test_vocab_types.py
git commit -m "port(vocab_types): vendored from pyarchinit, pure dataclasses"
```

---

### Task 13: Port `edge_registry`

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/edge_registry.py`
- Create: `$BRIDGE/tests/test_edge_registry.py`

- [ ] **Step 1: Copy source**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/edge_registry.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/edge_registry.py"
```

- [ ] **Step 2: Audit imports**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/edge_registry.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 3: Copy + adapt test**

```bash
cp "$PLUGIN/tests/sync/test_edge_registry.py" "$BRIDGE/tests/test_edge_registry.py"
sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/test_edge_registry.py"
rm "$BRIDGE/tests/test_edge_registry.py.bak"
```

- [ ] **Step 4: Run**

```bash
cd "$BRIDGE" && pytest tests/test_edge_registry.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/edge_registry.py tests/test_edge_registry.py
git commit -m "port(edge_registry): vendored from pyarchinit"
```

---

### Task 14: Port `_db_handle`

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/_db_handle.py`
- Create: `$BRIDGE/tests/test_db_handle.py`

- [ ] **Step 1: Copy source**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/_db_handle.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/_db_handle.py"
```

- [ ] **Step 2: Audit — `_db_handle` is already Qt-free per plugin audit**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/_db_handle.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 3: Copy the shim test (plugin file is `test_db_handle_shim.py`)**

```bash
cp "$PLUGIN/tests/sync/test_db_handle_shim.py" "$BRIDGE/tests/test_db_handle.py"
sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/test_db_handle.py"
rm "$BRIDGE/tests/test_db_handle.py.bak"
```

- [ ] **Step 4: Run**

```bash
cd "$BRIDGE" && pytest tests/test_db_handle.py -v
```

Expected: all pass (in-memory SQLite handle constructions).

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/_db_handle.py tests/test_db_handle.py
git commit -m "port(_db_handle): vendored DbHandle + resolver + _columns_of"
```

---

### Task 15: Port `vocab_provider` (+ transitive `vocab_provider_core`)

**Note:** plugin's `vocab_provider.py` lazy-imports `qgis.PyQt.QtCore` inside a `try:` block for its file-watcher. The bridge must strip that branch and rely on the `Settings` Protocol if the watcher behavior is needed by a consumer (it isn't, for MVP). `vocab_provider_core.py` is a Qt-free pure-Python helper that ships as a transitive dep.

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/vocab_provider_core.py`
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/vocab_provider.py`
- Create: `$BRIDGE/tests/test_vocab_provider_core.py`
- Create: `$BRIDGE/tests/test_vocab_provider.py`

- [ ] **Step 1: Copy `vocab_provider_core` (transitive helper, Qt-free)**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/vocab_provider_core.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/vocab_provider_core.py"
grep -nE "^(import|from) (PyQt|qgis|flask)" "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/vocab_provider_core.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 2: Copy `vocab_provider` source**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/vocab_provider.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/vocab_provider.py"
```

- [ ] **Step 3: Strip the `qgis.PyQt` block**

Open `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/vocab_provider.py` and replace the `try: from qgis.PyQt.QtCore import QFileSystemWatcher, QObject, pyqtSignal ... except ImportError: ...` block (around the top of the file per plugin layout) with:

```python
# Bridge: the QGIS-specific QFileSystemWatcher is NOT vendored.
# Consumers that want hot-reload of the YAML vocab files should wire it
# at the host layer and call VocabProvider.reload() themselves.
QFileSystemWatcher = None  # type: ignore[assignment]
QObject = object  # type: ignore[assignment,misc]
pyqtSignal = None  # type: ignore[assignment]
```

Then locate any class that previously inherited `QObject` and change it to inherit `object`. Locate any `pyqtSignal(...)` declarations and replace each with a stub: `def _noop_signal(*a, **k): pass`.

- [ ] **Step 4: Audit — verify the strip succeeded**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/vocab_provider.py" \
  && (echo "FAIL: still has Qt imports" && exit 1) || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 5: Copy + adapt both tests**

```bash
cp "$PLUGIN/tests/sync/test_vocab_provider_core.py" "$BRIDGE/tests/test_vocab_provider_core.py"
cp "$PLUGIN/tests/sync/test_vocab_provider_smoke.py" "$BRIDGE/tests/test_vocab_provider.py"
sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/test_vocab_provider_core.py" "$BRIDGE/tests/test_vocab_provider.py"
rm "$BRIDGE/tests/test_vocab_provider_core.py.bak" "$BRIDGE/tests/test_vocab_provider.py.bak"
```

- [ ] **Step 6: Run both tests**

```bash
cd "$BRIDGE" && pytest tests/test_vocab_provider_core.py tests/test_vocab_provider.py -v
```

Expected: all pass. If a test exercises the file-watcher specifically, skip it with `pytest.mark.skip(reason="watcher not vendored, use Settings Protocol")`.

- [ ] **Step 7: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/vocab_provider.py \
        src/pyarchinit_s3dgraphy_bridge/vocab_provider_core.py \
        tests/test_vocab_provider.py tests/test_vocab_provider_core.py
git commit -m "port(vocab_provider): strip QFileSystemWatcher, vendor core too"
```

---

### Task 16: Port `_workspace` (transitive helper for paradata_store)

**Note:** `_workspace.py` is NOT in the 16-module MVP list, but `paradata_store.py` imports `_resolve_workspace_dir` from it. It must be ported first, stripping the `from qgis.PyQt.QtCore import QSettings` block in favor of a `Settings` Protocol injection point.

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/_workspace.py`
- Create: `$BRIDGE/tests/test_workspace_root.py`

- [ ] **Step 1: Copy source**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/_workspace.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/_workspace.py"
```

- [ ] **Step 2: Locate the `QSettings` import block (per plugin grep, line ~)**

```bash
grep -nE "qgis|QSettings" "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/_workspace.py"
```

Expected: 1-2 lines pointing at a `from qgis.PyQt.QtCore import QSettings` block (typically inside a `try:` guard).

- [ ] **Step 3: Replace the QSettings branch with a Protocol-friendly signature**

In `_workspace.py`, find `_resolve_workspace_dir(handle, sito)` and change its signature to:

```python
def _resolve_workspace_dir(handle, sito, settings=None):
    """Resolve the per-site workspace root.

    Bridge change vs plugin: `settings` is an optional Settings Protocol
    implementation. If None, falls back to the env var
    PYARCHINIT_WORKSPACE_ROOT, then to ~/pyarchinit_workspace.
    The plugin's QSettings("pyarchinit/workspace_root") branch is
    NOT vendored — wire it from the host via the Settings Protocol.
    """
    import os
    from pathlib import Path

    if settings is not None:
        root = settings.get("workspace_root", None)
        if root:
            return Path(root) / sito

    root = os.environ.get("PYARCHINIT_WORKSPACE_ROOT")
    if root:
        return Path(root) / sito

    return Path.home() / "pyarchinit_workspace" / sito
```

Delete the entire prior `try: from qgis.PyQt.QtCore import QSettings ... except ImportError: ...` branch.

- [ ] **Step 4: Audit**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/_workspace.py" \
  && (echo "FAIL" && exit 1) || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 5: Copy + adapt the test**

```bash
cp "$PLUGIN/tests/sync/test_workspace_root.py" "$BRIDGE/tests/test_workspace_root.py"
sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/test_workspace_root.py"
rm "$BRIDGE/tests/test_workspace_root.py.bak"
```

Plus add one new test that exercises the new `settings=` parameter:

```python
# Append to tests/test_workspace_root.py
from pyarchinit_s3dgraphy_bridge._workspace import _resolve_workspace_dir


def test_resolve_workspace_dir_uses_settings_when_provided(tmp_path, mock_settings):
    mock_settings._data["workspace_root"] = str(tmp_path)
    out = _resolve_workspace_dir(handle=None, sito="DemoSite", settings=mock_settings)
    assert out == tmp_path / "DemoSite"
```

- [ ] **Step 6: Run**

```bash
cd "$BRIDGE" && pytest tests/test_workspace_root.py -v
```

Expected: all pass. If a plugin test references QSettings explicitly, mark it `pytest.mark.skip`.

- [ ] **Step 7: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/_workspace.py tests/test_workspace_root.py
git commit -m "port(_workspace): transitive helper, QSettings -> Settings Protocol"
```

---

### Task 17: Port `yed_classifier`

**Note:** plugin source uses an absolute import `from modules.s3dgraphy.sync._db_handle import _resolve_db_handle`. The bridge must rewrite this to relative `from ._db_handle import _resolve_db_handle`.

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_classifier.py`
- Create: `$BRIDGE/tests/test_yed_classifier.py`

- [ ] **Step 1: Copy + rewrite the absolute import**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/yed_classifier.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_classifier.py"
sed -i.bak 's|from modules\.s3dgraphy\.sync\._db_handle|from ._db_handle|g' \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_classifier.py"
rm "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_classifier.py.bak"
```

- [ ] **Step 2: Audit**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)|modules\.s3dgraphy" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_classifier.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 3: Copy + adapt tests**

```bash
cp "$PLUGIN/tests/sync/test_yed_classifier.py" "$BRIDGE/tests/test_yed_classifier.py"
sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/test_yed_classifier.py"
rm "$BRIDGE/tests/test_yed_classifier.py.bak"
```

- [ ] **Step 4: Run**

```bash
cd "$BRIDGE" && pytest tests/test_yed_classifier.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/yed_classifier.py tests/test_yed_classifier.py
git commit -m "port(yed_classifier): rewrite absolute -> relative import"
```

---

### Task 18: Port `yed_detector`

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_detector.py`
- Create: `$BRIDGE/tests/test_yed_detector.py`

- [ ] **Step 1: Copy source**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/yed_detector.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_detector.py"
```

- [ ] **Step 2: Audit**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_detector.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 3: Copy + adapt test**

```bash
cp "$PLUGIN/tests/sync/test_yed_detector.py" "$BRIDGE/tests/test_yed_detector.py"
sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/test_yed_detector.py"
rm "$BRIDGE/tests/test_yed_detector.py.bak"
```

- [ ] **Step 4: Run**

```bash
cd "$BRIDGE" && pytest tests/test_yed_detector.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/yed_detector.py tests/test_yed_detector.py
git commit -m "port(yed_detector): vendored, no Qt deps"
```

---

### Task 19: Port `yed_group_walker`

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_group_walker.py`
- Create: `$BRIDGE/tests/test_yed_group_walker.py`

- [ ] **Step 1: Copy source**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/yed_group_walker.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_group_walker.py"
```

- [ ] **Step 2: Audit**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_group_walker.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 3: Copy + adapt test**

```bash
cp "$PLUGIN/tests/sync/test_yed_group_walker.py" "$BRIDGE/tests/test_yed_group_walker.py"
sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/test_yed_group_walker.py"
rm "$BRIDGE/tests/test_yed_group_walker.py.bak"
```

- [ ] **Step 4: Run**

```bash
cd "$BRIDGE" && pytest tests/test_yed_group_walker.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/yed_group_walker.py tests/test_yed_group_walker.py
git commit -m "port(yed_group_walker): vendored, no Qt deps"
```

---

### Task 20: Port `yed_rapporti_policy` (+ transitive `ingest_result`, `conflict_resolver`)

**Note:** `yed_rapporti_policy` imports `CycleDetectedError` from `graph_ingestor`, which is too heavy to port yet. Solution: pull that one class out into a tiny `_errors.py` module FIRST. Plus `ingest_result.py` and `conflict_resolver.py` are transitive deps used by the future `graph_ingestor` port — port them here so the dependency graph stays linear.

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/_errors.py`
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/ingest_result.py`
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/conflict_resolver.py`
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_rapporti_policy.py`
- Create: `$BRIDGE/tests/test_yed_rapporti_policy.py`
- Create: `$BRIDGE/tests/test_ingest_result.py`
- Create: `$BRIDGE/tests/test_conflict_resolver.py`

- [ ] **Step 1: Extract `CycleDetectedError` into `_errors.py`**

```python
# src/pyarchinit_s3dgraphy_bridge/_errors.py
"""Stable exception classes shared across bridge modules.

Extracted from graph_ingestor.py during the port so leaf modules
(yed_rapporti_policy) don't need to import the heavy ingestor module.
"""

from __future__ import annotations


class GraphSyncError(Exception):
    """Base error for all sync failures."""


class CycleDetectedError(GraphSyncError):
    """Raised when ingest would create a cycle in the stratigraphic graph."""


class SchemaMismatchError(GraphSyncError):
    """Raised when DB schema does not match expectations."""
```

Write to `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/_errors.py`.

- [ ] **Step 2: Copy `ingest_result.py` and `conflict_resolver.py`**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/ingest_result.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/ingest_result.py"
cp "$PLUGIN/modules/s3dgraphy/sync/conflict_resolver.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/conflict_resolver.py"
```

- [ ] **Step 3: Copy `yed_rapporti_policy.py` and rewrite the CycleDetectedError import**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/yed_rapporti_policy.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_rapporti_policy.py"
sed -i.bak 's|from \.graph_ingestor import CycleDetectedError|from ._errors import CycleDetectedError|g' \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_rapporti_policy.py"
rm "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_rapporti_policy.py.bak"
```

- [ ] **Step 4: Audit all 4 files**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/_errors.py" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/ingest_result.py" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/conflict_resolver.py" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_rapporti_policy.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 5: Copy + adapt tests**

```bash
cp "$PLUGIN/tests/sync/test_yed_rapporti_policy.py" "$BRIDGE/tests/test_yed_rapporti_policy.py"
cp "$PLUGIN/tests/sync/test_ingest_result.py" "$BRIDGE/tests/test_ingest_result.py"
cp "$PLUGIN/tests/sync/test_conflict_resolver.py" "$BRIDGE/tests/test_conflict_resolver.py"
cp "$PLUGIN/tests/sync/test_rapporti_shorthand_dispatch.py" "$BRIDGE/tests/test_rapporti_shorthand_dispatch.py"
for f in test_yed_rapporti_policy test_ingest_result test_conflict_resolver test_rapporti_shorthand_dispatch; do
  sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/$f.py"
  rm "$BRIDGE/tests/$f.py.bak"
done
```

- [ ] **Step 6: Run all 4 tests**

```bash
cd "$BRIDGE" && pytest tests/test_yed_rapporti_policy.py tests/test_ingest_result.py tests/test_conflict_resolver.py tests/test_rapporti_shorthand_dispatch.py -v
```

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/_errors.py \
        src/pyarchinit_s3dgraphy_bridge/ingest_result.py \
        src/pyarchinit_s3dgraphy_bridge/conflict_resolver.py \
        src/pyarchinit_s3dgraphy_bridge/yed_rapporti_policy.py \
        tests/test_yed_rapporti_policy.py tests/test_ingest_result.py \
        tests/test_conflict_resolver.py tests/test_rapporti_shorthand_dispatch.py
git commit -m "port(yed_rapporti_policy): vendored + extract _errors.py, transitive ingest_result/conflict_resolver"
```

---

### Task 21: Port `yed_table_parser`

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_table_parser.py`
- Create: `$BRIDGE/tests/test_yed_table_parser.py`

- [ ] **Step 1: Copy source**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/yed_table_parser.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_table_parser.py"
```

- [ ] **Step 2: Audit**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_table_parser.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 3: Copy + adapt tests (two files)**

```bash
cp "$PLUGIN/tests/sync/test_yed_table_parser.py" "$BRIDGE/tests/test_yed_table_parser.py"
cp "$PLUGIN/tests/sync/test_table_parser_integration.py" "$BRIDGE/tests/test_table_parser_integration.py"
for f in test_yed_table_parser test_table_parser_integration; do
  sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/$f.py"
  rm "$BRIDGE/tests/$f.py.bak"
done
```

- [ ] **Step 4: Run**

```bash
cd "$BRIDGE" && pytest tests/test_yed_table_parser.py tests/test_table_parser_integration.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/yed_table_parser.py \
        tests/test_yed_table_parser.py tests/test_table_parser_integration.py
git commit -m "port(yed_table_parser): vendored, integration tests included"
```

---

### Task 22: Port `paradata_store`

**Note:** depends on `_db_handle`, `_workspace`. No Qt imports per audit.

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/paradata_store.py`
- Create: `$BRIDGE/tests/test_paradata_store.py`
- Create: `$BRIDGE/tests/test_paradata_idempotent.py`

- [ ] **Step 1: Copy source**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/paradata_store.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/paradata_store.py"
```

- [ ] **Step 2: Audit — paradata_store also uses `from .graph_ingestor import GraphSyncError`**

```bash
grep -nE "from \.graph_ingestor" "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/paradata_store.py"
```

If a hit is found, rewrite it to use `_errors`:

```bash
sed -i.bak 's|from \.graph_ingestor import GraphSyncError|from ._errors import GraphSyncError|g' \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/paradata_store.py"
rm "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/paradata_store.py.bak"
```

- [ ] **Step 3: Audit Qt/Flask**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/paradata_store.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 4: Copy + adapt tests**

```bash
cp "$PLUGIN/tests/sync/test_paradata_store.py" "$BRIDGE/tests/test_paradata_store.py"
cp "$PLUGIN/tests/sync/test_paradata_idempotent.py" "$BRIDGE/tests/test_paradata_idempotent.py"
for f in test_paradata_store test_paradata_idempotent; do
  sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/$f.py"
  rm "$BRIDGE/tests/$f.py.bak"
done
```

- [ ] **Step 5: Run**

```bash
cd "$BRIDGE" && pytest tests/test_paradata_store.py tests/test_paradata_idempotent.py -v
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/paradata_store.py \
        tests/test_paradata_store.py tests/test_paradata_idempotent.py
git commit -m "port(paradata_store): vendored, GraphSyncError -> _errors"
```

---

### Task 23: Port `graph_ingestor`

**Note:** the heaviest module (1486 lines). Has one Qt offender per audit: `from qgis.PyQt.QtWidgets import QApplication` inside a `try:` block (lines ~200-210 in plugin). Replace with a stdlib-only check.

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/graph_ingestor.py`
- Create: `$BRIDGE/tests/test_graph_ingestor.py`
- Create: `$BRIDGE/tests/test_idempotent_ingest.py`

- [ ] **Step 1: Copy source**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/graph_ingestor.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/graph_ingestor.py"
```

- [ ] **Step 2: Strip the QApplication branch**

Open `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/graph_ingestor.py`. Locate the block (around line 200-210):

```python
try:
    from qgis.PyQt.QtWidgets import QApplication
    if QApplication.instance() is not None:
        # yE-E: a Qt app is alive, skip the heuristic
        ...
except ImportError:
    ...
```

Replace it with:

```python
# Bridge: no Qt detection. The plugin used QApplication.instance()
# as a heuristic to detect "running inside QGIS" vs "running in a
# headless test"; in the bridge we always behave headlessly.
# Hosts that want the old behavior can pass a Settings entry
# `is_interactive_qgis=True` and branch on that.
```

- [ ] **Step 3: Rewrite the local re-import `from .ingest_result import IngestResult` inside method bodies — already relative, keep as-is. Re-export GraphSyncError/CycleDetectedError from `_errors`**

Locate the top of the file. After the existing `from __future__ import annotations`, ensure these top-level classes are re-exported from `_errors` instead of being defined inline. Find any `class GraphSyncError(Exception)` and `class CycleDetectedError(GraphSyncError)` definitions, delete them, and replace with:

```python
from ._errors import CycleDetectedError, GraphSyncError, SchemaMismatchError

__all__ = [
    "CycleDetectedError", "GraphSyncError", "SchemaMismatchError",
    "GraphIngestor",
]
```

- [ ] **Step 4: Audit**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)|QApplication" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/graph_ingestor.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 5: Copy + adapt tests**

```bash
cp "$PLUGIN/tests/sync/test_graph_ingestor.py" "$BRIDGE/tests/test_graph_ingestor.py"
cp "$PLUGIN/tests/sync/test_idempotent_ingest.py" "$BRIDGE/tests/test_idempotent_ingest.py"
for f in test_graph_ingestor test_idempotent_ingest; do
  sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/$f.py"
  rm "$BRIDGE/tests/$f.py.bak"
done
```

- [ ] **Step 6: Run**

```bash
cd "$BRIDGE" && pytest tests/test_graph_ingestor.py tests/test_idempotent_ingest.py -v
```

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/graph_ingestor.py \
        tests/test_graph_ingestor.py tests/test_idempotent_ingest.py
git commit -m "port(graph_ingestor): vendored, strip QApplication branch, re-export errors from _errors"
```

---

### Task 24: Port `graph_projector`

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/graph_projector.py`
- Create: `$BRIDGE/tests/test_graph_projector.py`
- Create: `$BRIDGE/tests/test_graph_projector_paradata.py`

- [ ] **Step 1: Copy source**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/graph_projector.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/graph_projector.py"
```

- [ ] **Step 2: Audit**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/graph_projector.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 3: Fix the `from .graph_ingestor import GraphSyncError` → `from ._errors import GraphSyncError`**

```bash
sed -i.bak 's|from \.graph_ingestor import GraphSyncError|from ._errors import GraphSyncError|g' \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/graph_projector.py"
rm "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/graph_projector.py.bak"
```

- [ ] **Step 4: Copy + adapt tests**

```bash
cp "$PLUGIN/tests/sync/test_graph_projector.py" "$BRIDGE/tests/test_graph_projector.py"
cp "$PLUGIN/tests/sync/test_graph_projector_paradata.py" "$BRIDGE/tests/test_graph_projector_paradata.py"
for f in test_graph_projector test_graph_projector_paradata; do
  sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/$f.py"
  rm "$BRIDGE/tests/$f.py.bak"
done
```

- [ ] **Step 5: Run**

```bash
cd "$BRIDGE" && pytest tests/test_graph_projector.py tests/test_graph_projector_paradata.py -v
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/graph_projector.py \
        tests/test_graph_projector.py tests/test_graph_projector_paradata.py
git commit -m "port(graph_projector): vendored, GraphSyncError -> _errors"
```

---

### Task 25: Port `group_projector`

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/group_projector.py`
- Create: `$BRIDGE/tests/test_group_projector.py`

- [ ] **Step 1: Copy source**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/group_projector.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/group_projector.py"
```

- [ ] **Step 2: Audit**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/group_projector.py" || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 3: Copy + adapt test**

```bash
cp "$PLUGIN/tests/sync/test_group_projector.py" "$BRIDGE/tests/test_group_projector.py"
sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/test_group_projector.py"
rm "$BRIDGE/tests/test_group_projector.py.bak"
```

- [ ] **Step 4: Run**

```bash
cd "$BRIDGE" && pytest tests/test_group_projector.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/group_projector.py tests/test_group_projector.py
git commit -m "port(group_projector): vendored base (no LocationNodeGroup in v1.0)"
```

---

### Task 26: Port `graphml_writer` + `yed_import_pipeline` (final two of the 16)

**Note:** these two are large (2216 + 1519 LoC) and import nothing Qt directly. They depend on every previously-ported module. Done together because they unlock the AC-2 golden suite.

**Files:**
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/graphml_writer.py`
- Create: `$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_import_pipeline.py`
- Create: `$BRIDGE/tests/test_graphml_writer_helpers.py`
- Create: `$BRIDGE/tests/test_graphml_writer_pipeline.py`
- Create: `$BRIDGE/tests/test_yed_import_pipeline.py`
- Create: `$BRIDGE/tests/test_yed_pipeline_integration.py`

- [ ] **Step 1: Copy both sources**

```bash
cp "$PLUGIN/modules/s3dgraphy/sync/graphml_writer.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/graphml_writer.py"
cp "$PLUGIN/modules/s3dgraphy/sync/yed_import_pipeline.py" \
   "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_import_pipeline.py"
```

- [ ] **Step 2: Audit both**

```bash
grep -nE "^(import|from) (PyQt|qgis|flask)" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/graphml_writer.py" \
  "$BRIDGE/src/pyarchinit_s3dgraphy_bridge/yed_import_pipeline.py" \
  || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 3: Copy + adapt the 4 tests**

```bash
cp "$PLUGIN/tests/sync/test_graphml_writer_helpers.py"  "$BRIDGE/tests/test_graphml_writer_helpers.py"
cp "$PLUGIN/tests/sync/test_graphml_writer_pipeline.py" "$BRIDGE/tests/test_graphml_writer_pipeline.py"
cp "$PLUGIN/tests/sync/test_yed_import_pipeline.py"     "$BRIDGE/tests/test_yed_import_pipeline.py"
cp "$PLUGIN/tests/sync/test_yed_pipeline_integration.py" "$BRIDGE/tests/test_yed_pipeline_integration.py"
for f in test_graphml_writer_helpers test_graphml_writer_pipeline test_yed_import_pipeline test_yed_pipeline_integration; do
  sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/$f.py"
  rm "$BRIDGE/tests/$f.py.bak"
done
```

- [ ] **Step 4: Copy fixtures used by these tests**

```bash
mkdir -p "$BRIDGE/tests/fixtures"
cp "$PLUGIN/tests/sync/fixtures/"*.graphml  "$BRIDGE/tests/fixtures/"
cp "$PLUGIN/tests/sync/fixtures/"*.json     "$BRIDGE/tests/fixtures/"
cp "$PLUGIN/tests/sync/fixtures/"*.sqlite   "$BRIDGE/tests/fixtures/" 2>/dev/null || true
ls "$BRIDGE/tests/fixtures/" | wc -l
```

Expected: 10+ files.

- [ ] **Step 5: Run all 4 tests**

```bash
cd "$BRIDGE" && pytest tests/test_graphml_writer_helpers.py tests/test_graphml_writer_pipeline.py tests/test_yed_import_pipeline.py tests/test_yed_pipeline_integration.py -v
```

Expected: all pass.

- [ ] **Step 6: Run the FULL bridge test suite as a regression check**

```bash
cd "$BRIDGE" && pytest -v -m "not slow"
```

Expected: full count green; record the number in the commit message.

- [ ] **Step 7: Verify the no-Qt/Flask guard**

```bash
cd "$BRIDGE" && make guard
```

Expected: `OK: zero Qt/Flask/QGIS imports`.

- [ ] **Step 8: Commit**

```bash
cd "$BRIDGE"
git add src/pyarchinit_s3dgraphy_bridge/graphml_writer.py \
        src/pyarchinit_s3dgraphy_bridge/yed_import_pipeline.py \
        tests/test_graphml_writer_helpers.py tests/test_graphml_writer_pipeline.py \
        tests/test_yed_import_pipeline.py tests/test_yed_pipeline_integration.py \
        tests/fixtures/
git commit -m "port(graphml_writer + yed_import_pipeline): final 2 of 16 + fixtures, 0 Qt deps verified"
```

---

### Task 27: Round-trip integration tests (L1 layer)

**Files:**
- Create: `$BRIDGE/tests/test_round_trip.py`
- Create: `$BRIDGE/tests/test_round_trip_with_paradata.py`
- Create: `$BRIDGE/tests/test_round_trip_with_groups.py`
- Create: `$BRIDGE/tests/test_yed_classifier_integration.py`
- Create: `$BRIDGE/tests/test_yed_parsers_orchestration.py`
- Create: `$BRIDGE/tests/test_group_walker_integration.py`

- [ ] **Step 1: Copy + adapt the 6 integration tests**

```bash
for f in test_round_trip test_round_trip_with_paradata test_round_trip_with_groups \
         test_yed_classifier_integration test_yed_parsers_orchestration \
         test_group_walker_integration; do
  cp "$PLUGIN/tests/sync/$f.py" "$BRIDGE/tests/$f.py"
  sed -i.bak 's|modules\.s3dgraphy\.sync\.|pyarchinit_s3dgraphy_bridge.|g' "$BRIDGE/tests/$f.py"
  rm "$BRIDGE/tests/$f.py.bak"
done
```

- [ ] **Step 2: Run the 6 tests**

```bash
cd "$BRIDGE" && pytest tests/test_round_trip.py tests/test_round_trip_with_paradata.py \
  tests/test_round_trip_with_groups.py tests/test_yed_classifier_integration.py \
  tests/test_yed_parsers_orchestration.py tests/test_group_walker_integration.py -v
```

Expected: all pass.

- [ ] **Step 3: Update CHANGELOG**

Edit `$BRIDGE/CHANGELOG.md`, replace the `[Unreleased]` section with:

```markdown
## [Unreleased]

### Added

- All 16 MVP modules vendored from pyarchinit 5.9.0.1-alpha.
- 5 typing.Protocol classes (DbSession, Workspace, Settings, FileProvider, Logger).
- L0 unit tests for every ported module.
- L1 round-trip integration tests (yEd -> SQLite -> GraphML).
- Zero Qt/Flask/QGIS imports in src/ (CI guard).

### Changed

- `_workspace._resolve_workspace_dir(...)` adds optional `settings=` parameter
  (Settings Protocol). QSettings branch removed; hosts must wire via Settings.
- `vocab_provider.VocabProvider` no longer inherits QObject and no longer
  installs a QFileSystemWatcher. Call `reload()` from the host on file change.
- `graph_ingestor`: the `QApplication.instance()` heuristic is removed.
  Bridge always behaves headlessly.
```

- [ ] **Step 4: Commit**

```bash
cd "$BRIDGE"
git add tests/test_round_trip.py tests/test_round_trip_with_paradata.py \
        tests/test_round_trip_with_groups.py tests/test_yed_classifier_integration.py \
        tests/test_yed_parsers_orchestration.py tests/test_group_walker_integration.py \
        CHANGELOG.md
git commit -m "test(L1): 6 round-trip integration tests + CHANGELOG unreleased section"
```

---

### Task 28: AC-2 byte-identical golden suite — fixtures

**Files:**
- Create: `$BRIDGE/tests/fixtures/ac2_golden/` directory with copied `.graphml` files
- Create: `$BRIDGE/tests/fixtures/ac2_golden/README.md`

- [ ] **Step 1: Create the golden directory**

```bash
mkdir -p "$BRIDGE/tests/fixtures/ac2_golden"
```

- [ ] **Step 2: Copy every plugin `.graphml` fixture into the golden set**

```bash
cp "$PLUGIN/tests/sync/fixtures/mini_volterra_baseline_ai03.graphml"     "$BRIDGE/tests/fixtures/ac2_golden/"
cp "$PLUGIN/tests/sync/fixtures/mini_volterra_external.graphml"          "$BRIDGE/tests/fixtures/ac2_golden/"
cp "$PLUGIN/tests/sync/fixtures/mini_volterra_external_with_new_epoch.graphml" "$BRIDGE/tests/fixtures/ac2_golden/"
cp "$PLUGIN/tests/sync/fixtures/paradata_volterra.graphml"               "$BRIDGE/tests/fixtures/ac2_golden/"
cp "$PLUGIN/tests/sync/fixtures/groups_volterra.graphml"                 "$BRIDGE/tests/fixtures/ac2_golden/"
cp "$PLUGIN/tests/sync/fixtures/legacy_5_5_x.graphml"                    "$BRIDGE/tests/fixtures/ac2_golden/"
cp "$PLUGIN/tests/sync/fixtures/em_demo_02_mini.graphml"                 "$BRIDGE/tests/fixtures/ac2_golden/"
ls "$BRIDGE/tests/fixtures/ac2_golden/" | wc -l
```

Expected: `7`.

- [ ] **Step 3: Write `tests/fixtures/ac2_golden/README.md`**

```markdown
# AC-2 Byte-Identical Golden Suite

These `.graphml` fixtures were captured from pyarchinit plugin v5.9.0.1-alpha.
Each one is the "ground truth": the bridge must produce a byte-identical output
when round-tripping through `GraphIngestor` -> in-memory SQLite -> `GraphmlWriter`.

| Fixture | Plugin source | Notes |
|---|---|---|
| `mini_volterra_baseline_ai03.graphml` | AI03 baseline (plugin 5.4.x) | Base round-trip case |
| `mini_volterra_external.graphml` | AI06 external groups | `is_in_activity` edges |
| `mini_volterra_external_with_new_epoch.graphml` | AI06 + Epoch | Period/Phase nodes |
| `paradata_volterra.graphml` | AI04 paradata | DocumentNode + LinkNode |
| `groups_volterra.graphml` | AI06 groups full | All 7 group kinds |
| `legacy_5_5_x.graphml` | Plugin 5.5.x compatibility | Pre-AI07 schema |
| `em_demo_02_mini.graphml` | EM template demo | Heriverse export format |

A failing fixture is **never** auto-updated by the test runner; a human must
review the diff, agree the new behavior is correct, then re-capture by running
the producer side and committing the new bytes.
```

- [ ] **Step 4: Commit**

```bash
cd "$BRIDGE"
git add tests/fixtures/ac2_golden/
git commit -m "test(AC-2): import 7 golden GraphML fixtures from plugin 5.9.0.1-alpha"
```

---

### Task 29: AC-2 byte-identical golden suite — runner

**Files:**
- Create: `$BRIDGE/tests/test_ac2_byte_identical.py`

- [ ] **Step 1: Write the runner**

```python
# tests/test_ac2_byte_identical.py
"""AC-2 contract: bridge output is byte-identical to plugin 5.9.0.1-alpha.

For every GraphML in tests/fixtures/ac2_golden/:
  1. Load the original bytes.
  2. Ingest into an in-memory SQLite via GraphIngestor.
  3. Re-project via GraphProjector + GraphmlWriter.
  4. Assert output bytes == original bytes (line endings normalized).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine

from pyarchinit_s3dgraphy_bridge._db_handle import DbHandle
from pyarchinit_s3dgraphy_bridge.graph_ingestor import GraphIngestor
from pyarchinit_s3dgraphy_bridge.graph_projector import GraphProjector
from pyarchinit_s3dgraphy_bridge.graphml_writer import GraphmlWriter

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "ac2_golden"


def _normalize(b: bytes) -> bytes:
    """Normalize CRLF -> LF and strip trailing whitespace per line."""
    return b"\n".join(line.rstrip() for line in b.replace(b"\r\n", b"\n").split(b"\n"))


@pytest.mark.slow
@pytest.mark.parametrize("fixture", sorted(GOLDEN_DIR.glob("*.graphml")), ids=lambda p: p.name)
def test_ac2_byte_identical_roundtrip(fixture: Path, tmp_path: Path):
    """Round-trip each golden fixture and assert byte-equality."""
    original = fixture.read_bytes()

    # Step 1: fresh in-memory SQLite + DbHandle
    sqlite_path = tmp_path / "ac2.sqlite"
    engine = create_engine(f"sqlite:///{sqlite_path}", future=True)
    handle = DbHandle(engine=engine, is_postgres=False, sqlite_path=sqlite_path)

    # Step 2: ingest the GraphML
    ingestor = GraphIngestor()
    ingestor.populate_list(handle=handle, graphml_bytes=original, sito="ac2_site")

    # Step 3: project back into a graph
    projector = GraphProjector(handle=handle, sito="ac2_site")
    graph = projector.project()

    # Step 4: write to GraphML bytes
    writer = GraphmlWriter()
    produced = writer.write_bytes(graph)

    assert _normalize(produced) == _normalize(original), (
        f"AC-2 byte-identical violated for {fixture.name}\n"
        f"original bytes: {len(original)} produced bytes: {len(produced)}"
    )
```

Write to `$BRIDGE/tests/test_ac2_byte_identical.py`.

- [ ] **Step 2: Run the golden suite explicitly (slow marker)**

```bash
cd "$BRIDGE" && pytest tests/test_ac2_byte_identical.py -v -m slow
```

Expected: `7 passed` (one per fixture).

- [ ] **Step 3: Confirm fast suite still excludes it**

```bash
cd "$BRIDGE" && pytest -v -m "not slow" --co -q | grep -c "ac2_byte_identical" || echo "0"
```

Expected: `0` (not collected when slow excluded).

- [ ] **Step 4: Commit**

```bash
cd "$BRIDGE"
git add tests/test_ac2_byte_identical.py
git commit -m "test(AC-2): parametrized golden runner over 7 fixtures (slow marker)"
```

---

### Task 30: CI matrix — `.github/workflows/ci.yml`

**Files:**
- Create: `$BRIDGE/.github/workflows/ci.yml`

- [ ] **Step 1: Create the workflows directory**

```bash
mkdir -p "$BRIDGE/.github/workflows"
```

- [ ] **Step 2: Write the CI workflow (full content, not a skeleton)**

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  guard:
    name: "Guard: no Qt/Flask/QGIS imports"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run guard
        run: |
          if grep -RnE "^(import|from) (PyQt|qgis|flask)" src/; then
            echo "FAIL: bridge must not import Qt, QGIS, or Flask"
            exit 1
          fi
          echo "OK: zero Qt/Flask/QGIS imports in src/"

  lint:
    name: "Lint (ruff + format check)"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: ruff check src tests
      - run: ruff format --check src tests

  type:
    name: "Type check (mypy strict)"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: mypy src

  test:
    name: "Test ${{ matrix.os }} / py${{ matrix.python }}"
    needs: [guard, lint, type]
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - name: Install
        run: pip install -e ".[dev]"
      - name: Fast suite (unit + integration, excludes slow)
        run: pytest -v -m "not slow" --cov=pyarchinit_s3dgraphy_bridge --cov-report=xml
      - name: AC-2 golden suite (slow)
        run: pytest -v -m slow
      - name: Upload coverage
        if: matrix.os == 'ubuntu-latest' && matrix.python == '3.12'
        uses: actions/upload-artifact@v4
        with:
          name: coverage-xml
          path: coverage.xml

  build:
    name: "Build wheel + sdist"
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install build
      - run: python -m build
      - name: Verify wheel installs in a clean venv
        run: |
          python -m venv /tmp/verify
          /tmp/verify/bin/pip install dist/*.whl
          /tmp/verify/bin/python -c "import pyarchinit_s3dgraphy_bridge; print(pyarchinit_s3dgraphy_bridge.__version__)"
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

Write to `$BRIDGE/.github/workflows/ci.yml`.

- [ ] **Step 3: Locally lint the YAML**

```bash
cd "$BRIDGE"
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo "YAML OK"
```

Expected: `YAML OK`.

- [ ] **Step 4: Commit**

```bash
cd "$BRIDGE"
git add .github/workflows/ci.yml
git commit -m "ci: 9-cell matrix (ubuntu/macos/windows x py 3.11/3.12/3.13) + guard + build"
```

---

### Task 31: Publish workflow — `.github/workflows/publish.yml`

**Files:**
- Create: `$BRIDGE/.github/workflows/publish.yml`

- [ ] **Step 1: Write the publish workflow (Trusted Publishing, no token)**

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - "v*"

permissions:
  contents: read
  id-token: write   # required for PyPI Trusted Publishing

concurrency:
  group: publish-${{ github.ref }}
  cancel-in-progress: false

jobs:
  build:
    name: Build distributions
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install build
      - run: python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    name: Publish to PyPI (Trusted Publishing)
    needs: [build]
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/pyarchinit-s3dgraphy-bridge
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - name: Publish
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          # No password / token: Trusted Publishing via OIDC.
          packages-dir: dist/
          print-hash: true
```

Write to `$BRIDGE/.github/workflows/publish.yml`.

- [ ] **Step 2: Lint the YAML**

```bash
cd "$BRIDGE"
python -c "import yaml; yaml.safe_load(open('.github/workflows/publish.yml'))" && echo "YAML OK"
```

Expected: `YAML OK`.

- [ ] **Step 3: Write the PyPI Trusted Publishing setup memo into the changelog**

Append to `$BRIDGE/CHANGELOG.md`, right under `### Added`:

```markdown
### Infrastructure

- GitHub Actions CI with 9-cell test matrix
  (ubuntu-latest / macos-latest / windows-latest x py 3.11 / 3.12 / 3.13).
- Trusted Publishing to PyPI on annotated `v*` tags
  (no token in repo, OIDC via `id-token: write`).
- Pre-publish setup gate: PyPI project `pyarchinit-s3dgraphy-bridge` must be
  created and a Trusted Publisher entry added pointing at this repo's
  `publish.yml` workflow and the `pypi` environment.
```

- [ ] **Step 4: Commit**

```bash
cd "$BRIDGE"
git add .github/workflows/publish.yml CHANGELOG.md
git commit -m "ci: publish.yml using PyPI Trusted Publishing on v* tags"
```

---

### Task 32: `PUBLIC_API.md` with plugin + mini-desk worked examples

**Files:**
- Create: `$BRIDGE/PUBLIC_API.md`

- [ ] **Step 1: Write the full `PUBLIC_API.md`**

```markdown
# Public API — pyarchinit-s3dgraphy-bridge

This is the contract of `pyarchinit-s3dgraphy-bridge`. Anything documented here
is covered by SemVer: breaking changes require a major version bump.

## 5 Protocol seams

The bridge does not know about Qt, QGIS, or Flask. Hosts implement these
five Protocols and pass instances to the bridge functions that need them.

### `DbSession`

```python
from typing import Protocol, Any

class DbSession(Protocol):
    is_postgres: bool
    def execute(self, sql: str, params: dict | None = None) -> Any: ...
    def commit(self) -> None: ...
```

### `Workspace`

```python
from pathlib import Path

class Workspace(Protocol):
    root: Path
    def tmp(self) -> Path: ...
```

### `Settings`

```python
class Settings(Protocol):
    def get(self, key: str, default: Any = None) -> Any: ...
```

### `FileProvider`

```python
class FileProvider(Protocol):
    def read_bytes(self, ref: str) -> bytes: ...
```

### `Logger`

```python
class Logger(Protocol):
    def info(self, msg: str) -> None: ...
    def warn(self, msg: str) -> None: ...
    def error(self, msg: str, exc: Exception | None = None) -> None: ...
```

## Worked example 1 — QGIS plugin (`pyarchinit`)

```python
# modules/s3dgraphy/bridge_adapter/qgis_impls.py
from pathlib import Path
import sqlite3

from qgis.core import QgsMessageLog, Qgis
from qgis.PyQt.QtCore import QSettings

from pyarchinit_s3dgraphy_bridge.protocols import (
    DbSession, Workspace, Settings, FileProvider, Logger,
)


class QgisDbSession:
    is_postgres: bool

    def __init__(self, conn: sqlite3.Connection, is_postgres: bool = False):
        self._conn = conn
        self.is_postgres = is_postgres

    def execute(self, sql, params=None):
        cur = self._conn.cursor()
        cur.execute(sql, params or {})
        return cur

    def commit(self):
        self._conn.commit()


class QgisWorkspace:
    def __init__(self, root: Path):
        self.root = root

    def tmp(self):
        d = self.root / "tmp"
        d.mkdir(parents=True, exist_ok=True)
        return d


class QSettingsProxy:
    def __init__(self):
        self._s = QSettings("pyarchinit", "bridge")

    def get(self, key, default=None):
        v = self._s.value(key, default)
        return v if v is not None else default


class QtFileProvider:
    """ref = absolute path on disk."""
    def read_bytes(self, ref):
        return Path(ref).read_bytes()


class QgsLogger:
    def info(self, msg):
        QgsMessageLog.logMessage(msg, "bridge", Qgis.Info)

    def warn(self, msg):
        QgsMessageLog.logMessage(msg, "bridge", Qgis.Warning)

    def error(self, msg, exc=None):
        if exc is not None:
            msg = f"{msg} | {type(exc).__name__}: {exc}"
        QgsMessageLog.logMessage(msg, "bridge", Qgis.Critical)
```

Usage from a plugin form:

```python
from pyarchinit_s3dgraphy_bridge.yed_import_pipeline import import_yed_raw

session = QgisDbSession(sqlite3.connect(self.db_path))
result = import_yed_raw(
    session=session,
    workspace=QgisWorkspace(Path("/Users/.../pyarchinit_workspace/Volterra")),
    settings=QSettingsProxy(),
    files=QtFileProvider(),
    logger=QgsLogger(),
    graphml_bytes=Path(self.selected_graphml).read_bytes(),
    sito="Volterra",
)
self.statusBar().showMessage(f"Imported {result.applied} rows")
```

## Worked example 2 — Flask backend (`pyarchinit-mini-desk`)

```python
# pyarchinit_mini/bridge_adapter/flask_impls.py
import logging
from pathlib import Path

from sqlalchemy.orm import Session
from flask import current_app

from pyarchinit_mini.models import AppSetting
from pyarchinit_mini.services.media_service import MediaService


class SqlalchemyDbSession:
    def __init__(self, session: Session, is_postgres: bool):
        self._session = session
        self.is_postgres = is_postgres

    def execute(self, sql, params=None):
        return self._session.execute(sql, params or {})

    def commit(self):
        self._session.commit()


class FlaskWorkspace:
    def __init__(self, root: Path):
        self.root = root

    def tmp(self):
        d = self.root / "tmp"
        d.mkdir(parents=True, exist_ok=True)
        return d


class AppSettingProxy:
    def __init__(self, session: Session):
        self._session = session

    def get(self, key, default=None):
        row = self._session.query(AppSetting).filter_by(key=key).one_or_none()
        return row.value if row else default


class UploadFileProvider:
    """ref = upload-id (UUIDv7) issued by MediaService."""
    def __init__(self, media_service: MediaService):
        self._media = media_service

    def read_bytes(self, ref):
        return self._media.fetch_bytes(upload_id=ref)


class PythonLogger:
    def __init__(self):
        self._log = logging.getLogger("bridge")

    def info(self, msg):
        self._log.info(msg)

    def warn(self, msg):
        self._log.warning(msg)

    def error(self, msg, exc=None):
        self._log.error(msg, exc_info=exc)
```

Usage from a Flask route:

```python
from flask import Blueprint, request, jsonify
from pyarchinit_s3dgraphy_bridge.yed_import_pipeline import import_yed_raw

bp = Blueprint("sync", __name__, url_prefix="/api/v1/sync")

@bp.post("/import")
def post_import():
    upload_id = request.json["upload_id"]
    sito = request.json["sito"]

    session = SqlalchemyDbSession(g.db, is_postgres=current_app.config["DB_IS_PG"])
    result = import_yed_raw(
        session=session,
        workspace=FlaskWorkspace(Path(current_app.config["WORKSPACE_ROOT"]) / sito),
        settings=AppSettingProxy(g.db),
        files=UploadFileProvider(current_app.media_service),
        logger=PythonLogger(),
        graphml_bytes=current_app.media_service.fetch_bytes(upload_id=upload_id),
        sito=sito,
    )
    return jsonify(applied=result.applied, errors=list(result.errors)), 200
```

## Stability promise

- Anything in `pyarchinit_s3dgraphy_bridge.__all__` or in the package root
  namespace is public API.
- Module-level functions and classes exported by the 16 vendored modules are
  public API (they are the original plugin surface, preserved verbatim).
- Symbols prefixed with `_` are private and may change without notice.
- Breaking changes to public API require a major version bump (`v2.0.0`).
- New optional parameters with defaults are minor bumps.
- Bug fixes that preserve API are patch bumps.
```

Write to `$BRIDGE/PUBLIC_API.md`.

- [ ] **Step 2: Commit**

```bash
cd "$BRIDGE"
git add PUBLIC_API.md
git commit -m "docs(public-api): 5 Protocols + plugin-side and mini-desk-side worked examples"
```

---

### Task 33: Tag v1.0.0 and trigger PyPI publish

**Files:**
- Modify: `$BRIDGE/CHANGELOG.md` (move `[Unreleased]` -> `[1.0.0]`)

- [ ] **Step 1: Final pre-tag green check**

```bash
cd "$BRIDGE"
. .venv/bin/activate
make guard
make lint
make type
pytest -v -m "not slow"
pytest -v -m slow
make build
```

All five must exit 0. If any fails, fix before tagging.

- [ ] **Step 2: Verify the built wheel installs cleanly**

```bash
cd "$BRIDGE"
python -m venv /tmp/v1-verify
/tmp/v1-verify/bin/pip install dist/pyarchinit_s3dgraphy_bridge-1.0.0-*.whl
/tmp/v1-verify/bin/python -c "
import pyarchinit_s3dgraphy_bridge as p
assert p.__version__ == '1.0.0'
from pyarchinit_s3dgraphy_bridge.protocols import DbSession, Workspace, Settings, FileProvider, Logger
print('OK')
"
rm -rf /tmp/v1-verify
```

Expected: `OK`.

- [ ] **Step 3: Promote `[Unreleased]` to `[1.0.0]` in CHANGELOG**

Open `$BRIDGE/CHANGELOG.md`. Change `## [Unreleased]` to `## [1.0.0] - 2026-MM-DD` (use today's actual date when executing). Add a fresh empty `## [Unreleased]` above it.

- [ ] **Step 4: Commit the CHANGELOG bump**

```bash
cd "$BRIDGE"
git add CHANGELOG.md
git commit -m "chore(release): v1.0.0 — finalize CHANGELOG"
```

- [ ] **Step 5: Push `main` to GitHub for the first time**

Assumes the GitHub repo `pyarchinit/pyarchinit-s3dgraphy-bridge` has already been created (empty) by the caller.

```bash
cd "$BRIDGE"
git remote add origin git@github.com:pyarchinit/pyarchinit-s3dgraphy-bridge.git
git push -u origin main
```

Expected: branch `main` published on GitHub. CI runs and all 9 matrix cells go green.

- [ ] **Step 6: Wait for green CI on `main`**

Manual gate. Verify via `gh run list --limit 1` or the Actions tab in the browser:

```bash
cd "$BRIDGE"
gh run list --limit 1 --json status,conclusion --jq '.[0] | "\(.status) \(.conclusion)"'
```

Expected: `completed success`.

- [ ] **Step 7: Pre-publish PyPI gate (one-time, manual)**

Confirm with the caller that:
1. The PyPI project `pyarchinit-s3dgraphy-bridge` is reserved (account with 2FA enabled).
2. A Trusted Publisher entry is registered on PyPI pointing at:
   - Repo: `pyarchinit/pyarchinit-s3dgraphy-bridge`
   - Workflow: `publish.yml`
   - Environment: `pypi`
3. The `pypi` GitHub Environment exists in the repo Settings with the same name.

Do NOT proceed to the next step until those three are confirmed.

- [ ] **Step 8: Create and push the annotated v1.0.0 tag**

```bash
cd "$BRIDGE"
git tag -a v1.0.0 -m "v1.0.0 — Bridge MVP: 16 modules + 5 Protocols + AC-2 golden suite + 9-cell CI"
git push origin v1.0.0
```

Expected: tag pushed; `Publish to PyPI` workflow starts within ~30s.

- [ ] **Step 9: Verify PyPI publication**

```bash
sleep 120   # generous wait for build + publish
pip index versions pyarchinit-s3dgraphy-bridge
```

Expected: `pyarchinit-s3dgraphy-bridge (1.0.0)` listed.

Also: `pip install pyarchinit-s3dgraphy-bridge==1.0.0` in a throwaway venv must succeed.

```bash
python -m venv /tmp/pypi-verify
/tmp/pypi-verify/bin/pip install pyarchinit-s3dgraphy-bridge==1.0.0
/tmp/pypi-verify/bin/python -c "
import pyarchinit_s3dgraphy_bridge
assert pyarchinit_s3dgraphy_bridge.__version__ == '1.0.0'
print('PyPI install OK')
"
rm -rf /tmp/pypi-verify
```

Expected: `PyPI install OK`.

- [ ] **Step 10: Final commit — none needed**

The release is complete. No further commit is required: the tag itself is the release artifact, and the CHANGELOG bump in Step 4 was already pushed. Bridge v1.0 is live on PyPI.

---

## Self-Review Checklist

Before declaring v1.0.0 shipped, the executor verifies every item below. Each box must be checked off with the evidence noted.

- [ ] **Repo skeleton complete**: `git log --oneline | wc -l` >= 33 commits.
- [ ] **5 Protocols defined**: `grep -c "@runtime_checkable" src/pyarchinit_s3dgraphy_bridge/protocols.py` equals 5.
- [ ] **16 MVP modules present** in `src/pyarchinit_s3dgraphy_bridge/`:
  - [ ] `_db_handle.py`
  - [ ] `edge_registry.py`
  - [ ] `graph_ingestor.py`
  - [ ] `graph_projector.py`
  - [ ] `graphml_writer.py`
  - [ ] `group_projector.py`
  - [ ] `paradata_store.py`
  - [ ] `uuid7.py`
  - [ ] `vocab_provider.py`
  - [ ] `vocab_types.py`
  - [ ] `yed_classifier.py`
  - [ ] `yed_detector.py`
  - [ ] `yed_group_walker.py`
  - [ ] `yed_import_pipeline.py`
  - [ ] `yed_rapporti_policy.py`
  - [ ] `yed_table_parser.py`
- [ ] **Transitive helpers present** (not in 16-list, but required): `_errors.py`, `_workspace.py`, `conflict_resolver.py`, `ingest_result.py`, `vocab_provider_core.py`.
- [ ] **Zero Qt/Flask/QGIS imports**: `make guard` exits 0.
- [ ] **All unit + integration tests green** (fast suite): `pytest -m "not slow"` exits 0; collected count >= 35.
- [ ] **AC-2 golden suite green**: `pytest -m slow` exits 0; 7 parametrized cases pass.
- [ ] **9-cell CI matrix green** on the commit being tagged: ubuntu/macos/windows x py3.11/3.12/3.13 all completed successful.
- [ ] **Build artifacts valid**: `dist/pyarchinit_s3dgraphy_bridge-1.0.0-py3-none-any.whl` and `.tar.gz` both present after `python -m build`.
- [ ] **Wheel imports clean** in fresh venv: `pip install dist/*.whl && python -c "import pyarchinit_s3dgraphy_bridge"` succeeds.
- [ ] **PUBLIC_API.md documents all 5 Protocols + both consumer examples** (plugin + mini-desk).
- [ ] **CHANGELOG.md** has a `[1.0.0]` section with the release date and an empty `[Unreleased]` above it.
- [ ] **Tag `v1.0.0` is annotated** (not lightweight): `git cat-file -t v1.0.0` returns `tag`.
- [ ] **PyPI Trusted Publishing entry** is configured for repo + workflow + environment.
- [ ] **PyPI shows v1.0.0**: `pip index versions pyarchinit-s3dgraphy-bridge` lists it.
- [ ] **Throwaway venv `pip install pyarchinit-s3dgraphy-bridge==1.0.0`** succeeds and the import resolves.
- [ ] **No `TODO` / `FIXME` / `XXX` markers in `src/`**: `grep -RnE "TODO|FIXME|XXX" src/` returns 0 lines (or every hit is justified in the commit message).

When every box above is checked, Plan 1 is complete and the v1.0 release is shipped. Plans 2-5 (mini-desk migration, plugin migration, Ollama/LMStudio, Heriverse doc) can begin.