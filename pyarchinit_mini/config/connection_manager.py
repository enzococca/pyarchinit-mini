#!/usr/bin/env python3
"""
Database Connection Manager
============================

Manages persistent database connections configuration.
Connections are saved in ~/.pyarchinit-mini/connections.json
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages saved database connections

    Features:
    - Save database connections with friendly names
    - Load connections from persistent storage
    - List all saved connections
    - Remove connections
    - Automatic persistence to JSON file
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize connection manager

        Args:
            config_dir: Optional custom config directory.
                       Defaults to ~/.pyarchinit-mini/
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / '.pyarchinit_mini'

        self.config_file = self.config_dir / 'connections.json'
        self._ensure_config_dir()
        self._connections: Dict[str, Dict[str, Any]] = {}
        self._load_connections()

    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Config directory: {self.config_dir}")
        except Exception as e:
            logger.error(f"Failed to create config directory: {e}")

    def _load_connections(self):
        """Load connections from JSON file"""
        if not self.config_file.exists():
            logger.info("No saved connections file found. Starting fresh.")
            self._connections = {}
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._connections = data.get('connections', {})
                logger.info(f"Loaded {len(self._connections)} saved connections")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse connections file: {e}")
            self._connections = {}
        except Exception as e:
            logger.error(f"Failed to load connections: {e}")
            self._connections = {}

    def _save_connections(self):
        """Save connections to JSON file"""
        try:
            data = {
                'connections': self._connections,
                'last_updated': datetime.now().isoformat()
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(self._connections)} connections to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save connections: {e}")
            return False

    def add_connection(self, name: str, db_type: str, connection_string: str,
                      description: str = "") -> Dict[str, Any]:
        """
        Add a new connection or update existing one

        Args:
            name: Friendly name for the connection (unique identifier)
            db_type: Database type ('sqlite' or 'postgresql')
            connection_string: Full connection string/URL
            description: Optional description

        Returns:
            Dictionary with success status and message
        """
        if not name or not name.strip():
            return {'success': False, 'message': 'Connection name is required'}

        if db_type not in ['sqlite', 'postgresql']:
            return {'success': False, 'message': 'Database type must be sqlite or postgresql'}

        if not connection_string or not connection_string.strip():
            return {'success': False, 'message': 'Connection string is required'}

        # Parse connection details for display
        connection_info = self._parse_connection_string(connection_string, db_type)

        self._connections[name] = {
            'name': name,
            'db_type': db_type,
            'connection_string': connection_string,
            'description': description,
            'display_info': connection_info,
            'created_at': datetime.now().isoformat(),
            'last_used': None
        }

        if self._save_connections():
            return {
                'success': True,
                'message': f'Connection "{name}" saved successfully',
                'connection': self._connections[name]
            }
        else:
            return {'success': False, 'message': 'Failed to save connection'}

    def _parse_connection_string(self, connection_string: str, db_type: str) -> str:
        """
        Parse connection string for display (hide password)

        Args:
            connection_string: Database connection string
            db_type: Database type

        Returns:
            Safe display string
        """
        if db_type == 'sqlite':
            # Extract database file path
            if ':///' in connection_string:
                path = connection_string.split(':///', 1)[1]
                return f"SQLite: {path}"
            return connection_string

        elif db_type == 'postgresql':
            # Parse PostgreSQL URL
            try:
                # Format: postgresql://user:password@host:port/database
                if '@' in connection_string:
                    protocol_and_auth = connection_string.split('@')[0]
                    host_and_db = connection_string.split('@')[1]

                    if ':' in protocol_and_auth:
                        protocol_and_user = protocol_and_auth.rsplit(':', 1)[0]
                        user = protocol_and_user.split('//')[-1]
                    else:
                        user = 'unknown'

                    # Extract host and database
                    if '/' in host_and_db:
                        host_port = host_and_db.split('/')[0]
                        database = host_and_db.split('/')[-1]
                    else:
                        host_port = host_and_db
                        database = 'unknown'

                    return f"PostgreSQL: {user}@{host_port}/{database}"
                else:
                    return connection_string
            except Exception:
                return connection_string

        return connection_string

    def get_connection(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a connection by name

        Args:
            name: Connection name

        Returns:
            Connection dictionary or None if not found
        """
        connection = self._connections.get(name)
        if connection:
            # Update last_used timestamp
            connection['last_used'] = datetime.now().isoformat()
            self._save_connections()
        return connection

    def remove_connection(self, name: str) -> Dict[str, Any]:
        """
        Remove a saved connection

        Args:
            name: Connection name to remove

        Returns:
            Dictionary with success status and message
        """
        if name not in self._connections:
            return {'success': False, 'message': f'Connection "{name}" not found'}

        del self._connections[name]

        if self._save_connections():
            return {'success': True, 'message': f'Connection "{name}" removed'}
        else:
            return {'success': False, 'message': 'Failed to save changes'}

    def list_connections(self) -> List[Dict[str, Any]]:
        """
        Get list of all saved connections

        Returns:
            List of connection dictionaries (with passwords hidden in display)
        """
        connections = []
        for name, conn_data in self._connections.items():
            # Create a copy without the full connection string for security
            safe_conn = {
                'name': conn_data['name'],
                'db_type': conn_data['db_type'],
                'description': conn_data.get('description', ''),
                'display_info': conn_data.get('display_info', ''),
                'created_at': conn_data.get('created_at'),
                'last_used': conn_data.get('last_used')
            }
            connections.append(safe_conn)

        return connections

    def get_connection_string(self, name: str) -> Optional[str]:
        """
        Get connection string for a saved connection

        Args:
            name: Connection name

        Returns:
            Connection string or None if not found
        """
        connection = self.get_connection(name)
        if connection:
            return connection.get('connection_string')
        return None

    def clear_all_connections(self) -> Dict[str, Any]:
        """
        Remove all saved connections

        Returns:
            Dictionary with success status and message
        """
        count = len(self._connections)
        self._connections = {}

        if self._save_connections():
            return {'success': True, 'message': f'Removed {count} connections'}
        else:
            return {'success': False, 'message': 'Failed to save changes'}


# Global instance
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager