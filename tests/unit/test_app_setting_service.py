import pytest
from pyarchinit_mini.services.app_setting_service import AppSettingService


@pytest.fixture
def svc(db_manager, tmp_path, monkeypatch):
    # Redirect secret key location to a temp dir
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    return AppSettingService(db_manager)


def test_set_and_get_plain_value(svc):
    svc.set("ai_provider", "openai", is_secret=False, description="LLM backend")
    assert svc.get("ai_provider") == "openai"


def test_set_and_get_secret_value(svc):
    svc.set("openai_api_key", "sk-test-xyz", is_secret=True)
    # Round-trip returns the plain value
    assert svc.get("openai_api_key") == "sk-test-xyz"


def test_secret_is_stored_encrypted(svc):
    svc.set("openai_api_key", "sk-test-xyz", is_secret=True)
    # Read the raw DB value — must NOT contain the plain key
    from pyarchinit_mini.models.app_setting import AppSetting
    with svc.db_manager.connection.get_session() as session:
        row = session.query(AppSetting).filter_by(key="openai_api_key").first()
        assert "sk-test-xyz" not in (row.value or ""), "Plain secret leaked into DB"


def test_get_missing_returns_none(svc):
    assert svc.get("nonexistent") is None


def test_list_settings(svc):
    svc.set("a", "1")
    svc.set("b", "2", is_secret=True)
    rows = svc.list_settings()
    keys = {r.key for r in rows}
    assert {"a", "b"}.issubset(keys)


def test_delete_setting(svc):
    svc.set("temp", "val")
    assert svc.delete("temp") is True
    assert svc.get("temp") is None
    assert svc.delete("temp") is False  # second delete returns False


def test_update_existing_key(svc):
    svc.set("ai_model", "gpt-5.4")
    svc.set("ai_model", "gpt-5.5")
    assert svc.get("ai_model") == "gpt-5.5"
