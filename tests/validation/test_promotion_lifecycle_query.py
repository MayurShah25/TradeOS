from tradeos.validation.in_memory_promotion_repository import (
    InMemoryPromotionTransitionRepository,
)
from tradeos.validation.promotion import (
    PromotionStage,
    PromotionStageTransition,
)
from tradeos.validation.promotion_lifecycle_query import query_promotion_lifecycle


def _transition(
    transition_id: str,
    from_stage: PromotionStage,
    to_stage: PromotionStage,
) -> PromotionStageTransition:
    return PromotionStageTransition(
        transition_id=transition_id,
        review_id=f"review-{transition_id}",
        evidence_id=f"evidence-{transition_id}",
        strategy_id="strategy-1",
        strategy_version="v1",
        from_stage=from_stage,
        to_stage=to_stage,
    )


def test_query_projects_repository_history() -> None:
    repository = InMemoryPromotionTransitionRepository()
    repository.save(_transition("t1", PromotionStage.RESEARCH, PromotionStage.BACKTEST))
    repository.save(_transition("t2", PromotionStage.BACKTEST, PromotionStage.VALIDATION))

    projection = query_promotion_lifecycle(
        repository=repository,
        strategy_id="strategy-1",
        strategy_version="v1",
        initial_stage=PromotionStage.RESEARCH,
    )

    assert projection.current_stage is PromotionStage.VALIDATION
    assert projection.transitions == (
        _transition("t1", PromotionStage.RESEARCH, PromotionStage.BACKTEST),
        _transition("t2", PromotionStage.BACKTEST, PromotionStage.VALIDATION),
    )


def test_query_ignores_other_strategy_history() -> None:
    repository = InMemoryPromotionTransitionRepository()
    repository.save(_transition("t1", PromotionStage.RESEARCH, PromotionStage.BACKTEST))

    other = PromotionStageTransition(
        transition_id="other",
        review_id="review-other",
        evidence_id="evidence-other",
        strategy_id="strategy-2",
        strategy_version="v1",
        from_stage=PromotionStage.RESEARCH,
        to_stage=PromotionStage.BACKTEST,
    )
    repository.save(other)

    projection = query_promotion_lifecycle(
        repository=repository,
        strategy_id="strategy-1",
        strategy_version="v1",
        initial_stage=PromotionStage.RESEARCH,
    )

    assert projection.current_stage is PromotionStage.BACKTEST
    assert projection.transitions == (
        _transition("t1", PromotionStage.RESEARCH, PromotionStage.BACKTEST),
    )


def test_query_rejects_version_lineage_mismatch() -> None:
    repository = InMemoryPromotionTransitionRepository()
    repository.save(_transition("t1", PromotionStage.RESEARCH, PromotionStage.BACKTEST))

    try:
        query_promotion_lifecycle(
            repository=repository,
            strategy_id="strategy-1",
            strategy_version="v2",
            initial_stage=PromotionStage.RESEARCH,
        )
    except ValueError as exc:
        assert str(exc) == "promotion transition version lineage does not match"
    else:
        raise AssertionError("expected lineage mismatch to fail closed")


def test_query_is_read_only() -> None:
    repository = InMemoryPromotionTransitionRepository()
    repository.save(_transition("t1", PromotionStage.RESEARCH, PromotionStage.BACKTEST))

    query_promotion_lifecycle(
        repository=repository,
        strategy_id="strategy-1",
        strategy_version="v1",
        initial_stage=PromotionStage.RESEARCH,
    )

    assert repository.list_for_strategy("strategy-1") == (
        _transition("t1", PromotionStage.RESEARCH, PromotionStage.BACKTEST),
    )
