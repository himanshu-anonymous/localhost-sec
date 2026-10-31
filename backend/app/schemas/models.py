"""
Data models and schemas for localhost (BASTION X).
Compliant with Formal Specification v1.0.
"""

from typing import Dict, List, Literal, Optional, Any
from pydantic import BaseModel, Field


class NodeState(BaseModel):
    """Health and load metrics for an individual network node."""
    id: str
    name: str
    layer: int  # 1 to 7
    status: Literal["HEALTHY", "OPERATIONAL", "DEGRADED", "SEVERELY_DEGRADED", "UNAVAILABLE", "COMPROMISED"]
    cpu_utilization: float = Field(default=0.1, ge=0.0, le=1.0)
    memory_utilization: float = Field(default=0.1, ge=0.0, le=1.0)
    connection_utilization: float = Field(default=0.05, ge=0.0, le=1.0)
    request_rate: float = Field(default=100.0, ge=0.0)
    response_latency_ms: float = Field(default=15.0, ge=0.0)
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    health_index: float = Field(default=1.0, ge=0.0, le=1.0)
    is_compromised: bool = False
    is_isolated: bool = False


class DefensiveActionProposal(BaseModel):
    """
    Proposed action vector from RL agent or operator.
    A_t in {0, 1, 2}^8 (0=Baseline, 1=Moderate, 2=Strict).
    """
    edge_rate_limit_level: int = Field(default=0, ge=0, le=2)
    connection_limit_level: int = Field(default=0, ge=0, le=2)
    app_quota_level: int = Field(default=0, ge=0, le=2)
    auth_throttle_level: int = Field(default=0, ge=0, le=2)
    app_concurrency_level: int = Field(default=0, ge=0, le=2)
    segmentation_mode: int = Field(default=0, ge=0, le=2)
    egress_limit_level: int = Field(default=0, ge=0, le=2)
    workload_priority_level: int = Field(default=0, ge=0, le=2)

    def to_list(self) -> List[int]:
        return [
            self.edge_rate_limit_level,
            self.connection_limit_level,
            self.app_quota_level,
            self.auth_throttle_level,
            self.app_concurrency_level,
            self.segmentation_mode,
            self.egress_limit_level,
            self.workload_priority_level
        ]

    @classmethod
    def from_list(cls, actions: List[int]) -> "DefensiveActionProposal":
        assert len(actions) == 8, f"Expected 8 action values, got {len(actions)}"
        return cls(
            edge_rate_limit_level=int(actions[0]),
            connection_limit_level=int(actions[1]),
            app_quota_level=int(actions[2]),
            auth_throttle_level=int(actions[3]),
            app_concurrency_level=int(actions[4]),
            segmentation_mode=int(actions[5]),
            egress_limit_level=int(actions[6]),
            workload_priority_level=int(actions[7])
        )


class DDPSValidationResult(BaseModel):
    """Audit record for DDPS validation pipeline."""
    is_approved: bool
    proposed_action: DefensiveActionProposal
    enforced_action: DefensiveActionProposal
    rejected_reasons: List[str] = Field(default_factory=list)
    stability_penalty: float = 0.0
    timestamp: float


class SyntheticIncidentEvent(BaseModel):
    """A synthetic security incident event mapped to MITRE ATT&CK."""
    event_id: str
    scenario_id: str
    tactic: str  # e.g., "Initial Access", "Credential Access", "Impact"
    technique_id: str  # e.g., "T1190", "T1110"
    target_node_id: str
    start_time_s: float
    duration_s: float
    intensity: float = Field(default=1.0, ge=0.0, le=1.0)
    description: str
    is_active: bool = False


class TelemetryRecord(BaseModel):
    """Normalized observation telemetry record S_t in R^14."""
    timestamp: float
    environment_id: str
    episode_id: int
    step: int
    edge_health: float
    auth_health: float
    app_health: float
    database_health: float
    cpu_pressure: float
    memory_pressure: float
    network_pressure: float
    authentication_latency: float
    application_error_rate: float
    connection_pressure: float
    east_west_anomaly_score: float
    incident_severity: float
    legitimate_request_success_rate: float
    defensive_overhead: float

    def to_observation_vector(self) -> List[float]:
        return [
            self.edge_health,
            self.auth_health,
            self.app_health,
            self.database_health,
            self.cpu_pressure,
            self.memory_pressure,
            self.network_pressure,
            self.authentication_latency,
            self.application_error_rate,
            self.connection_pressure,
            self.east_west_anomaly_score,
            self.incident_severity,
            self.legitimate_request_success_rate,
            self.defensive_overhead
        ]


class EvaluationMetrics(BaseModel):
    """Quantitative cyber-resilience benchmarks."""
    effective_availability_pct: float
    mean_time_to_containment_s: Optional[float] = None
    blast_radius_factor: float
    resilience_degradation_index: float
    security_invariant_violations: int = 0
    policy_churn_count: int = 0
    total_legitimate_requests: int = 0
    successful_legitimate_requests: int = 0
    episodes_evaluated: int = 1
