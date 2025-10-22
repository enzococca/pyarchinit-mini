"""
Generate Test 3D Model for s3Dgraphy Integration

Creates OBJ and GLTF files with proxy geometries representing stratigraphic units.
Each US is represented as a colored box positioned in 3D space based on stratigraphic level.
"""

import os
import json
import struct
import base64
from pathlib import Path


# Sample US data matching Extended Matrix types
SAMPLE_US = [
    {'us': 1001, 'type': 'Humus', 'area': 'A', 'period': 'Moderno', 'level': 0},
    {'us': 1002, 'type': 'Deposito', 'area': 'A', 'period': 'Medievale', 'level': 1},
    {'us': 1003, 'type': 'Taglio', 'area': 'A', 'period': 'Medievale', 'level': 2},
    {'us': 1004, 'type': 'Riempimento', 'area': 'A', 'period': 'Medievale', 'level': 3},
    {'us': 1005, 'type': 'Pavimento', 'area': 'B', 'period': 'Romano', 'level': 4},
    {'us': 1006, 'type': 'Muro', 'area': 'B', 'period': 'Romano', 'level': 5},
    {'us': 1007, 'type': 'Deposito', 'area': 'B', 'period': 'Romano', 'level': 6},
    {'us': 1008, 'type': 'Crollo', 'area': 'C', 'period': 'Tardo Antico', 'level': 3},
    {'us': 1009, 'type': 'Costruzione', 'area': 'C', 'period': 'Romano', 'level': 7},
    {'us': 1010, 'type': 'Terreno arativo', 'area': 'C', 'period': 'Moderno', 'level': 0},
]

# Extended Matrix colors (RGB 0-1 range)
EM_COLORS = {
    'Taglio': (0.545, 0.271, 0.075),       # #8B4513 - Dark brown
    'Deposito': (0.824, 0.412, 0.118),     # #D2691E - Chocolate
    'Riempimento': (0.804, 0.522, 0.247),  # #CD853F - Peru
    'Humus': (0.957, 0.643, 0.376),        # #F4A460 - Sandy brown
    'Terreno arativo': (0.957, 0.643, 0.376),
    'Muro': (0.502, 0.502, 0.502),         # #808080 - Gray
    'Pavimento': (0.275, 0.510, 0.706),    # #4682B4 - Steel blue
    'Distruzione': (1.0, 0.843, 0.0),      # #FFD700 - Gold
    'Crollo': (1.0, 0.843, 0.0),
    'Costruzione': (0.565, 0.933, 0.565),  # #90EE90 - Light green
}


def create_box_vertices(center_x, center_y, center_z, width=2.0, height=0.5, depth=2.0):
    """Create vertices for a box centered at given position"""
    hw, hh, hd = width/2, height/2, depth/2

    vertices = [
        # Front face
        (center_x - hw, center_y - hh, center_z + hd),
        (center_x + hw, center_y - hh, center_z + hd),
        (center_x + hw, center_y + hh, center_z + hd),
        (center_x - hw, center_y + hh, center_z + hd),
        # Back face
        (center_x - hw, center_y - hh, center_z - hd),
        (center_x + hw, center_y - hh, center_z - hd),
        (center_x + hw, center_y + hh, center_z - hd),
        (center_x - hw, center_y + hh, center_z - hd),
    ]

    return vertices


def generate_obj_model(output_path):
    """Generate OBJ file with colored boxes for each US"""

    vertices = []
    faces = []
    materials = []
    mtl_file = output_path.replace('.obj', '.mtl')

    vertex_offset = 0

    # Create MTL file with colors
    with open(mtl_file, 'w') as mtl:
        mtl.write("# Extended Matrix Materials\n")
        for us_type, color in EM_COLORS.items():
            mat_name = us_type.replace(' ', '_')
            mtl.write(f"\nnewmtl {mat_name}\n")
            mtl.write(f"Ka {color[0]:.3f} {color[1]:.3f} {color[2]:.3f}\n")
            mtl.write(f"Kd {color[0]:.3f} {color[1]:.3f} {color[2]:.3f}\n")
            mtl.write(f"Ks 0.5 0.5 0.5\n")
            mtl.write(f"Ns 32.0\n")
            mtl.write(f"d 1.0\n")

    # Generate OBJ
    with open(output_path, 'w') as obj:
        obj.write("# PyArchInit-Mini Test Model\n")
        obj.write("# Stratigraphic Units as colored boxes\n")
        obj.write(f"mtllib {os.path.basename(mtl_file)}\n\n")

        for us in SAMPLE_US:
            # Position based on area and level
            area_offset = {'A': -5, 'B': 0, 'C': 5}.get(us['area'], 0)
            x = area_offset + (hash(us['us']) % 3) - 1
            y = -us['level'] * 1.0  # Deeper = lower Y
            z = (hash(us['us']) % 3) - 1

            # Create box
            box_verts = create_box_vertices(x, y, z, width=2.5, height=0.4, depth=2.5)

            # Write vertices
            obj.write(f"# US {us['us']} - {us['type']}\n")
            obj.write(f"g US_{us['us']}\n")
            for v in box_verts:
                obj.write(f"v {v[0]:.3f} {v[1]:.3f} {v[2]:.3f}\n")

            # Use material
            mat_name = us['type'].replace(' ', '_')
            obj.write(f"usemtl {mat_name}\n")

            # Write faces (box has 6 faces, 2 triangles each)
            base = vertex_offset + 1

            # Front face
            obj.write(f"f {base} {base+1} {base+2}\n")
            obj.write(f"f {base} {base+2} {base+3}\n")
            # Back face
            obj.write(f"f {base+5} {base+4} {base+7}\n")
            obj.write(f"f {base+5} {base+7} {base+6}\n")
            # Top face
            obj.write(f"f {base+3} {base+2} {base+6}\n")
            obj.write(f"f {base+3} {base+6} {base+7}\n")
            # Bottom face
            obj.write(f"f {base+1} {base} {base+4}\n")
            obj.write(f"f {base+1} {base+4} {base+5}\n")
            # Right face
            obj.write(f"f {base+1} {base+5} {base+6}\n")
            obj.write(f"f {base+1} {base+6} {base+2}\n")
            # Left face
            obj.write(f"f {base+4} {base} {base+3}\n")
            obj.write(f"f {base+4} {base+3} {base+7}\n")

            obj.write("\n")
            vertex_offset += 8

    print(f"✓ Created OBJ model: {output_path}")
    print(f"✓ Created MTL file: {mtl_file}")


def generate_gltf_model(output_path):
    """Generate GLTF file with colored boxes for each US"""

    all_vertices = []
    all_indices = []
    all_colors = []

    vertex_offset = 0

    for us in SAMPLE_US:
        # Position based on area and level
        area_offset = {'A': -5, 'B': 0, 'C': 5}.get(us['area'], 0)
        x = area_offset + (hash(us['us']) % 3) - 1
        y = -us['level'] * 1.0  # Deeper = lower Y
        z = (hash(us['us']) % 3) - 1

        # Create box
        box_verts = create_box_vertices(x, y, z, width=2.5, height=0.4, depth=2.5)

        # Add vertices (flatten to list)
        for v in box_verts:
            all_vertices.extend([v[0], v[1], v[2]])

        # Get color for this US type
        color = EM_COLORS.get(us['type'], (0.867, 0.627, 0.867))  # Default plum

        # Add colors for all vertices (RGBA)
        for _ in range(8):
            all_colors.extend([color[0], color[1], color[2], 1.0])

        # Add indices for box faces
        base = vertex_offset
        box_indices = [
            # Front
            base, base+1, base+2,  base, base+2, base+3,
            # Back
            base+5, base+4, base+7,  base+5, base+7, base+6,
            # Top
            base+3, base+2, base+6,  base+3, base+6, base+7,
            # Bottom
            base+1, base, base+4,  base+1, base+4, base+5,
            # Right
            base+1, base+5, base+6,  base+1, base+6, base+2,
            # Left
            base+4, base, base+3,  base+4, base+3, base+7,
        ]
        all_indices.extend(box_indices)

        vertex_offset += 8

    # Convert to binary buffers
    vertices_bytes = struct.pack(f'{len(all_vertices)}f', *all_vertices)
    colors_bytes = struct.pack(f'{len(all_colors)}f', *all_colors)
    indices_bytes = struct.pack(f'{len(all_indices)}H', *all_indices)

    # Calculate buffer byte lengths
    vertices_byte_length = len(vertices_bytes)
    colors_byte_length = len(colors_bytes)
    indices_byte_length = len(indices_bytes)

    # Create GLTF JSON structure
    gltf = {
        "asset": {
            "version": "2.0",
            "generator": "PyArchInit-Mini s3Dgraphy Generator"
        },
        "scene": 0,
        "scenes": [
            {
                "name": "Stratigraphic Scene",
                "nodes": [0]
            }
        ],
        "nodes": [
            {
                "name": "US_Collection",
                "mesh": 0
            }
        ],
        "meshes": [
            {
                "name": "Stratigraphic_Units",
                "primitives": [
                    {
                        "attributes": {
                            "POSITION": 0,
                            "COLOR_0": 1
                        },
                        "indices": 2,
                        "mode": 4  # TRIANGLES
                    }
                ]
            }
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,  # FLOAT
                "count": len(all_vertices) // 3,
                "type": "VEC3",
                "max": [max(all_vertices[i::3]) for i in range(3)],
                "min": [min(all_vertices[i::3]) for i in range(3)]
            },
            {
                "bufferView": 1,
                "componentType": 5126,  # FLOAT
                "count": len(all_colors) // 4,
                "type": "VEC4"
            },
            {
                "bufferView": 2,
                "componentType": 5123,  # UNSIGNED_SHORT
                "count": len(all_indices),
                "type": "SCALAR"
            }
        ],
        "bufferViews": [
            {
                "buffer": 0,
                "byteOffset": 0,
                "byteLength": vertices_byte_length,
                "target": 34962  # ARRAY_BUFFER
            },
            {
                "buffer": 0,
                "byteOffset": vertices_byte_length,
                "byteLength": colors_byte_length,
                "target": 34962  # ARRAY_BUFFER
            },
            {
                "buffer": 0,
                "byteOffset": vertices_byte_length + colors_byte_length,
                "byteLength": indices_byte_length,
                "target": 34963  # ELEMENT_ARRAY_BUFFER
            }
        ],
        "buffers": [
            {
                "byteLength": vertices_byte_length + colors_byte_length + indices_byte_length,
                "uri": os.path.basename(output_path.replace('.gltf', '.bin'))
            }
        ]
    }

    # Write GLTF JSON
    with open(output_path, 'w') as f:
        json.dump(gltf, f, indent=2)

    # Write binary buffer
    bin_path = output_path.replace('.gltf', '.bin')
    with open(bin_path, 'wb') as f:
        f.write(vertices_bytes)
        f.write(colors_bytes)
        f.write(indices_bytes)

    print(f"✓ Created GLTF model: {output_path}")
    print(f"✓ Created binary buffer: {bin_path}")


def main():
    """Generate both OBJ and GLTF test models"""

    # Create output directory - use correct path for Model3DManager
    output_dir = Path("web_interface/static/uploads/3d_models/Sito Archeologico di Esempio/site")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate OBJ model
    obj_path = output_dir / "stratigraphy_test.obj"
    generate_obj_model(str(obj_path))

    # Generate GLTF model
    gltf_path = output_dir / "stratigraphy_test.gltf"
    generate_gltf_model(str(gltf_path))

    print(f"\n✓ Test models generated successfully!")
    print(f"\nModels contain {len(SAMPLE_US)} stratigraphic units:")
    for us in SAMPLE_US:
        color_rgb = [int(c * 255) for c in EM_COLORS.get(us['type'], (0.867, 0.627, 0.867))]
        print(f"  • US {us['us']}: {us['type']} (Area {us['area']}, {us['period']}) - RGB{tuple(color_rgb)}")


if __name__ == '__main__':
    main()