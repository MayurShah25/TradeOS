# TradeOS Market Data Architecture

**Document:** 14_MARKET_DATA_ARCHITECTURE.md  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Market-data ingestion, normalization, timestamps, providers, quality, freshness, historical data, streaming, caching, lineage, and data failure handling

---

## 1. Purpose

The Market Data Architecture defines how TradeOS receives, validates, normalizes, stores, and distributes market information.

The core principle is:

> **A trading decision is only as trustworthy as the data that was actually available when the decision was made.**

TradeOS must therefore know:

- What the data is
- Where it came from
- When it was generated
- When TradeOS received it
- Whether it is valid
- Whether it is fresh
- Whether it is complete
- Whether it was available at decision time

---

# 2. Market Data Philosophy

TradeOS should distinguish:

```text
Observed Data
    ≠
Derived Data
    ≠
Inferred Data
    ≠
Predicted Data
```

It should also distinguish:

```text
Event Time
    ≠
Ingestion Time
    ≠
Processing Time
    ≠
Decision Time
```

These distinctions are fundamental for backtesting, auditability, and learning.

---

# 3. Market Data Architecture

```text
External Providers
       ↓
Ingestion Layer
       ↓
Validation
       ↓
Normalization
       ↓
Canonical Data Model
       ↓
Storage / Cache
       ↓
Data Access Layer
       ↓
Agents / Strategies / Risk / Execution
```

---

# 4. Data Sources

Potential sources include:

```text
Price Data
Volume Data
Order Book Data
Corporate Actions
Reference Data
Economic Data
News
Fundamentals
Market Status
Broker Data
```

Each source should have an identified provider.

---

# 5. Provider Abstraction

TradeOS should not tightly couple business logic to a single data provider.

Conceptually:

```text
Market Data Interface
       ↓
Provider Adapter
       ↓
Provider A / B / C
```

This allows replacement or redundancy.

---

# 6. Provider Metadata

Every provider should have:

```text
provider_id
provider_version
supported_markets
supported_data_types
coverage
timestamp_semantics
update_frequency
status
```

---

# 7. Canonical Data Model

TradeOS should normalize provider-specific data into canonical structures.

Potential fields:

```text
instrument_id
event_time
ingestion_time
provider_id
data_type
value
sequence
quality_status
```

---

# 8. Instrument Identity

Instrument identity must be stable and unambiguous.

Provider symbols should map to canonical TradeOS instrument identifiers.

Example:

```text
Provider Symbol
      ↓
Instrument Mapping
      ↓
TradeOS Instrument ID
```

---

# 9. Symbol Mapping

Mappings may include:

```text
provider
provider_symbol
instrument_id
exchange
effective_from
effective_to
```

Historical mappings must be preserved.

---

# 10. Timestamp Model

Market events should retain multiple timestamps where available:

```text
event_time
source_time
ingestion_time
processing_time
```

Do not overwrite source timestamps with application timestamps.

---

# 11. Event Time

Event time represents when the market event occurred.

Examples:

```text
Trade Time
Quote Time
Bar Close Time
Order Book Update Time
```

---

# 12. Ingestion Time

Ingestion time represents when TradeOS received the event.

This enables latency measurement.

```text
ingestion_time - event_time
```

---

# 13. Processing Time

Processing time represents when TradeOS processed the event.

This can identify internal system latency.

---

# 14. Decision Time

Decision time represents when a trading workflow used the data.

A historical decision should never use data whose availability timestamp occurs after the decision time.

---

# 15. Data Availability Rule

A foundational invariant:

> **Information cannot be used before it was available to TradeOS.**

This applies to:

- Prices
- News
- Fundamentals
- Economic releases
- Corporate events
- Derived features

---

# 16. Real-Time Data

Real-time ingestion should support streaming where required.

Potential architecture:

```text
Provider Stream
      ↓
Message Bus
      ↓
Validation
      ↓
Normalization
      ↓
Consumers
```

---

# 17. Batch Data

Batch ingestion may be used for:

- Historical data
- Fundamentals
- Reference data
- Corporate actions
- Research datasets

Batch pipelines should preserve source metadata.

---

# 18. Historical Data

Historical datasets should be versioned.

Record:

```text
dataset_id
dataset_version
provider
coverage
created_at
adjustment_policy
quality_status
```

---

# 19. Historical Data Immutability

Once a dataset is used for an important backtest, its version should remain identifiable.

If the provider later revises data:

```text
Dataset v1
      ↓
Dataset v2
```

Do not silently replace the historical dataset used for previous results.

---

# 20. Data Adjustments

Where relevant, support:

```text
Raw Prices
Adjusted Prices
```

Adjustment methodology must be explicit.

---

# 21. Corporate Actions

Corporate-action data may include:

- Splits
- Dividends
- Mergers
- Spinoffs
- Symbol changes

Events should have effective dates and sources.

---

# 22. OHLCV Data

Canonical bars may contain:

```text
open
high
low
close
volume
event_time
instrument_id
```

The timeframe must be explicit.

Example:

```text
1m
5m
15m
1h
1d
```

---

# 23. Bar Construction

If TradeOS constructs bars from ticks, the methodology must be deterministic.

Define:

- Session boundaries
- Timezone
- Inclusion rules
- Missing intervals
- Late events

---

# 24. Tick Data

If tick data is supported, retain:

```text
timestamp
price
quantity
side where available
sequence where available
```

Tick-level storage may be optional depending on market scope.

---

# 25. Quote Data

Quotes may include:

```text
bid
bid_size
ask
ask_size
timestamp
```

Derived spread:

```text
ask - bid
```

must use clearly defined conventions.

---

# 26. Order Book Data

If supported:

```text
price
size
side
level
timestamp
sequence
```

Order-book snapshots and incremental updates must be distinguishable.

---

# 27. Data Sequence

Streaming sources may provide sequence identifiers.

TradeOS should use them where available to detect:

- Missing events
- Duplicates
- Out-of-order events

---

# 28. Duplicate Data

Duplicate events must not create duplicate downstream state.

Processing should be idempotent where possible.

---

# 29. Out-of-Order Data

Market events may arrive out of order.

TradeOS should preserve source event time and use controlled processing rules.

Do not blindly reorder data in a way that creates impossible historical states.

---

# 30. Missing Data

Missing data should be explicitly represented.

Do not silently fill gaps unless the filling methodology is defined.

---

# 31. Stale Data

Each data type should have a freshness policy.

Example:

```text
Latest Tick
      ↓
Freshness Check
      ↓
Fresh / Stale
```

A stale-data condition may block dependent decisions.

---

# 32. Data Freshness

Freshness may depend on:

```text
Data Type
Market
Instrument
Session
Provider
Strategy
```

Exact thresholds belong in configuration.

---

# 33. Data Quality Status

Possible statuses:

```text
VALID
STALE
MISSING
DUPLICATE
OUT_OF_ORDER
INVALID
SUSPECT
DEGRADED
```

---

# 34. Data Quality Score

Where useful, TradeOS may calculate a quality score from:

- Completeness
- Freshness
- Consistency
- Provider health
- Sequence integrity

Scores should not hide the underlying reasons.

---

# 35. Validation Rules

Validate:

- Numeric ranges
- Timestamp validity
- Instrument identity
- Price relationships
- Volume values
- Sequence continuity
- Required fields

---

# 36. OHLC Sanity Checks

For a normal OHLC bar:

```text
High ≥ Open
High ≥ Close
High ≥ Low

Low ≤ Open
Low ≤ Close
Low ≤ High
```

Invalid bars should be flagged.

---

# 37. Price Anomaly Detection

Potential anomalies:

- Impossible price
- Extreme discontinuity
- Negative price where invalid
- Zero price where invalid
- Unexpected tick size

An anomaly should be flagged rather than automatically discarded without trace.

---

# 38. Volume Validation

Validate:

- Non-negative volume
- Expected units
- Contract-specific interpretation
- Duplicate-event effects

---

# 39. Reference Data

Reference data should define:

```text
instrument
exchange
asset_class
currency
tick_size
lot_size
contract_multiplier
trading_calendar
```

---

# 40. Market Calendar

Market calendars should include:

- Trading days
- Sessions
- Holidays
- Early closes
- Special closures

Timezones must be explicit.

---

# 41. Market Status

Track states such as:

```text
PRE_OPEN
OPEN
HALTED
CLOSED
POST_MARKET
UNKNOWN
```

Execution must not assume a market is tradable solely because data is arriving.

---

# 42. News Data

News records should include:

```text
news_id
source
published_time
received_time
headline
content_reference
instrument_relevance
```

The original publication timestamp should be preserved.

---

# 43. Fundamental Data

Fundamental records should include:

```text
metric
value
period
announcement_time
effective_period
source
revision
```

This prevents revised information from leaking into historical decisions.

---

# 44. Economic Data

Economic releases should preserve:

```text
release_time
actual
consensus where available
previous
revision
source
```

Historical datasets should respect what was known at the time.

---

# 45. Data Revisions

Some data is revised after initial publication.

TradeOS should distinguish:

```text
As Initially Published
vs
Latest Revised Value
```

Backtesting should use the appropriate historical version.

---

# 46. Point-in-Time Data

Point-in-time datasets should answer:

> What information was available at timestamp T?

This is essential for unbiased research.

---

# 47. Data Lineage

Every important derived value should be traceable to:

```text
Source
Dataset Version
Transformation
Feature Version
Timestamp
```

---

# 48. Derived Features

Features may include:

```text
Moving Average
Volatility
Momentum
ATR
RSI
Breadth
Spread
```

Feature calculations should be deterministic and versioned.

---

# 49. Feature Versioning

Every feature definition should have:

```text
feature_id
feature_version
inputs
calculation_method
availability_rule
```

---

# 50. Feature Availability

A feature may only use information available at the relevant decision time.

Example:

```text
Daily Close Feature
```

must not be used at 2:00 PM if the daily close occurs at 4:00 PM.

---

# 51. Data Caching

Caching may improve performance.

Cache policies should define:

```text
TTL
staleness behavior
invalidation
provider
scope
```

A cache must never silently override fresher authoritative data.

---

# 52. Data Storage

Potential storage layers:

```text
Raw
Normalized
Derived
Feature
Aggregated
```

Keep raw source records where required for auditability.

---

# 53. Raw Data

Raw data should preserve provider representation where practical.

This supports:

- Reprocessing
- Debugging
- Audit
- Provider comparison

---

# 54. Normalized Data

Normalized data provides a common schema for TradeOS consumers.

Provider-specific quirks should be handled at the adapter/normalization boundary.

---

# 55. Data Retention

Retention should be defined by:

- Data type
- Cost
- Research requirements
- Audit requirements
- Legal requirements

---

# 56. Provider Redundancy

For critical data, TradeOS may support:

```text
Primary Provider
      ↓
Health Check
      ↓
Fallback Provider
```

Switching providers must preserve semantic consistency.

---

# 57. Provider Failover

A provider failure should not automatically mean:

```text
Use Any Available Data
```

Fallback data must pass compatibility and quality checks.

---

# 58. Provider Disagreement

If providers disagree materially:

```text
Provider A
Provider B
      ↓
Comparison
      ↓
Data Quality Event
```

The system may:

```text
Select trusted source
Degrade
Abstain
Escalate
```

---

# 59. Data Outage

If required market data becomes unavailable:

```text
Data Failure
     ↓
Dependent Workflow Detection
     ↓
ABSTAIN / BLOCK
```

Do not substitute fabricated or stale data silently.

---

# 60. Data Recovery

After an outage:

```text
Reconnect
 ↓
Backfill Missing Data
 ↓
Validate
 ↓
Reconcile
 ↓
Resume
```

---

# 61. Backfill

Backfills should be versioned and audited.

Do not silently alter already-audited decision records.

---

# 62. Streaming Recovery

After reconnecting to a stream:

```text
Reconnect
 ↓
Determine Last Known Sequence
 ↓
Request Missing Events
 ↓
Apply in Correct Order
 ↓
Resume Live Stream
```

If recovery is impossible:

```text
DEGRADED
```

---

# 63. Data Latency

Monitor:

```text
Source → TradeOS
TradeOS Ingestion → Processing
Processing → Decision
```

Latency should be recorded for relevant workflows.

---

# 64. Data Quality Monitoring

Monitor:

- Freshness
- Completeness
- Error rates
- Provider availability
- Sequence gaps
- Anomalies
- Latency

---

# 65. Data Quality Alerts

Alerts should be severity-based.

Example:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Critical data failure may block dependent trading.

---

# 66. Market Data and Risk

Risk calculations should know whether their inputs are:

```text
Fresh
Stale
Missing
Degraded
```

Risk should fail safely when critical inputs are unavailable.

---

# 67. Market Data and Strategy

Strategies should receive:

```text
Data
+
Timestamp
+
Quality
+
Availability
```

not just raw numbers.

---

# 68. Market Data and Prediction

Prediction models should receive the appropriate point-in-time feature set.

The model should not have access to future observations.

---

# 69. Market Data and Execution

Execution may require:

- Current price
- Spread
- Market status
- Liquidity
- Reference price

These inputs should be fresh enough for the configured execution policy.

---

# 70. Market Data and Learning

Learning should be able to determine:

> Was the information used by the decision actually correct and available at the time?

This prevents learning from corrupted historical inputs.

---

# 71. Market Data and Backtesting

Backtests must use datasets whose timestamp and revision semantics are known.

The simulator must preserve historical availability.

---

# 72. Data Snapshot

Important workflows may create a data snapshot reference:

```text
workflow_id
dataset_versions
feature_versions
snapshot_time
```

This supports reproducibility.

---

# 73. Decision Data Package

A decision may reference a package containing:

```text
Market Data
News
Fundamentals
Features
Regime
Data Quality
```

The package should be immutable for audit purposes.

---

# 74. Data Access Layer

Consumers should access data through stable interfaces.

Avoid allowing every agent to query provider APIs directly.

---

# 75. Data Access Permissions

Agents should receive only relevant data.

Example:

```text
Technical Agent
→ Market Price / Volume

News Agent
→ News

Fundamental Agent
→ Fundamental Data
```

---

# 76. Data Security

Protect:

- Provider credentials
- Premium data
- Licensed datasets
- Account-linked data
- Sensitive internal records

Do not expose credentials through agent context.

---

# 77. Licensed Data Controls

Where provider licenses restrict:

- Storage
- Redistribution
- Caching
- User access

TradeOS must respect those restrictions.

---

# 78. Data Reproducibility

A historical decision should allow reconstruction of:

```text
What data was available?
Which provider supplied it?
Which version was used?
What transformations occurred?
```

---

# 79. Data Failure Learning

Repeated data failures should feed the Learning System.

Examples:

```text
Provider outage
Repeated stale feed
Symbol mapping errors
Feature calculation errors
```

---

# 80. Market Data Architecture Invariants

The following must remain true:

1. Source timestamps are preserved.
2. Event time and ingestion time are distinct.
3. Point-in-time availability is respected.
4. Historical datasets are versioned.
5. Revised data is distinguishable from originally published data.
6. Data quality is explicit.
7. Stale data is never silently treated as fresh.
8. Missing data is never silently fabricated.
9. Provider failures are observable.
10. Derived features are versioned.
11. Instrument identity is canonical.
12. Critical data failures can block dependent workflows.
13. Backtests cannot use future information.
14. Data lineage is preserved.
15. Data consumers do not bypass the data-access boundary.

---

# 81. Initial Market Data Implementation

The first implementation should focus on:

```text
Provider
 ↓
Instrument Mapping
 ↓
Historical / Paper Data
 ↓
Canonical OHLCV
 ↓
Timestamp + Quality
 ↓
Data Access Interface
 ↓
Strategy / Risk
```

Then add:

```text
Streaming
Multiple Providers
Tick Data
Order Book
News
Fundamentals
Point-in-Time Dataset Engine
Advanced Data Quality Monitoring
```

---

# 82. Market Data Architecture Success Criteria

The Market Data System is successful when TradeOS can:

- Ingest market data reliably.
- Normalize provider differences.
- Track source and availability timestamps.
- Detect stale and invalid data.
- Preserve historical versions.
- Prevent look-ahead through point-in-time controls.
- Reconstruct decision-time data.
- Recover from provider outages.
- Support provider redundancy.
- Feed trustworthy data into Strategy, Risk, Prediction, Execution, and Learning.

---

# 83. Related Documents

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
- `docs/20_AGENT_CONTRACTS.md`
- `docs/21_CONFIGURATION.md`

---

## Version History

| Version | Status | Description |
|---|---|---|
| 0.1.0 | Architecture Baseline | Initial TradeOS market data architecture, including ingestion, normalization, point-in-time data, quality controls, provider abstraction, lineage, and failure handling |

---

> **Market data principle: know what was observed, know when it became available, know whether it was trustworthy, and never let tomorrow's information enter today's decision.**
