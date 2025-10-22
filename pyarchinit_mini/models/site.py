"""
Site model for archaeological sites management
"""

from sqlalchemy import Column, Integer, String, Text, Boolean
from .base import BaseModel


class Site(BaseModel):
    """
    Archaeological site model
    Adapted from PyArchInit SITE entity

    Supports i18n with separate IT/EN columns for translatable fields.
    """
    __tablename__ = 'site_table'

    # Primary key and language-neutral fields
    id_sito = Column(Integer, primary_key=True, autoincrement=True)
    sito = Column(String(350), nullable=False, unique=True)
    nazione = Column(String(250))
    regione = Column(String(250))
    comune = Column(String(250))
    provincia = Column(String(10))
    sito_path = Column(String(500))
    find_check = Column(Boolean, default=False)

    # Translatable fields (Italian + English)
    # Legacy column (kept for backward compatibility, maps to IT)
    definizione_sito = Column(String(250))
    descrizione = Column(Text)

    # English translations (new columns)
    definizione_sito_en = Column(String(250))
    descrizione_en = Column(Text)

    def __repr__(self):
        return f"<Site(id={self.id_sito}, nome='{self.sito}', comune='{self.comune}')>"

    @property
    def display_name(self):
        """Human readable name for the site"""
        return f"{self.sito} ({self.comune}, {self.provincia})"

    # Locale-aware properties
    def get_definizione_sito(self, locale='it'):
        """Get site definition in specified locale

        Args:
            locale: Language code ('it' or 'en')

        Returns:
            Site definition in requested language, fallback to IT if EN not available
        """
        if locale == 'en' and self.definizione_sito_en:
            return self.definizione_sito_en
        return self.definizione_sito

    def get_descrizione(self, locale='it'):
        """Get site description in specified locale

        Args:
            locale: Language code ('it' or 'en')

        Returns:
            Site description in requested language, fallback to IT if EN not available
        """
        if locale == 'en' and self.descrizione_en:
            return self.descrizione_en
        return self.descrizione

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

    @property
    def definizione_sito_localized(self):
        """Get site definition in current locale (auto-detected)"""
        return self.get_definizione_sito(self.get_current_locale())

    @property
    def descrizione_localized(self):
        """Get site description in current locale (auto-detected)"""
        return self.get_descrizione(self.get_current_locale())