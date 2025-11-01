"""
Event Stream for Real-time Blender Sync

Provides Server-Sent Events (SSE) for pushing real-time updates
from Blender to the web viewer without polling.
"""

import logging
import queue
import time
from typing import Dict, Any, Optional, Generator
from dataclasses import dataclass, asdict
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class BlenderEvent:
    """Blender event structure"""

    event_type: str  # e.g., "proxy_created", "proxy_updated", "visibility_changed"
    session_id: str
    data: Dict[str, Any]
    timestamp: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

    def to_sse_format(self) -> str:
        """
        Convert to SSE format

        Returns:
            SSE-formatted string: "event: {type}\ndata: {json}\n\n"
        """
        data_json = json.dumps({
            'event_type': self.event_type,
            'session_id': self.session_id,
            'data': self.data,
            'timestamp': self.timestamp
        })
        return f"event: {self.event_type}\ndata: {data_json}\n\n"


class EventStream:
    """
    Thread-safe event stream for broadcasting Blender updates

    Uses queues to manage multiple client connections and
    broadcast events from Blender to all connected clients.
    """

    def __init__(self, max_queue_size: int = 100):
        """
        Initialize event stream

        Args:
            max_queue_size: Maximum events per client queue
        """
        self.max_queue_size = max_queue_size
        self.clients: Dict[str, queue.Queue] = {}
        self._client_counter = 0

    def add_client(self, session_id: Optional[str] = None) -> str:
        """
        Add a new client listener

        Args:
            session_id: Optional session filter (only receive events for this session)

        Returns:
            Client ID
        """
        client_id = f"client_{self._client_counter}_{int(time.time())}"
        self._client_counter += 1

        self.clients[client_id] = {
            'queue': queue.Queue(maxsize=self.max_queue_size),
            'session_id': session_id,
            'connected_at': time.time()
        }

        logger.info(f"Client {client_id} connected (session filter: {session_id})")
        return client_id

    def remove_client(self, client_id: str):
        """Remove a client listener"""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Client {client_id} disconnected")

    def broadcast_event(self, event: BlenderEvent):
        """
        Broadcast event to all connected clients

        Args:
            event: BlenderEvent to broadcast
        """
        logger.debug(f"Broadcasting event: {event.event_type} for session {event.session_id}")

        disconnected_clients = []

        for client_id, client_info in self.clients.items():
            # Filter by session if client has session filter
            if client_info['session_id'] and client_info['session_id'] != event.session_id:
                continue

            try:
                # Try to put event in queue (non-blocking)
                client_info['queue'].put_nowait(event)
                logger.debug(f"Event queued for client {client_id}")
            except queue.Full:
                logger.warning(f"Client {client_id} queue full, dropping event")
                # Mark for disconnection if queue consistently full
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.remove_client(client_id)

    def stream_events(self, client_id: str, timeout: int = 30) -> Generator[str, None, None]:
        """
        Generate SSE stream for a client

        Args:
            client_id: Client identifier
            timeout: Maximum seconds to wait for events

        Yields:
            SSE-formatted event strings
        """
        if client_id not in self.clients:
            logger.error(f"Client {client_id} not found")
            return

        client_queue = self.clients[client_id]['queue']

        # Send initial connection event
        yield "event: connected\ndata: {\"status\": \"connected\"}\n\n"

        try:
            while True:
                try:
                    # Wait for event with timeout
                    event = client_queue.get(timeout=timeout)
                    yield event.to_sse_format()

                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    yield ": heartbeat\n\n"

                except GeneratorExit:
                    # Client disconnected
                    logger.info(f"Client {client_id} stream closed")
                    break

        finally:
            self.remove_client(client_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get stream statistics"""
        return {
            'total_clients': len(self.clients),
            'clients': [
                {
                    'id': client_id,
                    'session_id': info['session_id'],
                    'queue_size': info['queue'].qsize(),
                    'connected_duration': int(time.time() - info['connected_at'])
                }
                for client_id, info in self.clients.items()
            ]
        }


# Global event stream instance
_event_stream = None


def get_event_stream() -> EventStream:
    """Get global event stream instance"""
    global _event_stream
    if _event_stream is None:
        _event_stream = EventStream()
    return _event_stream


# ============================================================================
# Event Helper Functions
# ============================================================================

def emit_proxy_created(session_id: str, proxy_data: Dict[str, Any]):
    """Emit proxy created event"""
    event = BlenderEvent(
        event_type='proxy_created',
        session_id=session_id,
        data=proxy_data
    )
    get_event_stream().broadcast_event(event)


def emit_proxy_updated(session_id: str, proxy_id: str, updates: Dict[str, Any]):
    """Emit proxy updated event"""
    event = BlenderEvent(
        event_type='proxy_updated',
        session_id=session_id,
        data={'proxy_id': proxy_id, 'updates': updates}
    )
    get_event_stream().broadcast_event(event)


def emit_visibility_changed(session_id: str, proxy_id: str, visible: bool):
    """Emit visibility changed event"""
    event = BlenderEvent(
        event_type='visibility_changed',
        session_id=session_id,
        data={'proxy_id': proxy_id, 'visible': visible}
    )
    get_event_stream().broadcast_event(event)


def emit_transparency_changed(session_id: str, proxy_id: str, alpha: float):
    """Emit transparency changed event"""
    event = BlenderEvent(
        event_type='transparency_changed',
        session_id=session_id,
        data={'proxy_id': proxy_id, 'alpha': alpha}
    )
    get_event_stream().broadcast_event(event)


def emit_material_applied(session_id: str, proxy_id: str, material_data: Dict[str, Any]):
    """Emit material applied event"""
    event = BlenderEvent(
        event_type='material_applied',
        session_id=session_id,
        data={'proxy_id': proxy_id, 'material': material_data}
    )
    get_event_stream().broadcast_event(event)


def emit_scene_cleared(session_id: str):
    """Emit scene cleared event"""
    event = BlenderEvent(
        event_type='scene_cleared',
        session_id=session_id,
        data={}
    )
    get_event_stream().broadcast_event(event)


def emit_export_complete(session_id: str, export_data: Dict[str, Any]):
    """Emit export complete event"""
    event = BlenderEvent(
        event_type='export_complete',
        session_id=session_id,
        data=export_data
    )
    get_event_stream().broadcast_event(event)


def emit_batch_complete(session_id: str, batch_data: Dict[str, Any]):
    """Emit batch operation complete event"""
    event = BlenderEvent(
        event_type='batch_complete',
        session_id=session_id,
        data=batch_data
    )
    get_event_stream().broadcast_event(event)


def emit_error(session_id: str, error_message: str, context: Dict[str, Any] = None):
    """Emit error event"""
    event = BlenderEvent(
        event_type='error',
        session_id=session_id,
        data={'message': error_message, 'context': context or {}}
    )
    get_event_stream().broadcast_event(event)
