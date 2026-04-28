"""
Counterfactual flip testing for individual fairness.
"""
import numpy as np
import pandas as pd
from typing import Any, Optional
from .models import CounterfactualPair, CounterfactualResult, ModelType


def run_counterfactual_test(
    model: Any,
    X_test: pd.DataFrame,
    y_pred: np.ndarray,
    confidence_scores: Optional[np.ndarray],
    protected_attributes: list[str],
    model_type: ModelType,
    sample_limit: Optional[int] = None,
    X_for_model_columns: Optional[list[str]] = None,
) -> CounterfactualResult:
    """
    Run counterfactual flip test by swapping protected attributes.
    
    For each sample, create counterfactual versions by changing each protected
    attribute to other possible values, then check if predictions change.
    
    Args:
        model: The model object
        X_test: Test features (includes protected attributes)
        y_pred: Original predictions
        confidence_scores: Original confidence scores (if available)
        protected_attributes: List of protected attribute column names
        model_type: Type of model
        sample_limit: Maximum number of samples to test (None = all)
        X_for_model_columns: Columns that model expects (excludes protected attrs if not used)
        
    Returns:
        CounterfactualResult with flip statistics and examples
    """
    # Determine which columns to use for model predictions
    if X_for_model_columns is None:
        # Use all columns
        model_columns = list(X_test.columns)
    else:
        model_columns = X_for_model_columns
    # Limit samples if requested
    if sample_limit is not None and len(X_test) > sample_limit:
        indices = np.random.choice(len(X_test), sample_limit, replace=False)
        X_test_sample = X_test.iloc[indices].copy()
        y_pred_sample = y_pred[indices]
        confidence_sample = confidence_scores[indices] if confidence_scores is not None else None
    else:
        X_test_sample = X_test.copy()
        y_pred_sample = y_pred
        confidence_sample = confidence_scores
        indices = np.arange(len(X_test))
    
    total_comparisons = 0
    total_flips = 0
    flips_by_attribute = {attr: 0 for attr in protected_attributes}
    flip_examples = []
    score_differences = []
    
    # For each sample
    for idx, (sample_idx, row) in enumerate(X_test_sample.iterrows()):
        original_pred = y_pred_sample[idx]
        original_conf = confidence_sample[idx] if confidence_sample is not None else None
        
        # For each protected attribute
        for attr in protected_attributes:
            if attr not in X_test_sample.columns:
                continue
            
            original_value = row[attr]
            
            # Get all possible values for this attribute
            possible_values = X_test[attr].unique()
            
            # Create counterfactuals for each other value
            for cf_value in possible_values:
                if cf_value == original_value:
                    continue
                
                # Create counterfactual sample
                cf_sample = row.copy()
                cf_sample[attr] = cf_value
                cf_df = pd.DataFrame([cf_sample])
                
                # Use only columns model expects
                cf_df_for_model = cf_df[model_columns]
                
                # Get counterfactual prediction
                try:
                    cf_pred = model.predict(cf_df_for_model)[0]
                    
                    # Get confidence if available
                    cf_conf = None
                    if model_type != ModelType.REGRESSOR and hasattr(model, 'predict_proba'):
                        cf_proba = model.predict_proba(cf_df_for_model)
                        if model_type == ModelType.CLASSIFIER_BINARY:
                            cf_conf = cf_proba[0, 1] if cf_proba.shape[1] == 2 else cf_proba[0, 0]
                        else:
                            cf_conf = np.max(cf_proba[0])
                    
                    total_comparisons += 1
                    
                    # Check if prediction flipped
                    if cf_pred != original_pred:
                        total_flips += 1
                        flips_by_attribute[attr] += 1
                        
                        # Calculate confidence delta if available
                        conf_delta = None
                        if original_conf is not None and cf_conf is not None:
                            conf_delta = abs(cf_conf - original_conf)
                            score_differences.append(conf_delta)
                        
                        # Store example
                        flip_examples.append(CounterfactualPair(
                            original_index=int(sample_idx),
                            original_prediction=original_pred,
                            original_confidence=float(original_conf) if original_conf is not None else None,
                            counterfactual_prediction=cf_pred,
                            counterfactual_confidence=float(cf_conf) if cf_conf is not None else None,
                            flipped_attribute=attr,
                            original_value=original_value,
                            counterfactual_value=cf_value,
                            confidence_delta=float(conf_delta) if conf_delta is not None else None,
                        ))
                    else:
                        # Even if no flip, track score difference for MASD
                        if original_conf is not None and cf_conf is not None:
                            score_differences.append(abs(cf_conf - original_conf))
                
                except Exception as e:
                    # Skip this counterfactual if prediction fails
                    print(f"Warning: Counterfactual prediction failed for sample {sample_idx}, attr {attr}: {e}")
                    continue
    
    # Calculate statistics
    flip_rate = total_flips / total_comparisons if total_comparisons > 0 else 0.0
    
    flip_rates_by_attribute = {
        attr: flips_by_attribute[attr] / total_comparisons if total_comparisons > 0 else 0.0
        for attr in protected_attributes
    }
    
    # Mean Absolute Score Difference (MASD)
    masd = float(np.mean(score_differences)) if score_differences else None
    
    # Sort flip examples by confidence delta (most extreme first)
    flip_examples.sort(
        key=lambda x: x.confidence_delta if x.confidence_delta is not None else 0,
        reverse=True
    )
    
    # Keep top 20 examples
    top_examples = flip_examples[:20]
    
    return CounterfactualResult(
        total_samples=len(X_test_sample),
        total_comparisons=total_comparisons,
        total_flips=total_flips,
        flip_rate=flip_rate,
        mean_absolute_score_difference=masd,
        flips_by_attribute=flips_by_attribute,
        flip_rates_by_attribute=flip_rates_by_attribute,
        top_flip_examples=top_examples,
    )


def identify_high_risk_flips(
    counterfactual_result: CounterfactualResult,
    threshold: float = 0.05
) -> list[str]:
    """
    Identify protected attributes with flip rates above threshold.
    
    Args:
        counterfactual_result: Results from counterfactual testing
        threshold: Flip rate threshold (default 5%)
        
    Returns:
        List of attribute names with high flip rates
    """
    high_risk = []
    
    for attr, flip_rate in counterfactual_result.flip_rates_by_attribute.items():
        if flip_rate > threshold:
            high_risk.append(attr)
    
    return high_risk


def get_flip_examples_by_attribute(
    counterfactual_result: CounterfactualResult,
    attribute: str,
    n: int = 5
) -> list[CounterfactualPair]:
    """
    Get top N flip examples for a specific attribute.
    
    Args:
        counterfactual_result: Results from counterfactual testing
        attribute: Protected attribute name
        n: Number of examples to return
        
    Returns:
        List of CounterfactualPair objects
    """
    examples = [
        ex for ex in counterfactual_result.top_flip_examples
        if ex.flipped_attribute == attribute
    ]
    
    return examples[:n]
