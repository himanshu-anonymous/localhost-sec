"""
Canonical Telemetry and Security Event Schemas.
Compliant with Section 9 of AEGIS Master Implementation Spec.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class SecurityEventSchema(BaseModel):
    """Normalized Canonical Security Event."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_type: str = Field(..., description="haproxy, target_app, suricata, policy_agent, runner")
    source_name: str = Field(..., description="Container or component identifier")
    event_type: str = Field(..., description="auth_failure, auth_success, http_request, gateway_deny, alert")
    source_ip: str = Field(..., description="Verified origin IPv4")
    source_port: Optional[int] = Field(None)
    destination_ip: Optional[str] = Field(None)
    destination_port: Optional[int] = Field(None)
    protocol: str = Field(default="HTTP")
    severity: str = Field(default="info", description="info, low, warning, high, critical")
    simulation_run_id: Optional[str] = Field(None, description="Optional association with a test run")
    incident_id: Optional[str] = Field(None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DetectionRecord(BaseModel):
    """Deterministic Detection Output record."""
    detection_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    detector_id: str = Field(..., description="failed_login_detector, traffic_anomaly_detector, etc.")
    detector_version: str = Field(default="1.0.0")
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: str = Field(default="high")
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    inferred_techniques: List[str] = Field(default_factory=list, description="e.g. ['T1110']")
    evidence_event_ids: List[str] = Field(default_factory=list)
    reason: str = Field(...)
    affected_service: str = Field(...)
    source_ip: Optional[str] = Field(None)
    simulation_run_id: Optional[str] = Field(None)


class IncidentRecord(BaseModel):
    """Incident Grouping Record."""
    incident_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    severity: str = Field(default="high")
    status: str = Field(default="NEW", description="NEW, TRIAGED, INVESTIGATING, MITIGATING, MONITORING, RESOLVED, CLOSED")
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    affected_services: List[str] = Field(default_factory=list)
    source_identities: List[str] = Field(default_factory=list)
    related_event_ids: List[str] = Field(default_factory=list)
    related_detection_ids: List[str] = Field(default_factory=list)
    technique_associations: List[str] = Field(default_factory=list)
    resolved_at: Optional[datetime] = Field(None)
    resolution_notes: Optional[str] = Field(None)

