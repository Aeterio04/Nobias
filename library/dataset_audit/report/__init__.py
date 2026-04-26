"""
Advanced report generation system for dataset audits.

This module provides a modular, extensible report generation system
with support for multiple output formats (JSON, text, PDF) and
comprehensive sections including legal compliance and statistical validity.
"""

from .generator import generate_report
from .sections import (
    HealthSection,
    ConfigSection,
    RepresentationSection,
    ProxyFeaturesSection,
    FindingsSection,
    RemediationSection,
    ComplianceSection,
    ValiditySection,
)
from .formatters import (
    JSONFormatter,
    StringFormatter,
    PDFFormatter,
)

__all__ = [
    'generate_report',
    'HealthSection',
    'ConfigSection',
    'RepresentationSection',
    'ProxyFeaturesSection',
    'FindingsSection',
    'RemediationSection',
    'ComplianceSection',
    'ValiditySection',
    'JSONFormatter',
    'StringFormatter',
    'PDFFormatter',
]
