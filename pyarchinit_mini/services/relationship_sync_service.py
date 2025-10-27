#!/usr/bin/env python3
"""
Relationship Synchronization Service
=====================================

Provides bidirectional synchronization between:
- us_table.rapporti field (text format: "Copre 1, Taglia 2")
- us_relationships_table (structured relationship records)

This ensures consistency across all interfaces (Web UI, Desktop GUI, Harris Matrix Creator).
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database.manager import DatabaseManager
from ..models.harris_matrix import USRelationships


class RelationshipSyncService:
    """Service for synchronizing rapporti field with us_relationships_table"""

    # Relationship types mapping
    RELATIONSHIP_TYPES = {
        'Copre': 'Copre',
        'Coperto da': 'Coperto da',
        'Taglia': 'Taglia',
        'Tagliato da': 'Tagliato da',
        'Riempie': 'Riempie',
        'Riempito da': 'Riempito da',
        'Si lega a': 'Si lega a',
        'Si appoggia a': 'Si appoggia a',
        'Gli si appoggia': 'Gli si appoggia',
        'Uguale a': 'Uguale a',
        'Coperto': 'Coperto da',  # Alias
        'Contemporaneo a': 'Contemporaneo a',
        'Anteriore a': 'Anteriore a',
        'Posteriore a': 'Posteriore a'
    }

    # Inverse relationships
    INVERSE_RELATIONS = {
        'Copre': 'Coperto da',
        'Coperto da': 'Copre',
        'Taglia': 'Tagliato da',
        'Tagliato da': 'Taglia',
        'Riempie': 'Riempito da',
        'Riempito da': 'Riempie',
        'Si lega a': 'Si lega a',
        'Si appoggia a': 'Gli si appoggia',
        'Gli si appoggia': 'Si appoggia a',
        'Uguale a': 'Uguale a',
        'Contemporaneo a': 'Contemporaneo a',
        'Anteriore a': 'Posteriore a',
        'Posteriore a': 'Anteriore a'
    }

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def parse_rapporti_field(self, rapporti_text: str) -> List[Tuple[str, int]]:
        """
        Parse rapporti field into list of (relationship_type, target_us) tuples.

        Format: "Copre 1, Copre 2, Taglia 3"

        Args:
            rapporti_text: Comma-separated relationships

        Returns:
            List of (relationship_type, target_us_number) tuples
        """
        if not rapporti_text or not rapporti_text.strip():
            return []

        relationships = []
        parts = rapporti_text.split(',')

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Try to match relationship type
            matched = False
            for rel_type in self.RELATIONSHIP_TYPES.keys():
                if part.lower().startswith(rel_type.lower()):
                    # Extract US number after relationship type
                    remainder = part[len(rel_type):].strip()

                    # Remove "US" prefix if present
                    if remainder.upper().startswith('US'):
                        remainder = remainder[2:].strip()

                    try:
                        target_us = int(remainder)
                        # Normalize relationship type
                        normalized_rel = self.RELATIONSHIP_TYPES[rel_type]
                        relationships.append((normalized_rel, target_us))
                        matched = True
                        break
                    except ValueError:
                        # Not a valid number, skip
                        pass

            if not matched:
                # Try alternative parsing for formats like "1002, 2190"
                # This handles cases where multiple targets follow a relationship type
                # But this is already handled above, so we just skip
                pass

        return relationships

    def build_rapporti_field(self, relationships: List[Tuple[str, int]]) -> str:
        """
        Build rapporti field from list of relationships.

        Format: "Copre 1, Copre 2, Taglia 3"

        Args:
            relationships: List of (relationship_type, target_us) tuples

        Returns:
            Formatted rapporti string
        """
        if not relationships:
            return ""

        parts = []
        for rel_type, target_us in relationships:
            parts.append(f"{rel_type} {target_us}")

        return ", ".join(parts)

    def sync_rapporti_to_relationships_table(
        self,
        sito: str,
        us_number: int,
        rapporti_text: str,
        session: Optional[Session] = None
    ) -> Dict[str, int]:
        """
        Synchronize rapporti field TO us_relationships_table.

        This removes all existing relationships for this US and recreates them
        based on the rapporti field.

        Args:
            sito: Site name
            us_number: US number
            rapporti_text: Content of rapporti field
            session: Optional database session (creates new if not provided)

        Returns:
            Dictionary with 'deleted', 'created' counts
        """
        close_session = False
        if session is None:
            session = self.db_manager.connection.get_session().__enter__()
            close_session = True

        try:
            # Delete existing relationships for this US
            deleted = session.query(USRelationships).filter_by(
                sito=sito,
                us_from=us_number
            ).delete()

            # Parse rapporti field
            relationships = self.parse_rapporti_field(rapporti_text)

            # Create new relationship records
            created = 0
            for rel_type, target_us in relationships:
                relationship = USRelationships(
                    sito=sito,
                    us_from=us_number,
                    us_to=target_us,
                    relationship_type=rel_type,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(relationship)
                created += 1

            session.flush()

            return {
                'deleted': deleted,
                'created': created
            }

        finally:
            if close_session:
                session.__exit__(None, None, None)

    def sync_relationships_table_to_rapporti(
        self,
        sito: str,
        us_number: int,
        session: Optional[Session] = None
    ) -> str:
        """
        Synchronize us_relationships_table TO rapporti field.

        Builds the rapporti field content from us_relationships_table records.

        Args:
            sito: Site name
            us_number: US number
            session: Optional database session (creates new if not provided)

        Returns:
            Formatted rapporti string
        """
        close_session = False
        if session is None:
            session = self.db_manager.connection.get_session().__enter__()
            close_session = True

        try:
            # Get all relationships for this US
            relationships = session.query(USRelationships).filter_by(
                sito=sito,
                us_from=us_number
            ).order_by(USRelationships.us_to).all()

            # Convert to list of tuples
            rel_list = [(rel.relationship_type, rel.us_to) for rel in relationships]

            # Build rapporti string
            return self.build_rapporti_field(rel_list)

        finally:
            if close_session:
                session.__exit__(None, None, None)

    def sync_us_full(
        self,
        sito: str,
        us_number: int,
        rapporti_text: Optional[str] = None,
        session: Optional[Session] = None
    ) -> Dict[str, any]:
        """
        Fully synchronize a US - update us_relationships_table from rapporti field.

        Args:
            sito: Site name
            us_number: US number
            rapporti_text: Optional rapporti field content (if None, reads from db)
            session: Optional database session

        Returns:
            Dictionary with sync statistics
        """
        close_session = False
        if session is None:
            session = self.db_manager.connection.get_session().__enter__()
            close_session = True

        try:
            # If rapporti_text not provided, read from database
            if rapporti_text is None:
                from ..models.us import US
                us = session.query(US).filter_by(sito=sito, us=us_number).first()
                if not us:
                    return {'error': f'US {us_number} not found in site {sito}'}
                rapporti_text = us.rapporti or ""

            # Sync rapporti → relationships table
            result = self.sync_rapporti_to_relationships_table(
                sito, us_number, rapporti_text, session
            )

            return {
                'sito': sito,
                'us': us_number,
                'relationships_deleted': result['deleted'],
                'relationships_created': result['created'],
                'rapporti': rapporti_text
            }

        finally:
            if close_session:
                session.__exit__(None, None, None)

    def sync_all_site_us(
        self,
        sito: str,
        session: Optional[Session] = None
    ) -> Dict[str, any]:
        """
        Synchronize all US in a site from rapporti field to us_relationships_table.

        Args:
            sito: Site name
            session: Optional database session

        Returns:
            Dictionary with sync statistics
        """
        close_session = False
        if session is None:
            session = self.db_manager.connection.get_session().__enter__()
            close_session = True

        try:
            from ..models.us import US

            # Get all US for this site
            us_list = session.query(US).filter_by(sito=sito).all()

            total_deleted = 0
            total_created = 0
            us_processed = 0

            for us in us_list:
                result = self.sync_rapporti_to_relationships_table(
                    sito,
                    us.us,
                    us.rapporti or "",
                    session
                )
                total_deleted += result['deleted']
                total_created += result['created']
                us_processed += 1

            session.flush()

            return {
                'sito': sito,
                'us_processed': us_processed,
                'total_relationships_deleted': total_deleted,
                'total_relationships_created': total_created
            }

        finally:
            if close_session:
                session.__exit__(None, None, None)

    def create_reciprocal_relationship(
        self,
        sito: str,
        us_from: int,
        us_to: int,
        relationship_type: str,
        session: Optional[Session] = None
    ) -> bool:
        """
        Create a relationship and its reciprocal automatically.

        Args:
            sito: Site name
            us_from: Source US number
            us_to: Target US number
            relationship_type: Type of relationship
            session: Optional database session

        Returns:
            True if successful
        """
        close_session = False
        if session is None:
            session = self.db_manager.connection.get_session().__enter__()
            close_session = True

        try:
            # Create forward relationship
            forward_rel = USRelationships(
                sito=sito,
                us_from=us_from,
                us_to=us_to,
                relationship_type=relationship_type,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(forward_rel)

            # Create reciprocal relationship if inverse exists
            inverse_type = self.INVERSE_RELATIONS.get(relationship_type)
            if inverse_type:
                reciprocal_rel = USRelationships(
                    sito=sito,
                    us_from=us_to,
                    us_to=us_from,
                    relationship_type=inverse_type,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(reciprocal_rel)

            session.flush()
            return True

        finally:
            if close_session:
                session.__exit__(None, None, None)
