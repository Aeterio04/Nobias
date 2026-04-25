"""
agent_audit.statistics.intersectional — Intersectional Disparity Scan
========================================================================

Tests every k-way intersection of protected attributes for
compounded bias that single-attribute analysis misses.

Example: A Black woman may be treated worse than the sum of
penalties for being Black + being a woman separately.
This is known as intersectional discrimination.

Only runs in standard/full modes, and only when ≥2 single
attributes are individually flagged.
"""

from __future__ import annotations

import itertools
import pandas as pd


def intersectional_scan(
    df: pd.DataFrame,
    attributes: list[str],
    decision_col: str = "decision",
    disparity_threshold: float = 0.10,
    max_k: int | None = None,
) -> list[dict]:
    """
    Test all k-way intersections of attributes for disparity.

    Args:
        df: Results DataFrame.
        attributes: List of protected attribute column names.
        decision_col: Decision column name.
        disparity_threshold: Minimum disparity to flag.
        max_k: Maximum intersection size (default: all).

    Returns:
        List of findings, sorted by disparity (worst first).
    """
    findings: list[dict] = []
    max_k = max_k or len(attributes)

    for k in range(2, min(max_k + 1, len(attributes) + 1)):
        for combo in itertools.combinations(attributes, k):
            # Check that all attributes exist in the DataFrame
            if not all(attr in df.columns for attr in combo):
                continue

            grouped = df.groupby(list(combo))[decision_col].apply(
                lambda x: (x == "positive").mean()
            )

            if len(grouped) < 2:
                continue

            max_rate = grouped.max()
            min_rate = grouped.min()
            disparity = max_rate - min_rate

            if disparity > disparity_threshold:
                findings.append({
                    "intersection": combo,
                    "intersection_size": k,
                    "worst_group": grouped.idxmin(),
                    "best_group": grouped.idxmax(),
                    "worst_rate": float(min_rate),
                    "best_rate": float(max_rate),
                    "disparity": float(disparity),
                    "disparate_impact_ratio": (
                        float(min_rate / max_rate) if max_rate > 0 else 0.0
                    ),
                    "eeoc_violation": (min_rate / max_rate < 0.8) if max_rate > 0 else False,
                    "n_groups": len(grouped),
                })

    return sorted(findings, key=lambda x: x["disparity"], reverse=True)


def should_run_intersectional(
    single_findings: list[dict],
    mode: str = "standard",
    min_flagged: int = 2,
) -> bool:
    """
    Determine whether to run intersectional analysis.

    Only triggers in standard/full modes when at least min_flagged
    single-attribute findings have severity above CLEAR.

    Args:
        single_findings: Findings from single-attribute analysis.
        mode: Audit mode.
        min_flagged: Minimum number of flagged attributes to trigger.

    Returns:
        True if intersectional analysis should run.
    """
    if mode == "quick":
        return False

    if mode == "full":
        return True  # Always run in full mode

    # Standard mode: run only if ≥ min_flagged attributes are flagged
    flagged_count = sum(
        1 for f in single_findings
        if f.severity != "CLEAR"  # AgentFinding object, not dict
    )
    return flagged_count >= min_flagged
