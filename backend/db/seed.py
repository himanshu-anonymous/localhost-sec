"""
Initial Seeding Script for localhost (BASTION X / AEGIS).
Seeds:
- Environments ENV-A, ENV-B, ENV-C, ENV-D
- Core Attack Scenarios (T1110, T1498, T1613, T1046, T1550)
- Canonical Topology Templates
- Default Roles & Administrative User
"""

from typing import Optional
from sqlalchemy.orm import Session
from backend.db.postgres import SessionLocal
from backend.db.models import User, Role, UserRole, Environment, AttackScenario
from backend.mitre.importer import import_container_techniques
from backend.app.topology.network_graph import NetworkTopology

_topo = NetworkTopology()
CANONICAL_TOPOLOGY_TEMPLATE = {
    "nodes": [
        {"node_id": n.id, "name": n.name, "role": n.id, "zone": f"layer_{n.layer}"}
        for n in _topo.nodes.values()
    ],
    "edges": [
        {"source": src, "target": tgt, "port": 80, "rate_limit_rps": 100}
        for src, tgt in _topo.permitted_edges
    ]
}


def seed_database(db_session: Optional[Session] = None) -> dict:
    """Seeds database with environments, scenarios, roles, and initial catalog."""
    should_close = False
    session = db_session
    if session is None:
        session = SessionLocal()
        should_close = True

    try:
        # 1. Seed Roles
        for role_name in ["admin", "operator", "analyst", "auditor"]:
            if not session.query(Role).filter_by(role_name=role_name).first():
                session.add(Role(role_name=role_name))
        session.flush()

        # 2. Seed Default Admin User
        admin = session.query(User).filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@localhost.internal",
                password_hash="sha256$hashed_admin_password",
                is_active=True
            )
            session.add(admin)
            session.flush()
            admin_role = session.query(Role).filter_by(role_name="admin").first()
            if admin_role:
                session.add(UserRole(user_id=admin.user_id, role_id=admin_role.role_id))

        # 3. Import MITRE Containers STIX techniques first so foreign keys resolve
        import_container_techniques(db_session=session)

        # 4. Seed Environments ENV-A .. ENV-D
        environments_spec = [
            {
                "id": "ENV-A",
                "name": "Static Baseline Cyber-Range",
                "mode": "static_baseline",
                "description": "Baseline fixed permissive network defense policy with standard rate limits."
            },
            {
                "id": "ENV-B",
                "name": "Adaptive DDPS RL Cyber-Range",
                "mode": "adaptive_rl",
                "description": "Adaptive multi-layer defensive policy stack managed by shared PPO reinforcement learning."
            },
            {
                "id": "ENV-C",
                "name": "Hardened Strict Cyber-Range",
                "mode": "hardened_strict",
                "description": "Zero-trust hardened posture with tight rate limits and proactive boundary segmentation."
            },
            {
                "id": "ENV-D",
                "name": "Experimental Heuristic Cyber-Range",
                "mode": "experimental",
                "description": "Experimental heuristic defense policy tested against novel multi-stage synthetic attacks."
            }
        ]

        for env_def in environments_spec:
            env = session.query(Environment).filter_by(environment_id=env_def["id"]).first()
            if not env:
                env = Environment(
                    environment_id=env_def["id"],
                    name=env_def["name"],
                    mode=env_def["mode"],
                    description=env_def["description"],
                    baseline_topology_template=CANONICAL_TOPOLOGY_TEMPLATE,
                    baseline_policy_config={"rate_limit_rps": 100, "auth_throttle": 10, "session_ttl": 3600}
                )
                session.add(env)

        # 5. Seed Attack Scenarios
        scenarios_spec = [
            {
                "id": "brute_force",
                "technique_id": "T1110",
                "name": "Distributed Credential Stuffing & Brute Force",
                "target_service": "auth_svc",
                "duration": 60,
                "rate": 80
            },
            {
                "id": "bounded_http_load",
                "technique_id": "T1498",
                "name": "Bounded Network HTTP DoS Surge",
                "target_service": "edge_gw",
                "duration": 60,
                "rate": 120
            },
            {
                "id": "container_discovery",
                "technique_id": "T1613",
                "name": "Container & Infrastructure Resource Reconnaissance",
                "target_service": "runner",
                "duration": 45,
                "rate": 30
            },
            {
                "id": "service_discovery",
                "technique_id": "T1046",
                "name": "Internal Lateral Service Port Scanning",
                "target_service": "app_svc",
                "duration": 45,
                "rate": 40
            },
            {
                "id": "synthetic_session_replay",
                "technique_id": "T1550",
                "name": "Synthetic JWT Replay & Credential Alternate Abuse",
                "target_service": "app_gw",
                "duration": 30,
                "rate": 20
            }
        ]

        for sc in scenarios_spec:
            scenario = session.query(AttackScenario).filter_by(scenario_id=sc["id"]).first()
            if not scenario:
                scenario = AttackScenario(
                    scenario_id=sc["id"],
                    technique_id=sc["technique_id"],
                    name=sc["name"],
                    target_service=sc["target_service"],
                    max_duration_seconds=sc["duration"],
                    max_request_rate_rps=sc["rate"],
                    default_parameters={}
                )
                session.add(scenario)

        session.commit()
        return {
            "status": "seeded",
            "environments": len(environments_spec),
            "scenarios": len(scenarios_spec)
        }
    except Exception as e:
        session.rollback()
        raise e
    finally:
        if should_close:
            session.close()


if __name__ == "__main__":
    result = seed_database()
    print("Database seeding completed:", result)
