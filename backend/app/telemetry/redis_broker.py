"""
Redis Event Broker & Telemetry PubSub (Domain A & B Orchestration).
Compliant with Master Execution Specification: 'initiate redis also'.
Connects Docker workers, Central PPO Trainer, DDPS, and WebSocket broadcast.
Includes automatic fallback to in-memory event bus if Redis is unreachable.
"""

import os
import json
import socket
import logging
from typing import Dict, Any, Optional, Callable, List
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("localhost.redis")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6380"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)


class RedisTelemetryBroker:
    """
    High-frequency telemetry and event broker backed by Redis Pub/Sub.
    Channels:
    - `telemetry.{env_id}`
    - `rl.training_metrics`
    - `ddps.events`
    - `scenario.events`
    """

    def __init__(self):
        self.is_connected = False
        self.client = None
        self.in_memory_event_buffer: List[Dict[str, Any]] = []

        try:
            # Fast socket check before connecting client to avoid long retry hangs
            with socket.create_connection((REDIS_HOST, REDIS_PORT), timeout=0.15):
                pass

            import redis
            self.client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=0.5,
                socket_connect_timeout=0.2
            )
            self.client.ping()
            self.is_connected = True
            logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
        except Exception:
            self.is_connected = False

    def publish_event(self, channel: str, event_data: Dict[str, Any]) -> bool:
        """Publishes a structured JSON message to the specified Redis channel."""
        serialized = json.dumps(event_data)
        
        # Always maintain local memory buffer for WebSocket and dashboard queries
        self.in_memory_event_buffer.append({"channel": channel, "data": event_data})
        if len(self.in_memory_event_buffer) > 500:
            self.in_memory_event_buffer.pop(0)

        if self.is_connected and self.client:
            try:
                self.client.publish(channel, serialized)
                return True
            except Exception as e:
                logger.warning(f"Failed to publish to Redis channel {channel}: {e}")
                return False
        return True

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the most recent buffered events."""
        return self.in_memory_event_buffer[-limit:]

    def get_buffered_events(self, channel: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns in-memory buffered events matching an optional channel filter."""
        if channel is None:
            return self.in_memory_event_buffer[-limit:]
        return [
            ev["data"] for ev in self.in_memory_event_buffer
            if ev["channel"] == channel
        ][-limit:]


# Global singleton instance
broker = RedisTelemetryBroker()
