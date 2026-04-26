"""
NoBias Dataset Audit Module

Detects statistical biases in tabular datasets before model training.
"""

from typing import Union, List, Any
from pathlib import Path
import pandas as pd
import time
import uuid
from datetime import datetime

from .ingestion import load_and_validate, suggest_protected_columns
from .representation import analyze_representation, analyze_intersectional_representation
from .label_bias import analyze_label_bias
from .proxy_detection import detect_proxy_features
from .missing_data import analyze_missing_data
from .intersectional import analyze_intersectional_disparities
from .divergence import analyze_kl_divergence
from .severity import classify_overall_severity
from .remediation import suggest_remediations
from .models import DatasetAuditReport, DatasetFinding, ProxyFeature, Remediation, DatasetIntegrity

# New advanced report system
from .report_new import generate_report
from .report_new.formatters import JSONFormatter, StringFormatter, PDFFormatter


__all__ = [
    'audit_dataset',
    'suggest_protected_columns',
    'DatasetAuditReport',
    'DatasetFinding',
    'ProxyFeature',
    'Remediation',
    # New report functions
    'generate_report',
    'export_dataset_report_json',
    'export_dataset_report_string',
    'export_dataset_report_pdf',
]


# Convenience functions for new report system
def export_dataset_report_json(audit_report: DatasetAuditReport, filepath: str, mode: str = 'comprehensive') -> None:
    """
    Export dataset audit report as JSON.
    
    Args:
        audit_report: DatasetAuditReport object
        filepath: Output file path
        mode: 'comprehensive' or 'basic'
    """
    report_data = generate_report(audit_report)
    JSONFormatter.save(report_data, filepath, mode)


def export_dataset_report_string(audit_report: DatasetAuditReport, filepath: str, mode: str = 'detailed') -> None:
    """
    Export dataset audit report as text.
    
    Args:
        audit_report: DatasetAuditReport object
        filepath: Output file path
        mode: 'detailed' or 'summary'
    """
    report_data = generate_report(audit_report)
    StringFormatter.save(report_data, filepath, mode)


def export_dataset_report_pdf(audit_report: DatasetAuditReport, filepath: str) -> None:
    """
    Export dataset audit report as PDF.
    
    Args:
        audit_report: DatasetAuditReport object
        filepath: Output file path
    
    Raises:
        ImportError: If reportlab is not installed
    """
    report_data = generate_report(audit_report)
    PDFFormatter.save(report_data, filepath)


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
    # Start timing
    start_time = time.time()
    audit_id = f"dataset_audit_{uuid.uuid4().hex[:8]}"
    
    logs = []
    all_findings = []
    
    logs.append(f"Starting dataset audit: {audit_id}")
    logs.append(f"Timestamp: {datetime.utcnow().isoformat()}")
    
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
    
    # Compute audit integrity
    duration_seconds = time.time() - start_time
    logs.append(f"Audit completed in {duration_seconds:.2f}s")
    
    audit_integrity = DatasetIntegrity(
        data_hash=DatasetIntegrity.compute_hash({
            'row_count': metadata['row_count'],
            'column_count': metadata['column_count'],
            'protected_attributes': protected_attributes,
        }),
        findings_hash=DatasetIntegrity.compute_hash([f.__dict__ for f in all_findings]),
        config_hash=DatasetIntegrity.compute_hash({
            'protected_attributes': protected_attributes,
            'target_column': target_column,
            'positive_value': str(positive_value),
        }),
    )
    audit_integrity.audit_hash = DatasetIntegrity.compute_hash({
        'audit_id': audit_id,
        'data_hash': audit_integrity.data_hash,
        'findings_hash': audit_integrity.findings_hash,
        'config_hash': audit_integrity.config_hash,
    })
    
    # Build report
    report = DatasetAuditReport(
        audit_id=audit_id,
        dataset_name=metadata['dataset_name'],
        row_count=metadata['row_count'],
        column_count=metadata['column_count'],
        protected_attributes=protected_attributes,
        target_column=target_column,
        positive_value=positive_value,
        overall_severity=overall_severity,
        findings=all_findings,
        representation=representation,
        label_rates=label_rates,
        proxy_features=proxy_features,
        missing_data_matrix=missing_data_matrix,
        intersectional_disparities=intersectional_disparities,
        kl_divergences=kl_divergences,
        remediation_suggestions=remediation_suggestions,
        audit_integrity=audit_integrity,
        duration_seconds=duration_seconds,
        timestamp=datetime.utcnow().isoformat(),
        logs=logs
    )
    
    return report
