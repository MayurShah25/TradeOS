from enum import StrEnum

import pytest

from tradeos.core.state_machine import InvalidTransitionError, StateMachine


class State(StrEnum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


@pytest.fixture
def machine() -> StateMachine[State]:
    return StateMachine(
        {
            State.NEW: frozenset({State.ACTIVE}),
            State.ACTIVE: frozenset({State.CLOSED}),
            State.CLOSED: frozenset(),
        }
    )


def test_legal_transition_returns_target_and_record(machine: StateMachine[State]) -> None:
    target, record = machine.transition(
        State.NEW,
        State.ACTIVE,
        actor="test",
        reason="valid transition",
    )

    assert target is State.ACTIVE
    assert record.from_state is State.NEW
    assert record.to_state is State.ACTIVE


def test_illegal_transition_is_rejected(machine: StateMachine[State]) -> None:
    with pytest.raises(InvalidTransitionError):
        machine.transition(
            State.NEW,
            State.CLOSED,
            actor="test",
            reason="invalid transition",
        )


def test_actor_and_reason_are_required(machine: StateMachine[State]) -> None:
    with pytest.raises(ValueError, match="actor is required"):
        machine.transition(State.NEW, State.ACTIVE, actor="", reason="reason")

    with pytest.raises(ValueError, match="reason is required"):
        machine.transition(State.NEW, State.ACTIVE, actor="test", reason=" ")
