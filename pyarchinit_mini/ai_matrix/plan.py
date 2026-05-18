"""Dataclasses for AI Matrix Import plan + extraction results."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass
class USRow:
    us_num: str
    area: str | None
    unit_type: str
    descrizione: str
    fase_recente: int
    fase_iniziale: int


@dataclass
class EdgeRow:
    us_from: str
    us_to: str
    tipo: str


@dataclass
class AIPlan:
    detected_site: str | None
    detected_area: str | None
    us: list[USRow] = field(default_factory=list)
    edges: list[EdgeRow] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "detected_site": self.detected_site,
            "detected_area": self.detected_area,
            "us": [asdict(u) for u in self.us],
            "edges": [asdict(e) for e in self.edges],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AIPlan":
        return cls(
            detected_site=d.get("detected_site"),
            detected_area=d.get("detected_area"),
            us=[USRow(**u) for u in d.get("us", [])],
            edges=[EdgeRow(**e) for e in d.get("edges", [])],
        )


@dataclass
class ExtractResult:
    rejected: bool
    reason: str
    confidence: float
    plan: AIPlan | None
