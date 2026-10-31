# AEGIS Database Architecture

## 1. Relational PostgreSQL Schema (18 Tables across 5 Domains)

The database schema encapsulates operational and analytical data in PostgreSQL 16:

1. **Identity & Environments**:
   - `users`: Operator accounts.
   - `roles`: Role definitions (`admin`, `operator`, `analyst`, `auditor`).
   - `user_roles`: Many-to-many user-role association.
   - `environments`: Virtual environments (`ENV-A` baseline, `ENV-B` adaptive, `ENV-C` hardened, `ENV-D` experimental).

2. **MITRE ATT&CK Catalog**:
   - `mitre_catalog_versions`: Version snapshots of official STIX datasets.
   - `mitre_techniques`: Imported ATT&CK Container techniques.
   - `mitre_mappings`: Project mappings binding techniques to scenario IDs, detectors, and defense modules.

3. **Simulations & Telemetry**:
   - `attack_scenarios`: Registered attack scenarios (`brute_force`, `bounded_http_load`, etc.).
   - `simulation_runs`: Executed trial runs with ground truth technique references and environment modes.
   - `telemetry_metrics`: Node resource pressure and latency time-series.
   - `security_observations`: Normalized security events and packet telemetry.
   - `technique_detections`: Independent detection output records.

4. **Defense Actions & Auditing**:
   - `training_runs`: Shared PPO training episodes.
   - `rl_actions`: Policy action proposals.
   - `action_approvals`: Invariant validation results.
   - `security_violations`: Audit log of actions rejected by $\Omega$ invariants.
   - `defense_actions`: Applied defense changes with rollback references.
   - `defence_policies`: Versioned policy configurations.

5. **AI Evaluation**:
   - `gemma_reports`: Structured incident reports and reasoning from Gemma.
   - `evaluation_results`: Quantitative resilience scorecards (`detection_time_ms`, `mitigation_time_ms`, `legitimate_success_rate`, `false_positive_rate`, `recovery_time_ms`).

