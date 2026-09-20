"""In-memory persistence for immutable promotion reviews and audit history."""

from tradeos.validation.review import PromotionReview
from tradeos.validation.review_audit import PromotionReviewAuditEvent
from tradeos.validation.review_repository import PromotionReviewRepository


class InMemoryPromotionReviewRepository(PromotionReviewRepository):
    """Deterministic repository that rejects mutation and duplicate audit events."""

    def __init__(self) -> None:
        self._reviews: dict[str, PromotionReview] = {}
        self._audit_events: dict[str, PromotionReviewAuditEvent] = {}

    def get(self, review_id: str) -> PromotionReview | None:
        if not review_id:
            raise ValueError("review_id must not be empty")
        return self._reviews.get(review_id)

    def save(self, review: PromotionReview) -> None:
        existing = self.get(review.review_id)
        if existing is not None and existing != review:
            raise ValueError("promotion review is immutable")
        self._reviews[review.review_id] = review

    def list_for_evidence(self, evidence_id: str) -> tuple[PromotionReview, ...]:
        if not evidence_id:
            raise ValueError("evidence_id must not be empty")
        return tuple(
            review for review in self._reviews.values() if review.evidence_id == evidence_id
        )

    def append_audit_event(self, event: PromotionReviewAuditEvent) -> None:
        review = self.get(event.review_id)
        if review is None:
            raise ValueError("audit event references unknown review")
        if review.evidence_id != event.evidence_id:
            raise ValueError("audit event evidence does not match review")
        existing = self._audit_events.get(event.event_id)
        if existing is not None and existing != event:
            raise ValueError("promotion review audit event is immutable")
        self._audit_events[event.event_id] = event

    def list_audit_history(
        self, *, review_id: str | None = None
    ) -> tuple[PromotionReviewAuditEvent, ...]:
        if review_id == "":
            raise ValueError("review_id must not be empty")
        return tuple(
            event
            for event in self._audit_events.values()
            if review_id is None or event.review_id == review_id
        )
