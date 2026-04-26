"""
agent_audit.optimization — Token & Cost Optimization
=====================================================

Internal optimization layer for reducing token usage and API costs.

Key optimizations:
    1. Compressed JSON output format (80% output reduction)
    2. Prompt caching support (65% input reduction after first call)
    3. Two-pass SSS evaluation (50% fewer calls)
    4. Smart persona sampling (prioritize high-signal tests)
    5. Conditional escalation (adaptive depth based on findings)

Sub-modules:
    - prompt_templates.py : Optimized prompts with JSON output
    - two_pass.py         : Two-pass evaluation strategy
    - caching.py          : Prompt caching utilities
    - budget.py           : Token budget management
    - tiers.py            : Tiered audit configurations
"""

from agent_audit.optimization.prompt_templates import (
    build_optimized_evaluation_prompt,
    parse_json_response,
)
from agent_audit.optimization.two_pass import (
    TwoPassEvaluator,
    should_flag_for_rerun,
)
from agent_audit.optimization.budget import (
    TokenBudget,
    estimate_call_tokens,
    track_usage,
)
from agent_audit.optimization.tiers import (
    AuditTier,
    get_tier_config,
    TIER_1_CONFIG,
    TIER_2_CONFIG,
    TIER_3_CONFIG,
)

__all__ = [
    "build_optimized_evaluation_prompt",
    "parse_json_response",
    "TwoPassEvaluator",
    "should_flag_for_rerun",
    "TokenBudget",
    "estimate_call_tokens",
    "track_usage",
    "AuditTier",
    "get_tier_config",
    "TIER_1_CONFIG",
    "TIER_2_CONFIG",
    "TIER_3_CONFIG",
]
