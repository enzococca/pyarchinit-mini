"""
Validate Stratigraphic Relationships Tool

Validates that all stratigraphic units (US) have proper stratigraphic relationships.
Critical for maintaining archaeological data integrity.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from .base_tool import BaseTool, ToolDescription

logger = logging.getLogger(__name__)


class ValidateStratigraphicRelationshipsTool(BaseTool):
    """Validate stratigraphic relationships and find US without relationships"""

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="validate_stratigraphic_relationships",
            description=(
                "Validate stratigraphic relationships for a site. "
                "Finds stratigraphic units (US) that lack relationships, which is critical "
                "for maintaining data integrity in archaeological excavations. "
                "Returns detailed report with statistics and recommendations."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "site_name": {
                        "type": "string",
                        "description": "Name of the archaeological site to validate"
                    },
                    "include_details": {
                        "type": "boolean",
                        "description": "Include detailed information for each US without relationships (default: true)",
                        "default": True
                    }
                },
                "required": ["site_name"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute stratigraphic relationships validation"""
        try:
            site_name = arguments.get("site_name")
            include_details = arguments.get("include_details", True)

            if not site_name:
                return self._format_error("Site name is required")

            logger.info(f"Validating stratigraphic relationships for site: {site_name}")

            # Get validation report
            report = self._validate_relationships(site_name, include_details)

            if not report:
                return self._format_error(f"Site not found or has no stratigraphic units: {site_name}")

            return self._format_success(
                result=report,
                message=f"Validation complete for {site_name}: {report['total_us']} US analyzed"
            )

        except Exception as e:
            logger.error(f"Validation error: {str(e)}", exc_info=True)
            return self._format_error(f"Validation failed: {str(e)}")

    def _validate_relationships(
        self,
        site_name: str,
        include_details: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Validate stratigraphic relationships for a site

        Args:
            site_name: Name of the site
            include_details: Include detailed information for each US

        Returns:
            Validation report dictionary
        """
        try:
            with self.db_session() as session:
                # Get all US for this site
                us_query = text("""
                    SELECT
                        id_us,
                        us,
                        unita_tipo,
                        descrizione,
                        rapporti
                    FROM us_table
                    WHERE sito = :site_name
                    ORDER BY us
                """)

                us_results = session.execute(us_query, {"site_name": site_name}).fetchall()

                if not us_results:
                    return None

                # Get relationships from harris_matrix_table
                harris_query = text("""
                    SELECT DISTINCT
                        CASE
                            WHEN us_sopra = :us_number THEN us_sotto
                            WHEN us_sotto = :us_number THEN us_sopra
                        END as related_us
                    FROM harris_matrix_table
                    WHERE sito = :site_name
                        AND (us_sopra = :us_number OR us_sotto = :us_number)
                """)

                # Get relationships from us_relationships_table
                relationships_query = text("""
                    SELECT DISTINCT
                        CASE
                            WHEN us_from = :us_number THEN us_to
                            WHEN us_to = :us_number THEN us_from
                        END as related_us
                    FROM us_relationships_table
                    WHERE sito = :site_name
                        AND (us_from = :us_number OR us_to = :us_number)
                """)

                # Analyze each US
                us_with_relationships = []
                us_without_relationships = []

                for us_row in us_results:
                    us_number = us_row.us
                    rapporti_text = us_row.rapporti or ""

                    # Check harris_matrix_table
                    harris_rels = session.execute(
                        harris_query,
                        {"site_name": site_name, "us_number": us_number}
                    ).fetchall()

                    # Check us_relationships_table
                    structured_rels = session.execute(
                        relationships_query,
                        {"site_name": site_name, "us_number": us_number}
                    ).fetchall()

                    # Check rapporti field
                    has_rapporti_text = bool(rapporti_text.strip())

                    # Count total relationships
                    total_relationships = (
                        len(harris_rels) +
                        len(structured_rels) +
                        (1 if has_rapporti_text else 0)
                    )

                    if total_relationships > 0:
                        us_with_relationships.append({
                            "us": us_number,
                            "harris_matrix_count": len(harris_rels),
                            "structured_count": len(structured_rels),
                            "has_rapporti_text": has_rapporti_text
                        })
                    else:
                        us_info = {
                            "us": us_number,
                            "tipo": us_row.unita_tipo or "Non specificato",
                        }

                        if include_details:
                            us_info["descrizione"] = (
                                us_row.descrizione[:100] + "..."
                                if us_row.descrizione and len(us_row.descrizione) > 100
                                else us_row.descrizione or "Nessuna descrizione"
                            )

                        us_without_relationships.append(us_info)

                # Calculate statistics
                total_us = len(us_results)
                with_relationships = len(us_with_relationships)
                without_relationships = len(us_without_relationships)
                percentage_with = (with_relationships / total_us * 100) if total_us > 0 else 0
                percentage_without = (without_relationships / total_us * 100) if total_us > 0 else 0

                # Build report
                report = {
                    "site_name": site_name,
                    "total_us": total_us,
                    "us_with_relationships": with_relationships,
                    "us_without_relationships": without_relationships,
                    "percentage_with_relationships": round(percentage_with, 2),
                    "percentage_without_relationships": round(percentage_without, 2),
                    "validation_status": "PASS" if without_relationships == 0 else "WARNING",
                    "recommendations": self._generate_recommendations(
                        without_relationships,
                        total_us
                    )
                }

                # Add US without relationships
                if us_without_relationships:
                    report["us_without_relationships_list"] = us_without_relationships

                # Add summary statistics
                if with_relationships > 0:
                    total_harris = sum(u["harris_matrix_count"] for u in us_with_relationships)
                    total_structured = sum(u["structured_count"] for u in us_with_relationships)

                    report["relationship_statistics"] = {
                        "total_harris_matrix_entries": total_harris,
                        "total_structured_entries": total_structured,
                        "us_with_rapporti_text": sum(
                            1 for u in us_with_relationships if u["has_rapporti_text"]
                        )
                    }

                return report

        except Exception as e:
            logger.error(f"Error validating relationships: {str(e)}", exc_info=True)
            return None

    def _generate_recommendations(
        self,
        without_relationships: int,
        total_us: int
    ) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        if without_relationships == 0:
            recommendations.append(
                "All stratigraphic units have relationships. Data integrity is good."
            )
        elif without_relationships < total_us * 0.1:  # Less than 10%
            recommendations.append(
                f"Minor issues: {without_relationships} US without relationships. "
                "Review these units to add missing stratigraphic connections."
            )
        elif without_relationships < total_us * 0.3:  # Less than 30%
            recommendations.append(
                f"Moderate issues: {without_relationships} US without relationships. "
                "This may affect Harris Matrix generation. "
                "Prioritize adding relationships for these units."
            )
        else:
            recommendations.append(
                f"Major issues: {without_relationships} US without relationships. "
                "This significantly impacts stratigraphic analysis. "
                "Urgent review and relationship documentation required."
            )

        recommendations.append(
            "Use the 'create_us_relationships' tool to add missing relationships."
        )

        return recommendations
