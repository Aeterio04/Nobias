# Model Audit System - Visual Summary

> **A visual guide to understanding the model audit architecture and workflows**

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOBIAS MODEL AUDIT                            │
│                                                                  │
│  Comprehensive Fairness Testing for ML Models                   │
│  • Group + Individual + Intersectional • Legally defensible     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      6-STEP PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│  Step 1: Model & Data Loading                                   │
│  └─ Load model + test data + validate                          │
├─────────────────────────────────────────────────────────────────┤
│  Step 2: Baseline Predictions                                   │
│  └─ Get predictions + compute overall metrics                  │
├─────────────────────────────────────────────────────────────────┤
│  Step 3: Counterfactual Testing                                 │
│  └─ Flip protected attributes + count prediction changes       │
├─────────────────────────────────────────────────────────────────┤
│  Step 4: Group Fairness Metrics                                 │
│  └─ Demographic parity + equalized odds + EEOC compliance      │
├─────────────────────────────────────────────────────────────────┤
│  Step 5: Intersectional Analysis                                │
│  └─ Detect compounded bias across multiple attributes          │
├─────────────────────────────────────────────────────────────────┤
│  Step 6: Mitigation Recommendations                             │
│  └─ Generate concrete remediation strategies                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MODEL AUDIT REPORT                            │
│  • Findings with severity                                       │
│  • EEOC compliance status                                       │
│  • Mitigation options with code                                 │
│  • Tamper-evident audit trail                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Input Formats

```
┌──────────────────────────────────────────────────────────────┐
│                    SUPPORTED INPUTS                           │
└──────────────────────────────────────────────────────────────┘

MODEL INPUT
┌─────────────────────────────────────┐
│  File Path:                         │
│  • .pkl (pickle)                    │
│  • .joblib                          │
│                                     │
│  In-Memory Object:                  │
│  • Any sklearn-compatible model     │
│  • Must have predict() method       │
│  • Binary/multiclass: predict_proba│
└─────────────────────────────────────┘

TEST DATA INPUT
┌─────────────────────────────────────┐
│  File Path:                         │
│  • .csv                             │
│  • .xlsx, .xls                      │
│  • .parquet                         │
│                                     │
│  In-Memory:                         │
│  • pandas DataFrame                 │
│                                     │
│  Must Include:                      │
│  • All model features               │
│  • Protected attributes             │
│  • Target column                    │
└─────────────────────────────────────┘
```

---

## Fairness Metrics

```
┌──────────────────────────────────────────────────────────────┐
│                    METRICS COMPUTED                           │
└──────────────────────────────────────────────────────────────┘

GROUP FAIRNESS
┌─────────────────────────────────────────────────────────────┐
│  Demographic Parity                                          │
│  ├─ Equal approval rates across groups                      │
│  └─ Threshold: DPD < 0.10                                   │
│                                                              │
│  Equalized Odds                                              │
│  ├─ Equal TPR and FPR across groups                         │
│  └─ Threshold: Difference < 0.10                            │
│                                                              │
│  Disparate Impact (EEOC 80% Rule)                           │
│  ├─ DIR = min_rate / max_rate                               │
│  └─ Threshold: DIR >= 0.80 (LEGAL REQUIREMENT)              │
│                                                              │
│  Predictive Parity                                           │
│  ├─ Equal precision across groups                           │
│  └─ Threshold: Difference < 0.05                            │
│                                                              │
│  Calibration                                                 │
│  ├─ Predicted probabilities match outcomes                  │
│  └─ Threshold: Error < 0.05                                 │
└─────────────────────────────────────────────────────────────┘

INDIVIDUAL FAIRNESS
┌─────────────────────────────────────────────────────────────┐
│  Counterfactual Flip Rate                                    │
│  ├─ % predictions that change when only demographics change │
│  └─ Threshold: < 2% excellent, < 5% acceptable              │
│                                                              │
│  Mean Absolute Score Difference (MASD)                       │
│  ├─ Average score shift in counterfactuals                  │
│  └─ Threshold: < 0.05                                       │
└─────────────────────────────────────────────────────────────┘

INTERSECTIONAL
┌─────────────────────────────────────────────────────────────┐
│  Intersectional Disparity                                    │
│  ├─ Compounded bias for multiple attributes                 │
│  └─ Detects superadditive discrimination                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Severity Classification

```
┌──────────────────────────────────────────────────────────────┐
│                    SEVERITY LEVELS                            │
└──────────────────────────────────────────────────────────────┘

CRITICAL
┌─────────────────────────────────────┐
│  Thresholds:                        │
│  • DPD > 0.20                       │
│  • DIR < 0.60                       │
│  • Flip Rate > 15%                  │
│                                     │
│  Action: IMMEDIATE REMEDIATION      │
│  Risk: Legal liability              │
└─────────────────────────────────────┘

MODERATE
┌─────────────────────────────────────┐
│  Thresholds:                        │
│  • DPD 0.10-0.20                    │
│  • DIR 0.60-0.80                    │
│  • Flip Rate 5-15%                  │
│                                     │
│  Action: Remediation recommended    │
│  Risk: Compliance issues            │
└─────────────────────────────────────┘

LOW
┌─────────────────────────────────────┐
│  Thresholds:                        │
│  • DPD 0.05-0.10                    │
│  • DIR 0.80-0.90                    │
│  • Flip Rate 2-5%                   │
│                                     │
│  Action: Monitor                    │
│  Risk: Minor bias                   │
└─────────────────────────────────────┘

CLEAR
┌─────────────────────────────────────┐
│  Thresholds:                        │
│  • DPD < 0.05                       │
│  • DIR > 0.90                       │
│  • Flip Rate < 2%                   │
│                                     │
│  Action: None needed                │
│  Risk: Negligible                   │
└─────────────────────────────────────┘
```

---

## Workflow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    TYPICAL WORKFLOW                           │
└──────────────────────────────────────────────────────────────┘

START
  │
  ▼
┌─────────────────────────────────────┐
│  1. Train Model                     │
│     • sklearn, XGBoost, LightGBM    │
│     • Save as .pkl                  │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│  2. Prepare Test Data               │
│     • Include protected attributes  │
│     • Include target column         │
│     • Save as .csv                  │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│  3. Run Audit                       │
│     audit_model(                    │
│       model='model.pkl',            │
│       test_data='test.csv',         │
│       protected_attributes=[...],   │
│       target_column='...',          │
│       positive_value=1              │
│     )                               │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│  4. Review Findings                 │
│     • Check overall_severity        │
│     • Review critical findings      │
│     • Check EEOC compliance         │
└─────────────────────────────────────┘
  │
  ├─ CLEAR/LOW ──────────────────────┐
  │                                   │
  │                                   ▼
  │                          ┌─────────────────┐
  │                          │  5. Deploy      │
  │                          │     Model       │
  │                          └─────────────────┘
  │
  ├─ MODERATE/CRITICAL ──────────────┐
  │                                   │
  │                                   ▼
  │                          ┌─────────────────┐
  │                          │  5. Apply       │
  │                          │     Mitigation  │
  │                          └─────────────────┘
  │                                   │
  │                                   ▼
  │                          ┌─────────────────┐
  │                          │  6. Re-Audit    │
  │                          └─────────────────┘
  │                                   │
  └───────────────────────────────────┘
```

---

## Mitigation Strategies

```
┌──────────────────────────────────────────────────────────────┐
│                    REMEDIATION OPTIONS                        │
└──────────────────────────────────────────────────────────────┘

POST-PROCESSING (No Retraining)
┌─────────────────────────────────────────────────────────────┐
│  Threshold Adjustment                                        │
│  ├─ Adjust decision thresholds per group                    │
│  ├─ Complexity: LOW                                         │
│  ├─ Impact: Can achieve equalized odds                      │
│  └─ Code: fairlearn.postprocessing.ThresholdOptimizer      │
└─────────────────────────────────────────────────────────────┘

PRE-PROCESSING (Requires Retraining)
┌─────────────────────────────────────────────────────────────┐
│  Sample Reweighting                                          │
│  ├─ Assign fairness-aware weights to training samples       │
│  ├─ Complexity: MEDIUM                                      │
│  ├─ Impact: Moderate improvement, 1-3% accuracy loss        │
│  └─ Code: fairlearn.reductions.ExponentiatedGradient       │
│                                                              │
│  Remove Proxy Features                                       │
│  ├─ Drop features correlated with protected attributes      │
│  ├─ Complexity: LOW                                         │
│  ├─ Impact: Reduces individual fairness violations          │
│  └─ Code: df.drop(columns=proxy_features)                  │
└─────────────────────────────────────────────────────────────┘

IN-PROCESSING (Requires Retraining)
┌─────────────────────────────────────────────────────────────┐
│  Fairness Constraints                                        │
│  ├─ Add fairness constraints during training                │
│  ├─ Complexity: HIGH                                        │
│  ├─ Impact: Strong fairness guarantees                      │
│  └─ Code: fairlearn.reductions with constraints             │
└─────────────────────────────────────────────────────────────┘
```

---

## Output Structure

```
┌──────────────────────────────────────────────────────────────┐
│                    AUDIT REPORT                               │
└──────────────────────────────────────────────────────────────┘

ModelAuditReport
├─ audit_id: "model_audit_a1b2c3d4"
├─ timestamp: "2026-04-26T10:30:00Z"
├─ duration_seconds: 15.32
│
├─ Configuration
│  ├─ model_name: "RandomForestClassifier"
│  ├─ model_type: "binary_classifier"
│  ├─ test_sample_count: 2000
│  └─ protected_attributes: ["gender", "race"]
│
├─ Severity
│  └─ overall_severity: "MODERATE"
│
├─ Core Results
│  ├─ scorecard: {metric_name: MetricResult}
│  ├─ counterfactual_result: CounterfactualResult
│  ├─ findings: [ModelFinding]
│  └─ mitigation_options: [MitigationOption]
│
├─ Optional Analyses
│  ├─ intersectional_findings: [IntersectionalFinding]
│  └─ shap_analysis: SHAPAnalysis
│
├─ Metadata
│  ├─ baseline_metrics: {accuracy, f1, ...}
│  └─ per_group_metrics: {group: metrics}
│
└─ FairSight Compliance
   ├─ audit_integrity: ModelIntegrity (SHA-256 hashes)
   ├─ model_fingerprint: ModelFingerprint
   └─ confidence_intervals: {metric: CI}
```

---

## Quick Reference

```
┌──────────────────────────────────────────────────────────────┐
│                    CHEAT SHEET                                │
└──────────────────────────────────────────────────────────────┘

BASIC AUDIT
from nobias.model_audit import audit_model
report = audit_model(
    model='model.pkl',
    test_data='test.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

CHECK SEVERITY
print(report.overall_severity.value)
# CRITICAL | MODERATE | LOW | CLEAR

CHECK EEOC COMPLIANCE
for key, metric in report.scorecard.items():
    if 'disparate_impact' in key:
        if metric.value < 0.80:
            print(f"⚠️ EEOC VIOLATION: {metric.value:.2f}")

GET CRITICAL FINDINGS
critical = report.get_critical_findings()
for finding in critical:
    print(f"[{finding.severity.value}] {finding.title}")

EXPORT REPORT
report.export('audit.json', format='json')
report.export('audit.txt', format='text')

APPLY MITIGATION
for option in report.mitigation_options:
    print(f"{option.strategy_name}: {option.description}")
    if option.code_example:
        print(option.code_example)
```

---

## Performance

```
┌──────────────────────────────────────────────────────────────┐
│                    TYPICAL PERFORMANCE                        │
└──────────────────────────────────────────────────────────────┘

Dataset Size: 2,000 samples
Protected Attributes: 2 (gender, race)
Model: RandomForestClassifier

┌─────────────────────────────────────┐
│  Execution Time: 15-30 seconds      │
│  ├─ Loading: 1s                     │
│  ├─ Baseline: 2s                    │
│  ├─ Counterfactual: 5s              │
│  ├─ Group Fairness: 5s              │
│  ├─ Intersectional: 2s              │
│  └─ Report Generation: 1s           │
│                                     │
│  Memory Usage: < 500 MB             │
│  CPU Usage: 1-4 cores               │
└─────────────────────────────────────┘

Scales linearly with:
• Number of samples
• Number of protected attributes
• Model complexity
```

---

## Integration Points

```
┌──────────────────────────────────────────────────────────────┐
│                    WHERE TO INTEGRATE                         │
└──────────────────────────────────────────────────────────────┘

CI/CD PIPELINE
┌─────────────────────────────────────┐
│  def test_model_fairness():         │
│      report = audit_model(...)      │
│      assert report.overall_severity │
│             not in ['CRITICAL']     │
└─────────────────────────────────────┘

MODEL REGISTRY
┌─────────────────────────────────────┐
│  Before registering model:          │
│  1. Run audit                       │
│  2. Store audit_id with model      │
│  3. Attach audit report             │
└─────────────────────────────────────┘

DEPLOYMENT GATE
┌─────────────────────────────────────┐
│  if report.overall_severity in      │
│     ['CRITICAL', 'MODERATE']:       │
│      block_deployment()             │
│  else:                              │
│      approve_deployment()           │
└─────────────────────────────────────┘

MONITORING
┌─────────────────────────────────────┐
│  Schedule periodic audits:          │
│  • Weekly on production model       │
│  • After retraining                 │
│  • When data distribution shifts    │
└─────────────────────────────────────┘
```

---

## Next Steps

1. **Quick Start**: See [MODEL_AUDIT_QUICK_START.md](niru_MODEL_AUDIT_QUICK_START.md)
2. **Full Guide**: See [MODEL_AUDIT_IMPLEMENTATION_GUIDE.md](niru_MODEL_AUDIT_IMPLEMENTATION_GUIDE.md)
3. **Examples**: Check `examples/model_audit_example.py`
4. **API Reference**: See `API_REFERENCE.md`
