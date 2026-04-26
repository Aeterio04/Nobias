"""
Model Audit Module - Fairness auditing for trained ML models.

This module provides tools to audit trained machine learning models for bias and fairness issues.
It supports counterfactual testing, group fairness metrics, SHAP explainability, and mitigation strategies.
"""

from .models import (
    ModelAuditReport,
    ModelAuditConfig,
    ModelFinding,
    MetricResult,
    CounterfactualResult,
    CounterfactualPair,
    ProxyFeature,
    IntersectionalFinding,
    MitigationOption,
    SHAPAnalysis,
    Severity,
    ModelType,
)

from .loading import (
    load_model,
    load_test_data,
    prepare_model_and_data,
    ModelLoadError,
    DataLoadError,
)

from .api import (
    audit_model,
    quick_audit,
)

from .report import (
    export_report,
    generate_text_summary,
)

# New modular report system
try:
    from .report_new import (
        export_json,
        export_string,
        export_pdf,
        generate_comprehensive_report,
    )
    _new_reports_available = True
except ImportError:
    _new_reports_available = False

__all__ = [
    # Main API
    "audit_model",
    "quick_audit",
    
    # Configuration
    "ModelAuditConfig",
    
    # Report and results
    "ModelAuditReport",
    "ModelFinding",
    "MetricResult",
    "CounterfactualResult",
    "CounterfactualPair",
    "ProxyFeature",
    "IntersectionalFinding",
    "MitigationOption",
    "SHAPAnalysis",
    
    # Enums
    "Severity",
    "ModelType",
    
    # Loading utilities
    "load_model",
    "load_test_data",
    "prepare_model_and_data",
    "ModelLoadError",
    "DataLoadError",
    
    # Report utilities (old)
    "export_report",
    "generate_text_summary",
]

# Add new report functions if available
if _new_reports_available:
    __all__.extend([
        "export_json",
        "export_string",
        "export_pdf",
        "generate_comprehensive_report",
    ])

__version__ = "0.1.0"
