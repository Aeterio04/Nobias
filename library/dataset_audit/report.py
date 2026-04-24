from dataclasses import dataclass, asdict
from typing import List, Dict
import json
from pathlib import Path
from .models import DatasetFinding, ProxyFeature, Remediation


@dataclass
class DatasetAuditReport:
    """Complete audit report for a dataset."""
    dataset_name: str
    row_count: int
    column_count: int
    overall_severity: str
    findings: List[DatasetFinding]
    representation: Dict[str, Dict]
    label_rates: Dict[str, Dict]
    proxy_features: List[ProxyFeature]
    missing_data_matrix: Dict[str, Dict]
    intersectional_disparities: List[Dict]
    kl_divergences: Dict[str, Dict]
    remediation_suggestions: List[Remediation]
    logs: List[str]
    
    def to_dict(self) -> dict:
        """Convert report to dictionary."""
        return {
            'dataset_name': self.dataset_name,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'overall_severity': self.overall_severity,
            'findings': [asdict(f) for f in self.findings],
            'representation': self.representation,
            'label_rates': self.label_rates,
            'proxy_features': [asdict(p) for p in self.proxy_features],
            'missing_data_matrix': self.missing_data_matrix,
            'intersectional_disparities': self.intersectional_disparities,
            'kl_divergences': self.kl_divergences,
            'remediation_suggestions': [asdict(r) for r in self.remediation_suggestions],
            'logs': self.logs
        }
    
    def export(self, path: str) -> None:
        """
        Export report to file.
        
        Args:
            path: Output file path (.json or .pdf)
            
        Raises:
            NotImplementedError: For PDF export
        """
        path_obj = Path(path)
        
        if path_obj.suffix.lower() == '.json':
            with open(path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
        elif path_obj.suffix.lower() == '.pdf':
            raise NotImplementedError("PDF export not yet implemented")
        else:
            raise ValueError(f"Unsupported export format: {path_obj.suffix}")
    
    def to_text(self) -> str:
        """Generate human-readable text report."""
        lines = []
        lines.append("=" * 60)
        lines.append("NoBias Dataset Audit Report")
        lines.append("=" * 60)
        lines.append(f"Dataset: {self.dataset_name}")
        lines.append(f"Rows: {self.row_count:,} | Columns: {self.column_count}")
        lines.append(f"Overall Severity: {self.overall_severity}")
        lines.append("")
        
        # Group findings by severity
        critical = [f for f in self.findings if f.severity == 'CRITICAL']
        moderate = [f for f in self.findings if f.severity == 'MODERATE']
        low = [f for f in self.findings if f.severity == 'LOW']
        
        if critical:
            lines.append("🔴 CRITICAL FINDINGS")
            lines.append("-" * 60)
            for finding in critical:
                lines.append(f"[{finding.check.upper()}] {finding.message}")
                lines.append(f"  → {finding.metric}: {finding.value:.3f} (threshold: {finding.threshold:.3f})")
                lines.append(f"  → Confidence: {finding.confidence*100:.0f}%")
                lines.append("")
        
        if moderate:
            lines.append("🟠 MODERATE FINDINGS")
            lines.append("-" * 60)
            for finding in moderate:
                lines.append(f"[{finding.check.upper()}] {finding.message}")
                lines.append(f"  → {finding.metric}: {finding.value:.3f} (threshold: {finding.threshold:.3f})")
                lines.append(f"  → Confidence: {finding.confidence*100:.0f}%")
                lines.append("")
        
        if low:
            lines.append("🟡 LOW SEVERITY FINDINGS")
            lines.append("-" * 60)
            for finding in low:
                lines.append(f"[{finding.check.upper()}] {finding.message}")
                lines.append(f"  → {finding.metric}: {finding.value:.3f} (threshold: {finding.threshold:.3f})")
                lines.append("")
        
        if not self.findings:
            lines.append("✅ CLEAR - No significant bias detected")
            lines.append("")
        
        # Proxy features
        if self.proxy_features:
            lines.append("⚠️  PROXY FEATURES DETECTED")
            lines.append("-" * 60)
            for proxy in self.proxy_features[:5]:  # Top 5
                lines.append(f"'{proxy.feature}' → '{proxy.protected}'")
                lines.append(f"  → Method: {proxy.method} | Score: {proxy.score:.3f} | NMI: {proxy.nmi:.3f}")
            if len(self.proxy_features) > 5:
                lines.append(f"  ... and {len(self.proxy_features) - 5} more")
            lines.append("")
        
        # Remediation suggestions
        if self.remediation_suggestions:
            lines.append("💡 REMEDIATION SUGGESTIONS")
            lines.append("-" * 60)
            for rem in self.remediation_suggestions:
                lines.append(f"Strategy: {rem.strategy}")
                if rem.description:
                    lines.append(f"  → {rem.description}")
                lines.append(f"  → Estimated DIR after: {rem.estimated_dir_after:.3f}")
                lines.append(f"  → Estimated SPD after: {rem.estimated_spd_after:.3f}")
                lines.append("")
        
        # Representation summary
        if self.representation:
            lines.append("📊 REPRESENTATION SUMMARY")
            lines.append("-" * 60)
            for attr, groups in self.representation.items():
                lines.append(f"{attr}:")
                for group, stats in groups.items():
                    lines.append(f"  {group}: {stats['count']:,} samples ({stats['percentage']:.1f}%)")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
