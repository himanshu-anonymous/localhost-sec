"""
Integration test suite for FastAPI API Endpoints and WebSocket streaming.
Compliant with Section 10 & 14 of Master Execution Specification.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["project"] == "localhost (BASTION X)"
    assert data["status"] == "online"
    assert "docker_workers" in data


def test_environments_endpoints():
    # GET /api/v1/environments
    resp = client.get("/api/v1/environments")
    assert resp.status_code == 200
    data = resp.json()
    assert "environments" in data
    assert len(data["environments"]) == 4

    # GET /api/v1/environments/{id}
    resp_single = client.get("/api/v1/environments/env_b_adaptive")
    assert resp_single.status_code == 200
    assert resp_single.json()["environment_id"] == "env_b_adaptive"

    # POST /api/v1/environments/{id}/reset
    resp_reset = client.post("/api/v1/environments/env_b_adaptive/reset")
    assert resp_reset.status_code == 200
    assert resp_reset.json()["status"] == "reset"

    # POST /api/v1/environments/{id}/start & stop
    resp_start = client.post("/api/v1/environments/env_b_adaptive/start")
    assert resp_start.status_code == 200
    resp_stop = client.post("/api/v1/environments/env_b_adaptive/stop")
    assert resp_stop.status_code == 200


def test_scenarios_endpoints():
    # GET /api/v1/scenarios
    resp = client.get("/api/v1/scenarios")
    assert resp.status_code == 200
    data = resp.json()
    assert "scenarios" in data
    ids = [s["id"] for s in data["scenarios"]]
    assert "black_sky" in ids
    assert "held_out_evaluation" in ids


def test_training_lifecycle_endpoints():
    # GET /api/v1/training/{id}/status
    resp_status = client.get("/api/v1/training/exp-test-01/status")
    assert resp_status.status_code == 200
    assert "is_running" in resp_status.json()

    # POST /api/v1/training/start
    resp_start = client.post("/api/v1/training/start", json={
        "experiment_id": "exp-test-01",
        "scenario_name": "black_sky",
        "max_episodes": 1,
        "steps_per_episode": 10,
        "use_docker": False
    })
    assert resp_start.status_code == 200

    # POST /api/v1/training/{id}/pause
    resp_pause = client.post("/api/v1/training/exp-test-01/pause")
    assert resp_pause.status_code == 200

    # POST /api/v1/training/{id}/resume
    resp_resume = client.post("/api/v1/training/exp-test-01/resume")
    assert resp_resume.status_code == 200

    # POST /api/v1/training/{id}/stop
    resp_stop = client.post("/api/v1/training/exp-test-01/stop")
    assert resp_stop.status_code == 200


def test_policy_metadata_and_checkpoint_endpoints():
    # GET /api/v1/policy/metadata
    resp_meta = client.get("/api/v1/policy/metadata")
    assert resp_meta.status_code == 200
    meta = resp_meta.json()
    assert meta["algorithm"] == "PPO (Proximal Policy Optimization)"
    assert meta["observation_dimension"] == 14
    assert meta["action_heads"] == 8
    assert len(meta["security_invariants"]) == 5

    # GET /api/v1/policy/checkpoint
    resp_ckpt = client.get("/api/v1/policy/checkpoint")
    assert resp_ckpt.status_code == 200
    ckpt = resp_ckpt.json()
    assert "checkpoint_path" in ckpt
    assert "exists" in ckpt

    # GET /api/v1/policy/actions
    resp_act = client.get("/api/v1/policy/actions")
    assert resp_act.status_code == 200
    assert "actions" in resp_act.json()


def test_metrics_and_report_endpoints():
    resp_metrics = client.get("/api/v1/metrics/exp-test-01")
    assert resp_metrics.status_code == 200

    resp_report = client.get("/api/v1/experiments/exp-test-01/report")
    assert resp_report.status_code == 200
    data = resp_report.json()
    assert "benchmark_summary" in data
    assert "gemma_ai_explanation" in data


def test_websocket_telemetry_connection():
    with client.websocket_connect("/ws/v1/experiments/exp-test-ws") as websocket:
        # Check initial connection and receive backlog message
        data = websocket.receive_json()
        assert "event_type" in data or "workers" in data or "timestamp" in data
