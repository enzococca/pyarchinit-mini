"""
Validate Relationship Integrity Tool

Validates bidirectional integrity of stratigraphic relationships:
- Checks if relationships are reciprocal (US1: "Copre 2" ↔ US2: "Coperto da 1")
- Identifies orphaned references (US refers to non-existent units)
- Detects missing reciprocal relationships
- Validates consistency across the stratigraphic network
"""

import logging
from typing import Dict, Any, Optional, List, Set, Tuple
from sqlalchemy import text
from .base_tool import BaseTool, ToolDescription

logger = logging.getLogger(__name__)


# Reciprocal relationship mapping
RECIPROCAL_RELATIONSHIPS = {
    # Italian
    'Copre': 'Coperto da',
    'Coperto da': 'Copre',
    'Taglia': 'Tagliato da',
    'Tagliato da': 'Taglia',
    'Riempie': 'Riempito da',
    'Riempito da': 'Riempie',
    'Si lega a': 'Si lega a',  # Symmetric
    'Si appoggia a': 'Gli si appoggia',
    'Gli si appoggia': 'Si appoggia a',
    'Uguale a': 'Uguale a',  # Symmetric
    'Contemporaneo a': 'Contemporaneo a',  # Symmetric
    'Anteriore a': 'Posteriore a',
    'Posteriore a': 'Anteriore a',

    # English
    'Covers': 'Covered by',
    'Covered by': 'Covers',
    'Cuts': 'Cut by',
    'Cut by': 'Cuts',
    'Fills': 'Filled by',
    'Filled by': 'Fills',
    'Bonds with': 'Bonds with',  # Symmetric
    'Abuts': 'Abutted by',
    'Abutted by': 'Abuts',
    'Equal to': 'Equal to',  # Symmetric
    'Same as': 'Same as',  # Symmetric
    'Contemporary with': 'Contemporary with',  # Symmetric
    'Earlier than': 'Later than',
    'Later than': 'Earlier than',
}

# Symbol relationships (EM units)
SYMBOL_RECIPROCAL = {
    '>': '<',
    '<': '>',
    '>>': '<<',
    '<<': '>>',
}


class ValidateRelationshipIntegrityTool(BaseTool):
    """Validate bidirectional integrity of stratigraphic relationships"""

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="validate_relationship_integrity",
            description=(
                "Validate bidirectional integrity of stratigraphic relationships. "
                "Checks if relationships are reciprocal (e.g., US1: 'Copre 2' ↔ US2: 'Coperto da 1'). "
                "Identifies orphaned references and missing reciprocal relationships. "
                "Essential for ensuring Harris Matrix consistency."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "site_name": {
                        "type": "string",
                        "description": "Name of the archaeological site to validate"
                    },
                    "check_all_sites": {
                        "type": "boolean",
                        "description": "Check all sites in database (default: false)",
                        "default": False
                    },
                    "auto_suggest_fixes": {
                        "type": "boolean",
                        "description": "Automatically suggest fixes for broken relationships (default: true)",
                        "default": True
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Include detailed relationship analysis (default: false)",
                        "default": False
                    }
                },
                "required": [],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute relationship integrity validation"""
        try:
            site_name = arguments.get("site_name")
            check_all_sites = arguments.get("check_all_sites", False)
            auto_suggest_fixes = arguments.get("auto_suggest_fixes", True)
            verbose = arguments.get("verbose", False)

            if not site_name and not check_all_sites:
                return self._format_error(
                    "Either 'site_name' or 'check_all_sites=true' must be provided"
                )

            logger.info(
                f"Validating relationship integrity for "
                f"{'all sites' if check_all_sites else site_name}"
            )

            # Get validation report
            if check_all_sites:
                report = self._validate_all_sites(auto_suggest_fixes, verbose)
            else:
                report = self._validate_site(site_name, auto_suggest_fixes, verbose)

            if not report:
                return self._format_error(
                    f"Site not found or has no stratigraphic units: {site_name}"
                )

            return self._format_success(
                result=report,
                message=f"Integrity validation complete: {report['summary']['status']}"
            )

        except Exception as e:
            logger.error(f"Integrity validation error: {str(e)}", exc_info=True)
            return self._format_error(f"Integrity validation failed: {str(e)}")

    def _validate_site(
        self,
        site_name: str,
        auto_suggest_fixes: bool = True,
        verbose: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Validate relationship integrity for a single site

        Args:
            site_name: Name of the site
            auto_suggest_fixes: Generate fix suggestions
            verbose: Include detailed analysis

        Returns:
            Validation report dictionary
        """
        try:
            with self.db_session() as session:
                # Get all US for this site
                us_query = text("""
                    SELECT
                        us,
                        unita_tipo,
                        rapporti
                    FROM us_table
                    WHERE sito = :site_name
                    ORDER BY us
                """)
                us_results = session.execute(us_query, {"site_name": site_name}).fetchall()

                if not us_results:
                    return None

                # Build US map and relationship graph
                us_map = {}  # {us_number: {unita_tipo, rapporti, relationships: []}}
                all_us_numbers = set()

                for row in us_results:
                    us_number = str(row.us)
                    unita_tipo = row.unita_tipo or 'US'
                    rapporti = row.rapporti or ''

                    all_us_numbers.add(us_number)

                    # Parse relationships
                    relationships = self._parse_relationships(rapporti, unita_tipo)

                    us_map[us_number] = {
                        'unita_tipo': unita_tipo,
                        'rapporti': rapporti,
                        'relationships': relationships
                    }

                # Validate integrity
                issues = self._check_integrity(us_map, all_us_numbers)

                # Generate suggestions
                suggestions = []
                if auto_suggest_fixes and issues:
                    suggestions = self._generate_fixes(issues, us_map)

                # Calculate statistics
                total_relationships = sum(len(u['relationships']) for u in us_map.values())
                broken_relationships = len(issues.get('missing_reciprocal', []))
                orphaned_references = len(issues.get('orphaned_references', []))

                total_issues = broken_relationships + orphaned_references
                integrity_score = round(
                    ((total_relationships - total_issues) / total_relationships * 100), 2
                ) if total_relationships > 0 else 100.0

                report = {
                    'site_name': site_name,
                    'summary': {
                        'total_units': len(us_map),
                        'total_relationships': total_relationships,
                        'broken_relationships': broken_relationships,
                        'orphaned_references': orphaned_references,
                        'integrity_score': integrity_score,
                        'status': 'PASS' if total_issues == 0 else 'FAIL'
                    },
                    'statistics': {
                        'units_with_issues': len(set(
                            issue['from_us'] for issue in (
                                issues.get('missing_reciprocal', []) +
                                issues.get('orphaned_references', [])
                            )
                        ))
                    }
                }

                if total_issues > 0:
                    report['issues'] = issues

                if suggestions:
                    report['suggested_fixes'] = suggestions

                if verbose:
                    report['detailed_analysis'] = self._generate_detailed_analysis(
                        us_map, all_us_numbers
                    )

                return report

        except Exception as e:
            logger.error(f"Error validating site {site_name}: {str(e)}", exc_info=True)
            return None

    def _parse_relationships(
        self,
        rapporti: str,
        unita_tipo: str
    ) -> List[Dict[str, str]]:
        """
        Parse rapporti field into structured relationships

        Args:
            rapporti: Rapporti field content
            unita_tipo: Unit type (to determine if symbols or textual)

        Returns:
            List of relationship dictionaries with 'type' and 'target'
        """
        if not rapporti or not rapporti.strip():
            return []

        relationships = []

        # Split by comma or newline
        parts = [p.strip() for p in rapporti.replace('\n', ',').split(',') if p.strip()]

        for part in parts:
            # Try to match relationship patterns
            rel_type = None
            target = None

            # Check for symbols (>, <, >>, <<)
            for symbol in ['<<', '>>', '<', '>']:  # Check longer symbols first
                if part.startswith(symbol):
                    rel_type = symbol
                    target = part[len(symbol):].strip()
                    break

            # Check for textual relationships
            if not rel_type:
                for rel_text in RECIPROCAL_RELATIONSHIPS.keys():
                    if part.startswith(rel_text):
                        rel_type = rel_text
                        target = part[len(rel_text):].strip()
                        break

            if rel_type and target:
                relationships.append({
                    'type': rel_type,
                    'target': target
                })

        return relationships

    def _check_integrity(
        self,
        us_map: Dict[str, Dict[str, Any]],
        all_us_numbers: Set[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Check integrity of relationships across the network

        Args:
            us_map: Map of US numbers to their data
            all_us_numbers: Set of all valid US numbers

        Returns:
            Dictionary of issues categorized by type
        """
        issues = {
            'missing_reciprocal': [],
            'orphaned_references': [],
        }

        for us_number, us_data in us_map.items():
            for rel in us_data['relationships']:
                rel_type = rel['type']
                target = rel['target']

                # Check if target exists
                if target not in all_us_numbers:
                    issues['orphaned_references'].append({
                        'from_us': us_number,
                        'from_unita_tipo': us_data['unita_tipo'],
                        'relationship': rel_type,
                        'target_us': target,
                        'issue': f"Target US '{target}' does not exist"
                    })
                    continue

                # Check for reciprocal relationship
                reciprocal_type = self._get_reciprocal_type(rel_type)
                if not reciprocal_type:
                    # Unknown relationship type, skip
                    continue

                # Check if target has reciprocal relationship
                target_data = us_map.get(target)
                if not target_data:
                    continue

                has_reciprocal = any(
                    r['type'] == reciprocal_type and r['target'] == us_number
                    for r in target_data['relationships']
                )

                if not has_reciprocal:
                    issues['missing_reciprocal'].append({
                        'from_us': us_number,
                        'from_unita_tipo': us_data['unita_tipo'],
                        'relationship': rel_type,
                        'target_us': target,
                        'target_unita_tipo': target_data['unita_tipo'],
                        'expected_reciprocal': reciprocal_type,
                        'issue': f"US {target} should have '{reciprocal_type} {us_number}' but doesn't"
                    })

        return issues

    def _get_reciprocal_type(self, rel_type: str) -> Optional[str]:
        """Get the reciprocal relationship type"""
        # Check textual relationships
        if rel_type in RECIPROCAL_RELATIONSHIPS:
            return RECIPROCAL_RELATIONSHIPS[rel_type]

        # Check symbol relationships
        if rel_type in SYMBOL_RECIPROCAL:
            return SYMBOL_RECIPROCAL[rel_type]

        return None

    def _generate_fixes(
        self,
        issues: Dict[str, List[Dict[str, Any]]],
        us_map: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate suggested fixes for integrity issues"""
        fixes = []

        # Fix missing reciprocal relationships
        for issue in issues.get('missing_reciprocal', []):
            target_us = issue['target_us']
            target_data = us_map.get(target_us)

            if not target_data:
                continue

            # Generate new rapporti for target
            current_rapporti = target_data['rapporti']
            new_relationship = f"{issue['expected_reciprocal']} {issue['from_us']}"

            if current_rapporti and current_rapporti.strip():
                new_rapporti = f"{current_rapporti}, {new_relationship}"
            else:
                new_rapporti = new_relationship

            fixes.append({
                'issue_type': 'missing_reciprocal',
                'us': target_us,
                'unita_tipo': target_data['unita_tipo'],
                'action': 'add_relationship',
                'current_rapporti': current_rapporti,
                'suggested_rapporti': new_rapporti,
                'reason': f"Add reciprocal relationship for {issue['from_us']}: '{issue['relationship']} {target_us}'"
            })

        # Fix orphaned references
        for issue in issues.get('orphaned_references', []):
            from_us = issue['from_us']
            from_data = us_map.get(from_us)

            if not from_data:
                continue

            # Suggest removing the orphaned reference
            current_rapporti = from_data['rapporti']
            # Try to remove the specific relationship
            target_pattern = f"{issue['relationship']} {issue['target_us']}"
            new_rapporti = current_rapporti.replace(target_pattern, '').strip()
            # Clean up multiple commas
            while ',,' in new_rapporti:
                new_rapporti = new_rapporti.replace(',,', ',')
            new_rapporti = new_rapporti.strip(',').strip()

            fixes.append({
                'issue_type': 'orphaned_reference',
                'us': from_us,
                'unita_tipo': from_data['unita_tipo'],
                'action': 'remove_relationship',
                'current_rapporti': current_rapporti,
                'suggested_rapporti': new_rapporti,
                'reason': f"Remove reference to non-existent US '{issue['target_us']}'"
            })

        return fixes

    def _generate_detailed_analysis(
        self,
        us_map: Dict[str, Dict[str, Any]],
        all_us_numbers: Set[str]
    ) -> Dict[str, Any]:
        """Generate detailed analysis of relationship network"""
        # Calculate network metrics
        total_units = len(us_map)
        units_with_relationships = sum(1 for u in us_map.values() if u['relationships'])
        units_without_relationships = total_units - units_with_relationships

        # Calculate average connections per unit
        total_connections = sum(len(u['relationships']) for u in us_map.values())
        avg_connections = round(total_connections / total_units, 2) if total_units > 0 else 0

        # Find most connected units
        connected_units = sorted(
            [(us, len(data['relationships'])) for us, data in us_map.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Find isolated units
        isolated_units = [us for us, data in us_map.items() if not data['relationships']]

        return {
            'network_metrics': {
                'total_units': total_units,
                'units_with_relationships': units_with_relationships,
                'units_without_relationships': units_without_relationships,
                'total_connections': total_connections,
                'average_connections_per_unit': avg_connections
            },
            'most_connected_units': [
                {'us': us, 'connections': count} for us, count in connected_units
            ],
            'isolated_units': isolated_units[:20]  # Limit to 20
        }

    def _validate_all_sites(
        self,
        auto_suggest_fixes: bool = True,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Validate relationship integrity for all sites"""
        try:
            with self.db_session() as session:
                # Get all sites
                sites_query = text("SELECT DISTINCT sito FROM us_table ORDER BY sito")
                sites = session.execute(sites_query).fetchall()

                # Validate each site
                site_reports = {}
                total_broken = 0
                total_orphaned = 0
                total_relationships = 0

                for site_row in sites:
                    site_name = site_row.sito
                    report = self._validate_site(site_name, auto_suggest_fixes, verbose)

                    if report:
                        site_reports[site_name] = report
                        total_broken += report['summary']['broken_relationships']
                        total_orphaned += report['summary']['orphaned_references']
                        total_relationships += report['summary']['total_relationships']

                # Calculate global integrity
                total_issues = total_broken + total_orphaned
                global_integrity = round(
                    ((total_relationships - total_issues) / total_relationships * 100), 2
                ) if total_relationships > 0 else 100.0

                return {
                    'check_type': 'all_sites',
                    'total_sites': len(sites),
                    'global_summary': {
                        'total_relationships': total_relationships,
                        'broken_relationships': total_broken,
                        'orphaned_references': total_orphaned,
                        'integrity_score': global_integrity,
                        'status': 'PASS' if total_issues == 0 else 'FAIL'
                    },
                    'site_reports': site_reports
                }

        except Exception as e:
            logger.error(f"Error validating all sites: {str(e)}", exc_info=True)
            return {
                'error': str(e),
                'status': 'ERROR'
            }
