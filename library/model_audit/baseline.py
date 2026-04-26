"""
Baseline prediction and per-group performance metrics.
"""
import numpy as np
import pandas as pd
from typing import Any, Optional
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)
from .models import ModelType


def get_predictions(
    model: Any,
    X_test: pd.DataFrame,
    model_type: ModelType
) -> tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Get predictions and confidence scores from model.
    
    Args:
        model: The model object
        X_test: Test features
        model_type: Type of model
        
    Returns:
        Tuple of (predictions, confidence_scores)
        confidence_scores is None for regressors or models without predict_proba
    """
    predictions = model.predict(X_test)
    
    # Get confidence scores if available (classifiers only)
    confidence_scores = None
    if model_type != ModelType.REGRESSOR:
        if hasattr(model, 'predict_proba') and callable(model.predict_proba):
            proba = model.predict_proba(X_test)
            
            # For binary classification, use probability of positive class
            if model_type == ModelType.CLASSIFIER_BINARY:
                if proba.shape[1] == 2:
                    confidence_scores = proba[:, 1]
                else:
                    confidence_scores = proba[:, 0]
            else:
                # For multiclass, use max probability
                confidence_scores = np.max(proba, axis=1)
    
    return predictions, confidence_scores


def compute_baseline_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_type: ModelType,
    positive_value: Any = 1
) -> dict[str, float]:
    """
    Compute baseline performance metrics on full test set.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        model_type: Type of model
        positive_value: Value considered as positive class (for binary classification)
        
    Returns:
        Dictionary of metric names to values
    """
    metrics = {}
    
    if model_type == ModelType.REGRESSOR:
        # Regression metrics
        metrics['mse'] = mean_squared_error(y_true, y_pred)
        metrics['rmse'] = np.sqrt(metrics['mse'])
        metrics['mae'] = mean_absolute_error(y_true, y_pred)
        metrics['r2'] = r2_score(y_true, y_pred)
    else:
        # Classification metrics
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        
        if model_type == ModelType.CLASSIFIER_BINARY:
            # Binary classification metrics
            metrics['precision'] = precision_score(y_true, y_pred, pos_label=positive_value, zero_division=0)
            metrics['recall'] = recall_score(y_true, y_pred, pos_label=positive_value, zero_division=0)
            metrics['f1'] = f1_score(y_true, y_pred, pos_label=positive_value, zero_division=0)
            
            # Confusion matrix components
            cm = confusion_matrix(y_true, y_pred, labels=[positive_value, 1 - positive_value if isinstance(positive_value, int) else 0])
            if cm.size == 4:
                tn, fp, fn, tp = cm.ravel()
                metrics['true_positives'] = int(tp)
                metrics['true_negatives'] = int(tn)
                metrics['false_positives'] = int(fp)
                metrics['false_negatives'] = int(fn)
                
                # Rates
                metrics['tpr'] = tp / (tp + fn) if (tp + fn) > 0 else 0  # True Positive Rate / Recall
                metrics['tnr'] = tn / (tn + fp) if (tn + fp) > 0 else 0  # True Negative Rate / Specificity
                metrics['fpr'] = fp / (fp + tn) if (fp + tn) > 0 else 0  # False Positive Rate
                metrics['fnr'] = fn / (fn + tp) if (fn + tp) > 0 else 0  # False Negative Rate
                
                # Positive Predictive Value
                metrics['ppv'] = tp / (tp + fp) if (tp + fp) > 0 else 0
        else:
            # Multiclass metrics
            metrics['precision'] = precision_score(y_true, y_pred, average='weighted', zero_division=0)
            metrics['recall'] = recall_score(y_true, y_pred, average='weighted', zero_division=0)
            metrics['f1'] = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    return metrics


def compute_per_group_metrics(
    X_test: pd.DataFrame,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    protected_attributes: list[str],
    model_type: ModelType,
    positive_value: Any = 1
) -> dict[str, dict[str, float]]:
    """
    Compute performance metrics separately for each demographic group.
    
    Args:
        X_test: Test features (includes protected attributes)
        y_true: True labels
        y_pred: Predicted labels
        protected_attributes: List of protected attribute column names
        model_type: Type of model
        positive_value: Value considered as positive class
        
    Returns:
        Nested dict: {attribute: {group_value: {metric: value}}}
    """
    per_group = {}
    
    for attr in protected_attributes:
        if attr not in X_test.columns:
            continue
        
        per_group[attr] = {}
        unique_values = X_test[attr].unique()
        
        for value in unique_values:
            # Get indices for this group
            mask = X_test[attr] == value
            
            if mask.sum() == 0:
                continue
            
            # Compute metrics for this group
            group_y_true = y_true[mask]
            group_y_pred = y_pred[mask]
            
            group_metrics = compute_baseline_metrics(
                group_y_true,
                group_y_pred,
                model_type,
                positive_value
            )
            
            # Add sample count
            group_metrics['sample_count'] = int(mask.sum())
            
            per_group[attr][str(value)] = group_metrics
    
    return per_group


def compute_approval_rates(
    X_test: pd.DataFrame,
    y_pred: np.ndarray,
    protected_attributes: list[str],
    positive_value: Any = 1
) -> dict[str, dict[str, float]]:
    """
    Compute approval/positive prediction rates per group.
    
    Args:
        X_test: Test features (includes protected attributes)
        y_pred: Predicted labels
        protected_attributes: List of protected attribute column names
        positive_value: Value considered as positive class
        
    Returns:
        Nested dict: {attribute: {group_value: approval_rate}}
    """
    approval_rates = {}
    
    for attr in protected_attributes:
        if attr not in X_test.columns:
            continue
        
        approval_rates[attr] = {}
        unique_values = X_test[attr].unique()
        
        for value in unique_values:
            mask = X_test[attr] == value
            
            if mask.sum() == 0:
                continue
            
            group_preds = y_pred[mask]
            approval_rate = (group_preds == positive_value).mean()
            approval_rates[attr][str(value)] = float(approval_rate)
    
    return approval_rates


def get_group_label(attr: str, value: Any) -> str:
    """Create a readable label for a demographic group."""
    return f"{attr}={value}"


def compute_confusion_matrix_per_group(
    X_test: pd.DataFrame,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    protected_attributes: list[str],
    positive_value: Any = 1
) -> dict[str, dict[str, dict[str, int]]]:
    """
    Compute confusion matrix components for each demographic group.
    
    Args:
        X_test: Test features
        y_true: True labels
        y_pred: Predicted labels
        protected_attributes: Protected attribute column names
        positive_value: Positive class value
        
    Returns:
        Nested dict: {attribute: {group_value: {tp, tn, fp, fn}}}
    """
    cm_per_group = {}
    
    for attr in protected_attributes:
        if attr not in X_test.columns:
            continue
        
        cm_per_group[attr] = {}
        unique_values = X_test[attr].unique()
        
        for value in unique_values:
            mask = X_test[attr] == value
            
            if mask.sum() == 0:
                continue
            
            group_y_true = y_true[mask]
            group_y_pred = y_pred[mask]
            
            # Compute confusion matrix
            cm = confusion_matrix(
                group_y_true,
                group_y_pred,
                labels=[positive_value, 1 - positive_value if isinstance(positive_value, int) else 0]
            )
            
            if cm.size == 4:
                tn, fp, fn, tp = cm.ravel()
                cm_per_group[attr][str(value)] = {
                    'tp': int(tp),
                    'tn': int(tn),
                    'fp': int(fp),
                    'fn': int(fn),
                }
    
    return cm_per_group
