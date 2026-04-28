from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from datetime import datetime
import json
import hashlib


@dataclass
class DatasetFinding:
    """Represents a single bias finding in the dataset."""
    check: str
    severity: str
    message: str
    metric: str
    value: float
    threshold: float
    confidence: float


@dataclass
class ProxyFeature:
    """Represents a feature that may be a proxy for a protected attribute."""
    feature: str
    protected: str
    method: str
    score: float
    nmi: float


@dataclass
class Remediation:
    """Represents a remediation strategy with estimated impact."""
    strategy: str
    estimated_dir_after: float
    estimated_spd_after: float
    description: Optional[str] = None


@dataclass
class DatasetIntegrity:
    """
    Tamper-evident audit record for legal defensibility.
    
    Creates SHA-256 hashes of all audit components to prove
    the audit was not altered after completion.
    
    Required for: EU AI Act Art. 12, NIST AI RMF, ISO/IEC 42001
    """
    audit_hash: str = ""
    data_hash: str = ""
    findings_hash: str = ""
    config_hash: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @staticmethod
    def compute_hash(data: Any) -> str:
        """Compute SHA-256 hash of data."""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()


@dataclass
class DatasetAuditReport:
    """
    Complete dataset bias audit report.
    
    Contains all findings, statistical analyses, and remediation suggestions
    for a dataset audit.
    
    Attributes:
        audit_id: Unique identifier for this audit run
        dataset_name: Name of the audited dataset
        row_count: Number of rows in the dataset
        column_count: Number of columns in the dataset
        protected_attributes: List of protected attributes analyzed
        target_column: Name of the target/label column
        positive_value: Value representing positive class
        
        overall_severity: Worst severity across all findings (CRITICAL/MODERATE/LOW/CLEAR)
        
        findings: List of individual bias findings
        representation: Representation analysis results
        label_rates: Label distribution by protected attributes
        proxy_features: Detected proxy features
        missing_data_matrix: Missing data patterns
        intersectional_disparities: Intersectional bias findings
        kl_divergences: Distribution divergence metrics
        remediation_suggestions: Recommended remediation strategies
        
        # FairSight Compliance Fields
        audit_integrity: Tamper-evident audit record
        confidence_intervals: Statistical confidence intervals
        
        # Metadata
        duration_seconds: Wall-clock time for the audit
        timestamp: ISO timestamp of audit completion
        logs: Execution logs
    """
    # Core identification
    audit_id: str = ""
    dataset_name: str = ""
    row_count: int = 0
    column_count: int = 0
    protected_attributes: list[str] = field(default_factory=list)
    target_column: str = ""
    positive_value: Any = None
    
    # Severity
    overall_severity: str = "CLEAR"
    
    # Analysis results
    findings: list[DatasetFinding] = field(default_factory=list)
    representation: dict[str, Any] = field(default_factory=dict)
    label_rates: dict[str, Any] = field(default_factory=dict)
    proxy_features: list[ProxyFeature] = field(default_factory=list)
    missing_data_matrix: dict[str, Any] = field(default_factory=dict)
    intersectional_disparities: list[dict] = field(default_factory=list)
    kl_divergences: dict[str, float] = field(default_factory=dict)
    remediation_suggestions: list[Remediation] = field(default_factory=list)
    
    # FairSight Compliance
    audit_integrity: Optional[DatasetIntegrity] = None
    confidence_intervals: dict[str, dict] = field(default_factory=dict)
    
    # Metadata
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    logs: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize the full report to a dictionary."""
        return asdict(self)
    
    def export(self, path: str, format: str = "json") -> None:
        """
        Export the report to disk.
        
        Args:
            path: Output file path
            format: Format — "json" | "text" | "pdf"
        """
        if format == "json":
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
        elif format == "text":
            with open(path, "w") as f:
                f.write(self.to_text())
        elif format == "pdf":
            # Use the advanced report system
            from .report import generate_report
            from .report.formatters import PDFFormatter
            report_data = generate_report(self)
            PDFFormatter.save(report_data, path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def to_text(self) -> str:
        """Generate human-readable text summary."""
        lines = []
        lines.append("=" * 80)
        lines.append("DATASET BIAS AUDIT REPORT")
        lines.append("=" * 80)
        lines.append(f"\nAudit ID: {self.audit_id}")
        lines.append(f"Dataset: {self.dataset_name}")
        lines.append(f"Timestamp: {self.timestamp}")
        lines.append(f"Duration: {self.duration_seconds:.2f}s")
        lines.append(f"\nDataset Size: {self.row_count:,} rows × {self.column_count} columns")
        lines.append(f"Protected Attributes: {', '.join(self.protected_attributes)}")
        lines.append(f"Target Column: {self.target_column}")
        lines.append(f"\nOverall Severity: {self.overall_severity}")
        
        # Findings summary
        critical = sum(1 for f in self.findings if f.severity == "CRITICAL")
        moderate = sum(1 for f in self.findings if f.severity == "MODERATE")
        low = sum(1 for f in self.findings if f.severity == "LOW")
        
        lines.append(f"\nFindings Summary:")
        lines.append(f"  Critical: {critical}")
        lines.append(f"  Moderate: {moderate}")
        lines.append(f"  Low: {low}")
        lines.append(f"  Total: {len(self.findings)}")
        
        # Detailed findings
        if self.findings:
            lines.append(f"\n{'=' * 80}")
            lines.append("DETAILED FINDINGS")
            lines.append("=" * 80)
            for i, finding in enumerate(self.findings, 1):
                lines.append(f"\n[{finding.severity}] Finding #{i}: {finding.check}")
                lines.append(f"  {finding.message}")
                lines.append(f"  Metric: {finding.metric} = {finding.value:.4f} (threshold: {finding.threshold})")
        
        # Proxy features
        if self.proxy_features:
            lines.append(f"\n{'=' * 80}")
            lines.append("PROXY FEATURES DETECTED")
            lines.append("=" * 80)
            for proxy in self.proxy_features:
                lines.append(f"  {proxy.feature} → {proxy.protected} (score: {proxy.score:.3f})")
        
        # Remediation suggestions
        if self.remediation_suggestions:
            lines.append(f"\n{'=' * 80}")
            lines.append("REMEDIATION SUGGESTIONS")
            lines.append("=" * 80)
            for i, remedy in enumerate(self.remediation_suggestions, 1):
                lines.append(f"\n{i}. {remedy.strategy}")
                if remedy.description:
                    lines.append(f"   {remedy.description}")
                lines.append(f"   Expected DIR: {remedy.estimated_dir_after:.3f}")
                lines.append(f"   Expected SPD: {remedy.estimated_spd_after:.3f}")
        
        lines.append(f"\n{'=' * 80}")
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def get_critical_findings(self) -> list[DatasetFinding]:
        """Get all critical severity findings."""
        return [f for f in self.findings if f.severity == "CRITICAL"]
    
    def get_findings_by_check(self, check: str) -> list[DatasetFinding]:
        """Get findings by check type."""
        return [f for f in self.findings if f.check == check]
    
    def __repr__(self) -> str:
        critical = sum(1 for f in self.findings if f.severity == "CRITICAL")
        moderate = sum(1 for f in self.findings if f.severity == "MODERATE")
        low = sum(1 for f in self.findings if f.severity == "LOW")
        
        return (f"DatasetAuditReport: {self.dataset_name}\n"
                f"  Overall Severity: {self.overall_severity}\n"
                f"  Findings: {critical} critical, {moderate} moderate, {low} low\n"
                f"  Proxy Features: {len(self.proxy_features)}\n"
                f"  Remediation Options: {len(self.remediation_suggestions)}")
