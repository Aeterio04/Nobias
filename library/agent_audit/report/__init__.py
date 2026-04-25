"""
agent_audit.report — Comprehensive Report Generation & Export
==============================================================

Modular report generation system with multiple export formats.

Main exports:
    - generate_comprehensive_report(): Build full report dict
    - export_json(): Export to JSON format
    - export_string(): Export to human-readable text
    - export_pdf(): Export to PDF with charts
    - compare_audits(): Compare before/after reports

Internal modules:
    - sections: Report section builders (health, config, results, etc.)
    - formatters: Output formatters (JSON, string, PDF)
    - utils: Helper functions (badges, wrapping, etc.)
"""

from agent_audit.report.sections import (
    build_health_section,
    build_config_section,
    build_results_section,
    build_interpretation_section,
    build_raw_data_section,
)
from agent_audit.report.formatters import (
    export_json,
    export_string,
    export_pdf,
)
from agent_audit.report.generator import (
    generate_comprehensive_report,
    build_report_summary,
)
from agent_audit.interpreter.remediation import compare_audits


__all__ = [
    # Main functions
    "generate_comprehensive_report",
    "build_report_summary",
    "compare_audits",
    
    # Export functions
    "export_json",
    "export_string",
    "export_pdf",
    
    # Section builders (for advanced users)
    "build_health_section",
    "build_config_section",
    "build_results_section",
    "build_interpretation_section",
    "build_raw_data_section",
]
