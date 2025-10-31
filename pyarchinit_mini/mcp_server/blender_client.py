"""
Blender Client

TCP socket client for communicating with Blender MCP addon.
Sends JSON commands to Blender and receives responses.
"""

import socket
import json
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class BlenderCommand:
    """Blender command structure"""

    command_type: str
    params: Dict[str, Any]


@dataclass
class BlenderResponse:
    """Blender response structure"""

    status: str  # "success" or "error"
    result: Optional[Dict[str, Any]] = None
    message: str = ""


class BlenderConnectionError(Exception):
    """Raised when connection to Blender fails"""

    pass


class BlenderCommandError(Exception):
    """Raised when Blender command execution fails"""

    pass


class BlenderClient:
    """
    TCP Socket client for Blender MCP addon

    Communicates with Blender addon socket server (default port 9876)
    using JSON-encoded messages.

    Protocol:
        Request:  {"type": "command_type", "params": {...}}
        Response: {"status": "success|error", "result": {...}, "message": "..."}
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9876,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize Blender client

        Args:
            host: Blender host address
            port: Blender socket port
            timeout: Socket timeout in seconds
            max_retries: Maximum connection retry attempts
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.socket: Optional[socket.socket] = None
        self.connected = False

    def connect(self) -> bool:
        """
        Connect to Blender socket server

        Returns:
            True if connection successful

        Raises:
            BlenderConnectionError: If connection fails after retries
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"Connecting to Blender at {self.host}:{self.port} "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )

                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(self.timeout)
                self.socket.connect((self.host, self.port))

                self.connected = True
                logger.info(f"Connected to Blender successfully")
                return True

            except socket.timeout:
                logger.warning(f"Connection timeout (attempt {attempt + 1})")
                time.sleep(1)
            except ConnectionRefusedError:
                logger.warning(
                    f"Connection refused - is Blender running? (attempt {attempt + 1})"
                )
                time.sleep(2)
            except Exception as e:
                logger.error(f"Connection error: {e}")
                time.sleep(1)

        raise BlenderConnectionError(
            f"Failed to connect to Blender after {self.max_retries} attempts. "
            f"Ensure Blender is running with MCP addon enabled on port {self.port}."
        )

    def disconnect(self):
        """Disconnect from Blender"""
        if self.socket:
            try:
                self.socket.close()
                logger.info("Disconnected from Blender")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.socket = None
                self.connected = False

    def send_command(
        self, command_type: str, params: Dict[str, Any]
    ) -> BlenderResponse:
        """
        Send command to Blender

        Args:
            command_type: Type of command (e.g., "create_object", "apply_material")
            params: Command parameters

        Returns:
            BlenderResponse with status, result, message

        Raises:
            BlenderConnectionError: If not connected
            BlenderCommandError: If command execution fails
        """
        if not self.connected:
            raise BlenderConnectionError("Not connected to Blender")

        # Construct command
        command = {"type": command_type, "params": params}

        try:
            # Send command
            message = json.dumps(command) + "\n"
            self.socket.sendall(message.encode("utf-8"))
            logger.debug(f"Sent command: {command_type}")

            # Receive response
            response_data = self._receive_response()
            response = json.loads(response_data)

            # Parse response
            blender_response = BlenderResponse(
                status=response.get("status", "error"),
                result=response.get("result"),
                message=response.get("message", ""),
            )

            if blender_response.status == "error":
                raise BlenderCommandError(
                    f"Blender command '{command_type}' failed: {blender_response.message}"
                )

            logger.debug(f"Command '{command_type}' successful")
            return blender_response

        except socket.timeout:
            raise BlenderConnectionError(f"Timeout waiting for response from Blender")
        except json.JSONDecodeError as e:
            raise BlenderCommandError(f"Invalid JSON response from Blender: {e}")
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            raise

    def _receive_response(self, buffer_size: int = 4096) -> str:
        """
        Receive response from Blender

        Args:
            buffer_size: Socket buffer size

        Returns:
            Response string
        """
        response_parts = []
        while True:
            chunk = self.socket.recv(buffer_size).decode("utf-8")
            if not chunk:
                break
            response_parts.append(chunk)
            # Check if we received a complete message (ends with newline)
            if chunk.endswith("\n"):
                break

        return "".join(response_parts).strip()

    # ========================================================================
    # High-level Blender Commands
    # ========================================================================

    def create_proxy(
        self,
        proxy_id: str,
        location: Tuple[float, float, float],
        scale: Tuple[float, float, float],
        rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        geometry: str = "CUBE",
    ) -> Dict[str, Any]:
        """
        Create a proxy object in Blender

        Args:
            proxy_id: Unique proxy identifier
            location: (x, y, z) position
            scale: (x, y, z) scale
            rotation: (x, y, z) rotation in radians
            geometry: Object type (CUBE, SPHERE, CYLINDER, etc.)

        Returns:
            Result dict with proxy info
        """
        params = {
            "proxy_id": proxy_id,
            "location": {"x": location[0], "y": location[1], "z": location[2]},
            "scale": {"x": scale[0], "y": scale[1], "z": scale[2]},
            "rotation": {"x": rotation[0], "y": rotation[1], "z": rotation[2]},
            "geometry": geometry,
        }

        response = self.send_command("create_proxy", params)
        return response.result or {}

    def apply_material(
        self,
        proxy_id: str,
        material_name: str,
        base_color: Tuple[float, float, float, float],
        roughness: float = 0.7,
        metallic: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Apply material to proxy

        Args:
            proxy_id: Proxy identifier
            material_name: Material name
            base_color: (r, g, b, a) color (0.0-1.0)
            roughness: Roughness value (0.0-1.0)
            metallic: Metallic value (0.0-1.0)

        Returns:
            Result dict
        """
        params = {
            "proxy_id": proxy_id,
            "material_name": material_name,
            "base_color": {
                "r": base_color[0],
                "g": base_color[1],
                "b": base_color[2],
                "a": base_color[3],
            },
            "roughness": roughness,
            "metallic": metallic,
        }

        response = self.send_command("apply_material", params)
        return response.result or {}

    def set_visibility(self, proxy_id: str, visible: bool) -> Dict[str, Any]:
        """
        Set proxy visibility

        Args:
            proxy_id: Proxy identifier
            visible: Visibility state

        Returns:
            Result dict
        """
        params = {"proxy_id": proxy_id, "visible": visible}
        response = self.send_command("set_visibility", params)
        return response.result or {}

    def set_transparency(self, proxy_id: str, alpha: float) -> Dict[str, Any]:
        """
        Set proxy transparency

        Args:
            proxy_id: Proxy identifier
            alpha: Alpha value (0.0-1.0, where 1.0 is opaque)

        Returns:
            Result dict
        """
        params = {"proxy_id": proxy_id, "alpha": alpha}
        response = self.send_command("set_transparency", params)
        return response.result or {}

    def assign_to_collection(
        self, proxy_id: str, collection_name: str
    ) -> Dict[str, Any]:
        """
        Assign proxy to collection (layer)

        Args:
            proxy_id: Proxy identifier
            collection_name: Collection name

        Returns:
            Result dict
        """
        params = {"proxy_id": proxy_id, "collection_name": collection_name}
        response = self.send_command("assign_to_collection", params)
        return response.result or {}

    def export_gltf(
        self, output_path: str, selected_only: bool = False
    ) -> Dict[str, Any]:
        """
        Export scene to glTF format

        Args:
            output_path: Output file path
            selected_only: Export only selected objects

        Returns:
            Result dict with export info
        """
        params = {"output_path": output_path, "selected_only": selected_only}
        response = self.send_command("export_gltf", params)
        return response.result or {}

    def get_scene_info(self) -> Dict[str, Any]:
        """
        Get current scene information

        Returns:
            Scene info dict
        """
        response = self.send_command("get_scene_info", {})
        return response.result or {}

    def clear_scene(self, keep_camera: bool = True) -> Dict[str, Any]:
        """
        Clear all objects from scene

        Args:
            keep_camera: Whether to keep camera and lights

        Returns:
            Result dict
        """
        params = {"keep_camera": keep_camera}
        response = self.send_command("clear_scene", params)
        return response.result or {}

    def create_collection(
        self, collection_name: str, parent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a collection (layer)

        Args:
            collection_name: Collection name
            parent: Parent collection name (optional)

        Returns:
            Result dict
        """
        params = {"collection_name": collection_name, "parent": parent}
        response = self.send_command("create_collection", params)
        return response.result or {}

    def batch_create_proxies(
        self, proxies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create multiple proxies in batch

        Args:
            proxies: List of proxy definitions

        Returns:
            Result dict with created proxy IDs
        """
        params = {"proxies": proxies}
        response = self.send_command("batch_create_proxies", params)
        return response.result or {}

    def execute_python(self, code: str) -> Dict[str, Any]:
        """
        Execute arbitrary Python code in Blender context

        WARNING: This is a security risk. Use only with trusted code.

        Args:
            code: Python code to execute

        Returns:
            Result dict with execution output
        """
        logger.warning(
            "Executing arbitrary Python in Blender - ensure code is trusted!"
        )
        params = {"code": code}
        response = self.send_command("execute_python", params)
        return response.result or {}

    # ========================================================================
    # Context Manager Support
    # ========================================================================

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# ============================================================================
# Helper Functions
# ============================================================================


def test_blender_connection(
    host: str = "localhost", port: int = 9876
) -> Tuple[bool, str]:
    """
    Test connection to Blender

    Args:
        host: Blender host
        port: Blender port

    Returns:
        (success, message) tuple
    """
    try:
        with BlenderClient(host=host, port=port) as client:
            scene_info = client.get_scene_info()
            return True, f"Connected successfully. Scene: {scene_info.get('name', 'Unknown')}"
    except BlenderConnectionError as e:
        return False, f"Connection failed: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """CLI test utility"""
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            success, message = test_blender_connection()
            print(message)
            sys.exit(0 if success else 1)

    print("Blender Client Test")
    print("===================")

    try:
        with BlenderClient() as client:
            print("✓ Connected to Blender")

            # Get scene info
            scene_info = client.get_scene_info()
            print(f"✓ Scene: {scene_info.get('name', 'Unknown')}")

            # Create test proxy
            print("\nCreating test proxy...")
            result = client.create_proxy(
                proxy_id="test_proxy_1",
                location=(0.0, 0.0, 0.0),
                scale=(1.0, 1.0, 1.0),
                geometry="CUBE",
            )
            print(f"✓ Created proxy: {result}")

            # Apply material
            print("\nApplying material...")
            result = client.apply_material(
                proxy_id="test_proxy_1",
                material_name="Test_Material",
                base_color=(0.8, 0.2, 0.2, 1.0),
                roughness=0.7,
            )
            print(f"✓ Applied material: {result}")

            print("\n✓ All tests passed!")

    except BlenderConnectionError as e:
        print(f"\n✗ Connection error: {e}")
        sys.exit(1)
    except BlenderCommandError as e:
        print(f"\n✗ Command error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
