# Dataset Audit

Detects bias in datasets before model training.

## Usage

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

## Detects

- Representation bias
- Label bias (DIR/SPD)
- Proxy features
- Missing data patterns
- Intersectional disparities
- Distribution shifts

## Severity

CRITICAL | MODERATE | LOW | CLEAR
