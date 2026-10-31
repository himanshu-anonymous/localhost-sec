# MITRE ATT&CK Integration Guide for AEGIS

**Scope:** MITRE ATT&CK Enterprise --- Containers platform
(Docker/container environments)\
**Project:** AEGIS --- Adaptive Elastic Guard & Intelligent Security\
**Document version:** 1.0\
**Prepared:** 31 October 2026

------------------------------------------------------------------------

## 1. Purpose

This document explains how AEGIS should use MITRE ATT&CK to describe,
emulate, detect, and evaluate adversary behaviors in an isolated Docker
lab.

MITRE ATT&CK is a knowledge base of adversary tactics and techniques. It
is **not** an attack generator, exploit framework, or defense product.
AEGIS uses ATT&CK IDs and metadata to:

1.  Organize attack-emulation scenarios.
2.  Associate observed telemetry with known adversary behaviors.
3.  Map detections and defensive controls to techniques.
4.  Measure technique coverage.
5.  Explain incidents and recommend defensive actions through Gemma.
6.  Compare static and adaptive defenses under repeatable test
    conditions.

### Scope clarification

"Enterprise-Docker" is interpreted here as the **Enterprise ATT&CK
domain filtered to the `Containers` platform**. MITRE includes
Containers as a platform in Enterprise ATT&CK. The Containers platform
covers container technologies and orchestration systems; not every
technique is Docker-specific, and some examples are Kubernetes-oriented.

This document lists the parent techniques shown in the current MITRE
Containers matrix. The official STIX dataset is the source of truth for
current sub-techniques, descriptions, platform metadata, and changes.
The import process below retrieves those details instead of relying on a
permanently hard-coded list.

Official references:

-   Enterprise Containers matrix:
    https://attack.mitre.org/matrices/enterprise/containers/
-   Enterprise ATT&CK matrix:
    https://attack.mitre.org/matrices/enterprise/
-   ATT&CK data and tools:
    https://attack.mitre.org/resources/working-with-attack/
-   ATT&CK STIX data repository:
    https://github.com/mitre-attack/attack-stix-data
-   ATT&CK Navigator: https://mitre-attack.github.io/attack-navigator/

> **Versioning:** The MITRE site and STIX dataset change over time.
> Record the exact ATT&CK release or repository commit used for every
> experiment. Do not silently update the dataset during a comparison
> run.

------------------------------------------------------------------------

## 2. ATT&CK basics

### 2.1 Tactic

A tactic describes the adversary's **goal** --- the "why" behind an
action.

Examples:

-   Initial Access --- gain an entry point.
-   Execution --- run code or commands.
-   Persistence --- maintain access.
-   Privilege Escalation --- obtain higher permissions.
-   Credential Access --- obtain credentials or authentication material.
-   Discovery --- learn about the environment.
-   Lateral Movement --- move between systems or services.
-   Impact --- disrupt, destroy, or manipulate systems or data.

### 2.2 Technique

A technique describes **how** an adversary achieves a goal. It has an
identifier such as `T1611` (Escape to Host).

### 2.3 Sub-technique

A sub-technique provides a more specific variation of a technique. Its
ID adds a suffix, for example `T1059.004`. Store parent and
sub-technique IDs separately; do not strip the suffix when recording an
event.

### 2.4 Procedure

A procedure is a concrete way a threat actor or test implements a
technique. AEGIS simulation scenarios are controlled lab procedures, not
official MITRE procedures.

### 2.5 Mitigation and detection

-   **Mitigation:** a defensive recommendation or control that reduces
    the likelihood or impact of a technique.
-   **Detection:** analytics and telemetry used to identify behavior
    associated with a technique.
-   **Data component/source:** the event or log information needed by a
    detection.

ATT&CK does not guarantee that a technique can be detected from one
event. AEGIS should record the evidence and confidence behind each
detection.

------------------------------------------------------------------------

## 3. Enterprise Containers technique catalog

The following are the parent techniques displayed in MITRE's Enterprise
Containers matrix, grouped by tactic. A technique may appear under more
than one tactic in the matrix; the catalog should store one canonical
record per technique ID and associate it with all applicable tactics.

### 3.1 Initial Access

  -----------------------------------------------------------------------------------------------------
  ID                                                    Technique               AEGIS interpretation
  ----------------------------------------------------- ----------------------- -----------------------
  [T1190](https://attack.mitre.org/techniques/T1190/)   Exploit Public-Facing   Model a vulnerable test
                                                        Application             service receiving a
                                                                                simulated exploit
                                                                                indicator. Do not run
                                                                                real exploits against
                                                                                public systems.

  [T1133](https://attack.mitre.org/techniques/T1133/)   External Remote         Model access attempts
                                                        Services                through a deliberately
                                                                                exposed lab-only remote
                                                                                service.

  [T1078](https://attack.mitre.org/techniques/T1078/)   Valid Accounts          Model use of a seeded
                                                                                test identity and test
                                                                                credentials, including
                                                                                unusual access
                                                                                patterns.
  -----------------------------------------------------------------------------------------------------

### 3.2 Execution

  -----------------------------------------------------------------------------------------------------
  ID                                                    Technique               AEGIS interpretation
  ----------------------------------------------------- ----------------------- -----------------------
  [T1059](https://attack.mitre.org/techniques/T1059/)   Command and Scripting   Record a harmless,
                                                        Interpreter             allow-listed command
                                                                                event in a disposable
                                                                                container.

  [T1609](https://attack.mitre.org/techniques/T1609/)   Container               Generate test audit
                                                        Administration Command  events representing
                                                                                container
                                                                                administration
                                                                                activity.

  [T1610](https://attack.mitre.org/techniques/T1610/)   Deploy Container        Deploy a benign test
                                                                                container only into the
                                                                                dedicated lab
                                                                                network/namespace.

  [T1053](https://attack.mitre.org/techniques/T1053/)   Scheduled Task/Job      Model creation of a
                                                                                harmless scheduled test
                                                                                job and verify audit
                                                                                visibility.

  [T1204](https://attack.mitre.org/techniques/T1204/)   User Execution          Model a user-triggered
                                                                                action with a harmless
                                                                                test artifact or
                                                                                synthetic event.
  -----------------------------------------------------------------------------------------------------

### 3.3 Persistence

  -----------------------------------------------------------------------------------------------------
  ID                                                    Technique               AEGIS interpretation
  ----------------------------------------------------- ----------------------- -----------------------
  [T1098](https://attack.mitre.org/techniques/T1098/)   Account Manipulation    Model a test
                                                                                account/permission
                                                                                change and verify audit
                                                                                detection.

  [T1136](https://attack.mitre.org/techniques/T1136/)   Create Account          Create a disposable
                                                                                lab-only account
                                                                                through the target
                                                                                application's test
                                                                                interface.

  [T1543](https://attack.mitre.org/techniques/T1543/)   Create or Modify System Use a synthetic
                                                        Process                 service/process event
                                                                                or benign disposable
                                                                                test service.

  [T1133](https://attack.mitre.org/techniques/T1133/)   External Remote         Track persistence
                                                        Services                involving continued use
                                                                                of remote access
                                                                                services.

  [T1525](https://attack.mitre.org/techniques/T1525/)   Implant Internal Image  Use a local dummy image
                                                                                with a known test
                                                                                label/digest to
                                                                                validate image
                                                                                provenance controls.
                                                                                Never poison a shared
                                                                                or public registry.

  [T1053](https://attack.mitre.org/techniques/T1053/)   Scheduled Task/Job      Test whether a
                                                                                scheduled job persists
                                                                                beyond its intended
                                                                                lifecycle.

  [T1078](https://attack.mitre.org/techniques/T1078/)   Valid Accounts          Test whether an
                                                                                authorized test
                                                                                identity remains usable
                                                                                in an unexpected
                                                                                context.
  -----------------------------------------------------------------------------------------------------

### 3.4 Privilege Escalation

  -----------------------------------------------------------------------------------------------------
  ID                                                    Technique               AEGIS interpretation
  ----------------------------------------------------- ----------------------- -----------------------
  [T1098](https://attack.mitre.org/techniques/T1098/)   Account Manipulation    Detect unexpected
                                                                                changes to test account
                                                                                privileges or
                                                                                memberships.

  [T1543](https://attack.mitre.org/techniques/T1543/)   Create or Modify System Detect an unexpected
                                                        Process                 service/process
                                                                                configuration event in
                                                                                the lab.

  [T1611](https://attack.mitre.org/techniques/T1611/)   Escape to Host          **Do not perform a real
                                                                                container escape.**
                                                                                Generate a safe test
                                                                                event representing a
                                                                                blocked escape
                                                                                precondition and verify
                                                                                host/runtime controls.

  [T1068](https://attack.mitre.org/techniques/T1068/)   Exploitation for        Use a synthetic
                                                        Privilege Escalation    vulnerability finding
                                                                                or a safe intentionally
                                                                                vulnerable training
                                                                                target; do not execute
                                                                                host-escape payloads.

  [T1053](https://attack.mitre.org/techniques/T1053/)   Scheduled Task/Job      Detect a test job
                                                                                attempting to run with
                                                                                an unexpected privilege
                                                                                context.

  [T1078](https://attack.mitre.org/techniques/T1078/)   Valid Accounts          Detect use of a test
                                                                                account with
                                                                                permissions beyond its
                                                                                expected role.
  -----------------------------------------------------------------------------------------------------

### 3.5 Stealth

  -------------------------------------------------------------------------------------------------------
  ID                                                    Technique               AEGIS interpretation
  ----------------------------------------------------- ----------------------- -------------------------
  [T1612](https://attack.mitre.org/techniques/T1612/)   Build Image on Host     Model an unexpected local
                                                                                image-build event and
                                                                                verify build/audit
                                                                                policy.

  [T1070](https://attack.mitre.org/techniques/T1070/)   Indicator Removal       Use synthetic
                                                                                log-tampering indicators;
                                                                                never delete real audit
                                                                                logs or evidence.

  [T1036](https://attack.mitre.org/techniques/T1036/)   Masquerading            Use a harmless test
                                                                                image/container/account
                                                                                with a misleading test
                                                                                label and verify
                                                                                identity/provenance
                                                                                checks.
  -------------------------------------------------------------------------------------------------------

### 3.6 Defense Impairment

  -----------------------------------------------------------------------------------------------------
  ID                                                    Technique               AEGIS interpretation
  ----------------------------------------------------- ----------------------- -----------------------
  [T1685](https://attack.mitre.org/techniques/T1685/)   Disable or Modify Tools Simulate a
                                                                                monitoring-agent health
                                                                                failure; do not disable
                                                                                real host security
                                                                                tools.

  -----------------------------------------------------------------------------------------------------

### 3.7 Credential Access

  -----------------------------------------------------------------------------------------------------
  ID                                                    Technique               AEGIS interpretation
  ----------------------------------------------------- ----------------------- -----------------------
  [T1110](https://attack.mitre.org/techniques/T1110/)   Brute Force             Send a small, fixed
                                                                                number of failed logins
                                                                                to the local test login
                                                                                API.

  [T1528](https://attack.mitre.org/techniques/T1528/)   Steal Application       Use a synthetic token
                                                        Access Token            and model an
                                                                                unauthorized
                                                                                token-access event;
                                                                                never collect real
                                                                                tokens.

  [T1552](https://attack.mitre.org/techniques/T1552/)   Unsecured Credentials   Place a dummy canary
                                                                                credential in a
                                                                                disposable test fixture
                                                                                and verify
                                                                                secret-scanning alerts.
                                                                                Never use real secrets.
  -----------------------------------------------------------------------------------------------------

### 3.8 Discovery

  -----------------------------------------------------------------------------------------------------
  ID                                                    Technique               AEGIS interpretation
  ----------------------------------------------------- ----------------------- -----------------------
  [T1613](https://attack.mitre.org/techniques/T1613/)   Container and Resource  Query only the lab's
                                                        Discovery               own container inventory
                                                                                and verify that
                                                                                inventory access is
                                                                                audited.

  [T1046](https://attack.mitre.org/techniques/T1046/)   Network Service         Use a small,
                                                        Discovery               allow-listed set of lab
                                                                                service checks against
                                                                                known test containers.

  [T1069](https://attack.mitre.org/techniques/T1069/)   Permission Groups       Query test roles/groups
                                                        Discovery               in the lab application
                                                                                and verify audit
                                                                                events.
  -----------------------------------------------------------------------------------------------------

### 3.9 Lateral Movement

  -----------------------------------------------------------------------------------------------------
  ID                                                    Technique               AEGIS interpretation
  ----------------------------------------------------- ----------------------- -----------------------
  [T1550](https://attack.mitre.org/techniques/T1550/)   Use Alternate           Use a synthetic,
                                                        Authentication Material expired or replayed
                                                                                test token between lab
                                                                                services and verify
                                                                                rejection.

  -----------------------------------------------------------------------------------------------------

### 3.10 Impact

  -----------------------------------------------------------------------------------------------------
  ID                                                    Technique               AEGIS interpretation
  ----------------------------------------------------- ----------------------- -----------------------
  [T1485](https://attack.mitre.org/techniques/T1485/)   Data Destruction        Emit a synthetic
                                                                                destructive-action
                                                                                event or operate on
                                                                                disposable dummy files
                                                                                only.

  [T1499](https://attack.mitre.org/techniques/T1499/)   Endpoint Denial of      Apply a bounded
                                                        Service                 request/load test to
                                                                                the local target
                                                                                application.

  [T1490](https://attack.mitre.org/techniques/T1490/)   Inhibit System Recovery Simulate a
                                                                                recovery-control
                                                                                tampering event; do not
                                                                                delete backups or
                                                                                snapshots.

  [T1498](https://attack.mitre.org/techniques/T1498/)   Network Denial of       Run a bounded load
                                                        Service                 scenario only against
                                                                                the isolated lab
                                                                                service.

  [T1496](https://attack.mitre.org/techniques/T1496/)   Resource Hijacking      Run a short,
                                                                                resource-limited
                                                                                synthetic CPU/memory
                                                                                workload in a
                                                                                disposable container.
  -----------------------------------------------------------------------------------------------------

**Important:** The table is a human-readable parent-technique index. The
official STIX import is authoritative for all current
Containers-platform sub-techniques and metadata. Do not assume that
every technique above is equally applicable to every Docker deployment.

------------------------------------------------------------------------

## 4. Which techniques should AEGIS implement first?

Do not implement the entire catalog at once. Start with techniques that
can be safely emulated and measured with the current AEGIS architecture.

  -----------------------------------------------------------------------
  Priority          Technique         Why start here?   Suggested AEGIS
                                                        control
  ----------------- ----------------- ----------------- -----------------
  P0                T1110 --- Brute   Straightforward   Identity Guard,
                    Force             repeatable        Rate Limiter
                                      application       
                                      telemetry         

  P0                T1498 --- Network Demonstrates      Traffic Shield,
                    Denial of Service traffic anomaly   Rate Limiter
                                      and adaptive rate 
                                      limiting          

  P0                T1613 ---         Directly          Detection Engine,
                    Container and     exercises         Network
                    Resource          container         Segmentation
                    Discovery         visibility and    
                                      inventory         

  P1                T1046 --- Network Tests service     Network
                    Service Discovery visibility and    Segmentation
                                      segmentation      

  P1                T1550 --- Use     Tests synthetic   Session Guardian
                    Alternate         token/session     
                    Authentication    enforcement       
                    Material                            

  P1                T1552 ---         Tests secret      Secret Scanner,
                    Unsecured         detection and     Identity Guard
                    Credentials       safe canary       
                                      handling          

  P1                T1610 --- Deploy  Tests container   Container Policy
                    Container         deployment audit  Monitor
                                      and admission     
                                      policy            

  P2                T1525 --- Implant Tests image       Image Policy
                    Internal Image    provenance and    Monitor
                                      integrity         
                                      controls          

  P2                T1611 --- Escape  High-impact       Runtime Monitor,
                    to Host           behavior; use     Isolation Engine
                                      blocked-event     
                                      emulation only    

  P2                T1496 ---         Tests resource    Resource Monitor
                    Resource          limits and        
                    Hijacking         anomaly           
                                      monitoring        
  -----------------------------------------------------------------------

Suggested MVP: finish T1110 end-to-end before adding more scenarios. A
complete working pipeline is more valuable than a dashboard containing
many untested techniques.

------------------------------------------------------------------------

## 5. AEGIS architecture and data flow

``` text
                    MITRE ATT&CK STIX data
                              |
                              v
                    MITRE Catalog Importer
                              |
                              v
                      Technique Registry
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
      Scenario Registry                 Detection Mapping
             |                                 |
             v                                 |
      Isolated Docker Lab                      |
             |                                 |
             v                                 |
      Telemetry Collectors --------------------+
             |
             v
       Event Normalizer
             |
             v
      Detection + Correlation
             |
             v
        Incident Manager
             |
             +--------------------+
             |                    |
             v                    v
       Policy Engine         Gemma Analyst
             |                    |
             |              Recommendations
             |                    |
             +---------+----------+
                       |
                       v
               Defense Orchestrator
                       |
                       v
              Approved Defense Modules
                       |
                       v
             Verification + Audit Trail
                       |
                       v
                Dashboard + Metrics
```

### Design rules

1.  The simulator knows the intended technique ID; the detector must
    independently infer observed behavior.
2.  Keep simulation ground truth separate from detection output.
3.  Gemma explains and recommends; it does not execute commands or
    control Docker.
4.  The deterministic policy engine validates every recommendation
    against an allowlist.
5.  The defense orchestrator applies only approved, bounded
    configuration changes.
6.  Every action has an audit record, policy version, outcome and
    rollback path.
7.  If Gemma is unavailable, deterministic detection and defense
    continue.
8.  Treat logs and event payloads as untrusted data; do not follow
    instructions embedded in them.
9.  Use synthetic credentials, synthetic tokens and disposable data.
10. Keep the attack runner isolated from the Docker daemon socket and
    host control plane.

------------------------------------------------------------------------

## 6. Add the MITRE data to the project

### 6.1 Suggested repository structure

Add these folders to the existing AEGIS repository:

``` text
AEGIS/
├── backend/
│   ├── mitre/
│   │   ├── __init__.py
│   │   ├── importer.py
│   │   ├── catalog.py
│   │   ├── mapper.py
│   │   ├── schemas.py
│   │   ├── repository.py
│   │   └── data/
│   │       └── enterprise-attack.json
│   ├── detection/
│   │   ├── event_normalizer.py
│   │   ├── correlation_engine.py
│   │   └── detectors/
│   ├── orchestrator/
│   │   ├── policy_engine.py
│   │   └── state_machine.py
│   └── api/
│       └── mitre.py
├── simulation/
│   ├── runner.py
│   ├── scenario_registry.py
│   ├── limits.py
│   └── scenarios/
│       ├── brute_force.py
│       ├── bounded_http_load.py
│       ├── container_discovery.py
│       ├── service_discovery.py
│       ├── synthetic_session_replay.py
│       └── image_provenance_event.py
├── database/
│   └── migrations/
├── docs/
│   ├── MITRE.md
│   └── mitre-technique-mapping.md
└── scripts/
    └── update_mitre_data.py
```

### 6.2 Download the official STIX dataset

Use MITRE's official ATT&CK STIX data repository:

`https://github.com/mitre-attack/attack-stix-data`

The Enterprise collection is located at:

`enterprise-attack/enterprise-attack.json`

Download a release snapshot and place it at:

`backend/mitre/data/enterprise-attack.json`

For reproducible experiments, pin a release tag or commit and commit the
dataset version/hash to your project. Do not download the moving
`master` branch every time the backend starts.

### 6.3 Install dependencies

``` bash
pip install stix2 requests pydantic sqlalchemy psycopg[binary]
```

If you use an existing `requirements.txt`, add the packages there and
pin tested versions.

### 6.4 Import the Containers-platform techniques

Create `backend/mitre/importer.py`:

``` python
import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).parent
    / "data"
    / "enterprise-attack.json"
)

ATTACK_URL = "https://attack.mitre.org/techniques/{}/"


def external_attack_id(obj):
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id")
    return None


def import_container_techniques():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Missing ATT&CK dataset: {DATA_FILE}"
        )

    with DATA_FILE.open("r", encoding="utf-8") as file:
        bundle = json.load(file)

    objects = bundle.get("objects", [])
    results = []

    for obj in objects:
        if obj.get("type") != "attack-pattern":
            continue

        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue

        platforms = obj.get("x_mitre_platforms", [])

        if "Containers" not in platforms:
            continue

        technique_id = external_attack_id(obj)

        if not technique_id:
            continue

        tactics = [
            phase.get("phase_name")
            for phase in obj.get("kill_chain_phases", [])
            if phase.get("kill_chain_name") == "mitre-attack"
        ]

        results.append({
            "technique_id": technique_id,
            "name": obj.get("name"),
            "description": obj.get("description", ""),
            "platforms": platforms,
            "tactics": tactics,
            "is_subtechnique": obj.get(
                "x_mitre_is_subtechnique", False
            ),
            "url": ATTACK_URL.format(technique_id),
            "modified": obj.get("modified"),
        })

    results.sort(key=lambda item: item["technique_id"])

    output_file = DATA_FILE.parent / "containers-techniques.json"
    output_file.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print(f"Imported {len(results)} Containers techniques.")
    print(f"Output: {output_file}")

    return results


if __name__ == "__main__":
    import_container_techniques()
```

Run it:

``` bash
python -m backend.mitre.importer
```

This filters by the official `Containers` platform field and includes
sub-techniques where the source marks them as Containers-platform
techniques. It is safer and more maintainable than manually copying
technique names into application code.

If the upstream STIX structure changes, validate the dataset schema and
update the importer rather than silently importing an empty catalog.

### 6.5 Keep a local project mapping separate

Do not modify MITRE's source records to add AEGIS-specific fields. Store
project mappings in a separate file, for example
`backend/mitre/aegis-mapping.json`:

``` json
{
  "T1110": {
    "scenario_id": "brute_force",
    "detector_id": "failed_login_rate",
    "defense_modules": [
      "identity_guard",
      "rate_limiter"
    ],
    "simulation_mode": "safe_local",
    "implementation_status": "planned"
  },
  "T1498": {
    "scenario_id": "bounded_http_load",
    "detector_id": "traffic_rate_anomaly",
    "defense_modules": [
      "traffic_shield",
      "rate_limiter"
    ],
    "simulation_mode": "safe_local",
    "implementation_status": "planned"
  },
  "T1613": {
    "scenario_id": "container_discovery",
    "detector_id": "unexpected_container_inventory_access",
    "defense_modules": [
      "network_segmentation"
    ],
    "simulation_mode": "safe_local",
    "implementation_status": "planned"
  },
  "T1046": {
    "scenario_id": "service_discovery",
    "detector_id": "unexpected_service_probe",
    "defense_modules": [
      "network_segmentation"
    ],
    "simulation_mode": "safe_local",
    "implementation_status": "planned"
  },
  "T1550": {
    "scenario_id": "synthetic_session_replay",
    "detector_id": "invalid_or_replayed_test_token",
    "defense_modules": [
      "session_guardian"
    ],
    "simulation_mode": "synthetic_only",
    "implementation_status": "planned"
  }
}
```

The mapping file is owned by AEGIS. It connects MITRE metadata to your
own scenario, detector, module and implementation status.

------------------------------------------------------------------------

## 7. Database design

Use a canonical technique table and separate tables for simulation runs,
observations, detections and defense actions.

Example PostgreSQL schema:

``` sql
CREATE TABLE mitre_techniques (
    technique_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    tactics JSONB NOT NULL DEFAULT '[]',
    platforms JSONB NOT NULL DEFAULT '[]',
    is_subtechnique BOOLEAN NOT NULL DEFAULT FALSE,
    source_modified TIMESTAMPTZ,
    source_version TEXT,
    mitre_url TEXT NOT NULL
);

CREATE TABLE mitre_mappings (
    technique_id TEXT PRIMARY KEY
        REFERENCES mitre_techniques(technique_id),
    scenario_id TEXT,
    detector_id TEXT,
    defense_modules JSONB NOT NULL DEFAULT '[]',
    implementation_status TEXT NOT NULL DEFAULT 'not_started',
    notes TEXT
);

CREATE TABLE simulation_runs (
    run_id UUID PRIMARY KEY,
    technique_id TEXT NOT NULL
        REFERENCES mitre_techniques(technique_id),
    scenario_id TEXT NOT NULL,
    environment TEXT NOT NULL
        CHECK (environment IN ('static', 'adaptive')),
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    configuration JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE security_observations (
    event_id UUID PRIMARY KEY,
    run_id UUID REFERENCES simulation_runs(run_id),
    observed_at TIMESTAMPTZ NOT NULL,
    source TEXT NOT NULL,
    event_type TEXT NOT NULL,
    target_service TEXT,
    source_identity TEXT,
    severity TEXT,
    confidence NUMERIC(5,4),
    metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE technique_detections (
    detection_id UUID PRIMARY KEY,
    run_id UUID REFERENCES simulation_runs(run_id),
    technique_id TEXT
        REFERENCES mitre_techniques(technique_id),
    detected_at TIMESTAMPTZ NOT NULL,
    detector_id TEXT NOT NULL,
    confidence NUMERIC(5,4),
    evidence_event_ids JSONB NOT NULL DEFAULT '[]',
    analyst_status TEXT NOT NULL DEFAULT 'unreviewed'
);

CREATE TABLE defense_actions (
    action_id UUID PRIMARY KEY,
    run_id UUID REFERENCES simulation_runs(run_id),
    module_id TEXT NOT NULL,
    action_name TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    requested_by TEXT NOT NULL,
    approved BOOLEAN NOT NULL DEFAULT FALSE,
    applied_at TIMESTAMPTZ,
    result TEXT,
    rollback_reference TEXT,
    audit_metadata JSONB NOT NULL DEFAULT '{}'
);
```

### Coverage statuses

Use a controlled status vocabulary:

-   `not_started`
-   `catalog_imported`
-   `scenario_implemented`
-   `telemetry_verified`
-   `detection_implemented`
-   `detection_tested`
-   `mitigation_tested`
-   `regression_passed`

Do not mark a technique as detected merely because its simulation ran.

------------------------------------------------------------------------

## 8. Event format and ground truth

Use one normalized event schema across all scenarios:

``` json
{
  "event_id": "evt-lab-0001",
  "run_id": "run-uuid",
  "timestamp": "2026-10-31T10:00:00Z",
  "source": "target-app",
  "event_type": "authentication_failure",
  "target_service": "target-app",
  "source_identity": "lab-client-01",
  "severity": "medium",
  "metadata": {
    "test_account": "lab-user",
    "result": "failed"
  }
}
```

Keep simulation ground truth in a separate run record:

``` json
{
  "run_id": "run-uuid",
  "ground_truth_technique_id": "T1110",
  "scenario_id": "brute_force",
  "environment": "adaptive"
}
```

**Critical evaluation rule:** The detector must not read
`ground_truth_technique_id` as an input to its detection decision.
Ground truth is used only after detection to calculate whether the
detector identified the intended behavior.

A detection record should contain the detector's independently inferred
technique ID, evidence event IDs, confidence and timestamp.

------------------------------------------------------------------------

## 9. API endpoints

Suggested FastAPI routes:

  ----------------------------------------------------------------------------------------------
  Method                  Endpoint                                      Purpose
  ----------------------- --------------------------------------------- ------------------------
  GET                     `/api/mitre/techniques`                       List imported
                                                                        techniques; support
                                                                        tactic/platform/status
                                                                        filters

  GET                     `/api/mitre/techniques/{technique_id}`        Retrieve technique
                                                                        metadata and AEGIS
                                                                        mapping

  GET                     `/api/mitre/coverage`                         Return implementation
                                                                        and test coverage

  POST                    `/api/mitre/import`                           Import a previously
                                                                        downloaded, validated
                                                                        STIX snapshot;
                                                                        admin-only

  GET                     `/api/mitre/techniques/{technique_id}/runs`   List lab runs for a
                                                                        technique

  POST                    `/api/simulations/start`                      Start an approved
                                                                        scenario using a
                                                                        technique mapping

  POST                    `/api/simulations/{run_id}/stop`              Stop a running scenario

  GET                     `/api/simulations/{run_id}/results`           Return observations,
                                                                        detections and defense
                                                                        actions
  ----------------------------------------------------------------------------------------------

Example filtered request:

``` http
GET /api/mitre/techniques?platform=Containers&tactic=credential-access
```

Example response:

``` json
{
  "technique_id": "T1110",
  "name": "Brute Force",
  "platforms": ["Containers"],
  "tactics": ["credential-access"],
  "scenario_id": "brute_force",
  "implementation_status": "scenario_implemented",
  "mitre_url": "https://attack.mitre.org/techniques/T1110/"
}
```

Do not expose an API endpoint that accepts arbitrary shell commands or
arbitrary Docker arguments from the dashboard.

------------------------------------------------------------------------

## 10. Scenario implementation contract

Every AEGIS scenario should implement the same interface:

``` python
from typing import Protocol, Any


class Scenario(Protocol):
    scenario_id: str
    technique_ids: list[str]

    def validate(self, config: dict[str, Any]) -> None:
        """Validate lab target, permissions and hard safety limits."""
        ...

    def execute(self, config: dict[str, Any]) -> dict[str, Any]:
        """Run a bounded, approved simulation."""
        ...

    def collect_results(self) -> dict[str, Any]:
        """Return observations and scenario ground truth separately."""
        ...

    def cleanup(self) -> None:
        """Restore temporary test state."""
        ...
```

The runner should:

1.  Validate that the target is an approved lab service/container.
2.  Validate hard-coded upper bounds for duration, request rate and
    resources.
3.  Create a simulation run and record its ground-truth technique ID.
4.  Execute the registered scenario.
5.  Collect events from the same telemetry path used in normal
    monitoring.
6.  Run detection and correlation independently.
7.  Send the incident to the policy engine.
8.  Validate and apply only approved defense actions.
9.  Verify the resulting service and policy state.
10. Stop the scenario, clean up and persist the results.

The scenario registry must map a known `scenario_id` to reviewed code.
Never dynamically import a Python module or execute code based on a
user-supplied technique ID.

------------------------------------------------------------------------

## 11. Safe simulation plan for Docker

All testing must be limited to disposable containers and an isolated
Docker network owned by the project.

  -----------------------------------------------------------------------
  Technique               Safe test method        Evidence to collect
  ----------------------- ----------------------- -----------------------
  T1110                   Small fixed number of   Auth failures, source
                          failed logins against   identity, request
                          the local test API      timestamps

  T1498                   Bounded load against    Request rate, latency,
                          the local target with   error rate, resource
                          strict request/time     usage
                          limits                  

  T1613                   Read-only inventory     Inventory access, API
                          query against lab       audit event, caller
                          containers              identity

  T1046                   Small allow-listed      Connection attempts,
                          health checks against   destination service,
                          known lab services      timestamps

  T1550                   Synthetic               Token validation
                          expired/replayed token  result, session ID
                          against a test endpoint hash, rejection event

  T1552                   Dummy canary secret in  Secret scanner event;
                          a disposable fixture    never log the dummy
                                                  value itself

  T1610                   Deploy a benign test    Image digest, creator
                          container into the lab  identity, deployment
                          network                 event

  T1525                   Compare a local dummy   Image provenance
                          image label/digest      mismatch event
                          against an approved     
                          test manifest           

  T1611                   Generate a blocked      Runtime policy event,
                          escape-precondition     container privileges,
                          event or use runtime    alert
                          alert fixtures          

  T1496                   Short resource-limited  CPU/memory metrics,
                          synthetic workload in a resource limit and
                          disposable container    anomaly alert

  T1485 / T1490           Synthetic event or      Detection event and
                          disposable marker files evidence-preservation
                          only                    checks

  T1685                   Simulate monitor        Health status,
                          health-check failure    missing-heartbeat alert
                          without disabling host  
                          security tools          
  -----------------------------------------------------------------------

### Isolation checklist

-   Use a dedicated Docker network for the lab.
-   Do not attach the attack runner to production networks.
-   Do not mount `/var/run/docker.sock` into the attack runner.
-   Keep Docker daemon access in a separate, restricted orchestration
    component.
-   Apply container CPU, memory and process limits.
-   Use read-only filesystems where practical.
-   Use non-root users and drop unnecessary Linux capabilities.
-   Never use real passwords, access tokens, API keys or customer data.
-   Do not perform real container escapes, host privilege escalation,
    destructive actions, backup deletion or uncontrolled
    denial-of-service tests.
-   Set a maximum run duration and an out-of-band stop mechanism.
-   Capture logs before cleanup; preserve experiment evidence.

------------------------------------------------------------------------

## 12. Detection and defense mapping for AEGIS

The following is a starting project mapping, not a claim that these
controls fully mitigate the corresponding MITRE techniques.

  ----------------------------------------------------------------------------
  Technique         Detection signal      Candidate AEGIS   Example validated
                                          module            response
  ----------------- --------------------- ----------------- ------------------
  T1190             Abnormal application  Traffic Shield,   Restrict the test
                    errors or known test  Detection Engine  route; raise
                    vulnerability                           incident
                    indicator                               

  T1133             Unexpected            Identity Guard    Require approved
                    remote-service access                   identity and
                    pattern                                 access policy

  T1078             Unusual test-account  Identity Guard    Revoke test
                    use or privilege                        session; require
                    context                                 reauthentication

  T1609 / T1610     Unexpected container  Container Policy  Reject unapproved
                    admin/deployment      Monitor           deployment in the
                    event                                   lab

  T1611             Runtime               Isolation Engine  Preserve evidence;
                    escape-precondition                     isolate disposable
                    alert                                   test container if
                                                            approved

  T1525 / T1612     Image provenance or   Image Policy      Block unapproved
                    build-policy mismatch Monitor           test image from
                                                            deployment

  T1110             Failed-login burst    Rate Limiter,     Tighten login rate
                                          Identity Guard    limit and monitor
                                                            account

  T1528 / T1550     Unexpected token      Session Guardian  Revoke synthetic
                    access or invalid                       session and
                    replay                                  require
                                                            reauthentication

  T1552             Canary secret         Secret Scanner    Redact value,
                    detection                               alert, rotate only
                                                            test secret

  T1613 / T1046     Unexpected inventory  Network           Restrict only the
                    or service-probe      Segmentation      affected lab path
                    pattern                                 

  T1498 / T1499     Traffic surge and     Traffic Shield,   Apply bounded
                    service degradation   Rate Limiter      adaptive limits

  T1496             Unusual CPU/memory    Resource Monitor  Enforce container
                    consumption                             resource limits

  T1485 / T1490     Destructive-action or Audit/Recovery    Protect evidence
                    recovery-tampering    Monitor           and trigger
                    indicator                               recovery workflow

  T1685             Monitoring heartbeat  Monitoring Health Alert and use
                    missing               Guard             independent
                                                            telemetry
  ----------------------------------------------------------------------------

Core authentication and monitoring should not be switched off during a
response. Prefer layered controls and narrowly scoped changes.

------------------------------------------------------------------------

## 13. Gemma integration

Gemma should receive a compact incident object containing:

-   ATT&CK technique metadata from the local catalog.
-   Normalized observations and evidence references.
-   Detector's independently inferred classification and confidence.
-   Current AEGIS state.
-   Available defense modules and their current status.
-   Previous related incidents, if relevant.

Gemma should return structured recommendations such as:

``` json
{
  "incident_summary": "Repeated failed logins were observed against the lab login endpoint.",
  "technique_assessment": {
    "technique_id": "T1110",
    "confidence": 0.94
  },
  "recommended_modules": [
    "identity_guard",
    "rate_limiter"
  ],
  "recommended_actions": [
    {
      "module": "rate_limiter",
      "action": "tighten_login_rate_limit",
      "reason": "The failed-login rate exceeded the configured lab threshold."
    }
  ],
  "requires_human_approval": false
}
```

The policy engine must verify that:

-   The module exists and is enabled.
-   The action is on the module's allowlist.
-   The requested configuration is within hard limits.
-   The action is appropriate for the current incident and environment.
-   The action has an audit entry and rollback plan.

Treat the model's output as untrusted input. Gemma must not issue shell
commands, Docker commands, firewall commands or direct configuration
writes.

------------------------------------------------------------------------

## 14. Static vs adaptive experiment

For each selected technique, run equivalent trials in two environments.

### Static environment

-   Fixed baseline rate limits.
-   Fixed network policy.
-   Fixed session policy.
-   Standard monitoring.
-   No dynamic policy changes during the run.

### Adaptive environment

-   Same baseline controls.
-   Event-driven policy changes.
-   AEGIS state machine.
-   Validated module reconfiguration.
-   Verification and rollback.

Keep these constant between both environments:

-   Application image and version.
-   Baseline security configuration.
-   CPU and memory limits.
-   Test dataset and identities.
-   Scenario duration and workload.
-   Docker host and network conditions.

### Metrics

  -----------------------------------------------------------------------
  Metric                              Definition
  ----------------------------------- -----------------------------------
  Detection time                      Time from first relevant event to
                                      first valid detection

  Mitigation time                     Time from first relevant event to
                                      verified mitigation

  Legitimate request success          Successful benign requests / total
                                      benign requests

  False-positive rate                 Benign test windows incorrectly
                                      alerted / total benign test windows

  Service latency                     Median and p95 response latency

  Recovery time                       Time to return to baseline health
                                      and policy

  Resource overhead                   CPU and memory overhead caused by
                                      defense components

  Policy change overhead              Time and failure rate of policy
                                      application
  -----------------------------------------------------------------------

Repeat each trial and report actual measured results. Do not pre-fill
the dashboard with invented performance improvements.

------------------------------------------------------------------------

## 15. Dashboard design

Recommended screens:

1.  **ATT&CK Coverage:** Tactic columns, technique IDs, implementation
    statuses and links to MITRE.
2.  **Technique Detail:** Description, sub-techniques, platform tags,
    AEGIS mapping and related test runs.
3.  **Simulation Timeline:** Start/end, generated events, detections and
    defense actions.
4.  **Defense Activity:** State changes, module status, policy version
    and rollback status.
5.  **Static vs Adaptive:** Metrics and repeated-trial comparison.
6.  **Data Version:** ATT&CK release, STIX snapshot hash and last import
    time.

Use MITRE ATT&CK Navigator as a visual reference. AEGIS should show its
own measured implementation status, not imply that a colored technique
is fully covered simply because a scenario exists.

------------------------------------------------------------------------

## 16. Development roadmap

  --------------------------------------------------------------------------
  Stage                   Work                       Exit criteria
  ----------------------- -------------------------- -----------------------
  1 --- Catalog           Download and import        Local catalog includes
                          official STIX data; filter parent and
                          Containers platform        sub-technique records

  2 --- Mapping           Create AEGIS               Every MVP technique has
                          scenario/detector/module   an explicit mapping or
                          mapping                    `not_started` status

  3 --- Lab               Build isolated Docker      Lab is isolated and
                          target and telemetry path  produces normalized
                                                     events

  4 --- First scenario    Implement T1110 safe       Failed-login events are
                          simulation                 generated and stored

  5 --- Detection         Add independent            Detector identifies the
                          brute-force detector       pattern without reading
                                                     ground truth

  6 --- Defense           Connect Rate Limiter and   Approved policy change
                          Identity Guard through     is verified and audited
                          policy engine              

  7 --- AI                Add Gemma incident         Recommendations are
                          analysis                   schema-validated and
                                                     policy-checked

  8 --- More techniques   Add T1498, T1613, T1046,   Scenarios, detections
                          T1550                      and defenses pass
                                                     repeatable tests

  9 --- Evaluation        Run static/adaptive trials Metrics are calculated
                                                     from recorded
                                                     observations

  10 --- Expansion        Add other Containers       Coverage statuses
                          techniques based on        reflect tested
                          relevance                  capability
  --------------------------------------------------------------------------

### Definition of done for a technique

A technique is not "implemented" until:

-   It exists in the imported ATT&CK catalog.
-   It has a reviewed AEGIS mapping.
-   A safe lab scenario exists or an explicit reason is recorded why it
    is not emulated.
-   Telemetry is collected through the normal pipeline.
-   Detection works independently of scenario ground truth.
-   The defense response is policy-validated.
-   The action is verified, audited and reversible where applicable.
-   Regression tests pass.
-   Static/adaptive results are stored.

------------------------------------------------------------------------

## 17. Updating the catalog

Update the ATT&CK snapshot deliberately:

1.  Review the latest official ATT&CK release.
2.  Download the matching Enterprise STIX dataset.
3.  Record the release identifier, source URL, commit/tag and SHA-256
    hash.
4.  Run the importer in a test environment.
5.  Review added, modified, deprecated and revoked objects.
6.  Check whether existing AEGIS mappings still reference valid IDs.
7.  Run catalog and mapping tests.
8.  Approve and deploy the new snapshot.
9.  Preserve the old snapshot for historical experiment reproducibility.

Never rewrite old experiment records to point at a newer ATT&CK version.

------------------------------------------------------------------------

## 18. References

1.  MITRE ATT&CK Enterprise Containers Matrix ---
    https://attack.mitre.org/matrices/enterprise/containers/
2.  MITRE ATT&CK Enterprise Matrix ---
    https://attack.mitre.org/matrices/enterprise/
3.  MITRE ATT&CK Data and Tools ---
    https://attack.mitre.org/resources/attack-data-and-tools/
4.  MITRE ATT&CK Working with ATT&CK ---
    https://attack.mitre.org/resources/working-with-attack/
5.  MITRE ATT&CK STIX Data ---
    https://github.com/mitre-attack/attack-stix-data
6.  MITRE ATT&CK Navigator ---
    https://mitre-attack.github.io/attack-navigator/
7.  ATT&CK for Containers project ---
    https://ctid.mitre.org/projects/attck-for-containers/

------------------------------------------------------------------------

## 19. Final implementation recommendation

Build one complete vertical slice first:

**T1110 → local failed-login simulation → normalized telemetry →
independent detection → policy validation → Rate Limiter/Identity Guard
response → verification → Gemma explanation → dashboard timeline.**

Once this works reliably, reuse the same interfaces for T1498 and T1613.
This gives AEGIS a sound, measurable foundation before expanding to the
rest of the Containers technique catalog.
