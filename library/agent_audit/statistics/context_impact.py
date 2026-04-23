"""
agent_audit.statistics.context_impact — Context-Prime Impact Analysis
========================================================================

Measures how each context prime affects bias severity.
Exploits Mayilvaghanan et al.'s finding that contextual priming
caused the worst CFR degradations (up to 16.4%).

Only runs in "full" audit mode (which includes context primes).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from agent_audit.statistics.cfr import compute_all_cfr


def context_prime_impact(
    df: pd.DataFrame,
    attributes: list[str],
    context_col: str = "context_prime",
    decision_col: str = "decision",
) -> dict:
    """
    Measure how each context prime affects bias severity.

    For each prime, computes CFR across all attributes. Ranks primes
    by their bias amplification factor.

    Args:
        df: Results DataFrame with context_prime column.
        attributes: Protected attribute column names.
        context_col: Column identifying the context prime.
        decision_col: Decision column name.

    Returns:
        Dict with ranked_contexts, worst_context, and amplification.
    """
    if context_col not in df.columns:
        return {
            "ranked_contexts": [],
            "worst_context": None,
            "worst_context_cfr": 0.0,
            "context_amplification": 0.0,
        }

    impact: dict[str, dict] = {}

    for prime in df[context_col].unique():
        prime_df = df[df[context_col] == prime]
        cfr_results = compute_all_cfr(prime_df, attributes, decision_col)

        # Aggregate CFR across all attribute comparisons
        all_cfrs: list[float] = []
        for attr_results in cfr_results.values():
            for comparison in attr_results.values():
                all_cfrs.append(comparison["cfr"])

        impact[prime] = {
            "mean_cfr": float(np.mean(all_cfrs)) if all_cfrs else 0.0,
            "max_cfr": float(max(all_cfrs)) if all_cfrs else 0.0,
            "n_comparisons": len(all_cfrs),
            "detailed_cfr": cfr_results,
        }

    # Rank primes by max CFR (worst bias amplification first)
    ranked = sorted(
        impact.items(),
        key=lambda x: x[1]["max_cfr"],
        reverse=True,
    )

    # Compute amplification factor (worst / best)
    worst_cfr = ranked[0][1]["max_cfr"] if ranked else 0.0
    best_cfr = ranked[-1][1]["max_cfr"] if ranked else 0.0

    return {
        "ranked_contexts": [
            {"context": name, **data} for name, data in ranked
        ],
        "worst_context": ranked[0][0] if ranked else None,
        "worst_context_cfr": worst_cfr,
        "best_context": ranked[-1][0] if ranked else None,
        "best_context_cfr": best_cfr,
        "context_amplification": (
            worst_cfr / best_cfr if best_cfr > 0 else float("inf")
        ),
    }
