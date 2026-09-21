"""Deterministic projection of governed promotion lifecycle history."""

from dataclasses import dataclass

from tradeos.validation.promotion import (
    PromotionStage,
    PromotionStageTransition,
    allowed_next_stages,
)


@dataclass(frozen=True, slots=True)
class PromotionLifecycleProjection:
    """Immutable derived view of one strategy's governed promotion lifecycle."""

    strategy_id: str
    strategy_version: str
    initial_stage: PromotionStage
    current_stage: PromotionStage
    transitions: tuple[PromotionStageTransition, ...]

    def __post_init__(self) -> None:
        if not self.strategy_id.strip():
            raise ValueError("strategy_id must not be blank")
        if not self.strategy_version.strip():
            raise ValueError("strategy_version must not be blank")


def project_promotion_lifecycle(
    *,
    strategy_id: str,
    strategy_version: str,
    initial_stage: PromotionStage,
    transitions: tuple[PromotionStageTransition, ...],
) -> PromotionLifecycleProjection:
    """Reconstruct the deterministic current promotion stage from transition history."""
    if not strategy_id.strip():
        raise ValueError("strategy_id must not be blank")
    if not strategy_version.strip():
        raise ValueError("strategy_version must not be blank")

    current_stage = initial_stage
    seen_ids: set[str] = set()

    for transition in transitions:
        if transition.transition_id in seen_ids:
            raise ValueError("duplicate promotion transition")
        seen_ids.add(transition.transition_id)

        if transition.strategy_id != strategy_id:
            raise ValueError("promotion transition strategy lineage does not match")
        if transition.strategy_version != strategy_version:
            raise ValueError("promotion transition version lineage does not match")
        if transition.from_stage is not current_stage:
            raise ValueError("promotion transition history contains a broken stage chain")
        if transition.to_stage not in allowed_next_stages(current_stage):
            raise ValueError("promotion transition is not allowed")
        current_stage = transition.to_stage

    return PromotionLifecycleProjection(
        strategy_id=strategy_id,
        strategy_version=strategy_version,
        initial_stage=initial_stage,
        current_stage=current_stage,
        transitions=transitions,
    )
