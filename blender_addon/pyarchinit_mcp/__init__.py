"""
PyArchInit MCP Addon for Blender

Blender addon that receives commands from PyArchInit-Mini via TCP socket
to generate 3D stratigraphic visualizations.

Installation:
    1. Copy this folder to Blender's addons directory
    2. Enable the addon in Blender Preferences > Add-ons
    3. Start the MCP server from the 3D View sidebar (N panel)
"""

bl_info = {
    "name": "PyArchInit MCP Connector",
    "author": "PyArchInit Team",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > PyArchInit",
    "description": "MCP socket server for PyArchInit stratigraphic 3D generation",
    "category": "3D View",
    "doc_url": "https://github.com/pyarchinit/pyarchinit-mini",
}

import bpy
import socket
import threading
import json
import logging
from mathutils import Vector, Euler
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Socket Server
# ============================================================================

class MCPSocketServer:
    """
    TCP Socket server that receives commands from PyArchInit
    """

    def __init__(self, host='0.0.0.0', port=9876):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.thread = None

    def start(self):
        """Start the socket server in a background thread"""
        if self.running:
            logger.warning("Server already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        logger.info(f"MCP Server started on {self.host}:{self.port}")

    def stop(self):
        """Stop the socket server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        logger.info("MCP Server stopped")

    def _run_server(self):
        """Main server loop (runs in background thread)"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # Allow periodic checking of running flag

            logger.info(f"Listening for connections on {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    logger.info(f"Client connected from {address}")

                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket,),
                        daemon=True
                    )
                    client_thread.start()

                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")

        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def _handle_client(self, client_socket):
        """Handle a client connection"""
        try:
            buffer = ""
            while True:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                buffer += data

                # Process complete messages (ended with newline)
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message.strip():
                        response = self._process_command(message.strip())
                        client_socket.sendall((response + '\n').encode('utf-8'))

        except Exception as e:
            logger.error(f"Client handling error: {e}")
        finally:
            client_socket.close()
            logger.info("Client disconnected")

    def _process_command(self, message: str) -> str:
        """
        Process a command from the client

        Args:
            message: JSON command string

        Returns:
            JSON response string
        """
        try:
            command = json.loads(message)
            command_type = command.get('type')
            params = command.get('params', {})

            logger.info(f"Processing command: {command_type}")

            # Dispatch to appropriate handler
            handler = COMMAND_HANDLERS.get(command_type)
            if not handler:
                return json.dumps({
                    'status': 'error',
                    'message': f"Unknown command type: {command_type}"
                })

            # Execute command directly
            # Note: Most Blender API operations are thread-safe for reading
            # For commands that modify the scene, Blender handles thread safety internally
            try:
                result = handler(params)
            except Exception as e:
                logger.error(f"Command execution error: {e}", exc_info=True)
                result = {
                    'status': 'error',
                    'message': str(e)
                }

            return json.dumps(result)

        except json.JSONDecodeError as e:
            return json.dumps({
                'status': 'error',
                'message': f"Invalid JSON: {e}"
            })
        except Exception as e:
            logger.error(f"Command processing error: {e}", exc_info=True)
            return json.dumps({
                'status': 'error',
                'message': str(e)
            })


# ============================================================================
# Command Handlers
# ============================================================================

def handle_create_proxy(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a proxy object"""
    proxy_id = params['proxy_id']
    location = params['location']
    scale = params['scale']
    rotation = params.get('rotation', {'x': 0, 'y': 0, 'z': 0})
    geometry = params.get('geometry', 'CUBE')

    # Create object based on geometry type
    if geometry == 'CUBE':
        bpy.ops.mesh.primitive_cube_add()
    elif geometry == 'SPHERE':
        bpy.ops.mesh.primitive_uv_sphere_add()
    elif geometry == 'CYLINDER':
        bpy.ops.mesh.primitive_cylinder_add()
    elif geometry == 'PLANE':
        bpy.ops.mesh.primitive_plane_add()
    else:
        return {'status': 'error', 'message': f"Unknown geometry: {geometry}"}

    obj = bpy.context.active_object
    obj.name = f"Proxy_{proxy_id}"
    obj.location = Vector((location['x'], location['y'], location['z']))
    obj.scale = Vector((scale['x'], scale['y'], scale['z']))
    obj.rotation_euler = Euler((rotation['x'], rotation['y'], rotation['z']))

    # Add custom property to track proxy ID
    obj["proxy_id"] = proxy_id

    return {
        'status': 'success',
        'result': {
            'proxy_id': proxy_id,
            'object_name': obj.name
        },
        'message': f"Created proxy {proxy_id}"
    }


def handle_apply_material(params: Dict[str, Any]) -> Dict[str, Any]:
    """Apply material to proxy"""
    proxy_id = params['proxy_id']
    material_name = params['material_name']
    base_color = params['base_color']
    roughness = params.get('roughness', 0.7)
    metallic = params.get('metallic', 0.0)

    # Find proxy object
    obj = find_proxy_by_id(proxy_id)
    if not obj:
        return {'status': 'error', 'message': f"Proxy {proxy_id} not found"}

    # Create or get material
    mat = bpy.data.materials.get(material_name)
    if not mat:
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True

    # Set material properties
    nodes = mat.node_tree.nodes
    principled = nodes.get('Principled BSDF')
    if principled:
        principled.inputs['Base Color'].default_value = (
            base_color['r'], base_color['g'], base_color['b'], base_color['a']
        )
        principled.inputs['Roughness'].default_value = roughness
        principled.inputs['Metallic'].default_value = metallic

    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    return {
        'status': 'success',
        'result': {'material_name': material_name},
        'message': f"Applied material to proxy {proxy_id}"
    }


def handle_set_visibility(params: Dict[str, Any]) -> Dict[str, Any]:
    """Set proxy visibility"""
    proxy_id = params['proxy_id']
    visible = params['visible']

    obj = find_proxy_by_id(proxy_id)
    if not obj:
        return {'status': 'error', 'message': f"Proxy {proxy_id} not found"}

    obj.hide_viewport = not visible
    obj.hide_render = not visible

    return {
        'status': 'success',
        'result': {'visible': visible},
        'message': f"Set proxy {proxy_id} visibility to {visible}"
    }


def handle_set_transparency(params: Dict[str, Any]) -> Dict[str, Any]:
    """Set proxy transparency"""
    proxy_id = params['proxy_id']
    alpha = params['alpha']

    obj = find_proxy_by_id(proxy_id)
    if not obj:
        return {'status': 'error', 'message': f"Proxy {proxy_id} not found"}

    # Update material alpha
    if obj.data.materials:
        mat = obj.data.materials[0]
        if mat.use_nodes:
            principled = mat.node_tree.nodes.get('Principled BSDF')
            if principled:
                color = principled.inputs['Base Color'].default_value
                principled.inputs['Base Color'].default_value = (color[0], color[1], color[2], alpha)

                # Enable transparency
                mat.blend_method = 'BLEND'

    return {
        'status': 'success',
        'result': {'alpha': alpha},
        'message': f"Set proxy {proxy_id} transparency to {alpha}"
    }


def handle_assign_to_collection(params: Dict[str, Any]) -> Dict[str, Any]:
    """Assign proxy to collection"""
    proxy_id = params['proxy_id']
    collection_name = params['collection_name']

    obj = find_proxy_by_id(proxy_id)
    if not obj:
        return {'status': 'error', 'message': f"Proxy {proxy_id} not found"}

    # Get or create collection
    collection = bpy.data.collections.get(collection_name)
    if not collection:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)

    # Move object to collection
    for coll in obj.users_collection:
        coll.objects.unlink(obj)
    collection.objects.link(obj)

    return {
        'status': 'success',
        'result': {'collection': collection_name},
        'message': f"Assigned proxy {proxy_id} to collection {collection_name}"
    }


def handle_export_gltf(params: Dict[str, Any]) -> Dict[str, Any]:
    """Export scene to glTF"""
    output_path = params['output_path']
    selected_only = params.get('selected_only', False)

    try:
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            use_selection=selected_only,
            export_format='GLTF_SEPARATE'
        )

        return {
            'status': 'success',
            'result': {'output_path': output_path},
            'message': f"Exported to {output_path}"
        }
    except Exception as e:
        return {'status': 'error', 'message': f"Export failed: {e}"}


def handle_get_scene_info(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get current scene information"""
    scene = bpy.context.scene

    # Count proxy objects
    proxy_count = sum(1 for obj in scene.objects if "proxy_id" in obj)

    return {
        'status': 'success',
        'result': {
            'name': scene.name,
            'frame_current': scene.frame_current,
            'object_count': len(scene.objects),
            'proxy_count': proxy_count,
            'collections': [c.name for c in scene.collection.children]
        },
        'message': 'Scene info retrieved'
    }


def handle_clear_scene(params: Dict[str, Any]) -> Dict[str, Any]:
    """Clear all objects from scene"""
    keep_camera = params.get('keep_camera', True)

    deleted_count = 0
    for obj in list(bpy.context.scene.objects):
        if keep_camera and obj.type in ('CAMERA', 'LIGHT'):
            continue
        bpy.data.objects.remove(obj, do_unlink=True)
        deleted_count += 1

    return {
        'status': 'success',
        'result': {'deleted_count': deleted_count},
        'message': f"Cleared {deleted_count} objects"
    }


def handle_create_collection(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a collection"""
    collection_name = params['collection_name']
    parent_name = params.get('parent')

    # Create collection
    collection = bpy.data.collections.new(collection_name)

    # Link to parent or scene
    if parent_name:
        parent = bpy.data.collections.get(parent_name)
        if parent:
            parent.children.link(collection)
        else:
            return {'status': 'error', 'message': f"Parent collection {parent_name} not found"}
    else:
        bpy.context.scene.collection.children.link(collection)

    return {
        'status': 'success',
        'result': {'collection_name': collection_name},
        'message': f"Created collection {collection_name}"
    }


def handle_batch_create_proxies(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create multiple proxies in batch"""
    proxies = params['proxies']
    created_ids = []

    for proxy_def in proxies:
        try:
            result = handle_create_proxy(proxy_def)
            if result['status'] == 'success':
                created_ids.append(proxy_def['proxy_id'])
        except Exception as e:
            logger.error(f"Error creating proxy {proxy_def.get('proxy_id')}: {e}")

    return {
        'status': 'success',
        'result': {
            'created_count': len(created_ids),
            'proxy_ids': created_ids
        },
        'message': f"Created {len(created_ids)}/{len(proxies)} proxies"
    }


def handle_execute_python(params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute arbitrary Python code (use with caution!)"""
    code = params['code']

    try:
        exec_globals = {'bpy': bpy}
        exec(code, exec_globals)
        return {
            'status': 'success',
            'result': {},
            'message': 'Code executed successfully'
        }
    except Exception as e:
        return {'status': 'error', 'message': f"Execution error: {e}"}


# Command handler registry
COMMAND_HANDLERS = {
    'create_proxy': handle_create_proxy,
    'apply_material': handle_apply_material,
    'set_visibility': handle_set_visibility,
    'set_transparency': handle_set_transparency,
    'assign_to_collection': handle_assign_to_collection,
    'export_gltf': handle_export_gltf,
    'get_scene_info': handle_get_scene_info,
    'clear_scene': handle_clear_scene,
    'create_collection': handle_create_collection,
    'batch_create_proxies': handle_batch_create_proxies,
    'execute_python': handle_execute_python,
}


# ============================================================================
# Helper Functions
# ============================================================================

def find_proxy_by_id(proxy_id: str):
    """Find proxy object by ID custom property"""
    for obj in bpy.context.scene.objects:
        if obj.get("proxy_id") == proxy_id:
            return obj
    return None


# ============================================================================
# Blender UI Panel
# ============================================================================

class PYARCHINIT_PT_MCPPanel(bpy.types.Panel):
    """PyArchInit MCP Server Control Panel"""
    bl_label = "PyArchInit MCP"
    bl_idname = "PYARCHINIT_PT_mcp_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PyArchInit'

    def draw(self, context):
        layout = self.layout
        props = context.scene.pyarchinit_mcp_props

        layout.label(text="MCP Socket Server", icon='NETWORK_DRIVE')

        # Server controls
        row = layout.row()
        if not props.server_running:
            row.operator("pyarchinit_mcp.start_server", icon='PLAY')
        else:
            row.operator("pyarchinit_mcp.stop_server", icon='PAUSE')

        # Status
        layout.separator()
        status_text = "Running" if props.server_running else "Stopped"
        status_icon = 'CHECKMARK' if props.server_running else 'X'
        layout.label(text=f"Status: {status_text}", icon=status_icon)

        # Settings
        layout.separator()
        layout.prop(props, "server_port")
        layout.label(text=f"Host: 0.0.0.0")


# ============================================================================
# Operators
# ============================================================================

class PYARCHINIT_OT_StartServer(bpy.types.Operator):
    """Start MCP Socket Server"""
    bl_idname = "pyarchinit_mcp.start_server"
    bl_label = "Start Server"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.pyarchinit_mcp_props

        if not hasattr(bpy, 'pyarchinit_mcp_server'):
            bpy.pyarchinit_mcp_server = MCPSocketServer(port=props.server_port)

        bpy.pyarchinit_mcp_server.start()
        props.server_running = True

        self.report({'INFO'}, f"MCP Server started on port {props.server_port}")
        return {'FINISHED'}


class PYARCHINIT_OT_StopServer(bpy.types.Operator):
    """Stop MCP Socket Server"""
    bl_idname = "pyarchinit_mcp.stop_server"
    bl_label = "Stop Server"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.pyarchinit_mcp_props

        if hasattr(bpy, 'pyarchinit_mcp_server'):
            bpy.pyarchinit_mcp_server.stop()

        props.server_running = False

        self.report({'INFO'}, "MCP Server stopped")
        return {'FINISHED'}


# ============================================================================
# Properties
# ============================================================================

class PyArchInitMCPProperties(bpy.types.PropertyGroup):
    """MCP Server Properties"""

    server_running: bpy.props.BoolProperty(
        name="Server Running",
        default=False
    )

    server_port: bpy.props.IntProperty(
        name="Port",
        description="Socket server port",
        default=9876,
        min=1024,
        max=65535
    )


# ============================================================================
# Registration
# ============================================================================

classes = (
    PyArchInitMCPProperties,
    PYARCHINIT_PT_MCPPanel,
    PYARCHINIT_OT_StartServer,
    PYARCHINIT_OT_StopServer,
)


def register():
    """Register addon"""
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.pyarchinit_mcp_props = bpy.props.PointerProperty(
        type=PyArchInitMCPProperties
    )

    logger.info("PyArchInit MCP Addon registered")


def unregister():
    """Unregister addon"""
    # Stop server if running
    if hasattr(bpy, 'pyarchinit_mcp_server'):
        bpy.pyarchinit_mcp_server.stop()
        delattr(bpy, 'pyarchinit_mcp_server')

    del bpy.types.Scene.pyarchinit_mcp_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    logger.info("PyArchInit MCP Addon unregistered")


if __name__ == "__main__":
    register()
