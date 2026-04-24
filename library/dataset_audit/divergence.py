import pandas as pd
import numpy as np
from scipy.special import kl_div
from typing import List, Dict
from .models import DatasetFinding


def analyze_kl_divergence(
    df: pd.DataFrame,
    protected_attributes: List[str]
) -> tuple[Dict[str, Dict], List[DatasetFinding]]:
    """
    Analyze KL divergence of label distributions across groups.
    
    Args:
        df: Input DataFrame with '_target_binary' column
        protected_attributes: List of protected column names
        
    Returns:
        Tuple of (KL divergences dict, list of findings)
    """
    kl_divergences = {}
    findings = []
    epsilon = 1e-10
    
    for attr in protected_attributes:
        groups = df[attr].unique()
        
        if len(groups) < 2:
            continue
        
        # Find majority group
        group_sizes = df[attr].value_counts()
        majority_group = group_sizes.idxmax()
        
        # Get majority group label distribution
        majority_df = df[df[attr] == majority_group]
        majority_dist = np.array([
            (majority_df['_target_binary'] == 0).mean(),
            (majority_df['_target_binary'] == 1).mean()
        ])
        majority_dist = np.clip(majority_dist, epsilon, 1.0)
        
        group_kls = {}
        
        for group in groups:
            if group == majority_group:
                group_kls[str(group)] = 0.0
                continue
            
            group_df = df[df[attr] == group]
            
            if len(group_df) < 10:
                continue
            
            # Get group label distribution
            group_dist = np.array([
                (group_df['_target_binary'] == 0).mean(),
                (group_df['_target_binary'] == 1).mean()
            ])
            group_dist = np.clip(group_dist, epsilon, 1.0)
            
            # Compute KL divergence
            kl = np.sum(kl_div(group_dist, majority_dist))
            
            if np.isnan(kl) or np.isinf(kl):
                kl = 0.0
            
            group_kls[str(group)] = round(kl, 4)
            
            # Flag if KL > 0.1
            if kl > 0.1:
                confidence = _compute_confidence(len(group_df))
                
                severity = 'MODERATE' if kl > 0.2 else 'LOW'
                
                findings.append(DatasetFinding(
                    check='kl_divergence',
                    severity=severity,
                    message=f"Label distribution shift in '{attr}': group '{group}' has KL divergence of {kl:.4f} from majority group '{majority_group}'",
                    metric='KL',
                    value=kl,
                    threshold=0.1,
                    confidence=confidence
                ))
        
        kl_divergences[attr] = group_kls
    
    return kl_divergences, findings


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
