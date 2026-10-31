# BASTION X & AEGIS: Master Database Architecture and Execution Plan

**Project:** BASTION X / AEGIS (Adaptive Elastic Guard & Intelligent Security)

**Database Architecture:** Persistent Relational Store (PostgreSQL) + Ephemeral Runtime Graph (Neo4j)

**Threat Framework:** MITRE ATT&CK Enterprise — Containers Platform (STIX 2.1)

**Control Loop:** PPO Reinforcement Learning + DDPS 5-Stage Policy Gate + Gemma 4 Analyst

## 1. Executive Architecture and Storage Ownership

BASTION X (integrated with the AEGIS MITRE ATT&CK Containers framework) uses a hybrid two-database architecture. PostgreSQL serves as the permanent system of record for all catalog data, simulation runs, observations, detections, reinforcement learning records, policy approvals, and evaluation metrics. Neo4j operates strictly as a temporary, run-scoped graph scratchpad that hydrates when a simulation starts and purges automatically when the run completes.

```text
                       MITRE ATT&CK STIX 2.1 Snapshot
                      (Pinned enterprise-attack.json)
                                     |
                                     v
                         MITRE Catalog Importer
                                     |
                                     v
+-------------------------------------------------------------------------+
|                    POSTGRESQL (MAIN PERSISTENT DB)                      |
|  - MITRE Catalog (mitre_techniques) & AEGIS Mappings (mitre_mappings)   |
|  - Environments (ENV-A..D) & Simulation Runs (ground_truth_technique)   |
|  - Normalized Security Observations & Independent Technique Detections  |
|  - PPO Training Runs, RL Actions & DDPS 5-Stage Action Approvals        |
|  - Defense Orchestrator Audit Trail & Rollback References               |
|  - Gemma 4 Incident Reports & Static vs. Adaptive Evaluation Metrics    |
+-------------------------------------------------------------------------+
          |                                                  ^
          | 1. Hydrate Topology at Run Start                 | 4. Snapshot Final Topology
          | 2. Push Approved DDPS Edge Mutations             |    & Blast Radius Metrics
          v                                                  |    before Graph Teardown
+-------------------------------------------------------------------------+
|                  NEO4J (TEMPORARY RUNTIME GRAPH DB)                     |
|  - Ephemeral per active run_id + environment_id                         |
|  - Live Container & Service Topology (Gateway, AppServer, DB, Zones)    |
|  - Active Traffic Policies (ALLOWS_TRAFFIC_TO, DENIES_TRAFFIC_TO)       |
|  - Synthetic Attack Propagation Paths & Live Blast Radius Calculation   |
|  - Automatically purged (DETACH DELETE) upon simulation run completion  |
+-------------------------------------------------------------------------+

```

| Storage Layer | Persistence | Scope | Primary Role |
| --- | --- | --- | --- |
| **PostgreSQL** | Permanent | Global | Operational records and audit history |
| **Neo4j** | Temporary | Active Run | Live topology and blast radius |
| **In-Memory Store** | Ephemeral | Sub-second | Live Gymnasium state and WebSockets |
| **Filesystem** | Permanent | Versioned | Pinned STIX files and PPO models |

PostgreSQL owns all relational and historical data across simulation trials, while Neo4j holds only active container relationships during an ongoing run. High-frequency reinforcement learning state vectors remain in memory, and large binary checkpoints stay on disk.

### Core Architectural Rules

* **Ground-Truth Isolation:** PostgreSQL stores the ground-truth technique ID in the simulation run record, which detectors and PPO agents are strictly forbidden from reading during execution.
* **Upstream Immutability:** Official MITRE STIX records are imported into a read-only catalog table, while project scenarios, detectors, and defense modules live in a separate mapping table.
* **Ephemeral Lifecycle:** FastAPI hydrates Neo4j from PostgreSQL topology templates at run start, mutates edges on approved actions, snapshots final state to PostgreSQL, and deletes the graph at run end.
* **DDPS Gate:** Neither PPO nor Gemma 4 can modify containers or network rules directly; every proposed action must pass the 5-stage Dynamic Defensive Policy Stack.
* **Correlation Tracing:** Every observation, detection, RL decision, DDPS validation, defense action, and Gemma 4 report shares a run UUID and correlation UUID for end-to-end auditability.

## 2. MITRE ATT&CK Containers Prioritization and Safe Lab Mapping

| Technique ID | Technique Name | Priority | Simulation Mode | Primary Defense |
| --- | --- | --- | --- | --- |
| **T1110** | Brute Force | P0 | Safe Local | Rate Limiter |
| **T1498** | Network DoS | P0 | Safe Local | Traffic Shield |
| **T1613** | Container Discovery | P0 | Safe Local | Network Segmentation |
| **T1046** | Service Discovery | P1 | Safe Local | Network Segmentation |
| **T1550** | Alternate Auth Material | P1 | Synthetic Only | Session Guardian |
| **T1552** | Unsecured Credentials | P1 | Safe Local | Secret Scanner |
| **T1610** | Deploy Container | P1 | Safe Local | Container Policy |
| **T1525** | Implant Internal Image | P2 | Safe Local | Image Policy |
| **T1611** | Escape to Host | P2 | Blocked Event | Isolation Engine |
| **T1496** | Resource Hijacking | P2 | Safe Local | Resource Monitor |

All container scenarios execute inside an isolated Docker network without mounting the host Docker socket into the attack runner. High-risk techniques like T1611 (Escape to Host), T1485 (Data Destruction), T1490 (Inhibit System Recovery), and T1685 (Disable or Modify Tools) use synthetic or blocked-precondition events rather than destructive payloads.

## 3. PostgreSQL Schema Design (Main Persistent Database)

The PostgreSQL database contains 18 tables organized across five functional domains: Identity and Environments, MITRE Catalog and Mappings, Simulation and Detection, Reinforcement Learning and DDPS Governance, and AI Reporting and Evaluation.

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- DOMAIN 1: IDENTITY & VIRTUAL ENVIRONMENTS
-- ============================================================================

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name TEXT UNIQUE NOT NULL
        CHECK (role_name IN ('admin', 'operator', 'analyst', 'auditor'))
);

CREATE TABLE user_roles (
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    role_id INT REFERENCES roles(role_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE environments (
    environment_id TEXT PRIMARY KEY
        CHECK (environment_id IN ('ENV-A', 'ENV-B', 'ENV-C', 'ENV-D')),
    name TEXT NOT NULL,
    mode TEXT NOT NULL
        CHECK (mode IN ('static_baseline', 'adaptive_rl', 'hardened_strict', 'experimental')),
    description TEXT NOT NULL,
    baseline_topology_template JSONB NOT NULL DEFAULT '{}',
    baseline_policy_config JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- DOMAIN 2: MITRE ATT&CK CATALOG & AEGIS MAPPINGS
-- ============================================================================

CREATE TABLE mitre_catalog_versions (
    version_id TEXT PRIMARY KEY,
    stix_sha256 TEXT UNIQUE NOT NULL,
    source_url TEXT NOT NULL,
    git_commit_tag TEXT NOT NULL,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    technique_count INT NOT NULL
);

CREATE TABLE mitre_techniques (
    technique_id TEXT PRIMARY KEY,
    parent_technique_id TEXT REFERENCES mitre_techniques(technique_id),
    name TEXT NOT NULL,
    description TEXT,
    tactics JSONB NOT NULL DEFAULT '[]',
    platforms JSONB NOT NULL DEFAULT '[]',
    is_subtechnique BOOLEAN NOT NULL DEFAULT FALSE,
    source_modified TIMESTAMPTZ,
    source_version TEXT REFERENCES mitre_catalog_versions(version_id),
    mitre_url TEXT NOT NULL
);

CREATE TABLE mitre_mappings (
    technique_id TEXT PRIMARY KEY REFERENCES mitre_techniques(technique_id) ON DELETE CASCADE,
    priority_tier TEXT NOT NULL DEFAULT 'P2'
        CHECK (priority_tier IN ('P0', 'P1', 'P2', 'P3')),
    scenario_id TEXT UNIQUE,
    detector_id TEXT,
    defense_modules JSONB NOT NULL DEFAULT '[]',
    simulation_mode TEXT NOT NULL DEFAULT 'safe_local'
        CHECK (simulation_mode IN (
            'safe_local',
            'synthetic_only',
            'blocked_precondition_only',
            'disabled'
        )),
    implementation_status TEXT NOT NULL DEFAULT 'not_started'
        CHECK (implementation_status IN (
            'not_started',
            'catalog_imported',
            'scenario_implemented',
            'telemetry_verified',
            'detection_implemented',
            'detection_tested',
            'mitigation_tested',
            'regression_passed'
        )),
    safety_bounds JSONB NOT NULL DEFAULT '{}',
    notes TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- DOMAIN 3: SIMULATIONS, OBSERVATIONS & INDEPENDENT DETECTIONS
-- ============================================================================

CREATE TABLE attack_scenarios (
    scenario_id TEXT PRIMARY KEY,
    technique_id TEXT NOT NULL REFERENCES mitre_techniques(technique_id),
    name TEXT NOT NULL,
    target_service TEXT NOT NULL,
    max_duration_seconds INT NOT NULL DEFAULT 60,
    max_request_rate_rps INT NOT NULL DEFAULT 50,
    default_parameters JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE simulation_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    environment_id TEXT NOT NULL REFERENCES environments(environment_id),
    experiment_mode TEXT NOT NULL CHECK (experiment_mode IN ('static', 'adaptive')),
    scenario_id TEXT NOT NULL REFERENCES attack_scenarios(scenario_id),
    ground_truth_technique_id TEXT NOT NULL REFERENCES mitre_techniques(technique_id),
    catalog_version_id TEXT NOT NULL REFERENCES mitre_catalog_versions(version_id),
    initiated_by UUID REFERENCES users(user_id),
    status TEXT NOT NULL
        CHECK (status IN ('initializing', 'running', 'completed', 'aborted', 'failed')),
    configuration JSONB NOT NULL DEFAULT '{}',
    final_topology_snapshot JSONB,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);

CREATE TABLE telemetry_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    environment_id TEXT NOT NULL REFERENCES environments(environment_id),
    node_id TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    cpu_pct NUMERIC(5,2) NOT NULL,
    memory_pct NUMERIC(5,2) NOT NULL,
    req_per_sec NUMERIC(8,2) NOT NULL,
    auth_latency_ms NUMERIC(8,2) NOT NULL,
    failed_login_count INT NOT NULL DEFAULT 0,
    error_rate_pct NUMERIC(5,2) NOT NULL DEFAULT 0.0
);

CREATE TABLE security_observations (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    correlation_id UUID NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source TEXT NOT NULL,
    event_type TEXT NOT NULL,
    target_service TEXT,
    source_identity TEXT,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    confidence NUMERIC(5,4) DEFAULT 1.0000,
    metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE technique_detections (
    detection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    correlation_id UUID NOT NULL,
    inferred_technique_id TEXT NOT NULL REFERENCES mitre_techniques(technique_id),
    detector_id TEXT NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confidence NUMERIC(5,4) NOT NULL,
    evidence_event_ids JSONB NOT NULL DEFAULT '[]',
    analyst_status TEXT NOT NULL DEFAULT 'unreviewed'
        CHECK (analyst_status IN ('unreviewed', 'confirmed_true_positive', 'false_positive'))
);

-- ============================================================================
-- DOMAIN 4: PPO REINFORCEMENT LEARNING, DDPS & DEFENSE ORCHESTRATION
-- ============================================================================

CREATE TABLE training_runs (
    training_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    algorithm TEXT NOT NULL DEFAULT 'PPO',
    policy_version TEXT UNIQUE NOT NULL,
    total_timesteps INT NOT NULL,
    hyperparameters JSONB NOT NULL DEFAULT '{}',
    mean_reward NUMERIC(10,4),
    model_checkpoint_path TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE rl_actions (
    rl_action_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    training_id UUID REFERENCES training_runs(training_id),
    correlation_id UUID NOT NULL,
    step_number INT NOT NULL,
    state_vector JSONB NOT NULL,
    proposed_module TEXT NOT NULL,
    proposed_action TEXT NOT NULL,
    proposed_parameters JSONB NOT NULL DEFAULT '{}',
    step_reward NUMERIC(8,4),
    proposed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE action_approvals (
    approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    rl_action_id UUID REFERENCES rl_actions(rl_action_id) ON DELETE CASCADE,
    correlation_id UUID NOT NULL,
    schema_valid BOOLEAN NOT NULL,
    parameter_bounds_valid BOOLEAN NOT NULL,
    security_invariant_valid BOOLEAN NOT NULL,
    stability_check_valid BOOLEAN NOT NULL,
    ddps_decision TEXT NOT NULL
        CHECK (ddps_decision IN ('approved', 'rejected', 'escalated_to_human')),
    rejection_reason TEXT,
    requires_human_approval BOOLEAN NOT NULL DEFAULT FALSE,
    human_approved_by UUID REFERENCES users(user_id),
    validated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE security_violations (
    violation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    approval_id UUID NOT NULL REFERENCES action_approvals(approval_id) ON DELETE CASCADE,
    violated_invariant_code TEXT NOT NULL,
    attempted_action JSONB NOT NULL,
    severity TEXT NOT NULL DEFAULT 'high',
    logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE defense_actions (
    action_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    approval_id UUID NOT NULL REFERENCES action_approvals(approval_id),
    correlation_id UUID NOT NULL,
    module_id TEXT NOT NULL,
    action_name TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    requested_by TEXT NOT NULL
        CHECK (requested_by IN ('ppo_agent', 'deterministic_policy', 'human_operator')),
    approved BOOLEAN NOT NULL DEFAULT FALSE,
    applied_at TIMESTAMPTZ,
    result TEXT NOT NULL CHECK (result IN ('applied_verified', 'failed', 'rolled_back')),
    rollback_reference JSONB NOT NULL DEFAULT '{}',
    audit_metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE defence_policies (
    policy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    environment_id TEXT NOT NULL REFERENCES environments(environment_id),
    run_id UUID REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    version_num INT NOT NULL,
    rate_limit_rps INT NOT NULL,
    auth_throttle_threshold INT NOT NULL,
    session_ttl_seconds INT NOT NULL,
    isolated_nodes JSONB NOT NULL DEFAULT '[]',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- DOMAIN 5: GEMMA 4 ANALYSIS & STATIC VS. ADAPTIVE EVALUATION
-- ============================================================================

CREATE TABLE gemma_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    detection_id UUID REFERENCES technique_detections(detection_id),
    correlation_id UUID NOT NULL,
    model_version TEXT NOT NULL DEFAULT 'gemma-4-it',
    incident_summary TEXT NOT NULL,
    inferred_technique_id TEXT REFERENCES mitre_techniques(technique_id),
    confidence NUMERIC(5,4),
    recommended_modules JSONB NOT NULL DEFAULT '[]',
    recommended_actions JSONB NOT NULL DEFAULT '[]',
    explanation_markdown TEXT NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE evaluation_results (
    eval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID UNIQUE NOT NULL REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    environment_id TEXT NOT NULL REFERENCES environments(environment_id),
    technique_id TEXT NOT NULL REFERENCES mitre_techniques(technique_id),
    ground_truth_matched BOOLEAN NOT NULL,
    detection_time_ms NUMERIC(10,2),
    mitigation_time_ms NUMERIC(10,2),
    legitimate_success_rate NUMERIC(5,4) NOT NULL,
    false_positive_rate NUMERIC(5,4) NOT NULL,
    latency_p50_ms NUMERIC(8,2) NOT NULL,
    latency_p95_ms NUMERIC(8,2) NOT NULL,
    recovery_time_ms NUMERIC(10,2),
    blast_radius_fraction NUMERIC(5,4),
    resource_degradation_index NUMERIC(5,4),
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR QUERY PERFORMANCE
-- ============================================================================

CREATE INDEX idx_obs_run_time ON security_observations(run_id, observed_at);
CREATE INDEX idx_det_run_tech ON technique_detections(run_id, inferred_technique_id);
CREATE INDEX idx_telemetry_run_node ON telemetry_metrics(run_id, node_id, recorded_at);
CREATE INDEX idx_eval_tech_env ON evaluation_results(technique_id, environment_id);

```

## 4. Neo4j Schema and Ephemeral Lifecycle (Temporary Database)

Neo4j represents live network topology, trust zones, service dependencies, and active attack paths only while a simulation is running. Every node and edge includes run and environment identifiers so ENV-A, ENV-B, ENV-C, and ENV-D can run in parallel without state collisions.

### Graph Labels and Relationships

* **Node Labels:** ContainerNode, Gateway, AppServer, Database, SecurityZone, and ActiveIncident.
* **Relationship Types:** CONNECTS_TO, ALLOWS_TRAFFIC_TO, DENIES_TRAFFIC_TO, DEPENDS_ON, BELONGS_TO_ZONE, and TARGETS_NODE.

### Cypher Lifecycle Queries

```cypher
// 1. ONE-TIME STARTUP CONSTRAINT & INDEX INITIALIZATION
CREATE CONSTRAINT container_run_unique IF NOT EXISTS
FOR (n:ContainerNode) REQUIRE (n.run_id, n.environment_id, n.node_id) IS UNIQUE;

CREATE INDEX container_lookup_idx IF NOT EXISTS
FOR (n:ContainerNode) ON (n.run_id, n.environment_id);

// 2. HYDRATION AT SIMULATION START (From PostgreSQL environments.baseline_topology_template)
UNWIND $nodes AS node
MERGE (c:ContainerNode {
    run_id: $run_id,
    environment_id: $env_id,
    node_id: node.node_id
})
SET c.name = node.name,
    c.role = node.role,
    c.zone = node.zone,
    c.status = 'healthy',
    c.compromised = false,
    c.created_at = datetime();

UNWIND $edges AS edge
MATCH (src:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: edge.source})
MATCH (dst:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: edge.target})
MERGE (src)-[r:ALLOWS_TRAFFIC_TO {run_id: $run_id}]->(dst)
SET r.port = edge.port,
    r.rate_limit_rps = edge.rate_limit_rps,
    r.policy_version = 'baseline-v1';

// 3. ATTACH ACTIVE INCIDENT MARKER WHEN DETECTOR IDENTIFIES AN ATTACK
MATCH (target:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: $target_node})
MERGE (inc:ActiveIncident {run_id: $run_id, detection_id: $detection_id})
SET inc.inferred_technique_id = $technique_id,
    inc.confidence = $confidence,
    inc.detected_at = datetime()
MERGE (inc)-[:TARGETS_NODE {run_id: $run_id}]->(target);

// 4. MUTATE GRAPH EDGES WHEN DDPS APPROVES A DEFENSIVE ACTION
MATCH (src:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: $source_node})
      -[allow:ALLOWS_TRAFFIC_TO {run_id: $run_id}]->
      (dst:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: $target_node})
DELETE allow
MERGE (src)-[deny:DENIES_TRAFFIC_TO {run_id: $run_id}]->(dst)
SET deny.action_id = $action_id,
    deny.reason = $technique_id,
    deny.applied_at = datetime();

// 5. COMPUTE BLAST RADIUS FRACTION BEFORE TEARDOWN
MATCH (target:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: $attacked_node_id})
OPTIONAL MATCH path = (target)-[:ALLOWS_TRAFFIC_TO*1..4 {run_id: $run_id}]->(reachable:ContainerNode)
WITH target, collect(DISTINCT reachable.node_id) AS exposed_nodes
MATCH (all_nodes:ContainerNode {run_id: $run_id, environment_id: $env_id})
RETURN size(exposed_nodes) AS exposed_count,
       count(all_nodes) AS total_nodes,
       toFloat(size(exposed_nodes)) / count(all_nodes) AS blast_radius_fraction,
       exposed_nodes;

// 6. GUARANTEED EPHEMERAL TEARDOWN AT SIMULATION END
MATCH (n {run_id: $run_id})
DETACH DELETE n;

```

## 5. Backend Implementation and Data Contracts

### Repository Layout

```text
BASTION-X/
├── docker-compose.yml
├── backend/
│   ├── core/
│   │   ├── config.py
│   │   └── invariants.py
│   ├── db/
│   │   ├── postgres.py
│   │   ├── models.py
│   │   ├── neo4j_ephemeral.py
│   │   └── migrations/
│   ├── mitre/
│   │   ├── importer.py
│   │   ├── aegis-mapping.json
│   │   └── data/
│   │       └── enterprise-attack.json
│   ├── detection/
│   │   ├── event_normalizer.py
│   │   ├── correlation_engine.py
│   │   └── detectors/
│   │       └── brute_force_detector.py
│   ├── orchestrator/
│   │   ├── ddps_validator.py
│   │   └── defense_orchestrator.py
│   └── api/
│       ├── mitre.py
│       └── simulations.py
└── simulation/
    ├── runner.py
    ├── scenario_registry.py
    ├── limits.py
    └── scenarios/
        ├── brute_force.py
        ├── bounded_http_load.py
        ├── container_discovery.py
        ├── service_discovery.py
        └── synthetic_session_replay.py

```

### Local Project Mapping JSON

Store AEGIS-specific scenario, detector, and defense module mappings separately from the official MITRE STIX bundle:

```json
{
  "T1110": {
    "priority_tier": "P0",
    "scenario_id": "brute_force",
    "detector_id": "failed_login_rate",
    "defense_modules": ["identity_guard", "rate_limiter"],
    "simulation_mode": "safe_local",
    "implementation_status": "scenario_implemented"
  },
  "T1498": {
    "priority_tier": "P0",
    "scenario_id": "bounded_http_load",
    "detector_id": "traffic_rate_anomaly",
    "defense_modules": ["traffic_shield", "rate_limiter"],
    "simulation_mode": "safe_local",
    "implementation_status": "planned"
  },
  "T1613": {
    "priority_tier": "P0",
    "scenario_id": "container_discovery",
    "detector_id": "unexpected_container_inventory_access",
    "defense_modules": ["network_segmentation"],
    "simulation_mode": "safe_local",
    "implementation_status": "planned"
  },
  "T1046": {
    "priority_tier": "P1",
    "scenario_id": "service_discovery",
    "detector_id": "unexpected_service_probe",
    "defense_modules": ["network_segmentation"],
    "simulation_mode": "safe_local",
    "implementation_status": "planned"
  },
  "T1550": {
    "priority_tier": "P1",
    "scenario_id": "synthetic_session_replay",
    "detector_id": "invalid_or_replayed_test_token",
    "defense_modules": ["session_guardian"],
    "simulation_mode": "synthetic_only",
    "implementation_status": "planned"
  }
}

```

### MITRE STIX Importer to PostgreSQL

```python
import hashlib
import json
from pathlib import Path
from sqlalchemy import text
from backend.db.postgres import SessionLocal

BASE_DIR = Path(__file__).parent
STIX_FILE = BASE_DIR / "data" / "enterprise-attack.json"
MAPPING_FILE = BASE_DIR / "aegis-mapping.json"
ATTACK_URL = "https://attack.mitre.org/techniques/{}/"


def compute_sha256(filepath: Path) -> str:
    digest = hashlib.sha256()
    with filepath.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def external_attack_id(obj: dict) -> str | None:
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id")
    return None


def import_container_techniques(version_id: str = "attack-stix-v16.1") -> list[dict]:
    if not STIX_FILE.exists():
        raise FileNotFoundError(f"Missing ATT&CK dataset: {STIX_FILE}")

    stix_hash = compute_sha256(STIX_FILE)
    bundle = json.loads(STIX_FILE.read_text(encoding="utf-8"))
    aegis_map = (
        json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
        if MAPPING_FILE.exists()
        else {}
    )

    records = []
    for obj in bundle.get("objects", []):
        if obj.get("type") != "attack-pattern":
            continue
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue
        platforms = obj.get("x_mitre_platforms", [])
        if "Containers" not in platforms:
            continue

        tech_id = external_attack_id(obj)
        if not tech_id:
            continue

        is_sub = obj.get("x_mitre_is_subtechnique", False)
        parent_id = tech_id.split(".")[0] if is_sub and "." in tech_id else None
        tactics = [
            phase.get("phase_name")
            for phase in obj.get("kill_chain_phases", [])
            if phase.get("kill_chain_name") == "mitre-attack"
        ]

        records.append({
            "technique_id": tech_id,
            "parent_technique_id": parent_id,
            "name": obj.get("name"),
            "description": obj.get("description", ""),
            "tactics": json.dumps(tactics),
            "platforms": json.dumps(platforms),
            "is_subtechnique": is_sub,
            "source_modified": obj.get("modified"),
            "source_version": version_id,
            "mitre_url": ATTACK_URL.format(tech_id.replace(".", "/")),
        })

    records.sort(key=lambda item: (item["is_subtechnique"], item["technique_id"]))

    with SessionLocal() as db:
        db.execute(
            text("""
                INSERT INTO mitre_catalog_versions
                    (version_id, stix_sha256, source_url, git_commit_tag, technique_count)
                VALUES (:v, :h, :u, :t, :c)
                ON CONFLICT (version_id) DO NOTHING
            """),
            {
                "v": version_id,
                "h": stix_hash,
                "u": "https://github.com/mitre-attack/attack-stix-data",
                "t": version_id,
                "c": len(records),
            },
        )

        for rec in records:
            db.execute(
                text("""
                    INSERT INTO mitre_techniques (
                        technique_id, parent_technique_id, name, description,
                        tactics, platforms, is_subtechnique, source_modified,
                        source_version, mitre_url
                    ) VALUES (
                        :technique_id, :parent_technique_id, :name, :description,
                        CAST(:tactics AS JSONB), CAST(:platforms AS JSONB),
                        :is_subtechnique, :source_modified, :source_version, :mitre_url
                    )
                    ON CONFLICT (technique_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        tactics = EXCLUDED.tactics,
                        platforms = EXCLUDED.platforms,
                        source_modified = EXCLUDED.source_modified,
                        source_version = EXCLUDED.source_version
                """),
                rec,
            )

            cfg = aegis_map.get(rec["technique_id"], {})
            db.execute(
                text("""
                    INSERT INTO mitre_mappings (
                        technique_id, priority_tier, scenario_id, detector_id,
                        defense_modules, simulation_mode, implementation_status
                    ) VALUES (
                        :tid, :prio, :scen, :det, CAST(:mods AS JSONB), :mode, :status
                    )
                    ON CONFLICT (technique_id) DO UPDATE SET
                        priority_tier = EXCLUDED.priority_tier,
                        scenario_id = EXCLUDED.scenario_id,
                        detector_id = EXCLUDED.detector_id,
                        defense_modules = EXCLUDED.defense_modules,
                        simulation_mode = EXCLUDED.simulation_mode
                """),
                {
                    "tid": rec["technique_id"],
                    "prio": cfg.get("priority_tier", "P2"),
                    "scen": cfg.get("scenario_id"),
                    "det": cfg.get("detector_id"),
                    "mods": json.dumps(cfg.get("defense_modules", [])),
                    "mode": cfg.get("simulation_mode", "safe_local"),
                    "status": cfg.get("implementation_status", "catalog_imported"),
                },
            )
        db.commit()

    return records

```

### Ephemeral Neo4j Context Manager

```python
from contextlib import asynccontextmanager
from neo4j import AsyncGraphDatabase


class EphemeralGraphManager:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def hydrate_environment(
        self, run_id: str, env_id: str, topology_template: dict
    ) -> None:
        async with self.driver.session() as session:
            await session.run(
                """
                UNWIND $nodes AS node
                MERGE (c:ContainerNode {
                    run_id: $run_id, environment_id: $env_id, node_id: node.node_id
                })
                SET c.name = node.name,
                    c.role = node.role,
                    c.zone = node.zone,
                    c.status = 'healthy'
                """,
                run_id=run_id,
                env_id=env_id,
                nodes=topology_template.get("nodes", []),
            )
            await session.run(
                """
                UNWIND $edges AS edge
                MATCH (s:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: edge.source})
                MATCH (d:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: edge.target})
                MERGE (s)-[r:ALLOWS_TRAFFIC_TO {run_id: $run_id}]->(d)
                SET r.port = edge.port,
                    r.rate_limit_rps = edge.rate_limit_rps
                """,
                run_id=run_id,
                env_id=env_id,
                edges=topology_template.get("edges", []),
            )

    async def snapshot_and_teardown(self, run_id: str) -> dict:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (n:ContainerNode {run_id: $run_id})
                OPTIONAL MATCH (n)-[r]->(m:ContainerNode {run_id: $run_id})
                RETURN collect(DISTINCT properties(n)) AS nodes,
                       collect(DISTINCT {
                           source: n.node_id,
                           type: type(r),
                           target: m.node_id,
                           props: properties(r)
                       }) AS edges
                """,
                run_id=run_id,
            )
            record = await result.single()
            snapshot = {
                "nodes": record["nodes"] if record else [],
                "edges": record["edges"] if record else [],
            }
            await session.run(
                "MATCH (n {run_id: $run_id}) DETACH DELETE n",
                run_id=run_id,
            )
            return snapshot

    @asynccontextmanager
    async def simulation_graph_scope(
        self, run_id: str, env_id: str, topology_template: dict
    ):
        await self.hydrate_environment(run_id, env_id, topology_template)
        try:
            yield self
        finally:
            await self.snapshot_and_teardown(run_id)

```

### Normalized Observation and Gemma 4 JSON Payloads

```json
{
  "normalized_observation": {
    "event_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "run_id": "3f39a1c0-82d2-46c9-b044-04f3f9527111",
    "correlation_id": "c81d4e2e-bcf2-11e6-869b-7df92533d2db",
    "observed_at": "2026-10-31T10:00:00Z",
    "source": "target-app",
    "event_type": "authentication_failure",
    "target_service": "auth-service",
    "source_identity": "lab-client-01",
    "severity": "medium",
    "metadata": {
      "test_account": "lab-user",
      "result": "failed"
    }
  },
  "gemma_structured_recommendation": {
    "incident_summary": "Repeated failed logins were observed against the lab login endpoint.",
    "technique_assessment": {
      "technique_id": "T1110",
      "confidence": 0.94
    },
    "recommended_modules": ["identity_guard", "rate_limiter"],
    "recommended_actions": [
      {
        "module": "rate_limiter",
        "action": "tighten_login_rate_limit",
        "reason": "Failed-login rate exceeded the configured lab threshold."
      }
    ],
    "requires_human_approval": false
  }
}

```

## 6. FastAPI Endpoints and Phased Execution Plan

| HTTP Method | Endpoint Path | Primary Purpose |
| --- | --- | --- |
| **GET** | /api/mitre/techniques | List imported techniques by tactic or status |
| **GET** | /api/mitre/techniques/{id} | Fetch technique metadata and AEGIS mapping |
| **GET** | /api/mitre/coverage | Return implementation and test coverage |
| **POST** | /api/mitre/import | Import validated STIX snapshot to PostgreSQL |
| **POST** | /api/simulations/start | Hydrate Neo4j and launch safe scenario |
| **POST** | /api/simulations/{id}/stop | Stop scenario and trigger Neo4j teardown |
| **GET** | /api/simulations/{id}/results | Fetch observations, detections, and metrics |

All simulation control routes validate against an allowlist of registered scenario IDs and never accept arbitrary shell commands or raw Docker arguments.

### Five-Phase Execution Plan

1. **Infrastructure Spin-Up:** Deploy PostgreSQL 16 with persistent volume storage and Neo4j 5 configured with ephemeral memory-backed storage in Docker Compose.
2. **Schema & STIX Seeding:** Run Alembic migrations to create all 18 PostgreSQL tables, seed ENV-A through ENV-D, and run the MITRE importer on the pinned STIX snapshot.
3. **Vertical Slice (T1110):** Build the complete end-to-end pipeline for T1110 Brute Force: safe login burst, normalized observations, independent detection, DDPS validation, rate-limiter execution, Neo4j edge update, and Gemma 4 explanation.
4. **Shared PPO & DDPS Testing:** Connect the four virtual environments to Stable-Baselines3 PPO and verify that DDPS blocks and logs synthetic security invariant violations (such as disabling authentication).
5. **Catalog Expansion & Benchmarking:** Add T1498, T1613, T1046, and T1550 scenarios and run paired Static (ENV-A) versus Adaptive (ENV-B) trials to populate the evaluation results table.

<ADDITIONAL_METADATA>
The current local time is: 2026-10-31T13:57:12+05:30.
</ADDITIONAL_METADATA>
