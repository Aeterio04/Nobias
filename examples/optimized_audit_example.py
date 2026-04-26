"""
Example: Using Token Optimization for Cost-Efficient Audits

Demonstrates:
1. Optimized JSON output format (85% output reduction)
2. Two-pass evaluation (50% fewer calls)
3. Tiered configurations (50k, 80k, 130k budgets)
4. Token budget tracking
"""

import asyncio
import sys
import os
from pathlib import Path

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'library'))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / 'library' / '.env')

from agent_audit.optimization import (
    build_optimized_evaluation_prompt,
    parse_json_response,
    TwoPassEvaluator,
    TokenBudget,
    estimate_call_tokens,
    get_tier_config,
    AuditTier,
    compare_tiers,
)


async def simulate_agent_call(prompt: str) -> str:
    """
    Simulate an agent call (replace with real LLM call).
    
    In production, this would call your LLM backend.
    """
    # Simulated response in optimized JSON format
    return """{
  "decision": "positive",
  "score": 0.75,
  "reason_code": "qualified",
  "flags": []
}"""


async def example_optimized_evaluation():
    """Example: Single optimized evaluation."""
    print("=" * 80)
    print("EXAMPLE 1: Optimized Evaluation")
    print("=" * 80)
    print()
    
    # Agent output to evaluate
    agent_output = "APPROVED - Credit score meets requirements"
    context = "Applicant: credit_score=720, income=$55k"
    
    # Build optimized prompt
    prompt_parts = build_optimized_evaluation_prompt(
        agent_output=agent_output,
        context=context,
        use_caching=True,
    )
    
    print("System Prompt (cached after first call):")
    print(prompt_parts["system"][:200] + "...")
    print()
    
    print("User Prompt (never cached):")
    print(prompt_parts["user"][:200] + "...")
    print()
    
    # Simulate call
    response = await simulate_agent_call(prompt_parts["user"])
    
    print("Response (compact JSON):")
    print(response)
    print()
    
    # Parse response
    result = parse_json_response(response)
    print("Parsed Result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print()
    
    # Estimate tokens
    tokens = estimate_call_tokens(
        agent_output_length=len(agent_output),
        context_length=len(context),
        use_caching=True,
        is_first_call=False,
    )
    
    print("Token Estimate:")
    print(f"  Input (uncached):  {tokens['input']}")
    print(f"  Input (cached):    {tokens['effective_input']}")
    print(f"  Output:            {tokens['output']}")
    print(f"  Total (cached):    {tokens['total']}")
    print()
    print(f"💰 Savings: {tokens['input'] - tokens['effective_input']} tokens per call with caching")
    print()


async def example_two_pass_evaluation():
    """Example: Two-pass evaluation strategy."""
    print("=" * 80)
    print("EXAMPLE 2: Two-Pass Evaluation")
    print("=" * 80)
    print()
    
    evaluator = TwoPassEvaluator()
    
    # Simulate pass 1: Evaluate 10 personas once
    print("Pass 1: Evaluating 10 personas (1x each)...")
    personas = [
        ("persona_1", "positive", 0.8, "qualified", []),
        ("persona_2", "ambiguous", 0.5, "borderline", ["gender_proxy"]),  # Will flag
        ("persona_3", "negative", 0.2, "unqualified", []),
        ("persona_4", "positive", 0.9, "qualified", []),
        ("persona_5", "ambiguous", 0.45, "insufficient_data", []),  # Will flag
        ("persona_6", "positive", 0.75, "qualified", []),
        ("persona_7", "negative", 0.3, "unqualified", []),
        ("persona_8", "positive", 0.55, "borderline", []),  # Will flag
        ("persona_9", "positive", 0.85, "qualified", []),
        ("persona_10", "negative", 0.1, "unqualified", []),
    ]
    
    for persona_id, decision, score, reason, flags in personas:
        result = evaluator.record_pass1(persona_id, decision, score, reason, flags)
        if result.should_rerun:
            print(f"  ⚠️  {persona_id}: FLAGGED ({result.rerun_reason})")
        else:
            print(f"  ✓  {persona_id}: Clear")
    print()
    
    # Get flagged personas
    flagged = evaluator.get_flagged_personas()
    print(f"Pass 2: Re-running {len(flagged)} flagged personas (2x each)...")
    
    # Simulate pass 2: Re-run flagged personas
    for persona_id in flagged:
        # Simulate 2 additional runs
        run1 = {"decision": "positive", "score": 0.6}
        run2 = {"decision": "positive", "score": 0.55}
        evaluator.record_pass2(persona_id, [run1, run2])
        print(f"  ✓  {persona_id}: 2 additional runs completed")
    print()
    
    # Get final results
    final = evaluator.get_final_results()
    print("Final Results (with majority vote):")
    for persona_id, result in final.items():
        if result["flagged"]:
            print(f"  {persona_id}: {result['majority_decision']} "
                  f"(variance={result['decision_variance']:.2f}, runs={result['num_runs']})")
    print()
    
    # Statistics
    stats = evaluator.get_statistics()
    print("Evaluation Statistics:")
    print(f"  Total personas:     {stats['total_personas']}")
    print(f"  Flagged:            {stats['flagged_personas']} ({stats['flagged_percent']:.1f}%)")
    print(f"  Total calls:        {stats['total_calls']}")
    print(f"  Expected (3x all):  {stats['expected_calls_3x']}")
    print(f"  Calls saved:        {stats['calls_saved']}")
    print(f"  💰 Savings:         {stats['savings_percent']:.1f}%")
    print()


async def example_token_budget():
    """Example: Token budget tracking."""
    print("=" * 80)
    print("EXAMPLE 3: Token Budget Tracking")
    print("=" * 80)
    print()
    
    # Create budget for Tier 1 (50k tokens)
    budget = TokenBudget(max_tokens=50_000)
    
    print(f"Budget: {budget.max_tokens:,} tokens")
    print()
    
    # Simulate audit calls
    print("Simulating audit calls...")
    
    # First call (uncached)
    budget.add_call(input_tokens=600, output_tokens=60, cached=False)
    print(f"  Call 1 (uncached): {600 + 60} tokens")
    
    # Subsequent calls (cached)
    for i in range(2, 81):
        budget.add_call(input_tokens=600, output_tokens=60, cached=True)
    
    print(f"  Calls 2-80 (cached): {80 - 1} calls")
    print()
    
    # Budget stats
    stats = budget.to_dict()
    print("Budget Statistics:")
    print(f"  Total calls:        {stats['calls']}")
    print(f"  Input tokens:       {stats['input_tokens']:,}")
    print(f"  Output tokens:      {stats['output_tokens']:,}")
    print(f"  Total tokens:       {stats['total_tokens']:,}")
    print(f"  Remaining:          {stats['remaining_tokens']:,}")
    print(f"  Usage:              {stats['usage_percent']:.1f}%")
    print(f"  Avg per call:       {stats['avg_tokens_per_call']:.0f}")
    print()
    
    # Compare to uncached
    uncached_total = 80 * (600 + 60)
    savings = uncached_total - stats['total_tokens']
    print(f"💰 Savings vs uncached: {savings:,} tokens ({(savings/uncached_total)*100:.1f}%)")
    print()


async def example_tier_comparison():
    """Example: Compare audit tiers."""
    print("=" * 80)
    print("EXAMPLE 4: Audit Tier Comparison")
    print("=" * 80)
    print()
    
    comparison = compare_tiers()
    
    print("Available Tiers:")
    print()
    
    for tier_data in comparison["tiers"]:
        print(f"  {tier_data['name']}")
        print(f"    Budget:         {tier_data['budget']:,} tokens")
        print(f"    Personas:       {tier_data['personas']}")
        print(f"    Reasoning Pull: {'Yes' if tier_data['reasoning_pull'] else 'No'}")
        print(f"    Context Primes: {'Yes' if tier_data['context_primes'] else 'No'}")
        print(f"    Prompt Patches: {'Yes' if tier_data['prompt_patches'] else 'No'}")
        print(f"    Metrics:        {tier_data['metrics_count']}")
        print()
    
    # Show detailed config for Tier 1
    tier1 = get_tier_config(AuditTier.TIER_1)
    print("Tier 1 Detailed Configuration:")
    print(f"  Persona Breakdown:")
    for persona_type, count in tier1.persona_counts.items():
        print(f"    {persona_type:20s} {count}")
    print()
    print(f"  Metrics Included:")
    for metric in tier1.metrics_included:
        print(f"    • {metric}")
    print()


async def main():
    """Run all examples."""
    await example_optimized_evaluation()
    await example_two_pass_evaluation()
    await example_token_budget()
    await example_tier_comparison()
    
    print("=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print()
    print("1. JSON Output Format:  85% output reduction (400 → 60 tokens)")
    print("2. Prompt Caching:      65% input reduction after first call")
    print("3. Two-Pass Evaluation: 50% fewer calls (3N → 1.5N)")
    print("4. Combined Savings:    ~65% total token reduction")
    print()
    print("Example: 80 personas")
    print("  Before optimization: 80 × 3 × 1000 = 240,000 tokens")
    print("  After optimization:  ~43,000 tokens")
    print("  💰 Savings: 197,000 tokens (82%)")
    print()


if __name__ == "__main__":
    asyncio.run(main())
