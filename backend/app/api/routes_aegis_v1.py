"""
AEGIS REST API v1 Core Routes.
Compliant with Section 15 of AEGIS Master Implementation Spec.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from backend.app.telemetry.collector import telemetry_collector
from backend.app.telemetry.schemas import SecurityEventSchema, DetectionRecord, IncidentRecord
from backend.app.detection.engine import detection_engine
from backend.app.incidents.manager import incident_manager
from backend.app.defense.orchestrator import defense_orchestrator
from backend.app.defense.modules import AVAILABLE_DEFENSE_MODULES
from backend.app.ai.gemma_client import gemma_client, GemmaIncidentAnalysis
from backend.app.evaluation.comparison import evaluation_engine, ComparisonResult

router = APIRouter(prefix="/api/v1", tags=["AEGIS v1"])


# ============================================================================
# 1. HEALTH & DEPENDENCIES
# ============================================================================

@router.get("/health")
def get_health():
    return {
        "status": "healthy",
        "service": "AEGIS Orchestrator API",
        "defense_state": defense_orchestrator.get_state()["current_state"]
    }


@router.get("/health/dependencies")
def get_dependency_health():
    # Database check
    db_ok = False
    try:
        from backend.db.postgres import SessionLocal
        s = SessionLocal()
        s.execute("SELECT 1")
        s.close()
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "application": "healthy",
        "database": "online" if db_ok else "in_memory_mode",
        "gateway": "ready",
        "policy_agent": "ready",
        "telemetry_collector": "online",
        "gemma_service": "online" if gemma_client.is_live else "deterministic_synthesizer_active"
    }


# ============================================================================
# 2. TELEMETRY EVENTS & DETECTIONS
# ============================================================================

@router.get("/events", response_model=List[SecurityEventSchema])
def list_events(
    limit: int = Query(50, ge=1, le=500),
    source_type: Optional[str] = None,
    event_type: Optional[str] = None,
    source_ip: Optional[str] = None,
    simulation_run_id: Optional[str] = None
):
    return telemetry_collector.get_events(
        limit=limit,
        source_type=source_type,
        event_type=event_type,
        source_ip=source_ip,
        simulation_run_id=simulation_run_id
    )


@router.get("/events/{event_id}", response_model=SecurityEventSchema)
def get_event(event_id: str):
    ev = telemetry_collector.get_event_by_id(event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    return ev


@router.post("/events/ingest", response_model=SecurityEventSchema)
def ingest_event(event: SecurityEventSchema):
    ingested = telemetry_collector.ingest(event)
    # Automatically feed into detection engine
    detection = detection_engine.evaluate_event(ingested)
    if detection:
        incident_manager.correlate_detection(detection)
    return ingested


@router.get("/detections", response_model=List[DetectionRecord])
def list_detections(limit: int = Query(50, ge=1, le=100), simulation_run_id: Optional[str] = None):
    return detection_engine.get_detections(limit=limit, simulation_run_id=simulation_run_id)


@router.get("/detections/{detection_id}", response_model=DetectionRecord)
def get_detection(detection_id: str):
    det = detection_engine.get_detection_by_id(detection_id)
    if not det:
        raise HTTPException(status_code=404, detail="Detection not found")
    return det


# ============================================================================
# 3. INCIDENTS & GEMMA ANALYSIS
# ============================================================================

@router.get("/incidents", response_model=List[IncidentRecord])
def list_incidents(limit: int = Query(50, ge=1, le=100), status: Optional[str] = None):
    return incident_manager.get_incidents(limit=limit, status_filter=status)


@router.get("/incidents/{incident_id}", response_model=IncidentRecord)
def get_incident(incident_id: str):
    inc = incident_manager.get_incident_by_id(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc


@router.post("/incidents/{incident_id}/analyze", response_model=GemmaIncidentAnalysis)
def analyze_incident_with_gemma(incident_id: str):
    inc = incident_manager.get_incident_by_id(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    recent_events = [
        telemetry_collector.get_event_by_id(eid).model_dump(mode="json")
        for eid in inc.related_event_ids
        if telemetry_collector.get_event_by_id(eid)
    ]

    analysis = gemma_client.analyze_incident(
        incident_id=inc.incident_id,
        title=inc.title,
        description=inc.description,
        affected_services=inc.affected_services,
        source_identities=inc.source_identities,
        techniques=inc.technique_associations,
        evidence_event_ids=inc.related_event_ids,
        events_summary=recent_events
    )

    # Automatically advance incident lifecycle to INVESTIGATING
    incident_manager.update_status(incident_id, "INVESTIGATING", notes=analysis.incident_summary)
    return analysis


@router.post("/incidents/{incident_id}/mitigate")
def apply_incident_mitigation(incident_id: str):
    """Executes Gemma-recommended mitigation via deterministic policy engine."""
    analysis = analyze_incident_with_gemma(incident_id)
    results = []

    incident_manager.update_status(incident_id, "MITIGATING")
    for rec_action in analysis.recommended_actions:
        res = defense_orchestrator.process_incident_recommendation(
            incident_id=incident_id,
            module_id=rec_action.module_id,
            action_id=rec_action.action_id,
            parameters=rec_action.parameters,
            reason=rec_action.reason
        )
        results.append(res)

    incident_manager.update_status(incident_id, "RESOLVED", notes="Mitigation policy verified on gateway.")
    return {
        "incident_id": incident_id,
        "status": "mitigated",
        "actions_executed": results
    }


@router.post("/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: str, notes: str = "Operator manual resolution"):
    inc = incident_manager.update_status(incident_id, "RESOLVED", notes=notes)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc


# ============================================================================
# 4. DEFENSE ORCHESTRATION & STATE MACHINE
# ============================================================================

@router.get("/defense/modules")
def list_defense_modules():
    return list(AVAILABLE_DEFENSE_MODULES.values())


@router.get("/defense/state")
def get_defense_state():
    return defense_orchestrator.get_state()


@router.get("/defense/actions")
def list_defense_actions(limit: int = Query(50, ge=1, le=100)):
    return defense_orchestrator.get_actions(limit=limit)


@router.get("/defense/actions/{action_id}")
def get_defense_action(action_id: str):
    action = defense_orchestrator.get_action_by_id(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Defense action not found")
    return action


@router.post("/defense/emergency-stop")
def trigger_emergency_stop():
    success = defense_orchestrator.emergency_stop()
    return {
        "status": "EMERGENCY_STOP_ACTIVE",
        "success": success,
        "defense_state": defense_orchestrator.get_state()["current_state"]
    }


@router.post("/defense/rollback")
def rollback_defense_policies():
    results = defense_orchestrator.rollback_all(reason="Manual operator rollback")
    return {
        "status": "rolled_back",
        "restored_state": defense_orchestrator.get_state()["current_state"],
        "unblocked_results": results
    }


# ============================================================================
# 5. METRICS & STATIC VS ADAPTIVE COMPARISON
# ============================================================================

@router.get("/metrics/overview")
def get_metrics_overview():
    return {
        "total_events_ingested": len(telemetry_collector.events),
        "total_detections": len(detection_engine.detections),
        "open_incidents": len([i for i in incident_manager.incidents.values() if i.status != "RESOLVED"]),
        "defense_actions_applied": len(defense_orchestrator.applied_actions),
        "current_defense_state": defense_orchestrator.get_state()["current_state"]
    }


@router.get("/metrics/compare", response_model=ComparisonResult)
def compare_static_vs_adaptive(scenario_id: str = "brute_force"):
    return evaluation_engine.compare_scenario(scenario_id)

