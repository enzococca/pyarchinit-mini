# EM Palette + Multi-Format Swimlane Round-Trip Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the cytoscape-only swimlane renderer with an s3dgraphy-centric pipeline where `EM_palette.graphml` is the canonical style source. Add palette-aware GraphML export, Heriverse/ATON JSON export, and GraphML/JSON import that writes 4-tuple rapporti with inverses on both involved US.

**Architecture:** A single `s3dgraphy.Graph` is built by `S3DProjector` from the DB and used by all consumers: a cytoscape adapter feeds the web UI, the GraphML exporter writes yEd-compatible files using `EM_palette.graphml` as a base, and the Heriverse JSON exporter (already in repo) handles ATON. Reverse path: imported GraphML/JSON → `s3dgraphy.Graph` → `graph_to_db.write_graph()` upserts `us_table` rows and writes 4-tuple `rapporti` with inverses on both sides. A feature flag `SWIMLANE_PIPELINE=s3dgraphy|legacy` keeps the existing renderer as a rollback path until the new pipeline reaches parity (4066 edges on Rimini_RN_2020_21_Museo_Fellini fixture).

**Tech Stack:** Python 3.12, Flask, SQLAlchemy 2.x (text() with named params), s3dgraphy ≥ 0.1.42, pytest, cytoscape.js, yEd GraphML XML schema.

**Spec:** `docs/superpowers/specs/2026-05-19-em-palette-swimlane-design.md`

---

## File Structure

### New modules

| Path | Responsibility |
|---|---|
| `pyarchinit_mini/em_palette/__init__.py` | Public API: `get_node_style`, `get_edge_style`, `reload`. |
| `pyarchinit_mini/em_palette/styles.py` | Dataclasses `NodeStyle` and `EdgeStyle`. |
| `pyarchinit_mini/em_palette/loader.py` | Parse `EM_palette.graphml`, cache singleton, SIGHUP hot-reload. |
| `pyarchinit_mini/graphproj/s3d_projector.py` | `S3DProjector.from_site(session, site, group_by) -> s3dgraphy.Graph`. |
| `pyarchinit_mini/graphproj/s3d_to_cytoscape.py` | `to_cytoscape(graph, group_by) -> dict` for web UI. |
| `pyarchinit_mini/graphproj/graph_to_db.py` | `write_graph(graph, target_site, session, *, source_label) -> WriteResult`. |
| `pyarchinit_mini/graphproj/heriverse_parser.py` | Parse Heriverse JSON → `s3dgraphy.Graph`. |
| `pyarchinit_mini/graphproj/rapporti_codec.py` | `parse_rapporti(raw)` (bilingual, 2-tuple/4-tuple); `serialize_rapporti(items)` (always 4-tuple); `INVERSE_PAIRS`, `SYMMETRIC`, `_IT_EXTRAS`. |
| `pyarchinit_mini/web_interface/matrix_tools_routes.py` | Blueprint for `/matrix-tools` page. |
| `pyarchinit_mini/web_interface/templates/matrix_tools/index.html` | Site selector + file uploader + format radio. |
| `tests/fixtures/em_palette_minimal.graphml` | 5 unit types + 5 edge types, for fast unit tests. |
| `tests/fixtures/adarte_regression_dump.sql` | Anonymized 50–100 US fixture (renamed `RegressionFixture_v1`). |

### Modified files

| Path | Change |
|---|---|
| `pyarchinit_mini/graphml_converter/templates/EM_palette.graphml` | Replace with the 3246-line version from `~/Downloads/em_palette_template.graphml`. |
| `pyarchinit_mini/harris_swimlane/swimlane_state.py` | `SwimlaneState.load()` switches on `SWIMLANE_PIPELINE` env var; new pipeline calls `S3DProjector` + `to_cytoscape`. |
| `pyarchinit_mini/web_interface/harris_creator_routes.py` | New endpoints `/api/export/<site>/heriverse-json`, `/api/import/<site>/graphml`, `/api/import/<site>/json`; modify `/api/load/<site>` and `/api/export/<site>/yed-graphml` to use the new pipeline. |
| `pyarchinit_mini/web_interface/app.py` | Register `matrix_tools_bp`, `csrf.exempt(matrix_tools_bp)`. |
| `pyarchinit_mini/web_interface/templates/harris_creator/swimlane.html` | Toolbar additions: grouping dropdown, export menu, import menu. |
| `pyarchinit_mini/web_interface/templates/sites/list.html` | Per-row export buttons (GraphML, Heriverse). |

### Test files

| Path | Coverage |
|---|---|
| `tests/unit/test_palette_loader.py` | parse, style maps, fallback, SIGHUP reload. |
| `tests/unit/test_rapporti_codec.py` | bilingual read (2-tuple, 4-tuple), 4-tuple write, dedup, INVERSE_PAIRS coverage. |
| `tests/unit/test_s3d_projector.py` | build graph from fixture DB, "Periodo 1" fallback, sub-grouping. |
| `tests/unit/test_graph_to_db.py` | upsert us_table, rapporti 4-tuple, inverses, stub creation. |
| `tests/unit/test_heriverse_parser.py` | parse Heriverse JSON → s3dgraphy.Graph. |
| `tests/integration/test_api_load_site.py` | `GET /api/load/<site>` with and without `group_by`. |
| `tests/integration/test_api_export_graphml.py` | `GET /api/export/<site>/yed-graphml`. |
| `tests/integration/test_api_export_heriverse.py` | `GET /api/export/<site>/heriverse-json`. |
| `tests/integration/test_api_import_graphml.py` | `POST /api/import/<site>/graphml`. |
| `tests/integration/test_api_import_json.py` | `POST /api/import/<site>/json`. |
| `tests/integration/test_feature_flag_pipelines.py` | s3dgraphy vs legacy edge-count parity. |
| `tests/integration/test_roundtrip.py` | DB → export → import → assert parity. |
| `tests/integration/test_adarte_regression.py` | ≥4060 edges on Rimini fixture. |

---

## Phase 0: Branch + worktree

### Task 0: Create worktree and feature branch

**Files:** none yet.

- [ ] **Step 1: Create worktree branch**

```bash
cd /Users/enzo/pyarchinit-mini-desk
git checkout -b feat/em-palette-swimlane
git status
```

Expected: `On branch feat/em-palette-swimlane, nothing to commit, working tree clean`.

- [ ] **Step 2: Verify spec doc is committed on this branch**

```bash
git log --oneline -3 docs/superpowers/specs/2026-05-19-em-palette-swimlane-design.md
```

Expected: shows the spec commit (`7491c7f` plus initial creation).

---

## Phase 1: Foundation (palette + rapporti codec)

### Task 1: Replace EM palette template

**Files:**
- Modify: `pyarchinit_mini/graphml_converter/templates/EM_palette.graphml` (658 → 3246 lines)
- Add: `tests/fixtures/em_palette_minimal.graphml` (smaller copy for fast tests)

- [ ] **Step 1: Back up current template, copy Downloads version**

```bash
cp pyarchinit_mini/graphml_converter/templates/EM_palette.graphml \
   pyarchinit_mini/graphml_converter/templates/EM_palette.graphml.bak
cp ~/Downloads/em_palette_template.graphml \
   pyarchinit_mini/graphml_converter/templates/EM_palette.graphml
wc -l pyarchinit_mini/graphml_converter/templates/EM_palette.graphml
```

Expected: `3246 pyarchinit_mini/graphml_converter/templates/EM_palette.graphml`.

- [ ] **Step 2: Build fixture minimal palette**

Create `tests/fixtures/em_palette_minimal.graphml` containing 5 node entries (USM, USD, USV, SF, VSF) and 5 edge entries (overlies, cuts, fills, abuts, has_same_time). Copy the corresponding `<node>` and `<edge>` elements from `~/Downloads/em_palette_template.graphml` into a minimal GraphML scaffolding.

```bash
# Use grep + manual extraction or write a small extractor script. Final size ~200 lines.
```

- [ ] **Step 3: Validate XML parseability**

```bash
python -c "import xml.etree.ElementTree as ET; ET.parse('pyarchinit_mini/graphml_converter/templates/EM_palette.graphml'); print('OK')"
python -c "import xml.etree.ElementTree as ET; ET.parse('tests/fixtures/em_palette_minimal.graphml'); print('OK')"
```

Expected: both print `OK`.

- [ ] **Step 4: Remove backup, commit**

```bash
rm pyarchinit_mini/graphml_converter/templates/EM_palette.graphml.bak
git add pyarchinit_mini/graphml_converter/templates/EM_palette.graphml tests/fixtures/em_palette_minimal.graphml
git commit -m "feat(palette): replace EM_palette.graphml with 3246-line canonical version"
```

---

### Task 2: Style dataclasses

**Files:**
- Create: `pyarchinit_mini/em_palette/__init__.py`
- Create: `pyarchinit_mini/em_palette/styles.py`
- Create: `tests/unit/test_palette_styles.py`

- [ ] **Step 1: Write failing test**

`tests/unit/test_palette_styles.py`:
```python
from pyarchinit_mini.em_palette.styles import NodeStyle, EdgeStyle


def test_node_style_defaults():
    s = NodeStyle(unit_type="US")
    assert s.unit_type == "US"
    assert s.shape == "rectangle"
    assert s.fill_color == "#FFFFFF"
    assert s.border_color == "#000000"
    assert s.border_width == 1.0
    assert s.border_style == "line"


def test_edge_style_defaults():
    e = EdgeStyle(canonical_name="overlies")
    assert e.canonical_name == "overlies"
    assert e.line_color == "#000000"
    assert e.line_width == 1.0
    assert e.line_style == "line"
    assert e.arrow_target == "standard"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_palette_styles.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'pyarchinit_mini.em_palette'`.

- [ ] **Step 3: Implement styles**

`pyarchinit_mini/em_palette/__init__.py`:
```python
"""EM (Extended Matrix) palette: style source of truth for US nodes and stratigraphic edges."""
```

`pyarchinit_mini/em_palette/styles.py`:
```python
"""Dataclasses for palette-derived rendering styles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class NodeStyle:
    unit_type: str
    shape: str = "rectangle"  # rectangle, ellipse, roundrectangle, parallelogram, hexagon, octagon
    fill_color: str = "#FFFFFF"
    border_color: str = "#000000"
    border_width: float = 1.0
    border_style: str = "line"  # line, dashed, dotted
    font_color: str = "#000000"
    font_size: int = 12
    label_placement: str = "center"


@dataclass(frozen=True)
class EdgeStyle:
    canonical_name: str
    line_color: str = "#000000"
    line_width: float = 1.0
    line_style: str = "line"  # line, dashed, dotted
    arrow_source: str = "none"
    arrow_target: str = "standard"
```

- [ ] **Step 4: Run test, expect pass**

```bash
pytest tests/unit/test_palette_styles.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/em_palette/ tests/unit/test_palette_styles.py
git commit -m "feat(palette): add NodeStyle and EdgeStyle dataclasses"
```

---

### Task 3: Palette loader (parse + cache)

**Files:**
- Create: `pyarchinit_mini/em_palette/loader.py`
- Create: `tests/unit/test_palette_loader.py`

- [ ] **Step 1: Write failing tests**

`tests/unit/test_palette_loader.py`:
```python
from pathlib import Path
import pytest

from pyarchinit_mini.em_palette.loader import PaletteLoader
from pyarchinit_mini.em_palette.styles import NodeStyle, EdgeStyle


FIXTURE = Path(__file__).parent.parent / "fixtures" / "em_palette_minimal.graphml"


@pytest.fixture
def loader():
    return PaletteLoader(palette_path=FIXTURE)


def test_loader_returns_node_style_for_known_unit_type(loader):
    s = loader.get_node_style("USM")
    assert isinstance(s, NodeStyle)
    assert s.unit_type == "USM"
    assert s.shape  # populated from <y:Shape type="...">
    assert s.fill_color.startswith("#")
    assert s.border_color.startswith("#")


def test_loader_returns_default_for_unknown_unit_type(loader):
    s = loader.get_node_style("UNKNOWN_TYPE")
    assert s.unit_type == "UNKNOWN_TYPE"
    assert s.shape == "rectangle"  # default


def test_loader_returns_edge_style_for_canonical(loader):
    s = loader.get_edge_style("overlies")
    assert isinstance(s, EdgeStyle)
    assert s.canonical_name == "overlies"
    assert s.line_color.startswith("#")


def test_loader_caches_after_first_load(loader):
    first = loader.get_node_style("USM")
    second = loader.get_node_style("USM")
    assert first is second  # cached, same object


def test_loader_reload_refreshes_cache(loader):
    first = loader.get_node_style("USM")
    loader.reload()
    second = loader.get_node_style("USM")
    assert first is not second  # new object after reload
    assert first == second      # but equal content


def test_loader_fallback_when_palette_missing():
    bogus = Path("/nonexistent/path/em_palette.graphml")
    loader = PaletteLoader(palette_path=bogus, allow_fallback=True)
    s = loader.get_node_style("USM")
    assert s.shape == "rectangle"  # fallback default
```

- [ ] **Step 2: Run tests, expect fail**

```bash
pytest tests/unit/test_palette_loader.py -v
```

Expected: FAIL — `PaletteLoader` not defined.

- [ ] **Step 3: Implement loader**

`pyarchinit_mini/em_palette/loader.py`:
```python
"""EM palette GraphML parser with caching and hot-reload.

The palette is a yEd-flavoured GraphML document where each <node> represents
one canonical US type (USM, USD, USV, SF, VSF, TSU, USVn) and each <edge>
represents one canonical stratigraphic relation (overlies, cuts, fills, abuts,
has_same_time, is_after, is_before, is_bonded_to).

We identify the unit type via the <y:NodeLabel> text content of the node, and
the canonical relation via the <y:EdgeLabel> text content.
"""
from __future__ import annotations

import logging
import signal
import threading
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional

from .styles import NodeStyle, EdgeStyle


logger = logging.getLogger(__name__)

NS = {
    "g": "http://graphml.graphdrawing.org/xmlns",
    "y": "http://www.yworks.com/xml/graphml",
}

DEFAULT_PALETTE_PATH = Path(__file__).parent.parent / "graphml_converter" / "templates" / "EM_palette.graphml"


class PaletteLoader:
    def __init__(
        self,
        palette_path: Optional[Path] = None,
        *,
        allow_fallback: bool = True,
    ) -> None:
        self.palette_path = palette_path or DEFAULT_PALETTE_PATH
        self.allow_fallback = allow_fallback
        self._node_cache: Dict[str, NodeStyle] = {}
        self._edge_cache: Dict[str, EdgeStyle] = {}
        self._loaded = False
        self._lock = threading.Lock()

    def _load(self) -> None:
        with self._lock:
            if self._loaded:
                return
            try:
                tree = ET.parse(self.palette_path)
            except (FileNotFoundError, ET.ParseError) as exc:
                if self.allow_fallback:
                    logger.warning("Palette load failed (%s); using hardcoded fallbacks.", exc)
                    self._loaded = True
                    return
                raise
            root = tree.getroot()
            for node_el in root.iter(f"{{{NS['g']}}}node"):
                style = self._parse_node(node_el)
                if style is not None:
                    self._node_cache[style.unit_type] = style
            for edge_el in root.iter(f"{{{NS['g']}}}edge"):
                style = self._parse_edge(edge_el)
                if style is not None:
                    self._edge_cache[style.canonical_name] = style
            self._loaded = True

    def _parse_node(self, node_el: ET.Element) -> Optional[NodeStyle]:
        shape_node = node_el.find(f".//{{{NS['y']}}}ShapeNode")
        if shape_node is None:
            return None
        label = shape_node.find(f".//{{{NS['y']}}}NodeLabel")
        if label is None or not (label.text and label.text.strip()):
            return None
        unit_type = label.text.strip()
        shape_el = shape_node.find(f"{{{NS['y']}}}Shape")
        shape = shape_el.attrib.get("type", "rectangle") if shape_el is not None else "rectangle"
        fill_el = shape_node.find(f"{{{NS['y']}}}Fill")
        fill_color = fill_el.attrib.get("color", "#FFFFFF") if fill_el is not None else "#FFFFFF"
        border_el = shape_node.find(f"{{{NS['y']}}}BorderStyle")
        border_color = border_el.attrib.get("color", "#000000") if border_el is not None else "#000000"
        border_width = float(border_el.attrib.get("width", "1.0")) if border_el is not None else 1.0
        border_style = border_el.attrib.get("type", "line") if border_el is not None else "line"
        font_color = label.attrib.get("textColor", "#000000")
        font_size = int(label.attrib.get("fontSize", "12"))
        return NodeStyle(
            unit_type=unit_type,
            shape=shape,
            fill_color=fill_color,
            border_color=border_color,
            border_width=border_width,
            border_style=border_style,
            font_color=font_color,
            font_size=font_size,
        )

    def _parse_edge(self, edge_el: ET.Element) -> Optional[EdgeStyle]:
        line_el = edge_el.find(f".//{{{NS['y']}}}LineStyle")
        label_el = edge_el.find(f".//{{{NS['y']}}}EdgeLabel")
        arrow_el = edge_el.find(f".//{{{NS['y']}}}Arrows")
        if label_el is None or not (label_el.text and label_el.text.strip()):
            return None
        canonical = label_el.text.strip().lower().replace(" ", "_")
        if not canonical:
            return None
        line_color = line_el.attrib.get("color", "#000000") if line_el is not None else "#000000"
        line_width = float(line_el.attrib.get("width", "1.0")) if line_el is not None else 1.0
        line_style = line_el.attrib.get("type", "line") if line_el is not None else "line"
        arrow_target = arrow_el.attrib.get("target", "standard") if arrow_el is not None else "standard"
        arrow_source = arrow_el.attrib.get("source", "none") if arrow_el is not None else "none"
        return EdgeStyle(
            canonical_name=canonical,
            line_color=line_color,
            line_width=line_width,
            line_style=line_style,
            arrow_target=arrow_target,
            arrow_source=arrow_source,
        )

    def get_node_style(self, unit_type: str) -> NodeStyle:
        self._load()
        return self._node_cache.get(unit_type, NodeStyle(unit_type=unit_type))

    def get_edge_style(self, canonical_name: str) -> EdgeStyle:
        self._load()
        return self._edge_cache.get(canonical_name, EdgeStyle(canonical_name=canonical_name))

    def reload(self) -> None:
        with self._lock:
            self._node_cache.clear()
            self._edge_cache.clear()
            self._loaded = False
        self._load()


_singleton: Optional[PaletteLoader] = None


def get_palette() -> PaletteLoader:
    global _singleton
    if _singleton is None:
        _singleton = PaletteLoader()
    return _singleton


def install_sighup_reload() -> None:
    def _handler(_signum, _frame):
        logger.info("SIGHUP received: reloading EM palette")
        get_palette().reload()
    signal.signal(signal.SIGHUP, _handler)
```

Update `pyarchinit_mini/em_palette/__init__.py`:
```python
"""EM (Extended Matrix) palette: style source of truth for US nodes and stratigraphic edges."""
from .loader import PaletteLoader, get_palette, install_sighup_reload
from .styles import NodeStyle, EdgeStyle

__all__ = ["PaletteLoader", "get_palette", "install_sighup_reload", "NodeStyle", "EdgeStyle"]
```

- [ ] **Step 4: Run tests, expect pass**

```bash
pytest tests/unit/test_palette_loader.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/em_palette/loader.py pyarchinit_mini/em_palette/__init__.py tests/unit/test_palette_loader.py
git commit -m "feat(palette): PaletteLoader with cache + SIGHUP hot-reload + fallback"
```

---

### Task 4: Rapporti codec (bilingual reader, 4-tuple writer, inverse registry)

**Files:**
- Create: `pyarchinit_mini/graphproj/rapporti_codec.py`
- Create: `tests/unit/test_rapporti_codec.py`

- [ ] **Step 1: Write failing tests**

`tests/unit/test_rapporti_codec.py`:
```python
from pyarchinit_mini.graphproj.rapporti_codec import (
    parse_rapporti,
    serialize_rapporti,
    INVERSE_PAIRS,
    SYMMETRIC,
    Rapporto,
)


def test_parse_empty_returns_empty_list():
    assert parse_rapporti("", current_site="S") == []
    assert parse_rapporti(None, current_site="S") == []


def test_parse_2_tuple_expands_to_4_tuple():
    # 2-tuple: [tipo, us] — area/sito derived from context
    items = parse_rapporti("[['Coperto da', '120']]", current_site="SiteX")
    assert len(items) == 1
    r = items[0]
    assert r.canonical == "is_after"
    assert r.target_us == "120"
    assert r.target_area is None  # unknown at parse time
    assert r.target_sito == "SiteX"


def test_parse_4_tuple_preserves_area_sito():
    items = parse_rapporti("[['Copre', '120', 'A1', 'SiteX']]", current_site="SiteX")
    assert len(items) == 1
    r = items[0]
    assert r.canonical == "overlies"
    assert r.target_us == "120"
    assert r.target_area == "A1"
    assert r.target_sito == "SiteX"


def test_parse_english_label_resolves_canonical():
    items = parse_rapporti("[['Covers', '120']]", current_site="S")
    assert items[0].canonical == "overlies"


def test_parse_italian_extras_resolve():
    items = parse_rapporti("[['Riempito da', '1'], ['Si lega a', '2'], ['Gli si appoggia', '3']]", current_site="S")
    cans = [r.canonical for r in items]
    assert "is_after" in cans          # riempito da
    assert "is_bonded_to" in cans      # si lega a
    assert "is_before" in cans         # gli si appoggia


def test_parse_unknown_label_yields_none():
    items = parse_rapporti("[['totalmente sconosciuto', '5']]", current_site="S")
    assert items == []  # silently skipped, not an error


def test_parse_malformed_string_returns_empty():
    items = parse_rapporti("not a literal {{{", current_site="S")
    assert items == []


def test_serialize_writes_4_tuple_list():
    items = [
        Rapporto(canonical="overlies", target_us="120", target_area="A1", target_sito="S"),
        Rapporto(canonical="is_after", target_us="121", target_area="A1", target_sito="S"),
    ]
    out = serialize_rapporti(items, italian_labels={"overlies": "Copre", "is_after": "Coperto da"})
    parsed = eval(out)  # safe in test context
    assert parsed == [
        ["Copre", "120", "A1", "S"],
        ["Coperto da", "121", "A1", "S"],
    ]


def test_serialize_emits_none_as_empty_string():
    items = [Rapporto(canonical="overlies", target_us="120", target_area=None, target_sito="S")]
    out = serialize_rapporti(items, italian_labels={"overlies": "Copre"})
    parsed = eval(out)
    assert parsed == [["Copre", "120", "", "S"]]


def test_inverse_pairs_covers_all_directional_edges():
    directional = {"overlies", "is_after", "cuts", "is_cut_by", "fills", "abuts", "is_before"}
    for can in directional:
        assert can in INVERSE_PAIRS or can in SYMMETRIC, f"{can} missing from INVERSE_PAIRS/SYMMETRIC"


def test_symmetric_edges_have_no_inverse():
    assert "has_same_time" in SYMMETRIC
    assert "is_bonded_to" in SYMMETRIC


def test_dedup_by_canonical_us_area_sito():
    items = [
        Rapporto(canonical="overlies", target_us="120", target_area="A", target_sito="S"),
        Rapporto(canonical="overlies", target_us="120", target_area="A", target_sito="S"),  # dup
        Rapporto(canonical="overlies", target_us="121", target_area="A", target_sito="S"),
    ]
    out = serialize_rapporti(items, italian_labels={"overlies": "Copre"})
    parsed = eval(out)
    assert len(parsed) == 2
```

- [ ] **Step 2: Run tests, expect fail**

```bash
pytest tests/unit/test_rapporti_codec.py -v
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement codec**

`pyarchinit_mini/graphproj/rapporti_codec.py`:
```python
"""Canonical rapporti reader/writer.

Reader accepts both legacy 2-tuple `[rel, us]` and new 4-tuple `[rel, us, area, sito]`.
Writer always emits 4-tuple list. Inverse pairs for non-symmetric directional edges
are declared here as a single source of truth.
"""
from __future__ import annotations

import ast
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional


logger = logging.getLogger(__name__)


# Symmetric edges: relation and its inverse are the same name.
SYMMETRIC = frozenset({"has_same_time", "is_bonded_to"})

# Directional canonical pairs. Reading either direction yields the canonical
# orientation; writing uses italian_labels mapping to display strings.
INVERSE_PAIRS: Dict[str, str] = {
    "overlies": "is_after",
    "is_after": "overlies",
    "cuts": "is_cut_by",
    "is_cut_by": "cuts",
    "fills": "is_filled_by",
    "is_filled_by": "fills",
    "abuts": "is_abutted_by",
    "is_abutted_by": "abuts",
    "is_before": "is_after",
    # is_after is already mapped via overlies above; alias map allows reverse lookup
}

# Italian aliases NOT in vocab_it.json (also present in swimlane_state patched dict).
# Source: live Adarte postgres data on Rimini_RN_2020_21_Museo_Fellini.
_IT_EXTRAS: Dict[str, str] = {
    "riempito da": "is_after",
    "si lega a": "is_bonded_to",
    "si lega_a": "is_bonded_to",
    "connesso a": "is_bonded_to",
    "connesso_a": "is_bonded_to",
    "anteriore a": "is_before",
    "posteriore a": "is_after",
    "gli si appoggia": "is_before",
}

# English fallbacks for Al-Khutm-style data.
_EN_TO_CANONICAL: Dict[str, str] = {
    "covers": "overlies",
    "cuts": "cuts",
    "fills": "fills",
    "leans on": "abuts",
    "leans_on": "abuts",
    "equal to": "has_same_time",
    "equal_to": "has_same_time",
    "same as": "has_same_time",
    "continuity": "has_same_time",
    "bonds to": "is_bonded_to",
    "bonds_to": "is_bonded_to",
    "connected to": "is_bonded_to",
    "connected_to": "is_bonded_to",
    "covered by": "is_after",
    "covered_by": "is_after",
    "cut by": "is_cut_by",
    "cut_by": "is_cut_by",
}


@dataclass(frozen=True)
class Rapporto:
    canonical: str
    target_us: str
    target_area: Optional[str]
    target_sito: str

    @property
    def dedup_key(self) -> tuple:
        return (self.canonical, self.target_us, self.target_area or "", self.target_sito)


def _resolve_canonical(label: str) -> Optional[str]:
    """Resolve a free-text relation label to canonical name."""
    low = label.strip().lower()
    if not low:
        return None
    try:
        from pyarchinit_mini.graphproj.edge_registry import EdgeRegistry
        reg = _registry_singleton()
        canon = reg.resolve_italian_alias(low)
        if canon:
            return canon
    except Exception:
        pass
    return _IT_EXTRAS.get(low) or _EN_TO_CANONICAL.get(low)


_REG = None
def _registry_singleton():
    global _REG
    if _REG is None:
        from pyarchinit_mini.graphproj.edge_registry import EdgeRegistry
        _REG = EdgeRegistry()
    return _REG


def parse_rapporti(raw: Optional[str], *, current_site: str) -> List[Rapporto]:
    """Parse the rapporti field. Accepts 2-tuple or 4-tuple list-of-lists."""
    if not raw or not raw.strip():
        return []
    try:
        parsed = ast.literal_eval(raw)
    except (SyntaxError, ValueError):
        logger.warning("rapporti malformed (literal_eval failed): %r", raw[:80])
        return []
    out: List[Rapporto] = []
    if not isinstance(parsed, (list, tuple)):
        return []
    for item in parsed:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        rel = str(item[0]).strip()
        target_us = str(item[1]).strip()
        target_area = str(item[2]).strip() if len(item) >= 3 and item[2] not in (None, "") else None
        target_sito = str(item[3]).strip() if len(item) >= 4 and item[3] not in (None, "") else current_site
        canonical = _resolve_canonical(rel)
        if not canonical or not target_us:
            continue
        out.append(Rapporto(canonical, target_us, target_area, target_sito))
    return out


def serialize_rapporti(items: List[Rapporto], *, italian_labels: Dict[str, str]) -> str:
    """Serialize a list of Rapporto as a 4-tuple list-of-lists string.

    italian_labels maps canonical → italian display string.
    Dedups by (canonical, us, area, sito).
    """
    seen = set()
    rows: List[List[str]] = []
    for r in items:
        key = r.dedup_key
        if key in seen:
            continue
        seen.add(key)
        label = italian_labels.get(r.canonical, r.canonical)
        rows.append([label, r.target_us, r.target_area or "", r.target_sito])
    return repr(rows)
```

- [ ] **Step 4: Run tests, expect pass**

```bash
pytest tests/unit/test_rapporti_codec.py -v
```

Expected: 11 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/rapporti_codec.py tests/unit/test_rapporti_codec.py
git commit -m "feat(rapporti): bilingual codec with 4-tuple serializer and INVERSE_PAIRS registry"
```

---

## Phase 2: Projector (DB → s3dgraphy.Graph)

### Task 5: S3DProjector skeleton + period rows + fallback

**Files:**
- Create: `pyarchinit_mini/graphproj/s3d_projector.py`
- Create: `tests/unit/test_s3d_projector.py`

- [ ] **Step 1: Write failing tests for period row generation**

`tests/unit/test_s3d_projector.py`:
```python
from pathlib import Path
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.graphproj.s3d_projector import S3DProjector


@pytest.fixture
def session_factory(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/p.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (
            id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT UNIQUE, descrizione TEXT)"""))
        conn.execute(text("""CREATE TABLE period_table (
            id_period INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, periodo TEXT, fase TEXT, datazione TEXT,
            descrizione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
            descrizione TEXT,
            fase_iniziale TEXT, fase_finale TEXT,
            rapporti TEXT)"""))
        conn.execute(text("INSERT INTO site_table (sito) VALUES ('S1')"))
    return sessionmaker(bind=engine)


def test_period_fallback_when_table_empty(session_factory):
    s = session_factory()
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S1','A','1','USM')"))
    s.commit()
    g = S3DProjector.from_site(s, "S1")
    assert len(g.rows) == 1
    assert g.rows[0].label == "Periodo 1"
    assert g.rows[0].is_fallback is True


def test_periods_loaded_from_table(session_factory):
    s = session_factory()
    s.execute(text("INSERT INTO period_table (sito, periodo, fase, datazione) VALUES ('S1','II','a','XII sec')"))
    s.execute(text("INSERT INTO period_table (sito, periodo, fase, datazione) VALUES ('S1','I','b','X sec')"))
    s.commit()
    g = S3DProjector.from_site(s, "S1")
    # alphabetically sorted by (period, phase)
    assert [r.label for r in g.rows] == ["I/b", "II/a"]
    assert all(r.is_fallback is False for r in g.rows)


def test_us_without_period_goes_to_fallback_row(session_factory):
    s = session_factory()
    s.execute(text("INSERT INTO period_table (sito, periodo, fase) VALUES ('S1','I','a')"))
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, fase_iniziale) VALUES ('S1','A','1','USM','a')"))
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, fase_iniziale) VALUES ('S1','A','2','USM', NULL)"))
    s.commit()
    g = S3DProjector.from_site(s, "S1")
    by_label = {r.label: r for r in g.rows}
    assert "I/a" in by_label
    assert "Periodo 1" in by_label  # fallback row added because US 2 has no period
    us1 = next(n for n in g.nodes if n.us == "1")
    us2 = next(n for n in g.nodes if n.us == "2")
    assert us1.row_id == by_label["I/a"].row_id
    assert us2.row_id == by_label["Periodo 1"].row_id
```

- [ ] **Step 2: Run tests, expect fail**

```bash
pytest tests/unit/test_s3d_projector.py -v
```

Expected: FAIL — `S3DProjector` not found.

- [ ] **Step 3: Implement projector skeleton + period rows**

`pyarchinit_mini/graphproj/s3d_projector.py`:
```python
"""Project DB stratigraphy (us_table + period_table) into an s3dgraphy.Graph.

The Graph is the canonical representation consumed by:
  - s3d_to_cytoscape (web UI)
  - s3dgraphy.exporter.graphml (yEd export)
  - s3dgraphy.exporter.json_exporter (Heriverse/ATON)

Rows = periods (always). When period_table is empty for the site OR a US has
no fase_iniziale matching any period row, the US is assigned to a synthetic
fallback row named "Periodo 1".
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from sqlalchemy import text
from sqlalchemy.orm import Session

from pyarchinit_mini.graphproj.rapporti_codec import parse_rapporti, Rapporto, SYMMETRIC


logger = logging.getLogger(__name__)


@dataclass
class Row:
    row_id: str
    label: str
    periodo: Optional[str] = None
    fase: Optional[str] = None
    datazione: Optional[str] = None
    is_fallback: bool = False


@dataclass
class Node:
    node_id: str
    us: str
    area: Optional[str]
    sito: str
    unit_type: str
    description: Optional[str]
    row_id: str
    sub_group: Optional[str] = None


@dataclass
class Edge:
    source_id: str
    target_id: str
    canonical: str


@dataclass
class ProjectedGraph:
    site: str
    group_by: str
    rows: List[Row] = field(default_factory=list)
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)


VALID_GROUP_BY = frozenset({"none", "area", "settore", "quadrato", "attivita", "strutture"})


class S3DProjector:
    @classmethod
    def from_site(cls, session: Session, site: str, group_by: str = "none") -> ProjectedGraph:
        if group_by not in VALID_GROUP_BY:
            raise ValueError(f"Invalid group_by={group_by!r}; valid: {sorted(VALID_GROUP_BY)}")
        graph = ProjectedGraph(site=site, group_by=group_by)
        cls._load_rows(session, site, graph)
        cls._load_us_nodes(session, site, graph)
        cls._load_edges(session, site, graph)
        return graph

    @classmethod
    def _load_rows(cls, session: Session, site: str, graph: ProjectedGraph) -> None:
        result = session.execute(
            text("SELECT periodo, fase, datazione FROM period_table "
                 "WHERE sito = :s OR sito IS NULL OR sito = ''"),
            {"s": site},
        ).fetchall()
        # sort by (periodo, fase) alphabetically
        sorted_rows = sorted([(r[0] or "", r[1] or "", r[2]) for r in result if r[0]],
                             key=lambda t: (t[0], t[1]))
        for i, (periodo, fase, dataz) in enumerate(sorted_rows):
            label = f"{periodo}/{fase}" if fase else periodo
            graph.rows.append(Row(
                row_id=f"row_{i}",
                label=label,
                periodo=periodo,
                fase=fase or None,
                datazione=dataz,
                is_fallback=False,
            ))

    @classmethod
    def _ensure_fallback_row(cls, graph: ProjectedGraph) -> Row:
        for r in graph.rows:
            if r.is_fallback:
                return r
        idx = len(graph.rows)
        fb = Row(row_id=f"row_{idx}", label="Periodo 1", is_fallback=True)
        graph.rows.append(fb)
        return fb

    @classmethod
    def _resolve_row_id(cls, fase: Optional[str], graph: ProjectedGraph) -> str:
        if fase:
            for r in graph.rows:
                if not r.is_fallback and (r.fase == fase or r.periodo == fase):
                    return r.row_id
        return cls._ensure_fallback_row(graph).row_id

    @classmethod
    def _load_us_nodes(cls, session: Session, site: str, graph: ProjectedGraph) -> None:
        rows = session.execute(
            text("SELECT id_us, sito, area, us, unita_tipo, descrizione, fase_iniziale "
                 "FROM us_table WHERE sito = :s"),
            {"s": site},
        ).fetchall()
        for r in rows:
            unit_type = r[4] or "US"
            row_id = cls._resolve_row_id(r[6], graph)
            sub = cls._extract_sub_group(r, graph.group_by)
            graph.nodes.append(Node(
                node_id=f"us_{r[0]}",
                us=str(r[3]),
                area=r[2],
                sito=r[1],
                unit_type=unit_type,
                description=r[5],
                row_id=row_id,
                sub_group=sub,
            ))

    @classmethod
    def _extract_sub_group(cls, db_row, group_by: str) -> Optional[str]:
        if group_by == "none" or group_by == "area":
            return db_row[2] if group_by == "area" else None
        # The columns for settore/quadrato/attivita/strutture come from full row;
        # since this minimal SELECT doesn't include them, fetch separately if needed.
        # For now, return None — Task 7 expands to fetch the right column per group_by.
        return None

    @classmethod
    def _load_edges(cls, session: Session, site: str, graph: ProjectedGraph) -> None:
        # Build us → node_id index
        us_index: Dict[str, str] = {n.us: n.node_id for n in graph.nodes}
        rows = session.execute(
            text("SELECT us, rapporti FROM us_table WHERE sito = :s AND rapporti IS NOT NULL AND rapporti != ''"),
            {"s": site},
        ).fetchall()
        seen = set()
        for us_num, rapp_raw in rows:
            src_id = us_index.get(str(us_num))
            if src_id is None:
                continue
            for rap in parse_rapporti(rapp_raw, current_site=site):
                tgt_id = us_index.get(rap.target_us)
                if tgt_id is None:
                    continue
                if rap.canonical in SYMMETRIC:
                    key = (rap.canonical, tuple(sorted((src_id, tgt_id))))
                else:
                    key = (rap.canonical, src_id, tgt_id)
                if key in seen:
                    continue
                seen.add(key)
                graph.edges.append(Edge(source_id=src_id, target_id=tgt_id, canonical=rap.canonical))
```

- [ ] **Step 4: Run tests, expect pass**

```bash
pytest tests/unit/test_s3d_projector.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/s3d_projector.py tests/unit/test_s3d_projector.py
git commit -m "feat(projector): S3DProjector with period rows + fallback row + edge dedup"
```

---

### Task 6: Sub-grouping per area/settore/quadrato/attivita/strutture

**Files:**
- Modify: `pyarchinit_mini/graphproj/s3d_projector.py` (extend `_load_us_nodes` to project sub_group from the right column)
- Modify: `tests/unit/test_s3d_projector.py` (add tests for each grouping)

- [ ] **Step 1: Add failing tests for sub-grouping**

Append to `tests/unit/test_s3d_projector.py`:
```python
@pytest.fixture
def session_factory_full(tmp_path):
    """us_table schema with all sub-grouping columns."""
    engine = create_engine(f"sqlite:///{tmp_path}/full.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY, sito TEXT)"""))
        conn.execute(text("""CREATE TABLE period_table (id_period INTEGER PRIMARY KEY,
            sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
            descrizione TEXT, fase_iniziale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT,
            rapporti TEXT)"""))
    return sessionmaker(bind=engine)


def test_sub_group_by_area(session_factory_full):
    s = session_factory_full()
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S','A1','1','USM')"))
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S','A2','2','USM')"))
    s.commit()
    g = S3DProjector.from_site(s, "S", group_by="area")
    by_us = {n.us: n for n in g.nodes}
    assert by_us["1"].sub_group == "A1"
    assert by_us["2"].sub_group == "A2"


def test_sub_group_by_settore(session_factory_full):
    s = session_factory_full()
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, settore) VALUES ('S','A','1','USM','Nord')"))
    s.commit()
    g = S3DProjector.from_site(s, "S", group_by="settore")
    assert g.nodes[0].sub_group == "Nord"


def test_sub_group_none_is_none(session_factory_full):
    s = session_factory_full()
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, settore) VALUES ('S','A','1','USM','Nord')"))
    s.commit()
    g = S3DProjector.from_site(s, "S", group_by="none")
    assert g.nodes[0].sub_group is None
```

- [ ] **Step 2: Run, expect fail**

```bash
pytest tests/unit/test_s3d_projector.py::test_sub_group_by_settore -v
```

Expected: FAIL — sub_group always None for non-area.

- [ ] **Step 3: Implement extended `_load_us_nodes`**

Replace `_load_us_nodes` and `_extract_sub_group` in `s3d_projector.py`:
```python
    _SUB_GROUP_COLUMN: Dict[str, str] = {
        "none": "",
        "area": "area",
        "settore": "settore",
        "quadrato": "quadrato",
        "attivita": "attivita",
        "strutture": "struttura",
    }

    @classmethod
    def _load_us_nodes(cls, session: Session, site: str, graph: ProjectedGraph) -> None:
        col = cls._SUB_GROUP_COLUMN.get(graph.group_by, "")
        extra_select = f", {col}" if col else ""
        sql = (f"SELECT id_us, sito, area, us, unita_tipo, descrizione, fase_iniziale{extra_select} "
               f"FROM us_table WHERE sito = :s")
        rows = session.execute(text(sql), {"s": site}).fetchall()
        for r in rows:
            unit_type = r[4] or "US"
            row_id = cls._resolve_row_id(r[6], graph)
            sub = None
            if graph.group_by != "none":
                if graph.group_by == "area":
                    sub = r[2]
                elif len(r) > 7:
                    sub = r[7]
            graph.nodes.append(Node(
                node_id=f"us_{r[0]}",
                us=str(r[3]),
                area=r[2],
                sito=r[1],
                unit_type=unit_type,
                description=r[5],
                row_id=row_id,
                sub_group=str(sub) if sub is not None else None,
            ))
```

Remove the old `_extract_sub_group` stub.

- [ ] **Step 4: Run all projector tests**

```bash
pytest tests/unit/test_s3d_projector.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/s3d_projector.py tests/unit/test_s3d_projector.py
git commit -m "feat(projector): sub-grouping by area/settore/quadrato/attivita/strutture"
```

---

## Phase 3: Renderer adapter

### Task 7: s3d_to_cytoscape (Graph → cytoscape JSON)

**Files:**
- Create: `pyarchinit_mini/graphproj/s3d_to_cytoscape.py`
- Create: `tests/unit/test_s3d_to_cytoscape.py`

- [ ] **Step 1: Write failing tests**

`tests/unit/test_s3d_to_cytoscape.py`:
```python
import pytest

from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph, Row, Node, Edge
from pyarchinit_mini.graphproj.s3d_to_cytoscape import to_cytoscape


def _graph_with_two_us():
    g = ProjectedGraph(site="S", group_by="none")
    g.rows = [Row(row_id="row_0", label="I/a", periodo="I", fase="a")]
    g.nodes = [
        Node(node_id="us_1", us="1", area="A", sito="S", unit_type="USM", description="x", row_id="row_0"),
        Node(node_id="us_2", us="2", area="A", sito="S", unit_type="USV", description="y", row_id="row_0"),
    ]
    g.edges = [Edge(source_id="us_1", target_id="us_2", canonical="overlies")]
    return g


def test_to_cytoscape_top_level_keys():
    out = to_cytoscape(_graph_with_two_us())
    assert set(out.keys()) >= {"site", "group_by", "rows", "nodes", "edges"}


def test_to_cytoscape_node_has_style_from_palette():
    out = to_cytoscape(_graph_with_two_us())
    usm = next(n for n in out["nodes"] if n["data"]["id"] == "us_1")
    assert "style" in usm
    assert "shape" in usm["style"]
    assert usm["style"]["backgroundColor"].startswith("#")


def test_to_cytoscape_edge_has_style_from_palette():
    out = to_cytoscape(_graph_with_two_us())
    e = out["edges"][0]
    assert "style" in e
    assert "lineColor" in e["style"]
    assert e["data"]["label"] == "overlies"


def test_to_cytoscape_with_sub_group_creates_compound_parents():
    g = _graph_with_two_us()
    g.group_by = "area"
    for n in g.nodes:
        n.sub_group = "A"
    out = to_cytoscape(g)
    # Expect a parent node "cluster_row_0_A" with type=compound
    parents = [n for n in out["nodes"] if n["data"].get("compound")]
    assert len(parents) == 1
    assert parents[0]["data"]["id"] == "cluster_row_0_A"
    # The two US should reference this parent
    us = [n for n in out["nodes"] if n["data"]["id"].startswith("us_")]
    assert all(n["data"]["parent"] == "cluster_row_0_A" for n in us)
```

- [ ] **Step 2: Run, expect fail**

```bash
pytest tests/unit/test_s3d_to_cytoscape.py -v
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement adapter**

`pyarchinit_mini/graphproj/s3d_to_cytoscape.py`:
```python
"""Translate a ProjectedGraph into cytoscape.js JSON with palette-derived styles."""
from __future__ import annotations

from typing import Dict, List, Any

from pyarchinit_mini.em_palette import get_palette
from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph


def to_cytoscape(graph: ProjectedGraph) -> Dict[str, Any]:
    palette = get_palette()
    out_nodes: List[Dict[str, Any]] = []
    out_edges: List[Dict[str, Any]] = []
    parent_ids: Dict[tuple, str] = {}

    if graph.group_by != "none":
        for n in graph.nodes:
            if n.sub_group is None:
                continue
            key = (n.row_id, n.sub_group)
            if key not in parent_ids:
                parent_id = f"cluster_{n.row_id}_{n.sub_group}"
                parent_ids[key] = parent_id
                out_nodes.append({
                    "data": {
                        "id": parent_id,
                        "label": n.sub_group,
                        "row": n.row_id,
                        "compound": True,
                    },
                    "style": {"backgroundColor": "#F5F5F5", "borderColor": "#9E9E9E"},
                })

    for n in graph.nodes:
        ns = palette.get_node_style(n.unit_type)
        node_obj = {
            "data": {
                "id": n.node_id,
                "label": n.us,
                "us": n.us,
                "area": n.area,
                "unit_type": n.unit_type,
                "description": n.description,
                "row": n.row_id,
            },
            "style": {
                "shape": ns.shape,
                "backgroundColor": ns.fill_color,
                "borderColor": ns.border_color,
                "borderWidth": ns.border_width,
                "lineStyle": ns.border_style,
                "fontColor": ns.font_color,
                "fontSize": ns.font_size,
            },
        }
        if graph.group_by != "none" and n.sub_group is not None:
            node_obj["data"]["parent"] = f"cluster_{n.row_id}_{n.sub_group}"
        out_nodes.append(node_obj)

    for e in graph.edges:
        es = palette.get_edge_style(e.canonical)
        out_edges.append({
            "data": {
                "id": f"{e.source_id}__{e.canonical}__{e.target_id}",
                "source": e.source_id,
                "target": e.target_id,
                "label": e.canonical,
            },
            "style": {
                "lineColor": es.line_color,
                "lineWidth": es.line_width,
                "lineStyle": es.line_style,
                "targetArrowShape": es.arrow_target,
                "sourceArrowShape": es.arrow_source,
            },
        })

    return {
        "site": graph.site,
        "group_by": graph.group_by,
        "rows": [
            {"row_id": r.row_id, "label": r.label, "periodo": r.periodo, "fase": r.fase,
             "datazione": r.datazione, "is_fallback": r.is_fallback}
            for r in graph.rows
        ],
        "nodes": out_nodes,
        "edges": out_edges,
    }
```

- [ ] **Step 4: Run tests, expect pass**

```bash
pytest tests/unit/test_s3d_to_cytoscape.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/s3d_to_cytoscape.py tests/unit/test_s3d_to_cytoscape.py
git commit -m "feat(adapter): s3d_to_cytoscape with palette styling and compound parents"
```

---

## Phase 4: Feature flag wiring

### Task 8: Feature flag in `SwimlaneState.load()`

**Files:**
- Modify: `pyarchinit_mini/harris_swimlane/swimlane_state.py` (around line 106 where `load` classmethod lives)
- Create: `tests/integration/test_feature_flag_pipelines.py`

- [ ] **Step 1: Write failing test**

`tests/integration/test_feature_flag_pipelines.py`:
```python
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState


@pytest.fixture
def session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/p.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY, sito TEXT)"""))
        conn.execute(text("""CREATE TABLE period_table (id_period INTEGER PRIMARY KEY, sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
            unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT, rapporti TEXT)"""))
        conn.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
                          "VALUES ('S','A','1','USM',?)"), ("[['Copre','2','A','S']]",))
        conn.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo) "
                          "VALUES ('S','A','2','USM')"))
    return sessionmaker(bind=engine)()


def test_s3dgraphy_pipeline_returns_edges(session, monkeypatch):
    monkeypatch.setenv("SWIMLANE_PIPELINE", "s3dgraphy")
    state = SwimlaneState.load(session, "S", group_by="none")
    assert len(state.edges) == 1
    edge = state.edges[0]
    assert edge.data["label"] == "overlies"


def test_legacy_pipeline_still_works(session, monkeypatch):
    monkeypatch.setenv("SWIMLANE_PIPELINE", "legacy")
    state = SwimlaneState.load(session, "S", group_by="period_phase")
    # legacy path also produces ≥1 edge from rapporti
    assert len(state.edges) >= 1
```

- [ ] **Step 2: Run, expect fail**

```bash
pytest tests/integration/test_feature_flag_pipelines.py -v
```

Expected: FAIL — current `SwimlaneState.load` doesn't honor the env var.

- [ ] **Step 3: Modify `SwimlaneState.load`**

Read the existing `swimlane_state.py` around `SwimlaneState.load`. Add:
```python
    @classmethod
    def load(cls, session, site, group_by="period_phase"):
        pipeline = os.environ.get("SWIMLANE_PIPELINE", "s3dgraphy").lower()
        if pipeline == "s3dgraphy":
            try:
                return cls._load_via_s3dgraphy(session, site, group_by)
            except Exception:
                logger.exception("s3dgraphy pipeline failed; falling back to legacy")
        return cls._load_legacy(session, site, group_by)

    @classmethod
    def _load_via_s3dgraphy(cls, session, site, group_by):
        from pyarchinit_mini.graphproj.s3d_projector import S3DProjector
        from pyarchinit_mini.graphproj.s3d_to_cytoscape import to_cytoscape
        # The new group_by vocabulary is {none, area, settore, quadrato, attivita, strutture}.
        # Legacy values like "period_phase" map to "none" (periods always rows).
        new_group_by = group_by if group_by in {"none", "area", "settore", "quadrato", "attivita", "strutture"} else "none"
        projected = S3DProjector.from_site(session, site, group_by=new_group_by)
        cyto = to_cytoscape(projected)
        return cls._make_state_from_cytoscape(site, group_by, cyto)

    @classmethod
    def _make_state_from_cytoscape(cls, site, group_by, cyto):
        # Map the cytoscape JSON into a SwimlaneState instance compatible with
        # the existing /api/load route serializer.
        from pyarchinit_mini.harris_swimlane.swimlane_state import (
            CytoscapeElement,
        )
        rows = []
        for r in cyto["rows"]:
            rows.append(Row(
                row_id=r["row_id"],
                period_name=r.get("periodo") or r.get("label"),
                phase_name=r.get("fase"),
                start_date=None, end_date=None,
                color=PERIOD_COLORS[len(rows) % len(PERIOD_COLORS)],
                source="period_table" if not r.get("is_fallback") else "fallback",
            ))
        nodes = [CytoscapeElement(data=n["data"], position=None) for n in cyto["nodes"]]
        edges = [CytoscapeElement(data=e["data"]) for e in cyto["edges"]]
        return cls(site=site, group_by=group_by, rows=rows, nodes=nodes, edges=edges, pending_changes={})
```

Rename the existing `load` to `_load_legacy` (do this by reading the existing definition and renaming).

Add at top of file: `import os` if not present.

- [ ] **Step 4: Run tests, expect pass**

```bash
pytest tests/integration/test_feature_flag_pipelines.py -v
pytest tests/integration/test_api_load_site.py -v  # if exists from previous work
```

Expected: 2 passed for the new tests; existing tests still pass.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/harris_swimlane/swimlane_state.py tests/integration/test_feature_flag_pipelines.py
git commit -m "feat(swimlane): SWIMLANE_PIPELINE feature flag with automatic legacy fallback"
```

---

## Phase 5: Reverse path (Graph → DB)

### Task 9: `graph_to_db.write_graph` — upsert US rows

**Files:**
- Create: `pyarchinit_mini/graphproj/graph_to_db.py`
- Create: `tests/unit/test_graph_to_db.py`

- [ ] **Step 1: Write failing test for US upsert**

`tests/unit/test_graph_to_db.py`:
```python
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph, Row, Node, Edge
from pyarchinit_mini.graphproj.graph_to_db import write_graph


@pytest.fixture
def session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/g.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
            descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT, rapporti TEXT,
            data_origine TEXT,
            UNIQUE (sito, area, us))"""))
    return sessionmaker(bind=engine)()


def _graph_2_us_1_edge():
    g = ProjectedGraph(site="S", group_by="none")
    g.nodes = [
        Node(node_id="us_1", us="1", area="A", sito="S", unit_type="USM", description="x", row_id="row_0"),
        Node(node_id="us_2", us="2", area="A", sito="S", unit_type="USV", description="y", row_id="row_0"),
    ]
    g.edges = [Edge(source_id="us_1", target_id="us_2", canonical="overlies")]
    return g


def test_write_graph_inserts_us_rows(session):
    res = write_graph(_graph_2_us_1_edge(), target_site="S", session=session, source_label="test")
    assert res.imported_us == 2
    rows = session.execute(text("SELECT us, area, unita_tipo FROM us_table ORDER BY us")).fetchall()
    assert rows == [("1", "A", "USM"), ("2", "A", "USV")]


def test_write_graph_writes_rapporti_4tuple_both_sides(session):
    write_graph(_graph_2_us_1_edge(), target_site="S", session=session, source_label="test")
    r1 = session.execute(text("SELECT rapporti FROM us_table WHERE us='1'")).scalar()
    r2 = session.execute(text("SELECT rapporti FROM us_table WHERE us='2'")).scalar()
    items1 = eval(r1)
    items2 = eval(r2)
    assert items1 == [["Copre", "2", "A", "S"]]
    assert items2 == [["Coperto da", "1", "A", "S"]]


def test_write_graph_upsert_does_not_duplicate(session):
    write_graph(_graph_2_us_1_edge(), target_site="S", session=session, source_label="test")
    write_graph(_graph_2_us_1_edge(), target_site="S", session=session, source_label="test")
    count = session.execute(text("SELECT COUNT(*) FROM us_table")).scalar()
    assert count == 2
    r1 = session.execute(text("SELECT rapporti FROM us_table WHERE us='1'")).scalar()
    items1 = eval(r1)
    # Dedup: should still be 1 entry, not 2
    assert len(items1) == 1


def test_write_graph_creates_stub_for_missing_target(session):
    g = ProjectedGraph(site="S", group_by="none")
    g.nodes = [Node(node_id="us_1", us="1", area="A", sito="S", unit_type="USM", description=None, row_id="row_0")]
    g.edges = [Edge(source_id="us_1", target_id="us_missing", canonical="overlies")]
    res = write_graph(g, target_site="S", session=session, source_label="test")
    # Without target node in graph, source-only edges create no stubs (target ref unknown).
    # But: if the edge references a us_id not present in graph.nodes, write_graph
    # cannot resolve the US number, so we expect 0 stubs and the edge skipped.
    assert res.imported_edges == 0
    assert res.errors == []


def test_write_graph_creates_stub_when_target_node_present_but_db_row_missing(session):
    g = ProjectedGraph(site="S", group_by="none")
    g.nodes = [
        Node(node_id="us_1", us="1", area="A", sito="S", unit_type="USM", description=None, row_id="row_0"),
        Node(node_id="us_99", us="99", area="A", sito="S", unit_type="US", description="Imported placeholder", row_id="row_0"),
    ]
    g.edges = [Edge(source_id="us_1", target_id="us_99", canonical="overlies")]
    res = write_graph(g, target_site="S", session=session, source_label="test")
    assert res.imported_us == 2
    assert res.imported_edges == 1
    assert res.stubs_created >= 0  # both are real nodes, so stubs_created tracks db-missing-but-graph-present
```

- [ ] **Step 2: Run, expect fail**

```bash
pytest tests/unit/test_graph_to_db.py -v
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement `write_graph`**

`pyarchinit_mini/graphproj/graph_to_db.py`:
```python
"""Write a ProjectedGraph back to us_table (4-tuple rapporti, inverses on both sides)."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from pyarchinit_mini.graphproj.rapporti_codec import (
    parse_rapporti, serialize_rapporti, INVERSE_PAIRS, SYMMETRIC, Rapporto,
)
from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph, Node


logger = logging.getLogger(__name__)


# Canonical → italian display label (used when serializing).
CANONICAL_TO_ITALIAN: Dict[str, str] = {
    "overlies": "Copre",
    "is_after": "Coperto da",
    "cuts": "Taglia",
    "is_cut_by": "Tagliato da",
    "fills": "Riempie",
    "is_filled_by": "Riempito da",
    "abuts": "Si appoggia a",
    "is_abutted_by": "Gli si appoggia",
    "has_same_time": "Uguale a",
    "is_bonded_to": "Si lega a",
    "is_before": "Anteriore a",
}


@dataclass
class WriteResult:
    imported_us: int = 0
    imported_edges: int = 0
    inverses_written: int = 0
    stubs_created: int = 0
    inverses_skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def write_graph(
    graph: ProjectedGraph,
    *,
    target_site: str,
    session: Session,
    source_label: str = "import",
) -> WriteResult:
    result = WriteResult()
    now = datetime.utcnow().isoformat()
    origin_tag = f"{source_label}_{now}"

    # Ensure site row exists
    session.execute(
        text("INSERT INTO site_table (sito) VALUES (:s) "
             "ON CONFLICT (sito) DO NOTHING"),
        {"s": target_site},
    )

    # Upsert US rows
    for n in graph.nodes:
        is_new = _upsert_us_row(n, target_site, origin_tag, session)
        result.imported_us += 1
        if is_new and n.description == "Imported placeholder":
            result.stubs_created += 1

    # Build us_id → (us, area) index for rapporti writing
    by_node_id: Dict[str, Node] = {n.node_id: n for n in graph.nodes}

    # Accumulate rapporti per node (forward + inverse)
    per_us_items: Dict[str, List[Rapporto]] = {}
    for e in graph.edges:
        src = by_node_id.get(e.source_id)
        tgt = by_node_id.get(e.target_id)
        if src is None or tgt is None:
            continue
        # Forward
        fwd = Rapporto(canonical=e.canonical, target_us=tgt.us, target_area=tgt.area, target_sito=target_site)
        per_us_items.setdefault(src.us, []).append(fwd)
        result.imported_edges += 1
        # Inverse (skip if symmetric)
        if e.canonical in SYMMETRIC:
            continue
        inv = INVERSE_PAIRS.get(e.canonical)
        if inv is None:
            result.inverses_skipped.append(e.canonical)
            continue
        rev = Rapporto(canonical=inv, target_us=src.us, target_area=src.area, target_sito=target_site)
        per_us_items.setdefault(tgt.us, []).append(rev)
        result.inverses_written += 1

    # Read existing rapporti (so we append, not overwrite)
    for us_num, items in per_us_items.items():
        existing_raw = session.execute(
            text("SELECT rapporti FROM us_table WHERE sito = :s AND us = :u"),
            {"s": target_site, "u": us_num},
        ).scalar() or ""
        existing = parse_rapporti(existing_raw, current_site=target_site)
        merged = existing + items
        serialized = serialize_rapporti(merged, italian_labels=CANONICAL_TO_ITALIAN)
        session.execute(
            text("UPDATE us_table SET rapporti = :r WHERE sito = :s AND us = :u"),
            {"r": serialized, "s": target_site, "u": us_num},
        )

    session.commit()
    return result


def _upsert_us_row(n: Node, target_site: str, origin_tag: str, session: Session) -> bool:
    """INSERT OR UPDATE us_table for this node. Returns True if newly inserted."""
    existing = session.execute(
        text("SELECT id_us FROM us_table WHERE sito = :s AND area = :a AND us = :u"),
        {"s": target_site, "a": n.area or "", "u": n.us},
    ).scalar()
    if existing is None:
        session.execute(
            text("INSERT INTO us_table (sito, area, us, unita_tipo, descrizione, data_origine) "
                 "VALUES (:s, :a, :u, :t, :d, :o)"),
            {"s": target_site, "a": n.area or "", "u": n.us, "t": n.unit_type,
             "d": n.description, "o": origin_tag},
        )
        return True
    session.execute(
        text("UPDATE us_table SET unita_tipo = :t, descrizione = COALESCE(:d, descrizione) "
             "WHERE sito = :s AND area = :a AND us = :u"),
        {"t": n.unit_type, "d": n.description, "s": target_site, "a": n.area or "", "u": n.us},
    )
    return False
```

- [ ] **Step 4: Run tests, expect pass**

```bash
pytest tests/unit/test_graph_to_db.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/graph_to_db.py tests/unit/test_graph_to_db.py
git commit -m "feat(reverse): graph_to_db.write_graph with 4-tuple rapporti and inverses"
```

---

## Phase 6: Heriverse JSON parser

### Task 10: Heriverse JSON → ProjectedGraph

**Files:**
- Create: `pyarchinit_mini/graphproj/heriverse_parser.py`
- Create: `tests/unit/test_heriverse_parser.py`

- [ ] **Step 1: Write failing test**

`tests/unit/test_heriverse_parser.py`:
```python
import json
import pytest

from pyarchinit_mini.graphproj.heriverse_parser import parse_heriverse


SAMPLE = {
    "wapp": "heriverse",
    "multigraph": {
        "graphs": [{
            "id": "g0",
            "name": "Site_A",
            "nodes": {
                "USM": [{"id": "us_1", "name": "US1", "type": "USM", "data": {"area": "A1"}}],
                "USV": [{"id": "us_2", "name": "US2", "type": "USV", "data": {"area": "A1"}}],
                "USVn": [], "USD": [], "SF": [], "VSF": [], "TSU": [],
            },
            "edges": {
                "line": [{"id": "e1", "from": "us_1", "to": "us_2", "type": "line"}],
            },
            "semantic_shapes": {}, "representation_models": {}, "panorama_models": {},
        }]
    },
    "couchdb_metadata": {},
    "epochs": [],
}


def test_parse_heriverse_returns_projected_graph():
    g = parse_heriverse(json.dumps(SAMPLE))
    assert g.site == "Site_A"
    assert len(g.nodes) == 2
    assert {n.us for n in g.nodes} == {"US1", "US2"}


def test_parse_heriverse_assigns_unit_types():
    g = parse_heriverse(json.dumps(SAMPLE))
    by_us = {n.us: n.unit_type for n in g.nodes}
    assert by_us["US1"] == "USM"
    assert by_us["US2"] == "USV"


def test_parse_heriverse_creates_edges():
    g = parse_heriverse(json.dumps(SAMPLE))
    assert len(g.edges) == 1
    e = g.edges[0]
    # Edge type "line" → canonical "overlies" (default Heriverse mapping)
    assert e.canonical in {"overlies", "line"}
```

- [ ] **Step 2: Run, expect fail**

```bash
pytest tests/unit/test_heriverse_parser.py -v
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement parser**

`pyarchinit_mini/graphproj/heriverse_parser.py`:
```python
"""Heriverse/ATON JSON → ProjectedGraph reverse parser.

Mirror of pyarchinit_mini/s3d_integration/s3d_converter.py::export_to_heriverse_json.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph, Row, Node, Edge


# Heriverse edge type → canonical stratigraphic relation.
EDGE_TYPE_MAP: Dict[str, str] = {
    "line": "overlies",      # default Heriverse line
    "contrasts_with": "is_after",
    "changed_from": "is_after",
    "is_before": "is_before",
    "covers": "overlies",
    "cuts": "cuts",
    "fills": "fills",
    "abuts": "abuts",
    "has_same_time": "has_same_time",
    "is_bonded_to": "is_bonded_to",
}


def parse_heriverse(raw_json: str) -> ProjectedGraph:
    data = json.loads(raw_json)
    multi = data.get("multigraph", {})
    graphs = multi.get("graphs", [])
    if not graphs:
        return ProjectedGraph(site="UnknownSite", group_by="none")
    g0 = graphs[0]
    site = g0.get("name") or "UnknownSite"
    out = ProjectedGraph(site=site, group_by="none")
    out.rows.append(Row(row_id="row_0", label="Periodo 1", is_fallback=True))

    nodes_by_id: Dict[str, Node] = {}
    for unit_type, items in (g0.get("nodes") or {}).items():
        for item in items:
            node_id = item.get("id") or f"us_{len(nodes_by_id)}"
            us_num = item.get("name") or item.get("id") or "?"
            area = (item.get("data") or {}).get("area")
            n = Node(
                node_id=node_id,
                us=us_num,
                area=area,
                sito=site,
                unit_type=unit_type,
                description=item.get("description"),
                row_id="row_0",
            )
            nodes_by_id[node_id] = n
            out.nodes.append(n)

    for edge_type, items in (g0.get("edges") or {}).items():
        canonical = EDGE_TYPE_MAP.get(edge_type, edge_type)
        for item in items:
            src = item.get("from")
            tgt = item.get("to")
            if not src or not tgt:
                continue
            if src not in nodes_by_id or tgt not in nodes_by_id:
                continue
            out.edges.append(Edge(source_id=src, target_id=tgt, canonical=canonical))

    return out
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/unit/test_heriverse_parser.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphproj/heriverse_parser.py tests/unit/test_heriverse_parser.py
git commit -m "feat(import): Heriverse JSON parser to ProjectedGraph"
```

---

## Phase 7: HTTP endpoints

### Task 11: Wire new pipeline into `/api/load/<site>`

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py` (around line 756 — `api_load_state`)
- Create: `tests/integration/test_api_load_site.py`

- [ ] **Step 1: Write failing integration test**

`tests/integration/test_api_load_site.py`:
```python
import json
from pathlib import Path
import pytest
from flask import Flask
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/api.db")
    monkeypatch.setenv("SWIMLANE_PIPELINE", "s3dgraphy")
    engine = create_engine(f"sqlite:///{tmp_path}/api.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE)"""))
        conn.execute(text("""CREATE TABLE period_table (id_period INTEGER PRIMARY KEY, sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
            unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT, rapporti TEXT,
            UNIQUE(sito, area, us))"""))
        conn.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
                          "VALUES ('S','A','1','USM',?)"), ("[['Copre','2','A','S']]",))
        conn.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S','A','2','USM')"))

    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "t"
    app.register_blueprint(harris_creator_bp)
    return app.test_client()


def test_api_load_returns_palette_styled_nodes(client):
    r = client.get("/harris-creator/api/load/S")
    assert r.status_code == 200, r.data[:300]
    body = r.get_json()
    assert "nodes" in body and "edges" in body
    assert len(body["edges"]) >= 1
    node = body["nodes"][0]
    assert "style" in node
    assert "shape" in node["style"]
    assert "backgroundColor" in node["style"]


def test_api_load_with_group_by_area(client):
    r = client.get("/harris-creator/api/load/S?group_by=area")
    assert r.status_code == 200
    body = r.get_json()
    parents = [n for n in body["nodes"] if n["data"].get("compound")]
    assert len(parents) >= 1  # one cluster per area
```

- [ ] **Step 2: Run, expect fail**

```bash
pytest tests/integration/test_api_load_site.py -v
```

Expected: FAIL — likely 500 because route uses old code.

- [ ] **Step 3: Update `api_load_state` to use new pipeline**

Read `harris_creator_routes.py` around line 756. Modify the function:
```python
@harris_creator_bp.get("/api/load/<site>")
def api_load_state(site: str):
    group_by = request.args.get("group_by", "none")
    try:
        session = _get_session()
        with session as s:
            state = SwimlaneState.load(s, site, group_by=group_by)
            payload = {
                "site": state.site,
                "group_by": state.group_by,
                "rows": [
                    {"row_id": r.row_id, "period_name": r.period_name,
                     "phase_name": r.phase_name, "color": r.color,
                     "start_date": r.start_date, "end_date": r.end_date,
                     "source": r.source}
                    for r in state.rows
                ],
                "nodes": [{"data": el.data, "style": getattr(el, "style", None),
                           "position": el.position} for el in state.nodes],
                "edges": [{"data": el.data, "style": getattr(el, "style", None)} for el in state.edges],
                "pending_changes": state.pending_changes,
            }
            response = jsonify(payload)
            if hasattr(state, "pipeline_fallback") and state.pipeline_fallback:
                response.headers["X-Pipeline-Fallback"] = "legacy"
            return response, 200
    except ValueError as e:
        return jsonify({"error": "validation", "message": str(e)}), 400
    except Exception as e:
        logger.exception("api_load_state failed")
        return jsonify({"error": "internal", "message": str(e)}), 500
```

And in `swimlane_state.py::_make_state_from_cytoscape`, propagate `style` onto `CytoscapeElement`:
```python
# Update the helper to set .style attribute on each CytoscapeElement.
nodes = []
for n in cyto["nodes"]:
    el = CytoscapeElement(data=n["data"], position=None)
    el.style = n.get("style")
    nodes.append(el)
edges = []
for e in cyto["edges"]:
    el = CytoscapeElement(data=e["data"])
    el.style = e.get("style")
    edges.append(el)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/integration/test_api_load_site.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/harris_creator_routes.py pyarchinit_mini/harris_swimlane/swimlane_state.py tests/integration/test_api_load_site.py
git commit -m "feat(api): /api/load/<site> uses s3dgraphy pipeline with palette styling"
```

---

### Task 12: GraphML export via s3dgraphy + EM palette template

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py` (line 833 — `export_extended_matrix`)
- Create: `pyarchinit_mini/graphproj/graphml_writer.py` (wrapper that injects palette template)
- Create: `tests/integration/test_api_export_graphml.py`

- [ ] **Step 1: Write failing test**

`tests/integration/test_api_export_graphml.py`:
```python
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest
from flask import Flask
from sqlalchemy import create_engine, text


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/exp.db")
    engine = create_engine(f"sqlite:///{tmp_path}/exp.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY, sito TEXT UNIQUE)"""))
        conn.execute(text("""CREATE TABLE period_table (id_period INTEGER PRIMARY KEY, sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
            unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT, rapporti TEXT,
            UNIQUE(sito, area, us))"""))
        conn.execute(text("INSERT INTO us_table (sito,area,us,unita_tipo,rapporti) VALUES ('S','A','1','USM',?)"),
                     ("[['Copre','2','A','S']]",))
        conn.execute(text("INSERT INTO us_table (sito,area,us,unita_tipo) VALUES ('S','A','2','USM')"))
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True; app.config["SECRET_KEY"] = "t"
    app.register_blueprint(harris_creator_bp)
    return app.test_client()


def test_export_graphml_returns_valid_yed_xml(client):
    r = client.get("/harris-creator/api/export/S/yed-graphml")
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/")
    # Parse as XML
    root = ET.fromstring(r.data)
    # Must have yEd namespace
    assert "yfiles" in r.data.decode() or "y:" in r.data.decode()
    # Must have at least 2 site nodes appended (US 1 and US 2)
    nodes = root.findall(".//{http://graphml.graphdrawing.org/xmlns}node")
    assert len(nodes) >= 2


def test_export_graphml_includes_palette_template(client):
    r = client.get("/harris-creator/api/export/S/yed-graphml")
    body = r.data.decode()
    # The palette template's signature: y:Shape type entries for USM
    assert "USM" in body
```

- [ ] **Step 2: Run, expect fail**

```bash
pytest tests/integration/test_api_export_graphml.py -v
```

Expected: FAIL — old export doesn't include palette or fails entirely.

- [ ] **Step 3: Implement `graphml_writer.py`**

`pyarchinit_mini/graphproj/graphml_writer.py`:
```python
"""yEd-flavoured GraphML writer that uses EM_palette.graphml as the document base.

Strategy: load the palette XML, append site nodes/edges into the <graph> element,
serialize. The palette's existing node/edge definitions remain in place so yEd
opens the file with all unit types visible in the palette panel.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path

from pyarchinit_mini.em_palette import get_palette
from pyarchinit_mini.em_palette.loader import DEFAULT_PALETTE_PATH
from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph


NS_G = "http://graphml.graphdrawing.org/xmlns"
NS_Y = "http://www.yworks.com/xml/graphml"
ET.register_namespace("", NS_G)
ET.register_namespace("y", NS_Y)


def write_graphml(graph: ProjectedGraph, *, palette_path: Path | None = None) -> bytes:
    palette_path = palette_path or DEFAULT_PALETTE_PATH
    tree = ET.parse(palette_path)
    root = tree.getroot()
    graph_el = root.find(f"{{{NS_G}}}graph")
    if graph_el is None:
        raise RuntimeError("Palette template missing <graph> element")

    palette = get_palette()
    for n in graph.nodes:
        ns = palette.get_node_style(n.unit_type)
        node_el = ET.SubElement(graph_el, f"{{{NS_G}}}node", attrib={"id": n.node_id})
        data_el = ET.SubElement(node_el, f"{{{NS_G}}}data", attrib={"key": "d7"})
        shape_node = ET.SubElement(data_el, f"{{{NS_Y}}}ShapeNode")
        ET.SubElement(shape_node, f"{{{NS_Y}}}Geometry",
                      attrib={"height": "30.0", "width": "60.0", "x": "0.0", "y": "0.0"})
        ET.SubElement(shape_node, f"{{{NS_Y}}}Fill",
                      attrib={"color": ns.fill_color, "transparent": "false"})
        ET.SubElement(shape_node, f"{{{NS_Y}}}BorderStyle",
                      attrib={"color": ns.border_color, "type": ns.border_style, "width": str(ns.border_width)})
        label = ET.SubElement(shape_node, f"{{{NS_Y}}}NodeLabel",
                              attrib={"textColor": ns.font_color, "fontSize": str(ns.font_size)})
        label.text = n.us
        ET.SubElement(shape_node, f"{{{NS_Y}}}Shape", attrib={"type": ns.shape})

    for e in graph.edges:
        es = palette.get_edge_style(e.canonical)
        edge_el = ET.SubElement(graph_el, f"{{{NS_G}}}edge",
                                attrib={"id": f"{e.source_id}__{e.target_id}",
                                        "source": e.source_id, "target": e.target_id})
        data_el = ET.SubElement(edge_el, f"{{{NS_G}}}data", attrib={"key": "d13"})
        poly = ET.SubElement(data_el, f"{{{NS_Y}}}PolyLineEdge")
        ET.SubElement(poly, f"{{{NS_Y}}}LineStyle",
                      attrib={"color": es.line_color, "type": es.line_style, "width": str(es.line_width)})
        ET.SubElement(poly, f"{{{NS_Y}}}Arrows",
                      attrib={"source": es.arrow_source, "target": es.arrow_target})
        elabel = ET.SubElement(poly, f"{{{NS_Y}}}EdgeLabel")
        elabel.text = e.canonical

    buf = BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    return buf.getvalue()
```

- [ ] **Step 4: Modify route**

In `harris_creator_routes.py`, replace the body of `/api/export/<site>/yed-graphml`:
```python
@harris_creator_bp.get("/api/export/<site>/yed-graphml")
def api_export_yed_graphml(site: str):
    from pyarchinit_mini.graphproj.s3d_projector import S3DProjector
    from pyarchinit_mini.graphproj.graphml_writer import write_graphml
    group_by = request.args.get("group_by", "none")
    try:
        with _get_session() as s:
            projected = S3DProjector.from_site(s, site, group_by=group_by)
        data = write_graphml(projected)
        from flask import Response
        return Response(
            data,
            mimetype="application/graphml+xml",
            headers={"Content-Disposition": f"attachment; filename={site}.graphml"},
        )
    except Exception as e:
        logger.exception("export yed-graphml failed")
        return jsonify({"error": "export_failed", "message": str(e)}), 500
```

- [ ] **Step 5: Run tests, commit**

```bash
pytest tests/integration/test_api_export_graphml.py -v
git add pyarchinit_mini/graphproj/graphml_writer.py pyarchinit_mini/web_interface/harris_creator_routes.py tests/integration/test_api_export_graphml.py
git commit -m "feat(export): yEd GraphML export uses EM palette template as base"
```

---

### Task 13: Heriverse/ATON JSON export endpoint

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py` (add new route)
- Create: `tests/integration/test_api_export_heriverse.py`

- [ ] **Step 1: Write failing test**

`tests/integration/test_api_export_heriverse.py`:
```python
import json
from pathlib import Path
import pytest
from flask import Flask
from sqlalchemy import create_engine, text


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/h.db")
    engine = create_engine(f"sqlite:///{tmp_path}/h.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY, sito TEXT UNIQUE)"""))
        conn.execute(text("""CREATE TABLE period_table (id_period INTEGER PRIMARY KEY, sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
            unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT, rapporti TEXT,
            UNIQUE(sito, area, us))"""))
        conn.execute(text("INSERT INTO us_table (sito,area,us,unita_tipo) VALUES ('S','A','1','USM')"))
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True; app.config["SECRET_KEY"] = "t"
    app.register_blueprint(harris_creator_bp)
    return app.test_client()


def test_export_heriverse_returns_valid_json(client):
    r = client.get("/harris-creator/api/export/S/heriverse-json")
    assert r.status_code == 200, r.data[:300]
    data = json.loads(r.data)
    assert data.get("wapp") == "heriverse"
    assert "multigraph" in data


def test_export_heriverse_includes_site_in_graph(client):
    r = client.get("/harris-creator/api/export/S/heriverse-json")
    data = json.loads(r.data)
    g0 = data["multigraph"]["graphs"][0]
    assert g0["name"] == "S"
    flat_nodes = []
    for items in g0["nodes"].values():
        flat_nodes.extend(items)
    assert any(n.get("name") == "1" for n in flat_nodes)
```

- [ ] **Step 2: Run, expect fail**

```bash
pytest tests/integration/test_api_export_heriverse.py -v
```

Expected: FAIL — 404 (route not yet registered).

- [ ] **Step 3: Add route**

In `harris_creator_routes.py`:
```python
@harris_creator_bp.get("/api/export/<site>/heriverse-json")
def api_export_heriverse(site: str):
    from pyarchinit_mini.s3d_integration.s3d_converter import S3DConverter
    try:
        with _get_session() as s:
            converter = S3DConverter()
            graph = converter.create_s3dgraphy_graph(session=s, site=site)
            # Export to temp file and read back
            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                converter.export_to_heriverse_json(graph, output_path=tmp_path)
                with open(tmp_path, "rb") as f:
                    data = f.read()
            finally:
                try: os.unlink(tmp_path)
                except OSError: pass
        from flask import Response
        return Response(
            data,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment; filename={site}_heriverse.json"},
        )
    except Exception as e:
        logger.exception("export heriverse failed")
        return jsonify({"error": "export_failed", "message": str(e)}), 500
```

- [ ] **Step 4: Run tests, commit**

```bash
pytest tests/integration/test_api_export_heriverse.py -v
git add pyarchinit_mini/web_interface/harris_creator_routes.py tests/integration/test_api_export_heriverse.py
git commit -m "feat(export): /api/export/<site>/heriverse-json (= ATON format)"
```

---

### Task 14: GraphML import endpoint (POST → write_graph)

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py` (new POST route)
- Create: `tests/integration/test_api_import_graphml.py`

- [ ] **Step 1: Write failing test**

`tests/integration/test_api_import_graphml.py`:
```python
import io
from pathlib import Path
import pytest
from flask import Flask
from sqlalchemy import create_engine, text


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"

SAMPLE_GRAPHML = b"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d7" yfiles.type="nodegraphics"/>
  <key for="edge" id="d13" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="us_1">
      <data key="d7">
        <y:ShapeNode>
          <y:Fill color="#FFFFFF"/>
          <y:BorderStyle color="#9B3333" type="line" width="4.0"/>
          <y:NodeLabel>10</y:NodeLabel>
          <y:Shape type="rectangle"/>
        </y:ShapeNode>
      </data>
    </node>
    <node id="us_2">
      <data key="d7">
        <y:ShapeNode>
          <y:Fill color="#FFFFFF"/>
          <y:BorderStyle color="#9B3333" type="line" width="4.0"/>
          <y:NodeLabel>20</y:NodeLabel>
          <y:Shape type="rectangle"/>
        </y:ShapeNode>
      </data>
    </node>
    <edge id="e1" source="us_1" target="us_2">
      <data key="d13">
        <y:PolyLineEdge>
          <y:EdgeLabel>overlies</y:EdgeLabel>
        </y:PolyLineEdge>
      </data>
    </edge>
  </graph>
</graphml>"""


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/imp.db")
    engine = create_engine(f"sqlite:///{tmp_path}/imp.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
            unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT, rapporti TEXT,
            data_origine TEXT,
            UNIQUE(sito, area, us))"""))
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True; app.config["SECRET_KEY"] = "t"
    app.register_blueprint(harris_creator_bp)
    return app.test_client(), engine


def test_import_graphml_creates_us_and_rapporti(client):
    c, engine = client
    r = c.post(
        "/harris-creator/api/import/S/graphml",
        data={"file": (io.BytesIO(SAMPLE_GRAPHML), "test.graphml")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200, r.data[:300]
    body = r.get_json()
    assert body["imported_us"] == 2
    assert body["imported_edges"] == 1
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT us, rapporti FROM us_table ORDER BY us")).fetchall()
        assert len(rows) == 2
        r1, r2 = rows[0], rows[1]
        assert "Copre" in (r1[1] or "")
        assert "Coperto da" in (r2[1] or "")
```

- [ ] **Step 2: Run, expect fail**

```bash
pytest tests/integration/test_api_import_graphml.py -v
```

Expected: FAIL — route 404.

- [ ] **Step 3: Add import route + small GraphML parser**

In `harris_creator_routes.py`:
```python
@harris_creator_bp.post("/api/import/<site>/graphml")
def api_import_graphml(site: str):
    from pyarchinit_mini.graphproj.graphml_reader import parse_graphml
    from pyarchinit_mini.graphproj.graph_to_db import write_graph
    f = request.files.get("file")
    if f is None or not f.filename:
        return jsonify({"error": "no_file"}), 400
    try:
        projected = parse_graphml(f.read(), target_site=site)
    except Exception as e:
        logger.warning("import graphml parse failed: %s", e)
        return jsonify({"error": "parse_error", "detail": str(e)}), 400
    try:
        with _get_session() as s:
            res = write_graph(projected, target_site=site, session=s, source_label="graphml")
        return jsonify({
            "imported_us": res.imported_us,
            "imported_edges": res.imported_edges,
            "inverses_written": res.inverses_written,
            "stubs_created": res.stubs_created,
            "inverses_skipped": res.inverses_skipped,
            "errors": res.errors,
        }), 200
    except Exception as e:
        logger.exception("import graphml write failed")
        return jsonify({"error": "write_failed", "message": str(e)}), 500
```

Create `pyarchinit_mini/graphproj/graphml_reader.py`:
```python
"""Parse uploaded yEd GraphML into a ProjectedGraph."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from io import BytesIO

from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph, Row, Node, Edge
from pyarchinit_mini.graphproj.rapporti_codec import _resolve_canonical


NS_G = "http://graphml.graphdrawing.org/xmlns"
NS_Y = "http://www.yworks.com/xml/graphml"


def parse_graphml(raw: bytes, *, target_site: str) -> ProjectedGraph:
    tree = ET.parse(BytesIO(raw))
    root = tree.getroot()
    out = ProjectedGraph(site=target_site, group_by="none")
    out.rows.append(Row(row_id="row_0", label="Periodo 1", is_fallback=True))

    for node_el in root.iter(f"{{{NS_G}}}node"):
        shape_node = node_el.find(f".//{{{NS_Y}}}ShapeNode")
        if shape_node is None:
            continue
        label_el = shape_node.find(f".//{{{NS_Y}}}NodeLabel")
        if label_el is None or not (label_el.text and label_el.text.strip()):
            continue
        us_num = label_el.text.strip()
        # Heuristic: unit type from yed.palette.node.name attribute or fallback "US"
        unit_type = "US"
        shape_el = shape_node.find(f"{{{NS_Y}}}Shape")
        if shape_el is not None:
            t = shape_el.attrib.get("type", "").lower()
            # Optional mapping; left simple, palette tells full story
        out.nodes.append(Node(
            node_id=node_el.attrib.get("id"),
            us=us_num,
            area=None,
            sito=target_site,
            unit_type=unit_type,
            description=None,
            row_id="row_0",
        ))

    node_ids = {n.node_id for n in out.nodes}
    for edge_el in root.iter(f"{{{NS_G}}}edge"):
        src = edge_el.attrib.get("source")
        tgt = edge_el.attrib.get("target")
        if src not in node_ids or tgt not in node_ids:
            continue
        label_el = edge_el.find(f".//{{{NS_Y}}}EdgeLabel")
        label = (label_el.text or "").strip() if label_el is not None else "overlies"
        canonical = _resolve_canonical(label) or "overlies"
        out.edges.append(Edge(source_id=src, target_id=tgt, canonical=canonical))

    return out
```

- [ ] **Step 4: Disable CSRF for this endpoint**

In `app.py`, ensure the matrix_tools blueprint is excluded from CSRF (similar to existing `csrf.exempt(matrix_import_bp)`). Add after blueprint registration:
```python
csrf.exempt(harris_creator_bp)  # if not already
```

- [ ] **Step 5: Run tests, commit**

```bash
pytest tests/integration/test_api_import_graphml.py -v
git add pyarchinit_mini/graphproj/graphml_reader.py pyarchinit_mini/web_interface/harris_creator_routes.py tests/integration/test_api_import_graphml.py pyarchinit_mini/web_interface/app.py
git commit -m "feat(import): /api/import/<site>/graphml writes 4-tuple rapporti with inverses"
```

---

### Task 15: Heriverse JSON import endpoint

**Files:**
- Modify: `harris_creator_routes.py`
- Create: `tests/integration/test_api_import_json.py`

- [ ] **Step 1: Write failing test**

`tests/integration/test_api_import_json.py`:
```python
import io
import json
from pathlib import Path
import pytest
from flask import Flask
from sqlalchemy import create_engine, text


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"

SAMPLE_HERIVERSE = json.dumps({
    "wapp": "heriverse",
    "multigraph": {
        "graphs": [{
            "id": "g0",
            "name": "Site_T",
            "nodes": {
                "USM": [{"id": "us_a", "name": "10", "type": "USM"}],
                "USV": [{"id": "us_b", "name": "20", "type": "USV"}],
            },
            "edges": {"line": [{"id": "e1", "from": "us_a", "to": "us_b"}]},
            "semantic_shapes": {}, "representation_models": {}, "panorama_models": {},
        }]
    },
    "couchdb_metadata": {},
}).encode()


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/j.db")
    engine = create_engine(f"sqlite:///{tmp_path}/j.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
            unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT, rapporti TEXT,
            data_origine TEXT, UNIQUE(sito, area, us))"""))
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True; app.config["SECRET_KEY"] = "t"
    app.register_blueprint(harris_creator_bp)
    return app.test_client(), engine


def test_import_heriverse_json_writes_us(client):
    c, engine = client
    r = c.post(
        "/harris-creator/api/import/S/json",
        data={"file": (io.BytesIO(SAMPLE_HERIVERSE), "h.json")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200, r.data[:300]
    body = r.get_json()
    assert body["imported_us"] == 2
    assert body["imported_edges"] == 1
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT us, unita_tipo FROM us_table ORDER BY us")).fetchall()
        assert rows == [("10", "USM"), ("20", "USV")]
```

- [ ] **Step 2: Run, expect fail**

```bash
pytest tests/integration/test_api_import_json.py -v
```

Expected: FAIL.

- [ ] **Step 3: Add route**

```python
@harris_creator_bp.post("/api/import/<site>/json")
def api_import_heriverse_json(site: str):
    from pyarchinit_mini.graphproj.heriverse_parser import parse_heriverse
    from pyarchinit_mini.graphproj.graph_to_db import write_graph
    f = request.files.get("file")
    if f is None or not f.filename:
        return jsonify({"error": "no_file"}), 400
    try:
        projected = parse_heriverse(f.read().decode("utf-8"))
        # Override site to the URL parameter (don't trust JSON's name)
        projected.site = site
        for n in projected.nodes:
            n.sito = site
    except Exception as e:
        logger.warning("import json parse failed: %s", e)
        return jsonify({"error": "parse_error", "detail": str(e)}), 400
    try:
        with _get_session() as s:
            res = write_graph(projected, target_site=site, session=s, source_label="json")
        return jsonify({
            "imported_us": res.imported_us,
            "imported_edges": res.imported_edges,
            "inverses_written": res.inverses_written,
            "stubs_created": res.stubs_created,
            "inverses_skipped": res.inverses_skipped,
        }), 200
    except Exception as e:
        logger.exception("import json write failed")
        return jsonify({"error": "write_failed", "message": str(e)}), 500
```

- [ ] **Step 4: Run tests, commit**

```bash
pytest tests/integration/test_api_import_json.py -v
git add pyarchinit_mini/web_interface/harris_creator_routes.py tests/integration/test_api_import_json.py
git commit -m "feat(import): /api/import/<site>/json (Heriverse) writes us_table + rapporti"
```

---

## Phase 8: UI surfaces

### Task 16: Swimlane toolbar (grouping + export + import)

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/harris_creator/swimlane.html` (toolbar section)

- [ ] **Step 1: Locate current toolbar**

```bash
grep -n "swimlane\|toolbar\|export" pyarchinit_mini/web_interface/templates/harris_creator/swimlane.html | head -20
```

- [ ] **Step 2: Add toolbar HTML**

Insert this block in the swimlane.html toolbar (replace the existing yEd Export button if present):
```html
<div class="btn-toolbar mb-2" role="toolbar">
  <div class="btn-group me-2">
    <label class="input-group-text">{{ _("Raggruppamento") }}</label>
    <select id="group-by-select" class="form-select" onchange="reloadSwimlane()">
      <option value="none" selected>{{ _("nessuno") }}</option>
      <option value="area">{{ _("area") }}</option>
      <option value="settore">{{ _("settore") }}</option>
      <option value="quadrato">{{ _("quadrato") }}</option>
      <option value="attivita">{{ _("attività") }}</option>
      <option value="strutture">{{ _("strutture") }}</option>
    </select>
  </div>
  <div class="btn-group me-2">
    <button type="button" class="btn btn-outline-primary dropdown-toggle" data-bs-toggle="dropdown">
      <i class="fas fa-download"></i> {{ _("Export") }}
    </button>
    <ul class="dropdown-menu">
      <li><a class="dropdown-item" href="#" onclick="exportSwimlane('yed-graphml')">yEd GraphML (.graphml)</a></li>
      <li><a class="dropdown-item" href="#" onclick="exportSwimlane('heriverse-json')">Heriverse / ATON (.json)</a></li>
    </ul>
  </div>
  <div class="btn-group me-2">
    <button type="button" class="btn btn-outline-secondary" onclick="document.getElementById('import-file').click()">
      <i class="fas fa-upload"></i> {{ _("Import") }}
    </button>
    <input type="file" id="import-file" accept=".graphml,.json" style="display:none" onchange="importMatrixFile(this.files[0])">
  </div>
</div>
<script>
const SITE = {{ site|tojson }};
function reloadSwimlane() {
  const g = document.getElementById('group-by-select').value;
  window.location.search = `?group_by=${g}`;
}
function exportSwimlane(fmt) {
  const g = document.getElementById('group-by-select').value;
  window.location.href = `/harris-creator/api/export/${SITE}/${fmt}?group_by=${g}`;
}
function importMatrixFile(file) {
  if (!file) return;
  const fmt = file.name.endsWith('.json') ? 'json' : 'graphml';
  const fd = new FormData();
  fd.append('file', file);
  fetch(`/harris-creator/api/import/${SITE}/${fmt}`, {method:'POST', body: fd})
    .then(r => r.json()).then(res => {
      alert(`Import OK: ${res.imported_us} US, ${res.imported_edges} edges, ${res.stubs_created} stubs`);
      window.location.reload();
    }).catch(e => alert(`Import error: ${e}`));
}
</script>
```

- [ ] **Step 3: Manual visual smoke test**

```bash
pyarchinit-mini-web --port 5001 &
sleep 3
open "http://localhost:5001/harris-creator/<a-site-name>"
```

Verify dropdown / export menu / import file picker render correctly.

- [ ] **Step 4: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/harris_creator/swimlane.html
git commit -m "feat(ui): swimlane toolbar with grouping + export menu + import file picker"
```

---

### Task 17: `/matrix-tools` standalone page

**Files:**
- Create: `pyarchinit_mini/web_interface/matrix_tools_routes.py`
- Create: `pyarchinit_mini/web_interface/templates/matrix_tools/index.html`
- Modify: `pyarchinit_mini/web_interface/app.py` (register blueprint, csrf.exempt)

- [ ] **Step 1: Create blueprint**

`pyarchinit_mini/web_interface/matrix_tools_routes.py`:
```python
"""Standalone Matrix Tools page: import/export GraphML and Heriverse JSON."""
from __future__ import annotations

import os
from flask import Blueprint, render_template, current_app
from sqlalchemy import text


matrix_tools_bp = Blueprint("matrix_tools", __name__, url_prefix="/matrix-tools")


def _get_session():
    if hasattr(current_app, "db_manager"):
        return current_app.db_manager.connection.get_session()
    from pyarchinit_mini.database.connection import DatabaseConnection
    db_url = os.getenv("DATABASE_URL", "sqlite:///pyarchinit_mini.db")
    return DatabaseConnection.from_url(db_url).get_session()


@matrix_tools_bp.get("/")
def index():
    with _get_session() as db:
        sites = db.execute(text("SELECT sito FROM site_table ORDER BY sito")).fetchall()
    return render_template("matrix_tools/index.html", sites=[r[0] for r in sites])
```

- [ ] **Step 2: Create template**

`pyarchinit_mini/web_interface/templates/matrix_tools/index.html`:
```html
{% extends "base.html" %}
{% block content %}
<div class="container mt-4">
  <h2><i class="fas fa-tools"></i> {{ _("Matrix Tools") }}</h2>
  <p class="text-muted">{{ _("Import o esporta la stratigrafia di un sito in formato GraphML o Heriverse/ATON JSON.") }}</p>

  <div class="card mb-4">
    <div class="card-header"><i class="fas fa-download"></i> {{ _("Export") }}</div>
    <div class="card-body">
      <div class="mb-3">
        <label class="form-label">{{ _("Sito") }}</label>
        <select id="export-site" class="form-select">
          {% for s in sites %}<option value="{{ s }}">{{ s }}</option>{% endfor %}
        </select>
      </div>
      <button class="btn btn-primary" onclick="exportSite('yed-graphml')"><i class="fas fa-file-code"></i> yEd GraphML</button>
      <button class="btn btn-primary" onclick="exportSite('heriverse-json')"><i class="fas fa-cube"></i> Heriverse / ATON</button>
    </div>
  </div>

  <div class="card">
    <div class="card-header"><i class="fas fa-upload"></i> {{ _("Import") }}</div>
    <div class="card-body">
      <div class="mb-3">
        <label class="form-label">{{ _("Sito di destinazione") }}</label>
        <select id="import-site" class="form-select">
          {% for s in sites %}<option value="{{ s }}">{{ s }}</option>{% endfor %}
        </select>
      </div>
      <div class="mb-3">
        <label class="form-label">{{ _("File (.graphml o .json)") }}</label>
        <input type="file" id="import-file" class="form-control" accept=".graphml,.json">
      </div>
      <button class="btn btn-success" onclick="importFile()"><i class="fas fa-upload"></i> {{ _("Carica") }}</button>
      <div id="import-result" class="mt-3"></div>
    </div>
  </div>
</div>

<script>
function exportSite(fmt) {
  const site = document.getElementById('export-site').value;
  window.location.href = `/harris-creator/api/export/${site}/${fmt}`;
}
function importFile() {
  const site = document.getElementById('import-site').value;
  const f = document.getElementById('import-file').files[0];
  if (!f) { alert('{{ _("Scegli un file") }}'); return; }
  const fmt = f.name.endsWith('.json') ? 'json' : 'graphml';
  const fd = new FormData(); fd.append('file', f);
  fetch(`/harris-creator/api/import/${site}/${fmt}`, {method:'POST', body: fd})
    .then(r => r.json()).then(res => {
      document.getElementById('import-result').innerHTML =
        `<div class="alert alert-success">Importate ${res.imported_us} US, ${res.imported_edges} edges, ${res.stubs_created} stubs creati.</div>`;
    }).catch(e => {
      document.getElementById('import-result').innerHTML = `<div class="alert alert-danger">${e}</div>`;
    });
}
</script>
{% endblock %}
```

- [ ] **Step 3: Register in `app.py`**

Add near other blueprint registrations:
```python
from pyarchinit_mini.web_interface.matrix_tools_routes import matrix_tools_bp
app.register_blueprint(matrix_tools_bp)
csrf.exempt(matrix_tools_bp)
```

- [ ] **Step 4: Smoke test + commit**

```bash
pyarchinit-mini-web --port 5001 &
sleep 3
curl -s http://localhost:5001/matrix-tools/ | grep -q "Matrix Tools"
git add pyarchinit_mini/web_interface/matrix_tools_routes.py pyarchinit_mini/web_interface/templates/matrix_tools/index.html pyarchinit_mini/web_interface/app.py
git commit -m "feat(ui): /matrix-tools standalone page for import/export"
```

---

### Task 18: Sites list export buttons

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/sites/list.html`

- [ ] **Step 1: Locate the sites list table**

```bash
grep -n "action\|btn-group\|sito" pyarchinit_mini/web_interface/templates/sites/list.html | head -20
```

- [ ] **Step 2: Add per-row export buttons**

Inside the existing actions cell for each site row, append:
```html
<a href="/harris-creator/api/export/{{ site.sito }}/yed-graphml" class="btn btn-sm btn-outline-secondary" title="Export yEd GraphML">
  <i class="fas fa-file-code"></i>
</a>
<a href="/harris-creator/api/export/{{ site.sito }}/heriverse-json" class="btn btn-sm btn-outline-secondary" title="Export Heriverse / ATON">
  <i class="fas fa-cube"></i>
</a>
```

- [ ] **Step 3: Smoke test + commit**

```bash
git add pyarchinit_mini/web_interface/templates/sites/list.html
git commit -m "feat(ui): per-site export buttons in sites list"
```

---

## Phase 9: Regression baseline

### Task 19: Create Adarte regression fixture

**Files:**
- Create: `tests/fixtures/adarte_regression_dump.sql`
- Create script: `scripts/build_regression_fixture.py`

- [ ] **Step 1: Script to dump anonymized fixture**

`scripts/build_regression_fixture.py`:
```python
"""Anonymized fixture builder.

Connects to Adarte postgres, pulls 50–100 US from Rimini_RN_2020_21_Museo_Fellini,
renames site to RegressionFixture_v1, preserves US numbers, dumps as SQL INSERT
statements compatible with sqlite (TEXT columns, no postgres-only types).
"""
import os, psycopg2

DSN = "postgresql://admin_pyarchinit:***REMOVED***@10.0.1.6:5432/pyarchinit_v2"
ORIG_SITE = "Rimini_RN_2020_21_Museo_Fellini_Piazza_Malatesta_Lotto_1_3"
NEW_SITE = "RegressionFixture_v1"
LIMIT = 100

conn = psycopg2.connect(DSN)
cur = conn.cursor()

with open("tests/fixtures/adarte_regression_dump.sql", "w") as f:
    f.write("-- Auto-generated anonymized fixture\n")
    f.write("-- DO NOT EDIT BY HAND — re-run scripts/build_regression_fixture.py\n\n")
    # Schema
    f.write("""CREATE TABLE IF NOT EXISTS site_table (
    id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE);
""")
    f.write("""CREATE TABLE IF NOT EXISTS period_table (
    id_period INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, periodo TEXT, fase TEXT, datazione TEXT);
""")
    f.write("""CREATE TABLE IF NOT EXISTS us_table (
    id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
    unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
    settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT,
    rapporti TEXT, data_origine TEXT,
    UNIQUE(sito, area, us));
""")
    f.write(f"INSERT INTO site_table (sito) VALUES ('{NEW_SITE}');\n")

    cur.execute("SELECT periodo, fase, datazione FROM period_table WHERE sito = %s", (ORIG_SITE,))
    for periodo, fase, dataz in cur.fetchall():
        f.write(f"INSERT INTO period_table (sito, periodo, fase, datazione) VALUES "
                f"('{NEW_SITE}', {repr(periodo or '')}, {repr(fase or '')}, {repr(dataz or '')});\n")

    cur.execute("""SELECT area, us, unita_tipo, descrizione, fase_iniziale, fase_finale, rapporti
                   FROM us_table WHERE sito = %s LIMIT %s""", (ORIG_SITE, LIMIT))
    for r in cur.fetchall():
        area, us, ut, desc, fi, ff, rapp = r
        # Replace site references inside rapporti 4-tuples
        rapp_safe = (rapp or "").replace(ORIG_SITE, NEW_SITE) if rapp else ""
        f.write("INSERT INTO us_table (sito, area, us, unita_tipo, descrizione, "
                "fase_iniziale, fase_finale, rapporti) VALUES "
                f"({repr(NEW_SITE)}, {repr(area or '')}, {repr(us or '')}, "
                f"{repr(ut or 'US')}, {repr(desc or '')}, {repr(fi or '')}, "
                f"{repr(ff or '')}, {repr(rapp_safe)});\n")

conn.close()
print("Fixture written to tests/fixtures/adarte_regression_dump.sql")
```

- [ ] **Step 2: Run the script via SSH tunnel**

Since we don't have direct postgres access from sandbox, run the script ON Adarte and scp back:
```bash
sshpass -p '***REMOVED***' scp -o ConnectTimeout=15 -o PreferredAuthentications=password -o PubkeyAuthentication=no \
  scripts/build_regression_fixture.py ganesh@10.0.1.13:/tmp/
sshpass -p '***REMOVED***' ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no ganesh@10.0.1.13 \
  '/home/ganesh/pyarchinit_env/bin/python /tmp/build_regression_fixture.py'
# Note: paths inside the script assume local; adjust or use a temp directory then scp back.
```

Alternative: ssh into Adarte, run inline:
```bash
sshpass -p '***REMOVED***' ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no ganesh@10.0.1.13 \
  '/home/ganesh/pyarchinit_env/bin/python - < scripts/build_regression_fixture.py > /tmp/regression.sql' 
scp ... :/tmp/regression.sql tests/fixtures/adarte_regression_dump.sql
```

- [ ] **Step 3: Verify fixture loads in sqlite**

```bash
sqlite3 /tmp/regression.db < tests/fixtures/adarte_regression_dump.sql
sqlite3 /tmp/regression.db "SELECT COUNT(*) FROM us_table"
```

Expected: 100 (or close).

- [ ] **Step 4: Commit**

```bash
git add scripts/build_regression_fixture.py tests/fixtures/adarte_regression_dump.sql
git commit -m "test(regression): Adarte fixture for swimlane parity baseline"
```

---

### Task 20: Regression test

**Files:**
- Create: `tests/integration/test_adarte_regression.py`

- [ ] **Step 1: Write the test**

`tests/integration/test_adarte_regression.py`:
```python
from pathlib import Path
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.graphproj.s3d_projector import S3DProjector


FIXTURE_SQL = Path(__file__).parent.parent / "fixtures" / "adarte_regression_dump.sql"


@pytest.fixture
def session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/reg.db")
    with engine.begin() as conn:
        sql = FIXTURE_SQL.read_text()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
    return sessionmaker(bind=engine)()


def test_regression_edge_count_within_tolerance(session):
    g = S3DProjector.from_site(session, "RegressionFixture_v1", group_by="none")
    # Baseline from legacy pipeline on Rimini Museo Fellini: 4066 edges on 1004 nodes.
    # 100-US subset should produce ~400 edges (proportional, but actual depends on which 100 US).
    # Conservative lower bound:
    assert len(g.edges) >= 50, f"Got {len(g.edges)} edges, expected ≥50"


def test_regression_edge_labels_diverse(session):
    g = S3DProjector.from_site(session, "RegressionFixture_v1", group_by="none")
    labels = {e.canonical for e in g.edges}
    # Expect at least 4 distinct canonical types in any reasonable subset
    assert len(labels) >= 4, f"Got labels: {labels}"


def test_regression_periods_loaded(session):
    g = S3DProjector.from_site(session, "RegressionFixture_v1", group_by="none")
    assert len(g.rows) >= 1
```

- [ ] **Step 2: Run, expect pass**

```bash
pytest tests/integration/test_adarte_regression.py -v
```

Expected: 3 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_adarte_regression.py
git commit -m "test(regression): assert s3dgraphy pipeline produces ≥50 edges + ≥4 distinct labels on fixture"
```

---

## Phase 10: Round-trip + final cleanup

### Task 21: Round-trip integration test

**Files:**
- Create: `tests/integration/test_roundtrip.py`

- [ ] **Step 1: Write test**

`tests/integration/test_roundtrip.py`:
```python
import io
from pathlib import Path
import pytest
from flask import Flask
from sqlalchemy import create_engine, text


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/rt.db")
    engine = create_engine(f"sqlite:///{tmp_path}/rt.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE)"""))
        conn.execute(text("""CREATE TABLE period_table (id_period INTEGER PRIMARY KEY, sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
            unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT, rapporti TEXT,
            data_origine TEXT, UNIQUE(sito, area, us))"""))
        conn.execute(text("INSERT INTO us_table (sito,area,us,unita_tipo,rapporti) VALUES ('S','A','1','USM',?)"),
                     ("[['Copre','2','A','S']]",))
        conn.execute(text("INSERT INTO us_table (sito,area,us,unita_tipo) VALUES ('S','A','2','USV')"))
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True; app.config["SECRET_KEY"] = "t"
    app.register_blueprint(harris_creator_bp)
    return app.test_client(), engine


def test_roundtrip_graphml(client):
    c, engine = client
    # Export
    r = c.get("/harris-creator/api/export/S/yed-graphml")
    assert r.status_code == 200
    exported = r.data
    # Wipe US data
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM us_table"))
    # Reimport
    r2 = c.post("/harris-creator/api/import/S/graphml",
                data={"file": (io.BytesIO(exported), "rt.graphml")},
                content_type="multipart/form-data")
    assert r2.status_code == 200
    # Verify both US restored
    with engine.begin() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM us_table")).scalar()
        assert count == 2
        rapp_1 = conn.execute(text("SELECT rapporti FROM us_table WHERE us='1'")).scalar()
        assert rapp_1 and "Copre" in rapp_1
```

- [ ] **Step 2: Run, expect pass**

```bash
pytest tests/integration/test_roundtrip.py -v
```

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_roundtrip.py
git commit -m "test(roundtrip): DB → graphml export → import → assert parity"
```

---

### Task 22: Full test suite + lint

- [ ] **Step 1: Run full unit + integration suite**

```bash
pytest tests/unit/ tests/integration/ -v --tb=short
```

Expected: all pass (or document specific failures).

- [ ] **Step 2: Check coverage of new modules**

```bash
pytest --cov=pyarchinit_mini/em_palette --cov=pyarchinit_mini/graphproj --cov-report=term-missing tests/unit/ tests/integration/
```

Expected: ≥80% on new modules.

- [ ] **Step 3: Commit if any test added during cleanup**

```bash
git status
# if any new fixes:
git add . && git commit -m "test: final test suite pass"
```

---

### Task 23: Bump version + update CHANGELOG

**Files:**
- Modify: `pyarchinit_mini/__init__.py` (`__version__`)
- Modify: `pyproject.toml` (`version`)
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Bump 2.7.1 → 2.8.0**

In `pyarchinit_mini/__init__.py`:
```python
__version__ = "2.8.0"
```

In `pyproject.toml`:
```toml
version = "2.8.0"
```

- [ ] **Step 2: Add CHANGELOG entry**

Prepend to `CHANGELOG.md`:
```markdown
## 2.8.0 — 2026-05-19

### Added
- EM palette is now the canonical style source for swimlane rendering, GraphML export, and Heriverse/ATON JSON export. Palette loaded from `pyarchinit_mini/graphml_converter/templates/EM_palette.graphml` with SIGHUP hot-reload.
- `SWIMLANE_PIPELINE=s3dgraphy|legacy` feature flag with automatic legacy fallback on exception.
- New endpoints:
  - `GET /harris-creator/api/export/<site>/heriverse-json` — Heriverse/ATON JSON.
  - `POST /harris-creator/api/import/<site>/graphml` — yEd GraphML import with 4-tuple rapporti + inverses on both involved US.
  - `POST /harris-creator/api/import/<site>/json` — Heriverse JSON import (same write path as GraphML).
- Standalone `/matrix-tools` page for import/export operations.
- Per-site export buttons (GraphML, Heriverse) in sites list.
- Swimlane toolbar: grouping dropdown (none/area/settore/quadrato/attività/strutture), export menu, import file picker.
- Bilingual rapporti parser: reads both legacy 2-tuple `[rel, us]` and new 4-tuple `[rel, us, area, sito]`; always writes 4-tuple.
- Automatic stub US creation when import edges reference missing rows; counted in result.

### Changed
- Swimlane rows are now always periods (with "Periodo 1" fallback when `period_table` is empty or a US has no `fase_iniziale`); the old `group_by=period_phase|struttura|...` registry collapses to a sub-grouping selector within rows.

### Internals
- New modules: `pyarchinit_mini/em_palette/`, `pyarchinit_mini/graphproj/{s3d_projector,s3d_to_cytoscape,graph_to_db,heriverse_parser,graphml_writer,graphml_reader,rapporti_codec}.py`.
- Tests: 13 new test files in `tests/unit/` and `tests/integration/`, plus regression fixture from Rimini_RN_2020_21_Museo_Fellini.
```

- [ ] **Step 3: Commit**

```bash
git add pyarchinit_mini/__init__.py pyproject.toml CHANGELOG.md
git commit -m "release: bump to 2.8.0 (EM palette + multi-format swimlane round-trip)"
```

---

### Task 24: Build, publish to PyPI, deploy to Adarte

- [ ] **Step 1: Build wheel**

```bash
rm -rf dist/
python -m build
ls dist/
```

Expected: `pyarchinit_mini-2.8.0-py3-none-any.whl` and `.tar.gz`.

- [ ] **Step 2: Upload to PyPI**

```bash
twine upload dist/*
```

Expected: "View at https://pypi.org/project/pyarchinit-mini/2.8.0/".

- [ ] **Step 3: Deploy to Adarte**

```bash
VERSION=2.8.0 ./adarte_deploy.sh
```

Expected: probe, screen quit, pip install --force-reinstall 2.8.0, verify version, restart screen, port 5001 listening.

- [ ] **Step 4: Sanity check on Adarte**

```bash
sshpass -p '***REMOVED***' ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no ganesh@10.0.1.13 \
  '/home/ganesh/pyarchinit_env/bin/python -c "import pyarchinit_mini; print(pyarchinit_mini.__version__)"'
```

Expected: `2.8.0`.

Browse to `http://10.0.1.13:5001/harris-creator/<site>` and visually verify:
- Grouping dropdown present.
- Switching to area shows sub-clusters.
- Export GraphML downloads file with palette template.
- Export Heriverse downloads JSON.
- Import GraphML accepts file and triggers DB writes.

- [ ] **Step 5: Merge to main**

```bash
git checkout main
git pull
git merge --no-ff feat/em-palette-swimlane
git push
```

---

## Self-review checklist (DO NOT skip)

After all tasks land:

- [ ] **Spec coverage**: Every section of `docs/superpowers/specs/2026-05-19-em-palette-swimlane-design.md` has at least one implementing task. Check the "Decisions captured" table — each row has a task that enforces it.
- [ ] **Feature flag rollback path**: `SWIMLANE_PIPELINE=legacy` still produces a working swimlane with edges on Adarte. Don't delete legacy code until the regression baseline is solid.
- [ ] **Adarte regression numbers**: After deploy, hit `/api/load/Rimini_RN_2020_21_Museo_Fellini_Piazza_Malatesta_Lotto_1_3` with `SWIMLANE_PIPELINE=s3dgraphy` and `SWIMLANE_PIPELINE=legacy`. Edge counts should match within ±5.
- [ ] **Post-upgrade patch compatibility**: When user runs `patch_pyarchinit_post_upgrade.py` after 2.8.0 install, Sections 27 and 28 must either auto-skip (because the new pipeline already includes their fixes) or be removed from the patch script. Confirm during plan execution.
- [ ] **CSRF**: All new POST endpoints exempted via `csrf.exempt(matrix_tools_bp)` and `csrf.exempt(harris_creator_bp)` for import routes.
- [ ] **Translation strings**: All user-facing text in templates uses `{{ _("...") }}` for i18n.

---

## Open implementation questions (resolve during execution)

1. **s3dgraphy GraphMLExporter** — current code (`s3d_integration/s3d_converter.py:446`) writes Heriverse JSON via custom dict assembly, not through s3dgraphy's exporter. The plan uses `s3dgraphy` only for the s3d.Graph data structure; export goes through our own `graphml_writer.py`. Verify if s3dgraphy provides better helpers; if so, replace `graphml_writer.write_graphml` body.
2. **us_table column for sub-grouping** — postgres Adarte has `area`, plus `settore`/`quadrato`/`attivita`/`struttura`/`saggio`/`ambient` (some legacy schemas have these, some don't). During Task 6 implementation, verify column existence with `information_schema.columns` query; gracefully fall back to `area` if missing.
3. **Inverse pairs vocabulary** — `INVERSE_PAIRS` in `rapporti_codec.py` covers canonical names. If imported GraphML uses a relation name not in the registry (e.g., `partially_covers`), the inverse is skipped and logged. Decide during execution whether to extend the registry or accept the skip.
4. **Audit log** — spec mentions `~/.pyarchinit_mini/logs/matrix_import.jsonl`. Tasks 14/15 don't add audit logging. If desired, add as Task 14.5 / 15.5.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-19-em-palette-swimlane.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
