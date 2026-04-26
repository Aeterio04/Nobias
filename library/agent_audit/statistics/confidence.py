"""
agent_audit.statistics.confidence — Confidence Intervals & Statistical Validity
================================================================================

Computes confidence intervals for all rate estimates and applies
multiple testing corrections.

Without confidence intervals, point estimates are misleading.
CFR=28.6% from N=7 pairs has CI of [5%, 52%] - too wide to act on.
"""

from __future__ import annotations

import math
from typing import Tuple, List
from scipy import stats


def compute_proportion_ci(
    successes: int,
    total: int,
    confidence: float = 0.95,
) -> Tuple[float, float]:
    """
    Compute confidence interval for a proportion using Wilson score method.
    
    More accurate than normal approximation for small samples.
    
    Args:
        successes: Number of successes.
        total: Total number of trials.
        confidence: Confidence level (default 0.95 for 95% CI).
    
    Returns:
        Tuple of (lower_bound, upper_bound).
    """
    if total == 0:
        return (0.0, 0.0)
    
    p = successes / total
    z = stats.norm.ppf((1 + confidence) / 2)
    
    # Wilson score interval
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) / total + z**2 / (4 * total**2))) / denominator
    
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    
    return (lower, upper)


def compute_rate_with_ci(
    successes: int,
    total: int,
    confidence: float = 0.95,
) -> dict:
    """
    Compute rate with confidence interval and metadata.
    
    Args:
        successes: Number of successes.
        total: Total number of trials.
        confidence: Confidence level.
    
    Returns:
        Dict with rate, CI, sample size, and CI width.
    """
    rate = successes / total if total > 0 else 0.0
    lower, upper = compute_proportion_ci(successes, total, confidence)
    
    return {
        "rate": float(rate),
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "ci_width": float(upper - lower),
        "sample_size": total,
        "confidence_level": confidence,
    }


def apply_bonferroni_correction(
    p_values: List[float],
    alpha: float = 0.05,
) -> dict:
    """
    Apply Bonferroni correction for multiple testing.
    
    When testing N hypotheses simultaneously, the probability of at least
    one false positive is much higher than alpha. Bonferroni correction
    adjusts the threshold to control family-wise error rate.
    
    Args:
        p_values: List of p-values from multiple tests.
        alpha: Desired family-wise error rate (default 0.05).
    
    Returns:
        Dict with corrected threshold and significance flags.
    """
    n_tests = len(p_values)
    if n_tests == 0:
        return {
            "corrected_alpha": alpha,
            "n_tests": 0,
            "significant_raw": [],
            "significant_corrected": [],
        }
    
    corrected_alpha = alpha / n_tests
    
    significant_raw = [p < alpha for p in p_values]
    significant_corrected = [p < corrected_alpha for p in p_values]
    
    return {
        "corrected_alpha": corrected_alpha,
        "n_tests": n_tests,
        "significant_raw": significant_raw,
        "significant_corrected": significant_corrected,
        "n_significant_raw": sum(significant_raw),
        "n_significant_corrected": sum(significant_corrected),
        "potential_false_positives": sum(significant_raw) - sum(significant_corrected),
    }


def compute_statistical_power(
    n_per_group: int,
    effect_size: float,
    alpha: float = 0.05,
) -> float:
    """
    Compute statistical power for detecting a given effect size.
    
    Power = probability of detecting a real effect if it exists.
    Power < 0.80 means the test is underpowered.
    
    Args:
        n_per_group: Sample size per group.
        effect_size: Expected effect size (e.g., 0.10 for 10% difference).
        alpha: Significance level.
    
    Returns:
        Statistical power (0.0 to 1.0).
    """
    if n_per_group < 2:
        return 0.0
    
    # Simplified power calculation for two proportions
    # Assumes p1=0.5, p2=0.5+effect_size
    p1 = 0.5
    p2 = 0.5 + effect_size
    
    pooled_p = (p1 + p2) / 2
    se = math.sqrt(2 * pooled_p * (1 - pooled_p) / n_per_group)
    
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = (abs(p1 - p2) - z_alpha * se) / se
    
    power = stats.norm.cdf(z_beta)
    return max(0.0, min(1.0, power))


__all__ = [
    "compute_proportion_ci",
    "compute_rate_with_ci",
    "apply_bonferroni_correction",
    "compute_statistical_power",
]
