"""
agent_audit.statistics.cfr — Counterfactual Flip Rate
=======================================================

Primary fairness metric from Mayilvaghanan et al. (2025).
Measures the proportion of counterfactual pairs where the
agent's binary decision flips when only the protected
attribute changes.

Empirical baselines (18 LLMs, 3000 real transcripts):
    - Overall CFR range: 5.4% — 13.0%
    - Contextual priming worst case: 16.4%
    - Best-in-class: 5.4%

These baselines enable contextualised reporting:
    "Your agent's CFR is 11.2%. For reference, across 18 commercial
     LLMs, the range was 5.4%–13.0%."
"""

from __future__ import annotations

import pandas as pd


def compute_cfr(pairs: list[tuple[str, str]]) -> float:
    """
    Compute Counterfactual Flip Rate for a list of decision pairs.

    CFR = (# pairs where decision_A ≠ decision_B) / total pairs

    Args:
        pairs: List of (decision_original, decision_counterfactual).

    Returns:
        CFR as a float between 0.0 and 1.0.
    """
    if not pairs:
        return 0.0
    flips = sum(1 for a, b in pairs if a != b)
    return flips / len(pairs)


def compute_per_attribute_cfr(
    df: pd.DataFrame,
    attribute: str,
    decision_col: str = "decision",
    match_cols: list[str] | None = None,
) -> dict[str, dict]:
    """
    Compute CFR for each value of a protected attribute.

    Uses the most common value as the baseline group. Matches on
    all OTHER attributes when forming counterfactual pairs.

    Args:
        df: Results DataFrame with attribute columns and a decision column.
        attribute: The protected attribute to test (e.g. "gender").
        decision_col: Column name containing decisions.
        match_cols: Optional explicit list of columns to match on.

    Returns:
        Dict mapping "baseline_vs_comparison" → {cfr, n_pairs, ...}
    """
    values = df[attribute].unique()
    if len(values) < 2:
        return {}

    # Use the most common value as baseline
    baseline_val = df[attribute].mode()[0]
    baseline_df = df[df[attribute] == baseline_val]

    # Determine match columns (all attributes except the tested one)
    if match_cols is None:
        # Auto-detect: use all columns that look like attribute columns
        exclude = {attribute, decision_col, "score", "raw_outputs", "test_id",
                   "persona_id", "name", "score_std", "decision_variance",
                   "mean_score", "num_runs", "_variant_type", "_varied_attribute"}
        match_cols = [
            c for c in df.columns
            if c not in exclude and not c.startswith("_")
        ]

    results: dict[str, dict] = {}

    for compare_val in values:
        if compare_val == baseline_val:
            continue

        compare_df = df[df[attribute] == compare_val]

        # Find valid match columns (present in both DataFrames)
        valid_match = [c for c in match_cols if c in baseline_df.columns and c in compare_df.columns]

        if valid_match:
            merged = baseline_df.merge(
                compare_df,
                on=valid_match,
                suffixes=("_base", "_comp"),
            )
        else:
            # No match columns — create all pairwise combinations
            baseline_copy = baseline_df.copy()
            compare_copy = compare_df.copy()
            baseline_copy["_merge_key"] = 1
            compare_copy["_merge_key"] = 1
            merged = baseline_copy.merge(compare_copy, on="_merge_key", suffixes=("_base", "_comp"))
            merged.drop("_merge_key", axis=1, inplace=True)

        if len(merged) == 0:
            continue

        # Get decision column names after merge
        base_dec = f"{decision_col}_base"
        comp_dec = f"{decision_col}_comp"

        if base_dec not in merged.columns or comp_dec not in merged.columns:
            continue

        pairs = list(zip(merged[base_dec], merged[comp_dec]))
        cfr = compute_cfr(pairs)

        # Compute approval rates
        base_approval = (merged[base_dec] == "positive").mean()
        comp_approval = (merged[comp_dec] == "positive").mean()

        results[f"{baseline_val}_vs_{compare_val}"] = {
            "cfr": cfr,
            "n_pairs": len(pairs),
            "baseline_value": baseline_val,
            "comparison_value": compare_val,
            "baseline_approval_rate": float(base_approval),
            "comparison_approval_rate": float(comp_approval),
        }

    return results


def compute_all_cfr(
    df: pd.DataFrame,
    attributes: list[str],
    decision_col: str = "decision",
) -> dict[str, dict]:
    """
    Compute CFR for all protected attributes.

    Args:
        df: Results DataFrame.
        attributes: List of protected attribute column names.
        decision_col: Column name containing decisions.

    Returns:
        Dict mapping attribute → {comparison → cfr_result}.
    """
    results = {}
    for attr in attributes:
        if attr in df.columns:
            attr_cfr = compute_per_attribute_cfr(df, attr, decision_col)
            if attr_cfr:
                results[attr] = attr_cfr
    return results
