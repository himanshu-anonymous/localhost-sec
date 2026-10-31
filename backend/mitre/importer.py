import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).parent
    /"enterprise-attack"
    / "enterprise-attack.json"
)

ATTACK_URL = "https://attack.mitre.org/techniques/{}/"


def external_attack_id(obj):
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id")
    return None


def import_container_techniques():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Missing ATT&CK dataset: {DATA_FILE}"
        )

    with DATA_FILE.open("r", encoding="utf-8") as file:
        bundle = json.load(file)

    objects = bundle.get("objects", [])
    results = []

    for obj in objects:
        if obj.get("type") != "attack-pattern":
            continue

        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue

        platforms = obj.get("x_mitre_platforms", [])

        if "Containers" not in platforms:
            continue

        technique_id = external_attack_id(obj)

        if not technique_id:
            continue

        tactics = [
            phase.get("phase_name")
            for phase in obj.get("kill_chain_phases", [])
            if phase.get("kill_chain_name") == "mitre-attack"
        ]

        results.append({
            "technique_id": technique_id,
            "name": obj.get("name"),
            "description": obj.get("description", ""),
            "platforms": platforms,
            "tactics": tactics,
            "is_subtechnique": obj.get(
                "x_mitre_is_subtechnique", False
            ),
            "url": ATTACK_URL.format(technique_id),
            "modified": obj.get("modified"),
        })

    results.sort(key=lambda item: item["technique_id"])

    output_file = DATA_FILE.parent / "containers-techniques.json"
    output_file.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print(f"Imported {len(results)} Containers techniques.")
    print(f"Output: {output_file}")

    return results


if __name__ == "__main__":
    import_container_techniques()