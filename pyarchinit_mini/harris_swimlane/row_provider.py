"""RowProvider — derives swimlane rows from period_table (priority) or
distinct (periodo_iniziale, fase_iniziale) from periodizzazione_table + us_table (fallback)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from .compound_layout import derive_row_id


# Reused from graphml_converter/yed_template.py:YEdTemplate.PERIOD_COLORS
PERIOD_COLORS = [
    "#9642B7", "#7204CB", "#20ADB7", "#65C3E4", "#FA9639",
    "#85E1C9", "#6105C3", "#1DBCB1", "#9DC185", "#CB99D2",
    "#B7D2DF", "#D406E6", "#1E4B4B", "#7E0BD6", "#07D688",
    "#D37843", "#342400", "#F747A0", "#52BD36", "#E58042",
    "#097728", "#C84643", "#C9FC9E", "#085DE8", "#E4CC6F",
    "#3A8B9E", "#D4A5E8", "#8FE3B0", "#F2A65A", "#7B68EE",
]


@dataclass(frozen=True)
class Row:
    row_id: str
    period_name: str
    phase_name: Optional[str]
    start_date: Optional[int]
    end_date: Optional[int]
    color: str
    source: str  # "period_table" | "fallback_distinct"


class RowProvider:
    def __init__(self, session: Session, site: str) -> None:
        self.session = session
        self.site = site
        self._cache: Optional[list[Row]] = None

    def list_rows(self) -> list[Row]:
        if self._cache is not None:
            return self._cache
        rows = self._load_from_period_table()
        if not rows:
            rows = self._load_fallback()
        self._cache = rows
        return rows

    def find_row(self, period: str, phase: Optional[str]) -> Optional[Row]:
        for r in self.list_rows():
            if r.period_name == period and (r.phase_name or None) == (phase or None):
                return r
        return None

    def _load_from_period_table(self) -> list[Row]:
        """Load rows from ``period_table`` using the real pyarchinit schema.

        pyarchinit's ``period_table`` ships with columns ``periodo`` /
        ``fase`` / ``datazione`` / ``sito`` — there are no numeric
        ``start_date`` / ``end_date`` columns, so we leave those as ``None``
        and sort alphabetically. The ``sito`` column is filtered when
        present (cross-site rows with NULL/empty ``sito`` are still kept,
        matching legacy pyarchinit behaviour).
        """
        # SQLite < 3.30 doesn't support NULLS LAST. Sort in Python for portability.
        result = self.session.execute(
            text(
                "SELECT periodo, fase, datazione "
                "FROM period_table "
                "WHERE sito = :sito OR sito IS NULL OR sito = ''"
            ),
            {"sito": self.site},
        ).fetchall()
        sorted_result = sorted(
            (r for r in result if r[0]),
            key=lambda r: (r[0] or "", r[1] or ""),
        )
        out = []
        for i, r in enumerate(sorted_result):
            period = r[0]
            phase = r[1]
            row_id = derive_row_id(period, phase)
            out.append(Row(
                row_id=row_id,
                period_name=period,
                phase_name=phase,
                start_date=None,
                end_date=None,
                color=PERIOD_COLORS[i % len(PERIOD_COLORS)],
                source="period_table",
            ))
        return out

    def _load_fallback(self) -> list[Row]:
        sql = (
            "SELECT DISTINCT periodo_iniziale, fase_iniziale "
            "FROM periodizzazione_table WHERE sito = :sito "
            "UNION "
            "SELECT DISTINCT periodo_iniziale, fase_iniziale "
            "FROM us_table WHERE sito = :sito"
        )
        result = self.session.execute(text(sql), {"sito": self.site}).fetchall()
        sorted_result = sorted(
            (r for r in result if r[0]),
            key=lambda r: (r[0] or "", r[1] or ""),
        )
        out = []
        for i, r in enumerate(sorted_result):
            period = r[0]
            phase = r[1]
            row_id = derive_row_id(period, phase)
            out.append(Row(
                row_id=row_id,
                period_name=period,
                phase_name=phase,
                start_date=None,
                end_date=None,
                color=PERIOD_COLORS[i % len(PERIOD_COLORS)],
                source="fallback_distinct",
            ))
        return out
