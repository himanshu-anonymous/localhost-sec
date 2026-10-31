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

---

### Documentation Conventions
- All architectural updates, RFCs, and subsystem design documents must be placed in `system-docs/`.
- Markdown files should be cross-linked using standard relative links (e.g. `[Context Document](context.md)`).
- The root `README.md` should remain focused on high-level project overview, quickstart instructions, and live benchmark highlights.
