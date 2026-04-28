# Dataset Audit - Team Guide

## What Niru Built

A bias detection module for tabular datasets. Detects 7 types of bias before model training.

## Quick Test

```bash
cd Nobias
pip install pandas numpy scipy scikit-learn imbalanced-learn
python test_simple.py
```

## Usage

```python
from library.dataset_audit import audit_dataset

report = audit_dataset(
    data="your_data.csv",
    protected_attributes=["gender", "race"],
    target_column="outcome",
    positive_value=1
)

print(report.overall_severity)  # CRITICAL/MODERATE/LOW/CLEAR
print(report.to_text())
```

## What It Detects

1. Representation bias (small groups)
2. Label bias (DIR < 0.80 fails EEOC 80% rule)
3. Proxy features (indirect discrimination)
4. Missing data patterns
5. Intersectional disparities
6. Distribution shifts
7. Remediation suggestions

## Documentation

- **Module docs**: `/library/dataset_audit/README.md` and `OVERVIEW.md`
- **Setup guide**: `/docs/niru_start_here.md`
- **Technical details**: `/docs/niru_implementation.md`

## Files

- 12 Python files (~1,400 lines)
- 2 module docs
- 5 general docs
- 2 test scripts

## Status

✅ Complete and tested
✅ Pushed to GitHub (library branch)
✅ Ready for review/merge
