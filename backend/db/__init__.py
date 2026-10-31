"""
Database package for localhost (BASTION X).
Exports SQLAlchemy Base, engine, SessionLocal, and all ORM domain models.
"""

from backend.db.postgres import Base, SessionLocal, engine, get_db, init_db
from backend.db.models import (
    User,
    Role,
    UserRole,
    Environment,
    MitreCatalogVersion,
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

__all__ = [
    "Base",
    "SessionLocal",
    "engine",
    "get_db",
    "init_db",
    "User",
    "Role",
    "UserRole",
    "Environment",
    "MitreCatalogVersion",
    "MitreTechnique",
    "MitreMapping",
    "AttackScenario",
    "SimulationRun",
    "TelemetryMetric",
    "SecurityObservation",
    "TechniqueDetection",
    "TrainingRun",
    "RLAction",
    "ActionApproval",
    "SecurityViolation",
    "DefenseAction",
    "DefencePolicy",
    "GemmaReport",
    "EvaluationResult",
]
