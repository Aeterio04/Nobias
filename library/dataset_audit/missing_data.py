import pandas as pd
from scipy import stats
from typing import List, Dict, Tuple
from .models import DatasetFinding


def analyze_missing_data(
    df: pd.DataFrame,
    protected_attributes: List[str]
) -> Tuple[Dict[str, Dict], List[DatasetFinding]]:
    """
    Analyze differential missingness across protected groups.
    
    Args:
        df: Input DataFrame
        protected_attributes: List of protected column names
        
    Returns:
        Tuple of (missingness matrix, list of findings)
    """
    missingness_matrix = {}
    findings = []
    
    # Get columns with missing data
    cols_with_missing = [col for col in df.columns if df[col].isna().any()]
    
    if not cols_with_missing:
        return missingness_matrix, findings
    
    for col in cols_with_missing:
        if col in protected_attributes or col == '_target_binary':
            continue
        
        col_matrix = {}
        
        for attr in protected_attributes:
            group_missingness = {}
            groups = df[attr].unique()
            
            for group in groups:
                group_df = df[df[attr] == group]
                if len(group_df) == 0:
                    continue
                
                missing_pct = (group_df[col].isna().sum() / len(group_df)) * 100
                group_missingness[str(group)] = round(missing_pct, 2)
            
            if not group_missingness:
                continue
            
            col_matrix[attr] = group_missingness
            
            # Check for differential missingness
            missing_rates = list(group_missingness.values())
            if len(missing_rates) >= 2:
                max_rate = max(missing_rates)
                min_rate = min(missing_rates)
                diff = max_rate - min_rate
                
                if diff > 5.0:
                    # Chi-square test for independence
                    contingency = pd.crosstab(df[attr], df[col].isna())
                    chi2, p_value, _, _ = stats.chi2_contingency(contingency)
                    
                    if p_value < 0.05:
                        findings.append(DatasetFinding(
                            check='missing_data',
                            severity='MODERATE',
                            message=f"Differential missingness in '{col}' across '{attr}': {diff:.1f}% gap between groups (p={p_value:.4f})",
                            metric='missingness_gap',
                            value=diff,
                            threshold=5.0,
                            confidence=0.9
                        ))
        
        if col_matrix:
            missingness_matrix[col] = col_matrix
    
    return missingness_matrix, findings
