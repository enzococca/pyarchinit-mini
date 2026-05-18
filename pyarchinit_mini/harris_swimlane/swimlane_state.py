"""SwimlaneState — Cytoscape JSON <-> DB (full impl in Task 9)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .row_provider import Row


@dataclass
class CytoscapeElement:
    data: dict
    classes: str = ""
    position: Optional[dict] = None


@dataclass
class EditorState:
    site: str
    rows: list
    nodes: list
    edges: list
    pending_changes: dict


@dataclass
class SaveResult:
    updated: int
    inserted: int
    deleted: int
    errors: tuple
