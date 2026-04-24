from typing import List
from .models import DatasetFinding


SEVERITY_ORDER = {
    'CRITICAL': 4,
    'MODERATE': 3,
    'LOW': 2,
    'CLEAR': 1
}


def classify_overall_severity(findings: List[DatasetFinding]) -> str:
    """
    Classify overall severity based on all findings.
    
    Args:
        findings: List of DatasetFinding objects
        
    Returns:
        Overall severity: CRITICAL, MODERATE, LOW, or CLEAR
    """
    if not findings:
        return 'CLEAR'
    
    # Get worst severity
    worst_severity = max(
        findings,
        key=lambda f: SEVERITY_ORDER.get(f.severity, 0)
    ).severity
    
    return worst_severity


def severity_to_color(severity: str) -> str:
    """Map severity to color for visualization."""
    return {
        'CRITICAL': 'red',
        'MODERATE': 'orange',
        'LOW': 'yellow',
        'CLEAR': 'green'
    }.get(severity, 'gray')
