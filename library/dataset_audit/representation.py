import pandas as pd
from typing import List, Dict, Tuple
from .models import DatasetFinding


def analyze_representation(
    df: pd.DataFrame,
    protected_attributes: List[str]
) -> Tuple[Dict[str, Dict], List[DatasetFinding]]:
    """
    Analyze representation of groups in the dataset.
    
    Args:
        df: Input DataFrame
        protected_attributes: List of protected column names
        
    Returns:
        Tuple of (representation dict, list of findings)
    """
    representation = {}
    findings = []
    
    for attr in protected_attributes:
        counts = df[attr].value_counts()
        total = len(df)
        
        group_stats = {}
        majority_size = counts.max()
        
        for group, count in counts.items():
            pct = (count / total) * 100
            ratio_to_majority = count / majority_size if majority_size > 0 else 0
            
            group_stats[str(group)] = {
                'count': int(count),
                'percentage': round(pct, 2),
                'ratio_to_majority': round(ratio_to_majority, 3)
            }
            
            # Flag severe under-representation
            if ratio_to_majority < 0.10 and count != majority_size:
                confidence = _compute_confidence(count)
                findings.append(DatasetFinding(
                    check='representation',
                    severity='CRITICAL',
                    message=f"Group '{group}' in '{attr}' is severely under-represented ({count} samples, {pct:.1f}% of dataset, {ratio_to_majority*100:.1f}% of majority group)",
                    metric='ratio_to_majority',
                    value=ratio_to_majority,
                    threshold=0.10,
                    confidence=confidence
                ))
            elif pct < 35.0:
                confidence = _compute_confidence(count)
                findings.append(DatasetFinding(
                    check='representation',
                    severity='MODERATE',
                    message=f"Group '{group}' in '{attr}' is under-represented ({count} samples, {pct:.1f}% of dataset)",
                    metric='percentage',
                    value=pct,
                    threshold=35.0,
                    confidence=confidence
                ))
        
        representation[attr] = group_stats
    
    return representation, findings


def analyze_intersectional_representation(
    df: pd.DataFrame,
    protected_attributes: List[str]
) -> Tuple[List[Dict], List[DatasetFinding]]:
    """
    Analyze representation of intersectional groups.
    
    Args:
        df: Input DataFrame
        protected_attributes: List of protected column names
        
    Returns:
        Tuple of (intersectional stats, list of findings)
    """
    intersectional_stats = []
    findings = []
    
    if len(protected_attributes) < 2:
        return intersectional_stats, findings
    
    # 2-way intersections
    for i in range(len(protected_attributes)):
        for j in range(i + 1, len(protected_attributes)):
            attr1, attr2 = protected_attributes[i], protected_attributes[j]
            
            grouped = df.groupby([attr1, attr2]).size()
            total = len(df)
            
            for (val1, val2), count in grouped.items():
                pct = (count / total) * 100
                
                stat = {
                    'attributes': [attr1, attr2],
                    'values': [str(val1), str(val2)],
                    'count': int(count),
                    'percentage': round(pct, 2)
                }
                intersectional_stats.append(stat)
                
                if pct < 10.0:
                    confidence = _compute_confidence(count)
                    findings.append(DatasetFinding(
                        check='intersectional_representation',
                        severity='MODERATE',
                        message=f"Intersectional group ({attr1}={val1}, {attr2}={val2}) is under-represented ({count} samples, {pct:.1f}%)",
                        metric='percentage',
                        value=pct,
                        threshold=10.0,
                        confidence=confidence
                    ))
    
    return intersectional_stats, findings


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
