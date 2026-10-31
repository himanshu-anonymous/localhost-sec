# localhost (BASTION X)
### Adaptive Multi-Layer Network Defence Simulator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![RL Algorithm: PPO](https://img.shields.io/badge/RL-PPO-orange.svg)](https://arxiv.org/abs/1707.06347)
[![Safety: DDPS Invariant Guardrails](https://img.shields.io/badge/Safety-DDPS%20Enforced-green.svg)](#dynamic-defensive-policy-stack-ddps)
[![AI Analysis: Gemma 4](https://img.shields.io/badge/AI-Gemma%204-purple.svg)](system-docs/context.md)
[![License: Open Source](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An open-source, AI-assisted cyber-resilience experimentation platform that trains, evaluates, and benchmarks adaptive defensive policies across multiple isolated private network environments under concurrent, multi-stage attack scenarios.

---

## ⚡ The Core Problem & Innovation

Current cyber testing frameworks evaluate defensive controls (firewalls, WAFs, rate-limiters, IAM) in isolation. In reality, modern attacks exploit **cross-layer cascade failures** (e.g. volumetric edge saturation causing authentication timeouts, leading to thread starvation, and creating cover for lateral movement).

**localhost** introduces:
1. **The 3-Domain Architecture**:
   - **Domain A (Fast Simulation)**: Rapid deterministic Gymnasium-compatible RL training ($>100\text{Hz}$) with shared-policy PPO.
   - **Domain B (Container Cyber-Range)**: Isolated Docker private network validation for human-approved policy checkpoints.
   - **Domain C (AI Reasoning)**: Out-of-band Gemma 4 structured explanations and root-cause analysis (with multi-key rotation across environments).
2. **Dynamic Defensive Policy Stack (DDPS)**: An autonomous safety pipeline that adjusts multi-layer control priorities in real time without ever violating non-negotiable security invariants ($\Omega$).
3. **Synchronous 4-Way Parallel Benchmarking**: Tests Baseline (fixed permissive), Adaptive (DDPS active), Hardened (strict static), and Experimental policies simultaneously under identical attack seeds.

```mermaid
flowchart TD
    User["Operator / Dashboard"] --> Core["FastAPI Orchestrator"]
    Core --> EnvFactory["Parallel Environment Factory"]
    
    subgraph DOMAIN_A ["Domain A: Fast Simulation & Shared PPO Training"]
        EnvFactory --> EnvA["Env A: Baseline<br/>(Fixed Permissive)"]
        EnvFactory --> EnvB["Env B: Adaptive<br/>(DDPS + Shared PPO)"]
        EnvFactory --> EnvC["Env C: Hardened<br/>(Strict Static)"]
        EnvFactory --> EnvD["Env D: Experimental<br/>(Held-out Tuning)"]
        
        EnvA & EnvB & EnvC & EnvD --> PPO["Shared PPO Policy"]
        PPO --> DDPS["DDPS Safety & Invariant Validator (Omega)"]
        DDPS --> EnvA & EnvB & EnvC & EnvD
    end
    
    subgraph DOMAIN_C ["Domain C: AI Explanation"]
        DDPS --> Gemma["Gemma 4 Service<br/>(4-Key Rotation: Env A..D)"]
    end

    subgraph DOMAIN_B ["Domain B: Real Container Cyber-Range"]
        PPO -.->|Approved Checkpoint| Docker["Docker Private Network Validation"]
    end
```

---

## 🚀 Quickstart & Milestone M1 Demo

### 1. Prerequisites & Virtual Environment
```bash
# Clone the repository
git clone https://github.com/himanshu-anonymous/localhost-sec.git
cd localhost-sec

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure Environment Keys (optional for live Gemma reasoning)
cp .env.example .env
```

### 2. Run the Acceptance Tests
Verify all acceptance criteria of Milestone M1 (Parallel RL Simulation Proof) and Domain C (Gemma Reasoning Service):
```bash
python -m pytest backend/tests/ -v
```

### 3. Run the Live "Black Sky" Simulation Demonstration
```bash
python run_m1_demo.py
```

---

## 📊 Live Benchmark Results ("Black Sky CI/CD" Scenario)

| Environment Profile | Effective Availability | Blast Radius | Containment Time (MTTC) | Resiliency Degradation Index (RDI) |
| :--- | :---: | :---: | :---: | :---: |
| **`env_a_baseline`** (Permissive static) | **39.8%** | 0.12 | **UNCONTAINED** (Breach) | 60.2 |
| **`env_b_adaptive`** (DDPS + PPO) | **98.2%** | **0.00** | **0.0s** | **1.8** |
| **`env_c_hardened`** (Strict static) | 96.5% | 0.00 | 0.0s | 3.5 |
| **`env_d_experimental`** (AI tuning) | 74.8% | 0.00 | 6.0s | 25.3 |

> **Key Finding**: Under simultaneous Edge DDoS, Auth Stuffing, and Lateral CI exploitation, the **Adaptive policy (`env_b`)** contained the lateral pivot and maintained **98.2% service availability**, whereas the conventional static baseline collapsed to **39.8%**.

---

## 📁 Repository Structure

```
localhost-sec/
├── README.md                           # Main Project Overview & Quickstart
├── .env.example                        # Safe environment template for API keys
├── .gitignore                          # Ignored credentials, caches, & models
├── run_m1_demo.py                      # Live terminal demonstration runner
├── system-docs/                        # 📚 System Architecture & Specifications
│   ├── README.md                       # Documentation Index
│   ├── context.md                      # Comprehensive Architecture & Technical Spec v1.0
│   └── aegis_modular_defense.md        # Modular Defense Proposal Reference
├── backend/
│   ├── requirements.txt                # Python dependencies (Torch, Gymnasium, FastAPI)
│   ├── app/
│   │   ├── schemas/                    # Pydantic telemetry & action schemas
│   │   ├── topology/                   # 8-node logical enterprise graph
│   │   ├── scenarios/                  # MITRE ATT&CK incident generator (Black Sky)
│   │   ├── ddps/                       # Dynamic Defensive Policy Stack & Invariants (Omega)
│   │   ├── environments/               # Gymnasium environment & parallel vectorizer
│   │   ├── rl/                         # Shared PPO agent (PyTorch actor-critic)
│   │   └── gemma/                      # Gemma 4 Reasoning Service & multi-key rotation
│   └── tests/
│       ├── test_m1_parallel_simulation.py  # Milestone M1 acceptance tests
│       └── test_gemma_service.py           # Gemma service & schema tests
└── models/
    └── checkpoints/                    # Saved PyTorch policy checkpoints
```

---

## 📖 System Documentation

Detailed technical documentation, mathematical models, MITRE ATT&CK mapping, and system designs are maintained in the [`system-docs/`](system-docs/) folder:

- [**System Specification & Context (`system-docs/context.md`)**](system-docs/context.md): Full technical specification v1.0, mathematical state formulations, DDPS finite state machine, and roadmap.
- [**AEGIS Modular Defense Reference (`system-docs/aegis_modular_defense.md`)**](system-docs/aegis_modular_defense.md): In-depth modular defense architecture and state machine reference.
- [**Documentation Index (`system-docs/README.md`)**](system-docs/README.md): Guide to system documentation conventions.
