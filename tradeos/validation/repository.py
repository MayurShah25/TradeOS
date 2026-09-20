"""Persistence port for immutable validation evidence."""

from abc import ABC, abstractmethod

from tradeos.validation.evidence import ValidationEvidence


class ValidationEvidenceRepository(ABC):
    """Persistence boundary for immutable validation evidence snapshots."""

    @abstractmethod
    def get(self, evidence_id: str) -> ValidationEvidence | None:
        """Return evidence by stable identifier, or None when unknown."""
        raise NotImplementedError

    @abstractmethod
    def save(self, evidence: ValidationEvidence) -> None:
        """Persist evidence without permitting replacement of a different snapshot."""
        raise NotImplementedError

    @abstractmethod
    def list_for_strategy(
        self,
        strategy_id: str,
        *,
        strategy_version: str | None = None,
    ) -> tuple[ValidationEvidence, ...]:
        """Return evidence in stable insertion order with optional version filtering."""
        raise NotImplementedError
