"""
Dynamic Defensive Policy Stack (DDPS) & Invariant Validator.
Compliant with Section 7 of Formal Specification v1.0.
"""

from typing import List, Tuple, Optional
import copy
from backend.app.schemas.models import DefensiveActionProposal, DDPSValidationResult


class DynamicDefensivePolicyStack:
    """
    Safety-controlled interface between RL agent and network environment.
    Translates abstract actions into bounded defensive controls and strictly
    enforces hard security invariants (Omega).
    """

    def __init__(self, cooldown_steps: int = 5):
        self.cooldown_steps = cooldown_steps
        self.last_action_step = -cooldown_steps
        self.current_enforced_policy = DefensiveActionProposal()  # baseline (all 0s)
        self.last_known_safe_policy = DefensiveActionProposal()
        self.audit_log: List[DDPSValidationResult] = []
        self.rejected_count = 0
        self.approved_count = 0

    def validate_and_enforce(
        self,
        proposed_action: DefensiveActionProposal,
        current_step: int,
        attempted_illegal_bypass: bool = False
    ) -> DDPSValidationResult:
        """
        Executes the 5-stage DDPS verification pipeline:
        1. Schema validation
        2. Parameter boundary validation
        3. Security Invariant validation (Omega)
        4. Stability and Hysteresis check
        5. Action Approval or Rejection
        """
        rejection_reasons = []
        stability_penalty = 0.0

        # Stage 1: Schema / Type Check
        if not isinstance(proposed_action, DefensiveActionProposal):
            rejection_reasons.append("Invalid action schema type")

        # Stage 2: Parameter Boundary Check (A_t in {0, 1, 2}^8)
        action_vals = proposed_action.to_list()
        for idx, val in enumerate(action_vals):
            if val not in (0, 1, 2):
                rejection_reasons.append(f"Parameter index {idx} out of bounds: {val} not in {{0, 1, 2}}")

        # Stage 3: Hard Security Invariants (Omega)
        # Omega 1 & 2: Invariant compliance flag
        if attempted_illegal_bypass:
            rejection_reasons.append("Omega Violation: Attempted authentication or authorization bypass")

        # Omega 3: Segmentation mode must never be negative or unverified
        if proposed_action.segmentation_mode < 0 or proposed_action.segmentation_mode > 2:
            rejection_reasons.append("Omega Violation: Invalid microsegmentation state")

        # Stage 4: Stability & Hysteresis Checks (Penalize high-frequency thrashing)
        steps_since_last = current_step - self.last_action_step
        if steps_since_last < self.cooldown_steps and proposed_action != self.current_enforced_policy:
            # Policy oscillation under cooldown
            stability_penalty += 0.2
            # For sudden 2-level jump during cooldown, reject
            diffs = [abs(p - c) for p, c in zip(action_vals, self.current_enforced_policy.to_list())]
            if max(diffs) >= 2:
                rejection_reasons.append(f"Stability Violation: Excessive parameter jump ({max(diffs)}) during cooldown ({steps_since_last}/{self.cooldown_steps} steps)")

        # Stage 5: Enforcement Decision
        is_approved = len(rejection_reasons) == 0
        if is_approved:
            self.approved_count += 1
            self.last_known_safe_policy = copy.deepcopy(self.current_enforced_policy)
            self.current_enforced_policy = copy.deepcopy(proposed_action)
            self.last_action_step = current_step
            enforced = proposed_action
        else:
            self.rejected_count += 1
            # Revert / maintain current enforced safe policy
            enforced = copy.deepcopy(self.current_enforced_policy)

        result = DDPSValidationResult(
            is_approved=is_approved,
            proposed_action=proposed_action,
            enforced_action=enforced,
            rejected_reasons=rejection_reasons,
            stability_penalty=stability_penalty,
            timestamp=float(current_step)
        )
        self.audit_log.append(result)
        return result

    def rollback(self):
        """Rollback to last known safe configuration."""
        self.current_enforced_policy = copy.deepcopy(self.last_known_safe_policy)

    def reset(self):
        """Resets the policy stack state for a new episode."""
        self.current_enforced_policy = DefensiveActionProposal()
        self.last_known_safe_policy = DefensiveActionProposal()
        self.last_action_step = -self.cooldown_steps
        self.audit_log.clear()
        self.rejected_count = 0
        self.approved_count = 0
