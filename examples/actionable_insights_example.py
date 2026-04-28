"""
Example: Generate Actionable Insights from Model Audit Report

This example demonstrates how to generate plain-English actionable insights
from a model audit report for business users and frontend applications.
"""
import sys
import json
from pathlib import Path

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'library'))

from model_audit.interpreter import interpret_model_audit_report, export_actionable_insights


def example_generate_insights():
    """Generate actionable insights from existing audit report."""
    print("=" * 80)
    print("GENERATING ACTIONABLE INSIGHTS FROM MODEL AUDIT")
    print("=" * 80)
    
    # Path to existing comprehensive audit report
    report_path = Path(__file__).parent.parent / "output" / "model_audit_comprehensive.json"
    
    if not report_path.exists():
        print(f"\n❌ Report not found: {report_path}")
        print("Please run model_audit_example.py first to generate a report.")
        return
    
    print(f"\n📄 Loading report from: {report_path}")
    
    # Generate actionable insights
    print("\n🔄 Generating actionable insights...")
    insights = interpret_model_audit_report(report_path)
    
    # Display insights
    print("\n" + "=" * 80)
    print("ACTIONABLE INSIGHTS")
    print("=" * 80)
    
    # Plain English Section
    print("\n📝 PLAIN ENGLISH SUMMARY")
    print("-" * 80)
    plain = insights["plain_english"]
    print(f"\n🎯 One-Liner:")
    print(f"   {plain['one_liner']}")
    print(f"\n🔴 Biggest Problem:")
    print(f"   {plain['biggest_problem']}")
    print(f"\n👥 What This Means for Users:")
    print(f"   {plain['what_this_means_for_users']}")
    print(f"\n⚖️ Legal Risk:")
    print(f"   {plain['legal_risk']}")
    print(f"\n⚡ Quickest Fix:")
    print(f"   {plain['quickest_fix']}")
    
    # Action Priority
    print("\n\n📋 PRIORITIZED ACTIONS")
    print("-" * 80)
    for action in insights["action_priority"]:
        print(f"\n#{action['rank']} - {action['action'].split(':')[0]}")
        print(f"   Effort: {action['effort']} | Impact: {action['impact']} | Retraining: {'Yes' if action['requires_retraining'] else 'No'}")
        print(f"   Why: {action['reason']}")
        print(f"   Expected: {action['expected_metric_improvement']}")
        if action['do_this_first']:
            print(f"   ⭐ DO THIS FIRST")
    
    # Bias Amplification
    print("\n\n📊 BIAS AMPLIFICATION ANALYSIS")
    print("-" * 80)
    amp = insights["bias_amplification"]
    print(f"Verdict: {amp['verdict']}")
    print(f"Explanation: {amp['explanation']}")
    if amp['dataset_dir'] is not None:
        print(f"Dataset DIR: {amp['dataset_dir']:.4f}")
    print(f"Model DIR: {amp['model_dir']:.4f}")
    if amp['amplification_score'] is not None:
        print(f"Amplification Score: {amp['amplification_score']:.4f}")
    
    # Group Performance Gaps
    print("\n\n📈 GROUP PERFORMANCE GAPS")
    print("-" * 80)
    for gap in insights["group_performance_gaps"][:5]:  # Show top 5
        print(f"\n[{gap['severity']}] {gap['attribute']}: {gap['privileged_group']} vs {gap['unprivileged_group']}")
        print(f"   Accuracy Gap: {gap['accuracy_gap']:.4f}")
        print(f"   FPR Gap: {gap['fpr_gap']:.4f}")
        print(f"   FNR Gap: {gap['fnr_gap']:.4f}")
        print(f"   📝 {gap['plain_english']}")
    
    # Metric Scorecard
    print("\n\n📊 METRIC SCORECARD")
    print("-" * 80)
    failed_metrics = [m for m in insights["metric_scorecard"] if not m["passed"]]
    print(f"Failed Metrics: {len(failed_metrics)}/{len(insights['metric_scorecard'])}")
    for metric in failed_metrics[:5]:  # Show top 5 failures
        status = "✓" if metric["passed"] else "✗"
        print(f"{status} [{metric['severity']}] {metric['metric']} ({metric['attribute']})")
        print(f"   Value: {metric['value']:.4f} | Threshold: {metric['threshold']} | Gap: {metric['gap_to_pass']:.4f}")
    
    # Simulated Improvements
    print("\n\n🔮 SIMULATED IMPROVEMENTS")
    print("-" * 80)
    sim = insights["simulated_improvements"]
    
    print("\nCurrent State:")
    print(f"   Pass Rate: {sim['current_state']['pass_rate']:.1%}")
    print(f"   Critical Findings: {sim['current_state']['critical_findings']}")
    print(f"   Compliance: {sim['current_state']['compliance']}")
    
    print("\nIf Threshold Adjustment Applied:")
    print(f"   Pass Rate: {sim['if_threshold_adjustment']['pass_rate_after']:.1%} (↑{(sim['if_threshold_adjustment']['pass_rate_after'] - sim['current_state']['pass_rate']):.1%})")
    print(f"   Critical Findings: {sim['if_threshold_adjustment']['critical_findings_after']}")
    print(f"   Compliance: {sim['if_threshold_adjustment']['compliance_after']}")
    print(f"   Accuracy Impact: {sim['if_threshold_adjustment']['accuracy_impact']}")
    print(f"   Recommended: {'✓ YES' if sim['if_threshold_adjustment']['recommended'] else '✗ NO'}")
    
    print("\nIf Reweighting Applied:")
    print(f"   Pass Rate: {sim['if_reweighting']['pass_rate_after']:.1%} (↑{(sim['if_reweighting']['pass_rate_after'] - sim['current_state']['pass_rate']):.1%})")
    print(f"   Critical Findings: {sim['if_reweighting']['critical_findings_after']}")
    print(f"   Compliance: {sim['if_reweighting']['compliance_after']}")
    print(f"   Accuracy Impact: {sim['if_reweighting']['accuracy_impact']}")
    
    print("\nIf All Mitigations Applied:")
    print(f"   Pass Rate: {sim['if_all_applied']['pass_rate_after']:.1%} (↑{(sim['if_all_applied']['pass_rate_after'] - sim['current_state']['pass_rate']):.1%})")
    print(f"   Critical Findings: {sim['if_all_applied']['critical_findings_after']}")
    print(f"   Compliance: {sim['if_all_applied']['compliance_after']}")
    print(f"   Recommended: {'✓ YES' if sim['if_all_applied']['recommended'] else '✗ NO'}")
    
    # Summary Stats
    print("\n\n📊 SUMMARY STATISTICS")
    print("-" * 80)
    stats = insights["summary_stats"]
    print(f"Total Metrics Tested: {stats['total_metrics_tested']}")
    print(f"Metrics Passed: {stats['metrics_passed']}")
    print(f"Metrics Failed: {stats['metrics_failed']}")
    print(f"Pass Rate: {stats['pass_rate']:.1%}")
    print(f"Protected Attributes: {', '.join(stats['protected_attributes_tested'])}")
    print(f"Worst Performing Group: {stats['worst_performing_group']}")
    print(f"Best Performing Group: {stats['best_performing_group']}")
    print(f"Flip Rate: {stats['flip_rate']:.2%}")
    print(f"Individual Fairness: {stats['individual_fairness']}")
    print(f"Legal Risk Level: {stats['legal_risk_level']}")
    print(f"Retraining Required: {'Yes' if stats['retraining_required'] else 'No'}")
    
    # Export to file
    output_path = Path(__file__).parent.parent / "output" / "model_audit_actionable_insights.json"
    print(f"\n\n💾 Exporting insights to: {output_path}")
    
    with open(output_path, 'w') as f:
        json.dump(insights, f, indent=2)
    
    print("✓ Actionable insights exported successfully!")
    
    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETE")
    print("=" * 80)
    print("\nGenerated files:")
    print(f"  - {output_path}")
    print("\nThis JSON can be consumed by:")
    print("  - Frontend dashboards")
    print("  - Business intelligence tools")
    print("  - Compliance reporting systems")
    print("  - Executive summaries")


def example_with_dataset_audit():
    """Generate insights with dataset audit for bias amplification analysis."""
    print("\n\n" + "=" * 80)
    print("GENERATING INSIGHTS WITH BIAS AMPLIFICATION ANALYSIS")
    print("=" * 80)
    
    model_report_path = Path(__file__).parent.parent / "output" / "model_audit_comprehensive.json"
    dataset_report_path = Path(__file__).parent.parent / "output" / "dataset_audit_comprehensive.json"
    
    if not model_report_path.exists():
        print(f"\n❌ Model report not found: {model_report_path}")
        return
    
    if not dataset_report_path.exists():
        print(f"\n⚠️ Dataset report not found: {dataset_report_path}")
        print("Bias amplification analysis will be limited.")
        dataset_report_path = None
    
    # Generate insights with dataset audit
    print("\n🔄 Generating insights with bias amplification analysis...")
    insights = interpret_model_audit_report(model_report_path, dataset_report_path)
    
    # Display bias amplification
    print("\n📊 BIAS AMPLIFICATION ANALYSIS")
    print("-" * 80)
    amp = insights["bias_amplification"]
    print(f"Verdict: {amp['verdict']}")
    print(f"Explanation: {amp['explanation']}")
    
    if amp['dataset_dir'] is not None:
        print(f"\nDataset Disparate Impact: {amp['dataset_dir']:.4f}")
        print(f"Model Disparate Impact: {amp['model_dir']:.4f}")
        print(f"Amplification Score: {amp['amplification_score']:.4f}")
        
        if amp['amplification_score'] > 0:
            print("\n⚠️ WARNING: Model amplified bias from training data!")
            print("   Recommendation: Apply pre-processing techniques to training data")
        elif amp['amplification_score'] < 0:
            print("\n✓ GOOD: Model reduced bias from training data!")
            print("   The model is more fair than the data it was trained on")
    
    # Export
    output_path = Path(__file__).parent.parent / "output" / "model_audit_actionable_insights_with_amplification.json"
    with open(output_path, 'w') as f:
        json.dump(insights, f, indent=2)
    
    print(f"\n✓ Insights with amplification analysis saved to: {output_path}")


if __name__ == "__main__":
    # Run examples
    example_generate_insights()
    example_with_dataset_audit()
