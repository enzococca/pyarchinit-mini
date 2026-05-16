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
