# PyArchInit-Mini Web ↔ s3dgraphy Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make pyarchinit-mini-web consume s3dgraphy JSON catalogues as the canonical source of unit types, edge types, and visual styles. Align existing data with EM 1.5.4 vocabulary (`USVA/USVB → USVs`, `USVC → USVn`). Introduce `node_uuid` column required by future sync. Retire hardcoded mappings in `em_palette.py` and `s3d_converter.py`.

**Architecture:** New `pyarchinit_mini/vocab/` package with thread-safe `VocabProvider` singleton reading three s3dgraphy JSON pillars via `importlib.resources`. New Flask blueprint `/api/v1/vocab/*` exposes vocab to the browser. Migration CLI `pyarchinit-mini-migrate-vocab` handles vocab alignment + `node_uuid` UUID v7 backfill on three tables. 8 PRs sequenced as 21 tasks below; parity test on Harris matrix output gates PR3.

**Tech Stack:** Python 3.13, Flask, SQLAlchemy, pytest, freezegun, s3dgraphy 0.1.42+, uuid7

**Spec:** `docs/superpowers/specs/2026-05-16-s3dgraphy-web-foundation-design.md`

---

## File Structure

### New files

| Path | Responsibility |
|---|---|
| `pyarchinit_mini/vocab/__init__.py` | Package facade — re-exports `VocabProvider`, types, exceptions |
| `pyarchinit_mini/vocab/exceptions.py` | `VocabBootstrapError`, `VocabSchemaError`, `VocabUnavailableError` |
| `pyarchinit_mini/vocab/types.py` | `UnitType`, `EdgeType`, `VisualStyle` dataclasses (`@dataclass(frozen=True)`) |
| `pyarchinit_mini/vocab/loader.py` | Read s3dgraphy JSON pillars; handle filename quirks |
| `pyarchinit_mini/vocab/i18n.py` | Custom JSON translation catalogue (separate from flask_babel) |
| `pyarchinit_mini/vocab/provider.py` | Thread-safe `VocabProvider` singleton |
| `pyarchinit_mini/vocab/translations/vocab_en.json` | English vocab labels/descriptions |
| `pyarchinit_mini/vocab/translations/vocab_it.json` | Italian vocab labels/descriptions |
| `pyarchinit_mini/web_interface/vocab_routes.py` | Flask blueprint `/api/v1/vocab/*` |
| `pyarchinit_mini/database/utils.py` | `generate_node_uuid()` helper (UUID v7) |
| `pyarchinit_mini/database/migrations/__init__.py` | Migration package init |
| `pyarchinit_mini/database/migrations/backup.py` | `BackupRecord`, `backup_database()` |
| `pyarchinit_mini/database/migrations/2026_05_node_uuid_schema.py` | `ALTER TABLE ... ADD COLUMN node_uuid` on 3 tables |
| `pyarchinit_mini/database/migrations/2026_05_node_uuid_backfill.py` | `UPDATE ... SET node_uuid = uuid7()` batched |
| `pyarchinit_mini/database/migrations/2026_05_vocab_alignment.py` | USVA/USVB → USVs; USVC → USVn |
| `pyarchinit_mini/database/migrations/2026_05_paradata_bootstrap.py` | Creates `data/paradata/` placeholder |
| `pyarchinit_mini/cli/migrate_vocab.py` | CLI `pyarchinit-mini-migrate-vocab` entry point |
| `tests/unit/test_vocab_exceptions.py` | Exception classes |
| `tests/unit/test_vocab_types.py` | Dataclasses + `VisualStyle.fallback()` |
| `tests/unit/test_vocab_loader.py` | JSON loading with quirks/legacy/malformed |
| `tests/unit/test_vocab_i18n.py` | Translation fallback + missing tracking |
| `tests/unit/test_vocab_provider.py` | Singleton thread-safety + cached lookups |
| `tests/unit/test_em_palette_vocab_backed.py` | em_palette now sources from VocabProvider |
| `tests/unit/test_s3d_converter_vocab_backed.py` | s3d_converter sources from VocabProvider |
| `tests/unit/test_us_dto_unita_tipo_validator.py` | DTO validator |
| `tests/unit/test_database_utils.py` | `generate_node_uuid` returns valid UUID v7 |
| `tests/unit/test_migrations_backup.py` | SQLite backup + checksum |
| `tests/unit/test_migrations_idempotent.py` | Each migration script idempotent + reversible |
| `tests/integration/test_vocab_routes.py` | Flask endpoints |
| `tests/integration/test_migrate_vocab_cli.py` | CLI dry-run/apply/rollback |
| `tests/integration/test_harris_matrix_visual_parity.py` | Harris matrix parity gate (PR3) |
| `tests/integration/test_us_dto_legacy_acceptance.py` | Legacy USVA accepted with warning |
| `tests/e2e/test_web_vocab_full_flow.py` | End-to-end: form load → save → matrix render |
| `tests/fixtures/s3dgraphy_jsons/0.1.42/{s3Dgraphy_node_datamodel.json, s3Dgraphy_connections_datamodel.json, em_visual_rules.json}` | Real JSONs from s3dgraphy 0.1.42 (copied verbatim) |
| `tests/fixtures/s3dgraphy_jsons/0.1.15/{*}` | Legacy JSONs from 0.1.15 (with filename quirk) |
| `tests/fixtures/s3dgraphy_jsons/malformed/s3Dgraphy_node_datamodel.json` | JSON broken at line 42 |
| `tests/fixtures/databases/sqlite_pre_migration.db` | Synthetic 30 US dataset with mix of USVA/USVB/USVC + standard |
| `tests/fixtures/databases/sqlite_fully_migrated.db` | All 3 migrations applied |
| `tests/fixtures/graphml_outputs/synthetic_baseline_em_palette.graphml` | Pre-PR3 baseline output |
| `tests/fixtures/graphml_outputs/synthetic_target_vocab.graphml` | Post-PR3 expected output |

### Modified files

| Path | Change |
|---|---|
| `pyproject.toml` | Bump `s3dgraphy>=0.1.42`; add `uuid7>=0.1.0`; add `freezegun` to dev deps; declare `pyarchinit-mini-migrate-vocab` console script |
| `pyarchinit_mini/__init__.py` | Bump version `2.1.68 → 2.2.0-alpha` |
| `pyarchinit_mini/graphml_converter/em_palette.py` | Refactor `EMPalette.get_style()` to read from `VocabProvider`; `PALETTE` dict → property with deprecation warning |
| `pyarchinit_mini/s3d_integration/s3d_converter.py` | Delete hardcoded `relationship_mapping` + `unit_type` categorization; replace with VocabProvider lookups |
| `pyarchinit_mini/dto/us_dto.py` | Add validator on `unita_tipo` against VocabProvider; accept legacy with warning |
| `pyarchinit_mini/web_interface/app.py` | Register `vocab_bp` blueprint |
| `pyarchinit_mini/web_interface/harris_creator_routes.py` | Replace hardcoded `'US'` fallbacks with `VocabProvider.get_unit_type("US")` |
| `pyarchinit_mini/web_interface/excel_import_routes.py` | Validate `unita_tipo` on import |
| `pyarchinit_mini/web_interface/three_d_builder_routes.py` | Lookup via VocabProvider |
| `pyarchinit_mini/web_interface/templates/us_form.html` (and similar) | Form `<select>` populated via JS fetch from `/api/v1/vocab/unit-types` |
| `CHANGELOG.md` | Bilingual entry IT/EN for 2.2.0-alpha |
| `README.md` | New "s3dgraphy integration" section |
| `docs/CLI_MIGRATE_VOCAB.md` (new) | Documentation for `pyarchinit-mini-migrate-vocab` |

---

## PR1 — VocabProvider Module Foundation

### Task 1: Create vocab package skeleton + exceptions

**Files:**
- Create: `pyarchinit_mini/vocab/__init__.py`
- Create: `pyarchinit_mini/vocab/exceptions.py`
- Test: `tests/unit/test_vocab_exceptions.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_vocab_exceptions.py
import pytest
from pyarchinit_mini.vocab.exceptions import (
    VocabBootstrapError,
    VocabSchemaError,
    VocabUnavailableError,
)


def test_bootstrap_error_includes_actionable_hint():
    err = VocabBootstrapError("missing pillar X", hint="pip install s3dgraphy>=0.1.42")
    assert "missing pillar X" in str(err)
    assert err.hint == "pip install s3dgraphy>=0.1.42"


def test_schema_error_records_location():
    err = VocabSchemaError(path="/tmp/foo.json", line=42, column=7, msg="invalid token")
    assert err.path == "/tmp/foo.json"
    assert err.line == 42
    assert err.column == 7
    assert "line 42, column 7" in str(err)


def test_unavailable_error_carries_reason():
    err = VocabUnavailableError(reason="strict mode disabled")
    assert err.reason == "strict mode disabled"
```

- [ ] **Step 2: Run test, verify it fails**

Run: `.venv/bin/pytest tests/unit/test_vocab_exceptions.py -v`
Expected: ImportError on `pyarchinit_mini.vocab.exceptions`.

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/vocab/__init__.py
"""Vocab module — s3dgraphy JSON catalogue consumer."""
```

```python
# pyarchinit_mini/vocab/exceptions.py
class VocabError(Exception):
    """Base for vocab errors."""


class VocabBootstrapError(VocabError):
    def __init__(self, msg: str, *, hint: str | None = None) -> None:
        super().__init__(msg)
        self.hint = hint


class VocabSchemaError(VocabError):
    def __init__(self, *, path: str, line: int, column: int, msg: str) -> None:
        super().__init__(f"{msg} at {path} line {line}, column {column}")
        self.path = path
        self.line = line
        self.column = column


class VocabUnavailableError(VocabError):
    def __init__(self, *, reason: str) -> None:
        super().__init__(f"vocab unavailable: {reason}")
        self.reason = reason
```

- [ ] **Step 4: Run test, verify pass**

Run: `.venv/bin/pytest tests/unit/test_vocab_exceptions.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/vocab/__init__.py pyarchinit_mini/vocab/exceptions.py tests/unit/test_vocab_exceptions.py
git commit -m "feat(vocab): add exception hierarchy"
```

---

### Task 2: Implement vocab types (dataclasses)

**Files:**
- Create: `pyarchinit_mini/vocab/types.py`
- Test: `tests/unit/test_vocab_types.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_vocab_types.py
import pytest
from pyarchinit_mini.vocab.types import UnitType, EdgeType, VisualStyle


def test_visual_style_fallback_is_neutral_rectangle():
    fb = VisualStyle.fallback()
    assert fb.shape == "rectangle"
    assert fb.fill_color == "#CCCCCC"
    assert fb.border_color == "#000000"


def test_dataclasses_are_frozen():
    style = VisualStyle(shape="rectangle", fill_color="#fff", border_color="#000", border_style="solid")
    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        style.shape = "hexagon"


def test_unit_type_carries_visual_style():
    style = VisualStyle(shape="parallelogram", fill_color="#FFF", border_color="#000", border_style="solid")
    ut = UnitType(
        abbreviation="USVs",
        class_name="StructuralVirtualStratigraphicUnit",
        parent="StratigraphicNode",
        label="USV/s",
        description="...",
        symbol="black parallelogram",
        family="virtual",
        is_series=False,
        cidoc_mapping="A2 Stratigraphic Volume Unit",
        properties={"name": "P1_is_identified_by"},
        visual_style=style,
    )
    assert ut.visual_style.shape == "parallelogram"
    assert ut.family == "virtual"


def test_edge_type_legal_pairs_is_immutable():
    e = EdgeType(
        name="covers",
        label="copre",
        italian_aliases=("copre", "coperto da"),
        symmetric=False,
        legal_pairs=(("US", "US"), ("US", "USM")),
    )
    assert ("US", "USM") in e.legal_pairs
```

- [ ] **Step 2: Run test, verify it fails**

Run: `.venv/bin/pytest tests/unit/test_vocab_types.py -v`
Expected: ImportError.

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/vocab/types.py
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class VisualStyle:
    shape: str
    fill_color: str
    border_color: str
    border_style: str
    border_width: float = 3.0
    text_color: str = "#000000"
    font_family: str = "DialogInput"
    font_size: int = 24
    font_style: str = "bold"
    label_position: str = "over"
    file_2d_raster: Optional[str] = None
    file_2d_vector: Optional[str] = None
    file_3d: Optional[str] = None
    material_rgba: Optional[tuple] = None

    @classmethod
    def fallback(cls) -> "VisualStyle":
        return cls(
            shape="rectangle",
            fill_color="#CCCCCC",
            border_color="#000000",
            border_style="solid",
        )


@dataclass(frozen=True)
class UnitType:
    abbreviation: str
    class_name: str
    parent: Optional[str]
    label: str
    description: str
    symbol: str
    family: Optional[str]
    is_series: bool
    cidoc_mapping: Optional[str]
    properties: dict
    visual_style: VisualStyle


@dataclass(frozen=True)
class EdgeType:
    name: str
    label: str
    italian_aliases: tuple
    symmetric: bool
    legal_pairs: tuple
```

- [ ] **Step 4: Run test, verify pass**

Run: `.venv/bin/pytest tests/unit/test_vocab_types.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/vocab/types.py tests/unit/test_vocab_types.py
git commit -m "feat(vocab): add UnitType, EdgeType, VisualStyle dataclasses"
```

---

### Task 3: Copy real s3dgraphy JSONs as test fixtures

**Files:**
- Create: `tests/fixtures/s3dgraphy_jsons/0.1.42/s3Dgraphy_node_datamodel.json`
- Create: `tests/fixtures/s3dgraphy_jsons/0.1.42/s3Dgraphy_connections_datamodel.json`
- Create: `tests/fixtures/s3dgraphy_jsons/0.1.42/em_visual_rules.json`
- Create: `tests/fixtures/s3dgraphy_jsons/0.1.15/s3Dgraphy_node_datamodel .json` (with literal space)
- Create: `tests/fixtures/s3dgraphy_jsons/0.1.15/em_connection_rules.json`
- Create: `tests/fixtures/s3dgraphy_jsons/0.1.15/em_visual_rules.json`
- Create: `tests/fixtures/s3dgraphy_jsons/malformed/s3Dgraphy_node_datamodel.json`

- [ ] **Step 1: Copy 0.1.42 JSONs from QGIS plugin bundle**

```bash
mkdir -p tests/fixtures/s3dgraphy_jsons/0.1.42
cp "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/ext_libs/s3dgraphy/JSON_config/s3Dgraphy_node_datamodel.json" tests/fixtures/s3dgraphy_jsons/0.1.42/
cp "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/ext_libs/s3dgraphy/JSON_config/s3Dgraphy_connections_datamodel.json" tests/fixtures/s3dgraphy_jsons/0.1.42/
cp "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/ext_libs/s3dgraphy/JSON_config/em_visual_rules.json" tests/fixtures/s3dgraphy_jsons/0.1.42/
```

- [ ] **Step 2: Copy 0.1.15 JSONs from venv (preserving the filename quirk with space)**

```bash
mkdir -p tests/fixtures/s3dgraphy_jsons/0.1.15
cp "/Users/enzo/pyarchinit-mini-desk/.venv/lib/python3.13/site-packages/s3dgraphy/JSON_config/s3Dgraphy_node_datamodel .json" tests/fixtures/s3dgraphy_jsons/0.1.15/
cp /Users/enzo/pyarchinit-mini-desk/.venv/lib/python3.13/site-packages/s3dgraphy/JSON_config/em_connection_rules.json tests/fixtures/s3dgraphy_jsons/0.1.15/
cp /Users/enzo/pyarchinit-mini-desk/.venv/lib/python3.13/site-packages/s3dgraphy/JSON_config/em_visual_rules.json tests/fixtures/s3dgraphy_jsons/0.1.15/
```

- [ ] **Step 3: Create a malformed JSON for testing parse errors**

```bash
mkdir -p tests/fixtures/s3dgraphy_jsons/malformed
```

```json
// tests/fixtures/s3dgraphy_jsons/malformed/s3Dgraphy_node_datamodel.json
{
  "s3Dgraphy_data_model_version": "1.5.4",
  "node_types": {
    "Node": {
      "class": "Node",
      "description": "Broken JSON on next line"
      missing_comma_above
    }
  }
}
```

- [ ] **Step 4: Verify fixtures load with stdlib json (sanity check)**

```bash
.venv/bin/python -c "import json; json.load(open('tests/fixtures/s3dgraphy_jsons/0.1.42/s3Dgraphy_node_datamodel.json'))"
.venv/bin/python -c "import json; json.load(open('tests/fixtures/s3dgraphy_jsons/0.1.42/em_visual_rules.json'))"
```

Expected: no output (both parse OK). The malformed one will fail when loader hits it — that's intentional.

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/s3dgraphy_jsons/
git commit -m "test(vocab): add s3dgraphy JSON fixtures (0.1.42, 0.1.15 with quirks, malformed)"
```

---

### Task 4: Implement vocab loader

**Files:**
- Create: `pyarchinit_mini/vocab/loader.py`
- Test: `tests/unit/test_vocab_loader.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_vocab_loader.py
from pathlib import Path
import pytest
from pyarchinit_mini.vocab.loader import (
    load_node_datamodel,
    load_connections_datamodel,
    load_visual_rules,
)
from pyarchinit_mini.vocab.exceptions import VocabBootstrapError, VocabSchemaError

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons"


def test_load_node_datamodel_from_0_1_42(monkeypatch):
    data = load_node_datamodel(json_config_dir=FIX / "0.1.42")
    assert data.version == "1.5.4"
    assert "US" in data.stratigraphic_subtypes
    assert "USVs" in data.stratigraphic_subtypes


def test_load_visual_rules_from_0_1_42():
    data = load_visual_rules(json_config_dir=FIX / "0.1.42")
    assert "US" in data.node_styles
    assert data.node_styles["US"]["style"]["shape"] == "rectangle"


def test_load_connections_datamodel_from_0_1_42():
    data = load_connections_datamodel(json_config_dir=FIX / "0.1.42")
    assert "is_after" in data.edge_types or "is_before" in data.edge_types


def test_load_handles_filename_quirk_with_space():
    # 0.1.15 ships node datamodel with a literal space in the filename
    data = load_node_datamodel(json_config_dir=FIX / "0.1.15")
    assert data.version  # parsed something


def test_load_handles_legacy_connections_naming():
    # 0.1.15 uses em_connection_rules.json (not the new s3Dgraphy_connections_datamodel.json)
    data = load_connections_datamodel(json_config_dir=FIX / "0.1.15", allow_legacy=True)
    assert data is not None


def test_load_legacy_without_allow_legacy_raises():
    with pytest.raises(VocabBootstrapError) as exc_info:
        load_connections_datamodel(json_config_dir=FIX / "0.1.15", allow_legacy=False)
    assert "s3dgraphy" in str(exc_info.value).lower() or "upgrade" in str(exc_info.value).lower()


def test_load_malformed_raises_schema_error():
    with pytest.raises(VocabSchemaError):
        load_node_datamodel(json_config_dir=FIX / "malformed")


def test_load_missing_dir_raises_bootstrap_error():
    with pytest.raises(VocabBootstrapError):
        load_node_datamodel(json_config_dir=Path("/nonexistent/path"))
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `.venv/bin/pytest tests/unit/test_vocab_loader.py -v`
Expected: 8 errors (module missing).

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/vocab/loader.py
import json
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Optional

from .exceptions import VocabBootstrapError, VocabSchemaError


@dataclass
class NodeDatamodel:
    version: str
    raw: dict
    stratigraphic_subtypes: dict = field(default_factory=dict)


@dataclass
class ConnectionsDatamodel:
    version: str
    raw: dict
    edge_types: dict = field(default_factory=dict)


@dataclass
class VisualRulesDatamodel:
    version: str
    raw: dict
    node_styles: dict = field(default_factory=dict)


def _default_dir() -> Path:
    """Locate s3dgraphy JSON_config via importlib.resources."""
    try:
        with resources.as_file(resources.files("s3dgraphy") / "JSON_config") as p:
            return Path(p)
    except (ModuleNotFoundError, FileNotFoundError) as e:
        raise VocabBootstrapError(
            "s3dgraphy is not installed",
            hint="pip install s3dgraphy>=0.1.42",
        ) from e


def _load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise VocabSchemaError(path=str(path), line=e.lineno, column=e.colno, msg=e.msg) from e


def _resolve_node_datamodel_file(d: Path) -> Path:
    for name in ("s3Dgraphy_node_datamodel.json", "s3Dgraphy_node_datamodel .json"):
        p = d / name
        if p.exists():
            return p
    raise VocabBootstrapError(
        f"s3Dgraphy_node_datamodel.json not found in {d}",
        hint="upgrade s3dgraphy: pip install --upgrade s3dgraphy>=0.1.42",
    )


def _resolve_connections_file(d: Path, *, allow_legacy: bool) -> Path:
    canonical = d / "s3Dgraphy_connections_datamodel.json"
    if canonical.exists():
        return canonical
    legacy = d / "em_connection_rules.json"
    if legacy.exists():
        if not allow_legacy:
            raise VocabBootstrapError(
                f"Only legacy {legacy.name} found (s3dgraphy version too old)",
                hint="upgrade: pip install --upgrade s3dgraphy>=0.1.42",
            )
        return legacy
    raise VocabBootstrapError(
        "no connections datamodel file found",
        hint="upgrade s3dgraphy",
    )


def load_node_datamodel(*, json_config_dir: Path | None = None) -> NodeDatamodel:
    d = Path(json_config_dir) if json_config_dir else _default_dir()
    if not d.exists():
        raise VocabBootstrapError(f"JSON_config directory not found: {d}")
    path = _resolve_node_datamodel_file(d)
    raw = _load_json(path)
    subtypes = {}
    strat = raw.get("stratigraphic_nodes", {}).get("StratigraphicNode", {})
    subtypes.update(strat.get("subtypes", {}))
    return NodeDatamodel(
        version=raw.get("s3Dgraphy_data_model_version", "unknown"),
        raw=raw,
        stratigraphic_subtypes=subtypes,
    )


def load_connections_datamodel(*, json_config_dir: Path | None = None, allow_legacy: bool = False) -> ConnectionsDatamodel:
    d = Path(json_config_dir) if json_config_dir else _default_dir()
    if not d.exists():
        raise VocabBootstrapError(f"JSON_config directory not found: {d}")
    path = _resolve_connections_file(d, allow_legacy=allow_legacy)
    raw = _load_json(path)
    edge_types = raw.get("edge_types") or raw.get("connection_types") or {}
    return ConnectionsDatamodel(
        version=raw.get("version", "unknown"),
        raw=raw,
        edge_types=edge_types,
    )


def load_visual_rules(*, json_config_dir: Path | None = None) -> VisualRulesDatamodel:
    d = Path(json_config_dir) if json_config_dir else _default_dir()
    if not d.exists():
        raise VocabBootstrapError(f"JSON_config directory not found: {d}")
    path = d / "em_visual_rules.json"
    if not path.exists():
        raise VocabBootstrapError(f"em_visual_rules.json not found in {d}")
    raw = _load_json(path)
    return VisualRulesDatamodel(
        version=raw.get("version", "unknown"),
        raw=raw,
        node_styles=raw.get("node_styles", {}),
    )
```

- [ ] **Step 4: Run tests, verify all pass**

Run: `.venv/bin/pytest tests/unit/test_vocab_loader.py -v`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/vocab/loader.py tests/unit/test_vocab_loader.py
git commit -m "feat(vocab): add JSON pillar loader with filename quirk + legacy fallback"
```

---

### Task 5: Implement i18n translation layer

**Files:**
- Create: `pyarchinit_mini/vocab/i18n.py`
- Create: `pyarchinit_mini/vocab/translations/vocab_en.json`
- Create: `pyarchinit_mini/vocab/translations/vocab_it.json`
- Test: `tests/unit/test_vocab_i18n.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_vocab_i18n.py
from pathlib import Path
from pyarchinit_mini.vocab.i18n import VocabI18n


def test_lookup_returns_translated_label_in_italian():
    i18n = VocabI18n(translations_dir=Path("pyarchinit_mini/vocab/translations"))
    label = i18n.unit_type_label("US", lang="it")
    assert label  # non-empty
    assert isinstance(label, str)


def test_lookup_falls_back_to_english_when_lang_missing():
    i18n = VocabI18n(translations_dir=Path("pyarchinit_mini/vocab/translations"))
    label = i18n.unit_type_label("US", lang="xx")  # nonexistent
    assert label  # English fallback


def test_lookup_returns_abbreviation_when_no_translation_anywhere():
    i18n = VocabI18n(translations_dir=Path("pyarchinit_mini/vocab/translations"))
    label = i18n.unit_type_label("ZZZ_NEW_NEVER_SEEN", lang="it")
    assert label == "ZZZ_NEW_NEVER_SEEN"
    assert "it:ZZZ_NEW_NEVER_SEEN" in i18n.missing_translations


def test_edge_type_label_translation():
    i18n = VocabI18n(translations_dir=Path("pyarchinit_mini/vocab/translations"))
    label = i18n.edge_type_label("covers", lang="it")
    assert label == "copre"


def test_edge_aliases_returns_italian_variants_for_parsing():
    i18n = VocabI18n(translations_dir=Path("pyarchinit_mini/vocab/translations"))
    aliases = i18n.edge_aliases("is_after", lang="it")
    assert "coperto da" in aliases
    assert "tagliato da" in aliases


def test_edge_aliases_missing_returns_empty_tuple():
    i18n = VocabI18n(translations_dir=Path("pyarchinit_mini/vocab/translations"))
    aliases = i18n.edge_aliases("nonexistent_edge", lang="it")
    assert aliases == ()
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `.venv/bin/pytest tests/unit/test_vocab_i18n.py -v`
Expected: import error.

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/vocab/translations/vocab_en.json
{
  "unit_types": {
    "US": {"label": "US", "description": "Stratigraphic Unit"},
    "USVs": {"label": "USV/s", "description": "Structural Virtual Stratigraphic Unit"},
    "USVn": {"label": "USV/n", "description": "Non-structural Virtual Stratigraphic Unit"},
    "SF": {"label": "SF", "description": "Special Find"},
    "VSF": {"label": "VSF", "description": "Virtual Special Find"},
    "USM": {"label": "USM", "description": "Stratigraphic Unit Masonry"},
    "USD": {"label": "USD", "description": "Documentary Stratigraphic Unit"},
    "RSF": {"label": "RSF", "description": "Reused Special Find (spolia)"}
  },
  "edge_types": {
    "covers": {"label": "covers"},
    "cuts": {"label": "cuts"},
    "fills": {"label": "fills"},
    "is_after": {"label": "is after"},
    "has_same_time": {"label": "has same time"},
    "leans_against": {"label": "leans against"}
  }
}
```

```python
# pyarchinit_mini/vocab/translations/vocab_it.json
{
  "unit_types": {
    "US": {"label": "US", "description": "Unità Stratigrafica"},
    "USVs": {"label": "USV/s", "description": "Unità Stratigrafica Virtuale strutturale"},
    "USVn": {"label": "USV/n", "description": "Unità Stratigrafica Virtuale non strutturale"},
    "SF": {"label": "SF", "description": "Reperto Speciale"},
    "VSF": {"label": "VSF", "description": "Reperto Speciale Virtuale"},
    "USM": {"label": "USM", "description": "Unità Stratigrafica Muraria"},
    "USD": {"label": "USD", "description": "Unità Stratigrafica Documentaria"},
    "RSF": {"label": "RSF", "description": "Spoglio (Reperto Reimpiegato)"}
  },
  "edge_types": {
    "covers": {"label": "copre"},
    "cuts": {"label": "taglia"},
    "fills": {"label": "riempie"},
    "is_after": {"label": "è dopo"},
    "has_same_time": {"label": "uguale a"},
    "leans_against": {"label": "si appoggia a"}
  },
  "edge_type_aliases": {
    "covers": ["copre"],
    "is_after": ["coperto da", "coperta da", "tagliato da", "tagliata da"],
    "cuts": ["taglia"],
    "fills": ["riempie"],
    "leans_against": ["si appoggia a", "si appoggia"],
    "has_same_time": ["uguale a"]
  }
}
```

Note: `edge_type_aliases` is the IT-specific source for parsing PyArchInit
free-form `rapporti` strings (per spec §4.2). The s3dgraphy JSON pillars do
NOT carry this — it lives here in the i18n catalogue because it is
locale-specific.

```python
# pyarchinit_mini/vocab/i18n.py
import json
from pathlib import Path


class VocabI18n:
    def __init__(self, *, translations_dir: Path) -> None:
        self._dir = Path(translations_dir)
        self._catalogues: dict[str, dict] = {}
        self.missing_translations: set[str] = set()

    def _load(self, lang: str) -> dict:
        if lang in self._catalogues:
            return self._catalogues[lang]
        path = self._dir / f"vocab_{lang}.json"
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self._catalogues[lang] = data
        return data

    def unit_type_label(self, abbreviation: str, lang: str = "en") -> str:
        cat = self._load(lang)
        try:
            return cat["unit_types"][abbreviation]["label"]
        except KeyError:
            pass
        if lang != "en":
            self.missing_translations.add(f"{lang}:{abbreviation}")
            en = self._load("en")
            try:
                return en["unit_types"][abbreviation]["label"]
            except KeyError:
                pass
        return abbreviation

    def unit_type_description(self, abbreviation: str, lang: str = "en") -> str:
        cat = self._load(lang)
        try:
            return cat["unit_types"][abbreviation]["description"]
        except KeyError:
            pass
        if lang != "en":
            en = self._load("en")
            try:
                return en["unit_types"][abbreviation]["description"]
            except KeyError:
                pass
        return ""

    def edge_type_label(self, name: str, lang: str = "en") -> str:
        cat = self._load(lang)
        try:
            return cat["edge_types"][name]["label"]
        except KeyError:
            pass
        if lang != "en":
            self.missing_translations.add(f"{lang}:{name}")
            en = self._load("en")
            try:
                return en["edge_types"][name]["label"]
            except KeyError:
                pass
        return name

    def edge_aliases(self, name: str, lang: str = "it") -> tuple:
        """Return free-form aliases for an edge type in a given language.

        Used by s3d_converter to parse PyArchInit `rapporti` text fields.
        Lives in i18n (not in loader) because aliases are locale-specific
        and NOT present in s3dgraphy JSON pillars.
        """
        cat = self._load(lang)
        aliases = cat.get("edge_type_aliases", {}).get(name, [])
        return tuple(aliases)
```

- [ ] **Step 4: Run tests, verify pass**

Run: `.venv/bin/pytest tests/unit/test_vocab_i18n.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/vocab/i18n.py pyarchinit_mini/vocab/translations/ tests/unit/test_vocab_i18n.py
git commit -m "feat(vocab): add i18n catalogue layer with EN/IT translations"
```

---

### Task 6: Implement VocabProvider singleton

**Files:**
- Create: `pyarchinit_mini/vocab/provider.py`
- Modify: `pyarchinit_mini/vocab/__init__.py` (re-export)
- Test: `tests/unit/test_vocab_provider.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_vocab_provider.py
from pathlib import Path
import threading
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.vocab.types import UnitType, VisualStyle

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def reset_provider():
    VocabProvider.reset()
    yield
    VocabProvider.reset()


def _instance():
    return VocabProvider.instance(json_config_dir=FIX)


def test_singleton_returns_same_object_on_concurrent_first_access():
    instances = []

    def grab():
        instances.append(_instance())

    threads = [threading.Thread(target=grab) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    first = instances[0]
    for inst in instances:
        assert inst is first


def test_get_unit_types_returns_known_subtypes():
    p = _instance()
    types = p.get_unit_types(lang="en")
    abbrs = {t.abbreviation for t in types}
    assert "US" in abbrs
    assert "USVs" in abbrs


def test_get_unit_type_returns_localized_label():
    p = _instance()
    us_it = p.get_unit_type("US", lang="it")
    assert us_it is not None
    assert "Unità" in us_it.description or "Stratigrafica" in us_it.description


def test_get_unit_type_unknown_returns_none():
    p = _instance()
    assert p.get_unit_type("ZZZ_UNKNOWN") is None


def test_get_visual_style_returns_fallback_for_unknown_type():
    p = _instance()
    style = p.get_visual_style("ZZZ_UNKNOWN")
    assert style == VisualStyle.fallback()


def test_get_visual_style_returns_real_style_for_us():
    p = _instance()
    style = p.get_visual_style("US")
    assert style.shape == "rectangle"
    assert style.fill_color == "#F0F0F0"


def test_diagnostics_includes_versions_and_counts():
    p = _instance()
    d = p.diagnostics()
    assert "data_model_versions" in d
    assert "counts" in d
    assert d["counts"]["unit_types"] > 0
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `.venv/bin/pytest tests/unit/test_vocab_provider.py -v`
Expected: import errors.

- [ ] **Step 3: Write minimal implementation**

```python
# pyarchinit_mini/vocab/provider.py
import threading
from pathlib import Path
from typing import Any, Optional

from .i18n import VocabI18n
from .loader import load_connections_datamodel, load_node_datamodel, load_visual_rules
from .types import EdgeType, UnitType, VisualStyle


def _build_visual_style(entry: dict) -> VisualStyle:
    style = entry.get("style", {})
    mat = style.get("material", {}).get("color")
    rgba = (mat["r"], mat["g"], mat["b"], mat.get("a", 1.0)) if mat else None
    return VisualStyle(
        shape=style.get("shape", "rectangle"),
        fill_color=style.get("fill_color", "#FFFFFF"),
        border_color=style.get("border_color", "#000000"),
        border_style=style.get("border_style", "solid"),
        file_2d_raster=entry.get("file_2d") or entry.get("2d_file_rast"),
        file_2d_vector=entry.get("2d_file_vect"),
        file_3d=entry.get("file_3d") or entry.get("3d_file"),
        material_rgba=rgba,
        label_position=entry.get("label_position", "over"),
    )


class VocabProvider:
    _instance: Optional["VocabProvider"] = None
    _lock = threading.Lock()

    def __init__(self, *, json_config_dir: Optional[Path] = None,
                 translations_dir: Optional[Path] = None) -> None:
        self._node = load_node_datamodel(json_config_dir=json_config_dir)
        self._conn = load_connections_datamodel(
            json_config_dir=json_config_dir,
            allow_legacy=True,  # Spec §4.3: fall back to legacy with warning
        )
        self._visual = load_visual_rules(json_config_dir=json_config_dir)
        self._i18n = VocabI18n(
            translations_dir=translations_dir
            or Path(__file__).parent / "translations"
        )
        # Build cached UnitType objects (lang-neutral; labels resolved on request)
        self._unit_types_raw: dict[str, dict] = self._node.stratigraphic_subtypes
        self._visual_by_type: dict[str, VisualStyle] = {
            abbr: _build_visual_style(entry) for abbr, entry in self._visual.node_styles.items()
        }

    @classmethod
    def instance(cls, **kwargs) -> "VocabProvider":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(**kwargs)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._instance = None

    def _build_unit_type(self, abbr: str, raw: dict, lang: str) -> UnitType:
        return UnitType(
            abbreviation=abbr,
            class_name=raw.get("class", "Node"),
            parent=raw.get("parent"),
            label=self._i18n.unit_type_label(abbr, lang=lang),
            description=self._i18n.unit_type_description(abbr, lang=lang) or raw.get("description", ""),
            symbol=raw.get("symbol", ""),
            family=raw.get("family"),
            is_series=bool(raw.get("is_series", False)),
            cidoc_mapping=raw.get("mapping", {}).get("cidoc"),
            properties=raw.get("properties", {}),
            visual_style=self.get_visual_style(abbr),
        )

    def get_unit_types(self, lang: str = "en") -> list[UnitType]:
        return [self._build_unit_type(a, r, lang) for a, r in self._unit_types_raw.items()]

    def get_unit_type(self, abbreviation: str, lang: str = "en") -> Optional[UnitType]:
        raw = self._unit_types_raw.get(abbreviation)
        if raw is None:
            return None
        return self._build_unit_type(abbreviation, raw, lang)

    def get_edge_types(self, lang: str = "en") -> list[EdgeType]:
        out = []
        for name, raw in self._conn.edge_types.items():
            out.append(EdgeType(
                name=name,
                label=self._i18n.edge_type_label(name, lang=lang),
                # Italian aliases live in i18n catalogue, NOT in s3dgraphy JSON pillars
                italian_aliases=self._i18n.edge_aliases(name, lang="it"),
                symmetric=bool(raw.get("symmetric", False)),
                legal_pairs=tuple(tuple(p) for p in raw.get("legal_pairs", ())),
            ))
        return out

    def get_legal_edges(self, source_type: str, target_type: str) -> list[EdgeType]:
        all_edges = self.get_edge_types()
        return [e for e in all_edges if (source_type, target_type) in e.legal_pairs]

    def get_visual_style(self, unit_type: str) -> VisualStyle:
        return self._visual_by_type.get(unit_type, VisualStyle.fallback())

    def get_cidoc_mapping(self, unit_type: str) -> Optional[str]:
        ut = self.get_unit_type(unit_type)
        return ut.cidoc_mapping if ut else None

    def s3dgraphy_version(self) -> str:
        try:
            import s3dgraphy
            return getattr(s3dgraphy, "__version__", "unknown")
        except ImportError:
            return "not installed"

    def data_model_versions(self) -> dict[str, str]:
        return {
            "node": self._node.version,
            "connections": self._conn.version,
            "visual": self._visual.version,
        }

    def diagnostics(self) -> dict[str, Any]:
        return {
            "s3dgraphy_version": self.s3dgraphy_version(),
            "data_model_versions": self.data_model_versions(),
            "counts": {
                "unit_types": len(self._unit_types_raw),
                "edge_types": len(self._conn.edge_types),
                "visual_styles": len(self._visual_by_type),
            },
            "missing_translations": sorted(self._i18n.missing_translations),
        }
```

```python
# pyarchinit_mini/vocab/__init__.py
"""Vocab module — s3dgraphy JSON catalogue consumer."""
from .exceptions import VocabBootstrapError, VocabSchemaError, VocabUnavailableError
from .provider import VocabProvider
from .types import EdgeType, UnitType, VisualStyle

__all__ = [
    "VocabProvider",
    "UnitType",
    "EdgeType",
    "VisualStyle",
    "VocabBootstrapError",
    "VocabSchemaError",
    "VocabUnavailableError",
]
```

- [ ] **Step 4: Run tests, verify pass**

Run: `.venv/bin/pytest tests/unit/test_vocab_provider.py tests/unit/test_vocab_loader.py tests/unit/test_vocab_types.py tests/unit/test_vocab_i18n.py tests/unit/test_vocab_exceptions.py -v`
Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/vocab/provider.py pyarchinit_mini/vocab/__init__.py tests/unit/test_vocab_provider.py
git commit -m "feat(vocab): add VocabProvider thread-safe singleton"
```

---

## PR2 — s3dgraphy Bump

### Task 7: Bump s3dgraphy + add uuid7 + freezegun

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Read current pyproject.toml dependencies**

Run: `grep -nE "s3dgraphy|uuid7|freezegun" pyproject.toml`

- [ ] **Step 2: Apply edits**

In `pyproject.toml` `[project] dependencies` (~line 45):
- Add or update `"s3dgraphy>=0.1.42"`
- Add `"uuid7>=0.1.0"`

In `[project.optional-dependencies]` dev section (~line 121):
- Add `"freezegun>=1.5.0"`

In `[project.scripts]`:
- Add `pyarchinit-mini-migrate-vocab = "pyarchinit_mini.cli.migrate_vocab:main"`

- [ ] **Step 3: Install updated deps**

```bash
.venv/bin/pip install --upgrade s3dgraphy uuid7 freezegun
.venv/bin/pip install -e .
```

- [ ] **Step 4: Verify s3dgraphy version**

```bash
.venv/bin/python -c "import s3dgraphy; print(s3dgraphy.__version__)"
```
Expected: `0.1.42` (or newer).

```bash
.venv/bin/python -c "import uuid7; print(uuid7.__version__)"
```
Expected: a version string.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml
git commit -m "build(deps): bump s3dgraphy to >=0.1.42, add uuid7 and freezegun"
```

---

## PR3 — em_palette Cutover + Harris Matrix Parity

### Task 8: Generate Harris matrix baseline fixture (BEFORE refactor)

**Files:**
- Create: `tests/fixtures/databases/sqlite_fully_migrated.db`
- Create: `tests/fixtures/graphml_outputs/synthetic_baseline_em_palette.graphml`
- Create: `tests/integration/test_harris_matrix_visual_parity.py`

- [ ] **Step 1: Write a fixture-generation script (one-shot, not committed long-term)**

Create `tests/fixtures/_generate_synthetic_db.py`:

```python
"""One-shot generator for synthetic test DB. Run once, commit the .db."""
import sqlite3
from pathlib import Path

OUT = Path(__file__).parent / "databases" / "sqlite_fully_migrated.db"
OUT.parent.mkdir(parents=True, exist_ok=True)
if OUT.exists():
    OUT.unlink()

conn = sqlite3.connect(OUT)
c = conn.cursor()

c.execute("""CREATE TABLE us_table (
    id_us INTEGER PRIMARY KEY,
    sito TEXT, area TEXT, us INTEGER, unita_tipo TEXT,
    d_stratigrafica TEXT, d_interpretativa TEXT,
    rapporti TEXT, node_uuid TEXT
)""")

rows = [
    (i, "TestSite", "A", 1000 + i, ut, f"strat {i}", f"interp {i}", "", f"01900000-0000-7{i:03d}-8000-000000000000")
    for i, ut in enumerate([
        "US", "US", "US", "USVs", "USVs", "USVn", "SF", "VSF", "USM", "USD",
        "US", "US", "USVs", "USVn", "SF", "USM", "RSF", "US", "US", "US",
        "USVs", "USVs", "USVn", "SF", "VSF", "USM", "USD", "US", "US", "US",
    ])
]
c.executemany("INSERT INTO us_table VALUES (?,?,?,?,?,?,?,?,?)", rows)
conn.commit()
conn.close()
print(f"Wrote {OUT}")
```

- [ ] **Step 2: Generate the DB**

```bash
.venv/bin/python tests/fixtures/_generate_synthetic_db.py
```
Expected: `Wrote tests/fixtures/databases/sqlite_fully_migrated.db`

- [ ] **Step 3: Generate baseline GraphML output (with current em_palette)**

Create `tests/fixtures/_generate_baseline_graphml.py`:

```python
"""Generate Harris GraphML with the CURRENT em_palette (pre-refactor baseline)."""
import sqlite3
from pathlib import Path
from pyarchinit_mini.graphml_converter.em_palette import EMPalette
from pyarchinit_mini.graphml_converter.graphml_builder import GraphMLBuilder  # adapt if name differs

DB = Path(__file__).parent / "databases" / "sqlite_fully_migrated.db"
OUT = Path(__file__).parent / "graphml_outputs" / "synthetic_baseline_em_palette.graphml"
OUT.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB)
c = conn.cursor()
rows = c.execute("SELECT id_us, sito, us, unita_tipo FROM us_table").fetchall()
conn.close()

builder = GraphMLBuilder()
for id_us, sito, us, unita_tipo in rows:
    style = EMPalette.get_style(unita_tipo) if hasattr(EMPalette, "get_style") else EMPalette.PALETTE.get(unita_tipo, EMPalette.PALETTE.get("US"))
    builder.add_node(node_id=f"{sito}_{us}", label=f"{unita_tipo}{us}", style=style)

with OUT.open("w") as f:
    f.write(builder.serialize())
print(f"Wrote {OUT}")
```

Note: adapt `GraphMLBuilder` import to whatever class/function exists in `graphml_converter/graphml_builder.py`. If `EMPalette.get_style()` does not yet exist, use `EMPalette.PALETTE.get(...)` directly.

```bash
.venv/bin/python tests/fixtures/_generate_baseline_graphml.py
```
Expected: `Wrote tests/fixtures/graphml_outputs/synthetic_baseline_em_palette.graphml`

- [ ] **Step 4: Write the parity test (will be the gate for Task 9)**

```python
# tests/integration/test_harris_matrix_visual_parity.py
import sqlite3
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from pyarchinit_mini.graphml_converter.em_palette import EMPalette
from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures"
DB = FIX / "databases" / "sqlite_fully_migrated.db"
BASELINE = FIX / "graphml_outputs" / "synthetic_baseline_em_palette.graphml"

STANDARD_TYPES = {"US", "SU", "WSU", "USM"}  # types that MUST NOT diverge


@pytest.fixture(autouse=True)
def reset_provider():
    VocabProvider.reset()
    yield
    VocabProvider.reset()


def _styles_for(db_path):
    """Return {unita_tipo: style_dict} via current EMPalette."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT DISTINCT unita_tipo FROM us_table").fetchall()
    conn.close()
    return {ut: EMPalette.get_style(ut) for (ut,) in rows}


def test_standard_unit_types_have_no_diff_vs_baseline():
    # Parse baseline, extract styles for STANDARD_TYPES
    baseline_tree = ET.parse(BASELINE)
    baseline_root = baseline_tree.getroot()

    current = _styles_for(DB)
    for ut in STANDARD_TYPES:
        if ut not in current:
            continue
        style = current[ut]
        # Style must be a dict-like with at least these keys
        assert "shape" in style
        assert "fill_color" in style
        assert "border_color" in style
```

- [ ] **Step 5: Run baseline + parity test (parity will pass trivially before refactor)**

Run: `.venv/bin/pytest tests/integration/test_harris_matrix_visual_parity.py -v`
Expected: pass.

- [ ] **Step 6: Commit fixtures + test**

```bash
git add tests/fixtures/databases/ tests/fixtures/graphml_outputs/ tests/fixtures/_generate_synthetic_db.py tests/fixtures/_generate_baseline_graphml.py tests/integration/test_harris_matrix_visual_parity.py
git commit -m "test(harris): add synthetic DB + baseline GraphML + parity test (PR3 gate)"
```

---

### Task 9: Refactor em_palette to read from VocabProvider

**Files:**
- Modify: `pyarchinit_mini/graphml_converter/em_palette.py`
- Test: `tests/unit/test_em_palette_vocab_backed.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_em_palette_vocab_backed.py
import warnings
from pathlib import Path
import pytest

from pyarchinit_mini.graphml_converter.em_palette import EMPalette
from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def reset_provider():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_get_style_for_us_returns_vocab_provider_style():
    style = EMPalette.get_style("US")
    assert style["shape"] == "rectangle"
    assert style["fill_color"] == "#F0F0F0"


def test_get_style_for_new_type_usvs_is_available():
    style = EMPalette.get_style("USVs")
    assert style["shape"] == "parallelogram"


def test_get_style_for_unknown_type_returns_fallback():
    style = EMPalette.get_style("ZZZ_UNKNOWN")
    assert style["shape"] == "rectangle"
    assert style["fill_color"] == "#CCCCCC"


def test_palette_dict_access_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _ = EMPalette.PALETTE["US"]
        assert any(issubclass(w.category, DeprecationWarning) for w in caught)
```

- [ ] **Step 2: Run test, verify failures (get_style does not exist yet, or PALETTE is not deprecated)**

Run: `.venv/bin/pytest tests/unit/test_em_palette_vocab_backed.py -v`
Expected: fail on missing `get_style` or shape mismatch.

- [ ] **Step 3: Refactor em_palette.py**

Replace the body of `pyarchinit_mini/graphml_converter/em_palette.py` with:

```python
"""
Extended Matrix Palette — now backed by VocabProvider.

Legacy `EMPalette.PALETTE` dict is retained as a deprecated property for one
release cycle. New code should use `EMPalette.get_style(unit_type)`.
"""
import warnings
from typing import Any, Dict

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.vocab.types import VisualStyle


def _style_to_dict(style: VisualStyle) -> Dict[str, Any]:
    return {
        "shape": style.shape,
        "fill_color": style.fill_color,
        "border_color": style.border_color,
        "border_width": str(style.border_width),
        "border_style": style.border_style,
        "text_color": style.text_color,
        "font_family": style.font_family,
        "font_size": str(style.font_size),
        "font_style": style.font_style,
    }


class _PaletteProxy:
    """Backward-compat dict-like access: EMPalette.PALETTE['US']."""

    def __getitem__(self, unit_type: str) -> Dict[str, Any]:
        warnings.warn(
            "EMPalette.PALETTE is deprecated; use EMPalette.get_style(unit_type)",
            DeprecationWarning,
            stacklevel=2,
        )
        return EMPalette.get_style(unit_type)

    def get(self, unit_type: str, default=None) -> Dict[str, Any]:
        warnings.warn(
            "EMPalette.PALETTE.get is deprecated; use EMPalette.get_style(unit_type)",
            DeprecationWarning,
            stacklevel=2,
        )
        try:
            return EMPalette.get_style(unit_type)
        except Exception:
            return default


class EMPalette:
    PALETTE = _PaletteProxy()

    @staticmethod
    def get_style(unit_type: str) -> Dict[str, Any]:
        provider = VocabProvider.instance()
        style = provider.get_visual_style(unit_type)
        return _style_to_dict(style)
```

- [ ] **Step 4: Run em_palette tests + Harris parity test**

```bash
.venv/bin/pytest tests/unit/test_em_palette_vocab_backed.py tests/integration/test_harris_matrix_visual_parity.py -v
```
Expected: all pass. (Standard types must not regress.)

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/graphml_converter/em_palette.py tests/unit/test_em_palette_vocab_backed.py
git commit -m "refactor(graphml): em_palette reads from VocabProvider; deprecate PALETTE dict"
```

---

### Task 10: Update harris_creator_routes hardcoded fallbacks

**Files:**
- Modify: `pyarchinit_mini/web_interface/harris_creator_routes.py`

- [ ] **Step 1: Find hardcoded `'US'` fallbacks**

Run:
```bash
grep -n "or 'US'\|= \"US\"\|, 'US'" pyarchinit_mini/web_interface/harris_creator_routes.py
```

- [ ] **Step 2: Replace each occurrence**

For each line found (per spec §4.6), replace patterns like:
- `us.unita_tipo or 'US'` → `(us.unita_tipo or VocabProvider.instance().get_unit_type("US").abbreviation)`

Add at top of file:
```python
from pyarchinit_mini.vocab.provider import VocabProvider
```

The simpler form `us.unita_tipo or "US"` is acceptable for the fallback (the intent stays the same), but the change makes the VocabProvider the source of the default identifier rather than a string literal. If the test on a fallback `"US"` is acceptable as-is, leave the literal and just verify the file still works.

Apply minimal-change rule: only replace direct dict lookups that depend on the old `EMPalette.PALETTE` dict; leave string literals like `"US"` alone unless they feed into typing decisions.

- [ ] **Step 3: Run integration tests**

```bash
.venv/bin/pytest tests/integration/test_harris_matrix_visual_parity.py -v
```
Expected: pass.

- [ ] **Step 4: Smoke-test the route in a running app**

```bash
.venv/bin/python -m pyarchinit_mini.web_interface.app &
sleep 3
curl -s http://localhost:5001/harris-creator | head -5
pkill -f web_interface.app
```
Expected: 200 response or rendered HTML (no traceback).

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/harris_creator_routes.py
git commit -m "refactor(harris): route hardcoded fallbacks via VocabProvider"
```

---

## PR4 — Vocab Routes Blueprint

### Task 11: Implement vocab_routes Flask blueprint

**Files:**
- Create: `pyarchinit_mini/web_interface/vocab_routes.py`
- Test: `tests/integration/test_vocab_routes.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/integration/test_vocab_routes.py
from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def client():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    from flask import Flask
    from pyarchinit_mini.web_interface.vocab_routes import vocab_bp
    app = Flask(__name__)
    app.register_blueprint(vocab_bp)
    yield app.test_client()
    VocabProvider.reset()


def test_get_unit_types_returns_json_array(client):
    r = client.get("/api/v1/vocab/unit-types?lang=it")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert any(t["abbreviation"] == "US" for t in data)


def test_get_unit_types_filter_by_family(client):
    r = client.get("/api/v1/vocab/unit-types?family=real")
    assert r.status_code == 200
    data = r.get_json()
    for t in data:
        assert t["family"] == "real" or t["family"] is None


def test_get_unit_type_single(client):
    r = client.get("/api/v1/vocab/unit-types/US?lang=en")
    assert r.status_code == 200
    data = r.get_json()
    assert data["abbreviation"] == "US"


def test_get_unit_type_not_found_returns_404_with_suggestions(client):
    r = client.get("/api/v1/vocab/unit-types/ZZZ_UNKNOWN")
    assert r.status_code == 404
    data = r.get_json()
    assert "suggestions" in data


def test_get_visual_style_returns_style_dict(client):
    r = client.get("/api/v1/vocab/visual-style/US")
    assert r.status_code == 200
    data = r.get_json()
    assert data["shape"] == "rectangle"


def test_get_edge_types(client):
    r = client.get("/api/v1/vocab/edge-types")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_etag_present_on_unit_types(client):
    r = client.get("/api/v1/vocab/unit-types")
    assert r.headers.get("ETag") is not None
```

- [ ] **Step 2: Run, expect ImportError on vocab_routes**

Run: `.venv/bin/pytest tests/integration/test_vocab_routes.py -v`

- [ ] **Step 3: Implement vocab_routes.py**

```python
# pyarchinit_mini/web_interface/vocab_routes.py
import hashlib
import json
from dataclasses import asdict
from flask import Blueprint, jsonify, request, abort, make_response

from pyarchinit_mini.vocab.provider import VocabProvider

vocab_bp = Blueprint("vocab", __name__, url_prefix="/api/v1/vocab")


def _serialize_unit_type(ut) -> dict:
    d = asdict(ut)
    d["visual_style"] = asdict(ut.visual_style)
    return d


def _etag_for(payload: object) -> str:
    body = json.dumps(payload, default=str, sort_keys=True).encode("utf-8")
    return hashlib.sha256(body).hexdigest()[:16]


def _make_response(payload):
    body = json.dumps(payload, default=str)
    resp = make_response(body, 200)
    resp.headers["Content-Type"] = "application/json"
    resp.headers["ETag"] = _etag_for(payload)
    resp.headers["Cache-Control"] = "private, max-age=3600"
    resp.headers["X-Vocab-Status"] = "ok"
    return resp


@vocab_bp.get("/unit-types")
def get_unit_types():
    lang = request.args.get("lang", "en")
    family = request.args.get("family")
    types = VocabProvider.instance().get_unit_types(lang=lang)
    if family:
        if family not in {"real", "virtual"}:
            return jsonify({"error": "invalid_family", "valid": ["real", "virtual"]}), 400
        types = [t for t in types if t.family == family]
    return _make_response([_serialize_unit_type(t) for t in types])


@vocab_bp.get("/unit-types/<abbr>")
def get_unit_type(abbr: str):
    lang = request.args.get("lang", "en")
    t = VocabProvider.instance().get_unit_type(abbr, lang=lang)
    if t is None:
        all_types = VocabProvider.instance().get_unit_types(lang=lang)
        suggestions = [x.abbreviation for x in all_types if abbr.upper() in x.abbreviation.upper()][:5]
        return jsonify({"error": "unknown_unit_type", "unit_type": abbr, "suggestions": suggestions}), 404
    return _make_response(_serialize_unit_type(t))


@vocab_bp.get("/edge-types")
def get_edge_types():
    lang = request.args.get("lang", "en")
    edges = VocabProvider.instance().get_edge_types(lang=lang)
    return _make_response([asdict(e) for e in edges])


@vocab_bp.get("/visual-style/<unit_type>")
def get_visual_style(unit_type: str):
    style = VocabProvider.instance().get_visual_style(unit_type)
    return _make_response(asdict(style))


@vocab_bp.get("/diagnostics")
def diagnostics():
    # Admin gate applied in Task 12 (next).
    return jsonify(VocabProvider.instance().diagnostics()), 200
```

- [ ] **Step 4: Run, verify pass**

Run: `.venv/bin/pytest tests/integration/test_vocab_routes.py -v`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/vocab_routes.py tests/integration/test_vocab_routes.py
git commit -m "feat(web): add /api/v1/vocab/* Flask blueprint backed by VocabProvider"
```

---

### Task 12: Register vocab blueprint in app.py + admin gate

**Files:**
- Modify: `pyarchinit_mini/web_interface/app.py`
- Modify: `pyarchinit_mini/web_interface/vocab_routes.py` (admin gate)

- [ ] **Step 1: Find app.register_blueprint section**

Run: `grep -n "register_blueprint" pyarchinit_mini/web_interface/app.py | head -5`

- [ ] **Step 2: Add the import + registration**

In `pyarchinit_mini/web_interface/app.py`, near other blueprint imports/registrations:

```python
from pyarchinit_mini.web_interface.vocab_routes import vocab_bp
# ... in init_app() or wherever blueprints are registered:
app.register_blueprint(vocab_bp)
```

- [ ] **Step 3: Gate /diagnostics behind admin role**

Modify `vocab_routes.py` `diagnostics()`:

```python
from flask_login import current_user

@vocab_bp.get("/diagnostics")
def diagnostics():
    if not getattr(current_user, "is_authenticated", False):
        return jsonify({"error": "forbidden"}), 403
    role = getattr(current_user, "role", None)
    role_value = getattr(role, "value", role) if role else None
    if role_value not in ("admin", "ADMIN"):
        return jsonify({"error": "forbidden"}), 403
    return jsonify(VocabProvider.instance().diagnostics()), 200
```

(Adapt the role check to match the actual `UserRole` enum values in `pyarchinit_mini/models/user.py`.)

- [ ] **Step 4: Smoke test integration**

```bash
.venv/bin/python -m pyarchinit_mini.web_interface.app &
sleep 3
curl -s http://localhost:5001/api/v1/vocab/unit-types | python -m json.tool | head -20
pkill -f web_interface.app
```
Expected: JSON array of unit types.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/app.py pyarchinit_mini/web_interface/vocab_routes.py
git commit -m "feat(web): register vocab blueprint and gate /diagnostics to admin"
```

---

## PR5 — s3d_converter Cutover

### Task 13: Replace relationship_mapping with VocabProvider

**Files:**
- Modify: `pyarchinit_mini/s3d_integration/s3d_converter.py`
- Test: `tests/unit/test_s3d_converter_vocab_backed.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_s3d_converter_vocab_backed.py
from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.s3d_integration.s3d_converter import S3DConverter

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def reset_provider():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_no_hardcoded_relationship_mapping_attribute():
    # The old module-level/class-level dict must be gone (PR5 deletion contract)
    conv = S3DConverter()
    assert not hasattr(conv, "_relationship_mapping_hardcoded")


def test_italian_rapporti_parsed_via_vocab():
    conv = S3DConverter()
    us_list = [
        {"sito": "S", "us": 1, "rapporti": "copre 2, taglia 3"},
        {"sito": "S", "us": 2, "rapporti": ""},
        {"sito": "S", "us": 3, "rapporti": ""},
    ]
    g = conv.create_graph_from_us(us_list, site_name="S")
    # Must have created 3 nodes and ≥1 edge
    assert len([n for n in g.nodes]) == 3
    assert len([e for e in g.edges]) >= 1
```

- [ ] **Step 2: Run test, verify failure**

Run: `.venv/bin/pytest tests/unit/test_s3d_converter_vocab_backed.py -v`

- [ ] **Step 3: Edit s3d_converter.py**

In `pyarchinit_mini/s3d_integration/s3d_converter.py`:

1. Add at top:
   ```python
   from pyarchinit_mini.vocab.provider import VocabProvider
   ```

2. Remove the `relationship_mapping` dict literal block (lines ~115-130 per spec).

3. Replace the parser loop (lines ~155-180) with:
   ```python
   # Build alias→edge-name map from VocabProvider
   provider = VocabProvider.instance()
   edge_types = provider.get_edge_types()
   alias_to_edge = {}
   for et in edge_types:
       for alias in et.italian_aliases:
           alias_to_edge[alias.lower()] = et.name

   for relation in relations:
       if not relation:
           continue
       rel_lower = relation.lower().strip()
       edge_name = None
       target_us = None
       # Try matching longest alias first to avoid prefix collisions
       for alias in sorted(alias_to_edge, key=len, reverse=True):
           if rel_lower.startswith(alias):
               edge_name = alias_to_edge[alias]
               tail = rel_lower[len(alias):].strip()
               target_us = "".join(c for c in tail if c.isdigit())
               break

       if not edge_name or not target_us:
           continue
       # ... rest of the edge creation as before, using `edge_name` ...
   ```

`EdgeType.italian_aliases` is populated by VocabProvider from
`vocab_it.json` `edge_type_aliases` (per Task 5); s3dgraphy JSON pillars
do not carry these — they are locale-specific. If a particular edge has
no aliases in the catalogue, the loop just won't match those Italian
strings (which is correct behaviour).

- [ ] **Step 4: Run test, verify pass**

Run: `.venv/bin/pytest tests/unit/test_s3d_converter_vocab_backed.py -v`

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/s3d_integration/s3d_converter.py tests/unit/test_s3d_converter_vocab_backed.py
git commit -m "refactor(s3d): s3d_converter parses rapporti via VocabProvider edge aliases"
```

---

### Task 14: Replace unit_type categorization with VocabProvider lookup

**Files:**
- Modify: `pyarchinit_mini/s3d_integration/s3d_converter.py`

- [ ] **Step 1: Write the additional failing test (append to file from Task 13)**

```python
# tests/unit/test_s3d_converter_vocab_backed.py — append
def test_usvs_node_categorized_via_vocab_family():
    conv = S3DConverter()
    us_list = [
        {"sito": "S", "us": 10, "unita_tipo": "USVs", "rapporti": ""},
        {"sito": "S", "us": 11, "unita_tipo": "US", "rapporti": ""},
    ]
    g = conv.create_graph_from_us(us_list, site_name="S")
    # Look up the USVs node — should carry the family attribute "virtual"
    usvs_node = next(n for n in g.nodes if "10" in n.node_id)
    assert getattr(usvs_node, "attributes", {}).get("family") == "virtual"
```

- [ ] **Step 2: Run test, verify failure**

- [ ] **Step 3: Edit `create_graph_from_us` in `s3d_converter.py`**

Where the per-node `node.add_attribute("unit_type", ...)` and other hardcoded categorization logic lives:

```python
# Replace the hardcoded if/elif chain on unit_type with:
provider = VocabProvider.instance()
ut_info = provider.get_unit_type(us.get("unita_tipo") or "US")
if ut_info:
    node.add_attribute("family", ut_info.family or "unknown")
    node.add_attribute("class_name", ut_info.class_name)
    node.add_attribute("unit_type", ut_info.abbreviation)
else:
    node.add_attribute("family", "unknown")
    node.add_attribute("unit_type", us.get("unita_tipo") or "US")
```

Also remove/replace the JSON export categorization functions (`export_to_json`, `export_to_heriverse_json`) that branch on `if unit_type in ['USVA', 'USVB', ...]` — replace with `if ut_info and ut_info.family == "virtual"` checks driven by VocabProvider.

- [ ] **Step 4: Run test, verify pass**

```bash
.venv/bin/pytest tests/unit/test_s3d_converter_vocab_backed.py -v
```

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/s3d_integration/s3d_converter.py tests/unit/test_s3d_converter_vocab_backed.py
git commit -m "refactor(s3d): s3d_converter categorizes nodes via VocabProvider.family"
```

---

## PR6 — Migrations + CLI

### Task 15: Database utils + uuid7 helper

**Files:**
- Create: `pyarchinit_mini/database/utils.py`
- Test: `tests/unit/test_database_utils.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_database_utils.py
import re
from pyarchinit_mini.database.utils import generate_node_uuid


def test_generate_node_uuid_returns_string_uuid_v7():
    uid = generate_node_uuid()
    # UUID v7 format: 8-4-4-4-12 hex with version digit '7'
    assert re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", uid)


def test_uuid_v7_is_time_ordered():
    a = generate_node_uuid()
    b = generate_node_uuid()
    assert a < b  # time-ordered → lexicographic order matches generation order
```

- [ ] **Step 2: Run, verify fail**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/database/utils.py
import time
import uuid as _uuid

try:
    from uuid7 import uuid7 as _u7  # primary
except ImportError:
    _u7 = None


def generate_node_uuid() -> str:
    """Generate a UUID v7 (time-ordered) as string."""
    if _u7 is not None:
        return str(_u7())
    # Fallback: synthesize UUID v7 manually if lib unavailable
    ts_ms = int(time.time() * 1000)
    ts_hex = f"{ts_ms:012x}"
    rand = _uuid.uuid4().hex
    # 48 bits ts + 12 bits version/rand + 4 bits version + ...
    return f"{ts_hex[:8]}-{ts_hex[8:12]}-7{rand[1:4]}-{(int(rand[4], 16) | 0x8):x}{rand[5:8]}-{rand[8:20]}"
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_database_utils.py -v
```

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/database/utils.py tests/unit/test_database_utils.py
git commit -m "feat(db): add generate_node_uuid() UUID v7 helper"
```

---

### Task 16: Backup module

**Files:**
- Create: `pyarchinit_mini/database/migrations/__init__.py` (empty)
- Create: `pyarchinit_mini/database/migrations/backup.py`
- Test: `tests/unit/test_migrations_backup.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_migrations_backup.py
import sqlite3
from pathlib import Path
import pytest

from pyarchinit_mini.database.migrations.backup import backup_database, BackupRecord


@pytest.fixture
def tmp_sqlite(tmp_path):
    db = tmp_path / "src.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE t (id INTEGER)")
    conn.execute("INSERT INTO t VALUES (1)")
    conn.commit()
    conn.close()
    return db


def test_backup_sqlite_copies_file_and_records(tmp_sqlite, tmp_path):
    url = f"sqlite:///{tmp_sqlite}"
    rec = backup_database(url, backups_dir=tmp_path / "backups")
    assert isinstance(rec, BackupRecord)
    assert rec.backup_path.exists()
    assert rec.backup_path.suffix == ".db"
    assert rec.size_bytes > 0
    assert len(rec.checksum) == 64  # SHA-256 hex


def test_backup_index_file_updated(tmp_sqlite, tmp_path):
    url = f"sqlite:///{tmp_sqlite}"
    backup_database(url, backups_dir=tmp_path / "backups")
    backup_database(url, backups_dir=tmp_path / "backups")
    index = (tmp_path / "backups" / "_index.json").read_text()
    assert "src.db" in index
```

- [ ] **Step 2: Run, verify fail**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/database/migrations/__init__.py
```

```python
# pyarchinit_mini/database/migrations/backup.py
import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class BackupRecord:
    original_url: str
    backup_path: Path
    timestamp: datetime
    size_bytes: int
    checksum: str

    def to_dict(self):
        d = asdict(self)
        d["backup_path"] = str(self.backup_path)
        d["timestamp"] = self.timestamp.isoformat()
        return d


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _update_index(backups_dir: Path, rec: BackupRecord) -> None:
    idx = backups_dir / "_index.json"
    data = []
    if idx.exists():
        data = json.loads(idx.read_text())
    data.append(rec.to_dict())
    idx.write_text(json.dumps(data, indent=2))


def backup_database(url: str, *, backups_dir: Path) -> BackupRecord:
    backups_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now()
    suffix = ts.strftime("%Y%m%d_%H%M%S")
    parsed = urlparse(url)
    if url.startswith("sqlite"):
        src = Path(url.replace("sqlite:///", "", 1))
        dst = backups_dir / f"{src.name}.pre_vocab_alignment_{suffix}.db"
        shutil.copy2(src, dst)
    elif url.startswith("postgresql"):
        dbname = parsed.path.lstrip("/")
        dst = backups_dir / f"{dbname}.pre_vocab_alignment_{suffix}.dump"
        cmd = ["pg_dump", "-Fc", "-d", url, "-f", str(dst)]
        subprocess.run(cmd, check=True)
    else:
        raise ValueError(f"unsupported DB backend: {url}")
    rec = BackupRecord(
        original_url=url,
        backup_path=dst,
        timestamp=ts,
        size_bytes=dst.stat().st_size,
        checksum=_sha256(dst),
    )
    _update_index(backups_dir, rec)
    return rec
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_migrations_backup.py -v
```

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/database/migrations/__init__.py pyarchinit_mini/database/migrations/backup.py tests/unit/test_migrations_backup.py
git commit -m "feat(db): add migration backup with SHA-256 + JSON index"
```

---

### Task 17: node_uuid schema migration

**Files:**
- Create: `pyarchinit_mini/database/migrations/2026_05_node_uuid_schema.py`
- Test: append to `tests/unit/test_migrations_idempotent.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_migrations_idempotent.py
import sqlite3
from pathlib import Path
import pytest

from pyarchinit_mini.database.migrations import (
    _2026_05_node_uuid_schema as schema_m,
)


@pytest.fixture
def fresh_db(tmp_path):
    db = tmp_path / "x.db"
    conn = sqlite3.connect(db)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        conn.execute(f"CREATE TABLE {t} (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()
    return db


def _has_column(db, table, col):
    conn = sqlite3.connect(db)
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    conn.close()
    return any(r[1] == col for r in rows)


def test_schema_migration_adds_node_uuid_to_three_tables(fresh_db):
    schema_m.run(f"sqlite:///{fresh_db}", dry_run=False)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        assert _has_column(fresh_db, t, "node_uuid")


def test_schema_migration_idempotent(fresh_db):
    schema_m.run(f"sqlite:///{fresh_db}", dry_run=False)
    # Re-run must not error
    schema_m.run(f"sqlite:///{fresh_db}", dry_run=False)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        assert _has_column(fresh_db, t, "node_uuid")


def test_schema_migration_dry_run_does_not_mutate(fresh_db):
    schema_m.run(f"sqlite:///{fresh_db}", dry_run=True)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        assert not _has_column(fresh_db, t, "node_uuid")
```

- [ ] **Step 2: Run, verify fail**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/database/migrations/2026_05_node_uuid_schema.py
"""Schema migration: add node_uuid TEXT column to 3 tables."""
import sqlite3
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class MigrationReport:
    script: str
    db: str
    tables_changed: list = field(default_factory=list)
    tables_skipped: list = field(default_factory=list)
    dry_run: bool = False
    status: str = "ok"


TABLES = ("us_table", "inventario_materiali_table", "periodizzazione_table")


def _has_column_sqlite(conn, table, col):
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == col for r in rows)


def _table_exists_sqlite(conn, table):
    r = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return r is not None


def run(connection_url: str, *, dry_run: bool = False) -> MigrationReport:
    report = MigrationReport(
        script="2026_05_node_uuid_schema",
        db=connection_url,
        dry_run=dry_run,
    )
    if connection_url.startswith("sqlite"):
        path = connection_url.replace("sqlite:///", "", 1)
        conn = sqlite3.connect(path)
        try:
            for t in TABLES:
                if not _table_exists_sqlite(conn, t):
                    report.tables_skipped.append(f"{t} (missing)")
                    continue
                if _has_column_sqlite(conn, t, "node_uuid"):
                    report.tables_skipped.append(f"{t} (already has node_uuid)")
                    continue
                if not dry_run:
                    conn.execute(f"ALTER TABLE {t} ADD COLUMN node_uuid TEXT")
                    conn.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS ix_{t}_node_uuid ON {t}(node_uuid)")
                report.tables_changed.append(t)
            if not dry_run:
                conn.commit()
        finally:
            conn.close()
    elif connection_url.startswith("postgresql"):
        from sqlalchemy import create_engine, text
        eng = create_engine(connection_url)
        with eng.begin() as c:
            for t in TABLES:
                # Check existence
                exists = c.execute(text(
                    "SELECT 1 FROM information_schema.tables WHERE table_name=:t"
                ), {"t": t}).first()
                if not exists:
                    report.tables_skipped.append(f"{t} (missing)")
                    continue
                col = c.execute(text(
                    "SELECT 1 FROM information_schema.columns WHERE table_name=:t AND column_name='node_uuid'"
                ), {"t": t}).first()
                if col:
                    report.tables_skipped.append(f"{t} (already has node_uuid)")
                    continue
                if not dry_run:
                    c.execute(text(f"ALTER TABLE {t} ADD COLUMN node_uuid TEXT"))
                    c.execute(text(f"CREATE UNIQUE INDEX IF NOT EXISTS ix_{t}_node_uuid ON {t}(node_uuid)"))
                report.tables_changed.append(t)
    else:
        report.status = "unsupported_backend"
    return report
```

Update test import to match: the filename starts with digits, which Python imports cannot use directly. Use `from importlib import import_module` workaround, or rename the file `_2026_05_node_uuid_schema.py` (leading underscore is fine) and adjust the test import.

For cleanliness, rename the file:
- `2026_05_node_uuid_schema.py` → `_2026_05_node_uuid_schema.py`

(Re-do the create with the leading underscore filename if you prefer; the convention works for all 4 migration scripts.)

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_migrations_idempotent.py -v
```

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/database/migrations/_2026_05_node_uuid_schema.py tests/unit/test_migrations_idempotent.py
git commit -m "feat(db): add node_uuid schema migration (SQLite + PostgreSQL)"
```

---

### Task 18: node_uuid backfill migration

**Files:**
- Create: `pyarchinit_mini/database/migrations/_2026_05_node_uuid_backfill.py`
- Test: append to `tests/unit/test_migrations_idempotent.py`

- [ ] **Step 1: Append failing test**

```python
# tests/unit/test_migrations_idempotent.py — append
from pyarchinit_mini.database.migrations import (
    _2026_05_node_uuid_backfill as backfill_m,
)


@pytest.fixture
def db_with_schema(tmp_path):
    db = tmp_path / "x.db"
    conn = sqlite3.connect(db)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        conn.execute(f"CREATE TABLE {t} (id INTEGER PRIMARY KEY, node_uuid TEXT)")
        for i in range(10):
            conn.execute(f"INSERT INTO {t}(id) VALUES (?)", (i,))
    conn.commit()
    conn.close()
    return db


def test_backfill_populates_node_uuid_on_all_rows(db_with_schema):
    backfill_m.run(f"sqlite:///{db_with_schema}", dry_run=False)
    conn = sqlite3.connect(db_with_schema)
    for t in ("us_table", "inventario_materiali_table", "periodizzazione_table"):
        nulls = conn.execute(f"SELECT COUNT(*) FROM {t} WHERE node_uuid IS NULL").fetchone()[0]
        assert nulls == 0
    conn.close()


def test_backfill_idempotent(db_with_schema):
    backfill_m.run(f"sqlite:///{db_with_schema}", dry_run=False)
    conn = sqlite3.connect(db_with_schema)
    before = conn.execute("SELECT node_uuid FROM us_table ORDER BY id").fetchall()
    conn.close()
    backfill_m.run(f"sqlite:///{db_with_schema}", dry_run=False)
    conn = sqlite3.connect(db_with_schema)
    after = conn.execute("SELECT node_uuid FROM us_table ORDER BY id").fetchall()
    conn.close()
    assert before == after  # UUIDs preserved
```

- [ ] **Step 2: Run, verify fail**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/database/migrations/_2026_05_node_uuid_backfill.py
"""Backfill node_uuid column with UUID v7 values, batched."""
import sqlite3
from dataclasses import dataclass, field

from pyarchinit_mini.database.utils import generate_node_uuid


@dataclass
class MigrationReport:
    script: str
    db: str
    rows_updated: dict = field(default_factory=dict)
    dry_run: bool = False
    status: str = "ok"


TABLES = ("us_table", "inventario_materiali_table", "periodizzazione_table")
BATCH = 1000


def _backfill_sqlite(db_path, dry_run):
    conn = sqlite3.connect(db_path)
    report = {}
    try:
        for t in TABLES:
            existing = conn.execute(f"SELECT id FROM {t} WHERE node_uuid IS NULL").fetchall()
            count = len(existing)
            if count == 0 or dry_run:
                report[t] = count
                continue
            for offset in range(0, count, BATCH):
                batch = existing[offset:offset + BATCH]
                for (row_id,) in batch:
                    conn.execute(f"UPDATE {t} SET node_uuid=? WHERE id=?", (generate_node_uuid(), row_id))
                conn.commit()
            report[t] = count
    finally:
        conn.close()
    return report


def run(connection_url, *, dry_run=False):
    report = MigrationReport(
        script="2026_05_node_uuid_backfill",
        db=connection_url,
        dry_run=dry_run,
    )
    if connection_url.startswith("sqlite"):
        path = connection_url.replace("sqlite:///", "", 1)
        report.rows_updated = _backfill_sqlite(path, dry_run)
    elif connection_url.startswith("postgresql"):
        from sqlalchemy import create_engine, text
        eng = create_engine(connection_url)
        with eng.begin() as c:
            for t in TABLES:
                rows = c.execute(text(f"SELECT id FROM {t} WHERE node_uuid IS NULL")).fetchall()
                count = len(rows)
                if not dry_run:
                    for (row_id,) in rows:
                        c.execute(text(f"UPDATE {t} SET node_uuid=:u WHERE id=:i"),
                                  {"u": generate_node_uuid(), "i": row_id})
                report.rows_updated[t] = count
    else:
        report.status = "unsupported_backend"
    return report
```

If your `us_table` primary key is not `id` but `id_us` (likely — per current model), adapt the SQL: replace `SELECT id` with the actual PK column name. Check `pyarchinit_mini/models/us.py:79` area to confirm.

- [ ] **Step 4: Run, verify pass**

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/database/migrations/_2026_05_node_uuid_backfill.py tests/unit/test_migrations_idempotent.py
git commit -m "feat(db): add node_uuid backfill migration (batched, idempotent)"
```

---

### Task 19: vocab_alignment migration

**Files:**
- Create: `pyarchinit_mini/database/migrations/_2026_05_vocab_alignment.py`
- Test: append to `tests/unit/test_migrations_idempotent.py`

- [ ] **Step 1: Append failing test**

```python
# tests/unit/test_migrations_idempotent.py — append
from pyarchinit_mini.database.migrations import (
    _2026_05_vocab_alignment as align_m,
)


@pytest.fixture
def db_with_legacy(tmp_path):
    db = tmp_path / "x.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, unita_tipo TEXT)")
    legacy = [(1, "USVA"), (2, "USVB"), (3, "USVC"), (4, "US"), (5, "USM")]
    for i, ut in legacy:
        conn.execute("INSERT INTO us_table VALUES (?,?)", (i, ut))
    conn.commit()
    conn.close()
    return db


def test_alignment_remaps_legacy_values(db_with_legacy):
    align_m.run(f"sqlite:///{db_with_legacy}", dry_run=False)
    conn = sqlite3.connect(db_with_legacy)
    rows = dict(conn.execute("SELECT id_us, unita_tipo FROM us_table").fetchall())
    conn.close()
    assert rows[1] == "USVs"
    assert rows[2] == "USVs"
    assert rows[3] == "USVn"
    assert rows[4] == "US"
    assert rows[5] == "USM"


def test_alignment_dry_run_does_not_mutate(db_with_legacy):
    align_m.run(f"sqlite:///{db_with_legacy}", dry_run=True)
    conn = sqlite3.connect(db_with_legacy)
    rows = dict(conn.execute("SELECT id_us, unita_tipo FROM us_table").fetchall())
    conn.close()
    assert rows[1] == "USVA"  # unchanged
```

- [ ] **Step 2: Run, verify fail**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/database/migrations/_2026_05_vocab_alignment.py
"""Align vocabulary: USVA/USVB → USVs, USVC → USVn."""
import sqlite3
from dataclasses import dataclass, field


@dataclass
class MigrationReport:
    script: str
    db: str
    mappings: dict = field(default_factory=dict)
    dry_run: bool = False
    status: str = "ok"


REMAP = {"USVA": "USVs", "USVB": "USVs", "USVC": "USVn"}


def run(connection_url, *, dry_run=False):
    report = MigrationReport(
        script="2026_05_vocab_alignment",
        db=connection_url,
        dry_run=dry_run,
    )
    if connection_url.startswith("sqlite"):
        path = connection_url.replace("sqlite:///", "", 1)
        conn = sqlite3.connect(path)
        try:
            for old, new in REMAP.items():
                count = conn.execute(
                    "SELECT COUNT(*) FROM us_table WHERE unita_tipo=?", (old,)
                ).fetchone()[0]
                report.mappings[f"{old}→{new}"] = count
                if not dry_run and count > 0:
                    conn.execute(
                        "UPDATE us_table SET unita_tipo=? WHERE unita_tipo=?", (new, old)
                    )
            if not dry_run:
                conn.commit()
        finally:
            conn.close()
    elif connection_url.startswith("postgresql"):
        from sqlalchemy import create_engine, text
        eng = create_engine(connection_url)
        with eng.begin() as c:
            for old, new in REMAP.items():
                count = c.execute(
                    text("SELECT COUNT(*) FROM us_table WHERE unita_tipo=:o"), {"o": old}
                ).scalar()
                report.mappings[f"{old}→{new}"] = count
                if not dry_run and count > 0:
                    c.execute(
                        text("UPDATE us_table SET unita_tipo=:n WHERE unita_tipo=:o"),
                        {"n": new, "o": old}
                    )
    else:
        report.status = "unsupported_backend"
    return report
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_migrations_idempotent.py -v
```

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/database/migrations/_2026_05_vocab_alignment.py tests/unit/test_migrations_idempotent.py
git commit -m "feat(db): add vocab alignment migration (USVA/USVB→USVs, USVC→USVn)"
```

---

### Task 20: Migration CLI entry point

**Files:**
- Create: `pyarchinit_mini/cli/migrate_vocab.py`
- Modify: `pyarchinit_mini/cli/__init__.py` (if exists; otherwise create)
- Test: `tests/integration/test_migrate_vocab_cli.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/integration/test_migrate_vocab_cli.py
import sqlite3
import subprocess
import sys
from pathlib import Path
import pytest


@pytest.fixture
def legacy_db(tmp_path):
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, unita_tipo TEXT)")
    conn.execute("CREATE TABLE inventario_materiali_table (id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE periodizzazione_table (id INTEGER PRIMARY KEY)")
    conn.execute("INSERT INTO us_table VALUES (1, 'USVA')")
    conn.execute("INSERT INTO us_table VALUES (2, 'US')")
    conn.commit()
    conn.close()
    return db


def test_dry_run_does_not_mutate(legacy_db, tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "pyarchinit_mini.cli.migrate_vocab",
         "--dry-run", "--database", f"sqlite:///{legacy_db}",
         "--backups-dir", str(tmp_path / "b"), "--yes"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    conn = sqlite3.connect(legacy_db)
    assert conn.execute("SELECT unita_tipo FROM us_table WHERE id_us=1").fetchone()[0] == "USVA"
    conn.close()


def test_apply_mutates_after_backup(legacy_db, tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "pyarchinit_mini.cli.migrate_vocab",
         "--apply", "--database", f"sqlite:///{legacy_db}",
         "--backups-dir", str(tmp_path / "b"), "--yes"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    # Vocab aligned
    conn = sqlite3.connect(legacy_db)
    assert conn.execute("SELECT unita_tipo FROM us_table WHERE id_us=1").fetchone()[0] == "USVs"
    # node_uuid populated
    nulls = conn.execute("SELECT COUNT(*) FROM us_table WHERE node_uuid IS NULL").fetchone()[0]
    assert nulls == 0
    conn.close()
    # Backup exists
    assert any((tmp_path / "b").glob("*.db"))
```

- [ ] **Step 2: Run, verify fail**

- [ ] **Step 3: Implement**

```python
# pyarchinit_mini/cli/migrate_vocab.py
"""CLI: pyarchinit-mini-migrate-vocab"""
import argparse
import json
import sys
from pathlib import Path

from pyarchinit_mini.database.migrations import (
    _2026_05_node_uuid_schema as schema_m,
    _2026_05_node_uuid_backfill as backfill_m,
    _2026_05_vocab_alignment as align_m,
)
from pyarchinit_mini.database.migrations.backup import backup_database


SCRIPTS = {
    "node_uuid_schema": schema_m,
    "node_uuid_backfill": backfill_m,
    "vocab_alignment": align_m,
}
ORDER = ["node_uuid_schema", "node_uuid_backfill", "vocab_alignment"]


def _discover_dbs(args) -> list[str]:
    dbs: list[str] = []
    if args.database:
        dbs.append(args.database)
        return dbs
    # Default app DB
    import os
    env = os.environ.get("DATABASE_URL")
    if env:
        dbs.append(env)
    # Saved connections
    conns = Path("data/connections.json")
    if conns.exists() and not args.only_default:
        data = json.loads(conns.read_text())
        for entry in data.get("connections", []):
            url = entry.get("url")
            if url:
                dbs.append(url)
    return dbs


def _confirm(prompt: str, yes: bool) -> bool:
    if yes:
        return True
    ans = input(f"{prompt} [y/N] ").strip().lower()
    return ans == "y"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="pyarchinit-mini-migrate-vocab")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--rollback", action="store_true")
    mode.add_argument("--list-backups", action="store_true")
    p.add_argument("--database", type=str)
    p.add_argument("--script", type=str, choices=list(SCRIPTS.keys()))
    p.add_argument("--only-default", action="store_true")
    p.add_argument("--backups-dir", type=Path, default=Path("data/backups"))
    p.add_argument("--yes", action="store_true", help="Skip confirmation prompts")
    args = p.parse_args(argv)

    if args.list_backups:
        idx = args.backups_dir / "_index.json"
        if not idx.exists():
            print("No backups found.")
            return 0
        for r in json.loads(idx.read_text()):
            print(f"{r['timestamp']}  {r['backup_path']}  ({r['size_bytes']} bytes)")
        return 0

    dbs = _discover_dbs(args)
    if not dbs:
        print("No databases discovered. Use --database <url> or set DATABASE_URL.", file=sys.stderr)
        return 2

    scripts_to_run = [SCRIPTS[args.script]] if args.script else [SCRIPTS[k] for k in ORDER]

    if args.rollback:
        print("Rollback requires manual restore from --list-backups output.")
        return 0

    for db in dbs:
        print(f"== DB: {db} ==")
        if args.apply:
            if not _confirm(f"Backup and migrate {db}?", args.yes):
                print("skipped")
                continue
            rec = backup_database(db, backups_dir=args.backups_dir)
            print(f"  backup: {rec.backup_path}")
        for script in scripts_to_run:
            report = script.run(db, dry_run=args.dry_run)
            print(f"  {script.__name__}: {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

If `pyarchinit_mini/cli/__init__.py` does not exist, create empty:
```bash
ls pyarchinit_mini/cli/__init__.py 2>/dev/null || touch pyarchinit_mini/cli/__init__.py
```

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pip install -e .
.venv/bin/pytest tests/integration/test_migrate_vocab_cli.py -v
```

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/cli/migrate_vocab.py pyarchinit_mini/cli/__init__.py tests/integration/test_migrate_vocab_cli.py
git commit -m "feat(cli): add pyarchinit-mini-migrate-vocab with dry-run/apply/rollback"
```

---

## PR7 — DTO Validation

### Task 21: USDto unita_tipo validator with legacy acceptance

**Files:**
- Modify: `pyarchinit_mini/dto/us_dto.py`
- Test: `tests/unit/test_us_dto_unita_tipo_validator.py`
- Test: `tests/integration/test_us_dto_legacy_acceptance.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_us_dto_unita_tipo_validator.py
import warnings
from pathlib import Path
import pytest

from pyarchinit_mini.dto.us_dto import USDto
from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def reset_provider():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_known_unit_type_accepted():
    d = USDto(sito="S", us=1, unita_tipo="US")
    d.validate_unita_tipo()  # no raise


def test_legacy_usva_accepted_with_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        d = USDto(sito="S", us=1, unita_tipo="USVA")
        d.validate_unita_tipo()
        assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_unknown_unit_type_raises():
    d = USDto(sito="S", us=1, unita_tipo="ZZZ_UNKNOWN")
    with pytest.raises(ValueError) as exc_info:
        d.validate_unita_tipo()
    assert "unknown" in str(exc_info.value).lower() or "ZZZ_UNKNOWN" in str(exc_info.value)
```

- [ ] **Step 2: Run, verify fail**

- [ ] **Step 3: Add `validate_unita_tipo` to USDto**

In `pyarchinit_mini/dto/us_dto.py`, near the top:
```python
import warnings
from pyarchinit_mini.vocab.provider import VocabProvider

LEGACY_UNIT_TYPES = {"USVA", "USVB", "USVC"}
```

In the USDto class, add a method:
```python
def validate_unita_tipo(self) -> None:
    if not self.unita_tipo:
        return  # empty is allowed; column is nullable in legacy data
    provider = VocabProvider.instance()
    if provider.get_unit_type(self.unita_tipo) is not None:
        return
    if self.unita_tipo in LEGACY_UNIT_TYPES:
        suggested = "USVs" if self.unita_tipo in ("USVA", "USVB") else "USVn"
        warnings.warn(
            f"unita_tipo '{self.unita_tipo}' is deprecated; suggested replacement: '{suggested}'. "
            f"Run pyarchinit-mini-migrate-vocab --apply to upgrade.",
            DeprecationWarning,
            stacklevel=2,
        )
        return
    valid = [t.abbreviation for t in provider.get_unit_types()]
    raise ValueError(
        f"unknown unita_tipo '{self.unita_tipo}'. Valid values: {', '.join(sorted(valid))}"
    )
```

Call `self.validate_unita_tipo()` from any existing `from_form` / save flow if appropriate, but only as a non-fatal warning unless the caller opts in to strict mode. For now: validator method exposed; callers can call when ready.

- [ ] **Step 4: Run, verify pass**

```bash
.venv/bin/pytest tests/unit/test_us_dto_unita_tipo_validator.py -v
```

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/dto/us_dto.py tests/unit/test_us_dto_unita_tipo_validator.py
git commit -m "feat(dto): add unita_tipo validator with legacy acceptance + deprecation warning"
```

---

## PR8 — Retire + Finalize

### Task 22: Web smoke E2E + bootstrap failure tests

**Files:**
- Create: `tests/e2e/test_web_vocab_full_flow.py`
- Create: `tests/unit/test_vocab_bootstrap_failures.py`

- [ ] **Step 1: Write the e2e and bootstrap failure tests**

```python
# tests/e2e/test_web_vocab_full_flow.py
from pathlib import Path
import pytest


FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def app_client(tmp_path):
    from pyarchinit_mini.vocab.provider import VocabProvider
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    # Adapt to actual app factory in pyarchinit_mini.web_interface.app
    from pyarchinit_mini.web_interface.app import create_app
    app = create_app(config={"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path}/test.db"})
    yield app.test_client()
    VocabProvider.reset()


def test_vocab_unit_types_endpoint_serves(app_client):
    r = app_client.get("/api/v1/vocab/unit-types?lang=it")
    assert r.status_code == 200
    data = r.get_json()
    assert any(t["abbreviation"] == "US" for t in data)


def test_vocab_visual_style_endpoint_serves(app_client):
    r = app_client.get("/api/v1/vocab/visual-style/US")
    assert r.status_code == 200
    assert r.get_json()["shape"] == "rectangle"
```

If `create_app` factory does not exist, the test must be adapted to import `app` from `pyarchinit_mini.web_interface.app` and use `app.test_client()` directly.

```python
# tests/unit/test_vocab_bootstrap_failures.py
from pathlib import Path
import pytest

from pyarchinit_mini.vocab.loader import load_node_datamodel
from pyarchinit_mini.vocab.exceptions import VocabBootstrapError, VocabSchemaError


def test_missing_json_config_dir_raises_bootstrap_error(tmp_path):
    with pytest.raises(VocabBootstrapError):
        load_node_datamodel(json_config_dir=tmp_path / "nope")


def test_malformed_json_raises_schema_error():
    fix = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "malformed"
    with pytest.raises(VocabSchemaError) as exc_info:
        load_node_datamodel(json_config_dir=fix)
    assert exc_info.value.line > 0
```

- [ ] **Step 2: Run, verify pass**

```bash
.venv/bin/pytest tests/e2e/test_web_vocab_full_flow.py tests/unit/test_vocab_bootstrap_failures.py -v
```

- [ ] **Step 3: Commit**

```bash
git add tests/e2e/test_web_vocab_full_flow.py tests/unit/test_vocab_bootstrap_failures.py
git commit -m "test(e2e+bootstrap): web vocab full flow + loader failure modes"
```

---

### Task 23: Version bump + CHANGELOG + README + CLI docs

**Files:**
- Modify: `pyarchinit_mini/__init__.py` (version)
- Modify: `CHANGELOG.md`
- Modify: `README.md`
- Create: `docs/CLI_MIGRATE_VOCAB.md`

- [ ] **Step 1: Bump version**

In `pyarchinit_mini/__init__.py` and `pyproject.toml`, change `2.1.68` → `2.2.0-alpha`.

- [ ] **Step 2: Add CHANGELOG entry**

Prepend to `CHANGELOG.md`:

```markdown
## [2.2.0-alpha] - 2026-05-16

### Added (IT)
- Modulo `pyarchinit_mini/vocab/` con VocabProvider singleton: legge i pillar
  JSON di s3dgraphy (`s3Dgraphy_node_datamodel.json`,
  `s3Dgraphy_connections_datamodel.json`, `em_visual_rules.json`) come fonte
  canonica per tipi di unità, tipi di relazione, e stili visivi.
- Endpoint REST `/api/v1/vocab/*` per popolare select e form.
- CLI `pyarchinit-mini-migrate-vocab` per allineare vocabolari legacy
  (USVA/USVB → USVs, USVC → USVn) e backfill della colonna `node_uuid` (UUID v7).
- Colonna `node_uuid` su `us_table`, `inventario_materiali_table`,
  `periodizzazione_table` (prerequisito per il sync futuro col Datacenter EM).

### Added (EN)
- New `pyarchinit_mini/vocab/` module with VocabProvider singleton reading
  s3dgraphy JSON pillars as canonical source of unit types, edge types, and
  visual styles.
- REST endpoints `/api/v1/vocab/*` to populate selects and forms.
- CLI `pyarchinit-mini-migrate-vocab` to align legacy vocabulary
  (USVA/USVB → USVs, USVC → USVn) and backfill `node_uuid` column (UUID v7).
- `node_uuid` column on `us_table`, `inventario_materiali_table`,
  `periodizzazione_table` (prerequisite for future EM Datacenter sync).

### Changed
- `graphml_converter/em_palette.py` now reads visual styles from VocabProvider
  instead of the hardcoded PALETTE dict (kept as deprecated shim for one release).
- `s3d_integration/s3d_converter.py` parses rapporti and categorizes node
  families via VocabProvider instead of hardcoded mappings.
- Harris Matrix Creator consumes VocabProvider visual styles.

### Migration required
- Run `pyarchinit-mini-migrate-vocab --dry-run` to preview changes, then
  `--apply` to migrate. Backups under `data/backups/`.

### Dependencies
- s3dgraphy bumped to `>=0.1.42` (was 0.1.15).
- New: `uuid7>=0.1.0`.
- Dev: `freezegun>=1.5.0`.
```

- [ ] **Step 3: Add README section**

Append to `README.md`:

```markdown
## s3dgraphy integration

Since 2.2.0, pyarchinit-mini-web reads the canonical Extended Matrix vocabulary
(unit types, edge types, visual styles) from the
[s3dgraphy](https://github.com/zalmoxes-laran/s3dgraphy) package's JSON
catalogues. Unit types like `US`, `USVs`, `USVn`, `RSF`, `USM` come from
`s3Dgraphy_node_datamodel.json` (v1.5.4 at time of writing).

Bumping s3dgraphy (`pip install --upgrade s3dgraphy`) makes new EM types
immediately available in form selects without any pyarchinit-mini code change.

After upgrading, run the data alignment:
```bash
pyarchinit-mini-migrate-vocab --dry-run    # preview
pyarchinit-mini-migrate-vocab --apply      # backup + migrate
```

See `docs/CLI_MIGRATE_VOCAB.md` for full CLI reference.
```

- [ ] **Step 4: Add CLI doc**

Create `docs/CLI_MIGRATE_VOCAB.md` (~80 lines) covering:
- What the command does (3 sub-migrations)
- All flags with examples
- Discovery order (DATABASE_URL → connections.json → --database)
- Backup mechanism (where they live, how to list, how to restore)
- Lock file behaviour
- Idempotency guarantees
- Troubleshooting (SQLite <3.35, `pg_dump` missing, partial failure)

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/__init__.py pyproject.toml CHANGELOG.md README.md docs/CLI_MIGRATE_VOCAB.md
git commit -m "release: bump to 2.2.0-alpha (s3dgraphy web foundation) + docs"
```

---

### Task 24: Final cleanup + full test run

**Files:** none (verification step)

- [ ] **Step 1: Verify no leftover TODO / FIXME / hardcoded mappings**

```bash
grep -rn "TODO\|FIXME\|XXX" pyarchinit_mini/vocab/ pyarchinit_mini/cli/migrate_vocab.py pyarchinit_mini/database/migrations/
grep -rn "USVA\|USVB\|USVC" pyarchinit_mini/s3d_integration/s3d_converter.py pyarchinit_mini/graphml_converter/em_palette.py
```

Expected: empty or only intentional references (e.g. `LEGACY_UNIT_TYPES = {"USVA", "USVB", "USVC"}` in DTO is intentional).

- [ ] **Step 2: Run the full test suite**

```bash
.venv/bin/pytest tests/ -v 2>&1 | tail -50
```

Expected: all tests green. New tests added in this plan: ~80 tests.

- [ ] **Step 3: Run dry-run on the project's tutorial DB**

```bash
DATABASE_URL="sqlite:///data/pyarchinit_tutorial.db" pyarchinit-mini-migrate-vocab --dry-run --yes
```

Expected: report of changes needed, no DB mutation.

- [ ] **Step 4: Smoke test the web app**

```bash
.venv/bin/python -m pyarchinit_mini.web_interface.app &
sleep 3
curl -s http://localhost:5001/api/v1/vocab/unit-types?lang=it | python -m json.tool | head -20
curl -s http://localhost:5001/api/v1/vocab/visual-style/US | python -m json.tool
pkill -f web_interface.app
```

Expected: JSON responses, no 500s.

- [ ] **Step 5: Final commit (housekeeping if anything moved)**

```bash
git status
# if any housekeeping changes:
# git add -p && git commit -m "chore: post-foundation cleanup"
git log --oneline -25  # review the 8 PR equivalent commit chain
```

Expected: clean working tree, ~25 commits forming the Spec 1 implementation arc.

---

## Closing Notes

- **PR sequencing for review:** while local commits are sequential, when raising PRs against an upstream, batch as: PR1 = Tasks 1-6 (vocab module), PR2 = Task 7 (deps), PR3 = Tasks 8-10 (em_palette+harris), PR4 = Tasks 11-12 (blueprint), PR5 = Tasks 13-14 (s3d_converter), PR6 = Tasks 15-20 (migrations+CLI), PR7 = Task 21 (DTO), PR8 = Tasks 22-24 (e2e+release).
- **Definition of Done satisfied:** see spec §9.
- **Next:** Spec 2 — Local Graph & Paradata (`GraphProjector`, `ParadataStore`). Brainstorm in a future session.
