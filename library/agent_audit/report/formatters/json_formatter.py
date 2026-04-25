"""
agent_audit.report.formatters.json_formatter — JSON Export
===========================================================

Export reports to JSON format with comprehensive or basic mode.
"""

from __future__ import annotations

import json
from pathlib import Path

from agent_audit.models import AgentAuditReport
from agent_audit.report.generator import generate_comprehensive_report


def export_json(
    report: AgentAuditReport,
    output_path: str | Path,
    comprehensive: bool = True,
    indent: int = 2,
) -> None:
    """
    Export report to JSON format.
    
    Args:
        report: The AgentAuditReport to export.
        output_path: Path to save the JSON file.
        comprehensive: If True, includes all sections. If False, basic report only.
        indent: JSON indentation level (default 2).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if comprehensive:
        data = generate_comprehensive_report(report)
    else:
        data = report.to_dict()
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=indent, default=str)


__all__ = ["export_json"]
