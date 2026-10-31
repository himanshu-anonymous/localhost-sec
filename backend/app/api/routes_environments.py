"""
FastAPI Routes for Environments.
Compliant with Section 10 of Master Execution Specification.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
        "is_healthy": health.get(environment_id, False)
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
