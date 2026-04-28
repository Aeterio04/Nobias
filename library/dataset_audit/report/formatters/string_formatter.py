"""
String/text formatter for dataset audit reports.
"""

from typing import Dict, Any
from pathlib import Path


class StringFormatter:
    """Format dataset audit reports as human-readable text."""
    
    @staticmethod
    def format(report_data: Dict[str, Any], mode: str = 'detailed') -> str:
        """
        Format report data as text string.
        
        Args:
            report_data: Report data dictionary from generator
            mode: 'detailed' or 'summary'
        
        Returns:
            Formatted text string
        """
        if mode == 'summary':
            return StringFormatter._format_summary(report_data)
        else:
            return StringFormatter._format_detailed(report_data)
    
    @staticmethod
    def _format_summary(report_data: Dict[str, Any]) -> str:
        """Format a brief summary."""
        health = report_data.get('health', {})
        config = report_data.get('config', {})
        compliance = report_data.get('compliance', {})
        
        lines = []
        lines.append(f"Dataset: {config.get('dataset_name', 'Unknown')}")
        lines.append(f"Severity: {health.get('overall_severity', 'UNKNOWN')}")
        lines.append(f"Health Score: {health.get('health_score', 0)}/100")
        lines.append(f"Findings: {health.get('critical_findings', 0)} critical, {health.get('moderate_findings', 0)} moderate")
        lines.append(f"Proxy Features: {health.get('proxy_features_detected', 0)}")
        lines.append(f"Compliance: {compliance.get('overall_compliance_status', 'UNKNOWN')}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def _format_detailed(report_data: Dict[str, Any]) -> str:
        """Format a detailed report."""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("DATASET FAIRNESS AUDIT REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Health Section
        if 'health' in report_data:
            lines.extend(StringFormatter._format_health_section(report_data['health']))
            lines.append("")
        
        # Config Section
        if 'config' in report_data:
            lines.extend(StringFormatter._format_config_section(report_data['config']))
            lines.append("")
        
        # Representation Section
        if 'representation' in report_data:
            lines.extend(StringFormatter._format_representation_section(report_data['representation']))
            lines.append("")
        
        # Proxy Features Section
        if 'proxy_features' in report_data:
            lines.extend(StringFormatter._format_proxy_section(report_data['proxy_features']))
            lines.append("")
        
        # Findings Section
        if 'findings' in report_data:
            lines.extend(StringFormatter._format_findings_section(report_data['findings']))
            lines.append("")
        
        # Remediation Section
        if 'remediation' in report_data:
            lines.extend(StringFormatter._format_remediation_section(report_data['remediation']))
            lines.append("")
        
        # Compliance Section
        if 'compliance' in report_data:
            lines.extend(StringFormatter._format_compliance_section(report_data['compliance']))
            lines.append("")
        
        # Validity Section
        if 'validity' in report_data:
            lines.extend(StringFormatter._format_validity_section(report_data['validity']))
            lines.append("")
        
        # Footer
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return '\n'.join(lines)
    
    @staticmethod
    def _format_health_section(health: Dict) -> list:
        """Format health section."""
        lines = []
        lines.append("[HEALTH OVERVIEW]")
        lines.append("-" * 80)
        lines.append(f"Overall Severity: {health.get('overall_severity', 'UNKNOWN')}")
        lines.append(f"Health Score: {health.get('health_score', 0)}/100")
        lines.append(f"Total Findings: {health.get('total_findings', 0)}")
        lines.append(f"  - Critical: {health.get('critical_findings', 0)}")
        lines.append(f"  - Moderate: {health.get('moderate_findings', 0)}")
        lines.append(f"  - Low: {health.get('low_findings', 0)}")
        lines.append(f"Proxy Features Detected: {health.get('proxy_features_detected', 0)}")
        return lines
    
    @staticmethod
    def _format_config_section(config: Dict) -> list:
        """Format config section."""
        lines = []
        lines.append("[DATASET CONFIGURATION]")
        lines.append("-" * 80)
        lines.append(f"Dataset Name: {config.get('dataset_name', 'Unknown')}")
        lines.append(f"Rows: {config.get('row_count', 0):,}")
        lines.append(f"Columns: {config.get('column_count', 0)}")
        lines.append(f"Audit Timestamp: {config.get('audit_timestamp', 'Unknown')}")
        return lines
    
    @staticmethod
    def _format_representation_section(representation: Dict) -> list:
        """Format representation section."""
        lines = []
        lines.append("[DEMOGRAPHIC REPRESENTATION]")
        lines.append("-" * 80)
        
        group_dists = representation.get('group_distributions', {})
        for attr, groups in group_dists.items():
            lines.append(f"\n{attr}:")
            for group, stats in groups.items():
                lines.append(f"  {group}: {stats['count']:,} samples ({stats['percentage']:.1f}%)")
        
        # Label rates
        label_rates = representation.get('label_rates', {})
        if label_rates:
            lines.append("\nLabel Rates by Group:")
            for attr, groups in label_rates.items():
                lines.append(f"\n{attr}:")
                for group, stats in groups.items():
                    pos_rate = stats.get('positive_rate', 0)
                    lines.append(f"  {group}: {pos_rate:.2%} positive rate")
        
        return lines
    
    @staticmethod
    def _format_proxy_section(proxy_features: Dict) -> list:
        """Format proxy features section."""
        lines = []
        lines.append("[PROXY FEATURES]")
        lines.append("-" * 80)
        lines.append(f"Total Detected: {proxy_features.get('total_proxy_features', 0)}")
        lines.append(f"  - High Risk: {proxy_features.get('high_risk_proxies', 0)}")
        lines.append(f"  - Medium Risk: {proxy_features.get('medium_risk_proxies', 0)}")
        lines.append(f"  - Low Risk: {proxy_features.get('low_risk_proxies', 0)}")
        
        proxies = proxy_features.get('proxy_features', [])
        if proxies:
            lines.append("\nTop Proxy Features:")
            for i, proxy in enumerate(proxies[:10], 1):  # Top 10
                lines.append(f"\n{i}. '{proxy['feature']}' -> '{proxy['protected_attribute']}'")
                lines.append(f"   Risk Level: {proxy['risk_level']}")
                lines.append(f"   Correlation: {proxy['correlation_score']:.4f}")
                lines.append(f"   NMI: {proxy['normalized_mutual_info']:.4f}")
                lines.append(f"   Method: {proxy['detection_method']}")
        
        return lines
    
    @staticmethod
    def _format_findings_section(findings: Dict) -> list:
        """Format findings section."""
        lines = []
        lines.append("[BIAS FINDINGS]")
        lines.append("-" * 80)
        lines.append(f"Total Findings: {findings.get('total_findings', 0)}")
        lines.append(f"\nSummary: {findings.get('summary', 'No summary available')}")
        
        findings_by_sev = findings.get('findings_by_severity', {})
        
        # Critical findings
        critical = findings_by_sev.get('CRITICAL', [])
        if critical:
            lines.append("\n[CRITICAL FINDINGS]")
            for i, finding in enumerate(critical, 1):
                lines.append(f"\n{i}. [{finding['check_type']}] {finding['message']}")
                lines.append(f"   Metric: {finding['metric_name']} = {finding['metric_value']:.4f}")
                lines.append(f"   Threshold: {finding['threshold']:.4f}")
                lines.append(f"   Confidence: {finding['confidence']:.2%}")
        
        # Moderate findings
        moderate = findings_by_sev.get('MODERATE', [])
        if moderate:
            lines.append("\n[MODERATE FINDINGS]")
            for i, finding in enumerate(moderate, 1):
                lines.append(f"\n{i}. [{finding['check_type']}] {finding['message']}")
                lines.append(f"   Metric: {finding['metric_name']} = {finding['metric_value']:.4f}")
                lines.append(f"   Threshold: {finding['threshold']:.4f}")
        
        # Low findings
        low = findings_by_sev.get('LOW', [])
        if low:
            lines.append(f"\n[LOW SEVERITY FINDINGS] ({len(low)} findings)")
        
        return lines
    
    @staticmethod
    def _format_remediation_section(remediation: Dict) -> list:
        """Format remediation section."""
        lines = []
        lines.append("[REMEDIATION STRATEGIES]")
        lines.append("-" * 80)
        lines.append(f"Total Strategies: {remediation.get('total_strategies', 0)}")
        
        strategies = remediation.get('recommended_strategies', [])
        priority = remediation.get('priority_order', [])
        
        if strategies:
            lines.append("\nRecommended Actions (Priority Order):")
            for i, strategy_name in enumerate(priority, 1):
                # Find the strategy details
                strategy = next((s for s in strategies if s['strategy_name'] == strategy_name), None)
                if strategy:
                    lines.append(f"\n{i}. {strategy['strategy_name']}")
                    if strategy.get('description'):
                        lines.append(f"   Description: {strategy['description']}")
                    lines.append(f"   Expected Impact: {strategy['expected_impact']}")
                    lines.append(f"   Complexity: {strategy['implementation_complexity']}")
                    lines.append(f"   Estimated DIR After: {strategy['estimated_dir_after']:.4f}")
                    lines.append(f"   Estimated SPD After: {strategy['estimated_spd_after']:.4f}")
        
        return lines
    
    @staticmethod
    def _format_compliance_section(compliance: Dict) -> list:
        """Format compliance section."""
        lines = []
        lines.append("[LEGAL COMPLIANCE]")
        lines.append("-" * 80)
        lines.append(f"Overall Status: {compliance.get('overall_compliance_status', 'UNKNOWN')}")
        
        # EEOC 80% rule
        eeoc = compliance.get('eeoc_80_rule', {})
        lines.append(f"\nEEOC 80% Rule (4/5ths): {'PASS' if eeoc.get('compliant', False) else 'FAIL'}")
        lines.append(f"Violations: {eeoc.get('total_violations', 0)}")
        
        violations = eeoc.get('violations', [])
        if violations:
            lines.append("\nViolation Details:")
            for v in violations[:5]:  # Top 5
                lines.append(f"  - {v['attribute']} / {v['group']}: {v['ratio']:.2%} ratio")
        
        # Recommendations
        recommendations = compliance.get('recommendations', [])
        if recommendations:
            lines.append("\nCompliance Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
        
        return lines
    
    @staticmethod
    def _format_validity_section(validity: Dict) -> list:
        """Format validity section."""
        lines = []
        lines.append("[STATISTICAL VALIDITY]")
        lines.append("-" * 80)
        lines.append(f"Average Confidence: {validity.get('average_confidence', 0):.2%}")
        lines.append(f"Sample Size: {validity.get('sample_size', 0):,}")
        lines.append(f"Sample Adequacy: {validity.get('sample_adequacy', 'UNKNOWN')}")
        lines.append(f"Data Completeness: {validity.get('data_completeness', 0):.2%}")
        lines.append(f"Statistical Power: {validity.get('statistical_power', 'UNKNOWN')}")
        
        limitations = validity.get('limitations', [])
        if limitations:
            lines.append("\nLimitations:")
            for i, limitation in enumerate(limitations, 1):
                lines.append(f"{i}. {limitation}")
        
        return lines
    
    @staticmethod
    def save(report_data: Dict[str, Any], filepath: str, mode: str = 'detailed') -> None:
        """
        Save report as text file.
        
        Args:
            report_data: Report data dictionary from generator
            filepath: Output file path
            mode: 'detailed' or 'summary'
        """
        text_str = StringFormatter.format(report_data, mode)
        
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text_str)
        
        print(f"Report exported to: {filepath}")
