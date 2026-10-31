"""
AEGIS Defense Modules Registry.
Compliant with Section 13.1 of AEGIS Master Implementation Spec.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class DefenseModuleDescriptor(BaseModel):
    module_id: str
    name: str
    description: str
    implementation_status: str = Field(..., description="active, planned, deprecated")
    enabled: bool = True
    allowed_actions: List[str] = Field(default_factory=list)


AVAILABLE_DEFENSE_MODULES: Dict[str, DefenseModuleDescriptor] = {
    "gateway_acl": DefenseModuleDescriptor(
        module_id="gateway_acl",
        name="Gateway Access Control List",
        description="Enforces dynamic L7 source IP blocking/unblocking at the mTLS application gateway",
        implementation_status="active",
        enabled=True,
        allowed_actions=["block_source_ip", "unblock_source_ip"]
    ),
    "rate_limiter": DefenseModuleDescriptor(
        module_id="rate_limiter",
        name="Adaptive Rate Limiter",
        description="Throttles aggressive HTTP and authentication request rates per client IP",
        implementation_status="active",
        enabled=True,
        allowed_actions=["tighten_login_rate_limit", "reset_rate_limit"]
    ),
    "identity_guard": DefenseModuleDescriptor(
        module_id="identity_guard",
        name="Identity & Access Guard",
        description="Enforces account lockouts, MFA challenges, and credential throttling",
        implementation_status="active",
        enabled=True,
        allowed_actions=["throttle_account", "lock_test_account"]
    ),
    "session_guardian": DefenseModuleDescriptor(
        module_id="session_guardian",
        name="Session Guardian",
        description="Revokes compromised or replayed synthetic session tokens",
        implementation_status="planned",
        enabled=False,
        allowed_actions=["revoke_session_token"]
    ),
    "network_segmentation": DefenseModuleDescriptor(
        module_id="network_segmentation",
        name="Network Segmentation Policy",
        description="Quarantines internal service communication paths",
        implementation_status="planned",
        enabled=False,
        allowed_actions=["isolate_service_link"]
    ),
    "monitoring_guard": DefenseModuleDescriptor(
        module_id="monitoring_guard",
        name="Monitoring & Telemetry Watchdog",
        description="Monitors telemetry pipeline integrity and sensor heartbeat",
        implementation_status="planned",
        enabled=False,
        allowed_actions=["alert_telemetry_gap"]
    ),
    "resource_guard": DefenseModuleDescriptor(
        module_id="resource_guard",
        name="Container Resource Guard",
        description="Clamps CPU and memory quotas to prevent resource starvation",
        implementation_status="planned",
        enabled=False,
        allowed_actions=["throttle_cpu_quota"]
    )
}

