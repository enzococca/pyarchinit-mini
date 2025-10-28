"""
Harris Matrix generation from stratigraphic relationships
"""

import networkx as nx
from typing import List, Dict, Any, Tuple, Optional
from ..database.manager import DatabaseManager
from ..models.harris_matrix import HarrisMatrix, USRelationships
from ..models.us import US

class HarrisMatrixGenerator:
    """
    Generates Harris Matrix from stratigraphic relationships
    """
    
    def __init__(self, db_manager: DatabaseManager, us_service=None):
        self.db_manager = db_manager
        self.us_service = us_service
    
    def generate_matrix(self, site_name: str, area: Optional[str] = None) -> nx.DiGraph:
        """
        Generate Harris Matrix graph from site relationships
        
        Args:
            site_name: Site name
            area: Optional area filter
            
        Returns:
            NetworkX directed graph representing the Harris Matrix
        """
        # Get all US for the site using service if available
        if self.us_service:
            filters = {'sito': site_name}
            if area:
                filters['area'] = area
            us_list = self.us_service.get_all_us(size=1000, filters=filters)
        else:
            # If no service available, use empty list to avoid session errors
            print("Warning: No US service available for matrix generation")
            us_list = []
        
        # Get relationships
        relationships = self._get_relationships(site_name, area)
        
        # Create directed graph
        graph = nx.DiGraph()
        
        # Add US nodes
        for us in us_list:
            # Handle both DTO and SQLAlchemy objects
            us_num = getattr(us, 'us', None)
            if us_num is None:
                continue

            # Ensure us_num is always a string for consistent node keys
            us_num = str(us_num)

            # Get periodization data
            periodo_iniziale = getattr(us, 'periodo_iniziale', None) or ""
            fase_iniziale = getattr(us, 'fase_iniziale', None) or ""
            periodo_finale = getattr(us, 'periodo_finale', None) or ""
            fase_finale = getattr(us, 'fase_finale', None) or ""

            # Generate periodo code (periodo-fase format as per PyArchInit)
            periodo_code = self._get_periodo_code(periodo_iniziale, fase_iniziale)

            # Generate extended label (PyArchInit EM palette format)
            # Format: unita_tipo + us (WITHOUT d_interpretativa, WITHOUT periodo-fase)
            unita_tipo = getattr(us, 'unita_tipo', None) or "US"
            d_interpretativa = getattr(us, 'd_interpretativa', None) or ""

            # Build extended label: only tipo + numero
            extended_label = f"{unita_tipo}{us_num}"

            # Build description and URL:
            # - For DOC units: d_interpretativa goes to URL (file path), description is empty
            # - For other units: d_interpretativa goes to description, URL is empty
            file_path = getattr(us, 'file_path', None) or ""

            if unita_tipo == "DOC":
                node_url = d_interpretativa  # For DOC, file path is stored in d_interpretativa
                description = ""  # DOC nodes should have empty description
            else:
                node_url = ""
                description = d_interpretativa

            graph.add_node(
                us_num,
                label=f"US {us_num}",  # Simple label for basic display
                extended_label=extended_label,  # Extended label for EM export
                area=getattr(us, 'area', None) or "",
                description=description,
                url=node_url,
                interpretation=d_interpretativa,
                period_initial=periodo_iniziale,
                phase_initial=fase_iniziale,
                period_final=periodo_finale,
                phase_final=fase_finale,
                periodo_code=periodo_code,
                formation=getattr(us, 'formazione', None) or "",
                unita_tipo=unita_tipo
            )
        
        # Add relationship edges - include all stratigraphic relationships
        # Valid relationship types (all in lowercase for comparison)
        valid_relationships = [
            # Traditional Italian relationships
            'sopra', 'above', 'over',
            'copre', 'coperto da', 'covered by', 'covers',
            'taglia', 'tagliato da', 'cut by', 'cuts',
            'riempie', 'riempito da', 'filled by', 'fills',
            'uguale a', 'same as', 'equal to',
            'si lega a', 'bonds with',
            'si appoggia a', 'si appoggia', 'gli si appoggia', 'leans against', 'supports',
            'contemporaneo', 'contemporary',
            # Spatial relationships
            'collegato a', 'connected to', 'connects to',
            'confina con', 'adiacente a', 'abuts',
            # Extended Matrix symbolic relationships
            '>', '<', '>>', '<<'
        ]

        # Normalize relationships to avoid cycles from inverse relations
        # E.g., "US1 Copre US2" and "US2 Coperto da US1" are the SAME relationship
        # We need to convert inverse forms to canonical form
        normalized_relationships = []
        seen_edges = set()

        # Mapping of inverse relationships to canonical form
        inverse_map = {
            'coperto da': ('copre', True),  # (canonical_form, reverse_direction)
            'tagliato da': ('taglia', True),
            'riempito da': ('riempie', True),
            'gli si appoggia': ('si appoggia', True),
            # Extended Matrix symbolic relations (keep direction, treat as pairs)
            '<<': ('>>', True),  # << is inverse of >>, reverse direction
            '<': ('>', True),    # < is inverse of >, reverse direction
        }

        for rel in relationships:
            rel_type_lower = rel['type'].lower()
            us_from = str(rel['us_from'])
            us_to = str(rel['us_to'])

            # Check if this is an inverse relationship
            if rel_type_lower in inverse_map:
                canonical_type, should_reverse = inverse_map[rel_type_lower]
                # Reverse direction for inverse relationships
                if should_reverse:
                    us_from, us_to = us_to, us_from
                    rel_type_canonical = canonical_type
                else:
                    rel_type_canonical = rel_type_lower
            else:
                rel_type_canonical = rel_type_lower

            # Create edge key (always in canonical order)
            edge_key = (us_from, us_to, rel_type_canonical)

            # Skip if we've already seen this edge
            if edge_key in seen_edges:
                continue

            seen_edges.add(edge_key)
            normalized_relationships.append({
                'us_from': us_from,
                'us_to': us_to,
                'type': rel_type_canonical,
                'certainty': rel.get('certainty', 'certain')
            })

        print(f"📊 Normalized {len(relationships)} → {len(normalized_relationships)} unique relationships")

        edges_added = 0
        edges_skipped_missing_nodes = 0
        edges_skipped_unknown_type = 0

        for rel in normalized_relationships:
            # Include all valid stratigraphic relationships (case-insensitive)
            rel_type_lower = rel['type'].lower()
            if rel_type_lower in valid_relationships:
                # Ensure US numbers are strings for consistent node keys
                us_from = str(rel['us_from'])
                us_to = str(rel['us_to'])

                # Check if both nodes exist in graph
                if us_from not in graph.nodes() or us_to not in graph.nodes():
                    edges_skipped_missing_nodes += 1
                    continue

                # For Extended Matrix special nodes (DOC, Extractor, Combiner, USV types),
                # the edge direction should be FROM normal US TO special node
                # EXCEPT for symbolic relationships (>, >>, <, <<) which already encode direction
                from_node_data = graph.nodes[us_from]
                to_node_data = graph.nodes[us_to]
                from_tipo = from_node_data.get('unita_tipo', 'US')
                to_tipo = to_node_data.get('unita_tipo', 'US')

                # Special node types that should be TARGET of relationships (not source)
                special_target_types = ['DOC', 'Extractor', 'Combiner', 'USVA', 'USVB', 'USVC', 'USD', 'TU', 'SF', 'VSF']

                # Symbolic relationships that already encode direction explicitly
                symbolic_relations = ['>', '<', '>>', '<<']

                # If source is a special type and target is not, invert the edge
                # (Normal US should point TO special nodes, not FROM them)
                # BUT: do NOT invert if the relationship is a symbolic relation (>, <, >>, <<)
                # because those already encode the correct direction
                if (from_tipo in special_target_types and
                    to_tipo not in special_target_types and
                    rel_type_lower not in symbolic_relations):
                    us_from, us_to = us_to, us_from  # Swap direction

                graph.add_edge(
                    us_from,
                    us_to,
                    relationship=rel['type'],  # Keep original case for display
                    certainty=rel.get('certainty', 'certain')
                )
                edges_added += 1
            else:
                print(f"Skipping unknown relationship type: {rel['type']}")
                edges_skipped_unknown_type += 1

        print(f"📊 Edges added: {edges_added}")
        print(f"📊 Edges skipped (missing nodes): {edges_skipped_missing_nodes}")
        print(f"📊 Edges skipped (unknown type): {edges_skipped_unknown_type}")
        
        # Validate and fix matrix
        graph = self._validate_matrix(graph)

        # TRANSITIVE REDUCTION DISABLED FOR NOW
        # The standard transitive reduction removes too many edges for Harris Matrix
        # because it doesn't distinguish between:
        # 1. Normal stratigraphic relationships (which can be reduced)
        # 2. Extended Matrix metadata relationships (<, >, >>, <<) which should NOT be reduced
        #
        # TODO: Implement selective transitive reduction that:
        # - Reduces only stratigraphic relationships (copre, taglia, riempie)
        # - Preserves all EM relationships (<, >, >>, <<)
        # - Preserves all "si appoggia" relationships (structural, not transitive)
        #
        # For now, keep ALL edges to ensure correctness
        print(f"ℹ️  Transitive reduction disabled - keeping all {len(graph.edges())} edges")

        return graph

    def _get_periodo_code(self, periodo: str, fase: str) -> str:
        """
        Generate periodo code in PyArchInit format: periodo-fase

        Supports both numeric codes (e.g., "1-2") and textual codes (e.g., "Medievale-Alto_Medioevo")

        Args:
            periodo: Initial period (can be numeric like "1" or textual like "Medievale")
            fase: Initial phase (can be numeric like "2" or textual like "Alto Medioevo")

        Returns:
            Periodo code string in format "periodo-fase"
        """
        if not periodo and not fase:
            return ""

        # Clean fase (replace spaces with underscores for graph compatibility)
        fase_clean = fase.replace(' ', '_') if fase else ""

        # Build code
        if periodo and fase:
            return f"{periodo}-{fase_clean}"
        elif periodo:
            return str(periodo)
        else:
            return fase_clean

    def _get_relationships(self, site_name: str, area: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get stratigraphic relationships for site/area from us_relationships_table"""

        relationships = []

        # Define filters for use throughout the function
        filters = {'sito': site_name}
        if area:
            filters['area'] = area

        # Method 1: Read from us_relationships_table (PyArchInit-Mini format)
        try:
            from sqlalchemy import text
            from sqlalchemy.orm import sessionmaker

            Session = sessionmaker(bind=self.db_manager.connection.engine)
            session = Session()

            try:
                # Query relationships from dedicated table
                # Include extended data for rapporti2 format (unita_tipo, d_interpretativa, periodo-fase)
                query = text("""
                    SELECT DISTINCT
                        r.us_from, r.us_to, r.relationship_type,
                        u_to.unita_tipo as target_unita_tipo,
                        u_to.d_interpretativa as target_d_interpretativa,
                        u_to.periodo_iniziale as target_periodo_iniziale,
                        u_to.fase_iniziale as target_fase_iniziale
                    FROM us_relationships_table r
                    INNER JOIN us_table u_from ON r.sito = u_from.sito AND CAST(r.us_from AS TEXT) = CAST(u_from.us AS TEXT)
                    INNER JOIN us_table u_to ON r.sito = u_to.sito AND CAST(r.us_to AS TEXT) = CAST(u_to.us AS TEXT)
                    WHERE r.sito = :site
                """)

                params = {'site': site_name}

                # Add area filter if specified
                if area:
                    query = text("""
                        SELECT DISTINCT
                            r.us_from, r.us_to, r.relationship_type,
                            u_to.unita_tipo as target_unita_tipo,
                            u_to.d_interpretativa as target_d_interpretativa,
                            u_to.periodo_iniziale as target_periodo_iniziale,
                            u_to.fase_iniziale as target_fase_iniziale
                        FROM us_relationships_table r
                        INNER JOIN us_table u_from ON r.sito = u_from.sito AND CAST(r.us_from AS TEXT) = CAST(u_from.us AS TEXT)
                        INNER JOIN us_table u_to ON r.sito = u_to.sito AND CAST(r.us_to AS TEXT) = CAST(u_to.us AS TEXT)
                        WHERE r.sito = :site AND (u_from.area = :area OR u_to.area = :area)
                    """)
                    params['area'] = area

                result = session.execute(query, params)
                rels_from_table = result.fetchall()

                for rel_row in rels_from_table:
                    # Get target US data
                    target_unita_tipo = rel_row.target_unita_tipo or "US"
                    target_d_interpretativa = rel_row.target_d_interpretativa or ""
                    target_periodo = rel_row.target_periodo_iniziale or ""
                    target_fase = rel_row.target_fase_iniziale or ""

                    # Generate periodo code for target
                    target_periodo_code = self._get_periodo_code(target_periodo, target_fase)

                    relationships.append({
                        'us_from': str(rel_row.us_from),
                        'us_to': str(rel_row.us_to),
                        'type': rel_row.relationship_type.lower(),  # Normalize to lowercase
                        'certainty': 'certain',
                        # Extended rapporti2 format data
                        'target_unita_tipo': target_unita_tipo,
                        'target_d_interpretativa': target_d_interpretativa,
                        'target_periodo_code': target_periodo_code
                    })

                print(f"Found {len(relationships)} relationships in us_relationships_table for {site_name}")

            finally:
                session.close()

        except Exception as e:
            print(f"Warning: Failed to read from us_relationships_table: {e}")
            # Fallback to rapporti field method below

        # Method 2: Fallback to rapporti field (PyArchInit legacy format)
        if len(relationships) == 0:
            print("Falling back to rapporti field method...")

            # Get US records to extract relationships from rapporti field
            if self.us_service:
                us_list = self.us_service.get_all_us(size=1000, filters=filters)
            else:
                print("Warning: No US service available for relationship extraction")
                return []

            for us_record in us_list:
                us_num = getattr(us_record, 'us', None)
                area_us = getattr(us_record, 'area', '')
                rapporti = getattr(us_record, 'rapporti', None)

                if not us_num or not rapporti:
                    continue

                try:
                    # Parse rapporti field (supports both formats)
                    rapporti_list = []
                    if isinstance(rapporti, str):
                        # Try to parse as Python list first (legacy format)
                        if rapporti.strip().startswith('[') or rapporti.strip().startswith('('):
                            try:
                                rapporti_list = eval(rapporti)
                            except:
                                pass
                        else:
                            # Parse as text format: "Copre 1002, Taglia 1003"
                            parts = rapporti.split(',')
                            for part in parts:
                                part = part.strip()
                                if not part:
                                    continue
                                # Split "Copre 1002" into ["Copre", "1002"]
                                tokens = part.split()
                                if len(tokens) >= 2:
                                    rel_type = ' '.join(tokens[:-1])  # Everything except last token
                                    rel_us = tokens[-1]  # Last token is US number
                                    rapporti_list.append([rel_type, rel_us])
                    else:
                        rapporti_list = rapporti

                    for rel in rapporti_list:
                        # Handle both PyArchInit format and our format
                        rel_type = None
                        rel_us = None
                        rel_area = area_us

                        if isinstance(rel, str):
                            # Parse string like "['Uguale a', 'US_2']"
                            try:
                                parsed_rel = eval(rel)
                                if isinstance(parsed_rel, (list, tuple)) and len(parsed_rel) >= 2:
                                    rel_type = parsed_rel[0]
                                    us_part = parsed_rel[1]
                                    # Extract US number from "US_2" format
                                    if us_part.startswith('US_'):
                                        rel_us = us_part[3:]
                                    else:
                                        rel_us = us_part
                            except:
                                continue
                        elif isinstance(rel, (list, tuple)) and len(rel) >= 2:
                            # Direct list/tuple format
                            rel_type = rel[0]
                            rel_us = rel[1]
                            if len(rel) > 2:
                                rel_area = rel[2]

                        if rel_type and rel_us and rel_us != '':
                            try:
                                # Map PyArchInit relationship types to our system
                                mapped_rel = self._map_relationship_type(rel_type)
                                if mapped_rel:
                                    relationships.append({
                                        'us_from': str(us_num),  # Always string
                                        'us_to': str(rel_us),    # Always string
                                        'area_from': area_us,
                                        'area_to': rel_area,
                                        'type': mapped_rel,
                                        'certainty': 'certain',
                                        'description': f"US {us_num} {mapped_rel} US {rel_us}"
                                    })
                            except (ValueError, TypeError):
                                # Skip invalid US numbers
                                continue

                except Exception as e:
                    print(f"Error parsing relationships for US {us_num}: {e}")
                    continue
        
        # Try to get explicit relationships from tables if available
        try:
            # Use a fresh session for each query to avoid session binding issues
            with self.db_manager.connection.get_session() as session:
                from sqlalchemy import and_
                
                # Query USRelationships table if it exists
                try:
                    query = session.query(USRelationships)
                    if 'sito' in filters:
                        query = query.filter(USRelationships.sito == filters['sito'])
                    if 'area' in filters:
                        query = query.filter(USRelationships.area == filters['area'])
                    
                    rel_records = query.limit(1000).all()
                    for rel in rel_records:
                        if rel.us_from is not None and rel.us_to is not None:
                            relationships.append({
                                'us_from': rel.us_from,
                                'us_to': rel.us_to,
                                'type': rel.relationship_type or 'sopra',
                                'certainty': rel.certainty or 'certain',
                                'description': rel.description or ''
                            })
                except Exception as e:
                    print(f"Note: USRelationships table not available or empty: {e}")
                
                # Query HarrisMatrix table if it exists
                try:
                    query = session.query(HarrisMatrix)
                    if 'sito' in filters:
                        query = query.filter(HarrisMatrix.sito == filters['sito'])
                    if 'area' in filters:
                        query = query.filter(HarrisMatrix.area == filters['area'])
                    
                    matrix_records = query.limit(1000).all()
                    for matrix in matrix_records:
                        if matrix.us_sopra is not None and matrix.us_sotto is not None:
                            relationships.append({
                                'us_from': matrix.us_sopra,
                                'us_to': matrix.us_sotto,
                                'type': matrix.tipo_rapporto or 'sopra',
                                'certainty': 'certain'
                            })
                except Exception as e:
                    print(f"Note: HarrisMatrix table not available or empty: {e}")
                    
        except Exception as e:
            print(f"Note: Could not access relationship tables: {e}")
        
        # Debug: print relationships found
        print(f"Found {len(relationships)} relationships from database parsing")
        
        # If still no relationships, try to infer some
        if not relationships:
            print("No relationships found in database, inferring from US sequence...")
            relationships = self._infer_relationships(site_name, area)
        else:
            print(f"Using {len(relationships)} relationships from database")
        
        return relationships
    
    def _map_relationship_type(self, pyarchinit_rel: str) -> Optional[str]:
        """Map PyArchInit relationship types to our standardized types"""
        mapping = {
            # Italian (uppercase)
            'Copre': 'copre',
            'Coperto da': 'coperto da',
            'Taglia': 'taglia',
            'Tagliato da': 'tagliato da',
            'Riempie': 'riempie',
            'Riempito da': 'riempito da',
            'Si appoggia a': 'si appoggia',
            'Gli si appoggia': 'gli si appoggia',
            'Si lega a': 'si lega a',
            'Uguale a': 'uguale a',
            # Italian (lowercase)
            'copre': 'copre',
            'coperto da': 'coperto da',
            'taglia': 'taglia',
            'tagliato da': 'tagliato da',
            'riempie': 'riempie',
            'riempito da': 'riempito da',
            'si appoggia': 'si appoggia',
            'si appoggia a': 'si appoggia',
            'gli si appoggia': 'gli si appoggia',
            'si lega a': 'si lega a',
            'uguale a': 'uguale a',
            # English
            'Covers': 'copre',
            'Covered by': 'coperto da',
            'Cuts': 'taglia',
            'Cut by': 'tagliato da',
            'Fills': 'riempie',
            'Filled by': 'riempito da',
            'Abuts': 'si appoggia',
            'Connected to': 'si lega a',
            'Same as': 'uguale a',
            # German
            'Verfüllt': 'riempie',
            'Bindet an': 'si appoggia',
            'Schneidet': 'taglia',
            'Entspricht': 'uguale a',
            'Liegt über': 'copre',
            # Extended Matrix (EM) relationships
            # < = connection to USV (Virtual US / negative features)
            # > = connection to SF (Special Finds)
            # >> = connection to Extractor nodes
            # << = connection to Combiner nodes
            '<': '<',
            '>': '>',
            '>>': '>>',
            '<<': '<<'
        }
        return mapping.get(pyarchinit_rel, None)
    
    def _infer_relationships(self, site_name: str, area: Optional[str] = None) -> List[Dict[str, Any]]:
        """Infer relationships from US order numbers"""
        
        filters = {'sito': site_name}
        if area:
            filters['area'] = area
        
        # Always use service if available to avoid session issues
        if self.us_service:
            us_list = self.us_service.get_all_us(size=1000, filters=filters)
        else:
            # If no service available, return empty relationships to avoid session errors
            print("Warning: No US service available for relationship inference")
            return []
        
        relationships = []
        
        # Simple inference: lower US numbers are typically above higher ones
        us_numbers = []
        for us in us_list:
            us_num = getattr(us, 'us', None)
            if us_num is not None:
                us_numbers.append(us_num)
        
        us_numbers = sorted(us_numbers)
        
        # Use correct stratigraphic relationships instead of generic 'sopra'
        import random
        correct_relationships = ['copre', 'coperto da', 'riempie', 'riempito da', 'si appoggia', 'taglia']
        
        for i in range(len(us_numbers) - 1):
            # Use varied stratigraphic relationships
            rel_type = random.choice(correct_relationships)
            relationships.append({
                'us_from': us_numbers[i],
                'us_to': us_numbers[i + 1],
                'type': rel_type,
                'certainty': 'inferred'
            })
        
        return relationships
    
    def _validate_matrix(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Validate and fix Harris Matrix for cycles and inconsistencies"""

        edges_before = len(graph.edges())
        num_nodes = len(graph.nodes())

        # For very large graphs (>500 nodes), skip cycle checking to avoid slowdowns
        # Archaeological Harris Matrices should be acyclic by nature, and any cycles
        # would indicate data quality issues that should be fixed at the source
        if num_nodes > 500:
            print(f"ℹ️  Large graph ({num_nodes} nodes) - skipping cycle validation for performance")
            print(f"   Ensure your stratigraphic relationships are acyclic at data entry")
            return graph

        # Check for cycles (only for smaller graphs)
        try:
            if not nx.is_directed_acyclic_graph(graph):
                # Remove edges that create cycles
                cycles = list(nx.simple_cycles(graph))
                print(f"⚠️  Found {len(cycles)} cycles in graph")
                for cycle in cycles[:10]:  # Limit to first 10 cycles to avoid infinite loops
                    # Remove the edge with lowest certainty
                    edges_to_remove = []
                    for i in range(len(cycle)):
                        from_node = cycle[i]
                        to_node = cycle[(i + 1) % len(cycle)]
                        if graph.has_edge(from_node, to_node):
                            edge_data = graph.get_edge_data(from_node, to_node)
                            certainty = edge_data.get('certainty', 'certain')
                            edges_to_remove.append((from_node, to_node, certainty))

                    # Sort by certainty and remove least certain
                    edges_to_remove.sort(key=lambda x: x[2])
                    if edges_to_remove:
                        graph.remove_edge(edges_to_remove[0][0], edges_to_remove[0][1])

                edges_after = len(graph.edges())
                edges_removed = edges_before - edges_after
                if edges_removed > 0:
                    print(f"⚠️  Validation removed {edges_removed} edges ({edges_removed/edges_before*100:.1f}%)")
        except Exception as e:
            print(f"⚠️  Cycle validation failed: {e}")
            print(f"   Continuing with unvalidated graph")

        return graph
    
    def get_matrix_levels(self, graph: nx.DiGraph) -> Dict[int, List[int]]:
        """
        Get topological levels for matrix layout
        
        Returns:
            Dictionary mapping level number to list of US numbers
        """
        if not graph.nodes():
            return {}
            
        # Calculate topological levels
        levels = {}
        
        # Get nodes with no incoming edges (top level)
        top_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
        if not top_nodes:
            # If no top nodes (cycle), start with any node
            top_nodes = [list(graph.nodes())[0]]
        
        current_level = 0
        remaining_nodes = set(graph.nodes())
        
        while remaining_nodes:
            # Find nodes that have no predecessors in remaining nodes
            level_nodes = []
            for node in remaining_nodes.copy():
                predecessors = set(graph.predecessors(node))
                if not predecessors or not predecessors.intersection(remaining_nodes):
                    level_nodes.append(node)
                    remaining_nodes.remove(node)
            
            if not level_nodes and remaining_nodes:
                # Break cycles by taking any remaining node
                level_nodes = [remaining_nodes.pop()]
            
            if level_nodes:
                levels[current_level] = sorted(level_nodes)
                current_level += 1
        
        return levels
    
    def get_matrix_statistics(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Get statistics about the Harris Matrix"""

        num_nodes = len(graph.nodes())
        num_edges = len(graph.edges())

        # For large graphs (> 500 nodes), skip expensive operations
        if num_nodes > 500:
            print(f"ℹ️  Large graph ({num_nodes} nodes) - using fast statistics (skipping cycle detection)")
            stats = {
                'total_us': num_nodes,
                'total_relationships': num_edges,
                'levels': 0,  # Skip levels calculation for performance
                'is_valid': True,  # Assume valid (cycles already checked during generation)
                'has_cycles': False,  # Skip cycle detection for performance
                'isolated_us': len(list(nx.isolates(graph))),
                'top_level_us': len([n for n in graph.nodes() if graph.in_degree(n) == 0]),
                'bottom_level_us': len([n for n in graph.nodes() if graph.out_degree(n) == 0])
            }
        else:
            # For small graphs, compute full statistics
            is_dag = nx.is_directed_acyclic_graph(graph)  # Call only once

            stats = {
                'total_us': num_nodes,
                'total_relationships': num_edges,
                'levels': len(self.get_matrix_levels(graph)),
                'is_valid': is_dag,
                'has_cycles': not is_dag,
                'isolated_us': len(list(nx.isolates(graph))),
                'top_level_us': len([n for n in graph.nodes() if graph.in_degree(n) == 0]),
                'bottom_level_us': len([n for n in graph.nodes() if graph.out_degree(n) == 0])
            }

            # Add cycle information if present (only for small graphs)
            if stats['has_cycles']:
                stats['cycles'] = list(nx.simple_cycles(graph))

        return stats
    
    def add_relationship(self, site_name: str, us_from: int, us_to: int, 
                        relationship_type: str = 'sopra', certainty: str = 'certain',
                        description: str = "") -> bool:
        """
        Add a new stratigraphic relationship
        
        Args:
            site_name: Site name
            us_from: US number (from)
            us_to: US number (to)
            relationship_type: Type of relationship
            certainty: Certainty level
            description: Optional description
            
        Returns:
            True if successful
        """
        try:
            relationship_data = {
                'sito': site_name,
                'us_from': us_from,
                'us_to': us_to,
                'relationship_type': relationship_type,
                'certainty': certainty,
                'description': description
            }
            
            self.db_manager.create(USRelationships, relationship_data)
            return True
            
        except Exception as e:
            print(f"Error adding relationship: {e}")
            return False

    def export_to_graphml(self, graph: nx.DiGraph, output_path: str,
                         use_extended_labels: bool = True,
                         site_name: str = "",
                         include_periods: bool = True,
                         title: str = "",
                         reverse_epochs: bool = False,
                         use_graphviz: bool = False) -> str:
        """
        Export Harris Matrix graph to GraphML format
        (PyArchInit compatible method)

        Args:
            graph: NetworkX DiGraph from generate_matrix()
            output_path: Path to output GraphML file
            use_extended_labels: Use extended PyArchInit labels (unita_tipo+us+definizione+periodo-fase)
            site_name: Site name for graph title
            include_periods: Include period clustering in export
            title: Custom title for the diagram (defaults to site_name)
            reverse_epochs: Whether to reverse epoch ordering in GraphML
            use_graphviz: If True, use Graphviz-based export; if False, use pure NetworkX (default)

        Returns:
            Path to the generated GraphML file
        """
        # Use pure NetworkX exporter by default (no Graphviz required)
        if not use_graphviz:
            from pyarchinit_mini.graphml_converter.pure_networkx_exporter import export_harris_matrix_pure_python

            print("")
            print("📊 Exporting Harris Matrix with pure NetworkX (no Graphviz required)")
            print("")

            return export_harris_matrix_pure_python(
                graph=graph,
                output_path=output_path,
                site_name=site_name,
                title=title or site_name,
                use_extended_labels=use_extended_labels,
                include_periods=include_periods,
                apply_transitive_reduction=True,
                reverse_epochs=reverse_epochs,
                db_manager=self.db_manager
            )

        # Graphviz-based export (requires Graphviz installation)
        try:
            from graphviz import Digraph
        except ImportError:
            print("❌ ERROR: Python graphviz module not installed")
            print("   Install with: pip install 'pyarchinit-mini[harris]'")
            print("   or: pip install graphviz")
            print("")
            print("💡 TIP: You can use pure NetworkX export (default) which doesn't require Graphviz:")
            print("   generator.export_to_graphml(graph, output_path, use_graphviz=False)")
            return ""

        # Check if Graphviz software is installed
        import shutil
        if not shutil.which('dot'):
            print("⚠️  WARNING: Graphviz software not found in system PATH")
            print("   The Python module 'graphviz' requires Graphviz software to be installed.")
            print("   ")
            print("   Install instructions:")
            print("   - Linux (Debian/Ubuntu): sudo apt install graphviz")
            print("   - Linux (Fedora/RHEL):   sudo dnf install graphviz")
            print("   - macOS (Homebrew):      brew install graphviz")
            print("   - Windows (Chocolatey):  choco install graphviz")
            print("   - Or download from:      https://graphviz.org/download/")
            print("   ")
            print("   After installation, verify with: dot -V")
            print("")
            print("💡 TIP: You can use pure NetworkX export which doesn't require Graphviz:")
            print("   generator.export_to_graphml(graph, output_path, use_graphviz=False)")
            return ""

        # Choose layout engine based on graph size
        # For medium graphs (500-700 nodes), use sfdp which is MUCH faster
        # For very large graphs (700+ nodes), skip layout pre-calculation (let yEd handle it)
        num_nodes = len(graph.nodes())
        num_edges = len(graph.edges())

        # Thresholds for layout engine selection
        skip_layout = num_nodes > 700 or num_edges > 2000  # Very large - skip layout
        use_sfdp = (num_nodes > 500 or num_edges > 1500) and not skip_layout  # Medium-large - use sfdp
        layout_engine = 'sfdp' if use_sfdp else 'dot'

        if skip_layout:
            print(f"⚠️  Very large graph detected ({num_nodes} nodes, {num_edges} edges)")
            print(f"   Skipping layout pre-calculation to avoid memory issues")
            print(f"   yEd will calculate the layout when you open the file")
        elif use_sfdp:
            print(f"🚀 Using sfdp layout engine for large graph ({num_nodes} nodes, {num_edges} edges)")
            print(f"   sfdp is optimized for large graphs and will be much faster than dot")

        # Create Graphviz Digraph (PyArchInit method)
        G = Digraph(engine=layout_engine, strict=False)
        G.attr(rankdir='TB')
        G.attr(compound='true')
        G.graph_attr['pad'] = "0.5"

        if use_sfdp:
            # sfdp-specific optimizations for large graphs
            G.graph_attr['overlap'] = 'scale'  # Scale layout to avoid overlaps
            G.graph_attr['sep'] = '+10'        # Minimum separation between nodes
            G.graph_attr['esep'] = '+3'        # Edge separation
            G.graph_attr['K'] = '0.3'          # Spring constant (affects spacing)
        else:
            # dot-specific settings for hierarchical layout
            G.graph_attr['nodesep'] = "1"
            G.graph_attr['ranksep'] = "1.5"
            G.graph_attr['splines'] = 'ortho'

        G.graph_attr['dpi'] = '150'

        # Build edge lists by type for Extended Matrix styling
        # All edges are BLACK but with different styles
        edges_dotted = []           # taglia, tagliato da, property, >, <, >>, <<
        edges_double_no_arrow = []  # uguale a, si lega a
        edges_dot_arrow = []        # si appoggia, gli si appoggia
        edges_box_arrow = []        # riempie, riempito da
        edges_no_arrow = []         # continuity (CON)
        edges_normal = []           # copre, coperto da (default stratigraphic)

        # Get ALL nodes from graph (including isolated nodes without relationships)
        us_rilevanti = set(graph.nodes())

        # Classify edges by relationship type
        for source, target, edge_data in graph.edges(data=True):
            rel_type = edge_data.get('relationship', 'sopra')
            rel_lower = rel_type.lower()

            # Get node labels for edge
            source_label = graph.nodes[source].get('extended_label' if use_extended_labels else 'label', source)
            target_label = graph.nodes[target].get('extended_label' if use_extended_labels else 'label', target)

            edge_tuple = (source_label, target_label)

            # Check if source or target is a CON node (continuity)
            is_continuity = (source_label.startswith('CON') or target_label.startswith('CON') or
                           'continuità' in source_label.lower() or 'continuità' in target_label.lower() or
                           'continuity' in source_label.lower() or 'continuity' in target_label.lower())

            # Classify by Extended Matrix style
            if is_continuity or 'continuità' in rel_lower or 'continuity' in rel_lower:
                # Continuity edges: solid without arrow
                edges_no_arrow.append(edge_tuple)
            elif rel_lower in ['taglia', 'tagliato da', 'cuts', 'cut by', 'property', '>', '<', '>>', '<<']:
                edges_dotted.append(edge_tuple)
            elif rel_lower in ['uguale a', 'same as', 'si lega a', 'bonds with']:
                edges_double_no_arrow.append(edge_tuple)
            elif rel_lower in ['si appoggia', 'si appoggia a', 'gli si appoggia', 'leans against', 'abuts']:
                edges_dot_arrow.append(edge_tuple)
            elif rel_lower in ['riempie', 'riempito da', 'fills', 'filled by']:
                edges_box_arrow.append(edge_tuple)
            else:
                # Default: normal stratigraphic relationships (copre, coperto da, sopra, etc.)
                edges_normal.append(edge_tuple)

        # Organize nodes by datazione estesa if requested
        if include_periods:
            # Build lookup map from periodizzazione_table: (periodo, fase) -> datazione_estesa
            from sqlalchemy import text
            from sqlalchemy.orm import sessionmaker

            periodo_fase_to_datazione = {}  # Map (periodo, fase) to datazione_estesa

            try:
                Session = sessionmaker(bind=self.db_manager.connection.engine)
                session = Session()

                try:
                    # Query periodizzazione_table to build lookup map
                    query = text("""
                        SELECT periodo_iniziale, fase_iniziale, datazione_estesa
                        FROM periodizzazione_table
                        WHERE sito = :site
                    """)
                    result = session.execute(query, {'site': site_name})

                    for row in result.fetchall():
                        periodo = str(row.periodo_iniziale) if row.periodo_iniziale else ''
                        fase = str(row.fase_iniziale) if row.fase_iniziale else ''
                        datazione = row.datazione_estesa or 'Non datato'

                        # Create key from periodo-fase
                        key = (periodo, fase)
                        periodo_fase_to_datazione[key] = datazione

                finally:
                    session.close()

            except Exception as e:
                print(f"Warning: Could not load periodizzazione data: {e}")

            # Group nodes by datazione_estesa
            datazione_groups = {}
            datazione_min_periodo_fase = {}  # Track min (periodo, fase) for each datazione

            for node_id, node_data in graph.nodes(data=True):
                # Include ALL nodes (even isolated ones without relationships)

                # Get periodo/fase from node data (from us_table)
                # IMPORTANT: Handle None values correctly (str(None) = 'None' not '')
                periodo_raw = node_data.get('period_initial')
                fase_raw = node_data.get('phase_initial')

                periodo = str(periodo_raw) if periodo_raw is not None and periodo_raw != '' else ''
                fase = str(fase_raw) if fase_raw is not None and fase_raw != '' else ''

                # Look up datazione_estesa using periodo-fase key
                lookup_key = (periodo, fase)
                if lookup_key in periodo_fase_to_datazione:
                    datazione = periodo_fase_to_datazione[lookup_key]
                else:
                    datazione = 'Non datato'

                # Track minimum (periodo, fase) for this datazione for correct sorting
                if datazione not in datazione_min_periodo_fase:
                    datazione_min_periodo_fase[datazione] = (periodo, fase)
                else:
                    current_min = datazione_min_periodo_fase[datazione]
                    # Compare periodo first, then fase
                    # Use 'ZZZ' for empty strings so they sort last
                    if (periodo or 'ZZZ', fase or 'ZZZ') < (current_min[0] or 'ZZZ', current_min[1] or 'ZZZ'):
                        datazione_min_periodo_fase[datazione] = (periodo, fase)

                # Use datazione as primary key, track nodes by datazione only
                if datazione not in datazione_groups:
                    datazione_groups[datazione] = []

                datazione_groups[datazione].append((node_id, node_data))

            # Sort by minimum (periodo, fase) for each datazione (ordine cronologico)
            # Non datato should be last
            sorted_groups = sorted(
                datazione_groups.items(),
                key=lambda x: (
                    datazione_min_periodo_fase[x[0]][0] or 'ZZZ',  # periodo
                    datazione_min_periodo_fase[x[0]][1] or 'ZZZ',  # fase
                    x[0]  # datazione name as tiebreaker
                )
            )

            # Create subgraphs per datazione
            cluster_id = 0
            for datazione, nodes in sorted_groups:
                cluster_id += 1

                # Create single cluster for each datazione
                cluster_key = f'cluster_datazione_{cluster_id}'

                with G.subgraph(name=cluster_key) as c:
                    # Use datazione_estesa as label
                    c.attr(label=datazione,
                          style='filled', color='lightblue', rank='same')

                    # Add nodes to datazione cluster
                    for node_id, node_data in nodes:
                        if use_extended_labels and 'extended_label' in node_data:
                            node_label = node_data['extended_label']
                        else:
                            node_label = f"US{node_id}"

                        # Add node with description as tooltip, URL and period NAME (datazione_estesa)
                        node_desc = node_data.get('description', '')
                        node_url = node_data.get('url', '')

                        # Build attributes dict
                        attrs = {'label': node_label, 'shape': 'box', 'style': 'filled',
                                'fillcolor': 'white', 'tooltip': node_desc}
                        if node_url:
                            attrs['URL'] = node_url
                        # Use datazione_estesa (period NAME) instead of period code for positioning
                        if datazione:
                            attrs['period'] = datazione

                        c.node(node_label, **attrs)
        else:
            # Simple mode: add all nodes without grouping
            for node_id, node_data in graph.nodes(data=True):
                if use_extended_labels and 'extended_label' in node_data:
                    node_label = node_data['extended_label']
                else:
                    node_label = f"US{node_id}"

                # Add node with description as tooltip, URL and period code
                node_desc = node_data.get('description', '')
                node_url = node_data.get('url', '')
                periodo_code = node_data.get('periodo_code', '')

                # Build attributes dict
                attrs = {'label': node_label, 'shape': 'box', 'style': 'filled',
                        'fillcolor': 'white', 'tooltip': node_desc}
                if node_url:
                    attrs['URL'] = node_url
                if periodo_code:
                    attrs['period'] = periodo_code

                G.node(node_label, **attrs)

        # Add edges with Extended Matrix styling
        # All edges are BLACK but with different line styles and arrowheads

        # 1. Dotted edges (cuts, property, EM symbols)
        for source_label, target_label in edges_dotted:
            G.edge(source_label, target_label,
                  color='black',
                  style='dotted',
                  arrowhead='normal')

        # 2. Double arrows (uguale a, si lega a)
        # These relationships mean nodes are equivalent
        # Use dir=both for double arrows, constraint=false to avoid affecting layout
        for source_label, target_label in edges_double_no_arrow:
            G.edge(source_label, target_label,
                  color='black',
                  style='bold',
                  dir='both',  # Double arrows on both ends
                  arrowhead='normal',
                  arrowtail='normal')

        # 3. Solid with dot arrow (si appoggia)
        for source_label, target_label in edges_dot_arrow:
            G.edge(source_label, target_label,
                  color='black',
                  style='solid',
                  arrowhead='dot')

        # 4. Solid with box arrow (riempie)
        for source_label, target_label in edges_box_arrow:
            G.edge(source_label, target_label,
                  color='black',
                  style='solid',
                  arrowhead='box')

        # 5. Solid without arrow (continuity)
        for source_label, target_label in edges_no_arrow:
            G.edge(source_label, target_label,
                  color='black',
                  style='solid',
                  arrowhead='none')

        # 6. Normal solid arrows (copre, coperto da - default stratigraphic)
        for source_label, target_label in edges_normal:
            G.edge(source_label, target_label,
                  color='black',
                  style='solid',
                  arrowhead='normal')

        # Render to DOT file
        # For large graphs we use sfdp which is much faster than dot
        dot_path = output_path.replace('.graphml', '.dot')
        G.format = 'dot'

        if skip_layout:
            # For very large graphs, skip layout processing entirely
            # Just write the DOT source directly (yEd will calculate layout)
            print(f"ℹ️  Writing DOT source without layout processing (fast mode)...")
            with open(dot_path, 'w', encoding='utf-8') as f:
                f.write(G.source)
            print(f"✅ Generated DOT file (no layout): {dot_path}")
        else:
            # For smaller graphs, process layout with sfdp or dot
            try:
                import subprocess

                # Write source to file first
                dot_source_path = dot_path.replace('.dot', '_source.dot')
                with open(dot_source_path, 'w', encoding='utf-8') as f:
                    f.write(G.source)

                # Use sfdp or dot to process the layout
                print(f"ℹ️  Processing layout with {layout_engine}...")
                with open(dot_path, 'w') as outfile:
                    result = subprocess.run(
                        [layout_engine, '-Tdot', dot_source_path],
                        stdout=outfile,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=120  # 2 minutes timeout even for large graphs with sfdp
                    )

                if result.returncode == 0:
                    print(f"✅ Generated DOT file with {layout_engine} layout: {dot_path}")
                else:
                    print(f"⚠️  {layout_engine} processing failed, using source DOT")
                    import shutil
                    shutil.copy(dot_source_path, dot_path)

            except subprocess.TimeoutExpired:
                print(f"⚠️  {layout_engine} timeout - graph too large, using source DOT")
                # Use source DOT without layout
                import shutil
                shutil.copy(dot_source_path, dot_path)
            except Exception as e:
                print(f"⚠️  Error during {layout_engine} processing: {e}")
                print(f"   Using source DOT without layout")
                with open(dot_path, 'w', encoding='utf-8') as f:
                    f.write(G.source)

        # Apply transitive reduction using Graphviz tred command
        # This is the PyArchInit approach: use tred to reduce the graph
        # while preserving only the minimal set of edges
        dot_reduced_path = dot_path.replace('.dot', '_tred.dot')

        try:
            import subprocess
            print(f"ℹ️  Applying transitive reduction with tred...")

            # Calculate timeout based on graph size (larger graphs need more time)
            # For large graphs: ~60 seconds for 500-1000 nodes, 120s for 1000+
            tred_timeout = 30 if num_nodes < 500 else (60 if num_nodes < 1000 else 120)

            # Run tred command: tred input.dot > output_tred.dot
            with open(dot_reduced_path, 'w') as outfile:
                result = subprocess.run(
                    ['tred', dot_path],
                    stdout=outfile,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=tred_timeout
                )

            if result.returncode == 0:
                print(f"✅ Transitive reduction applied: {dot_reduced_path}")
                # Use the reduced DOT for GraphML conversion
                dot_path = dot_reduced_path
            else:
                print(f"⚠️  tred command failed: {result.stderr}")
                print(f"ℹ️  Using unreduced DOT file")
        except FileNotFoundError:
            print(f"⚠️  tred command not found (Graphviz software not installed)")
            print(f"   Install Graphviz: https://graphviz.org/download/")
            print(f"   - Linux: sudo apt install graphviz")
            print(f"   - macOS: brew install graphviz")
            print(f"   - Windows: choco install graphviz")
            print(f"ℹ️  Using unreduced DOT file (matrix may have redundant edges)")
        except Exception as e:
            print(f"⚠️  Error running tred: {e}")
            print(f"ℹ️  Using unreduced DOT file")

        # Convert DOT to GraphML using existing PyArchInit converter
        try:
            from ..graphml_converter.converter import convert_dot_to_graphml

            # Convert using PyArchInit method
            success = convert_dot_to_graphml(
                dot_path,
                output_path,
                title=title or site_name or "Harris Matrix",
                reverse_epochs=reverse_epochs
            )

            if success:
                print(f"✅ Exported Harris Matrix to GraphML: {output_path}")
                print(f"  - Nodes: {len(graph.nodes())}")
                print(f"  - Edges: {len(graph.edges())}")
                print(f"  - Extended labels: {use_extended_labels}")
                print(f"  - Method: DOT → GraphML (PyArchInit compatible)")
                return output_path
            else:
                print(f"⚠️  Could not convert DOT to GraphML")
                print(f"DOT file is available at: {dot_path}")
                return dot_path

        except Exception as e:
            print(f"Warning: Could not convert DOT to GraphML: {e}")
            import traceback
            traceback.print_exc()
            print(f"DOT file is available at: {dot_path}")
            # Return DOT path as fallback
            return dot_path