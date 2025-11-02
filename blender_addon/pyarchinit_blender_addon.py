"""
PyArchInit Blender MCP Addon

Receives commands from PyArchInit MCP Server and creates 3D stratigraphic models
with REAL geometry based on archaeological data (US descriptions, materials, colors, etc.)

Installation:
1. Open Blender
2. Go to Edit > Preferences > Add-ons
3. Click "Install" and select this file
4. Enable "PyArchInit: MCP Builder"
5. Start the MCP server from the addon panel

Usage:
- Start server: Opens TCP socket on port 9876
- Receives JSON commands from PyArchInit
- Creates real 3D geometry with materials
- Streams progress via WebSocket
"""

bl_info = {
    "name": "PyArchInit: MCP Builder",
    "author": "PyArchInit Team",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > PyArchInit",
    "description": "Build 3D stratigraphic models from PyArchInit MCP commands",
    "category": "Object",
}

import bpy
import bmesh
import json
import socket
import threading
import logging
from typing import Dict, Any, List, Optional, Tuple
from mathutils import Vector, Matrix
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Global State
# ============================================================================

class MCPServerState:
    """Global state for MCP server"""
    server_thread: Optional[threading.Thread] = None
    server_socket: Optional[socket.socket] = None
    running: bool = False
    current_session: Optional[str] = None
    progress_messages: List[Dict[str, Any]] = []  # Store progress for polling

    # 3D scene state
    proxies: Dict[str, Any] = {}  # proxy_id -> proxy_object
    collections: Dict[str, Any] = {}  # collection_name -> collection


server_state = MCPServerState()


# ============================================================================
# Progress Tracking (Simple, No WebSocket)
# ============================================================================

def send_progress_sync(message: Dict[str, Any]):
    """Store progress message for later retrieval"""
    try:
        server_state.progress_messages.append(message)
        # Keep only last 100 messages
        if len(server_state.progress_messages) > 100:
            server_state.progress_messages = server_state.progress_messages[-100:]

        # Also log to console
        logger.info(f"Progress: {message.get('action', 'unknown')} - {message.get('message', '')}")
    except Exception as e:
        logger.error(f"Error storing progress: {e}")


# ============================================================================
# Geometry Creation Functions
# ============================================================================

def create_stratigraphic_geometry(
    proxy_id: str,
    us_data: Dict[str, Any],
    position: Tuple[float, float, float],
    graphml_edges: List[Dict[str, Any]]
) -> bpy.types.Object:
    """
    Create REAL 3D geometry for a stratigraphic unit

    Based on:
    - unità_tipo: determines base geometry shape
    - descrizione: influences detail level
    - relationships: affects vertical position and connections

    Args:
        proxy_id: Unique identifier
        us_data: Complete US data from database
        position: (x, y, z) position from GraphML
        graphml_edges: Stratigraphic relationships

    Returns:
        Created Blender object
    """
    us_id = us_data.get('us_id')
    unita_tipo = us_data.get('unita_tipo', 'US')
    descrizione = us_data.get('descrizione', '')

    # Send progress
    send_progress_sync({
        "type": "progress",
        "action": "creating_geometry",
        "us_id": us_id,
        "unita_tipo": unita_tipo,
        "message": f"Creating geometry for US {us_id} ({unita_tipo})"
    })

    # Create mesh based on unità_tipo
    mesh = bpy.data.meshes.new(name=f"US_{us_id}_mesh")
    obj = bpy.data.objects.new(f"US_{us_id}", mesh)

    bm = bmesh.new()

    # Geometry creation based on unità_tipo
    if unita_tipo in ["Strato", "Layer", "US"]:
        # Create layered geometry (stratified deposit)
        create_layer_geometry(bm, us_data, descrizione)

    elif unita_tipo in ["Struttura", "Structure", "Muro", "Wall"]:
        # Create structural geometry (walls, foundations)
        create_structure_geometry(bm, us_data, descrizione)

    elif unita_tipo in ["Taglio", "Cut", "Fossa"]:
        # Create negative feature (cut, pit)
        create_cut_geometry(bm, us_data, descrizione)

    elif unita_tipo in ["Riempimento", "Fill"]:
        # Create fill geometry
        create_fill_geometry(bm, us_data, descrizione)

    else:
        # Default generic geometry
        create_generic_geometry(bm, us_data, descrizione)

    # Apply mesh
    bm.to_mesh(mesh)
    bm.free()

    # Set position
    obj.location = Vector(position)

    # Link to scene
    bpy.context.collection.objects.link(obj)

    logger.info(f"Created geometry for US {us_id}: {unita_tipo}")

    return obj


def create_layer_geometry(bm: bmesh.types.BMesh, us_data: Dict[str, Any], descrizione: str):
    """Create geometry for stratified layers"""
    # Create a layered rectangular volume
    # Base size from description or default
    width = 4.0
    length = 4.0
    thickness = 0.3  # Thin layer

    # Vary thickness based on description keywords
    if "sottile" in descrizione.lower() or "thin" in descrizione.lower():
        thickness = 0.15
    elif "spesso" in descrizione.lower() or "thick" in descrizione.lower():
        thickness = 0.6

    # Create box with varied top surface
    bmesh.ops.create_cube(bm, size=1.0)

    # Scale to layer proportions
    bmesh.ops.scale(bm, vec=(width, length, thickness), verts=bm.verts)

    # Add surface variation for natural deposits
    if "naturale" in descrizione.lower() or "natural" in descrizione.lower():
        # Subdivide top surface
        top_faces = [f for f in bm.faces if f.normal.z > 0.9]
        bmesh.ops.subdivide_edges(
            bm,
            edges=[e for f in top_faces for e in f.edges],
            cuts=3
        )

        # Displace vertices randomly for natural look
        import random
        for v in bm.verts:
            if v.co.z > 0:
                v.co.z += random.uniform(-0.05, 0.05)


def create_structure_geometry(bm: bmesh.types.BMesh, us_data: Dict[str, Any], descrizione: str):
    """Create geometry for structural elements (walls, foundations)"""
    # Create more substantial, vertical geometry
    width = 0.6  # Wall thickness
    length = 3.0  # Wall length
    height = 2.0  # Wall height

    # Adjust based on description
    if "fondazione" in descrizione.lower() or "foundation" in descrizione.lower():
        height = 0.8  # Shorter for foundations
        width = 0.8  # Thicker
    elif "muro" in descrizione.lower() or "wall" in descrizione.lower():
        height = 2.5

    # Create box
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(width, length, height), verts=bm.verts)

    # Add detail for masonry
    if "pietra" in descrizione.lower() or "stone" in descrizione.lower():
        # Subdivide for stone blocks
        bmesh.ops.subdivide_edges(
            bm,
            edges=bm.edges[:],
            cuts=2
        )


def create_cut_geometry(bm: bmesh.types.BMesh, us_data: Dict[str, Any], descrizione: str):
    """Create geometry for negative features (cuts, pits)"""
    # Create inverted/negative geometry
    # Use cylinder for pits, rectangular for trenches

    if "fossa" in descrizione.lower() or "pit" in descrizione.lower():
        # Cylindrical pit
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            cap_tris=False,
            segments=16,
            radius1=1.0,
            radius2=0.8,  # Slightly tapered
            depth=1.5
        )
    else:
        # Rectangular cut
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(2.0, 1.0, 1.5), verts=bm.verts)


def create_fill_geometry(bm: bmesh.types.BMesh, us_data: Dict[str, Any], descrizione: str):
    """Create geometry for fill deposits"""
    # Similar to layer but more irregular
    width = 3.0
    length = 3.0
    thickness = 0.8

    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(width, length, thickness), verts=bm.verts)

    # Add irregularity
    import random
    for v in bm.verts:
        v.co.x += random.uniform(-0.1, 0.1)
        v.co.y += random.uniform(-0.1, 0.1)


def create_generic_geometry(bm: bmesh.types.BMesh, us_data: Dict[str, Any], descrizione: str):
    """Create generic geometry for undefined types"""
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(2.0, 2.0, 0.5), verts=bm.verts)


# ============================================================================
# Material Application
# ============================================================================

def apply_archaeological_material(
    obj: bpy.types.Object,
    us_data: Dict[str, Any],
    auto_color: bool = True
) -> bpy.types.Material:
    """
    Apply material based on archaeological data

    Uses:
    - periodo: determines color scheme
    - unità_tipo: determines material properties
    - custom colors if specified
    """
    us_id = us_data.get('us_id')
    periodo = us_data.get('periodo', 'Unknown')
    unita_tipo = us_data.get('unita_tipo', 'US')
    custom_color = us_data.get('color')

    # Send progress
    send_progress_sync({
        "type": "progress",
        "action": "applying_material",
        "us_id": us_id,
        "periodo": periodo,
        "message": f"Applying material for US {us_id} ({periodo})"
    })

    # Create material
    mat_name = f"US_{us_id}_mat"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)

    # Create output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)

    # Link
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # Set color based on period or custom
    if custom_color:
        # Use custom color (hex to RGB)
        color = hex_to_rgb(custom_color)
    elif auto_color:
        color = get_period_color(periodo)
    else:
        color = (0.5, 0.5, 0.5, 1.0)

    bsdf.inputs['Base Color'].default_value = color

    # Set material properties based on unità_tipo
    if unita_tipo in ["Struttura", "Structure", "Muro"]:
        bsdf.inputs['Roughness'].default_value = 0.8  # Rough stone
        bsdf.inputs['Metallic'].default_value = 0.0
    elif unita_tipo in ["Strato", "Layer"]:
        bsdf.inputs['Roughness'].default_value = 0.9  # Very rough earth
        bsdf.inputs['Metallic'].default_value = 0.0
    else:
        bsdf.inputs['Roughness'].default_value = 0.7
        bsdf.inputs['Metallic'].default_value = 0.0

    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    logger.info(f"Applied material to US {us_id}: {periodo}")

    return mat


def get_period_color(periodo: str) -> Tuple[float, float, float, float]:
    """Get color based on archaeological period"""
    period_colors = {
        "Romano": (0.8, 0.3, 0.2, 1.0),  # Red-brown
        "Medieval": (0.5, 0.4, 0.3, 1.0),  # Brown
        "Medievale": (0.5, 0.4, 0.3, 1.0),
        "Preistorico": (0.7, 0.6, 0.4, 1.0),  # Tan
        "Prehistoric": (0.7, 0.6, 0.4, 1.0),
        "Etrusco": (0.3, 0.3, 0.6, 1.0),  # Blue
        "Etruscan": (0.3, 0.3, 0.6, 1.0),
        "Moderno": (0.6, 0.6, 0.6, 1.0),  # Gray
        "Modern": (0.6, 0.6, 0.6, 1.0),
    }

    return period_colors.get(periodo, (0.5, 0.5, 0.5, 1.0))


def hex_to_rgb(hex_color: str) -> Tuple[float, float, float, float]:
    """Convert hex color to RGB (0-1 range)"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b, 1.0)


# ============================================================================
# Command Handlers
# ============================================================================

def handle_build_stratigraphic_model(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build complete stratigraphic 3D model

    Receives:
    - session_id: Session identifier
    - site_name: Site name
    - proxies: List of proxy definitions with COMPLETE US data
    - graphml_data: GraphML relationships
    """
    try:
        session_id = params.get('session_id')
        site_name = params.get('site_name', 'Unknown Site')
        proxies = params.get('proxies', [])
        graphml_edges = params.get('graphml_edges', [])
        options = params.get('options', {})

        server_state.current_session = session_id

        logger.info(f"Building stratigraphic model for session {session_id}")
        logger.info(f"Site: {site_name}, Proxies: {len(proxies)}")

        # Send start message
        send_progress_sync({
            "type": "start",
            "session_id": session_id,
            "site_name": site_name,
            "total_proxies": len(proxies),
            "message": f"Starting construction of {len(proxies)} stratigraphic units"
        })

        # Create site collection
        collection_name = f"Site_{site_name}"
        if collection_name not in bpy.data.collections:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)
        else:
            collection = bpy.data.collections[collection_name]

        server_state.collections[collection_name] = collection

        # Create each proxy
        created_objects = []

        for i, proxy_data in enumerate(proxies):
            proxy_id = proxy_data.get('proxy_id')
            us_data = proxy_data.get('us_data', {})
            position = proxy_data.get('position', [0, 0, 0])

            # Create geometry
            obj = create_stratigraphic_geometry(
                proxy_id=proxy_id,
                us_data=us_data,
                position=tuple(position),
                graphml_edges=graphml_edges
            )

            # Apply material
            apply_archaeological_material(
                obj=obj,
                us_data=us_data,
                auto_color=options.get('auto_color', True)
            )

            # Add to collection
            collection.objects.link(obj)
            bpy.context.collection.objects.unlink(obj)

            # Store in state
            server_state.proxies[proxy_id] = obj
            created_objects.append(obj)

            # Send progress
            progress_pct = int(((i + 1) / len(proxies)) * 100)
            send_progress_sync({
                "type": "progress",
                "action": "created_us",
                "us_id": us_data.get('us_id'),
                "progress": progress_pct,
                "message": f"Created US {us_data.get('us_id')} ({i+1}/{len(proxies)})"
            })

            # Small delay for streaming effect
            time.sleep(0.1)

        # Send completion
        send_progress_sync({
            "type": "complete",
            "session_id": session_id,
            "created_count": len(created_objects),
            "message": f"Successfully created {len(created_objects)} stratigraphic units"
        })

        logger.info(f"Completed building model: {len(created_objects)} objects created")

        return {
            "status": "success",
            "result": {
                "session_id": session_id,
                "created_count": len(created_objects),
                "proxy_ids": [obj.name for obj in created_objects]
            },
            "message": f"Created {len(created_objects)} objects successfully"
        }

    except Exception as e:
        logger.error(f"Error building stratigraphic model: {e}", exc_info=True)
        send_progress_sync({
            "type": "error",
            "error": str(e),
            "message": f"Failed to build model: {e}"
        })
        return {
            "status": "error",
            "message": str(e)
        }


def handle_create_proxy(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle simple proxy creation (legacy compatibility)"""
    try:
        proxy_id = params.get('proxy_id')
        location = params.get('location', {'x': 0, 'y': 0, 'z': 0})
        scale = params.get('scale', {'x': 1, 'y': 1, 'z': 1})
        geometry = params.get('geometry', 'CUBE')

        # Create simple geometry
        if geometry == 'CUBE':
            bpy.ops.mesh.primitive_cube_add(
                location=(location['x'], location['y'], location['z']),
                scale=(scale['x'], scale['y'], scale['z'])
            )
        elif geometry == 'SPHERE':
            bpy.ops.mesh.primitive_uv_sphere_add(
                location=(location['x'], location['y'], location['z']),
                scale=(scale['x'], scale['y'], scale['z'])
            )

        obj = bpy.context.active_object
        obj.name = proxy_id

        server_state.proxies[proxy_id] = obj

        return {
            "status": "success",
            "result": {"proxy_id": proxy_id},
            "message": f"Created proxy {proxy_id}"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def handle_get_scene_info(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get current scene information"""
    try:
        return {
            "status": "success",
            "result": {
                "name": bpy.context.scene.name,
                "objects_count": len(bpy.data.objects),
                "proxies_count": len(server_state.proxies)
            },
            "message": "Scene info retrieved"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def handle_clear_scene(params: Dict[str, Any]) -> Dict[str, Any]:
    """Clear scene"""
    try:
        keep_camera = params.get('keep_camera', True)

        bpy.ops.object.select_all(action='SELECT')
        if keep_camera:
            bpy.ops.object.select_by_type(type='CAMERA', extend=False)
            bpy.ops.object.select_all(action='INVERT')

        bpy.ops.object.delete()

        server_state.proxies.clear()

        return {
            "status": "success",
            "message": "Scene cleared"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def handle_get_progress(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get progress messages"""
    try:
        # Return and clear progress messages
        messages = server_state.progress_messages.copy()
        server_state.progress_messages.clear()

        return {
            "status": "success",
            "result": {
                "messages": messages,
                "count": len(messages)
            },
            "message": f"Retrieved {len(messages)} progress messages"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Command dispatcher
COMMAND_HANDLERS = {
    "build_stratigraphic_model": handle_build_stratigraphic_model,
    "create_proxy": handle_create_proxy,
    "get_scene_info": handle_get_scene_info,
    "clear_scene": handle_clear_scene,
    "get_progress": handle_get_progress,
}


# ============================================================================
# TCP Socket Server
# ============================================================================

def handle_client_connection(client_socket: socket.socket, address: tuple):
    """Handle incoming client connection"""
    logger.info(f"Client connected from {address}")

    try:
        # Receive data
        data = b""
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            data += chunk
            if chunk.endswith(b"\n"):
                break

        if not data:
            return

        # Parse command
        command = json.loads(data.decode('utf-8').strip())
        command_type = command.get('type')
        params = command.get('params', {})

        logger.info(f"Received command: {command_type}")

        # Execute command
        if command_type in COMMAND_HANDLERS:
            response = COMMAND_HANDLERS[command_type](params)
        else:
            response = {
                "status": "error",
                "message": f"Unknown command type: {command_type}"
            }

        # Send response
        response_json = json.dumps(response) + "\n"
        client_socket.sendall(response_json.encode('utf-8'))

        logger.info(f"Command {command_type} completed: {response.get('status')}")

    except Exception as e:
        logger.error(f"Error handling client: {e}", exc_info=True)
        error_response = {"status": "error", "message": str(e)}
        try:
            client_socket.sendall((json.dumps(error_response) + "\n").encode('utf-8'))
        except:
            pass

    finally:
        client_socket.close()
        logger.info(f"Client disconnected: {address}")


def start_tcp_server(host: str = "localhost", port: int = 9876):
    """Start TCP socket server"""
    try:
        server_state.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_state.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_state.server_socket.bind((host, port))
        server_state.server_socket.listen(5)
        server_state.running = True

        logger.info(f"MCP Server started on {host}:{port}")

        while server_state.running:
            try:
                # Accept connection
                client_socket, address = server_state.server_socket.accept()

                # Handle in separate thread
                client_thread = threading.Thread(
                    target=handle_client_connection,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()

            except Exception as e:
                if server_state.running:
                    logger.error(f"Error accepting connection: {e}")

    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
    finally:
        if server_state.server_socket:
            server_state.server_socket.close()
        logger.info("MCP Server stopped")


def stop_tcp_server():
    """Stop TCP socket server"""
    server_state.running = False
    if server_state.server_socket:
        server_state.server_socket.close()
    server_state.server_socket = None


# ============================================================================
# Blender Operators
# ============================================================================

class PYARCHINIT_OT_start_server(bpy.types.Operator):
    """Start PyArchInit MCP Server"""
    bl_idname = "pyarchinit.start_server"
    bl_label = "Start MCP Server"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if server_state.running:
            self.report({'WARNING'}, "Server already running")
            return {'CANCELLED'}

        # Start server in background thread
        server_state.server_thread = threading.Thread(
            target=start_tcp_server,
            args=("localhost", 9876),
            daemon=True
        )
        server_state.server_thread.start()

        self.report({'INFO'}, "MCP Server started on port 9876")
        return {'FINISHED'}


class PYARCHINIT_OT_stop_server(bpy.types.Operator):
    """Stop PyArchInit MCP Server"""
    bl_idname = "pyarchinit.stop_server"
    bl_label = "Stop MCP Server"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if not server_state.running:
            self.report({'WARNING'}, "Server not running")
            return {'CANCELLED'}

        stop_tcp_server()

        self.report({'INFO'}, "MCP Server stopped")
        return {'FINISHED'}


class PYARCHINIT_PT_main_panel(bpy.types.Panel):
    """PyArchInit MCP Builder Panel"""
    bl_label = "PyArchInit MCP"
    bl_idname = "PYARCHINIT_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PyArchInit'

    def draw(self, context):
        layout = self.layout

        # Server status
        if server_state.running:
            layout.label(text="Status: Running", icon='LIGHT')
            layout.operator("pyarchinit.stop_server", icon='CANCEL')
        else:
            layout.label(text="Status: Stopped", icon='LIGHT_DATA')
            layout.operator("pyarchinit.start_server", icon='PLAY')

        layout.separator()

        # Info
        box = layout.box()
        box.label(text="Server Info:")
        box.label(text=f"Port: 9876")
        box.label(text=f"Proxies: {len(server_state.proxies)}")
        if server_state.current_session:
            box.label(text=f"Session: {server_state.current_session[:8]}...")


# ============================================================================
# Registration
# ============================================================================

classes = (
    PYARCHINIT_OT_start_server,
    PYARCHINIT_OT_stop_server,
    PYARCHINIT_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    logger.info("PyArchInit MCP Addon registered")


def unregister():
    # Stop server if running
    if server_state.running:
        stop_tcp_server()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    logger.info("PyArchInit MCP Addon unregistered")


if __name__ == "__main__":
    register()
