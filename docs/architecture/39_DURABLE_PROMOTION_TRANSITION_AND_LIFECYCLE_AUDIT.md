# 39 — Durable Promotion Transition & Lifecycle Audit

## Purpose

This document defines the durable persistence boundary for governed promotion-stage transitions and their lifecycle audit history.

It extends the deterministic transition contract in 38_PROMOTION_STAGE_TRANSITION_BOUNDARY.md without expanding execution authority.

## Canonical Flow

Validation Evidence
        ↓
Promotion Review
        ↓
Promotion Stage Transition
        ↓
Persistent Transition Record
        ↓
Lifecycle Audit History

The transition record is the durable representation of one approved governance stage change. Lifecycle history makes that change reconstructable without using the execution audit trail.

## Invariants

1. A persisted transition preserves the exact transition, review, evidence, strategy, and stage lineage produced by the deterministic transition contract.
2. A transition identifier is immutable. Re-saving the exact same record is idempotent; replacing it with a different snapshot is rejected.
3. Lifecycle audit events are append-only and immutable by event identifier. Re-saving an identical event is idempotent; mutation is rejected.
4. An audit event must reference an existing transition and must preserve its review/evidence lineage.
5. Retrieval preserves stable insertion order so a strategy's promotion lifecycle can be reconstructed deterministically.
6. Lifecycle persistence does not authorize orders, bypass Risk, alter execution authorization, or enable live trading.
7. CONTROLLED_PROMOTION remains a lifecycle stage only; it is not an implicit live-trading or broker-execution permission.

## Repository Boundary

The PromotionTransitionRepository port owns durable storage behavior. Implementations are provided for deterministic in-memory tests and local SQLite persistence.

The repository supports retrieval by transition, strategy, and review, plus append-only lifecycle audit history. It intentionally does not merge with execution audit storage.

## Data Model

### Promotion transition

The persisted transition contains:

- transition_id
- review_id
- evidence_id
- strategy_id
- strategy_version
- from_stage
- to_stage

### Lifecycle audit event

The persisted event contains:

- event_id
- transition_id
- review_id
- evidence_id
- event_type
- actor_id
- occurred_at (UTC)
- detail

## Failure Semantics

- Unknown transition referenced by an audit event → reject.
- Review/evidence lineage mismatch → reject.
- Existing transition ID with different contents → reject as immutable.
- Existing event ID with different contents → reject as immutable.
- Blank stable identifiers → reject.
- Non-UTC lifecycle timestamps → reject.

## Non-Goals

This phase does not:

- add broker connectivity;
- authorize live orders;
- automatically advance stages;
- infer missing governance approvals;
- mutate prior lifecycle records;
- replace or weaken deterministic Risk controls;
- create a live-trading state machine.
