"""
AEGIS Telemetry Collector.
Buffers and persists normalized events to in-memory store and PostgreSQL.
Compliant with Section 9 & 14 of AEGIS Master Implementation Spec.
"""

import logging
from typing import List, Optional, Dict, Any
from backend.app.telemetry.schemas import SecurityEventSchema
from backend.app.telemetry.redis_broker import broker

logger = logging.getLogger("aegis.telemetry_collector")


class TelemetryCollector:
    def __init__(self, max_buffer_size: int = 2000):
        self.max_buffer_size = max_buffer_size
        self.events: List[SecurityEventSchema] = []

    def ingest(self, event: SecurityEventSchema) -> SecurityEventSchema:
        """Ingests a normalized event, adds to ring buffer, broadcasts, and persists."""
        self.events.append(event)
        if len(self.events) > self.max_buffer_size:
            self.events.pop(0)

        # Broadcast via Redis / in-memory broker
        broker.publish_event(f"telemetry.events", event.model_dump(mode="json"))

        # Optional PostgreSQL persistence if DB session available
        try:
            from backend.db.postgres import SessionLocal
            from backend.db.models import SecurityObservation
            import uuid

            session = SessionLocal()
            try:
                obs = SecurityObservation(
                    observation_id=uuid.UUID(event.event_id) if len(event.event_id) == 36 else uuid.uuid4(),
                    run_id=uuid.UUID(event.simulation_run_id) if event.simulation_run_id and len(event.simulation_run_id) == 36 else None,
                    environment_id="ENV-B",
                    node_id=event.source_name,
                    metric_name=event.event_type,
                    metric_value=1.0,
                    anomaly_detected=event.severity in ["high", "critical"],
                    observed_at=event.occurred_at
                )
                session.add(obs)
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()
        except Exception:
            pass

        return event

    def get_events(
        self,
        limit: int = 100,
        source_type: Optional[str] = None,
        event_type: Optional[str] = None,
        source_ip: Optional[str] = None,
        simulation_run_id: Optional[str] = None
    ) -> List[SecurityEventSchema]:
        """Retrieves filtered events from the buffer."""
        filtered = self.events
        if source_type:
            filtered = [e for e in filtered if e.source_type == source_type]
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        if source_ip:
            filtered = [e for e in filtered if e.source_ip == source_ip]
        if simulation_run_id:
            filtered = [e for e in filtered if e.simulation_run_id == simulation_run_id]

        return filtered[-limit:]

    def get_event_by_id(self, event_id: str) -> Optional[SecurityEventSchema]:
        for e in reversed(self.events):
            if e.event_id == event_id:
                return e
        return None

    def clear(self):
        self.events.clear()


# Global singleton instance
telemetry_collector = TelemetryCollector()

