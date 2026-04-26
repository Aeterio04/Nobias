# NoBias

Bias detection and mitigation library for datasets and AI systems.

## Modules

- ✅ **dataset_audit** - Detects bias in tabular datasets
- ⏳ **model_audit** - Planned
- 🔧 **agent_audit** - In progress

## Quick Start - Dataset Audit

```bash
pip install pandas numpy scipy scikit-learn imbalanced-learn
```

```python
from library.dataset_audit import audit_dataset

report = audit_dataset(
    data="data.csv",
    protected_attributes=["gender", "race"],
    target_column="hired",
    positive_value=1
)

print(report.overall_severity)
print(report.to_text())
```

## Testing

```bash
python test_simple.py  # Synthetic data (no download)
python test_adult.py   # UCI Adult dataset (requires internet)
```

## Documentation

See `/docs` folder for detailed guides.
