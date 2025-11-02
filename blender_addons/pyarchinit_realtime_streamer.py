"""
PyArchInit Real-Time Streamer for Blender
Connects to PyArchInit WebSocket server and streams scene changes in real-time

Installation:
1. Open Blender
2. Edit → Preferences → Add-ons → Install
3. Select this file
4. Enable "PyArchInit Real-Time Streamer"
5. Configure WebSocket URL in addon preferences (default: http://localhost:5001)
6. Click "Connect to PyArchInit" in the 3D View sidebar (N panel)

Architecture:
Claude AI → Blender (via blender-mcp) → WebSocket → Web Viewer
"""

bl_info = {
    "name": "PyArchInit Real-Time Streamer",
    "author": "PyArchInit Team",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > PyArchInit",
    "description": "Stream Blender scene changes to PyArchInit web viewer in real-time",
    "category": "System",
}

import bpy
import socketio
import threading
import time
from bpy.app.handlers import persistent

# Global SocketIO client
sio_client = None
sio_thread = None
is_connected = False


class PyArchInitPreferences(bpy.types.AddonPreferences):
    """Addon preferences"""
    bl_idname = __name__

    websocket_url: bpy.props.StringProperty(
        name="WebSocket URL",
        description="URL of PyArchInit WebSocket server",
        default="http://localhost:5001"
    )

    auto_connect: bpy.props.BoolProperty(
        name="Auto-connect on startup",
        description="Automatically connect to WebSocket on Blender startup",
        default=False
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "websocket_url")
        layout.prop(self, "auto_connect")


class PYARCHINIT_OT_ConnectWebSocket(bpy.types.Operator):
    """Connect to PyArchInit WebSocket server"""
    bl_idname = "pyarchinit.connect_websocket"
    bl_label = "Connect to PyArchInit"
    bl_description = "Establish real-time connection to PyArchInit web viewer"

    def execute(self, context):
        global sio_client, is_connected

        if is_connected:
            self.report({'INFO'}, "Already connected to PyArchInit")
            return {'CANCELLED'}

        # Get WebSocket URL from preferences
        prefs = context.preferences.addons[__name__].preferences
        url = prefs.websocket_url

        # Create SocketIO client
        sio_client = socketio.Client(reconnection=True, reconnection_attempts=5)

        # Define event handlers
        @sio_client.event
        def connect():
            global is_connected
            is_connected = True
            print(f"[PyArchInit] Connected to {url}")

            # Send connection info
            sio_client.emit('blender_connect', {
                'blender_version': f"{bpy.app.version_string}",
                'python_version': f"{bpy.app.version[0]}.{bpy.app.version[1]}",
                'project_name': bpy.path.basename(bpy.context.blend_data.filepath) or "Untitled"
            })

        @sio_client.event
        def disconnect():
            global is_connected
            is_connected = False
            print("[PyArchInit] Disconnected from server")

        @sio_client.event
        def blender_connect_ack(data):
            print(f"[PyArchInit] Connection acknowledged: {data}")

        @sio_client.event
        def blender_command(data):
            """Receive commands from web viewer"""
            command = data.get('command')
            params = data.get('params', {})
            print(f"[PyArchInit] Received command: {command}")

            # Handle commands (can be extended)
            if command == 'get_scene_info':
                send_scene_update()

        # Connect in separate thread
        def connect_async():
            try:
                sio_client.connect(url)
                sio_client.wait()  # Keep connection alive
            except Exception as e:
                print(f"[PyArchInit] Connection error: {e}")
                is_connected = False

        global sio_thread
        sio_thread = threading.Thread(target=connect_async, daemon=True)
        sio_thread.start()

        self.report({'INFO'}, f"Connecting to {url}...")
        return {'FINISHED'}


class PYARCHINIT_OT_DisconnectWebSocket(bpy.types.Operator):
    """Disconnect from PyArchInit WebSocket server"""
    bl_idname = "pyarchinit.disconnect_websocket"
    bl_label = "Disconnect from PyArchInit"

    def execute(self, context):
        global sio_client, is_connected

        if not is_connected:
            self.report({'INFO'}, "Not connected")
            return {'CANCELLED'}

        try:
            sio_client.emit('blender_disconnect')
            sio_client.disconnect()
            is_connected = False
            self.report({'INFO'}, "Disconnected from PyArchInit")
        except Exception as e:
            self.report({'ERROR'}, f"Disconnect error: {e}")

        return {'FINISHED'}


class PYARCHINIT_PT_MainPanel(bpy.types.Panel):
    """PyArchInit Real-Time Streamer panel"""
    bl_label = "PyArchInit Streamer"
    bl_idname = "PYARCHINIT_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PyArchInit"

    def draw(self, context):
        layout = self.layout

        # Connection status
        if is_connected:
            layout.label(text="Status: Connected", icon='LINKED')
            layout.operator("pyarchinit.disconnect_websocket", icon='UNLINKED')
            layout.separator()
            layout.operator("pyarchinit.send_scene_update", icon='FILE_REFRESH')
        else:
            layout.label(text="Status: Disconnected", icon='UNLINKED')
            layout.operator("pyarchinit.connect_websocket", icon='LINKED')


class PYARCHINIT_OT_SendSceneUpdate(bpy.types.Operator):
    """Send complete scene update to web viewer"""
    bl_idname = "pyarchinit.send_scene_update"
    bl_label = "Send Scene Update"

    def execute(self, context):
        if not is_connected:
            self.report({'ERROR'}, "Not connected to PyArchInit")
            return {'CANCELLED'}

        send_scene_update()
        self.report({'INFO'}, "Scene update sent")
        return {'FINISHED'}


def extract_mesh_data(obj):
    """Extract vertices and faces from a mesh object"""
    if obj.type != 'MESH':
        return None

    # Apply modifiers to get evaluated mesh
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()

    # Extract vertices (world space coordinates)
    vertices = []
    for v in mesh.vertices:
        # Transform to world space
        world_co = obj.matrix_world @ v.co
        vertices.append([world_co.x, world_co.y, world_co.z])

    # Extract faces (convert to triangles)
    faces = []
    mesh.calc_loop_triangles()
    for tri in mesh.loop_triangles:
        faces.append([tri.vertices[0], tri.vertices[1], tri.vertices[2]])

    obj_eval.to_mesh_clear()

    return {
        'vertices': vertices,
        'faces': faces,
        'vertex_count': len(vertices),
        'face_count': len(faces)
    }


def send_scene_update():
    """Send complete scene state to web viewer"""
    global sio_client

    if not is_connected or not sio_client:
        return

    scene = bpy.context.scene

    # Collect all scene objects
    objects = []
    for obj in scene.objects:
        obj_data = {
            'object_name': obj.name,
            'object_type': obj.type,
            'location': list(obj.location),
            'rotation': list(obj.rotation_euler),
            'scale': list(obj.scale),
            'visible': not obj.hide_get()
        }

        # Add material info if available
        if obj.type == 'MESH' and obj.active_material:
            mat = obj.active_material
            if mat.use_nodes:
                bsdf = mat.node_tree.nodes.get('Principled BSDF')
                if bsdf:
                    base_color = bsdf.inputs['Base Color'].default_value
                    obj_data['material'] = {
                        'name': mat.name,
                        'base_color': list(base_color),
                        'roughness': bsdf.inputs['Roughness'].default_value,
                        'metallic': bsdf.inputs['Metallic'].default_value
                    }

        # Extract mesh geometry data
        if obj.type == 'MESH':
            mesh_data = extract_mesh_data(obj)
            if mesh_data:
                obj_data['mesh_data'] = mesh_data
                print(f"[PyArchInit] Extracted {mesh_data['vertex_count']} vertices, {mesh_data['face_count']} faces from {obj.name}")

        # Check for PyArchInit proxy metadata
        if 'proxy_id' in obj:
            obj_data['proxy_id'] = obj['proxy_id']

        objects.append(obj_data)

    # Send scene update
    sio_client.emit('blender_scene_update', {
        'scene_name': scene.name,
        'objects': objects,
        'camera': {
            'location': list(scene.camera.location) if scene.camera else [0, 0, 0],
            'rotation': list(scene.camera.rotation_euler) if scene.camera else [0, 0, 0]
        },
        'timestamp': time.time()
    })

    print(f"[PyArchInit] Sent scene update with {len(objects)} objects")


@persistent
def on_depsgraph_update(scene, depsgraph):
    """Handler for scene changes - broadcasts updates to web viewer"""
    global is_connected, sio_client

    if not is_connected or not sio_client:
        return

    # Send updates for modified objects
    for update in depsgraph.updates:
        if isinstance(update.id, bpy.types.Object):
            obj = update.id

            # Object transformation changed
            if update.is_updated_transform:
                sio_client.emit('blender_object_updated', {
                    'object_name': obj.name,
                    'changes': ['location', 'rotation', 'scale'],
                    'new_values': {
                        'location': list(obj.location),
                        'rotation': list(obj.rotation_euler),
                        'scale': list(obj.scale)
                    },
                    'timestamp': time.time()
                })

            # Object geometry changed - send full mesh data
            elif update.is_updated_geometry and obj.type == 'MESH':
                mesh_data = extract_mesh_data(obj)
                if mesh_data:
                    sio_client.emit('blender_object_updated', {
                        'object_name': obj.name,
                        'changes': ['geometry'],
                        'mesh_data': mesh_data,
                        'timestamp': time.time()
                    })
                    print(f"[PyArchInit] Geometry updated for {obj.name}: {mesh_data['vertex_count']} vertices, {mesh_data['face_count']} faces")


# Registration
classes = (
    PyArchInitPreferences,
    PYARCHINIT_OT_ConnectWebSocket,
    PYARCHINIT_OT_DisconnectWebSocket,
    PYARCHINIT_OT_SendSceneUpdate,
    PYARCHINIT_PT_MainPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register depsgraph update handler
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)

    print("[PyArchInit] Real-Time Streamer registered")


def unregister():
    global is_connected, sio_client

    # Disconnect if connected
    if is_connected and sio_client:
        try:
            sio_client.disconnect()
        except:
            pass

    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # Remove handler
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)

    print("[PyArchInit] Real-Time Streamer unregistered")


if __name__ == "__main__":
    register()
