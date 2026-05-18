# Spec 7 — Extended Matrix Round-Trip Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align pyarchinit-mini-web with the pyarchinit Extended Matrix template on three planes — editor layout (lane verticali, Harris-classico interno), yEd GraphML export byte-compatible with pyarchinit QGIS, and yEd GraphML import populating `us_table` / `site_table` / `periodizzazione_table` with upsert by `node_uuid`.

**Architecture:** Server-side `harris_layout` computes positions, `swimlane_state.load` accepts a `group_by` query parameter (9 values), rewritten `yed_writer` emits the full 38-key `y:TableNode YED_TABLE_NODE` structure, new `yed_importer` parses files into a 2-phase `ImportPlan`, new `/import-graphml` blueprint exposes upload + preview + apply.

**Tech Stack:** Python 3.13, Flask, SQLAlchemy 2.x, lxml (XML parsing/emission), pytest, Cytoscape.js (editor frontend, no changes to library — only data shape), Bootstrap 5 (templates).

**Spec:** `docs/superpowers/specs/2026-05-18-spec-7-extended-matrix-roundtrip-design.md`

**Reference file:** `/Users/enzo/Downloads/cartella senza nome 16/Extended_Matrix_test_1.graphml`

---

## File Structure

### Create

- `pyarchinit_mini/harris_swimlane/harris_layout.py`
- `pyarchinit_mini/graphml_io/yed_importer.py`
- `pyarchinit_mini/graphml_io/yed_keys.py` (shared key d0..d37 constants)
- `pyarchinit_mini/web_interface/yed_import_routes.py`
- `pyarchinit_mini/web_interface/templates/yed_import/index.html`
- `pyarchinit_mini/web_interface/templates/yed_import/preview.html`
- `pyarchinit_mini/web_interface/templates/yed_import/result.html`
- `tests/unit/test_harris_layout.py`
- `tests/unit/test_yed_writer_extended_matrix.py`
- `tests/unit/test_yed_importer_parse.py`
- `tests/unit/test_yed_importer_plan.py`
- `tests/integration/test_yed_import_routes.py`
- `tests/integration/test_swimlane_group_by.py`
- `tests/integration/test_roundtrip_extmatrix.py`
- `tests/fixtures/yed_graphml/extended_matrix_pyarchinit.graphml` (copy of reference)
- `tests/fixtures/yed_graphml/minimal.graphml`
- `tests/fixtures/yed_graphml/vanilla_yed.graphml`
- `tests/fixtures/yed_graphml/malformed.graphml`
- `tests/fixtures/yed_graphml_outputs/golden_volterra_extmatrix.graphml`
- `tests/fixtures/_generate_yed_test_files.py`
- `docs/EXTENDED_MATRIX_IMPORT.md`
- `docs/EXTENDED_MATRIX_EXPORT.md`
- `docs/HARRIS_LAYOUT_ALGO.md`

### Modify

- `pyarchinit_mini/__init__.py` — bump `2.4.8` → `2.5.0`
- `pyproject.toml` — same version bump
- `CHANGELOG.md` — new `[2.5.0]` section IT + EN
- `pyarchinit_mini/harris_swimlane/swimlane_state.py` — accept `group_by` kwarg, call `harris_layout`
- `pyarchinit_mini/harris_swimlane/exceptions.py` — add `YEDImporterError`, `YEDImportValidationError`
- `pyarchinit_mini/graphml_io/yed_writer.py` — rewrite to emit YED_TABLE_NODE; keep old `write_yed_graphml` as deprecated wrapper
- `pyarchinit_mini/web_interface/harris_creator_routes.py` — accept `group_by` query param on `/api/load/<site>` and `/api/export/<site>/yed-graphml`
- `pyarchinit_mini/web_interface/app.py` — register `yed_import_bp`
- `pyarchinit_mini/web_interface/templates/harris_creator/editor.html` — add Group By dropdown + JS handler
- `pyarchinit_mini/web_interface/templates/base.html` — add Import GraphML link in both navbar dropdown and lateral sidebar

---

## Task 1: Bootstrap test fixtures

**Files:**
- Create: `tests/fixtures/_generate_yed_test_files.py`
- Create: `tests/fixtures/yed_graphml/extended_matrix_pyarchinit.graphml`
- Create: `tests/fixtures/yed_graphml/minimal.graphml`
- Create: `tests/fixtures/yed_graphml/vanilla_yed.graphml`
- Create: `tests/fixtures/yed_graphml/malformed.graphml`

- [ ] **Step 1: Copy the reference file**

```bash
mkdir -p tests/fixtures/yed_graphml tests/fixtures/yed_graphml_outputs
cp "/Users/enzo/Downloads/cartella senza nome 16/Extended_Matrix_test_1.graphml" \
   tests/fixtures/yed_graphml/extended_matrix_pyarchinit.graphml
```

- [ ] **Step 2: Write the fixture generator**

Create `tests/fixtures/_generate_yed_test_files.py`:

```python
"""One-shot generator for yEd Extended Matrix test fixtures.
Run once; commit the generated files.
"""
from pathlib import Path

FIX = Path(__file__).parent / "yed_graphml"
FIX.mkdir(parents=True, exist_ok=True)

MINIMAL = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key attr.name="pyarchinit.epochs_meta" attr.type="string" for="graph" id="d0"/>
  <key attr.name="EMID" attr.type="string" for="node" id="d4"/>
  <key attr.name="pyarchinit.us" attr.type="string" for="node" id="d6"/>
  <key attr.name="pyarchinit.area" attr.type="string" for="node" id="d7"/>
  <key attr.name="pyarchinit.sito" attr.type="string" for="node" id="d8"/>
  <key attr.name="pyarchinit.unita_tipo" attr.type="string" for="node" id="d9"/>
  <key attr.name="pyarchinit.periodo_iniziale" attr.type="string" for="node" id="d10"/>
  <key attr.name="pyarchinit.fase_iniziale" attr.type="string" for="node" id="d11"/>
  <key attr.name="pyarchinit.node_uuid" attr.type="string" for="node" id="d16"/>
  <key for="node" id="d31" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <data key="d0"><![CDATA[[{"name":"P1","periodo":"1","fase":"a","datazione_estesa":"Iron Age"}]]]></data>
    <node id="n1">
      <data key="d4">uuid-001</data>
      <data key="d6">1</data>
      <data key="d7">A</data>
      <data key="d8">TestSite</data>
      <data key="d9">US</data>
      <data key="d10">1</data>
      <data key="d11">a</data>
      <data key="d16">uuid-001</data>
    </node>
    <node id="n2">
      <data key="d4">uuid-002</data>
      <data key="d6">2</data>
      <data key="d7">A</data>
      <data key="d8">TestSite</data>
      <data key="d9">US</data>
      <data key="d10">1</data>
      <data key="d11">a</data>
      <data key="d16">uuid-002</data>
    </node>
    <node id="n3">
      <data key="d4">uuid-003</data>
      <data key="d6">3</data>
      <data key="d7">A</data>
      <data key="d8">TestSite</data>
      <data key="d9">USVs</data>
      <data key="d10">1</data>
      <data key="d11">a</data>
      <data key="d16">uuid-003</data>
    </node>
    <edge id="e1" source="n1" target="n2"/>
    <edge id="e2" source="n2" target="n3"/>
  </graph>
</graphml>
"""

VANILLA = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n1">
      <data key="d6"><y:ShapeNode><y:NodeLabel>plain</y:NodeLabel></y:ShapeNode></data>
    </node>
  </graph>
</graphml>
"""

MALFORMED = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph edgedefault="directed" id="G">
    <node id="n1">
      <data key="d6">incomplete
"""

(FIX / "minimal.graphml").write_text(MINIMAL, encoding="utf-8")
(FIX / "vanilla_yed.graphml").write_text(VANILLA, encoding="utf-8")
(FIX / "malformed.graphml").write_text(MALFORMED, encoding="utf-8")
print(f"Wrote 3 fixtures to {FIX}")
```

- [ ] **Step 3: Run the generator**

Run: `.venv/bin/python tests/fixtures/_generate_yed_test_files.py`
Expected: `Wrote 3 fixtures to .../tests/fixtures/yed_graphml`

- [ ] **Step 4: Verify all 4 fixtures present**

Run: `ls tests/fixtures/yed_graphml/`
Expected output: `extended_matrix_pyarchinit.graphml`, `malformed.graphml`, `minimal.graphml`, `vanilla_yed.graphml`

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/_generate_yed_test_files.py \
        tests/fixtures/yed_graphml/extended_matrix_pyarchinit.graphml \
        tests/fixtures/yed_graphml/minimal.graphml \
        tests/fixtures/yed_graphml/vanilla_yed.graphml \
        tests/fixtures/yed_graphml/malformed.graphml
git commit -m "test(spec7): bootstrap yEd Extended Matrix test fixtures"
```

---

## Task 2: Shared key constants module

**Files:**
- Create: `pyarchinit_mini/graphml_io/yed_keys.py`
- Test: `tests/unit/test_yed_writer_extended_matrix.py` (will be created in Task 5, just placeholder check now)

- [ ] **Step 1: Write `yed_keys.py`**

```python
"""yEd GraphML key definitions for pyarchinit Extended Matrix files.

The 38 keys d0..d37 are the canonical schema used by pyarchinit QGIS plugin.
Both yed_writer (emission) and yed_importer (parsing) share this mapping.

Each KEY entry: (key_id, attr_name, attr_type, for_target, yfiles_type)
"""
from typing import NamedTuple, Optional


class KeyDef(NamedTuple):
    key_id: str           # "d0" .. "d37"
    attr_name: Optional[str]
    attr_type: Optional[str]
    for_target: str       # "graph" | "node" | "edge" | "port" | "graphml"
    yfiles_type: Optional[str] = None


KEYS: tuple[KeyDef, ...] = (
    KeyDef("d0", "pyarchinit.epochs_meta", "string", "graph"),
    KeyDef("d1", None, None, "port", "portgraphics"),
    KeyDef("d2", None, None, "port", "portgeometry"),
    KeyDef("d3", None, None, "port", "portuserdata"),
    KeyDef("d4", "EMID", "string", "node"),
    KeyDef("d5", "URI", "string", "node"),
    KeyDef("d6", "pyarchinit.us", "string", "node"),
    KeyDef("d7", "pyarchinit.area", "string", "node"),
    KeyDef("d8", "pyarchinit.sito", "string", "node"),
    KeyDef("d9", "pyarchinit.unita_tipo", "string", "node"),
    KeyDef("d10", "pyarchinit.periodo_iniziale", "string", "node"),
    KeyDef("d11", "pyarchinit.fase_iniziale", "string", "node"),
    KeyDef("d12", "pyarchinit.rapporti", "string", "node"),
    KeyDef("d13", "pyarchinit.d_stratigrafica", "string", "node"),
    KeyDef("d14", "pyarchinit.d_interpretativa", "string", "node"),
    KeyDef("d15", "pyarchinit.documentazione", "string", "node"),
    KeyDef("d16", "pyarchinit.node_uuid", "string", "node"),
    KeyDef("d17", "pyarchinit.struttura", "string", "node"),
    KeyDef("d18", "pyarchinit.attivita", "string", "node"),
    KeyDef("d19", "pyarchinit.settore", "string", "node"),
    KeyDef("d20", "pyarchinit.ambient", "string", "node"),
    KeyDef("d21", "pyarchinit.saggio", "string", "node"),
    KeyDef("d22", "pyarchinit.quad_par", "string", "node"),
    KeyDef("d23", "pyarchinit.datazione_estesa", "string", "node"),
    KeyDef("d24", "pyarchinit.periodo", "string", "node"),
    KeyDef("d25", "pyarchinit.fase", "string", "node"),
    KeyDef("d26", "pyarchinit.cron_iniziale", "string", "node"),
    KeyDef("d27", "pyarchinit.cron_finale", "string", "node"),
    KeyDef("d28", "pyarchinit.datazione_estesa", "string", "node"),
    KeyDef("d29", "url", "string", "node"),
    KeyDef("d30", "description", "string", "node"),
    KeyDef("d31", None, None, "node", "nodegraphics"),
    KeyDef("d32", None, None, "graphml", "resources"),
    KeyDef("d33", "EMID", "string", "edge"),
    KeyDef("d34", "URI", "string", "edge"),
    KeyDef("d35", "url", "string", "edge"),
    KeyDef("d36", "description", "string", "edge"),
    KeyDef("d37", None, None, "edge", "edgegraphics"),
)


# Quick lookups used at parse/emit time.
KEY_BY_ID: dict[str, KeyDef] = {k.key_id: k for k in KEYS}
KEY_BY_ATTR_NAME: dict[str, KeyDef] = {k.attr_name: k for k in KEYS if k.attr_name}

# Subset of node keys whose values map 1:1 to us_table columns.
US_NODE_FIELDS = (
    "pyarchinit.us", "pyarchinit.area", "pyarchinit.sito",
    "pyarchinit.unita_tipo", "pyarchinit.periodo_iniziale",
    "pyarchinit.fase_iniziale", "pyarchinit.rapporti",
    "pyarchinit.d_stratigrafica", "pyarchinit.d_interpretativa",
    "pyarchinit.documentazione", "pyarchinit.node_uuid",
    "pyarchinit.struttura", "pyarchinit.attivita", "pyarchinit.settore",
    "pyarchinit.ambient", "pyarchinit.saggio", "pyarchinit.quad_par",
    "pyarchinit.datazione_estesa",
)
```

- [ ] **Step 2: Smoke-test the module imports**

Run: `.venv/bin/python -c "from pyarchinit_mini.graphml_io.yed_keys import KEYS, KEY_BY_ID; print(len(KEYS), 'keys'); assert len(KEYS) == 38; assert KEY_BY_ID['d6'].attr_name == 'pyarchinit.us'"`
Expected: `38 keys`

- [ ] **Step 3: Commit**

```bash
git add pyarchinit_mini/graphml_io/yed_keys.py
git commit -m "feat(spec7): shared yEd key constants (d0..d37) for Extended Matrix"
```

---

## Task 3: `harris_layout` module — topological positions

**Files:**
- Create: `pyarchinit_mini/harris_swimlane/harris_layout.py`
- Test: `tests/unit/test_harris_layout.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/unit/test_harris_layout.py`:

```python
"""Tests for harris_layout — server-side Harris-classico positioning."""
import pytest

from pyarchinit_mini.harris_swimlane.harris_layout import compute_harris_positions


def test_empty_input_returns_empty():
    positions = compute_harris_positions([], [], lane_id_for=lambda n: "L", lane_widths={"L": 200})
    assert positions == {}


def test_single_node_centered_in_lane():
    nodes = [{"id": "n1", "lane": "L1"}]
    positions = compute_harris_positions(
        nodes, [], lane_id_for=lambda n: n["lane"], lane_widths={"L1": 200}
    )
    assert "n1" in positions
    x, y = positions["n1"]
    assert 0 <= x <= 200


def test_two_nodes_one_edge_recent_on_top():
    nodes = [{"id": "n1", "lane": "L1"}, {"id": "n2", "lane": "L1"}]
    edges = [{"source": "n1", "target": "n2", "label": "overlies"}]
    positions = compute_harris_positions(
        nodes, edges, lane_id_for=lambda n: n["lane"], lane_widths={"L1": 200}
    )
    # n1 overlies n2 ⇒ n1 must be above n2 in canvas (smaller y).
    assert positions["n1"][1] < positions["n2"][1]


def test_orphan_nodes_packed_at_bottom():
    nodes = [
        {"id": "n1", "lane": "L1"}, {"id": "n2", "lane": "L1"},
        {"id": "orphan", "lane": "L1"},
    ]
    edges = [{"source": "n1", "target": "n2", "label": "overlies"}]
    positions = compute_harris_positions(
        nodes, edges, lane_id_for=lambda n: n["lane"], lane_widths={"L1": 200}
    )
    # orphan has no edges → must end up at the deepest y in lane
    max_y = max(y for _, y in positions.values())
    assert positions["orphan"][1] == max_y


def test_multiple_lanes_isolation():
    nodes = [
        {"id": "a", "lane": "L1"}, {"id": "b", "lane": "L1"},
        {"id": "c", "lane": "L2"},
    ]
    edges = [{"source": "a", "target": "b", "label": "overlies"}]
    positions = compute_harris_positions(
        nodes, edges,
        lane_id_for=lambda n: n["lane"],
        lane_widths={"L1": 200, "L2": 200},
    )
    # Each lane independently positioned — no overlap on x between lanes.
    assert positions["c"][0] >= 0
    assert positions["a"][1] < positions["b"][1]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/unit/test_harris_layout.py -v`
Expected: 5 failures with `ModuleNotFoundError: No module named 'pyarchinit_mini.harris_swimlane.harris_layout'`

- [ ] **Step 3: Implement `harris_layout.py`**

Create `pyarchinit_mini/harris_swimlane/harris_layout.py`:

```python
"""Harris-classico positioning algorithm — server-side, deterministic.

Each lane gets a sub-graph layout: nodes connected by stratigraphic edges
(``overlies``, ``is_after``) are ranked top→bottom so the most recent
(no incoming edges) is at the top of the lane and the oldest is at the
bottom. Orphan nodes (no edges) sit at the deepest y in their lane.

Output is consumed by ``SwimlaneState.load`` and ``yed_writer`` so the
editor canvas and the exported yEd file produce identical geometry.
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Callable


_TOPO_EDGE_LABELS = frozenset({"overlies", "is_after"})


def compute_harris_positions(
    nodes: list[dict],
    edges: list[dict],
    *,
    lane_id_for: Callable[[dict], str],
    lane_widths: dict[str, int],
    node_w: int = 80,
    node_h: int = 30,
    h_gap: int = 30,
    v_gap: int = 20,
) -> dict[str, tuple[float, float]]:
    """Compute (x, y) for every node, confined within its lane.

    Args:
        nodes: list of {"id", "lane", ...}.
        edges: list of {"source", "target", "label"}.
        lane_id_for: callable returning the lane id for a node.
        lane_widths: lane_id → pixel width (used to clamp x within lane).
        node_w / node_h: pixel dims for layout spacing.
        h_gap / v_gap: spacing between sibling nodes.

    Returns:
        {node_id: (x, y)} with global canvas coordinates (lane x-offsets
        baked in by the caller's lane_widths order).
    """
    if not nodes:
        return {}

    # Group nodes by lane.
    lane_nodes: dict[str, list[dict]] = defaultdict(list)
    for n in nodes:
        lane_nodes[lane_id_for(n)].append(n)

    # Index edges only those participating in topological order.
    topo_edges_by_lane: dict[str, list[tuple[str, str]]] = defaultdict(list)
    node_to_lane = {n["id"]: lane_id_for(n) for n in nodes}
    for e in edges:
        if e.get("label") not in _TOPO_EDGE_LABELS:
            continue
        s_lane = node_to_lane.get(e["source"])
        t_lane = node_to_lane.get(e["target"])
        if s_lane and s_lane == t_lane:
            topo_edges_by_lane[s_lane].append((e["source"], e["target"]))

    positions: dict[str, tuple[float, float]] = {}
    x_offset = 0.0
    for lane_id, ns in lane_nodes.items():
        width = lane_widths.get(lane_id, 200)
        sub_positions = _layout_lane(ns, topo_edges_by_lane[lane_id], width,
                                     node_w, node_h, h_gap, v_gap)
        for nid, (x_local, y_local) in sub_positions.items():
            positions[nid] = (x_offset + x_local, y_local)
        x_offset += width + h_gap

    return positions


def _layout_lane(
    nodes: list[dict], edges: list[tuple[str, str]], lane_width: int,
    node_w: int, node_h: int, h_gap: int, v_gap: int,
) -> dict[str, tuple[float, float]]:
    """Layout one lane: ranked top→bottom by topological order, orphans last."""
    in_edges: dict[str, list[str]] = defaultdict(list)
    out_edges: dict[str, list[str]] = defaultdict(list)
    node_ids = {n["id"] for n in nodes}
    for s, t in edges:
        if s in node_ids and t in node_ids:
            in_edges[t].append(s)
            out_edges[s].append(t)

    # Kahn's algorithm — assign rank to each connected node.
    rank: dict[str, int] = {}
    queue = deque(nid for nid in node_ids if not in_edges.get(nid))
    while queue:
        nid = queue.popleft()
        r = max((rank[p] + 1 for p in in_edges.get(nid, [])), default=0)
        rank[nid] = r
        for nxt in out_edges.get(nid, []):
            # Re-enqueue only when all parents have a rank already.
            if all(p in rank for p in in_edges.get(nxt, [])):
                if nxt not in rank:
                    queue.append(nxt)

    # Nodes not in rank (cycles / orphans) get the deepest rank.
    max_rank = max(rank.values(), default=0)
    orphan_rank = max_rank + 1
    ranked: dict[int, list[str]] = defaultdict(list)
    for n in nodes:
        nid = n["id"]
        r = rank.get(nid, orphan_rank)
        ranked[r].append(nid)

    positions: dict[str, tuple[float, float]] = {}
    for r in sorted(ranked.keys()):
        siblings = ranked[r]
        row_w = len(siblings) * node_w + (len(siblings) - 1) * h_gap
        start_x = max((lane_width - row_w) / 2.0, 0.0)
        y = r * (node_h + v_gap)
        for i, nid in enumerate(siblings):
            x = start_x + i * (node_w + h_gap)
            positions[nid] = (x, y)
    return positions
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/unit/test_harris_layout.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/harris_swimlane/harris_layout.py tests/unit/test_harris_layout.py
git commit -m "feat(spec7): harris_layout — server-side Harris-classico positions"
```

---

## Task 4: Extend `swimlane_state.load` with `group_by`

**Files:**
- Modify: `pyarchinit_mini/harris_swimlane/swimlane_state.py`
- Test: `tests/integration/test_swimlane_group_by.py`

- [ ] **Step 1: Write the failing integration tests**

Create `tests/integration/test_swimlane_group_by.py`:

```python
"""Integration tests for SwimlaneState.load(group_by=...) — 9 valid values."""
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState

DB_FIX = Path(__file__).parent.parent / "fixtures" / "databases" / "sqlite_volterra_30us_with_periods.db"


@pytest.fixture
def session():
    eng = create_engine(f"sqlite:///{DB_FIX}")
    s = sessionmaker(bind=eng)()
    yield s
    s.close()


def test_default_group_by_is_period_phase(session):
    state = SwimlaneState.load(session, "Volterra")
    assert state.group_by == "period_phase"
    assert len(state.rows) == 5


def test_group_by_period_phase_explicit(session):
    state = SwimlaneState.load(session, "Volterra", group_by="period_phase")
    assert state.group_by == "period_phase"
    assert len(state.rows) == 5


def test_group_by_none_returns_single_lane(session):
    state = SwimlaneState.load(session, "Volterra", group_by="none")
    assert state.group_by == "none"
    assert len(state.rows) == 1
    assert state.rows[0].row_id == "row_default"


def test_group_by_invalid_raises(session):
    with pytest.raises(ValueError, match="invalid group_by"):
        SwimlaneState.load(session, "Volterra", group_by="not_a_valid_value")


@pytest.mark.parametrize("gb", ["struttura", "attivita", "settore", "area", "ambient", "saggio", "quad_par"])
def test_group_by_distinct_field_runs(session, gb):
    state = SwimlaneState.load(session, "Volterra", group_by=gb)
    assert state.group_by == gb
    # Fixture has no values in these columns → 1 lane "(missing)"
    assert len(state.rows) >= 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/integration/test_swimlane_group_by.py -v`
Expected: failures: `EditorState has no attribute group_by` / `load() got an unexpected keyword argument 'group_by'`.

- [ ] **Step 3: Update `EditorState` dataclass**

Open `pyarchinit_mini/harris_swimlane/swimlane_state.py` and modify the `EditorState` dataclass:

```python
@dataclass
class EditorState:
    site: str
    rows: list
    nodes: list
    edges: list
    pending_changes: dict
    group_by: str = "period_phase"
```

- [ ] **Step 4: Add `_VALID_GROUP_BY` + `_build_lanes_by_distinct` + extend `load`**

Add at the top of `swimlane_state.py` (after imports):

```python
_VALID_GROUP_BY = frozenset({
    "period_phase",
    "struttura", "attivita", "settore", "area",
    "ambient", "saggio", "quad_par",
    "none",
})

_DISTINCT_FIELD_COLS = {
    "struttura": "struttura",
    "attivita": "attivita",
    "settore": "settore",
    "area": "area",
    "ambient": "ambient",
    "saggio": "saggio",
    "quad_par": "quad_par",
}
```

Replace `SwimlaneState.load` signature and body to accept `group_by`:

```python
@staticmethod
def load(session: Session, site: str, *, group_by: str = "period_phase") -> EditorState:
    """Load swimlane editor state for the site, organised by group_by."""
    if group_by not in _VALID_GROUP_BY:
        raise ValueError(f"invalid group_by: {group_by!r}")

    # ... (existing color/style resolution stays the same) ...

    if group_by == "period_phase":
        provider = RowProvider(session, site)
        rows = provider.list_rows()
    elif group_by == "none":
        from .row_provider import Row, PERIOD_COLORS
        rows = [Row(
            row_id="row_default",
            period_name="All",
            phase_name=None,
            start_date=None, end_date=None,
            color=PERIOD_COLORS[0],
            source="virtual_none",
        )]
    else:
        col = _DISTINCT_FIELD_COLS[group_by]
        rows = _build_lanes_by_distinct(session, site, col)

    # ... existing us_rows loading stays the same ...
    # ... existing nodes building stays the same, except parent_row_id is
    # computed differently for non-period_phase ...

    state = EditorState(
        site=site,
        rows=rows,
        nodes=nodes,
        edges=edges,
        pending_changes={"us_updates": [], "us_inserts": [], "us_deletes": []},
        group_by=group_by,
    )
    return state
```

Add helper near other module-level helpers:

```python
def _build_lanes_by_distinct(session, site: str, col: str):
    """Return one Row per DISTINCT value of us_table.<col> for the site."""
    from .row_provider import Row, PERIOD_COLORS
    rows = session.execute(
        text(f"SELECT DISTINCT COALESCE({col}, '') AS v FROM us_table "
             f"WHERE sito = :sito ORDER BY v"),
        {"sito": site},
    ).fetchall()
    out = []
    for i, r in enumerate(rows):
        value = r[0] or "(unset)"
        row_id = "row_" + value.lower().replace(" ", "_").replace("/", "_") or "row_unset"
        out.append(Row(
            row_id=row_id,
            period_name=value,
            phase_name=None,
            start_date=None,
            end_date=None,
            color=PERIOD_COLORS[i % len(PERIOD_COLORS)],
            source=f"distinct_{col}",
        ))
    if not out:
        out.append(Row(
            row_id="row_unset", period_name="(unset)", phase_name=None,
            start_date=None, end_date=None,
            color=PERIOD_COLORS[0], source=f"distinct_{col}",
        ))
    return out
```

Replace the loop that computes `parent_row_id` for each US node to use the lookup based on `group_by`:

```python
# Compute parent_row_id depending on group_by.
def _parent_row_id_for(r) -> str:
    if group_by == "period_phase":
        return derive_row_id(r[7], r[8])  # periodo, fase
    if group_by == "none":
        return "row_default"
    # The remaining mapping: r index 2 = area; we need a row by the col value
    # For non-period_phase, we re-query us_table for the col value because it
    # may not be in the SELECT projection. To keep performance, extend the
    # SELECT below.
    col_index_map = {
        "area": 2, "struttura": 12, "attivita": 13, "settore": 14,
        "ambient": 15, "saggio": 16, "quad_par": 17,
    }
    idx = col_index_map[group_by]
    raw = r[idx] or ""
    if not raw:
        return "row_unset"
    return "row_" + raw.lower().replace(" ", "_").replace("/", "_")
```

And extend the SQL inside `load` for non-period_phase group_by to include extra columns:

```python
us_rows = session.execute(text(
    "SELECT id_us, sito, area, us, unita_tipo, rapporti, node_uuid, "
    "periodo_iniziale, fase_iniziale, "
    "d_stratigrafica, datazione, file_path, "
    "struttura, attivita, settore, ambient, saggio, quad_par "
    "FROM us_table WHERE sito = :sito ORDER BY id_us"
), {"sito": site}).fetchall()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/integration/test_swimlane_group_by.py tests/unit/test_harris_swimlane_*.py tests/integration/test_harris_swimlane_*.py -q --tb=short`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/harris_swimlane/swimlane_state.py \
        tests/integration/test_swimlane_group_by.py
git commit -m "feat(spec7): swimlane_state.load accepts group_by (9 values)"
```

---

## Task 5: Wire `harris_layout` into `swimlane_state.load`

**Files:**
- Modify: `pyarchinit_mini/harris_swimlane/swimlane_state.py`
- Test: `tests/integration/test_swimlane_group_by.py` (extended)

- [ ] **Step 1: Add test for Harris layout integration**

Append to `tests/integration/test_swimlane_group_by.py`:

```python
def test_harris_positions_within_lanes(session):
    state = SwimlaneState.load(session, "Volterra")
    # Nodes within the same lane must have ascending y when there is an
    # edge between them (older below newer).
    by_id = {n.data["id"]: n for n in state.nodes if not n.data.get("is_swimlane")}
    for e in state.edges:
        if e.data.get("label") != "overlies":
            continue
        src = by_id.get(e.data["source"])
        tgt = by_id.get(e.data["target"])
        if not src or not tgt:
            continue
        if src.data.get("parent") != tgt.data.get("parent"):
            continue
        # source overlies target → source must be above target (smaller y).
        assert src.position["y"] <= tgt.position["y"], (
            f"{src.data['id']} should be above {tgt.data['id']}"
        )
```

- [ ] **Step 2: Run test — expect failure**

Run: `.venv/bin/python -m pytest tests/integration/test_swimlane_group_by.py::test_harris_positions_within_lanes -v`
Expected: failure (current `initial_node_position` is naive sequential).

- [ ] **Step 3: Replace position computation in `swimlane_state.load`**

In `swimlane_state.py`, replace the per-node `pos = initial_node_position(...)` loop with a call to `harris_layout` AFTER all nodes are built:

```python
# (After all nodes appended with placeholder position = None)
from .harris_layout import compute_harris_positions

# Convert nodes into the harris_layout input shape.
hl_nodes = [
    {"id": el.data["id"], "lane": el.data["parent"]}
    for el in nodes if not el.data.get("is_swimlane")
]
hl_edges = [
    {"source": e.data["source"], "target": e.data["target"], "label": e.data["label"]}
    for e in edges
]
lane_widths = {row.row_id: 300 for row in rows}
positions = compute_harris_positions(
    hl_nodes, hl_edges,
    lane_id_for=lambda n: n["lane"],
    lane_widths=lane_widths,
)
for el in nodes:
    if el.data.get("is_swimlane"):
        continue
    x, y = positions.get(el.data["id"], (0.0, 0.0))
    el.position = {"x": x, "y": y}
```

(Remove the prior `pos = initial_node_position(_RowLike(), idx)` block — replace it with `el.position = None` initially, then overwritten by the loop above.)

- [ ] **Step 4: Run all swimlane tests**

Run: `.venv/bin/python -m pytest tests/unit/test_harris_swimlane_*.py tests/integration/test_harris_swimlane_*.py tests/integration/test_swimlane_group_by.py -q --tb=short`
Expected: all pass (47 prior + new ones).

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/harris_swimlane/swimlane_state.py \
        tests/integration/test_swimlane_group_by.py
git commit -m "feat(spec7): swimlane_state uses harris_layout for node positions"
```

---

## Task 6: `/api/load/<site>` accepts `group_by` query param

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py`
- Test: `tests/integration/test_swimlane_group_by.py` (extended)

- [ ] **Step 1: Write the failing API test**

Append to `tests/integration/test_swimlane_group_by.py`:

```python
def test_api_load_accepts_group_by(tmp_path, monkeypatch):
    from flask import Flask
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp

    db_path = str(DB_FIX)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(harris_creator_bp)
    cli = app.test_client()

    r = cli.get("/harris-creator/api/load/Volterra?group_by=none")
    assert r.status_code == 200, r.get_data(as_text=True)
    body = r.get_json()
    assert body["group_by"] == "none"
    assert len(body["rows"]) == 1
```

- [ ] **Step 2: Run test — expect failure**

Run: `.venv/bin/python -m pytest tests/integration/test_swimlane_group_by.py::test_api_load_accepts_group_by -v`
Expected: failure (current endpoint ignores `group_by`).

- [ ] **Step 3: Update the `/api/load/<site>` endpoint**

In `pyarchinit_mini/web_interface/harris_creator_routes.py`, locate `api_get_load` and add a `request.args.get("group_by", "period_phase")` parse + pass-through:

```python
@harris_creator_bp.get("/api/load/<site>")
def api_get_load(site: str):
    group_by = request.args.get("group_by", "period_phase")
    try:
        session = _get_session()
        state = SwimlaneState.load(session, site, group_by=group_by)
        return jsonify({
            "site": state.site,
            "group_by": state.group_by,
            "rows": [
                {
                    "row_id": r.row_id,
                    "period_name": r.period_name,
                    "phase_name": r.phase_name,
                    "color": r.color,
                    "start_date": r.start_date,
                    "end_date": r.end_date,
                    "source": r.source,
                }
                for r in state.rows
            ],
            "nodes": [{"data": el.data, "position": el.position} for el in state.nodes],
            "edges": [{"data": el.data} for el in state.edges],
            "pending_changes": state.pending_changes,
        }), 200
    except ValueError as e:
        return jsonify({"error": "validation", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "internal", "message": str(e)}), 500
```

- [ ] **Step 4: Run the test — expect pass**

Run: `.venv/bin/python -m pytest tests/integration/test_swimlane_group_by.py::test_api_load_accepts_group_by -v`
Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/harris_creator_routes.py \
        tests/integration/test_swimlane_group_by.py
git commit -m "feat(spec7): /api/load/<site>?group_by=X 9 valid values"
```

---

## Task 7: yEd writer — emit `<key>` declarations

**Files:**
- Modify: `pyarchinit_mini/graphml_io/yed_writer.py`
- Test: `tests/unit/test_yed_writer_extended_matrix.py`

- [ ] **Step 1: Write the failing test for keys section**

Create `tests/unit/test_yed_writer_extended_matrix.py`:

```python
"""Tests for yed_writer rewrite — Extended Matrix byte-compat."""
from pathlib import Path
import pytest

from pyarchinit_mini.harris_swimlane.swimlane_state import EditorState, CytoscapeElement
from pyarchinit_mini.graphml_io.yed_writer import write_extended_matrix_graphml


@pytest.fixture
def minimal_state():
    return EditorState(
        site="TestSite", rows=[], nodes=[], edges=[],
        pending_changes={}, group_by="period_phase",
    )


def test_emits_38_key_definitions(tmp_path, minimal_state):
    out = tmp_path / "out.graphml"
    write_extended_matrix_graphml(
        minimal_state, site_meta={"sito": "TestSite"}, epochs=[], out=out,
    )
    xml = out.read_text(encoding="utf-8")
    # Count <key declarations
    assert xml.count("<key ") >= 38
    # Specific keys present
    for k in ("d0", "d4", "d6", "d8", "d16", "d31", "d37"):
        assert f'id="{k}"' in xml


def test_root_graphml_namespace(tmp_path, minimal_state):
    out = tmp_path / "out.graphml"
    write_extended_matrix_graphml(
        minimal_state, site_meta={"sito": "TestSite"}, epochs=[], out=out,
    )
    xml = out.read_text(encoding="utf-8")
    assert 'xmlns="http://graphml.graphdrawing.org/xmlns"' in xml
    assert 'xmlns:y="http://www.yworks.com/xml/graphml"' in xml
```

- [ ] **Step 2: Run test — expect failure**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_writer_extended_matrix.py -v`
Expected: failure — `write_extended_matrix_graphml` does not exist.

- [ ] **Step 3: Implement initial structure**

Rewrite `pyarchinit_mini/graphml_io/yed_writer.py`:

```python
"""yEd-flavored GraphML writer — Extended Matrix template compatible with
pyarchinit QGIS plugin.

Emits:
  - 38 <key> declarations (d0..d37 from yed_keys.KEYS)
  - <graph> with optional <data key="d0"> epochs_meta payload
  - one <node yfiles.foldertype="group"> root with <y:TableNode YED_TABLE_NODE>
  - per-row <y:Row> children inside the TableNode
  - per-US <node> children with all 38 keys valorized
  - per-edge <edge> with edgegraphics

The old write_yed_graphml is kept as a thin deprecated wrapper for one
release; removed in 2.6.0.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
from xml.sax.saxutils import escape

from pyarchinit_mini.harris_swimlane.exceptions import YEDWriterError
from pyarchinit_mini.graphml_io.yed_keys import KEYS, KeyDef


def write_extended_matrix_graphml(
    state: Any,
    *,
    site_meta: dict,
    epochs: list[dict],
    out: Path,
) -> None:
    """Atomic write — emits at out, .tmp staging."""
    out = Path(out)
    tmp = out.with_suffix(out.suffix + ".tmp")
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        xml = _build_xml(state, site_meta, epochs)
        tmp.write_text(xml, encoding="utf-8")
        tmp.replace(out)
    except Exception as e:
        if tmp.exists():
            try: tmp.unlink()
            except Exception: pass
        raise YEDWriterError(path=str(out), msg=str(e)) from e


def _build_xml(state, site_meta: dict, epochs: list[dict]) -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns" '
        'xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" '
        'xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" '
        'xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xmlns:y="http://www.yworks.com/xml/graphml" '
        'xmlns:yed="http://www.yworks.com/xml/yed/3" '
        'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns '
        'http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">',
    ]
    parts.extend(_render_key_declarations(KEYS))
    parts.append('  <graph edgedefault="directed" id="G">')
    parts.append(_render_epochs_meta(epochs))
    parts.append(_render_table_root(state, site_meta))
    parts.append(_render_us_nodes(state))
    parts.append(_render_edges(state))
    parts.append('  </graph>')
    parts.append('</graphml>')
    return "\n".join(p for p in parts if p)


def _render_key_declarations(keys: Iterable[KeyDef]) -> list[str]:
    out = []
    for k in keys:
        attrs = [f'id="{k.key_id}"', f'for="{k.for_target}"']
        if k.attr_name:
            attrs.append(f'attr.name="{escape(k.attr_name)}"')
        if k.attr_type:
            attrs.append(f'attr.type="{k.attr_type}"')
        if k.yfiles_type:
            attrs.append(f'yfiles.type="{k.yfiles_type}"')
        out.append('  <key ' + ' '.join(attrs) + '/>')
    return out


def _render_epochs_meta(epochs: list[dict]) -> str:
    import json
    if not epochs:
        return ''
    payload = json.dumps(epochs, ensure_ascii=False)
    return f'    <data key="d0" xml:space="preserve"><![CDATA[{payload}]]></data>'


def _render_table_root(state, site_meta: dict) -> str:
    """Stub — filled in Task 8."""
    return ''


def _render_us_nodes(state) -> str:
    """Stub — filled in Task 9."""
    return ''


def _render_edges(state) -> str:
    """Stub — filled in Task 10."""
    return ''


# Deprecated thin wrapper for one release.
def write_yed_graphml(state: Any, path: Path) -> None:
    """DEPRECATED — use write_extended_matrix_graphml. Removed in 2.6.0."""
    import warnings
    warnings.warn(
        "write_yed_graphml is deprecated; use write_extended_matrix_graphml",
        DeprecationWarning, stacklevel=2,
    )
    write_extended_matrix_graphml(
        state, site_meta={"sito": getattr(state, "site", "Unknown")}, epochs=[], out=path,
    )
```

- [ ] **Step 4: Run tests — expect pass**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_writer_extended_matrix.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphml_io/yed_writer.py tests/unit/test_yed_writer_extended_matrix.py
git commit -m "feat(spec7): yed_writer emits 38-key declarations + namespaces"
```

---

## Task 8: yEd writer — emit `y:TableNode` root with rows

**Files:**
- Modify: `pyarchinit_mini/graphml_io/yed_writer.py`
- Test: `tests/unit/test_yed_writer_extended_matrix.py` (extended)

- [ ] **Step 1: Add the failing test**

Append to `tests/unit/test_yed_writer_extended_matrix.py`:

```python
def test_emits_table_node_root(tmp_path):
    from pyarchinit_mini.harris_swimlane.row_provider import Row
    rows = [
        Row(row_id="row_p1_a", period_name="Period01", phase_name="a",
            start_date=0, end_date=100, color="#FFAAAA", source="period_table"),
        Row(row_id="row_p2_a", period_name="Period02", phase_name="a",
            start_date=100, end_date=200, color="#AAFFAA", source="period_table"),
    ]
    state = EditorState(site="TestSite", rows=rows, nodes=[], edges=[],
                       pending_changes={}, group_by="period_phase")
    out = tmp_path / "out.graphml"
    write_extended_matrix_graphml(state, site_meta={"sito": "TestSite"}, epochs=[], out=out)
    xml = out.read_text(encoding="utf-8")
    assert 'yfiles.foldertype="group"' in xml
    assert 'configuration="YED_TABLE_NODE"' in xml
    assert '<y:Row id="row_p1_a"' in xml
    assert '<y:Row id="row_p2_a"' in xml
```

- [ ] **Step 2: Run — expect failure**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_writer_extended_matrix.py::test_emits_table_node_root -v`
Expected: failure.

- [ ] **Step 3: Implement `_render_table_root`**

Replace stub in `yed_writer.py`:

```python
def _render_table_root(state, site_meta: dict) -> str:
    """Emit the y:TableNode group node containing all swimlane rows."""
    sito = site_meta.get("sito", "Unknown")
    rows_xml = []
    row_height = 200
    for i, row in enumerate(state.rows):
        rid = escape(row.row_id)
        label_text = row.period_name
        if row.phase_name:
            label_text = f"{row.period_name} / {row.phase_name}"
        if row.start_date is not None or row.end_date is not None:
            label_text = f"{label_text} [start:{row.start_date or 0};end:{row.end_date or 0}]"
        rows_xml.append(
            f'              <y:Row id="{rid}" height="{row_height}" '
            f'minimumHeight="80.0" nodeLabelMaxWidth="0.0"/>'
        )

    # Compute table geometry.
    height = max(len(state.rows) * row_height + 60, 200)
    width = 2000

    parts = [
        '    <node id="swimlane_root" yfiles.foldertype="group">',
        f'      <data key="d4"><![CDATA[swimlane-root-{escape(sito)}]]></data>',
        f'      <data key="d8">{escape(sito)}</data>',
        '      <data key="d30">Stratigrafia</data>',
        '      <data key="d31">',
        '        <y:TableNode configuration="YED_TABLE_NODE">',
        f'          <y:Geometry height="{height}.0" width="{width}.0" x="0.0" y="0.0"/>',
        '          <y:Fill color="#ECF5FF" color2="#0042F440" transparent="false"/>',
        '          <y:BorderStyle hasColor="false" type="line" width="1.0"/>',
        f'          <y:NodeLabel alignment="center" autoSizePolicy="content" '
        f'fontFamily="Dialog" fontSize="15" fontStyle="plain" hasBackgroundColor="false" '
        f'hasLineColor="false" horizontalTextPosition="center" iconTextGap="4" '
        f'modelName="internal" modelPosition="t" textColor="#000000" '
        f'verticalTextPosition="bottom" visible="true" xml:space="preserve">'
        f'Archaeological Site [ID:{escape(sito)}]</y:NodeLabel>',
        '          <y:Table>',
        '            <y:Insets bottom="0.0" bottomF="0.0" left="0.0" leftF="0.0" '
        'right="0.0" rightF="0.0" top="24.0" topF="24.0"/>',
        '            <y:Columns/>',
        '            <y:Rows>',
        *rows_xml,
        '            </y:Rows>',
        '          </y:Table>',
        '        </y:TableNode>',
        '      </data>',
        '      <graph edgedefault="directed" id="swimlane_root::graph">',
    ]
    # Note: closing of <graph> + </node> happens in _render_us_nodes (Task 9)
    # because US nodes are children of this nested graph.
    return "\n".join(parts)
```

- [ ] **Step 4: Run — expect pass**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_writer_extended_matrix.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphml_io/yed_writer.py tests/unit/test_yed_writer_extended_matrix.py
git commit -m "feat(spec7): yed_writer emits y:TableNode YED_TABLE_NODE root"
```

---

## Task 9: yEd writer — emit per-US `<node>` with all keys

**Files:**
- Modify: `pyarchinit_mini/graphml_io/yed_writer.py`
- Test: `tests/unit/test_yed_writer_extended_matrix.py` (extended)

- [ ] **Step 1: Add failing test**

Append to `tests/unit/test_yed_writer_extended_matrix.py`:

```python
def test_emits_us_node_with_keys(tmp_path):
    from pyarchinit_mini.harris_swimlane.row_provider import Row
    rows = [Row(row_id="row_p1_a", period_name="P1", phase_name="a",
               start_date=0, end_date=100, color="#FFAAAA", source="period_table")]
    nodes = [CytoscapeElement(
        data={
            "id": "us_42", "label": "US42", "parent": "row_p1_a",
            "unit_type": "US", "color": "#F0F0F0",
            "shape": "rectangle", "border_color": "#540909", "border_style": "solid",
            "us": 42, "us_number": 42,
            "node_uuid": "uuid-42",
            "period": "1", "phase": "a",
            "description": "test strato",
            "area": "A",
            "datazione": "II sec",
            "file_path": "",
        },
        position={"x": 100, "y": 50},
    )]
    state = EditorState(site="TestSite", rows=rows, nodes=nodes, edges=[],
                       pending_changes={}, group_by="period_phase")
    out = tmp_path / "out.graphml"
    write_extended_matrix_graphml(state, site_meta={"sito": "TestSite"}, epochs=[], out=out)
    xml = out.read_text(encoding="utf-8")
    assert '<node id="us_42"' in xml
    assert '<data key="d6">42</data>' in xml
    assert '<data key="d7">A</data>' in xml
    assert '<data key="d8">TestSite</data>' in xml
    assert '<data key="d9">US</data>' in xml
    assert '<data key="d16">' in xml and 'uuid-42' in xml
    assert '<y:ShapeNode>' in xml
```

- [ ] **Step 2: Run — expect failure**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_writer_extended_matrix.py::test_emits_us_node_with_keys -v`
Expected: failure.

- [ ] **Step 3: Implement `_render_us_nodes`**

Replace stub in `yed_writer.py`:

```python
def _render_us_nodes(state) -> str:
    """Emit each US node as child of the swimlane_root graph."""
    parts = []
    sito = state.site
    for el in state.nodes:
        if el.data.get("is_swimlane"):
            continue
        d = el.data
        nid = escape(str(d["id"]))
        us_num = d.get("us_number") or d.get("us") or ""
        unit_type = d.get("unit_type") or "US"
        node_uuid = d.get("node_uuid") or ""
        area = d.get("area") or ""
        periodo = d.get("period") or ""
        fase = d.get("phase") or ""
        rapporti = d.get("rapporti") or ""
        d_strat = d.get("description") or ""
        d_interp = d.get("d_interpretativa") or ""
        documentazione = d.get("file_path") or ""
        struttura = d.get("struttura") or ""
        attivita = d.get("attivita") or ""
        settore = d.get("settore") or ""
        ambient = d.get("ambient") or ""
        saggio = d.get("saggio") or ""
        quad_par = d.get("quad_par") or ""
        datazione = d.get("datazione") or ""
        pos = el.position or {"x": 0, "y": 0}
        x, y = pos.get("x", 0), pos.get("y", 0)
        color = d.get("color") or "#F0F0F0"
        border_color = d.get("border_color") or "#540909"
        border_style = d.get("border_style") or "solid"
        shape = d.get("shape") or "rectangle"

        parts.append(f'        <node id="{nid}">')
        parts.append(f'          <data key="d4"><![CDATA[{escape(str(node_uuid))}]]></data>')
        parts.append('          <data key="d5"/>')
        parts.append(f'          <data key="d6">{escape(str(us_num))}</data>')
        parts.append(f'          <data key="d7">{escape(str(area))}</data>')
        parts.append(f'          <data key="d8">{escape(sito)}</data>')
        parts.append(f'          <data key="d9">{escape(str(unit_type))}</data>')
        parts.append(f'          <data key="d10">{escape(str(periodo))}</data>')
        parts.append(f'          <data key="d11">{escape(str(fase))}</data>')
        parts.append(f'          <data key="d12"><![CDATA[{rapporti}]]></data>')
        parts.append(f'          <data key="d13">{escape(str(d_strat))}</data>')
        parts.append(f'          <data key="d14">{escape(str(d_interp))}</data>')
        parts.append(f'          <data key="d15">{escape(str(documentazione))}</data>')
        parts.append(f'          <data key="d16">{escape(str(node_uuid))}</data>')
        parts.append(f'          <data key="d17">{escape(str(struttura))}</data>')
        parts.append(f'          <data key="d18">{escape(str(attivita))}</data>')
        parts.append(f'          <data key="d19">{escape(str(settore))}</data>')
        parts.append(f'          <data key="d20">{escape(str(ambient))}</data>')
        parts.append(f'          <data key="d21">{escape(str(saggio))}</data>')
        parts.append(f'          <data key="d22">{escape(str(quad_par))}</data>')
        parts.append(f'          <data key="d23">{escape(str(datazione))}</data>')
        parts.append('          <data key="d31">')
        parts.append('            <y:ShapeNode>')
        parts.append(f'              <y:Geometry height="30.0" width="80.0" x="{x}" y="{y}"/>')
        parts.append(f'              <y:Fill color="{color}" transparent="false"/>')
        parts.append(f'              <y:BorderStyle color="{border_color}" type="{border_style}" width="3.0"/>')
        parts.append(f'              <y:NodeLabel>{escape(d.get("label", str(us_num)))}</y:NodeLabel>')
        parts.append(f'              <y:Shape type="{shape}"/>')
        parts.append('            </y:ShapeNode>')
        parts.append('          </data>')
        parts.append('        </node>')

    parts.append('      </graph>')  # close swimlane_root::graph
    parts.append('    </node>')     # close swimlane_root node
    return "\n".join(parts)
```

- [ ] **Step 4: Run — expect pass**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_writer_extended_matrix.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphml_io/yed_writer.py tests/unit/test_yed_writer_extended_matrix.py
git commit -m "feat(spec7): yed_writer emits per-US <node> with all 38 keys"
```

---

## Task 10: yEd writer — emit edges + golden file test

**Files:**
- Modify: `pyarchinit_mini/graphml_io/yed_writer.py`
- Create: `tests/fixtures/yed_graphml_outputs/golden_volterra_extmatrix.graphml`
- Test: `tests/unit/test_yed_writer_extended_matrix.py` (extended)

- [ ] **Step 1: Add failing test for edges**

Append to `tests/unit/test_yed_writer_extended_matrix.py`:

```python
def test_emits_edges(tmp_path):
    from pyarchinit_mini.harris_swimlane.row_provider import Row
    rows = [Row(row_id="row_p1_a", period_name="P1", phase_name="a",
               start_date=0, end_date=100, color="#FFAAAA", source="period_table")]
    nodes = [
        CytoscapeElement(data={"id": "us_1", "label": "US1", "parent": "row_p1_a",
            "unit_type": "US", "us": 1, "us_number": 1, "node_uuid": "u1"},
            position={"x": 0, "y": 0}),
        CytoscapeElement(data={"id": "us_2", "label": "US2", "parent": "row_p1_a",
            "unit_type": "US", "us": 2, "us_number": 2, "node_uuid": "u2"},
            position={"x": 100, "y": 50}),
    ]
    edges = [CytoscapeElement(data={"id": "e1", "source": "us_1",
        "target": "us_2", "label": "overlies"})]
    state = EditorState(site="TestSite", rows=rows, nodes=nodes, edges=edges,
                       pending_changes={}, group_by="period_phase")
    out = tmp_path / "out.graphml"
    write_extended_matrix_graphml(state, site_meta={"sito": "TestSite"}, epochs=[], out=out)
    xml = out.read_text(encoding="utf-8")
    assert '<edge id="e1" source="us_1" target="us_2"' in xml
    assert 'y:PolyLineEdge' in xml or 'y:GenericEdge' in xml
```

- [ ] **Step 2: Run — expect failure**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_writer_extended_matrix.py::test_emits_edges -v`
Expected: failure.

- [ ] **Step 3: Implement `_render_edges`**

Replace stub in `yed_writer.py`:

```python
def _render_edges(state) -> str:
    parts = []
    for el in state.edges:
        d = el.data
        eid = escape(str(d.get("id", "")))
        source = escape(str(d.get("source", "")))
        target = escape(str(d.get("target", "")))
        label = d.get("label", "")
        parts.append(f'    <edge id="{eid}" source="{source}" target="{target}">')
        parts.append(f'      <data key="d36">{escape(str(label))}</data>')
        parts.append('      <data key="d37">')
        parts.append('        <y:PolyLineEdge>')
        parts.append('          <y:Path sx="0.0" sy="0.0" tx="0.0" ty="0.0"/>')
        parts.append('          <y:LineStyle color="#000000" type="line" width="1.0"/>')
        parts.append('          <y:Arrows source="none" target="standard"/>')
        if label:
            parts.append(f'          <y:EdgeLabel>{escape(label)}</y:EdgeLabel>')
        parts.append('          <y:BendStyle smoothed="false"/>')
        parts.append('        </y:PolyLineEdge>')
        parts.append('      </data>')
        parts.append('    </edge>')
    return "\n".join(parts)
```

- [ ] **Step 4: Run — expect pass**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_writer_extended_matrix.py -v`
Expected: 5 passed.

- [ ] **Step 5: Generate golden file**

Run:

```bash
.venv/bin/python -c "
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState
from pyarchinit_mini.graphml_io.yed_writer import write_extended_matrix_graphml
eng = create_engine('sqlite:///tests/fixtures/databases/sqlite_volterra_30us_with_periods.db')
s = sessionmaker(bind=eng)()
state = SwimlaneState.load(s, 'Volterra')
write_extended_matrix_graphml(state, site_meta={'sito':'Volterra'}, epochs=[],
    out='tests/fixtures/yed_graphml_outputs/golden_volterra_extmatrix.graphml')
print('golden written')
"
```
Expected: `golden written`.

- [ ] **Step 6: Add golden file regression test**

Append to `tests/unit/test_yed_writer_extended_matrix.py`:

```python
def test_golden_volterra_stable(tmp_path):
    """Regression: regenerate golden + diff against committed copy."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState

    eng = create_engine("sqlite:///tests/fixtures/databases/sqlite_volterra_30us_with_periods.db")
    s = sessionmaker(bind=eng)()
    state = SwimlaneState.load(s, "Volterra")
    out = tmp_path / "live.graphml"
    write_extended_matrix_graphml(state, site_meta={"sito": "Volterra"}, epochs=[], out=out)
    golden = Path("tests/fixtures/yed_graphml_outputs/golden_volterra_extmatrix.graphml").read_text()
    assert out.read_text().count("<node") == golden.count("<node")
    assert out.read_text().count("<edge") == golden.count("<edge")
    assert out.read_text().count("<y:Row") == golden.count("<y:Row")
```

- [ ] **Step 7: Run all yed_writer tests**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_writer_extended_matrix.py -v`
Expected: 6 passed.

- [ ] **Step 8: Commit**

```bash
git add pyarchinit_mini/graphml_io/yed_writer.py \
        tests/unit/test_yed_writer_extended_matrix.py \
        tests/fixtures/yed_graphml_outputs/golden_volterra_extmatrix.graphml
git commit -m "feat(spec7): yed_writer emits edges + golden file regression"
```

---

## Task 11: `/api/export/<site>/yed-graphml` accepts `group_by`

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py`
- Test: `tests/integration/test_swimlane_group_by.py` (extended)

- [ ] **Step 1: Write failing test**

Append:

```python
def test_api_export_yed_with_group_by(tmp_path, monkeypatch):
    from flask import Flask
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{DB_FIX}")
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(harris_creator_bp)
    cli = app.test_client()

    r = cli.get("/harris-creator/api/export/Volterra/yed-graphml?group_by=none")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "YED_TABLE_NODE" in body
    assert '<y:Row id="row_default"' in body
```

- [ ] **Step 2: Run — expect failure**

Expected: 200 but content uses old `write_yed_graphml` placeholder or rows not aligned.

- [ ] **Step 3: Update `api_export_yed`**

Replace body in `harris_creator_routes.py`:

```python
@harris_creator_bp.get("/api/export/<site>/yed-graphml")
def api_export_yed(site: str):
    from pyarchinit_mini.graphml_io.yed_writer import write_extended_matrix_graphml
    group_by = request.args.get("group_by", "period_phase")
    try:
        session = _get_session()
        state = SwimlaneState.load(session, site, group_by=group_by)
        epochs = []  # populate from periodizzazione_table in Task 12
        out_dir = _Path("data/exports/harris_yed")
        out_dir.mkdir(parents=True, exist_ok=True)
        site_slug = slugify(site)
        out_path = out_dir / f"{site_slug}-extmatrix.graphml"
        write_extended_matrix_graphml(
            state, site_meta={"sito": site}, epochs=epochs, out=out_path,
        )
        # ... existing index.json upsert stays the same ...
        return _send_file(
            out_path.resolve(), as_attachment=True,
            download_name=f"{site_slug}-extmatrix.graphml",
            mimetype="application/xml",
        )
    except YEDWriterError as e:
        return jsonify({"error": "writer", "message": str(e)}), 500
    except ValueError as e:
        return jsonify({"error": "validation", "message": str(e)}), 400
```

- [ ] **Step 4: Run test — expect pass**

Run: `.venv/bin/python -m pytest tests/integration/test_swimlane_group_by.py::test_api_export_yed_with_group_by -v`
Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/harris_creator_routes.py \
        tests/integration/test_swimlane_group_by.py
git commit -m "feat(spec7): /api/export/<site>/yed-graphml?group_by=X"
```

---

## Task 12: Populate `epochs` from `periodizzazione_table` on export

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py`
- Test: `tests/integration/test_swimlane_group_by.py` (extended)

- [ ] **Step 1: Add failing test**

```python
def test_export_includes_epochs_meta(tmp_path, monkeypatch):
    from flask import Flask
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{DB_FIX}")
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(harris_creator_bp)
    cli = app.test_client()
    r = cli.get("/harris-creator/api/export/Volterra/yed-graphml")
    body = r.get_data(as_text=True)
    # Volterra fixture has periods → epochs_meta payload should appear
    assert 'key="d0"' in body
```

- [ ] **Step 2: Add helper `_load_epochs(session, site)` in `harris_creator_routes.py`**

```python
def _load_epochs(session, site: str) -> list[dict]:
    """Load periodizzazione rows for the site to feed yed_writer epochs_meta."""
    rows = session.execute(text(
        "SELECT DISTINCT periodo_iniziale, fase_iniziale, datazione_estesa "
        "FROM periodizzazione_table WHERE sito = :s AND periodo_iniziale IS NOT NULL"
    ), {"s": site}).fetchall()
    out = []
    for r in rows:
        out.append({
            "name": f"Period{r[0]}" + (f"_phase{r[1]}" if r[1] else ""),
            "periodo": r[0] or "",
            "fase": r[1] or "",
            "datazione_estesa": r[2] or "",
        })
    return out
```

- [ ] **Step 3: Wire it in `api_export_yed`**

Replace `epochs = []` with `epochs = _load_epochs(session, site)`.

- [ ] **Step 4: Run — expect pass**

Run: `.venv/bin/python -m pytest tests/integration/test_swimlane_group_by.py::test_export_includes_epochs_meta -v`
Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/harris_creator_routes.py \
        tests/integration/test_swimlane_group_by.py
git commit -m "feat(spec7): export populates epochs_meta from periodizzazione_table"
```

---

## Task 13: yEd importer — XML parser

**Files:**
- Create: `pyarchinit_mini/graphml_io/yed_importer.py`
- Modify: `pyarchinit_mini/harris_swimlane/exceptions.py`
- Test: `tests/unit/test_yed_importer_parse.py`

- [ ] **Step 1: Add exception class**

Open `pyarchinit_mini/harris_swimlane/exceptions.py` and append:

```python
class YEDImporterError(HarrisSwimlaneError):
    """Base for yEd import errors (parsing, validation, application)."""


class YEDImportValidationError(YEDImporterError):
    """Caller-facing validation error during build_import_plan."""
```

- [ ] **Step 2: Write failing parser tests**

Create `tests/unit/test_yed_importer_parse.py`:

```python
"""Tests for yed_importer.parse_extended_matrix."""
from pathlib import Path
import pytest

from pyarchinit_mini.graphml_io.yed_importer import parse_extended_matrix
from pyarchinit_mini.harris_swimlane.exceptions import YEDImporterError

FIX = Path(__file__).parent.parent / "fixtures" / "yed_graphml"


def test_parse_minimal_returns_expected_nodes():
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    assert len(parsed.nodes) == 3
    assert parsed.nodes[0]["us"] == "1"
    assert parsed.nodes[0]["sito"] == "TestSite"
    assert parsed.nodes[0]["unita_tipo"] == "US"
    assert parsed.nodes[2]["unita_tipo"] == "USVs"


def test_parse_minimal_returns_edges():
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    assert len(parsed.edges) == 2
    e = parsed.edges[0]
    assert e["us_from"] == "1" and e["us_to"] == "2"


def test_parse_minimal_returns_epochs():
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    assert len(parsed.epochs) == 1
    assert parsed.epochs[0]["name"] == "P1"


def test_parse_vanilla_yed_raises():
    with pytest.raises(YEDImporterError, match="not a pyarchinit"):
        parse_extended_matrix(FIX / "vanilla_yed.graphml")


def test_parse_malformed_raises():
    with pytest.raises(YEDImporterError):
        parse_extended_matrix(FIX / "malformed.graphml")


def test_parse_reference_file_runs():
    """Reference fixture parses without error and returns ≥10 nodes."""
    parsed = parse_extended_matrix(FIX / "extended_matrix_pyarchinit.graphml")
    assert len(parsed.nodes) >= 10
```

- [ ] **Step 3: Run — expect failure**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_importer_parse.py -v`
Expected: failures (module not implemented).

- [ ] **Step 4: Implement `yed_importer.py` parser**

Create `pyarchinit_mini/graphml_io/yed_importer.py`:

```python
"""yEd GraphML importer for pyarchinit Extended Matrix files.

Pipeline:
  1. parse_extended_matrix(path) → ParsedGraphML (raw extraction)
  2. build_import_plan(parsed, session) → ImportPlan (DB diff)
  3. apply_import_plan(plan, session) → ImportResult (commit)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from lxml import etree

from pyarchinit_mini.harris_swimlane.exceptions import (
    YEDImporterError, YEDImportValidationError,
)
from pyarchinit_mini.graphml_io.yed_keys import KEY_BY_ATTR_NAME, US_NODE_FIELDS


@dataclass
class ParsedGraphML:
    epochs: list[dict] = field(default_factory=list)
    nodes: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)


NS = {
    "g": "http://graphml.graphdrawing.org/xmlns",
    "y": "http://www.yworks.com/xml/graphml",
}


def parse_extended_matrix(path: Path) -> ParsedGraphML:
    """Parse a pyarchinit Extended Matrix yEd GraphML file.

    Raises YEDImporterError if the file is malformed or not pyarchinit-shaped.
    """
    path = Path(path)
    try:
        tree = etree.parse(str(path))
    except etree.XMLSyntaxError as e:
        raise YEDImporterError(f"malformed XML: {e}") from e

    root = tree.getroot()
    # Build attr_name → key_id map by reading <key> elements.
    key_attr_to_id: dict[str, str] = {}
    key_id_to_attr: dict[str, str] = {}
    for k in root.findall("g:key", NS):
        kid = k.get("id")
        attr = k.get("attr.name")
        if kid and attr:
            key_attr_to_id[attr] = kid
            key_id_to_attr[kid] = attr

    # Validate: must have at least pyarchinit.us key declared.
    if "pyarchinit.us" not in key_attr_to_id:
        raise YEDImporterError("not a pyarchinit Extended Matrix file (no pyarchinit.us key)")

    parsed = ParsedGraphML()

    # Graph-level data (epochs_meta).
    graphs = root.findall(".//g:graph", NS)
    for g in graphs:
        for d in g.findall("g:data", NS):
            if d.get("key") == key_attr_to_id.get("pyarchinit.epochs_meta"):
                txt = (d.text or "").strip()
                if txt:
                    try:
                        parsed.epochs = json.loads(txt)
                    except json.JSONDecodeError:
                        pass  # warning will surface in build_import_plan
                break

    # Node-level data — index node_id → us_number for later edge mapping.
    node_id_to_us: dict[str, str] = {}
    for n in root.findall(".//g:node", NS):
        node_id = n.get("id", "")
        rec: dict = {"_node_id": node_id}
        for d in n.findall("g:data", NS):
            kid = d.get("key", "")
            attr = key_id_to_attr.get(kid)
            if not attr:
                continue
            if attr.startswith("pyarchinit."):
                short = attr.split("pyarchinit.", 1)[1]
                rec[short] = (d.text or "").strip()
            elif attr == "EMID":
                rec.setdefault("node_uuid", (d.text or "").strip())
        # Only nodes with pyarchinit.us are stratigraphic US records.
        if rec.get("us"):
            parsed.nodes.append(rec)
            node_id_to_us[node_id] = rec["us"]

    # Edges — only those connecting recognised US nodes.
    for e in root.findall(".//g:edge", NS):
        src = e.get("source", "")
        tgt = e.get("target", "")
        us_from = node_id_to_us.get(src)
        us_to = node_id_to_us.get(tgt)
        if not us_from or not us_to:
            continue
        rel = ""
        for d in e.findall("g:data", NS):
            kid = d.get("key", "")
            attr = key_id_to_attr.get(kid, "")
            if attr == "description":
                rel = (d.text or "").strip()
                break
        parsed.edges.append({
            "us_from": us_from, "us_to": us_to, "type": rel,
        })

    return parsed
```

- [ ] **Step 5: Run — expect pass**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_importer_parse.py -v`
Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/graphml_io/yed_importer.py \
        pyarchinit_mini/harris_swimlane/exceptions.py \
        tests/unit/test_yed_importer_parse.py
git commit -m "feat(spec7): yed_importer.parse_extended_matrix (XML parser)"
```

---

## Task 14: yEd importer — `build_import_plan`

**Files:**
- Modify: `pyarchinit_mini/graphml_io/yed_importer.py`
- Test: `tests/unit/test_yed_importer_plan.py`

- [ ] **Step 1: Write failing tests**

Create `tests/unit/test_yed_importer_plan.py`:

```python
"""Tests for build_import_plan — DB diff + conflict detection."""
import sqlite3
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.graphml_io.yed_importer import (
    parse_extended_matrix, build_import_plan,
)


@pytest.fixture
def session(tmp_path):
    db = tmp_path / "plan.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
    CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY, sito TEXT);
    CREATE TABLE us_table (
      id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
      d_stratigrafica TEXT, datazione TEXT, file_path TEXT,
      rapporti TEXT, node_uuid TEXT,
      periodo_iniziale TEXT, fase_iniziale TEXT,
      struttura TEXT, attivita TEXT, settore TEXT,
      ambient TEXT, saggio TEXT, quad_par TEXT
    );
    CREATE TABLE periodizzazione_table (
      id_periodizzazione INTEGER PRIMARY KEY,
      sito TEXT, periodo_iniziale TEXT, fase_iniziale TEXT,
      datazione_estesa TEXT
    );
    CREATE TABLE us_relationships_table (
      id_relationship INTEGER PRIMARY KEY,
      sito TEXT, us_from TEXT, us_to TEXT, relationship_type TEXT
    );
    """)
    conn.commit(); conn.close()
    eng = create_engine(f"sqlite:///{db}")
    s = sessionmaker(bind=eng)()
    yield s
    s.close()


FIX = Path(__file__).parent.parent / "fixtures" / "yed_graphml"


def test_plan_marks_site_da_creare(session):
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan = build_import_plan(parsed, session)
    assert plan.sites == [{"sito": "TestSite", "da_creare": True}]


def test_plan_all_us_action_create_on_empty_db(session):
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan = build_import_plan(parsed, session)
    assert len(plan.us_records) == 3
    assert all(r["action"] == "create" for r in plan.us_records)


def test_plan_marks_update_when_uuid_exists(session):
    from sqlalchemy import text
    session.execute(text(
        "INSERT INTO us_table (sito, us, unita_tipo, node_uuid) "
        "VALUES ('TestSite', '1', 'US', 'uuid-001')"
    ))
    session.commit()
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan = build_import_plan(parsed, session)
    us1 = next(r for r in plan.us_records if r["us"] == "1")
    assert us1["action"] == "update"


def test_plan_includes_periodizations(session):
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan = build_import_plan(parsed, session)
    assert len(plan.periodizations) >= 1


def test_plan_includes_relationships(session):
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan = build_import_plan(parsed, session)
    assert len(plan.relationships) == 2
```

- [ ] **Step 2: Run — expect failure**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_importer_plan.py -v`
Expected: failure (`build_import_plan` does not exist).

- [ ] **Step 3: Implement `build_import_plan`**

Append to `yed_importer.py`:

```python
from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass
class ImportPlan:
    sites: list[dict] = field(default_factory=list)
    periodizations: list[dict] = field(default_factory=list)
    us_records: list[dict] = field(default_factory=list)
    relationships: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)


def build_import_plan(parsed: ParsedGraphML, session: Session) -> ImportPlan:
    plan = ImportPlan()
    if not parsed.nodes:
        raise YEDImportValidationError("File contains no US nodes")
    sito_set = {n.get("sito") for n in parsed.nodes if n.get("sito")}
    if not sito_set:
        raise YEDImportValidationError("No pyarchinit.sito on any node")

    # Sites
    for sito in sito_set:
        existing = session.execute(text(
            "SELECT 1 FROM site_table WHERE sito = :s LIMIT 1"
        ), {"s": sito}).fetchone()
        plan.sites.append({"sito": sito, "da_creare": existing is None})

    # Periodizations from epochs_meta
    seen_pz = set()
    for ep in parsed.epochs:
        for sito in sito_set:
            key = (sito, ep.get("periodo"), ep.get("fase"))
            if key in seen_pz:
                continue
            seen_pz.add(key)
            existing = session.execute(text(
                "SELECT 1 FROM periodizzazione_table "
                "WHERE sito=:s AND periodo_iniziale=:p AND fase_iniziale=:f LIMIT 1"
            ), {"s": sito, "p": ep.get("periodo", ""), "f": ep.get("fase", "")}).fetchone()
            plan.periodizations.append({
                "sito": sito,
                "periodo": ep.get("periodo", ""),
                "fase": ep.get("fase", ""),
                "datazione_estesa": ep.get("datazione_estesa", ""),
                "action": "update" if existing else "create",
            })

    # US records — upsert by node_uuid, fallback (sito, us)
    for n in parsed.nodes:
        sito = n.get("sito")
        us = n.get("us")
        uuid = n.get("node_uuid") or n.get("EMID") or ""
        existing = None
        if uuid:
            existing = session.execute(text(
                "SELECT id_us FROM us_table WHERE node_uuid = :u LIMIT 1"
            ), {"u": uuid}).fetchone()
        if not existing:
            existing = session.execute(text(
                "SELECT id_us FROM us_table WHERE sito = :s AND us = :u LIMIT 1"
            ), {"s": sito, "u": us}).fetchone()
        action = "update" if existing else "create"
        plan.us_records.append({
            "sito": sito, "us": us, "node_uuid": uuid,
            "unita_tipo": n.get("unita_tipo", "US"),
            "area": n.get("area", ""),
            "periodo_iniziale": n.get("periodo_iniziale", ""),
            "fase_iniziale": n.get("fase_iniziale", ""),
            "d_stratigrafica": n.get("d_stratigrafica", ""),
            "rapporti": n.get("rapporti", ""),
            "struttura": n.get("struttura", ""),
            "attivita": n.get("attivita", ""),
            "settore": n.get("settore", ""),
            "ambient": n.get("ambient", ""),
            "saggio": n.get("saggio", ""),
            "quad_par": n.get("quad_par", ""),
            "datazione": n.get("datazione_estesa", ""),
            "action": action,
        })

    # Relationships
    for e in parsed.edges:
        plan.relationships.append({
            "sito": list(sito_set)[0] if len(sito_set) == 1 else "",
            "us_from": e["us_from"],
            "us_to": e["us_to"],
            "type": e["type"],
            "action": "create",
        })

    return plan
```

- [ ] **Step 4: Run — expect pass**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_importer_plan.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphml_io/yed_importer.py \
        tests/unit/test_yed_importer_plan.py
git commit -m "feat(spec7): yed_importer.build_import_plan (DB diff + upsert)"
```

---

## Task 15: yEd importer — `apply_import_plan`

**Files:**
- Modify: `pyarchinit_mini/graphml_io/yed_importer.py`
- Test: `tests/unit/test_yed_importer_plan.py` (extended)

- [ ] **Step 1: Add failing test**

Append:

```python
def test_apply_inserts_new_records(session):
    from sqlalchemy import text
    from pyarchinit_mini.graphml_io.yed_importer import apply_import_plan
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan = build_import_plan(parsed, session)
    result = apply_import_plan(plan, session)
    assert result.us_created == 3
    assert result.sites_created == 1
    count = session.execute(text("SELECT COUNT(*) FROM us_table")).scalar()
    assert count == 3


def test_apply_is_idempotent(session):
    from pyarchinit_mini.graphml_io.yed_importer import apply_import_plan
    parsed = parse_extended_matrix(FIX / "minimal.graphml")
    plan1 = build_import_plan(parsed, session)
    apply_import_plan(plan1, session)

    plan2 = build_import_plan(parsed, session)
    result2 = apply_import_plan(plan2, session)
    assert result2.us_created == 0
    assert result2.us_updated == 3
```

- [ ] **Step 2: Run — expect failure**

Expected: `apply_import_plan` does not exist.

- [ ] **Step 3: Implement `apply_import_plan`**

Append to `yed_importer.py`:

```python
@dataclass
class ImportResult:
    sites_created: int = 0
    sites_updated: int = 0
    periodizations_created: int = 0
    periodizations_updated: int = 0
    us_created: int = 0
    us_updated: int = 0
    us_skipped: int = 0
    relationships_created: int = 0
    duration_ms: int = 0
    errors: list[str] = field(default_factory=list)


def apply_import_plan(plan: ImportPlan, session: Session) -> ImportResult:
    """Apply the plan in one transaction. Best-effort auto-regen after."""
    import time
    start = time.time()
    result = ImportResult()
    try:
        for s in plan.sites:
            if s["da_creare"]:
                session.execute(text(
                    "INSERT INTO site_table (sito) VALUES (:s)"
                ), {"s": s["sito"]})
                result.sites_created += 1

        for p in plan.periodizations:
            if p["action"] == "create":
                session.execute(text(
                    "INSERT INTO periodizzazione_table "
                    "(sito, periodo_iniziale, fase_iniziale, datazione_estesa) "
                    "VALUES (:s, :p, :f, :d)"
                ), {"s": p["sito"], "p": p["periodo"], "f": p["fase"],
                    "d": p["datazione_estesa"]})
                result.periodizations_created += 1
            else:
                result.periodizations_updated += 1

        for r in plan.us_records:
            if r["action"] == "create":
                session.execute(text(
                    "INSERT INTO us_table (sito, area, us, unita_tipo, "
                    "node_uuid, periodo_iniziale, fase_iniziale, "
                    "d_stratigrafica, rapporti, datazione, "
                    "struttura, attivita, settore, ambient, saggio, quad_par) "
                    "VALUES (:sito, :area, :us, :ut, :uuid, :p, :f, :ds, :rap, :dz, "
                    ":struttura, :attivita, :settore, :ambient, :saggio, :quad_par)"
                ), {
                    "sito": r["sito"], "area": r["area"], "us": r["us"],
                    "ut": r["unita_tipo"], "uuid": r["node_uuid"] or None,
                    "p": r["periodo_iniziale"], "f": r["fase_iniziale"],
                    "ds": r["d_stratigrafica"], "rap": r["rapporti"],
                    "dz": r["datazione"],
                    "struttura": r["struttura"], "attivita": r["attivita"],
                    "settore": r["settore"], "ambient": r["ambient"],
                    "saggio": r["saggio"], "quad_par": r["quad_par"],
                })
                result.us_created += 1
            else:
                # Update by node_uuid if present, else by (sito, us)
                if r["node_uuid"]:
                    session.execute(text(
                        "UPDATE us_table SET sito=:sito, area=:area, us=:us, "
                        "unita_tipo=:ut, periodo_iniziale=:p, fase_iniziale=:f, "
                        "d_stratigrafica=:ds, rapporti=:rap, datazione=:dz, "
                        "struttura=:struttura, attivita=:attivita, settore=:settore, "
                        "ambient=:ambient, saggio=:saggio, quad_par=:quad_par "
                        "WHERE node_uuid = :uuid"
                    ), {**{k: r[k] for k in [
                        "sito", "area", "us", "ds", "rap", "dz",
                        "struttura", "attivita", "settore", "ambient", "saggio", "quad_par",
                    ]}, "ut": r["unita_tipo"],
                       "p": r["periodo_iniziale"], "f": r["fase_iniziale"],
                       "uuid": r["node_uuid"]})
                else:
                    session.execute(text(
                        "UPDATE us_table SET unita_tipo=:ut, periodo_iniziale=:p, "
                        "fase_iniziale=:f, d_stratigrafica=:ds, rapporti=:rap, "
                        "datazione=:dz, struttura=:struttura, attivita=:attivita, "
                        "settore=:settore, ambient=:ambient, saggio=:saggio, "
                        "quad_par=:quad_par WHERE sito=:sito AND us=:us"
                    ), {"ut": r["unita_tipo"],
                        "p": r["periodo_iniziale"], "f": r["fase_iniziale"],
                        "ds": r["d_stratigrafica"], "rap": r["rapporti"],
                        "dz": r["datazione"],
                        "struttura": r["struttura"], "attivita": r["attivita"],
                        "settore": r["settore"], "ambient": r["ambient"],
                        "saggio": r["saggio"], "quad_par": r["quad_par"],
                        "sito": r["sito"], "us": r["us"]})
                result.us_updated += 1

        seen_rel = set()
        for rel in plan.relationships:
            key = (rel["sito"], rel["us_from"], rel["us_to"], rel["type"])
            if key in seen_rel:
                continue
            seen_rel.add(key)
            # Dedupe against DB
            exists = session.execute(text(
                "SELECT 1 FROM us_relationships_table "
                "WHERE sito=:s AND us_from=:f AND us_to=:t AND relationship_type=:r LIMIT 1"
            ), {"s": rel["sito"], "f": rel["us_from"], "t": rel["us_to"], "r": rel["type"]}).fetchone()
            if not exists:
                session.execute(text(
                    "INSERT INTO us_relationships_table "
                    "(sito, us_from, us_to, relationship_type) "
                    "VALUES (:s, :f, :t, :r)"
                ), {"s": rel["sito"], "f": rel["us_from"], "t": rel["us_to"], "r": rel["type"]})
                result.relationships_created += 1
        session.commit()
    except Exception as e:
        session.rollback()
        result.errors.append(str(e))

    result.duration_ms = int((time.time() - start) * 1000)
    return result
```

- [ ] **Step 4: Run — expect pass**

Run: `.venv/bin/python -m pytest tests/unit/test_yed_importer_plan.py -v`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphml_io/yed_importer.py tests/unit/test_yed_importer_plan.py
git commit -m "feat(spec7): yed_importer.apply_import_plan (transactional + idempotent)"
```

---

## Task 16: `/import-graphml/` blueprint — index + preview

**Files:**
- Create: `pyarchinit_mini/web_interface/yed_import_routes.py`
- Create: `pyarchinit_mini/web_interface/templates/yed_import/index.html`
- Modify: `pyarchinit_mini/web_interface/app.py`
- Test: `tests/integration/test_yed_import_routes.py`

- [ ] **Step 1: Write failing integration test**

Create `tests/integration/test_yed_import_routes.py`:

```python
"""Integration tests for /import-graphml/ endpoints."""
import io
from pathlib import Path
import pytest

from flask import Flask

from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
from pyarchinit_mini.web_interface.yed_import_routes import yed_import_bp


FIX = Path(__file__).parent.parent / "fixtures" / "yed_graphml"


@pytest.fixture
def client(tmp_path, monkeypatch):
    from sqlalchemy import create_engine, text
    from pyarchinit_mini.models.base import Base
    db_path = tmp_path / "imp.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    eng = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(eng)
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"
    app.register_blueprint(harris_creator_bp)
    app.register_blueprint(yed_import_bp)
    yield app.test_client()


def test_index_renders(client):
    r = client.get("/import-graphml/")
    assert r.status_code == 200
    assert b"Import GraphML" in r.data or b"yEd" in r.data


def test_preview_minimal_file(client):
    data = (FIX / "minimal.graphml").read_bytes()
    r = client.post(
        "/import-graphml/preview",
        data={"file": (io.BytesIO(data), "minimal.graphml")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "3" in body  # 3 US created
```

- [ ] **Step 2: Run — expect failure**

Expected: `cannot import yed_import_bp`.

- [ ] **Step 3: Create the blueprint**

Create `pyarchinit_mini/web_interface/yed_import_routes.py`:

```python
"""Blueprint for /import-graphml/ — upload + preview + apply yEd Extended Matrix."""
from __future__ import annotations

import os
import uuid
from pathlib import Path

from flask import (
    Blueprint, current_app, request, render_template, jsonify,
    session as flask_session, redirect, url_for,
)

from pyarchinit_mini.graphml_io.yed_importer import (
    parse_extended_matrix, build_import_plan, apply_import_plan,
)
from pyarchinit_mini.harris_swimlane.exceptions import (
    YEDImporterError, YEDImportValidationError,
)


yed_import_bp = Blueprint(
    "yed_import", __name__, url_prefix="/import-graphml",
    template_folder="templates",
)

_PLAN_CACHE: dict[str, dict] = {}


def _get_session():
    if hasattr(current_app, "db_manager"):
        return current_app.db_manager.connection.get_session()
    from pyarchinit_mini.database.connection import DatabaseConnection
    db_url = os.getenv("DATABASE_URL", "sqlite:///pyarchinit_mini.db")
    return DatabaseConnection.from_url(db_url).get_session()


@yed_import_bp.get("/")
def index():
    return render_template("yed_import/index.html")


@yed_import_bp.post("/preview")
def preview():
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify({"error": "missing_file"}), 400
    tmpdir = Path("/tmp/yed_import")
    tmpdir.mkdir(parents=True, exist_ok=True)
    upload_path = tmpdir / f"{uuid.uuid4().hex}.graphml"
    f.save(str(upload_path))

    try:
        with _get_session() as session:
            parsed = parse_extended_matrix(upload_path)
            plan = build_import_plan(parsed, session)
    except (YEDImporterError, YEDImportValidationError) as e:
        return jsonify({"error": "import", "message": str(e)}), 400
    finally:
        try: upload_path.unlink()
        except Exception: pass

    plan_id = uuid.uuid4().hex
    _PLAN_CACHE[plan_id] = {
        "sites": plan.sites,
        "periodizations": plan.periodizations,
        "us_records": plan.us_records,
        "relationships": plan.relationships,
        "warnings": plan.warnings,
        "conflicts": plan.conflicts,
    }
    return render_template("yed_import/preview.html", plan_id=plan_id, plan=plan)


@yed_import_bp.post("/apply")
def apply():
    plan_id = request.form.get("plan_id", "")
    raw = _PLAN_CACHE.pop(plan_id, None)
    if not raw:
        return jsonify({"error": "plan_expired"}), 400
    from pyarchinit_mini.graphml_io.yed_importer import ImportPlan
    plan = ImportPlan(**raw)
    with _get_session() as session:
        result = apply_import_plan(plan, session)
    return render_template("yed_import/result.html", result=result)
```

- [ ] **Step 4: Create the index template**

Create `pyarchinit_mini/web_interface/templates/yed_import/index.html`:

```html
{% extends "base.html" %}
{% block title %}{{ _('Import GraphML') }}{% endblock %}
{% block content %}
<div class="container py-4">
  <h1><i class="fas fa-file-import"></i> {{ _('Import yEd GraphML') }}</h1>
  <p class="text-muted">
    {{ _('Upload an Extended Matrix .graphml exported from pyarchinit QGIS or this editor to populate the site / US / periodizzazione tables. Preview before apply.') }}
  </p>
  <form action="{{ url_for('yed_import.preview') }}" method="post"
        enctype="multipart/form-data" class="card p-4">
    <div class="mb-3">
      <label class="form-label">{{ _('GraphML file') }}</label>
      <input type="file" name="file" accept=".graphml,application/xml" required
             class="form-control"/>
    </div>
    <button type="submit" class="btn btn-primary">
      <i class="fas fa-search"></i> {{ _('Preview') }}
    </button>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 5: Register the blueprint in `app.py`**

In `pyarchinit_mini/web_interface/app.py`, after the existing blueprint registrations:

```python
from pyarchinit_mini.web_interface.yed_import_routes import yed_import_bp
app.register_blueprint(yed_import_bp)
```

- [ ] **Step 6: Create a stub preview.html (Task 17 fills it)**

Create `pyarchinit_mini/web_interface/templates/yed_import/preview.html`:

```html
{% extends "base.html" %}
{% block content %}
<div class="container py-4">
  <h2>Preview</h2>
  <p>plan_id: {{ plan_id }}</p>
  <p>{{ plan.us_records|length }} US records</p>
</div>
{% endblock %}
```

- [ ] **Step 7: Run tests**

Run: `.venv/bin/python -m pytest tests/integration/test_yed_import_routes.py::test_index_renders tests/integration/test_yed_import_routes.py::test_preview_minimal_file -v`
Expected: 2 passed.

- [ ] **Step 8: Commit**

```bash
git add pyarchinit_mini/web_interface/yed_import_routes.py \
        pyarchinit_mini/web_interface/templates/yed_import/index.html \
        pyarchinit_mini/web_interface/templates/yed_import/preview.html \
        pyarchinit_mini/web_interface/app.py \
        tests/integration/test_yed_import_routes.py
git commit -m "feat(spec7): /import-graphml/ blueprint (index + preview + apply)"
```

---

## Task 17: Preview + result templates

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/yed_import/preview.html`
- Create: `pyarchinit_mini/web_interface/templates/yed_import/result.html`
- Test: `tests/integration/test_yed_import_routes.py` (extended)

- [ ] **Step 1: Add apply test**

Append:

```python
def test_apply_end_to_end(client):
    import io
    data = (FIX / "minimal.graphml").read_bytes()
    r = client.post(
        "/import-graphml/preview",
        data={"file": (io.BytesIO(data), "minimal.graphml")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    import re
    m = re.search(r'name="plan_id"\s+value="([0-9a-f]+)"', body)
    assert m, body
    plan_id = m.group(1)

    r2 = client.post(
        "/import-graphml/apply",
        data={"plan_id": plan_id},
    )
    assert r2.status_code == 200
    assert b"3" in r2.data  # 3 US created
```

- [ ] **Step 2: Replace preview template content**

Rewrite `templates/yed_import/preview.html`:

```html
{% extends "base.html" %}
{% block title %}{{ _('Import Preview') }}{% endblock %}
{% block content %}
<div class="container py-4">
  <h1><i class="fas fa-eye"></i> {{ _('Import Preview') }}</h1>

  <div class="card mb-3">
    <div class="card-body">
      <h5>{{ _('Sites') }}</h5>
      <ul>
        {% for s in plan.sites %}
          <li>{{ s.sito }} — {% if s.da_creare %}<span class="badge bg-success">{{ _('to create') }}</span>{% else %}<span class="badge bg-secondary">{{ _('exists') }}</span>{% endif %}</li>
        {% endfor %}
      </ul>
    </div>
  </div>

  <div class="card mb-3">
    <div class="card-body">
      <h5>{{ _('Periodizations') }} ({{ plan.periodizations|length }})</h5>
      <p>{{ plan.periodizations|selectattr('action','equalto','create')|list|length }} {{ _('to create') }},
         {{ plan.periodizations|selectattr('action','equalto','update')|list|length }} {{ _('to update') }}</p>
    </div>
  </div>

  <div class="card mb-3">
    <div class="card-body">
      <h5>{{ _('US records') }} ({{ plan.us_records|length }})</h5>
      <p>{{ plan.us_records|selectattr('action','equalto','create')|list|length }} {{ _('to create') }},
         {{ plan.us_records|selectattr('action','equalto','update')|list|length }} {{ _('to update') }}</p>
    </div>
  </div>

  <div class="card mb-3">
    <div class="card-body">
      <h5>{{ _('Relationships') }} ({{ plan.relationships|length }})</h5>
    </div>
  </div>

  {% if plan.warnings %}
  <div class="alert alert-warning">
    <strong>{{ _('Warnings') }}:</strong>
    <ul>{% for w in plan.warnings %}<li>{{ w }}</li>{% endfor %}</ul>
  </div>
  {% endif %}

  {% if plan.conflicts %}
  <div class="alert alert-danger">
    <strong>{{ _('Conflicts') }}:</strong>
    <ul>{% for c in plan.conflicts %}<li>{{ c }}</li>{% endfor %}</ul>
  </div>
  {% endif %}

  <form action="{{ url_for('yed_import.apply') }}" method="post">
    <input type="hidden" name="plan_id" value="{{ plan_id }}"/>
    <button type="submit" class="btn btn-primary">
      <i class="fas fa-check"></i> {{ _('Apply') }}
    </button>
    <a href="{{ url_for('yed_import.index') }}" class="btn btn-outline-secondary">
      {{ _('Cancel') }}
    </a>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 3: Create the result template**

Create `templates/yed_import/result.html`:

```html
{% extends "base.html" %}
{% block title %}{{ _('Import Result') }}{% endblock %}
{% block content %}
<div class="container py-4">
  <h1><i class="fas fa-check-circle text-success"></i> {{ _('Import Result') }}</h1>

  {% if result.errors %}
  <div class="alert alert-danger">
    <strong>{{ _('Errors') }}:</strong>
    <ul>{% for e in result.errors %}<li>{{ e }}</li>{% endfor %}</ul>
  </div>
  {% endif %}

  <ul class="list-group mb-3">
    <li class="list-group-item">{{ _('Sites created') }}: {{ result.sites_created }}</li>
    <li class="list-group-item">{{ _('Periodizations created') }}: {{ result.periodizations_created }}, {{ _('updated') }}: {{ result.periodizations_updated }}</li>
    <li class="list-group-item">{{ _('US created') }}: {{ result.us_created }}, {{ _('updated') }}: {{ result.us_updated }}</li>
    <li class="list-group-item">{{ _('Relationships created') }}: {{ result.relationships_created }}</li>
    <li class="list-group-item">{{ _('Duration') }}: {{ result.duration_ms }} ms</li>
  </ul>

  <a href="{{ url_for('yed_import.index') }}" class="btn btn-primary">
    {{ _('Import another file') }}
  </a>
</div>
{% endblock %}
```

- [ ] **Step 4: Run all import tests**

Run: `.venv/bin/python -m pytest tests/integration/test_yed_import_routes.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/yed_import/preview.html \
        pyarchinit_mini/web_interface/templates/yed_import/result.html \
        tests/integration/test_yed_import_routes.py
git commit -m "feat(spec7): preview + result templates for yEd import"
```

---

## Task 18: Editor toolbar `group_by` dropdown + sidebar entry

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/harris_creator/editor.html`
- Modify: `pyarchinit_mini/web_interface/templates/base.html`

- [ ] **Step 1: Add Group By dropdown in editor.html**

Locate the toolbar in `harris_creator/editor.html` (near `<button id="save-btn"`) and add:

```html
<select id="group-by-selector" class="form-select form-select-sm" style="display:inline-block;width:auto">
  <option value="period_phase" selected>Period + Phase</option>
  <option value="struttura">Struttura</option>
  <option value="attivita">Attività</option>
  <option value="settore">Settore</option>
  <option value="area">Area</option>
  <option value="ambient">Ambient</option>
  <option value="saggio">Saggio</option>
  <option value="quad_par">Quad/Par</option>
  <option value="none">No grouping</option>
</select>
```

- [ ] **Step 2: Wire the change handler**

In the inline JS at the bottom of `editor.html`, near `loadSwimlaneState`:

```javascript
document.getElementById('group-by-selector')?.addEventListener('change', (ev) => {
  const site = window._currentSite;
  if (!site) return;
  loadSwimlaneStateWithGroupBy(site, ev.target.value);
});

async function loadSwimlaneStateWithGroupBy(site, group_by) {
  try {
    const url = `/harris-creator/api/load/${encodeURIComponent(site)}?group_by=${encodeURIComponent(group_by)}`;
    const r = await fetch(url);
    if (!r.ok) {
      alert(`Load failed: ${await r.text()}`);
      return;
    }
    const state = await r.json();
    renderSwimlaneState(state);
  } catch (e) {
    alert(`Error: ${e.message}`);
  }
}
```

- [ ] **Step 3: Add sidebar entries in base.html**

In `templates/base.html`, after the Paradata link (both navbar + lateral sidebar):

Navbar dropdown:
```html
<li><a class="dropdown-item" href="{{ url_for('yed_import.index') }}"><i class="fas fa-file-import"></i> {{ _('Import GraphML') }}</a></li>
```

Lateral sidebar:
```html
<li><a href="{{ url_for('yed_import.index') }}"><i class="fas fa-file-import"></i> {{ _('Import GraphML') }}</a></li>
```

- [ ] **Step 4: Smoke-test app boot**

Run: `.venv/bin/python -c "from pyarchinit_mini.web_interface.app import create_app; ret = create_app(); app = ret[0] if isinstance(ret, tuple) else ret; rules = [r.rule for r in app.url_map.iter_rules() if 'import-graphml' in r.rule]; assert rules; print('routes ok:', rules)"`
Expected: list of 3 routes (`/`, `/preview`, `/apply`).

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/harris_creator/editor.html \
        pyarchinit_mini/web_interface/templates/base.html
git commit -m "feat(spec7): Group By dropdown + Import GraphML sidebar entries"
```

---

## Task 19: Round-trip integration test

**Files:**
- Create: `tests/integration/test_roundtrip_extmatrix.py`

- [ ] **Step 1: Write the round-trip test**

Create `tests/integration/test_roundtrip_extmatrix.py`:

```python
"""End-to-end round-trip: DB → export → re-import → DB unchanged."""
from pathlib import Path
import sqlite3
import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState
from pyarchinit_mini.graphml_io.yed_writer import write_extended_matrix_graphml
from pyarchinit_mini.graphml_io.yed_importer import (
    parse_extended_matrix, build_import_plan, apply_import_plan,
)

FIX_DB = Path(__file__).parent.parent / "fixtures" / "databases" / "sqlite_volterra_30us_with_periods.db"


def _snapshot(session):
    return {
        "us": session.execute(text(
            "SELECT us, unita_tipo, periodo_iniziale, fase_iniziale, node_uuid "
            "FROM us_table WHERE sito='Volterra' ORDER BY us"
        )).fetchall(),
        "rels": session.execute(text(
            "SELECT us_from, us_to, relationship_type "
            "FROM us_relationships_table WHERE sito='Volterra' ORDER BY us_from, us_to"
        )).fetchall(),
    }


def test_roundtrip_export_then_reimport_idempotent(tmp_path):
    # 1. Open source DB and snapshot
    eng_src = create_engine(f"sqlite:///{FIX_DB}")
    s_src = sessionmaker(bind=eng_src)()
    before = _snapshot(s_src)

    # 2. Export
    state = SwimlaneState.load(s_src, "Volterra")
    out = tmp_path / "roundtrip.graphml"
    write_extended_matrix_graphml(state, site_meta={"sito": "Volterra"}, epochs=[], out=out)
    s_src.close()

    # 3. New empty DB
    import shutil
    target = tmp_path / "target.db"
    shutil.copyfile(FIX_DB, target)
    eng_dst = create_engine(f"sqlite:///{target}")
    s_dst = sessionmaker(bind=eng_dst)()

    # 4. Re-import
    parsed = parse_extended_matrix(out)
    plan = build_import_plan(parsed, s_dst)
    apply_import_plan(plan, s_dst)

    # 5. Snapshot after
    after = _snapshot(s_dst)
    s_dst.close()

    # All US present (counts equal)
    assert {r[0] for r in before["us"]} == {r[0] for r in after["us"]}
```

- [ ] **Step 2: Run — expect pass**

Run: `.venv/bin/python -m pytest tests/integration/test_roundtrip_extmatrix.py -v`
Expected: 1 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_roundtrip_extmatrix.py
git commit -m "test(spec7): round-trip export-then-reimport idempotency"
```

---

## Task 20: Documentation

**Files:**
- Create: `docs/EXTENDED_MATRIX_IMPORT.md`
- Create: `docs/EXTENDED_MATRIX_EXPORT.md`
- Create: `docs/HARRIS_LAYOUT_ALGO.md`

- [ ] **Step 1: Write EXTENDED_MATRIX_IMPORT.md**

Create `docs/EXTENDED_MATRIX_IMPORT.md`:

```markdown
# Extended Matrix Import — User Guide

This page describes how to import a pyarchinit Extended Matrix `.graphml`
file into pyarchinit-mini's database.

## When to use

You exported a Harris matrix from pyarchinit QGIS plugin (or from another
pyarchinit-mini instance) and want to populate `us_table`, `site_table`,
and `periodizzazione_table` from it.

## Steps

1. Navigate to **Tools → Import GraphML** in the sidebar.
2. Upload a `.graphml` file.
3. Review the preview — you'll see counts of records that will be created /
   updated / skipped per table.
4. Click **Apply** to commit the changes.

## What happens

- `site_table`: a row is created if `pyarchinit.sito` is new.
- `periodizzazione_table`: rows from `pyarchinit.epochs_meta` (graph-level).
  Upsert on `(sito, periodo_iniziale, fase_iniziale)`.
- `us_table`: upsert on `node_uuid` first, then `(sito, us)`. All
  `pyarchinit.*` keys are mapped to their corresponding columns.
- `us_relationships_table`: edges are imported with deduplication on
  the triple `(sito, us_from, us_to, relationship_type)`.

## Conflicts

If `node_uuid` matches an existing US in a **different** site, the preview
shows a conflict. Resolve manually by deleting the existing US or editing
the source file before re-importing.

## Files supported

- pyarchinit QGIS plugin Extended Matrix exports
- pyarchinit-mini Extended Matrix exports (round-trip)

Plain yEd files without `pyarchinit.us` keys are rejected with HTTP 400.
```

- [ ] **Step 2: Write EXTENDED_MATRIX_EXPORT.md**

Create `docs/EXTENDED_MATRIX_EXPORT.md`:

```markdown
# Extended Matrix Export — User Guide

The Harris Matrix Editor can export its current state as a yEd-flavored
GraphML file compatible with pyarchinit QGIS plugin and yEd Desktop.

## Steps

1. Open the editor on a site (e.g. `/harris-creator/editor?site=Volterra`).
2. (Optional) Choose **Group by** in the toolbar to organise lanes by
   `period_phase` (default), `struttura`, `attivita`, `settore`, `area`,
   `ambient`, `saggio`, `quad_par`, or `none`.
3. Click **Export yEd GraphML** in the toolbar.

The file is saved at
`data/exports/harris_yed/<site_slug>-extmatrix.graphml` and offered for
download.

## What's inside

- `y:TableNode configuration="YED_TABLE_NODE"` root with one `y:Row` per lane
- All 38 keys d0..d37 (epochs_meta, EMID, pyarchinit.us / area / sito /
  unita_tipo / periodo_iniziale / fase_iniziale / rapporti /
  d_stratigrafica / d_interpretativa / documentazione / node_uuid /
  struttura / attivita / settore / ambient / saggio / quad_par /
  datazione_estesa, plus URI / description / nodegraphics / edgegraphics)
- Per-US `<node>` children with full `pyarchinit.*` payload
- Per-edge `<edge>` with `y:PolyLineEdge` and edge label

## Compatibility

- yEd Desktop 3.x — opens directly, preserves table layout
- pyarchinit QGIS plugin — round-trip via `pyarchinit.*` keys

## Round-trip

Export then re-import via `/import-graphml/` is idempotent: same node_uuid
matches, no duplicates created.
```

- [ ] **Step 3: Write HARRIS_LAYOUT_ALGO.md**

Create `docs/HARRIS_LAYOUT_ALGO.md`:

```markdown
# Harris Layout Algorithm

The server-side module `pyarchinit_mini/harris_swimlane/harris_layout.py`
computes (x, y) positions for each US node within its swimlane so the
editor canvas and yEd export produce identical geometry.

## Algorithm

For each lane:

1. Build a sub-graph using only edges labelled `overlies` or `is_after`
   that connect nodes within the lane.
2. Run Kahn's topological sort:
   - Sources (no incoming edges) get rank 0 (top of lane)
   - Each successor's rank = max(predecessor ranks) + 1
3. Orphan nodes (no edges) get rank = max_rank + 1 (bottom of lane).
4. Per rank: distribute siblings horizontally, centred in the lane width.

## Output

`{node_id: (x, y)}` with canvas-global coordinates. Lane x-offsets are
baked in by accumulating `lane_widths`.

## Determinism

The output is fully deterministic given the same inputs. Both the editor
and the writer call `compute_harris_positions` with the same arguments,
so the yEd export reproduces the editor view.

## Limits

- Cycles (rare but possible if rapporti are inconsistent) get rank =
  max_rank + 1 (treated as orphans).
- Lanes with > 10,000 nodes fall back to a simple grid layout.
```

- [ ] **Step 4: Commit**

```bash
git add docs/EXTENDED_MATRIX_IMPORT.md docs/EXTENDED_MATRIX_EXPORT.md \
        docs/HARRIS_LAYOUT_ALGO.md
git commit -m "docs(spec7): user guides for import + export + layout algo"
```

---

## Task 21: CHANGELOG + version bump to 2.5.0

**Files:**
- Modify: `pyarchinit_mini/__init__.py`
- Modify: `pyproject.toml`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Bump version in pyproject.toml**

```bash
sed -i '' 's/version = "2.4.8"/version = "2.5.0"/' pyproject.toml
```

Verify with: `grep -n version pyproject.toml | head -2`
Expected: `version = "2.5.0"`

- [ ] **Step 2: Bump version in __init__.py**

```bash
sed -i '' 's/__version__ = "2.4.8"/__version__ = "2.5.0"/' pyarchinit_mini/__init__.py
```

- [ ] **Step 3: Prepend a 2.5.0 section to CHANGELOG.md**

Add the following block at the top of `CHANGELOG.md` (before the existing
`## [2.4.8]` entry):

```markdown
## [2.5.0] - 2026-05-18

### Added (IT)
- Editor swimlane: dropdown "Group by" con 9 valori (period_phase | struttura
  | attivita | settore | area | ambient | saggio | quad_par | none).
  Cambiando valore le lane si ricostruiscono e i nodi US si ridistribuiscono
  con un layout Harris-classico server-side.
- Nuovo modulo `harris_swimlane/harris_layout.py` — ordinamento topologico
  per dipendenze stratigrafiche (`overlies` / `is_after`), recent in alto.
- Nuovo `graphml_io/yed_importer.py` — parse + build_import_plan +
  apply_import_plan per round-trip da Extended Matrix → DB. Idempotente,
  preview 2-fasi, upsert by `node_uuid`.
- Nuova pagina `/import-graphml/` (upload + preview + apply). Sidebar entry
  sia in navbar che laterale (sezione Tools).

### Changed (IT)
- `graphml_io/yed_writer.py` riscritto: emette file Extended Matrix
  byte-compat con pyarchinit QGIS (38 keys d0..d37, `y:TableNode
  YED_TABLE_NODE`, `pyarchinit.epochs_meta`, `pyarchinit.*` per ogni nodo
  US). Vecchio `write_yed_graphml` mantenuto come wrapper deprecato.
- API `/harris-creator/api/load/<site>` accetta `?group_by=...` query
  param (default `period_phase`, retro-compat).
- API `/harris-creator/api/export/<site>/yed-graphml` accetta `?group_by=...`
  e popola `epochs_meta` da `periodizzazione_table`.
- Path output cambia in `data/exports/harris_yed/<slug>-extmatrix.graphml`
  (era `<slug>-harris-yed.graphml`).

### Added (EN)
- Editor "Group by" dropdown with 9 values; lanes rebuild + Harris-classic
  re-layout on change.
- New `harris_swimlane/harris_layout.py` — server-side topological
  positioning.
- New `graphml_io/yed_importer.py` — round-trip yEd → DB.
- New `/import-graphml/` page (upload + preview + apply).

### Changed (EN)
- `graphml_io/yed_writer.py` rewritten — emits 38-key Extended Matrix
  byte-compat with pyarchinit.
- `/api/load` and `/api/export` accept `?group_by=...`.
- Export output path renamed `*-extmatrix.graphml`.

```

- [ ] **Step 4: Run full test suite**

Run: `.venv/bin/python -m pytest tests/ -q --tb=no`
Expected: 0 failed (except the pre-existing `test_delete_site` if still relevant).

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/__init__.py pyproject.toml CHANGELOG.md
git commit -m "release: bump to 2.5.0 (Spec 7 Extended Matrix round-trip)"
```

---

## Task 22: Final regression sweep

**Files:**
- (no files modified)

- [ ] **Step 1: Run all tests one more time**

Run: `.venv/bin/python -m pytest tests/ -q --tb=short`
Expected: pre-existing failures unchanged, all new tests pass.

- [ ] **Step 2: Verify URL map**

Run:
```bash
.venv/bin/python -c "
from pyarchinit_mini.web_interface.app import create_app
ret = create_app(); app = ret[0] if isinstance(ret, tuple) else ret
for r in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
    if any(k in r.rule for k in ('harris-creator', 'import-graphml')):
        methods = ','.join(sorted(r.methods - {'HEAD','OPTIONS'}))
        print(f'{methods:10s} {r.rule}')
"
```
Expected output contains:
- `GET        /harris-creator/api/load/<site>`
- `GET        /harris-creator/api/export/<site>/yed-graphml`
- `GET        /import-graphml/`
- `POST       /import-graphml/preview`
- `POST       /import-graphml/apply`

- [ ] **Step 3: Manual smoke test**

```bash
.venv/bin/pyarchinit-mini-web &
sleep 3
curl -s http://localhost:5000/import-graphml/ | grep -o "Import yEd" | head -1
kill %1
```
Expected: `Import yEd`

- [ ] **Step 4: Commit if any tweaks needed**

(No-op if regression passed.)

---

## Self-Review

### Spec coverage

| Spec section | Tasks |
|---|---|
| §3 Architecture | Tasks 4, 5, 7-10, 16-18 |
| §4.1 swimlane_state extension | Task 4 |
| §4.2 harris_layout | Task 3 |
| §4.3 yed_writer rewrite | Tasks 7, 8, 9, 10 |
| §4.4 yed_importer | Tasks 13, 14, 15 |
| §4.5 yed_import_routes blueprint | Tasks 16, 17 |
| §4.6 Templates | Tasks 16, 17 |
| §4.7 Editor toolbar | Task 18 |
| §4.8 Sidebar entry | Task 18 |
| §5 Data flows 1-5 | Tasks 4, 6, 11, 12, 16, 17 |
| §6 XML structure + keys | Tasks 2 (constants), 7-10 (emit), 13 (parse) |
| §7 Error handling | Tasks 13, 14, 16 |
| §8 Testing strategy | Tasks 3, 7-10, 13-15, 16, 17, 19 |
| §9 DoD | All tasks; final sweep Task 22 |
| §10 Backwards compat | Task 7 (deprecated wrapper) |

### Placeholder scan

No "TBD", "TODO", "implement later", or "add appropriate error handling"
in plan body — verified.

### Type consistency

- `EditorState.group_by` added in Task 4, used by writer in Tasks 8/9, by
  routes in Task 6, by frontend in Task 18 — consistent.
- `KeyDef` (Task 2) shared between writer (Task 7) and importer (Task 13).
- `ImportPlan` / `ImportResult` defined in Tasks 14 / 15, used by blueprint
  in Tasks 16 / 17 — consistent.
- `compute_harris_positions` signature in Task 3 matches usage in Task 5.

Plan complete. Ready for implementation.
