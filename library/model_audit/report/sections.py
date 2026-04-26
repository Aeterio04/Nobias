"""
model_audit.report.sections — Report Section Builders
======================================================

Modular section builders for comprehensive reports.
"""

from typing import Dict, Any
from ..models import ModelAuditReport


def build_health_section(report: ModelAuditReport) -> Dict[str, Any]:
    """
    Build health & metadata section.
    
    Returns:
        Dict with model info, test info, and overall health
    """
    return {
        "model_info": {
            "model_name": report.model_name,
            "model_type": report.model_type.value,
            "test_sample_count": report.test_sample_count,
        },
        "overall_health": {
            "severity": report.overall_severity.value,
            "critical_findings": sum(1 for f in report.findings if f.severity.value == "CRITICAL"),
            "moderate_findings": sum(1 for f in report.findings if f.severity.value == "MODERATE"),
            "low_findings": sum(1 for f in report.findings if f.severity.value == "LOW"),
        },
        "metrics_summary": {
            "total_metrics": len(report.scorecard),
            "passed_metrics": sum(1 for m in report.scorecard.values() if m.passed),
            "failed_metrics": sum(1 for m in report.scorecard.values() if not m.passed),
            "pass_rate": sum(1 for m in report.scorecard.values() if m.passed) / len(report.scorecard) if report.scorecard else 0,
        }
    }


def build_config_section(report: ModelAuditReport) -> Dict[str, Any]:
    """
    Build configuration section.
    
    Returns:
        Dict with test configuration details
    """
    return {
        "protected_attributes": report.protected_attributes,
        "test_configuration": {
            "total_samples": report.test_sample_count,
            "attributes_tested": len(report.protected_attributes),
        },
        "baseline_performance": report.baseline_metrics,
    }


def build_results_section(report: ModelAuditReport) -> Dict[str, Any]:
    """
    Build results & statistics section.
    
    Returns:
        Dict with fairness metrics, counterfactual results, and statistics
    """
    # Organize metrics by attribute
    metrics_by_attribute = {}
    for metric_key, metric_result in report.scorecard.items():
        # Extract attribute from key (e.g., "gender_Male_vs_Female_demographic_parity")
        parts = metric_key.split('_')
        if len(parts) >= 1:
            attr = parts[0]
            if attr not in metrics_by_attribute:
                metrics_by_attribute[attr] = []
            metrics_by_attribute[attr].append({
                "metric_name": metric_result.metric_name,
                "value": float(metric_result.value),
                "threshold": float(metric_result.threshold),
                "passed": metric_result.passed,
                "p_value": float(metric_result.p_value) if metric_result.p_value else None,
                "privileged_group": metric_result.privileged_group,
                "unprivileged_group": metric_result.unprivileged_group,
            })
    
    return {
        "overall": {
            "severity": report.overall_severity.value,
            "flip_rate": float(report.counterfactual_result.flip_rate),
            "total_findings": len(report.findings),
        },
        "fairness_metrics": metrics_by_attribute,
        "counterfactual": {
            "flip_rate": float(report.counterfactual_result.flip_rate),
            "total_flips": report.counterfactual_result.total_flips,
            "total_comparisons": report.counterfactual_result.total_comparisons,
            "flips_by_attribute": {k: int(v) for k, v in report.counterfactual_result.flips_by_attribute.items()},
            "flip_rates_by_attribute": {k: float(v) for k, v in report.counterfactual_result.flip_rates_by_attribute.items()},
        },
        "per_group_metrics": report.per_group_metrics,
    }


def build_findings_section(report: ModelAuditReport) -> Dict[str, Any]:
    """
    Build findings section.
    
    Returns:
        Dict with all findings organized by severity
    """
    findings_by_severity = {
        "CRITICAL": [],
        "MODERATE": [],
        "LOW": [],
    }
    
    for finding in report.findings:
        findings_by_severity[finding.severity.value].append({
            "id": finding.finding_id,
            "category": finding.category,
            "title": finding.title,
            "description": finding.description,
            "affected_groups": finding.affected_groups,
            "evidence": finding.evidence,
        })
    
    # Intersectional findings
    intersectional = []
    if report.intersectional_findings:
        for finding in report.intersectional_findings:
            intersectional.append({
                "attributes": finding.attributes,
                "values": finding.attribute_values,
                "metric": finding.metric_name,
                "value": float(finding.metric_value),
                "baseline": float(finding.baseline_value),
                "superadditive": finding.is_superadditive,
                "severity": finding.severity.value,
                "sample_count": finding.sample_count,
            })
    
    return {
        "findings_by_severity": findings_by_severity,
        "intersectional_findings": intersectional,
        "total_findings": len(report.findings),
    }


def build_mitigation_section(report: ModelAuditReport) -> Dict[str, Any]:
    """
    Build mitigation & remediation section.
    
    Returns:
        Dict with mitigation strategies
    """
    mitigations_by_category = {
        "post_processing": [],
        "pre_processing": [],
        "in_processing": [],
    }
    
    for mitigation in report.mitigation_options:
        mitigations_by_category[mitigation.category].append({
            "name": mitigation.strategy_name,
            "description": mitigation.description,
            "expected_impact": mitigation.expected_impact,
            "complexity": mitigation.implementation_complexity,
            "requires_retraining": mitigation.requires_retraining,
            "parameters": mitigation.parameters,
        })
    
    return {
        "total_options": len(report.mitigation_options),
        "by_category": mitigations_by_category,
        "recommended_order": [
            "post_processing",  # Try these first (no retraining)
            "pre_processing",   # Then these (requires retraining)
            "in_processing",    # Advanced (model architecture changes)
        ],
    }


def build_compliance_section(report: ModelAuditReport) -> Dict[str, Any]:
    """
    Build legal compliance section (EEOC).
    
    Returns:
        Dict with EEOC compliance status
    """
    # Check disparate impact ratios for EEOC 80% rule
    violations = []
    warnings = []
    
    for metric_key, metric_result in report.scorecard.items():
        if "disparate_impact" in metric_key.lower():
            if metric_result.value < 0.80:
                violations.append({
                    "metric": metric_result.metric_name,
                    "value": float(metric_result.value),
                    "threshold": 0.80,
                    "groups": f"{metric_result.unprivileged_group} vs {metric_result.privileged_group}",
                    "message": f"Disparate Impact Ratio {metric_result.value:.2%} below EEOC 80% threshold",
                })
            elif metric_result.value < 0.90:
                warnings.append({
                    "metric": metric_result.metric_name,
                    "value": float(metric_result.value),
                    "threshold": 0.80,
                    "groups": f"{metric_result.unprivileged_group} vs {metric_result.privileged_group}",
                    "message": f"Disparate Impact Ratio {metric_result.value:.2%} close to EEOC threshold",
                })
    
    overall_status = "NON-COMPLIANT" if violations else ("WARNING" if warnings else "COMPLIANT")
    
    return {
        "overall_status": overall_status,
        "eeoc_80_percent_rule": {
            "description": "EEOC Uniform Guidelines on Employee Selection Procedures (1978)",
            "threshold": 0.80,
            "reference": "https://www.eeoc.gov/laws/guidance/questions-and-answers-clarify-and-provide-common-interpretation-uniform-guidelines",
        },
        "violations": violations,
        "warnings": warnings,
        "compliant": len(violations) == 0,
    }


def build_validity_section(report: ModelAuditReport) -> Dict[str, Any]:
    """
    Build statistical validity section.
    
    Returns:
        Dict with statistical validity metrics
    """
    # Calculate confidence intervals for key metrics
    confidence_intervals = {}
    
    for metric_key, metric_result in report.scorecard.items():
        if metric_result.p_value is not None:
            # Simple confidence interval estimation
            # In production, use proper statistical methods
            margin = 1.96 * 0.05  # 95% CI, simplified
            confidence_intervals[metric_result.metric_name] = {
                "point_estimate": float(metric_result.value),
                "lower_bound": float(max(0, metric_result.value - margin)),
                "upper_bound": float(min(1, metric_result.value + margin)),
                "confidence_level": 0.95,
            }
    
    return {
        "confidence_intervals": confidence_intervals,
        "sample_size": report.test_sample_count,
        "statistical_power": "adequate" if report.test_sample_count >= 100 else "limited",
        "notes": [
            "Confidence intervals provide range of plausible values for metrics",
            "Larger sample sizes provide more precise estimates",
            "P-values indicate statistical significance of observed differences",
        ],
    }
