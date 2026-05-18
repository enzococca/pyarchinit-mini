"""GraphIngestor — 2-phase populate_list (preview + apply).

Phase 1 (preview): compute IngestPlan classifying each input node as
  - INSERT (no DB row with matching node_uuid)
  - UPDATE (DB row exists; graph node represents an edit)
  - SKIP_LOCAL_NEWER (DB row's updated_at > graph node — future Spec 3)
  - SKIP_LOCKED (row protected by another user — future Spec 3)
Plus a snapshot_revision (SHA-256 hash of relevant DB state) for staleness
detection between preview and apply.

Phase 2 (apply): execute the plan in a single transaction. Refuses to
proceed if current snapshot_revision != plan.snapshot_revision (DB
changed between preview and apply).

Identity key: node.attributes['EMid'] ↔ us_table.node_uuid (per Spec 1 §4.3).
"""
import hashlib
from typing import Any

import s3dgraphy
from sqlalchemy import text
from sqlalchemy.orm import Session

from .ingest_plan import IngestPlan, IngestResult, NodePlanEntry
from .exceptions import IngestError, IngestStaleError


class GraphIngestor:
    def __init__(self, session: Session, site: str) -> None:
        self.session = session
        self.site = site

    def _current_snapshot_revision(self) -> str:
        """Hash relevant DB state for staleness detection."""
        rows = self.session.execute(text(
            "SELECT node_uuid, us, unita_tipo FROM us_table "
            "WHERE sito = :sito ORDER BY COALESCE(node_uuid, ''), us"
        ), {"sito": self.site}).fetchall()
        canonical = "|".join(
            f"{r[0] or ''}:{r[1]}:{r[2] or ''}" for r in rows
        )
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    def _existing_rows_by_uuid(self) -> dict[str, dict]:
        rows = self.session.execute(text(
            "SELECT node_uuid, us, unita_tipo FROM us_table WHERE sito = :sito"
        ), {"sito": self.site}).fetchall()
        result = {}
        for r in rows:
            uuid = r[0] or ""
            if uuid:
                result[uuid] = {"us": r[1], "unita_tipo": r[2]}
        return result

    def _classify_node(self, node: "s3dgraphy.Node", existing: dict[str, dict]) -> tuple[str, NodePlanEntry] | None:
        """Classify one graph node. Returns (bucket_name, entry) or None to skip."""
        attrs = getattr(node, "attributes", {}) or {}
        emid = attrs.get("EMid", "")
        unita_tipo = attrs.get("unit_type", "US")
        # Derive us number from node.name (format "<TYPE><NUM>"). Some nodes
        # (e.g. GeoPositionNode) won't have a numeric tail — skip silently.
        us_str = "".join(c for c in (node.name or "") if c.isdigit())
        if not us_str:
            return None
        us_num = int(us_str)
        semantic_id = f"pyarchinit:site={self.site}/us={us_num}"

        after_row = {
            "us": us_num,
            "unita_tipo": unita_tipo,
            "node_uuid": emid,
        }

        if emid and emid in existing:
            return "updates", NodePlanEntry(
                node_uuid=emid,
                unit_type=unita_tipo,
                semantic_id=semantic_id,
                before=existing[emid],
                after=after_row,
                reason="graph_newer",
            )
        return "inserts", NodePlanEntry(
            node_uuid=emid or "",
            unit_type=unita_tipo,
            semantic_id=semantic_id,
            before=None,
            after=after_row,
            reason="new",
        )

    def preview(self, graph: "s3dgraphy.Graph", *, dry_run: bool = True) -> IngestPlan:
        """Compute IngestPlan. No DB writes."""
        inserts: list[NodePlanEntry] = []
        updates: list[NodePlanEntry] = []
        skips_local_newer: list[NodePlanEntry] = []
        skips_locked: list[NodePlanEntry] = []

        snapshot = self._current_snapshot_revision()
        existing = self._existing_rows_by_uuid()

        buckets = {
            "inserts": inserts,
            "updates": updates,
            "skips_local_newer": skips_local_newer,
            "skips_locked": skips_locked,
        }

        for node in graph.nodes:
            result = self._classify_node(node, existing)
            if result is None:
                continue
            bucket_name, entry = result
            buckets[bucket_name].append(entry)

        return IngestPlan(
            site=self.site,
            snapshot_revision=snapshot,
            inserts=tuple(inserts),
            updates=tuple(updates),
            skips_local_newer=tuple(skips_local_newer),
            skips_locked=tuple(skips_locked),
        )

    def apply(self, plan: IngestPlan) -> IngestResult:
        """Stub for Task 15."""
        raise NotImplementedError("apply() implemented in Task 15")
