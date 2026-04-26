"""
agent_audit.optimization.tiers — Tiered Audit Configurations
=============================================================

Pre-configured audit tiers optimized for different token budgets.

Tier 1 (50k tokens):  80 personas, core metrics
Tier 2 (80k tokens):  100 personas, + reasoning analysis
Tier 3 (130k tokens): 120 personas, + prompt patches
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class AuditTier(str, Enum):
    """Audit tier levels."""
    TIER_1 = "tier_1"  # 50k budget
    TIER_2 = "tier_2"  # 80k budget
    TIER_3 = "tier_3"  # 130k budget
    ADAPTIVE = "adaptive"  # Conditional escalation


@dataclass
class TierConfig:
    """
    Configuration for an audit tier.
    
    Attributes:
        name: Tier name
        token_budget: Maximum tokens allowed
        persona_counts: Dict of persona type → count
        enable_reasoning_pull: Pull verbose reasoning for flagged cases
        enable_context_primes: Test with fairness preambles
        enable_prompt_patches: Test prompt modifications
        enable_reproducibility_check: Spot-check reproducibility
        two_pass_enabled: Use two-pass evaluation
        metrics_included: List of metrics to compute
    """
    name: str
    token_budget: int
    persona_counts: dict[str, int]
    enable_reasoning_pull: bool = False
    enable_context_primes: bool = False
    enable_prompt_patches: bool = False
    enable_reproducibility_check: bool = False
    two_pass_enabled: bool = True
    metrics_included: list[str] = None
    
    def __post_init__(self):
        if self.metrics_included is None:
            self.metrics_included = [
                "cfr",
                "ba_cfr",
                "demographic_parity",
                "eeoc_air",
                "masd",
                "confidence_intervals",
                "bonferroni",
            ]
    
    @property
    def total_personas(self) -> int:
        """Total personas across all types."""
        return sum(self.persona_counts.values())
    
    def to_dict(self) -> dict[str, Any]:
        """Export config as dict."""
        return {
            "name": self.name,
            "token_budget": self.token_budget,
            "total_personas": self.total_personas,
            "persona_counts": self.persona_counts,
            "enable_reasoning_pull": self.enable_reasoning_pull,
            "enable_context_primes": self.enable_context_primes,
            "enable_prompt_patches": self.enable_prompt_patches,
            "enable_reproducibility_check": self.enable_reproducibility_check,
            "two_pass_enabled": self.two_pass_enabled,
            "metrics_included": self.metrics_included,
        }


# ── Tier 1: 50k Token Budget ─────────────────────────────────────────────────

TIER_1_CONFIG = TierConfig(
    name="Tier 1 - Core Compliance",
    token_budget=50_000,
    persona_counts={
        "pairwise_grid": 40,      # 20 pairs → pure CFR signal
        "name_proxy": 30,         # Indirect bias detection
        "intersectional": 10,     # 2-way combos
    },
    enable_reasoning_pull=False,
    enable_context_primes=False,
    enable_prompt_patches=False,
    enable_reproducibility_check=False,
    two_pass_enabled=True,
    metrics_included=[
        "cfr",
        "ba_cfr",
        "demographic_parity",
        "eeoc_air",
        "masd",
        "confidence_intervals",
        "bonferroni",
    ],
)


# ── Tier 2: 80k Token Budget ─────────────────────────────────────────────────

TIER_2_CONFIG = TierConfig(
    name="Tier 2 - Enhanced Analysis",
    token_budget=80_000,
    persona_counts={
        "pairwise_grid": 50,      # 25 pairs
        "name_proxy": 30,         # Name-based testing
        "intersectional": 15,     # 2-way combos
        "context_primed": 5,      # Baseline for CPE
    },
    enable_reasoning_pull=True,   # Pull reasoning for 15 flagged cases
    enable_context_primes=True,   # Test fairness preambles
    enable_prompt_patches=False,
    enable_reproducibility_check=False,
    two_pass_enabled=True,
    metrics_included=[
        "cfr",
        "ba_cfr",
        "demographic_parity",
        "eeoc_air",
        "masd",
        "confidence_intervals",
        "bonferroni",
        "reasoning_sentiment_delta",
        "context_priming_effect",
        "name_proxy_split",
        "stereotype_consistency",
    ],
)


# ── Tier 3: 130k Token Budget ────────────────────────────────────────────────

TIER_3_CONFIG = TierConfig(
    name="Tier 3 - Full Audit Suite",
    token_budget=130_000,
    persona_counts={
        "pairwise_grid": 60,      # 30 pairs
        "name_proxy": 30,         # Name testing
        "intersectional": 20,     # 2 and 3-way combos
        "context_primed": 10,     # CPE baseline
    },
    enable_reasoning_pull=True,   # Pull reasoning for 25 flagged cases
    enable_context_primes=True,   # Test fairness preambles
    enable_prompt_patches=True,   # Test 2 prompt modifications
    enable_reproducibility_check=True,  # Spot-check 10 personas
    two_pass_enabled=True,
    metrics_included=[
        "cfr",
        "ba_cfr",
        "demographic_parity",
        "eeoc_air",
        "masd",
        "confidence_intervals",
        "bonferroni",
        "reasoning_sentiment_delta",
        "context_priming_effect",
        "name_proxy_split",
        "stereotype_consistency",
        "prompt_patch_delta",
        "reproducibility_score",
        "coded_language_detection",
    ],
)


# ── Adaptive Tier Configuration ──────────────────────────────────────────────

@dataclass
class AdaptiveConfig:
    """
    Adaptive tier that escalates based on findings.
    
    Stage 1 (15k): 30 personas, quick scan
    Stage 2 (+25k): Expand to 80 personas if CFR > 10%
    Stage 3 (+90k): Full Tier 3 if findings confirmed
    
    Expected average: ~25k tokens per audit (60% resolve early)
    """
    stage_1_budget: int = 15_000
    stage_2_budget: int = 40_000  # Cumulative
    stage_3_budget: int = 130_000  # Cumulative
    
    stage_1_personas: int = 30
    stage_2_personas: int = 80
    stage_3_personas: int = 120
    
    escalation_threshold_cfr: float = 0.10  # Escalate if CFR > 10%
    
    def should_escalate_to_stage_2(self, cfr: float) -> bool:
        """Check if findings warrant stage 2."""
        return cfr > self.escalation_threshold_cfr
    
    def should_escalate_to_stage_3(self, findings_count: int, severity: str) -> bool:
        """Check if findings warrant stage 3."""
        return findings_count > 3 or severity in ["CRITICAL", "MODERATE"]


ADAPTIVE_CONFIG = AdaptiveConfig()


# ── Tier Selection ───────────────────────────────────────────────────────────

def get_tier_config(tier: AuditTier | str) -> TierConfig | AdaptiveConfig:
    """
    Get configuration for a tier.
    
    Args:
        tier: AuditTier enum or string name
    
    Returns:
        TierConfig or AdaptiveConfig
    
    Raises:
        ValueError: If tier is unknown
    """
    if isinstance(tier, str):
        tier = AuditTier(tier)
    
    if tier == AuditTier.TIER_1:
        return TIER_1_CONFIG
    elif tier == AuditTier.TIER_2:
        return TIER_2_CONFIG
    elif tier == AuditTier.TIER_3:
        return TIER_3_CONFIG
    elif tier == AuditTier.ADAPTIVE:
        return ADAPTIVE_CONFIG
    else:
        raise ValueError(f"Unknown tier: {tier}")


def estimate_tier_from_budget(token_budget: int) -> AuditTier:
    """
    Recommend a tier based on available token budget.
    
    Args:
        token_budget: Available tokens
    
    Returns:
        Recommended AuditTier
    """
    if token_budget < 50_000:
        return AuditTier.TIER_1
    elif token_budget < 80_000:
        return AuditTier.TIER_1
    elif token_budget < 130_000:
        return AuditTier.TIER_2
    else:
        return AuditTier.TIER_3


def compare_tiers() -> dict[str, Any]:
    """
    Compare all tiers side-by-side.
    
    Returns:
        Dict with tier comparison data
    """
    tiers = [TIER_1_CONFIG, TIER_2_CONFIG, TIER_3_CONFIG]
    
    comparison = {
        "tiers": [],
    }
    
    for tier in tiers:
        comparison["tiers"].append({
            "name": tier.name,
            "budget": tier.token_budget,
            "personas": tier.total_personas,
            "reasoning_pull": tier.enable_reasoning_pull,
            "context_primes": tier.enable_context_primes,
            "prompt_patches": tier.enable_prompt_patches,
            "metrics_count": len(tier.metrics_included),
        })
    
    return comparison


__all__ = [
    "AuditTier",
    "TierConfig",
    "AdaptiveConfig",
    "TIER_1_CONFIG",
    "TIER_2_CONFIG",
    "TIER_3_CONFIG",
    "ADAPTIVE_CONFIG",
    "get_tier_config",
    "estimate_tier_from_budget",
    "compare_tiers",
]
