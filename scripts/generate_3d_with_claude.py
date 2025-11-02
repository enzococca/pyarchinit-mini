#!/usr/bin/env python3
"""
Generate 3D reconstruction using Claude AI and blender-mcp

This script exports archaeological data from PyArchInit and creates
structured prompts for Claude to generate intelligent 3D reconstructions
in Blender using multiple specialized agents.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set database URL
DB_PATH = "/Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini/pyarchinit_mini.db"
os.environ['DATABASE_URL'] = f'sqlite:///{DB_PATH}'

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.models.us import US
from pyarchinit_mini.models.site import Site


def export_site_data_for_claude(site_name: str) -> Dict[str, Any]:
    """
    Export site data in a format optimized for Claude AI interpretation

    Returns a structured dictionary with all archaeological data,
    dimensions, descriptions, and relationships.
    """

    db_conn = DatabaseConnection.from_url(f'sqlite:///{DB_PATH}')
    session = db_conn.SessionLocal()

    try:
        # Get site
        site = session.query(Site).filter(Site.sito == site_name).first()
        if not site:
            raise ValueError(f"Site '{site_name}' not found")

        # Get all US for this site
        us_units = session.query(US).filter(US.sito == site_name).order_by(US.us).all()

        # Organize by type
        physical_units = []
        em_reconstructions = []
        em_ancient_restorations = []
        em_modern_restorations = []
        combiners = []
        extractors = []
        docs = []

        for us in us_units:
            us_data = {
                "id": us.us,
                "type": us.unita_tipo or "Physical",
                "stratigraphic_description": us.d_stratigrafica,
                "interpretative_description": us.d_interpretativa,
                "full_description": us.descrizione,
                "period_start": us.periodo_iniziale,
                "period_end": us.periodo_finale,
                "formation": us.formazione,
                "structure": us.struttura,
                "color": us.colore,
                "consistency": us.consistenza,
                "inclusions": us.inclusi,
                "dimensions": {
                    "length_max": us.lunghezza_max,
                    "width_avg": us.larghezza_media,
                    "height_max": us.altezza_max,
                    "height_min": us.altezza_min,
                    "depth_max": us.profondita_max,
                    "depth_min": us.profondita_min,
                    "absolute_elevation": us.quota_abs
                },
                "observations": us.osservazioni
            }

            # Categorize by type
            if us.unita_tipo == "EM_Reconstruction":
                em_reconstructions.append(us_data)
            elif us.unita_tipo == "EM_Ancient_Restoration":
                em_ancient_restorations.append(us_data)
            elif us.unita_tipo == "EM_Modern_Restoration":
                em_modern_restorations.append(us_data)
            elif us.unita_tipo == "Combiner":
                combiners.append(us_data)
            elif us.unita_tipo == "Extractor":
                extractors.append(us_data)
            elif us.unita_tipo == "DOC":
                docs.append(us_data)
            else:
                physical_units.append(us_data)

        # Create structured export
        export_data = {
            "site": {
                "name": site.sito,
                "type": site.definizione_sito,
                "description": site.descrizione,
                "location": {
                    "country": site.nazione,
                    "region": site.regione,
                    "province": site.provincia,
                    "municipality": site.comune
                }
            },
            "units": {
                "physical": physical_units,
                "em_reconstructions": em_reconstructions,
                "em_ancient_restorations": em_ancient_restorations,
                "em_modern_restorations": em_modern_restorations,
                "combiners": combiners,
                "extractors": extractors,
                "documentation": docs
            },
            "statistics": {
                "total_units": len(us_units),
                "physical_units": len(physical_units),
                "reconstruction_nodes": len(em_reconstructions),
                "restoration_nodes": len(em_ancient_restorations) + len(em_modern_restorations)
            }
        }

        return export_data

    finally:
        session.close()


def create_claude_prompt_for_3d_generation(site_data: Dict[str, Any]) -> str:
    """
    Create a structured prompt for Claude to generate 3D reconstruction
    using blender-mcp tools.

    The prompt includes:
    - Site context and description
    - All physical units with dimensions
    - Reconstruction requirements
    - Material specifications
    - Validation criteria
    """

    site = site_data["site"]
    units = site_data["units"]

    prompt = f"""# 3D Archaeological Reconstruction: {site['name']}

## Context
You are an archaeological 3D reconstruction specialist. Your task is to create an accurate,
proportional 3D model of the **{site['name']}** in Blender using the blender-mcp tools.

**Site Description:** {site['description']}
**Location:** {site['location']['municipality']}, {site['location']['province']}, {site['location']['region']}, {site['location']['country']}

## Requirements

### 1. PHYSICAL UNITS (Excavated structures and layers)

Create these physical archaeological units with EXACT dimensions in meters:

"""

    # Add physical units
    for unit in units["physical"]:
        dims = unit["dimensions"]
        prompt += f"""
**US {unit['id']}** - {unit['stratigraphic_description']}
- Description: {unit['interpretative_description']}
- Period: {unit['period_start']} to {unit['period_end']}
- Structure type: {unit['structure'] or 'Layer'}
- Dimensions: {dims['length_max']}m (L) × {dims['width_avg']}m (W) × {dims['height_max']}m (H)
- Elevation: {dims['absolute_elevation']}m a.s.l.
- Material: {unit['color']}, {unit['consistency']}
- Inclusions: {unit['inclusions']}
"""

    prompt += """

### 2. RECONSTRUCTION NODES (Virtual 3D reconstructions)

Create these hypothetical reconstructions based on archaeological evidence:

"""

    # Add reconstruction nodes
    for unit in units["em_reconstructions"]:
        prompt += f"""
**EM {unit['id']}** - {unit['stratigraphic_description']}
- Description: {unit['full_description']}
- Period: {unit['period_start']}
- Observations: {unit['observations']}
"""

    prompt += """

### 3. MATERIALS AND TEXTURES

Apply realistic materials based on period and construction:

- **Republican period (II BC)**: Travertine stone (white-cream), pozzolanic mortar
- **Imperial period (I-II AD)**: Marble (white Carrara marble), colored opus sectile
- **Medieval period**: Reused Roman materials, lime mortar
- **Modern restoration**: Concrete (grey), steel reinforcement

### 4. SPATIAL ORGANIZATION

- Use absolute elevations (m a.s.l.) for Z-axis positioning
- Oldest layers at bottom (lowest elevation)
- Walls vertical, layers horizontal
- Maintain proportions between elements

### 5. VALIDATION CRITERIA

Your 3D model must:
✓ Use EXACT dimensions from the data (in meters)
✓ Respect stratigraphic relationships (lower = older)
✓ Apply period-appropriate materials
✓ Maintain architectural proportions
✓ Position elements at correct absolute elevations

## Instructions

1. **Clear the scene** - Remove default cube, camera, light
2. **Create physical units** - Build all excavated structures (US 1000-2007)
3. **Add reconstructions** - Create hypothetical elements (EM 3001-3003)
4. **Apply materials** - Assign realistic textures and colors
5. **Position correctly** - Use elevations for vertical placement
6. **Add lighting** - Studio lighting to showcase the reconstruction
7. **Set camera** - Isometric view showing the entire temple

## Expected Output

A complete 3D model of the **Temple of Fortuna** showing:
- Excavated foundations and walls (Republican period)
- Stratigraphic layers in section
- Virtual reconstruction of missing elements (roof, columns)
- Clear visual distinction between excavated and reconstructed parts
- Accurate scale and proportions (temple approx. 30m × 20m)

**Start by creating the foundation and perimeter walls (USM 2001-2004), then build upward layer by layer.**
"""

    return prompt


def create_agent_prompts(site_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Create specialized prompts for different agent roles
    """

    agents = {}

    # Architect Agent - Build base structure
    agents["architect"] = f"""You are the ARCHITECT agent for {site_data['site']['name']}.

Your role: Create the BASE STRUCTURE (foundations, walls, podium).

Physical units to build (exact dimensions in meters):
{json.dumps(site_data['units']['physical'], indent=2)}

Instructions:
1. Start with foundations (lowest elevation units)
2. Build perimeter walls (USM 2001-2004)
3. Use box primitives scaled to exact dimensions
4. Position using absolute elevations
5. Group related elements in collections

Output: Base structure ready for validation.
"""

    # Validator Agent
    agents["validator"] = """You are the VALIDATOR agent.

Your role: Verify dimensions, proportions, and spatial relationships.

Tasks:
1. Measure all created objects
2. Check dimensions match specifications
3. Verify elevations are correct
4. Check that walls connect properly
5. Report any discrepancies

Output: Validation report with measurements.
"""

    # Texturizer Agent
    agents["texturizer"] = """You are the TEXTURIZER agent.

Your role: Apply realistic archaeological materials.

Material specifications:
- Republican travertine: Base color (0.9, 0.85, 0.75), roughness 0.7
- Imperial marble: Base color (0.95, 0.95, 0.95), roughness 0.3, slight specularity
- Medieval reused stone: Base color (0.7, 0.7, 0.6), roughness 0.8, mixed texture
- Modern cement: Base color (0.5, 0.5, 0.5), roughness 0.6

Tasks:
1. Create materials for each period
2. Apply to appropriate objects
3. Add subtle weathering/aging
4. Ensure visual distinction between periods

Output: All objects with appropriate materials.
"""

    # Reconstructor Agent
    agents["reconstructor"] = f"""You are the RECONSTRUCTOR agent for {site_data['site']['name']}.

Your role: Create HYPOTHETICAL RECONSTRUCTIONS of missing elements.

Reconstruction nodes:
{json.dumps(site_data['units']['em_reconstructions'], indent=2)}

Tasks:
1. Create roof structure (EM 3002)
2. Reconstruct complete columns (EM 3003)
3. Build full temple elevation (EM 3001)
4. Use transparent/wireframe for virtual parts

Output: Complete reconstructed temple showing both excavated and virtual elements.
"""

    return agents


def save_data_and_prompts(site_name: str, output_dir: str = "output"):
    """
    Export site data and generate prompts for Claude
    """

    print(f"\n{'='*80}")
    print(f"GENERATING 3D RECONSTRUCTION PROMPTS: {site_name}")
    print(f"{'='*80}\n")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Export site data
    print("📊 Exporting site data...")
    site_data = export_site_data_for_claude(site_name)

    data_file = output_path / f"{site_name.replace(' ', '_')}_data.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(site_data, f, indent=2, ensure_ascii=False)
    print(f"   ✅ Data exported to: {data_file}")

    # Generate main prompt
    print("\n📝 Generating main reconstruction prompt...")
    main_prompt = create_claude_prompt_for_3d_generation(site_data)

    prompt_file = output_path / f"{site_name.replace(' ', '_')}_prompt.md"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(main_prompt)
    print(f"   ✅ Prompt saved to: {prompt_file}")

    # Generate agent prompts
    print("\n🤖 Generating specialized agent prompts...")
    agent_prompts = create_agent_prompts(site_data)

    for agent_name, agent_prompt in agent_prompts.items():
        agent_file = output_path / f"{site_name.replace(' ', '_')}_agent_{agent_name}.md"
        with open(agent_file, 'w', encoding='utf-8') as f:
            f.write(agent_prompt)
        print(f"   ✅ {agent_name.capitalize()} agent: {agent_file}")

    # Print summary
    print(f"\n{'='*80}")
    print("✅ PROMPTS GENERATED SUCCESSFULLY")
    print(f"{'='*80}\n")
    print("📊 Summary:")
    print(f"   - Site: {site_name}")
    print(f"   - Total units: {site_data['statistics']['total_units']}")
    print(f"   - Physical units: {site_data['statistics']['physical_units']}")
    print(f"   - Reconstruction nodes: {site_data['statistics']['reconstruction_nodes']}")
    print(f"   - Agent prompts: {len(agent_prompts)}")

    print("\n🎯 Next steps:")
    print("   1. Open Blender and start the blender-mcp addon")
    print(f"   2. Open Claude Desktop/Cursor with blender-mcp configured")
    print(f"   3. Copy the main prompt from: {prompt_file}")
    print("   4. Paste into Claude and let it generate the 3D model")
    print("   5. Use specialized agent prompts for refinement")

    print("\n💡 Agent workflow:")
    print("   - ARCHITECT: Build base structure")
    print("   - VALIDATOR: Check dimensions and proportions")
    print("   - TEXTURIZER: Apply realistic materials")
    print("   - RECONSTRUCTOR: Add virtual reconstruction elements")

    return data_file, prompt_file, agent_prompts


def list_available_sites() -> List[str]:
    """List all available sites in the database"""
    db_conn = DatabaseConnection.from_url(f'sqlite:///{DB_PATH}')
    session = db_conn.SessionLocal()

    try:
        sites = session.query(Site.sito).all()
        return [site[0] for site in sites]
    finally:
        session.close()


def interactive_site_selection() -> str:
    """Interactive CLI to select a site"""
    sites = list_available_sites()

    if not sites:
        print("❌ No sites found in database!")
        sys.exit(1)

    print("\n" + "="*80)
    print("AVAILABLE SITES IN DATABASE")
    print("="*80 + "\n")

    for i, site in enumerate(sites, 1):
        print(f"  {i}. {site}")

    print("\n" + "="*80 + "\n")

    while True:
        try:
            choice = input(f"Select site (1-{len(sites)}) or 'q' to quit: ").strip()

            if choice.lower() == 'q':
                print("Cancelled.")
                sys.exit(0)

            idx = int(choice) - 1
            if 0 <= idx < len(sites):
                return sites[idx]
            else:
                print(f"❌ Please enter a number between 1 and {len(sites)}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            sys.exit(0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate 3D reconstruction prompts for Claude AI from PyArchInit database"
    )
    parser.add_argument(
        '--site',
        type=str,
        help='Site name (if not provided, interactive selection will be used)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output/3d_generation',
        help='Output directory for generated prompts (default: output/3d_generation)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available sites and exit'
    )

    args = parser.parse_args()

    # List sites and exit
    if args.list:
        sites = list_available_sites()
        print("\n📊 Available sites in database:\n")
        for site in sites:
            print(f"  - {site}")
        print()
        sys.exit(0)

    # Get site name
    if args.site:
        site_name = args.site
        # Verify site exists
        sites = list_available_sites()
        if site_name not in sites:
            print(f"❌ Site '{site_name}' not found in database!")
            print(f"\nAvailable sites: {', '.join(sites)}")
            sys.exit(1)
    else:
        # Interactive selection
        site_name = interactive_site_selection()

    # Generate prompts
    try:
        save_data_and_prompts(site_name, output_dir=args.output)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
