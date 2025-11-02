#!/usr/bin/env python3
"""
Test script to verify Socket.IO connection to PyArchInit server
This simulates what the Blender addon should do
"""

import socketio
import time

# Create Socket.IO client
sio = socketio.Client(reconnection=True, reconnection_attempts=5)

# Connection events
@sio.event
def connect():
    print("✅ Connected to PyArchInit server!")

    # Send blender_connect event
    sio.emit('blender_connect', {
        'blender_version': 'Test 1.0',
        'python_version': '3.11',
        'project_name': 'Test Project'
    })
    print("📤 Sent blender_connect event")

@sio.event
def disconnect():
    print("❌ Disconnected from server")

@sio.event
def blender_connect_ack(data):
    print(f"✅ Connection acknowledged by server: {data}")

@sio.event
def connect_error(data):
    print(f"❌ Connection error: {data}")

# Try to connect
print("🔌 Attempting to connect to http://localhost:5001...")
try:
    sio.connect('http://localhost:5001')
    print("⏳ Waiting 5 seconds to test connection...")
    time.sleep(5)

    # Send a test scene update
    print("📤 Sending test scene update...")
    sio.emit('blender_scene_update', {
        'scene_name': 'Test Scene',
        'objects': [
            {
                'object_name': 'TestCube',
                'object_type': 'MESH',
                'location': [0, 0, 0],
                'rotation': [0, 0, 0],
                'scale': [1, 1, 1]
            }
        ],
        'camera': {'location': [0, 0, 0], 'rotation': [0, 0, 0]},
        'timestamp': time.time()
    })
    print("✅ Test scene update sent")

    time.sleep(2)
    sio.disconnect()
    print("✅ Test completed successfully!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
