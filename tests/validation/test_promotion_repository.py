"""Tests for durable promotion transition persistence and lifecycle history."""

from datetime import UTC, datetime

import pytest

from tradeos.infrastructure import SQLitePromotionTransitionRepository
from tradeos.validation import (
    InMemoryPromotionTransitionRepository,
    PromotionStage,
    PromotionStageTransition,
    PromotionTransitionAuditEvent,
    PromotionTransitionAuditEventType,
)


def make_transition(
    *,
    transition_id: str = "transition-1",
    review_id: str = "review-1",
    evidence_id: str = "evidence-1",
    strategy_id: str = "strategy-1",
    from_stage: PromotionStage = PromotionStage.PAPER,
    to_stage: PromotionStage = PromotionStage.CONTROLLED_PROMOTION,
) -> PromotionStageTransition:
    return PromotionStageTransition(
        transition_id=transition_id,
        review_id=review_id,
        evidence_id=evidence_id,
        strategy_id=strategy_id,
        strategy_version="1.0.0",
        from_stage=from_stage,
        to_stage=to_stage,
    )


def make_event(
    *,
    event_id: str = "event-1",
    transition_id: str = "transition-1",
    review_id: str = "review-1",
    evidence_id: str = "evidence-1",
) -> PromotionTransitionAuditEvent:
    return PromotionTransitionAuditEvent(
        event_id=event_id,
        transition_id=transition_id,
        review_id=review_id,
        evidence_id=evidence_id,
        event_type=PromotionTransitionAuditEventType.TRANSITION_RECORDED,
        actor_id="governance-system",
        occurred_at=datetime(2026, 1, 2, 1, tzinfo=UTC),
        detail="Promotion transition recorded.",
    )


def test_in_memory_repository_preserves_transition_lineage_and_order() -> None:
    repository = InMemoryPromotionTransitionRepository()
    first = make_transition()
    second = make_transition(
        transition_id="transition-2",
        from_stage=PromotionStage.RESEARCH,
        to_stage=PromotionStage.BACKTEST,
    )
    repository.save(first)
    repository.save(second)

    assert repository.get(first.transition_id) == first
    assert repository.list_for_strategy(first.strategy_id) == (first, second)
    assert repository.list_for_review(first.review_id) == (first, second)


def test_in_memory_repository_rejects_transition_replacement() -> None:
    repository = InMemoryPromotionTransitionRepository()
    repository.save(make_transition())

    with pytest.raises(ValueError, match="immutable"):
        repository.save(make_transition(evidence_id="different-evidence"))


def test_in_memory_repository_preserves_append_only_lifecycle_history() -> None:
    repository = InMemoryPromotionTransitionRepository()
    transition = make_transition()
    first = make_event()
    second = make_event(event_id="event-2")
    repository.save(transition)
    repository.append_audit_event(first)
    repository.append_audit_event(first)
    repository.append_audit_event(second)

    assert repository.list_audit_history() == (first, second)
    assert repository.list_audit_history(transition_id=transition.transition_id) == (
        first,
        second,
    )


def test_in_memory_repository_rejects_unknown_or_wrong_lineage_event() -> None:
    repository = InMemoryPromotionTransitionRepository()
    repository.save(make_transition())

    with pytest.raises(ValueError, match="unknown transition"):
        repository.append_audit_event(make_event(transition_id="unknown"))

    with pytest.raises(ValueError, match="lineage"):
        repository.append_audit_event(make_event(evidence_id="different-evidence"))


def test_sqlite_repository_round_trips_transition_and_history(tmp_path) -> None:
    database = tmp_path / "transitions.db"
    transition = make_transition()
    event = make_event()

    with SQLitePromotionTransitionRepository(database) as repository:
        repository.save(transition)
        repository.append_audit_event(event)

    with SQLitePromotionTransitionRepository(database) as repository:
        assert repository.get(transition.transition_id) == transition
        assert repository.list_for_strategy(transition.strategy_id) == (transition,)
        assert repository.list_audit_history() == (event,)


def test_sqlite_repository_rejects_mutation_and_preserves_idempotency(tmp_path) -> None:
    database = tmp_path / "transitions.db"
    transition = make_transition()
    event = make_event()

    with SQLitePromotionTransitionRepository(database) as repository:
        repository.save(transition)
        repository.save(transition)
        repository.append_audit_event(event)
        repository.append_audit_event(event)

        with pytest.raises(ValueError, match="immutable"):
            repository.save(make_transition(evidence_id="different-evidence"))

        with pytest.raises(ValueError, match="lineage"):
            repository.append_audit_event(
                make_event(event_id="event-1", evidence_id="different-evidence")
            )

        assert repository.get(transition.transition_id) == transition
        assert repository.list_audit_history() == (event,)
