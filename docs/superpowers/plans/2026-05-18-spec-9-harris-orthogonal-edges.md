# Spec 9 — Harris orthogonal edges Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render Harris Matrix Creator stratigraphic edges as right-angle orthogonal paths (Cytoscape `taxi`), matching the yEd `y:PolyLineEdge` style used by pyarchinit QGIS. Increase server-side layout spacing so the new routing has room to breathe.

**Architecture:** Two-file change. `harris_creator_editor.js` (Cytoscape `edge` selector) gains three new style properties: `curve-style: 'taxi'`, `taxi-direction: 'vertical'`, `taxi-turn: 'auto'`. `harris_layout.py` bumps two default integers in `compute_harris_positions` (`v_gap` 20→40, `h_gap` 30→50). No logic changes, no API breaking.

**Tech Stack:** Cytoscape.js 3.26 (already loaded), pyarchinit_mini.harris_swimlane.harris_layout (Python).

**Spec:** `docs/superpowers/specs/2026-05-18-spec-9-harris-orthogonal-edges-design.md`

---

## File Structure

### Modify

- `pyarchinit_mini/__init__.py` — bump `2.5.1` → `2.6.0`
- `pyproject.toml` — same version bump
- `CHANGELOG.md` — new `[2.6.0]` section IT + EN
- `pyarchinit_mini/harris_swimlane/harris_layout.py` — defaults `v_gap=40`, `h_gap=50`
- `pyarchinit_mini/web_interface/static/js/harris_creator_editor.js` — edge style block
- `tests/unit/test_harris_layout.py` — append 2 default-introspection tests

### Create

(no new files)

---

## Task 1: harris_layout default v_gap and h_gap bumped

**Files:**
- Modify: `pyarchinit_mini/harris_swimlane/harris_layout.py`
- Test: `tests/unit/test_harris_layout.py` (append)

- [ ] **Step 1: Write the failing tests**

Append at the END of `tests/unit/test_harris_layout.py`:

```python
import inspect

from pyarchinit_mini.harris_swimlane import harris_layout as _harris_layout_mod


def test_compute_harris_positions_default_v_gap_is_40():
    """Spec 9: bumped v_gap default 20 → 40 for orthogonal edge breathing room."""
    sig = inspect.signature(_harris_layout_mod.compute_harris_positions)
    assert sig.parameters["v_gap"].default == 40


def test_compute_harris_positions_default_h_gap_is_50():
    """Spec 9: bumped h_gap default 30 → 50 for orthogonal edge breathing room."""
    sig = inspect.signature(_harris_layout_mod.compute_harris_positions)
    assert sig.parameters["h_gap"].default == 50
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/unit/test_harris_layout.py::test_compute_harris_positions_default_v_gap_is_40 tests/unit/test_harris_layout.py::test_compute_harris_positions_default_h_gap_is_50 -v`
Expected: 2 failures (`AssertionError: 20 != 40` and `AssertionError: 30 != 50`).

- [ ] **Step 3: Bump the defaults**

Open `pyarchinit_mini/harris_swimlane/harris_layout.py`. Locate the function signature:

```python
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
```

Change ONLY `h_gap` and `v_gap` defaults:

```python
def compute_harris_positions(
    nodes: list[dict],
    edges: list[dict],
    *,
    lane_id_for: Callable[[dict], str],
    lane_widths: dict[str, int],
    node_w: int = 80,
    node_h: int = 30,
    h_gap: int = 50,
    v_gap: int = 40,
) -> dict[str, tuple[float, float]]:
```

Leave the function body and `_layout_lane` helper unchanged.

- [ ] **Step 4: Run the two new tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/unit/test_harris_layout.py::test_compute_harris_positions_default_v_gap_is_40 tests/unit/test_harris_layout.py::test_compute_harris_positions_default_h_gap_is_50 -v`
Expected: 2 passed.

- [ ] **Step 5: Run the full harris_layout suite (regression)**

Run: `.venv/bin/python -m pytest tests/unit/test_harris_layout.py -v`
Expected: 10 passed (8 prior + 2 new). The 8 prior tests pass `lane_widths` explicitly and use synthetic graphs, so the default bump doesn't affect their assertions.

- [ ] **Step 6: Run swimlane integration tests (regression)**

Run: `.venv/bin/python -m pytest tests/integration/test_swimlane_group_by.py tests/integration/test_harris_swimlane_routes_*.py -q --tb=line`
Expected: all pass. `SwimlaneState.load` (Spec 7) calls `compute_harris_positions` with explicit `lane_id_for` + `lane_widths` but NO override of `h_gap`/`v_gap`, so it will silently pick up the new defaults — the only effect is that positions are spread out more. No assertions in these integration tests depend on the exact (x, y) values.

- [ ] **Step 7: Commit**

```bash
git add pyarchinit_mini/harris_swimlane/harris_layout.py tests/unit/test_harris_layout.py
git commit -m "feat(spec9): harris_layout defaults v_gap=40, h_gap=50"
```

---

## Task 2: harris_creator_editor.js — orthogonal edge style

**Files:**
- Modify: `pyarchinit_mini/web_interface/static/js/harris_creator_editor.js`

- [ ] **Step 1: Locate the edge selector**

Run: `grep -n "selector: 'edge'" /Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/web_interface/static/js/harris_creator_editor.js | head -3`

Expected: a match around line 261 (the base edge selector). The other matches (`edge:selected`, `edge[style="dashed"]`, etc.) are override selectors — leave them alone; they inherit from the base.

- [ ] **Step 2: Modify the base edge style block**

Open `pyarchinit_mini/web_interface/static/js/harris_creator_editor.js`. Locate the block at around lines 260-269:

```javascript
            // Edge styles - default (normal stratigraphic)
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#666',
                    'target-arrow-color': '#666',
                    'target-arrow-shape': 'triangle',
                }
            },
```

REPLACE the `style` object to add three new properties (curve-style + taxi-direction + taxi-turn), preserving the four existing ones:

```javascript
            // Edge styles - default (normal stratigraphic)
            // Spec 9: orthogonal routing matches yEd PolyLineEdge style used
            // by pyarchinit QGIS plugin.
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#666',
                    'target-arrow-color': '#666',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'taxi',
                    'taxi-direction': 'vertical',
                    'taxi-turn': 'auto',
                }
            },
```

Do NOT modify any other selector block (`edge:selected`, `edge[style="dashed"]`, `edge[edgeCategory="negative"]`, etc.) — they cascade from the base and inherit the new `curve-style` automatically.

- [ ] **Step 3: Smoke-test app boot**

Run:
```bash
.venv/bin/python -c "
from pyarchinit_mini.web_interface.app import create_app
ret = create_app()
app = ret[0] if isinstance(ret, tuple) else ret
print('App loaded OK, harris_creator_editor.js served as static')
"
```
Expected: `App loaded OK, ...`

- [ ] **Step 4: Grep-verify the new properties are present**

Run:
```bash
grep -c "'curve-style': 'taxi'" /Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/web_interface/static/js/harris_creator_editor.js
grep -c "'taxi-direction': 'vertical'" /Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/web_interface/static/js/harris_creator_editor.js
grep -c "'taxi-turn': 'auto'" /Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/web_interface/static/js/harris_creator_editor.js
```
Expected: `1`, `1`, `1` (each property appears exactly once in the base edge selector).

- [ ] **Step 5: Run swimlane integration regression**

Run: `.venv/bin/python -m pytest tests/integration/test_swimlane_group_by.py tests/integration/test_harris_swimlane_routes_*.py tests/unit/test_harris_layout.py -q --tb=line`
Expected: all pass.

- [ ] **Step 6: Manual smoke (if pyarchinit-mini-web is running locally on 5001)**

Open in browser: `http://localhost:5001/harris-creator/editor?site=<your_test_site>`

The edges between US nodes should now render with 90° angles (a vertical segment, then a horizontal segment) instead of curved diagonals. If the browser was cached, hard-reload (Ctrl+Shift+R / Cmd+Shift+R).

If pyarchinit-mini-web isn't running locally, skip this step — Task 4 (manual smoke + final sweep) will catch issues.

- [ ] **Step 7: Commit**

```bash
git add pyarchinit_mini/web_interface/static/js/harris_creator_editor.js
git commit -m "feat(spec9): harris_creator_editor edges use orthogonal taxi routing"
```

---

## Task 3: Bump version to 2.6.0 + CHANGELOG

**Files:**
- Modify: `pyarchinit_mini/__init__.py`
- Modify: `pyproject.toml`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Bump version in pyproject.toml**

Edit `/Users/enzo/pyarchinit-mini-desk/pyproject.toml` and change:
```
version = "2.5.1"
```
to:
```
version = "2.6.0"
```

- [ ] **Step 2: Bump version in __init__.py**

Edit `/Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/__init__.py` and change:
```
__version__ = "2.5.1"
```
to:
```
__version__ = "2.6.0"
```

- [ ] **Step 3: Prepend the `[2.6.0]` section to CHANGELOG.md**

At the TOP of `CHANGELOG.md` (BEFORE the existing `## [2.5.1]` entry), PREPEND this exact block:

```markdown
## [2.6.0] - 2026-05-18

### Changed (IT)
- Editor Harris Matrix Creator: gli archi stratigrafici sono ora resi con
  routing ortogonale (90°, `curve-style: 'taxi'`) invece che con curve
  bezier diagonali. Allineato al `y:PolyLineEdge` di yEd usato da
  pyarchinit QGIS plugin.
- `harris_swimlane/harris_layout.py`: defaults aumentati a `v_gap=40`
  (era 20) e `h_gap=50` (era 30) per dare respiro agli archi ortogonali.
  Chiamanti che passano i parametri esplicitamente non sono toccati.

### Changed (EN)
- Harris Matrix Creator editor: stratigraphic edges now render with
  right-angle routing (`curve-style: 'taxi'`) instead of bezier curves,
  matching the `y:PolyLineEdge` style used by pyarchinit QGIS.
- `harris_swimlane/harris_layout.py`: defaults bumped to `v_gap=40`
  (was 20) and `h_gap=50` (was 30) to give orthogonal edges breathing
  room. Explicit callers are unaffected.

```

- [ ] **Step 4: Run the full test suite**

Run: `.venv/bin/python -m pytest tests/ -q --tb=no 2>&1 | tail -5`
Expected: the same baseline as before Spec 9 (the only pre-existing
failure is `tests/unit/test_site_service.py::test_delete_site`). All
other tests pass — including the 2 new harris_layout default tests from
Task 1 and the 8 prior harris_layout tests.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/__init__.py pyproject.toml CHANGELOG.md
git commit -m "release: bump to 2.6.0 (Spec 9 Harris orthogonal edges)"
```

---

## Task 4: Final regression sweep + manual smoke

**Files:** (none modified)

- [ ] **Step 1: Run the full test suite one more time**

Run: `.venv/bin/python -m pytest tests/ -q --tb=short 2>&1 | tail -10`

Expected: 1 failure (`test_delete_site`, pre-existing), all new and prior tests pass.

- [ ] **Step 2: Verify the version is exposed correctly**

Run:
```bash
.venv/bin/python -c "import pyarchinit_mini; print(pyarchinit_mini.__version__)"
```
Expected: `2.6.0`

- [ ] **Step 3: Verify URL map unchanged**

Run:
```bash
.venv/bin/python -c "
from pyarchinit_mini.web_interface.app import create_app
ret = create_app(); app = ret[0] if isinstance(ret, tuple) else ret
rules = [r.rule for r in app.url_map.iter_rules() if 'harris-creator' in r.rule]
print(f'harris-creator routes: {len(rules)}')
"
```
Expected: same number of routes as before (Spec 9 doesn't add or remove any). Just confirms no regression.

- [ ] **Step 4: Manual smoke (optional if pyarchinit-mini-web is running on 5001)**

Open `http://localhost:5001/harris-creator/editor?site=<a site with edges>` in browser. Hard-reload (Ctrl+Shift+R).

Verify:
1. Edges between US nodes render as right-angle paths (vertical segment + horizontal segment), not bezier curves.
2. The matrix appears slightly more spread out vertically and horizontally (the larger gap defaults).
3. No console errors related to `taxi` / `curve-style`.

If any of those fail, document in the commit (this task does not block on manual smoke since it requires a running server, but the smoke results should be recorded).

No commit needed if all checks pass.

---

## Self-Review

### Spec coverage

| Spec section | Task |
|---|---|
| §1 Goal | Tasks 1 + 2 |
| §3 Architecture (2 files) | Tasks 1 + 2 |
| §4.1 harris_creator_editor.js taxi style | Task 2 |
| §4.2 harris_layout.py defaults | Task 1 |
| §5 Data flow | implicit via Tasks 1+2 (no new code path) |
| §6 Error handling | n/a (no new error paths) |
| §7 Testing (default introspection + regression) | Tasks 1, 4 |
| §8 DoD bump + CHANGELOG | Task 3 |
| §9 Backwards compat (explicit callers unaffected) | confirmed in Task 1 step 6 |

### Placeholder scan

No "TBD", "TODO", or "implement later" in plan body — verified.

### Type consistency

- `v_gap`/`h_gap` int defaults consistent between Task 1 spec (40, 50) and Task 4 verification.
- Cytoscape property names (`curve-style`, `taxi-direction`, `taxi-turn`) consistent between Task 2 implementation and Task 2 grep verification.

Plan complete. Ready for implementation.
