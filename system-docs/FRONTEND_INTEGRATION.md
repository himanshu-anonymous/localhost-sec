# BASTION X — Frontend Integration Guide & Contract Specification

**Document Version:** 1.0  
**Target Audience:** Frontend Engineers (Branch: `origin/trisha_frontend`)  
**Backend Classification:** Adaptive Multi-Layer Network Defence Simulator Orchestrator Core  

---

## 1. Frontend Branch Identification

- **Git Branch:** `origin/trisha_frontend` (tracked on remote)
- **Base Integration Commit:** `11f199d`
- **Target Stack:** React 18 / TypeScript / Vite / Tailwind CSS / React Flow
- **Integration Boundary:** The frontend operates on a dedicated branch and consumes the backend via standard REST APIs (`http://localhost:8000`) and WebSocket streams (`ws://localhost:8000`).

---

## 2. Backend Startup Instructions

### Option A: Complete Containerized Stack (Workers + DBs + Redis)
```bash
# 1. Clone & enter repository
git clone https://github.com/himanshu-anonymous/localhost-sec.git
cd localhost-sec

# 2. Configure environment
cp .env.example .env

# 3. Spin up PostgreSQL, Neo4j, Redis, and 4 Workers
docker compose up -d

# 4. Start Central Orchestrator
python -m backend.app.main
```

### Option B: Local Python Development Mode (In-Memory Fallback)
```bash
# Activate virtual environment
.\.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Linux/macOS

# Launch FastAPI Orchestrator
python -m backend.app.main
# Server binds to http://0.0.0.0:8000
# OpenAPI Docs: http://localhost:8000/docs
# Interactive Visualizer: http://localhost:8000/dashboard
```

---

## 3. API Base URL & CORS Requirements

- **REST API Base URL:** `http://localhost:8000`
- **WebSocket Base URL:** `ws://localhost:8000`
- **CORS Configuration:** Fully permissive in development mode (`allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`).
- **Authentication:** Standard Bearer JWT optional; default simulator runs in operator mode without blocking headers.

---

## 4. REST Endpoints Specification

### 4.1 Environment Management

#### `GET /api/v1/environments`
Lists the 4 parallel cyber-range simulation environments and their container health.

**Response Example:**
```json
{
  "environments": [
    {
      "id": "env_a_baseline",
      "url": "http://localhost:8001",
      "docker_healthy": true,
      "profile": "baseline"
    },
    {
      "id": "env_b_adaptive",
      "url": "http://localhost:8002",
      "docker_healthy": true,
      "profile": "adaptive"
    },
    {
      "id": "env_c_hardened",
      "url": "http://localhost:8003",
      "docker_healthy": true,
      "profile": "hardened"
    },
    {
      "id": "env_d_experimental",
      "url": "http://localhost:8004",
      "docker_healthy": true,
      "profile": "adaptive"
    }
  ]
}
```

#### `GET /api/v1/environments/{environment_id}`
Returns status and telemetry profile of a specific instance.

#### `POST /api/v1/environments/{environment_id}/reset`
Resets the simulation instance state to initial baseline.

---

### 4.2 Scenario Management

#### `GET /api/v1/scenarios`
Lists available synthetic incident scenarios.

**Response Example:**
```json
{
  "scenarios": [
    {
      "name": "black_sky",
      "description": "Multi-stage cascade failure: volumetric edge DDoS, credential stuffing, and lateral pivot",
      "duration_seconds": 120,
      "incident_count": 3
    },
    {
      "name": "held_out_evaluation",
      "description": "Repeatable evaluation benchmark with fixed seeds",
      "duration_seconds": 60,
      "incident_count": 2
    }
  ]
}
```

#### `GET /api/v1/scenarios/{scenario_name}/timeline`
Returns the temporal event timeline for incident visualization.

---

### 4.3 Training Controls (Shared PPO Agent)

#### `POST /api/v1/training/start`
Starts central shared PPO policy training across all 4 workers in a background thread.

**Request Body:**
```json
{
  "experiment_id": "exp-blacksky-001",
  "scenario_name": "black_sky",
  "max_episodes": 5,
  "steps_per_episode": 100,
  "use_docker": false
}
```

**Response Example:**
```json
{
  "status": "started",
  "experiment_id": "exp-blacksky-001",
  "worker_mode": "in_process",
  "max_episodes": 5,
  "steps_per_episode": 100
}
```

#### `POST /api/v1/training/{experiment_id}/pause`
Pauses the active PPO training loop.

#### `POST /api/v1/training/{experiment_id}/resume`
Resumes paused PPO training.

#### `POST /api/v1/training/{experiment_id}/stop`
Terminates training safely and serializes checkpoint to `models/checkpoints/`.

#### `GET /api/v1/training/{experiment_id}/status`
Returns live training progress.

**Response Example:**
```json
{
  "is_running": true,
  "is_paused": false,
  "current_episode": 2,
  "current_step": 45,
  "total_timesteps": 245,
  "active_experiment_id": "exp-blacksky-001",
  "worker_mode": "in_process"
}
```

---

### 4.4 Defensive Policy & DDPS Governance

#### `GET /api/v1/policy/metadata`
Returns policy parameter dimensions, action head mappings, and hard invariants.

**Response Example:**
```json
{
  "policy_version": "m1_ppo_policy_v1",
  "algorithm": "PPO",
  "architecture": "Shared Multi-Head Actor-Critic",
  "observation_dimension": 14,
  "action_heads": 8,
  "action_levels": [0, 1, 2],
  "action_head_names": [
    "edge_rate_limit",
    "auth_throttle",
    "app_rate_limit",
    "session_ttl",
    "isolate_compromised",
    "block_lateral",
    "privilege_lockdown",
    "rollback_trigger"
  ],
  "security_invariants": [
    {"code": "OMEGA_1", "description": "Authentication service must never be disabled or unreachable"},
    {"code": "OMEGA_2", "description": "Database must never be directly reachable from DMZ or untrusted zones"},
    {"code": "OMEGA_3", "description": "Legitimate traffic throughput floor must be upheld"}
  ]
}
```

#### `GET /api/v1/policy/actions`
Query historical action proposals and their DDPS rejection reasons.

---

### 4.5 MITRE ATT&CK Catalog & Mappings

- `GET /api/mitre/techniques`: Lists container techniques with optional `tactic` and `priority` query filters.
- `GET /api/mitre/techniques/{id}`: Detailed technique documentation and mapped AEGIS defense modules.
- `GET /api/mitre/coverage`: Coverage statistics and priority tier breakdowns (P0–P3).

---

### 4.6 Experiment Reports & Evaluation

#### `GET /api/v1/experiments/{experiment_id}/report`
Provides quantitative comparative evaluation metrics and Gemma 4 AI root-cause analysis.

**Response Example:**
```json
{
  "experiment_id": "exp-live",
  "timestamp": "2026-10-31T12:00:00Z",
  "benchmark_summary": {
    "effective_availability_pct": 98.2,
    "blast_radius_factor": 0.0,
    "mean_time_to_contain_sec": 0.0,
    "resiliency_degradation_index": 1.8
  },
  "gemma_ai_explanation": {
    "incident_summary": "Concurrent L1 flood combined with L4 credential stuffing at T=30s caused cascading worker exhaustion.",
    "defensive_action_explanation": "Agent elevated edge rate-limiting and throttled auth requests, shielding the core DB.",
    "invariant_status": "All invariants upheld. No unauthorized DB access permitted.",
    "comparative_assessment": "Adaptive policy achieved 98.2% availability vs 39.8% for baseline.",
    "policy_outcome": "Successful containment under 0.5s."
  }
}
```

---

## 5. WebSocket Telemetry Stream

### 5.1 Connection
- **Endpoint:** `ws://localhost:8000/ws/v1/experiments/{experiment_id}`
- **Protocol:** JSON messages streamed at each simulation step (10 Hz).

### 5.2 Handshake Message
Upon connecting, the server sends an immediate handshake:
```json
{
  "event_type": "websocket.connected",
  "experiment_id": "exp-live",
  "timestamp": "connected"
}
```

### 5.3 Live Telemetry Frame Schema (`environment.telemetry`)
Streamed continuously across all 4 environments simultaneously:
```json
{
  "event_type": "environment.telemetry",
  "experiment_id": "exp-live",
  "episode": 1,
  "step": 35,
  "workers": {
    "env_a_baseline": {
      "observation": [0.85, 0.42, 0.12, 0.95, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
      "reward": -42.5,
      "metrics": {
        "effective_availability_pct": 39.8,
        "blast_radius_factor": 0.12,
        "active_incidents": 2
      }
    },
    "env_b_adaptive": {
      "observation": [0.12, 0.05, 0.00, 0.10, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
      "reward": 18.2,
      "metrics": {
        "effective_availability_pct": 98.2,
        "blast_radius_factor": 0.00,
        "active_incidents": 0
      }
    },
    "env_c_hardened": {
      "observation": [0.15, 0.08, 0.00, 0.12, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
      "reward": 12.0,
      "metrics": {
        "effective_availability_pct": 96.5,
        "blast_radius_factor": 0.00,
        "active_incidents": 0
      }
    },
    "env_d_experimental": {
      "observation": [0.35, 0.22, 0.00, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
      "reward": 4.5,
      "metrics": {
        "effective_availability_pct": 74.8,
        "blast_radius_factor": 0.00,
        "active_incidents": 1
      }
    }
  }
}
```

---

## 6. Error Response Conventions

All backend endpoints adhere to RFC 7807 problem details / standard FastAPI HTTPException format:
```json
{
  "detail": "Descriptive human-readable error explanation."
}
```

**Common Status Codes:**
- `200 OK`: Request succeeded.
- `400 Bad Request`: Schema validation error or invalid parameter range.
- `404 Not Found`: Target environment ID, scenario, or experiment ID not found.
- `409 Conflict`: Attempting to start training when another training session is active.
- `500 Internal Server Error`: Unhandled system failure.
