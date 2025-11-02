"""
WebSocket event handlers for real-time collaboration
"""

from flask import request
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from datetime import datetime
from typing import Dict, List

# Store online users: {sid: {username, user_id, connected_at}}
online_users: Dict[str, dict] = {}


def init_socketio_events(socketio):
    """
    Initialize WebSocket event handlers

    Args:
        socketio: Flask-SocketIO instance
    """

    @socketio.on('connect')
    def handle_connect():
        """
        Handle client connection

        Allows both authenticated web users and unauthenticated Blender clients.
        Blender clients will authenticate via the 'blender_connect' event.
        """
        sid = request.sid

        # Only track authenticated users (web clients)
        if current_user.is_authenticated:
            online_users[sid] = {
                'username': current_user.username,
                'user_id': current_user.id,
                'role': current_user.role,
                'connected_at': datetime.utcnow().isoformat()
            }

            print(f"[WebSocket] User connected: {current_user.username} (SID: {sid})")

            # Notify all clients about new user
            emit('user_joined', {
                'username': current_user.username,
                'user_id': current_user.id,
                'role': current_user.role,
                'timestamp': datetime.utcnow().isoformat()
            }, broadcast=True, skip_sid=sid)

            # Send current online users to the new client
            emit('online_users', {
                'users': [
                    {
                        'username': user['username'],
                        'user_id': user['user_id'],
                        'role': user['role']
                    }
                    for user in online_users.values()
                ]
            })
        else:
            # Allow unauthenticated connections (for Blender clients)
            # Blender clients will send 'blender_connect' event after connecting
            print(f"[WebSocket] Unauthenticated client connected (SID: {sid}) - likely Blender")

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        sid = request.sid

        if sid in online_users:
            user_info = online_users.pop(sid)
            print(f"[WebSocket] User disconnected: {user_info['username']} (SID: {sid})")

            # Notify all clients about user leaving
            emit('user_left', {
                'username': user_info['username'],
                'user_id': user_info['user_id'],
                'timestamp': datetime.utcnow().isoformat()
            }, broadcast=True)

    @socketio.on('get_online_users')
    def handle_get_online_users():
        """Send list of online users to requesting client"""
        emit('online_users', {
            'users': [
                {
                    'username': user['username'],
                    'user_id': user['user_id'],
                    'role': user['role']
                }
                for user in online_users.values()
            ]
        })

    @socketio.on('site_created')
    def handle_site_created(data):
        """Broadcast site creation"""
        if not current_user.is_authenticated:
            return

        emit('site_created', {
            'site_name': data.get('site_name'),
            'site_id': data.get('site_id'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('site_updated')
    def handle_site_updated(data):
        """Broadcast site update"""
        if not current_user.is_authenticated:
            return

        emit('site_updated', {
            'site_name': data.get('site_name'),
            'site_id': data.get('site_id'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('site_deleted')
    def handle_site_deleted(data):
        """Broadcast site deletion"""
        if not current_user.is_authenticated:
            return

        emit('site_deleted', {
            'site_name': data.get('site_name'),
            'site_id': data.get('site_id'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('us_created')
    def handle_us_created(data):
        """Broadcast US creation"""
        if not current_user.is_authenticated:
            return

        emit('us_created', {
            'site': data.get('site'),
            'us_number': data.get('us_number'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('us_updated')
    def handle_us_updated(data):
        """Broadcast US update"""
        if not current_user.is_authenticated:
            return

        emit('us_updated', {
            'site': data.get('site'),
            'us_number': data.get('us_number'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('us_deleted')
    def handle_us_deleted(data):
        """Broadcast US deletion"""
        if not current_user.is_authenticated:
            return

        emit('us_deleted', {
            'site': data.get('site'),
            'us_number': data.get('us_number'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('inventario_created')
    def handle_inventario_created(data):
        """Broadcast inventario creation"""
        if not current_user.is_authenticated:
            return

        emit('inventario_created', {
            'numero_inventario': data.get('numero_inventario'),
            'site': data.get('site'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('inventario_updated')
    def handle_inventario_updated(data):
        """Broadcast inventario update"""
        if not current_user.is_authenticated:
            return

        emit('inventario_updated', {
            'numero_inventario': data.get('numero_inventario'),
            'site': data.get('site'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('inventario_deleted')
    def handle_inventario_deleted(data):
        """Broadcast inventario deletion"""
        if not current_user.is_authenticated:
            return

        emit('inventario_deleted', {
            'numero_inventario': data.get('numero_inventario'),
            'site': data.get('site'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)


def broadcast_site_created(socketio, site_name, site_id):
    """Helper to broadcast site creation from server side"""
    socketio.emit('site_created', {
        'site_name': site_name,
        'site_id': site_id,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_site_updated(socketio, site_name, site_id):
    """Helper to broadcast site update from server side"""
    socketio.emit('site_updated', {
        'site_name': site_name,
        'site_id': site_id,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_us_created(socketio, site, us_number):
    """Helper to broadcast US creation from server side"""
    socketio.emit('us_created', {
        'site': site,
        'us_number': us_number,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_site_deleted(socketio, site_name, site_id):
    """Helper to broadcast site deletion from server side"""
    socketio.emit('site_deleted', {
        'site_name': site_name,
        'site_id': site_id,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_us_updated(socketio, site, us_number):
    """Helper to broadcast US update from server side"""
    socketio.emit('us_updated', {
        'site': site,
        'us_number': us_number,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_us_deleted(socketio, site, us_number):
    """Helper to broadcast US deletion from server side"""
    socketio.emit('us_deleted', {
        'site': site,
        'us_number': us_number,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_inventario_created(socketio, numero_inventario, site):
    """Helper to broadcast inventario creation from server side"""
    socketio.emit('inventario_created', {
        'numero_inventario': numero_inventario,
        'site': site,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_inventario_updated(socketio, numero_inventario, site):
    """Helper to broadcast inventario update from server side"""
    socketio.emit('inventario_updated', {
        'numero_inventario': numero_inventario,
        'site': site,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_inventario_deleted(socketio, numero_inventario, site):
    """Helper to broadcast inventario deletion from server side"""
    socketio.emit('inventario_deleted', {
        'numero_inventario': numero_inventario,
        'site': site,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


# ============================================================================
# BLENDER REAL-TIME STREAMING EVENTS
# ============================================================================

# Store Blender client connections: {sid: {blender_version, connected_at}}
blender_clients: Dict[str, dict] = {}


def init_blender_socketio_events(socketio):
    """
    Initialize Blender WebSocket event handlers for real-time streaming

    Architecture:
    Claude AI → Blender (via blender-mcp) → WebSocket → Viewer

    Args:
        socketio: Flask-SocketIO instance
    """

    @socketio.on('blender_connect')
    def handle_blender_connect(data):
        """
        Handle Blender client connection

        Args:
            data: {
                'blender_version': str,
                'python_version': str,
                'project_name': str (optional)
            }
        """
        sid = request.sid
        blender_clients[sid] = {
            'blender_version': data.get('blender_version', 'Unknown'),
            'python_version': data.get('python_version', 'Unknown'),
            'project_name': data.get('project_name'),
            'connected_at': datetime.utcnow().isoformat()
        }

        print(f"[Blender WebSocket] Blender connected: {data.get('blender_version')} (SID: {sid})")

        # Notify all web viewers that Blender is connected
        emit('blender_connected', {
            'blender_version': data.get('blender_version'),
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=sid)

        # Acknowledge connection to Blender
        emit('blender_connect_ack', {
            'status': 'connected',
            'sid': sid
        })

    @socketio.on('blender_disconnect')
    def handle_blender_disconnect():
        """Handle Blender client disconnection"""
        sid = request.sid

        if sid in blender_clients:
            blender_info = blender_clients.pop(sid)
            print(f"[Blender WebSocket] Blender disconnected: {blender_info['blender_version']} (SID: {sid})")

            # Notify all web viewers that Blender disconnected
            emit('blender_disconnected', {
                'timestamp': datetime.utcnow().isoformat()
            }, broadcast=True)

    @socketio.on('blender_scene_update')
    def handle_blender_scene_update(data):
        """
        Handle complete scene update from Blender

        Args:
            data: {
                'scene_name': str,
                'objects': List[dict],  # All scene objects
                'camera': dict,
                'lights': List[dict],
                'timestamp': str
            }
        """
        print(f"[Blender Stream] Scene update received: {data.get('scene_name')}")

        # Broadcast to all web viewers (except Blender itself)
        emit('blender_scene_update', data, broadcast=True, skip_sid=request.sid)

    @socketio.on('blender_object_created')
    def handle_blender_object_created(data):
        """
        Handle object creation in Blender

        Args:
            data: {
                'object_name': str,
                'object_type': str,  # 'MESH', 'LIGHT', 'CAMERA', etc.
                'location': [x, y, z],
                'rotation': [x, y, z],
                'scale': [x, y, z],
                'material': dict (optional),
                'proxy_id': str (optional),  # Link to PyArchInit US
                'timestamp': str
            }
        """
        print(f"[Blender Stream] Object created: {data.get('object_name')}")

        # Broadcast to all web viewers
        emit('blender_object_created', data, broadcast=True, skip_sid=request.sid)

    @socketio.on('blender_object_updated')
    def handle_blender_object_updated(data):
        """
        Handle object modification in Blender

        Args:
            data: {
                'object_name': str,
                'changes': dict,  # What changed (location, rotation, scale, material, etc.)
                'new_values': dict,  # New values for changed properties
                'timestamp': str
            }
        """
        # print(f"[Blender Stream] Object updated: {data.get('object_name')}")  # Can be verbose

        # Broadcast to all web viewers
        emit('blender_object_updated', data, broadcast=True, skip_sid=request.sid)

    @socketio.on('blender_object_deleted')
    def handle_blender_object_deleted(data):
        """
        Handle object deletion in Blender

        Args:
            data: {
                'object_name': str,
                'timestamp': str
            }
        """
        print(f"[Blender Stream] Object deleted: {data.get('object_name')}")

        # Broadcast to all web viewers
        emit('blender_object_deleted', data, broadcast=True, skip_sid=request.sid)

    @socketio.on('blender_material_updated')
    def handle_blender_material_updated(data):
        """
        Handle material update in Blender

        Args:
            data: {
                'material_name': str,
                'object_name': str,
                'base_color': [r, g, b, a],
                'roughness': float,
                'metallic': float,
                'timestamp': str
            }
        """
        print(f"[Blender Stream] Material updated: {data.get('material_name')}")

        # Broadcast to all web viewers
        emit('blender_material_updated', data, broadcast=True, skip_sid=request.sid)

    @socketio.on('blender_camera_update')
    def handle_blender_camera_update(data):
        """
        Handle camera movement in Blender

        Args:
            data: {
                'location': [x, y, z],
                'rotation': [x, y, z],
                'lens': float,
                'timestamp': str
            }
        """
        # Broadcast to all web viewers (for synchronized viewport)
        emit('blender_camera_update', data, broadcast=True, skip_sid=request.sid)

    @socketio.on('blender_build_progress')
    def handle_blender_build_progress(data):
        """
        Handle build progress updates from Claude AI → Blender

        Args:
            data: {
                'build_session_id': str,
                'site_name': str,
                'total_objects': int,
                'built_objects': int,
                'current_object': str,
                'percentage': float,
                'agent': str,  # 'architect', 'validator', 'texturizer', 'reconstructor'
                'message': str,
                'timestamp': str
            }
        """
        print(f"[Blender Build] {data.get('message')} ({data.get('percentage')}%)")

        # Broadcast to all web viewers
        emit('blender_build_progress', data, broadcast=True, skip_sid=request.sid)

    @socketio.on('get_blender_status')
    def handle_get_blender_status():
        """Send Blender connection status to requesting client"""
        is_connected = len(blender_clients) > 0

        emit('blender_status', {
            'connected': is_connected,
            'clients': [
                {
                    'blender_version': client['blender_version'],
                    'project_name': client.get('project_name')
                }
                for client in blender_clients.values()
            ] if is_connected else []
        })


def broadcast_blender_command(socketio, command, params):
    """
    Helper to send commands from web viewer to Blender

    Args:
        socketio: Flask-SocketIO instance
        command: str - Command name (e.g., 'build_proxies', 'delete_object', etc.)
        params: dict - Command parameters
    """
    socketio.emit('blender_command', {
        'command': command,
        'params': params,
        'timestamp': datetime.utcnow().isoformat()
    })
