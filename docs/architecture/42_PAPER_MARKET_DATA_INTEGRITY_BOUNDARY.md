# 42 — Paper Market Data Integrity Boundary

**Status:** Implemented  
**Phase:** 6.1  
**Owner:** Market Data / Paper Trading Operations  
**Depends on:** Global rules and Phase 3 paper-trading execution boundaries

## Purpose

Phase 6.1 establishes the first operational boundary for paper-trading market data. A paper execution workflow must consume an explicit, immutable market-data snapshot rather than an unstructured price value.

The boundary makes freshness, instrument identity, source identity, timestamp, and positive-price validity deterministic and auditable.

## Canonical flow

```text
Market Data Source
      ↓
Paper Market Data Snapshot
      ↓
Deterministic Freshness / Integrity Validation
      ↓
Paper Trading Workflow
```

## Snapshot contract

Each snapshot contains:

- `instrument_id`
- `price`
- `observed_at` as UTC
- `source_id`

Snapshots are immutable.

A snapshot is valid only when:

1. instrument identity is nonblank;
2. source identity is nonblank;
3. price is strictly positive;
4. timestamp is timezone-aware UTC;
5. the observation is not in the future relative to the validation clock;
6. its age does not exceed the configured maximum age.

## Safety behavior

Invalid or stale market data must fail closed.

The validator must not:

- repair a missing price;
- substitute another instrument's price;
- infer a timestamp;
- silently refresh data;
- call a broker;
- authorize an order;
- override Risk;
- convert stale data into a valid trading input.

A failed validation means the paper workflow must not use that snapshot for a trading decision.

## Freshness

Freshness is deterministic:

```text
age = validation_time - observed_at
valid when 0 <= age <= max_age
```

The caller supplies the validation clock explicitly so tests and audit behavior remain reproducible.

## Phase boundary

Phase 6.1 does not introduce:

- live broker connectivity;
- live orders;
- autonomous trading;
- risk overrides;
- automatic data-source failover;
- portfolio mutation;
- inferred prices;
- external market-data dependencies.

The next Phase 6 increments may compose this boundary into broader paper-trading operations and operational monitoring.

## Testing requirements

At minimum verify:

- valid snapshot acceptance;
- positive-price enforcement;
- UTC timestamp enforcement;
- future observation rejection;
- stale snapshot rejection;
- instrument/source identity validation;
- deterministic age calculation;
- immutable snapshot behavior.
