"""
NoBias Dataset Audit Module

Detects statistical biases in tabular datasets before model training.
"""

from typing import Union, List, Any
from pathlib import Path
import pandas as pd

from .ingestion import load_and_validate, suggest_protected_columns
from .representation import analyze_representation, analyze_intersectional_representation
from .label_bias import analyze_label_bias
from .proxy_detection import detect_proxy_features
from .missing_data import analyze_missing_data
from .intersectional import analyze_intersectional_disparities
from .divergence import analyze_kl_divergence
from .severity import classify_overall_severity
from .remediation import suggest_remediations
from .report import DatasetAuditReport
from .models import DatasetFinding, ProxyFeature, Remediation


__all__ = [
    'audit_dataset',
    'suggest_protected_columns',
    'DatasetAuditReport',
    'DatasetFinding',
    'ProxyFeature',
    'Remediation'
]


def audit_dataset(
    data: Union[str, Path, pd.DataFrame],
    protected_attributes: List[str],
    target_column: str,
    positive_value: Any
) -> DatasetAuditReport:
    """
    Audit a dataset for statistical biases.
    
    Args:
        data: File path (CSV, Excel, Parquet) or pandas DataFrame
        protected_attributes: List of protected column names (e.g., ['gender', 'race'])
        target_column: Name of the target/label column
        positive_value: Value representing the positive class (e.g., 1, 'Yes', '>50K')
        
    Returns:
        DatasetAuditReport with findings and remediation suggestions
        
    Raises:
        ValueError: If validation fails
        
    Example:
        >>> report = audit_dataset(
        ...     data='hiring_data.csv',
        ...     protected_attributes=['gender', 'race'],
        ...     target_column='hired',
        ...     positive_value=1
        ... )
        >>> print(report.overall_severity)
        >>> print(report.to_text())
        >>> report.export('audit.json')
    """
    logs = []
    all_findings = []
    
    # Phase 1: Ingestion
    logs.append("Phase 1: Data ingestion and validation")
    df, metadata = load_and_validate(data, protected_attributes, target_column, positive_value)
    logs.extend(metadata['logs'])
    
    # Phase 2: Representation
    logs.append("Phase 2: Representation analysis")
    representation, rep_findings = analyze_representation(df, protected_attributes)
    all_findings.extend(rep_findings)
    
    intersectional_rep, intersect_rep_findings = analyze_intersectional_representation(
        df, protected_attributes
    )
    all_findings.extend(intersect_rep_findings)
    logs.append(f"Found {len(rep_findings)} representation issues")
    
    # Phase 3: Label Bias
    logs.append("Phase 3: Label bias analysis")
    label_rates, label_findings = analyze_label_bias(df, protected_attributes)
    all_findings.extend(label_findings)
    logs.append(f"Found {len(label_findings)} label bias issues")
    
    # Phase 4: Proxy Detection
    logs.append("Phase 4: Proxy feature detection")
    proxy_features = detect_proxy_features(df, protected_attributes, target_column)
    logs.append(f"Detected {len(proxy_features)} potential proxy features")
    
    # Phase 5: Missing Data
    logs.append("Phase 5: Missing data analysis")
    missing_data_matrix, missing_findings = analyze_missing_data(df, protected_attributes)
    all_findings.extend(missing_findings)
    logs.append(f"Found {len(missing_findings)} missing data issues")
    
    # Phase 6: Intersectional Disparities
    logs.append("Phase 6: Intersectional disparity analysis")
    intersectional_disparities, intersect_findings = analyze_intersectional_disparities(
        df, protected_attributes
    )
    all_findings.extend(intersect_findings)
    logs.append(f"Found {len(intersect_findings)} intersectional disparities")
    
    # Phase 7: KL Divergence
    logs.append("Phase 7: KL divergence analysis")
    kl_divergences, kl_findings = analyze_kl_divergence(df, protected_attributes)
    all_findings.extend(kl_findings)
    logs.append(f"Found {len(kl_findings)} distribution shifts")
    
    # Severity Classification
    overall_severity = classify_overall_severity(all_findings)
    logs.append(f"Overall severity: {overall_severity}")
    
    # Remediation Suggestions
    logs.append("Generating remediation suggestions")
    remediation_suggestions = suggest_remediations(df, protected_attributes, label_rates)
    logs.append(f"Generated {len(remediation_suggestions)} remediation strategies")
    
    # Build report
    report = DatasetAuditReport(
        dataset_name=metadata['dataset_name'],
        row_count=metadata['row_count'],
        column_count=metadata['column_count'],
        overall_severity=overall_severity,
        findings=all_findings,
        representation=representation,
        label_rates=label_rates,
        proxy_features=proxy_features,
        missing_data_matrix=missing_data_matrix,
        intersectional_disparities=intersectional_disparities,
        kl_divergences=kl_divergences,
        remediation_suggestions=remediation_suggestions,
        logs=logs
    )
    
    return report
