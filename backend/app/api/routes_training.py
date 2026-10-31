"""
FastAPI Routes for Shared RL Training Lifecycle.
Compliant with Section 6 & 10 of Master Execution Specification.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.orchestrator.training_service import trainer_service
from backend.app.environments.docker_manager import docker_manager

router = APIRouter(prefix="/api/v1/training", tags=["RL Training"])


class TrainingStartRequest(BaseModel):
    experiment_id: str = "exp-blacksky-001"
    scenario_name: str = "black_sky"
    max_episodes: int = Field(default=3, ge=1, le=100)
    steps_per_episode: int = Field(default=100, ge=10, le=1000)
    use_docker: bool = False


@router.post("/start")
def start_training(req: TrainingStartRequest):
    """Initiates shared PPO training across parallel workers."""
    worker_urls = None
    if req.use_docker:
        worker_urls = docker_manager.get_worker_urls()

    res = trainer_service.start_training(
        experiment_id=req.experiment_id,
        scenario_name=req.scenario_name,
        max_episodes=req.max_episodes,
        steps_per_episode=req.steps_per_episode,
        worker_urls=worker_urls
    )
    return res


@router.post("/{experiment_id}/pause")
def pause_training(experiment_id: str):
    return trainer_service.pause_training()


@router.post("/{experiment_id}/resume")
def resume_training(experiment_id: str):
    return trainer_service.resume_training()


@router.post("/{experiment_id}/stop")
def stop_training(experiment_id: str):
    return trainer_service.stop_training()


@router.get("/{experiment_id}/status")
def get_training_status(experiment_id: str):
    return trainer_service.get_status()
