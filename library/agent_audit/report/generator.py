"""
agent_audit.report.generator — Main Report Generator
=====================================================

Core report generation logic that combines all sections.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from agent_audit.models import AgentAuditReport
from agent_audit.report.sections import (
    build_health_section,
    build_config_section,
    build_results_section,
    build_interpretation_section,
    build_raw_data_section,
    build_compliance_section,
    build_validity_section,
)
from agent_audit.report.utils import severity_badge


def generate_comprehensive_report(report: AgentAuditReport) -> dict[str, Any]:
    """
    Generate a comprehensive report with all sections.
    
    Combines all section builders into a single structured report.
    Includes FairSight compliance sections.
    
    Args:
        report: The AgentAuditReport to process.
    
    Returns:
        Dict with all report sections.
    """
    return {
        "report_version": "1.1",  # Updated for FairSight
        "generated_at": datetime.utcnow().isoformat(),
        "section_1_health": build_health_section(report),
        "section_2_configuration": build_config_section(report),
        "section_3_results": build_results_section(report),
        "section_4_interpretation": build_interpretation_section(report),
        "section_5_raw_data": build_raw_data_section(report),
        "section_6_compliance": build_compliance_section(report),
        "section_7_validity": build_validity_section(report),
    }


def build_report_summary(report: AgentAuditReport) -> str:
    """
    Generate a brief human-readable summary.
    
    Legacy function for quick summaries.
    
    Args:
        report: The complete audit report.
    
    Returns:
        Multi-line summary string.
    """
    lines = [
        f"═══ Agent Bias Audit Report ═══",
        f"Audit ID:    {report.audit_id}",
        f"Mode:        {report.mode}",
        f"Duration:    {report.duration_seconds:.1f}s",
        f"API Calls:   {report.total_calls}",
        f"",
        f"Overall Severity: {severity_badge(report.overall_severity)}",
        f"Overall CFR:      {report.overall_cfr:.1%}",
        f"Benchmark Range:  {report.benchmark_range[0]:.1%} – {report.benchmark_range[1]:.1%}",
        f"",
    ]

    if report.findings:
        lines.append(f"═══ Findings ({len(report.findings)}) ═══")
        for f in report.findings:
            lines.append(
                f"  [{f.severity:8s}] {f.attribute}: {f.metric} = {f.value:.4f} "
                f"(p = {f.p_value:.4f})"
            )
            lines.append(f"            {f.benchmark_context}")
            lines.append("")
    else:
        lines.append("No significant bias findings detected.")

    if report.interpretation and report.interpretation.overall_assessment:
        lines.append(f"═══ Assessment ═══")
        lines.append(report.interpretation.overall_assessment)
        lines.append("")

    if report.prompt_suggestions:
        lines.append(f"═══ Remediation Suggestions ═══")
        for i, s in enumerate(report.prompt_suggestions, 1):
            lines.append(f"  {i}. [{s.confidence}] {s.suggestion_text[:100]}...")
        lines.append("")

    if report.stress_test_results:
        st = report.stress_test_results
        lines.append(f"═══ Stress Test ═══")
        lines.append(f"  Rounds:    {st.rounds_completed}")
        lines.append(f"  Mutations: {st.total_mutations_tested}")
        lines.append(f"  Max CFR:   {st.max_cfr_achieved:.1%}")
        lines.append(f"  Result:    {st.conclusion}")

    return "\n".join(lines)


__all__ = [
    "generate_comprehensive_report",
    "build_report_summary",
]
