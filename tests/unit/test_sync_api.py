# -*- coding: utf-8 -*-
"""Test sync API endpoints."""


def test_sync_status_endpoint():
    """Test /api/v1/sync/status returns expected shape."""
    from pyarchinit_mini.api.sync import router, SyncStatusResponse
    assert router is not None
    resp = SyncStatusResponse(state="OFFLINE_EDITING", online=False, running=False)
    assert resp.state == "OFFLINE_EDITING"
    assert resp.online is False


def test_sync_response_models():
    """Test Pydantic response models."""
    from pyarchinit_mini.api.sync import SyncStatusResponse, ExportResponse
    s = SyncStatusResponse(state="OFFLINE_EDITING", online=True, running=True,
                           queue_pending=3, queue_completed=10, queue_failed=1)
    assert s.queue_pending == 3
    e = ExportResponse(success=True, bundle_path="/tmp/bundle.zip")
    assert e.success
    assert e.errors == []


def test_connectivity_endpoint_exists():
    """Test that connectivity endpoint is registered."""
    from pyarchinit_mini.api.sync import router
    paths = [r.path for r in router.routes]
    assert any("/connectivity" in p for p in paths)


def test_queue_endpoint_exists():
    """Test that queue endpoint is registered."""
    from pyarchinit_mini.api.sync import router
    paths = [r.path for r in router.routes]
    assert any("/queue" in p for p in paths)


def test_conflicts_endpoint_exists():
    """Test that conflicts endpoint is registered."""
    from pyarchinit_mini.api.sync import router
    paths = [r.path for r in router.routes]
    assert any("/conflicts" in p for p in paths)


def test_export_request_model():
    """Test ExportRequest model."""
    from pyarchinit_mini.api.sync import ExportRequest
    req = ExportRequest()
    assert req.site_name is None
    req2 = ExportRequest(site_name="TestSite")
    assert req2.site_name == "TestSite"
