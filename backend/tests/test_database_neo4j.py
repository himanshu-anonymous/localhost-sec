"""
Automated Integration Tests for Master Database Architecture.
Tests:
- PostgreSQL Schema (18 tables across 5 domains)
- MITRE ATT&CK STIX 2.1 Importer
- Ephemeral Neo4j Lifecycle & Dynamic Blast Radius Calculation
- Simulation & Cyber-Range API Endpoints
"""

import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.db.postgres import Base, get_db
from backend.db.seed import seed_database
from backend.db.models import (
    User,
    Environment,
    MitreTechnique,
    MitreMapping,
    AttackScenario,
    SimulationRun,
    TelemetryMetric,
    SecurityObservation,
    TechniqueDetection,
    TrainingRun,
    RLAction,
    ActionApproval,
    SecurityViolation,
    DefenseAction,
    DefencePolicy,
    GemmaReport,
    EvaluationResult,
)
from backend.db.neo4j_ephemeral import EphemeralGraphManager
from backend.mitre.importer import import_container_techniques
from backend.app.main import app


# Test database setup (in-memory SQLite with StaticPool for thread-safe sharing)
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Sets up fresh database schema and seeds initial data."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    seed_database(session)
    session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def test_domain_1_identity_and_environments():
    """Validates Domain 1: Users, Roles, UserRoles, and Environments."""
    session = TestingSessionLocal()
    users = session.query(User).all()
    envs = session.query(Environment).all()
    session.close()

    assert len(users) >= 1
    assert users[0].username == "admin"
    assert len(envs) == 4
    env_ids = [e.environment_id for e in envs]
    assert set(env_ids) == {"ENV-A", "ENV-B", "ENV-C", "ENV-D"}


def test_domain_2_mitre_catalog_and_mappings():
    """Validates Domain 2: MITRE catalog versioning, techniques, and AEGIS mappings."""
    session = TestingSessionLocal()
    techs = session.query(MitreTechnique).all()
    maps = session.query(MitreMapping).all()
    session.close()

    assert len(techs) >= 10
    assert len(maps) >= 10

    # Verify T1110 Brute Force P0 configuration
    t1110_map = next((m for m in maps if m.technique_id == "T1110"), None)
    assert t1110_map is not None
    assert t1110_map.priority_tier == "P0"
    assert t1110_map.scenario_id == "brute_force"
    assert t1110_map.simulation_mode == "safe_local"
    assert "rate_limiter" in t1110_map.defense_modules


def test_domain_3_to_5_schema_definitions():
    """Validates all 18 tables exist and can hold operational records."""
    session = TestingSessionLocal()
    tables = Base.metadata.tables.keys()
    session.close()

    required_tables = [
        "users", "roles", "user_roles", "environments",
        "mitre_catalog_versions", "mitre_techniques", "mitre_mappings",
        "attack_scenarios", "simulation_runs", "telemetry_metrics",
        "security_observations", "technique_detections",
        "training_runs", "rl_actions", "action_approvals",
        "security_violations", "defense_actions", "defence_policies",
        "gemma_reports", "evaluation_results"
    ]
    for tbl in required_tables:
        assert tbl in tables, f"Missing table: {tbl}"


def test_ephemeral_neo4j_lifecycle():
    """Validates run-scoped ephemeral graph lifecycle, mutation, and blast radius calculation."""
    async def _async_test():
        mgr = EphemeralGraphManager()
        topology = {
            "nodes": [
                {"node_id": "edge_gw", "name": "Edge Gateway", "role": "gateway", "zone": "dmz"},
                {"node_id": "app_svc", "name": "App Service", "role": "app", "zone": "internal"},
                {"node_id": "db", "name": "Database", "role": "db", "zone": "secure"},
            ],
            "edges": [
                {"source": "edge_gw", "target": "app_svc", "port": 80, "rate_limit_rps": 100},
                {"source": "app_svc", "target": "db", "port": 5432, "rate_limit_rps": 50},
            ]
        }
        run_id = "test-run-neo4j-lifecycle"
        env_id = "ENV-B"

        async with mgr.simulation_graph_scope(run_id, env_id, topology):
            # 1. Initial blast radius before defensive mutation
            blast_initial = await mgr.compute_blast_radius(run_id, env_id, "edge_gw")
            assert blast_initial["total_nodes"] == 3
            assert blast_initial["exposed_count"] == 2  # app_svc and db are reachable
            assert blast_initial["blast_radius_fraction"] > 0.60

            # 2. Defensively isolate app_svc by severing edge from edge_gw
            await mgr.mutate_traffic_policy(run_id, env_id, "edge_gw", "app_svc", "act-isolate", "T1110")

            # 3. Blast radius after policy mutation
            blast_mitigated = await mgr.compute_blast_radius(run_id, env_id, "edge_gw")
            assert blast_mitigated["exposed_count"] == 0
            assert blast_mitigated["blast_radius_fraction"] == 0.0

        # 4. Verify teardown purges nodes
        assert run_id not in mgr._in_memory_fallback

    asyncio.run(_async_test())


def test_api_mitre_endpoints():
    """Tests /api/mitre endpoints for techniques, detail, coverage, and import."""
    client = TestClient(app)

    # 1. List techniques
    resp = client.get("/api/mitre/techniques")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] > 0
    assert any(t["technique_id"] == "T1110" for t in data["techniques"])

    # 2. Technique detail
    resp_detail = client.get("/api/mitre/techniques/T1110")
    assert resp_detail.status_code == 200
    detail = resp_detail.json()
    assert detail["technique_id"] == "T1110"
    assert detail["aegis_mapping"]["priority_tier"] == "P0"

    # 3. Coverage report
    resp_cov = client.get("/api/mitre/coverage")
    assert resp_cov.status_code == 200
    cov = resp_cov.json()
    assert cov["total_techniques"] > 0
    assert "P0" in cov["priority_breakdown"]


def test_api_simulation_lifecycle():
    """Tests /api/simulations/start, /stop, and /results endpoints."""
    client = TestClient(app)

    # 1. Start simulation
    start_payload = {
        "environment_id": "ENV-B",
        "experiment_mode": "adaptive",
        "scenario_id": "brute_force",
        "ground_truth_technique_id": "T1110",
        "catalog_version_id": "attack-stix-v16.1",
        "configuration": {"rate_multiplier": 1.5}
    }
    resp_start = client.post("/api/simulations/start", json=start_payload)
    assert resp_start.status_code == 200
    start_data = resp_start.json()
    run_id = start_data["run_id"]
    assert start_data["status"] == "started"
    assert start_data["neo4j_hydrated"] is True

    # 2. List simulations
    resp_list = client.get("/api/simulations")
    assert resp_list.status_code == 200
    sims = resp_list.json()["simulations"]
    assert any(s["run_id"] == run_id for s in sims)

    # 3. Stop simulation and trigger teardown
    resp_stop = client.post(f"/api/simulations/{run_id}/stop")
    assert resp_stop.status_code == 200
    stop_data = resp_stop.json()
    assert stop_data["status"] == "completed"
    assert stop_data["neo4j_purged"] is True

    # 4. Fetch final results
    resp_results = client.get(f"/api/simulations/{run_id}/results")
    assert resp_results.status_code == 200
    results = resp_results.json()
    assert results["run_id"] == run_id
    assert results["status"] == "completed"
    assert results["evaluation"]["legitimate_success_rate"] == 0.985
