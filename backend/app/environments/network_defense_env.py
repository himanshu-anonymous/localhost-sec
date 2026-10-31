"""
Gymnasium-compatible Network Defense Environment (Fast Simulation Layer - Domain A).
Compliant with Section 5.1 & Section 6 of Formal Specification v1.0.
"""

from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from backend.app.schemas.models import (
    DefensiveActionProposal,
    TelemetryRecord,
    EvaluationMetrics,
)
from backend.app.topology.network_graph import NetworkTopology
from backend.app.scenarios.incident_engine import ScenarioEngine
from backend.app.ddps.policy_stack import DynamicDefensivePolicyStack


class NetworkDefenseEnv(gym.Env):
    """
    Deterministic discrete-step cyber-resilience simulation environment.
    Observation Space: Box(14,) normalized in [0.0, 1.0]
    Action Space: MultiDiscrete([3, 3, 3, 3, 3, 3, 3, 3]) in {0, 1, 2}^8
    """

    metadata = {"render_modes": ["human"], "version": "1.0.0"}

    def __init__(
        self,
        environment_id: str = "env_adaptive",
        scenario_name: str = "black_sky",
        fixed_policy_profile: Optional[str] = None,  # "baseline", "hardened", or None (agent controlled)
        max_steps: int = 100,
        dt_seconds: float = 1.0,
        seed: Optional[int] = None
    ):
        super().__init__()
        self.environment_id = environment_id
        self.scenario_name = scenario_name
        self.fixed_policy_profile = fixed_policy_profile
        self.max_steps = max_steps
        self.dt_seconds = dt_seconds
        self.initial_seed = seed

        # Observation Space S_t in R^14 (all bounded [0.0, 1.0])
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(14,),
            dtype=np.float32
        )

        # Action Space A_t in {0, 1, 2}^8
        self.action_space = spaces.MultiDiscrete([3, 3, 3, 3, 3, 3, 3, 3])

        # Core Simulation Subsystems
        self.topology = NetworkTopology()
        self.scenario = ScenarioEngine(scenario_name=scenario_name, seed=seed)
        self.ddps = DynamicDefensivePolicyStack()

        # Episode State Tracking
        self.current_step = 0
        self.sim_time_s = 0.0
        self.episode_id = 0
        self.total_legitimate_requests = 0
        self.successful_legitimate_requests = 0
        self.compromise_init_time: Optional[float] = None
        self.containment_time: Optional[float] = None
        self.accumulated_degradation = 0.0
        self.last_observation: Optional[np.ndarray] = None

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        if seed is not None:
            self.initial_seed = seed

        self.episode_id += 1
        self.current_step = 0
        self.sim_time_s = 0.0
        self.total_legitimate_requests = 0
        self.successful_legitimate_requests = 0
        self.compromise_init_time = None
        self.containment_time = None
        self.accumulated_degradation = 0.0

        # Reset subsystems
        self.topology.reset()
        self.scenario = ScenarioEngine(
            scenario_name=self.scenario_name,
            seed=self.initial_seed + self.episode_id if self.initial_seed is not None else None
        )
        self.ddps.reset()

        obs = self._compute_observation()
        self.last_observation = obs
        info = self._get_info()
        return obs, info

    def step(self, action: Any) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        self.current_step += 1
        self.sim_time_s += self.dt_seconds

        # 1. Action translation & Enforcement profile
        if self.fixed_policy_profile == "baseline":
            # Strict fixed conventional rules (all 0)
            proposal = DefensiveActionProposal()
        elif self.fixed_policy_profile == "hardened":
            # Strict static zero-trust rules (all 2)
            proposal = DefensiveActionProposal(
                edge_rate_limit_level=2,
                connection_limit_level=2,
                app_quota_level=2,
                auth_throttle_level=2,
                app_concurrency_level=2,
                segmentation_mode=2,
                egress_limit_level=2,
                workload_priority_level=2
            )
        else:
            # RL Agent or Operator Proposed Action
            if isinstance(action, np.ndarray):
                action_list = [int(x) for x in action.tolist()]
            elif isinstance(action, (list, tuple)):
                action_list = [int(x) for x in action]
            else:
                action_list = [0] * 8
            proposal = DefensiveActionProposal.from_list(action_list)

        # 2. DDPS Validation & Security Invariant Enforcement
        validation = self.ddps.validate_and_enforce(
            proposed_action=proposal,
            current_step=self.current_step
        )
        enforced = validation.enforced_action

        # 3. Fetch active synthetic incidents
        active_incidents = self.scenario.get_active_incidents(self.sim_time_s)
        incident_types = {inc.technique_id: inc for inc in active_incidents}

        # 4. Simulate State Dynamics & Cross-Layer Pressure
        # Baseline legitimate traffic: 100 req/sec nominal
        step_legit_attempts = 100
        step_legit_successes = 100

        # --- Layer 1 & 2: Edge & Transport (T1499 Flood) ---
        edge_node = self.topology.get_node(NetworkTopology.EDGE_GW)
        if "T1499" in incident_types:
            flood = incident_types["T1499"]
            # Mitigation by edge_rate_limit_level (0=none, 1=moderate, 2=aggressive)
            drop_ratio = 0.1 if enforced.edge_rate_limit_level == 0 else (0.6 if enforced.edge_rate_limit_level == 1 else 0.88)
            effective_flood = flood.intensity * (1.0 - drop_ratio)
            edge_node.cpu_utilization = min(1.0, 0.15 + effective_flood * 0.9)
            edge_node.connection_utilization = min(1.0, 0.1 + effective_flood * 0.85)
            edge_node.health_index = max(0.05, 1.0 - effective_flood * 0.9)
            if enforced.edge_rate_limit_level == 0:
                # Unmitigated edge flood drops legitimate requests
                step_legit_successes -= int(step_legit_attempts * 0.55)
            elif enforced.edge_rate_limit_level == 2:
                # Aggressive filtering causes minor false positive drop (5%)
                step_legit_successes -= int(step_legit_attempts * 0.05)
        else:
            edge_node.cpu_utilization = max(0.1, edge_node.cpu_utilization * 0.8)
            edge_node.connection_utilization = max(0.05, edge_node.connection_utilization * 0.8)
            edge_node.health_index = min(1.0, edge_node.health_index + 0.1)

        # --- Layer 4: Identity & Auth (T1110 Credential Stuffing) ---
        auth_node = self.topology.get_node(NetworkTopology.AUTH_SVC)
        if "T1110" in incident_types:
            stuffing = incident_types["T1110"]
            throttle = enforced.auth_throttle_level  # 0, 1, 2
            # Cross-layer coupling: edge degradation slows down auth
            edge_penalty = (1.0 - edge_node.health_index) * 0.3
            auth_mitigation = 0.1 if throttle == 0 else (0.55 if throttle == 1 else 0.85)
            auth_load = (stuffing.intensity * (1.0 - auth_mitigation)) + edge_penalty
            auth_node.cpu_utilization = min(1.0, 0.1 + auth_load * 0.85)
            auth_node.response_latency_ms = 15.0 + auth_load * 1200.0
            auth_node.health_index = max(0.05, 1.0 - auth_load * 0.85)
            if throttle == 0 and "T1499" in incident_types:
                # Severe cascade drop: auth timeout cascade
                step_legit_successes -= int(step_legit_attempts * 0.35)
        else:
            auth_node.cpu_utilization = max(0.1, auth_node.cpu_utilization * 0.85)
            auth_node.response_latency_ms = max(15.0, auth_node.response_latency_ms * 0.7)
            auth_node.health_index = min(1.0, auth_node.health_index + 0.1)

        # --- Layer 5: CI/CD Workload (T1059 CI Exhaustion) ---
        ci_node = self.topology.get_node(NetworkTopology.CI_RUNNER)
        if "T1059" in incident_types:
            ci_flood = incident_types["T1059"]
            priority_shield = enforced.workload_priority_level  # 0=none, 1=reserved, 2=isolated
            mitigated_ci_load = ci_flood.intensity * (1.0 - priority_shield * 0.4)
            ci_node.cpu_utilization = min(1.0, 0.2 + mitigated_ci_load * 0.8)
            ci_node.health_index = max(0.1, 1.0 - mitigated_ci_load * 0.75)
        else:
            ci_node.cpu_utilization = max(0.1, ci_node.cpu_utilization * 0.85)
            ci_node.health_index = min(1.0, ci_node.health_index + 0.1)

        # --- Layer 6 & 7: Lateral Movement to Database (T1046) ---
        db_node = self.topology.get_node(NetworkTopology.DATABASE)
        if "T1046" in incident_types:
            if self.compromise_init_time is None:
                self.compromise_init_time = self.sim_time_s
            
            # Defense mechanism: segmentation_mode
            # 0 = Default (no isolation, CI runner can probe)
            # 1 = Strict ACL
            # 2 = Quarantine CI Subnet (total containment)
            if enforced.segmentation_mode >= 1:
                # Contained!
                self.topology.isolate_node(NetworkTopology.CI_RUNNER, True)
                if self.containment_time is None:
                    self.containment_time = self.sim_time_s
                db_node.health_index = 1.0
                db_node.is_compromised = False
            else:
                # Uncontained breach: lateral movement reaches DB
                self.topology.mark_compromised(NetworkTopology.DATABASE, True)
                db_node.health_index = 0.1
                step_legit_successes = 0  # Complete data integrity failure
        else:
            db_node.health_index = 1.0 if not db_node.is_compromised else 0.2

        # 5. Accumulate Metrics
        step_legit_successes = max(0, min(step_legit_attempts, step_legit_successes))
        self.total_legitimate_requests += step_legit_attempts
        self.successful_legitimate_requests += step_legit_successes

        # Resiliency degradation index (integral of lost throughput)
        step_throughput_ratio = step_legit_successes / float(step_legit_attempts)
        self.accumulated_degradation += (1.0 - step_throughput_ratio) * self.dt_seconds

        # 6. Compute Observation Vector S_t in R^14
        obs = self._compute_observation()
        self.last_observation = obs

        # 7. Compute Reward Function R_t
        reward = self._compute_reward(
            legit_ratio=step_throughput_ratio,
            validation=validation,
            enforced=enforced
        )

        terminated = False
        truncated = self.current_step >= self.max_steps
        info = self._get_info()

        return obs, float(reward), terminated, truncated, info

    def _compute_observation(self) -> np.ndarray:
        edge = self.topology.get_node(NetworkTopology.EDGE_GW)
        auth = self.topology.get_node(NetworkTopology.AUTH_SVC)
        app = self.topology.get_node(NetworkTopology.APP_SVC)
        db = self.topology.get_node(NetworkTopology.DATABASE)

        all_nodes = list(self.topology.get_all_nodes().values())
        avg_cpu = float(np.mean([n.cpu_utilization for n in all_nodes]))
        avg_mem = float(np.mean([n.memory_utilization for n in all_nodes]))
        avg_conn = float(np.mean([n.connection_utilization for n in all_nodes]))

        active_inc = self.scenario.get_active_incidents(self.sim_time_s)
        severity = float(np.mean([inc.intensity for inc in active_inc])) if active_inc else 0.0

        auth_latency_norm = min(1.0, auth.response_latency_ms / 1000.0)
        app_err_rate = min(1.0, (1.0 - app.health_index))
        ew_anomaly = 1.0 if any(inc.technique_id == "T1046" for inc in active_inc) else 0.0

        legit_rate = (
            self.successful_legitimate_requests / max(1, self.total_legitimate_requests)
            if self.total_legitimate_requests > 0 else 1.0
        )

        # Defensive overhead (normalized penalty for strict rules)
        enforced_vals = self.ddps.current_enforced_policy.to_list()
        defensive_overhead = float(sum(enforced_vals)) / 16.0  # max 16 (8 * 2)

        s_t = np.array([
            float(edge.health_index),
            float(auth.health_index),
            float(app.health_index),
            float(db.health_index),
            avg_cpu,
            avg_mem,
            float(edge.connection_utilization),
            auth_latency_norm,
            app_err_rate,
            avg_conn,
            ew_anomaly,
            severity,
            float(legit_rate),
            defensive_overhead
        ], dtype=np.float32)

        return np.clip(s_t, 0.0, 1.0)

    def _compute_reward(
        self,
        legit_ratio: float,
        validation: Any,
        enforced: DefensiveActionProposal
    ) -> float:
        """
        Reward function compliant with Section 6.4:
        R_t = w_a * Availability + w_c * Containment + w_i * Invariants
              - w_o * Overhead - w_f * FalsePositives - w_ch * Churn
        """
        w_a = 0.35
        w_c = 0.25
        w_i = 0.20
        w_o = 0.05
        w_f = 0.10
        w_ch = 0.05

        availability = legit_ratio
        
        # Containment: is DB protected and CI runner isolated if attack occurred
        db = self.topology.get_node(NetworkTopology.DATABASE)
        containment = 1.0 if not db.is_compromised else 0.0

        # Invariant compliance: was action approved without security bypass
        invariants = 1.0 if validation.is_approved else 0.0

        # Overhead penalty
        overhead = float(sum(enforced.to_list())) / 16.0

        # False positive penalty (e.g., dropping legitimate requests)
        false_positive = 1.0 - legit_ratio

        # Policy churn & stability penalty
        churn = validation.stability_penalty

        r_t = (
            w_a * availability
            + w_c * containment
            + w_i * invariants
            - w_o * overhead
            - w_f * false_positive
            - w_ch * churn
        )
        return float(r_t)

    def _get_info(self) -> Dict[str, Any]:
        avail_pct = (
            (self.successful_legitimate_requests / max(1, self.total_legitimate_requests)) * 100.0
            if self.total_legitimate_requests > 0 else 100.0
        )
        
        mttc = None
        if self.compromise_init_time is not None and self.containment_time is not None:
            mttc = max(0.0, self.containment_time - self.compromise_init_time)

        # Blast radius: compromised or degraded nodes / total nodes
        nodes = list(self.topology.get_all_nodes().values())
        impacted = sum(1 for n in nodes if n.is_compromised or n.health_index < 0.75)
        blast_radius = impacted / float(len(nodes))

        metrics = EvaluationMetrics(
            effective_availability_pct=avail_pct,
            mean_time_to_containment_s=mttc,
            blast_radius_factor=blast_radius,
            resilience_degradation_index=self.accumulated_degradation,
            security_invariant_violations=self.ddps.rejected_count,
            policy_churn_count=len(self.ddps.audit_log),
            total_legitimate_requests=self.total_legitimate_requests,
            successful_legitimate_requests=self.successful_legitimate_requests
        )

        return {
            "environment_id": self.environment_id,
            "step": self.current_step,
            "sim_time_s": self.sim_time_s,
            "enforced_policy": self.ddps.current_enforced_policy.model_dump(),
            "metrics": metrics.model_dump()
        }
