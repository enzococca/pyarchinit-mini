# s3dgraphy adoption (issue #2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Project the pyarchinit-mini database into `s3dgraphy.Graph` through the shared library's `PyArchInitImporter`, keep only thin mini-side layers (rapporti edges, swimlane rows, views, write-back) on that graph, and delete the local `ProjectedGraph` model.

**Architecture:** `GraphProjector.populate_graph()` calls `PyArchInitImporter(connection_url=<mini engine URL>, filters={"sito": site})`, then mini attaches a `node.attributes["pyarchinit"]` block to every stratigraphic node (correlated by `node_uuid`, else by the importer's own node name), adds stratigraphic edges from `rapporti` through the existing `rapporti_codec`, and stores swimlane rows in `graph.attributes["swimlane"]`. Views (cytoscape JSON, yEd TableNode), readers (yEd minimal, Heriverse) and write-back (`write_graph`, `GraphIngestor`) all read/write that one `s3dgraphy.Graph`; `s3d_projector.py` is removed.

**Tech Stack:** Python 3.9+, SQLAlchemy 2.0 (`<2.1`), s3dgraphy `>=1.6.0.dev39,<1.7` (needs `psycopg2-binary` for Postgres, already a dependency), networkx (transitive reduction), pytest.

**Spec:** `docs/superpowers/specs/2026-10-06-s3dgraphy-adoption-design.md`

## Global Constraints

- Dependency pins, verbatim: `s3dgraphy>=1.6.0.dev39,<1.7` in both `pyproject.toml` and `requirements.txt`; `requires-python = ">=3.9,<3.15"`; `sqlalchemy>=2.0.0,<2.1` stays.
- `pyarchinit_mini/stratigraph/` is not touched (spec D2).
- The importer is always constructed with `connection_url=` and `filters=`; **never** with `existing_graph=` (spec §3).
- Stratigraphic edge `edge_type` values are mini canonicals in forward form only: `overlies, cuts, fills, abuts, has_same_time, is_bonded_to, is_before` (spec §4); `edge_id = f"{src}__{canonical}__{tgt}"`.
- The cytoscape JSON shape consumed by `templates/harris_creator/editor.html` and `static/js/harris_creator_editor.js` must not change (flat palette keys, `is_dashed` as the strings `"true"/"false"`, `parent` nesting, `rows` list).
- Public call signatures kept: `GraphProjector.populate_graph(session, site, *, area=None, group_by="none")`, `to_cytoscape(graph)`, `graphml_writer.write_graphml(graph, *, palette_path=None) -> bytes`, `parse_graphml(raw, *, target_site)`, `parse_heriverse(raw_json)`, `write_graph(graph, *, target_site, session, source_label="import") -> WriteResult`, `GraphIngestor(session, site).preview/apply`, `_trigger_graph_regen(site, *, session=)`.
- Run the whole suite with `.venv/bin/python -m pytest -q -p no:cacheprovider -o addopts=""` before every commit that touches code; commits carry no AI attribution lines.
- Work on a branch in a worktree (`superpowers:using-git-worktrees`): branch name `feat/s3dgraphy-adoption`.

## Review Focus

1. **US rows with NULL `node_uuid`** (databases never backfilled): the importer gives them a random uuid; attributes and edges must still attach through name correlation — pinned by `test_attach_matches_row_without_uuid_by_importer_name` (Task 5).
2. **Same US number in two areas** with area-qualified rapporti (`[['Copre','2','B','S']]`): the target must resolve by `(area, us)` before the `us`-only fallback — pinned by `test_target_resolves_by_area_then_us` (Task 4).
3. **Postgres URLs** with `postgresql+psycopg2://` and a password containing `@`/`:`-free but URL-encoded characters must reach the importer unchanged (`render_as_string(hide_password=False)`) — pinned by `test_postgres_url_keeps_password_and_driver` (Task 2).
4. **Node names containing digits in area/settore** (`A1.US12`): the ingestor must not read `112` — pinned by `test_us_number_uses_trailing_digits_when_no_attrs` (Task 12).
5. **Importer failure** (missing table, locked file): `populate_graph` raises `ProjectionError`, and auto-regen still never raises — pinned by `test_populate_graph_wraps_importer_failure` (Task 6) plus the existing `tests/unit/test_auto_regen.py` "never raises" cases.
6. **Legacy free-text rapporti** (`"copre 1002"`): no edges, no exception — pinned by `test_free_text_rapporti_yield_no_edges` (Task 6).

---

## File Structure

| File | Responsibility |
|------|----------------|
| `pyarchinit_mini/graphproj/strat_graph.py` (new) | The graph contract: helpers to create stratigraphic nodes, read/write the `pyarchinit` and `swimlane` attribute blocks, select stratigraphic nodes/edges. |
| `pyarchinit_mini/graphproj/connection_url.py` (new) | SQLAlchemy session → DB-API connection URL for the importer. |
| `pyarchinit_mini/graphproj/periods.py` (new) | `PeriodRow`, `load_period_rows`, `resolve_row_id` (moved from `s3d_projector`). |
| `pyarchinit_mini/graphproj/strat_edges.py` (new) | `NodeIndex`, `build_stratigraphic_edges`, `add_stratigraphic_edges` (edge normalisation moved from `s3d_projector`). |
| `pyarchinit_mini/graphproj/enrich.py` (new) | `VALID_GROUP_BY`, `UsRow`, `load_us_rows`, `attach_pyarchinit_attributes`. |
| `pyarchinit_mini/graphproj/projector.py` (rewrite) | `GraphProjector.populate_graph` orchestration on the importer. |
| `pyarchinit_mini/graphproj/s3d_to_cytoscape.py` (rewrite) | `to_cytoscape(graph)` on `s3dgraphy.Graph`. |
| `pyarchinit_mini/graphproj/graphml_writer.py` (rewrite) | yEd TableNode bytes from `s3dgraphy.Graph`. |
| `pyarchinit_mini/graphproj/graphml_reader.py`, `heriverse_parser.py` (rewrite) | Produce `s3dgraphy.Graph`. |
| `pyarchinit_mini/graphproj/graph_to_db.py` (rewrite) | `write_graph(graph: s3dgraphy.Graph, …)`. |
| `pyarchinit_mini/graphproj/ingestor.py` (modify) | US number from attrs / trailing digits. |
| `pyarchinit_mini/graphproj/s3d_projector.py` | **deleted** (Task 14). |
| `pyarchinit_mini/web_interface/harris_creator_routes.py`, `pyarchinit_mini/harris_swimlane/swimlane_state.py` (modify) | Call-site updates. |
| `tests/unit/strat_graph_factory.py` (new) | Test helper building contract-conformant graphs without a DB. |
| `tests/unit/test_strat_graph.py`, `test_connection_url.py`, `test_periods.py`, `test_strat_edges.py`, `test_enrich.py`, `test_projector_populate.py` (new); existing graphproj tests adapted. |

---

### Task 0: Spike — pin s3dgraphy 1.6.0.dev39 and prove the importer on mini's schema

**Files:**
- Modify: `pyproject.toml:43` (`requires-python`), `pyproject.toml:61` (`s3dgraphy` pin), `requirements.txt:56`
- Modify: `tests/unit/test_dependency_pins.py`
- Create: `tests/unit/test_s3dgraphy_importer_spike.py`

**Interfaces:**
- Produces: the guarantee that `from s3dgraphy.importer.pyarchinit_importer import PyArchInitImporter` works with `connection_url=`/`filters=` on a mini-schema SQLite file, and that `graph.attributes` is a dict. Every later task relies on this.

- [ ] **Step 1: Write the failing pin test**

Append to `tests/unit/test_dependency_pins.py`:

```python
def _requirement_for(name: str, text: str) -> str:
    for line in text.splitlines():
        item = line.split("#", 1)[0].strip().rstrip(",").strip('"')
        if item.lower().startswith(name):
            return item[len(name):].replace(" ", "")
    raise AssertionError(f"{name} requirement not found")


@pytest.mark.parametrize("path", ["requirements.txt", "pyproject.toml"])
def test_s3dgraphy_is_pinned_to_1_6_prerelease_line(path):
    spec = _requirement_for("s3dgraphy", (ROOT / path).read_text(encoding="utf-8"))
    assert spec == ">=1.6.0.dev39,<1.7", f"{path}: s3dgraphy spec {spec!r}"


def test_requires_python_floor_is_3_9():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.9,<3.15"' in text
```

- [ ] **Step 2: Run it to verify it fails**

Run: `.venv/bin/python -m pytest tests/unit/test_dependency_pins.py -q -p no:cacheprovider`
Expected: 3 failures (`>=0.1.42`, `>=1.5.0`, requires-python).

- [ ] **Step 3: Update the pins and install**

`pyproject.toml` line 43: `requires-python = ">=3.9,<3.15"`; line 61: `"s3dgraphy>=1.6.0.dev39,<1.7",  # shared DB⇄graph library (issue #2); pre-release pin on purpose`.
`requirements.txt` line 56: `s3dgraphy>=1.6.0.dev39,<1.7`.

Run: `.venv/bin/pip install "s3dgraphy>=1.6.0.dev39,<1.7"` and confirm `.venv/bin/python -c "import s3dgraphy; print(s3dgraphy.__version__)"` prints `1.6.0.dev39` (or a later 1.6 pre-release).

- [ ] **Step 4: Write the spike test (importer end-to-end on mini's schema)**

Create `tests/unit/test_s3dgraphy_importer_spike.py`:

```python
"""Canary for the s3dgraphy importer API this project builds on (issue #2).

If this file goes red after a s3dgraphy upgrade, the library changed under us;
fix graphproj/* before touching anything else.
"""
import sqlite3

import pytest
from s3dgraphy.importer.pyarchinit_importer import PyArchInitImporter
from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode


@pytest.fixture
def mini_db(tmp_path):
    path = tmp_path / "mini.sqlite"
    c = sqlite3.connect(path)
    c.executescript("""
    CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, settore TEXT,
      us TEXT, unita_tipo TEXT, d_stratigrafica TEXT, descrizione TEXT, rapporti TEXT,
      node_uuid TEXT, periodo_iniziale TEXT, fase_iniziale TEXT, quota_abs REAL, schedatore TEXT);
    CREATE TABLE periodizzazione_table (id_periodizzazione INTEGER PRIMARY KEY, sito TEXT,
      periodo_iniziale TEXT, fase_iniziale TEXT, datazione_estesa TEXT);
    INSERT INTO us_table VALUES (1,'S','A','Nord','1','US','strato','d1',
      "[['Copre', '2', 'A', 'S']]",'0192aaaa-0000-7000-8000-000000000001','I','a',12.5,'Mario');
    INSERT INTO us_table VALUES (2,'S','A','Nord','2','USM','muro','d2',NULL,NULL,'I','a',NULL,'Mario');
    INSERT INTO us_table VALUES (3,'OTHER','A','','9','US','altro',NULL,NULL,NULL,NULL,NULL,NULL,NULL);
    """)
    c.commit(); c.close()
    return path


def test_importer_reads_only_the_filtered_site_and_keys_nodes_by_uuid(mini_db):
    imp = PyArchInitImporter(connection_url=f"sqlite:///{mini_db}",
                             mapping_name="pyarchinit_us_mapping", filters={"sito": "S"})
    graph = imp.parse()
    strat = [n for n in graph.nodes if isinstance(n, StratigraphicNode)]
    assert sorted(n.name for n in strat) == ["A.Nord.US1", "A.Nord.USM2"]
    by_name = {n.name: n for n in strat}
    assert by_name["A.Nord.US1"].node_id == "0192aaaa-0000-7000-8000-000000000001"
    assert by_name["A.Nord.USM2"].node_id != ""          # minted uuid4 for the NULL row
    assert isinstance(graph.attributes, dict)             # we store swimlane rows here


def test_importer_does_not_create_stratigraphic_edges(mini_db):
    imp = PyArchInitImporter(connection_url=f"sqlite:///{mini_db}",
                             mapping_name="pyarchinit_us_mapping", filters={"sito": "S"})
    graph = imp.parse()
    strat_ids = {n.node_id for n in graph.nodes if isinstance(n, StratigraphicNode)}
    assert not [e for e in graph.edges if e.edge_source in strat_ids and e.edge_target in strat_ids]


def test_importer_degrades_when_periodizzazione_has_mini_columns(mini_db):
    imp = PyArchInitImporter(connection_url=f"sqlite:///{mini_db}",
                             mapping_name="pyarchinit_us_mapping", filters={"sito": "S"})
    imp.parse()
    assert any("periodization table" in w for w in imp.warnings)


def test_name_resolution_helper_collapses_empty_parts(mini_db):
    imp = PyArchInitImporter(connection_url=f"sqlite:///{mini_db}",
                             mapping_name="pyarchinit_us_mapping", filters={"sito": "S"})
    assert imp._resolve_node_name({"area": "A", "settore": "", "unita_tipo": "US", "us": "7"}, "us") == "A.US7"
    assert imp._resolve_node_name({"area": None, "settore": None, "unita_tipo": "USVs", "us": "3"}, "us") == "USVs3"
```

- [ ] **Step 5: Run the spike + full suite**

Run: `.venv/bin/python -m pytest tests/unit/test_s3dgraphy_importer_spike.py tests/unit/test_dependency_pins.py -q -p no:cacheprovider` → all pass.
Run the full suite: `.venv/bin/python -m pytest -q -p no:cacheprovider -o addopts=""`. If `tests/unit/test_vocab_*`/`test_em_palette_vocab_backed.py` fail because `JSON_config` changed in 1.6, fix the vocab fixture path in `tests/fixtures/s3dgraphy_jsons/` (copy the 1.6 `em_visual_rules.json`/`s3Dgraphy_connections_datamodel.json` beside the `0.1.42` folder and point the fixture at it) — do not weaken assertions.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml requirements.txt tests/unit/test_dependency_pins.py tests/unit/test_s3dgraphy_importer_spike.py tests/fixtures
git commit -m "build(deps): target s3dgraphy>=1.6.0.dev39,<1.7 + importer spike test (issue #2)"
```

---

### Task 1: The graph contract helpers (`strat_graph.py`)

**Files:**
- Create: `pyarchinit_mini/graphproj/strat_graph.py`
- Create: `tests/unit/test_strat_graph.py`
- Create: `tests/unit/strat_graph_factory.py`

**Interfaces:**
- Produces:
  - `new_graph(site: str) -> Graph`
  - `new_strat_node(*, node_id: str, name: str, unit_type: str, description: str = "") -> StratigraphicNode`
  - `is_stratigraphic(node) -> bool`, `stratigraphic_nodes(graph) -> list`, `stratigraphic_edges(graph) -> list`
  - `pyarchinit_attrs(node) -> dict`, `set_pyarchinit_attrs(node, *, us, unit_type, sito, area=None, description=None, periodo=None, fase=None, row_id="row_0", sub_group=None, node_uuid=None, id_us=None, family=None) -> node`
  - `set_swimlane(graph, *, site, group_by, rows: list[dict]) -> None`, `get_swimlane(graph) -> dict`
  - `FALLBACK_ROW = {"row_id": "row_0", "label": "Periodo 1", "periodo": None, "fase": None, "datazione": None, "is_fallback": True}`
  - test factory `make_graph(site="S", group_by="none", rows=None, nodes=(), edges=()) -> Graph` where `nodes` are dicts with keys `id, us, unit_type, area, row_id, sub_group, description, node_uuid` and `edges` are `(src_id, tgt_id, canonical)`.

- [ ] **Step 1: Write the failing tests**

`tests/unit/test_strat_graph.py`:

```python
from s3dgraphy.nodes.geo_position_node import GeoPositionNode
from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode

from pyarchinit_mini.graphproj.strat_graph import (
    FALLBACK_ROW, get_swimlane, new_graph, new_strat_node, pyarchinit_attrs,
    set_pyarchinit_attrs, set_swimlane, stratigraphic_edges, stratigraphic_nodes,
)


def test_new_graph_has_site_id_and_only_the_geo_node():
    g = new_graph("Volterra")
    assert g.graph_id == "strat:Volterra"
    assert stratigraphic_nodes(g) == []
    assert any(isinstance(n, GeoPositionNode) for n in g.nodes)


def test_new_strat_node_picks_subclass_from_unit_type():
    usvs = new_strat_node(node_id="u", name="USVs3", unit_type="USVs")
    assert isinstance(usvs, StratigraphicNode)
    assert type(usvs).__name__ == "StructuralVirtualStratigraphicUnit"
    assert type(new_strat_node(node_id="m", name="USM2", unit_type="USM")).__name__ == "StratigraphicUnit"


def test_set_and_read_pyarchinit_attrs_keeps_legacy_keys():
    n = new_strat_node(node_id="u", name="US1", unit_type="US")
    set_pyarchinit_attrs(n, us="1", unit_type="US", sito="S", area="A", row_id="row_0",
                         node_uuid="u", family="stratigraphic")
    assert pyarchinit_attrs(n)["us"] == "1"
    assert pyarchinit_attrs(n)["area"] == "A"
    assert n.attributes["unit_type"] == "US"
    assert n.attributes["EMid"] == "u"
    assert n.attributes["family"] == "stratigraphic"


def test_pyarchinit_attrs_is_empty_dict_for_foreign_nodes():
    n = new_strat_node(node_id="u", name="US1", unit_type="US")
    assert pyarchinit_attrs(n) == {}


def test_stratigraphic_edges_excludes_edges_to_non_stratigraphic_nodes():
    g = new_graph("S")
    a = g.add_node(new_strat_node(node_id="a", name="US1", unit_type="US"))
    b = g.add_node(new_strat_node(node_id="b", name="US2", unit_type="US"))
    geo = [n for n in g.nodes if isinstance(n, GeoPositionNode)][0]
    g.add_edge("a__overlies__b", "a", "b", "overlies")
    g.add_edge("a_geo", "a", geo.node_id, "generic_connection")
    assert [e.edge_id for e in stratigraphic_edges(g)] == ["a__overlies__b"]


def test_swimlane_roundtrip_and_default():
    g = new_graph("S")
    assert get_swimlane(g) == {"site": "S", "group_by": "none", "rows": []}
    set_swimlane(g, site="S", group_by="area", rows=[FALLBACK_ROW])
    assert get_swimlane(g)["rows"][0]["label"] == "Periodo 1"
    assert get_swimlane(g)["group_by"] == "area"
```

- [ ] **Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/unit/test_strat_graph.py -q -p no:cacheprovider`
Expected: `ModuleNotFoundError: No module named 'pyarchinit_mini.graphproj.strat_graph'`.

- [ ] **Step 3: Implement `strat_graph.py`**

```python
"""The s3dgraphy.Graph contract mini uses everywhere (spec §4).

A projected or imported graph is a plain ``s3dgraphy.Graph``. On top of what
``PyArchInitImporter`` produces, mini adds:

* ``node.attributes["pyarchinit"]`` on every stratigraphic node: the row-level
  facts the swimlane editor, the yEd writer and the DB write-back need and the
  importer does not keep (us number, area, unit type, period/phase, …).
* ``graph.attributes["swimlane"]``: the period rows (lanes) for the editor.

The legacy keys ``unit_type``, ``family`` and ``EMid`` stay on the node for the
ingestor and older callers.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from s3dgraphy.graph import Graph
from s3dgraphy.nodes.base_node import Node
from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode
from s3dgraphy.utils.utils import apply_legacy_kind, get_stratigraphic_node_class

PYARCHINIT_KEY = "pyarchinit"
SWIMLANE_KEY = "swimlane"
FALLBACK_ROW: Dict[str, Any] = {
    "row_id": "row_0", "label": "Periodo 1", "periodo": None, "fase": None,
    "datazione": None, "is_fallback": True,
}


def new_graph(site: str) -> Graph:
    return Graph(
        graph_id=f"strat:{site}",
        name=f"{site} stratigraphic graph",
        description="Projected from PyArchInit-Mini DB",
    )


def new_strat_node(*, node_id: str, name: str, unit_type: str, description: str = "") -> StratigraphicNode:
    kind = (unit_type or "US").strip() or "US"
    cls = get_stratigraphic_node_class(kind)
    node = cls(node_id=node_id, name=name, description=description or "")
    apply_legacy_kind(node, kind)
    return node


def is_stratigraphic(node: Node) -> bool:
    return isinstance(node, StratigraphicNode)


def stratigraphic_nodes(graph: Graph) -> List[Node]:
    return [n for n in graph.nodes if is_stratigraphic(n)]


def stratigraphic_edges(graph: Graph) -> list:
    ids = {n.node_id for n in stratigraphic_nodes(graph)}
    return [e for e in graph.edges if e.edge_source in ids and e.edge_target in ids]


def pyarchinit_attrs(node: Node) -> Dict[str, Any]:
    attrs = node.attributes if getattr(node, "attributes", None) is not None else {}
    return attrs.get(PYARCHINIT_KEY) or {}


def set_pyarchinit_attrs(
    node: Node, *, us: str, unit_type: str, sito: str,
    area: Optional[str] = None, description: Optional[str] = None,
    periodo: Optional[str] = None, fase: Optional[str] = None,
    row_id: str = "row_0", sub_group: Optional[str] = None,
    node_uuid: Optional[str] = None, id_us: Optional[int] = None,
    family: Optional[str] = None,
) -> Node:
    if getattr(node, "attributes", None) is None:
        node.attributes = {}
    node.attributes[PYARCHINIT_KEY] = {
        "id_us": id_us, "sito": sito, "area": area, "us": str(us),
        "unit_type": unit_type or "US", "description": description,
        "periodo": periodo, "fase": fase, "row_id": row_id,
        "sub_group": sub_group, "node_uuid": node_uuid,
    }
    node.attributes["unit_type"] = unit_type or "US"
    node.attributes["family"] = family or "unknown"
    node.attributes["EMid"] = node_uuid or ""
    return node


def set_swimlane(graph: Graph, *, site: str, group_by: str, rows: List[Dict[str, Any]]) -> None:
    graph.attributes[SWIMLANE_KEY] = {"site": site, "group_by": group_by, "rows": list(rows)}


def get_swimlane(graph: Graph) -> Dict[str, Any]:
    stored = (graph.attributes or {}).get(SWIMLANE_KEY)
    if stored:
        return stored
    site = graph.graph_id.split(":", 1)[1] if ":" in (graph.graph_id or "") else (graph.graph_id or "")
    return {"site": site, "group_by": "none", "rows": []}
```

- [ ] **Step 4: Write the test factory** `tests/unit/strat_graph_factory.py`:

```python
"""Build contract-conformant s3dgraphy graphs for view/writer tests (no DB)."""
from pyarchinit_mini.graphproj.strat_graph import (
    FALLBACK_ROW, new_graph, new_strat_node, set_pyarchinit_attrs, set_swimlane,
)


def make_graph(site="S", group_by="none", rows=None, nodes=(), edges=()):
    g = new_graph(site)
    rows = list(rows) if rows is not None else [dict(FALLBACK_ROW)]
    set_swimlane(g, site=site, group_by=group_by, rows=rows)
    for n in nodes:
        node = new_strat_node(node_id=n["id"], name=f"{n.get('unit_type', 'US')}{n['us']}",
                              unit_type=n.get("unit_type", "US"), description=n.get("description") or "")
        set_pyarchinit_attrs(
            node, us=n["us"], unit_type=n.get("unit_type", "US"), sito=site,
            area=n.get("area"), description=n.get("description"),
            periodo=n.get("periodo"), fase=n.get("fase"),
            row_id=n.get("row_id", rows[0]["row_id"]), sub_group=n.get("sub_group"),
            node_uuid=n.get("node_uuid"), id_us=n.get("id_us"),
        )
        g.add_node(node)
    for src, tgt, canonical in edges:
        g.add_edge(f"{src}__{canonical}__{tgt}", src, tgt, canonical)
    return g
```

- [ ] **Step 5: Run tests** — `.venv/bin/python -m pytest tests/unit/test_strat_graph.py -q -p no:cacheprovider` → 6 passed.

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/graphproj/strat_graph.py tests/unit/test_strat_graph.py tests/unit/strat_graph_factory.py
git commit -m "feat(graphproj): s3dgraphy graph contract helpers (pyarchinit attrs, swimlane rows)"
```

---

### Task 2: Connection URL for the importer

**Files:**
- Create: `pyarchinit_mini/graphproj/connection_url.py`
- Create: `tests/unit/test_connection_url.py`

**Interfaces:**
- Produces: `connection_url_from_session(session) -> str` raising `ProjectionError` (from `graphproj/exceptions.py`, signature `ProjectionError(msg, *, site=None)`).

- [ ] **Step 1: Write the failing tests**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from pyarchinit_mini.graphproj.connection_url import connection_url_from_session
from pyarchinit_mini.graphproj.exceptions import ProjectionError


def test_sqlite_file_becomes_absolute_file_url(tmp_path):
    db = tmp_path / "x.db"
    with Session(create_engine(f"sqlite:///{db}")) as s:
        assert connection_url_from_session(s) == f"sqlite:///{db.resolve()}"


def test_relative_sqlite_path_is_made_absolute(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with Session(create_engine("sqlite:///rel.db")) as s:
        assert connection_url_from_session(s) == f"sqlite:///{(tmp_path / 'rel.db').resolve()}"


def test_in_memory_sqlite_is_rejected():
    with Session(create_engine("sqlite://")) as s:
        with pytest.raises(ProjectionError):
            connection_url_from_session(s)


def test_postgres_url_keeps_password_and_driver():
    url = "postgresql+psycopg2://u:p%40ss@db.example:5432/mini"
    with Session(create_engine(url)) as s:   # no connection is opened
        assert connection_url_from_session(s) == url


def test_other_backends_are_rejected():
    with Session(create_engine("mysql+pymysql://u:p@h/db")) as s:
        with pytest.raises(ProjectionError):
            connection_url_from_session(s)
```

(If `pymysql` is not installed the last test must `pytest.importorskip("pymysql")` at the top of that test.)

- [ ] **Step 2: Run to verify failure** — `ModuleNotFoundError`.

- [ ] **Step 3: Implement**

```python
"""Translate mini's SQLAlchemy session into the connection URL s3dgraphy's
PyArchInitImporter accepts (``sqlite:///<abs path>`` or ``postgresql://…``)."""
from __future__ import annotations

import os

from .exceptions import ProjectionError


def connection_url_from_session(session) -> str:
    url = session.get_bind().url
    backend = url.get_backend_name()
    if backend == "sqlite":
        if not url.database or url.database == ":memory:":
            raise ProjectionError(
                "s3dgraphy projection needs a file-backed SQLite database "
                "(in-memory databases cannot be shared with the importer)"
            )
        return "sqlite:///" + os.path.abspath(url.database)
    if backend in ("postgresql", "postgres"):
        return url.render_as_string(hide_password=False)
    raise ProjectionError(f"Unsupported database backend for s3dgraphy projection: {backend}")
```

- [ ] **Step 4: Run tests** → pass. **Step 5: Commit** `feat(graphproj): connection URL resolver for the s3dgraphy importer`.

---

### Task 3: Period rows (`periods.py`)

**Files:**
- Create: `pyarchinit_mini/graphproj/periods.py`
- Create: `tests/unit/test_periods.py`

**Interfaces:**
- Produces: `PeriodRow` dataclass (`row_id, label, periodo, fase, datazione, is_fallback`, `.as_dict()`), `load_period_rows(session, site) -> list[PeriodRow]`, `resolve_row_id(rows, phase) -> str` (appends the fallback row lazily, exactly as `S3DProjector._resolve_row_id` did).

- [ ] **Step 1: Failing tests** (use a file SQLite created with `pyarchinit_mini.database.connection.DatabaseConnection.sqlite(path)` + `create_tables()`, insert with `sqlalchemy.text`):

```python
from sqlalchemy import text

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.graphproj.periods import PeriodRow, load_period_rows, resolve_row_id


def _session(tmp_path):
    conn = DatabaseConnection.sqlite(str(tmp_path / "p.db"))
    conn.create_tables()
    return conn.get_session()


def test_rows_sorted_with_slash_labels(tmp_path):
    with _session(tmp_path) as s:
        s.execute(text("INSERT INTO period_table (sito, periodo, fase, datazione) VALUES ('S','II','a',NULL), ('S','I','b','sec. I')"))
        s.commit()
        rows = load_period_rows(s, "S")
    assert [r.label for r in rows] == ["I/b", "II/a"]
    assert rows[0].row_id == "row_0" and rows[0].datazione == "sec. I" and not rows[0].is_fallback


def test_empty_periodo_rows_are_dropped_and_blank_fase_is_none(tmp_path):
    with _session(tmp_path) as s:
        s.execute(text("INSERT INTO period_table (sito, periodo, fase) VALUES ('S','',''), ('S','I','')"))
        s.commit()
        rows = load_period_rows(s, "S")
    assert [(r.label, r.fase) for r in rows] == [("I", None)]


def test_resolve_matches_fase_then_periodo_then_appends_fallback_once():
    rows = [PeriodRow(row_id="row_0", label="I/a", periodo="I", fase="a")]
    assert resolve_row_id(rows, "a") == "row_0"
    assert resolve_row_id(rows, "I") == "row_0"
    assert resolve_row_id(rows, None) == "row_1"
    assert resolve_row_id(rows, "zzz") == "row_1"
    assert len(rows) == 2 and rows[1].is_fallback and rows[1].label == "Periodo 1"


def test_as_dict_matches_swimlane_row_shape():
    assert PeriodRow(row_id="row_0", label="Periodo 1", is_fallback=True).as_dict() == {
        "row_id": "row_0", "label": "Periodo 1", "periodo": None, "fase": None,
        "datazione": None, "is_fallback": True,
    }
```

- [ ] **Step 2: Run → ModuleNotFoundError.**

- [ ] **Step 3: Implement**

```python
"""Swimlane period rows from mini's period_table (moved from s3d_projector)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy import text

FALLBACK_LABEL = "Periodo 1"


@dataclass
class PeriodRow:
    row_id: str
    label: str
    periodo: Optional[str] = None
    fase: Optional[str] = None
    datazione: Optional[str] = None
    is_fallback: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {"row_id": self.row_id, "label": self.label, "periodo": self.periodo,
                "fase": self.fase, "datazione": self.datazione, "is_fallback": self.is_fallback}


def load_period_rows(session, site: str) -> List[PeriodRow]:
    rows = session.execute(
        text("SELECT periodo, fase, datazione FROM period_table "
             "WHERE sito = :s OR sito IS NULL OR sito = ''"),
        {"s": site},
    ).fetchall()
    items = [(p, (f or None), d) for p, f, d in rows if p]
    items.sort(key=lambda t: (str(t[0] or ""), str(t[1] or "")))
    return [
        PeriodRow(row_id=f"row_{i}", label=(f"{p}/{f}" if f else str(p)), periodo=p, fase=f, datazione=d)
        for i, (p, f, d) in enumerate(items)
    ]


def resolve_row_id(rows: List[PeriodRow], phase: Optional[str]) -> str:
    if phase is not None:
        for r in rows:
            if not r.is_fallback and (r.fase == phase or r.periodo == phase):
                return r.row_id
    for r in rows:
        if r.is_fallback:
            return r.row_id
    fallback = PeriodRow(row_id=f"row_{len(rows)}", label=FALLBACK_LABEL, is_fallback=True)
    rows.append(fallback)
    return fallback.row_id
```

- [ ] **Step 4: Run → pass. Step 5: Commit** `refactor(graphproj): period rows module (from s3d_projector)`.

---

### Task 4: Stratigraphic edges from rapporti (`strat_edges.py`)

**Files:**
- Create: `pyarchinit_mini/graphproj/strat_edges.py`
- Create: `tests/unit/test_strat_edges.py`

**Interfaces:**
- Consumes: `rapporti_codec.parse_rapporti(raw, *, current_site)`, `SYMMETRIC`, `INVERSE_PAIRS`, `REVERSE_TO_FORWARD`; `strat_graph.stratigraphic_nodes`, `pyarchinit_attrs`.
- Produces:
  - `STRATIGRAPHIC_EDGE_TYPES = frozenset(INVERSE_PAIRS) | SYMMETRIC`
  - `@dataclass(frozen=True) StratEdge(source_id, target_id, canonical)`
  - `NodeIndex.from_graph(graph) -> NodeIndex` with `.resolve(us: str, area: str | None) -> str | None` and `.by_id_us: dict[int, str]`
  - `build_stratigraphic_edges(rapporti_rows, *, site, index) -> list[StratEdge]` where `rapporti_rows` is an iterable of `(source_node_id, rapporti_raw)`
  - `add_stratigraphic_edges(graph, edges) -> int`

- [ ] **Step 1: Failing tests**

```python
from pyarchinit_mini.graphproj.strat_edges import (
    NodeIndex, StratEdge, add_stratigraphic_edges, build_stratigraphic_edges,
)
from pyarchinit_mini.graphproj.strat_graph import stratigraphic_edges
from strat_graph_factory import make_graph


def _g():
    return make_graph(nodes=[{"id": "n1", "us": "1", "area": "A"}, {"id": "n2", "us": "2", "area": "A"},
                             {"id": "n3", "us": "3", "area": "A"}, {"id": "n2b", "us": "2", "area": "B"}])


def test_copre_becomes_overlies_forward():
    g = _g(); idx = NodeIndex.from_graph(g)
    edges = build_stratigraphic_edges([("n1", "[['Copre', '2', 'A', 'S']]")], site="S", index=idx)
    assert edges == [StratEdge("n1", "n2", "overlies")]


def test_inverse_rapporti_are_swapped_to_forward():
    g = _g(); idx = NodeIndex.from_graph(g)
    for raw, canonical in [("[['Coperto da', '2', 'A', 'S']]", "overlies"),
                           ("[['Tagliato da', '2', 'A', 'S']]", "cuts"),
                           ("[['Riempito da', '2', 'A', 'S']]", "fills")]:
        assert build_stratigraphic_edges([("n1", raw)], site="S", index=idx) == [StratEdge("n2", "n1", canonical)]


def test_reciprocal_symmetric_is_emitted_once():
    g = _g(); idx = NodeIndex.from_graph(g)
    edges = build_stratigraphic_edges([("n1", "[['Uguale a', '2', 'A', 'S']]"),
                                       ("n2", "[['Uguale a', '1', 'A', 'S']]")], site="S", index=idx)
    assert len(edges) == 1 and edges[0].canonical == "has_same_time"


def test_forward_and_its_inverse_on_both_rows_dedup_to_one_edge():
    g = _g(); idx = NodeIndex.from_graph(g)
    edges = build_stratigraphic_edges([("n1", "[['Copre', '2', 'A', 'S']]"),
                                       ("n2", "[['Coperto da', '1', 'A', 'S']]")], site="S", index=idx)
    assert edges == [StratEdge("n1", "n2", "overlies")]


def test_transitive_reduction_drops_implied_edge():
    g = _g(); idx = NodeIndex.from_graph(g)
    edges = build_stratigraphic_edges([("n1", "[['Copre', '2', 'A', 'S'], ['Copre', '3', 'A', 'S']]"),
                                       ("n2", "[['Copre', '3', 'A', 'S']]")], site="S", index=idx)
    assert set(edges) == {StratEdge("n1", "n2", "overlies"), StratEdge("n2", "n3", "overlies")}


def test_target_resolves_by_area_then_us():
    g = _g(); idx = NodeIndex.from_graph(g)
    assert build_stratigraphic_edges([("n1", "[['Copre', '2', 'B', 'S']]")], site="S", index=idx) == [StratEdge("n1", "n2b", "overlies")]
    assert build_stratigraphic_edges([("n1", "[['Copre', '2']]")], site="S", index=idx)[0].target_id in {"n2", "n2b"}


def test_unknown_target_and_second_rapporto_keep_original_source():
    g = _g(); idx = NodeIndex.from_graph(g)
    edges = build_stratigraphic_edges([("n1", "[['Coperto da', '99', 'A', 'S'], ['Copre', '3', 'A', 'S']]")], site="S", index=idx)
    assert edges == [StratEdge("n1", "n3", "overlies")]


def test_add_edges_is_idempotent_and_uses_contract_ids():
    g = _g()
    e = [StratEdge("n1", "n2", "overlies")]
    assert add_stratigraphic_edges(g, e) == 1
    assert add_stratigraphic_edges(g, e) == 0
    assert [x.edge_id for x in stratigraphic_edges(g)] == ["n1__overlies__n2"]
    assert stratigraphic_edges(g)[0].edge_type == "overlies"
```

(`tests/unit/__init__.py` exists; import the factory as `from tests.unit.strat_graph_factory import make_graph` if the bare import fails under the repo's pytest config.)

- [ ] **Step 2: Run → ModuleNotFoundError.**

- [ ] **Step 3: Implement**

```python
"""Stratigraphic edges from us_table.rapporti, layered on an s3dgraphy.Graph.

s3dgraphy's PyArchInitImporter does not map ``rapporti`` (mapping ``relations``
is empty until s3Dgraphy#26 lands), so mini keeps its codec and adds the edges.
Normalisation is unchanged from the former S3DProjector: inverse → forward with
endpoint swap, symmetric dedup, inverse dedup, per-canonical transitive reduction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from .rapporti_codec import INVERSE_PAIRS, REVERSE_TO_FORWARD, SYMMETRIC, parse_rapporti
from .strat_graph import pyarchinit_attrs, stratigraphic_nodes

STRATIGRAPHIC_EDGE_TYPES = frozenset(INVERSE_PAIRS) | SYMMETRIC


@dataclass(frozen=True)
class StratEdge:
    source_id: str
    target_id: str
    canonical: str


class NodeIndex:
    def __init__(self) -> None:
        self.by_area_us: Dict[Tuple[str, str], str] = {}
        self.by_us: Dict[str, str] = {}
        self.by_id_us: Dict[int, str] = {}

    @classmethod
    def from_graph(cls, graph) -> "NodeIndex":
        idx = cls()
        for node in stratigraphic_nodes(graph):
            a = pyarchinit_attrs(node)
            if not a:
                continue
            us = str(a["us"])
            idx.by_area_us[(a.get("area") or "", us)] = node.node_id
            idx.by_us.setdefault(us, node.node_id)
            if a.get("id_us") is not None:
                idx.by_id_us[int(a["id_us"])] = node.node_id
        return idx

    def resolve(self, us: str, area: Optional[str]) -> Optional[str]:
        if area:
            hit = self.by_area_us.get((area, str(us)))
            if hit:
                return hit
        return self.by_us.get(str(us))


def build_stratigraphic_edges(rapporti_rows: Iterable[Tuple[str, Optional[str]]], *, site: str,
                              index: NodeIndex) -> List[StratEdge]:
    seen = set()
    edges: List[StratEdge] = []
    for source_id, raw in rapporti_rows:
        if not raw or not str(raw).strip():
            continue
        for rap in parse_rapporti(raw, current_site=site):
            target_id = index.resolve(rap.target_us, rap.target_area)
            if target_id is None:
                continue
            canonical, src, tgt = rap.canonical, source_id, target_id
            if canonical in REVERSE_TO_FORWARD:
                canonical = REVERSE_TO_FORWARD[canonical]
                src, tgt = tgt, src
            key = (canonical, tuple(sorted((src, tgt)))) if canonical in SYMMETRIC else (canonical, src, tgt)
            if key in seen:
                continue
            seen.add(key)
            edges.append(StratEdge(src, tgt, canonical))
    return _transitive_reduction(_drop_redundant_inverses(edges))


def _drop_redundant_inverses(edges: List[StratEdge]) -> List[StratEdge]:
    forward = {(e.canonical, e.source_id, e.target_id) for e in edges if e.canonical not in SYMMETRIC}
    kept: List[StratEdge] = []
    for e in edges:
        if e.canonical not in SYMMETRIC:
            inv = INVERSE_PAIRS.get(e.canonical)
            if inv is not None and (inv, e.target_id, e.source_id) in forward and e.canonical > inv:
                continue
        kept.append(e)
    return kept


def _transitive_reduction(edges: List[StratEdge]) -> List[StratEdge]:
    try:
        import networkx as nx
    except ImportError:
        return edges
    by_canon: Dict[str, List[StratEdge]] = {}
    for e in edges:
        by_canon.setdefault(e.canonical, []).append(e)
    reduced: List[StratEdge] = []
    for canon, group in by_canon.items():
        if canon in SYMMETRIC:
            reduced.extend(group)
            continue
        dg = nx.DiGraph()
        dg.add_edges_from((e.source_id, e.target_id) for e in group)
        try:
            keep = set(nx.transitive_reduction(dg).edges())
        except nx.NetworkXError:
            reduced.extend(group)
            continue
        reduced.extend(e for e in group if (e.source_id, e.target_id) in keep)
    return reduced


def add_stratigraphic_edges(graph, edges: Iterable[StratEdge]) -> int:
    added = 0
    for e in edges:
        edge_id = f"{e.source_id}__{e.canonical}__{e.target_id}"
        if graph.find_edge_by_id(edge_id) is None:
            graph.add_edge(edge_id, e.source_id, e.target_id, e.canonical)
            added += 1
    return added
```

- [ ] **Step 4: Run → pass. Step 5: Commit** `refactor(graphproj): rapporti → stratigraphic edge layer on s3dgraphy.Graph`.

---

### Task 5: Row loading and attribute attachment (`enrich.py`)

**Files:**
- Create: `pyarchinit_mini/graphproj/enrich.py`
- Create: `tests/unit/test_enrich.py`

**Interfaces:**
- Consumes: Task 1 helpers, Task 3 `resolve_row_id`, `VocabProvider.instance().get_unit_type(ut)` (existing), the importer instance (for `_resolve_node_name`).
- Produces:
  - `VALID_GROUP_BY = frozenset({"none", "area", "settore", "quadrato", "attivita", "strutture"})`
  - `@dataclass UsRow(id_us, sito, area, us, unita_tipo_raw, unit_type, description, periodo, phase, sub_group, node_uuid, rapporti, settore)`
  - `load_us_rows(session, site, *, group_by="none", area=None) -> list[UsRow]`
  - `attach_pyarchinit_attributes(graph, importer, rows, *, period_rows) -> dict[int, str]` (id_us → node_id; rows that match no node are logged and omitted)

- [ ] **Step 1: Failing tests** (file SQLite via `DatabaseConnection.sqlite(...).create_tables()`; the importer fixture is `PyArchInitImporter(connection_url=f"sqlite:///{path}", mapping_name="pyarchinit_us_mapping", filters={"sito": "S"})`):

```python
import pytest
from s3dgraphy.importer.pyarchinit_importer import PyArchInitImporter
from sqlalchemy import text

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.graphproj.enrich import VALID_GROUP_BY, attach_pyarchinit_attributes, load_us_rows
from pyarchinit_mini.graphproj.periods import PeriodRow
from pyarchinit_mini.graphproj.strat_graph import pyarchinit_attrs, stratigraphic_nodes


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "e.db"
    conn = DatabaseConnection.sqlite(str(path)); conn.create_tables()
    with conn.get_session() as s:
        s.execute(text("INSERT INTO site_table (sito) VALUES ('S')"))
        s.execute(text("INSERT INTO us_table (sito, area, settore, us, unita_tipo, descrizione, fase_iniziale, periodo_iniziale, struttura, node_uuid, rapporti) VALUES "
                       "('S','A','Nord','1','US','d1','a','I','Edificio_A','0192aaaa-0000-7000-8000-000000000001',\"[['Copre', '2', 'A', 'S']]\"),"
                       "('S','A','Nord','2','USM','d2',NULL,NULL,NULL,NULL,NULL)"))
        s.commit()
    return conn, path


def _graph(path):
    imp = PyArchInitImporter(connection_url=f"sqlite:///{path}", mapping_name="pyarchinit_us_mapping", filters={"sito": "S"})
    return imp, imp.parse()


def test_load_rows_reads_description_phase_group_and_rapporti(db):
    conn, _ = db
    with conn.get_session() as s:
        rows = load_us_rows(s, "S", group_by="strutture")
    r = {x.us: x for x in rows}
    assert r["1"].description == "d1" and r["1"].phase == "a" and r["1"].periodo == "I"
    assert r["1"].sub_group == "Edificio_A" and r["2"].sub_group is None
    assert r["1"].rapporti.startswith("[[") and r["2"].unit_type == "USM"


def test_load_rows_rejects_unknown_group_by(db):
    conn, _ = db
    with conn.get_session() as s, pytest.raises(ValueError):
        load_us_rows(s, "S", group_by="banana")
    assert "strutture" in VALID_GROUP_BY


def test_attach_matches_row_by_uuid(db):
    conn, path = db
    imp, g = _graph(path)
    with conn.get_session() as s:
        rows = load_us_rows(s, "S")
    period_rows = [PeriodRow(row_id="row_0", label="I/a", periodo="I", fase="a")]
    mapping = attach_pyarchinit_attributes(g, imp, rows, period_rows=period_rows)
    node = next(n for n in stratigraphic_nodes(g) if n.node_id == "0192aaaa-0000-7000-8000-000000000001")
    a = pyarchinit_attrs(node)
    assert a["us"] == "1" and a["area"] == "A" and a["row_id"] == "row_0" and a["description"] == "d1"
    assert node.attributes["EMid"] == "0192aaaa-0000-7000-8000-000000000001"
    assert mapping[a["id_us"]] == node.node_id


def test_attach_matches_row_without_uuid_by_importer_name(db):
    conn, path = db
    imp, g = _graph(path)
    with conn.get_session() as s:
        rows = load_us_rows(s, "S")
    period_rows = [PeriodRow(row_id="row_0", label="I/a", periodo="I", fase="a")]
    attach_pyarchinit_attributes(g, imp, rows, period_rows=period_rows)
    usm = next(n for n in stratigraphic_nodes(g) if n.name == "A.Nord.USM2")
    assert pyarchinit_attrs(usm)["us"] == "2"
    assert pyarchinit_attrs(usm)["row_id"] == "row_1"        # fallback row appended
    assert period_rows[1].is_fallback


def test_attach_skips_rows_without_node_and_reports_them(db, caplog):
    conn, path = db
    imp, g = _graph(path)
    with conn.get_session() as s:
        rows = load_us_rows(s, "S")
    for n in list(stratigraphic_nodes(g)):
        if n.name == "A.Nord.USM2":
            g.remove_node(n.node_id)
    mapping = attach_pyarchinit_attributes(g, imp, rows, period_rows=[])
    assert len(mapping) == 1 and "A.Nord.USM2" in caplog.text
```

- [ ] **Step 2: Run → ModuleNotFoundError.**

- [ ] **Step 3: Implement**

```python
"""Read the us_table columns the importer does not keep and attach them to the
importer's nodes (spec §4/§5)."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy import text

from .periods import PeriodRow, resolve_row_id
from .strat_graph import is_stratigraphic, set_pyarchinit_attrs, stratigraphic_nodes

logger = logging.getLogger(__name__)

VALID_GROUP_BY = frozenset({"none", "area", "settore", "quadrato", "attivita", "strutture"})
_SUB_GROUP_COLUMN = {"area": "area", "settore": "settore", "quadrato": "quadrato",
                     "attivita": "attivita", "strutture": "struttura"}


@dataclass
class UsRow:
    id_us: int
    sito: str
    area: Optional[str]
    us: str
    unita_tipo_raw: Optional[str]
    unit_type: str
    description: Optional[str]
    periodo: Optional[str]
    phase: Optional[str]
    sub_group: Optional[str]
    node_uuid: Optional[str]
    rapporti: Optional[str]
    settore: Optional[str]


def _available_columns(session) -> set:
    """Column names of us_table on this connection (SQLite and PostgreSQL)."""
    try:
        return set(session.execute(text("SELECT * FROM us_table LIMIT 0")).keys())
    except Exception as exc:
        logger.error("Cannot inspect us_table: %s", exc)
        try:
            session.rollback()
        except Exception:
            pass
        return set()


def load_us_rows(session, site: str, *, group_by: str = "none", area: Optional[str] = None) -> List[UsRow]:
    if group_by not in VALID_GROUP_BY:
        raise ValueError(f"group_by must be one of {sorted(VALID_GROUP_BY)}, got {group_by!r}")
    cols = _available_columns(session)
    if not cols:
        return []

    def pick(*candidates: str) -> str:
        for c in candidates:
            if c in cols:
                return c
        return "NULL"  # selected as a literal NULL column

    group_col = _SUB_GROUP_COLUMN.get(group_by, "")
    sql = (
        f"SELECT id_us, sito, area, us, unita_tipo, "
        f"{pick('descrizione', 'd_stratigrafica')}, {pick('fase_iniziale', 'periodo_iniziale')}, "
        f"{pick('periodo_iniziale')}, {pick('node_uuid')}, {pick('rapporti')}, {pick('settore')}, "
        f"{pick(group_col) if group_col else 'NULL'} "
        f"FROM us_table WHERE sito = :s" + (" AND area = :a" if area else "") + " ORDER BY id_us"
    )
    params = {"s": site, **({"a": area} if area else {})}
    rows = session.execute(text(sql), params).fetchall()
    out: List[UsRow] = []
    for r in rows:
        if group_by == "none":
            sub = None
        elif group_by == "area":
            sub = r[2]
        else:
            sub = r[11]
        out.append(UsRow(
            id_us=r[0], sito=r[1], area=r[2], us=str(r[3]), unita_tipo_raw=r[4],
            unit_type=r[4] or "US", description=r[5], phase=r[6], periodo=r[7],
            sub_group=(str(sub) if sub is not None else None), node_uuid=r[8],
            rapporti=r[9], settore=r[10],
        ))
    return out


def attach_pyarchinit_attributes(graph, importer, rows: List[UsRow], *, period_rows: List[PeriodRow]) -> Dict[int, str]:
    from pyarchinit_mini.vocab.provider import VocabProvider
    provider = VocabProvider.instance()
    by_id = {n.node_id: n for n in stratigraphic_nodes(graph)}
    mapping: Dict[int, str] = {}
    for r in rows:
        node = by_id.get(r.node_uuid) if r.node_uuid else None
        if node is None:
            name = importer._resolve_node_name(
                {"area": r.area, "settore": r.settore, "unita_tipo": r.unita_tipo_raw, "us": r.us}, "us")
            node = graph.find_node_by_name(name)
            if node is None or not is_stratigraphic(node):
                logger.warning("us_table row id_us=%s (%s) has no node in the projected graph; skipped", r.id_us, name)
                continue
        ut = provider.get_unit_type(r.unit_type)
        family = ut.family if (ut and getattr(ut, "family", None)) else "unknown"
        set_pyarchinit_attrs(
            node, us=r.us, unit_type=r.unit_type, sito=r.sito, area=r.area,
            description=r.description, periodo=r.periodo, fase=r.phase,
            row_id=resolve_row_id(period_rows, r.phase), sub_group=r.sub_group,
            node_uuid=r.node_uuid or node.node_id, id_us=r.id_us, family=family,
        )
        mapping[r.id_us] = node.node_id
    return mapping
```

Note the `node_uuid` fallback: for rows with a NULL uuid the node's minted id is stored so `EMid` is never blank; the ingestor treats it as an insert if it is not in the DB, which is the previous behaviour for uuid-less rows.

- [ ] **Step 4: Run → pass. Step 5: Commit** `refactor(graphproj): us_table row loader + attribute attachment onto importer nodes`.

---

### Task 6: `GraphProjector.populate_graph` on the importer

**Files:**
- Rewrite: `pyarchinit_mini/graphproj/projector.py`
- Create: `tests/unit/test_projector_populate.py`
- Modify: `tests/unit/test_graphproj_projector.py` (fixture rapporti to list-of-lists; keep every assertion)

**Interfaces:**
- Consumes: Tasks 1–5.
- Produces: `GraphProjector.populate_graph(session, site, *, area=None, group_by="none") -> s3dgraphy.Graph` with the contract of spec §4; `GraphProjector.MAPPING_NAME = "pyarchinit_us_mapping"`.

- [ ] **Step 1: Failing tests** `tests/unit/test_projector_populate.py`:

```python
import pytest
from sqlalchemy import text

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.graphproj.exceptions import ProjectionError
from pyarchinit_mini.graphproj.projector import GraphProjector
from pyarchinit_mini.graphproj.strat_graph import (
    get_swimlane, pyarchinit_attrs, stratigraphic_edges, stratigraphic_nodes,
)


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "proj.db"
    conn = DatabaseConnection.sqlite(str(path)); conn.create_tables()
    with conn.get_session() as s:
        s.execute(text("INSERT INTO site_table (sito) VALUES ('S')"))
        s.execute(text("INSERT INTO period_table (sito, periodo, fase) VALUES ('S','I','a')"))
        s.execute(text(
            "INSERT INTO us_table (sito, area, settore, us, unita_tipo, descrizione, fase_iniziale, periodo_iniziale, node_uuid, rapporti) VALUES "
            "('S','A','Nord','1','US','d1','a','I','0192aaaa-0000-7000-8000-000000000001',\"[['Copre', '2', 'A', 'S']]\"),"
            "('S','A','Nord','2','USM','d2','a','I',NULL,NULL),"
            "('S','A',NULL,'3','USVs',NULL,NULL,NULL,'0192aaaa-0000-7000-8000-000000000003',\"[['Taglia', '1', 'A', 'S']]\")"))
        s.commit()
    return conn, path


def test_populate_builds_contract_graph(db):
    conn, _ = db
    with conn.get_session() as s:
        g = GraphProjector.populate_graph(s, "S", group_by="area")
    assert g.graph_id == "strat:S"
    nodes = {pyarchinit_attrs(n)["us"]: n for n in stratigraphic_nodes(g)}
    assert set(nodes) == {"1", "2", "3"}
    assert nodes["1"].node_id == "0192aaaa-0000-7000-8000-000000000001"
    assert {(e.edge_source, e.edge_type, e.edge_target) for e in stratigraphic_edges(g)} == {
        (nodes["1"].node_id, "overlies", nodes["2"].node_id),
        (nodes["3"].node_id, "cuts", nodes["1"].node_id),
    }
    sw = get_swimlane(g)
    assert sw["group_by"] == "area" and sw["rows"][0]["label"] == "I/a"
    assert pyarchinit_attrs(nodes["1"])["sub_group"] == "A"


def test_populate_is_stable_for_rows_with_uuid(db):
    conn, _ = db
    with conn.get_session() as s:
        a = GraphProjector.populate_graph(s, "S"); b = GraphProjector.populate_graph(s, "S")
    ids = lambda g: {n.node_id for n in stratigraphic_nodes(g) if pyarchinit_attrs(n)["node_uuid"].startswith("0192")}
    assert ids(a) == ids(b)


def test_populate_area_filter_and_unknown_site(db):
    conn, _ = db
    with conn.get_session() as s:
        assert len(stratigraphic_nodes(GraphProjector.populate_graph(s, "S", area="B"))) == 0
        assert len(stratigraphic_nodes(GraphProjector.populate_graph(s, "NOPE"))) == 0


def test_populate_rejects_bad_group_by(db):
    conn, _ = db
    with conn.get_session() as s, pytest.raises(ValueError):
        GraphProjector.populate_graph(s, "S", group_by="banana")


def test_free_text_rapporti_yield_no_edges(db):
    conn, _ = db
    with conn.get_session() as s:
        s.execute(text("UPDATE us_table SET rapporti = 'copre 2' WHERE us = '1'")); s.commit()
        g = GraphProjector.populate_graph(s, "S")
    assert all(e.edge_type != "overlies" for e in stratigraphic_edges(g))


def test_populate_graph_wraps_importer_failure(db):
    conn, _ = db
    with conn.get_session() as s:
        s.execute(text("DROP TABLE us_table")); s.commit()
        with pytest.raises(ProjectionError):
            GraphProjector.populate_graph(s, "S")
```

- [ ] **Step 2: Run → failures** (`populate_graph() got an unexpected keyword argument 'group_by'`, missing contract attrs).

- [ ] **Step 3: Rewrite `projector.py`**

```python
"""GraphProjector — DB → s3dgraphy.Graph through the shared library (issue #2).

The projection itself is s3dgraphy's ``PyArchInitImporter`` (nodes, qualia,
locations, authors, documents, epochs). Mini adds what the library does not
provide yet: the stratigraphic edges from ``rapporti`` and the swimlane rows /
row-level attributes the editor needs (spec §3–§5).
"""
from __future__ import annotations

import logging
from typing import Optional

from s3dgraphy.graph import Graph
from s3dgraphy.importer.pyarchinit_importer import PyArchInitImporter
from sqlalchemy.orm import Session

from .connection_url import connection_url_from_session
from .enrich import VALID_GROUP_BY, attach_pyarchinit_attributes, load_us_rows
from .exceptions import ProjectionError
from .periods import load_period_rows
from .strat_edges import NodeIndex, add_stratigraphic_edges, build_stratigraphic_edges
from .strat_graph import set_swimlane

logger = logging.getLogger(__name__)


class GraphProjector:
    MAPPING_NAME = "pyarchinit_us_mapping"

    @staticmethod
    def populate_graph(session: Session, site: str, *, area: Optional[str] = None,
                       group_by: str = "none") -> Graph:
        if group_by not in VALID_GROUP_BY:
            raise ValueError(f"group_by must be one of {sorted(VALID_GROUP_BY)}, got {group_by!r}")
        filters = {"sito": site}
        if area:
            filters["area"] = area
        importer = PyArchInitImporter(
            connection_url=connection_url_from_session(session),
            mapping_name=GraphProjector.MAPPING_NAME,
            filters=filters,
        )
        try:
            graph = importer.parse()
        except Exception as exc:  # the importer wraps everything in ImportError
            raise ProjectionError(f"s3dgraphy import failed for site {site!r}: {exc}", site=site) from exc
        graph.graph_id = f"strat:{site}"
        graph.name = f"{site} stratigraphic graph"
        graph.description = "Projected from PyArchInit-Mini DB via s3dgraphy"
        for w in importer.warnings:
            logger.debug("s3dgraphy importer [%s]: %s", site, w)

        period_rows = load_period_rows(session, site)
        us_rows = load_us_rows(session, site, group_by=group_by, area=area)
        attach_pyarchinit_attributes(graph, importer, us_rows, period_rows=period_rows)

        index = NodeIndex.from_graph(graph)
        rapporti_rows = [(index.by_id_us[r.id_us], r.rapporti) for r in us_rows if r.id_us in index.by_id_us]
        add_stratigraphic_edges(graph, build_stratigraphic_edges(rapporti_rows, site=site, index=index))

        set_swimlane(graph, site=site, group_by=group_by, rows=[r.as_dict() for r in period_rows])
        return graph
```

- [ ] **Step 4: Adapt `tests/unit/test_graphproj_projector.py`**: change the fixture's `rapporti` value from `"copre 1002"` to `"[['Copre', '1002', 'A', 'S']]"` (same semantics, codec format); keep every assertion. If the fixture builds its own tables with `sqlite3`, add the columns `node_uuid, settore, periodo_iniziale, fase_iniziale, descrizione` (NULL allowed) so `load_us_rows` finds them.

- [ ] **Step 5: Run** `tests/unit/test_projector_populate.py tests/unit/test_graphproj_projector.py tests/unit/test_auto_regen.py` → pass (auto_regen only needs the signature). Then the full suite; `test_s3d_projector.py` still passes because `s3d_projector.py` is untouched until Task 14.

- [ ] **Step 6: Commit** `feat(graphproj): populate_graph projects through s3dgraphy PyArchInitImporter (issue #2)`.

---

### Task 7: Cytoscape view on `s3dgraphy.Graph`

**Files:**
- Rewrite: `pyarchinit_mini/graphproj/s3d_to_cytoscape.py`
- Modify: `tests/unit/test_s3d_to_cytoscape.py` (build graphs with the factory; assertions unchanged)

**Interfaces:**
- Produces: `to_cytoscape(graph: s3dgraphy.Graph) -> dict` with exactly the JSON of today (period-row compounds, optional cluster compounds `cluster_{row_id}_{sub_group}`, flat palette keys, `is_dashed` strings).

- [ ] **Step 1: Rewrite the tests' graph construction** — replace `ProjectedGraph(...)`/`Node(...)`/`Edge(...)` with `make_graph(site="S", group_by=..., rows=[...], nodes=[{"id": "us_1", "us": "1", "unit_type": "US", "area": "A", "row_id": "row_0", "sub_group": ...}], edges=[("us_1", "us_2", "overlies")])`. Keep every assertion listed in the data-contract report (shape, palette keys, `label == "1"`, `parent == "row_0"`, clusters, `arrowtarget`, `rows[0]`). Add one test: a stratigraphic node **without** pyarchinit attrs (built with `new_strat_node` and `g.add_node`) renders with `label == node.name`, `unit_type == "US"` and `parent == rows[0]["row_id"]`.

- [ ] **Step 2: Run → fails** (`to_cytoscape` expects `ProjectedGraph`).

- [ ] **Step 3: Rewrite the module**

```python
"""Translate the projected s3dgraphy.Graph into cytoscape.js JSON with
palette-derived styles. Output shape unchanged (flat palette keys, period rows
always emitted as compound parents, sub-clusters nested inside rows)."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from pyarchinit_mini.em_palette import get_palette
from .rapporti_codec import SYMMETRIC, display_label
from .strat_graph import get_swimlane, pyarchinit_attrs, stratigraphic_edges, stratigraphic_nodes


def _node_view(node, default_row_id: str) -> Dict[str, Any]:
    a = pyarchinit_attrs(node)
    if a:
        return {"id": node.node_id, "us": a["us"], "area": a.get("area"), "unit_type": a.get("unit_type") or "US",
                "description": a.get("description"), "row_id": a.get("row_id") or default_row_id,
                "sub_group": a.get("sub_group")}
    return {"id": node.node_id, "us": node.name, "area": None, "unit_type": "US",
            "description": node.description or None, "row_id": default_row_id, "sub_group": None}


def to_cytoscape(graph) -> Dict[str, Any]:
    palette = get_palette()
    sw = get_swimlane(graph)
    rows: List[Dict[str, Any]] = list(sw["rows"]) or [{"row_id": "row_0", "label": "Periodo 1", "periodo": None,
                                                        "fase": None, "datazione": None, "is_fallback": True}]
    group_by = sw["group_by"]
    out_nodes: List[Dict[str, Any]] = []
    out_edges: List[Dict[str, Any]] = []

    for r in rows:
        label = f"{r['label']} — {r['datazione']}" if r.get("datazione") else r["label"]
        out_nodes.append({"data": {"id": r["row_id"], "label": label, "compound": True,
                                   "is_period_row": True, "is_fallback": r["is_fallback"]}})

    views = [_node_view(n, rows[0]["row_id"]) for n in stratigraphic_nodes(graph)]
    parent_ids: Dict[Tuple[str, str], str] = {}
    if group_by != "none":
        for v in views:
            if v["sub_group"] is None:
                continue
            key = (v["row_id"], v["sub_group"])
            if key not in parent_ids:
                cluster_id = f"cluster_{v['row_id']}_{v['sub_group']}"
                parent_ids[key] = cluster_id
                out_nodes.append({"data": {"id": cluster_id, "label": v["sub_group"], "row": v["row_id"],
                                           "compound": True, "is_period_row": False, "parent": v["row_id"]}})

    for v in views:
        ns = palette.get_node_style(v["unit_type"])
        parent = parent_ids.get((v["row_id"], v["sub_group"]), v["row_id"]) if (group_by != "none" and v["sub_group"] is not None) else v["row_id"]
        out_nodes.append({"data": {
            "id": v["id"], "label": v["us"], "us": v["us"], "area": v["area"], "unit_type": v["unit_type"],
            "description": v["description"], "row": v["row_id"], "parent": parent,
            "shape": ns.shape, "bgcolor": ns.fill_color, "bordercolor": ns.border_color,
            "borderwidth": ns.border_width, "borderstyle": ns.border_style,
            "fontcolor": ns.font_color, "fontsize": ns.font_size,
        }})

    for e in stratigraphic_edges(graph):
        canonical = e.edge_type
        es = palette.get_edge_style(canonical)
        out_edges.append({"data": {
            "id": f"{e.edge_source}__{canonical}__{e.edge_target}", "source": e.edge_source, "target": e.edge_target,
            "label": display_label(canonical, locale="it"), "canonical": canonical,
            "linecolor": es.line_color, "linewidth": es.line_width, "linestyle": es.line_style,
            "arrowtarget": "none" if canonical in SYMMETRIC else es.arrow_target, "arrowsource": es.arrow_source,
            "is_dashed": "true" if canonical == "cuts" else "false",
        }})

    return {"site": sw["site"], "group_by": group_by,
            "rows": [{"row_id": r["row_id"], "label": r["label"], "periodo": r.get("periodo"), "fase": r.get("fase"),
                      "datazione": r.get("datazione"), "is_fallback": r["is_fallback"]} for r in rows],
            "nodes": out_nodes, "edges": out_edges}
```

- [ ] **Step 4: Run** `tests/unit/test_s3d_to_cytoscape.py` → pass. **Step 5: Commit** `refactor(graphproj): cytoscape view reads the s3dgraphy graph contract`.

---

### Task 8: yEd TableNode writer on `s3dgraphy.Graph`

**Files:**
- Rewrite: `pyarchinit_mini/graphproj/graphml_writer.py`
- Modify: the unit test that covers it (`tests/unit/test_graphml_writer*.py` — locate with `grep -rl "graphproj.graphml_writer" tests/`); build inputs with the factory.

**Interfaces:**
- Produces: `write_graphml(graph, *, palette_path=None) -> bytes` (unchanged signature). Node data passed to `write_extended_matrix_graphml` now also carries `node_uuid`, `period`, `phase` (keys read by `graphml_io/yed_writer.py`).

- [ ] **Step 1: Adapt/extend tests**: keep the existing assertions (bytes start with `<?xml`/`<graphml`, contains `YED_TABLE_NODE`, one `<y:Row` per row, node labels, Italian edge labels). Add: `test_yed_output_carries_node_uuid` — a node with `node_uuid="0192aaaa-…"` makes that string appear in the output.

- [ ] **Step 2: Run → fails.**

- [ ] **Step 3: Rewrite the module**

```python
"""yEd-flavoured GraphML writer (EM Harris Matrix Creator format) from the
projected s3dgraphy.Graph: ONE <y:TableNode> group with one <y:Row> per
swimlane row, US nodes positioned inside their row, Italian edge labels.
Thin bridge to graphml_io.yed_writer.write_extended_matrix_graphml."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

from .rapporti_codec import CANONICAL_TO_ITALIAN, display_label
from .strat_graph import get_swimlane, pyarchinit_attrs, stratigraphic_edges, stratigraphic_nodes


def write_graphml(graph, *, palette_path: Optional[Path] = None) -> bytes:
    """Render the graph as yEd-compatible GraphML bytes (palette_path is ignored)."""
    from pyarchinit_mini.harris_swimlane.swimlane_state import CytoscapeElement
    from pyarchinit_mini.harris_swimlane.row_provider import Row as LegacyRow, PERIOD_COLORS
    from pyarchinit_mini.graphml_io.yed_writer import write_extended_matrix_graphml

    sw = get_swimlane(graph)
    swim_rows = list(sw["rows"]) or [{"row_id": "row_0", "label": "Periodo 1", "periodo": None,
                                      "fase": None, "datazione": None, "is_fallback": True}]
    rows = [
        LegacyRow(row_id=r["row_id"], period_name=r.get("periodo") or r["label"], phase_name=r.get("fase"),
                  start_date=None, end_date=None, color=PERIOD_COLORS[i % len(PERIOD_COLORS)],
                  source="fallback" if r["is_fallback"] else "period_table")
        for i, r in enumerate(swim_rows)
    ]
    row_index = {r["row_id"]: i for i, r in enumerate(swim_rows)}
    row_height, node_h, node_w = 200, 30.0, 80.0
    col_counter: dict = {}

    nodes = []
    for node in stratigraphic_nodes(graph):
        a = pyarchinit_attrs(node)
        us = str(a.get("us") or node.name)
        row_id = a.get("row_id") or swim_rows[0]["row_id"]
        ri = row_index.get(row_id, 0)
        col = col_counter.get(row_id, 0)
        col_counter[row_id] = col + 1
        nodes.append(CytoscapeElement(
            data={
                "id": node.node_id, "us": us, "us_number": us, "label": us,
                "area": a.get("area") or "", "unit_type": a.get("unit_type") or "US",
                "description": a.get("description") or (node.description or ""),
                "row": row_id, "node_uuid": a.get("node_uuid") or node.node_id,
                "period": a.get("periodo") or "", "phase": a.get("fase") or "",
            },
            position={"x": col * (node_w + 20) + 30, "y": ri * row_height + (row_height / 2 - node_h / 2)},
        ))

    edges = []
    for e in stratigraphic_edges(graph):
        canonical = e.edge_type
        edges.append(CytoscapeElement(data={
            "id": f"{e.edge_source}__{canonical}__{e.edge_target}",
            "source": e.edge_source, "target": e.edge_target,
            "label": display_label(canonical, locale="it"), "canonical": canonical,
            "relationship": CANONICAL_TO_ITALIAN.get(canonical, canonical),
        }))

    class _State:
        site = sw["site"]
        group_by = sw["group_by"]
        pending_changes: dict = {}

    state = _State()
    state.rows, state.nodes, state.edges = rows, nodes, edges
    epochs = [{"row_id": r["row_id"], "periodo": r.get("periodo"), "fase": r.get("fase"),
               "datazione": r["datazione"]} for r in swim_rows if r.get("datazione")]

    with tempfile.NamedTemporaryFile(suffix=".graphml", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        write_extended_matrix_graphml(state, site_meta={"sito": sw["site"]}, epochs=epochs, out=Path(tmp_path))
        with open(tmp_path, "rb") as fh:
            return fh.read()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
```

- [ ] **Step 4: Run → pass. Step 5: Commit** `refactor(graphproj): yEd TableNode writer reads the s3dgraphy graph (now emits node_uuid)`.

---

### Task 9: Switch the editor call sites to the new projector

**Files:**
- Modify: `pyarchinit_mini/harris_swimlane/swimlane_state.py:118-160` (`_load_via_s3dgraphy`)
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py` (`/api/load/<site>` ~l.729-760, `/api/export/<site>/yed-graphml` ~l.885-900, imports l.743-746/890-896)
- Tests: `tests/unit/test_harris_swimlane_state_save.py`, `tests/integration/test_harris_swimlane_routes_save.py`, and the route tests that patch `S3DProjector` (find with `grep -rn "S3DProjector\|s3d_projector" tests/`).

**Interfaces:**
- Consumes: `GraphProjector.populate_graph(session, site, group_by=…)`, `to_cytoscape(graph)`, `write_graphml(graph)`, `VALID_GROUP_BY` from `graphproj.enrich`.

- [ ] **Step 1: Update tests first**: every `patch("…s3d_projector.S3DProjector.from_site")` becomes `patch("pyarchinit_mini.graphproj.projector.GraphProjector.populate_graph")` returning `make_graph(...)`; imports of `VALID_GROUP_BY` move to `pyarchinit_mini.graphproj.enrich`. Run them → fail (old symbols still imported by production code paths under test).

- [ ] **Step 2: Edit `swimlane_state._load_via_s3dgraphy`**:

```python
from pyarchinit_mini.graphproj.enrich import VALID_GROUP_BY
from pyarchinit_mini.graphproj.projector import GraphProjector
from pyarchinit_mini.graphproj.s3d_to_cytoscape import to_cytoscape

s3d_group_by = group_by if group_by in VALID_GROUP_BY else "none"
graph = GraphProjector.populate_graph(session, site, group_by=s3d_group_by)
cyto = to_cytoscape(graph)
return _make_state_from_cytoscape(site, group_by, cyto)
```

- [ ] **Step 3: Edit `harris_creator_routes`**: `/api/load/<site>` → `graph = GraphProjector.populate_graph(db, site, group_by=group_by); payload = to_cytoscape(graph)`; `/api/export/<site>/yed-graphml` → `graph = GraphProjector.populate_graph(db, site, group_by=group_by); data = write_graphml(graph)`; replace `from pyarchinit_mini.graphproj.s3d_projector import S3DProjector, VALID_GROUP_BY` with `from pyarchinit_mini.graphproj.enrich import VALID_GROUP_BY` + `from pyarchinit_mini.graphproj.projector import GraphProjector`. Keep the `X-Pipeline-Fallback: legacy` behaviour unchanged.

- [ ] **Step 4: Run** the swimlane/harris tests and the full suite → pass. **Step 5: Commit** `refactor(harris): editor load/export use GraphProjector on s3dgraphy (no ProjectedGraph)`.

---

### Task 10: yEd minimal reader and Heriverse parser produce `s3dgraphy.Graph`

**Files:**
- Rewrite: `pyarchinit_mini/graphproj/graphml_reader.py`, `pyarchinit_mini/graphproj/heriverse_parser.py`
- Modify: their unit tests (`grep -rl "graphml_reader\|heriverse_parser" tests/`): assert on `stratigraphic_nodes(g)`, `pyarchinit_attrs(n)["us"]`, `stratigraphic_edges(g)[i].edge_type`, `get_swimlane(g)["rows"] == [FALLBACK_ROW]`.

**Interfaces:**
- Produces: `parse_graphml(raw: bytes, *, target_site: str) -> Graph`, `parse_heriverse(raw_json: str) -> Graph`; both set `pyarchinit` attrs (`us`, `unit_type`, `area`, `sito`, `description`, `row_id="row_0"`) and the fallback swimlane row.

- [ ] **Step 1: Adapt tests, run → fail.**

- [ ] **Step 2: Implement** — keep the XML/JSON walking code as is; replace node/edge construction:

```python
# graphml_reader.py (inside parse_graphml, after the XML walk collected (xml_id, label) pairs and (src, tgt, label) edges)
graph = new_graph(target_site)
set_swimlane(graph, site=target_site, group_by="none", rows=[dict(FALLBACK_ROW)])
for xml_id, label in node_pairs:
    node = new_strat_node(node_id=xml_id, name=label, unit_type="US")
    set_pyarchinit_attrs(node, us=label, unit_type="US", sito=target_site, row_id="row_0", node_uuid=xml_id)
    graph.add_node(node)
known = {n.node_id for n in stratigraphic_nodes(graph)}
for src, tgt, edge_label in edge_triples:
    if src in known and tgt in known:
        canonical = _resolve_canonical(edge_label) or "overlies"
        graph.add_edge(f"{src}__{canonical}__{tgt}", src, tgt, canonical)
return graph
```

`heriverse_parser.py` — keep `EDGE_TYPE_MAP` and the JSON walk; replace the node/edge construction with:

```python
def parse_heriverse(raw_json: str):
    data = json.loads(raw_json)
    g0 = data["multigraph"]["graphs"][0]
    site = g0.get("name") or "UnknownSite"
    graph = new_graph(site)
    set_swimlane(graph, site=site, group_by="none", rows=[dict(FALLBACK_ROW)])
    counter = 0
    for unit_type, items in (g0.get("nodes") or {}).items():
        for item in items:
            counter += 1
            node_id = item.get("id") or f"us_{counter}"
            us = str(item.get("name") or item.get("id") or "?")
            node = new_strat_node(node_id=node_id, name=f"{unit_type}{us}", unit_type=unit_type,
                                  description=item.get("description") or "")
            set_pyarchinit_attrs(node, us=us, unit_type=unit_type, sito=site,
                                 area=(item.get("data") or {}).get("area"),
                                 description=item.get("description"), row_id="row_0", node_uuid=node_id)
            graph.add_node(node)
    known = {n.node_id for n in stratigraphic_nodes(graph)}
    for edge_type, items in (g0.get("edges") or {}).items():
        canonical = EDGE_TYPE_MAP.get(edge_type, edge_type)
        for item in items:
            src, tgt = item.get("from"), item.get("to")
            if src in known and tgt in known:
                graph.add_edge(f"{src}__{canonical}__{tgt}", src, tgt, canonical)
    return graph
```

Both modules import `json`/`xml` as today plus `from .strat_graph import FALLBACK_ROW, new_graph, new_strat_node, set_pyarchinit_attrs, set_swimlane, stratigraphic_nodes`. The route that imports Heriverse JSON passes its own `target_site` to `write_graph`, so the site inside the graph is informational only.

- [ ] **Step 3: Run → pass. Step 4: Commit** `refactor(graphproj): yEd/Heriverse readers build s3dgraphy graphs`.

---

### Task 11: DB write-back from `s3dgraphy.Graph`

**Files:**
- Rewrite the top of `pyarchinit_mini/graphproj/graph_to_db.py` (signature + node/edge reads; the per-US rapporti merge stays identical)
- Modify: `tests/unit/test_graph_to_db.py` (inputs via the factory; every assertion kept)

**Interfaces:**
- Produces: `write_graph(graph: s3dgraphy.Graph, *, target_site, session, source_label="import") -> WriteResult` (unchanged result dataclass).

- [ ] **Step 1: Adapt tests** (`make_graph(nodes=[{"id": "n1", "us": "1", "area": "A", "unit_type": "USM"}, …], edges=[("n1", "n2", "overlies")])`; the "Imported placeholder" case sets `description`). Run → fail.

- [ ] **Step 2: Implement** — replace the `ProjectedGraph, Node` import with (add `import re` and `Optional` to the module imports):

```python
from typing import NamedTuple
from .strat_graph import pyarchinit_attrs, stratigraphic_edges, stratigraphic_nodes


class _NodeView(NamedTuple):
    node_id: str
    us: str
    area: Optional[str]
    unit_type: str
    description: Optional[str]


def _us_from_name(name: str) -> str:
    m = re.search(r"(\d+)\s*$", name or "")
    return m.group(1) if m else (name or "")


def _views(graph) -> List[_NodeView]:
    out = []
    for n in stratigraphic_nodes(graph):
        a = pyarchinit_attrs(n)
        out.append(_NodeView(n.node_id, str(a.get("us") or _us_from_name(n.name)), a.get("area"),
                             a.get("unit_type") or "US", a.get("description") if a else (n.description or None)))
    return out
```

and in `write_graph`: `for n in _views(graph): …` (unchanged body), `by_node_id = {v.node_id: v for v in _views(graph)}`, `for e in stratigraphic_edges(graph): src = by_node_id.get(e.edge_source); tgt = by_node_id.get(e.edge_target); canonical = e.edge_type` (then the existing forward/inverse `Rapporto` code with `canonical` in place of `e.canonical`). `_upsert_us_row(n, …)` keeps reading `n.us/n.area/n.unit_type/n.description`.

- [ ] **Step 3: Run → pass. Step 4: Commit** `refactor(graphproj): write_graph consumes the s3dgraphy graph contract`.

---

### Task 12: Ingestor US number from attributes

**Files:**
- Modify: `pyarchinit_mini/graphproj/ingestor.py:57-66`
- Modify: `tests/unit/test_graphproj_ingestor_preview.py` (+1 test)

- [ ] **Step 1: Failing tests** (append to `tests/unit/test_graphproj_ingestor_preview.py`; reuse that file's existing session fixture — it seeds site `S`/`Volterra` with one US — and add the imports `from s3dgraphy.graph import Graph`, `from s3dgraphy.nodes.base_node import Node`, `from strat_graph_factory import make_graph`; replace `session_with_site` below with that fixture's name):

```python
def test_us_number_uses_trailing_digits_when_no_attrs(session_with_site):
    g = Graph(graph_id="x")
    n = Node("A1_12", "A1.US12", ""); n.attributes = {"unit_type": "US", "EMid": ""}
    g.add_node(n)
    plan = GraphIngestor(session_with_site, "S").preview(g)
    assert [e.after["us"] for e in plan.inserts] == [12]


def test_us_number_prefers_pyarchinit_attrs(session_with_site):
    g = make_graph(site="S", nodes=[{"id": "u", "us": "77", "unit_type": "US", "node_uuid": ""}])
    plan = GraphIngestor(session_with_site, "S").preview(g)
    assert [e.after["us"] for e in plan.inserts] == [77]
```

(`make_graph` stores the node id as `EMid` when `node_uuid` is empty — see Task 5's note; an id not present in `us_table` is classified as an insert, which is what the assertion needs.)

- [ ] **Step 2: Run → first test fails (`112`).**

- [ ] **Step 3: Implement** — replace the digit filter with (add `import re` to the module):

```python
from .strat_graph import pyarchinit_attrs

def _us_number(node) -> Optional[int]:
    a = pyarchinit_attrs(node)
    if a.get("us") is not None and str(a["us"]).strip().isdigit():
        return int(str(a["us"]).strip())
    m = re.search(r"(\d+)\s*$", node.name or "")
    return int(m.group(1)) if m else None
```

and use `us = _us_number(node); if us is None: continue`.

- [ ] **Step 4: Run** the two ingestor test files → pass. **Step 5: Commit** `fix(graphproj): ingestor reads the US number from attrs, else trailing digits`.

---

### Task 13: Import routes + Postgres/Adarte parity check (before deleting the old projector)

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py` (`/api/import/<site>/graphml` ~l.973-985, `/api/import/<site>/json` ~l.1002-1018)
- Create: `pyarchinit_mini/scripts/graph_parity_check.py`
- Tests: `tests/integration/test_matrix_import_upload_route.py` and any route test patching `parse_graphml`/`parse_heriverse`/`write_graph`.

- [ ] **Step 1: Routes** — drop the lines that overwrote `projected.site` and `n.sito`; the readers already take `target_site` / `write_graph` takes `target_site`. Run the route tests → pass.

- [ ] **Step 2: Parity script** (maintainer-run; read-only):

```python
"""Compare the new s3dgraphy projection with the old S3DProjector on a real DB.

Usage: DATABASE_URL=postgresql://… python -m pyarchinit_mini.scripts.graph_parity_check "<site>"
Prints node/edge counts of both pipelines, the per-canonical edge histogram, and wall time.
Acceptance (spec §7): |edges_new - edges_old| <= 5 % and populate_graph < 3 s.
"""
import os, sys, time
from collections import Counter
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.graphproj.projector import GraphProjector
from pyarchinit_mini.graphproj.s3d_projector import S3DProjector
from pyarchinit_mini.graphproj.strat_graph import stratigraphic_edges, stratigraphic_nodes

site = sys.argv[1]
conn = DatabaseConnection.from_url(os.environ["DATABASE_URL"])
with conn.get_session() as s:
    t0 = time.perf_counter(); old = S3DProjector.from_site(s, site, "none"); t_old = time.perf_counter() - t0
    t0 = time.perf_counter(); new = GraphProjector.populate_graph(s, site); t_new = time.perf_counter() - t0
print(f"old: {len(old.nodes)} nodes {len(old.edges)} edges in {t_old:.2f}s")
print(f"new: {len(stratigraphic_nodes(new))} nodes {len(stratigraphic_edges(new))} edges in {t_new:.2f}s (graph total {len(new.nodes)} nodes)")
print("old by canonical:", Counter(e.canonical for e in old.edges))
print("new by canonical:", Counter(e.edge_type for e in stratigraphic_edges(new)))
```

Run it against the Adarte database for `Rimini_RN_2020_21_Museo_Fellini` (exact name from `site_table`) with `DATABASE_URL` from `.adarte_secrets.sh` (`ADARTE_DB`), and against a local SQLite copy of the tutorial DB. Record the numbers in the PR/commit message. If the edge delta exceeds 5 %, diff the per-canonical histograms before continuing: the usual cause is `(area, us)` resolution changing a target that the old `us`-only index resolved to the wrong area — that is a correctness improvement, document it; any other cause is a bug in Task 4.

- [ ] **Step 3: Commit** `chore(graphproj): import routes on the new readers + parity check script`.

---

### Task 14: Delete `s3d_projector.py` and guard against regressions

**Files:**
- Delete: `pyarchinit_mini/graphproj/s3d_projector.py`, `pyarchinit_mini/scripts/graph_parity_check.py` (one-off, numbers recorded in Task 13's commit), `tests/unit/test_s3d_projector.py` (its cases now live in `test_periods.py`, `test_strat_edges.py`, `test_enrich.py`, `test_projector_populate.py` — verify each listed behaviour has a home before deleting: empty period_table → one fallback row; sorted labels; phase→row; Copre/Coperto da/Tagliato da/Riempito da; reciprocal Uguale a; group_by area/settore/strutture/none; missing sub-group column; no reverse canonicals).
- Create: `tests/unit/test_no_projected_graph.py`

- [ ] **Step 1: Guard test**

```python
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_projected_graph_model_is_gone():
    hits = subprocess.run(["grep", "-rn", "ProjectedGraph\\|s3d_projector", str(ROOT / "pyarchinit_mini")],
                          capture_output=True, text=True).stdout
    assert hits == "", hits
```

- [ ] **Step 2: Run → fails** (hits listed). Delete the files, fix any remaining import the grep shows, rerun → pass.

- [ ] **Step 3: Full suite** → green. **Step 4: Commit** `refactor(graphproj): remove ProjectedGraph/S3DProjector — projection is s3dgraphy-only (closes the code side of #2)`.

---

### Task 15: Docs, changelog, release and issue bookkeeping

**Files:**
- Modify: `docs/GRAPH_AUTO_REGEN.md` (projection = s3dgraphy importer + mini edge layer; the regenerated GraphML now carries qualia/location/author nodes), `docs/HARRIS_SWIMLANE.md` (pipeline section), `docs/features/s3dgraphy.rst` (one paragraph: what the library does for mini, what stays local and why)
- Modify: `CHANGELOG.md` (new `## 3.6.0` entry), `pyproject.toml` + `pyarchinit_mini/__init__.py` + `adarte_deploy.sh` version → `3.6.0`

- [ ] **Step 1: CHANGELOG entry**

```markdown
## 3.6.0 — <date>

### Changed — DB⇄graph projection through s3dgraphy (issue #2)
- `GraphProjector.populate_graph()` now projects `us_table` through the shared library's
  `PyArchInitImporter` (s3dgraphy ≥ 1.6.0.dev39): node ids are the row `node_uuid`, nodes
  are typed `StratigraphicNode` subclasses, and the graph carries qualia (`has_property`),
  locations (`is_in_location`), authors and documents; on plugin-schema databases also
  epochs. The local `ProjectedGraph` model (`graphproj/s3d_projector.py`) is gone.
- Mini keeps, as thin layers on that graph: stratigraphic edges from `rapporti`
  (`rapporti_codec`, same normalisation as before), swimlane rows from `period_table`,
  the cytoscape view, the yEd TableNode export (which now also writes `node_uuid`), the
  yEd/Heriverse readers and the DB write-back.
- Dependency: `s3dgraphy>=1.6.0.dev39,<1.7`; `requires-python>=3.9`.
- Not changed: the StratiGraph bundle/sync layer (`stratigraph/`), pending WP4 bundle I/O in s3dgraphy.
```

- [ ] **Step 2: Version bump + full suite + commit** `chore(release): 3.6.0 — s3dgraphy-based DB⇄graph projection (issue #2)`.

- [ ] **Step 3: Release** per `docs`/memory deploy workflow: `python -m build`, `twine upload dist/*3.6.0*`, push `main` (Railway auto-deploy — poll `railway deployment list --json` until SUCCESS and curl the login page), `./adarte_deploy.sh`; then open `/harris-creator` on Adarte for the Rimini site and confirm the editor loads with the parity numbers from Task 13.

- [ ] **Step 4: Issues** — comment on and close enzococca/pyarchinit-mini#2 (what landed, the three follow-ups from spec §8); comment on zalmoxes-laran/s3Dgraphy#25 under the "mini (#2)" item: adopted on 1.6.0.dev39; `rapporti` edges still mini-side until #26 covers `relations`; bundle I/O awaited in the library (mini keeps its `stratigraph/` bundle code until then).
