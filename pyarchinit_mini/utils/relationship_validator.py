"""
Relationship Validator Utility

Validates stratigraphic relationships based on unit type (unita_tipo).
Enforces the dual system: textual relationships for US/USM, symbols for EM units.
"""

import re
from typing import List, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# UNIT TYPE CONSTANTS
# ============================================================================

# Standard stratigraphic units (use textual relationships ONLY)
STANDARD_UNIT_TYPES = {
    'US',   # Unità Stratigrafica
    'USM',  # Unità Stratigrafica Muraria
    'SU',   # Stratigraphic Unit (English)
    'WSU',  # Wall Stratigraphic Unit (English)
    'UST',  # Unità Stratigrafica Tomba
}

# Extended Matrix units (use symbols ONLY)
EM_UNIT_TYPES_SINGLE_SYMBOL = {
    'USVA',  # Negative interface type A
    'USVB',  # Negative interface type B
    'USVC',  # Negative interface type C
    'SF',    # Foundation structure
    'SFA',   # Foundation structure type A
    'CON',   # Context node
}

EM_UNIT_TYPES_DOUBLE_SYMBOL = {
    'DOC',       # Document
    'property',  # Property node
    'Extractor', # Extractor node
    'Combiner',  # Combiner node
}

# All EM unit types
EM_UNIT_TYPES = EM_UNIT_TYPES_SINGLE_SYMBOL | EM_UNIT_TYPES_DOUBLE_SYMBOL


# ============================================================================
# RELATIONSHIP CONSTANTS
# ============================================================================

# Textual relationships (Italian)
TEXTUAL_RELATIONSHIPS_IT = {
    'Copre',
    'Coperto da',
    'Taglia',
    'Tagliato da',
    'Riempie',
    'Riempito da',
    'Si lega a',
    'Si appoggia a',
    'Gli si appoggia',
    'Uguale a',
    'Contemporaneo a',
    'Anteriore a',
    'Posteriore a',
}

# Textual relationships (English)
TEXTUAL_RELATIONSHIPS_EN = {
    'Covers',
    'Covered by',
    'Cuts',
    'Cut by',
    'Fills',
    'Filled by',
    'Bonds with',
    'Abuts',
    'Abutted by',
    'Equal to',
    'Same as',
    'Contemporary with',
    'Earlier than',
    'Later than',
}

# All textual relationships
TEXTUAL_RELATIONSHIPS = TEXTUAL_RELATIONSHIPS_IT | TEXTUAL_RELATIONSHIPS_EN

# Symbol relationships
SYMBOL_RELATIONSHIPS = {
    '>',   # Single arrow (stratigraphic connection)
    '<',   # Single arrow reverse
    '>>',  # Double arrow (non-stratigraphic connection)
    '<<',  # Double arrow reverse
}


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def is_standard_unit(unita_tipo: str) -> bool:
    """
    Check if unit type is a standard stratigraphic unit (US/USM)

    Args:
        unita_tipo: Unit type string

    Returns:
        True if standard unit type
    """
    return unita_tipo in STANDARD_UNIT_TYPES


def is_em_unit(unita_tipo: str) -> bool:
    """
    Check if unit type is an Extended Matrix unit

    Args:
        unita_tipo: Unit type string

    Returns:
        True if EM unit type
    """
    return unita_tipo in EM_UNIT_TYPES


def uses_single_symbols(unita_tipo: str) -> bool:
    """
    Check if unit type uses single symbols (>, <)

    Args:
        unita_tipo: Unit type string

    Returns:
        True if uses single symbols
    """
    return unita_tipo in EM_UNIT_TYPES_SINGLE_SYMBOL


def uses_double_symbols(unita_tipo: str) -> bool:
    """
    Check if unit type uses double symbols (>>, <<)

    Args:
        unita_tipo: Unit type string

    Returns:
        True if uses double symbols
    """
    return unita_tipo in EM_UNIT_TYPES_DOUBLE_SYMBOL


def parse_rapporti_field(rapporti: str) -> List[str]:
    """
    Parse rapporti field into individual relationships

    Args:
        rapporti: Rapporti field content

    Returns:
        List of individual relationship strings
    """
    if not rapporti or not rapporti.strip():
        return []

    # Split by comma or newline
    relationships = re.split(r'[,\n]', rapporti)

    # Strip whitespace and filter empty strings
    return [rel.strip() for rel in relationships if rel.strip()]


def is_textual_relationship(relationship: str) -> bool:
    """
    Check if a relationship string is textual

    Args:
        relationship: Relationship string (e.g., "Copre 123", "Covered by 456")

    Returns:
        True if textual relationship
    """
    # Check if starts with any known textual relationship
    for rel_type in TEXTUAL_RELATIONSHIPS:
        if relationship.startswith(rel_type):
            return True
    return False


def is_symbol_relationship(relationship: str) -> bool:
    """
    Check if a relationship string uses symbols

    Args:
        relationship: Relationship string (e.g., "> 123", "<< 456")

    Returns:
        True if symbol relationship
    """
    # Check if starts with any known symbol
    for symbol in SYMBOL_RELATIONSHIPS:
        if relationship.startswith(symbol):
            return True
    return False


def extract_relationship_type(relationship: str) -> Optional[str]:
    """
    Extract relationship type from relationship string

    Args:
        relationship: Relationship string

    Returns:
        Relationship type (textual or symbol) or None
    """
    # Check textual first
    for rel_type in TEXTUAL_RELATIONSHIPS:
        if relationship.startswith(rel_type):
            return rel_type

    # Check symbols
    for symbol in SYMBOL_RELATIONSHIPS:
        if relationship.startswith(symbol):
            return symbol

    return None


def validate_unit_relationships(
    unita_tipo: str,
    rapporti: str
) -> Tuple[bool, List[str]]:
    """
    Validate that relationships are appropriate for unit type

    Args:
        unita_tipo: Unit type (US, USM, USVA, DOC, etc.)
        rapporti: Rapporti field content

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if not unita_tipo:
        errors.append("Unit type (unita_tipo) is missing")
        return False, errors

    # Parse relationships
    relationships = parse_rapporti_field(rapporti)

    if not relationships:
        # No relationships - this is checked by validate_stratigraphic_relationships_tool
        return True, []

    # Validate based on unit type
    if is_standard_unit(unita_tipo):
        # Standard units MUST use textual relationships ONLY
        for rel in relationships:
            if is_symbol_relationship(rel):
                errors.append(
                    f"Standard unit type '{unita_tipo}' MUST NOT use symbols. "
                    f"Found: '{rel}'. Use textual relationships (Copre, Taglia, etc.)"
                )
            elif not is_textual_relationship(rel):
                # Unknown relationship format
                errors.append(
                    f"Unknown relationship format for standard unit: '{rel}'"
                )

    elif is_em_unit(unita_tipo):
        # EM units MUST use symbols ONLY
        for rel in relationships:
            if is_textual_relationship(rel):
                errors.append(
                    f"EM unit type '{unita_tipo}' MUST NOT use textual relationships. "
                    f"Found: '{rel}'. Use symbols (>, <, >>, <<)"
                )
            elif not is_symbol_relationship(rel):
                # Unknown relationship format
                errors.append(
                    f"Unknown relationship format for EM unit: '{rel}'"
                )

        # Additional validation for symbol type
        if uses_single_symbols(unita_tipo):
            # Should prefer >, < but can also use >>, << for connections to non-stratigraphic units
            for rel in relationships:
                if rel.startswith('>>') or rel.startswith('<<'):
                    # This is allowed but log as info
                    logger.debug(
                        f"{unita_tipo} uses double symbols (>>, <<) - "
                        f"likely connecting to non-stratigraphic unit"
                    )

        elif uses_double_symbols(unita_tipo):
            # Should use ONLY >>, <<
            for rel in relationships:
                if rel.startswith('>') and not rel.startswith('>>'):
                    errors.append(
                        f"Non-stratigraphic unit '{unita_tipo}' should use double symbols (>>, <<). "
                        f"Found single symbol: '{rel}'"
                    )
                elif rel.startswith('<') and not rel.startswith('<<'):
                    errors.append(
                        f"Non-stratigraphic unit '{unita_tipo}' should use double symbols (>>, <<). "
                        f"Found single symbol: '{rel}'"
                    )

    else:
        errors.append(f"Unknown unit type: '{unita_tipo}'")

    is_valid = len(errors) == 0
    return is_valid, errors


def get_validation_summary(
    total_units: int,
    valid_units: int,
    invalid_units: int,
    error_details: Dict[str, List[str]]
) -> Dict[str, any]:
    """
    Generate validation summary report

    Args:
        total_units: Total number of units checked
        valid_units: Number of valid units
        invalid_units: Number of invalid units
        error_details: Dictionary mapping US number to list of errors

    Returns:
        Summary dictionary
    """
    return {
        'total_units': total_units,
        'valid_units': valid_units,
        'invalid_units': invalid_units,
        'validation_rate': round((valid_units / total_units * 100), 2) if total_units > 0 else 0,
        'error_details': error_details,
        'status': 'PASS' if invalid_units == 0 else 'FAIL'
    }


# ============================================================================
# RECOMMENDATION FUNCTIONS
# ============================================================================

def suggest_correct_format(unita_tipo: str, wrong_relationship: str) -> Optional[str]:
    """
    Suggest correct format for a wrong relationship

    Args:
        unita_tipo: Unit type
        wrong_relationship: The incorrect relationship string

    Returns:
        Suggestion string or None
    """
    if is_standard_unit(unita_tipo):
        # Standard unit using symbols - suggest textual
        if wrong_relationship.startswith('>'):
            return "Use textual: 'Copre [US_NUMBER]' or 'Covers [US_NUMBER]'"
        elif wrong_relationship.startswith('<'):
            return "Use textual: 'Coperto da [US_NUMBER]' or 'Covered by [US_NUMBER]'"
        elif wrong_relationship.startswith('>>'):
            return "Use textual relationships (Copre, Taglia, Si lega a, etc.)"
        elif wrong_relationship.startswith('<<'):
            return "Use textual relationships (Coperto da, Tagliato da, etc.)"

    elif is_em_unit(unita_tipo):
        # EM unit using textual - suggest symbols
        if 'Copre' in wrong_relationship or 'Covers' in wrong_relationship:
            return "Use symbol: '> [US_NUMBER]'"
        elif 'Coperto da' in wrong_relationship or 'Covered by' in wrong_relationship:
            return "Use symbol: '< [US_NUMBER]'"
        elif 'Taglia' in wrong_relationship or 'Cuts' in wrong_relationship:
            return "Use symbol: '> [US_NUMBER]'"
        elif uses_double_symbols(unita_tipo):
            return "Use double symbols: '>> [US_NUMBER]' or '<< [US_NUMBER]'"
        else:
            return "Use single symbols: '> [US_NUMBER]' or '< [US_NUMBER]'"

    return None
