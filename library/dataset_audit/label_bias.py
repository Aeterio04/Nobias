import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Dict, Tuple
from .models import DatasetFinding


def analyze_label_bias(
    df: pd.DataFrame,
    protected_attributes: List[str]
) -> Tuple[Dict[str, Dict], List[DatasetFinding]]:
    """
    Analyze label bias across protected groups.
    
    Args:
        df: Input DataFrame with '_target_binary' column
        protected_attributes: List of protected column names
        
    Returns:
        Tuple of (label rates dict, list of findings)
    """
    label_rates = {}
    findings = []
    logs = []
    
    for attr in protected_attributes:
        rates = {}
        groups = df[attr].unique()
        
        if len(groups) < 2:
            logs.append(f"Skipping label bias for '{attr}': only 1 group")
            continue
        
        # Compute positive rate per group
        group_rates = {}
        for group in groups:
            group_df = df[df[attr] == group]
            if len(group_df) == 0:
                continue
            
            pos_rate = group_df['_target_binary'].mean()
            group_rates[str(group)] = {
                'positive_rate': round(pos_rate, 4),
                'count': len(group_df),
                'positive_count': int(group_df['_target_binary'].sum())
            }
        
        if not group_rates:
            continue
        
        # Find privileged group (highest positive rate)
        privileged_group = max(group_rates.keys(), key=lambda g: group_rates[g]['positive_rate'])
        privileged_rate = group_rates[privileged_group]['positive_rate']
        
        if privileged_rate == 0:
            logs.append(f"Warning: privileged group '{privileged_group}' in '{attr}' has 0 positive rate. Skipping DIR/SPD.")
            label_rates[attr] = group_rates
            continue
        
        # Compute DIR and SPD for each unprivileged group
        for group, group_stats in group_rates.items():
            if group == privileged_group:
                continue
            
            unprivileged_rate = group_stats['positive_rate']
            
            # DIR
            dir_value = unprivileged_rate / privileged_rate if privileged_rate > 0 else None
            
            # SPD
            spd_value = unprivileged_rate - privileged_rate
            
            # Chi-square test
            contingency = pd.crosstab(df[attr] == group, df['_target_binary'])
            chi2, p_value, _, _ = stats.chi2_contingency(contingency)
            
            confidence = _compute_confidence(group_stats['count'])
            
            # Flag based on thresholds
            if dir_value is not None:
                if dir_value < 0.60 and p_value < 0.01:
                    findings.append(DatasetFinding(
                        check='label_bias',
                        severity='CRITICAL',
                        message=f"Severe disparate impact in '{attr}': group '{group}' has {dir_value:.2f}x positive rate vs '{privileged_group}' (p={p_value:.4f})",
                        metric='DIR',
                        value=dir_value,
                        threshold=0.60,
                        confidence=confidence
                    ))
                elif dir_value < 0.80 and p_value < 0.05:
                    findings.append(DatasetFinding(
                        check='label_bias',
                        severity='MODERATE',
                        message=f"Disparate impact in '{attr}': group '{group}' has {dir_value:.2f}x positive rate vs '{privileged_group}' (p={p_value:.4f})",
                        metric='DIR',
                        value=dir_value,
                        threshold=0.80,
                        confidence=confidence
                    ))
                elif dir_value < 0.90:
                    findings.append(DatasetFinding(
                        check='label_bias',
                        severity='LOW',
                        message=f"Minor disparate impact in '{attr}': group '{group}' has {dir_value:.2f}x positive rate vs '{privileged_group}'",
                        metric='DIR',
                        value=dir_value,
                        threshold=0.90,
                        confidence=confidence
                    ))
            
            if spd_value < -0.20 and p_value < 0.01:
                findings.append(DatasetFinding(
                    check='label_bias',
                    severity='CRITICAL',
                    message=f"Severe statistical parity violation in '{attr}': group '{group}' has {spd_value:.3f} lower positive rate (p={p_value:.4f})",
                    metric='SPD',
                    value=spd_value,
                    threshold=-0.20,
                    confidence=confidence
                ))
            elif spd_value < -0.10 and p_value < 0.05:
                findings.append(DatasetFinding(
                    check='label_bias',
                    severity='MODERATE',
                    message=f"Statistical parity violation in '{attr}': group '{group}' has {spd_value:.3f} lower positive rate (p={p_value:.4f})",
                    metric='SPD',
                    value=spd_value,
                    threshold=-0.10,
                    confidence=confidence
                ))
            elif spd_value < -0.05:
                findings.append(DatasetFinding(
                    check='label_bias',
                    severity='LOW',
                    message=f"Minor statistical parity gap in '{attr}': group '{group}' has {spd_value:.3f} lower positive rate",
                    metric='SPD',
                    value=spd_value,
                    threshold=-0.05,
                    confidence=confidence
                ))
            
            # Chi-square independence test
            if p_value < 0.05:
                logs.append(f"Chi-square test for '{attr}': χ²={chi2:.2f}, p={p_value:.4f} (significant)")
        
        label_rates[attr] = group_rates
    
    return label_rates, findings


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
