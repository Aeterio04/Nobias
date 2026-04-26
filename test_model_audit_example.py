"""
Example: How to test the model audit system
"""
from nobias.model_audit import audit_model

# Run audit
report = audit_model(
    model='test_hiring_model.pkl',
    test_data='test_hiring_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)

# Print results
print("\n" + "="*60)
print("MODEL AUDIT RESULTS")
print("="*60)
print(f"\nAudit ID: {report.audit_id}")
print(f"Overall Severity: {report.overall_severity.value}")
print(f"Counterfactual Flip Rate: {report.counterfactual_result.flip_rate:.2%}")

print(f"\n📊 Findings: {len(report.findings)} total")
for finding in report.findings:
    print(f"  [{finding.severity.value}] {finding.title}")

print(f"\n🔧 Mitigation Options: {len(report.mitigation_options)}")
for option in report.mitigation_options:
    print(f"  - {option.strategy_name} ({option.category})")

# Export report
report.export('test_model_audit_report.json', format='json')
print(f"\n✅ Report exported to 'test_model_audit_report.json'")
