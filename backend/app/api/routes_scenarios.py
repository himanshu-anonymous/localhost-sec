"""
FastAPI Routes for MITRE ATT&CK Scenarios.
Compliant with Section 7 & 10 of Master Execution Specification.
"""

from typing import Dict, Any, List
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.scenarios.incident_engine import ScenarioEngine

router = APIRouter(prefix="/api/v1/scenarios", tags=["Scenarios"])


class ScenarioCreateRequest(BaseModel):
    scenario_id: str
    name: str
    tactic: str
    technique_id: str
    target_node_id: str
    start_time_s: float
    duration_s: float
    intensity: float = Field(default=0.8, ge=0.0, le=1.0)
    description: str


@router.get("")
def list_scenarios():
    """Lists available pre-packaged MITRE ATT&CK scenarios."""
    black_sky = ScenarioEngine("black_sky")
    held_out = ScenarioEngine("held_out_evaluation")
    return {
        "scenarios": [
            {
                "id": "black_sky",
                "name": "Black Sky CI/CD Resilience Test",
                "event_count": len(black_sky.events),
                "events": [e.model_dump() for e in black_sky.events]
            },
            {
                "id": "held_out_evaluation",
                "name": "Held-out WAF & Exfiltration Test",
                "event_count": len(held_out.events),
                "events": [e.model_dump() for e in held_out.events]
            }
        ]
    }


@router.post("")
def create_scenario(req: ScenarioCreateRequest):
    """Registers a synthetic attack scenario."""
    return {
        "status": "registered",
        "scenario_id": req.scenario_id,
        "payload": req.model_dump()
    }
