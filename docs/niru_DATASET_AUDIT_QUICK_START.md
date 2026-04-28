# Dataset Audit - Quick Start Guide

Get started with NoBias Dataset Audit in 5 minutes.

---

## Installation

```bash
pip install pandas numpy scipy scikit-learn
```

---

## Basic Usage - Audit a Dataset

### Step 1: Prepare Your Data

Your dataset should include:
- All features
- Protected attributes (gender, race, age, etc.)
- Target column with labels

```python
import pandas as pd

# Load data
data = pd.read_csv('training_data.csv')

# Example structure:
# gender, race, age, experience, education, hired
# Male, White, 35, 5, Bachelor, 1
# Female, Black, 28, 3, Master, 0
```

### Step 2: Run the Audit

```python
from nobias import audit_dataset

report = audit_dataset(
    data='training_data.csv',            # Path or DataFrame
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)
```

### Step 3: Check Results

```python
# Overall assessment
print(f"Severity: {report.overall_severity}")
print(f"Total Findings: {len(report.findings)}")

# Critical findings
for finding in report.get_critical_findings():
    print(f"[{finding.severity}] {finding.message}")
```

---

## Quick Example - DataFrame

```python
from nobias import audit_dataset
import pandas as pd

# Load DataFrame
df = pd.read_csv('data.csv')

# Run audit
report = audit_dataset(
    data=df,
    protected_attributes=['gender', 'race'],
    target_column='approved',
    positive_value=1,
)

print(f"Severity: {report.overall_severity}")
print(f"Findings: {len(report.findings)}")
```

---

## Understanding the Output

### Severity Levels

- **CRITICAL**: Immediate action required (DIR < 0.60, representation < 5%)
- **MODERATE**: Remediation recommended (DIR 0.60-0.80, representation 5-10%)
- **LOW**: Monitor (DIR 0.80-0.90, representation 10-20%)
- **CLEAR**: No significant bias (DIR > 0.90, representation > 20%)

### Key Metrics

**Representation Ratio**: Percentage of each group in dataset
- <10%: Underrepresented
- 10-20%: Low representation
- 20-40%: Adequate
- >40%: Well represented

**Disparate Impact Ratio (DIR)**: EEOC 80% rule for label distribution
- <0.80: **LEGAL VIOLATION**
- 0.80-0.85: Warning
- >0.85: Compliant

**Selection Rate Difference (SRD)**: Difference in positive label rates
- <0.05: Negligible
- 0.05-0.10: Minor
- 0.10-0.20: Significant
- >0.20: Severe

---

## Export Results

```python
# JSON format
report.export('dataset_audit.json', format='json')

# Text format
report.export('dataset_audit.txt', format='text')

# PDF format
report.export('dataset_audit.pdf', format='pdf')
```

---

## Common Use Cases

### 1. Pre-Training Validation

```python
report = audit_dataset(data, protected_attributes, target_column, positive_value)

if report.overall_severity in ['CRITICAL', 'MODERATE']:
    print("⚠️ Dataset has bias - apply remediation before training")
    for remedy in report.remediation_suggestions:
        print(f"  - {remedy.strategy}: {remedy.description}")
else:
    print("✅ Dataset passed fairness check")
```

### 2. Check EEOC Compliance

```python
report = audit_dataset(data, protected_attributes, target_column, positive_value)

for attr, rates in report.label_rates.items():
    if rates['dir'] < 0.80:
        print(f"⚠️ EEOC VIOLATION for {attr}: DIR={rates['dir']:.2f}")
    else:
        print(f"✅ {attr} compliant: DIR={rates['dir']:.2f}")
```

### 3. Identify Proxy Features

```python
report = audit_dataset(data, protected_attributes, target_column, positive_value)

print("Proxy Features Detected:")
for proxy in report.proxy_features:
    print(f"  {proxy.feature} → {proxy.protected} (score: {proxy.score:.3f})")
```

### 4. Compare Original vs Cleaned

```python
# Audit original
report_original = audit_dataset(data_original, protected_attributes, target_column, positive_value)

# Apply remediation
# ... your remediation code ...

# Audit cleaned
report_cleaned = audit_dataset(data_cleaned, protected_attributes, target_column, positive_value)

# Compare
print(f"Original DIR: {report_original.label_rates['gender']['dir']:.2f}")
print(f"Cleaned DIR: {report_cleaned.label_rates['gender']['dir']:.2f}")
```

---

## Bias Types Detected

### 1. Representation Bias
Underrepresented groups in dataset

### 2. Label Bias
Different approval rates across demographics

### 3. Proxy Features
Features that encode protected attributes (e.g., names, zip codes)

### 4. Missing Data Bias
Systematic missingness patterns by group

### 5. Intersectional Bias
Compounded underrepresentation for multiple attributes

### 6. Distribution Shift
Different feature distributions across groups

### 7. Correlation Bias
Features correlated with protected attributes

---

## Remediation Strategies

The audit automatically suggests remediation strategies:

```python
for remedy in report.remediation_suggestions:
    print(f"\n{remedy.strategy}")
    print(f"  Description: {remedy.description}")
    print(f"  Expected DIR after: {remedy.estimated_dir_after:.2f}")
    print(f"  Expected SPD after: {remedy.estimated_spd_after:.2f}")
```

Common strategies:
- **Stratified Resampling**: Oversample underrepresented groups
- **Sample Reweighting**: Assign weights to balance groups
- **Remove Proxy Features**: Drop features that encode protected attributes
- **Imputation**: Fill missing data systematically

---

## Next Steps

- **Detailed Analysis**: See [DATASET_AUDIT_IMPLEMENTATION_GUIDE.md](niru_DATASET_AUDIT_IMPLEMENTATION_GUIDE.md)
- **Visual Summary**: See [DATASET_AUDIT_VISUAL_SUMMARY.md](niru_DATASET_AUDIT_VISUAL_SUMMARY.md)
- **Remediation**: Apply suggested strategies from `report.remediation_suggestions`
- **Examples**: Check `examples/dataset_audit_example.py`

---

## Troubleshooting

**Issue**: "Protected attribute not found"
- **Solution**: Check column names match exactly (case-sensitive)

**Issue**: "Insufficient samples"
- **Solution**: Use larger dataset (min 1000 samples recommended)

**Issue**: "High proxy feature scores"
- **Solution**: Review proxy features and consider removing them

**Issue**: "No remediation suggestions"
- **Solution**: Dataset is already fair (CLEAR severity) - proceed with training

---

## Support

- Full Documentation: `library/dataset_audit/README.md`
- API Reference: `API_REFERENCE.md`
- Examples: `examples/dataset_audit_example.py`
