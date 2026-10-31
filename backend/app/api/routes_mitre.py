"""
FastAPI Routes for MITRE ATT&CK Catalog & AEGIS Mapping.
Endpoints:
- GET /api/mitre/techniques
- GET /api/mitre/techniques/{id}
- GET /api/mitre/coverage
- POST /api/mitre/import
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.db.postgres import get_db
from backend.db.models import MitreTechnique, MitreMapping, MitreCatalogVersion
from backend.mitre.importer import import_container_techniques

router = APIRouter(prefix="/api/mitre", tags=["MITRE ATT&CK"])


@router.get("/techniques")
def list_techniques(
    tactic: Optional[str] = Query(None, description="Filter by MITRE tactic name"),
    status: Optional[str] = Query(None, description="Filter by implementation status"),
    priority: Optional[str] = Query(None, description="Filter by priority tier (P0, P1, P2, P3)"),
    db: Session = Depends(get_db)
):
    """List imported MITRE ATT&CK Container techniques with optional filters."""
    query = db.query(MitreTechnique).outerjoin(MitreMapping)

    if priority:
        query = query.filter(MitreMapping.priority_tier == priority)
    if status:
        query = query.filter(MitreMapping.implementation_status == status)

    techniques = query.all()

    results = []
    for tech in techniques:
        # Tactic filter (stored as JSON array)
        if tactic and tactic.lower() not in [t.lower() for t in (tech.tactics or [])]:
            continue

        mapping = tech.mapping
        results.append({
            "technique_id": tech.technique_id,
            "name": tech.name,
            "tactics": tech.tactics,
            "platforms": tech.platforms,
            "is_subtechnique": tech.is_subtechnique,
            "parent_technique_id": tech.parent_technique_id,
            "mitre_url": tech.mitre_url,
            "aegis_mapping": {
                "priority_tier": mapping.priority_tier if mapping else "P2",
                "scenario_id": mapping.scenario_id if mapping else None,
                "detector_id": mapping.detector_id if mapping else None,
                "defense_modules": mapping.defense_modules if mapping else [],
                "simulation_mode": mapping.simulation_mode if mapping else "safe_local",
                "implementation_status": mapping.implementation_status if mapping else "not_started"
            } if mapping else None
        })

    return {
        "count": len(results),
        "techniques": results
    }


@router.get("/techniques/{technique_id}")
def get_technique_detail(technique_id: str, db: Session = Depends(get_db)):
    """Fetch complete technique metadata, STIX reference, and AEGIS mapping."""
    tech = db.query(MitreTechnique).filter(MitreTechnique.technique_id == technique_id).first()
    if not tech:
        raise HTTPException(status_code=404, detail=f"MITRE technique {technique_id} not found")

    mapping = tech.mapping
    return {
        "technique_id": tech.technique_id,
        "name": tech.name,
        "description": tech.description,
        "tactics": tech.tactics,
        "platforms": tech.platforms,
        "is_subtechnique": tech.is_subtechnique,
        "parent_technique_id": tech.parent_technique_id,
        "source_version": tech.source_version,
        "mitre_url": tech.mitre_url,
        "aegis_mapping": {
            "priority_tier": mapping.priority_tier if mapping else "P2",
            "scenario_id": mapping.scenario_id if mapping else None,
            "detector_id": mapping.detector_id if mapping else None,
            "defense_modules": mapping.defense_modules if mapping else [],
            "simulation_mode": mapping.simulation_mode if mapping else "safe_local",
            "implementation_status": mapping.implementation_status if mapping else "not_started",
            "safety_bounds": mapping.safety_bounds if mapping else {},
            "notes": mapping.notes if mapping else ""
        } if mapping else None
    }


@router.get("/coverage")
def get_mitre_coverage(db: Session = Depends(get_db)):
    """Calculates implementation and verification coverage across container techniques."""
    total_techniques = db.query(MitreTechnique).count()
    mappings = db.query(MitreMapping).all()

    status_counts = {}
    priority_counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    implemented_count = 0

    for m in mappings:
        st = m.implementation_status
        status_counts[st] = status_counts.get(st, 0) + 1
        priority_counts[m.priority_tier] = priority_counts.get(m.priority_tier, 0) + 1

        if st in ("scenario_implemented", "telemetry_verified", "detection_implemented", "detection_tested", "mitigation_tested", "regression_passed"):
            implemented_count += 1

    coverage_pct = (implemented_count / total_techniques * 100.0) if total_techniques > 0 else 0.0

    return {
        "total_techniques": total_techniques,
        "implemented_techniques": implemented_count,
        "coverage_percentage": round(coverage_pct, 2),
        "status_breakdown": status_counts,
        "priority_breakdown": priority_counts
    }


@router.post("/import")
def trigger_mitre_import(version_id: str = "attack-stix-v16.1", db: Session = Depends(get_db)):
    """Imports pinned MITRE ATT&CK STIX 2.1 container snapshot into PostgreSQL."""
    try:
        imported = import_container_techniques(version_id=version_id, db_session=db)
        return {
            "status": "success",
            "imported_count": len(imported),
            "catalog_version": version_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import STIX catalog: {str(e)}")
