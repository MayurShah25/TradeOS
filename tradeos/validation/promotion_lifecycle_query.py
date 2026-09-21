"""Repository-backed read boundary for governed promotion lifecycle projection."""

from tradeos.validation.promotion import PromotionStage
from tradeos.validation.promotion_projection import (
    PromotionLifecycleProjection,
    project_promotion_lifecycle,
)
from tradeos.validation.promotion_repository import PromotionTransitionRepository


def query_promotion_lifecycle(
    *,
    repository: PromotionTransitionRepository,
    strategy_id: str,
    strategy_version: str,
    initial_stage: PromotionStage,
) -> PromotionLifecycleProjection:
    """Project one strategy lifecycle from immutable repository history.

    This is a read-side composition boundary: it loads immutable transitions
    and delegates all lifecycle validation to the deterministic projection.
    It never writes, advances, approves, authorizes, or executes anything.
    """
    transitions = repository.list_for_strategy(strategy_id)
    return project_promotion_lifecycle(
        strategy_id=strategy_id,
        strategy_version=strategy_version,
        initial_stage=initial_stage,
        transitions=transitions,
    )
