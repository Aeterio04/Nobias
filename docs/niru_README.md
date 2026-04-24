# Dataset Audit - Niru

## Quick Links

- **niru_start_here.md** - Setup and first run
- **niru_how_to_run.md** - Usage examples
- **niru_implementation.md** - Technical details
- **niru_complete.txt** - Quick summary

## Module Location

`/library/dataset_audit/`

## What It Does

Detects 7 types of bias in datasets:
1. Representation bias
2. Label bias (DIR/SPD)
3. Proxy features
4. Missing data patterns
5. Intersectional disparities
6. Distribution shifts
7. Remediation suggestions

## Quick Start

```bash
cd Nobias
pip install pandas numpy scipy scikit-learn imbalanced-learn
python test_simple.py
```

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
report.export("audit.json")
```

## Key Metrics

- **DIR** (Disparate Impact Ratio): < 0.80 fails EEOC 80% rule
- **SPD** (Statistical Parity Difference): < -0.10 is moderate bias
- **Confidence**: 30% to 100% based on sample size

## Module Docs

See `/library/dataset_audit/`:
- README.md - Quick guide
- OVERVIEW.md - Detailed documentation
