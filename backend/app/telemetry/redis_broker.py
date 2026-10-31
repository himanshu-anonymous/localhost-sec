"""
Redis Event Broker & Telemetry PubSub (Domain A & B Orchestration).
Compliant with Master Execution Specification: 'initiate redis also'.
Connects Docker workers, Central PPO Trainer, DDPS, and WebSocket broadcast.
Includes automatic fallback to in-memory event bus if Redis is unreachable.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("localhost.redis")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
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
            import redis
            self.client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=1.0
            )
            # Ping test
            self.client.ping()
            self.is_connected = True
            logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
        except Exception as e:
            logger.warning(f"Redis connection unavailable ({e}). Using resilient in-memory broker fallback.")
            self.is_connected = False

    def publish_event(self, channel: str, event_data: Dict[str, Any]) -> bool:
        """Publishes a structured JSON message to the specified Redis channel."""
        serialized = json.dumps(event_data)
        
        # Always maintain local memory buffer for WebSocket and dashboard queries
        self.in_memory_event_buffer.append({"channel": channel, "data": event_data})
        if len(self.in_memory_event_buffer) > 1000:
            self.in_memory_event_buffer.pop(0)

        if self.is_connected and self.client:
            try:
                self.client.publish(channel, serialized)
                return True
            except Exception as e:
                logger.debug(f"Redis publish failure on channel {channel}: {e}")
                return False
        return False

    def get_recent_events(self, limit: int = 50, channel_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves recent events from in-memory ring buffer."""
        events = self.in_memory_event_buffer
        if channel_filter:
            events = [e for e in events if e["channel"] == channel_filter]
        return events[-limit:]


# Global singleton instance
broker = RedisTelemetryBroker()
