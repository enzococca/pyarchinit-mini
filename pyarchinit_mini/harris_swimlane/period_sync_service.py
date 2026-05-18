"""PeriodSyncService — interactive row creation upserts period_table.

When user creates a new swimlane row in the editor, this service ensures
a corresponding ``period_table`` entry exists. Uses the real pyarchinit
schema: ``periodo`` / ``fase`` / ``datazione`` (NO numeric start/end columns).

Caller-supplied ``start_date`` / ``end_date`` (ints) are stringified into
``datazione`` as ``"start..end"`` when both provided, single year otherwise.
On promote (``maybe_promote_fallback``), idempotency is on ``(periodo, fase)``.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from .compound_layout import derive_row_id
from .exceptions import PeriodSyncError
from .row_provider import Row, PERIOD_COLORS


def _format_datazione(start: Optional[int], end: Optional[int]) -> Optional[str]:
    if start is None and end is None:
        return None
    if start is not None and end is not None:
        return f"{start}..{end}"
    return str(start if start is not None else end)


class PeriodSyncService:
    def __init__(self, session: Session, site: Optional[str] = None) -> None:
        self.session = session
        self.site = site

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
            "SELECT id_period FROM period_table "
            "WHERE periodo = :p AND "
            "(fase = :ph OR (fase IS NULL AND :ph IS NULL))"
        ), {"p": period_name, "ph": phase_name}).fetchone()

        if existing is None:
            self.session.execute(text(
                "INSERT INTO period_table (sito, periodo, fase, datazione) "
                "VALUES (:s, :p, :ph, :dz)"
            ), {
                "s": self.site,
                "p": period_name,
                "ph": phase_name,
                "dz": _format_datazione(start_date, end_date),
            })
            self.session.commit()

        row_id = derive_row_id(period_name, phase_name)
        return Row(
            row_id=row_id,
            period_name=period_name,
            phase_name=phase_name,
            start_date=start_date,
            end_date=end_date,
            color=PERIOD_COLORS[0],
            source="period_table",
        )

    def maybe_promote_fallback(self, site: str) -> int:
        """Bulk-promote distinct (periodo_iniziale, fase_iniziale) values into
        ``period_table``. Idempotent on ``(periodo, fase)``. Returns count promoted."""
        # Bind site at promotion time so INSERTs land on the right row.
        prev_site = self.site
        self.site = site
        try:
            existing = {
                (r[0], r[1])
                for r in self.session.execute(text(
                    "SELECT periodo, fase FROM period_table "
                    "WHERE sito = :s OR sito IS NULL OR sito = ''"
                ), {"s": site}).fetchall()
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
        finally:
            self.site = prev_site
