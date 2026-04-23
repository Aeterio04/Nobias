"""
agent_audit.statistics.parity — Demographic Parity & Disparate Impact
========================================================================

Computes approval rate per demographic group and checks the
EEOC 4/5ths (80%) rule for disparate impact.

The 80% rule: if the selection rate for any protected group is
less than 80% of the rate for the group with the highest rate,
this constitutes prima facie evidence of adverse impact.
"""

from __future__ import annotations

import pandas as pd


def compute_demographic_parity(
    df: pd.DataFrame,
    attribute: str,
    decision_col: str = "decision",
) -> dict:
    """
    Compute approval rates per group and check EEOC 80% rule.

    Args:
        df: Results DataFrame.
        attribute: Protected attribute column name.
        decision_col: Column name containing decisions.

    Returns:
        Dict with approval_rates, disparity, disparate_impact_ratio,
        and eeoc_violation flag.
    """
    approval_by_group = df.groupby(attribute)[decision_col].apply(
        lambda x: (x == "positive").mean()
    ).to_dict()

    if not approval_by_group:
        return {
            "approval_rates": {},
            "max_group": None,
            "min_group": None,
            "disparity": 0.0,
            "disparate_impact_ratio": 1.0,
            "eeoc_violation": False,
        }

    max_rate = max(approval_by_group.values())
    min_rate = min(approval_by_group.values())

    # Disparate impact ratio (EEOC 4/5ths rule)
    disparate_impact_ratio = min_rate / max_rate if max_rate > 0 else 0.0

    return {
        "approval_rates": approval_by_group,
        "max_group": max(approval_by_group, key=approval_by_group.get),
        "min_group": min(approval_by_group, key=approval_by_group.get),
        "disparity": max_rate - min_rate,
        "disparate_impact_ratio": float(disparate_impact_ratio),
        "eeoc_violation": disparate_impact_ratio < 0.8,
    }


def compute_all_parity(
    df: pd.DataFrame,
    attributes: list[str],
    decision_col: str = "decision",
) -> dict[str, dict]:
    """
    Compute demographic parity for all protected attributes.

    Args:
        df: Results DataFrame.
        attributes: List of protected attribute column names.
        decision_col: Column name containing decisions.

    Returns:
        Dict mapping attribute → parity results.
    """
    results = {}
    for attr in attributes:
        if attr in df.columns:
            results[attr] = compute_demographic_parity(df, attr, decision_col)
    return results
