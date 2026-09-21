# Promotion Lifecycle Query Boundary

**Status:** Implemented  
**Phase:** 5.9  
**Owner:** Promotion Lifecycle Governance  
**Depends on:** Documents 38, 39, and 40

## Purpose

Phase 5.9 adds a repository-backed read boundary for the governed promotion lifecycle. It composes the immutable promotion-transition repository with the deterministic lifecycle projection so callers can reconstruct the current stage and ordered transition history without directly coupling application code to persistence details.

The query boundary is read-side only. It does not create a second source of truth.

## Canonical flow

```text
Immutable Promotion Transition Repository
                ↓
      Promotion Lifecycle Query
                ↓
  Deterministic Lifecycle Projection
                ↓
 Current Stage + Ordered History
```

## Contract

`query_promotion_lifecycle(...)` requires:

- an existing `PromotionTransitionRepository`,
- explicit `strategy_id`,
- explicit `strategy_version`,
- explicit `initial_stage`.

It loads transitions for the requested strategy and delegates lineage and stage-chain validation to `project_promotion_lifecycle`.

## Invariants

1. Repository history is the only source of lifecycle transition records.
2. The query is deterministic for a given repository state and inputs.
3. No transition is created, changed, deleted, or reordered by the query.
4. Strategy version lineage is validated by the canonical projection.
5. Invalid, conflicting, or incomplete stage history fails closed.
6. The query cannot approve a strategy or authorize execution.
7. `CONTROLLED_PROMOTION` remains a lifecycle stage, not live-trading permission.
8. The query boundary does not connect to brokers or execution gateways.
9. No risk control can be bypassed through the query.
10. The result is an immutable `PromotionLifecycleProjection`.

## Read-only behavior

The query performs exactly one repository read operation: `list_for_strategy(strategy_id)`. It does not call repository write or audit methods.

The repository remains responsible for persistence semantics and stable retrieval order. The projection remains responsible for validating the legal lifecycle graph and exact strategy/version lineage.

## Failure semantics

The query fails closed when:

- the requested strategy/version is blank;
- repository history contains a transition for the strategy with a different version;
- the transition chain is broken;
- transition history violates the canonical promotion graph.

Empty history is valid and projects the explicitly supplied initial stage.

## Non-goals

Phase 5.9 does not add:

- automatic promotion advancement;
- promotion approval;
- execution authorization;
- live trading;
- broker connectivity;
- risk overrides;
- lifecycle mutation;
- inferred governance decisions;
- a new persistent lifecycle state machine.

## Testing requirements

The implementation must verify:

- repository-backed reconstruction;
- isolation from other strategy histories;
- version-lineage rejection;
- read-only behavior.

## Next boundary

Phase 5.9 completes the read-side composition of the durable promotion lifecycle. Phase 6 remains the next major roadmap phase: Paper Trading Operations.
