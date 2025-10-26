#!/usr/bin/env python3
"""
Harris Matrix Template Generator
=================================

Generate template files for Harris Matrix CSV/Excel import.

The template includes:
- Example nodes with all Extended Matrix types
- Example relationships demonstrating all relationship types
- Clear instructions and field descriptions
"""

import click
import pandas as pd
import os
from typing import Literal


def create_template_data():
    """Create template data with examples"""

    # Nodes template with examples
    nodes_data = {
        'us_number': [
            # Regular US nodes
            '1001', '1002', '1003', '1004', '1005',
            # Special node types examples
            '2001', '2002', '2003', '2004', '2005', '2006'
        ],
        'unit_type': [
            # Standard nodes
            'US', 'US', 'US', 'USM', 'US',
            # Extended Matrix special types
            'USVA', 'Extractor', 'Combiner', 'DOC', 'SF', 'TU'
        ],
        'description': [
            'Topsoil layer',
            'Stone wall foundation',
            'Fill deposit',
            'Brick wall',
            'Floor surface',
            'Pit cut (virtual)',
            'Aggregate extraction node',
            'Combined stratigraphic context',
            'Site plan drawing',
            'Pottery assemblage',
            'Test trench 1'
        ],
        'area': [
            'Area A', 'Area A', 'Area A', 'Area A', 'Area A',
            'Area B', 'Area B', 'Area B', 'Area A', 'Area A', 'Area B'
        ],
        'period': [
            'Modern', 'Medieval', 'Medieval', 'Medieval', 'Roman',
            'Medieval', 'Medieval', 'Medieval', '', 'Roman', ''
        ],
        'phase': [
            '', 'Late', 'Late', 'Late', 'Early',
            '', '', '', '', 'Early', ''
        ],
        'file_path': [
            '', '', '', '', '',
            '', '', '', 'docs/site_plan_2024.pdf', '', ''
        ]
    }

    # Relationships template with examples
    relationships_data = {
        'from_us': [
            # Standard stratigraphic relationships
            '1001', '1002', '1003', '1004',
            # Extended Matrix relationships
            '1002', '1003', '1002',
            # Special relationships
            '1001', '1001'
        ],
        'to_us': [
            '1002', '1003', '1004', '1005',
            '2001', '2002', '2003',
            '2004', '2005'
        ],
        'relationship': [
            # Standard types (English names - will be converted)
            'Covers', 'Covers', 'Fills', 'Bonds_to',
            # Extended Matrix symbols
            '<', '>>', '>>',
            # Special types
            '<<', '>'
        ],
        'notes': [
            'Topsoil covers wall',
            'Wall foundation above fill',
            'Fill deposit inside pit',
            'Wall bonds to floor',
            'Connection to virtual pit cut',
            'Extraction relationship (aggregate)',
            'Combination relationship',
            'Associated with document',
            'Contains special finds'
        ]
    }

    nodes_df = pd.DataFrame(nodes_data)
    relationships_df = pd.DataFrame(relationships_data)

    return nodes_df, relationships_df


def create_instructions():
    """Create instruction sheet data"""
    instructions = {
        'Section': [
            'OVERVIEW',
            '',
            'NODES_REQUIRED',
            'NODES_REQUIRED',
            '',
            'NODES_OPTIONAL',
            'NODES_OPTIONAL',
            'NODES_OPTIONAL',
            'NODES_OPTIONAL',
            'NODES_OPTIONAL',
            '',
            'UNIT_TYPES',
            'UNIT_TYPES',
            'UNIT_TYPES',
            'UNIT_TYPES',
            'UNIT_TYPES',
            'UNIT_TYPES',
            'UNIT_TYPES',
            'UNIT_TYPES',
            'UNIT_TYPES',
            'UNIT_TYPES',
            'UNIT_TYPES',
            'UNIT_TYPES',
            'UNIT_TYPES',
            '',
            'RELATIONSHIPS_REQUIRED',
            'RELATIONSHIPS_REQUIRED',
            'RELATIONSHIPS_REQUIRED',
            '',
            'RELATIONSHIP_TYPES_STANDARD',
            'RELATIONSHIP_TYPES_STANDARD',
            'RELATIONSHIP_TYPES_STANDARD',
            'RELATIONSHIP_TYPES_STANDARD',
            'RELATIONSHIP_TYPES_STANDARD',
            'RELATIONSHIP_TYPES_STANDARD',
            'RELATIONSHIP_TYPES_STANDARD',
            'RELATIONSHIP_TYPES_STANDARD',
            'RELATIONSHIP_TYPES_STANDARD',
            '',
            'RELATIONSHIP_TYPES_EM',
            'RELATIONSHIP_TYPES_EM',
            'RELATIONSHIP_TYPES_EM',
            'RELATIONSHIP_TYPES_EM',
            '',
            'RELATIONSHIP_TYPES_SPECIAL',
            '',
            'NOTES',
            'NOTES',
            'NOTES',
        ],
        'Field/Value': [
            'This template allows you to import a complete Harris Matrix',
            '',
            'us_number', 'unit_type',
            '',
            'description', 'area', 'period', 'phase', 'file_path',
            '',
            'US', 'USM', 'USVA', 'USVB', 'USVC', 'TU', 'USD', 'SF', 'VSF', 'CON', 'DOC', 'Extractor', 'Combiner',
            '',
            'from_us', 'to_us', 'relationship',
            '',
            'Covers', 'Covered_by', 'Fills', 'Filled_by', 'Cuts', 'Cut_by', 'Bonds_to', 'Equal_to', 'Leans_on',
            '',
            '>', '<', '>>', '<<',
            '',
            'Continuity',
            '',
            'DOC units require file_path', 'Periods and phases help organize the matrix visually', 'Areas group units spatially'
        ],
        'Description': [
            'Fill the NODES and RELATIONSHIPS sheets with your data',
            '',
            'Unique US number (required)', 'Type of unit (default: US)',
            '',
            'Human-readable description', 'Spatial grouping (e.g., Area A, Trench 1)', 'Chronological period (e.g., Medieval, Roman)', 'Subdivision of period (e.g., Early, Late)', 'Path to document file (for DOC units)',
            '',
            'Standard stratigraphic unit', 'Mural stratigraphic unit', 'Virtual US type A (negative features)', 'Virtual US type B', 'Virtual US type C', 'Topographic unit', 'Stratigraphic unit (special)', 'Special finds', 'Virtual special finds', 'Context', 'Document (requires file_path)', 'Extractor node (aggregation)', 'Combiner node (aggregation)',
            '',
            'Source US number', 'Target US number', 'Type of relationship',
            '',
            'from_us covers/above to_us', 'from_us covered by/below to_us', 'from_us fills to_us', 'from_us filled by to_us', 'from_us cuts to_us', 'from_us cut by to_us', 'from_us bonds to to_us', 'from_us equals to_us', 'from_us leans on to_us',
            '',
            'Connection to single-symbol unit (USVA, SF, etc.)', 'Reverse connection from single-symbol unit', 'Connection to double-symbol unit (Extractor, Combiner, DOC)', 'Reverse from double-symbol unit',
            '',
            'Contemporary units (solid line, no arrow)',
            '',
            'File path relative to project or absolute', 'Used for visual grouping in matrix', 'Used for horizontal grouping (rows)'
        ]
    }

    return pd.DataFrame(instructions)


@click.command()
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['xlsx', 'csv'], case_sensitive=False),
              default='xlsx',
              help='Output format (default: xlsx)')
@click.option('--output', '-o',
              default='harris_matrix_template',
              help='Output filename (without extension)')
@click.option('--with-examples', '-e',
              is_flag=True,
              default=True,
              help='Include example data (default: yes)')
def generate_template(output_format, output, with_examples):
    """
    Generate Harris Matrix import template

    \b
    Creates a template file with:
    - NODES sheet: Define all stratigraphic units
    - RELATIONSHIPS sheet: Define connections between units
    - INSTRUCTIONS sheet: Field descriptions and examples

    \b
    Examples:
        # Generate Excel template with examples
        pyarchinit-harris-template

        # Generate CSV template
        pyarchinit-harris-template --format csv

        # Custom output name
        pyarchinit-harris-template -o my_site_template
    """
    click.echo("=" * 60)
    click.echo("Harris Matrix Template Generator")
    click.echo("=" * 60)

    # Create template data
    if with_examples:
        nodes_df, relationships_df = create_template_data()
        click.echo("✓ Including example data")
    else:
        # Empty template
        nodes_df = pd.DataFrame({
            'us_number': [],
            'unit_type': [],
            'description': [],
            'area': [],
            'period': [],
            'phase': [],
            'file_path': []
        })
        relationships_df = pd.DataFrame({
            'from_us': [],
            'to_us': [],
            'relationship': [],
            'notes': []
        })
        click.echo("✓ Empty template (no examples)")

    instructions_df = create_instructions()

    # Generate output filename
    output_file = f"{output}.{output_format}"

    # Write file
    try:
        if output_format == 'xlsx':
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Write sheets
                instructions_df.to_excel(writer, sheet_name='INSTRUCTIONS', index=False)
                nodes_df.to_excel(writer, sheet_name='NODES', index=False)
                relationships_df.to_excel(writer, sheet_name='RELATIONSHIPS', index=False)

            click.echo(f"\n✅ Excel template created: {output_file}")
            click.echo(f"\n📖 The file has 3 sheets:")
            click.echo(f"   1. INSTRUCTIONS - Read this first!")
            click.echo(f"   2. NODES - Define your stratigraphic units here")
            click.echo(f"   3. RELATIONSHIPS - Define connections between units here")

        else:  # CSV
            # For CSV, combine into single file with section markers
            csv_output = f"{output}_INSTRUCTIONS.csv"
            instructions_df.to_csv(csv_output, index=False)
            click.echo(f"✓ Instructions: {csv_output}")

            csv_output = f"{output}_NODES.csv"
            nodes_df.to_csv(csv_output, index=False)
            click.echo(f"✓ Nodes: {csv_output}")

            csv_output = f"{output}_RELATIONSHIPS.csv"
            relationships_df.to_csv(csv_output, index=False)
            click.echo(f"✓ Relationships: {csv_output}")

            click.echo(f"\n✅ CSV templates created")
            click.echo(f"\n⚠️  Note: For CSV import, use the NODES file and include")
            click.echo(f"   RELATIONSHIPS data below the nodes, separated by an empty line.")

        click.echo(f"\n📝 Next steps:")
        click.echo(f"   1. Open the template file")
        click.echo(f"   2. Read the INSTRUCTIONS sheet carefully")
        click.echo(f"   3. Fill in your data in NODES and RELATIONSHIPS sheets")
        click.echo(f"   4. Import using: pyarchinit-harris-import {output_file} --site \"Your Site Name\"")

        click.echo("\n" + "=" * 60)

    except Exception as e:
        click.echo(f"❌ Error creating template: {str(e)}", err=True)
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    generate_template()