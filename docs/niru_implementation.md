# Dataset Audit - Niru Implementation

## What It Does

Detects 7 types of bias in datasets before model training.

## Architecture

### 1. Data Ingestion (`ingestion.py`)
- Loads CSV, Excel, Parquet files
- Auto-detects column types (categorical, numeric)
- Validates protected attributes exist
- Binarizes target column
- Handles edge cases (missing columns, single groups)

### 2. Representation Analysis (`representation.py`)
- Counts samples per demographic group
- Calculates percentage of total
- Flags groups < 10% of majority size (CRITICAL)
- Flags groups < 35% of total (MODERATE)
- Checks intersectional group sizes

### 3. Label Bias Detection (`label_bias.py`)
- **DIR (Disparate Impact Ratio)**:
  - Formula: P(Y=1|unprivileged) / P(Y=1|privileged)
  - CRITICAL if < 0.60
  - MODERATE if < 0.80 (EEOC 80% rule)
  - LOW if < 0.90

- **SPD (Statistical Parity Difference)**:
  - Formula: P(Y=1|unprivileged) - P(Y=1|privileged)
  - CRITICAL if < -0.20
  - MODERATE if < -0.10
  - LOW if < -0.05

- **Chi-square test**: Tests independence of label × protected attribute

### 4. Proxy Detection (`proxy_detection.py`)
- Finds features correlated with protected attributes
- Methods:
  - **Cramér's V**: Categorical × Categorical
  - **Point-biserial**: Numeric × Categorical (binary)
  - **Eta-squared**: Numeric × Categorical (multi-class)
  - **Pearson**: Numeric × Numeric
  - **NMI**: Normalized Mutual Information
- Flags if correlation > 0.3 OR NMI > 0.1

### 5. Missing Data Analysis (`missing_data.py`)
- Computes null percentage per group
- Flags if max - min missingness > 5%
- Chi-square test for independence
- Outputs missingness matrix

### 6. Intersectional Analysis (`intersectional.py`)
- Analyzes 2-way group combinations
- Computes DIR for worst vs best group
- Flags disparity > 10%
- Detects superadditive bias (intersectional > individual)

### 7. Distribution Shift (`divergence.py`)
- KL divergence of label distributions
- Compares each group to majority group
- Flags KL > 0.1 (MODERATE if > 0.2)

### 8. Severity Classification (`severity.py`)
- Maps findings to severity levels
- Overall severity = worst finding
- Order: CRITICAL > MODERATE > LOW > CLEAR

### 9. Remediation (`remediation.py`)
- **Reweighting**: Adjust sample weights to equalize outcomes
- **Disparate Impact Remover**: Transform features (repair_level=0.8)
- **SMOTE**: Oversample under-represented groups
- Each includes estimated post-fix DIR/SPD

### 10. Report Generation (`report.py`)
- Aggregates all findings
- Generates human-readable text
- Exports to JSON
- Groups findings by severity

## Data Models (`models.py`)

```python
@dataclass
class DatasetFinding:
    check: str              # Type of check
    severity: str           # CRITICAL/MODERATE/LOW
    message: str            # Human-readable description
    metric: str             # DIR, SPD, etc.
    value: float            # Actual value
    threshold: float        # Threshold violated
    confidence: float       # 0.3 to 1.0

@dataclass
class ProxyFeature:
    feature: str            # Feature name
    protected: str          # Protected attribute
    method: str             # Correlation method
    score: float            # Correlation score
    nmi: float              # Mutual information

@dataclass
class Remediation:
    strategy: str           # Fix strategy name
    estimated_dir_after: float
    estimated_spd_after: float
    description: str
```

## Confidence Scoring

Based on sample size of smallest group:
- < 30 samples → 30% confidence
- < 100 samples → 60% confidence
- < 500 samples → 80% confidence
- ≥ 500 samples → 100% confidence

## Edge Cases Handled

- Division by zero → return None, skip metric
- Single group → skip comparative checks
- All-null column → skip, log warning
- Empty intersectional group → skip silently
- Privileged group with 0 positive rate → skip DIR/SPD

## Dependencies

- **pandas** ≥ 2.0 - Data handling
- **numpy** ≥ 1.24 - Numerical operations
- **scipy** ≥ 1.11 - Statistical tests (chi-square, correlations, KL divergence)
- **scikit-learn** ≥ 1.3 - Mutual information, preprocessing
- **imbalanced-learn** ≥ 0.11 - SMOTE oversampling

## Performance

- Typical dataset (10K rows, 20 cols): ~2-5 seconds
- Large dataset (100K rows, 50 cols): ~10-30 seconds
- Bottlenecks: Chi-square tests, intersectional analysis

## Files (12 Python + 2 Docs)

**Code**:
- `__init__.py` - Main API (audit_dataset function)
- `models.py` - Data classes
- `ingestion.py` - Load & validate
- `representation.py` - Group analysis
- `label_bias.py` - DIR/SPD/chi-square
- `proxy_detection.py` - Correlations
- `missing_data.py` - Missingness
- `intersectional.py` - Group combos
- `divergence.py` - KL divergence
- `severity.py` - Classification
- `remediation.py` - Fix suggestions
- `report.py` - Output generation

**Docs**:
- `README.md` - Quick guide
- `OVERVIEW.md` - Detailed documentation

## Usage Example

```python
from library.dataset_audit import audit_dataset

report = audit_dataset(
    data="hiring_data.csv",
    protected_attributes=["gender", "race"],
    target_column="hired",
    positive_value=1
)

# Overall severity
print(report.overall_severity)  # "CRITICAL"

# Findings by severity
critical = [f for f in report.findings if f.severity == "CRITICAL"]
for finding in critical:
    print(f"{finding.message}")
    print(f"  {finding.metric}: {finding.value:.3f} (threshold: {finding.threshold})")
    print(f"  Confidence: {finding.confidence*100:.0f}%")

# Proxy features
for proxy in report.proxy_features:
    print(f"{proxy.feature} → {proxy.protected}: {proxy.score:.3f}")

# Remediation
for rem in report.remediation_suggestions:
    print(f"{rem.strategy}: DIR after = {rem.estimated_dir_after:.3f}")

# Export
report.export("audit.json")
```
