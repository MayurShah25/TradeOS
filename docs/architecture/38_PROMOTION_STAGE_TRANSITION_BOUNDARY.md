# TradeOS Promotion Stage Transition Boundary

**Document:** 38_PROMOTION_STAGE_TRANSITION_BOUNDARY.md  
**Version:** 0.1.0  
**Status:** Architecture Baseline

## Purpose

Phase 5.6 defines the deterministic stage transition that may follow a governance review. It turns an explicitly approved review into one narrowly defined lifecycle transition while preserving the separation between promotion governance and execution authority.

## Lifecycle

```
RESEARCH
   ↓
BACKTEST
   ↓
VALIDATION
   ↓
PAPER
   ↓
CONTROLLED_PROMOTION
```

Each arrow is an explicit, single-step transition. A strategy cannot skip stages through a governance review.

## Transition contract

A `PromotionStageTransition` records:

- transition identifier;
- review identifier;
- evidence identifier;
- strategy identifier and exact strategy version;
- source stage;
- target stage.

A transition is valid only when:

1. the referenced review is `APPROVED_FOR_NEXT_STAGE`;
2. the review is `ELIGIBLE_FOR_REVIEW`;
3. the target is the explicitly allowed next stage for the source;
4. the transition preserves exact review/evidence/strategy lineage.

Pending, rejected, or ineligible reviews cannot create a transition.

## Authority boundary

A promotion transition is a lifecycle/governance state change only.

It does not:

- authorize an order;
- grant execution permission;
- bypass deterministic Risk;
- enable live trading;
- connect to a broker;
- imply a profitable outcome;
- permit skipping validation or paper trading.

`CONTROLLED_PROMOTION` is deliberately terminal in Phase 5.6. There is no implicit `LIVE` or `AUTONOMOUS` stage.

Any future controlled-live capability requires a separate governed architecture change and must not be inferred from this transition contract.

## Deterministic behavior

The transition function contains no model inference, scoring, prediction, or discretionary override. The review decision is the governance input; the allowed stage graph is the deterministic authority.

The transition result is immutable. Later governance activity creates a new review and, if applicable, a new transition rather than mutating historical state.

## Failure behavior

If review approval, eligibility, lineage, or stage ordering is invalid, transition creation fails closed.

No fallback transition is inferred.

## Relationship to execution

The boundary remains:

```
Validation Evidence
        ↓
Promotion Review
        ↓
Promotion Stage Transition
        ↓
Execution Authorization
        ↓
Deterministic Risk / Execution Controls
        ↓
Execution
```

The arrows are conceptual workflow boundaries, not automatic authority grants. A promotion transition never substitutes for the downstream Risk Gate or execution authorization requirements.
