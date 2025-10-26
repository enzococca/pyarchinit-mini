#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verify GraphML Reverse Periods - Check period order in reverse epochs file
"""

import xml.etree.ElementTree as ET

def verify_graphml_reverse():
    """Verify the reverse epochs GraphML file"""

    print("=" * 80)
    print("VERIFY GRAPHML REVERSE EPOCHS")
    print("=" * 80)
    print()

    graphml_path = "/Users/enzo/Desktop/dom_zu_lund_harris_matrix_REVERSE.graphml"

    try:
        # Parse GraphML
        tree = ET.parse(graphml_path)
        root = tree.getroot()

        print(f"GraphML file: {graphml_path}")
        print()

        # Find all NodeLabel elements with row IDs (period labels)
        period_labels = []

        for label in root.findall('.//{http://www.yworks.com/xml/graphml}NodeLabel'):
            # Check if this is a row label
            model_param = label.find('{http://www.yworks.com/xml/graphml}ModelParameter/{http://www.yworks.com/xml/graphml}RowNodeLabelModelParameter')
            if model_param is not None:
                row_id = model_param.get('id')
                if row_id and row_id.startswith('row_'):
                    period_text = label.text or ''
                    if period_text and period_text not in period_labels:
                        period_labels.append(period_text)

        # Normalize
        normalized_labels = [p.strip().strip(',').strip() for p in period_labels]

        print(f"Period rows found: {len(normalized_labels)}")
        print()

        if normalized_labels:
            print("PERIOD ROWS (in GraphML order):")
            print("-" * 80)
            for i, period in enumerate(normalized_labels, 1):
                print(f"  {i}. {period}")
            print()

        # Expected reverse order (newest → oldest)
        expected_reverse = [
            'Non datato',
            'Neuzeit',
            'Spätmittelalter',
            'Hochmittelalter bis Spätmittelalter',
            'Hochmittelalter',
            'Wikingerzeit',
            'Vorgeschichte bis Wikingerzeit',
            'Geologisch'
        ]

        print("EXPECTED ORDER (newest → oldest):")
        print("-" * 80)
        for i, period in enumerate(expected_reverse, 1):
            print(f"  {i}. {period}")
        print()

        # Check if order matches
        print("VERIFICATION:")
        print("-" * 80)
        if normalized_labels == expected_reverse:
            print("✅ SUCCESS: Periods are in correct REVERSE order!")
        else:
            print("⚠️  Order differs from expected")
            print()
            print("Differences:")
            for i, (actual, expected) in enumerate(zip(normalized_labels, expected_reverse), 1):
                if actual == expected:
                    print(f"  {i}. ✅ {actual}")
                else:
                    print(f"  {i}. ❌ Got '{actual}', expected '{expected}'")

        # Check if all periods are present
        all_present = all(p in normalized_labels for p in expected_reverse)
        if all_present and len(normalized_labels) == 8:
            print()
            print("✅ All 8 periods are present")
        else:
            print()
            print(f"❌ Expected 8 periods, found {len(normalized_labels)}")

        print()
        print("=" * 80)

    except FileNotFoundError:
        print(f"❌ File not found: {graphml_path}")
        print()
        print("Please run test_sfdp_export_reverse.py first:")
        print("  .venv/bin/python test_sfdp_export_reverse.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    verify_graphml_reverse()