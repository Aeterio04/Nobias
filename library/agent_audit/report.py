"""
agent_audit.report — Report Generation & Export
==================================================

Compiles all findings, persona results, interpretations, and
suggestions into the final AgentAuditReport object.

Export formats:
    - JSON: Full structured report
    - CAFFE: CAFFE-compliant test suite JSON
    - PDF: Human-readable report with charts (future)

Also provides compare_audits() for before/after remediation tracking.
"""

from __future__ import annotations

from agent_audit.models import AgentAuditReport
from agent_audit.interpreter.remediation import compare_audits


def build_report_summary(report: AgentAuditReport) -> str:
    """
    Generate a human-readable summary of the audit report.

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
        f"Overall Severity: {_severity_badge(report.overall_severity)}",
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


def _severity_badge(severity: str) -> str:
    """Return a formatted severity badge."""
    badges = {
        "CRITICAL": "🔴 CRITICAL",
        "MODERATE": "🟡 MODERATE",
        "LOW":      "🟢 LOW",
        "CLEAR":    "✅ CLEAR",
    }
    return badges.get(severity, severity)


__all__ = ["compare_audits", "build_report_summary"]
