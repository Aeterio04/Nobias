# Dataset Audit System - Complete Implementation Guide

> **A comprehensive guide to understanding and using the NoBias Dataset Audit System**  
> **For data scientists and ML engineers**

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [What We're Building & Why](#what-were-building--why)
3. [Key Concepts](#key-concepts)
4. [System Architecture](#system-architecture)
5. [Implementation Details](#implementation-details)
6. [Example Workflows](#example-workflows)
7. [Input/Output Examples](#inputoutput-examples)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Executive Summary

The NoBias Dataset Audit System is a **production-ready framework** for detecting statistical biases in tabular datasets before model training. It identifies representation imbalances, label bias, proxy features, and intersectional disparities to prevent biased models.

### What Makes This Special

- **Preventive**: Catch bias before training (cheaper than fixing models)
- **Comprehensive**: 7 types of bias detection
- **Actionable**: Concrete remediation strategies (resampling, reweighting, etc.)
- **Fast**: Audits complete in seconds
- **Privacy-Friendly**: All analysis runs locally

### Quick Stats

- **Bias Types Detected**: 7 (representation, label, proxy, missing data, intersectional, distribution shift, correlation)
- **Speed**: 2-10 seconds for typical datasets
- **Compliance**: EU AI Act, NIST AI RMF, ISO/IEC 42001 ready
- **Data Support**: CSV, Excel, Parquet, pandas DataFrame

---

## What We're Building & Why

### The Problem

Biased datasets lead to biased models. Common issues:

1. **Representation Bias**: Underrepresented groups in data
2. **Label Bias**: Different label rates across demographics
3. **Proxy Features**: Features correlated with protected attributes
4. **Missing Data Bias**: Systematic missingness patterns
5. **Intersectional Bias**: Compounded underrepresentation
6. **Distribution Shift**: Different feature distributions across groups
7. **Correlation Bias**: Features that encode protected attributes

Traditional approaches miss these because:
- Manual inspection doesn't scale
- Summary statistics don't reveal bias patterns
- No systematic framework
- No legal defensibility

### Our Solution

A **7-phase pipeline** that:

1. **Ingests** data from multiple formats
2. **Analyzes** representation (group sizes, balance)
3. **Detects** label bias (approval rate disparities)
4. **Identifies** proxy features (correlation + mutual information)
5. **Examines** missing data patterns
6. **Scans** intersectional disparities
7. **Measures** distribution shifts (KL divergence)

### How It Ties to Our Goal

**Goal**: Prevent biased models by fixing datasets first

**How we achieve it**:
- **Prevention**: Catch bias before expensive training
- **Transparency**: Tamper-evident audit trails
- **Actionability**: Concrete remediation strategies

---

## Key Concepts

### Representation Bias

**What it measures**: Are all demographic groups adequately represented?

**Metrics**:
- **Group Size**: Absolute count per group
- **Representation Ratio**: `group_size / total_size`
- **Balance Score**: Ratio of smallest to largest group

**Thresholds**:
- Representation ratio < 0.10 (10%) = Underrepresented
- Balance score < 0.50 = Imbalanced

**Example**:
```
Total: 10,000 samples
Male: 7,000 (70%)
Female: 3,000 (30%)
Balance Score: 3000/7000 = 0.43 → IMBALANCED
```

### Label Bias

**What it measures**: Do different groups have different positive label rates?

**Metrics**:
- **Selection Rate**: `P(Y=1 | A=a)` for each group
- **Selection Rate Difference (SRD)**: `|P(Y=1|A=a) - P(Y=1|A=b)|`
- **Disparate Impact Ratio (DIR)**: `min_rate / max_rate`

**Thresholds**:
- SRD > 0.10 = Significant disparity
- DIR < 0.80 = EEOC violation

**Example**:
```
Male approval rate: 80%
Female approval rate: 60%
SRD: 0.20 (20 percentage points)
DIR: 0.60/0.80 = 0.75 → EEOC VIOLATION
```

### Proxy Features

**What it measures**: Which features encode protected attributes?

**Methods**:
1. **Pearson Correlation**: Linear relationship
2. **Mutual Information**: Non-linear relationship
3. **Predictive Power**: Can feature predict protected attribute?

**Thresholds**:
- |Correlation| > 0.3 = Potential proxy
- Mutual Information > 0.1 = Potential proxy
- Predictive accuracy > 0.70 = Strong proxy

**Example**:
```
Feature: "first_name"
Protected: "gender"
Mutual Information: 0.45 → STRONG PROXY
(Names like "Jennifer", "Michael" reveal gender)
```

### Missing Data Bias

**What it measures**: Is data missing systematically by group?

**Metrics**:
- **Missingness Rate**: `P(missing | A=a)` for each group
- **Missingness Difference**: `|P(missing|A=a) - P(missing|A=b)|`

**Thresholds**:
- Missingness difference > 0.10 = Systematic bias

**Example**:
```
Income missing for 5% of White applicants
Income missing for 25% of Black applicants
Difference: 0.20 → SYSTEMATIC BIAS
```

### Intersectional Bias

**What it measures**: Are intersectional groups (e.g., Black Women) underrepresented?

**Method**:
1. Compute expected size: `P(A=a) × P(B=b) × total_size`
2. Compare to actual size
3. Flag significant deviations

**Example**:
```
Black: 20% of data
Female: 50% of data
Expected Black Female: 0.20 × 0.50 = 10%
Actual Black Female: 5%
→ UNDERREPRESENTED (50% of expected)
```

### Distribution Shift

**What it measures**: Do feature distributions differ across groups?

**Metric**: KL Divergence (Kullback-Leibler)

**Formula**: `KL(P||Q) = Σ P(x) log(P(x)/Q(x))`

**Thresholds**:
- KL < 0.1 = Similar distributions
- KL 0.1-0.5 = Moderate shift
- KL > 0.5 = Severe shift

**Example**:
```
Credit score distribution:
  Male: mean=720, std=50
  Female: mean=680, std=60
KL Divergence: 0.35 → MODERATE SHIFT
```

### Severity Classification

| Severity | Representation | Label Bias (SRD) | DIR | Meaning |
|----------|----------------|------------------|-----|---------|
| **CRITICAL** | < 5% | > 0.20 | < 0.60 | Immediate action required |
| **MODERATE** | 5-10% | 0.10-0.20 | 0.60-0.80 | Remediation recommended |
| **LOW** | 10-20% | 0.05-0.10 | 0.80-0.90 | Monitor |
| **CLEAR** | > 20% | < 0.05 | > 0.90 | No action needed |

---

## System Architecture

### The 7-Phase Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Data Ingestion & Validation                       │
│ • Load from CSV, Excel, Parquet, or DataFrame              │
│ • Validate protected attributes exist                      │
│ • Validate target column exists                            │
│ • Check for sufficient samples                             │
├─────────────────────────────────────────────────────────────┤
│ PHASE 2: Representation Analysis                           │
│ • Count samples per group                                  │
│ • Compute representation ratios                            │
│ • Compute balance scores                                   │
│ • Flag underrepresented groups                             │
├─────────────────────────────────────────────────────────────┤
│ PHASE 3: Label Bias Analysis                               │
│ • Compute selection rates per group                        │
│ • Compute selection rate differences                       │
│ • Compute disparate impact ratios                          │
│ • Statistical significance tests                           │
├─────────────────────────────────────────────────────────────┤
│ PHASE 4: Proxy Feature Detection                           │
│ • Pearson correlation with protected attributes            │
│ • Mutual information with protected attributes             │
│ • Rank features by proxy risk                              │
├─────────────────────────────────────────────────────────────┤
│ PHASE 5: Missing Data Analysis                             │
│ • Compute missingness rates per group                      │
│ • Compute missingness differences                          │
│ • Flag systematic missingness patterns                     │
├─────────────────────────────────────────────────────────────┤
│ PHASE 6: Intersectional Disparity Analysis                 │
│ • Enumerate all intersectional groups                      │
│ • Compute expected vs actual sizes                         │
│ • Flag underrepresented intersections                      │
├─────────────────────────────────────────────────────────────┤
│ PHASE 7: Distribution Shift Analysis                       │
│ • Compute KL divergence for numeric features               │
│ • Compare distributions across groups                      │
│ • Flag significant shifts                                  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input
  ├─ Data (path or DataFrame)
  ├─ Protected attributes (e.g., ['gender', 'race'])
  ├─ Target column
  └─ Positive value
       │
       ▼
Phase 1: Ingestion
  ├─ Load data
  ├─ Validate columns
  └─ Basic statistics
       │
       ▼
Phase 2: Representation
  ├─ Count per group
  ├─ Compute ratios
  └─ Flag underrepresented
       │
       ▼
Phase 3: Label Bias
  ├─ Selection rates
  ├─ Rate differences
  └─ DIR computation
       │
       ▼
Phase 4: Proxy Detection
  ├─ Correlation analysis
  ├─ Mutual information
  └─ Rank features
       │
       ▼
Phase 5: Missing Data
  ├─ Missingness rates
  └─ Systematic patterns
       │
       ▼
Phase 6: Intersectional
  ├─ Expected sizes
  └─ Actual vs expected
       │
       ▼
Phase 7: Distribution Shift
  ├─ KL divergence
  └─ Feature distributions
       │
       ▼
Generate Findings & Recommendations
  ├─ Classify severity
  ├─ Generate remediation options
  └─ Build audit report
       │
       ▼
DatasetAuditReport
  ├─ audit_id, timestamp, duration
  ├─ overall_severity
  ├─ findings (structured)
  ├─ representation analysis
  ├─ label_rates
  ├─ proxy_features
  ├─ missing_data_matrix
  ├─ intersectional_disparities
  ├─ kl_divergences
  ├─ remediation_suggestions
  ├─ audit_integrity (SHA-256 hashes)
  └─ confidence_intervals
```

---

## Implementation Details

### Main API Function

```python
from nobias import audit_dataset

report = audit_dataset(
    data='training_data.csv',              # Path or DataFrame
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)
```

### Supported Data Formats

**File Paths**:
- CSV: `.csv`
- Excel: `.xlsx`, `.xls`
- Parquet: `.parquet`

**In-Memory**:
- pandas DataFrame

**Example**:
```python
# From file
report = audit_dataset(
    data='data.csv',
    protected_attributes=['gender'],
    target_column='approved',
    positive_value=1,
)

# From DataFrame
import pandas as pd
df = pd.read_csv('data.csv')
report = audit_dataset(
    data=df,
    protected_attributes=['gender'],
    target_column='approved',
    positive_value=1,
)
```

### Output Structure

```python
DatasetAuditReport(
    # Identification
    audit_id='dataset_audit_a1b2c3d4',
    timestamp='2026-04-26T10:30:00.000Z',
    duration_seconds=2.45,
    
    # Configuration
    dataset_name='training_data.csv',
    row_count=10000,
    column_count=15,
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
    
    # Severity
    overall_severity='MODERATE',
    
    # Findings
    findings=[
        DatasetFinding(
            check='representation',
            severity='MODERATE',
            message='Gender imbalance detected: Female 30% vs Male 70%',
            metric='representation_ratio',
            value=0.30,
            threshold=0.40,
            confidence=0.95,
        ),
        DatasetFinding(
            check='label_bias',
            severity='CRITICAL',
            message='EEOC violation: Female approval rate 60% vs Male 80% (DIR=0.75)',
            metric='disparate_impact_ratio',
            value=0.75,
            threshold=0.80,
            confidence=0.99,
        ),
        # ... more findings
    ],
    
    # Analysis Results
    representation={
        'gender': {
            'Male': {'count': 7000, 'ratio': 0.70},
            'Female': {'count': 3000, 'ratio': 0.30},
        },
        'balance_score': 0.43,
    },
    
    label_rates={
        'gender': {
            'Male': 0.80,
            'Female': 0.60,
            'srd': 0.20,
            'dir': 0.75,
        },
    },
    
    proxy_features=[
        ProxyFeature(
            feature='first_name',
            protected='gender',
            method='mutual_information',
            score=0.45,
            nmi=0.45,
        ),
        # ... more proxies
    ],
    
    missing_data_matrix={
        'income': {
            'White': 0.05,
            'Black': 0.25,
            'difference': 0.20,
        },
    },
    
    intersectional_disparities=[
        {
            'attributes': {'gender': 'Female', 'race': 'Black'},
            'expected_count': 1000,
            'actual_count': 500,
            'ratio': 0.50,
            'severity': 'CRITICAL',
        },
    ],
    
    kl_divergences={
        'credit_score': {
            'Male_vs_Female': 0.35,
            'White_vs_Black': 0.42,
        },
    },
    
    remediation_suggestions=[
        Remediation(
            strategy='Stratified Resampling',
            estimated_dir_after=0.85,
            estimated_spd_after=0.08,
            description='Oversample underrepresented groups to balance dataset',
        ),
        # ... more suggestions
    ],
    
    # FairSight Compliance
    audit_integrity=DatasetIntegrity(...),
    confidence_intervals={...},
    
    # Logs
    logs=['Phase 1: Data ingestion...', ...],
)
```

---

## Example Workflows

### Workflow 1: Quick Dataset Check

**Scenario**: You have a dataset and want to check for obvious bias

```python
from nobias import audit_dataset

# Run audit
report = audit_dataset(
    data='hiring_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)

# Check results
print(f"Overall Severity: {report.overall_severity}")
print(f"Total Findings: {len(report.findings)}")

# Check critical issues
critical = report.get_critical_findings()
if critical:
    print(f"\n⚠️ {len(critical)} CRITICAL issues found:")
    for finding in critical:
        print(f"  - {finding.message}")
```

**Time**: ~2 seconds  
**Use case**: Initial data quality check

---

### Workflow 2: Detailed Analysis with Remediation

**Scenario**: You found bias and want to fix it

```python
from nobias import audit_dataset

# Run audit
report = audit_dataset(
    data='training_data.csv',
    protected_attributes=['gender', 'race', 'age'],
    target_column='approved',
    positive_value=1,
)

# Export for documentation
report.export('dataset_audit.json', format='json')
report.export('dataset_audit.txt', format='text')

# Review findings by type
print("\n📊 Representation Issues:")
for finding in report.get_findings_by_check('representation'):
    print(f"  [{finding.severity}] {finding.message}")

print("\n📊 Label Bias Issues:")
for finding in report.get_findings_by_check('label_bias'):
    print(f"  [{finding.severity}] {finding.message}")

print("\n📊 Proxy Features:")
for proxy in report.proxy_features:
    print(f"  {proxy.feature} → {proxy.protected} (score: {proxy.score:.3f})")

# Review remediation options
print("\n🔧 Remediation Suggestions:")
for i, remedy in enumerate(report.remediation_suggestions, 1):
    print(f"\n{i}. {remedy.strategy}")
    print(f"   {remedy.description}")
    print(f"   Expected DIR after: {remedy.estimated_dir_after:.2f}")
    print(f"   Expected SPD after: {remedy.estimated_spd_after:.2f}")
```

**Time**: ~5 seconds  
**Use case**: Detailed analysis and remediation planning

---

### Workflow 3: Comparing Datasets

**Scenario**: You want to compare original vs cleaned dataset

```python
from nobias import audit_dataset

# Audit original
report_original = audit_dataset(
    data='original_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)

# Apply remediation (e.g., resampling)
# ... your remediation code ...

# Audit cleaned
report_cleaned = audit_dataset(
    data='cleaned_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)

# Compare
print("📊 Comparison:")
print(f"\nOriginal:")
print(f"  Severity: {report_original.overall_severity}")
print(f"  Findings: {len(report_original.findings)}")
print(f"  DIR: {report_original.label_rates['gender']['dir']:.2f}")

print(f"\nCleaned:")
print(f"  Severity: {report_cleaned.overall_severity}")
print(f"  Findings: {len(report_cleaned.findings)}")
print(f"  DIR: {report_cleaned.label_rates['gender']['dir']:.2f}")

improvement = report_cleaned.label_rates['gender']['dir'] - report_original.label_rates['gender']['dir']
print(f"\nDIR Improvement: +{improvement:.2f}")
```

**Time**: ~4 seconds (2 audits)  
**Use case**: Validating remediation effectiveness

---

### Workflow 4: Automated Data Pipeline

**Scenario**: Integrate audit into your data pipeline

```python
from nobias import audit_dataset
import pandas as pd

def validate_dataset(data_path, protected_attrs, target_col, positive_val):
    """Validate dataset before training."""
    
    # Run audit
    report = audit_dataset(
        data=data_path,
        protected_attributes=protected_attrs,
        target_column=target_col,
        positive_value=positive_val,
    )
    
    # Check for critical issues
    critical = report.get_critical_findings()
    
    if critical:
        print(f"❌ Dataset validation FAILED: {len(critical)} critical issues")
        for finding in critical:
            print(f"  - {finding.message}")
        return False
    
    # Check EEOC compliance
    for attr, rates in report.label_rates.items():
        if rates['dir'] < 0.80:
            print(f"❌ EEOC violation for {attr}: DIR={rates['dir']:.2f}")
            return False
    
    print("✅ Dataset validation PASSED")
    return True

# Use in pipeline
if validate_dataset('data.csv', ['gender', 'race'], 'hired', 1):
    # Proceed with training
    train_model()
else:
    # Apply remediation
    apply_remediation()
```

**Time**: ~2 seconds  
**Use case**: CI/CD integration, automated validation

---

## Input/Output Examples

### Example 1: Hiring Dataset

**Input**:
```python
report = audit_dataset(
    data='hiring_data.csv',
    protected_attributes=['gender', 'race', 'age'],
    target_column='hired',
    positive_value=1,
)
```

**Data** (`hiring_data.csv`):
```csv
gender,race,age,experience,education,hired
Male,White,35,5,Bachelor,1
Female,Black,28,3,Master,0
Male,Asian,42,10,PhD,1
Female,White,31,4,Bachelor,1
...
```

**Output**:
```python
DatasetAuditReport(
    audit_id='dataset_audit_a1b2c3d4',
    dataset_name='hiring_data.csv',
    row_count=10000,
    overall_severity='MODERATE',
    
    findings=[
        DatasetFinding(
            check='representation',
            severity='MODERATE',
            message='Gender imbalance: Female 30% vs Male 70%',
            metric='representation_ratio',
            value=0.30,
            threshold=0.40,
        ),
        DatasetFinding(
            check='label_bias',
            severity='MODERATE',
            message='Gender hiring disparity: Female 62% vs Male 78% (SRD=0.16)',
            metric='selection_rate_difference',
            value=0.16,
            threshold=0.10,
        ),
    ],
    
    proxy_features=[
        ProxyFeature(
            feature='first_name',
            protected='gender',
            method='mutual_information',
            score=0.45,
            nmi=0.45,
        ),
    ],
    
    remediation_suggestions=[
        Remediation(
            strategy='Stratified Resampling',
            estimated_dir_after=0.85,
            estimated_spd_after=0.08,
            description='Oversample Female candidates to 40% representation',
        ),
        Remediation(
            strategy='Remove Proxy Features',
            estimated_dir_after=0.82,
            estimated_spd_after=0.10,
            description='Remove first_name feature (strong gender proxy)',
        ),
    ],
)
```

---

### Example 2: Lending Dataset with EEOC Violation

**Input**:
```python
report = audit_dataset(
    data='loan_applications.csv',
    protected_attributes=['race'],
    target_column='approved',
    positive_value=1,
)
```

**Output** (Critical Finding):
```python
DatasetAuditReport(
    overall_severity='CRITICAL',
    
    findings=[
        DatasetFinding(
            check='label_bias',
            severity='CRITICAL',
            message='EEOC violation: Black approval rate 50% vs White 75% (DIR=0.67)',
            metric='disparate_impact_ratio',
            value=0.67,
            threshold=0.80,
            confidence=0.99,
        ),
    ],
    
    label_rates={
        'race': {
            'White': 0.75,
            'Black': 0.50,
            'srd': 0.25,
            'dir': 0.67,  # EEOC VIOLATION
        },
    },
)
```

---

## Best Practices

### 1. Data Preparation

**DO**:
- Include all protected attributes in data
- Use complete dataset (not samples)
- Handle missing values appropriately
- Document data sources

**DON'T**:
- Remove protected attributes before audit
- Use only a subset of data
- Ignore missing data patterns

### 2. Interpretation

**DO**:
- Review all findings, not just severity
- Check EEOC compliance (DIR >= 0.80)
- Examine proxy features
- Consider intersectional findings

**DON'T**:
- Ignore "LOW" severity findings
- Focus only on representation
- Skip proxy feature analysis

### 3. Remediation

**DO**:
- Start with least invasive (reweighting)
- Test remediation effectiveness
- Re-audit after changes
- Document remediation steps

**DON'T**:
- Apply multiple remediations at once
- Skip validation
- Remove protected attributes

### 4. Documentation

**DO**:
- Export audit reports
- Document findings
- Track remediation steps
- Version datasets

**DON'T**:
- Skip documentation
- Lose audit trails
- Forget to re-audit

---

## Troubleshooting

### Issue: "Protected attribute not found"

**Cause**: Column name mismatch

**Solution**:
```python
# Check column names
import pandas as pd
df = pd.read_csv('data.csv')
print(df.columns.tolist())

# Use exact column name
report = audit_dataset(
    data=df,
    protected_attributes=['Gender'],  # Match exact case
    target_column='Hired',
    positive_value=1,
)
```

### Issue: "Insufficient samples"

**Cause**: Too few samples in dataset

**Solution**:
- Use larger dataset (min 1000 samples recommended)
- Combine rare categories
- Skip intersectional analysis

### Issue: "High proxy feature scores"

**Cause**: Features encode protected attributes

**Interpretation**: Normal for features like names, zip codes

**Solution**:
- Review proxy features list
- Consider removing high-score proxies
- Document decision to keep/remove

### Issue: "No remediation suggestions"

**Cause**: Dataset is already fair (CLEAR severity)

**Interpretation**: No action needed

**Solution**: Proceed with training

---

## Summary

The Dataset Audit System provides:
- ✅ Comprehensive bias detection (7 types)
- ✅ Legal compliance (EEOC, EU AI Act, NIST)
- ✅ Actionable remediation strategies
- ✅ Fast execution (seconds)
- ✅ Privacy-friendly (local analysis)

**Next Steps**:
1. Run your first audit: `audit_dataset(data, protected_attributes, target_column, positive_value)`
2. Review findings and severity
3. Check EEOC compliance (DIR >= 0.80)
4. Apply recommended remediations
5. Re-audit and document results

For more details, see:
- API Reference: `library/dataset_audit/README.md`
- Example Scripts: `examples/dataset_audit_example.py`
- Remediation Guide: `docs/REMEDIATION_STRATEGIES.md`
