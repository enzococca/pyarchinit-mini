"""
Pottery model — 1:1 schema parity with PyArchInit-QGIS pottery_table.

Inherits sync/audit columns from BaseModel:
- created_at, updated_at
- entity_uuid, version_number
- last_modified_by, last_modified_timestamp
- sync_status, editing_by, editing_since
"""
from sqlalchemy import Column, Integer, Text, Numeric, UniqueConstraint, Index

from .base import BaseModel


class Pottery(BaseModel):
    __tablename__ = "pottery_table"

    # 32 columns mirroring PyArchInit-QGIS Pottery_table.py
    id_rep = Column(Integer, primary_key=True, autoincrement=True)
    id_number = Column(Integer, nullable=True)
    sito = Column(Text, nullable=False)
    area = Column(Text)
    us = Column(Integer)
    box = Column(Integer)
    photo = Column(Text)
    drawing = Column(Text)
    anno = Column(Integer)
    fabric = Column(Text)
    percent = Column(Text)
    material = Column(Text)
    form = Column(Text)
    specific_form = Column(Text)
    ware = Column(Text)
    munsell = Column(Text)
    surf_trat = Column(Text)
    exdeco = Column(Text)
    intdeco = Column(Text)
    wheel_made = Column(Text)
    descrip_ex_deco = Column(Text)
    descrip_in_deco = Column(Text)
    note = Column(Text)
    diametro_max = Column(Numeric(7, 3))
    qty = Column(Integer)
    diametro_rim = Column(Numeric(7, 3))
    diametro_bottom = Column(Numeric(7, 3))
    diametro_height = Column(Numeric(7, 3))
    diametro_preserved = Column(Numeric(7, 3))
    specific_shape = Column(Text)
    bag = Column(Integer)
    sector = Column(Text)

    __table_args__ = (
        UniqueConstraint("sito", "id_number", name="ID_rep_unico"),
        Index("ix_pottery_sito_area_us", "sito", "area", "us"),
        Index("ix_pottery_form", "form"),
        Index("ix_pottery_fabric", "fabric"),
    )

    def __repr__(self) -> str:
        return (
            f"<Pottery id_rep={self.id_rep} sito={self.sito!r} "
            f"id_number={self.id_number} form={self.form!r}>"
        )
