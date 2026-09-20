# TradeOS Durable Promotion Review and Governance Audit

**Document:** 37_DURABLE_PROMOTION_REVIEW_AND_GOVERNANCE_AUDIT.md  
**Version:** 0.1.0  
**Status:** Architecture Baseline

## Purpose

Phase 5.5 makes promotion review records durable while preserving the Phase 5 governance boundary. Review snapshots and governance audit events are immutable and remain separate from execution audit state.

## Governance flow

```
Validation Evidence
       |
       v
Promotion Review
       |
       +---------------------------+
       |                           |
       v                           v
Persistent Review Record    Governance Audit History
       |                           |
       +-------------+-------------+
                     v
              Promotion Review
                 Retrieval
```

## Review persistence

The review repository preserves:

- review identifier;
- exact evidence identifier;
- strategy identity and strategy version;
- deterministic eligibility;
- governance decision;
- reviewer identity when completed;
- UTC completion timestamp when completed;
- mandatory rationale.

A review identifier is immutable. Re-saving the exact same snapshot is idempotent. A different snapshot using an existing review identifier is rejected.

Multiple immutable review records may reference the same evidence when governance requires distinct review snapshots. The repository does not reinterpret or mutate prior decisions.

## Governance audit history

Audit events are immutable append-only records containing:

- event identifier;
- review identifier;
- evidence identifier;
- event type;
- actor identity;
- UTC occurrence timestamp;
- governance detail.

An audit event must reference an existing review and the same evidence identifier carried by that review. Re-saving the exact same event is idempotent; replacing an existing event identifier is rejected.

Audit history is ordered by repository insertion order and can be retrieved globally or for one review.

## Authority boundary

This persistence layer is governance storage only.

It cannot:

- authorize an order;
- bypass deterministic Risk;
- create execution authority;
- connect to a live broker;
- convert `APPROVED_FOR_NEXT_STAGE` into live-trading approval.

Execution audit events remain owned by the execution boundary. Governance audit history must not be added to the execution audit schema.

## Failure and immutability semantics

Persistence failures must not silently change a review decision. A rejected replacement leaves the original snapshot and audit history intact.

A later validation run produces new validation evidence. A later governance decision is represented by a new immutable review record rather than mutating an existing record.

## Durable storage

SQLite stores review records and governance audit events in dedicated tables. The review repository owns only its validation/governance tables and does not modify paper-trading or execution reconciliation schemas.

## Testing requirements

Phase 5.5 requires tests covering:

1. in-memory review round trip and lineage;
2. durable SQLite review round trip;
3. immutable review replacement rejection;
4. completed-review metadata preservation;
5. append-only audit ordering;
6. idempotent audit re-save;
7. audit rejection for unknown reviews;
8. audit rejection when evidence lineage does not match;
9. durable audit round trip;
10. preservation of original state after rejected mutation.
