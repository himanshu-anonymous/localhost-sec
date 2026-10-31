# AEGIS REST API Specification (v1)

Versioned endpoints exposed under `/api/v1/`:

## 1. Health & Readiness
- `GET /api/v1/health`: Overall health and current defense state machine status.
- `GET /api/v1/health/dependencies`: Component-by-component readiness report (application, database, gateway, policy_agent, telemetry_collector, gemma_service).

## 2. Telemetry & Detections
- `GET /api/v1/events`: Query normalized security events with pagination, source, and IP filters.
- `GET /api/v1/events/{id}`: Retrieve single normalized security event.
- `POST /api/v1/events/ingest`: Ingest raw security events from sensors, normalizes and routes to detector.
- `GET /api/v1/detections`: List independent detection records.
- `GET /api/v1/detections/{id}`: Detection record detail with inferred techniques and evidence event IDs.

## 3. Incidents & Gemma Analysis
- `GET /api/v1/incidents`: List correlated security incidents (`NEW`, `INVESTIGATING`, `MITIGATING`, `RESOLVED`).
- `GET /api/v1/incidents/{id}`: Detailed incident record.
- `POST /api/v1/incidents/{id}/analyze`: Triggers Gemma structured incident assessment and recommended defense modules/actions.
- `POST /api/v1/incidents/{id}/mitigate`: Executes approved recommendation through the policy engine and applies gateway block.
- `POST /api/v1/incidents/{id}/resolve`: Resolves the incident.

## 4. Defense Orchestration
- `GET /api/v1/defense/modules`: List available defense modules (`gateway_acl`, `rate_limiter`, etc.).
- `GET /api/v1/defense/state`: Current defense state machine state (`NORMAL`, `SUSPECTED_ATTACK`, `CONTAINED`, etc.).
- `GET /api/v1/defense/actions`: Audit history of executed defense actions.
- `POST /api/v1/defense/emergency-stop`: Immediate emergency stop, revoking temporary blocks and freezing policies.
- `POST /api/v1/defense/rollback`: Reverts temporary gateway blocks to safe baseline.

## 5. Metrics & Comparison
- `GET /api/v1/metrics/overview`: High-level operations telemetry counter.
- `GET /api/v1/metrics/compare?scenario_id=brute_force`: Empirical comparison between Static and Adaptive defense runs.

