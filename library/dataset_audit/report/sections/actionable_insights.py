"""
Actionable Insights Section for Dataset Audit Reports.

Generates plain-English summaries and prioritized action items
for both technical and non-technical users.
"""

from typing import Dict, Any, List, Optional
import math


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
    def _get_worst_dir(audit_report) -> Optional[float]:
        """Get worst Disparate Impact Ratio from findings."""
        dir_values = []
        for finding in audit_report.findings:
            if finding.metric_name == 'DIR' and finding.metric_value is not None:
                dir_values.append(finding.metric_value)
        return min(dir_values) if dir_values else None
    
    @staticmethod
    def _get_worst_spd(audit_report) -> Optional[float]:
        """Get worst Statistical Parity Difference from findings."""
        spd_values = []
        for finding in audit_report.findings:
            if finding.metric_name == 'SPD' and finding.metric_value is not None:
                spd_values.append(abs(finding.metric_value))
        return max(spd_values) if spd_values else None
    
    @staticmethod
    def _get_compliance_data(audit_report) -> Dict[str, Any]:
        """Extract compliance information."""
        # Check if compliance data exists in report
        compliance_violations = []
        
        for finding in audit_report.findings:
            if finding.check_type == 'label_bias' and finding.severity == 'CRITICAL':
                if 'DIR' in finding.message or 'disparate impact' in finding.message.lower():
                    compliance_violations.append(finding)
        
        return {
            'has_violations': len(compliance_violations) > 0,
            'violation_count': len(compliance_violations),
            'violations': compliance_violations
        }
    
    @staticmethod
    def _generate_plain_english(audit_report, critical_findings, worst_dir, compliance_data) -> Dict[str, str]:
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
            if top_remediation.strategy_name == 'reweighting':
                quickest_fix = (
                    "Apply sample reweighting - this adjusts the importance of each data point without changing your data. "
                    "It's the fastest fix (can be done in minutes) and will improve fairness significantly. "
                    f"Expected improvement: selection rates will go from {int(worst_dir * 100) if worst_dir else 'current'}% to ~95% of the highest group."
                )
            elif top_remediation.strategy_name == 'disparate_impact_remover':
                quickest_fix = (
                    "Use disparate impact remover to transform your features. This reduces bias while keeping your data usable. "
                    "Takes about 30 minutes to implement."
                )
            else:
                quickest_fix = f"Apply {top_remediation.strategy_name}: {top_remediation.description}"
        else:
            quickest_fix = "Remove or transform high-risk proxy features that leak protected attribute information."
        
        return {
            'one_liner': one_liner,
            'biggest_problem': biggest_problem,
            'legal_risk': legal_risk,
            'quickest_fix': quickest_fix
        }
    
    @staticmethod
    def _generate_action_priority(audit_report, critical_findings, moderate_findings) -> List[Dict[str, Any]]:
        """Generate prioritized action list."""
        actions = []
        rank = 1
        
        # Priority 1: Apply reweighting if available
        reweighting = next((r for r in audit_report.remediation_suggestions if r.strategy_name == 'reweighting'), None)
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
        high_risk_proxies = [p for p in audit_report.proxy_features if p.risk_level == 'HIGH']
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
        underrep_findings = [f for f in moderate_findings if f.check_type == 'representation']
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
        dir_remover = next((r for r in audit_report.remediation_suggestions if r.strategy_name == 'disparate_impact_remover'), None)
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
        intersect_findings = [f for f in critical_findings if f.check_type == 'intersectional_disparity']
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
    def _generate_checklist(audit_report, critical_findings, moderate_findings) -> List[Dict[str, Any]]:
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
            if finding.check_type == 'label_bias':
                effort = 'LOW'
                expected_outcome = 'Disparate impact ratio improves to ≥0.80 (EEOC compliant)'
            elif finding.check_type == 'intersectional_disparity':
                effort = 'HIGH'
                expected_outcome = 'Intersectional groups achieve fair representation and outcomes'
            else:
                effort = 'MEDIUM'
                expected_outcome = 'Issue resolved, fairness metrics improve'
            
            checklist.append({
                'id': f'C{task_id:03d}',
                'task': f'Fix {finding.check_type}: {finding.message[:100]}...' if len(finding.message) > 100 else f'Fix {finding.check_type}: {finding.message}',
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
            
            if finding.check_type == 'representation':
                effort = 'MEDIUM'
                expected_outcome = 'Group representation increases to ≥10% of dataset'
            elif finding.check_type == 'superadditive_bias':
                effort = 'HIGH'
                expected_outcome = 'Intersectional bias reduced to additive levels'
            else:
                effort = 'MEDIUM'
                expected_outcome = 'Moderate issue resolved'
            
            checklist.append({
                'id': f'C{task_id:03d}',
                'task': f'Address {finding.check_type}: {finding.message[:100]}...' if len(finding.message) > 100 else f'Address {finding.check_type}: {finding.message}',
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
    def _generate_column_risks(audit_report) -> List[Dict[str, Any]]:
        """Generate column risk scores."""
        column_risks = []
        
        for proxy in audit_report.proxy_features:
            # Calculate risk score (1-10)
            if proxy.risk_level == 'HIGH':
                base_score = 9
            elif proxy.risk_level == 'MEDIUM':
                base_score = 6
            else:
                base_score = 3
            
            # Adjust based on correlation
            if proxy.correlation_score is not None and not math.isnan(proxy.correlation_score):
                if proxy.correlation_score > 0.8:
                    risk_score = 10
                elif proxy.correlation_score > 0.5:
                    risk_score = base_score
                else:
                    risk_score = max(base_score - 2, 1)
            else:
                risk_score = base_score
            
            # Determine action
            if proxy.risk_level == 'HIGH':
                if proxy.correlation_score and proxy.correlation_score >= 0.99:
                    action = 'REMOVE'
                    action_reason = 'Perfect correlation with protected attribute - this is the protected attribute itself or a direct encoding'
                else:
                    action = 'REMOVE'
                    action_reason = f'High correlation ({proxy.correlation_score:.2f}) with {proxy.protected_attribute} - will leak bias'
            elif proxy.risk_level == 'MEDIUM':
                action = 'TRANSFORM'
                action_reason = f'Moderate correlation with {proxy.protected_attribute} - consider debiasing transformation'
            else:
                action = 'MONITOR'
                action_reason = 'Low risk but monitor for bias amplification during training'
            
            column_risks.append({
                'column': proxy.feature,
                'risk_score': risk_score,
                'risk_level': proxy.risk_level,
                'reason': f'Correlated with {proxy.protected_attribute} (method: {proxy.detection_method}, score: {proxy.correlation_score:.3f if proxy.correlation_score and not math.isnan(proxy.correlation_score) else "N/A"})',
                'protected_attribute': proxy.protected_attribute,
                'action': action,
                'action_reason': action_reason
            })
        
        # Sort by risk score descending
        column_risks.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return column_risks
    
    @staticmethod
    def _generate_simulations(audit_report, worst_dir) -> Dict[str, Any]:
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
            f.check_type == 'label_bias' and f.severity == 'CRITICAL' and 'DIR' in f.message
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
        reweighting = next((r for r in audit_report.remediation_suggestions if r.strategy_name == 'reweighting'), None)
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
        smote = next((r for r in audit_report.remediation_suggestions if r.strategy_name == 'smote'), None)
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
    def _generate_summary_stats(audit_report, column_risks) -> Dict[str, Any]:
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
            r.strategy_name in ['disparate_impact_remover', 'smote']
            for r in audit_report.remediation_suggestions
        )
        
        # Legal risk level
        critical_count = len([f for f in audit_report.findings if f.severity == 'CRITICAL'])
        has_eeoc_violations = any(
            f.check_type == 'label_bias' and f.severity == 'CRITICAL'
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
