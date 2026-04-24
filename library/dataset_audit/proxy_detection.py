import pandas as pd
import numpy as np
from scipy import stats
from sklearn.metrics import mutual_info_score
from typing import List
from .models import ProxyFeature


def detect_proxy_features(
    df: pd.DataFrame,
    protected_attributes: List[str],
    target_column: str
) -> List[ProxyFeature]:
    """
    Detect features that may be proxies for protected attributes.
    
    Args:
        df: Input DataFrame
        protected_attributes: List of protected column names
        target_column: Name of target column
        
    Returns:
        List of ProxyFeature objects, sorted by score descending
    """
    proxy_features = []
    
    # Get non-protected, non-target features
    exclude_cols = set(protected_attributes + [target_column, '_target_binary'])
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    for feature in feature_cols:
        # Skip if all null
        if df[feature].isna().all():
            continue
        
        for protected in protected_attributes:
            score, method = _compute_correlation(df, feature, protected)
            
            if score is None:
                continue
            
            # Compute NMI
            nmi = _compute_nmi(df, feature, protected)
            
            # Flag if correlation > 0.3 OR NMI > 0.1
            if score > 0.3 or nmi > 0.1:
                proxy_features.append(ProxyFeature(
                    feature=feature,
                    protected=protected,
                    method=method,
                    score=round(score, 3),
                    nmi=round(nmi, 3)
                ))
    
    # Sort by score descending
    proxy_features.sort(key=lambda x: x.score, reverse=True)
    
    return proxy_features


def _compute_correlation(df: pd.DataFrame, feature: str, protected: str) -> tuple:
    """
    Compute correlation between feature and protected attribute.
    
    Returns:
        Tuple of (score, method_name)
    """
    feature_data = df[feature].dropna()
    protected_data = df.loc[feature_data.index, protected]
    
    if len(feature_data) == 0:
        return None, None
    
    feature_is_numeric = pd.api.types.is_numeric_dtype(feature_data)
    protected_is_numeric = pd.api.types.is_numeric_dtype(protected_data)
    
    try:
        if not feature_is_numeric and not protected_is_numeric:
            # Categorical x Categorical: Cramér's V
            contingency = pd.crosstab(feature_data, protected_data)
            chi2, _, _, _ = stats.chi2_contingency(contingency)
            n = contingency.sum().sum()
            min_dim = min(contingency.shape[0], contingency.shape[1]) - 1
            cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
            return cramers_v, 'cramers_v'
        
        elif feature_is_numeric and not protected_is_numeric:
            # Numeric x Categorical: Point-biserial (if binary) or eta-squared
            if protected_data.nunique() == 2:
                # Point-biserial
                protected_binary = pd.Categorical(protected_data).codes
                corr, _ = stats.pointbiserialr(protected_binary, feature_data)
                return abs(corr), 'point_biserial'
            else:
                # Eta-squared (ANOVA effect size)
                groups = [feature_data[protected_data == val].values for val in protected_data.unique()]
                groups = [g for g in groups if len(g) > 0]
                if len(groups) < 2:
                    return 0.0, 'eta_squared'
                f_stat, _ = stats.f_oneway(*groups)
                # Convert F to eta-squared approximation
                df_between = len(groups) - 1
                df_within = len(feature_data) - len(groups)
                eta_squared = (f_stat * df_between) / (f_stat * df_between + df_within)
                return eta_squared, 'eta_squared'
        
        elif not feature_is_numeric and protected_is_numeric:
            # Categorical x Numeric: same as numeric x categorical
            if feature_data.nunique() == 2:
                feature_binary = pd.Categorical(feature_data).codes
                corr, _ = stats.pointbiserialr(feature_binary, protected_data)
                return abs(corr), 'point_biserial'
            else:
                groups = [protected_data[feature_data == val].values for val in feature_data.unique()]
                groups = [g for g in groups if len(g) > 0]
                if len(groups) < 2:
                    return 0.0, 'eta_squared'
                f_stat, _ = stats.f_oneway(*groups)
                df_between = len(groups) - 1
                df_within = len(protected_data) - len(groups)
                eta_squared = (f_stat * df_between) / (f_stat * df_between + df_within)
                return eta_squared, 'eta_squared'
        
        else:
            # Numeric x Numeric: Pearson correlation
            corr, _ = stats.pearsonr(feature_data, protected_data)
            return abs(corr), 'pearson'
    
    except Exception:
        return None, None


def _compute_nmi(df: pd.DataFrame, feature: str, protected: str) -> float:
    """
    Compute Normalized Mutual Information.
    
    Returns:
        NMI score (0 to 1)
    """
    try:
        feature_data = df[feature].dropna()
        protected_data = df.loc[feature_data.index, protected]
        
        if len(feature_data) == 0:
            return 0.0
        
        # Convert to categorical codes
        feature_codes = pd.Categorical(feature_data).codes
        protected_codes = pd.Categorical(protected_data).codes
        
        # Compute MI
        mi = mutual_info_score(feature_codes, protected_codes)
        
        # Compute entropies
        h_feature = stats.entropy(pd.Series(feature_codes).value_counts())
        h_protected = stats.entropy(pd.Series(protected_codes).value_counts())
        
        # Normalize
        if h_feature == 0 or h_protected == 0:
            return 0.0
        
        nmi = mi / np.sqrt(h_feature * h_protected)
        return nmi
    
    except Exception:
        return 0.0
