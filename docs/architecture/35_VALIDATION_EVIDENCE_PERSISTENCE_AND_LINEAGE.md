# TradeOS Validation Evidence Persistence and Lineage

**Document:** 35_VALIDATION_EVIDENCE_PERSISTENCE_AND_LINEAGE.md  
**Version:** 0.1.0  
**Status:** Architecture Baseline

## Purpose

Phase 5.3 makes validation evidence durable and auditable. The evidence snapshot created by Phase 5.2 remains immutable; persistence adds a durable record without adding approval or execution authority.

## Evidence flow

    Validation Run
         |
         v
    ValidationEvidence
         |
         +----------------------+
         |                      |
         v                      v
    In-Memory Repository    SQLite Repository
         |                      |
         +----------+-----------+
                    v
           Retrieval / Review

## Persisted lineage

Each evidence record retains:

- evidence identifier;
- strategy identity and exact strategy version;
- dataset version;
- configuration version;
- code version;
- UTC evidence generation timestamp;
- every recorded validation gate and result;
- known limitations, including failed-gate reasons.

The repository does not recompute or reinterpret the evidence.

## Immutability

An existing evidence_id cannot be replaced with a different evidence snapshot. Re-saving the exact same immutable snapshot is idempotent.

Retrieval returns the immutable domain object and never mutates stored evidence.

## Retrieval semantics

Evidence can be retrieved by stable evidence ID or listed by strategy, optionally filtered to an exact strategy version. Results preserve repository insertion order.

## Authority boundary

Persistence is evidence storage only. It cannot:

- approve a strategy;
- grant promotion;
- bypass deterministic Risk;
- authorize an order;
- enable live trading.

ELIGIBLE_FOR_REVIEW remains a governance input, not execution authority.

## Durable storage

SQLite stores structured lineage columns plus serialized gate results and limitations. A composite lineage index supports exact strategy/version lineage queries while the evidence ID remains the primary immutable key.

## Migration and compatibility

The Phase 5.3 repository owns its own validation_evidence table. It does not alter the existing paper-trading run or audit schemas. This isolates validation evidence persistence from execution state and keeps the execution authority boundary unchanged.
