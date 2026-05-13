"""Data Transfer Object for Pottery records."""
from __future__ import annotations

from dataclasses import dataclass, fields, asdict
from datetime import datetime
from decimal import Decimal
from typing import Optional


def _to_float(v):
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    return v


@dataclass
class PotteryDTO:
    id_rep: Optional[int] = None
    id_number: Optional[int] = None
    sito: Optional[str] = None
    area: Optional[str] = None
    us: Optional[int] = None
    box: Optional[int] = None
    photo: Optional[str] = None
    drawing: Optional[str] = None
    anno: Optional[int] = None
    fabric: Optional[str] = None
    percent: Optional[str] = None
    material: Optional[str] = None
    form: Optional[str] = None
    specific_form: Optional[str] = None
    ware: Optional[str] = None
    munsell: Optional[str] = None
    surf_trat: Optional[str] = None
    exdeco: Optional[str] = None
    intdeco: Optional[str] = None
    wheel_made: Optional[str] = None
    descrip_ex_deco: Optional[str] = None
    descrip_in_deco: Optional[str] = None
    note: Optional[str] = None
    diametro_max: Optional[float] = None
    qty: Optional[int] = None
    diametro_rim: Optional[float] = None
    diametro_bottom: Optional[float] = None
    diametro_height: Optional[float] = None
    diametro_preserved: Optional[float] = None
    specific_shape: Optional[str] = None
    bag: Optional[int] = None
    sector: Optional[str] = None

    # Sync / audit
    entity_uuid: Optional[str] = None
    version_number: Optional[int] = None
    sync_status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_model(cls, m) -> "PotteryDTO":
        kw = {}
        names = {f.name for f in fields(cls)}
        for n in names:
            v = getattr(m, n, None)
            if n.startswith("diametro_"):
                v = _to_float(v)
            kw[n] = v
        return cls(**kw)

    def to_dict(self) -> dict:
        return asdict(self)
