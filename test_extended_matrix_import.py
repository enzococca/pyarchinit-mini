#!/usr/bin/env python3
"""
Test script for Extended Matrix Excel Parser
=============================================

Tests the import of Metro C - Amba Aradam Excel file.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pyarchinit_mini.services.extended_matrix_excel_parser import import_extended_matrix_excel
from pyarchinit_mini.database.connection import DatabaseConnection


def main():
    """Test Extended Matrix import."""

    excel_path = "/Users/enzo/Downloads/Telegram Desktop/Unita_Stratigrafiche_MetroC_AmbaAradam_Completo.xlsx"
    site_name = "Metro C - Amba Aradam"

    # Use project database instead of default
    db_path = "/Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db"

    print("="*70)
    print("Testing Extended Matrix Excel Parser")
    print("="*70)
    print(f"Excel file: {excel_path}")
    print(f"Site: {site_name}")
    print(f"Database: {db_path}")
    print("="*70)
    print()

    # Check if file exists
    if not Path(excel_path).exists():
        print(f"✗ Error: Excel file not found: {excel_path}")
        print("Please update the path in this script.")
        sys.exit(1)

    try:
        # Create database connection for project database
        connection_string = f"sqlite:///{db_path}"
        db_connection = DatabaseConnection(connection_string)

        # Run import
        stats = import_extended_matrix_excel(
            excel_path=excel_path,
            site_name=site_name,
            generate_graphml=True,
            db_connection=db_connection
        )

        # Display results
        print("\n" + "="*70)
        print("Test Results")
        print("="*70)
        print(f"✓ Test completed successfully!")
        print(f"  - US created: {stats['us_created']}")
        print(f"  - US updated: {stats['us_updated']}")
        print(f"  - Relationships: {stats['relationships_created']}")

        if 'graphml_path' in stats:
            print(f"  - GraphML: {stats['graphml_path']}")

        if stats.get('errors'):
            print(f"\n⚠ Warnings/Errors: {len(stats['errors'])}")
            for error in stats['errors'][:5]:
                print(f"  - {error}")

        print("="*70)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
