"""
Site service - Business logic for site management
"""

from typing import List, Dict, Any, Optional
from ..database.manager import DatabaseManager
from ..models.site import Site
from ..dto.site_dto import SiteDTO
from ..utils.validators import validate_data
from ..utils.exceptions import ValidationError, RecordNotFoundError, DuplicateRecordError

class SiteService:
    """Service class for site operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_site(self, site_data: Dict[str, Any]) -> Site:
        """Create a new site"""
        # Validate data
        validate_data('site', site_data)
        
        # Check for duplicate site name
        existing_site = self.db_manager.get_by_field(Site, 'sito', site_data['sito'])
        if existing_site:
            raise DuplicateRecordError(f"Site '{site_data['sito']}' already exists")
        
        # Create site
        return self.db_manager.create(Site, site_data)
    
    def create_site_dto(self, site_data: Dict[str, Any]) -> SiteDTO:
        """Create a new site and return as DTO"""
        try:
            with self.db_manager.connection.get_session() as session:
                # Validate data
                validate_data('site', site_data)
                
                # Check for duplicate site name
                existing_site = session.query(Site).filter(Site.sito == site_data['sito']).first()
                if existing_site:
                    raise DuplicateRecordError(f"Site '{site_data['sito']}' already exists")
                
                # Create site
                site = Site(**site_data)
                session.add(site)
                session.flush()  # Get the ID
                session.refresh(site)  # Refresh to get all data
                
                # Convert to DTO while still in session
                return SiteDTO.from_model(site)
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to create Site: {e}")
    
    def get_site_by_id(self, site_id: int) -> Optional[Site]:
        """Get site by ID"""
        return self.db_manager.get_by_id(Site, site_id)
    
    def get_site_dto_by_id(self, site_id: int) -> Optional[SiteDTO]:
        """Get site by ID as DTO"""
        try:
            with self.db_manager.connection.get_session() as session:
                site = session.query(Site).filter(Site.id_sito == site_id).first()
                if site:
                    return SiteDTO.from_model(site)
                return None
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get Site by ID {site_id}: {e}")
    
    def get_site_by_name(self, site_name: str) -> Optional[Site]:
        """Get site by name"""
        return self.db_manager.get_by_field(Site, 'sito', site_name)
    
    def get_all_sites(self, page: int = 1, size: int = 10, 
                     filters: Optional[Dict[str, Any]] = None) -> List[SiteDTO]:
        """Get all sites with pagination and filtering - returns DTOs"""
        try:
            from sqlalchemy import asc, desc
            with self.db_manager.connection.get_session() as session:
                query = session.query(Site)
                
                # Apply filters
                if filters:
                    for key, value in filters.items():
                        if hasattr(Site, key):
                            query = query.filter(getattr(Site, key) == value)
                
                # Apply ordering
                query = query.order_by(asc(Site.sito))
                
                # Apply pagination
                offset = (page - 1) * size
                sites = query.offset(offset).limit(size).all()
                
                # Convert to DTOs while still in session
                return [SiteDTO.from_model(site) for site in sites]
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get Site records: {e}")
    
    def update_site(self, site_id: int, update_data: Dict[str, Any]) -> Site:
        """Update existing site"""
        # For updates, we don't need full validation (only check specific business rules)
        # Skip validate_data() for updates as it requires all mandatory fields
        
        # Check if site name is being changed and if new name already exists
        if 'sito' in update_data:
            existing_site = self.db_manager.get_by_field(Site, 'sito', update_data['sito'])
            if existing_site and existing_site.id_sito != site_id:
                raise DuplicateRecordError(f"Site '{update_data['sito']}' already exists")
        
        # Update site
        return self.db_manager.update(Site, site_id, update_data)
    
    def update_site_dto(self, site_id: int, update_data: Dict[str, Any]) -> Optional[SiteDTO]:
        """Update existing site and return DTO"""
        try:
            self.update_site(site_id, update_data)
            return self.get_site_dto_by_id(site_id)
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to update Site: {e}")
    
    def delete_site(self, site_id: int) -> Dict[str, int]:
        """
        Delete site and all related records (cascade deletion)

        Args:
            site_id: ID of the site to delete

        Returns:
            Dictionary with counts of deleted records by table

        Raises:
            RecordNotFoundError: If site does not exist
        """
        # Track deletion counts
        deletion_stats = {
            'us_relationships': 0,
            'periodizzazione': 0,
            'inventario': 0,
            'us': 0,
            'site': 0
        }

        try:
            with self.db_manager.connection.get_session() as session:
                from ..models.us import US
                from ..models.inventario_materiali import InventarioMateriali
                from ..models.harris_matrix import USRelationships, Periodizzazione

                # Get site within the session
                site = session.query(Site).filter(Site.id_sito == site_id).first()
                if not site:
                    raise RecordNotFoundError(f"Site with ID {site_id} not found")

                site_name = site.sito

                # Delete in order to respect foreign key constraints:
                # 1. US Relationships (references US)
                relationships = session.query(USRelationships).filter(
                    USRelationships.sito == site_name
                ).all()
                for rel in relationships:
                    session.delete(rel)
                    deletion_stats['us_relationships'] += 1

                # 2. Periodizzazione (references US and Site)
                periodizzazioni = session.query(Periodizzazione).filter(
                    Periodizzazione.sito == site_name
                ).all()
                for per in periodizzazioni:
                    session.delete(per)
                    deletion_stats['periodizzazione'] += 1

                # 3. Inventario Materiali (references Site and US)
                inventario = session.query(InventarioMateriali).filter(
                    InventarioMateriali.sito == site_name
                ).all()
                for inv in inventario:
                    session.delete(inv)
                    deletion_stats['inventario'] += 1

                # 4. US (references Site)
                us_records = session.query(US).filter(US.sito == site_name).all()
                for us in us_records:
                    session.delete(us)
                    deletion_stats['us'] += 1

                # 5. Finally, delete the site itself
                session.delete(site)
                deletion_stats['site'] = 1

                # Commit the transaction
                session.commit()

                return deletion_stats

        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to delete site and related records: {e}")
    
    def count_sites(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count sites with optional filters"""
        return self.db_manager.count(Site, filters)
    
    def search_sites(self, search_term: str, page: int = 1, size: int = 10,
                    filters: Optional[Dict[str, Any]] = None) -> List[SiteDTO]:
        """Search sites by term - returns DTOs"""
        try:
            from sqlalchemy import asc, desc, or_
            with self.db_manager.connection.get_session() as session:
                query = session.query(Site)
                
                # Apply search filters
                if search_term:
                    search_filter = or_(
                        Site.sito.contains(search_term),
                        Site.comune.contains(search_term),
                        Site.provincia.contains(search_term),
                        Site.regione.contains(search_term),
                        Site.descrizione.contains(search_term)
                    )
                    query = query.filter(search_filter)
                
                # Apply additional filters
                if filters:
                    for key, value in filters.items():
                        if hasattr(Site, key):
                            query = query.filter(getattr(Site, key) == value)
                
                # Apply ordering
                query = query.order_by(asc(Site.sito))
                
                # Apply pagination
                offset = (page - 1) * size
                sites = query.offset(offset).limit(size).all()
                
                # Convert to DTOs while still in session
                return [SiteDTO.from_model(site) for site in sites]
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to search Site records: {e}")
    
    def get_unique_countries(self) -> List[str]:
        """Get list of unique countries"""
        # This would need a custom query
        # For now, implement with raw query
        query = "SELECT DISTINCT nazione FROM site_table WHERE nazione IS NOT NULL ORDER BY nazione"
        results = self.db_manager.execute_raw_query(query)
        return [row[0] for row in results if row[0]]
    
    def get_unique_regions(self, nazione: Optional[str] = None) -> List[str]:
        """Get list of unique regions, optionally filtered by country"""
        if nazione:
            query = "SELECT DISTINCT regione FROM site_table WHERE regione IS NOT NULL AND nazione = :nazione ORDER BY regione"
            results = self.db_manager.execute_raw_query(query, {'nazione': nazione})
        else:
            query = "SELECT DISTINCT regione FROM site_table WHERE regione IS NOT NULL ORDER BY regione"
            results = self.db_manager.execute_raw_query(query)
        return [row[0] for row in results if row[0]]
    
    def get_unique_municipalities(self, nazione: Optional[str] = None, 
                                 regione: Optional[str] = None) -> List[str]:
        """Get list of unique municipalities with optional filters"""
        conditions = []
        params = {}
        
        if nazione:
            conditions.append("nazione = :nazione")
            params['nazione'] = nazione
        if regione:
            conditions.append("regione = :regione")
            params['regione'] = regione
        
        where_clause = "WHERE comune IS NOT NULL"
        if conditions:
            where_clause += " AND " + " AND ".join(conditions)
        
        query = f"SELECT DISTINCT comune FROM site_table {where_clause} ORDER BY comune"
        results = self.db_manager.execute_raw_query(query, params)
        return [row[0] for row in results if row[0]]
    
    def get_site_statistics(self, site_id: int) -> Dict[str, Any]:
        """Get statistics for a site"""
        site = self.get_site_by_id(site_id)
        if not site:
            raise RecordNotFoundError(f"Site with ID {site_id} not found")
        
        # Get counts of related records
        # Note: These would need proper foreign key relationships
        us_count_query = "SELECT COUNT(*) FROM us_table WHERE sito = :sito"
        inv_count_query = "SELECT COUNT(*) FROM inventario_materiali_table WHERE sito = :sito"
        
        us_count = self.db_manager.execute_raw_query(us_count_query, {'sito': site.sito})[0][0]
        inv_count = self.db_manager.execute_raw_query(inv_count_query, {'sito': site.sito})[0][0]
        
        return {
            'site_id': site_id,
            'site_name': site.sito,
            'us_count': us_count,
            'inventory_count': inv_count,
            'location': f"{site.comune}, {site.provincia}" if site.comune and site.provincia else None
        }
    
    def get_all_sites_dto(self, page: int = 1, size: int = 10) -> List[SiteDTO]:
        """Get all sites as DTOs with pagination"""
        try:
            with self.db_manager.connection.get_session() as session:
                offset = (page - 1) * size
                sites = session.query(Site).offset(offset).limit(size).all()
                # Convert to DTOs while still in session
                return [SiteDTO.from_model(site) for site in sites]
        except Exception as e:
            from ..exceptions import DatabaseError
            raise DatabaseError(f"Failed to get sites as DTOs: {e}")
    
    def count_sites(self) -> int:
        """Count total number of sites"""
        try:
            return self.db_manager.count(Site)
        except Exception as e:
            from ..exceptions import DatabaseError
            raise DatabaseError(f"Failed to count sites: {e}")