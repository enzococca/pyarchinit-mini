"""
Validate Stratigraphy Tool - Stratigraphic Relationship Validator for MCP

This tool enables AI assistants to validate and fix stratigraphic relationships.
Features:
- Detect stratigraphic paradoxes (contradictory relationships)
- Find cycles in Harris Matrix (temporal paradoxes)
- Check for missing reciprocal relationships
- Validate chronological consistency with periodization data
- Auto-fix missing reciprocal relationships
- Works with both Italian and English relationship types
"""

import logging
import os
from typing import Dict, Any, Optional, List
from sqlalchemy import Table, MetaData
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.utils.stratigraphic_validator import StratigraphicValidator

logger = logging.getLogger(__name__)


def validate_stratigraphy(
    site: Optional[str] = None,
    area: Optional[str] = None,
    check_chronology: bool = False,
    auto_fix: bool = False
) -> dict:
    """
    Validate stratigraphic relationships for archaeological units (US).

    This tool detects and optionally fixes:
    - Paradoxes (contradictory relationships like "US 1 copre 2" and "US 1 coperto da 2")
    - Cycles (temporal paradoxes like US1 → US2 → US3 → US1)
    - Missing reciprocal relationships (if US 1 copre 2, then US 2 should have coperto da 1)
    - Chronological inconsistencies (if periodization data available)
    - References to non-existent US

    Args:
        site: Specific site to validate (None = all sites)
        area: Specific area to validate (requires site, None = all areas)
        check_chronology: If True, validates chronological consistency using periodization data
        auto_fix: If True, automatically fixes missing reciprocal relationships
                 (does NOT fix paradoxes - those require manual intervention)

    Returns:
        dict: Validation report with structure:
        {
            "success": True | False,
            "valid": True | False,  # True if no errors found
            "units_checked": <number of US validated>,
            "relationships_found": <total relationships>,
            "errors": [
                "Error description 1",
                "Error description 2",
                ...
            ],
            "error_count": <number of errors>,
            "fixes_applied": [  # Only if auto_fix=True
                {
                    "us": <US number>,
                    "sito": <site>,
                    "area": <area>,
                    "action": "added_reciprocal_relationship",
                    "details": "..."
                }
            ],
            "fixes_count": <number of fixes applied>,
            "warnings": [...]  # Non-critical issues
        }

    Examples:
        # Validate all stratigraphic relationships
        result = validate_stratigraphy()

        # Validate specific site
        result = validate_stratigraphy(site="Pompei")

        # Validate and auto-fix missing reciprocals
        result = validate_stratigraphy(
            site="Tempio della Fortuna",
            auto_fix=True
        )

        # Full validation with chronology check
        result = validate_stratigraphy(
            site="Pompei",
            area="1",
            check_chronology=True,
            auto_fix=True
        )

    Notes:
        - Paradoxes MUST be fixed manually (conflicting relationships)
        - Cycles indicate serious logical errors in the stratigraphy
        - Missing reciprocals can be auto-fixed safely
        - Chronology check requires periodization data (datazioni_table)
        - Supports both Italian and English relationship types
    """
    try:
        # Get database connection - use config default if DATABASE_URL not set
        from pyarchinit_mini.mcp_server.config import _get_default_database_url
        database_url = os.getenv("DATABASE_URL") or _get_default_database_url()
        db_connection = DatabaseConnection(database_url)
        db_manager = DatabaseManager(db_connection)
        engine = db_connection.engine
        metadata = MetaData()

        # Build query filters
        filters = []
        if site:
            filters.append(f"sito = '{site}'")
        if area and site:
            filters.append(f"area = '{area}'")

        where_clause = " WHERE " + " AND ".join(filters) if filters else ""

        # Query US data
        us_table = Table('us_table', metadata, autoload_with=engine)
        with engine.connect() as conn:
            query = f"SELECT * FROM us_table{where_clause}"
            result = conn.execute(us_table.select())
            us_list = [dict(row._mapping) for row in result]

        if not us_list:
            site_info = f" for site '{site}'" if site else ""
            area_info = f" area '{area}'" if area else ""
            return {
                "success": True,
                "valid": True,
                "message": f"No US found{site_info}{area_info}",
                "units_checked": 0,
                "relationships_found": 0,
                "errors": [],
                "error_count": 0
            }

        # Query periodization data if needed for chronology check
        periodization_list = None
        if check_chronology:
            datazioni_table = Table('datazioni_table', metadata, autoload_with=engine)
            with engine.connect() as conn:
                query = f"SELECT * FROM datazioni_table{where_clause}"
                result = conn.execute(datazioni_table.select())
                periodization_list = [dict(row._mapping) for row in result]

        # Create validator and run validation
        validator = StratigraphicValidator()
        report = validator.get_validation_report(us_list, periodization_list)

        # Prepare base response
        response = {
            "success": True,
            "valid": report['valid'],
            "units_checked": report['units_checked'],
            "relationships_found": report['relationships_found'],
            "errors": report['errors'],
            "error_count": report['error_count'],
            "has_chronology_check": report.get('has_chronology', False)
        }

        # Categorize errors for better reporting
        paradoxes = []
        cycles = []
        chronology_errors = []
        other_errors = []

        for error in report['errors']:
            if 'Paradox' in error or 'paradox' in error.lower():
                paradoxes.append(error)
            elif 'cycle' in error.lower() or 'Temporal paradox' in error:
                cycles.append(error)
            elif 'cronologic' in error.lower():
                chronology_errors.append(error)
            else:
                other_errors.append(error)

        response['error_categories'] = {
            "paradoxes": paradoxes,
            "cycles": cycles,
            "chronology_errors": chronology_errors,
            "other_errors": other_errors
        }

        # Generate and apply fixes if requested
        if auto_fix:
            fixes = validator.generate_relationship_fixes(us_list)
            fixes_applied = []
            warnings = []

            # Apply relationship updates (missing reciprocals)
            for fix in fixes['updates']:
                try:
                    with engine.begin() as conn:
                        update_query = us_table.update().where(
                            (us_table.c.sito == fix['sito']) &
                            (us_table.c.area == fix['area']) &
                            (us_table.c.us == fix['us'])
                        ).values(rapporti=fix['new_value'])

                        result = conn.execute(update_query)

                        if result.rowcount > 0:
                            fixes_applied.append({
                                "us": fix['us'],
                                "sito": fix['sito'],
                                "area": fix['area'],
                                "action": "added_reciprocal_relationship",
                                "details": fix['reason'],
                                "old_value": fix['old_value'],
                                "new_value": fix['new_value']
                            })
                except Exception as e:
                    logger.error(f"Error applying fix to US {fix['us']}: {e}")
                    warnings.append(f"Failed to fix US {fix['us']}: {str(e)}")

            # Warn about missing US (don't auto-create them)
            if fixes['creates']:
                for create_fix in fixes['creates']:
                    warnings.append(
                        f"US {create_fix['us']} does not exist but is referenced by US {create_fix['created_from']} - "
                        f"Manual creation recommended"
                    )

            response['fixes_applied'] = fixes_applied
            response['fixes_count'] = len(fixes_applied)
            response['warnings'] = warnings
            response['missing_us_count'] = len(fixes['creates'])

            # Re-validate after fixes
            if fixes_applied:
                # Reload US data
                with engine.connect() as conn:
                    query = f"SELECT * FROM us_table{where_clause}"
                    result = conn.execute(us_table.select())
                    us_list_updated = [dict(row._mapping) for row in result]

                # Validate again
                validator_recheck = StratigraphicValidator()
                report_after = validator_recheck.get_validation_report(
                    us_list_updated,
                    periodization_list
                )

                response['after_fixes'] = {
                    "valid": report_after['valid'],
                    "error_count": report_after['error_count'],
                    "errors": report_after['errors'],
                    "improvement": report['error_count'] - report_after['error_count']
                }

        # Generate summary message
        if response['valid']:
            response['message'] = f"✓ All {response['units_checked']} units validated successfully - no errors found"
        else:
            error_summary = []
            if paradoxes:
                error_summary.append(f"{len(paradoxes)} paradox(es)")
            if cycles:
                error_summary.append(f"{len(cycles)} cycle(s)")
            if chronology_errors:
                error_summary.append(f"{len(chronology_errors)} chronology error(s)")
            if other_errors:
                error_summary.append(f"{len(other_errors)} other error(s)")

            response['message'] = f"✗ Found {response['error_count']} error(s): {', '.join(error_summary)}"

            if auto_fix and response.get('fixes_count', 0) > 0:
                response['message'] += f"\n  Applied {response['fixes_count']} automatic fix(es)"

        return response

    except Exception as e:
        logger.error(f"Error validating stratigraphy: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to validate stratigraphy: {str(e)}"
        }


def get_relationship_statistics(site: Optional[str] = None) -> dict:
    """
    Get statistics about stratigraphic relationships.

    Args:
        site: Specific site (None = all sites)

    Returns:
        dict: Statistics with relationship type counts, most connected US, etc.
    """
    try:
        db_manager = DatabaseManager()
        engine = db_manager.engine
        metadata = MetaData()

        # Build query filter
        where_clause = f" WHERE sito = '{site}'" if site else ""

        # Query US data
        us_table = Table('us_table', metadata, autoload_with=engine)
        with engine.connect() as conn:
            query = f"SELECT * FROM us_table{where_clause}"
            result = conn.execute(us_table.select())
            us_list = [dict(row._mapping) for row in result]

        if not us_list:
            return {
                "success": True,
                "message": "No US found",
                "total_us": 0
            }

        # Analyze relationships
        validator = StratigraphicValidator()
        relationship_types = {}
        us_connection_count = {}

        for us_data in us_list:
            us_number = us_data.get('us')
            rapporti = us_data.get('rapporti', '')

            if not rapporti:
                us_connection_count[us_number] = 0
                continue

            relationships = validator.parse_relationships(us_number, rapporti)
            us_connection_count[us_number] = len(relationships)

            for rel_type, target_us in relationships:
                if rel_type not in relationship_types:
                    relationship_types[rel_type] = 0
                relationship_types[rel_type] += 1

        # Find most connected US
        most_connected = sorted(
            us_connection_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            "success": True,
            "total_us": len(us_list),
            "us_with_relationships": sum(1 for count in us_connection_count.values() if count > 0),
            "total_relationships": sum(us_connection_count.values()),
            "relationship_types": relationship_types,
            "most_connected_us": [
                {"us": us_num, "connections": count}
                for us_num, count in most_connected
            ],
            "average_connections": sum(us_connection_count.values()) / len(us_list) if us_list else 0
        }

    except Exception as e:
        logger.error(f"Error getting relationship statistics: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get relationship statistics: {str(e)}"
        }
