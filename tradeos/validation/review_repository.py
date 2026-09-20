"""Persistence port for immutable promotion reviews and governance history."""

from abc import ABC, abstractmethod

from tradeos.validation.review import PromotionReview
from tradeos.validation.review_audit import PromotionReviewAuditEvent


class PromotionReviewRepository(ABC):
    """Persistence boundary for immutable promotion reviews and audit events."""

    @abstractmethod
    def get(self, review_id: str) -> PromotionReview | None:
        """Return a review by stable identifier, or None when unknown."""
        raise NotImplementedError

    @abstractmethod
    def save(self, review: PromotionReview) -> None:
        """Persist a review without permitting replacement of a different snapshot."""
        raise NotImplementedError

    @abstractmethod
    def list_for_evidence(self, evidence_id: str) -> tuple[PromotionReview, ...]:
        """Return review records for one immutable evidence identifier."""
        raise NotImplementedError

    @abstractmethod
    def append_audit_event(self, event: PromotionReviewAuditEvent) -> None:
        """Append an immutable governance audit event."""
        raise NotImplementedError

    @abstractmethod
    def list_audit_history(
        self, *, review_id: str | None = None
    ) -> tuple[PromotionReviewAuditEvent, ...]:
        """Return append-only governance history in stable insertion order."""
        raise NotImplementedError
