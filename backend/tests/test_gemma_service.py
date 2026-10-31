"""
Test suite for Gemma 4 Reasoning Service (Domain C).
Verifies credential configuration, schema validation, and structured analysis output.
"""

import os
import pytest
from backend.app.gemma.service import GemmaReasoningService, GemmaAnalysisReport


def test_gemma_service_initialization_and_keys():
    service = GemmaReasoningService()
    # Check that keys are mapped
    assert "env_a_baseline" in service.keys
    assert "env_b_adaptive" in service.keys
    assert "env_c_hardened" in service.keys
    assert "env_d_experimental" in service.keys


def test_gemma_analysis_output_schema():
    service = GemmaReasoningService()
    
    metrics = {
        "effective_availability_pct": 93.8,
        "blast_radius_factor": 0.0,
        "mean_time_to_containment_s": 4.0,
        "resilience_degradation_index": 6.1
    }
    
    report = service.analyze_incident_and_defense(
        environment_id="env_b_adaptive",
        metrics=metrics,
        active_incidents=["T1499", "T1110", "T1046"],
        enforced_policy={"edge_rate_limit_level": 2, "segmentation_mode": 2},
        ddps_rejected_count=0
    )
    
    assert isinstance(report, GemmaAnalysisReport)
    assert report.environment_id == "env_b_adaptive"
    assert "Adaptive DDPS" in report.incident_summary
    assert len(report.recommendations) > 0
    assert "All mandatory security invariants" in report.invariant_status
    assert report.confidence_score > 0.9


def test_gemma_baseline_versus_adaptive_comparison():
    service = GemmaReasoningService()
    
    rep_a = service.analyze_incident_and_defense(
        environment_id="env_a_baseline",
        metrics={"effective_availability_pct": 39.8, "blast_radius_factor": 0.12},
        active_incidents=["T1499", "T1046"],
        enforced_policy={"edge_rate_limit_level": 0}
    )
    
    rep_b = service.analyze_incident_and_defense(
        environment_id="env_b_adaptive",
        metrics={"effective_availability_pct": 93.8, "blast_radius_factor": 0.0},
        active_incidents=["T1499", "T1046"],
        enforced_policy={"edge_rate_limit_level": 2}
    )
    
    # Baseline identifies failure; Adaptive identifies successful defense
    assert "collapsed" in rep_a.incident_summary.lower()
    assert "isolating" in rep_b.incident_summary.lower() or "adjusted" in rep_b.incident_summary.lower()
