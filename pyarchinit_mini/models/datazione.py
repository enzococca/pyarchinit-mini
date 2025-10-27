#!/usr/bin/env python3
"""
Datazione Model - Chronological Dating System
==============================================

Manages archaeological chronological datings with name and time range.

Author: PyArchInit Team
License: GPL v2
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .base import BaseModel


class Datazione(BaseModel):
    """
    Datazione table - Archaeological chronological datings

    Stores standardized chronological datings with:
    - Nome datazione (Dating name)
    - Fascia cronologica (Time range/period)

    Used in US records to provide consistent chronological references.
    """

    __tablename__ = 'datazioni_table'

    # Primary key
    id_datazione = Column(Integer, primary_key=True, autoincrement=True)

    # Dating identification
    nome_datazione = Column(String(200), nullable=False, unique=True,
                           comment='Name of the chronological dating (e.g., "Età del Bronzo Antico")')

    fascia_cronologica = Column(String(200), nullable=True,
                                comment='Time range (e.g., "2200-1900 a.C.")')

    # Additional info
    descrizione = Column(Text, nullable=True,
                        comment='Detailed description of the dating period')

    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Datazione(id={self.id_datazione}, nome='{self.nome_datazione}', fascia='{self.fascia_cronologica}')>"

    @property
    def full_label(self):
        """Get full label with nome + fascia cronologica"""
        if self.fascia_cronologica:
            return f"{self.nome_datazione} ({self.fascia_cronologica})"
        return self.nome_datazione

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id_datazione': self.id_datazione,
            'nome_datazione': self.nome_datazione,
            'fascia_cronologica': self.fascia_cronologica,
            'descrizione': self.descrizione,
            'full_label': self.full_label,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
