"""
AEGIS Defense State Machine.
Compliant with Section 13.2 of AEGIS Master Implementation Spec.
"""

import logging
from enum import Enum
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger("aegis.defense_state_machine")


class DefenseState(str, Enum):
    NORMAL = "NORMAL"
    OBSERVING = "OBSERVING"
    SUSPECTED_ATTACK = "SUSPECTED_ATTACK"
    CONFIRMED_ATTACK = "CONFIRMED_ATTACK"
    MITIGATING = "MITIGATING"
    CONTAINED = "CONTAINED"
    RECOVERING = "RECOVERING"
    DEGRADED = "DEGRADED"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class StateTransitionRecord:
    def __init__(
        self,
        from_state: DefenseState,
        to_state: DefenseState,
        trigger: str,
        reason: str,
        actor: str = "defense_orchestrator"
    ):
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.from_state = from_state
        self.to_state = to_state
        self.trigger = trigger
        self.reason = reason
        self.actor = actor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "trigger": self.trigger,
            "reason": self.reason,
            "actor": self.actor
        }


class DefenseStateMachine:
    # Permitted valid state transitions
    VALID_TRANSITIONS = {
        DefenseState.NORMAL: [DefenseState.OBSERVING, DefenseState.SUSPECTED_ATTACK, DefenseState.EMERGENCY_STOP],
        DefenseState.OBSERVING: [DefenseState.NORMAL, DefenseState.SUSPECTED_ATTACK, DefenseState.EMERGENCY_STOP],
        DefenseState.SUSPECTED_ATTACK: [DefenseState.CONFIRMED_ATTACK, DefenseState.OBSERVING, DefenseState.NORMAL, DefenseState.EMERGENCY_STOP],
        DefenseState.CONFIRMED_ATTACK: [DefenseState.MITIGATING, DefenseState.DEGRADED, DefenseState.EMERGENCY_STOP],
        DefenseState.MITIGATING: [DefenseState.CONTAINED, DefenseState.DEGRADED, DefenseState.EMERGENCY_STOP],
        DefenseState.CONTAINED: [DefenseState.RECOVERING, DefenseState.CONFIRMED_ATTACK, DefenseState.EMERGENCY_STOP],
        DefenseState.RECOVERING: [DefenseState.NORMAL, DefenseState.CONFIRMED_ATTACK, DefenseState.EMERGENCY_STOP],
        DefenseState.DEGRADED: [DefenseState.RECOVERING, DefenseState.MITIGATING, DefenseState.EMERGENCY_STOP],
        DefenseState.EMERGENCY_STOP: [DefenseState.RECOVERING, DefenseState.NORMAL]
    }

    def __init__(self):
        self.current_state = DefenseState.NORMAL
        self.transition_history: List[StateTransitionRecord] = []
        self.last_transition_time = datetime.now(timezone.utc)

    def transition_to(self, new_state: DefenseState, trigger: str, reason: str, actor: str = "orchestrator") -> bool:
        if self.current_state == new_state:
            return True

        allowed = self.VALID_TRANSITIONS.get(self.current_state, [])
        if new_state not in allowed and new_state != DefenseState.EMERGENCY_STOP:
            logger.warning(
                f"Invalid state transition rejected: {self.current_state.value} -> {new_state.value} "
                f"(Trigger: {trigger})"
            )
            return False

        rec = StateTransitionRecord(
            from_state=self.current_state,
            to_state=new_state,
            trigger=trigger,
            reason=reason,
            actor=actor
        )
        prev = self.current_state
        self.current_state = new_state
        self.last_transition_time = datetime.now(timezone.utc)
        self.transition_history.append(rec)

        logger.info(f"DEFENSE STATE CHANGED: {prev.value} -> {new_state.value} (Trigger: {trigger})")
        return True

    def trigger_emergency_stop(self, reason: str = "Operator manual emergency stop") -> bool:
        return self.transition_to(
            DefenseState.EMERGENCY_STOP,
            trigger="EMERGENCY_STOP_TRIGGERED",
            reason=reason,
            actor="operator"
        )

    def reset_to_normal(self, reason: str = "System reset to baseline") -> bool:
        return self.transition_to(
            DefenseState.NORMAL,
            trigger="RESET_BASELINE",
            reason=reason,
            actor="operator"
        )

    def get_status(self) -> Dict[str, Any]:
        return {
            "current_state": self.current_state.value,
            "last_transition_time": self.last_transition_time.isoformat(),
            "history": [r.to_dict() for r in self.transition_history[-10:]]
        }

