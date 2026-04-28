"""
model_audit.report.formatters.json_formatter — JSON Export
===========================================================

Export reports to JSON format with comprehensive or basic mode.
"""

from __future__ import annotations

import json
import numpy as np
from pathlib import Path
from typing import Any

from ...models import ModelAuditReport
from ..generator import generate_comprehensive_report


def convert_to_serializable(obj: Any) -> Any:
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def export_json(
    report: ModelAuditReport,
    output_path: str | Path,
    comprehensive: bool = True,
    indent: int = 2,
) -> None:
    """
    Export report to JSON format.
    
    Args:
        report: The ModelAuditReport to export.
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
    
    # Convert numpy types
    data = convert_to_serializable(data)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)
    
    print(f"Report exported to: {output_path}")


__all__ = ["export_json"]
