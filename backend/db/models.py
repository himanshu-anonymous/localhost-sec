"""
SQLAlchemy ORM Models for localhost (BASTION X).
Encapsulates all 18 PostgreSQL tables across 5 domains:
1. Identity & Virtual Environments
2. MITRE ATT&CK Catalog & AEGIS Mappings
3. Simulations, Observations & Technique Detections
4. PPO RL, DDPS & Defense Actions
5. Gemma 4 Analysis & Evaluation
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Boolean,
    DateTime,
    Numeric,
    Text,
    ForeignKey,
    JSON,
    Index,
    Uuid,
)
from sqlalchemy.orm import relationship
from backend.db.postgres import Base


# ============================================================================
# DOMAIN 1: IDENTITY & VIRTUAL ENVIRONMENTS
# ============================================================================

class User(Base):
    __tablename__ = "users"

    user_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    username = Column(String(128), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(64), unique=True, nullable=False)  # 'admin', 'operator', 'analyst', 'auditor'


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(Uuid, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True)

    user = relationship("User", back_populates="roles")


class Environment(Base):
    __tablename__ = "environments"

    environment_id = Column(String(32), primary_key=True)  # 'ENV-A', 'ENV-B', 'ENV-C', 'ENV-D'
    name = Column(String(128), nullable=False)
    mode = Column(String(64), nullable=False)  # 'static_baseline', 'adaptive_rl', 'hardened_strict', 'experimental'
    description = Column(Text, nullable=False)
    baseline_topology_template = Column(JSON, default=dict, nullable=False)
    baseline_policy_config = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


# ============================================================================
# DOMAIN 2: MITRE ATT&CK CATALOG & AEGIS MAPPINGS
# ============================================================================

class MitreCatalogVersion(Base):
    __tablename__ = "mitre_catalog_versions"

    version_id = Column(String(64), primary_key=True)
    stix_sha256 = Column(String(64), unique=True, nullable=False)
    source_url = Column(String(512), nullable=False)
    git_commit_tag = Column(String(64), nullable=False)
    imported_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    technique_count = Column(Integer, nullable=False)


class MitreTechnique(Base):
    __tablename__ = "mitre_techniques"

    technique_id = Column(String(32), primary_key=True)
    parent_technique_id = Column(String(32), ForeignKey("mitre_techniques.technique_id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    tactics = Column(JSON, default=list, nullable=False)
    platforms = Column(JSON, default=list, nullable=False)
    is_subtechnique = Column(Boolean, default=False, nullable=False)
    source_modified = Column(DateTime(timezone=True), nullable=True)
    source_version = Column(String(64), ForeignKey("mitre_catalog_versions.version_id"), nullable=True)
    mitre_url = Column(String(512), nullable=False)

    mapping = relationship("MitreMapping", back_populates="technique", uselist=False)


class MitreMapping(Base):
    __tablename__ = "mitre_mappings"

    technique_id = Column(String(32), ForeignKey("mitre_techniques.technique_id", ondelete="CASCADE"), primary_key=True)
    priority_tier = Column(String(8), default="P2", nullable=False)  # 'P0', 'P1', 'P2', 'P3'
    scenario_id = Column(String(64), unique=True, nullable=True)
    detector_id = Column(String(64), nullable=True)
    defense_modules = Column(JSON, default=list, nullable=False)
    simulation_mode = Column(String(32), default="safe_local", nullable=False)
    implementation_status = Column(String(64), default="not_started", nullable=False)
    safety_bounds = Column(JSON, default=dict, nullable=False)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    technique = relationship("MitreTechnique", back_populates="mapping")


# ============================================================================
# DOMAIN 3: SIMULATIONS, OBSERVATIONS & DETECTIONS
# ============================================================================

class AttackScenario(Base):
    __tablename__ = "attack_scenarios"

    scenario_id = Column(String(64), primary_key=True)
    technique_id = Column(String(32), ForeignKey("mitre_techniques.technique_id"), nullable=False)
    name = Column(String(128), nullable=False)
    target_service = Column(String(64), nullable=False)
    max_duration_seconds = Column(Integer, default=60, nullable=False)
    max_request_rate_rps = Column(Integer, default=50, nullable=False)
    default_parameters = Column(JSON, default=dict, nullable=False)


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    run_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    environment_id = Column(String(32), ForeignKey("environments.environment_id"), nullable=False)
    experiment_mode = Column(String(32), nullable=False)  # 'static', 'adaptive'
    scenario_id = Column(String(64), ForeignKey("attack_scenarios.scenario_id"), nullable=False)
    ground_truth_technique_id = Column(String(32), ForeignKey("mitre_techniques.technique_id"), nullable=False)
    catalog_version_id = Column(String(64), ForeignKey("mitre_catalog_versions.version_id"), nullable=False)
    initiated_by = Column(Uuid, ForeignKey("users.user_id"), nullable=True)
    status = Column(String(32), nullable=False)  # 'initializing', 'running', 'completed', 'aborted', 'failed'
    configuration = Column(JSON, default=dict, nullable=False)
    final_topology_snapshot = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)


class TelemetryMetric(Base):
    __tablename__ = "telemetry_metrics"

    metric_id = Column(BigInteger, primary_key=True, autoincrement=True)
    run_id = Column(Uuid, ForeignKey("simulation_runs.run_id", ondelete="CASCADE"), nullable=False)
    environment_id = Column(String(32), ForeignKey("environments.environment_id"), nullable=False)
    node_id = Column(String(64), nullable=False)
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    cpu_pct = Column(Numeric(5, 2), nullable=False)
    memory_pct = Column(Numeric(5, 2), nullable=False)
    req_per_sec = Column(Numeric(8, 2), nullable=False)
    auth_latency_ms = Column(Numeric(8, 2), nullable=False)
    failed_login_count = Column(Integer, default=0, nullable=False)
    error_rate_pct = Column(Numeric(5, 2), default=0.0, nullable=False)


class SecurityObservation(Base):
    __tablename__ = "security_observations"

    event_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    run_id = Column(Uuid, ForeignKey("simulation_runs.run_id", ondelete="CASCADE"), nullable=False)
    correlation_id = Column(Uuid, nullable=False)
    observed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    source = Column(String(64), nullable=False)
    event_type = Column(String(64), nullable=False)
    target_service = Column(String(64), nullable=True)
    source_identity = Column(String(64), nullable=True)
    severity = Column(String(16), nullable=False)  # 'low', 'medium', 'high', 'critical'
    confidence = Column(Numeric(5, 4), default=1.0000, nullable=False)
    metadata_json = Column("metadata", JSON, default=dict, nullable=False)


class TechniqueDetection(Base):
    __tablename__ = "technique_detections"

    detection_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    run_id = Column(Uuid, ForeignKey("simulation_runs.run_id", ondelete="CASCADE"), nullable=False)
    correlation_id = Column(Uuid, nullable=False)
    inferred_technique_id = Column(String(32), ForeignKey("mitre_techniques.technique_id"), nullable=False)
    detector_id = Column(String(64), nullable=False)
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    confidence = Column(Numeric(5, 4), nullable=False)
    evidence_event_ids = Column(JSON, default=list, nullable=False)
    analyst_status = Column(String(32), default="unreviewed", nullable=False)


# ============================================================================
# DOMAIN 4: PPO REINFORCEMENT LEARNING, DDPS & DEFENSE ORCHESTRATION
# ============================================================================

class TrainingRun(Base):
    __tablename__ = "training_runs"

    training_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    algorithm = Column(String(32), default="PPO", nullable=False)
    policy_version = Column(String(64), unique=True, nullable=False)
    total_timesteps = Column(Integer, nullable=False)
    hyperparameters = Column(JSON, default=dict, nullable=False)
    mean_reward = Column(Numeric(10, 4), nullable=True)
    model_checkpoint_path = Column(String(512), nullable=False)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class RLAction(Base):
    __tablename__ = "rl_actions"

    rl_action_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    run_id = Column(Uuid, ForeignKey("simulation_runs.run_id", ondelete="CASCADE"), nullable=False)
    training_id = Column(Uuid, ForeignKey("training_runs.training_id"), nullable=True)
    correlation_id = Column(Uuid, nullable=False)
    step_number = Column(Integer, nullable=False)
    state_vector = Column(JSON, nullable=False)
    proposed_module = Column(String(64), nullable=False)
    proposed_action = Column(String(64), nullable=False)
    proposed_parameters = Column(JSON, default=dict, nullable=False)
    step_reward = Column(Numeric(8, 4), nullable=True)
    proposed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ActionApproval(Base):
    __tablename__ = "action_approvals"

    approval_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    run_id = Column(Uuid, ForeignKey("simulation_runs.run_id", ondelete="CASCADE"), nullable=False)
    rl_action_id = Column(Uuid, ForeignKey("rl_actions.rl_action_id", ondelete="CASCADE"), nullable=True)
    correlation_id = Column(Uuid, nullable=False)
    schema_valid = Column(Boolean, nullable=False)
    parameter_bounds_valid = Column(Boolean, nullable=False)
    security_invariant_valid = Column(Boolean, nullable=False)
    stability_check_valid = Column(Boolean, nullable=False)
    ddps_decision = Column(String(32), nullable=False)  # 'approved', 'rejected', 'escalated_to_human'
    rejection_reason = Column(Text, nullable=True)
    requires_human_approval = Column(Boolean, default=False, nullable=False)
    human_approved_by = Column(Uuid, ForeignKey("users.user_id"), nullable=True)
    validated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class SecurityViolation(Base):
    __tablename__ = "security_violations"

    violation_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    run_id = Column(Uuid, ForeignKey("simulation_runs.run_id", ondelete="CASCADE"), nullable=False)
    approval_id = Column(Uuid, ForeignKey("action_approvals.approval_id", ondelete="CASCADE"), nullable=False)
    violated_invariant_code = Column(String(64), nullable=False)
    attempted_action = Column(JSON, nullable=False)
    severity = Column(String(16), default="high", nullable=False)
    logged_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class DefenseAction(Base):
    __tablename__ = "defense_actions"

    action_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    run_id = Column(Uuid, ForeignKey("simulation_runs.run_id", ondelete="CASCADE"), nullable=False)
    approval_id = Column(Uuid, ForeignKey("action_approvals.approval_id"), nullable=False)
    correlation_id = Column(Uuid, nullable=False)
    module_id = Column(String(64), nullable=False)
    action_name = Column(String(64), nullable=False)
    policy_version = Column(String(64), nullable=False)
    requested_by = Column(String(32), nullable=False)  # 'ppo_agent', 'deterministic_policy', 'human_operator'
    approved = Column(Boolean, default=False, nullable=False)
    applied_at = Column(DateTime(timezone=True), nullable=True)
    result = Column(String(32), nullable=False)  # 'applied_verified', 'failed', 'rolled_back'
    rollback_reference = Column(JSON, default=dict, nullable=False)
    audit_metadata = Column(JSON, default=dict, nullable=False)


class DefencePolicy(Base):
    __tablename__ = "defence_policies"

    policy_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    environment_id = Column(String(32), ForeignKey("environments.environment_id"), nullable=False)
    run_id = Column(Uuid, ForeignKey("simulation_runs.run_id", ondelete="CASCADE"), nullable=True)
    version_num = Column(Integer, nullable=False)
    rate_limit_rps = Column(Integer, nullable=False)
    auth_throttle_threshold = Column(Integer, nullable=False)
    session_ttl_seconds = Column(Integer, nullable=False)
    isolated_nodes = Column(JSON, default=list, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


# ============================================================================
# DOMAIN 5: GEMMA 4 ANALYSIS & STATIC VS. ADAPTIVE EVALUATION
# ============================================================================

class GemmaReport(Base):
    __tablename__ = "gemma_reports"

    report_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    run_id = Column(Uuid, ForeignKey("simulation_runs.run_id", ondelete="CASCADE"), nullable=False)
    detection_id = Column(Uuid, ForeignKey("technique_detections.detection_id"), nullable=True)
    correlation_id = Column(Uuid, nullable=False)
    model_version = Column(String(64), default="gemma-4-it", nullable=False)
    incident_summary = Column(Text, nullable=False)
    inferred_technique_id = Column(String(32), ForeignKey("mitre_techniques.technique_id"), nullable=True)
    confidence = Column(Numeric(5, 4), nullable=True)
    recommended_modules = Column(JSON, default=list, nullable=False)
    recommended_actions = Column(JSON, default=list, nullable=False)
    explanation_markdown = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    eval_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    run_id = Column(Uuid, ForeignKey("simulation_runs.run_id", ondelete="CASCADE"), unique=True, nullable=False)
    environment_id = Column(String(32), ForeignKey("environments.environment_id"), nullable=False)
    technique_id = Column(String(32), ForeignKey("mitre_techniques.technique_id"), nullable=False)
    ground_truth_matched = Column(Boolean, nullable=False)
    detection_time_ms = Column(Numeric(10, 2), nullable=True)
    mitigation_time_ms = Column(Numeric(10, 2), nullable=True)
    legitimate_success_rate = Column(Numeric(5, 4), nullable=False)
    false_positive_rate = Column(Numeric(5, 4), nullable=False)
    latency_p50_ms = Column(Numeric(8, 2), nullable=False)
    latency_p95_ms = Column(Numeric(8, 2), nullable=False)
    recovery_time_ms = Column(Numeric(10, 2), nullable=True)
    blast_radius_fraction = Column(Numeric(5, 4), nullable=True)
    resource_degradation_index = Column(Numeric(5, 4), nullable=True)
    computed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


# ============================================================================
# PERFORMANCE INDEXES
# ============================================================================

Index("idx_obs_run_time", SecurityObservation.run_id, SecurityObservation.observed_at)
Index("idx_det_run_tech", TechniqueDetection.run_id, TechniqueDetection.inferred_technique_id)
Index("idx_telemetry_run_node", TelemetryMetric.run_id, TelemetryMetric.node_id, TelemetryMetric.recorded_at)
Index("idx_eval_tech_env", EvaluationResult.technique_id, EvaluationResult.environment_id)
