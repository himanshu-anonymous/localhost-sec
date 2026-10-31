"""
Simulation Worker Server (Docker Environment Instance).
Compliant with Section 4 & 5 of Master Execution Specification.
Runs as a lightweight containerized worker exposing a Gymnasium-compatible HTTP interface.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.environments.network_defense_env import NetworkDefenseEnv
from backend.app.schemas.models import DefensiveActionProposal

# Environment configuration from container environment
ENV_ID = os.getenv("ENV_ID", "env_b_adaptive")
SCENARIO_NAME = os.getenv("SCENARIO_NAME", "black_sky")
POLICY_PROFILE = os.getenv("POLICY_PROFILE", None)
if POLICY_PROFILE == "none" or POLICY_PROFILE == "":
    POLICY_PROFILE = None

MAX_STEPS = int(os.getenv("MAX_STEPS", "100"))
BASE_SEED = int(os.getenv("BASE_SEED", "42"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(f"localhost.worker.{ENV_ID}")

app = FastAPI(
    title=f"localhost Simulation Worker — {ENV_ID}",
    description="Containerized Gymnasium-compatible Simulation Worker",
    version="1.0.0"
)

# Initialize the discrete network defense environment
sim_env = NetworkDefenseEnv(
    environment_id=ENV_ID,
    scenario_name=SCENARIO_NAME,
    fixed_policy_profile=POLICY_PROFILE,
    max_steps=MAX_STEPS,
    seed=BASE_SEED
)


class StepRequest(BaseModel):
    action: List[int] = Field(..., description="Action vector in {0, 1, 2}^8")


class ResetRequest(BaseModel):
    seed: Optional[int] = None


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "environment_id": ENV_ID,
        "scenario_name": sim_env.scenario_name,
        "policy_profile": sim_env.fixed_policy_profile,
        "step": sim_env.current_step,
        "sim_time_s": sim_env.sim_time_s,
        "episode_id": sim_env.episode_id
    }


@app.post("/reset")
def reset_environment(req: Optional[ResetRequest] = None):
    seed = req.seed if req and req.seed is not None else None
    obs, info = sim_env.reset(seed=seed)
    return {
        "environment_id": ENV_ID,
        "observation": obs.tolist(),
        "info": info
    }


@app.post("/step")
def step_environment(req: StepRequest):
    if len(req.action) != 8:
        raise HTTPException(status_code=400, detail=f"Expected 8 action values, got {len(req.action)}")
    
    obs, reward, terminated, truncated, info = sim_env.step(req.action)
    return {
        "environment_id": ENV_ID,
        "observation": obs.tolist(),
        "reward": float(reward),
        "terminated": bool(terminated),
        "truncated": bool(truncated),
        "info": info
    }


@app.get("/observation")
def get_current_observation():
    obs = sim_env.last_observation
    if obs is None:
        obs, _ = sim_env.reset()
    return {
        "environment_id": ENV_ID,
        "observation": obs.tolist(),
        "step": sim_env.current_step
    }


@app.get("/status")
def get_detailed_status():
    nodes = {nid: n.model_dump() for nid, n in sim_env.topology.get_all_nodes().items()}
    active_incidents = [
        inc.model_dump() for inc in sim_env.scenario.get_active_incidents(sim_env.sim_time_s)
    ]
    info = sim_env._get_info()
    return {
        "environment_id": ENV_ID,
        "step": sim_env.current_step,
        "sim_time_s": sim_env.sim_time_s,
        "nodes": nodes,
        "active_incidents": active_incidents,
        "enforced_policy": info["enforced_policy"],
        "metrics": info["metrics"],
        "ddps_audit_count": len(sim_env.ddps.audit_log),
        "ddps_rejected_count": sim_env.ddps.rejected_count
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting simulation worker {ENV_ID} on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
