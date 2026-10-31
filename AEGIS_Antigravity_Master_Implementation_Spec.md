# AEGIS --- Complete System Implementation Specification

## Master Build Brief for Google Antigravity

**Document type:** Engineering specification and implementation prompt\
**Project:** AEGIS --- Adaptive Elastic Guard & Intelligent Security\
**Target environment:** Local development on Windows + Docker Desktop
(Linux containers)\
**Primary orchestration:** Docker Compose\
**Backend:** Python + FastAPI\
**Database:** PostgreSQL\
**AI layer:** Gemma only\
**MITRE framework:** MITRE ATT&CK Enterprise, with the already-imported
Containers-platform catalog\
**Core objective:** Demonstrate adaptive, modular network defense
against repeatable, controlled cyberattack simulations, and compare
adaptive defense with static defense.

------------------------------------------------------------------------

# 0. Instructions to Antigravity --- Read Before Coding

You are the lead architect and implementation engineer for AEGIS. Build
a complete, runnable, locally hosted cybersecurity simulation and
adaptive-defense platform from the existing repository.

This document is the source of truth for the implementation. Do not
merely generate a mock dashboard, static architecture, disconnected code
samples, or placeholder API responses. Build an integrated system whose
components communicate through working APIs, Docker networks, persistent
PostgreSQL storage, and repeatable tests.

## 0.1 Existing project context

The project already has these decisions and assets:

1.  The project is named **AEGIS**.
2.  MITRE ATT&CK data has already been added to the project under
    `backend/mitre/`. Preserve and inspect the existing implementation
    before changing it.
3.  One team member is separately implementing PostgreSQL. Inspect the
    current database work and integrate with it where possible. Do not
    overwrite an existing schema or migration history without reviewing
    it.
4.  **Gemma is the only LLM intended to be integrated into AEGIS. Do not
    add Pi.dev or another agent framework/model.**
5.  The system uses Docker-based attack and protected-target
    environments.
6.  The system must support both **static-defense** and
    **adaptive-defense** experiment modes.
7.  Access model is **local only** for the initial version.
8.  Defense behavior is adaptive, but changes must be
    deterministic-policy-validated and auditable.
9.  The frontend must visualize attack activity, detected incidents,
    defense state, module transitions, and experiment comparisons.

## 0.2 First actions --- repository reconnaissance

Before generating or editing files:

-   Inspect the entire repository tree.
-   Identify the current backend framework, frontend framework, entry
    points, environment configuration, database implementation, MITRE
    importer/catalog, simulation code, Docker files, and existing tests.
-   Read existing `README.md`, `MITRE.md`, database migrations, and
    Compose files.
-   Identify code that is already functional and preserve it.
-   Do not create duplicate FastAPI applications, duplicate database
    models, duplicate MITRE catalogs, or competing Docker Compose
    stacks.
-   Produce a concise implementation plan and a list of files to
    create/change.
-   Then implement in small, verifiable milestones.
-   If a required detail is missing, choose a secure, conventional
    default and document it. Ask only if proceeding would risk
    destructive changes or make integration impossible.

Do not assume the previous prototype archive is already installed or
working. Validate all current files and fix errors you find.

## 0.3 Non-negotiable implementation rules

-   The system must start locally through Docker Compose.
-   Use health checks and dependency readiness; do not rely only on
    `depends_on` startup ordering.
-   Never expose the attack environment, target services, policy API,
    PostgreSQL, Redis, or monitoring interfaces to the host unless
    explicitly required for local development. Bind any required host
    ports to `127.0.0.1`.
-   Do not mount `/var/run/docker.sock` into the attacker, target, AI,
    or ordinary backend containers.
-   Do not run containers in privileged mode.
-   Do not give the attack simulator host networking.
-   Do not allow arbitrary shell commands, arbitrary Docker arguments,
    arbitrary firewall rules, or arbitrary HAProxy commands through
    APIs.
-   Use allowlisted scenario IDs and allowlisted defense actions.
-   Treat all logs, packets, user inputs, and LLM output as untrusted.
-   Gemma must never directly execute actions. Gemma may analyze and
    recommend; deterministic policy code authorizes and executes.
-   Detection must not use simulator ground truth as an input to its
    decision.
-   Every defense action must have an audit record and an outcome.
-   Every simulation must have a hard time limit, resource limit,
    cleanup procedure, and emergency stop.
-   Never simulate attacks against public IPs, third-party systems,
    college networks, or real user accounts. Only use the local isolated
    lab.
-   Do not build real malware, persistence, credential theft,
    destructive payloads, real container escapes, or uncontrolled
    denial-of-service tools. Use benign, bounded simulations and
    synthetic events.

------------------------------------------------------------------------

# 1. Product Goal and Demonstration

AEGIS is a modular adaptive cybersecurity defense platform.

It creates an isolated local lab containing test services. Controlled
attack scenarios generate observable activity against those services. A
telemetry pipeline collects events, a detection engine identifies
suspicious behavior, MITRE ATT&CK provides standardized technique
context, Gemma explains incidents and recommends defense modules, and a
deterministic policy engine validates proposed responses.

The defense orchestrator applies approved configuration changes to the
lab gateway and other defense modules. A dashboard displays the full
event timeline and compares static and adaptive defense results.

## 1.1 Primary demonstration

The main demonstration must show:

1.  A user selects an ATT&CK technique/scenario.
2.  AEGIS starts a controlled simulation in Docker.
3.  Traffic reaches a protected target only through the security
    gateway.
4.  Telemetry is collected by network and application sensors.
5.  The detection engine independently detects suspicious behavior.
6.  An incident is created and associated with one or more ATT&CK
    techniques.
7.  Gemma receives a sanitized incident context and returns structured
    recommendations.
8.  The policy engine validates the recommendation against hard rules.
9.  The orchestrator activates or adjusts the required defense modules.
10. The system verifies whether the response worked.
11. All events and state changes are saved in PostgreSQL.
12. The dashboard displays attack, detection, recommendation, action,
    mitigation, and recovery timelines.
13. The same scenario can be repeated in static mode.
14. The dashboard compares static and adaptive measurements.

## 1.2 Success criteria

The MVP is successful only when at least one scenario works end-to-end
in both static and adaptive modes, all events are persisted, the defense
action changes the actual lab gateway behavior, and the dashboard
displays measured results.

A dashboard populated with fabricated data does not count as a working
implementation.

------------------------------------------------------------------------

# 2. System Architecture

## 2.1 Logical architecture

``` text
                         LOCAL USER
                             |
                             v
                    React / Web Dashboard
                             |
                         HTTPS / API
                             |
                             v
                    FastAPI Application
                             |
          +------------------+-------------------+
          |                  |                   |
          v                  v                   v
    Simulation API      Incident API         MITRE API
          |                  |                   |
          v                  v                   v
    Scenario Runner    Detection Engine     MITRE Catalog
          |                  |                   |
          v                  v                   |
    Docker Lab         Correlation Engine         |
          |                  |                   |
          +------------------+-------------------+
                             |
                             v
                       Incident Manager
                             |
                 +-----------+-----------+
                 |                       |
                 v                       v
             Gemma AI              Policy Engine
          analysis/advice        deterministic rules
                 |                       |
                 +-----------+-----------+
                             |
                             v
                    Defense Orchestrator
                             |
              +--------------+---------------+
              |              |               |
              v              v               v
          Gateway ACL    Rate Limiter    Session/Identity
              |              |               |
              +--------------+---------------+
                             |
                             v
                     Verification Engine
                             |
                             v
                       PostgreSQL
                             |
                             v
                        Dashboard
```

## 2.2 Runtime Docker topology

Create separate Docker networks with non-overlapping private subnets.
Confirm these subnets do not overlap with existing Docker networks,
VPNs, or the host LAN. Make subnet values configurable through `.env`.

Recommended logical networks:

  ------------------------------------------------------------------------------
  Network                 Example subnet     Attached services Purpose
  ----------------------- ------------------ ----------------- -----------------
  `aegis_frontend`        `172.31.1.0/24`    frontend, backend UI/API
                                                               communication

  `aegis_control`         `172.31.2.0/24`    backend, policy   Control plane
                                             agent, database   

  `aegis_access`          `172.31.10.0/24`   attack client,    Lab ingress
                                             gateway, sensor   

  `aegis_target`          `172.31.20.0/24`   gateway, target   Protected target
                                             services, sensor  network
                                             where needed      

  `aegis_observability`   `172.31.3.0/24`    telemetry         Logs and metrics
                                             collector,        
                                             monitoring        
                                             services          
  ------------------------------------------------------------------------------

These are examples, not mandatory hard-coded values. The generated
configuration must detect and document overlap risks.

### Network separation rules

-   The attacker container joins only `aegis_access`.
-   Protected targets join only `aegis_target`.
-   The gateway joins both `aegis_access` and `aegis_target`.
-   The backend joins the frontend and control networks.
-   The policy agent joins the control network and only the minimum
    runtime-control channel required.
-   PostgreSQL joins the control network and is not published to the
    host by default.
-   The attacker must not directly route to the target network.
-   The AI service must not join the attack network.
-   The attack simulator must not receive Docker daemon access.
-   Monitoring must observe lab traffic without becoming an uncontrolled
    forwarding path.

Use `internal: true` on lab networks where compatible with the required
services. If an image requires package downloads, use a separate build
stage or temporary controlled egress; do not permanently give the attack
network internet access.

## 2.3 Important distinction: gateway vs transparent network firewall

The initial gateway implementation may use HAProxy for HTTP/HTTPS
traffic. HAProxy is an application proxy; it does not transparently
protect every arbitrary TCP/UDP protocol.

Implement the MVP honestly:

-   HTTPS target traffic is forced through the HAProxy gateway.
-   Dynamic source blocking is enforced at the gateway for requests that
    traverse it.
-   Suricata observes traffic on the appropriate interfaces.
-   Add protocol-specific TCP proxy frontends for other services only
    when needed.
-   Do not claim that an HTTP reverse proxy is a complete L3/L4
    firewall.
-   If transparent L3/L4 filtering is required later, implement a
    separately reviewed router/firewall component using Linux namespaces
    and nftables, with explicit routing, forwarding, and return-path
    tests.

------------------------------------------------------------------------

# 3. Technology Stack

Use the existing repository stack when it is already established. The
following is the default target stack.

  -----------------------------------------------------------------------
  Layer                   Technology              Responsibility
  ----------------------- ----------------------- -----------------------
  Frontend                Existing React/Vite     Dashboard
                          app, if present         

  Backend                 Python 3.12 + FastAPI   APIs and orchestration

  Database                PostgreSQL 16+          Persistent state and
                                                  audit

  ORM/migrations          SQLAlchemy 2 + Alembic  Models and schema
                                                  evolution

  Validation              Pydantic 2              API and model schemas

  Cache/queue             Redis (optional for     Background jobs and
                          MVP)                    transient state

  AI                      Gemma                   Incident analysis and
                                                  recommendations

  AI runtime              Existing selected Gemma Inference
                          provider/runtime        

  Gateway                 HAProxy                 mTLS and controlled
                                                  traffic proxy

  Network IDS             Suricata                Network event detection

  Network metadata        Zeek (optional later)   Protocol metadata

  Lab services            Nginx and selected      Safe targets
                          protocol services       

  Container orchestration Docker Compose v2       Local environment

  Metrics                 Prometheus (optional)   System metrics

  Charts                  Existing frontend chart Visualization
                          library                 
  -----------------------------------------------------------------------

Do not add a new framework merely because it appears in this
specification. Prefer the existing project dependencies if they can
satisfy the requirements.

------------------------------------------------------------------------

# 4. Repository Structure

Adapt this to the existing project rather than blindly replacing it.

``` text
AEGIS/
├── README.md
├── .env.example
├── compose.yaml
├── compose.dev.yaml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DATABASE.md
│   ├── MITRE.md
│   ├── SECURITY.md
│   ├── SIMULATION.md
│   └── OPERATIONS.md
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   ├── security.py
│   │   │   └── lifecycle.py
│   │   ├── api/
│   │   │   ├── health.py
│   │   │   ├── simulations.py
│   │   │   ├── incidents.py
│   │   │   ├── detections.py
│   │   │   ├── defense.py
│   │   │   ├── metrics.py
│   │   │   └── mitre.py
│   │   ├── database/
│   │   │   ├── session.py
│   │   │   ├── base.py
│   │   │   └── models/
│   │   ├── schemas/
│   │   ├── mitre/
│   │   │   ├── importer.py
│   │   │   ├── catalog.py
│   │   │   ├── mapper.py
│   │   │   └── data/
│   │   │       └── [existing official ATT&CK data]
│   │   ├── simulation/
│   │   │   ├── registry.py
│   │   │   ├── runner.py
│   │   │   ├── limits.py
│   │   │   └── scenarios/
│   │   ├── telemetry/
│   │   │   ├── schemas.py
│   │   │   ├── collector.py
│   │   │   ├── normalizer.py
│   │   │   └── adapters/
│   │   ├── detection/
│   │   │   ├── engine.py
│   │   │   ├── correlation.py
│   │   │   └── rules/
│   │   ├── incidents/
│   │   │   ├── manager.py
│   │   │   └── lifecycle.py
│   │   ├── ai/
│   │   │   ├── gemma_client.py
│   │   │   ├── prompts.py
│   │   │   ├── schemas.py
│   │   │   └── analyzer.py
│   │   ├── policy/
│   │   │   ├── engine.py
│   │   │   ├── rules.py
│   │   │   └── validation.py
│   │   ├── defense/
│   │   │   ├── orchestrator.py
│   │   │   ├── state_machine.py
│   │   │   ├── modules/
│   │   │   └── adapters/
│   │   └── evaluation/
│   │       ├── metrics.py
│   │       └── comparison.py
│   ├── tests/
│   ├── Dockerfile
│   └── alembic/
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── types/
│   └── Dockerfile
│
├── infrastructure/
│   ├── gateway/
│   │   ├── haproxy.cfg
│   │   └── acl/
│   ├── suricata/
│   │   ├── suricata.yaml
│   │   └── rules/
│   ├── policy-agent/
│   ├── lab/
│   │   ├── attacker/
│   │   ├── targets/
│   │   └── configs/
│   └── certificates/
│       └── README.md
│
├── scripts/
│   ├── dev-up.ps1
│   ├── dev-down.ps1
│   ├── generate-certs.ps1
│   ├── seed-db.py
│   └── verify-stack.ps1
│
└── tests/
    ├── integration/
    ├── security/
    └── end_to_end/
```

Keep the official MITRE data where it currently exists if moving it
would break working imports. Avoid duplicate copies of large STIX files.

------------------------------------------------------------------------

# 5. Docker Compose Requirements

Create a primary Compose file that starts the complete local system. Use
separate profiles or Compose override files for optional services.

## 5.1 Required services

  Service          Required                    Purpose
  ---------------- --------------------------- --------------------------------
  `frontend`       Yes                         Dashboard
  `backend`        Yes                         FastAPI
  `postgres`       Yes                         Persistent database
  `gateway`        Yes                         HAProxy secure access
  `policy-agent`   Yes                         Restricted adaptive policy API
  `attacker`       Yes                         Controlled test client
  `target-web`     Yes                         Protected web target
  `suricata`       Yes                         Network monitoring
  `gemma`          Depends on chosen runtime   AI analysis
  `redis`          Optional                    Background tasks/cache
  `zeek`           Optional                    Deeper network metadata

## 5.2 Container hardening

For every service:

-   Use a non-root user wherever supported.
-   Drop Linux capabilities by default; add only those specifically
    needed.
-   Set `read_only: true` where compatible.
-   Use `tmpfs` for temporary writable paths where possible.
-   Set CPU and memory limits.
-   Set `pids_limit`.
-   Use `no-new-privileges:true`.
-   Avoid `privileged: true`.
-   Avoid mounting the Docker socket.
-   Pin images to tested versions or digests for reproducibility.
-   Use named volumes for persistent data.
-   Use health checks.
-   Do not publish ports unless required for local UI access.
-   Bind published development ports to `127.0.0.1`.
-   Use Docker secrets or protected environment files for credentials.
-   Never bake credentials into images.

## 5.3 Host port plan

Suggested local-only published ports:

  Service          Host binding       Notes
  ---------------- ------------------ --------------------------------
  Frontend         `127.0.0.1:3000`   Dashboard
  Backend          `127.0.0.1:8000`   API/docs for development
  Gateway          `127.0.0.1:8443`   Local mTLS test endpoint
  PostgreSQL       Not published      Access through Compose network
  Policy agent     Not published      Backend-only access
  Suricata         Not published      Logs via volume/collector
  Attack targets   Not published      Reach through gateway only

Production-like local demonstration may route frontend API calls through
a single local reverse proxy. Do not expose internal service ports
unnecessarily.

## 5.4 Compose quality

-   `docker compose config` must succeed.
-   `docker compose build` must complete.
-   `docker compose up -d` must reach healthy states.
-   `docker compose down` must stop all services cleanly.
-   Persistent database data must survive normal restarts.
-   `docker compose down -v` must be documented as destructive because
    it removes volumes.
-   Provide `.env.example`, never commit real `.env`.
-   Provide PowerShell scripts for Windows users.

------------------------------------------------------------------------

# 6. Secure Network Access Stack

## 6.1 Initial MVP design

Implement a controlled application gateway:

-   HAProxy accepts HTTPS traffic.
-   TLS 1.3 minimum.
-   Require client certificate authentication (mTLS) for protected
    endpoints.
-   The gateway is the only service attached to both access and target
    networks.
-   The attacker container joins only the access network.
-   Protected targets join only the target network.
-   The policy agent updates a restricted HAProxy ACL through a local
    runtime socket.
-   Suricata monitors the relevant gateway-facing interface.
-   The backend can call the policy agent only over the internal control
    network.

Do not describe this as a complete transparent firewall. It protects
traffic that passes through the gateway.

## 6.2 Certificates

Generate a local development CA and distinct certificates for:

-   Gateway server.
-   AEGIS backend client.
-   Attack-lab client.
-   Optional monitoring collector.

Requirements:

-   SANs must match the hostnames used by clients.
-   Server certificate must have serverAuth EKU.
-   Client certificates must have clientAuth EKU.
-   Private keys must not be committed.
-   Certificates must be regenerable.
-   Provide a clear rotation/revocation procedure.
-   The backend must trust only the configured lab CA.
-   Do not disable TLS verification as a permanent workaround.

## 6.3 Adaptive policy agent

Create a restricted service exposing only explicit operations such as:

-   Read current policy state.
-   Block a lab source IP.
-   Unblock a lab source IP.
-   Read gateway health.
-   Read policy version/status.

Validation:

-   Authenticate every request.
-   Accept only valid IP addresses from the configured lab subnet.
-   Reject loopback, multicast, network/broadcast, host, and
    out-of-scope addresses.
-   Do not accept arbitrary HAProxy commands.
-   Do not accept shell strings or raw firewall rules.
-   Persist desired state.
-   Apply changes to the live gateway.
-   Verify the applied state.
-   Roll back persistence if the runtime update fails.
-   Log actor, incident, reason, policy version, timestamp, result, and
    rollback information.
-   Rate-limit the policy API.
-   Never publish the policy API to the host.

## 6.4 Future L3/L4 firewall extension

Do not implement a fragile half-router in the MVP. Document the
extension point.

For a later transparent network-defense layer:

-   Use a dedicated router/firewall container or Linux network
    namespace.
-   Use nftables for explicit forward-chain policies.
-   Configure IP forwarding intentionally.
-   Ensure both forward and return paths traverse the enforcement point.
-   Add tests proving targets cannot be reached directly.
-   Test TCP and UDP separately.
-   Add explicit rollback and out-of-band stop.
-   Never expose a generic endpoint that accepts arbitrary nftables
    commands.

------------------------------------------------------------------------

# 7. MITRE ATT&CK Integration

## 7.1 Preserve existing integration

Inspect the existing `backend/mitre/` implementation. Reuse it. Do not
re-download or duplicate the dataset if it is already present and valid.

The catalog should expose:

-   Technique ID.
-   Technique name.
-   Description.
-   Tactic relationships.
-   Platforms.
-   Sub-technique flag.
-   Parent technique ID.
-   Official MITRE URL.
-   Dataset release/version.
-   Source modified timestamp.
-   AEGIS scenario mapping.
-   AEGIS implementation status.

Keep official MITRE metadata separate from AEGIS-owned mappings.

## 7.2 Data import behavior

-   Import from a pinned Enterprise ATT&CK STIX snapshot.
-   Filter `Containers` platform records for the current lab catalog.
-   Include applicable sub-techniques.
-   Exclude revoked/deprecated records from active selectable lists
    while retaining historical references where needed.
-   Store release/version and source hash.
-   Make imports repeatable and idempotent.
-   Do not delete experiment history when the catalog is updated.
-   Add tests for duplicate IDs and missing external references.

## 7.3 Initial technique scenarios

Prioritize safe, measurable scenarios:

  -----------------------------------------------------------------------
  Technique               Safe simulation         Detection/control
  ----------------------- ----------------------- -----------------------
  T1110 --- Brute Force   Fixed small number of   Auth anomaly, identity
                          failed logins to lab    guard, rate limiter
                          app                     

  T1498 --- Network       Strictly bounded        Request-rate anomaly,
  Denial of Service       request-load test       gateway limit
                          against lab target      

  T1613 --- Container and Read-only lab inventory Inventory access audit
  Resource Discovery      query                   

  T1046 --- Network       Small allowlisted       Probe pattern detection
  Service Discovery       service checks in lab   

  T1550 --- Use Alternate Synthetic               Session validation
  Authentication Material expired/replayed test   
                          token                   

  T1552 --- Unsecured     Dummy canary secret in  Secret scanner
  Credentials             a disposable fixture    

  T1610 --- Deploy        Benign deployment event Deployment audit/policy
  Container               in the lab              

  T1496 --- Resource      Short resource-limited  Resource monitor
  Hijacking               CPU/memory workload     
  -----------------------------------------------------------------------

Only implement scenarios that are relevant to the available target
services and telemetry. Do not claim full ATT&CK coverage just because
the catalog imported.

------------------------------------------------------------------------

# 8. Simulation Engine

## 8.1 Scenario registry

Every scenario must be registered in code and have:

-   `scenario_id`
-   Name and description
-   MITRE technique IDs
-   Allowed target service(s)
-   Required lab environment
-   Configuration schema
-   Hard maximum duration
-   Hard request/event rate
-   Resource ceilings
-   Cleanup function
-   Expected telemetry types
-   Ground-truth metadata

Never dynamically import modules or execute code from a user-supplied
scenario name.

## 8.2 Simulation lifecycle

``` text
CREATED
  |
  v
VALIDATING
  |
  v
READY
  |
  v
RUNNING
  |
  v
COMPLETED / FAILED / STOPPED / TIMED_OUT
  |
  v
CLEANUP
  |
  v
RESULTS_SAVED
```

A simulation must be stoppable by an operator. A watchdog must stop
scenarios that exceed duration or resource limits.

## 8.3 Static and adaptive modes

Every scenario supports two comparable modes:

### Static

-   Fixed baseline controls.
-   No automated defense reconfiguration during the trial.
-   Monitoring and event collection remain enabled.
-   Baseline security controls are not disabled in ways that expose the
    host.

### Adaptive

-   Same baseline controls.
-   Detection events can trigger policy evaluation.
-   Approved defense modules can change their configuration.
-   Each transition is audited.
-   The system verifies the effect of a change.

Do not change workload, target image, CPU allocation, request profile,
or scenario duration between static and adaptive trials unless the
experiment explicitly records the difference.

## 8.4 Initial scenarios

Implement in this order:

1.  `brute_force`: a small, fixed number of failed logins against the
    local application.
2.  `bounded_http_load`: a low-rate, short-duration request load against
    the local gateway target.
3.  `service_discovery`: a small allowlist of known lab endpoints.
4.  `synthetic_session_replay`: a synthetic token that is expired or
    marked as replayed.
5.  `container_inventory_read`: read-only inventory access against
    lab-owned metadata.

For each scenario: - Validate the target is a lab-owned service. -
Refuse arbitrary target IPs/domains. - Enforce hard-coded maximum
rates/duration. - Capture ground truth separately. - Use the normal
telemetry pipeline. - Clean up temporary data. - Persist the result.

------------------------------------------------------------------------

# 9. Telemetry and Event Normalization

## 9.1 Sources

Support these sources incrementally:

-   Target application logs.
-   HAProxy access logs.
-   HAProxy runtime policy events.
-   Suricata EVE JSON.
-   Docker/container health and resource metrics.
-   Authentication service events.
-   Simulation runner lifecycle events.

Do not treat simulation runner ground truth as detection evidence.

## 9.2 Canonical event schema

Use a normalized schema similar to:

``` json
{
  "event_id": "uuid",
  "occurred_at": "2026-10-31T10:00:00Z",
  "ingested_at": "2026-10-31T10:00:01Z",
  "source_type": "haproxy",
  "source_name": "aegis-gateway",
  "event_type": "http_request",
  "source_ip": "172.31.10.10",
  "source_port": 50122,
  "destination_ip": "172.31.20.10",
  "destination_port": 8080,
  "protocol": "HTTP",
  "severity": "info",
  "simulation_run_id": "uuid-or-null",
  "incident_id": null,
  "metadata": {
    "method": "GET",
    "path": "/",
    "status_code": 200
  }
}
```

Use UTC `TIMESTAMPTZ` in PostgreSQL. Validate and sanitize fields. Avoid
storing secrets, session cookies, passwords, private keys, or full
sensitive request bodies.

## 9.3 Ground truth separation

Simulation run stores intended technique:

``` json
{
  "ground_truth_technique_id": "T1110",
  "scenario_id": "brute_force"
}
```

Detection output independently stores inferred technique:

``` json
{
  "detected_technique_id": "T1110",
  "confidence": 0.91,
  "evidence_event_ids": ["..."]
}
```

The detection engine must not read the ground-truth field when deciding
what happened. Use it only after detection for evaluation.

------------------------------------------------------------------------

# 10. Detection Engine

Implement deterministic detectors first. Gemma is not the primary
detection mechanism.

## 10.1 MVP detectors

-   Failed-login threshold detector.
-   HTTP request-rate anomaly detector.
-   Repeated endpoint/service-probe detector.
-   Invalid/replayed synthetic session detector.
-   Monitoring-agent heartbeat-loss detector.

## 10.2 Detection record

Every detection must include:

-   Detector ID and version.
-   Timestamp.
-   Severity.
-   Confidence.
-   Inferred technique IDs.
-   Evidence event IDs.
-   Reason/explanation.
-   Affected service.
-   Source identity/IP where appropriate.
-   Simulation run association, if available.

## 10.3 False positives

Include benign baseline traffic and normal user requests in experiments.
Calculate false positives using defined time windows and known benign
test periods. Do not define every event from the attacker container as
malicious automatically.

------------------------------------------------------------------------

# 11. Incident Management

An incident groups related detections and events.

Lifecycle:

``` text
NEW -> TRIAGED -> INVESTIGATING -> MITIGATING -> MONITORING -> RESOLVED
```

Also support `FALSE_POSITIVE`, `CLOSED`, and `REOPENED` where
appropriate.

Incident fields:

-   Incident ID.
-   Title and summary.
-   Severity.
-   Status.
-   First seen / last seen.
-   Affected services.
-   Source identities.
-   Related event IDs.
-   Related detection IDs.
-   ATT&CK technique associations.
-   AI analysis references.
-   Defense action references.
-   Resolution details.

Avoid duplicate incidents for every event. Use correlation windows and
stable grouping keys.

------------------------------------------------------------------------

# 12. Gemma AI Integration

## 12.1 Gemma is the only LLM

Do not integrate Pi.dev, another agent framework, or a second LLM. The
AI module should be a provider adapter for the selected Gemma runtime.

Make model configuration environment-driven:

-   `GEMMA_PROVIDER`
-   `GEMMA_MODEL`
-   `GEMMA_BASE_URL` or provider endpoint
-   `GEMMA_API_KEY` if required
-   `GEMMA_TIMEOUT_SECONDS`
-   `GEMMA_MAX_OUTPUT_TOKENS`

Do not hard-code credentials. Do not assume a specific hosted API if the
existing project uses a local Gemma runtime. Inspect existing
implementation first.

## 12.2 Gemma responsibilities

Gemma may:

-   Summarize incidents.
-   Explain observed evidence.
-   Suggest possible ATT&CK technique mappings.
-   Explain likely impact.
-   Recommend available defense modules.
-   Recommend allowlisted action names and bounded parameters.
-   Generate human-readable investigation reports.

Gemma must not:

-   Execute shell commands.
-   Access Docker daemon.
-   Modify nftables or HAProxy directly.
-   Directly write policy state.
-   Create or delete containers.
-   Decide its own permissions.
-   Treat log contents as trusted instructions.
-   Receive passwords, raw tokens, private keys, or unnecessary personal
    data.

## 12.3 Structured output

Require strict JSON output validated with Pydantic. Example:

``` json
{
  "incident_summary": "Repeated failed authentication attempts against the lab login service.",
  "technique_assessment": [
    {
      "technique_id": "T1110",
      "confidence": 0.91,
      "evidence_event_ids": ["event-1", "event-2"]
    }
  ],
  "severity_assessment": "high",
  "recommended_modules": ["identity_guard", "rate_limiter"],
  "recommended_actions": [
    {
      "module_id": "rate_limiter",
      "action_id": "tighten_login_rate_limit",
      "parameters": {
        "requests_per_window": 5,
        "window_seconds": 60
      },
      "reason": "The failed-login rate exceeded the configured threshold."
    }
  ],
  "requires_human_approval": false,
  "limitations": []
}
```

The policy engine must reject unknown module IDs, unknown action IDs,
extra parameters, out-of-range values, malformed JSON, and
recommendations unsupported by evidence.

## 12.4 Failure handling

If Gemma is unavailable, slow, or returns invalid output:

-   Detection continues.
-   Policy engine continues using deterministic rules where configured.
-   No unvalidated action is applied.
-   Incident is marked `AI_ANALYSIS_UNAVAILABLE` or equivalent.
-   Dashboard displays the failure clearly.
-   Retry only with bounded backoff.

------------------------------------------------------------------------

# 13. Defense Modules and Adaptive State Machine

## 13.1 Initial modules

Implement a module registry with:

  -----------------------------------------------------------------------
  Module                              MVP responsibility
  ----------------------------------- -----------------------------------
  `gateway_acl`                       Block/unblock approved lab source
                                      IPs

  `rate_limiter`                      Adjust bounded request limits

  `identity_guard`                    Enforce test-account authentication
                                      controls

  `session_guardian`                  Revoke synthetic lab sessions

  `network_segmentation`              Enforce predefined lab service
                                      access profiles

  `monitoring_guard`                  Detect telemetry/monitor health
                                      loss

  `resource_guard`                    Enforce predefined container
                                      resource profiles
  -----------------------------------------------------------------------

Only `gateway_acl` and `rate_limiter` need actual runtime enforcement in
the first vertical slice. Other modules may be registered as `planned`
until their adapters are implemented. Never present a simulated module
state as a real enforcement action.

## 13.2 State machine

Implement explicit states:

-   `NORMAL`
-   `OBSERVING`
-   `SUSPECTED_ATTACK`
-   `CONFIRMED_ATTACK`
-   `MITIGATING`
-   `CONTAINED`
-   `RECOVERING`
-   `DEGRADED`
-   `EMERGENCY_STOP`

Transitions must have: - Trigger event. - Required
confidence/severity. - Policy rule. - Approved actions. - Timeout. -
Verification condition. - Rollback condition. - Audit entry.

Example:

``` text
NORMAL
  |
  | unusual failed-login rate
  v
OBSERVING
  |
  | deterministic threshold + evidence
  v
SUSPECTED_ATTACK
  |
  | policy confirms and approves
  v
CONFIRMED_ATTACK
  |
  | apply rate limit / source block
  v
MITIGATING
  |
  | gateway verifies enforcement
  v
CONTAINED
  |
  | cooldown + benign health checks
  v
RECOVERING
  |
  | baseline policy restored safely
  v
NORMAL
```

## 13.3 Defense invariants

-   Never disable authentication as an emergency response.
-   Never disable all rate limits during an attack.
-   Never block the backend, policy agent, gateway management channel,
    or emergency operator path.
-   Never apply a rule outside the lab subnet.
-   Never block an address based only on unvalidated LLM output.
-   Prefer narrow, temporary controls.
-   Every temporary action has an expiry/rollback plan.
-   Maintain a manual emergency stop.
-   Keep a protected management path independent from the data path.
-   On policy-agent failure, fail closed for new risky actions but
    preserve existing safe baseline policies.

------------------------------------------------------------------------

# 14. PostgreSQL Data Model

Inspect the teammate's existing database branch/files first. Integrate
with it instead of creating duplicate tables. Use SQLAlchemy models and
Alembic migrations if that is the current stack.

## 14.1 Required logical tables

### MITRE

-   `mitre_techniques`
-   `mitre_tactics`
-   `mitre_technique_tactics`
-   `mitre_mappings`

### Simulation

-   `simulation_scenarios`
-   `simulation_runs`
-   `simulation_configurations`

### Telemetry

-   `event_sources`
-   `security_events`
-   `event_correlations`

### Detection and incidents

-   `detections`
-   `incidents`
-   `incident_events`
-   `incident_techniques`

### Defense

-   `defense_modules`
-   `defense_policies`
-   `defense_states`
-   `state_transitions`
-   `defense_actions`
-   `action_audit_logs`

### AI

-   `ai_analyses`
-   `ai_recommendations`

### Evaluation

-   `experiment_trials`
-   `experiment_metrics`
-   `experiment_comparisons`

## 14.2 Suggested fields

Use UUID primary keys for operational records.

`mitre_techniques`: - `technique_id` (e.g. T1110; unique string primary
or unique key) - `name` - `description` - `platforms` JSONB -
`is_subtechnique` - `parent_technique_id` - `mitre_url` -
`source_version` - `source_modified_at`

`simulation_scenarios`: - `id` - `scenario_id` (unique) - `name` -
`description` - `technique_id` - `configuration_schema` JSONB -
`max_duration_seconds` - `max_event_rate` - `status`

`simulation_runs`: - `id` - `scenario_id` -
`ground_truth_technique_id` - `environment_mode` (`static` or
`adaptive`) - `status` - `started_at` - `ended_at` - `configuration`
JSONB - `cleanup_status`

`security_events`: - `id` - `simulation_run_id` - `occurred_at` -
`ingested_at` - `source_type` - `source_name` - `event_type` -
`source_ip` - `destination_ip` - `protocol` - `severity` - `metadata`
JSONB

`detections`: - `id` - `simulation_run_id` - `detector_id` -
`detected_at` - `severity` - `confidence` - `evidence_event_ids` JSONB -
`inferred_techniques` JSONB

`incidents`: - `id` - `title` - `description` - `severity` - `status` -
`first_seen` - `last_seen` - `resolved_at`

`defense_modules`: - `id` - `module_id` (unique) - `name` -
`description` - `implementation_status` - `enabled`

`defense_actions`: - `id` - `incident_id` - `module_id` - `action_id` -
`requested_by` - `policy_version` - `approved` -
`previous_configuration` JSONB - `new_configuration` JSONB -
`execution_status` - `executed_at` - `expires_at` - `rollback_status` -
`result` JSONB

`ai_analyses`: - `id` - `incident_id` - `model_name` -
`prompt_version` - `input_event_ids` JSONB - `analysis_json` JSONB -
`status` - `created_at`

`ai_recommendations`: - `id` - `analysis_id` - `module_id` -
`action_id` - `parameters` JSONB - `reason` - `validation_status` -
`policy_decision`

`experiment_metrics`: - `id` - `simulation_run_id` -
`detection_time_ms` - `mitigation_time_ms` - `mean_latency_ms` -
`p95_latency_ms` - `benign_success_rate` - `false_positive_rate` -
`recovery_time_ms` - `cpu_usage_percent` - `memory_usage_mb` -
`created_at`

## 14.3 Database requirements

-   Use foreign keys and unique constraints.
-   Use `TIMESTAMPTZ` and UTC.
-   Use JSONB only for genuinely flexible fields.
-   Index timestamps, technique IDs, run IDs, incident IDs, status, and
    source IP where useful.
-   Use migrations, not manual schema mutation.
-   Use transactions for defense-action lifecycle changes.
-   Keep event and action history append-only where practical.
-   Do not store real credentials, raw session cookies, private keys, or
    secrets.
-   Add retention configuration for high-volume telemetry.
-   Add seed data for known ATT&CK techniques, scenarios, and defense
    modules.
-   Preserve historical experiment records across MITRE catalog updates.

------------------------------------------------------------------------

# 15. Backend API Specification

Use versioned routes under `/api/v1`.

## 15.1 Health

-   `GET /api/v1/health`
-   `GET /api/v1/health/dependencies`

Return application, database, gateway, policy-agent, telemetry, and
Gemma readiness separately.

## 15.2 MITRE

-   `GET /api/v1/mitre/techniques`
-   `GET /api/v1/mitre/techniques/{technique_id}`
-   `GET /api/v1/mitre/tactics`
-   `GET /api/v1/mitre/coverage`
-   `POST /api/v1/mitre/import` --- administrator-only, disabled outside
    development unless explicitly enabled.

Support filters for platform, tactic, search term, sub-technique, and
implementation status.

## 15.3 Simulation

-   `GET /api/v1/simulations/scenarios`
-   `GET /api/v1/simulations/scenarios/{scenario_id}`
-   `POST /api/v1/simulations/runs`
-   `GET /api/v1/simulations/runs`
-   `GET /api/v1/simulations/runs/{run_id}`
-   `POST /api/v1/simulations/runs/{run_id}/stop`
-   `GET /api/v1/simulations/runs/{run_id}/results`

POST run request example:

``` json
{
  "scenario_id": "brute_force",
  "environment_mode": "adaptive",
  "configuration": {
    "target_service": "target-web",
    "duration_seconds": 30,
    "attempt_count": 8
  }
}
```

Validate every field against scenario hard limits. Do not accept
arbitrary target addresses.

## 15.4 Events and detections

-   `GET /api/v1/events`
-   `GET /api/v1/events/{event_id}`
-   `GET /api/v1/detections`
-   `GET /api/v1/detections/{detection_id}`

## 15.5 Incidents

-   `GET /api/v1/incidents`
-   `GET /api/v1/incidents/{incident_id}`
-   `POST /api/v1/incidents/{incident_id}/analyze`
-   `POST /api/v1/incidents/{incident_id}/resolve`

## 15.6 Defense

-   `GET /api/v1/defense/modules`
-   `GET /api/v1/defense/state`
-   `GET /api/v1/defense/actions`
-   `GET /api/v1/defense/actions/{action_id}`
-   `POST /api/v1/defense/actions/{action_id}/approve` if human approval
    is required
-   `POST /api/v1/defense/emergency-stop`

Do not expose arbitrary module command execution.

## 15.7 Metrics

-   `GET /api/v1/metrics/overview`
-   `GET /api/v1/metrics/runs/{run_id}`
-   `GET /api/v1/metrics/compare?scenario_id=...`

All APIs must use Pydantic request/response schemas, clear HTTP status
codes, structured errors, pagination, and input validation.

------------------------------------------------------------------------

# 16. Dashboard Requirements

Build a real connected dashboard, not a static design.

## 16.1 Main dashboard

Show: - System health. - Current defense state. - Active simulation. -
Recent incidents. - Events per minute. - Active defense modules. -
Latest policy transitions. - Static/adaptive summary metrics.

## 16.2 MITRE coverage page

-   ATT&CK technique list and search.
-   Tactic filters.
-   Technique detail panel.
-   Scenario mapping.
-   Detection implementation status.
-   Mitigation test status.
-   Link to official ATT&CK page.
-   Dataset version.

Distinguish imported, mapped, simulated, detected, and mitigation-tested
statuses.

## 16.3 Simulation page

-   Scenario selector.
-   MITRE technique reference.
-   Static/adaptive mode selector.
-   Validated configuration controls.
-   Start/stop actions.
-   Live run status.
-   Run timeline.
-   Result summary.

The frontend must not allow arbitrary IPs or arbitrary command strings
as simulation targets.

## 16.4 Live monitoring page

-   Recent security events.
-   Severity.
-   Source and destination.
-   Protocol.
-   Detector.
-   Associated incident.
-   ATT&CK mapping.
-   Search and filters.

Use WebSocket or polling for live updates. Keep a reliable REST
fallback.

## 16.5 Defense activity page

Display: - Module status. - Current configuration profile. -
State-machine state. - Trigger event. - Gemma recommendation. - Policy
decision. - Actual action result. - Expiry/rollback timer. - Audit
history.

Make it visually obvious whether an action was merely recommended,
approved, attempted, applied, verified, or rolled back.

## 16.6 Static vs adaptive comparison

Compare: - Detection time. - Mitigation time. - Legitimate request
success rate. - False-positive rate. - Mean and p95 latency. - Recovery
time. - CPU and memory overhead. - Number of policy changes. - Failed
policy changes.

Use only stored experiment measurements. Show trial count and
configuration details. Never fabricate improvements.

## 16.7 Visual design

Use a professional security operations dashboard: - Dark theme by
default if compatible with the existing frontend. - Clear typography and
consistent spacing. - Restrained status colors. - Green for healthy,
amber for warning, red for critical. - Accessible contrast. - Responsive
layout. - Loading, empty, error, and disconnected states. - No fake
charts or hard-coded metrics in production views.

------------------------------------------------------------------------

# 17. Static vs Adaptive Experiment Methodology

The project's main research/demo objective is to compare static and
adaptive defense fairly.

## 17.1 Controlled variables

Keep constant between paired runs: - Target image/version. - Scenario
version. - Workload profile. - Duration. - Request count/rate. - Docker
resource limits. - Baseline security policy. - Test data and synthetic
identities. - Host environment as far as practical.

## 17.2 Metrics definitions

`detection_time_ms`: Time between first relevant ground-truth scenario
event and first valid detection. Ground truth is used only for post-run
evaluation.

`mitigation_time_ms`: Time between first relevant event and verified
enforcement.

`benign_success_rate`: Successful benign requests divided by total
benign requests in the measurement window.

`false_positive_rate`: Benign evaluation windows incorrectly flagged
divided by total benign evaluation windows. Document the chosen
denominator.

`mean_latency_ms` and `p95_latency_ms`: Latency of benign requests
during the trial.

`recovery_time_ms`: Time from attack stop/containment to verified
baseline health and policy.

`resource_overhead`: CPU and memory consumed by the defense/monitoring
components. Record sampling method and interval.

## 17.3 Trial strategy

-   Run at least three repeated trials per mode for a demonstration
    dataset; more trials are preferable.
-   Alternate or randomize static/adaptive order to reduce warm-up bias.
-   Store all trial configuration.
-   Report median and spread, not just the best result.
-   Show incomplete or failed runs.
-   Do not compare trials with different workload parameters as if they
    were identical.

------------------------------------------------------------------------

# 18. Security Requirements and Threat Model

## 18.1 Assets

-   Host machine.
-   Docker daemon.
-   Backend API.
-   PostgreSQL.
-   Gemma endpoint/runtime.
-   Policy agent.
-   Gateway and firewall policies.
-   Attack and target containers.
-   Certificates and API secrets.
-   Simulation and incident data.

## 18.2 Threats to account for

-   Malicious or malformed telemetry.
-   Prompt injection in log content.
-   Compromised attacker container.
-   Unauthorized policy API calls.
-   Replayed or stolen client certificates.
-   Policy-agent compromise.
-   Unintended network paths.
-   Container privilege escalation.
-   Resource exhaustion.
-   Database injection or unauthorized access.
-   LLM hallucination or invalid structured output.
-   Incorrect source-IP attribution due to proxying.
-   False-positive automated blocking.

## 18.3 Required mitigations

-   Isolated Docker networks.
-   Least-privilege containers.
-   No Docker socket in attack/AI/backend services.
-   mTLS for protected gateway access.
-   Authenticated policy API.
-   Strict action allowlists.
-   Hard-coded upper bounds enforced server-side.
-   Pydantic validation.
-   SQL parameterization/ORM.
-   Secret management.
-   Audit logging.
-   Action expiry and rollback.
-   Emergency stop.
-   Input sanitization and prompt-injection-resistant AI design.
-   Dependency/image version pinning.
-   Automated tests for access boundaries.

## 18.4 Source IP attribution

When using a reverse proxy, the backend may see the proxy address rather
than the original client address. Configure trusted proxy headers
carefully:

-   Only trust headers inserted by the gateway.
-   Strip client-supplied forwarding headers at the edge.
-   Never trust arbitrary `X-Forwarded-For` from an untrusted client.
-   Record both transport peer and verified original source where
    available.
-   Use the correct source identity for policy decisions.

------------------------------------------------------------------------

# 19. Logging, Monitoring and Audit

Every important action must be traceable.

Record: - Simulation started/stopped. - Scenario configuration. - Events
ingested. - Detection created. - Incident created/updated. - Gemma
analysis requested/completed/failed. - Recommendation
validated/rejected. - Policy transition requested/approved/rejected. -
Defense action applied/failed/verified. - Rollback
requested/completed/failed. - Operator actions. - Emergency stop.

Logs must be structured JSON where possible. Do not log secrets or full
tokens. Include correlation IDs (`simulation_run_id`, `incident_id`,
`action_id`) in relevant logs.

Suricata EVE JSON should be parsed through a dedicated adapter. Avoid
directly sharing writable log directories with unrelated services.

------------------------------------------------------------------------

# 20. Testing Requirements

Antigravity must create and run tests, not just write test files.

## 20.1 Unit tests

-   MITRE importer and catalog.
-   Scenario registry validation.
-   Scenario hard limits.
-   Event normalization.
-   Detection thresholds.
-   Incident correlation.
-   Gemma JSON schema validation.
-   Policy allowlist.
-   IP/subnet validation.
-   Defense state transitions.
-   Metrics calculations.

## 20.2 Integration tests

-   Backend connects to PostgreSQL.
-   Alembic migrations run from an empty database.
-   MITRE endpoints return imported data.
-   Simulation run creates database records.
-   Telemetry collector ingests a fixture.
-   Detection creates a record.
-   Incident grouping works.
-   Policy agent authenticates requests.
-   Policy agent rejects out-of-scope IPs.
-   HAProxy ACL update blocks a lab client.
-   Unblock restores access.
-   Suricata produces readable events.

## 20.3 End-to-end test

The primary E2E test must:

1.  Start the stack.
2.  Confirm services are healthy.
3.  Confirm attacker cannot reach target directly.
4.  Confirm attacker can reach target through mTLS gateway.
5.  Start the bounded brute-force simulation.
6.  Verify authentication events were ingested.
7.  Verify the detector created a detection without reading ground
    truth.
8.  Verify an incident was created.
9.  Mock Gemma or use the configured test model to produce a valid
    recommendation.
10. Verify the policy engine approves only an allowed action.
11. Verify the gateway blocks the test source.
12. Verify the target becomes inaccessible through the gateway for that
    source.
13. Stop the simulation and perform recovery.
14. Verify unblock/rollback.
15. Verify PostgreSQL contains the complete event and action history.
16. Verify dashboard APIs return the run and metrics.

Use a deterministic mock Gemma response in CI so tests do not require an
external AI API. Add a separate integration test for the actual
configured Gemma provider.

## 20.4 Negative security tests

-   No client certificate: gateway rejects.
-   Certificate signed by unknown CA: gateway rejects.
-   TLS version below minimum: gateway rejects.
-   Missing/incorrect policy token: policy API rejects.
-   IP outside lab subnet: policy API rejects.
-   Arbitrary action ID: policy engine rejects.
-   Extra/unexpected LLM JSON fields: validator rejects.
-   Arbitrary target IP in simulation request: runner rejects.
-   Attack container to target direct path: connection fails.
-   Attack container to PostgreSQL: connection fails.
-   Policy agent to Docker socket: no socket is mounted.
-   Emergency stop: stops active simulation and blocks new ones.

------------------------------------------------------------------------

# 21. Implementation Roadmap

Implement in small vertical slices. Do not attempt to build every module
at once.

## Phase 0 --- Reconnaissance and baseline

-   Inspect repository.
-   Preserve working MITRE integration.
-   Inspect database teammate's work.
-   Confirm frontend/backend frameworks.
-   Document current state.
-   Confirm Docker Desktop works.
-   Confirm subnet ranges do not overlap.

**Exit criteria:** architecture plan and file-change plan approved; no
destructive overwrite.

## Phase 1 --- Compose foundation

-   Build backend, frontend, PostgreSQL, gateway, target, attacker,
    policy agent, and Suricata services.
-   Create isolated networks.
-   Add health checks.
-   Add `.env.example`.
-   Add certificate generation.
-   Add resource limits and container hardening.

**Exit criteria:** stack starts, health checks pass, target has no
direct attacker path.

## Phase 2 --- Secure gateway

-   Configure TLS 1.3 and mTLS.
-   Configure gateway-to-target route.
-   Configure restricted runtime socket.
-   Implement policy-agent authentication.
-   Implement block/unblock with IP scope validation.
-   Test live gateway behavior.

**Exit criteria:** mTLS access succeeds; invalid cert fails; approved
block causes 403; unblock restores access.

## Phase 3 --- PostgreSQL integration

-   Reuse or extend current schema.
-   Create Alembic migrations.
-   Add seed data.
-   Add repositories and database session handling.
-   Add indexes and constraints.

**Exit criteria:** all core records persist and survive restart.

## Phase 4 --- MITRE and scenario registry

-   Connect existing MITRE catalog.
-   Map initial techniques to scenario IDs.
-   Build scenario registry and limits.
-   Add scenario API.

**Exit criteria:** UI/API can list techniques and start only registered
scenarios.

## Phase 5 --- Telemetry and detection

-   Collect target and gateway logs.
-   Collect Suricata EVE JSON.
-   Normalize events.
-   Implement brute-force detector.
-   Create detections and incidents.

**Exit criteria:** a bounded simulation generates persisted events and
independent detection.

## Phase 6 --- Adaptive defense

-   Implement state machine.
-   Implement policy engine.
-   Connect rate limiter/gateway ACL.
-   Add action verification and rollback.
-   Add audit history.

**Exit criteria:** a detected incident causes a policy-validated, real
gateway configuration change.

## Phase 7 --- Gemma

-   Integrate configured Gemma runtime/provider.
-   Add prompt and response schemas.
-   Sanitize incident context.
-   Validate model output.
-   Add failure handling.
-   Keep deterministic policy engine authoritative.

**Exit criteria:** Gemma produces a validated recommendation;
invalid/unavailable AI cannot cause an action.

## Phase 8 --- Dashboard

-   Main overview.
-   MITRE coverage.
-   Simulation control.
-   Live events.
-   Incident detail.
-   Defense activity.
-   Static/adaptive comparison.

**Exit criteria:** all visible data comes from working APIs and
persisted records.

## Phase 9 --- Experiment and polish

-   Add repeated trials.
-   Add metrics and comparison.
-   Add security negative tests.
-   Add operator docs.
-   Verify clean startup and shutdown.
-   Prepare demo workflow.

**Exit criteria:** complete end-to-end demo with reproducible
measurements.

------------------------------------------------------------------------

# 22. Required Deliverables

At completion, provide:

1.  Updated repository with working implementation.
2.  Primary `compose.yaml`.
3.  `.env.example`.
4.  Dockerfiles for custom services.
5.  Gateway configuration.
6.  Policy agent.
7.  Suricata configuration and local rules.
8.  Backend API and services.
9.  PostgreSQL models and Alembic migrations.
10. MITRE integration preserving existing data.
11. Safe simulation scenarios.
12. Detection and correlation engine.
13. Gemma integration.
14. Policy engine and defense state machine.
15. Frontend dashboard pages.
16. Unit, integration, negative-security, and E2E tests.
17. PowerShell setup/start/stop/verification scripts.
18. `README.md` with exact setup commands.
19. `docs/ARCHITECTURE.md`.
20. `docs/API.md`.
21. `docs/DATABASE.md`.
22. `docs/SECURITY.md`.
23. `docs/SIMULATION.md`.
24. A demo runbook with expected results.

------------------------------------------------------------------------

# 23. Definition of Done

Do not report completion until these checks pass:

-   [ ] Existing repository functionality preserved.
-   [ ] Existing MITRE dataset/importer reused.
-   [ ] No duplicate MITRE dataset accidentally created.
-   [ ] PostgreSQL migrations run from an empty database.
-   [ ] `docker compose config` succeeds.
-   [ ] Docker images build successfully.
-   [ ] All required services become healthy.
-   [ ] All host-published ports bind to localhost.
-   [ ] Attacker cannot directly access protected target.
-   [ ] mTLS gateway access works.
-   [ ] Invalid certificate is rejected.
-   [ ] Policy API rejects invalid token.
-   [ ] Policy API rejects out-of-scope IP.
-   [ ] Approved block changes live gateway behavior.
-   [ ] Unblock restores access.
-   [ ] Suricata telemetry is collected.
-   [ ] Scenario runner enforces hard limits.
-   [ ] Detection is independent of ground truth.
-   [ ] Incident and event records persist.
-   [ ] Gemma output is schema-validated.
-   [ ] Gemma cannot directly execute actions.
-   [ ] Policy engine rejects unapproved actions.
-   [ ] Defense actions are audited and reversible.
-   [ ] Static and adaptive modes are both available.
-   [ ] Metrics are calculated from actual observations.
-   [ ] Dashboard uses live backend data.
-   [ ] Emergency stop works.
-   [ ] `docker compose down` cleans up correctly.
-   [ ] Documentation matches the actual implementation.

If any item fails, report it as incomplete. Do not fabricate test
results or claim that an untested feature works.

------------------------------------------------------------------------

# 24. Required Final Report from Antigravity

When implementation is complete, return a final engineering report
containing:

1.  What was already present and reused.
2.  What files were created.
3.  What files were modified.
4.  Final Docker service list and network topology.
5.  Database tables/migrations created or reused.
6.  API endpoints implemented.
7.  Scenarios implemented.
8.  Detection rules implemented.
9.  Defense modules that perform real actions.
10. Gemma provider/runtime and configuration.
11. Commands to start and stop the complete system.
12. Test commands and actual pass/fail results.
13. Known limitations.
14. Security risks that remain.
15. Recommended next implementation milestone.

Do not hide failures. Include exact errors and remediation steps.

------------------------------------------------------------------------

# 25. First MVP Demo Runbook

The first demo should be deliberately small and reliable.

1.  Start the full Compose stack.
2.  Open the AEGIS dashboard.
3.  Confirm all services show healthy.
4.  Open MITRE coverage and select `T1110 — Brute Force`.
5.  Select `static` mode and run the bounded test scenario.
6.  Show authentication events and detection result.
7.  Repeat the same scenario in `adaptive` mode.
8.  Show the incident and Gemma analysis.
9.  Show the deterministic policy decision.
10. Show the gateway ACL changing and the test source being blocked.
11. Show legitimate test requests and service health.
12. Stop the scenario and verify recovery/rollback.
13. Open the static-vs-adaptive comparison.
14. Show measured detection time, mitigation time, benign request
    success, latency, and recovery time.
15. Explain the limitations and number of trials honestly.

The demo must use a small fixed number of test requests against the
local lab target. It must not generate uncontrolled traffic.

------------------------------------------------------------------------

# 26. Final Direction

Build AEGIS as a modular, testable, secure-by-default local
cybersecurity research platform.

The key engineering principle is:

**Simulation generates behavior. Telemetry records behavior. Detection
identifies behavior. Gemma explains and recommends. The policy engine
authorizes. The orchestrator applies. Verification proves the result.
PostgreSQL preserves the evidence. The dashboard makes the process
observable.**

Do not sacrifice this separation for a quick visual demo.

Start with repository reconnaissance, then implement the first complete
vertical slice:

**T1110 → bounded local simulation → telemetry → independent detection →
incident → Gemma recommendation → deterministic policy validation →
gateway block → verification → rollback → PostgreSQL records → dashboard
timeline.**

Once that vertical slice works, expand the scenario catalog and defense
modules.
