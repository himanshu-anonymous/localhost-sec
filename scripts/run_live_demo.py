"""
AEGIS Live Vertical Slice Demo Runner.
Executes the primary demo sequence compliant with Section 25 of the Master Specification.
"""

import json
import urllib.request
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000/api/v1"


def get_json(url: str) -> Dict[str, Any]:
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post_json(url: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = json.dumps(data).encode("utf-8") if data is not None else b"{}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    print("=" * 65)
    print("      AEGIS — Live Adaptive Defense Demonstration (T1110)      ")
    print("=" * 65)

    # 1. Check health
    health = get_json(f"{BASE_URL}/health")
    print(f"\n[1] Health Check: {health['status']} | Defense State: {health['defense_state']}")

    # 2. Ingest events
    target_ip = "172.31.10.15"
    print(f"\n[2] Ingesting 5 failed authentication attempts from {target_ip}...")
    for i in range(1, 6):
        ev = {
            "source_type": "target_app",
            "source_name": "target-web",
            "event_type": "auth_failure",
            "source_ip": target_ip,
            "destination_ip": "172.31.20.10",
            "protocol": "HTTP",
            "severity": "warning",
            "metadata": {"username": "admin", "attempt": i}
        }
        post_json(f"{BASE_URL}/events/ingest", ev)
    print("    [+] 5 telemetry events ingested and normalized.")

    # 3. Independent Detection
    dets = get_json(f"{BASE_URL}/detections")
    print(f"\n[3] Detection Engine Output:")
    print(f"    - Detections Generated: {len(dets)}")
    if dets:
        latest = dets[-1]
        print(f"    - Detector: {latest['detector_id']}")
        print(f"    - Inferred Techniques: {latest['inferred_techniques']}")
        print(f"    - Confidence: {latest['confidence']}")
        print(f"    - Evidence Events: {len(latest['evidence_event_ids'])}")

    # 4. Incident Correlation
    incs = get_json(f"{BASE_URL}/incidents")
    print(f"\n[4] Incident Manager Output:")
    if incs:
        inc = incs[-1]
        inc_id = inc["incident_id"]
        print(f"    - Incident ID: {inc_id}")
        print(f"    - Title: {inc['title']}")
        print(f"    - Status: {inc['status']}")
        print(f"    - Source Identities: {inc['source_identities']}")

        # 5. Gemma AI Analysis
        print(f"\n[5] Requesting Gemma AI Structured Incident Analysis...")
        analysis = post_json(f"{BASE_URL}/incidents/{inc_id}/analyze")
        print(f"    - Summary: {analysis['incident_summary']}")
        print(f"    - Recommended Modules: {analysis['recommended_modules']}")
        action = analysis["recommended_actions"][0]
        print(f"    - Recommended Action: {action['module_id']}.{action['action_id']}")
        print(f"    - Justification: {action['reason']}")

        # 6. Deterministic Policy Enforcement
        print(f"\n[6] Authorizing & Applying Mitigation via Deterministic Policy Engine...")
        mit = post_json(f"{BASE_URL}/incidents/{inc_id}/mitigate")
        executed = mit["actions_executed"][0]
        print(f"    - Policy Approved: {executed['approved']}")
        print(f"    - Execution Status: {executed['execution_status']}")
        print(f"    - Applied Action: {executed['module_id']}.{executed['action_id_name']}")

    # 7. Defense State
    st = get_json(f"{BASE_URL}/defense/state")
    print(f"\n[7] Gateway Defense State Machine:")
    print(f"    - Current State: {st['current_state']}")

    # 8. Empirical Static vs. Adaptive Comparison
    comp = get_json(f"{BASE_URL}/metrics/compare?scenario_id=brute_force")
    print(f"\n[8] Empirical Resilience Comparison (Static vs Adaptive):")
    print(f"    - Static Defense Availability:   {comp['static_defense']['benign_success_rate']*100:.1f}%")
    print(f"    - Adaptive Defense Availability: {comp['adaptive_defense']['benign_success_rate']*100:.1f}%")
    print(f"    - Automated Mitigation Time:     {comp['adaptive_defense']['mitigation_time_ms']} ms")
    print(f"    - Mean Latency Improvement:      {comp['delta_summary']['latency_reduction_pct']}% reduction")
    print(f"    - Availability Advantage:        +{comp['delta_summary']['availability_improvement_pct']}%")

    print("\n" + "=" * 65)
    print("                 DEMONSTRATION RUN COMPLETE                      ")
    print("=" * 65)


if __name__ == "__main__":
    main()

