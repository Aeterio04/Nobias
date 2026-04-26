"""
Group fairness metrics computation.
"""
import numpy as np
import pandas as pd
from typing import Any, Optional
from scipy import stats
from .models import MetricResult


def compute_demographic_parity(
    X_test: pd.DataFrame,
    y_pred: np.ndarray,
    protected_attribute: str,
    privileged_value: Any,
    unprivileged_value: Any,
    positive_value: Any = 1,
    threshold: float = 0.10
) -> MetricResult:
    """
    Compute Demographic Parity Difference (DPD).
    
    DPD = P(Y_pred=1 | A=unprivileged) - P(Y_pred=1 | A=privileged)
    
    Args:
        X_test: Test features
        y_pred: Predictions
        protected_attribute: Name of protected attribute
        privileged_value: Value representing privileged group
        unprivileged_value: Value representing unprivileged group
        positive_value: Value representing positive prediction
        threshold: Threshold for pass/fail
        
    Returns:
        MetricResult object
    """
    # Get masks for each group
    priv_mask = X_test[protected_attribute] == privileged_value
    unpriv_mask = X_test[protected_attribute] == unprivileged_value
    
    # Calculate approval rates
    priv_approval = (y_pred[priv_mask] == positive_value).mean() if priv_mask.sum() > 0 else 0
    unpriv_approval = (y_pred[unpriv_mask] == positive_value).mean() if unpriv_mask.sum() > 0 else 0
    
    # DPD = unprivileged - privileged (positive means unprivileged favored)
    dpd = unpriv_approval - priv_approval
    
    # Statistical significance test (two-proportion z-test)
    n_priv = priv_mask.sum()
    n_unpriv = unpriv_mask.sum()
    
    p_value = None
    if n_priv > 0 and n_unpriv > 0:
        # Two-proportion z-test
        count_priv = (y_pred[priv_mask] == positive_value).sum()
        count_unpriv = (y_pred[unpriv_mask] == positive_value).sum()
        
        p_pooled = (count_priv + count_unpriv) / (n_priv + n_unpriv)
        se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n_priv + 1/n_unpriv))
        
        if se > 0:
            z_stat = dpd / se
            p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    
    passed = abs(dpd) <= threshold
    
    return MetricResult(
        metric_name="Demographic Parity Difference",
        value=dpd,
        threshold=threshold,
        passed=passed,
        p_value=p_value,
        privileged_group=f"{protected_attribute}={privileged_value}",
        unprivileged_group=f"{protected_attribute}={unprivileged_value}",
        description=f"Difference in approval rates: {dpd:.4f} (threshold: ±{threshold})"
    )


def compute_disparate_impact(
    X_test: pd.DataFrame,
    y_pred: np.ndarray,
    protected_attribute: str,
    privileged_value: Any,
    unprivileged_value: Any,
    positive_value: Any = 1,
    threshold: float = 0.80
) -> MetricResult:
    """
    Compute Disparate Impact Ratio (DIR).
    
    DIR = P(Y_pred=1 | A=unprivileged) / P(Y_pred=1 | A=privileged)
    
    The 80% rule (EEOC): DIR should be >= 0.80
    
    Args:
        X_test: Test features
        y_pred: Predictions
        protected_attribute: Name of protected attribute
        privileged_value: Value representing privileged group
        unprivileged_value: Value representing unprivileged group
        positive_value: Value representing positive prediction
        threshold: Minimum acceptable ratio (default 0.80)
        
    Returns:
        MetricResult object
    """
    priv_mask = X_test[protected_attribute] == privileged_value
    unpriv_mask = X_test[protected_attribute] == unprivileged_value
    
    priv_approval = (y_pred[priv_mask] == positive_value).mean() if priv_mask.sum() > 0 else 0
    unpriv_approval = (y_pred[unpriv_mask] == positive_value).mean() if unpriv_mask.sum() > 0 else 0
    
    # Avoid division by zero
    if priv_approval == 0:
        dir_ratio = float('inf') if unpriv_approval > 0 else 1.0
    else:
        dir_ratio = unpriv_approval / priv_approval
    
    passed = dir_ratio >= threshold
    
    return MetricResult(
        metric_name="Disparate Impact Ratio",
        value=dir_ratio,
        threshold=threshold,
        passed=passed,
        privileged_group=f"{protected_attribute}={privileged_value}",
        unprivileged_group=f"{protected_attribute}={unprivileged_value}",
        description=f"Ratio of approval rates: {dir_ratio:.4f} (threshold: >={threshold})"
    )


def compute_equalized_odds(
    X_test: pd.DataFrame,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    protected_attribute: str,
    privileged_value: Any,
    unprivileged_value: Any,
    positive_value: Any = 1,
    threshold: float = 0.10
) -> MetricResult:
    """
    Compute Equalized Odds Difference.
    
    Equalized Odds = max(|FPR_diff|, |FNR_diff|)
    where FPR = False Positive Rate, FNR = False Negative Rate
    
    Args:
        X_test: Test features
        y_true: True labels
        y_pred: Predictions
        protected_attribute: Name of protected attribute
        privileged_value: Value representing privileged group
        unprivileged_value: Value representing unprivileged group
        positive_value: Value representing positive prediction
        threshold: Maximum acceptable difference
        
    Returns:
        MetricResult object
    """
    priv_mask = X_test[protected_attribute] == privileged_value
    unpriv_mask = X_test[protected_attribute] == unprivileged_value
    
    # Calculate FPR and FNR for each group
    def calc_rates(mask):
        if mask.sum() == 0:
            return 0.0, 0.0
        
        y_t = y_true[mask]
        y_p = y_pred[mask]
        
        # True negatives and false positives
        negatives = y_t != positive_value
        if negatives.sum() > 0:
            fpr = ((y_p == positive_value) & negatives).sum() / negatives.sum()
        else:
            fpr = 0.0
        
        # True positives and false negatives
        positives = y_t == positive_value
        if positives.sum() > 0:
            fnr = ((y_p != positive_value) & positives).sum() / positives.sum()
        else:
            fnr = 0.0
        
        return fpr, fnr
    
    priv_fpr, priv_fnr = calc_rates(priv_mask)
    unpriv_fpr, unpriv_fnr = calc_rates(unpriv_mask)
    
    fpr_diff = abs(unpriv_fpr - priv_fpr)
    fnr_diff = abs(unpriv_fnr - priv_fnr)
    
    eod = max(fpr_diff, fnr_diff)
    passed = eod <= threshold
    
    return MetricResult(
        metric_name="Equalized Odds Difference",
        value=eod,
        threshold=threshold,
        passed=passed,
        privileged_group=f"{protected_attribute}={privileged_value}",
        unprivileged_group=f"{protected_attribute}={unprivileged_value}",
        description=f"Max(|FPR_diff|={fpr_diff:.4f}, |FNR_diff|={fnr_diff:.4f}) = {eod:.4f}"
    )


def compute_predictive_parity(
    X_test: pd.DataFrame,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    protected_attribute: str,
    privileged_value: Any,
    unprivileged_value: Any,
    positive_value: Any = 1,
    threshold: float = 0.05
) -> MetricResult:
    """
    Compute Predictive Parity (PPV difference).
    
    PPV = Positive Predictive Value = Precision
    Predictive Parity = |PPV_privileged - PPV_unprivileged|
    
    Args:
        X_test: Test features
        y_true: True labels
        y_pred: Predictions
        protected_attribute: Name of protected attribute
        privileged_value: Value representing privileged group
        unprivileged_value: Value representing unprivileged group
        positive_value: Value representing positive prediction
        threshold: Maximum acceptable difference
        
    Returns:
        MetricResult object
    """
    priv_mask = X_test[protected_attribute] == privileged_value
    unpriv_mask = X_test[protected_attribute] == unprivileged_value
    
    def calc_ppv(mask):
        if mask.sum() == 0:
            return 0.0
        
        y_t = y_true[mask]
        y_p = y_pred[mask]
        
        predicted_positive = y_p == positive_value
        if predicted_positive.sum() == 0:
            return 0.0
        
        true_positive = (y_t == positive_value) & predicted_positive
        ppv = true_positive.sum() / predicted_positive.sum()
        
        return ppv
    
    priv_ppv = calc_ppv(priv_mask)
    unpriv_ppv = calc_ppv(unpriv_mask)
    
    ppv_diff = abs(priv_ppv - unpriv_ppv)
    passed = ppv_diff <= threshold
    
    return MetricResult(
        metric_name="Predictive Parity",
        value=ppv_diff,
        threshold=threshold,
        passed=passed,
        privileged_group=f"{protected_attribute}={privileged_value}",
        unprivileged_group=f"{protected_attribute}={unprivileged_value}",
        description=f"|PPV_diff| = {ppv_diff:.4f} (priv={priv_ppv:.4f}, unpriv={unpriv_ppv:.4f})"
    )


def compute_calibration_difference(
    X_test: pd.DataFrame,
    y_true: np.ndarray,
    confidence_scores: np.ndarray,
    protected_attribute: str,
    privileged_value: Any,
    unprivileged_value: Any,
    positive_value: Any = 1,
    n_bins: int = 10,
    threshold: float = 0.05
) -> MetricResult:
    """
    Compute Calibration Difference across groups.
    
    Bins confidence scores into deciles and compares actual positive rates
    between privileged and unprivileged groups.
    
    Args:
        X_test: Test features
        y_true: True labels
        confidence_scores: Model confidence scores
        protected_attribute: Name of protected attribute
        privileged_value: Value representing privileged group
        unprivileged_value: Value representing unprivileged group
        positive_value: Value representing positive prediction
        n_bins: Number of bins for calibration
        threshold: Maximum acceptable difference
        
    Returns:
        MetricResult object
    """
    if confidence_scores is None:
        return MetricResult(
            metric_name="Calibration Difference",
            value=0.0,
            threshold=threshold,
            passed=True,
            description="Skipped (no confidence scores available)"
        )
    
    priv_mask = X_test[protected_attribute] == privileged_value
    unpriv_mask = X_test[protected_attribute] == unprivileged_value
    
    # Create bins
    bins = np.linspace(0, 1, n_bins + 1)
    
    max_diff = 0.0
    
    for i in range(n_bins):
        bin_mask = (confidence_scores >= bins[i]) & (confidence_scores < bins[i + 1])
        
        # Privileged group in this bin
        priv_bin_mask = priv_mask & bin_mask
        if priv_bin_mask.sum() > 0:
            priv_actual_rate = (y_true[priv_bin_mask] == positive_value).mean()
        else:
            priv_actual_rate = 0.0
        
        # Unprivileged group in this bin
        unpriv_bin_mask = unpriv_mask & bin_mask
        if unpriv_bin_mask.sum() > 0:
            unpriv_actual_rate = (y_true[unpriv_bin_mask] == positive_value).mean()
        else:
            unpriv_actual_rate = 0.0
        
        # Track maximum difference across bins
        diff = abs(priv_actual_rate - unpriv_actual_rate)
        max_diff = max(max_diff, diff)
    
    passed = max_diff <= threshold
    
    return MetricResult(
        metric_name="Calibration Difference",
        value=max_diff,
        threshold=threshold,
        passed=passed,
        privileged_group=f"{protected_attribute}={privileged_value}",
        unprivileged_group=f"{protected_attribute}={unprivileged_value}",
        description=f"Max calibration difference across {n_bins} bins: {max_diff:.4f}"
    )


def compute_all_fairness_metrics(
    X_test: pd.DataFrame,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    confidence_scores: Optional[np.ndarray],
    protected_attribute: str,
    privileged_value: Any,
    unprivileged_value: Any,
    positive_value: Any = 1,
    thresholds: Optional[dict[str, float]] = None
) -> dict[str, MetricResult]:
    """
    Compute all fairness metrics for a single protected attribute pair.
    
    Args:
        X_test: Test features
        y_true: True labels
        y_pred: Predictions
        confidence_scores: Model confidence scores (optional)
        protected_attribute: Name of protected attribute
        privileged_value: Value representing privileged group
        unprivileged_value: Value representing unprivileged group
        positive_value: Value representing positive prediction
        thresholds: Custom thresholds for each metric
        
    Returns:
        Dictionary mapping metric names to MetricResult objects
    """
    if thresholds is None:
        thresholds = {
            "demographic_parity": 0.10,
            "disparate_impact": 0.80,
            "equalized_odds": 0.10,
            "predictive_parity": 0.05,
            "calibration": 0.05,
        }
    
    metrics = {}
    
    # Demographic Parity
    metrics["demographic_parity"] = compute_demographic_parity(
        X_test, y_pred, protected_attribute,
        privileged_value, unprivileged_value, positive_value,
        thresholds.get("demographic_parity", 0.10)
    )
    
    # Disparate Impact
    metrics["disparate_impact"] = compute_disparate_impact(
        X_test, y_pred, protected_attribute,
        privileged_value, unprivileged_value, positive_value,
        thresholds.get("disparate_impact", 0.80)
    )
    
    # Equalized Odds
    metrics["equalized_odds"] = compute_equalized_odds(
        X_test, y_true, y_pred, protected_attribute,
        privileged_value, unprivileged_value, positive_value,
        thresholds.get("equalized_odds", 0.10)
    )
    
    # Predictive Parity
    metrics["predictive_parity"] = compute_predictive_parity(
        X_test, y_true, y_pred, protected_attribute,
        privileged_value, unprivileged_value, positive_value,
        thresholds.get("predictive_parity", 0.05)
    )
    
    # Calibration (if confidence scores available)
    if confidence_scores is not None:
        metrics["calibration"] = compute_calibration_difference(
            X_test, y_true, confidence_scores, protected_attribute,
            privileged_value, unprivileged_value, positive_value,
            n_bins=10,
            threshold=thresholds.get("calibration", 0.05)
        )
    
    return metrics
