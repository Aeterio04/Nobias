# Dataset Audit - Niru How to Run

## Install

```bash
cd Nobias
pip install pandas numpy scipy scikit-learn imbalanced-learn
```

## Run Test

```bash
python test_simple.py  # Synthetic data (no download)
python test_adult.py   # UCI Adult dataset (needs internet)
```

## Use Your Data

```python
from library.dataset_audit import audit_dataset

report = audit_dataset(
    data="your_data.csv",
    protected_attributes=["gender", "race"],
    target_column="outcome",
    positive_value=1
)

print(report.to_text())
report.export("audit.json")
```

## Datasets to Try

- **UCI Adult Income** - `test_adult.py` downloads it
- **COMPAS Recidivism** - https://github.com/propublica/compas-analysis
- **German Credit** - https://archive.ics.uci.edu/ml/datasets/statlog+(german+credit+data)
- **Your own CSV** - Any tabular data with protected attributes
