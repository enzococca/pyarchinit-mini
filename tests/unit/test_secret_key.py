"""Flask session secret-key resolution (no hardcoded key).

Order: environment variable (FLASK_SECRET_KEY, then SECRET_KEY) -> per-install
key file under the data folder (generated once, mode 0600) -> hard failure
naming the path. There is deliberately no third fallback.
"""
import os
import stat
import sys

import pytest

from pyarchinit_mini.utils.secret_key import (
    KEY_FILENAME,
    resolve_secret_key,
    secret_key_path,
)


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    for var in ("FLASK_SECRET_KEY", "SECRET_KEY"):
        monkeypatch.delenv(var, raising=False)
    return tmp_path


def test_env_flask_secret_key_wins_and_no_file_is_written(home, monkeypatch):
    monkeypatch.setenv("FLASK_SECRET_KEY", "from-env-0123456789")
    assert resolve_secret_key() == "from-env-0123456789"
    assert not (home / KEY_FILENAME).exists()


def test_env_plain_secret_key_is_accepted_too(home, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "railway-style-value")
    assert resolve_secret_key() == "railway-style-value"


def test_flask_secret_key_takes_precedence_over_secret_key(home, monkeypatch):
    monkeypatch.setenv("FLASK_SECRET_KEY", "flask-one")
    monkeypatch.setenv("SECRET_KEY", "plain-one")
    assert resolve_secret_key() == "flask-one"


@pytest.mark.parametrize("bad", ["", "   ", "your-secret-key-here", "change-this-in-production"])
def test_blank_or_placeholder_env_is_ignored(home, monkeypatch, bad):
    monkeypatch.setenv("FLASK_SECRET_KEY", bad)
    key = resolve_secret_key()
    assert key != bad.strip()
    assert (home / KEY_FILENAME).exists()


def test_key_file_is_generated_once_and_stable_across_calls(home):
    first = resolve_secret_key()
    second = resolve_secret_key()
    assert first == second
    assert (home / KEY_FILENAME).read_text().strip() == first


def test_generated_key_is_long_and_unique_per_install(home, tmp_path_factory, monkeypatch):
    one = resolve_secret_key()
    other_home = tmp_path_factory.mktemp("other")
    monkeypatch.setenv("PYARCHINIT_HOME", str(other_home))
    two = resolve_secret_key()
    assert len(one) >= 32 and len(two) >= 32
    assert one != two


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX file modes")
def test_key_file_is_private_to_the_user(home):
    resolve_secret_key()
    mode = stat.S_IMODE(os.stat(home / KEY_FILENAME).st_mode)
    assert mode == 0o600


def test_existing_key_file_is_reused_even_with_trailing_newline(home):
    (home / KEY_FILENAME).write_text("pre-existing-key-value\n")
    assert resolve_secret_key() == "pre-existing-key-value"


def test_secret_key_path_honours_pyarchinit_home(home):
    assert secret_key_path() == home / KEY_FILENAME


@pytest.mark.skipif(sys.platform == "win32" or os.geteuid() == 0, reason="needs non-root POSIX")
def test_unwritable_data_folder_fails_loudly_with_the_path(home):
    os.chmod(home, 0o500)
    try:
        with pytest.raises(RuntimeError) as exc:
            resolve_secret_key()
        assert str(home / KEY_FILENAME) in str(exc.value)
        assert "FLASK_SECRET_KEY" in str(exc.value)
    finally:
        os.chmod(home, 0o700)


def test_create_app_no_longer_embeds_a_hardcoded_secret():
    import inspect
    from pyarchinit_mini.web_interface import app as web_app
    src = inspect.getsource(web_app.create_app)
    assert "your-secret-key-here" not in src
    assert "resolve_secret_key()" in src
