# System Documentation Index
## localhost (BASTION X)

This directory contains the formal architectural specifications, technical proposals, mathematical models, and design documentation for **localhost**.

---

### Core Documentation

1. [**Formal Architecture & Technical Specification v1.0 (`context.md`)**](context.md)
   - **Executive Vision**: The Cross-Layer Exploitation Paradox & research hypothesis.
   - **The 3-Domain Architecture**: Domain A (Fast Simulation & Shared PPO), Domain B (Docker Cyber-Range Validation), Domain C (Gemma 4 Analysis).
   - **Network Topology Graph**: 8-node canonical enterprise topology and deny-by-default communication policies.
   - **Dynamic Defensive Policy Stack (DDPS)**: Safety pipeline, parameter vectors $\mathbf{\Theta}_k(t)$, and Hard Security Invariants ($\Omega$).
   - **MITRE ATT&CK Scenario Engine**: Attack campaign formulation and the "Black Sky CI/CD" benchmark.
   - **Telemetry & Quantitative Metrics**: Mathematical definitions of $A_{\text{eff}}$, $MTTC$, $BRF$, and $RDI$.
   - **Implementation Acceptance Criteria**: Milestone criteria for M1 through M7.

2. [**MITRE ATT&CK Integration Guide for Enterprise Containers (`MITRE.md`)**](MITRE.md)
   - Scope: Enterprise ATT&CK domain filtered to the `Containers` platform.
   - 9 Tactic mappings: Initial Access, Execution, Persistence, Privilege Escalation, Credential Access, Discovery, Lateral Movement, Exfiltration, Impact.
   - Emulation rules, detection analytics, telemetry mapping, and STIX data pipelines.

3. [**Master Database Architecture & Ephemeral Graph Plan (`DATABASE_ARCHITECTURE.md`)**](DATABASE_ARCHITECTURE.md)
   - Persistent Relational Store (PostgreSQL 16) + Ephemeral Runtime Graph (Neo4j 5).
   - 18 relational tables across 5 domains.
   - Run-scoped Neo4j graph hydration, dynamic edge mutation, blast radius calculation, and automatic teardown.

4. [**AEGIS: Adaptive Modular Cybersecurity Defense (`aegis_modular_defense.md`)**](aegis_modular_defense.md)
   - Detailed specification of modular defense orchestration, defense state machine, and static vs. adaptive Docker evaluation.

---

### Documentation Conventions
- All architectural updates, proposals, and design documents must be stored in `system-docs/`.
- Markdown files are cross-linked using standard relative links.
- The root `README.md` serves as the concise executive entry point, quickstart guide, and repository directory.
