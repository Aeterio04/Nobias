"""
Data models for model audit results and findings.
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Optional, Literal
from enum import Enum
from datetime import datetime
import json
import hashlib


class Severity(str, Enum):
    """Severity levels for audit findings."""
    CRITICAL = "CRITICAL"
    MODERATE = "MODERATE"
    LOW = "LOW"
    CLEAR = "CLEAR"


class ModelType(str, Enum):
    """Supported model types."""
    CLASSIFIER_BINARY = "binary_classifier"
    CLASSIFIER_MULTICLASS = "multiclass_classifier"
    REGRESSOR = "regressor"


@dataclass
class ModelIntegrity:
    """
    Tamper-evident audit record for legal defensibility.
    
    Creates SHA-256 hashes of all audit components to prove
    the audit was not altered after completion.
    
    Required for: EU AI Act Art. 12, NIST AI RMF, ISO/IEC 42001
    """
    audit_hash: str = ""
    model_hash: str = ""
    predictions_hash: str = ""
    config_hash: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @staticmethod
    def compute_hash(data: Any) -> str:
        """Compute SHA-256 hash of data."""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()


@dataclass
class ModelFingerprint:
    """
    Exact model state for reproducibility.
    
    Ensures audit is tied to a specific model version.
    
    Required for: ISO/IEC 42001 reproducibility, EU AI Act Art. 9
    """
    model_name: str = ""
    model_type: str = ""
    feature_count: int = 0
    model_hash: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class MetricResult:
    """Result for a single fairness metric."""
    metric_name: str
    value: float
    threshold: float
    passed: bool
    p_value: Optional[float] = None
    privileged_group: Optional[str] = None
    unprivileged_group: Optional[str] = None
    description: str = ""
    
    def __repr__(self) -> str:
        status = "✓ PASS" if self.passed else "✗ FAIL"
        return f"{self.metric_name}: {self.value:.4f} (threshold: {self.threshold}) [{status}]"


@dataclass
class CounterfactualPair:
    """A single counterfactual example showing prediction flip."""
    original_index: int
    original_prediction: Any
    original_confidence: Optional[float]
    counterfactual_prediction: Any
    counterfactual_confidence: Optional[float]
    flipped_attribute: str
    original_value: Any
    counterfactual_value: Any
    confidence_delta: Optional[float] = None
    
    def __repr__(self) -> str:
        return (f"Sample {self.original_index}: {self.flipped_attribute} "
                f"{self.original_value}→{self.counterfactual_value} | "
                f"Prediction: {self.original_prediction}→{self.counterfactual_prediction}")


@dataclass
class CounterfactualResult:
    """Results from counterfactual flip testing."""
    total_samples: int
    total_comparisons: int
    total_flips: int
    flip_rate: float
    mean_absolute_score_difference: Optional[float] = None
    flips_by_attribute: dict[str, int] = field(default_factory=dict)
    flip_rates_by_attribute: dict[str, float] = field(default_factory=dict)
    top_flip_examples: list[CounterfactualPair] = field(default_factory=list)
    
    def __repr__(self) -> str:
        return (f"Counterfactual Flips: {self.total_flips}/{self.total_comparisons} "
                f"({self.flip_rate:.2%})")


@dataclass
class ProxyFeature:
    """A feature identified as a potential proxy for protected attributes."""
    feature_name: str
    protected_attribute: str
    correlation: float
    shap_importance_rank: int
    mean_shap_value: float
    risk_level: Severity
    
    def __repr__(self) -> str:
        return (f"{self.feature_name} → {self.protected_attribute} "
                f"(corr={self.correlation:.3f}, SHAP rank={self.shap_importance_rank})")


@dataclass
class IntersectionalFinding:
    """Finding for intersectional bias analysis."""
    attributes: list[str]
    attribute_values: dict[str, Any]
    metric_name: str
    metric_value: float
    baseline_value: float
    is_superadditive: bool
    severity: Severity
    sample_count: int
    
    def __repr__(self) -> str:
        attrs_str = " & ".join(f"{k}={v}" for k, v in self.attribute_values.items())
        return (f"[{attrs_str}] {self.metric_name}={self.metric_value:.4f} "
                f"(baseline={self.baseline_value:.4f}) [{self.severity}]")


@dataclass
class ModelFinding:
    """A single audit finding with evidence and recommendations."""
    finding_id: str
    severity: Severity
    category: str  # "group_fairness", "counterfactual", "proxy", "intersectional"
    title: str
    description: str
    evidence: dict[str, Any]
    affected_groups: list[str]
    metric_results: list[MetricResult] = field(default_factory=list)
    
    def __repr__(self) -> str:
        return f"[{self.severity}] {self.title}"


@dataclass
class MitigationOption:
    """A mitigation strategy with implementation details."""
    strategy_name: str
    category: Literal["post_processing", "pre_processing", "in_processing"]
    description: str
    expected_impact: str
    implementation_complexity: Literal["low", "medium", "high"]
    requires_retraining: bool
    parameters: dict[str, Any] = field(default_factory=dict)
    code_example: Optional[str] = None
    
    def __repr__(self) -> str:
        retrain = " (requires retraining)" if self.requires_retraining else ""
        return f"{self.strategy_name} [{self.category}]{retrain}"


@dataclass
class SHAPAnalysis:
    """Results from SHAP explainability analysis."""
    feature_importance: dict[str, float]  # feature → mean |SHAP|
    proxy_features: list[ProxyFeature]
    group_divergence: dict[str, dict[str, int]]  # feature → {group: rank}
    plots_available: list[str]  # ["summary", "per_group", "waterfall"]
    
    def get_top_features(self, n: int = 10) -> list[tuple[str, float]]:
        """Get top N most important features."""
        return sorted(self.feature_importance.items(), 
                     key=lambda x: abs(x[1]), 
                     reverse=True)[:n]


@dataclass
class ModelAuditConfig:
    """Configuration for model audit."""
    protected_attributes: list[str]
    target_column: str
    positive_value: Any = 1
    run_shap: bool = True
    run_intersectional: bool = True
    counterfactual_sample_limit: Optional[int] = None
    shap_sample_limit: Optional[int] = 1000
    fairness_thresholds: dict[str, float] = field(default_factory=lambda: {
        "demographic_parity": 0.10,
        "equalized_odds": 0.10,
        "disparate_impact": 0.80,
        "predictive_parity": 0.05,
        "calibration": 0.05,
    })
    severity_thresholds: dict[str, dict] = field(default_factory=lambda: {
        "CRITICAL": {"dpd": 0.20, "dir": 0.60, "flip_rate": 0.15},
        "MODERATE": {"dpd": 0.10, "dir": 0.80, "flip_rate": 0.05},
        "LOW": {"dpd": 0.05, "dir": 0.90, "flip_rate": 0.02},
    })


@dataclass
class ModelAuditReport:
    """Complete audit report for a model."""
    # Core identification
    audit_id: str = ""
    model_name: str = ""
    model_type: ModelType = ModelType.CLASSIFIER_BINARY
    test_sample_count: int = 0
    protected_attributes: list[str] = field(default_factory=list)
    
    # Severity
    overall_severity: Severity = Severity.CLEAR
    
    # Core results
    scorecard: dict[str, MetricResult] = field(default_factory=dict)
    counterfactual_result: Optional[CounterfactualResult] = None
    findings: list[ModelFinding] = field(default_factory=list)
    mitigation_options: list[MitigationOption] = field(default_factory=list)
    
    # Optional analyses
    intersectional_findings: list[IntersectionalFinding] = field(default_factory=list)
    shap_analysis: Optional[SHAPAnalysis] = None
    
    # Metadata
    baseline_metrics: dict[str, float] = field(default_factory=dict)
    per_group_metrics: dict[str, dict[str, float]] = field(default_factory=dict)
    
    # FairSight Compliance
    audit_integrity: Optional[ModelIntegrity] = None
    model_fingerprint: Optional[ModelFingerprint] = None
    confidence_intervals: dict[str, dict] = field(default_factory=dict)
    
    # Timing
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "model_name": self.model_name,
            "model_type": self.model_type.value,
            "test_sample_count": self.test_sample_count,
            "protected_attributes": self.protected_attributes,
            "overall_severity": self.overall_severity.value,
            "scorecard": {k: {
                "value": v.value,
                "threshold": v.threshold,
                "passed": v.passed,
                "p_value": v.p_value,
            } for k, v in self.scorecard.items()},
            "counterfactual_summary": {
                "flip_rate": self.counterfactual_result.flip_rate,
                "total_flips": self.counterfactual_result.total_flips,
                "flips_by_attribute": self.counterfactual_result.flips_by_attribute,
            },
            "findings_count": {
                "CRITICAL": sum(1 for f in self.findings if f.severity == Severity.CRITICAL),
                "MODERATE": sum(1 for f in self.findings if f.severity == Severity.MODERATE),
                "LOW": sum(1 for f in self.findings if f.severity == Severity.LOW),
            },
            "mitigation_options_count": len(self.mitigation_options),
            "intersectional_findings_count": len(self.intersectional_findings),
            "shap_available": self.shap_analysis is not None,
        }
    
    def export(
        self,
        output_path: str,
        format: str = "json",
        include_actionable_insights: bool = True,
        dataset_audit_path: Optional[str] = None
    ) -> None:
        """
        Export report to file.
        
        Args:
            output_path: Path to save report
            format: Output format ("json", "comprehensive", "text", "summary", "actionable")
            include_actionable_insights: Whether to also generate actionable insights JSON
            dataset_audit_path: Optional path to dataset audit for bias amplification analysis
        """
        from .report_export import export_report
        export_report(self, output_path, format, include_actionable_insights, dataset_audit_path)
    
    def get_critical_findings(self) -> list[ModelFinding]:
        """Get all critical severity findings."""
        return [f for f in self.findings if f.severity == Severity.CRITICAL]
    
    def get_findings_by_category(self, category: str) -> list[ModelFinding]:
        """Get findings by category."""
        return [f for f in self.findings if f.category == category]
    
    def __repr__(self) -> str:
        critical = sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
        moderate = sum(1 for f in self.findings if f.severity == Severity.MODERATE)
        low = sum(1 for f in self.findings if f.severity == Severity.LOW)
        
        return (f"ModelAuditReport: {self.model_name}\n"
                f"  Overall Severity: {self.overall_severity.value}\n"
                f"  Findings: {critical} critical, {moderate} moderate, {low} low\n"
                f"  Counterfactual Flip Rate: {self.counterfactual_result.flip_rate:.2%}\n"
                f"  Mitigation Options: {len(self.mitigation_options)}")
