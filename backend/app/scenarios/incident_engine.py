"""
MITRE ATT&CK-Inspired Synthetic Scenario Engine.
Compliant with Section 8 of Formal Specification v1.0.
"""

from typing import List, Dict, Optional
import random
from backend.app.schemas.models import SyntheticIncidentEvent
from backend.app.topology.network_graph import NetworkTopology


class ScenarioEngine:
    """
    Orchestrates temporal, overlapping synthetic security incident campaigns.
    Enforces deterministic reproducibility given a fixed random seed.
    """

    def __init__(self, scenario_name: str = "black_sky", seed: Optional[int] = None):
        self.scenario_name = scenario_name
        self.seed = seed
        self.rng = random.Random(seed)
        self.events: List[SyntheticIncidentEvent] = []
        self._load_scenario(scenario_name)

    def _load_scenario(self, scenario_name: str):
        if scenario_name == "black_sky":
            self.events = self._build_black_sky_campaign()
        elif scenario_name == "held_out_evaluation":
            self.events = self._build_held_out_evaluation_campaign()
        elif scenario_name == "quiescent":
            self.events = []
        else:
            raise ValueError(f"Unknown scenario: {scenario_name}")

    def _build_black_sky_campaign(self) -> List[SyntheticIncidentEvent]:
        """Canonical Black Sky CI/CD Multi-Stage Resilience Benchmark."""
        return [
            SyntheticIncidentEvent(
                event_id="INC-001-EDGE-FLOOD",
                scenario_id="black_sky",
                tactic="Impact",
                technique_id="T1499",
                target_node_id=NetworkTopology.EDGE_GW,
                start_time_s=15.0,
                duration_s=70.0,
                intensity=0.9,
                description="Volumetric L3/L4 SYN & Ingress Flood targeting edge gateway"
            ),
            SyntheticIncidentEvent(
                event_id="INC-002-AUTH-STUFFING",
                scenario_id="black_sky",
                tactic="Credential Access",
                technique_id="T1110",
                target_node_id=NetworkTopology.AUTH_SVC,
                start_time_s=30.0,
                duration_s=45.0,
                intensity=0.85,
                description="Distributed credential stuffing and bcrypt compute exhaustion"
            ),
            SyntheticIncidentEvent(
                event_id="INC-003-CI-EXHAUSTION",
                scenario_id="black_sky",
                tactic="Execution",
                technique_id="T1059",
                target_node_id=NetworkTopology.CI_RUNNER,
                start_time_s=45.0,
                duration_s=45.0,
                intensity=0.8,
                description="Malicious pull-request flood starving CI/CD runner thread pools"
            ),
            SyntheticIncidentEvent(
                event_id="INC-004-LATERAL-SCAN",
                scenario_id="black_sky",
                tactic="Lateral Movement",
                technique_id="T1046",
                target_node_id=NetworkTopology.DATABASE,
                start_time_s=60.0,
                duration_s=25.0,
                intensity=0.95,
                description="Compromised runner executing port scanning and lateral pivot to DB"
            )
        ]

    def _build_held_out_evaluation_campaign(self) -> List[SyntheticIncidentEvent]:
        """Held-out validation scenario with different timings and vectors."""
        return [
            SyntheticIncidentEvent(
                event_id="EVAL-001-APP-EXPLOIT",
                scenario_id="held_out_evaluation",
                tactic="Initial Access",
                technique_id="T1190",
                target_node_id=NetworkTopology.APP_GW,
                start_time_s=10.0,
                duration_s=50.0,
                intensity=0.75,
                description="WAF bypass probe and payload injection targeting application endpoints"
            ),
            SyntheticIncidentEvent(
                event_id="EVAL-002-EXFILTRATION",
                scenario_id="held_out_evaluation",
                tactic="Exfiltration",
                technique_id="T1048",
                target_node_id=NetworkTopology.DATABASE,
                start_time_s=35.0,
                duration_s=40.0,
                intensity=0.85,
                description="Anomalous egress volume and database exfiltration burst"
            )
        ]

    def get_active_incidents(self, current_time_s: float) -> List[SyntheticIncidentEvent]:
        """Returns list of currently active incidents at simulation time t."""
        active = []
        for event in self.events:
            if event.start_time_s <= current_time_s < (event.start_time_s + event.duration_s):
                event_copy = event.model_copy()
                event_copy.is_active = True
                active.append(event_copy)
        return active
