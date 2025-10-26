#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verify GraphML Periods - Check that the GraphML file contains all 8 period rows
"""

import xml.etree.ElementTree as ET

def verify_graphml_periods():
    """Verify the GraphML file has all 8 period rows"""

    print("=" * 80)
    print("VERIFY GRAPHML PERIODS")
    print("=" * 80)
    print()

    graphml_path = "/Users/enzo/Desktop/dom_zu_lund_harris_matrix.graphml"

    try:
        # Parse GraphML
        tree = ET.parse(graphml_path)
        root = tree.getroot()

        # GraphML namespace
        ns = {'': 'http://graphml.graphdrawing.org/xmlns',
              'y': 'http://www.yworks.com/xml/graphml'}

        print(f"GraphML file: {graphml_path}")
        print()

        # Find all NodeLabel elements with row IDs (period labels)
        # These are the period row labels in the table structure
        period_labels = []

        for label in root.findall('.//{http://www.yworks.com/xml/graphml}NodeLabel'):
            # Check if this is a row label (has y:ModelParameter with y:RowNodeLabelModelParameter)
            model_param = label.find('{http://www.yworks.com/xml/graphml}ModelParameter/{http://www.yworks.com/xml/graphml}RowNodeLabelModelParameter')
            if model_param is not None:
                # Extract the row ID
                row_id = model_param.get('id')
                if row_id and row_id.startswith('row_'):
                    # Extract period name from row ID
                    period_name = row_id.replace('row_', '').replace('_', ' ')
                    period_text = label.text or ''
                    if period_text and period_text not in period_labels:
                        period_labels.append(period_text)

        print(f"Period rows found: {len(period_labels)}")
        print()

        if period_labels:
            print("PERIOD ROWS IN GRAPHML:")
            print("-" * 80)
            for i, period in enumerate(period_labels, 1):
                print(f"  {i}. {period}")
            print()

        # Normalize period labels (strip whitespace and commas)
        normalized_labels = [p.strip().strip(',').strip() for p in period_labels]

        # Verify expected periods
        expected_periods = [
            'Geologisch',
            'Vorgeschichte bis Wikingerzeit',
            'Wikingerzeit',
            'Hochmittelalter',
            'Hochmittelalter bis Spätmittelalter',
            'Spätmittelalter',
            'Neuzeit',
            'Non datato'
        ]

        print("VERIFICATION:")
        print("-" * 80)
        all_present = True
        for expected in expected_periods:
            if expected in normalized_labels:
                print(f"  ✅ {expected}")
            else:
                print(f"  ❌ MISSING: {expected}")
                all_present = False

        print()

        if all_present and len(period_labels) == 8:
            print("✅ SUCCESS: All 8 expected periods are present in GraphML!")
        elif len(period_labels) == 8 and not all_present:
            print(f"⚠️  WARNING: Found 8 periods but some names don't match expected")
        else:
            print(f"❌ FAILED: Expected 8 periods, found {len(period_labels)}")

        print()
        print("=" * 80)

    except FileNotFoundError:
        print(f"❌ File not found: {graphml_path}")
        print()
        print("Please run test_sfdp_export.py first:")
        print("  .venv/bin/python test_sfdp_export.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    verify_graphml_periods()