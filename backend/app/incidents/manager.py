"""
AEGIS Incident Management and Correlation Engine.
Correlates detections into unified incidents and tracks security response lifecycle.
Compliant with Section 11 of AEGIS Master Implementation Spec.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from backend.app.telemetry.schemas import DetectionRecord, IncidentRecord

logger = logging.getLogger("aegis.incident_manager")


class IncidentManager:
    def __init__(self, correlation_window_s: int = 120):
        self.correlation_window = timedelta(seconds=correlation_window_s)
        self.incidents: Dict[str, IncidentRecord] = {}

    def correlate_detection(self, detection: DetectionRecord) -> IncidentRecord:
        """
        Correlates a detection into an existing active incident, or creates a new one.
        """
        now = detection.detected_at
        src_ip = detection.source_ip or "unknown"

        # Search for an open incident matching source_ip within correlation window
        for inc in reversed(list(self.incidents.values())):
            if inc.status not in ["RESOLVED", "CLOSED", "FALSE_POSITIVE"]:
                if src_ip in inc.source_identities or detection.affected_service in inc.affected_services:
                    if now - inc.last_seen <= self.correlation_window:
                        # Append to existing incident
                        inc.last_seen = now
                        if detection.detection_id not in inc.related_detection_ids:
                            inc.related_detection_ids.append(detection.detection_id)
                        for ev_id in detection.evidence_event_ids:
                            if ev_id not in inc.related_event_ids:
                                inc.related_event_ids.append(ev_id)
                        for tech in detection.inferred_techniques:
                            if tech not in inc.technique_associations:
                                inc.technique_associations.append(tech)
                        inc.status = "INVESTIGATING"
                        logger.info(f"Correlated detection {detection.detection_id} into Incident {inc.incident_id}")
                        return inc

        # Create new incident
        tech_str = ", ".join(detection.inferred_techniques) or "Unknown Technique"
        title = f"Suspicious Activity ({tech_str}) on {detection.affected_service}"
        desc = f"Detector '{detection.detector_id}' identified malicious or anomalous pattern: {detection.reason}"

        new_incident = IncidentRecord(
            title=title,
            description=desc,
            severity=detection.severity,
            status="NEW",
            first_seen=now,
            last_seen=now,
            affected_services=[detection.affected_service],
            source_identities=[src_ip] if src_ip else [],
            related_event_ids=list(detection.evidence_event_ids),
            related_detection_ids=[detection.detection_id],
            technique_associations=list(detection.inferred_techniques)
        )
        self.incidents[new_incident.incident_id] = new_incident
        logger.info(f"Created NEW Incident {new_incident.incident_id}: {title}")
        return new_incident

    def update_status(self, incident_id: str, new_status: str, notes: Optional[str] = None) -> Optional[IncidentRecord]:
        inc = self.incidents.get(incident_id)
        if not inc:
            return None
        inc.status = new_status
        inc.last_seen = datetime.now(timezone.utc)
        if new_status in ["RESOLVED", "CLOSED"]:
            inc.resolved_at = datetime.now(timezone.utc)
        if notes:
            inc.resolution_notes = notes
        logger.info(f"Incident {incident_id} status updated to {new_status}")
        return inc

    def get_incidents(self, limit: int = 50, status_filter: Optional[str] = None) -> List[IncidentRecord]:
        incs = list(self.incidents.values())
        if status_filter:
            incs = [i for i in incs if i.status == status_filter]
        return incs[-limit:]

    def get_incident_by_id(self, incident_id: str) -> Optional[IncidentRecord]:
        return self.incidents.get(incident_id)

    def clear(self):
        self.incidents.clear()


# Global singleton instance
incident_manager = IncidentManager()

