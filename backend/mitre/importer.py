"""
MITRE ATT&CK STIX 2.1 Importer for localhost (BASTION X / AEGIS).
Ingests pinned STIX Enterprise Containers techniques and binds project AEGIS mappings into PostgreSQL.
"""

import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.db.postgres import SessionLocal
from backend.db.models import MitreCatalogVersion, MitreTechnique, MitreMapping

BASE_DIR = Path(__file__).parent
STIX_FILE = BASE_DIR / "data" / "enterprise-attack.json"
MAPPING_FILE = BASE_DIR / "aegis-mapping.json"
ATTACK_URL = "https://attack.mitre.org/techniques/{}/"


def compute_sha256(filepath: Path) -> str:
    digest = hashlib.sha256()
    with filepath.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def external_attack_id(obj: dict) -> Optional[str]:
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id")
    return None


def import_container_techniques(
    version_id: str = "attack-stix-v16.1",
    db_session: Optional[Session] = None
) -> List[Dict[str, Any]]:
    """Imports STIX 2.1 ATT&CK Containers techniques and binds AEGIS mappings."""
    if not STIX_FILE.exists():
        raise FileNotFoundError(f"Missing ATT&CK dataset: {STIX_FILE}")

    stix_hash = compute_sha256(STIX_FILE)
    bundle = json.loads(STIX_FILE.read_text(encoding="utf-8"))
    aegis_map = (
        json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
        if MAPPING_FILE.exists()
        else {}
    )

    records = []
    for obj in bundle.get("objects", []):
        if obj.get("type") != "attack-pattern":
            continue
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue
        platforms = obj.get("x_mitre_platforms", [])
        if "Containers" not in platforms:
            continue

        tech_id = external_attack_id(obj)
        if not tech_id:
            continue

        is_sub = obj.get("x_mitre_is_subtechnique", False)
        parent_id = tech_id.split(".")[0] if is_sub and "." in tech_id else None
        tactics = [
            phase.get("phase_name")
            for phase in obj.get("kill_chain_phases", [])
            if phase.get("kill_chain_name") == "mitre-attack"
        ]

        records.append({
            "technique_id": tech_id,
            "parent_technique_id": parent_id,
            "name": obj.get("name", tech_id),
            "description": obj.get("description", ""),
            "tactics": tactics,
            "platforms": platforms,
            "is_subtechnique": is_sub,
            "source_modified": None,  # Will parse or default in ORM
            "source_version": version_id,
            "mitre_url": ATTACK_URL.format(tech_id.replace(".", "/")),
        })

    # Sort parents before subtechniques
    records.sort(key=lambda item: (item["is_subtechnique"], item["technique_id"]))

    should_close = False
    session = db_session
    if session is None:
        session = SessionLocal()
        should_close = True

    try:
        # 1. Upsert catalog version
        catalog_ver = session.query(MitreCatalogVersion).filter_by(version_id=version_id).first()
        if not catalog_ver:
            catalog_ver = MitreCatalogVersion(
                version_id=version_id,
                stix_sha256=stix_hash,
                source_url="https://github.com/mitre-attack/attack-stix-data",
                git_commit_tag=version_id,
                technique_count=len(records)
            )
            session.add(catalog_ver)
            session.flush()

        # 2. Upsert techniques and mappings
        for rec in records:
            tech = session.query(MitreTechnique).filter_by(technique_id=rec["technique_id"]).first()
            if not tech:
                tech = MitreTechnique(
                    technique_id=rec["technique_id"],
                    parent_technique_id=rec["parent_technique_id"],
                    name=rec["name"],
                    description=rec["description"],
                    tactics=rec["tactics"],
                    platforms=rec["platforms"],
                    is_subtechnique=rec["is_subtechnique"],
                    source_version=rec["source_version"],
                    mitre_url=rec["mitre_url"]
                )
                session.add(tech)
            else:
                tech.name = rec["name"]
                tech.description = rec["description"]
                tech.tactics = rec["tactics"]
                tech.platforms = rec["platforms"]
                tech.source_version = rec["source_version"]
                tech.mitre_url = rec["mitre_url"]

            session.flush()

            cfg = aegis_map.get(rec["technique_id"], {})
            mapping = session.query(MitreMapping).filter_by(technique_id=rec["technique_id"]).first()
            if not mapping:
                mapping = MitreMapping(
                    technique_id=rec["technique_id"],
                    priority_tier=cfg.get("priority_tier", "P2"),
                    scenario_id=cfg.get("scenario_id"),
                    detector_id=cfg.get("detector_id"),
                    defense_modules=cfg.get("defense_modules", []),
                    simulation_mode=cfg.get("simulation_mode", "safe_local"),
                    implementation_status=cfg.get("implementation_status", "catalog_imported"),
                    safety_bounds={},
                    notes=""
                )
                session.add(mapping)
            else:
                mapping.priority_tier = cfg.get("priority_tier", mapping.priority_tier)
                mapping.scenario_id = cfg.get("scenario_id", mapping.scenario_id)
                mapping.detector_id = cfg.get("detector_id", mapping.detector_id)
                mapping.defense_modules = cfg.get("defense_modules", mapping.defense_modules)
                mapping.simulation_mode = cfg.get("simulation_mode", mapping.simulation_mode)
                mapping.implementation_status = cfg.get("implementation_status", mapping.implementation_status)

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        if should_close:
            session.close()

    return records


if __name__ == "__main__":
    imported = import_container_techniques()
    print(f"Imported {len(imported)} MITRE ATT&CK Container techniques into PostgreSQL.")
