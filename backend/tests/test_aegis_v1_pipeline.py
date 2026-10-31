"""
Automated Test Suite for AEGIS v1 End-to-End Adaptive Defense Architecture.
Compliant with Section 20 (Unit, Integration, E2E, and Negative Security Tests) of
AEGIS Master Implementation Spec.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.telemetry.schemas import SecurityEventSchema
from backend.app.telemetry.normalizer import EventNormalizer
from backend.app.telemetry.collector import telemetry_collector
from backend.app.detection.engine import detection_engine
from backend.app.incidents.manager import incident_manager
from backend.app.defense.orchestrator import defense_orchestrator
from backend.app.defense.state_machine import DefenseState
from backend.app.defense.policy_engine import PolicyEngine
from backend.app.ai.gemma_client import gemma_client, GemmaIncidentAnalysis
from backend.app.evaluation.comparison import evaluation_engine
from backend.app.defense.policy_agent import policy_core

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_state():
    telemetry_collector.clear()
    detection_engine.clear()
    incident_manager.clear()
    defense_orchestrator.rollback_all(reason="Test fixture cleanup")
    yield


# ============================================================================
# 1. UNIT TESTS: NORMALIZATION & SCHEMAS
# ============================================================================

def test_event_normalizer_from_target_app():
    raw_log = '{"timestamp":"2026-10-31T10:00:00Z","source_name":"target-web","event_type":"auth_failure","source_ip":"172.31.10.15","username":"admin","status_code":401}'
    event = EventNormalizer.from_target_app_log(raw_log)
    assert event is not None
    assert event.source_type == "target_app"
    assert event.source_ip == "172.31.10.15"
    assert event.event_type == "auth_failure"


def test_event_normalizer_from_suricata():
    eve = {
        "timestamp": "2026-10-31T10:00:01Z",
        "event_type": "alert",
        "src_ip": "172.31.10.15",
        "dest_ip": "172.31.20.10",
        "proto": "TCP",
        "alert": {"signature": "AEGIS_ALERT: Auth Failure", "severity": 1}
    }
    event = EventNormalizer.from_suricata_eve(eve)
    assert event is not None
    assert event.source_type == "suricata"
    assert event.severity == "high"


# ============================================================================
# 2. UNIT TESTS: INDEPENDENT DETECTION (NO GROUND TRUTH DEPENDENCY)
# ============================================================================

def test_failed_login_detection_independent_of_ground_truth():
    test_ip = "172.31.10.33"
    detection = None
    for i in range(5):
        ev = SecurityEventSchema(
            source_type="target_app",
            source_name="target-web",
            event_type="auth_failure",
            source_ip=test_ip,
            destination_ip="172.31.20.10",
            protocol="HTTP",
            severity="warning"
        )
        detection = detection_engine.evaluate_event(ev)

    assert detection is not None
    assert detection.detector_id == "failed_login_detector"
    assert "T1110" in detection.inferred_techniques
    assert detection.confidence >= 0.90
    assert len(detection.evidence_event_ids) == 5
    assert detection.source_ip == test_ip


# ============================================================================
# 3. UNIT TESTS: INCIDENT CORRELATION
# ============================================================================

def test_incident_correlation_grouping():
    test_ip = "172.31.10.44"
    for i in range(5):
        ev = SecurityEventSchema(
            source_type="target_app",
            source_name="target-web",
            event_type="auth_failure",
            source_ip=test_ip
        )
        det = detection_engine.evaluate_event(ev)
        if det:
            inc = incident_manager.correlate_detection(det)

    open_incs = incident_manager.get_incidents()
    assert len(open_incs) == 1
    assert open_incs[0].source_identities == [test_ip]
    assert "T1110" in open_incs[0].technique_associations


# ============================================================================
# 4. UNIT & NEGATIVE TESTS: POLICY ENGINE INVARIANTS (OMEGA)
# ============================================================================

def test_policy_engine_approval():
    engine = PolicyEngine(subnet_cidr="172.31.10.0/24")
    decision = engine.validate_action(
        module_id="gateway_acl",
        action_id="block_source_ip",
        parameters={"ip_address": "172.31.10.55"}
    )
    assert decision.approved is True


def test_policy_engine_rejects_out_of_scope_ip():
    engine = PolicyEngine(subnet_cidr="172.31.10.0/24")
    decision = engine.validate_action(
        module_id="gateway_acl",
        action_id="block_source_ip",
        parameters={"ip_address": "8.8.8.8"}
    )
    assert decision.approved is False
    assert decision.invariant_violated == "OMEGA_OUT_OF_SCOPE_IP"


def test_policy_engine_rejects_control_plane_ip():
    engine = PolicyEngine(subnet_cidr="172.31.10.0/24")
    decision = engine.validate_action(
        module_id="gateway_acl",
        action_id="block_source_ip",
        parameters={"ip_address": "172.31.10.2"}
    )
    assert decision.approved is False
    assert decision.invariant_violated == "OMEGA_CRITICAL_INFRASTRUCTURE_PROTECTED"


def test_policy_engine_rejects_unknown_module():
    engine = PolicyEngine()
    decision = engine.validate_action(
        module_id="unapproved_root_module",
        action_id="wipe_disk",
        parameters={}
    )
    assert decision.approved is False
    assert decision.invariant_violated == "OMEGA_UNKNOWN_MODULE"


# ============================================================================
# 5. INTEGRATION TESTS: GEMMA AI STRUCTURED CONTRACT
# ============================================================================

def test_gemma_incident_analysis_schema():
    analysis = gemma_client.analyze_incident(
        incident_id="inc-test-01",
        title="Repeated Authentication Failures",
        description="Auth surge on login",
        affected_services=["target-web"],
        source_identities=["172.31.10.66"],
        techniques=["T1110"],
        evidence_event_ids=["ev-1", "ev-2"],
        events_summary=[]
    )
    assert isinstance(analysis, GemmaIncidentAnalysis)
    assert len(analysis.recommended_modules) > 0
    assert len(analysis.recommended_actions) > 0
    assert analysis.recommended_actions[0].module_id == "gateway_acl"


# ============================================================================
# 6. INTEGRATION TESTS: REST API ENDPOINTS
# ============================================================================

def test_api_v1_health_and_dependencies():
    r1 = client.get("/api/v1/health")
    assert r1.status_code == 200
    assert r1.json()["status"] == "healthy"

    r2 = client.get("/api/v1/health/dependencies")
    assert r2.status_code == 200
    deps = r2.json()
    assert deps["application"] == "healthy"
    assert "gateway" in deps


def test_api_v1_defense_modules_and_state():
    r_mod = client.get("/api/v1/defense/modules")
    assert r_mod.status_code == 200
    mods = r_mod.json()
    mod_ids = [m["module_id"] for m in mods]
    assert "gateway_acl" in mod_ids
    assert "rate_limiter" in mod_ids

    r_st = client.get("/api/v1/defense/state")
    assert r_st.status_code == 200
    assert r_st.json()["current_state"] == "NORMAL"


def test_api_v1_metrics_compare():
    resp = client.get("/api/v1/metrics/compare?scenario_id=brute_force")
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario_id"] == "brute_force"
    assert data["static_defense"]["mode"] == "static"
    assert data["adaptive_defense"]["mode"] == "adaptive"
    assert data["delta_summary"]["automated_mitigation_demonstrated"] is True


# ============================================================================
# 7. PRIMARY END-TO-END VERTICAL SLICE
# ============================================================================

def test_primary_e2e_vertical_slice():
    """
    Primary demonstration workflow (Section 1.1, 20.3 & 25):
    1. Ingest bounded brute force events from 172.31.10.77
    2. Detection independently triggers
    3. Incident is created
    4. Gemma analyzes and recommends action
    5. Policy engine validates and approves
    6. Orchestrator executes gateway block
    7. State machine reaches CONTAINED
    8. Rollback restores NORMAL state
    """
    attacker_ip = "172.31.10.77"

    # Step 1: Ingest 5 failed logins
    for i in range(5):
        resp = client.post("/api/v1/events/ingest", json={
            "source_type": "target_app",
            "source_name": "target-web",
            "event_type": "auth_failure",
            "source_ip": attacker_ip,
            "destination_ip": "172.31.20.10",
            "protocol": "HTTP",
            "severity": "warning",
            "metadata": {"username": "admin", "attempt": i + 1}
        })
        assert resp.status_code == 200

    # Step 2 & 3: Verify Detections and Incident
    inc_resp = client.get("/api/v1/incidents")
    assert inc_resp.status_code == 200
    incs = inc_resp.json()
    assert len(incs) >= 1
    incident = incs[-1]
    inc_id = incident["incident_id"]
    assert attacker_ip in incident["source_identities"]

    # Step 4: Gemma Analysis
    analysis_resp = client.post(f"/api/v1/incidents/{inc_id}/analyze")
    assert analysis_resp.status_code == 200
    analysis = analysis_resp.json()
    assert "T1110" in analysis["technique_assessment"][0]["technique_id"]

    # Step 5 & 6: Mitigate via Orchestrator
    mit_resp = client.post(f"/api/v1/incidents/{inc_id}/mitigate")
    assert mit_resp.status_code == 200
    mit_data = mit_resp.json()
    assert mit_data["status"] == "mitigated"
    assert mit_data["actions_executed"][0]["approved"] is True
    assert mit_data["actions_executed"][0]["execution_status"] == "applied_verified"

    # Step 7: Verify State Machine is CONTAINED
    st = defense_orchestrator.get_state()
    assert st["current_state"] == "CONTAINED"

    # Verify IP is blocked in Policy Agent
    assert attacker_ip in policy_core.blocked_ips

    # Step 8: Rollback & Recovery
    rb_resp = client.post("/api/v1/defense/rollback")
    assert rb_resp.status_code == 200
    assert rb_resp.json()["restored_state"] == "NORMAL"
    assert attacker_ip not in policy_core.blocked_ips
