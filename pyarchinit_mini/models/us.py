"""
Stratigraphic Unit (US) model
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class US(BaseModel):
    """
    Stratigraphic Unit model
    Adapted from PyArchInit US entity with key fields
    """
    __tablename__ = 'us_table'
    
    # Primary key and identification
    id_us = Column(Integer, primary_key=True, autoincrement=True)
    sito = Column(String(350), ForeignKey('site_table.sito', ondelete='CASCADE'), nullable=False)
    area = Column(String(20))
    us = Column(Integer, nullable=False)
    
    # Basic stratigraphic information (i18n fields)
    # Legacy columns (kept for backward compatibility, map to IT)
    d_stratigrafica = Column(String(350))
    d_interpretativa = Column(String(350))
    descrizione = Column(Text)
    interpretazione = Column(Text)

    # English translations (new columns)
    d_stratigrafica_en = Column(String(350))
    d_interpretativa_en = Column(String(350))
    descrizione_en = Column(Text)
    interpretazione_en = Column(Text)
    
    # Chronological data
    periodo_iniziale = Column(String(300))
    fase_iniziale = Column(String(300))
    periodo_finale = Column(String(300))
    fase_finale = Column(String(300))
    
    # Excavation data
    scavato = Column(String(20))
    attivita = Column(String(30))
    anno_scavo = Column(Integer)
    metodo_di_scavo = Column(String(20))
    data_schedatura = Column(Date)
    schedatore = Column(String(100))
    
    # Physical characteristics (i18n fields)
    # Legacy columns (kept for backward compatibility, map to IT)
    formazione = Column(String(20))
    stato_di_conservazione = Column(String(20))
    colore = Column(String(20))
    consistenza = Column(String(20))
    struttura = Column(String(30))

    # English translations (new columns)
    formazione_en = Column(String(20))
    stato_di_conservazione_en = Column(String(20))
    colore_en = Column(String(20))
    consistenza_en = Column(String(20))
    struttura_en = Column(String(30))
    
    # Documentation and relationships (i18n fields for some)
    # Legacy columns (kept for backward compatibility, map to IT)
    inclusi = Column(Text)
    campioni = Column(Text)
    rapporti = Column(Text)  # Language-neutral
    documentazione = Column(Text)
    cont_per = Column(Text)  # Language-neutral
    order_layer = Column(Integer)  # Language-neutral

    # English translations (new columns)
    inclusi_en = Column(Text)
    campioni_en = Column(Text)
    documentazione_en = Column(Text)
    
    # USM specific fields (Unità Stratigrafiche Murarie)
    unita_tipo = Column(String(200))
    settore = Column(String(200))
    quad_par = Column(String(200))
    ambient = Column(String(200))
    saggio = Column(String(200))
    
    # Additional ICCD alignment fields
    n_catalogo_generale = Column(String(25))
    n_catalogo_interno = Column(String(25))
    n_catalogo_internazionale = Column(String(25))
    soprintendenza = Column(String(200))
    
    # Measurements
    quota_relativa = Column(Float)
    quota_abs = Column(Float)
    lunghezza_max = Column(Float)
    altezza_max = Column(Float)
    altezza_min = Column(Float)
    profondita_max = Column(Float)
    profondita_min = Column(Float)
    larghezza_media = Column(Float)
    
    # Additional data (i18n for observations)
    # Legacy columns (kept for backward compatibility, map to IT)
    osservazioni = Column(Text)
    datazione = Column(String(100))  # Language-neutral
    flottazione = Column(String(5))  # Language-neutral
    setacciatura = Column(String(5))  # Language-neutral
    affidabilita = Column(String(5))  # Language-neutral
    direttore_us = Column(String(100))  # Language-neutral (names)
    responsabile_us = Column(String(100))  # Language-neutral (names)

    # English translations (new columns)
    osservazioni_en = Column(Text)
    
    # Relationships
    site_ref = relationship("Site", foreign_keys=[sito], 
                           primaryjoin="US.sito == Site.sito")
    
    def __repr__(self):
        return f"<US(id={self.id_us}, sito='{self.sito}', area='{self.area}', us={self.us})>"

    @property
    def display_name(self):
        """Human readable identifier for the US"""
        return f"US {self.us} - Area {self.area} ({self.sito})"

    # ========== Locale-aware helper methods ==========

    @staticmethod
    def get_current_locale():
        """Get current locale from Flask request context or default to 'it'

        Returns:
            Language code ('it' or 'en')
        """
        try:
            from flask import has_request_context
            if has_request_context():
                from pyarchinit_mini.i18n import get_locale
                return str(get_locale())
        except ImportError:
            pass
        return 'it'

    def get_field_localized(self, field_base, locale='it'):
        """Get any field in specified locale with fallback to IT

        Args:
            field_base: Base field name (e.g., 'd_stratigrafica')
            locale: Language code ('it' or 'en')

        Returns:
            Field value in requested language, fallback to IT if EN not available
        """
        if locale == 'en':
            en_field = f"{field_base}_en"
            en_value = getattr(self, en_field, None)
            if en_value:
                return en_value
        return getattr(self, field_base, None)

    # ========== Stratigraphic description methods ==========

    def get_d_stratigrafica(self, locale='it'):
        """Get stratigraphic description in specified locale"""
        return self.get_field_localized('d_stratigrafica', locale)

    def get_d_interpretativa(self, locale='it'):
        """Get interpretative description in specified locale"""
        return self.get_field_localized('d_interpretativa', locale)

    def get_descrizione(self, locale='it'):
        """Get general description in specified locale"""
        return self.get_field_localized('descrizione', locale)

    def get_interpretazione(self, locale='it'):
        """Get interpretation in specified locale"""
        return self.get_field_localized('interpretazione', locale)

    # ========== Physical characteristics methods ==========

    def get_formazione(self, locale='it'):
        """Get formation process in specified locale"""
        return self.get_field_localized('formazione', locale)

    def get_stato_di_conservazione(self, locale='it'):
        """Get conservation state in specified locale"""
        return self.get_field_localized('stato_di_conservazione', locale)

    def get_colore(self, locale='it'):
        """Get color in specified locale"""
        return self.get_field_localized('colore', locale)

    def get_consistenza(self, locale='it'):
        """Get consistency in specified locale"""
        return self.get_field_localized('consistenza', locale)

    def get_struttura(self, locale='it'):
        """Get structure in specified locale"""
        return self.get_field_localized('struttura', locale)

    # ========== Documentation methods ==========

    def get_inclusi(self, locale='it'):
        """Get inclusions in specified locale"""
        return self.get_field_localized('inclusi', locale)

    def get_campioni(self, locale='it'):
        """Get samples in specified locale"""
        return self.get_field_localized('campioni', locale)

    def get_documentazione(self, locale='it'):
        """Get documentation in specified locale"""
        return self.get_field_localized('documentazione', locale)

    def get_osservazioni(self, locale='it'):
        """Get observations in specified locale"""
        return self.get_field_localized('osservazioni', locale)

    # ========== Auto-detected locale properties ==========

    @property
    def d_stratigrafica_localized(self):
        """Stratigraphic description in current locale"""
        return self.get_d_stratigrafica(self.get_current_locale())

    @property
    def d_interpretativa_localized(self):
        """Interpretative description in current locale"""
        return self.get_d_interpretativa(self.get_current_locale())

    @property
    def descrizione_localized(self):
        """General description in current locale"""
        return self.get_descrizione(self.get_current_locale())

    @property
    def interpretazione_localized(self):
        """Interpretation in current locale"""
        return self.get_interpretazione(self.get_current_locale())

    @property
    def formazione_localized(self):
        """Formation process in current locale"""
        return self.get_formazione(self.get_current_locale())

    @property
    def stato_di_conservazione_localized(self):
        """Conservation state in current locale"""
        return self.get_stato_di_conservazione(self.get_current_locale())

    @property
    def colore_localized(self):
        """Color in current locale"""
        return self.get_colore(self.get_current_locale())

    @property
    def consistenza_localized(self):
        """Consistency in current locale"""
        return self.get_consistenza(self.get_current_locale())

    @property
    def struttura_localized(self):
        """Structure in current locale"""
        return self.get_struttura(self.get_current_locale())

    @property
    def inclusi_localized(self):
        """Inclusions in current locale"""
        return self.get_inclusi(self.get_current_locale())

    @property
    def campioni_localized(self):
        """Samples in current locale"""
        return self.get_campioni(self.get_current_locale())

    @property
    def documentazione_localized(self):
        """Documentation in current locale"""
        return self.get_documentazione(self.get_current_locale())

    @property
    def osservazioni_localized(self):
        """Observations in current locale"""
        return self.get_osservazioni(self.get_current_locale())
    
    @property
    def full_identifier(self):
        """Complete identifier: Site.Area.US"""
        return f"{self.sito}.{self.area}.{self.us}"