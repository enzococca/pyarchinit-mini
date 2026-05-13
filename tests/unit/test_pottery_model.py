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
