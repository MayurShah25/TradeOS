# TradeOS Agent Contracts

**Document:** 20_AGENT_CONTRACTS.md  
**Version:** 0.1.1  
**Status:** Architecture Baseline  
**Scope:** Agent interfaces, input/output contracts, permissions, tool usage, confidence, abstention, errors, handoffs, validation, and governance

---

## 1. Purpose

Agent Contracts define how TradeOS agents communicate with the rest of the system.

The core principle is:

> **An agent is a bounded component with a contract, not an unrestricted autonomous process.**

Agent contracts define interface behavior and bounded permissions; they do not create authority beyond permissions granted by system policy, Risk, Security, and execution controls.

Every production agent must have:

- A defined purpose
- Defined inputs
- Defined outputs
- Defined permissions
- Defined failure behavior
- Defined confidence semantics
- Defined escalation behavior
- Versioned instructions/configuration
- Testable contracts

---

# 2. Agent Contract Philosophy

Agents should:

```text
Observe
  ↓
Analyze
  ↓
Produce Structured Output
  ↓
Explain Evidence
  ↓
State Uncertainty
  ↓
Return Control
```

Agents should not silently:

- Change system rules
- Change risk limits
- Create unauthorized orders
- Invent missing data
- Treat assumptions as facts
- Modify their own production contract

---

# 3. Agent Taxonomy

Initial TradeOS agents:

```text
Orchestrator Agent
Market Context Agent
Technical Analysis Agent
Fundamental Analysis Agent
News/Event Agent
Market Regime Agent
Strategy Agent
Prediction Agent
Critic Agent
Portfolio Agent
Risk Agent
Execution Agent
Journal Agent
Learning Agent
Research Agent
Coach Agent
```

Some functions should remain deterministic services rather than agents.

---

# 4. Deterministic Services vs Agents

Use deterministic code for:

- Position sizing
- Risk calculations
- P&L
- Exposure
- Drawdown
- Order validation
- State transitions
- Reconciliation
- Schema validation

Use agents where reasoning or interpretation provides value.

---

# 5. Common Agent Contract

Every agent should expose conceptually:

```text
agent_id
agent_version
task
input_schema
output_schema
permissions
tools
constraints
timeout
cost_budget
failure_policy
authority_scope
authorization_context
```

---

# 6. Request Contract

An agent request should include:

```text
request_id
workflow_id
agent_id
agent_version
timestamp
task
context
inputs
constraints
deadline
```

---

# 7. Response Contract

An agent response should include:

```text
request_id
workflow_id
agent_id
agent_version
status
result
evidence
confidence
uncertainty
warnings
errors
created_at
```

---

# 8. Agent Status

Canonical statuses:

```text
SUCCESS
PARTIAL
ABSTAIN
INSUFFICIENT_DATA
REQUIRES_REVIEW
FAILED
TIMEOUT
REJECTED
```

---

# 9. Confidence Contract

Agents may provide confidence, but confidence must be explicitly defined.

Example:

```text
confidence:
  value: 0.72
  meaning: confidence in analytical conclusion
```

Confidence is not probability unless explicitly defined as calibrated probability.

---

# 10. Uncertainty Contract

Agents should identify uncertainty separately.

Example:

```text
uncertainty:
  level: HIGH
  reasons:
    - stale news
    - conflicting technical signals
```

---

# 11. Evidence Contract

Important conclusions should reference evidence.

Example:

```text
evidence:
  - source_id: market_data_123
    type: MARKET_DATA
  - source_id: news_456
    type: NEWS
```

An agent should distinguish:

```text
FACT
INFERENCE
ASSUMPTION
HYPOTHESIS
```

---

# 12. No Fabrication Rule

If an agent does not know something:

```text
UNKNOWN
```

or:

```text
INSUFFICIENT_DATA
```

must be returned.

The agent must not invent:

- Prices
- News
- Fills
- Positions
- Account balances
- Broker responses
- Historical events

---

# 13. Tool Contract

Each agent must declare the tools it can use.

Example:

```text
Market Context Agent
  allowed:
    market_data
    news_search
```

An agent must not access tools outside its permissions.

---

# 14. Tool Result Integrity

Agents must distinguish:

```text
Tool Result
```

from:

```text
Agent Interpretation
```

Tool results should not be silently altered.

---

# 15. Agent Permissions

Permissions should be explicit.

Possible permission classes:

```text
READ_MARKET_DATA
READ_PORTFOLIO
READ_RESEARCH
WRITE_ANALYSIS
WRITE_JOURNAL
REQUEST_RISK
REQUEST_EXECUTION
EXECUTE_ORDER
MODIFY_CONFIGURATION
```

High-impact permissions require stronger governance.

---

# 16. Least Privilege

Each agent should receive the minimum permissions necessary for its job.

Example:

```text
Technical Agent
→ market data

Risk Agent
→ portfolio/risk data

Execution Agent
→ execution interface
```

An analysis agent should not receive broker-order permissions.

---

# 17. Orchestrator Agent

### Purpose

Coordinate multi-agent workflows.

### Responsibilities

- Select agents
- Build context
- Manage sequencing
- Handle dependencies
- Collect outputs
- Detect missing responses
- Escalate failures

### Must Not

- Override Risk
- Directly bypass contracts
- Invent missing agent results

---

# 18. Market Context Agent

### Purpose

Provide broad market context.

Potential inputs:

- Market data
- Breadth
- Volatility
- Macro information
- Cross-asset information

Output:

```text
market_context
regime_candidates
key_observations
evidence
uncertainty
```

---

# 19. Technical Analysis Agent

### Purpose

Analyze price/volume behavior.

Potential outputs:

- Trend
- Support/resistance
- Momentum
- Volatility
- Pattern observations
- Setup evidence

It must distinguish calculated indicators from interpretation.

---

# 20. Fundamental Analysis Agent

### Purpose

Analyze fundamental information where applicable.

Potential outputs:

- Fundamental trend
- Valuation context
- Earnings context
- Financial changes
- Relevant risks

The agent must identify data dates and avoid using information unavailable at the decision time.

---

# 21. News/Event Agent

### Purpose

Identify and interpret relevant events.

Output should include:

```text
event
timestamp
source
relevance
sentiment/context
potential market impact
uncertainty
```

News relevance should not automatically imply trade direction.

---

# 22. Market Regime Agent

### Purpose

Classify the current market environment.

Possible outputs:

```text
TRENDING
RANGING
HIGH_VOLATILITY
LOW_VOLATILITY
BREAKOUT
REVERSAL
UNCERTAIN
```

Regime classification should include confidence and evidence.

---

# 23. Strategy Agent

### Purpose

Convert validated setup information into a strategy proposal.

Inputs:

- Market context
- Strategy rules
- Technical analysis
- Fundamental analysis where relevant
- Prediction
- Regime

Outputs:

```text
trade_proposal
strategy_id
strategy_version
thesis
entry
stop
target
invalidation
expected_scenarios
```

The Strategy Agent cannot approve its own risk.

---

# 24. Prediction Agent

### Purpose

Produce probabilistic scenarios.

Outputs may include:

```text
scenario
probability
horizon
expected_range
uncertainty
model_version
```

Prediction cannot authorize execution.

---

# 25. Critic Agent

### Purpose

Challenge the proposed decision.

Review:

- Evidence
- Contradictions
- Strategy compliance
- Prediction quality
- Risk assumptions
- Regime fit
- Data quality

Output:

```text
PASS
CONCERN
REJECT
```

The Critic should identify reasons, not merely disagree.

---

# 26. Portfolio Agent

### Purpose

Evaluate portfolio-level consequences.

Review:

- Existing positions
- Correlation
- Concentration
- Strategy exposure
- Directional exposure
- Margin/leverage context

Output:

```text
portfolio_impact
warnings
recommended_adjustments
```

It does not override hard Risk limits.

---

# 27. Risk Agent

### Purpose

Provide risk interpretation and recommendations.

The Risk Agent may identify:

- Risk concentration
- Event risk
- Liquidity risk
- Stress concerns
- Strategy-specific risk

However:

> **The deterministic Risk Engine remains authoritative for hard constraints.**

---

# 28. Execution Agent

### Purpose

Coordinate execution within explicit authorization.

The Execution Agent may:

- Prepare an order intent
- Validate execution conditions
- Submit through approved interfaces when explicit authorization is present
- Monitor status
- Request reconciliation

It must not independently decide that a trade should exist, create live authority, bypass Risk, or treat an agent recommendation as execution authorization.

---

# 29. Journal Agent

### Purpose

Record structured trade and workflow information.

The Journal Agent should preserve:

- Thesis
- Evidence
- Decisions
- Risk
- Execution
- Outcome
- Lessons

It should not rewrite historical facts.

---

# 30. Learning Agent

### Purpose

Identify potential learning opportunities.

It may:

- Detect repeated mistakes
- Find patterns
- Compare outcomes
- Recommend interventions
- Evaluate learning effectiveness

It must not silently activate safety-critical changes, grant permissions, weaken security controls, modify Risk limits, or authorize live execution.

---

# 31. Research Agent

### Purpose

Support strategy/model research.

It may:

- Form hypotheses
- Search evidence
- Propose experiments
- Analyze results
- Suggest validation paths

Research output is not production authorization.

---

# 32. Coach Agent

### Purpose

Provide human-facing feedback.

It may explain:

- What happened
- What went well
- What went wrong
- Repeated behaviors
- Relevant lessons

The Coach should distinguish facts from interpretation.

---

# 33. Agent Handoff Contract

When one agent passes work to another:

```text
source_agent
destination_agent
workflow_id
request_id
task
input_references
constraints
timestamp
```

The receiving agent should know what is authoritative and what is an interpretation.

---

# 34. Context Contract

Agent context should be structured into:

```text
SYSTEM RULES
TASK
FACTS
CALCULATIONS
PRIOR ANALYSIS
LEARNING
USER INPUT
```

Agents should not treat all context as equally authoritative.

---

# 35. Context Priority

A recommended authority hierarchy:

```text
Safety / System Rules
      ↓
Validated Data
      ↓
Deterministic Calculations
      ↓
Validated Strategy Rules
      ↓
Agent Analysis
      ↓
Unverified Hypotheses
```

---

# 36. Agent Disagreement

Disagreement should be preserved.

Example:

```text
Technical Agent → Bullish
Fundamental Agent → Neutral
News Agent → Bearish
```

The Orchestrator should not erase these differences.

The Critic may evaluate them.

---

# 37. Abstention

Every reasoning agent should be capable of abstaining.

Reasons may include:

```text
INSUFFICIENT_DATA
HIGH_UNCERTAINTY
CONFLICTING_EVIDENCE
OUT_OF_SCOPE
TOOL_FAILURE
OUT_OF_DISTRIBUTION
```

Abstention is valid behavior.

---

# 38. Error Contract

Errors should be structured.

Example:

```text
error_code
message
retryable
severity
source
```

Avoid returning only unstructured error text.

---

# 39. Retry Contract

Retries should depend on error type.

```text
Transient Tool Failure
→ Retry

Invalid Input
→ Do Not Retry

Permission Failure
→ Escalate

Unknown Execution State
→ Reconcile
```

---

# 40. Timeout Contract

Every agent call should have a timeout.

Timeout behavior:

```text
Timeout
  ↓
Record
  ↓
Retry if safe
  ↓
Fallback / Escalate
```

A timeout must not cause unsafe execution.

---

# 41. Cost Contract

Agents should have configurable budgets for:

- Tokens
- Tool calls
- Compute
- Time

Cost limits should prevent runaway workflows.

---

# 42. Agent Output Schema

Production agents should return machine-readable structured output.

Human-readable explanations may accompany structured data.

Example:

```text
result:
  decision: CONCERN
  reasons:
    - weak confirmation
    - high volatility
```

---

# 43. Schema Validation

Agent outputs should be validated before downstream use.

```text
Agent Output
     ↓
Schema Validation
     ↓
Accepted / Rejected
```

Malformed output should not silently enter execution workflows.

---

# 44. Versioning

Every production agent should have:

```text
agent_id
agent_version
prompt_version
tool_version
configuration_version
```

This allows historical reconstruction.

---

# 45. Prompt Versioning

Prompt changes can change agent behavior.

Therefore prompts should be:

- Versioned
- Tested
- Audited
- Promotable through validation

---

# 46. Agent Evaluation

Evaluate agents on:

- Accuracy
- Consistency
- Instruction following
- Hallucination
- Abstention
- Tool usage
- Latency
- Cost
- Safety
- Repeated mistakes

---

# 47. Agent Regression Tests

Every agent should have scenario tests.

Examples:

```text
Normal Input
Missing Data
Conflicting Data
Stale Data
Extreme Market
Invalid Request
Risk Rejection
Tool Failure
Prompt Injection Attempt
```

---

# 48. Agent Safety Tests

Agents must demonstrate:

```text
Cannot bypass Risk
Cannot fabricate broker state
Cannot fabricate market data
Cannot invent permissions
Cannot modify protected configuration
Cannot create unauthorized orders
```

---

# 49. Prompt Injection Resistance

External text such as:

- News
- Websites
- Documents
- Market commentary

must be treated as untrusted content.

An external source must not be allowed to redefine system instructions.

---

# 50. Tool Isolation

Tools should expose only required capabilities.

For example:

```text
Research Agent
→ research tools

Execution Agent
→ execution tools

Risk Agent
→ risk data
```

Tool access should be auditable.

---

# 51. Agent Memory

Agent memory should distinguish:

```text
Current Context
Historical Facts
Validated Learning
Unverified Hypotheses
```

An agent should not treat a speculative prior response as a permanent fact.

---

# 52. Learning Feedback

Agent performance outcomes should flow back into the Learning System.

```text
Agent Output
     ↓
Actual Outcome
     ↓
Performance Evaluation
     ↓
Pattern
     ↓
Learning Recommendation
```

---

# 53. Agent Self-Improvement Boundary

Agents may participate in:

```text
Self-Evaluation
Error Analysis
Improvement Recommendations
```

They may not independently deploy new production behavior.

---

# 54. Agent Promotion Lifecycle

```text
Prototype
 ↓
Contract Tests
 ↓
Scenario Tests
 ↓
Safety Tests
 ↓
Shadow
 ↓
Paper
 ↓
Evaluation
 ↓
Approval
 ↓
Production
```

---

# 55. Agent Health

Monitor:

- Availability
- Latency
- Error rate
- Timeout rate
- Cost
- Output validity
- Accuracy
- Abstention rate
- Safety violations

---

# 56. Agent Circuit Breaker

If an agent behaves abnormally:

```text
Anomaly
 ↓
Circuit Breaker
 ↓
Stop Agent
 ↓
Fallback / Escalate
```

The rest of the system should continue only if safe.

---

# 57. Agent Fallback

Fallbacks should be explicit.

Example:

```text
News Agent unavailable
      ↓
No News-Dependent Strategy
```

Do not silently replace a missing critical input with invented information.

---

# 58. Agent Authority Model

A simplified authority model:

```text
Analysis Agents
      ↓
Strategy Agent
      ↓
Critic
      ↓
Portfolio
      ↓
Risk
      ↓
Execution
```

No agent can skip a higher-priority safety boundary.

Agent-to-agent handoffs transfer data and recommendations, not authority. A downstream agent must obtain its own explicitly permitted authority from the governing system boundary.

---

# 59. Agent-to-Agent Trust

Agent output should not automatically be considered truth because another agent produced it.

Downstream agents should know:

```text
Source
Evidence
Confidence
Version
Timestamp
```

---

# 60. Structured Reasoning Boundary

Agents may reason internally, but production interfaces should expose structured conclusions rather than relying on hidden reasoning.

Required external artifacts include:

- Conclusions
- Evidence references
- Assumptions
- Confidence
- Uncertainty
- Decision/recommendation
- Warnings

---

# 61. Agent Audit Record

For important workflows, store:

```text
request
agent_version
context_reference
tools_used
tool_results_reference
output
decision
confidence
errors
timestamp
```

Sensitive data should be handled according to security policy.

---

# 62. Agent Contract Invariants

The following must remain true:

1. Every production agent has a contract.
2. Agent permissions are explicit.
3. Least privilege applies.
4. Agent output is schema-validated.
5. Agents can abstain.
6. Agents cannot fabricate facts.
7. Agents cannot bypass Risk.
8. Agents cannot independently change production rules.
9. External content is untrusted.
10. Agent versions are auditable.
11. Tool use is auditable.
12. Agent disagreements are preserved.
13. Agent failures have defined behavior.
14. Execution authority is separate from analysis authority.
15. Deterministic safety controls remain authoritative.
16. Agent contracts cannot grant authority that was not explicitly granted by the governing system.
17. Agent-to-agent handoffs transfer information and recommendations, not permissions or execution authority.
18. Learning feedback cannot directly authorize production behavior, modify Risk limits, or weaken security controls.
19. Observability or telemetry cannot grant permissions or mutate authoritative financial state.
20. Live execution requires explicit authorization independent of an agent's analytical recommendation.

---

# 63. Initial Agent Implementation

The first implementation should use a small number of agents:

```text
Orchestrator
   ↓
Technical
   ↓
Strategy
   ↓
Critic
   ↓
Risk
   ↓
Journal
```

Add:

```text
Prediction
Portfolio
News
Fundamental
Learning
Research
Coach
```

incrementally.

---

# 64. Agent Contract Testing

Before integrating an agent into the trading workflow:

```text
Schema Test
 ↓
Permission Test
 ↓
Failure Test
 ↓
Safety Test
 ↓
Scenario Test
 ↓
Shadow Test
```

---

# 65. Agent Architecture Success Criteria

The contract system is successful when TradeOS can:

- Add an agent without redesigning the platform.
- Validate agent outputs automatically.
- Control agent permissions.
- Track agent versions.
- Detect agent failures.
- Preserve agent disagreements.
- Evaluate agent performance.
- Learn from repeated agent mistakes.
- Prevent agents from bypassing Risk.
- Replace or disable an agent safely.
- Prevent agent coordination from creating an unbounded authority path.
- Preserve explicit authorization boundaries through agent handoffs.

---

# 66. Related Documents

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
- `docs/21_CONFIGURATION.md`

---

## Version History

| Version | Status | Description |
|---|---|---|
| 0.1.0 | Architecture Baseline | Initial TradeOS agent contracts, permissions, structured outputs, failure handling, safety boundaries, evaluation, and governance |
| 0.1.1 | Architecture Baseline | Clarified authority scope, explicit authorization context, bounded agent handoffs, and non-escalation boundaries across Risk, Security, Execution, Observability, and Learning |

---

> **Agent principle: every agent has a job, every job has boundaries, every output has evidence, and no agent is above the system's safety rules.**
