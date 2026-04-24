# Dataset Audit - Niru Start Here

## Quick Setup

```bash
cd Nobias
pip install pandas numpy scipy scikit-learn imbalanced-learn
python test_simple.py
```

## What You Built

**Module**: `/library/dataset_audit/`

**Files**: 12 Python files + 2 docs

**What it does**: Detects 7 types of bias in datasets before model training

## Usage

```python
from library.dataset_audit import audit_dataset

report = audit_dataset(
    data="data.csv",
    protected_attributes=["gender", "race"],
    target_column="hired",
    positive_value=1
)

print(report.overall_severity)  # CRITICAL/MODERATE/LOW/CLEAR
print(report.to_text())
```

## What It Detects

1. **Representation bias** - Groups too small
2. **Label bias** - DIR < 0.80 (fails EEOC 80% rule)
3. **Proxy features** - Columns that leak protected info
4. **Missing data** - Differential missingness > 5%
5. **Intersectional** - Hidden bias in group combos
6. **Distribution shift** - KL divergence > 0.1
7. **Remediation** - 3 fix strategies with estimated impact

## Key Metrics

- **DIR** (Disparate Impact Ratio): unprivileged_rate / privileged_rate
  - < 0.60 = CRITICAL
  - < 0.80 = MODERATE (fails EEOC 80% rule)
  - < 0.90 = LOW

- **SPD** (Statistical Parity Difference): unprivileged_rate - privileged_rate
  - < -0.20 = CRITICAL
  - < -0.10 = MODERATE
  - < -0.05 = LOW

## Test Results

When you ran `test_simple.py`, it found:
- CRITICAL: Female DIR = 0.47 (way below 0.60)
- MODERATE: Under-representation issues
- Proxy feature: zip_code → race (0.507 correlation)
- Remediation: Reweighting can improve DIR to 0.95

## Module Structure

```
library/dataset_audit/
├── __init__.py          # Main API
├── models.py            # Data classes
├── ingestion.py         # Load CSV/Excel/Parquet
├── representation.py    # Group sizes
├── label_bias.py        # DIR/SPD/chi-square
├── proxy_detection.py   # Correlations
├── missing_data.py      # Missingness
├── intersectional.py    # Group combos
├── divergence.py        # KL divergence
├── severity.py          # Classification
├── remediation.py       # Fix suggestions
├── report.py            # Output
├── README.md            # Quick guide
└── OVERVIEW.md          # Detailed docs
```

## Git Workflow

```bash
# Only commit your module
git add library/dataset_audit/
git commit -m "dataset_audit: your changes"
git push origin library
```

## Documentation

- **Module docs**: `/library/dataset_audit/README.md` and `OVERVIEW.md`
- **General docs**: `/docs/niru_*.md` files
- **Test**: `test_simple.py` and `test_adult.py`
