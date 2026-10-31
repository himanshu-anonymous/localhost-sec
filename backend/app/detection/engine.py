"""
AEGIS Deterministic Detection Engine.
Operates on normalized telemetry independent of simulation ground truth.
Compliant with Section 9.3 & 10 of AEGIS Master Implementation Spec.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
from backend.app.telemetry.schemas import SecurityEventSchema, DetectionRecord

logger = logging.getLogger("aegis.detection_engine")


class DetectionEngine:
    def __init__(
        self,
        failed_login_threshold: int = 5,
        failed_login_window_s: int = 30,
        traffic_surge_threshold: int = 30,
        traffic_surge_window_s: int = 10,
    ):
        self.failed_login_threshold = failed_login_threshold
        self.failed_login_window = timedelta(seconds=failed_login_window_s)
        self.traffic_surge_threshold = traffic_surge_threshold
        self.traffic_surge_window = timedelta(seconds=traffic_surge_window_s)

        # In-memory sliding telemetry windows per source_ip
        self.recent_auth_failures: Dict[str, List[SecurityEventSchema]] = defaultdict(list)
        self.recent_requests: Dict[str, List[SecurityEventSchema]] = defaultdict(list)
        self.detections: List[DetectionRecord] = []

    def evaluate_event(self, event: SecurityEventSchema) -> Optional[DetectionRecord]:
        """
        Evaluates a single event against deterministic detection rules.
        CRITICAL: Never reads ground_truth metadata.
        """
        now = event.occurred_at
        src_ip = event.source_ip

        # 1. Rule: Failed Login Threshold Detector (T1110)
        if event.event_type == "auth_failure":
            window = self.recent_auth_failures[src_ip]
            window.append(event)
            # Prune old events outside sliding window
            cutoff = now - self.failed_login_window
            self.recent_auth_failures[src_ip] = [e for e in window if e.occurred_at >= cutoff]

            active_window = self.recent_auth_failures[src_ip]
            if len(active_window) >= self.failed_login_threshold:
                evidence_ids = [e.event_id for e in active_window]
                detection = DetectionRecord(
                    detector_id="failed_login_detector",
                    detector_version="1.0.0",
                    detected_at=now,
                    severity="high",
                    confidence=0.92,
                    inferred_techniques=["T1110"],
                    evidence_event_ids=evidence_ids,
                    reason=f"Observed {len(active_window)} failed authentication attempts within {self.failed_login_window.total_seconds():.0f}s from source IP {src_ip}.",
                    affected_service=event.source_name,
                    source_ip=src_ip,
                    simulation_run_id=event.simulation_run_id
                )
                self.detections.append(detection)
                # Clear evaluated window to prevent duplicate alerts
                self.recent_auth_failures[src_ip].clear()
                logger.warning(f"DETECTION TRIGGERED: T1110 Brute Force by {src_ip} (Evidence count: {len(evidence_ids)})")
                return detection

        # 2. Rule: HTTP Traffic Rate Anomaly Detector (T1498)
        if event.event_type in ["http_request", "gateway_deny"]:
            window = self.recent_requests[src_ip]
            window.append(event)
            cutoff = now - self.traffic_surge_window
            self.recent_requests[src_ip] = [e for e in window if e.occurred_at >= cutoff]

            active_window = self.recent_requests[src_ip]
            if len(active_window) >= self.traffic_surge_threshold:
                evidence_ids = [e.event_id for e in active_window]
                detection = DetectionRecord(
                    detector_id="traffic_anomaly_detector",
                    detector_version="1.0.0",
                    detected_at=now,
                    severity="high",
                    confidence=0.88,
                    inferred_techniques=["T1498"],
                    evidence_event_ids=evidence_ids,
                    reason=f"High request rate detected: {len(active_window)} requests within {self.traffic_surge_window.total_seconds():.0f}s from source IP {src_ip}.",
                    affected_service="aegis-gateway",
                    source_ip=src_ip,
                    simulation_run_id=event.simulation_run_id
                )
                self.detections.append(detection)
                self.recent_requests[src_ip].clear()
                logger.warning(f"DETECTION TRIGGERED: T1498 Traffic Surge by {src_ip}")
                return detection

        # 3. Rule: Session Token Replay / Expired Synthetic Token (T1550)
        if event.metadata.get("token_status") == "replayed_or_expired":
            detection = DetectionRecord(
                detector_id="session_replay_detector",
                detector_version="1.0.0",
                detected_at=now,
                severity="high",
                confidence=0.90,
                inferred_techniques=["T1550"],
                evidence_event_ids=[event.event_id],
                reason=f"Synthetic session token expired or replay flag observed from {src_ip}.",
                affected_service=event.source_name,
                source_ip=src_ip,
                simulation_run_id=event.simulation_run_id
            )
            self.detections.append(detection)
            return detection

        return None

    def get_detections(self, limit: int = 50, simulation_run_id: Optional[str] = None) -> List[DetectionRecord]:
        results = self.detections
        if simulation_run_id:
            results = [d for d in results if d.simulation_run_id == simulation_run_id]
        return results[-limit:]

    def get_detection_by_id(self, detection_id: str) -> Optional[DetectionRecord]:
        for d in reversed(self.detections):
            if d.detection_id == detection_id:
                return d
        return None

    def clear(self):
        self.recent_auth_failures.clear()
        self.recent_requests.clear()
        self.detections.clear()


# Global singleton instance
detection_engine = DetectionEngine()

