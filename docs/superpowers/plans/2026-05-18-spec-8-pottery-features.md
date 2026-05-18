# Spec 8 — Pottery Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add pottery preview thumbnails, id_number+anno search filters, fix language-switch URL preservation, and inline gallery in detail view.

**Architecture:** New `lang_routes` blueprint owns `POST /set-language/<lang>` (saves session + redirect to referrer). `PotteryService._FILTERABLE` gains `id_number`, `anno` with integer cast guard. `MediaService` gets a batch `get_media_for_entity_ids` to pre-load thumbs without N+1 in the list view. Templates: list.html grows 2 inputs + mini-carousel (CSS scroll-snap) + GLightbox; detail.html gains a `<div id="pottery-media-grid">` filled by `/api/media/by-entity/pottery/<id>` + GLightbox.

**Tech Stack:** Flask + Flask-Babel, SQLAlchemy 2.x, Bootstrap 5, GLightbox 3.2.0 (already in base.html), pytest.

**Spec:** `docs/superpowers/specs/2026-05-18-spec-8-pottery-features-design.md`

---

## File Structure

### Create

- `pyarchinit_mini/i18n/lang_routes.py`
- `tests/integration/test_lang_routes.py`
- `tests/integration/test_pottery_filters_id_number_anno.py`
- `tests/integration/test_pottery_list_media_thumbs.py`

### Modify

- `pyarchinit_mini/__init__.py` — bump `2.5.0` → `2.5.1`
- `pyproject.toml` — same version bump
- `CHANGELOG.md` — new `[2.5.1]` section IT + EN
- `pyarchinit_mini/web_interface/app.py` — register `lang_bp` + CSRF exempt
- `pyarchinit_mini/services/pottery_service.py` — `_FILTERABLE` + integer-cast for id_number/anno
- `pyarchinit_mini/services/media_service.py` — new `get_media_for_entity_ids` batch method
- `pyarchinit_mini/web_interface/pottery_routes.py` — `FILTER_KEYS`, pre-load media batch
- `pyarchinit_mini/web_interface/templates/pottery/list.html` — 2 input filtri + mini-carousel
- `pyarchinit_mini/web_interface/templates/pottery/detail.html` — gallery grid section
- `pyarchinit_mini/web_interface/templates/components/language_switcher.html` — `<a>` → POST form

---

## Task 1: `lang_routes` blueprint

**Files:**
- Create: `pyarchinit_mini/i18n/lang_routes.py`
- Test: `tests/integration/test_lang_routes.py`

- [ ] **Step 1: Write the failing test**

Create `tests/integration/test_lang_routes.py`:

```python
"""Integration tests for /set-language/<lang> endpoint."""
import pytest
from flask import Flask

from pyarchinit_mini.i18n.lang_routes import lang_bp


@pytest.fixture
def client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"
    app.register_blueprint(lang_bp)

    # Stub `index` route so url_for fallback resolves.
    @app.route("/")
    def index():
        return "home"

    return app.test_client()


def test_set_language_it_saves_session(client):
    r = client.post("/set-language/it", headers={"Referer": "/pottery/?q=test"})
    assert r.status_code == 302
    assert r.location == "/pottery/?q=test"
    with client.session_transaction() as s:
        assert s["lang"] == "it"


def test_set_language_en_saves_session(client):
    r = client.post("/set-language/en", headers={"Referer": "/pottery/"})
    assert r.status_code == 302
    with client.session_transaction() as s:
        assert s["lang"] == "en"


def test_set_language_invalid_redirects_no_change(client):
    r = client.post("/set-language/zh", headers={"Referer": "/pottery/"})
    assert r.status_code == 302
    with client.session_transaction() as s:
        assert "lang" not in s


def test_set_language_no_referrer_falls_back_to_index(client):
    r = client.post("/set-language/it")
    assert r.status_code == 302
    assert r.location.endswith("/")


def test_set_language_preserves_query_string(client):
    r = client.post(
        "/set-language/en",
        headers={"Referer": "/pottery/?sito=Volterra&id_number=42&anno=2024"},
    )
    assert r.status_code == 302
    assert r.location == "/pottery/?sito=Volterra&id_number=42&anno=2024"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/integration/test_lang_routes.py -v`
Expected: `ImportError: cannot import name 'lang_bp' from 'pyarchinit_mini.i18n.lang_routes'`.

- [ ] **Step 3: Implement `lang_routes.py`**

Create `pyarchinit_mini/i18n/lang_routes.py` with EXACT content:

```python
"""Blueprint for language switching — POST + redirect to referrer.

Preserves the current URL query string by relying on the browser's Referer
header. Compatible with the existing get_locale() resolution chain
(session > URL > Accept-Language > default).
"""
from flask import Blueprint, session, redirect, request, url_for

lang_bp = Blueprint("lang", __name__)

_VALID_LANGS = frozenset({"it", "en"})


@lang_bp.post("/set-language/<lang>")
def set_language(lang: str):
    """Save chosen language in session, redirect back to referrer (or /)."""
    if lang in _VALID_LANGS:
        session["lang"] = lang
        session.permanent = True
    target = request.referrer or url_for("index")
    return redirect(target)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/integration/test_lang_routes.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/i18n/lang_routes.py tests/integration/test_lang_routes.py
git commit -m "feat(spec8): lang_routes blueprint — POST /set-language/<lang>"
```

---

## Task 2: Register `lang_bp` in app.py with CSRF exemption

**Files:**
- Modify: `pyarchinit_mini/web_interface/app.py`

- [ ] **Step 1: Locate the existing blueprint registration block**

Run: `grep -n "csrf.exempt\|register_blueprint(yed_import_bp\|register_blueprint(paradata_ui_bp" /Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/web_interface/app.py | head -5`

Identify the line where `yed_import_bp` is registered and where the `csrf.exempt(...)` calls live (around lines 580–595 per the existing file).

- [ ] **Step 2: Add the import + registration**

Open `pyarchinit_mini/web_interface/app.py` and locate this block:

```python
    # Register yEd GraphML import blueprint (Spec 7)
    app.register_blueprint(yed_import_bp)
```

Just BEFORE it, ADD:

```python
    # Register language switcher blueprint (Spec 8)
    from pyarchinit_mini.i18n.lang_routes import lang_bp
    app.register_blueprint(lang_bp)
```

Then in the `csrf.exempt(...)` block (where paradata_ui_bp and yed_import_bp are already exempt), ADD on its own line:

```python
    csrf.exempt(lang_bp)            # Spec 8 — POST /set-language/<lang>
```

- [ ] **Step 3: Smoke-test app boot + route discovery**

Run:
```bash
.venv/bin/python -c "
from pyarchinit_mini.web_interface.app import create_app
ret = create_app()
app = ret[0] if isinstance(ret, tuple) else ret
rules = [r.rule for r in app.url_map.iter_rules() if 'set-language' in r.rule]
assert rules, 'lang_bp not registered'
print('OK lang routes:', rules)
"
```
Expected: `OK lang routes: ['/set-language/<lang>']`

- [ ] **Step 4: Verify regression**

Run: `.venv/bin/python -m pytest tests/integration/test_lang_routes.py -v`
Expected: 5 passed (unchanged).

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/app.py
git commit -m "feat(spec8): register lang_bp + CSRF exempt"
```

---

## Task 3: language_switcher.html → POST form

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/components/language_switcher.html`

- [ ] **Step 1: Replace template content**

REWRITE `pyarchinit_mini/web_interface/templates/components/language_switcher.html` with EXACT content:

```html
<!-- Language Switcher Component (Spec 8 — POST form preserves query string via Referer) -->
<div class="language-switcher ms-3">
    <div class="btn-group" role="group" aria-label="Language selector">
        {% set current_lang = get_locale() %}
        <form method="post" action="{{ url_for('lang.set_language', lang='it') }}" class="d-inline m-0">
            <button type="submit"
                    class="btn btn-sm {% if current_lang == 'it' %}btn-primary{% else %}btn-outline-secondary{% endif %}"
                    title="Italiano">🇮🇹 IT</button>
        </form>
        <form method="post" action="{{ url_for('lang.set_language', lang='en') }}" class="d-inline m-0">
            <button type="submit"
                    class="btn btn-sm {% if current_lang == 'en' %}btn-primary{% else %}btn-outline-secondary{% endif %}"
                    title="English">🇬🇧 EN</button>
        </form>
    </div>
</div>

<style>
.language-switcher .btn {
    font-size: 0.875rem;
    padding: 0.25rem 0.5rem;
}

.language-switcher .btn:hover {
    text-decoration: none;
}
</style>
```

- [ ] **Step 2: Smoke test via curl**

Open a local pyarchinit-mini-web (if running on 5001) and run:
```bash
curl -s -X POST -H "Referer: http://localhost:5001/pottery/?q=test" -i http://localhost:5001/set-language/en 2>&1 | head -10
```
Expected: HTTP 302 + `Location: http://localhost:5001/pottery/?q=test`

If pyarchinit-mini-web isn't running locally, skip and rely on Task 1's unit tests.

- [ ] **Step 3: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/components/language_switcher.html
git commit -m "feat(spec8): language switcher uses POST form preserving query string"
```

---

## Task 4: PotteryService filters — id_number + anno

**Files:**
- Modify: `pyarchinit_mini/services/pottery_service.py:115-141`
- Test: `tests/integration/test_pottery_filters_id_number_anno.py`

- [ ] **Step 1: Write failing tests**

Create `tests/integration/test_pottery_filters_id_number_anno.py`:

```python
"""PotteryService respects id_number / anno filters with integer-cast guard."""
import sqlite3
from pathlib import Path
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.models.base import Base
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.models.pottery import Pottery
from pyarchinit_mini.services.pottery_service import PotteryService


@pytest.fixture
def db_manager(tmp_path):
    db = tmp_path / "pot_filters.db"
    conn = DatabaseConnection.from_url(f"sqlite:///{db}")
    Base.metadata.create_all(conn.engine)
    mgr = DatabaseManager(conn)
    # Seed 4 rows: 2 different anno, 2 different id_number
    with conn.get_session() as s:
        s.add(Site(sito="TestSite"))
        s.commit()
    with conn.get_session() as s:
        s.add(Pottery(sito="TestSite", us=1, id_number=10, anno=2024, form="amphora"))
        s.add(Pottery(sito="TestSite", us=2, id_number=11, anno=2024, form="olla"))
        s.add(Pottery(sito="TestSite", us=3, id_number=12, anno=2025, form="amphora"))
        s.add(Pottery(sito="TestSite", us=4, id_number=13, anno=2025, form="olla"))
        s.commit()
    return mgr


def test_filter_by_id_number(db_manager):
    svc = PotteryService(db_manager)
    items, total = svc.get_all_pottery(filters={"id_number": 11})
    assert total == 1
    assert items[0].id_number == 11


def test_filter_by_anno(db_manager):
    svc = PotteryService(db_manager)
    items, total = svc.get_all_pottery(filters={"anno": 2024})
    assert total == 2
    assert {i.anno for i in items} == {2024}


def test_filter_combined_id_number_and_anno(db_manager):
    svc = PotteryService(db_manager)
    items, total = svc.get_all_pottery(filters={"anno": 2025, "id_number": 12})
    assert total == 1
    assert items[0].id_number == 12 and items[0].anno == 2025


def test_filter_id_number_non_numeric_ignored(db_manager):
    """A non-numeric id_number must be silently ignored (no SQL error)."""
    svc = PotteryService(db_manager)
    items, total = svc.get_all_pottery(filters={"id_number": "abc"})
    assert total == 4  # all 4 rows returned (filter dropped)


def test_filter_anno_non_numeric_ignored(db_manager):
    svc = PotteryService(db_manager)
    items, total = svc.get_all_pottery(filters={"anno": "xyz"})
    assert total == 4
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/integration/test_pottery_filters_id_number_anno.py -v`
Expected: 5 failures (current `_FILTERABLE` does not include `id_number`/`anno`).

- [ ] **Step 3: Update `_apply_filters` in pottery_service.py**

Open `pyarchinit_mini/services/pottery_service.py`. Locate line 116 where `_FILTERABLE = ("sito", "area", "us", "form", "fabric", "ware", "material")` is defined.

REPLACE the `_apply_filters` method (lines ~115-141) with:

```python
    # ---------- Listing & Filtering ----------
    _FILTERABLE = ("sito", "area", "us", "form", "fabric", "ware", "material")
    _FILTERABLE_INT = ("id_number", "anno")

    def _apply_filters(self, q, filters: Optional[Dict[str, Any]]):
        if not filters:
            return q
        for k in self._FILTERABLE:
            v = filters.get(k)
            if v in (None, ""):
                continue
            col = getattr(Pottery, k)
            q = q.filter(col == v)
        for k in self._FILTERABLE_INT:
            v = filters.get(k)
            if v in (None, ""):
                continue
            try:
                ival = int(v)
            except (TypeError, ValueError):
                continue  # silently drop non-numeric input
            col = getattr(Pottery, k)
            q = q.filter(col == ival)
        q_text = filters.get("q")
        if q_text:
            like = f"%{q_text}%"
            q = q.filter(
                or_(
                    Pottery.form.ilike(like),
                    Pottery.specific_form.ilike(like),
                    Pottery.fabric.ilike(like),
                    Pottery.ware.ilike(like),
                    Pottery.note.ilike(like),
                    Pottery.descrip_ex_deco.ilike(like),
                    Pottery.descrip_in_deco.ilike(like),
                )
            )
        return q
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/integration/test_pottery_filters_id_number_anno.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/services/pottery_service.py \
        tests/integration/test_pottery_filters_id_number_anno.py
git commit -m "feat(spec8): PotteryService filters by id_number + anno"
```

---

## Task 5: pottery_routes FILTER_KEYS extended

**Files:**
- Modify: `pyarchinit_mini/web_interface/pottery_routes.py`

- [ ] **Step 1: Locate FILTER_KEYS occurrences**

Run: `grep -nE "\\(\"sito\",\\s*\"area\",\\s*\"us\",\\s*\"form\",\\s*\"fabric\"\\)" /Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/web_interface/pottery_routes.py`

Expected: 4–5 matches around lines 72, 233, 259, 375, 409.

- [ ] **Step 2: Replace each tuple inline**

Open `pyarchinit_mini/web_interface/pottery_routes.py`. Find each occurrence of the literal tuple
`("sito","area","us","form","fabric")` and replace it with
`("sito","area","us","form","fabric","id_number","anno")`.

There are 4 such tuples (lines 72-ish inside pottery_list dict-comprehension, lines 233/259/375 inside the export views, and possibly line 73 in `q=request.args.get("q")` paragraph — leave that one alone, replace only the tuples).

After editing, verify with:
```bash
grep -nE "\"id_number\",\"anno\"" /Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/web_interface/pottery_routes.py | wc -l
```
Expected: at least 4.

- [ ] **Step 3: Manual smoke test (if local web is up)**

Visit `http://localhost:5001/pottery/?id_number=10&anno=2024` — the filtered set should restrict.

- [ ] **Step 4: Run full pottery test suite**

Run: `.venv/bin/python -m pytest tests/integration/test_pottery_*.py tests/integration/test_pottery_filters_id_number_anno.py -q --tb=line`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/pottery_routes.py
git commit -m "feat(spec8): pottery_routes filters dict includes id_number + anno"
```

---

## Task 6: MediaService batch helper + pre-load in pottery_list

**Files:**
- Modify: `pyarchinit_mini/services/media_service.py`
- Modify: `pyarchinit_mini/web_interface/pottery_routes.py`
- Test: `tests/integration/test_pottery_list_media_thumbs.py`

- [ ] **Step 1: Write failing test**

Create `tests/integration/test_pottery_list_media_thumbs.py`:

```python
"""pottery_list pre-loads media via MediaService.get_media_for_entity_ids."""
from pathlib import Path
import pytest

from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.models.base import Base
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.models.pottery import Pottery
from pyarchinit_mini.services.media_service import MediaService


@pytest.fixture
def db_manager(tmp_path):
    db = tmp_path / "media_batch.db"
    conn = DatabaseConnection.from_url(f"sqlite:///{db}")
    Base.metadata.create_all(conn.engine)
    return DatabaseManager(conn)


def test_get_media_for_entity_ids_empty_input(db_manager):
    svc = MediaService(db_manager)
    out = svc.get_media_for_entity_ids("pottery", [])
    assert out == {}


def test_get_media_for_entity_ids_returns_dict_by_id(db_manager):
    """With no rows in media_table, every id maps to an empty list."""
    svc = MediaService(db_manager)
    out = svc.get_media_for_entity_ids("pottery", [1, 2, 3])
    assert out == {1: [], 2: [], 3: []}
```

- [ ] **Step 2: Run — expect failure**

Run: `.venv/bin/python -m pytest tests/integration/test_pottery_list_media_thumbs.py -v`
Expected: `AttributeError: 'MediaService' object has no attribute 'get_media_for_entity_ids'`.

- [ ] **Step 3: Add the batch method to MediaService**

Open `pyarchinit_mini/services/media_service.py`. Find the existing `def get_media_by_entity` method (around line 93). Right AFTER it (preserving indentation as a class method), add:

```python
    def get_media_for_entity_ids(
        self, entity_type: str, entity_ids: list[int]
    ) -> dict[int, list[dict]]:
        """Pre-load media for many entities in one shot, returning a dict
        keyed by entity_id with a list of media descriptors.

        Avoids the N+1 problem when rendering paginated lists. Every input id
        appears in the output (with an empty list if no media exist), so the
        caller can safely do `out.get(id, [])` or just `out[id]`.

        Each media descriptor is:
            {"id_media": int, "media_name": str, "media_path": str,
             "media_type": str, "url": "/media/<path>", "thumb_url": "/media/<path>"}
        """
        result: dict[int, list[dict]] = {eid: [] for eid in entity_ids}
        if not entity_ids:
            return result
        for eid in entity_ids:
            try:
                items = self.get_media_by_entity(entity_type, eid)
            except Exception:
                items = []
            result[eid] = [
                {
                    "id_media": m.id_media,
                    "media_name": m.media_name,
                    "media_path": m.media_path,
                    "media_type": m.media_type,
                    "url": f"/media/{m.media_path}",
                    "thumb_url": f"/media/{m.media_path}",
                }
                for m in items
            ]
        return result
```

NOTE: this is a per-id loop, not a single SQL query — get_media_by_entity already exists and works. Real batch SQL is a YAGNI optimisation; we can do it later if pagination size grows large.

- [ ] **Step 4: Wire into pottery_list**

Open `pyarchinit_mini/web_interface/pottery_routes.py`. Locate the `pottery_list` function (around line 68). At its end, BEFORE the `render_template(...)` call, prepare `media_by_pottery`:

Find a snippet like:
```python
    return render_template(
        "pottery/list.html",
        items=items, filters=filters, total=total, page=page, size=size,
        media_ids=media_ids,
    )
```

REPLACE with:
```python
    # Spec 8 — preload media descriptors for thumbnails in list cells.
    from pyarchinit_mini.services.media_service import MediaService
    media_svc = MediaService(app.db_manager)
    media_by_pottery = media_svc.get_media_for_entity_ids(
        "pottery", [p.id_rep for p in items]
    )
    return render_template(
        "pottery/list.html",
        items=items, filters=filters, total=total, page=page, size=size,
        media_ids=media_ids,
        media_by_pottery=media_by_pottery,
    )
```

If `media_ids` is computed in the existing function, leave that logic in place — `media_by_pottery` is additional, not replacement.

- [ ] **Step 5: Run tests**

Run: `.venv/bin/python -m pytest tests/integration/test_pottery_list_media_thumbs.py tests/integration/test_pottery_filters_id_number_anno.py -v`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/services/media_service.py \
        pyarchinit_mini/web_interface/pottery_routes.py \
        tests/integration/test_pottery_list_media_thumbs.py
git commit -m "feat(spec8): MediaService batch + pottery_list pre-loads thumbs"
```

---

## Task 7: list.html — 2 input filters + mini-carousel column

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/pottery/list.html`

- [ ] **Step 1: Replace the filter form**

Open `pyarchinit_mini/web_interface/templates/pottery/list.html`. Locate the existing `<form method="get" class="row g-2 mb-3">` block (around lines 16-26). REPLACE it with:

```html
  <form method="get" class="row g-2 mb-3">
    <div class="col-md-2"><input class="form-control form-control-sm" type="text"   name="sito"      value="{{ filters.sito or '' }}" placeholder="Sito"></div>
    <div class="col-md-1"><input class="form-control form-control-sm" type="text"   name="area"      value="{{ filters.area or '' }}" placeholder="Area"></div>
    <div class="col-md-1"><input class="form-control form-control-sm" type="number" name="us"        value="{{ filters.us or '' }}" placeholder="US"></div>
    <div class="col-md-1"><input class="form-control form-control-sm" type="number" name="id_number" value="{{ filters.id_number or '' }}" placeholder="ID num" min="0"></div>
    <div class="col-md-1"><input class="form-control form-control-sm" type="number" name="anno"      value="{{ filters.anno or '' }}" placeholder="Anno" min="1900" max="2099"></div>
    <div class="col-md-2"><input class="form-control form-control-sm" type="text"   name="form"      value="{{ filters.form or '' }}" placeholder="Forma" list="dl-forms"></div>
    <div class="col-md-1"><input class="form-control form-control-sm" type="text"   name="fabric"    value="{{ filters.fabric or '' }}" placeholder="Impasto" list="dl-fabrics"></div>
    <div class="col-md-2"><input class="form-control form-control-sm" type="text"   name="q"         value="{{ filters.q or '' }}" placeholder="Ricerca"></div>
    <div class="col-md-1"><button class="btn btn-sm btn-secondary">Filtra</button></div>
    <datalist id="dl-forms"></datalist>
    <datalist id="dl-fabrics"></datalist>
  </form>
```

- [ ] **Step 2: Replace the Media cell**

In the same file, locate the cell that renders the media badge (around lines 41-47):
```html
        <td>
          {% if p.id_rep in media_ids %}
            <span class="badge bg-success" title="Media allegati"><i class="fas fa-paperclip"></i> Sì</span>
          {% else %}
            <span class="badge bg-secondary" title="Nessun media">No</span>
          {% endif %}
        </td>
```

REPLACE with:
```html
        <td>
          {% set media_list = media_by_pottery.get(p.id_rep, []) %}
          {% if media_list %}
            <div class="pottery-mini-carousel" role="list">
              {% for m in media_list %}
                <a class="glightbox" data-gallery="pot-{{ p.id_rep }}"
                   href="{{ m.url }}" data-title="{{ m.media_name }}" role="listitem">
                  <img src="{{ m.thumb_url or m.url }}" alt="" loading="lazy"
                       width="48" height="48"
                       style="object-fit:cover;border-radius:3px"/>
                </a>
              {% endfor %}
            </div>
          {% else %}
            <span class="badge bg-secondary">No</span>
          {% endif %}
        </td>
```

- [ ] **Step 3: Add CSS for the mini-carousel**

At the top of `list.html` (after `{% block content %}` is opened but before the main `<div>`, or inside a new `{% block extra_css %}` block if not present), ADD:

```html
{% block extra_css %}
<style>
.pottery-mini-carousel {
  display: flex; gap: 4px; max-width: 200px;
  overflow-x: auto; scroll-snap-type: x mandatory;
  padding: 2px;
}
.pottery-mini-carousel > a { scroll-snap-align: start; flex: 0 0 auto; }
.pottery-mini-carousel::-webkit-scrollbar { height: 4px; }
.pottery-mini-carousel::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 2px; }
</style>
{% endblock %}
```

If a `{% block extra_css %}` block already exists in list.html, APPEND the `<style>` content to it instead of creating a duplicate.

- [ ] **Step 4: Bind GLightbox after the table**

At the BOTTOM of `list.html` (before `{% endblock %}`), inside the existing `<script>` block (or add one if not present), APPEND:

```html
<script>
document.addEventListener('DOMContentLoaded', function () {
  if (window.GLightbox) {
    GLightbox({ selector: '.pottery-mini-carousel a.glightbox' });
  }
});
</script>
```

GLightbox JS is already loaded from base.html (verified at template line ~17). If you don't see it, add it to base.html in the `{% block extra_js %}`.

- [ ] **Step 5: Manual smoke check (if web is up)**

Visit `http://localhost:5001/pottery/?id_number=10` — input should pre-populate; cell should show thumbnails for pottery with media.

- [ ] **Step 6: Verify regression**

Run: `.venv/bin/python -m pytest tests/integration/test_pottery_*.py tests/integration/test_pottery_filters_id_number_anno.py tests/integration/test_pottery_list_media_thumbs.py -q --tb=line`
Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/pottery/list.html
git commit -m "feat(spec8): pottery list — id_number/anno filters + mini-carousel thumbs"
```

---

## Task 8: detail.html — gallery grid + GLightbox

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/pottery/detail.html`

- [ ] **Step 1: Locate insertion point**

Open `pyarchinit_mini/web_interface/templates/pottery/detail.html`. The current file already calls `fetch("/api/media/by-entity/pottery/{{ pottery.id_rep }}")` around line 56 (in a `<script>` block) but does not visualize the result inline. The goal is to add a visible thumbnail grid populated by the same fetch.

- [ ] **Step 2: Add the gallery section near the top of the content**

Inside `{% block content %}` near the top (right after the title heading), ADD:

```html
<!-- Spec 8: inline media gallery -->
<div id="pottery-media-grid" class="mb-4">
  <h5><i class="fas fa-images"></i> {{ _('Media') }}</h5>
  <div class="d-flex flex-wrap gap-2" id="pottery-thumbs">
    <span class="text-muted">{{ _('Loading...') }}</span>
  </div>
</div>
```

- [ ] **Step 3: Replace or extend the existing fetch script**

Find the existing `<script>` block that contains `fetch("/api/media/by-entity/pottery/{{ pottery.id_rep }}")`. REPLACE the entire block with:

```html
<script>
fetch("/api/media/by-entity/pottery/{{ pottery.id_rep }}")
  .then(r => r.ok ? r.json() : { items: [] })
  .then(data => {
    const container = document.getElementById('pottery-thumbs');
    const items = data.items || data || [];
    if (!items.length) {
      container.innerHTML = '<p class="text-muted m-0">{{ _("No media") }}</p>';
      return;
    }
    container.innerHTML = items.map(m => `
      <a class="glightbox" data-gallery="pot-detail-{{ pottery.id_rep }}"
         href="${m.url}" data-title="${(m.media_name || m.filename || '').replace(/"/g, '&quot;')}">
        <img src="${m.thumb_url || m.url}" alt=""
             width="120" height="120" loading="lazy"
             style="object-fit:cover;border-radius:4px;border:1px solid var(--border-color)"/>
      </a>
    `).join('');
    if (window.GLightbox) {
      GLightbox({ selector: '#pottery-thumbs .glightbox' });
    }
  })
  .catch(err => {
    document.getElementById('pottery-thumbs').innerHTML =
      '<p class="text-danger m-0">{{ _("Errore caricamento media") }}: ' + err + '</p>';
  });
</script>
```

If the existing script block did more than just media-related work, surgically keep the non-media parts and add the new fetch alongside.

- [ ] **Step 4: Manual smoke**

If pyarchinit-mini-web is running locally on 5001, navigate to `/pottery/<id>` for an id that has media — the thumb grid should appear; click opens the GLightbox.

- [ ] **Step 5: Verify regression**

Run: `.venv/bin/python -m pytest tests/integration/test_pottery_*.py -q --tb=line`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/pottery/detail.html
git commit -m "feat(spec8): pottery detail — inline thumbnail gallery (GLightbox)"
```

---

## Task 9: CHANGELOG + version bump to 2.5.1

**Files:**
- Modify: `pyarchinit_mini/__init__.py`
- Modify: `pyproject.toml`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Bump version in pyproject.toml**

Edit `/Users/enzo/pyarchinit-mini-desk/pyproject.toml` and change:
```
version = "2.5.0"
```
to:
```
version = "2.5.1"
```

- [ ] **Step 2: Bump version in __init__.py**

Edit `/Users/enzo/pyarchinit-mini-desk/pyarchinit_mini/__init__.py` and change:
```
__version__ = "2.5.0"
```
to:
```
__version__ = "2.5.1"
```

- [ ] **Step 3: Prepend `[2.5.1]` section to CHANGELOG.md**

At the TOP of `CHANGELOG.md` (BEFORE the existing `## [2.5.0]` entry), PREPEND:

```markdown
## [2.5.1] - 2026-05-18

### Added (IT)
- Pottery list: anteprima media in linea con mini-carousel CSS scroll-snap
  (thumb 48x48 + GLightbox). N+1 evitato con pre-load batch via
  `MediaService.get_media_for_entity_ids`.
- Pottery filtri: nuovi input `id_number` e `anno` (esatti, integer cast
  con guard `try/except`).
- Pottery detail: galleria thumbnail inline (120x120, GLightbox) sopra i
  campi della scheda.
- Nuovo blueprint `pyarchinit_mini/i18n/lang_routes.py` con
  `POST /set-language/<lang>` che salva session e fa redirect al referrer.
  Lo switcher di lingua diventa `<form>` POST: preserva la query string
  corrente (filtri/ricerca non si perdono più al cambio lingua).

### Changed (IT)
- `templates/components/language_switcher.html`: `<a>` sostituiti con form POST.
- `PotteryService._FILTERABLE_INT` aggiunto con `id_number`, `anno`.
- `pottery_routes.FILTER_KEYS` esteso con `id_number`, `anno`.

### Added (EN)
- Pottery list: inline media preview with CSS scroll-snap mini-carousel
  (48x48 thumbs + GLightbox). Batch pre-load avoids N+1.
- Pottery filters: new `id_number` + `anno` exact-match inputs with
  integer cast guard.
- Pottery detail: inline thumbnail gallery (120x120, GLightbox).
- New `pyarchinit_mini/i18n/lang_routes.py` blueprint: `POST /set-language/<lang>`
  saves session + redirects to referrer, preserving the URL query string
  (filters/search no longer lost on language switch).

### Changed (EN)
- Language switcher templates: anchors replaced with POST forms.
- `PotteryService._FILTERABLE_INT` introduces `id_number`, `anno`.
- `pottery_routes.FILTER_KEYS` extended.

```

- [ ] **Step 4: Run full test suite**

Run: `.venv/bin/python -m pytest tests/ -q --tb=no`
Expected: same baseline failures as before Spec 8 (e.g. pre-existing
`test_delete_site`), no NEW failures. All Spec 8 tests pass.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/__init__.py pyproject.toml CHANGELOG.md
git commit -m "release: bump to 2.5.1 (Spec 8 pottery features)"
```

---

## Task 10: Final regression sweep

**Files:** (no files modified)

- [ ] **Step 1: Run all tests one more time**

Run: `.venv/bin/python -m pytest tests/ -q --tb=short 2>&1 | tail -10`
Expected: pre-existing failures unchanged, all Spec 8 tests pass.

- [ ] **Step 2: Verify URL map**

Run:
```bash
.venv/bin/python -c "
from pyarchinit_mini.web_interface.app import create_app
ret = create_app(); app = ret[0] if isinstance(ret, tuple) else ret
target = ('set-language', 'pottery')
for r in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
    if any(k in r.rule for k in target):
        m = ','.join(sorted(r.methods - {'HEAD','OPTIONS'}))
        print(f'{m:10s} {r.rule}')
"
```
Expected output includes:
- `POST       /set-language/<lang>`
- `GET        /pottery/`
- `GET        /pottery/<int:id_rep>`
(plus the existing pottery routes).

- [ ] **Step 3: Manual smoke checklist**

If you have `pyarchinit-mini-web` running on `localhost:5001`, manually verify:
1. `GET /pottery/?id_number=10` returns only matching pottery.
2. `GET /pottery/?anno=2024` returns only 2024 pottery.
3. Pottery list shows thumbnails for records with media.
4. Pottery detail shows inline thumbnail grid that opens GLightbox.
5. Click `IT`/`EN` switcher buttons preserves filters (URL still shows `?sito=...&id_number=...`).
6. Filtri non-numerici (`/pottery/?id_number=abc`) ritornano lista intera (no SQL error).

No commit needed if all 6 OK.

---

## Self-Review

### Spec coverage

| Spec section | Tasks |
|---|---|
| §3 Architecture | Tasks 1, 2, 7, 8 |
| §4.1 lang_routes blueprint | Task 1 |
| §4.2-4.3 pottery_routes FILTER_KEYS + service | Tasks 4, 5 |
| §4.4-4.5 list.html filter + carousel | Task 7 |
| §4.6 detail.html gallery | Task 8 |
| §4.7 language_switcher.html POST | Task 3 |
| §5 Data flow A | Tasks 5, 6, 7 |
| §5 Data flow B | Task 8 |
| §5 Data flow C | Tasks 1, 2, 3 |
| §6 Error handling (non-numeric input, no referrer, no media) | Tasks 1, 4, 8 |
| §7 Testing | Tasks 1, 4, 6 |
| §8 DoD + bump | Task 9 |

### Placeholder scan

No "TBD", "TODO", "implement later", or "add appropriate error handling"
in plan body — verified.

### Type consistency

- `_FILTERABLE_INT` introduced in Task 4 has same naming convention as
  existing `_FILTERABLE` — consistent.
- `media_by_pottery` dict shape (id → list[dict]) consistent between
  Tasks 6 and 7.
- `lang_bp` and `set_language` view name match between Tasks 1, 2, and 3
  (the `url_for('lang.set_language', ...)` in language_switcher.html).
- `csrf.exempt(lang_bp)` in Task 2 matches the import in Task 1.

Plan complete. Ready for implementation.
