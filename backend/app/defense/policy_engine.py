"""
AEGIS Deterministic Defense Policy Engine.
Validates candidate defensive actions against hard security invariants (Omega).
Compliant with Section 13.3 & 18 of AEGIS Master Implementation Spec.
"""

import ipaddress
import logging
from typing import Dict, Any, Tuple, Optional
from backend.app.defense.modules import AVAILABLE_DEFENSE_MODULES

logger = logging.getLogger("aegis.policy_engine")

LAB_ACCESS_SUBNET = "172.31.10.0/24"
PROTECTED_CONTROL_IPS = {
    "127.0.0.1",
    "172.31.10.1",   # Gateway host default route
    "172.31.10.2",   # Gateway ingress interface
    "172.31.2.10",   # Backend API
    "172.31.2.20",   # Policy Agent
    "172.31.2.30",   # PostgreSQL
}


class PolicyDecision:
    def __init__(self, approved: bool, reason: str, invariant_violated: Optional[str] = None):
        self.approved = approved
        self.reason = reason
        self.invariant_violated = invariant_violated

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approved": self.approved,
            "reason": self.reason,
            "invariant_violated": self.invariant_violated
        }


class PolicyEngine:
    def __init__(self, subnet_cidr: str = LAB_ACCESS_SUBNET):
        self.subnet = ipaddress.IPv4Network(subnet_cidr, strict=False)

    def validate_action(
        self,
        module_id: str,
        action_id: str,
        parameters: Dict[str, Any]
    ) -> PolicyDecision:
        """
        Validates candidate action against hard invariants.
        Deterministic rule code - AI has no direct execution privileges.
        """
        # 1. Module Allowlist check
        if module_id not in AVAILABLE_DEFENSE_MODULES:
            return PolicyDecision(
                approved=False,
                reason=f"Unknown or unauthorized module '{module_id}'",
                invariant_violated="OMEGA_UNKNOWN_MODULE"
            )

        module_desc = AVAILABLE_DEFENSE_MODULES[module_id]
        if not module_desc.enabled or module_desc.implementation_status != "active":
            return PolicyDecision(
                approved=False,
                reason=f"Module '{module_id}' is not in active/enabled status",
                invariant_violated="OMEGA_MODULE_INACTIVE"
            )

        # 2. Action Allowlist check
        if action_id not in module_desc.allowed_actions:
            return PolicyDecision(
                approved=False,
                reason=f"Action '{action_id}' not allowed for module '{module_id}'",
                invariant_violated="OMEGA_UNKNOWN_ACTION"
            )

        # 3. Invariant: gateway_acl parameter checks
        if module_id == "gateway_acl":
            ip_str = parameters.get("ip_address")
            if not ip_str:
                return PolicyDecision(
                    approved=False,
                    reason="Missing 'ip_address' parameter for gateway_acl action",
                    invariant_violated="OMEGA_MISSING_PARAM"
                )

            try:
                ip_obj = ipaddress.IPv4Address(ip_str.strip())
            except ValueError:
                return PolicyDecision(
                    approved=False,
                    reason=f"Malformed IPv4 address '{ip_str}'",
                    invariant_violated="OMEGA_MALFORMED_IP"
                )

            # Invariant: Must be within lab access subnet
            if ip_obj not in self.subnet:
                return PolicyDecision(
                    approved=False,
                    reason=f"IP {ip_str} is outside lab access subnet ({self.subnet})",
                    invariant_violated="OMEGA_OUT_OF_SCOPE_IP"
                )

            # Invariant: Never block control plane, backend, or gateway itself
            if str(ip_obj) in PROTECTED_CONTROL_IPS or ip_obj.is_loopback:
                return PolicyDecision(
                    approved=False,
                    reason=f"Cannot block protected control plane/gateway address {ip_str}",
                    invariant_violated="OMEGA_CRITICAL_INFRASTRUCTURE_PROTECTED"
                )

        # 4. Invariant: rate_limiter parameter bounds
        if module_id == "rate_limiter":
            rps = parameters.get("requests_per_window", 10)
            window = parameters.get("window_seconds", 60)
            if rps < 1 or rps > 10000:
                return PolicyDecision(
                    approved=False,
                    reason=f"Requests per window ({rps}) exceeds safe boundaries [1, 10000]",
                    invariant_violated="OMEGA_RATE_LIMIT_OUT_OF_BOUNDS"
                )
            if window < 1 or window > 3600:
                return PolicyDecision(
                    approved=False,
                    reason=f"Window seconds ({window}) exceeds safe boundaries [1, 3600]",
                    invariant_violated="OMEGA_WINDOW_OUT_OF_BOUNDS"
                )

        return PolicyDecision(
            approved=True,
            reason="Action successfully validated against all hard security invariants"
        )

