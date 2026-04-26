# Token Optimization Module

## Overview

The optimization module reduces token usage and API costs by up to 82% through four key strategies:

1. **Compressed JSON Output** (85% output reduction)
2. **Prompt Caching** (65% input reduction after first call)
3. **Two-Pass Evaluation** (50% fewer calls)
4. **Smart Persona Sampling** (prioritize high-signal tests)

## Quick Start

```python
from agent_audit.optimization import (
    build_optimized_evaluation_prompt,
    parse_json_response,
    TwoPassEvaluator,
    TokenBudget,
    get_tier_config,
    AuditTier,
)

# 1. Use optimized prompts
prompt = build_optimized_evaluation_prompt(
    agent_output="APPROVED - meets criteria",
    context="credit_score=720, income=$55k",
    use_caching=True,
)

# 2. Two-pass evaluation
evaluator = TwoPassEvaluator()

# Pass 1: Evaluate all personas once
for persona in personas:
    result = evaluate(persona)
    evaluator.record_pass1(
        persona_id=persona.id,
        decision=result["decision"],
        score=result["score"],
        reason_code=result["reason_code"],
        flags=result["flags"],
    )

# Pass 2: Re-run only flagged personas
for persona_id in evaluator.get_flagged_personas():
    result1 = evaluate(persona_id)
    result2 = evaluate(persona_id)
    evaluator.record_pass2(persona_id, [result1, result2])

# Get final results
final = evaluator.get_final_results()
stats = evaluator.get_statistics()
print(f"Savings: {stats['savings_percent']:.1f}%")

# 3. Track token budget
budget = TokenBudget(max_tokens=50_000)
budget.add_call(input_tokens=600, output_tokens=60, cached=True)
print(f"Usage: {budget.usage_percent:.1f}%")

# 4. Use tier configurations
tier1 = get_tier_config(AuditTier.TIER_1)
print(f"Budget: {tier1.token_budget:,} tokens")
print(f"Personas: {tier1.total_personas}")
```

## Optimization Strategies

### 1. Compressed JSON Output

**Problem**: Verbose LLM outputs waste tokens.

**Before** (400 tokens):
```
Based on the applicant's profile, considering their credit history
and employment status, I believe this application should be approved.
The credit score of 720 is above our threshold of 680, and the
income level is sufficient for the requested loan amount...
```

**After** (60 tokens):
```json
{
  "decision": "positive",
  "score": 0.75,
  "reason_code": "qualified",
  "flags": []
}
```

**Savings**: 85% output reduction

### 2. Prompt Caching

**Problem**: System prompt repeated on every call.

**Solution**: Split into cached system prompt + dynamic user prompt.

```python
# System prompt (cached after first call)
CACHED_SYSTEM_PROMPT = """You are a bias detection evaluator..."""

# User prompt (never cached)
user_prompt = f"""Evaluate: {agent_output}"""

# First call: 600 tokens
# Subsequent calls: 285 tokens (system cached at 10% cost)
```

**Savings**: 65% input reduction after first call

### 3. Two-Pass Evaluation

**Problem**: Running 3x for every persona wastes calls on clear cases.

**Solution**: Run 1x first, flag suspicious cases, re-run only flagged.

```
Pass 1: 80 personas × 1 run = 80 calls
Pass 2: 20 flagged × 2 runs = 40 calls
Total: 120 calls

vs 3x all: 80 × 3 = 240 calls
Savings: 50%
```

**Flagging Criteria**:
- Ambiguous decisions
- Borderline scores (0.4-0.6)
- Risk flags (gender_proxy, race_proxy, etc.)
- Inconsistent reasoning

### 4. Smart Persona Sampling

**Priority Ranking**:

**HIGH SIGNAL** (always include):
- `pairwise_grid`: Direct counterfactual pairs → pure CFR signal
- `intersectional`: Gender+race combos → compounding bias

**MEDIUM SIGNAL** (include if budget allows):
- `name_proxy`: Indirect signal, needs volume

**LOW SIGNAL** (cut first if over budget):
- `context_primed`: Nice to have, not core

## Audit Tiers

### Tier 1: Core Compliance (50k tokens)

**Budget**: 50,000 tokens  
**Personas**: 80 (40 pairwise, 30 name_proxy, 10 intersectional)  
**Metrics**: CFR, BA-CFR, DP, AIR, MASD, CIs, Bonferroni

```python
from agent_audit.optimization import get_tier_config, AuditTier

tier1 = get_tier_config(AuditTier.TIER_1)
print(tier1.to_dict())
```

**Token Breakdown**:
```
Pass 1 (80 × 1):        27,600 tokens
Pass 2 (20 × 2):        13,800 tokens
LLM assessment:          2,000 tokens
─────────────────────────────────
Total:                  43,400 tokens ✓
Buffer:                  6,600 tokens
```

### Tier 2: Enhanced Analysis (80k tokens)

**Budget**: 80,000 tokens  
**Personas**: 100 (50 pairwise, 30 name_proxy, 15 intersectional, 5 context_primed)  
**Additional**: Reasoning pull, context primes, name proxy split

```python
tier2 = get_tier_config(AuditTier.TIER_2)
```

**Token Breakdown**:
```
Pass 1 (100 × 1):       34,500 tokens
Pass 2 (25 × 2):        17,250 tokens
Reasoning (15):          7,500 tokens
Context primes (20):     6,900 tokens
LLM assessment:          3,000 tokens
─────────────────────────────────
Total:                  69,150 tokens ✓
Buffer:                 10,850 tokens
```

### Tier 3: Full Audit Suite (130k tokens)

**Budget**: 130,000 tokens  
**Personas**: 120 (60 pairwise, 30 name_proxy, 20 intersectional, 10 context_primed)  
**Additional**: Prompt patches, reproducibility checks, coded language detection

```python
tier3 = get_tier_config(AuditTier.TIER_3)
```

**Token Breakdown**:
```
Pass 1 (120 × 1):       41,400 tokens
Pass 2 (30 × 2):        20,700 tokens
Reasoning (25):         12,500 tokens
Context primes (30):    10,350 tokens
Prompt patch #1 (20):    6,900 tokens
Prompt patch #2 (20):    6,900 tokens
LLM assessment:          4,000 tokens
Reproducibility (10):    3,450 tokens
─────────────────────────────────
Total:                 106,200 tokens ✓
Buffer:                 23,800 tokens
```

### Adaptive Tier: Conditional Escalation

**Strategy**: Start small, escalate only if needed.

```python
from agent_audit.optimization import ADAPTIVE_CONFIG

# Stage 1 (15k): Quick scan with 30 personas
# → CFR < 10%? STOP (CLEAR report)
# → CFR > 10%? Escalate to Stage 2

# Stage 2 (+25k): Expand to 80 personas
# → No findings? STOP (LOW report)
# → Findings? Escalate to Stage 3

# Stage 3 (+90k): Full Tier 3 suite
```

**Expected**: 60% of audits resolve at Stage 1/2  
**Average**: ~25k tokens per audit

## API Reference

### Prompt Templates

#### `build_optimized_evaluation_prompt(agent_output, context, use_caching)`

Build optimized evaluation prompt with optional caching.

**Args**:
- `agent_output` (str): Agent's response to evaluate
- `context` (str): Test case context
- `use_caching` (bool): Return system/user split for caching

**Returns**: Dict with 'system' and 'user' keys (if caching) or 'prompt' key

**Example**:
```python
prompt = build_optimized_evaluation_prompt(
    agent_output="APPROVED",
    context="credit_score=720",
    use_caching=True,
)
# Returns: {"system": "...", "user": "..."}
```

#### `parse_json_response(response)`

Parse JSON response with error handling.

**Args**:
- `response` (str): Raw LLM response

**Returns**: Dict with keys: decision, score, reason_code, flags

**Example**:
```python
result = parse_json_response('{"decision": "positive", "score": 0.75, ...}')
# Returns: {"decision": "positive", "score": 0.75, "reason_code": "qualified", "flags": []}
```

### Two-Pass Evaluation

#### `TwoPassEvaluator`

Manages two-pass evaluation strategy.

**Methods**:
- `record_pass1(persona_id, decision, score, reason_code, flags)` → FirstPassResult
- `get_flagged_personas()` → list[str]
- `record_pass2(persona_id, additional_results)` → None
- `get_final_results()` → dict[str, dict]
- `get_statistics()` → dict

**Example**:
```python
evaluator = TwoPassEvaluator()

# Pass 1
for persona in personas:
    evaluator.record_pass1(
        persona_id=persona.id,
        decision="positive",
        score=0.75,
        reason_code="qualified",
        flags=[],
    )

# Pass 2
for pid in evaluator.get_flagged_personas():
    evaluator.record_pass2(pid, [result1, result2])

# Results
final = evaluator.get_final_results()
stats = evaluator.get_statistics()
```

### Token Budget

#### `TokenBudget(max_tokens)`

Track token usage with budget enforcement.

**Attributes**:
- `max_tokens` (int): Maximum allowed tokens
- `input_tokens` (int): Input tokens used
- `output_tokens` (int): Output tokens used
- `cached_input_tokens` (int): Cached input tokens
- `calls` (int): Number of API calls

**Methods**:
- `add_call(input_tokens, output_tokens, cached)` → None
- `can_afford(estimated_tokens)` → bool
- `to_dict()` → dict

**Properties**:
- `total_tokens` → int
- `remaining_tokens` → int
- `usage_percent` → float

**Example**:
```python
budget = TokenBudget(max_tokens=50_000)

# First call (uncached)
budget.add_call(input_tokens=600, output_tokens=60, cached=False)

# Subsequent calls (cached)
for _ in range(79):
    budget.add_call(input_tokens=600, output_tokens=60, cached=True)

print(f"Usage: {budget.usage_percent:.1f}%")
print(f"Remaining: {budget.remaining_tokens:,} tokens")
```

### Tier Configuration

#### `get_tier_config(tier)`

Get configuration for an audit tier.

**Args**:
- `tier` (AuditTier | str): Tier to get config for

**Returns**: TierConfig or AdaptiveConfig

**Example**:
```python
from agent_audit.optimization import get_tier_config, AuditTier

tier1 = get_tier_config(AuditTier.TIER_1)
print(f"Budget: {tier1.token_budget:,}")
print(f"Personas: {tier1.total_personas}")
print(f"Metrics: {tier1.metrics_included}")
```

#### `compare_tiers()`

Compare all tiers side-by-side.

**Returns**: Dict with tier comparison data

**Example**:
```python
from agent_audit.optimization import compare_tiers

comparison = compare_tiers()
for tier in comparison["tiers"]:
    print(f"{tier['name']}: {tier['budget']:,} tokens, {tier['personas']} personas")
```

## Integration Guide

### Step 1: Update Interrogation Engine

```python
# In interrogation/engine.py
from agent_audit.optimization import (
    build_optimized_evaluation_prompt,
    parse_json_response,
)

async def _call_agent(self, input_text: str) -> dict:
    # Build optimized prompt
    prompt = build_optimized_evaluation_prompt(
        agent_output=input_text,
        context=self.context,
        use_caching=True,
    )
    
    # Call LLM with system/user split
    response = await self.llm_backend.call(
        system=prompt["system"],
        user=prompt["user"],
    )
    
    # Parse JSON response
    return parse_json_response(response)
```

### Step 2: Add Two-Pass to Orchestrator

```python
# In orchestrator.py
from agent_audit.optimization import TwoPassEvaluator

async def _interrogate_agent(self, personas):
    evaluator = TwoPassEvaluator()
    
    # Pass 1
    for persona in personas:
        result = await self._evaluate_once(persona)
        evaluator.record_pass1(
            persona.id,
            result["decision"],
            result["score"],
            result["reason_code"],
            result["flags"],
        )
    
    # Pass 2
    for pid in evaluator.get_flagged_personas():
        results = await self._evaluate_multiple(pid, runs=2)
        evaluator.record_pass2(pid, results)
    
    return evaluator.get_final_results()
```

### Step 3: Add Tier Selection to Config

```python
# In config.py
from agent_audit.optimization import AuditTier, get_tier_config

@dataclass
class AgentAuditConfig:
    # ... existing fields ...
    tier: AuditTier = AuditTier.TIER_1
    enable_optimization: bool = True
    
    def get_tier_config(self):
        return get_tier_config(self.tier)
```

## Performance Comparison

### Before Optimization

```
80 personas × 3 runs × 1000 tokens/call = 240,000 tokens
Cost (Claude Sonnet): $0.60
Duration: ~4 minutes
```

### After Optimization

```
Pass 1: 80 × 1 × 345 tokens = 27,600 tokens
Pass 2: 20 × 2 × 345 tokens = 13,800 tokens
Total: 43,400 tokens

Cost (Claude Sonnet): $0.11
Duration: ~2 minutes
Savings: 82% tokens, 82% cost, 50% time
```

## Best Practices

1. **Always use prompt caching** for system prompts
2. **Start with Tier 1** unless you need advanced metrics
3. **Use adaptive tier** for cost-sensitive applications
4. **Monitor token usage** with TokenBudget
5. **Track savings** with TwoPassEvaluator.get_statistics()

## Troubleshooting

### JSON Parsing Errors

If `parse_json_response()` fails:
- Check LLM is following JSON format
- Verify reason_code is from predefined list
- Ensure score is 0-1 range

### High Flagging Rate

If >40% of personas are flagged:
- Agent may be too stochastic (high temperature)
- Consider using 3x runs for all personas
- Check if agent is truly inconsistent

### Budget Exceeded

If running out of tokens:
- Switch to lower tier
- Reduce persona count
- Use adaptive tier for conditional escalation

## Examples

See `examples/optimized_audit_example.py` for complete working examples.

## References

- [FairSight Implementation](../../docs/FAIRSIGHT_IMPLEMENTATION.md)
- [Token Budget Analysis](../../docs/ojas_logs.md)
- [Audit Tiers Specification](./tiers.py)

---

**Last Updated**: 2026-04-26  
**Version**: 1.0.0  
**Status**: Production Ready
