"""Dropbox must be configurable with a refresh token from /settings/storage.

Dropbox has issued only short-lived access tokens (4 h) since 2021; a
long-running deployment (Railway, a server) needs the refresh-token flow
(refresh_token + app_key + app_secret), which DropboxBackend already
implements. Until now the settings page exposed no refresh_token field, and
the backend used a (possibly expired) access_token in preference to the
refresh flow whenever both were saved.
"""
import sys
import types

import pytest

from pyarchinit_mini.web_interface.app import STORAGE_BACKEND_DEFS
from pyarchinit_mini.storage.backends.dropbox_backend import DropboxBackend


def test_dropbox_fieldset_exposes_refresh_token_as_secret():
    defn = STORAGE_BACKEND_DEFS["dropbox"]
    assert "refresh_token" in defn["fields"]
    assert "refresh_token" in defn["secret_fields"]


class _FakeDropbox:
    """Records how the SDK client was constructed; answers the probe call."""
    instances = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        _FakeDropbox.instances.append(self)

    def users_get_current_account(self):
        return {"ok": True}


@pytest.fixture
def fake_dropbox_sdk(monkeypatch):
    _FakeDropbox.instances = []
    mod = types.ModuleType("dropbox")
    mod.Dropbox = _FakeDropbox
    exc = types.ModuleType("dropbox.exceptions")
    exc.AuthError = type("AuthError", (Exception,), {})
    mod.exceptions = exc
    monkeypatch.setitem(sys.modules, "dropbox", mod)
    monkeypatch.setitem(sys.modules, "dropbox.exceptions", exc)
    return _FakeDropbox


def test_backend_prefers_refresh_flow_when_refresh_token_is_saved(fake_dropbox_sdk):
    backend = DropboxBackend("/", {
        "access_token": "short-lived-and-expired",
        "refresh_token": "rt", "app_key": "ak", "app_secret": "as",
    })

    assert backend.connect() is True
    client = fake_dropbox_sdk.instances[-1]
    assert client.kwargs.get("oauth2_refresh_token") == "rt"
    assert client.kwargs.get("app_key") == "ak"
    assert client.kwargs.get("app_secret") == "as"
    assert "short-lived-and-expired" not in client.args


def test_backend_still_accepts_plain_access_token(fake_dropbox_sdk):
    backend = DropboxBackend("/", {"access_token": "tok"})

    assert backend.connect() is True
    client = fake_dropbox_sdk.instances[-1]
    assert client.args == ("tok",)
