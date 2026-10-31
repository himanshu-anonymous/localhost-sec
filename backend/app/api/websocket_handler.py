"""
WebSocket Telemetry Broadcaster.
Compliant with Section 10 & 12 of Master Execution Specification.
Streams real-time simulation updates and training metrics to the React dashboard.
"""

import asyncio
import json
import logging
from typing import Set, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.app.telemetry.redis_broker import broker

router = APIRouter(tags=["WebSockets"])
logger = logging.getLogger("localhost.ws")


class ConnectionManager:
    """Manages active WebSocket subscribers for live experiment telemetry."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)
        for dc in dead_connections:
            self.active_connections.discard(dc)


ws_manager = ConnectionManager()


@router.websocket("/ws/v1/experiments/{experiment_id}")
async def websocket_experiment_telemetry(websocket: WebSocket, experiment_id: str):
    """
    Real-time WebSocket endpoint streaming:
    - environment.telemetry
    - rl.training_metrics
    - ddps.actions
    - experiment.completed
    """
    await ws_manager.connect(websocket)
    last_sent_count = len(broker.in_memory_event_buffer)

    try:
        # Send initial backlog or handshake message
        recent = broker.get_recent_events(limit=10)
        if not recent:
            await websocket.send_json({
                "event_type": "websocket.connected",
                "experiment_id": experiment_id,
                "timestamp": "connected"
            })
        else:
            for evt in recent:
                await websocket.send_json(evt["data"])

        # Continuous streaming loop
        while True:
            current_count = len(broker.in_memory_event_buffer)
            if current_count > last_sent_count:
                new_events = broker.in_memory_event_buffer[last_sent_count:current_count]
                for evt in new_events:
                    await websocket.send_json(evt["data"])
                last_sent_count = current_count

            # Small sleep to yield to event loop
            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.debug(f"WebSocket stream terminated: {e}")
        ws_manager.disconnect(websocket)
