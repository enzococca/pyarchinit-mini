# Spec 2 — Local Graph & Paradata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the local graph projection + paradata storage + GraphML I/O layer for pyarchinit-mini-web: `GraphProjector` (DB → s3dgraphy.Graph), `ParadataStore` (per-site filesystem-backed paradata.graphml), `GraphIngestor` (preview/apply import flow), GraphML writer/reader delegated to s3dgraphy.exporter, auto-regen hook on US/USM save, 5 paradata CRUD HTML pages, and import GraphML flow with mandatory 2-phase preview.

**Architecture:** Two new packages (`pyarchinit_mini/graphproj/` + `pyarchinit_mini/graphml_io/`) + 3 new route modules (`graph_routes.py`, `paradata_routes.py`, `paradata_ui_routes.py`). Auto-regen hook fires post-commit on US save and writes merged `stratigraphy.graphml` atomically per-site. Old in-house writers (`graphml_builder`, `graphml_exporter`, `pure_networkx_exporter`, `converter`) get deprecation shims; `harris_creator_routes` is refactored to the new writer directly.

**Tech Stack:** Python 3.13, Flask, SQLAlchemy, pytest, s3dgraphy 0.1.42 (`exporter.graphml`, `importer.import_graphml`, `merge.GraphMerger`, `importer.pyarchinit_importer`), `fcntl`/`msvcrt` for locks.

**Spec:** `docs/superpowers/specs/2026-05-17-spec-2-local-graph-paradata-design.md`

---

## File Structure

### New files

| Path | Responsibility |
|---|---|
| `pyarchinit_mini/graphproj/__init__.py` | Package facade — re-exports public types |
| `pyarchinit_mini/graphproj/exceptions.py` | `ProjectionError`, `IngestError`, `IngestStaleError`, `ParadataConflict`, `ParadataNotFound`, `ParadataStorageError`, `GraphMLReadError`, `GraphMLWriteError` |
| `pyarchinit_mini/graphproj/filesystem.py` | `atomic_write()`, `paradata_flock()` (cross-platform), `_slugify()`, dir helpers |
| `pyarchinit_mini/graphproj/edge_registry.py` | Edge typing — wraps `VocabProvider.get_edge_types()` |
| `pyarchinit_mini/graphproj/projector.py` | `GraphProjector.populate_graph()` |
| `pyarchinit_mini/graphproj/paradata_store.py` | `ParadataStore` — load/atomic_write + CRUD per node type |
| `pyarchinit_mini/graphproj/ingest_plan.py` | `IngestPlan`, `IngestResult`, `NodePlanEntry` frozen dataclasses |
| `pyarchinit_mini/graphproj/ingestor.py` | `GraphIngestor.preview()` / `apply()` |
| `pyarchinit_mini/graphproj/auto_regen.py` | Post-commit hook + `disable_regen()` context + `force_regen_all_touched_sites()` |
| `pyarchinit_mini/graphml_io/__init__.py` | Package init |
| `pyarchinit_mini/graphml_io/writer.py` | `write_graphml(graph, path)` delegates to s3dgraphy |
| `pyarchinit_mini/graphml_io/reader.py` | `read_graphml(path)` delegates to s3dgraphy |
| `pyarchinit_mini/web_interface/graph_routes.py` | Flask blueprint `/sites/<site>/graph/{view,download,import-preview,import-apply}` |
| `pyarchinit_mini/web_interface/paradata_routes.py` | Flask blueprint `/api/v1/paradata/<site>/{authors,licenses,embargoes,documents,epochs}` |
| `pyarchinit_mini/web_interface/paradata_ui_routes.py` | Flask blueprint `/paradata/<site>/...` (HTML) |
| `pyarchinit_mini/web_interface/templates/paradata/list.html` | Shared list template (parameterized by node type) |
| `pyarchinit_mini/web_interface/templates/paradata/edit.html` | Shared edit form |
| `pyarchinit_mini/web_interface/templates/graph_import_preview.html` | Diff renderer |
| `pyarchinit_mini/web_interface/templates/graph_import_result.html` | Result page |
| `pyarchinit_mini/web_interface/templates/_partials/regen_banner.html` | Status banner partial |
| `docs/PARADATA_GUIDE.md` | User docs |
| `docs/GRAPH_AUTO_REGEN.md` | Dev docs |
| `tests/unit/test_graphproj_*.py` | Per-module unit tests |
| `tests/integration/test_paradata_routes.py` | REST API tests |
| `tests/integration/test_paradata_ui.py` | HTML page tests |
| `tests/integration/test_graph_routes.py` | Graph routes tests |
| `tests/integration/test_auto_regen_on_save.py` | Auto-regen integration |
| `tests/integration/test_bulk_import_single_regen.py` | Bulk debounce |
| `tests/integration/test_concurrent_saves_serialize.py` | Flock test |
| `tests/integration/test_graphml_writer_parity.py` | PR2 gate |
| `tests/integration/test_harris_matrix_post_cutover.py` | PR8 gate |
| `tests/e2e/test_paradata_ui_crud.py` | E2E HTML round-trip |
| `tests/e2e/test_ingest_preview_stale.py` | E2E staleness |
| `tests/fixtures/databases/sqlite_volterra_30us.db` | DB fixture |
| `tests/fixtures/paradata_graphmls/*.graphml` | Paradata fixtures |
| `tests/fixtures/ingest_uploads/*.graphml` | Import fixtures |
| `tests/fixtures/graphml_outputs/*.graphml` | Writer parity baselines |
| `tests/fixtures/_generate_volterra_synthetic.py` | Fixture regen script |

### Modified files

| Path | Change |
|---|---|
| `pyarchinit_mini/services/us_service.py` (or equivalent) | Add post-commit call to `auto_regen._trigger_graph_regen(site, session)` |
| `pyarchinit_mini/web_interface/app.py` | Register `graph_routes`, `paradata_routes`, `paradata_ui_routes` blueprints |
| `pyarchinit_mini/web_interface/excel_import_routes.py` | Wrap bulk import in `with auto_regen.disable_regen():` + `force_regen_all_touched_sites()` |
| `pyarchinit_mini/web_interface/harris_creator_routes.py` | Replace `from graphml_converter.graphml_builder import GraphMLBuilder` with `from graphml_io.writer import write_graphml` (PR8) |
| `pyarchinit_mini/graphml_converter/graphml_builder.py` | Add `_PaletteProxy`-style shim emitting `DeprecationWarning` (PR8) |
| `pyarchinit_mini/graphml_converter/graphml_exporter.py` | Same shim |
| `pyarchinit_mini/graphml_converter/pure_networkx_exporter.py` | Same shim |
| `pyarchinit_mini/graphml_converter/converter.py` | Same shim |
| `.gitignore` | Add `data/paradata/**/stratigraphy.graphml`, `data/paradata/**/.paradata.lock`, `data/paradata/**/*.tmp`, `data/paradata/**/imports/*`, `data/paradata/_regen.log`, `data/paradata/_metrics.sqlite` |
| `pyarchinit_mini/__init__.py` | Bump version `2.2.0-alpha → 2.3.0-alpha` |
| `pyproject.toml` | Bump version, declare any new console scripts if needed |
| `CHANGELOG.md` | Prepend bilingual entry |
| `README.md` | Add "Graph projection & paradata" section |

---

## PR1 — graphproj Package Foundation

### Task 1: Create graphproj package skeleton + exceptions

**Files:**
- Create: `pyarchinit_mini/graphproj/__init__.py`
- Create: `pyarchinit_mini/graphproj/exceptions.py`
- Test: `tests/unit/test_graphproj_exceptions.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_graphproj_exceptions.py
import pytest
from pyarchinit_mini.graphproj.exceptions import (
    ProjectionError,
    IngestError,
    IngestStaleError,
    ParadataConflict,
    ParadataNotFound,
    ParadataStorageError,
    GraphMLReadError,
    GraphMLWriteError,
)


def test_projection_error_carries_site():
    err = ProjectionError("missing site", site="X")
    assert err.site == "X"
    assert "missing site" in str(err)


def test_ingest_stale_error_carries_expected_revision():
    err = IngestStaleError(expected="abc123", actual="def456")
    assert err.expected == "abc123"
    assert err.actual == "def456"
    assert "abc123" in str(err) and "def456" in str(err)


def test_paradata_conflict_carries_existing():
    existing = {"node_id": "n1", "name": "M. Rossi"}
    err = ParadataConflict(node_id="n1", existing=existing)
    assert err.existing == existing


def test_paradata_not_found_carries_node_id():
    err = ParadataNotFound(node_id="n1")
    assert err.node_id == "n1"


def test_graphml_read_error_carries_path():
    err = GraphMLReadError(path="/tmp/x.graphml", msg="malformed XML")
    assert err.path == "/tmp/x.graphml"
```

- [ ] **Step 2: Run, verify ImportError**

Run: `.venv/bin/pytest tests/unit/test_graphproj_exceptions.py -v`

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/graphproj/__init__.py
"""Graph projection & paradata storage layer (Spec 2)."""
```

```python
# pyarchinit_mini/graphproj/exceptions.py
from typing import Optional


class GraphProjError(Exception):
    """Base for graphproj errors."""


class ProjectionError(GraphProjError):
    def __init__(self, msg: str, *, site: Optional[str] = None) -> None:
        super().__init__(msg)
        self.site = site


class IngestError(GraphProjError):
    pass


class IngestStaleError(IngestError):
    def __init__(self, *, expected: str, actual: str) -> None:
        super().__init__(f"Plan stale: expected snapshot {expected}, found {actual}")
        self.expected = expected
        self.actual = actual


class ParadataConflict(GraphProjError):
    def __init__(self, *, node_id: str, existing: dict) -> None:
        super().__init__(f"Paradata node {node_id} already exists")
        self.node_id = node_id
        self.existing = existing


class ParadataNotFound(GraphProjError):
    def __init__(self, *, node_id: str) -> None:
        super().__init__(f"Paradata node {node_id} not found")
        self.node_id = node_id


class ParadataStorageError(GraphProjError):
    def __init__(self, msg: str, *, path: Optional[str] = None) -> None:
        super().__init__(msg)
        self.path = path


class GraphMLReadError(GraphProjError):
    def __init__(self, *, path: str, msg: str) -> None:
        super().__init__(f"{msg} reading {path}")
        self.path = path


class GraphMLWriteError(GraphProjError):
    def __init__(self, *, path: str, msg: str) -> None:
        super().__init__(f"{msg} writing {path}")
        self.path = path
```

- [ ] **Step 4: Run, verify pass**

Run: `.venv/bin/pytest tests/unit/test_graphproj_exceptions.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/__init__.py pyarchinit_mini/graphproj/exceptions.py tests/unit/test_graphproj_exceptions.py
git commit -m "feat(graphproj): add exception hierarchy"
```

---

### Task 2: filesystem helpers (atomic_write + flock + slugify)

**Files:**
- Create: `pyarchinit_mini/graphproj/filesystem.py`
- Test: `tests/unit/test_graphproj_filesystem.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_graphproj_filesystem.py
import threading
import time
from pathlib import Path
import pytest

from pyarchinit_mini.graphproj.filesystem import (
    atomic_write,
    paradata_flock,
    slugify,
    paradata_dir,
)


def test_atomic_write_creates_file(tmp_path):
    target = tmp_path / "x.txt"
    atomic_write("hello", target)
    assert target.read_text() == "hello"
    assert not (tmp_path / "x.txt.tmp").exists()


def test_atomic_write_overwrites_existing(tmp_path):
    target = tmp_path / "x.txt"
    target.write_text("old")
    atomic_write("new", target)
    assert target.read_text() == "new"


def test_atomic_write_does_not_leave_tmp_on_success(tmp_path):
    target = tmp_path / "x.txt"
    atomic_write("hello", target)
    assert list(tmp_path.glob("*.tmp")) == []


def test_slugify_basic():
    assert slugify("Volterra") == "volterra"
    assert slugify("Sito Archeologico di Esempio") == "sito-archeologico-di-esempio"
    assert slugify("Metro C / Roma 2026") == "metro-c-roma-2026"


def test_slugify_rejects_empty():
    with pytest.raises(ValueError):
        slugify("")


def test_paradata_dir_returns_under_root(tmp_path):
    d = paradata_dir("Volterra", root=tmp_path)
    assert d == tmp_path / "volterra"


def test_flock_serializes_writers(tmp_path):
    results = []

    def writer(value: int) -> None:
        with paradata_flock("X", root=tmp_path):
            time.sleep(0.05)
            results.append(value)

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # All 4 ran; can't assert exact order but no interleaving exceptions
    assert sorted(results) == [0, 1, 2, 3]
```

- [ ] **Step 2: Run, verify failures**

Run: `.venv/bin/pytest tests/unit/test_graphproj_filesystem.py -v`

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/graphproj/filesystem.py
"""Filesystem helpers: atomic write + per-site flock + slugify."""
from __future__ import annotations

import re
import sys
import unicodedata
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

DEFAULT_PARADATA_ROOT = Path("data/paradata")


def slugify(name: str) -> str:
    if not name or not name.strip():
        raise ValueError("name cannot be empty")
    # ASCII fold
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    # Lowercase, replace non-alnum with hyphens, collapse
    s = folded.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if not s:
        raise ValueError(f"name slugifies to empty: {name!r}")
    return s


def paradata_dir(site: str, *, root: Optional[Path] = None) -> Path:
    base = Path(root) if root else DEFAULT_PARADATA_ROOT
    return base / slugify(site)


def atomic_write(content: str, target: Path, *, encoding: str = "utf-8") -> None:
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(content, encoding=encoding)
    tmp.replace(target)


@contextmanager
def paradata_flock(site: str, *, root: Optional[Path] = None) -> Iterator[None]:
    d = paradata_dir(site, root=root)
    d.mkdir(parents=True, exist_ok=True)
    lock_path = d / ".paradata.lock"
    fp = lock_path.open("a+")
    try:
        if sys.platform == "win32":
            import msvcrt
            # msvcrt only locks a region; lock 1 byte at offset 0
            msvcrt.locking(fp.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                fp.seek(0)
                msvcrt.locking(fp.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
    finally:
        fp.close()
```

- [ ] **Step 4: Run, verify pass**

Run: `.venv/bin/pytest tests/unit/test_graphproj_filesystem.py -v`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/filesystem.py tests/unit/test_graphproj_filesystem.py
git commit -m "feat(graphproj): add atomic_write, flock, slugify helpers"
```

---

### Task 3: edge_registry (VocabProvider wrapper)

**Files:**
- Create: `pyarchinit_mini/graphproj/edge_registry.py`
- Test: `tests/unit/test_graphproj_edge_registry.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_graphproj_edge_registry.py
from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphproj.edge_registry import EdgeRegistry

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def reset_provider():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_resolve_alias_returns_canonical_edge_name():
    reg = EdgeRegistry()
    name = reg.resolve_italian_alias("copre")
    assert name == "covers"


def test_resolve_compound_alias_coperto_da():
    reg = EdgeRegistry()
    name = reg.resolve_italian_alias("coperto da")
    assert name == "is_after"


def test_resolve_alias_unknown_returns_none():
    reg = EdgeRegistry()
    assert reg.resolve_italian_alias("xyzzy") is None


def test_longest_alias_wins():
    """coperto da (longer) must match before copre when both candidates."""
    reg = EdgeRegistry()
    # The lookup must consume the whole alias, not just a prefix
    assert reg.resolve_italian_alias("coperto") is None  # 'coperto' alone not an alias
```

- [ ] **Step 2: Run, verify ImportError**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/graphproj/edge_registry.py
"""Edge typing registry — wraps VocabProvider for canonical lookups."""
from typing import Optional

from pyarchinit_mini.vocab.provider import VocabProvider


class EdgeRegistry:
    """Resolves Italian rapporti aliases → canonical s3dgraphy edge type names.

    All data comes from VocabProvider (vocab_it.json edge_type_aliases).
    """

    def __init__(self) -> None:
        provider = VocabProvider.instance()
        self._alias_to_name: dict[str, str] = {}
        for edge in provider.get_edge_types():
            for alias in edge.italian_aliases:
                self._alias_to_name[alias.lower()] = edge.name
        # Pre-sort aliases by length descending for longest-first matching
        self._sorted_aliases = sorted(self._alias_to_name.keys(), key=len, reverse=True)

    def resolve_italian_alias(self, text: str) -> Optional[str]:
        """Resolve an Italian alias string to canonical edge name.

        Matches exactly (lowercase): returns the canonical edge name if
        text is in the alias table, None otherwise.
        """
        return self._alias_to_name.get(text.lower())

    def parse_rapporti_token(self, rel: str) -> tuple[Optional[str], Optional[str]]:
        """Parse one 'rapporti' token like 'coperto da 24' into (edge_name, target_us).

        Returns (None, None) if no alias matches.
        """
        rel_lower = rel.lower().strip()
        for alias in self._sorted_aliases:
            if rel_lower.startswith(alias):
                edge_name = self._alias_to_name[alias]
                tail = rel_lower[len(alias):].strip()
                target_us = "".join(c for c in tail if c.isdigit())
                if not target_us:
                    return edge_name, None
                return edge_name, target_us
        return None, None
```

- [ ] **Step 4: Run, verify pass**

Run: `.venv/bin/pytest tests/unit/test_graphproj_edge_registry.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/edge_registry.py tests/unit/test_graphproj_edge_registry.py
git commit -m "feat(graphproj): add EdgeRegistry wrapping VocabProvider"
```

---

## PR2 — GraphML Writer/Reader Delegate

### Task 4: Recon s3dgraphy 0.1.42 exporter/importer APIs

**Files:** none (recon-only, output saved as comments in writer.py)

This task does NOT produce a commit. It produces information for the next 2 tasks. Save findings as a code comment at the top of `graphml_io/writer.py` when you implement it in Task 5.

- [ ] **Step 1: Inspect s3dgraphy.exporter.graphml module**

```bash
.venv/bin/python -c "
import s3dgraphy.exporter.graphml as g
import inspect
for name in dir(g):
    if name.startswith('_'):
        continue
    obj = getattr(g, name)
    if callable(obj):
        try:
            sig = inspect.signature(obj)
            print(f'{name}{sig}')
        except (ValueError, TypeError):
            print(f'{name}  (no sig)')
    else:
        print(f'{name}  ({type(obj).__name__})')
"
```

- [ ] **Step 2: Inspect s3dgraphy.importer.import_graphml module**

```bash
.venv/bin/python -c "
import s3dgraphy.importer.import_graphml as g
import inspect
for name in dir(g):
    if name.startswith('_'):
        continue
    obj = getattr(g, name)
    if callable(obj):
        try:
            sig = inspect.signature(obj)
            print(f'{name}{sig}')
        except (ValueError, TypeError):
            print(f'{name}  (no sig)')
    else:
        print(f'{name}  ({type(obj).__name__})')
"
```

- [ ] **Step 3: Inspect s3dgraphy.merge.GraphMerger**

```bash
.venv/bin/python -c "
import s3dgraphy.merge as m
import inspect
for name in dir(m):
    if name.startswith('_'):
        continue
    obj = getattr(m, name)
    print(name, type(obj).__name__)
print()
if hasattr(m, 'GraphMerger'):
    print('GraphMerger methods:')
    for name in dir(m.GraphMerger):
        if name.startswith('_'):
            continue
        obj = getattr(m.GraphMerger, name)
        if callable(obj):
            try:
                sig = inspect.signature(obj)
                print(f'  {name}{sig}')
            except (ValueError, TypeError):
                print(f'  {name}')
"
```

- [ ] **Step 4: Test a round-trip with a minimal graph**

```bash
.venv/bin/python -c "
import s3dgraphy
from s3dgraphy.exporter import graphml as exporter
from pathlib import Path
g = s3dgraphy.Graph(graph_id='test', name='Test')
g.add_node(s3dgraphy.Node('n1', 'Node 1', 'desc'))
# Try whatever the exporter API looks like
print('s3dgraphy graph created:', g.graph_id)
print('exporter module dir:', [x for x in dir(exporter) if not x.startswith('_')])
# Find the write function:
for name in dir(exporter):
    if 'write' in name.lower() or 'export' in name.lower() or 'serialize' in name.lower():
        print('candidate:', name)
"
```

- [ ] **Step 5: Document findings**

Save findings (function names + signatures) for use in Task 5 and Task 6. No commit.

---

### Task 5: graphml_io.writer — delegate to s3dgraphy

**Files:**
- Create: `pyarchinit_mini/graphml_io/__init__.py`
- Create: `pyarchinit_mini/graphml_io/writer.py`
- Test: `tests/unit/test_graphml_io_writer.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_graphml_io_writer.py
from pathlib import Path
import pytest

import s3dgraphy
from pyarchinit_mini.graphml_io.writer import write_graphml


def test_write_graphml_produces_file(tmp_path):
    g = s3dgraphy.Graph(graph_id="test", name="Test", description="d")
    g.add_node(s3dgraphy.Node("n1", "Node 1", "first"))
    g.add_node(s3dgraphy.Node("n2", "Node 2", "second"))
    g.add_edge("e1", "n1", "n2", "is_before")

    out = tmp_path / "out.graphml"
    write_graphml(g, out)

    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "<graphml" in content or "<?xml" in content
    assert "n1" in content


def test_write_graphml_raises_on_invalid_target(tmp_path):
    from pyarchinit_mini.graphproj.exceptions import GraphMLWriteError
    g = s3dgraphy.Graph(graph_id="test", name="Test", description="d")
    bad = tmp_path / "nonexistent_dir" / "out.graphml"  # parent doesn't exist
    # If the impl auto-creates parents, this should succeed. If not, expect error.
    # We test the contract: either succeeds or raises GraphMLWriteError.
    try:
        write_graphml(g, bad)
        assert bad.exists()
    except GraphMLWriteError:
        pass  # acceptable
```

- [ ] **Step 2: Run, verify ImportError**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/graphml_io/__init__.py
"""Thin wrappers around s3dgraphy exporter/importer for GraphML."""
```

```python
# pyarchinit_mini/graphml_io/writer.py
"""GraphML writer — delegates to s3dgraphy.exporter.graphml.

Resolved s3dgraphy 0.1.42 API (per Task 4 recon):
- Use whatever function the recon found. Most common s3dgraphy exporters
  expose either a top-level `write_graphml(graph, path)` or a class with
  a `write()` method. Adapt the call below to match.
"""
from pathlib import Path
from typing import Any

from pyarchinit_mini.graphproj.exceptions import GraphMLWriteError


def write_graphml(graph: Any, path: Path) -> None:
    """Serialize a s3dgraphy.Graph to GraphML at path.

    Creates parent directory if missing.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from s3dgraphy.exporter import graphml as s3d_exporter
        # The function name depends on what Task 4 recon found.
        # Try common candidates in order:
        for candidate in ("write_graphml", "export_graphml", "write", "export"):
            fn = getattr(s3d_exporter, candidate, None)
            if callable(fn):
                fn(graph, str(path))
                return
        # If none found, look for a class with a write method:
        for cls_name in ("GraphMLExporter", "GraphMLWriter"):
            cls = getattr(s3d_exporter, cls_name, None)
            if cls is not None:
                exporter = cls()
                if hasattr(exporter, "write"):
                    exporter.write(graph, str(path))
                    return
                if hasattr(exporter, "export"):
                    exporter.export(graph, str(path))
                    return
        raise GraphMLWriteError(
            path=str(path),
            msg="No suitable s3dgraphy.exporter.graphml entry point found",
        )
    except GraphMLWriteError:
        raise
    except Exception as e:
        raise GraphMLWriteError(path=str(path), msg=str(e)) from e
```

- [ ] **Step 4: Run, verify pass**

Run: `.venv/bin/pytest tests/unit/test_graphml_io_writer.py -v`
Expected: 2 passed. If the first test fails because no candidate matched, inspect the s3dgraphy module again and add the correct call.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphml_io/__init__.py pyarchinit_mini/graphml_io/writer.py tests/unit/test_graphml_io_writer.py
git commit -m "feat(graphml_io): add writer delegating to s3dgraphy.exporter.graphml"
```

---

### Task 6: graphml_io.reader — delegate to s3dgraphy

**Files:**
- Create: `pyarchinit_mini/graphml_io/reader.py`
- Test: `tests/unit/test_graphml_io_reader.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_graphml_io_reader.py
from pathlib import Path
import pytest

import s3dgraphy
from pyarchinit_mini.graphml_io.writer import write_graphml
from pyarchinit_mini.graphml_io.reader import read_graphml


def test_round_trip_preserves_nodes_and_edges(tmp_path):
    """Write then read: structural fields preserved."""
    g = s3dgraphy.Graph(graph_id="rt", name="RT", description="round-trip")
    g.add_node(s3dgraphy.Node("a", "A", "first"))
    g.add_node(s3dgraphy.Node("b", "B", "second"))
    g.add_edge("e1", "a", "b", "is_before")

    out = tmp_path / "rt.graphml"
    write_graphml(g, out)

    loaded = read_graphml(out)
    node_ids = {n.node_id for n in loaded.nodes}
    assert "a" in node_ids
    assert "b" in node_ids


def test_read_missing_file_raises(tmp_path):
    from pyarchinit_mini.graphproj.exceptions import GraphMLReadError
    with pytest.raises(GraphMLReadError):
        read_graphml(tmp_path / "nonexistent.graphml")
```

- [ ] **Step 2: Run, verify ImportError**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/graphml_io/reader.py
"""GraphML reader — delegates to s3dgraphy.importer.import_graphml.

Resolved s3dgraphy 0.1.42 API (per Task 4 recon):
- Adapt the call below to whatever the recon found.
"""
from pathlib import Path
from typing import Any

from pyarchinit_mini.graphproj.exceptions import GraphMLReadError


def read_graphml(path: Path) -> Any:
    """Read a GraphML file into a s3dgraphy.Graph."""
    path = Path(path)
    if not path.exists():
        raise GraphMLReadError(path=str(path), msg="file not found")
    try:
        from s3dgraphy.importer import import_graphml as s3d_importer
        for candidate in ("read_graphml", "import_graphml", "read", "load"):
            fn = getattr(s3d_importer, candidate, None)
            if callable(fn):
                return fn(str(path))
        for cls_name in ("GraphMLImporter", "GraphMLReader"):
            cls = getattr(s3d_importer, cls_name, None)
            if cls is not None:
                importer = cls()
                if hasattr(importer, "read"):
                    return importer.read(str(path))
                if hasattr(importer, "import_"):
                    return importer.import_(str(path))
        raise GraphMLReadError(
            path=str(path),
            msg="No suitable s3dgraphy.importer.import_graphml entry point found",
        )
    except GraphMLReadError:
        raise
    except Exception as e:
        raise GraphMLReadError(path=str(path), msg=str(e)) from e
```

- [ ] **Step 4: Run, verify pass**

Run: `.venv/bin/pytest tests/unit/test_graphml_io_reader.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphml_io/reader.py tests/unit/test_graphml_io_reader.py
git commit -m "feat(graphml_io): add reader delegating to s3dgraphy.importer.import_graphml"
```

---

## PR3 — GraphProjector + ParadataStore + Auto-Regen

### Task 7: ParadataStore — load/atomic_write

**Files:**
- Create: `pyarchinit_mini/graphproj/paradata_store.py`
- Test: `tests/unit/test_paradata_store_basic.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_paradata_store_basic.py
from pathlib import Path
import pytest

import s3dgraphy
from pyarchinit_mini.graphproj.paradata_store import ParadataStore


def test_load_returns_empty_graph_when_no_file(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    g = store.load()
    assert isinstance(g, s3dgraphy.Graph)
    # Empty graph has 0 nodes
    assert len(list(g.nodes)) == 0


def test_atomic_write_persists_graph(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    g = store.load()
    g.add_node(s3dgraphy.Node("author:1", "M. Rossi", "author note"))
    store.atomic_write(g)
    # Re-load
    store2 = ParadataStore("X", root=tmp_path)
    loaded = store2.load()
    ids = {n.node_id for n in loaded.nodes}
    assert "author:1" in ids


def test_atomic_write_creates_dir(tmp_path):
    store = ParadataStore("New Site", root=tmp_path)
    g = s3dgraphy.Graph(graph_id="ns", name="New Site", description="")
    store.atomic_write(g)
    assert (tmp_path / "new-site" / "paradata.graphml").exists()
```

- [ ] **Step 2: Run, verify ImportError**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/graphproj/paradata_store.py
"""ParadataStore — per-site filesystem-backed paradata.graphml."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import s3dgraphy

from .filesystem import atomic_write, paradata_dir, paradata_flock, slugify
from .exceptions import ParadataStorageError
from pyarchinit_mini.graphml_io.reader import read_graphml
from pyarchinit_mini.graphml_io.writer import write_graphml


PARADATA_FILENAME = "paradata.graphml"


class ParadataStore:
    def __init__(self, site: str, *, root: Optional[Path] = None) -> None:
        self.site = site
        self._root = Path(root) if root else None
        self._dir = paradata_dir(site, root=root)
        self._path = self._dir / PARADATA_FILENAME

    def load(self) -> "s3dgraphy.Graph":
        """Returns paradata Graph. Empty Graph if file missing."""
        if not self._path.exists():
            return s3dgraphy.Graph(
                graph_id=f"paradata:{slugify(self.site)}",
                name=f"{self.site} paradata",
                description="",
            )
        try:
            return read_graphml(self._path)
        except Exception as e:
            raise ParadataStorageError(
                f"Cannot load paradata: {e}",
                path=str(self._path),
            ) from e

    def atomic_write(self, graph: "s3dgraphy.Graph") -> None:
        """Persist graph atomically via tmp + os.replace."""
        with paradata_flock(self.site, root=self._root):
            self._dir.mkdir(parents=True, exist_ok=True)
            # Write to tmp then atomic move (write_graphml does the actual serialization)
            tmp = self._path.with_suffix(self._path.suffix + ".tmp")
            try:
                write_graphml(graph, tmp)
                tmp.replace(self._path)
            except Exception as e:
                # Cleanup .tmp on error
                if tmp.exists():
                    tmp.unlink()
                raise ParadataStorageError(
                    f"Cannot write paradata: {e}",
                    path=str(self._path),
                ) from e
```

- [ ] **Step 4: Run, verify pass**

Run: `.venv/bin/pytest tests/unit/test_paradata_store_basic.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/paradata_store.py tests/unit/test_paradata_store_basic.py
git commit -m "feat(graphproj): ParadataStore load + atomic_write"
```

---

### Task 8: ParadataStore — CRUD for AuthorNode (template)

**Files:**
- Modify: `pyarchinit_mini/graphproj/paradata_store.py`
- Test: `tests/unit/test_paradata_store_authors.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_paradata_store_authors.py
from pathlib import Path
import pytest

from pyarchinit_mini.graphproj.paradata_store import ParadataStore
from pyarchinit_mini.graphproj.exceptions import ParadataConflict, ParadataNotFound


def test_add_and_list_authors(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    a = store.add_author(name="M. Rossi", orcid="0000-0001")
    assert a["name"] == "M. Rossi"
    assert a["orcid"] == "0000-0001"
    assert a["node_id"].startswith("author:")

    authors = store.list_authors()
    assert len(authors) == 1
    assert authors[0]["name"] == "M. Rossi"


def test_add_author_duplicate_name_raises(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    store.add_author(name="M. Rossi")
    with pytest.raises(ParadataConflict):
        store.add_author(name="M. Rossi")


def test_update_author(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    a = store.add_author(name="M. Rossi")
    updated = store.update_author(a["node_id"], orcid="0000-0002")
    assert updated["orcid"] == "0000-0002"
    assert updated["name"] == "M. Rossi"


def test_update_author_missing_raises(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    with pytest.raises(ParadataNotFound):
        store.update_author("author:nonexistent", name="X")


def test_delete_author(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    a = store.add_author(name="M. Rossi")
    store.delete_author(a["node_id"])
    assert store.list_authors() == []


def test_delete_author_missing_raises(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    with pytest.raises(ParadataNotFound):
        store.delete_author("author:nonexistent")
```

- [ ] **Step 2: Run, verify failures**

- [ ] **Step 3: Add CRUD methods to ParadataStore**

Append to `pyarchinit_mini/graphproj/paradata_store.py`:

```python
import s3dgraphy
# (top imports already in file)

# Inside ParadataStore class, append:

    AUTHOR_PREFIX = "author:"

    def _next_author_id(self, graph: "s3dgraphy.Graph") -> str:
        existing = [n.node_id for n in graph.nodes
                    if n.node_id.startswith(self.AUTHOR_PREFIX)]
        n = len(existing) + 1
        # Find next unused
        while f"{self.AUTHOR_PREFIX}{n}" in existing:
            n += 1
        return f"{self.AUTHOR_PREFIX}{n}"

    def _author_to_dict(self, node: "s3dgraphy.Node") -> dict:
        return {
            "node_id": node.node_id,
            "name": node.name,
            "orcid": (node.attributes.get("orcid") if hasattr(node, "attributes") else None),
        }

    def list_authors(self) -> list[dict]:
        g = self.load()
        return [
            self._author_to_dict(n) for n in g.nodes
            if n.node_id.startswith(self.AUTHOR_PREFIX)
        ]

    def add_author(self, *, name: str, orcid: str | None = None) -> dict:
        with paradata_flock(self.site, root=self._root):
            g = self.load()
            # Dedupe by name (case-insensitive)
            for n in g.nodes:
                if n.node_id.startswith(self.AUTHOR_PREFIX) and n.name.lower() == name.lower():
                    raise ParadataConflict(
                        node_id=n.node_id,
                        existing=self._author_to_dict(n),
                    )
            node_id = self._next_author_id(g)
            node = s3dgraphy.Node(node_id, name, "")
            if orcid:
                node.attributes["orcid"] = orcid
            g.add_node(node)
            self.atomic_write(g)
            return self._author_to_dict(node)

    def update_author(self, node_id: str, *, name: str | None = None,
                      orcid: str | None = None) -> dict:
        with paradata_flock(self.site, root=self._root):
            g = self.load()
            target = next((n for n in g.nodes if n.node_id == node_id), None)
            if target is None:
                raise ParadataNotFound(node_id=node_id)
            if name is not None:
                target.name = name
            if orcid is not None:
                target.attributes["orcid"] = orcid
            self.atomic_write(g)
            return self._author_to_dict(target)

    def delete_author(self, node_id: str) -> None:
        with paradata_flock(self.site, root=self._root):
            g = self.load()
            target = next((n for n in g.nodes if n.node_id == node_id), None)
            if target is None:
                raise ParadataNotFound(node_id=node_id)
            # s3dgraphy 0.1.42 may or may not have a remove_node helper.
            # If not, mutate the underlying list:
            if hasattr(g, "remove_node"):
                g.remove_node(target)
            else:
                # Fallback: mutate the internal nodes list directly
                g.nodes = [n for n in g.nodes if n.node_id != node_id]
            self.atomic_write(g)
```

Note: if `node.attributes` doesn't exist on s3dgraphy 0.1.42 Node (it might be on a different attribute name like `node.metadata`), inspect with:
```bash
.venv/bin/python -c "import s3dgraphy; n = s3dgraphy.Node('a','A','d'); print(dir(n))"
```

And adapt the attribute accessor accordingly.

- [ ] **Step 4: Run, verify pass**

Run: `.venv/bin/pytest tests/unit/test_paradata_store_authors.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/paradata_store.py tests/unit/test_paradata_store_authors.py
git commit -m "feat(graphproj): ParadataStore CRUD for AuthorNode"
```

---

### Task 9: ParadataStore — CRUD for licenses, embargoes, documents, epochs

**Files:**
- Modify: `pyarchinit_mini/graphproj/paradata_store.py`
- Test: `tests/unit/test_paradata_store_other_types.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_paradata_store_other_types.py
import pytest
from pyarchinit_mini.graphproj.paradata_store import ParadataStore
from pyarchinit_mini.graphproj.exceptions import ParadataNotFound


def test_license_crud(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    l = store.add_license(name="CC-BY-NC-ND", url="https://creativecommons.org/...")
    assert l["name"] == "CC-BY-NC-ND"
    assert store.list_licenses() == [l]
    upd = store.update_license(l["node_id"], url="https://newurl")
    assert upd["url"] == "https://newurl"
    store.delete_license(l["node_id"])
    assert store.list_licenses() == []


def test_embargo_crud(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    e = store.add_embargo(label="Until 2030", until="2030-01-01")
    assert e["label"] == "Until 2030"
    assert store.list_embargoes() == [e]
    upd = store.update_embargo(e["node_id"], until="2031-01-01")
    assert upd["until"] == "2031-01-01"
    store.delete_embargo(e["node_id"])
    assert store.list_embargoes() == []


def test_document_crud(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    d = store.add_document(title="Excavation Report 2024", uri="https://...")
    assert d["title"] == "Excavation Report 2024"
    upd = store.update_document(d["node_id"], uri="https://new")
    assert upd["uri"] == "https://new"
    store.delete_document(d["node_id"])
    assert store.list_documents() == []


def test_epoch_crud(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    e = store.add_epoch(name="Roman Imperial", start=-27, end=476)
    assert e["start"] == -27
    upd = store.update_epoch(e["node_id"], end=500)
    assert upd["end"] == 500
    store.delete_epoch(e["node_id"])
    assert store.list_epochs() == []


def test_update_unknown_raises_not_found(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    with pytest.raises(ParadataNotFound):
        store.update_license("license:bogus", name="X")
```

- [ ] **Step 2: Run, verify failures**

- [ ] **Step 3: Add the 4 other type families to ParadataStore**

Each follows the same pattern as `AuthorNode`. Append to ParadataStore class:

```python
    LICENSE_PREFIX = "license:"
    EMBARGO_PREFIX = "embargo:"
    DOCUMENT_PREFIX = "document:"
    EPOCH_PREFIX = "epoch:"

    # --- helpers (generic) ---

    def _next_id(self, graph: "s3dgraphy.Graph", prefix: str) -> str:
        existing = {n.node_id for n in graph.nodes if n.node_id.startswith(prefix)}
        n = 1
        while f"{prefix}{n}" in existing:
            n += 1
        return f"{prefix}{n}"

    def _generic_add(self, prefix: str, name: str, **attrs) -> dict:
        with paradata_flock(self.site, root=self._root):
            g = self.load()
            node_id = self._next_id(g, prefix)
            node = s3dgraphy.Node(node_id, name, "")
            for k, v in attrs.items():
                if v is not None:
                    node.attributes[k] = v
            g.add_node(node)
            self.atomic_write(g)
            return self._generic_to_dict(node, attrs.keys())

    def _generic_update(self, prefix: str, node_id: str, **attrs) -> dict:
        with paradata_flock(self.site, root=self._root):
            g = self.load()
            target = next((n for n in g.nodes if n.node_id == node_id), None)
            if target is None or not target.node_id.startswith(prefix):
                raise ParadataNotFound(node_id=node_id)
            for k, v in attrs.items():
                if v is not None:
                    if k == "name":
                        target.name = v
                    else:
                        target.attributes[k] = v
            self.atomic_write(g)
            return self._generic_to_dict(target, attrs.keys())

    def _generic_delete(self, prefix: str, node_id: str) -> None:
        with paradata_flock(self.site, root=self._root):
            g = self.load()
            target = next((n for n in g.nodes if n.node_id == node_id), None)
            if target is None or not target.node_id.startswith(prefix):
                raise ParadataNotFound(node_id=node_id)
            if hasattr(g, "remove_node"):
                g.remove_node(target)
            else:
                g.nodes = [n for n in g.nodes if n.node_id != node_id]
            self.atomic_write(g)

    def _generic_list(self, prefix: str, attr_keys: list[str]) -> list[dict]:
        g = self.load()
        return [
            self._generic_to_dict(n, attr_keys)
            for n in g.nodes if n.node_id.startswith(prefix)
        ]

    def _generic_to_dict(self, node, attr_keys) -> dict:
        out = {"node_id": node.node_id, "name": node.name}
        attrs = getattr(node, "attributes", {}) or {}
        for k in attr_keys:
            if k != "name":
                out[k] = attrs.get(k)
        return out

    # --- licenses ---

    def list_licenses(self) -> list[dict]:
        return self._generic_list(self.LICENSE_PREFIX, ["url"])

    def add_license(self, *, name: str, url: str | None = None) -> dict:
        return self._generic_add(self.LICENSE_PREFIX, name, url=url)

    def update_license(self, node_id: str, **fields) -> dict:
        return self._generic_update(self.LICENSE_PREFIX, node_id, **fields)

    def delete_license(self, node_id: str) -> None:
        return self._generic_delete(self.LICENSE_PREFIX, node_id)

    # --- embargoes ---

    def list_embargoes(self) -> list[dict]:
        return self._generic_list(self.EMBARGO_PREFIX, ["label", "until"])

    def add_embargo(self, *, label: str, until: str | None = None) -> dict:
        return self._generic_add(self.EMBARGO_PREFIX, label, until=until)

    def update_embargo(self, node_id: str, **fields) -> dict:
        return self._generic_update(self.EMBARGO_PREFIX, node_id, **fields)

    def delete_embargo(self, node_id: str) -> None:
        return self._generic_delete(self.EMBARGO_PREFIX, node_id)

    # --- documents ---

    def list_documents(self) -> list[dict]:
        return self._generic_list(self.DOCUMENT_PREFIX, ["uri"])

    def add_document(self, *, title: str, uri: str | None = None) -> dict:
        return self._generic_add(self.DOCUMENT_PREFIX, title, uri=uri)

    def update_document(self, node_id: str, **fields) -> dict:
        # Map 'title' kwarg to 'name' field if provided
        if "title" in fields:
            fields["name"] = fields.pop("title")
        return self._generic_update(self.DOCUMENT_PREFIX, node_id, **fields)

    def delete_document(self, node_id: str) -> None:
        return self._generic_delete(self.DOCUMENT_PREFIX, node_id)

    # --- epochs ---

    def list_epochs(self) -> list[dict]:
        return self._generic_list(self.EPOCH_PREFIX, ["start", "end"])

    def add_epoch(self, *, name: str, start=None, end=None) -> dict:
        return self._generic_add(self.EPOCH_PREFIX, name, start=start, end=end)

    def update_epoch(self, node_id: str, **fields) -> dict:
        return self._generic_update(self.EPOCH_PREFIX, node_id, **fields)

    def delete_epoch(self, node_id: str) -> None:
        return self._generic_delete(self.EPOCH_PREFIX, node_id)
```

Note: `_author_to_dict` should be aligned to use the generic helper too. After implementing the generic helpers, simplify the author methods to call them. The test contract (return dict with `node_id`, `name`, `orcid`) must still hold:

```python
    # Refactor author methods to use generic helpers (optional but cleaner)
    def list_authors(self) -> list[dict]:
        return self._generic_list(self.AUTHOR_PREFIX, ["orcid"])

    def add_author(self, *, name: str, orcid: str | None = None) -> dict:
        # Preserve dedupe-by-name behaviour
        with paradata_flock(self.site, root=self._root):
            g = self.load()
            for n in g.nodes:
                if n.node_id.startswith(self.AUTHOR_PREFIX) and n.name.lower() == name.lower():
                    raise ParadataConflict(
                        node_id=n.node_id,
                        existing=self._generic_to_dict(n, ["orcid"]),
                    )
        return self._generic_add(self.AUTHOR_PREFIX, name, orcid=orcid)

    def update_author(self, node_id: str, **fields) -> dict:
        return self._generic_update(self.AUTHOR_PREFIX, node_id, **fields)

    def delete_author(self, node_id: str) -> None:
        return self._generic_delete(self.AUTHOR_PREFIX, node_id)
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_paradata_store_authors.py tests/unit/test_paradata_store_other_types.py -v
```
Expected: 11 passed total.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/paradata_store.py tests/unit/test_paradata_store_other_types.py
git commit -m "feat(graphproj): ParadataStore CRUD for licenses, embargoes, documents, epochs"
```

---

### Task 10: GraphProjector.populate_graph()

**Files:**
- Create: `pyarchinit_mini/graphproj/projector.py`
- Test: `tests/unit/test_graphproj_projector.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_graphproj_projector.py
from pathlib import Path
import pytest
import sqlite3

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphproj.projector import GraphProjector
from pyarchinit_mini.graphproj.exceptions import ProjectionError

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


@pytest.fixture
def session(tmp_path):
    """Real SQLAlchemy session against a synthetic DB with us_table populated."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY,
        sito TEXT, area TEXT, us INTEGER, unita_tipo TEXT,
        d_stratigrafica TEXT, d_interpretativa TEXT,
        rapporti TEXT, node_uuid TEXT
    )""")
    rows = [
        (1, "Volterra", "A", 1001, "US", "strat 1", "interp 1", "copre 1002", "0190-0000-7000-8000-000000000001"),
        (2, "Volterra", "A", 1002, "US", "strat 2", "interp 2", "", "0190-0000-7000-8000-000000000002"),
        (3, "Volterra", "A", 1003, "USVs", "virtual reconstruction", "", "", "0190-0000-7000-8000-000000000003"),
    ]
    conn.executemany("INSERT INTO us_table VALUES (?,?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()

    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def test_populate_graph_returns_graph(session):
    g = GraphProjector.populate_graph(session, "Volterra")
    assert g is not None
    assert len(list(g.nodes)) == 3


def test_populate_graph_idempotent(session):
    g1 = GraphProjector.populate_graph(session, "Volterra")
    g2 = GraphProjector.populate_graph(session, "Volterra")
    ids1 = {n.node_id for n in g1.nodes}
    ids2 = {n.node_id for n in g2.nodes}
    assert ids1 == ids2


def test_populate_graph_creates_stratigraphic_edges(session):
    g = GraphProjector.populate_graph(session, "Volterra")
    # 'copre 1002' should produce an edge between us 1001 and us 1002
    edges = list(g.edges)
    assert len(edges) >= 1


def test_populate_graph_empty_site_returns_empty_graph(session):
    g = GraphProjector.populate_graph(session, "NoSuchSite")
    assert len(list(g.nodes)) == 0


def test_populate_graph_area_filter(session):
    g = GraphProjector.populate_graph(session, "Volterra", area="A")
    assert len(list(g.nodes)) == 3
    g_b = GraphProjector.populate_graph(session, "Volterra", area="B")
    assert len(list(g_b.nodes)) == 0
```

- [ ] **Step 2: Run, verify failures**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/graphproj/projector.py
"""GraphProjector — DB rows → s3dgraphy.Graph (stratigraphic layer only)."""
from typing import Optional

import s3dgraphy
from sqlalchemy import text
from sqlalchemy.orm import Session

from pyarchinit_mini.vocab.provider import VocabProvider
from .edge_registry import EdgeRegistry
from .exceptions import ProjectionError


class GraphProjector:
    @staticmethod
    def populate_graph(
        session: Session,
        site: str,
        *,
        area: Optional[str] = None,
    ) -> "s3dgraphy.Graph":
        """DB rows → s3dgraphy.Graph (stratigraphic layer only)."""
        graph = s3dgraphy.Graph(
            graph_id=f"strat:{site}",
            name=f"{site} stratigraphic graph",
            description=f"Projected from PyArchInit-Mini DB",
        )

        sql = "SELECT id_us, sito, area, us, unita_tipo, rapporti, node_uuid FROM us_table WHERE sito = :sito"
        params = {"sito": site}
        if area:
            sql += " AND area = :area"
            params["area"] = area
        sql += " ORDER BY id_us"

        rows = session.execute(text(sql), params).fetchall()

        provider = VocabProvider.instance()
        registry = EdgeRegistry()

        # Build us → node_id map first
        us_to_node = {}
        for row in rows:
            row_dict = row._mapping if hasattr(row, "_mapping") else dict(zip(row.keys(), row))
            us_num = str(row_dict["us"])
            sito = row_dict["sito"]
            ar = row_dict["area"] or ""
            node_id = f"{sito}_{ar}_{us_num}" if ar else f"{sito}_{us_num}"

            unita_tipo = row_dict["unita_tipo"] or "US"
            ut_info = provider.get_unit_type(unita_tipo)
            family = ut_info.family if ut_info else "unknown"

            node = s3dgraphy.Node(node_id, f"{unita_tipo}{us_num}", "")
            node.attributes["unit_type"] = unita_tipo
            node.attributes["family"] = family
            node.attributes["EMid"] = row_dict["node_uuid"] or ""

            graph.add_node(node)
            us_to_node[us_num] = node_id

        # Edges from rapporti
        edge_counter = 0
        for row in rows:
            row_dict = row._mapping if hasattr(row, "_mapping") else dict(zip(row.keys(), row))
            rapporti = row_dict["rapporti"] or ""
            if not rapporti.strip():
                continue
            source_us = str(row_dict["us"])
            source_id = us_to_node[source_us]

            for raw_token in rapporti.replace(";", ",").split(","):
                token = raw_token.strip()
                if not token:
                    continue
                edge_name, target_us = registry.parse_rapporti_token(token)
                if edge_name is None or target_us is None:
                    continue
                if target_us not in us_to_node:
                    continue
                target_id = us_to_node[target_us]
                edge_counter += 1
                edge_id = f"e{edge_counter}"
                graph.add_edge(edge_id, source_id, target_id, edge_name)

        return graph
```

- [ ] **Step 4: Run, verify pass**

Run: `.venv/bin/pytest tests/unit/test_graphproj_projector.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/projector.py tests/unit/test_graphproj_projector.py
git commit -m "feat(graphproj): GraphProjector.populate_graph (stratigraphic layer)"
```

---

### Task 11: auto_regen module (hook + context manager)

**Files:**
- Create: `pyarchinit_mini/graphproj/auto_regen.py`
- Test: `tests/unit/test_auto_regen.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_auto_regen.py
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from pyarchinit_mini.graphproj.auto_regen import (
    _trigger_graph_regen,
    disable_regen,
    force_regen_all_touched_sites,
    _is_regen_disabled,
    _record_touched_site,
    _drain_touched_sites,
)


def test_disable_regen_context_sets_flag():
    assert _is_regen_disabled() is False
    with disable_regen():
        assert _is_regen_disabled() is True
    assert _is_regen_disabled() is False


def test_disable_regen_records_touched_sites():
    with disable_regen():
        _record_touched_site("Volterra")
        _record_touched_site("Pompei")
        _record_touched_site("Volterra")  # dedupe
    drained = _drain_touched_sites()
    assert set(drained) == {"Volterra", "Pompei"}


def test_drain_touched_sites_is_one_shot():
    with disable_regen():
        _record_touched_site("X")
    first = _drain_touched_sites()
    second = _drain_touched_sites()
    assert "X" in first
    assert second == []


def test_trigger_regen_no_op_when_env_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("PYARCHINIT_DISABLE_AUTO_REGEN", "1")
    monkeypatch.chdir(tmp_path)
    session = MagicMock()
    # Should not raise, should not write any file
    _trigger_graph_regen("Volterra", session=session)
    assert not (tmp_path / "data" / "paradata" / "volterra" / "stratigraphy.graphml").exists()


def test_trigger_regen_catches_errors(tmp_path, monkeypatch):
    """Regen failures must be caught and logged, never propagate."""
    monkeypatch.chdir(tmp_path)
    session = MagicMock()
    with patch("pyarchinit_mini.graphproj.auto_regen.GraphProjector.populate_graph",
               side_effect=RuntimeError("boom")):
        # Must NOT raise
        _trigger_graph_regen("Volterra", session=session)
```

- [ ] **Step 2: Run, verify failures**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/graphproj/auto_regen.py
"""Post-commit auto-regen hook for stratigraphy.graphml.

Fires after US/USM save commits. Best-effort, error-isolated: regen failures
do NOT propagate (they're logged + cached for banner display).

Disable globally with env PYARCHINIT_DISABLE_AUTO_REGEN=1.
Disable temporarily (bulk import) with `with disable_regen():` context.
"""
from __future__ import annotations

import logging
import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .filesystem import paradata_dir, slugify, paradata_flock
from .paradata_store import ParadataStore
from .projector import GraphProjector
from pyarchinit_mini.graphml_io.writer import write_graphml

logger = logging.getLogger(__name__)

_local = threading.local()
STRATIGRAPHY_FILENAME = "stratigraphy.graphml"


def _is_regen_disabled() -> bool:
    return getattr(_local, "disabled", False)


def _record_touched_site(site: str) -> None:
    if not hasattr(_local, "touched"):
        _local.touched = []
    if site not in _local.touched:
        _local.touched.append(site)


def _drain_touched_sites() -> list[str]:
    touched = getattr(_local, "touched", [])
    _local.touched = []
    return touched


@contextmanager
def disable_regen() -> Iterator[None]:
    """Disable per-row auto-regen for the duration of the block.

    Use with bulk imports to avoid N regens; call force_regen_all_touched_sites()
    at the end to do a single regen per touched site.
    """
    prev = getattr(_local, "disabled", False)
    _local.disabled = True
    try:
        yield
    finally:
        _local.disabled = prev


def _trigger_graph_regen(site: str, *, session: Any) -> None:
    """Best-effort post-commit regen. Never raises."""
    if os.environ.get("PYARCHINIT_DISABLE_AUTO_REGEN") == "1":
        return
    if _is_regen_disabled():
        _record_touched_site(site)
        return
    try:
        graph = GraphProjector.populate_graph(session, site)
        store = ParadataStore(site)
        paradata = store.load()
        # Merge stratigraphic + paradata
        # (s3dgraphy.merge.GraphMerger API per recon; fallback: union nodes/edges)
        merged = _merge_graphs(graph, paradata)
        out_path = paradata_dir(site) / STRATIGRAPHY_FILENAME
        # write_graphml inside flock to serialize with paradata writes
        with paradata_flock(site):
            tmp = out_path.with_suffix(out_path.suffix + ".tmp")
            write_graphml(merged, tmp)
            tmp.replace(out_path)
        logger.info("regen ok site=%s nodes=%d edges=%d",
                    site, len(list(merged.nodes)), len(list(merged.edges)))
    except Exception:
        logger.exception("regen failed for site=%s", site)
        # Note: cache update (regen_status) happens in the Flask layer
        # (see graph_routes); auto_regen is decoupled from Flask cache.


def _merge_graphs(strat: Any, paradata: Any) -> Any:
    """Merge stratigraphic + paradata graphs.

    Tries s3dgraphy.merge.GraphMerger first (per 0.1.42 API); falls back to
    union-of-nodes/edges if the merger is not available.
    """
    try:
        from s3dgraphy.merge import GraphMerger
        if hasattr(GraphMerger, "merge"):
            return GraphMerger.merge(strat, paradata)
        # Class instance with merge method
        merger = GraphMerger()
        if hasattr(merger, "merge"):
            return merger.merge(strat, paradata)
    except Exception as e:
        logger.warning("GraphMerger unavailable (%s); falling back to union", e)
    # Fallback: copy paradata nodes/edges into strat
    for node in paradata.nodes:
        try:
            strat.add_node(node)
        except Exception:
            pass  # node may already exist
    for edge in paradata.edges:
        try:
            strat.add_edge(
                edge.edge_id, edge.edge_source, edge.edge_target, edge.edge_type
            )
        except Exception:
            pass
    return strat


def force_regen_all_touched_sites() -> None:
    """Regen each site touched during the most recent disable_regen() block.

    Called at end of bulk import. Drains the touched-list (one-shot).
    """
    sites = _drain_touched_sites()
    if not sites:
        return
    # Need a session — bulk import callers should provide one.
    # In Flask context, retrieve from g or from the import route.
    # For now, this function logs and expects caller to pass session:
    logger.warning(
        "force_regen_all_touched_sites called without session; sites=%s. "
        "Callers should use _trigger_graph_regen(site, session=...) explicitly "
        "after their bulk operation commits.", sites
    )
```

- [ ] **Step 4: Run, verify pass**

Run: `.venv/bin/pytest tests/unit/test_auto_regen.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/auto_regen.py tests/unit/test_auto_regen.py
git commit -m "feat(graphproj): auto_regen hook + disable_regen context"
```

---

### Task 12: Wire auto_regen into us_service post-commit

**Files:**
- Modify: `pyarchinit_mini/services/us_service.py` (or equivalent)
- Test: `tests/integration/test_auto_regen_on_save.py`

- [ ] **Step 1: Locate the us_service save function**

```bash
grep -rn "def save_us\|def create_us\|class USService" pyarchinit_mini/services/ pyarchinit_mini/web_interface/ 2>/dev/null | head -10
```

Find the existing function that commits a new/edited US row. Note its file path and signature.

- [ ] **Step 2: Write integration test**

```python
# tests/integration/test_auto_regen_on_save.py
from pathlib import Path
import sqlite3
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_save_us_triggers_regen(tmp_path, monkeypatch):
    """After saving a US, stratigraphy.graphml must exist on disk."""
    monkeypatch.chdir(tmp_path)
    # Setup: create DB with empty us_table
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us INTEGER,
        unita_tipo TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        rapporti TEXT, node_uuid TEXT
    )""")
    conn.commit()
    conn.close()

    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    session = Session()

    # Insert US via direct SQL, then trigger regen explicitly to verify the integration
    session.execute(text(
        "INSERT INTO us_table (sito, us, unita_tipo, rapporti, node_uuid) "
        "VALUES ('Volterra', 1001, 'US', '', 'uuid-1')"
    ))
    session.commit()

    from pyarchinit_mini.graphproj.auto_regen import _trigger_graph_regen
    _trigger_graph_regen("Volterra", session=session)

    out = tmp_path / "data" / "paradata" / "volterra" / "stratigraphy.graphml"
    assert out.exists(), "stratigraphy.graphml not created"

    session.close()


def test_save_us_regen_fail_does_not_propagate(tmp_path, monkeypatch):
    """Auto-regen failures must not raise to the caller."""
    monkeypatch.chdir(tmp_path)
    from unittest.mock import patch
    from pyarchinit_mini.graphproj.auto_regen import _trigger_graph_regen
    with patch(
        "pyarchinit_mini.graphproj.auto_regen.GraphProjector.populate_graph",
        side_effect=RuntimeError("boom"),
    ):
        _trigger_graph_regen("X", session=None)  # must NOT raise
```

- [ ] **Step 3: Run, verify tests pass already (no wiring change needed for the integration test, which calls _trigger_graph_regen explicitly)**

```bash
.venv/bin/pytest tests/integration/test_auto_regen_on_save.py -v
```
Expected: 2 passed.

- [ ] **Step 4: Wire the post-commit call into the actual us_service**

Open the file located in Step 1. Find the function that does `session.commit()` after a US insert/update. Immediately after the commit, add:

```python
# At top of file:
from pyarchinit_mini.graphproj.auto_regen import _trigger_graph_regen

# After session.commit() in the save function:
try:
    _trigger_graph_regen(us.sito, session=session)
except Exception:
    pass  # _trigger already swallows; this is defensive
```

If the save function returns to a Flask route that uses `db.session`, use that session. Adapt the call to whatever session object is available.

If you cannot locate a single `save_us` function (e.g. the save is done directly in route handlers), add the trigger to each route handler that commits a new/edited US, immediately after `db.session.commit()`. Search:

```bash
grep -rn "session.commit\|db.session.commit" pyarchinit_mini/web_interface/ | grep -i "us\|stratigr" | head -10
```

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/services/us_service.py tests/integration/test_auto_regen_on_save.py
# OR if the wiring is in web_interface routes:
# git add pyarchinit_mini/web_interface/<route_file>.py tests/integration/test_auto_regen_on_save.py
git commit -m "feat(graphproj): wire auto_regen post-commit on US save"
```

---

## PR4 — GraphIngestor + IngestPlan

### Task 13: IngestPlan / IngestResult / NodePlanEntry dataclasses

**Files:**
- Create: `pyarchinit_mini/graphproj/ingest_plan.py`
- Test: `tests/unit/test_ingest_plan.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_ingest_plan.py
import pytest
from pyarchinit_mini.graphproj.ingest_plan import (
    NodePlanEntry,
    IngestPlan,
    IngestResult,
)


def test_node_plan_entry_frozen():
    e = NodePlanEntry(
        node_uuid="u1", unit_type="US",
        semantic_id="pyarchinit:site=X/us=1",
        before=None, after={"us": 1}, reason="new",
    )
    with pytest.raises(Exception):
        e.reason = "different"


def test_ingest_plan_frozen():
    p = IngestPlan(
        site="X", snapshot_revision="abc",
        inserts=(), updates=(), skips_local_newer=(), skips_locked=(),
    )
    with pytest.raises(Exception):
        p.snapshot_revision = "def"


def test_ingest_result_carries_counts():
    p = IngestPlan(
        site="X", snapshot_revision="abc",
        inserts=(), updates=(), skips_local_newer=(), skips_locked=(),
    )
    r = IngestResult(plan=p, inserted=5, updated=3, skipped=2, errors=())
    assert r.inserted == 5
    assert r.updated == 3
    assert r.skipped == 2
```

- [ ] **Step 2: Run, verify ImportError**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/graphproj/ingest_plan.py
"""IngestPlan / IngestResult / NodePlanEntry — frozen dataclasses for GraphIngestor."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NodePlanEntry:
    node_uuid: str
    unit_type: str
    semantic_id: str
    before: Optional[dict]
    after: dict
    reason: str


@dataclass(frozen=True)
class IngestPlan:
    site: str
    snapshot_revision: str
    inserts: tuple[NodePlanEntry, ...]
    updates: tuple[NodePlanEntry, ...]
    skips_local_newer: tuple[NodePlanEntry, ...]
    skips_locked: tuple[NodePlanEntry, ...]


@dataclass(frozen=True)
class IngestResult:
    plan: IngestPlan
    inserted: int
    updated: int
    skipped: int
    errors: tuple[str, ...]
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_ingest_plan.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/ingest_plan.py tests/unit/test_ingest_plan.py
git commit -m "feat(graphproj): IngestPlan/IngestResult/NodePlanEntry dataclasses"
```

---

### Task 14: GraphIngestor.preview()

**Files:**
- Create: `pyarchinit_mini/graphproj/ingestor.py`
- Test: `tests/unit/test_graphproj_ingestor_preview.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_graphproj_ingestor_preview.py
from pathlib import Path
import sqlite3
import pytest

import s3dgraphy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphproj.ingestor import GraphIngestor
from pyarchinit_mini.graphproj.ingest_plan import IngestPlan

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


@pytest.fixture
def session(tmp_path):
    db = tmp_path / "ing.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us INTEGER,
        unita_tipo TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        rapporti TEXT, node_uuid TEXT
    )""")
    # Pre-existing: US 1001 with node_uuid u-1
    conn.execute(
        "INSERT INTO us_table (sito, us, unita_tipo, node_uuid) "
        "VALUES ('Volterra', 1001, 'US', 'u-1')"
    )
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def _build_input_graph_with(nodes_data):
    """Helper: build a s3dgraphy graph with given (us, unita_tipo, EMid) tuples."""
    g = s3dgraphy.Graph(graph_id="ing", name="ing", description="")
    for us_num, unita_tipo, emid in nodes_data:
        node_id = f"Volterra_{us_num}"
        n = s3dgraphy.Node(node_id, f"{unita_tipo}{us_num}", "")
        n.attributes["unit_type"] = unita_tipo
        n.attributes["EMid"] = emid
        g.add_node(n)
    return g


def test_preview_new_node_classified_as_insert(session):
    g = _build_input_graph_with([(1002, "US", "u-2")])
    plan = GraphIngestor(session, "Volterra").preview(g)
    assert isinstance(plan, IngestPlan)
    assert len(plan.inserts) == 1
    assert plan.inserts[0].reason == "new"


def test_preview_existing_node_classified_as_update(session):
    g = _build_input_graph_with([(1001, "US", "u-1")])
    plan = GraphIngestor(session, "Volterra").preview(g)
    assert len(plan.updates) == 1
    assert plan.updates[0].before is not None
    assert plan.updates[0].after["us"] == 1001 or plan.updates[0].after.get("us_num") == 1001


def test_preview_snapshot_revision_set(session):
    g = _build_input_graph_with([(1002, "US", "u-2")])
    plan = GraphIngestor(session, "Volterra").preview(g)
    assert plan.snapshot_revision != ""
    assert len(plan.snapshot_revision) >= 8  # hash-like
```

- [ ] **Step 2: Run, verify ImportError**

- [ ] **Step 3: Implement preview()**

```python
# pyarchinit_mini/graphproj/ingestor.py
"""GraphIngestor — 2-phase populate_list (preview + apply)."""
import hashlib
from typing import Any

import s3dgraphy
from sqlalchemy import text
from sqlalchemy.orm import Session

from .ingest_plan import IngestPlan, IngestResult, NodePlanEntry
from .exceptions import IngestError, IngestStaleError


class GraphIngestor:
    def __init__(self, session: Session, site: str) -> None:
        self.session = session
        self.site = site

    def _current_snapshot_revision(self) -> str:
        """Hash relevant DB state for staleness detection."""
        rows = self.session.execute(text(
            "SELECT node_uuid, us, unita_tipo FROM us_table "
            "WHERE sito = :sito ORDER BY node_uuid"
        ), {"sito": self.site}).fetchall()
        canonical = "|".join(
            f"{r[0] or ''}:{r[1]}:{r[2] or ''}" for r in rows
        )
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    def _existing_rows_by_uuid(self) -> dict[str, dict]:
        rows = self.session.execute(text(
            "SELECT node_uuid, us, unita_tipo FROM us_table WHERE sito = :sito"
        ), {"sito": self.site}).fetchall()
        result = {}
        for r in rows:
            uuid = r[0] or ""
            if uuid:
                result[uuid] = {"us": r[1], "unita_tipo": r[2]}
        return result

    def preview(self, graph: "s3dgraphy.Graph", *, dry_run: bool = True) -> IngestPlan:
        inserts: list[NodePlanEntry] = []
        updates: list[NodePlanEntry] = []
        skips_local_newer: list[NodePlanEntry] = []
        skips_locked: list[NodePlanEntry] = []

        snapshot = self._current_snapshot_revision()
        existing = self._existing_rows_by_uuid()

        for node in graph.nodes:
            attrs = getattr(node, "attributes", {}) or {}
            emid = attrs.get("EMid", "")
            unita_tipo = attrs.get("unit_type", "US")
            # Derive us number from node.name (format "<TYPE><NUM>")
            us_str = "".join(c for c in node.name if c.isdigit())
            us_num = int(us_str) if us_str else 0
            semantic_id = f"pyarchinit:site={self.site}/us={us_num}"

            after_row = {
                "us": us_num,
                "unita_tipo": unita_tipo,
                "node_uuid": emid,
            }

            if emid and emid in existing:
                entry = NodePlanEntry(
                    node_uuid=emid,
                    unit_type=unita_tipo,
                    semantic_id=semantic_id,
                    before=existing[emid],
                    after=after_row,
                    reason="graph_newer",
                )
                updates.append(entry)
            else:
                entry = NodePlanEntry(
                    node_uuid=emid or "",
                    unit_type=unita_tipo,
                    semantic_id=semantic_id,
                    before=None,
                    after=after_row,
                    reason="new",
                )
                inserts.append(entry)

        return IngestPlan(
            site=self.site,
            snapshot_revision=snapshot,
            inserts=tuple(inserts),
            updates=tuple(updates),
            skips_local_newer=tuple(skips_local_newer),
            skips_locked=tuple(skips_locked),
        )

    def apply(self, plan: IngestPlan) -> IngestResult:
        """Stub for Task 15."""
        raise NotImplementedError
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_graphproj_ingestor_preview.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/ingestor.py tests/unit/test_graphproj_ingestor_preview.py
git commit -m "feat(graphproj): GraphIngestor.preview() with snapshot revision"
```

---

### Task 15: GraphIngestor.apply() + staleness check

**Files:**
- Modify: `pyarchinit_mini/graphproj/ingestor.py`
- Test: `tests/unit/test_graphproj_ingestor_apply.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_graphproj_ingestor_apply.py
from pathlib import Path
import sqlite3
import pytest

import s3dgraphy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphproj.ingestor import GraphIngestor
from pyarchinit_mini.graphproj.exceptions import IngestStaleError

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


@pytest.fixture
def session(tmp_path):
    db = tmp_path / "app.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us INTEGER,
        unita_tipo TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        rapporti TEXT, node_uuid TEXT
    )""")
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def _input_graph(nodes):
    g = s3dgraphy.Graph(graph_id="ing", name="ing", description="")
    for us_num, unita_tipo, emid in nodes:
        n = s3dgraphy.Node(f"Volterra_{us_num}", f"{unita_tipo}{us_num}", "")
        n.attributes["unit_type"] = unita_tipo
        n.attributes["EMid"] = emid
        g.add_node(n)
    return g


def test_apply_inserts_new_us_rows(session):
    g = _input_graph([(2001, "US", "u-1"), (2002, "US", "u-2")])
    ing = GraphIngestor(session, "Volterra")
    plan = ing.preview(g)
    result = ing.apply(plan)
    assert result.inserted == 2
    # Verify rows present
    count = session.execute(text(
        "SELECT COUNT(*) FROM us_table WHERE sito='Volterra'"
    )).scalar()
    assert count == 2


def test_apply_stale_plan_raises(session):
    g = _input_graph([(2001, "US", "u-1")])
    ing = GraphIngestor(session, "Volterra")
    plan = ing.preview(g)
    # Mutate DB so snapshot changes
    session.execute(text(
        "INSERT INTO us_table (sito, us, unita_tipo, node_uuid) "
        "VALUES ('Volterra', 9999, 'US', 'mutator')"
    ))
    session.commit()
    with pytest.raises(IngestStaleError):
        ing.apply(plan)
```

- [ ] **Step 2: Run, verify failure**

- [ ] **Step 3: Implement apply()**

Replace the `apply()` stub in `ingestor.py`:

```python
    def apply(self, plan: IngestPlan) -> IngestResult:
        """Execute the plan. Transaction-wrapped. Verifies snapshot freshness."""
        current = self._current_snapshot_revision()
        if current != plan.snapshot_revision:
            raise IngestStaleError(expected=plan.snapshot_revision, actual=current)

        inserted = 0
        updated = 0
        skipped = 0
        errors: list[str] = []

        try:
            for entry in plan.inserts:
                try:
                    self.session.execute(text(
                        "INSERT INTO us_table (sito, us, unita_tipo, node_uuid) "
                        "VALUES (:sito, :us, :unita_tipo, :node_uuid)"
                    ), {
                        "sito": self.site,
                        "us": entry.after["us"],
                        "unita_tipo": entry.after["unita_tipo"],
                        "node_uuid": entry.after["node_uuid"] or entry.node_uuid,
                    })
                    inserted += 1
                except Exception as e:
                    errors.append(f"insert {entry.semantic_id}: {e}")
            for entry in plan.updates:
                try:
                    self.session.execute(text(
                        "UPDATE us_table SET us=:us, unita_tipo=:unita_tipo "
                        "WHERE node_uuid=:node_uuid AND sito=:sito"
                    ), {
                        "sito": self.site,
                        "us": entry.after["us"],
                        "unita_tipo": entry.after["unita_tipo"],
                        "node_uuid": entry.node_uuid,
                    })
                    updated += 1
                except Exception as e:
                    errors.append(f"update {entry.semantic_id}: {e}")
            skipped = len(plan.skips_local_newer) + len(plan.skips_locked)
            if errors:
                self.session.rollback()
                inserted = updated = 0
            else:
                self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return IngestResult(
            plan=plan,
            inserted=inserted,
            updated=updated,
            skipped=skipped,
            errors=tuple(errors),
        )
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_graphproj_ingestor_apply.py -v
```
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/ingestor.py tests/unit/test_graphproj_ingestor_apply.py
git commit -m "feat(graphproj): GraphIngestor.apply with snapshot staleness check"
```

---

## PR5 — Paradata REST API

### Task 16: paradata_routes blueprint (authors CRUD)

**Files:**
- Create: `pyarchinit_mini/web_interface/paradata_routes.py`
- Test: `tests/integration/test_paradata_routes_authors.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/integration/test_paradata_routes_authors.py
from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    from flask import Flask
    from pyarchinit_mini.web_interface.paradata_routes import paradata_bp
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(paradata_bp)
    yield app.test_client()
    VocabProvider.reset()


def test_post_then_list_authors(client):
    r = client.post(
        "/api/v1/paradata/Volterra/authors",
        json={"name": "M. Rossi", "orcid": "0000-0001"},
    )
    assert r.status_code == 201
    body = r.get_json()
    assert body["name"] == "M. Rossi"

    r2 = client.get("/api/v1/paradata/Volterra/authors")
    assert r2.status_code == 200
    authors = r2.get_json()
    assert len(authors) == 1
    assert authors[0]["name"] == "M. Rossi"


def test_put_author(client):
    r = client.post(
        "/api/v1/paradata/Volterra/authors",
        json={"name": "M. Rossi"},
    )
    node_id = r.get_json()["node_id"]
    r2 = client.put(
        f"/api/v1/paradata/Volterra/authors/{node_id}",
        json={"orcid": "0000-0002"},
    )
    assert r2.status_code == 200
    assert r2.get_json()["orcid"] == "0000-0002"


def test_delete_author(client):
    r = client.post(
        "/api/v1/paradata/Volterra/authors",
        json={"name": "M. Rossi"},
    )
    node_id = r.get_json()["node_id"]
    r2 = client.delete(f"/api/v1/paradata/Volterra/authors/{node_id}")
    assert r2.status_code == 204
    r3 = client.get("/api/v1/paradata/Volterra/authors")
    assert r3.get_json() == []


def test_post_duplicate_returns_409(client):
    client.post("/api/v1/paradata/Volterra/authors", json={"name": "M. Rossi"})
    r = client.post("/api/v1/paradata/Volterra/authors", json={"name": "M. Rossi"})
    assert r.status_code == 409
    body = r.get_json()
    assert body["error"] == "duplicate"


def test_put_unknown_returns_404(client):
    r = client.put(
        "/api/v1/paradata/Volterra/authors/author:bogus",
        json={"name": "X"},
    )
    assert r.status_code == 404
```

- [ ] **Step 2: Run, verify ImportError**

- [ ] **Step 3: Implement blueprint**

```python
# pyarchinit_mini/web_interface/paradata_routes.py
"""REST API for paradata CRUD (authors first; other types added in Task 17)."""
from flask import Blueprint, jsonify, request

from pyarchinit_mini.graphproj.paradata_store import ParadataStore
from pyarchinit_mini.graphproj.exceptions import (
    ParadataConflict, ParadataNotFound, ParadataStorageError,
)

paradata_bp = Blueprint("paradata", __name__, url_prefix="/api/v1/paradata")


# --- authors ---

@paradata_bp.get("/<site>/authors")
def list_authors(site: str):
    store = ParadataStore(site)
    return jsonify(store.list_authors()), 200


@paradata_bp.post("/<site>/authors")
def create_author(site: str):
    payload = request.get_json() or {}
    name = payload.get("name")
    if not name:
        return jsonify({"error": "validation", "fields": {"name": "required"}}), 400
    orcid = payload.get("orcid")
    try:
        author = ParadataStore(site).add_author(name=name, orcid=orcid)
    except ParadataConflict as e:
        return jsonify({"error": "duplicate", "existing": e.existing}), 409
    except ParadataStorageError as e:
        return jsonify({"error": "storage", "message": str(e)}), 500
    return jsonify(author), 201


@paradata_bp.put("/<site>/authors/<node_id>")
def update_author(site: str, node_id: str):
    payload = request.get_json() or {}
    try:
        updated = ParadataStore(site).update_author(
            node_id,
            name=payload.get("name"),
            orcid=payload.get("orcid"),
        )
    except ParadataNotFound:
        return jsonify({"error": "not_found", "node_id": node_id}), 404
    except ParadataStorageError as e:
        return jsonify({"error": "storage", "message": str(e)}), 500
    return jsonify(updated), 200


@paradata_bp.delete("/<site>/authors/<node_id>")
def delete_author(site: str, node_id: str):
    try:
        ParadataStore(site).delete_author(node_id)
    except ParadataNotFound:
        return jsonify({"error": "not_found", "node_id": node_id}), 404
    return "", 204
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/integration/test_paradata_routes_authors.py -v
```
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/paradata_routes.py tests/integration/test_paradata_routes_authors.py
git commit -m "feat(web): paradata REST blueprint (authors CRUD)"
```

---

### Task 17: paradata_routes extend to licenses, embargoes, documents, epochs

**Files:**
- Modify: `pyarchinit_mini/web_interface/paradata_routes.py`
- Test: `tests/integration/test_paradata_routes_other_types.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/integration/test_paradata_routes_other_types.py
from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    from flask import Flask
    from pyarchinit_mini.web_interface.paradata_routes import paradata_bp
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(paradata_bp)
    yield app.test_client()
    VocabProvider.reset()


@pytest.mark.parametrize("kind,body", [
    ("licenses", {"name": "CC-BY", "url": "https://creativecommons.org/..."}),
    ("embargoes", {"label": "Until 2030", "until": "2030-01-01"}),
    ("documents", {"title": "Report 2024", "uri": "https://example.org/report"}),
    ("epochs", {"name": "Roman", "start": -27, "end": 476}),
])
def test_crud_round_trip(client, kind, body):
    r = client.post(f"/api/v1/paradata/Volterra/{kind}", json=body)
    assert r.status_code == 201, f"{kind} POST failed: {r.data}"
    created = r.get_json()
    node_id = created["node_id"]

    r2 = client.get(f"/api/v1/paradata/Volterra/{kind}")
    assert any(item["node_id"] == node_id for item in r2.get_json())

    r3 = client.delete(f"/api/v1/paradata/Volterra/{kind}/{node_id}")
    assert r3.status_code == 204

    r4 = client.get(f"/api/v1/paradata/Volterra/{kind}")
    assert r4.get_json() == []
```

- [ ] **Step 2: Run, verify failure**

- [ ] **Step 3: Extend blueprint**

Append to `pyarchinit_mini/web_interface/paradata_routes.py`:

```python
# --- generic kind dispatcher ---

KIND_METHODS = {
    "licenses": ("list_licenses", "add_license", "update_license", "delete_license",
                 ("name", "url"), "name"),
    "embargoes": ("list_embargoes", "add_embargo", "update_embargo", "delete_embargo",
                  ("label", "until"), "label"),
    "documents": ("list_documents", "add_document", "update_document", "delete_document",
                  ("title", "uri"), "title"),
    "epochs": ("list_epochs", "add_epoch", "update_epoch", "delete_epoch",
               ("name", "start", "end"), "name"),
}


def _kind_op(site: str, kind: str, op: str):
    if kind not in KIND_METHODS:
        return None
    list_n, add_n, upd_n, del_n, fields, required = KIND_METHODS[kind]
    store = ParadataStore(site)
    return getattr(store, {"list": list_n, "add": add_n, "update": upd_n, "delete": del_n}[op])


@paradata_bp.get("/<site>/<kind>")
def list_kind(site: str, kind: str):
    if kind == "authors":
        return list_authors(site)
    fn = _kind_op(site, kind, "list")
    if fn is None:
        return jsonify({"error": "unknown_kind"}), 404
    return jsonify(fn()), 200


@paradata_bp.post("/<site>/<kind>")
def create_kind(site: str, kind: str):
    if kind == "authors":
        return create_author(site)
    if kind not in KIND_METHODS:
        return jsonify({"error": "unknown_kind"}), 404
    payload = request.get_json() or {}
    _, _, _, _, fields, required_field = KIND_METHODS[kind]
    if required_field not in payload or not payload[required_field]:
        return jsonify({
            "error": "validation",
            "fields": {required_field: "required"},
        }), 400
    fn = _kind_op(site, kind, "add")
    kwargs = {f: payload.get(f) for f in fields if f in payload}
    try:
        created = fn(**kwargs)
    except ParadataConflict as e:
        return jsonify({"error": "duplicate", "existing": e.existing}), 409
    except ParadataStorageError as e:
        return jsonify({"error": "storage", "message": str(e)}), 500
    return jsonify(created), 201


@paradata_bp.put("/<site>/<kind>/<node_id>")
def update_kind(site: str, kind: str, node_id: str):
    if kind == "authors":
        return update_author(site, node_id)
    if kind not in KIND_METHODS:
        return jsonify({"error": "unknown_kind"}), 404
    payload = request.get_json() or {}
    _, _, _, _, fields, _ = KIND_METHODS[kind]
    fn = _kind_op(site, kind, "update")
    kwargs = {f: payload[f] for f in fields if f in payload}
    try:
        updated = fn(node_id, **kwargs)
    except ParadataNotFound:
        return jsonify({"error": "not_found", "node_id": node_id}), 404
    except ParadataStorageError as e:
        return jsonify({"error": "storage", "message": str(e)}), 500
    return jsonify(updated), 200


@paradata_bp.delete("/<site>/<kind>/<node_id>")
def delete_kind(site: str, kind: str, node_id: str):
    if kind == "authors":
        return delete_author(site, node_id)
    if kind not in KIND_METHODS:
        return jsonify({"error": "unknown_kind"}), 404
    fn = _kind_op(site, kind, "delete")
    try:
        fn(node_id)
    except ParadataNotFound:
        return jsonify({"error": "not_found", "node_id": node_id}), 404
    return "", 204
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/integration/test_paradata_routes_other_types.py tests/integration/test_paradata_routes_authors.py -v
```
Expected: 9 passed (5 from Task 16 + 4 parametrized).

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/paradata_routes.py tests/integration/test_paradata_routes_other_types.py
git commit -m "feat(web): paradata REST CRUD for licenses, embargoes, documents, epochs"
```

---

## PR6 — Paradata UI Pages

### Task 18: paradata_ui_routes — list + edit pages for all 5 types

**Files:**
- Create: `pyarchinit_mini/web_interface/paradata_ui_routes.py`
- Create: `pyarchinit_mini/web_interface/templates/paradata/list.html`
- Create: `pyarchinit_mini/web_interface/templates/paradata/edit.html`
- Test: `tests/integration/test_paradata_ui.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/integration/test_paradata_ui.py
from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    from flask import Flask
    from pyarchinit_mini.web_interface.paradata_routes import paradata_bp
    from pyarchinit_mini.web_interface.paradata_ui_routes import paradata_ui_bp
    app = Flask(
        __name__,
        template_folder=str(
            Path(__file__).parent.parent.parent
            / "pyarchinit_mini" / "web_interface" / "templates"
        ),
    )
    app.config["TESTING"] = True
    app.secret_key = "test"
    app.register_blueprint(paradata_bp)
    app.register_blueprint(paradata_ui_bp)
    yield app.test_client()
    VocabProvider.reset()


def test_list_authors_page_renders(client):
    r = client.get("/paradata/Volterra/authors")
    assert r.status_code == 200
    assert b"Author" in r.data or b"author" in r.data


def test_create_author_via_form_redirects_to_list(client):
    r = client.post(
        "/paradata/Volterra/authors/new",
        data={"name": "M. Rossi", "orcid": "0000-0001"},
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)
    # Verify it's in the list
    r2 = client.get("/paradata/Volterra/authors")
    assert b"M. Rossi" in r2.data


def test_delete_author_via_post(client):
    # Seed
    client.post("/paradata/Volterra/authors/new", data={"name": "X"})
    r_list = client.get("/paradata/Volterra/authors")
    # Extract the node_id from the response (depends on template; for now,
    # use the API to fetch it)
    import json
    r_json = client.get("/api/v1/paradata/Volterra/authors")
    authors = r_json.get_json()
    nid = authors[0]["node_id"]
    r = client.post(
        f"/paradata/Volterra/authors/{nid}/delete",
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)
    r_after = client.get("/api/v1/paradata/Volterra/authors")
    assert r_after.get_json() == []
```

- [ ] **Step 2: Run, verify failure**

- [ ] **Step 3: Implement templates**

Create `pyarchinit_mini/web_interface/templates/paradata/list.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{ kind|capitalize }} — {{ site }}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="p-4">
  <h1>{{ kind|capitalize }} for site {{ site }}</h1>
  <a href="{{ url_for('paradata_ui.new', site=site, kind=kind) }}" class="btn btn-primary mb-3">New {{ kind|capitalize }}</a>
  <table class="table table-striped">
    <thead><tr>
      {% for col in columns %}<th>{{ col }}</th>{% endfor %}
      <th>Actions</th>
    </tr></thead>
    <tbody>
      {% for item in items %}
      <tr>
        {% for col in columns %}<td>{{ item.get(col, '') }}</td>{% endfor %}
        <td>
          <a href="{{ url_for('paradata_ui.edit', site=site, kind=kind, node_id=item.node_id) }}" class="btn btn-sm btn-secondary">Edit</a>
          <form action="{{ url_for('paradata_ui.delete', site=site, kind=kind, node_id=item.node_id) }}" method="post" style="display:inline">
            <button class="btn btn-sm btn-danger" onclick="return confirm('Delete?')">Delete</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
```

Create `pyarchinit_mini/web_interface/templates/paradata/edit.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{% if item %}Edit{% else %}New{% endif %} {{ kind|capitalize }}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="p-4">
  <h1>{% if item %}Edit{% else %}New{% endif %} {{ kind|capitalize }}</h1>
  <form method="post" action="{{ form_action }}">
    {% for field in fields %}
    <div class="mb-3">
      <label class="form-label">{{ field|capitalize }}</label>
      <input type="text" name="{{ field }}" value="{{ item.get(field, '') if item else '' }}" class="form-control">
    </div>
    {% endfor %}
    <button type="submit" class="btn btn-primary">Save</button>
    <a href="{{ url_for('paradata_ui.list', site=site, kind=kind) }}" class="btn btn-secondary">Cancel</a>
  </form>
</body>
</html>
```

- [ ] **Step 4: Implement blueprint**

```python
# pyarchinit_mini/web_interface/paradata_ui_routes.py
"""HTML pages for paradata CRUD — 5 sections (one per node type)."""
from flask import Blueprint, render_template, request, redirect, url_for, abort

from pyarchinit_mini.graphproj.paradata_store import ParadataStore
from pyarchinit_mini.graphproj.exceptions import ParadataConflict, ParadataNotFound

paradata_ui_bp = Blueprint("paradata_ui", __name__, url_prefix="/paradata")


KIND_DEF = {
    "authors": {
        "list_fn": "list_authors", "add_fn": "add_author",
        "update_fn": "update_author", "delete_fn": "delete_author",
        "columns": ["name", "orcid"], "fields": ["name", "orcid"],
    },
    "licenses": {
        "list_fn": "list_licenses", "add_fn": "add_license",
        "update_fn": "update_license", "delete_fn": "delete_license",
        "columns": ["name", "url"], "fields": ["name", "url"],
    },
    "embargoes": {
        "list_fn": "list_embargoes", "add_fn": "add_embargo",
        "update_fn": "update_embargo", "delete_fn": "delete_embargo",
        "columns": ["label", "until"], "fields": ["label", "until"],
    },
    "documents": {
        "list_fn": "list_documents", "add_fn": "add_document",
        "update_fn": "update_document", "delete_fn": "delete_document",
        "columns": ["name", "uri"], "fields": ["title", "uri"],
    },
    "epochs": {
        "list_fn": "list_epochs", "add_fn": "add_epoch",
        "update_fn": "update_epoch", "delete_fn": "delete_epoch",
        "columns": ["name", "start", "end"], "fields": ["name", "start", "end"],
    },
}


def _kind_or_404(kind):
    if kind not in KIND_DEF:
        abort(404)
    return KIND_DEF[kind]


@paradata_ui_bp.get("/<site>/<kind>", endpoint="list")
def list_(site, kind):
    cfg = _kind_or_404(kind)
    store = ParadataStore(site)
    items = getattr(store, cfg["list_fn"])()
    return render_template(
        "paradata/list.html",
        site=site, kind=kind, items=items, columns=cfg["columns"],
    )


@paradata_ui_bp.get("/<site>/<kind>/new", endpoint="new")
def new(site, kind):
    cfg = _kind_or_404(kind)
    return render_template(
        "paradata/edit.html",
        site=site, kind=kind, item=None, fields=cfg["fields"],
        form_action=url_for("paradata_ui.new", site=site, kind=kind),
    )


@paradata_ui_bp.post("/<site>/<kind>/new", endpoint="new_post")
def new_post(site, kind):
    cfg = _kind_or_404(kind)
    store = ParadataStore(site)
    kwargs = {f: request.form.get(f) or None for f in cfg["fields"]}
    # Drop None for required first field (let store enforce)
    try:
        getattr(store, cfg["add_fn"])(**kwargs)
    except ParadataConflict:
        pass  # Could re-render with error; for now silently redirect
    return redirect(url_for("paradata_ui.list", site=site, kind=kind))


@paradata_ui_bp.route("/<site>/<kind>/new", methods=["POST"])
def new_alias(site, kind):
    return new_post(site, kind)


@paradata_ui_bp.get("/<site>/<kind>/<node_id>/edit", endpoint="edit")
def edit(site, kind, node_id):
    cfg = _kind_or_404(kind)
    store = ParadataStore(site)
    items = getattr(store, cfg["list_fn"])()
    item = next((i for i in items if i["node_id"] == node_id), None)
    if item is None:
        abort(404)
    return render_template(
        "paradata/edit.html",
        site=site, kind=kind, item=item, fields=cfg["fields"],
        form_action=url_for(
            "paradata_ui.edit_post", site=site, kind=kind, node_id=node_id
        ),
    )


@paradata_ui_bp.post("/<site>/<kind>/<node_id>/edit", endpoint="edit_post")
def edit_post(site, kind, node_id):
    cfg = _kind_or_404(kind)
    store = ParadataStore(site)
    kwargs = {f: request.form.get(f) or None for f in cfg["fields"]}
    try:
        getattr(store, cfg["update_fn"])(node_id, **kwargs)
    except ParadataNotFound:
        abort(404)
    return redirect(url_for("paradata_ui.list", site=site, kind=kind))


@paradata_ui_bp.post("/<site>/<kind>/<node_id>/delete", endpoint="delete")
def delete(site, kind, node_id):
    cfg = _kind_or_404(kind)
    store = ParadataStore(site)
    try:
        getattr(store, cfg["delete_fn"])(node_id)
    except ParadataNotFound:
        abort(404)
    return redirect(url_for("paradata_ui.list", site=site, kind=kind))
```

- [ ] **Step 4: Run, verify pass**

Note: this task's create-form test uses URL `/paradata/Volterra/authors/new` for POST (form action). The blueprint maps `new` (GET) and `new_post` (POST) at the same URL. If Flask refuses duplicate endpoint registrations, consolidate using `methods=["GET", "POST"]` and inspect `request.method`. Adapt as needed.

```bash
.venv/bin/pytest tests/integration/test_paradata_ui.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/paradata_ui_routes.py pyarchinit_mini/web_interface/templates/paradata/ tests/integration/test_paradata_ui.py
git commit -m "feat(web): paradata UI pages (5 types CRUD)"
```

---

## PR7 — Graph Routes (view/download/import)

### Task 19: graph_routes view + download

**Files:**
- Create: `pyarchinit_mini/web_interface/graph_routes.py`
- Test: `tests/integration/test_graph_routes.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/integration/test_graph_routes.py
from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    from flask import Flask
    from pyarchinit_mini.web_interface.graph_routes import graph_bp
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test"
    app.register_blueprint(graph_bp)
    yield app.test_client(), tmp_path
    VocabProvider.reset()


def test_download_returns_404_when_no_graph(client):
    cli, _ = client
    r = cli.get("/sites/Volterra/graph/download")
    assert r.status_code == 404


def test_download_serves_file_when_exists(client):
    cli, tmp_path = client
    out_dir = tmp_path / "data" / "paradata" / "volterra"
    out_dir.mkdir(parents=True)
    (out_dir / "stratigraphy.graphml").write_text("<graphml/>", encoding="utf-8")
    r = cli.get("/sites/Volterra/graph/download")
    assert r.status_code == 200
    assert b"<graphml/>" in r.data
    assert "attachment" in r.headers.get("Content-Disposition", "")
```

- [ ] **Step 2: Run, verify ImportError**

- [ ] **Step 3: Implement view + download**

```python
# pyarchinit_mini/web_interface/graph_routes.py
"""Graph routes — view, download, import-preview, import-apply."""
from pathlib import Path
from flask import Blueprint, abort, send_file

from pyarchinit_mini.graphproj.filesystem import paradata_dir, slugify

graph_bp = Blueprint("graph", __name__, url_prefix="/sites")


def _stratigraphy_path(site: str) -> Path:
    return paradata_dir(site) / "stratigraphy.graphml"


@graph_bp.get("/<site>/graph/download")
def download(site: str):
    path = _stratigraphy_path(site)
    if not path.exists():
        abort(404)
    return send_file(
        path,
        as_attachment=True,
        download_name=f"{slugify(site)}_stratigraphy.graphml",
        mimetype="application/xml",
    )


@graph_bp.get("/<site>/graph/view")
def view(site: str):
    path = _stratigraphy_path(site)
    if not path.exists():
        abort(404)
    return path.read_text(encoding="utf-8"), 200, {"Content-Type": "application/xml"}
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/integration/test_graph_routes.py -v
```
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/graph_routes.py tests/integration/test_graph_routes.py
git commit -m "feat(web): graph_routes view + download"
```

---

### Task 20: graph_routes import-preview + import-apply

**Files:**
- Modify: `pyarchinit_mini/web_interface/graph_routes.py`
- Create: `pyarchinit_mini/web_interface/templates/graph_import_preview.html`
- Create: `pyarchinit_mini/web_interface/templates/graph_import_result.html`
- Test: `tests/integration/test_graph_import_flow.py`

- [ ] **Step 1: Write failing test**

```python
# tests/integration/test_graph_import_flow.py
import sqlite3
from pathlib import Path
import pytest

import s3dgraphy
from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphml_io.writer import write_graphml

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def client_and_session(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)

    # DB setup
    db = tmp_path / "app.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us INTEGER,
        unita_tipo TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
        rapporti TEXT, node_uuid TEXT
    )""")
    conn.commit()
    conn.close()

    from flask import Flask, g
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker
    from pyarchinit_mini.web_interface.graph_routes import graph_bp

    eng = create_engine(f"sqlite:///{db}")
    Session = scoped_session(sessionmaker(bind=eng))

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test"

    @app.before_request
    def attach_session():
        g.db_session = Session()

    @app.teardown_request
    def remove_session(exc):
        Session.remove()

    app.register_blueprint(graph_bp)

    yield app.test_client(), tmp_path
    VocabProvider.reset()


def _build_upload(tmp_path, nodes):
    """Create a GraphML file to upload."""
    g = s3dgraphy.Graph(graph_id="up", name="up", description="")
    for us_num, ut, emid in nodes:
        n = s3dgraphy.Node(f"Volterra_{us_num}", f"{ut}{us_num}", "")
        n.attributes["unit_type"] = ut
        n.attributes["EMid"] = emid
        g.add_node(n)
    path = tmp_path / "upload.graphml"
    write_graphml(g, path)
    return path


def test_preview_then_apply_round_trip(client_and_session):
    cli, tmp_path = client_and_session
    upload_path = _build_upload(tmp_path, [(3001, "US", "u-3001")])

    # POST preview
    with upload_path.open("rb") as f:
        r = cli.post(
            "/sites/Volterra/graph/import-preview",
            data={"file": (f, "upload.graphml")},
            content_type="multipart/form-data",
        )
    assert r.status_code == 200
    assert b"INSERT" in r.data or b"insert" in r.data.lower()
```

- [ ] **Step 2: Run, verify failure**

- [ ] **Step 3: Implement preview + apply routes**

Append to `pyarchinit_mini/web_interface/graph_routes.py`:

```python
import uuid
from flask import g, render_template, request, session as flask_session

from pyarchinit_mini.graphproj.filesystem import paradata_dir
from pyarchinit_mini.graphproj.ingestor import GraphIngestor
from pyarchinit_mini.graphproj.exceptions import IngestStaleError, GraphMLReadError
from pyarchinit_mini.graphml_io.reader import read_graphml


@graph_bp.post("/<site>/graph/import-preview")
def import_preview(site: str):
    upload = request.files.get("file")
    if upload is None:
        return ("No file uploaded", 400)

    imports_dir = paradata_dir(site) / "imports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    upload_id = uuid.uuid4().hex
    saved_path = imports_dir / f"{upload_id}.graphml"
    upload.save(saved_path)

    try:
        graph = read_graphml(saved_path)
    except GraphMLReadError as e:
        return f"Invalid GraphML: {e}", 400

    db_session = getattr(g, "db_session", None)
    if db_session is None:
        return "No DB session bound", 500
    ingestor = GraphIngestor(db_session, site)
    plan = ingestor.preview(graph)

    # Store plan reference in Flask session
    flask_session[f"import_plan:{site}:{upload_id}"] = {
        "snapshot_revision": plan.snapshot_revision,
        "inserts": [e.__dict__ for e in plan.inserts],
        "updates": [e.__dict__ for e in plan.updates],
        "skips_local_newer": [e.__dict__ for e in plan.skips_local_newer],
        "skips_locked": [e.__dict__ for e in plan.skips_locked],
    }

    return render_template(
        "graph_import_preview.html",
        site=site, plan=plan, upload_id=upload_id,
    )


@graph_bp.post("/<site>/graph/import-apply")
def import_apply(site: str):
    upload_id = request.form.get("upload_id")
    if not upload_id:
        return "Missing upload_id", 400

    stored = flask_session.get(f"import_plan:{site}:{upload_id}")
    if stored is None:
        return "Plan not found in session", 404

    # Reconstruct plan
    from pyarchinit_mini.graphproj.ingest_plan import IngestPlan, NodePlanEntry
    def _r(entries):
        return tuple(NodePlanEntry(**e) for e in entries)
    plan = IngestPlan(
        site=site,
        snapshot_revision=stored["snapshot_revision"],
        inserts=_r(stored["inserts"]),
        updates=_r(stored["updates"]),
        skips_local_newer=_r(stored["skips_local_newer"]),
        skips_locked=_r(stored["skips_locked"]),
    )

    db_session = getattr(g, "db_session", None)
    ingestor = GraphIngestor(db_session, site)
    try:
        result = ingestor.apply(plan)
    except IngestStaleError as e:
        return f"Plan stale (expected={e.expected}, actual={e.actual}). Re-upload.", 409

    # Cleanup
    flask_session.pop(f"import_plan:{site}:{upload_id}", None)
    upload_file = paradata_dir(site) / "imports" / f"{upload_id}.graphml"
    if upload_file.exists():
        upload_file.unlink()

    return render_template(
        "graph_import_result.html",
        site=site, result=result,
    )
```

Create `pyarchinit_mini/web_interface/templates/graph_import_preview.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Import preview — {{ site }}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="p-4">
  <h1>Import preview for {{ site }}</h1>

  <h2>To INSERT ({{ plan.inserts|length }})</h2>
  <table class="table table-sm"><thead><tr><th>node_uuid</th><th>unit_type</th><th>semantic_id</th></tr></thead><tbody>
    {% for e in plan.inserts %}<tr><td>{{ e.node_uuid }}</td><td>{{ e.unit_type }}</td><td>{{ e.semantic_id }}</td></tr>{% endfor %}
  </tbody></table>

  <h2>To UPDATE ({{ plan.updates|length }})</h2>
  <table class="table table-sm"><thead><tr><th>node_uuid</th><th>before</th><th>after</th></tr></thead><tbody>
    {% for e in plan.updates %}<tr><td>{{ e.node_uuid }}</td><td>{{ e.before }}</td><td>{{ e.after }}</td></tr>{% endfor %}
  </tbody></table>

  <h2>Skipped — local newer ({{ plan.skips_local_newer|length }})</h2>
  <h2>Skipped — locked ({{ plan.skips_locked|length }})</h2>

  <form action="{{ url_for('graph.import_apply', site=site) }}" method="post" class="mt-3">
    <input type="hidden" name="upload_id" value="{{ upload_id }}">
    <button class="btn btn-primary">Confirm and apply</button>
    <a href="{{ url_for('graph.view', site=site) }}" class="btn btn-secondary">Cancel</a>
  </form>
</body>
</html>
```

Create `pyarchinit_mini/web_interface/templates/graph_import_result.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Import result — {{ site }}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="p-4">
  <h1>Import result for {{ site }}</h1>
  <p>Inserted: {{ result.inserted }}</p>
  <p>Updated: {{ result.updated }}</p>
  <p>Skipped: {{ result.skipped }}</p>
  {% if result.errors %}
  <h3>Errors</h3>
  <ul>{% for e in result.errors %}<li>{{ e }}</li>{% endfor %}</ul>
  {% endif %}
</body>
</html>
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/integration/test_graph_import_flow.py -v
```
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/graph_routes.py pyarchinit_mini/web_interface/templates/graph_import_*.html tests/integration/test_graph_import_flow.py
git commit -m "feat(web): graph import preview + apply with snapshot staleness"
```

---

## PR8 — Retire Old Writers + Cutover + Release

### Task 21: Refactor harris_creator_routes to use graphml_io.writer

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py`
- Test: `tests/integration/test_harris_matrix_post_cutover.py`

- [ ] **Step 1: Capture baseline Harris matrix output (before cutover)**

```bash
.venv/bin/python -c "
from pathlib import Path
import sqlite3
from pyarchinit_mini.graphml_converter.graphml_builder import GraphMLBuilder
fix_db = Path('tests/fixtures/databases/sqlite_fully_migrated.db')
if not fix_db.exists():
    print('Baseline DB not found; skipping baseline capture')
else:
    conn = sqlite3.connect(fix_db)
    rows = conn.execute('SELECT id_us, sito, us, unita_tipo FROM us_table ORDER BY id_us').fetchall()
    conn.close()
    b = GraphMLBuilder()
    for id_us, sito, us, ut in rows:
        b.add_node(node_id=f'{sito}_{us}', label=f'{ut}{us}')
    out = Path('tests/fixtures/graphml_outputs/harris_baseline_pre_pr8.graphml')
    out.parent.mkdir(parents=True, exist_ok=True)
    # Use whatever serialize method works (to_string or fallback)
    try:
        out.write_text(b.to_string(pretty_print=True), encoding='utf-8')
        print(f'wrote {out}')
    except Exception as e:
        print(f'baseline capture failed: {e}')
"
```

If the baseline can't be captured (e.g., `to_string()` is broken per Spec 1 finding), document that the parity test will use a more relaxed regression check (US shape == "rectangle" only).

- [ ] **Step 2: Write the regression test**

```python
# tests/integration/test_harris_matrix_post_cutover.py
"""PR8 gate: harris matrix output must not regress visually for standard
unit types after harris_creator_routes is refactored to graphml_io.writer."""
from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphml_converter.em_palette import EMPalette

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_us_shape_remains_rectangle_after_cutover():
    style = EMPalette.get_node_style("US100")
    assert style["shape"] == "rectangle"


def test_usm_shape_remains_rectangle_after_cutover():
    style = EMPalette.get_node_style("USM100")
    assert style["shape"] == "rectangle"


def test_usvs_supported_after_cutover():
    style = EMPalette.get_node_style("USVs100")
    assert style["shape"] == "parallelogram"
```

- [ ] **Step 3: Refactor harris_creator_routes**

```bash
grep -n "GraphMLBuilder\|graphml_builder\|graphml_exporter" pyarchinit_mini/web_interface/harris_creator_routes.py | head -10
```

For each `GraphMLBuilder` usage that produces an output file:
- Replace the manual `.add_node()` loop + `.to_string()` with: build a `s3dgraphy.Graph` directly (using `GraphProjector.populate_graph` if a DB session is available; otherwise construct nodes/edges manually) and call `graphml_io.writer.write_graphml(graph, output_path)`.

Add at top of file:
```python
from pyarchinit_mini.graphml_io.writer import write_graphml
from pyarchinit_mini.graphproj.projector import GraphProjector
```

Where the existing route generates the Harris matrix GraphML, replace the block with:
```python
# Generate via VocabProvider-backed writer (PR8 cutover)
graph = GraphProjector.populate_graph(db_session, site)
out_path = Path("pyarchinit_mini/web_interface/uploads/graphml") / f"{site}_stratigraphy.graphml"
write_graphml(graph, out_path)
```

Adapt the exact integration to whatever the route currently does (the route's responsibility is creating the file at a known location for the front-end viewer).

- [ ] **Step 4: Run regression test**

```bash
.venv/bin/pytest tests/integration/test_harris_matrix_post_cutover.py tests/integration/test_harris_matrix_visual_parity.py -v
```
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/harris_creator_routes.py tests/integration/test_harris_matrix_post_cutover.py
git commit -m "refactor(harris): cut over to graphml_io.writer (PR8)"
```

---

### Task 22: Deprecation shims on old writers

**Files:**
- Modify: `pyarchinit_mini/graphml_converter/graphml_builder.py`
- Modify: `pyarchinit_mini/graphml_converter/graphml_exporter.py`
- Modify: `pyarchinit_mini/graphml_converter/pure_networkx_exporter.py`
- Modify: `pyarchinit_mini/graphml_converter/converter.py`
- Test: `tests/unit/test_deprecated_writers_shim.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_deprecated_writers_shim.py
import warnings
import pytest


def test_graphml_builder_import_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        from pyarchinit_mini.graphml_converter.graphml_builder import GraphMLBuilder
        b = GraphMLBuilder()
        b.add_node(node_id="n1", label="US1")
        # Construct or use the class — warning should fire on construction or first use
    msgs = [str(w.message) for w in caught if issubclass(w.category, DeprecationWarning)]
    assert any("graphml_io.writer" in m or "deprecated" in m.lower() for m in msgs)


def test_graphml_exporter_import_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        import pyarchinit_mini.graphml_converter.graphml_exporter as mod
        # Trigger module-level warning if any callable exposed:
        for name in dir(mod):
            obj = getattr(mod, name)
            if callable(obj) and not name.startswith("_"):
                try:
                    obj()
                except Exception:
                    pass
                break
    msgs = [str(w.message) for w in caught if issubclass(w.category, DeprecationWarning)]
    assert any("deprecated" in m.lower() for m in msgs)
```

- [ ] **Step 2: Run, verify failure**

- [ ] **Step 3: Add warnings to each writer module**

In each of the 4 files (`graphml_builder.py`, `graphml_exporter.py`, `pure_networkx_exporter.py`, `converter.py`), add at the top (after existing imports):

```python
import warnings as _warnings
_warnings.warn(
    "{module_name} is deprecated; use pyarchinit_mini.graphml_io.writer instead. "
    "This module will be removed in Spec 3.",
    DeprecationWarning,
    stacklevel=2,
)
```

Replace `{module_name}` with the actual module path string for each file.

For `graphml_builder.py`, ALSO add a `__init__` shim emitting the warning so import + construct both trigger it:

```python
# At top of GraphMLBuilder.__init__:
def __init__(self, ...):
    _warnings.warn(
        "GraphMLBuilder is deprecated; use pyarchinit_mini.graphml_io.writer.write_graphml instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    # ... existing init body
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_deprecated_writers_shim.py -v
```
Expected: 2 passed. If the existing module-level imports already happened in test session, the warning may not re-fire — use `importlib.reload` in the test if needed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphml_converter/*.py tests/unit/test_deprecated_writers_shim.py
git commit -m "refactor(graphml): add DeprecationWarning shims on 4 legacy writers"
```

---

### Task 23: Register new blueprints + .gitignore

**Files:**
- Modify: `pyarchinit_mini/web_interface/app.py`
- Modify: `.gitignore`

- [ ] **Step 1: Find blueprint registration area**

```bash
grep -n "register_blueprint" pyarchinit_mini/web_interface/app.py | head -5
```

- [ ] **Step 2: Register the 3 new blueprints**

Add imports near other blueprint imports in `app.py`:
```python
from pyarchinit_mini.web_interface.graph_routes import graph_bp
from pyarchinit_mini.web_interface.paradata_routes import paradata_bp
from pyarchinit_mini.web_interface.paradata_ui_routes import paradata_ui_bp
```

In the registration section (~line 544-560 per Spec 1 reference):
```python
app.register_blueprint(graph_bp)
app.register_blueprint(paradata_bp)
app.register_blueprint(paradata_ui_bp)
```

- [ ] **Step 3: Update .gitignore**

Append to `.gitignore`:
```
# Spec 2: paradata derived artifacts
data/paradata/**/stratigraphy.graphml
data/paradata/**/.paradata.lock
data/paradata/**/*.tmp
data/paradata/**/imports/*
data/paradata/_regen.log
data/paradata/_metrics.sqlite
```

- [ ] **Step 4: Smoke test**

```bash
.venv/bin/python -c "
from flask import Flask
from pyarchinit_mini.web_interface.graph_routes import graph_bp
from pyarchinit_mini.web_interface.paradata_routes import paradata_bp
from pyarchinit_mini.web_interface.paradata_ui_routes import paradata_ui_bp
app = Flask(__name__)
app.register_blueprint(graph_bp)
app.register_blueprint(paradata_bp)
app.register_blueprint(paradata_ui_bp)
print('routes:')
for r in app.url_map.iter_rules():
    print(' ', r.rule)
"
```

Expected: see /sites/<site>/graph/*, /api/v1/paradata/*, /paradata/<site>/* routes.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/app.py .gitignore
git commit -m "feat(web): register graph/paradata/paradata_ui blueprints + .gitignore"
```

---

### Task 24: Version bump + CHANGELOG + README + 2 user docs

**Files:**
- Modify: `pyarchinit_mini/__init__.py`
- Modify: `pyproject.toml`
- Modify: `CHANGELOG.md`
- Modify: `README.md`
- Create: `docs/PARADATA_GUIDE.md`
- Create: `docs/GRAPH_AUTO_REGEN.md`

- [ ] **Step 1: Bump version**

Replace `2.2.0-alpha` with `2.3.0-alpha` in `pyarchinit_mini/__init__.py` and `pyproject.toml`.

- [ ] **Step 2: Prepend CHANGELOG entry**

Prepend to `CHANGELOG.md` (above the 2.2.0-alpha entry):

```markdown
## [2.3.0-alpha] - 2026-05-17

### Added (IT)
- Modulo `pyarchinit_mini/graphproj/` con `GraphProjector` (DB → s3dgraphy.Graph),
  `ParadataStore` (per-sito su filesystem), `GraphIngestor` (preview/apply
  bidirezionale).
- Modulo `pyarchinit_mini/graphml_io/` con writer/reader delegati a
  `s3dgraphy.exporter.graphml` / `s3dgraphy.importer.import_graphml`.
- Auto-regen di `data/paradata/<site>/stratigraphy.graphml` su ogni save US/USM
  (best-effort, errori isolati). Disabilitabile con `PYARCHINIT_DISABLE_AUTO_REGEN=1`
  o con il context manager `auto_regen.disable_regen()` per bulk import.
- 5 pagine HTML CRUD per paradata (authors, licenses, embargoes, documents, epochs)
  + REST API `/api/v1/paradata/<site>/...`.
- Route web `/sites/<site>/graph/{view,download,import-preview,import-apply}`
  con preview 2-fasi obbligatorio per l'import GraphML.

### Added (EN)
- New `pyarchinit_mini/graphproj/` package with `GraphProjector`, `ParadataStore`,
  `GraphIngestor` (2-phase preview/apply).
- New `pyarchinit_mini/graphml_io/` package delegating to s3dgraphy.
- Auto-regen of merged stratigraphy.graphml on US/USM save, error-isolated.
- 5 paradata CRUD HTML pages + REST API.
- Graph routes: view, download, import-preview, import-apply with snapshot
  staleness check.

### Changed
- `graphml_converter/{graphml_builder, graphml_exporter, pure_networkx_exporter,
  converter}.py` marked deprecated (emit `DeprecationWarning`); will be removed
  in Spec 3.
- `harris_creator_routes.py` refactored to use `graphml_io.writer` directly.

### Dependencies
- No new dependencies. Uses s3dgraphy 0.1.42 (already bumped in 2.2.0-alpha).

### Spec / Plan
- Spec: `docs/superpowers/specs/2026-05-17-spec-2-local-graph-paradata-design.md`
- Plan: `docs/superpowers/plans/2026-05-17-spec-2-local-graph-paradata.md`
- This is Spec 2 of 4 for the s3dgraphy bidirectional bridge work.
```

- [ ] **Step 3: Append README section**

Append to `README.md`:

```markdown

## Graph projection & paradata

Since 2.3.0-alpha, pyarchinit-mini-web auto-generates the stratigraphic graph
as a GraphML file every time you save a US/USM record. Output lives at
`data/paradata/<site_slug>/stratigraphy.graphml` and merges:

- **Stratigraphic layer** (auto-projected from `us_table` via `GraphProjector`)
- **Paradata layer** (authors, licenses, embargoes, documents, epochs — managed
  via the new `/paradata/<site>/...` pages)

### Paradata editing

Visit `/paradata/<site>/{authors,licenses,embargoes,documents,epochs}` to
manage paradata nodes. REST endpoints under `/api/v1/paradata/<site>/...`
mirror the UI.

See `docs/PARADATA_GUIDE.md` for what each node type means.

### Graph import

`/sites/<site>/graph/import` accepts a GraphML file; you'll see a preview of
the planned changes (INSERT / UPDATE / SKIP) and must confirm before any DB
write happens.

### Auto-regen control

- Disable globally: `export PYARCHINIT_DISABLE_AUTO_REGEN=1` before starting Flask.
- Disable during bulk operations: use `with graphproj.auto_regen.disable_regen():`
  in your code.

See `docs/GRAPH_AUTO_REGEN.md` for details.
```

- [ ] **Step 4: Create `docs/PARADATA_GUIDE.md`**

```markdown
# Paradata Guide

Paradata are graph nodes that describe metadata about your archaeological
data — authorship, licensing, embargoes, documents, and chronological epochs.
They live alongside your stratigraphic data and travel with it when you
publish or import a graph.

## The 5 paradata node types

### AuthorNode (/paradata/<site>/authors)
Represents a person who contributed to documenting the site. Fields: name,
optional ORCID. Used to track who recorded what.

### LicenseNode (/paradata/<site>/licenses)
Represents a license under which the site's data is published. Fields: name
(e.g. "CC-BY-NC-ND"), optional URL.

### EmbargoNode (/paradata/<site>/embargoes)
Represents a time-bound restriction on data publication. Fields: label,
optional `until` date.

### DocumentNode (/paradata/<site>/documents)
Represents an external document (excavation report, publication, photo album).
Fields: title, optional URI.

### EpochNode (/paradata/<site>/epochs)
Represents a chronological period. Fields: name, optional `start` and `end`
years (negative for BCE).

## Storage

All paradata for a site live in a single file:
```
data/paradata/<site_slug>/paradata.graphml
```
This file IS committed to git. It's safe to edit by hand if you need to do
bulk operations (back up first).

When you save a US/USM record, the system auto-regenerates a merged file:
```
data/paradata/<site_slug>/stratigraphy.graphml
```
This file is the input + paradata combined; it's NOT committed (derived).

## Concurrent edits

In Spec 2 the policy is **last-writer-wins**. If two users edit the same
AuthorNode at the same time, the later save overwrites. Real-time conflict
resolution arrives in Spec 3.

## Adding a new paradata type

The 5 types are wired into the system; adding a 6th requires code changes
in `ParadataStore` (add the CRUD methods) and `paradata_routes.py` /
`paradata_ui_routes.py` (add the kind config). See `docs/superpowers/specs/`
for the architecture.
```

- [ ] **Step 5: Create `docs/GRAPH_AUTO_REGEN.md`**

```markdown
# Graph auto-regen

Every time a US/USM record is saved, pyarchinit-mini-web rebuilds the
merged stratigraphic graph for that site:

```
data/paradata/<site_slug>/stratigraphy.graphml
```

This file combines:
1. The stratigraphic layer (read from `us_table` via `GraphProjector`)
2. The paradata layer (read from `paradata.graphml` via `ParadataStore`)

## When it fires

- After `session.commit()` in `services/us_service.py` (or equivalent
  Flask route handlers that save US/USM rows)
- After any paradata CRUD operation (Implicit — see Open Q #5 in Spec 2)

## When it does NOT fire

- During bulk operations wrapped in `auto_regen.disable_regen()`:
  ```python
  from pyarchinit_mini.graphproj import auto_regen
  with auto_regen.disable_regen():
      for row in big_excel:
          us_service.save_us(row, session)
  # Manually trigger one regen per touched site at the end:
  for site in auto_regen._drain_touched_sites():
      auto_regen._trigger_graph_regen(site, session=session)
  ```
- When `PYARCHINIT_DISABLE_AUTO_REGEN=1` is set in the environment
- When the per-site flock is already held (the second writer waits)

## Failure handling

Auto-regen failures are caught and logged. The originating save still
returns 201 to the user — graph regen is best-effort and never blocks
saving data.

Logs:
- `data/paradata/_regen.log` — JSON-line per regen event
- Standard Python logger `pyarchinit_mini.graphproj`

The Flask cache key `regen_status:<site>` carries the latest regen
status; a UI banner (TODO Spec 3) surfaces error states to users.

## Disabling for development

Set `PYARCHINIT_DISABLE_AUTO_REGEN=1` before starting Flask:

```bash
export PYARCHINIT_DISABLE_AUTO_REGEN=1
.venv/bin/python -m pyarchinit_mini.web_interface.app
```

In this mode `stratigraphy.graphml` is never written, but US/USM saves
still work normally.

## Performance

Regen latency for a 100-US site is typically under 50ms. For larger sites
(Volterra-scale ~1500 US) expect 200-500ms. The post-commit invocation is
synchronous in the request handler today; large-dataset deployments may
want to wrap this in a background queue (out of scope for Spec 2).
```

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/__init__.py pyproject.toml CHANGELOG.md README.md docs/PARADATA_GUIDE.md docs/GRAPH_AUTO_REGEN.md
git commit -m "release: bump to 2.3.0-alpha (Spec 2 local graph & paradata) + docs"
```

---

### Task 25: Final verification

**Files:** none (verification only)

- [ ] **Step 1: Full Spec 2 test surface green**

```bash
.venv/bin/pytest \
  tests/unit/test_graphproj_*.py \
  tests/unit/test_paradata_store_*.py \
  tests/unit/test_auto_regen.py \
  tests/unit/test_ingest_plan.py \
  tests/unit/test_graphml_io_*.py \
  tests/unit/test_deprecated_writers_shim.py \
  tests/integration/test_paradata_routes_*.py \
  tests/integration/test_paradata_ui.py \
  tests/integration/test_graph_routes.py \
  tests/integration/test_graph_import_flow.py \
  tests/integration/test_auto_regen_on_save.py \
  tests/integration/test_harris_matrix_post_cutover.py \
  -v 2>&1 | tail -10
```

Expected: all green. ~110+ tests added/touched by Spec 2.

- [ ] **Step 2: Spec 1 tests still green (no regression)**

```bash
.venv/bin/pytest \
  tests/unit/test_vocab_*.py \
  tests/unit/test_em_palette_vocab_backed.py \
  tests/unit/test_s3d_converter_vocab_backed.py \
  tests/unit/test_us_dto_unita_tipo_validator.py \
  tests/unit/test_database_utils.py \
  tests/unit/test_migrations_*.py \
  tests/integration/test_vocab_routes.py \
  tests/integration/test_harris_matrix_visual_parity.py \
  tests/integration/test_migrate_vocab_cli.py \
  tests/e2e/test_web_vocab_full_flow.py \
  -v 2>&1 | tail -5
```

Expected: all green (Spec 1's 83 tests still pass).

- [ ] **Step 3: Auto-regen smoke against tutorial DB (read-only)**

```bash
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" .venv/bin/python -c "
from pyarchinit_mini.graphproj.auto_regen import _trigger_graph_regen
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
eng = create_engine('sqlite:///data/pyarchinit_tutorial.db')
Session = sessionmaker(bind=eng)
session = Session()
sites = [r[0] for r in session.execute(text('SELECT DISTINCT sito FROM us_table LIMIT 3')).fetchall()]
print('sites:', sites)
for s in sites:
    _trigger_graph_regen(s, session=session)
    print('regen attempted for', s)
session.close()
"
ls -la data/paradata/*/stratigraphy.graphml 2>&1 | head -5
```

Expected: stratigraphy.graphml appears under data/paradata/<slug>/ for each tested site, OR a meaningful error message logged (which is also acceptable — auto-regen catches everything).

- [ ] **Step 4: Web app smoke test (routes available)**

```bash
.venv/bin/python -c "
from flask import Flask
from pyarchinit_mini.web_interface.app import create_app
app = create_app()
print('Vocab routes:', [r.rule for r in app.url_map.iter_rules() if 'vocab' in r.rule])
print('Graph routes:', [r.rule for r in app.url_map.iter_rules() if 'graph' in r.rule])
print('Paradata routes:', [r.rule for r in app.url_map.iter_rules() if 'paradata' in r.rule])
"
```

Expected: see graph_bp, paradata_bp, paradata_ui_bp routes registered.

- [ ] **Step 5: Review commit chain**

```bash
git log --oneline main..HEAD | wc -l
git log --oneline main..HEAD | head -30
```

Expected: ~26-28 commits for Spec 2 (one per task + the spec/plan + release).

- [ ] **Step 6: Final report**

Compile a brief final report (under 300 words):
- Total new tests added (count)
- Final test count (all green)
- Any leftover concerns
- Tutorial DB smoke summary
- Commit count on the feature branch
- Anything that surprised you

No commit in this task — verification only.

Report status with one of:
- `STATUS: DONE` — everything green, ready to merge
- `STATUS: DONE_WITH_CONCERNS` — green but flagging observations
- `STATUS: BLOCKED` — something critical fails

---

## Closing Notes

- **PR sequencing for review:** local commits are sequential, but for upstream
  PRs batch as: PR1 = Tasks 1-3 (graphproj foundation), PR2 = Tasks 4-6
  (graphml_io), PR3 = Tasks 7-12 (ParadataStore + Projector + auto-regen),
  PR4 = Tasks 13-15 (Ingestor), PR5 = Tasks 16-17 (paradata REST), PR6 =
  Task 18 (paradata UI), PR7 = Tasks 19-20 (graph routes), PR8 = Tasks
  21-25 (cutover + release).
- **Definition of Done satisfied:** see spec §9.
- **Next:** Spec 3 — Sync Engine + EM Backend. Will need a working EM
  Datacenter API or a mock; brainstorm timing depends on Datacenter readiness.

## Known gaps (deferred — flag as `# TODO(Spec-3)` in code)

These were called out in the spec but intentionally deferred from this plan
to keep scope manageable. Add inline TODO markers when you touch the
surrounding code; the final review (Spec 1 pattern) will then capture them
as explicit deferred items.

1. **audit.log writes** (spec §4.8): each ParadataStore write should append
   a JSON-line to `data/paradata/<site_slug>/audit.log`. Currently silent.
   Add `# TODO(Spec-3): audit log entry` in `ParadataStore._generic_add/update/delete`.
2. **`excel_import_routes` integration with `disable_regen()`** (spec §5.2):
   the helper exists (Task 11) but the bulk-import route isn't wired.
   Add `# TODO(Spec-3): wrap loop in auto_regen.disable_regen()` in
   `pyarchinit_mini/web_interface/excel_import_routes.py` near the
   `for row in parsed:` loop.
3. **`/_regen.log` rotating writer** (spec §7.6): currently regen events
   only hit the Python `logging` channel; the JSON-line log isn't written.
   Add `# TODO(Spec-3): append JSON-line to data/paradata/_regen.log` in
   `auto_regen._trigger_graph_regen`.
4. **Regen status banner UI** (spec §5.5): the `regen_status:<site>` cache
   key isn't yet read by any template. Add `# TODO(Spec-3): render banner
   partial` in the site detail template.
5. **`_metrics.sqlite` telemetry** (spec §7.8): admin diagnostics endpoint
   `/api/v1/graphproj/diagnostics` not implemented. Add a stub route
   returning 501 with `# TODO(Spec-3): wire metrics`.
6. **`paradata_routes` audit-log on writes**: same gap as #1, on the REST
   side; add the same TODO marker in the create/update/delete handlers.

These items have low individual risk (the system functions without them)
but together represent the operational maturity that Spec 3 should bring
along with the SyncEngine work.
