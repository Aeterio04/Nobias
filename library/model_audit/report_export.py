"""
Report export functionality for model audit reports.

Supports multiple output formats:
- JSON (basic and comprehensive)
- Text (detailed and summary)
- Actionable Insights JSON (for frontend/business users)
- PDF (future)
"""
from typing import Any, Optional, Union
from pathlib import Path
import json
from datetime import datetime


def export_report(
    report: Any,  # ModelAuditReport
    output_path: Union[str, Path],
    format: str = "json",
    include_actionable_insights: bool = True,
    dataset_audit_path: Optional[Union[str, Path]] = None,
) -> None:
    """
    Export model audit report to file.
    
    Args:
        report: ModelAuditReport object
        output_path: Path to save report
        format: Output format ("json", "text", "comprehensive", "actionable")
        include_actionable_insights: Whether to also generate actionable insights JSON
        dataset_audit_path: Optional path to dataset audit for bias amplification analysis
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format == "json" or format == "basic":
        _export_basic_json(report, output_path)
    elif format == "comprehensive":
        _export_comprehensive_json(report, output_path)
    elif format == "text" or format == "detailed":
        _export_detailed_text(report, output_path)
    elif format == "summary":
        _export_summary_text(report, output_path)
    elif format == "actionable":
        _export_actionable_insights(report, output_path, dataset_audit_path)
    else:
        raise ValueError(f"Unknown format: {format}. Use 'json', 'comprehensive', 'text', 'summary', or 'actionable'")
    
    # Also generate actionable insights if requested
    if include_actionable_insights and format != "actionable":
        actionable_path = output_path.parent / f"{output_path.stem}_actionable.json"
        _export_actionable_insights(report, actionable_path, dataset_audit_path)


def _export_basic_json(report: Any, output_path: Path) -> None:
    """Export basic JSON format (simplified)."""
    data = report.to_dict()
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Basic JSON report saved to: {output_path}")


def _export_comprehensive_json(report: Any, output_path: Path) -> None:
    """Export comprehensive JSON format (full details for frontend)."""
    # Build comprehensive structure
    data = {
        "health": {
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
            },
        },
        "config": {
            "protected_attributes": report.protected_attributes,
            "test_configuration": {
                "total_samples": report.test_sample_count,
                "attributes_tested": len(report.protected_attributes),
            },
            "baseline_performance": report.baseline_metrics,
        },
        "results": {
            "overall": {
                "severity": report.overall_severity.value,
                "flip_rate": report.counterfactual_result.flip_rate if report.counterfactual_result else 0,
                "total_findings": len(report.findings),
            },
            "fairness_metrics": _organize_fairness_metrics(report),
            "counterfactual": {
                "flip_rate": report.counterfactual_result.flip_rate if report.counterfactual_result else 0,
                "total_flips": report.counterfactual_result.total_flips if report.counterfactual_result else 0,
                "total_comparisons": report.counterfactual_result.total_comparisons if report.counterfactual_result else 0,
                "flips_by_attribute": report.counterfactual_result.flips_by_attribute if report.counterfactual_result else {},
                "flip_rates_by_attribute": report.counterfactual_result.flip_rates_by_attribute if report.counterfactual_result else {},
            },
            "per_group_metrics": report.per_group_metrics,
        },
        "findings": {
            "findings_by_severity": _organize_findings_by_severity(report),
            "intersectional_findings": _format_intersectional_findings(report),
            "total_findings": len(report.findings),
        },
        "mitigation": {
            "total_options": len(report.mitigation_options),
            "by_category": _organize_mitigation_by_category(report),
            "recommended_order": ["post_processing", "pre_processing", "in_processing"],
        },
        "compliance": _generate_compliance_section(report),
        "validity": {
            "confidence_intervals": report.confidence_intervals,
            "sample_size": report.test_sample_count,
            "statistical_power": "adequate" if report.test_sample_count >= 100 else "limited",
            "notes": [
                "Confidence intervals provide range of plausible values for metrics",
                "Larger sample sizes provide more precise estimates",
                "P-values indicate statistical significance of observed differences",
            ],
        },
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Comprehensive JSON report saved to: {output_path}")


def _export_detailed_text(report: Any, output_path: Path) -> None:
    """Export detailed text format (human-readable)."""
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append("MODEL FAIRNESS AUDIT REPORT")
    lines.append("=" * 80)
    lines.append(f"Model: {report.model_name}")
    lines.append(f"Audit ID: {report.audit_id}")
    lines.append(f"Timestamp: {report.timestamp}")
    lines.append(f"Duration: {report.duration_seconds:.2f}s")
    lines.append("")
    
    # Overall Health
    lines.append("OVERALL HEALTH")
    lines.append("-" * 80)
    lines.append(f"Severity: {report.overall_severity.value}")
    lines.append(f"Test Samples: {report.test_sample_count:,}")
    lines.append(f"Protected Attributes: {', '.join(report.protected_attributes)}")
    lines.append("")
    
    critical_count = sum(1 for f in report.findings if f.severity.value == "CRITICAL")
    moderate_count = sum(1 for f in report.findings if f.severity.value == "MODERATE")
    low_count = sum(1 for f in report.findings if f.severity.value == "LOW")
    
    lines.append(f"Findings:")
    lines.append(f"  🔴 Critical: {critical_count}")
    lines.append(f"  🟡 Moderate: {moderate_count}")
    lines.append(f"  🟢 Low: {low_count}")
    lines.append("")
    
    # Baseline Performance
    lines.append("BASELINE PERFORMANCE")
    lines.append("-" * 80)
    for metric, value in report.baseline_metrics.items():
        if isinstance(value, float):
            lines.append(f"  {metric}: {value:.4f}")
        else:
            lines.append(f"  {metric}: {value}")
    lines.append("")
    
    # Fairness Metrics
    lines.append("FAIRNESS METRICS")
    lines.append("-" * 80)
    passed = sum(1 for m in report.scorecard.values() if m.passed)
    total = len(report.scorecard)
    lines.append(f"Pass Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    lines.append("")
    
    for metric_key, metric_result in report.scorecard.items():
        status = "✓ PASS" if metric_result.passed else "✗ FAIL"
        lines.append(f"{status} {metric_result.metric_name}")
        lines.append(f"    Value: {metric_result.value:.4f} (threshold: {metric_result.threshold})")
        if metric_result.privileged_group and metric_result.unprivileged_group:
            lines.append(f"    Groups: {metric_result.privileged_group} vs {metric_result.unprivileged_group}")
        if metric_result.p_value is not None:
            lines.append(f"    P-value: {metric_result.p_value:.6f}")
        lines.append("")
    
    # Counterfactual Results
    if report.counterfactual_result:
        lines.append("COUNTERFACTUAL TESTING")
        lines.append("-" * 80)
        cf = report.counterfactual_result
        lines.append(f"Flip Rate: {cf.flip_rate:.2%}")
        lines.append(f"Total Flips: {cf.total_flips:,} / {cf.total_comparisons:,}")
        lines.append("")
        lines.append("Flips by Attribute:")
        for attr, count in cf.flips_by_attribute.items():
            rate = cf.flip_rates_by_attribute.get(attr, 0)
            lines.append(f"  {attr}: {count:,} ({rate:.2%})")
        lines.append("")
    
    # Findings
    lines.append("DETAILED FINDINGS")
    lines.append("-" * 80)
    for finding in report.findings:
        lines.append(f"[{finding.severity.value}] {finding.title}")
        lines.append(f"  ID: {finding.finding_id}")
        lines.append(f"  Category: {finding.category}")
        lines.append(f"  Description: {finding.description}")
        lines.append(f"  Affected Groups: {', '.join(finding.affected_groups)}")
        lines.append(f"  Evidence: {finding.evidence}")
        lines.append("")
    
    # Mitigation Options
    lines.append("MITIGATION RECOMMENDATIONS")
    lines.append("-" * 80)
    for i, option in enumerate(report.mitigation_options, 1):
        retrain = " (requires retraining)" if option.requires_retraining else ""
        lines.append(f"{i}. {option.strategy_name} [{option.category}]{retrain}")
        lines.append(f"   {option.description}")
        lines.append(f"   Expected Impact: {option.expected_impact}")
        lines.append(f"   Complexity: {option.implementation_complexity}")
        if option.code_example:
            lines.append(f"   Code Example:")
            for line in option.code_example.split('\n'):
                lines.append(f"     {line}")
        lines.append("")
    
    # Footer
    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Detailed text report saved to: {output_path}")


def _export_summary_text(report: Any, output_path: Path) -> None:
    """Export summary text format (brief overview)."""
    lines = []
    
    lines.append("MODEL AUDIT SUMMARY")
    lines.append("=" * 60)
    lines.append(f"Model: {report.model_name}")
    lines.append(f"Severity: {report.overall_severity.value}")
    lines.append(f"Test Samples: {report.test_sample_count:,}")
    lines.append("")
    
    critical_count = sum(1 for f in report.findings if f.severity.value == "CRITICAL")
    moderate_count = sum(1 for f in report.findings if f.severity.value == "MODERATE")
    low_count = sum(1 for f in report.findings if f.severity.value == "LOW")
    
    lines.append(f"Findings: {critical_count} critical, {moderate_count} moderate, {low_count} low")
    
    passed = sum(1 for m in report.scorecard.values() if m.passed)
    total = len(report.scorecard)
    lines.append(f"Metrics: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    if report.counterfactual_result:
        lines.append(f"Flip Rate: {report.counterfactual_result.flip_rate:.2%}")
    
    lines.append("")
    lines.append("Top Issues:")
    for finding in report.findings[:3]:
        lines.append(f"  - [{finding.severity.value}] {finding.title}")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Summary text report saved to: {output_path}")


def _export_actionable_insights(
    report: Any,
    output_path: Path,
    dataset_audit_path: Optional[Path] = None
) -> None:
    """Export actionable insights JSON (for business users and frontend)."""
    from .interpreter import interpret_model_audit_report
    
    # First export comprehensive JSON to temp location
    temp_comprehensive = output_path.parent / f"_temp_comprehensive_{output_path.stem}.json"
    _export_comprehensive_json(report, temp_comprehensive)
    
    # Generate actionable insights
    insights = interpret_model_audit_report(temp_comprehensive, dataset_audit_path)
    
    # Clean up temp file
    temp_comprehensive.unlink()
    
    # Save actionable insights
    with open(output_path, 'w') as f:
        json.dump(insights, f, indent=2)
    
    print(f"✓ Actionable insights saved to: {output_path}")


# Helper functions

def _organize_fairness_metrics(report: Any) -> dict:
    """Organize fairness metrics by protected attribute."""
    metrics_by_attr = {}
    
    for metric_key, metric_result in report.scorecard.items():
        # Extract attribute from key (e.g., "gender_Female_vs_Male_demographic_parity")
        parts = metric_key.split('_')
        if len(parts) >= 1:
            attr = parts[0]
            
            if attr not in metrics_by_attr:
                metrics_by_attr[attr] = []
            
            metrics_by_attr[attr].append({
                "metric_name": metric_result.metric_name,
                "value": metric_result.value,
                "threshold": metric_result.threshold,
                "passed": metric_result.passed,
                "p_value": metric_result.p_value,
                "privileged_group": metric_result.privileged_group,
                "unprivileged_group": metric_result.unprivileged_group,
            })
    
    return metrics_by_attr


def _organize_findings_by_severity(report: Any) -> dict:
    """Organize findings by severity level."""
    findings_by_severity = {
        "CRITICAL": [],
        "MODERATE": [],
        "LOW": [],
    }
    
    for finding in report.findings:
        severity = finding.severity.value
        if severity in findings_by_severity:
            findings_by_severity[severity].append({
                "id": finding.finding_id,
                "category": finding.category,
                "title": finding.title,
                "description": finding.description,
                "affected_groups": finding.affected_groups,
                "evidence": finding.evidence,
            })
    
    return findings_by_severity


def _format_intersectional_findings(report: Any) -> list:
    """Format intersectional findings."""
    formatted = []
    
    for finding in report.intersectional_findings:
        formatted.append({
            "attributes": finding.attributes,
            "values": finding.attribute_values,
            "metric": finding.metric_name,
            "value": finding.metric_value,
            "baseline": finding.baseline_value,
            "superadditive": finding.is_superadditive,
            "severity": finding.severity.value,
            "sample_count": finding.sample_count,
        })
    
    return formatted


def _organize_mitigation_by_category(report: Any) -> dict:
    """Organize mitigation options by category."""
    by_category = {
        "post_processing": [],
        "pre_processing": [],
        "in_processing": [],
    }
    
    for option in report.mitigation_options:
        category = option.category
        if category in by_category:
            by_category[category].append({
                "name": option.strategy_name,
                "description": option.description,
                "expected_impact": option.expected_impact,
                "complexity": option.implementation_complexity,
                "requires_retraining": option.requires_retraining,
                "parameters": option.parameters,
            })
    
    return by_category


def _generate_compliance_section(report: Any) -> dict:
    """Generate compliance section with EEOC analysis."""
    # Check for EEOC violations (DIR < 0.80)
    violations = []
    warnings = []
    
    for metric_key, metric_result in report.scorecard.items():
        if "disparate_impact" in metric_key.lower():
            if metric_result.value < 0.80:
                violations.append({
                    "metric": metric_result.metric_name,
                    "value": metric_result.value,
                    "threshold": 0.80,
                    "groups": f"{metric_result.unprivileged_group} vs {metric_result.privileged_group}",
                    "message": f"Disparate Impact Ratio {metric_result.value:.2%} below EEOC 80% threshold",
                })
            elif metric_result.value < 0.85:
                warnings.append({
                    "metric": metric_result.metric_name,
                    "value": metric_result.value,
                    "threshold": 0.80,
                    "groups": f"{metric_result.unprivileged_group} vs {metric_result.privileged_group}",
                    "message": f"Disparate Impact Ratio {metric_result.value:.2%} close to EEOC threshold",
                })
    
    return {
        "overall_status": "NON-COMPLIANT" if violations else "COMPLIANT",
        "eeoc_80_percent_rule": {
            "description": "EEOC Uniform Guidelines on Employee Selection Procedures (1978)",
            "threshold": 0.80,
            "reference": "https://www.eeoc.gov/laws/guidance/questions-and-answers-clarify-and-provide-common-interpretation-uniform-guidelines",
        },
        "violations": violations,
        "warnings": warnings,
        "compliant": len(violations) == 0,
    }
