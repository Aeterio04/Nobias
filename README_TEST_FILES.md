# Test Files for NoBias Audits

## Files Included

1. **test_hiring_data.csv** - Sample hiring dataset (50 rows)
   - Columns: gender, race, age, experience, education_years, skills_score, hired
   - Protected attributes: gender, race
   - Target: hired (1 = hired, 0 = not hired)

2. **test_hiring_model.pkl** - Pre-trained RandomForest model
   - Trained on the hiring dataset
   - Features: age, experience, education_years, skills_score
   - 80% test accuracy

3. **test_model_audit_example.py** - Example script for model audit
4. **test_dataset_audit_example.py** - Example script for dataset audit

## How to Use

### Test Model Audit

```bash
python test_model_audit_example.py
```

This will:
- Load the model and test data
- Run fairness audit
- Print findings and severity
- Export report to JSON

### Test Dataset Audit

```bash
python test_dataset_audit_example.py
```

This will:
- Load the dataset
- Analyze for bias
- Print findings and remediation suggestions
- Export report to JSON

### Manual Testing

```python
# Model Audit
from nobias.model_audit import audit_model

report = audit_model(
    model='test_hiring_model.pkl',
    test_data='test_hiring_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)

print(f"Severity: {report.overall_severity.value}")
print(f"Flip Rate: {report.counterfactual_result.flip_rate:.2%}")
```

```python
# Dataset Audit
from nobias import audit_dataset

report = audit_dataset(
    data='test_hiring_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)

print(f"Severity: {report.overall_severity}")
print(f"Findings: {len(report.findings)}")
```

## Expected Results

The test data intentionally has some bias patterns to demonstrate the audit capabilities:
- Gender imbalance in hiring rates
- Some counterfactual flips
- Proxy features may be detected

This allows you to see the audit system working on realistic biased data.

## Recreate Model

If you need to recreate the model:

```bash
python create_test_model.py
```

This will retrain and save `test_hiring_model.pkl`.
