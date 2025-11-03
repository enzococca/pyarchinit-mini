"""
Generate Report Tool

Creates comprehensive reports and summaries about archaeological data:
- Site reports (details, statistics, US counts)
- US reports (by type, with/without relationships)
- Relationship reports (validation status, statistics)
- Support for multiple output formats (json, markdown, text)
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy import text, func
from datetime import datetime
from .base_tool import BaseTool, ToolDescription
from ...utils.relationship_validator import is_standard_unit, is_em_unit

logger = logging.getLogger(__name__)


class GenerateReportTool(BaseTool):
    """Generate comprehensive reports about archaeological data"""

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="generate_report",
            description=(
                "Generate comprehensive reports and summaries about archaeological data. "
                "Supports site reports, US reports, relationship reports, and validation summaries. "
                "Can output in JSON, Markdown, or plain text format. "
                "Use this for overview, statistics, and data integrity checks."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "enum": ["site", "us", "relationships", "summary", "validation"],
                        "description": (
                            "Type of report: "
                            "'site' = site details and statistics, "
                            "'us' = US units analysis by type, "
                            "'relationships' = relationship statistics, "
                            "'summary' = overall database summary, "
                            "'validation' = validation status report"
                        )
                    },
                    "site_name": {
                        "type": "string",
                        "description": "Specific site name (optional, for site-specific reports)"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["json", "markdown", "text"],
                        "default": "markdown",
                        "description": "Output format: json, markdown, or text"
                    },
                    "include_details": {
                        "type": "boolean",
                        "default": False,
                        "description": "Include detailed unit listings (default: false, stats only)"
                    },
                    "filter_unit_type": {
                        "type": "string",
                        "description": "Filter by unit type (US, USM, USVA, DOC, etc.)"
                    }
                },
                "required": ["report_type"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute report generation"""
        try:
            report_type = arguments.get("report_type")
            site_name = arguments.get("site_name")
            output_format = arguments.get("output_format", "markdown")
            include_details = arguments.get("include_details", False)
            filter_unit_type = arguments.get("filter_unit_type")

            logger.info(
                f"Generating {report_type} report "
                f"(format: {output_format}, site: {site_name or 'all'})"
            )

            # Generate appropriate report
            if report_type == "site":
                report_data = self._generate_site_report(site_name, include_details)
            elif report_type == "us":
                report_data = self._generate_us_report(site_name, filter_unit_type, include_details)
            elif report_type == "relationships":
                report_data = self._generate_relationship_report(site_name, include_details)
            elif report_type == "summary":
                report_data = self._generate_summary_report()
            elif report_type == "validation":
                report_data = self._generate_validation_report(site_name)
            else:
                return self._format_error(f"Unknown report type: {report_type}")

            if not report_data:
                return self._format_error("No data found for report")

            # Format output
            if output_format == "json":
                formatted_output = report_data
            elif output_format == "markdown":
                formatted_output = self._format_as_markdown(report_type, report_data)
            else:  # text
                formatted_output = self._format_as_text(report_type, report_data)

            return self._format_success(
                result=formatted_output,
                message=f"{report_type.capitalize()} report generated successfully"
            )

        except Exception as e:
            logger.error(f"Report generation error: {str(e)}", exc_info=True)
            return self._format_error(f"Report generation failed: {str(e)}")

    def _generate_site_report(
        self,
        site_name: Optional[str] = None,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """Generate site report with details and statistics"""
        with self.db_session() as session:
            if site_name:
                # Single site report
                site_query = text("""
                    SELECT
                        sito,
                        nazione,
                        regione,
                        comune,
                        provincia,
                        definizione_sito,
                        descrizione,
                        COUNT(DISTINCT us) as total_us
                    FROM us_table
                    WHERE sito = :site_name
                    GROUP BY sito, nazione, regione, comune, provincia, definizione_sito, descrizione
                """)
                site_result = session.execute(site_query, {"site_name": site_name}).fetchone()

                if not site_result:
                    return None

                # Get US type breakdown
                us_types_query = text("""
                    SELECT
                        COALESCE(unita_tipo, 'US') as unita_tipo,
                        COUNT(*) as count
                    FROM us_table
                    WHERE sito = :site_name
                    GROUP BY unita_tipo
                    ORDER BY count DESC
                """)
                us_types = session.execute(us_types_query, {"site_name": site_name}).fetchall()

                # Get relationship statistics
                rel_stats_query = text("""
                    SELECT
                        COUNT(*) as total_units,
                        SUM(CASE WHEN rapporti IS NOT NULL AND rapporti != '' THEN 1 ELSE 0 END) as with_relationships,
                        SUM(CASE WHEN rapporti IS NULL OR rapporti = '' THEN 1 ELSE 0 END) as without_relationships
                    FROM us_table
                    WHERE sito = :site_name
                """)
                rel_stats = session.execute(rel_stats_query, {"site_name": site_name}).fetchone()

                report = {
                    "site_name": site_result.sito,
                    "location": {
                        "nazione": site_result.nazione,
                        "regione": site_result.regione,
                        "comune": site_result.comune,
                        "provincia": site_result.provincia
                    },
                    "definition": site_result.definizione_sito,
                    "description": site_result.descrizione,
                    "statistics": {
                        "total_us": site_result.total_us,
                        "us_by_type": {row.unita_tipo: row.count for row in us_types},
                        "relationships": {
                            "with_relationships": rel_stats.with_relationships,
                            "without_relationships": rel_stats.without_relationships,
                            "coverage_percentage": round(
                                (rel_stats.with_relationships / rel_stats.total_units * 100), 2
                            ) if rel_stats.total_units > 0 else 0
                        }
                    },
                    "generated_at": datetime.now().isoformat()
                }

                if include_details:
                    # Get list of US
                    us_list_query = text("""
                        SELECT
                            us,
                            COALESCE(unita_tipo, 'US') as unita_tipo,
                            d_stratigrafica,
                            rapporti
                        FROM us_table
                        WHERE sito = :site_name
                        ORDER BY us
                    """)
                    us_list = session.execute(us_list_query, {"site_name": site_name}).fetchall()
                    report["us_details"] = [
                        {
                            "us": row.us,
                            "unita_tipo": row.unita_tipo,
                            "description": row.d_stratigrafica,
                            "has_relationships": bool(row.rapporti and row.rapporti.strip())
                        }
                        for row in us_list
                    ]

                return report

            else:
                # All sites summary
                sites_query = text("""
                    SELECT
                        sito,
                        COUNT(DISTINCT us) as total_us,
                        MIN(anno_scavo) as first_excavation,
                        MAX(anno_scavo) as last_excavation
                    FROM us_table
                    GROUP BY sito
                    ORDER BY total_us DESC
                """)
                sites = session.execute(sites_query).fetchall()

                return {
                    "total_sites": len(sites),
                    "sites": [
                        {
                            "name": row.sito,
                            "total_us": row.total_us,
                            "excavation_years": f"{row.first_excavation}-{row.last_excavation}" if row.first_excavation else "N/A"
                        }
                        for row in sites
                    ],
                    "generated_at": datetime.now().isoformat()
                }

    def _generate_us_report(
        self,
        site_name: Optional[str] = None,
        filter_unit_type: Optional[str] = None,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """Generate US analysis report by type"""
        with self.db_session() as session:
            # Build query
            where_clauses = []
            params = {}

            if site_name:
                where_clauses.append("sito = :site_name")
                params["site_name"] = site_name

            if filter_unit_type:
                where_clauses.append("unita_tipo = :unit_type")
                params["unit_type"] = filter_unit_type

            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            # Get counts by unit type
            type_query = text(f"""
                SELECT
                    COALESCE(unita_tipo, 'US') as unita_tipo,
                    COUNT(*) as count,
                    SUM(CASE WHEN rapporti IS NOT NULL AND rapporti != '' THEN 1 ELSE 0 END) as with_relationships,
                    SUM(CASE WHEN rapporti IS NULL OR rapporti = '' THEN 1 ELSE 0 END) as without_relationships
                FROM us_table
                {where_sql}
                GROUP BY unita_tipo
                ORDER BY count DESC
            """)
            type_results = session.execute(type_query, params).fetchall()

            # Categorize by standard vs EM
            standard_units = []
            em_units = []
            unknown_units = []

            for row in type_results:
                unit_info = {
                    "unita_tipo": row.unita_tipo,
                    "count": row.count,
                    "with_relationships": row.with_relationships,
                    "without_relationships": row.without_relationships,
                    "relationship_coverage": round(
                        (row.with_relationships / row.count * 100), 2
                    ) if row.count > 0 else 0
                }

                if is_standard_unit(row.unita_tipo):
                    unit_info["category"] = "standard"
                    standard_units.append(unit_info)
                elif is_em_unit(row.unita_tipo):
                    unit_info["category"] = "em"
                    em_units.append(unit_info)
                else:
                    unit_info["category"] = "unknown"
                    unknown_units.append(unit_info)

            report = {
                "filter": {
                    "site": site_name or "all",
                    "unit_type": filter_unit_type or "all"
                },
                "summary": {
                    "total_units": sum(row.count for row in type_results),
                    "standard_units_count": sum(u["count"] for u in standard_units),
                    "em_units_count": sum(u["count"] for u in em_units),
                    "unit_types_found": len(type_results)
                },
                "standard_units": standard_units,
                "em_units": em_units,
                "generated_at": datetime.now().isoformat()
            }

            if unknown_units:
                report["unknown_units"] = unknown_units

            if include_details and filter_unit_type:
                # Get detailed unit list for specific type
                detail_query = text(f"""
                    SELECT
                        us,
                        d_stratigrafica,
                        rapporti
                    FROM us_table
                    {where_sql}
                    ORDER BY us
                """)
                details = session.execute(detail_query, params).fetchall()
                report["unit_details"] = [
                    {
                        "us": row.us,
                        "description": row.d_stratigrafica,
                        "relationships": row.rapporti or "None"
                    }
                    for row in details
                ]

            return report

    def _generate_relationship_report(
        self,
        site_name: Optional[str] = None,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """Generate relationship statistics report"""
        with self.db_session() as session:
            where_sql = "WHERE sito = :site_name" if site_name else ""
            params = {"site_name": site_name} if site_name else {}

            # Overall statistics
            stats_query = text(f"""
                SELECT
                    COUNT(*) as total_units,
                    SUM(CASE WHEN rapporti IS NOT NULL AND rapporti != '' THEN 1 ELSE 0 END) as with_relationships,
                    SUM(CASE WHEN rapporti IS NULL OR rapporti = '' THEN 1 ELSE 0 END) as without_relationships
                FROM us_table
                {where_sql}
            """)
            stats = session.execute(stats_query, params).fetchone()

            # Relationship types distribution
            rel_types_query = text(f"""
                SELECT
                    us,
                    COALESCE(unita_tipo, 'US') as unita_tipo,
                    rapporti
                FROM us_table
                {where_sql}
                AND rapporti IS NOT NULL
                AND rapporti != ''
            """)
            rel_results = session.execute(rel_types_query, params).fetchall()

            # Analyze relationship formats
            textual_count = 0
            symbol_count = 0
            mixed_count = 0
            relationship_keywords = {
                'textual': ['Copre', 'Coperto', 'Taglia', 'Si lega', 'Riempie', 'Covers', 'Cuts', 'Fills'],
                'symbols': ['>', '<', '>>', '<<']
            }

            for row in rel_results:
                rapporti = row.rapporti or ""
                has_textual = any(kw in rapporti for kw in relationship_keywords['textual'])
                has_symbols = any(sym in rapporti for sym in relationship_keywords['symbols'])

                if has_textual and has_symbols:
                    mixed_count += 1
                elif has_textual:
                    textual_count += 1
                elif has_symbols:
                    symbol_count += 1

            report = {
                "filter": {
                    "site": site_name or "all"
                },
                "statistics": {
                    "total_units": stats.total_units,
                    "with_relationships": stats.with_relationships,
                    "without_relationships": stats.without_relationships,
                    "coverage_percentage": round(
                        (stats.with_relationships / stats.total_units * 100), 2
                    ) if stats.total_units > 0 else 0
                },
                "relationship_formats": {
                    "textual_only": textual_count,
                    "symbols_only": symbol_count,
                    "mixed": mixed_count
                },
                "generated_at": datetime.now().isoformat()
            }

            if include_details and stats.without_relationships > 0:
                # List units without relationships
                no_rel_query = text(f"""
                    SELECT
                        us,
                        COALESCE(unita_tipo, 'US') as unita_tipo,
                        d_stratigrafica
                    FROM us_table
                    {where_sql}
                    {'AND' if where_sql else 'WHERE'} (rapporti IS NULL OR rapporti = '')
                    ORDER BY us
                """)
                no_rel_results = session.execute(no_rel_query, params).fetchall()
                report["units_without_relationships"] = [
                    {
                        "us": row.us,
                        "unita_tipo": row.unita_tipo,
                        "description": row.d_stratigrafica
                    }
                    for row in no_rel_results
                ]

            return report

    def _generate_summary_report(self) -> Dict[str, Any]:
        """Generate overall database summary report"""
        with self.db_session() as session:
            # Site count
            site_count_query = text("SELECT COUNT(DISTINCT sito) as count FROM us_table")
            site_count = session.execute(site_count_query).scalar()

            # Total US
            us_count_query = text("SELECT COUNT(*) as count FROM us_table")
            us_count = session.execute(us_count_query).scalar()

            # US by type
            type_query = text("""
                SELECT
                    COALESCE(unita_tipo, 'US') as unita_tipo,
                    COUNT(*) as count
                FROM us_table
                GROUP BY unita_tipo
                ORDER BY count DESC
            """)
            types = session.execute(type_query).fetchall()

            # Relationship coverage
            rel_query = text("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN rapporti IS NOT NULL AND rapporti != '' THEN 1 ELSE 0 END) as with_rel
                FROM us_table
            """)
            rel_stats = session.execute(rel_query).fetchone()

            # Period distribution
            period_query = text("""
                SELECT
                    periodo_iniziale,
                    COUNT(*) as count
                FROM us_table
                WHERE periodo_iniziale IS NOT NULL AND periodo_iniziale != ''
                GROUP BY periodo_iniziale
                ORDER BY count DESC
                LIMIT 10
            """)
            periods = session.execute(period_query).fetchall()

            return {
                "database_summary": {
                    "total_sites": site_count,
                    "total_us": us_count,
                    "relationship_coverage": {
                        "with_relationships": rel_stats.with_rel,
                        "without_relationships": rel_stats.total - rel_stats.with_rel,
                        "percentage": round((rel_stats.with_rel / rel_stats.total * 100), 2) if rel_stats.total > 0 else 0
                    }
                },
                "unit_types": {row.unita_tipo: row.count for row in types},
                "top_periods": [{"period": row.periodo_iniziale, "count": row.count} for row in periods],
                "generated_at": datetime.now().isoformat()
            }

    def _generate_validation_report(
        self,
        site_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate validation status report"""
        with self.db_session() as session:
            where_sql = "WHERE sito = :site_name" if site_name else ""
            params = {"site_name": site_name} if site_name else {}

            # Get all units for validation
            query = text(f"""
                SELECT
                    us,
                    COALESCE(unita_tipo, 'US') as unita_tipo,
                    rapporti
                FROM us_table
                {where_sql}
                ORDER BY us
            """)
            units = session.execute(query, params).fetchall()

            # Quick validation summary
            total = len(units)
            without_relationships = sum(1 for u in units if not u.rapporti or not u.rapporti.strip())
            with_relationships = total - without_relationships

            return {
                "filter": {
                    "site": site_name or "all"
                },
                "validation_summary": {
                    "total_units": total,
                    "with_relationships": with_relationships,
                    "without_relationships": without_relationships,
                    "relationship_coverage": round(
                        (with_relationships / total * 100), 2
                    ) if total > 0 else 0
                },
                "recommendations": [
                    f"{without_relationships} units need stratigraphic relationships" if without_relationships > 0 else "All units have relationships",
                    "Use 'validate_relationship_format' tool for detailed format validation",
                    "Use 'validate_stratigraphic_relationships' tool for data integrity check"
                ],
                "generated_at": datetime.now().isoformat()
            }

    def _format_as_markdown(self, report_type: str, data: Dict[str, Any]) -> str:
        """Format report data as Markdown"""
        lines = []
        lines.append(f"# {report_type.upper()} REPORT")
        lines.append("")
        lines.append(f"**Generated at**: {data.get('generated_at', 'N/A')}")
        lines.append("")

        if report_type == "site":
            if "site_name" in data:
                # Single site report
                lines.append(f"## Site: {data['site_name']}")
                lines.append("")
                lines.append(f"**Location**: {data['location']['comune']}, {data['location']['regione']}, {data['location']['nazione']}")
                lines.append(f"**Definition**: {data.get('definition', 'N/A')}")
                lines.append(f"**Description**: {data.get('description', 'N/A')}")
                lines.append("")
                lines.append("### Statistics")
                lines.append(f"- Total US: {data['statistics']['total_us']}")
                lines.append("")
                lines.append("**US by Type:**")
                for utype, count in data['statistics']['us_by_type'].items():
                    lines.append(f"  - {utype}: {count}")
                lines.append("")
                lines.append("**Relationships:**")
                rel = data['statistics']['relationships']
                lines.append(f"  - With relationships: {rel['with_relationships']}")
                lines.append(f"  - Without relationships: {rel['without_relationships']}")
                lines.append(f"  - Coverage: {rel['coverage_percentage']}%")

                if "us_details" in data:
                    lines.append("")
                    lines.append("### US Details")
                    for us in data['us_details']:
                        status = "✓" if us['has_relationships'] else "✗"
                        lines.append(f"- {status} {us['unita_tipo']}_{us['us']}: {us['description']}")
            else:
                # All sites summary
                lines.append(f"## Total Sites: {data['total_sites']}")
                lines.append("")
                for site in data['sites']:
                    lines.append(f"### {site['name']}")
                    lines.append(f"- US: {site['total_us']}")
                    lines.append(f"- Years: {site['excavation_years']}")
                    lines.append("")

        elif report_type == "us":
            lines.append(f"## Filter: {data['filter']['site']} / {data['filter']['unit_type']}")
            lines.append("")
            lines.append("### Summary")
            lines.append(f"- Total units: {data['summary']['total_units']}")
            lines.append(f"- Standard units (US/USM): {data['summary']['standard_units_count']}")
            lines.append(f"- EM units: {data['summary']['em_units_count']}")
            lines.append("")

            if data.get('standard_units'):
                lines.append("### Standard Units (US/USM)")
                for unit in data['standard_units']:
                    lines.append(f"- **{unit['unita_tipo']}**: {unit['count']} units, {unit['relationship_coverage']}% with relationships")
                lines.append("")

            if data.get('em_units'):
                lines.append("### Extended Matrix Units")
                for unit in data['em_units']:
                    lines.append(f"- **{unit['unita_tipo']}**: {unit['count']} units, {unit['relationship_coverage']}% with relationships")

        elif report_type == "relationships":
            lines.append(f"## Filter: {data['filter']['site']}")
            lines.append("")
            lines.append("### Statistics")
            stats = data['statistics']
            lines.append(f"- Total units: {stats['total_units']}")
            lines.append(f"- With relationships: {stats['with_relationships']} ({stats['coverage_percentage']}%)")
            lines.append(f"- Without relationships: {stats['without_relationships']}")
            lines.append("")
            lines.append("### Relationship Formats")
            formats = data['relationship_formats']
            lines.append(f"- Textual only: {formats['textual_only']}")
            lines.append(f"- Symbols only: {formats['symbols_only']}")
            lines.append(f"- Mixed: {formats['mixed']}")

            if "units_without_relationships" in data:
                lines.append("")
                lines.append("### Units Without Relationships")
                for unit in data['units_without_relationships']:
                    lines.append(f"- {unit['unita_tipo']}_{unit['us']}: {unit['description']}")

        elif report_type == "summary":
            summ = data['database_summary']
            lines.append("## Database Summary")
            lines.append(f"- Total sites: {summ['total_sites']}")
            lines.append(f"- Total US: {summ['total_us']}")
            lines.append(f"- Relationship coverage: {summ['relationship_coverage']['percentage']}%")
            lines.append("")
            lines.append("### Unit Types")
            for utype, count in data['unit_types'].items():
                lines.append(f"- {utype}: {count}")
            lines.append("")
            lines.append("### Top Periods")
            for period in data['top_periods']:
                lines.append(f"- {period['period']}: {period['count']}")

        elif report_type == "validation":
            lines.append(f"## Filter: {data['filter']['site']}")
            lines.append("")
            summ = data['validation_summary']
            lines.append("### Validation Summary")
            lines.append(f"- Total units: {summ['total_units']}")
            lines.append(f"- With relationships: {summ['with_relationships']}")
            lines.append(f"- Without relationships: {summ['without_relationships']}")
            lines.append(f"- Coverage: {summ['relationship_coverage']}%")
            lines.append("")
            lines.append("### Recommendations")
            for rec in data['recommendations']:
                lines.append(f"- {rec}")

        return "\n".join(lines)

    def _format_as_text(self, report_type: str, data: Dict[str, Any]) -> str:
        """Format report data as plain text"""
        # For simplicity, use markdown format without symbols
        markdown = self._format_as_markdown(report_type, data)
        # Remove markdown formatting
        text = markdown.replace("#", "").replace("**", "").replace("*", "")
        return text
