"""
agent_audit.report.formatters.string_formatter — String Export
===============================================================

Export reports to human-readable text format (non-LLM).
"""

from __future__ import annotations

from agent_audit.models import AgentAuditReport
from agent_audit.report.generator import build_report_summary
from agent_audit.report.sections import (
    build_health_section,
    build_config_section,
    build_results_section,
    build_interpretation_section,
    build_raw_data_section,
)
from agent_audit.report.utils import wrap_text, severity_badge


def export_string(report: AgentAuditReport, detailed: bool = True) -> str:
    """
    Export report to human-readable string format (non-LLM).
    
    Args:
        report: The AgentAuditReport to export.
        detailed: If True, includes all sections. If False, summary only.
    
    Returns:
        Formatted string report.
    """
    if not detailed:
        return build_report_summary(report)
    
    lines = []
    
    # Header
    lines.append("═" * 80)
    lines.append("AGENT BIAS AUDIT REPORT")
    lines.append("═" * 80)
    lines.append("")
    
    # Section 1: Health & Metadata
    health = build_health_section(report)
    lines.append("SECTION 1: HEALTH & METADATA")
    lines.append("─" * 80)
    lines.append(f"Audit ID:        {health['audit_id']}")
    lines.append(f"Timestamp:       {health['timestamp']}")
    lines.append(f"Mode:            {health['mode']}")
    lines.append(f"Duration:        {health['duration_formatted']}")
    lines.append("")
    lines.append(f"API Calls:")
    lines.append(f"  Total:         {health['api_calls']['total']}")
    lines.append(f"  Per Persona:   {health['api_calls']['per_persona']}")
    lines.append(f"  Calls/Second:  {health['api_calls']['calls_per_second']}")
    lines.append("")
    lines.append(f"Estimated Tokens:")
    lines.append(f"  Total:         {health['estimated_tokens']['total']:,}")
    lines.append(f"  Input:         {health['estimated_tokens']['input_tokens']:,}")
    lines.append(f"  Output:        {health['estimated_tokens']['output_tokens']:,}")
    lines.append("")
    lines.append(f"Performance:")
    lines.append(f"  Avg Latency:   {health['performance']['avg_call_latency_ms']}ms")
    lines.append(f"  Personas:      {health['performance']['personas_tested']}")
    lines.append(f"  Findings:      {health['performance']['findings_generated']}")
    lines.append("")
    
    # Section 2: Configuration
    config = build_config_section(report)
    lines.append("SECTION 2: TEST CONFIGURATION")
    lines.append("─" * 80)
    lines.append(f"Protected Attributes: {', '.join(config['protected_attributes'])}")
    lines.append("")
    lines.append(f"Persona Generation:")
    lines.append(f"  Total Personas:    {config['persona_generation']['total_personas']}")
    lines.append(f"  Unique Names:      {config['persona_generation']['unique_names']}")
    lines.append(f"  Context Primes:    {config['persona_generation']['context_primes']}")
    lines.append("")
    lines.append(f"Test Variants:")
    for variant, count in config['test_variants'].items():
        lines.append(f"  {variant:20s} {count}")
    lines.append("")
    
    # Section 3: Results & Statistics
    results = build_results_section(report)
    lines.append("SECTION 3: RESULTS & STATISTICS")
    lines.append("─" * 80)
    lines.append(f"Overall Severity:  {results['overall']['severity_badge']}")
    lines.append(f"Overall CFR:       {results['overall']['overall_cfr_percent']}")
    lines.append(f"Benchmark Range:   {results['overall']['benchmark_range']['min_percent']} - {results['overall']['benchmark_range']['max_percent']}")
    lines.append(f"Total Findings:    {results['overall']['total_findings']}")
    lines.append("")
    
    lines.append("Severity Breakdown:")
    for sev, count in results['severity_breakdown'].items():
        if count > 0:
            badge = severity_badge(sev)
            lines.append(f"  {badge:20s} {count}")
    lines.append("")
    
    lines.append("Findings by Attribute:")
    for attr, findings in results['findings_by_attribute'].items():
        lines.append(f"  {attr}:")
        for finding in findings:
            lines.append(f"    [{finding['severity']:8s}] {finding['metric']:20s} = {finding['value']:.4f} (p={finding['p_value']:.4f})")
    lines.append("")
    
    lines.append("Decision Statistics:")
    lines.append(f"  Positive:      {results['decision_statistics']['distribution']['positive']} ({results['decision_statistics']['distribution_percent']['positive']})")
    lines.append(f"  Negative:      {results['decision_statistics']['distribution']['negative']} ({results['decision_statistics']['distribution_percent']['negative']})")
    lines.append(f"  Ambiguous:     {results['decision_statistics']['distribution']['ambiguous']} ({results['decision_statistics']['distribution_percent']['ambiguous']})")
    lines.append(f"  Positive Rate: {results['decision_statistics']['positive_rate']:.1%}")
    lines.append("")
    
    if results['score_statistics']:
        lines.append("Score Statistics:")
        lines.append(f"  Mean:  {results['score_statistics']['mean']:.4f}")
        lines.append(f"  Min:   {results['score_statistics']['min']:.4f}")
        lines.append(f"  Max:   {results['score_statistics']['max']:.4f}")
        lines.append(f"  Std:   {results['score_statistics']['std']:.4f}")
        lines.append("")
    
    lines.append("Variance Statistics:")
    lines.append(f"  Mean Variance:      {results['variance_statistics']['mean_variance']:.4f}")
    lines.append(f"  Max Variance:       {results['variance_statistics']['max_variance']:.4f}")
    lines.append(f"  High Variance (>0.3): {results['variance_statistics']['high_variance_count']}")
    lines.append("")
    
    # Section 4: Interpretation & Remediation
    interp = build_interpretation_section(report)
    lines.append("SECTION 4: INTERPRETATION & REMEDIATION")
    lines.append("─" * 80)
    
    if interp['interpretation']['overall_assessment']:
        lines.append("Overall Assessment:")
        lines.append(wrap_text(interp['interpretation']['overall_assessment'], 78, "  "))
        lines.append("")
    
    if interp['prompt_suggestions']:
        lines.append(f"Prompt Suggestions ({interp['suggestions_count']}):")
        for i, suggestion in enumerate(interp['prompt_suggestions'], 1):
            lines.append(f"  {i}. [{suggestion['confidence'].upper()}] ({suggestion['word_count']} words)")
            lines.append(wrap_text(suggestion['suggestion_text'], 74, "     "))
            if suggestion['rationale']:
                lines.append(f"     Rationale: {suggestion['rationale']}")
            lines.append("")
    
    if interp['stress_test']:
        st = interp['stress_test']
        lines.append("Stress Test Results:")
        lines.append(f"  Rounds Completed:   {st['rounds_completed']}")
        lines.append(f"  Mutations Tested:   {st['total_mutations_tested']}")
        lines.append(f"  Max CFR Achieved:   {st['max_cfr_percent']}")
        lines.append(f"  Conclusion:         {st['conclusion']}")
        lines.append("")
    
    # Section 5: Raw Data Summary
    raw = build_raw_data_section(report)
    lines.append("SECTION 5: RAW DATA SUMMARY")
    lines.append("─" * 80)
    lines.append(f"Total Personas:      {raw['total_personas']}")
    lines.append(f"CAFFE Test Cases:    {raw['total_caffe_cases']}")
    lines.append("")
    lines.append("(Full raw data available in JSON export)")
    lines.append("")
    
    # Footer
    lines.append("═" * 80)
    lines.append("END OF REPORT")
    lines.append("═" * 80)
    
    return "\n".join(lines)


__all__ = ["export_string"]
