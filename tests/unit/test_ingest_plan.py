import pytest
from pyarchinit_mini.graphproj.ingest_plan import (
    NodePlanEntry,
    IngestPlan,
    IngestResult,
)


def test_node_plan_entry_frozen():
    e = NodePlanEntry(
        node_uuid="u1", unit_type="US",
        semantic_id="pyarchinit:site=X/us=1",
        before=None, after={"us": 1}, reason="new",
    )
    with pytest.raises(Exception):
        e.reason = "different"


def test_ingest_plan_frozen():
    p = IngestPlan(
        site="X", snapshot_revision="abc",
        inserts=(), updates=(), skips_local_newer=(), skips_locked=(),
    )
    with pytest.raises(Exception):
        p.snapshot_revision = "def"


def test_ingest_result_carries_counts():
    p = IngestPlan(
        site="X", snapshot_revision="abc",
        inserts=(), updates=(), skips_local_newer=(), skips_locked=(),
    )
    r = IngestResult(plan=p, inserted=5, updated=3, skipped=2, errors=())
    assert r.inserted == 5
    assert r.updated == 3
    assert r.skipped == 2
    assert r.errors == ()
