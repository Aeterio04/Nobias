"""
model_audit.report.generator — Report Generation Logic
=======================================================

Core report generation functions.
"""

from typing import Dict, Any
from ..models import ModelAuditReport
from .sections import (
    build_health_section,
    build_config_section,
    build_results_section,
    build_findings_section,
    build_mitigation_section,
    build_compliance_section,
    build_validity_section,
)


def generate_comprehensive_report(report: ModelAuditReport) -> Dict[str, Any]:
    """
    Generate comprehensive report with all sections.
    
    Args:
        report: ModelAuditReport object
        
    Returns:
        Dict with all report sections
    """
    return {
        "health": build_health_section(report),
        "config": build_config_section(report),
        "results": build_results_section(report),
        "findings": build_findings_section(report),
        "mitigation": build_mitigation_section(report),
        "compliance": build_compliance_section(report),
        "validity": build_validity_section(report),
    }


def build_report_summary(report: ModelAuditReport) -> str:
    """
    Build a concise summary of the report.
    
    Args:
        report: ModelAuditReport object
        
    Returns:
        Summary string
    """
    lines = []
    lines.append(f"Model: {report.model_name}")
    lines.append(f"Severity: {report.overall_severity.value}")
    lines.append(f"Flip Rate: {report.counterfactual_result.flip_rate:.2%}")
    
    critical = sum(1 for f in report.findings if f.severity.value == "CRITICAL")
    moderate = sum(1 for f in report.findings if f.severity.value == "MODERATE")
    
    lines.append(f"Findings: {critical} critical, {moderate} moderate")
    
    passed = sum(1 for m in report.scorecard.values() if m.passed)
    total = len(report.scorecard)
    lines.append(f"Metrics: {passed}/{total} passed ({passed/total*100:.0f}%)")
    
    return "\n".join(lines)
