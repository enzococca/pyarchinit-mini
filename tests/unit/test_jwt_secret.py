"""API JWT tokens must not be signed with a hardcoded default secret."""
import pytest

jose = pytest.importorskip("jose")
from jose import jwt  # noqa: E402

from pyarchinit_mini.utils import auth as auth_utils  # noqa: E402


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    for var in ("JWT_SECRET_KEY", "FLASK_SECRET_KEY", "SECRET_KEY"):
        monkeypatch.delenv(var, raising=False)
    return tmp_path


def test_token_forged_with_old_default_secret_is_rejected(isolated):
    forged = jwt.encode({"sub": "admin"}, "your-secret-key-change-in-production", algorithm="HS256")
    assert auth_utils.decode_access_token(forged) is None


def test_round_trip_uses_per_install_secret(isolated):
    token = auth_utils.create_access_token({"sub": "alice"})
    assert auth_utils.decode_access_token(token)["sub"] == "alice"


def test_jwt_secret_key_env_still_wins(isolated, monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "explicit-jwt-secret")
    token = auth_utils.create_access_token({"sub": "bob"})
    assert jwt.decode(token, "explicit-jwt-secret", algorithms=["HS256"])["sub"] == "bob"
