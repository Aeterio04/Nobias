"""
model_audit.report — Comprehensive Report Generation & Export
==============================================================

Modular report generation system with multiple export formats.

Main exports:
    - generate_comprehensive_report(): Build full report dict
    - export_json(): Export to JSON format
    - export_string(): Export to human-readable text
    - export_pdf(): Export to PDF with charts
"""

from .formatters.json_formatter import export_json
from .formatters.string_formatter import export_string
from .formatters.pdf_formatter import export_pdf
from .generator import (
    generate_comprehensive_report,
    build_report_summary,
)
from .sections import (
    build_health_section,
    build_config_section,
    build_results_section,
    build_findings_section,
    build_mitigation_section,
)


__all__ = [
    # Main functions
    "generate_comprehensive_report",
    "build_report_summary",
    
    # Export functions
    "export_json",
    "export_string",
    "export_pdf",
    
    # Section builders (for advanced users)
    "build_health_section",
    "build_config_section",
    "build_results_section",
    "build_findings_section",
    "build_mitigation_section",
]
