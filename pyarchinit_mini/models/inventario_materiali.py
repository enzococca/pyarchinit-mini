"""
Material inventory model - Complete PyArchInit compatibility
"""

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .base import BaseModel

class InventarioMateriali(BaseModel):
    """
    Material inventory model
    Complete implementation from PyArchInit INVENTARIO_MATERIALI entity
    """
    __tablename__ = 'inventario_materiali_table'
    
    # Primary key and identification
    id_invmat = Column(Integer, primary_key=True, autoincrement=True)
    sito = Column(Text, ForeignKey('site_table.sito', ondelete='CASCADE'), nullable=False)
    numero_inventario = Column(Integer, nullable=False)
    
    # Classification and description (i18n fields)
    # Legacy columns (kept for backward compatibility, map to IT)
    tipo_reperto = Column(Text)
    criterio_schedatura = Column(Text)
    definizione = Column(Text)
    descrizione = Column(Text)

    # English translations (new columns)
    tipo_reperto_en = Column(Text)
    criterio_schedatura_en = Column(Text)
    definizione_en = Column(Text)
    descrizione_en = Column(Text)
    
    # Context information
    area = Column(Text)
    us = Column(Text)  # Changed to Text as per original schema
    
    # Physical state and processing (i18n for conservation state)
    lavato = Column(String(3))  # Language-neutral (Sì/No)
    nr_cassa = Column(Text)  # Language-neutral (box number)
    luogo_conservazione = Column(Text)  # Language-neutral (location)
    stato_conservazione = Column(String(200))  # Legacy IT

    # English translations (new columns)
    stato_conservazione_en = Column(String(200))
    
    # Dating and documentation (i18n for elementi_reperto)
    datazione_reperto = Column(String(200))  # Language-neutral (dates/periods)
    elementi_reperto = Column(Text)  # Legacy IT
    misurazioni = Column(Text)  # Language-neutral (measurements)
    rif_biblio = Column(Text)  # Language-neutral (biblio refs)

    # English translations (new columns)
    elementi_reperto_en = Column(Text)
    
    # Technical characteristics
    tecnologie = Column(Text)
    forme_minime = Column(Integer)
    forme_massime = Column(Integer)
    totale_frammenti = Column(Integer)
    
    # Ceramic specific fields (i18n for descriptive ones)
    corpo_ceramico = Column(String(200))  # Legacy IT
    rivestimento = Column(String(200))  # Legacy IT
    diametro_orlo = Column(Numeric(7, 3))  # Language-neutral (measurement)
    peso = Column(Numeric(9, 3))  # Language-neutral (measurement)
    tipo = Column(String(200))  # Language-neutral (type code)
    eve_orlo = Column(Numeric(7, 3))  # Language-neutral (measurement)

    # English translations (new columns)
    corpo_ceramico_en = Column(String(200))
    rivestimento_en = Column(String(200))
    
    # Classification flags
    repertato = Column(String(3))  # Changed to String(3) as per original
    diagnostico = Column(String(3))  # Changed to String(3) as per original
    
    # Additional identification and context (i18n for tipo_contenitore)
    n_reperto = Column(Integer)  # Language-neutral (artifact number)
    tipo_contenitore = Column(String(200))  # Legacy IT
    struttura = Column(String(200))  # Language-neutral (structure code)
    years = Column(Integer)  # Language-neutral (year)

    # English translations (new columns)
    tipo_contenitore_en = Column(String(200))
    
    # Additional fields from original PyArchInit schema
    schedatore = Column(Text)  # Who catalogued the item
    date_scheda = Column(Text)  # Date of cataloguing
    punto_rinv = Column(Text)  # Find point/location
    negativo_photo = Column(Text)  # Photo negative reference
    diapositiva = Column(Text)  # Slide reference
    
    # Relationships
    site_ref = relationship("Site", foreign_keys=[sito],
                           primaryjoin="InventarioMateriali.sito == Site.sito")

    # Note: US relationship would need proper foreign key setup
    # us_ref = relationship("US", foreign_keys=[sito, area, us])

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
            field_base: Base field name (e.g., 'tipo_reperto')
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

    # ========== Classification and description methods ==========

    def get_tipo_reperto(self, locale='it'):
        """Get artifact type in specified locale"""
        return self.get_field_localized('tipo_reperto', locale)

    def get_criterio_schedatura(self, locale='it'):
        """Get cataloguing criterion in specified locale"""
        return self.get_field_localized('criterio_schedatura', locale)

    def get_definizione(self, locale='it'):
        """Get definition in specified locale"""
        return self.get_field_localized('definizione', locale)

    def get_descrizione(self, locale='it'):
        """Get description in specified locale"""
        return self.get_field_localized('descrizione', locale)

    def get_stato_conservazione(self, locale='it'):
        """Get conservation state in specified locale"""
        return self.get_field_localized('stato_conservazione', locale)

    def get_elementi_reperto(self, locale='it'):
        """Get artifact elements in specified locale"""
        return self.get_field_localized('elementi_reperto', locale)

    def get_corpo_ceramico(self, locale='it'):
        """Get ceramic body in specified locale"""
        return self.get_field_localized('corpo_ceramico', locale)

    def get_rivestimento(self, locale='it'):
        """Get coating/covering in specified locale"""
        return self.get_field_localized('rivestimento', locale)

    def get_tipo_contenitore(self, locale='it'):
        """Get container type in specified locale"""
        return self.get_field_localized('tipo_contenitore', locale)

    # ========== Auto-detected locale properties ==========

    @property
    def tipo_reperto_localized(self):
        """Artifact type in current locale"""
        return self.get_tipo_reperto(self.get_current_locale())

    @property
    def criterio_schedatura_localized(self):
        """Cataloguing criterion in current locale"""
        return self.get_criterio_schedatura(self.get_current_locale())

    @property
    def definizione_localized(self):
        """Definition in current locale"""
        return self.get_definizione(self.get_current_locale())

    @property
    def descrizione_localized(self):
        """Description in current locale"""
        return self.get_descrizione(self.get_current_locale())

    @property
    def stato_conservazione_localized(self):
        """Conservation state in current locale"""
        return self.get_stato_conservazione(self.get_current_locale())

    @property
    def elementi_reperto_localized(self):
        """Artifact elements in current locale"""
        return self.get_elementi_reperto(self.get_current_locale())

    @property
    def corpo_ceramico_localized(self):
        """Ceramic body in current locale"""
        return self.get_corpo_ceramico(self.get_current_locale())

    @property
    def rivestimento_localized(self):
        """Coating/covering in current locale"""
        return self.get_rivestimento(self.get_current_locale())

    @property
    def tipo_contenitore_localized(self):
        """Container type in current locale"""
        return self.get_tipo_contenitore(self.get_current_locale())

    def __repr__(self):
        return f"<InventarioMateriali(id={self.id_invmat}, sito='{self.sito}', " \
               f"numero={self.numero_inventario}, tipo='{self.tipo_reperto}')>"
    
    @property
    def display_name(self):
        """Human readable identifier"""
        return f"Inv. {self.numero_inventario} - {self.tipo_reperto} ({self.sito})"
    
    @property
    def context_info(self):
        """Context information as string"""
        context_parts = []
        if self.area:
            context_parts.append(f"Area {self.area}")
        if self.us:
            context_parts.append(f"US {self.us}")
        return " - ".join(context_parts) if context_parts else "Nessun contesto"