"""
Test suite for Simulation Worker Server and Remote Worker Adapter.
Compliant with Section 4, 5 & 14 of Master Execution Specification.
Verifies container worker interface contract over HTTP/REST.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.worker_server import app as worker_app
from backend.app.environments.remote_worker_adapter import RemoteWorkerEnv

worker_client = TestClient(worker_app)


def test_worker_server_endpoints():
    # 1. Health check
    resp_health = worker_client.get("/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["status"] == "healthy"

    # 2. Reset
    resp_reset = worker_client.post("/reset", json={"seed": 42})
    assert resp_reset.status_code == 200
    data_reset = resp_reset.json()
    assert "observation" in data_reset
    assert len(data_reset["observation"]) == 14

    # 3. Step
    resp_step = worker_client.post("/step", json={"action": [1, 1, 1, 1, 1, 1, 1, 1]})
    assert resp_step.status_code == 200
    data_step = resp_step.json()
    assert "reward" in data_step
    assert "observation" in data_step
    assert len(data_step["observation"]) == 14
    assert data_step["terminated"] is False

    # 4. Status
    resp_status = worker_client.get("/status")
    assert resp_status.status_code == 200
    data_status = resp_status.json()
    assert "nodes" in data_status
    assert "metrics" in data_status


def test_worker_rejection_of_malformed_actions():
    # Action vector must be exactly length 8
    resp_bad = worker_client.post("/step", json={"action": [1, 2, 3]})
    assert resp_bad.status_code == 400
    assert "Expected 8 action values" in resp_bad.json()["detail"]
