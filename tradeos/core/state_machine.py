"""Deterministic state-machine primitives for TradeOS."""

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeVar


StateT = TypeVar("StateT", bound=StrEnum)


class InvalidTransitionError(ValueError):
    """Raised when a requested transition is not legal from the current state."""


@dataclass(frozen=True, slots=True)
class Transition[T: StrEnum]:
    """A validated state transition request."""

    from_state: T
    to_state: T
    actor: str
    reason: str


class StateMachine[T: StrEnum]:
    """Small deterministic state-machine engine.

    The transition table is immutable after construction. The engine performs
    no persistence and grants no authority; callers must supply the authoritative
    actor and the surrounding application service must enforce permissions.
    """

    def __init__(self, transitions: dict[T, frozenset[T]]) -> None:
        self._transitions = dict(transitions)

    def can_transition(self, current: T, target: T) -> bool:
        """Return whether the transition is explicitly allowed."""
        return target in self._transitions.get(current, frozenset())

    def transition(
        self,
        current: T,
        target: T,
        *,
        actor: str,
        reason: str,
    ) -> tuple[T, Transition[T]]:
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
