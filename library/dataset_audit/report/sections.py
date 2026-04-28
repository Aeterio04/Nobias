"""
Report sections for dataset audit reports.

Each section is responsible for extracting and formatting a specific
aspect of the audit results.
"""

from typing import Dict, Any, List
from datetime import datetime
import math


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



class ActionableInsightsSection:
    """Generate actionable insights from dataset audit report."""
    
    @staticmethod
    def generate(audit_report) -> Dict[str, Any]:
        """
        Generate actionable insights section.
        
        Args:
            audit_report: DatasetAuditReport object
            
        Returns:
            Dictionary with actionable insights
        """
        # Get critical findings
        critical_findings = [f for f in audit_report.findings if f.severity == 'CRITICAL']
        moderate_findings = [f for f in audit_report.findings if f.severity == 'MODERATE']
        
        # Get worst metrics
        worst_dir = ActionableInsightsSection._get_worst_dir(audit_report)
        worst_spd = ActionableInsightsSection._get_worst_spd(audit_report)
        
        # Get compliance info
        compliance_data = ActionableInsightsSection._get_compliance_data(audit_report)
        
        # Generate plain English section
        plain_english = ActionableInsightsSection._generate_plain_english(
            audit_report, critical_findings, worst_dir, compliance_data
        )
        
        # Generate action priority
        action_priority = ActionableInsightsSection._generate_action_priority(
            audit_report, critical_findings, moderate_findings
        )
        
        # Generate improvement checklist
        improvement_checklist = ActionableInsightsSection._generate_checklist(
            audit_report, critical_findings, moderate_findings
        )
        
        # Generate column risk scores
        column_risk_scores = ActionableInsightsSection._generate_column_risks(
            audit_report
        )
        
        # Generate simulated improvements
        simulated_improvements = ActionableInsightsSection._generate_simulations(
            audit_report, worst_dir
        )
        
        # Generate summary stats
        summary_stats = ActionableInsightsSection._generate_summary_stats(
            audit_report, column_risk_scores
        )
        
        return {
            'plain_english': plain_english,
            'action_priority': action_priority,
            'improvement_checklist': improvement_checklist,
            'column_risk_scores': column_risk_scores,
            'simulated_improvements': simulated_improvements,
            'summary_stats': summary_stats,
        }
    
    @staticmethod
    def _get_worst_dir(audit_report):
        """Get worst Disparate Impact Ratio from findings."""
        dir_values = []
        for finding in audit_report.findings:
            if finding.metric == 'DIR' and finding.value is not None:
                dir_values.append(finding.value)
        return min(dir_values) if dir_values else None
    
    @staticmethod
    def _get_worst_spd(audit_report):
        """Get worst Statistical Parity Difference from findings."""
        spd_values = []
        for finding in audit_report.findings:
            if finding.metric == 'SPD' and finding.value is not None:
                spd_values.append(abs(finding.value))
        return max(spd_values) if spd_values else None
    
    @staticmethod
    def _get_compliance_data(audit_report):
        """Extract compliance information."""
        compliance_violations = []
        
        for finding in audit_report.findings:
            if finding.check == 'label_bias' and finding.severity == 'CRITICAL':
                if 'DIR' in finding.message or 'disparate impact' in finding.message.lower():
                    compliance_violations.append(finding)
        
        return {
            'has_violations': len(compliance_violations) > 0,
            'violation_count': len(compliance_violations),
            'violations': compliance_violations
        }
    
    @staticmethod
    def _generate_plain_english(audit_report, critical_findings, worst_dir, compliance_data):
        """Generate plain English explanations."""
        # One-liner
        if not critical_findings:
            one_liner = "Your dataset looks good with no critical bias issues detected."
        else:
            main_issue = critical_findings[0]
            if 'gender' in main_issue.message.lower():
                one_liner = f"Women are being selected at only {int(worst_dir * 100) if worst_dir else 'significantly lower'}% the rate of men in your dataset."
            elif 'race' in main_issue.message.lower():
                one_liner = "Certain racial groups are being selected at significantly lower rates than others."
            else:
                one_liner = f"Your dataset has {len(critical_findings)} critical fairness issues that need immediate attention."
        
        # Biggest problem
        if not critical_findings:
            biggest_problem = "No critical issues found. Your dataset shows good demographic balance and fair representation across groups."
        else:
            main_issue = critical_findings[0]
            if worst_dir and worst_dir < 0.5:
                biggest_problem = (
                    f"The biggest problem is severe imbalance in who gets positive outcomes. "
                    f"Some groups are getting selected at less than half the rate of others. "
                    f"This means if you train a model on this data, it will likely discriminate against these groups. "
                    f"Found in: {main_issue.message}"
                )
            else:
                biggest_problem = (
                    f"Your dataset shows unfair treatment patterns. {main_issue.message}. "
                    f"This could lead to discriminatory decisions if used for training."
                )
        
        # Legal risk
        if compliance_data['has_violations']:
            legal_risk = (
                f"YES - High legal risk. Your dataset fails the EEOC 80% rule with {compliance_data['violation_count']} violation(s). "
                f"This means some groups are selected at less than 80% the rate of the highest group. "
                f"Using this data for hiring, lending, or other regulated decisions could expose you to discrimination lawsuits. "
                f"You should fix these issues before using this data."
            )
        elif critical_findings:
            legal_risk = (
                "MODERATE - While not all issues trigger EEOC violations, your dataset has critical fairness problems "
                "that could be challenged in court. Recommend fixing before production use."
            )
        else:
            legal_risk = (
                "LOW - Your dataset appears to meet basic fairness standards. "
                "However, always consult legal counsel for regulated use cases."
            )
        
        # Quickest fix
        if audit_report.remediation_suggestions:
            top_remediation = audit_report.remediation_suggestions[0]
            if top_remediation.strategy == 'reweighting':
                quickest_fix = (
                    "Apply sample reweighting - this adjusts the importance of each data point without changing your data. "
                    "It's the fastest fix (can be done in minutes) and will improve fairness significantly. "
                    f"Expected improvement: selection rates will go from {int(worst_dir * 100) if worst_dir else 'current'}% to ~95% of the highest group."
                )
            elif top_remediation.strategy == 'disparate_impact_remover':
                quickest_fix = (
                    "Use disparate impact remover to transform your features. This reduces bias while keeping your data usable. "
                    "Takes about 30 minutes to implement."
                )
            else:
                quickest_fix = f"Apply {top_remediation.strategy}: {top_remediation.description or 'Recommended remediation strategy'}"
        else:
            quickest_fix = "Remove or transform high-risk proxy features that leak protected attribute information."
        
        return {
            'one_liner': one_liner,
            'biggest_problem': biggest_problem,
            'legal_risk': legal_risk,
            'quickest_fix': quickest_fix
        }
    
    @staticmethod
    def _generate_action_priority(audit_report, critical_findings, moderate_findings):
        """Generate prioritized action list."""
        actions = []
        rank = 1
        
        # Priority 1: Apply reweighting if available
        reweighting = next((r for r in audit_report.remediation_suggestions if r.strategy == 'reweighting'), None)
        if reweighting and critical_findings:
            worst_dir = ActionableInsightsSection._get_worst_dir(audit_report)
            actions.append({
                'rank': rank,
                'action': 'Apply sample reweighting to balance positive outcome rates across demographic groups',
                'reason': (
                    f"Highest impact, lowest effort. Current worst disparate impact ratio is {worst_dir:.2f} "
                    f"(needs ≥0.80). Reweighting can improve this to ~{reweighting.estimated_dir_after:.2f} "
                    f"without changing your data."
                ),
                'effort': 'LOW',
                'impact': 'HIGH',
                'do_this_first': True
            })
            rank += 1
        
        # Priority 2: Remove high-risk proxy features
        high_risk_proxies = [p for p in audit_report.proxy_features if _classify_proxy_risk(p.score, p.nmi) == 'HIGH']
        if high_risk_proxies and len(high_risk_proxies) <= 5:
            proxy_names = [p.feature for p in high_risk_proxies[:3]]
            actions.append({
                'rank': rank,
                'action': f"Remove {len(high_risk_proxies)} high-risk proxy features from your dataset",
                'reason': (
                    f"Features like {', '.join(proxy_names)} are strongly correlated with protected attributes "
                    f"and will leak bias into any model trained on this data. Removing them is straightforward."
                ),
                'effort': 'LOW',
                'impact': 'HIGH',
                'do_this_first': False
            })
            rank += 1
        
        # Priority 3: Address underrepresentation
        underrep_findings = [f for f in moderate_findings if f.check == 'representation']
        if underrep_findings:
            actions.append({
                'rank': rank,
                'action': 'Collect more data for underrepresented groups or apply SMOTE oversampling',
                'reason': (
                    f"Found {len(underrep_findings)} underrepresented groups. "
                    f"Small sample sizes lead to unreliable model predictions for these groups."
                ),
                'effort': 'MEDIUM',
                'impact': 'MEDIUM',
                'do_this_first': False
            })
            rank += 1
        
        # Priority 4: Apply disparate impact remover
        dir_remover = next((r for r in audit_report.remediation_suggestions if r.strategy == 'disparate_impact_remover'), None)
        if dir_remover and critical_findings:
            actions.append({
                'rank': rank,
                'action': 'Apply disparate impact remover to transform feature distributions',
                'reason': (
                    f"Reduces group-dependent variation in features. "
                    f"Expected DIR improvement to {dir_remover.estimated_dir_after:.2f}. "
                    f"More thorough than reweighting but requires feature transformation."
                ),
                'effort': 'MEDIUM',
                'impact': 'MEDIUM',
                'do_this_first': False
            })
            rank += 1
        
        # Priority 5: Address intersectional disparities
        intersect_findings = [f for f in critical_findings if f.check == 'intersectional_disparity']
        if intersect_findings:
            actions.append({
                'rank': rank,
                'action': 'Address intersectional bias through targeted oversampling or reweighting',
                'reason': (
                    f"Found {len(intersect_findings)} intersectional disparity issue(s). "
                    f"Some combinations of demographics (e.g., Female + Black) face compounded disadvantage. "
                    f"Requires targeted intervention."
                ),
                'effort': 'HIGH',
                'impact': 'HIGH',
                'do_this_first': False
            })
            rank += 1
        
        return actions
    
    @staticmethod
    def _generate_checklist(audit_report, critical_findings, moderate_findings):
        """Generate improvement checklist."""
        checklist = []
        task_id = 1
        
        # One checklist item per critical finding
        for finding in critical_findings:
            columns_affected = []
            
            # Extract affected columns from message
            if 'gender' in finding.message.lower():
                columns_affected.append('gender')
            if 'race' in finding.message.lower():
                columns_affected.append('race')
            if 'age' in finding.message.lower():
                columns_affected.append('age')
            
            # Determine effort
            if finding.check == 'label_bias':
                effort = 'LOW'
                expected_outcome = 'Disparate impact ratio improves to ≥0.80 (EEOC compliant)'
            elif finding.check == 'intersectional_disparity':
                effort = 'HIGH'
                expected_outcome = 'Intersectional groups achieve fair representation and outcomes'
            else:
                effort = 'MEDIUM'
                expected_outcome = 'Issue resolved, fairness metrics improve'
            
            checklist.append({
                'id': f'C{task_id:03d}',
                'task': f'Fix {finding.check}: {finding.message[:100]}...' if len(finding.message) > 100 else f'Fix {finding.check}: {finding.message}',
                'reason': f'Critical severity issue. {finding.message}',
                'columns_affected': columns_affected if columns_affected else None,
                'status': 'pending',
                'priority': 1,
                'effort': effort,
                'expected_outcome': expected_outcome
            })
            task_id += 1
        
        # One checklist item per moderate finding (up to 10)
        for finding in moderate_findings[:10]:
            columns_affected = []
            
            if 'gender' in finding.message.lower():
                columns_affected.append('gender')
            if 'race' in finding.message.lower():
                columns_affected.append('race')
            
            if finding.check == 'representation':
                effort = 'MEDIUM'
                expected_outcome = 'Group representation increases to ≥10% of dataset'
            elif finding.check == 'superadditive_bias':
                effort = 'HIGH'
                expected_outcome = 'Intersectional bias reduced to additive levels'
            else:
                effort = 'MEDIUM'
                expected_outcome = 'Moderate issue resolved'
            
            checklist.append({
                'id': f'C{task_id:03d}',
                'task': f'Address {finding.check}: {finding.message[:100]}...' if len(finding.message) > 100 else f'Address {finding.check}: {finding.message}',
                'reason': f'Moderate severity issue. {finding.message}',
                'columns_affected': columns_affected if columns_affected else None,
                'status': 'pending',
                'priority': 2,
                'effort': effort,
                'expected_outcome': expected_outcome
            })
            task_id += 1
        
        return checklist
    
    @staticmethod
    def _generate_column_risks(audit_report):
        """Generate column risk scores."""
        column_risks = []
        
        for proxy in audit_report.proxy_features:
            # Calculate risk score (1-10)
            risk_level = _classify_proxy_risk(proxy.score, proxy.nmi)
            if risk_level == 'HIGH':
                base_score = 9
            elif risk_level == 'MEDIUM':
                base_score = 6
            else:
                base_score = 3
            
            # Adjust based on correlation
            if proxy.score is not None and not math.isnan(proxy.score):
                if proxy.score > 0.8:
                    risk_score = 10
                elif proxy.score > 0.5:
                    risk_score = base_score
                else:
                    risk_score = max(base_score - 2, 1)
            else:
                risk_score = base_score
            
            # Determine action
            if risk_level == 'HIGH':
                if proxy.score and proxy.score >= 0.99:
                    action = 'REMOVE'
                    action_reason = 'Perfect correlation with protected attribute - this is the protected attribute itself or a direct encoding'
                else:
                    action = 'REMOVE'
                    action_reason = f'High correlation ({proxy.score:.2f}) with {proxy.protected} - will leak bias'
            elif risk_level == 'MEDIUM':
                action = 'TRANSFORM'
                action_reason = f'Moderate correlation with {proxy.protected} - consider debiasing transformation'
            else:
                action = 'MONITOR'
                action_reason = 'Low risk but monitor for bias amplification during training'
            
            column_risks.append({
                'column': proxy.feature,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'reason': f'Correlated with {proxy.protected} (method: {proxy.method}, score: {proxy.score:.3f if proxy.score and not math.isnan(proxy.score) else "N/A"})',
                'protected_attribute': proxy.protected,
                'action': action,
                'action_reason': action_reason
            })
        
        # Sort by risk score descending
        column_risks.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return column_risks
    
    @staticmethod
    def _generate_simulations(audit_report, worst_dir):
        """Generate simulated improvement scenarios."""
        # Get current state
        critical_count = len([f for f in audit_report.findings if f.severity == 'CRITICAL'])
        moderate_count = len([f for f in audit_report.findings if f.severity == 'MODERATE'])
        
        # Calculate health score (0-100)
        total_findings = len(audit_report.findings)
        if total_findings == 0:
            health_score = 100
        else:
            # Penalize critical more than moderate
            penalty = (critical_count * 10) + (moderate_count * 5)
            health_score = max(0, 100 - penalty)
        
        # Check compliance
        has_eeoc_violations = any(
            f.check == 'label_bias' and f.severity == 'CRITICAL' and 'DIR' in f.message
            for f in audit_report.findings
        )
        current_compliance = 'FAIL' if has_eeoc_violations else 'PASS'
        
        current_state = {
            'health_score': round(health_score, 1),
            'dir': round(worst_dir, 4) if worst_dir else None,
            'critical_findings': critical_count,
            'compliance': current_compliance
        }
        
        # Simulate reweighting
        reweighting = next((r for r in audit_report.remediation_suggestions if r.strategy == 'reweighting'), None)
        if reweighting:
            dir_after_reweight = reweighting.estimated_dir_after
            findings_resolved = max(1, int(critical_count * 0.7))  # Estimate 70% of critical findings resolved
            findings_remaining = total_findings - findings_resolved
            health_after_reweight = min(100, health_score + (findings_resolved * 8))
            compliance_after_reweight = 'PASS' if dir_after_reweight >= 0.8 else 'FAIL'
            
            if_reweighting_applied = {
                'health_score_after': round(health_after_reweight, 1),
                'dir_after': round(dir_after_reweight, 4),
                'findings_resolved': findings_resolved,
                'findings_remaining': findings_remaining,
                'compliance_after': compliance_after_reweight,
                'accuracy_impact': 'No accuracy impact - reweighting does not change data'
            }
        else:
            if_reweighting_applied = None
        
        # Simulate SMOTE
        smote = next((r for r in audit_report.remediation_suggestions if r.strategy == 'smote'), None)
        if smote:
            dir_after_smote = smote.estimated_dir_after
            findings_resolved_smote = max(1, int(moderate_count * 0.6))  # Estimate 60% of moderate findings resolved
            findings_remaining_smote = total_findings - findings_resolved_smote
            health_after_smote = min(100, health_score + (findings_resolved_smote * 5))
            compliance_after_smote = 'PASS' if dir_after_smote >= 0.8 else 'FAIL'
            
            if_smote_applied = {
                'health_score_after': round(health_after_smote, 1),
                'dir_after': round(dir_after_smote, 4),
                'findings_resolved': findings_resolved_smote,
                'findings_remaining': findings_remaining_smote,
                'compliance_after': compliance_after_smote,
                'accuracy_impact': 'Slight improvement expected due to better minority representation'
            }
        else:
            if_smote_applied = None
        
        # Simulate all applied
        if reweighting and smote:
            best_dir = max(reweighting.estimated_dir_after, smote.estimated_dir_after)
            total_resolved = min(total_findings, int(critical_count * 0.8) + int(moderate_count * 0.7))
            health_after_all = min(100, health_score + (total_resolved * 7))
            
            if_all_applied = {
                'health_score_after': round(health_after_all, 1),
                'dir_after': round(best_dir, 4),
                'findings_resolved': total_resolved,
                'findings_remaining': max(0, total_findings - total_resolved),
                'compliance_after': 'PASS' if best_dir >= 0.8 else 'FAIL',
                'recommended': True
            }
        else:
            if_all_applied = None
        
        return {
            'current_state': current_state,
            'if_reweighting_applied': if_reweighting_applied,
            'if_smote_applied': if_smote_applied,
            'if_all_applied': if_all_applied
        }
    
    @staticmethod
    def _generate_summary_stats(audit_report, column_risks):
        """Generate summary statistics."""
        total_at_risk = len(column_risks)
        to_remove = len([c for c in column_risks if c['action'] == 'REMOVE'])
        to_monitor = len([c for c in column_risks if c['action'] == 'MONITOR'])
        
        # Estimate fix time
        critical_count = len([f for f in audit_report.findings if f.severity == 'CRITICAL'])
        moderate_count = len([f for f in audit_report.findings if f.severity == 'MODERATE'])
        
        if critical_count == 0:
            estimated_time = '1-2 hours'
        elif critical_count <= 3:
            estimated_time = '4-8 hours'
        else:
            estimated_time = '1-2 days'
        
        # Determine if retraining required
        needs_retraining = any(
            r.strategy in ['disparate_impact_remover', 'smote']
            for r in audit_report.remediation_suggestions
        )
        
        # Legal risk level
        has_eeoc_violations = any(
            f.check == 'label_bias' and f.severity == 'CRITICAL'
            for f in audit_report.findings
        )
        
        if has_eeoc_violations:
            legal_risk = 'CRITICAL'
        elif critical_count > 0:
            legal_risk = 'HIGH'
        elif moderate_count > 5:
            legal_risk = 'MEDIUM'
        else:
            legal_risk = 'LOW'
        
        return {
            'total_columns_at_risk': total_at_risk,
            'columns_to_remove': to_remove,
            'columns_to_monitor': to_monitor,
            'estimated_fix_time': estimated_time,
            'retraining_required': needs_retraining,
            'legal_risk_level': legal_risk
        }
