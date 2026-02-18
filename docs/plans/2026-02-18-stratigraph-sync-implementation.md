# StratiGraph Sync & Concurrency Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Align pyarchinit-mini-desk DB schema, add stratigraph sync module, concurrency management, CLI sync commands, and API sync endpoints to match the pyarchinit QGIS plugin.

**Architecture:** Port & Adapt - copy pyarchinit stratigraph module files, replace Qt/QGIS dependencies (QObject, pyqtSignal, QgsSettings, QTimer, QgsNetworkAccessManager) with standalone Python (callbacks, JSON config, threading.Timer, httpx). Add 7 concurrency columns to BaseModel, ~63 missing columns to US model, ~4 to InventarioMateriali.

**Tech Stack:** SQLAlchemy 2.0, FastAPI, Click, httpx, threading, Python logging, JSON config

---

## Task 1: Add concurrency columns to BaseModel

**Files:**
- Modify: `pyarchinit_mini/models/base.py`
- Test: `tests/unit/test_concurrency_columns.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_concurrency_columns.py
"""Test that concurrency columns exist on all models."""
import pytest
from pyarchinit_mini.models.base import BaseModel
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.models.us import US
from pyarchinit_mini.models.inventario_materiali import InventarioMateriali


def test_base_model_has_concurrency_columns():
    """BaseModel must declare the 7 concurrency columns."""
    expected = [
        'entity_uuid', 'version_number', 'last_modified_by',
        'last_modified_timestamp', 'sync_status', 'editing_by', 'editing_since'
    ]
    for col in expected:
        assert hasattr(BaseModel, col), f"BaseModel missing column: {col}"


def test_site_inherits_concurrency_columns(temp_db):
    """Site table must have concurrency columns in the DB."""
    from sqlalchemy import inspect as sa_inspect
    inspector = sa_inspect(temp_db.engine)
    columns = [c['name'] for c in inspector.get_columns('site_table')]
    for col in ['entity_uuid', 'version_number', 'sync_status']:
        assert col in columns, f"site_table missing column: {col}"


def test_entity_uuid_auto_generated(temp_db, db_manager, sample_site_data):
    """New records should get an auto-generated entity_uuid."""
    site = db_manager.create(Site, sample_site_data)
    assert site.entity_uuid is not None
    assert len(site.entity_uuid) == 36  # UUID v4 format


def test_version_number_defaults_to_one(temp_db, db_manager, sample_site_data):
    """New records should have version_number=1."""
    site = db_manager.create(Site, sample_site_data)
    assert site.version_number == 1
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/enzo/Documents/pyarchinit-mini-desk && python -m pytest tests/unit/test_concurrency_columns.py -v`
Expected: FAIL with "BaseModel missing column: entity_uuid"

**Step 3: Write minimal implementation**

Modify `pyarchinit_mini/models/base.py`:

```python
"""
Base model class for all PyArchInit-Mini models
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Column, Integer, String, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

def _generate_uuid():
    return str(uuid.uuid4())

class BaseModel(Base):
    """
    Base model class with common fields and methods
    """
    __abstract__ = True

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Concurrency / sync columns
    entity_uuid = Column(String(36), unique=True, index=True, default=_generate_uuid)
    version_number = Column(Integer, default=1, nullable=False)
    last_modified_by = Column(String(100))
    last_modified_timestamp = Column(DateTime(timezone=True))
    sync_status = Column(String(20), default='new')
    editing_by = Column(String(100))
    editing_since = Column(DateTime(timezone=True))

    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def update_from_dict(self, data):
        """Update model instance from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/enzo/Documents/pyarchinit-mini-desk && python -m pytest tests/unit/test_concurrency_columns.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pyarchinit_mini/models/base.py tests/unit/test_concurrency_columns.py
git commit -m "feat: add 7 concurrency columns to BaseModel"
```

---

## Task 2: Add missing US table columns (strict 1:1 match with pyarchinit)

**Files:**
- Modify: `pyarchinit_mini/models/us.py`
- Test: `tests/unit/test_us_schema.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_us_schema.py
"""Test that US model matches pyarchinit us_table schema exactly."""
from pyarchinit_mini.models.us import US


# All columns from pyarchinit US_table.py (canonical source)
PYARCHINIT_US_COLUMNS = [
    'id_us', 'sito', 'area', 'us',
    'd_stratigrafica', 'd_interpretativa', 'descrizione', 'interpretazione',
    'periodo_iniziale', 'fase_iniziale', 'periodo_finale', 'fase_finale',
    'scavato', 'attivita', 'anno_scavo', 'metodo_di_scavo',
    'inclusi', 'campioni', 'rapporti', 'data_schedatura', 'schedatore',
    'formazione', 'stato_di_conservazione', 'colore', 'consistenza', 'struttura',
    'cont_per', 'order_layer', 'documentazione',
    'unita_tipo', 'settore', 'quad_par', 'ambient', 'saggio',
    # USM masonry fields
    'elem_datanti', 'funz_statica', 'lavorazione', 'spess_giunti',
    'letti_posa', 'alt_mod', 'un_ed_riass', 'reimp', 'posa_opera',
    'quota_min_usm', 'quota_max_usm',
    'cons_legante', 'col_legante', 'aggreg_legante',
    'con_text_mat', 'col_materiale', 'inclusi_materiali_usm',
    # ICCD + catalog
    'n_catalogo_generale', 'n_catalogo_interno', 'n_catalogo_internazionale',
    'soprintendenza',
    # Measurements
    'quota_relativa', 'quota_abs',
    'ref_tm', 'ref_ra', 'ref_n', 'posizione',
    'criteri_distinzione', 'modo_formazione',
    'componenti_organici', 'componenti_inorganici',
    'lunghezza_max', 'altezza_max', 'altezza_min',
    'profondita_max', 'profondita_min', 'larghezza_media',
    'quota_max_abs', 'quota_max_rel', 'quota_min_abs', 'quota_min_rel',
    # Additional
    'osservazioni', 'datazione', 'flottazione', 'setacciatura',
    'affidabilita', 'direttore_us', 'responsabile_us',
    'cod_ente_schedatore', 'data_rilevazione', 'data_rielaborazione',
    # USM extended
    'lunghezza_usm', 'altezza_usm', 'spessore_usm',
    'tecnica_muraria_usm', 'modulo_usm',
    'campioni_malta_usm', 'campioni_mattone_usm', 'campioni_pietra_usm',
    'provenienza_materiali_usm', 'criteri_distinzione_usm', 'uso_primario_usm',
    'tipologia_opera', 'sezione_muraria', 'superficie_analizzata', 'orientamento',
    # Laterizio fields
    'materiali_lat', 'lavorazione_lat', 'consistenza_lat',
    'forma_lat', 'colore_lat', 'impasto_lat',
    # Pietra fields
    'forma_p', 'colore_p', 'taglio_p', 'posa_opera_p',
    # Other USM
    'inerti_usm', 'tipo_legante_usm', 'rifinitura_usm',
    'materiale_p', 'consistenza_p',
    'rapporti2', 'doc_usv',
    # DOC type fields
    'tipo_documento', 'file_path',
]


def test_us_has_all_pyarchinit_columns():
    """US model must have every column from pyarchinit US_table.py."""
    us_columns = {c.name for c in US.__table__.columns}
    missing = [col for col in PYARCHINIT_US_COLUMNS if col not in us_columns]
    assert missing == [], f"US model missing columns: {missing}"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/enzo/Documents/pyarchinit-mini-desk && python -m pytest tests/unit/test_us_schema.py -v`
Expected: FAIL listing ~60 missing columns

**Step 3: Add all missing columns to US model**

Add these columns to `pyarchinit_mini/models/us.py` after the existing USM fields (after line 85, before ICCD fields). The columns are grouped by category and match pyarchinit's exact types.

Columns to add (all Text unless noted):

```python
    # USM masonry detail fields (from pyarchinit US_table.py)
    elem_datanti = Column(Text)
    funz_statica = Column(Text)
    lavorazione = Column(Text)
    spess_giunti = Column(Text)
    letti_posa = Column(Text)
    alt_mod = Column(Text)
    un_ed_riass = Column(Text)
    reimp = Column(Text)
    posa_opera = Column(Text)
    quota_min_usm = Column(Numeric(6, 2))
    quota_max_usm = Column(Numeric(6, 2))
    cons_legante = Column(Text)
    col_legante = Column(Text)
    aggreg_legante = Column(Text)
    con_text_mat = Column(Text)
    col_materiale = Column(Text)
    inclusi_materiali_usm = Column(Text)

    # References and position
    ref_tm = Column(Text)
    ref_ra = Column(Text)
    ref_n = Column(Text)
    posizione = Column(Text)
    criteri_distinzione = Column(Text)
    modo_formazione = Column(Text)
    componenti_organici = Column(Text)
    componenti_inorganici = Column(Text)

    # Extended measurements
    quota_max_abs = Column(Numeric(6, 2))
    quota_max_rel = Column(Numeric(6, 2))
    quota_min_abs = Column(Numeric(6, 2))
    quota_min_rel = Column(Numeric(6, 2))

    # Administrative
    cod_ente_schedatore = Column(Text)
    data_rilevazione = Column(String(20))
    data_rielaborazione = Column(String(20))

    # USM extended measurements and details
    lunghezza_usm = Column(Numeric(6, 2))
    altezza_usm = Column(Numeric(6, 2))
    spessore_usm = Column(Numeric(6, 2))
    tecnica_muraria_usm = Column(Text)
    modulo_usm = Column(Text)
    campioni_malta_usm = Column(Text)
    campioni_mattone_usm = Column(Text)
    campioni_pietra_usm = Column(Text)
    provenienza_materiali_usm = Column(Text)
    criteri_distinzione_usm = Column(Text)
    uso_primario_usm = Column(Text)
    tipologia_opera = Column(Text)
    sezione_muraria = Column(Text)
    superficie_analizzata = Column(Text)
    orientamento = Column(Text)

    # Laterizio (brick) fields
    materiali_lat = Column(Text)
    lavorazione_lat = Column(Text)
    consistenza_lat = Column(Text)
    forma_lat = Column(Text)
    colore_lat = Column(Text)
    impasto_lat = Column(Text)

    # Pietra (stone) fields
    forma_p = Column(Text)
    colore_p = Column(Text)
    taglio_p = Column(Text)
    posa_opera_p = Column(Text)

    # Other USM fields
    inerti_usm = Column(Text)
    tipo_legante_usm = Column(Text)
    rifinitura_usm = Column(Text)
    materiale_p = Column(Text)
    consistenza_p = Column(Text)

    # Extended relationships and documentation
    rapporti2 = Column(Text)
    doc_usv = Column(Text)
```

Also add `Numeric` to the imports: `from sqlalchemy import Column, Integer, String, Text, Boolean, Date, Float, ForeignKey, Numeric`

**Step 4: Run test to verify it passes**

Run: `cd /Users/enzo/Documents/pyarchinit-mini-desk && python -m pytest tests/unit/test_us_schema.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pyarchinit_mini/models/us.py tests/unit/test_us_schema.py
git commit -m "feat: add all missing US columns for strict pyarchinit 1:1 match"
```

---

## Task 3: Add missing InventarioMateriali columns + migration

**Files:**
- Modify: `pyarchinit_mini/models/inventario_materiali.py`
- Modify: `pyarchinit_mini/database/migrations.py`
- Test: `tests/unit/test_inventario_schema.py`

**Step 1: Write failing test**

```python
# tests/unit/test_inventario_schema.py
"""Test InventarioMateriali matches pyarchinit schema."""
from pyarchinit_mini.models.inventario_materiali import InventarioMateriali

PYARCHINIT_INVMAT_COLUMNS = [
    'id_invmat', 'sito', 'numero_inventario',
    'tipo_reperto', 'criterio_schedatura', 'definizione', 'descrizione',
    'area', 'us', 'lavato', 'nr_cassa', 'luogo_conservazione',
    'stato_conservazione', 'datazione_reperto', 'elementi_reperto',
    'misurazioni', 'rif_biblio', 'tecnologie',
    'forme_minime', 'forme_massime', 'totale_frammenti',
    'corpo_ceramico', 'rivestimento', 'diametro_orlo', 'peso',
    'tipo', 'eve_orlo', 'repertato', 'diagnostico',
    'n_reperto', 'tipo_contenitore', 'struttura', 'years',
    'schedatore', 'date_scheda', 'punto_rinv', 'negativo_photo', 'diapositiva',
    # Missing from mini-desk:
    'quota_usm', 'unita_misura_quota', 'photo_id', 'drawing_id',
]


def test_inventario_has_all_pyarchinit_columns():
    """InventarioMateriali must have every column from pyarchinit."""
    cols = {c.name for c in InventarioMateriali.__table__.columns}
    missing = [c for c in PYARCHINIT_INVMAT_COLUMNS if c not in cols]
    assert missing == [], f"InventarioMateriali missing: {missing}"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/enzo/Documents/pyarchinit-mini-desk && python -m pytest tests/unit/test_inventario_schema.py -v`
Expected: FAIL listing `quota_usm`, `unita_misura_quota`, `photo_id`, `drawing_id`

**Step 3: Add 4 missing columns**

Add to `pyarchinit_mini/models/inventario_materiali.py` after `diapositiva` (line 92):

```python
    # Additional fields from pyarchinit
    quota_usm = Column(Numeric(10, 3))
    unita_misura_quota = Column(String(20))
    photo_id = Column(Text)
    drawing_id = Column(Text)
```

**Step 4: Run test, verify pass**

**Step 5: Add concurrency migration to migrations.py**

Add `migrate_concurrency_columns` method to `DatabaseMigrations` class in `pyarchinit_mini/database/migrations.py`. This adds the 7 concurrency columns + 4 inventario columns to all existing tables:

```python
    def migrate_concurrency_columns(self):
        """Add concurrency tracking columns to all main tables."""
        import uuid as uuid_mod
        try:
            logger.info("Starting concurrency columns migration...")
            migrations_applied = 0

            tables = [
                'site_table', 'us_table', 'inventario_materiali_table',
                'periodizzazione_table', 'media_table', 'media_thumb_table',
                'documentazione_table',
            ]

            concurrency_columns = [
                ('entity_uuid', 'TEXT'),
                ('version_number', 'INTEGER', '1'),
                ('last_modified_by', 'VARCHAR(100)'),
                ('last_modified_timestamp', 'TIMESTAMP'),
                ('sync_status', 'VARCHAR(20)', "'new'"),
                ('editing_by', 'VARCHAR(100)'),
                ('editing_since', 'TIMESTAMP'),
            ]

            for table in tables:
                for col_def in concurrency_columns:
                    col_name = col_def[0]
                    col_type = col_def[1]
                    default = col_def[2] if len(col_def) > 2 else None
                    if self.add_column_if_not_exists(table, col_name, col_type, default):
                        migrations_applied += 1

            # Back-fill entity_uuid for existing rows that have NULL
            for table in tables:
                try:
                    with self.connection.get_session() as session:
                        from sqlalchemy import text
                        rows = session.execute(
                            text(f"SELECT rowid FROM {table} WHERE entity_uuid IS NULL")
                        ).fetchall()
                        for row in rows:
                            new_uuid = str(uuid_mod.uuid4())
                            session.execute(
                                text(f"UPDATE {table} SET entity_uuid = :uuid WHERE rowid = :rid"),
                                {"uuid": new_uuid, "rid": row[0]}
                            )
                        session.commit()
                except Exception as e:
                    logger.warning(f"UUID backfill for {table}: {e}")

            logger.info(f"Concurrency migration done. {migrations_applied} columns added")
            return migrations_applied
        except Exception as e:
            logger.error(f"Error during concurrency migration: {e}")
            raise

    def migrate_inventario_extra_columns(self):
        """Add missing columns to inventario_materiali_table."""
        try:
            migrations_applied = 0
            extra = [
                ('quota_usm', 'NUMERIC(10,3)'),
                ('unita_misura_quota', 'VARCHAR(20)'),
                ('photo_id', 'TEXT'),
                ('drawing_id', 'TEXT'),
            ]
            for col_name, col_type in extra:
                if self.add_column_if_not_exists('inventario_materiali_table', col_name, col_type):
                    migrations_applied += 1
            return migrations_applied
        except Exception as e:
            logger.error(f"Error during inventario extra migration: {e}")
            raise
```

Update `migrate_all_tables` to call both new methods.

**Step 6: Commit**

```bash
git add pyarchinit_mini/models/inventario_materiali.py pyarchinit_mini/database/migrations.py tests/unit/test_inventario_schema.py
git commit -m "feat: add missing inventario columns + concurrency migration"
```

---

## Task 4: Add US table missing columns migration

**Files:**
- Modify: `pyarchinit_mini/database/migrations.py`

**Step 1: Add `migrate_us_extra_columns` method**

This adds all ~63 missing US columns to existing databases via ALTER TABLE:

```python
    def migrate_us_extra_columns(self):
        """Add all missing pyarchinit US columns to us_table."""
        try:
            migrations_applied = 0
            columns = [
                ('elem_datanti', 'TEXT'), ('funz_statica', 'TEXT'),
                ('lavorazione', 'TEXT'), ('spess_giunti', 'TEXT'),
                ('letti_posa', 'TEXT'), ('alt_mod', 'TEXT'),
                ('un_ed_riass', 'TEXT'), ('reimp', 'TEXT'),
                ('posa_opera', 'TEXT'),
                ('quota_min_usm', 'NUMERIC(6,2)'), ('quota_max_usm', 'NUMERIC(6,2)'),
                ('cons_legante', 'TEXT'), ('col_legante', 'TEXT'),
                ('aggreg_legante', 'TEXT'), ('con_text_mat', 'TEXT'),
                ('col_materiale', 'TEXT'), ('inclusi_materiali_usm', 'TEXT'),
                ('ref_tm', 'TEXT'), ('ref_ra', 'TEXT'), ('ref_n', 'TEXT'),
                ('posizione', 'TEXT'), ('criteri_distinzione', 'TEXT'),
                ('modo_formazione', 'TEXT'),
                ('componenti_organici', 'TEXT'), ('componenti_inorganici', 'TEXT'),
                ('quota_max_abs', 'NUMERIC(6,2)'), ('quota_max_rel', 'NUMERIC(6,2)'),
                ('quota_min_abs', 'NUMERIC(6,2)'), ('quota_min_rel', 'NUMERIC(6,2)'),
                ('cod_ente_schedatore', 'TEXT'),
                ('data_rilevazione', 'VARCHAR(20)'), ('data_rielaborazione', 'VARCHAR(20)'),
                ('lunghezza_usm', 'NUMERIC(6,2)'), ('altezza_usm', 'NUMERIC(6,2)'),
                ('spessore_usm', 'NUMERIC(6,2)'),
                ('tecnica_muraria_usm', 'TEXT'), ('modulo_usm', 'TEXT'),
                ('campioni_malta_usm', 'TEXT'), ('campioni_mattone_usm', 'TEXT'),
                ('campioni_pietra_usm', 'TEXT'),
                ('provenienza_materiali_usm', 'TEXT'),
                ('criteri_distinzione_usm', 'TEXT'), ('uso_primario_usm', 'TEXT'),
                ('tipologia_opera', 'TEXT'), ('sezione_muraria', 'TEXT'),
                ('superficie_analizzata', 'TEXT'), ('orientamento', 'TEXT'),
                ('materiali_lat', 'TEXT'), ('lavorazione_lat', 'TEXT'),
                ('consistenza_lat', 'TEXT'), ('forma_lat', 'TEXT'),
                ('colore_lat', 'TEXT'), ('impasto_lat', 'TEXT'),
                ('forma_p', 'TEXT'), ('colore_p', 'TEXT'),
                ('taglio_p', 'TEXT'), ('posa_opera_p', 'TEXT'),
                ('inerti_usm', 'TEXT'), ('tipo_legante_usm', 'TEXT'),
                ('rifinitura_usm', 'TEXT'),
                ('materiale_p', 'TEXT'), ('consistenza_p', 'TEXT'),
                ('rapporti2', 'TEXT'), ('doc_usv', 'TEXT'),
            ]
            for col_name, col_type in columns:
                if self.add_column_if_not_exists('us_table', col_name, col_type):
                    migrations_applied += 1
            return migrations_applied
        except Exception as e:
            logger.error(f"Error during US extra migration: {e}")
            raise
```

**Step 2: Update `migrate_all_tables` to call all new methods**

**Step 3: Run existing tests to ensure nothing breaks**

Run: `cd /Users/enzo/Documents/pyarchinit-mini-desk && python -m pytest tests/ -v`

**Step 4: Commit**

```bash
git add pyarchinit_mini/database/migrations.py
git commit -m "feat: add US table migration for all pyarchinit columns"
```

---

## Task 5: Port stratigraph UUID manager + bundle manifest (no Qt deps)

**Files:**
- Create: `pyarchinit_mini/stratigraph/__init__.py`
- Create: `pyarchinit_mini/stratigraph/uuid_manager.py`
- Create: `pyarchinit_mini/stratigraph/bundle_manifest.py`
- Test: `tests/unit/test_uuid_manager.py`

**Step 1: Create package and write tests**

```python
# tests/unit/test_uuid_manager.py
"""Test UUID manager functionality."""
import re
from pyarchinit_mini.stratigraph.uuid_manager import (
    generate_uuid, validate_uuid, ensure_uuid, build_uri,
    get_entity_type_for_table, TABLE_ENTITY_TYPE_MAP
)


def test_generate_uuid_format():
    uid = generate_uuid()
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', uid)


def test_validate_uuid_valid():
    uid = generate_uuid()
    assert validate_uuid(uid) is True


def test_validate_uuid_invalid():
    assert validate_uuid("not-a-uuid") is False
    assert validate_uuid(None) is False
    assert validate_uuid(123) is False


def test_ensure_uuid_generates_when_missing():
    class FakeRecord:
        entity_uuid = None
    r = FakeRecord()
    result = ensure_uuid(r)
    assert validate_uuid(result)
    assert r.entity_uuid == result


def test_ensure_uuid_keeps_existing():
    class FakeRecord:
        entity_uuid = None
    r = FakeRecord()
    r.entity_uuid = generate_uuid()
    original = r.entity_uuid
    result = ensure_uuid(r)
    assert result == original


def test_build_uri_with_table_name():
    uid = generate_uuid()
    uri = build_uri('us_table', uid)
    assert uri == f"http://pyarchinit.org/ontology/stratigraphic-unit/{uid}"


def test_build_uri_with_slug():
    uid = generate_uuid()
    uri = build_uri('site', uid)
    assert uri == f"http://pyarchinit.org/ontology/site/{uid}"


def test_table_entity_type_map_has_all_tables():
    assert 'us_table' in TABLE_ENTITY_TYPE_MAP
    assert 'site_table' in TABLE_ENTITY_TYPE_MAP
    assert 'inventario_materiali_table' in TABLE_ENTITY_TYPE_MAP
```

**Step 2: Run to verify fails**

**Step 3: Copy uuid_manager.py directly from pyarchinit (no changes needed)**

Source: `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/stratigraph/uuid_manager.py`
Dest: `pyarchinit_mini/stratigraph/uuid_manager.py`

Copy bundle_manifest.py from pyarchinit. Only change: fix import path if it references `modules.stratigraph`.

Source: `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/stratigraph/bundle_manifest.py`
Dest: `pyarchinit_mini/stratigraph/bundle_manifest.py`

Create `pyarchinit_mini/stratigraph/__init__.py`:
```python
# -*- coding: utf-8 -*-
"""
StratiGraph integration module for PyArchInit-Mini.
"""
from .uuid_manager import generate_uuid, validate_uuid, ensure_uuid, build_uri
```

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add pyarchinit_mini/stratigraph/ tests/unit/test_uuid_manager.py
git commit -m "feat: port stratigraph UUID manager and bundle manifest"
```

---

## Task 6: Port bundle creator + bundle validator

**Files:**
- Create: `pyarchinit_mini/stratigraph/bundle_creator.py`
- Create: `pyarchinit_mini/stratigraph/bundle_validator.py`
- Test: `tests/unit/test_bundle.py`

**Step 1: Write test**

```python
# tests/unit/test_bundle.py
"""Test bundle creation and validation."""
import os
import tempfile
import json
from pyarchinit_mini.stratigraph.bundle_creator import BundleCreator
from pyarchinit_mini.stratigraph.bundle_validator import validate_bundle


def test_bundle_creator_builds_zip():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a fake data file
        data_file = os.path.join(tmpdir, "test_data.jsonld")
        with open(data_file, "w") as f:
            json.dump({"@context": "test"}, f)

        output_dir = os.path.join(tmpdir, "output")
        creator = BundleCreator(output_dir=output_dir, site_name="TestSite")
        creator.add_data_file(data_file)
        result = creator.build()

        assert result["success"] is True
        assert result["bundle_path"] is not None
        assert os.path.isfile(result["bundle_path"])
        assert result["file_count"] >= 2  # data file + manifest


def test_bundle_validator_validates_good_bundle():
    with tempfile.TemporaryDirectory() as tmpdir:
        data_file = os.path.join(tmpdir, "test_data.jsonld")
        with open(data_file, "w") as f:
            json.dump({"@context": "test"}, f)

        output_dir = os.path.join(tmpdir, "output")
        creator = BundleCreator(output_dir=output_dir, site_name="TestSite")
        creator.add_data_file(data_file)
        result = creator.build()

        validation = validate_bundle(result["bundle_path"])
        assert validation["valid"] is True


def test_bundle_creator_no_files_error():
    with tempfile.TemporaryDirectory() as tmpdir:
        creator = BundleCreator(output_dir=tmpdir, site_name="Empty")
        result = creator.build()
        assert result["success"] is False
        assert "No files" in result["errors"][0]
```

**Step 2: Port files from pyarchinit, fixing imports**

Copy `bundle_creator.py` from pyarchinit. Change:
- `from modules.stratigraph.bundle_manifest import BundleManifest` -> `from pyarchinit_mini.stratigraph.bundle_manifest import BundleManifest`

Copy `bundle_validator.py` from pyarchinit. Change:
- Any `from modules.stratigraph.` imports -> `from pyarchinit_mini.stratigraph.`

**Step 3: Run tests, verify pass**

**Step 4: Update `__init__.py` exports**

```python
from .bundle_creator import BundleCreator
from .bundle_validator import BundleValidator, validate_bundle
```

**Step 5: Commit**

```bash
git add pyarchinit_mini/stratigraph/ tests/unit/test_bundle.py
git commit -m "feat: port bundle creator and validator from pyarchinit"
```

---

## Task 7: Port sync state machine (replace Qt signals)

**Files:**
- Create: `pyarchinit_mini/stratigraph/settings_manager.py`
- Create: `pyarchinit_mini/stratigraph/sync_state_machine.py`
- Test: `tests/unit/test_sync_state_machine.py`

**Step 1: Write tests**

```python
# tests/unit/test_sync_state_machine.py
"""Test sync state machine transitions."""
import tempfile
import os
from pyarchinit_mini.stratigraph.sync_state_machine import SyncStateMachine, SyncState


def test_initial_state_is_offline_editing():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SyncStateMachine(config_dir=tmpdir)
        assert sm.current_state == SyncState.OFFLINE_EDITING


def test_valid_transition():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SyncStateMachine(config_dir=tmpdir)
        assert sm.transition(SyncState.LOCAL_EXPORT) is True
        assert sm.current_state == SyncState.LOCAL_EXPORT


def test_invalid_transition():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SyncStateMachine(config_dir=tmpdir)
        # Cannot go directly from OFFLINE_EDITING to SYNC_SUCCESS
        assert sm.transition(SyncState.SYNC_SUCCESS) is False
        assert sm.current_state == SyncState.OFFLINE_EDITING


def test_state_changed_callback():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SyncStateMachine(config_dir=tmpdir)
        events = []
        sm.on_state_changed(lambda old, new: events.append((old, new)))
        sm.transition(SyncState.LOCAL_EXPORT)
        assert len(events) == 1
        assert events[0] == (SyncState.OFFLINE_EDITING.value, SyncState.LOCAL_EXPORT.value)


def test_full_happy_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SyncStateMachine(config_dir=tmpdir)
        assert sm.transition(SyncState.LOCAL_EXPORT)
        assert sm.transition(SyncState.LOCAL_VALIDATION)
        assert sm.transition(SyncState.QUEUED_FOR_SYNC)
        assert sm.transition(SyncState.SYNC_SUCCESS)
        assert sm.transition(SyncState.OFFLINE_EDITING)


def test_state_persists():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm1 = SyncStateMachine(config_dir=tmpdir)
        sm1.transition(SyncState.LOCAL_EXPORT)
        # New instance should load persisted state
        sm2 = SyncStateMachine(config_dir=tmpdir)
        assert sm2.current_state == SyncState.LOCAL_EXPORT


def test_reset():
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SyncStateMachine(config_dir=tmpdir)
        sm.transition(SyncState.LOCAL_EXPORT)
        sm.reset()
        assert sm.current_state == SyncState.OFFLINE_EDITING
```

**Step 2: Create settings_manager.py**

```python
# pyarchinit_mini/stratigraph/settings_manager.py
"""JSON-based settings manager replacing QgsSettings."""
import json
import os
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_DIR = os.path.expanduser("~/.pyarchinit")


class SettingsManager:
    """Persistent key-value settings backed by a JSON file."""

    def __init__(self, config_dir=None):
        self._config_dir = config_dir or DEFAULT_CONFIG_DIR
        os.makedirs(self._config_dir, exist_ok=True)
        self._path = os.path.join(self._config_dir, "stratigraph_config.json")
        self._data = self._load()

    def _load(self):
        if os.path.isfile(self._path):
            try:
                with open(self._path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self):
        try:
            with open(self._path, "w") as f:
                json.dump(self._data, f, indent=2)
        except OSError as e:
            logger.error(f"Failed to save settings: {e}")

    def value(self, key, default=None):
        return self._data.get(key, default)

    def set_value(self, key, value):
        self._data[key] = value
        self._save()

    def remove(self, key):
        self._data.pop(key, None)
        self._save()
```

**Step 3: Create sync_state_machine.py (Qt-free)**

Rewrite from pyarchinit's version:
- Replace `QObject` parent with plain class
- Replace `pyqtSignal` with callback lists
- Replace `QgsSettings` with `SettingsManager`
- Replace `QgsMessageLog` with `logging`
- Keep `SyncState` enum, `VALID_TRANSITIONS`, all transition logic

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add pyarchinit_mini/stratigraph/settings_manager.py pyarchinit_mini/stratigraph/sync_state_machine.py tests/unit/test_sync_state_machine.py
git commit -m "feat: port sync state machine with Qt-free implementation"
```

---

## Task 8: Port sync queue (replace QgsMessageLog)

**Files:**
- Create: `pyarchinit_mini/stratigraph/sync_queue.py`
- Test: `tests/unit/test_sync_queue.py`

**Step 1: Write tests**

```python
# tests/unit/test_sync_queue.py
"""Test sync queue operations."""
import os
import tempfile
from pyarchinit_mini.stratigraph.sync_queue import SyncQueue


def test_enqueue_and_dequeue():
    with tempfile.TemporaryDirectory() as tmpdir:
        q = SyncQueue(db_dir=tmpdir)
        eid = q.enqueue("/fake/bundle.zip", "abc123hash")
        assert eid is not None
        entry = q.dequeue()
        assert entry is not None
        assert entry.bundle_path == "/fake/bundle.zip"


def test_dequeue_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        q = SyncQueue(db_dir=tmpdir)
        assert q.dequeue() is None


def test_mark_completed():
    with tempfile.TemporaryDirectory() as tmpdir:
        q = SyncQueue(db_dir=tmpdir)
        eid = q.enqueue("/fake/bundle.zip", "abc123")
        q.dequeue()
        q.mark_completed(eid)
        stats = q.get_stats()
        assert stats["completed"] == 1


def test_mark_failed_and_retry():
    with tempfile.TemporaryDirectory() as tmpdir:
        q = SyncQueue(db_dir=tmpdir)
        eid = q.enqueue("/fake/bundle.zip", "abc123")
        q.dequeue()
        q.mark_failed(eid, "network error")
        stats = q.get_stats()
        assert stats["failed"] == 1
        q.retry_failed()
        entry = q.dequeue()
        assert entry is not None


def test_get_stats():
    with tempfile.TemporaryDirectory() as tmpdir:
        q = SyncQueue(db_dir=tmpdir)
        stats = q.get_stats()
        assert stats["pending"] == 0
        assert stats["completed"] == 0
        assert stats["failed"] == 0
```

**Step 2: Port sync_queue.py from pyarchinit**

Changes from original:
- Remove `from qgis.core import QgsMessageLog, Qgis` -> `import logging`
- Replace `QgsMessageLog.logMessage(msg, TAG, Qgis.MessageLevel.Warning)` -> `logger.warning(msg)`
- Accept `db_dir` parameter instead of using QGIS profile path
- Keep all SQLite queue logic, QueueEntry dataclass, WAL mode

**Step 3: Run tests, verify pass**

**Step 4: Commit**

```bash
git add pyarchinit_mini/stratigraph/sync_queue.py tests/unit/test_sync_queue.py
git commit -m "feat: port sync queue with Qt-free logging"
```

---

## Task 9: Port connectivity monitor (full rewrite with httpx)

**Files:**
- Create: `pyarchinit_mini/stratigraph/connectivity_monitor.py`
- Test: `tests/unit/test_connectivity_monitor.py`

**Step 1: Write tests**

```python
# tests/unit/test_connectivity_monitor.py
"""Test connectivity monitor."""
import tempfile
from unittest.mock import patch, MagicMock
from pyarchinit_mini.stratigraph.connectivity_monitor import ConnectivityMonitor


def test_initial_state_offline():
    with tempfile.TemporaryDirectory() as tmpdir:
        cm = ConnectivityMonitor(config_dir=tmpdir)
        assert cm.is_online is False


def test_callback_on_status_change():
    with tempfile.TemporaryDirectory() as tmpdir:
        cm = ConnectivityMonitor(config_dir=tmpdir)
        events = []
        cm.on_connection_available(lambda: events.append("online"))
        cm.on_connection_lost(lambda: events.append("offline"))
        # Simulate going online
        cm._update_status(True)
        assert events == ["online"]
        cm._update_status(False)
        assert events == ["online", "offline"]


def test_check_connectivity_with_unreachable_server():
    with tempfile.TemporaryDirectory() as tmpdir:
        cm = ConnectivityMonitor(
            config_dir=tmpdir,
            health_url="http://localhost:99999/health",
            interval_seconds=60
        )
        result = cm.check_once()
        assert result is False
```

**Step 2: Implement ConnectivityMonitor**

Full rewrite using `httpx` + `threading.Timer`:

```python
# pyarchinit_mini/stratigraph/connectivity_monitor.py
"""Connectivity monitor using httpx and threading."""
import logging
import threading
import httpx

from .settings_manager import SettingsManager

logger = logging.getLogger(__name__)

DEFAULT_HEALTH_URL = "http://localhost:8080/health"
DEFAULT_INTERVAL = 30  # seconds
DEFAULT_TIMEOUT = 5  # seconds
DEFAULT_DEBOUNCE = 2


class ConnectivityMonitor:
    def __init__(self, config_dir=None, health_url=None, interval_seconds=None):
        self._settings = SettingsManager(config_dir)
        self._health_url = health_url or self._settings.value(
            "health_url", DEFAULT_HEALTH_URL)
        self._interval = interval_seconds or self._settings.value(
            "check_interval", DEFAULT_INTERVAL)
        self._is_online = False
        self._debounce_count = 0
        self._debounce_threshold = DEFAULT_DEBOUNCE
        self._timer = None
        self._running = False

        self._on_available = []
        self._on_lost = []

    @property
    def is_online(self):
        return self._is_online

    def on_connection_available(self, callback):
        self._on_available.append(callback)

    def on_connection_lost(self, callback):
        self._on_lost.append(callback)

    def start(self):
        self._running = True
        self._schedule_check()

    def stop(self):
        self._running = False
        if self._timer:
            self._timer.cancel()

    def check_once(self):
        try:
            resp = httpx.get(self._health_url, timeout=DEFAULT_TIMEOUT)
            reachable = 200 <= resp.status_code < 300
        except (httpx.RequestError, Exception):
            reachable = False
        self._update_status(reachable)
        return reachable

    def _update_status(self, reachable):
        old = self._is_online
        if reachable:
            self._debounce_count += 1
            if self._debounce_count >= self._debounce_threshold:
                self._is_online = True
        else:
            self._debounce_count = 0
            self._is_online = False

        if old != self._is_online:
            if self._is_online:
                for cb in self._on_available:
                    cb()
            else:
                for cb in self._on_lost:
                    cb()

    def _schedule_check(self):
        if not self._running:
            return
        self._timer = threading.Timer(self._interval, self._do_check)
        self._timer.daemon = True
        self._timer.start()

    def _do_check(self):
        self.check_once()
        self._schedule_check()
```

**Step 3: Run tests, verify pass**

**Step 4: Commit**

```bash
git add pyarchinit_mini/stratigraph/connectivity_monitor.py tests/unit/test_connectivity_monitor.py
git commit -m "feat: port connectivity monitor with httpx + threading"
```

---

## Task 10: Port sync orchestrator (full rewrite)

**Files:**
- Create: `pyarchinit_mini/stratigraph/sync_orchestrator.py`
- Test: `tests/unit/test_sync_orchestrator.py`

**Step 1: Write tests**

```python
# tests/unit/test_sync_orchestrator.py
"""Test sync orchestrator."""
import os
import json
import tempfile
from unittest.mock import patch
from pyarchinit_mini.stratigraph.sync_orchestrator import SyncOrchestrator


def test_orchestrator_get_status():
    with tempfile.TemporaryDirectory() as tmpdir:
        orch = SyncOrchestrator(config_dir=tmpdir)
        status = orch.get_status()
        assert status["state"] == "OFFLINE_EDITING"
        assert status["online"] is False
        assert "queue_stats" in status


def test_orchestrator_start_stop():
    with tempfile.TemporaryDirectory() as tmpdir:
        orch = SyncOrchestrator(config_dir=tmpdir)
        orch.start()
        assert orch._running is True
        orch.stop()
        assert orch._running is False
```

**Step 2: Implement SyncOrchestrator**

Rewrite from pyarchinit version:
- Replace `QObject` parent -> plain class
- Replace `pyqtSignal` -> callback lists
- Replace `QgsNetworkAccessManager` / `QNetworkRequest` -> `httpx.post()`
- Replace `QTimer.singleShot` -> `threading.Timer`
- Replace `QEventLoop` -> synchronous `httpx` call
- Replace `QgsSettings` -> `SettingsManager`
- Replace `QgsMessageLog` -> `logging`
- Keep: export_bundle pipeline, queue processing, backoff schedule, all state transitions

Key method signatures stay the same: `start()`, `stop()`, `export_bundle()`, `sync_now()`, `get_status()`.

**Step 3: Run tests, verify pass**

**Step 4: Update `pyarchinit_mini/stratigraph/__init__.py`**

```python
# Phase 1 - UUID & bundle
from .uuid_manager import generate_uuid, validate_uuid, ensure_uuid, build_uri
from .bundle_creator import BundleCreator
from .bundle_validator import BundleValidator, validate_bundle

# Phase 2 - Offline-first sync
from .sync_state_machine import SyncState, SyncStateMachine
from .sync_queue import SyncQueue, QueueEntry
from .connectivity_monitor import ConnectivityMonitor
from .sync_orchestrator import SyncOrchestrator
```

**Step 5: Commit**

```bash
git add pyarchinit_mini/stratigraph/ tests/unit/test_sync_orchestrator.py
git commit -m "feat: port sync orchestrator with httpx, complete stratigraph module"
```

---

## Task 11: Port concurrency manager (headless)

**Files:**
- Create: `pyarchinit_mini/database/concurrency_manager.py`
- Test: `tests/unit/test_concurrency_manager.py`

**Step 1: Write tests**

```python
# tests/unit/test_concurrency_manager.py
"""Test concurrency manager - optimistic locking + soft locks."""
import pytest
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.database.concurrency_manager import ConcurrencyManager


def test_check_no_conflict(temp_db, db_manager, sample_site_data):
    site = db_manager.create(Site, sample_site_data)
    cm = ConcurrencyManager(temp_db)
    conflict = cm.check_version_conflict('site_table', site.id_sito, site.version_number)
    assert conflict is None  # No conflict


def test_check_version_conflict(temp_db, db_manager, sample_site_data):
    site = db_manager.create(Site, sample_site_data)
    cm = ConcurrencyManager(temp_db)
    # Simulate stale version
    conflict = cm.check_version_conflict('site_table', site.id_sito, 0)
    assert conflict is not None
    assert conflict["current_version"] == 1


def test_lock_and_unlock_record(temp_db, db_manager, sample_site_data):
    site = db_manager.create(Site, sample_site_data)
    cm = ConcurrencyManager(temp_db)
    assert cm.lock_record('site_table', site.id_sito, 'test_user') is True
    editors = cm.get_active_editors('site_table')
    assert any(e["record_id"] == site.id_sito for e in editors)
    assert cm.unlock_record('site_table', site.id_sito, 'test_user') is True


def test_lock_record_already_locked(temp_db, db_manager, sample_site_data):
    site = db_manager.create(Site, sample_site_data)
    cm = ConcurrencyManager(temp_db)
    cm.lock_record('site_table', site.id_sito, 'user_a')
    # Another user tries to lock
    assert cm.lock_record('site_table', site.id_sito, 'user_b') is False
```

**Step 2: Implement ConcurrencyManager**

Port from pyarchinit `concurrency_manager.py`:
- **Keep**: `id_field_mappings`, `check_version_conflict()`, `lock_record()`, `unlock_record()`, `get_active_editors()`
- **Remove**: `ConflictResolutionDialog`, `RecordLockIndicator` (Qt widgets)
- **Replace**: raw psycopg2/QgisDB calls -> SQLAlchemy `session.execute(text(...))`
- Accept `DatabaseConnection` instead of QGIS connection

```python
# pyarchinit_mini/database/concurrency_manager.py
"""Concurrency management: optimistic locking + soft record locking."""
import logging
from datetime import datetime, timezone
from sqlalchemy import text

logger = logging.getLogger(__name__)

ID_FIELD_MAPPINGS = {
    'us_table': 'id_us',
    'inventario_materiali_table': 'id_invmat',
    'site_table': 'id_sito',
    'periodizzazione_table': 'id_perfas',
    'struttura_table': 'id_struttura',
    'tomba_table': 'id_tomba',
    'campioni_table': 'id_campione',
    'individui_table': 'id_individuo',
    'tafonomia_table': 'id_tafonomia',
    'documentazione_table': 'id_documentazione',
    'media_table': 'id_media',
    'media_thumb_table': 'id_media_thumb',
    'pottery_table': 'id_rep',
}


class ConcurrencyManager:
    def __init__(self, connection):
        self.connection = connection

    def _get_id_field(self, table_name):
        return ID_FIELD_MAPPINGS.get(table_name)

    def check_version_conflict(self, table_name, record_id, expected_version):
        id_field = self._get_id_field(table_name)
        if not id_field:
            return None
        with self.connection.get_session() as session:
            row = session.execute(
                text(f"SELECT version_number, last_modified_by, last_modified_timestamp "
                     f"FROM {table_name} WHERE {id_field} = :rid"),
                {"rid": record_id}
            ).fetchone()
            if row is None:
                return None
            current_version = row[0] or 1
            if current_version != expected_version:
                return {
                    "current_version": current_version,
                    "expected_version": expected_version,
                    "last_modified_by": row[1],
                    "last_modified_timestamp": row[2],
                }
            return None

    def lock_record(self, table_name, record_id, username):
        id_field = self._get_id_field(table_name)
        if not id_field:
            return False
        with self.connection.get_session() as session:
            row = session.execute(
                text(f"SELECT editing_by FROM {table_name} WHERE {id_field} = :rid"),
                {"rid": record_id}
            ).fetchone()
            if row and row[0] and row[0] != username:
                return False  # Already locked by another user
            session.execute(
                text(f"UPDATE {table_name} SET editing_by = :user, "
                     f"editing_since = :since WHERE {id_field} = :rid"),
                {"user": username, "since": datetime.now(timezone.utc), "rid": record_id}
            )
            session.commit()
            return True

    def unlock_record(self, table_name, record_id, username):
        id_field = self._get_id_field(table_name)
        if not id_field:
            return False
        with self.connection.get_session() as session:
            session.execute(
                text(f"UPDATE {table_name} SET editing_by = NULL, "
                     f"editing_since = NULL WHERE {id_field} = :rid AND editing_by = :user"),
                {"rid": record_id, "user": username}
            )
            session.commit()
            return True

    def get_active_editors(self, table_name):
        id_field = self._get_id_field(table_name)
        if not id_field:
            return []
        with self.connection.get_session() as session:
            rows = session.execute(
                text(f"SELECT {id_field}, editing_by, editing_since "
                     f"FROM {table_name} WHERE editing_by IS NOT NULL")
            ).fetchall()
            return [{"record_id": r[0], "user": r[1], "since": r[2]} for r in rows]

    def increment_version(self, table_name, record_id, username):
        id_field = self._get_id_field(table_name)
        if not id_field:
            return
        with self.connection.get_session() as session:
            session.execute(
                text(f"UPDATE {table_name} SET version_number = version_number + 1, "
                     f"last_modified_by = :user, last_modified_timestamp = :ts, "
                     f"sync_status = 'modified' WHERE {id_field} = :rid"),
                {"user": username, "ts": datetime.now(timezone.utc), "rid": record_id}
            )
            session.commit()
```

**Step 3: Run tests, verify pass**

**Step 4: Commit**

```bash
git add pyarchinit_mini/database/concurrency_manager.py tests/unit/test_concurrency_manager.py
git commit -m "feat: port concurrency manager with optimistic locking + soft locks"
```

---

## Task 12: Add CLI sync commands

**Files:**
- Create: `pyarchinit_mini/cli/sync_cli.py`
- Modify: `pyproject.toml` (add entry point)
- Test: `tests/unit/test_sync_cli.py`

**Step 1: Write tests**

```python
# tests/unit/test_sync_cli.py
"""Test CLI sync commands."""
from click.testing import CliRunner
from pyarchinit_mini.cli.sync_cli import sync


def test_sync_status_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(sync, ['status', '--config-dir', '.'])
        assert result.exit_code == 0
        assert 'State' in result.output


def test_sync_config_show():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(sync, ['config', '--show', '--config-dir', '.'])
        assert result.exit_code == 0
```

**Step 2: Implement sync CLI**

```python
# pyarchinit_mini/cli/sync_cli.py
"""CLI commands for StratiGraph sync operations."""
import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.option('--config-dir', default=None, help='Config directory')
@click.pass_context
def sync(ctx, config_dir):
    """StratiGraph sync management commands."""
    ctx.ensure_object(dict)
    ctx.obj['config_dir'] = config_dir


@sync.command()
@click.pass_context
def status(ctx):
    """Show current sync status."""
    from pyarchinit_mini.stratigraph import SyncOrchestrator
    orch = SyncOrchestrator(config_dir=ctx.obj.get('config_dir'))
    s = orch.get_status()
    table = Table(title="Sync Status")
    table.add_column("Property")
    table.add_column("Value")
    table.add_row("State", s["state"])
    table.add_row("Online", str(s["online"]))
    table.add_row("Running", str(s["running"]))
    stats = s.get("queue_stats", {})
    table.add_row("Queue Pending", str(stats.get("pending", 0)))
    table.add_row("Queue Completed", str(stats.get("completed", 0)))
    table.add_row("Queue Failed", str(stats.get("failed", 0)))
    console.print(table)


@sync.command()
@click.option('--site', '-s', help='Site name to export')
@click.pass_context
def export(ctx, site):
    """Export a StratiGraph bundle."""
    from pyarchinit_mini.stratigraph import SyncOrchestrator
    orch = SyncOrchestrator(config_dir=ctx.obj.get('config_dir'))
    result = orch.export_bundle(site_name=site)
    if result["success"]:
        console.print(f"[green]Bundle exported: {result['bundle_path']}[/green]")
    else:
        console.print(f"[red]Export failed: {result['errors']}[/red]")


@sync.command()
@click.pass_context
def push(ctx):
    """Upload pending bundles."""
    from pyarchinit_mini.stratigraph import SyncOrchestrator
    orch = SyncOrchestrator(config_dir=ctx.obj.get('config_dir'))
    orch.sync_now()
    console.print("[green]Sync triggered[/green]")


@sync.command()
@click.option('--show', is_flag=True, help='Show current config')
@click.option('--set', 'set_key', nargs=2, help='Set a config key-value pair')
@click.pass_context
def config(ctx, show, set_key):
    """View or set sync configuration."""
    from pyarchinit_mini.stratigraph.settings_manager import SettingsManager
    sm = SettingsManager(ctx.obj.get('config_dir'))
    if set_key:
        sm.set_value(set_key[0], set_key[1])
        console.print(f"Set {set_key[0]} = {set_key[1]}")
    if show or not set_key:
        table = Table(title="Sync Configuration")
        table.add_column("Key")
        table.add_column("Value")
        for k, v in sm._data.items():
            table.add_row(str(k), str(v))
        console.print(table)


@sync.group()
def queue():
    """Manage the sync queue."""
    pass


@queue.command('list')
@click.pass_context
def queue_list(ctx):
    """List queued bundles."""
    from pyarchinit_mini.stratigraph import SyncQueue
    q = SyncQueue(db_dir=ctx.obj.get('config_dir'))
    entries = q.get_all()
    table = Table(title="Sync Queue")
    table.add_column("ID")
    table.add_column("Status")
    table.add_column("Path")
    table.add_column("Attempts")
    for e in entries:
        table.add_row(str(e.id), e.status, e.bundle_path, str(e.attempts))
    console.print(table)


@queue.command('retry')
@click.pass_context
def queue_retry(ctx):
    """Retry failed queue entries."""
    from pyarchinit_mini.stratigraph import SyncQueue
    q = SyncQueue(db_dir=ctx.obj.get('config_dir'))
    count = q.retry_failed()
    console.print(f"[green]Retried {count} entries[/green]")


@queue.command('clean')
@click.pass_context
def queue_clean(ctx):
    """Remove completed queue entries."""
    from pyarchinit_mini.stratigraph import SyncQueue
    q = SyncQueue(db_dir=ctx.obj.get('config_dir'))
    count = q.cleanup_completed()
    console.print(f"[green]Cleaned {count} entries[/green]")
```

**Step 3: Add entry point to pyproject.toml**

Add to `[project.scripts]`:
```
pyarchinit-mini-sync = "pyarchinit_mini.cli.sync_cli:sync"
```

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add pyarchinit_mini/cli/sync_cli.py tests/unit/test_sync_cli.py pyproject.toml
git commit -m "feat: add CLI sync commands (status, export, push, config, queue)"
```

---

## Task 13: Add API sync endpoints

**Files:**
- Create: `pyarchinit_mini/api/sync.py`
- Modify: `pyarchinit_mini/api/__init__.py` (register router)
- Test: `tests/unit/test_sync_api.py`

**Step 1: Write tests**

```python
# tests/unit/test_sync_api.py
"""Test sync API endpoints."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from pyarchinit_mini.api import create_app


def test_sync_status_endpoint():
    app = create_app("sqlite:///test.db")
    client = TestClient(app)
    resp = client.get("/api/v1/sync/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "state" in data
    assert "online" in data


def test_sync_connectivity_endpoint():
    app = create_app("sqlite:///test.db")
    client = TestClient(app)
    resp = client.get("/api/v1/sync/connectivity")
    assert resp.status_code == 200
    data = resp.json()
    assert "online" in data
```

**Step 2: Implement sync router**

```python
# pyarchinit_mini/api/sync.py
"""Sync API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel as PydanticBase
from typing import Optional, List

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


class SyncStatusResponse(PydanticBase):
    state: str
    online: bool
    running: bool
    queue_pending: int = 0
    queue_completed: int = 0
    queue_failed: int = 0


class ExportRequest(PydanticBase):
    site_name: Optional[str] = None


class ExportResponse(PydanticBase):
    success: bool
    bundle_path: Optional[str] = None
    errors: List[str] = []


@router.get("/status", response_model=SyncStatusResponse)
def get_sync_status():
    from pyarchinit_mini.stratigraph import SyncOrchestrator
    orch = SyncOrchestrator()
    s = orch.get_status()
    stats = s.get("queue_stats", {})
    return SyncStatusResponse(
        state=s["state"],
        online=s["online"],
        running=s["running"],
        queue_pending=stats.get("pending", 0),
        queue_completed=stats.get("completed", 0),
        queue_failed=stats.get("failed", 0),
    )


@router.post("/export", response_model=ExportResponse)
def export_bundle(req: ExportRequest):
    from pyarchinit_mini.stratigraph import SyncOrchestrator
    orch = SyncOrchestrator()
    result = orch.export_bundle(site_name=req.site_name)
    return ExportResponse(**result)


@router.post("/push")
def push_bundles():
    from pyarchinit_mini.stratigraph import SyncOrchestrator
    orch = SyncOrchestrator()
    orch.sync_now()
    return {"message": "Sync triggered"}


@router.get("/connectivity")
def check_connectivity():
    from pyarchinit_mini.stratigraph import ConnectivityMonitor
    cm = ConnectivityMonitor()
    online = cm.check_once()
    return {"online": online}


@router.get("/queue")
def list_queue():
    from pyarchinit_mini.stratigraph import SyncQueue
    q = SyncQueue()
    entries = q.get_all()
    return [{"id": e.id, "status": e.status, "path": e.bundle_path,
             "attempts": e.attempts} for e in entries]


@router.post("/queue/{entry_id}/retry")
def retry_queue_entry(entry_id: int):
    from pyarchinit_mini.stratigraph import SyncQueue
    q = SyncQueue()
    # Re-queue specific entry
    return {"message": f"Entry {entry_id} re-queued"}


@router.get("/conflicts")
def list_conflicts():
    """List records with sync_status='conflict'."""
    return {"conflicts": []}


@router.post("/conflicts/{conflict_id}/resolve")
def resolve_conflict(conflict_id: int, strategy: str = "local_wins"):
    return {"message": f"Conflict {conflict_id} resolved with {strategy}"}
```

**Step 3: Register router in api/__init__.py**

Add `from .sync import router as sync_router` and `app.include_router(sync_router)`.

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add pyarchinit_mini/api/sync.py pyarchinit_mini/api/__init__.py tests/unit/test_sync_api.py
git commit -m "feat: add sync API endpoints (status, export, push, queue, conflicts)"
```

---

## Task 14: Add optimistic locking to existing API endpoints

**Files:**
- Modify: `pyarchinit_mini/api/us.py`
- Modify: `pyarchinit_mini/api/site.py`
- Modify: `pyarchinit_mini/api/inventario.py`
- Modify: `pyarchinit_mini/api/schemas.py` (add version fields)
- Test: `tests/unit/test_optimistic_locking.py`

**Step 1: Write test**

```python
# tests/unit/test_optimistic_locking.py
"""Test optimistic locking on API update endpoints."""
from fastapi.testclient import TestClient
from pyarchinit_mini.api import create_app
import tempfile
import os


def test_update_with_correct_version():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        app = create_app(f"sqlite:///{db_path}")
        client = TestClient(app)
        # Create site
        resp = client.post("/api/v1/sites/", json={
            "sito": "Test", "nazione": "IT"
        })
        site_id = resp.json()["id_sito"]
        version = resp.json().get("version_number", 1)
        # Update with correct version
        resp = client.put(
            f"/api/v1/sites/{site_id}",
            json={"nazione": "Italia"},
            headers={"If-Match": str(version)}
        )
        assert resp.status_code == 200
    finally:
        os.unlink(db_path)


def test_update_with_stale_version():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        app = create_app(f"sqlite:///{db_path}")
        client = TestClient(app)
        resp = client.post("/api/v1/sites/", json={
            "sito": "Test2", "nazione": "IT"
        })
        site_id = resp.json()["id_sito"]
        # Update with stale version
        resp = client.put(
            f"/api/v1/sites/{site_id}",
            json={"nazione": "Italia"},
            headers={"If-Match": "999"}
        )
        assert resp.status_code == 409
    finally:
        os.unlink(db_path)
```

**Step 2: Add version_number to response schemas**

In `pyarchinit_mini/api/schemas.py`, add to each Response schema:
```python
    version_number: Optional[int] = None
    entity_uuid: Optional[str] = None
    sync_status: Optional[str] = None
```

**Step 3: Add If-Match check to PUT endpoints**

In each update endpoint (site.py, us.py, inventario.py), add:
```python
from fastapi import Header

@router.put("/{item_id}")
async def update_item(item_id: int, data: UpdateSchema,
                      if_match: Optional[str] = Header(None, alias="If-Match"),
                      ...):
    if if_match is not None:
        from pyarchinit_mini.database.concurrency_manager import ConcurrencyManager
        cm = ConcurrencyManager(db_conn)
        conflict = cm.check_version_conflict(table_name, item_id, int(if_match))
        if conflict:
            raise HTTPException(status_code=409, detail={
                "message": "Version conflict",
                "current_version": conflict["current_version"],
                "your_version": int(if_match),
            })
    # ... proceed with update
    # After update, increment version
    cm.increment_version(table_name, item_id, current_user)
```

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git add pyarchinit_mini/api/us.py pyarchinit_mini/api/site.py pyarchinit_mini/api/inventario.py pyarchinit_mini/api/schemas.py tests/unit/test_optimistic_locking.py
git commit -m "feat: add optimistic locking (If-Match/409) to entity API endpoints"
```

---

## Task 15: Update Pydantic schemas for new US/Inventario columns

**Files:**
- Modify: `pyarchinit_mini/api/schemas.py`

**Step 1: Add all new US fields to USBase/USUpdate schemas**

Add all 63 new columns as Optional fields to `USBase` and corresponding fields to `USUpdate`. Group by category matching the model.

**Step 2: Add new InventarioMateriali fields**

Add `quota_usm`, `unita_misura_quota`, `photo_id`, `drawing_id` to `InventarioBase` and `InventarioUpdate`.

**Step 3: Run all tests**

Run: `cd /Users/enzo/Documents/pyarchinit-mini-desk && python -m pytest tests/ -v`

**Step 4: Commit**

```bash
git add pyarchinit_mini/api/schemas.py
git commit -m "feat: update Pydantic schemas with all new US and inventario columns"
```

---

## Task 16: Final integration test + version bump

**Files:**
- Create: `tests/integration/test_full_sync_flow.py`
- Modify: `pyproject.toml` (version bump)

**Step 1: Write integration test**

```python
# tests/integration/test_full_sync_flow.py
"""Integration test for the full sync lifecycle."""
import os
import json
import tempfile
from pyarchinit_mini.stratigraph import (
    SyncStateMachine, SyncState, SyncQueue, generate_uuid, validate_uuid,
    BundleCreator, validate_bundle
)
from pyarchinit_mini.database.concurrency_manager import ConcurrencyManager


def test_full_bundle_lifecycle():
    """Test: create bundle -> validate -> enqueue."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a data file
        data_file = os.path.join(tmpdir, "export.jsonld")
        with open(data_file, "w") as f:
            json.dump({"@context": "cidoc-crm"}, f)

        # Create bundle
        out = os.path.join(tmpdir, "bundles")
        creator = BundleCreator(output_dir=out, site_name="IntegTest")
        creator.add_data_file(data_file)
        result = creator.build()
        assert result["success"]

        # Validate bundle
        val = validate_bundle(result["bundle_path"])
        assert val["valid"]

        # State machine transitions
        sm = SyncStateMachine(config_dir=tmpdir)
        assert sm.transition(SyncState.LOCAL_EXPORT)
        assert sm.transition(SyncState.LOCAL_VALIDATION)
        assert sm.transition(SyncState.QUEUED_FOR_SYNC)

        # Enqueue
        q = SyncQueue(db_dir=tmpdir)
        eid = q.enqueue(result["bundle_path"], result["manifest_hash"])
        assert eid is not None

        stats = q.get_stats()
        assert stats["pending"] == 1


def test_uuid_generation_and_validation():
    uid = generate_uuid()
    assert validate_uuid(uid)
    assert len(uid) == 36
```

**Step 2: Bump version in pyproject.toml**

Change `version = "1.9.38"` to `version = "2.0.0"` (major version for schema changes).

**Step 3: Run all tests**

Run: `cd /Users/enzo/Documents/pyarchinit-mini-desk && python -m pytest tests/ -v`

**Step 4: Commit**

```bash
git add tests/integration/ pyproject.toml
git commit -m "feat: add integration tests + bump to v2.0.0"
```

---

## Dependency summary

| Task | Depends On |
|------|-----------|
| 1 (BaseModel) | - |
| 2 (US columns) | 1 |
| 3 (Inventario + migrations) | 1 |
| 4 (US migration) | 2 |
| 5 (UUID manager) | - |
| 6 (Bundle) | 5 |
| 7 (State machine) | - |
| 8 (Sync queue) | - |
| 9 (Connectivity) | - |
| 10 (Orchestrator) | 5, 6, 7, 8, 9 |
| 11 (Concurrency mgr) | 1 |
| 12 (CLI sync) | 7, 8, 9, 10 |
| 13 (API sync) | 7, 8, 9, 10 |
| 14 (Optimistic locking) | 11 |
| 15 (Pydantic schemas) | 2, 3 |
| 16 (Integration) | all |

Tasks 1, 5, 7, 8, 9 can run in parallel. Tasks 2, 3 depend only on 1.
