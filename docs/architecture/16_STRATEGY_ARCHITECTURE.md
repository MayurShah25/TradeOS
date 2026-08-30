# TradeOS Strategy Architecture

**Document:** 16_STRATEGY_ARCHITECTURE.md  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Strategy definitions, signals, rules, lifecycle, versions, regime compatibility, portfolio interaction, validation, deployment, and retirement

---

## 1. Purpose

The Strategy Architecture defines how TradeOS represents, evaluates, versions, validates, and deploys trading strategies.

The core principle is:

> **A strategy is a versioned, testable decision framework—not an agent's opinion.**

A strategy must be explicit enough to:

- Explain its logic
- Backtest its behavior
- Validate its assumptions
- Evaluate its risks
- Reproduce its decisions
- Monitor its production behavior
- Learn from its outcomes

---

# 2. Strategy Philosophy

TradeOS should distinguish:

```text
Strategy
  ≠
Signal
  ≠
Trade Proposal
  ≠
Prediction
  ≠
Risk Decision
  ≠
Execution
```

A strategy generates conditions or proposals.

It does not independently authorize execution.

---

# 3. Strategy Architecture

```text
Market Data
     ↓
Feature Layer
     ↓
Regime / Context
     ↓
Strategy
     ↓
Signal
     ↓
Trade Proposal
     ↓
Critic
     ↓
Portfolio
     ↓
Risk
     ↓
Execution
```

---

# 4. Strategy Definition

Every strategy should have:

```text
strategy_id
strategy_version
name
description
status
asset_classes
markets
instruments
timeframes
rules
parameters
risk_policy
regime_requirements
```

---

# 5. Strategy Identity

`strategy_id` should remain stable across versions.

Example:

```text
breakout_volume
```

Versions may be:

```text
breakout_volume.v1
breakout_volume.v2
breakout_volume.v3
```

---

# 6. Strategy Versioning

A material strategy change creates a new version.

Examples:

- Entry rule change
- Exit rule change
- Stop methodology change
- Signal calculation change
- Parameter methodology change
- Regime logic change

Historical trades must reference the version used.

---

# 7. Strategy Status

Possible statuses:

```text
DRAFT
RESEARCH
BACKTEST
VALIDATION
PAPER
APPROVED
PRODUCTION
PAUSED
DEGRADED
RETIRED
```

---

# 8. Strategy Lifecycle

```text
Idea
 ↓
Research
 ↓
Definition
 ↓
Backtest
 ↓
Robustness
 ↓
Out-of-Sample
 ↓
Walk-Forward
 ↓
Paper
 ↓
Approval
 ↓
Production
 ↓
Monitoring
 ↓
Pause / Revalidate / Retire
```

---

# 9. Strategy Scope

A strategy should explicitly define where it is intended to operate.

Examples:

```text
Asset Class
Market
Instrument
Timeframe
Trading Session
Regime
```

A strategy outside its declared scope should not automatically run.

---

# 10. Strategy Inputs

Inputs may include:

```text
Price
Volume
Volatility
Features
Market Regime
News/Event Context
Fundamentals
Prediction
Portfolio Context
```

Each input should have an identified source and timestamp.

---

# 11. Strategy Data Availability

All inputs must obey point-in-time rules.

The strategy must not use information that was unavailable at decision time.

---

# 12. Strategy Parameters

Parameters should be explicit.

Examples:

```text
lookback_period
breakout_threshold
volume_multiplier
stop_distance
target_distance
holding_period
```

---

# 13. Parameter Constraints

Each parameter should define:

```text
type
unit
minimum
maximum
default
required
```

---

# 14. Entry Rules

Entry logic should be explicit.

Example:

```text
IF
price > breakout_level
AND
volume > threshold
AND
regime == TRENDING
THEN
generate_signal
```

Exact strategy logic belongs in strategy implementation/configuration.

---

# 15. Exit Rules

Strategies should define:

```text
Profit Target
Stop Loss
Time Exit
Signal Reversal
Invalidation
Risk Exit
```

Risk exits may override strategy exits.

---

# 16. Invalidation Rules

A strategy should define conditions under which its thesis becomes invalid.

Examples:

```text
Breakout failure
Regime change
Data invalidity
Event risk
Time expiration
```

---

# 17. Signal

A signal represents a strategy condition.

Potential structure:

```text
signal_id
strategy_id
strategy_version
instrument_id
direction
strength
timestamp
conditions
evidence
```

---

# 18. Signal Strength

Signal strength should have defined semantics.

It should not be confused with:

```text
Probability of Profit
```

unless explicitly calibrated.

---

# 19. Signal Deduplication

Repeated market events should not unintentionally create duplicate signals.

Signals should have identifiers or deterministic deduplication rules.

---

# 20. Signal Expiration

Signals may become stale.

A signal should have:

```text
created_at
valid_until
```

where appropriate.

---

# 21. Trade Proposal

A strategy signal may become a trade proposal.

Potential fields:

```text
trade_proposal_id
strategy_id
strategy_version
instrument
direction
entry
stop
target
quantity_candidate
thesis
invalidation
created_at
```

The candidate quantity is not final authorization.

---

# 22. Strategy Does Not Own Final Quantity

Position sizing should be determined by the appropriate deterministic Risk/Portfolio process.

Strategy may provide:

```text
Preferred Risk/Reward
Suggested Structure
```

but should not bypass Risk.

---

# 23. Strategy and Prediction

Prediction may provide probabilistic information.

The strategy may use it as an input where defined.

Prediction does not replace strategy logic.

---

# 24. Strategy and Regime

A strategy should declare compatible regimes.

Example:

```text
Breakout Strategy
→ Trending
→ Breakout
```

A strategy may explicitly reject:

```text
Low-volatility range
```

if validated evidence supports that constraint.

---

# 25. Strategy and Market Regime

Regime compatibility should be tested, not assumed.

Research and validation should provide evidence for regime-specific behavior.

---

# 26. Strategy and Portfolio

The strategy should provide enough metadata for Portfolio to calculate:

- Exposure
- Strategy allocation
- Correlation
- Concentration
- Portfolio heat

---

# 27. Strategy and Risk

Risk evaluates the strategy proposal in context.

```text
Strategy
   ↓
Trade Proposal
   ↓
Portfolio Impact
   ↓
Risk
```

Risk can reject a strategy-generated trade.

---

# 28. Strategy and Execution

Execution receives an approved order intent only after the required gates.

Strategy should never call the broker directly.

---

# 29. Strategy and Learning

The Learning System should evaluate strategy behavior.

Examples:

```text
Repeated losses in regime X
Repeated late exits
Unexpected slippage
Prediction mismatch
```

Learning may recommend research or strategy changes.

---

# 30. Strategy and Research

Research generates candidate improvements.

```text
Research
 ↓
Strategy Candidate
 ↓
Validation
 ↓
Strategy Version
```

---

# 31. Strategy and Backtesting

Every production strategy should have a validation lineage.

```text
Strategy Version
 ↓
Validation
 ↓
Experiments
 ↓
Dataset Versions
```

---

# 32. Strategy Determinism

Where possible, strategy logic should be deterministic.

Given the same:

```text
Inputs
+
Configuration
+
Version
```

the strategy should produce the same result.

---

# 33. AI-Assisted Strategies

AI may assist with:

- Context interpretation
- Feature generation
- Regime interpretation
- Research
- Candidate generation

However, AI-generated logic must be explicitly bounded and validated.

---

# 34. LLM Strategy Boundary

An LLM should not silently invent strategy rules during live execution.

If dynamic reasoning is permitted, the permissible decision space must be defined.

---

# 35. Strategy Rule Registry

Rules may be stored in structured configuration.

Example:

```text
rule_id
strategy_id
strategy_version
condition
priority
action
```

---

# 36. Rule Priority

Where multiple rules interact, priority should be explicit.

Example:

```text
Safety Exit
    >
Risk Exit
    >
Strategy Invalidation
    >
Strategy Profit Target
```

Exact hierarchy should be defined by system governance.

---

# 37. Strategy Conflicts

If two strategy rules conflict:

```text
Conflict
 ↓
Deterministic Resolution
or
REVIEW
```

Do not allow arbitrary agent interpretation to resolve safety-critical conflicts.

---

# 38. Multi-Strategy Environment

TradeOS may run multiple strategies simultaneously.

Each strategy must maintain separate identity and performance tracking.

---

# 39. Strategy Interaction

Strategies may create overlapping exposure.

Portfolio must evaluate:

```text
Strategy A Exposure
+
Strategy B Exposure
```

before allowing additional risk.

---

# 40. Strategy Correlation

Track correlation among strategy returns where appropriate.

Two different strategies may still be effectively the same risk.

---

# 41. Strategy Allocation

Portfolio configuration may define strategy allocation constraints.

Examples:

```text
Maximum Strategy Exposure
Maximum Strategy Risk
Maximum Strategy Allocation
```

---

# 42. Strategy Capacity

A strategy may have limited capacity.

Consider:

- Liquidity
- Market impact
- Trade frequency
- Position size
- Execution quality

---

# 43. Strategy Scalability

Backtest performance at one capital level should not automatically imply the same performance at larger capital.

Capacity should be tested.

---

# 44. Strategy Transaction Costs

Strategies must be evaluated after:

- Fees
- Spread
- Slippage
- Market impact where relevant

---

# 45. Strategy Performance

Track:

```text
Return
Drawdown
Expectancy
Win Rate
Profit Factor
Turnover
Exposure
Risk-Adjusted Metrics
```

Performance should be evaluated by context.

---

# 46. Strategy Performance by Regime

Track:

```text
Strategy
+
Regime
→
Performance
```

This can identify regime-specific weaknesses.

---

# 47. Strategy Performance by Instrument

Track:

```text
Strategy
+
Instrument
→
Performance
```

A strategy may be strong on one instrument and weak on another.

---

# 48. Strategy Performance by Time

Track:

- Time of day
- Day
- Month
- Year
- Holding period

---

# 49. Strategy Drawdown

Monitor:

```text
Current Drawdown
Maximum Drawdown
Drawdown Duration
Recovery
```

---

# 50. Strategy Degradation

A production strategy may deteriorate.

Possible causes:

```text
Market Structure Change
Data Change
Execution Change
Parameter Drift
Strategy Crowding
Regime Shift
```

---

# 51. Strategy Health

Possible health states:

```text
HEALTHY
WATCH
DEGRADED
PAUSED
REQUIRES_REVALIDATION
RETIRED
```

---

# 52. Strategy Monitoring

Monitor:

- Performance
- Drawdown
- Trade frequency
- Signal frequency
- Slippage
- Regime distribution
- Prediction quality
- Execution quality

---

# 53. Strategy Drift

Compare current behavior with validated historical behavior.

Potential drift signals:

```text
Expectancy Decline
Win Rate Shift
Drawdown Increase
Signal Distribution Change
Execution Cost Increase
```

---

# 54. Revalidation Triggers

Revalidate when:

- Material code changes
- Rule changes
- Parameter changes
- Data source changes
- Model dependency changes
- Significant performance degradation
- Market structure changes

---

# 55. Strategy Pause

A strategy may be paused when:

```text
Risk Breach
Performance Degradation
Data Issue
Execution Issue
Validation Expiration
Operational Issue
```

Pause behavior should be deterministic.

---

# 56. Strategy Retirement

Retire a strategy when evidence no longer supports continued operation.

Retirement should preserve historical records.

---

# 57. Strategy Rollback

A strategy version should support rollback to a previously approved version.

```text
v3
 ↓
Problem
 ↓
v2
```

---

# 58. Strategy Shadow Mode

A new strategy may run without generating executable trades.

```text
Market
 ↓
New Strategy
 ↓
Shadow Signal
 ↓
Compare
```

---

# 59. Strategy Paper Mode

Paper mode should exercise the complete workflow without real financial exposure.

---

# 60. Strategy Production Promotion

Promotion requires:

```text
Research
 ↓
Backtest
 ↓
Robustness
 ↓
Out-of-Sample
 ↓
Walk-Forward
 ↓
Paper
 ↓
Review
 ↓
Approval
```

---

# 61. Strategy Approval Record

Record:

```text
strategy_id
strategy_version
validation_reference
risk_reference
approval_status
approved_by
approved_at
known_limitations
```

---

# 62. Strategy Configuration Snapshot

Each strategy decision should reference:

```text
strategy_version
configuration_version
configuration_hash
```

---

# 63. Strategy Audit

Historical decisions should reconstruct:

```text
Strategy Version
Inputs
Rules
Parameters
Signal
Trade Proposal
Risk Decision
Execution
Outcome
```

---

# 64. Strategy Explainability

A strategy should be able to state:

```text
Why Signal Was Generated
Which Rules Triggered
Which Inputs Were Used
Which Conditions Were Not Met
Why Proposal Was Invalidated
```

---

# 65. Strategy Rejection

A strategy signal may be rejected by:

```text
Critic
Portfolio
Risk
Execution
Data Quality
```

Rejection should record the reason.

---

# 66. Strategy Learning

Learning should evaluate:

```text
Expected Strategy Behavior
vs
Actual Strategy Behavior
```

Examples:

```text
Signal frequency too high
Exit behavior too slow
Performance weak in regime X
Execution cost higher than expected
```

---

# 67. Strategy Research Feedback

Learning may create new research questions.

```text
Observed Weakness
 ↓
Research Hypothesis
 ↓
Experiment
 ↓
Candidate Improvement
```

---

# 68. Strategy Parameter Learning

Parameter changes should never occur automatically from a single performance observation.

Parameter updates require:

```text
Evidence
+
Research
+
Validation
+
Approval
```

---

# 69. Strategy Overfitting Protection

Avoid continuously tuning a production strategy against its own recent performance.

This can create adaptive overfitting.

---

# 70. Strategy Change Budget

Where useful, limit the frequency of material strategy changes.

This makes performance evaluation more meaningful.

---

# 71. Strategy Experiment Lineage

Each strategy version should identify:

```text
parent_version
research_id
experiment_id
validation_id
```

---

# 72. Strategy Dependency Registry

A strategy may depend on:

```text
Features
Models
Market Data
Regime Classifier
Prediction
Execution Policy
```

Dependencies should be explicit.

---

# 73. Dependency Compatibility

A strategy should not activate if required dependencies are:

```text
Missing
Incompatible
Unvalidated
Disabled
```

---

# 74. Strategy Failure Modes

Potential failures:

```text
Missing Data
Stale Data
Invalid Feature
Regime Unknown
Prediction Unavailable
Portfolio State Stale
Risk Rejection
Execution Failure
```

Each should have defined behavior.

---

# 75. Strategy Fail-Safe Behavior

When required inputs are unavailable:

```text
ABSTAIN
```

or:

```text
NO SIGNAL
```

Do not invent substitutes.

---

# 76. Strategy Testing

Strategies should have:

- Unit tests
- Scenario tests
- Backtests
- Regression tests
- Robustness tests
- Out-of-sample tests
- Walk-forward tests
- Paper tests

---

# 77. Strategy Scenario Tests

Examples:

```text
Valid Setup
Weak Setup
Conflicting Signals
Missing Data
Stale Data
Extreme Volatility
Regime Change
Risk Rejection
Execution Failure
```

---

# 78. Strategy Regression Tests

A new version must be tested against prior expected behavior.

Changes in signal frequency or outcomes should be intentional and explainable.

---

# 79. Strategy Security

Strategy configuration must not allow:

- Credential access
- Unauthorized execution
- Risk bypass
- Permission escalation

---

# 80. Strategy Architecture Invariants

The following must remain true:

1. Strategies are versioned.
2. Strategy logic is explicit.
3. Inputs are point-in-time valid.
4. Signals are distinct from trade proposals.
5. Strategy does not own final risk authorization.
6. Strategy does not directly call brokers.
7. Risk can reject any strategy proposal.
8. Portfolio evaluates aggregate impact.
9. Material changes create new versions.
10. Historical strategy versions remain reconstructable.
11. Production strategies have validation lineage.
12. Strategy dependencies are explicit.
13. Invalid dependencies prevent activation.
14. Strategy failures fail safely.
15. Parameter changes require controlled validation.

---

# 81. Initial Strategy Implementation

The first implementation should focus on one deterministic strategy:

```text
Market Data
     ↓
Feature Calculation
     ↓
Strategy Rules
     ↓
Signal
     ↓
Trade Proposal
     ↓
Risk
     ↓
Paper Execution
```

Start with a simple, transparent strategy rather than a highly adaptive AI strategy.

---

# 82. Future Strategy Architecture

Later versions may support:

```text
Multi-Strategy Portfolios
Regime-Adaptive Strategies
ML-Assisted Signals
Dynamic Allocation
Strategy Ensembles
Automated Research
Adaptive Execution
```

All remain subject to validation and Risk.

---

# 83. Strategy Architecture Success Criteria

The Strategy System is successful when TradeOS can:

- Define strategies explicitly.
- Version every material change.
- Generate reproducible signals.
- Create structured trade proposals.
- Evaluate regime compatibility.
- Track strategy performance.
- Detect strategy degradation.
- Revalidate or pause strategies.
- Maintain strategy research lineage.
- Prevent strategy logic from bypassing Risk or Execution controls.

---

# 84. Related Documents

- `README.md`
- `rules.md`
- `docs/04_SYSTEM_ARCHITECTURE.md`
- `docs/05_AGENT_ARCHITECTURE.md`
- `docs/06_DATA_ARCHITECTURE.md`
- `docs/07_TRADING_WORKFLOWS.md`
- `docs/08_RISK_MANAGEMENT.md`
- `docs/09_PREDICTION_ENGINE.md`
- `docs/10_LEARNING_SYSTEM.md`
- `docs/11_BACKTESTING_AND_VALIDATION.md`
- `docs/12_EXECUTION_ARCHITECTURE.md`
- `docs/13_PORTFOLIO_ARCHITECTURE.md`
- `docs/14_MARKET_DATA_ARCHITECTURE.md`
- `docs/15_RESEARCH_ARCHITECTURE.md`
- `docs/20_AGENT_CONTRACTS.md`
- `docs/21_CONFIGURATION.md`

---

## Version History

| Version | Status | Description |
|---|---|---|
| 0.1.0 | Architecture Baseline | Initial TradeOS strategy architecture, including strategy definitions, signals, lifecycle, versioning, regime compatibility, validation, deployment, monitoring, and learning |

---

> **Strategy principle: make the logic explicit, make the evidence reproducible, make every version traceable, and never let strategy logic bypass portfolio, risk, or execution controls.**
