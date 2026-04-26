"""
model_audit.report.formatters.string_formatter — String Export
===============================================================

Export reports to human-readable text format.
"""

from __future__ import annotations

import sys
from ...models import ModelAuditReport
from ..generator import build_report_summary
from ..sections import (
    build_health_section,
    build_config_section,
    build_results_section,
    build_findings_section,
    build_mitigation_section,
    build_compliance_section,
    build_validity_section,
)


def severity_badge(severity: str, use_emoji: bool = True) -> str:
    """Get severity badge with optional emoji."""
    if not use_emoji:
        return f"[{severity}]"
    
    badges = {
        "CRITICAL": "[CRITICAL]",
        "MODERATE": "[MODERATE]",
        "LOW": "[LOW]",
        "CLEAR": "[CLEAR]",
    }
    return badges.get(severity, f"[{severity}]")


def export_string(report: ModelAuditReport, detailed: bool = True) -> str:
    """
    Export report to human-readable string format.
    
    Args:
        report: The ModelAuditReport to export.
        detailed: If True, includes all sections. If False, summary only.
    
    Returns:
        Formatted string report.
    """
    # Detect if we're on Windows with limited console encoding
    use_emoji = sys.platform != 'win32' or sys.stdout.encoding.lower() in ['utf-8', 'utf8']
    
    if not detailed:
        return build_report_summary(report)
    
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append("MODEL FAIRNESS AUDIT REPORT")
    lines.append("=" * 80)
    lines.append("")
    
    # Section 1: Health & Metadata
    health = build_health_section(report)
    lines.append("SECTION 1: HEALTH & METADATA")
    lines.append("-" * 80)
    lines.append(f"Model Name:      {health['model_info']['model_name']}")
    lines.append(f"Model Type:      {health['model_info']['model_type']}")
    lines.append(f"Test Samples:    {health['model_info']['test_sample_count']:,}")
    lines.append("")
    lines.append(f"Overall Health:")
    lines.append(f"  Severity:      {severity_badge(health['overall_health']['severity'], use_emoji)}")
    lines.append(f"  Critical:      {health['overall_health']['critical_findings']}")
    lines.append(f"  Moderate:      {health['overall_health']['moderate_findings']}")
    lines.append(f"  Low:           {health['overall_health']['low_findings']}")
    lines.append("")
    lines.append(f"Metrics Summary:")
    lines.append(f"  Total:         {health['metrics_summary']['total_metrics']}")
    lines.append(f"  Passed:        {health['metrics_summary']['passed_metrics']}")
    lines.append(f"  Failed:        {health['metrics_summary']['failed_metrics']}")
    lines.append(f"  Pass Rate:     {health['metrics_summary']['pass_rate']:.1%}")
    lines.append("")
    
    # Section 2: Configuration
    config = build_config_section(report)
    lines.append("SECTION 2: TEST CONFIGURATION")
    lines.append("-" * 80)
    lines.append(f"Protected Attributes: {', '.join(config['protected_attributes'])}")
    lines.append("")
    lines.append(f"Test Configuration:")
    lines.append(f"  Total Samples:     {config['test_configuration']['total_samples']:,}")
    lines.append(f"  Attributes Tested: {config['test_configuration']['attributes_tested']}")
    lines.append("")
    if config['baseline_performance']:
        lines.append(f"Baseline Performance:")
        for metric, value in list(config['baseline_performance'].items())[:5]:
            lines.append(f"  {metric:20s} {value:.4f}")
    lines.append("")
    
    # Section 3: Results & Statistics
    results = build_results_section(report)
    lines.append("SECTION 3: RESULTS & STATISTICS")
    lines.append("-" * 80)
    lines.append(f"Overall Severity:  {severity_badge(results['overall']['severity'], use_emoji)}")
    lines.append(f"Flip Rate:         {results['overall']['flip_rate']:.2%}")
    lines.append(f"Total Findings:    {results['overall']['total_findings']}")
    lines.append("")
    
    lines.append("Fairness Metrics by Attribute:")
    for attr, metrics in results['fairness_metrics'].items():
        lines.append(f"  {attr}:")
        for metric in metrics:
            status = "[PASS]" if metric['passed'] else "[FAIL]"
            lines.append(f"    {status} {metric['metric_name']:30s} = {metric['value']:.4f} (threshold: {metric['threshold']:.4f})")
            if metric['p_value']:
                lines.append(f"         p-value: {metric['p_value']:.4f}")
    lines.append("")
    
    lines.append("Counterfactual Testing:")
    lines.append(f"  Flip Rate:         {results['counterfactual']['flip_rate']:.2%}")
    lines.append(f"  Total Flips:       {results['counterfactual']['total_flips']:,} / {results['counterfactual']['total_comparisons']:,}")
    lines.append(f"  Flips by Attribute:")
    for attr, count in results['counterfactual']['flips_by_attribute'].items():
        rate = results['counterfactual']['flip_rates_by_attribute'][attr]
        lines.append(f"    {attr:20s} {count:,} ({rate:.2%})")
    lines.append("")
    
    # Section 4: Findings
    findings = build_findings_section(report)
    lines.append("SECTION 4: FINDINGS & ISSUES")
    lines.append("-" * 80)
    
    for severity_level in ["CRITICAL", "MODERATE", "LOW"]:
        findings_list = findings['findings_by_severity'][severity_level]
        if findings_list:
            lines.append(f"{severity_badge(severity_level, use_emoji)} Findings ({len(findings_list)}):")
            for finding in findings_list:
                lines.append(f"  [{finding['id']}] {finding['title']}")
                lines.append(f"      {finding['description']}")
                lines.append(f"      Affected: {', '.join(finding['affected_groups'])}")
                lines.append("")
    
    if findings['intersectional_findings']:
        lines.append("Intersectional Findings:")
        for finding in findings['intersectional_findings'][:5]:
            attrs_str = " & ".join(f"{k}={v}" for k, v in finding['values'].items())
            lines.append(f"  [{finding['severity']}] {attrs_str}")
            lines.append(f"      {finding['metric']}: {finding['value']:.2%} (expected: {finding['baseline']:.2%})")
            lines.append(f"      Sample size: {finding['sample_count']:,}")
        if len(findings['intersectional_findings']) > 5:
            lines.append(f"  ... and {len(findings['intersectional_findings']) - 5} more")
    lines.append("")
    
    # Section 5: Mitigation
    mitigation = build_mitigation_section(report)
    lines.append("SECTION 5: MITIGATION & REMEDIATION")
    lines.append("-" * 80)
    lines.append(f"Total Options: {mitigation['total_options']}")
    lines.append("")
    
    for category in mitigation['recommended_order']:
        options = mitigation['by_category'][category]
        if options:
            lines.append(f"{category.replace('_', ' ').title()} Strategies:")
            for i, option in enumerate(options, 1):
                retrain = " (requires retraining)" if option['requires_retraining'] else ""
                lines.append(f"  {i}. {option['name']}{retrain}")
                lines.append(f"     {option['description']}")
                lines.append(f"     Impact: {option['expected_impact']}")
                lines.append(f"     Complexity: {option['complexity']}")
                lines.append("")
    
    # Section 6: Legal Compliance
    compliance = build_compliance_section(report)
    lines.append("SECTION 6: LEGAL COMPLIANCE (EEOC)")
    lines.append("-" * 80)
    lines.append(f"Overall Status: {compliance['overall_status']}")
    lines.append("")
    
    if compliance['violations']:
        lines.append("[WARNING] LEGAL VIOLATIONS DETECTED:")
        for v in compliance['violations']:
            lines.append(f"  - {v['message']}")
            lines.append(f"    Groups: {v['groups']}")
        lines.append("")
    
    if compliance['warnings']:
        lines.append("[WARNING] Warnings:")
        for w in compliance['warnings']:
            lines.append(f"  - {w['message']}")
        lines.append("")
    
    lines.append(f"EEOC 80% Rule: {compliance['eeoc_80_percent_rule']['description']}")
    lines.append(f"Reference: {compliance['eeoc_80_percent_rule']['reference']}")
    lines.append("")
    
    # Section 7: Statistical Validity
    validity = build_validity_section(report)
    lines.append("SECTION 7: STATISTICAL VALIDITY")
    lines.append("-" * 80)
    lines.append(f"Sample Size:       {validity['sample_size']:,}")
    lines.append(f"Statistical Power: {validity['statistical_power']}")
    lines.append("")
    
    if validity['confidence_intervals']:
        lines.append("Confidence Intervals (95%):")
        for metric, ci in list(validity['confidence_intervals'].items())[:5]:
            lines.append(f"  {metric}:")
            lines.append(f"    Point Estimate: {ci['point_estimate']:.4f}")
            lines.append(f"    95% CI: [{ci['lower_bound']:.4f}, {ci['upper_bound']:.4f}]")
        if len(validity['confidence_intervals']) > 5:
            lines.append(f"  ... and {len(validity['confidence_intervals']) - 5} more")
    lines.append("")
    
    lines.append("Notes:")
    for note in validity['notes']:
        lines.append(f"  - {note}")
    lines.append("")
    
    # Footer
    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    return "\n".join(lines)


__all__ = ["export_string"]
