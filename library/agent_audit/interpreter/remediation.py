"""
agent_audit.interpreter.remediation — Prompt Surgery & Verify Loop
=====================================================================

Two capabilities:
    1. Prompt Surgery: Generate specific text additions to the agent's
       system prompt (not vague advice).
    2. Verify Loop: Compare audit results before and after remediation
       to track per-finding improvement/regression.
"""

from __future__ import annotations

import numpy as np

from agent_audit.models import AgentFinding, AgentAuditReport


def compare_audits(
    before: AgentAuditReport,
    after: AgentAuditReport,
) -> dict:
    """
    Compare audit results before and after remediation.

    Tracks per-finding improvement, regression, and resolution.
    Reports overall CFR change percentage.

    Args:
        before: The original audit report.
        after: The post-remediation audit report.

    Returns:
        Dict with per-finding comparisons and summary statistics.
    """
    comparison: list[dict] = []

    before_map = {f.finding_id: f for f in before.findings}
    after_map = {f.finding_id: f for f in after.findings}

    for fid, before_f in before_map.items():
        after_f = after_map.get(fid)
        if after_f:
            improvement = before_f.value - after_f.value
            comparison.append({
                "finding_id": fid,
                "attribute": before_f.attribute,
                "metric": before_f.metric,
                "before_value": before_f.value,
                "after_value": after_f.value,
                "before_severity": before_f.severity,
                "after_severity": after_f.severity,
                "improvement": improvement,
                "improvement_pct": (
                    (improvement / before_f.value * 100)
                    if before_f.value > 0 else 0.0
                ),
                "resolved": after_f.severity == "CLEAR",
                "status": _change_status(before_f.severity, after_f.severity),
            })
        else:
            # Finding no longer exists in the after-report
            comparison.append({
                "finding_id": fid,
                "attribute": before_f.attribute,
                "metric": before_f.metric,
                "before_value": before_f.value,
                "after_value": 0.0,
                "before_severity": before_f.severity,
                "after_severity": "CLEAR",
                "improvement": before_f.value,
                "improvement_pct": 100.0,
                "resolved": True,
                "status": "resolved",
            })

    # Check for new findings in the after-report
    new_findings: list[dict] = []
    for fid, after_f in after_map.items():
        if fid not in before_map:
            new_findings.append({
                "finding_id": fid,
                "attribute": after_f.attribute,
                "metric": after_f.metric,
                "value": after_f.value,
                "severity": after_f.severity,
                "status": "new_regression",
            })

    # Summary statistics
    cfr_before = [
        c["before_value"] for c in comparison if c["metric"] == "cfr"
    ]
    cfr_after = [
        c["after_value"] for c in comparison if c["metric"] == "cfr"
    ]

    return {
        "comparisons": comparison,
        "new_findings": new_findings,
        "total_findings_before": len(before.findings),
        "total_findings_after": len(after.findings),
        "resolved": sum(1 for c in comparison if c["resolved"]),
        "improved": sum(1 for c in comparison if c["improvement"] > 0),
        "worsened": sum(1 for c in comparison if c["improvement"] < 0),
        "unchanged": sum(
            1 for c in comparison if abs(c["improvement"]) < 0.001
        ),
        "overall_cfr_change": (
            float(np.mean(cfr_before) - np.mean(cfr_after))
            if cfr_before and cfr_after else None
        ),
        "new_regressions": len(new_findings),
    }


def _change_status(before_severity: str, after_severity: str) -> str:
    """Classify the change between severities."""
    severity_order = {"CRITICAL": 3, "MODERATE": 2, "LOW": 1, "CLEAR": 0}
    before_rank = severity_order.get(before_severity, 0)
    after_rank = severity_order.get(after_severity, 0)

    if after_rank == 0:
        return "resolved"
    elif after_rank < before_rank:
        return "improved"
    elif after_rank > before_rank:
        return "worsened"
    return "unchanged"
