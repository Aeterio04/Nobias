"""
Example: How to test the dataset audit system
"""
from nobias import audit_dataset

# Run audit
report = audit_dataset(
    data='test_hiring_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)

# Print results
print("\n" + "="*60)
print("DATASET AUDIT RESULTS")
print("="*60)
print(f"\nAudit ID: {report.audit_id}")
print(f"Overall Severity: {report.overall_severity}")
print(f"Total Findings: {len(report.findings)}")

print(f"\n📊 Critical Findings:")
for finding in report.get_critical_findings():
    print(f"  [{finding.severity}] {finding.message}")

print(f"\n🔍 Proxy Features: {len(report.proxy_features)}")
for proxy in report.proxy_features:
    print(f"  {proxy.feature} → {proxy.protected} (score: {proxy.score:.3f})")

print(f"\n🔧 Remediation Suggestions: {len(report.remediation_suggestions)}")
for remedy in report.remediation_suggestions:
    print(f"  - {remedy.strategy}")

# Export report
report.export('test_dataset_audit_report.json', format='json')
print(f"\n✅ Report exported to 'test_dataset_audit_report.json'")
