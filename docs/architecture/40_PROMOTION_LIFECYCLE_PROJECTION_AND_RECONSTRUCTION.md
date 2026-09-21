# TradeOS Promotion Lifecycle Projection & Reconstruction

**Document:** `40_PROMOTION_LIFECYCLE_PROJECTION_AND_RECONSTRUCTION.md`  
**Version:** 0.1.0  
**Status:** Architecture Baseline

## Purpose

Phase 5.8 defines the deterministic read-side projection of a strategy's governed promotion lifecycle from immutable promotion-transition records.

It extends the durable transition history established by Phase 5.7 without creating new authority or mutating historical records.

## Canonical Flow

```
Immutable Promotion Transitions
          ↓
Deterministic Lifecycle Projection
          ↓
Current Promotion Stage + Ordered History
```

The projection is a derived view. The persisted transition repository remains the source of historical truth.

## Invariants

1. Projection is deterministic: the same ordered transition history produces the same result.
2. Historical transition records are never mutated by projection.
3. A projection must begin from an explicit initial stage.
4. The first transition must originate from the initial stage.
5. Every subsequent transition must originate from the previously projected stage.
6. A transition's strategy identity and version must remain consistent across the projected lifecycle.
7. Transition records must follow the legal stage graph defined by the deterministic promotion transition contract.
8. Duplicate transition identifiers are rejected.
9. Reordered, skipped, conflicting, or branching transition histories are rejected rather than silently normalized.
10. `CONTROLLED_PROMOTION` remains a lifecycle stage only; projection does not grant execution authority or live-trading permission.
11. Projection performs no model inference, scoring, approval, risk override, broker action, or stage mutation.

## Projection Model

The projection contains:

- strategy identifier;
- strategy version;
- initial stage;
- current stage;
- ordered immutable transition history.

An empty history is valid and represents the initial stage.

A non-empty history must form one contiguous legal path from the initial stage.

## Failure Semantics

- Empty strategy identifier or version → reject.
- Transition from the wrong source stage → reject.
- First transition not rooted at the requested initial stage → reject.
- Strategy identity/version mismatch → reject.
- Duplicate transition identifier → reject.
- Transition graph violation → reject.
- Any transition after terminal `CONTROLLED_PROMOTION` → reject through the legal transition contract.

The projection must fail closed. It must never invent a missing transition or infer a current stage from incomplete history.

## Repository Boundary

The projection consumes immutable transition records retrieved from `PromotionTransitionRepository`.

It does not persist a second source of truth. A future cache or materialized view must remain derivable from the durable transition history and must not replace it.

## Relationship to Governance and Execution

The lifecycle projection answers:

> "What governed promotion stage is supported by the recorded transition history?"

It does not answer:

> "May TradeOS place an order?"

Execution authorization, Risk, operating-mode controls, and broker-state validation remain independent downstream boundaries.

## Testing Requirements

Phase 5.8 requires tests covering:

1. empty lifecycle projection;
2. valid multi-stage reconstruction;
3. strategy lineage preservation;
4. invalid first-stage rejection;
5. broken stage-chain rejection;
6. strategy/version mismatch rejection;
7. duplicate transition rejection;
8. terminal-stage protection;
9. deterministic ordering;
10. no mutation of persisted transition records.

## Non-Goals

This phase does not:

- add broker connectivity;
- authorize live orders;
- automatically advance promotion stages;
- infer governance approvals;
- mutate historical transitions;
- create a live-trading state machine;
- replace deterministic Risk or execution authorization.
