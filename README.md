# AEGIS --- Adaptive Modular Cybersecurity Defense

> **An AI-assisted, attack-aware security orchestration platform that
> dynamically adapts modular defense controls and compares their
> effectiveness against a static security baseline.**

```{=html}
<p align="center">
```
`<strong>`{=html}Dynamic Defense · Modular Security · Attack Simulation
· Gemma Intelligence`</strong>`{=html}
```{=html}
</p>
```

------------------------------------------------------------------------

## Table of Contents

-   [Overview](#overview)
-   [Problem Statement](#problem-statement)
-   [Objectives](#objectives)
-   [Core Innovation](#core-innovation)
-   [System Architecture](#system-architecture)
-   [Major Components](#major-components)
-   [Defense Modules](#defense-modules)
-   [Defense State Machine](#defense-state-machine)
-   [Attack Scenarios](#attack-scenarios)
-   [Gemma AI Integration](#gemma-ai-integration)
-   [Static vs Adaptive Evaluation](#static-vs-adaptive-evaluation)
-   [Technology Stack](#technology-stack)
-   [API Design](#api-design)
-   [Data Flow](#data-flow)
-   [Repository Structure](#repository-structure)
-   [Implementation Roadmap](#implementation-roadmap)
-   [Security and Safety Design](#security-and-safety-design)
-   [Expected Demonstration](#expected-demonstration)
-   [Project Status](#project-status)
-   [Contributing](#contributing)
-   [License](#license)

------------------------------------------------------------------------

## Overview

AEGIS is a proposed modular cybersecurity defense platform designed to
respond dynamically to changing network threats.

Conventional security deployments often rely on fixed configurations.
AEGIS explores a different approach: monitor network and application
behavior, identify suspicious activity, and adapt the configuration and
enforcement priority of independent security controls according to the
current threat.

The platform uses isolated Docker-based environments to compare two
approaches under equivalent simulated attack scenarios:

1.  **Static Defense:** A baseline environment using fixed security
    configurations.
2.  **Adaptive Defense:** An environment where a policy-driven
    orchestrator can adjust approved security controls in response to
    detected events.

Gemma acts as an AI security analyst. It summarizes incidents,
correlates evidence, explains potential impact, and recommends defensive
configurations. A deterministic policy engine---not the language
model---validates and applies security changes.

### Project at a glance

  -----------------------------------------------------------------------
  Attribute                           Description
  ----------------------------------- -----------------------------------
  Project name                        AEGIS

  Full name                           Adaptive Elastic Guard &
                                      Intelligent Security

  Domain                              Cybersecurity, network security, AI

  Architecture                        Modular defense orchestration

  Simulation                          Isolated Docker-based environments

  AI component                        Gemma API

  Main comparison                     Static defense vs adaptive defense

  Primary goal                        Demonstrate and measure
                                      attack-aware defense adaptation
  -----------------------------------------------------------------------

## Problem Statement

Traditional network security architectures frequently use predefined
security configurations that may not respond optimally to changing
attack patterns, evolving threats, or cascading failures across
dependent services.

Security mechanisms such as traffic filtering, rate limiting, identity
controls, session protection, and network segmentation are often
configured and managed independently. This can make coordinated
responses difficult and may delay containment when an attack affects
multiple components.

AEGIS proposes a modular, attack-aware defense orchestration
architecture that:

-   Collects telemetry from protected services and network components.
-   Detects suspicious behavior through deterministic rules and event
    correlation.
-   Dynamically adjusts approved security-control configurations.
-   Preserves foundational controls such as authentication and
    authorization.
-   Uses Gemma to explain incidents and recommend defensive measures.
-   Compares adaptive defense against a static baseline under controlled
    conditions.

## Objectives

1.  Design a modular architecture in which security controls can be
    managed independently.
2.  Build isolated Docker environments for controlled attack simulation.
3.  Collect and normalize network, application, authentication, and
    session events.
4.  Implement a deterministic defense state machine.
5.  Dynamically configure selected security controls through a
    centralized orchestrator.
6.  Integrate Gemma for incident analysis and defense recommendations.
7.  Provide a real-time dashboard for attacks, events, defense states,
    and module activity.
8.  Evaluate adaptive and static environments using repeatable
    experiments and measurable metrics.

## Core Innovation

The central idea is **attack-aware dynamic security-control
orchestration**.

AEGIS does not attempt to replace TCP, UDP, HTTP, TLS, DNS, or other
communication protocols. Instead, it dynamically changes how security
controls govern and protect communication and application services.

Security modules are independent components with defined interfaces. The
orchestrator can reinforce, configure, prioritize, or restore their
policies according to observed conditions.

The system uses overlapping defenses rather than a sequence of walls
where one control must fail before another becomes active.

### Design principles

-   **Modularity:** Each defense control has a defined interface and
    responsibility.
-   **Defense in depth:** Foundational protections remain enabled.
-   **Deterministic enforcement:** Security actions are validated by
    policy rules.
-   **AI-assisted analysis:** Gemma provides explanations and
    recommendations.
-   **Resilience:** Existing protections continue if the AI service is
    unavailable.
-   **Auditability:** Every state transition and policy change is
    recorded.
-   **Measurability:** The adaptive environment is compared with a
    matched static baseline.

------------------------------------------------------------------------

## System Architecture

AEGIS is organized into six major subsystems.

``` mermaid
flowchart TB
    subgraph SIM["1. Attack Simulation Environment"]
        A1["Traffic Generator"]
        A2["Authentication Test Client"]
        A3["DNS Test Client"]
        A4["Session Test Client"]
        A5["Lateral Movement Simulator"]
    end

    subgraph NET["2. Protected Docker Environment"]
        B["Nginx API Gateway"]
        C["Authentication Service"]
        D["Protected Application"]
        E["Redis Session Store"]
        F["Private Service Network"]
    end

    subgraph OBS["3. Telemetry and Detection"]
        G["Log Collector"]
        H["Network Monitor"]
        I["Detection Engine"]
        J["Event Normalizer"]
    end

    subgraph CORE["4. Adaptive Orchestration"]
        K["Defense State Machine"]
        L["Policy Engine"]
        M["Defense Module Manager"]
        N["Audit Engine"]
    end

    subgraph AI["5. AI Intelligence"]
        O["Gemma API"]
        P["Incident Analysis"]
        Q["Recommendations"]
    end

    subgraph UI["6. Dashboard and Evaluation"]
        R["React Dashboard"]
        S["Static vs Adaptive Comparison"]
        T["Live Network Visualization"]
    end

    SIM --> NET
    NET --> OBS
    OBS --> CORE
    CORE <--> AI
    M --> NET
    CORE --> UI
    AI --> UI
    OBS --> UI
```

### Subsystem responsibilities

  -----------------------------------------------------------------------
  Subsystem                           Responsibility
  ----------------------------------- -----------------------------------
  Attack Simulation Engine            Runs predefined, controlled attack
                                      scenarios

  Telemetry & Detection Engine        Collects events and identifies
                                      suspicious behavior

  Defense Orchestrator                Evaluates events and coordinates
                                      defense changes

  Modular Defense Layer               Enforces security policies

  Gemma Intelligence Layer            Analyzes incidents and recommends
                                      configurations

  Dashboard & Evaluation              Displays system state and compares
                                      experiment results
  -----------------------------------------------------------------------

## Major Components

### 1. Attack Simulation Engine

Generates controlled scenarios against isolated test services.

Responsibilities:

-   Start and stop predefined simulations.
-   Apply bounded scenario intensity and duration.
-   Tag generated events with a simulation identifier.
-   Record scenario start and end times.
-   Provide repeatable test conditions for both environments.

Suggested tools:

-   Locust for controlled HTTP load testing.
-   Python test clients for authentication, DNS, and session scenarios.
-   Docker Compose for isolated environments.

### 2. Telemetry and Detection Engine

Acts as the monitoring and event-collection layer.

**Data sources:**

-   Nginx access and error logs.
-   Application authentication logs.
-   Docker container health and resource metrics.
-   Network connection metadata.
-   DNS query logs.
-   Session validation events.
-   Firewall events.

**Detection responsibilities:**

-   Identify abnormal request rates.
-   Detect repeated authentication failures.
-   Identify unusual source-identity changes.
-   Detect unexpected DNS behavior.
-   Identify invalid or replayed test sessions.
-   Detect unauthorized internal service communication.

The MVP should use deterministic thresholds, signatures, and event
correlation. Statistical anomaly detection can be added as an extension.

### 3. Defense Orchestrator

The orchestrator is the central control component.

Responsibilities:

-   Maintain the current defense state.
-   Evaluate normalized security events.
-   Select applicable policy rules.
-   Coordinate defense-module configuration.
-   Prevent conflicting or unsafe policy changes.
-   Verify that changes were successfully applied.
-   Restore known-good configurations when appropriate.
-   Record all decisions and transitions.

The orchestrator should remain independent of the application being
protected.

### 4. Dashboard and Evaluation Engine

Provides the operator interface and experimental measurement system.

It should display:

-   Current threat level and defense state.
-   Active attack simulations.
-   Security events and alerts.
-   Defense module status and configuration.
-   Network topology.
-   Gemma incident summaries and recommendations.
-   Static versus adaptive comparison.
-   Performance and availability metrics.

------------------------------------------------------------------------

## Defense Modules

Each defense module is an independent component managed through a common
interface.

  -----------------------------------------------------------------------
  Module                  Responsibility          Suggested
                                                  implementation
  ----------------------- ----------------------- -----------------------
  Traffic Shield          Traffic filtering at    Nginx
                          the application edge    

  Rate Limiter            Request throttling      Nginx / application
                                                  middleware

  Identity Guard          Authentication and      FastAPI / RBAC
                          role-based              
                          authorization           

  IP Reputation Engine    Source behavior and     Python policy engine
                          reputation analysis     

  DNS Guardian            DNS event monitoring    DNS telemetry
                          and anomaly detection   

  Session Guardian        Session validation and  Redis / application
                          revocation              middleware

  Network Segmentation    Restricts communication Docker networks /
                          between services        firewall

  Isolation Engine        Contains affected test  Docker / firewall
                          services or clients     
  -----------------------------------------------------------------------

### Common defense-module interface

Every module should support:

-   Evaluation of relevant security events.
-   Configuration validation.
-   Application of an approved policy.
-   Health and status reporting.
-   Configuration versioning.
-   Rollback to a known-good configuration.
-   Audit logging.

Example interface:

``` python
from abc import ABC, abstractmethod

class DefenseModule(ABC):

    @abstractmethod
    def evaluate(self, event):
        pass

    @abstractmethod
    def validate_config(self, policy):
        pass

    @abstractmethod
    def configure(self, policy):
        pass

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def rollback(self):
        pass
```

A module must not report a configuration as active until the underlying
control has applied and verified it.

------------------------------------------------------------------------

## Defense State Machine

AEGIS uses five operational states. State transitions are based on
validated detection events, policy rules, confidence thresholds, and
system health.

``` mermaid
stateDiagram-v2
    [*] --> NORMAL

    NORMAL --> GUARDED: Suspicious activity
    GUARDED --> ADAPTIVE: Confirmed or escalating threat
    ADAPTIVE --> CONTAINMENT: Critical compromise indicators

    GUARDED --> NORMAL: Activity clears and health checks pass
    ADAPTIVE --> RECOVERY: Threat controlled
    CONTAINMENT --> RECOVERY: Containment verified

    RECOVERY --> NORMAL: Restoration and health checks pass

    GUARDED --> CONTAINMENT: Critical indicators
    RECOVERY --> ADAPTIVE: Threat reappears
```

### State definitions

  -----------------------------------------------------------------------
  State                   Description             Typical controls
  ----------------------- ----------------------- -----------------------
  `NORMAL`                Standard operation      Baseline policies and
                                                  monitoring

  `GUARDED`               Suspicious activity     Enhanced logging,
                          observed                reputation checks,
                                                  stricter monitoring

  `ADAPTIVE`              Threat confirmed or     Reinforced rate limits,
                          escalating              targeted filtering,
                                                  stricter session checks

  `CONTAINMENT`           Critical compromise     Session revocation,
                          indicators              segmentation, workload
                                                  isolation

  `RECOVERY`              Threat controlled       Gradual policy rollback
                                                  and service
                                                  verification
  -----------------------------------------------------------------------

### State-transition safeguards

-   A single low-confidence event should not trigger complete lockdown.
-   Use event correlation and confidence thresholds.
-   Apply hysteresis and minimum dwell times to prevent rapid state
    switching.
-   Preserve authentication and authorization controls.
-   Verify service health before restoring normal policies.
-   Maintain an audit trail of every transition.

## Attack Scenarios

The initial simulation suite should include:

  ------------------------------------------------------------------------
  Scenario          Simulated         Expected          Expected defense
                    behavior          detection         
  ----------------- ----------------- ----------------- ------------------
  DDoS-like         High-volume HTTP  Traffic surge and Edge filtering and
  overload          requests          service           rate limiting
                                      degradation       

  Brute-force       Repeated invalid  Authentication    Authentication
  simulation        login attempts    anomalies         throttling and
                                                        monitoring

  IP rotation       Requests from     Source behavior   Behavioral
                    multiple          changes           analysis and
                    simulated source                    targeted
                    identities                          restrictions

  DNS anomaly       Unexpected DNS    DNS               DNS monitoring and
                    resolution        irregularities    validation
                    patterns                            

  Session abuse     Invalid or        Session           Session revocation
                    replayed test     validation        and
                    session tokens    anomalies         reauthentication

  Lateral movement  Unauthorized      Segmentation      Network
                    requests between  violations        restriction and
                    isolated services                   isolation

  Combined scenario Multiple          Correlated        Coordinated
                    controlled        security events   multi-module
                    conditions                          response
  ------------------------------------------------------------------------

All simulations must run only against infrastructure owned or explicitly
authorized by the project team.

## Gemma AI Integration

Gemma acts as the **AI Security Analyst and Defense Configuration
Advisor**.

### Responsibilities

1.  Summarize security incidents.
2.  Explain detected behavior in understandable language.
3.  Correlate related security events.
4.  Identify potentially affected services.
5.  Recommend relevant defense modules.
6.  Suggest policy adjustments within predefined limits.
7.  Generate incident reports.

### Example input

``` json
{
  "event_id": "evt-001",
  "event_type": "traffic_anomaly",
  "severity": "high",
  "confidence": 0.94,
  "target_service": "auth-service",
  "source_identity": "simulated-client-04",
  "metadata": {
    "observed_requests": 12000,
    "baseline_requests": 500
  }
}
```

### Example structured output

``` json
{
  "incident_summary": "Elevated traffic affecting authentication",
  "attack_classification": "ddos_like_overload",
  "severity": "high",
  "recommended_modules": [
    "traffic_shield",
    "rate_limiter",
    "identity_guard"
  ],
  "recommended_actions": [
    {
      "action": "reinforce_rate_limit",
      "priority": 1
    },
    {
      "action": "increase_auth_monitoring",
      "priority": 2
    }
  ],
  "reasoning": "Traffic volume and authentication latency increased together."
}
```

### AI safety and execution model

Gemma must never directly execute privileged commands, modify firewall
rules, or access the Docker socket.

The intended workflow is:

1.  Detection engine publishes normalized events.
2.  Gemma analyzes the incident.
3.  Gemma returns a structured recommendation.
4.  The policy engine validates the recommendation against an allowlist
    and safety constraints.
5.  The orchestrator applies only permitted changes.
6.  The system verifies the result and records the action.

The deterministic defense engine must continue operating if the Gemma
API is unavailable.

Treat logs and event metadata as untrusted input. Redact secrets and
explicitly instruct the model to interpret event content as data rather
than instructions.

------------------------------------------------------------------------

## Static vs Adaptive Evaluation

A central goal of AEGIS is to measure whether adaptive defense provides
practical benefits over a static configuration.

### Experimental environments

**Environment A --- Static Defense**

-   Fixed Nginx configuration.
-   Fixed rate limits.
-   Fixed firewall policies.
-   Standard authentication and session controls.
-   Continuous monitoring.

**Environment B --- Adaptive Defense**

-   Same application and baseline security controls.
-   Dynamic rate-limit configuration.
-   Policy-driven firewall changes.
-   Adaptive session enforcement.
-   Centralized defense orchestration.
-   State-based security responses.

Both environments should receive equivalent attack scenarios, workload,
resource limits, and test durations.

### Evaluation metrics

  -----------------------------------------------------------------------
  Metric                              Purpose
  ----------------------------------- -----------------------------------
  Detection Time                      Time between attack start and
                                      detection

  Mitigation Time                     Time between detection and verified
                                      mitigation

  Service Availability                Whether legitimate clients can
                                      access the service

  Average Response Latency            Effect on legitimate request
                                      performance

  False Positive Rate                 Frequency of legitimate activity
                                      incorrectly flagged

  Resource Overhead                   CPU and memory used by the defense
                                      system

  Recovery Time                       Time required to restore normal
                                      operation

  Policy Switching Overhead           Cost of applying dynamic
                                      configurations
  -----------------------------------------------------------------------

### Example comparison format

The following values are illustrative placeholders, not measured
results.

  Metric                         Static   Adaptive
  ---------------------------- -------- ----------
  Detection time                  8 sec      5 sec
  Mitigation time                20 sec      7 sec
  Legitimate request success        72%        91%
  Recovery time                  35 sec     15 sec
  False positive rate                4%         5%

Actual results must be obtained through repeatable experiments. Adaptive
defense may improve some metrics while increasing latency, resource
consumption, or false positives in others.

------------------------------------------------------------------------

## Technology Stack

  -----------------------------------------------------------------------
  Layer                   Technology              Purpose
  ----------------------- ----------------------- -----------------------
  Frontend                React                   Dashboard and
                                                  visualization

  Styling                 Tailwind CSS            Interface styling

  Backend                 Python + FastAPI        APIs and orchestration

  AI                      Gemma API               Incident analysis and
                                                  recommendations

  Reverse Proxy           Nginx                   Traffic handling and
                                                  rate limiting

  Network Monitoring      Suricata                Network intrusion
                                                  detection

  Traffic Analysis        Zeek (optional)         Network metadata and
                                                  protocol analysis

  Firewall                nftables                Network policy
                                                  enforcement

  Infrastructure          Docker Compose          Isolated environments

  Database                PostgreSQL              Persistent records and
                                                  audit history

  Cache / Session Store   Redis                   Session data and
                                                  temporary state

  Load Testing            Locust                  Controlled HTTP load
                                                  simulation

  Real-time Updates       WebSockets              Dashboard event
                                                  streaming
  -----------------------------------------------------------------------

The MVP should begin with a smaller subset: React, FastAPI, Docker
Compose, Nginx, PostgreSQL, and Gemma. Additional monitoring tools can
be integrated as the architecture matures.

------------------------------------------------------------------------

## API Design

The FastAPI backend should expose separate API groups for simulations,
defense orchestration, security monitoring, and AI analysis.

### Simulation APIs

  Method   Endpoint                         Purpose
  -------- -------------------------------- -----------------------------
  POST     `/api/simulations/start`         Start a predefined scenario
  POST     `/api/simulations/stop`          Stop a running scenario
  GET      `/api/simulations`               List simulations
  GET      `/api/simulations/{id}`          Retrieve simulation status
  GET      `/api/simulations/{id}/events`   Retrieve scenario events

Example request:

``` json
{
  "scenario": "ddos_overload",
  "target": "adaptive_environment",
  "duration_seconds": 60,
  "intensity": "medium"
}
```

Only predefined scenario names and bounded parameters should be
accepted.

### Defense APIs

  ---------------------------------------------------------------------------------------
  Method                  Endpoint                                Purpose
  ----------------------- --------------------------------------- -----------------------
  GET                     `/api/defense/state`                    Current defense state

  GET                     `/api/defense/modules`                  List defense modules

  GET                     `/api/defense/modules/{id}`             Retrieve module
                                                                  configuration

  POST                    `/api/defense/modules/{id}/configure`   Apply a validated
                                                                  configuration

  POST                    `/api/defense/evaluate`                 Evaluate normalized
                                                                  events

  POST                    `/api/defense/rollback`                 Restore a previous
                                                                  policy

  GET                     `/api/defense/history`                  Retrieve transition
                                                                  history
  ---------------------------------------------------------------------------------------

### Security APIs

  Method   Endpoint                    Purpose
  -------- --------------------------- ---------------------------
  GET      `/api/security/events`      Retrieve security events
  GET      `/api/security/alerts`      Retrieve active alerts
  GET      `/api/security/metrics`     Retrieve security metrics
  GET      `/api/security/incidents`   Retrieve incidents
  GET      `/api/security/topology`    Retrieve network topology

### AI APIs

  Method   Endpoint                          Purpose
  -------- --------------------------------- ----------------------------------
  POST     `/api/ai/analyze`                 Analyze security events
  POST     `/api/ai/recommend`               Generate defense recommendations
  GET      `/api/ai/incident-summary/{id}`   Retrieve an incident summary
  GET      `/api/ai/explanations/{id}`       Retrieve an AI explanation

### WebSocket

``` text
/ws/dashboard
```

Example event:

``` json
{
  "event_type": "DEFENSE_STATE_CHANGED",
  "previous_state": "GUARDED",
  "current_state": "ADAPTIVE",
  "reason": "Sustained traffic anomaly",
  "active_modules": [
    "traffic_shield",
    "rate_limiter",
    "identity_guard",
    "session_guardian"
  ]
}
```

------------------------------------------------------------------------

## Data Flow

The main event-processing pipeline is:

``` mermaid
sequenceDiagram
    participant A as Attack Simulator
    participant N as Network Gateway
    participant D as Detection Engine
    participant O as Orchestrator
    participant G as Gemma
    participant P as Policy Engine
    participant F as Defense Modules
    participant UI as Dashboard

    A->>N: Generate simulated traffic
    N->>D: Send traffic telemetry
    D->>D: Detect anomaly
    D->>O: Publish normalized event
    O->>O: Evaluate rules and state
    O->>G: Request incident analysis
    G-->>O: Return recommendations
    O->>P: Validate proposed policy
    P->>P: Check allowlists and safety limits
    P->>F: Apply approved configuration
    F-->>O: Return application status
    O->>UI: Broadcast state and module changes
    D->>UI: Broadcast security events
    G->>UI: Publish incident explanation
```

### Normalized security event format

``` json
{
  "event_id": "evt-001",
  "timestamp": "2026-10-31T10:30:00Z",
  "source": "nginx_monitor",
  "event_type": "traffic_anomaly",
  "severity": "high",
  "confidence": 0.94,
  "target_service": "auth-service",
  "source_identity": "simulated-client-04",
  "metadata": {
    "observed_requests": 12000,
    "baseline_requests": 500
  }
}
```

A normalized event schema allows additional detection tools to be
integrated without changing the orchestrator's core interface.

------------------------------------------------------------------------

## Database Design

PostgreSQL should store persistent operational, experimental, and audit
information.

  -----------------------------------------------------------------------
  Table                               Important fields
  ----------------------------------- -----------------------------------
  `simulations`                       id, scenario, environment, status,
                                      started_at

  `security_events`                   id, event_type, severity, source,
                                      timestamp, metadata

  `incidents`                         id, attack_type, confidence, status

  `defense_modules`                   id, name, status,
                                      current_configuration

  `defense_states`                    id, state_name, entered_at

  `policy_versions`                   id, module_id, configuration,
                                      version

  `state_transitions`                 previous_state, next_state, reason

  `ai_recommendations`                incident_id, recommendation,
                                      approval_status

  `action_audit_logs`                 action, actor, result, timestamp

  `experiment_metrics`                environment, metric, value,
                                      timestamp
  -----------------------------------------------------------------------

Redis can be used for temporary session information, caching, and
short-lived operational state. PostgreSQL remains the persistent source
of truth.

------------------------------------------------------------------------

## Repository Structure

``` text
AEGIS/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── dashboard/
│   │   ├── network-topology/
│   │   └── defense-visualization/
│   └── package.json
│
├── backend/
│   ├── api/
│   │   ├── simulations.py
│   │   ├── defense.py
│   │   ├── security.py
│   │   └── ai.py
│   │
│   ├── orchestrator/
│   │   ├── state_machine.py
│   │   ├── policy_engine.py
│   │   └── module_manager.py
│   │
│   ├── defense_modules/
│   │   ├── traffic_shield.py
│   │   ├── rate_limiter.py
│   │   ├── identity_guard.py
│   │   ├── ip_reputation.py
│   │   ├── dns_guardian.py
│   │   ├── session_guardian.py
│   │   └── network_isolation.py
│   │
│   ├── detection/
│   │   ├── traffic_detector.py
│   │   ├── auth_detector.py
│   │   ├── dns_detector.py
│   │   └── event_normalizer.py
│   │
│   ├── ai/
│   │   ├── gemma_client.py
│   │   ├── prompts.py
│   │   └── response_validator.py
│   │
│   ├── evaluation/
│   │   ├── metrics.py
│   │   └── comparison.py
│   │
│   └── main.py
│
├── simulation/
│   ├── scenarios/
│   ├── traffic_generator/
│   ├── auth_simulator/
│   ├── dns_simulator/
│   └── session_simulator/
│
├── infrastructure/
│   ├── docker-compose.yml
│   ├── static/
│   ├── adaptive/
│   ├── nginx/
│   └── monitoring/
│
├── database/
│   └── schema.sql
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── experiments.md
│
└── README.md
```

------------------------------------------------------------------------

## Implementation Roadmap

The project should be implemented in four phases.

### Phase 1 --- Infrastructure and baseline

-   [ ] Create isolated Docker environments.
-   [ ] Deploy the same application in static and adaptive environments.
-   [ ] Configure Nginx.
-   [ ] Implement basic authentication and RBAC.
-   [ ] Implement baseline rate limiting.
-   [ ] Build the initial React dashboard.

**Deliverable:** Two functioning environments with equivalent baseline
security controls.

### Phase 2 --- Adaptive defense

-   [ ] Implement common defense-module interfaces.
-   [ ] Build the five-state defense state machine.
-   [ ] Implement event normalization.
-   [ ] Build the deterministic policy engine.
-   [ ] Implement dynamic rate-limit configuration.
-   [ ] Add network isolation and rollback.
-   [ ] Verify configuration changes after application.

**Deliverable:** A functioning adaptive defense orchestrator.

### Phase 3 --- AI and monitoring

-   [ ] Integrate the Gemma API.
-   [ ] Implement incident analysis.
-   [ ] Implement structured AI recommendations.
-   [ ] Add security-event monitoring.
-   [ ] Add real-time WebSocket updates.
-   [ ] Build network topology visualization.
-   [ ] Display AI explanations in the dashboard.

**Deliverable:** An AI-assisted security monitoring dashboard.

### Phase 4 --- Testing and evaluation

-   [ ] Implement predefined attack scenarios.
-   [ ] Test individual and combined scenarios.
-   [ ] Measure static versus adaptive performance.
-   [ ] Test AI service failure and deterministic fallback.
-   [ ] Test rollback and recovery.
-   [ ] Generate experiment reports.
-   [ ] Document limitations and results.

**Deliverable:** A repeatable demonstration and experimental comparison.

------------------------------------------------------------------------

## Security and Safety Design

Security controls must remain effective even when the orchestration or
AI layer experiences failures.

Key requirements:

-   Keep the attack simulation environment isolated from public and
    production networks.
-   Use predefined simulation scenarios with bounded parameters.
-   Never expose the Docker privileged socket to the frontend or AI
    service.
-   Do not allow arbitrary shell commands through APIs or AI responses.
-   Preserve authentication and authorization during all defense-state
    transitions.
-   Validate every proposed configuration against an allowlist and
    explicit limits.
-   Require administrator approval for disruptive actions such as
    workload isolation.
-   Keep versioned configurations and known-good rollback policies.
-   Authenticate and authorize administrative APIs.
-   Store API credentials in environment variables or a secrets manager.
-   Redact tokens, passwords, and other secrets before sending telemetry
    to an external AI API.
-   Maintain audit records for policy changes, approvals, and execution
    results.
-   Ensure the deterministic defense engine remains operational if Gemma
    is unavailable.

## Expected Demonstration

The intended hackathon demonstration follows this sequence:

1.  Start the static and adaptive environments.
2.  Display their baseline security configurations.
3.  Launch a controlled traffic-overload scenario.
4.  Observe detection events in both environments.
5.  Show the adaptive environment transitioning from `NORMAL` to
    `GUARDED` and then `ADAPTIVE`.
6.  Display the relevant defense modules being reconfigured.
7.  Introduce a separate authentication or session-abuse scenario.
8.  Show identity and session protections responding without disabling
    foundational controls.
9.  Display Gemma's incident analysis and recommendations.
10. Show the experiment comparison with measured availability, latency,
    mitigation time, and recovery time.

The final demonstration should make the adaptive changes visible and
show their actual effect on the protected test services.

------------------------------------------------------------------------

## Project Status

**Current stage:** Architecture and design finalized; implementation
planned.

Planned milestones:

-   [ ] Repository initialization
-   [ ] Docker environment setup
-   [ ] Static baseline deployment
-   [ ] Adaptive environment deployment
-   [ ] Defense module framework
-   [ ] Orchestrator and state machine
-   [ ] Telemetry and detection
-   [ ] Gemma integration
-   [ ] Dashboard implementation
-   [ ] Experimental evaluation

## Contributing

Contributions are welcome as the project moves into implementation.

Suggested areas:

-   Frontend and dashboard development.
-   Backend APIs and orchestration.
-   Network security and defense modules.
-   Attack simulation and test scenarios.
-   Gemma integration and structured output validation.
-   Experiment design and performance evaluation.
-   Documentation and testing.

For substantial changes, discuss the proposed design before submitting a
pull request.

## License

License to be selected by the project maintainers.

------------------------------------------------------------------------

```{=html}
<p align="center">
```
`<strong>`{=html}AEGIS --- Adapt. Defend.
Recover.`</strong>`{=html}`<br>`{=html} `<sub>`{=html}Building a
measurable, modular and adaptive approach to cybersecurity
defense.`</sub>`{=html}
```{=html}
</p>
```
