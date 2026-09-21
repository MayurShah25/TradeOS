# 43 — Paper Market Data Stream Boundary

**Status:** Implemented  
**Phase:** 6.2  
**Owner:** Market Data / Paper Trading Operations  
**Depends on:** Document 42 — Paper Market Data Integrity Boundary

## Purpose

Phase 6.2 adds a deterministic in-process stream boundary for paper-trading market data. It accepts immutable snapshots only when they belong to the configured instrument and source and arrive in strictly increasing observation-time order.

## Invariants

1. Stream instrument and source identities are explicit and nonblank.
2. Every accepted snapshot passes the Document 42 snapshot validation.
3. Instrument and source identities must match the stream.
4. The first valid snapshot is accepted.
5. Subsequent observations must have a strictly later observed_at.
6. Duplicate and out-of-order observations are rejected.
7. Rejected observations never replace the latest accepted state.
8. No implicit sorting, deduplication, price repair, timestamp repair, or source failover occurs.
9. The stream has no trading, risk, broker, portfolio, or authorization authority.

## State model

EMPTY → valid snapshot → LATEST(snapshot N) → strictly newer valid snapshot → LATEST(snapshot N+1)

Invalid, duplicate, or out-of-order input is rejected and current state is preserved.

## Safety boundary

This component is an operational data-integrity boundary only. It does not generate strategy signals, create trade proposals, approve risk, authorize execution, call brokers, mutate portfolio state, persist a second source of truth, automatically recover a failed source, or reorder historical observations.

Freshness remains governed by the explicit policy in Document 42. The stream establishes ordering and identity.

## Testing

Coverage includes first acceptance, ordered updates, duplicate/out-of-order rejection, identity mismatch, invalid snapshot fail-closed behavior, and state preservation.