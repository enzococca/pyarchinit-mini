#!/usr/bin/env python3
"""
Datazione Service - Chronological Dating Management
====================================================

Service layer for managing archaeological chronological datings.

Author: PyArchInit Team
License: GPL v2
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.exc import IntegrityError

from ..database.manager import DatabaseManager
from ..models.datazione import Datazione
from ..utils.exceptions import ValidationError, RecordNotFoundError, DatabaseError


class DatazioneService:
    """Service class for Datazione operations"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def create_datazione(self, datazione_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new datazione

        Args:
            datazione_data: Dictionary with datazione fields

        Returns:
            Created Datazione dict

        Raises:
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        # Validate required fields
        if not datazione_data.get('nome_datazione'):
            raise ValidationError("Nome datazione is required", 'nome_datazione', None)

        try:
            with self.db_manager.connection.get_session() as session:
                datazione = Datazione(**datazione_data)
                session.add(datazione)
                session.flush()
                return datazione.to_dict()
        except IntegrityError as e:
            if 'UNIQUE constraint' in str(e) or 'unique constraint' in str(e).lower():
                raise ValidationError(
                    f"Datazione '{datazione_data['nome_datazione']}' already exists",
                    'nome_datazione',
                    datazione_data['nome_datazione']
                )
            raise DatabaseError(f"Failed to create datazione: {e}")

    def get_datazione_by_id(self, datazione_id: int) -> Optional[Dict[str, Any]]:
        """Get datazione by ID"""
        with self.db_manager.connection.get_session() as session:
            datazione = session.query(Datazione).filter_by(id_datazione=datazione_id).first()
            if datazione:
                return datazione.to_dict()
            return None

    def get_datazione_by_nome(self, nome: str) -> Optional[Dict[str, Any]]:
        """Get datazione by nome"""
        with self.db_manager.connection.get_session() as session:
            datazione = session.query(Datazione).filter_by(nome_datazione=nome).first()
            if datazione:
                return datazione.to_dict()
            return None

    def get_all_datazioni(self, page: int = 1, size: int = 1000) -> List[Dict[str, Any]]:
        """
        Get all datazioni with pagination

        Args:
            page: Page number (1-based)
            size: Number of records per page

        Returns:
            List of Datazione dicts (to avoid session issues)
        """
        try:
            from sqlalchemy import asc
            with self.db_manager.connection.get_session() as session:
                query = session.query(Datazione)

                # Apply ordering by nome_datazione
                query = query.order_by(asc(Datazione.nome_datazione))

                # Apply pagination
                offset = (page - 1) * size
                datazioni = query.offset(offset).limit(size).all()

                # Convert to dicts to avoid detached instance errors
                return [d.to_dict() for d in datazioni]

        except Exception as e:
            raise DatabaseError(f"Failed to get datazioni: {e}")

    def get_datazioni_choices(self) -> List[Dict[str, str]]:
        """
        Get datazioni as choices for forms (nome + fascia)

        Returns:
            List of dicts with 'value' (nome) and 'label' (full_label)
        """
        datazioni = self.get_all_datazioni()
        return [
            {
                'value': d['nome_datazione'],
                'label': d['full_label']
            }
            for d in datazioni
        ]

    def update_datazione(self, datazione_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing datazione

        Args:
            datazione_id: Datazione ID
            update_data: Dictionary with fields to update

        Returns:
            Updated Datazione dict

        Raises:
            RecordNotFoundError: If datazione not found
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        try:
            with self.db_manager.connection.get_session() as session:
                datazione = session.query(Datazione).filter_by(id_datazione=datazione_id).first()
                if not datazione:
                    raise RecordNotFoundError(f"Datazione {datazione_id} not found")

                for key, value in update_data.items():
                    setattr(datazione, key, value)
                session.flush()
                return datazione.to_dict()
        except IntegrityError as e:
            if 'UNIQUE constraint' in str(e) or 'unique constraint' in str(e).lower():
                raise ValidationError(
                    f"Datazione '{update_data.get('nome_datazione')}' already exists",
                    'nome_datazione',
                    update_data.get('nome_datazione')
                )
            raise DatabaseError(f"Failed to update datazione: {e}")

    def delete_datazione(self, datazione_id: int) -> bool:
        """
        Delete datazione

        Args:
            datazione_id: Datazione ID

        Returns:
            True if deleted successfully

        Raises:
            RecordNotFoundError: If datazione not found
            DatabaseError: If database operation fails
        """
        return self.db_manager.delete(Datazione, datazione_id)

    def count_datazioni(self) -> int:
        """Count total datazioni"""
        return self.db_manager.count(Datazione)

    def initialize_default_datazioni(self) -> int:
        """
        Initialize database with default Italian archaeological datazioni

        Returns:
            Number of datazioni created
        """
        default_datazioni = [
            # Preistoria
            {"nome_datazione": "Paleolitico Inferiore", "fascia_cronologica": "2.000.000-300.000 a.C."},
            {"nome_datazione": "Paleolitico Medio", "fascia_cronologica": "300.000-40.000 a.C."},
            {"nome_datazione": "Paleolitico Superiore", "fascia_cronologica": "40.000-10.000 a.C."},
            {"nome_datazione": "Mesolitico", "fascia_cronologica": "10.000-6.000 a.C."},
            {"nome_datazione": "Neolitico Antico", "fascia_cronologica": "6.000-5.000 a.C."},
            {"nome_datazione": "Neolitico Medio", "fascia_cronologica": "5.000-4.300 a.C."},
            {"nome_datazione": "Neolitico Recente", "fascia_cronologica": "4.300-3.500 a.C."},
            {"nome_datazione": "Neolitico Finale", "fascia_cronologica": "3.500-3.200 a.C."},

            # Età dei Metalli
            {"nome_datazione": "Eneolitico/Età del Rame", "fascia_cronologica": "3.200-2.200 a.C."},
            {"nome_datazione": "Età del Bronzo Antico", "fascia_cronologica": "2.200-1.700 a.C."},
            {"nome_datazione": "Età del Bronzo Medio", "fascia_cronologica": "1.700-1.350 a.C."},
            {"nome_datazione": "Età del Bronzo Recente", "fascia_cronologica": "1.350-1.200 a.C."},
            {"nome_datazione": "Età del Bronzo Finale", "fascia_cronologica": "1.200-1.020 a.C."},
            {"nome_datazione": "Prima Età del Ferro", "fascia_cronologica": "1.020-750 a.C."},
            {"nome_datazione": "Seconda Età del Ferro", "fascia_cronologica": "750-580 a.C."},

            # Età Classica
            {"nome_datazione": "Età Arcaica", "fascia_cronologica": "VIII-VI sec. a.C."},
            {"nome_datazione": "Età Classica", "fascia_cronologica": "V-IV sec. a.C."},
            {"nome_datazione": "Età Ellenistica", "fascia_cronologica": "IV-I sec. a.C."},
            {"nome_datazione": "Età Repubblicana", "fascia_cronologica": "509-27 a.C."},
            {"nome_datazione": "Età Augustea", "fascia_cronologica": "27 a.C.-14 d.C."},
            {"nome_datazione": "Età Giulio-Claudia", "fascia_cronologica": "14-68 d.C."},
            {"nome_datazione": "Età Flavia", "fascia_cronologica": "69-96 d.C."},
            {"nome_datazione": "Età Antonina", "fascia_cronologica": "96-192 d.C."},
            {"nome_datazione": "Età dei Severi", "fascia_cronologica": "193-235 d.C."},
            {"nome_datazione": "Crisi del III secolo", "fascia_cronologica": "235-284 d.C."},
            {"nome_datazione": "Tarda Età Imperiale", "fascia_cronologica": "284-476 d.C."},

            # Medioevo
            {"nome_datazione": "Alto Medioevo", "fascia_cronologica": "V-X secolo"},
            {"nome_datazione": "Basso Medioevo", "fascia_cronologica": "XI-XV secolo"},
            {"nome_datazione": "Età Longobarda", "fascia_cronologica": "568-774 d.C."},
            {"nome_datazione": "Età Carolingia", "fascia_cronologica": "774-888 d.C."},
            {"nome_datazione": "Età Comunale", "fascia_cronologica": "XI-XIII secolo"},

            # Età Moderna e Contemporanea
            {"nome_datazione": "Rinascimento", "fascia_cronologica": "XV-XVI secolo"},
            {"nome_datazione": "Età Moderna", "fascia_cronologica": "XVI-XVIII secolo"},
            {"nome_datazione": "Età Contemporanea", "fascia_cronologica": "XIX-XXI secolo"},

            # Generiche
            {"nome_datazione": "Non datato", "fascia_cronologica": ""},
            {"nome_datazione": "Generico", "fascia_cronologica": ""},
        ]

        created_count = 0
        for dat_data in default_datazioni:
            try:
                # Check if already exists
                existing = self.get_datazione_by_nome(dat_data['nome_datazione'])
                if not existing:
                    self.create_datazione(dat_data)
                    created_count += 1
            except Exception as e:
                print(f"Warning: Failed to create datazione '{dat_data['nome_datazione']}': {e}")
                continue

        return created_count
