"""
FastAPI Routes for Policy, Checkpoint, and DDPS Action History.
Compliant with Section 7 & 9 of Master Execution Specification.
"""

import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.db.postgres import get_db
from backend.db.models import ActionApproval, RLAction, SecurityViolation, DefencePolicy
from backend.app.orchestrator.training_service import trainer_service

router = APIRouter(prefix="/api/v1/policy", tags=["Defensive Policy & DDPS"])


@router.get("/metadata")
def get_policy_metadata():
    """Returns policy version, model architecture, action bounds, and hard invariants."""
    return {
        "policy_version": "m1_ppo_policy_v1",
        "algorithm": "PPO (Proximal Policy Optimization)",
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
            {"code": "OMEGA_3", "description": "Legitimate traffic throughput floor must be upheld (never drop below minimum threshold)"},
            {"code": "OMEGA_4", "description": "Admin control plane access must enforce multi-factor privilege invariant"},
            {"code": "OMEGA_5", "description": "Microsegmentation links must not be severed without fallback route for essential telemetry"}
        ]
    }


@router.get("/checkpoint")
def get_policy_checkpoint():
    """Returns active model checkpoint path, size, and parameter information."""
    checkpoint_path = "models/checkpoints/m1_ppo_policy.pt"
    exists = os.path.exists(checkpoint_path)
    size_bytes = os.path.getsize(checkpoint_path) if exists else 0

    return {
        "checkpoint_path": checkpoint_path,
        "exists": exists,
        "size_bytes": size_bytes,
        "last_modified": os.path.getmtime(checkpoint_path) if exists else None,
        "model_summary": {
            "obs_dim": trainer_service.agent.obs_dim,
            "num_actions": trainer_service.agent.num_actions,
            "action_levels": trainer_service.agent.action_levels
        }
    }


@router.get("/actions")
def get_action_history(
    limit: int = Query(50, le=200),
    decision: Optional[str] = Query(None, description="Filter by decision: approved, rejected, escalated_to_human"),
    db: Session = Depends(get_db)
):
    """Returns history of proposed, approved, and rejected actions with DDPS reasons."""
    results = []
    try:
        query = db.query(ActionApproval).order_by(ActionApproval.validated_at.desc())
        if decision:
            query = query.filter(ActionApproval.ddps_decision == decision)
        approvals = query.limit(limit).all()

        for app in approvals:
            results.append({
                "approval_id": str(app.approval_id),
                "run_id": str(app.run_id),
                "decision": app.ddps_decision,
                "rejection_reason": app.rejection_reason,
                "schema_valid": app.schema_valid,
                "parameter_bounds_valid": app.parameter_bounds_valid,
                "security_invariant_valid": app.security_invariant_valid,
                "stability_check_valid": app.stability_check_valid,
                "validated_at": app.validated_at.isoformat() if app.validated_at else None
            })
    except Exception:
        results = []

    return {
        "count": len(results),
        "actions": results
    }
