"""
Example of using swimlane functionality to organize Harris Matrix GraphML by periods.

This example demonstrates:
1. Exporting Harris Matrix to GraphML
2. Applying swimlane organization to group nodes by archaeological periods
3. Customizing swimlane colors

Requirements:
    pip install pyarchinit-mini
"""

from pyarchinit_mini.database import DatabaseConnection, DatabaseManager
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.harris_matrix import HarrisMatrixGenerator
from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer
from pyarchinit_mini.graphml_converter import (
    convert_dot_content_to_graphml,
    apply_swimlanes_to_graphml
)
import tempfile
import os


def export_harris_matrix_with_swimlanes(
    site_name: str,
    output_file: str,
    title: str = "Archaeological Context",
    period_colors: dict = None
):
    """
    Export Harris Matrix to GraphML with swimlane organization.

    Args:
        site_name: Name of the archaeological site
        output_file: Path to save GraphML file
        title: Title for the swimlane table
        period_colors: Dict mapping period names to background colors

    Example period_colors:
        {
            'Moderno': '#CCFFCC',
            'Medievale': '#FFCC7F',
            'Romano Imperiale': '#FF9900',
            'Geologico': '#CCCCCC'
        }
    """
    print(f"=== Exporting Harris Matrix with Swimlanes ===\n")
    print(f"Site: {site_name}")
    print(f"Output: {output_file}\n")

    # Step 1: Connect to database
    print("Step 1: Connecting to database...")
    db_conn = DatabaseConnection('sqlite:///./pyarchinit_mini.db')
    db_manager = DatabaseManager(db_conn)
    us_service = USService(db_manager)
    print("  ✓ Connected\n")

    # Step 2: Generate Harris Matrix graph
    print("Step 2: Generating Harris Matrix graph...")
    matrix_generator = HarrisMatrixGenerator(db_manager, us_service)
    graph = matrix_generator.generate_matrix(site_name)
    print(f"  ✓ Generated graph with {graph.number_of_nodes()} nodes\n")

    # Step 3: Generate DOT content
    print("Step 3: Generating DOT content...")
    graphviz_visualizer = PyArchInitMatrixVisualizer()
    dot_content = graphviz_visualizer.get_dot_source(graph, grouping='period_area')
    print(f"  ✓ Generated DOT ({len(dot_content)} characters)\n")

    # Step 4: Convert to GraphML
    print("Step 4: Converting to GraphML...")
    graphml_content = convert_dot_content_to_graphml(dot_content)
    print(f"  ✓ Converted to GraphML ({len(graphml_content)} characters)\n")

    # Step 5: Apply swimlanes
    print("Step 5: Applying swimlane organization...")
    swimlane_graphml = apply_swimlanes_to_graphml(
        graphml_content,
        title=title,
        row_colors=period_colors
    )
    print(f"  ✓ Applied swimlanes\n")

    # Step 6: Save to file
    print("Step 6: Saving to file...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(swimlane_graphml)

    file_size_kb = os.path.getsize(output_file) / 1024
    print(f"  ✓ Saved to {output_file}")
    print(f"  ✓ File size: {file_size_kb:.2f} KB\n")

    print("=== Export Complete ===\n")
    print("To view in yEd:")
    print("  1. Open yEd Graph Editor")
    print("  2. File → Open → Select the .graphml file")
    print("  3. Nodes are organized in swimlanes by period")
    print("  4. Each period has its own horizontal row (swimlane)")
    print("  5. Use Layout → Hierarchical to arrange nodes within swimlanes\n")


def main():
    """Main example demonstrating swimlane functionality."""

    # Example 1: Basic swimlane export
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Swimlane Export")
    print("="*70 + "\n")

    export_harris_matrix_with_swimlanes(
        site_name='Sito Archeologico di Esempio',
        output_file='/tmp/harris_matrix_swimlanes_basic.graphml',
        title='Sito Archeologico di Esempio'
    )

    # Example 2: Custom period colors
    print("\n" + "="*70)
    print("EXAMPLE 2: Custom Period Colors")
    print("="*70 + "\n")

    custom_colors = {
        'Moderno': '#CCFFCC',          # Light green
        'Medievale': '#FFCC7F',        # Light orange
        'Romano Imperiale': '#FF9900', # Orange
        'Geologico': '#CCCCCC'         # Light gray
    }

    export_harris_matrix_with_swimlanes(
        site_name='Sito Archeologico di Esempio',
        output_file='/tmp/harris_matrix_swimlanes_colored.graphml',
        title='Sito Archeologico - Organized by Period',
        period_colors=custom_colors
    )

    # Example 3: Direct API usage
    print("\n" + "="*70)
    print("EXAMPLE 3: Direct Swimlane API Usage")
    print("="*70 + "\n")

    from pyarchinit_mini.graphml_converter import SwimlaneOrganizer

    # Load existing GraphML
    print("Loading existing GraphML file...")
    with open('/tmp/harris_matrix_swimlanes_basic.graphml', 'r', encoding='utf-8') as f:
        graphml = f.read()

    # Create organizer
    print("Creating swimlane organizer...")
    organizer = SwimlaneOrganizer(graphml)

    # Extract periods
    print("Extracting periods from node labels...")
    node_to_period = organizer.extract_periods_from_labels()
    print(f"  ✓ Found {len(organizer.periods)} periods:")
    for period in sorted(organizer.periods):
        count = sum(1 for p in node_to_period.values() if p == period)
        print(f"    - {period}: {count} nodes")

    print("\n" + "="*70)
    print("Swimlane Examples Complete!")
    print("="*70 + "\n")
    print("Output files:")
    print("  - /tmp/harris_matrix_swimlanes_basic.graphml")
    print("  - /tmp/harris_matrix_swimlanes_colored.graphml")
    print("\nOpen these files in yEd to see the swimlane organization!")


if __name__ == '__main__':
    main()
