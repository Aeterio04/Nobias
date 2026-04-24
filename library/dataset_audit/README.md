# Dataset Audit Module

Detects statistical bias in datasets before model training.

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

## What It Detects

1. Representation bias (group sizes)
2. Label bias (DIR/SPD metrics)
3. Proxy features (indirect discrimination)
4. Missing data patterns
5. Intersectional disparities
6. Distribution shifts (KL divergence)
7. Remediation suggestions

## Module Files

- `__init__.py` - Main API
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

## Documentation

- **CHANGELOG.md** - Implementation notes
- **DEV_PLAN.md** - Original specification

See `/docs` folder for setup and usage guides.
