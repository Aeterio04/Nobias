# Dataset Audit System - Visual Summary

> **A visual guide to understanding the dataset audit architecture and workflows**

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOBIAS DATASET AUDIT                          │
│                                                                  │
│  Preventive Bias Detection for Training Data                    │
│  • 7 bias types • Fast (seconds) • Privacy-friendly             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      7-PHASE PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: Data Ingestion & Validation                           │
│  └─ Load + validate + basic statistics                         │
├─────────────────────────────────────────────────────────────────┤
│  Phase 2: Representation Analysis                               │
│  └─ Count groups + compute balance scores                      │
├─────────────────────────────────────────────────────────────────┤
│  Phase 3: Label Bias Analysis                                   │
│  └─ Selection rates + EEOC compliance                          │
├─────────────────────────────────────────────────────────────────┤
│  Phase 4: Proxy Feature Detection                               │
│  └─ Correlation + mutual information                           │
├─────────────────────────────────────────────────────────────────┤
│  Phase 5: Missing Data Analysis                                 │
│  └─ Systematic missingness patterns                            │
├─────────────────────────────────────────────────────────────────┤
│  Phase 6: Intersectional Disparity Analysis                     │
│  └─ Compounded underrepresentation                             │
├─────────────────────────────────────────────────────────────────┤
│  Phase 7: Distribution Shift Analysis                           │
│  └─ KL divergence across groups                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATASET AUDIT REPORT                          │
│  • Findings with severity                                       │
│  • EEOC compliance status                                       │
│  • Remediation strategies                                       │
│  • Tamper-evident audit trail                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Input Formats

```
┌──────────────────────────────────────────────────────────────┐
│                    SUPPORTED INPUTS                           │
└──────────────────────────────────────────────────────────────┘

FILE FORMATS
┌─────────────────────────────────────┐
│  • CSV (.csv)                       │
│  • Excel (.xlsx, .xls)              │
│  • Parquet (.parquet)               │
└─────────────────────────────────────┘

IN-MEMORY
┌─────────────────────────────────────┐
│  • pandas DataFrame                 │
└─────────────────────────────────────┘

REQUIRED COLUMNS
┌─────────────────────────────────────┐
│  • Protected attributes             │
│    (gender, race, age, etc.)        │
│  • Target column                    │
│    (hired, approved, etc.)          │
│  • Feature columns                  │
│    (experience, education, etc.)    │
└─────────────────────────────────────┘
```

---

## Bias Types Detected

```
┌──────────────────────────────────────────────────────────────┐
│                    7 BIAS TYPES                               │
└──────────────────────────────────────────────────────────────┘

1. REPRESENTATION BIAS
┌─────────────────────────────────────────────────────────────┐
│  What: Underrepresented groups in dataset                   │
│  Metric: Representation ratio, balance score                │
│  Threshold: < 10% = underrepresented                        │
│  Example: Female 30% vs Male 70%                            │
└─────────────────────────────────────────────────────────────┘

2. LABEL BIAS
┌─────────────────────────────────────────────────────────────┐
│  What: Different approval rates across demographics         │
│  Metric: Selection Rate Difference (SRD), DIR               │
│  Threshold: SRD > 0.10, DIR < 0.80 (EEOC violation)        │
│  Example: Male 80% approved vs Female 60%                   │
└─────────────────────────────────────────────────────────────┘

3. PROXY FEATURES
┌─────────────────────────────────────────────────────────────┐
│  What: Features that encode protected attributes            │
│  Metric: Correlation, mutual information                    │
│  Threshold: |corr| > 0.3, MI > 0.1                         │
│  Example: first_name reveals gender                         │
└─────────────────────────────────────────────────────────────┘

4. MISSING DATA BIAS
┌─────────────────────────────────────────────────────────────┐
│  What: Systematic missingness by group                      │
│  Metric: Missingness rate difference                        │
│  Threshold: Difference > 0.10                               │
│  Example: Income missing 25% for Black vs 5% for White     │
└─────────────────────────────────────────────────────────────┘

5. INTERSECTIONAL BIAS
┌─────────────────────────────────────────────────────────────┐
│  What: Compounded underrepresentation                       │
│  Metric: Actual vs expected size                            │
│  Threshold: < 50% of expected                               │
│  Example: Black Female 5% vs expected 10%                   │
└─────────────────────────────────────────────────────────────┘

6. DISTRIBUTION SHIFT
┌─────────────────────────────────────────────────────────────┐
│  What: Different feature distributions across groups        │
│  Metric: KL divergence                                      │
│  Threshold: KL > 0.5 = severe shift                        │
│  Example: Credit score mean 720 vs 680                      │
└─────────────────────────────────────────────────────────────┘

7. CORRELATION BIAS
┌─────────────────────────────────────────────────────────────┐
│  What: Features correlated with protected attributes        │
│  Metric: Pearson correlation                                │
│  Threshold: |corr| > 0.3                                   │
│  Example: zip_code correlated with race                     │
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
│  • Representation < 5%              │
│  • SRD > 0.20                       │
│  • DIR < 0.60                       │
│                                     │
│  Action: IMMEDIATE REMEDIATION      │
│  Risk: Legal liability              │
└─────────────────────────────────────┘

MODERATE
┌─────────────────────────────────────┐
│  Thresholds:                        │
│  • Representation 5-10%             │
│  • SRD 0.10-0.20                    │
│  • DIR 0.60-0.80                    │
│                                     │
│  Action: Remediation recommended    │
│  Risk: Compliance issues            │
└─────────────────────────────────────┘

LOW
┌─────────────────────────────────────┐
│  Thresholds:                        │
│  • Representation 10-20%            │
│  • SRD 0.05-0.10                    │
│  • DIR 0.80-0.90                    │
│                                     │
│  Action: Monitor                    │
│  Risk: Minor bias                   │
└─────────────────────────────────────┘

CLEAR
┌─────────────────────────────────────┐
│  Thresholds:                        │
│  • Representation > 20%             │
│  • SRD < 0.05                       │
│  • DIR > 0.90                       │
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
│  1. Collect Training Data           │
│     • From database, files, etc.    │
│     • Include protected attributes  │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│  2. Run Audit                       │
│     audit_dataset(                  │
│       data='data.csv',              │
│       protected_attributes=[...],   │
│       target_column='...',          │
│       positive_value=1              │
│     )                               │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│  3. Review Findings                 │
│     • Check overall_severity        │
│     • Review critical findings      │
│     • Check EEOC compliance         │
│     • Identify proxy features       │
└─────────────────────────────────────┘
  │
  ├─ CLEAR/LOW ──────────────────────┐
  │                                   │
  │                                   ▼
  │                          ┌─────────────────┐
  │                          │  4. Train       │
  │                          │     Model       │
  │                          └─────────────────┘
  │
  ├─ MODERATE/CRITICAL ──────────────┐
  │                                   │
  │                                   ▼
  │                          ┌─────────────────┐
  │                          │  4. Apply       │
  │                          │     Remediation │
  │                          └─────────────────┘
  │                                   │
  │                                   ▼
  │                          ┌─────────────────┐
  │                          │  5. Re-Audit    │
  │                          └─────────────────┘
  │                                   │
  └───────────────────────────────────┘
```

---

## Remediation Strategies

```
┌──────────────────────────────────────────────────────────────┐
│                    REMEDIATION OPTIONS                        │
└──────────────────────────────────────────────────────────────┘

RESAMPLING
┌─────────────────────────────────────────────────────────────┐
│  Stratified Resampling                                       │
│  ├─ Oversample underrepresented groups                      │
│  ├─ Complexity: LOW                                         │
│  ├─ Impact: Balances representation                         │
│  └─ Code: sklearn.utils.resample                           │
└─────────────────────────────────────────────────────────────┘

REWEIGHTING
┌─────────────────────────────────────────────────────────────┐
│  Sample Reweighting                                          │
│  ├─ Assign weights to balance groups                        │
│  ├─ Complexity: LOW                                         │
│  ├─ Impact: Balances without changing data size             │
│  └─ Code: sklearn.utils.class_weight.compute_sample_weight │
└─────────────────────────────────────────────────────────────┘

FEATURE REMOVAL
┌─────────────────────────────────────────────────────────────┐
│  Remove Proxy Features                                       │
│  ├─ Drop features that encode protected attributes          │
│  ├─ Complexity: LOW                                         │
│  ├─ Impact: Reduces proxy bias                              │
│  └─ Code: df.drop(columns=proxy_features)                  │
└─────────────────────────────────────────────────────────────┘

IMPUTATION
┌─────────────────────────────────────────────────────────────┐
│  Fair Imputation                                             │
│  ├─ Fill missing data systematically                        │
│  ├─ Complexity: MEDIUM                                      │
│  ├─ Impact: Reduces missing data bias                       │
│  └─ Code: sklearn.impute.SimpleImputer                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Output Structure

```
┌──────────────────────────────────────────────────────────────┐
│                    AUDIT REPORT                               │
└──────────────────────────────────────────────────────────────┘

DatasetAuditReport
├─ audit_id: "dataset_audit_a1b2c3d4"
├─ timestamp: "2026-04-26T10:30:00Z"
├─ duration_seconds: 2.45
│
├─ Configuration
│  ├─ dataset_name: "training_data.csv"
│  ├─ row_count: 10000
│  ├─ column_count: 15
│  ├─ protected_attributes: ["gender", "race"]
│  ├─ target_column: "hired"
│  └─ positive_value: 1
│
├─ Severity
│  └─ overall_severity: "MODERATE"
│
├─ Findings
│  └─ findings: [DatasetFinding]
│
├─ Analysis Results
│  ├─ representation: {group: {count, ratio}}
│  ├─ label_rates: {attr: {srd, dir}}
│  ├─ proxy_features: [ProxyFeature]
│  ├─ missing_data_matrix: {feature: {group: rate}}
│  ├─ intersectional_disparities: [...]
│  └─ kl_divergences: {feature: {comparison: kl}}
│
├─ Remediation
│  └─ remediation_suggestions: [Remediation]
│
└─ FairSight Compliance
   ├─ audit_integrity: DatasetIntegrity (SHA-256 hashes)
   └─ confidence_intervals: {metric: CI}
```

---

## Quick Reference

```
┌──────────────────────────────────────────────────────────────┐
│                    CHEAT SHEET                                │
└──────────────────────────────────────────────────────────────┘

BASIC AUDIT
from nobias import audit_dataset
report = audit_dataset(
    data='data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

CHECK SEVERITY
print(report.overall_severity)
# CRITICAL | MODERATE | LOW | CLEAR

CHECK EEOC COMPLIANCE
for attr, rates in report.label_rates.items():
    if rates['dir'] < 0.80:
        print(f"⚠️ EEOC VIOLATION: {attr} DIR={rates['dir']:.2f}")

GET CRITICAL FINDINGS
critical = report.get_critical_findings()
for finding in critical:
    print(f"[{finding.severity}] {finding.message}")

CHECK PROXY FEATURES
for proxy in report.proxy_features:
    print(f"{proxy.feature} → {proxy.protected} (score: {proxy.score:.3f})")

EXPORT REPORT
report.export('audit.json', format='json')
report.export('audit.txt', format='text')
report.export('audit.pdf', format='pdf')

APPLY REMEDIATION
for remedy in report.remediation_suggestions:
    print(f"{remedy.strategy}: {remedy.description}")
    print(f"  Expected DIR: {remedy.estimated_dir_after:.2f}")
```

---

## Performance

```
┌──────────────────────────────────────────────────────────────┐
│                    TYPICAL PERFORMANCE                        │
└──────────────────────────────────────────────────────────────┘

Dataset Size: 10,000 rows × 15 columns
Protected Attributes: 2 (gender, race)

┌─────────────────────────────────────┐
│  Execution Time: 2-5 seconds        │
│  ├─ Ingestion: 0.5s                 │
│  ├─ Representation: 0.2s            │
│  ├─ Label Bias: 0.3s                │
│  ├─ Proxy Detection: 1.0s           │
│  ├─ Missing Data: 0.2s              │
│  ├─ Intersectional: 0.5s            │
│  └─ Distribution Shift: 0.3s        │
│                                     │
│  Memory Usage: < 200 MB             │
│  CPU Usage: 1-2 cores               │
└─────────────────────────────────────┘

Scales linearly with:
• Number of rows
• Number of columns
• Number of protected attributes
```

---

## Integration Points

```
┌──────────────────────────────────────────────────────────────┐
│                    WHERE TO INTEGRATE                         │
└──────────────────────────────────────────────────────────────┘

DATA PIPELINE
┌─────────────────────────────────────┐
│  def validate_data(df):             │
│      report = audit_dataset(...)    │
│      if report.overall_severity     │
│         in ['CRITICAL']:            │
│          raise ValueError("Bias")   │
│      return df                      │
└─────────────────────────────────────┘

CI/CD PIPELINE
┌─────────────────────────────────────┐
│  def test_data_fairness():          │
│      report = audit_dataset(...)    │
│      assert report.overall_severity │
│             not in ['CRITICAL']     │
└─────────────────────────────────────┘

DATA VERSIONING
┌─────────────────────────────────────┐
│  Before versioning dataset:         │
│  1. Run audit                       │
│  2. Store audit_id with data       │
│  3. Attach audit report             │
└─────────────────────────────────────┘

AUTOMATED REMEDIATION
┌─────────────────────────────────────┐
│  report = audit_dataset(...)        │
│  if report.overall_severity ==      │
│     'CRITICAL':                     │
│      apply_remediation(             │
│          report.remediation_        │
│          suggestions[0]             │
│      )                              │
└─────────────────────────────────────┘
```

---

## Next Steps

1. **Quick Start**: See [DATASET_AUDIT_QUICK_START.md](niru_DATASET_AUDIT_QUICK_START.md)
2. **Full Guide**: See [DATASET_AUDIT_IMPLEMENTATION_GUIDE.md](niru_DATASET_AUDIT_IMPLEMENTATION_GUIDE.md)
3. **Examples**: Check `examples/dataset_audit_example.py`
4. **API Reference**: See `API_REFERENCE.md`
