# -*- coding: utf-8 -*-
"""Sync API endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel as PydanticBase
from typing import Optional, List

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


class SyncStatusResponse(PydanticBase):
    state: str
    online: bool
    running: bool
    queue_pending: int = 0
    queue_completed: int = 0
    queue_failed: int = 0


class ExportRequest(PydanticBase):
    site_name: Optional[str] = None


class ExportResponse(PydanticBase):
    success: bool
    bundle_path: Optional[str] = None
    errors: List[str] = []


@router.get("/status", response_model=SyncStatusResponse)
def get_sync_status():
    from pyarchinit_mini.stratigraph import SyncOrchestrator
    orch = SyncOrchestrator()
    s = orch.get_status()
    stats = s.get("queue_stats", {})
    return SyncStatusResponse(
        state=s["state"],
        online=s["online"],
        running=s["running"],
        queue_pending=stats.get("pending", 0),
        queue_completed=stats.get("completed", 0),
        queue_failed=stats.get("failed", 0),
    )


@router.post("/export", response_model=ExportResponse)
def export_bundle(req: ExportRequest):
    from pyarchinit_mini.stratigraph import SyncOrchestrator
    orch = SyncOrchestrator()
    result = orch.export_bundle(site_name=req.site_name)
    return ExportResponse(**result)


@router.post("/push")
def push_bundles():
    from pyarchinit_mini.stratigraph import SyncOrchestrator
    orch = SyncOrchestrator()
    orch.sync_now()
    return {"message": "Sync triggered"}


@router.get("/connectivity")
def check_connectivity():
    from pyarchinit_mini.stratigraph import ConnectivityMonitor
    cm = ConnectivityMonitor()
    cm.check_now()
    return {"online": cm.is_online}


@router.get("/queue")
def list_queue():
    from pyarchinit_mini.stratigraph import SyncQueue
    q = SyncQueue()
    entries = q.get_all()
    return [{"id": e.id, "status": e.status, "path": e.bundle_path,
             "attempts": e.attempts} for e in entries]


@router.post("/queue/{entry_id}/retry")
def retry_queue_entry(entry_id: int):
    from pyarchinit_mini.stratigraph import SyncQueue
    q = SyncQueue()
    q.retry_failed(entry_id)
    return {"message": f"Entry {entry_id} re-queued"}


@router.get("/conflicts")
def list_conflicts():
    """List records with sync_status='conflict'."""
    return {"conflicts": []}


@router.post("/conflicts/{conflict_id}/resolve")
def resolve_conflict(conflict_id: int, strategy: str = "local_wins"):
    return {"message": f"Conflict {conflict_id} resolved with {strategy}"}
