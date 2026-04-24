import pandas as pd
from typing import List, Dict
from .models import DatasetFinding


def analyze_intersectional_disparities(
    df: pd.DataFrame,
    protected_attributes: List[str]
) -> tuple[List[Dict], List[DatasetFinding]]:
    """
    Analyze label disparities in intersectional groups.
    
    Args:
        df: Input DataFrame with '_target_binary' column
        protected_attributes: List of protected column names
        
    Returns:
        Tuple of (intersectional disparities, list of findings)
    """
    disparities = []
    findings = []
    
    if len(protected_attributes) < 2:
        return disparities, findings
    
    # 2-way intersections
    for i in range(len(protected_attributes)):
        for j in range(i + 1, len(protected_attributes)):
            attr1, attr2 = protected_attributes[i], protected_attributes[j]
            
            grouped = df.groupby([attr1, attr2])['_target_binary'].agg(['mean', 'count'])
            
            if len(grouped) < 2:
                continue
            
            rates = {}
            for (val1, val2), row in grouped.iterrows():
                if row['count'] < 10:  # Skip very small groups
                    continue
                rates[(val1, val2)] = row['mean']
            
            if len(rates) < 2:
                continue
            
            # Find best and worst groups
            best_group = max(rates.keys(), key=lambda k: rates[k])
            worst_group = min(rates.keys(), key=lambda k: rates[k])
            
            best_rate = rates[best_group]
            worst_rate = rates[worst_group]
            
            if best_rate == 0:
                continue
            
            # Compute DIR
            dir_value = worst_rate / best_rate
            disparity_pct = (1 - dir_value) * 100
            
            disparity = {
                'attributes': [attr1, attr2],
                'best_group': [str(best_group[0]), str(best_group[1])],
                'worst_group': [str(worst_group[0]), str(worst_group[1])],
                'best_rate': round(best_rate, 4),
                'worst_rate': round(worst_rate, 4),
                'dir': round(dir_value, 3),
                'disparity_pct': round(disparity_pct, 2)
            }
            disparities.append(disparity)
            
            # Flag if disparity > 10%
            if disparity_pct > 10.0:
                confidence = _compute_confidence(grouped.loc[worst_group, 'count'])
                
                severity = 'CRITICAL' if dir_value < 0.60 else 'MODERATE' if dir_value < 0.80 else 'LOW'
                
                findings.append(DatasetFinding(
                    check='intersectional_disparity',
                    severity=severity,
                    message=f"Intersectional disparity: ({attr1}={worst_group[0]}, {attr2}={worst_group[1]}) has {disparity_pct:.1f}% lower positive rate than ({attr1}={best_group[0]}, {attr2}={best_group[1]})",
                    metric='DIR',
                    value=dir_value,
                    threshold=0.90,
                    confidence=confidence
                ))
            
            # Check for superadditive bias
            # Compare intersectional disparity to individual attribute disparities
            attr1_rates = df.groupby(attr1)['_target_binary'].mean()
            attr2_rates = df.groupby(attr2)['_target_binary'].mean()
            
            attr1_disparity = (attr1_rates.max() - attr1_rates.min()) if len(attr1_rates) > 1 else 0
            attr2_disparity = (attr2_rates.max() - attr2_rates.min()) if len(attr2_rates) > 1 else 0
            
            max_individual_disparity = max(attr1_disparity, attr2_disparity)
            intersectional_disparity_abs = best_rate - worst_rate
            
            if intersectional_disparity_abs > max_individual_disparity * 1.2:
                findings.append(DatasetFinding(
                    check='superadditive_bias',
                    severity='MODERATE',
                    message=f"Superadditive bias detected: intersectional disparity ({intersectional_disparity_abs:.3f}) exceeds individual attribute disparities",
                    metric='disparity_ratio',
                    value=intersectional_disparity_abs / max_individual_disparity if max_individual_disparity > 0 else 0,
                    threshold=1.2,
                    confidence=0.8
                ))
    
    # Sort by disparity magnitude
    disparities.sort(key=lambda x: x['disparity_pct'], reverse=True)
    
    return disparities, findings


def _compute_confidence(sample_size: int) -> float:
    """Compute confidence score based on sample size."""
    if sample_size < 30:
        return 0.3
    elif sample_size < 100:
        return 0.6
    elif sample_size < 500:
        return 0.8
    else:
        return 1.0
