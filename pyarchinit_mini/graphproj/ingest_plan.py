"""IngestPlan / IngestResult / NodePlanEntry — frozen dataclasses for GraphIngestor."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NodePlanEntry:
    node_uuid: str
    unit_type: str
    semantic_id: str
    before: Optional[dict]
    after: dict
    reason: str


@dataclass(frozen=True)
class IngestPlan:
    site: str
    snapshot_revision: str
    inserts: tuple[NodePlanEntry, ...]
    updates: tuple[NodePlanEntry, ...]
    skips_local_newer: tuple[NodePlanEntry, ...]
    skips_locked: tuple[NodePlanEntry, ...]


@dataclass(frozen=True)
class IngestResult:
    plan: IngestPlan
    inserted: int
    updated: int
    skipped: int
    errors: tuple[str, ...]
