#!/usr/bin/env python3
"""
Create a comprehensive Harris Matrix test file with 20 US of various Extended Matrix types
"""
import pandas as pd

# Define 20 US with various Extended Matrix types
nodes_data = {
    'us_number': [
        '1001', '1002', '1003', '1004', '1005',
        '1006', '1007', '1008', '1009', '1010',
        '2001', '2002', '2003', '2004', '2005',
        '3001', '3002', '3003', '3004', '3005'
    ],
    'unit_type': [
        'US',        # 1001 - Standard stratigraphic unit
        'US',        # 1002
        'US',        # 1003
        'USM',       # 1004 - Mural unit
        'USM',       # 1005
        'USVA',      # 1006 - Virtual type A (negative feature)
        'US',        # 1007
        'US',        # 1008
        'SF',        # 1009 - Special find
        'US',        # 1010
        'US',        # 2001
        'USVB',      # 2002 - Virtual type B
        'US',        # 2003
        'TU',        # 2004 - Topographic unit
        'US',        # 2005
        'Extractor', # 3001 - Aggregation node
        'US',        # 3002
        'VSF',       # 3003 - Virtual special find
        'Combiner',  # 3004 - Combination node
        'DOC'        # 3005 - Document
    ],
    'description': [
        'Topsoil layer',
        'Brown silty deposit',
        'Stone collapse layer',
        'North wall foundation',
        'East wall facing',
        'Foundation trench cut',
        'Fill of foundation trench',
        'Clay floor surface',
        'Bronze coin hoard',
        'Charcoal-rich deposit',
        'Sandy deposit',
        'Pit cut (virtual)',
        'Pit fill',
        'Ground surface level',
        'Building debris',
        'Medieval phase aggregate',
        'Mortar floor',
        'Ceramic assemblage (virtual)',
        'Medieval features combination',
        'Site plan drawing'
    ],
    'area': [
        'Area A', 'Area A', 'Area A', 'Area A', 'Area A',
        'Area A', 'Area A', 'Area A', 'Area A', 'Area A',
        'Area B', 'Area B', 'Area B', 'Area B', 'Area B',
        'Area C', 'Area C', 'Area C', 'Area C', 'Area C'
    ],
    'period': [
        'Medievale', 'Medievale', 'Medievale', 'Romano Imperiale', 'Romano Imperiale',
        'Romano Imperiale', 'Romano Imperiale', 'Romano Repubblicano', 'Medievale', 'Romano Repubblicano',
        'Medievale', 'Medievale', 'Medievale', 'Romano Imperiale', 'Medievale',
        'Medievale', 'Medievale', 'Medievale', 'Medievale', ''
    ],
    'phase': [
        'Basso Medioevo', 'Alto Medioevo', 'Basso Medioevo', 'Alto Impero', 'Medio Impero',
        'Alto Impero', 'Alto Impero', 'Tardo Repubblicano', 'Alto Medioevo', 'Medio Repubblicano',
        'Basso Medioevo', 'Basso Medioevo', 'Alto Medioevo', 'Medio Impero', 'Basso Medioevo',
        '', 'Alto Medioevo', 'Basso Medioevo', '', ''
    ],
    'file_path': [
        '', '', '', '', '',
        '', '', '', '', '',
        '', '', '', '', '',
        '', '', '', '', 'docs/site_plan_2024.pdf'
    ]
}

# Define relationships forming a realistic stratigraphic sequence
relationships_data = {
    'from_us': [
        # Area A sequence
        '1001', '1002', '1003', '1004', '1004', '1005', '1006', '1007', '1008', '1009',
        # Area B sequence
        '2001', '2002', '2003', '2004', '2005',
        # Area C and connections
        '3001', '3002', '3003', '3004', '3005',
        # Cross-area relationships
        '1001', '2001', '1008', '2005'
    ],
    'to_us': [
        # Area A
        '1002', '1003', '1004', '1005', '1006', '1006', '1007', '1008', '1009', '1010',
        # Area B
        '2002', '2003', '2004', '2005', '3002',
        # Area C
        '1001', '3003', '1009', '1001', '3002',
        # Cross-area
        '2001', '3001', '3002', '3001'
    ],
    'relationship': [
        # Area A
        'Covers', 'Covers', 'Covers', 'Bonds_to', 'Fills', 'Cut_by', 'Fills', 'Covers', 'Covers', 'Covers',
        # Area B
        'Covers', 'Cut_by', 'Fills', 'Covers', 'Covers',
        # Area C
        '>', '>', '>', '>>', '>',
        # Cross-area
        'Equal_to', 'Continuity', '>>', '>>'
    ]
}

# Create DataFrames
nodes_df = pd.DataFrame(nodes_data)
relationships_df = pd.DataFrame(relationships_data)

# Create Excel file with 2 sheets
output_file = '/Users/enzo/Documents/pyarchinit-mini-desk/test_20us_complete.xlsx'

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    nodes_df.to_excel(writer, sheet_name='NODES', index=False)
    relationships_df.to_excel(writer, sheet_name='RELATIONSHIPS', index=False)

print(f"✅ Created comprehensive test file: {output_file}")
print(f"   - {len(nodes_df)} nodes")
print(f"   - {len(relationships_df)} relationships")
print(f"   - Node types: {', '.join(nodes_df['unit_type'].unique())}")
print(f"\n📝 Import command:")
print(f"   pyarchinit-harris-import test_20us_complete.xlsx --site 'Test Site EM 20 US'")