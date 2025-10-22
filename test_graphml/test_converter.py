#!/usr/bin/env python3
"""
Test script for GraphML converter
"""
import sys
sys.path.insert(0, '/Users/enzo/Documents/pyarchinit-mini-desk')

from pyarchinit_mini.graphml_converter import (
    convert_dot_to_graphml,
    convert_dot_content_to_graphml,
    GraphMLConverterOptions
)

def test_file_conversion():
    """Test file-based conversion"""
    print("=" * 60)
    print("Test 1: File-based conversion")
    print("=" * 60)

    input_file = "/Users/enzo/Documents/pyarchinit-mini-desk/test_graphml/test_harris.dot"
    output_file = "/Users/enzo/Documents/pyarchinit-mini-desk/test_graphml/test_harris.graphml"

    options = GraphMLConverterOptions()
    options.verbose = True

    success = convert_dot_to_graphml(
        input_file,
        output_file,
        title="Test Site - Harris Matrix",
        reverse_epochs=False,
        options=options
    )

    if success:
        print(f"\n✓ Conversion successful!")
        print(f"  Input: {input_file}")
        print(f"  Output: {output_file}")

        # Check output file size
        import os
        size = os.path.getsize(output_file)
        print(f"  Output file size: {size} bytes")

        # Show first few lines
        print(f"\n  First 20 lines of output:")
        with open(output_file, 'r') as f:
            for i, line in enumerate(f):
                if i < 20:
                    print(f"    {line.rstrip()}")
                else:
                    break
    else:
        print("\n✗ Conversion failed!")
        return False

    return True

def test_string_conversion():
    """Test string-based conversion"""
    print("\n" + "=" * 60)
    print("Test 2: String-based conversion")
    print("=" * 60)

    dot_content = """digraph SimpleTest {
    "US 100" [label="US 100", shape=box];
    "US 101" [label="US 101", shape=box];
    "US 100" -> "US 101" [label="Covers"];
}"""

    graphml_content = convert_dot_content_to_graphml(
        dot_content,
        title="Simple Test",
        reverse_epochs=False
    )

    if graphml_content:
        print(f"\n✓ String conversion successful!")
        print(f"  GraphML content length: {len(graphml_content)} characters")
        print(f"\n  First 500 characters:")
        print(graphml_content[:500])
    else:
        print("\n✗ String conversion failed!")
        return False

    return True

if __name__ == '__main__':
    print("\nGraphML Converter Test Suite")
    print("=" * 60)

    try:
        test1_passed = test_file_conversion()
        test2_passed = test_string_conversion()

        print("\n" + "=" * 60)
        print("Test Results:")
        print("=" * 60)
        print(f"  File conversion: {'✓ PASSED' if test1_passed else '✗ FAILED'}")
        print(f"  String conversion: {'✓ PASSED' if test2_passed else '✗ FAILED'}")

        if test1_passed and test2_passed:
            print("\n✓ All tests passed!")
            sys.exit(0)
        else:
            print("\n✗ Some tests failed!")
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
