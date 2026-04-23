# Dataset Audit Module — Development Plan

> **Module purpose**: Accept a tabular dataset + protected attribute labels → detect statistical
> biases in representation, labelling, feature correlations, and intersectional disparities →
> return a structured report with severity-graded findings + remediation suggestions.

---

## 1. Public API Surface

```python
from nobias.dataset_audit import audit_dataset, DatasetAuditConfig, DatasetAuditReport

report: DatasetAuditReport = audit_dataset(
    data="path/to/file.csv",            # or pd.DataFrame
    protected_attributes=["gender", "race", "age"],
    target_column="hired",
    positive_value="Yes",
)

print(report.overall_severity)           # "MODERATE"
print(report.findings)                   # List[DatasetFinding]
report.export("report.pdf")
```

---

## 2. Core Detection Pipeline (implement in this order)

### Phase 1 — Data Ingestion & Validation
- [ ] Accept CSV, Excel (.xlsx), Parquet via filepath or raw DataFrame
- [ ] Auto-detect column types (categorical, numeric, boolean)
- [ ] Validate protected attribute columns exist and have ≥2 unique values
- [ ] Validate target column exists and identify positive/negative classes
- [ ] Generate row count, column count, data preview (first 10 rows)

### Phase 2 — Representation Analysis
- [ ] Count per-group sample sizes for each protected attribute
- [ ] Compute representation ratios (group % in dataset vs expected baseline)
- [ ] Flag severe under-representation (<10% of majority group)
- [ ] Intersectional representation: check all 2-way attribute crossings

### Phase 3 — Label Bias Scan
- [ ] Compute positive label rate per group for each protected attribute
- [ ] Disparate Impact Ratio (DIR): P(Y=1|unprivileged) / P(Y=1|privileged)
- [ ] Flag DIR < 0.80 (EEOC 80% rule threshold)
- [ ] Statistical Parity Difference (SPD): P(Y=1|unprivileged) - P(Y=1|privileged)
- [ ] Flag SPD < -0.10
- [ ] Chi-square test for independence of label × protected attribute

### Phase 4 — Feature-Attribute Correlation (Proxy Detection)
- [ ] For each non-protected feature, compute correlation with each protected attribute
- [ ] Categorical×categorical: Cramér's V
- [ ] Numeric×categorical: point-biserial correlation
- [ ] Numeric×numeric: Pearson r
- [ ] Normalised Mutual Information between features and protected attributes
- [ ] Flag features with correlation > 0.5 as potential proxy variables
- [ ] Rank proxy features by strength of association

### Phase 5 — Missing Data Analysis
- [ ] Compute missingness rate per column per demographic group
- [ ] Flag differential missingness > 5% between groups (measurement bias)
- [ ] Use scipy.stats.chi2_contingency to test if missingness is independent of group
- [ ] Generate missingness matrix (columns × groups) for heatmap visualisation

### Phase 6 — Intersectional Disparity Scan
- [ ] For all 2-way and 3-way crossings of protected attributes:
  - Compute positive label rate per intersectional group
  - Compute DIR for worst-vs-best group
  - Flag disparity > 10% as finding
- [ ] Sort intersectional findings by disparity magnitude

### Phase 7 — KL Divergence (Distribution Shift)
- [ ] For each protected attribute, compute KL divergence of label distribution
  across demographic subgroups
- [ ] Flag KL divergence > 0.1 as evidence of distribution shift

---

## 3. Severity Classification

```
CRITICAL:  DIR < 0.60 or SPD < -0.20 (p < 0.01)
MODERATE:  DIR < 0.80 or SPD < -0.10 (p < 0.05)
LOW:       DIR < 0.90 or SPD < -0.05  
CLEAR:     DIR ≥ 0.90 and SPD ≥ -0.05
```

---

## 4. Remediation Outputs

- [ ] **Reweighting**: Kamiran & Calders (2012) — compute sample weights that equalise
  positive label rates across groups. Output as a weight column (CSV download).
- [ ] **Disparate Impact Remover**: Feldman et al. (2015) — transform non-protected
  feature distributions to remove group-dependent variation. Output as modified CSV.
- [ ] **SMOTE oversampling**: Generate synthetic samples for under-represented
  intersectional groups. Output as augmented CSV.
- [ ] For each remediation, compute estimated post-fix metrics (DIR, SPD).

---

## 5. Report Object Schema

```python
@dataclass
class DatasetAuditReport:
    dataset_name: str
    row_count: int
    column_count: int
    overall_severity: str                      # CRITICAL | MODERATE | LOW | CLEAR
    findings: list[DatasetFinding]
    representation: dict                       # per-attribute group counts + ratios
    label_rates: dict                          # per-attribute positive label rates
    proxy_features: list[ProxyFeature]         # flagged correlations
    missing_data_matrix: dict                  # column × group missingness rates
    intersectional_disparities: list[dict]
    remediation_suggestions: list[Remediation]
    
    def export(self, path: str): ...           # PDF or JSON
    def to_dict(self) -> dict: ...             # for API serialisation
```

---

## 6. Dependencies

```
pandas >= 2.0          # data handling
numpy >= 1.24          # numerics
scipy >= 1.11          # chi-square, KL divergence, correlation tests
scikit-learn           # mutual information, label encoding
imbalanced-learn       # SMOTE oversampling
```

---

## 7. File Structure

```
dataset_audit/
├── __init__.py            # Public API: audit_dataset(), DatasetAuditConfig
├── ingestion.py           # File loading, type detection, validation
├── representation.py      # Group counts, representation ratios
├── label_bias.py          # DIR, SPD, chi-square
├── proxy_detection.py     # Feature-attribute correlations, mutual info
├── missing_data.py        # Differential missingness analysis
├── intersectional.py      # k-way intersection scans
├── divergence.py          # KL divergence of label distributions
├── severity.py            # Severity classifier (shared thresholds)
├── remediation.py         # Reweighting, DI remover, SMOTE
├── report.py              # DatasetAuditReport, export (JSON/PDF)
└── models.py              # Dataclasses: DatasetFinding, ProxyFeature, etc.
```
