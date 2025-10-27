#!/usr/bin/env python3
"""
CLI tool for importing Extended Matrix Excel files
===================================================

Usage:
    python -m pyarchinit_mini.cli.extended_matrix_import \\
        --excel path/to/file.xlsx \\
        --site "Site Name" \\
        --graphml
"""

import argparse
import sys
from pathlib import Path

from pyarchinit_mini.services.extended_matrix_excel_parser import import_extended_matrix_excel


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Import Extended Matrix Excel file into PyArchInit-Mini',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Import Excel and generate GraphML
  python -m pyarchinit_mini.cli.extended_matrix_import \\
      --excel MetroC_AmbaAradam.xlsx \\
      --site "Metro C - Amba Aradam" \\
      --graphml

  # Import without GraphML generation
  python -m pyarchinit_mini.cli.extended_matrix_import \\
      --excel data.xlsx \\
      --site "My Site"

  # Specify GraphML output path
  python -m pyarchinit_mini.cli.extended_matrix_import \\
      --excel data.xlsx \\
      --site "My Site" \\
      --graphml \\
      --output custom_name.graphml
        '''
    )

    parser.add_argument(
        '--excel', '-e',
        required=True,
        help='Path to Extended Matrix Excel file'
    )

    parser.add_argument(
        '--site', '-s',
        required=True,
        help='Archaeological site name'
    )

    parser.add_argument(
        '--graphml', '-g',
        action='store_true',
        help='Generate GraphML file for Extended Matrix visualization'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output path for GraphML file (optional)'
    )

    args = parser.parse_args()

    # Validate Excel file exists
    excel_path = Path(args.excel)
    if not excel_path.exists():
        print(f"✗ Error: Excel file not found: {excel_path}")
        sys.exit(1)

    if not excel_path.suffix.lower() in ['.xlsx', '.xls']:
        print(f"✗ Error: File must be Excel format (.xlsx or .xls)")
        sys.exit(1)

    try:
        # Run import
        stats = import_extended_matrix_excel(
            excel_path=str(excel_path),
            site_name=args.site,
            generate_graphml=args.graphml
        )

        # Success
        sys.exit(0)

    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
