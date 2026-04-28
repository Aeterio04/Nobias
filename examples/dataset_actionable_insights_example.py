"""
Example: Generate Actionable Insights from Dataset Audit

This example shows how to generate plain-English actionable insights
from a dataset audit report, including:
- Plain English summaries for non-technical users
- Prioritized action items
- Improvement checklist
- Column risk scores
- Simulated improvement scenarios
"""

import json
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from library.dataset_audit import audit_dataset
from library.dataset_audit.report import generate_report


def main():
    print("=" * 80)
    print("DATASET AUDIT - ACTIONABLE INSIGHTS EXAMPLE")
    print("=" * 80)
    
    # Run dataset audit
    print("\n[1/3] Running dataset audit...")
    report = audit_dataset(
        data='test_data_biased.csv',
        protected_attributes=['gender', 'race'],
        target_column='hired',
        positive_value=1
    )
    
    print(f"✓ Audit complete: {report.overall_severity} severity")
    print(f"  - {len([f for f in report.findings if f.severity == 'CRITICAL'])} critical findings")
    print(f"  - {len([f for f in report.findings if f.severity == 'MODERATE'])} moderate findings")
    
    # Generate full report with actionable insights
    print("\n[2/3] Generating actionable insights...")
    full_report = generate_report(report)
    
    # Extract actionable insights
    insights = full_report.get('actionable_insights', {})
    
    # Display plain English summary
    print("\n" + "=" * 80)
    print("PLAIN ENGLISH SUMMARY")
    print("=" * 80)
    
    plain_english = insights.get('plain_english', {})
    print(f"\n📌 ONE-LINER:")
    print(f"   {plain_english.get('one_liner', 'N/A')}")
    
    print(f"\n🚨 BIGGEST PROBLEM:")
    print(f"   {plain_english.get('biggest_problem', 'N/A')}")
    
    print(f"\n⚖️  LEGAL RISK:")
    print(f"   {plain_english.get('legal_risk', 'N/A')}")
    
    print(f"\n⚡ QUICKEST FIX:")
    print(f"   {plain_english.get('quickest_fix', 'N/A')}")
    
    # Display action priority
    print("\n" + "=" * 80)
    print("PRIORITIZED ACTIONS")
    print("=" * 80)
    
    actions = insights.get('action_priority', [])
    for action in actions[:3]:  # Show top 3
        print(f"\n#{action['rank']} - {action['action']}")
        print(f"   Effort: {action['effort']} | Impact: {action['impact']}")
        if action.get('do_this_first'):
            print(f"   ⭐ DO THIS FIRST")
        print(f"   Reason: {action['reason']}")
    
    # Display column risks
    print("\n" + "=" * 80)
    print("HIGH-RISK COLUMNS")
    print("=" * 80)
    
    column_risks = insights.get('column_risk_scores', [])
    high_risk = [c for c in column_risks if c['risk_level'] == 'HIGH'][:5]
    
    for col in high_risk:
        print(f"\n🔴 {col['column']} (Risk Score: {col['risk_score']}/10)")
        print(f"   Action: {col['action']}")
        print(f"   Reason: {col['action_reason']}")
    
    # Display simulated improvements
    print("\n" + "=" * 80)
    print("SIMULATED IMPROVEMENTS")
    print("=" * 80)
    
    simulations = insights.get('simulated_improvements', {})
    current = simulations.get('current_state', {})
    
    print(f"\n📊 CURRENT STATE:")
    print(f"   Health Score: {current.get('health_score', 'N/A')}/100")
    print(f"   Disparate Impact Ratio: {current.get('dir', 'N/A')}")
    print(f"   Critical Findings: {current.get('critical_findings', 'N/A')}")
    print(f"   Compliance: {current.get('compliance', 'N/A')}")
    
    if_reweight = simulations.get('if_reweighting_applied')
    if if_reweight:
        print(f"\n✨ IF REWEIGHTING APPLIED:")
        print(f"   Health Score: {current.get('health_score', 0)} → {if_reweight.get('health_score_after', 'N/A')}")
        print(f"   DIR: {current.get('dir', 0):.2f} → {if_reweight.get('dir_after', 'N/A')}")
        print(f"   Findings Resolved: {if_reweight.get('findings_resolved', 'N/A')}")
        print(f"   Compliance: {current.get('compliance', 'N/A')} → {if_reweight.get('compliance_after', 'N/A')}")
    
    if_all = simulations.get('if_all_applied')
    if if_all:
        print(f"\n🎯 IF ALL STRATEGIES APPLIED:")
        print(f"   Health Score: {current.get('health_score', 0)} → {if_all.get('health_score_after', 'N/A')}")
        print(f"   DIR: {current.get('dir', 0):.2f} → {if_all.get('dir_after', 'N/A')}")
        print(f"   Findings Resolved: {if_all.get('findings_resolved', 'N/A')}/{current.get('critical_findings', 0) + len([f for f in report.findings if f.severity == 'MODERATE'])}")
        print(f"   Compliance: {if_all.get('compliance_after', 'N/A')}")
        if if_all.get('recommended'):
            print(f"   ⭐ RECOMMENDED APPROACH")
    
    # Display summary stats
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    summary = insights.get('summary_stats', {})
    print(f"\n📊 Columns at Risk: {summary.get('total_columns_at_risk', 'N/A')}")
    print(f"   - To Remove: {summary.get('columns_to_remove', 'N/A')}")
    print(f"   - To Monitor: {summary.get('columns_to_monitor', 'N/A')}")
    print(f"\n⏱️  Estimated Fix Time: {summary.get('estimated_fix_time', 'N/A')}")
    print(f"🔄 Retraining Required: {summary.get('retraining_required', 'N/A')}")
    print(f"⚖️  Legal Risk Level: {summary.get('legal_risk_level', 'N/A')}")
    
    # Save full insights to JSON
    print("\n[3/3] Saving actionable insights...")
    output_path = Path('output/dataset_actionable_insights.json')
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(insights, f, indent=2)
    
    print(f"✓ Saved to: {output_path}")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print("\nThe actionable insights JSON contains:")
    print("  - plain_english: Non-technical summaries")
    print("  - action_priority: Ranked action items")
    print("  - improvement_checklist: Task-by-task checklist")
    print("  - column_risk_scores: Risk assessment for each column")
    print("  - simulated_improvements: Before/after scenarios")
    print("  - summary_stats: Overall statistics")
    print("\nThis JSON can be consumed by your frontend for visualization!")


if __name__ == '__main__':
    main()
