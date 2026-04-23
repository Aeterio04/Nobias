"""
agent_audit.statistics.significance — Statistical Significance Tests
=======================================================================

Provides p-value computation for bias findings using:
    - Chi-square test: for binary decisions (contingency tables)
    - Welch's t-test: for numeric scores (unequal variances)
    - Mann-Whitney U: for non-normal score distributions

p-value thresholds:
    0.01 → CRITICAL (strong statistical evidence)
    0.05 → MODERATE (significant)
    0.10 → LOW (suggestive but not conclusive)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def chi_square_test(
    df: pd.DataFrame,
    attribute: str,
    decision_col: str = "decision",
) -> dict:
    """
    Chi-square test of independence between attribute and decision.

    Tests whether the distribution of decisions is independent of
    the protected attribute value. Requires sufficient sample size.

    Args:
        df: Results DataFrame.
        attribute: Protected attribute column.
        decision_col: Decision column.

    Returns:
        Dict with chi2 statistic, p_value, dof, and significance level.
    """
    try:
        contingency = pd.crosstab(df[attribute], df[decision_col])
        if contingency.shape[0] < 2 or contingency.shape[1] < 2:
            return {"chi2": 0.0, "p_value": 1.0, "dof": 0, "significance": "insufficient_data"}

        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

        return {
            "chi2": float(chi2),
            "p_value": float(p_value),
            "dof": int(dof),
            "significance": _classify_significance(p_value),
            "expected_frequencies": expected.tolist(),
        }
    except (ValueError, np.linalg.LinAlgError):
        return {"chi2": 0.0, "p_value": 1.0, "dof": 0, "significance": "error"}


def welch_t_test(
    group_a_scores: list[float],
    group_b_scores: list[float],
) -> dict:
    """
    Welch's t-test for comparing mean scores between two groups.

    Accounts for unequal variances (does NOT assume equal variance).

    Args:
        group_a_scores: Scores for group A.
        group_b_scores: Scores for group B.

    Returns:
        Dict with t_statistic, p_value, and significance level.
    """
    if len(group_a_scores) < 2 or len(group_b_scores) < 2:
        return {
            "t_statistic": 0.0,
            "p_value": 1.0,
            "significance": "insufficient_data",
        }

    try:
        t_stat, p_value = stats.ttest_ind(
            group_a_scores, group_b_scores, equal_var=False
        )
        return {
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "significance": _classify_significance(p_value),
            "mean_a": float(np.mean(group_a_scores)),
            "mean_b": float(np.mean(group_b_scores)),
            "std_a": float(np.std(group_a_scores)),
            "std_b": float(np.std(group_b_scores)),
        }
    except (ValueError, ZeroDivisionError):
        return {"t_statistic": 0.0, "p_value": 1.0, "significance": "error"}


def mann_whitney_u_test(
    group_a_scores: list[float],
    group_b_scores: list[float],
) -> dict:
    """
    Mann-Whitney U test (non-parametric alternative to t-test).

    Used when score distributions may not be normal.

    Args:
        group_a_scores: Scores for group A.
        group_b_scores: Scores for group B.

    Returns:
        Dict with U_statistic, p_value, and significance level.
    """
    if len(group_a_scores) < 2 or len(group_b_scores) < 2:
        return {
            "U_statistic": 0.0,
            "p_value": 1.0,
            "significance": "insufficient_data",
        }

    try:
        u_stat, p_value = stats.mannwhitneyu(
            group_a_scores, group_b_scores, alternative="two-sided"
        )
        return {
            "U_statistic": float(u_stat),
            "p_value": float(p_value),
            "significance": _classify_significance(p_value),
        }
    except ValueError:
        return {"U_statistic": 0.0, "p_value": 1.0, "significance": "error"}


def compute_significance(
    df: pd.DataFrame,
    attribute: str,
    decision_col: str = "decision",
    score_col: str = "score",
) -> dict:
    """
    Compute appropriate significance test based on data type.

    Uses chi-square for binary decisions and Welch's t-test for
    numeric scores.

    Args:
        df: Results DataFrame.
        attribute: Protected attribute to test.
        decision_col: Decision column name.
        score_col: Score column name.

    Returns:
        Dict with test results and which test was used.
    """
    result = {"attribute": attribute}

    # Chi-square on decisions
    chi2_result = chi_square_test(df, attribute, decision_col)
    result["chi_square"] = chi2_result
    result["primary_p_value"] = chi2_result["p_value"]

    # If numeric scores available, also run t-test
    if score_col in df.columns and df[score_col].notna().sum() > 0:
        groups = df.groupby(attribute)[score_col].apply(list).to_dict()
        group_names = list(groups.keys())
        if len(group_names) >= 2:
            # Pairwise t-tests for all group pairs
            t_tests = {}
            for i, g1 in enumerate(group_names):
                for g2 in group_names[i + 1:]:
                    scores_a = [s for s in groups[g1] if s is not None]
                    scores_b = [s for s in groups[g2] if s is not None]
                    if scores_a and scores_b:
                        t_tests[f"{g1}_vs_{g2}"] = welch_t_test(scores_a, scores_b)
            result["t_tests"] = t_tests

            # Use minimum p-value from t-tests if available
            min_p = min(
                (t["p_value"] for t in t_tests.values()),
                default=1.0,
            )
            result["score_p_value"] = min_p

    return result


def _classify_significance(p_value: float) -> str:
    """
    Classify p-value into significance level.

    Args:
        p_value: The computed p-value.

    Returns:
        "critical" (p < 0.01), "significant" (p < 0.05),
        "suggestive" (p < 0.10), or "not_significant".
    """
    if p_value < 0.01:
        return "critical"
    elif p_value < 0.05:
        return "significant"
    elif p_value < 0.10:
        return "suggestive"
    return "not_significant"
