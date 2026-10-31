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

2. [**AEGIS: Adaptive Modular Cybersecurity Defense (`aegis_modular_defense.md`)**](aegis_modular_defense.md)
   - Detailed specification of modular defense orchestration, defense state machine, and static vs. adaptive Docker evaluation.

---

### Documentation Conventions
- All architectural updates, proposals, and design documents must be stored in `system-docs/`.
- Markdown files are cross-linked using standard relative links.
- The root `README.md` serves as the concise executive entry point, quickstart guide, and repository directory.
