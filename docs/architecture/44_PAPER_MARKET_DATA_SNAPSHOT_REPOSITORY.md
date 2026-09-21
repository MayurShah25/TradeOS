# 44 — Paper Market Data Snapshot Repository

**Status:** Implemented  
**Phase:** 6.3  
**Owner:** Market Data / Paper Trading Operations  
**Depends on:** Documents 42–43

## Purpose

Phase 6.3 establishes the persistence boundary for validated paper-market-data snapshots. Persistence is immutable, deterministic, and separate from the stream and from all trading authority.

## Canonical flow

```
Market Data Source
      ↓
Validated Snapshot
      ↓
Ordered Stream
      ↓
Immutable Snapshot Repository
      ↓
Paper Trading Operations
```

## Invariants

1. A snapshot must pass its deterministic validation before persistence.
2. The identity key is `instrument_id + source_id + observed_at`.
3. Re-saving the exact same snapshot is idempotent.
4. A different snapshot under an existing identity is rejected.
5. Retrieval is deterministic and observation-time ordered.
6. UTC timestamps are required at the persistence boundary.
7. Persistence does not alter, repair, reorder, or infer snapshot values.
8. The repository has no strategy, Risk, authorization, broker, or portfolio authority.
9. Repository state is historical data, not a signal or execution decision.

## Safety boundary

This repository does not:

- generate signals;
- calculate risk;
- authorize orders;
- call brokers;
- mutate portfolio state;
- silently replace observations;
- perform automatic source failover;
- convert stale observations into fresh ones.

Freshness remains the responsibility of the explicit validation policy in Document 42. Ordering remains the responsibility of Document 43.

## Testing

The implementation covers round-trip persistence, exact idempotent re-save, mutation rejection, deterministic ordering, source filtering, invalid-data rejection, and UTC lookup enforcement.
