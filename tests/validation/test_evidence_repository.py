"""Tests for immutable validation evidence persistence."""

from datetime import UTC, datetime

import pytest

from tradeos.infrastructure import SQLiteValidationEvidenceRepository
from tradeos.validation import (
    InMemoryValidationEvidenceRepository,
    ValidationEvidence,
    ValidationStage,
)


def make_evidence(
    *,
    evidence_id: str = "evidence-1",
    strategy_id: str = "moving-average-cross",
    strategy_version: str = "1.0.0",
    code_version: str = "commit-1",
) -> ValidationEvidence:
    return ValidationEvidence(
        evidence_id=evidence_id,
        strategy_id=strategy_id,
        strategy_version=strategy_version,
        dataset_version="dataset-1",
        configuration_version="config-1",
        code_version=code_version,
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
        gate_results=(
            (ValidationStage.BACKTEST, True),
            (ValidationStage.ROBUSTNESS, False),
        ),
        known_limitations=("drawdown threshold failed",),
    )


def test_in_memory_repository_preserves_evidence_and_lineage() -> None:
    repository = InMemoryValidationEvidenceRepository()
    evidence = make_evidence()
    repository.save(evidence)

    assert repository.get(evidence.evidence_id) == evidence
    assert repository.list_for_strategy("moving-average-cross") == (evidence,)
    assert repository.list_for_strategy("moving-average-cross", strategy_version="1.0.0") == (
        evidence,
    )


def test_in_memory_repository_rejects_replacement() -> None:
    repository = InMemoryValidationEvidenceRepository()
    repository.save(make_evidence())

    with pytest.raises(ValueError, match="immutable"):
        repository.save(make_evidence(code_version="different-commit"))


def test_sqlite_repository_round_trips_all_lineage_and_failure_details(tmp_path) -> None:
    database = tmp_path / "validation.db"
    evidence = make_evidence()

    with SQLiteValidationEvidenceRepository(database) as repository:
        repository.save(evidence)

    with SQLiteValidationEvidenceRepository(database) as repository:
        assert repository.get("evidence-1") == evidence
        assert repository.list_for_strategy("moving-average-cross") == (evidence,)


def test_sqlite_repository_rejects_replacement_and_preserves_original(tmp_path) -> None:
    database = tmp_path / "validation.db"
    evidence = make_evidence()

    with SQLiteValidationEvidenceRepository(database) as repository:
        repository.save(evidence)
        with pytest.raises(ValueError, match="immutable"):
            repository.save(make_evidence(code_version="different-commit"))
        assert repository.get("evidence-1") == evidence
