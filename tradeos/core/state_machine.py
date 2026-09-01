"""Deterministic state-machine primitives for TradeOS."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, TypeVar


StateT = TypeVar("StateT", bound=StrEnum)


class InvalidTransitionError(ValueError):
    """Raised when a requested transition is not legal from the current state."""


@dataclass(frozen=True, slots=True)
class Transition:
    """A validated state transition request."""

    from_state: StateT
    to_state: StateT
    actor: str
    reason: str


class StateMachine(Generic[StateT]):
    """Small deterministic state-machine engine.

    The transition table is immutable after construction. The engine performs
    no persistence and grants no authority; callers must supply the authoritative
    actor and the surrounding application service must enforce permissions.
    """

    def __init__(self, transitions: dict[StateT, frozenset[StateT]]) -> None:
        self._transitions = dict(transitions)

    def can_transition(self, current: StateT, target: StateT) -> bool:
        """Return whether the transition is explicitly allowed."""
        return target in self._transitions.get(current, frozenset())

    def transition(
        self,
        current: StateT,
        target: StateT,
        *,
        actor: str,
        reason: str,
    ) -> tuple[StateT, Transition]:
        """Validate and return a transition without mutating external state."""
        if not actor.strip():
            raise ValueError("actor is required")
        if not reason.strip():
            raise ValueError("reason is required")
        if not self.can_transition(current, target):
            raise InvalidTransitionError(f"Illegal transition: {current} -> {target}")
        return target, Transition(
            from_state=current,
            to_state=target,
            actor=actor,
            reason=reason,
        )
