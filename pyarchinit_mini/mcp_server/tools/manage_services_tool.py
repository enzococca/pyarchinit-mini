"""
Manage Services Tool - PyArchInit Services Manager for MCP

This tool enables AI assistants to start, stop, and manage PyArchInit services.
Features:
- Start services in background (web, api, gui, mcp-http)
- Stop running services
- Check service status
- List running services
- View service logs
"""

import logging
import os
import subprocess
import signal
import psutil
from typing import Dict, Any, Optional, List
from pathlib import Path
import time

logger = logging.getLogger(__name__)


def manage_service(
    action: str,
    service: str,
    port: Optional[int] = None,
    host: str = "localhost",
    database_url: Optional[str] = None,
    background: bool = True
) -> dict:
    """
    Manage PyArchInit services (start, stop, status).

    Args:
        action: Action to perform.
                Valid values: "start", "stop", "status", "list", "logs"
        service: Service to manage.
                Valid values: "web", "api", "gui", "mcp-http", "all"
        port: Optional port number for the service.
              Defaults: web=5001, api=8000, mcp-http=8765
        host: Host to bind to (default: "localhost")
        database_url: Optional database URL. If not provided, uses config default.
        background: If True, runs service in background (default: True)

    Returns:
        dict: Result with structure:
        {
            "success": True | False,
            "message": "Success/error message",
            "service": "<service_name>",
            "action": "<action_performed>",
            "pid": <process_id> (for start action),
            "url": "<service_url>" (for start action),
            "services": [...] (for list action)
        }

    Examples:
        # Start web interface
        result = manage_service(
            action="start",
            service="web"
        )

        # Start API server on custom port
        result = manage_service(
            action="start",
            service="api",
            port=9000
        )

        # Start GUI
        result = manage_service(
            action="start",
            service="gui"
        )

        # Stop web interface
        result = manage_service(
            action="stop",
            service="web"
        )

        # Check status of all services
        result = manage_service(
            action="status",
            service="all"
        )

        # List running services
        result = manage_service(
            action="list",
            service="all"
        )

    Notes:
        - Services run in background by default
        - Service logs are stored in ~/.pyarchinit_mini/logs/
        - Use action="logs" to view recent log entries
        - Stopping "all" stops all PyArchInit services
    """
    try:
        # Validate action
        valid_actions = ["start", "stop", "status", "list", "logs"]
        if action not in valid_actions:
            return {
                "success": False,
                "error": "invalid_action",
                "message": f"Action must be one of: {', '.join(valid_actions)}"
            }

        # Validate service
        valid_services = ["web", "api", "gui", "mcp-http", "all"]
        if service not in valid_services:
            return {
                "success": False,
                "error": "invalid_service",
                "message": f"Service must be one of: {', '.join(valid_services)}"
            }

        # Get database URL if not provided
        if database_url is None:
            from pyarchinit_mini.mcp_server.config import _get_default_database_url
            database_url = os.getenv("DATABASE_URL") or _get_default_database_url()

        # Service configuration
        service_config = {
            "web": {
                "command": "pyarchinit-mini-web",
                "default_port": 5001,
                "name": "PyArchInit Web Interface",
                "log_file": "web.log"
            },
            "api": {
                "command": "pyarchinit-mini-api",
                "default_port": 8000,
                "name": "PyArchInit API Server",
                "log_file": "api.log"
            },
            "gui": {
                "command": "pyarchinit-mini-gui",
                "default_port": None,  # GUI doesn't use port
                "name": "PyArchInit Desktop GUI",
                "log_file": "gui.log"
            },
            "mcp-http": {
                "command": "pyarchinit-mini-mcp-http",
                "default_port": 8765,
                "name": "PyArchInit MCP HTTP Server",
                "log_file": "mcp-http.log"
            }
        }

        # Handle "list" action
        if action == "list":
            running_services = _get_running_services()
            return {
                "success": True,
                "action": "list",
                "message": f"Found {len(running_services)} running service(s)",
                "services": running_services
            }

        # Handle "all" service
        if service == "all":
            if action == "status":
                # Get status of all services
                statuses = {}
                for svc_name in ["web", "api", "gui", "mcp-http"]:
                    pid = _find_service_pid(svc_name, service_config)
                    statuses[svc_name] = {
                        "running": pid is not None,
                        "pid": pid,
                        "name": service_config[svc_name]["name"]
                    }

                running_count = sum(1 for s in statuses.values() if s["running"])
                return {
                    "success": True,
                    "action": "status",
                    "service": "all",
                    "message": f"{running_count} of 4 services running",
                    "statuses": statuses
                }

            elif action == "stop":
                # Stop all services
                stopped = []
                errors = []
                for svc_name in ["web", "api", "gui", "mcp-http"]:
                    result = manage_service("stop", svc_name)
                    if result["success"]:
                        stopped.append(svc_name)
                    else:
                        errors.append(f"{svc_name}: {result.get('message', 'unknown error')}")

                if errors:
                    return {
                        "success": False,
                        "action": "stop",
                        "service": "all",
                        "message": f"Stopped {len(stopped)} service(s), {len(errors)} error(s)",
                        "stopped": stopped,
                        "errors": errors
                    }
                else:
                    return {
                        "success": True,
                        "action": "stop",
                        "service": "all",
                        "message": f"Stopped all {len(stopped)} running service(s)",
                        "stopped": stopped
                    }

            elif action == "start":
                return {
                    "success": False,
                    "error": "invalid_operation",
                    "message": "Cannot start 'all' services. Please specify individual service."
                }

        # Get service configuration
        config = service_config.get(service)
        if not config:
            return {
                "success": False,
                "error": "unknown_service",
                "message": f"Unknown service: {service}"
            }

        # Handle "start" action
        if action == "start":
            # Check if already running
            existing_pid = _find_service_pid(service, service_config)
            if existing_pid:
                return {
                    "success": False,
                    "error": "already_running",
                    "message": f"{config['name']} is already running (PID: {existing_pid})",
                    "pid": existing_pid,
                    "service": service
                }

            # Prepare command
            command = config["command"]
            service_port = port or config["default_port"]

            # Prepare environment
            env = os.environ.copy()
            env["DATABASE_URL"] = database_url

            if service_port:
                env["PORT"] = str(service_port)

            # Prepare log directory
            log_dir = Path.home() / '.pyarchinit_mini' / 'logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / config["log_file"]

            # Start service
            if background:
                # Start in background with output to log file
                with open(log_file, 'w') as log:
                    process = subprocess.Popen(
                        [command],
                        env=env,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        start_new_session=True  # Detach from parent
                    )

                # Wait a bit to check if it started successfully
                time.sleep(1)
                if process.poll() is not None:
                    # Process died immediately
                    with open(log_file, 'r') as log:
                        error_output = log.read()
                    return {
                        "success": False,
                        "error": "startup_failed",
                        "message": f"Service failed to start. Check log: {log_file}",
                        "log_output": error_output[-500:] if error_output else ""
                    }

                # Build service URL
                if service_port:
                    service_url = f"http://{host}:{service_port}"
                else:
                    service_url = None

                return {
                    "success": True,
                    "action": "start",
                    "service": service,
                    "message": f"{config['name']} started successfully",
                    "pid": process.pid,
                    "url": service_url,
                    "log_file": str(log_file)
                }
            else:
                # Start in foreground (not recommended for MCP)
                return {
                    "success": False,
                    "error": "foreground_not_supported",
                    "message": "Foreground mode not supported in MCP context. Use background=True."
                }

        # Handle "stop" action
        elif action == "stop":
            pid = _find_service_pid(service, service_config)
            if not pid:
                return {
                    "success": False,
                    "error": "not_running",
                    "message": f"{config['name']} is not running",
                    "service": service
                }

            # Try to stop gracefully
            try:
                process = psutil.Process(pid)
                process.terminate()

                # Wait for termination
                try:
                    process.wait(timeout=5)
                    return {
                        "success": True,
                        "action": "stop",
                        "service": service,
                        "message": f"{config['name']} stopped successfully",
                        "pid": pid
                    }
                except psutil.TimeoutExpired:
                    # Force kill if not terminated
                    process.kill()
                    return {
                        "success": True,
                        "action": "stop",
                        "service": service,
                        "message": f"{config['name']} force stopped (was not responding)",
                        "pid": pid
                    }
            except psutil.NoSuchProcess:
                return {
                    "success": False,
                    "error": "process_not_found",
                    "message": f"Process {pid} not found (may have already stopped)",
                    "service": service
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": "stop_failed",
                    "message": f"Failed to stop service: {str(e)}",
                    "service": service
                }

        # Handle "status" action
        elif action == "status":
            pid = _find_service_pid(service, service_config)
            if pid:
                try:
                    process = psutil.Process(pid)
                    service_port = port or config["default_port"]
                    service_url = f"http://{host}:{service_port}" if service_port else None

                    return {
                        "success": True,
                        "action": "status",
                        "service": service,
                        "message": f"{config['name']} is running",
                        "running": True,
                        "pid": pid,
                        "url": service_url,
                        "cpu_percent": process.cpu_percent(),
                        "memory_mb": process.memory_info().rss / (1024 * 1024)
                    }
                except psutil.NoSuchProcess:
                    return {
                        "success": True,
                        "action": "status",
                        "service": service,
                        "message": f"{config['name']} is not running (stale PID)",
                        "running": False
                    }
            else:
                return {
                    "success": True,
                    "action": "status",
                    "service": service,
                    "message": f"{config['name']} is not running",
                    "running": False
                }

        # Handle "logs" action
        elif action == "logs":
            log_dir = Path.home() / '.pyarchinit_mini' / 'logs'
            log_file = log_dir / config["log_file"]

            if not log_file.exists():
                return {
                    "success": False,
                    "error": "no_logs",
                    "message": f"No log file found for {config['name']}",
                    "service": service
                }

            # Read last 50 lines
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    last_lines = lines[-50:] if len(lines) > 50 else lines

                return {
                    "success": True,
                    "action": "logs",
                    "service": service,
                    "message": f"Last {len(last_lines)} log lines for {config['name']}",
                    "log_file": str(log_file),
                    "logs": ''.join(last_lines)
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": "read_logs_failed",
                    "message": f"Failed to read logs: {str(e)}",
                    "service": service
                }

    except Exception as e:
        logger.error(f"Error managing service: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to manage service: {str(e)}"
        }


def _find_service_pid(service: str, service_config: dict) -> Optional[int]:
    """
    Find PID of running service by command name.

    Args:
        service: Service name
        service_config: Service configuration dict

    Returns:
        PID if found, None otherwise
    """
    try:
        config = service_config.get(service)
        if not config:
            return None

        command_name = config["command"]

        # Search through all processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline')
                if cmdline and any(command_name in cmd for cmd in cmdline):
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return None
    except Exception as e:
        logger.warning(f"Error finding service PID: {e}")
        return None


def _get_running_services() -> List[Dict[str, Any]]:
    """
    Get list of all running PyArchInit services.

    Returns:
        List of service information dictionaries
    """
    services = []
    service_commands = [
        "pyarchinit-mini-web",
        "pyarchinit-mini-api",
        "pyarchinit-mini-gui",
        "pyarchinit-mini-mcp-http"
    ]

    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = proc.info.get('cmdline', [])
                for cmd in service_commands:
                    if any(cmd in c for c in cmdline):
                        services.append({
                            "pid": proc.info['pid'],
                            "command": cmd,
                            "name": cmd.replace("pyarchinit-mini-", "").upper(),
                            "uptime_seconds": time.time() - proc.info.get('create_time', time.time())
                        })
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logger.warning(f"Error listing services: {e}")

    return services
