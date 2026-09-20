"""In-memory persistence adapter for immutable validation evidence."""

from tradeos.validation.evidence import ValidationEvidence
from tradeos.validation.repository import ValidationEvidenceRepository


class InMemoryValidationEvidenceRepository(ValidationEvidenceRepository):
    """Deterministic repository that rejects mutation of an existing evidence ID."""

    def __init__(self) -> None:
        self._items: dict[str, ValidationEvidence] = {}

    def get(self, evidence_id: str) -> ValidationEvidence | None:
        if not evidence_id:
            raise ValueError("evidence_id must not be empty")
        return self._items.get(evidence_id)

    def save(self, evidence: ValidationEvidence) -> None:
        existing = self.get(evidence.evidence_id)
        if existing is not None and existing != evidence:
            raise ValueError("validation evidence is immutable")
        self._items[evidence.evidence_id] = evidence

    def list_for_strategy(
        self,
        strategy_id: str,
        *,
        strategy_version: str | None = None,
    ) -> tuple[ValidationEvidence, ...]:
        if not strategy_id:
            raise ValueError("strategy_id must not be empty")
        if strategy_version == "":
            raise ValueError("strategy_version must not be empty")
        return tuple(
            evidence
            for evidence in self._items.values()
            if evidence.strategy_id == strategy_id
            and (strategy_version is None or evidence.strategy_version == strategy_version)
        )
