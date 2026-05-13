"""Render Pottery records to PDF via WeasyPrint."""
from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from typing import Iterable, List

from flask import render_template

from ..models.pottery import Pottery
from .pottery_dto import PotteryDTO


class PotteryPDFService:
    @staticmethod
    def render_sheets(potteries: Iterable[Pottery], version: str = "2.1.60") -> bytes:
        from weasyprint import HTML  # lazy import — heavy dependency
        dtos: List[PotteryDTO] = [PotteryDTO.from_model(p) for p in potteries]
        html = render_template(
            "pdf/pottery_sheet.html",
            potteries=dtos,
            version=version,
            printed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        )
        buf = BytesIO()
        HTML(string=html).write_pdf(buf)
        buf.seek(0)
        return buf.read()
