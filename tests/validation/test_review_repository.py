"""Tests for durable promotion review persistence and governance history."""

from datetime import UTC, datetime

import pytest

from tradeos.infrastructure import SQLitePromotionReviewRepository
from tradeos.validation import (
    InMemoryPromotionReviewRepository,
    PromotionEligibility,
    PromotionReview,
    PromotionReviewAuditEvent,
    PromotionReviewAuditEventType,
    PromotionReviewDecision,
)


def make_review(
    *,
    review_id: str = "review-1",
    evidence_id: str = "evidence-1",
    decision: PromotionReviewDecision = PromotionReviewDecision.PENDING,
) -> PromotionReview:
    completed = decision is not PromotionReviewDecision.PENDING
    return PromotionReview(
        review_id=review_id,
        evidence_id=evidence_id,
        strategy_id="strategy-1",
        strategy_version="1.0.0",
        eligibility=PromotionEligibility.ELIGIBLE_FOR_REVIEW,
        decision=decision,
        reviewer_id="reviewer-1" if completed else None,
        reviewed_at=datetime(2026, 1, 2, tzinfo=UTC) if completed else None,
        rationale="Governance review record.",
    )


def make_event(
    *,
    event_id: str = "event-1",
    review_id: str = "review-1",
    evidence_id: str = "evidence-1",
) -> PromotionReviewAuditEvent:
    return PromotionReviewAuditEvent(
        event_id=event_id,
        review_id=review_id,
        evidence_id=evidence_id,
        event_type=PromotionReviewAuditEventType.REVIEW_RECORDED,
        actor_id="governance-system",
        occurred_at=datetime(2026, 1, 2, 1, tzinfo=UTC),
        detail="Review recorded for governance.",
    )


def test_in_memory_repository_preserves_review_lineage_and_is_idempotent() -> None:
    repository = InMemoryPromotionReviewRepository()
    review = make_review()
    repository.save(review)
    repository.save(review)

    assert repository.get(review.review_id) == review
    assert repository.list_for_evidence(review.evidence_id) == (review,)


def test_in_memory_repository_rejects_review_replacement() -> None:
    repository = InMemoryPromotionReviewRepository()
    repository.save(make_review())

    with pytest.raises(ValueError, match="immutable"):
        repository.save(make_review(review_id="review-1", evidence_id="different-evidence"))


def test_in_memory_repository_preserves_append_only_audit_history() -> None:
    repository = InMemoryPromotionReviewRepository()
    review = make_review()
    first = make_event()
    second = make_event(
        event_id="event-2",
    )
    repository.save(review)
    repository.append_audit_event(first)
    repository.append_audit_event(first)
    repository.append_audit_event(second)

    assert repository.list_audit_history() == (first, second)
    assert repository.list_audit_history(review_id=review.review_id) == (first, second)


def test_in_memory_repository_rejects_audit_for_unknown_or_wrong_evidence() -> None:
    repository = InMemoryPromotionReviewRepository()
    repository.save(make_review())

    with pytest.raises(ValueError, match="unknown review"):
        repository.append_audit_event(make_event(review_id="unknown"))

    with pytest.raises(ValueError, match="evidence"):
        repository.append_audit_event(make_event(evidence_id="different-evidence"))


def test_sqlite_repository_round_trips_review_and_audit_history(tmp_path) -> None:
    database = tmp_path / "reviews.db"
    review = make_review(decision=PromotionReviewDecision.REJECTED)
    event = make_event()

    with SQLitePromotionReviewRepository(database) as repository:
        repository.save(review)
        repository.append_audit_event(event)

    with SQLitePromotionReviewRepository(database) as repository:
        assert repository.get(review.review_id) == review
        assert repository.list_for_evidence(review.evidence_id) == (review,)
        assert repository.list_audit_history() == (event,)


def test_sqlite_repository_rejects_review_and_audit_mutation(tmp_path) -> None:
    database = tmp_path / "reviews.db"
    review = make_review()
    event = make_event()

    with SQLitePromotionReviewRepository(database) as repository:
        repository.save(review)
        repository.append_audit_event(event)

        with pytest.raises(ValueError, match="immutable"):
            repository.save(make_review(review_id="review-1", evidence_id="different"))

        with pytest.raises(ValueError, match="immutable"):
            repository.append_audit_event(
                make_event(event_id="event-1", evidence_id="different-evidence")
            )

        assert repository.get(review.review_id) == review
        assert repository.list_audit_history() == (event,)
