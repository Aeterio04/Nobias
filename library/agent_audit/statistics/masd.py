"""
agent_audit.statistics.masd — Mean Absolute Score Difference
==============================================================

Secondary fairness metric from Mayilvaghanan et al. (2025).
Used when agents produce numeric scores (confidence, rating, risk).

MASD = (1/N) × Σ|score_original − score_counterfactual|

Unlike CFR, MASD catches sub-threshold bias: the agent doesn't flip
its decision, but assigns systematically lower scores to one group.
"""

from __future__ import annotations

import pandas as pd
import numpy as np


def compute_masd(pairs: list[tuple[float, float]]) -> float:
    """
    Compute Mean Absolute Score Difference for score pairs.

    MASD = (1/N) × Σ|score_A - score_B|

    Args:
        pairs: List of (score_original, score_counterfactual).

    Returns:
        MASD as a float (0.0 = identical scores).
    """
    if not pairs:
        return 0.0
    return sum(abs(a - b) for a, b in pairs) / len(pairs)


def compute_per_attribute_masd(
    df: pd.DataFrame,
    attribute: str,
    score_col: str = "score",
    match_cols: list[str] | None = None,
) -> dict[str, dict]:
    """
    Compute MASD for each value of a protected attribute.

    Uses the most common value as baseline. Only valid when
    numeric scores are available.

    Args:
        df: Results DataFrame with score column.
        attribute: The protected attribute to test.
        score_col: Column name containing numeric scores.
        match_cols: Optional columns to match on for pairing.

    Returns:
        Dict mapping "baseline_vs_comparison" → {masd, ...}
    """
    # Filter to rows with valid scores
    scored_df = df.dropna(subset=[score_col])
    if len(scored_df) < 2:
        return {}

    values = scored_df[attribute].unique()
    if len(values) < 2:
        return {}

    baseline_val = scored_df[attribute].mode()[0]
    baseline_df = scored_df[scored_df[attribute] == baseline_val]

    if match_cols is None:
        exclude = {attribute, score_col, "decision", "raw_outputs", "test_id",
                   "persona_id", "name", "score_std", "decision_variance",
                   "mean_score", "num_runs", "_variant_type", "_varied_attribute"}
        match_cols = [
            c for c in scored_df.columns
            if c not in exclude and not c.startswith("_")
        ]

    results: dict[str, dict] = {}

    for compare_val in values:
        if compare_val == baseline_val:
            continue

        compare_df = scored_df[scored_df[attribute] == compare_val]
        valid_match = [c for c in match_cols if c in baseline_df.columns]

        if valid_match:
            merged = baseline_df.merge(
                compare_df,
                on=valid_match,
                suffixes=("_base", "_comp"),
            )
        else:
            continue

        base_score = f"{score_col}_base"
        comp_score = f"{score_col}_comp"

        if base_score not in merged.columns or comp_score not in merged.columns:
            continue

        score_pairs = merged[[base_score, comp_score]].dropna()
        if len(score_pairs) == 0:
            continue

        pairs = list(zip(score_pairs[base_score], score_pairs[comp_score]))
        masd = compute_masd(pairs)

        results[f"{baseline_val}_vs_{compare_val}"] = {
            "masd": masd,
            "n_pairs": len(pairs),
            "baseline_mean_score": float(np.mean([p[0] for p in pairs])),
            "comparison_mean_score": float(np.mean([p[1] for p in pairs])),
            "score_direction": (
                "lower" if np.mean([p[1] for p in pairs]) < np.mean([p[0] for p in pairs])
                else "higher"
            ),
        }

    return results
