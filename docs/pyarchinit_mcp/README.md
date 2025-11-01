# PyArchInit MCP Blender Addon

Blender addon that receives commands from PyArchInit-Mini to generate 3D stratigraphic visualizations via MCP (Model Context Protocol).

## Features

- **TCP Socket Server**: Receives commands from PyArchInit on port 9876
- **Proxy Generation**: Creates 3D proxy objects for stratigraphic units
- **Material Management**: Applies materials with customizable colors
- **Visibility Control**: Show/hide proxies dynamically
- **glTF Export**: Export scenes for web visualization
- **Collection Management**: Organize proxies by period/area
- **Batch Operations**: Create multiple proxies efficiently

## Requirements

- Blender 3.0 or higher
- Python 3.7+ (included with Blender)

## Installation

### Method 1: Manual Installation

1. **Copy addon folder**:
   ```bash
   # Linux
   cp -r blender_addon/pyarchinit_mcp ~/.config/blender/3.x/scripts/addons/

   # macOS
   cp -r blender_addon/pyarchinit_mcp ~/Library/Application\ Support/Blender/3.x/scripts/addons/

   # Windows
   copy blender_addon\pyarchinit_mcp %APPDATA%\Blender Foundation\Blender\3.x\scripts\addons\
   ```

2. **Enable addon in Blender**:
   - Open Blender
   - Go to Edit → Preferences → Add-ons
   - Search for "PyArchInit"
   - Enable "3D View: PyArchInit MCP Connector"

### Method 2: Install from ZIP

1. **Create ZIP file**:
   ```bash
   cd blender_addon
   zip -r pyarchinit_mcp.zip pyarchinit_mcp/
   ```

2. **Install in Blender**:
   - Open Blender
   - Go to Edit → Preferences → Add-ons
   - Click "Install..." button
   - Select `pyarchinit_mcp.zip`
   - Enable the addon

## Usage

### 1. Start MCP Server

1. Open Blender's 3D View
2. Press `N` to open the sidebar
3. Go to the "PyArchInit" tab
4. Click "Start Server"
5. Server will listen on `0.0.0.0:9876`

### 2. Connect from PyArchInit

In PyArchInit web interface:
- Navigate to 3D Builder section
- Click "Test Blender Connection"
- If successful, you'll see "Connected" status

### 3. Generate 3D Models

Use Claude's prompt interface to generate stratigraphic 3D models:

```
Create a 3D model of Site 1, showing US 1-10 with
Bronze Age layers in brown and Iron Age layers in gray
```

The addon will:
1. Receive commands from PyArchInit
2. Create proxy objects in Blender
3. Apply materials based on chronology
4. Export to glTF for web viewing

## Supported Commands

### create_proxy
Create a 3D proxy object
```json
{
  "type": "create_proxy",
  "params": {
    "proxy_id": "US_1",
    "location": {"x": 0, "y": 0, "z": 0},
    "scale": {"x": 5, "y": 5, "z": 1},
    "rotation": {"x": 0, "y": 0, "z": 0},
    "geometry": "CUBE"
  }
}
```

### apply_material
Apply material to proxy
```json
{
  "type": "apply_material",
  "params": {
    "proxy_id": "US_1",
    "material_name": "Bronze_Age",
    "base_color": {"r": 0.6, "g": 0.4, "b": 0.2, "a": 1.0},
    "roughness": 0.7,
    "metallic": 0.0
  }
}
```

### set_visibility
Show/hide proxy
```json
{
  "type": "set_visibility",
  "params": {
    "proxy_id": "US_1",
    "visible": true
  }
}
```

### set_transparency
Set proxy transparency
```json
{
  "type": "set_transparency",
  "params": {
    "proxy_id": "US_1",
    "alpha": 0.5
  }
}
```

### export_gltf
Export scene to glTF
```json
{
  "type": "export_gltf",
  "params": {
    "output_path": "/path/to/output.gltf",
    "selected_only": false
  }
}
```

### get_scene_info
Get current scene information
```json
{
  "type": "get_scene_info",
  "params": {}
}
```

### clear_scene
Clear all objects
```json
{
  "type": "clear_scene",
  "params": {
    "keep_camera": true
  }
}
```

### batch_create_proxies
Create multiple proxies at once
```json
{
  "type": "batch_create_proxies",
  "params": {
    "proxies": [
      {
        "proxy_id": "US_1",
        "location": {"x": 0, "y": 0, "z": 0},
        "scale": {"x": 5, "y": 5, "z": 1},
        "geometry": "CUBE"
      },
      {
        "proxy_id": "US_2",
        "location": {"x": 0, "y": 0, "z": 1},
        "scale": {"x": 5, "y": 5, "z": 1},
        "geometry": "CUBE"
      }
    ]
  }
}
```

## Configuration

### Change Server Port

Default port is 9876. To change:
1. Open addon panel (N → PyArchInit)
2. Modify "Port" value
3. Restart server

### Firewall Settings

Ensure port 9876 is open for incoming connections:

```bash
# Linux (ufw)
sudo ufw allow 9876/tcp

# macOS
# Add rule in System Preferences → Security & Privacy → Firewall → Options

# Windows
# Add inbound rule in Windows Firewall
```

## Testing

### Test from Python

```bash
cd pyarchinit_mini/mcp_server
python blender_client.py --test
```

Expected output:
```
Connected successfully. Scene: Scene
```

### Test from Blender Console

1. In Blender, go to Scripting workspace
2. Run this code:
```python
import bpy

# Start server
bpy.ops.pyarchinit_mcp.start_server()

# Check status
props = bpy.context.scene.pyarchinit_mcp_props
print(f"Server running: {props.server_running}")
print(f"Port: {props.server_port}")
```

## Troubleshooting

### Server won't start
- Check if port 9876 is already in use
- Try changing the port
- Check Blender console for errors

### Connection refused
- Ensure server is started in Blender
- Check firewall settings
- Verify PyArchInit is using correct host/port

### Commands timeout
- Increase timeout in BlenderClient (default 30s)
- Check for Blender console errors
- Verify command JSON is valid

### Objects not appearing
- Check if proxies are created: Objects panel in Outliner
- Verify location/scale parameters
- Check viewport shading mode (Solid/Material Preview)

## Development

### Enable Debug Logging

In Blender Python console:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### Add Custom Commands

1. Add handler function in `__init__.py`:
```python
def handle_my_command(params: Dict[str, Any]) -> Dict[str, Any]:
    # Implementation
    return {
        'status': 'success',
        'result': {},
        'message': 'Command executed'
    }
```

2. Register in COMMAND_HANDLERS:
```python
COMMAND_HANDLERS = {
    # ... existing handlers ...
    'my_command': handle_my_command,
}
```

3. Add client method in `blender_client.py`:
```python
def my_command(self, params):
    response = self.send_command('my_command', params)
    return response.result or {}
```

## Architecture

```
┌─────────────────┐
│ PyArchInit Web  │
│   + Frontend    │
└────────┬────────┘
         │ HTTP/WS
┌────────┴────────┐
│ PyArchInit API  │
│  + MCP Server   │
└────────┬────────┘
         │ TCP Socket (port 9876)
         │ JSON Protocol
┌────────┴────────┐
│ Blender Addon   │
│  + Socket Svr   │
│  + Cmd Handlers │
│  + 3D Engine    │
└─────────────────┘
```

## License

Same as PyArchInit-Mini (GPL-3.0)

## Support

- Issues: https://github.com/pyarchinit/pyarchinit-mini/issues
- Documentation: https://pyarchinit.github.io/pyarchinit-mini
- Community: PyArchInit mailing list

## Credits

Developed by the PyArchInit Team as part of the 3D Builder feature for archaeological stratigraphic visualization.
