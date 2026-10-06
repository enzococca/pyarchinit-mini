"""Swimlane period rows from mini's period_table (moved from s3d_projector)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy import text

FALLBACK_LABEL = "Periodo 1"


@dataclass
class PeriodRow:
    row_id: str
    label: str
    periodo: Optional[str] = None
    fase: Optional[str] = None
    datazione: Optional[str] = None
    is_fallback: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {"row_id": self.row_id, "label": self.label, "periodo": self.periodo,
                "fase": self.fase, "datazione": self.datazione, "is_fallback": self.is_fallback}


def load_period_rows(session, site: str) -> List[PeriodRow]:
    rows = session.execute(
        text("SELECT periodo, fase, datazione FROM period_table "
             "WHERE sito = :s OR sito IS NULL OR sito = ''"),
        {"s": site},
    ).fetchall()
    items = [(p, (f or None), d) for p, f, d in rows if p]
    items.sort(key=lambda t: (str(t[0] or ""), str(t[1] or "")))
    return [
        PeriodRow(row_id=f"row_{i}", label=(f"{p}/{f}" if f else str(p)), periodo=p, fase=f, datazione=d)
        for i, (p, f, d) in enumerate(items)
    ]


def resolve_row_id(rows: List[PeriodRow], phase: Optional[str]) -> str:
    if phase is not None:
        for r in rows:
            if not r.is_fallback and (r.fase == phase or r.periodo == phase):
                return r.row_id
    for r in rows:
        if r.is_fallback:
            return r.row_id
    fallback = PeriodRow(row_id=f"row_{len(rows)}", label=FALLBACK_LABEL, is_fallback=True)
    rows.append(fallback)
    return fallback.row_id
