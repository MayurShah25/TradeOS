"""Tests for deterministic promotion lifecycle projection."""

import pytest

from tradeos.validation import (
    PromotionLifecycleProjection,
    PromotionStage,
    PromotionStageTransition,
    project_promotion_lifecycle,
)


def make_transition(
    *,
    transition_id: str,
    strategy_id: str = "strategy-1",
    strategy_version: str = "1.0.0",
    from_stage: PromotionStage,
    to_stage: PromotionStage,
) -> PromotionStageTransition:
    return PromotionStageTransition(
        transition_id=transition_id,
        review_id=f"review-{transition_id}",
        evidence_id=f"evidence-{transition_id}",
        strategy_id=strategy_id,
        strategy_version=strategy_version,
        from_stage=from_stage,
        to_stage=to_stage,
    )


def test_empty_history_projects_initial_stage() -> None:
    projection = project_promotion_lifecycle(
        strategy_id="strategy-1",
        strategy_version="1.0.0",
        initial_stage=PromotionStage.RESEARCH,
        transitions=(),
    )

    assert projection == PromotionLifecycleProjection(
        strategy_id="strategy-1",
        strategy_version="1.0.0",
        initial_stage=PromotionStage.RESEARCH,
        current_stage=PromotionStage.RESEARCH,
        transitions=(),
    )


def test_valid_history_reconstructs_current_stage() -> None:
    transitions = (
        make_transition(
            transition_id="t1",
            from_stage=PromotionStage.RESEARCH,
            to_stage=PromotionStage.BACKTEST,
        ),
        make_transition(
            transition_id="t2",
            from_stage=PromotionStage.BACKTEST,
            to_stage=PromotionStage.VALIDATION,
        ),
        make_transition(
            transition_id="t3",
            from_stage=PromotionStage.VALIDATION,
            to_stage=PromotionStage.PAPER,
        ),
        make_transition(
            transition_id="t4",
            from_stage=PromotionStage.PAPER,
            to_stage=PromotionStage.CONTROLLED_PROMOTION,
        ),
    )

    projection = project_promotion_lifecycle(
        strategy_id="strategy-1",
        strategy_version="1.0.0",
        initial_stage=PromotionStage.RESEARCH,
        transitions=transitions,
    )

    assert projection.current_stage is PromotionStage.CONTROLLED_PROMOTION
    assert projection.transitions == transitions


def test_rejects_wrong_initial_transition() -> None:
    transition = make_transition(
        transition_id="t1",
        from_stage=PromotionStage.BACKTEST,
        to_stage=PromotionStage.VALIDATION,
    )

    with pytest.raises(ValueError, match="broken stage chain"):
        project_promotion_lifecycle(
            strategy_id="strategy-1",
            strategy_version="1.0.0",
            initial_stage=PromotionStage.RESEARCH,
            transitions=(transition,),
        )


def test_rejects_strategy_or_version_lineage_mismatch() -> None:
    transition = make_transition(
        transition_id="t1",
        from_stage=PromotionStage.RESEARCH,
        to_stage=PromotionStage.BACKTEST,
        strategy_version="2.0.0",
    )

    with pytest.raises(ValueError, match="version lineage"):
        project_promotion_lifecycle(
            strategy_id="strategy-1",
            strategy_version="1.0.0",
            initial_stage=PromotionStage.RESEARCH,
            transitions=(transition,),
        )


def test_rejects_duplicate_transition() -> None:
    transition = make_transition(
        transition_id="t1",
        from_stage=PromotionStage.RESEARCH,
        to_stage=PromotionStage.BACKTEST,
    )

    with pytest.raises(ValueError, match="duplicate"):
        project_promotion_lifecycle(
            strategy_id="strategy-1",
            strategy_version="1.0.0",
            initial_stage=PromotionStage.RESEARCH,
            transitions=(transition, transition),
        )


def test_rejects_broken_stage_chain() -> None:
    transitions = (
        make_transition(
            transition_id="t1",
            from_stage=PromotionStage.RESEARCH,
            to_stage=PromotionStage.BACKTEST,
        ),
        make_transition(
            transition_id="t2",
            from_stage=PromotionStage.VALIDATION,
            to_stage=PromotionStage.PAPER,
        ),
    )

    with pytest.raises(ValueError, match="broken stage chain"):
        project_promotion_lifecycle(
            strategy_id="strategy-1",
            strategy_version="1.0.0",
            initial_stage=PromotionStage.RESEARCH,
            transitions=transitions,
        )


def test_rejects_transition_after_terminal_stage() -> None:
    transitions = (
        make_transition(
            transition_id="t1",
            from_stage=PromotionStage.PAPER,
            to_stage=PromotionStage.CONTROLLED_PROMOTION,
        ),
        make_transition(
            transition_id="t2",
            from_stage=PromotionStage.CONTROLLED_PROMOTION,
            to_stage=PromotionStage.PAPER,
        ),
    )

    with pytest.raises(ValueError, match="broken stage chain"):
        project_promotion_lifecycle(
            strategy_id="strategy-1",
            strategy_version="1.0.0",
            initial_stage=PromotionStage.PAPER,
            transitions=transitions,
        )
