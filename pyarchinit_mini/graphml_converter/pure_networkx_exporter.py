"""
Pure NetworkX GraphML Exporter
Complete GraphML export without Graphviz dependency
Produces yEd-compatible Extended Matrix output with period clustering
"""

import networkx as nx
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from xml.etree.ElementTree import Element

from .graphml_builder import GraphMLBuilder


class PureNetworkXExporter:
    """
    Export Harris Matrix to GraphML using pure Python/NetworkX
    No Graphviz software dependency required
    """

    def __init__(self, db_manager=None):
        """Initialize exporter

        Args:
            db_manager: Optional database manager for fetching period datations
        """
        self.builder = GraphMLBuilder()
        self.db_manager = db_manager

    def _load_period_datations(self, site_name: str) -> Dict[Tuple[str, str], Tuple[str, Optional[int], Optional[int]]]:
        """
        Load period datations from periodizzazione_table with chronological dates

        Args:
            site_name: Site name to query

        Returns:
            Dictionary mapping (periodo_iniziale, fase_iniziale) to (datazione_estesa, start_date, end_date)
        """
        if not self.db_manager:
            print("⚠️  No database manager provided - using numeric period labels")
            return {}

        periodo_fase_to_info = {}

        try:
            from sqlalchemy import text
            from sqlalchemy.orm import sessionmaker

            Session = sessionmaker(bind=self.db_manager.connection.engine)
            session = Session()

            try:
                # Query periodizzazione_table JOIN period_table to get dates for chronological sorting
                query = text("""
                    SELECT DISTINCT
                        p.periodo_iniziale,
                        p.fase_iniziale,
                        p.datazione_estesa,
                        per.start_date,
                        per.end_date
                    FROM periodizzazione_table p
                    LEFT JOIN period_table per ON (
                        (p.period_id_final IS NOT NULL AND per.id_period = p.period_id_final) OR
                        (p.period_id_final IS NULL AND per.id_period = p.period_id_initial)
                    )
                    WHERE p.sito = :site
                """)
                result = session.execute(query, {'site': site_name})

                for row in result.fetchall():
                    periodo = str(row.periodo_iniziale) if row.periodo_iniziale else ''
                    fase = str(row.fase_iniziale) if row.fase_iniziale else ''
                    datazione = row.datazione_estesa or 'Non datato'
                    start_date = row.start_date if hasattr(row, 'start_date') else None
                    end_date = row.end_date if hasattr(row, 'end_date') else None

                    # Create key from periodo-fase
                    key = (periodo, fase)
                    periodo_fase_to_info[key] = (datazione, start_date, end_date)

                print(f"✅ Loaded {len(periodo_fase_to_info)} period datations with chronological dates")

            finally:
                session.close()

        except Exception as e:
            print(f"⚠️  Could not load periodizzazione data: {e}")
            import traceback
            traceback.print_exc()

        return periodo_fase_to_info

    def export(
        self,
        graph: nx.DiGraph,
        output_path: str,
        site_name: str = "",
        title: str = "",
        use_extended_labels: bool = True,
        include_periods: bool = True,
        apply_transitive_reduction: bool = True,
        reverse_epochs: bool = True
    ) -> str:
        """
        Export Harris Matrix graph to GraphML with yEd compatibility

        Args:
            graph: NetworkX directed graph with Extended Matrix attributes
            output_path: Output file path
            site_name: Site name for title
            title: Graph title (defaults to site_name)
            use_extended_labels: Use PyArchInit Extended Matrix label format
            include_periods: Group nodes by periods in TableNode
            apply_transitive_reduction: Remove redundant edges
            reverse_epochs: Reverse chronological order (newest first, default: True)

        Returns:
            Output file path on success, None on failure
        """
        try:
            print(f"")
            print(f"=== Pure NetworkX GraphML Export ===")
            print(f"Site: {site_name}")
            print(f"Nodes: {len(graph.nodes())}")
            print(f"Edges: {len(graph.edges())}")
            print(f"")

            # Step 1: Apply transitive reduction if requested
            export_graph = graph.copy()

            if apply_transitive_reduction:
                export_graph = self._apply_transitive_reduction(export_graph)

            # Step 1b: Load period datations from database
            period_datations = {}
            if include_periods and site_name:
                period_datations = self._load_period_datations(site_name)

            # Step 2: Group nodes by period if requested
            period_groups = {}
            if include_periods:
                period_groups = self._group_nodes_by_period(export_graph, period_datations)
                print(f"✅ Grouped nodes into {len(period_groups)} periods")
                print(f"")

            # Step 3: Build GraphML structure
            graph_title = title or site_name or "Harris Matrix"
            self.builder.create_document(title=graph_title)

            # Step 4: Add TableNode group if periods exist
            nested_graph = None
            if include_periods and period_groups:
                nested_graph = self._add_period_clustering(site_name, period_groups, reverse_epochs)

            # Step 4b: Add nodes
            if nested_graph is not None:
                # Add nodes inside TableNode nested graph
                self._add_nodes_nested(export_graph, use_extended_labels, nested_graph, reverse_epochs, period_datations)
            else:
                # Add nodes flat (no period clustering)
                self._add_nodes_flat(export_graph, use_extended_labels)

            # Step 5: Add edges
            # Use prefixed node IDs if nodes are nested
            use_nested_ids = (nested_graph is not None)
            # Reverse edge direction if epochs are reversed (so edges point downward)
            self._add_edges(export_graph, use_nested_ids=use_nested_ids, reverse_direction=reverse_epochs)

            # Step 6: Write to file
            self.builder.write_to_file(output_path)

            print(f"")
            print(f"✅ Export complete: {output_path}")
            print(f"")

            return output_path

        except Exception as e:
            print(f"❌ Export failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _apply_transitive_reduction(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Apply transitive reduction to remove redundant edges

        Args:
            graph: Input graph

        Returns:
            Reduced graph
        """
        print(f"ℹ️  Applying transitive reduction...")

        edges_before = len(graph.edges())

        # Check if graph is a DAG
        try:
            is_dag = nx.is_directed_acyclic_graph(graph)
        except Exception as e:
            print(f"⚠️  Could not check if graph is acyclic: {e}")
            is_dag = False

        if not is_dag:
            print(f"⚠️  Graph contains cycles - transitive reduction requires a DAG")
            print(f"   Skipping transitive reduction (keeping all edges)")
            print(f"   Note: Cycles may indicate data quality issues")
            print(f"")
            return graph

        # Apply transitive reduction
        try:
            reduced_graph = nx.transitive_reduction(graph)

            # Copy node attributes
            for node_id, node_data in graph.nodes(data=True):
                for attr_key, attr_value in node_data.items():
                    reduced_graph.nodes[node_id][attr_key] = attr_value

            # Copy edge attributes
            for source, target, edge_data in graph.edges(data=True):
                if reduced_graph.has_edge(source, target):
                    for attr_key, attr_value in edge_data.items():
                        reduced_graph[source][target][attr_key] = attr_value

            edges_after = len(reduced_graph.edges())
            edges_removed = edges_before - edges_after
            reduction_pct = (edges_removed / edges_before * 100) if edges_before > 0 else 0

            print(f"✅ Transitive reduction complete:")
            print(f"   - Edges before: {edges_before}")
            print(f"   - Edges after: {edges_after}")
            print(f"   - Removed: {edges_removed} ({reduction_pct:.1f}%)")
            print(f"")

            return reduced_graph

        except Exception as e:
            print(f"⚠️  Transitive reduction failed: {e}")
            print(f"   Keeping original graph")
            print(f"")
            return graph

    def _group_nodes_by_period(
        self,
        graph: nx.DiGraph,
        period_datations: Dict[Tuple[str, str], Tuple[str, Optional[int], Optional[int]]] = None
    ) -> Dict[str, Tuple[List[str], str, Tuple[str, str], Optional[int], Optional[int]]]:
        """
        Group nodes by their period attribute and extract period labels with chronological dates

        Args:
            graph: Input graph
            period_datations: Optional mapping of (periodo_initial, fase_initial) to (datazione_estesa, start_date, end_date)

        Returns:
            Dictionary mapping period codes to (node_list, period_label, (period_initial, phase_initial), start_date, end_date) tuples
        """
        if period_datations is None:
            period_datations = {}

        period_groups = defaultdict(lambda: {
            'nodes': [],
            'period_initial': None,
            'phase_initial': None,
            'start_date': None,
            'end_date': None
        })

        for node_id, node_data in graph.nodes(data=True):
            # Get period numeric values
            period_initial = node_data.get('period_initial', '')
            phase_initial = node_data.get('phase_initial', '')

            # Convert to string for consistent handling
            periodo_str = str(period_initial) if period_initial else ''
            fase_str = str(phase_initial) if phase_initial else ''

            # Look up datazione estesa and dates from database mapping
            lookup_key = (periodo_str, fase_str)
            start_date = None
            end_date = None

            if lookup_key in period_datations:
                period_info = period_datations[lookup_key]
                period_label = period_info[0]  # datazione_estesa
                start_date = period_info[1] if len(period_info) > 1 else None
                end_date = period_info[2] if len(period_info) > 2 else None
            else:
                # Fallback: check node's period attribute (might already have extended date)
                period_label = node_data.get('period', '')
                if not period_label:
                    # Last fallback: generate numeric label
                    if periodo_str:
                        if fase_str:
                            period_label = f"Periodo {periodo_str} - Fase {fase_str}"
                        else:
                            period_label = f"Periodo {periodo_str}"
                    else:
                        period_label = 'Non datato'

            # Use period_label as grouping key
            period_groups[period_label]['nodes'].append(node_id)
            # Store numeric values and dates for sorting
            if periodo_str and period_groups[period_label]['period_initial'] is None:
                period_groups[period_label]['period_initial'] = periodo_str
            if fase_str and period_groups[period_label]['phase_initial'] is None:
                period_groups[period_label]['phase_initial'] = fase_str
            if start_date and period_groups[period_label]['start_date'] is None:
                period_groups[period_label]['start_date'] = start_date
            if end_date and period_groups[period_label]['end_date'] is None:
                period_groups[period_label]['end_date'] = end_date

        # Convert to final format: {period: (node_list, label, (period_initial, phase_initial), start_date, end_date)}
        result = {}
        for period_label, data in period_groups.items():
            result[period_label] = (
                data['nodes'],
                period_label,
                (data['period_initial'] or '', data['phase_initial'] or ''),
                data['start_date'],
                data['end_date']
            )

        return result

    def _add_period_clustering(
        self,
        site_name: str,
        period_groups: Dict[str, Tuple[List[str], str, Tuple[str, str], Optional[int], Optional[int]]],
        reverse_epochs: bool = True
    ) -> Optional[Element]:
        """
        Add TableNode structure with period rows sorted chronologically

        Args:
            site_name: Site name for TableNode title
            period_groups: Dictionary mapping period codes to (node_list, label, (period_initial, phase_initial), start_date, end_date) tuples
            reverse_epochs: Reverse chronological order (newest first)

        Returns:
            Nested graph element for adding nodes
        """
        print(f"ℹ️  Creating TableNode with {len(period_groups)} period rows...")

        # Sort periods CHRONOLOGICALLY using end_date from Period table
        # If reverse_epochs=True, invert to show newest periods first (at top)
        def chronological_sort_key(period_code):
            period_data = period_groups[period_code]
            end_date = period_data[4] if len(period_data) > 4 else None
            start_date = period_data[3] if len(period_data) > 3 else None
            periodo_fase = period_data[2] if len(period_data) > 2 else ('', '')

            # Return a 3-tuple to ensure consistent sorting:
            # (has_date, date_value, periodo_val, fase_val)
            # This ensures all keys have same structure for comparison
            if end_date is not None:
                return (1, end_date, 0, 0)
            elif start_date is not None:
                return (1, start_date, 0, 0)
            else:
                # No date available, use periodo/fase for sorting
                # Put periods without dates AFTER those with dates (0 < 1)
                periodo_val, fase_val = self._period_sort_key_numeric(periodo_fase)
                # Ensure periodo_val and fase_val are comparable types
                # Convert to tuple of (0, inf, periodo_val, fase_val)
                # Using float('inf') for date position to sort after dated periods
                return (0, float('inf'), periodo_val if isinstance(periodo_val, (int, float)) else 0,
                        fase_val if isinstance(fase_val, (int, float)) else 0)

        sorted_periods = sorted(period_groups.keys(), key=chronological_sort_key)

        if reverse_epochs:
            sorted_periods = list(reversed(sorted_periods))
            print(f"ℹ️  Reversed chronological order (newest first): {sorted_periods}")
        else:
            print(f"ℹ️  Chronological order (oldest first): {sorted_periods}")

        # Prepare period rows: (period_id, period_label, node_ids)
        periods = []
        for period_code in sorted_periods:
            node_ids = period_groups[period_code][0]
            period_label = period_groups[period_code][1]
            period_id = self._sanitize_id(period_code)
            periods.append((period_id, period_label, node_ids))

        # Add TableNode group structure and get nested graph
        group_node, nested_graph = self.builder.add_table_node_group(
            site_name=site_name,
            periods=periods,
            width=1044.0,
            row_height=940.0
        )

        print(f"✅ Created TableNode with nested graph for {len(period_groups)} periods sorted chronologically")
        print(f"")

        return nested_graph

    def _add_nodes_flat(self, graph: nx.DiGraph, use_extended_labels: bool):
        """
        Add nodes without period grouping (flat structure)

        Args:
            graph: Input graph
            use_extended_labels: Use Extended Matrix label format
        """
        print(f"ℹ️  Adding {len(graph.nodes())} nodes...")

        for node_id, node_data in graph.nodes(data=True):
            # Get label
            if use_extended_labels:
                label = node_data.get('extended_label', f'US{node_id}')
            else:
                label = node_data.get('label', f'US{node_id}')

            # Get other attributes
            description = node_data.get('description', '')
            url = node_data.get('url', '')
            period = node_data.get('period', '')
            area = node_data.get('area', '')

            # Add node
            self.builder.add_node(
                node_id=node_id,
                label=label,
                extended_label=node_data.get('extended_label', ''),
                description=description,
                url=url,
                period=period,
                area=area
            )

        print(f"✅ Added {len(graph.nodes())} nodes")

    def _add_nodes_nested(
        self,
        graph: nx.DiGraph,
        use_extended_labels: bool,
        nested_graph: Element,
        reverse_epochs: bool = True,
        period_datations: Dict[Tuple[str, str], Tuple[str, Optional[int], Optional[int]]] = None
    ):
        """
        Add nodes inside TableNode nested graph with prefixed IDs
        Nodes are positioned in their period rows sorted chronologically

        Args:
            graph: Input graph
            use_extended_labels: Use Extended Matrix label format
            nested_graph: Parent graph element for nesting
            reverse_epochs: Reverse chronological order (newest first)
            period_datations: Optional mapping of (periodo_initial, fase_initial) to (datazione_estesa, start_date, end_date)
        """
        print(f"ℹ️  Adding {len(graph.nodes())} nodes to TableNode nested graph...")

        # Group nodes by period and create period->row_index mapping
        period_groups = self._group_nodes_by_period(graph, period_datations)

        # Use chronological sorting (same logic as _add_period_clustering)
        def chronological_sort_key(period_code):
            period_data = period_groups[period_code]
            end_date = period_data[4] if len(period_data) > 4 else None
            start_date = period_data[3] if len(period_data) > 3 else None
            periodo_fase = period_data[2] if len(period_data) > 2 else ('', '')

            # Return a 4-tuple to ensure consistent sorting:
            # (has_date, date_value, periodo_val, fase_val)
            # This ensures all keys have same structure for comparison
            if end_date is not None:
                return (1, end_date, 0, 0)
            elif start_date is not None:
                return (1, start_date, 0, 0)
            else:
                # No date available, use periodo/fase for sorting
                # Put periods without dates AFTER those with dates (0 < 1)
                periodo_val, fase_val = self._period_sort_key_numeric(periodo_fase)
                # Ensure periodo_val and fase_val are comparable types
                # Convert to tuple of (0, inf, periodo_val, fase_val)
                # Using float('inf') for date position to sort after dated periods
                return (0, float('inf'), periodo_val if isinstance(periodo_val, (int, float)) else 0,
                        fase_val if isinstance(fase_val, (int, float)) else 0)

        sorted_periods = sorted(period_groups.keys(), key=chronological_sort_key)
        if reverse_epochs:
            sorted_periods = list(reversed(sorted_periods))

        period_to_row = {period: idx for idx, period in enumerate(sorted_periods)}

        # Calculate Y positions
        row_height = 940.0
        header_offset = 100.0

        # Track node count per row for horizontal distribution
        nodes_per_row = {period: 0 for period in sorted_periods}

        for node_id, node_data in graph.nodes(data=True):
            # Get label
            if use_extended_labels:
                label = node_data.get('extended_label', f'US{node_id}')
            else:
                label = node_data.get('label', f'US{node_id}')

            # Get other attributes
            description = node_data.get('description', '')
            url = node_data.get('url', '')

            # Get period using EXACT same logic as _group_nodes_by_period
            # Get period numeric values
            period_initial = node_data.get('period_initial', '')
            phase_initial = node_data.get('phase_initial', '')

            # Convert to string for consistent handling
            periodo_str = str(period_initial) if period_initial else ''
            fase_str = str(phase_initial) if phase_initial else ''

            # Look up datazione estesa from database mapping
            lookup_key = (periodo_str, fase_str)
            if period_datations and lookup_key in period_datations:
                period_info = period_datations[lookup_key]
                period = period_info[0]  # Extract datazione_estesa from tuple
            else:
                # Fallback: check node's period attribute (might already have extended date)
                period = node_data.get('period', '')
                if not period:
                    # Last fallback: generate numeric label
                    if periodo_str:
                        if fase_str:
                            period = f"Periodo {periodo_str} - Fase {fase_str}"
                        else:
                            period = f"Periodo {periodo_str}"
                    else:
                        period = 'Non datato'

            area = node_data.get('area', '')

            # Determine period row
            period_row = period_to_row.get(period, 0)

            # Calculate Y position for this period row
            y_position = header_offset + (period_row * row_height)

            # Add horizontal offset for nodes in same row (simple distribution)
            node_offset = nodes_per_row[period] * 150.0  # 150px spacing
            nodes_per_row[period] += 1

            # Add node with prefixed ID
            prefixed_node_id = f"table_node_group::{node_id}"

            # Add node to nested graph with position
            self.builder.add_node(
                node_id=prefixed_node_id,
                label=label,
                extended_label=node_data.get('extended_label', ''),
                description=description,
                url=url,
                period=period,
                area=area,
                parent_graph=nested_graph,
                y_position=y_position,
                period_row=period_row
            )

        print(f"✅ Added {len(graph.nodes())} nested nodes across {len(sorted_periods)} period rows")

    def _add_edges(self, graph: nx.DiGraph, use_nested_ids: bool = False, reverse_direction: bool = False):
        """
        Add edges with relationship attributes

        Args:
            graph: Input graph
            use_nested_ids: If True, use prefixed node IDs (table_node_group::ID)
            reverse_direction: If True, invert source/target (for reversed epoch display)
        """
        print(f"ℹ️  Adding {len(graph.edges())} edges...")

        for source, target, edge_data in graph.edges(data=True):
            # Get edge attributes
            label = edge_data.get('label', '')
            relationship = edge_data.get('relationship', '')
            certainty = edge_data.get('certainty', '')

            # Invert source/target if epochs are reversed
            # This ensures edges still point downward (from newer to older)
            if reverse_direction:
                source, target = target, source

            # Use prefixed IDs if nodes are nested in TableNode
            if use_nested_ids:
                source_id = f"table_node_group::{source}"
                target_id = f"table_node_group::{target}"
            else:
                source_id = source
                target_id = target

            # Add edge
            self.builder.add_edge(
                source_id=source_id,
                target_id=target_id,
                label=label,
                relationship=relationship,
                certainty=certainty
            )

        print(f"✅ Added {len(graph.edges())} edges")

    @staticmethod
    def _period_sort_key(period_str: str):
        """
        Generate sort key for period string (e.g., "2.3" -> (2, 3))

        Args:
            period_str: Period string (e.g., "1", "2.3", "Periodo 2")

        Returns:
            Tuple for sorting
        """
        import re
        # Extract numbers from string
        numbers = re.findall(r'\d+\.?\d*', period_str)
        if numbers:
            try:
                # Parse first number as float (handles "2.3" format)
                return (float(numbers[0]),)
            except ValueError:
                pass
        # Fallback to string comparison
        return (period_str,)

    @staticmethod
    def _period_sort_key_numeric(periodo_fase_tuple: Tuple[str, str]):
        """
        Generate sort key from (period_initial, phase_initial) tuple

        Args:
            periodo_fase_tuple: (period_initial, phase_initial) tuple (e.g., ("2", "3"))

        Returns:
            Tuple for sorting, handling empty strings as ZZZ for sorting last
        """
        periodo, fase = periodo_fase_tuple

        # Try to convert to float for numeric periods, fallback to string for textual periods
        try:
            periodo_val = float(periodo) if periodo else float('inf')
        except (ValueError, TypeError):
            # For textual periods (e.g., "Hellenistic", "Medieval"), use string sorting
            periodo_val = periodo if periodo else 'zzz'

        try:
            fase_val = float(fase) if fase else float('inf')
        except (ValueError, TypeError):
            fase_val = fase if fase else 'zzz'

        return (periodo_val, fase_val)

    @staticmethod
    def _sanitize_id(text: str) -> str:
        """
        Sanitize text for use as XML ID

        Args:
            text: Input text

        Returns:
            Sanitized ID string
        """
        import re
        # Replace spaces and special chars with underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        # Remove consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        return sanitized or 'node'


# Convenience function
def export_harris_matrix_pure_python(
    graph: nx.DiGraph,
    output_path: str,
    site_name: str = "",
    title: str = "",
    use_extended_labels: bool = True,
    include_periods: bool = True,
    apply_transitive_reduction: bool = True,
    reverse_epochs: bool = True,
    db_manager=None
) -> str:
    """
    Export Harris Matrix to GraphML using pure Python/NetworkX

    Args:
        graph: NetworkX directed graph with Extended Matrix attributes
        output_path: Output file path
        site_name: Site name for title
        title: Graph title
        use_extended_labels: Use Extended Matrix label format
        include_periods: Group nodes by periods
        apply_transitive_reduction: Remove redundant edges
        reverse_epochs: Reverse chronological order (newest first, default: True)
        db_manager: Optional database manager for fetching period datations

    Returns:
        Output file path on success, None on failure
    """
    exporter = PureNetworkXExporter(db_manager=db_manager)
    return exporter.export(
        graph=graph,
        output_path=output_path,
        site_name=site_name,
        title=title,
        use_extended_labels=use_extended_labels,
        include_periods=include_periods,
        apply_transitive_reduction=apply_transitive_reduction,
        reverse_epochs=reverse_epochs
    )
