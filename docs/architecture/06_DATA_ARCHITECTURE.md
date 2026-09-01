# TradeOS Data Architecture

**Document:** 06_DATA_ARCHITECTURE.md  
**Version:** 0.2.0  
**Status:** Architecture Baseline  
**Scope:** Data domains, entities, relationships, storage, lineage, quality, retention, versioning, and learning-oriented data design

---

## 1. Purpose

This document defines how TradeOS stores, organizes, validates, relates, versions, and retrieves information.

The data architecture must support four fundamental requirements:

1. **Trading correctness**
2. **Full auditability**
3. **Reproducible research**
4. **Continuous learning from outcomes and repeated mistakes**

TradeOS must distinguish between:

- Market facts
- Derived calculations
- Agent interpretations
- Predictions
- Decisions
- Executions
- Outcomes
- Learning patterns

These categories must never be treated as interchangeable.

---

# 2. Data Architecture Principles

TradeOS data must be:

- Accurate
- Traceable
- Versioned
- Time-aware
- Auditable
- Reproducible
- Structured
- Secure
- Appropriately retained

The architecture should favor durable historical records over destructive updates.

---

# 3. Data Truth and Processing Model

TradeOS must distinguish information by both **provenance** and **authority**. The following represents the normal processing lineage; it is not a claim that later records are inherently more truthful than source records.

```text
                    SOURCE DATA
                        │
                        ▼
                 VALIDATED DATA
                        │
                        ▼
                DERIVED METRICS
                        │
                        ▼
               AGENT INTERPRETATION
                        │
                        ▼
                  PREDICTION
                        │
                        ▼
                 TRADE PROPOSAL
                        │
                        ▼
              RISK EVALUATION
                        │
                        ▼
                   EXECUTION
                        │
                        ▼
                     OUTCOME
                        │
                        ▼
                    LEARNING
```

Each record remains its own category of truth. For example, an execution record does not replace market-source truth, and a model prediction must never overwrite an actual historical price.

Authority is defined by the owning component and control boundary, not by position in this processing flow. In particular, hard risk constraints are authoritative through the deterministic Risk Engine and Risk Gate.

---

# 4. Primary Data Domains

The initial logical data domains are:

```text
Reference Data
Market Data
Instrument Data
Strategy Data
Agent Data
Prediction Data
Portfolio Data
Risk Data
Execution Data
Journal Data
Learning Data
Research Data
Configuration Data
Audit Data
System Data
```

---

# 5. Reference Data

Reference data describes relatively stable definitions used throughout the system.

Examples:

- Exchanges
- Markets
- Currencies
- Time zones
- Asset classes
- Trading sessions
- Order types
- Position sides
- Trade states
- Risk states

Reference data should be centrally defined rather than duplicated across modules.

---

# 6. Instrument Data

An instrument represents something TradeOS can analyze or potentially trade.

Examples:

- Equity
- ETF
- Index
- Futures contract
- Options contract
- Currency pair
- Cryptocurrency
- Commodity instrument

A normalized instrument should contain information such as:

```text
instrument_id
symbol
display_name
asset_class
market
exchange
currency
tick_size
lot_size
contract_size
expiry
strike
option_type
status
```

Market-specific fields may be optional.

---

# 7. Market Data

Market data represents observations from external sources.

Examples:

- Tick
- Quote
- OHLCV candle
- Order book snapshot
- Volume
- Open interest
- Corporate event
- Fundamental observation
- News event

Market data must retain source and timestamp information.

---

# 8. Market Data Timestamp Model

Important timestamps should include:

```text
event_time
source_time
received_time
processed_time
```

These are different concepts.

For example:

```text
Exchange generated tick
        ↓
Source timestamp
        ↓
TradeOS receives tick
        ↓
Receive timestamp
        ↓
TradeOS processes tick
        ↓
Processing timestamp
```

This is important for latency analysis and backtesting.

---

# 9. Data Freshness

Each real-time data object should have a freshness state.

Conceptually:

```text
FRESH
AGING
STALE
INVALID
UNKNOWN
```

Trading workflows must define acceptable freshness thresholds.

Stale data should not silently be treated as current data.

---

# 10. Data Quality

TradeOS should detect:

- Missing values
- Duplicate records
- Invalid timestamps
- Impossible prices
- Negative quantities where invalid
- Abnormal jumps
- Missing candles
- Out-of-order events
- Provider inconsistencies

Data-quality problems should be recorded rather than silently hidden.

---

# 11. Data Lineage

Important data should have lineage.

A derived value should be traceable to its inputs.

Example:

```text
Prediction
   ↓
Feature Set
   ↓
Indicators
   ↓
Market Data
   ↓
Data Provider
```

This allows historical results to be reconstructed.

---

# 12. Strategy Data

A strategy record should identify:

```text
strategy_id
strategy_version
name
description
asset_classes
markets
timeframes
entry_rules
exit_rules
risk_assumptions
parameters
status
created_at
updated_at
```

Strategy versions should be immutable once used in a historical production/paper decision.

---

# 13. Strategy Status

Potential statuses:

```text
DRAFT
RESEARCH
BACKTESTING
VALIDATION
PAPER
APPROVED
ACTIVE
PAUSED
RETIRED
REJECTED
```

Only appropriately approved strategies may participate in live execution.

---

# 14. Agent Data

Each agent should have a persistent definition.

Fields may include:

```text
agent_id
agent_version
name
category
purpose
model
capabilities
permissions
memory_scope
token_budget
timeout
status
```

Agent versions must be associated with important outputs.

---

# 15. Agent Output Data

Agent outputs should be stored in structured form.

Example:

```text
agent_output_id
workflow_id
agent_id
agent_version
model
input_reference
output_schema_version
output_payload
confidence
created_at
status
```

The raw model response may be retained when appropriate, but structured outputs should be the primary downstream interface.

---

# 16. Prediction Data

Predictions should be stored independently from trades.

A prediction may include:

```text
prediction_id
instrument_id
timestamp
horizon
model_id
model_version
scenario
probability
confidence
expected_range
features_reference
market_regime
created_at
```

Predictions should later be compared with actual outcomes.

---

# 17. Prediction Calibration Data

TradeOS should evaluate whether predicted probabilities correspond to actual frequencies.

Example:

```text
Predicted probability: 80%
Observed frequency over comparable cases: 63%
```

This may reveal model overconfidence.

Calibration data should be retained for model evaluation and learning.

---

# 18. Trade Proposal

A Trade Proposal represents a proposed trading decision before execution.

It should include:

```text
trade_proposal_id
workflow_id
instrument_id
strategy_id
strategy_version
direction
entry
stop
target
quantity
thesis
evidence
invalidations
prediction_reference
critic_reference
portfolio_reference
risk_reference
operating_mode
status
created_at
```

A proposal is not an order.

---

# 19. Trade Proposal States

Potential states:

```text
CREATED
ANALYZING
CRITIQUED
PORTFOLIO_REVIEWED
RISK_REVIEWED
PENDING_APPROVAL
APPROVED
REJECTED
EXPIRED
EXECUTED
CANCELLED
```

Historical state transitions should be auditable.

---

# 20. Risk Decision Data

Every risk evaluation should produce a durable record that preserves the distinct deterministic and contextual stages.

Fields may include:

```text
risk_decision_id
trade_proposal_id
account_id
equity
risk_amount
risk_percent
position_size
daily_loss
drawdown
portfolio_exposure
leverage
margin
risk_engine_result
risk_review_result
risk_gate_decision
reason_codes
risk_engine_version
risk_review_agent_version
created_at
```

The three risk fields have different meanings:

- `risk_engine_result` — deterministic evaluation of hard numerical constraints.
- `risk_review_result` — contextual review and reasoning from the Risk Review Agent.
- `risk_gate_decision` — deterministic enforcement decision governing whether execution may proceed.

A hard Risk Engine rejection cannot be converted into approval downstream.

---

# 21. Portfolio Data

Portfolio records should represent:

- Accounts
- Cash
- Positions
- Exposure
- Margin
- Leverage
- P&L
- Risk
- Correlations

Portfolio state should be reconstructable from underlying events where practical.

---

# 22. Position Data

A position should track:

```text
position_id
account_id
instrument_id
side
quantity
average_entry
current_quantity
realized_pnl
unrealized_pnl
opened_at
updated_at
status
```

Broker-reported state should remain distinguishable from internally expected state.

---

# 23. Order Data

Orders should include:

```text
order_id
client_order_id
broker_order_id
trade_proposal_id
instrument_id
side
quantity
price
order_type
time_in_force
status
filled_quantity
average_fill_price
submitted_at
updated_at
```

Order status changes should be recorded.

---

# 24. Fill Data

A fill represents actual execution.

Fields may include:

```text
fill_id
order_id
broker_fill_id
quantity
price
fees
timestamp
```

Trade P&L should ultimately be based on actual fills rather than intended prices.

---

# 25. Trade Record

A Trade represents the completed lifecycle of a trading decision.

It should connect:

```text
Trade
 ├── Strategy
 ├── Prediction
 ├── Agent Analysis
 ├── Critic
 ├── Portfolio
 ├── Risk
 ├── Orders
 ├── Fills
 ├── Position
 └── Outcome
```

---

# 26. Trade Journal

The Trade Journal should preserve the decision narrative.

Potential fields:

```text
journal_id
trade_id
trade_proposal_id
thesis
expected_scenario
actual_scenario
decision_quality
execution_quality
mistakes
lessons
user_notes
agent_notes
created_at
```

The journal should support both structured and human-readable information.

---

# 27. Decision Quality vs Outcome

TradeOS must explicitly distinguish:

```text
Good Decision + Loss
Bad Decision + Win
Good Decision + Win
Bad Decision + Loss
```

A loss does not automatically mean the decision was wrong.

A win does not automatically mean the decision was good.

This distinction is essential for learning.

---

# 28. Mistake Data

Mistakes should be represented as structured records.

Example:

```text
mistake_id
trade_id
category
type
severity
description
evidence
detected_by
confidence
created_at
```

Categories may include:

```text
TRADING
ANALYSIS
PROCESS
SYSTEM
AGENT
```

---

# 29. Mistake Taxonomy

Initial mistake types include:

### Trading

- Late entry
- Chasing
- FOMO
- Overtrading
- Stop widening
- Excessive risk
- Premature exit
- Holding invalidated trade

### Analysis

- Misread trend
- Ignored contradiction
- Indicator overreliance
- Poor regime interpretation
- Prediction overconfidence

### Process

- Missing confirmation
- Incomplete checklist
- Poor preparation
- Inadequate review

### System

- Data error
- Duplicate signal
- Incorrect calculation
- Position mismatch
- Order-state error

### Agent

- Repeated false positives
- Overconfidence
- Context misuse
- Failure to abstain
- Repeated analytical error

The taxonomy should evolve through versioned changes.

---

# 30. Pattern Candidate

A Pattern Candidate represents a possible recurring behavior.

Example:

```text
pattern_candidate_id
pattern_type
related_mistake_type
sample_count
affected_strategies
affected_markets
affected_regimes
evidence
confidence
status
created_at
```

Potential statuses:

```text
OBSERVED
CANDIDATE
VALIDATING
VALIDATED
REJECTED
RETIRED
```

---

# 31. Repeated-Mistake Learning

TradeOS must support learning from recurring mistakes.

Example:

```text
Trade #1
Late Entry

Trade #7
Late Entry

Trade #14
Late Entry

Trade #20
Late Entry
        ↓
Pattern Candidate
        ↓
Evidence Review
        ↓
Validated Pattern
        ↓
Learning Rule
        ↓
Future Detection
```

The system should measure whether intervention reduces recurrence.

---

# 32. Pattern Context

A repeated mistake may only occur under certain conditions.

Therefore patterns should capture context such as:

- Market
- Instrument
- Strategy
- Timeframe
- Market regime
- Volatility
- Session
- Time of day
- Direction
- Portfolio state
- User behavior
- Agent behavior

This prevents overly broad conclusions.

---

# 33. Learning Rule Data

A validated learning rule may contain:

```text
learning_rule_id
pattern_id
rule_type
description
scope
evidence
confidence
created_from
approval_status
activation_date
version
evaluation_metrics
```

A learning rule must have clear scope.

---

# 34. Learning Rule Examples

Examples:

```text
"Flag late entries occurring more than X% beyond the defined setup threshold."

"Require additional confirmation for breakout setups without sufficient volume."

"Warn when the user proposes a new trade immediately after a loss if historical behavior shows elevated error rates."
```

These examples are illustrative; exact thresholds must be validated before implementation.

---

# 35. Learning Rule Governance

Learning rules should follow:

```text
Observed
 ↓
Candidate
 ↓
Validated
 ↓
Proposed
 ↓
Approved
 ↓
Active
 ↓
Measured
 ↓
Retained / Modified / Retired
```

AI agents cannot silently activate a new safety-critical rule.

---

# 36. Agent Performance Data

TradeOS should maintain performance records for agents.

Example:

```text
agent_performance_id
agent_id
agent_version
metric
value
market
strategy
regime
time_period
sample_count
created_at
```

This supports questions such as:

> Which agent performs well in trending markets?

and:

> Which agent is consistently overconfident during high volatility?

---

# 37. Agent Learning

Agent performance should feed learning.

Example:

```text
Prediction Agent
      ↓
High-confidence predictions
      ↓
Outcome comparison
      ↓
Calibration analysis
      ↓
Repeated overconfidence
      ↓
Agent Pattern
      ↓
Learning Recommendation
```

The learning system may recommend:

- Reduced reliance
- Additional validation
- Different context
- Model replacement
- Retraining
- Human review

It may not silently deploy changes.

---

# 38. Memory Data

TradeOS memory should be divided into controlled categories.

```text
Workflow Memory
Operational Memory
Episodic Memory
Pattern Memory
Strategy Memory
Agent Memory
Learning Memory
```

Each memory type should have:

- Owner
- Scope
- Retention
- Access policy
- Version
- Confidence where applicable

---

# 39. Memory Confidence

Not all memories are equally reliable.

Memory records should distinguish, where appropriate:

```text
FACT
OBSERVATION
HYPOTHESIS
PREDICTION
VALIDATED_PATTERN
RECOMMENDATION
```

A hypothesis must never be treated as a fact.

---

# 40. Research Data

Research experiments should store:

```text
experiment_id
hypothesis
strategy_version
dataset
parameters
features
model
results
metrics
status
created_at
```

Research must remain traceable.

---

# 41. Backtest Data

A backtest run should contain:

```text
backtest_id
strategy_id
strategy_version
dataset_id
start_time
end_time
timeframe
parameters
transaction_costs
slippage
initial_capital
metrics
trade_count
results_location
software_version
created_at
```

---

# 42. Backtest Metrics

Potential metrics include:

- Net return
- CAGR where applicable
- Win rate
- Profit factor
- Expectancy
- Maximum drawdown
- Sharpe ratio
- Sortino ratio
- Average win
- Average loss
- Risk/reward
- Exposure
- Turnover
- Slippage impact

Metrics must not be interpreted without context.

---

# 43. Model Data

Prediction models should have versioned records.

Example:

```text
model_id
model_version
model_type
training_dataset
feature_set
training_period
validation_period
parameters
metrics
status
created_at
```

---

# 44. Configuration Data

Configuration versions should be stored or referenced for important runs.

Examples:

- Risk configuration
- Agent configuration
- Strategy configuration
- Market configuration
- Broker configuration
- Environment configuration

A historical decision should be traceable to the configuration active at that time.

---

# 45. Audit Data

Audit events should capture important state changes.

Examples:

```text
USER_LOGIN
CONFIG_CHANGED
STRATEGY_PROMOTED
MODEL_PROMOTED
TRADE_PROPOSED
RISK_APPROVED
RISK_REJECTED
ORDER_SUBMITTED
ORDER_FILLED
ORDER_CANCELLED
POSITION_RECONCILED
LEARNING_RULE_CREATED
LEARNING_RULE_APPROVED
KILL_SWITCH_ACTIVATED
```

---

# 46. Event Sourcing Consideration

TradeOS should consider event-based historical reconstruction for important trading state.

For example:

```text
Order Created
    ↓
Order Submitted
    ↓
Partial Fill
    ↓
Final Fill
    ↓
Position Updated
```

The architecture does not require complete event sourcing everywhere.

Use it where reconstruction and auditability materially benefit.

---

# 47. Database Technology

PostgreSQL is the intended primary relational datastore.

Potential supporting technologies may include:

- Redis for short-lived state/cache
- Object storage for large files/datasets
- Specialized time-series storage if scale eventually requires it

Technology decisions should be validated against actual workload before adding complexity.

---

# 48. Raw vs Normalized Data

Where practical, preserve both:

```text
Raw Source Data
      ↓
Normalized Data
      ↓
Derived Data
```

Raw data supports:

- Debugging
- Reprocessing
- Provider comparison
- Historical reconstruction

Normalized data supports application logic.

---

# 49. Data Immutability

Certain records should be treated as immutable after creation.

Examples:

- Historical fills
- Completed trades
- Historical risk decisions
- Agent outputs used in decisions
- Backtest results
- Strategy versions
- Model versions

Corrections should create additional records rather than silently altering history.

---

# 50. Data Retention

Retention policies should be defined by data class.

Potential categories:

```text
Critical Audit Data
Long-term / durable

Trade History
Long-term / durable

Strategy/Model Versions
Long-term / durable

Agent Performance
Long-term / durable

Raw High-Frequency Data
Policy-dependent

Temporary Agent Context
Short-term
```

Retention must balance auditability, storage cost, and privacy/security.

---

# 51. Data Access Control

Data access should follow least privilege.

For example:

```text
Technical Agent
→ Market Data

Risk Review Agent
→ Portfolio + Risk State

Execution Service / OMS
→ Approved Order + Execution State

Coach Agent
→ Learning + Journal

Learning Agent
→ Historical Outcomes + Performance
```

No agent should receive all data by default.

---

# 52. Personally Sensitive Information

TradeOS should minimize storage of unnecessary personal information.

User-specific trading information should be protected appropriately.

AI prompts should not include unnecessary sensitive data.

---

# 53. Data Quality States

Important datasets should support quality metadata.

Example:

```text
VALID
PARTIAL
STALE
SUSPECT
INVALID
UNAVAILABLE
```

Downstream components must respect these states.

---

# 54. Data Versioning

Where data can materially affect reproducibility, record:

- Provider
- Dataset version
- Retrieval timestamp
- Transformation version
- Schema version

A backtest should never rely on an undocumented mutable dataset.

---

# 55. Schema Versioning

Important data contracts should include schema versions.

Example:

```text
trade_proposal.v1
trade_proposal.v2
risk_decision.v1
agent_output.v1
```

Schema changes should be deliberate and documented.

---

# 56. Data Relationships

Core relationships should resemble:

```text
Market
  ↓
Instrument
  ↓
Market Data
  ↓
Strategy Run
  ↓
Trade Proposal
  ├── Agent Outputs
  ├── Prediction
  ├── Critic
  ├── Portfolio Review
  └── Risk Decision
          ↓
        Order
          ↓
        Fill
          ↓
       Position
          ↓
        Trade
          ↓
       Journal
          ↓
      Mistakes
          ↓
      Patterns
          ↓
   Learning Rules
```

This relationship is central to TradeOS.

---

# 57. Example Analytical Query

TradeOS should eventually be capable of answering:

> "Show every late-entry mistake over the last 12 months."

The system should be able to retrieve:

```text
Date
Instrument
Strategy
Market Regime
Entry
Expected Entry
Deviation
Outcome
P&L
Severity
Detection Source
Learning Rule
```

---

# 58. Example Learning Query

TradeOS should eventually answer:

> "Has the late-entry learning rule improved behavior?"

Conceptually:

```text
Before Intervention
    ↓
Late-entry frequency
    ↓
Intervention activated
    ↓
After Intervention
    ↓
Late-entry frequency
    ↓
Compare
```

This makes learning measurable rather than anecdotal.

---

# 59. Example Agent Query

TradeOS should eventually answer:

> "How reliable has the Prediction Agent been for breakout strategies in high-volatility conditions?"

The system should combine:

```text
Agent Version
+
Strategy
+
Market Regime
+
Prediction Probability
+
Actual Outcome
+
Calibration
+
Sample Size
```

---

# 60. Data Architecture Invariants

The following must remain true:

1. Source market data remains distinguishable from AI interpretation.
2. Predictions remain distinguishable from outcomes.
3. Proposed trades remain distinguishable from actual orders.
4. Intended positions remain distinguishable from broker positions.
5. Historical records remain reconstructable.
6. Important versions are recorded.
7. Data quality is explicit.
8. Agent access is least-privilege.
9. Learning is traceable to evidence.
10. Learning cannot silently rewrite history.
11. Hard Risk Engine results remain distinguishable from contextual Risk Review results.
12. Risk Gate decisions remain distinguishable from both Risk Engine and Risk Review outputs.
13. Execution state is owned by deterministic execution services/OMS rather than an autonomous reasoning agent.
14. Context selection should support efficient reasoning without indiscriminately expanding agent input.

---

# 61. Initial Data Implementation

The first implementation should not build every possible table.

Initial priority:

```text
Instrument
Market Data
Strategy
Trade Proposal
Risk Decision
Order
Fill
Position
Trade
Journal
Mistake
Learning Pattern
```

Then expand into:

```text
Agent Performance
Prediction Calibration
Research Experiments
Advanced Memory
Model Registry
Configuration Registry
```

This keeps the initial system manageable.

---

# 62. Data Architecture Success Criteria

The data architecture is successful when TradeOS can:

- Reconstruct important decisions.
- Trace trades to their evidence.
- Trace executions to proposals.
- Compare predictions with actual outcomes.
- Identify repeated mistakes.
- Measure whether learning works.
- Measure agent performance.
- Reproduce research results.
- Preserve historical truth.
- Prevent untrusted interpretations from becoming facts.
- Trace risk from deterministic evaluation through contextual review to the final gate decision.
- Assemble relevant context efficiently without treating token minimization as the sole objective.

---

# 63. Related Documents

- `README.md`
- `rules.md`
- `docs/01_PROJECT_VISION.md`
- `docs/02_DESIGN_PRINCIPLES.md`
- `docs/03_ENGINEERING_PRINCIPLES.md`
- `docs/04_SYSTEM_ARCHITECTURE.md`
- `docs/05_AGENT_ARCHITECTURE.md`
- `docs/07_TRADING_WORKFLOWS.md`
- `docs/08_RISK_MANAGEMENT.md`
- `docs/09_PREDICTION_ENGINE.md`
- `docs/10_LEARNING_SYSTEM.md`
- `docs/11_BACKTESTING_AND_VALIDATION.md`
- `docs/12_EXECUTION_ARCHITECTURE.md`
- `docs/20_AGENT_CONTRACTS.md`
- `docs/21_CONFIGURATION.md`

---

## Version History

| Version | Status | Description |
|---|---|---|
| 0.1.0 | Architecture Baseline | Initial TradeOS data architecture, including learning and repeated-mistake data structures |
| 0.2.0 | Architecture Baseline | Aligned risk-stage data, execution ownership, provenance semantics, and efficient-reasoning context principles |

---

> **Data principle: preserve what happened, distinguish what was inferred, connect decisions to outcomes, and make learning traceable to evidence.**
