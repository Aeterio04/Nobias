"""
Model Audit Report Interpreter - Generates actionable insights from audit reports.

This module transforms technical model audit reports into plain-English insights
with prioritized actions for both technical and non-technical stakeholders.
"""
from typing import Dict, List, Any, Optional, Union
import json
from pathlib import Path
from dataclasses import dataclass, asdict


def interpret_model_audit_report(
    report_data: Union[str, Path, Dict[str, Any]],
    dataset_audit_data: Optional[Union[str, Path, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generate actionable insights from a model audit report.
    
    Args:
        report_data: Path to comprehensive JSON report or dict with report data
        dataset_audit_data: Optional path to dataset audit report or dict (for bias amplification)
        
    Returns:
        Dict with structured actionable insights
    """
    # Load report data
    if isinstance(report_data, (str, Path)):
        with open(report_data, 'r') as f:
            report = json.load(f)
    else:
        report = report_data
    
    # Load dataset audit if provided
    dataset_report = None
    if dataset_audit_data:
        if isinstance(dataset_audit_data, (str, Path)):
            with open(dataset_audit_data, 'r') as f:
                dataset_report = json.load(f)
        else:
            dataset_report = dataset_audit_data
    
    # Build the actionable insights
    insights = {
        "plain_english": _generate_plain_english(report),
        "action_priority": _generate_action_priority(report),
        "bias_amplification": _analyze_bias_amplification(report, dataset_report),
        "group_performance_gaps": _analyze_group_performance_gaps(report),
        "metric_scorecard": _generate_metric_scorecard(report),
        "simulated_improvements": _simulate_improvements(report),
        "summary_stats": _generate_summary_stats(report),
    }
    
    return insights


def _generate_plain_english(report: Dict[str, Any]) -> Dict[str, str]:
    """Generate plain-English explanations for non-technical users."""
    health = report.get("health", {})
    findings = report.get("findings", {})
    results = report.get("results", {})
    compliance = report.get("compliance", {})
    
    # Find the biggest problem
    critical_findings = findings.get("findings_by_severity", {}).get("CRITICAL", [])
    moderate_findings = findings.get("findings_by_severity", {}).get("MODERATE", [])
    
    # Determine worst finding
    worst_finding = None
    if critical_findings:
        worst_finding = critical_findings[0]
    elif moderate_findings:
        worst_finding = moderate_findings[0]
    
    # One-liner
    severity = health.get("overall_health", {}).get("severity", "UNKNOWN")
    critical_count = health.get("overall_health", {}).get("critical_findings", 0)
    
    if severity == "CRITICAL":
        one_liner = f"This model has {critical_count} critical bias issues that could lead to legal violations"
    elif severity == "MODERATE":
        one_liner = f"This model shows moderate bias with {critical_count} critical issues requiring attention"
    elif severity == "LOW":
        one_liner = "This model has minor fairness concerns that should be monitored"
    else:
        one_liner = "This model passes fairness checks with no significant bias detected"
    
    # Biggest problem explanation
    if worst_finding:
        affected = ", ".join(worst_finding.get("affected_groups", []))
        evidence = worst_finding.get("evidence", {})
        metric_value = evidence.get("metric_value", 0)
        
        if "Demographic Parity" in worst_finding.get("title", ""):
            biggest_problem = (
                f"The model approves different groups at very different rates. "
                f"The gap is {abs(metric_value):.1%}, which means one group is {abs(metric_value):.1%} "
                f"more likely to be approved than another. This affects: {affected}."
            )
        elif "Disparate Impact" in worst_finding.get("title", ""):
            biggest_problem = (
                f"The model violates the EEOC 80% rule. One group is approved at only "
                f"{metric_value:.1%} the rate of another group. Federal law requires at least 80%. "
                f"This affects: {affected}."
            )
        elif "Equalized Odds" in worst_finding.get("title", ""):
            biggest_problem = (
                f"The model makes different types of errors for different groups. "
                f"The error rate gap is {abs(metric_value):.1%}. This means one group experiences "
                f"more false rejections or false approvals. This affects: {affected}."
            )
        else:
            biggest_problem = worst_finding.get("description", "Bias detected in model predictions")
    else:
        biggest_problem = "No significant bias detected. Model performs fairly across groups."
    
    # What this means for users
    flip_rate = results.get("overall", {}).get("flip_rate", 0)
    if critical_count > 0 or flip_rate > 0.05:
        what_this_means = (
            "Real people from certain demographic groups are being unfairly rejected or approved "
            "by this model. If you're in an affected group, you might be denied opportunities "
            "that you deserve, or approved when you shouldn't be. This creates unequal treatment "
            "based on protected characteristics like gender or race."
        )
    elif len(moderate_findings) > 0:
        what_this_means = (
            "Some demographic groups may experience slightly different treatment by this model. "
            "While not severe, this could accumulate over time and affect opportunities for "
            "certain groups more than others."
        )
    else:
        what_this_means = (
            "The model treats different demographic groups fairly and equally. Users can expect "
            "consistent treatment regardless of their protected characteristics."
        )
    
    # Legal risk
    is_compliant = compliance.get("compliant", True)
    violations = compliance.get("violations", [])
    
    if not is_compliant and violations:
        legal_risk = (
            f"YES - This model would likely fail an EEOC audit. It violates the federal 80% rule "
            f"with {len(violations)} violation(s). This creates legal liability for discrimination "
            f"lawsuits. Companies using this model could face penalties, lawsuits, and be required "
            f"to provide back-pay to affected individuals. Legal exposure: HIGH."
        )
    elif critical_count > 0:
        legal_risk = (
            "POSSIBLY - While not a direct EEOC violation, the model shows significant bias that "
            "could be challenged in court. If someone from an affected group is denied and files "
            "a complaint, this audit would support their case. Legal exposure: MEDIUM."
        )
    elif len(moderate_findings) > 0:
        legal_risk = (
            "LOW RISK - The model shows some bias but likely wouldn't fail a legal audit. "
            "However, it's worth fixing these issues to reduce any potential legal exposure. "
            "Legal exposure: LOW."
        )
    else:
        legal_risk = (
            "NO RISK - This model would pass an EEOC audit. It treats groups fairly and equally. "
            "Legal exposure: MINIMAL."
        )
    
    # Quickest fix
    mitigation = report.get("mitigation", {})
    post_processing = mitigation.get("by_category", {}).get("post_processing", [])
    
    if post_processing:
        quickest_fix = (
            f"{post_processing[0].get('name', 'Threshold Adjustment')}: "
            f"{post_processing[0].get('description', '')} "
            f"This requires NO retraining and can be done in hours. "
            f"Expected impact: {post_processing[0].get('expected_impact', 'Significant improvement')}"
        )
    else:
        quickest_fix = (
            "Sample Reweighting: Adjust training data weights to reduce bias. "
            "This requires retraining the model but is a proven technique. "
            "Expected impact: Moderate improvement in fairness metrics."
        )
    
    return {
        "one_liner": one_liner,
        "biggest_problem": biggest_problem,
        "what_this_means_for_users": what_this_means,
        "legal_risk": legal_risk,
        "quickest_fix": quickest_fix,
    }


def _generate_action_priority(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate prioritized action list ranked by impact/effort ratio."""
    actions = []
    rank = 1
    
    mitigation = report.get("mitigation", {})
    findings = report.get("findings", {})
    results = report.get("results", {})
    
    # Get all mitigation options
    post_processing = mitigation.get("by_category", {}).get("post_processing", [])
    pre_processing = mitigation.get("by_category", {}).get("pre_processing", [])
    in_processing = mitigation.get("by_category", {}).get("in_processing", [])
    
    # Priority 1: Post-processing (no retraining, quick wins)
    for option in post_processing:
        # Estimate metric improvement
        critical_count = len(findings.get("findings_by_severity", {}).get("CRITICAL", []))
        moderate_count = len(findings.get("findings_by_severity", {}).get("MODERATE", []))
        
        if "Threshold" in option.get("name", ""):
            expected_improvement = (
                f"Demographic parity could improve from current violations to <0.05 difference. "
                f"Expected to resolve {min(critical_count, 2)} critical findings."
            )
        else:
            expected_improvement = "Moderate improvement in fairness metrics expected"
        
        actions.append({
            "rank": rank,
            "action": f"{option.get('name', 'Unknown')}: {option.get('description', '')}",
            "reason": (
                f"Ranked #{rank} because it requires no retraining (fastest to implement) "
                f"and can address {critical_count} critical findings. "
                f"Complexity is {option.get('complexity', 'low')}."
            ),
            "requires_retraining": option.get("requires_retraining", False),
            "effort": option.get("complexity", "low").upper(),
            "impact": "HIGH" if critical_count > 2 else "MEDIUM",
            "do_this_first": rank == 1,
            "expected_metric_improvement": expected_improvement,
        })
        rank += 1
    
    # Priority 2: Pre-processing (requires retraining but effective)
    for option in pre_processing:
        critical_count = len(findings.get("findings_by_severity", {}).get("CRITICAL", []))
        
        if "Reweighting" in option.get("name", ""):
            expected_improvement = (
                f"Can reduce demographic parity difference by 30-50%. "
                f"Expected to resolve {min(critical_count, 3)} critical findings."
            )
        elif "Remove" in option.get("name", "") or "Proxy" in option.get("name", ""):
            flip_rate = results.get("overall", {}).get("flip_rate", 0)
            expected_improvement = (
                f"Flip rate could drop from {flip_rate:.1%} to <2%. "
                f"Reduces individual fairness violations."
            )
        else:
            expected_improvement = "Significant improvement in fairness metrics expected"
        
        actions.append({
            "rank": rank,
            "action": f"{option.get('name', 'Unknown')}: {option.get('description', '')}",
            "reason": (
                f"Ranked #{rank} because it requires retraining (slower) but provides "
                f"more fundamental bias reduction. Complexity is {option.get('complexity', 'medium')}."
            ),
            "requires_retraining": option.get("requires_retraining", True),
            "effort": option.get("complexity", "medium").upper(),
            "impact": "HIGH" if critical_count > 2 else "MEDIUM",
            "do_this_first": False,
            "expected_metric_improvement": expected_improvement,
        })
        rank += 1
    
    # Priority 3: In-processing (requires retraining and more complex)
    for option in in_processing:
        actions.append({
            "rank": rank,
            "action": f"{option.get('name', 'Unknown')}: {option.get('description', '')}",
            "reason": (
                f"Ranked #{rank} because it requires retraining and modifying the training "
                f"process. Most complex but can provide best long-term results."
            ),
            "requires_retraining": option.get("requires_retraining", True),
            "effort": option.get("complexity", "high").upper(),
            "impact": "HIGH",
            "do_this_first": False,
            "expected_metric_improvement": "Comprehensive fairness improvement across all metrics",
        })
        rank += 1
    
    return actions


def _analyze_bias_amplification(
    report: Dict[str, Any],
    dataset_report: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Analyze whether model amplified or reduced dataset bias."""
    # Get worst disparate impact from model
    model_dir = 1.0  # Default to no bias
    fairness_metrics = report.get("results", {}).get("fairness_metrics", {})
    
    for attr, metrics in fairness_metrics.items():
        for metric in metrics:
            if metric.get("metric_name") == "Disparate Impact Ratio":
                value = metric.get("value", 1.0)
                if abs(1.0 - value) > abs(1.0 - model_dir):
                    model_dir = value
    
    # Get dataset DIR if available
    dataset_dir = None
    if dataset_report:
        dataset_fairness = dataset_report.get("results", {}).get("fairness_metrics", {})
        for attr, metrics in dataset_fairness.items():
            for metric in metrics:
                if metric.get("metric_name") == "Disparate Impact Ratio":
                    dataset_dir = metric.get("value", 1.0)
                    break
            if dataset_dir:
                break
    
    # Calculate amplification
    if dataset_dir is not None:
        amplification_score = abs(1.0 - model_dir) - abs(1.0 - dataset_dir)
        
        if amplification_score > 0.05:
            verdict = "Model AMPLIFIED bias"
            explanation = (
                f"The model made the bias worse. The dataset had a disparate impact of "
                f"{dataset_dir:.2f}, but the model increased it to {model_dir:.2f}. "
                f"This means the model learned and amplified existing biases in the training data."
            )
        elif amplification_score < -0.05:
            verdict = "Model REDUCED bias"
            explanation = (
                f"The model actually reduced bias! The dataset had a disparate impact of "
                f"{dataset_dir:.2f}, but the model improved it to {model_dir:.2f}. "
                f"This is good - the model is more fair than the data it was trained on."
            )
        else:
            verdict = "Model MAINTAINED bias level"
            explanation = (
                f"The model neither amplified nor reduced bias. Both dataset and model show "
                f"similar disparate impact (~{model_dir:.2f}). The model learned the bias "
                f"but didn't make it worse."
            )
    else:
        amplification_score = None
        verdict = "No dataset audit available"
        explanation = (
            "Cannot determine if model amplified bias without a dataset audit. "
            "Run a dataset audit first to compare model bias against data bias."
        )
    
    return {
        "dataset_dir": dataset_dir,
        "model_dir": model_dir,
        "amplification_score": amplification_score,
        "verdict": verdict,
        "explanation": explanation,
    }


def _analyze_group_performance_gaps(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze performance gaps between demographic groups."""
    gaps = []
    
    per_group = report.get("results", {}).get("per_group_metrics", {})
    
    for attribute, groups in per_group.items():
        group_names = list(groups.keys())
        
        # Compare first group (often privileged) with others
        if len(group_names) < 2:
            continue
        
        privileged_group = group_names[0]
        priv_metrics = groups[privileged_group]
        
        for unprivileged_group in group_names[1:]:
            unpriv_metrics = groups[unprivileged_group]
            
            # Calculate gaps
            accuracy_gap = priv_metrics.get("accuracy", 0) - unpriv_metrics.get("accuracy", 0)
            fpr_gap = unpriv_metrics.get("fpr", 0) - priv_metrics.get("fpr", 0)
            fnr_gap = unpriv_metrics.get("fnr", 0) - priv_metrics.get("fnr", 0)
            
            # Determine severity
            max_gap = max(abs(accuracy_gap), abs(fpr_gap), abs(fnr_gap))
            if max_gap > 0.15:
                severity = "CRITICAL"
            elif max_gap > 0.10:
                severity = "MODERATE"
            else:
                severity = "LOW"
            
            # Plain English explanation
            if fpr_gap > 0.05:
                plain_english = (
                    f"{unprivileged_group} is {fpr_gap:.1%} more likely to be falsely rejected "
                    f"than {privileged_group}. This means qualified {unprivileged_group} individuals "
                    f"are being incorrectly denied at a higher rate."
                )
            elif fnr_gap > 0.05:
                plain_english = (
                    f"{unprivileged_group} is {fnr_gap:.1%} more likely to be falsely approved "
                    f"than {privileged_group}. This means unqualified {unprivileged_group} individuals "
                    f"are being incorrectly approved at a higher rate."
                )
            elif accuracy_gap > 0.05:
                plain_english = (
                    f"The model is {abs(accuracy_gap):.1%} less accurate for {unprivileged_group} "
                    f"than {privileged_group}. This means the model makes more mistakes overall "
                    f"for {unprivileged_group}."
                )
            else:
                plain_english = f"Performance is similar between {privileged_group} and {unprivileged_group}."
            
            gaps.append({
                "attribute": attribute,
                "privileged_group": privileged_group,
                "unprivileged_group": unprivileged_group,
                "accuracy_gap": round(accuracy_gap, 4),
                "fpr_gap": round(fpr_gap, 4),
                "fnr_gap": round(fnr_gap, 4),
                "severity": severity,
                "plain_english": plain_english,
            })
    
    return gaps


def _generate_metric_scorecard(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate scorecard for all fairness metrics."""
    scorecard = []
    
    fairness_metrics = report.get("results", {}).get("fairness_metrics", {})
    
    for attribute, metrics in fairness_metrics.items():
        for metric in metrics:
            value = metric.get("value", 0)
            threshold = metric.get("threshold", 0)
            passed = metric.get("passed", False)
            
            # Calculate gap to pass
            if "Disparate Impact" in metric.get("metric_name", ""):
                # For DIR, need to be >= threshold
                gap_to_pass = max(0, threshold - value)
            else:
                # For differences, need to be <= threshold
                gap_to_pass = max(0, abs(value) - threshold)
            
            # Determine severity
            if not passed:
                if gap_to_pass > 0.15 or (value < 0.6 and "Disparate Impact" in metric.get("metric_name", "")):
                    severity = "CRITICAL"
                elif gap_to_pass > 0.05:
                    severity = "MODERATE"
                else:
                    severity = "LOW"
            else:
                severity = "PASS"
            
            scorecard.append({
                "metric": metric.get("metric_name", "Unknown"),
                "attribute": attribute,
                "value": round(value, 4),
                "threshold": threshold,
                "passed": passed,
                "gap_to_pass": round(gap_to_pass, 4),
                "severity": severity,
            })
    
    return scorecard


def _simulate_improvements(report: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate expected improvements from mitigation strategies."""
    health = report.get("health", {})
    findings = report.get("findings", {})
    compliance = report.get("compliance", {})
    
    current_pass_rate = health.get("metrics_summary", {}).get("pass_rate", 0)
    critical_count = health.get("overall_health", {}).get("critical_findings", 0)
    moderate_count = health.get("overall_health", {}).get("moderate_findings", 0)
    is_compliant = compliance.get("compliant", True)
    
    # Current state
    current_state = {
        "pass_rate": current_pass_rate,
        "critical_findings": critical_count,
        "compliance": "PASS" if is_compliant else "FAIL",
        "worst_dir": _get_worst_dir(report),
    }
    
    # Simulate threshold adjustment (post-processing)
    threshold_pass_rate = min(1.0, current_pass_rate + 0.3)  # Typically 30% improvement
    threshold_critical = max(0, critical_count - 2)  # Resolves ~2 critical issues
    threshold_compliant = threshold_pass_rate > 0.7
    
    if_threshold_adjustment = {
        "pass_rate_after": round(threshold_pass_rate, 2),
        "critical_findings_after": threshold_critical,
        "compliance_after": "PASS" if threshold_compliant else "FAIL",
        "requires_retraining": False,
        "accuracy_impact": "Typically <2% accuracy loss",
        "recommended": True,
    }
    
    # Simulate reweighting (pre-processing)
    reweight_pass_rate = min(1.0, current_pass_rate + 0.4)  # Typically 40% improvement
    reweight_critical = max(0, critical_count - 3)  # Resolves ~3 critical issues
    reweight_compliant = reweight_pass_rate > 0.75
    
    if_reweighting = {
        "pass_rate_after": round(reweight_pass_rate, 2),
        "critical_findings_after": reweight_critical,
        "compliance_after": "PASS" if reweight_compliant else "FAIL",
        "requires_retraining": True,
        "accuracy_impact": "1-3% accuracy loss expected",
    }
    
    # Simulate all applied
    all_pass_rate = min(1.0, current_pass_rate + 0.5)  # Combined 50% improvement
    all_critical = 0  # Should resolve all critical
    all_compliant = True
    
    if_all_applied = {
        "pass_rate_after": round(all_pass_rate, 2),
        "critical_findings_after": all_critical,
        "compliance_after": "PASS",
        "recommended": True,
    }
    
    return {
        "current_state": current_state,
        "if_threshold_adjustment": if_threshold_adjustment,
        "if_reweighting": if_reweighting,
        "if_all_applied": if_all_applied,
    }


def _generate_summary_stats(report: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary statistics."""
    health = report.get("health", {})
    findings = report.get("findings", {})
    results = report.get("results", {})
    compliance = report.get("compliance", {})
    
    metrics_summary = health.get("metrics_summary", {})
    overall_health = health.get("overall_health", {})
    
    # Find worst and best performing groups
    per_group = results.get("results", {}).get("per_group_metrics", {})
    worst_group = "Unknown"
    best_group = "Unknown"
    worst_accuracy = 1.0
    best_accuracy = 0.0
    
    for attribute, groups in per_group.items():
        for group_name, metrics in groups.items():
            accuracy = metrics.get("accuracy", 0)
            if accuracy < worst_accuracy:
                worst_accuracy = accuracy
                worst_group = f"{attribute}={group_name}"
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_group = f"{attribute}={group_name}"
    
    # Determine legal risk level
    critical_count = overall_health.get("critical_findings", 0)
    is_compliant = compliance.get("compliant", True)
    
    if not is_compliant:
        legal_risk_level = "CRITICAL"
    elif critical_count > 3:
        legal_risk_level = "HIGH"
    elif critical_count > 0:
        legal_risk_level = "MEDIUM"
    else:
        legal_risk_level = "LOW"
    
    # Determine if retraining required
    retraining_required = critical_count > 2 or not is_compliant
    
    return {
        "total_metrics_tested": metrics_summary.get("total_metrics", 0),
        "metrics_passed": metrics_summary.get("passed_metrics", 0),
        "metrics_failed": metrics_summary.get("failed_metrics", 0),
        "pass_rate": metrics_summary.get("pass_rate", 0),
        "protected_attributes_tested": report.get("config", {}).get("protected_attributes", []),
        "worst_performing_group": worst_group,
        "best_performing_group": best_group,
        "flip_rate": results.get("overall", {}).get("flip_rate", 0),
        "individual_fairness": "PASS" if results.get("overall", {}).get("flip_rate", 0) < 0.05 else "FAIL",
        "legal_risk_level": legal_risk_level,
        "retraining_required": retraining_required,
    }


def _get_worst_dir(report: Dict[str, Any]) -> float:
    """Get worst disparate impact ratio from report."""
    worst_dir = 1.0
    fairness_metrics = report.get("results", {}).get("fairness_metrics", {})
    
    for attr, metrics in fairness_metrics.items():
        for metric in metrics:
            if metric.get("metric_name") == "Disparate Impact Ratio":
                value = metric.get("value", 1.0)
                if abs(1.0 - value) > abs(1.0 - worst_dir):
                    worst_dir = value
    
    return worst_dir


# Export function for easy use
def export_actionable_insights(
    report_path: Union[str, Path],
    output_path: Union[str, Path],
    dataset_audit_path: Optional[Union[str, Path]] = None
) -> None:
    """
    Generate and export actionable insights from model audit report.
    
    Args:
        report_path: Path to model_audit_comprehensive.json
        output_path: Path to save actionable insights JSON
        dataset_audit_path: Optional path to dataset audit for bias amplification analysis
    """
    insights = interpret_model_audit_report(report_path, dataset_audit_path)
    
    with open(output_path, 'w') as f:
        json.dump(insights, f, indent=2)
    
    print(f"✓ Actionable insights exported to: {output_path}")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python interpreter.py <model_audit_comprehensive.json> <output.json> [dataset_audit_comprehensive.json]")
        sys.exit(1)
    
    report_path = sys.argv[1]
    output_path = sys.argv[2]
    dataset_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    export_actionable_insights(report_path, output_path, dataset_path)
