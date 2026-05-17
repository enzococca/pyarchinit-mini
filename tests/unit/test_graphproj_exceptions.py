import pytest
from pyarchinit_mini.graphproj.exceptions import (
    ProjectionError,
    IngestError,
    IngestStaleError,
    ParadataConflict,
    ParadataNotFound,
    ParadataStorageError,
    GraphMLReadError,
    GraphMLWriteError,
)


def test_projection_error_carries_site():
    err = ProjectionError("missing site", site="X")
    assert err.site == "X"
    assert "missing site" in str(err)


def test_ingest_stale_error_carries_expected_revision():
    err = IngestStaleError(expected="abc123", actual="def456")
    assert err.expected == "abc123"
    assert err.actual == "def456"
    assert "abc123" in str(err) and "def456" in str(err)


def test_paradata_conflict_carries_existing():
    existing = {"node_id": "n1", "name": "M. Rossi"}
    err = ParadataConflict(node_id="n1", existing=existing)
    assert err.existing == existing


def test_paradata_not_found_carries_node_id():
    err = ParadataNotFound(node_id="n1")
    assert err.node_id == "n1"


def test_graphml_read_error_carries_path():
    err = GraphMLReadError(path="/tmp/x.graphml", msg="malformed XML")
    assert err.path == "/tmp/x.graphml"
