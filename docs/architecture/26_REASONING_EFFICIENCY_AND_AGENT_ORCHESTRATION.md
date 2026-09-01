# TradeOS Reasoning Efficiency and Agent Orchestration

**Document:** `26_REASONING_EFFICIENCY_AND_AGENT_ORCHESTRATION.md`  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Reasoning efficiency, bounded agent invocation, workflow orchestration, token efficiency, adaptive computation, and anti-loop safeguards

---

## 1. Purpose

TradeOS must use AI where reasoning creates meaningful value and deterministic software everywhere reasoning is unnecessary.

The objective is not simply to minimize tokens or minimize the number of AI calls.

The objective is:

> **TradeOS should learn to think more efficiently so it can trade better.**

Efficiency is valuable only when it preserves or improves decision quality.

---

# 2. Core Principle

> **Use the minimum necessary reasoning for the decision, while increasing reasoning when additional analysis is demonstrably valuable.**

This means TradeOS should continuously improve:

- What information it considers
- Which reasoning steps it performs
- When those steps are performed
- Which agents are actually relevant
- When additional critique is useful
- When deterministic rules can replace repeated reasoning
- When additional computation improves decision quality

---

# 3. Workflow, Not Agent Chatter

TradeOS is a **workflow system with specialized reasoning nodes**, not an unrestricted network of agents having conversations with one another.

Preferred model:

```text
Trigger
  ↓
Deterministic Workflow
  ↓
Cheap Eligibility Checks
  ↓
Required Reasoning Node
  ↓
Structured Output
  ↓
Deterministic Validation
  ↓
Next Required Step
```

Avoid:

```text
Agent A
  ↓
Agent B
  ↓
Agent C
  ↓
Agent A
  ↓
Agent B
  ↓
...
```

unless the workflow explicitly defines and controls the iteration.

---

# 4. Deterministic First

Where a question can be answered deterministically, TradeOS must not invoke an LLM merely for convenience.

Examples:

```text
Position sizing
P&L
Exposure
Drawdown
Risk limits
Order validation
State transitions
Reconciliation
Schema validation
Market-session checks
Configuration validation
```

These should be handled by deterministic services or engines.

---

# 5. Reasoning Nodes

AI agents should be invoked when interpretation, synthesis, critique, or adaptive reasoning is required.

Examples:

```text
Market interpretation
Technical synthesis
Fundamental interpretation
News interpretation
Regime assessment
Strategy reasoning
Prediction
Critique
Research synthesis
Learning analysis
Coaching
```

Each reasoning node must have a defined purpose and structured output contract.

---

# 6. Agent Invocation Policy

An agent should be invoked only when at least one of the following is true:

1. Its reasoning is explicitly required by the workflow.
2. A deterministic gate identifies a condition requiring interpretation.
3. A learned relevance policy determines that the agent is materially useful.
4. A governance rule requires independent review.
5. A contradiction requires additional reasoning.

Agent availability alone is not a reason to invoke an agent.

---

# 7. Progressive Computation

TradeOS should prefer cheap checks before expensive reasoning.

```text
Market Event
   ↓
Basic Data Validation
   ↓
Instrument Eligibility
   ↓
Liquidity / Session Checks
   ↓
Setup Detection
   ↓
Relevant Reasoning
   ↓
Governance
```

A workflow should terminate as soon as a deterministic condition makes further reasoning unnecessary.

---

# 8. Context Efficiency

Agents should receive the **minimum sufficient context**, not the entire system history.

Context should be selected according to:

```text
Task
Instrument
Time Horizon
Strategy
Market Regime
Relevant Evidence
Required History
```

Unrelated context should not be passed merely because it is available.

---

# 9. Context Quality Over Context Quantity

More context does not automatically mean better reasoning.

TradeOS should optimize for:

```text
Relevant Information
+
Correct Temporal Ordering
+
Reliable Provenance
+
Clear Contradictions
+
Appropriate Historical Context
```

rather than maximum context size.

---

# 10. Structured Agent Output

Reasoning agents should return structured results where practical.

Example:

```text
assessment
key_evidence
contradictory_evidence
uncertainty
recommendation
abstention_reason
required_next_step
```

Free-form prose may accompany the result for explanation, but downstream systems should rely on validated structured fields.

---

# 11. Agent-to-Agent Calls

Direct agent-to-agent invocation is not the default pattern.

Preferred:

```text
Workflow Service
      ↓
Agent A
      ↓
Structured Result
      ↓
Workflow Service
      ↓
Agent B
```

This keeps orchestration visible, bounded, auditable, and controllable.

An agent may request another reasoning capability only through an approved workflow/tool interface.

---

# 12. Bounded Iteration

Any reasoning loop must define:

```text
purpose
termination condition
maximum iterations
time budget
compute/token budget
quality threshold
```

A loop without an explicit termination condition is prohibited.

---

# 13. Contradiction Handling

Additional reasoning should be triggered by meaningful uncertainty or contradiction, not by a generic desire for more analysis.

Example:

```text
Technical Analysis
       ↓
Fundamental Analysis
       ↓
Material Contradiction
       ↓
Critic Agent
       ↓
Resolution / Abstention
```

If no material contradiction exists, another reasoning pass should not be invoked solely for completeness.

---

# 14. Adaptive Reasoning Depth

TradeOS may use different reasoning depths depending on the decision.

Example:

```text
LOW COMPLEXITY
→ deterministic filters

MEDIUM COMPLEXITY
→ one or two reasoning nodes

HIGH COMPLEXITY
→ additional independent analysis / critique

HIGH RISK
→ stronger governance and validation
```

Reasoning depth must never weaken safety controls.

---

# 15. Learning to Think More Efficiently

The Learning System should evaluate not only trade outcomes, but also the effectiveness of the reasoning process.

It may learn:

- Which agents are useful for which conditions
- Which evidence is predictive or redundant
- Which reasoning sequences improve decisions
- Which questions repeatedly fail to change outcomes
- Which contradictions deserve escalation
- Which deterministic filters can safely eliminate unnecessary reasoning
- Which additional analysis materially improves decision quality

---

# 16. Reasoning Efficiency Learning Loop

```text
Decision
  ↓
Reasoning Trace
  ↓
Outcome
  ↓
Evaluate Decision Quality
  ↓
Evaluate Reasoning Efficiency
  ↓
Identify Pattern
  ↓
Validate Pattern
  ↓
Recommend Workflow Improvement
  ↓
Governed Approval
  ↓
Updated Workflow / Policy
```

Learning recommendations must not silently change production workflows.

---

# 17. Efficiency Is Not the Objective Function

TradeOS must not optimize for:

```text
minimum tokens
minimum latency
minimum agent calls
```

at the expense of decision quality, safety, or robustness.

A more useful objective is conceptually:

```text
Decision Quality
───────────────
Reasoning Cost
```

subject to:

```text
Safety Constraints
Risk Constraints
Data Quality
Latency Requirements
Governance Requirements
```

---

# 18. Value of Additional Reasoning

Before an additional expensive reasoning call, the workflow should conceptually ask:

```text
Could this analysis materially change the decision?
        ↓
       YES → reason
        ↓
       NO → continue without it
```

This may be implemented using deterministic rules, learned relevance models, or workflow policy.

A learned relevance model is advisory and cannot bypass mandatory governance.

---

# 19. Caching and Reuse

Safe intermediate results may be reused when their validity conditions remain satisfied.

Examples:

```text
Instrument metadata
Market session state
Stable reference data
Validated feature calculations
Previously validated research artifacts
```

Time-sensitive reasoning should not be reused after its validity window expires.

---

# 20. Reasoning Trace

For important decisions, TradeOS should preserve a reasoning trace containing references to:

```text
workflow_id
agent_id
agent_version
prompt/configuration version where applicable
input references
output schema/version
reasoning step
latency
compute/token metadata where available
result
```

The trace is for audit and learning; it is not itself an authorization mechanism.

---

# 21. Agent Failure

If a required agent fails:

```text
Agent Failure
     ↓
Workflow Policy
     ├── Retry if justified
     ├── Use approved fallback
     ├── Degrade
     ├── Abstain
     └── Stop
```

Retrying indefinitely is prohibited.

---

# 22. Retry Policy

Retries must have:

```text
maximum attempts
backoff
reason
idempotency protection
termination condition
```

A retry must not duplicate financial actions.

---

# 23. Fallback Reasoning

A fallback agent or model may only be used if:

- It is explicitly approved for the task.
- Its output contract is compatible.
- Its reliability is known.
- Its use does not bypass governance.

Fallback is not permission to use an arbitrary model.

---

# 24. Abstention

Agents should be allowed to return:

```text
ABSTAIN
INSUFFICIENT_DATA
CONTRADICTORY
OUT_OF_SCOPE
REQUIRES_REVIEW
```

Abstention is a valid outcome, not necessarily a failure.

---

# 25. No Autonomous Agent Loop

Agents must not autonomously:

```text
spawn unlimited agents
modify their own permissions
modify their own system instructions
create unrestricted recursive workflows
increase their own reasoning budget
bypass workflow governance
```

---

# 26. Tool Calls

Agent tools should be narrowly scoped.

A reasoning agent should not receive tools for unrelated capabilities.

For example:

```text
Technical Agent
→ market analysis tools

Research Agent
→ research retrieval tools

Risk Review Agent
→ risk-context read tools

Execution Service
→ broker tools
```

---

# 27. Token/Compute Budgets

Where practical, workflows should define resource budgets:

```text
max_agent_calls
max_iterations
max_execution_time
max_context_size
max_compute_cost
```

Budgets are safeguards, not objectives.

If a decision requires more reasoning than the configured budget, the workflow should fail safely or request review rather than silently truncate critical analysis.

---

# 28. Efficiency Metrics

TradeOS may monitor:

```text
reasoning_calls_per_workflow
reasoning_cost
latency
context_size
repeated_analysis_rate
abstention_rate
additional-analysis usefulness
decision quality
false-positive analysis
false-negative analysis
```

These metrics should be evaluated together.

---

# 29. Learning Metrics

Learning should evaluate whether a reasoning change:

- Improves expected decision quality.
- Reduces avoidable reasoning.
- Preserves safety.
- Improves robustness.
- Reduces repeated mistakes.
- Improves calibration.
- Improves execution outcomes where causally attributable.

No single efficiency metric should be optimized in isolation.

---

# 30. Governance of Reasoning Changes

Changes to agent routing, prompts, reasoning depth, or workflow logic should be versioned.

Recommended path:

```text
Observation
 ↓
Hypothesis
 ↓
Experiment
 ↓
Validation
 ↓
Recommendation
 ↓
Approval
 ↓
Deployment
 ↓
Monitoring
```

---

# 31. Safety Boundary

Reasoning efficiency may optimize **how TradeOS thinks**, but it cannot weaken:

```text
Risk Limits
Execution Authorization
Permission Model
Kill Switches
Point-in-Time Integrity
Auditability
Data Quality Requirements
Human Approval Requirements
```

---

# 32. Core Invariants

1. Deterministic tasks must not be delegated to LLMs without justification.
2. Agents are bounded reasoning nodes, not unrestricted autonomous loops.
3. Workflow orchestration is deterministic and auditable.
4. Additional reasoning requires a defined reason.
5. Reasoning loops require explicit limits and termination conditions.
6. More tokens do not automatically mean better decisions.
7. Fewer tokens do not automatically mean better efficiency.
8. Learning may improve reasoning efficiency, but cannot bypass governance.
9. Reasoning optimization must not weaken risk or execution controls.
10. Production reasoning changes are versioned and governed.

---

## 33. Related Documents

- `04_SYSTEM_ARCHITECTURE.md`
- `05_AGENT_ARCHITECTURE.md`
- `10_LEARNING_SYSTEM.md`
- `20_AGENT_CONTRACTS.md`
- `22_DOMAIN_MODEL.md`
- `23_STATE_MACHINES.md`
- `24_EVENT_CONTRACTS.md`
- `25_AUTHORITY_AND_PERMISSION_MODEL.md`

---

**TradeOS Reasoning Principle**

> **Do not think less for the sake of efficiency. Learn what to think about, when to think about it, and how deeply to think—so TradeOS can make better decisions with disciplined computation.**
