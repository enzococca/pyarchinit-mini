"""PeriodSyncService — interactive row creation upserts period_table.

When user creates a new swimlane row in the editor, this service ensures
a corresponding period_table entry exists. Idempotent on (period_name, phase_name).
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from .compound_layout import derive_row_id
from .exceptions import PeriodSyncError
from .row_provider import Row, PERIOD_COLORS


class PeriodSyncService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_row(self, period_name: str, phase_name: Optional[str] = None,
                   start_date: Optional[int] = None,
                   end_date: Optional[int] = None) -> Row:
        if not period_name or not period_name.strip():
            raise PeriodSyncError("period_name is required",
                                   period_name=period_name, phase_name=phase_name)
        if start_date is not None and end_date is not None and start_date > end_date:
            raise PeriodSyncError(
                "start_date must be <= end_date",
                period_name=period_name, phase_name=phase_name,
            )

        existing = self.session.execute(text(
            "SELECT id_period, start_date, end_date FROM period_table "
            "WHERE period_name = :p AND "
            "(phase_name = :ph OR (phase_name IS NULL AND :ph IS NULL))"
        ), {"p": period_name, "ph": phase_name}).fetchone()

        if existing is None:
            self.session.execute(text(
                "INSERT INTO period_table (period_name, phase_name, start_date, end_date) "
                "VALUES (:p, :ph, :sd, :ed)"
            ), {"p": period_name, "ph": phase_name, "sd": start_date, "ed": end_date})
            self.session.commit()
            sd = start_date
            ed = end_date
        else:
            sd = existing[1]
            ed = existing[2]

        row_id = derive_row_id(period_name, phase_name)
        return Row(
            row_id=row_id,
            period_name=period_name,
            phase_name=phase_name,
            start_date=sd,
            end_date=ed,
            color=PERIOD_COLORS[0],
            source="period_table",
        )

    def maybe_promote_fallback(self, site: str) -> int:
        """Bulk-promote distinct (periodo_iniziale, fase_iniziale) values into
        period_table. Idempotent. Returns count promoted."""
        existing = {
            (r[0], r[1])
            for r in self.session.execute(text(
                "SELECT period_name, phase_name FROM period_table"
            )).fetchall()
        }
        candidates = self.session.execute(text(
            "SELECT DISTINCT periodo_iniziale, fase_iniziale "
            "FROM periodizzazione_table WHERE sito = :s "
            "UNION "
            "SELECT DISTINCT periodo_iniziale, fase_iniziale "
            "FROM us_table WHERE sito = :s"
        ), {"s": site}).fetchall()
        count = 0
        for period, phase in candidates:
            if not period:
                continue
            if (period, phase) in existing:
                continue
            try:
                self.upsert_row(period_name=period, phase_name=phase)
                count += 1
            except PeriodSyncError:
                continue
        return count
