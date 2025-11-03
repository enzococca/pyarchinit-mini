"""
Validate Relationship Format Tool

Validates that stratigraphic units use the correct relationship format:
- US/USM standard units → textual relationships ONLY
- EM units (USVA, SF, DOC, etc.) → symbols ONLY
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy import text
from .base_tool import BaseTool, ToolDescription
from ...utils.relationship_validator import (
    validate_unit_relationships,
    get_validation_summary,
    suggest_correct_format,
    is_standard_unit,
    is_em_unit,
)

logger = logging.getLogger(__name__)


class ValidateRelationshipFormatTool(BaseTool):
    """Validate that relationship formats match unit types"""

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="validate_relationship_format",
            description=(
                "Validate that stratigraphic units use the correct relationship format. "
                "US/USM must use textual relationships (Copre, Taglia, etc.). "
                "EM units (USVA, SF, DOC, etc.) must use symbols (>, <, >>, <<). "
                "Returns detailed validation report with errors and suggestions."
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
                    "include_suggestions": {
                        "type": "boolean",
                        "description": "Include correction suggestions for errors (default: true)",
                        "default": True
                    }
                },
                "required": [],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute relationship format validation"""
        try:
            site_name = arguments.get("site_name")
            check_all_sites = arguments.get("check_all_sites", False)
            include_suggestions = arguments.get("include_suggestions", True)

            if not site_name and not check_all_sites:
                return self._format_error(
                    "Either 'site_name' or 'check_all_sites=true' must be provided"
                )

            logger.info(
                f"Validating relationship formats for "
                f"{'all sites' if check_all_sites else site_name}"
            )

            # Get validation report
            if check_all_sites:
                report = self._validate_all_sites(include_suggestions)
            else:
                report = self._validate_site(site_name, include_suggestions)

            if not report:
                return self._format_error(
                    f"Site not found or has no stratigraphic units: {site_name}"
                )

            return self._format_success(
                result=report,
                message=f"Validation complete: {report['summary']['status']}"
            )

        except Exception as e:
            logger.error(f"Validation error: {str(e)}", exc_info=True)
            return self._format_error(f"Validation failed: {str(e)}")

    def _validate_site(
        self,
        site_name: str,
        include_suggestions: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Validate relationship formats for a single site

        Args:
            site_name: Name of the site
            include_suggestions: Include correction suggestions

        Returns:
            Validation report dictionary
        """
        try:
            with self.db_session() as session:
                # Get all US for this site with unita_tipo and rapporti
                us_query = text("""
                    SELECT
                        id_us,
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

                # Validate each US
                valid_count = 0
                invalid_count = 0
                error_details = {}
                unit_type_stats = {
                    'standard': {'total': 0, 'valid': 0, 'invalid': 0},
                    'em': {'total': 0, 'valid': 0, 'invalid': 0}
                }

                for us_row in us_results:
                    us_number = us_row.us
                    unita_tipo = us_row.unita_tipo or 'US'  # Default to US if not set
                    rapporti = us_row.rapporti or ''

                    # Track unit type stats
                    if is_standard_unit(unita_tipo):
                        unit_type_stats['standard']['total'] += 1
                    elif is_em_unit(unita_tipo):
                        unit_type_stats['em']['total'] += 1

                    # Skip if no relationships
                    if not rapporti.strip():
                        valid_count += 1
                        if is_standard_unit(unita_tipo):
                            unit_type_stats['standard']['valid'] += 1
                        elif is_em_unit(unita_tipo):
                            unit_type_stats['em']['valid'] += 1
                        continue

                    # Validate relationships
                    is_valid, errors = validate_unit_relationships(unita_tipo, rapporti)

                    if is_valid:
                        valid_count += 1
                        if is_standard_unit(unita_tipo):
                            unit_type_stats['standard']['valid'] += 1
                        elif is_em_unit(unita_tipo):
                            unit_type_stats['em']['valid'] += 1
                    else:
                        invalid_count += 1
                        if is_standard_unit(unita_tipo):
                            unit_type_stats['standard']['invalid'] += 1
                        elif is_em_unit(unita_tipo):
                            unit_type_stats['em']['invalid'] += 1

                        # Add error details
                        error_info = {
                            'us': us_number,
                            'unita_tipo': unita_tipo,
                            'rapporti': rapporti,
                            'errors': errors
                        }

                        # Add suggestions if requested
                        if include_suggestions:
                            suggestions = []
                            for error in errors:
                                # Extract wrong relationship from error message
                                if "Found:" in error:
                                    wrong_rel = error.split("Found:")[1].split(".")[0].strip().strip("'\"")
                                    suggestion = suggest_correct_format(unita_tipo, wrong_rel)
                                    if suggestion:
                                        suggestions.append(suggestion)
                            if suggestions:
                                error_info['suggestions'] = suggestions

                        error_details[f"{unita_tipo}_{us_number}"] = error_info

                # Build report
                total = len(us_results)
                summary = get_validation_summary(
                    total, valid_count, invalid_count, error_details
                )

                report = {
                    'site_name': site_name,
                    'summary': summary,
                    'unit_type_statistics': unit_type_stats
                }

                if invalid_count > 0:
                    report['invalid_units'] = error_details
                    report['recommendations'] = self._generate_recommendations(
                        invalid_count,
                        total,
                        unit_type_stats
                    )

                return report

        except Exception as e:
            logger.error(f"Error validating site {site_name}: {str(e)}", exc_info=True)
            return None

    def _validate_all_sites(
        self,
        include_suggestions: bool = True
    ) -> Dict[str, Any]:
        """
        Validate relationship formats for all sites

        Args:
            include_suggestions: Include correction suggestions

        Returns:
            Validation report dictionary
        """
        try:
            with self.db_session() as session:
                # Get all sites
                sites_query = text("SELECT DISTINCT sito FROM us_table ORDER BY sito")
                sites = session.execute(sites_query).fetchall()

                # Validate each site
                site_reports = {}
                total_valid = 0
                total_invalid = 0
                total_units = 0

                for site_row in sites:
                    site_name = site_row.sito
                    report = self._validate_site(site_name, include_suggestions)

                    if report:
                        site_reports[site_name] = report
                        total_valid += report['summary']['valid_units']
                        total_invalid += report['summary']['invalid_units']
                        total_units += report['summary']['total_units']

                # Build global report
                return {
                    'check_type': 'all_sites',
                    'total_sites': len(sites),
                    'total_units': total_units,
                    'total_valid': total_valid,
                    'total_invalid': total_invalid,
                    'validation_rate': round((total_valid / total_units * 100), 2) if total_units > 0 else 0,
                    'site_reports': site_reports,
                    'status': 'PASS' if total_invalid == 0 else 'FAIL'
                }

        except Exception as e:
            logger.error(f"Error validating all sites: {str(e)}", exc_info=True)
            return {
                'error': str(e),
                'status': 'ERROR'
            }

    def _generate_recommendations(
        self,
        invalid_count: int,
        total_count: int,
        unit_type_stats: Dict[str, Dict[str, int]]
    ) -> list[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        # Overall recommendation
        percentage = (invalid_count / total_count * 100) if total_count > 0 else 0

        if percentage > 50:
            recommendations.append(
                f"CRITICAL: {percentage:.1f}% of units have incorrect relationship formats. "
                "This requires immediate attention."
            )
        elif percentage > 20:
            recommendations.append(
                f"WARNING: {percentage:.1f}% of units have incorrect relationship formats. "
                "Review and correct these units."
            )
        else:
            recommendations.append(
                f"Minor issues: {percentage:.1f}% of units have incorrect formats. "
                "Review individual errors below."
            )

        # Standard units recommendations
        if unit_type_stats['standard']['invalid'] > 0:
            recommendations.append(
                f"Standard units (US/USM): {unit_type_stats['standard']['invalid']} invalid. "
                "These MUST use textual relationships (Copre, Taglia, Si lega a, etc.)"
            )

        # EM units recommendations
        if unit_type_stats['em']['invalid'] > 0:
            recommendations.append(
                f"EM units (USVA, SF, DOC, etc.): {unit_type_stats['em']['invalid']} invalid. "
                "These MUST use symbols (>, <, >>, <<)"
            )

        recommendations.append(
            "Use the 'manage_data' tool with operation='update' to fix incorrect relationships."
        )

        recommendations.append(
            "Refer to STRATIGRAPHIC_RELATIONSHIPS_BY_UNIT_TYPE.md for complete rules."
        )

        return recommendations
