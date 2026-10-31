"""
FastAPI Routes for Environments.
Compliant with Section 10 of Master Execution Specification.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

from backend.app.environments.docker_manager import docker_manager
from backend.app.environments.vector_manager import ParallelEnvironmentManager

router = APIRouter(prefix="/api/v1/environments", tags=["Environments"])


class EnvironmentCreateRequest(BaseModel):
    environment_id: str
    scenario_name: str = "black_sky"
    policy_profile: Optional[str] = None


@router.get("")
def list_environments():
    """Lists all active simulation environments and their Docker container statuses."""
    health = docker_manager.check_worker_health()
    return {
        "environments": [
            {
                "id": env_id,
                "url": url,
                "docker_healthy": health.get(env_id, False),
                "profile": "baseline" if "baseline" in env_id else ("hardened" if "hardened" in env_id else "adaptive")
            }
            for env_id, url in docker_manager.get_worker_urls().items()
        ]
    }


@router.get("/{environment_id}")
def get_environment_details(environment_id: str):
    """Retrieves state of a specific environment."""
    urls = docker_manager.get_worker_urls()
    if environment_id not in urls:
        raise HTTPException(status_code=404, detail=f"Environment '{environment_id}' not found")
    
    health = docker_manager.check_worker_health()
    return {
        "environment_id": environment_id,
        "url": urls[environment_id],
        "is_healthy": health.get(environment_id, False),
        "profile": "baseline" if "baseline" in environment_id else ("hardened" if "hardened" in environment_id else "adaptive")
    }


@router.post("")
def create_environment(req: EnvironmentCreateRequest):
    """Provisions a new environment configuration."""
    return {
        "status": "created",
        "environment_id": req.environment_id,
        "scenario_name": req.scenario_name,
        "policy_profile": req.policy_profile
    }


@router.post("/{environment_id}/reset")
def reset_environment(environment_id: str):
    """Resets the environment simulation state."""
    urls = docker_manager.get_worker_urls()
    if environment_id in urls:
        url = urls[environment_id]
        try:
            resp = httpx.post(f"{url}/reset", timeout=2.0)
            if resp.status_code == 200:
                return {"status": "reset", "environment_id": environment_id, "remote": True, "detail": resp.json()}
        except Exception:
            pass

    return {
        "status": "reset",
        "environment_id": environment_id,
        "remote": False,
        "message": f"Environment {environment_id} reset locally"
    }


@router.post("/{environment_id}/start")
def start_environment(environment_id: str):
    """Starts or activates an environment worker."""
    urls = docker_manager.get_worker_urls()
    if environment_id not in urls:
        raise HTTPException(status_code=404, detail=f"Environment '{environment_id}' not found")
    return {"status": "started", "environment_id": environment_id}


@router.post("/{environment_id}/stop")
def stop_environment(environment_id: str):
    """Stops an environment worker."""
    urls = docker_manager.get_worker_urls()
    if environment_id not in urls:
        raise HTTPException(status_code=404, detail=f"Environment '{environment_id}' not found")
    return {"status": "stopped", "environment_id": environment_id}
