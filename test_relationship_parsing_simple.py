#!/usr/bin/env python3
"""
Test relationship parsing from rapporti field
"""

# Test the parsing logic
rapporti_str = "Copre 1002, Taglia 1005, Si appoggia a 1001"

print("Testing relationship parsing...")
print(f"Input: {rapporti_str}")
print("\nParsed relationships:")

parts = rapporti_str.split(',')
for part in parts:
    part = part.strip()
    if not part:
        continue

    # Split "Copre 1002" into ["Copre", "1002"]
    tokens = part.split()
    if len(tokens) >= 2:
        rel_type = ' '.join(tokens[:-1])  # Everything except last token
        target_us = tokens[-1]  # Last token is US number

        print(f"  Type: '{rel_type}', Target: '{target_us}'")

print("\n✓ Parsing test completed!")
