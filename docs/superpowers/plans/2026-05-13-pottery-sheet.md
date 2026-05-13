# Pottery Sheet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Pottery (ceramica) records module to pyarchinit-mini with 1:1 schema parity to PyArchInit-QGIS `pottery_table`, full CRUD across Web / Desktop GUI / CLI, media attachments, PDF / Excel / CSV / legacy QGIS import-export, and analytics, shipped as v2.1.60.

**Architecture:** New SQLAlchemy model `Pottery(BaseModel)` mirroring the 32 columns of QGIS `pottery_table` plus the 9 sync columns from `BaseModel`. New `PotteryService` (mirrors `InventarioService`). Web routes registered via `_register_pottery_routes(app)` called from `create_app()`. Templates under `templates/pottery/` use a 3-tab Bootstrap layout matching QGIS. Media via existing polymorphic `media_table` with `entity_type='pottery'`. Desktop GUI via new `pottery_panel.py` + `pottery_dialog_extended.py`. Schema is auto-included in `upgrade_legacy_schema` (v2.1.56/57) because the model lives in `Base.metadata`.

**Tech Stack:** SQLAlchemy 2.x, Flask, Bootstrap 5 (existing), Chart.js (existing), WeasyPrint, pandas+openpyxl, Tkinter (Desktop GUI), matplotlib (Desktop analytics), pytest.

**Spec:** `docs/superpowers/specs/2026-05-13-pottery-sheet-design.md`

---

## File Structure

### Create

- `pyarchinit_mini/models/pottery.py` — `Pottery(BaseModel)` model, 32 cols + UniqueConstraint + indexes
- `pyarchinit_mini/services/pottery_dto.py` — `PotteryDTO` dataclass
- `pyarchinit_mini/services/pottery_service.py` — `PotteryService` (CRUD, listing, validation, stats, MNI)
- `pyarchinit_mini/services/pottery_pdf_service.py` — WeasyPrint rendering
- `pyarchinit_mini/web_interface/pottery_routes.py` — `_register_pottery_routes(app)` Flask routes
- `pyarchinit_mini/web_interface/templates/pottery/list.html`
- `pyarchinit_mini/web_interface/templates/pottery/form.html`
- `pyarchinit_mini/web_interface/templates/pottery/detail.html`
- `pyarchinit_mini/web_interface/templates/pottery/_row_card.html`
- `pyarchinit_mini/web_interface/templates/pdf/pottery_sheet.html`
- `pyarchinit_mini/desktop_gui/pottery_panel.py`
- `pyarchinit_mini/desktop_gui/pottery_dialog_extended.py`
- `tests/unit/test_pottery_model.py`
- `tests/unit/test_pottery_service.py`
- `tests/unit/test_pottery_dto.py`
- `tests/integration/test_pottery_routes.py`
- `tests/integration/test_pottery_legacy_upgrade.py`
- `tests/integration/test_pottery_excel_roundtrip.py`
- `tests/fixtures/legacy_with_pottery.sqlite` — small fixture, built in Task 0

### Modify

- `pyarchinit_mini/__init__.py` — version bump → `2.1.60`
- `pyproject.toml` — version bump → `2.1.60`
- `pyarchinit_mini/models/__init__.py` — export `Pottery`
- `pyarchinit_mini/services/__init__.py` — export `PotteryService`
- `pyarchinit_mini/database/migrations.py` — ensure `pottery_table` is created on boot
- `pyarchinit_mini/services/import_export_service.py:1963-1982` — add `'pottery_table'` to `tables_order`
- `pyarchinit_mini/web_interface/app.py:288` — add `('pottery', 'Pottery')` to media `entity_type` SelectField
- `pyarchinit_mini/web_interface/app.py:2682-2706` — add `pottery` branch in upload route
- `pyarchinit_mini/web_interface/app.py:2642+` — add `/api/media/pottery` endpoint
- `pyarchinit_mini/web_interface/app.py` — call `_register_pottery_routes(app)` inside `create_app`
- `pyarchinit_mini/web_interface/templates/base.html` — add *Pottery* to Records dropdown
- `pyarchinit_mini/web_interface/templates/admin/database.html` — pottery in migrate wizard table list
- `pyarchinit_mini/web_interface/templates/analytics/dashboard.html` — 3 pottery charts + MNI card
- `pyarchinit_mini/desktop_gui/main_window.py:163-166, 206` — add Pottery view menu + notebook tab
- `pyarchinit_mini/desktop_gui/analytics_dialog.py` — 3 pottery matplotlib charts

---

## Task 0: Test scaffold and legacy fixture

**Files:**
- Create: `tests/fixtures/build_legacy_with_pottery.py`
- Create: `tests/fixtures/legacy_with_pottery.sqlite` (output)
- Create: `tests/conftest.py` *(only if missing)*

- [ ] **Step 1: Verify pytest infrastructure exists**

Run:
```bash
ls tests/ && grep -E "^pytest|^addopts" pyproject.toml
```

Expected: `tests/` directory exists; `pyproject.toml` has `[tool.pytest.ini_options]` block.

- [ ] **Step 2: Create legacy fixture builder**

Create `tests/fixtures/build_legacy_with_pottery.py`:

```python
"""
Build a minimal legacy PyArchInit-QGIS SQLite DB that contains the
pottery_table with the original QGIS schema (no sync columns).
Used by integration tests for upgrade_legacy_schema and migrate-database.
"""
from pathlib import Path
import sqlite3

FIXTURE = Path(__file__).parent / "legacy_with_pottery.sqlite"

def build():
    if FIXTURE.exists():
        FIXTURE.unlink()
    conn = sqlite3.connect(FIXTURE)
    cur = conn.cursor()
    # Minimal site_table and us_table so the upgrade pass can run
    cur.execute("""
        CREATE TABLE site_table (
            id_sito INTEGER PRIMARY KEY,
            sito TEXT NOT NULL,
            nazione TEXT,
            regione TEXT,
            comune TEXT,
            descrizione TEXT,
            find_check INTEGER
        )
    """)
    cur.execute("INSERT INTO site_table VALUES (1, 'Castelseprio', 'IT', 'Lombardia', 'CS', 'desc', 0)")

    cur.execute("""
        CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY,
            sito TEXT,
            area TEXT,
            us INTEGER,
            d_stratigrafica TEXT
        )
    """)
    cur.execute("INSERT INTO us_table VALUES (1, 'Castelseprio', 'A', 1, 'strato')")

    # QGIS pottery_table EXACT schema (no sync cols)
    cur.execute("""
        CREATE TABLE pottery_table (
            id_rep INTEGER PRIMARY KEY,
            id_number INTEGER,
            sito TEXT,
            area TEXT,
            us INTEGER,
            box INTEGER,
            photo TEXT,
            drawing TEXT,
            anno INTEGER,
            fabric TEXT,
            percent TEXT,
            material TEXT,
            form TEXT,
            specific_form TEXT,
            ware TEXT,
            munsell TEXT,
            surf_trat TEXT,
            exdeco TEXT,
            intdeco TEXT,
            wheel_made TEXT,
            descrip_ex_deco TEXT,
            descrip_in_deco TEXT,
            note TEXT,
            diametro_max NUMERIC(7,3),
            qty INTEGER,
            diametro_rim NUMERIC(7,3),
            diametro_bottom NUMERIC(7,3),
            diametro_height NUMERIC(7,3),
            diametro_preserved NUMERIC(7,3),
            specific_shape TEXT,
            bag INTEGER,
            sector TEXT,
            UNIQUE (sito, id_number)
        )
    """)
    cur.executemany(
        "INSERT INTO pottery_table VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (1, 101, 'Castelseprio', 'A', 1, 5, '/leg/p1.jpg', '/leg/d1.png',
             2023, 'Coarse', '80%', 'Ceramica', 'Olla', 'Olla A', 'African RS',
             '7.5YR 5/6', 'lisciata', 'liscia', 'liscia', 'Yes',
             'esterno liscio', 'interno liscio', 'integra',
             14.5, 1, 12.0, 6.0, 18.0, 100.0, 'A1', 3, 'NE'),
            (2, 102, 'Castelseprio', 'A', 1, 5, None, None,
             2023, 'Fine', '20%', 'Ceramica', 'Ciotola', None, 'TS',
             '5YR 6/8', 'depurata', None, None, 'Indeterminate',
             None, None, 'frammento di orlo',
             8.0, 2, 8.0, None, None, 30.0, 'B2', 4, 'NE'),
        ],
    )
    conn.commit()
    conn.close()
    print(f"Built fixture: {FIXTURE}")

if __name__ == "__main__":
    build()
```

- [ ] **Step 3: Generate the fixture**

Run:
```bash
python tests/fixtures/build_legacy_with_pottery.py
```

Expected:
```
Built fixture: tests/fixtures/legacy_with_pottery.sqlite
```

- [ ] **Step 4: Commit fixture builder and binary**

```bash
git add tests/fixtures/build_legacy_with_pottery.py tests/fixtures/legacy_with_pottery.sqlite
git commit -m "test: legacy QGIS pottery fixture for upgrade tests"
```

---

## Task 1: `Pottery` SQLAlchemy model

**Files:**
- Create: `pyarchinit_mini/models/pottery.py`
- Modify: `pyarchinit_mini/models/__init__.py`
- Test: `tests/unit/test_pottery_model.py`

- [ ] **Step 1: Write failing test**

Create `tests/unit/test_pottery_model.py`:

```python
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from pyarchinit_mini.models.base import Base
from pyarchinit_mini.models.pottery import Pottery


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    s = SessionLocal()
    yield s
    s.close()


def test_pottery_has_all_qgis_columns():
    cols = {c.name for c in Pottery.__table__.columns}
    qgis_cols = {
        "id_rep", "id_number", "sito", "area", "us", "box", "photo",
        "drawing", "anno", "fabric", "percent", "material", "form",
        "specific_form", "ware", "munsell", "surf_trat", "exdeco",
        "intdeco", "wheel_made", "descrip_ex_deco", "descrip_in_deco",
        "note", "diametro_max", "qty", "diametro_rim", "diametro_bottom",
        "diametro_height", "diametro_preserved", "specific_shape", "bag",
        "sector",
    }
    assert qgis_cols.issubset(cols), f"Missing: {qgis_cols - cols}"


def test_pottery_has_sync_columns():
    cols = {c.name for c in Pottery.__table__.columns}
    sync_cols = {
        "created_at", "updated_at", "entity_uuid", "version_number",
        "last_modified_by", "last_modified_timestamp",
        "sync_status", "editing_by", "editing_since",
    }
    assert sync_cols.issubset(cols), f"Missing sync: {sync_cols - cols}"


def test_pottery_unique_constraint_sito_id_number(session):
    p1 = Pottery(sito="X", id_number=1, form="Olla")
    p2 = Pottery(sito="X", id_number=1, form="Ciotola")
    session.add(p1)
    session.commit()
    session.add(p2)
    with pytest.raises(IntegrityError):
        session.commit()


def test_pottery_can_save_and_load(session):
    p = Pottery(
        sito="X", id_number=42, area="A", us=10,
        form="Olla", fabric="Coarse", qty=3,
        diametro_max=15.5,
    )
    session.add(p)
    session.commit()
    loaded = session.query(Pottery).filter_by(id_number=42).first()
    assert loaded is not None
    assert loaded.sito == "X"
    assert loaded.qty == 3
    assert loaded.entity_uuid is not None
    assert loaded.version_number == 1
    assert loaded.sync_status == "new"


def test_pottery_indexes_present():
    indexes = {idx.name for idx in Pottery.__table__.indexes}
    assert "ix_pottery_sito_area_us" in indexes
    assert "ix_pottery_form" in indexes
    assert "ix_pottery_fabric" in indexes
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_pottery_model.py -v`
Expected: `ModuleNotFoundError: No module named 'pyarchinit_mini.models.pottery'`

- [ ] **Step 3: Implement the model**

Create `pyarchinit_mini/models/pottery.py`:

```python
"""
Pottery model — 1:1 schema parity with PyArchInit-QGIS pottery_table.

Inherits sync/audit columns from BaseModel:
- created_at, updated_at
- entity_uuid, version_number
- last_modified_by, last_modified_timestamp
- sync_status, editing_by, editing_since
"""
from sqlalchemy import Column, Integer, Text, Numeric, UniqueConstraint, Index

from .base import BaseModel


class Pottery(BaseModel):
    __tablename__ = "pottery_table"

    # 32 columns mirroring PyArchInit-QGIS Pottery_table.py
    id_rep = Column(Integer, primary_key=True, autoincrement=True)
    id_number = Column(Integer, nullable=True)
    sito = Column(Text, nullable=False)
    area = Column(Text)
    us = Column(Integer)
    box = Column(Integer)
    photo = Column(Text)
    drawing = Column(Text)
    anno = Column(Integer)
    fabric = Column(Text)
    percent = Column(Text)
    material = Column(Text)
    form = Column(Text)
    specific_form = Column(Text)
    ware = Column(Text)
    munsell = Column(Text)
    surf_trat = Column(Text)
    exdeco = Column(Text)
    intdeco = Column(Text)
    wheel_made = Column(Text)
    descrip_ex_deco = Column(Text)
    descrip_in_deco = Column(Text)
    note = Column(Text)
    diametro_max = Column(Numeric(7, 3))
    qty = Column(Integer)
    diametro_rim = Column(Numeric(7, 3))
    diametro_bottom = Column(Numeric(7, 3))
    diametro_height = Column(Numeric(7, 3))
    diametro_preserved = Column(Numeric(7, 3))
    specific_shape = Column(Text)
    bag = Column(Integer)
    sector = Column(Text)

    __table_args__ = (
        UniqueConstraint("sito", "id_number", name="ID_rep_unico"),
        Index("ix_pottery_sito_area_us", "sito", "area", "us"),
        Index("ix_pottery_form", "form"),
        Index("ix_pottery_fabric", "fabric"),
    )

    def __repr__(self) -> str:
        return (
            f"<Pottery id_rep={self.id_rep} sito={self.sito!r} "
            f"id_number={self.id_number} form={self.form!r}>"
        )
```

- [ ] **Step 4: Register in models package**

Edit `pyarchinit_mini/models/__init__.py` — append after line 14:

```python
from .pottery import Pottery
```

And update `__all__` if present, e.g. add `"Pottery"`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/unit/test_pottery_model.py -v`
Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/models/pottery.py pyarchinit_mini/models/__init__.py tests/unit/test_pottery_model.py
git commit -m "feat(model): add Pottery model matching PyArchInit-QGIS pottery_table"
```

---

## Task 2: `PotteryDTO` dataclass

**Files:**
- Create: `pyarchinit_mini/services/pottery_dto.py`
- Test: `tests/unit/test_pottery_dto.py`

- [ ] **Step 1: Write failing test**

Create `tests/unit/test_pottery_dto.py`:

```python
from datetime import datetime, timezone
from pyarchinit_mini.models.pottery import Pottery
from pyarchinit_mini.services.pottery_dto import PotteryDTO


def test_dto_round_trip_from_model():
    p = Pottery(
        id_rep=1, id_number=42, sito="X", area="A", us=10, box=2, anno=2024,
        form="Olla", fabric="Coarse", qty=3, diametro_max=15.5,
    )
    dto = PotteryDTO.from_model(p)
    assert dto.id_rep == 1
    assert dto.sito == "X"
    assert dto.form == "Olla"
    assert dto.diametro_max == 15.5
    d = dto.to_dict()
    assert d["sito"] == "X"
    assert d["qty"] == 3


def test_dto_handles_all_qgis_fields():
    qgis_fields = {
        "id_rep", "id_number", "sito", "area", "us", "box", "photo",
        "drawing", "anno", "fabric", "percent", "material", "form",
        "specific_form", "ware", "munsell", "surf_trat", "exdeco",
        "intdeco", "wheel_made", "descrip_ex_deco", "descrip_in_deco",
        "note", "diametro_max", "qty", "diametro_rim", "diametro_bottom",
        "diametro_height", "diametro_preserved", "specific_shape", "bag",
        "sector",
    }
    dto_fields = {f for f in PotteryDTO.__dataclass_fields__.keys()}
    assert qgis_fields.issubset(dto_fields)
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_pottery_dto.py -v`
Expected: `ModuleNotFoundError: No module named 'pyarchinit_mini.services.pottery_dto'`

- [ ] **Step 3: Implement DTO**

Create `pyarchinit_mini/services/pottery_dto.py`:

```python
"""Data Transfer Object for Pottery records."""
from __future__ import annotations

from dataclasses import dataclass, fields, asdict
from datetime import datetime
from decimal import Decimal
from typing import Optional


def _to_float(v):
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    return v


@dataclass
class PotteryDTO:
    id_rep: Optional[int] = None
    id_number: Optional[int] = None
    sito: Optional[str] = None
    area: Optional[str] = None
    us: Optional[int] = None
    box: Optional[int] = None
    photo: Optional[str] = None
    drawing: Optional[str] = None
    anno: Optional[int] = None
    fabric: Optional[str] = None
    percent: Optional[str] = None
    material: Optional[str] = None
    form: Optional[str] = None
    specific_form: Optional[str] = None
    ware: Optional[str] = None
    munsell: Optional[str] = None
    surf_trat: Optional[str] = None
    exdeco: Optional[str] = None
    intdeco: Optional[str] = None
    wheel_made: Optional[str] = None
    descrip_ex_deco: Optional[str] = None
    descrip_in_deco: Optional[str] = None
    note: Optional[str] = None
    diametro_max: Optional[float] = None
    qty: Optional[int] = None
    diametro_rim: Optional[float] = None
    diametro_bottom: Optional[float] = None
    diametro_height: Optional[float] = None
    diametro_preserved: Optional[float] = None
    specific_shape: Optional[str] = None
    bag: Optional[int] = None
    sector: Optional[str] = None

    # Sync / audit
    entity_uuid: Optional[str] = None
    version_number: Optional[int] = None
    sync_status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_model(cls, m) -> "PotteryDTO":
        kw = {}
        names = {f.name for f in fields(cls)}
        for n in names:
            v = getattr(m, n, None)
            if n.startswith("diametro_"):
                v = _to_float(v)
            kw[n] = v
        return cls(**kw)

    def to_dict(self) -> dict:
        return asdict(self)
```

- [ ] **Step 4: Run tests to verify pass**

Run: `pytest tests/unit/test_pottery_dto.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/services/pottery_dto.py tests/unit/test_pottery_dto.py
git commit -m "feat(service): add PotteryDTO with QGIS-aligned fields"
```

---

## Task 3: `PotteryService` create + validation

**Files:**
- Create: `pyarchinit_mini/services/pottery_service.py`
- Modify: `pyarchinit_mini/services/__init__.py`
- Test: `tests/unit/test_pottery_service.py`

- [ ] **Step 1: Write failing test (create + validation)**

Create `tests/unit/test_pottery_service.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.models.base import Base
from pyarchinit_mini.models.pottery import Pottery
from pyarchinit_mini.services.pottery_service import PotteryService


@pytest.fixture
def db_manager():
    """In-memory DatabaseManager."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    mgr = DatabaseManager.__new__(DatabaseManager)
    mgr.engine = engine
    mgr.SessionLocal = sessionmaker(bind=engine)
    return mgr


@pytest.fixture
def svc(db_manager):
    return PotteryService(db_manager)


def test_create_pottery_minimal(svc):
    p = svc.create_pottery({"sito": "X", "form": "Olla"})
    assert p.id_rep is not None
    assert p.sito == "X"
    assert p.form == "Olla"


def test_create_pottery_requires_sito(svc):
    with pytest.raises(ValueError, match="sito"):
        svc.create_pottery({"form": "Olla"})


def test_create_pottery_qty_must_be_positive(svc):
    with pytest.raises(ValueError, match="qty"):
        svc.create_pottery({"sito": "X", "qty": 0})
    with pytest.raises(ValueError, match="qty"):
        svc.create_pottery({"sito": "X", "qty": -1})


def test_create_pottery_rejects_duplicate_sito_id_number(svc):
    svc.create_pottery({"sito": "X", "id_number": 1})
    with pytest.raises(ValueError, match="already exists"):
        svc.create_pottery({"sito": "X", "id_number": 1})
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_pottery_service.py -v`
Expected: ModuleNotFoundError for pottery_service.

- [ ] **Step 3: Implement minimal service**

Create `pyarchinit_mini/services/pottery_service.py`:

```python
"""Pottery records service (CRUD + listing + stats)."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, or_

from ..database.manager import DatabaseManager
from ..models.pottery import Pottery
from .pottery_dto import PotteryDTO

logger = logging.getLogger(__name__)

_POTTERY_COLUMNS = {c.name for c in Pottery.__table__.columns}


class PotteryService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    # ---------- CRUD ----------
    def create_pottery(self, data: Dict[str, Any]) -> Pottery:
        clean = self._validate_and_clean(data)
        if clean.get("id_number") is not None:
            self._validate_unique_sito_idnumber(clean["sito"], clean["id_number"])
        session = self.db.SessionLocal()
        try:
            p = Pottery(**{k: v for k, v in clean.items() if k in _POTTERY_COLUMNS})
            session.add(p)
            session.commit()
            session.refresh(p)
            return p
        finally:
            session.close()

    # ---------- Validation ----------
    def _validate_and_clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get("sito"):
            raise ValueError("sito is required")
        qty = data.get("qty")
        if qty is not None and qty != "":
            try:
                qi = int(qty)
            except (TypeError, ValueError):
                raise ValueError("qty must be an integer")
            if qi < 1:
                raise ValueError("qty must be >= 1")
            data["qty"] = qi
        return data

    def _validate_unique_sito_idnumber(
        self, sito: str, id_number: int, exclude_id: Optional[int] = None
    ) -> None:
        session = self.db.SessionLocal()
        try:
            q = session.query(Pottery).filter(
                Pottery.sito == sito, Pottery.id_number == id_number
            )
            if exclude_id is not None:
                q = q.filter(Pottery.id_rep != exclude_id)
            existing = q.first()
            if existing is not None:
                raise ValueError(
                    f"Pottery with sito={sito!r} id_number={id_number} already exists"
                )
        finally:
            session.close()
```

- [ ] **Step 4: Register service in package**

Edit `pyarchinit_mini/services/__init__.py` — append:

```python
from .pottery_service import PotteryService  # noqa: F401
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/unit/test_pottery_service.py -v`
Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/services/pottery_service.py pyarchinit_mini/services/__init__.py tests/unit/test_pottery_service.py
git commit -m "feat(service): PotteryService.create_pottery with validation"
```

---

## Task 4: Service CRUD (get / update / delete)

**Files:**
- Modify: `pyarchinit_mini/services/pottery_service.py`
- Modify: `tests/unit/test_pottery_service.py`

- [ ] **Step 1: Append failing tests to `tests/unit/test_pottery_service.py`**

Append:

```python
def test_get_pottery_by_id(svc):
    p = svc.create_pottery({"sito": "X", "form": "Olla"})
    fetched = svc.get_pottery_by_id(p.id_rep)
    assert fetched is not None
    assert fetched.id_rep == p.id_rep


def test_get_pottery_by_id_missing(svc):
    assert svc.get_pottery_by_id(99999) is None


def test_get_pottery_dto_by_id(svc):
    p = svc.create_pottery({"sito": "X", "form": "Olla", "qty": 2})
    dto = svc.get_pottery_dto_by_id(p.id_rep)
    assert dto is not None
    assert dto.sito == "X"
    assert dto.qty == 2


def test_update_pottery(svc):
    p = svc.create_pottery({"sito": "X", "form": "Olla"})
    u = svc.update_pottery(p.id_rep, {"form": "Ciotola", "qty": 5})
    assert u.form == "Ciotola"
    assert u.qty == 5


def test_update_pottery_missing_raises(svc):
    with pytest.raises(ValueError, match="not found"):
        svc.update_pottery(99999, {"form": "X"})


def test_update_does_not_break_unique_constraint(svc):
    a = svc.create_pottery({"sito": "X", "id_number": 1})
    b = svc.create_pottery({"sito": "X", "id_number": 2})
    with pytest.raises(ValueError, match="already exists"):
        svc.update_pottery(b.id_rep, {"id_number": 1})


def test_delete_pottery(svc):
    p = svc.create_pottery({"sito": "X", "form": "Olla"})
    assert svc.delete_pottery(p.id_rep) is True
    assert svc.get_pottery_by_id(p.id_rep) is None


def test_delete_pottery_missing_returns_false(svc):
    assert svc.delete_pottery(99999) is False
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/unit/test_pottery_service.py -v -k "get_ or update_ or delete_"`
Expected: AttributeError or NameError for the new methods.

- [ ] **Step 3: Implement CRUD methods**

Append to `pyarchinit_mini/services/pottery_service.py` (inside class body, after `_validate_unique_sito_idnumber`):

```python
    # ---------- Read ----------
    def get_pottery_by_id(self, id_rep: int) -> Optional[Pottery]:
        session = self.db.SessionLocal()
        try:
            return session.query(Pottery).filter(Pottery.id_rep == id_rep).first()
        finally:
            session.close()

    def get_pottery_dto_by_id(self, id_rep: int) -> Optional[PotteryDTO]:
        p = self.get_pottery_by_id(id_rep)
        return PotteryDTO.from_model(p) if p else None

    # ---------- Update / Delete ----------
    def update_pottery(self, id_rep: int, data: Dict[str, Any]) -> Pottery:
        session = self.db.SessionLocal()
        try:
            p = session.query(Pottery).filter(Pottery.id_rep == id_rep).first()
            if p is None:
                raise ValueError(f"Pottery id_rep={id_rep} not found")
            new_sito = data.get("sito", p.sito)
            new_idn = data.get("id_number", p.id_number)
            if new_idn is not None and (new_sito != p.sito or new_idn != p.id_number):
                self._validate_unique_sito_idnumber(new_sito, new_idn, exclude_id=id_rep)
            if "qty" in data and data["qty"] not in (None, ""):
                try:
                    q = int(data["qty"])
                except (TypeError, ValueError):
                    raise ValueError("qty must be an integer")
                if q < 1:
                    raise ValueError("qty must be >= 1")
                data["qty"] = q
            for k, v in data.items():
                if k in _POTTERY_COLUMNS:
                    setattr(p, k, v)
            session.commit()
            session.refresh(p)
            return p
        finally:
            session.close()

    def delete_pottery(self, id_rep: int) -> bool:
        session = self.db.SessionLocal()
        try:
            p = session.query(Pottery).filter(Pottery.id_rep == id_rep).first()
            if p is None:
                return False
            session.delete(p)
            session.commit()
            return True
        finally:
            session.close()
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/unit/test_pottery_service.py -v`
Expected: 12 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/services/pottery_service.py tests/unit/test_pottery_service.py
git commit -m "feat(service): PotteryService get / update / delete"
```

---

## Task 5: Service listing, filtering, search

**Files:**
- Modify: `pyarchinit_mini/services/pottery_service.py`
- Modify: `tests/unit/test_pottery_service.py`

- [ ] **Step 1: Append failing tests**

Append to `tests/unit/test_pottery_service.py`:

```python
@pytest.fixture
def populated(svc):
    svc.create_pottery({"sito": "X", "area": "A", "us": 1, "form": "Olla", "fabric": "Coarse", "qty": 5})
    svc.create_pottery({"sito": "X", "area": "A", "us": 2, "form": "Ciotola", "fabric": "Fine", "qty": 1})
    svc.create_pottery({"sito": "Y", "area": "B", "us": 1, "form": "Olla", "fabric": "Coarse", "qty": 2})
    return svc


def test_get_all_pottery_paginated(populated):
    items, total = populated.get_all_pottery(page=1, size=2)
    assert total == 3
    assert len(items) == 2


def test_get_all_pottery_filter_by_sito(populated):
    items, total = populated.get_all_pottery(filters={"sito": "X"})
    assert total == 2
    assert all(i.sito == "X" for i in items)


def test_get_all_pottery_filter_combined(populated):
    items, total = populated.get_all_pottery(filters={"sito": "X", "form": "Olla"})
    assert total == 1


def test_count_pottery(populated):
    assert populated.count_pottery() == 3
    assert populated.count_pottery({"form": "Olla"}) == 2


def test_search_pottery_text(populated):
    items = populated.search_pottery("Cias")  # case-insensitive substring
    # nothing matches
    assert items == []
    items = populated.search_pottery("Olla")
    assert len(items) == 2


def test_get_pottery_by_site(populated):
    items = populated.get_pottery_by_site("Y")
    assert len(items) == 1
    assert items[0].sito == "Y"


def test_get_pottery_by_us(populated):
    items = populated.get_pottery_by_us("X", "A", 1)
    assert len(items) == 1


def test_get_pottery_by_form(populated):
    items = populated.get_pottery_by_form("Olla")
    assert len(items) == 2
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/unit/test_pottery_service.py -v -k "get_all or count_pott or search_ or by_site or by_us or by_form"`
Expected: AttributeError on the new methods.

- [ ] **Step 3: Implement listing methods**

Append inside `PotteryService` class in `pyarchinit_mini/services/pottery_service.py`:

```python
    # ---------- Listing & Filtering ----------
    _FILTERABLE = ("sito", "area", "us", "form", "fabric", "ware", "material")

    def _apply_filters(self, q, filters: Optional[Dict[str, Any]]):
        if not filters:
            return q
        for k in self._FILTERABLE:
            v = filters.get(k)
            if v in (None, ""):
                continue
            col = getattr(Pottery, k)
            q = q.filter(col == v)
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

    def get_all_pottery(
        self, page: int = 1, size: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Pottery], int]:
        session = self.db.SessionLocal()
        try:
            q = session.query(Pottery)
            q = self._apply_filters(q, filters)
            total = q.count()
            items = q.order_by(Pottery.id_rep.desc()).offset((page - 1) * size).limit(size).all()
            return items, total
        finally:
            session.close()

    def count_pottery(self, filters: Optional[Dict[str, Any]] = None) -> int:
        session = self.db.SessionLocal()
        try:
            q = session.query(Pottery)
            q = self._apply_filters(q, filters)
            return q.count()
        finally:
            session.close()

    def search_pottery(self, q_text: str, page: int = 1, size: int = 10) -> List[Pottery]:
        items, _ = self.get_all_pottery(page=page, size=size, filters={"q": q_text})
        return items

    def get_pottery_by_site(self, sito: str, page: int = 1, size: int = 10) -> List[Pottery]:
        items, _ = self.get_all_pottery(page=page, size=size, filters={"sito": sito})
        return items

    def get_pottery_by_us(
        self, sito: str, area: Optional[str], us: int,
        page: int = 1, size: int = 10
    ) -> List[Pottery]:
        items, _ = self.get_all_pottery(
            page=page, size=size, filters={"sito": sito, "area": area, "us": us}
        )
        return items

    def get_pottery_by_form(self, form: str, page: int = 1, size: int = 10) -> List[Pottery]:
        items, _ = self.get_all_pottery(page=page, size=size, filters={"form": form})
        return items
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/unit/test_pottery_service.py -v`
Expected: 20 passed (all earlier + 8 new).

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/services/pottery_service.py tests/unit/test_pottery_service.py
git commit -m "feat(service): PotteryService listing, filtering, search"
```

---

## Task 6: Service stats + MNI

**Files:**
- Modify: `pyarchinit_mini/services/pottery_service.py`
- Modify: `tests/unit/test_pottery_service.py`

- [ ] **Step 1: Append failing tests**

Append to `tests/unit/test_pottery_service.py`:

```python
def test_form_distribution(populated):
    dist = populated.get_form_distribution()
    assert dist["Olla"] == 2
    assert dist["Ciotola"] == 1


def test_fabric_distribution_scoped_by_site(populated):
    dist = populated.get_fabric_distribution(sito="X")
    assert dist["Coarse"] == 1
    assert dist["Fine"] == 1


def test_count_by_site(populated):
    rows = populated.count_by_site()
    by_site = {r["sito"]: r["count"] for r in rows}
    assert by_site["X"] == 2
    assert by_site["Y"] == 1


def test_calculate_mni(populated):
    # MNI groups by (form, fabric, ware) summing qty
    mni = populated.calculate_mni(sito="X")
    # (Olla, Coarse, None) qty=5 and (Ciotola, Fine, None) qty=1
    assert mni["total"] == 6
    assert len(mni["groups"]) == 2
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/unit/test_pottery_service.py -v -k "distribution or count_by or calculate_mni"`
Expected: AttributeError.

- [ ] **Step 3: Implement stats methods**

Append inside `PotteryService`:

```python
    # ---------- Stats ----------
    def _distribution(self, column_name: str, sito: Optional[str] = None) -> Dict[str, int]:
        session = self.db.SessionLocal()
        try:
            col = getattr(Pottery, column_name)
            q = session.query(col, func.count(Pottery.id_rep)).group_by(col)
            if sito:
                q = q.filter(Pottery.sito == sito)
            return {k: c for k, c in q.all() if k is not None}
        finally:
            session.close()

    def get_form_distribution(self, sito: Optional[str] = None) -> Dict[str, int]:
        return self._distribution("form", sito)

    def get_fabric_distribution(self, sito: Optional[str] = None) -> Dict[str, int]:
        return self._distribution("fabric", sito)

    def get_ware_distribution(self, sito: Optional[str] = None) -> Dict[str, int]:
        return self._distribution("ware", sito)

    def count_by_site(self) -> List[Dict[str, Any]]:
        session = self.db.SessionLocal()
        try:
            rows = (
                session.query(Pottery.sito, func.count(Pottery.id_rep))
                .group_by(Pottery.sito)
                .all()
            )
            return [{"sito": s, "count": c} for s, c in rows]
        finally:
            session.close()

    def calculate_mni(
        self, sito: str, area: Optional[str] = None, us: Optional[int] = None
    ) -> Dict[str, Any]:
        """Minimum Number of Individuals — sum of qty grouped by form+fabric+ware."""
        session = self.db.SessionLocal()
        try:
            q = session.query(
                Pottery.form, Pottery.fabric, Pottery.ware,
                func.coalesce(func.sum(Pottery.qty), 0),
            ).filter(Pottery.sito == sito)
            if area:
                q = q.filter(Pottery.area == area)
            if us is not None:
                q = q.filter(Pottery.us == us)
            q = q.group_by(Pottery.form, Pottery.fabric, Pottery.ware)
            groups = [
                {"form": f, "fabric": fa, "ware": w, "mni": int(s or 0)}
                for f, fa, w, s in q.all()
            ]
            total = sum(g["mni"] for g in groups)
            return {"total": total, "groups": groups}
        finally:
            session.close()
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/unit/test_pottery_service.py -v`
Expected: 24 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/services/pottery_service.py tests/unit/test_pottery_service.py
git commit -m "feat(service): PotteryService stats + MNI"
```

---

## Task 7: Wire Pottery into migrations + legacy upgrade

**Files:**
- Modify: `pyarchinit_mini/database/migrations.py`
- Test: `tests/integration/test_pottery_legacy_upgrade.py`

- [ ] **Step 1: Write failing integration test**

Create `tests/integration/test_pottery_legacy_upgrade.py`:

```python
"""
Verify upgrade_legacy_schema picks up pottery_table:
- Existing legacy rows preserved
- Sync columns added with backfill
- Missing legacy table created from scratch on a DB without pottery
"""
import shutil
import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

from pyarchinit_mini.services.import_export_service import ImportExportService

FIXTURE = Path("tests/fixtures/legacy_with_pottery.sqlite")


@pytest.fixture
def legacy_db(tmp_path):
    dst = tmp_path / "legacy.sqlite"
    shutil.copy(FIXTURE, dst)
    return dst


def test_upgrade_preserves_pottery_rows(legacy_db):
    db_url = f"sqlite:///{legacy_db}"
    stats = ImportExportService.upgrade_legacy_schema(db_url)
    assert "pottery_table" in stats.get("added_per_table", {}) or \
           "pottery_table" in stats.get("created_tables", [])
    # Re-open and verify rows survived + sync cols present
    conn = sqlite3.connect(legacy_db)
    cur = conn.cursor()
    rows = cur.execute("SELECT id_rep, sito, id_number FROM pottery_table ORDER BY id_rep").fetchall()
    assert rows == [(1, "Castelseprio", 101), (2, "Castelseprio", 102)]
    cols = [r[1] for r in cur.execute("PRAGMA table_info(pottery_table)").fetchall()]
    for sync in ("entity_uuid", "version_number", "sync_status",
                 "created_at", "updated_at"):
        assert sync in cols, f"Missing sync column {sync}"
    # entity_uuid backfilled non-null
    null_uuids = cur.execute("SELECT COUNT(*) FROM pottery_table WHERE entity_uuid IS NULL").fetchone()[0]
    assert null_uuids == 0
    conn.close()


def test_upgrade_creates_pottery_when_missing(tmp_path):
    """A legacy DB that lacks pottery_table entirely should get it created."""
    db_path = tmp_path / "no_pottery.sqlite"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY, sito TEXT)")
    conn.execute("INSERT INTO site_table VALUES (1, 'TestSite')")
    conn.commit()
    conn.close()

    db_url = f"sqlite:///{db_path}"
    stats = ImportExportService.upgrade_legacy_schema(db_url)
    assert "pottery_table" in stats.get("created_tables", []) or \
           stats.get("tables_created", 0) > 0

    engine = create_engine(db_url)
    insp = inspect(engine)
    assert "pottery_table" in insp.get_table_names()
```

- [ ] **Step 2: Run test to verify failure (or pass — depends on metadata wiring)**

Run: `pytest tests/integration/test_pottery_legacy_upgrade.py -v`

Expected: FAIL — `pottery_table` is not in `Base.metadata` until Task 1's `__init__.py` import is loaded by `import_export_service`. If `import_export_service` doesn't import models, the test will fail here.

- [ ] **Step 3: Verify models import path**

Run:
```bash
grep -nE "from .*models|import.*Base" pyarchinit_mini/services/import_export_service.py | head -5
```

Note: Confirm that `import_export_service.py` already imports a path that triggers loading `pyarchinit_mini/models/__init__.py` (and thus registers `Pottery` in `Base.metadata`). If not, add at the top of `import_export_service.py`:

```python
from ..models import Pottery  # noqa: F401 — ensure Pottery is registered in Base.metadata
```

(Only edit if grep showed no model import path. Most likely it already imports site/us/inventario etc., so a wildcard models import is enough — verify.)

- [ ] **Step 4: Update migrations.py to ensure pottery is created on boot**

Edit `pyarchinit_mini/database/migrations.py`:

Find the section that calls `Base.metadata.create_all` (search `create_all` in the file). Pottery will be picked up automatically once it is in `Base.metadata`. If there is a hardcoded `tables_to_create` list, append `Pottery.__table__`.

Add a defensive import near the top of `migrations.py`:

```python
from ..models import Pottery  # noqa: F401 — ensure pottery_table registered for create_all
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/integration/test_pottery_legacy_upgrade.py -v`
Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/database/migrations.py pyarchinit_mini/services/import_export_service.py tests/integration/test_pottery_legacy_upgrade.py
git commit -m "feat: wire pottery_table into migrations and legacy upgrade"
```

---

## Task 8: Add pottery_table to migrate-database wizard

**Files:**
- Modify: `pyarchinit_mini/services/import_export_service.py:1963-1982`

- [ ] **Step 1: Edit `tables_order` list**

In `pyarchinit_mini/services/import_export_service.py` around lines 1963–1982, replace:

```python
            tables_order = [
                'users',
                'site_table',
                'datazioni_table',
                'us_table',
                'us_relationships_table',
                'period_table',
                'periodizzazione_table',
                'pyarchinit_thesaurus_sigle',
                'thesaurus_field',
                'thesaurus_category',
                'inventario_materiali_table',
                'media_table',
                'media_thumb_table',
                'documentation_table',
                'harris_matrix_table',
                'extended_matrix_table',
                'tma_materiali_archeologici',
                'tma_materiali_ripetibili',
            ]
```

With:

```python
            tables_order = [
                'users',
                'site_table',
                'datazioni_table',
                'us_table',
                'us_relationships_table',
                'period_table',
                'periodizzazione_table',
                'pyarchinit_thesaurus_sigle',
                'thesaurus_field',
                'thesaurus_category',
                'inventario_materiali_table',
                'pottery_table',
                'media_table',
                'media_thumb_table',
                'documentation_table',
                'harris_matrix_table',
                'extended_matrix_table',
                'tma_materiali_archeologici',
                'tma_materiali_ripetibili',
            ]
```

`pottery_table` is positioned after `inventario_materiali_table` so any site/us referenced is already in the target.

- [ ] **Step 2: Verify the edit**

Run:
```bash
grep -A1 "inventario_materiali_table" pyarchinit_mini/services/import_export_service.py | head -5
```

Expected: line after `'inventario_materiali_table',` contains `'pottery_table',`.

- [ ] **Step 3: Commit**

```bash
git add pyarchinit_mini/services/import_export_service.py
git commit -m "feat(migrate): add pottery_table to migrate-database order"
```

---

## Task 9: Web routes scaffold

**Files:**
- Create: `pyarchinit_mini/web_interface/pottery_routes.py`
- Modify: `pyarchinit_mini/web_interface/app.py`

- [ ] **Step 1: Locate app.py registration point**

Run:
```bash
grep -nE "def create_app|_register_.*_routes|register_blueprint" pyarchinit_mini/web_interface/app.py | head -15
```

Note the function pattern used (probably `register_blueprint` or inline routes inside `create_app`).

- [ ] **Step 2: Create routes scaffold**

Create `pyarchinit_mini/web_interface/pottery_routes.py`:

```python
"""Pottery web routes. Call _register_pottery_routes(app) from create_app()."""
from __future__ import annotations

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort,
)
from flask_login import login_required, current_user

from ..services.pottery_service import PotteryService
from ..services.pottery_dto import PotteryDTO


def _register_pottery_routes(app):
    """Register pottery URL rules on the Flask app."""

    @app.route("/pottery")
    @login_required
    def pottery_list():
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 25))
        filters = {
            k: request.args.get(k)
            for k in ("sito", "area", "us", "form", "fabric", "ware", "q")
            if request.args.get(k)
        }
        if "us" in filters:
            try:
                filters["us"] = int(filters["us"])
            except ValueError:
                filters.pop("us")
        svc = PotteryService(app.db_manager)
        items, total = svc.get_all_pottery(page=page, size=size, filters=filters)
        return render_template(
            "pottery/list.html",
            items=[PotteryDTO.from_model(p) for p in items],
            total=total, page=page, size=size, filters=filters,
        )
```

- [ ] **Step 3: Wire it into `create_app`**

Find `def create_app` in `pyarchinit_mini/web_interface/app.py`. Just before the function returns the `app`, append:

```python
    from .pottery_routes import _register_pottery_routes
    _register_pottery_routes(app)
```

(Import is local to avoid load-order issues.)

- [ ] **Step 4: Smoke test that the app still imports**

Run:
```bash
python -c "from pyarchinit_mini.web_interface.app import create_app; print('OK')"
```

Expected: `OK`. If it errors, fix circular imports.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/pottery_routes.py pyarchinit_mini/web_interface/app.py
git commit -m "feat(web): pottery routes scaffold + list endpoint"
```

---

## Task 10: List template

**Files:**
- Create: `pyarchinit_mini/web_interface/templates/pottery/list.html`
- Test: `tests/integration/test_pottery_routes.py`

- [ ] **Step 1: Write failing integration test**

Create `tests/integration/test_pottery_routes.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.models.base import Base
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.pottery_service import PotteryService
from pyarchinit_mini.web_interface.app import create_app


@pytest.fixture
def app(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path/'t.sqlite'}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    a = create_app()
    a.config["TESTING"] = True
    a.config["LOGIN_DISABLED"] = True  # bypass @login_required for these tests
    return a


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def svc(app):
    return PotteryService(app.db_manager)


def test_list_page_renders(client, svc):
    svc.create_pottery({"sito": "X", "form": "Olla", "qty": 1})
    r = client.get("/pottery")
    assert r.status_code == 200
    assert b"Pottery" in r.data
    assert b"Olla" in r.data


def test_list_page_filter_by_sito(client, svc):
    svc.create_pottery({"sito": "X", "form": "Olla"})
    svc.create_pottery({"sito": "Y", "form": "Ciotola"})
    r = client.get("/pottery?sito=X")
    assert r.status_code == 200
    assert b"Olla" in r.data
    assert b"Ciotola" not in r.data
```

- [ ] **Step 2: Run test**

Run: `pytest tests/integration/test_pottery_routes.py -v`
Expected: TemplateNotFound: `pottery/list.html`.

- [ ] **Step 3: Implement template**

Create `pyarchinit_mini/web_interface/templates/pottery/list.html`:

```jinja2
{% extends "base.html" %}
{% block title %}Pottery{% endblock %}

{% block content %}
<div class="container-fluid mt-3">
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h1>Pottery <small class="text-muted">({{ total }})</small></h1>
    <div>
      <a href="{{ url_for('pottery_create') }}" class="btn btn-primary">+ Nuovo</a>
      <a href="{{ url_for('pottery_export_excel', **filters) }}" class="btn btn-outline-success">Excel</a>
      <a href="{{ url_for('pottery_export_csv', **filters) }}" class="btn btn-outline-secondary">CSV</a>
      <a href="{{ url_for('pottery_export_pdf', **filters) }}" class="btn btn-outline-danger">PDF</a>
      <a href="{{ url_for('pottery_import_form') }}" class="btn btn-outline-info">Import</a>
    </div>
  </div>

  <form method="get" class="row g-2 mb-3">
    <div class="col-md-2"><input class="form-control form-control-sm" type="text" name="sito" value="{{ filters.sito or '' }}" placeholder="Sito"></div>
    <div class="col-md-1"><input class="form-control form-control-sm" type="text" name="area" value="{{ filters.area or '' }}" placeholder="Area"></div>
    <div class="col-md-1"><input class="form-control form-control-sm" type="number" name="us" value="{{ filters.us or '' }}" placeholder="US"></div>
    <div class="col-md-2"><input class="form-control form-control-sm" type="text" name="form" value="{{ filters.form or '' }}" placeholder="Forma" list="dl-forms"></div>
    <div class="col-md-2"><input class="form-control form-control-sm" type="text" name="fabric" value="{{ filters.fabric or '' }}" placeholder="Impasto" list="dl-fabrics"></div>
    <div class="col-md-3"><input class="form-control form-control-sm" type="text" name="q" value="{{ filters.q or '' }}" placeholder="Ricerca testo libero"></div>
    <div class="col-md-1"><button class="btn btn-sm btn-secondary">Filtra</button></div>
    <datalist id="dl-forms"></datalist>
    <datalist id="dl-fabrics"></datalist>
  </form>

  <div class="table-responsive">
  <table class="table table-sm table-hover">
    <thead><tr>
      <th>id_rep</th><th>id_num</th><th>Sito</th><th>Area</th><th>US</th>
      <th>Forma</th><th>Impasto</th><th>Ware</th><th>Qty</th><th></th>
    </tr></thead>
    <tbody>
    {% for p in items %}
      <tr>
        <td>{{ p.id_rep }}</td><td>{{ p.id_number or '' }}</td>
        <td>{{ p.sito }}</td><td>{{ p.area or '' }}</td><td>{{ p.us or '' }}</td>
        <td>{{ p.form or '' }}</td><td>{{ p.fabric or '' }}</td>
        <td>{{ p.ware or '' }}</td><td>{{ p.qty or '' }}</td>
        <td>
          <a class="btn btn-sm btn-outline-primary" href="{{ url_for('pottery_detail', id_rep=p.id_rep) }}">Vedi</a>
          <a class="btn btn-sm btn-outline-warning" href="{{ url_for('pottery_edit', id_rep=p.id_rep) }}">Edit</a>
        </td>
      </tr>
    {% else %}
      <tr><td colspan="10" class="text-muted">Nessun risultato</td></tr>
    {% endfor %}
    </tbody>
  </table>
  </div>

  {% set pages = (total // size) + (1 if total % size else 0) %}
  {% if pages > 1 %}
  <nav><ul class="pagination pagination-sm">
    {% for p in range(1, pages+1) %}
      <li class="page-item {% if p == page %}active{% endif %}">
        <a class="page-link" href="{{ url_for('pottery_list', page=p, **filters) }}">{{ p }}</a>
      </li>
    {% endfor %}
  </ul></nav>
  {% endif %}
</div>

<script>
fetch("/api/pottery/forms").then(r=>r.json()).then(o=>{
  const dl = document.getElementById("dl-forms");
  (o.values||[]).forEach(v => { const opt=document.createElement("option"); opt.value=v; dl.appendChild(opt); });
});
fetch("/api/pottery/fabrics").then(r=>r.json()).then(o=>{
  const dl = document.getElementById("dl-fabrics");
  (o.values||[]).forEach(v => { const opt=document.createElement("option"); opt.value=v; dl.appendChild(opt); });
});
</script>
{% endblock %}
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/integration/test_pottery_routes.py -v -k "list_page"`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/pottery/list.html tests/integration/test_pottery_routes.py
git commit -m "feat(web): pottery list template with filters and pagination"
```

---

## Task 11: Create form route + 3-tab template

**Files:**
- Modify: `pyarchinit_mini/web_interface/pottery_routes.py`
- Create: `pyarchinit_mini/web_interface/templates/pottery/form.html`
- Modify: `tests/integration/test_pottery_routes.py`

- [ ] **Step 1: Append failing tests**

Append to `tests/integration/test_pottery_routes.py`:

```python
def test_create_form_renders(client):
    r = client.get("/pottery/create")
    assert r.status_code == 200
    assert b"Description data" in r.data
    assert b"Technical Data" in r.data
    assert b"Supplements" in r.data


def test_create_post_inserts_record(client, svc):
    r = client.post("/pottery/create", data={
        "sito": "X", "area": "A", "us": "1", "form": "Olla",
        "fabric": "Coarse", "qty": "2",
    }, follow_redirects=False)
    assert r.status_code in (302, 303)
    items, total = svc.get_all_pottery()
    assert total == 1
    assert items[0].sito == "X"
    assert items[0].form == "Olla"


def test_create_post_missing_sito_flashes_error(client):
    r = client.post("/pottery/create", data={"form": "Olla"}, follow_redirects=True)
    assert r.status_code == 200
    assert b"sito" in r.data.lower()  # flashed error
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/integration/test_pottery_routes.py -v -k "create_"`
Expected: 404 / NotImplementedError on `/pottery/create`.

- [ ] **Step 3: Implement routes**

Append inside `_register_pottery_routes` in `pyarchinit_mini/web_interface/pottery_routes.py`:

```python
    @app.route("/pottery/create", methods=["GET", "POST"])
    @login_required
    def pottery_create():
        svc = PotteryService(app.db_manager)
        if request.method == "POST":
            data = _extract_pottery_form(request.form)
            try:
                p = svc.create_pottery(data)
            except ValueError as e:
                flash(str(e), "danger")
                return render_template(
                    "pottery/form.html",
                    pottery=None, form_data=data, mode="create",
                )
            flash(f"Pottery #{p.id_rep} created.", "success")
            return redirect(url_for("pottery_detail", id_rep=p.id_rep))
        return render_template(
            "pottery/form.html", pottery=None, form_data={}, mode="create"
        )
```

And in the same file, above `_register_pottery_routes` define the helper:

```python
_POTTERY_FORM_FIELDS = (
    "id_number", "sito", "area", "us", "box", "photo", "drawing", "anno",
    "fabric", "percent", "material", "form", "specific_form", "ware",
    "munsell", "surf_trat", "exdeco", "intdeco", "wheel_made",
    "descrip_ex_deco", "descrip_in_deco", "note", "diametro_max", "qty",
    "diametro_rim", "diametro_bottom", "diametro_height",
    "diametro_preserved", "specific_shape", "bag", "sector",
)
_INT_FIELDS = {"id_number", "us", "box", "anno", "qty", "bag"}
_NUM_FIELDS = {
    "diametro_max", "diametro_rim", "diametro_bottom",
    "diametro_height", "diametro_preserved",
}


def _extract_pottery_form(form) -> dict:
    """Pull pottery fields from a Flask request.form, coercing types."""
    out = {}
    for k in _POTTERY_FORM_FIELDS:
        v = form.get(k)
        if v in (None, ""):
            continue
        if k in _INT_FIELDS:
            try:
                out[k] = int(v)
            except ValueError:
                continue
        elif k in _NUM_FIELDS:
            try:
                out[k] = float(v)
            except ValueError:
                continue
        else:
            out[k] = v
    return out
```

- [ ] **Step 4: Implement form template**

Create `pyarchinit_mini/web_interface/templates/pottery/form.html`:

```jinja2
{% extends "base.html" %}
{% block title %}Pottery — {{ "New" if mode=="create" else pottery.id_rep }}{% endblock %}

{% macro fld(name, label, type="text", required=False, value=None) %}
<div class="mb-2">
  <label class="form-label" for="f_{{name}}">{{ label }}{% if required %} *{% endif %}</label>
  <input class="form-control form-control-sm" id="f_{{name}}" name="{{name}}" type="{{type}}"
    value="{{ value if value is not none else (form_data.get(name) if form_data else (pottery|attr(name) if pottery else '')) }}"
    {% if required %}required{% endif %}>
</div>
{% endmacro %}

{% macro txa(name, label) %}
<div class="mb-2">
  <label class="form-label" for="f_{{name}}">{{ label }}</label>
  <textarea class="form-control form-control-sm" id="f_{{name}}" name="{{name}}" rows="3">{{ form_data.get(name) if form_data else (pottery|attr(name) if pottery else '') }}</textarea>
</div>
{% endmacro %}

{% block content %}
<div class="container mt-3">
  <h1>Pottery {% if mode=="create" %}<small class="text-muted">— Nuovo</small>{% else %}#{{ pottery.id_rep }}{% endif %}</h1>

  <form method="post" novalidate>
    <ul class="nav nav-tabs" role="tablist">
      <li class="nav-item"><a class="nav-link active" data-bs-toggle="tab" href="#tab-desc">Description data</a></li>
      <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#tab-tech">Technical Data</a></li>
      <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#tab-supp">Supplements</a></li>
    </ul>

    <div class="tab-content border border-top-0 p-3">

      <div class="tab-pane fade show active" id="tab-desc">
        <div class="row">
          <div class="col-md-4">{{ fld("sito", "Sito", required=True) }}</div>
          <div class="col-md-4">{{ fld("area", "Area") }}</div>
          <div class="col-md-2">{{ fld("us", "US", type="number") }}</div>
          <div class="col-md-2">{{ fld("sector", "Sector") }}</div>
          <div class="col-md-2">{{ fld("anno", "Year", type="number") }}</div>
          <div class="col-md-2">{{ fld("box", "Box", type="number") }}</div>
          <div class="col-md-2">{{ fld("bag", "Bag", type="number") }}</div>
          <div class="col-md-2">{{ fld("id_number", "ID number", type="number") }}</div>
          <div class="col-md-3">{{ fld("material", "Material") }}</div>
          <div class="col-md-3">{{ fld("form", "Form") }}</div>
          <div class="col-md-3">{{ fld("specific_form", "Specific form") }}</div>
          <div class="col-md-3">{{ fld("specific_shape", "Specific shape") }}</div>
          <div class="col-md-6">{{ fld("photo", "Photo (path)") }}</div>
          <div class="col-md-6">{{ fld("drawing", "Drawing (path)") }}</div>
          <div class="col-12">{{ txa("note", "Note") }}</div>
        </div>
        {% if pottery %}
        <a class="btn btn-outline-secondary btn-sm" href="{{ url_for('pottery_media', id_rep=pottery.id_rep) }}">📎 Manage media</a>
        {% endif %}
      </div>

      <div class="tab-pane fade" id="tab-tech">
        <div class="row">
          <div class="col-md-3">{{ fld("fabric", "Fabric") }}</div>
          <div class="col-md-3">{{ fld("ware", "Ware") }}</div>
          <div class="col-md-3">{{ fld("munsell", "Munsell") }}</div>
          <div class="col-md-3">{{ fld("percent", "Percent preserved") }}</div>
          <div class="col-md-4">{{ fld("surf_trat", "Surface treatment") }}</div>
          <div class="col-md-2">
            <label class="form-label" for="f_wheel_made">Wheel-made</label>
            <select class="form-select form-select-sm" id="f_wheel_made" name="wheel_made">
              {% set wm = form_data.get('wheel_made') if form_data else (pottery.wheel_made if pottery else '') %}
              <option value=""></option>
              <option value="Yes" {% if wm=='Yes' %}selected{% endif %}>Yes</option>
              <option value="No" {% if wm=='No' %}selected{% endif %}>No</option>
              <option value="Indeterminate" {% if wm=='Indeterminate' %}selected{% endif %}>Indeterminate</option>
            </select>
          </div>
          <div class="col-md-3">{{ fld("exdeco", "Exterior deco") }}</div>
          <div class="col-md-3">{{ fld("intdeco", "Interior deco") }}</div>
          <div class="col-md-6">{{ txa("descrip_ex_deco", "Ext deco description") }}</div>
          <div class="col-md-6">{{ txa("descrip_in_deco", "Int deco description") }}</div>
          <div class="col-md-2">{{ fld("qty", "Qty", type="number") }}</div>
          <div class="col-md-2">{{ fld("diametro_max", "Diam max", type="number") }}</div>
          <div class="col-md-2">{{ fld("diametro_rim", "Diam rim", type="number") }}</div>
          <div class="col-md-2">{{ fld("diametro_bottom", "Diam bottom", type="number") }}</div>
          <div class="col-md-2">{{ fld("diametro_height", "Diam height", type="number") }}</div>
          <div class="col-md-2">{{ fld("diametro_preserved", "Diam preserved", type="number") }}</div>
        </div>
      </div>

      <div class="tab-pane fade" id="tab-supp">
        <ul class="nav nav-pills mb-2">
          <li class="nav-item"><a class="nav-link active" data-bs-toggle="tab" href="#sub-bib">Bibliography</a></li>
          <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#sub-stat">Statistic</a></li>
        </ul>
        <div class="tab-content">
          <div class="tab-pane fade show active" id="sub-bib">
            <p class="text-muted">Bibliography integration coming in a future release.</p>
          </div>
          <div class="tab-pane fade" id="sub-stat">
            <p class="text-muted">Statistics are computed from saved records — visible on the detail view.</p>
          </div>
        </div>
      </div>

    </div>

    <div class="mt-3">
      <button class="btn btn-primary">Save</button>
      <a class="btn btn-secondary" href="{{ url_for('pottery_list') }}">Cancel</a>
    </div>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/integration/test_pottery_routes.py -v -k "create_"`
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/web_interface/pottery_routes.py pyarchinit_mini/web_interface/templates/pottery/form.html tests/integration/test_pottery_routes.py
git commit -m "feat(web): pottery create route + 3-tab form template"
```

---

## Task 12: Detail route + template

**Files:**
- Modify: `pyarchinit_mini/web_interface/pottery_routes.py`
- Create: `pyarchinit_mini/web_interface/templates/pottery/detail.html`
- Modify: `tests/integration/test_pottery_routes.py`

- [ ] **Step 1: Append test**

Append to `tests/integration/test_pottery_routes.py`:

```python
def test_detail_renders_record(client, svc):
    p = svc.create_pottery({"sito": "X", "form": "Olla", "fabric": "Coarse"})
    r = client.get(f"/pottery/{p.id_rep}")
    assert r.status_code == 200
    assert b"Olla" in r.data
    assert b"Coarse" in r.data


def test_detail_404_for_missing(client):
    r = client.get("/pottery/99999")
    assert r.status_code == 404
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/integration/test_pottery_routes.py -v -k "detail"`

- [ ] **Step 3: Implement route**

Append inside `_register_pottery_routes`:

```python
    @app.route("/pottery/<int:id_rep>")
    @login_required
    def pottery_detail(id_rep: int):
        svc = PotteryService(app.db_manager)
        p = svc.get_pottery_by_id(id_rep)
        if not p:
            abort(404)
        return render_template(
            "pottery/detail.html",
            pottery=PotteryDTO.from_model(p),
        )
```

- [ ] **Step 4: Implement template**

Create `pyarchinit_mini/web_interface/templates/pottery/detail.html`:

```jinja2
{% extends "base.html" %}
{% block title %}Pottery #{{ pottery.id_rep }}{% endblock %}

{% macro row(label, val) %}
<div class="col-md-3"><strong>{{ label }}:</strong> {{ val if val is not none else '' }}</div>
{% endmacro %}

{% block content %}
<div class="container mt-3">
  <div class="d-flex justify-content-between">
    <h1>Pottery #{{ pottery.id_rep }} <small class="text-muted">{{ pottery.sito }}{% if pottery.id_number %} · ID {{ pottery.id_number }}{% endif %}</small></h1>
    <div>
      <a class="btn btn-warning" href="{{ url_for('pottery_edit', id_rep=pottery.id_rep) }}">Edit</a>
      <a class="btn btn-outline-danger" href="{{ url_for('pottery_export_single_pdf', id_rep=pottery.id_rep) }}">PDF</a>
      <form method="post" class="d-inline" action="{{ url_for('pottery_delete', id_rep=pottery.id_rep) }}"
            onsubmit="return confirm('Delete pottery #{{ pottery.id_rep }}?');">
        <button class="btn btn-danger">Delete</button>
      </form>
    </div>
  </div>

  <h3 class="mt-3">Description</h3>
  <div class="row g-2">
    {{ row("Site", pottery.sito) }}{{ row("Area", pottery.area) }}{{ row("US", pottery.us) }}{{ row("Sector", pottery.sector) }}
    {{ row("Year", pottery.anno) }}{{ row("Box", pottery.box) }}{{ row("Bag", pottery.bag) }}{{ row("ID number", pottery.id_number) }}
    {{ row("Material", pottery.material) }}{{ row("Form", pottery.form) }}{{ row("Specific form", pottery.specific_form) }}{{ row("Specific shape", pottery.specific_shape) }}
  </div>

  <h3 class="mt-3">Technical</h3>
  <div class="row g-2">
    {{ row("Fabric", pottery.fabric) }}{{ row("Ware", pottery.ware) }}{{ row("Munsell", pottery.munsell) }}{{ row("Percent", pottery.percent) }}
    {{ row("Surface treat.", pottery.surf_trat) }}{{ row("Wheel-made", pottery.wheel_made) }}{{ row("Ext deco", pottery.exdeco) }}{{ row("Int deco", pottery.intdeco) }}
  </div>
  {% if pottery.descrip_ex_deco or pottery.descrip_in_deco %}
  <div class="row g-2">
    {% if pottery.descrip_ex_deco %}<div class="col-md-6"><strong>Ext deco desc.:</strong> {{ pottery.descrip_ex_deco }}</div>{% endif %}
    {% if pottery.descrip_in_deco %}<div class="col-md-6"><strong>Int deco desc.:</strong> {{ pottery.descrip_in_deco }}</div>{% endif %}
  </div>
  {% endif %}

  <h3 class="mt-3">Measurements</h3>
  <div class="row g-2">
    {{ row("Qty", pottery.qty) }}{{ row("Diam max", pottery.diametro_max) }}{{ row("Diam rim", pottery.diametro_rim) }}
    {{ row("Diam bottom", pottery.diametro_bottom) }}{{ row("Diam height", pottery.diametro_height) }}{{ row("Diam preserved", pottery.diametro_preserved) }}
  </div>

  {% if pottery.note %}
  <h3 class="mt-3">Notes</h3>
  <p>{{ pottery.note }}</p>
  {% endif %}

  <h3 class="mt-3">Media attachments</h3>
  <div id="pottery-media-grid" class="d-flex flex-wrap gap-2">
    <em class="text-muted">Loading…</em>
  </div>
  <a class="btn btn-sm btn-outline-secondary mt-2" href="{{ url_for('pottery_media', id_rep=pottery.id_rep) }}">📎 Manage media</a>
</div>

<script>
fetch("/api/media/by_entity?entity_type=pottery&entity_id={{ pottery.id_rep }}")
  .then(r => r.ok ? r.json() : {items:[]})
  .then(o => {
    const g = document.getElementById("pottery-media-grid");
    g.innerHTML = "";
    (o.items||[]).forEach(m => {
      const img = document.createElement("img");
      img.src = m.thumb_url || m.url;
      img.style.maxWidth = "120px"; img.style.maxHeight = "120px";
      img.title = m.media_name || "";
      img.className = "border rounded";
      g.appendChild(img);
    });
    if (!g.children.length) g.innerHTML = "<em class='text-muted'>Nessun media allegato</em>";
  });
</script>
{% endblock %}
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/integration/test_pottery_routes.py -v -k "detail"`
Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/web_interface/pottery_routes.py pyarchinit_mini/web_interface/templates/pottery/detail.html tests/integration/test_pottery_routes.py
git commit -m "feat(web): pottery detail route + template"
```

---

## Task 13: Edit + Delete routes

**Files:**
- Modify: `pyarchinit_mini/web_interface/pottery_routes.py`
- Modify: `tests/integration/test_pottery_routes.py`

- [ ] **Step 1: Append tests**

Append to `tests/integration/test_pottery_routes.py`:

```python
def test_edit_get_prefills_form(client, svc):
    p = svc.create_pottery({"sito": "X", "form": "Olla"})
    r = client.get(f"/pottery/{p.id_rep}/edit")
    assert r.status_code == 200
    assert b"Olla" in r.data


def test_edit_post_updates(client, svc):
    p = svc.create_pottery({"sito": "X", "form": "Olla"})
    r = client.post(f"/pottery/{p.id_rep}/edit", data={
        "sito": "X", "form": "Ciotola", "qty": "3"
    })
    assert r.status_code in (302, 303)
    refreshed = svc.get_pottery_by_id(p.id_rep)
    assert refreshed.form == "Ciotola"
    assert refreshed.qty == 3


def test_delete_removes_record(client, svc):
    p = svc.create_pottery({"sito": "X", "form": "Olla"})
    r = client.post(f"/pottery/{p.id_rep}/delete")
    assert r.status_code in (302, 303)
    assert svc.get_pottery_by_id(p.id_rep) is None
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/integration/test_pottery_routes.py -v -k "edit_ or delete_removes"`

- [ ] **Step 3: Implement edit + delete routes**

Append inside `_register_pottery_routes`:

```python
    @app.route("/pottery/<int:id_rep>/edit", methods=["GET", "POST"])
    @login_required
    def pottery_edit(id_rep: int):
        svc = PotteryService(app.db_manager)
        p = svc.get_pottery_by_id(id_rep)
        if not p:
            abort(404)
        if request.method == "POST":
            data = _extract_pottery_form(request.form)
            try:
                svc.update_pottery(id_rep, data)
            except ValueError as e:
                flash(str(e), "danger")
                return render_template(
                    "pottery/form.html",
                    pottery=PotteryDTO.from_model(p),
                    form_data=data, mode="edit",
                )
            flash(f"Pottery #{id_rep} updated.", "success")
            return redirect(url_for("pottery_detail", id_rep=id_rep))
        return render_template(
            "pottery/form.html",
            pottery=PotteryDTO.from_model(p),
            form_data={}, mode="edit",
        )

    @app.route("/pottery/<int:id_rep>/delete", methods=["POST"])
    @login_required
    def pottery_delete(id_rep: int):
        svc = PotteryService(app.db_manager)
        if not svc.delete_pottery(id_rep):
            abort(404)
        flash(f"Pottery #{id_rep} deleted.", "info")
        return redirect(url_for("pottery_list"))
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/integration/test_pottery_routes.py -v -k "edit_ or delete_removes"`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/pottery_routes.py tests/integration/test_pottery_routes.py
git commit -m "feat(web): pottery edit + delete routes"
```

---

## Task 14: Autocomplete + Stats API endpoints

**Files:**
- Modify: `pyarchinit_mini/web_interface/pottery_routes.py`
- Modify: `tests/integration/test_pottery_routes.py`

- [ ] **Step 1: Append tests**

Append to `tests/integration/test_pottery_routes.py`:

```python
def test_api_forms_returns_distinct(client, svc):
    svc.create_pottery({"sito": "X", "form": "Olla"})
    svc.create_pottery({"sito": "X", "form": "Ciotola"})
    svc.create_pottery({"sito": "Y", "form": "Olla"})
    r = client.get("/api/pottery/forms")
    assert r.status_code == 200
    vs = r.get_json()["values"]
    assert set(vs) == {"Olla", "Ciotola"}


def test_api_stats(client, svc):
    svc.create_pottery({"sito": "X", "form": "Olla", "fabric": "Coarse", "qty": 5, "anno": 2024})
    svc.create_pottery({"sito": "X", "form": "Ciotola", "fabric": "Fine", "qty": 1, "anno": 2024})
    r = client.get("/api/pottery/stats?sito=X")
    assert r.status_code == 200
    o = r.get_json()
    assert o["total"] == 2
    assert any(d["form"] == "Olla" for d in o["by_form"])
    assert o["mni"] == 6
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/integration/test_pottery_routes.py -v -k "api_forms or api_stats"`

- [ ] **Step 3: Implement endpoints**

Append inside `_register_pottery_routes`:

```python
    @app.route("/api/pottery/forms")
    @login_required
    def pottery_api_forms():
        return _distinct_values(app, "form")

    @app.route("/api/pottery/fabrics")
    @login_required
    def pottery_api_fabrics():
        return _distinct_values(app, "fabric")

    @app.route("/api/pottery/wares")
    @login_required
    def pottery_api_wares():
        return _distinct_values(app, "ware")

    @app.route("/api/pottery/stats")
    @login_required
    def pottery_api_stats():
        svc = PotteryService(app.db_manager)
        sito = request.args.get("sito")
        area = request.args.get("area")
        us = request.args.get("us")
        us_int = int(us) if us and us.isdigit() else None

        by_form = svc.get_form_distribution(sito) if sito else svc.get_form_distribution()
        by_fabric = svc.get_fabric_distribution(sito) if sito else svc.get_fabric_distribution()
        by_ware = svc.get_ware_distribution(sito) if sito else svc.get_ware_distribution()

        filters = {k: v for k, v in {"sito": sito, "area": area, "us": us_int}.items() if v}
        total = svc.count_pottery(filters or None)
        mni = svc.calculate_mni(sito, area, us_int)["total"] if sito else 0

        # Time series by anno
        from sqlalchemy import func as f
        session = app.db_manager.SessionLocal()
        try:
            from ..models.pottery import Pottery
            q = session.query(Pottery.anno, f.count(Pottery.id_rep)).group_by(Pottery.anno)
            if sito:
                q = q.filter(Pottery.sito == sito)
            by_anno = [{"anno": a, "count": c} for a, c in q.all() if a is not None]
        finally:
            session.close()

        return jsonify({
            "total": total,
            "by_form": [{"form": k, "count": v} for k, v in by_form.items()],
            "by_fabric": [{"fabric": k, "count": v} for k, v in by_fabric.items()],
            "by_ware": [{"ware": k, "count": v} for k, v in by_ware.items()],
            "by_anno": by_anno,
            "mni": mni,
        })
```

Also add the helper just above `_register_pottery_routes`:

```python
def _distinct_values(app, column_name: str):
    from ..models.pottery import Pottery
    session = app.db_manager.SessionLocal()
    try:
        col = getattr(Pottery, column_name)
        rows = session.query(col).filter(col.isnot(None)).distinct().all()
        return jsonify({"values": sorted({r[0] for r in rows if r[0]})})
    finally:
        session.close()
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/integration/test_pottery_routes.py -v -k "api_forms or api_stats"`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/pottery_routes.py tests/integration/test_pottery_routes.py
git commit -m "feat(web): pottery autocomplete + stats API endpoints"
```

---

## Task 15: Media wiring (entity_type=pottery)

**Files:**
- Modify: `pyarchinit_mini/web_interface/app.py:288, 2682-2706, 2642+`
- Modify: `pyarchinit_mini/web_interface/pottery_routes.py`
- Modify: `tests/integration/test_pottery_routes.py`

- [ ] **Step 1: Add `('pottery', 'Pottery')` to media SelectField**

In `pyarchinit_mini/web_interface/app.py:288`, find the `entity_type = SelectField('Entity Type', choices=[...])` and add `('pottery', 'Pottery')` at the end of the choices list.

Run before to confirm exact form:
```bash
sed -n '286,300p' pyarchinit_mini/web_interface/app.py
```

Add the tuple inline.

- [ ] **Step 2: Add pottery branch in upload validation route**

In `app.py:2682-2706` find the existing `elif entity_type == 'inventario':` block. Add immediately after it (still inside the same `if/elif` chain):

```python
                elif entity_type == 'pottery':
                    from .pottery_routes import PotteryService
                    psvc = PotteryService(app.db_manager)
                    p = psvc.get_pottery_by_id(int(entity_id))
                    if not p:
                        flash(f"Pottery #{entity_id} not found", "danger")
                        return redirect(url_for("media_upload"))
```

(Match the style and indentation of the surrounding block; the snippet above is illustrative — preserve the existing logging/flash conventions.)

- [ ] **Step 3: Add `/api/media/pottery` endpoint**

In `app.py` near the existing `/api/media/inventario` endpoint (search for `@app.route('/api/media/inventario')` around line 2642), add a parallel endpoint:

```python
    @app.route('/api/media/pottery')
    @login_required
    def api_media_pottery():
        svc = PotteryService(app.db_manager)
        items, _ = svc.get_all_pottery(page=1, size=500)
        return jsonify({
            "items": [
                {
                    "id_rep": p.id_rep, "sito": p.sito,
                    "id_number": p.id_number, "form": p.form,
                    "fabric": p.fabric,
                }
                for p in items
            ]
        })
```

(Adjust to match the inventario pattern in this file — including the PotteryService import at the top.)

- [ ] **Step 4: Add `pottery_media` URL stub**

Append inside `_register_pottery_routes` in `pyarchinit_mini/web_interface/pottery_routes.py`:

```python
    @app.route("/pottery/<int:id_rep>/media")
    @login_required
    def pottery_media(id_rep: int):
        # Reuse the universal media manager via redirect with entity params.
        return redirect(url_for("media_manage", entity_type="pottery", entity_id=id_rep))
```

(If `media_manage` isn't the actual endpoint name, look it up in `app.py` and adjust.)

- [ ] **Step 5: Append integration test**

Append to `tests/integration/test_pottery_routes.py`:

```python
def test_api_media_pottery_lists_records(client, svc):
    p = svc.create_pottery({"sito": "X", "form": "Olla"})
    r = client.get("/api/media/pottery")
    assert r.status_code == 200
    items = r.get_json()["items"]
    assert any(i["id_rep"] == p.id_rep for i in items)
```

- [ ] **Step 6: Run tests**

Run: `pytest tests/integration/test_pottery_routes.py -v -k "api_media_pottery"`
Expected: pass.

- [ ] **Step 7: Commit**

```bash
git add pyarchinit_mini/web_interface/app.py pyarchinit_mini/web_interface/pottery_routes.py tests/integration/test_pottery_routes.py
git commit -m "feat(web): pottery media wiring (entity_type=pottery + /api/media/pottery)"
```

---

## Task 16: Excel + CSV export

**Files:**
- Modify: `pyarchinit_mini/web_interface/pottery_routes.py`
- Test: `tests/integration/test_pottery_excel_roundtrip.py`

- [ ] **Step 1: Write failing test**

Create `tests/integration/test_pottery_excel_roundtrip.py`:

```python
import io
import pytest
from openpyxl import load_workbook

from tests.integration.test_pottery_routes import app, client, svc  # reuse fixtures


def test_excel_export_returns_xlsx(client, svc):
    svc.create_pottery({"sito": "X", "form": "Olla", "fabric": "Coarse", "qty": 1})
    r = client.get("/export/pottery/excel")
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/")
    wb = load_workbook(io.BytesIO(r.data))
    assert "pottery" in wb.sheetnames


def test_csv_export(client, svc):
    svc.create_pottery({"sito": "X", "form": "Olla"})
    r = client.get("/export/pottery/csv")
    assert r.status_code == 200
    body = r.data.decode("utf-8")
    assert "sito" in body and "Olla" in body
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/integration/test_pottery_excel_roundtrip.py -v`
Expected: 404.

- [ ] **Step 3: Implement export routes**

Append inside `_register_pottery_routes` in `pyarchinit_mini/web_interface/pottery_routes.py`:

```python
    @app.route("/export/pottery/excel")
    @login_required
    def pottery_export_excel():
        import io
        import pandas as pd
        from datetime import datetime, timezone
        from flask import send_file
        svc = PotteryService(app.db_manager)
        filters = {k: request.args.get(k) for k in ("sito","area","us","form","fabric") if request.args.get(k)}
        if "us" in filters:
            try: filters["us"] = int(filters["us"])
            except ValueError: filters.pop("us")
        items, _ = svc.get_all_pottery(page=1, size=10_000, filters=filters)
        rows = [PotteryDTO.from_model(p).to_dict() for p in items]
        df = pd.DataFrame(rows, columns=list(_POTTERY_FORM_FIELDS) + ["id_rep"])
        meta = pd.DataFrame([{
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "version": "2.1.60", "filters": str(filters),
            "row_count": len(rows),
        }])
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df.to_excel(w, sheet_name="pottery", index=False)
            meta.to_excel(w, sheet_name="metadata", index=False)
        buf.seek(0)
        return send_file(
            buf, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True, download_name="pottery.xlsx",
        )

    @app.route("/export/pottery/csv")
    @login_required
    def pottery_export_csv():
        import io
        import csv
        from flask import Response
        svc = PotteryService(app.db_manager)
        filters = {k: request.args.get(k) for k in ("sito","area","us","form","fabric") if request.args.get(k)}
        if "us" in filters:
            try: filters["us"] = int(filters["us"])
            except ValueError: filters.pop("us")
        items, _ = svc.get_all_pottery(page=1, size=10_000, filters=filters)
        header = list(_POTTERY_FORM_FIELDS) + ["id_rep"]
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=header)
        w.writeheader()
        for p in items:
            d = PotteryDTO.from_model(p).to_dict()
            w.writerow({k: d.get(k, "") for k in header})
        return Response(
            buf.getvalue(), mimetype="text/csv",
            headers={"Content-Disposition": 'attachment; filename="pottery.csv"'},
        )
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/integration/test_pottery_excel_roundtrip.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/pottery_routes.py tests/integration/test_pottery_excel_roundtrip.py
git commit -m "feat(web): pottery Excel + CSV export"
```

---

## Task 17: Excel/CSV import

**Files:**
- Modify: `pyarchinit_mini/web_interface/pottery_routes.py`
- Modify: `tests/integration/test_pottery_excel_roundtrip.py`

- [ ] **Step 1: Append test**

Append to `tests/integration/test_pottery_excel_roundtrip.py`:

```python
import pandas as pd

def test_excel_import_roundtrip(client, svc):
    # Build XLSX bytes
    df = pd.DataFrame([{
        "sito": "X", "form": "Olla", "fabric": "Coarse", "qty": 1, "id_number": 10,
    }, {
        "sito": "X", "form": "Ciotola", "fabric": "Fine", "qty": 2, "id_number": 11,
    }])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="pottery", index=False)
    buf.seek(0)
    r = client.post(
        "/import/pottery/excel",
        data={"file": (buf, "in.xlsx"), "mode": "skip"},
        content_type="multipart/form-data",
    )
    assert r.status_code in (200, 302)
    items, total = svc.get_all_pottery()
    assert total == 2


def test_excel_import_skip_duplicates(client, svc):
    svc.create_pottery({"sito": "X", "id_number": 10, "form": "Old"})
    df = pd.DataFrame([{"sito": "X", "id_number": 10, "form": "New"}])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="pottery", index=False)
    buf.seek(0)
    client.post(
        "/import/pottery/excel",
        data={"file": (buf, "in.xlsx"), "mode": "skip"},
        content_type="multipart/form-data",
    )
    p = svc.get_pottery_by_id(1)
    assert p.form == "Old"  # not overwritten


def test_excel_import_update_mode(client, svc):
    svc.create_pottery({"sito": "X", "id_number": 10, "form": "Old"})
    df = pd.DataFrame([{"sito": "X", "id_number": 10, "form": "New"}])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="pottery", index=False)
    buf.seek(0)
    client.post(
        "/import/pottery/excel",
        data={"file": (buf, "in.xlsx"), "mode": "update"},
        content_type="multipart/form-data",
    )
    items, _ = svc.get_all_pottery()
    forms = [i.form for i in items]
    assert "New" in forms
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/integration/test_pottery_excel_roundtrip.py -v -k "import_"`
Expected: 404.

- [ ] **Step 3: Implement import route + form GET**

Append inside `_register_pottery_routes`:

```python
    @app.route("/import/pottery", methods=["GET"])
    @login_required
    def pottery_import_form():
        return render_template("pottery/import_form.html")

    @app.route("/import/pottery/excel", methods=["POST"])
    @login_required
    def pottery_import_excel():
        import pandas as pd
        f = request.files.get("file")
        if not f:
            flash("Missing file", "danger")
            return redirect(url_for("pottery_import_form"))
        mode = request.form.get("mode", "skip")  # skip | update | renumber
        try:
            if f.filename.lower().endswith(".csv"):
                df = pd.read_csv(f)
            else:
                df = pd.read_excel(f, sheet_name="pottery")
        except Exception as e:
            flash(f"Cannot read file: {e}", "danger")
            return redirect(url_for("pottery_import_form"))

        svc = PotteryService(app.db_manager)
        stats = {"inserted": 0, "updated": 0, "skipped": 0, "errors": []}
        for idx, row in df.iterrows():
            data = {k: (None if pd.isna(v) else v) for k, v in row.items() if k in _POTTERY_FORM_FIELDS}
            sito = data.get("sito")
            idn = data.get("id_number")
            if not sito:
                stats["errors"].append(f"row {idx+2}: missing sito")
                continue
            existing = None
            if idn is not None:
                from ..models.pottery import Pottery
                session = app.db_manager.SessionLocal()
                try:
                    existing = (
                        session.query(Pottery)
                        .filter(Pottery.sito == sito, Pottery.id_number == int(idn))
                        .first()
                    )
                finally:
                    session.close()
            try:
                if existing and mode == "skip":
                    stats["skipped"] += 1
                elif existing and mode == "update":
                    svc.update_pottery(existing.id_rep, data)
                    stats["updated"] += 1
                elif existing and mode == "renumber":
                    data.pop("id_number", None)
                    svc.create_pottery(data)
                    stats["inserted"] += 1
                else:
                    svc.create_pottery(data)
                    stats["inserted"] += 1
            except ValueError as e:
                stats["errors"].append(f"row {idx+2}: {e}")

        flash(
            f"Import done: {stats['inserted']} inserted, "
            f"{stats['updated']} updated, {stats['skipped']} skipped, "
            f"{len(stats['errors'])} errors.",
            "info",
        )
        return redirect(url_for("pottery_list"))
```

- [ ] **Step 4: Create import form template**

Create `pyarchinit_mini/web_interface/templates/pottery/import_form.html`:

```jinja2
{% extends "base.html" %}
{% block title %}Import Pottery{% endblock %}
{% block content %}
<div class="container mt-3">
  <h1>Import Pottery — Excel / CSV</h1>
  <form method="post" action="{{ url_for('pottery_import_excel') }}" enctype="multipart/form-data">
    <div class="mb-3">
      <label class="form-label">File (.xlsx or .csv)</label>
      <input class="form-control" type="file" name="file" accept=".xlsx,.csv" required>
    </div>
    <div class="mb-3">
      <label class="form-label">Duplicate handling</label>
      <div class="form-check"><input class="form-check-input" type="radio" name="mode" value="skip" id="m1" checked><label for="m1" class="form-check-label">Skip duplicates</label></div>
      <div class="form-check"><input class="form-check-input" type="radio" name="mode" value="update" id="m2"><label for="m2" class="form-check-label">Update duplicates</label></div>
      <div class="form-check"><input class="form-check-input" type="radio" name="mode" value="renumber" id="m3"><label for="m3" class="form-check-label">Renumber (new id_number)</label></div>
    </div>
    <button class="btn btn-primary">Import</button>
    <a class="btn btn-secondary" href="{{ url_for('pottery_list') }}">Cancel</a>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/integration/test_pottery_excel_roundtrip.py -v`
Expected: 5 passed (all from this file).

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/web_interface/pottery_routes.py pyarchinit_mini/web_interface/templates/pottery/import_form.html tests/integration/test_pottery_excel_roundtrip.py
git commit -m "feat(web): pottery Excel/CSV import with skip/update/renumber"
```

---

## Task 18: PDF export

**Files:**
- Create: `pyarchinit_mini/services/pottery_pdf_service.py`
- Create: `pyarchinit_mini/web_interface/templates/pdf/pottery_sheet.html`
- Modify: `pyarchinit_mini/web_interface/pottery_routes.py`
- Modify: `tests/integration/test_pottery_routes.py`

- [ ] **Step 1: Append test**

Append to `tests/integration/test_pottery_routes.py`:

```python
def test_pdf_single(client, svc):
    p = svc.create_pottery({"sito": "X", "form": "Olla", "fabric": "Coarse", "qty": 2})
    r = client.get(f"/export/pottery_single_pdf/{p.id_rep}")
    assert r.status_code == 200
    assert r.data.startswith(b"%PDF")  # valid PDF magic


def test_pdf_batch(client, svc):
    svc.create_pottery({"sito": "X", "form": "Olla"})
    svc.create_pottery({"sito": "X", "form": "Ciotola"})
    r = client.get("/export/pottery_pdf?sito=X")
    assert r.status_code == 200
    assert r.data.startswith(b"%PDF")
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/integration/test_pottery_routes.py -v -k "pdf_"`
Expected: 404.

- [ ] **Step 3: Implement PDF service**

Create `pyarchinit_mini/services/pottery_pdf_service.py`:

```python
"""Render Pottery records to PDF via WeasyPrint."""
from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from typing import Iterable, List

from flask import render_template
from weasyprint import HTML

from ..models.pottery import Pottery
from .pottery_dto import PotteryDTO


class PotteryPDFService:
    @staticmethod
    def render_sheets(potteries: Iterable[Pottery], version: str = "2.1.60") -> bytes:
        dtos: List[PotteryDTO] = [PotteryDTO.from_model(p) for p in potteries]
        html = render_template(
            "pdf/pottery_sheet.html",
            potteries=dtos,
            version=version,
            printed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        )
        buf = BytesIO()
        HTML(string=html).write_pdf(buf)
        buf.seek(0)
        return buf.read()
```

- [ ] **Step 4: Implement PDF template**

Create `pyarchinit_mini/web_interface/templates/pdf/pottery_sheet.html`:

```jinja2
<!doctype html>
<html><head><meta charset="utf-8">
<style>
  @page { size: A4; margin: 1.4cm; }
  body { font: 10pt/1.3 sans-serif; color: #111; }
  h1 { font-size: 14pt; margin: 0 0 .4em; }
  .sheet { page-break-after: always; }
  .sheet:last-child { page-break-after: auto; }
  .header { display: flex; justify-content: space-between; border-bottom: 1px solid #444; padding-bottom: 4px; }
  .row { display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0; }
  .row > div { flex: 1 1 30%; }
  .section { border-top: 1px dashed #aaa; margin-top: 6px; padding-top: 4px; }
  .label { font-weight: bold; }
  .footer { position: running(footer); font-size: 8pt; color: #555; }
  @page { @bottom-center { content: element(footer); } }
</style></head>
<body>
{% for p in potteries %}
<div class="sheet">
  <div class="header">
    <h1>POTTERY SHEET</h1>
    <div><strong>Site:</strong> {{ p.sito }} &nbsp; <strong>ID rep:</strong> {{ p.id_rep }} &nbsp; <strong>ID #:</strong> {{ p.id_number or '' }}</div>
  </div>

  <div class="row">
    <div><span class="label">Area:</span> {{ p.area or '' }}</div>
    <div><span class="label">US:</span> {{ p.us or '' }}</div>
    <div><span class="label">Year:</span> {{ p.anno or '' }}</div>
    <div><span class="label">Sector:</span> {{ p.sector or '' }}</div>
    <div><span class="label">Bag:</span> {{ p.bag or '' }}</div>
    <div><span class="label">Box:</span> {{ p.box or '' }}</div>
  </div>

  <div class="section">
    <div class="label">Description</div>
    <div class="row">
      <div><span class="label">Material:</span> {{ p.material or '' }}</div>
      <div><span class="label">Form:</span> {{ p.form or '' }}</div>
      <div><span class="label">Specific form:</span> {{ p.specific_form or '' }}</div>
      <div><span class="label">Specific shape:</span> {{ p.specific_shape or '' }}</div>
    </div>
  </div>

  <div class="section">
    <div class="label">Technical</div>
    <div class="row">
      <div><span class="label">Fabric:</span> {{ p.fabric or '' }}</div>
      <div><span class="label">Ware:</span> {{ p.ware or '' }}</div>
      <div><span class="label">Munsell:</span> {{ p.munsell or '' }}</div>
      <div><span class="label">Surface treat.:</span> {{ p.surf_trat or '' }}</div>
      <div><span class="label">Wheel-made:</span> {{ p.wheel_made or '' }}</div>
      <div><span class="label">Percent:</span> {{ p.percent or '' }}</div>
    </div>
    <div class="row">
      <div><span class="label">Ext deco:</span> {{ p.exdeco or '' }} → {{ p.descrip_ex_deco or '' }}</div>
      <div><span class="label">Int deco:</span> {{ p.intdeco or '' }} → {{ p.descrip_in_deco or '' }}</div>
    </div>
  </div>

  <div class="section">
    <div class="label">Measurements</div>
    <div class="row">
      <div><span class="label">Qty:</span> {{ p.qty or '' }}</div>
      <div><span class="label">Diam max:</span> {{ p.diametro_max or '' }}</div>
      <div><span class="label">Rim:</span> {{ p.diametro_rim or '' }}</div>
      <div><span class="label">Bottom:</span> {{ p.diametro_bottom or '' }}</div>
      <div><span class="label">Height:</span> {{ p.diametro_height or '' }}</div>
      <div><span class="label">Preserved:</span> {{ p.diametro_preserved or '' }}</div>
    </div>
  </div>

  {% if p.note %}
  <div class="section">
    <div class="label">Notes</div>
    <p>{{ p.note }}</p>
  </div>
  {% endif %}
</div>
{% endfor %}

<div class="footer">pyarchinit-mini v{{ version }} · printed {{ printed_at }}</div>
</body></html>
```

- [ ] **Step 5: Implement PDF routes**

Append inside `_register_pottery_routes` in `pyarchinit_mini/web_interface/pottery_routes.py`:

```python
    @app.route("/export/pottery_pdf")
    @login_required
    def pottery_export_pdf():
        from flask import send_file
        from ..services.pottery_pdf_service import PotteryPDFService
        svc = PotteryService(app.db_manager)
        filters = {k: request.args.get(k) for k in ("sito","area","us","form","fabric") if request.args.get(k)}
        if "us" in filters:
            try: filters["us"] = int(filters["us"])
            except ValueError: filters.pop("us")
        items, _ = svc.get_all_pottery(page=1, size=10_000, filters=filters)
        if not items:
            flash("No pottery records matching filters.", "warning")
            return redirect(url_for("pottery_list"))
        from .. import __version__
        pdf_bytes = PotteryPDFService.render_sheets(items, version=__version__)
        from io import BytesIO
        return send_file(
            BytesIO(pdf_bytes), mimetype="application/pdf",
            as_attachment=True, download_name="pottery.pdf",
        )

    @app.route("/export/pottery_single_pdf/<int:id_rep>")
    @login_required
    def pottery_export_single_pdf(id_rep: int):
        from flask import send_file
        from ..services.pottery_pdf_service import PotteryPDFService
        svc = PotteryService(app.db_manager)
        p = svc.get_pottery_by_id(id_rep)
        if not p:
            abort(404)
        from .. import __version__
        pdf_bytes = PotteryPDFService.render_sheets([p], version=__version__)
        from io import BytesIO
        return send_file(
            BytesIO(pdf_bytes), mimetype="application/pdf",
            as_attachment=True, download_name=f"pottery_{id_rep}.pdf",
        )
```

- [ ] **Step 6: Run tests**

Run: `pytest tests/integration/test_pottery_routes.py -v -k "pdf_"`
Expected: 2 passed.

- [ ] **Step 7: Commit**

```bash
git add pyarchinit_mini/services/pottery_pdf_service.py pyarchinit_mini/web_interface/templates/pdf/pottery_sheet.html pyarchinit_mini/web_interface/pottery_routes.py tests/integration/test_pottery_routes.py
git commit -m "feat(web): pottery PDF export (single + batch)"
```

---

## Task 19: Navbar integration

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/base.html`

- [ ] **Step 1: Find the Records dropdown**

Run:
```bash
grep -nE "Records|nav-link|Inventario|dropdown" pyarchinit_mini/web_interface/templates/base.html | head -20
```

Locate the `<li class="nav-item dropdown">` block that contains `Inventario Materiali`.

- [ ] **Step 2: Add Pottery entry**

Right after the line that contains the Inventario `<a class="dropdown-item" …>Inventario Materiali</a>`, insert:

```jinja2
<li><a class="dropdown-item" href="{{ url_for('pottery_list') }}">Pottery</a></li>
```

- [ ] **Step 3: Verify it renders in the smoke test**

Run:
```bash
pytest tests/integration/test_pottery_routes.py::test_list_page_renders -v
```

Then quick manual check via `curl`:
```bash
python -c "
from pyarchinit_mini.web_interface.app import create_app
a = create_app(); a.config['LOGIN_DISABLED']=True
c = a.test_client(); r = c.get('/')
print('pottery in navbar:', b'pottery_list' in r.data or b'/pottery' in r.data)
"
```

Expected: `pottery in navbar: True`.

- [ ] **Step 4: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/base.html
git commit -m "feat(ui): add Pottery to Records navbar dropdown"
```

---

## Task 20: Analytics dashboard charts + MNI card

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/analytics/dashboard.html`

- [ ] **Step 1: Find dashboard charts section**

Run:
```bash
grep -nE "<canvas|Chart\.js|chart_type|new Chart" pyarchinit_mini/web_interface/templates/analytics/dashboard.html | head -20
```

Identify where existing chart canvases are declared.

- [ ] **Step 2: Append 3 charts + MNI card**

Just before the closing main content `</div>`, append:

```jinja2
<div class="card mt-4"><div class="card-body">
  <h4>Pottery — Distribuzione</h4>
  <div class="row">
    <div class="col-md-4"><canvas id="potteryFormChart"></canvas></div>
    <div class="col-md-4"><canvas id="potteryFabricChart"></canvas></div>
    <div class="col-md-4"><canvas id="potteryWareChart"></canvas></div>
  </div>
  <div class="row mt-3">
    <div class="col-md-6"><canvas id="potteryAnnoChart"></canvas></div>
    <div class="col-md-6">
      <div class="card text-center">
        <div class="card-body">
          <h2 id="potteryMNI">—</h2>
          <p class="text-muted">Min Number of Individuals<br><small>(group by form+fabric+ware)</small></p>
        </div>
      </div>
    </div>
  </div>
</div></div>

<script>
(function(){
  const sito = (new URLSearchParams(location.search)).get("sito") || "";
  fetch("/api/pottery/stats" + (sito ? `?sito=${encodeURIComponent(sito)}` : ""))
    .then(r => r.json())
    .then(o => {
      document.getElementById("potteryMNI").textContent = o.mni || 0;
      new Chart(document.getElementById("potteryFormChart"), {
        type: "doughnut",
        data: { labels: o.by_form.map(x=>x.form), datasets: [{ data: o.by_form.map(x=>x.count) }] },
        options: { plugins: { title: { display: true, text: "Form distribution" } } },
      });
      new Chart(document.getElementById("potteryFabricChart"), {
        type: "bar",
        data: { labels: o.by_fabric.map(x=>x.fabric), datasets: [{ label: "Fabric", data: o.by_fabric.map(x=>x.count) }] },
        options: { indexAxis: "y", plugins: { title: { display: true, text: "Fabric distribution" } } },
      });
      new Chart(document.getElementById("potteryWareChart"), {
        type: "bar",
        data: { labels: o.by_ware.map(x=>x.ware), datasets: [{ label: "Ware", data: o.by_ware.map(x=>x.count) }] },
        options: { plugins: { title: { display: true, text: "Ware distribution" } } },
      });
      new Chart(document.getElementById("potteryAnnoChart"), {
        type: "bar",
        data: { labels: o.by_anno.map(x=>x.anno), datasets: [{ label: "By year", data: o.by_anno.map(x=>x.count) }] },
        options: { plugins: { title: { display: true, text: "Pottery by year" } } },
      });
    });
})();
</script>
```

- [ ] **Step 3: Smoke test**

Run:
```bash
python -c "
from pyarchinit_mini.web_interface.app import create_app
a = create_app(); a.config['LOGIN_DISABLED']=True
c = a.test_client(); r = c.get('/analytics')
print('status', r.status_code, 'has potteryFormChart:', b'potteryFormChart' in r.data)
"
```

Expected: `status 200, has potteryFormChart: True` (or another success status if `/analytics` is at a different path — adjust to match the real route).

- [ ] **Step 4: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/analytics/dashboard.html
git commit -m "feat(analytics): pottery distribution charts + MNI card"
```

---

## Task 21: Desktop GUI panel

**Files:**
- Create: `pyarchinit_mini/desktop_gui/pottery_panel.py`
- Modify: `pyarchinit_mini/desktop_gui/main_window.py`

- [ ] **Step 1: Check existing tab registration**

Run:
```bash
grep -nE "show_tab|notebook.add|self\.notebook" pyarchinit_mini/desktop_gui/main_window.py | head -20
```

Identify the pattern (`self.notebook.add(self.inventory_panel, text=…)`).

- [ ] **Step 2: Create pottery panel**

Create `pyarchinit_mini/desktop_gui/pottery_panel.py`:

```python
"""Tkinter panel for the Pottery records tab."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from ..services.pottery_service import PotteryService
from ..services.pottery_dto import PotteryDTO


class PotteryPanel(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.svc = PotteryService(db_manager)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=4, pady=4)
        for text, cmd in [
            ("+ New", self.on_new), ("Edit", self.on_edit),
            ("Delete", self.on_delete), ("Refresh", self.refresh),
        ]:
            ttk.Button(toolbar, text=text, command=cmd).pack(side="left", padx=2)

        cols = ("id_rep", "sito", "area", "us", "form", "fabric", "qty")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=80, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)
        self.tree.bind("<Double-1>", lambda e: self.on_edit())

        self.status = ttk.Label(self, text="", anchor="w")
        self.status.pack(fill="x", padx=4, pady=2)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        items, total = self.svc.get_all_pottery(page=1, size=1000)
        for p in items:
            self.tree.insert(
                "", "end",
                values=(p.id_rep, p.sito, p.area or "", p.us or "",
                        p.form or "", p.fabric or "", p.qty or ""),
            )
        self.status.config(text=f"{total} record(s)")

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def on_new(self):
        from .pottery_dialog_extended import PotteryDialog
        dlg = PotteryDialog(self, self.svc)
        if dlg.result_id is not None:
            self.refresh()

    def on_edit(self):
        id_rep = self._selected_id()
        if id_rep is None:
            messagebox.showinfo("Pottery", "Select a row first.")
            return
        from .pottery_dialog_extended import PotteryDialog
        dlg = PotteryDialog(self, self.svc, id_rep=id_rep)
        if dlg.result_id is not None:
            self.refresh()

    def on_delete(self):
        id_rep = self._selected_id()
        if id_rep is None:
            messagebox.showinfo("Pottery", "Select a row first.")
            return
        if not messagebox.askyesno("Pottery", f"Delete #{id_rep}?"):
            return
        if self.svc.delete_pottery(id_rep):
            self.refresh()
```

- [ ] **Step 3: Register tab in `main_window.py`**

Edit `pyarchinit_mini/desktop_gui/main_window.py`:

Below the existing tab registrations (search for `self.notebook.add(self.inventory_panel`), append a similar block:

```python
        from .pottery_panel import PotteryPanel
        self.pottery_panel = PotteryPanel(self.notebook, self.db_manager)
        self.notebook.add(self.pottery_panel, text=_("Pottery"))
        self._tab_keys["pottery"] = self.pottery_panel
```

(Use the same `self._tab_keys` map if the codebase uses one; if not, omit that line — check by grepping `_tab_keys` first.)

Also add to the View menu (`main_window.py:163-166`):

```python
        view_menu.add_command(label=_("Pottery"), command=lambda: self.show_tab("pottery"))
```

- [ ] **Step 4: Smoke import test**

Run:
```bash
python -c "
import tkinter
root = tkinter.Tk(); root.withdraw()
from pyarchinit_mini.desktop_gui.pottery_panel import PotteryPanel
print('PotteryPanel import OK')
"
```

Expected: `PotteryPanel import OK`.

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/desktop_gui/pottery_panel.py pyarchinit_mini/desktop_gui/main_window.py
git commit -m "feat(desktop): pottery panel + View menu entry"
```

---

## Task 22: Desktop GUI dialog

**Files:**
- Create: `pyarchinit_mini/desktop_gui/pottery_dialog_extended.py`

- [ ] **Step 1: Implement minimal dialog**

Create `pyarchinit_mini/desktop_gui/pottery_dialog_extended.py`:

```python
"""Modal dialog for creating/editing a Pottery record."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from ..services.pottery_service import PotteryService

_TEXT_FIELDS = (
    "sito", "area", "sector", "material", "form", "specific_form",
    "specific_shape", "fabric", "ware", "munsell", "percent",
    "surf_trat", "exdeco", "intdeco", "wheel_made",
    "descrip_ex_deco", "descrip_in_deco", "note",
    "photo", "drawing",
)
_INT_FIELDS = ("id_number", "us", "box", "anno", "qty", "bag")
_NUM_FIELDS = (
    "diametro_max", "diametro_rim", "diametro_bottom",
    "diametro_height", "diametro_preserved",
)


class PotteryDialog(tk.Toplevel):
    def __init__(self, parent, svc: PotteryService, id_rep: int | None = None):
        super().__init__(parent)
        self.title(f"Pottery — {'New' if id_rep is None else f'#{id_rep}'}")
        self.svc = svc
        self.id_rep = id_rep
        self.result_id = None
        self.vars = {}

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        desc = ttk.Frame(nb); nb.add(desc, text="Description data")
        tech = ttk.Frame(nb); nb.add(tech, text="Technical Data")
        supp = ttk.Frame(nb); nb.add(supp, text="Supplements")

        desc_fields = ["sito", "area", "us", "sector", "anno", "box", "bag",
                       "id_number", "material", "form", "specific_form",
                       "specific_shape", "photo", "drawing", "note"]
        tech_fields = ["fabric", "ware", "munsell", "percent", "surf_trat",
                       "wheel_made", "exdeco", "intdeco",
                       "descrip_ex_deco", "descrip_in_deco", "qty",
                       "diametro_max", "diametro_rim", "diametro_bottom",
                       "diametro_height", "diametro_preserved"]

        self._build_fields(desc, desc_fields)
        self._build_fields(tech, tech_fields)
        ttk.Label(supp, text="Bibliography integration coming in a future release.").pack(padx=8, pady=8)

        btn_row = ttk.Frame(self); btn_row.pack(fill="x", padx=8, pady=8)
        ttk.Button(btn_row, text="Save", command=self._save).pack(side="right", padx=4)
        ttk.Button(btn_row, text="Cancel", command=self.destroy).pack(side="right")

        if id_rep is not None:
            self._load()

        self.transient(parent); self.grab_set(); self.wait_window()

    def _build_fields(self, parent, fields):
        for i, name in enumerate(fields):
            ttk.Label(parent, text=name).grid(row=i, column=0, sticky="w", padx=4, pady=2)
            v = tk.StringVar()
            self.vars[name] = v
            ttk.Entry(parent, textvariable=v, width=40).grid(row=i, column=1, sticky="we", padx=4, pady=2)
        parent.columnconfigure(1, weight=1)

    def _load(self):
        p = self.svc.get_pottery_by_id(self.id_rep)
        if not p:
            return
        for name, var in self.vars.items():
            val = getattr(p, name, None)
            var.set("" if val is None else str(val))

    def _collect(self):
        data = {}
        for name, var in self.vars.items():
            raw = var.get().strip()
            if raw == "":
                continue
            if name in _INT_FIELDS:
                try: data[name] = int(raw)
                except ValueError: continue
            elif name in _NUM_FIELDS:
                try: data[name] = float(raw)
                except ValueError: continue
            else:
                data[name] = raw
        return data

    def _save(self):
        data = self._collect()
        try:
            if self.id_rep is None:
                p = self.svc.create_pottery(data)
                self.result_id = p.id_rep
            else:
                self.svc.update_pottery(self.id_rep, data)
                self.result_id = self.id_rep
        except ValueError as e:
            messagebox.showerror("Validation", str(e))
            return
        self.destroy()
```

- [ ] **Step 2: Smoke import test**

Run:
```bash
python -c "from pyarchinit_mini.desktop_gui.pottery_dialog_extended import PotteryDialog; print('OK')"
```

Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add pyarchinit_mini/desktop_gui/pottery_dialog_extended.py
git commit -m "feat(desktop): pottery New/Edit dialog with 3 tabs"
```

---

## Task 23: Migrate-database wizard UI entry

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/admin/database.html`

- [ ] **Step 1: Locate migrate table picker block**

Run:
```bash
grep -nE "inventario_materiali_table|migrate.*table|tables_to_migrate|name=\"tables\"" pyarchinit_mini/web_interface/templates/admin/database.html | head -10
```

If there is a static checkbox list, find the `inventario_materiali_table` checkbox.

- [ ] **Step 2: Add pottery checkbox**

Immediately after the `inventario_materiali_table` checkbox `<label>` block, append (use the exact pattern used by neighbors):

```jinja2
<div class="form-check">
  <input class="form-check-input" type="checkbox" name="migrate_tables" value="pottery_table" id="mt-pottery" checked>
  <label class="form-check-label" for="mt-pottery">pottery_table</label>
</div>
```

(If the migrate wizard auto-detects tables from source DB introspection instead of using a fixed list, this step is a no-op — verify with the grep first.)

- [ ] **Step 3: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/admin/database.html
git commit -m "feat(admin): pottery_table checkbox in migrate-database wizard"
```

---

## Task 24: Version bump + final integration sweep

**Files:**
- Modify: `pyarchinit_mini/__init__.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Bump version in `__init__.py`**

Edit `pyarchinit_mini/__init__.py:26`:

Replace:
```python
__version__ = "2.1.59"
```

With:
```python
__version__ = "2.1.60"
```

- [ ] **Step 2: Bump version in `pyproject.toml`**

Edit `pyproject.toml:7`:

Replace:
```toml
version = "2.1.59"
```

With:
```toml
version = "2.1.60"
```

- [ ] **Step 3: Run full test suite**

Run:
```bash
pytest tests/unit/test_pottery_model.py tests/unit/test_pottery_dto.py tests/unit/test_pottery_service.py tests/integration/test_pottery_routes.py tests/integration/test_pottery_legacy_upgrade.py tests/integration/test_pottery_excel_roundtrip.py -v
```

Expected: all green (≈ 35+ tests).

- [ ] **Step 4: Run any pre-existing test suite to confirm no regressions**

Run:
```bash
pytest tests/ -x --ignore=tests/integration/test_pottery_routes.py --ignore=tests/integration/test_pottery_legacy_upgrade.py --ignore=tests/integration/test_pottery_excel_roundtrip.py --ignore=tests/unit/test_pottery_model.py --ignore=tests/unit/test_pottery_dto.py --ignore=tests/unit/test_pottery_service.py -v 2>&1 | tail -30
```

Expected: no new failures (existing tests pass — or fail with the same baseline they had before).

- [ ] **Step 5: Manual smoke test in browser**

Run:
```bash
python -c "
from pyarchinit_mini.web_interface.app import create_app
import threading, time, urllib.request
a = create_app(); a.config['LOGIN_DISABLED']=True
t = threading.Thread(target=lambda: a.run(port=5099, use_reloader=False), daemon=True); t.start()
time.sleep(2)
for path in ['/pottery', '/pottery/create', '/api/pottery/forms', '/api/pottery/stats']:
    code = urllib.request.urlopen(f'http://127.0.0.1:5099{path}').getcode()
    print(path, '->', code)
"
```

Expected: `200` for all four paths.

- [ ] **Step 6: Commit version bump**

```bash
git add pyarchinit_mini/__init__.py pyproject.toml
git commit -m "chore: bump version to 2.1.60 — pottery sheet"
```

---

## Task 25: Build, push, release

**Files:** none (release activities)

- [ ] **Step 1: Build wheel + sdist**

Run:
```bash
rm -rf dist build *.egg-info && python -m build
```

Expected: `dist/pyarchinit_mini-2.1.60-py3-none-any.whl` and `dist/pyarchinit-mini-2.1.60.tar.gz` produced.

- [ ] **Step 2: Push commits to GitHub**

Run:
```bash
git push origin main
```

- [ ] **Step 3: Upload to PyPI**

Run:
```bash
python -m twine upload dist/pyarchinit_mini-2.1.60* dist/pyarchinit-mini-2.1.60*
```

Expected: 2 files uploaded to <https://pypi.org/project/pyarchinit-mini/2.1.60/>.

- [ ] **Step 4: Wait for PyPI CDN propagation**

Run:
```bash
until pip index versions pyarchinit-mini 2>/dev/null | grep -q '2\.1\.60'; do sleep 4; done && echo "available"
```

Expected: `available`.

- [ ] **Step 5: Deploy to Adarte via expect**

Run (use the established expect script pattern from v2.1.55–2.1.59):
```bash
expect <<'EOF'
set timeout 300
spawn ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ganesh@10.0.1.13 "source /home/ganesh/pmini_env/bin/activate && pip install --upgrade --no-deps --no-cache-dir -i https://pypi.org/simple/ pyarchinit-mini==2.1.60 && python -c 'import pyarchinit_mini; print(pyarchinit_mini.__version__)' && screen -S pmini -X quit; screen -dmS pmini bash -c 'source /home/ganesh/pmini_env/bin/activate && pyarchinit-mini-web' && echo DONE"
expect -re "(?i)password:" { send -- "***REMOVED***\r"; exp_continue }
expect "DONE"
EOF
```

Expected: prints `2.1.60` and `DONE`.

- [ ] **Step 6: Smoke test Adarte web endpoint**

Run:
```bash
curl -sI http://10.0.1.13:5000/ | head -5
```

Expected: `HTTP/1.1 302 FOUND` (redirect to login) — confirms the server is up.

---

## Notes for the engineer

- **TDD discipline:** every task is *write failing test → run it red → implement minimal → run it green → commit*. Don't merge steps.
- **Don't add features not in this plan.** The spec is the source of truth.
- **If a step fails:** stop, read the error, fix root cause. Don't `--no-verify` past hook failures.
- **Pre-existing test failures** in unrelated suites are fine to leave — verify they were failing on `main` too before claiming regression.
- **Bibliography sub-tab** is intentionally a placeholder; do not implement it.
- **OpenAI 5.5 / AI admin / multimedia overflow fix / backup module** are separate features and shipped under their own version bumps after pottery.
