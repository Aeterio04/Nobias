"""
Report sections for dataset audit reports.

Each section is responsible for extracting and formatting a specific
aspect of the audit results.
"""

from typing import Dict, Any, List
from datetime import datetime


class HealthSection:
    """Overall health summary of the dataset audit."""
    
    @staticmethod
    def generate(report) -> Dict[str, Any]:
        """Generate health section from audit report."""
        critical_count = sum(1 for f in report.findings if f.severity == 'CRITICAL')
        moderate_count = sum(1 for f in report.findings if f.severity == 'MODERATE')
        low_count = sum(1 for f in report.findings if f.severity == 'LOW')
        
        # Calculate health score (0-100)
        total_findings = len(report.findings)
        if total_findings == 0:
            health_score = 100
        else:
            # Weight: critical=10, moderate=5, low=1
            weighted_score = (critical_count * 10 + moderate_count * 5 + low_count * 1)
            max_possible = total_findings * 10
            health_score = max(0, 100 - (weighted_score / max_possible * 100))
        
        return {
            'overall_severity': report.overall_severity,
            'health_score': round(health_score, 1),
            'total_findings': total_findings,
            'critical_findings': critical_count,
            'moderate_findings': moderate_count,
            'low_findings': low_count,
            'proxy_features_detected': len(report.proxy_features),
            'timestamp': datetime.now().isoformat(),
        }


class ConfigSection:
    """Configuration and metadata about the dataset."""
    
    @staticmethod
    def generate(report) -> Dict[str, Any]:
        """Generate config section from audit report."""
        return {
            'dataset_name': report.dataset_name,
            'row_count': report.row_count,
            'column_count': report.column_count,
            'audit_timestamp': datetime.now().isoformat(),
        }


class RepresentationSection:
    """Demographic representation analysis."""
    
    @staticmethod
    def generate(report) -> Dict[str, Any]:
        """Generate representation section from audit report."""
        return {
            'group_distributions': report.representation,
            'label_rates': report.label_rates,
            'kl_divergences': report.kl_divergences,
            'intersectional_disparities': report.intersectional_disparities,
            'missing_data_matrix': report.missing_data_matrix,
        }


class ProxyFeaturesSection:
    """Proxy feature detection results."""
    
    @staticmethod
    def generate(report) -> Dict[str, Any]:
        """Generate proxy features section from audit report."""
        proxy_list = []
        for proxy in report.proxy_features:
            proxy_list.append({
                'feature': proxy.feature,
                'protected_attribute': proxy.protected,
                'detection_method': proxy.method,
                'correlation_score': round(proxy.score, 4),
                'normalized_mutual_info': round(proxy.nmi, 4),
                'risk_level': _classify_proxy_risk(proxy.score, proxy.nmi),
            })
        
        # Sort by risk
        proxy_list.sort(key=lambda x: x['correlation_score'], reverse=True)
        
        return {
            'total_proxy_features': len(proxy_list),
            'high_risk_proxies': sum(1 for p in proxy_list if p['risk_level'] == 'HIGH'),
            'medium_risk_proxies': sum(1 for p in proxy_list if p['risk_level'] == 'MEDIUM'),
            'low_risk_proxies': sum(1 for p in proxy_list if p['risk_level'] == 'LOW'),
            'proxy_features': proxy_list,
        }


class FindingsSection:
    """Detailed bias findings."""
    
    @staticmethod
    def generate(report) -> Dict[str, Any]:
        """Generate findings section from audit report."""
        findings_by_severity = {
            'CRITICAL': [],
            'MODERATE': [],
            'LOW': [],
        }
        
        for finding in report.findings:
            findings_by_severity[finding.severity].append({
                'check_type': finding.check,
                'message': finding.message,
                'metric_name': finding.metric,
                'metric_value': round(finding.value, 4),
                'threshold': round(finding.threshold, 4),
                'confidence': round(finding.confidence, 4),
                'severity': finding.severity,
            })
        
        return {
            'total_findings': len(report.findings),
            'findings_by_severity': findings_by_severity,
            'summary': _generate_findings_summary(report.findings),
        }


class RemediationSection:
    """Remediation strategies and recommendations."""
    
    @staticmethod
    def generate(report) -> Dict[str, Any]:
        """Generate remediation section from audit report."""
        strategies = []
        for rem in report.remediation_suggestions:
            strategies.append({
                'strategy_name': rem.strategy,
                'description': rem.description or '',
                'estimated_dir_after': round(rem.estimated_dir_after, 4),
                'estimated_spd_after': round(rem.estimated_spd_after, 4),
                'implementation_complexity': _estimate_complexity(rem.strategy),
                'expected_impact': _estimate_impact(rem),
            })
        
        return {
            'total_strategies': len(strategies),
            'recommended_strategies': strategies,
            'priority_order': _prioritize_strategies(strategies),
        }


class ComplianceSection:
    """Legal and regulatory compliance assessment."""
    
    @staticmethod
    def generate(report) -> Dict[str, Any]:
        """Generate compliance section from audit report."""
        # Check EEOC 80% rule (4/5ths rule)
        eeoc_violations = []
        for attr, groups in report.label_rates.items():
            rates = {g: stats.get('positive_rate', 0) for g, stats in groups.items()}
            if len(rates) >= 2:
                max_rate = max(rates.values())
                for group, rate in rates.items():
                    if max_rate > 0:
                        ratio = rate / max_rate
                        if ratio < 0.8:
                            eeoc_violations.append({
                                'attribute': attr,
                                'group': group,
                                'selection_rate': round(rate, 4),
                                'max_rate': round(max_rate, 4),
                                'ratio': round(ratio, 4),
                                'passes_80_rule': False,
                            })
        
        # Check representation balance
        representation_issues = []
        for attr, groups in report.representation.items():
            percentages = [stats['percentage'] for stats in groups.values()]
            if percentages:
                max_pct = max(percentages)
                min_pct = min(percentages)
                if max_pct > 0 and (min_pct / max_pct) < 0.5:
                    representation_issues.append({
                        'attribute': attr,
                        'imbalance_ratio': round(min_pct / max_pct, 4),
                        'concern': 'Severe underrepresentation detected',
                    })
        
        return {
            'eeoc_80_rule': {
                'total_violations': len(eeoc_violations),
                'violations': eeoc_violations,
                'compliant': len(eeoc_violations) == 0,
            },
            'representation_balance': {
                'total_issues': len(representation_issues),
                'issues': representation_issues,
            },
            'overall_compliance_status': 'PASS' if len(eeoc_violations) == 0 else 'FAIL',
            'recommendations': _generate_compliance_recommendations(eeoc_violations, representation_issues),
        }


class ValiditySection:
    """Statistical validity and confidence assessment."""
    
    @staticmethod
    def generate(report) -> Dict[str, Any]:
        """Generate validity section from audit report."""
        # Calculate average confidence across findings
        if report.findings:
            avg_confidence = sum(f.confidence for f in report.findings) / len(report.findings)
        else:
            avg_confidence = 1.0
        
        # Sample size adequacy
        sample_adequacy = _assess_sample_size(report.row_count, report.representation)
        
        # Data quality metrics
        total_cells = report.row_count * report.column_count
        missing_cells = sum(
            stats.get('missing_count', 0)
            for attr_data in report.missing_data_matrix.values()
            for stats in attr_data.values()
        )
        completeness = 1.0 - (missing_cells / total_cells) if total_cells > 0 else 0.0
        
        return {
            'average_confidence': round(avg_confidence, 4),
            'sample_size': report.row_count,
            'sample_adequacy': sample_adequacy,
            'data_completeness': round(completeness, 4),
            'statistical_power': _estimate_statistical_power(report.row_count),
            'limitations': _identify_limitations(report),
        }


# Helper functions

def _classify_proxy_risk(score: float, nmi: float) -> str:
    """Classify proxy feature risk level."""
    if score > 0.7 or nmi > 0.5:
        return 'HIGH'
    elif score > 0.4 or nmi > 0.3:
        return 'MEDIUM'
    else:
        return 'LOW'


def _generate_findings_summary(findings: List) -> str:
    """Generate a summary of findings."""
    if not findings:
        return "No significant bias detected in the dataset."
    
    critical = sum(1 for f in findings if f.severity == 'CRITICAL')
    moderate = sum(1 for f in findings if f.severity == 'MODERATE')
    
    if critical > 0:
        return f"Dataset shows {critical} critical bias issue(s) requiring immediate attention."
    elif moderate > 0:
        return f"Dataset shows {moderate} moderate bias issue(s) that should be addressed."
    else:
        return "Dataset shows minor bias issues with low severity."


def _estimate_complexity(strategy: str) -> str:
    """Estimate implementation complexity of a remediation strategy."""
    strategy_lower = strategy.lower()
    if 'resample' in strategy_lower or 'reweight' in strategy_lower:
        return 'LOW'
    elif 'synthetic' in strategy_lower or 'augment' in strategy_lower:
        return 'MEDIUM'
    elif 'collect' in strategy_lower or 'recollect' in strategy_lower:
        return 'HIGH'
    else:
        return 'MEDIUM'


def _estimate_impact(remediation) -> str:
    """Estimate the expected impact of a remediation strategy."""
    dir_improvement = remediation.estimated_dir_after - 0.8  # Assuming 0.8 is target
    spd_improvement = abs(remediation.estimated_spd_after)  # Closer to 0 is better
    
    if dir_improvement > 0.1 and spd_improvement < 0.05:
        return 'HIGH'
    elif dir_improvement > 0.05 or spd_improvement < 0.1:
        return 'MEDIUM'
    else:
        return 'LOW'


def _prioritize_strategies(strategies: List[Dict]) -> List[str]:
    """Prioritize remediation strategies by impact and complexity."""
    # Sort by impact (high first) and complexity (low first)
    impact_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
    complexity_order = {'LOW': 3, 'MEDIUM': 2, 'HIGH': 1}
    
    sorted_strategies = sorted(
        strategies,
        key=lambda s: (impact_order.get(s['expected_impact'], 0), 
                      complexity_order.get(s['implementation_complexity'], 0)),
        reverse=True
    )
    
    return [s['strategy_name'] for s in sorted_strategies]


def _generate_compliance_recommendations(eeoc_violations: List, representation_issues: List) -> List[str]:
    """Generate compliance recommendations."""
    recommendations = []
    
    if eeoc_violations:
        recommendations.append(
            "Address EEOC 80% rule violations through resampling or reweighting to ensure "
            "selection rates across groups meet the 4/5ths threshold."
        )
    
    if representation_issues:
        recommendations.append(
            "Improve demographic representation balance through targeted data collection "
            "or synthetic data augmentation for underrepresented groups."
        )
    
    if not recommendations:
        recommendations.append("Dataset meets basic compliance requirements. Continue monitoring.")
    
    return recommendations


def _assess_sample_size(row_count: int, representation: Dict) -> str:
    """Assess if sample size is adequate for statistical validity."""
    # Check minimum samples per group
    min_samples_per_group = float('inf')
    for attr_data in representation.values():
        for stats in attr_data.values():
            min_samples_per_group = min(min_samples_per_group, stats['count'])
    
    if min_samples_per_group < 30:
        return 'INSUFFICIENT'
    elif min_samples_per_group < 100:
        return 'MARGINAL'
    elif min_samples_per_group < 500:
        return 'ADEQUATE'
    else:
        return 'EXCELLENT'


def _estimate_statistical_power(sample_size: int) -> str:
    """Estimate statistical power based on sample size."""
    if sample_size < 100:
        return 'LOW'
    elif sample_size < 500:
        return 'MEDIUM'
    elif sample_size < 1000:
        return 'HIGH'
    else:
        return 'VERY_HIGH'


def _identify_limitations(report) -> List[str]:
    """Identify limitations in the audit."""
    limitations = []
    
    # Sample size limitations
    if report.row_count < 500:
        limitations.append(
            f"Small sample size (n={report.row_count}) may limit statistical power and generalizability."
        )
    
    # Missing data limitations
    total_cells = report.row_count * report.column_count
    missing_cells = sum(
        stats.get('missing_count', 0)
        for attr_data in report.missing_data_matrix.values()
        for stats in attr_data.values()
    )
    if total_cells > 0 and (missing_cells / total_cells) > 0.1:
        limitations.append(
            f"High missing data rate ({missing_cells/total_cells:.1%}) may affect reliability of findings."
        )
    
    # Representation limitations
    for attr, groups in report.representation.items():
        for group, stats in groups.items():
            if stats['count'] < 30:
                limitations.append(
                    f"Small sample size for {attr}={group} (n={stats['count']}) limits confidence in group-specific findings."
                )
    
    if not limitations:
        limitations.append("No major limitations identified in the audit methodology.")
    
    return limitations
