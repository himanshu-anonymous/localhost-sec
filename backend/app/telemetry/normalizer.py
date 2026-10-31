"""
AEGIS Telemetry Event Normalizer.
Translates heterogeneous log streams into canonical SecurityEventSchema objects.
Compliant with Section 9 of AEGIS Master Implementation Spec.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from backend.app.telemetry.schemas import SecurityEventSchema


class EventNormalizer:
    @staticmethod
    def from_target_app_log(raw_log: str, sim_run_id: Optional[str] = None) -> Optional[SecurityEventSchema]:
        """Normalizes a structured JSON log line from target-web."""
        try:
            data = json.loads(raw_log.strip())
            return SecurityEventSchema(
                occurred_at=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(timezone.utc),
                source_type="target_app",
                source_name=data.get("source_name", "target-web"),
                event_type=data.get("event_type", "http_request"),
                source_ip=data.get("source_ip", "unknown"),
                destination_ip=data.get("destination_ip", "172.31.20.10"),
                destination_port=8080,
                protocol="HTTP",
                severity=data.get("severity", "info"),
                simulation_run_id=sim_run_id,
                metadata={
                    "username": data.get("username"),
                    "status_code": data.get("status_code"),
                    "path": data.get("path")
                }
            )
        except Exception:
            return None

    @staticmethod
    def from_haproxy_access_log(line: str, sim_run_id: Optional[str] = None) -> Optional[SecurityEventSchema]:
        """Normalizes an HAProxy HTTP log entry."""
        # e.g.: 172.31.10.10:50122 [31/Oct/2026:10:00:00.123] aegis_secure_ingress target_cluster/target_web 0/0/1/2/3 401 150 - - ---- ...
        parts = line.strip().split()
        if len(parts) < 10:
            return None
        try:
            src_ip = parts[0].split(":")[0]
            status_code = int(parts[10]) if parts[10].isdigit() else 200
            severity = "warning" if status_code >= 400 else "info"
            event_type = "gateway_deny" if status_code == 403 else "http_request"
            return SecurityEventSchema(
                source_type="haproxy",
                source_name="aegis-gateway",
                event_type=event_type,
                source_ip=src_ip,
                destination_ip="172.31.20.10",
                destination_port=8443,
                protocol="HTTPS",
                severity="high" if status_code == 403 else severity,
                simulation_run_id=sim_run_id,
                metadata={"status_code": status_code, "raw_line": line}
            )
        except Exception:
            return None

    @staticmethod
    def from_suricata_eve(eve_json: Dict[str, Any], sim_run_id: Optional[str] = None) -> Optional[SecurityEventSchema]:
        """Normalizes a Suricata EVE JSON event record."""
        event_type = eve_json.get("event_type", "alert")
        alert = eve_json.get("alert", {})
        return SecurityEventSchema(
            occurred_at=datetime.fromisoformat(eve_json["timestamp"]) if "timestamp" in eve_json else datetime.now(timezone.utc),
            source_type="suricata",
            source_name="suricata-sensor",
            event_type=f"suricata_{event_type}",
            source_ip=eve_json.get("src_ip", "unknown"),
            source_port=eve_json.get("src_port"),
            destination_ip=eve_json.get("dest_ip"),
            destination_port=eve_json.get("dest_port"),
            protocol=eve_json.get("proto", "TCP"),
            severity="high" if alert.get("severity", 3) <= 2 else "warning",
            simulation_run_id=sim_run_id,
            metadata={
                "signature": alert.get("signature"),
                "signature_id": alert.get("signature_id"),
                "category": alert.get("category")
            }
        )

    @staticmethod
    def from_dict(data: Dict[str, Any], sim_run_id: Optional[str] = None) -> SecurityEventSchema:
        """Direct dictionary ingestion."""
        if sim_run_id and not data.get("simulation_run_id"):
            data["simulation_run_id"] = sim_run_id
        return SecurityEventSchema(**data)

