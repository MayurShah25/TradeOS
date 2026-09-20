# TradeOS Validation Evidence from Research Results

**Document:** 34_VALIDATION_EVIDENCE_FROM_RESEARCH_RESULTS.md  
**Version:** 0.1.0  
**Status:** Architecture Baseline

## Purpose

Phase 5.2 removes manually asserted validation outcomes from the evidence boundary. Evidence gates are derived from deterministic Phase 4 research outputs and explicit, immutable threshold configurations.

## Evidence flow

```
BacktestResult
    ↓ calculate_metrics
BacktestMetrics ──────────────┐
                              │
RobustnessResult[]            │
    ↓ calculate_metrics       │
Scenario metrics ─────────────┤
                              ↓
WalkForwardFold[]
    ↓ aggregate metrics
WalkForwardMetrics
    ↓ walk-forward gate
WalkForwardValidationResult
                              ↓
                Validation Evidence
                              ↓
                 Promotion Eligibility
```

## Gate semantics

### BACKTEST

Derived from `BacktestMetrics` using explicit minimum trade count, minimum total return, and maximum drawdown thresholds.

### ROBUSTNESS

Every supplied robustness scenario must satisfy the configured minimum return and maximum drawdown thresholds. One failed scenario fails the robustness gate.

### OUT_OF_SAMPLE

The walk-forward out-of-sample fold returns are evaluated individually. The configured minimum fold count must be met and every fold must satisfy the minimum return threshold.

### WALK_FORWARD

Uses the existing deterministic `evaluate_walk_forward_gate` contract. Its thresholds remain separate from the out-of-sample fold-return gate.

## Evidence lineage

The builder requires:

- strategy identity and version;
- dataset version;
- configuration version;
- code version;
- evidence generation timestamp;
- actual Phase 4 metrics/results.

The builder does not accept a caller-supplied boolean for any implemented gate.

## Failure preservation

Failed gate reasons are stored in `known_limitations`. A failed result therefore remains part of the evidence record rather than being discarded.

## Authority boundary

The builder creates research evidence only.

It cannot:

- approve a strategy;
- bypass Risk;
- authorize an order;
- enable live trading;
- alter execution permissions.

`ELIGIBLE_FOR_REVIEW` remains a governance input, not execution authority.
