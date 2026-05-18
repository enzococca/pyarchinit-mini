# Spec 3-bis — Harris Swimlane Editor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring yEd-like swimlanes (rows = period+phase) back to the Harris Matrix Creator. Auto-place existing US records by `periodo_iniziale + fase_iniziale`; allow interactive row creation; emit yEd-flavored GraphML with `y:TableNode + y:Rows`. New writer separate from Spec 2's s3dgraphy delegate (legacy `pure_networkx_exporter` stays deprecated).

**Architecture:** New `pyarchinit_mini/harris_swimlane/` package (5 modules: row_provider, swimlane_state, period_sync_service, compound_layout, exceptions) + new `graphml_io/yed_writer.py` + 5 new REST endpoints + editor.html updates (Cytoscape compound nodes). Drag-drop persists only on explicit Save; Save endpoint also triggers Spec 2 auto_regen of `stratigraphy.graphml`. yEd export is on-demand to `data/exports/harris_yed/<slug>-harris-yed.graphml`.

**Tech Stack:** Python 3.13, Flask, SQLAlchemy, pytest, Cytoscape.js, s3dgraphy 0.1.42+ (only for visual style lookup via VocabProvider — not for export here), `xml.etree.ElementTree` for yEd GraphML emission.

**Spec:** `docs/superpowers/specs/2026-05-18-harris-swimlane-template-design.md`

---

## File Structure

### New files

| Path | Responsibility |
|---|---|
| `pyarchinit_mini/harris_swimlane/__init__.py` | Package init + public re-exports |
| `pyarchinit_mini/harris_swimlane/exceptions.py` | SwimlaneError + 4 subclasses (RowProviderError, PeriodSyncError, SwimlaneStateError, YEDWriterError) |
| `pyarchinit_mini/harris_swimlane/row_provider.py` | `Row` frozen dataclass + `RowProvider` class with `list_rows()` + `find_row()`; period_table priority → fallback distinct |
| `pyarchinit_mini/harris_swimlane/period_sync_service.py` | `PeriodSyncService.upsert_row()` + `maybe_promote_fallback()` |
| `pyarchinit_mini/harris_swimlane/compound_layout.py` | `initial_node_position()`, `compute_row_positions()`, `derive_row_id()` slugifier |
| `pyarchinit_mini/harris_swimlane/swimlane_state.py` | `CytoscapeElement`, `EditorState`, `SaveResult` dataclasses + `SwimlaneState.load()` + `SwimlaneState.save()` |
| `pyarchinit_mini/graphml_io/yed_writer.py` | `write_yed_graphml(state, path)` — y:TableNode + y:Rows + y:ShapeNode per US |
| `tests/unit/test_harris_swimlane_exceptions.py` | 5 exception classes |
| `tests/unit/test_harris_swimlane_row_provider.py` | period_table happy path + fallback + sort + color cycling |
| `tests/unit/test_harris_swimlane_period_sync.py` | upsert_row idempotency + validation |
| `tests/unit/test_harris_swimlane_compound_layout.py` | positioning math + derive_row_id slugifier |
| `tests/unit/test_harris_swimlane_state_load.py` | EditorState construction from DB + edges via EdgeRegistry |
| `tests/unit/test_harris_swimlane_state_save.py` | DB UPDATE/INSERT/DELETE + transactional rollback + auto_regen invocation |
| `tests/unit/test_yed_writer.py` | XML structure + VocabProvider styling + atomic write |
| `tests/integration/test_yed_writer_parity.py` | Golden fixture parity (PR2 gate) |
| `tests/integration/test_harris_swimlane_routes_load.py` | GET /api/swimlanes/<site> + /api/load/<site> |
| `tests/integration/test_harris_swimlane_routes_save.py` | POST /api/save/<site> + auto_regen integration |
| `tests/integration/test_harris_swimlane_routes_create_row.py` | POST /api/swimlanes/<site> + period_table side-effect |
| `tests/integration/test_yed_export_route.py` | GET /api/export/<site>/yed-graphml |
| `tests/e2e/test_harris_swimlane_full_flow.py` | Load → drag → save → re-load + empty-site flow |
| `tests/fixtures/databases/sqlite_volterra_30us_with_periods.db` | 30 US distributed over 5 (period, phase) rows |
| `tests/fixtures/databases/sqlite_periodizzazione_only.db` | Fallback path fixture |
| `tests/fixtures/databases/sqlite_empty_site.db` | Empty state fixture |
| `tests/fixtures/cytoscape_states/volterra_loaded.json` | Expected /api/load response |
| `tests/fixtures/cytoscape_states/volterra_pending_changes.json` | Typical /api/save body |
| `tests/fixtures/yed_graphml_outputs/volterra_baseline.graphml` | Golden yed_writer output (parity gate) |
| `tests/fixtures/_generate_harris_swimlane_synthetic.py` | One-shot fixture generator (committed for reproducibility) |
| `docs/HARRIS_SWIMLANE.md` | User docs — editor usage + drag-drop + row creation |
| `docs/YED_INTEGRATION.md` | Advanced docs — round-trip, limits, future specs |

### Modified files

| Path | Change |
|---|---|
| `pyarchinit_mini/web_interface/harris_creator_routes.py` | Add 5 new endpoints; imports for harris_swimlane + yed_writer + auto_regen |
| `pyarchinit_mini/web_interface/templates/harris_creator/editor.html` | Cytoscape compound config + drag-drop handlers + "+ New Row" modal + Save button + Export button |
| `pyarchinit_mini/__init__.py` | Bump version `2.3.0-alpha → 2.4.0-alpha` |
| `pyproject.toml` | Bump version |
| `CHANGELOG.md` | Prepend bilingual entry |
| `README.md` | Add "Harris Swimlane Editor" section |
| `.gitignore` | Add `data/exports/harris_yed/**/*.graphml`, `data/exports/harris_yed/_index.json`, `data/exports/harris_yed/*.tmp` |

---

## PR1 — harris_swimlane Foundation

### Task 1: Package skeleton + exceptions

**Files:**
- Create: `pyarchinit_mini/harris_swimlane/__init__.py`
- Create: `pyarchinit_mini/harris_swimlane/exceptions.py`
- Test: `tests/unit/test_harris_swimlane_exceptions.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_harris_swimlane_exceptions.py
import pytest
from pyarchinit_mini.harris_swimlane.exceptions import (
    SwimlaneError,
    RowProviderError,
    PeriodSyncError,
    SwimlaneStateError,
    YEDWriterError,
)


def test_swimlane_error_is_base():
    assert issubclass(RowProviderError, SwimlaneError)
    assert issubclass(PeriodSyncError, SwimlaneError)
    assert issubclass(SwimlaneStateError, SwimlaneError)
    assert issubclass(YEDWriterError, SwimlaneError)


def test_row_provider_error_carries_site():
    err = RowProviderError("missing rows", site="X")
    assert err.site == "X"
    assert "missing rows" in str(err)


def test_period_sync_error_carries_period():
    err = PeriodSyncError("duplicate", period_name="P1", phase_name="a")
    assert err.period_name == "P1"
    assert err.phase_name == "a"


def test_yed_writer_error_carries_path():
    err = YEDWriterError(path="/tmp/x.graphml", msg="disk full")
    assert err.path == "/tmp/x.graphml"
    assert "disk full" in str(err)


def test_swimlane_state_error_carries_op():
    err = SwimlaneStateError("rollback", op="save")
    assert err.op == "save"
```

- [ ] **Step 2: Run, verify ImportError**

Run: `.venv/bin/pytest tests/unit/test_harris_swimlane_exceptions.py -v`

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/harris_swimlane/__init__.py
"""Harris Matrix swimlane editor backend (Spec 3-bis)."""
```

```python
# pyarchinit_mini/harris_swimlane/exceptions.py
from typing import Optional


class SwimlaneError(Exception):
    """Base for harris_swimlane errors."""


class RowProviderError(SwimlaneError):
    def __init__(self, msg: str, *, site: Optional[str] = None) -> None:
        super().__init__(msg)
        self.site = site


class PeriodSyncError(SwimlaneError):
    def __init__(self, msg: str, *, period_name: Optional[str] = None,
                 phase_name: Optional[str] = None) -> None:
        super().__init__(msg)
        self.period_name = period_name
        self.phase_name = phase_name


class SwimlaneStateError(SwimlaneError):
    def __init__(self, msg: str, *, op: Optional[str] = None) -> None:
        super().__init__(msg)
        self.op = op


class YEDWriterError(SwimlaneError):
    def __init__(self, *, path: str, msg: str) -> None:
        super().__init__(f"{msg} (path={path})")
        self.path = path
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_harris_swimlane_exceptions.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/harris_swimlane/__init__.py pyarchinit_mini/harris_swimlane/exceptions.py tests/unit/test_harris_swimlane_exceptions.py
git commit -m "feat(harris_swimlane): add exception hierarchy"
```

---

### Task 2: compound_layout helpers (Row dataclass + slugify)

**Files:**
- Create: `pyarchinit_mini/harris_swimlane/compound_layout.py`
- Test: `tests/unit/test_harris_swimlane_compound_layout.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_harris_swimlane_compound_layout.py
import pytest
from pyarchinit_mini.harris_swimlane.compound_layout import (
    derive_row_id,
    initial_node_position,
    compute_row_positions,
)
from pyarchinit_mini.harris_swimlane.row_provider import Row


def test_derive_row_id_period_and_phase():
    assert derive_row_id("Period 1", "a") == "row_period-1_a"


def test_derive_row_id_period_only():
    assert derive_row_id("Roman Imperial", None) == "row_roman-imperial"


def test_derive_row_id_unassigned():
    assert derive_row_id(None, None) == "_unassigned"


def test_initial_node_position_returns_xy():
    row = Row(row_id="row_p1_a", period_name="P1", phase_name="a",
              start_date=100, end_date=200, color="#FF0000", source="period_table")
    pos = initial_node_position(row, index_in_row=0)
    assert "x" in pos and "y" in pos
    assert isinstance(pos["x"], (int, float))
    assert isinstance(pos["y"], (int, float))


def test_initial_node_position_spaces_nodes_horizontally():
    row = Row(row_id="r", period_name="P", phase_name=None,
              start_date=None, end_date=None, color="#000", source="period_table")
    p0 = initial_node_position(row, 0)
    p1 = initial_node_position(row, 1)
    assert p1["x"] > p0["x"]  # nodes spread horizontally within row


def test_compute_row_positions_recent_at_top():
    rows = [
        Row("r1", "P1", "a", 100, 200, "#000", "period_table"),
        Row("r2", "P2", "a", 200, 300, "#111", "period_table"),
        Row("r3", "P3", "a", 300, 400, "#222", "period_table"),
    ]
    positions = compute_row_positions(rows)
    # r3 (most recent, start_date=300) should have smallest y (top of canvas)
    assert positions["r3"][1] < positions["r2"][1] < positions["r1"][1]


def test_compute_row_positions_handles_nulls():
    rows = [
        Row("r_none", "P", None, None, None, "#000", "fallback_distinct"),
        Row("r_p1", "P1", "a", 100, 200, "#111", "period_table"),
    ]
    positions = compute_row_positions(rows)
    # Both rows get valid positions; nulls sort to bottom (stable)
    assert positions["r_p1"][1] != positions["r_none"][1]
```

- [ ] **Step 2: Run, verify ImportError**

Run: `.venv/bin/pytest tests/unit/test_harris_swimlane_compound_layout.py -v`

The test imports `Row` from `row_provider`, which doesn't exist yet. Defer those imports by writing a placeholder Row first:

Create a temporary `pyarchinit_mini/harris_swimlane/row_provider.py` (Task 3 will overwrite):

```python
# pyarchinit_mini/harris_swimlane/row_provider.py
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Row:
    row_id: str
    period_name: str
    phase_name: Optional[str]
    start_date: Optional[int]
    end_date: Optional[int]
    color: str
    source: str
```

This stub is enough to import `Row`. Task 3 will add `RowProvider` to the same file.

- [ ] **Step 3: Implement compound_layout.py**

```python
# pyarchinit_mini/harris_swimlane/compound_layout.py
"""Cytoscape compound layout helpers + row_id slugifier.

Coordinate system: x grows right, y grows DOWN (canvas convention).
Recent rows go to TOP (smaller y). Spec D4.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Optional


CANVAS_WIDTH = 2000
ROW_HEIGHT_BASE = 80
ROW_HEIGHT_PER_NODE = 40
NODE_WIDTH = 100
NODE_HORIZONTAL_GAP = 20
NODE_INITIAL_X = 50
NODE_INITIAL_Y = 20


def derive_row_id(period_name: Optional[str], phase_name: Optional[str]) -> str:
    """Slugify (period, phase) into a stable row_id.

    Returns '_unassigned' if both are None/empty.
    """
    if not period_name or not period_name.strip():
        return "_unassigned"
    p_slug = _slug_part(period_name)
    if not phase_name or not phase_name.strip():
        return f"row_{p_slug}"
    ph_slug = _slug_part(phase_name)
    return f"row_{p_slug}_{ph_slug}"


def _slug_part(s: str) -> str:
    folded = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    out = folded.lower()
    out = re.sub(r"[^a-z0-9]+", "-", out)
    return out.strip("-")


def initial_node_position(row, index_in_row: int) -> dict:
    """Compute initial (x, y) for a node within its row parent.

    x: NODE_INITIAL_X + index * (NODE_WIDTH + NODE_HORIZONTAL_GAP)
    y: NODE_INITIAL_Y (Cytoscape places within parent compound)
    """
    return {
        "x": NODE_INITIAL_X + index_in_row * (NODE_WIDTH + NODE_HORIZONTAL_GAP),
        "y": NODE_INITIAL_Y,
    }


def compute_row_positions(rows) -> dict:
    """Stack rows top-to-bottom; recent (highest start_date) at top.

    Returns {row_id: (x, y)} for each row's top-left corner.
    Rows with NULL start_date go to the bottom (stable order).
    """
    # Separate rows with start_date from those without
    dated = [r for r in rows if r.start_date is not None]
    undated = [r for r in rows if r.start_date is None]
    # Sort dated by start_date descending (most recent first)
    dated_sorted = sorted(dated, key=lambda r: -r.start_date)
    # Undated keep original order
    ordered = dated_sorted + undated

    positions = {}
    cursor_y = 0
    for row in ordered:
        positions[row.row_id] = (0, cursor_y)
        # Height per row is computed elsewhere; reserve fixed base for now
        cursor_y += ROW_HEIGHT_BASE
    return positions
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_harris_swimlane_compound_layout.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/harris_swimlane/compound_layout.py pyarchinit_mini/harris_swimlane/row_provider.py tests/unit/test_harris_swimlane_compound_layout.py
git commit -m "feat(harris_swimlane): add compound_layout helpers + Row dataclass stub"
```

---

### Task 3: RowProvider with period_table priority + fallback

**Files:**
- Modify: `pyarchinit_mini/harris_swimlane/row_provider.py` (extend with RowProvider class)
- Test: `tests/unit/test_harris_swimlane_row_provider.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_harris_swimlane_row_provider.py
import sqlite3
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.harris_swimlane.row_provider import Row, RowProvider


@pytest.fixture
def session_with_period_table(tmp_path):
    db = tmp_path / "rp.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE period_table (
        id_period INTEGER PRIMARY KEY,
        period_name TEXT NOT NULL,
        phase_name TEXT,
        start_date INTEGER,
        end_date INTEGER,
        description TEXT,
        chronology TEXT
    )""")
    conn.execute("""CREATE TABLE periodizzazione_table (
        id_periodizzazione INTEGER PRIMARY KEY,
        sito TEXT, area TEXT, us INTEGER,
        periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT
    )""")
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY,
        sito TEXT, us INTEGER,
        periodo_iniziale TEXT, fase_iniziale TEXT
    )""")
    rows = [
        ("Roman Imperial", "early", -27, 100),
        ("Roman Imperial", "late", 100, 476),
        ("Medieval", "early", 476, 1000),
    ]
    for r in rows:
        conn.execute(
            "INSERT INTO period_table (period_name, phase_name, start_date, end_date) VALUES (?,?,?,?)",
            r,
        )
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


@pytest.fixture
def session_fallback_only(tmp_path):
    """No period_table; distinct values in periodizzazione_table."""
    db = tmp_path / "rp_fb.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE period_table (
        id_period INTEGER PRIMARY KEY, period_name TEXT, phase_name TEXT,
        start_date INTEGER, end_date INTEGER, description TEXT, chronology TEXT
    )""")
    conn.execute("""CREATE TABLE periodizzazione_table (
        id_periodizzazione INTEGER PRIMARY KEY,
        sito TEXT, area TEXT, us INTEGER,
        periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT
    )""")
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY,
        sito TEXT, us INTEGER,
        periodo_iniziale TEXT, fase_iniziale TEXT
    )""")
    pz = [
        ("Volterra", "A", 1, "Roman", "a", None, None),
        ("Volterra", "A", 2, "Medieval", "b", None, None),
        ("Volterra", "A", 3, "Roman", "a", None, None),
    ]
    for r in pz:
        conn.execute(
            "INSERT INTO periodizzazione_table (sito, area, us, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale) VALUES (?,?,?,?,?,?,?)",
            r,
        )
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def test_list_rows_from_period_table_sorted_recent_first(session_with_period_table):
    rows = RowProvider(session_with_period_table, "Volterra").list_rows()
    assert len(rows) == 3
    # Medieval/early (start=476) should be the most recent
    assert rows[0].period_name == "Medieval"
    assert rows[1].period_name == "Roman Imperial"
    assert rows[1].phase_name == "late"
    assert rows[2].phase_name == "early"


def test_list_rows_source_period_table(session_with_period_table):
    rows = RowProvider(session_with_period_table, "Volterra").list_rows()
    for r in rows:
        assert r.source == "period_table"


def test_list_rows_assigns_color(session_with_period_table):
    rows = RowProvider(session_with_period_table, "Volterra").list_rows()
    for r in rows:
        assert r.color.startswith("#")
        assert len(r.color) == 7


def test_list_rows_fallback_path(session_fallback_only):
    rows = RowProvider(session_fallback_only, "Volterra").list_rows()
    assert len(rows) == 2  # 2 distinct (period, phase) pairs
    for r in rows:
        assert r.source == "fallback_distinct"
        assert r.start_date is None


def test_find_row_returns_match(session_with_period_table):
    rp = RowProvider(session_with_period_table, "Volterra")
    rp.list_rows()  # populate cache
    row = rp.find_row("Roman Imperial", "early")
    assert row is not None
    assert row.period_name == "Roman Imperial"


def test_find_row_unknown_returns_none(session_with_period_table):
    rp = RowProvider(session_with_period_table, "Volterra")
    rp.list_rows()
    assert rp.find_row("Bogus", "x") is None
```

- [ ] **Step 2: Run, verify failure**

- [ ] **Step 3: Extend row_provider.py with RowProvider class**

Replace the contents of `pyarchinit_mini/harris_swimlane/row_provider.py`:

```python
# pyarchinit_mini/harris_swimlane/row_provider.py
"""RowProvider — derives swimlane rows from period_table (priority)
or distinct (periodo_iniziale, fase_iniziale) values in periodizzazione_table
+ us_table (fallback). Spec D2."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from .compound_layout import derive_row_id


# Reused from graphml_converter/yed_template.py:YEdTemplate.PERIOD_COLORS
PERIOD_COLORS = [
    "#9642B7", "#7204CB", "#20ADB7", "#65C3E4", "#FA9639",
    "#85E1C9", "#6105C3", "#1DBCB1", "#9DC185", "#CB99D2",
    "#B7D2DF", "#D406E6", "#1E4B4B", "#7E0BD6", "#07D688",
    "#D37843", "#342400", "#F747A0", "#52BD36", "#E58042",
    "#097728", "#C84643", "#C9FC9E", "#085DE8", "#E4CC6F",
    "#3A8B9E", "#D4A5E8", "#8FE3B0", "#F2A65A", "#7B68EE",
]


@dataclass(frozen=True)
class Row:
    row_id: str
    period_name: str
    phase_name: Optional[str]
    start_date: Optional[int]
    end_date: Optional[int]
    color: str
    source: str  # "period_table" | "fallback_distinct"


class RowProvider:
    def __init__(self, session: Session, site: str) -> None:
        self.session = session
        self.site = site
        self._cache: Optional[list[Row]] = None

    def list_rows(self) -> list[Row]:
        if self._cache is not None:
            return self._cache
        rows = self._load_from_period_table()
        if not rows:
            rows = self._load_fallback()
        self._cache = rows
        return rows

    def find_row(self, period: str, phase: Optional[str]) -> Optional[Row]:
        for r in self.list_rows():
            if r.period_name == period and (r.phase_name or None) == (phase or None):
                return r
        return None

    def _load_from_period_table(self) -> list[Row]:
        result = self.session.execute(text(
            "SELECT period_name, phase_name, start_date, end_date "
            "FROM period_table ORDER BY start_date DESC NULLS LAST, period_name, phase_name"
        )).fetchall()
        out = []
        for i, r in enumerate(result):
            period = r[0]
            phase = r[1]
            row_id = derive_row_id(period, phase)
            out.append(Row(
                row_id=row_id,
                period_name=period,
                phase_name=phase,
                start_date=r[2],
                end_date=r[3],
                color=PERIOD_COLORS[i % len(PERIOD_COLORS)],
                source="period_table",
            ))
        return out

    def _load_fallback(self) -> list[Row]:
        # Union distinct from periodizzazione_table + us_table
        sql = (
            "SELECT DISTINCT periodo_iniziale, fase_iniziale "
            "FROM periodizzazione_table WHERE sito = :sito "
            "UNION "
            "SELECT DISTINCT periodo_iniziale, fase_iniziale "
            "FROM us_table WHERE sito = :sito"
        )
        result = self.session.execute(text(sql), {"sito": self.site}).fetchall()
        out = []
        sorted_result = sorted(
            (r for r in result if r[0]),  # filter NULLs
            key=lambda r: (r[0] or "", r[1] or ""),
        )
        for i, r in enumerate(sorted_result):
            period = r[0]
            phase = r[1]
            row_id = derive_row_id(period, phase)
            out.append(Row(
                row_id=row_id,
                period_name=period,
                phase_name=phase,
                start_date=None,
                end_date=None,
                color=PERIOD_COLORS[i % len(PERIOD_COLORS)],
                source="fallback_distinct",
            ))
        return out
```

If SQLite version on test machine doesn't support `NULLS LAST` (older SQLite), the test may error. SQLite 3.30+ supports it. Modern Python ships SQLite >= 3.35. If you hit the issue, replace the ORDER BY with manual sort in Python.

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_harris_swimlane_row_provider.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/harris_swimlane/row_provider.py tests/unit/test_harris_swimlane_row_provider.py
git commit -m "feat(harris_swimlane): RowProvider with period_table priority + fallback"
```

---

### Task 4: PeriodSyncService.upsert_row

**Files:**
- Create: `pyarchinit_mini/harris_swimlane/period_sync_service.py`
- Test: `tests/unit/test_harris_swimlane_period_sync.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_harris_swimlane_period_sync.py
import sqlite3
import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.harris_swimlane.period_sync_service import PeriodSyncService
from pyarchinit_mini.harris_swimlane.exceptions import PeriodSyncError


@pytest.fixture
def session(tmp_path):
    db = tmp_path / "ps.db"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE period_table (
        id_period INTEGER PRIMARY KEY AUTOINCREMENT,
        period_name TEXT NOT NULL,
        phase_name TEXT,
        start_date INTEGER, end_date INTEGER,
        description TEXT, chronology TEXT
    )""")
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def test_upsert_row_creates_new_entry(session):
    svc = PeriodSyncService(session)
    row = svc.upsert_row(period_name="P1", phase_name="a",
                         start_date=100, end_date=200)
    assert row.period_name == "P1"
    assert row.phase_name == "a"
    assert row.start_date == 100
    assert row.row_id == "row_p1_a"


def test_upsert_row_idempotent(session):
    svc = PeriodSyncService(session)
    svc.upsert_row(period_name="P1", phase_name="a", start_date=100, end_date=200)
    svc.upsert_row(period_name="P1", phase_name="a", start_date=100, end_date=200)
    count = session.execute(text(
        "SELECT COUNT(*) FROM period_table WHERE period_name='P1' AND phase_name='a'"
    )).scalar()
    assert count == 1


def test_upsert_row_different_phase_creates_new(session):
    svc = PeriodSyncService(session)
    svc.upsert_row(period_name="P1", phase_name="a")
    svc.upsert_row(period_name="P1", phase_name="b")
    count = session.execute(text(
        "SELECT COUNT(*) FROM period_table WHERE period_name='P1'"
    )).scalar()
    assert count == 2


def test_upsert_row_empty_period_raises(session):
    svc = PeriodSyncService(session)
    with pytest.raises(PeriodSyncError):
        svc.upsert_row(period_name="")


def test_upsert_row_invalid_date_range_raises(session):
    svc = PeriodSyncService(session)
    with pytest.raises(PeriodSyncError):
        svc.upsert_row(period_name="P1", phase_name="a",
                       start_date=200, end_date=100)


def test_upsert_row_no_phase(session):
    svc = PeriodSyncService(session)
    row = svc.upsert_row(period_name="Iron Age")
    assert row.phase_name is None
    assert row.row_id == "row_iron-age"
```

- [ ] **Step 2: Run, verify failure**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/harris_swimlane/period_sync_service.py
"""PeriodSyncService — interactive row creation upserts period_table.

When user creates a new swimlane row in the editor, this service ensures
a corresponding period_table entry exists. Idempotent on (period_name,
phase_name) pair. Spec §4.3.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from .compound_layout import derive_row_id
from .exceptions import PeriodSyncError
from .row_provider import Row, PERIOD_COLORS


class PeriodSyncService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_row(self, period_name: str, phase_name: Optional[str] = None,
                   start_date: Optional[int] = None,
                   end_date: Optional[int] = None) -> Row:
        if not period_name or not period_name.strip():
            raise PeriodSyncError("period_name is required",
                                   period_name=period_name, phase_name=phase_name)
        if start_date is not None and end_date is not None and start_date > end_date:
            raise PeriodSyncError(
                "start_date must be <= end_date",
                period_name=period_name, phase_name=phase_name,
            )

        # Check if entry already exists
        existing = self.session.execute(text(
            "SELECT id_period, start_date, end_date FROM period_table "
            "WHERE period_name = :p AND "
            "(phase_name = :ph OR (phase_name IS NULL AND :ph IS NULL))"
        ), {"p": period_name, "ph": phase_name}).fetchone()

        if existing is None:
            self.session.execute(text(
                "INSERT INTO period_table (period_name, phase_name, start_date, end_date) "
                "VALUES (:p, :ph, :sd, :ed)"
            ), {"p": period_name, "ph": phase_name, "sd": start_date, "ed": end_date})
            self.session.commit()
            sd = start_date
            ed = end_date
        else:
            sd = existing[1]
            ed = existing[2]

        row_id = derive_row_id(period_name, phase_name)
        return Row(
            row_id=row_id,
            period_name=period_name,
            phase_name=phase_name,
            start_date=sd,
            end_date=ed,
            color=PERIOD_COLORS[0],  # caller may reassign on full list refresh
            source="period_table",
        )

    def maybe_promote_fallback(self, site: str) -> int:
        """Bulk-promote distinct (periodo_iniziale, fase_iniziale) values from
        periodizzazione_table + us_table into period_table.

        Returns count promoted. Idempotent. Not exposed to UI in Spec 3-bis
        (Spec 4 territory)."""
        existing = {
            (r[0], r[1])
            for r in self.session.execute(text(
                "SELECT period_name, phase_name FROM period_table"
            )).fetchall()
        }
        candidates = self.session.execute(text(
            "SELECT DISTINCT periodo_iniziale, fase_iniziale "
            "FROM periodizzazione_table WHERE sito = :s "
            "UNION "
            "SELECT DISTINCT periodo_iniziale, fase_iniziale "
            "FROM us_table WHERE sito = :s"
        ), {"s": site}).fetchall()
        count = 0
        for period, phase in candidates:
            if not period:
                continue
            if (period, phase) in existing:
                continue
            try:
                self.upsert_row(period_name=period, phase_name=phase)
                count += 1
            except PeriodSyncError:
                continue
        return count
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_harris_swimlane_period_sync.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/harris_swimlane/period_sync_service.py tests/unit/test_harris_swimlane_period_sync.py
git commit -m "feat(harris_swimlane): PeriodSyncService.upsert_row (idempotent)"
```

---

## PR2 — yed_writer

### Task 5: Generate synthetic test DB + Cytoscape fixture

**Files:**
- Create: `tests/fixtures/_generate_harris_swimlane_synthetic.py`
- Create: `tests/fixtures/databases/sqlite_volterra_30us_with_periods.db`
- Create: `tests/fixtures/cytoscape_states/volterra_loaded.json`

- [ ] **Step 1: Write the fixture generator**

```python
# tests/fixtures/_generate_harris_swimlane_synthetic.py
"""One-shot generator for harris_swimlane test fixtures. Run once; commit outputs."""
import json
import sqlite3
from pathlib import Path

FIX = Path(__file__).parent
DB = FIX / "databases" / "sqlite_volterra_30us_with_periods.db"
JSON_OUT = FIX / "cytoscape_states" / "volterra_loaded.json"

DB.parent.mkdir(parents=True, exist_ok=True)
JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
if DB.exists():
    DB.unlink()

conn = sqlite3.connect(DB)
c = conn.cursor()

c.executescript("""
CREATE TABLE period_table (
    id_period INTEGER PRIMARY KEY AUTOINCREMENT,
    period_name TEXT NOT NULL,
    phase_name TEXT,
    start_date INTEGER, end_date INTEGER,
    description TEXT, chronology TEXT
);
CREATE TABLE periodizzazione_table (
    id_periodizzazione INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT, area TEXT, us INTEGER,
    periodo_iniziale TEXT, fase_iniziale TEXT,
    periodo_finale TEXT, fase_finale TEXT
);
CREATE TABLE us_table (
    id_us INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT, area TEXT, us INTEGER, unita_tipo TEXT,
    d_stratigrafica TEXT, d_interpretativa TEXT,
    rapporti TEXT, node_uuid TEXT,
    periodo_iniziale TEXT, fase_iniziale TEXT,
    periodo_finale TEXT, fase_finale TEXT
);
""")

# 5 (period, phase) rows
periods = [
    ("Roman", "a", -27, 100),
    ("Roman", "b", 100, 300),
    ("Late Antiquity", "a", 300, 600),
    ("Medieval", "a", 600, 1200),
    ("Medieval", "b", 1200, 1500),
]
for p, ph, sd, ed in periods:
    c.execute(
        "INSERT INTO period_table (period_name, phase_name, start_date, end_date) VALUES (?,?,?,?)",
        (p, ph, sd, ed),
    )

# 30 US distributed
us_records = []
for i in range(30):
    period, phase, _, _ = periods[i % 5]
    rapporti = f"copre {1000 + (i+1) % 30}" if i % 3 == 0 else ""
    us_records.append(
        ("Volterra", "A", 1000 + i, "US",
         f"strat {i}", f"interp {i}",
         rapporti, f"uuid-{i:03d}",
         period, phase, None, None)
    )
c.executemany(
    "INSERT INTO us_table (sito, area, us, unita_tipo, d_stratigrafica, d_interpretativa, rapporti, node_uuid, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
    us_records,
)

conn.commit()
conn.close()
print(f"Wrote {DB} (30 US, 5 periods)")

# Expected Cytoscape JSON structure (for test_swimlane_state_load.py reference)
cytoscape = {
    "rows": [
        {"row_id": "row_medieval_b", "period_name": "Medieval", "phase_name": "b"},
        {"row_id": "row_medieval_a", "period_name": "Medieval", "phase_name": "a"},
        {"row_id": "row_late-antiquity_a", "period_name": "Late Antiquity", "phase_name": "a"},
        {"row_id": "row_roman_b", "period_name": "Roman", "phase_name": "b"},
        {"row_id": "row_roman_a", "period_name": "Roman", "phase_name": "a"},
    ],
    "nodes_count": 30,
    "edges_count_at_least": 10,
}
JSON_OUT.write_text(json.dumps(cytoscape, indent=2))
print(f"Wrote {JSON_OUT}")
```

- [ ] **Step 2: Run the generator**

```bash
cd /Users/enzo/pyarchinit-mini-desk
.venv/bin/python tests/fixtures/_generate_harris_swimlane_synthetic.py
```

Expected: `Wrote tests/fixtures/databases/sqlite_volterra_30us_with_periods.db (30 US, 5 periods)` and `Wrote tests/fixtures/cytoscape_states/volterra_loaded.json`.

- [ ] **Step 3: Verify the DB**

```bash
.venv/bin/python -c "
import sqlite3
conn = sqlite3.connect('tests/fixtures/databases/sqlite_volterra_30us_with_periods.db')
print('US count:', conn.execute('SELECT COUNT(*) FROM us_table').fetchone()[0])
print('Period count:', conn.execute('SELECT COUNT(*) FROM period_table').fetchone()[0])
print('Sample US:')
for r in conn.execute('SELECT us, unita_tipo, periodo_iniziale, fase_iniziale FROM us_table LIMIT 3'):
    print(' ', r)
"
```

Expected: 30 US, 5 periods.

- [ ] **Step 4: Commit fixtures + generator**

```bash
git add tests/fixtures/_generate_harris_swimlane_synthetic.py tests/fixtures/databases/sqlite_volterra_30us_with_periods.db tests/fixtures/cytoscape_states/volterra_loaded.json
git commit -m "test(harris_swimlane): add synthetic DB fixture (30 US, 5 periods)"
```

---

### Task 6: yed_writer minimal (XML root + TableNode skeleton)

**Files:**
- Create: `pyarchinit_mini/graphml_io/yed_writer.py`
- Test: `tests/unit/test_yed_writer.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_yed_writer.py
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest

from pyarchinit_mini.harris_swimlane.row_provider import Row
from pyarchinit_mini.harris_swimlane.swimlane_state import EditorState
from pyarchinit_mini.graphml_io.yed_writer import write_yed_graphml


def _empty_state():
    return EditorState(
        site="Test", rows=[], nodes=[], edges=[], pending_changes={},
    )


def _state_with_one_row():
    row = Row(row_id="row_p1_a", period_name="P1", phase_name="a",
              start_date=100, end_date=200, color="#FF0000", source="period_table")
    return EditorState(
        site="Test", rows=[row], nodes=[], edges=[], pending_changes={},
    )


def test_write_yed_graphml_creates_file(tmp_path):
    state = _empty_state()
    out = tmp_path / "empty.graphml"
    write_yed_graphml(state, out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "<graphml" in content
    assert "y:TableNode" in content or "<y:Table" in content


def test_write_yed_graphml_emits_one_row(tmp_path):
    state = _state_with_one_row()
    out = tmp_path / "onerow.graphml"
    write_yed_graphml(state, out)
    content = out.read_text(encoding="utf-8")
    assert 'id="row_p1_a"' in content


def test_write_yed_graphml_no_tmp_left(tmp_path):
    state = _empty_state()
    out = tmp_path / "x.graphml"
    write_yed_graphml(state, out)
    assert list(tmp_path.glob("*.tmp")) == []


def test_write_yed_graphml_creates_parent_dir(tmp_path):
    state = _empty_state()
    out = tmp_path / "nested" / "deep" / "out.graphml"
    write_yed_graphml(state, out)
    assert out.exists()


def test_write_yed_graphml_raises_on_write_error(tmp_path):
    from pyarchinit_mini.harris_swimlane.exceptions import YEDWriterError
    state = _empty_state()
    # /dev/null/foo is not a valid path on POSIX
    bad = Path("/dev/null/cannot_write_here.graphml")
    with pytest.raises(YEDWriterError):
        write_yed_graphml(state, bad)
```

- [ ] **Step 2: Run, verify ImportError**

The test imports `EditorState` from `swimlane_state` — which doesn't exist yet. Add a stub first to enable the tests to fail at the YED writer level:

Create `pyarchinit_mini/harris_swimlane/swimlane_state.py` (stub — full impl in Task 8):

```python
# pyarchinit_mini/harris_swimlane/swimlane_state.py
"""SwimlaneState — Cytoscape JSON ↔ DB serialization (full impl in Task 8)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .row_provider import Row


@dataclass
class CytoscapeElement:
    data: dict
    classes: str = ""
    position: Optional[dict] = None


@dataclass
class EditorState:
    site: str
    rows: list
    nodes: list
    edges: list
    pending_changes: dict


@dataclass
class SaveResult:
    updated: int
    inserted: int
    deleted: int
    errors: tuple
```

- [ ] **Step 3: Implement minimal yed_writer**

```python
# pyarchinit_mini/graphml_io/yed_writer.py
"""yEd-flavored GraphML writer — emits y:TableNode + y:Rows + per-node y:ShapeNode.

Separate from s3dgraphy.exporter.graphml (Spec 2). Used by Harris Swimlane
Editor for on-demand export to data/exports/harris_yed/<slug>-harris-yed.graphml.

Visual styles per US node come from VocabProvider.get_visual_style(unit_type)
(Spec 1 contract). PERIOD_COLORS palette for row backgrounds comes from
Row.color (assigned by RowProvider).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from pyarchinit_mini.harris_swimlane.exceptions import YEDWriterError


# yEd XML namespaces
NS = {
    "graphml": "http://graphml.graphdrawing.org/xmlns",
    "y": "http://www.yworks.com/xml/graphml",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


def write_yed_graphml(state: Any, path: Path) -> None:
    """Emit yEd-flavored GraphML to path. Atomic write via tmp + os.replace."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        xml = _build_xml(state)
        tmp.write_text(xml, encoding="utf-8")
        tmp.replace(path)
    except Exception as e:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass
        raise YEDWriterError(path=str(path), msg=str(e)) from e


def _build_xml(state) -> str:
    """Build the yEd-flavored GraphML XML string."""
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns" '
        'xmlns:y="http://www.yworks.com/xml/graphml" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns '
        'http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">',
        '  <key for="node" id="d6" yfiles.type="nodegraphics"/>',
        '  <key for="edge" id="d10" yfiles.type="edgegraphics"/>',
        '  <graph id="G" edgedefault="directed">',
        _build_swimlane_root(state),
        _build_edges(state),
        '  </graph>',
        '</graphml>',
    ]
    return "\n".join(parts)


def _build_swimlane_root(state) -> str:
    """Build the root group node containing the TableNode with rows."""
    row_xml = _build_table_rows(state.rows)
    nodes_xml = _build_us_nodes(state.nodes)
    return (
        '    <node id="swimlane_root" yfiles.foldertype="group">\n'
        '      <data key="d6">\n'
        '        <y:TableNode>\n'
        '          <y:Geometry height="800" width="2000" x="0" y="0"/>\n'
        '          <y:Fill color="#FAFAFA" transparent="false"/>\n'
        '          <y:BorderStyle color="#000000" type="line" width="1.0"/>\n'
        '          <y:Table>\n'
        f'{row_xml}'
        '            <y:Columns>\n'
        '              <y:Column id="col_main" width="1900.0"/>\n'
        '            </y:Columns>\n'
        '          </y:Table>\n'
        '        </y:TableNode>\n'
        '      </data>\n'
        '      <graph id="swimlane_root:" edgedefault="directed">\n'
        f'{nodes_xml}'
        '      </graph>\n'
        '    </node>\n'
    )


def _build_table_rows(rows) -> str:
    if not rows:
        return '            <y:Rows/>\n'
    lines = ['            <y:Rows>']
    for r in rows:
        lines.append(
            f'              <y:Row id="{r.row_id}" height="80.0" minimumHeight="40.0"/>'
        )
    lines.append('            </y:Rows>\n')
    return "\n".join(lines)


def _build_us_nodes(nodes) -> str:
    """Stub for Task 7 — actual node shape emission. Returns empty for now."""
    return ""


def _build_edges(state) -> str:
    """Stub for Task 7 — edge emission. Returns empty for now."""
    return ""
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_yed_writer.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/harris_swimlane/swimlane_state.py pyarchinit_mini/graphml_io/yed_writer.py tests/unit/test_yed_writer.py
git commit -m "feat(graphml_io): yed_writer minimal (TableNode + Rows skeleton)"
```

---

### Task 7: yed_writer node/edge emission + VocabProvider styling

**Files:**
- Modify: `pyarchinit_mini/graphml_io/yed_writer.py` (extend `_build_us_nodes` + `_build_edges`)
- Test: `tests/unit/test_yed_writer.py` (extend with node/edge tests)

- [ ] **Step 1: Append failing tests**

```python
# tests/unit/test_yed_writer.py — append

from pathlib import Path
from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.harris_swimlane.swimlane_state import CytoscapeElement

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX_VOCAB)
    yield
    VocabProvider.reset()


def _state_with_us():
    row = Row(row_id="row_p1_a", period_name="P1", phase_name="a",
              start_date=100, end_date=200, color="#FF0000", source="period_table")
    nodes = [
        CytoscapeElement(data={"id": "us_1", "label": "US1", "unit_type": "US",
                                "parent": "row_p1_a"}),
        CytoscapeElement(data={"id": "us_2", "label": "USVs2", "unit_type": "USVs",
                                "parent": "row_p1_a"}),
    ]
    edges = [
        CytoscapeElement(data={"id": "e1", "source": "us_1", "target": "us_2",
                                "label": "overlies"}),
    ]
    return EditorState(site="T", rows=[row], nodes=nodes, edges=edges,
                       pending_changes={})


def test_write_yed_graphml_emits_us_nodes(tmp_path):
    state = _state_with_us()
    out = tmp_path / "n.graphml"
    write_yed_graphml(state, out)
    content = out.read_text(encoding="utf-8")
    assert 'id="us_1"' in content
    assert 'id="us_2"' in content
    assert "y:ShapeNode" in content


def test_write_yed_graphml_uses_vocabprovider_styles(tmp_path):
    state = _state_with_us()
    out = tmp_path / "n.graphml"
    write_yed_graphml(state, out)
    content = out.read_text(encoding="utf-8")
    # US visual style from VocabProvider should be reflected as fill color
    # US fill = #F0F0F0; USVs different shape (parallelogram)
    assert 'color="#F0F0F0"' in content or 'color="#f0f0f0"' in content
    assert 'parallelogram' in content.lower()


def test_write_yed_graphml_emits_edges(tmp_path):
    state = _state_with_us()
    out = tmp_path / "e.graphml"
    write_yed_graphml(state, out)
    content = out.read_text(encoding="utf-8")
    assert 'source="us_1"' in content
    assert 'target="us_2"' in content
    assert "overlies" in content
```

- [ ] **Step 2: Run, verify failure**

- [ ] **Step 3: Implement node/edge emission**

Replace the stub `_build_us_nodes` and `_build_edges` in `yed_writer.py`:

```python
def _build_us_nodes(nodes) -> str:
    """Emit y:ShapeNode per US with VocabProvider visual styles."""
    if not nodes:
        return ""
    from pyarchinit_mini.vocab.provider import VocabProvider
    from pyarchinit_mini.vocab.types import VisualStyle
    try:
        provider = VocabProvider.instance()
    except Exception:
        provider = None

    lines = []
    for el in nodes:
        nid = el.data.get("id", "")
        label = el.data.get("label", nid)
        unit_type = el.data.get("unit_type", "US")
        # Lookup visual style
        if provider:
            style = provider.get_visual_style(unit_type)
        else:
            style = VisualStyle.fallback()
        fill = style.fill_color
        border = style.border_color
        shape = style.shape
        lines.append(
            f'        <node id="{nid}">\n'
            f'          <data key="d6">\n'
            f'            <y:ShapeNode>\n'
            f'              <y:Geometry x="50" y="20" width="80" height="50"/>\n'
            f'              <y:Fill color="{fill}" transparent="false"/>\n'
            f'              <y:BorderStyle color="{border}" type="line" width="3.0"/>\n'
            f'              <y:NodeLabel fontSize="12">{_xml_escape(label)}</y:NodeLabel>\n'
            f'              <y:Shape type="{shape}"/>\n'
            f'            </y:ShapeNode>\n'
            f'          </data>\n'
            f'        </node>'
        )
    return "\n".join(lines) + "\n"


def _build_edges(state) -> str:
    """Emit y:GenericEdge per stratigraphic edge."""
    if not state.edges:
        return ""
    lines = []
    for el in state.edges:
        eid = el.data.get("id", "")
        src = el.data.get("source", "")
        tgt = el.data.get("target", "")
        lbl = el.data.get("label", "")
        lines.append(
            f'    <edge id="{eid}" source="{src}" target="{tgt}">\n'
            f'      <data key="d10">\n'
            f'        <y:GenericEdge>\n'
            f'          <y:LineStyle color="#000000" type="line" width="1.0"/>\n'
            f'          <y:Arrows source="none" target="standard"/>\n'
            f'          <y:EdgeLabel>{_xml_escape(lbl)}</y:EdgeLabel>\n'
            f'        </y:GenericEdge>\n'
            f'      </data>\n'
            f'    </edge>'
        )
    return "\n".join(lines) + "\n"


def _xml_escape(s: str) -> str:
    """Minimal XML escape for safe content embedding."""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_yed_writer.py -v
```

Expected: 8 passed (5 from Task 6 + 3 new).

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphml_io/yed_writer.py tests/unit/test_yed_writer.py
git commit -m "feat(graphml_io): yed_writer emits y:ShapeNode + y:GenericEdge with VocabProvider styles"
```

---

### Task 8: yed_writer golden parity test

**Files:**
- Create: `tests/fixtures/yed_graphml_outputs/volterra_baseline.graphml`
- Create: `tests/integration/test_yed_writer_parity.py`

- [ ] **Step 1: Generate the golden baseline**

```bash
mkdir -p tests/fixtures/yed_graphml_outputs
cat > /tmp/gen_baseline.py << 'EOF'
"""Generate the golden baseline for yed_writer parity test."""
import sys
from pathlib import Path
sys.path.insert(0, "/Users/enzo/pyarchinit-mini-desk")

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.harris_swimlane.row_provider import Row
from pyarchinit_mini.harris_swimlane.swimlane_state import EditorState, CytoscapeElement
from pyarchinit_mini.graphml_io.yed_writer import write_yed_graphml

VocabProvider.reset()
VocabProvider.instance(json_config_dir=Path("tests/fixtures/s3dgraphy_jsons/0.1.42"))

rows = [
    Row("row_medieval_b", "Medieval", "b", 1200, 1500, "#9642B7", "period_table"),
    Row("row_medieval_a", "Medieval", "a", 600, 1200, "#7204CB", "period_table"),
    Row("row_late-antiquity_a", "Late Antiquity", "a", 300, 600, "#20ADB7", "period_table"),
    Row("row_roman_b", "Roman", "b", 100, 300, "#65C3E4", "period_table"),
    Row("row_roman_a", "Roman", "a", -27, 100, "#FA9639", "period_table"),
]
nodes = [
    CytoscapeElement(data={"id": "us_1", "label": "US1", "unit_type": "US",
                            "parent": "row_roman_a"}),
    CytoscapeElement(data={"id": "us_2", "label": "US2", "unit_type": "US",
                            "parent": "row_roman_b"}),
    CytoscapeElement(data={"id": "us_3", "label": "USVs3", "unit_type": "USVs",
                            "parent": "row_medieval_a"}),
]
edges = [
    CytoscapeElement(data={"id": "e1", "source": "us_2", "target": "us_1",
                            "label": "overlies"}),
]
state = EditorState(site="Volterra", rows=rows, nodes=nodes, edges=edges,
                    pending_changes={})

out = Path("tests/fixtures/yed_graphml_outputs/volterra_baseline.graphml")
out.parent.mkdir(parents=True, exist_ok=True)
write_yed_graphml(state, out)
print(f"Wrote {out}")
EOF
.venv/bin/python /tmp/gen_baseline.py
```

Expected: `Wrote tests/fixtures/yed_graphml_outputs/volterra_baseline.graphml`

- [ ] **Step 2: Inspect the output to confirm it's valid**

```bash
head -20 tests/fixtures/yed_graphml_outputs/volterra_baseline.graphml
.venv/bin/python -c "import xml.etree.ElementTree as ET; ET.parse('tests/fixtures/yed_graphml_outputs/volterra_baseline.graphml'); print('valid XML')"
```

Expected: valid XML output.

- [ ] **Step 3: Write the parity test**

```python
# tests/integration/test_yed_writer_parity.py
"""PR2 gate: yed_writer output must match golden fixture for canonical Volterra state.

Differences allowed: minor coordinate jitter, yfiles version metadata.
Critical contract: TableNode + Rows count + per-node id + style colors stable.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.harris_swimlane.row_provider import Row
from pyarchinit_mini.harris_swimlane.swimlane_state import EditorState, CytoscapeElement
from pyarchinit_mini.graphml_io.yed_writer import write_yed_graphml

FIX = Path(__file__).parent.parent / "fixtures"
GOLDEN = FIX / "yed_graphml_outputs" / "volterra_baseline.graphml"
VOCAB_FIX = FIX / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=VOCAB_FIX)
    yield
    VocabProvider.reset()


def _build_volterra_state():
    rows = [
        Row("row_medieval_b", "Medieval", "b", 1200, 1500, "#9642B7", "period_table"),
        Row("row_medieval_a", "Medieval", "a", 600, 1200, "#7204CB", "period_table"),
        Row("row_late-antiquity_a", "Late Antiquity", "a", 300, 600, "#20ADB7", "period_table"),
        Row("row_roman_b", "Roman", "b", 100, 300, "#65C3E4", "period_table"),
        Row("row_roman_a", "Roman", "a", -27, 100, "#FA9639", "period_table"),
    ]
    nodes = [
        CytoscapeElement(data={"id": "us_1", "label": "US1", "unit_type": "US",
                                "parent": "row_roman_a"}),
        CytoscapeElement(data={"id": "us_2", "label": "US2", "unit_type": "US",
                                "parent": "row_roman_b"}),
        CytoscapeElement(data={"id": "us_3", "label": "USVs3", "unit_type": "USVs",
                                "parent": "row_medieval_a"}),
    ]
    edges = [
        CytoscapeElement(data={"id": "e1", "source": "us_2", "target": "us_1",
                                "label": "overlies"}),
    ]
    return EditorState(site="Volterra", rows=rows, nodes=nodes, edges=edges,
                       pending_changes={})


def test_yed_writer_output_matches_golden(tmp_path):
    state = _build_volterra_state()
    out = tmp_path / "v.graphml"
    write_yed_graphml(state, out)

    actual = out.read_text(encoding="utf-8")
    golden = GOLDEN.read_text(encoding="utf-8")

    assert actual == golden, (
        "yed_writer output diverged from golden. "
        "If intentional, regenerate via /tmp/gen_baseline.py"
    )


def test_yed_writer_row_count_matches_golden():
    """Independent check: row count in golden file matches what we'd emit."""
    tree = ET.parse(GOLDEN)
    rows = tree.findall(".//{http://www.yworks.com/xml/graphml}Row")
    assert len(rows) == 5  # Volterra has 5 (period, phase) rows


def test_yed_writer_node_count_matches_golden():
    tree = ET.parse(GOLDEN)
    # Count nodes excluding the swimlane_root group
    ns = {"g": "http://graphml.graphdrawing.org/xmlns"}
    nodes = tree.findall(".//g:graph[@id='swimlane_root:']/g:node", ns)
    assert len(nodes) == 3  # us_1, us_2, us_3
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/integration/test_yed_writer_parity.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/yed_graphml_outputs/volterra_baseline.graphml tests/integration/test_yed_writer_parity.py
git commit -m "test(yed_writer): add golden fixture + parity gate (PR2)"
```

---

## PR3 — load endpoint

### Task 9: SwimlaneState.load — full implementation

**Files:**
- Modify: `pyarchinit_mini/harris_swimlane/swimlane_state.py` (replace stub with full impl)
- Test: `tests/unit/test_harris_swimlane_state_load.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_harris_swimlane_state_load.py
import sqlite3
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"
DB_FIX = Path(__file__).parent.parent / "fixtures" / "databases" / "sqlite_volterra_30us_with_periods.db"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX_VOCAB)
    yield
    VocabProvider.reset()


@pytest.fixture
def session():
    eng = create_engine(f"sqlite:///{DB_FIX}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def test_load_returns_editor_state_with_rows(session):
    state = SwimlaneState.load(session, "Volterra")
    assert state.site == "Volterra"
    assert len(state.rows) == 5  # 5 (period, phase) pairs in fixture


def test_load_returns_30_us_nodes(session):
    state = SwimlaneState.load(session, "Volterra")
    assert len(state.nodes) == 30


def test_load_assigns_parent_row_to_each_node(session):
    state = SwimlaneState.load(session, "Volterra")
    for el in state.nodes:
        assert "parent" in el.data
        assert el.data["parent"].startswith("row_") or el.data["parent"] == "_unassigned"


def test_load_creates_edges_from_rapporti(session):
    state = SwimlaneState.load(session, "Volterra")
    # Fixture has rapporti like "copre 1001" every 3rd US — 10 edges expected
    assert len(state.edges) >= 5  # at least some edges


def test_load_empty_site_returns_empty_state(session):
    state = SwimlaneState.load(session, "NoSuchSite")
    assert state.rows == [] or len(state.rows) == 0
    assert state.nodes == []
    assert state.edges == []
```

- [ ] **Step 2: Run, verify failure (stub doesn't implement load)**

- [ ] **Step 3: Replace the swimlane_state.py stub with full implementation**

```python
# pyarchinit_mini/harris_swimlane/swimlane_state.py
"""SwimlaneState — Cytoscape JSON ↔ DB serialization.

Load: row_provider + us_table → EditorState (Cytoscape-shaped).
Save: pending_changes → DB UPDATE/INSERT/DELETE in single transaction.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from .row_provider import Row, RowProvider
from .compound_layout import derive_row_id, initial_node_position
from .exceptions import SwimlaneStateError


@dataclass
class CytoscapeElement:
    data: dict
    classes: str = ""
    position: Optional[dict] = None


@dataclass
class EditorState:
    site: str
    rows: list[Row]
    nodes: list[CytoscapeElement]
    edges: list[CytoscapeElement]
    pending_changes: dict


@dataclass
class SaveResult:
    updated: int
    inserted: int
    deleted: int
    errors: tuple


class SwimlaneState:
    @staticmethod
    def load(session: Session, site: str) -> EditorState:
        """Load editor state for site. Empty state if site has no data."""
        provider = RowProvider(session, site)
        rows = provider.list_rows()

        # Load US records for site
        us_rows = session.execute(text(
            "SELECT id_us, sito, area, us, unita_tipo, rapporti, node_uuid, "
            "periodo_iniziale, fase_iniziale "
            "FROM us_table WHERE sito = :sito ORDER BY id_us"
        ), {"sito": site}).fetchall()

        nodes: list[CytoscapeElement] = []
        us_to_node_id: dict[int, str] = {}
        # Track count per row for initial positioning
        row_counts: dict[str, int] = {}

        for r in us_rows:
            id_us = r[0]
            us_num = r[3]
            unita_tipo = r[4] or "US"
            periodo = r[7]
            fase = r[8]
            parent_row_id = derive_row_id(periodo, fase)

            node_id = f"us_{id_us}"
            us_to_node_id[us_num] = node_id

            idx = row_counts.get(parent_row_id, 0)
            row_counts[parent_row_id] = idx + 1

            # Build Row-like object for initial_node_position
            class _RowLike:
                row_id = parent_row_id
            pos = initial_node_position(_RowLike(), idx)

            nodes.append(CytoscapeElement(
                data={
                    "id": node_id,
                    "label": f"{unita_tipo}{us_num}",
                    "parent": parent_row_id,
                    "unit_type": unita_tipo,
                    "period": periodo,
                    "phase": fase,
                    "us": us_num,
                    "node_uuid": r[6],
                },
                position=pos,
            ))

        # Add row nodes (compound parents) as Cytoscape elements
        for row in rows:
            nodes.append(CytoscapeElement(
                data={
                    "id": row.row_id,
                    "label": _row_label(row),
                    "is_swimlane": True,
                    "color": row.color,
                    "period_name": row.period_name,
                    "phase_name": row.phase_name,
                },
                classes="swimlane",
            ))

        # Edges from rapporti via EdgeRegistry
        edges = SwimlaneState._build_edges(us_rows, us_to_node_id)

        return EditorState(
            site=site,
            rows=rows,
            nodes=nodes,
            edges=edges,
            pending_changes={"us_updates": [], "us_inserts": [], "us_deletes": []},
        )

    @staticmethod
    def _build_edges(us_rows, us_to_node_id) -> list[CytoscapeElement]:
        """Parse rapporti for each US and build edges via EdgeRegistry."""
        try:
            from pyarchinit_mini.graphproj.edge_registry import EdgeRegistry
            registry = EdgeRegistry()
        except Exception:
            return []

        edges = []
        edge_counter = 0
        for r in us_rows:
            us_num = r[3]
            rapporti = r[5] or ""
            if not rapporti.strip():
                continue
            source_node_id = us_to_node_id.get(us_num)
            if source_node_id is None:
                continue
            for token in rapporti.replace(";", ",").split(","):
                tok = token.strip()
                if not tok:
                    continue
                edge_name, target_us = registry.parse_rapporti_token(tok)
                if edge_name is None or target_us is None:
                    continue
                try:
                    target_int = int(target_us)
                except (ValueError, TypeError):
                    continue
                target_node_id = us_to_node_id.get(target_int)
                if target_node_id is None:
                    continue
                edge_counter += 1
                edges.append(CytoscapeElement(data={
                    "id": f"e{edge_counter}",
                    "source": source_node_id,
                    "target": target_node_id,
                    "label": edge_name,
                }))
        return edges

    @staticmethod
    def save(session: Session, site: str, state: dict) -> SaveResult:
        """Stub for Task 11. Will apply pending_changes."""
        raise NotImplementedError("save() implemented in Task 11")


def _row_label(row: Row) -> str:
    if row.phase_name:
        return f"{row.period_name} / {row.phase_name}"
    return row.period_name
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_harris_swimlane_state_load.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/harris_swimlane/swimlane_state.py tests/unit/test_harris_swimlane_state_load.py
git commit -m "feat(harris_swimlane): SwimlaneState.load with EdgeRegistry-based edges"
```

---

### Task 10: New endpoints `/api/swimlanes/<site>` GET + `/api/load/<site>` GET

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py` (add 2 endpoints + imports)
- Test: `tests/integration/test_harris_swimlane_routes_load.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/integration/test_harris_swimlane_routes_load.py
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"
DB_FIX = Path(__file__).parent.parent / "fixtures" / "databases" / "sqlite_volterra_30us_with_periods.db"


@pytest.fixture
def client():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX_VOCAB)

    from flask import Flask, g
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp

    eng = create_engine(f"sqlite:///{DB_FIX}")
    Session = sessionmaker(bind=eng)

    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.before_request
    def _attach():
        g.db_session = Session()

    @app.teardown_request
    def _detach(exc):
        g.db_session.close()

    app.register_blueprint(harris_creator_bp)

    yield app.test_client()
    VocabProvider.reset()


def test_get_swimlanes_returns_rows_json(client):
    r = client.get("/harris-creator/api/swimlanes/Volterra")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert len(data) == 5
    for row in data:
        assert "row_id" in row
        assert "period_name" in row
        assert "color" in row


def test_get_load_returns_editor_state(client):
    r = client.get("/harris-creator/api/load/Volterra")
    assert r.status_code == 200
    data = r.get_json()
    assert "rows" in data
    assert "nodes" in data
    assert "edges" in data
    assert len(data["rows"]) == 5
    # 30 US + 5 row compound parents = 35 nodes
    assert len(data["nodes"]) == 35


def test_get_load_empty_site(client):
    r = client.get("/harris-creator/api/load/UnknownSite")
    assert r.status_code == 200
    data = r.get_json()
    assert data["nodes"] == []
    assert data["edges"] == []
```

- [ ] **Step 2: Run, verify failures (404 — endpoints don't exist)**

- [ ] **Step 3: Add the 2 endpoints to harris_creator_routes.py**

Append to `pyarchinit_mini/web_interface/harris_creator_routes.py`:

```python
# === Spec 3-bis: Harris Swimlane Editor endpoints ===

from dataclasses import asdict
from flask import g

from pyarchinit_mini.harris_swimlane.row_provider import RowProvider
from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState
from pyarchinit_mini.harris_swimlane.exceptions import SwimlaneError, RowProviderError


def _get_session():
    """Helper: get session from Flask g or fall back to get_db_session()."""
    db = getattr(g, "db_session", None)
    if db is None:
        db = get_db_session()
    return db


@harris_creator_bp.get("/api/swimlanes/<site>")
def api_get_swimlanes(site: str):
    """List swimlane rows for the site. Spec §4.7."""
    try:
        session = _get_session()
        provider = RowProvider(session, site)
        rows = provider.list_rows()
        return jsonify([{
            "row_id": r.row_id,
            "period_name": r.period_name,
            "phase_name": r.phase_name,
            "start_date": r.start_date,
            "end_date": r.end_date,
            "color": r.color,
            "source": r.source,
        } for r in rows]), 200
    except RowProviderError as e:
        return jsonify({"error": "row_provider", "message": str(e)}), 500
    except Exception as e:
        logger.exception("api_get_swimlanes failed")
        return jsonify({"error": "internal", "message": str(e)}), 500


@harris_creator_bp.get("/api/load/<site>")
def api_load_state(site: str):
    """Load full editor state (rows + nodes + edges) as Cytoscape JSON."""
    try:
        session = _get_session()
        state = SwimlaneState.load(session, site)
        return jsonify({
            "site": state.site,
            "rows": [{
                "row_id": r.row_id,
                "period_name": r.period_name,
                "phase_name": r.phase_name,
                "color": r.color,
                "start_date": r.start_date,
                "end_date": r.end_date,
                "source": r.source,
            } for r in state.rows],
            "nodes": [{
                "data": el.data,
                "classes": el.classes,
                "position": el.position,
            } for el in state.nodes],
            "edges": [{
                "data": el.data,
                "classes": el.classes,
            } for el in state.edges],
            "pending_changes": state.pending_changes,
        }), 200
    except SwimlaneError as e:
        return jsonify({"error": "swimlane", "message": str(e)}), 500
    except Exception as e:
        logger.exception("api_load_state failed")
        return jsonify({"error": "internal", "message": str(e)}), 500
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/integration/test_harris_swimlane_routes_load.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/harris_creator_routes.py tests/integration/test_harris_swimlane_routes_load.py
git commit -m "feat(web): /api/swimlanes/<site> + /api/load/<site> GET endpoints"
```

---

## PR4 — save endpoint + auto_regen

### Task 11: SwimlaneState.save + auto_regen invocation

**Files:**
- Modify: `pyarchinit_mini/harris_swimlane/swimlane_state.py` (implement `save`)
- Test: `tests/unit/test_harris_swimlane_state_save.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_harris_swimlane_state_save.py
import sqlite3
from pathlib import Path
from unittest.mock import patch
import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX_VOCAB)
    yield
    VocabProvider.reset()


@pytest.fixture
def session(tmp_path):
    db = tmp_path / "save.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
    CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, area TEXT, us INTEGER, unita_tipo TEXT,
        d_stratigrafica TEXT, d_interpretativa TEXT, rapporti TEXT,
        node_uuid TEXT, periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT
    );
    INSERT INTO us_table (sito, area, us, unita_tipo, node_uuid, periodo_iniziale, fase_iniziale)
    VALUES ('Volterra', 'A', 1001, 'US', 'u-1', 'Roman', 'a');
    INSERT INTO us_table (sito, area, us, unita_tipo, node_uuid, periodo_iniziale, fase_iniziale)
    VALUES ('Volterra', 'A', 1002, 'US', 'u-2', 'Medieval', 'a');
    """)
    conn.commit()
    conn.close()
    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    s = Session()
    yield s
    s.close()


def test_save_updates_us_periodo(session):
    state = {
        "pending_us_updates": [
            {"us": 1001, "periodo_iniziale": "Medieval", "fase_iniziale": "b"},
        ],
        "pending_us_inserts": [],
        "pending_us_deletes": [],
    }
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen"):
        result = SwimlaneState.save(session, "Volterra", state)
    assert result.updated == 1
    row = session.execute(text(
        "SELECT periodo_iniziale, fase_iniziale FROM us_table WHERE us=1001"
    )).fetchone()
    assert row[0] == "Medieval"
    assert row[1] == "b"


def test_save_inserts_new_us(session):
    state = {
        "pending_us_updates": [],
        "pending_us_inserts": [
            {"sito": "Volterra", "area": "A", "us": 1003, "unita_tipo": "US",
             "periodo_iniziale": "Roman", "fase_iniziale": "b"},
        ],
        "pending_us_deletes": [],
    }
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen"):
        result = SwimlaneState.save(session, "Volterra", state)
    assert result.inserted == 1
    count = session.execute(text(
        "SELECT COUNT(*) FROM us_table WHERE us=1003"
    )).scalar()
    assert count == 1


def test_save_deletes_us(session):
    state = {
        "pending_us_updates": [],
        "pending_us_inserts": [],
        "pending_us_deletes": [{"us": 1001}],
    }
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen"):
        result = SwimlaneState.save(session, "Volterra", state)
    assert result.deleted == 1
    count = session.execute(text(
        "SELECT COUNT(*) FROM us_table WHERE us=1001"
    )).scalar()
    assert count == 0


def test_save_triggers_auto_regen(session):
    state = {
        "pending_us_updates": [
            {"us": 1001, "periodo_iniziale": "Medieval", "fase_iniziale": "b"},
        ],
        "pending_us_inserts": [],
        "pending_us_deletes": [],
    }
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen") as mock_regen:
        SwimlaneState.save(session, "Volterra", state)
        mock_regen.assert_called_once_with("Volterra", session=session)


def test_save_empty_pending_returns_zero_counts(session):
    state = {
        "pending_us_updates": [],
        "pending_us_inserts": [],
        "pending_us_deletes": [],
    }
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen"):
        result = SwimlaneState.save(session, "Volterra", state)
    assert result.updated == 0
    assert result.inserted == 0
    assert result.deleted == 0
```

- [ ] **Step 2: Run, verify failure (NotImplementedError)**

- [ ] **Step 3: Replace the save() stub**

In `pyarchinit_mini/harris_swimlane/swimlane_state.py`, replace the stub `save`:

```python
    @staticmethod
    def save(session: Session, site: str, state: dict) -> SaveResult:
        """Apply pending_changes to DB. Transaction-wrapped.

        Body shape:
          {
            "pending_us_updates": [{"us": int, "periodo_iniziale": str, "fase_iniziale": str}, ...],
            "pending_us_inserts": [{"sito", "us", "unita_tipo", "periodo_iniziale", "fase_iniziale", ...}, ...],
            "pending_us_deletes": [{"us": int}, ...],
          }

        After successful commit: triggers Spec 2 auto_regen for stratigraphy.graphml.
        Returns SaveResult; raises SwimlaneStateError on transactional failure.
        """
        updates = state.get("pending_us_updates", [])
        inserts = state.get("pending_us_inserts", [])
        deletes = state.get("pending_us_deletes", [])

        updated = 0
        inserted = 0
        deleted = 0
        errors: list[str] = []

        try:
            for u in updates:
                try:
                    session.execute(text(
                        "UPDATE us_table SET periodo_iniziale=:p, fase_iniziale=:ph "
                        "WHERE us=:us AND sito=:sito"
                    ), {
                        "p": u.get("periodo_iniziale"),
                        "ph": u.get("fase_iniziale"),
                        "us": u["us"],
                        "sito": site,
                    })
                    updated += 1
                except Exception as e:
                    errors.append(f"update us={u.get('us')}: {e}")

            for ins in inserts:
                try:
                    # generate node_uuid via uuid7 if missing (Spec 1 helper)
                    node_uuid = ins.get("node_uuid")
                    if not node_uuid:
                        try:
                            from pyarchinit_mini.database.utils import generate_node_uuid
                            node_uuid = generate_node_uuid()
                        except Exception:
                            node_uuid = None
                    session.execute(text(
                        "INSERT INTO us_table (sito, area, us, unita_tipo, "
                        "periodo_iniziale, fase_iniziale, node_uuid) "
                        "VALUES (:sito, :area, :us, :ut, :p, :ph, :uuid)"
                    ), {
                        "sito": ins.get("sito", site),
                        "area": ins.get("area"),
                        "us": ins["us"],
                        "ut": ins.get("unita_tipo", "US"),
                        "p": ins.get("periodo_iniziale"),
                        "ph": ins.get("fase_iniziale"),
                        "uuid": node_uuid,
                    })
                    inserted += 1
                except Exception as e:
                    errors.append(f"insert us={ins.get('us')}: {e}")

            for d in deletes:
                try:
                    session.execute(text(
                        "DELETE FROM us_table WHERE us=:us AND sito=:sito"
                    ), {"us": d["us"], "sito": site})
                    deleted += 1
                except Exception as e:
                    errors.append(f"delete us={d.get('us')}: {e}")

            if errors:
                session.rollback()
                updated = inserted = deleted = 0
            else:
                session.commit()
                # Spec 2 auto-regen
                try:
                    from pyarchinit_mini.graphproj.auto_regen import _trigger_graph_regen
                    _trigger_graph_regen(site, session=session)
                except Exception:
                    # auto_regen swallows its own errors; this is belt+suspenders
                    pass
        except Exception as e:
            session.rollback()
            raise SwimlaneStateError(f"save failed: {e}", op="save") from e

        return SaveResult(
            updated=updated,
            inserted=inserted,
            deleted=deleted,
            errors=tuple(errors),
        )
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_harris_swimlane_state_save.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/harris_swimlane/swimlane_state.py tests/unit/test_harris_swimlane_state_save.py
git commit -m "feat(harris_swimlane): SwimlaneState.save with auto_regen integration"
```

---

### Task 12: POST `/api/save/<site>` endpoint

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py` (add save endpoint)
- Test: `tests/integration/test_harris_swimlane_routes_save.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/integration/test_harris_swimlane_routes_save.py
from pathlib import Path
import sqlite3
import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def client_and_db(tmp_path):
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX_VOCAB)

    db = tmp_path / "save_route.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
    CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, area TEXT, us INTEGER, unita_tipo TEXT,
        d_stratigrafica TEXT, d_interpretativa TEXT, rapporti TEXT,
        node_uuid TEXT, periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT
    );
    INSERT INTO us_table (sito, us, unita_tipo, node_uuid, periodo_iniziale, fase_iniziale)
    VALUES ('Volterra', 1001, 'US', 'u-1', 'Roman', 'a');
    """)
    conn.commit()
    conn.close()

    from flask import Flask, g
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp

    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)

    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.before_request
    def _attach():
        g.db_session = Session()

    @app.teardown_request
    def _detach(exc):
        g.db_session.close()

    app.register_blueprint(harris_creator_bp)

    yield app.test_client(), db
    VocabProvider.reset()


def test_post_save_updates_us(client_and_db, monkeypatch):
    cli, db = client_and_db
    # Don't actually trigger auto_regen
    from unittest.mock import patch
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen"):
        r = cli.post("/harris-creator/api/save/Volterra", json={
            "pending_us_updates": [
                {"us": 1001, "periodo_iniziale": "Medieval", "fase_iniziale": "b"},
            ],
            "pending_us_inserts": [],
            "pending_us_deletes": [],
        })
    assert r.status_code == 200
    data = r.get_json()
    assert data["updated"] == 1

    # Verify DB
    conn = sqlite3.connect(db)
    val = conn.execute("SELECT periodo_iniziale FROM us_table WHERE us=1001").fetchone()[0]
    conn.close()
    assert val == "Medieval"


def test_post_save_invalid_body_returns_400(client_and_db):
    cli, _ = client_and_db
    r = cli.post("/harris-creator/api/save/Volterra", json={})
    # Empty body still works (all keys default to []); returns 200 with zeros
    assert r.status_code == 200
    data = r.get_json()
    assert data["updated"] == 0


def test_post_save_handles_save_error(client_and_db):
    cli, _ = client_and_db
    from unittest.mock import patch
    with patch("pyarchinit_mini.graphproj.auto_regen._trigger_graph_regen"):
        # Insert duplicate us — should produce errors[]
        r = cli.post("/harris-creator/api/save/Volterra", json={
            "pending_us_inserts": [
                {"sito": "Volterra", "us": 1001, "unita_tipo": "US"},  # duplicate
            ],
        })
    # Either 200 with errors[] or 500; both acceptable
    assert r.status_code in (200, 500)
```

- [ ] **Step 2: Run, verify failure (endpoint 404)**

- [ ] **Step 3: Add endpoint to harris_creator_routes.py**

Append to `harris_creator_routes.py`:

```python
@harris_creator_bp.post("/api/save/<site>")
def api_save_state(site: str):
    """Save pending_changes for site. Triggers Spec 2 auto_regen on success."""
    try:
        payload = request.get_json(silent=True) or {}
        session = _get_session()
        result = SwimlaneState.save(session, site, payload)
        return jsonify({
            "updated": result.updated,
            "inserted": result.inserted,
            "deleted": result.deleted,
            "errors": list(result.errors),
        }), 200
    except SwimlaneError as e:
        return jsonify({"error": "swimlane", "message": str(e)}), 500
    except Exception as e:
        logger.exception("api_save_state failed")
        return jsonify({"error": "internal", "message": str(e)}), 500
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/integration/test_harris_swimlane_routes_save.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/harris_creator_routes.py tests/integration/test_harris_swimlane_routes_save.py
git commit -m "feat(web): POST /api/save/<site> endpoint with auto_regen integration"
```

---

## PR5 — row creation endpoint

### Task 13: POST `/api/swimlanes/<site>` (create row)

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py`
- Test: `tests/integration/test_harris_swimlane_routes_create_row.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/integration/test_harris_swimlane_routes_create_row.py
import sqlite3
import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def client_and_db(tmp_path):
    db = tmp_path / "rc.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
    CREATE TABLE period_table (
        id_period INTEGER PRIMARY KEY AUTOINCREMENT,
        period_name TEXT NOT NULL, phase_name TEXT,
        start_date INTEGER, end_date INTEGER,
        description TEXT, chronology TEXT
    );
    """)
    conn.commit()
    conn.close()

    from flask import Flask, g
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp

    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.before_request
    def _attach():
        g.db_session = Session()

    @app.teardown_request
    def _detach(exc):
        g.db_session.close()

    app.register_blueprint(harris_creator_bp)
    yield app.test_client(), db


def test_post_create_row(client_and_db):
    cli, db = client_and_db
    r = cli.post("/harris-creator/api/swimlanes/Volterra", json={
        "period_name": "Period 1",
        "phase_name": "a",
        "start_date": 100,
        "end_date": 200,
    })
    assert r.status_code == 201
    data = r.get_json()
    assert data["period_name"] == "Period 1"
    assert data["row_id"] == "row_period-1_a"

    # period_table updated
    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM period_table").fetchone()[0]
    conn.close()
    assert count == 1


def test_post_create_row_idempotent(client_and_db):
    cli, db = client_and_db
    cli.post("/harris-creator/api/swimlanes/Volterra", json={
        "period_name": "P1", "phase_name": "a",
    })
    r = cli.post("/harris-creator/api/swimlanes/Volterra", json={
        "period_name": "P1", "phase_name": "a",
    })
    # Either 201 or 200 acceptable for idempotent re-creation
    assert r.status_code in (200, 201)

    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM period_table").fetchone()[0]
    conn.close()
    assert count == 1


def test_post_create_row_empty_name_returns_400(client_and_db):
    cli, _ = client_and_db
    r = cli.post("/harris-creator/api/swimlanes/Volterra", json={
        "period_name": "",
    })
    assert r.status_code == 400


def test_post_create_row_invalid_dates_returns_400(client_and_db):
    cli, _ = client_and_db
    r = cli.post("/harris-creator/api/swimlanes/Volterra", json={
        "period_name": "P1", "start_date": 200, "end_date": 100,
    })
    assert r.status_code == 400
```

- [ ] **Step 2: Run, verify failures**

- [ ] **Step 3: Add endpoint**

Append to `harris_creator_routes.py`:

```python
from pyarchinit_mini.harris_swimlane.period_sync_service import PeriodSyncService
from pyarchinit_mini.harris_swimlane.exceptions import PeriodSyncError


@harris_creator_bp.post("/api/swimlanes/<site>")
def api_create_row(site: str):
    """Create a new swimlane row (upsert period_table). site param is for
    URL consistency; period_table is currently cross-site (Spec note)."""
    payload = request.get_json(silent=True) or {}
    period_name = payload.get("period_name", "")
    phase_name = payload.get("phase_name") or None
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")
    try:
        session = _get_session()
        svc = PeriodSyncService(session)
        row = svc.upsert_row(
            period_name=period_name, phase_name=phase_name,
            start_date=start_date, end_date=end_date,
        )
        return jsonify({
            "row_id": row.row_id,
            "period_name": row.period_name,
            "phase_name": row.phase_name,
            "start_date": row.start_date,
            "end_date": row.end_date,
            "color": row.color,
            "source": row.source,
        }), 201
    except PeriodSyncError as e:
        return jsonify({
            "error": "validation",
            "message": str(e),
            "period_name": e.period_name,
            "phase_name": e.phase_name,
        }), 400
    except Exception as e:
        logger.exception("api_create_row failed")
        return jsonify({"error": "internal", "message": str(e)}), 500
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/integration/test_harris_swimlane_routes_create_row.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/harris_creator_routes.py tests/integration/test_harris_swimlane_routes_create_row.py
git commit -m "feat(web): POST /api/swimlanes/<site> creates row + period_table upsert"
```

---

## PR6 — editor.html frontend

### Task 14: editor.html Cytoscape compound config + swimlane rendering

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/harris_creator/editor.html`

This task adds JS code to the existing editor.html template to:
1. Fetch `/api/load/<site>` and render rows as compound parents
2. Style swimlane parents with their row color
3. Render US nodes as compound children

- [ ] **Step 1: Inspect current editor.html structure**

```bash
grep -nE "cy = cytoscape|cy.add|var cy|let cy|const cy|swimlane|loadGraph" pyarchinit_mini/web_interface/templates/harris_creator/editor.html | head -20
```

Note the existing JS structure: variable name (`cy`), where it's initialized, where elements are added.

- [ ] **Step 2: Add the swimlane-loading JS function**

In `editor.html`, near the bottom inside the `<script>` block (after `cy` is initialized), insert:

```html
<script>
// === Spec 3-bis: Harris Swimlane integration ===

async function loadSwimlaneState(site) {
    const r = await fetch(`/harris-creator/api/load/${encodeURIComponent(site)}`);
    if (!r.ok) {
        console.error("Failed to load swimlane state:", await r.text());
        return;
    }
    const state = await r.json();
    renderSwimlaneState(state);
}

function renderSwimlaneState(state) {
    // Clear current
    cy.elements().remove();

    // Add swimlane parent nodes
    const swimlaneNodes = state.nodes.filter(el => el.data.is_swimlane);
    const usNodes = state.nodes.filter(el => !el.data.is_swimlane);

    // Compound parents first
    cy.add(swimlaneNodes.map(el => ({
        group: 'nodes',
        data: el.data,
        classes: 'swimlane',
    })));

    // US children with parent
    cy.add(usNodes.map(el => ({
        group: 'nodes',
        data: el.data,
        position: el.position,
    })));

    // Edges
    cy.add(state.edges.map(el => ({
        group: 'edges',
        data: el.data,
    })));

    // Style swimlanes with their color
    cy.nodes('.swimlane').forEach(n => {
        const color = n.data('color') || '#EEEEEE';
        n.style({
            'background-color': color,
            'background-opacity': 0.2,
            'border-color': color,
            'border-width': 2,
            'label': n.data('label'),
            'text-valign': 'top',
            'text-halign': 'left',
            'padding': 10,
        });
    });

    // Store site for later save
    window._currentSite = state.site;
    window._pendingChanges = {us_updates: [], us_inserts: [], us_deletes: []};
}

// Auto-load on page ready if site is in URL
window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const site = params.get('site');
    if (site && typeof cy !== 'undefined') {
        loadSwimlaneState(site);
    }
});
</script>
```

If the existing editor.html structure has a different `cy` initialization pattern, adapt the placement. The key contract: `cy` must be defined before `renderSwimlaneState` runs.

- [ ] **Step 3: Smoke test via manual browser load (optional)**

For automated test, we just need to verify the template renders without HTML errors:

```bash
.venv/bin/python -c "
from flask import Flask
app = Flask(__name__,
    template_folder='pyarchinit_mini/web_interface/templates')
with app.test_request_context():
    from flask import render_template
    try:
        html = render_template('harris_creator/editor.html')
        assert 'loadSwimlaneState' in html
        print('template renders OK with swimlane JS')
    except Exception as e:
        print(f'template error: {e}')
"
```

Expected: `template renders OK with swimlane JS`

- [ ] **Step 4: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/harris_creator/editor.html
git commit -m "feat(harris): editor.html loads swimlane state with compound parents"
```

---

### Task 15: editor.html drag-drop handlers + pending_changes tracking + "+ New Row" modal + Save button

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/harris_creator/editor.html`

- [ ] **Step 1: Add drag-drop handler + Save button**

In `editor.html`, append to the existing `<script>` block:

```html
<script>
// === Drag-drop: track parent changes as pending_changes ===

function setupSwimlaneDragHandlers() {
    cy.on('dragfree', 'node', function(evt) {
        const node = evt.target;
        if (node.hasClass('swimlane')) return;  // ignore parent drags

        const newParent = node.parent().id();
        const oldParent = node.data('_lastParent') || node.data('parent');

        if (newParent && newParent !== oldParent) {
            const usId = node.data('us');
            const update = {
                us: usId,
                periodo_iniziale: cy.getElementById(newParent).data('period_name'),
                fase_iniziale: cy.getElementById(newParent).data('phase_name'),
            };
            // Replace any existing pending update for this US
            window._pendingChanges.us_updates = window._pendingChanges.us_updates.filter(
                u => u.us !== usId
            );
            window._pendingChanges.us_updates.push(update);
            node.data('_lastParent', newParent);
            showUnsavedIndicator();
        }
    });
}

function showUnsavedIndicator() {
    let ind = document.getElementById('swimlane-unsaved-indicator');
    if (!ind) {
        ind = document.createElement('div');
        ind.id = 'swimlane-unsaved-indicator';
        ind.style.cssText = 'position:fixed;top:10px;right:10px;background:#FFC107;padding:8px 16px;border-radius:4px;z-index:9999;font-weight:bold';
        ind.textContent = '● Unsaved changes';
        document.body.appendChild(ind);
    }
    ind.style.display = 'block';
}

function hideUnsavedIndicator() {
    const ind = document.getElementById('swimlane-unsaved-indicator');
    if (ind) ind.style.display = 'none';
}

// === Save button ===

async function saveSwimlaneState() {
    const site = window._currentSite;
    if (!site) {
        alert('No site loaded');
        return;
    }
    const r = await fetch(`/harris-creator/api/save/${encodeURIComponent(site)}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(window._pendingChanges),
    });
    if (!r.ok) {
        alert(`Save failed: ${await r.text()}`);
        return;
    }
    const result = await r.json();
    alert(`Saved: ${result.updated} updates, ${result.inserted} inserts, ${result.deleted} deletes`);
    if (result.errors && result.errors.length > 0) {
        console.error('Save errors:', result.errors);
    }
    hideUnsavedIndicator();
    window._pendingChanges = {us_updates: [], us_inserts: [], us_deletes: []};
    // Reload to capture side effects
    loadSwimlaneState(site);
}

// === "+ New Row" modal ===

function showNewRowModal() {
    const period = prompt('Period name:');
    if (!period) return;
    const phase = prompt('Phase name (optional):') || null;
    const startStr = prompt('Start date (year, optional):');
    const endStr = prompt('End date (year, optional):');
    const start = startStr ? parseInt(startStr, 10) : null;
    const end = endStr ? parseInt(endStr, 10) : null;

    fetch(`/harris-creator/api/swimlanes/${encodeURIComponent(window._currentSite)}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            period_name: period,
            phase_name: phase,
            start_date: start,
            end_date: end,
        }),
    }).then(r => {
        if (!r.ok) {
            return r.text().then(t => alert(`Create row failed: ${t}`));
        }
        return r.json().then(row => {
            alert(`Created row: ${row.row_id}`);
            loadSwimlaneState(window._currentSite);
        });
    });
}

// Wire up the new buttons (assuming buttons added to HTML toolbar)
window.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {  // wait for cy init
        if (typeof cy !== 'undefined') {
            setupSwimlaneDragHandlers();
        }
    }, 500);
});
</script>
```

- [ ] **Step 2: Add toolbar buttons to the HTML**

Find the existing toolbar area in `editor.html` (look for a `<div class="btn-toolbar">` or similar). Add 3 new buttons:

```html
<!-- Spec 3-bis Harris Swimlane controls -->
<button onclick="showNewRowModal()" class="btn btn-sm btn-primary">+ New Row</button>
<button onclick="saveSwimlaneState()" class="btn btn-sm btn-success">💾 Save</button>
<button onclick="exportYedGraphml()" class="btn btn-sm btn-info">⬇ Export yEd GraphML</button>
```

- [ ] **Step 3: Smoke test template renders**

```bash
.venv/bin/python -c "
from flask import Flask
app = Flask(__name__,
    template_folder='pyarchinit_mini/web_interface/templates')
with app.test_request_context():
    from flask import render_template
    html = render_template('harris_creator/editor.html')
    assert 'saveSwimlaneState' in html
    assert 'showNewRowModal' in html
    assert 'setupSwimlaneDragHandlers' in html
    print('template renders OK with swimlane controls')
"
```

- [ ] **Step 4: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/harris_creator/editor.html
git commit -m "feat(harris): editor.html drag-drop tracking + Save/+New Row modals"
```

---

## PR7 — yEd export endpoint + UI

### Task 16: GET `/api/export/<site>/yed-graphml` endpoint

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py`
- Test: `tests/integration/test_yed_export_route.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/integration/test_yed_export_route.py
import sqlite3
import json
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.vocab.provider import VocabProvider

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"
DB_FIX = Path(__file__).parent.parent / "fixtures" / "databases" / "sqlite_volterra_30us_with_periods.db"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX_VOCAB)

    # Copy fixture DB
    import shutil
    db = tmp_path / "app.db"
    shutil.copy(DB_FIX, db)

    from flask import Flask, g
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp

    eng = create_engine(f"sqlite:///{db}")
    Session = sessionmaker(bind=eng)

    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.before_request
    def _attach():
        g.db_session = Session()

    @app.teardown_request
    def _detach(exc):
        g.db_session.close()

    app.register_blueprint(harris_creator_bp)
    yield app.test_client(), tmp_path
    VocabProvider.reset()


def test_get_export_returns_graphml_download(client):
    cli, tmp_path = client
    r = cli.get("/harris-creator/api/export/Volterra/yed-graphml")
    assert r.status_code == 200
    assert "xml" in r.headers.get("Content-Type", "").lower()
    body = r.data.decode("utf-8", errors="ignore")
    assert "<graphml" in body
    assert "y:TableNode" in body or "y:Table" in body

    # File should also exist on disk
    out_path = tmp_path / "data" / "exports" / "harris_yed" / "volterra-harris-yed.graphml"
    assert out_path.exists()


def test_get_export_updates_index_json(client):
    cli, tmp_path = client
    cli.get("/harris-creator/api/export/Volterra/yed-graphml")
    idx = tmp_path / "data" / "exports" / "harris_yed" / "_index.json"
    assert idx.exists()
    data = json.loads(idx.read_text())
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["site"] == "Volterra"
```

- [ ] **Step 2: Run, verify failure**

- [ ] **Step 3: Add export endpoint to harris_creator_routes.py**

Append:

```python
from pyarchinit_mini.graphml_io.yed_writer import write_yed_graphml
from pyarchinit_mini.harris_swimlane.exceptions import YEDWriterError
from pyarchinit_mini.graphproj.filesystem import slugify
import json as _json


@harris_creator_bp.get("/api/export/<site>/yed-graphml")
def api_export_yed(site: str):
    """Export current swimlane state as yEd-flavored GraphML. On-demand."""
    try:
        session = _get_session()
        state = SwimlaneState.load(session, site)

        out_dir = Path("data/exports/harris_yed")
        out_dir.mkdir(parents=True, exist_ok=True)
        site_slug = slugify(site)
        out_path = out_dir / f"{site_slug}-harris-yed.graphml"
        write_yed_graphml(state, out_path)

        # Update _index.json
        idx_path = out_dir / "_index.json"
        entries = []
        if idx_path.exists():
            try:
                entries = _json.loads(idx_path.read_text())
            except Exception:
                entries = []
        from datetime import datetime
        entries.append({
            "site": site,
            "site_slug": site_slug,
            "file_path": str(out_path),
            "file_size": out_path.stat().st_size,
            "timestamp": datetime.now().isoformat(),
        })
        idx_path.write_text(_json.dumps(entries, indent=2))

        return send_file(
            out_path,
            as_attachment=True,
            download_name=f"{site_slug}-harris-yed.graphml",
            mimetype="application/xml",
        )
    except YEDWriterError as e:
        return jsonify({"error": "yed_writer", "message": str(e)}), 500
    except SwimlaneError as e:
        return jsonify({"error": "swimlane", "message": str(e)}), 500
    except Exception as e:
        logger.exception("api_export_yed failed")
        return jsonify({"error": "internal", "message": str(e)}), 500


# Imports needed at top (if not already present):
# from pathlib import Path
# from flask import send_file
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/integration/test_yed_export_route.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Add export button JS to editor.html**

In `editor.html`, append to the swimlane script block:

```html
<script>
function exportYedGraphml() {
    const site = window._currentSite;
    if (!site) {
        alert('No site loaded');
        return;
    }
    // Trigger download
    window.location.href = `/harris-creator/api/export/${encodeURIComponent(site)}/yed-graphml`;
}
</script>
```

The button was already added in Task 15. This step just wires the handler.

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/web_interface/harris_creator_routes.py pyarchinit_mini/web_interface/templates/harris_creator/editor.html tests/integration/test_yed_export_route.py
git commit -m "feat(web): GET /api/export/<site>/yed-graphml + export button"
```

---

## PR8 — Release docs + .gitignore + final verification

### Task 17: .gitignore + version bump + CHANGELOG + README + user docs

**Files:**
- Modify: `.gitignore`
- Modify: `pyarchinit_mini/__init__.py`
- Modify: `pyproject.toml`
- Modify: `CHANGELOG.md`
- Modify: `README.md`
- Create: `docs/HARRIS_SWIMLANE.md`
- Create: `docs/YED_INTEGRATION.md`

- [ ] **Step 1: Update .gitignore**

Append to `.gitignore`:

```
# Spec 3-bis: Harris Swimlane on-demand exports
data/exports/harris_yed/**/*.graphml
data/exports/harris_yed/_index.json
data/exports/harris_yed/*.tmp
```

- [ ] **Step 2: Version bump**

Replace `2.3.0-alpha` → `2.4.0-alpha` in:
- `pyarchinit_mini/__init__.py`
- `pyproject.toml`

Verify:
```bash
.venv/bin/python -c "import pyarchinit_mini; print(pyarchinit_mini.__version__)"
```
Expected: `2.4.0-alpha`

- [ ] **Step 3: Prepend CHANGELOG entry**

```markdown
## [2.4.0-alpha] - 2026-05-18

### Added (IT)
- Modulo `pyarchinit_mini/harris_swimlane/` (5 sub-moduli: row_provider,
  swimlane_state, period_sync_service, compound_layout, exceptions) per
  l'editor swimlane di Harris Matrix.
- `pyarchinit_mini/graphml_io/yed_writer.py` — nuovo emitter
  yEd-flavored con `y:TableNode + y:Rows + y:ShapeNode`, **separato**
  dall'export s3dgraphy clean di Spec 2.
- 5 nuove route REST per il Harris Creator:
  `GET /api/swimlanes/<site>`, `POST /api/swimlanes/<site>`,
  `GET /api/load/<site>`, `POST /api/save/<site>`,
  `GET /api/export/<site>/yed-graphml`.
- Editor `/harris-creator/editor` ora carica swimlane automaticamente
  per sito esistente (row da `period_table` priorità → fallback
  distinct values), supporta drag-drop tra row, creazione interattiva
  di nuove row, save esplicito con auto-regen (Spec 2) post-commit.
- Export yEd GraphML on-demand → `data/exports/harris_yed/<slug>-harris-yed.graphml`.

### Added (EN)
- New `pyarchinit_mini/harris_swimlane/` package — backend for
  Harris-matrix swimlane editing.
- New `pyarchinit_mini/graphml_io/yed_writer.py` — yEd-flavored
  GraphML emitter (TableNode + Rows + ShapeNode), separate from the
  s3dgraphy clean export of Spec 2.
- 5 new REST endpoints under `/harris-creator/api/`.
- Editor loads swimlanes auto from `period_table` (fallback distinct);
  supports drag-drop, interactive row creation, explicit Save with
  Spec 2 auto-regen integration. On-demand yEd export.

### Changed
- `harris_creator_routes.py` extended (additive — existing routes
  unaffected).
- `editor.html` extended (additive — Cytoscape compound nodes,
  swimlane parents, new toolbar buttons).

### Architecture note
Two GraphML outputs now coexist:
- `data/paradata/<slug>/stratigraphy.graphml` (Spec 2 auto-regen,
  s3dgraphy clean, EM-canonical) — for the EM Datacenter
- `data/exports/harris_yed/<slug>-harris-yed.graphml` (Spec 3-bis,
  on-demand, yEd-flavored with TableNode) — for users editing in yEd Desktop

Legacy `pure_networkx_exporter` stays deprecated (was deprecated in
Spec 2 PR8); NOT resurrected.

### Dependencies
- No new dependencies.

### Spec / Plan
- Spec: `docs/superpowers/specs/2026-05-18-harris-swimlane-template-design.md`
- Plan: `docs/superpowers/plans/2026-05-18-harris-swimlane-template.md`
- Spec 3-bis (auxiliary): independent of Spec 3 (SyncEngine + EM
  Datacenter, on hold pending Datacenter readiness).
```

- [ ] **Step 4: Append README section**

```markdown

## Harris Swimlane Editor

Since 2.4.0-alpha, the Harris Matrix Creator at `/harris-creator/editor`
displays stratigraphic graphs with **yEd-like swimlanes** — horizontal
rows representing periods+phases. Existing US records are auto-placed
in their row based on `periodo_iniziale + fase_iniziale`. Users can
drag US records between rows, create new rows interactively, and save
back to the DB.

Row source priority:
1. `period_table` (formal definitions)
2. Fallback: distinct `(periodo_iniziale, fase_iniziale)` from
   `periodizzazione_table` + `us_table`

### Two GraphML outputs

- `data/paradata/<site>/stratigraphy.graphml` (Spec 2, auto-regen):
  s3dgraphy clean, EM-canonical, for the EM Datacenter
- `data/exports/harris_yed/<site>-harris-yed.graphml` (Spec 3-bis,
  on-demand): yEd-flavored with `y:TableNode`, for users editing in
  yEd Desktop

### Auto-regen integration

Save endpoint also triggers Spec 2's auto_regen for
`stratigraphy.graphml`, keeping the canonical output consistent with
DB state.

See `docs/HARRIS_SWIMLANE.md` and `docs/YED_INTEGRATION.md`.
```

- [ ] **Step 5: Create `docs/HARRIS_SWIMLANE.md`**

```markdown
# Harris Swimlane Editor — User Guide

The Harris Matrix Creator's swimlane editor lets you view and edit
stratigraphic graphs with horizontal rows representing temporal
periods+phases.

## Opening the editor

Navigate to `/harris-creator/editor?site=<SITE_NAME>`. The editor
auto-loads:
- **Rows** (swimlanes) from `period_table` for your site; if empty,
  derived from distinct `periodo_iniziale + fase_iniziale` values in
  `periodizzazione_table` + `us_table`.
- **US records** placed in their respective row (auto-layout).
- **Edges** from `rapporti` strings (parsed via canonical edge names
  like `overlies`, `is_after`, `cuts`).

## Drag-drop a US to a different row

Just drag the US node from one row to another. The change is tracked
client-side — the "● Unsaved changes" indicator appears in the top right.
**No DB write happens until you click Save.**

## Create a new row

Click "**+ New Row**". You'll be prompted for:
- **Period name** (required, e.g. "Period 4")
- **Phase name** (optional, e.g. "a")
- **Start date** (optional, year — negative for BCE)
- **End date** (optional)

The row is added to `period_table` immediately (idempotent — if the
combination already exists, the existing row is reused). It appears at
the top of the editor (most-recent placement).

## Save changes

Click "**💾 Save**" to commit all pending changes to the DB:
- US updates (row reassignments)
- US inserts (new records)
- US deletes

After a successful save, Spec 2's auto-regen also fires, refreshing
`data/paradata/<site>/stratigraphy.graphml` for downstream consumers.

## Export yEd GraphML

Click "**⬇ Export yEd GraphML**" to download a yEd-flavored GraphML file:
`<site>-harris-yed.graphml`. Open it in yEd Desktop to edit the layout
with full yEd swimlane support.

The export is on-demand — no auto-regen. Each click rewrites the file.

## Limitations (current scope)

- **Last-writer-wins on concurrent edits**: if two users edit at once,
  the later Save overwrites the earlier. Real-time conflict resolution
  is Spec 4.
- **No round-trip from yEd Desktop back to editor**: you can export,
  edit in yEd, but re-importing yEd-edited GraphML is deferred to
  Spec 3-ter.
- **Period_table is cross-site**: a row created in site A's editor is
  visible in site B's editor too. Per-site isolation is Spec 4 if needed.
- **Multi-period US**: an US with both `periodo_iniziale` and
  `periodo_finale` is placed only in the starting row. Spanning rows
  visually is Spec 4.
```

- [ ] **Step 6: Create `docs/YED_INTEGRATION.md`**

```markdown
# yEd Integration — Round-trip + Limits

The Harris Swimlane Editor produces yEd-flavored GraphML files
(`data/exports/harris_yed/<site>-harris-yed.graphml`) that you can open
directly in [yEd Desktop](https://www.yworks.com/products/yed).

## Structure of the yEd-flavored export

The export uses yEd's `y:TableNode` structure with one `y:Row` per
`(period_name, phase_name)` pair:

```xml
<node id="swimlane_root" yfiles.foldertype="group">
  <data key="d6">
    <y:TableNode>
      <y:Table>
        <y:Rows>
          <y:Row id="row_medieval_b" height="80.0"/>
          <y:Row id="row_medieval_a" height="80.0"/>
          ...
        </y:Rows>
      </y:Table>
    </y:TableNode>
  </data>
  <graph id="swimlane_root:" edgedefault="directed">
    <node id="us_5"> <!-- US lives in the nested graph -->
      <data key="d6"><y:ShapeNode>...</y:ShapeNode></data>
    </node>
    ...
  </graph>
</node>
```

US visual styles (color, shape, border) come from `VocabProvider.get_visual_style(unit_type)`
(Spec 1's canonical source).

## Workflow: edit in yEd Desktop

1. From the editor, click **⬇ Export yEd GraphML**.
2. Open the downloaded file in yEd Desktop.
3. Use yEd's swimlane tools (Layout → Hierarchical → Swimlanes) to
   refine row placement, add edge labels, adjust colors.
4. Save the yEd file separately (do NOT overwrite — round-trip is not
   yet supported).

## Limits

- **No round-trip yet**: editor → yEd works; yEd-edited GraphML back to
  the web editor is deferred to Spec 3-ter. If you need this, save the
  yEd file under a different name and continue editing in yEd.
- **Edge auto-routing inside TableNode**: yEd's hierarchical layout
  inside a TableNode may produce edge routings you don't like. Use
  yEd's "Edge Routing" tool to manually adjust.
- **Cross-row edges**: `rapporti` produces edges between US records in
  different rows; yEd renders them across rows but may overlap.
  Manual cleanup in yEd Desktop.

## Future work

- **Spec 3-ter** (proposed): GraphML re-import — Harris Creator reads
  yEd-edited GraphML and reconstructs editor state (with potential
  conflict resolution if DB has diverged).
- **Spec 4**: Real-time concurrent editing, conflict resolution UI.

## Related

- Spec 1: VocabProvider — canonical source for node visual styles.
- Spec 2: GraphProjector + s3dgraphy.exporter.graphml — for EM
  Datacenter consumption (clean GraphML, no TableNode).
- This Spec 3-bis: yEd-flavored output for human-editing-in-yEd
  workflows.
```

- [ ] **Step 7: Commit**

```bash
git add .gitignore pyarchinit_mini/__init__.py pyproject.toml CHANGELOG.md README.md docs/HARRIS_SWIMLANE.md docs/YED_INTEGRATION.md
git commit -m "release: bump to 2.4.0-alpha (Spec 3-bis Harris Swimlane Editor) + docs"
```

---

### Task 18: Final verification

**Files:** none (verification only)

- [ ] **Step 1: Full Spec 3-bis test surface green**

```bash
.venv/bin/python -m pytest \
  tests/unit/test_harris_swimlane_*.py \
  tests/unit/test_yed_writer.py \
  tests/integration/test_yed_writer_parity.py \
  tests/integration/test_harris_swimlane_routes_load.py \
  tests/integration/test_harris_swimlane_routes_save.py \
  tests/integration/test_harris_swimlane_routes_create_row.py \
  tests/integration/test_yed_export_route.py \
  -v 2>&1 | tail -10
```

Expected: all green; report count.

- [ ] **Step 2: Spec 1 + Spec 2 regression check**

```bash
.venv/bin/python -m pytest \
  tests/unit/test_vocab_*.py \
  tests/unit/test_graphproj_*.py \
  tests/unit/test_paradata_store_*.py \
  tests/unit/test_auto_regen.py \
  tests/unit/test_em_palette_vocab_backed.py \
  tests/unit/test_s3d_converter_vocab_backed.py \
  tests/integration/test_harris_matrix_visual_parity.py \
  tests/integration/test_harris_matrix_post_cutover.py \
  tests/integration/test_paradata_routes_authors.py \
  tests/integration/test_graph_routes.py \
  tests/integration/test_graph_import_flow.py \
  -v 2>&1 | tail -5
```

Expected: green (no regression).

- [ ] **Step 3: Smoke test web app routes**

```bash
.venv/bin/python -c "
from pyarchinit_mini.web_interface.app import create_app
app = create_app()
harris = [r.rule for r in app.url_map.iter_rules() if 'harris' in r.rule]
print('Harris routes:', len(harris))
for r in sorted(harris):
    print(' ', r)
"
```

Expected: see all 5 new endpoints (`/api/swimlanes`, `/api/load`,
`/api/save`, `/api/export/.../yed-graphml`) plus existing `/editor`,
`/api/export/<format>`, etc.

- [ ] **Step 4: Manual smoke on Volterra fixture**

```bash
# Spin up app pointing at fixture
DATABASE_URL="sqlite:///tests/fixtures/databases/sqlite_volterra_30us_with_periods.db" \
  .venv/bin/python -m pyarchinit_mini.web_interface.app &
APP_PID=$!
sleep 3

# Hit /api/swimlanes
curl -s http://localhost:5001/harris-creator/api/swimlanes/Volterra | python -m json.tool | head -20

# Hit /api/load
curl -s http://localhost:5001/harris-creator/api/load/Volterra | python -c "
import json, sys
d = json.load(sys.stdin)
print('rows:', len(d['rows']))
print('nodes:', len(d['nodes']))
print('edges:', len(d['edges']))
"

# Hit export
curl -s -o /tmp/volterra-harris-yed.graphml \
  http://localhost:5001/harris-creator/api/export/Volterra/yed-graphml
echo 'Export file:'
ls -lh /tmp/volterra-harris-yed.graphml
head -10 /tmp/volterra-harris-yed.graphml

kill $APP_PID 2>/dev/null
```

Expected: API responses look right; export file > 5KB; contains yEd TableNode.

- [ ] **Step 5: Review commit chain**

```bash
git log --oneline main..HEAD | wc -l
git log --oneline main..HEAD | head -25
```

Expected: ~20-22 commits.

- [ ] **Step 6: Final report**

Compile a brief (under 300 words) report:
- Total new tests added (count)
- Final test count: Spec 1 + Spec 2 + Spec 3-bis all green
- Routes registered (5 new Harris swimlane endpoints)
- Two-output architecture working (stratigraphy.graphml + harris-yed.graphml)
- Volterra fixture smoke: rows/nodes/edges counts
- Commit count
- Notable observations

Report status:
- `STATUS: DONE` — everything green, ready to merge
- `STATUS: DONE_WITH_CONCERNS` — observations
- `STATUS: BLOCKED` — critical failure

No commits in this task — verification only.

---

## Closing Notes

- **PR sequencing for upstream review:** local commits sequential, but
  for PRs against an upstream: PR1 = Tasks 1-4 (foundation), PR2 = Tasks
  5-8 (yed_writer), PR3 = Tasks 9-10 (load), PR4 = Tasks 11-12 (save),
  PR5 = Task 13 (create row), PR6 = Tasks 14-15 (frontend), PR7 = Task
  16 (export), PR8 = Tasks 17-18 (release).

- **Definition of Done satisfied:** see spec §9.

- **Known limitations carried into Spec 4:**
  - Last-writer-wins on concurrent edits (no real-time conflict UI)
  - No round-trip from yEd back to editor (Spec 3-ter)
  - Cross-site `period_table` (no per-site isolation)
  - Multi-period US placed only in start row

- **Next:** Spec 3 (SyncEngine + EM Backend) remains on hold pending EM
  Datacenter API readiness. Spec 3-ter (yEd round-trip) and Spec 4
  (real-time conflict resolution + per-site period_table) are future
  candidates.
