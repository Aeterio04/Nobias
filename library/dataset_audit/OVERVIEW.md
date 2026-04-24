# Dataset Audit - Overview

## What It Does

Analyzes tabular datasets for statistical bias before model training. Detects 7 types of bias and suggests fixes.

## Core Functionality

### 1. Representation Analysis
- Counts samples per demographic group
- Flags under-represented groups (< 10% of majority)
- Checks intersectional group sizes (e.g., Black + Female)

### 2. Label Bias Detection
- **DIR (Disparate Impact Ratio)**: Measures if unprivileged groups get fewer positive outcomes
  - Formula: P(Y=1|unprivileged) / P(Y=1|privileged)
  - Threshold: < 0.80 fails EEOC 80% rule
- **SPD (Statistical Parity Difference)**: Absolute gap in positive rates
  - Formula: P(Y=1|unprivileged) - P(Y=1|privileged)
  - Threshold: < -0.10 is moderate bias
- **Chi-square test**: Statistical significance of label-group dependency

### 3. Proxy Feature Detection
- Finds non-protected features correlated with protected attributes
- Methods:
  - Cramér's V (categorical × categorical)
  - Point-biserial (numeric × categorical)
  - Pearson correlation (numeric × numeric)
  - Normalized Mutual Information (NMI)
- Flags features with correlation > 0.3 or NMI > 0.1

### 4. Missing Data Analysis
- Computes null percentage per group
- Flags differential missingness > 5% between groups
- Chi-square test for independence

### 5. Intersectional Disparities
- Analyzes 2-way and 3-way group combinations
- Detects superadditive bias (intersectional > individual)
- Flags disparities > 10%

### 6. Distribution Shift
- KL divergence of label distributions across groups
- Flags KL > 0.1

### 7. Remediation Suggestions
- **Reweighting**: Adjust sample weights to equalize outcomes
- **Disparate Impact Remover**: Transform features to reduce bias
- **SMOTE**: Oversample under-represented groups
- Each includes estimated post-fix DIR/SPD

## Severity Classification

- **CRITICAL**: DIR < 0.60 or SPD < -0.20 (immediate action)
- **MODERATE**: DIR < 0.80 or SPD < -0.10 (needs attention)
- **LOW**: DIR < 0.90 or SPD < -0.05 (monitor)
- **CLEAR**: No significant bias

## Confidence Scoring

Every finding includes confidence based on sample size:
- < 30 samples → 30% confidence
- < 100 samples → 60% confidence
- < 500 samples → 80% confidence
- ≥ 500 samples → 100% confidence

## Input Requirements

- **Data**: CSV, Excel, or Parquet file (or pandas DataFrame)
- **Protected attributes**: List of sensitive columns (e.g., ["gender", "race"])
- **Target column**: Outcome variable to analyze
- **Positive value**: What counts as "success" (e.g., 1, "Yes", ">50K")

## Output

Returns `DatasetAuditReport` with:
- `overall_severity`: CRITICAL/MODERATE/LOW/CLEAR
- `findings`: List of specific issues with metrics
- `proxy_features`: Correlated features
- `remediation_suggestions`: Fix strategies with estimated impact
- `representation`: Group counts and percentages
- `label_rates`: Positive rates per group
- `missing_data_matrix`: Null percentages
- `intersectional_disparities`: Group combination analysis
- `kl_divergences`: Distribution shifts

## Example

```python
from library.dataset_audit import audit_dataset

report = audit_dataset(
    data="hiring_data.csv",
    protected_attributes=["gender", "race"],
    target_column="hired",
    positive_value=1
)

# Check severity
print(report.overall_severity)  # "CRITICAL"

# View findings
for finding in report.findings:
    print(f"[{finding.severity}] {finding.message}")
    print(f"  Metric: {finding.metric} = {finding.value:.3f}")
    print(f"  Confidence: {finding.confidence*100:.0f}%")

# Get remediation suggestions
for rem in report.remediation_suggestions:
    print(f"{rem.strategy}: DIR after = {rem.estimated_dir_after:.3f}")

# Export
report.export("audit.json")
```

## Dependencies

- pandas ≥ 2.0
- numpy ≥ 1.24
- scipy ≥ 1.11
- scikit-learn ≥ 1.3
- imbalanced-learn ≥ 0.11
