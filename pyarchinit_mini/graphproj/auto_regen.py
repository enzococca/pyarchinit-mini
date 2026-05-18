"""Post-commit auto-regen hook for stratigraphy.graphml.

Fires after US/USM save commits. Best-effort, error-isolated: regen
failures do NOT propagate — they're logged + cached for banner display
in the UI (cache wiring happens in Flask layer).

Disable globally with env PYARCHINIT_DISABLE_AUTO_REGEN=1.
Disable temporarily (bulk import) with `with disable_regen():` context.

Spec 2 simplification (per Task 8 finding): paradata is stored in a JSON
sidecar (paradata.json), not in the Graph. Therefore the output
stratigraphy.graphml is just the projector's stratigraphic graph —
no merge step. Paradata remains visible via the REST API / UI but is
NOT embedded in stratigraphy.graphml.
"""
from __future__ import annotations

import logging
import os
import threading
from contextlib import contextmanager
from typing import Any, Iterator

from .filesystem import paradata_dir, paradata_flock
from .projector import GraphProjector
from pyarchinit_mini.graphml_io.writer import write_graphml

logger = logging.getLogger(__name__)

_local = threading.local()
STRATIGRAPHY_FILENAME = "stratigraphy.graphml"


def _is_regen_disabled() -> bool:
    return getattr(_local, "disabled", False)


def _record_touched_site(site: str) -> None:
    if not hasattr(_local, "touched"):
        _local.touched = []
    if site not in _local.touched:
        _local.touched.append(site)


def _drain_touched_sites() -> list[str]:
    touched = getattr(_local, "touched", [])
    _local.touched = []
    return touched


@contextmanager
def disable_regen() -> Iterator[None]:
    """Disable per-row auto-regen for the duration of the block.

    Use with bulk imports to avoid N regens; call
    force_regen_all_touched_sites() at end to regen once per touched site.
    """
    prev = getattr(_local, "disabled", False)
    _local.disabled = True
    try:
        yield
    finally:
        _local.disabled = prev


def _trigger_graph_regen(site: str, *, session: Any) -> None:
    """Best-effort post-commit regen of stratigraphy.graphml. Never raises.

    No merge step (Spec 2 sidecar pattern): output is the pure GraphProjector
    result. Paradata remains in paradata.json, not embedded.
    """
    if os.environ.get("PYARCHINIT_DISABLE_AUTO_REGEN") == "1":
        return
    if _is_regen_disabled():
        _record_touched_site(site)
        return
    try:
        graph = GraphProjector.populate_graph(session, site)
        out_path = paradata_dir(site) / STRATIGRAPHY_FILENAME
        # Serialize under per-site flock so concurrent regens don't interleave.
        # Atomic: write to .tmp then replace(), so readers never see partial file.
        with paradata_flock(site):
            tmp = out_path.with_suffix(out_path.suffix + ".tmp")
            write_graphml(graph, tmp)
            tmp.replace(out_path)
        logger.info(
            "regen ok site=%s nodes=%d edges=%d",
            site, len(list(graph.nodes)), len(list(graph.edges)),
        )
    except Exception:
        logger.exception("regen failed for site=%s", site)
        # Cache update (regen_status:<site>) happens in the Flask layer
        # (see graph_routes); auto_regen is decoupled from Flask cache.


def force_regen_all_touched_sites() -> None:
    """Drain the touched-site list (one-shot).

    Caller (typically the bulk-import route) must call _trigger_graph_regen
    explicitly for each returned site, providing its session, because
    auto_regen has no way to obtain a Session from thread-local storage.
    """
    sites = _drain_touched_sites()
    if not sites:
        return
    logger.warning(
        "force_regen_all_touched_sites called for sites=%s — caller must "
        "now invoke _trigger_graph_regen(site, session=...) for each, "
        "providing the active SQLAlchemy session.",
        sites,
    )
