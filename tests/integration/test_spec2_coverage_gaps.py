"""TODO(Spec-3) coverage gap stubs — see Spec 2 review.

Each test below is xfail-marked because the underlying implementation
either doesn't exist yet (banner) or hasn't been hardened (concurrent
regen) — but the test names + docstrings serve as a tracked checklist.
"""
import pytest


@pytest.mark.xfail(reason="TODO(Spec-3): concurrent regen on same site")
def test_concurrent_regen_same_site_does_not_corrupt_output():
    """Two threads invoke _trigger_graph_regen for the same site;
    neither leaves a .tmp file behind; final stratigraphy.graphml
    is valid XML."""
    assert False, "test not yet implemented"


@pytest.mark.xfail(reason="TODO(Spec-3): cross-site paradata isolation")
def test_paradata_for_one_site_does_not_leak_to_another():
    """ParadataStore('A').add_author(name='X') → ParadataStore('B').list_authors() == []"""
    assert False, "test not yet implemented"


@pytest.mark.xfail(reason="TODO(Spec-3): snapshot_revision determinism")
def test_snapshot_revision_is_deterministic_across_calls():
    """Two calls to GraphIngestor._current_snapshot_revision() with
    identical DB state produce the same hash."""
    assert False, "test not yet implemented"
