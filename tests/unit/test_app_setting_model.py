import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.models.base import Base
from pyarchinit_mini.models.app_setting import AppSetting


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    s = SessionLocal()
    yield s
    s.close()


def test_app_setting_has_columns():
    cols = {c.name for c in AppSetting.__table__.columns}
    expected = {"id_setting", "key", "value", "is_secret", "description",
                "created_at", "updated_at", "entity_uuid"}
    assert expected.issubset(cols), f"Missing columns: {expected - cols}"


def test_app_setting_key_is_unique(session):
    a = AppSetting(key="openai_api_key", value="sk-1", is_secret=True)
    b = AppSetting(key="openai_api_key", value="sk-2", is_secret=True)
    session.add(a); session.commit()
    session.add(b)
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        session.commit()


def test_app_setting_roundtrip(session):
    s = AppSetting(key="ai_provider", value="openai", is_secret=False,
                   description="LLM backend")
    session.add(s); session.commit()
    loaded = session.query(AppSetting).filter_by(key="ai_provider").first()
    assert loaded.value == "openai"
    assert loaded.is_secret is False
    assert loaded.description == "LLM backend"
