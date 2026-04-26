"""
Intersectional fairness analysis.

Checks for compounded bias across multiple protected attributes.
"""
import numpy as np
import pandas as pd
from typing import Any, List
from itertools import combinations
from .models import IntersectionalFinding, Severity
from .fairness_metrics import compute_demographic_parity


def analyze_intersectional_bias(
    X_test: pd.DataFrame,
    y_pred: np.ndarray,
    protected_attributes: list[str],
    positive_value: Any = 1,
    min_sample_size: int = 30
) -> list[IntersectionalFinding]:
    """
    Analyze intersectional bias across combinations of protected attributes.
    
    Checks if bias is compounded (superadditive) when multiple attributes intersect.
    For example, checks if Black women face worse outcomes than Black people or women alone.
    
    Args:
        X_test: Test features
        y_pred: Predictions
        protected_attributes: List of protected attribute column names
        positive_value: Value representing positive prediction
        min_sample_size: Minimum samples required for a group to be analyzed
        
    Returns:
        List of IntersectionalFinding objects
    """
    findings = []
    
    # Only analyze 2-way intersections for now (can extend to 3-way later)
    for attr1, attr2 in combinations(protected_attributes, 2):
        if attr1 not in X_test.columns or attr2 not in X_test.columns:
            continue
        
        # Get unique values for each attribute
        values1 = X_test[attr1].unique()
        values2 = X_test[attr2].unique()
        
        # Calculate baseline approval rates for each attribute individually
        baseline_rates = {}
        
        for val1 in values1:
            mask = X_test[attr1] == val1
            if mask.sum() >= min_sample_size:
                rate = (y_pred[mask] == positive_value).mean()
                baseline_rates[f"{attr1}={val1}"] = rate
        
        for val2 in values2:
            mask = X_test[attr2] == val2
            if mask.sum() >= min_sample_size:
                rate = (y_pred[mask] == positive_value).mean()
                baseline_rates[f"{attr2}={val2}"] = rate
        
        # Calculate approval rates for intersections
        for val1 in values1:
            for val2 in values2:
                mask = (X_test[attr1] == val1) & (X_test[attr2] == val2)
                sample_count = mask.sum()
                
                if sample_count < min_sample_size:
                    continue
                
                intersect_rate = (y_pred[mask] == positive_value).mean()
                
                # Get baseline rates for comparison
                base1 = baseline_rates.get(f"{attr1}={val1}", intersect_rate)
                base2 = baseline_rates.get(f"{attr2}={val2}", intersect_rate)
                
                # Expected rate if effects were additive
                overall_rate = (y_pred == positive_value).mean()
                expected_rate = (base1 + base2) / 2
                
                # Check if intersection shows worse outcomes than expected
                # (superadditive bias)
                deviation = intersect_rate - expected_rate
                
                # Flag if deviation is significant (> 5% worse than expected)
                is_superadditive = deviation < -0.05
                
                if is_superadditive:
                    # Determine severity based on magnitude
                    if abs(deviation) > 0.15:
                        severity = Severity.CRITICAL
                    elif abs(deviation) > 0.10:
                        severity = Severity.MODERATE
                    else:
                        severity = Severity.LOW
                    
                    finding = IntersectionalFinding(
                        attributes=[attr1, attr2],
                        attribute_values={attr1: val1, attr2: val2},
                        metric_name="approval_rate",
                        metric_value=intersect_rate,
                        baseline_value=expected_rate,
                        is_superadditive=True,
                        severity=severity,
                        sample_count=int(sample_count),
                    )
                    findings.append(finding)
    
    # Sort by severity and magnitude
    findings.sort(
        key=lambda f: (
            ["CLEAR", "LOW", "MODERATE", "CRITICAL"].index(f.severity.value),
            abs(f.metric_value - f.baseline_value)
        ),
        reverse=True
    )
    
    return findings


def get_intersectional_groups(
    X_test: pd.DataFrame,
    protected_attributes: list[str],
    min_sample_size: int = 30
) -> list[dict[str, Any]]:
    """
    Get all intersectional groups with sufficient sample size.
    
    Args:
        X_test: Test features
        protected_attributes: List of protected attribute column names
        min_sample_size: Minimum samples required
        
    Returns:
        List of group definitions with sample counts
    """
    groups = []
    
    for attr1, attr2 in combinations(protected_attributes, 2):
        if attr1 not in X_test.columns or attr2 not in X_test.columns:
            continue
        
        values1 = X_test[attr1].unique()
        values2 = X_test[attr2].unique()
        
        for val1 in values1:
            for val2 in values2:
                mask = (X_test[attr1] == val1) & (X_test[attr2] == val2)
                sample_count = mask.sum()
                
                if sample_count >= min_sample_size:
                    groups.append({
                        "attributes": {attr1: val1, attr2: val2},
                        "sample_count": int(sample_count),
                        "label": f"{attr1}={val1} & {attr2}={val2}"
                    })
    
    return groups
