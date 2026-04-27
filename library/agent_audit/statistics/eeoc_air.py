"""
agent_audit.statistics.eeoc_air — EEOC Adverse Impact Ratio
============================================================

Legal compliance metric from EEOC Uniform Guidelines on Employee
Selection Procedures (29 CFR Part 1607).

The 80% (four-fifths) rule: If the selection rate for any protected
group is less than 80% of the rate for the group with the highest rate,
this constitutes prima facie evidence of adverse impact.

This is a LEGAL THRESHOLD, not just a statistical metric.
"""

from __future__ import annotations

import pandas as pd
from typing import Dict, Any


def compute_eeoc_air(
    df: pd.DataFrame,
    attribute: str,
    decision_col: str = "decision",
) -> Dict[str, Any]:
    """
    Compute EEOC Adverse Impact Ratio (AIR) for a protected attribute.
    
    AIR = (approval_rate of lowest-approved group) / (approval_rate of highest-approved group)
    
    Legal threshold: AIR < 0.80 = adverse impact = legal violation risk
    
    Args:
        df: Results DataFrame.
        attribute: Protected attribute column name.
        decision_col: Column name containing decisions.
    
    Returns:
        Dict with AIR, approval rates, legal status, and risk level.
    """
    # Compute approval rates per group
    approval_by_group = df.groupby(attribute)[decision_col].apply(
        lambda x: (x == "positive").mean()
    ).to_dict()
    
    if not approval_by_group or len(approval_by_group) < 2:
        return {
            "air": 1.0,
            "approval_rates": approval_by_group,
            "highest_group": None,
            "lowest_group": None,
            "legal_status": "INSUFFICIENT_DATA",
            "risk_level": "UNKNOWN",
            "eeoc_compliant": True,
            "threshold": 0.80,
        }
    
    max_rate = max(approval_by_group.values())
    min_rate = min(approval_by_group.values())
    
    highest_group = max(approval_by_group, key=approval_by_group.get)
    lowest_group = min(approval_by_group, key=approval_by_group.get)
    
    # Degenerate case: all rates are identical (perfect parity)
    # This happens when all groups have the same approval rate
    # AIR = 1.0 means perfect parity, not a violation
    if max_rate == min_rate:
        return {
            "air": 1.0,
            "approval_rates": {k: float(v) for k, v in approval_by_group.items()},
            "highest_group": highest_group,
            "lowest_group": lowest_group,
            "highest_rate": float(max_rate),
            "lowest_rate": float(min_rate),
            "legal_status": "COMPLIANT",
            "risk_level": "NONE",
            "eeoc_compliant": True,
            "threshold": 0.80,
            "disparity": 0.0,
            "note": "Perfect parity - all groups have identical approval rates",
        }
    
    # Compute AIR
    air = min_rate / max_rate if max_rate > 0 else 0.0
    
    # Determine legal status
    if air >= 0.80:
        legal_status = "COMPLIANT"
        risk_level = "LOW"
        eeoc_compliant = True
    elif 0.70 <= air < 0.80:
        legal_status = "WARNING"
        risk_level = "MODERATE"
        eeoc_compliant = False
    else:  # air < 0.70
        legal_status = "VIOLATION"
        risk_level = "HIGH"
        eeoc_compliant = False
    
    return {
        "air": float(air),
        "approval_rates": {k: float(v) for k, v in approval_by_group.items()},
        "highest_group": highest_group,
        "lowest_group": lowest_group,
        "highest_rate": float(max_rate),
        "lowest_rate": float(min_rate),
        "legal_status": legal_status,
        "risk_level": risk_level,
        "eeoc_compliant": eeoc_compliant,
        "threshold": 0.80,
        "disparity": float(max_rate - min_rate),
    }


def compute_all_eeoc_air(
    df: pd.DataFrame,
    attributes: list[str],
    decision_col: str = "decision",
) -> Dict[str, Dict[str, Any]]:
    """
    Compute EEOC AIR for all protected attributes.
    
    Args:
        df: Results DataFrame.
        attributes: List of protected attribute column names.
        decision_col: Column name containing decisions.
    
    Returns:
        Dict mapping attribute → AIR results.
    """
    results = {}
    for attr in attributes:
        if attr in df.columns:
            results[attr] = compute_eeoc_air(df, attr, decision_col)
    return results


__all__ = ["compute_eeoc_air", "compute_all_eeoc_air"]
