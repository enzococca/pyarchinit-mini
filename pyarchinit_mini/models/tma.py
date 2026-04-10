"""
TMA - Tabella Materiali Archeologici
Two related tables: tma_materiali_archeologici (master) + tma_materiali_ripetibili (detail)
"""

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from .base import BaseModel


class TmaMaterialiArcheologici(BaseModel):
    """Master TMA record (one per crate/box)"""
    __tablename__ = 'tma_materiali_archeologici'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identification
    sito = Column(Text)
    area = Column(Text)
    localita = Column(Text)
    settore = Column(Text)
    inventario = Column(Text)

    # Object data (OG)
    ogtm = Column(Text)  # Material type

    # Location data (LC)
    ldct = Column(Text)              # Location type
    ldcn = Column(Text)              # Location denomination
    vecchia_collocazione = Column(Text)
    cassetta = Column(Text)          # Box

    # Excavation data (RE - DSC)
    scan = Column(Text)              # Excavation name
    saggio = Column(Text)            # Test pit
    vano_locus = Column(Text)        # Room/Locus
    dscd = Column(Text)              # Excavation date
    dscu = Column(Text)              # Stratigraphic Unit (US)

    # Survey data (RE - RCG)
    rcgd = Column(Text)              # Survey date
    rcgz = Column(Text)              # Survey specifications

    # Other acquisition (RE - AIN)
    aint = Column(Text)              # Acquisition type
    aind = Column(Text)              # Acquisition date

    # Dating (DT)
    dtzg = Column(Text)              # Chronological range

    # Analytical data (DA)
    deso = Column(Text)              # Object indications

    # Historical-critical notes (NSC)
    nsc = Column(Text)

    # Documentation (DO)
    ftap = Column(Text)              # Photo type
    ftan = Column(Text)              # Photo identification code
    drat = Column(Text)              # Drawing type
    dran = Column(Text)              # Drawing identification code
    draa = Column(Text)              # Drawing author

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TmaMaterialiRipetibili(BaseModel):
    """Repetitive material data — many rows per TMA master record"""
    __tablename__ = 'tma_materiali_ripetibili'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_tma = Column(Integer, nullable=True, index=True)  # FK to tma_materiali_archeologici.id

    # Material description (MAD)
    madi = Column(String(50))        # Inventory

    # Material component (MAC) - all repetitive
    macc = Column(String(50))        # Category
    macl = Column(String(50))        # Class
    macp = Column(String(50))        # Typological specification
    macd = Column(String(50))        # Definition
    cronologia_mac = Column(String(100))
    macq = Column(String(20))        # Quantity
    peso = Column(Float)             # Weight

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}