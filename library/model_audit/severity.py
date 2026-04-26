"""
Severity classification for audit findings.
"""
from typing import Optional
from .models import Severity, MetricResult, CounterfactualResult


def classify_severity(
    scorecard: dict[str, MetricResult],
    counterfactual_result: CounterfactualResult,
    thresholds: Optional[dict[str, dict]] = None
) -> Severity:
    """
    Classify overall audit severity based on metrics and counterfactual results.
    
    Severity levels:
    - CRITICAL: DPD > 0.20 and p < 0.01, OR DIR < 0.60, OR flip_rate > 15%
    - MODERATE: DPD > 0.10 and p < 0.05, OR DIR < 0.80, OR flip_rate > 5%
    - LOW: DPD > 0.05, OR flip_rate > 2%
    - CLEAR: All metrics within thresholds
    
    Args:
        scorecard: Dictionary of fairness metrics
        counterfactual_result: Counterfactual testing results
        thresholds: Custom severity thresholds
        
    Returns:
        Severity enum value
    """
    if thresholds is None:
        thresholds = {
            "CRITICAL": {"dpd": 0.20, "dir": 0.60, "flip_rate": 0.15, "p_value": 0.01},
            "MODERATE": {"dpd": 0.10, "dir": 0.80, "flip_rate": 0.05, "p_value": 0.05},
            "LOW": {"dpd": 0.05, "dir": 0.90, "flip_rate": 0.02},
        }
    
    # Check CRITICAL conditions
    critical_thresholds = thresholds["CRITICAL"]
    
    # Check demographic parity with statistical significance
    if "demographic_parity" in scorecard:
        dpd_metric = scorecard["demographic_parity"]
        if (abs(dpd_metric.value) > critical_thresholds["dpd"] and 
            dpd_metric.p_value is not None and 
            dpd_metric.p_value < critical_thresholds["p_value"]):
            return Severity.CRITICAL
    
    # Check disparate impact ratio
    if "disparate_impact" in scorecard:
        dir_metric = scorecard["disparate_impact"]
        if dir_metric.value < critical_thresholds["dir"]:
            return Severity.CRITICAL
    
    # Check counterfactual flip rate
    if counterfactual_result.flip_rate > critical_thresholds["flip_rate"]:
        return Severity.CRITICAL
    
    # Check MODERATE conditions
    moderate_thresholds = thresholds["MODERATE"]
    
    if "demographic_parity" in scorecard:
        dpd_metric = scorecard["demographic_parity"]
        if (abs(dpd_metric.value) > moderate_thresholds["dpd"] and 
            dpd_metric.p_value is not None and 
            dpd_metric.p_value < moderate_thresholds["p_value"]):
            return Severity.MODERATE
    
    if "disparate_impact" in scorecard:
        dir_metric = scorecard["disparate_impact"]
        if dir_metric.value < moderate_thresholds["dir"]:
            return Severity.MODERATE
    
    if counterfactual_result.flip_rate > moderate_thresholds["flip_rate"]:
        return Severity.MODERATE
    
    # Check any failed metrics for MODERATE
    if any(not metric.passed for metric in scorecard.values()):
        return Severity.MODERATE
    
    # Check LOW conditions
    low_thresholds = thresholds["LOW"]
    
    if "demographic_parity" in scorecard:
        dpd_metric = scorecard["demographic_parity"]
        if abs(dpd_metric.value) > low_thresholds["dpd"]:
            return Severity.LOW
    
    if "disparate_impact" in scorecard:
        dir_metric = scorecard["disparate_impact"]
        if dir_metric.value < low_thresholds["dir"]:
            return Severity.LOW
    
    if counterfactual_result.flip_rate > low_thresholds["flip_rate"]:
        return Severity.LOW
    
    # All checks passed
    return Severity.CLEAR


def classify_metric_severity(metric: MetricResult) -> Severity:
    """
    Classify severity for a single metric.
    
    Args:
        metric: MetricResult to classify
        
    Returns:
        Severity enum value
    """
    if metric.passed:
        return Severity.CLEAR
    
    # Determine severity based on how far from threshold
    if metric.metric_name == "Demographic Parity Difference":
        abs_value = abs(metric.value)
        if abs_value > 0.20:
            return Severity.CRITICAL
        elif abs_value > 0.10:
            return Severity.MODERATE
        else:
            return Severity.LOW
    
    elif metric.metric_name == "Disparate Impact Ratio":
        if metric.value < 0.60:
            return Severity.CRITICAL
        elif metric.value < 0.80:
            return Severity.MODERATE
        else:
            return Severity.LOW
    
    elif metric.metric_name == "Equalized Odds Difference":
        if metric.value > 0.15:
            return Severity.CRITICAL
        elif metric.value > 0.10:
            return Severity.MODERATE
        else:
            return Severity.LOW
    
    elif metric.metric_name == "Predictive Parity":
        if metric.value > 0.10:
            return Severity.MODERATE
        else:
            return Severity.LOW
    
    elif metric.metric_name == "Calibration Difference":
        if metric.value > 0.10:
            return Severity.MODERATE
        else:
            return Severity.LOW
    
    # Default
    return Severity.MODERATE if not metric.passed else Severity.CLEAR


def classify_flip_rate_severity(flip_rate: float) -> Severity:
    """
    Classify severity based on counterfactual flip rate.
    
    Args:
        flip_rate: Proportion of predictions that flipped
        
    Returns:
        Severity enum value
    """
    if flip_rate > 0.15:
        return Severity.CRITICAL
    elif flip_rate > 0.05:
        return Severity.MODERATE
    elif flip_rate > 0.02:
        return Severity.LOW
    else:
        return Severity.CLEAR


def get_severity_description(severity: Severity) -> str:
    """
    Get human-readable description of severity level.
    
    Args:
        severity: Severity enum value
        
    Returns:
        Description string
    """
    descriptions = {
        Severity.CRITICAL: (
            "CRITICAL: Significant fairness violations detected. "
            "Immediate action required before deployment."
        ),
        Severity.MODERATE: (
            "MODERATE: Notable fairness concerns identified. "
            "Review and mitigation recommended."
        ),
        Severity.LOW: (
            "LOW: Minor fairness issues detected. "
            "Consider monitoring and potential improvements."
        ),
        Severity.CLEAR: (
            "CLEAR: No significant fairness violations detected. "
            "Model passes fairness thresholds."
        ),
    }
    return descriptions.get(severity, "Unknown severity level")


def get_severity_color(severity: Severity) -> str:
    """
    Get color code for severity level (for visualization).
    
    Args:
        severity: Severity enum value
        
    Returns:
        Color name or hex code
    """
    colors = {
        Severity.CRITICAL: "#D32F2F",  # Red
        Severity.MODERATE: "#F57C00",  # Orange
        Severity.LOW: "#FBC02D",       # Yellow
        Severity.CLEAR: "#388E3C",     # Green
    }
    return colors.get(severity, "#757575")  # Gray default
